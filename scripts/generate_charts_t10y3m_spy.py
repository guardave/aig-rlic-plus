#!/usr/bin/env python3
"""Chart generation: 10Y-3M Treasury Spread x SPY."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart  # noqa: E402

PAIR = "t10y3m_spy"
DATE_TAG = "20260620"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

C_IND = "#0072B2"
C_SPY = "#D55E00"
C_STRAT = "#009E73"
C_BENCH = "#6C7A89"
C_BAD = "#CC79A7"
C_LINE = "#4D4D4D"


def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / "t10y3m_spy_monthly_latest.parquet")


def load_winner() -> dict:
    return json.loads((RES / "winner_summary.json").read_text())


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    meta = {
        "chart_name": name,
        "pair_id": PAIR,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/generate_charts_t10y3m_spy.py",
        "caption": caption,
        "narrative_alignment_note": caption,
        "disposition": "consumed",
        "source_artifacts": sources,
    }
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  wrote {name}.json")


def nber_legend(fig: go.Figure) -> None:
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square"),
        name="NBER recession period",
        hoverinfo="skip",
    ))


def chart_hero() -> None:
    df = load_monthly()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    fig.add_trace(go.Scatter(
        x=df.index, y=df["t10y3m"], name="10Y-3M Treasury Spread (pp)",
        line=dict(color=C_IND, width=2),
        hovertemplate="%{x|%Y-%m}<br>Spread: %{y:.2f} pp<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["spy"], name="SPY price",
        line=dict(color=C_SPY, width=1.6),
        hovertemplate="%{x|%Y-%m}<br>SPY: %{y:.2f}<extra></extra>",
    ), secondary_y=True)
    inv = df["t10y3m"] < 0
    starts = inv.index[inv & ~inv.shift(1, fill_value=False)]
    ends = inv.index[inv & ~inv.shift(-1, fill_value=False)]
    for s, e in zip(starts, ends):
        fig.add_vrect(x0=s, x1=e, fillcolor="rgba(204,121,167,0.18)", line_width=0, layer="below")
    fig.add_hline(y=0, line_dash="dash", line_color=C_LINE, line_width=1, secondary_y=False)
    nber_legend(fig)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                             marker=dict(size=12, color="rgba(204,121,167,0.35)", symbol="square"),
                             name="Yield-curve inversion", hoverinfo="skip"))
    fig.update_layout(
        title="10Y-3M Treasury Spread vs SPY",
        template="plotly_white",
        height=520,
        hovermode="x unified",
        legend=dict(orientation="v", x=1.06, y=1, xanchor="left", yanchor="top"),
        margin=dict(r=190),
    )
    fig.update_yaxes(title_text="10Y-3M spread (percentage points)", secondary_y=False)
    fig.update_yaxes(title_text="SPY price", secondary_y=True)
    save("hero", fig, "10Y-3M spread and SPY price with NBER recessions and inversion bands.", ["data/t10y3m_spy_monthly_latest.parquet"])


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>Inverted/flat", "Q2", "Q3", "Q4<br>Steep"]
    fig = make_dual_panel_regime_chart(
        labels,
        q["sharpe"].astype(float).tolist(),
        (q["mean_return"].astype(float) * 12 * 100).tolist(),
        signal_label="10Y-3M Spread",
        x_axis_title="Yield-curve spread quartile",
        axis_noun="",
    )
    fig.update_layout(title="SPY Returns by Yield-Curve Regime")
    save("regime_stats", fig, "SPY performance by 10Y-3M spread quartile.", ["results/t10y3m_spy/regime_quartile_returns.csv"])


def chart_correlation_heatmap() -> None:
    corr = pd.read_csv(CORE / "correlations.csv")
    sub = corr[corr["metric"] == "pearson"].copy()
    sub["signal"] = sub["pair_name"].str.replace(r"_to_spy_fwd_\d+m", "", regex=True)
    sub["horizon"] = sub["pair_name"].str.extract(r"fwd_(\d+)m")[0] + "m"
    piv = sub.pivot_table(index="signal", columns="horizon", values="value", aggfunc="first")
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=piv.columns, y=piv.index, colorscale="RdBu", zmid=0,
        text=np.round(piv.values, 2), texttemplate="%{text}", colorbar=dict(title="r"),
    ))
    fig.update_layout(title="Correlation: Yield-Curve Signals vs Forward SPY Returns", template="plotly_white", height=520)
    save("correlation_heatmap", fig, "Pearson correlations between yield-curve transforms and forward SPY returns.", [str(CORE / "correlations.csv")])


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"], C_SPY, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="CCF"))
    fig.add_hline(y=ccf["upper_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=ccf["lower_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Pre-Whitened CCF: Yield-Curve Change vs SPY Return", xaxis_title="Lag (negative = spread leads)", yaxis_title="Correlation", template="plotly_white", height=430)
    save("ccf_prewhitened", fig, "Cross-correlation after differencing the spread; negative lags indicate the curve moves before SPY.", [str(CORE / "ccf_prewhitened.csv")])


def chart_granger() -> None:
    gr = pd.read_csv(CORE / "granger_causality.csv")
    fig = go.Figure()
    for direction, color, label in [
        ("indicator_to_target", C_IND, "10Y-3M -> SPY"),
        ("target_to_indicator", C_SPY, "SPY -> 10Y-3M"),
    ]:
        sub = gr[gr["direction"] == direction]
        fig.add_trace(go.Bar(x=sub["lag"], y=sub["f_statistic"], name=label, marker_color=color))
    fig.add_hline(y=4.0, line_dash="dash", line_color=C_LINE, annotation_text="rough 5% guide")
    fig.update_layout(title="Granger F-statistics by Lag", xaxis_title="Lag (months)", yaxis_title="F-statistic", barmode="group", template="plotly_white", height=430)
    save("granger_f_by_lag", fig, "Both-direction Granger test; p-values in hover/source table determine significance.", [str(CORE / "granger_causality.csv")])


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lp["horizon"], y=lp["coef"], mode="lines+markers", name="Coefficient", line=dict(color=C_IND)))
    fig.add_trace(go.Scatter(x=lp["horizon"], y=lp["ci_upper"], mode="lines", line=dict(color=C_BENCH, dash="dash"), name="95% CI upper"))
    fig.add_trace(go.Scatter(x=lp["horizon"], y=lp["ci_lower"], mode="lines", line=dict(color=C_BENCH, dash="dash"), name="95% CI lower", fill="tonexty"))
    fig.add_hline(y=0, line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Local Projections: SPY Response to Higher 10Y-3M Spread", xaxis_title="Forward horizon (months)", yaxis_title="Coefficient", template="plotly_white", height=430)
    save("local_projections", fig, "Local projection coefficients for the spread against forward SPY returns.", [str(CORE / "local_projections.csv")])


def chart_quantile() -> None:
    qr = pd.read_csv(CORE / "quantile_regression.csv")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qr["tau"], y=qr["coef"], mode="lines+markers", name="Quantile coefficient", line=dict(color=C_IND)))
    fig.add_trace(go.Scatter(x=qr["tau"], y=qr["ci_upper"], mode="lines", line=dict(color=C_BENCH, dash="dash"), name="95% CI upper"))
    fig.add_trace(go.Scatter(x=qr["tau"], y=qr["ci_lower"], mode="lines", line=dict(color=C_BENCH, dash="dash"), name="95% CI lower", fill="tonexty"))
    fig.add_hline(y=0, line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Quantile Regression: 3M Forward SPY Return", xaxis_title="Return quantile", yaxis_title="Spread coefficient", template="plotly_white", height=430)
    save("quantile_coef", fig, "Quantile regression checks whether the curve matters more in weak or strong SPY-return tails.", [str(CORE / "quantile_regression.csv")])


def chart_equity_drawdown() -> None:
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    fig = go.Figure()
    add_nber_shading(fig, x_min=strat.index.min(), x_max=strat.index.max())
    fig.add_trace(go.Scatter(x=strat.index, y=strat["strategy_equity"], name="Strategy", line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=strat.index, y=strat["benchmark_equity"], name="Buy-and-hold SPY", line=dict(color=C_BENCH, width=2, dash="dash")))
    nber_legend(fig)
    fig.update_layout(title="Strategy Equity Curve vs Buy-and-Hold SPY", yaxis_title="Growth of $1", template="plotly_white", height=470)
    save("equity_curves", fig, "Winner strategy equity curve compared with buy-and-hold SPY.", [str(RES / f"strategy_returns_{DATE_TAG}.csv")])

    dd_s = strat["strategy_equity"] / strat["strategy_equity"].cummax() - 1
    dd_b = strat["benchmark_equity"] / strat["benchmark_equity"].cummax() - 1
    fig2 = go.Figure()
    add_nber_shading(fig2, x_min=strat.index.min(), x_max=strat.index.max())
    fig2.add_trace(go.Scatter(x=strat.index, y=dd_s * 100, name="Strategy drawdown", line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=strat.index, y=dd_b * 100, name="Buy-and-hold drawdown", line=dict(color=C_BENCH, width=2, dash="dash")))
    nber_legend(fig2)
    fig2.update_layout(title="Strategy Drawdown vs Buy-and-Hold SPY", yaxis_title="Drawdown (%)", template="plotly_white", height=430)
    save("drawdown", fig2, "Drawdown comparison for the winner strategy and SPY buy-and-hold.", [str(RES / f"strategy_returns_{DATE_TAG}.csv")])


def chart_tournament() -> None:
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    valid = t[t["valid"] & (t["signal"] != "BENCHMARK")]
    fig = go.Figure(go.Scatter(
        x=valid["max_drawdown"] * 100,
        y=valid["oos_sharpe"],
        mode="markers",
        marker=dict(color=valid["lead_months"], colorscale="Viridis", showscale=True, colorbar=dict(title="Lead")),
        text=valid["signal"] + " / " + valid["threshold"] + " / " + valid["strategy"],
        name="Strategy candidates",
    ))
    fig.update_layout(title="Tournament Search: Sharpe vs Drawdown", xaxis_title="Max drawdown (%)", yaxis_title="OOS Sharpe", template="plotly_white", height=470)
    save("tournament_scatter", fig, "Each point is a valid strategy candidate from the tournament.", [str(RES / f"tournament_results_{DATE_TAG}.csv")])

    fig2 = go.Figure(go.Histogram(x=valid["oos_sharpe"], nbinsx=40, marker_color=C_IND, name="OOS Sharpe"))
    fig2.update_layout(title="Tournament Sharpe Distribution", xaxis_title="OOS Sharpe", yaxis_title="Count", template="plotly_white", height=410)
    save("tournament_sharpe_dist", fig2, "Distribution of search-phase OOS Sharpe across valid strategies.", [str(RES / f"tournament_results_{DATE_TAG}.csv")])


def chart_rolling_correlation() -> None:
    df = load_monthly()
    rc = df["t10y3m"].rolling(60, min_periods=36).corr(df["spy_ret"])
    out = pd.DataFrame({"date": rc.index, "rolling_corr": rc.values}).dropna()
    out.to_csv(RES / f"rolling_correlation_{PAIR}.csv", index=False)
    fig = go.Figure()
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    fig.add_trace(go.Scatter(x=rc.index, y=rc.values, name="60M rolling correlation", line=dict(color=C_IND)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_LINE)
    nber_legend(fig)
    fig.update_layout(title="Rolling Correlation: 10Y-3M Spread vs SPY Return", yaxis_title="Correlation", template="plotly_white", height=430)
    save("rolling_correlation", fig, "Rolling 60-month correlation between the yield spread and SPY monthly returns.", [str(RES / f"rolling_correlation_{PAIR}.csv")])


def chart_structural_break() -> None:
    df = load_monthly()
    roll = df["spy_ret"].rolling(60, min_periods=36).corr(df["t10y3m"])
    z = (roll - roll.mean()) / roll.std()
    payload = {"pair_id": PAIR, "method": "rolling-correlation z-score proxy", "max_abs_z": float(z.abs().max())}
    (RES / f"structural_break_{PAIR}.json").write_text(json.dumps(payload, indent=2) + "\n")
    fig = go.Figure()
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    fig.add_trace(go.Scatter(x=z.index, y=z.values, name="Break proxy z-score", line=dict(color=C_BAD)))
    fig.add_hline(y=2, line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=-2, line_dash="dash", line_color=C_LINE)
    nber_legend(fig)
    fig.update_layout(title="Structural Break Proxy: Relationship Stability", yaxis_title="Rolling-correlation z-score", template="plotly_white", height=430)
    save("structural_break", fig, "Proxy check for large changes in the spread-SPY relationship.", [str(RES / f"structural_break_{PAIR}.json")])


def chart_subperiod() -> None:
    sp = pd.read_csv(RES / "subperiod_sharpe.csv")
    fig = go.Figure(go.Bar(x=sp["period"], y=sp["buy_hold_sharpe"], marker_color=C_IND, name="SPY Sharpe"))
    fig.update_layout(title="SPY Sharpe During Major Episodes", yaxis_title="Sharpe", template="plotly_white", height=410)
    save("subperiod_sharpe", fig, "Buy-and-hold SPY Sharpe during major yield-curve and market-stress episodes.", ["results/t10y3m_spy/subperiod_sharpe.csv"])
    save("walk_forward", fig, "Alias for the dashboard's standard walk-forward chart slot.", ["results/t10y3m_spy/subperiod_sharpe.csv"])


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_monthly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    fig.add_trace(go.Scatter(x=df.index, y=df["t10y3m"], name="10Y-3M spread", line=dict(color=C_IND)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_SPY)), secondary_y=True)
    fig.add_hline(y=0, line_dash="dash", line_color=C_LINE, secondary_y=False)
    nber_legend(fig)
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="Spread (pp)", secondary_y=False)
    fig.update_yaxes(title_text="SPY", secondary_y=True)
    save(f"history_zoom_{slug}", fig, title, ["data/t10y3m_spy_monthly_latest.parquet"])


def main() -> None:
    chart_hero()
    chart_regime_stats()
    chart_correlation_heatmap()
    chart_ccf()
    chart_granger()
    chart_local_projections()
    chart_quantile()
    chart_equity_drawdown()
    chart_tournament()
    chart_rolling_correlation()
    chart_structural_break()
    chart_subperiod()
    chart_history_zoom("dotcom", "Dot-Com Cycle: Inversion Before the 2001 Recession", "1998-01-31", "2003-12-31")
    chart_history_zoom("gfc", "Global Financial Crisis: Curve Inversion Before the Drawdown", "2005-01-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock: A Brief Pre-Shock Inversion", "2018-01-31", "2021-12-31")
    chart_history_zoom("inflation_2022", "2022-24 Inversion: Early Warning, Long Wait", "2021-01-31", "2025-11-30")
    chart_history_zoom("rate_hike_2022", "2022-24 Inversion: Early Warning, Long Wait", "2021-01-31", "2025-11-30")
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
