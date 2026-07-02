# Design System — Rationale and Tokens

The briefing designer enforces a coherent design language. This document explains *why* — every choice has a reason. When you find yourself wanting to override a default, read the rationale first.

## Table of contents

1. Type system
2. Color system
3. Grid and rhythm
4. Hierarchy
5. Editorial conventions
6. Why WeasyPrint

---

## 1. Type system

### Two families maximum

The brief uses one serif (for body and display) and one sans-serif (for kickers, captions, table headers). That's it. Three families confuses the eye. One family bores it.

**Default serif: Lora.** It's available in the Linux container, supports the full Latin extended range (essential for Portuguese diacritics), has both regular and italic variable fonts, and reads beautifully at body size. Lora's slightly humanist character makes it feel less corporate than Source Serif Pro and less academic than Merriweather. If unavailable, fall back to `Liberation Serif` or `DejaVu Serif`.

**Default sans-serif: Liberation Sans.** Universally available, similar metrics to Helvetica/Arial. Used only for: kicker labels, sidebar titles, chart axis labels, captions, page numbers, and uppercase metadata. Never for body.

### Size scale

A modular scale with five steps. Resist the urge to introduce intermediate sizes.

| Use | Size | Line height |
|---|---|---|
| Cover title | 44pt | 1.05 |
| Cover deck (subtitle) | 16pt italic | 1.35 |
| Article title (after cover) | 18pt | 1.2 |
| Section heading (h2) | 13.5pt bold | 1.2 |
| Subsection (h3) | 11pt italic bold | 1.3 |
| Pull quote | 14pt italic | 1.35 |
| Lede paragraph | 11.5pt | 1.5 |
| Body | 10.5pt | 1.45 |
| Sidebar / caption | 9.5pt | 1.45 |
| Source list | 8pt | 1.45 |
| Page footer | 8.5pt italic | 1 |

### Why justified text

Body text is justified with hyphenation enabled. This is non-negotiable for editorial feel. Ragged-right reads as a memo or blog post; justified reads as an *article*. The CSS sets `hyphens: auto` which works for `lang="pt-BR"` and `lang="en"` in WeasyPrint.

### Italics carry meaning

Italics are reserved for: foreign terms, publication titles, emphasis (sparingly), and pull quotes. Never use them for "tone" or decoration. Bold is even more restricted — reserve it for genuine emphasis on a quantitative claim or a critical noun, no more than once or twice per page.

---

## 2. Color system

Each persona has a palette of exactly six colors:

```
--accent       (the one bright color, used for kickers, drop caps, h2-numerals)
--ink          (near-black for body text)
--secondary    (a muted second accent, used in charts and rules)
--muted        (cool grey for metadata, captions)
--surface      (off-white background)
--paper        (the page color, very slightly tinted)
```

Why a tinted background. Pure white (`#FFFFFF`) on a printed PDF page reads cold and cheap. A barely-warm off-white (`#FEFCF8` for editorial, `#FAFAF7` for academic) signals quality without being noticeable. The tint must be ≤2% saturation — the reader should not consciously perceive it.

Why one accent. Multi-color schemes look like Microsoft templates. Editorial publications use one signature color (Economist red, FT salmon, NYT black-and-white) and let typography do the work. The accent is used: drop caps, kicker labels, section numerals, pull-quote rules, chart "primary" series, callout backgrounds.

Why no gradients. Gradients are decoration without meaning. Briefings encode meaning in every visual choice; gradients fail this test.

See `PERSONAS.md` for the exact hex values per persona.

---

## 3. Grid and rhythm

### Page

A4 portrait, 22mm top, 22mm bottom, 20mm left, 20mm right. This produces a text block of roughly 170mm × 213mm — slightly narrower than US Letter convention, which suits Lora's wider counters and the typical European reading culture.

### Vertical rhythm

The base unit is the body line height (10.5pt × 1.45 ≈ 15pt). All vertical spacing is a multiple:

- Paragraph spacing: 3mm (about 1 unit, no first-line indent)
- After h3: 2mm
- Before h3: 5mm
- Before h2: 9mm
- After h2: 3mm
- Around figures and sidebars: 5-6mm
- Around pull quotes: 6mm

This rhythm is what makes the page feel calm. Skipping it makes the page feel restless even when the user can't articulate why.

### First-line indents vs. paragraph spacing

Use paragraph spacing (3mm), not first-line indents. Indents belong in fiction and academic monographs; spacing belongs in editorial layout. Don't mix.

### Orphans and widows

Set `orphans: 3; widows: 3;`. This prevents single lines from being stranded at page tops or bottoms. It costs the renderer a small amount of layout effort. Worth it.

---

## 4. Hierarchy

The reader scans down the page in roughly this order:

1. Page kicker (if present) — "Briefing · 04 maio 2026"
2. Article title — large display
3. Lede paragraph — distinguished by the dropcap and slightly larger size
4. Section headings (Roman numerals)
5. Subsection headings (italic)
6. Body
7. Sidebars and pull quotes (peripheral vision)

If the hierarchy is right, a reader who only reads the first sentence of every paragraph plus the headings should still understand the argument. Test this on every brief.

### The Roman-numeral signature

The default editorial persona numbers sections in Roman numerals (`I.`, `II.`, `III.`...). This is a deliberate signal: it says "this is an essay, not a memo." The Romans also break up the dense `<h2>` text and provide a visual anchor for citing sections in later notes.

In the financial persona, switch to Arabic numerals (`1.`, `2.`...). In the academic persona, drop section numbering altogether and let the heading text do the work. In the governmental persona, use lettered sections (`A.`, `B.`...) which feels report-like.

---

## 5. Editorial conventions

### The kicker

A kicker is the small uppercase line above a title. It tells the reader what kind of content this is: "Briefing · Estratégia", "Investment Memo · Fixed Income", "Policy Note · Climate". Always letter-spaced (0.18em), in the accent color, in sans-serif at 8-9pt. Never put a kicker in italic or bold — it's already loud enough from the letterspacing.

### The deck

The deck is the italic line under a major title. It compresses the entire piece into one sentence with a verb. Do not write decks like "An analysis of X". Write decks like "Why the Project Freedom announcement is more cautious than its rhetoric suggests."

### The lede

The first paragraph of the article (after the title block). Distinguished by:
- Slightly larger size (11.5pt instead of 10.5)
- A drop cap on the first letter
- More leading

The lede tells the reader the entire thesis. It's the most important paragraph in the brief.

### The dropcap

Two lines tall, in the accent color, font-weight 700, no background — a true drop cap with the text wrapping around it. Implementation detail that matters: WeasyPrint crashes on `::first-letter { float: left }`, and the workaround of an inline-block `::first-letter` inflates the first line's box to the cap's height, visibly breaking the body's leading rhythm. The robust pattern is a real `<span class="dropcap">` floated left (floats on actual elements are fully supported); `line-height: 0.78` on the span sinks the glyph across two text lines.

### The pull quote

Used sparingly — one or two per brief. A pull quote is a sentence pulled from the body that crystallizes the argument visually. It's set in italic, 14pt, with a 3pt accent rule on the left, and an attribution line in small caps below. Don't fabricate pull quotes; pull them from your own prose.

### The sidebar

A sidebar is a self-contained box of supplementary information that supports but doesn't disrupt the argument. Examples: "What's in the proposal", "Glossary of terms", "By the numbers", "Timeline of events". Always tagged with a small uppercase title in the accent color, set in a tinted background (`#F4EFE5` for editorial, varies by persona), with a left accent rule.

Sidebars use 9.5pt body. Bullets *are* allowed inside sidebars — that's their job. But don't write more than 5-7 bullets; if you need more, you have a section, not a sidebar.

### The pull-quote / sidebar split

If you have a sentence to amplify, use a pull quote. If you have structured supplementary info, use a sidebar. Don't put bullets in pull quotes.

### Page furniture

