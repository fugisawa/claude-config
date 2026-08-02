#!/usr/bin/env python3
"""
Extract tables from a PDF to CSV, Excel or JSON.

Usage:
    python extract_tables.py input.pdf [--output tables.csv] [--format csv|excel|json]
                             [--pages 1-5] [--strategy lines|text] [--min-rows 2]

Detection strategy is the whole game, so it is a flag rather than a guess:
  lines (default) — reads the ruling lines actually drawn on the page. Precise when the
                    table has borders; blind when it does not.
  text            — infers columns from whitespace alignment. Finds borderless tables and
                    hallucinates structure in ordinary prose. Always check --min-rows.

Multiple tables land in one CSV separated by a blank line and a `# table N (page P)`
comment; Excel gets one sheet per table; JSON keeps them as a list of objects with their
page number. When nothing is found the script says so and exits 0 — an empty result is an
answer, not an error.

Exit codes:
    0 - Success
    1 - File not found
    2 - Invalid input
    3 - Processing error
"""

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import OK, get_logger, require_file, require_import, run  # noqa: E402

require_import('pdfplumber')
import pdfplumber  # noqa: E402

logger = get_logger(__name__)


def parse_pages(spec: str | None, total: int) -> list[int]:
    """'1-5,8' -> zero-based indices, clamped to the document."""
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


def clean(row: list) -> list[str]:
    """Cells arrive with embedded newlines from wrapped text; flatten them."""
    return [(cell or '').replace('\n', ' ').strip() for cell in row]


def write_csv(tables: list[dict], out: Path) -> None:
    with out.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        for index, table in enumerate(tables, start=1):
            if index > 1:
                handle.write('\n')
            handle.write(f"# table {index} (page {table['page']})\n")
            writer.writerows(table['rows'])


def write_excel(tables: list[dict], out: Path) -> None:
    require_import('openpyxl')
    from openpyxl import Workbook
    book = Workbook()
    default = book.active
    if default is not None:          # openpyxl always creates one; be explicit anyway
        book.remove(default)
    for index, table in enumerate(tables, start=1):
        sheet = book.create_sheet(f"t{index}_p{table['page']}"[:31])
        for row in table['rows']:
            sheet.append(row)
    book.save(out)


def main() -> int:
    parser = argparse.ArgumentParser(description='Extract tables from PDF')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', '-o', type=Path, help='Default: stdout (csv/json)')
    parser.add_argument('--format', '-f', choices=['csv', 'excel', 'json'], default='csv')
    parser.add_argument('--pages', help='e.g. 1-5,8 (1-based); default: all')
    parser.add_argument('--strategy', choices=['lines', 'text'], default='lines')
    parser.add_argument('--min-rows', type=int, default=2,
                        help='Discard candidates with fewer rows (default 2)')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.input)
        if args.format == 'excel' and not args.output:
            raise ValueError('--format excel needs --output')

        settings = {'vertical_strategy': args.strategy,
                    'horizontal_strategy': args.strategy}
        tables: list[dict] = []
        with pdfplumber.open(str(args.input)) as pdf:
            for index in parse_pages(args.pages, len(pdf.pages)):
                page = pdf.pages[index]
                for found in page.extract_tables(table_settings=settings):
                    rows = [clean(row) for row in found]
                    if len(rows) >= args.min_rows:
                        tables.append({'page': index + 1, 'rows': rows})

        if not tables:
            logger.info(f"No tables found with strategy={args.strategy}. "
                        f"Try --strategy {'text' if args.strategy == 'lines' else 'lines'}")
            return OK

        logger.info(f"Found {len(tables)} table(s)")
        if args.format == 'excel':
            write_excel(tables, args.output)
        elif args.format == 'json':
            payload = json.dumps(tables, ensure_ascii=False, indent=2)
            args.output.write_text(payload, encoding='utf-8') if args.output else print(payload)
        elif args.output:
            write_csv(tables, args.output)
        else:
            writer = csv.writer(sys.stdout)
            for index, table in enumerate(tables, start=1):
                print(f"# table {index} (page {table['page']})")
                writer.writerows(table['rows'])
                print()

        if args.output:
            logger.info(f"Saved to {args.output}")
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
