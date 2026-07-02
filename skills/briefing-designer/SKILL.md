---
name: briefing-designer
description: >-
  Produces sophisticated PDF briefings and analytical reports with editorial-academic hybrid design, calibrated uncertainty language, and answer-first argument architecture. Use this skill ANY time the user asks for a "briefing", "relatório", "report", "dossiê", "análise em PDF", "executive summary", "policy brief", "white paper", "intelligence report", "investment memo", "strategic note", or any deliverable combining analytical prose, data visualization, and professional editorial layout in PDF — including long-form documents (20-40 pp) with table of contents, footnotes, and running headers. Also trigger when the user wants to convert prior conversation analysis into a polished, downloadable PDF for circulation. Domains: geopolitics, finance, technology, science, public policy, intelligence, strategy consulting, academic synthesis. Four design personas (editorial, academic, governmental, financial); pt-BR, en, es, fr. Do NOT use for slide decks (pptx), spreadsheets (xlsx), or plain Word documents (docx).
---

# Briefing Designer

> **Ambiente:** WeasyPrint e matplotlib já instalados (render testado) — pule o `pip install`.

Produces analytical PDF briefings that feel like a hybrid between *The Economist*, *Foreign Affairs*, and a quality academic journal — and that *argue* like a first-rate analytical shop: answer first, calibrated uncertainty, honest charts. Dense, restrained, typographically refined, built for a reader who values argument over decoration.

## When to use this skill

The defining feature of a briefing is **a substantive analytical argument delivered in editorial form**. Use it for: "Generate a PDF briefing on [topic]", "Turn this into a report / dossiê / relatório / white paper", "Make me a policy brief / investment memo / strategic note", "Create a PDF for circulation about [analysis we just did]", "I need a downloadable analytical document".

Do **not** use for: short notes, simple letters, certificates, slide decks (use `pptx`), spreadsheets (use `xlsx`), generic Word documents (use `docx`).

Upstream/downstream integrations: the `deep-research` skill can power the retrieval layer before writing; the `data-analyst` skill can prepare the analytical layer (EDA, statistics) whose findings this skill renders; the `repercussao-midiatica` skill consumes this skill's templates and scripts directly — **never rename or move `scripts/make_charts.py`, `scripts/validate.py`, `templates/`, or `PERSONAS.md`**, other skills depend on these paths.

## Core philosophy

The reader is sophisticated but may be a layperson in the domain. The document must:

1. **Lead with the answer.** The lede states the central judgment; the body earns it. Never a mystery novel.
2. **Calibrate every uncertainty.** Probabilistic claims use a fixed vocabulary ladder anchored to ranges ("provável (55–80%)"); evidence quality is rated separately as confidence. Plain language always — the analytic discipline is invisible, only its clarity shows.
3. **Reward attention, not skimming.** Long paragraphs are fine. Bullets only inside sidebars or genuinely enumerative content.
4. **Use restraint.** One accent color, one serif, one sans-serif, hierarchy through typography.
5. **Visualize only when the visualization adds an idea.** A chart makes a claim, not decoration. Three charts max in a 10-page brief.
6. **Cite, but don't over-quote.** Direct quotations under 15 words, one per source, paraphrase by default.

## Workflow

Follow this sequence rigorously. Each step is gated — do not skip ahead.

```
Task Progress:
- [ ] 1. Parameters fixed (persona, language, length, audience, stance, mode)
- [ ] 2. Argument architected (central judgment, MECE sections, charts planned)
- [ ] 3. Prose written (calibrated language, answer-first lede)
- [ ] 4. Charts generated (make_charts.py)
- [ ] 5. HTML assembled (template + components)
- [ ] 6. validate.py passing
- [ ] 7. PDF rendered, visually inspected, presented
```

### Step 1 — Establish brief parameters

Fix six parameters. Ask the user only for what cannot be inferred from context.

| Parameter | Options | Default if unspecified |
|---|---|---|
| **Persona** | editorial / academic / governmental / financial | editorial |
| **Language** | pt-BR / en / es / fr | match the conversation |
| **Length** | short (4-6 pp) / standard (8-12 pp) / long (15-25 pp) / extended (25-40 pp) | standard |
| **Audience** | technical specialist / informed generalist / executive | informed generalist |
| **Stance** | descriptive / argumentative / prescriptive | argumentative |
| **Mode** | article (default) / long-form | article; long-form when length ≥ long |

