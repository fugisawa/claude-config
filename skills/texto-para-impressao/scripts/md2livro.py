#!/usr/bin/env python3
"""md2livro.py — Markdown de leitura corrida → PDF com tipografia de livro (LuaLaTeX).

    python3 md2livro.py texto.md --inspecionar        # inventário do texto, sem gerar nada
    python3 md2livro.py texto.md                      # gera texto.pdf ao lado do arquivo de origem
    python3 md2livro.py texto.md --autor "Fulano" --fonte charter --notas fim --so-frente
    python3 md2livro.py --help

O conteúdo não muda: o escape LaTeX é verificado por ida e volta em cada parágrafo, e as
únicas substituições são de glifo (aspas retas → curvas, ... → …, -- → –, --- → —), que o
relatório conta. Se o texto já vier com aspas curvas ou travessões, nada é tocado.
"""
from __future__ import annotations

import argparse
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# ----------------------------------------------------------------------------- fontes
# nome → (fontspec, corpo pt, entrelinha pt). Corpo e entrelinha são pontos de partida
# medidos para ~68 caracteres por linha numa mancha de 118 mm; o relatório mede de novo.
FONTES = {
    "garamond": (r"\setmainfont{EBGaramond}[Extension=.otf,UprightFont=*-Regular,ItalicFont=*-Italic,"
                 r"BoldFont=*-SemiBold,BoldItalicFont=*-SemiBoldItalic,Numbers=OldStyle,Ligatures=TeX]", 13.0, 17.0),
    "crimson": (r"\setmainfont{CrimsonPro}[Extension=.ttf,UprightFont=*-Regular,ItalicFont=*-Italic,"
                r"BoldFont=*-SemiBold,BoldItalicFont=*-SemiBoldItalic,Numbers=OldStyle,Ligatures=TeX]", 12.5, 16.5),
    "charter": (r"\setmainfont{XCharter}[Extension=.otf,UprightFont=*-Roman,ItalicFont=*-Italic,"
                r"BoldFont=*-Bold,BoldItalicFont=*-BoldItalic,Numbers=OldStyle,Ligatures=TeX]", 11.5, 15.5),
    "alegreya": (r"\setmainfont{Alegreya}[Extension=.otf,UprightFont=*-Regular,ItalicFont=*-Italic,"
                 r"BoldFont=*-Bold,BoldItalicFont=*-BoldItalic,Numbers=OldStyle,Ligatures=TeX]", 12.0, 16.0),
}
PAPEIS = {"a4": (210.0, 297.0, "a4paper"), "carta": (215.9, 279.4, "letterpaper")}
BABEL = {"pt": "brazil", "en": "english"}
TITULO_NOTAS = {"pt": "Notas", "en": "Notes"}

# ----------------------------------------------------------------------------- padrões
MD_DEF = re.compile(r"^\[\^([^\]\s]+)\]:\s?(.*)$")
MD_REF = re.compile(r"\[\^([^\]\s]+)\](?!:)")
PG_ITEM = re.compile(r"^\[(\d+)\]\s+(.*)$")
PG_REF = re.compile(r" ?\[(\d+)\]")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
THEMATIC = re.compile(r"^\s*(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$")
INDENTED = re.compile(r"^(?:    |\t)(.*)$")
UL = re.compile(r"^[-*+]\s+(.*)$")
OL = re.compile(r"^\d+[.)]\s+(.*)$")
QUOTE = re.compile(r"^>\s?(.*)$")
LINK = re.compile(r"\[([^\]]+)\]\((\S+?)\)")
# `$…$` só com não-espaço junto aos cifrões e sem dígito depois do segundo (regra do pandoc):
# "custa $5 e o outro é$10" não casa.
MATH = re.compile(r"\$(\S(?:[^$\n]*?\S)?)\$(?!\d)")
BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
ITAL = re.compile(r"(?<![\w*])\*(?=\S)([^*]+?)(?<=\S)\*(?![\w*])|(?<![\w_])_(?=\S)([^_]+?)(?<=\S)_(?![\w_])")
CODE = re.compile(r"`([^`]+)`")

ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
       "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
S = {k: chr(0xE000 + i) for i, k in enumerate(
    ["b0", "b1", "i0", "i1", "c0", "c1", "ref0", "ref1", "url0", "url1", "m0", "m1"])}


def is_notes_heading(line: str) -> bool:
    return line.strip().lstrip("#").strip().lower() in ("notes", "notas", "endnotes", "notas finais")


