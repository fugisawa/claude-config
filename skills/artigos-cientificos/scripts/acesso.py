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
manuais (cópia do autor, conectores, navegador da app, o acesso do perfil, pedido ao autor), que
ficam em `references/escada-de-acesso.md`. A cópia que um degrau manual trouxe entra pela
`registrar_manual`, com a etiqueta (A, B ou C) que quem a obteve declara; D não se registra.

Nas duas entradas, o PDF cuja p. 1 é a capa do ResearchGate vira cópia de leitura sem ela, e o
PDF obtido fica guardado em `originais/`, ao lado; o recibo segue com o hash e as páginas dele.

Antes de rodar a escada, o `abrir` lê o recibo que já está no destino. Se o recibo registra uma
cópia aberta, o `abrir` não a troca sem `substituir`; se registra uma tentativa que falhou, o
`abrir` herda dele o diário.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import os
import re
import shutil
import subprocess
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


def _agora() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


@contextlib.contextmanager
def _desfaz_se_falhar(*caminhos: Path):
    """Põe de lado, com nome provisório, os arquivos que o bloco pode sobrescrever. Se o bloco falha, apaga o
    que ele deixou nesses caminhos e devolve os antigos ao lugar; se dá certo, apaga os antigos. É o que impede
    que a extração que falha depois do download deixe a cópia baixada no lugar da que já estava."""
    anteriores = {caminho: caminho.with_name(f".{caminho.name}.anterior") for caminho in caminhos if caminho.exists()}
    for caminho, anterior in anteriores.items():
        os.replace(caminho, anterior)
    try:
        yield
    except BaseException:
        for caminho in caminhos:
            caminho.unlink(missing_ok=True)
        for caminho, anterior in anteriores.items():
            os.replace(anterior, caminho)
        raise
    for anterior in anteriores.values():
        anterior.unlink(missing_ok=True)


def _meta_serializavel(meta: Registro | None) -> dict | None:
    return {**asdict(meta), "autores": list(meta.autores)} if meta else None


# ── a capa do ResearchGate ────────────────────────────────────────────────────────────────

def _guardado(arquivo: Path) -> Path:
    """Onde fica o PDF obtido quando a cópia de leitura é ele sem a capa: `originais/`, com o mesmo nome."""
    return arquivo.parent / "originais" / arquivo.name


def _tem_capa(arquivo: Path) -> bool:
    return leitura.eh_capa_do_researchgate(leitura.texto_da_pagina(arquivo, 1))


def retirar_capa(arquivo: Path, *, info=leitura.pdfinfo, extrair=leitura.extrair_texto) -> tuple[dict, Path]:
    """Guarda o PDF obtido em `originais/`, com o mesmo nome e a data que tinha, e grava no lugar dele a
    cópia de leitura, sem a p. 1 e com a data de agora: o transporte entre as máquinas só troca arquivo
    por outro mais novo, e é assim que a cópia cortada substitui a que ainda tem capa na outra máquina.
    O corte e a extração do texto se fazem numa cópia provisória, e o disco só muda quando os dois
    deram certo; se um falha, tudo fica como estava. Devolve o que o recibo diz da cópia de leitura e
    o texto dela."""
    guardado = _guardado(arquivo)
    if guardado.exists() and leitura.sha256_de(guardado) != leitura.sha256_de(arquivo):
        raise RuntimeError(f"{guardado} já existe e é outro PDF; mova-o antes, ou mantenha a capa com --manter-capa")
    provisoria = arquivo.with_name(f".{arquivo.stem}.sem-capa.pdf")
    guardando = guardado.with_name(f".{guardado.name}.guardando")
    try:
        ferramenta = leitura.sem_a_primeira_pagina(arquivo, provisoria)
        texto_provisorio = extrair(provisoria, "pdf")
        copia = {"retirada": "capa do ResearchGate", "pagina_retirada": 1,
                 "paginas": info(provisoria).get("paginas"), "sha256": leitura.sha256_de(provisoria),
                 "pdf_obtido": str(guardado), "ferramenta": ferramenta}
        guardado.parent.mkdir(exist_ok=True)
        shutil.copy2(arquivo, guardando)
        os.replace(guardando, guardado)
        os.replace(provisoria, arquivo)
        texto = arquivo.with_suffix(".txt")
        os.replace(texto_provisorio, texto)
    finally:
        for resto in (provisoria, provisoria.with_suffix(".txt"), guardando):
            resto.unlink(missing_ok=True)
    return copia, texto


