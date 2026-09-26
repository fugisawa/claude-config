#!/usr/bin/env python3
"""Coordinate conservative photo rectification and local OCR.

This coordinator preserves originals, runs rectification once for the whole
batch, OCRs the credible rectified image (or the original when rectification
abstains or fails), and writes one auditable batch manifest. Rectified images
are kept under ``rectified/`` because they are evidence the manifest points
at. A successful process means the helpers ran; it does not certify
transcription accuracy.

Usage:
  python batch_ocr.py INPUT [INPUT ...] --output-dir OUTPUT
  python batch_ocr.py DIRECTORY --output-dir OUTPUT

Exit codes: 0 every image completed and the requested language was applied;
2 usage error, or partial run — an image errored, or no engine applied the
requested language (see ``language_applied_by`` and ``warnings``).
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "opencv-python-headless>=4.8",
#   "numpy>=1.24",
#   "pillow>=10.1",
#   "rapidocr-onnxruntime>=1.3,<2",
# ]
# ///
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ocr_common import DEFAULT_LANG, DEFAULT_MIN_AREA_RATIO, DEFAULT_PSM, DEFAULT_SCALE, Source, parse_sources

EXIT_PARTIAL = 2
OCR_STATUS_BY_EXIT = {0: "completed", 3: "completed_language_unapplied"}
RECTIFIED_DIR = "rectified"
STDERR_TAIL = 2000


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def rectify_all(script: Path, sources: list[Source], rectified: Path, min_area_ratio: float) -> list[dict[str, Any]]:
    """One rectification run for the batch; every source gets a record, even on failure."""
    proc = run([sys.executable, str(script), *[str(s.path) for s in sources], "--output-dir", str(rectified), "--min-area-ratio", str(min_area_ratio)])
    manifest = read_json(rectified / "rectification_manifest.json", {})
    by_path = {r.get("source_path"): r for r in manifest.get("files", [])} if isinstance(manifest, dict) else {}
    records = []
    for source in sources:
        base = {"source": source.path.name, "source_path": source.resolved, "source_sha256": source.sha256}
        record = by_path.get(source.resolved)
        if proc.returncode != 0:
            records.append({**base, "status": "error", "reason": "rectification_process_failed", "stderr": proc.stderr[-STDERR_TAIL:]})
        elif record is None:
            records.append({**base, "status": "error", "reason": "missing_rectification_record", "stderr": proc.stderr[-STDERR_TAIL:]})
        else:
            records.append({**record, **base})
    return records


def select_input(record: dict[str, Any], rectified: Path) -> tuple[Path, str]:
    """Rectified image when credible; otherwise the original, with the route named."""
    if record.get("status") == "rectified" and record.get("output"):
        return rectified / str(record["output"]), "rectified"
    if record.get("status") == "error":
        return Path(record["source_path"]), "original_after_rectification_error"
    return Path(record["source_path"]), "original_after_abstention"


def ocr_command(script: Path, selected: Path, ocr_dir: Path, args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(script), str(selected), "--output-dir", str(ocr_dir), "--lang", args.lang, "--scale", str(args.scale), "--rotate", args.rotate, "--psm", *[str(x) for x in args.psm]]
    if args.no_tesseract:
        command.append("--no-tesseract")
    if args.tesseract_bin:
        command += ["--tesseract-bin", args.tesseract_bin]
    if args.tessdata:
        command += ["--tessdata", args.tessdata]
    return command


def ocr_one(script: Path, record: dict[str, Any], rectified: Path, ocr_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    selected, route = select_input(record, rectified)
    proc = run(ocr_command(script, selected, ocr_dir, args))
    helper = read_json(ocr_dir / "manifest.json", {})
    helper = helper if isinstance(helper, dict) else {}
    files = helper.get("files", [])
    status = OCR_STATUS_BY_EXIT.get(proc.returncode, "error") if files else "error"
    return {
        "source": record["source"],
        "source_path": record["source_path"],
        "source_sha256": record["source_sha256"],
        "selected_input": str(selected.resolve()),
        "route": route,
        "status": status,
        "output_dir": str(ocr_dir),
        "candidate_count": sum(int(x.get("candidate_count", 0)) for x in files),
        "language_applied_by": list(helper.get("language_applied_by", [])),
        "helper_manifest": str((ocr_dir / "manifest.json").resolve()),
        "helper_warnings": list(helper.get("warnings", [])),
        "stderr": proc.stderr[-STDERR_TAIL:] if status == "error" else "",
    }


def batch_warnings(lang: str, applied: list[str]) -> list[str]:
    warnings = ["OCR output requires visual verification; helper success is not transcription proof."]
    if lang and not applied:
        warnings.append(
            f"Requested language '{lang}' was not applied by any engine; the candidates come from "
            "RapidOCR's bundled Chinese/English model. Expect lost or invented diacritics."
        )
    return warnings


def build_manifest(args: argparse.Namespace, scripts: dict[str, Path], sources: list[Source], rectification: list[dict[str, Any]], ocr: list[dict[str, Any]]) -> dict[str, Any]:
    applied = sorted({engine for record in ocr for engine in record["language_applied_by"]})
    status = "completed" if all(record["status"] == "completed" for record in ocr) else "partial"
    return {
        "schema_version": 2,
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "status": status,
        "language_requested": args.lang,
        "language_applied_by": applied,
        "tool": "batch_ocr.py",
        "scripts": {name: str(path) for name, path in scripts.items()},
        "options": {"scale": args.scale, "min_area_ratio": args.min_area_ratio, "psm": args.psm, "rotate": args.rotate, "no_tesseract": args.no_tesseract},
        "input_count": len(sources),
        "rectification": rectification,
        "ocr": ocr,
        "abstentions": [x for x in rectification if x.get("status") == "abstain"],
        "warnings": batch_warnings(args.lang, applied),
    }


def write_summary(output: Path, manifest: dict[str, Any]) -> None:
    rectification, ocr = manifest["rectification"], manifest["ocr"]
    summary = [
        "# OCR batch run",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Inputs: {manifest['input_count']}",
        f"- Rectified: {sum(x.get('status') == 'rectified' for x in rectification)}",
        f"- Abstained: {sum(x.get('status') == 'abstain' for x in rectification)}",
        f"- OCR completed: {sum(x['status'] == 'completed' for x in ocr)}",
        f"- Language requested: `{manifest['language_requested'] or '(none)'}`",
        f"- Language applied by: {', '.join(manifest['language_applied_by']) or 'no engine'}",
        "",
        *(f"> {warning}" for warning in manifest["warnings"]),
        "",
        "See `batch_manifest.json` for hashes, routes, candidates, and errors.",
    ]
    (output / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", type=Path, help="image files or directories")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--lang", default=DEFAULT_LANG, help="OCR language passed to ocr_photos.py (Tesseract only)")
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE)
    parser.add_argument("--min-area-ratio", type=float, default=DEFAULT_MIN_AREA_RATIO)
    parser.add_argument("--tesseract-bin", default=os.environ.get("TESSERACT_BIN"))
    parser.add_argument("--tessdata", default=os.environ.get("TESSDATA_PREFIX"))
    parser.add_argument("--no-tesseract", action="store_true", help="RapidOCR only, even if Tesseract is available (debugging)")
    parser.add_argument("--psm", type=int, nargs="+", default=list(DEFAULT_PSM))
    parser.add_argument("--rotate", choices=("auto", "0", "90", "180", "270"), default="auto", help="passed to ocr_photos.py; auto detects sideways photos")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    sources = parse_sources(parser, args.inputs)
    script_dir = Path(__file__).resolve().parent
    scripts = {"rectify": script_dir / "rectify_photos.py", "ocr": script_dir / "ocr_photos.py"}
    if not all(path.exists() for path in scripts.values()):
        parser.error("bundled rectify_photos.py and ocr_photos.py are required")

    output = args.output_dir.resolve()
    rectified = output / RECTIFIED_DIR
    rectified.mkdir(parents=True, exist_ok=True)
    rectification = rectify_all(scripts["rectify"], sources, rectified, args.min_area_ratio)
    ocr_records = []
    for source, record in zip(sources, rectification):
        ocr_records.append(ocr_one(scripts["ocr"], record, rectified, output / "ocr" / source.stem, args))
        print(f"[{len(ocr_records)}/{len(sources)}] {source.path.name}: {ocr_records[-1]['route']}, status={ocr_records[-1]['status']}")

    manifest = build_manifest(args, scripts, sources, rectification, ocr_records)
    (output / "batch_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(output, manifest)
    print(f"batch status={manifest['status']}; manifest={output / 'batch_manifest.json'}")
    return 0 if manifest["status"] == "completed" else EXIT_PARTIAL


if __name__ == "__main__":
    raise SystemExit(main())