Every page after the cover shows: a footer with the brief title and date on the left, page X of Y on the right. Both in muted color, italic, 8.5pt. Nothing else. The cover has no footer.

### Endmark

The brief ends with a small ornament — `❦` (floral heart) or `§` (silcrow) for editorial, `■` (filled square) for financial, none for academic. This signals "the body is done, what follows is apparatus."

---

## 6. Why WeasyPrint

We use WeasyPrint because:

- It accepts standard HTML/CSS3, so the same source can be inspected in a browser during development.
- It supports `@page` directives, page counters, named string sets, page-break controls, and CSS Paged Media — features that LibreOffice / docx pipelines lack.
- It renders consistently from the command line, no GUI dependencies.
- It produces small, properly-tagged PDFs.

WeasyPrint limitations to know:

- No support for `::first-letter { float: left; }` — crashes the layout engine. And a non-floated oversized `::first-letter` inflates the first line's leading. Use the floated `<span class="dropcap">` pattern in `design_system.css` instead.
- No JavaScript execution. All charts must be pre-rendered as PNG/SVG.
- Limited support for some advanced CSS Grid features. Stick to flexbox for layout.
- Variable fonts work but advanced font features (`font-variation-settings`) may not. Use static font weights when possible.

The renderer is invoked via `templates/render.py`. Don't reinvent it — the script handles edge cases (font loading, base URL for images, output validation) that bare `weasyprint.HTML().write_pdf()` does not.

---

## 7. Long-form print engineering (v2)

Documents of 15+ pages stop being articles and become *publications*: the reader navigates instead of reading linearly. Long-form mode adds the navigation apparatus using WeasyPrint's CSS paged-media support. Everything below already lives in `design_system.css` section 13; this is the rationale and the gotchas.

### What the machinery does

- **Table of contents.** `nav.toc a::after` uses `leader(dotted)` to fill the line and `target-counter(attr(href), page)` to print the *live* page number of each anchor — the numbers update automatically when content reflows. This is why anchors must resolve: a dangling `href` renders a blank where the number should be (the validator catches this).
- **Running headers.** `string-set: section-title content()` on `h2` captures each section title into a named string; `@top-right { content: string(section-title) }` prints the *current* section at the top of each page. Scope is "the page of the element and subsequent pages," so a page containing two h2s shows the latest one.
- **Footnotes.** `float: footnote` moves the span's content to the page-bottom footnote area; `::footnote-call` and `::footnote-marker` style the in-text number and the note's number. The `@footnote` area gets a hairline top rule. Numbering is automatic via the `footnote` counter.
- **PDF bookmarks.** `bookmark-level` on the cover title, h2 and h3 builds the PDF outline panel for free, in any mode.

### Gotchas learned the hard way

- **`line-height: 0` on `::footnote-call`** — without it, the superscript call stretches the host line and creates uneven leading wherever a footnote appears.
- **Don't use `footnote-policy: line`.** It sounds attractive (keeps call and note on the same page) but in practice it forces the call's line — and following blocks — to the next page whenever the footnote area is tight, producing half-empty pages. A note occasionally spilling to the following page is standard book typography; accept it. If a specific spill bothers you, move the call a sentence earlier or shorten the note.
- **Named page for the body.** Long-form routes `article` to `@page longform-body` so the running header only appears on body pages — never on the cover or the TOC. Don't put `@top-right` on the global `@page`.
- **Footnotes belong inline.** Write the note's text exactly where the call should appear. Moving the spans to the end of the file detaches calls from their pages.
- **Keep the TOC selective.** `target-counter()` is cheap, but a TOC listing every h3 reads like an outline dump. Sections always; subsections only when a reader would plausibly jump to them.
- **`leader()` support is partial in WeasyPrint** (the function works in `content` for the TOC pattern above; exotic combinations may not). Stick to the documented pattern.
- **Page-count sanity.** After rendering, check that TOC numbers match reality on a couple of entries — a stale anchor id after renaming sections is the classic failure.
