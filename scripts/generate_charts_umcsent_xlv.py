#!/usr/bin/env python3
"""
Chart Generation: Michigan Consumer Sentiment (UMCSENT) × XLV
=============================================================
Produces the standard 10-chart Plotly JSON set for the Streamlit portal.

Charts:
  1. umcsent_xlv_hero           -- UMCSENT YoY vs XLV price (dual-axis)
  2. umcsent_xlv_correlations   -- Pearson correlation heatmap
  3. umcsent_xlv_regime_stats   -- XLV returns by UMCSENT quartile
  4. umcsent_xlv_ccf            -- Cross-correlation function
  5. umcsent_xlv_equity_curves  -- Winner equity curve vs B&H
  6. umcsent_xlv_drawdown       -- Drawdown comparison
  7. umcsent_xlv_rolling_sharpe -- Rolling 12M Sharpe
  8. umcsent_xlv_tournament_scatter -- Sharpe vs MDD scatter
  9. umcsent_xlv_signal_dist    -- Signal distribution / direction breakdown
  10. umcsent_xlv_wf_sharpe     -- Walk-forward OOS rolling Sharpe

Author: Econ Evan (Econometrics Agent)
Date: 2026-04-20
"""

import os
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = str(Path(__file__).resolve().parents[1])
PAIR_ID = "umcsent_xlv"
DATE_TAG = "20260420"
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "output", "charts", PAIR_ID, "plotly")
os.makedirs(CHART_DIR, exist_ok=True)

# Color palette
C_INDICATOR = "#d62728"    # Red for UMCSENT
C_EQUITY = "#1f77b4"       # Blue for XLV
C_STRATEGY = "#2ca02c"     # Green for strategy
C_BENCHMARK = "#7f7f7f"    # Gray for benchmark
C_SPY = "#ff7f0e"          # Orange for SPY
C_CONTRACTION = "rgba(214, 39, 40, 0.12)"


def save_chart(fig, name):
    path = os.path.join(CHART_DIR, f"{name}.json")
    fig.write_json(path)
    print(f"  Saved: {name}.json")


def load_monthly():
    """Load the monthly dataset."""
    parquet_path = os.path.join(DATA_DIR, "umcsent_xlv_monthly_19980101_20251231.parquet")
    return pd.read_parquet(parquet_path)


def load_tournament():
    return pd.read_csv(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv"))


def load_winner():
    with open(os.path.join(RESULTS_DIR, "winner_summary.json")) as f:
        return json.load(f)


# ===================================================================
# CHART 1: Hero — UMCSENT YoY vs XLV price (dual-axis)
# ===================================================================
def chart_hero():
    df = load_monthly()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # UMCSENT YoY on primary axis
    yoy_valid = df["umcsent_yoy"].dropna()
    fig.add_trace(
        go.Scatter(x=yoy_valid.index, y=yoy_valid.values,
                   name="UMCSENT YoY Change (%)",
                   line=dict(color=C_INDICATOR, width=2)),
        secondary_y=False,
    )

    # XLV price on secondary axis
    fig.add_trace(
        go.Scatter(x=df.index, y=df["xlv"],
                   name="XLV Price ($)",
                   line=dict(color=C_EQUITY, width=1.5)),
        secondary_y=True,
    )

    # Shade periods when UMCSENT YoY < 0 (pessimism)
    if "umcsent_yoy" in df.columns:
        pessimism = df["umcsent_yoy"] < 0
        starts = pessimism.index[pessimism & ~pessimism.shift(1, fill_value=False)]
        ends = pessimism.index[pessimism & ~pessimism.shift(-1, fill_value=False)]
        for s, e in zip(starts, ends):
            fig.add_vrect(x0=s, x1=e, fillcolor=C_CONTRACTION,
                          layer="below", line_width=0)

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5,
                  secondary_y=False)

    fig.update_layout(
        title="Michigan Consumer Sentiment YoY Change vs XLV Price (1999-2025)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    )
    fig.update_yaxes(title_text="UMCSENT YoY Change (%)", secondary_y=False)
    fig.update_yaxes(title_text="XLV Price ($)", secondary_y=True)
    save_chart(fig, f"{PAIR_ID}_hero")


# ===================================================================
# CHART 2: Correlation heatmap
# ===================================================================
def chart_correlations():
    corr_df = pd.read_csv(os.path.join(EXPLORE_DIR, "correlations.csv"))
    pearson = corr_df[corr_df["method"] == "Pearson"]

    pivot = pearson.pivot(index="signal", columns="horizon", values="correlation")
    col_order = [c for c in ["xlv_fwd_1m", "xlv_fwd_3m", "xlv_fwd_6m", "xlv_fwd_12m"]
                 if c in pivot.columns]
    pivot = pivot[col_order]

    # Clean axis labels
    row_labels = [s.replace("umcsent_", "UMCSENT ").replace("_", " ") for s in pivot.index]
    col_labels = [c.replace("xlv_fwd_", "").upper() for c in pivot.columns]

    # Mark significance
    pivot_p = pearson.pivot(index="signal", columns="horizon", values="p_value")[col_order]
    annot = []
    for i, row in enumerate(pivot.index):
        r = []
        for j, col in enumerate(pivot.columns):
            val = pivot.loc[row, col]
            p = pivot_p.loc[row, col]
            star = "**" if p < 0.01 else ("*" if p < 0.05 else "")
            r.append(f"{val:.3f}{star}")
        annot.append(r)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=col_labels,
        y=row_labels,
        colorscale="RdBu",
        zmid=0,
        zmin=-0.3, zmax=0.3,
        text=annot,
        texttemplate="%{text}",
        textfont={"size": 10},
    ))

    fig.update_layout(
        title="Pearson Correlation: UMCSENT Signals → XLV Forward Returns<br><sup>* p<0.05, ** p<0.01</sup>",
        xaxis_title="XLV Forward Return Horizon",
        yaxis_title="Signal",
        template="plotly_white",
        height=450,
    )
    save_chart(fig, f"{PAIR_ID}_correlations")


