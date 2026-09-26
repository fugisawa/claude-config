#!/usr/bin/env python3
"""Local-first OCR ensemble for photographed pages.

Uses Pillow preprocessing, RapidOCR, and optionally Tesseract with the requested
language pack. It preserves raw candidates, boxes, confidences and preprocessing
provenance; it does not silently correct OCR text. An image that cannot be
processed gets an ``error`` record and the run continues.

Usage:
  python ocr_photos.py INPUT [INPUT ...] --output-dir OUTPUT_DIR
  python ocr_photos.py page.jpg --output-dir OUTPUT_DIR --tesseract-bin /path/to/tesseract
  python ocr_photos.py INPUT_DIR --output-dir OUTPUT_DIR --no-tesseract   # RapidOCR only, for debugging

Inputs may be image files or directories (JPG, JPEG, PNG, TIF, TIFF, WebP, BMP).

Language contract: ``--lang`` reaches Tesseract only. RapidOCR runs its bundled
Chinese/English recognition model and ignores the flag. ``language_applied_by``
names Tesseract only when at least one Tesseract invocation actually succeeded
with the requested pack — a present binary with a missing pack counts as not
applied. Status ``completed_language_unapplied`` then exits 3.

Orientation: phone photos of open books are often sideways with no EXIF flag, and
neither engine compensates. ``--rotate auto`` (default) decides on a small copy: RapidOCR
box geometry says whether the text runs horizontally (upright or upside down) or
vertically, and Tesseract's confidence — it reads upside-down text badly — picks the
member of that pair. Without Tesseract an upside-down photo may stay upside down. The
angle applied is recorded per image as ``rotation_applied``.

Exit codes: 0 completed; 2 usage error, or partial run (an image errored);
3 completed, requested language unapplied.
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pillow>=10.1",
#   "numpy>=1.24",
#   "rapidocr-onnxruntime>=1.3,<2",
# ]
# ///
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from ocr_common import DEFAULT_LANG, DEFAULT_PSM, DEFAULT_SCALE, Source, parse_sources

EXIT_PARTIAL = 2
EXIT_LANGUAGE_UNAPPLIED = 3
STATUS_COMPLETED = "completed"
STATUS_LANGUAGE_UNAPPLIED = "completed_language_unapplied"
STDERR_TAIL = 400
ROTATIONS = (0, 90, 180, 270)
ROTATION_CHOICES = ("auto", *(str(r) for r in ROTATIONS))
DETECT_MAX_SIDE = 1000
KEEP_UPRIGHT_RATIO = 0.9  # rotate only when another orientation reads clearly better
HORIZONTAL_BOX_RATIO = 1.5  # a text box at least this much wider than tall runs horizontally


class EngineOptions(NamedTuple):
    lang: str
    psm: tuple[int, ...]
    tessdata: str | None
    scale: int
    rotate: str


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as opened:
        return ImageOps.exif_transpose(opened).convert("RGB")


def horizontal_chars(image: Image.Image, rapid: Any) -> float:
    """Characters RapidOCR finds inside boxes that run horizontally. RapidOCR reads sideways
    text almost as confidently as upright text, so confidence cannot tell; box shape can."""
    result, _ = rapid(np.asarray(image)[:, :, ::-1])  # RapidOCR expects BGR
    total = 0.0
    for box, text, _score in result or []:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        width, height = max(xs) - min(xs), max(ys) - min(ys)
        if width >= HORIZONTAL_BOX_RATIO * max(height, 1):
            total += len(text)
    return total


def tesseract_confidence(image: Image.Image, binary: str, options: EngineOptions) -> float:
    """Mean word confidence on a small copy: upside-down text reads as low-confidence junk."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        image.save(handle.name)
        words = tesseract_candidate(Path(handle.name), binary, options, 6)["words"]
    Path(handle.name).unlink(missing_ok=True)
    return sum(w["confidence"] for w in words) / len(words) if words else 0.0