def starts_other_block(line: str) -> bool:
    return bool(HEADING.match(line) or QUOTE.match(line) or THEMATIC.match(line) or INDENTED.match(line))


@dataclass
class Doc:
    title: str | None = None
    subs: list = field(default_factory=list)      # (kind, texto): kind ∈ {autor, data}
    blocks: list = field(default_factory=list)    # ver parse_body
    notes: dict = field(default_factory=dict)     # chave → [('p', txt) | ('verse', [linhas])]
    note_style: str | None = None                 # 'pg' | 'md' | None
    notes_heading: str | None = None
    colofao: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    counts: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- leitura
def split_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).split("\n"):
        k, sep, v = line.partition(":")
        if sep:
            meta[k.strip().lower()] = v.strip().strip("\"'")
    return meta, text[m.end():]


def extract_md_notes(lines: list[str], doc: Doc) -> list[str]:
    """Remove as definições `[^id]: …` do corpo, deixando no lugar delas no máximo UMA linha
    em branco (duas virariam quebra de seção)."""
    body, cur, pending_break = [], None, False
    for line in lines:
        m = MD_DEF.match(line)
        if m:
            cur = [("p", m.group(2).strip())]
            doc.notes[m.group(1)] = cur
            pending_break = False
            if body and body[-1].strip():
                body.append("")
            continue
        if cur is not None:
            if not line.strip():
                pending_break = True
                continue
            if line.startswith(("  ", "\t")):
                txt = line.strip()
                cur.append(("p", txt)) if pending_break else cur.__setitem__(-1, ("p", cur[-1][1] + " " + txt))
                pending_break = False
                continue
            cur = None
            pending_break = False
        body.append(line)
    if doc.notes:
        doc.note_style = "md"
    return body


def extract_pg_notes(lines: list[str], doc: Doc) -> list[str]:
    start = None
    for i, line in enumerate(lines):
        if is_notes_heading(line):
            nxt = next((l for l in lines[i + 1:] if l.strip()), "")
            if PG_ITEM.match(nxt):
                start = i
                break
    if start is None:
        return lines
    doc.note_style, doc.notes_heading = "pg", lines[start].strip().lstrip("#").strip()
    cur, blanks, colofao = None, 0, False
    for line in lines[start + 1:]:
        if not line.strip():
            blanks += 1
            continue
        m = PG_ITEM.match(line)
        if m and not colofao:
            cur = [("p", m.group(2).strip())]
            doc.notes[m.group(1)] = cur
        elif colofao or (cur is not None and blanks >= 2):
            colofao = True
            if blanks >= 1 or not doc.colofao:
                doc.colofao.append(line.strip())
            else:
                doc.colofao[-1] += " " + line.strip()
        elif cur is not None:
            mi = INDENTED.match(line)
            if mi:
                if blanks or cur[-1][0] != "verse":
                    cur.append(("verse", []))
                cur[-1][1].append(mi.group(1).strip())
            elif blanks:
                cur.append(("p", line.strip()))
            else:
                cur[-1] = ("p", cur[-1][1] + " " + line.strip())
        blanks = 0
    return lines[:start]


def _parse_quote(lines, i):
    paras, cur = [], []
    while i < len(lines) and QUOTE.match(lines[i]):
        t = QUOTE.match(lines[i]).group(1).strip()
        if t:
            cur.append(t)
        elif cur:
            paras.append(" ".join(cur)); cur = []
        i += 1
    if cur:
        paras.append(" ".join(cur))
    return ("quote", paras), i


def _parse_verse(lines, i):
    verses = []
    while i < len(lines) and INDENTED.match(lines[i]):
        verses.append(INDENTED.match(lines[i]).group(1).rstrip())
        i += 1
    return ("verse", verses), i


def _parse_list(lines, i, kind, rx):
    """Item = linha com marcador; linha seguinte sem marcador e sem outro bloco é continuação
    (com ou sem recuo); a lista acaba em linha vazia ou em outro bloco."""
    items = []
    while i < len(lines) and lines[i].strip():
        mm = rx.match(lines[i])
        if mm:
            items.append(mm.group(1).strip())
        elif items and not starts_other_block(lines[i]) and not (UL.match(lines[i]) or OL.match(lines[i])):
            items[-1] += " " + lines[i].strip()
        else:
            break
        i += 1
    return (kind, items), i


def _parse_paragraph(lines, i):
    para = []
    while i < len(lines) and lines[i].strip() and not starts_other_block(lines[i]):
        para.append(lines[i].strip())
        i += 1
    return para, i


