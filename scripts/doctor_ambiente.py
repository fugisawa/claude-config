#!/usr/bin/env python3
"""Health check da declaração de ambiente (~/.claude/docs/ambiente-por-maquina.md).

`~/.claude` é um clone em mais de uma máquina e o CLAUDE.md é carregado inteiro
nas duas. Frase que diga "esta máquina" num arquivo compartilhado é
infalsificável — "esta" resolve diferente conforme quem lê —, e em 10/08/2026
três de quatro afirmações estavam erradas na máquina do trabalho: mandava não
instalar um nvm já instalado, dizia node 18 onde o apt tem v20, e mandava usar
`batcat`, que não existe ali (seguir a instrução falharia).

O conserto foi mover o que varia para uma declaração com uma seção por máquina.
Este doctor é o que impede a declaração de repetir o defeito da prosa: ele
compara o que está declarado com o que a máquina responde AGORA.

**Compara comportamento, não leitura.** Guarda-se o dono do node e o major
(`nvm v24`), nunca o patch: `v24.18.0 → v24.19.1` não muda nada para quem lê a
instrução, e reprovar isso faria o gancho apanhar `--no-verify` em uma semana.
O que muda comportamento é comando que aparece ou some, dono que troca, major
que anda.

A chave é o `machine-id`, não o `hostname`: as duas máquinas se chamam
`fugisawa`, e chave que colide faria uma ler a seção da outra como sua, calada.

    uv run --with pyyaml python ~/.claude/scripts/doctor_ambiente.py

ERROR (exit 1): maquina-nao-declarada · fato-divergente · declaracao-duplicada
WARN  (exit 0): secao-pendente
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from registry_lint import Finding, Report, Severity, render

__all__ = ["Severity", "scan", "probe_machine", "main"]

DEFAULT_DECL = Path.home() / ".claude" / "docs" / "ambiente-por-maquina.md"

# Comandos cujo NOME varia por distro/instalação — a classe de fato que já
# produziu instrução impossível de seguir (`batcat`).
COMANDOS = ("bat", "batcat", "fd", "fdfind", "rg", "nvm", "conda",
            "uv", "pyenv", "bun", "brew", "magick", "convert")

BLOCO = re.compile(r"^```decl\s*\n(.*?)^```", re.MULTILINE | re.DOTALL)
CONTEXTOS_NODE = ("interativo", "nao-interativo", "apt")


def _parse_bloco(corpo: str) -> dict:
    """Um bloco ```decl``` → dicionário de campos. Linha sem `:` é ignorada."""
    campos: dict[str, str] = {}
    for linha in corpo.splitlines():
        if ":" in linha:
            chave, _, valor = linha.partition(":")
            campos[chave.strip()] = valor.strip()
    return campos


def _lista(valor: str) -> set[str]:
    return {p.strip() for p in valor.split(",") if p.strip()}


def _node(valor: str) -> tuple[str, int] | None:
    """`nvm v24` → ('nvm', 24). Devolve None se não casar — declaração torta
    não pode virar comparação silenciosamente verdadeira."""
    m = re.fullmatch(r"(\S+)\s+v?(\d+)(?:\.\S*)?", valor.strip())
    return (m.group(1), int(m.group(2))) if m else None


def scan(texto: str, probe: dict, origem: Path = DEFAULT_DECL) -> Report:
    """Confere a declaração contra o que a máquina respondeu.

    `probe` é injetado: um doctor que medisse a máquina aqui dentro só passaria
    na máquina em que foi escrito.
    """
    findings: list[Finding] = []
    blocos = [_parse_bloco(m.group(1)) for m in BLOCO.finditer(texto)]

    vistos: dict[str, int] = {}
    declarada: dict | None = None

    for campos in blocos:
        mid = campos.get("machine-id", "").strip()
        if not mid:
            continue
        if mid == "pendente":
            findings.append(Finding(
                Severity.WARN, "secao-pendente", campos.get("rotulo", "?"),
                "seção nunca medida — rode o bloco de coleta nessa máquina e "
                "substitua. Não reprova aqui: pendência de uma máquina não "
                "pode travar o commit da outra."))
            continue
        vistos[mid] = vistos.get(mid, 0) + 1
        if mid == probe["machine_id"]:
            declarada = campos

    for mid, n in sorted(vistos.items()):
        if n > 1:
            findings.append(Finding(
                Severity.ERROR, "declaracao-duplicada", mid,
                f"{n} seções declaram o mesmo machine-id — não dá para saber "
                "qual descreve a máquina."))

    if declarada is None:
        findings.append(Finding(
            Severity.ERROR, "maquina-nao-declarada", probe["machine_id"],
            f"nenhuma seção declara o machine-id {probe['machine_id']}. Esta "
            "máquina está rodando com config compartilhada e sem declarar o "
            "próprio ambiente — que é a situação que produziu instrução errada "
            "em 10/08/2026. Acrescente uma seção em docs/ambiente-por-maquina.md."))
        return Report(origem, len(blocos), findings)

    rotulo = declarada.get("rotulo", probe["machine_id"])

    presentes = _lista(declarada.get("presentes", ""))
    ausentes = _lista(declarada.get("ausentes", ""))
    for cmd, existe_agora in sorted(probe["comandos"].items()):
        declarado_presente = cmd in presentes
        declarado_ausente = cmd in ausentes
        if not (declarado_presente or declarado_ausente):
            continue  # não declarado é silêncio, não erro: a lista é curadoria
        if declarado_presente and not existe_agora:
            findings.append(Finding(
                Severity.ERROR, "fato-divergente", rotulo,
                f"`{cmd}` está declarado como presente e NÃO responde mais. "
                "Instrução que o invoque vai falhar."))
        elif declarado_ausente and existe_agora:
            findings.append(Finding(
                Severity.ERROR, "fato-divergente", rotulo,
                f"`{cmd}` está declarado como ausente e passou a existir. "
                "A declaração está mandando usar o contorno sem necessidade."))

    for contexto in CONTEXTOS_NODE:
        bruto = declarada.get(f"node-{contexto}")
        if not bruto:
            continue
        esperado, medido = _node(bruto), probe["node"].get(contexto)
        if esperado is None:
            findings.append(Finding(
                Severity.ERROR, "fato-divergente", rotulo,
                f"node-{contexto}: `{bruto}` não tem a forma `<dono> v<major>` "
                "e não pôde ser conferido."))
            continue
        if medido is None:
            continue
        if esperado != medido:
            findings.append(Finding(
                Severity.ERROR, "fato-divergente", rotulo,
                f"node-{contexto}: declarado {esperado[0]} v{esperado[1]}, "
                f"medido {medido[0]} v{medido[1]}. "
                "(Patch não conta — só dono e major.)"))

    return Report(origem, len(blocos), findings)


def _versao_major(argv: list[str]) -> int | None:
    try:
        saida = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"v?(\d+)\.\d+", saida.stdout.strip())
    return int(m.group(1)) if m else None


def _dono(caminho: str) -> str:
    if "/.nvm/" in caminho:
        return "nvm"
    if "linuxbrew" in caminho or "/homebrew/" in caminho:
        return "brew"
    if caminho.startswith("/usr/"):
        return "apt"
    return "outro"


def probe_machine() -> dict:
    """Mede a máquina. É a fronteira de E/S — fica fora do seam testado."""
    mid = ""
    try:
        mid = Path("/etc/machine-id").read_text().strip()[:8]
    except OSError:
        pass

    node: dict[str, tuple[str, int]] = {}

    # Interativo vs não-interativo diferem quando o nvm entra pelo .bashrc: o
    # `command -v node` de um script MENTE sobre o que aparece no terminal.
    #
    # E o interativo tem uma segunda armadilha, medida em 10/08/2026: com nvm
    # PREGUIÇOSO, `node` é uma FUNÇÃO de shell até a primeira chamada. Antes
    # dela, `command -v node` devolve só "node" e `type -P node` devolve o
    # binário do brew — de modo que o probe concluiria "brew" justamente onde o
    # terminal entrega nvm. Por isso a versão é pedida ANTES do caminho: chamar
    # `node --version` é o que dispara a carga e troca o PATH.
    inter = subprocess.run(
        ["bash", "-ic", "node --version 2>/dev/null; command -v node"],
        capture_output=True, text=True, timeout=30)
    linhas = [l for l in inter.stdout.strip().splitlines() if l.strip()]
    if len(linhas) >= 2:
        if (m := re.search(r"v?(\d+)\.", linhas[-2])):
            node["interativo"] = (_dono(linhas[-1]), int(m.group(1)))

    if (exe := shutil.which("node")):
        if (major := _versao_major([exe, "--version"])) is not None:
            node["nao-interativo"] = (_dono(str(Path(exe).resolve())), major)

    if Path("/usr/bin/node").exists():
        if (major := _versao_major(["/usr/bin/node", "--version"])) is not None:
            node["apt"] = ("apt", major)

    comandos = {c: shutil.which(c) is not None for c in COMANDOS}
    # nvm é função de shell, não binário: which() nunca o acha.
    comandos["nvm"] = (Path.home() / ".nvm" / "nvm.sh").is_file()

    return {"machine_id": mid, "node": node, "comandos": comandos}


def main(argv: list[str]) -> int:
    decl = Path(argv[1]).expanduser() if len(argv) > 1 else DEFAULT_DECL
    if not decl.is_file():
        print(f"declaração não encontrada: {decl}", file=sys.stderr)
        return 2
    report = scan(decl.read_text(encoding="utf-8"), probe_machine(), decl)
    print(render(report, "declaração de ambiente"))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
