"""Conferência de números e afirmações no texto extraído, sem despejar o texto no contexto.

A busca tolera o que o `pdftotext` e a tipografia mudam: sinal de menos tipográfico (U+2212),
travessão e hífen curto no lugar do sinal, espaço duro, vírgula decimal contra ponto, e espaços
soltos em volta de `=`, `<` e `>`. O resultado é uma lista de achados com número da linha e
uma linha de contexto para cada lado, que é o que se lê para decidir — e o que se cita.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

TROCAS = str.maketrans({
    "−": "-", "–": "-", "‐": "-", "‑": "-", " ": " ",
    " ": " ", " ": " ",
})


@dataclass(frozen=True)
class Achado:
    expressao: str
    linha: int
    texto: str
    antes: tuple[str, ...]
    depois: tuple[str, ...]


def normalizar(s: str) -> str:
    return re.sub(r"[ \t]+", " ", s.translate(TROCAS))


def _padrao(expressao: str) -> re.Pattern:
    """Regex tolerante: espaços opcionais em volta de operadores e decimal com vírgula ou ponto."""
    partes = []
    for trecho in re.split(r"(\s+|[=<>≤≥]|[.,](?=\d))", normalizar(expressao)):
        if not trecho:
            continue
        if trecho.isspace():
            partes.append(r"\s*")
        elif trecho in "=<>≤≥":
            partes.append(r"\s*" + re.escape(trecho) + r"\s*")
        elif trecho in ".,":
            partes.append(r"[.,]")
        else:
            inicio = r"(?<!\d)" if trecho[0].isdigit() else ""
            fim = r"(?!\d)" if trecho[-1].isdigit() else ""
            partes.append(inicio + re.escape(trecho) + fim)
    return re.compile("".join(partes), re.IGNORECASE)


def procurar(texto: str, expressoes: list[str], contexto: int = 1) -> list[Achado]:
    linhas = normalizar(texto).splitlines()
    achados = []
    for expressao in expressoes:
        padrao = _padrao(expressao)
        for i, linha in enumerate(linhas):
            if padrao.search(linha):
                achados.append(Achado(
                    expressao=expressao, linha=i + 1, texto=linha.strip(),
                    antes=tuple(l.strip() for l in linhas[max(0, i - contexto):i]),
                    depois=tuple(l.strip() for l in linhas[i + 1:i + 1 + contexto])))
    return achados


def relatorio(achados: list[Achado], expressoes: list[str], limite: int = 6) -> str:
    """Um bloco por expressão: quantas vezes apareceu e as primeiras ocorrências com contexto."""
    blocos = []
    for expressao in expressoes:
        meus = [a for a in achados if a.expressao == expressao]
        if not meus:
            blocos.append(f"✗ {expressao!r}: não encontrado")
            continue
        blocos.append(f"✓ {expressao!r}: {len(meus)} ocorrência(s)")
        for a in meus[:limite]:
            for l in a.antes:
                blocos.append(f"      {l}")
            blocos.append(f"  {a.linha:>5} {a.texto}")
            for l in a.depois:
                blocos.append(f"      {l}")
        if len(meus) > limite:
            blocos.append(f"      … e mais {len(meus) - limite}")
    return "\n".join(blocos)