def looks_like_subtitle(para: list[str], txt: str) -> bool:
    return (len(para) == 1 and len(txt) <= 60 and len(txt.split()) <= 8 and "[" not in txt
            and not txt.endswith((".", "?", "!", ":", ";", "]", ")")))


def parse_body(lines: list[str], doc: Doc) -> None:
    i, blanks, subs_open = 0, 0, True

    def add(block):
        nonlocal blanks, subs_open
        last = doc.blocks[-1][0] if doc.blocks else None
        if (blanks >= 2 and doc.blocks and last not in ("h2", "h3", "break")
                and block[0] not in ("h2", "h3", "break")):
            doc.blocks.append(("break",))
        doc.blocks.append(block)
        blanks, subs_open = 0, False

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            blanks += 1; i += 1
            continue
        mh = HEADING.match(line)
        if mh:
            level, txt = len(mh.group(1)), mh.group(2)
            if level == 1 and doc.title is None and not doc.blocks:
                doc.title = txt
            else:
                add(("h2" if level <= 2 else "h3", txt))
            i += 1
        elif THEMATIC.match(line):
            if doc.blocks and doc.blocks[-1][0] != "break":
                doc.blocks.append(("break",))
            blanks, subs_open = 0, False
            i += 1
        elif QUOTE.match(line):
            block, i = _parse_quote(lines, i); add(block)
        elif INDENTED.match(line):
            block, i = _parse_verse(lines, i); add(block)
        elif UL.match(line):
            block, i = _parse_list(lines, i, "ul", UL); add(block)
        elif OL.match(line):
            block, i = _parse_list(lines, i, "ol", OL); add(block)
        else:
            para, i = _parse_paragraph(lines, i)
            txt = " ".join(para)
            if subs_open and doc.title is not None and len(doc.subs) < 3 and looks_like_subtitle(para, txt):
                kind = "data" if re.search(r"\d", txt) else "autor"
                doc.subs.append((kind, txt))
                if len(txt.split()) > 5:
                    doc.warnings.append(f"linha curta lida como {kind} do rosto, confira: {txt!r} (force com --titulo/--autor/--data)")
                blanks = 0
            else:
                add(("p", txt))
    doc.counts = {k: sum(1 for b in doc.blocks if b[0] == k) for k in ("p", "h2", "h3", "break", "quote", "verse", "ul", "ol")}


def guess_lang(text: str) -> tuple[str, int, int]:
    t = f" {re.sub(r'[^\w\s]', ' ', text.lower())} "
    en = sum(t.count(f" {w} ") for w in ("the", "and", "of", "to", "is", "that", "you", "it"))
    pt = sum(t.count(f" {w} ") for w in ("de", "que", "não", "uma", "para", "com", "os", "as", "um", "se"))
    return ("pt" if pt > en else "en"), pt, en


