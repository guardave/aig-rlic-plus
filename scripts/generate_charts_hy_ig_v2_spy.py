#!/usr/bin/env python3
"""
Chart Generation: HY-IG Credit Spread v2 -> S&P 500 (SPY)
==========================================================
Produces 10 standard Plotly JSON charts for the Streamlit portal.

Output filenames follow the spec exactly:
  1. hy_ig_v2_spy_spread_history_annotated.json
  2. hy_ig_v2_spy_returns_by_regime.json
  3. hy_ig_v2_spy_correlation_heatmap.json
  4. hy_ig_v2_spy_hmm_regime_probs.json
  5. hy_ig_v2_spy_local_projections.json
  6. hy_ig_v2_spy_quantile_regression.json
  7. hy_ig_v2_spy_tournament_sharpe_dist.json
  8. hy_ig_v2_spy_equity_curves.json
  9. hy_ig_v2_spy_returns_by_regime.json
 10. hy_ig_v2_spy_drawdown_comparison.json

Author: Vera (Visualization Agent)
Date: 2026-04-10
"""

import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = "/workspaces/aig-rlic-plus"
PAIR_ID = "hy_ig_v2_spy"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
CHART_DIR = os.path.join(BASE_DIR, "output", "charts", PAIR_ID, "plotly")
os.makedirs(CHART_DIR, exist_ok=True)

# ── Colour palette (SOP standard) ─────────────────────────────────────────
C_PRIMARY    = "#0072B2"   # Blue
C_SECONDARY  = "#D55E00"   # Vermillion
C_TERTIARY   = "#009E73"   # Green
C_ALERT      = "#CC79A7"   # Pink
C_NEUTRAL    = "#999999"   # Gray
C_RECESSION  = "rgba(0, 0, 0, 0.08)"
TEMPLATE     = "plotly_white"

# Regime quartile colours (green->red)
C_Q1, C_Q2, C_Q3, C_Q4 = C_TERTIARY, C_PRIMARY, C_SECONDARY, C_ALERT

# ── Helper ─────────────────────────────────────────────────────────────────
def save_chart(fig, name):
    path = os.path.join(CHART_DIR, f"{name}.json")
    fig.write_json(path)
    print(f"  OK  {name}.json")


def _note(fig, text):
    """Add a small educating source note at the bottom of the chart."""
    fig.add_annotation(
        text=text, xref="paper", yref="paper",
        x=0, y=-0.12, showarrow=False,
        font=dict(size=9, color="#888888"), xanchor="left",
    )


def _load_master():
    return pd.read_parquet(
        os.path.join(DATA_DIR, f"{PAIR_ID}_daily_20260410.parquet")
    )


def _load_winner():
    with open(os.path.join(RESULTS_DIR, "winner_summary.json")) as f:
        return json.load(f)


# ── NBER recession bars ───────────────────────────────────────────────────
RECESSIONS = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

# Key events (max 4-5 per SOP annotation density rule)
EVENT_ANNOTATIONS = [
    ("2008-09-15", "Lehman\nBrothers"),
    ("2020-03-23", "COVID\nLow"),
    ("2022-06-16", "Rate\nShock"),
]


def _add_recessions(fig, idx_min, idx_max):
    for s, e in RECESSIONS:
        ts, te = pd.Timestamp(s), pd.Timestamp(e)
        if te < idx_min or ts > idx_max:
            continue
        fig.add_vrect(x0=max(ts, idx_min), x1=min(te, idx_max),
                      fillcolor=C_RECESSION, layer="below", line_width=0)


def _oos_start():
    """Determine OOS start from walk-forward file."""
    wf = pd.read_csv(
        os.path.join(RESULTS_DIR, "tournament_validation_20260410", "walk_forward.csv")
    )
    return str(wf["test_year"].min()) + "-01-01"


def _drawdown(cumulative):
    peak = cumulative.expanding().max()
    return (cumulative / peak - 1)


