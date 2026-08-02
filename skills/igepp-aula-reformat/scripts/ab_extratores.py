#!/usr/bin/env python3
"""A/B de extratores de PDF — mede, no SEU pdf, o que cada um ganha e o que perde.

Existe porque a escolha de extrator desta skill não é óbvia e já foi medida uma vez
(28/07/2026, contra a marca d'água do IGEPP): docling extraiu ~23% mais texto e zero
artefato de marca d'água, mas perdeu TODA a ênfase inline — e em texto legal o negrito
carrega sentido. Empate técnico, veredito "complemento, não substituto". Aquele script se
perdeu; este o reconstrói e acrescenta um terceiro braço, o pdfplumber, para testar a
outra decisão dura da skill: "não confie no dump para tabelas, transcreva da imagem".

    uv run --with pymupdf --with pymupdf4llm --with pdfplumber python ab_extratores.py in.pdf
    # com o braço docling (instalação pesada, ~2 GB):
    uv run --with pymupdf --with pymupdf4llm --with pdfplumber --with docling \
        python ab_extratores.py in.pdf --docling

O que ele NÃO faz: decidir por você. Ele imprime o placar e grava a saída de cada braço
lado a lado, para você abrir os dois e olhar. Número não decide sozinho qual perdeu menos
do que importa.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# O kernel CUDA desta máquina é incompatível com o runtime que o docling carrega (herança
# do salto NVIDIA 535→580): sem isto ele aborta na importação. Precisa vir ANTES do import.
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

RE_NEGRITO = re.compile(r"\*\*[^*\n]{2,}\*\*|__[^_\n]{2,}__")
RE_SUBLINHADO = re.compile(r"<u>.*?</u>|~~.*?~~", re.S)
RE_LINHA_TABELA = re.compile(r"^\s*\|.*\|\s*$", re.M)
# A marca d'água do IGEPP entra no dump como fragmentos soltos de "Edição 20xx" — às vezes
# rotacionados caractere a caractere, daí o padrão frouxo.
RE_MARCA_DAGUA = re.compile(r"Edi[çc][ãa]o\s*\d{4}|E\s*d\s*i\s*[çc]\s*[ãa]\s*o", re.I)


@dataclass
class Resultado:
    """Placar de um braço. Sem julgamento embutido — o julgamento é do leitor."""

    nome: str
    texto: str = ""
    segundos: float = 0.0
    erro: str = ""
    extras: dict[str, int] = field(default_factory=dict)

    @property
    def metricas(self) -> dict[str, int]:
        if self.erro:
            return {}
        return {
            "caracteres": len(self.texto),
            "linhas": self.texto.count("\n"),
            "negrito": len(RE_NEGRITO.findall(self.texto)),
            "sublinhado/tachado": len(RE_SUBLINHADO.findall(self.texto)),
            "linhas de tabela": len(RE_LINHA_TABELA.findall(self.texto)),
            "marca d'água": len(RE_MARCA_DAGUA.findall(self.texto)),
            **self.extras,
        }


def _cronometra(nome: str, fn) -> Resultado:
    t0 = time.perf_counter()
    try:
        texto, extras = fn()
        return Resultado(nome, texto, time.perf_counter() - t0, extras=extras)
    except ImportError as e:
        return Resultado(nome, erro=f"não instalado: {e.name}")
    except Exception as e:                                  # noqa: BLE001 — é um probe
        return Resultado(nome, erro=f"{type(e).__name__}: {e}")


def braco_pymupdf4llm(pdf: Path, paginas: int | None) -> tuple[str, dict[str, int]]:
    import pymupdf4llm

    kw = {"pages": list(range(paginas))} if paginas else {}
    return pymupdf4llm.to_markdown(str(pdf), **kw), {}


def braco_docling(pdf: Path, paginas: int | None) -> tuple[str, dict[str, int]]:
    from docling.document_converter import DocumentConverter

    doc = DocumentConverter().convert(str(pdf)).document
    md = doc.export_to_markdown()
    if paginas:                       # o converter não recorta; corta-se depois, grosseiro
        md = "\n".join(md.splitlines()[: paginas * 60])
    return md, {"imagens marcadas": md.count("<!-- image -->")}


def braco_pdfplumber(pdf: Path, paginas: int | None) -> tuple[str, dict[str, int]]:
    """Terceiro braço: o que interessa aqui NÃO é o texto corrido, é a tabela.

    A skill hoje manda transcrever tabela olhando a imagem, porque o dump embaralha as
    células. O pdfplumber detecta tabela por LINHAS do desenho, não pelo fluxo do texto —
    é uma hipótese diferente, e é isso que este braço mede.
    """
    import pdfplumber

    partes: list[str] = []
    tabelas = celulas = 0
    with pdfplumber.open(str(pdf)) as arq:
        for pagina in arq.pages[:paginas] if paginas else arq.pages:
            partes.append(pagina.extract_text() or "")
            for tabela in pagina.extract_tables():
                tabelas += 1
                celulas += sum(len(linha) for linha in tabela)
                for linha in tabela:
                    limpa = [(c or "").replace("\n", " ").strip() for c in linha]
                    partes.append("| " + " | ".join(limpa) + " |")
    return "\n".join(partes), {"tabelas detectadas": tabelas, "células": celulas}


def imprime_placar(resultados: list[Resultado]) -> None:
    vivos = [r for r in resultados if not r.erro]
    for r in resultados:
        if r.erro:
            print(f"  {r.nome:<14} — {r.erro}", file=sys.stderr)
    if not vivos:
        sys.exit("nenhum braço rodou; instale ao menos um extrator")

    chaves: list[str] = []
    for r in vivos:                                  # união preservando a ordem de inserção
        chaves += [k for k in r.metricas if k not in chaves]

    largura = max(len(k) for k in chaves) + 2
    print(f"\n{'métrica':<{largura}}" + "".join(f"{r.nome:>16}" for r in vivos))
    print("─" * (largura + 16 * len(vivos)))
    for chave in chaves:
        linha = f"{chave:<{largura}}"
        for r in vivos:
            v = r.metricas.get(chave)
            linha += f"{'—' if v is None else v:>16}"
        print(linha)
    print(f"{'segundos':<{largura}}" + "".join(f"{r.segundos:>16.1f}" for r in vivos))

    print("\nComo ler:")
    print("  · negrito/sublinhado ZERO num braço = ele perdeu a ênfase inline. Em texto")
    print("    legal isso não é detalhe: o negrito marca o que a banca troca.")
    print("  · marca d'água > 0 = fragmentos da tarja vazaram para o dump.")
    print("  · tabelas detectadas (pdfplumber) testa a regra 'transcreva da imagem':")
    print("    se vier 0 ou com células vazias, a regra continua certa.")
    print("  · caracteres a mais NÃO é melhor por si — pode ser mobília repetida.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pdf", type=Path)
    p.add_argument("--paginas", type=int, default=None,
                   help="limita às N primeiras páginas (amostra rápida)")
    p.add_argument("--docling", action="store_true",
                   help="inclui o braço docling (instalação pesada)")
    p.add_argument("--out", type=Path, default=None,
                   help="grava a saída de cada braço aqui, para comparação visual")
    a = p.parse_args()

    if not a.pdf.is_file():
        sys.exit(f"não achei {a.pdf}")

    bracos = [("pymupdf4llm", braco_pymupdf4llm), ("pdfplumber", braco_pdfplumber)]
    if a.docling:
        bracos.insert(1, ("docling", braco_docling))

    print(f"A/B em {a.pdf.name}"
          + (f" (primeiras {a.paginas} páginas)" if a.paginas else ""))
    resultados = [_cronometra(nome, lambda f=fn: f(a.pdf, a.paginas)) for nome, fn in bracos]
    imprime_placar(resultados)

    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        for r in resultados:
            if not r.erro:
                destino = a.out / f"{a.pdf.stem}.{r.nome}.md"
                destino.write_text(r.texto, encoding="utf-8")
                print(f"  → {destino}")
        print("\nAbra os arquivos lado a lado. O placar diz quanto; só o olho diz o quê.")


if __name__ == "__main__":
    main()