# ----------------------------------------------------------------------------- inline
class Ctx:
    def __init__(self, doc: Doc, notas: str, lang: str):
        self.doc, self.notas, self.lang = doc, notas, lang
        self.refs: list[str] = []
        self.urls: list[str] = []
        self.maths: list[str] = []
        self.order: list[str] = []          # chaves na ordem de primeira citação
        self.norm = {"aspas": 0, "apóstrofos": 0, "reticências": 0, "travessões": 0, "escapes": 0}

    # --- normalização tipográfica (só glifos; contada no relatório)
    def pre(self, s: str) -> str:
        c = self.norm
        n = s.count("---"); s = s.replace("---", "—"); c["travessões"] += n
        n = len(re.findall(r"(?<!-)--(?!-)", s)); s = re.sub(r"(?<!-)--(?!-)", "–", s); c["travessões"] += n
        n = s.count("..."); s = s.replace("...", "…"); c["reticências"] += n
        if s.count('"') % 2:
            self.doc.warnings.append(f'aspas duplas em número ímpar, deixadas retas: {s[:70]}…')
        else:
            s, n = re.subn(r'"([^"]*)"', "“\\1”", s); c["aspas"] += n
        s, n1 = re.subn(r"(^|[\s(\[“—–])'(?=\w)", "\\1‘", s)
        n2 = s.count("'"); s = s.replace("'", "’"); c["apóstrofos"] += n1 + n2
        return s

    def esc(self, s: str) -> str:
        t = "".join(ESC.get(ch, ch) for ch in s)
        self.norm["escapes"] += sum(s.count(ch) for ch in ESC)
        back = t
        for ch, e in sorted(ESC.items(), key=lambda kv: -len(kv[1])):
            back = back.replace(e, ch)
        assert back == s, ("escape não reversível", s)
        return t

    def note_latex(self, key: str) -> str:
        out = []
        for kind, val in self.doc.notes[key]:
            if kind == "p":
                out.append(self.inline(val))
            else:
                out.append(r"\hspace*{1em}" + r"\\ \hspace*{1em}".join(self.inline(v) for v in val))
        return r"\par\smallskip\noindent ".join(out)

    def note_number(self, key: str) -> str:
        return key if self.doc.note_style == "pg" else str(self.order.index(key) + 1)

    def ref(self, key: str) -> str | None:
        if key not in self.doc.notes:
            self.doc.warnings.append(f"nota [{key}] citada sem definição; deixada literal")
            return None
        if key in self.order:
            self.doc.warnings.append(f"nota [{key}] citada mais de uma vez; a segunda chamada só repete o número")
            num = self.note_number(key)
            latex = (r"\footnotemark[" + num + "]") if self.notas == "rodape" else (r"\textsuperscript{" + num + "}")
        else:
            self.order.append(key)
            if self.notas == "rodape":
                latex = r"\footnote{" + self.note_latex(key) + "}"
            else:
                latex = r"\textsuperscript{" + self.note_number(key) + "}"
        self.refs.append(latex)
        return f"{S['ref0']}{len(self.refs) - 1}{S['ref1']}"

    def inline(self, s: str) -> str:
        # 1. proteger o que não pode passar pelo escape
        def _ref(m):
            r = self.ref(m.group(1))
            return r if r is not None else m.group(0)
        s = MD_REF.sub(_ref, s)
        if self.doc.note_style == "pg":
            s = PG_REF.sub(lambda m: _ref(m) if m.group(1) in self.doc.notes else m.group(0), s)
        def _url(m):
            self.urls.append(m.group(2)); return f"{m.group(1)}{S['url0']}{len(self.urls) - 1}{S['url1']}"
        s = LINK.sub(_url, s)
        def _math(m):
            self.maths.append(m.group(0))
            self.doc.warnings.append(f"fórmula {m.group(0)!r} passa direta em modo matemático (fonte Computer Modern): confira no PDF")
            return f"{S['m0']}{len(self.maths) - 1}{S['m1']}"
        s = MATH.sub(_math, s)
        # 2. marcação inline → sentinelas
        s = CODE.sub(lambda m: S["c0"] + m.group(1) + S["c1"], s)
        s = BOLD.sub(lambda m: S["b0"] + m.group(1) + S["b1"], s)
        s = ITAL.sub(lambda m: S["i0"] + (m.group(1) or m.group(2)) + S["i1"], s)
        if "*" in s:
            self.doc.warnings.append(f"asterisco solto ficou literal: {s[:70]}…")
        # 3. glifos, 4. escape reversível, 5. sentinelas → LaTeX
        s = self.esc(self.pre(s))
        s = s.replace(S["b0"], r"\textbf{").replace(S["b1"], "}")
        s = s.replace(S["i0"], r"\emph{").replace(S["i1"], "}")
        s = s.replace(S["c0"], r"\texttt{").replace(S["c1"], "}")
        s = re.sub(f"{S['ref0']}(\\d+){S['ref1']}", lambda m: self.refs[int(m.group(1))], s)
        url_open, url_close = (r"\footnote{\url{", "}}") if self.notas == "rodape" else (r" (\url{", "})")
        s = re.sub(f"{S['url0']}(\\d+){S['url1']}", lambda m: url_open + self.urls[int(m.group(1))] + url_close, s)
        s = re.sub(f"{S['m0']}(\\d+){S['m1']}", lambda m: self.maths[int(m.group(1))], s)
        return s


