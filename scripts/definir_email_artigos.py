#!/usr/bin/env python3
"""Define ARTIGOS_EMAIL no settings.local.json desta máquina, fora do git.

    python3 scripts/definir_email_artigos.py <e-mail>      grava (idempotente)
    python3 scripts/definir_email_artigos.py --verificar   sai 0 se definido, 1 se falta
    python3 scripts/definir_email_artigos.py --gancho      SessionStart: avisa só quando falta

Por que aqui, e não no settings.json: o claude-config é PÚBLICO, e o e-mail é a identificação
do Daniel para o Unpaywall, o Crossref e o OpenAlex (autorizada em 16/09/2026 para esses três
serviços e mais nenhum), não para o GitHub. O settings.local.json fica fora do git por
whitelist, então cada máquina grava o seu; o gancho de SessionStart, este mesmo script com
`--gancho`, avisa a máquina que ainda não gravou, e cala assim que ela grava. O e-mail nunca
está neste arquivo: vem do argumento, e a sessão o tem no próprio contexto.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LOCAL = Path.home() / ".claude" / "settings.local.json"
CHAVE = "ARTIGOS_EMAIL"
AVISO = (f"{CHAVE} não está definido nesta máquina ({LOCAL}): a skill artigos-cientificos pula o "
         "Unpaywall. O Daniel autorizou em 16/09/2026 o e-mail dele para Unpaywall, Crossref e OpenAlex "
         "(skills/artigos-cientificos/SKILL.md, Perfil de acesso); grave com: "
         "python3 ~/.claude/scripts/definir_email_artigos.py <e-mail do Daniel>")


def ler() -> dict:
    return json.loads(LOCAL.read_text(encoding="utf-8")) if LOCAL.exists() else {}


def definido(dados: dict) -> bool:
    return bool((dados.get("env") or {}).get(CHAVE))


def gravar(email: str) -> int:
    if "@" not in email or " " in email:
        print(f"isto não parece um e-mail: {email!r}", file=sys.stderr)
        return 1
    dados = ler()
    env = dict(dados.get("env") or {})
    if env.get(CHAVE) == email:
        print(f"{CHAVE} já estava definido em {LOCAL}")
        return 0
    env[CHAVE] = email
    novo = {**dados, "env": env}
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL.write_text(json.dumps(novo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{CHAVE} gravado em {LOCAL}; vale a partir da próxima sessão")
    return 0


def gancho() -> int:
    """Saída no formato dos ganchos de SessionStart; silêncio quando não há o que dizer."""
    try:
        entrada = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, OSError):
        entrada = {}
    if entrada.get("source", "startup") not in ("startup", "resume"):
        return 0
    if definido(ler()):
        return 0
    print(json.dumps({"systemMessage": AVISO,
                      "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": AVISO}},
                     ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--gancho":
        return gancho()
    if argv[0] == "--verificar":
        if definido(ler()):
            print(f"{CHAVE} definido em {LOCAL}")
            return 0
        print(AVISO, file=sys.stderr)
        return 1
    return gravar(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
