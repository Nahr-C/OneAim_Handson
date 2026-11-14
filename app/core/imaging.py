from __future__ import annotations

import base64
import io
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image
from scipy import ndimage


def encode_png(array: np.ndarray) -> str:
    image = Image.fromarray(array)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    payload = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def normalize_to_uint8(array: np.ndarray) -> np.ndarray:
    array = np.asarray(array, dtype=np.float32)
    min_val = float(array.min())
    max_val = float(array.max())
    if max_val <= min_val:
        return np.zeros(array.shape, dtype=np.uint8)
    scaled = (array - min_val) / (max_val - min_val)
    return np.clip(scaled * 255.0, 0, 255).astype(np.uint8)


def read_dicom_pixels(ds: pydicom.dataset.FileDataset) -> np.ndarray:
    pixels = ds.pixel_array.astype(np.float32)
    return pixels * float(getattr(ds, "RescaleSlope", 1.0)) + float(getattr(ds, "RescaleIntercept", 0.0))


def window_image(ds: pydicom.dataset.FileDataset) -> np.ndarray:
    pixels = read_dicom_pixels(ds)
    window_center = getattr(ds, "WindowCenter", None)
    window_width = getattr(ds, "WindowWidth", None)
    if isinstance(window_center, pydicom.multival.MultiValue):
        window_center = float(window_center[0])
    if isinstance(window_width, pydicom.multival.MultiValue):
        window_width = float(window_width[0])
    if window_center is not None and window_width is not None and float(window_width) > 1:
        center = float(window_center)
        width = float(window_width)
        pixels = np.clip(pixels, center - width / 2.0, center + width / 2.0)
    return normalize_to_uint8(pixels)


def build_comparison_overlay(student_mask: np.ndarray, gt_mask: np.ndarray) -> np.ndarray:
    overlay = np.zeros((*student_mask.shape, 4), dtype=np.uint8)
    overlap = np.logical_and(student_mask > 0, gt_mask > 0)
    false_positive = np.logical_and(student_mask > 0, gt_mask == 0)
    false_negative = np.logical_and(student_mask == 0, gt_mask > 0)
    overlay[overlap] = np.array([70, 202, 160, 170], dtype=np.uint8)
    overlay[false_positive] = np.array([255, 186, 73, 185], dtype=np.uint8)
    overlay[false_negative] = np.array([255, 99, 132, 185], dtype=np.uint8)
    return overlay


def build_contour(mask: np.ndarray) -> list[list[int]]:
    border = np.logical_xor(mask > 0, ndimage.binary_erosion(mask > 0))
    points = np.argwhere(border)
    if len(points) == 0:
        return []
    sampled = points[:: max(1, len(points) // 400)]
    return [[int(col), int(row)] for row, col in sampled]


def slice_position_key(ds: pydicom.dataset.FileDataset) -> tuple[float, float, float] | None:
    position = getattr(ds, "ImagePositionPatient", None)
    if position is not None:
        return tuple(round(float(value), 3) for value in position)
    slice_location = getattr(ds, "SliceLocation", None)
    if slice_location is not None:
        return (round(float(slice_location), 3), 0.0, 0.0)
    return None


def build_phase_lookup(paths: list[Path]) -> tuple[dict[str, Path], dict[tuple[float, float, float], Path]]:
    by_stem: dict[str, Path] = {}
    by_position: dict[tuple[float, float, float], Path] = {}
    for path in paths:
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        by_stem[path.stem] = path
        position_key = slice_position_key(ds)
        if position_key is not None:
            by_position[position_key] = path
    return by_stem, by_position


def approximate_water_fat(in_phase_pixels: np.ndarray, out_phase_pixels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    in_phase = np.maximum(np.asarray(in_phase_pixels, dtype=np.float32), 0.0)
    out_phase = np.maximum(np.asarray(out_phase_pixels, dtype=np.float32), 0.0)
    water = np.maximum((in_phase + out_phase) * 0.5, 0.0)
    fat = np.abs(in_phase - out_phase) * 0.5
    return water, fat


def approximate_pdff(in_phase_pixels: np.ndarray, out_phase_pixels: np.ndarray) -> np.ndarray:
    in_phase = np.maximum(np.asarray(in_phase_pixels, dtype=np.float32), 0.0)
    water, fat = approximate_water_fat(in_phase, out_phase_pixels)
    signal = water + fat
    pdff = np.clip(fat / np.maximum(signal, 1e-6), 0.0, 1.0)

    foreground_signal = np.maximum(in_phase, signal)
    nonzero_signal = foreground_signal[foreground_signal > 0]
    if nonzero_signal.size:
        threshold = max(float(np.percentile(foreground_signal, 99)) * 0.02, float(np.median(nonzero_signal)) * 0.15)
        foreground = foreground_signal > threshold
        foreground = ndimage.binary_opening(foreground, structure=np.ones((3, 3), dtype=bool))
        foreground = ndimage.binary_closing(foreground, structure=np.ones((5, 5), dtype=bool))
        foreground = ndimage.binary_fill_holes(foreground)
    else:
        foreground = foreground_signal > 0

    pdff = pdff.astype(np.float32, copy=False)
    pdff[~foreground] = np.nan
    return pdff


def pdff_to_rgba(pdff: np.ndarray) -> np.ndarray:
    values = np.asarray(pdff, dtype=np.float32)
    valid = np.isfinite(values)
    # Map 0-50% to a blue->cyan->yellow->red teaching spectrum.
    normalized = np.clip(np.nan_to_num(values, nan=0.0) / 0.5, 0.0, 1.0)
    red = np.clip(255.0 * np.minimum(np.maximum((normalized - 0.5) / 0.5, 0.0), 1.0), 0, 255)
    green = np.clip(255.0 * (1.0 - np.abs(normalized - 0.5) / 0.5), 0, 255)
    blue = np.clip(255.0 * np.minimum(np.maximum((0.5 - normalized) / 0.5, 0.0), 1.0), 0, 255)
    alpha = np.where(valid, 170, 0)
    return np.stack([red, green, blue, alpha], axis=-1).astype(np.uint8)


def summarize_pdff(pdff: np.ndarray, mask: np.ndarray) -> dict[str, float | int] | None:
    values = np.asarray(pdff, dtype=np.float32)[mask > 0]
    values = values[np.isfinite(values)]
    values = values[values > 0]
    if values.size == 0:
        return None
    lower, upper = np.percentile(values, [5, 95])
    trimmed_values = values[(values >= lower) & (values <= upper)]
    if trimmed_values.size == 0:
        trimmed_values = values
    return {
        "mean": round(float(values.mean()) * 100.0, 2),
        "trimmedMean": round(float(trimmed_values.mean()) * 100.0, 2),
        "median": round(float(np.median(values)) * 100.0, 2),
        "voxelCount": int(values.size),
    }


def load_label_mask(mask_path: Path, label_value: int) -> np.ndarray:
    return (np.array(Image.open(mask_path).convert("L")) == label_value).astype(np.uint8)