# ----------------------------------------------------------------------------- LaTeX
PREAMBLE = r"""\documentclass[12pt,@PAPER@,@SIDES@]{article}
\usepackage[@PAPER@,@GEOSIDES@textwidth=@TW@mm,textheight=@TH@pt,@HMARGIN@,top=@TOP@mm,headsep=9mm,footskip=14mm,headheight=16pt,marginparwidth=0pt,marginparsep=0pt]{geometry}
\usepackage{fontspec}
@FONT@
\usepackage[@BABEL@]{babel}
\usepackage[protrusion=true,expansion=true,final]{microtype}
\usepackage{fancyhdr}
\IfFileExists{needspace.sty}{\usepackage{needspace}}{\newcommand{\needspace}[1]{\par\penalty-800}}
\makeatletter
\renewcommand\normalsize{\@setfontsize\normalsize{@CORPO@}{@LEAD@}}
\renewcommand\small{\@setfontsize\small{@SMALL@}{@SMALLLEAD@}}
\renewcommand\footnotesize{\@setfontsize\footnotesize{@FN@}{@FNLEAD@}}
\DeclareMathSizes{@CORPO@}{@CORPO@}{@SMALL@}{@FN@}
\renewcommand\@makefnmark{\hbox{\@textsuperscript{\normalfont\addfontfeature{Numbers=Lining}\@thefnmark}}}
\renewcommand\@makefntext[1]{\parindent 0pt\leftskip 1.6em\noindent\hskip-1.6em\makebox[1.6em][l]{\addfontfeature{Numbers=Lining}\@thefnmark.}#1}
\makeatother
\normalsize
\topskip=@CORPO@pt
\setlength{\parindent}{1.3em}
\setlength{\parskip}{0pt}
\raggedbottom
\widowpenalty=10000 \clubpenalty=10000 \displaywidowpenalty=10000
\emergencystretch=1.5em
\setlength{\skip\footins}{16pt plus 6pt minus 2pt}
\renewcommand\footnoterule{\kern-3pt\hrule width 0.3\columnwidth height 0.3pt\kern 2.7pt}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
@HEADERS@
\fancypagestyle{plain}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\fancyfoot[C]{\small\thepage}}
\newcommand{\sectionbreak}{\par\penalty-300
  \vspace{1\baselineskip plus 0.3\baselineskip minus 0.1\baselineskip}%
  {\centering *\hspace{1.2em}*\hspace{1.2em}*\par}\nopagebreak
  \vspace{1\baselineskip plus 0.3\baselineskip minus 0.1\baselineskip}\nopagebreak}
\newcommand{\secao}[1]{\par\needspace{5\baselineskip}\vspace{2\baselineskip}%
  {\centering\scshape\addfontfeature{LetterSpace=8}#1\par}\nopagebreak
  \vspace{1\baselineskip}\nopagebreak}
\newcommand{\subsecao}[1]{\par\needspace{4\baselineskip}\vspace{1\baselineskip}%
  {\noindent\itshape #1\par}\nopagebreak\vspace{0.4\baselineskip}\nopagebreak}
\renewcommand{\labelitemi}{--}
\usepackage[hidelinks]{hyperref}
\urlstyle{same}
\hypersetup{pdftitle={@PDFTITLE@},pdfauthor={@PDFAUTHOR@},pdflang={@LANG@}}
\begin{document}
"""


def _layout(a) -> dict:
    W, H, paper = PAPEIS[a.papel]
    corpo, lead = a.corpo, a.entrelinha
    top, bottom_min = 32.0, 38.0
    n_lines = int((H - top - bottom_min) / (lead * 0.3528))
    inner = 24.0 if a.margem_anotacao else 34.0
    return {
        "@PAPER@": paper, "@SIDES@": "oneside" if a.so_frente else "twoside",
        "@GEOSIDES@": "" if a.so_frente else "twoside,",
        "@TW@": f"{a.mancha:.1f}", "@TH@": str(round((n_lines - 1) * lead + corpo, 2)), "@TOP@": f"{top:.0f}",
        "@HMARGIN@": f"left={(W - a.mancha) / 2:.1f}mm" if a.so_frente else f"inner={inner:.1f}mm",
        "@FONT@": FONTES[a.fonte][0], "@BABEL@": BABEL[a.lang], "@LANG@": "pt-BR" if a.lang == "pt" else "en",
        "@CORPO@": str(corpo), "@LEAD@": str(lead),
        "@SMALL@": str(round(corpo - 1.5, 2)), "@SMALLLEAD@": str(round(lead - 2, 2)),
        "@FN@": str(round(corpo - 2.5, 2)), "@FNLEAD@": str(round(lead - 4, 2)),
    }


def _headers(a, ctx: Ctx, titulo: str, autor: str) -> str:
    sc = r"\small\scshape\addfontfeature{LetterSpace=10}"
    tit, aut = sc + ctx.esc(ctx.pre(titulo)), sc + ctx.esc(ctx.pre(autor or titulo))
    if a.sem_cabecalho:
        return r"\fancyfoot[C]{\small\thepage}"
    if a.so_frente:
        return r"\fancyhead[C]{" + tit + r"}\fancyhead[R]{\small\thepage}"
    return (r"\fancyhead[LE,RO]{\small\thepage}" + "\n" + r"\fancyhead[CE]{" + aut + "}\n"
            + r"\fancyhead[CO]{" + tit + "}")


