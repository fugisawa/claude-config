#!/usr/bin/env python3
"""
validate.py — Validate a briefing HTML before rendering.

Checks:
  1. Direct quotes (text inside <q>, "..." with markers) are <= 15 words.
  2. No source is referenced in more than one direct quote.
  3. Lede paragraph exists and is between 60 and 200 words.
  4. All <img src="..."> in chart-wraps point to files that exist.
  5. Language attribute is consistent (single primary language declared).
  6. Common AI tells (parallel-three constructions, "in conclusion") flagged.
  7. No empty section headings, no orphan h3 without preceding h2.
  8. Analytic rigor (v2): probability+confidence mixed in one sentence (error),
     vague hedges instead of calibrated terms (warning), ladder terms without
     range anchors or scale legend (warning), internal jargon leaking into the
     rendered text (error).
  9. Long-form (v2): TOC anchors that don't resolve (error), TOC without the
     'longform' body class (warning).

Usage:
    python validate.py <path/to/briefing.html>

Returns exit code 0 if all checks pass, 1 otherwise. Prints a human-readable report.
"""

from __future__ import annotations
import sys
import re
import argparse
from pathlib import Path
from html.parser import HTMLParser


# ============================================================
# Quote extraction
# ============================================================

QUOTE_PATTERNS = [
    # "..." (curly or straight)
    re.compile(r'[""]([^""]{15,500})[""]'),
    re.compile(r'"([^"]{15,500})"'),
    # «...» (continental European style, sometimes used in Portuguese)
    re.compile(r'«([^»]{15,500})»'),
]


def extract_quotes(text: str) -> list[str]:
    """Find all probable direct quotations in the prose."""
    quotes = []
    for pat in QUOTE_PATTERNS:
        for m in pat.finditer(text):
            q = m.group(1).strip()
            if q:
                quotes.append(q)
    return quotes


def word_count(s: str) -> int:
    return len(re.findall(r"\b\w+\b", s))


# ============================================================
# HTML parsing
# ============================================================

class BriefParser(HTMLParser):
    """Strip HTML and capture structure."""

    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self.lede_text: str = ""
        self.in_lede = False
        self.in_script_or_style = False
        self.images: list[str] = []
        self.h2_count = 0
        self.h3_before_h2 = False
        self.lang = None
        self.persona = None
        self.empty_h2 = []
        self._h2_buf = ""
        self._in_h2 = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == "html" and "lang" in attrs_d:
            self.lang = attrs_d["lang"]
        if tag == "body":
            cls = attrs_d.get("class", "")
            for c in cls.split():
                if c.startswith("persona-"):
                    self.persona = c.replace("persona-", "")
        if tag in ("script", "style"):
            self.in_script_or_style = True
        if tag == "p" and "lede" in attrs_d.get("class", ""):
            self.in_lede = True
        if tag == "img":
            src = attrs_d.get("src")
            if src:
                self.images.append(src)
        if tag == "h2":
            self._in_h2 = True
            self._h2_buf = ""
            if self.h2_count == 0 and self.h3_before_h2:
                pass  # already flagged
            self.h2_count += 1
        if tag == "h3" and self.h2_count == 0:
            self.h3_before_h2 = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_script_or_style = False
        if tag == "p" and self.in_lede:
            self.in_lede = False
        if tag == "h2":
            if not self._h2_buf.strip():
                self.empty_h2.append(self.h2_count)
            self._in_h2 = False

    def handle_data(self, data):
        if self.in_script_or_style:
            return
        self.text_parts.append(data)
        if self.in_lede:
            self.lede_text += data
        if self._in_h2:
            self._h2_buf += data

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)


# ============================================================
# Common AI-tells detection
# ============================================================

AI_TELLS = [
    (re.compile(r"\bin conclusion\b", re.I),
     "AI-tell: 'in conclusion' is a closing cliché; prefer a direct synthesis."),
    (re.compile(r"\bem conclusão\b", re.I),
     "AI-tell: 'em conclusão' é cliché de fechamento; prefira síntese direta."),
    (re.compile(r"\bit('s| is) important to note\b", re.I),
     "AI-tell: 'it is important to note' adds no information; cut it."),
    (re.compile(r"\bé importante (notar|destacar|frisar|salientar)\b", re.I),
     "AI-tell: 'é importante notar/destacar' adiciona zero informação; corte."),
    (re.compile(r"\bvarious factors\b", re.I),
     "AI-tell: 'various factors' is hand-waving; name the factors."),
    (re.compile(r"\bdiversos fatores\b", re.I),
     "AI-tell: 'diversos fatores' é evasivo; nomeie os fatores."),
    (re.compile(r"\bin today's (rapidly )?changing world\b", re.I),
     "AI-tell: 'in today's changing world' is filler; cut."),
    # Parallel-three: very rough heuristic
    (re.compile(r"\b(\w+ly), (\w+ly), and (\w+ly)\b"),
     "AI-tell: parallel three adverbs ('quickly, efficiently, and reliably'). Often a tell."),
]


