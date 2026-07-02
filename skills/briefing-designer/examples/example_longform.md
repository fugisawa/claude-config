# Worked example — Long-form brief (20+ pp, editorial persona, pt-BR)

This example shows the *deltas* relative to a standard article brief. Everything else (cover, lede, sections, charts, synthesis, sources) follows `example_geopolitical.md`.

## Scenario

User asks: "Transforme nossa análise sobre a reforma administrativa num relatório completo, uns 25 páginas, para circular entre assessores."

Parameters inferred: persona editorial, pt-BR, length extended → **mode long-form**, audience informed generalist, stance argumentative.

## Delta 1 — body class

```html
<body class="persona-editorial longform" lang="pt-BR">
```

The `longform` class activates running headers (each `h2` title at the top-right of body pages) and routes `article` to the long-form page template.

## Delta 2 — TOC after the cover

```html
<nav class="toc">
  <div class="toc-title">Sumário</div>
  <ol>
    <li class="toc-l1"><a href="#sec-1">I. O que a reforma efetivamente muda</a></li>
    <li class="toc-l1"><a href="#sec-2">II. A coalizão que a sustenta — e seus limites</a></li>
    <li class="toc-l2"><a href="#sec-2-1">O cálculo dos governadores</a></li>
    <li class="toc-l1"><a href="#sec-3">III. O melhor argumento contrário</a></li>
    <li class="toc-l1"><a href="#sec-4">IV. Cenários e probabilidades</a></li>
    <li class="toc-l1"><a href="#sintese">Síntese</a></li>
    <li class="toc-l1"><a href="#fontes">Fontes e notas</a></li>
  </ol>
</nav>
```

Every `href` resolves to an `id` on the corresponding heading: `<h2 id="sec-1">…</h2>`. Page numbers and dotted leaders are automatic. Note section III: in a long argumentative brief, the strongest opposing case gets a full section, not a paragraph.

## Delta 3 — key assessments after the lede

```html
<div class="key-assessments">
  <span class="ka-label">Avaliações principais</span>
  <ol>
    <li>É provável (55–80%) que o texto-base seja votado na Câmara antes do recesso
        de julho. <span class="confidence">Confiança alta: o calendário foi confirmado
        por três fontes independentes da Mesa e do colégio de líderes.</span></li>
    <li>É improvável (20–45%) que a regra de estabilidade sobreviva sem
        desidratação no Senado.</li>
    <li>É quase certo (95–99%) que o impacto fiscal de curto prazo ficará abaixo
        das projeções oficiais. <span class="confidence">Confiança média: a base de
        cálculo é sólida, mas depende de premissas de adesão não testadas.</span></li>
  </ol>
</div>
```

Likelihood rates the event; confidence rates the evidence — separate sentences, always.

## Delta 4 — footnotes for granular asides

```html
<p>O dispositivo replica a redação da PEC 32/2020<span class="footnote">PEC 32/2020,
art. 37-A na redação da Comissão Especial; a versão atual suprime o §2º.</span>,
mas desloca a vigência…</p>
```

Footnotes carry source minutiae and qualifications — never argument.

## Delta 5 — indicators before the synthesis

```html
<div class="indicators">
  <span class="ind-label">O que mudaria esta avaliação</span>
  <ul>
    <li>A devolução do texto pela CCJ do Senado antes de setembro enfraqueceria a avaliação 1.</li>
    <li>Adesão de dois ou mais governadores do Sudeste ao manifesto contrário enfraqueceria a avaliação 2.</li>
    <li>A publicação da estimativa revisada do impacto fiscal pela IFI reforçaria (ou derrubaria) a avaliação 3.</li>
  </ul>
</div>
```

## Delta 6 — the probability legend with the sources

```html
<p class="uncertainty-note">Os termos de probabilidade neste documento seguem uma
escala fixa: muito improvável (5–20%), improvável (20–45%), chances aproximadamente
iguais (45–55%), provável (55–80%), muito provável (80–95%), quase certo (95–99%).</p>
```

## Validation & render

`validate.py` additionally checks: TOC anchors resolve, no probability+confidence in one sentence, no vague hedges ("talvez", "possivelmente"), ladder terms anchored, legend present, no internal jargon in the text. Render as usual with `templates/render.py`; preview a footnote page and confirm TOC page numbers on two entries.
