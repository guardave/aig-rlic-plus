#!/usr/bin/env python3
"""
Chart Generation: Industrial Production (INDPRO) → S&P 500 (SPY)
================================================================
Produces Plotly JSON charts for the Streamlit portal.

Author: Vera (Visualization Agent)
Date: 2026-03-14
"""

import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE_DIR = "/workspaces/aig-rlic-plus"
RESULTS_DIR = os.path.join(BASE_DIR, "results", "indpro_spy")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "output", "charts", "indpro_spy", "plotly")
os.makedirs(CHART_DIR, exist_ok=True)

# Color palette
C_INDICATOR = "#d62728"   # Red for IP
C_EQUITY = "#1f77b4"      # Blue for SPY
C_STRATEGY = "#2ca02c"    # Green for strategy
C_BENCHMARK = "#7f7f7f"   # Gray for benchmark
C_CONTRACTION = "rgba(214, 39, 40, 0.15)"

def save_chart(fig, name):
    path = os.path.join(CHART_DIR, f"{name}.json")
    fig.write_json(path)
    print(f"  Saved: {name}.json")


def chart_hero():
    """Hero chart: INDPRO YoY vs SPY (dual-axis)."""
    df = pd.read_parquet(os.path.join(DATA_DIR, "indpro_spy_monthly_19900101_20251231.parquet"))

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df.index, y=df["indpro_yoy"], name="IP YoY Growth (%)",
                   line=dict(color=C_INDICATOR, width=2)),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["spy"], name="SPY Price ($)",
                   line=dict(color=C_EQUITY, width=1.5)),
        secondary_y=True,
    )

    # Shade contraction periods (IP YoY < 0)
    contraction = df["indpro_yoy"] < 0
    starts = contraction.index[contraction & ~contraction.shift(1, fill_value=False)]
    ends = contraction.index[contraction & ~contraction.shift(-1, fill_value=False)]

    for s, e in zip(starts, ends):
        fig.add_vrect(x0=s, x1=e, fillcolor=C_CONTRACTION,
                      layer="below", line_width=0)

    # Zero line for IP
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5,
                  secondary_y=False)

    fig.update_layout(
        title="Industrial Production Growth vs S&P 500 (1990-2025)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    )
    fig.update_yaxes(title_text="IP YoY Growth (%)", secondary_y=False)
    fig.update_yaxes(title_text="SPY Price ($)", secondary_y=True)

    save_chart(fig, "indpro_spy_hero")


def chart_regime_stats():
    """Regime descriptive stats bar chart."""
    regime_df = pd.read_csv(os.path.join(RESULTS_DIR, "exploratory_20260314", "regime_descriptive_stats.csv"))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=regime_df["regime"], y=regime_df["sharpe"],
        name="Annualized Sharpe",
        marker_color=[C_INDICATOR, C_BENCHMARK, C_EQUITY, C_STRATEGY],
        text=[f"{v:.2f}" for v in regime_df["sharpe"]],
        textposition="outside",
    ))

    fig.update_layout(
        title="SPY Sharpe Ratio by INDPRO YoY Growth Quartile",
        xaxis_title="IP Growth Quartile (Q1=Lowest, Q4=Highest)",
        yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white",
        height=400,
        showlegend=False,
    )

    save_chart(fig, "indpro_spy_regime_stats")


