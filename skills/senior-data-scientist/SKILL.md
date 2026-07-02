---
name: senior-data-scientist
description: Use when doing data analysis, statistical modeling, or ML in Python/R — exploratory analysis, feature engineering, model selection and evaluation, train/test leakage, cross-validation or backtesting, A/B testing and causal inference, time series, imbalanced classes, or turning a dataframe into a defensible quantitative decision.
---

# Senior Data Scientist

## Overview

The senior move is **not a fancier model — it's a question framed correctly, a validation that matches deployment, and an honest read of uncertainty.** Most real failures are leakage, the wrong metric, or a missing baseline — not insufficient model power.

## When to use

- EDA, modeling, evaluation, or feature engineering on tabular / time-series data.
- "Is this result real?", "why does it work in the notebook but fail live?", choosing a metric or validation scheme.
- A/B tests, causal questions, time series, imbalanced classification.

**Not for:** probabilistic forecasting / beating a market → `forecasting-calibration`. Chart design → `dataviz-storytelling`. Streamlit wiring → `streamlit-apps`. LLM pipelines → `langchain-stack`.

## The disciplines that actually matter

### 1. Frame before you fit
Write the decision this informs and the cost of each error *before* modeling. A model with no decision attached is a hobby.

### 2. Leakage is the cardinal sin
Most "amazing" results are leakage. Hunt all four kinds:
- **Target leakage** — a feature is a proxy or consequence of the label.
- **Temporal leakage** — using the future: aggregates over the whole set, look-ahead joins.
- **Group leakage** — the same entity (user, team, patient) in train and test.
- **Preprocessing leakage** — fitting scaler/imputer/encoder on all data, *then* splitting.
- **Selection leakage** — running feature selection or target-aware encoding on the full dataset before the split.

Fix: **split first**, fit every transform inside the fold (use a `Pipeline`).

### 3. Validation must mimic deployment
- IID rows → stratified k-fold. Time-ordered → **walk-forward** (never shuffle). Repeated entities → **GroupKFold**.
- Tuning and reporting on the same split inflates everything → **nested CV** (inner tunes, outer reports).
- Report a **baseline first** (majority class, last value, group mean). Beat the dumb thing before the smart thing.

### 4. The metric is a decision, not a default
Accuracy lies under imbalance. Choose for the decision: ranking → ROC-AUC / PR-AUC; probabilities → log-loss / Brier **+ calibration**; regression → MAE vs RMSE by outlier cost. A model used for probabilities must be **calibrated**, not merely discriminative.

### 5. Uncertainty, honestly
Point estimates without intervals overclaim. Bootstrap a CI on the metric; on small or dependent data the gap between models is often **inconclusive** — say so plainly.

### 6. Reproducible or it didn't happen
Seed, pin versions, version the data, one command to reproduce. A result you can't rerun is an anecdote.

## A/B testing & causal (quick reference)

- Pre-register hypothesis, primary metric, MDE, and sample size. Peeking inflates Type-I error → fixed horizon or a proper sequential test.
- Correlation ≠ cause: watch confounding, selection, Simpson's paradox. Tools: difference-in-differences, IV, regression discontinuity, matching/propensity — and state the identifying assumption out loud.

## Helpers bundled with this skill

- `scripts/experiment_designer.py`, `scripts/feature_engineering_pipeline.py`, `scripts/model_evaluation_suite.py`
- Deeper references: `references/statistical_methods_advanced.md`, `references/experiment_design_frameworks.md`, `references/feature_engineering_patterns.md`

## Common mistakes

- Preprocessing before splitting → leakage. Split first, transform in-fold.
- No baseline → no idea whether the model adds value.
- Optimizing accuracy on imbalanced data → a confident, useless classifier.
- Tuning on the test set (or the same CV you report) → inflated metrics.
- Shuffling a time series → look-ahead leakage.
- A point metric with no interval on small data → false precision.
