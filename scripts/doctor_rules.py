#!/usr/bin/env python3
"""Verifica se `rules/common/agents.md` ainda diz a verdade sobre quem serve cada agente.

O arquivo de regras manda usar nove agentes PROATIVAMENTE, "located in
`~/.claude/agents/`". Em 11/08/2026 isso era falso para OITO deles: só
`code-reviewer` é local; os outros vêm do plugin ECC. A falha é silenciosa por
construção — a regra some junto com o plugin, e o que sobra é um arquivo que
manda usar agente inexistente, o que se lê como "o Claude não seguiu a regra".

É a lição `skills/learned/referencia-declarada-sem-validador.md`: identificador
escrito à mão nomeia alvo ENUMERÁVEL, e ninguém cruza. Aqui se cruza. A coluna
`Provider` da tabela é a declaração; o disco é a verdade; divergir reprova.

Também é a resposta à divergência entre máquinas. O plugin está instalado em
casa e (medido em 11/08/2026) não no trabalho — logo o mesmo arquivo compartilhado
é verdadeiro de um lado e mentira do outro. Nenhum recado resolve isso, porque a
prosa não sabe onde está sendo lida; esta checagem sabe, porque roda nas duas.

    uv run --with pyyaml python scripts/doctor_rules.py

Exit 1 = a tabela declara provedor que o disco não confirma.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGRAS = ROOT / "rules" / "common" / "agents.md"
SETTINGS = ROOT / "settings.json"
INSTALADOS = ROOT / "plugins" / "installed_plugins.json"

# Apelido curto na tabela -> id real do plugin. O id NÃO é confiado: ele é
# cruzado contra installed_plugins.json, que é a razão de esta linha existir
# em vez de o apelido ser resolvido no olho.
APELIDOS = {"ecc": "everything-claude-code@everything-claude-code"}


def nomes_com_frontmatter(base: Path) -> dict[str, Path]:
    """Mesma identidade que o harness usa: só o campo `name:`, varredura recursiva."""
    achados: dict[str, Path] = {}
    if not base.is_dir():
        return achados
    for p in sorted(base.rglob("*.md")):
        try:
            texto = p.read_text(encoding="utf-8", errors="ignore")[:2000]
        except OSError:
            continue
        m = re.search(r"^name:\s*(.+)$", texto, re.M)
        if m:
            achados.setdefault(m.group(1).strip(), p)
    return achados


def agentes_de_plugins() -> dict[str, str]:
    """name: -> id do plugin, para todo plugin instalado cujo caminho existe."""
    if not INSTALADOS.is_file():
        return {}
    try:
        dados = json.loads(INSTALADOS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    prov: dict[str, str] = {}
    for pid, entradas in dados.get("plugins", {}).items():
        for e in entradas:
            base = Path(e.get("installPath", ""))
            if not base.is_dir():
                continue
            for nome in nomes_com_frontmatter(base / "agents"):
                prov.setdefault(nome, pid)
    return prov


def habilitados() -> dict[str, bool]:
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8")).get("enabledPlugins", {})
    except (OSError, json.JSONDecodeError):
        return {}


def linhas_declaradas() -> list[tuple[str, str]]:
    """Lê (agente, provedor) da tabela cuja segunda coluna se chama Provider."""
    if not REGRAS.is_file():
        return []
    linhas, dentro = [], False
    for bruta in REGRAS.read_text(encoding="utf-8").splitlines():
        if not bruta.lstrip().startswith("|"):
            dentro = False
            continue
        campos = [c.strip() for c in bruta.strip().strip("|").split("|")]
        if len(campos) < 2:
            continue
        if campos[0].lower() == "agent" and campos[1].lower() == "provider":
            dentro = True
            continue
        if dentro and not set(campos[0]) <= {"-", ":", " "}:
            linhas.append((campos[0], campos[1]))
    return linhas


def scan(
    declaradas: list[tuple[str, str]],
    locais: set[str],
    plugins: dict[str, str],
    ligados: dict[str, bool],
) -> list[str]:
    """Seam puro: recebe as quatro listas já lidas e devolve os erros.

    Nada de disco aqui. Um doctor que lesse a máquina de dentro do teste só
    passaria na máquina em que foi escrito — que é o defeito que ele existe
    para pegar.
    """
    erros: list[str] = []

    if not declaradas:
        erros.append(
            "a tabela de agentes sumiu ou perdeu a coluna `Provider` — "
            "sem ela esta checagem não guarda nada (e passaria em silêncio)"
        )

    for agente, provedor in declaradas:
        real_local = agente in locais
        real_plugin = plugins.get(agente)

        if provedor == "local":
            if not real_local:
                onde = f"vem do plugin {real_plugin}" if real_plugin else "não existe em lugar nenhum"
                erros.append(f"[{agente}] declarado `local`, mas {onde}")
            continue

        pid = APELIDOS.get(provedor)
        if pid is None:
            erros.append(
                f"[{agente}] provedor `{provedor}` desconhecido — "
                f"apelidos válidos: local, {', '.join(sorted(APELIDOS))}"
            )
            continue
        if real_plugin is None:
            erros.append(
                f"[{agente}] declarado `{provedor}`, mas o plugin não está instalado "
                f"NESTA máquina — instale-o, ou tire a linha da tabela"
            )
            continue
        if real_plugin != pid:
            erros.append(f"[{agente}] declarado `{provedor}` ({pid}), mas quem serve é {real_plugin}")
            continue
        if ligados.get(pid) is not True:
            estado = "sem entrada em enabledPlugins" if pid not in ligados else f"enabledPlugins={ligados[pid]!r}"
            erros.append(
                f"[{agente}] o plugin {pid} está instalado mas NÃO habilitado ({estado}) — "
                f"a regra manda usar um agente que não carrega"
            )

    return erros


def main() -> int:
    declaradas = linhas_declaradas()
    locais = nomes_com_frontmatter(ROOT / "agents")
    plugins = agentes_de_plugins()
    ligados = habilitados()

    print(f"regras      : {REGRAS.relative_to(ROOT)}")
    print(f"  declarados: {len(declaradas)}")
    print(f"  locais     : {len(locais)} agentes | plugins: {len(plugins)} agentes")

    erros = scan(declaradas, set(locais), plugins, ligados)

    print(f"  problemas : {len(erros)}")
    if erros:
        print("\nERROS")
        for e in erros:
            print(f"  {e}")
        return 1
    print("\nOK — todo agente citado na regra resolve, e pelo provedor declarado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