def chart_correlations():
    """Correlation heatmap across signals and horizons."""
    corr_df = pd.read_csv(os.path.join(RESULTS_DIR, "exploratory_20260314", "correlations.csv"))

    # Filter to Pearson only
    pearson = corr_df[corr_df["method"] == "Pearson"]

    # Pivot
    pivot = pearson.pivot(index="signal", columns="horizon", values="correlation")
    # Reorder columns
    col_order = [c for c in ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"] if c in pivot.columns]
    pivot = pivot[col_order]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[c.replace("spy_fwd_", "").upper() for c in pivot.columns],
        y=[s.replace("indpro_", "IP ") for s in pivot.index],
        colorscale="RdBu_r",
        zmid=0,
        zmin=-0.2, zmax=0.2,
        text=[[f"{v:.3f}" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont={"size": 11},
    ))

    fig.update_layout(
        title="Pearson Correlation: IP Signals → SPY Forward Returns",
        xaxis_title="Forward Return Horizon",
        yaxis_title="Signal",
        template="plotly_white",
        height=450,
    )

    save_chart(fig, "indpro_spy_correlations")


def chart_ccf():
    """Cross-correlation function bar chart."""
    ccf_df = pd.read_csv(os.path.join(RESULTS_DIR, "exploratory_20260314", "ccf.csv"))

    colors = ["#d62728" if sig else "#1f77b4" for sig in ccf_df["significant"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ccf_df["lag"], y=ccf_df["ccf"],
        marker_color=colors,
        name="CCF",
    ))

    # Add 95% CI bands
    if len(ccf_df) > 0:
        se = ccf_df["se"].iloc[0]
        fig.add_hline(y=1.96*se, line_dash="dash", line_color="gray", line_width=0.5)
        fig.add_hline(y=-1.96*se, line_dash="dash", line_color="gray", line_width=0.5)

    fig.update_layout(
        title="Cross-Correlation: IP YoY Growth vs SPY Monthly Return",
        xaxis_title="Lag (months, negative = IP leads)",
        yaxis_title="Cross-Correlation",
        template="plotly_white",
        height=400,
    )

    save_chart(fig, "indpro_spy_ccf")


def chart_local_projections():
    """Local projection coefficients by horizon."""
    lp_df = pd.read_csv(os.path.join(RESULTS_DIR, "core_models_20260314", "local_projections.csv"))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=lp_df["horizon_months"], y=lp_df["coef_indpro_yoy"],
        mode="lines+markers",
        name="Coefficient",
        line=dict(color=C_EQUITY, width=2),
        marker=dict(size=8),
    ))

    # CI bands
    fig.add_trace(go.Scatter(
        x=list(lp_df["horizon_months"]) + list(lp_df["horizon_months"][::-1]),
        y=list(lp_df["ci_upper"]) + list(lp_df["ci_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(31, 119, 180, 0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% CI",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5)

    # Mark significant
    sig = lp_df[lp_df["p_value"] < 0.05]
    if len(sig) > 0:
        fig.add_trace(go.Scatter(
            x=sig["horizon_months"], y=sig["coef_indpro_yoy"],
            mode="markers",
            marker=dict(size=12, color=C_INDICATOR, symbol="star"),
            name="Significant (p<0.05)",
        ))

    fig.update_layout(
        title="Local Projection: IP YoY Growth → SPY Forward Returns",
        xaxis_title="Forecast Horizon (months)",
        yaxis_title="Coefficient (HAC-robust)",
        template="plotly_white",
        height=400,
    )

    save_chart(fig, "indpro_spy_local_projections")


def chart_quantile_regression():
    """Quantile regression coefficients across quantiles."""
    qr_df = pd.read_csv(os.path.join(RESULTS_DIR, "core_models_20260314", "quantile_regression.csv"))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=qr_df["quantile"], y=qr_df["coef_indpro_yoy"],
        mode="lines+markers",
        name="QR Coefficient",
        line=dict(color=C_EQUITY, width=2),
        marker=dict(size=8),
    ))

    fig.add_trace(go.Scatter(
        x=list(qr_df["quantile"]) + list(qr_df["quantile"][::-1]),
        y=list(qr_df["ci_upper"]) + list(qr_df["ci_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(31, 119, 180, 0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% CI",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5)

    fig.update_layout(
        title="Quantile Regression: IP YoY → 3M Forward SPY Return",
        xaxis_title="Quantile (0.05 = worst outcomes, 0.95 = best)",
        yaxis_title="Coefficient",
        template="plotly_white",
        height=400,
    )

    save_chart(fig, "indpro_spy_quantile_regression")


def chart_tournament_scatter():
    """Tournament scatter: OOS Sharpe vs annual turnover."""
    tourn_df = pd.read_csv(os.path.join(RESULTS_DIR, "tournament_results_20260314.csv"))

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
            name="Buy-and-Hold",
        ))

    # Mark top 5
    top5 = valid.nlargest(5, "oos_sharpe")
    if len(top5) > 0:
        fig.add_trace(go.Scatter(
            x=top5["annual_turnover"], y=top5["oos_sharpe"],
            mode="markers",
            marker=dict(size=12, color=C_STRATEGY, symbol="star", line=dict(width=1, color="black")),
            name="Top 5",
        ))

    fig.update_layout(
        title=f"Tournament Results: {len(tourn_df)} Combinations ({len(valid)} Valid)",
        xaxis_title="Annual Turnover",
        yaxis_title="OOS Sharpe Ratio (2018-2025)",
        template="plotly_white",
        height=500,
    )

    save_chart(fig, "indpro_spy_tournament_scatter")


def chart_equity_curves():
    """Equity curves for top strategies vs buy-and-hold."""
    df = pd.read_parquet(os.path.join(DATA_DIR, "indpro_spy_monthly_19900101_20251231.parquet"))
    tourn_df = pd.read_csv(os.path.join(RESULTS_DIR, "tournament_results_20260314.csv"))

    oos = df[df.index >= "2018-01-01"].copy()

    if "spy_ret" not in oos.columns:
        oos["spy_ret"] = oos["spy"].pct_change()

    fig = go.Figure()

    # Buy-and-hold
    bh_cum = (1 + oos["spy_ret"]).cumprod()
    fig.add_trace(go.Scatter(
        x=bh_cum.index, y=bh_cum.values,
        name="Buy & Hold SPY",
        line=dict(color=C_BENCHMARK, width=2, dash="dash"),
    ))

    # Top strategy: S6_mom3m / T1_fixed_p75 / P1_long_cash / L6
    # Simulate it
    valid_strats = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid_strats) > 0:
        top = valid_strats.nlargest(3, "oos_sharpe")

        colors_strat = [C_STRATEGY, C_INDICATOR, C_EQUITY]
        for idx, (_, row) in enumerate(top.iterrows()):
            # Approximate simulation using signal
            sig_col_map = {
                "S6_mom3m": "indpro_mom_3m",
                "S3_mom": "indpro_mom",
                "S4_dev_trend": "indpro_dev_trend",
                "S7_mom6m": "indpro_mom_6m",
                "S2_yoy": "indpro_yoy",
            }
            sig_col = sig_col_map.get(row["signal"], None)
            if sig_col is None or sig_col not in oos.columns:
                continue

            signal = oos[sig_col].shift(int(row["lead_months"]))

            # Determine threshold
            if "T1_fixed" in row["threshold"]:
                # Fixed percentile from IS
                is_data = df[df.index <= "2017-12-31"]
                if sig_col in is_data.columns:
                    pct = int(row["threshold"].split("p")[1])
                    thresh = is_data[sig_col].quantile(pct / 100)
                else:
                    continue
            elif "T2_roll" in row["threshold"]:
                pct = int(row["threshold"].split("p")[1])
                thresh = signal.rolling(60, min_periods=36).quantile(pct / 100)
            elif "T3_zscore" in row["threshold"]:
                k = float(row["threshold"].split("_")[-1])
                rm = signal.rolling(60, min_periods=36)
                thresh = rm.mean() + k * rm.std()
            else:
                continue

            if isinstance(thresh, (int, float)):
                position = (signal > thresh).astype(float)
            else:
                position = (signal > thresh).astype(float)

            strat_ret = position.shift(1) * oos["spy_ret"]
            strat_cum = (1 + strat_ret.fillna(0)).cumprod()

            label = f"#{idx+1}: {row['signal']}/{row['threshold']}"
            fig.add_trace(go.Scatter(
                x=strat_cum.index, y=strat_cum.values,
                name=label,
                line=dict(color=colors_strat[idx], width=2),
            ))

    fig.update_layout(
        title="Equity Curves: Top Strategies vs Buy-and-Hold (OOS 2018-2025)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return ($1 invested)",
        template="plotly_white",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    save_chart(fig, "indpro_spy_equity_curves")


def chart_granger():
    """Granger causality p-values by lag."""
    gc_df = pd.read_csv(os.path.join(RESULTS_DIR, "core_models_20260314", "granger_causality.csv"))

    fig = go.Figure()

    for direction in gc_df["direction"].unique():
        sub = gc_df[gc_df["direction"] == direction]
        color = C_INDICATOR if "INDPRO" in direction else C_EQUITY
        fig.add_trace(go.Scatter(
            x=sub["lag"], y=sub["p_value"],
            mode="lines+markers",
            name=direction,
            line=dict(color=color, width=2),
            marker=dict(size=8),
        ))

    fig.add_hline(y=0.05, line_dash="dash", line_color="gray", line_width=1,
                  annotation_text="p=0.05")

    fig.update_layout(
        title="Granger Causality: P-Values by Lag Order",
        xaxis_title="Lag Order (months)",
        yaxis_title="P-Value",
        template="plotly_white",
        height=400,
    )

    save_chart(fig, "indpro_spy_granger")


def chart_rf_importance():
    """Random Forest feature importance."""
    fi_df = pd.read_csv(os.path.join(RESULTS_DIR, "core_models_20260314", "rf_feature_importance.csv"))
    fi_df = fi_df.sort_values("importance")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=fi_df["importance"],
        y=fi_df["feature"].str.replace("indpro_", "IP ").str.replace("yield_spread_", ""),
        orientation="h",
        marker_color=C_EQUITY,
    ))

    fig.update_layout(
        title="Random Forest Feature Importance (Last Walk-Forward Window)",
        xaxis_title="Importance",
        template="plotly_white",
        height=400,
    )

    save_chart(fig, "indpro_spy_rf_importance")


if __name__ == "__main__":
    print("Generating INDPRO → SPY charts...")
    chart_hero()
    chart_regime_stats()
    chart_correlations()
    chart_ccf()
    chart_local_projections()
    chart_quantile_regression()
    chart_tournament_scatter()
    chart_equity_curves()
    chart_granger()
    chart_rf_importance()
    print(f"\nDone. Charts saved to {CHART_DIR}")
