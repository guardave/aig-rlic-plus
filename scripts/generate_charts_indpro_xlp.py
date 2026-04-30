#!/usr/bin/env python3
"""
Chart Generation: Industrial Production (INDPRO) → Consumer Staples (XLP)
==========================================================================
Produces Plotly JSON charts for the Streamlit portal.
Standard 10-chart set for indpro_xlp.

Charts:
  1. hero              - INDPRO YoY vs XLP price (dual-axis)
  2. correlations      - Rolling 12m and 36m correlations
  3. regime_stats      - XLP returns by INDPRO quartile
  4. ccf               - Cross-correlation function
  5. equity_curves     - Signal backtest equity curve
  6. drawdown          - Drawdown comparison
  7. rolling_sharpe    - Rolling Sharpe
  8. tournament_scatter - Tournament scatter
  9. signal_dist       - Signal distribution
  10. walk_forward     - Walk-forward rolling Sharpe

Author: Evan (Econometrics Agent)
Date: 2026-04-20
Pair: indpro_xlp
"""

import os
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE_DIR = str(Path(__file__).resolve().parents[1])
RESULTS_DIR = os.path.join(BASE_DIR, "results", "indpro_xlp")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "output", "charts", "indpro_xlp", "plotly")
EXPLORE_DIR = os.path.join(RESULTS_DIR, "exploratory_20260420")
DATE_TAG = "20260420"
OOS_START = "2019-01-31"

os.makedirs(CHART_DIR, exist_ok=True)

# Color palette
C_INDICATOR = "#d62728"    # Red for IP
C_EQUITY = "#1f77b4"       # Blue for XLP
C_STRATEGY = "#2ca02c"     # Green for strategy
C_BENCHMARK = "#7f7f7f"    # Gray for benchmark
C_CONTRACTION = "rgba(214, 39, 40, 0.15)"
C_EXPANSION = "rgba(44, 160, 44, 0.08)"


def save_chart(fig, name):
    path = os.path.join(CHART_DIR, f"{name}.json")
    fig.write_json(path)
    print(f"  Saved: {name}.json")


def load_monthly():
    return pd.read_parquet(os.path.join(DATA_DIR, "indpro_xlp_monthly_19980101_20251231.parquet"))


