"""Testes do doctor_agents — seam: scan(root) -> Report.

Fixtures são árvores mínimas em tmpdir com resultado esperado conhecido,
escrito à mão (nunca recalculado pela mesma lógica do código sob teste).
"""
import tempfile
import unittest
from pathlib import Path

from doctor_agents import Severity, scan

CLEAN = """---
name: alpha
description: Does alpha things.
---

# Alpha
Body.
"""


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ScanTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def codes(self, severity: Severity) -> list[str]:
        return sorted(f.code for f in scan(self.root).findings if f.severity is severity)

    def test_clean_tree_has_no_findings(self) -> None:
        write(self.root, "alpha.md", CLEAN)
        write(self.root, "sub/beta.md", CLEAN.replace("alpha", "beta"))
        report = scan(self.root)
        self.assertEqual(report.findings, [])
        self.assertEqual(report.item_count, 2)
        self.assertTrue(report.ok)

    def test_scan_is_recursive(self) -> None:
        write(self.root, "deep/deeper/gamma.md", CLEAN.replace("alpha", "gamma"))
        self.assertEqual(scan(self.root).item_count, 1)

    def test_duplicate_name_across_subdirs_is_an_error(self) -> None:
        # Same `name:` in two files — the loader picks one by filesystem read
        # order, so this must be reported, not tolerated.
        write(self.root, "alpha.md", CLEAN)
        write(self.root, "_archived/alpha.md", CLEAN)
        self.assertEqual(self.codes(Severity.ERROR), ["duplicate-name"])
        dup = next(f for f in scan(self.root).findings if f.code == "duplicate-name")
        self.assertIn("_archived/alpha.md", dup.detail)
        self.assertIn("alpha.md", dup.detail)
        self.assertFalse(scan(self.root).ok)

    def test_name_from_frontmatter_not_filename(self) -> None:
        # Identity comes from `name:`; differing filenames do NOT collide.
        write(self.root, "one.md", CLEAN)
        write(self.root, "two.md", CLEAN.replace("name: alpha", "name: distinct"))
        self.assertEqual(self.codes(Severity.ERROR), [])

    def test_malformed_yaml_is_an_error(self) -> None:
        # The real-world break: an unquoted example block whose `user:` /
        # `Context:` lines terminate the frontmatter mapping.
        write(self.root, "bad.md", """---
name: bad
description: Use this agent. Examples:
<example>
Context: something happens
user: "hi"
</example>
color: red
---

Body.
""")
        self.assertEqual(self.codes(Severity.ERROR), ["invalid-frontmatter"])

    def test_missing_required_keys_is_an_error(self) -> None:
        write(self.root, "noname.md", "---\ndescription: Orphan.\n---\n\nBody.\n")
        self.assertEqual(self.codes(Severity.ERROR), ["missing-key"])

    def test_file_without_frontmatter_only_warns(self) -> None:
        # agents/ legitimately holds a few non-agent docs (README, notes).
        # ERROR is reserved for files that TRY to be an agent and are broken.
        write(self.root, "README.md", "# Just docs\n")
        self.assertEqual(self.codes(Severity.WARN), ["no-frontmatter"])
        self.assertTrue(scan(self.root).ok)

    def test_overlong_description_warns_but_does_not_fail(self) -> None:
        write(self.root, "alpha.md", CLEAN.replace(
            "Does alpha things.", "x" * 900))
        report = scan(self.root)
        self.assertEqual(self.codes(Severity.WARN), ["long-description"])
        self.assertTrue(report.ok, "warnings must not fail the gate")

    def test_name_filename_mismatch_warns(self) -> None:
        write(self.root, "architect-review.md",
              CLEAN.replace("name: alpha", "name: architect-reviewer"))
        self.assertEqual(self.codes(Severity.WARN), ["name-filename-mismatch"])

    def test_ignores_non_markdown_files(self) -> None:
        write(self.root, "alpha.md", CLEAN)
        write(self.root, "notes.txt", "not an agent")
        write(self.root, "helper.py", "print('hi')")
        self.assertEqual(scan(self.root).item_count, 1)
        self.assertEqual(scan(self.root).findings, [])


if __name__ == "__main__":
    unittest.main()
