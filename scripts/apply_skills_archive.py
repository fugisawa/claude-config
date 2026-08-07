#!/usr/bin/env python3
"""Replica o arquivamento de skills descrito em docs/skills-inventory.md.

As skills de terceiros não são versionadas (o .gitignore cura item a item),
então mover 295 diretórios para skills-archive/ NÃO viaja pelo git — sem este
script a outra máquina continuaria com elas carregadas, e as duas divergiriam
em silêncio. O inventário é a fonte da verdade; aqui só se aplica.

    uv run --with pyyaml python scripts/apply_skills_archive.py --dry-run
    uv run --with pyyaml python scripts/apply_skills_archive.py

Reverter é `mv skills-archive/<nome> skills/` — ou --restore <nome>.
Reinicie o Claude Code depois: o watcher só vê diretórios que já existiam
no início da sessão.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
ARCHIVE = ROOT / "skills-archive"
INVENTORY = ROOT / "docs" / "skills-inventory.md"

# linhas do índice: | `nome` | familia | descrição |
ROW = re.compile(r"^\|\s*`([a-z0-9][a-z0-9._-]*)`\s*\|")


def nomes_do_inventario() -> list[str]:
    if not INVENTORY.is_file():
        sys.exit(f"inventário não encontrado: {INVENTORY}")
    achados = [m.group(1) for m in map(ROW.match, INVENTORY.read_text(encoding="utf-8").splitlines()) if m]
    if not achados:
        sys.exit(f"nenhuma skill listada em {INVENTORY} — formato mudou?")
    return sorted(set(achados))


def curadas() -> set[str]:
    """Skills versionadas — jamais arquivar, mesmo que listadas por engano."""
    import subprocess

    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "skills/"], capture_output=True, text=True
    ).stdout.split()
    return {p.split("/")[1] for p in out if "/" in p}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="mostra sem mover")
    ap.add_argument("--restore", metavar="NOME", help="traz uma skill de volta")
    args = ap.parse_args()

    if args.restore:
        src, dst = ARCHIVE / args.restore, SKILLS / args.restore
        if not src.exists():
            sys.exit(f"não está no arquivo: {src}")
        if dst.exists():
            sys.exit(f"já existe em skills/: {dst}")
        shutil.move(str(src), str(dst))
        print(f"restaurada: {args.restore} — reinicie o Claude Code")
        return 0

    protegidas = curadas()
    alvo = nomes_do_inventario()
    mover, ausentes, barradas = [], [], []
    for nome in alvo:
        if nome in protegidas:
            barradas.append(nome)  # trava: curada nunca sai
        elif (SKILLS / nome).exists() or (SKILLS / nome).is_symlink():
            mover.append(nome)
        else:
            ausentes.append(nome)

    print(f"inventário: {len(alvo)} | já arquivadas/ausentes: {len(ausentes)} | a mover: {len(mover)}")
    if barradas:
        print(f"BARRADAS (versionadas, ignoradas): {', '.join(barradas)}")
    if not mover:
        print("nada a fazer — esta máquina já está alinhada.")
        return 0
    if args.dry_run:
        for nome in mover:
            print(f"  [dry-run] skills/{nome} -> skills-archive/{nome}")
        return 0

    ARCHIVE.mkdir(exist_ok=True)
    for nome in mover:
        shutil.move(str(SKILLS / nome), str(ARCHIVE / nome))
    print(f"movidas {len(mover)} — reinicie o Claude Code para o registro refletir")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
