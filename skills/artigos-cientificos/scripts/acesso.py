"""A escada de acesso que dá para automatizar: reúne candidatos, ordena, baixa o primeiro que é
texto de verdade e devolve um resultado com diário de tudo o que foi tentado.

A ordem é decidida por três chaves, nesta prioridade: o formato (PDF antes de XML, e os dois
antes de página de pouso), a versão (publicada, depois aceita, depois pré-publicação) e o degrau
(Unpaywall, OpenAlex, Semantic Scholar, Europe PMC, arXiv, TDM da Crossref). Página de pouso
entra por último porque só serve se trouxer `citation_pdf_url` no cabeçalho.

Cada fonte é uma função pura que devolve (metadados ou None, candidatos, linha do diário); a
rede entra só por `buscar` (JSON) e `obter` (bytes), injetáveis. O e-mail só é passado às
chamadas de Crossref, OpenAlex e Unpaywall, e `fontes.http_get` o barra por host de qualquer modo.

O que esta escada NÃO faz, de propósito: Sci-Hub, LibGen, Anna's Archive ou qualquer
espelho que redistribua sem licença. O que ela não abre vira instrução para os degraus
manuais (cópia do autor, conectores, navegador da app, pedido ao autor, acesso institucional),
que ficam em `references/escada-de-acesso.md`.
"""
from __future__ import annotations

import datetime as dt
import re
import urllib.parse
from dataclasses import asdict
from pathlib import Path

import fontes
import leitura
import procedencia
from fontes import Candidato, Registro

DEGRAUS = ("unpaywall", "openalex", "semantic-scholar", "europepmc", "arxiv", "crossref-tdm")
RANK_TIPO = {"pdf": 0, "xml": 1, "landing": 2}
RANK_VERSAO = {"publishedVersion": 0, "acceptedVersion": 1, "submittedVersion": 2, "": 3}
META_PDF = (
    re.compile(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']', re.I),
)
ACEITAR_TEXTO = "application/pdf,application/xml;q=0.9,text/html;q=0.8,*/*;q=0.5"
SEM_EMAIL = "unpaywall: pulado — defina ARTIGOS_EMAIL ou --email (a API exige e-mail real)"


def ordenar(candidatos: list[Candidato]) -> list[Candidato]:
    """Remove URLs repetidas (fica a primeira) e ordena por formato, versão e degrau."""
    vistos: set[str] = set()
    unicos = []
    for c in candidatos:
        if c.url not in vistos:
            vistos.add(c.url)
            unicos.append(c)

    def chave(c: Candidato):
        degrau = DEGRAUS.index(c.degrau) if c.degrau in DEGRAUS else len(DEGRAUS)
        return (RANK_TIPO.get(c.tipo, 3), RANK_VERSAO.get(c.versao, 3), degrau)

    return sorted(unicos, key=chave)


def eh_pdf(corpo: bytes) -> bool:
    return b"%PDF-" in corpo[:1024]


def pdf_url_na_pagina(html: str, base: str) -> str:
    """O `citation_pdf_url` que repositórios e editoras põem no cabeçalho, resolvido contra a base."""
    for padrao in META_PDF:
        m = padrao.search(html)
        if m:
            return urllib.parse.urljoin(base, m.group(1))
    return ""


# ── uma função por fonte: (metadados ou None, candidatos, linha do diário) ─────────────────

def _json(buscar, url: str, *, email: str | None = None) -> dict | None:
    status, obj = buscar(url, email=email)
    return obj if status == 200 and isinstance(obj, dict) else None


def _crossref(doi: str, email: str | None, buscar):
    msg = (_json(buscar, fontes.crossref_url(doi, email), email=email) or {}).get("message")
    if not msg:
        return None, [], "crossref: sem registro"
    return fontes.normalizar_crossref(msg), fontes.candidatos_crossref(msg), "crossref: metadados obtidos"


def _openalex(doi: str, email: str | None, buscar):
    obj = _json(buscar, fontes.openalex_url(doi, email), email=email)
    if obj is None:
        return None, [], "openalex: sem registro"
    registro, cands = fontes.normalizar_openalex(obj), fontes.candidatos_openalex(obj)
    return registro, cands, f"openalex: oa_status={registro.oa_status or '?'}, {len(cands)} candidato(s)"


def _unpaywall(doi: str, email: str | None, buscar):
    if not email:
        return None, [], SEM_EMAIL
    obj = _json(buscar, fontes.unpaywall_url(doi, email), email=email)
    if obj is None:
        return None, [], "unpaywall: sem resposta útil"
    cands = fontes.candidatos_unpaywall(obj)
    return None, cands, f"unpaywall: oa_status={obj.get('oa_status') or '?'}, {len(cands)} candidato(s)"


def _semantic_scholar(doi: str, buscar):
    obj = _json(buscar, fontes.s2_url(doi))
    if obj is None:
        return [], "semantic-scholar: sem registro", {}
    cands = fontes.candidatos_s2(obj)
    return cands, f"semantic-scholar: {len(cands)} candidato(s)", fontes.ids_s2(obj)


def _europepmc(doi: str, pmcid: str, buscar):
    if not pmcid:
        pmcid = fontes.pmcid_de_europepmc(_json(buscar, fontes.europepmc_busca_url(doi)) or {})
    linha = f"europepmc: {'PMCID ' + pmcid if pmcid else 'sem texto integral'}"
    return fontes.candidatos_europepmc(pmcid), linha


