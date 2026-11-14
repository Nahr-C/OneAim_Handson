from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image, ImageDraw


def polygon_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return area * 0.5


def segments_intersect(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> bool:
    def orient(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def on_segment(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> bool:
        return (
            min(p[0], r[0]) <= q[0] <= max(p[0], r[0])
            and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])
        )

    o1 = orient(a1, a2, b1)
    o2 = orient(a1, a2, b2)
    o3 = orient(b1, b2, a1)
    o4 = orient(b1, b2, a2)

    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0):
        return True

    epsilon = 1e-7
    if abs(o1) < epsilon and on_segment(a1, b1, a2):
        return True
    if abs(o2) < epsilon and on_segment(a1, b2, a2):
        return True
    if abs(o3) < epsilon and on_segment(b1, a1, b2):
        return True
    if abs(o4) < epsilon and on_segment(b1, a2, b2):
        return True
    return False


def validate_polygon(points: list[tuple[float, float]], shape: tuple[int, int]) -> tuple[bool, str]:
    if len(points) < 3:
        return False, "At least three points are required."

    height, width = shape
    for x, y in points:
        if not (0 <= x < width and 0 <= y < height):
            return False, "The contour extends outside the image bounds."

    if abs(polygon_area(points)) < 1.0:
        return False, "The contour area is too small."

    for index in range(len(points)):
        a1 = points[index]
        a2 = points[(index + 1) % len(points)]
        for other in range(index + 1, len(points)):
            next_other = (other + 1) % len(points)
            if index == other or (index + 1) % len(points) == other or index == next_other:
                continue
            if segments_intersect(a1, a2, points[other], points[next_other]):
                return False, "The contour self-intersects. Please adjust the polygon."
    return True, "Contour is valid."


def rasterize_polygon(points: list[tuple[float, float]], shape: tuple[int, int]) -> np.ndarray:
    height, width = shape
    image = Image.new("L", (width, height), color=0)
    draw = ImageDraw.Draw(image)
    draw.polygon(points, fill=255, outline=255)
    return (np.array(image) > 0).astype(np.uint8)


def dice_score(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    mask_a = mask_a.astype(bool)
    mask_b = mask_b.astype(bool)
    total = mask_a.sum() + mask_b.sum()
    if total == 0:
        return 1.0
    return float(2.0 * np.logical_and(mask_a, mask_b).sum() / total)


def iou_score(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    mask_a = mask_a.astype(bool)
    mask_b = mask_b.astype(bool)
    union = np.logical_or(mask_a, mask_b).sum()
    if union == 0:
        return 1.0
    return float(np.logical_and(mask_a, mask_b).sum() / union)


def evaluation_summary(student_mask: np.ndarray, gt_mask: np.ndarray) -> dict[str, Any]:
    return {
        "dice": round(dice_score(student_mask, gt_mask), 4),
        "iou": round(iou_score(student_mask, gt_mask), 4),
        "studentArea": int(student_mask.sum()),
        "groundTruthArea": int(gt_mask.sum()),
    }