def detect_rotation(image: Image.Image, rapid: Any, tesseract: str | None, options: EngineOptions) -> int:
    """Counter-clockwise degrees that make the page upright, judged on a small copy."""
    small = image.copy()
    small.thumbnail((DETECT_MAX_SIDE, DETECT_MAX_SIDE))
    rotated = {angle: small.rotate(angle, expand=True) for angle in ROTATIONS}
    horizontal = {angle: horizontal_chars(img, rapid) for angle, img in rotated.items()}
    family = (0, 180) if horizontal[0] + horizontal[180] >= horizontal[90] + horizontal[270] else (90, 270)
    if tesseract:
        scores = {angle: tesseract_confidence(rotated[angle], tesseract, options) for angle in family}
    else:
        scores = {angle: horizontal[angle] for angle in family}
    best = max(family, key=scores.get)
    if family[0] == 0 and scores[0] >= KEEP_UPRIGHT_RATIO * scores[best]:
        return 0
    return best


def preprocess(image: Image.Image, out: Path, scale: int, stem: str, rotation: int) -> dict[str, Path]:
    base = image.rotate(rotation, expand=True) if rotation else image
    base = base.resize((base.width * scale, base.height * scale), Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(base)
    contrast = ImageOps.autocontrast(gray)
    contrast = ImageEnhance.Sharpness(contrast).enhance(1.35)
    denoised = contrast.filter(ImageFilter.MedianFilter(size=3))
    variants = {"color": base, "gray": gray, "contrast": contrast, "denoised": denoised}
    paths: dict[str, Path] = {}
    for name, image in variants.items():
        target = out / f"{stem}_{name}.png"
        image.save(target)
        paths[name] = target
    return paths


def rapidocr_candidate(path: Path, engine: Any) -> dict[str, Any]:
    result, stage_timings = engine(str(path))
    lines = [{"text": text, "confidence": float(score), "box": box} for box, text, score in (result or [])]
    return {"engine": "rapidocr", "source": path.name, "elapsed_stages_s": stage_timings, "lines": lines}


def parse_words(stdout: str) -> list[dict[str, Any]]:
    """Word rows (level 5) of Tesseract's TSV, with boxes and the ids that place them on a line."""
    rows = stdout.splitlines()
    if not rows:
        return []
    header = rows[0].split("\t")
    words = []
    for row in rows[1:]:
        values = row.split("\t")
        if len(values) != len(header):
            continue
        item = dict(zip(header, values))
        text = item.get("text", "").strip()
        if not text:
            continue
        try:
            confidence = float(item.get("conf", "-1"))
        except ValueError:
            confidence = -1.0
        words.append({
            "text": text,
            "confidence": confidence,
            "box": {"x": int(item.get("left", 0)), "y": int(item.get("top", 0)), "w": int(item.get("width", 0)), "h": int(item.get("height", 0))},
            "level": int(item.get("level", 0)),
            "line_id": [int(item.get(k, 0)) for k in ("page_num", "block_num", "par_num", "line_num")],
        })
    return words


def group_lines(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rebuild text lines from words sharing (page, block, paragraph, line), in TSV order."""
    grouped: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for word in words:
        grouped.setdefault(tuple(word["line_id"]), []).append(word)
    lines = []
    for members in grouped.values():
        boxes = [w["box"] for w in members]
        x, y = min(b["x"] for b in boxes), min(b["y"] for b in boxes)
        lines.append({
            "text": " ".join(w["text"] for w in members),
            "confidence": sum(w["confidence"] for w in members) / len(members),
            "box": {"x": x, "y": y, "w": max(b["x"] + b["w"] for b in boxes) - x, "h": max(b["y"] + b["h"] for b in boxes) - y},
            "word_count": len(members),
        })
    return lines


def tesseract_candidate(path: Path, binary: str, options: EngineOptions, psm: int) -> dict[str, Any]:
    env = {**os.environ, "TESSDATA_PREFIX": options.tessdata} if options.tessdata else os.environ.copy()
    cmd = [binary, str(path), "stdout", "-l", options.lang, "--psm", str(psm), "tsv"]
    started = time.time()
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True, check=False)
    words = parse_words(proc.stdout) if proc.returncode == 0 else []
    return {
        "engine": "tesseract",
        "source": path.name,
        "lang": options.lang,
        "psm": psm,
        "elapsed_s": time.time() - started,
        "returncode": proc.returncode,
        "stderr": proc.stderr,
        "lines": group_lines(words),
        "words": words,
    }


def collect_candidates(variants: dict[str, Path], rapid: Any, tesseract: str | None, options: EngineOptions) -> list[dict[str, Any]]:
    candidates = []
    for variant, image_path in variants.items():
        candidates.append({"variant": variant, **rapidocr_candidate(image_path, rapid)})
        if tesseract:
            for psm in options.psm:
                candidates.append({"variant": variant, **tesseract_candidate(image_path, tesseract, options, psm)})
    return candidates


def tesseract_outcome(candidates: list[dict[str, Any]]) -> tuple[bool, str]:
    """Did any Tesseract invocation succeed with output? If none did, why (first stderr tail)."""
    runs = [c for c in candidates if c["engine"] == "tesseract"]
    if any(c["returncode"] == 0 and c["lines"] for c in runs):
        return True, ""
    failure = next((c["stderr"].strip()[-STDERR_TAIL:] for c in runs if c["stderr"].strip()), "no output")
    return False, failure


def heuristic_best(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Diagnostic only: line count and confidence are not accuracy. Never select on this alone."""
    best = max(candidates, key=lambda c: (len(c["lines"]), sum(float(x.get("confidence", 0)) for x in c["lines"])))
    return {"engine": best["engine"], "variant": best["variant"], "line_count": len(best["lines"])}


def write_candidates(candidates_dir: Path, stem: str, payload: dict[str, Any]) -> None:
    (candidates_dir / f"{stem}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for index, candidate in enumerate(payload["candidates"]):
        text = "\n".join(line["text"] for line in candidate["lines"])
        (candidates_dir / f"{stem}_{index:03d}_{candidate['engine']}_{candidate['variant']}.txt").write_text(text, encoding="utf-8")


def process_source(source: Source, rapid: Any, tesseract: str | None, options: EngineOptions, out: Path) -> dict[str, Any]:
    """One image in, one record out; a failure becomes an ``error`` record, not a crash."""
    record = {"source": source.path.name, "source_path": source.resolved, "sha256": source.sha256, "stem": source.stem}
    try:
        image = load_image(source.path)
        rotation = detect_rotation(image, rapid, tesseract, options) if options.rotate == "auto" else int(options.rotate)
        variants = preprocess(image, out / "preprocessed", options.scale, source.stem, rotation)
        candidates = collect_candidates(variants, rapid, tesseract, options)
    except Exception as exc:  # the boundary is one image; the reason is kept, the batch goes on
        print(f"error: {source.path.name}: {exc!r}", file=sys.stderr)
        return {**record, "status": "error", "reason": repr(exc), "candidate_count": 0}
    record = {**record, "rotation_applied": rotation}
    write_candidates(out / "candidates", source.stem, {**record, "candidates": candidates})
    tesseract_ok, tesseract_error = tesseract_outcome(candidates) if tesseract else (False, "")
    return {
        **record,
        "status": "ok",
        "candidate_count": len(candidates),
        "tesseract_ok": tesseract_ok,
        "tesseract_error": tesseract_error,
        "best_candidate": heuristic_best(candidates),
    }


def language_report(lang: str, tesseract: str | None, files: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Which engines honoured ``--lang``, judged by actual output, and what the reader must be told."""
    succeeded = any(f.get("tesseract_ok") for f in files)
    applied = ["tesseract"] if succeeded else []
    warnings = []
    if not tesseract:
        warnings.append("Tesseract not found or disabled; only RapidOCR candidates were generated.")
    elif not succeeded:
        failure = next((f["tesseract_error"] for f in files if f.get("tesseract_error")), "no output")
        warnings.append(f"Tesseract at {tesseract} produced no output for language '{lang}': {failure}")
    if lang and not applied:
        warnings.append(
            f"Requested language '{lang}' was not applied by any engine: RapidOCR uses its bundled "
            f"Chinese/English model and ignores --lang. Install the '{lang}' Tesseract pack "
            "(check `tesseract --list-langs`) or pass --tesseract-bin/--tessdata."
        )
    return applied, warnings


def run_status(files: list[dict[str, Any]], lang: str, applied: list[str]) -> tuple[str, int]:
    """Errors outrank an unapplied language; both are always visible in ``warnings``."""
    failed = [f for f in files if f["status"] == "error"]
    if failed:
        return ("failed" if len(failed) == len(files) else "partial"), EXIT_PARTIAL
    if lang and not applied:
        return STATUS_LANGUAGE_UNAPPLIED, EXIT_LANGUAGE_UNAPPLIED
    return STATUS_COMPLETED, 0


def write_readme(out: Path, manifest: dict[str, Any]) -> None:
    # Human-facing index: candidates remain separate so no uncertain OCR is
    # silently presented as a canonical transcription.
    md = [
        "# OCR candidates",
        "",
        "> Candidates are raw engine outputs. Select and verify one per image against the source.",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Language requested: `{manifest['language_requested'] or '(none)'}`",
        f"- Language applied by: {', '.join(manifest['language_applied_by']) or 'no engine'}",
        "",
        *(f"> {warning}" for warning in manifest["warnings"]),
        "",
    ]
    for item in manifest["files"]:
        md += [f"## `{item['source']}`", "", f"- SHA-256: `{item['sha256']}`"]
        if item["status"] == "error":
            md += [f"- Status: error — {item['reason']}", ""]
            continue
        best = item["best_candidate"]
        md += [
            f"- Candidates: {item['candidate_count']}",
            f"- Heuristic candidate (not accuracy proof): `{best['engine']}/{best['variant']}` with {best['line_count']} lines",
            f"- Raw JSON: `candidates/{item['stem']}.json`",
            "",
        ]
    (out / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", type=Path, help="image files or directories")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE)
    parser.add_argument("--tesseract-bin", default=os.environ.get("TESSERACT_BIN"))
    parser.add_argument("--tessdata", default=os.environ.get("TESSDATA_PREFIX"))
    parser.add_argument("--no-tesseract", action="store_true", help="RapidOCR only, even if Tesseract is available (debugging)")
    parser.add_argument("--lang", default=DEFAULT_LANG, help="Tesseract language; RapidOCR ignores it")
    parser.add_argument("--psm", type=int, nargs="+", default=list(DEFAULT_PSM))
    parser.add_argument("--rotate", choices=ROTATION_CHOICES, default="auto", help="counter-clockwise degrees to apply before OCR; auto detects sideways photos")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    sources = parse_sources(parser, args.inputs)
    out = args.output_dir
    (out / "preprocessed").mkdir(parents=True, exist_ok=True)
    (out / "candidates").mkdir(parents=True, exist_ok=True)

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError as exc:
        parser.error(f"RapidOCR is required in the selected environment: {exc}")
    rapid = RapidOCR()
    tesseract = None if args.no_tesseract else (args.tesseract_bin or shutil.which("tesseract"))
    options = EngineOptions(lang=args.lang, psm=tuple(args.psm), tessdata=args.tessdata, scale=args.scale, rotate=args.rotate)

    files = []
    for source in sources:
        files.append(process_source(source, rapid, tesseract, options, out))
        print(source.path.name, files[-1]["status"], "candidates=", files[-1]["candidate_count"])

    applied, warnings = language_report(args.lang, tesseract, files)
    status, exit_code = run_status(files, args.lang, applied)
    manifest = {
        "status": status,
        "language_requested": args.lang,
        "language_applied_by": applied,
        "tesseract": tesseract,
        "warnings": warnings,
        "files": files,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out, manifest)
    print(f"{status}: {len(sources)} image(s); output={out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
