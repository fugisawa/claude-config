#!/usr/bin/env python3
"""
Merge several PDFs into one.

Usage:
    python merge_pdfs.py file1.pdf file2.pdf file3.pdf --output merged.pdf
    python merge_pdfs.py 'chapters/*.pdf' --output book.pdf --sort
    python merge_pdfs.py a.pdf b.pdf --output out.pdf --bookmarks

Inputs are merged in the order given — that is the contract, so a shell glob that expands
to `10.pdf 1.pdf 2.pdf` merges in that wrong order silently. Pass --sort to sort naturally
(so `2.pdf` precedes `10.pdf`), or quote the glob and let this script expand it.

--bookmarks adds one outline entry per source file, named after the file. Useful when the
merged result is meant to be navigated rather than printed.

Exit codes:
    0 - Success
    1 - File not found
    2 - Invalid input
    3 - Processing error
"""

import argparse
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import OK, get_logger, require_import, run  # noqa: E402

require_import('pypdf')
from pypdf import PdfWriter  # noqa: E402

logger = get_logger(__name__)


def natural_key(path: Path) -> list:
    """Sort key where 2 comes before 10 — the order humans mean when they name files."""
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', path.name)]


def resolve(patterns: list[str], sort: bool) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = [Path(match) for match in glob.glob(pattern)]
        if matches:
            paths += sorted(matches, key=natural_key) if sort else sorted(matches)
        else:
            paths.append(Path(pattern))          # literal name; existence checked below
    if sort:
        paths.sort(key=natural_key)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description='Merge PDFs')
    parser.add_argument('inputs', nargs='+', help='PDF files, or a quoted glob')
    parser.add_argument('--output', '-o', type=Path, required=True)
    parser.add_argument('--sort', action='store_true', help='Natural sort (2 before 10)')
    parser.add_argument('--bookmarks', action='store_true',
                        help='One outline entry per source file')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        paths = resolve(args.inputs, args.sort)
        missing = [path for path in paths if not path.is_file()]
        if missing:
            raise FileNotFoundError(', '.join(str(path) for path in missing))
        if len(paths) < 2:
            raise ValueError('merging needs at least two PDFs')

        writer = PdfWriter()
        total = 0
        for path in paths:
            before = len(writer.pages)
            writer.append(str(path))
            total += len(writer.pages) - before
            if args.bookmarks:
                writer.add_outline_item(path.stem, before)
            logger.info(f"+ {path.name} ({len(writer.pages) - before} pages)")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('wb') as handle:
            writer.write(handle)
        logger.info(f"{len(paths)} files, {total} pages -> {args.output}")
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