Read `PERSONAS.md` for what each persona implies for design tokens, voice, and structure. **Long-form mode** (≥15 pp) adds: table of contents with dotted leaders and live page numbers, running headers showing the current section, true footnotes at page bottom, and PDF bookmarks — see "Long-form mode" below.

### Step 2 — Architect the argument

Before writing a word, read `TRADECRAFT.md` (always, for argumentative/prescriptive stances; skim Section 6 even for descriptive ones). Then fix on paper:

1. **The central judgment** — one sentence. This becomes the spine of the lede.
2. **The 2–4 major judgments** for the "Avaliações principais" box, each with its ladder term and range.
3. **The section plan** — 3–9 sections, each a *distinct, non-overlapping* reason or dimension; one of them takes the strongest opposing view seriously. Decide which sections get sidebars (1–3 across the brief, never adjacent), pull quotes (1–2), and charts.
4. **Each chart's claim** — what single idea does it encode? Choose the chart *type* from the data relationship using the decision grammar in `CHARTS.md` (deviation → diverging bars; ranking → ordered bars/dot plot; change over time → line/slope; magnitude comparison across two states → dumbbell; correlation → scatter; etc.).
5. **Indicators** — 3–5 observable developments that would change the assessment.

Structural skeleton (article mode):

```
Cover → Article header → Lede (the answer, SCQA-compressed)
  → Avaliações principais box (argumentative/prescriptive)
  → Body sections (numbered, each one reason)
      sidebars / pull quotes / charts where planned
  → "O que mudaria esta avaliação" (indicators)
  → Synthesis section
→ Sources & notes (with the probability-scale legend)
```

Read `COMPONENTS.md` for the component catalog.

### Step 3 — Write the prose

Write to the audience parameter, in the chosen language, in the persona's voice (`PERSONAS.md`). The prose must:

- Open with a **lede paragraph** compressing the whole argument into 4-6 sentences: shared context → what changed → the question it raises → the answer. The reader who stops here has the gist *and the conclusion*.
- Use the **calibrated uncertainty vocabulary** from `TRADECRAFT.md` Section 2 for every probabilistic claim — anchor first uses with ranges, ban "talvez/possivelmente/maybe/perhaps" in analytic claims.
- State **confidence separately from likelihood**, never in the same sentence, only for major judgments, always with a "porque" clause (`TRADECRAFT.md` Section 3).
- Use **numbered sections** with claim-stating titles where the persona allows, 1-3 substantial paragraphs each, with transitions — the brief is one argument, not a list.
- Close with a **synthesis section** that names what is being tested, decided, or revealed.

Avoid: generic AI fillers ("In conclusion", "It's important to note"), hedging that commits to nothing, three parallel same-length clauses (an AI-authorship tic), and any tradecraft jargon in the rendered text (`TRADECRAFT.md` Section 1).

Run the self-checks in `TRADECRAFT.md` Section 7 before moving on.

### Step 4 — Generate the charts

Read `CHARTS.md` for the decision grammar, conventions, and library. Each chart: makes exactly one claim (named in its title), uses only the persona's palette, has a source footer, and is referenced in the prose by number. Generate via `scripts/make_charts.py` — never raw matplotlib; the script enforces design consistency. **Embed the `.svg` output in the HTML** (vector = crisp at any resolution); the 300-dpi PNG is only a fallback for non-PDF contexts. Available: `bar_chart`, `hbar_chart`, `line_chart`, `slope_chart`, `dot_plot`, `stacked_chart`, `dumbbell_chart`, `scatter_chart`.

Never break the scale on bar charts — if the range demands it, use a dumbbell or switch to log scale. No 3D, no shadows, no gradients, no dual axes.

### Step 5 — Assemble the HTML

Use `templates/briefing_template.html` as the scaffold; it imports `templates/design_system.css` (all tokens and component styles — override tokens via the `:root` block to switch persona). Copy component markup from `COMPONENTS.md`; don't invent new components unless the user asks for something not covered.

**Long-form mode** additionally uses (markup and setup in `COMPONENTS.md`, components 14-16):
- `<nav class="toc">` after the cover — entries with `href` anchors get dotted leaders and auto page numbers via `target-counter()`.
- Running headers: section `h2`s feed `string-set: section-title`, displayed at `@top-right` of body pages.
- Footnotes: `<span class="footnote">text</span>` inline — WeasyPrint floats it to the page bottom with an automatic marker. Use for source asides and qualifications too granular for the prose; never for argument.
- PDF bookmarks come free from `bookmark-level` rules already in the CSS.

