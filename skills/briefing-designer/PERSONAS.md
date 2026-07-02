# Personas — Design Specifications

Four personas cover the great majority of analytical-briefing use cases. Each persona is a complete package of color tokens, typographic adjustments, voice conventions, and structural defaults. Pick one and commit to it — don't mix.

---

## Persona 1: Editorial (default)

The editorial persona is the project's default. It draws on *The Economist*, *Foreign Affairs*, *The New Yorker*, and the long-form analytical magazine tradition. Use it whenever the audience is an informed generalist who wants an argument, not a fact dump.

### Color tokens

```css
:root {
  --accent:    #E3120B;   /* Economist red */
  --ink:       #121212;   /* Near-black body */
  --secondary: #006BA2;   /* Steel blue, secondary chart series */
  --muted:     #758D99;   /* Cool grey for metadata */
  --surface:   #F4EFE5;   /* Sidebar tint, cream */
  --paper:     #FEFCF8;   /* Page background, very warm off-white */
  --rule:      #2A2A2A;   /* Hairline rules */
}
```

### Typography

- Body: Lora 10.5pt / 1.45, justified, hyphenation on
- Display: Lora 700 (headings, dropcap)
- Sans: Liberation Sans for kickers, captions, axis labels
- Section numbering: **Roman numerals** in accent color (`I.`, `II.`...)
- Dropcap: 32pt, accent color, on lede paragraph only

### Voice

- Third person, confident, thesis-driven.
- Allow occasional irony, especially in transitions.
- Use foreign terms (Latin, French, German) sparingly when they capture a concept English doesn't have a single word for. Italicize them.
- The closing section is called "Síntese" (pt-BR) / "Synthesis" (en) / "Conclusión" (es) / "Synthèse" (fr).
- Endmark: `❦`

### Cover

- 12pt accent rule across the top of the page
- Kicker: "BRIEFING ESTRATÉGICO · [TÓPICO]"
- Title: very large (44pt) display serif
- Deck: italic deck of one or two sentences
- Hairline rule under the deck
- Byline block: "Análise estratégica" / location / date / horizon
- Abstract block at the bottom, 11pt, with a small uppercase "RESUMO" / "ABSTRACT" label

### When NOT to use

- Quantitative-heavy financial analysis where every page has tables (use Financial)
- Peer-reviewed-style research synthesis (use Academic)
- Government policy memos with statutory recommendations (use Governmental)

---

## Persona 2: Academic

Modeled on journals like *International Security*, *American Political Science Review*, and the more readable end of academic publishing. Use when the audience expects extensive citation, hedged claims, and exhaustive context.

### Color tokens

```css
:root {
  --accent:    #1B2A4E;   /* Deep navy */
  --ink:       #1A1A1A;
  --secondary: #6B7280;   /* Slate */
  --muted:     #6B7280;
  --surface:   #EAE7E0;   /* Warm beige */
  --paper:     #FAFAF7;   /* Off-white */
  --rule:      #1A1A1A;
}
```

### Typography

- Body: Lora 10.5pt / 1.5 (slightly more leading), justified
- No dropcap on the lede (academic convention prefers a clean opening)
- Section headings: numbered with Arabic (`1.`, `2.`...) or unnumbered, never Roman
- Subsection: bold roman, not italic
- Footnote-style references in the text (superscript numerals)
- Sans: Liberation Sans only for figure captions

### Voice

- Neutral third person, hedged.
- Sentences average 22-30 words.
- Methodological caveats early in the brief.
- Closing section called "Conclusion" / "Conclusão" / "Conclusión" / "Conclusion".
- No endmark, or a discreet `§`

### Cover

- No top accent rule; instead, a large `§` ornament in navy
- Kicker line in small caps: "WORKING PAPER · [INSTITUTION]"
- Title: 36pt, serif, weight 600 (not 700 — academic restraint)
- Deck: roman, not italic, 14pt
- Author block with affiliation
- Abstract: 250-word maximum, justified, with a small "ABSTRACT" header
- A keywords line below the abstract: "Keywords: X, Y, Z."

### Sources convention

In academic persona, sources are numbered footnotes in Chicago author-date or APA style, not the prose-style "Notas e fontes" of editorial. Each in-text citation gets a superscript that maps to a numbered note at the end.

---

## Persona 3: Governmental