def _linha_da_capa(copia: dict, paginas_do_obtido) -> str:
    return (f"{copia['retirada']} (p. {copia['pagina_retirada']} do PDF obtido) retirada com {copia['ferramenta']}; "
            f"a cópia de leitura, neste caminho, tem {copia['paginas'] or '?'} páginas e SHA-256 {copia['sha256']}; "
            f"o PDF obtido, de {paginas_do_obtido or '?'} páginas e com o SHA-256 deste recibo, está em "
            f"{copia['pdf_obtido']}; o texto é o da cópia de leitura")


def _capa_no_abrir(arquivo: Path, formato: str, manter_capa: bool,
                   extrair) -> tuple[dict | None, Path | None, list[str]]:
    """No `abrir`, o download já está no disco quando a capa aparece: a que não sai fica, e o diário diz
    por quê, em vez de a abertura inteira falhar. Devolve a cópia de leitura, o texto dela e a nota."""
    if formato != "pdf" or manter_capa or not _tem_capa(arquivo):
        return None, None, []
    try:
        return (*retirar_capa(arquivo, extrair=extrair), [])
    except RuntimeError as erro:
        return None, None, [f"capa do ResearchGate mantida na p. 1: {erro}"]


def _escada(doi: str, destino: Path, *, email: str | None, apenas_listar: bool, manter_capa: bool,
            obter, buscar, extrair, agora: str | None) -> dict:
    """A escada em si, sem olhar recibo nenhum: reúne os candidatos, baixa o primeiro que é texto de verdade e
    devolve o resultado."""
    candidatos, meta, diario = coletar(doi, email, buscar=buscar, obter=obter)
    base = {"doi": doi, "status": "nao_aberto", "meta": _meta_serializavel(meta),
            "candidatos": [asdict(c) for c in candidatos], "diario": diario,
            "tentado_em": agora or _agora()}
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
        try:
            with _desfaz_se_falhar(arquivo, arquivo.with_suffix(".txt")):
                arquivo.write_bytes(corpo)
                copia, texto, nota = _capa_no_abrir(arquivo, formato, manter_capa, extrair)
                texto = texto or extrair(arquivo, formato)
        except (RuntimeError, subprocess.CalledProcessError) as erro:
            raise RuntimeError(f"{cand.degrau}: a cópia baixada de {final} não deu texto ({erro}); "
                               "o destino ficou como estava") from erro
        obtido = Path(copia["pdf_obtido"]) if copia else arquivo
        info = leitura.pdfinfo(obtido) if formato == "pdf" else {}
        return {
            **base, "status": "aberto", "arquivo": str(arquivo), "texto": str(texto),
            "formato": formato, "degrau": cand.degrau, "url": cand.url, "url_final": final,
            "versao": cand.versao, "licenca": cand.licenca,
            "etiqueta": procedencia.etiqueta_do_degrau(cand.degrau),
            "sha256": leitura.sha256_de(obtido), "paginas": info.get("paginas"),
            "produtor": info.get("produtor", ""), "copia_de_leitura": copia,
            "baixado_em": agora or _agora(),
            "diario": diario + [f"{cand.degrau}: aberto como {formato} a partir de {final}"]
                      + ([_linha_da_capa(copia, info.get("paginas"))] if copia else nota),
        }
    return {**base, "diario": diario}


