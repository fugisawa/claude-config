"""Do arquivo ao texto: validação do PDF, `pdfinfo`, `pdftotext`, JATS para texto corrido (título, resumo e
corpo, também dentro do `<pmc-articleset>` do efetch) e a capa do ResearchGate, que se reconhece pelo texto da
p. 1 e se tira com o `pypdf`."""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPO_MAX_DO_PDFTOTEXT = 60   # segundos; um PDF de 381 páginas e 11 MB saiu do `-raw` em 0,4 s
MARCAS_DA_CAPA_DO_RESEARCHGATE = ("see discussions, stats, and author profiles for this publication at",
                                  "researchgate.net/publication")
TAGS_DE_TEXTO = {"p", "title", "td", "th", "label", "caption", "abstract"}
BLOCOS = TAGS_DE_TEXTO | {"sec", "fig", "table-wrap", "table", "tr", "list", "list-item",
                          "disp-formula", "disp-quote", "boxed-text", "ref", "fn"}


def sha256_de(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def pdfinfo(caminho: Path) -> dict:
    """Páginas, produtor, criador e data de criação; dicionário vazio se o binário faltar."""
    if not shutil.which("pdfinfo"):
        return {}
    saida = subprocess.run(["pdfinfo", str(caminho)], capture_output=True, text=True)
    if saida.returncode != 0:
        return {}
    campos = {}
    for linha in saida.stdout.splitlines():
        chave, _, valor = linha.partition(":")
        campos[chave.strip().lower()] = valor.strip()
    paginas = campos.get("pages", "")
    return {
        "paginas": int(paginas) if paginas.isdigit() else None,
        "produtor": campos.get("producer", ""),
        "criador": campos.get("creator", ""),
        "criado_em": campos.get("creationdate", ""),
    }


def pdftotext(caminho: Path, destino: Path) -> Path:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext ausente: instale poppler-utils (apt install poppler-utils)")
    subprocess.run(["pdftotext", "-layout", str(caminho), str(destino)], check=True)
    return destino


def texto_em_ordem_de_leitura(pdf: Path) -> str | None:
    """O texto na ordem em que o PDF o desenha (`pdftotext -raw`), que, ao contrário do `-layout`, não
    intercala as colunas; só na memória, nada vai para o disco. None sem o `pdftotext`, se ele falhar
    ou se passar de TEMPO_MAX_DO_PDFTOTEXT."""
    if not shutil.which("pdftotext"):
        return None
    try:
        saida = subprocess.run(["pdftotext", "-raw", "-enc", "UTF-8", str(pdf), "-"], capture_output=True,
                               timeout=TEMPO_MAX_DO_PDFTOTEXT)
    except subprocess.TimeoutExpired:
        return None
    return saida.stdout.decode("utf-8", "replace") if saida.returncode == 0 else None


def texto_da_pagina(pdf: Path, pagina: int) -> str:
    """O texto de uma página do PDF, só na memória; vazio sem o `pdftotext`, se ele falhar ou se passar
    de TEMPO_MAX_DO_PDFTOTEXT."""
    if not shutil.which("pdftotext"):
        return ""
    try:
        saida = subprocess.run(["pdftotext", "-f", str(pagina), "-l", str(pagina), "-enc", "UTF-8", str(pdf), "-"],
                               capture_output=True, timeout=TEMPO_MAX_DO_PDFTOTEXT)
    except subprocess.TimeoutExpired:
        return ""
    return saida.stdout.decode("utf-8", "replace") if saida.returncode == 0 else ""


def eh_capa_do_researchgate(texto: str) -> bool:
    """A página que o ResearchGate põe antes do artigo traz as duas marcas, que a extração pode partir em
    linhas; o endereço sozinho não basta, porque o próprio artigo pode citá-lo."""
    corrido = " ".join(texto.split()).lower()
    return all(marca in corrido for marca in MARCAS_DA_CAPA_DO_RESEARCHGATE)


def sem_a_primeira_pagina(pdf: Path, destino: Path) -> str:
    """Grava em `destino` o PDF sem a p. 1, com os metadados do original, e devolve a ferramenta, para o
    diário. Só esta função precisa do `pypdf`, e por isso só ela o importa."""
    try:
        import pypdf
    except ImportError as erro:
        raise RuntimeError("pypdf ausente: instale-o (python3 -m pip install pypdf), ou mantenha a capa com "
                           "--manter-capa") from erro
    try:
        leitor = pypdf.PdfReader(str(pdf))
        total = len(leitor.pages)
        if total > 1:
            escritor = pypdf.PdfWriter()
            for pagina in leitor.pages[1:]:
                escritor.add_page(pagina)
            if leitor.metadata:
                escritor.add_metadata(leitor.metadata)
            with open(destino, "wb") as f:
                escritor.write(f)
    except Exception as erro:   # nem tudo o que o pypdf levanta é PyPdfError: o PDF com AES sem o cryptography dá DependencyError
        raise RuntimeError(f"o pypdf não tirou a capa de {pdf.name} ({type(erro).__name__}: {erro}); "
                           "mantenha-a com --manter-capa") from erro
    if total < 2:
        raise RuntimeError(f"{pdf.name} só tem a capa do ResearchGate, sem o artigo")
    return f"pypdf {pypdf.__version__}"


RECUSA_ILEGIVEL = "XML ilegível"
RECUSA_SEM_CORPO = "XML sem o corpo do artigo"
MARCAS_DE_MANUSCRITO = frozenset({"pmc-prop-manuscript", "is-manuscript"})   # PMC e Europe PMC, em <custom-meta>; o
# `is-manuscript` = yes não foi medido num manuscrito real do Europe PMC, só o `no` em três XMLs (02/10/2026)
SEM_IDENTIFICADOR = "sem identificador"


def _nome(el) -> str:
    return el.tag.split("}")[-1]


def _primeiro(el, nome: str):
    """O primeiro descendente com esse nome, em ordem de documento, ou None."""
    return next((filho for filho in el.iter() if _nome(filho) == nome), None)


def _filho(el, nome: str):
    """O primeiro filho direto com esse nome, ou None."""
    return next((filho for filho in el if _nome(filho) == nome), None)


def _ler(xml_bytes: bytes):
    """A raiz do XML, ou None quando ele não se lê, inclusive pela entidade que só o DTD externo definiria."""
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None


def _artigo_de(raiz):
    """O <article>: a própria raiz, ou o primeiro dentro dela, porque o efetch do NCBI devolve o artigo num
    <pmc-articleset>; None quando não há nenhum."""
    return raiz if _nome(raiz) == "article" else _primeiro(raiz, "article")


def _texto_inteiro(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _titulo_e_resumo(artigo) -> list[str]:
    """O <article-title> e os parágrafos de cada <abstract> da frente do artigo. O resto da frente (periódico,
    autores, datas, palavras-chave) fica de fora, e o <article-title> das referências, no fundo, também."""
    frente = _filho(artigo, "front")
    if frente is None:
        return []
    titulo = _primeiro(frente, "article-title")
    partes = [" ".join(_texto(titulo).split())] if titulo is not None else []
    for resumo in (el for el in frente.iter() if _nome(el) == "abstract"):
        partes += [parte for filho in resumo for parte in _colher(filho)]
    return [parte for parte in partes if parte]


def jats_para_texto(xml_bytes: bytes) -> str:
    """Texto corrido de um artigo JATS: o título, os parágrafos do resumo e o corpo, nesta ordem, um bloco por
    parágrafo. Sem nenhum dos três, o documento inteiro; sem XML legível, os bytes como texto."""
    raiz = _ler(xml_bytes)
    if raiz is None:
        return xml_bytes.decode("utf-8", "replace")
    artigo = _artigo_de(raiz)
    if artigo is None:
        return _texto_inteiro(raiz)
    corpo = _filho(artigo, "body")
    partes = _titulo_e_resumo(artigo) + (_colher(corpo) if corpo is not None else [])
    return "\n\n".join(partes) if partes else _texto_inteiro(artigo)


def recusa_do_jats(xml_bytes: bytes) -> str:
    """Vazio quando o XML é um artigo JATS com o corpo, que é o texto integral; senão, o motivo da recusa. O efetch
    do NCBI responde 200 só com a folha de rosto e o resumo quando a editora não libera o XML, e 200 com <error>
    quando o PMCID não existe; a página XHTML também tem <body>, mas não tem <article>, e o <body> de um
    <sub-article> (parecer, correção) não é o do artigo."""
    raiz = _ler(xml_bytes)
    if raiz is None:
        return RECUSA_ILEGIVEL
    artigo = _artigo_de(raiz)
    corpo = _filho(artigo, "body") if artigo is not None else None
    if corpo is None or not "".join(corpo.itertext()).strip():
        return RECUSA_SEM_CORPO
    return ""


def _declarado_manuscrito(frente) -> bool:
    """Se o PMC (`pmc-prop-manuscript`) ou o Europe PMC (`is-manuscript`) dizem, em <custom-meta>, que o XML é o
    manuscrito do autor."""
    for meta in (el for el in frente.iter() if _nome(el) == "custom-meta"):
        nome = (getattr(_filho(meta, "meta-name"), "text", "") or "").strip()
        valor = (getattr(_filho(meta, "meta-value"), "text", "") or "").strip().lower()
        if nome in MARCAS_DE_MANUSCRITO and valor == "yes":
            return True
    return False


def manuscrito_do_jats(xml_bytes: bytes) -> str:
    """O identificador do manuscrito do autor (NIHMS…) quando o PMC ou o Europe PMC declaram o XML como
    manuscrito, "sem identificador" quando declaram sem o trazer, e vazio quando não declaram. O
    <article-id pub-id-type="manuscript-id"> sozinho não serve de marca: ele fica no XML depois que a editora
    substitui o manuscrito pela versão publicada (medido em 02/10/2026 em dois XMLs, Sage Choice e Springer)."""
    raiz = _ler(xml_bytes)
    artigo = _artigo_de(raiz) if raiz is not None else None
    frente = _filho(artigo, "front") if artigo is not None else None
    if frente is None or not _declarado_manuscrito(frente):
        return ""
    for el in frente.iter():
        if _nome(el) == "article-id" and el.get("pub-id-type") == "manuscript-id":
            return (el.text or "").strip() or SEM_IDENTIFICADOR
    return SEM_IDENTIFICADOR


def _texto(el) -> str:
    """Texto do elemento com espaço só na fronteira de bloco: `<sub>` e `<italic>` não partem a palavra."""
    pedacos = [el.text or ""]
    for filho in el:
        separador = " " if filho.tag.split("}")[-1] in BLOCOS else ""
        pedacos += [separador, _texto(filho), separador, filho.tail or ""]
    return "".join(pedacos)


def _colher(el) -> list[str]:
    """Um bloco por elemento de texto mais externo; o que está aninhado nele já veio em `_texto`."""
    if el.tag.split("}")[-1] in TAGS_DE_TEXTO:
        texto = " ".join(_texto(el).split())
        return [texto] if texto else []
    return [parte for filho in el for parte in _colher(filho)]


def extrair_texto(arquivo: Path, formato: str) -> Path:
    """Grava `<arquivo>.txt` ao lado do original e devolve o caminho."""
    destino = arquivo.with_suffix(".txt")
    if formato == "pdf":
        return pdftotext(arquivo, destino)
    destino.write_text(jats_para_texto(arquivo.read_bytes()), encoding="utf-8")
    return destino
