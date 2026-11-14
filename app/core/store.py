from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pydicom
from scipy import ndimage

from .geometry import evaluation_summary, rasterize_polygon, validate_polygon
from .imaging import (
    approximate_pdff,
    approximate_water_fat,
    build_comparison_overlay,
    build_contour,
    build_phase_lookup,
    encode_png,
    load_label_mask,
    normalize_to_uint8,
    pdff_to_rgba,
    read_dicom_pixels,
    slice_position_key,
    summarize_pdff,
    window_image,
)


ORGAN_LABELS = {
    "liver": {"name": "Liver", "value": 63},
    "organ_2": {"name": "Right Kidney", "value": 126},
    "organ_3": {"name": "Left Kidney", "value": 189},
    "organ_4": {"name": "Spleen", "value": 252},
}


@dataclass
class SliceRecord:
    dicom_path: Path
    gt_path: Path
    basename: str
    out_phase_path: Path | None = None


def organ_info() -> list[dict[str, Any]]:
    return [{"key": key, "name": item["name"], "value": item["value"]} for key, item in ORGAN_LABELS.items()]


def organ_value_from_key(organ_key: str) -> int:
    if organ_key not in ORGAN_LABELS:
        raise KeyError(f"Unknown organ: {organ_key}")
    return int(ORGAN_LABELS[organ_key]["value"])


class DatasetStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.index = self._scan()
        self._slice_cache: dict[tuple[str, str, int, str], dict[str, Any]] = {}
        self._volume_cache: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._orthogonal_cache: dict[tuple[str, str, int, int | None, int | None, str], dict[str, Any]] = {}

    def _scan(self) -> dict[str, dict[str, Any]]:
        cases: dict[str, dict[str, Any]] = {}
        for patient_dir in sorted(self.data_dir.iterdir(), key=lambda item: item.name):
            if not patient_dir.is_dir():
                continue
            sequences: dict[str, Any] = {}
            for sequence_dir in sorted(patient_dir.iterdir(), key=lambda item: item.name):
                ground_dir = sequence_dir / "Ground"
                dicom_root = sequence_dir / "DICOM_anon"
                if not ground_dir.exists() or not dicom_root.exists():
                    continue

                sequence_kind = "dual_echo" if (dicom_root / "InPhase").exists() and (dicom_root / "OutPhase").exists() else "single_echo"
                if sequence_kind == "dual_echo":
                    dicom_candidates, in_phase_positions = build_phase_lookup(sorted((dicom_root / "InPhase").glob("*.dcm")))
                    _, out_phase_positions = build_phase_lookup(sorted((dicom_root / "OutPhase").glob("*.dcm")))
                else:
                    dicom_candidates = {path.stem: path for path in dicom_root.rglob("*.dcm")}
                    in_phase_positions = {}
                    out_phase_positions = {}

                slices: list[SliceRecord] = []
                for gt_path in sorted(ground_dir.glob("*.png")):
                    dicom_path = dicom_candidates.get(gt_path.stem)
                    if dicom_path is None:
                        continue
                    out_phase_path = None
                    if sequence_kind == "dual_echo":
                        position_key = next((key for key, value in in_phase_positions.items() if value == dicom_path), None)
                        if position_key is None:
                            position_key = slice_position_key(pydicom.dcmread(dicom_path, stop_before_pixels=True))
                        if position_key is not None:
                            out_phase_path = out_phase_positions.get(position_key)
                    slices.append(SliceRecord(dicom_path, gt_path, gt_path.stem, out_phase_path=out_phase_path))

                if slices:
                    sequences[sequence_dir.name] = {
                        "name": sequence_dir.name,
                        "slice_count": len(slices),
                        "slices": slices,
                        "supports_pdff": any(item.out_phase_path is not None for item in slices),
                    }

            if sequences:
                cases[patient_dir.name] = {"patient_id": patient_dir.name, "sequences": sequences}
        return cases

    def list_cases(self) -> list[dict[str, Any]]:
        return [
            {
                "patientId": patient_id,
                "sequenceCount": len(patient["sequences"]),
                "sequences": [
                    {
                        "name": name,
                        "sliceCount": sequence["slice_count"],
                        "supportsPdff": bool(sequence.get("supports_pdff")),
                    }
                    for name, sequence in patient["sequences"].items()
                ],
            }
            for patient_id, patient in self.index.items()
        ]

    def _get_sequence(self, patient_id: str, sequence_name: str) -> dict[str, Any]:
        patient = self.index.get(patient_id)
        if patient is None:
            raise KeyError(f"Unknown patient: {patient_id}")
        sequence = patient["sequences"].get(sequence_name)
        if sequence is None:
            raise KeyError(f"Unknown sequence: {sequence_name}")
        return sequence

    def get_case_detail(self, patient_id: str, sequence_name: str) -> dict[str, Any]:
        sequence = self._get_sequence(patient_id, sequence_name)
        return {
            "patientId": patient_id,
            "sequence": sequence_name,
            "sliceCount": sequence["slice_count"],
            "supportsPdff": bool(sequence.get("supports_pdff")),
            "slices": [{"index": index, "label": record.basename} for index, record in enumerate(sequence["slices"])],
        }

    def get_slice_payload(self, patient_id: str, sequence_name: str, slice_index: int, organ_key: str) -> dict[str, Any]:
        cache_key = (patient_id, sequence_name, slice_index, organ_key)
        if cache_key in self._slice_cache:
            return self._slice_cache[cache_key]

        sequence = self._get_sequence(patient_id, sequence_name)
        record = sequence["slices"][slice_index]
        ds = pydicom.dcmread(record.dicom_path)
        image = window_image(ds)
        organ_value = organ_value_from_key(organ_key)
        gt_mask = load_label_mask(record.gt_path, organ_value)
        gt_overlay = np.zeros((*gt_mask.shape, 4), dtype=np.uint8)
        gt_overlay[gt_mask > 0] = np.array([61, 215, 215, 150], dtype=np.uint8)
        spacing = getattr(ds, "PixelSpacing", [1.0, 1.0])
        if isinstance(spacing, pydicom.multival.MultiValue):
            spacing = list(spacing)

        pdff_overlay = None
        pdff_stats = None
        water_image = None
        fat_image = None
        if record.out_phase_path is not None:
            out_phase_ds = pydicom.dcmread(record.out_phase_path)
            in_pixels = read_dicom_pixels(ds)
            out_pixels = read_dicom_pixels(out_phase_ds)
            water, fat = approximate_water_fat(in_pixels, out_pixels)
            pdff_map = approximate_pdff(in_pixels, out_pixels)
            water_image = normalize_to_uint8(water)
            fat_image = normalize_to_uint8(fat)
            pdff_overlay = pdff_to_rgba(pdff_map)
            pdff_stats = summarize_pdff(pdff_map, gt_mask)

        payload = {
            "patientId": patient_id,
            "sequence": sequence_name,
            "index": slice_index,
            "basename": record.basename,
            "organKey": organ_key,
            "organName": ORGAN_LABELS[organ_key]["name"],
            "image": encode_png(image),
            "waterImage": encode_png(water_image) if water_image is not None else None,
            "fatImage": encode_png(fat_image) if fat_image is not None else None,
            "gtOverlay": encode_png(gt_overlay),
            "pdffOverlay": encode_png(pdff_overlay) if pdff_overlay is not None else None,
            "gtContour": build_contour(gt_mask),
            "gtMaskArea": int(gt_mask.sum()),
            "width": int(image.shape[1]),
            "height": int(image.shape[0]),
            "sliceCount": sequence["slice_count"],
            "supportsPdff": record.out_phase_path is not None,
            "pdffLabel": "Approx. PDFF (%)",
            "gtPdffStats": pdff_stats,
            "pixelSpacing": [float(spacing[0]), float(spacing[1])],
            "sliceThickness": float(getattr(ds, "SliceThickness", 1.0)),
            "teachingText": f"Teal indicates the expert {ORGAN_LABELS[organ_key]['name'].lower()} region. Browse nearby slices to understand how the anatomy evolves in depth.",
        }
        self._slice_cache[cache_key] = payload
        return payload

    def evaluate(self, patient_id: str, sequence_name: str, slice_index: int, points: list[list[float]], organ_key: str) -> dict[str, Any]:
        slice_payload = self.get_slice_payload(patient_id, sequence_name, slice_index, organ_key)
        polygon = [(float(point[0]), float(point[1])) for point in points]
        is_valid, message = validate_polygon(polygon, (slice_payload["height"], slice_payload["width"]))
        if not is_valid:
            return {"ok": False, "message": message}

        sequence = self._get_sequence(patient_id, sequence_name)
        organ_value = organ_value_from_key(organ_key)
        gt_mask = load_label_mask(sequence["slices"][slice_index].gt_path, organ_value)
        student_mask = rasterize_polygon(polygon, gt_mask.shape)
        student_pdff_stats = None
        if sequence["slices"][slice_index].out_phase_path is not None:
            in_phase_ds = pydicom.dcmread(sequence["slices"][slice_index].dicom_path)
            out_phase_ds = pydicom.dcmread(sequence["slices"][slice_index].out_phase_path)
            pdff_map = approximate_pdff(read_dicom_pixels(in_phase_ds), read_dicom_pixels(out_phase_ds))
            student_pdff_stats = summarize_pdff(pdff_map, student_mask)
        return {
            "ok": True,
            "message": "Evaluation complete.",
            **evaluation_summary(student_mask, gt_mask),
            "studentPdffStats": student_pdff_stats,
            "comparisonOverlay": encode_png(build_comparison_overlay(student_mask, gt_mask)),
            "studentContour": build_contour(student_mask),
        }

    def start_segmentation_session(self, patient_id: str, organ_key: str = "liver", count: int = 10, min_area: int = 500) -> dict[str, Any]:
        patient = self.index.get(patient_id)
        if patient is None:
            raise KeyError(f"Unknown patient: {patient_id}")

        sequence_name = "T1DUAL" if "T1DUAL" in patient["sequences"] else next(iter(patient["sequences"]))
        sequence = patient["sequences"][sequence_name]
        organ_value = organ_value_from_key(organ_key)
        candidates = []
        for index, record in enumerate(sequence["slices"]):
            mask = load_label_mask(record.gt_path, organ_value)
            area = int(mask.sum())
            if area >= min_area:
                candidates.append({"index": index, "label": record.basename, "gtArea": area})

        if len(candidates) < count:
            raise ValueError(f"Only {len(candidates)} slices meet the minimum area threshold.")

        selected = sorted(random.sample(candidates, count), key=lambda item: item["index"])
        return {
            "patientId": patient_id,
            "sequence": sequence_name,
            "organKey": organ_key,
            "organName": ORGAN_LABELS[organ_key]["name"],
            "minArea": min_area,
            "slices": selected,
        }

    def evaluate_segmentation_session(self, patient_id: str, sequence_name: str, organ_key: str, submissions: list[dict[str, Any]]) -> dict[str, Any]:
        sequence = self._get_sequence(patient_id, sequence_name)
        organ_value = organ_value_from_key(organ_key)
        per_slice = []
        student_masks = []
        gt_masks = []
        source_indices = []
        student_volume_pdff_values = []
        gt_volume_pdff_values = []

        for item in submissions:
            slice_index = int(item["index"])
            polygon = [(float(point[0]), float(point[1])) for point in item["points"]]
            gt_mask = load_label_mask(sequence["slices"][slice_index].gt_path, organ_value)
            is_valid, message = validate_polygon(polygon, gt_mask.shape)
            if not is_valid:
                raise ValueError(f"Slice {slice_index}: {message}")
            student_mask = rasterize_polygon(polygon, gt_mask.shape)
            record = sequence["slices"][slice_index]
            student_pdff_stats = None
            gt_pdff_stats = None
            if record.out_phase_path is not None:
                in_phase_ds = pydicom.dcmread(record.dicom_path)
                out_phase_ds = pydicom.dcmread(record.out_phase_path)
                pdff_map = approximate_pdff(read_dicom_pixels(in_phase_ds), read_dicom_pixels(out_phase_ds))
                student_pdff_stats = summarize_pdff(pdff_map, student_mask)
                gt_pdff_stats = summarize_pdff(pdff_map, gt_mask)
                student_values = pdff_map[student_mask > 0]
                student_values = student_values[np.isfinite(student_values)]
                student_values = student_values[student_values > 0]
                if student_values.size:
                    student_volume_pdff_values.append(student_values)
                gt_values = pdff_map[gt_mask > 0]
                gt_values = gt_values[np.isfinite(gt_values)]
                gt_values = gt_values[gt_values > 0]
                if gt_values.size:
                    gt_volume_pdff_values.append(gt_values)
            summary = evaluation_summary(student_mask, gt_mask)
            per_slice.append(
                {
                    "index": slice_index,
                    "label": record.basename,
                    **summary,
                    "studentPdffStats": student_pdff_stats,
                    "gtPdffStats": gt_pdff_stats,
                    "comparisonOverlay": encode_png(build_comparison_overlay(student_mask, gt_mask)),
                    "studentContour": build_contour(student_mask),
                    "gtContour": build_contour(gt_mask),
                }
            )
            student_masks.append(student_mask)
            gt_masks.append(gt_mask)
            source_indices.append(slice_index)

        dice_values = [item["dice"] for item in per_slice]
        student_volume = self._mask_stack_to_volume_payload(student_masks, source_indices, sequence)
        gt_volume = self._mask_stack_to_volume_payload(gt_masks, source_indices, sequence)
        student_volume["volumePdffMedian"] = round(float(np.median(np.concatenate(student_volume_pdff_values))) * 100.0, 2) if student_volume_pdff_values else None
        gt_volume["volumePdffMedian"] = round(float(np.median(np.concatenate(gt_volume_pdff_values))) * 100.0, 2) if gt_volume_pdff_values else None
        return {
            "ok": True,
            "score": round(float(np.mean(dice_values)) * 100.0, 1) if dice_values else 0.0,
            "meanDice": round(float(np.mean(dice_values)), 4) if dice_values else 0.0,
            "perSlice": per_slice,
            "studentVolume": student_volume,
            "gtVolume": gt_volume,
        }

    def _mask_stack_to_volume_payload(self, masks: list[np.ndarray], source_indices: list[int], sequence: dict[str, Any]) -> dict[str, Any]:
        if not masks:
            return {"points": [], "pointSliceIndices": [], "slicePlanes": {}, "bbox": [1, 1, 1], "sliceCount": 0, "sourceSliceIndices": []}

        first_ds = pydicom.dcmread(sequence["slices"][source_indices[0]].dicom_path, stop_before_pixels=True)
        spacing = getattr(first_ds, "PixelSpacing", [1.0, 1.0])
        if isinstance(spacing, pydicom.multival.MultiValue):
            spacing = list(spacing)
        spacing_y, spacing_x = float(spacing[0]), float(spacing[1])
        slice_thickness = float(getattr(first_ds, "SliceThickness", 1.0))
        volume = np.stack(masks, axis=0)
        if volume.max() == 0:
            return {"points": [], "pointSliceIndices": [], "slicePlanes": {}, "bbox": [1, 1, 1], "sliceCount": len(masks), "sourceSliceIndices": source_indices}

        boundary = np.logical_xor(volume > 0, ndimage.binary_erosion(volume > 0))
        boundary_points = np.argwhere(boundary)
        sampled = boundary_points[:: max(1, int(boundary_points.shape[0] / 5500) or 1)]
        coords = np.array(
            [[x * spacing_x, y * spacing_y, source_indices[int(z)] * slice_thickness] for z, y, x in sampled],
            dtype=np.float32,
        )
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        center = (mins + maxs) / 2.0
        scale = float(np.max(maxs - mins)) or 1.0

        slice_planes: dict[str, list[list[list[float]]]] = {}
        for slice_index, mask in enumerate(volume > 0):
            runs = []
            for y, row in enumerate(mask):
                xs = np.flatnonzero(row)
                if xs.size == 0:
                    continue
                splits = np.where(np.diff(xs) > 1)[0] + 1
                for run in np.split(xs, splits):
                    x0 = int(run[0])
                    x1 = int(run[-1]) + 1
                    z = float(source_indices[slice_index]) * slice_thickness
                    quad = np.array(
                        [
                            [x0 * spacing_x, y * spacing_y, z],
                            [x1 * spacing_x, y * spacing_y, z],
                            [x1 * spacing_x, (y + 1) * spacing_y, z],
                            [x0 * spacing_x, (y + 1) * spacing_y, z],
                        ],
                        dtype=np.float32,
                    )
                    runs.append(((quad - center) / scale).round(5).tolist())
            if runs:
                slice_planes[str(slice_index)] = runs

        return {
            "points": ((coords - center) / scale).tolist(),
            "pointSliceIndices": sampled[:, 0].astype(int).tolist(),
            "slicePlanes": slice_planes,
            "bbox": (maxs - mins).round(3).tolist(),
            "sliceCount": len(masks),
            "sourceSliceIndices": source_indices,
        }

    def get_volume_payload(self, patient_id: str, sequence_name: str, organ_key: str) -> dict[str, Any]:
        cache_key = (patient_id, sequence_name, organ_key)
        if cache_key in self._volume_cache:
            return self._volume_cache[cache_key]

        sequence = self._get_sequence(patient_id, sequence_name)
        masks = []
        volume_pdff_values = []
        spacings = None
        slice_thickness = 1.0
        organ_value = organ_value_from_key(organ_key)
        for record in sequence["slices"]:
            mask = load_label_mask(record.gt_path, organ_value)
            masks.append(mask)
            if spacings is None:
                ds = pydicom.dcmread(record.dicom_path, stop_before_pixels=True)
                values = getattr(ds, "PixelSpacing", [1.0, 1.0])
                if isinstance(values, pydicom.multival.MultiValue):
                    values = list(values)
                spacings = [float(values[0]), float(values[1])]
                slice_thickness = float(getattr(ds, "SliceThickness", 1.0))
            if record.out_phase_path is not None and mask.any():
                in_phase_ds = pydicom.dcmread(record.dicom_path)
                out_phase_ds = pydicom.dcmread(record.out_phase_path)
                pdff_map = approximate_pdff(read_dicom_pixels(in_phase_ds), read_dicom_pixels(out_phase_ds))
                values_in_mask = pdff_map[mask > 0]
                values_in_mask = values_in_mask[np.isfinite(values_in_mask)]
                values_in_mask = values_in_mask[values_in_mask > 0]
                if values_in_mask.size:
                    volume_pdff_values.append(values_in_mask)

        volume = np.stack(masks, axis=0)
        if volume.max() == 0:
            payload = {"points": [], "bbox": [1, 1, 1], "sliceCount": len(masks)}
            self._volume_cache[cache_key] = payload
            return payload

        boundary = np.logical_xor(volume > 0, ndimage.binary_erosion(volume > 0))
        sampled = np.argwhere(boundary)[:: max(1, int(np.argwhere(boundary).shape[0] / 5500) or 1)]
        spacing_z, spacing_y, spacing_x = slice_thickness, spacings[0], spacings[1]
        coords = np.array([[x * spacing_x, y * spacing_y, z * spacing_z] for z, y, x in sampled], dtype=np.float32)
        point_slice_indices = sampled[:, 0].astype(int)
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        center = (mins + maxs) / 2.0
        scale = float(np.max(maxs - mins)) or 1.0

        slice_planes: dict[str, list[list[list[float]]]] = {}
        for slice_index, mask in enumerate(volume > 0):
            runs = []
            for y, row in enumerate(mask):
                xs = np.flatnonzero(row)
                if xs.size == 0:
                    continue
                splits = np.where(np.diff(xs) > 1)[0] + 1
                for run in np.split(xs, splits):
                    x0 = int(run[0])
                    x1 = int(run[-1]) + 1
                    z = float(slice_index) * spacing_z
                    quad = np.array(
                        [
                            [x0 * spacing_x, y * spacing_y, z],
                            [x1 * spacing_x, y * spacing_y, z],
                            [x1 * spacing_x, (y + 1) * spacing_y, z],
                            [x0 * spacing_x, (y + 1) * spacing_y, z],
                        ],
                        dtype=np.float32,
                    )
                    runs.append(((quad - center) / scale).round(5).tolist())
            if runs:
                slice_planes[str(slice_index)] = runs

        payload = {
            "points": ((coords - center) / scale).tolist(),
            "pointSliceIndices": point_slice_indices.tolist(),
            "slicePlanes": slice_planes,
            "volumePdffMedian": round(float(np.median(np.concatenate(volume_pdff_values))) * 100.0, 2) if volume_pdff_values else None,
            "bbox": (maxs - mins).round(3).tolist(),
            "sliceCount": len(masks),
        }
        self._volume_cache[cache_key] = payload
        return payload

    @staticmethod
    def _sample_axis_positions(axis_size: int, target_count: int) -> list[int]:
        if axis_size <= 0 or target_count <= 0:
            return [0]
        count = min(axis_size, target_count)
        return np.linspace(0, axis_size - 1, count).round().astype(int).tolist()

    @staticmethod
    def _nearest_sample_index(positions: list[int], source_index: int) -> int:
        return min(range(len(positions)), key=lambda item: abs(positions[item] - source_index))

    def get_orthogonal_payload(
        self,
        patient_id: str,
        sequence_name: str,
        axial_index: int,
        coronal_index: int | None,
        sagittal_index: int | None,
        organ_key: str,
    ) -> dict[str, Any]:
        cache_key = (patient_id, sequence_name, axial_index, coronal_index, sagittal_index, organ_key)
        if cache_key in self._orthogonal_cache:
            return self._orthogonal_cache[cache_key]

        sequence = self._get_sequence(patient_id, sequence_name)
        if axial_index < 0 or axial_index >= sequence["slice_count"]:
            raise IndexError(f"Axial index out of range: {axial_index}")

        images = []
        masks = []
        organ_value = organ_value_from_key(organ_key)
        spacing = [1.0, 1.0]
        slice_thickness = 1.0
        for index, record in enumerate(sequence["slices"]):
            ds = pydicom.dcmread(record.dicom_path)
            images.append(window_image(ds))
            masks.append(load_label_mask(record.gt_path, organ_value))
            if index == 0:
                values = getattr(ds, "PixelSpacing", [1.0, 1.0])
                if isinstance(values, pydicom.multival.MultiValue):
                    values = list(values)
                spacing = [float(values[0]), float(values[1])]
                slice_thickness = float(getattr(ds, "SliceThickness", 1.0))

        volume = np.stack(images, axis=0)
        mask_volume = np.stack(masks, axis=0)
        if mask_volume.any():
            z_values, y_values, x_values = np.argwhere(mask_volume > 0).T
            default_coronal_index = int(np.median(y_values))
            default_sagittal_index = int(np.median(x_values))
        else:
            default_coronal_index = volume.shape[1] // 2
            default_sagittal_index = volume.shape[2] // 2

        coronal_positions = self._sample_axis_positions(volume.shape[1], sequence["slice_count"])
        sagittal_positions = self._sample_axis_positions(volume.shape[2], sequence["slice_count"])
        coronal_index = self._nearest_sample_index(coronal_positions, default_coronal_index) if coronal_index is None else coronal_index
        sagittal_index = self._nearest_sample_index(sagittal_positions, default_sagittal_index) if sagittal_index is None else sagittal_index
        if coronal_index < 0 or coronal_index >= len(coronal_positions):
            raise IndexError(f"Coronal index out of range: {coronal_index}")
        if sagittal_index < 0 or sagittal_index >= len(sagittal_positions):
            raise IndexError(f"Sagittal index out of range: {sagittal_index}")

        coronal_source_index = coronal_positions[coronal_index]
        sagittal_source_index = sagittal_positions[sagittal_index]

        axial = volume[axial_index]
        coronal = volume[:, coronal_source_index, :]
        sagittal = volume[:, :, sagittal_source_index]

        spacing_y, spacing_x = spacing
        coronal_zoom_y = max(0.2, min(8.0, slice_thickness / spacing_x))
        sagittal_zoom_y = max(0.2, min(8.0, slice_thickness / spacing_y))
        coronal = ndimage.zoom(coronal, (coronal_zoom_y, 1.0), order=1)
        sagittal = ndimage.zoom(sagittal, (sagittal_zoom_y, 1.0), order=1)

        payload = {
            "patientId": patient_id,
            "sequence": sequence_name,
            "index": axial_index,
            "organKey": organ_key,
            "organName": ORGAN_LABELS[organ_key]["name"],
            "views": [
                {
                    "key": "axial",
                    "name": "Axial",
                    "subtitle": "Transverse / original slice plane",
                    "image": encode_png(axial),
                    "index": int(axial_index),
                    "sourceIndex": int(axial_index),
                    "slice": int(axial_index + 1),
                    "sliceCount": int(sequence["slice_count"]),
                },
                {
                    "key": "coronal",
                    "name": "Coronal",
                    "subtitle": "Front-to-back reconstructed plane",
                    "image": encode_png(normalize_to_uint8(coronal)),
                    "index": int(coronal_index),
                    "sourceIndex": int(coronal_source_index),
                    "slice": int(coronal_index + 1),
                    "sliceCount": int(len(coronal_positions)),
                },
                {
                    "key": "sagittal",
                    "name": "Sagittal",
                    "subtitle": "Left-to-right reconstructed plane",
                    "image": encode_png(normalize_to_uint8(sagittal)),
                    "index": int(sagittal_index),
                    "sourceIndex": int(sagittal_source_index),
                    "slice": int(sagittal_index + 1),
                    "sliceCount": int(len(sagittal_positions)),
                },
            ],
            "spacing": {
                "row": spacing_y,
                "column": spacing_x,
                "sliceThickness": slice_thickness,
            },
        }
        self._orthogonal_cache[cache_key] = payload
        return payload
