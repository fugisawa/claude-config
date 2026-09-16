"""O registro de procedência: o que se grava ao lado do PDF e o parágrafo que vai para o material.

Sem procedência, a cópia é só um arquivo; com ela, quem ler o material sabe de onde o texto
veio, em que versão, com que hash e em que data foi conferido — e consegue repetir a conferência.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

VERSAO_DA_SKILL = "1.0"
NOME_DA_VERSAO = {
    "publishedVersion": "publicada",
    "acceptedVersion": "aceita (manuscrito do autor, antes da diagramação)",
    "submittedVersion": "submetida (pré-publicação)",
    "": "não declarada pela fonte",
}
NOME_DO_DEGRAU = {
    "unpaywall": "Unpaywall",
    "openalex": "OpenAlex",
    "semantic-scholar": "Semantic Scholar",
    "europepmc": "Europe PMC",
    "arxiv": "arXiv",
    "crossref-tdm": "link de mineração de texto declarado na Crossref",
    "manual": "busca manual",
}


def slug_de_doi(doi: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", doi.lower()).strip("-")


def sobrenome(nome: str) -> str:
    partes = nome.split()
    return partes[-1] if partes else ""


def autores_curtos(autores: list[str] | tuple[str, ...]) -> str:
    nomes = [sobrenome(a) for a in autores if sobrenome(a)]
    if not nomes:
        return "Autor não informado"
    if len(nomes) == 1:
        return nomes[0]
    if len(nomes) == 2:
        return f"{nomes[0]} e {nomes[1]}"
    return f"{nomes[0]} e col."


def registro_de_procedencia(resultado: dict, conferido_em: str | None = None) -> dict:
    meta = resultado.get("meta") or {}
    return {
        "skill": "artigos-cientificos",
        "versao_da_skill": VERSAO_DA_SKILL,
        "doi": resultado.get("doi", ""),
        "titulo": meta.get("titulo", ""),
        "autores": list(meta.get("autores") or []),
        "periodico": meta.get("periodico", ""),
        "ano": meta.get("ano"),
        "volume": meta.get("volume", ""),
        "numero": meta.get("numero", ""),
        "paginas": meta.get("paginas", ""),
        "status": resultado.get("status", "nao_aberto"),
        "degrau": resultado.get("degrau", ""),
        "url": resultado.get("url", ""),
        "url_final": resultado.get("url_final", ""),
        "formato": resultado.get("formato", ""),
        "versao_do_texto": resultado.get("versao", ""),
        "licenca": resultado.get("licenca", ""),
        "sha256": resultado.get("sha256", ""),
        "paginas_do_arquivo": resultado.get("paginas"),
        "produtor_do_pdf": resultado.get("produtor", ""),
        "arquivo": resultado.get("arquivo", ""),
        "texto": resultado.get("texto", ""),
        "baixado_em": resultado.get("baixado_em", ""),
        "conferido_em": conferido_em or "",
        "diario": list(resultado.get("diario") or []),
    }


def _citacao(reg: dict) -> str:
    partes = [f"{autores_curtos(reg.get('autores') or [])} ({reg.get('ano') or 's.d.'})"]
    if reg.get("titulo"):
        partes.append(f"\"{reg['titulo']}\"")
    veiculo = reg.get("periodico") or ""
    if veiculo:
        volume = reg.get("volume") or ""
        numero = f"({reg['numero']})" if reg.get("numero") else ""
        paginas = f", {reg['paginas']}" if reg.get("paginas") else ""
        partes.append(f"*{veiculo}* {volume}{numero}{paginas}".rstrip())
    if reg.get("doi"):
        partes.append(f"DOI {reg['doi']}")
    return ", ".join(p for p in partes if p) + "."


def paragrafo_fonte(reg: dict) -> str:
    """O parágrafo `Fonte:` no padrão do material: citação, de onde veio a cópia, versão, hash e data."""
    citacao = _citacao(reg)
    if reg.get("status") != "aberto":
        return (f"Fonte: {citacao} ⚑ Texto integral não aberto: nenhum degrau da escada devolveu "
                f"cópia legível ({'; '.join(reg.get('diario') or []) or 'sem tentativas registradas'}). "
                f"Os valores citados seguem não conferidos em fonte primária.")
    origem = NOME_DO_DEGRAU.get(reg.get("degrau", ""), reg.get("degrau", ""))
    versao = NOME_DA_VERSAO.get(reg.get("versao_do_texto", ""), reg.get("versao_do_texto", ""))
    paginas = reg.get("paginas_do_arquivo")
    tamanho = f", {paginas} páginas" if paginas else ""
    hash_curto = (reg.get("sha256") or "")[:12]
    data = reg.get("conferido_em") or reg.get("baixado_em", "")[:10]
    return (f"Fonte: {citacao} Cópia obtida por {origem} em {reg.get('url_final') or reg.get('url')}, "
            f"versão {versao}{tamanho}, SHA-256 {hash_curto}…; valores conferidos no texto "
            f"em {data}.")


def gravar(destino: Path, slug: str, reg: dict) -> Path:
    caminho = destino / f"{slug}.procedencia.json"
    caminho.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return caminho