# ===================================================================
# CHART 3: Regime stats bar chart
# ===================================================================
def chart_regime_stats():
    regime_df = pd.read_csv(os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv"))

    colors = [C_INDICATOR, "#ff7f0e", C_EQUITY, C_STRATEGY]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Annualized Sharpe by UMCSENT YoY Quartile",
                                        "Annualized Return by UMCSENT YoY Quartile"])

    fig.add_trace(go.Bar(
        x=regime_df["regime"], y=regime_df["sharpe"],
        name="Sharpe",
        marker_color=colors,
        text=[f"{v:.2f}" for v in regime_df["sharpe"]],
        textposition="outside",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=regime_df["regime"], y=regime_df["ann_return_pct"],
        name="Ann Return %",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in regime_df["ann_return_pct"]],
        textposition="outside",
    ), row=1, col=2)

    fig.update_layout(
        template="plotly_white",
        height=450,
        showlegend=False,
    )
    fig.update_xaxes(title_text="Sentiment YoY Quartile (Q1=Low, Q4=High)")
    fig.update_yaxes(title_text="Annualized Sharpe", row=1, col=1)
    fig.update_yaxes(title_text="Annualized Return (%)", row=1, col=2)
    save_chart(fig, f"{PAIR_ID}_regime_stats")


# ===================================================================
# CHART 4: CCF bar chart
# ===================================================================
def chart_ccf():
    ccf_df = pd.read_csv(os.path.join(EXPLORE_DIR, "ccf.csv"))

    colors = [C_INDICATOR if sig else "#aec7e8" for sig in ccf_df["significant"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ccf_df["lag"], y=ccf_df["ccf"],
        marker_color=colors,
        name="CCF",
    ))

    if len(ccf_df) > 0:
        se = ccf_df["se"].iloc[0]
        fig.add_hline(y=1.96 * se, line_dash="dash", line_color="gray", line_width=0.8,
                      annotation_text="95% CI")
        fig.add_hline(y=-1.96 * se, line_dash="dash", line_color="gray", line_width=0.8)

    fig.update_layout(
        title="Cross-Correlation: UMCSENT YoY Change vs XLV Monthly Return<br><sup>Red bars = statistically significant at 95%</sup>",
        xaxis_title="Lag (months; negative = UMCSENT leads XLV)",
        yaxis_title="Cross-Correlation",
        template="plotly_white",
        height=400,
    )
    save_chart(fig, f"{PAIR_ID}_ccf")


