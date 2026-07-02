#!/usr/bin/env python3
"""
make_charts.py — Generate charts that match a briefing persona.

Usage:
    from make_charts import bar_chart, hbar_chart, line_chart, save

    fig = bar_chart(
        persona="editorial",
        title="Costs diverge by two orders of magnitude",
        categories=["1 wk", "1 mo", "3 mo", "6 mo"],
        series=[
            {"name": "Scenario (i)", "values": [0.4, 1.0, 2.5, 5.0], "color": "secondary"},
            {"name": "Scenario (ii)", "values": [10, 50, 150, 400], "color": "accent"},
        ],
        y_label="US$ billions (log)",
        log_y=True,
        source="Author's analysis based on CNAS, CBO, Pentagon.",
    )
    save(fig, "/path/to/chart", formats=["png", "svg"])
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import Iterable


# ============================================================
# PERSONA TOKENS (mirror design_system.css)
# ============================================================

PERSONAS = {
    "editorial": {
        "accent":    "#E3120B",
        "ink":       "#121212",
        "secondary": "#006BA2",
        "muted":     "#758D99",
        "surface":   "#F4EFE5",
        "paper":     "#FEFCF8",
    },
    "academic": {
        "accent":    "#1B2A4E",
        "ink":       "#1A1A1A",
        "secondary": "#6B7280",
        "muted":     "#6B7280",
        "surface":   "#EAE7E0",
        "paper":     "#FAFAF7",
    },
    "governmental": {
        "accent":    "#2C3E50",
        "ink":       "#1A1A1A",
        "secondary": "#A07000",
        "muted":     "#6B6B6B",
        "surface":   "#F0EDE5",
        "paper":     "#FCFAF5",
    },
    "financial": {
        "accent":    "#FF6B00",
        "ink":       "#0A0E1A",
        "secondary": "#00A86B",
        "muted":     "#6B7280",
        "surface":   "#F5F5F2",
        "paper":     "#FFFFFF",
    },
}


def _resolve_color(token_or_hex: str, persona: dict) -> str:
    """Accept either a token name ('accent', 'secondary', 'muted') or a hex string."""
    if token_or_hex in persona:
        return persona[token_or_hex]
    return token_or_hex


def _setup_rcparams(persona: dict, language: str = "pt"):
    """Configure matplotlib to match the persona."""
    decimal_sep = "," if language in ("pt", "es", "fr") else "."
    thousands_sep = "." if language in ("pt", "es", "fr") else ","

    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Lora", "Liberation Serif", "DejaVu Serif"],
        "font.size": 10,
        "axes.edgecolor": persona["ink"],
        "axes.linewidth": 0.8,
        "axes.labelcolor": persona["ink"],
        "xtick.color": persona["ink"],
        "ytick.color": persona["ink"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": persona["paper"],
        "figure.facecolor": persona["paper"],
        "savefig.facecolor": persona["paper"],
        "axes.formatter.use_locale": False,
        # SVG is the embed format for PDFs (vector = always crisp).
        # 'path' converts text to outlines so the rendered PDF never
        # depends on the SVG renderer resolving the chart fonts.
        "svg.fonttype": "path",
    })


def _add_source(fig, source: str, persona: dict):
    """Add a source attribution at the bottom of the figure."""
    if not source:
        return
    fig.text(
        0.05, -0.04, source,
        fontsize=8, style="italic", color=persona["muted"],
        ha="left", va="top",
    )


def _format_number(value: float, language: str = "pt") -> str:
    """Format a number in locale-appropriate style."""
    if language in ("pt", "es", "fr"):
        if isinstance(value, int) or value == int(value):
            return f"{int(value):,}".replace(",", ".")
        return f"{value:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        if isinstance(value, int) or value == int(value):
            return f"{int(value):,}"
        return f"{value:,.1f}"


# ============================================================
# CHART TYPES
# ============================================================

def bar_chart(
    persona: str = "editorial",
    title: str = "",
    subtitle: str = "",
    categories: list = None,
    series: list = None,
    y_label: str = "",
    log_y: bool = False,
    figsize: tuple = (7.5, 4.2),
    show_values: bool = True,
    source: str = "",
    language: str = "pt",
):
    """
    Vertical bar chart, 1–N series.

    series: list of dicts with keys 'name', 'values', and 'color' (token or hex).
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if categories is None or series is None:
        raise ValueError("`categories` and `series` are required.")

    fig, ax = plt.subplots(figsize=figsize)

    n_series = len(series)
    n_categories = len(categories)
    width_total = 0.8
    width = width_total / n_series
    x = np.arange(n_categories)

    for i, s in enumerate(series):
        color = _resolve_color(s.get("color", "accent"), p)
        offset = (i - (n_series - 1) / 2) * width
        bars = ax.bar(
            x + offset, s["values"], width,
            label=s["name"], color=color, edgecolor="none", zorder=3,
        )
        if show_values:
            for bar, val in zip(bars, s["values"]):
                if val == 0:
                    continue
                y_pos = val * 1.4 if log_y else val + max(s["values"]) * 0.02
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    y_pos,
                    _format_number(val, language),
                    ha="center", va="bottom",
                    fontsize=8.5, color=color, weight="bold",
                )

    if log_y:
        ax.set_yscale("log")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10.5)
    if y_label:
        ax.set_ylabel(y_label, fontsize=10, style="italic")
    ax.grid(axis="y", linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.4, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", which="major", labelsize=10, length=0)

    if title:
        # Title is set via the chart-title HTML element, not on the figure.
        # But we can use suptitle if user prefers. Default: omit.
        pass

    if n_series > 1:
        ax.legend(loc="upper left", frameon=False, fontsize=10,
                  bbox_to_anchor=(0, 1.02), ncol=1)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def hbar_chart(
    persona: str = "editorial",
    title: str = "",
    categories: list = None,
    values: list = None,
    colors: list = None,
    x_label: str = "",
    figsize: tuple = (7.5, 4.0),
    show_values: bool = True,
    value_suffix: str = "",
    source: str = "",
    language: str = "pt",
):
    """
    Horizontal bar chart. Good for ranked items with descriptive labels.

    colors: optional list, same length as categories. Token names or hex.
            If None, all bars use accent.
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if categories is None or values is None:
        raise ValueError("`categories` and `values` are required.")

    if colors is None:
        bar_colors = [p["accent"]] * len(categories)
    else:
        bar_colors = [_resolve_color(c, p) for c in colors]

    fig, ax = plt.subplots(figsize=figsize)

    bars = ax.barh(categories, values, color=bar_colors, edgecolor="none", zorder=3)

    max_val = max(values)
    ax.set_xlim(0, max_val * 1.25)

    if x_label:
        ax.set_xlabel(x_label, fontsize=10, style="italic")

    ax.invert_yaxis()
    ax.tick_params(axis="y", labelsize=10.5, length=0, pad=8)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="x", linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.4, zorder=1)
    ax.set_axisbelow(True)

    for spine in ["left", "bottom", "top", "right"]:
        ax.spines[spine].set_visible(False)

    if show_values:
        for bar, val in zip(bars, values):
            label = f"{_format_number(val, language)}{value_suffix}"
            ax.text(val + max_val * 0.02, bar.get_y() + bar.get_height() / 2,
                    label, va="center", fontsize=11, weight="bold", color=p["ink"])

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def line_chart(
    persona: str = "editorial",
    x: list = None,
    series: list = None,
    y_label: str = "",
    x_label: str = "",
    figsize: tuple = (7.5, 4.2),
    source: str = "",
    language: str = "pt",
):
    """
    Time series chart. 1–4 lines.

    series: list of {'name': str, 'values': list, 'color': str (token or hex)}
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if x is None or series is None:
        raise ValueError("`x` and `series` are required.")

    fig, ax = plt.subplots(figsize=figsize)

    for s in series:
        color = _resolve_color(s.get("color", "accent"), p)
        ax.plot(x, s["values"], label=s["name"], color=color, linewidth=2, zorder=3)
        # Direct label at the right end
        ax.text(x[-1], s["values"][-1], "  " + s["name"],
                color=color, fontsize=9.5, va="center", weight="bold")

    if y_label:
        ax.set_ylabel(y_label, fontsize=10, style="italic")
    if x_label:
        ax.set_xlabel(x_label, fontsize=10, style="italic")

    ax.grid(axis="y", linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.4, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", which="major", labelsize=10, length=0)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def slope_chart(
    persona: str = "editorial",
    items: list = None,
    label_left: str = "",
    label_right: str = "",
    figsize: tuple = (7.5, 5.0),
    source: str = "",
    language: str = "pt",
):
    """
    Slope diagram between two columns.

    items: list of {'name': str, 'left': float, 'right': float, 'highlight': bool (optional)}
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if items is None:
        raise ValueError("`items` is required.")

    fig, ax = plt.subplots(figsize=figsize)

    for item in items:
        color = p["accent"] if item.get("highlight") else p["muted"]
        lw = 2.0 if item.get("highlight") else 1.0
        ax.plot([0, 1], [item["left"], item["right"]],
                color=color, linewidth=lw, zorder=3, marker="o", markersize=5)
        ax.text(-0.02, item["left"], item["name"] + "  ",
                ha="right", va="center", fontsize=9, color=p["ink"])
        ax.text(1.02, item["right"], "  " + _format_number(item["right"], language),
                ha="left", va="center", fontsize=9, color=color, weight="bold")

    ax.set_xlim(-0.3, 1.3)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([label_left, label_right], fontsize=10.5, weight="bold")

    for spine in ["left", "right", "top", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", left=False, labelleft=False)
    ax.tick_params(axis="x", length=0, pad=6)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def dot_plot(
    persona: str = "editorial",
    items: list = None,
    x_label: str = "",
    figsize: tuple = (7.5, 4.0),
    source: str = "",
    language: str = "pt",
):
    """
    Cleveland dot plot. Each item has a 'low', 'high', and 'point' (optional).

    items: list of {'name': str, 'low': float, 'high': float, 'point': float (optional)}
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if items is None:
        raise ValueError("`items` is required.")

    fig, ax = plt.subplots(figsize=figsize)

    names = [i["name"] for i in items]
    y_pos = np.arange(len(items))

    for i, item in enumerate(items):
        ax.plot([item["low"], item["high"]], [i, i],
                color=p["muted"], linewidth=1.5, zorder=2)
        ax.plot(item["low"], i, "o", color=p["secondary"], markersize=8, zorder=3)
        ax.plot(item["high"], i, "o", color=p["accent"], markersize=8, zorder=3)
        if "point" in item:
            ax.plot(item["point"], i, "D", color=p["ink"], markersize=7, zorder=4)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10.5)
    ax.invert_yaxis()
    if x_label:
        ax.set_xlabel(x_label, fontsize=10, style="italic")
    ax.grid(axis="x", linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.4, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0)

    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def stacked_chart(
    persona: str = "editorial",
    x: list = None,
    series: list = None,
    style: str = "area",
    y_label: str = "",
    figsize: tuple = (7.5, 4.2),
    source: str = "",
    language: str = "pt",
):
    """
    Stacked area or bar chart for compositional data.

    style: "area" or "bar"
    series: list of {'name': str, 'values': list, 'color': str}
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if x is None or series is None:
        raise ValueError("`x` and `series` are required.")

    fig, ax = plt.subplots(figsize=figsize)

    if style == "area":
        values_matrix = [s["values"] for s in series]
        labels = [s["name"] for s in series]
        colors = [_resolve_color(s.get("color", "accent"), p) for s in series]
        ax.stackplot(x, values_matrix, labels=labels, colors=colors, alpha=0.9)
    elif style == "bar":
        bottom = np.zeros(len(x))
        for s in series:
            color = _resolve_color(s.get("color", "accent"), p)
            ax.bar(x, s["values"], bottom=bottom, label=s["name"],
                   color=color, edgecolor="none", zorder=3)
            bottom += np.array(s["values"])
    else:
        raise ValueError(f"Unknown style: {style}")

    if y_label:
        ax.set_ylabel(y_label, fontsize=10, style="italic")
    ax.grid(axis="y", linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.4, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0)
    ax.legend(loc="upper left", frameon=False, fontsize=10)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def dumbbell_chart(
    persona: str = "editorial",
    items: list = None,
    labels: tuple = ("Antes", "Depois"),
    x_label: str = "",
    figsize: tuple = (7.5, 4.0),
    source: str = "",
    language: str = "pt",
    show_values: bool = True,
):
    """
    Dumbbell ("thermometer") chart: two values per category joined by a line.
    The honest replacement for broken-scale bars when comparing two states
    (before/after, scenario A vs B, men vs women).

    items: list of {'name': str, 'a': float, 'b': float}
           'a' is drawn in --secondary, 'b' in --accent.
    labels: (label_for_a, label_for_b) — drawn once, on the first row,
            so no legend is needed (direct labeling).
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if items is None:
        raise ValueError("`items` is required.")

    fig, ax = plt.subplots(figsize=figsize)

    names = [i["name"] for i in items]
    y_pos = np.arange(len(items))

    for i, item in enumerate(items):
        ax.plot([item["a"], item["b"]], [i, i],
                color=p["muted"], linewidth=2.0, zorder=2, solid_capstyle="round")
        ax.plot(item["a"], i, "o", color=p["secondary"], markersize=9, zorder=3)
        ax.plot(item["b"], i, "o", color=p["accent"], markersize=9, zorder=3)
        if show_values:
            # Place value labels outside the dumbbell, away from the line
            lo, hi = sorted([item["a"], item["b"]])
            for val, ha, off in [(lo, "right", -1), (hi, "left", 1)]:
                ax.annotate(_format_number(val, language), (val, i),
                            textcoords="offset points", xytext=(8 * off, 0),
                            ha=ha, va="center", fontsize=8.5, color=p["ink"])

    # Direct labels on the first (top) row instead of a legend.
    # When the two points sit close together, the labels would collide
    # if both were centered above their points — push them apart
    # horizontally (outward) whenever the gap is under 18% of the range.
    first = items[0]
    all_vals = [v for it in items for v in (it["a"], it["b"])]
    span = (max(all_vals) - min(all_vals)) or 1.0
    close = abs(first["a"] - first["b"]) < 0.18 * span
    a_left = first["a"] <= first["b"]
    if close:
        ha_a = "right" if a_left else "left"
        ha_b = "left" if a_left else "right"
    else:
        ha_a = ha_b = "center"
    ax.annotate(labels[0], (first["a"], 0), textcoords="offset points",
                xytext=(0, 12), ha=ha_a, fontsize=9,
                color=p["secondary"], fontweight="bold")
    ax.annotate(labels[1], (first["b"], 0), textcoords="offset points",
                xytext=(0, 12), ha=ha_b, fontsize=9,
                color=p["accent"], fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10.5)
    ax.invert_yaxis()
    ax.set_ylim(len(items) - 0.5, -0.9)  # headroom for the direct labels
    if x_label:
        ax.set_xlabel(x_label, fontsize=10, style="italic")
    ax.grid(axis="x", linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.4, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0)

    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


