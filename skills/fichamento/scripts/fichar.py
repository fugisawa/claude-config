#!/usr/bin/env python3
"""fichar.py — a infraestrutura comum dos quatro modos da skill `fichamento`.

O que ele faz, e só isso: acha o texto extraído de uma fonte a partir do identificador FT do
registro (ou de um DOI, ou de um caminho); dá o mapa de páginas e de seções; devolve janelas do
texto por página, por termo ou por seção, para que o texto integral fique no disco e só a janela
entre no contexto; calcula a página impressa a partir do form feed e do intervalo do registro;
grava um bloco datado no fim da seção "## Do modelo" da nota de leitura, sem tocar em mais nada;
e valida um bloco contra o contrato da skill antes de gravá-lo.

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


def _procedencias(copias: Path) -> dict[str, Path]:
    por_doi = {}
    for p in glob.glob(str(copias / "*.procedencia.json")):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if d.get("doi"):
            por_doi[d["doi"].lower()] = Path(p)
    return por_doi


def _txt_de(procedencia: Path) -> Path | None:
    d = json.load(open(procedencia, encoding="utf-8"))
    arq = d.get("arquivo") or ""
    if not arq:
        return None
    cands = [Path(arq).with_suffix(".txt"), procedencia.with_name(procedencia.name.replace(".procedencia.json", ".txt"))]
    for c in cands:
        if c.exists():
            return c
    return None


def localizar(ft: str, raiz: Path) -> Fonte:
    registro = (raiz / "fontes" / "registro.md").read_text(encoding="utf-8")
    bloco = _secao_ft(registro, ft)
    if not bloco:
        raise SystemExit(f"{ft} não está no registro")
    ref = _campo(bloco, "Referência"); doi = _doi_de(ref)
    proc = _procedencias(raiz / "fontes" / "copias").get(doi)
    txt = _txt_de(proc) if proc else None
    return Fonte(ft=ft, doi=doi, referencia=ref, paginas=_paginas_de(ref), versao_copia=_campo(bloco, "Versão da cópia"),
                 txt=txt, procedencia=proc)


# ---------------------------------------------------------------- páginas e mapa

def texto_corrido(fonte: Fonte) -> Path:
    """A extração sem `-layout`, para artigo em duas colunas que o leiaute intercala linha a linha.
    Fica ao lado da cópia, com o sufixo .corrido.txt, e se cria uma vez a partir do PDF da procedência."""
    if not fonte.procedencia:
        raise SystemExit("sem procedência: não há PDF de onde reextrair")
    d = json.load(open(fonte.procedencia, encoding="utf-8"))
    pdf = Path(d.get("arquivo") or "")
    if not pdf.exists() or pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"a cópia não é PDF ou não existe: {pdf}")
    alvo = pdf.with_suffix(".corrido.txt")
    if not alvo.exists():
        r = subprocess.run(["pdftotext", str(pdf), str(alvo)], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("pdftotext falhou: " + r.stderr.strip())
    return alvo


def paginas(txt: str) -> list[str]:
    """O texto dividido por form feed; o índice 0 é a primeira página da cópia."""
    return txt.split(FF)


def pagina_impressa(indice: int, fonte: Fonte | None) -> str:
    """Página como o manuscrito a cita: a impressa, se o registro traz o intervalo; senão 'da cópia'."""
    if fonte and fonte.paginas and not fonte.versao_copia.lower().startswith(("prova", "manuscrito", "pré")):
        return f"p. {fonte.paginas[0] + indice}"
    return f"p. {indice + 1} da cópia"


_TITULO = re.compile(r"^\s*(?:[0-9]+(?:\.[0-9]+)*\.?\s+)?([A-ZÀ-Ú][A-Za-zÀ-ú' ,:\-]{2,70})\s*$")


def mapa(txt: str, fonte: Fonte | None = None) -> list[tuple[str, int, str]]:
    """Cabeçalhos prováveis: linha curta, sem ponto final, entre linhas em branco, com inicial maiúscula."""
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
                saida.append((pagina_impressa(i, fonte), j + 1, s))
    return saida


def indice_de_pagina(pagina: int, fonte: Fonte | None, total: int) -> int:
    """Traduz o que o usuário pediu para o índice na cópia: página impressa se o registro dá o
    intervalo e o número cai nele; senão, índice a partir de 1."""
    if fonte and fonte.paginas and fonte.paginas[0] <= pagina <= fonte.paginas[1] and not fonte.versao_copia.lower().startswith(("prova", "manuscrito", "pré")):
        return pagina - fonte.paginas[0]
    return pagina - 1


def janela_pagina(txt: str, indice: int) -> str:
    pags = paginas(txt)
    if indice < 0 or indice >= len(pags):
        raise SystemExit(f"a cópia tem {len(pags)} páginas (índices 1 a {len(pags)}); pedido fora do intervalo. "
                         "--pagina aceita a página impressa quando o registro traz o intervalo, ou o índice na cópia.")
    return pags[indice]


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
    cab = mapa(txt, fonte)
    alvo = [c for c in cab if titulo.lower() in c[2].lower()]
    if not alvo:
        return f"seção não achada: {titulo}; cabeçalhos vistos: " + "; ".join(c[2] for c in cab[:30])
    pag, linha, _ = alvo[0]
    # posição absoluta
    pags = paginas(txt); idx = [i for i, c in enumerate(cab) if c is alvo[0]][0]
    ini_pag = int(re.search(r"\d+", pag).group(0))
    base = ini_pag - (fonte.paginas[0] if fonte and fonte.paginas and pag.startswith("p. ") and "da cópia" not in pag else 1)
    linhas = pags[base].split("\n")
    trecho = linhas[linha - 1: linha - 1 + max_linhas]
    return f"[{pag}] {alvo[0][2]}\n" + "\n".join(trecho)


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
    s.add_argument("--pagina", type=int, help="página impressa (quando o registro traz o intervalo) ou índice na cópia, a partir de 1")
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
    if a.cmd == "localizar":
        print(json.dumps({"ft": f.ft, "doi": f.doi, "paginas_impressas": f.paginas, "versao_copia": f.versao_copia,
                          "txt": str(f.txt.relative_to(raiz)) if f.txt else None,
                          "procedencia": str(f.procedencia.relative_to(raiz)) if f.procedencia else None}, ensure_ascii=False, indent=1))
        if not f.txt:
            print("sem cópia local: abra pela skill artigos-cientificos (artigo.py abrir/registrar) antes de fichar", file=sys.stderr); return 2
        return 0
    if not f.txt:
        print("sem cópia local: abra pela skill artigos-cientificos antes de fichar", file=sys.stderr); return 2
    origem = texto_corrido(f) if getattr(a, "corrido", False) else f.txt
    txt = origem.read_text(encoding="utf-8", errors="replace")
    if a.cmd == "mapa":
        print(f"texto: {origem.relative_to(raiz)}")
        print(f"{len(paginas(txt))} páginas na cópia; {pagina_impressa(0, f)} é a primeira")
        for pag, linha, titulo in mapa(txt, f):
            print(f"{pag:>16}  L{linha:<5} {titulo}")
        return 0
    if a.cmd == "janela":
        if a.pagina:
            idx = indice_de_pagina(a.pagina, f, len(paginas(txt)))
            print(f"[{pagina_impressa(idx, f)}; índice {idx + 1} na cópia]\n" + janela_pagina(txt, idx))
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
