#!/usr/bin/env python3
"""PostToolUse advisory linter for Claude Code skill/agent definitions.

Fires only when a SKILL.md (under .../skills/) or an agent .md (under .../agents/)
is written/edited. Skills are validated strictly (the skill loader rejects bad
YAML / name!=dir / description>1024). Agents are validated leniently, matching
how Claude Code's agent loader tolerates colons in the description line.

Exit 0 = OK / not applicable.  Exit 2 = surface the warning to Claude.
"""
import sys, json, re, pathlib

def warn(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

fp = (data.get("tool_input") or {}).get("file_path", "")
if not fp:
    sys.exit(0)
p = pathlib.Path(fp)
s = str(p)
is_skill = p.name == "SKILL.md" and "/skills/" in s
is_agent = "/agents/" in s and p.suffix == ".md" and "/skills/" not in s
if not (is_skill or is_agent) or not p.exists():
    sys.exit(0)

text = p.read_text()
m = re.match(r"^---\n(.*?)\n---", text, re.S)
if not m:
    warn(f"[skill-lint] {p.name}: missing YAML frontmatter (--- … ---).")
body = m.group(1)

nm = re.search(r"^name:\s*(.+?)\s*$", body, re.M)
if not nm:
    warn(f"[skill-lint] {p.name}: frontmatter missing 'name'.")
name = nm.group(1).strip().strip("'\"")
expected = p.parent.name if is_skill else p.stem
if name != expected:
    kind = "directory" if is_skill else "file"
    warn(f"[skill-lint] {p.name}: name '{name}' must equal the {kind} name '{expected}'.")

if is_skill:
    try:
        import yaml
        meta = yaml.safe_load(body) or {}
    except Exception as e:
        first = str(e).splitlines()[0]
        warn(f"[skill-lint] {p.name}: invalid YAML frontmatter — if the description "
             f"contains a colon, quote it or use a '>-' block scalar. ({first})")
    desc = meta.get("description", "")
    if not desc:
        warn(f"[skill-lint] {p.name}: missing 'description'.")
    if len(desc) > 1024:
        warn(f"[skill-lint] {p.name}: description is {len(desc)} chars (>1024) — the "
             f"skill loader will reject it. Trim it.")

sys.exit(0)