def scatter_chart(
    persona: str = "editorial",
    points: list = None,
    x_label: str = "",
    y_label: str = "",
    highlight: list = None,
    annotation: str = "",
    figsize: tuple = (7.5, 4.6),
    source: str = "",
    language: str = "pt",
):
    """
    Scatter plot for correlation/distribution claims.

    points: list of {'x': float, 'y': float, 'name': str (optional),
                     'size': float (optional, bubble area weight)}
    highlight: list of names to draw in --accent with labels; everything
               else renders muted. This enforces the "color carries the
               claim" convention — a scatter where every point is loud
               makes no claim.
    annotation: short text placed in the emptiest corner — use it to name
                the pattern the reader should see (readers assume the
                relationship is causal unless told otherwise; say so here
                or in the chart subtitle when it isn't).
    """
    p = PERSONAS[persona]
    _setup_rcparams(p, language)

    if points is None:
        raise ValueError("`points` is required.")

    fig, ax = plt.subplots(figsize=figsize)
    highlight = set(highlight or [])

    for pt in points:
        is_hl = pt.get("name") in highlight
        color = p["accent"] if is_hl else p["muted"]
        # 40 pt^2 base area reads well at brief column width; size weights scale it
        area = 40 * pt.get("size", 1.0)
        ax.scatter(pt["x"], pt["y"], s=area, color=color,
                   alpha=0.95 if is_hl else 0.55, zorder=3 if is_hl else 2,
                   edgecolors="none")
        if is_hl and pt.get("name"):
            ax.annotate(pt["name"], (pt["x"], pt["y"]),
                        textcoords="offset points", xytext=(7, 5),
                        fontsize=9, color=p["ink"], fontweight="bold")

    if annotation:
        ax.annotate(annotation, xy=(0.97, 0.05), xycoords="axes fraction",
                    ha="right", va="bottom", fontsize=9, style="italic",
                    color=p["muted"])

    if x_label:
        ax.set_xlabel(x_label, fontsize=10, style="italic")
    if y_label:
        ax.set_ylabel(y_label, fontsize=10, style="italic")
    ax.grid(linestyle="-", linewidth=0.4, color=p["muted"], alpha=0.35, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    _add_source(fig, source, p)
    plt.tight_layout()
    return fig


# Backwards-compatible alias (older docs referenced `scatter`)
scatter = scatter_chart


# ============================================================
# SAVING
# ============================================================

def save(fig, path_without_ext: str, formats: Iterable[str] = ("svg", "png")):
    """Save the figure in the requested formats. Path should not include extension.

    Embed the .svg in the briefing HTML — vector graphics stay crisp at any
    zoom/print resolution, while raster PNGs blur when WeasyPrint scales
    them to the column width. The .png (300 dpi) is a fallback for contexts
    that can't take SVG (e.g. pasting into chat or slides).
    """
    saved = []
    for fmt in formats:
        out = f"{path_without_ext}.{fmt}"
        if fmt == "png":
            fig.savefig(out, bbox_inches="tight", dpi=300)
        else:
            fig.savefig(out, bbox_inches="tight", format=fmt)
        saved.append(out)
    plt.close(fig)
    return saved


# ============================================================
# CLI for quick testing
# ============================================================

if __name__ == "__main__":
    # Example usage / smoke test
    fig = bar_chart(
        persona="editorial",
        categories=["1 wk", "1 mo", "3 mo", "6 mo"],
        series=[
            {"name": "Scenario (i)", "values": [0.4, 1.0, 2.5, 5.0], "color": "secondary"},
            {"name": "Scenario (ii)", "values": [10, 50, 150, 400], "color": "accent"},
        ],
        y_label="US$ billions (log)",
        log_y=True,
        source="Author's analysis based on CNAS, CBO.",
        language="en",
    )
    save(fig, "/tmp/test_chart")
    print("Smoke test chart saved to /tmp/test_chart.{png,svg}")
