#!/usr/bin/env python3
"""Chart generation for SLOOS C&I (Small Firms) net-% tightening x SPY.

QUARTERLY pair. Reads data/sloos_ci_small_spy_quarterly_latest.parquet and
results/sloos_ci_small_spy/* at DATE_TAG 20260830. Produces the same chart-name
set the config references (hero, equity_curves, drawdown, correlation_heatmap,
ccf_prewhitened, granger_f_by_lag, local_projections, quantile_coef,
regime_stats, rolling_correlation, structural_break, subperiod_sharpe,
tournament_scatter, tournament_sharpe_dist, walk_forward + history_zoom
episodes). Each chart carries a _meta.json sidecar. write_image is wrapped in
try/except because Chrome may be absent in the devcontainer.

HONEST FRAMING (binding): the winner is a FOUND-IN-SEARCH candidate whose
direction (procyclical, L3q) CONTRADICTS the countercyclical credit-crunch
prior. Charts label numbers as search-phase / descriptive, never as validated
edge. Every number traces to results/sloos_ci_small_spy/*.
"""

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

PAIR = "sloos_ci_small_spy"
DATE_TAG = "20260830"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

# Colorblind-friendly palette (Wong), consistent with the fleet.
C_IND = "#D55E00"     # indicator (SLOOS tightening)
C_TGT = "#0072B2"     # target (SPY)
C_STRAT = "#009E73"   # winner strategy
C_BENCH = "#6C7A89"   # buy-and-hold benchmark
C_LINE = "#4D4D4D"
C_STRESS = "#CC79A7"


