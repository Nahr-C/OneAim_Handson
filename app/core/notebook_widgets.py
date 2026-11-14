from __future__ import annotations

from collections.abc import Sequence
from itertools import count
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pydicom
from IPython.display import display
from ipympl.backend_nbagg import new_figure_manager_given_figure
from ipywidgets import Button, HBox, IntSlider, Label, VBox
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure

from .geometry import evaluation_summary, rasterize_polygon
from .imaging import build_comparison_overlay, load_label_mask, window_image

_FIGURE_NUMBERS = count(10000)


def make_mask_cmap(color: tuple[float, float, float], alpha: float = 0.55) -> ListedColormap:
    return ListedColormap([(0, 0, 0, 0), (*color, alpha)])


def create_widget_figure(figsize: tuple[float, float], max_width: str) -> Figure:
    fig = Figure(figsize=figsize, constrained_layout=True)
    was_interactive = plt.isinteractive()
    plt.ioff()
    try:
        new_figure_manager_given_figure(next(_FIGURE_NUMBERS), fig)
    finally:
        plt.interactive(was_interactive)
    limit_widget_canvas(fig, max_width=max_width)
    return fig


def limit_widget_canvas(fig: Figure, width: str = "100%", max_width: str = "980px") -> None:
    canvas = fig.canvas
    if hasattr(canvas, "layout"):
        canvas.layout.width = width
        canvas.layout.max_width = max_width
    for attr in ("toolbar_visible", "header_visible", "footer_visible", "resizable"):
        if hasattr(canvas, attr):
            setattr(canvas, attr, False)


def prevent_implicit_display(fig: Figure) -> None:
    if hasattr(fig.canvas, "_closed"):
        fig.canvas._closed = True


def show_mri_and_mask(
    image: np.ndarray,
    mask: np.ndarray,
    mask_cmap: ListedColormap,
    *,
    figsize: tuple[float, float] = (8.5, 4.2),
    max_width: str = "900px",
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=figsize, constrained_layout=True)
    limit_widget_canvas(fig, max_width=max_width)

    axes[0].imshow(image, cmap="gray")
    axes[0].set_title("MRI slice")
    axes[0].axis("off")

    axes[1].imshow(image, cmap="gray")
    axes[1].imshow(mask, cmap=mask_cmap, interpolation="nearest")
    axes[1].set_title("MRI slice with liver mask overlay")
    axes[1].axis("off")

    plt.show()


def preload_slice_frames(
    slice_records: Sequence[Any],
    organ_value: int,
) -> tuple[list[np.ndarray], list[np.ndarray], list[str]]:
    images: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    labels: list[str] = []

    for record in slice_records:
        ds = pydicom.dcmread(record.dicom_path)
        images.append(window_image(ds))
        masks.append(load_label_mask(record.gt_path, organ_value))
        labels.append(record.basename)

    return images, masks, labels


def browse_slices(
    images: Sequence[np.ndarray],
    masks: Sequence[np.ndarray],
    labels: Sequence[str],
    mask_cmap: ListedColormap,
    *,
    initial_index: int = 0,
    figsize: tuple[float, float] = (5.2, 5.2),
    max_width: str = "620px",
) -> VBox:
    index = int(np.clip(initial_index, 0, len(images) - 1))

    fig = create_widget_figure(figsize, max_width)
    ax = fig.subplots()
    image_artist = ax.imshow(images[index], cmap="gray")
    mask_artist = ax.imshow(masks[index], cmap=mask_cmap, interpolation="nearest")
    title = ax.set_title(f"Slice {index} | {labels[index]}")
    ax.axis("off")

    slider = IntSlider(
        min=0,
        max=len(images) - 1,
        step=1,
        value=index,
        continuous_update=True,
        description="Slice",
        readout=True,
    )

    def update(change: dict[str, Any]) -> None:
        idx = int(change["new"])
        image_artist.set_data(images[idx])
        mask_artist.set_data(masks[idx])
        title.set_text(f"Slice {idx} | {labels[idx]}")
        fig.canvas.draw_idle()

    slider.observe(update, names="value")
    return VBox([fig.canvas, slider])