For policy briefs, ministerial notes, regulatory analysis. Models include UK Cabinet Office briefings, OECD policy papers, World Bank policy notes. Use when the audience is officialdom and the brief might inform a decision.

### Color tokens

```css
:root {
  --accent:    #2C3E50;   /* Dark slate */
  --ink:       #1A1A1A;
  --secondary: #A07000;   /* Ochre (the second accent) */
  --muted:     #6B6B6B;
  --surface:   #F0EDE5;   /* Warm parchment */
  --paper:     #FCFAF5;   /* Light parchment */
  --rule:      #1A1A1A;
}
```

### Typography

- Body: Lora 10.5pt / 1.45, justified
- Display: Lora 700, slightly tighter tracking on headings
- Section numbering: lettered (`A.`, `B.`, `C.`)
- Subsection: numbered (`A.1`, `A.2`)
- Sans: Liberation Sans for the prominent **Executive Summary** box and **Recommendations** box

### Voice

- Third person, declarative, no irony.
- Recommendations stated in indicative future ("The government should...").
- The closing section is always called "Recommendations" / "Recomendações" / "Recomendaciones" / "Recommandations" and is structured as a numbered list.
- No endmark.

### Cover

- A double rule (3pt + 0.5pt) across the top in slate
- A coat-of-arms-style ornament if appropriate (or just an institutional name)
- Title: 38pt, serif, weight 700
- Deck: italic
- A "Classification" line ("UNCLASSIFIED" / "RESTRICTED" / etc.) in small caps if relevant
- An Executive Summary block on the cover, 200-400 words, in a tinted box

### Required sections

Governmental briefs MUST contain:
- Executive Summary (front, in box)
- Background / Context
- Analysis
- Options (when prescriptive)
- Recommendations
- Annex / Sources

---

## Persona 4: Financial

For investment memos, equity research, sell-side notes, and economic forecasts. Models include Bloomberg Intelligence, JP Morgan research, Bridgewater daily observations. The defining feature: every claim must support a thesis, and tables are foregrounded.

### Color tokens

```css
:root {
  --accent:    #FF6B00;   /* Bloomberg-ish orange */
  --ink:       #0A0E1A;   /* Near-black with a blue tint */
  --secondary: #00A86B;   /* Green for positive numbers */
  --muted:     #6B7280;
  --surface:   #F5F5F2;
  --paper:     #FFFFFF;   /* Clean white — tables look better on white */
  --rule:      #0A0E1A;
}
```

Note: financial is the only persona on pure white. The others use tinted paper because they're meant to be read; financial briefs are scanned and parsed.

### Typography

- Body: Lora 10pt / 1.4 (tighter than other personas)
- Display: Lora 700, condensed feel
- Section numbering: Arabic (`1.`, `2.`)
- Tables foregrounded — table styling more elaborate than other personas
- Sans: Liberation Sans for ALL numerical content (prices, ratios, percentages) — numerals in monospaced sans look more authoritative

### Voice

- Clipped, declarative.
- Sentences average 12-18 words.
- "Long X / Short Y" framing where appropriate.
- The brief states a thesis on page 1, supports it for the body, then lists risks at the end.
- Closing section called "Risks" / "Riscos" + "Catalysts" / "Catalisadores".
- Endmark: `■`

### Cover

- A thick (16pt) accent rule on the LEFT side of the page (vertical, not horizontal)
- Kicker: "EQUITY RESEARCH · [SECTOR]" or "MACRO NOTE · [REGION]"
- Title: 32pt, weight 700
- Deck: roman, not italic, 13pt
- A table on the cover summarizing the thesis: ticker, current price, target, recommendation, risk rating
- Date and analyst name in small caps

### Required components

Financial briefs heavily feature **tables**. The brief should have at least 2 tables (cover summary + one in-body), and frequently a chart with quantitative axes. See `COMPONENTS.md` for the financial table style.

---

## Choosing the persona

Use this decision tree:

1. **Is the deliverable for a peer-reviewed-style audience that expects citations and methodological hedging?** → Academic
2. **Will this inform an official decision, with formal recommendations?** → Governmental
3. **Is the primary content a quantitative thesis with risks/catalysts, for a financial audience?** → Financial
4. **Otherwise** → Editorial

If genuinely unsure, ask the user. But don't ask if context already implies the answer.
