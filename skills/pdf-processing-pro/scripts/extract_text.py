#!/usr/bin/env python3
"""
Extract text from a PDF.

Usage:
    python extract_text.py input.pdf [--output text.txt] [--preserve-formatting]
                           [--pages 1-5] [--page-markers]

--preserve-formatting keeps the visual layout: pdfplumber pads with spaces so columns stay
in their column. Use it for anything with a two-column layout or an aligned table; leave it
off for prose, where the padding turns into ragged whitespace.

What this does NOT recover is inline emphasis — bold, underline, strikethrough. Plain text
extraction has nowhere to put it. If the source is legal or exam material, where bold marks
what matters, extract emphasis separately (see the emphasis note in TABLES.md and the
`ab_extratores.py` diagnostic in the igepp-aula-reformat skill).

Exit codes:
    0 - Success
    1 - File not found
    2 - Invalid input
    3 - Processing error
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import OK, get_logger, require_file, require_import, run  # noqa: E402

require_import('pdfplumber')
import pdfplumber  # noqa: E402

logger = get_logger(__name__)


def parse_pages(spec: str | None, total: int) -> list[int]:
    if not spec:
        return list(range(total))
    wanted: list[int] = []
    for chunk in spec.split(','):
        chunk = chunk.strip()
        if '-' in chunk:
            first, last = (int(part) for part in chunk.split('-', 1))
            wanted += list(range(first, last + 1))
        else:
            wanted.append(int(chunk))
    return [n - 1 for n in wanted if 1 <= n <= total]


def main() -> int:
    parser = argparse.ArgumentParser(description='Extract text from PDF')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', '-o', type=Path, help='Default: stdout')
    parser.add_argument('--preserve-formatting', action='store_true',
                        help='Keep visual layout (space padding)')
    parser.add_argument('--pages', help='e.g. 1-5,8 (1-based); default: all')
    parser.add_argument('--page-markers', action='store_true',
                        help='Insert "--- page N ---" between pages')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.input)
        chunks: list[str] = []
        empty = 0
        with pdfplumber.open(str(args.input)) as pdf:
            indices = parse_pages(args.pages, len(pdf.pages))
            for index in indices:
                page = pdf.pages[index]
                text = page.extract_text(layout=args.preserve_formatting) or ''
                if not text.strip():
                    empty += 1
                if args.page_markers:
                    chunks.append(f"--- page {index + 1} ---")
                chunks.append(text)

        result = '\n'.join(chunks)
        if empty:
            logger.warning(
                f"{empty}/{len(indices)} page(s) yielded no text — the PDF may be scanned; "
                "see OCR.md")

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result, encoding='utf-8')
            logger.info(f"{len(result)} chars -> {args.output}")
        else:
            print(result)
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