def _sync_student_namespace(namespace: dict[str, Any] | None, state: dict[str, Any]) -> None:
    if namespace is None:
        return
    current_index = int(state["current_index"])
    current_mask = state["student_masks"].get(current_index)
    namespace["student_masks"] = state["student_masks"]
    namespace["student_polygons"] = state["polygons"]
    namespace["student_slice_index"] = current_index
    namespace["student_mask"] = (
        current_mask.copy()
        if current_mask is not None
        else np.zeros_like(state["gt_masks"][current_index], dtype=np.uint8)
    )
    namespace["student_polygon"] = state["polygons"].setdefault(current_index, [])
    namespace["evaluation"] = state["evaluations"].get(current_index)
    namespace["student_evaluations"] = state["evaluations"]
    namespace["student_export_paths"] = state["export_paths"]


def create_student_segmentation_widget(
    images: Sequence[np.ndarray] | np.ndarray,
    gt_masks: Sequence[np.ndarray] | np.ndarray,
    labels: Sequence[str] | None = None,
    *,
    initial_index: int = 0,
    namespace: dict[str, Any] | None = None,
    output_dir: Any | None = None,
    patient_id: str = "patient",
    sequence_name: str = "sequence",
    figsize: tuple[float, float] = (5.4, 5.4),
    max_width: str = "640px",
) -> tuple[VBox, dict[str, Any]]:
    if isinstance(images, np.ndarray):
        image_list = [images]
    else:
        image_list = list(images)
    if isinstance(gt_masks, np.ndarray):
        gt_mask_list = [gt_masks]
    else:
        gt_mask_list = list(gt_masks)
    if labels is None:
        label_list = [f"Slice {index}" for index in range(len(image_list))]
    else:
        label_list = list(labels)

    current_index = int(np.clip(initial_index, 0, len(image_list) - 1))
    state: dict[str, Any] = {
        "current_index": current_index,
        "images": image_list,
        "gt_masks": gt_mask_list,
        "labels": label_list,
        "polygons": {},
        "student_masks": {},
        "evaluations": {},
        "export_paths": {},
    }
    _sync_student_namespace(namespace, state)
    student_mask_cmap = make_mask_cmap((1.0, 0.6, 0.0), alpha=0.55)
    status_label = Label(value="Click points around the liver boundary on the image.")

    fig = create_widget_figure(figsize, max_width)
    ax = fig.subplots()

    image_artist = ax.imshow(image_list[current_index], cmap="gray")
    empty_mask = np.zeros_like(gt_mask_list[current_index], dtype=np.uint8)
    student_overlay = ax.imshow(empty_mask, cmap=student_mask_cmap, interpolation="nearest")
    point_line, = ax.plot([], [], color="orange", marker="o", linewidth=2, markersize=4)
    title = ax.set_title(f"Draw student mask | Slice {current_index} | {label_list[current_index]}")
    ax.axis("off")

    def refresh_polygon(close: bool = False) -> None:
        idx = int(state["current_index"])
        points = state["polygons"].setdefault(idx, [])
        mask = state["student_masks"].get(idx)
        if mask is None:
            mask = np.zeros_like(state["gt_masks"][idx], dtype=np.uint8)
        student_overlay.set_data(mask)
        if not points:
            point_line.set_data([], [])
        else:
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            if close and len(points) >= 3:
                xs = xs + [xs[0]]
                ys = ys + [ys[0]]
            point_line.set_data(xs, ys)
        fig.canvas.draw_idle()

    def report(message: str) -> None:
        status_label.value = message

    def load_current_slice() -> None:
        idx = int(state["current_index"])
        image_artist.set_data(state["images"][idx])
        title.set_text(f"Draw student mask | Slice {idx} | {state['labels'][idx]}")
        refresh_polygon(close=idx in state["student_masks"])
        _sync_student_namespace(namespace, state)

    slider = IntSlider(
        min=0,
        max=len(image_list) - 1,
        step=1,
        value=current_index,
        continuous_update=False,
        description="Slice",
        readout=True,
    )
    previous_button = Button(description="Previous")
    next_button = Button(description="Next")

    def go_previous(_: Any) -> None:
        if slider.value > slider.min:
            slider.value -= 1

    def go_next(_: Any) -> None:
        if slider.value < slider.max:
            slider.value += 1

    def on_slice_change(change: dict[str, Any]) -> None:
        state["current_index"] = int(change["new"])
        load_current_slice()
        saved = len(state["student_masks"])
        report(f"Slice {state['current_index']} selected. Saved masks: {saved}.")

    def on_click(event: Any) -> None:
        if event.button != 1 or event.inaxes != ax or event.xdata is None or event.ydata is None:
            return
        idx = int(state["current_index"])
        if idx in state["student_masks"]:
            state["student_masks"].pop(idx, None)
            state["evaluations"].pop(idx, None)
        state["polygons"].setdefault(idx, []).append((float(event.xdata), float(event.ydata)))
        _sync_student_namespace(namespace, state)
        refresh_polygon(close=False)
        report(f"Slice {idx}: points collected: {len(state['polygons'][idx])}")

    def undo_point(_: Any) -> None:
        idx = int(state["current_index"])
        points = state["polygons"].setdefault(idx, [])
        if points:
            points.pop()
        state["student_masks"].pop(idx, None)
        state["evaluations"].pop(idx, None)
        _sync_student_namespace(namespace, state)
        refresh_polygon(close=False)
        report(f"Slice {idx}: points collected: {len(points)}")

    def reset_polygon(_: Any) -> None:
        idx = int(state["current_index"])
        state["polygons"][idx] = []
        state["student_masks"].pop(idx, None)
        state["evaluations"].pop(idx, None)
        _sync_student_namespace(namespace, state)
        refresh_polygon(close=False)
        report(f"Slice {idx} reset. Click points around the liver boundary.")

    def close_polygon(_: Any) -> None:
        idx = int(state["current_index"])
        if len(state["polygons"].setdefault(idx, [])) < 3:
            report("A polygon needs at least 3 points.")
            return
        refresh_polygon(close=True)
        report(f"Slice {idx}: polygon closed visually. Click Generate Mask.")

    def generate_mask(_: Any) -> None:
        idx = int(state["current_index"])
        points = state["polygons"].setdefault(idx, [])
        if len(points) < 3:
            report("A polygon needs at least 3 points before mask generation.")
            return
        student_mask = rasterize_polygon(points, state["gt_masks"][idx].shape)
        state["student_masks"][idx] = student_mask
        state["evaluations"][idx] = evaluation_summary(student_mask, state["gt_masks"][idx])
        if output_dir is not None:
            from PIL import Image

            export_path = output_dir / f"{patient_id}_{sequence_name}_slice{idx:03d}_student_mask.png"
            Image.fromarray((student_mask > 0).astype(np.uint8) * 255).save(export_path)
            state["export_paths"][idx] = export_path
        _sync_student_namespace(namespace, state)
        refresh_polygon(close=True)
        export_message = f" Saved to {state['export_paths'][idx]}." if idx in state["export_paths"] else ""
        report(
            f"Slice {idx} mask saved. "
            f"Dice={state['evaluations'][idx]['dice']:.3f}, "
            f"IoU={state['evaluations'][idx]['iou']:.3f}, "
            f"area={state['evaluations'][idx]['studentArea']} pixels. "
            f"Saved masks: {len(state['student_masks'])}.{export_message}"
        )

    undo_button = Button(description="Undo Point")
    reset_button = Button(description="Reset")
    close_button = Button(description="Close Polygon")
    generate_button = Button(description="Generate Mask", button_style="success")

    previous_button.on_click(go_previous)
    next_button.on_click(go_next)
    undo_button.on_click(undo_point)
    reset_button.on_click(reset_polygon)
    close_button.on_click(close_polygon)
    generate_button.on_click(generate_mask)
    slider.observe(on_slice_change, names="value")
    fig.canvas.mpl_connect("button_press_event", on_click)

    widget = VBox([
        fig.canvas,
        HBox([previous_button, slider, next_button]),
        HBox([undo_button, reset_button, close_button, generate_button]),
        status_label,
    ])
    return widget, state