# ===================================================================
# CHART 5: Equity curves (winner vs buy-and-hold)
# ===================================================================
def chart_equity_curves():
    df = load_monthly()
    winner = load_winner()
    tourn_df = load_tournament()

    oos_start = winner["oos_start"]
    oos = df[df.index >= oos_start].copy()

    if "xlv_ret" not in oos.columns:
        oos["xlv_ret"] = oos["xlv"].pct_change()

    fig = go.Figure()

    # Buy-and-hold XLV
    bh_cum = (1 + oos["xlv_ret"].fillna(0)).cumprod()
    fig.add_trace(go.Scatter(
        x=bh_cum.index, y=bh_cum.values,
        name="Buy & Hold XLV",
        line=dict(color=C_BENCHMARK, width=2, dash="dash"),
    ))

    # SPY as second benchmark
    if "spy_ret" in oos.columns:
        spy_cum = (1 + oos["spy_ret"].fillna(0)).cumprod()
        fig.add_trace(go.Scatter(
            x=spy_cum.index, y=spy_cum.values,
            name="Buy & Hold SPY",
            line=dict(color=C_SPY, width=1.5, dash="dot"),
        ))

    # Top strategies
    valid_strats = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid_strats) > 0:
        top3 = valid_strats.nlargest(3, "oos_sharpe")
        colors_strat = [C_STRATEGY, C_INDICATOR, C_EQUITY]

        is_end = winner["is_end"]
        sig_col_map = {
            "S1_level":     "umcsent",
            "S2_yoy":       "umcsent_yoy",
            "S3_mom":       "umcsent_mom",
            "S4_zscore":    "umcsent_zscore",
            "S5_3m_ma":     "umcsent_3m_ma",
            "S6_direction": "umcsent_direction",
            "S7_dev_ma":    "umcsent_dev_ma",
        }

        for idx, (_, row) in enumerate(top3.iterrows()):
            sig_col = sig_col_map.get(row["signal"])
            if sig_col is None or sig_col not in oos.columns:
                continue

            signal = oos[sig_col].shift(int(row["lead_months"]))

            # Reconstruct threshold
            try:
                thresh_name = row["threshold"]
                if "T1_fixed" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    is_data = df[df.index <= is_end]
                    thresh = is_data[sig_col].quantile(pct / 100) if sig_col in is_data.columns else 0
                elif "T2_roll" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    thresh = signal.rolling(60, min_periods=36).quantile(pct / 100)
                elif "T4_zero" in thresh_name:
                    thresh = 0
                else:
                    continue

                if isinstance(thresh, (int, float)):
                    position = (signal < thresh).astype(float)  # countercyclical
                else:
                    position = (signal < thresh).astype(float)

                strat_ret = position.shift(1) * oos["xlv_ret"]
                strat_cum = (1 + strat_ret.fillna(0)).cumprod()

                label = f"#{idx+1}: {row['signal']}/L{row['lead_months']}"
                fig.add_trace(go.Scatter(
                    x=strat_cum.index, y=strat_cum.values,
                    name=label,
                    line=dict(color=colors_strat[idx], width=2),
                ))
            except Exception as e:
                print(f"    Equity curve #{idx+1} failed: {e}")

    fig.update_layout(
        title=f"Equity Curves: Top Strategies vs Buy-and-Hold (OOS {oos_start[:7]} – 2025-12)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return ($1 invested)",
        template="plotly_white",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    save_chart(fig, f"{PAIR_ID}_equity_curves")


# ===================================================================
# CHART 6: Drawdown comparison
# ===================================================================
def chart_drawdown():
    df = load_monthly()
    winner = load_winner()
    tourn_df = load_tournament()

    oos_start = winner["oos_start"]
    oos = df[df.index >= oos_start].copy()
    if "xlv_ret" not in oos.columns:
        oos["xlv_ret"] = oos["xlv"].pct_change()

    fig = go.Figure()

    # B&H drawdown
    bh_cum = (1 + oos["xlv_ret"].fillna(0)).cumprod()
    bh_dd = (bh_cum / bh_cum.cummax() - 1)
    fig.add_trace(go.Scatter(
        x=bh_dd.index, y=bh_dd.values * 100,
        name="Buy & Hold XLV",
        fill="tozeroy",
        fillcolor="rgba(127,127,127,0.15)",
        line=dict(color=C_BENCHMARK, width=1.5, dash="dash"),
    ))

    # Winner strategy drawdown
    valid_strats = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid_strats) > 0:
        best = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
        sig_col_map = {
            "S1_level":     "umcsent",
            "S2_yoy":       "umcsent_yoy",
            "S3_mom":       "umcsent_mom",
            "S4_zscore":    "umcsent_zscore",
            "S5_3m_ma":     "umcsent_3m_ma",
            "S6_direction": "umcsent_direction",
            "S7_dev_ma":    "umcsent_dev_ma",
        }
        sig_col = sig_col_map.get(best["signal"])
        if sig_col and sig_col in oos.columns:
            try:
                signal = oos[sig_col].shift(int(best["lead_months"]))
                is_end = winner["is_end"]
                thresh_name = best["threshold"]
                if "T1_fixed" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    is_data = df[df.index <= is_end]
                    thresh = is_data[sig_col].quantile(pct / 100)
                elif "T4_zero" in thresh_name:
                    thresh = 0
                else:
                    thresh = 0

                position = (signal < thresh).astype(float)
                strat_ret = position.shift(1) * oos["xlv_ret"]
                strat_cum = (1 + strat_ret.fillna(0)).cumprod()
                strat_dd = (strat_cum / strat_cum.cummax() - 1)

                fig.add_trace(go.Scatter(
                    x=strat_dd.index, y=strat_dd.values * 100,
                    name=f"Winner: {best['signal']}/L{best['lead_months']}",
                    fill="tozeroy",
                    fillcolor="rgba(44,160,44,0.15)",
                    line=dict(color=C_STRATEGY, width=2),
                ))
            except Exception as e:
                print(f"    Drawdown strategy failed: {e}")

    fig.update_layout(
        title="Drawdown Comparison: Winner Strategy vs Buy-and-Hold XLV",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    save_chart(fig, f"{PAIR_ID}_drawdown")


# ===================================================================
# CHART 7: Rolling Sharpe
# ===================================================================
def chart_rolling_sharpe():
    df = load_monthly()
    winner = load_winner()
    tourn_df = load_tournament()

    oos_start = winner["oos_start"]
    oos = df[df.index >= oos_start].copy()
    if "xlv_ret" not in oos.columns:
        oos["xlv_ret"] = oos["xlv"].pct_change()

    fig = go.Figure()

    # B&H rolling Sharpe (12M)
    bh_roll = oos["xlv_ret"].rolling(12, min_periods=8)
    bh_sharpe = (bh_roll.mean() / bh_roll.std()) * np.sqrt(12)
    fig.add_trace(go.Scatter(
        x=bh_sharpe.index, y=bh_sharpe.values,
        name="Buy & Hold XLV",
        line=dict(color=C_BENCHMARK, width=1.5, dash="dash"),
    ))

    # Winner strategy rolling Sharpe
    valid_strats = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid_strats) > 0:
        best = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
        sig_col_map = {
            "S1_level":     "umcsent",
            "S2_yoy":       "umcsent_yoy",
            "S3_mom":       "umcsent_mom",
            "S4_zscore":    "umcsent_zscore",
            "S5_3m_ma":     "umcsent_3m_ma",
            "S6_direction": "umcsent_direction",
            "S7_dev_ma":    "umcsent_dev_ma",
        }
        sig_col = sig_col_map.get(best["signal"])
        if sig_col and sig_col in oos.columns:
            try:
                signal = oos[sig_col].shift(int(best["lead_months"]))
                is_end = winner["is_end"]
                thresh_name = best["threshold"]
                if "T1_fixed" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    is_data = df[df.index <= is_end]
                    thresh = is_data[sig_col].quantile(pct / 100)
                elif "T4_zero" in thresh_name:
                    thresh = 0
                else:
                    thresh = 0

                position = (signal < thresh).astype(float)
                strat_ret = position.shift(1) * oos["xlv_ret"]
                strat_roll = strat_ret.rolling(12, min_periods=8)
                strat_sharpe = (strat_roll.mean() / strat_roll.std()) * np.sqrt(12)

                fig.add_trace(go.Scatter(
                    x=strat_sharpe.index, y=strat_sharpe.values,
                    name=f"Winner: {best['signal']}/L{best['lead_months']}",
                    line=dict(color=C_STRATEGY, width=2),
                ))
            except Exception as e:
                print(f"    Rolling Sharpe strategy failed: {e}")

    fig.add_hline(y=0, line_dash="dash", line_color="red", line_width=0.5)

    fig.update_layout(
        title="Rolling 12-Month Sharpe Ratio (OOS Period)",
        xaxis_title="Date",
        yaxis_title="Rolling Sharpe (12M)",
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    save_chart(fig, f"{PAIR_ID}_rolling_sharpe")


# ===================================================================
# CHART 8: Tournament scatter (Sharpe vs MDD)
# ===================================================================
def chart_tournament_scatter():
    tourn_df = load_tournament()

    valid = tourn_df[(tourn_df["valid"]) & (tourn_df["signal"] != "BENCHMARK")]
    invalid = tourn_df[(~tourn_df["valid"]) & (tourn_df["signal"] != "BENCHMARK")]
    benchmark = tourn_df[tourn_df["signal"] == "BENCHMARK"]

    fig = go.Figure()

    if len(invalid) > 0:
        fig.add_trace(go.Scatter(
            x=invalid["annual_turnover"], y=invalid["oos_sharpe"],
            mode="markers",
            marker=dict(size=3, color="#cccccc", opacity=0.2),
            name="Invalid",
        ))

    if len(valid) > 0:
        dd_pct = valid["max_drawdown"] * 100
        fig.add_trace(go.Scatter(
            x=valid["annual_turnover"], y=valid["oos_sharpe"],
            mode="markers",
            marker=dict(
                size=5,
                color=dd_pct,
                colorscale="RdYlGn",
                colorbar=dict(title="Max DD (%)"),
                opacity=0.6,
            ),
            text=[f"{r['signal']}/{r['threshold']}/{r['strategy']}" for _, r in valid.iterrows()],
            hovertemplate="%{text}<br>Sharpe: %{y:.2f}<br>Turnover: %{x:.1f}<extra></extra>",
            name="Valid Strategies",
        ))

    if len(benchmark) > 0:
        fig.add_trace(go.Scatter(
            x=[benchmark.iloc[0]["annual_turnover"]],
            y=[benchmark.iloc[0]["oos_sharpe"]],
            mode="markers",
            marker=dict(size=14, color=C_BENCHMARK, symbol="diamond"),
            name="Buy-and-Hold XLV",
        ))

    top5 = valid.nlargest(5, "oos_sharpe") if len(valid) > 0 else pd.DataFrame()
    if len(top5) > 0:
        fig.add_trace(go.Scatter(
            x=top5["annual_turnover"], y=top5["oos_sharpe"],
            mode="markers",
            marker=dict(size=12, color=C_STRATEGY, symbol="star", line=dict(width=1, color="black")),
            name="Top 5",
        ))

    fig.update_layout(
        title=f"Tournament Results: {len(tourn_df):,} Combinations ({len(valid):,} Valid)",
        xaxis_title="Annual Turnover (trades/year)",
        yaxis_title="OOS Sharpe Ratio",
        template="plotly_white",
        height=500,
    )
    save_chart(fig, f"{PAIR_ID}_tournament_scatter")


# ===================================================================
# CHART 9: Signal distribution / direction breakdown
# ===================================================================
def chart_signal_dist():
    df = load_monthly()
    winner_data = load_winner()
    is_end = winner_data["is_end"]
    oos_start = winner_data["oos_start"]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["UMCSENT YoY Distribution",
                                        "XLV Returns: YoY Rising vs Falling Sentiment"])

    yoy = df["umcsent_yoy"].dropna()

    # Histogram of YoY values
    fig.add_trace(go.Histogram(
        x=yoy.values,
        nbinsx=40,
        name="UMCSENT YoY",
        marker_color=C_INDICATOR,
        opacity=0.7,
    ), row=1, col=1)
    fig.add_vline(x=0, line_dash="dash", line_color="black", row=1, col=1)

    # XLV returns when sentiment is rising vs falling (direction signal)
    valid = df[["umcsent_direction", "xlv_fwd_3m"]].dropna()
    rising = valid.loc[valid["umcsent_direction"] > 0, "xlv_fwd_3m"] * 100
    falling = valid.loc[valid["umcsent_direction"] < 0, "xlv_fwd_3m"] * 100

    fig.add_trace(go.Box(
        y=rising.values,
        name=f"Rising Sentiment (n={len(rising)})",
        marker_color=C_SPY,
        boxmean=True,
    ), row=1, col=2)
    fig.add_trace(go.Box(
        y=falling.values,
        name=f"Falling Sentiment (n={len(falling)})",
        marker_color=C_INDICATOR,
        boxmean=True,
    ), row=1, col=2)

    fig.update_layout(
        template="plotly_white",
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_xaxes(title_text="UMCSENT YoY (%)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="XLV 3M Forward Return (%)", row=1, col=2)
    save_chart(fig, f"{PAIR_ID}_signal_dist")


# ===================================================================
# CHART 10: Walk-forward OOS rolling Sharpe
# ===================================================================
def chart_wf_sharpe():
    df = load_monthly()
    winner = load_winner()

    oos_start = winner["oos_start"]
    oos = df[df.index >= oos_start].copy()
    if "xlv_ret" not in oos.columns:
        oos["xlv_ret"] = oos["xlv"].pct_change()

    tourn_df = load_tournament()
    valid_strats = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]

    fig = go.Figure()

    # Annual rolling Sharpe for winner
    if len(valid_strats) > 0:
        best = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
        sig_col_map = {
            "S1_level":     "umcsent",
            "S2_yoy":       "umcsent_yoy",
            "S3_mom":       "umcsent_mom",
            "S4_zscore":    "umcsent_zscore",
            "S5_3m_ma":     "umcsent_3m_ma",
            "S6_direction": "umcsent_direction",
            "S7_dev_ma":    "umcsent_dev_ma",
        }
        sig_col = sig_col_map.get(best["signal"])
        if sig_col and sig_col in oos.columns:
            try:
                signal = oos[sig_col].shift(int(best["lead_months"]))
                is_end = winner["is_end"]
                thresh_name = best["threshold"]
                if "T1_fixed" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    is_data = df[df.index <= is_end]
                    thresh = is_data[sig_col].quantile(pct / 100)
                elif "T4_zero" in thresh_name:
                    thresh = 0
                else:
                    thresh = 0

                position = (signal < thresh).astype(float)
                strat_ret = position.shift(1) * oos["xlv_ret"]

                # Annual Sharpe by calendar year
                years = sorted(oos.index.year.unique())
                annual_data = []
                for yr in years:
                    yr_mask = oos.index.year == yr
                    yr_ret = strat_ret[yr_mask].dropna()
                    bh_ret = oos.loc[yr_mask, "xlv_ret"].dropna()
                    if len(yr_ret) >= 8:
                        s = (yr_ret.mean() / yr_ret.std()) * np.sqrt(12) if yr_ret.std() > 0 else 0
                        b = (bh_ret.mean() / bh_ret.std()) * np.sqrt(12) if bh_ret.std() > 0 else 0
                        annual_data.append({"year": yr, "strat_sharpe": s, "bh_sharpe": b})

                annual_df = pd.DataFrame(annual_data)
                if len(annual_df) > 0:
                    bar_colors = [C_STRATEGY if v > 0 else C_INDICATOR for v in annual_df["strat_sharpe"]]
                    fig.add_trace(go.Bar(
                        x=annual_df["year"].astype(str),
                        y=annual_df["strat_sharpe"],
                        name="Strategy Annual Sharpe",
                        marker_color=bar_colors,
                    ))
                    fig.add_trace(go.Scatter(
                        x=annual_df["year"].astype(str),
                        y=annual_df["bh_sharpe"],
                        name="B&H XLV Sharpe",
                        mode="lines+markers",
                        line=dict(color=C_BENCHMARK, width=2, dash="dash"),
                    ))
            except Exception as e:
                print(f"    Walk-forward Sharpe failed: {e}")

    fig.add_hline(y=0, line_dash="dash", line_color="red", line_width=0.5)

    fig.update_layout(
        title="Walk-Forward Annual Sharpe Ratio (OOS Period by Year)",
        xaxis_title="Year",
        yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white",
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="group",
    )
    save_chart(fig, f"{PAIR_ID}_wf_sharpe")


# ===================================================================
# MAIN
# ===================================================================
if __name__ == "__main__":
    print(f"Generating charts for {PAIR_ID}...")
    chart_hero()
    chart_correlations()
    chart_regime_stats()
    chart_ccf()
    chart_equity_curves()
    chart_drawdown()
    chart_rolling_sharpe()
    chart_tournament_scatter()
    chart_signal_dist()
    chart_wf_sharpe()
    print(f"\nDone. Charts saved to {CHART_DIR}")
    charts = os.listdir(CHART_DIR)
    print(f"Total charts: {len(charts)}")
    for c in sorted(charts):
        size_kb = os.path.getsize(os.path.join(CHART_DIR, c)) // 1024
        print(f"  {c}  ({size_kb} KB)")
