#!/usr/bin/env python3
"""Health check for the Claude Code agent registry (~/.claude/agents/).

Claude Code scans `.claude/agents/` **recursively**; an agent's identity comes
only from its `name:` frontmatter, not from its path or filename. When two files
declare the same name, the loader keeps one "chosen by filesystem read order
rather than a documented precedence" — so a duplicate name means you cannot know
which definition is live.

Malformed frontmatter is treated as an ERROR here, unlike in `doctor_skills.py`.
That asymmetry is empirical: on 2026-08-07, eleven agent files with broken YAML
turned out not to be registered *at all*, while skills with equally broken
frontmatter still load. Agents fail silently; skills survive.

    uv run --with pyyaml python ~/.claude/scripts/doctor_agents.py

ERROR (exit 1): duplicate-name · invalid-frontmatter · missing-key
WARN  (exit 0): no-frontmatter · long-description · name-filename-mismatch
"""
from __future__ import annotations

import sys
from pathlib import Path

from registry_lint import (Finding, Report, Severity, duplicate_findings,
                           read_frontmatter, registry_files, render)

__all__ = ["Severity", "scan", "main"]

DEFAULT_ROOT = Path.home() / ".claude" / "agents"
MAX_DESCRIPTION = 800


def scan(root: Path) -> Report:
    """Resolve the agent registry from the filesystem and audit it."""
    findings: list[Finding] = []
    by_name: dict[str, list[str]] = {}

    for path in registry_files(root, "*.md"):
        rel = path.relative_to(root).as_posix()
        front = read_frontmatter(path.read_text(encoding="utf-8", errors="replace"))

        if front is None:
            findings.append(Finding(
                Severity.WARN, "no-frontmatter", rel,
                "no YAML frontmatter — this file does not register as an agent"))
            continue

        if not front.strict:
            findings.append(Finding(
                Severity.ERROR, "invalid-frontmatter", rel,
                "frontmatter is not valid YAML — the agent may not register at "
                "all. Usually an unquoted example block whose `user:` / "
                "`Context:` lines end the mapping."))
            continue

        name, description = front.meta.get("name"), front.meta.get("description")
        missing = [k for k, v in (("name", name), ("description", description))
                   if not isinstance(v, str) or not v.strip()]
        if missing:
            findings.append(Finding(
                Severity.ERROR, "missing-key", rel,
                f"required key(s) absent or not a string: {', '.join(missing)}"))
            continue

        name, description = name.strip(), description.strip()
        by_name.setdefault(name, []).append(rel)

        if len(description) > MAX_DESCRIPTION:
            findings.append(Finding(
                Severity.WARN, "long-description", rel,
                f"description is {len(description)} chars (> {MAX_DESCRIPTION}); "
                f"it loads into every session — trim the <example> blocks"))

        if name != path.stem:
            findings.append(Finding(
                Severity.WARN, "name-filename-mismatch", rel,
                f"declares `name: {name}` but the file is {path.name} — legal, "
                f"but the file is hard to find by agent name"))

    findings.extend(duplicate_findings(by_name, "agent"))
    return Report(root=root, item_count=len(by_name), findings=findings)


def main(argv: list[str]) -> int:
    root = Path(argv[1]).expanduser() if len(argv) > 1 else DEFAULT_ROOT
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    report = scan(root)
    print(render(report, "agent registry"))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