def _title_block(doc: Doc, a, ctx: Ctx, titulo: str, autor: str) -> list[str]:
    big = round(a.corpo * 2.15, 1)
    out = [r"\thispagestyle{plain}" + "\n" + r"\begin{center}" + "\n" + r"\vspace*{8mm}" + "\n"
           + rf"{{\fontsize{{{big}}}{{{round(big * 1.15, 1)}}}\selectfont " + ctx.inline(titulo) + r"\par}"]
    if autor:
        out.append(r"\vspace{5mm}" + "\n" + r"{\large\scshape\addfontfeature{LetterSpace=10}" + ctx.inline(autor) + r"\par}")
    for kind, t in doc.subs:
        if kind == "data":
            out.append(r"\vspace{2mm}" + "\n" + r"{\itshape " + ctx.inline(t) + r"\par}")
        elif t != autor:
            out.append(r"\vspace{2mm}" + "\n" + r"{\large " + ctx.inline(t) + r"\par}")
    out.append(r"\end{center}" + "\n" + r"\vspace{9mm}")
    return out


def _blocks_latex(doc: Doc, ctx: Ctx) -> list[str]:
    out, noindent = [], True
    for b in doc.blocks:
        kind = b[0]
        if kind == "p":
            out.append((r"\noindent " if noindent else "") + ctx.inline(b[1]))
            noindent = False
            continue
        noindent = True
        if kind == "break":
            out.append(r"\sectionbreak")
        elif kind == "h2":
            out.append(r"\secao{" + ctx.inline(b[1]) + "}")
        elif kind == "h3":
            out.append(r"\subsecao{" + ctx.inline(b[1]) + "}")
        elif kind == "quote":
            out.append(r"\begin{quote}" + "\n" + "\n\n".join(ctx.inline(p) for p in b[1]) + "\n" + r"\end{quote}")
        elif kind == "verse":
            out.append(r"\begin{verse}" + "\n" + "\\\\\n".join(ctx.inline(v) for v in b[1]) + "\n" + r"\end{verse}")
        elif kind in ("ul", "ol"):
            env = "itemize" if kind == "ul" else "enumerate"
            out.append(rf"\begin{{{env}}}" + "\n" + "\n".join(r"\item " + ctx.inline(it) for it in b[1]) + "\n" + rf"\end{{{env}}}")
    return out


def _endnotes_latex(doc: Doc, a, ctx: Ctx) -> list[str]:
    head = doc.notes_heading or TITULO_NOTAS[a.lang]
    items = [r"\item[" + ctx.note_number(k) + ".] " + ctx.note_latex(k) for k in ctx.order]
    return [r"\secao{" + ctx.inline(head) + "}",
            r"{\small\begin{list}{}{\setlength{\leftmargin}{2em}\setlength{\labelwidth}{1.5em}"
            r"\setlength{\labelsep}{0.5em}\setlength{\itemsep}{0.4\baselineskip}}" + "\n"
            + "\n".join(items) + "\n" + r"\end{list}}"]


def build_tex(doc: Doc, a, ctx: Ctx) -> str:
    autor = a.autor or next((t for k, t in doc.subs if k == "autor"), "")
    titulo = a.titulo or doc.title or ""
    tex = PREAMBLE
    for k, v in _layout(a).items():
        tex = tex.replace(k, v)
    tex = (tex.replace("@HEADERS@", _headers(a, ctx, titulo, autor))
           .replace("@PDFTITLE@", ctx.esc(titulo)).replace("@PDFAUTHOR@", ctx.esc(autor)))
    out = _title_block(doc, a, ctx, titulo, autor) if titulo else []
    out += _blocks_latex(doc, ctx)
    if a.notas == "fim" and ctx.order:
        out += _endnotes_latex(doc, a, ctx)
    missing = [k for k in doc.notes if k not in ctx.order]
    if missing:
        doc.warnings.append(f"notas definidas e nunca citadas: {missing}")
    if doc.colofao:
        out.append(r"\sectionbreak")
        out.append(r"{\small\noindent " + r"\par\smallskip\noindent ".join(ctx.inline(p) for p in doc.colofao) + r"\par}")
    return tex + "\n\n".join(out) + "\n\\end{document}\n"