def browse_student_masked_slices(
    images: Sequence[np.ndarray],
    student_masks: dict[int, np.ndarray],
    labels: Sequence[str],
    *,
    figsize: tuple[float, float] = (8.6, 4.2),
    max_width: str = "900px",
) -> VBox | Label:
    saved_indices = sorted(student_masks)
    if not saved_indices:
        return Label(value="No student masks have been generated yet.")

    fig = create_widget_figure(figsize, max_width)
    axes = fig.subplots(1, 2)
    selected = saved_indices[0]
    masked_image = np.where(student_masks[selected] > 0, images[selected], 0)

    image_artist = axes[0].imshow(images[selected], cmap="gray")
    masked_artist = axes[1].imshow(masked_image, cmap="gray")
    axes[0].set_title(f"Original | Slice {selected}")
    axes[1].set_title("MRI pixels inside student mask")
    for ax in axes:
        ax.axis("off")

    slider = IntSlider(
        min=0,
        max=len(saved_indices) - 1,
        step=1,
        value=0,
        continuous_update=True,
        description="Mask",
        readout=True,
    )

    def update(change: dict[str, Any]) -> None:
        idx = saved_indices[int(change["new"])]
        image_artist.set_data(images[idx])
        masked_artist.set_data(np.where(student_masks[idx] > 0, images[idx], 0))
        axes[0].set_title(f"Original | Slice {idx} | {labels[idx]}")
        fig.canvas.draw_idle()

    slider.observe(update, names="value")
    update({"new": 0})
    return VBox([fig.canvas, slider])


