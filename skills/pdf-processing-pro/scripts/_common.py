#!/usr/bin/env python3
"""
Shared helpers for the pdf-processing-pro scripts.

Every script in this directory is runnable on its own; this module only holds what would
otherwise be copy-pasted eight times — the exit-code contract and the logger setup. It has
no third-party imports, so importing it can never be the thing that breaks a script.

Exit codes (the contract documented in SKILL.md — keep these stable):
    0 - Success
    1 - File not found
    2 - Invalid input
    3 - Processing error
    4 - Validation error
"""

import logging
import sys
from pathlib import Path
from typing import Callable

OK = 0
NOT_FOUND = 1
INVALID_INPUT = 2
PROCESSING_ERROR = 3
VALIDATION_ERROR = 4


def get_logger(name: str) -> logging.Logger:
    """Logger with the same format the original analyze_form.py established."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)


def require_file(path: Path) -> None:
    """Raise FileNotFoundError unless `path` is an existing file."""
    if not path.is_file():
        raise FileNotFoundError(path)


def require_import(module: str, package: str | None = None) -> None:
    """Exit 3 with an actionable message when an optional dependency is missing.

    Called at import time by each script. Exiting here rather than raising keeps the
    traceback out of the user's face for the single most common failure — a missing wheel.
    """
    import importlib
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"Error: {module} not installed. Run: pip install {package or module}",
              file=sys.stderr)
        sys.exit(PROCESSING_ERROR)


def run(main_body: Callable[[], int], logger: logging.Logger, verbose: bool = False) -> int:
    """Map exceptions onto the documented exit codes, uniformly across the scripts."""
    try:
        return main_body()
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return NOT_FOUND
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return INVALID_INPUT
    except Exception as e:                                   # noqa: BLE001 — CLI boundary
        logger.error(f"Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return PROCESSING_ERROR
