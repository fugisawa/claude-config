"""Shared primitives for the ~/.claude registry checkers.

Used by `doctor_agents.py` (agents/) and `doctor_skills.py` (skills/).

The frontmatter reader is deliberately **more tolerant than strict YAML**,
because the real Claude Code loader is: files opening with `--- ` (trailing
space) or carrying a stray `--- Unknown` line still register. A checker stricter
than the loader reports false positives, so those cases are recovered and
flagged as fragile rather than declared broken.
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

OPEN = re.compile(r"^---[ \t]*\r?\n")
CLOSE = re.compile(r"\r?\n---[ \t]*\r?\n")
SCALAR = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):[ \t]+(.*)$")
BLOCK = re.compile(r"[|>][-+]?\d*")  # YAML block scalar indicator


class Severity(enum.Enum):
    ERROR = "error"
    WARN = "warn"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class Report:
    root: Path
    item_count: int
    findings: list[Finding]

    @property
    def ok(self) -> bool:
        return not any(f.severity is Severity.ERROR for f in self.findings)


@dataclass(frozen=True)
class Frontmatter:
    meta: dict
    strict: bool  # False when only the lenient recovery below could read it


def _salvage(raw: str) -> dict:
    """Recover top-level keys line by line when strict YAML gives up.

    Handles block scalars (`description: |`, `>`, `|-`, `>-`), whose value lives
    on the following indented lines. Reading only the marker would yield a 1-char
    description and misreport a perfectly good skill as unroutable.
    """
    out: dict[str, str] = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        hit = SCALAR.match(lines[i])
        i += 1
        if not hit:
            continue
        key, value = hit.group(1), hit.group(2).strip()
        if BLOCK.fullmatch(value):
            block: list[str] = []
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in " \t"):
                block.append(lines[i].strip())
                i += 1
            value = " ".join(p for p in block if p)
        out.setdefault(key, value.strip("\"'"))
    return out


def read_frontmatter(text: str) -> Frontmatter | None:
    """Parse a leading frontmatter block. None when there is no block at all."""
    opened = OPEN.match(text)
    if opened is None:
        return None
    rest = text[opened.end():]
    closed = CLOSE.search(rest)
    if closed is None:
        return None
    raw = rest[:closed.start()]
    try:
        meta = yaml.safe_load(raw)
        if isinstance(meta, dict):
            return Frontmatter(meta, strict=True)
    except yaml.YAMLError:
        pass
    return Frontmatter(_salvage(raw), strict=False)


def duplicate_findings(by_name: dict[str, list[str]], kind: str) -> list[Finding]:
    """One ERROR per name claimed by more than one file."""
    return [
        Finding(
            Severity.ERROR, "duplicate-name", paths[0],
            f"`name: {name}` is declared by {len(paths)} {kind} files "
            f"({', '.join(paths)}) — the loader keeps one by filesystem read "
            f"order, so which definition is live is undefined",
        )
        for name, paths in sorted(by_name.items()) if len(paths) > 1
    ]


def render(report: Report, label: str) -> str:
    errors = [f for f in report.findings if f.severity is Severity.ERROR]
    warns = [f for f in report.findings if f.severity is Severity.WARN]
    lines = [f"{label}: {report.root}",
             f"  unique names : {report.item_count}",
             f"  errors       : {len(errors)}",
             f"  warnings     : {len(warns)}"]
    for title, group in (("ERRORS", errors), ("WARNINGS", warns)):
        if not group:
            continue
        lines.append(f"\n{title}")
        for f in group:
            lines.append(f"  [{f.code}] {f.path}\n      {f.detail}")
    lines.append("\nOK — registry is unambiguous." if report.ok
                 else "\nFAIL — resolve the errors above.")
    return "\n".join(lines)