# ============================================================
# Analytic-rigor layer (v2) — see TRADECRAFT.md
# All reader-facing messages stay in plain language.
# ============================================================

# Calibrated probability ladder, all four document languages
LADDER_TERMS = [
    # pt-BR
    "quase nenhuma chance", "muito improvável", "improvável",
    "chances aproximadamente iguais", "muito provável", "provável", "quase certo",
    # en
    "almost no chance", "very unlikely", "unlikely", "roughly even chance",
    "very likely", "likely", "almost certain",
    # es
    "casi ninguna posibilidad", "muy improbable", "improbable",
    "posibilidades casi iguales", "muy probable", "probable", "casi seguro",
    # fr
    "presque aucune chance", "très improbable", "improbable",
    "chances à peu près égales", "très probable", "probable", "presque certain",
]
# Order longest-first so "muito provável" matches before "provável"
LADDER_TERMS.sort(key=len, reverse=True)
LADDER_RE = re.compile(
    "|".join(re.escape(t) for t in LADDER_TERMS), re.IGNORECASE
)

# Confidence-in-the-evidence expressions
CONFIDENCE_RE = re.compile(
    r"\b(confian[çc]a\s+(alta|m[ée]dia|baixa)"
    r"|(high|moderate|medium|low)\s+confidence"
    r"|confianza\s+(alta|media|baja)"
    r"|confiance\s+([ée]lev[ée]e|moyenne|faible))\b",
    re.IGNORECASE,
)

# Uncalibrated hedges — carry no fixed meaning; banned in analytic claims
VAGUE_HEDGES = re.compile(
    r"\b(talvez|possivelmente|pode ser que|provavelmente talvez"
    r"|maybe|perhaps|possibly"
    r"|quiz[áa]s?|tal vez"
    r"|peut-[êe]tre)\b",
    re.IGNORECASE,
)

# Probability-range anchor, e.g. "(55–80%)" or "(55-80%)"
RANGE_ANCHOR_RE = re.compile(r"\(\s*\d{1,2}\s*[–\-]\s*\d{1,2}\s*%\s*\)")

