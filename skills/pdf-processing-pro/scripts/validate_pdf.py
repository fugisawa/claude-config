#!/usr/bin/env python3
"""
Check a PDF's integrity and report what a downstream tool will run into.

Usage:
    python validate_pdf.py input.pdf [--json] [--strict]

Reports: page count, encryption, damaged structure, pages with no text layer (i.e. scans
that need OCR), embedded vs missing fonts, form fields and attachments. Text-layer coverage
is the number worth reading first — a "valid" PDF that is 100% images will silently produce
an empty extraction, and that is the failure people lose an hour to.

By default the exit code reflects only fatal problems (unreadable, encrypted without a
password). --strict also fails on warnings, which is what you want inside a pipeline.

Exit codes:
    0 - Valid (or only warnings, without --strict)
    1 - File not found
    3 - Processing error
    4 - Validation error (fatal problem, or any warning under --strict)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (OK, VALIDATION_ERROR, get_logger, require_file,  # noqa: E402
                     require_import, run)

require_import('pypdf')
from pypdf import PdfReader  # noqa: E402
from pypdf.errors import PdfReadError  # noqa: E402

logger = get_logger(__name__)


def font_report(reader: PdfReader) -> tuple[int, int]:
    """(embedded, total) font count — non-embedded fonts render differently elsewhere."""
    embedded = total = 0
    seen: set = set()
    for page in reader.pages:
        fonts = ((page.get('/Resources') or {}).get('/Font') or {})
        for ref in fonts.values():
            font = ref.get_object()
            key = font.get('/BaseFont', id(font))
            if key in seen:            # the same font is referenced on every page
                continue
            seen.add(key)
            total += 1
            # A Type0 (composite) font — what any modern renderer emits for subset fonts —
            # keeps the descriptor one level down, in its descendant. Reading only the top
            # level reports every well-made PDF as "not embedded", which is worse than
            # useless: it trains you to ignore the warning.
            descriptors = []
            if font.get('/Subtype') == '/Type0':
                for child in font.get('/DescendantFonts') or []:
                    child_obj = child.get_object()
                    if '/FontDescriptor' in child_obj:
                        descriptors.append(child_obj['/FontDescriptor'].get_object())
            elif '/FontDescriptor' in font:
                descriptors.append(font['/FontDescriptor'].get_object())
            if any(key in d for d in descriptors
                   for key in ('/FontFile', '/FontFile2', '/FontFile3')):
                embedded += 1
    return embedded, total


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate PDF integrity')
    parser.add_argument('input', type=Path)
    parser.add_argument('--json', action='store_true', help='Machine-readable output')
    parser.add_argument('--strict', action='store_true', help='Warnings become failures')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.input)
        report: dict = {'file': str(args.input),
                        'size_bytes': args.input.stat().st_size}
        fatal: list[str] = []
        warnings: list[str] = []

        try:
            reader = PdfReader(str(args.input))
        except PdfReadError as e:
            report.update(readable=False, fatal=[f'cannot parse: {e}'])
            print(json.dumps(report, indent=2) if args.json else f"FATAL: cannot parse: {e}")
            return VALIDATION_ERROR

        report['readable'] = True
        report['encrypted'] = reader.is_encrypted
        if reader.is_encrypted:
            try:
                reader.decrypt('')                       # empty owner password is common
                warnings.append('encrypted, opened with an empty password')
            except Exception:                            # noqa: BLE001
                fatal.append('encrypted and needs a password')

        if not fatal:
            report['pages'] = len(reader.pages)
            without_text = [index + 1 for index, page in enumerate(reader.pages)
                            if not (page.extract_text() or '').strip()]
            report['pages_without_text'] = without_text
            report['text_coverage'] = (
                round(1 - len(without_text) / max(len(reader.pages), 1), 3))
            if without_text:
                warnings.append(
                    f"{len(without_text)} page(s) with no text layer — likely scanned; "
                    "see OCR.md")

            embedded, total = font_report(reader)
            report['fonts'] = {'embedded': embedded, 'total': total}
            if total and embedded < total:
                warnings.append(f"{total - embedded}/{total} font(s) not embedded")

            fields = reader.get_fields() or {}
            report['form_fields'] = len(fields)
            report['metadata'] = {key.lstrip('/'): str(value) for key, value
                                  in (reader.metadata or {}).items()}

        report['fatal'] = fatal
        report['warnings'] = warnings

        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(f"{args.input.name}: {report.get('pages', '?')} pages, "
                  f"text coverage {report.get('text_coverage', 0):.0%}")
            for problem in fatal:
                print(f"  FATAL: {problem}")
            for warning in warnings:
                print(f"  warn:  {warning}")
            if not fatal and not warnings:
                print("  no problems found")

        if fatal or (warnings and args.strict):
            return VALIDATION_ERROR
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
