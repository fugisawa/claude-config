"""Testes do doctor_skills — seam: scan(root) -> Report.

Fixtures reproduzem defeitos observados na árvore real (delimitador com espaço
à direita, linha `--- Unknown`, description que só repete o nome), com o
resultado esperado escrito à mão.
"""
import tempfile
import unittest
from pathlib import Path

from registry_lint import Severity
from doctor_skills import scan

CLEAN = """---
name: alpha-tool
description: Does a specific, describable thing. Use when the user asks for that thing by name or by symptom.
---

# Alpha
Body.
"""


def write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class ScanTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def codes(self, severity: Severity) -> list[str]:
        return sorted(f.code for f in scan(self.root).findings if f.severity is severity)

    def test_clean_tree_has_no_findings(self) -> None:
        write(self.root, "alpha-tool/SKILL.md", CLEAN)
        report = scan(self.root)
        self.assertEqual(report.findings, [])
        self.assertEqual(report.item_count, 1)
        self.assertTrue(report.ok)

    def test_finds_nested_skills(self) -> None:
        # Real tree has skills/security/aws-security-audit/SKILL.md
        write(self.root, "security/aws-audit/SKILL.md",
              CLEAN.replace("alpha-tool", "aws-audit"))
        self.assertEqual(scan(self.root).item_count, 1)

    def test_tolerates_trailing_space_on_delimiter(self) -> None:
        # animejs-animation opens with "--- " and DOES load in Claude Code.
        # A strict parser would call this "no frontmatter" — a false positive.
        write(self.root, "alpha-tool/SKILL.md", "--- \n" + CLEAN[4:])
        self.assertEqual(scan(self.root).findings, [])

    def test_salvageable_yaml_warns_but_is_not_an_error(self) -> None:
        # alpha-vantage has a stray "--- Unknown" line. Strict YAML rejects it,
        # yet the skill registers, so this is fragility, not breakage.
        write(self.root, "alpha-tool/SKILL.md", """---
name: alpha-tool
description: Does a specific, describable thing. Use when the user asks for it.
--- Unknown
metadata:
    author: someone
---

Body.
""")
        self.assertEqual(self.codes(Severity.WARN), ["malformed-yaml"])
        self.assertTrue(scan(self.root).ok)
        self.assertEqual(scan(self.root).item_count, 1, "name must still be recovered")

    def test_salvage_reads_block_scalars(self) -> None:
        # The google-*-automation family writes `description: |` with the text on
        # following indented lines, and carries a stray `--- Apache-2.0` line.
        # A naive line scan recovers "|" — a 1-char description — and would
        # wrongly report the skill as unroutable.
        write(self.root, "gmail-automation/SKILL.md", """---
name: gmail-automation
description: |
  Interact with Gmail - search emails, read messages, send emails and drafts.
  Use when the user asks to search, read, send, or label email.
--- Apache-2.0
metadata:
  license: Apache-2.0
---

Body.
""")
        report = scan(self.root)
        self.assertEqual(
            sorted(f.code for f in report.findings), ["malformed-yaml"],
            "the stray `---` line is fragile, but the description is fine")

    def test_duplicate_name_is_an_error(self) -> None:
        write(self.root, "one/SKILL.md", CLEAN)
        write(self.root, "two/SKILL.md", CLEAN)
        self.assertIn("duplicate-name", self.codes(Severity.ERROR))
        self.assertFalse(scan(self.root).ok)

    def test_missing_description_is_an_error(self) -> None:
        write(self.root, "alpha-tool/SKILL.md", "---\nname: alpha-tool\n---\n\nBody.\n")
        self.assertEqual(self.codes(Severity.ERROR), ["missing-key"])

    def test_no_frontmatter_at_all_is_an_error(self) -> None:
        write(self.root, "alpha-tool/SKILL.md", "# Just a doc\n")
        self.assertEqual(self.codes(Severity.ERROR), ["no-frontmatter"])

    def test_description_echoing_the_name_warns(self) -> None:
        # Real cases: build -> "build", food-database-query -> "Food Database Query".
        # Such a description carries no routing signal at all.
        write(self.root, "alpha-tool/SKILL.md",
              CLEAN.replace("Does a specific, describable thing. Use when the user "
                            "asks for that thing by name or by symptom.", "Alpha Tool"))
        self.assertEqual(self.codes(Severity.WARN), ["echo-description"])

    def test_very_thin_description_warns(self) -> None:
        write(self.root, "alpha-tool/SKILL.md",
              CLEAN.replace("Does a specific, describable thing. Use when the user "
                            "asks for that thing by name or by symptom.", "Fuzz stuff"))
        self.assertEqual(self.codes(Severity.WARN), ["thin-description"])

    def test_a_short_but_meaningful_description_is_accepted(self) -> None:
        # favicon: "Generate favicons from a source image" (37 chars) is fine.
        write(self.root, "favicon/SKILL.md",
              CLEAN.replace("alpha-tool", "favicon").replace(
                  "Does a specific, describable thing. Use when the user asks for "
                  "that thing by name or by symptom.",
                  "Generate favicons from a source image"))
        self.assertEqual(scan(self.root).findings, [])

    def test_name_not_matching_directory_warns(self) -> None:
        write(self.root, "pdf/SKILL.md", CLEAN.replace("alpha-tool", "pdf-official"))
        self.assertEqual(self.codes(Severity.WARN), ["name-dir-mismatch"])

    def test_name_with_spaces_or_capitals_warns(self) -> None:
        write(self.root, "agent-development/SKILL.md",
              CLEAN.replace("name: alpha-tool", "name: Agent Development"))
        self.assertEqual(
            self.codes(Severity.WARN), ["name-dir-mismatch", "unslugged-name"])

    def test_overlong_description_warns_without_failing(self) -> None:
        write(self.root, "alpha-tool/SKILL.md", CLEAN.replace(
            "Does a specific, describable thing. Use when the user asks for that "
            "thing by name or by symptom.", "x" * 1600))
        self.assertEqual(self.codes(Severity.WARN), ["long-description"])
        self.assertTrue(scan(self.root).ok)

    def test_ignores_non_skill_markdown(self) -> None:
        write(self.root, "alpha-tool/SKILL.md", CLEAN)
        write(self.root, "alpha-tool/reference.md", "# notes\n")
        write(self.root, "README.md", "# skills\n")
        self.assertEqual(scan(self.root).item_count, 1)
        self.assertEqual(scan(self.root).findings, [])


if __name__ == "__main__":
    unittest.main()
