#!/usr/bin/env python3
"""Chart generation for all 3 TED spread variants → SPY."""

import os, json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE = str(Path(__file__).resolve().parents[1])
C_IND = "#d62728"; C_EQ = "#1f77b4"; C_STRAT = "#2ca02c"; C_BM = "#7f7f7f"

VARIANTS = [
    ("sofr_ted_spy", "SOFR - DTB3", "2023-01-01"),
    ("dff_ted_spy", "DFF - DTB3 (Fed Funds TED)", "2018-01-01"),
    ("ted_spliced_spy", "TEDRATE + adj DFF-TED (Spliced)", "2018-01-01"),
]

def save(fig, pair_id, name):
    d = os.path.join(BASE, "output", "charts", pair_id, "plotly")
    os.makedirs(d, exist_ok=True)
    fig.write_json(os.path.join(d, f"{pair_id}_{name}.json"))

def gen_hero(pair_id, label):
    df = pd.read_parquet(os.path.join(BASE, "data", f"{pair_id}_daily_20260314.parquet"))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df.index, y=df["spread"], name=label, line=dict(color=C_IND, width=1.5)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_EQ, width=1.5)), secondary_y=True)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5, secondary_y=False)
    fig.update_layout(title=f"{label} vs S&P 500", template="plotly_white", height=450,
                      hovermode="x unified", legend=dict(orientation="h", y=1.02, x=1, xanchor="right"))
    fig.update_yaxes(title_text="Spread (%)", secondary_y=False)
    fig.update_yaxes(title_text="SPY ($)", secondary_y=True)
    save(fig, pair_id, "hero")

def gen_regime(pair_id):
    rdf = pd.read_csv(os.path.join(BASE, "results", pair_id, "exploratory_20260314", "regime_descriptive_stats.csv"))
    if len(rdf) == 0: return
    fig = go.Figure(go.Bar(x=rdf["regime"], y=rdf["sharpe"],
        marker_color=[C_STRAT, C_EQ, C_BM, C_IND],
        text=[f"{v:.2f}" for v in rdf["sharpe"]], textposition="outside"))
    fig.update_layout(title="SPY Sharpe by Spread Quartile", template="plotly_white", height=380, showlegend=False,
                      xaxis_title="Spread Quartile (Q1=Lowest, Q4=Highest)", yaxis_title="Annualized Sharpe")
    save(fig, pair_id, "regime_stats")

def gen_correlations(pair_id):
    cdf = pd.read_csv(os.path.join(BASE, "results", pair_id, "exploratory_20260314", "correlations.csv"))
    pearson = cdf[cdf["method"] == "Pearson"]
    if len(pearson) == 0: return
    pivot = pearson.pivot(index="signal", columns="horizon", values="correlation")
    cols = [c for c in ["spy_fwd_1d","spy_fwd_5d","spy_fwd_21d","spy_fwd_63d"] if c in pivot.columns]
    if not cols: return
    pivot = pivot[cols]
    fig = go.Figure(go.Heatmap(z=pivot.values, x=[c.replace("spy_fwd_","") for c in pivot.columns],
        y=[s.replace("spread_","") for s in pivot.index], colorscale="RdBu_r", zmid=0, zmin=-0.15, zmax=0.15,
        text=[[f"{v:.3f}" for v in row] for row in pivot.values], texttemplate="%{text}", textfont={"size":10}))
    fig.update_layout(title="Correlation: Spread Signals → SPY Returns", template="plotly_white", height=400)
    save(fig, pair_id, "correlations")

def gen_tournament(pair_id):
    tdf = pd.read_csv(os.path.join(BASE, "results", pair_id, "tournament_results_20260314.csv"))
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    invalid = tdf[~tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    bh = tdf[tdf["signal"] == "BENCHMARK"]
    fig = go.Figure()
    if len(invalid) > 0:
        fig.add_trace(go.Scatter(x=invalid["annual_turnover"], y=invalid["oos_sharpe"], mode="markers",
            marker=dict(size=4, color="#ccc", opacity=0.3), name="Invalid"))
    if len(valid) > 0:
        fig.add_trace(go.Scatter(x=valid["annual_turnover"], y=valid["oos_sharpe"], mode="markers",
            marker=dict(size=6, color=valid["max_drawdown"], colorscale="RdYlGn",
                        colorbar=dict(title="Max DD (%)"), opacity=0.7),
            text=[f"{r['signal']}/{r['threshold']}/{r['strategy']}" for _,r in valid.iterrows()],
            hovertemplate="%{text}<br>Sharpe: %{y:.2f}<extra></extra>", name="Valid"))
    if len(bh) > 0:
        fig.add_trace(go.Scatter(x=[bh.iloc[0]["annual_turnover"]], y=[bh.iloc[0]["oos_sharpe"]],
            mode="markers", marker=dict(size=15, color=C_BM, symbol="diamond"), name="Buy & Hold"))
    top5 = valid.nlargest(5, "oos_sharpe") if len(valid) > 0 else pd.DataFrame()
    if len(top5) > 0:
        fig.add_trace(go.Scatter(x=top5["annual_turnover"], y=top5["oos_sharpe"], mode="markers",
            marker=dict(size=12, color=C_STRAT, symbol="star", line=dict(width=1, color="black")), name="Top 5"))
    fig.update_layout(title=f"Tournament: {len(tdf)} Combos ({len(valid)} Valid)",
        xaxis_title="Annual Turnover", yaxis_title="OOS Sharpe", template="plotly_white", height=450)
    save(fig, pair_id, "tournament_scatter")

def gen_local_projections(pair_id):
    lp = pd.read_csv(os.path.join(BASE, "results", pair_id, "core_models_20260314", "local_projections.csv"))
    if len(lp) == 0: return
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lp["horizon_days"], y=lp["coef"], mode="lines+markers",
        line=dict(color=C_EQ, width=2), marker=dict(size=8), name="Coefficient"))
    fig.add_trace(go.Scatter(
        x=list(lp["horizon_days"]) + list(lp["horizon_days"][::-1]),
        y=list(lp["ci_upper"]) + list(lp["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(31,119,180,0.2)", line=dict(color="rgba(0,0,0,0)"), name="95% CI"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.5)
    sig = lp[lp["p_value"] < 0.05]
    if len(sig) > 0:
        fig.add_trace(go.Scatter(x=sig["horizon_days"], y=sig["coef"], mode="markers",
            marker=dict(size=12, color=C_IND, symbol="star"), name="Significant"))
    fig.update_layout(title="Local Projections: Spread → SPY Returns", template="plotly_white", height=380,
        xaxis_title="Horizon (days)", yaxis_title="Coefficient (HAC)")
    save(fig, pair_id, "local_projections")

if __name__ == "__main__":
    print("Generating charts for 3 TED variants...")
    for pid, label, _ in VARIANTS:
        print(f"\n  {pid}:")
        gen_hero(pid, label)
        gen_regime(pid)
        gen_correlations(pid)
        gen_tournament(pid)
        gen_local_projections(pid)
    print("\nDone.")