def export_student_masks(
    student_masks: dict[int, np.ndarray],
    output_dir: Any,
    patient_id: str,
    sequence_name: str,
) -> list[Any]:
    paths = []
    from PIL import Image

    for idx, mask in sorted(student_masks.items()):
        export_path = output_dir / f"{patient_id}_{sequence_name}_slice{idx:03d}_student_mask.png"
        Image.fromarray((mask > 0).astype(np.uint8) * 255).save(export_path)
        paths.append(export_path)
    return paths


def student_evaluation_table(evaluations: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "slice_index": idx,
            "dice": values["dice"],
            "iou": values["iou"],
            "student_area": values["studentArea"],
            "ground_truth_area": values["groundTruthArea"],
        }
        for idx, values in sorted(evaluations.items())
    ]


def create_mask_comparison_browser(
    images: Sequence[np.ndarray],
    student_masks: dict[int, np.ndarray],
    gt_masks: Sequence[np.ndarray],
    labels: Sequence[str],
    *,
    figsize: tuple[float, float] = (5.8, 5.8),
    max_width: str = "680px",
) -> VBox | Label:
    saved_indices = sorted(student_masks)
    if not saved_indices:
        return Label(value="No student masks have been generated yet.")

    selected = saved_indices[0]
    fig = create_widget_figure(figsize, max_width)
    ax = fig.subplots()
    image_artist = ax.imshow(images[selected], cmap="gray")
    overlay_artist = ax.imshow(
        build_comparison_overlay(student_masks[selected], gt_masks[selected]),
        interpolation="nearest",
    )
    title = ax.set_title(f"Student vs GT | Slice {selected} | {labels[selected]}")
    ax.axis("off")

    slider = IntSlider(
        min=0,
        max=len(saved_indices) - 1,
        step=1,
        value=0,
        continuous_update=True,
        description="Mask",
        readout=True,
    )
    summary = Label(value="Green = overlap, amber = student-only, red = missed GT.")

    def update(change: dict[str, Any]) -> None:
        idx = saved_indices[int(change["new"])]
        image_artist.set_data(images[idx])
        overlay_artist.set_data(build_comparison_overlay(student_masks[idx], gt_masks[idx]))
        title.set_text(f"Student vs GT | Slice {idx} | {labels[idx]}")
        fig.canvas.draw_idle()

    slider.observe(update, names="value")
    return VBox([fig.canvas, slider, summary])


def show_widget(widget: Any) -> Any:
    display(widget)
    return widget