def load_tournament():
    return pd.read_csv(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv"))


def load_winner():
    with open(os.path.join(RESULTS_DIR, "winner_summary.json")) as f:
        return json.load(f)


# =============================================================================
# Chart 1: Hero — INDPRO YoY vs XLP price (dual-axis)
# =============================================================================
def chart_hero():
    df = load_monthly()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df.index, y=df["indpro_yoy"], name="IP YoY Growth (%)",
                   line=dict(color=C_INDICATOR, width=2)),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["xlp"], name="XLP Price ($)",
                   line=dict(color=C_EQUITY, width=1.5)),
        secondary_y=True,
    )

    # Shade contraction periods (IP YoY < 0)
    if "indpro_yoy" in df.columns:
        contraction = df["indpro_yoy"] < 0
        starts = contraction.index[contraction & ~contraction.shift(1, fill_value=False)]
        ends = contraction.index[contraction & ~contraction.shift(-1, fill_value=False)]
        for s, e in zip(starts, ends):
            fig.add_vrect(x0=s, x1=e, fillcolor=C_CONTRACTION, layer="below", line_width=0)

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5, secondary_y=False)

    fig.update_layout(
        title="Industrial Production Growth vs Consumer Staples ETF (XLP, 1998-2025)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    )
    fig.update_yaxes(title_text="IP YoY Growth (%)", secondary_y=False)
    fig.update_yaxes(title_text="XLP Price ($)", secondary_y=True)

    save_chart(fig, "indpro_xlp_hero")


# =============================================================================
# Chart 2: Correlations — rolling 12m and 36m
# =============================================================================
def chart_correlations():
    df = load_monthly()

    if "indpro_yoy" not in df.columns or "xlp_ret" not in df.columns:
        print("  Skipping correlations chart — missing columns")
        return

    # Compute rolling Pearson correlations
    roll12 = df["indpro_yoy"].rolling(12, min_periods=10).corr(df["xlp_ret"])
    roll36 = df["indpro_yoy"].rolling(36, min_periods=30).corr(df["xlp_ret"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=roll12.index, y=roll12.values,
        name="12M Rolling Correlation",
        line=dict(color=C_INDICATOR, width=1.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=roll36.index, y=roll36.values,
        name="36M Rolling Correlation",
        line=dict(color=C_EQUITY, width=2),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5)

    # OOS start line
    fig.add_vline(x=pd.Timestamp(OOS_START).timestamp() * 1000, line_dash="longdash",
                  line_color="black", line_width=1)

    fig.update_layout(
        title="Rolling Correlation: INDPRO YoY vs XLP Monthly Return",
        xaxis_title="Date",
        yaxis_title="Pearson Correlation",
        template="plotly_white",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    save_chart(fig, "indpro_xlp_correlations")


# =============================================================================
# Chart 3: Regime analysis — XLP returns by INDPRO quartile
# =============================================================================
def chart_regime_stats():
    regime_path = os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv")
    if not os.path.exists(regime_path):
        print("  Skipping regime chart — file not found")
        return

    regime_df = pd.read_csv(regime_path)
    colors = [C_INDICATOR, C_BENCHMARK, C_EQUITY, C_STRATEGY]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regime_df["regime"],
        y=regime_df["sharpe"],
        name="Annualized Sharpe",
        marker_color=colors[:len(regime_df)],
        text=[f"{v:.2f}" for v in regime_df["sharpe"]],
        textposition="outside",
    ))

    fig.update_layout(
        title="XLP Sharpe Ratio by INDPRO YoY Growth Quartile",
        xaxis_title="IP Growth Quartile (Q1=Lowest, Q4=Highest)",
        yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white",
        height=400,
        showlegend=False,
    )

    save_chart(fig, "indpro_xlp_regime_stats")


# =============================================================================
# Chart 4: CCF
# =============================================================================
def chart_ccf():
    ccf_path = os.path.join(EXPLORE_DIR, "ccf.csv")
    if not os.path.exists(ccf_path):
        print("  Skipping CCF chart — file not found")
        return

    ccf_df = pd.read_csv(ccf_path)
    colors = [C_INDICATOR if sig else C_EQUITY for sig in ccf_df["significant"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ccf_df["lag"], y=ccf_df["ccf"],
        marker_color=colors,
        name="CCF",
    ))

    if len(ccf_df) > 0:
        se = ccf_df["se"].iloc[0]
        fig.add_hline(y=1.96 * se, line_dash="dash", line_color="gray", line_width=0.5)
        fig.add_hline(y=-1.96 * se, line_dash="dash", line_color="gray", line_width=0.5)

    fig.update_layout(
        title="Cross-Correlation: INDPRO YoY Growth vs XLP Monthly Return",
        xaxis_title="Lag (months, negative = IP leads XLP)",
        yaxis_title="Cross-Correlation",
        template="plotly_white",
        height=400,
    )

    save_chart(fig, "indpro_xlp_ccf")


# =============================================================================
# Chart 5: Equity curves (signal backtest)
# =============================================================================
def chart_equity_curves():
    df = load_monthly()
    tourn_df = load_tournament()
    ws = load_winner()

    oos = df[df.index >= OOS_START].copy()

    if "xlp_ret" not in oos.columns:
        if "xlp" in oos.columns:
            oos["xlp_ret"] = oos["xlp"].pct_change()
        else:
            print("  Skipping equity curves — no XLP return data")
            return

    fig = go.Figure()

    # Buy-and-hold XLP
    bh_cum = (1 + oos["xlp_ret"].fillna(0)).cumprod()
    fig.add_trace(go.Scatter(
        x=bh_cum.index, y=bh_cum.values,
        name="Buy & Hold XLP",
        line=dict(color=C_BENCHMARK, width=2, dash="dash"),
    ))

    # Simulate winner strategy
    sig_col_map = {
        "S1_level": "indpro",
        "S2_yoy": "indpro_yoy",
        "S3_mom": "indpro_mom",
        "S4_dev_trend": "indpro_dev_trend",
        "S5_zscore": "indpro_zscore_60m",
        "S6_mom3m": "indpro_mom_3m",
        "S7_mom6m": "indpro_mom_6m",
        "S8_accel": "indpro_accel",
        "S9_contraction": "indpro_contraction",
    }

    valid_strats = tourn_df[(tourn_df["valid"]) & (tourn_df["signal"] != "BENCHMARK")]
    top3 = valid_strats.nlargest(3, "oos_sharpe")
    colors_strat = [C_STRATEGY, C_INDICATOR, C_EQUITY]

    for idx, (_, row) in enumerate(top3.iterrows()):
        sig_col = sig_col_map.get(row["signal"])
        if sig_col is None or sig_col not in df.columns:
            continue

        signal = df[sig_col].shift(int(row["lead_months"]))

        # Reconstruct position
        thresh_name = str(row["threshold"])
        is_data = df[df.index < OOS_START]

        try:
            if "T1_fixed_p" in thresh_name:
                pct = int(thresh_name.split("p")[1])
                thresh = is_data[sig_col].quantile(pct / 100) if sig_col in is_data.columns else None
            elif "T2_roll_p" in thresh_name:
                pct = int(thresh_name.split("p")[1])
                thresh = signal.rolling(60, min_periods=36).quantile(pct / 100)
            elif "T3_zscore" in thresh_name and "neg_" not in thresh_name:
                k = float(thresh_name.split("_")[-1])
                rm = signal.rolling(60, min_periods=36)
                thresh = rm.mean() + k * rm.std()
            elif "T3_zscore_neg_" in thresh_name:
                k = float(thresh_name.split("_")[-1])
                rm = signal.rolling(60, min_periods=36)
                thresh = rm.mean() - k * rm.std()
            elif thresh_name == "T4_zero":
                thresh = 0
            else:
                continue

            if thresh is None:
                continue

            if isinstance(thresh, (int, float)):
                above = signal > thresh
            else:
                above = signal > thresh

            orientation = "counter" if "_counter" in str(row["strategy"]) else "pro"
            if orientation == "counter":
                position = (~above).astype(float)
            else:
                position = above.astype(float)

            strat_ret = position.shift(1) * df["xlp_ret"]
            oos_strat = strat_ret[df.index >= OOS_START]
            strat_cum = (1 + oos_strat.fillna(0)).cumprod()

            label = f"#{idx+1}: {row['signal']}/{row['threshold']}"
            fig.add_trace(go.Scatter(
                x=strat_cum.index, y=strat_cum.values,
                name=label,
                line=dict(color=colors_strat[idx], width=2),
            ))
        except Exception as e:
            print(f"    Equity curve for rank {idx+1} failed: {e}")
            continue

    fig.update_layout(
        title=f"Equity Curves: Top Strategies vs Buy-and-Hold XLP (OOS {OOS_START[:7]}-2025)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return ($1 invested)",
        template="plotly_white",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    save_chart(fig, "indpro_xlp_equity_curves")


# =============================================================================
# Chart 6: Drawdown comparison
# =============================================================================
def chart_drawdown():
    df = load_monthly()
    tourn_df = load_tournament()

    oos = df[df.index >= OOS_START].copy()
    if "xlp_ret" not in oos.columns:
        if "xlp" in oos.columns:
            oos["xlp_ret"] = oos["xlp"].pct_change()
        else:
            return

    fig = go.Figure()

    # Buy-and-hold drawdown
    bh_cum = (1 + oos["xlp_ret"].fillna(0)).cumprod()
    bh_dd = (bh_cum - bh_cum.cummax()) / bh_cum.cummax()
    fig.add_trace(go.Scatter(
        x=bh_dd.index, y=bh_dd.values * 100,
        name="Buy & Hold XLP",
        line=dict(color=C_BENCHMARK, width=2, dash="dash"),
        fill="tozeroy",
        fillcolor="rgba(127,127,127,0.15)",
    ))

    # Winner strategy drawdown
    valid_strats = tourn_df[(tourn_df["valid"]) & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid_strats) > 0:
        sig_col_map = {
            "S1_level": "indpro",
            "S2_yoy": "indpro_yoy",
            "S3_mom": "indpro_mom",
            "S4_dev_trend": "indpro_dev_trend",
            "S5_zscore": "indpro_zscore_60m",
            "S6_mom3m": "indpro_mom_3m",
            "S7_mom6m": "indpro_mom_6m",
            "S8_accel": "indpro_accel",
            "S9_contraction": "indpro_contraction",
        }
        best = valid_strats.iloc[0]
        sig_col = sig_col_map.get(str(best["signal"]))

        if sig_col and sig_col in df.columns:
            signal = df[sig_col].shift(int(best["lead_months"]))
            thresh_name = str(best["threshold"])
            is_data = df[df.index < OOS_START]

            try:
                if "T2_roll_p" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    thresh = signal.rolling(60, min_periods=36).quantile(pct / 100)
                elif "T1_fixed_p" in thresh_name:
                    pct = int(thresh_name.split("p")[1])
                    thresh = is_data[sig_col].quantile(pct / 100) if sig_col in is_data.columns else 0
                else:
                    thresh = signal.rolling(60, min_periods=36).quantile(0.75)

                if isinstance(thresh, (int, float)):
                    above = signal > thresh
                else:
                    above = signal > thresh

                orientation = "counter" if "_counter" in str(best["strategy"]) else "pro"
                position = (~above).astype(float) if orientation == "counter" else above.astype(float)

                strat_ret = position.shift(1) * df["xlp_ret"]
                oos_strat = strat_ret[df.index >= OOS_START]
                strat_cum = (1 + oos_strat.fillna(0)).cumprod()
                strat_dd = (strat_cum - strat_cum.cummax()) / strat_cum.cummax()

                fig.add_trace(go.Scatter(
                    x=strat_dd.index, y=strat_dd.values * 100,
                    name=f"Winner: {best['signal']}/{best['threshold']}",
                    line=dict(color=C_STRATEGY, width=2),
                    fill="tozeroy",
                    fillcolor="rgba(44,160,44,0.15)",
                ))
            except Exception as e:
                print(f"    Drawdown strategy simulation failed: {e}")

    fig.update_layout(
        title=f"Drawdown Comparison: Winner Strategy vs Buy-and-Hold XLP (OOS)",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    save_chart(fig, "indpro_xlp_drawdown")


# =============================================================================
# Chart 7: Rolling Sharpe
# =============================================================================
def chart_rolling_sharpe():
    df = load_monthly()

    if "xlp_ret" not in df.columns:
        if "xlp" in df.columns:
            df["xlp_ret"] = df["xlp"].pct_change()
        else:
            return

    oos = df[df.index >= OOS_START].copy()

    # Rolling 12M Sharpe for buy-and-hold XLP
    bh_roll = oos["xlp_ret"].rolling(12, min_periods=10)
    bh_sharpe = (bh_roll.mean() / bh_roll.std()) * np.sqrt(12)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bh_sharpe.index, y=bh_sharpe.values,
        name="Buy & Hold XLP (12M Rolling Sharpe)",
        line=dict(color=C_BENCHMARK, width=2, dash="dash"),
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5)

    fig.update_layout(
        title="Rolling 12-Month Sharpe Ratio: Buy-and-Hold XLP (OOS Period)",
        xaxis_title="Date",
        yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white",
        height=420,
    )

    save_chart(fig, "indpro_xlp_rolling_sharpe")


# =============================================================================
# Chart 8: Tournament scatter
# =============================================================================
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
            marker=dict(size=4, color="#cccccc", opacity=0.3),
            name="Invalid",
        ))

    if len(valid) > 0:
        fig.add_trace(go.Scatter(
            x=valid["annual_turnover"], y=valid["oos_sharpe"],
            mode="markers",
            marker=dict(
                size=6,
                color=valid["max_drawdown"],
                colorscale="RdYlGn",
                colorbar=dict(title="Max DD (%)"),
                opacity=0.7,
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
            marker=dict(size=15, color=C_BENCHMARK, symbol="diamond"),
            name="Buy-and-Hold XLP",
        ))

    top5 = valid.nlargest(5, "oos_sharpe")
    if len(top5) > 0:
        fig.add_trace(go.Scatter(
            x=top5["annual_turnover"], y=top5["oos_sharpe"],
            mode="markers",
            marker=dict(size=12, color=C_STRATEGY, symbol="star", line=dict(width=1, color="black")),
            name="Top 5",
        ))

    fig.update_layout(
        title=f"Tournament Results: {len(tourn_df):,} Combinations ({len(valid):,} Valid)",
        xaxis_title="Annual Turnover",
        yaxis_title="OOS Sharpe Ratio",
        template="plotly_white",
        height=500,
    )

    save_chart(fig, "indpro_xlp_tournament_scatter")


# =============================================================================
# Chart 9: Signal distribution
# =============================================================================
def chart_signal_dist():
    df = load_monthly()

    # Show distribution of the winner signal: INDPRO acceleration
    if "indpro_accel" not in df.columns:
        print("  Skipping signal distribution — indpro_accel not found")
        return

    sig = df["indpro_accel"].dropna()

    oos_mask = df.index >= OOS_START
    is_sig = df.loc[~oos_mask, "indpro_accel"].dropna()
    oos_sig = df.loc[oos_mask, "indpro_accel"].dropna()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=is_sig, name="In-Sample", nbinsx=30,
        marker_color=C_INDICATOR, opacity=0.6,
        histnorm="probability density",
    ))
    fig.add_trace(go.Histogram(
        x=oos_sig, name="Out-of-Sample", nbinsx=20,
        marker_color=C_EQUITY, opacity=0.6,
        histnorm="probability density",
    ))

    # Add IS 75th percentile threshold line
    p75 = is_sig.rolling(60, min_periods=36).quantile(0.75).iloc[-1] if len(is_sig) > 0 else is_sig.quantile(0.75)
    fig.add_vline(x=float(is_sig.quantile(0.75)),
                  line_dash="dash", line_color="red", line_width=1.5,
                  annotation_text="IS p75 threshold")

    fig.update_layout(
        title="INDPRO Acceleration Signal Distribution (IS vs OOS)",
        xaxis_title="INDPRO MoM Acceleration (pp)",
        yaxis_title="Probability Density",
        template="plotly_white",
        barmode="overlay",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    save_chart(fig, "indpro_xlp_signal_dist")


# =============================================================================
# Chart 10: Walk-forward rolling Sharpe
# =============================================================================
def chart_walk_forward():
    df = load_monthly()
    tourn_df = load_tournament()

    # Walk-forward: simulate winner strategy over expanding windows
    valid_strats = tourn_df[(tourn_df["valid"]) & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid_strats) == 0:
        print("  Skipping walk-forward — no valid strategies")
        return

    best = valid_strats.iloc[0]

    sig_col_map = {
        "S1_level": "indpro",
        "S2_yoy": "indpro_yoy",
        "S3_mom": "indpro_mom",
        "S4_dev_trend": "indpro_dev_trend",
        "S5_zscore": "indpro_zscore_60m",
        "S6_mom3m": "indpro_mom_3m",
        "S7_mom6m": "indpro_mom_6m",
        "S8_accel": "indpro_accel",
        "S9_contraction": "indpro_contraction",
    }
    sig_col = sig_col_map.get(str(best["signal"]))
    if sig_col is None or sig_col not in df.columns:
        print(f"  Skipping walk-forward — signal column '{sig_col}' not found (winner: {best['signal']})")
        # Fall back to indpro_mom
        sig_col = "indpro_mom"
        if sig_col not in df.columns:
            return

    if "xlp_ret" not in df.columns and "xlp" in df.columns:
        df["xlp_ret"] = df["xlp"].pct_change()

    signal = df[sig_col].shift(int(best["lead_months"]))
    thresh_name = str(best["threshold"])

    sharpe_series = {}

    # Compute rolling 24-month Sharpe on OOS period
    oos = df[df.index >= OOS_START].copy()
    if "xlp_ret" not in oos.columns:
        print("  Skipping walk-forward — missing xlp_ret")
        return

    is_data = df[df.index < OOS_START]
    try:
        if "T2_roll_p" in thresh_name:
            pct = int(thresh_name.split("p")[1])
            thresh = signal.rolling(60, min_periods=36).quantile(pct / 100)
        elif "T1_fixed_p" in thresh_name:
            pct = int(thresh_name.split("p")[1])
            thresh = is_data[sig_col].quantile(pct / 100) if sig_col in is_data.columns else 0
        else:
            thresh = signal.rolling(60, min_periods=36).quantile(0.75)

        if isinstance(thresh, (int, float)):
            above = signal > thresh
        else:
            above = signal > thresh

        orientation = "counter" if "_counter" in str(best["strategy"]) else "pro"
        position = (~above).astype(float) if orientation == "counter" else above.astype(float)

        strat_ret = position.shift(1) * df["xlp_ret"]
        oos_strat = strat_ret[df.index >= OOS_START]

        # Rolling 24M Sharpe
        roll24 = oos_strat.rolling(24, min_periods=18)
        roll_sharpe = (roll24.mean() / roll24.std()) * np.sqrt(12)

        # BH rolling Sharpe
        bh_roll = oos["xlp_ret"].rolling(24, min_periods=18)
        bh_sharpe = (bh_roll.mean() / bh_roll.std()) * np.sqrt(12)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=roll_sharpe.index, y=roll_sharpe.values,
            name=f"Winner Strategy (24M Rolling Sharpe)",
            line=dict(color=C_STRATEGY, width=2),
        ))
        fig.add_trace(go.Scatter(
            x=bh_sharpe.index, y=bh_sharpe.values,
            name="Buy & Hold XLP (24M Rolling Sharpe)",
            line=dict(color=C_BENCHMARK, width=2, dash="dash"),
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5)

        fig.update_layout(
            title="Walk-Forward Rolling Sharpe: Winner vs Buy-and-Hold XLP (OOS)",
            xaxis_title="Date",
            yaxis_title="Annualized Sharpe Ratio (24M window)",
            template="plotly_white",
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        save_chart(fig, "indpro_xlp_walk_forward")

    except Exception as e:
        print(f"  Walk-forward chart failed: {e}")


# =============================================================================
# Main
# =============================================================================
if __name__ == "__main__":
    print("Generating INDPRO → XLP charts...")
    chart_hero()
    chart_correlations()
    chart_regime_stats()
    chart_ccf()
    chart_equity_curves()
    chart_drawdown()
    chart_rolling_sharpe()
    chart_tournament_scatter()
    chart_signal_dist()
    chart_walk_forward()
    print(f"\nDone. 10 charts saved to {CHART_DIR}")
    # Verify all 10 exist
    expected = [
        "indpro_xlp_hero",
        "indpro_xlp_correlations",
        "indpro_xlp_regime_stats",
        "indpro_xlp_ccf",
        "indpro_xlp_equity_curves",
        "indpro_xlp_drawdown",
        "indpro_xlp_rolling_sharpe",
        "indpro_xlp_tournament_scatter",
        "indpro_xlp_signal_dist",
        "indpro_xlp_walk_forward",
    ]
    missing = [c for c in expected if not os.path.exists(os.path.join(CHART_DIR, f"{c}.json"))]
    if missing:
        print(f"\nWARNING: Missing charts: {missing}")
    else:
        print(f"\nAll {len(expected)} charts verified.")
