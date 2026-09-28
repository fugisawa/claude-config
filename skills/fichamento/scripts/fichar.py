#!/usr/bin/env python3
"""fichar.py — a infraestrutura comum dos quatro modos da skill `fichamento`.

O que ele faz, e só isso: acha o texto extraído de uma fonte a partir do identificador FT do
registro (ou de um DOI, ou de um caminho); dá o mapa de páginas e de seções; devolve janelas do
texto por página, por termo ou por seção, para que o texto integral fique no disco e só a janela
entre no contexto; calcula a página impressa a partir do form feed, do intervalo do registro e das
páginas que a cópia traz antes do artigo (capa da editora, folha de rosto do repositório), ou pela
numeração impressa na própria cópia, quando o registro cita por ela, como na publicação antecipada e na
reimpressão; diz "sem paginação" quando o texto não tem página, como o que vem de XML, de HTML ou de
OCR sem form feed; grava um bloco datado no fim da seção "## Do modelo" da nota de leitura, sem tocar
em mais nada; e valida um bloco contra o contrato da skill antes de gravá-lo.

Não usa rede. A busca tolerante por termo vem do `texto.py` da skill `artigos-cientificos`,
importado por caminho relativo dentro de ~/.claude/skills, nunca copiado.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

_AQUI = Path(__file__).resolve()
_ARTIGOS = _AQUI.parents[2] / "artigos-cientificos" / "scripts"
if _ARTIGOS.exists() and str(_ARTIGOS) not in sys.path:
    sys.path.insert(0, str(_ARTIGOS))
try:
    import texto as _texto  # type: ignore
except Exception:  # pragma: no cover - sem a artigos-cientificos, a busca é literal
    _texto = None

MARCA_MODELO = "## Do modelo"
MARCA_AUTOR = "## Do autor"
MODOS = ("explorar", "responder", "verificar", "sintetizar")
ROTULOS_RESPONDER = ("sustenta", "refuta", "misto", "insuficiente", "não consta")
VEREDITOS = ("sustentada", "sustentada com ressalva", "indeterminada", "enfraquecida", "refutada")
NIVEIS = ("E", "S", "I", "G")
FF = "\f"


# ---------------------------------------------------------------- localizar

def raiz_do_projeto(raiz: Path | None = None) -> Path:
    if raiz:
        return Path(raiz).resolve()
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("fora de um repositório git: passe --raiz")
    return Path(r.stdout.strip())


@dataclass(frozen=True)
class Fonte:
    ft: str
    doi: str
    referencia: str
    paginas: tuple[int, int] | None   # intervalo impresso do periódico, se o registro o traz
    versao_copia: str
    txt: Path | None
    procedencia: Path | None
    deslocamento: int = 0             # páginas da cópia antes da primeira impressa: capa da editora, folha de rosto
    aviso: str = ""                   # o texto declarado no recibo falta aqui, ou o deslocamento está em dúvida
    sem_paginas: str = ""             # por que o texto não diz a página de cada linha: cópia em XML ou HTML, texto sem form feed
    paginas_da_copia: tuple[int, int] | None = None   # a numeração impressa na própria cópia, quando o registro cita por ela


def _secao_ft(registro: str, ft: str) -> str | None:
    m = re.search(r"(?ms)^### " + re.escape(ft) + r" — .*?(?=^### FT-|^## |\Z)", registro)
    return m.group(0) if m else None


def _campo(bloco: str, nome: str) -> str:
    m = re.search(r"^- \*\*" + re.escape(nome) + r":\*\* (.*)$", bloco, re.M)
    return m.group(1).strip() if m else ""


def _doi_de(referencia: str) -> str:
    m = re.search(r"DOI (10\.\S+?)(?=[ ;)]|$)", referencia)
    return m.group(1).lower() if m else ""


def _paginas_de(referencia: str) -> tuple[int, int] | None:
    m = re.search(r"\b(\d{1,5})[-–](\d{1,5})\.? DOI", referencia)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return (a, b) if b >= a else None


def _ler_recibo(procedencia: str | Path) -> dict:
    return json.loads(Path(procedencia).read_text(encoding="utf-8"))


def _procedencias(copias: Path) -> dict[str, Path]:
    por_doi = {}
    for p in glob.glob(str(copias / "*.procedencia.json")):
        try:
            d = _ler_recibo(p)
        except Exception:
            continue
        if d.get("doi"):
            por_doi[d["doi"].lower()] = Path(p)
    return por_doi


def _no_disco(caminho: str, procedencia: Path, raiz: Path) -> Path | None:
    """Onde está, nesta máquina, o arquivo que o recibo nomeia. O recibo grava o caminho como o comando
    o recebeu: só o nome, relativo à pasta do recibo; relativo à raiz do projeto ("fontes/copias/x.pdf");
    ou absoluto, às vezes com a pasta pessoal da outra máquina. Quando nenhuma dessas leituras existe
    aqui, vale o mesmo nome na pasta do recibo, onde a artigos-cientificos grava a cópia por padrão."""
    if not caminho:
        return None
    c = Path(caminho)
    cands = [c] if c.is_absolute() else [procedencia.parent / c, raiz / c]
    return next((x for x in cands + [procedencia.parent / c.name] if x.exists()), None)


def _txt_de(procedencia: Path, raiz: Path) -> tuple[Path | None, str]:
    """O texto que o recibo declara, e o aviso quando ele não está nesta máquina. Nesse caso não se
    lê outro no lugar dele, porque o texto com o nome do DOI pode ser outra versão, como a
    pré-publicação de Steyvers e col. (2025) ao lado da versão publicada. O recibo sem o campo
    'texto' fica com os candidatos de antes: o arquivo com .txt e o texto com o nome do recibo."""
    d = _ler_recibo(procedencia)
    declarado = d.get("texto") or ""
    if declarado:
        achado = _no_disco(declarado, procedencia, raiz)
        if achado:
            return achado, ""
        return None, (f"o recibo {procedencia.name} declara o texto {Path(declarado).name}, que não está nesta máquina: "
                      "traga a cópia da outra máquina. Nenhum outro texto o substitui, nem o de uma nova abertura da "
                      "fonte, porque pode ser outra versão dela")
    arq = d.get("arquivo") or ""
    if not arq:
        return None, ""
    do_pdf = _no_disco(str(Path(arq).with_suffix(".txt")), procedencia, raiz)
    do_recibo = procedencia.with_name(procedencia.name.replace(".procedencia.json", ".txt"))
    return do_pdf or (do_recibo if do_recibo.exists() else None), ""


def localizar(ft: str, raiz: Path) -> Fonte:
    registro = (raiz / "fontes" / "registro.md").read_text(encoding="utf-8")
    bloco = _secao_ft(registro, ft)
    if not bloco:
        raise SystemExit(f"{ft} não está no registro")
    ref = _campo(bloco, "Referência"); doi = _doi_de(ref)
    proc = _procedencias(raiz / "fontes" / "copias").get(doi)
    txt, falta = _txt_de(proc, raiz) if proc else (None, "")
    pags = _paginas_de(ref); versao = _campo(bloco, "Versão da cópia")
    sem = _sem_paginas(proc, pags, txt); da_copia = None
    if _cita_a_copia(versao) and txt and not sem:
        da_copia, deslocamento, aviso = _numeracao_da_copia(versao, txt)
    else:
        deslocamento, aviso = _deslocamento(versao, pags, txt)   # sem texto não há aviso de deslocamento
    return Fonte(ft=ft, doi=doi, referencia=ref, paginas=pags, versao_copia=versao, txt=txt, procedencia=proc,
                 deslocamento=deslocamento, aviso=falta or aviso, sem_paginas=sem, paginas_da_copia=da_copia)


# ---------------------------------------------------------------- páginas e mapa

def texto_corrido(fonte: Fonte) -> Path:
    """A extração sem `-layout`, para artigo em duas colunas que o leiaute intercala linha a linha.
    Fica ao lado da cópia, com o sufixo .corrido.txt, e se cria uma vez a partir do PDF da procedência."""
    if not fonte.procedencia:
        raise SystemExit("sem procedência: não há PDF de onde reextrair")
    arq = _ler_recibo(fonte.procedencia).get("arquivo") or ""
    pdf = _no_disco(arq, fonte.procedencia, fonte.procedencia.resolve().parents[2])
    if not pdf or pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"a cópia não é PDF ou não está nesta máquina: {arq}")
    alvo = pdf.with_suffix(".corrido.txt")
    if not alvo.exists():
        r = subprocess.run(["pdftotext", str(pdf), str(alvo)], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("pdftotext falhou: " + r.stderr.strip())
    return alvo


def paginas(txt: str) -> list[str]:
    """O texto dividido por form feed; o índice 0 é a primeira página da cópia."""
    return txt.split(FF)


def total_de_paginas(txt: str) -> int:
    """Quantas páginas o PDF tem. O pdftotext fecha toda página com form feed, até a última, e o form
    feed da última não abre outra: a parte vazia que sobra depois dele não é página."""
    return len(paginas(txt)) - int(txt.endswith(FF))


_NUMERO_SOLTO = re.compile(r"(?<!\S)\d{1,5}(?!\S)")
_DECLARACAO_PDF = re.compile(r"página (\d+) do PDF é a página (\d+)")   # como a Versão da cópia declara onde a numeração começa


_CITA_A_COPIA = re.compile(r"(?:páginas citadas(?: abaixo)? são as|localizações(?: abaixo)? citam a (?:página|paginação)"
                           r"(?: \d+[-–]\d+)?) da (?:cópia|reimpressão)\b", re.I)
_PROVA_OU_MANUSCRITO = ("prova", "manuscrito", "pré")   # como começa a Versão da cópia da prova, do manuscrito e da pré-publicação


def _cita_a_copia(versao: str) -> bool:
    """A Versão da cópia diz que as páginas citadas são as impressas na própria cópia, e não as do periódico,
    como na publicação antecipada e na reimpressão: 'as páginas citadas abaixo são as da cópia', 'as
    localizações citam a página da reimpressão'. A prova, o manuscrito e a pré-publicação ficam de fora
    mesmo quando o campo diz o mesmo, como o de Tricot e Sweller (2014): o rótulo deles continua sendo a
    posição no PDF, como se apresentou ao autor na decisão de 28/09/2026."""
    return bool(_CITA_A_COPIA.search(versao)) and not versao.lower().startswith(_PROVA_OU_MANUSCRITO)


def _sem_paginacao(versao: str) -> bool:
    """A versão lida não tem a paginação do periódico: prova, manuscrito, pré-publicação, e a cópia
    que o registro cita pela numeração impressa nela."""
    return versao.lower().startswith(_PROVA_OU_MANUSCRITO) or _cita_a_copia(versao)


def _sem_paginas(procedencia: Path | None, intervalo: tuple[int, int] | None, txt: Path | None) -> str:
    """Por que o texto não diz em que página está cada linha; vazio quando diz. O XML JATS do PubMed
    Central e do Europe PMC e a página HTML não têm página: o texto inteiro é uma só. O pdftotext
    fecha toda página com form feed, até a última, e o texto sem nenhum também é uma página só, que
    é a do artigo apenas quando o intervalo do registro tem uma."""
    formato = (_ler_recibo(procedencia).get("formato") or "").lower() if procedencia else ""
    if formato in ("xml", "html"):
        return f"o recibo declara a cópia em {formato.upper()}, que não tem página"
    if not txt or (intervalo and intervalo[0] == intervalo[1]) or FF in txt.read_text(encoding="utf-8", errors="replace"):
        return ""
    if intervalo:
        return f"o texto não tem form feed, e o intervalo {intervalo[0]}–{intervalo[1]} do registro tem mais de uma página"
    return "o texto não tem form feed, e o script não acha o intervalo de páginas na referência do registro"


def _deslocamento(versao: str, intervalo: tuple[int, int] | None, txt: Path | None) -> tuple[int, str]:
    """Quantas páginas a cópia traz antes da primeira impressa, e o aviso se houver. Vale o que o
    registro declara, porque é pela regra dele que as AF citam; senão, o que os cabeçalhos da cópia
    mostram; senão, zero, que é supor que a cópia começa na primeira página do artigo."""
    if not intervalo or _sem_paginacao(versao):
        return 0, ""
    p0, p1 = intervalo
    pags = paginas(txt.read_text(encoding="utf-8", errors="replace")) if txt else []
    declarado = _deslocamento_declarado(versao, p0)
    achado = _deslocamento_achado(intervalo, pags)
    if declarado is not None:
        if achado is not None and achado != declarado:
            return declarado, (f"a Versão da cópia do registro põe a p. {p0} na página {declarado + 1} do PDF, e os "
                               f"cabeçalhos da cópia a põem na página {achado + 1}; vale o registro, porque as afirmações dele "
                               "citam as páginas por essa correspondência")
        return declarado, ""
    if achado is not None:
        return achado, ""
    com_texto = sum(1 for p in pags if p.strip())
    if com_texto > p1 - p0 + 1:
        return 0, (f"a cópia tem {com_texto} páginas com texto e o intervalo {p0}–{p1} do registro tem {p1 - p0 + 1}, e nem os "
                   f"cabeçalhos nem a Versão da cópia dizem onde o artigo começa; supõe-se que na primeira página do PDF. "
                   f"Se houver capa antes dele, declare na Versão da cópia \"a página N do PDF é a página {p0}\"")
    return 0, ""


def _deslocamento_declarado(versao: str, p0: int) -> int | None:
    """O que o campo 'Versão da cópia' declara, nas formas em que o registro o escreve:
    'a página 2 do PDF é a página 268' e 'a página impressa é a do PDF mais 229' (ou 'menos 1')."""
    m = _DECLARACAO_PDF.search(versao)
    if m:
        return int(m.group(1)) - 1 - (int(m.group(2)) - p0)
    m = re.search(r"página impressa é a do PDF (mais|menos) (\d+)", versao)
    if not m:
        return None
    soma = int(m.group(2)) if m.group(1) == "mais" else -int(m.group(2))
    return p0 - soma - 1


def _numeros_da_borda(pag: str) -> set[int]:
    """Os números soltos nas três primeiras e nas três últimas linhas da página, onde ficam o cabeçalho e o pé."""
    linhas = [l for l in pag.split("\n") if l.strip()]
    return {int(n) for l in linhas[:3] + linhas[-3:] for n in _NUMERO_SOLTO.findall(l)}


def _mais_votado(votos: Counter) -> int | None:
    """O mais votado, se tiver três votos ao menos e nenhum empate: um número solto no texto não basta,
    nem dois alinhados por acaso, e sem indício a resposta é None."""
    ordem = votos.most_common(2)
    if not ordem or ordem[0][1] < 3 or (len(ordem) > 1 and ordem[1][1] == ordem[0][1]):
        return None
    return ordem[0][0]


def _deslocamento_achado(intervalo: tuple[int, int], pags: list[str]) -> int | None:
    """O deslocamento que os cabeçalhos da cópia mostram. Cada número do intervalo que aparece solto
    no cabeçalho ou no pé da página i vota em i - (n - p0), e vence o mais votado."""
    p0, p1 = intervalo
    votos = Counter()
    for i, pag in enumerate(pags):
        votos.update({i - (n - p0) for n in _numeros_da_borda(pag) if p0 <= n <= p1})
    return _mais_votado(votos)


def _numeracao_da_copia(versao: str, txt: Path) -> tuple[tuple[int, int] | None, int, str]:
    """A numeração impressa na própria cópia, quando o registro cita por ela: o intervalo, as páginas do
    PDF antes da primeira impressa e o aviso. A primeira página impressa sai do que a Versão da cópia
    declara, 'a página 2 do PDF é a página 1'; senão, dos números que o cabeçalho e o pé imprimem; sem
    nenhum dos dois, o N do rótulo 'p. N da cópia' é a posição no PDF, e o aviso diz como declarar. A
    numeração vai até a última página com texto, porque há página cujo número não chega à camada de
    texto, como a p. 13 de Harrison e col. (2020)."""
    pags = paginas(txt.read_text(encoding="utf-8", errors="replace"))
    fim = max((i for i, p in enumerate(pags) if p.strip()), default=0)
    achada = _numeracao_achada(pags)
    m = _DECLARACAO_PDF.search(versao)
    if m:
        primeira, deslocamento = int(m.group(2)), int(m.group(1)) - 1
        aviso = ""
        if achada and achada[0] - achada[1] != primeira - deslocamento:   # número impresso menos índice, pelas duas fontes
            aviso = (f"a Versão da cópia do registro põe a p. {primeira} da cópia na página {deslocamento + 1} do PDF, e os números "
                     f"impressos no cabeçalho e no pé a põem na página {primeira - achada[0] + achada[1] + 1} do PDF; vale o registro, "
                     "porque as afirmações dele citam as páginas por essa correspondência")
    elif achada:
        (primeira, deslocamento), aviso = achada, ""
    else:
        return None, 0, ("a Versão da cópia do registro diz que as páginas citadas são as impressas na cópia, e nem ela nem os "
                         "números do cabeçalho e do pé dizem em que página do PDF a numeração impressa começa; supõe-se que na "
                         "primeira, e por isso o N do rótulo \"p. N da cópia\" é a posição da página no PDF. Se houver capa antes "
                         "do artigo, declare na Versão da cópia em que página do PDF está a primeira página impressa, como "
                         "\"a página 2 do PDF é a página 1\"")
    return (primeira, primeira + fim - deslocamento), deslocamento, aviso


def _numeracao_achada(pags: list[str]) -> tuple[int, int] | None:
    """A numeração que a cópia imprime no cabeçalho e no pé, sem intervalo do registro que a limite: cada
    número solto no cabeçalho ou no pé da página i vota em n - i, o número impresso menos o índice, e vence
    o mais votado. Devolve a primeira página impressa e o índice dela na cópia. A primeira página do artigo
    costuma sair sem número, e por isso a numeração que só aparece a partir da p. 2 começa na p. 1, se a
    cópia tem a página anterior."""
    votos, primeiras = Counter(), {}
    for i, pag in enumerate(pags):
        for n in _numeros_da_borda(pag) - {0}:
            votos[n - i] += 1; primeiras[n - i] = min(n, primeiras.get(n - i, n))
    c = _mais_votado(votos)
    if c is None:
        return None
    primeira = 1 if primeiras[c] == 2 and c <= 1 else primeiras[c]   # a p. 1 cai no índice 1 - c, que tem de existir
    return primeira, primeira - c


def pagina_impressa(indice: int, fonte: Fonte | None) -> str:
    """Página como o manuscrito a cita: a impressa, se o registro traz o intervalo e a página cai
    dentro do artigo; senão 'da cópia', que é também o rótulo da capa e do que vem depois do artigo.
    Quando o registro cita a numeração impressa na própria cópia, como a da publicação antecipada ou a
    da reimpressão, o rótulo é 'p. N da cópia' com esse número, e a página fora dela, como a capa, leva
    'p. N do PDF', que é a posição no arquivo.
    Quando o texto não diz a página de cada linha, o rótulo é 'sem paginação', e o bloco cita a seção."""
    if fonte and fonte.sem_paginas:
        return "sem paginação"
    if fonte and fonte.paginas_da_copia:
        a, b = fonte.paginas_da_copia
        p = a + indice - fonte.deslocamento
        return f"p. {p} da cópia" if a <= p <= b else f"p. {indice + 1} do PDF"
    if fonte and fonte.paginas and not _sem_paginacao(fonte.versao_copia):
        p = fonte.paginas[0] + indice - fonte.deslocamento
        if fonte.paginas[0] <= p <= fonte.paginas[1]:
            return f"p. {p}"
    return f"p. {indice + 1} da cópia"


_TITULO = re.compile(r"^\s*(?:[0-9]+(?:\.[0-9]+)*\.?\s+)?([A-ZÀ-Ú][A-Za-zÀ-ú' ,:\-]{2,70})\s*$")


def _cabecalhos(txt: str) -> list[tuple[int, int, str]]:
    """Cabeçalhos prováveis, com o índice da página na cópia: linha curta, sem ponto final, entre
    linhas em branco, com inicial maiúscula."""
    saida = []
    for i, pag in enumerate(paginas(txt)):
        linhas = pag.split("\n")
        for j, l in enumerate(linhas):
            s = l.strip()
            if not s or len(s) > 70 or s.endswith((".", ",", ";")):
                continue
            antes = linhas[j - 1].strip() if j > 0 else ""
            depois = linhas[j + 1].strip() if j + 1 < len(linhas) else ""
            if antes == "" and depois == "" and (_TITULO.match(s) or s.isupper()):
                saida.append((i, j + 1, s))
    return saida


def mapa(txt: str, fonte: Fonte | None = None) -> list[tuple[str, int, str]]:
    """Os cabeçalhos prováveis, com a página como o manuscrito a cita."""
    return [(pagina_impressa(i, fonte), linha, titulo) for i, linha, titulo in _cabecalhos(txt)]


def indice_de_pagina(pagina: int, fonte: Fonte | None, total: int) -> int:
    """Traduz o que o usuário pediu para o índice na cópia: página impressa se o registro dá o
    intervalo e o número cai nele, ou se o número cai na numeração impressa na cópia, quando o registro
    cita por ela; senão, índice a partir de 1. A cópia sem paginação não tem página que se peça: a única
    que ela tem é o texto inteiro."""
    if fonte and fonte.sem_paginas:
        raise SystemExit(f"sem paginação: {fonte.sem_paginas}; peça a janela por --termo ou --secao")
    if fonte and fonte.paginas_da_copia and fonte.paginas_da_copia[0] <= pagina <= fonte.paginas_da_copia[1]:
        return pagina - fonte.paginas_da_copia[0] + fonte.deslocamento
    if fonte and fonte.paginas and fonte.paginas[0] <= pagina <= fonte.paginas[1] and not _sem_paginacao(fonte.versao_copia):
        return pagina - fonte.paginas[0] + fonte.deslocamento
    return pagina - 1


def janela_pagina(txt: str, indice: int) -> str:
    n = total_de_paginas(txt)
    if indice < 0 or indice >= n:
        raise SystemExit(f"o PDF tem {n} páginas (posições 1 a {n}); pedido fora do intervalo. --pagina aceita a página "
                         "impressa, que é a da cópia quando o registro cita a numeração dela e a do periódico quando o "
                         "registro traz o intervalo, ou a posição no PDF.")
    return paginas(txt)[indice]


def janela_termo(txt: str, termos: list[str], contexto: int = 3, fonte: Fonte | None = None, limite: int = 8) -> str:
    """Linhas em volta de cada ocorrência, com a página impressa; usa a busca tolerante da artigos-cientificos."""
    contexto = max(1, contexto)   # com 0 a janela é só a linha do achado, que numa cópia em colunas não diz nada
    linhas, pag_de_linha = _linhas_com_pagina(txt)
    saida = []; vistos = set()

    def janela(i: int, rotulo: str) -> None:
        if i in vistos:
            return
        vistos.add(i)
        lo, hi = max(0, i - contexto), min(len(linhas), i + contexto + 1)
        saida.append(f"[{pagina_impressa(pag_de_linha[i], fonte)}, linha {i + 1}] {rotulo}\n" +
                     "\n".join(x.replace(FF, "") for x in linhas[lo:hi]))

    achados_por_termo = {t: False for t in termos}
    if _texto is not None:
        for a in _texto.procurar(txt, termos, contexto=contexto):
            achados_por_termo[a.expressao] = True
            if len(saida) < limite:
                janela(a.linha - 1, a.expressao)
    else:
        for i, l in enumerate(linhas):
            for t in termos:
                if t.lower() in l.lower():
                    achados_por_termo[t] = True
                    if len(saida) < limite:
                        janela(i, t)
    # segunda passada: o que a busca por linha não achou, procura-se no texto emendado,
    # sem a hifenização de fim de linha ("confi-\ndence") e com as quebras viradas em espaço
    faltam = [t for t, ok in achados_por_termo.items() if not ok]
    if faltam:
        flat, mapa_linha = _emendar(linhas)
        for t in faltam:
            t_plano = _sem_diacriticos(t)
            padrao = _texto._padrao(t_plano) if _texto is not None else re.compile(re.escape(t_plano), re.I)
            for m in padrao.finditer(flat):
                if len(saida) >= limite:
                    break
                janela(mapa_linha[m.start()], t + " (achado no texto emendado, sem hífen de fim de linha)")
    return "\n\n".join(saida) if saida else "não consta na cópia: nenhuma das expressões foi achada"


def _linhas_com_pagina(txt: str) -> tuple[list[str], list[int]]:
    """As linhas como o `texto.procurar` as numera (str.splitlines, em que o form feed também
    quebra linha), e a página de cada uma: a página avança depois da linha que o form feed fecha."""
    linhas, pags, p = [], [], 0
    for peca in txt.splitlines(keepends=True):
        linhas.append(peca.rstrip("\r\n\f\v\x1c\x1d\x1e\x85\u2028\u2029"))
        pags.append(p)
        if peca.endswith(FF):
            p += 1
    return linhas, pags


def _sem_diacriticos(s: str) -> str:
    """Tira acentos e também o acento solto que o pdftotext deixa antes da vogal ("K¨ohnken")."""
    import unicodedata
    s = re.sub(r"[\u00a8\u00b4\u0060\u005e\u02dc\u00b8\u02c6\u02d8\u02d9\u02da\u02dd](?=[A-Za-z])", "", s)
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _emendar(linhas: list[str]) -> tuple[str, list[int]]:
    """Texto corrido sem hifenização de fim de linha, com o mapa de cada caractere para a linha de origem."""
    partes = []; mapa = []
    for i, l in enumerate(linhas):
        s = _sem_diacriticos(l.replace(FF, "").rstrip())
        if s.endswith("-") and len(s) > 1 and s[-2].isalpha():
            s = s[:-1]; sep = ""
        else:
            sep = " "
        partes.append(s + sep); mapa.extend([i] * (len(s) + len(sep)))
    return "".join(partes), mapa


def janela_secao(txt: str, titulo: str, fonte: Fonte | None = None, max_linhas: int = 120) -> str:
    cab = _cabecalhos(txt)
    alvo = [c for c in cab if titulo.lower() in c[2].lower()]
    if not alvo:
        return f"seção não achada: {titulo}; cabeçalhos vistos: " + "; ".join(c[2] for c in cab[:30])
    indice, linha, nome = alvo[0]
    trecho = paginas(txt)[indice].split("\n")[linha - 1: linha - 1 + max_linhas]
    return f"[{pagina_impressa(indice, fonte)}] {nome}\n" + "\n".join(trecho)


# ---------------------------------------------------------------- gravar e validar

def _marca(texto: str, marca: str) -> int:
    """Posição da marca como título de seção, no início de linha; -1 se não houver."""
    m = re.search(r"(?m)^" + re.escape(marca) + r"[ \t]*$", texto)
    return m.start() if m else -1


def carimbo(modo: str, quando: str | None = None, ferramenta: str = "Claude Code") -> str:
    d = quando or _dt.date.today().isoformat()
    return f"### {modo} — {d}"


def gravar(nota: Path, modo: str, bloco: str, quando: str | None = None, ferramenta: str = "Claude Code") -> str:
    """Acrescenta o bloco ao fim da seção '## Do modelo'; cria a seção antes de '## Do autor' se faltar."""
    if modo not in MODOS:
        raise SystemExit(f"modo inválido: {modo}")
    t = nota.read_text(encoding="utf-8")
    fim = _marca(t, MARCA_AUTOR)
    if fim < 0:
        raise SystemExit(f"a nota não tem a seção '{MARCA_AUTOR}': {nota}")
    if _marca(t, MARCA_MODELO) < 0:
        t = t[:fim] + MARCA_MODELO + "\n\n" + t[fim:]
    ini = _marca(t, MARCA_MODELO); fim = _marca(t, MARCA_AUTOR)
    secao = t[ini:fim].rstrip("\n")
    novo = secao + "\n\n" + carimbo(modo, quando, ferramenta) + "\n\n" + bloco.strip() + "\n\n_ferramenta: " + ferramenta + "; skill fichamento_\n\n"
    t = t[:ini] + novo + t[fim:]
    nota.write_text(t, encoding="utf-8")
    return carimbo(modo, quando, ferramenta)


_CITACAO = re.compile(r"[“\"][^”\"]{3,}[”\"]")
_PAGINA = re.compile(r"\(p\. \d+(?:[-–]\d+)?(?: da cópia)?\)|\bp\. \d+(?:[-–]\d+)?(?: da cópia)?\b"
                     r"|\((?:seção|subseção|cap\.|capítulo|§)[^)]{1,80}\)")   # versão sem paginação: a subseção, como o registro faz
_NUMERO = re.compile(r"(?<![A-Za-z\-])\d+(?:[.,]\d+)?%?")
_DOI = re.compile(r"\b10\.\d{4,9}/[^\s|\]>\"]+")


def validar(bloco: str, modo: str) -> list[str]:
    """Devolve a lista de violações do contrato; vazia quer dizer que o bloco pode ser gravado."""
    erros = []
    if modo not in MODOS:
        return [f"modo inválido: {modo}"]
    linhas = [l for l in bloco.split("\n") if l.strip()]
    if any(l.startswith("Fonte:") for l in linhas):
        erros.append("o bloco traz um parágrafo 'Fonte:'; a procedência fica no registro")
    ISENTAS = ("**Pergunta.**", "**Alegação", "**Versão mais forte.**", "**Alvo.**", "**Recorte.**", "- **Afirmação:**", "- **Razão:**", "- **Origem:**")
    for l in linhas:
        if l.strip().startswith(ISENTAS):
            continue
        citas = [c for c in _CITACAO.findall(l) if len(c.split()) >= 4]   # aspas em palavra solta não são citação
        if citas and not _PAGINA.search(l):
            erros.append(f"trecho citado sem página: {l[:80]}")
    if "não consta" not in bloco.lower() and not any(_PAGINA.search(l) for l in linhas):
        erros.append("nenhum número ou trecho ancorado em página, e nenhum 'não consta': o bloco parece feito do resumo")
    if modo == "responder":
        if not re.search(r"\*\*Rótulo:\*\* (" + "|".join(map(re.escape, ROTULOS_RESPONDER)) + r")", bloco):
            erros.append("modo responder sem linha '**Rótulo:** ' com um dos valores: " + ", ".join(ROTULOS_RESPONDER))
    if modo == "verificar":
        if not re.search(r"\*\*Veredito:\*\* (" + "|".join(map(re.escape, VEREDITOS)) + r")", bloco):
            erros.append("modo verificar sem '**Veredito:** ' em um dos cinco graus: " + ", ".join(VEREDITOS))
        if not re.search(r"\*\*Nível da checagem:\*\* [ESIG]\b", bloco):
            erros.append("modo verificar sem '**Nível da checagem:** E|S|I|G'")
        if "**O que mudaria esta avaliação:**" not in bloco:
            erros.append("modo verificar sem '**O que mudaria esta avaliação:**'")
    if modo == "explorar":
        if not re.search(r"\*\*Tipo de fonte:\*\* ", bloco):
            erros.append("modo explorar sem '**Tipo de fonte:** '")
        if not re.search(r"\((apoia|contraria|menciona)\)", bloco):
            erros.append("modo explorar sem conexão rotulada (apoia|contraria|menciona)")
    m = re.search(r"(?ms)^\*\*Perguntas ao autor:\*\*\s*\n((?:\s*(?:\d+\.|-) .+\n?)+)", bloco)
    n_perg = len(re.findall(r"^\s*(?:\d+\.|-) ", m.group(1), re.M)) if m else 0
    if not (2 <= n_perg <= 3):
        erros.append("o bloco não fecha com '**Perguntas ao autor:**' seguido de duas ou três perguntas")
    return erros


def _limpar_doi(d: str) -> str:
    d = d.rstrip(".,;:")
    while d.endswith(")") and d.count(")") > d.count("("):   # o ')' de fecho da frase, não o do DOI
        d = d[:-1]
    return d


def dois_mencionados(bloco: str) -> list[str]:
    return sorted(set(_limpar_doi(d) for d in _DOI.findall(bloco)))


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", type=Path, help="raiz do projeto (padrão: git rev-parse --show-toplevel)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("localizar", help="FT -> DOI, cópia, texto, intervalo de páginas"); s.add_argument("ft")
    s = sub.add_parser("mapa", help="páginas e cabeçalhos prováveis"); s.add_argument("ft")
    s.add_argument("--corrido", action="store_true", help="usa a extração sem -layout (artigo em duas colunas)")
    s = sub.add_parser("janela", help="uma página, ou as linhas em volta de termos, ou uma seção"); s.add_argument("ft")
    s.add_argument("--corrido", action="store_true", help="usa a extração sem -layout (artigo em duas colunas)")
    s.add_argument("--pagina", type=int, help="página impressa (a da cópia quando o registro cita a numeração dela, senão a do periódico) ou posição no PDF, a partir de 1")
    s.add_argument("--termo", action="append", help="expressão a procurar (repetível)")
    s.add_argument("--secao", help="parte do título da seção")
    s.add_argument("--contexto", type=int, default=3)
    s = sub.add_parser("validar", help="confere um bloco contra o contrato do modo"); s.add_argument("modo", choices=MODOS); s.add_argument("bloco", type=Path)
    s = sub.add_parser("gravar", help="acrescenta o bloco validado à seção Do modelo da nota docs/leituras/<nome>.md"); s.add_argument("ft", metavar="nome", help="FT-… ou sintese-<recorte>"); s.add_argument("modo", choices=MODOS)
    s.add_argument("bloco", type=Path); s.add_argument("--data"); s.add_argument("--ferramenta", default="Claude Code"); s.add_argument("--sem-validar", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "validar":
        erros = validar(a.bloco.read_text(encoding="utf-8"), a.modo)
        for e in erros:
            print("✗", e)
        dois = dois_mencionados(a.bloco.read_text(encoding="utf-8"))
        print("DOIs mencionados, a resolver com artigo.py resolver:", ", ".join(dois) if dois else "nenhum no bloco")
        print("ok: o bloco obedece ao contrato" if not erros else f"{len(erros)} violação(ões)")
        return 0 if not erros else 2

    raiz = raiz_do_projeto(a.raiz)
    if a.cmd == "gravar":
        nota = raiz / "docs" / "leituras" / f"{a.ft}.md"
        if not nota.exists():
            print(f"nota não existe: {nota}; rode docs/leituras/gerar_notas.py", file=sys.stderr); return 1
        bloco = a.bloco.read_text(encoding="utf-8")
        if not a.sem_validar:
            erros = validar(bloco, a.modo)
            if erros:
                for e in erros: print("✗", e)
                return 2
        print("gravado:", gravar(nota, a.modo, bloco, a.data, a.ferramenta), "em", nota.relative_to(raiz)); return 0

    f = localizar(a.ft, raiz)
    if f.aviso:
        print(f"aviso: {f.ft}: {f.aviso}", file=sys.stderr)
    if a.cmd == "localizar":
        print(json.dumps({"ft": f.ft, "doi": f.doi, "paginas_impressas": f.paginas, "deslocamento": f.deslocamento,
                          **({"sem_paginas": f.sem_paginas} if f.sem_paginas else {}),
                          **({"paginas_da_copia": f.paginas_da_copia} if f.paginas_da_copia else {}), "versao_copia": f.versao_copia,
                          "txt": str(f.txt.relative_to(raiz)) if f.txt else None,
                          "procedencia": str(f.procedencia.relative_to(raiz)) if f.procedencia else None}, ensure_ascii=False, indent=1))
        if not f.txt:
            if not f.aviso:   # sem texto, o aviso é o do texto declarado que falta aqui, e reabrir a fonte pode trazer outra versão
                print("sem cópia local: abra pela skill artigos-cientificos (artigo.py abrir/registrar) antes de fichar", file=sys.stderr)
            return 2
        return 0
    if not f.txt:
        if not f.aviso:
            print("sem cópia local: abra pela skill artigos-cientificos antes de fichar", file=sys.stderr)
        return 2
    origem = texto_corrido(f) if getattr(a, "corrido", False) else f.txt
    txt = origem.read_text(encoding="utf-8", errors="replace")
    if a.cmd == "mapa":
        print(f"texto: {origem.relative_to(raiz)}")
        n, d = total_de_paginas(txt), f.deslocamento
        if f.sem_paginas:
            print(f"sem paginação: {f.sem_paginas}; o bloco cita a seção, \"(seção …)\", e não uma página")
        elif f.paginas_da_copia:
            print(f"{n} páginas no PDF; o registro cita a numeração impressa na cópia, e não a do periódico: a "
                  f"{pagina_impressa(d, f)} é a {d + 1}ª delas" + (", e o que vem antes leva o rótulo 'do PDF'" if d > 0 else ""))
        elif d > 0 and not pagina_impressa(d, f).endswith("da cópia"):
            print(f"{n} páginas na cópia; a {pagina_impressa(d, f)} é a {d + 1}ª delas, e o que vem antes não é do artigo "
                  "(capa, folha de rosto) e leva o rótulo 'da cópia'")
        else:
            print(f"{n} páginas na cópia; {pagina_impressa(0, f)} é a primeira")
        for pag, linha, titulo in mapa(txt, f):
            print(f"{pag:>16}  L{linha:<5} {titulo}")
        return 0
    if a.cmd == "janela":
        if a.pagina:
            idx = indice_de_pagina(a.pagina, f, len(paginas(txt)))
            print(f"[{pagina_impressa(idx, f)}; posição {idx + 1} no PDF]\n" + janela_pagina(txt, idx))
        elif a.termo:
            print(janela_termo(txt, a.termo, a.contexto, f))
        elif a.secao:
            print(janela_secao(txt, a.secao, f))
        else:
            print("diga --pagina, --termo ou --secao", file=sys.stderr); return 1
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