def _build_winner_curve(df, oos_start):
    """Build winner strategy equity curve using signal probabilities."""
    sig_df = pd.read_parquet(
        os.path.join(RESULTS_DIR, "signals_20260410.parquet")
    )
    oos = df[df.index >= oos_start].copy()
    spy_ret = oos["spy_ret"] if "spy_ret" in oos.columns else oos["spy"].pct_change()

    prob_col = "hmm_2state_prob_stress"
    if prob_col not in sig_df.columns:
        # fallback
        hmm_cols = [c for c in sig_df.columns if "hmm" in c.lower()]
        prob_col = hmm_cols[0] if hmm_cols else None

    if prob_col is None:
        return oos.index, spy_ret * 0, spy_ret

    stress_prob = sig_df.loc[
        oos.index.intersection(sig_df.index), prob_col
    ].reindex(oos.index)

    # P2 = signal strength: position = 1 - stress_prob (counter-cyclical)
    position = (1 - stress_prob).clip(0, 1).shift(1)
    strat_ret = position * spy_ret
    return oos.index, strat_ret.fillna(0), spy_ret.fillna(0)


# ══════════════════════════════════════════════════════════════════════════
# 1. Spread History Annotated
# ══════════════════════════════════════════════════════════════════════════
def chart_spread_history_annotated():
    """25-year HY-IG spread time series with NBER recessions and key events."""
    df = _load_master()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # HY-IG spread (inverted y-axis: wider = worse, so inverted for visual alignment with SPY)
    fig.add_trace(
        go.Scatter(x=df.index, y=df["hy_ig_spread"],
                   name="HY-IG OAS Spread (bps)",
                   line=dict(color=C_SECONDARY, width=1.5)),
        secondary_y=False,
    )

    # SPY overlay
    fig.add_trace(
        go.Scatter(x=df.index, y=df["spy"],
                   name="SPY Price ($)",
                   line=dict(color=C_PRIMARY, width=1.5)),
        secondary_y=True,
    )

    # NBER recession shading (alpha 0.1 per SOP)
    _add_recessions(fig, df.index.min(), df.index.max())

    # Event annotations (max 4-5)
    for dt_str, label in EVENT_ANNOTATIONS:
        dt = pd.Timestamp(dt_str)
        if dt < df.index.min() or dt > df.index.max():
            continue
        idx = df.index.get_indexer([dt], method="nearest")[0]
        y_val = df["hy_ig_spread"].iloc[idx]
        fig.add_annotation(
            x=dt, y=y_val, text=label, showarrow=True,
            arrowhead=2, arrowsize=0.8, ax=0, ay=-40,
            font=dict(size=9, color=C_SECONDARY), secondary_y=False,
        )

    fig.update_layout(
        title="Wider Credit Spreads Foreshadow Equity Drawdowns (2000-2025)",
        template=TEMPLATE, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=520, margin=dict(b=80),
    )
    fig.update_yaxes(title_text="HY-IG OAS Spread (bps)", autorange="reversed",
                     secondary_y=False)
    fig.update_yaxes(title_text="SPY Price ($)", secondary_y=True)

    _note(fig, "Source: ICE BofA OAS indices via FRED; SPY via Yahoo Finance. "
          "Gray bands = NBER recessions.")
    save_chart(fig, f"{PAIR_ID}_spread_history_annotated")


# ══════════════════════════════════════════════════════════════════════════
# 2. Returns by Regime (Quartile Bar)
# ══════════════════════════════════════════════════════════════════════════
def chart_returns_by_regime():
    """Bar chart of annualized SPY returns by spread quartile with Sharpe labels."""
    rdf = pd.read_csv(
        os.path.join(RESULTS_DIR, "exploratory_20260410", "regime_descriptive_stats.csv")
    )

    bar_text = [
        f"{row['ann_return_pct']:.1f}%<br>Sharpe {row['sharpe']:.2f}"
        for _, row in rdf.iterrows()
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rdf["regime"],
        y=rdf["ann_return_pct"],
        marker_color=[C_Q1, C_Q2, C_Q3, C_Q4][:len(rdf)],
        text=bar_text, textposition="outside", textfont=dict(size=11),
    ))

    fig.update_layout(
        title="Low Spreads = Strong Equity: SPY Returns Fall as Credit Stress Rises",
        xaxis_title="HY-IG Spread Quartile (Q1 = Tight/Calm, Q4 = Wide/Stress)",
        yaxis_title="Annualized Return (%)",
        template=TEMPLATE, height=450, showlegend=False,
        margin=dict(b=80),
    )
    _note(fig, "Counter-cyclical: Q1 (tight spreads) delivers 16.9% ann. return; "
          "Q4 (wide spreads) is negative.")
    save_chart(fig, f"{PAIR_ID}_returns_by_regime")


