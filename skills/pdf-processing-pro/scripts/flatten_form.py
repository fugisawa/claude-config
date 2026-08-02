#!/usr/bin/env python3
"""
Make a filled form non-editable.

Usage:
    python flatten_form.py filled.pdf final.pdf [--strip] [--verbose]

Read this before you rely on it. There are two different things called "flattening":

  read-only (default here)  — every field keeps its value and its appearance, but gains the
                              ReadOnly flag, so viewers refuse to edit it. Pure pypdf, no
                              extra dependency, fully reversible by anyone who clears the
                              flag. Right for "stop accidental edits before I email this".

  true flatten (--strip)    — the field objects are removed and only the drawn appearance
                              survives, so there is no form left to edit. This script does
                              it by dropping the widget annotations and the AcroForm entry
                              after the appearance streams exist. It is NOT reversible.

Neither is a security control. If the value must be unforgeable, the answer is a signature,
not a flag. And --strip depends on the appearance streams already being generated: if the
file was filled without NeedAppearances (see fill_form.py), stripping can leave the page
visually blank. The script checks for that and refuses rather than handing you an empty PDF.

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
from pypdf.generic import ArrayObject, NameObject, NumberObject  # noqa: E402

logger = get_logger(__name__)

READ_ONLY_FLAG = 1


def widgets(page) -> list:
    """Form widget annotations on a page (the objects that carry field appearance)."""
    found = []
    for annot in page.get('/Annots') or []:
        obj = annot.get_object()
        if obj.get('/Subtype') == '/Widget':
            found.append(obj)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description='Flatten a filled PDF form')
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--strip', action='store_true',
                        help='Remove the fields entirely (irreversible)')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    def body() -> int:
        require_file(args.input)
        reader = PdfReader(str(args.input))
        if not (reader.get_fields() or {}):
            raise ValueError(f'{args.input} has no form fields — nothing to flatten')

        writer = PdfWriter(clone_from=str(args.input))
        touched = 0

        if args.strip:
            missing_appearance = [obj for page in writer.pages for obj in widgets(page)
                                  if not (obj.get('/AP') or {}).get('/N')]
            if missing_appearance:
                raise ValueError(
                    f'{len(missing_appearance)} field(s) have no appearance stream; '
                    'stripping now would blank them. Refill with fill_form.py (which sets '
                    'NeedAppearances), open and save once in a viewer, then retry')
            for page in writer.pages:
                keep = [annot for annot in (page.get('/Annots') or [])
                        if annot.get_object().get('/Subtype') != '/Widget']
                touched += len(page.get('/Annots') or []) - len(keep)
                if keep:
                    page[NameObject('/Annots')] = ArrayObject(keep)
                elif '/Annots' in page:
                    del page[NameObject('/Annots')]
            root = writer._root_object                                     # noqa: SLF001
            if '/AcroForm' in root:
                del root[NameObject('/AcroForm')]
            logger.info(f'Stripped {touched} field widget(s) — form removed')
        else:
            for page in writer.pages:
                for obj in widgets(page):
                    obj[NameObject('/Ff')] = NumberObject(
                        int(obj.get('/Ff', 0)) | READ_ONLY_FLAG)
                    touched += 1
            logger.info(f'Marked {touched} field(s) read-only (reversible)')

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('wb') as handle:
            writer.write(handle)
        logger.info(f'-> {args.output}')
        return OK

    return run(body, logger, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