# ── o recibo que já estava no destino ─────────────────────────────────────────────────────

MARCA_DA_TENTATIVA = "nova tentativa em "
MESMO_RESULTADO = ", com o mesmo resultado"


def _repetida(linha: str) -> bool:
    return linha.startswith(MARCA_DA_TENTATIVA) and linha.endswith(MESMO_RESULTADO)


def _ultimo_resultado(diario: list[str]) -> list[str]:
    """As linhas da última tentativa registrada no diário: as que vêm depois da última linha que marca uma
    tentativa de resultado novo, sem as linhas do fim que só dizem que ele se repetiu."""
    fim = len(diario)
    while fim and _repetida(diario[fim - 1]):
        fim -= 1
    marcas = [i for i in range(fim) if diario[i].startswith(MARCA_DA_TENTATIVA)]
    return diario[marcas[-1] + 1 if marcas else 0:fim]


def _herdar_tentativa(anterior: dict | None, resultado: dict) -> dict:
    """O recibo de 'não obtido' que estava no destino passa ao resultado da nova tentativa o diário dele e a
    data da primeira tentativa, porque é a mesma busca que continua. O diário novo entra depois da linha que
    marca a tentativa, com a data dela; se ele repete o da última tentativa, fica só a linha, dizendo isso. O
    recibo de cópia aberta não se emenda."""
    if not procedencia.tentativa_que_falhou(anterior):
        return resultado
    antigo, novo = list(anterior.get("diario") or []), resultado["diario"]
    marca = f"{MARCA_DA_TENTATIVA}{resultado['tentado_em'][:10]}"
    diario = antigo + ([marca + MESMO_RESULTADO] if novo == _ultimo_resultado(antigo) else [marca, *novo])
    return {**resultado, "diario": diario, "tentado_em": anterior.get("tentado_em") or resultado["tentado_em"]}


def _recusa_da_copia_aberta(caminho: Path, anterior: dict) -> str:
    return (f"o recibo {caminho} registra a cópia aberta {anterior.get('arquivo') or '(sem arquivo declarado)'}, "
            "e o abrir não a troca sem que se peça: passe --substituir se a cópia que a escada abrir deve tomar o "
            "lugar dela e do recibo, --listar para só ver os candidatos, ou outro --destino")


def _recusa_de_outro_doi(caminho: Path, anterior: dict, doi: str) -> str:
    return (f"o recibo {caminho} é do DOI {anterior['doi']}, e não de {doi}, que dá o mesmo nome de arquivo: "
            "use outro --destino")


def abrir(doi: str, destino: Path, *, email: str | None = None, apenas_listar: bool = False,
          manter_capa: bool = False, anterior: dict | None = None, substituir: bool = False,
          obter=fontes.http_get, buscar=fontes.http_json, extrair=leitura.extrair_texto,
          agora: str | None = None) -> dict:
    """Roda a escada para um DOI e devolve o resultado como dicionário serializável.

    `status` é `aberto` (texto no disco), `listado` (só a lista de candidatos, com `--listar`) ou
    `nao_aberto` (nenhum candidato rendeu texto; o diário diz o que cada um respondeu). A capa do
    ResearchGate sai da cópia de leitura, salvo com `manter_capa`.

    `anterior` é o recibo que já estava no destino. Se ele é de outro DOI com o mesmo nome de arquivo, a
    abertura se interrompe antes de qualquer consulta. Se registra uma cópia aberta, ela também se
    interrompe, porque o download escreveria por cima da cópia e o recibo novo tomaria o lugar do dela; só
    com `substituir` ela segue. Se registra uma tentativa que falhou, o resultado herda dele o diário e a
    data da primeira tentativa (`_herdar_tentativa`). Quando o texto não sai da cópia baixada, o destino
    fica como estava (`_desfaz_se_falhar`)."""
    if anterior and not apenas_listar:
        caminho = procedencia.caminho_do_recibo(destino, procedencia.slug_de_doi(doi))
        if procedencia.de_outro_doi(anterior, doi):
            raise RuntimeError(_recusa_de_outro_doi(caminho, anterior, doi))
        if procedencia.copia_aberta(anterior) and not substituir:
            raise RuntimeError(_recusa_da_copia_aberta(caminho, anterior))
    resultado = _escada(doi, destino, email=email, apenas_listar=apenas_listar, manter_capa=manter_capa,
                        obter=obter, buscar=buscar, extrair=extrair, agora=agora)
    return resultado if apenas_listar else _herdar_tentativa(anterior, resultado)


