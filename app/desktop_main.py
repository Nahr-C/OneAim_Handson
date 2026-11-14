from __future__ import annotations

import base64
import math
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QPoint, QPointF, Qt, Signal
from PySide6.QtGui import QAction, QColor, QImage, QPainter, QPainterPath, QPen, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.store import DatasetStore, organ_info


def data_url_to_pixmap(data_url: str | None) -> QPixmap | None:
    if not data_url:
        return None
    _, encoded = data_url.split(",", 1)
    raw = base64.b64decode(encoded)
    image = QImage.fromData(raw, "PNG")
    if image.isNull():
        return None
    return QPixmap.fromImage(image)


class SliceViewer(QWidget):
    polygonChanged = Signal()
    statusChanged = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(720, 720)
        self.base_pixmap: QPixmap | None = None
        self.gt_pixmap: QPixmap | None = None
        self.pdff_pixmap: QPixmap | None = None
        self.comparison_pixmap: QPixmap | None = None
        self.show_gt = True
        self.show_pdff = True
        self.scale_factor = 1.0
        self.offset = QPointF(0.0, 0.0)
        self.dragging = False
        self.drag_anchor = QPoint()
        self.start_offset = QPointF(0.0, 0.0)
        self.image_size = QPointF(0.0, 0.0)
        self.polygon: list[QPointF] = []
        self.polygon_closed = False
        self.gt_contour: list[list[int]] = []
        self.student_contour: list[list[int]] = []

    def set_slice_data(
        self,
        base: QPixmap | None,
        gt: QPixmap | None,
        pdff: QPixmap | None,
        gt_contour: list[list[int]],
    ) -> None:
        self.base_pixmap = base
        self.gt_pixmap = gt
        self.pdff_pixmap = pdff
        self.gt_contour = gt_contour
        self.student_contour = []
        self.comparison_pixmap = None
        self.clear_polygon()
        if base and not base.isNull():
            self.image_size = QPointF(base.width(), base.height())
        else:
            self.image_size = QPointF(0.0, 0.0)
        self.fit_to_view()

    def set_overlays(self, show_gt: bool, show_pdff: bool) -> None:
        self.show_gt = show_gt
        self.show_pdff = show_pdff
        self.update()

    def set_student_contour(self, contour: list[list[int]]) -> None:
        self.student_contour = contour
        self.update()

    def set_comparison_overlay(self, pixmap: QPixmap | None) -> None:
        self.comparison_pixmap = pixmap
        self.update()

    def fit_to_view(self) -> None:
        if not self.base_pixmap or self.base_pixmap.isNull():
            return
        view_width = max(1, self.width())
        view_height = max(1, self.height())
        pix_width = self.base_pixmap.width()
        pix_height = self.base_pixmap.height()
        self.scale_factor = min(view_width / pix_width, view_height / pix_height) * 0.92
        self.offset = QPointF(
            view_width / 2 - pix_width * self.scale_factor / 2,
            view_height / 2 - pix_height * self.scale_factor / 2,
        )
        self.update()

    def zoom_at(self, multiplier: float, anchor: QPointF | None = None) -> None:
        if not self.base_pixmap or self.base_pixmap.isNull():
            return
        if anchor is None:
            anchor = QPointF(self.width() / 2, self.height() / 2)
        image_point = self.canvas_to_image(anchor)
        next_scale = max(0.2, min(12.0, self.scale_factor * multiplier))
        self.scale_factor = next_scale
        self.offset = QPointF(anchor.x() - image_point.x() * next_scale, anchor.y() - image_point.y() * next_scale)
        self.update()

    def canvas_to_image(self, point: QPointF) -> QPointF:
        return QPointF(
            (point.x() - self.offset.x()) / self.scale_factor,
            (point.y() - self.offset.y()) / self.scale_factor,
        )

    def image_to_canvas(self, point: QPointF) -> QPointF:
        return QPointF(
            point.x() * self.scale_factor + self.offset.x(),
            point.y() * self.scale_factor + self.offset.y(),
        )

    def _within_image(self, point: QPointF) -> bool:
        return (
            0.0 <= point.x() < self.image_size.x()
            and 0.0 <= point.y() < self.image_size.y()
        )

    def clear_polygon(self) -> None:
        self.polygon = []
        self.polygon_closed = False
        self.student_contour = []
        self.update()
        self.polygonChanged.emit()

    def undo_point(self) -> None:
        if self.polygon_closed:
            self.polygon_closed = False
        elif self.polygon:
            self.polygon.pop()
        self.student_contour = []
        self.update()
        self.polygonChanged.emit()

    def close_polygon(self) -> bool:
        if len(self.polygon) < 3:
            self.statusChanged.emit("At least three points are required to close the contour.")
            return False
        self.polygon_closed = True
        self.update()
        self.polygonChanged.emit()
        self.statusChanged.emit("Contour closed. Evaluate to compare with the GT mask.")
        return True

    def get_polygon_points(self) -> list[list[float]]:
        return [[point.x(), point.y()] for point in self.polygon]

    def _draw_landmarks(self, painter: QPainter, points: list[list[int]], color: QColor, radius: float) -> None:
        if not points:
            return
        pen = QPen(color)
        pen.setWidthF(0.0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        for x, y in points:
            painter.drawEllipse(QPointF(float(x), float(y)), radius, radius)

    def _draw_polygon(self, painter: QPainter) -> None:
        if not self.polygon:
            return
        pen = QPen(QColor("#ffbe49"))
        pen.setWidthF(2.0 / self.scale_factor)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        path.moveTo(self.polygon[0])
        for point in self.polygon[1:]:
            path.lineTo(point)
        if self.polygon_closed and len(self.polygon) > 2:
            path.closeSubpath()
        painter.drawPath(path)

        for index, point in enumerate(self.polygon):
            painter.setBrush(QColor("#ffbe49"))
            radius = 4.5 / self.scale_factor if index == 0 else 3.6 / self.scale_factor
            painter.drawEllipse(point, radius, radius)

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#041019"))
        if not self.base_pixmap or self.base_pixmap.isNull():
            painter.setPen(QColor("#8ca6b8"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No slice loaded")
            return

        painter.translate(self.offset)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.drawPixmap(0, 0, self.base_pixmap)
        if self.show_pdff and self.pdff_pixmap and not self.pdff_pixmap.isNull():
            painter.drawPixmap(0, 0, self.pdff_pixmap)
        if self.show_gt and self.gt_pixmap and not self.gt_pixmap.isNull():
            painter.drawPixmap(0, 0, self.gt_pixmap)
        if self.comparison_pixmap and not self.comparison_pixmap.isNull():
            painter.drawPixmap(0, 0, self.comparison_pixmap)

        if self.show_gt:
            self._draw_landmarks(painter, self.gt_contour, QColor("#42d7d0"), 1.8 / self.scale_factor)
        self._draw_landmarks(painter, self.student_contour, QColor("#ffbe49"), 1.8 / self.scale_factor)
        self._draw_polygon(painter)

    def wheelEvent(self, event: QWheelEvent) -> None:
        multiplier = 1.08 if event.angleDelta().y() > 0 else 1 / 1.08
        self.zoom_at(multiplier, event.position())
        event.accept()

    def mousePressEvent(self, event: Any) -> None:
        pan_triggered = event.button() in {Qt.MiddleButton, Qt.RightButton} or (
            event.button() == Qt.LeftButton and bool(event.modifiers() & Qt.ShiftModifier)
        )
        if pan_triggered:
            self.dragging = True
            self.drag_anchor = event.pos()
            self.start_offset = QPointF(self.offset)
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() != Qt.LeftButton or self.base_pixmap is None:
            return

        if self.polygon_closed:
            self.statusChanged.emit("Reset or undo the contour before adding more points.")
            return

        image_point = self.canvas_to_image(event.position())
        if not self._within_image(image_point):
            return

        if len(self.polygon) >= 3:
            first_canvas = self.image_to_canvas(self.polygon[0])
            if (
                abs(first_canvas.x() - event.position().x()) ** 2
                + abs(first_canvas.y() - event.position().y()) ** 2
            ) ** 0.5 < 14:
                self.close_polygon()
                return

        self.polygon.append(image_point)
        self.student_contour = []
        self.update()
        self.polygonChanged.emit()
        self.statusChanged.emit("Contour point added. Click near the first point or press Close Contour.")

    def mouseMoveEvent(self, event: Any) -> None:
        if not self.dragging:
            return
        delta = event.pos() - self.drag_anchor
        self.offset = QPointF(self.start_offset.x() + delta.x(), self.start_offset.y() + delta.y())
        self.update()

    def mouseReleaseEvent(self, event: Any) -> None:
        self.dragging = False
        self.unsetCursor()

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        if self.base_pixmap and not self.base_pixmap.isNull():
            self.fit_to_view()


class VolumeViewer(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(320, 260)
        self.points: list[list[float]] = []
        self.yaw = -0.6
        self.pitch = 0.55
        self.zoom = 1.8
        self.dragging = False
        self.drag_anchor = QPoint()
        self.start_yaw = self.yaw
        self.start_pitch = self.pitch

    def set_points(self, points: list[list[float]]) -> None:
        self.points = points
        self.update()

    def _project_point(self, point: list[float]) -> tuple[float, float, float]:
        x, y, z = point
        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)
        cos_pitch = math.cos(self.pitch)
        sin_pitch = math.sin(self.pitch)
        x1 = x * cos_yaw - z * sin_yaw
        z1 = x * sin_yaw + z * cos_yaw
        y1 = y * cos_pitch - z1 * sin_pitch
        z2 = y * sin_pitch + z1 * cos_pitch
        perspective = 180 * self.zoom / (z2 + 3.2)
        return x1 * perspective, y1 * perspective, z2 + 2.5

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#07111a"))
        if not self.points:
            painter.setPen(QColor("#8ca6b8"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No 3D GT surface available")
            return

        projected = sorted((self._project_point(point) for point in self.points), key=lambda item: item[2])
        width = self.width()
        height = self.height()
        for x, y, depth in projected:
            alpha = max(0.12, 0.85 - depth * 0.25)
            radius = max(1.1, 4.5 - depth * 0.9)
            color = QColor(66, 215, 208)
            color.setAlphaF(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(width / 2 + x, height / 2 + y), radius, radius)

    def mousePressEvent(self, event: Any) -> None:
        if event.button() != Qt.LeftButton:
            return
        self.dragging = True
        self.drag_anchor = event.pos()
        self.start_yaw = self.yaw
        self.start_pitch = self.pitch
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: Any) -> None:
        if not self.dragging:
            return
        self.yaw = self.start_yaw + (event.pos().x() - self.drag_anchor.x()) * 0.01
        self.pitch = self.start_pitch + (event.pos().y() - self.drag_anchor.y()) * 0.01
        self.update()

    def mouseReleaseEvent(self, event: Any) -> None:
        self.dragging = False
        self.unsetCursor()

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.zoom = max(0.8, min(4.5, self.zoom * (1.08 if event.angleDelta().y() > 0 else 1 / 1.08)))
        self.update()
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self, store: DatasetStore) -> None:
        super().__init__()
        self.store = store
        self.cases = self.store.list_cases()
        self.case_detail: dict[str, Any] | None = None
        self.slice_payload: dict[str, Any] | None = None
        self.volume_payload: dict[str, Any] | None = None
        self.current_patient = self.cases[0]["patientId"] if self.cases else None
        self.current_sequence = self.cases[0]["sequences"][0]["name"] if self.cases and self.cases[0]["sequences"] else None
        self.current_organ = "liver"
        self.current_index = 0

        self.setWindowTitle("Liver MRI Desktop Studio")
        self.resize(1600, 960)
        self._build_ui()
        self._populate_controls()
        self._load_case_detail()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(340)

        form = QFormLayout()
        self.patient_select = QComboBox()
        self.sequence_select = QComboBox()
        self.organ_select = QComboBox()
        form.addRow("Patient", self.patient_select)
        form.addRow("Sequence", self.sequence_select)
        form.addRow("Organ", self.organ_select)
        left_layout.addLayout(form)

        self.slice_label = QLabel("Slice -")
        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setMinimum(0)
        self.slice_slider.setMaximum(0)
        left_layout.addWidget(self.slice_label)
        left_layout.addWidget(self.slice_slider)

        slice_buttons = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        slice_buttons.addWidget(self.prev_button)
        slice_buttons.addWidget(self.next_button)
        left_layout.addLayout(slice_buttons)

        self.show_gt_toggle = QCheckBox("Show GT overlay")
        self.show_gt_toggle.setChecked(True)
        self.show_pdff_toggle = QCheckBox("Show approximate PDFF")
        self.show_pdff_toggle.setChecked(True)
        left_layout.addWidget(self.show_gt_toggle)
        left_layout.addWidget(self.show_pdff_toggle)

        self.spacing_label = QLabel("Spacing: -")
        self.thickness_label = QLabel("Thickness: -")
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        left_layout.addWidget(self.spacing_label)
        left_layout.addWidget(self.thickness_label)
        left_layout.addWidget(self.status_label)
        left_layout.addStretch(1)

        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        self.viewer = SliceViewer()
        self.volume_viewer = VolumeViewer()
        toolbar = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.fit_button = QPushButton("Fit View")
        toolbar.addWidget(self.zoom_in_button)
        toolbar.addWidget(self.zoom_out_button)
        toolbar.addWidget(self.fit_button)
        toolbar.addStretch(1)
        center_layout.addLayout(toolbar)
        center_layout.addWidget(self.viewer, stretch=1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setMaximumWidth(360)

        self.undo_button = QPushButton("Undo Point")
        self.reset_button = QPushButton("Reset Contour")
        self.close_button = QPushButton("Close Contour")
        self.evaluate_button = QPushButton("Evaluate")

        draw_buttons_a = QHBoxLayout()
        draw_buttons_a.addWidget(self.undo_button)
        draw_buttons_a.addWidget(self.reset_button)
        draw_buttons_b = QHBoxLayout()
        draw_buttons_b.addWidget(self.close_button)
        draw_buttons_b.addWidget(self.evaluate_button)

        self.dice_label = QLabel("Dice: --")
        self.iou_label = QLabel("IoU: --")
        self.gt_area_label = QLabel("GT Area: --")
        self.user_area_label = QLabel("User Area: --")
        self.gt_mean_label = QLabel("GT Mean: --")
        self.gt_median_label = QLabel("GT Median: --")
        self.user_mean_label = QLabel("User Mean: --")
        self.user_median_label = QLabel("User Median: --")
        self.pdff_note_label = QLabel("Approximate PDFF is available only on dual-echo T1 data.")
        self.pdff_note_label.setWordWrap(True)
        self.teaching_text_label = QLabel("Browse a case to inspect anatomy, GT, and PDFF overlays.")
        self.teaching_text_label.setWordWrap(True)
        self.surface_points_label = QLabel("Surface samples: --")
        self.volume_slices_label = QLabel("Slice stack: --")
        self.volume_box_label = QLabel("Bounding box: --")

        right_layout.addWidget(QLabel("Drawing"))
        right_layout.addLayout(draw_buttons_a)
        right_layout.addLayout(draw_buttons_b)
        right_layout.addWidget(QLabel("Evaluation"))
        for widget in [
            self.dice_label,
            self.iou_label,
            self.gt_area_label,
            self.user_area_label,
            QLabel("Fat Fraction Summary"),
            self.gt_mean_label,
            self.gt_median_label,
            self.user_mean_label,
            self.user_median_label,
            self.pdff_note_label,
            QLabel("3D GT Surface"),
            self.volume_viewer,
            self.surface_points_label,
            self.volume_slices_label,
            self.volume_box_label,
            QLabel("Teaching Notes"),
            self.teaching_text_label,
        ]:
            right_layout.addWidget(widget)
        right_layout.addStretch(1)

        root.addWidget(left_panel)
        root.addWidget(center_panel, stretch=1)
        root.addWidget(right_panel)

        self.patient_select.currentIndexChanged.connect(self._on_patient_changed)
        self.sequence_select.currentIndexChanged.connect(self._on_sequence_changed)
        self.organ_select.currentIndexChanged.connect(self._on_organ_changed)
        self.slice_slider.valueChanged.connect(self._on_slice_changed)
        self.prev_button.clicked.connect(self._go_previous)
        self.next_button.clicked.connect(self._go_next)
        self.show_gt_toggle.toggled.connect(self._refresh_overlay_visibility)
        self.show_pdff_toggle.toggled.connect(self._refresh_overlay_visibility)
        self.zoom_in_button.clicked.connect(lambda: self.viewer.zoom_at(1.12))
        self.zoom_out_button.clicked.connect(lambda: self.viewer.zoom_at(1 / 1.12))
        self.fit_button.clicked.connect(self.viewer.fit_to_view)
        self.undo_button.clicked.connect(self._undo_polygon)
        self.reset_button.clicked.connect(self._reset_polygon)
        self.close_button.clicked.connect(self._close_polygon)
        self.evaluate_button.clicked.connect(self._evaluate_polygon)
        self.viewer.polygonChanged.connect(self._on_polygon_changed)
        self.viewer.statusChanged.connect(self._set_status)

        fit_action = QAction("Fit View", self)
        fit_action.setShortcut("F")
        fit_action.triggered.connect(self.viewer.fit_to_view)
        self.addAction(fit_action)

        undo_action = QAction("Undo Point", self)
        undo_action.setShortcut("Z")
        undo_action.triggered.connect(self._undo_polygon)
        self.addAction(undo_action)

        reset_action = QAction("Reset Contour", self)
        reset_action.setShortcut("R")
        reset_action.triggered.connect(self._reset_polygon)
        self.addAction(reset_action)

        close_action = QAction("Close Contour", self)
        close_action.setShortcut("C")
        close_action.triggered.connect(self._close_polygon)
        self.addAction(close_action)

        eval_action = QAction("Evaluate", self)
        eval_action.setShortcut("Return")
        eval_action.triggered.connect(self._evaluate_polygon)
        self.addAction(eval_action)

    def _populate_controls(self) -> None:
        self.patient_select.blockSignals(True)
        self.patient_select.clear()
        for item in self.cases:
            self.patient_select.addItem(f"Patient {item['patientId']}", item["patientId"])
        if self.current_patient:
            index = self.patient_select.findData(self.current_patient)
            self.patient_select.setCurrentIndex(max(0, index))
        self.patient_select.blockSignals(False)

        self.organ_select.blockSignals(True)
        self.organ_select.clear()
        for organ in organ_info():
            self.organ_select.addItem(f"{organ['name']} ({organ['value']})", organ["key"])
        self.organ_select.setCurrentIndex(max(0, self.organ_select.findData(self.current_organ)))
        self.organ_select.blockSignals(False)

        self._populate_sequences()

    def _populate_sequences(self) -> None:
        patient = next((item for item in self.cases if item["patientId"] == self.current_patient), None)
        sequences = patient["sequences"] if patient else []
        self.sequence_select.blockSignals(True)
        self.sequence_select.clear()
        for sequence in sequences:
            label = sequence["name"]
            if sequence.get("supportsPdff"):
                label += " [PDFF]"
            self.sequence_select.addItem(label, sequence["name"])
        if sequences:
            if self.current_sequence not in [item["name"] for item in sequences]:
                self.current_sequence = sequences[0]["name"]
            self.sequence_select.setCurrentIndex(max(0, self.sequence_select.findData(self.current_sequence)))
        self.sequence_select.blockSignals(False)

    def _load_case_detail(self) -> None:
        if not self.current_patient or not self.current_sequence:
            return
        try:
            self.case_detail = self.store.get_case_detail(self.current_patient, self.current_sequence)
        except Exception as exc:
            QMessageBox.critical(self, "Load Error", str(exc))
            return
        self.slice_slider.blockSignals(True)
        self.slice_slider.setMaximum(max(0, self.case_detail["sliceCount"] - 1))
        self.current_index = min(self.current_index, self.case_detail["sliceCount"] - 1)
        self.slice_slider.setValue(self.current_index)
        self.slice_slider.blockSignals(False)
        self._load_slice()
        self._load_volume()

    def _load_slice(self) -> None:
        if not self.current_patient or not self.current_sequence:
            return
        self.slice_payload = self.store.get_slice_payload(self.current_patient, self.current_sequence, self.current_index, self.current_organ)
        payload = self.slice_payload
        self.slice_label.setText(f"Slice {self.current_index + 1} / {payload['sliceCount']}  |  {payload['basename']}")
        self.spacing_label.setText(f"Spacing: {payload['pixelSpacing'][0]:.2f} x {payload['pixelSpacing'][1]:.2f} mm")
        self.thickness_label.setText(f"Thickness: {payload['sliceThickness']:.2f} mm")
        self.teaching_text_label.setText(payload["teachingText"])
        self.show_pdff_toggle.setEnabled(payload["supportsPdff"])
        if not payload["supportsPdff"]:
            self.show_pdff_toggle.setChecked(False)

        self.viewer.set_slice_data(
            data_url_to_pixmap(payload["image"]),
            data_url_to_pixmap(payload["gtOverlay"]),
            data_url_to_pixmap(payload["pdffOverlay"]),
            payload["gtContour"],
        )
        self._refresh_overlay_visibility()
        self._reset_metrics(payload.get("gtPdffStats"), payload["gtMaskArea"])
        self._set_status("Left click adds contour points. Shift + left drag, middle drag, or right drag pans. Mouse wheel zooms.")

    def _load_volume(self) -> None:
        if not self.current_patient or not self.current_sequence:
            return
        self.volume_payload = self.store.get_volume_payload(self.current_patient, self.current_sequence, self.current_organ)
        self.volume_viewer.set_points(self.volume_payload.get("points", []))
        self.surface_points_label.setText(f"Surface samples: {len(self.volume_payload.get('points', [])):,}")
        self.volume_slices_label.setText(f"Slice stack: {self.volume_payload.get('sliceCount', 0)}")
        bbox = self.volume_payload.get("bbox", [0, 0, 0])
        self.volume_box_label.setText(f"Bounding box: {bbox[0]:.1f} x {bbox[1]:.1f} x {bbox[2]:.1f} mm")

    def _reset_metrics(self, gt_stats: dict[str, Any] | None, gt_area: int) -> None:
        self.dice_label.setText("Dice: --")
        self.iou_label.setText("IoU: --")
        self.gt_area_label.setText(f"GT Area: {gt_area:,}")
        self.user_area_label.setText("User Area: --")
        self.gt_mean_label.setText(f"GT Mean: {gt_stats['mean']:.2f}%" if gt_stats else "GT Mean: --")
        self.gt_median_label.setText(f"GT Median: {gt_stats['median']:.2f}%" if gt_stats else "GT Median: --")
        self.user_mean_label.setText("User Mean: --")
        self.user_median_label.setText("User Median: --")
        if self.slice_payload and self.slice_payload["supportsPdff"]:
            if gt_stats:
                self.pdff_note_label.setText("Approximate PDFF is available on this slice. GT statistics are shown now, and user statistics will appear after evaluation.")
            else:
                self.pdff_note_label.setText("Approximate PDFF is available on this slice, but the selected GT mask is empty here.")
        else:
            self.pdff_note_label.setText("This sequence does not contain paired in-phase/out-phase images, so no approximate PDFF map is available.")

    def _set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _refresh_overlay_visibility(self) -> None:
        self.viewer.set_overlays(self.show_gt_toggle.isChecked(), self.show_pdff_toggle.isChecked())

    def _on_polygon_changed(self) -> None:
        self.dice_label.setText("Dice: --")
        self.iou_label.setText("IoU: --")
        self.user_area_label.setText("User Area: --")
        self.user_mean_label.setText("User Mean: --")
        self.user_median_label.setText("User Median: --")
        self.viewer.set_comparison_overlay(None)

    def _undo_polygon(self) -> None:
        self.viewer.undo_point()

    def _reset_polygon(self) -> None:
        self.viewer.clear_polygon()
        self._set_status("Contour reset.")

    def _close_polygon(self) -> None:
        self.viewer.close_polygon()

    def _evaluate_polygon(self) -> None:
        if not self.slice_payload:
            return
        if not self.viewer.polygon_closed:
            self._set_status("Close the contour before evaluation.")
            return
        try:
            result = self.store.evaluate(
                self.current_patient,
                self.current_sequence,
                self.current_index,
                self.viewer.get_polygon_points(),
                self.current_organ,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Evaluation Error", str(exc))
            return

        if not result.get("ok"):
            QMessageBox.warning(self, "Invalid Contour", result.get("message", "Evaluation failed."))
            self._set_status(result.get("message", "Evaluation failed."))
            return

        self.viewer.set_student_contour(result.get("studentContour", []))
        self.viewer.set_comparison_overlay(data_url_to_pixmap(result.get("comparisonOverlay")))
        self.dice_label.setText(f"Dice: {result['dice']:.3f}")
        self.iou_label.setText(f"IoU: {result['iou']:.3f}")
        self.user_area_label.setText(f"User Area: {result['studentArea']:,}")
        student_stats = result.get("studentPdffStats")
        self.user_mean_label.setText(f"User Mean: {student_stats['mean']:.2f}%" if student_stats else "User Mean: --")
        self.user_median_label.setText(f"User Median: {student_stats['median']:.2f}%" if student_stats else "User Median: --")
        if student_stats:
            self.pdff_note_label.setText("User contour fat-fraction statistics are shown alongside the GT statistics for this slice.")
        self._set_status("Evaluation complete. Amber contour shows your result against the GT landmarks.")

    def _on_patient_changed(self) -> None:
        self.current_patient = self.patient_select.currentData()
        self.current_index = 0
        self._populate_sequences()
        self._load_case_detail()

    def _on_sequence_changed(self) -> None:
        self.current_sequence = self.sequence_select.currentData()
        self.current_index = 0
        self._load_case_detail()

    def _on_organ_changed(self) -> None:
        self.current_organ = self.organ_select.currentData()
        self.current_index = 0
        self._load_case_detail()

    def _on_slice_changed(self, value: int) -> None:
        self.current_index = int(value)
        self._load_slice()

    def _go_previous(self) -> None:
        if self.current_index <= 0:
            return
        self.current_index -= 1
        self.slice_slider.setValue(self.current_index)

    def _go_next(self) -> None:
        if not self.case_detail or self.current_index >= self.case_detail["sliceCount"] - 1:
            return
        self.current_index += 1
        self.slice_slider.setValue(self.current_index)


def main() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data" / "sample_data"
    app = QApplication(sys.argv)
    window = MainWindow(DatasetStore(data_dir))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