# ----------------------------------------------------------------------------- build
def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def compile_pdf(tex: str, build: Path) -> Path:
    src = build / "livro.tex"
    src.write_text(tex, encoding="utf-8")
    for _ in range(2):
        r = run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", src.name], cwd=build)
        if r.returncode:
            log = (build / "livro.log").read_text(errors="replace")
            erros = "\n".join(l for l in log.splitlines() if l.startswith("!") or l.startswith("l."))
            sys.exit(f"lualatex falhou. Linhas de erro do log ({build / 'livro.log'}):\n{erros[:2000]}")
    return build / "livro.pdf"


def page_text(pdf: Path, page: int) -> str:
    return run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"]).stdout


def relatorio_build(build: Path, pdf: Path) -> dict:
    log = (build / "livro.log").read_text(errors="replace")
    info = {"paginas": None, "overfull": len(re.findall(r"^Overfull \\hbox", log, re.M)),
            "underfull": len(re.findall(r"^Underfull", log, re.M)),
            "glifos_ausentes": sorted(set(re.findall(r"Missing character: There is no (\S+)", log)))}
    m = re.search(r"Output written on .*?\((\d+) pages?", log)
    info["paginas"] = int(m.group(1)) if m else None
    if shutil.which("pdftotext") and info["paginas"]:
        n = info["paginas"]
        first, last = (2, min(4, n)) if n >= 2 else (1, 1)
        r = run(["pdftotext", "-f", str(first), "-l", str(last), str(pdf), "-"])
        lens = [len(l) for l in r.stdout.splitlines() if len(l) > 50]
        info["cpl"] = round(statistics.median(lens), 1) if lens else None
    return info


