"""copia_pelo_hash.py — acha, para o fichar.py, a cópia que nenhum recibo aponta, pelo SHA-256 que o parágrafo
"Fonte:" do registro guarda.

O recibo é o .procedencia.json que a skill artigos-cientificos grava ao lado da cópia. A fonte sem DOI não tem
recibo, porque o `artigo.py registrar` exige um DOI, e o recibo que só registra a tentativa de abrir a fonte não
aponta texto. O parágrafo "Fonte:" guarda os primeiros dígitos do SHA-256 do arquivo baixado, e é por eles que a
cópia se acha em fontes/copias/.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


def hash_do_fonte(bloco: str) -> str:
    """Os dígitos do SHA-256 que o parágrafo "Fonte:" da FT guarda, 'SHA-256 109232d4a2b4…', que são os do arquivo
    baixado; vazio quando ele não guarda nenhum. Só o parágrafo "Fonte:" conta, porque a Versão da cópia pode citar o
    hash de outra versão, como o da pré-publicação de Latimier, Peyre e Ramus (2021)."""
    m = re.search(r"(?m)^Fonte: .*?\bSHA-256 ([0-9a-f]{8,64})", bloco)
    return m.group(1) if m else ""


def pelo_hash(bloco: str, copias: Path) -> tuple[Path | None, Path | None, str, bool]:
    """A cópia cujo SHA-256 começa pelos dígitos do parágrafo "Fonte:", o texto dela, o aviso e se o texto foi gravado
    agora. O arquivo que não se lê, como o que o Syncthing ainda está gravando, não derruba a busca, e o aviso o cita
    quando ela falha. Quando nenhum arquivo daqui tem esse hash, o aviso manda trazer a cópia da outra máquina, como o
    do texto que o recibo declara e que falta."""
    prefixo = hash_do_fonte(bloco)
    if not prefixo:
        return None, None, "", False
    candidatos = (p for p in sorted(copias.glob("*")) if p.is_file() and not p.name.endswith(".procedencia.json"))
    ilegiveis = []
    for p in candidatos:
        try:
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError:
            ilegiveis.append(p.name); continue
        if digest.startswith(prefixo):
            return (p, *texto_da_copia(p))
    nao_lidos = f" (não se leram {', '.join(ilegiveis)}, e a cópia pode ser um deles)" if ilegiveis else ""
    return None, None, (f"o parágrafo \"Fonte:\" do registro guarda o SHA-256 {prefixo}…, e nenhum arquivo de "
                        f"fontes/copias/ tem esse hash nesta máquina{nao_lidos}: traga a cópia da outra máquina. Nenhum "
                        "outro arquivo a substitui, nem o de uma nova abertura da fonte, porque pode ser outra versão dela"), False


def texto_da_copia(copia: Path) -> tuple[Path | None, str, bool]:
    """O texto da cópia, o aviso quando não há texto e se o texto foi gravado agora. O texto é a própria cópia, quando o
    que se baixou já é texto, como a página copiada pelo navegador, ou o .txt de mesmo nome ao lado dela. Quando a cópia
    é um PDF que ainda não tem .txt, como o que o autor pôs na pasta à mão, o texto se extrai na primeira vez, com
    pdftotext -layout, como faz a artigos-cientificos."""
    if copia.suffix.lower() == ".txt":
        return copia, "", False
    texto = copia.with_suffix(".txt")
    if texto.exists():
        return texto, "", False
    falta = f"a cópia {copia.name} confere com o SHA-256 do registro, mas o texto dela, {texto.name}, não existe"
    if copia.suffix.lower() != ".pdf":
        return None, falta + ", e o script só extrai o texto de PDF: grave-o à mão com esse nome, ao lado da cópia", False
    try:
        r = subprocess.run(["pdftotext", "-layout", str(copia), str(texto)], capture_output=True, text=True)
    except FileNotFoundError:
        return None, falta + ", e o pdftotext não está instalado nesta máquina (pacote poppler-utils)", False
    if r.returncode != 0:
        texto.unlink(missing_ok=True)   # o .txt pela metade passaria por texto nas próximas vezes
        erro = r.stderr.strip().splitlines()
        return None, falta + ", e o pdftotext não o extraiu: " + (erro[-1] if erro else f"código {r.returncode}"), False
    return texto, "", True