# ── a cópia que veio de degrau manual ─────────────────────────────────────────────────────

VERSAO_DECLARADA = {"publicada": "publishedVersion", "aceita": "acceptedVersion",
                    "submetida": "submittedVersion", "": ""}
FORMATO_DO_SUFIXO = {".pdf": "pdf", ".xml": "xml", ".html": "html", ".htm": "html"}


def _texto_a_extrair(arquivo: Path, formato: str, texto: Path | None, sobrescrever: bool) -> Path | None:
    """Confere, antes de tocar em qualquer arquivo, de onde vem o texto da cópia. A página HTML só entra
    com o texto já extraído dela, que se usa como está; o PDF e o XML têm o texto extraído para o .txt
    ao lado, e o .txt que já existe só se sobrescreve quando se pede. Devolve o .txt que a extração vai
    substituir, ou None."""
    if formato == "html":
        if texto is None:
            raise RuntimeError(f"{arquivo.name}: página HTML só se registra com --texto, o texto já extraído "
                               "dela, porque o script não extrai texto de HTML")
        if not texto.is_file():
            raise RuntimeError(f"o texto {texto} não existe ou não é um arquivo")
        if texto.resolve() == arquivo.resolve():
            raise RuntimeError(f"--texto aponta para a própria cópia, {arquivo.name}; passe o texto extraído dela")
        if texto.stat().st_size == 0:
            raise RuntimeError(f"o texto {texto} está vazio")
        return None
    if texto is not None:
        raise RuntimeError("--texto vale só para página HTML; o texto de PDF e de XML se extrai da cópia")
    alvo = arquivo.with_suffix(".txt")
    if not alvo.exists():
        return None
    if not sobrescrever:
        raise RuntimeError(f"{alvo} já existe, e o registro não sobrescreve texto sem que se peça: passe "
                           f"--sobrescrever-texto se ele pode ser trocado pelo texto extraído de {arquivo.name}, "
                           "ou dê outro nome à cópia se ele veio de outra, como a página HTML ao lado do XML")
    return alvo


def _capa_a_retirar(arquivo: Path, formato: str, manter_capa: bool) -> bool:
    """Se a p. 1 do PDF é a capa do ResearchGate. Sem capa, o PDF que tem um homônimo guardado em
    `originais/` é, quase certamente, a cópia de leitura de um corte anterior, e registrá-lo como PDF
    obtido gravaria no recibo um hash que não confere com a URL; isso se recusa."""
    if formato != "pdf" or manter_capa:
        return False
    if _tem_capa(arquivo):
        return True
    guardado = _guardado(arquivo)
    if guardado.exists():
        raise RuntimeError(f"{guardado} existe, e {arquivo.name} parece a cópia de leitura de um corte anterior, "
                           "sem a capa e com outro hash: para registrar de novo, devolva o PDF obtido ao lugar dela, "
                           "ou passe --manter-capa se esta é mesmo a cópia obtida")
    return False


