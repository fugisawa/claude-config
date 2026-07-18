"""Extração de texto de aulas IGEPP (TCPDF) imune à marca d'água rotacionada.

Estratégia: extração por spans do PyMuPDF, filtrando
  1. linhas rotacionadas (dir != horizontal) -> marca d'água "Edição 20xx";
  2. mobília repetida (mesmo texto na mesma altura em >=40% das páginas)
     -> rodapés/cabeçalhos de texto ("Controladoria-Geral da União", site etc.);
  3. números de página (linha que é só o número da própria página).

NUNCA use redação (apply_redactions) para remover a marca d'água: os retângulos
diagonais das linhas rotacionadas engolem o texto do corpo por baixo.

Saída: uma linha por linha do PDF, com **negrito** / *itálico* / ***ambos***,
separadores "===== PAGE N =====" e linha em branco em saltos verticais grandes.

Uso:
    uv run --with pymupdf python extract_spans.py aula.pdf saida.txt
    # cortes manuais extras (pontos, opcional):
    uv run --with pymupdf python extract_spans.py aula.pdf saida.txt --header-cut 80 --footer-cut 90
"""
import argparse
from collections import Counter

import fitz

GAP_BLANK_LINE = 30  # salto vertical (pt) que vira linha em branco na saída
FURNITURE_MIN_FRACTION = 0.4  # (y, texto) presente em >=40% das páginas = mobília


def styled_text(line: dict) -> str:
    parts = []
    for span in line["spans"]:
        t = span["text"]
        if not t.strip():
            parts.append(t)
            continue
        bold = bool(span["flags"] & 16) or "Bold" in span["font"]
        italic = bool(span["flags"] & 2) or "Italic" in span["font"]
        if bold and italic:
            t = f"***{t}***"
        elif bold:
            t = f"**{t}**"
        elif italic:
            t = f"*{t}*"
        parts.append(t)
    return "".join(parts).rstrip()


def collect_lines(doc: fitz.Document, header_cut: float, footer_cut: float):
    """[(page_no, y0, x0, texto_estilizado, texto_plano)] sem watermark/cortes."""
    rows = []
    for pno, page in enumerate(doc, start=1):
        h = page.rect.height
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                dx, dy = line["dir"]
                if abs(dy) > 0.01:
                    continue  # marca d'água rotacionada
                x0, y0, x1, y1 = line["bbox"]
                if header_cut and y1 < header_cut:
                    continue
                if footer_cut and y0 > h - footer_cut:
                    continue
                plain = "".join(s["text"] for s in line["spans"]).strip()
                if not plain:
                    continue
                rows.append((pno, y0, x0, styled_text(line), plain))
    return rows


def furniture_keys(rows, n_pages: int) -> set:
    """Chaves (y arredondado, texto) que se repetem em muitas páginas."""
    freq = Counter()
    for pno, y0, _x0, _st, plain in rows:
        freq[(round(y0), plain)] += 1
    threshold = max(3, int(n_pages * FURNITURE_MIN_FRACTION))
    return {k for k, c in freq.items() if c >= threshold}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--header-cut", type=float, default=0.0,
                    help="descartar linhas acima deste y (pt); 0 = desligado")
    ap.add_argument("--footer-cut", type=float, default=0.0,
                    help="descartar linhas a menos de N pt do pé da página; 0 = desligado")
    ap.add_argument("--pages", default="",
                    help="intervalo A-B (1-based, inclusivo) para extrair só parte do PDF")
    args = ap.parse_args()

    try:
        doc = fitz.open(args.pdf)
    except Exception as e:
        raise SystemExit(f"erro: não foi possível abrir {args.pdf}: {e}")
    rows = collect_lines(doc, args.header_cut, args.footer_cut)
    furniture = furniture_keys(rows, len(doc))  # mobília calculada no doc INTEIRO

    p_ini, p_fim = 1, len(doc)
    if args.pages:
        try:
            p_ini, p_fim = (int(x) for x in args.pages.split("-"))
        except ValueError:
            raise SystemExit(f"erro: --pages espera A-B (ex.: 1-8), recebi {args.pages!r}")

    if furniture:
        import sys
        print("mobília detectada (auditar):", file=sys.stderr)
        for y, txt in sorted(furniture):
            print(f"  y={y}: {txt[:70]}", file=sys.stderr)
    out, dropped = [], 0
    for pno in range(p_ini, p_fim + 1):
        page_rows = sorted(
            (r for r in rows if r[0] == pno), key=lambda r: (round(r[1], 1), r[2])
        )
        out.append(f"\n===== PAGE {pno} =====\n")
        prev_y = None
        for _pno, y0, _x0, styled, plain in page_rows:
            if (round(y0), plain) in furniture:
                dropped += 1
                continue
            if plain in (str(pno), f"{pno}/{len(doc)}", f"- {pno} -",
                         f"Página {pno}", f"Pág. {pno}"):
                dropped += 1
                continue
            if plain.startswith("Powered by TCPDF"):
                dropped += 1
                continue
            gap = "" if prev_y is None or (y0 - prev_y) < GAP_BLANK_LINE else "\n"
            out.append(f"{gap}{styled}")
            prev_y = y0

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"{len(doc)} páginas; {len(rows)} linhas; {dropped} de mobília/nº descartadas -> {args.out}")


if __name__ == "__main__":
    main()
