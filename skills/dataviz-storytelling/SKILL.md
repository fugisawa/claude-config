---
name: dataviz-storytelling
description: Use when designing or critiquing charts, plots, or dashboards in Python (Altair, Plotly, matplotlib, Streamlit) — choosing a chart type, reducing clutter, visualizing forecasts/uncertainty/calibration or model-vs-market, direct-labeling vs legends, colorblind-safe and light/dark-safe palettes, or making a visualization self-evident and not "poluído".
---

# Dataviz & Storytelling

## Overview

Encode the **one thing that matters** with the strongest perceptual channel, delete everything else, and show uncertainty. Core principle: **position > length > hue > area** for accuracy — pick one channel for the key dimension; every extra mark must earn its ink.

## When to use

- Choosing or critiquing a chart for a Python data app (Streamlit dashboard, report).
- "This is cluttered / confusing / poluído" — making a view self-evident.
- Visualizing forecasts: uncertainty bands, reliability/calibration, model-vs-market, over/under-performance.
- Palette/theming decisions (colorblind-safe, light + dark).

**Not for:** Streamlit mechanics → `streamlit-apps`. Model/metric choices → `forecasting-calibration`.

## Principles

1. **Maximize data-ink.** Remove gridlines, borders, heavy ticks unless they carry information.
2. **One preattentive channel for the key dimension.** Two simultaneous encodings = noise, not signal.
3. **Color earns its place** by encoding a variable or highlighting an outlier — never decoration. Max 5–6 categorical hues, then facet.
4. **Direct-label, don't legend.** Label series at their endpoints; legends only past ~4 colliding series.
5. **Aligned bars beat a table of numbers** for comparison. Never a pie/donut past 3 slices.
6. **Small multiples** over one overloaded chart when you have >3–4 series.
7. **Show uncertainty explicitly** — bands/intervals, not a footnote. A forecast without a range lies by omission.
8. **Redundant encoding for accessibility** — shape/linestyle/label alongside color (also the colorblind fix).
9. **Annotate to one insight.** Write zero annotations until you know the single thing the viewer should leave with.

## Chart-selection decision table

| Need | Chart | Key note |
|---|---|---|
| Compare N categories (≤10) | horizontal **sorted bar** | sort desc, label bars directly |
| Categories over time | small-multiple lines / grouped bar | avoid spaghetti past 4 series |
| One distribution | histogram / KDE | mark median with a rule |
| Compare distributions | overlapping KDE / violin | boxplots hide shape |
| Relationship | scatter | add **y=x** when comparing predicted vs actual |
| Part-to-whole (≤3) | normalized stacked bar | pie only if gestalt composition matters |
| Trend | single-axis line | **dual-axis almost always misleads** |
| Trend + uncertainty | line + **confidence band** | band opacity ≈ 0.2, solid central line |
| Forecast range | **fan**: line + nested quantile bands | 50/80/95% widening |
| Model vs market/actual | **scatter + y=x diagonal** | above diagonal = over-prediction |
| Over/under-performance | **diverging bar** (actual − expected) | prominent zero reference |
| Probabilities | sorted horizontal **probability bar** | sort by predicted prob desc |
| Calibration | **reliability diagram** + count histogram | reference diagonal = perfect |

## Library guidance (in Streamlit)

| Use | Pick | Why |
|---|---|---|
| Statistical / declarative / small multiples / forecast bands | **Altair** | `st.altair_chart(c, theme="streamlit")` auto-adapts to light/dark |
| Interactivity (range sliders, dropdowns), model-vs-actual scatter, maps | **Plotly** | set `template="plotly_white"`/`"plotly_dark"` to match theme |
| Static, pixel-perfect, calibration plots (`CalibrationDisplay`) | **matplotlib** | always `plt.close(fig)` to avoid leaks |

Code recipes (fan chart, model-vs-market scatter, perf delta, reliability, probability bars): see `forecast-viz.md`.

## Common mistakes

- **Altair `configure_*` + Streamlit theme** silently override Streamlit's tokens. Use `.properties()` for sizing; reserve `configure_*` for `theme=None`.
- **Dual-axis line charts** — the scale ratio is arbitrary and misleading. Use small multiples or index both to 100.
- **Over-annotated uncertainty** — opacity gradient only; put quantile meanings in the subtitle.
- **matplotlib in loops without `plt.close()`** → memory leak in long Streamlit sessions.
- **Red/green diverging** fails deuteranopia (~5% of men). Use **Wong blue/orange** (`#0072B2` / `#D55E00`).
- **Altair >5000 rows** raises MaxRowsError → `alt.data_transformers.enable("vegafusion")` or pass a URL/file.
