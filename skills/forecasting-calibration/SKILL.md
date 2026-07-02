---
name: forecasting-calibration
description: Use when building or evaluating a probabilistic forecast that should match or beat a market or benchmark — sports results, match odds (home/draw/away), elections, brackets, or any multi-outcome probability model; or when working with calibration, RPS, Brier, log-loss, reliability diagrams, devigging bookmaker odds, blending model vs market, backtesting, or closing-line value (CLV).
---

# Forecasting & Calibration — match or beat the market

## Overview

The gap to a sharp market is closed **not by model complexity** but by four disciplines: (1) anchor to **de-vigged market probabilities**, (2) a sound structural model (time-decayed Dixon-Coles / bivariate Poisson), (3) **post-hoc calibration**, (4) honest **out-of-sample** measurement (RPS + CLV on walk-forward splits). A complex model scored in-sample looks brilliant and loses money.

## When to use

- Predicting multi-outcome events (H/D/A, elections, brackets) where a market or benchmark exists.
- "Does my model beat the bookies / the polls?", "is it calibrated?", "what's my real edge?"
- Working with odds, implied probabilities, backtests, or any proper score.

**Not for:** point/regression forecasting without probabilities → `senior-data-scientist`. Chart design → `dataviz-storytelling`. App wiring → `streamlit-apps`.

## Beat-the-market checklist

1. **De-vig the closing line with the power method** — it is your single best predictor and your calibration target. (Basic normalization ignores favorite-longshot bias and underprices favorites.)
2. **Structural model = time-decayed Dixon-Coles** with the low-score ρ correction; tune decay λ on held-out seasons, never in-sample.
3. **Recalibrate post-hoc** (isotonic, ≥200 samples) on a dedicated holdout *before* blending.
4. **Blend by log-opinion pooling**, weight λ fit on walk-forward; expect λ_model ≈ 0.2–0.35 (heavily market-anchored). If best λ=0, the market already dominates your model — say so.
5. **Score only out-of-sample with RPS** (primary) + log-loss; never tune on the evaluation split.
6. **Track CLV on every pick** — median CLV ≤ 0 after 200+ picks means no discoverable edge. Full stop.
7. **Tournaments:** leave-one-edition-out CV + bootstrap CI on RPS; declare superiority only across ≥3 editions (a 64-match World Cup ≈ 20 independent results).

## Metrics quick reference

| Metric | For | Note |
|---|---|---|
| **RPS** (Ranked Probability Score) | ordinal multi-outcome (H/D/A) | **primary**; penalizes wrong-direction more; uniform 3-way E[RPS] ≈ 0.222 (2/9), worst case 1.0 |
| **Log-loss** | overconfidence | strictly proper; punishes confident-and-wrong hardest |
| **Brier** | quick summary | proper but ignores outcome ordering |
| **Reliability diagram** | calibration vs sharpness | sharp ≠ calibrated; bin predicted vs observed frequency |
| **CLV** | real edge | `your_odds / closing_odds − 1`; converges faster than realized ROI |

## Devig + blend quick reference

- **Power method** (preferred): solve `Σ pᵢ^k = 1`, then `pᵢ = pᵢ_raw^k`. Corrects FLB; Clarke 2017 ranks it #1–2 on every accuracy metric. Shin = robustness check. Normalization = last resort.
- **Log-opinion pool:** `p ∝ p_model^λ · p_market^(1−λ)`; the only pool that preserves conditional-independence structure. Fit λ by minimizing log-loss on a holdout.

Runnable code + formulas: see `methods.md`.

## Backtesting rules

- **Walk-forward (expanding window) only** — standard k-fold leaks the future. This is the #1 practical mistake.
- **Leave-one-tournament-out** for tournament prediction; **embargo** rows adjacent to the test fold when using rolling-form features.
- **Nested CV:** inner loop tunes ρ/λ/K, outer loop gives the honest RPS. Never select hyperparameters on the data you report.

## Common mistakes

- **Look-ahead leakage** from k-fold on time-ordered matches → walk-forward.
- **Overfitting tournament noise** (tuning ρ/λ on one 64-match cup) → multi-edition CV + bootstrap CI.
- **Ignoring CLV**, judging on 100-bet ROI → far too noisy to separate edge from variance.
- **Flat-normalization devig** → underprices favorites (FLB). Use the power method.
- **Miscalibration hidden by sharpness** → a model that says 90% on favorites can be terrible on draws. Reliability diagram per outcome + isotonic.
- **Feature-stuffing without regularization** → great in-sample RPS, worse out-of-sample. Curate + LASSO + walk-forward validate.
