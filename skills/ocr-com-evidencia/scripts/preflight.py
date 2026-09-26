#!/usr/bin/env python3
"""Say what this machine is missing for the photo OCR scripts, and how to get it.

Checks the tools the scripts call, and whether Tesseract has the requested
language pack — a present binary without the pack is the failure that matters.
Python dependencies are not checked here: ``uv run --script`` resolves them
from each script's PEP 723 block on first use.

Usage:
  python preflight.py --lang por
  python preflight.py --lang por --json

Exit 0 when the minimum is present (uv, Tesseract with the language); 1 otherwise.
"""
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from typing import Any

REQUIRED = ("uv", "tesseract")
OPTIONAL = ("pdftoppm", "ocrmypdf")
HINTS = {
    "uv": "instale o uv: curl -LsSf https://astral.sh/uv/install.sh | sh",
    "pdftoppm": "opcional (renderiza páginas de PDF): apt install poppler-utils",
    "ocrmypdf": "opcional (PDF pesquisável): uv tool install ocrmypdf — exige tesseract e ghostscript",
}
TESSERACT_NO_SUDO = """\
tesseract ausente. Com sudo: apt install tesseract-ocr tesseract-ocr-{lang}
Sem sudo, extraia os .deb do Ubuntu numa pasta do usuário e exponha um wrapper no PATH:
  mkdir -p ~/.local/opt/tesseract && cd ~/.local/opt/tesseract
  apt-get download tesseract-ocr libtesseract5 liblept5 tesseract-ocr-eng tesseract-ocr-{lang}
  for d in *.deb; do dpkg -x "$d" .; done
  cat > ~/.local/bin/tesseract <<'SH'
  #!/usr/bin/env bash
  ROOT="$(cd "$(dirname "$(readlink -f "$0")")/../opt/tesseract" && pwd)"
  export LD_LIBRARY_PATH="$ROOT/usr/lib/x86_64-linux-gnu${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}}"
  export TESSDATA_PREFIX="${{TESSDATA_PREFIX:-$ROOT/usr/share/tesseract-ocr/5/tessdata}}"
  exec "$ROOT/usr/bin/tesseract" "$@"
  SH
  chmod +x ~/.local/bin/tesseract && tesseract --list-langs"""
PACK_MISSING = "tesseract presente, mas sem o pacote '{lang}' (idiomas: {langs}). Instale tesseract-ocr-{lang} ou copie {lang}.traineddata para o tessdata."


def tesseract_languages(binary: str) -> list[str]:
    try:
        proc = subprocess.run([binary, "--list-langs"], capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return []
    lines = (proc.stdout + proc.stderr).splitlines()
    return sorted(l.strip() for l in lines[1:] if l.strip() and not l.startswith("List of"))


def probe(lang: str, tesseract_bin: str | None) -> dict[str, Any]:
    tools: dict[str, dict[str, Any]] = {}
    for name in REQUIRED + OPTIONAL:
        path = tesseract_bin if name == "tesseract" and tesseract_bin else shutil.which(name)
        tools[name] = {"present": path is not None, "path": path, "required": name in REQUIRED}
    languages = tesseract_languages(tools["tesseract"]["path"]) if tools["tesseract"]["present"] else []
    tools["tesseract"]["languages"] = languages
    language_available = bool(lang) and lang in languages
    ready = all(tools[n]["present"] for n in REQUIRED) and (language_available or not lang)
    return {"language_requested": lang, "language_available": language_available, "ready": ready, "tools": tools}


def hints(report: dict[str, Any]) -> list[str]:
    lang = report["language_requested"]
    out = []
    for name, info in report["tools"].items():
        if info["present"]:
            continue
        out.append(TESSERACT_NO_SUDO.format(lang=lang or "por") if name == "tesseract" else HINTS[name])
    if report["tools"]["tesseract"]["present"] and lang and not report["language_available"]:
        out.append(PACK_MISSING.format(lang=lang, langs=", ".join(report["tools"]["tesseract"]["languages"]) or "nenhum"))
    return out


def render(report: dict[str, Any]) -> str:
    lines = [f"{'ferramenta':12} {'estado':10} caminho"]
    for name, info in report["tools"].items():
        state = "presente" if info["present"] else ("AUSENTE" if info["required"] else "ausente (opcional)")
        lines.append(f"{name:12} {state:10} {info['path'] or ''}")
    tess = report["tools"]["tesseract"]
    if tess["present"]:
        lines.append(f"idiomas do tesseract: {', '.join(tess['languages']) or 'nenhum'}")
    lines.append(f"idioma pedido '{report['language_requested']}': {'disponível' if report['language_available'] else 'NÃO disponível'}")
    lines.append("pronto: " + ("sim" if report["ready"] else "não"))
    lines += [""] + hints(report)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lang", default="por", help="Tesseract language the scripts will request")
    parser.add_argument("--tesseract-bin", default=os.environ.get("TESSERACT_BIN"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = probe(args.lang, args.tesseract_bin)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report), end="" if not args.json else "\n")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
