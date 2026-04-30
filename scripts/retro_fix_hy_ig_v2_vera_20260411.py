"""
Retro fix for HY-IG v2 charts (Vera, 2026-04-11).

Applies Chart Integrity Rules A1-A5 from the updated Visualization Agent SOP:

  - Rule A1: Hero chart axis de-inversion (was autorange='reversed')
  - Rule A2: Unit discipline — spread values live in percentage points in
    results/hy_ig_v2_spy/signals_20260410.parquet (mean ~3.82, range 1.47-15.31).
    Labels said 'bps'. 1% = 100 bps, so the bps display scale is ×100 (not ×10000).
    Example: last observation 2.02% → 202 bps.
  - Rule A3: Canonical short-name filenames under
    output/charts/hy_ig_v2_spy/plotly/{chart_type}.json (the pair_id lives
    in the directory, never in the filename). This script writes BOTH the
    canonical short-name AND the legacy prefixed version to avoid breaking
    anything mid-migration.
  - Rule A4: A regression note section is appended to
    results/hy_ig_v2_spy/regression_note_20260411.md (separate step — this
    script only writes charts; the regression note is managed in-SOP).
  - Rule A5: Every saved chart JSON gets a sibling _meta.json with a
    technical caption.

Charts produced:

  - hero                 (hero_spread_vs_spy): axis de-inverted, bps-corrected,
                          current-value annotation, dual-panel layout
  - correlation_heatmap  : canonical top-8 signals by |corr| at 63d horizon,
                          cols = 1d/5d/21d/63d/126d/252d, RdBu_r, zmid=0
  - ccf_prewhitened      : new chart — pre-whitened CCF bar plot with 95% CI
  - transfer_entropy     : new chart — bidirectional horizontal TE bar
  - quartile_returns     : new chart — Sharpe by spread quartile

Run:

    python3 scripts/retro_fix_hy_ig_v2_vera_20260411.py

Outputs:

    output/charts/hy_ig_v2_spy/plotly/{chart_type}.json          (canonical)
    output/charts/hy_ig_v2_spy/plotly/hy_ig_v2_spy_{chart_type}.json  (legacy)
    output/charts/hy_ig_v2_spy/plotly/{chart_type}_meta.json     (Rule A5)

IMPORTANT: does NOT modify scripts/generate_charts_hy_ig_v2_spy.py (the
2026-04-10 production version).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
PAIR_ID = "hy_ig_v2_spy"

RESULTS_DIR = REPO_ROOT / "results" / PAIR_ID
CORE_DIR = RESULTS_DIR / "core_models_20260410"
EXPLORATORY_DIR = RESULTS_DIR / "exploratory_20260410"
DATA_PARQUET = REPO_ROOT / "data" / "hy_ig_v2_spy_daily_20260410.parquet"
SIGNALS_PARQUET = RESULTS_DIR / "signals_20260410.parquet"

OUT_DIR = REPO_ROOT / "output" / "charts" / PAIR_ID / "plotly"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Colors (from SOP colorblind-safe palette)
# ---------------------------------------------------------------------------

COLOR_PRIMARY = "#0072B2"   # blue
COLOR_SECOND = "#D55E00"    # vermillion
COLOR_TERTIARY = "#009E73"  # green
COLOR_HIGHLIGHT = "#CC79A7"  # pink
COLOR_NEUTRAL = "#999999"   # grey


# ---------------------------------------------------------------------------
# Save helper (Rule A3 canonical path + legacy prefix + Rule A5 meta)
# ---------------------------------------------------------------------------

def save_chart(fig: go.Figure, chart_type: str, tech_caption: str) -> None:
    """Save fig to canonical short-name path, legacy prefixed path, and
    write a {chart_type}_meta.json with the technical caption (Rule A5)."""
    canonical_path = OUT_DIR / f"{chart_type}.json"
    legacy_path = OUT_DIR / f"{PAIR_ID}_{chart_type}.json"
    meta_path = OUT_DIR / f"{chart_type}_meta.json"

    payload = pio.to_json(fig)
    canonical_path.write_text(payload)
    legacy_path.write_text(payload)

    meta = {
        "chart_type": chart_type,
        "pair_id": PAIR_ID,
        "caption": tech_caption,
        "owner": "viz-vera",
        "produced_on": "2026-04-11",
        "source_script": "scripts/retro_fix_hy_ig_v2_vera_20260411.py",
        # VIZ-O1: disposition mandate. Every chart this script produces is a
        # page_template slot (core-zone). Exploratory orphans for this pair
        # are handled separately via results/hy_ig_v2_spy/analyst_suggestions.json
        # under key "exploratory_charts" (Rule VIZ-E1 / APP-PT2).
        "disposition": "consumed",
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"  saved: {canonical_path.relative_to(REPO_ROOT)}")
    print(f"  saved: {legacy_path.relative_to(REPO_ROOT)}")
    print(f"  saved: {meta_path.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Rule A2 unit audit
# ---------------------------------------------------------------------------

def audit_unit(y, unit_label: str, chart_type: str) -> None:
    y = [v for v in y if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not y:
        return
    ymax = max(y)
    ymin = min(y)
    if unit_label == "bps":
        if abs(ymax) < 10 and abs(ymin) < 10:
            raise ValueError(
                f"[{chart_type}] bps axis but values look like decimals/percent "
                f"(range [{ymin}, {ymax}]) — rescale or fix label"
            )
    elif unit_label == "%":
        if max(abs(ymax), abs(ymin)) < 1:
            raise ValueError(
                f"[{chart_type}] '%' axis but values look like fractions "
                f"(range [{ymin}, {ymax}]) — multiply by 100 or fix label"
            )


# ---------------------------------------------------------------------------
# CHART 1 — Hero: HY-IG spread vs SPY (axis de-inverted, bps-corrected)
# ---------------------------------------------------------------------------

def chart_hero() -> None:
    print("\n[1/5] Hero — spread vs SPY (fix axis inversion + bps unit)")
    df = pd.read_parquet(DATA_PARQUET)
    df = df[["hy_ig_spread_pct", "spy"]].dropna()
    # Rule A2: spread is in percentage points (e.g. 2.02 = 2.02%). Convert to
    # bps for display (2.02% × 100 = 202 bps). Verify the scale before/after.
    # NOTE (Wave 5C retro-apply 2026-04-19): column renamed hy_ig_spread → hy_ig_spread_pct
    # per DATA-D12 to make the percent unit explicit at the name layer.
    pct_min, pct_max = df["hy_ig_spread_pct"].min(), df["hy_ig_spread_pct"].max()
    spread_bps = df["hy_ig_spread_pct"] * 100.0
    bps_min, bps_max = spread_bps.min(), spread_bps.max()
    print(f"  spread (source): pct range [{pct_min:.2f}, {pct_max:.2f}]")
    print(f"  spread (display): bps range [{bps_min:.0f}, {bps_max:.0f}]")

    last_date = df.index.max()
    last_bps = spread_bps.iloc[-1]

    # Dual-panel (shared X): top = spread in bps, bottom = SPY price.
    # No inversion on either axis (Rule A1).
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
        row_heights=[0.5, 0.5],
        subplot_titles=(
            "HY-IG OAS Spread (bps, where 100 bps = 1%)",
            "SPY Price (USD)",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.index, y=spread_bps,
            name="HY-IG OAS Spread",
            line=dict(color=COLOR_SECOND, width=1.4),
            hovertemplate="%{x|%Y-%m-%d}<br>Spread: %{y:.0f} bps<extra></extra>",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["spy"],
            name="SPY Price",
            line=dict(color=COLOR_PRIMARY, width=1.4),
            hovertemplate="%{x|%Y-%m-%d}<br>SPY: $%{y:.0f}<extra></extra>",
        ),
        row=2, col=1,
    )

    # Current-value annotation on the spread panel
    fig.add_annotation(
        x=last_date, y=last_bps,
        xref="x", yref="y",
        text=f"Current ({last_date:%Y-%m-%d}): {last_bps:.0f} bps",
        showarrow=True, arrowhead=2, ax=-60, ay=-40,
        bgcolor="white", bordercolor=COLOR_SECOND, borderwidth=1,
        font=dict(size=11, color=COLOR_SECOND),
        row=1, col=1,
    )

    fig.update_yaxes(
        title_text="Spread (bps, where 100 bps = 1%)",
        rangemode="tozero",
        row=1, col=1,
    )
    fig.update_yaxes(
        title_text="SPY Price (USD)",
        rangemode="tozero",
        row=2, col=1,
    )
    fig.update_xaxes(title_text="Date", row=2, col=1)

    fig.update_layout(
        title=dict(
            text="HY-IG OAS Spread vs SPY — 2000 to 2025",
            x=0.02, xanchor="left",
        ),
        template="plotly_white",
        height=620,
        showlegend=False,
        margin=dict(l=70, r=30, t=80, b=60),
        annotations=list(fig.layout.annotations) + [
            dict(
                x=0, y=-0.18, xref="paper", yref="paper",
                text=(
                    "Source: FRED (BAMLH0A0HYM2, BAMLC0A0CM), Yahoo Finance. "
                    "Spread shown in basis points (1% = 100 bps). "
                    "Dual-panel layout; neither axis inverted."
                ),
                showarrow=False, font=dict(size=10, color=COLOR_NEUTRAL),
                xanchor="left",
            ),
        ],
    )

    # Rule A2 programmatic audit — must succeed
    audit_unit(spread_bps.tolist(), "bps", "hero")

    save_chart(
        fig, "hero",
        tech_caption=(
            "Dual-panel time series of HY-IG OAS spread (top, bps) and SPY "
            "price (bottom, USD) from 2000 to 2025. Both axes are non-inverted. "
            "Last observation annotated with current spread in bps."
        ),
    )
    print(f"  BEFORE: yaxis autorange='reversed', label 'HY-IG OAS Spread (bps)', values in pct (max {pct_max:.2f})")
    print(f"  AFTER : yaxis non-inverted, label 'Spread (bps, where 100 bps = 1%)', values in bps (max {bps_max:.0f})")


# ---------------------------------------------------------------------------
# CHART 2 — Correlation heatmap (canonical top-8 signals)
# ---------------------------------------------------------------------------

# Human-readable display names for signals
DISPLAY_NAMES = {
    "nfci_momentum_13w": "NFCI Momentum (13w)",
    "bank_smallcap_ratio": "Bank vs Small-Cap Ratio",
    "hy_ig_mom_63d": "HY-IG Momentum (63d)",
    "yield_spread_10y3m": "Yield Curve 10y-3m",
    "bbb_ig_spread": "BBB-IG Spread",
    "ccc_bb_spread": "CCC-BB Spread",
    "hy_ig_realized_vol_21d": "HY-IG Realized Vol (21d)",
    "hy_ig_roc_63d": "HY-IG RoC (63d)",
}

HORIZON_ORDER = ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d",
                 "spy_fwd_63d", "spy_fwd_126d", "spy_fwd_252d"]
HORIZON_LABELS = ["1D", "5D", "21D", "63D", "126D", "252D"]


def chart_correlation_heatmap() -> None:
    print("\n[2/5] Correlation heatmap (canonical top-8 signals)")
    df = pd.read_csv(EXPLORATORY_DIR / "correlations.csv")

    # Rank by |corr| at 63d horizon, take top 8 (Rule A3 spec)
    h63 = df[df["horizon"] == "spy_fwd_63d"].copy()
    h63["abs_corr"] = h63["correlation"].abs()
    h63 = h63.sort_values("abs_corr", ascending=False)
    top8_signals = h63["signal"].head(8).tolist()
    print(f"  selected signals (descending |corr| at 63d):")
    for s in top8_signals:
        c = h63[h63["signal"] == s]["correlation"].iloc[0]
        print(f"    {s}: {c:+.4f}")

    # Build (signal × horizon) correlation matrix in the canonical order
    sub = df[df["signal"].isin(top8_signals)].copy()
    sub["signal"] = pd.Categorical(sub["signal"], categories=top8_signals, ordered=True)
    pivot = sub.pivot(index="signal", columns="horizon", values="correlation")
    pivot = pivot[HORIZON_ORDER]  # enforce column order
    pivot = pivot.loc[top8_signals]  # enforce row order (descending |corr|)

    # Display labels
    y_labels = [DISPLAY_NAMES.get(s, s) for s in pivot.index]
    z = pivot.values
    text = [[f"{v:+.3f}" if pd.notnull(v) else "" for v in row] for row in z]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=HORIZON_LABELS,
            y=y_labels,
            colorscale="RdBu_r",
            zmid=0,
            zmin=-0.25,
            zmax=0.25,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=11, color="black"),
            colorbar=dict(title="Pearson r", thickness=14),
            hovertemplate="%{y}<br>Horizon: %{x}<br>r = %{z:+.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text=(
                "Credit-Stress Signals vs SPY Forward Returns<br>"
                "<sub>Top-8 signals by |correlation| at the 63-day horizon</sub>"
            ),
            x=0.02, xanchor="left",
        ),
        xaxis=dict(title="SPY Forward Return Horizon", side="bottom"),
        yaxis=dict(title="Signal", autorange="reversed"),  # matrix row convention (top = strongest)
        template="plotly_white",
        height=480,
        margin=dict(l=200, r=60, t=90, b=60),
        annotations=[
            dict(
                x=0, y=-0.22, xref="paper", yref="paper",
                text=(
                    "Red = higher signal → lower forward return (risk-off). "
                    "Blue = higher signal → higher forward return. "
                    "Signal selection: top 8 by |correlation| at 63d horizon."
                ),
                showarrow=False, font=dict(size=10, color=COLOR_NEUTRAL),
                xanchor="left",
            ),
        ],
    )

    save_chart(
        fig, "correlation_heatmap",
        tech_caption=(
            "Heatmap of Pearson correlations between 8 credit-stress signals "
            "(rows) and SPY forward returns at 6 horizons (1d, 5d, 21d, 63d, "
            "126d, 252d). Signals ranked descending by |correlation| at the "
            "63-day horizon; diverging RdBu_r palette centered at zero."
        ),
    )
    print("  NOTE: previous heatmap used 20 signals in alphabetical order.")
    print("  NEW  : canonical 8 signals in descending |corr|@63d order (Rule A3).")


# ---------------------------------------------------------------------------
# CHART 3 — Pre-whitened CCF bar plot
# ---------------------------------------------------------------------------

def chart_ccf_prewhitened() -> None:
    print("\n[3/5] CCF pre-whitened (new method chart)")
    df = pd.read_csv(CORE_DIR / "ccf_prewhitened.csv")

    colors = [COLOR_PRIMARY if sig else COLOR_NEUTRAL for sig in df["significant"]]
    ci_upper = df["upper_ci"].iloc[0]
    ci_lower = df["lower_ci"].iloc[0]
    lag0_val = df.loc[df["lag"] == 0, "ccf"].iloc[0]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["lag"], y=df["ccf"],
            marker=dict(color=colors),
            name="CCF",
            hovertemplate="Lag %{x}d<br>r = %{y:+.4f}<extra></extra>",
        )
    )
    # 95% CI reference lines
    fig.add_hline(y=ci_upper, line_dash="dot", line_color=COLOR_NEUTRAL,
                  annotation_text=f"+95% CI ({ci_upper:+.3f})",
                  annotation_position="top right",
                  annotation_font_size=10)
    fig.add_hline(y=ci_lower, line_dash="dot", line_color=COLOR_NEUTRAL,
                  annotation_text=f"−95% CI ({ci_lower:+.3f})",
                  annotation_position="bottom right",
                  annotation_font_size=10)
    fig.add_hline(y=0, line_color="black", line_width=1)

    # lag-0 callout
    fig.add_annotation(
        x=0, y=lag0_val,
        text=f"Lag 0 (same day)<br>r = {lag0_val:+.3f}",
        showarrow=True, arrowhead=2, ax=50, ay=-40,
        bgcolor="white", bordercolor="black", borderwidth=1,
        font=dict(size=11),
    )

    fig.update_layout(
        title=dict(
            text=(
                "Pre-whitened Cross-correlation: "
                "HY-IG Spread Changes vs SPY Returns"
            ),
            x=0.02, xanchor="left",
        ),
        xaxis=dict(
            title="Lag (days, negative = credit leads, positive = equity leads)",
            dtick=2,
        ),
        yaxis=dict(title="Cross-correlation coefficient"),
        template="plotly_white",
        height=480,
        showlegend=False,
        margin=dict(l=70, r=30, t=80, b=90),
        annotations=list(fig.layout.annotations) + [
            dict(
                x=0, y=-0.24, xref="paper", yref="paper",
                text=(
                    "Bars above the dotted line indicate statistically "
                    "significant lead-lag dynamics at 95% confidence. Blue = "
                    "significant, grey = not significant. Both series "
                    "pre-whitened via ARIMA(2,0,2) fit to HY-IG spread."
                ),
                showarrow=False, font=dict(size=10, color=COLOR_NEUTRAL),
                xanchor="left",
            ),
        ],
    )

    save_chart(
        fig, "ccf_prewhitened",
        tech_caption=(
            "Pre-whitened cross-correlation bars at lags −20 to +20 days "
            "between HY-IG spread changes and SPY log returns. Blue bars are "
            "significant at 95%, grey are not. Dotted lines mark ±1.96/√N "
            "significance bands."
        ),
    )


# ---------------------------------------------------------------------------
# CHART 4 — Transfer entropy bidirectional bar
# ---------------------------------------------------------------------------

def chart_transfer_entropy() -> None:
    print("\n[4/5] Transfer entropy (new method chart)")
    df = pd.read_csv(CORE_DIR / "transfer_entropy.csv")
    # Row order: credit_to_equity on top, equity_to_credit below
    order = ["credit_to_equity", "equity_to_credit"]
    df = df.set_index("direction").loc[order].reset_index()

    labels = ["Credit → Equity", "Equity → Credit"]
    values = df["te_value"].tolist()
    p_values = df["permutation_p_value"].tolist()
    colors = [
        COLOR_PRIMARY if p < 0.05 else COLOR_NEUTRAL
        for p in p_values
    ]
    annotations_text = [
        f"{v:.4f} nats (p = {p:.3f})"
        for v, p in zip(values, p_values)
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=labels, x=values, orientation="h",
            marker=dict(color=colors),
            text=annotations_text,
            textposition="outside",
            textfont=dict(size=12),
            hovertemplate="%{y}<br>TE = %{x:.4f} nats<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text="Transfer Entropy — Nonlinear Information Flow",
            x=0.02, xanchor="left",
        ),
        xaxis=dict(
            title="Transfer entropy (nats)",
            range=[0, max(values) * 1.5],
        ),
        yaxis=dict(title=""),
        template="plotly_white",
        height=360,
        showlegend=False,
        margin=dict(l=150, r=120, t=80, b=80),
        annotations=[
            dict(
                x=0, y=-0.30, xref="paper", yref="paper",
                text=(
                    "Longer bars = more information flowing in that "
                    "direction. Transfer entropy captures nonlinear "
                    "dependence beyond linear correlation. "
                    "Blue = significant at p < 0.05; grey = not significant. "
                    "Shannon histogram estimator, 6 quantile bins, lag 1d, "
                    "500 block-shift permutations."
                ),
                showarrow=False, font=dict(size=10, color=COLOR_NEUTRAL),
                xanchor="left",
            ),
        ],
    )

    save_chart(
        fig, "transfer_entropy",
        tech_caption=(
            "Bidirectional transfer entropy (nats) between HY-IG spread and "
            "SPY daily returns. Credit→Equity channel carries ~7.6× more "
            "information than the reverse. Blue = significant at p<0.05."
        ),
    )


# ---------------------------------------------------------------------------
# CHART 5 — Quartile returns grouped bar
# ---------------------------------------------------------------------------

def chart_quartile_returns() -> None:
    print("\n[5/5] Quartile returns (new method chart)")
    df = pd.read_csv(CORE_DIR / "quartile_returns.csv")
    df = df.sort_values("quartile").reset_index(drop=True)

    quartiles = df["quartile"].tolist()
    ann_returns_pct = (df["ann_return"] * 100).tolist()
    sharpes = df["sharpe"].tolist()
    n_obs = df["n_obs"].tolist()
    lower_bps = (df["cutoff_lower"] * 100).tolist()
    upper_bps = (df["cutoff_upper"] * 100).tolist()

    # Labels below each quartile: n=X days, spread Y-Z bps
    subcaptions = [
        f"n={n:,} days<br>spread {lo:.0f}-{hi:.0f} bps"
        for n, lo, hi in zip(n_obs, lower_bps, upper_bps)
    ]

    # Color Sharpe bars by annualized return (green positive, red negative)
    def color_for(ret_pct):
        if ret_pct > 0:
            return COLOR_TERTIARY
        return COLOR_SECOND

    bar_colors = [color_for(r) for r in ann_returns_pct]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=quartiles, y=sharpes,
            marker=dict(color=bar_colors),
            text=[f"Sharpe {s:+.2f}<br>Ann. {r:+.1f}%"
                  for s, r in zip(sharpes, ann_returns_pct)],
            textposition="outside",
            textfont=dict(size=11),
            hovertemplate=(
                "%{x}<br>Sharpe: %{y:.2f}<br>Ann. return: %{customdata:+.1f}%<extra></extra>"
            ),
            customdata=ann_returns_pct,
        )
    )
    fig.add_hline(y=0, line_color="black", line_width=1)

    # Sub-captions under each x-tick
    for q, sub in zip(quartiles, subcaptions):
        fig.add_annotation(
            x=q, y=0,
            xref="x", yref="paper",
            yshift=-40,
            text=sub,
            showarrow=False,
            font=dict(size=10, color=COLOR_NEUTRAL),
            align="center",
        )

    ymax = max(sharpes) + 0.4
    ymin = min(min(sharpes) - 0.4, -0.4)
    fig.update_layout(
        title=dict(
            text="SPY Performance Conditional on HY-IG Spread Quartile",
            x=0.02, xanchor="left",
        ),
        xaxis=dict(
            title="HY-IG Spread Quartile (Q1 = tightest, Q4 = widest)",
        ),
        yaxis=dict(
            title="Sharpe Ratio (dimensionless)",
            range=[ymin, ymax],
        ),
        template="plotly_white",
        height=520,
        showlegend=False,
        margin=dict(l=70, r=30, t=80, b=140),
        annotations=list(fig.layout.annotations) + [
            dict(
                x=0, y=-0.34, xref="paper", yref="paper",
                text=(
                    "Q1 = tightest spreads (calm), Q4 = widest spreads "
                    "(stress). Risk-adjusted returns collapse as spreads "
                    "widen. Bar color: green = positive annualized return, "
                    "red = negative."
                ),
                showarrow=False, font=dict(size=10, color=COLOR_NEUTRAL),
                xanchor="left",
            ),
        ],
    )

    save_chart(
        fig, "quartile_returns",
        tech_caption=(
            "SPY Sharpe ratio by HY-IG spread quartile (Q1 = tightest, "
            "Q4 = widest), with annualized return annotation and sample "
            "counts. Illustrates the credit-cycle gradient from Q1 Sharpe "
            "+1.45 to Q4 Sharpe −0.04."
        ),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("Retro fix — HY-IG v2 charts (Vera, 2026-04-11)")
    print("Applies SOP Rules A1-A5 to the 2026-04-10 production run.")
    print("=" * 72)

    chart_hero()
    chart_correlation_heatmap()
    chart_ccf_prewhitened()
    chart_transfer_entropy()
    chart_quartile_returns()

    print("\nDone.")


if __name__ == "__main__":
    main()
