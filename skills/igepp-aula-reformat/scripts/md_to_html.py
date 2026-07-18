"""Converte o Markdown da aula (convenções em CONVENTIONS.md) em HTML de impressão.

O HTML resultante referencia aula.css (copiar do diretório assets/ da skill) e é
renderizado com WeasyPrint. Diagramas: o N-ésimo bloco ```mermaid vira
<figure><img src="diagramaN.svg"> se diagramaN.svg existir ao lado do HTML;
sem o arquivo, o bloco é pulado com aviso (crie o SVG e reconverta).

Uso:
    python md_to_html.py aula.md aula.html
"""
import argparse
import os
import re
import sys
import unicodedata

ESC_STAR, ESC_UND = "\x01", "\x02"


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "sec"


def inline(text: str) -> str:
    t = text.replace("\\*", ESC_STAR).replace("\\_", ESC_UND)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"~~(.+?)~~", r"<s>\1</s>", t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    t = t.replace("&lt;br&gt;", "<br>")  # <br> literal permitido (células de tabela)
    t = t.replace(ESC_STAR, "*").replace(ESC_UND, "_")
    return t


def parse_frontmatter(lines: list) -> tuple:
    """YAML simples chave: valor. Retorna (dict, resto_das_linhas)."""
    if not lines or lines[0].strip() != "---":
        return {}, lines
    meta = {}
    for i, ln in enumerate(lines[1:], start=1):
        if ln.strip() == "---":
            return meta, lines[i + 1:]
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", ln)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    sys.exit("erro: frontmatter aberto com '---' na linha 1 nunca foi fechado")