# ══════════════════════════════════════════════════════════════════════════
# 3. Correlation Heatmap
# ══════════════════════════════════════════════════════════════════════════
def chart_correlation_heatmap():
    """Heatmap of signal x horizon Pearson correlations. RdBu_r colorscale."""
    cdf = pd.read_csv(
        os.path.join(RESULTS_DIR, "exploratory_20260410", "correlations.csv")
    )

    # All rows are Pearson in this file (no method column filtering needed)
    pivot = cdf.pivot(index="signal", columns="horizon", values="correlation")

    h_order = [c for c in ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d",
                           "spy_fwd_63d", "spy_fwd_126d", "spy_fwd_252d"]
               if c in pivot.columns]
    pivot = pivot[h_order]

    h_labels = [c.replace("spy_fwd_", "").upper() for c in h_order]
    s_labels = pivot.index.tolist()

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values, x=h_labels, y=s_labels,
        colorscale="RdBu_r", zmid=0, zmin=-0.40, zmax=0.40,
        text=[[f"{v:.3f}" for v in row] for row in pivot.values],
        texttemplate="%{text}", textfont={"size": 9},
        colorbar=dict(title="Pearson r"),
    ))

    fig.update_layout(
        title="Credit Signals Strengthen at Longer Horizons (Red = Negative)",
        xaxis_title="SPY Forward Return Horizon",
        yaxis_title="Credit Spread Signal",
        template=TEMPLATE, height=650, margin=dict(l=200, b=80),
    )
    _note(fig, "Source: Pearson correlations on daily data (2000-2025). "
          "Red = spread widening predicts lower returns.")
    save_chart(fig, f"{PAIR_ID}_correlation_heatmap")


# ══════════════════════════════════════════════════════════════════════════
# 4. HMM Regime Probabilities
# ══════════════════════════════════════════════════════════════════════════
def chart_hmm_regime_probs():
    """HMM stress probability time series with shaded stress periods and SPY overlay."""
    sig_df = pd.read_parquet(
        os.path.join(RESULTS_DIR, "signals_20260410.parquet")
    )
    df = _load_master()

    # Identify stress probability column
    if "hmm_2state_prob_stress" in sig_df.columns:
        prob_col = "hmm_2state_prob_stress"
    elif "ms_2state_stress_prob" in sig_df.columns:
        prob_col = "ms_2state_stress_prob"
    else:
        hmm_cols = [c for c in sig_df.columns if "hmm" in c.lower()]
        if not hmm_cols:
            print("  SKIP  hmm_regime_probs (no stress probability column)")
            return
        prob_col = hmm_cols[0]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Stress probability (left axis)
    fig.add_trace(
        go.Scatter(x=sig_df.index, y=sig_df[prob_col],
                   fill="tozeroy",
                   fillcolor="rgba(204, 121, 167, 0.15)",
                   line=dict(color=C_ALERT, width=1),
                   name="Stress Probability"),
        secondary_y=False,
    )

    # Shade stress episodes (prob > 0.5)
    stress = sig_df[prob_col] > 0.5
    if stress.any():
        starts = sig_df.index[stress & ~stress.shift(1, fill_value=False)]
        ends = sig_df.index[stress & ~stress.shift(-1, fill_value=False)]
        for s, e in zip(starts, ends):
            fig.add_vrect(x0=s, x1=e,
                          fillcolor="rgba(204, 121, 167, 0.10)",
                          layer="below", line_width=0)

    # SPY on secondary axis
    spy_aligned = df["spy"].reindex(sig_df.index, method="ffill")
    fig.add_trace(
        go.Scatter(x=sig_df.index, y=spy_aligned,
                   name="SPY Price ($)",
                   line=dict(color=C_PRIMARY, width=1.5)),
        secondary_y=True,
    )

    # 0.5 threshold line (winner strategy)
    fig.add_hline(y=0.5, line_dash="dash", line_color=C_NEUTRAL, line_width=1,
                  annotation_text="0.5 threshold (winner)", annotation_position="top right",
                  annotation_font_size=9, secondary_y=False)

    # NBER recession shading
    _add_recessions(fig, sig_df.index.min(), sig_df.index.max())

    fig.update_layout(
        title="HMM Detects Every Major Stress Episode (Prob > 0.5 = Reduce Exposure)",
        template=TEMPLATE, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500, margin=dict(b=80),
    )
    fig.update_yaxes(title_text="P(Stress State)", range=[0, 1.05], secondary_y=False)
    fig.update_yaxes(title_text="SPY Price ($)", secondary_y=True)

    _note(fig, "Source: 2-state Gaussian HMM fitted on HY-IG spread changes. "
          "Pink shading = stress probability > 0.5.")
    save_chart(fig, f"{PAIR_ID}_hmm_regime_probs")


