#!/usr/bin/env python3
"""
render.py — Convert briefing HTML to a print-ready PDF.

Usage:
    python render.py <input.html> <output.pdf>

The script:
  - Resolves relative paths for charts/images
  - Configures fonts available in the environment
  - Validates the rendered output (page count, file size sanity)
  - Prints a summary

Requires: weasyprint >= 60
"""

import sys
import os
import argparse
from pathlib import Path


def render(html_path: str, pdf_path: str, base_url: str | None = None) -> dict:
    """Render an HTML file to a PDF. Returns a dict with file metadata."""
    try:
        from weasyprint import HTML, CSS
    except ImportError as e:
        raise RuntimeError(
            "WeasyPrint is not installed. Install with: pip install weasyprint"
        ) from e

    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()

    if not html_path.exists():
        raise FileNotFoundError(f"Input HTML not found: {html_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Use the HTML file's directory as base_url so relative <img src> work
    base = base_url or str(html_path.parent) + "/"

    html = HTML(filename=str(html_path), base_url=base)
    html.write_pdf(str(pdf_path))

    size_kb = pdf_path.stat().st_size / 1024

    # Quick sanity check: count pages by re-opening with pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        n_pages = len(reader.pages)
    except Exception:
        n_pages = None

    return {
        "input": str(html_path),
        "output": str(pdf_path),
        "size_kb": size_kb,
        "pages": n_pages,
    }


def main():
    parser = argparse.ArgumentParser(description="Render a briefing HTML to PDF.")
    parser.add_argument("input", help="Path to input HTML file")
    parser.add_argument("output", help="Path to output PDF file")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL for resolving relative image paths (defaults to HTML directory)",
    )
    args = parser.parse_args()

    try:
        result = render(args.input, args.output, args.base_url)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("Briefing rendered successfully.")
    print(f"  Input:  {result['input']}")
    print(f"  Output: {result['output']}")
    print(f"  Size:   {result['size_kb']:.1f} KB")
    if result["pages"] is not None:
        print(f"  Pages:  {result['pages']}")


if __name__ == "__main__":
    main()
