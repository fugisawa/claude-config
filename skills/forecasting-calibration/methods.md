# Forecasting & calibration — methods, formulas, code

All snippets assume `import numpy as np`. Probabilities are rows over K ordered outcomes (e.g. `[P(H), P(D), P(A)]`).

## 1. Devigging bookmaker odds → probabilities

```python
def devig_power(odds, tol=1e-12):
    """Power method: solve Σ inv_i^k = 1. Corrects favorite-longshot bias."""
    inv = 1.0 / np.asarray(odds, float)          # raw implied, sums to 1+overround
    lo, hi = 0.1, 10.0
    for _ in range(200):
        k = 0.5 * (lo + hi)
        s = (inv ** k).sum()
        if s > 1: lo = k                          # higher k shrinks the sum
        else:     hi = k
        if hi - lo < tol: break                   # stop once converged
    p = inv ** k
    return p / p.sum()

def devig_normalize(odds):                        # last resort: ignores FLB
    inv = 1.0 / np.asarray(odds, float)
    return inv / inv.sum()
```

Shin's method (insider-trading model) is a useful robustness check but loses to the power method in multi-outcome leagues with strong FLB; reach for it only when comparing.

## 2. Structural model (notes)

- **Dixon-Coles**: two correlated Poisson goal counts + a low-score correction `τ(x,y; ρ)` that reweights (0-0),(1-0),(0-1),(1-1). Ignoring ρ miscalibrates the **draw** probability.
- **Time decay**: weight each historical match by `exp(-ξ·Δt_days)` in the likelihood. Tune ξ on held-out seasons; typical half-life ≈ 6–18 months.
- Modern alternative: Bayesian dynamic Dixon-Coles (attack/defence as latent random walks) removes manual decay tuning and propagates uncertainty (JRSS-C 2025).

## 3. Calibration

```python
def rps(probs, outcome_idx):
    """Ranked Probability Score for ONE ordered prediction. Lower is better."""
    p = np.asarray(probs, float)
    cp = np.cumsum(p)
    co = np.cumsum(np.eye(len(p))[outcome_idx])
    return ((cp - co) ** 2).sum() / (len(p) - 1)

# Brier / log-loss over a matrix P (N×K) with integer labels y:
def brier(P, y): return ((P - np.eye(P.shape[1])[y]) ** 2).sum(1).mean()
def logloss(P, y, eps=1e-15): return -np.log(np.clip(P[np.arange(len(y)), y], eps, 1)).mean()
```

**Reliability diagram** (per outcome): `sklearn.calibration.CalibrationDisplay.from_predictions(y==k, P[:,k])`, or `pycalib` for multiclass with error bars.

**Isotonic recalibration** (≥200 holdout samples), fit per outcome then renormalize:

```python
from sklearn.isotonic import IsotonicRegression

def fit_isotonic(P_hold, y_hold):
    K = P_hold.shape[1]
    cals = []
    for k in range(K):
        ir = IsotonicRegression(out_of_bounds="clip")
        ir.fit(P_hold[:, k], (y_hold == k).astype(float))
        cals.append(ir)
    return cals

def apply_isotonic(cals, P):
    C = np.column_stack([cals[k].predict(P[:, k]) for k in range(len(cals))])
    return C / C.sum(1, keepdims=True)
```

**Caveat:** per-column monotonicity holds *before* renormalization (guaranteed by `IsotonicRegression`) but **not after** dividing by the row sum — a higher raw `p_k` can map to a lower calibrated `p_k`. If outcome *ordering* near a decision threshold matters, prefer temperature scaling (preserves order) or use isotonic only to *report* calibration.

For softmax/neural outputs, **temperature scaling** (divide logits by a scalar T>1 learned on validation) is a cheaper 1-parameter alternative.

## 4. Blending model + market

```python
def log_pool(p_model, p_market, w):
    """Log-opinion pool. w = weight on the model (1-w on the market)."""
    p = (np.asarray(p_model) ** w) * (np.asarray(p_market) ** (1 - w))
    return p / p.sum()

from scipy.optimize import minimize_scalar
def fit_lambda(P_model, P_market, y):
    """Fit blend weight by minimizing log-loss on a holdout (N×K arrays)."""
    def nll(w):
        P = (P_model ** w) * (P_market ** (1 - w))
        P = P / P.sum(1, keepdims=True)
        return logloss(P, y)
    return minimize_scalar(nll, bounds=(0, 1), method="bounded").x
```

**Caveat:** if `P_model` is near-uniform its `(1/K)^w` factor cancels after normalization, so the objective becomes a power-transform of the market and the returned λ is **not** interpretable as a model weight. Sanity check: if `logloss(P_model, y) ≈ log(K)`, the model has no signal — skip blending.

## 5. Backtesting

```python
def walk_forward(df, fit_predict, min_train=380):
    """Expanding window over time-sorted matches. fit_predict(train, test)->P."""
    df = df.sort_values("date").reset_index(drop=True)
    preds = []
    for i in range(min_train, len(df)):
        P = fit_predict(df.iloc[:i], df.iloc[[i]])    # train on past only
        preds.append(P[0])
    return np.array(preds)                            # aligns with df.iloc[min_train:]
```

- **Leave-one-tournament-out:** hold out entire editions; within-edition form leaks under naive match-level splits.
- **Purged/embargo CV** (López de Prado): drop a buffer of rows adjacent in time to the test fold so rolling features don't bleed across the boundary.

```python
def boot_ci_rps(rps_model, rps_market, n=10000, seed_arr=None):
    """Bootstrap CI on the per-match RPS difference (model − market)."""
    d = np.asarray(rps_model) - np.asarray(rps_market)
    idx = np.random.randint(0, len(d), (n, len(d)))
    means = d[idx].mean(1)
    return np.percentile(means, [2.5, 97.5])          # straddles 0 ⇒ inconclusive
```

## 6. Closing Line Value

```python
def clv(your_decimal_odds, closing_decimal_odds):
    """Positive ⇒ you beat the closing line. Median>0 over 200+ picks ⇒ real edge."""
    return your_decimal_odds / closing_decimal_odds - 1
```

Log CLV for **every** prediction, not just bets placed. It is the practitioner gold standard: consistent positive CLV is mathematically equivalent to positive EV over large samples, and converges as a signal far faster than realized win rate.

## References

1. Dixon & Coles (1997), *JRSS-C* — bivariate Poisson + ρ low-score correction (the baseline).
2. Massé & Jolfaei (2021), arXiv:2106.14345 — verification, reliability/resolution decompositions for football.
3. Clarke et al. (2017), *Am. J. Sports Science* — power method beats Shin & normalization for overround.
4. Bayesian state-space EPL model (2025), *JRSS-C* 74(3):717 — dynamic Dixon-Coles.
5. Zeileis et al. (2024), arXiv:2410.09068 — EURO 2024 via combined statistical learning (odds + xG + ratings).
6. Stübinger & Knoll (2018), *AI 2018* — "Beat the Bookmaker", honest OOS methodology.
7. López de Prado (2018), *Advances in Financial ML* — purged/embargoed CV.
8. Outlier.bet — practitioner devig method comparison; The Lines — CLV explainer.
