# Example: Financial / Investment Memo

This example demonstrates the financial persona applied to a single-name equity research note.

## When to draw on this example

- User asks for "investment memo" / "equity research" / "macro note" / "thesis"
- Audience: portfolio managers, allocators, risk committees
- Output should foreground numbers; tables are part of the argument
- A clear thesis with risks and catalysts is required

## Structural choices to copy

1. **Cover summary table** — the reader's first stop. Ticker, current price, target, recommendation, risk rating.
2. **Page 1 of body opens with a one-sentence thesis** in a callout-datapoint style.
3. **Numbered sections (Arabic), short.** Sentences average 12–18 words.
4. **At least 2 financial tables in body.** Multi-year financials or comp comparisons.
5. **Risks and Catalysts sections at the end** — never collapsed into one. The asymmetry of upside vs. downside *is* the thesis.
6. **No pull quotes.** No drop caps. Tighter, more clinical.
7. **End with `■` mark.**

## Voice notes

- Clipped sentences. Active voice. No hedging vocabulary like "potentially" or "may possibly" — say what you mean.
- Numbers carry the argument. If a sentence does not contain or directly support a number, scrutinize whether it earns its place.
- Past results in declarative tense. Forward views in conditional ("If oil holds above $90, FY26 EPS clears $5.20.").

## Required components

- Cover with summary table
- 1-2 callout-datapoint blocks
- Min 2 financial tables (income statement / multiples / comp set)
- 1-2 charts (price action, valuation, scenario fan)
- "Risks" section
- "Catalysts" section (typically before risks)

## Lede formula

> We initiate coverage of [Company] with a [BUY/HOLD/SELL] rating and a 12-month price target of [$X], implying [X]% upside from current levels. Our thesis rests on [3-5 word summary]. The principal risk is [single most important downside].

## Sample HTML structure

```html
<body class="persona-financial">
  <!-- COVER (cover-financial variant) -->
  <section class="cover cover-financial">
    <div class="cover-vertical-rule"></div>
    <div class="cover-kicker">EQUITY RESEARCH · [SECTOR]</div>
    <h1 class="cover-title">[Company]: [Thesis verb-phrase]</h1>
    <p class="cover-deck">[Single-sentence thesis with verb.]</p>
    <table class="cover-summary-table">...</table>
    <div class="cover-byline">
      <em>Analyst:</em> [Name] &middot; [Date]
    </div>
  </section>

  <!-- BODY -->
  <div class="article-header">
    <div class="kicker">RESEARCH · [DATE]</div>
    <h1>[Thesis as a question or claim]</h1>
  </div>

  <p class="lede">[Lede formula above]</p>

  <h2>Thesis in three points</h2>
  <p>[Para 1]</p>
  <div class="callout callout-datapoint">
    <div class="datapoint-number">+47%</div>
    <div class="datapoint-label">implied 12-month upside to our base case</div>
  </div>
  <p>[Para 2]</p>

  <h2>Financial trajectory</h2>
  <p>[Para]</p>
  <table class="financial-table">[multi-year financials]</table>

  <h2>Valuation</h2>
  <table class="financial-table">[multiples vs comps]</table>
  <figure class="chart-wrap">[scenario fan chart]</figure>

  <h2>Catalysts</h2>
  <p>[Specific events with dates]</p>

  <h2>Risks</h2>
  <p>[Specific risks, ordered by severity]</p>

  <div class="end-mark">■</div>

  <div class="sources">[disclosures + sources]</div>
</body>
```
