# Charts — Decision Grammar, Conventions, Library

Charts in a briefing are arguments compressed into shape. A chart that doesn't make a claim shouldn't exist. This document covers (a) how to *choose* a chart from the data relationship, (b) the conventions that keep charts coherent, and (c) how to use `scripts/make_charts.py`.

---

## Decision grammar — choose the chart from the relationship

Before picking a chart type, name the **relationship in the data** that carries the claim. Each relationship has one or two preferred forms in this system (adapted from the data-journalism practice of organizing chart choice by relationship, not by aesthetics):

| Relationship the claim rests on | Preferred form | Function | Notes |
|---|---|---|---|
| **Change over time** — trajectory, growth, rates | line | `line_chart` | ≥5 points; ≤4 series; fewer points → bars |
| **Ranking** — order matters more than value | ordered horizontal bars or dot plot | `hbar_chart`, `dot_plot` | always sorted; never alphabetical when ranking is the claim |
| **Magnitude** — absolute size comparison, few categories | vertical bars | `bar_chart` | zero-based axis, no exceptions |
| **Two states per item** — before/after, A vs B, gap | dumbbell | `dumbbell_chart` | the editorial replacement for broken-scale bars and paired-bar clutter |
| **Movement between two points in time** — who rose, who fell | slope | `slope_chart` | more revealing than a bar of differences |
| **Correlation** — does X move with Y | scatter | `scatter_chart` | annotate the pattern; readers assume causality unless told otherwise — say so in the subtitle if the link is not causal |
| **Part-to-whole over time** — composition is the claim | stacked area/bar | `stacked_chart` | only when composition itself is the claim; stacking hides series trends |
| **Deviation** — above/below a reference (target, zero, average) | diverging bars from the baseline | `bar_chart` with negatives | accent for negative, secondary for positive (fixed semantics) |
| **Distribution / outliers** | scatter or dot plot with intervals | `scatter_chart`, `dot_plot` | histograms rarely earn their place in a brief; consider a sentence instead |

If the claim doesn't map to any row, the right "chart" is probably an annotated table (financial persona) or a sentence. If two relationships compete, make two charts or pick the one the *title-claim* expresses.

---

## Conventions

### One chart, one claim

Every chart's title should be a claim, not a description. Compare:

| Bad (description) | Good (claim) |
|---|---|
| "Costs by scenario" | "Costs diverge by two orders of magnitude" |
| "Inflation by year" | "Inflation has stalled above target since 2024" |
| "Survey results" | "Voters trust banks less than the army" |

### Persona palette only

Each chart uses **at most three colors from the active persona's palette**: `--accent` (the primary series), `--secondary` (the comparison series), and `--muted` (for context, gridlines, baselines). Don't introduce new colors. Don't use color rainbows. Don't use rainbow gradients.

### Labels on, legend often off

Direct labeling beats legends. If a chart has only two series, label them at the end of each line / top of each bar instead of using a legend. Legends only when 3+ series make direct labeling impossible.

### No 3D, no shadows, no gradients

3D charts compress information loss. Shadows decorate without informing. Gradients confuse comparison. None of them.

### Source attribution

Every chart has a footer line with source attribution, in muted color, italic, 8pt. Format:

```
Fonte: [primary source]. Notas: [if any].
```

If the chart is the result of original analysis, write "Análise própria com base em [data sources]." or in English "Author's analysis based on [data sources]."

### Logarithmic when range > 100x

If the data spans more than two orders of magnitude (e.g., one bar is 0.4 and another is 400), use a log scale. Linear scales hide small values.

### Never break the scale on bars; never use dual axes

A bar's length *is* its value — truncating the axis lies about the ratio. If small differences matter on large values, switch forms: a **dumbbell** shows the two values as points and the gap as a line, which is honest at any zoom; alternatively, index the series (=100 at baseline) or go log. Dual-axis charts are banned outright: the implied correlation is an artifact of axis choice. If two variables must share a figure, index both to a common base or split into stacked panels.

### Negative numbers

Use the persona's accent (red in editorial, orange in financial) for negatives. Reserve `--secondary` for the positive series. This is one of the few places color encoding has fixed semantics.

---

## Supported chart types

### 1. Bar chart (vertical)

For comparing magnitudes across discrete categories. The most common chart type.

**When to use:** Compare two or more discrete values (cost A vs cost B, region X vs region Y, scenario i vs scenario ii).

**When NOT to use:** Time series (use line chart). Continuous data (use scatter or histogram).

