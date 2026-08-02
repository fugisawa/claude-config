#!/usr/bin/env python3
"""
Fill a PDF AcroForm with values from JSON.

Usage:
    python fill_form.py input.pdf data.json output.pdf [--validate] [--flatten] [--verbose]

Data file: a flat JSON object mapping field name to value.
    {"full_name": "Ada Lovelace", "subscribe": "/Yes", "country": "BR"}

--validate refuses to write anything unless every key in data.json exists in the form and
every checkbox/radio value is one of the states the field actually declares. Without it,
pypdf silently ignores unknown keys and you get a blank field you only notice on paper.

Exit codes:
    0 - Success
    1 - File not found
    2 - Invalid input
    3 - Processing error
    4 - Validation error
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (OK, VALIDATION_ERROR, get_logger, require_file,  # noqa: E402
                     require_import, run)

require_import('pypdf')
from pypdf import PdfReader, PdfWriter  # noqa: E402
from pypdf.generic import NameObject, NumberObject  # noqa: E402

logger = get_logger(__name__)

READ_ONLY_FLAG = 1


def declared_states(field: dict) -> list[str]:
    """Export values a button field accepts, read from its appearance dictionary."""
    appearances = field.get('/_States_')
    if appearances:
        return [str(state) for state in appearances]
    normal = (field.get('/AP') or {}).get('/N') or {}
    return [str(key) for key in normal]


def validate(fields: dict, data: dict) -> list[str]:
    """Return human-readable problems; empty list means the data fits the form."""
    problems = []
    for name, value in data.items():
        if name not in fields:
            problems.append(f"field not in form: {name!r}")
            continue
        field = fields[name]
        if field.get('/FT') == '/Btn':
            states = declared_states(field)
            if states and str(value) not in states:
                problems.append(
                    f"{name!r}: {value!r} is not one of the declared states {states}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description='Fill PDF form with JSON data')
    parser.add_argument('input', type=Path, help='Input PDF (must contain an AcroForm)')
    parser.add_argument('data', type=Path, help='JSON file with field values')
    parser.add_argument('output', type=Path, help='Output PDF')
    parser.add_argument('--validate', action='store_true',
                        help='Fail before writing if data does not fit the form')
    parser.add_argument('--flatten', action='store_true',
                        help='Mark fields read-only after filling (see flatten_form.py)')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.input)
        require_file(args.data)

        data = json.loads(args.data.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('data.json must be a JSON object of field -> value')

        reader = PdfReader(str(args.input))
        fields = reader.get_fields() or {}
        if not fields:
            raise ValueError(f'{args.input} has no form fields (not an AcroForm)')

        if args.validate:
            problems = validate(fields, data)
            if problems:
                for problem in problems:
                    logger.error(problem)
                return VALIDATION_ERROR

        writer = PdfWriter(clone_from=str(args.input))
        # Without NeedAppearances most viewers render filled text fields as blank: the
        # value is in the PDF, but no appearance stream was generated for it.
        writer.set_need_appearances_writer(True)
        for page in writer.pages:
            if '/Annots' in page:
                writer.update_page_form_field_values(page, data)

        if args.flatten:
            for page in writer.pages:
                for annot in page.get('/Annots') or []:
                    obj = annot.get_object()
                    flags = int(obj.get('/Ff', 0))
                    obj[NameObject('/Ff')] = NumberObject(flags | READ_ONLY_FLAG)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('wb') as handle:
            writer.write(handle)

        filled = [name for name in data if name in fields]
        logger.info(f"Filled {len(filled)}/{len(data)} fields -> {args.output}")
        if len(filled) != len(data) and not args.validate:
            logger.warning('Some keys were not form fields; rerun with --validate to list')
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