### Step 6 — Validate (feedback loop)

Run `python scripts/validate.py <file.html>`. It checks copyright quotas (quotes ≤15 words, one per source), language consistency, lede presence and size, chart references — and the analytic-rigor layer: confidence+likelihood mixed in one sentence (error), uncalibrated hedges like "talvez/maybe" in analytic prose (warning), ladder terms used without any range anchor (warning), missing probability-scale legend when ladder terms appear (warning), TOC anchors that don't resolve (error, long-form).

**If validation fails, fix and re-run. Only render when it passes** (warnings need judgment, errors need fixes).

### Step 7 — Render and present

Run `python templates/render.py <input.html> <output.pdf>` (WeasyPrint ≥60; install with `pip install weasyprint --break-system-packages` if missing). Inspect the PDF before presenting — use `pdftoppm` to preview the cover, first body page, a chart page, a footnote page (long-form), and the sources page. Check: no orphaned headings, charts not overflowing margins, footnotes on the right pages, TOC page numbers correct.

Save the PDF to the working directory (or `./outputs/`) and tell the user the path; offer to open it. Keep the post-amble brief — do **not** explain at length what is in the document.

## Persona quick reference

| Persona | Visual signature | Voice |
|---|---|---|
| **editorial** (default) | Economist red `#E3120B`, cream paper, serif drop caps, Roman numerals, red-rule pull quotes | Confident, third-person, thesis-driven, occasional irony |
| **academic** | Deep navy `#1B2A4E`, off-white, no drop caps, abstract block, footnote-style sources | Neutral, hedged, exhaustive citation, longer sentences |
| **governmental** | Slate `#2C3E50` + ochre `#A07000`, classical serif, executive summary box | Impersonal, declarative, structured around recommendations |
| **financial** | Near-black `#0A0E1A`, single accent (orange/red), tighter grid, tables foregrounded | Clipped, quantitative, every claim supports a thesis |

Full specs in `PERSONAS.md`.

## Common failures to avoid

- **Burying the conclusion.** The single worst failure. Lede = answer.
- **Vague hedging.** "Pode ser que talvez" communicates nothing; "improvável (20–45%)" communicates a position.
- **Over-formatting.** No bullets in running text, no bold-for-emphasis sprawl, no header per paragraph.
- **Decoration without information.** No icons, no stray rules, no gradients.
- **Dropcap done wrong.** `::first-letter` + `float: left` crashes WeasyPrint, and an inline-block `::first-letter` inflates the first line's leading. Use the floated `<span class="dropcap">` pattern from `COMPONENTS.md` (component 3) — floats on real elements are safe.
- **Charts with default matplotlib styling.** Always `scripts/make_charts.py`.
- **Breaking bar-chart scales** or using dual axes — use dumbbell/log/indexing instead.
- **Tradecraft jargon leaking** into the rendered text (see `TRADECRAFT.md` Section 1).
- **Copyright violations.** The validator catches most; stay vigilant — paraphrase, don't quote.

## File map

```
briefing-designer/
├── SKILL.md              ← you are here
├── TRADECRAFT.md         ← analytic rigor: uncertainty ladders, confidence, argument architecture
├── REFERENCE.md          ← design-system rationale + long-form print engineering notes
├── PERSONAS.md           ← detailed spec for each of the four personas
├── COMPONENTS.md         ← copy-paste HTML snippets (incl. key-assessments box, TOC, footnotes)
├── CHARTS.md             ← chart decision grammar, conventions, library reference
├── templates/
│   ├── briefing_template.html   ← scaffolded HTML with placeholders (article + long-form blocks)
│   ├── design_system.css        ← tokens + component styles (incl. long-form machinery)
│   └── render.py                ← HTML → PDF via WeasyPrint
├── scripts/
│   ├── make_charts.py           ← parameterized chart generator (8 types)
│   └── validate.py              ← copyright, consistency & analytic-rigor checker
└── examples/
    ├── example_geopolitical.md  ← worked example: intelligence-style brief
    ├── example_financial.md     ← worked example: investment memo
    ├── example_academic.md      ← worked example: research synthesis
    └── example_longform.md      ← worked example: 20+ pp document with TOC/footnotes
```

When in doubt about a component, look at `examples/` — each is a complete end-to-end demonstration.