# Internal jargon that must never reach the reader (TRADECRAFT.md §1)
JARGON_RE = re.compile(
    r"\b(ICD\s*203|MECE|SCQA|BLUF|words of estimative probability"
    r"|key judgments?|analytic tradecraft|structured analytic techniques?)\b",
    re.IGNORECASE,
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


# ============================================================
# Validation
# ============================================================

def validate(html_path: str) -> dict:
    """Run all checks. Returns a dict with errors, warnings, info."""
    html = Path(html_path).read_text(encoding="utf-8")

    parser = BriefParser()
    parser.feed(html)

    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # 1 — Quote length
    quotes = extract_quotes(parser.text)
    long_quotes = [(q, word_count(q)) for q in quotes if word_count(q) > 15]
    if long_quotes:
        for q, n in long_quotes[:5]:
            preview = q[:80] + ("..." if len(q) > 80 else "")
            errors.append(f"Quote with {n} words (limit: 15): \"{preview}\"")
        if len(long_quotes) > 5:
            errors.append(f"... and {len(long_quotes) - 5} more long quotes")

    # 2 — Duplicate sources hard to detect without semantic analysis;
    #     issue a warning if many quotes from same nearby context
    if len(quotes) > 8:
        warnings.append(f"Brief contains {len(quotes)} direct quotations. Default should be paraphrasing; prune.")

    # 3 — Lede word count
    lede_words = word_count(parser.lede_text)
    if lede_words == 0:
        errors.append("No lede paragraph found. Add <p class=\"lede\">...</p>.")
    elif lede_words < 60:
        warnings.append(f"Lede has only {lede_words} words; aim for 60-200.")
    elif lede_words > 200:
        warnings.append(f"Lede has {lede_words} words; aim for 60-200. Consider trimming.")
    else:
        info.append(f"Lede: {lede_words} words (OK).")

    # 4 — Image existence
    base = Path(html_path).parent
    missing = []
    for img_src in parser.images:
        if img_src.startswith(("http://", "https://", "data:")):
            continue
        candidate = (base / img_src).resolve() if not Path(img_src).is_absolute() else Path(img_src)
        if not candidate.exists():
            missing.append(img_src)
    if missing:
        for m in missing:
            errors.append(f"Image referenced but not found: {m}")

    # 5 — Language consistency
    if not parser.lang:
        warnings.append("No <html lang> attribute set. Hyphenation may misbehave.")
    else:
        info.append(f"Language: {parser.lang}")

    # 6 — AI-tells
    for pat, msg in AI_TELLS:
        if pat.search(parser.text):
            warnings.append(msg)

    # 7 — Heading structure
    if parser.h3_before_h2:
        warnings.append("h3 appears before any h2. Section structure is unconventional.")
    if parser.empty_h2:
        errors.append(f"Empty h2 heading(s) detected (positions: {parser.empty_h2}).")
    if parser.h2_count == 0:
        warnings.append("No h2 headings. The brief has no section structure.")

    # 8 — Persona declared
    if not parser.persona:
        warnings.append("No persona class on <body>. Will use editorial defaults.")
    else:
        info.append(f"Persona: {parser.persona}")

    # ----------------------------------------------------------
    # Analytic-rigor layer (v2) — plain-language messages
    # ----------------------------------------------------------

    # 9 — Confidence and likelihood must never share a sentence:
    #     they rate different things (the evidence vs the event).
    mixed = []
    for s in _sentences(parser.text):
        if CONFIDENCE_RE.search(s) and LADDER_RE.search(s):
            mixed.append(s[:90] + ("..." if len(s) > 90 else ""))
    for s in mixed[:3]:
        errors.append(
            "Probabilidade e confiança na mesma frase — separe em duas frases "
            f"(a probabilidade avalia o evento; a confiança, a base de evidências): \"{s}\""
        )
    if len(mixed) > 3:
        errors.append(f"... e mais {len(mixed) - 3} frase(s) misturando probabilidade e confiança.")

    # 10 — Vague hedges carry no calibrated meaning
    hedge_hits = VAGUE_HEDGES.findall(parser.text)
    if hedge_hits:
        sample = ", ".join(sorted({h if isinstance(h, str) else h[0] for h in hedge_hits})[:5])
        warnings.append(
            f"Termos vagos de incerteza no texto ({sample}) — em afirmações analíticas, "
            "troque por um termo da escala fixa com faixa: ex. 'improvável (20–45%)', "
            "'provável (55–80%)'. Ver TRADECRAFT.md §2."
        )

    # 11 — Ladder terms should be anchored and explained
    ladder_uses = LADDER_RE.findall(parser.text)
    if ladder_uses:
        if not RANGE_ANCHOR_RE.search(parser.text):
            warnings.append(
                f"O documento usa termos calibrados de probabilidade ({len(ladder_uses)} ocorrência(s)) "
                "mas nenhum vem ancorado com a faixa percentual. Ancore ao menos o primeiro uso "
                "de cada termo: 'provável (55–80%)'."
            )
        if 'uncertainty-note' not in html:
            warnings.append(
                "Termos calibrados de probabilidade sem a legenda da escala. Adicione a nota "
                "<p class=\"uncertainty-note\">...</p> junto às fontes (COMPONENTS.md, componente 14)."
            )
        info.append(f"Vocabulário calibrado: {len(ladder_uses)} uso(s).")

    # 12 — Internal jargon must not leak into the rendered text
    jargon_found = sorted({j if isinstance(j, str) else j[0] for j in JARGON_RE.findall(parser.text)})
    if jargon_found:
        errors.append(
            "Jargão técnico interno vazou para o texto final ("
            + ", ".join(jargon_found)
            + ") — o leitor é leigo; use as formulações em linguagem natural de TRADECRAFT.md §1."
        )

    # 13 — Long-form: every TOC anchor must resolve to an id
    toc_hrefs = re.findall(r'<nav class="toc".*?</nav>', html, re.DOTALL | re.IGNORECASE)
    if toc_hrefs:
        hrefs = re.findall(r'href="#([^"]+)"', toc_hrefs[0])
        ids = set(re.findall(r'id="([^"]+)"', html))
        dangling = [h for h in hrefs if h not in ids]
        for h in dangling:
            errors.append(f"Entrada do sumário aponta para âncora inexistente: #{h}")
        if not dangling and hrefs:
            info.append(f"Sumário: {len(hrefs)} entrada(s), todas as âncoras resolvem.")
        if 'class="longform"' not in html and "longform" not in (html.split("<body", 1)[1][:200] if "<body" in html else ""):
            warnings.append(
                "Há um sumário (<nav class=\"toc\">) mas <body> não tem a classe 'longform' — "
                "cabeçalhos correntes e numeração do sumário dependem dela."
            )

    # 14 — Key-assessments box presence (informational)
    if 'key-assessments' in html:
        info.append("Caixa de avaliações principais presente.")
    else:
        info.append("Sem caixa de avaliações principais (ok para briefs descritivos).")

    return {
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "n_quotes": len(quotes),
        "n_images": len(parser.images),
        "n_sections": parser.h2_count,
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Validate a briefing HTML file.")
    parser.add_argument("html", help="Path to briefing HTML")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args()

    result = validate(args.html)

    print(f"\nValidation report — {args.html}\n")
    print(f"  Sections: {result['n_sections']}")
    print(f"  Images:   {result['n_images']}")
    print(f"  Quotes:   {result['n_quotes']}")
    print()

    if result["info"]:
        print("INFO:")
        for line in result["info"]:
            print(f"  · {line}")
        print()

    if result["warnings"]:
        print("WARNINGS:")
        for line in result["warnings"]:
            print(f"  ⚠ {line}")
        print()

    if result["errors"]:
        print("ERRORS:")
        for line in result["errors"]:
            print(f"  ✗ {line}")
        print()

    has_problems = bool(result["errors"]) or (args.strict and result["warnings"])
    if has_problems:
        print("Validation FAILED.\n")
        sys.exit(1)
    else:
        print("Validation passed.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