def _words(s: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", s).split()[:5]).lower()


def first_note_page(doc: Doc, ctx: Ctx, pdf: Path, n: int) -> int | None:
    """Página em que o texto da primeira nota citada aparece (só faz sentido com notas no rodapé)."""
    if not ctx.order or not shutil.which("pdftotext"):
        return None
    first = doc.notes[ctx.order[0]][0]
    needle = _words(first[1] if first[0] == "p" else first[1][0])
    for pg in range(1, n + 1):
        if needle and needle in _words_all(page_text(pdf, pg)):
            return pg
    return None


def _words_all(s: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", s).split()).lower()


def render_controle(doc: Doc, ctx: Ctx, pdf: Path, build: Path, n: int) -> list[Path]:
    pages = {1, 2, 3, n}
    if ctx.notas == "rodape":
        pg = first_note_page(doc, ctx, pdf, n)
        if pg:
            pages.add(pg)
    for pg in sorted(p for p in pages if 1 <= p <= n):
        run(["pdftoppm", "-r", "60", "-png", "-f", str(pg), "-l", str(pg), str(pdf), str(build / "controle")])
    return sorted(build.glob("controle*.png"))


# ----------------------------------------------------------------------------- main
def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fonte_md", type=Path, help="arquivo Markdown de origem")
    p.add_argument("-o", "--saida", type=Path, help="PDF de saída (padrão: mesmo nome, ao lado da origem)")
    p.add_argument("--inspecionar", action="store_true", help="só imprime o inventário do texto")
    p.add_argument("--fonte", choices=FONTES, default="garamond", help="família tipográfica do corpo")
    p.add_argument("--corpo", type=float, help="tamanho do corpo em pt (padrão depende da fonte)")
    p.add_argument("--entrelinha", type=float, help="entrelinha em pt (padrão depende da fonte)")
    p.add_argument("--mancha", type=float, default=118.0, help="largura da mancha de texto em mm (padrão 118)")
    p.add_argument("--notas", choices=("rodape", "fim"), default="rodape")
    p.add_argument("--papel", choices=PAPEIS, default="a4")
    p.add_argument("--so-frente", action="store_true", help="margens simétricas, sem espelhamento")
    p.add_argument("--margem-anotacao", action="store_true", help="mancha deslocada para dentro, margem externa larga")
    p.add_argument("--lang", choices=BABEL, help="idioma da hifenização (padrão: adivinhado)")
    p.add_argument("--titulo"); p.add_argument("--autor"); p.add_argument("--data")
    p.add_argument("--sem-cabecalho", action="store_true", help="só número de página no pé")
    p.add_argument("--tex", type=Path, help="também grava o .tex gerado neste caminho")
    p.add_argument("--sem-controle", action="store_true", help="não renderiza as páginas de controle em PNG")
    a = p.parse_args(argv)
    for nome in ("corpo", "entrelinha", "mancha"):
        v = getattr(a, nome)
        if v is not None and v <= 0:
            p.error(f"--{nome} tem de ser positivo")
    return a


def load_doc(a) -> tuple[Doc, dict, str]:
    try:
        raw = a.fonte_md.read_text(encoding="utf-8-sig")
    except (FileNotFoundError, UnicodeDecodeError, PermissionError) as e:
        sys.exit(f"não consegui ler {a.fonte_md}: {e}")
    meta, text = split_front_matter(raw)
    doc = Doc()
    lines = extract_pg_notes(extract_md_notes(text.split("\n"), doc), doc)
    parse_body(lines, doc)
    if meta.get("title"):
        doc.title = meta["title"]
    if meta.get("author") and not a.autor:
        a.autor = meta["author"]
    if meta.get("date") and not any(k == "data" for k, _ in doc.subs):
        doc.subs.append(("data", meta["date"]))
    if a.data:
        doc.subs = [s for s in doc.subs if s[0] != "data"] + [("data", a.data)]
    return doc, meta, text


def inventario(doc: Doc, a, ctx: Ctx, npt: int, nen: int) -> None:
    autor = a.autor or next((t for k, t in doc.subs if k == "autor"), None)
    print(f"título: {doc.title!r}  autor: {autor!r}  subtítulos: {doc.subs}")
    print(f"idioma: {a.lang} (pt={npt} en={nen})  fonte: {a.fonte} {a.corpo}/{a.entrelinha} pt  mancha: {a.mancha} mm  "
          f"papel: {a.papel} {'só frente' if a.so_frente else 'frente e verso'}")
    print(f"blocos: {doc.counts}")
    print(f"notas: estilo={doc.note_style} definidas={len(doc.notes)} citadas={len(ctx.order)} "
          f"(+{len(ctx.urls)} de link) → {a.notas}  colofão: {len(doc.colofao)} parágrafo(s)")
    print(f"normalizações de glifo: {ctx.norm}  math: {len(ctx.maths)}")
    print(f"avisos: {len(doc.warnings)}")
    for w in doc.warnings:
        print(f"AVISO: {w}")


def main(argv=None) -> int:
    a = parse_args(argv)
    doc, meta, text = load_doc(a)
    lang, npt, nen = guess_lang(text)
    meta_lang = meta.get("lang", "")[:2].lower()
    a.lang = a.lang or (meta_lang if meta_lang in BABEL else lang)
    _, corpo0, lead0 = FONTES[a.fonte]
    a.corpo = a.corpo or corpo0
    a.entrelinha = a.entrelinha or round(a.corpo * lead0 / corpo0, 1)

    ctx = Ctx(doc, a.notas, a.lang)
    tex = build_tex(doc, a, ctx)
    inventario(doc, a, ctx, npt, nen)
    if a.tex:
        a.tex.write_text(tex, encoding="utf-8")
        print(f"tex: {a.tex}")
    if a.inspecionar:
        return 0
    if not shutil.which("lualatex"):
        sys.exit("lualatex não encontrado: instale TeX Live (texlive-luatex, texlive-fonts-extra) ou use --tex e compile noutra máquina")
    build = Path(tempfile.mkdtemp(prefix="md2livro-"))
    pdf = compile_pdf(tex, build)
    out = a.saida or a.fonte_md.with_suffix(".pdf")
    if out.exists():
        print(f"AVISO: {out} já existia e foi sobrescrito")
    shutil.copy(pdf, out)
    info = relatorio_build(build, pdf)
    print(f"PDF: {out}  páginas: {info['paginas']}  caracteres/linha (mediana): {info.get('cpl')}  "
          f"overfull: {info['overfull']}  underfull: {info['underfull']}  glifos ausentes: {info['glifos_ausentes'] or 'nenhum'}")
    print(f"build: {build} (livro.tex, livro.log)")
    cpl = info.get("cpl")
    if cpl and not 60 <= cpl <= 72:
        print(f"SUGESTÃO: cpl fora de 60–72; tente --mancha {a.mancha * 68 / cpl:.0f} ou ajuste --corpo")
    if not a.sem_controle:
        if not shutil.which("pdftoppm"):
            print("AVISO: pdftoppm ausente (poppler-utils); páginas de controle não renderizadas")
        else:
            pngs = render_controle(doc, ctx, pdf, build, info["paginas"] or 1)
            print("controle:", " ".join(str(f) for f in pngs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
