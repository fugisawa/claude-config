#!/usr/bin/env python3
"""Detect, rectify and crop photographed document pages conservatively.

The script never overwrites originals. It writes a rectified image only when a
credible four-corner contour is found; otherwise it writes an abstention record
so the caller can request visual review instead of guessing. An unreadable
image gets an ``error`` record and the run continues.

Usage:
  python rectify_photos.py INPUT [INPUT ...] --output-dir OUTPUT_DIR

Inputs may be image files or directories (scanned one level deep). Accepted
formats: JPG, JPEG, PNG, TIF, TIFF, WebP, BMP. A missing path or a run with no
usable input is a usage error (exit 2), never a silent empty success.
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "opencv-python-headless>=4.8",
#   "numpy>=1.24",
# ]
# ///
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from ocr_common import DEFAULT_MIN_AREA_RATIO, Source, parse_sources

MANIFEST_NAME = "rectification_manifest.json"
# A page contour should dominate alternatives and occupy most, but not all, of
# the photo. Borderless pages abstain and go to visual review.
MIN_DOMINANCE = 0.05


def order_points(points: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    sums = points.sum(axis=1)
    diffs = np.diff(points, axis=1).ravel()
    rect[0] = points[np.argmin(sums)]
    rect[2] = points[np.argmax(sums)]
    rect[1] = points[np.argmin(diffs)]
    rect[3] = points[np.argmax(diffs)]
    return rect


def warp_candidate(image: np.ndarray, contour: np.ndarray, min_area: float) -> tuple[float, np.ndarray, np.ndarray] | None:
    """Return (area, corners, warped image) when the contour is a credible convex quadrilateral."""
    area = cv2.contourArea(contour)
    if area < min_area:
        return None
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
    if len(approx) != 4 or not cv2.isContourConvex(approx):
        return None
    rect = order_points(approx.reshape(4, 2).astype("float32"))
    top = np.linalg.norm(rect[1] - rect[0])
    bottom = np.linalg.norm(rect[2] - rect[3])
    left = np.linalg.norm(rect[3] - rect[0])
    right = np.linalg.norm(rect[2] - rect[1])
    dst_w = max(int(max(top, bottom)), 1)
    dst_h = max(int(max(left, right)), 1)
    destination = np.array([[0, 0], [dst_w - 1, 0], [dst_w - 1, dst_h - 1], [0, dst_h - 1]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(rect, destination)
    return area, rect, cv2.warpPerspective(image, matrix, (dst_w, dst_h))


def page_candidates(image: np.ndarray, min_area_ratio: float) -> list[tuple[float, np.ndarray, np.ndarray]]:
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 35, 120)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = min_area_ratio * float(width * height)
    candidates = (warp_candidate(image, contour, min_area) for contour in contours)
    return sorted((c for c in candidates if c is not None), key=lambda item: item[0], reverse=True)


def rectify(source: Source, out: Path, min_area_ratio: float) -> dict[str, Any]:
    record = {"source": source.path.name, "source_path": source.resolved, "source_sha256": source.sha256}
    image = cv2.imread(str(source.path))
    if image is None:
        return {**record, "status": "error", "reason": "unreadable_image"}
    candidates = page_candidates(image, min_area_ratio)
    if not candidates:
        return {**record, "status": "abstain", "reason": "no_credible_four_corner_page"}
    best_area, corners, warped = candidates[0]
    second_area = candidates[1][0] if len(candidates) > 1 else 0.0
    height, width = image.shape[:2]
    area_ratio = best_area / float(width * height)
    dominance = (best_area - second_area) / best_area if best_area else 0.0
    if len(candidates) > 1 and dominance < MIN_DOMINANCE:
        return {**record, "status": "abstain", "reason": "ambiguous_page_contour", "area_ratio": area_ratio, "candidate_count": len(candidates)}
    target = out / f"{source.stem}_rectified.png"
    cv2.imwrite(str(target), warped)
    return {**record, "status": "rectified", "output": target.name, "area_ratio": area_ratio, "candidate_count": len(candidates), "corners_xy": corners.astype(int).tolist()}


def load_previous(manifest_path: Path) -> dict[str, dict[str, Any]]:
    """Records of an earlier run into the same directory, keyed like the new ones."""
    if not manifest_path.exists():
        return {}
    try:
        items = json.loads(manifest_path.read_text(encoding="utf-8")).get("files", [])
        return {item.get("source_path") or item["source"]: item for item in items}
    except (OSError, json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return {}


def write_manifest(manifest_path: Path, records: list[dict[str, Any]]) -> None:
    """Merge into an existing manifest so repeated runs into one directory stay auditable."""
    merged = {**load_previous(manifest_path), **{record["source_path"]: record for record in records}}
    files = [merged[key] for key in sorted(merged)]
    manifest_path.write_text(json.dumps({"files": files}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", type=Path, help="image files or directories")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--min-area-ratio", type=float, default=DEFAULT_MIN_AREA_RATIO)
    args = parser.parse_args()

    sources = parse_sources(parser, args.inputs)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = [rectify(source, args.output_dir, args.min_area_ratio) for source in sources]
    write_manifest(args.output_dir / MANIFEST_NAME, records)
    for record in records:
        print(record["source"], record["status"], record.get("reason", record.get("output", "")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
