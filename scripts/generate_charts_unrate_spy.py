#!/usr/bin/env python3
"""Chart generation for UNRATE x SPY."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart  # noqa: E402

PAIR = "unrate_spy"
DATE_TAG = "20260717"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

C_IND = "#D55E00"
C_TGT = "#0072B2"
C_STRAT = "#009E73"
C_BENCH = "#6C7A89"
C_LINE = "#4D4D4D"
C_STRESS = "#CC79A7"


def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / "unrate_spy_monthly_latest.parquet")


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    fig.write_image(OUT / f"_perceptual_check_{name}.png", width=1200, height=600, scale=1)
    meta = {
        "chart_name": name,
        "pair_id": PAIR,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/generate_charts_unrate_spy.py",
        "caption": caption,
        "narrative_alignment_note": caption,
        "disposition": "consumed",
        "source_artifacts": sources,
    }
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  wrote {name}.json")


def nber_legend(fig: go.Figure) -> None:
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square"),
            name="NBER recession period",
            hoverinfo="skip",
        )
    )


def sahm_legend(fig: go.Figure) -> None:
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=12, color="rgba(204,121,167,0.28)", symbol="square"),
            name="Sahm-style labor stress",
            hoverinfo="skip",
        )
    )


def add_sahm_shading(fig: go.Figure, df: pd.DataFrame) -> None:
    stress = df["unrate_sahm"].fillna(0) >= 0.5
    starts = stress.index[stress & ~stress.shift(1, fill_value=False)]
    ends = stress.index[stress & ~stress.shift(-1, fill_value=False)]
    for start, end in zip(starts, ends):
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor="rgba(204,121,167,0.18)",
            line_width=0,
            layer="below",
        )


def chart_hero() -> None:
    df = load_monthly()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    add_sahm_shading(fig, df)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["unrate"],
            name="U.S. unemployment rate",
            line=dict(color=C_IND, width=2),
            hovertemplate="%{x|%Y-%m}<br>UNRATE: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["spy"],
            name="SPY price",
            line=dict(color=C_TGT, width=1.6),
            hovertemplate="%{x|%Y-%m}<br>SPY: %{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )
    nber_legend(fig)
    sahm_legend(fig)
    fig.update_layout(
        title="U.S. Unemployment Rate vs SPY",
        template="plotly_white",
        height=520,
        hovermode="x unified",
        legend=dict(orientation="v", x=1.05, y=1),
        margin=dict(r=190),
    )
    fig.update_yaxes(title_text="Unemployment rate (%)", secondary_y=False)
    fig.update_yaxes(title_text="SPY price", secondary_y=True)
    save("hero", fig, "UNRATE and SPY with NBER recessions and Sahm-style labor-stress bands.", ["data/unrate_spy_monthly_latest.parquet"])


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>Low unemployment", "Q2", "Q3", "Q4<br>High unemployment"]
    fig = make_dual_panel_regime_chart(
        labels,
        q["sharpe"].astype(float).tolist(),
        (q["mean_return"].astype(float) * 12 * 100).tolist(),
        signal_label="UNRATE",
        x_axis_title="Unemployment-rate quartile",
        axis_noun="",
    )
    fig.update_layout(title="SPY Returns by Unemployment Regime")
    save("regime_stats", fig, "SPY performance across unemployment-rate quartiles.", ["results/unrate_spy/regime_quartile_returns.csv"])


def chart_correlation_heatmap() -> None:
    corr = pd.read_csv(CORE / "correlations.csv")
    sub = corr[corr["metric"] == "pearson"].copy()
    sub["signal"] = sub["pair_name"].str.replace(r"_to_spy_fwd_\d+m", "", regex=True)
    sub["horizon"] = sub["pair_name"].str.extract(r"fwd_(\d+)m")[0] + "m"
    piv = sub.pivot_table(index="signal", columns="horizon", values="value", aggfunc="first")
    fig = go.Figure(
        go.Heatmap(
            z=piv.values,
            x=piv.columns,
            y=piv.index,
            colorscale="RdBu",
            zmid=0,
            text=np.round(piv.values, 2),
            texttemplate="%{text}",
            colorbar=dict(title="r"),
        )
    )
    fig.update_layout(title="Correlation: UNRATE Signals vs Forward SPY Returns", template="plotly_white", height=520)
    save("correlation_heatmap", fig, "Pearson correlations between UNRATE transforms and forward SPY returns.", [str(CORE / "correlations.csv")])


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"], C_IND, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="CCF"))
    fig.add_hline(y=ccf["upper_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=ccf["lower_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Cross-Correlation: UNRATE Change vs SPY Return", xaxis_title="Lag", yaxis_title="Correlation", template="plotly_white", height=430)
    save("ccf_prewhitened", fig, "Cross-correlation between UNRATE 3-month change and SPY returns.", [str(CORE / "ccf_prewhitened.csv")])


def chart_granger() -> None:
    gr = pd.read_csv(CORE / "granger_causality.csv")
    fig = go.Figure()
    if not gr.empty:
        fig.add_trace(go.Bar(x=gr["lag"], y=gr["p_value"], name="p-value", marker_color=C_IND))
    fig.add_hline(y=0.05, line_dash="dash", line_color=C_LINE, annotation_text="p = 0.05")
    fig.update_layout(title="Granger Causality: Does UNRATE Help Forecast SPY?", xaxis_title="Lag (months)", yaxis_title="p-value", template="plotly_white", height=430)
    save("granger_f_by_lag", fig, "Granger p-values by lag for UNRATE 3-month change predicting SPY returns.", [str(CORE / "granger_causality.csv")])


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = go.Figure(go.Bar(x=lp["horizon"].astype(str) + "m", y=lp["coef"], marker_color=C_IND, name="Coefficient"))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Local Projection: SPY Response to Rising UNRATE", xaxis_title="Forward horizon", yaxis_title="Coefficient", template="plotly_white", height=430)
    save("local_projections", fig, "Estimated SPY response to a 1 percentage point rise in the 3-month UNRATE change.", [str(CORE / "local_projections.csv")])


def chart_quantile() -> None:
    q = pd.read_csv(CORE / "quantile_regression.csv")
    fig = go.Figure(go.Scatter(x=q["quantile"], y=q["coef"], mode="lines+markers", name="Coefficient", line=dict(color=C_IND)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Quantile Regression Coefficient", xaxis_title="SPY return quantile", yaxis_title="UNRATE coefficient", template="plotly_white", height=430)
    save("quantile_coef", fig, "UNRATE coefficient across SPY forward-return quantiles.", [str(CORE / "quantile_regression.csv")])


def chart_equity_drawdown() -> None:
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat.index, y=strat["strategy_equity"], name="Winner strategy", line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=strat.index, y=strat["benchmark_equity"], name="Buy-and-hold SPY", line=dict(color=C_BENCH, width=2, dash="dash")))
    fig.update_layout(title="Equity Curve: UNRATE Strategy vs SPY", yaxis_title="Growth of $1", template="plotly_white", height=460)
    save("equity_curves", fig, "Winner strategy equity curve compared with buy-and-hold SPY.", [str(RES / f"strategy_returns_{DATE_TAG}.csv")])

    dd = pd.DataFrame(index=strat.index)
    dd["strategy"] = strat["strategy_equity"] / strat["strategy_equity"].cummax() - 1
    dd["benchmark"] = strat["benchmark_equity"] / strat["benchmark_equity"].cummax() - 1
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["strategy"] * 100, name="Winner strategy", line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["benchmark"] * 100, name="Buy-and-hold SPY", line=dict(color=C_BENCH, width=2, dash="dash")))
    fig2.update_layout(title="Drawdown Comparison", yaxis_title="Drawdown (%)", template="plotly_white", height=430)
    save("drawdown", fig2, "Drawdown comparison for the winner strategy and SPY buy-and-hold.", [str(RES / f"strategy_returns_{DATE_TAG}.csv")])


def chart_tournament() -> None:
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    valid = t[(t["valid"]) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure(go.Box(x=valid["lead_months"].astype(str), y=valid["oos_sharpe"], name="Valid strategies", marker_color=C_IND))
    fig.update_layout(title="Tournament Sharpe Distribution by Lead", xaxis_title="Lead (months)", yaxis_title="OOS Sharpe", template="plotly_white", height=450)
    save("tournament_sharpe_dist", fig, "Distribution of OOS Sharpe across valid tournament strategies by lead.", [str(RES / f"tournament_results_{DATE_TAG}.csv")])
    save("tournament_scatter", fig, "Alias for tournament scatter slot.", [str(RES / f"tournament_results_{DATE_TAG}.csv")])


def chart_rolling_correlation() -> None:
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=rc["date"], y=rc["rolling_corr"], name="60-month rolling correlation", line=dict(color=C_IND)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Rolling Correlation: UNRATE Change vs SPY", yaxis_title="Correlation", template="plotly_white", height=430)
    save("rolling_correlation", fig, "Rolling 60-month correlation between UNRATE 3-month change and SPY returns.", [str(RES / f"rolling_correlation_{PAIR}.csv")])


def chart_structural_break() -> None:
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    fig = go.Figure(go.Indicator(mode="number", value=sb["max_abs_z"], title={"text": "Max abs rolling-correlation z-score"}))
    fig.update_layout(title="Structural Break Proxy", template="plotly_white", height=360)
    save("structural_break", fig, "Proxy check for large changes in the UNRATE-SPY relationship.", [str(RES / f"structural_break_{PAIR}.json")])


def chart_subperiod() -> None:
    sp = pd.read_csv(RES / "subperiod_sharpe.csv")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sp["period"], y=sp["strategy_sharpe"], name="Strategy Sharpe", marker_color=C_STRAT))
    fig.add_trace(go.Bar(x=sp["period"], y=sp["buy_hold_sharpe"], name="SPY Sharpe", marker_color=C_BENCH))
    fig.update_layout(title="Sharpe During Major Stress Episodes", yaxis_title="Sharpe", barmode="group", template="plotly_white", height=410)
    save("subperiod_sharpe", fig, "Strategy and buy-and-hold SPY Sharpe during major stress episodes.", ["results/unrate_spy/subperiod_sharpe.csv"])
    save("walk_forward", fig, "Alias for the dashboard's standard walk-forward chart slot.", ["results/unrate_spy/subperiod_sharpe.csv"])


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_monthly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    add_sahm_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df["unrate"], name="UNRATE", line=dict(color=C_IND)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_TGT)), secondary_y=True)
    nber_legend(fig)
    sahm_legend(fig)
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="UNRATE (%)", secondary_y=False)
    fig.update_yaxes(title_text="SPY", secondary_y=True)
    save(f"history_zoom_{slug}", fig, f"{title}; gray bands are NBER recessions and pink bands are Sahm-style labor stress.", ["data/unrate_spy_monthly_latest.parquet"])


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
    chart_history_zoom("dotcom", "Dot-Com Cycle: Unemployment Rose After Equity Weakness", "1999-01-31", "2003-12-31")
    chart_history_zoom("gfc", "Global Financial Crisis: Labor Stress Confirmed the Recession", "2006-01-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock: Unemployment Spike", "2018-01-31", "2021-12-31")
    chart_history_zoom("inflation_2022", "2022 Rate-Hike Cycle: Labor Market Stayed Resilient", "2021-01-31", "2025-12-31")
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