def parse_table(rows: list) -> str:
    def cells(row: str) -> list:
        raw = row.strip().strip("|")
        return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", raw)]

    header = cells(rows[0])
    sep_re = re.compile(r"^:?-+:?$")
    if len(rows) > 1 and all(sep_re.match(c) for c in cells(rows[1])):
        body = [cells(r) for r in rows[2:]]
    else:
        print("aviso: tabela sem linha separadora GFM; nenhuma linha descartada",
              file=sys.stderr)
        body = [cells(r) for r in rows[1:]]
    out = ["<table>", "<thead><tr>"]
    for h in header:
        out.append(f"<th>{inline(h)}</th>")
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>")
        for i, c in enumerate(r):
            attr = ""
            bare = c.replace("*", "").strip()
            if i == len(r) - 1 and bare in ("Sim", "Não", "Nao"):
                attr = ' class="yes"' if bare == "Sim" else ' class="no"'
            out.append(f"<td{attr}>{inline(c)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def parse_list_block(lines: list) -> str:
    items = []  # (indent, ordered, content)
    prev_indent = -1
    for ln in lines:
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if not m:
            if items:
                items[-1] = (items[-1][0], items[-1][1], items[-1][2] + " " + ln.strip())
            continue
        indent = min(len(m.group(1)) // 2, prev_indent + 1)  # salto >1 nível = HTML inválido
        prev_indent = indent
        items.append((indent, m.group(2) not in ("-", "*"), m.group(3)))

    out, stack, prev = [], [], -1
    for indent, ordered, content in items:
        tag = "ol" if ordered else "ul"
        if indent > prev:
            for _ in range(indent - prev):
                out.append(f"<{tag}>")
                stack.append(tag)
        elif indent < prev:
            for _ in range(prev - indent):
                out.append("</li>")
                out.append(f"</{stack.pop()}>")
            out.append("</li>")
        else:
            out.append("</li>")
        out.append(f"<li>{inline(content)}")
        prev = indent
    while stack:
        out.append("</li>")
        out.append(f"</{stack.pop()}>")
    return "".join(out)


def parse_blockquote(lines: list) -> str:
    inner = [re.sub(r"^>\s?", "", ln) for ln in lines]
    m = re.match(r"^\[!(\w+)\]\s*(.*)$", inner[0]) if inner else None
    if m:
        kind, title = m.group(1).lower(), m.group(2)
        cls = "callout warning" if kind in ("warning", "caution") else "callout"
        return (
            f'<div class="{cls}"><div class="callout-title">{inline(title)}</div>'
            f"{render_blocks(inner[1:])}</div>"
        )
    return f"<blockquote>{render_blocks(inner)}</blockquote>"


def render_blocks(lines: list) -> str:
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            block = []
            while i < len(lines) and (
                re.match(r"^\s*([-*]|\d+\.)\s+", lines[i])
                or (lines[i].startswith("    ") and lines[i].strip())
            ):
                block.append(lines[i])
                i += 1
            out.append(parse_list_block(block))
            continue
        if ln.startswith(">"):
            block = []
            while i < len(lines) and lines[i].startswith(">"):
                block.append(lines[i])
                i += 1
                # linha ">" vazia entre parágrafos do quote já vem com ">"
            out.append(parse_blockquote(block))
            continue
        if ln.strip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(parse_table(block))
            continue
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(\s*([-*]|\d+\.)\s+|>|\||#{1,6}\s|---\s*$|```)", lines[i]
        ):
            para.append(lines[i].strip())
            i += 1
        text = " ".join(para)
        cls = ""
        if text.startswith("**Comentários:**"):
            cls = ' class="coment"'
        elif text.startswith("*Material original"):
            cls = ' class="colophon"'
        out.append(f"<p{cls}>{inline(text)}</p>")
    return "".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md_in")
    ap.add_argument("html_out")
    args = ap.parse_args()

    try:
        src = open(args.md_in, encoding="utf-8").read().split("\n")
    except OSError as e:
        sys.exit(f"erro: não foi possível ler {args.md_in}: {e}")
    meta, rest = parse_frontmatter(src)
    html_dir = os.path.dirname(os.path.abspath(args.html_out))
    os.makedirs(html_dir, exist_ok=True)

    # garante o CSS ao lado do HTML (esquecê-lo gerava PDF sem estilo, em silêncio)
    css_dst = os.path.join(html_dir, "aula.css")
    if not os.path.exists(css_dst):
        import shutil
        css_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "aula.css")
        if os.path.exists(css_src):
            shutil.copy(css_src, css_dst)
            print(f"aula.css copiado para {html_dir}", file=sys.stderr)

    # corpo começa no primeiro "## "
    try:
        start = next(i for i, ln in enumerate(rest) if ln.startswith("## "))
    except StopIteration:
        sys.exit("erro: nenhum heading '## ' encontrado no corpo do MD")
    lines = rest[start:]

    n_questoes = sum(1 for ln in lines if re.match(r"^\*\*Questão \d+\*\*\s*[-–—]\s*", ln))

    body, toc = [], []
    seen_slugs = {}
    i = 0
    mermaid_n = 0
    in_questao = False

    def close_questao():
        nonlocal in_questao
        if in_questao:
            body.append("</section>")
            in_questao = False

    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            if j >= len(lines):
                sys.exit(f"erro: bloco ``` aberto nunca foi fechado (conteúdo após ele seria perdido)")
            if not ln.startswith("```mermaid"):
                print("aviso: bloco ``` não-mermaid ignorado (sem suporte no PDF)",
                      file=sys.stderr)
            if ln.startswith("```mermaid"):
                mermaid_n += 1
                svg = f"diagrama{mermaid_n}.svg"
                if os.path.exists(os.path.join(html_dir, svg)):
                    body.append(
                        f'<figure class="diagram"><img src="{svg}" alt="Diagrama {mermaid_n}"/>'
                        "<figcaption>Diagrama redesenhado a partir do original.</figcaption></figure>"
                    )
                else:
                    print(f"aviso: {svg} não encontrado em {html_dir}; figura pulada",
                          file=sys.stderr)
            i = j + 1
            continue

        m = re.match(r"^(#{2,4})\s+(.*)$", ln)
        if m:
            close_questao()
            level, title = len(m.group(1)), m.group(2).strip()
            hid = slugify(title)
            if hid in seen_slugs:
                seen_slugs[hid] += 1
                hid = f"{hid}-{seen_slugs[hid]}"
            else:
                seen_slugs[hid] = 1
            if level <= 3:
                toc.append((level, hid, title))
            body.append(f'<h{level} id="{hid}">{inline(title)}</h{level}>')
            i += 1
            continue

        if re.match(r"^---\s*$", ln):
            close_questao()
            i += 1
            continue

        mq = re.match(r"^\*\*Questão (\d+)\*\*\s*[-–—]\s*(.*)$", ln)
        if mq:
            close_questao()
            body.append(
                '<section class="questao"><div class="qhead">'
                f'<span class="qnum">Questão {mq.group(1)}</span>'
                f'<span class="qmeta">{inline(mq.group(2))}</span></div>'
            )
            in_questao = True
            i += 1
            continue

        mg = re.match(r"^\*\*Gabarito:\*\*\s*(.*)$", ln)
        if mg and in_questao:
            body.append(f'<div class="gabarito">Gabarito: {inline(mg.group(1))}</div>')
            close_questao()
            i += 1
            continue

        block = []
        while i < len(lines):
            cur = lines[i]
            if (
                cur.startswith("```")
                or re.match(r"^#{2,4}\s", cur)
                or re.match(r"^---\s*$", cur)
                or re.match(r"^\*\*Questão \d+\*\*\s*[-–—]\s*", cur)
                or (in_questao and re.match(r"^\*\*Gabarito:\*\*", cur))
            ):
                break
            block.append(cur)
            i += 1
        body.append(render_blocks(block))

    close_questao()

    title = meta.get("title", "Aula")
    subtitle = meta.get("subtitle", "")
    kicker = meta.get("kicker", meta.get("concurso", ""))
    footer = meta.get("footer", title)
    disciplina = meta.get("disciplina", "")
    tipo = meta.get("tipo", "")
    autor = meta.get("autor", "")
    edicao = meta.get("edicao", "")
    questoes_line = f"{tipo} — {n_questoes} questões comentadas" if n_questoes else tipo

    toc_html = "".join(
        f'<li class="lvl{lv}"><a href="#{hid}">{inline(t)}</a></li>' for lv, hid, t in toc
    )
    sub_html = f'<div class="cover-sub">{inline(subtitle)}</div>' if subtitle else ""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{inline(title)}</title>
<link rel="stylesheet" href="aula.css">
</head>
<body>
<div class="string-set-footer">{inline(footer)}</div>

<section class="cover">
  <div class="cover-kicker">{inline(kicker)}</div>
  <h1 class="cover-title">{inline(title)}</h1>
  {sub_html}
  <hr class="cover-rule">
  <div class="cover-meta">
    <strong>{inline(disciplina)}</strong><br>
    {questoes_line}<br>
    Autor: <strong>{inline(autor)}</strong> · IGEPP — Edição {edicao}
  </div>
  <div class="cover-note">Edição reformatada: texto integral preservado; diagramas e tabelas
  redesenhados; marca d'água e elementos repetidos do original removidos para impressão limpa.</div>
</section>

<nav class="toc">
  <div class="toc-title">Sumário</div>
  <ul>{toc_html}</ul>
</nav>

<article>
{''.join(body)}
</article>

</body>
</html>"""

    with open(args.html_out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{len(html)} chars, {n_questoes} questões, {len(toc)} entradas de sumário -> {args.html_out}")


if __name__ == "__main__":
    main()