def _arxiv(arxiv_id: str, meta: Registro | None, buscar, obter):
    """Candidato do arXiv e, quando ninguém deu metadados, Semantic Scholar por arXiv:id e depois o Atom."""
    if not arxiv_id:
        return None, [], []
    cands, linhas, meta_ax = fontes.candidatos_arxiv(arxiv_id), [f"arxiv: {arxiv_id}"], None
    if meta is None:
        obj = _json(buscar, fontes.s2_arxiv_url(arxiv_id))
        if obj is not None:
            meta_ax, cands = fontes.normalizar_s2(obj), cands + fontes.candidatos_s2(obj)
            linhas = linhas + [f"semantic-scholar: metadados pelo arXiv:{arxiv_id}"]
    if meta is None and meta_ax is None:
        status, corpo, _, _ = obter(fontes.arxiv_api_url(arxiv_id), aceitar="application/atom+xml")
        meta_ax = fontes.normalizar_arxiv_atom(corpo) if status == 200 else None
        if meta_ax is not None:
            linhas = linhas + [f"arxiv: metadados pelo Atom de {arxiv_id}"]
    return meta_ax, cands, linhas


def coletar(doi: str, email: str | None, *, buscar=fontes.http_json, obter=fontes.http_get):
    """Consulta as APIs abertas. Cada falha vira uma linha do diário, nunca uma exceção."""
    meta_cr, c_cr, l_cr = _crossref(doi, email, buscar)
    meta_oa, c_oa, l_oa = _openalex(doi, email, buscar)
    _, c_un, l_un = _unpaywall(doi, email, buscar)
    c_s2, l_s2, ids = _semantic_scholar(doi, buscar)
    meta = meta_cr or meta_oa
    arxiv_id = (fontes.extrair_arxiv_id(doi) or (meta_oa.arxiv_id if meta_oa else "")
                or ids.get("arxiv_id", ""))
    pmcid = (meta_oa.pmcid if meta_oa else "") or ids.get("pmcid", "")
    c_ep, l_ep = _europepmc(doi, pmcid, buscar)
    meta_ax, c_ax, l_ax = _arxiv(arxiv_id, meta, buscar, obter)
    diario = [l_cr, l_oa, l_un, l_s2, l_ep, *l_ax]
    return ordenar(c_cr + c_oa + c_un + c_s2 + c_ep + c_ax), meta or meta_ax, diario


# ── baixar e abrir ────────────────────────────────────────────────────────────────────────

def baixar(cand: Candidato, *, obter=fontes.http_get):
    """Tenta um candidato. Devolve (corpo, url_final, formato) ou None."""
    status, corpo, final, _ = obter(cand.url, aceitar=ACEITAR_TEXTO)
    if status != 200 or not corpo:
        return None
    if eh_pdf(corpo):
        return corpo, final, "pdf"
    if cand.tipo == "xml" and corpo.lstrip().startswith(b"<"):
        return corpo, final, "xml"
    url_pdf = pdf_url_na_pagina(corpo[:300_000].decode("utf-8", "replace"), final)
    if url_pdf and url_pdf != cand.url:
        status, corpo, final, _ = obter(url_pdf, aceitar="application/pdf")
        if status == 200 and eh_pdf(corpo):
            return corpo, final, "pdf"
    return None


def _meta_serializavel(meta: Registro | None) -> dict | None:
    return {**asdict(meta), "autores": list(meta.autores)} if meta else None


def abrir(doi: str, destino: Path, *, email: str | None = None, apenas_listar: bool = False,
          obter=fontes.http_get, buscar=fontes.http_json, extrair=leitura.extrair_texto,
          agora: str | None = None) -> dict:
    """Roda a escada para um DOI e devolve o resultado como dicionário serializável.

    `status` é `aberto` (texto no disco), `listado` (só a lista de candidatos, com `--listar`) ou
    `nao_aberto` (nenhum candidato rendeu texto; o diário diz o que cada um respondeu)."""
    candidatos, meta, diario = coletar(doi, email, buscar=buscar, obter=obter)
    base = {"doi": doi, "status": "nao_aberto", "meta": _meta_serializavel(meta),
            "candidatos": [asdict(c) for c in candidatos], "diario": diario}
    if apenas_listar:
        return {**base, "status": "listado" if candidatos else "nao_aberto"}
    if not candidatos:
        return base

    destino.mkdir(parents=True, exist_ok=True)
    slug = procedencia.slug_de_doi(doi)
    for cand in candidatos:
        baixado = baixar(cand, obter=obter)
        if baixado is None:
            diario = diario + [f"{cand.degrau}: nada legível em {cand.url}"]
            continue
        corpo, final, formato = baixado
        arquivo = destino / f"{slug}.{formato}"
        arquivo.write_bytes(corpo)
        texto = extrair(arquivo, formato)
        info = leitura.pdfinfo(arquivo) if formato == "pdf" else {}
        return {
            **base, "status": "aberto", "arquivo": str(arquivo), "texto": str(texto),
            "formato": formato, "degrau": cand.degrau, "url": cand.url, "url_final": final,
            "versao": cand.versao, "licenca": cand.licenca,
            "sha256": leitura.sha256_de(arquivo), "paginas": info.get("paginas"),
            "produtor": info.get("produtor", ""),
            "baixado_em": agora or dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "diario": diario + [f"{cand.degrau}: aberto como {formato} a partir de {final}"],
        }
    return {**base, "diario": diario}
