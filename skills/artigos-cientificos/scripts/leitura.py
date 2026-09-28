"""Do arquivo ao texto: validação do PDF, `pdfinfo`, `pdftotext`, JATS para texto corrido e a capa do
ResearchGate, que se reconhece pelo texto da p. 1 e se tira com o `pypdf`."""
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


def jats_para_texto(xml_bytes: bytes) -> str:
    """Texto corrido do corpo de um artigo JATS; sem corpo, o documento inteiro."""
    try:
        raiz = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return xml_bytes.decode("utf-8", "replace")
    corpo = next((el for el in raiz.iter() if el.tag.split("}")[-1] == "body"), raiz)
    partes = _colher(corpo)
    if partes:
        return "\n\n".join(partes)
    return re.sub(r"\s+", " ", "".join(raiz.itertext())).strip()


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
