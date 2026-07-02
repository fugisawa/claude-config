# Components — HTML Snippet Library

This document is a catalog of every component the briefing system supports. Each component has:
1. **When to use** it
2. **HTML snippet** (copy and paste)
3. **CSS class names** (for reference; styles live in `design_system.css`)
4. **Variants** if any

Use the components in this catalog. Don't invent new ones unless the user explicitly asks for something not covered — the design system's coherence depends on a fixed vocabulary.

---

## Table of contents

1. Cover variants (3)
2. Article header
3. Lede paragraph
4. Section headings (h2, h3)
5. Sidebar (with variants: numbers, list, definition, warning)
6. Pull quote
7. Callout (insight / warning / datapoint)
8. Tables (data, financial, comparison)
9. Charts (figure wrapper)
10. Sources block (editorial / academic)
11. Endmark

---

## 1. Cover variants

### Variant A — Editorial cover (default)

```html
<section class="cover cover-editorial">
  <div class="cover-kicker">BRIEFING ESTRATÉGICO · [TÓPICO]</div>
  <h1 class="cover-title">Título<br>Principal</h1>
  <p class="cover-deck">Subtítulo italicizado de uma ou duas frases que compressa o argumento inteiro.</p>
  <hr class="cover-rule">
  <div class="cover-byline">
    <strong>Análise estratégica</strong><br>
    [Local] &middot; [data por extenso]<br>
    <em>Horizonte: [janela de análise]</em>
  </div>
  <div class="cover-abstract">
    <span class="cover-abstract-label">Resumo</span>
    [4-6 frases compactando o argumento. Não cite fontes aqui — isso é apenas para o leitor decidir se vai ler o resto.]
  </div>
</section>
```

### Variant B — Academic cover

```html
<section class="cover cover-academic">
  <div class="cover-ornament">§</div>
  <div class="cover-kicker">WORKING PAPER · [INSTITUIÇÃO]</div>
  <h1 class="cover-title">Título do Trabalho</h1>
  <p class="cover-deck">Deck em romano, não itálico, mais curto.</p>
  <div class="cover-author">
    [Nome do autor]<br>
    <em>[Afiliação]</em><br>
    [Data]
  </div>
  <div class="cover-abstract">
    <span class="cover-abstract-label">Abstract</span>
    [Resumo de até 250 palavras, justificado, sem ornamento.]
  </div>
  <div class="cover-keywords">
    <strong>Keywords:</strong> termo1, termo2, termo3, termo4.
  </div>
</section>
```

### Variant C — Financial cover

```html
<section class="cover cover-financial">
  <div class="cover-vertical-rule"></div>
  <div class="cover-kicker">EQUITY RESEARCH · [SETOR]</div>
  <h1 class="cover-title">[Empresa / Tese]</h1>
  <p class="cover-deck">Tese em uma frase, sem ornamento, com verbo forte.</p>
  <table class="cover-summary-table">
    <tr><th>Ticker</th><td>XXXX</td></tr>
    <tr><th>Current</th><td>$XX.XX</td></tr>
    <tr><th>Target (12mo)</th><td>$XX.XX</td></tr>
    <tr><th>Recommendation</th><td><strong>BUY / HOLD / SELL</strong></td></tr>
    <tr><th>Risk rating</th><td>Low / Medium / High</td></tr>
  </table>
  <div class="cover-byline">
    <em>Analyst:</em> [Name] &middot; [Date]
  </div>
</section>
```

---

## 2. Article header (after cover, opens the body)

```html
<div class="article-header">
  <div class="kicker">BRIEFING &middot; [DATA]</div>
  <h1>Título do artigo, geralmente uma pergunta ou tese.</h1>
</div>
```

---

## 3. Lede paragraph

The first body paragraph. The drop cap requires wrapping the first letter in a `<span class="dropcap">` — the span is floated left so the cap sinks two lines deep without inflating the first line's leading. (Why a span and not `::first-letter`: WeasyPrint crashes on floated `::first-letter`, and the inline-block alternative stretches the first line's box to the cap's height, breaking the body's line rhythm.) In the academic persona the span is neutralized by CSS, so include it regardless of persona.

