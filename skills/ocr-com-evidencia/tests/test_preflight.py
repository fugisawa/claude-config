"""Seam tests for preflight.py: what a new machine is missing, stated so it can be acted on."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "preflight.py"
HAS_TESSERACT = shutil.which("tesseract") is not None


def run(*args: str, env: dict | None = None, expect: int | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8", env=env or dict(os.environ, PYTHONIOENCODING="utf-8"))
    if expect is not None:
        assert proc.returncode == expect, f"rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    return proc


def empty_path_env() -> dict:
    """An environment where no OCR tool can be found, whatever the machine has."""
    return {"PATH": "/nonexistent", "HOME": os.environ.get("HOME", "/tmp"), "PYTHONIOENCODING": "utf-8"}


class TestPreflight:
    def test_json_report_names_every_tool_and_the_requested_language(self):
        proc = run("--lang", "por", "--json")
        report = json.loads(proc.stdout)
        assert set(report["tools"]) >= {"uv", "tesseract", "pdftoppm", "ocrmypdf"}
        assert report["language_requested"] == "por"
        assert "ready" in report

    def test_without_tools_it_fails_and_says_what_to_install(self):
        proc = run("--lang", "por", env=empty_path_env(), expect=1)
        assert "tesseract" in proc.stdout and "uv" in proc.stdout
        assert "dpkg -x" in proc.stdout, "the no-sudo recipe must be printed where it is needed"

    def test_without_tools_json_is_not_ready(self):
        proc = run("--lang", "por", "--json", env=empty_path_env(), expect=1)
        report = json.loads(proc.stdout)
        assert report["ready"] is False
        assert report["tools"]["tesseract"]["present"] is False
        assert report["language_available"] is False

    @pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract not on PATH")
    def test_with_tesseract_the_language_is_checked_against_list_langs(self):
        proc = run("--lang", "por", "--json")
        report = json.loads(proc.stdout)
        assert report["tools"]["tesseract"]["present"] is True
        assert "por" in report["tools"]["tesseract"]["languages"]
        assert report["language_available"] is True
        missing = json.loads(run("--lang", "xyz", "--json", expect=1).stdout)
        assert missing["language_available"] is False

    def test_help(self):
        proc = run("--help", expect=0)
        assert "--lang" in proc.stdout
