#!/usr/bin/env python3
"""
Split a PDF into individual pages or ranges.

Usage:
    python split_pdf.py input.pdf --output-dir pages/
    python split_pdf.py input.pdf --output-dir out/ --ranges 1-10,11-20,21-
    python split_pdf.py input.pdf --output-dir out/ --every 25 --prefix chapter

Page numbers are 1-based and inclusive, matching what a reader sees. An open range
(`21-`) runs to the last page. Output names are zero-padded to the width of the document,
so `page_007.pdf` sorts correctly next to `page_142.pdf` in any file manager.

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

require_import('pypdf')
from pypdf import PdfReader, PdfWriter  # noqa: E402

logger = get_logger(__name__)


def parse_ranges(spec: str, total: int) -> list[tuple[int, int]]:
    """'1-10,11-20,21-' -> [(0,9),(10,19),(20,total-1)] as zero-based inclusive pairs."""
    ranges: list[tuple[int, int]] = []
    for chunk in spec.split(','):
        chunk = chunk.strip()
        if '-' in chunk:
            head, tail = chunk.split('-', 1)
            first = int(head)
            last = int(tail) if tail.strip() else total
        else:
            first = last = int(chunk)
        if not (1 <= first <= last <= total):
            raise ValueError(f"range {chunk!r} is outside 1-{total}")
        ranges.append((first - 1, last - 1))
    return ranges


def main() -> int:
    parser = argparse.ArgumentParser(description='Split PDF into pages or ranges')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', '-d', type=Path, required=True)
    parser.add_argument('--ranges', help='e.g. 1-10,11-20,21- (1-based, inclusive)')
    parser.add_argument('--every', type=int, help='Fixed-size chunks of N pages')
    parser.add_argument('--prefix', default='page', help='Filename prefix (default: page)')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.input)
        if args.ranges and args.every:
            raise ValueError('use --ranges or --every, not both')

        reader = PdfReader(str(args.input))
        total = len(reader.pages)
        if total == 0:
            raise ValueError('the PDF has no pages')

        if args.ranges:
            chunks = parse_ranges(args.ranges, total)
        elif args.every:
            if args.every < 1:
                raise ValueError('--every must be at least 1')
            chunks = [(start, min(start + args.every - 1, total - 1))
                      for start in range(0, total, args.every)]
        else:
            chunks = [(index, index) for index in range(total)]

        args.output_dir.mkdir(parents=True, exist_ok=True)
        width = len(str(total))
        for first, last in chunks:
            writer = PdfWriter()
            for index in range(first, last + 1):
                writer.add_page(reader.pages[index])
            name = (f"{args.prefix}_{first + 1:0{width}d}.pdf" if first == last
                    else f"{args.prefix}_{first + 1:0{width}d}-{last + 1:0{width}d}.pdf")
            with (args.output_dir / name).open('wb') as handle:
                writer.write(handle)
            logger.info(f"{name} ({last - first + 1} pages)")

        logger.info(f"{total} pages -> {len(chunks)} file(s) in {args.output_dir}")
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