### 2. Bar chart (horizontal)

For comparing categories with long labels, or when there are 5+ items to rank.

**When to use:** Probability distributions over named scenarios; rankings; categorical comparisons with descriptive labels.

### 3. Line chart

For time series. The default for "X over time."

**When to use:** Anything with a time axis. Trajectories, growth, rates over multiple periods.

**Avoid:** Lines with fewer than 5 data points (use a bar instead). More than 4 series (the chart becomes spaghetti).

### 4. Stacked bar / area

For composition that sums to 100%, evolving over time.

**When to use:** Market share over time, budget composition by category.

**Caution:** Stacked charts hide individual series trends. Only use when the *composition* itself is the claim.

### 5. Scatter plot

For correlation or distribution.

**When to use:** Showing relationship between two continuous variables; identifying outliers.

### 6. Slope chart

Two columns of points, lines connecting them. Compares the same items across two time points or conditions.

**When to use:** "Which items moved most between t=0 and t=1?" Often more revealing than a bar of differences.

### 7. Dot plot (Cleveland)

Like a horizontal bar but with a dot at the value, often with a leading line.

**When to use:** Ranking many items where small differences matter; expressing intervals (lo and hi dots connected by a line).

### 8. Annotated table

Sometimes the right "chart" is a table with conditional formatting. Numbers colored by sign, cells highlighted by importance. The financial persona uses these heavily.

---

## Using `make_charts.py`

The script exposes a function for each chart type, with the persona's tokens applied automatically. Example:

```python
from scripts.make_charts import bar_chart, save

fig = bar_chart(
    persona="editorial",
    title="Custo militar diverge em duas ordens de grandeza",
    categories=["1 semana", "1 mês", "3 meses", "6 meses"],
    series=[
        {"name": "Cenário (i): Irã não escala", "values": [0.4, 1.0, 2.5, 5.0], "color": "secondary"},
        {"name": "Cenário (ii): retomada da guerra", "values": [10, 50, 150, 400], "color": "accent"},
    ],
    y_label="US$ bilhões — escala log",
    log_y=True,
    source="Análise própria com base em CNAS, CBO, Pentágono e WarCosts.org.",
)
save(fig, "/path/to/output", formats=["svg", "png"])
```

Available functions in `make_charts.py`:

| Function | Purpose |
|---|---|
| `bar_chart()` | Vertical bars, 1–N series (incl. diverging/deviation) |
| `hbar_chart()` | Horizontal bars (good for ranked items) |
| `line_chart()` | Time series, 1–4 lines |
| `stacked_chart()` | Stacked area or bar |
| `slope_chart()` | Slope diagram between two columns |
| `dot_plot()` | Cleveland dot plot |
| `dumbbell_chart()` | Two values per category joined by a line (before/after, A vs B) |
| `scatter_chart()` | Scatter / correlation, optional point labels |

### Standard parameters

All functions accept:

- `persona` — `"editorial"` (default), `"academic"`, `"governmental"`, `"financial"`
- `title` — the claim
- `subtitle` — optional secondary line under the title
- `source` — attribution footer
- `figsize` — defaults to `(7.5, 4.2)` which fits the brief column width
- `language` — `"pt"`, `"en"`, `"es"`, `"fr"` (controls decimal separator, thousands separator)

### Color references

Series colors are referenced by token name:

- `"accent"` — the primary series color
- `"secondary"` — the comparison series
- `"muted"` — context, baselines

Don't pass hex codes directly; the token system ensures persona consistency.

### Embed the SVG, not the PNG

In the briefing HTML, reference the `.svg` file (`<img src="chart1.svg">`). Vector charts render crisp at any print resolution and zoom level; raster PNGs blur when WeasyPrint scales them to the column width. Text in the SVGs is pre-converted to paths, so no font availability issues at render time. Keep the 300-dpi PNG only as a fallback for contexts that can't take SVG (chat previews, slide pastes).

---

## Anti-patterns to refuse

If the user asks for any of these, push back:

- **Pie charts.** Banned. They're notoriously hard to read and compare. Replace with horizontal bars.
- **3D anything.** Banned for the reasons above.
- **Charts with 6+ series.** Suggest splitting into small multiples instead.
- **Decorative charts that don't make a claim.** Ask the user what the chart is meant to communicate. If they can't say, the chart shouldn't exist.

A briefing reader's time is the scarcest resource in the system. Every chart must respect it.