def load_quarterly() -> pd.DataFrame:
    df = pd.read_parquet(REPO / "data" / f"{PAIR}_quarterly_latest.parquet")
    df.index = pd.to_datetime(df.index)
    return df


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    try:
        fig.write_image(OUT / f"_perceptual_check_{name}.png", width=1200, height=600, scale=1)
    except Exception as exc:  # Chrome/kaleido may be absent in the devcontainer
        print(f"  (png skipped for {name}: {exc.__class__.__name__})")
    meta = {
        "chart_name": name,
        "pair_id": PAIR,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/generate_charts_sloos_ci_small_spy.py",
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


def chart_hero() -> None:
    df = load_quarterly()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    fig.add_hline(y=0, line_color=C_LINE, line_width=1, secondary_y=False)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["sloos_ci_small"],
            name="SLOOS net-% tightening (small firms)",
            line=dict(color=C_IND, width=2),
            hovertemplate="%{x|%Y-Q%q}<br>Net-%% tightening: %{y:.1f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["spy"],
            name="SPY price",
            line=dict(color=C_TGT, width=1.6),
            hovertemplate="%{x|%Y-Q%q}<br>SPY: %{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )
    nber_legend(fig)
    fig.update_layout(
        title="SLOOS C&I Tightening (Small Firms) vs SPY",
        template="plotly_white",
        height=520,
        hovermode="x unified",
        legend=dict(orientation="v", x=1.05, y=1),
        margin=dict(r=210),
    )
    fig.update_yaxes(title_text="Net % of banks tightening", secondary_y=False)
    fig.update_yaxes(title_text="SPY price", secondary_y=True)
    save(
        "hero",
        fig,
        "SLOOS small-firm net-% C&I tightening and SPY with NBER recessions; "
        "tightening spikes cluster around credit crunches.",
        [f"data/{PAIR}_quarterly_latest.parquet"],
    )


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = [
        "Q1<br>Least tightening",
        "Q2",
        "Q3",
        "Q4<br>Most tightening",
    ]
    fig = make_dual_panel_regime_chart(
        labels,
        q["sharpe"].astype(float).tolist(),
        (q["mean_return"].astype(float) * 4 * 100).tolist(),
        signal_label="SLOOS tightening",
        x_axis_title="SLOOS net-% tightening quartile",
        axis_noun="",
    )
    fig.update_layout(title="SPY Returns by SLOOS-Tightening Regime")
    save(
        "regime_stats",
        fig,
        "Concurrent SPY performance across SLOOS-tightening quartiles; the "
        "highest-tightening quartile (Q4) has the weakest Sharpe (0.31) — "
        "consistent with the countercyclical credit prior.",
        [f"results/{PAIR}/regime_quartile_returns.csv"],
    )


def chart_correlation_heatmap() -> None:
    corr = pd.read_csv(CORE / "correlations.csv")
    sub = corr[corr["metric"] == "pearson"].copy()
    sub["signal"] = sub["pair_name"].str.replace(r"_to_spy_fwd_\d+q", "", regex=True)
    sub["horizon"] = sub["pair_name"].str.extract(r"fwd_(\d+)q")[0] + "q"
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
    fig.update_layout(
        title="Correlation: SLOOS Signals vs Forward SPY Returns",
        template="plotly_white",
        height=520,
    )
    save(
        "correlation_heatmap",
        fig,
        "Pearson correlations between SLOOS transforms and forward SPY returns "
        "at 1-, 2-, and 4-quarter horizons; associations are weak and mostly "
        "mildly negative (none significant).",
        [str(CORE / "correlations.csv")],
    )


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"], C_IND, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="CCF"))
    fig.add_hline(y=ccf["upper_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=ccf["lower_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.update_layout(
        title="Cross-Correlation: SLOOS Tightening vs SPY Return",
        xaxis_title="Lag (quarters)",
        yaxis_title="Correlation",
        template="plotly_white",
        height=430,
    )
    save(
        "ccf_prewhitened",
        fig,
        "Pre-whitened cross-correlation between SLOOS tightening and SPY "
        "returns; the only bars breaching the band are at negative offsets "
        "(-1, -2), a mild inverse concurrent echo — not a clean predictive lead.",
        [str(CORE / "ccf_prewhitened.csv")],
    )


def chart_granger() -> None:
    gr = pd.read_csv(RES / "granger_by_lag.csv")
    fig = go.Figure()
    if not gr.empty:
        fig.add_trace(go.Bar(x=gr["lag"], y=gr["p_value"], name="p-value", marker_color=C_IND))
    fig.add_hline(y=0.05, line_dash="dash", line_color=C_LINE, annotation_text="p = 0.05")
    fig.update_layout(
        title="Granger Causality: Does SLOOS Tightening Help Forecast SPY?",
        xaxis_title="Lag (quarters)",
        yaxis_title="p-value",
        template="plotly_white",
        height=430,
    )
    save(
        "granger_f_by_lag",
        fig,
        "Granger p-values by quarterly lag for SLOOS tightening predicting SPY "
        "returns; every lag is insignificant (min p 0.23) — SLOOS does not "
        "Granger-cause SPY at the tested lags.",
        [f"results/{PAIR}/granger_by_lag.csv"],
    )


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = go.Figure(
        go.Bar(x=lp["horizon"].astype(str) + "q", y=lp["coef"], marker_color=C_IND, name="Coefficient")
    )
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(
        title="Local Projection: SPY Response to Rising SLOOS Tightening",
        xaxis_title="Forward horizon (quarters)",
        yaxis_title="Coefficient",
        template="plotly_white",
        height=430,
    )
    save(
        "local_projections",
        fig,
        "Estimated SPY response to a rise in SLOOS 4-quarter tightening change; "
        "coefficients are near zero and insignificant across horizons.",
        [str(CORE / "local_projections.csv")],
    )


def chart_quantile() -> None:
    q = pd.read_csv(CORE / "quantile_regression.csv")
    fig = go.Figure(
        go.Scatter(x=q["quantile"], y=q["coef"], mode="lines+markers", name="Coefficient", line=dict(color=C_IND))
    )
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(
        title="Quantile Regression Coefficient",
        xaxis_title="SPY return quantile",
        yaxis_title="SLOOS coefficient",
        template="plotly_white",
        height=430,
    )
    save(
        "quantile_coef",
        fig,
        "SLOOS coefficient across SPY forward-return quantiles; flat and "
        "near-zero — no state-dependent predictive content.",
        [str(CORE / "quantile_regression.csv")],
    )


def chart_equity_drawdown() -> None:
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat.index, y=strat["strategy_equity"], name="Winner strategy", line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=strat.index, y=strat["benchmark_equity"], name="Buy-and-hold SPY", line=dict(color=C_BENCH, width=2, dash="dash")))
    fig.update_layout(
        title="Equity Curve: SLOOS Strategy vs SPY",
        yaxis_title="Growth of $1",
        template="plotly_white",
        height=460,
    )
    save(
        "equity_curves",
        fig,
        "Winner strategy equity curve vs buy-and-hold SPY (found-in-search "
        "candidate; full-sample path, OOS from 2017-12).",
        [f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv"],
    )

    dd = pd.DataFrame(index=strat.index)
    dd["strategy"] = strat["strategy_equity"] / strat["strategy_equity"].cummax() - 1
    dd["benchmark"] = strat["benchmark_equity"] / strat["benchmark_equity"].cummax() - 1
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["strategy"] * 100, name="Winner strategy", line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["benchmark"] * 100, name="Buy-and-hold SPY", line=dict(color=C_BENCH, width=2, dash="dash")))
    fig2.update_layout(
        title="Drawdown Comparison",
        yaxis_title="Drawdown (%)",
        template="plotly_white",
        height=430,
    )
    save(
        "drawdown",
        fig2,
        "Drawdown comparison; the shallower drawdown (OOS -4.3% vs -23.9%) is "
        "the strategy's one defensible virtue — read the Sharpe as volatility "
        "avoidance.",
        [f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv"],
    )


def chart_tournament() -> None:
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    valid = t[(t["valid"]) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure(
        go.Box(x=valid["lead_quarters"].astype(str), y=valid["oos_sharpe"], name="Valid strategies", marker_color=C_IND)
    )
    fig.add_hline(y=0.89098, line_dash="dash", line_color=C_BENCH, annotation_text="Buy-and-hold 0.89")
    fig.update_layout(
        title="Tournament Sharpe Distribution by Lead",
        xaxis_title="Lead (quarters)",
        yaxis_title="OOS Sharpe",
        template="plotly_white",
        height=450,
    )
    save(
        "tournament_sharpe_dist",
        fig,
        "OOS Sharpe distribution across valid tournament strategies by lead; "
        "the median valid combo (0.60) UNDERPERFORMS buy-and-hold (0.89) — the "
        "winner is the right tail of its own search.",
        [f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
    )
    save(
        "tournament_scatter",
        fig,
        "Distribution of OOS Sharpe across valid tournament strategies by "
        "lead; the winner (1.51) is the grid maximum, median valid 0.60 "
        "below buy-and-hold 0.89.",
        [f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
    )


def chart_rolling_correlation() -> None:
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(
        go.Scatter(x=rc["date"], y=rc["rolling_corr"], name="Rolling correlation", line=dict(color=C_IND))
    )
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(
        title="Rolling Correlation: SLOOS Tightening vs SPY",
        yaxis_title="Correlation",
        template="plotly_white",
        height=430,
    )
    save(
        "rolling_correlation",
        fig,
        "Rolling correlation between SLOOS tightening and SPY returns; the sign "
        "swings through time, so the relationship needs ongoing monitoring.",
        [f"results/{PAIR}/rolling_correlation_{PAIR}.csv"],
    )


def chart_structural_break() -> None:
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    fig = go.Figure(
        go.Indicator(mode="number", value=sb["max_abs_z"], title={"text": "Max abs rolling-correlation z-score"})
    )
    fig.update_layout(title="Structural Break Proxy", template="plotly_white", height=360)
    save(
        "structural_break",
        fig,
        "Proxy check for large changes in the SLOOS-SPY relationship "
        "(rolling-correlation z-score); max |z| = 2.41.",
        [f"results/{PAIR}/structural_break_{PAIR}.json"],
    )


def chart_subperiod() -> None:
    sp = pd.read_csv(RES / "subperiod_sharpe.csv")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sp["period"], y=sp["strategy_sharpe"], name="Strategy Sharpe", marker_color=C_STRAT))
    fig.add_trace(go.Bar(x=sp["period"], y=sp["buy_hold_sharpe"], name="SPY Sharpe", marker_color=C_BENCH))
    fig.update_layout(
        title="Sharpe During Major Credit-Stress Episodes",
        yaxis_title="Sharpe",
        barmode="group",
        template="plotly_white",
        height=410,
    )
    save(
        "subperiod_sharpe",
        fig,
        "Strategy and buy-and-hold SPY Sharpe during major credit-stress "
        "episodes; several pre-OOS episodes precede the strategy window, so "
        "the durability read rests on a handful of cycles.",
        [f"results/{PAIR}/subperiod_sharpe.csv"],
    )
    save(
        "walk_forward",
        fig,
        "Sub-period Sharpe by credit-stress episode (walk-forward durability "
        "slot); the lead rests on few credit cycles.",
        [f"results/{PAIR}/subperiod_sharpe.csv"],
    )


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_quarterly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    fig.add_hline(y=0, line_color=C_LINE, line_width=1, secondary_y=False)
    fig.add_trace(
        go.Scatter(x=df.index, y=df["sloos_ci_small"], name="SLOOS net-% tightening", line=dict(color=C_IND)),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_TGT)),
        secondary_y=True,
    )
    nber_legend(fig)
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="Net % tightening", secondary_y=False)
    fig.update_yaxes(title_text="SPY", secondary_y=True)
    save(
        f"history_zoom_{slug}",
        fig,
        f"{title}; gray bands are NBER recessions.",
        [f"data/{PAIR}_quarterly_latest.parquet"],
    )


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
    chart_history_zoom("dotcom", "Dot-Com Recession: Tightening Rose Ahead of the Downturn", "1999-03-31", "2003-12-31")
    chart_history_zoom("gfc", "Global Financial Crisis: Net-Tightening Spiked to Record Highs", "2006-03-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock: Banks Tightened Sharply in 2020-Q2", "2018-03-31", "2021-12-31")
    chart_history_zoom("rate_hike_2022", "2022-23 Tightening: Post-SVB Credit Squeeze", "2021-03-31", "2025-09-30")
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
