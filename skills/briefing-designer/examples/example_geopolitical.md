# Example: Geopolitical Briefing

This example shows the editorial persona applied to a geopolitical analysis. It is the canonical demonstration of the skill.

## When to draw on this example

- User asks for an "intelligence brief" / "geopolitical analysis"
- The audience is informed generalists (think *Foreign Affairs* readership)
- The argument is causal, not just descriptive
- Probability or scenario analysis is involved

## Structural choices to copy

1. **Open with what the news *is*, then immediately what the news *means*.** First section "The announcement and what it actually is" — the gap between rhetoric and operational reality is the structural hook.
2. **Numbered sections in Roman.** Signals essay, not memo.
3. **One sidebar of "by the numbers"** to anchor the discussion in concrete figures.
4. **One pull quote** from an external expert, used to crystallize the central asymmetry.
5. **Charts each make one claim:** (a) cost asymmetry between two scenarios; (b) magazine drain illustrating the structural cost problem; (c) probability distribution of outcomes.
6. **Synthesis section names what is being tested**, not just what happened.
7. **Sources organized by topic group**, not chronologically.

## Voice notes

- Confident assertions, but carefully hedged with attribution where needed.
- Allow a sentence of dry irony per ~3 pages (no more).
- End with a sentence that gestures at structural significance ("the last act of an order, not the first of a new one").

## Lede formula

> [Subject] [verb of news event] [object]. The [official narrative] is [characterization]; the [actual operational reality] is [contrasting characterization]. The difference between the two narratives is the cere of the analysis that follows.

## Sample HTML structure

```html
<body class="persona-editorial">
  <!-- COVER (cover-editorial variant) -->

  <!-- ARTICLE -->
  <div class="article-header">
    <div class="kicker">BRIEFING · [DATE]</div>
    <h1>Project [name]: the last act of an old order, or the first of a new one?</h1>
  </div>

  <p class="lede">[60-200 word thesis]</p>

  <h2>The announcement and what it actually is</h2>
  <p>[2 paragraphs of contrast]</p>
  <aside class="sidebar sidebar-numbers">
    <div class="sidebar-title">By the numbers</div>
    <ul>...</ul>
  </aside>

  <h2>The reaction and the underlying context</h2>
  <p>[2 paragraphs setting up the strategic environment]</p>

  <h2>Cost scenarios — from gesture to war</h2>
  <p>[Establish baseline parameters first]</p>
  <h3>Scenario (i)</h3>
  <p>...</p>
  <h3>Scenario (ii)</h3>
  <p>...</p>
  <figure class="chart-wrap">...</figure>

  <h2>Military feasibility</h2>
  <p>...</p>
  <figure class="chart-wrap">[asymmetry chart]</figure>

  <h2>Domestic politics</h2>
  <h2>Global politics</h2>
  <h2>Economic feasibility</h2>

  <h2>Likely outcomes (90-day horizon)</h2>
  <figure class="chart-wrap">[probability distribution]</figure>
  <h3>Outcome A — ~40%</h3>
  <h3>Outcome B — ~30%</h3>
  <h3>Outcome C — ~20%</h3>
  <h3>Outcome D — ~10%</h3>

  <h2>Synthesis</h2>
  <p>[What is being tested]</p>
  <p>[What the most likely combinations imply]</p>
  <p>[Implications for [user's home country / interest]]</p>

  <div class="end-mark">❦</div>

  <div class="sources">...</div>
</body>
```