```html
<p class="lede"><span class="dropcap">O</span> parágrafo de abertura compressa toda a tese em quatro a seis frases. O leitor deve poder parar aqui e já saber do que se trata. Use frases ligeiramente mais longas e mais ambiciosas do que no corpo.</p>
```

Note the cap letter lives *inside* the span and is omitted from the running text ("<span>O</span> parágrafo", not "<span>O</span>O parágrafo").

---

## 4. Section headings

### h2 — Numbered section

```html
<h2>O anúncio e o que ele de fato é</h2>
```

The numeral is added automatically by CSS counter (`I.`, `II.`... in editorial; `1.`, `2.`... in academic/financial; `A.`, `B.`... in governmental).

### h3 — Subsection

```html
<h3>Cenário (i) — O Irã não trata como ato de guerra</h3>
```

No automatic numbering on h3.

---

## 5. Sidebar variants

### 5a — Numbers sidebar (most common)

Use to give the reader a structured snapshot of figures.

```html
<aside class="sidebar sidebar-numbers">
  <div class="sidebar-title">Por números</div>
  <ul>
    <li><strong>15.000</strong> militares mobilizados</li>
    <li><strong>100+</strong> aeronaves embarcadas e em terra</li>
    <li><strong>~20.000</strong> marítimos presos no estreito</li>
  </ul>
</aside>
```

### 5b — Bulleted list sidebar

For enumerative content that doesn't fit "numbers" framing.

```html
<aside class="sidebar">
  <div class="sidebar-title">Pontos do plano</div>
  <ul>
    <li>Item curto, uma linha quando possível.</li>
    <li>Item curto, paralelo gramaticalmente ao primeiro.</li>
    <li>Item curto.</li>
  </ul>
</aside>
```

### 5c — Definition sidebar

For explaining a term or concept.

```html
<aside class="sidebar sidebar-definition">
  <div class="sidebar-title">O que é "magazine drain"?</div>
  <p>Termo da literatura militar para a depleção acelerada de munições caras (interceptadores, mísseis de cruzeiro) frente a um adversário capaz de lançar grandes volumes de armas baratas (drones de baixo custo, foguetes não-guiados). Cria assimetria de custo insustentável.</p>
</aside>
```

### 5d — Warning sidebar

For highlighting risk or contested information.

```html
<aside class="sidebar sidebar-warning">
  <div class="sidebar-title">Atenção</div>
  <p>Os números a seguir vêm de declarações de governo americano e não foram independentemente verificados. Análises do CSIS e da Brookings apresentam estimativas até 30% maiores.</p>
</aside>
```

---

## 6. Pull quote

A sentence pulled from the body that crystallizes the argument. Use sparingly — one or two per brief.

```html
<blockquote class="pullquote">
  Texto do pull quote em itálico, idealmente uma única frase ou duas curtas, capturando o ponto central.
  <span class="pullquote-attr">Atribuição em pequenas maiúsculas</span>
</blockquote>
```

The attribution is optional. If the quote is from your own analysis (not a source), omit `<span class="pullquote-attr">`.

---

## 7. Callouts (in-line emphasis blocks)

Different from sidebars: callouts interrupt the flow rather than sitting beside it. Use rarely — once per brief at most.

### 7a — Insight callout

```html
<div class="callout callout-insight">
  <strong>Insight.</strong> A diferença entre os cenários é qualitativa, não quantitativa: duas ordens de grandeza separam o gesto humanitário de uma campanha de proporções históricas.
</div>
```

### 7b — Datapoint callout

For a single number that anchors the argument.

```html
<div class="callout callout-datapoint">
  <div class="datapoint-number">US$ 1,88 bi</div>
  <div class="datapoint-label">por dia, gasto militar dos EUA nos primeiros seis dias da Operation Epic Fury</div>
</div>
```

### 7c — Warning callout

```html
<div class="callout callout-warning">
  <strong>Risco.</strong> Estoques de SM-2/SM-6 já estão pressionados; demanda incremental tem custo de oportunidade alto no Indo-Pacífico.
</div>
```

---

## 8. Tables

### 8a — Data table (editorial / academic)

