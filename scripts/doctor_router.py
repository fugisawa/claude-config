#!/usr/bin/env python3
"""Verifica se o router `skills/ask-daniel/SKILL.md` ainda diz a verdade.

O CLAUDE.md avisa que "um router desatualizado mente" — mas mente em SILÊNCIO:
citar uma skill que foi arquivada, um agente aposentado ou um comando que nunca
existiu não produz erro nenhum. Em 07/08/2026 o router mandava usar `/verify`,
que não existe (o nativo é `/run`), e ninguém percebeu.

Resolve cada `nome` citado em crase contra: skills ativas, skills arquivadas,
agentes ativos, agentes aposentados, commands, plugins (`ns:skill`), nativos do
harness e tools de MCP.

    uv run --with pyyaml python scripts/doctor_router.py

Exit 1 = citação aponta para algo arquivado/aposentado/inexistente.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUTER = ROOT / "skills" / "ask-daniel" / "SKILL.md"

# Nativos do harness e tools de MCP não vivem no disco — mantenha à mão.
# Ao adicionar um nativo novo ao router, acrescente aqui.
NATIVOS = {
    "code-review", "simplify", "loop", "schedule", "update-config", "dataviz",
    "claude-api", "run", "init", "security-review", "commit", "ultra",
    "artifact-design", "artifact-diagramming", "artifact-capabilities",
    "keybindings-help", "fewer-permission-prompts", "claude-in-chrome",
}
MCP_TOOLS = {"mcp-brasil", "search_tools", "call_tool"}
# Skills de projeto (fora de ~/.claude) e agentes de plugin — resolvem noutro escopo.
FORA_DO_ESCOPO = {"artefatos-estudo", "planner", "tdd-guide", "research"}

# Menções históricas deliberadas: o router explica um erro passado de propósito.
# Formato: nome -> trecho que precisa estar na mesma linha para valer a isenção.
HISTORICAS = {"verify": "que não existe"}


def nomes_com_frontmatter(base: Path) -> set[str]:
    achados = set()
    if not base.is_dir():
        return achados
    for p in base.rglob("*.md"):
        try:
            m = re.search(r"^name:\s*(\S+)", p.read_text(encoding="utf-8", errors="replace"), re.M)
        except OSError:
            continue
        if m:
            achados.add(m.group(1))
    return achados


def main() -> int:
    if not ROUTER.is_file():
        print(f"router não encontrado: {ROUTER}")
        return 1
    linhas = ROUTER.read_text(encoding="utf-8").splitlines()

    skills = {d.name for d in (ROOT / "skills").iterdir()} if (ROOT / "skills").is_dir() else set()
    arquivadas = {d.name for d in (ROOT / "skills-archive").iterdir()} if (ROOT / "skills-archive").is_dir() else set()
    agentes = nomes_com_frontmatter(ROOT / "agents")
    aposentados = nomes_com_frontmatter(ROOT / "agents-archive")
    commands = {p.stem for p in (ROOT / "commands").glob("*.md")}
    ok = skills | agentes | commands | NATIVOS | MCP_TOOLS | FORA_DO_ESCOPO

    problemas: list[tuple[int, str, str]] = []
    vistos: set[str] = set()
    for n, linha in enumerate(linhas, 1):
        for nome in re.findall(r"`/?([a-z][a-z0-9:_-]{2,})`", linha):
            if ":" in nome or nome in ok or nome in vistos:
                continue
            if nome in HISTORICAS and HISTORICAS[nome] in linha:
                continue  # menção histórica explicada na própria linha
            vistos.add(nome)
            if nome in arquivadas:
                problemas.append((n, nome, "skill ARQUIVADA em skills-archive/ — restaure ou remova a citação"))
            elif nome in aposentados:
                problemas.append((n, nome, "agente APOSENTADO em agents-archive/ — restaure ou remova a citação"))
            else:
                problemas.append((n, nome, "não resolve para skill, agente, command, plugin, nativo ou MCP"))

    print(f"router      : {ROUTER.relative_to(ROOT)}")
    print(f"skills ativas: {len(skills)} | arquivadas: {len(arquivadas)} | agentes: {len(agentes)}")
    print(f"problemas   : {len(problemas)}")
    if problemas:
        print("\nPROBLEMAS")
        for n, nome, motivo in problemas:
            print(f"  linha {n}: `{nome}` — {motivo}")
        print("\num router que cita o que não existe manda o Claude para o vazio, sem erro.")
        return 1
    print("\nOK — toda citação do router resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