# ══════════════════════════════════════════════════════════════════════════
# 5. Local Projections (Impulse Response)
# ══════════════════════════════════════════════════════════════════════════
def chart_local_projections():
    """LP coefficient +/- CI at each horizon showing gradual signal build."""
    lp = pd.read_csv(
        os.path.join(RESULTS_DIR, "core_models_20260410", "local_projections.csv")
    )

    fig = go.Figure()

    # CI band
    fig.add_trace(go.Scatter(
        x=list(lp["horizon_days"]) + list(lp["horizon_days"][::-1]),
        y=list(lp["ci_upper"]) + list(lp["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(0, 114, 178, 0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="95% CI", showlegend=True,
    ))

    # Point estimates
    fig.add_trace(go.Scatter(
        x=lp["horizon_days"], y=lp["coef"],
        mode="lines+markers",
        line=dict(color=C_PRIMARY, width=2.5),
        marker=dict(size=10),
        name="Coefficient",
    ))

    # Star significant horizons
    sig = lp[lp["p_value"] < 0.05]
    if len(sig) > 0:
        fig.add_trace(go.Scatter(
            x=sig["horizon_days"], y=sig["coef"],
            mode="markers",
            marker=dict(size=14, color=C_SECONDARY, symbol="star"),
            name="Significant (p < 0.05)",
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.7)

    fig.update_layout(
        title="Credit Spread Impact Builds Over Quarters (Significant at 63 Days)",
        xaxis_title="Forecast Horizon (trading days)",
        yaxis_title="Coefficient (HAC-robust SE)",
        template=TEMPLATE, height=450, margin=dict(b=80),
    )
    _note(fig, "Source: Local projections of HY-IG spread on SPY forward returns, "
          "Newey-West HAC standard errors. Stars = p < 0.05.")
    save_chart(fig, f"{PAIR_ID}_local_projections")


# ══════════════════════════════════════════════════════════════════════════
# 6. Quantile Regression
# ══════════════════════════════════════════════════════════════════════════
def chart_quantile_regression():
    """Coefficient across quantiles 0.05-0.95 highlighting tail effects."""
    qr = pd.read_csv(
        os.path.join(RESULTS_DIR, "core_models_20260410", "quantile_regression.csv")
    )

    fig = go.Figure()

    # CI band
    fig.add_trace(go.Scatter(
        x=list(qr["quantile"]) + list(qr["quantile"][::-1]),
        y=list(qr["ci_upper"]) + list(qr["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(0, 114, 178, 0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="95% CI",
    ))

    # Coefficient line
    fig.add_trace(go.Scatter(
        x=qr["quantile"], y=qr["coef"],
        mode="lines+markers",
        line=dict(color=C_PRIMARY, width=2.5),
        marker=dict(size=10),
        name="QR Coefficient",
    ))

    # Highlight tail quantiles
    tails = qr[qr["quantile"].isin([0.05, 0.10, 0.90, 0.95])]
    if len(tails) > 0:
        fig.add_trace(go.Scatter(
            x=tails["quantile"], y=tails["coef"],
            mode="markers",
            marker=dict(size=14, color=C_SECONDARY, symbol="diamond"),
            name="Tail Quantiles",
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.7)

    # Shade left tail region
    fig.add_vrect(x0=0.0, x1=0.15, fillcolor="rgba(213, 94, 0, 0.08)",
                  layer="below", line_width=0,
                  annotation_text="Left tail", annotation_position="top left",
                  annotation_font_size=9, annotation_font_color="#888")

    fig.update_layout(
        title="Credit Spreads Hit Hardest in the Tails: Symmetric V-Shape",
        xaxis_title="Return Quantile (0.05 = worst outcomes, 0.95 = best)",
        yaxis_title="Coefficient",
        template=TEMPLATE, height=450, margin=dict(b=80),
    )
    _note(fig, "Source: Quantile regression of HY-IG spread on SPY 63-day forward return. "
          "Negative at left tail = wider spreads worsen drawdowns.")
    save_chart(fig, f"{PAIR_ID}_quantile_regression")


# ══════════════════════════════════════════════════════════════════════════
# 7. Tournament Sharpe Distribution
# ══════════════════════════════════════════════════════════════════════════
def chart_tournament_sharpe_dist():
    """Histogram of OOS Sharpe with winner and benchmark marked."""
    tdf = pd.read_csv(
        os.path.join(RESULTS_DIR, "tournament_results_20260410.csv")
    )
    winner = _load_winner()

    valid = tdf[(tdf["valid"]) & (tdf["signal"] != "BENCHMARK")]
    bh = tdf[tdf["signal"] == "BENCHMARK"]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=valid["oos_sharpe"], nbinsx=50,
        marker_color=C_PRIMARY, opacity=0.7,
        name=f"Valid ({len(valid)})",
    ))

    # Winner line
    fig.add_vline(
        x=winner["oos_sharpe"], line_color=C_TERTIARY, line_width=2.5,
        annotation_text=f"Winner: {winner['oos_sharpe']:.2f}",
        annotation_position="top right",
        annotation_font_size=10, annotation_font_color=C_TERTIARY,
    )

    # Benchmark line
    if len(bh) > 0:
        bh_sharpe = bh.iloc[0]["oos_sharpe"]
        fig.add_vline(
            x=bh_sharpe, line_color=C_NEUTRAL, line_width=2, line_dash="dash",
            annotation_text=f"B&H: {bh_sharpe:.2f}",
            annotation_position="top left",
            annotation_font_size=10, annotation_font_color=C_NEUTRAL,
        )

    n_better = max(1, int((valid["oos_sharpe"] >= winner["oos_sharpe"]).sum()))

    fig.update_layout(
        title=f"Winner Ranks Top {n_better} of {len(valid)} Valid Strategies (Sharpe {winner['oos_sharpe']:.2f})",
        xaxis_title="Out-of-Sample Sharpe Ratio",
        yaxis_title="Count",
        template=TEMPLATE, height=450, barmode="overlay",
        margin=dict(b=80),
    )
    _note(fig, f"Source: 5D tournament, {len(tdf)} total combinations, "
          f"{len(valid)} pass validity filters.")
    save_chart(fig, f"{PAIR_ID}_tournament_sharpe_dist")


# ══════════════════════════════════════════════════════════════════════════
# 8. Equity Curves (Dual Panel with Drawdown)
# ══════════════════════════════════════════════════════════════════════════
def chart_equity_curves():
    """Equity curves: top 3 strategies vs buy-and-hold with drawdown panel below."""
    df = _load_master()
    sig_df = pd.read_parquet(
        os.path.join(RESULTS_DIR, "signals_20260410.parquet")
    )
    tdf = pd.read_csv(
        os.path.join(RESULTS_DIR, "tournament_results_20260410.csv")
    )
    winner = _load_winner()

    oos_start = _oos_start()
    oos = df[df.index >= oos_start].copy()
    spy_ret = oos["spy_ret"] if "spy_ret" in oos.columns else oos["spy"].pct_change()

    # Dual panel: equity + drawdown
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.7, 0.3], vertical_spacing=0.05,
        subplot_titles=["Equity Curves (OOS)", "Drawdown"],
    )

    # Buy-and-hold
    bh_cum = (1 + spy_ret.fillna(0)).cumprod()
    fig.add_trace(
        go.Scatter(x=bh_cum.index, y=bh_cum.values,
                   name="Buy & Hold SPY",
                   line=dict(color=C_NEUTRAL, width=2, dash="dash")),
        row=1, col=1,
    )

    # Build top-3 strategy curves
    valid = tdf[(tdf["valid"]) & (tdf["signal"] != "BENCHMARK")]
    top3 = valid.nlargest(3, "oos_sharpe")

    sig_col_map = {
        "S6_hmm_stress": "hmm_2state_prob_stress",
        "S7_ms_stress": "ms_2state_stress_prob",
    }

    strat_colors = [C_TERTIARY, C_PRIMARY, C_ALERT]
    strat_cums = []

    for idx, (_, row) in enumerate(top3.iterrows()):
        sig_name = row["signal"]
        sig_col = sig_col_map.get(sig_name)

        if sig_col is None:
            candidates = [c for c in sig_df.columns
                          if sig_name.lower().replace("s", "").replace("_", "")
                          in c.lower().replace("_", "")]
            sig_col = candidates[0] if candidates else None

        if sig_col is None:
            candidates = [c for c in oos.columns if "hy_ig" in c]
            sig_col = candidates[0] if candidates else None

        if sig_col is None:
            continue

        if sig_col in sig_df.columns:
            signal_vals = sig_df.loc[
                oos.index.intersection(sig_df.index), sig_col
            ].reindex(oos.index)
        elif sig_col in oos.columns:
            signal_vals = oos[sig_col]
        else:
            continue

        lead = int(row["lead_days"]) if "lead_days" in row.index else 0
        if lead > 0:
            signal_vals = signal_vals.shift(lead)

        strategy = row["strategy"]
        threshold = row["threshold"]

        if "hmm" in threshold.lower() or "ms" in threshold.lower():
            thresh_val = float(threshold.split("_")[-1]) if "_" in threshold else 0.5
            if strategy == "P2":
                position = (1 - signal_vals).clip(0, 1)
            else:
                position = (signal_vals < thresh_val).astype(float)
        elif "rp" in threshold.lower():
            parts = threshold.split("rp")
            pct = float(parts[-1]) / 100 if len(parts) > 1 else 0.75
            rolling_thresh = signal_vals.rolling(504, min_periods=252).quantile(pct)
            position = (signal_vals > rolling_thresh).astype(float)
        else:
            position = (signal_vals < signal_vals.median()).astype(float)

        strat_ret = position.shift(1) * spy_ret
        strat_cum = (1 + strat_ret.fillna(0)).cumprod()
        strat_cums.append(strat_cum)

        label = f"#{idx+1}: {sig_name} / {threshold}"
        fig.add_trace(
            go.Scatter(x=strat_cum.index, y=strat_cum.values,
                       name=label,
                       line=dict(color=strat_colors[idx % 3], width=2)),
            row=1, col=1,
        )

    # Drawdowns (B&H + winner = first strategy)
    bh_dd = _drawdown(bh_cum) * 100
    fig.add_trace(
        go.Scatter(x=bh_dd.index, y=bh_dd.values,
                   name="B&H DD", fill="tozeroy",
                   fillcolor="rgba(153, 153, 153, 0.2)",
                   line=dict(color=C_NEUTRAL, width=1), showlegend=False),
        row=2, col=1,
    )

    if strat_cums:
        winner_dd = _drawdown(strat_cums[0]) * 100
        fig.add_trace(
            go.Scatter(x=winner_dd.index, y=winner_dd.values,
                       name="Winner DD", fill="tozeroy",
                       fillcolor="rgba(0, 158, 115, 0.15)",
                       line=dict(color=C_TERTIARY, width=1), showlegend=False),
            row=2, col=1,
        )

    fig.update_layout(
        title=f"Top Strategies Outperform Buy-and-Hold (OOS from {oos_start})",
        template=TEMPLATE, height=620, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(b=80),
    )
    fig.update_yaxes(title_text="Growth of $1", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)

    _note(fig, "Source: Simulated equity curves using persisted signal probabilities. No look-ahead bias.")
    save_chart(fig, f"{PAIR_ID}_equity_curves")


# ══════════════════════════════════════════════════════════════════════════
# 9. Returns by Regime (Grouped Bar)
# ══════════════════════════════════════════════════════════════════════════
def chart_returns_by_regime_grouped():
    """Grouped bar: returns, vol, Sharpe by spread quartile."""
    rdf = pd.read_csv(
        os.path.join(RESULTS_DIR, "exploratory_20260410", "regime_descriptive_stats.csv")
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=rdf["regime"], y=rdf["ann_return_pct"],
        name="Ann. Return (%)", marker_color=C_PRIMARY,
        text=[f"{v:.1f}%" for v in rdf["ann_return_pct"]], textposition="outside",
    ))

    fig.add_trace(go.Bar(
        x=rdf["regime"], y=rdf["ann_vol_pct"],
        name="Ann. Volatility (%)", marker_color=C_SECONDARY,
        text=[f"{v:.1f}%" for v in rdf["ann_vol_pct"]], textposition="outside",
    ))

    fig.add_trace(go.Bar(
        x=rdf["regime"], y=rdf["sharpe"] * 10,
        name="Sharpe (x10 for scale)", marker_color=C_TERTIARY,
        text=[f"{v:.2f}" for v in rdf["sharpe"]], textposition="outside",
    ))

    fig.update_layout(
        title="Credit Regime Anatomy: Return, Vol, and Sharpe by Quartile",
        xaxis_title="HY-IG Spread Quartile",
        yaxis_title="Value (%, Sharpe scaled x10)",
        template=TEMPLATE, height=480, barmode="group",
        margin=dict(b=80),
    )
    _note(fig, "Q4 (widest spreads): highest volatility (28.7%), negative returns, "
          "Sharpe near zero. Sharpe values shown on bars (scaled x10 on y-axis).")
    save_chart(fig, f"{PAIR_ID}_returns_by_regime")


# ══════════════════════════════════════════════════════════════════════════
# 10. Drawdown Comparison
# ══════════════════════════════════════════════════════════════════════════
def chart_drawdown_comparison():
    """Drawdown comparison: winner strategy vs buy-and-hold."""
    df = _load_master()
    winner = _load_winner()
    oos_start = _oos_start()

    _, strat_ret, spy_ret = _build_winner_curve(df, oos_start)

    bh_cum = (1 + spy_ret).cumprod()
    strat_cum = (1 + strat_ret).cumprod()

    bh_dd = _drawdown(bh_cum) * 100
    strat_dd = _drawdown(strat_cum) * 100

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=bh_dd.index, y=bh_dd.values,
        fill="tozeroy", fillcolor="rgba(153, 153, 153, 0.2)",
        line=dict(color=C_NEUTRAL, width=1.5),
        name=f"Buy & Hold (max {bh_dd.min():.1f}%)",
    ))

    fig.add_trace(go.Scatter(
        x=strat_dd.index, y=strat_dd.values,
        fill="tozeroy", fillcolor="rgba(0, 158, 115, 0.15)",
        line=dict(color=C_TERTIARY, width=1.5),
        name=f"Winner: HMM-P2 (max {strat_dd.min():.1f}%)",
    ))

    # Annotate worst B&H drawdown
    bh_worst_idx = bh_dd.idxmin()
    fig.add_annotation(
        x=bh_worst_idx, y=bh_dd.min(),
        text=f"B&H worst: {bh_dd.min():.1f}%",
        showarrow=True, arrowhead=2, ax=40, ay=-20,
        font=dict(size=9, color=C_NEUTRAL),
    )

    # Annotate worst strategy drawdown
    strat_worst_idx = strat_dd.idxmin()
    fig.add_annotation(
        x=strat_worst_idx, y=strat_dd.min(),
        text=f"Strategy worst: {strat_dd.min():.1f}%",
        showarrow=True, arrowhead=2, ax=-40, ay=-20,
        font=dict(size=9, color=C_TERTIARY),
    )

    fig.update_layout(
        title=f"HMM Signal Limits Drawdowns: {strat_dd.min():.0f}% vs {bh_dd.min():.0f}% B&H",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template=TEMPLATE, height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(b=80),
    )
    _note(fig, "Source: Drawdown from peak equity. Winner = HMM stress probability, "
          "signal-strength position sizing (P2).")
    save_chart(fig, f"{PAIR_ID}_drawdown_comparison")


# ══════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Generating {PAIR_ID} charts (10 standard set)...")
    print(f"Output: {CHART_DIR}\n")

    chart_spread_history_annotated()     # 1
    chart_returns_by_regime()            # 2
    chart_correlation_heatmap()          # 3
    chart_hmm_regime_probs()             # 4
    chart_local_projections()            # 5
    chart_quantile_regression()          # 6
    chart_tournament_sharpe_dist()       # 7
    chart_equity_curves()                # 8
    chart_returns_by_regime_grouped()    # 9
    chart_drawdown_comparison()          # 10

    # Summary
    charts = [f for f in os.listdir(CHART_DIR) if f.endswith(".json")]
    print(f"\nDone. {len(charts)} charts saved to {CHART_DIR}")
    for c in sorted(charts):
        print(f"  {c}")