```html
<table class="data-table">
  <thead>
    <tr>
      <th>Cenário</th>
      <th>Probabilidade</th>
      <th>Brent (US$/bbl)</th>
      <th>Implicação para EUA</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>A. Acordo parcial</td>
      <td>40%</td>
      <td>80–90</td>
      <td>Vitória política</td>
    </tr>
    <tr>
      <td>B. Conflito congelado</td>
      <td>30%</td>
      <td>95–115</td>
      <td>Inflação persistente</td>
    </tr>
  </tbody>
</table>
```

### 8b — Financial table (financial persona)

Use for thesis summaries, multiple comparisons, valuation breakdowns.

```html
<table class="financial-table">
  <thead>
    <tr>
      <th></th>
      <th class="num">FY24A</th>
      <th class="num">FY25E</th>
      <th class="num">FY26E</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Revenue ($mn)</td>
      <td class="num">12,450</td>
      <td class="num">14,200</td>
      <td class="num">16,800</td>
    </tr>
    <tr>
      <td>EBITDA margin</td>
      <td class="num">22.4%</td>
      <td class="num">24.1%</td>
      <td class="num">26.8%</td>
    </tr>
    <tr class="row-emphasis">
      <td><strong>EPS ($)</strong></td>
      <td class="num"><strong>3.42</strong></td>
      <td class="num"><strong>4.18</strong></td>
      <td class="num"><strong>5.21</strong></td>
    </tr>
  </tbody>
</table>
```

### 8c — Comparison table

Two or three columns, for option-vs-option analysis.

```html
<table class="comparison-table">
  <thead>
    <tr>
      <th></th>
      <th>Opção A</th>
      <th>Opção B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Custo</th>
      <td>US$ 200 mi</td>
      <td>US$ 800 mi</td>
    </tr>
    <tr>
      <th>Risco</th>
      <td>Baixo</td>
      <td>Alto</td>
    </tr>
    <tr>
      <th>Reversibilidade</th>
      <td>Alta</td>
      <td>Baixa</td>
    </tr>
  </tbody>
</table>
```

---

## 9. Charts (figure wrapper)

Charts are pre-generated PNG/SVG files (see `CHARTS.md` for how to generate them). The HTML wraps them with the standard caption + label format.

```html
<figure class="chart-wrap">
  <div class="chart-label">Gráfico 1</div>
  <div class="chart-title">Título do gráfico — uma claim, não uma descrição</div>
  <img src="path/to/chart.png" alt="Descrição do gráfico para acessibilidade">
  <figcaption class="chart-caption">
    Fonte: [origem dos dados]. Notas: [se houver].
  </figcaption>
</figure>
```

Chart titles should make a claim ("Custo militar diverge em duas ordens de grandeza"), not just describe ("Custos por cenário").

---

## 10. Sources block

### 10a — Editorial sources (prose-style)

```html
<div class="sources">
  <div class="sources-title">Notas e fontes</div>
  <p><strong>Anúncio e desenho operacional:</strong> Fonte 1; Fonte 2; Fonte 3 (autor, data).</p>
  <p><strong>Reação iraniana:</strong> Fonte 4; Fonte 5.</p>
  <p><strong>Estimativas de custo:</strong> Fonte 6 (instituição); Fonte 7.</p>
  <p>Análise editorial e probabilidades atribuídas são síntese própria; não pretendem rigor probabilístico formal.</p>
</div>
```

### 10b — Academic references (numbered)

```html
<div class="references">
  <div class="references-title">References</div>
  <ol class="references-list">
    <li id="ref1">Author, A. (2026). <em>Title of work</em>. Publisher. https://doi.org/...</li>
    <li id="ref2">Author, B., &amp; Author, C. (2025). Article title. <em>Journal Name</em>, 42(3), 100–120.</li>
  </ol>
</div>
```

In-text citation in academic mode uses superscript: `<sup><a href="#ref1">1</a></sup>`.

---

## 11. Endmark

The endmark closes the body before the sources. Choose the persona-appropriate symbol.

```html
<div class="end-mark">❦</div>     <!-- editorial -->
<div class="end-mark">§</div>     <!-- academic, optional -->
<div class="end-mark">■</div>     <!-- financial -->
<!-- governmental: omit -->
```

---

## Composition rules

