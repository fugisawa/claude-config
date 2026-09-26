#!/usr/bin/env python3
"""Helpers shared by the photo OCR scripts: accepted formats, defaults, discovery, stems.

Kept in one place so the three CLIs cannot drift apart on which files they accept,
on how they name their artifacts, or on the defaults one forwards to the other.
"""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from pathlib import Path
from typing import NamedTuple

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"})
NO_INPUT_MESSAGE = "no supported image files found (accepted: " + ", ".join(sorted(IMAGE_EXTENSIONS)) + ")"
HASH_SUFFIX_LENGTH = 8

DEFAULT_LANG = "por"
DEFAULT_SCALE = 3
DEFAULT_PSM = (3, 4, 6)
DEFAULT_MIN_AREA_RATIO = 0.25


class Source(NamedTuple):
    """One input image with the two things every artifact is named or keyed by."""
    path: Path
    sha256: str
    stem: str

    @property
    def resolved(self) -> str:
        return str(self.path.resolve())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def unusable_inputs(inputs: list[Path]) -> list[Path]:
    """Explicit arguments that are neither a directory nor a supported image file."""
    return [item for item in inputs if not item.is_dir() and not is_image(item)]


def discover_images(inputs: list[Path]) -> list[Path]:
    """Files are taken as given; directories are scanned one level deep, sorted by name.

    The same file reached twice is kept once, keyed by its resolved path.
    """
    found: list[Path] = []
    for item in inputs:
        if item.is_dir():
            found.extend(p for p in sorted(item.iterdir()) if is_image(p))
        elif is_image(item):
            found.append(item)
    unique: dict[str, Path] = {}
    for path in found:
        unique.setdefault(str(path.resolve()), path)
    return list(unique.values())


def unique_stems(paths: list[Path], hashes: dict[Path, str]) -> dict[Path, str]:
    """Output stem per input; homonyms receive a hash suffix so artifacts never collide."""
    normalized = {path: path.stem.replace(" ", "_") for path in paths}
    counts = Counter(normalized.values())
    return {
        path: stem if counts[stem] == 1 else f"{stem}_{hashes[path][:HASH_SUFFIX_LENGTH]}"
        for path, stem in normalized.items()
    }


def discover_sources(inputs: list[Path]) -> list[Source]:
    paths = discover_images(inputs)
    hashes = {path: sha256(path) for path in paths}
    stems = unique_stems(paths, hashes)
    return [Source(path, hashes[path], stems[path]) for path in paths]


def parse_sources(parser: argparse.ArgumentParser, inputs: list[Path]) -> list[Source]:
    """Validate the CLI inputs at the boundary: a typo or an empty directory is a usage error."""
    unusable = unusable_inputs(inputs)
    if unusable:
        parser.error("input not found or not a supported image: " + ", ".join(str(p) for p in unusable))
    sources = discover_sources(inputs)
    if not sources:
        parser.error(NO_INPUT_MESSAGE)
    return sources
