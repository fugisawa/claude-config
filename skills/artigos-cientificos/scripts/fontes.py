"""Clientes das APIs abertas de literatura, com a rede isolada em duas funções.

Cada API tem três peças: a função que monta a URL, a que normaliza a resposta já
decodificada em um `Registro`, e a que extrai `Candidato`s de acesso ao texto.
As duas últimas são puras (recebem dicionários, devolvem objetos imutáveis) e são
o que os testes cobrem sem rede. Só `http_get` e `http_json` tocam a rede.

APIs cobertas: Crossref, OpenAlex, Unpaywall, Semantic Scholar, Europe PMC e arXiv.
Nenhuma exige chave. Unpaywall exige um e-mail real (rejeita placeholder com 422);
OpenAlex e Crossref usam o e-mail só para o "polite pool". O e-mail nunca é fixado
no código: vem de `ARTIGOS_EMAIL` ou de `--email`, e sem ele o degrau Unpaywall é
pulado, com aviso.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

VERSAO = "1.0"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+", re.IGNORECASE)
ARXIV_RE = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf)/|arxiv:|10\.48550/arxiv\.)(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)
CROSSREF = "https://api.crossref.org/works/"
OPENALEX = "https://api.openalex.org/works"
UNPAYWALL = "https://api.unpaywall.org/v2/"
S2 = "https://api.semanticscholar.org/graph/v1/paper/"
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
ARXIV_API = "https://export.arxiv.org/api/query"
ATOM = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
HOSTS_COM_EMAIL = frozenset({"api.crossref.org", "api.openalex.org", "api.unpaywall.org"})
TENTATIVAS = 3
ESPERA = 2.0
TIMEOUT = 60


@dataclass(frozen=True)
class Registro:
    """Metadados bibliográficos normalizados, sempre com a API de origem em `fonte`."""
    doi: str
    titulo: str = ""
    autores: tuple[str, ...] = ()
    periodico: str = ""
    ano: int | None = None
    volume: str = ""
    numero: str = ""
    paginas: str = ""
    tipo: str = ""
    editora: str = ""
    is_oa: bool | None = None
    oa_status: str = ""
    licenca: str = ""
    citado_por: int | None = None
    arxiv_id: str = ""
    pmid: str = ""
    pmcid: str = ""
    fonte: str = ""
    correspondente: str = ""
    pais_correspondente: str = ""
    correspondente_marcado: bool = False


@dataclass(frozen=True)
class Candidato:
    """Um endereço onde o texto integral pode estar, e o que se sabe sobre ele."""
    url: str
    degrau: str
    versao: str = ""
    licenca: str = ""
    hospedeiro: str = ""
    tipo: str = "pdf"


def extrair_doi(texto: str) -> str | None:
    """Acha um DOI dentro de qualquer texto (URL, citação, prosa) e o devolve em minúsculas."""
    m = DOI_RE.search(texto or "")
    if not m:
        return None
    return m.group(0).rstrip(".,;:)]}").lower()


def extrair_arxiv_id(texto: str) -> str:
    m = ARXIV_RE.search(texto or "")
    return m.group(1) if m else ""


def email_para(url: str, email: str | None) -> str | None:
    """O e-mail só acompanha pedidos a Crossref, OpenAlex e Unpaywall; para qualquer outro host, None."""
    if not email:
        return None
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    return email if host in HOSTS_COM_EMAIL else None


def user_agent(email: str | None) -> str:
    base = f"artigos-cientificos/{VERSAO} (skill do Claude Code)"
    return f"{base} mailto:{email}" if email else base


def http_get(url: str, *, email: str | None = None, aceitar: str = "*/*",
             timeout: int = TIMEOUT, tentativas: int = TENTATIVAS,
             espera: float = ESPERA, dormir=time.sleep):
    """Devolve (status, corpo, url_final, cabeçalhos). Não levanta em 4xx; repete em 429 e 5xx."""
    req = urllib.request.Request(
        url, headers={"User-Agent": user_agent(email_para(url, email)), "Accept": aceitar})
    ultimo = (0, b"", url, {})
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read(), resp.geturl(), dict(resp.headers)
        except urllib.error.HTTPError as erro:
            corpo = erro.read() if hasattr(erro, "read") else b""
            ultimo = (erro.code, corpo, url, dict(erro.headers or {}))
            if erro.code != 429 and erro.code < 500:
                return ultimo
        except (urllib.error.URLError, TimeoutError, OSError) as erro:
            ultimo = (0, str(erro).encode(), url, {})
        if i + 1 < tentativas:
            dormir(espera * (2 ** i))
    return ultimo


def http_json(url: str, **kw):
    """Devolve (status, objeto decodificado ou None)."""
    status, corpo, _, _ = http_get(url, aceitar="application/json", **kw)
    if not corpo:
        return status, None
    try:
        return status, json.loads(corpo.decode("utf-8"))
    except ValueError:
        return status, None


# ── Crossref ────────────────────────────────────────────────────────────────

def crossref_url(doi: str, email: str | None = None) -> str:
    consulta = f"?mailto={urllib.parse.quote(email)}" if email else ""
    return f"{CROSSREF}{urllib.parse.quote(doi, safe='/')}{consulta}"


def _ano_crossref(msg: dict) -> int | None:
    for chave in ("published-print", "published-online", "published", "issued", "created"):
        partes = (msg.get(chave) or {}).get("date-parts") or []
        if partes and partes[0] and partes[0][0]:
            return int(partes[0][0])
    return None


def normalizar_crossref(msg: dict) -> Registro:
    autores = tuple(
        " ".join(p for p in (a.get("given"), a.get("family")) if p)
        for a in msg.get("author") or [])
    licenca = ""
    for item in msg.get("license") or []:
        licenca = item.get("URL") or licenca
    numero = msg.get("issue") or (msg.get("journal-issue") or {}).get("issue") or ""
    return Registro(
        doi=(msg.get("DOI") or "").lower(),
        titulo=" ".join(msg.get("title") or []),
        autores=autores,
        periodico=" ".join(msg.get("container-title") or []),
        ano=_ano_crossref(msg),
        volume=str(msg.get("volume") or ""),
        numero=str(numero),
        paginas=str(msg.get("page") or msg.get("article-number") or ""),
        tipo=msg.get("type") or "",
        editora=msg.get("publisher") or "",
        licenca=licenca,
        citado_por=msg.get("is-referenced-by-count"),
        fonte="crossref",
    )


def candidatos_crossref(msg: dict) -> list[Candidato]:
    """Links de mineração de texto (TDM) declarados pela editora; quase sempre pagos."""
    return [
        Candidato(url=item["URL"], degrau="crossref-tdm", hospedeiro="publisher")
        for item in msg.get("link") or []
        if (item.get("content-type") or "").lower() == "application/pdf" and item.get("URL")
    ]


# ── OpenAlex ────────────────────────────────────────────────────────────────

CAMPOS_OPENALEX = ("id,doi,title,publication_year,cited_by_count,open_access,"
                   "best_oa_location,locations,primary_location,authorships,type,ids,biblio")


def openalex_url(doi: str, email: str | None = None) -> str:
    consulta = f"?mailto={urllib.parse.quote(email)}" if email else ""
    return f"{OPENALEX}/doi:{urllib.parse.quote(doi, safe='/')}{consulta}"


def openalex_busca_url(consulta: str, *, desde: int | None = None, n: int = 10,
                       email: str | None = None) -> str:
    params = {"search": consulta, "per-page": str(n), "select": CAMPOS_OPENALEX}
    if desde:
        params["filter"] = f"from_publication_date:{desde}-01-01"
    if email:
        params["mailto"] = email
    return f"{OPENALEX}?{urllib.parse.urlencode(params)}"


def _id_curto(valor: str | None, prefixo: str) -> str:
    return (valor or "").replace(prefixo, "").strip("/")


def normalizar_pmcid(valor: str | None) -> str:
    """O OpenAlex devolve o PMCID sem o prefixo; o Europe PMC e o PMC exigem `PMC` na frente."""
    limpo = (valor or "").strip().upper()
    if not limpo:
        return ""
    return limpo if limpo.startswith("PMC") else f"PMC{limpo}"


def _correspondente(authorships: list) -> tuple[str, str, bool]:
    """Nome e país do autor de correspondência que o OpenAlex marca (`is_corresponding`); sem a
    marca, o primeiro autor, e a flag diz que foi só um palpite a conferir na primeira página."""
    marcados = [a for a in authorships if a.get("is_corresponding")]
    escolhido = marcados[0] if marcados else (authorships[0] if authorships else {})
    nome = (escolhido.get("author") or {}).get("display_name") or ""
    paises = [p for p in (escolhido.get("countries") or []) if p] or [
        i.get("country_code") for i in escolhido.get("institutions") or [] if i.get("country_code")]
    return nome, (paises[0] if paises else ""), bool(marcados)


def normalizar_openalex(obj: dict) -> Registro:
    ids = obj.get("ids") or {}
    local = obj.get("primary_location") or {}
    oa = obj.get("open_access") or {}
    melhor = obj.get("best_oa_location") or {}
    biblio = obj.get("biblio") or {}
    paginas = "-".join(p for p in (biblio.get("first_page"), biblio.get("last_page")) if p)
    autores = tuple(
        (a.get("author") or {}).get("display_name") or "" for a in obj.get("authorships") or [])
    correspondente, pais, marcado = _correspondente(list(obj.get("authorships") or []))
    return Registro(
        doi=_id_curto(obj.get("doi"), "https://doi.org/").lower(),
        titulo=obj.get("title") or "",
        autores=autores,
        periodico=((local.get("source") or {}).get("display_name") or ""),
        ano=obj.get("publication_year"),
        volume=str(biblio.get("volume") or ""),
        numero=str(biblio.get("issue") or ""),
        paginas=paginas,
        tipo=obj.get("type") or "",
        is_oa=oa.get("is_oa"),
        oa_status=oa.get("oa_status") or "",
        licenca=melhor.get("license") or "",
        citado_por=obj.get("cited_by_count"),
        arxiv_id=extrair_arxiv_id(json.dumps(obj.get("locations") or [])),
        pmid=_id_curto(ids.get("pmid"), "https://pubmed.ncbi.nlm.nih.gov/"),
        pmcid=normalizar_pmcid(_id_curto(ids.get("pmcid"), "https://www.ncbi.nlm.nih.gov/pmc/articles/")),
        fonte="openalex",
        correspondente=correspondente,
        pais_correspondente=pais,
        correspondente_marcado=marcado,
    )


def candidatos_openalex(obj: dict) -> list[Candidato]:
    vistos: set[str] = set()
    saida: list[Candidato] = []
    locais = [obj.get("best_oa_location") or {}] + list(obj.get("locations") or [])
    for local in locais:
        if not local or local.get("is_oa") is False:
            continue
        url = local.get("pdf_url")
        if url and url not in vistos:
            vistos.add(url)
            saida.append(Candidato(
                url=url, degrau="openalex", versao=local.get("version") or "",
                licenca=local.get("license") or "",
                hospedeiro=((local.get("source") or {}).get("type") or "")))
    oa_url = (obj.get("open_access") or {}).get("oa_url")
    if oa_url and oa_url not in vistos:
        saida.append(Candidato(url=oa_url, degrau="openalex", tipo="landing"))
    return saida


def normalizar_openalex_lista(obj: dict) -> list[Registro]:
    return [normalizar_openalex(item) for item in obj.get("results") or []]


# ── Unpaywall ───────────────────────────────────────────────────────────────

def unpaywall_url(doi: str, email: str) -> str:
    return f"{UNPAYWALL}{urllib.parse.quote(doi, safe='/')}?email={urllib.parse.quote(email)}"


def candidatos_unpaywall(obj: dict) -> list[Candidato]:
    vistos: set[str] = set()
    saida: list[Candidato] = []
    locais = [obj.get("best_oa_location") or {}] + list(obj.get("oa_locations") or [])
    for local in locais:
        if not local:
            continue
        for chave, tipo in (("url_for_pdf", "pdf"), ("url_for_landing_page", "landing")):
            url = local.get(chave)
            if url and url not in vistos:
                vistos.add(url)
                saida.append(Candidato(
                    url=url, degrau="unpaywall", versao=local.get("version") or "",
                    licenca=local.get("license") or "",
                    hospedeiro=local.get("host_type") or "", tipo=tipo))
    return saida


# ── Semantic Scholar ────────────────────────────────────────────────────────

def s2_url(doi: str) -> str:
    return (f"{S2}DOI:{urllib.parse.quote(doi, safe='/')}"
            "?fields=title,openAccessPdf,externalIds,isOpenAccess")


def candidatos_s2(obj: dict) -> list[Candidato]:
    pdf = obj.get("openAccessPdf") or {}
    if not pdf.get("url"):
        return []
    return [Candidato(url=pdf["url"], degrau="semantic-scholar",
                      licenca=pdf.get("license") or "")]


def s2_arxiv_url(arxiv_id: str) -> str:
    """Metadados pelo identificador do arXiv, para quando Crossref e OpenAlex não têm o DOI DataCite."""
    return (f"{S2}arXiv:{urllib.parse.quote(arxiv_id)}"
            "?fields=title,authors,year,venue,journal,externalIds,openAccessPdf,citationCount")


def normalizar_s2(obj: dict) -> Registro:
    ext = obj.get("externalIds") or {}
    periodico = (obj.get("journal") or {}).get("name") or obj.get("venue") or ""
    return Registro(
        doi=(ext.get("DOI") or "").lower(),
        titulo=obj.get("title") or "",
        autores=tuple(a.get("name") or "" for a in obj.get("authors") or []),
        periodico=periodico,
        ano=obj.get("year"),
        citado_por=obj.get("citationCount"),
        arxiv_id=ext.get("ArXiv") or "",
        pmid=str(ext.get("PubMed") or ""),
        pmcid=normalizar_pmcid(ext.get("PubMedCentral")),
        fonte="semantic-scholar",
    )


def ids_s2(obj: dict) -> dict:
    ext = obj.get("externalIds") or {}
    return {"arxiv_id": ext.get("ArXiv") or "", "pmid": str(ext.get("PubMed") or ""),
            "pmcid": normalizar_pmcid(ext.get("PubMedCentral"))}


# ── Europe PMC ──────────────────────────────────────────────────────────────

def europepmc_busca_url(doi: str) -> str:
    consulta = urllib.parse.quote(f'DOI:"{doi}"')
    return f"{EUROPEPMC}/search?query={consulta}&format=json&resultType=lite&pageSize=5"


def pmcid_de_europepmc(obj: dict) -> str:
    for item in (obj.get("resultList") or {}).get("result") or []:
        if item.get("pmcid"):
            return normalizar_pmcid(item["pmcid"])
    return ""


def candidatos_europepmc(pmcid: str) -> list[Candidato]:
    if not pmcid:
        return []
    return [
        Candidato(url=f"https://europepmc.org/articles/{pmcid}?pdf=render",
                  degrau="europepmc", versao="publishedVersion", hospedeiro="repository"),
        Candidato(url=f"{EUROPEPMC}/{pmcid}/fullTextXML", degrau="europepmc",
                  versao="publishedVersion", hospedeiro="repository", tipo="xml"),
    ]


# ── arXiv ───────────────────────────────────────────────────────────────────

def arxiv_api_url(arxiv_id: str) -> str:
    return f"{ARXIV_API}?id_list={urllib.parse.quote(arxiv_id)}"


def normalizar_arxiv_atom(xml_bytes: bytes) -> Registro | None:
    """Do Atom do arXiv ao Registro. None quando não é Atom ou quando a única entrada se chama `Error`,
    que é como o arXiv responde a parâmetro malformado, com HTTP 200."""
    try:
        raiz = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None
    entrada = raiz.find("a:entry", ATOM)
    if entrada is None:
        return None
    titulo = " ".join((entrada.findtext("a:title", "", ATOM) or "").split())
    if not titulo or titulo == "Error":
        return None
    publicado = entrada.findtext("a:published", "", ATOM) or ""
    return Registro(
        doi=(entrada.findtext("x:doi", "", ATOM) or "").lower(),
        titulo=titulo,
        autores=tuple(" ".join((a.findtext("a:name", "", ATOM) or "").split())
                      for a in entrada.findall("a:author", ATOM)),
        periodico="arXiv",
        ano=int(publicado[:4]) if publicado[:4].isdigit() else None,
        tipo="preprint",
        is_oa=True,
        arxiv_id=extrair_arxiv_id(entrada.findtext("a:id", "", ATOM) or ""),
        fonte="arxiv",
    )


def candidatos_arxiv(arxiv_id: str) -> list[Candidato]:
    if not arxiv_id:
        return []
    return [Candidato(url=f"https://arxiv.org/pdf/{arxiv_id}", degrau="arxiv",
                      versao="submittedVersion", hospedeiro="repository")]