def registrar_manual(doi: str, arquivo: Path, *, url: str, origem: str, etiqueta: str,
                     versao: str = "", meta=None, texto: Path | None = None, anterior: dict | None = None,
                     sobrescrever_texto: bool = False, manter_capa: bool = False, destino: Path | None = None,
                     extrair=leitura.extrair_texto, info=leitura.pdfinfo, agora: str | None = None) -> dict:
    """A cópia obtida por degrau manual (site do autor, pedido atendido, biblioteca) ganha a mesma
    procedência do `abrir`: texto extraído, hash, páginas, data — e a etiqueta que quem a obteve
    declara, porque o script não tem como saber de onde ela veio. Rota D não se registra.

    `meta` são os metadados, ou a função que os busca, chamada só depois das verificações, para que o
    registro recusado não gaste consulta às APIs. `texto` é o texto já extraído da página HTML, que
    entra sem reextração. `anterior` é o recibo que já estava em `destino` (por padrão, a pasta da
    cópia). Se ele é de outro DOI com o mesmo nome de arquivo, o registro se recusa antes de tocar em
    arquivo e de consultar as APIs, porque herdaria o diário de uma tentativa alheia ou tomaria o lugar
    do recibo de outra cópia. Se ele registra uma tentativa que falhou, o diário dela e a data em que
    foi feita passam para este, porque é a mesma busca que agora terminou. A capa do ResearchGate sai
    da cópia de leitura, salvo com `manter_capa`, e só depois de todas as verificações."""
    if procedencia.de_outro_doi(anterior, doi):
        caminho = procedencia.caminho_do_recibo(destino or arquivo.parent, procedencia.slug_de_doi(doi))
        raise RuntimeError(_recusa_de_outro_doi(caminho, anterior, doi))
    if etiqueta not in procedencia.ETIQUETAS_REGISTRAVEIS:
        raise RuntimeError(f"etiqueta {etiqueta!r} não se registra: só A, B ou C (D está fora da escada)")
    if versao not in VERSAO_DECLARADA:
        raise RuntimeError(f"versão {versao!r}: use publicada, aceita ou submetida")
    formato = FORMATO_DO_SUFIXO.get(arquivo.suffix.lower())
    if formato is None:
        raise RuntimeError(f"{arquivo.name}: só se registra PDF, XML JATS ou página HTML com o texto já extraído")
    if formato == "pdf" and not eh_pdf(arquivo.read_bytes()[:1024]):
        raise RuntimeError(f"{arquivo.name} não é um PDF (falta o cabeçalho %PDF-)")
    com_capa = _capa_a_retirar(arquivo, formato, manter_capa)
    texto = Path(texto) if texto is not None else None
    substituido = _texto_a_extrair(arquivo, formato, texto, sobrescrever_texto)
    meta = meta() if callable(meta) else meta
    copia = None
    if com_capa:
        copia, texto = retirar_capa(arquivo, info=info, extrair=extrair)
    elif formato != "html":
        texto = extrair(arquivo, formato)
    obtido = Path(copia["pdf_obtido"]) if copia else arquivo
    avisos = [f"{substituido} existia e foi substituído pelo texto extraído de {arquivo.name}"] if substituido else []
    dados = info(obtido) if formato == "pdf" else {}
    quando = agora or _agora()
    diario, tentado_em = [f"manual: {origem}, em {url}"], quando
    if procedencia.tentativa_que_falhou(anterior):
        diario = list(anterior.get("diario") or []) + diario
        tentado_em = anterior.get("tentado_em") or quando
    if copia:
        diario = diario + [_linha_da_capa(copia, dados.get("paginas"))]
    return {
        "doi": doi, "status": "aberto", "meta": meta if isinstance(meta, dict) else _meta_serializavel(meta),
        "candidatos": [], "diario": diario, "tentado_em": tentado_em,
        "arquivo": str(arquivo), "texto": str(texto), "formato": formato, "degrau": "manual",
        "origem": origem, "url": url, "url_final": url, "versao": VERSAO_DECLARADA[versao],
        "licenca": "", "etiqueta": etiqueta, "sha256": leitura.sha256_de(obtido),
        "paginas": dados.get("paginas"), "produtor": dados.get("produtor", ""), "copia_de_leitura": copia,
        "baixado_em": quando, "avisos": avisos,
    }
