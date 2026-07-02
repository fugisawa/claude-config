# Forecast-viz recipes

Adapt column names. Wong colorblind-safe palette: blue `#0072B2`, vermillion `#D55E00`, green `#009E73`, reddish-purple `#CC79A7`, sky `#56B4E9`.

## Fan / interval chart (time-series uncertainty) — Altair

```python
import altair as alt
base = alt.Chart(df)                              # cols: date, forecast, lo80, hi80, lo95, hi95
band95 = base.mark_area(opacity=0.15).encode(x="date:T", y="lo95:Q", y2="hi95:Q")
band80 = base.mark_area(opacity=0.30).encode(x="date:T", y="lo80:Q", y2="hi80:Q")
line   = base.mark_line(color="#0072B2").encode(x="date:T", y="forecast:Q")
chart  = (band95 + band80 + line).properties(height=320)
# st.altair_chart(chart, theme="streamlit", use_container_width=True)
```

For bootstrap CIs straight from raw data: `base.mark_errorband(extent="ci")`.

## Model vs market (predicted vs actual) scatter — Plotly

```python
import plotly.express as px
fig = px.scatter(df, x="actual", y="predicted", color="segment",
                 template="plotly_white")          # "plotly_dark" when st.context.theme.type=="dark"
lo, hi = df[["actual", "predicted"]].min().min(), df[["actual", "predicted"]].max().max()
fig.add_shape(type="line", x0=lo, y0=lo, x1=hi, y1=hi,
              line=dict(dash="dash", color="gray"))  # y=x reference
# above the diagonal = model over-predicts; st.plotly_chart(fig, use_container_width=True)
```

## Over/under-performance (actual − expected) — Altair diverging bar

```python
alt.Chart(df).mark_bar().encode(                    # cols: team, delta
    x=alt.X("delta:Q", title="actual − expected"),
    y=alt.Y("team:N", sort="-x"),
    color=alt.condition(alt.datum.delta > 0,
                        alt.value("#0072B2"),        # over-performed
                        alt.value("#D55E00")),       # under-performed
).properties(height=alt.Step(18))                    # zero line is the axis itself
```

## Reliability / calibration diagram — matplotlib (per outcome)

```python
import matplotlib.pyplot as plt
from sklearn.calibration import CalibrationDisplay
fig, ax = plt.subplots(figsize=(4, 4))
for k, name in enumerate(["Home", "Draw", "Away"]):
    CalibrationDisplay.from_predictions((y == k).astype(int), P[:, k],
                                        n_bins=10, name=name, ax=ax)
ax.plot([0, 1], [0, 1], "k--", lw=1)                # perfect calibration
ax.set_xlabel("predicted probability"); ax.set_ylabel("observed frequency")
# st.pyplot(fig); plt.close(fig)
```

`pip install pycalib` gives `plot_reliability_diagram()` with error bars for multiclass.

## Probability bars (ranked confidence) — Altair

```python
# Layer two named charts — don't chain .mark_bar() after .encode() (it drops the encodings).
bars = alt.Chart(df).mark_bar(color="#0072B2").encode(   # cols: outcome, prob
    x=alt.X("prob:Q", scale=alt.Scale(domain=[0, 1])),
    y=alt.Y("outcome:N", sort="-x"),
)
labels = alt.Chart(df).mark_text(align="left", dx=3).encode(
    x="prob:Q", y=alt.Y("outcome:N", sort="-x"),
    text=alt.Text("prob:Q", format=".0%"),               # direct labels, no legend
)
bars + labels
```

## Light/dark palette pairs

Pick colors as (light-bg, dark-bg) pairs and check WCAG contrast on both. A hue that reads on white often fails on dark slate; nudge lightness, keep hue. Let Altair's `theme="streamlit"` handle neutrals; only hard-code the categorical/semantic hues (the Wong set above works on both).
