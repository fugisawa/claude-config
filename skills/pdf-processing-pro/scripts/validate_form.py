#!/usr/bin/env python3
"""
Validate form data against a schema, before it ever touches a PDF.

Usage:
    python validate_form.py data.json schema.json [--verbose]

Schema format (deliberately small — this is a pre-flight check, not JSON Schema):
    {
      "full_name": {"required": true, "type": "string", "max_length": 60},
      "age":       {"type": "integer", "min": 0, "max": 130},
      "country":   {"type": "string", "enum": ["BR", "PT", "AO"]},
      "email":     {"type": "string", "pattern": "^[^@]+@[^@]+\\\\.[a-z]{2,}$"}
    }

Keys present in data but absent from the schema are reported as warnings, not errors: a
form usually has more fields than you chose to constrain.

Exit codes:
    0 - Success (data is valid)
    1 - File not found
    2 - Invalid input (malformed JSON or schema)
    4 - Validation error (data does not satisfy the schema)
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (OK, VALIDATION_ERROR, get_logger, require_file, run)  # noqa: E402

logger = get_logger(__name__)

TYPES: dict[str, type | tuple[type, ...]] = {
    'string': str,
    'integer': int,
    'number': (int, float),
    'boolean': bool,
}


def check(name: str, value: object, rule: dict) -> list[str]:
    """All problems with one field — never stops at the first, so one run lists them all."""
    problems: list[str] = []
    expected = rule.get('type')
    if expected:
        if expected not in TYPES:
            raise ValueError(f"schema for {name!r}: unknown type {expected!r}")
        # bool is a subclass of int in Python; an integer field must not accept True.
        if expected in ('integer', 'number') and isinstance(value, bool):
            problems.append(f"{name}: expected {expected}, got boolean")
        elif not isinstance(value, TYPES[expected]):
            problems.append(f"{name}: expected {expected}, got {type(value).__name__}")

    if 'enum' in rule and value not in rule['enum']:
        problems.append(f"{name}: {value!r} not in {rule['enum']}")

    text = value if isinstance(value, str) else None
    if text is not None:
        if 'max_length' in rule and len(text) > rule['max_length']:
            problems.append(f"{name}: {len(text)} chars, max is {rule['max_length']}")
        if 'min_length' in rule and len(text) < rule['min_length']:
            problems.append(f"{name}: {len(text)} chars, min is {rule['min_length']}")
        if 'pattern' in rule and not re.search(rule['pattern'], text):
            problems.append(f"{name}: does not match /{rule['pattern']}/")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 'min' in rule and value < rule['min']:
            problems.append(f"{name}: {value} is below min {rule['min']}")
        if 'max' in rule and value > rule['max']:
            problems.append(f"{name}: {value} is above max {rule['max']}")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate form data against a schema')
    parser.add_argument('data', type=Path, help='JSON file with field values')
    parser.add_argument('schema', type=Path, help='JSON file with the rules')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.data)
        require_file(args.schema)
        data = json.loads(args.data.read_text(encoding='utf-8'))
        schema = json.loads(args.schema.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(schema, dict):
            raise ValueError('both data and schema must be JSON objects')

        problems: list[str] = []
        for name, rule in schema.items():
            if not isinstance(rule, dict):
                raise ValueError(f"schema for {name!r} must be an object")
            if name not in data:
                if rule.get('required'):
                    problems.append(f"{name}: required field is missing")
                continue
            problems += check(name, data[name], rule)

        for name in data:
            if name not in schema:
                logger.warning(f"{name}: present in data, not constrained by the schema")

        if problems:
            for problem in problems:
                logger.error(problem)
            logger.error(f"{len(problems)} problem(s); data was NOT accepted")
            return VALIDATION_ERROR

        logger.info(f"Valid: {len(schema)} rule(s) satisfied")
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
