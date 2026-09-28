"""Do arquivo ao texto: validação do PDF, `pdfinfo`, `pdftotext` e JATS para texto corrido."""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPO_MAX_DO_PDFTOTEXT = 60   # segundos; um PDF de 381 páginas e 11 MB saiu do `-raw` em 0,4 s
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