- **Sidebars and pull quotes never sit adjacent.** Leave at least two paragraphs of body between them.
- **Charts never sit adjacent.** Leave at least one section between charts.
- **Don't open a section with a sidebar or chart.** Open with body prose, place visual furniture after the argument is established.
- **One callout per brief, maximum.** Callouts interrupt; sidebars don't. Pick your interruption carefully.
- **Tables in financial briefs can be larger and more numerous** than in editorial briefs. The financial reader expects tables.

When in doubt, leave it out. The brief's authority comes from restraint, not from filling every page.

---

## 12. Key assessments box ("Avaliações principais")

**When to use:** Immediately after the lede, in argumentative or prescriptive briefs. Lists the 2–4 major judgments — each a complete sentence with its calibrated probability term and range; the most consequential ones followed by a separate confidence sentence. See `TRADECRAFT.md` Sections 2–4 for the language rules. Label by language: "Avaliações principais" / "Key assessments" / "Evaluaciones principales" / "Évaluations principales".

```html
<div class="key-assessments">
  <span class="ka-label">Avaliações principais</span>
  <ol>
    <li>É muito provável (80–95%) que [julgamento 1].
        <span class="confidence">Confiança alta: [fontes múltiplas e independentes que convergem porque...].</span></li>
    <li>É provável (55–80%) que [julgamento 2].</li>
    <li>É improvável (20–45%) que [julgamento 3].
        <span class="confidence">Confiança média: [base crível, mas corroboração insuficiente porque...].</span></li>
  </ol>
</div>
```

## 13. Indicators block ("O que mudaria esta avaliação")

**When to use:** Near the synthesis section. 3–5 *observable* developments (an event, a threshold, a published document), each tied to the judgment it affects and the direction. See `TRADECRAFT.md` Section 5. Label by language: "O que mudaria esta avaliação" / "What would change this assessment" / "Qué cambiaría esta evaluación" / "Ce qui changerait cette évaluation".

```html
<div class="indicators">
  <span class="ind-label">O que mudaria esta avaliação</span>
  <ul>
    <li>[Evento observável] enfraqueceria a avaliação 1.</li>
    <li>[Número cruzando limiar] reforçaria a avaliação 2.</li>
    <li>[Documento publicado até data] enfraqueceria a avaliação central.</li>
  </ul>
</div>
```

## 14. Probability-scale legend

**When to use:** Whenever ladder terms appear in the document (which is almost always). One italic line in the sources/notes area, written naturally — not a compliance table.

```html
<p class="uncertainty-note">Os termos de probabilidade neste documento seguem uma
escala fixa: muito improvável (5–20%), improvável (20–45%), chances aproximadamente
iguais (45–55%), provável (55–80%), muito provável (80–95%), quase certo (95–99%).</p>
```

## 15. Table of contents (long-form mode)

**When to use:** Documents ≥15 pp with `class="longform"` on `<body>`. Place immediately after the cover. Every `href` must point to an existing `id`; the CSS adds dotted leaders and live page numbers automatically via `target-counter()`. Use `toc-l1` for sections, `toc-l2` for subsections worth listing (be selective — a TOC is navigation, not an outline dump).

```html
<nav class="toc">
  <div class="toc-title">Sumário</div>
  <ol>
    <li class="toc-l1"><a href="#sec-1">I. Título da primeira seção</a></li>
    <li class="toc-l2"><a href="#sec-1-1">Subseção relevante</a></li>
    <li class="toc-l1"><a href="#sec-2">II. Título da segunda seção</a></li>
    <li class="toc-l1"><a href="#sintese">Síntese</a></li>
    <li class="toc-l1"><a href="#fontes">Fontes e notas</a></li>
  </ol>
</nav>
```

Each section heading then carries the matching id: `<h2 id="sec-1">...</h2>`.

## 16. Footnotes (long-form mode)

**When to use:** Source asides, terminological clarifications, and qualifications too granular for the prose. Never for argument — if it matters to the thesis, it belongs in the body. Write the note *inline* where the call should appear; WeasyPrint floats it to the page bottom and numbers it automatically.

```html
<p>O dispositivo foi regulamentado em 2024<span class="footnote">Decreto
n.º 11.999/2024, art. 7º; a redação anterior exigia regulamentação por lei
ordinária.</span> e desde então...</p>
```

Running headers (the current section name at the top of each page) require no markup: with `class="longform"` on `<body>`, each `h2`'s text is picked up automatically.
