#!/usr/bin/env python3
"""Chart generation for New Home Sales (HSN1F) x SPY (Phase B). Captions carry no typed results: every number in a caption is
read from the pipeline artifacts."""

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
import chart_provenance  # noqa: E402  (records chart inputs; imported before any data is read)
from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart  # noqa: E402

PAIR = "nhs_saar_rebuilt_spy"
DATE_TAG = "20261018"
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
    return pd.read_parquet(REPO / "data" / "nhs_saar_rebuilt_spy_monthly_latest.parquet")


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    chart_provenance.record(PAIR, OUT / f"{name}.json", sources, "scripts/generate_charts_nhs_saar_rebuilt_spy.py")
    try:
        fig.write_image(OUT / f"_perceptual_check_{name}.png", width=1200, height=600, scale=1)
    except Exception as exc:  # noqa: BLE001 - PNG is a secondary perceptual-check artifact
        print(f"  (perceptual PNG skipped for {name}: {exc.__class__.__name__})")
    meta = {
        "chart_name": name,
        "pair_id": PAIR,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/generate_charts_nhs_saar_rebuilt_spy.py",
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


def contraction_legend(fig: go.Figure) -> None:
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=12, color="rgba(204,121,167,0.28)", symbol="square"),
            name="Home sales below year-earlier level",
            hoverinfo="skip",
        )
    )


def add_contraction_shading(fig: go.Figure, df: pd.DataFrame) -> None:
    stress = df["nhs_pct_yoy"].fillna(0) < 0
    starts = stress.index[stress & ~stress.shift(1, fill_value=False)]
    ends = stress.index[stress & ~stress.shift(-1, fill_value=False)]
    for start, end in zip(starts, ends):
        # add_shape with xref/yref: add_vrect silently adds nothing on make_subplots(secondary_y) figures
        fig.add_shape(type="rect", xref="x", yref="paper", x0=start.strftime("%Y-%m-%d"), x1=end.strftime("%Y-%m-%d"), y0=0, y1=1,
                      fillcolor="rgba(204,121,167,0.22)", line_width=0, layer="below")


def chart_hero() -> None:
    df = load_monthly()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    add_contraction_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df["hsn1f"], name="New home sales (thousands, SAAR)",
                             line=dict(color=C_IND, width=2),
                             hovertemplate="%{x|%Y-%m}<br>HSN1F: %{y:,.0f}k<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY price", line=dict(color=C_TGT, width=1.6),
                             hovertemplate="%{x|%Y-%m}<br>SPY: %{y:.2f}<extra></extra>"), secondary_y=True)
    nber_legend(fig)
    contraction_legend(fig)
    fig.update_layout(title="New Home Sales vs SPY", template="plotly_white", height=520, hovermode="x unified",
                      legend=dict(orientation="v", x=1.05, y=1), margin=dict(r=210))
    fig.update_yaxes(title_text="New home sales (thousands, SAAR)", secondary_y=False)
    fig.update_yaxes(title_text="SPY price", secondary_y=True)
    save("hero", fig, "New home sales and SPY with NBER recessions; pink bands mark months when new home sales were "
         "below their year-earlier level.", [f"data/{PAIR}_monthly_latest.parquet"])


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>weakest", "Q2", "Q3", "Q4<br>strongest"]
    fig = make_dual_panel_regime_chart(
        labels, q["sharpe"].astype(float).tolist(), (q["mean_return"].astype(float) * 12 * 100).tolist(),
        signal_label="6-month home-sales growth", x_axis_title="Quartile of 6-month growth in new home sales",
        axis_noun="", sample_sizes=q["n"].astype(int).tolist())
    fig.update_layout(title=dict(text="SPY Returns by New-Home-Sales Growth Regime", y=0.98), margin=dict(t=150))
    save("regime_stats", fig, "SPY performance in the same month across quartiles of 6-month growth in new home "
         "sales.", [f"results/{PAIR}/regime_quartile_returns.csv"])


def chart_correlation_heatmap() -> None:
    corr = pd.read_csv(CORE / "correlations.csv")
    sub = corr[corr["metric"] == "pearson"].copy()
    sub["signal"] = sub["pair_name"].str.replace(r"_to_spy_fwd_\d+m", "", regex=True)
    sub["h"] = sub["pair_name"].str.extract(r"fwd_(\d+)m")[0].astype(int)
    piv = sub.pivot_table(index="signal", columns="h", values="value", aggfunc="first").sort_index(axis=1)
    fig = go.Figure(go.Heatmap(z=piv.values, x=[f"{h}m" for h in piv.columns], y=piv.index, colorscale="RdBu",
                               zmid=0, text=np.round(piv.values, 2), texttemplate="%{text}", colorbar=dict(title="r")))
    fig.update_layout(title="Correlation: New-Home-Sales Signals vs Forward SPY Returns", template="plotly_white",
                      height=520, xaxis_title="Forward SPY return horizon")
    save("correlation_heatmap", fig, "Pearson correlations between new-home-sales transforms and forward SPY returns.",
         [str(CORE / "correlations.csv")])


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"], C_IND, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="CCF"))
    for col, show in (("upper_ci", True), ("lower_ci", False)):   # 95% band per lag (n differs by lag)
        fig.add_trace(go.Scatter(x=ccf["lag"], y=ccf[col], mode="lines", line=dict(dash="dash", color=C_LINE, shape="hvh"),
                                 name="95% band (1.96/sqrt(n))", showlegend=show, hoverinfo="skip"))
    fig.update_layout(title="Cross-Correlation: Change in 6-Month Home-Sales Growth vs SPY Return",
                      xaxis_title="Lag (months; positive = home sales first)", yaxis_title="Correlation",
                      template="plotly_white", height=430)
    save("ccf_prewhitened", fig, "Cross-correlation between the monthly change in 6-month new-home-sales growth and "
         "SPY returns.", [str(CORE / "ccf_prewhitened.csv")])


def chart_granger() -> None:
    gr = pd.read_csv(CORE / "granger_causality.csv")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=gr["lag"], y=gr["p_value"], name="p-value (single lag)", marker_color=C_IND))
    fig.add_trace(go.Scatter(x=gr["lag"], y=gr["p_value_holm"], name="Holm-adjusted p-value (all lags)",
                             mode="markers", marker=dict(color=C_LINE, symbol="diamond", size=9)))
    fig.add_hline(y=0.05, line_dash="dash", line_color=C_LINE)
    # label outside the plot area, right of the line end: never over a bar (live render and PNG)
    fig.add_annotation(text="p = 0.05", xref="paper", x=1.0, y=0.05, xanchor="left", showarrow=False,
                       font=dict(size=11, color=C_LINE))
    fig.update_layout(title="Granger Causality: Does Home-Sales Growth Help Forecast SPY?",
                      xaxis_title="Lag (months)", yaxis_title="p-value", template="plotly_white", height=430,
                      legend=dict(orientation="h", y=-0.2), margin=dict(r=80))
    save("granger_f_by_lag", fig, "Granger p-values by lag for 6-month new-home-sales growth predicting SPY returns, "
         "with Holm-adjusted p-values across the lags tested.", [str(CORE / "granger_causality.csv")])


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    half = (1.96 * lp["se"]).tolist()
    fig = go.Figure(go.Bar(x=lp["horizon"].astype(str) + "m", y=lp["coef"], marker_color=C_IND,
                           name="Coefficient (95% HAC CI)",
                           error_y=dict(type="data", array=half, visible=True, thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Local Projection: SPY Response to Faster Home-Sales Growth", xaxis_title="Forward horizon",
                      yaxis_title="Coefficient (95% HAC CI whiskers)", template="plotly_white", height=430)
    save("local_projections", fig, "Estimated forward SPY return per percentage point of 6-month new-home-sales growth "
         "(Newey-West errors).", [str(CORE / "local_projections.csv")])


def chart_quantile() -> None:
    q = pd.read_csv(CORE / "quantile_regression.csv")
    fig = go.Figure(go.Scatter(x=q["quantile"], y=q["coef"], mode="lines+markers", name="Coefficient (95% block-bootstrap CI)",
                               line=dict(color=C_IND),
                               error_y=dict(type="data", symmetric=False, array=(q["ci_high"] - q["coef"]).tolist(),
                                            arrayminus=(q["coef"] - q["ci_low"]).tolist(), visible=True,
                                            thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    qt = json.loads((CORE / "quantile_equality_test.json").read_text())
    verdict = ("slopes DIFFER across quantiles" if qt["reject_equality"] else
               "consistent with a uniform effect across quantiles")
    fig.add_annotation(text=f"Cross-quantile slope equality (block-bootstrap Wald): p={qt['p_value']:.3f} - {verdict}",
                       xref="paper", yref="paper", x=0, y=1.14, showarrow=False, font=dict(size=11), align="left")
    fig.update_layout(margin=dict(t=110), title=dict(text="Quantile Regression Coefficient", y=0.97),
                      xaxis_title="Quantile of 3-month forward SPY return",
                      yaxis_title="6-month growth coefficient (95% CI whiskers)", template="plotly_white", height=430)
    save("quantile_coef", fig, "6-month new-home-sales growth coefficient across quantiles of 3-month forward SPY "
         "returns.", [str(CORE / "quantile_regression.csv"), str(CORE / "quantile_equality_test.json")])


def chart_equity_drawdown() -> None:
    full = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    # from the first training month: before it the real-time rule has no published vintage (no position at all)
    is0 = full.index[full["sample"] == "IS"][0]
    strat = full.loc[is0:].copy()
    strat["strategy_equity"] = (1 + strat["strategy_return"]).cumprod()
    strat["benchmark_equity"] = (1 + strat["benchmark_return"]).cumprod()
    oos0 = strat.index[strat["sample"] == "OOS"][0].strftime("%Y-%m-%d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat.index, y=strat["strategy_equity"], name="Winner strategy (as known at the time)",
                             line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=strat.index, y=strat["benchmark_equity"], name="Buy-and-hold SPY",
                             line=dict(color=C_BENCH, width=2, dash="dash")))
    fig.add_shape(type="line", xref="x", yref="paper", x0=oos0, x1=oos0, y0=0, y1=1,
                  line=dict(dash="dot", color=C_LINE))
    fig.add_annotation(x=oos0, y=1, yref="paper", text="test period starts", showarrow=False, xanchor="left",
                       yanchor="bottom", font=dict(size=11))
    fig.update_layout(title="Equity Curve: New-Home-Sales Strategy vs SPY", yaxis_title="Growth of $1",
                      template="plotly_white", height=460)
    save("equity_curves", fig, "Winner strategy (as known at the time: real-time HSN1F vintages) equity curve compared "
         "with buy-and-hold SPY, both from the first training month.", [str(RES / f"strategy_returns_{DATE_TAG}.csv")])

    dd = pd.DataFrame(index=strat.index)
    dd["strategy"] = strat["strategy_equity"] / strat["strategy_equity"].cummax() - 1
    dd["benchmark"] = strat["benchmark_equity"] / strat["benchmark_equity"].cummax() - 1
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["strategy"] * 100, name="Winner strategy", line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["benchmark"] * 100, name="Buy-and-hold SPY",
                              line=dict(color=C_BENCH, width=2, dash="dash")))
    fig2.update_layout(title="Drawdown Comparison (from the first training month)", yaxis_title="Drawdown (%)", template="plotly_white", height=430)
    save("drawdown", fig2, "Drawdown comparison for the winner strategy (as known at the time) and SPY buy-and-hold.",
         [str(RES / f"strategy_returns_{DATE_TAG}.csv")])


def chart_tournament() -> None:
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    valid = t[(t["valid"]) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure(go.Box(x=valid["lead_months"].astype(str), y=valid["oos_sharpe"], name="Valid strategies",
                           marker_color=C_IND))
    fig.update_layout(title="Tournament Sharpe Distribution by Lead", xaxis_title="Lead (months)",
                      yaxis_title="OOS Sharpe", template="plotly_white", height=450)
    cap = ("Distribution of OOS Sharpe across valid tournament strategies by lead (as known at the time; the winner is "
           "chosen on training data, not on this OOS score).")
    save("tournament_sharpe_dist", fig, cap, [str(RES / f"tournament_results_{DATE_TAG}.csv")])
    save("tournament_scatter", fig, "Alias for tournament scatter slot.", [str(RES / f"tournament_results_{DATE_TAG}.csv")])


def chart_rolling_correlation() -> None:
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=rc["date"], y=rc["rolling_corr"], name="60-month rolling correlation",
                               line=dict(color=C_IND)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Rolling Correlation: 6-Month Home-Sales Growth vs SPY", yaxis_title="Correlation",
                      template="plotly_white", height=430)
    save("rolling_correlation", fig, "Rolling 60-month correlation between 6-month new-home-sales growth and SPY "
         "returns.", [str(RES / f"rolling_correlation_{PAIR}.csv")])


def chart_structural_break() -> None:
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    fig = go.Figure(go.Indicator(mode="number", value=sb["max_abs_z"], number=dict(valueformat=".2f"),
                                 title={"text": "Max abs rolling-correlation z-score"}))
    fig.update_layout(title="Structural Break Proxy", template="plotly_white", height=360)
    save("structural_break", fig, "Proxy check for large changes in the HSN1F-SPY relationship.",
         [str(RES / f"structural_break_{PAIR}.json")])


def chart_subperiod() -> None:
    sp = pd.read_csv(RES / "subperiod_sharpe.csv")
    x = [f"{p}<br>({ph}, n={n})" for p, ph, n in zip(sp["period"], sp["phase"], sp["n_obs"])]
    flat = (sp["strategy_return"] == 0) & (sp["strategy_sharpe"] == 0)   # in cash the whole window: no Sharpe
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=sp["strategy_sharpe"].where(~flat), name="Strategy Sharpe", marker_color=C_STRAT))
    for xi in [xv for xv, f in zip(x, flat) if f]:
        fig.add_annotation(x=xi, y=0, text="strategy in cash<br>all window", showarrow=False, yshift=18,
                           xshift=-28, font=dict(size=11, color=C_STRAT))
    fig.add_trace(go.Bar(x=x, y=sp["buy_hold_sharpe"], name="SPY Sharpe", marker_color=C_BENCH))
    fig.update_layout(title="Sharpe During Major Stress Episodes", yaxis_title="Sharpe", barmode="group",
                      template="plotly_white", height=430, margin=dict(b=90))
    save("subperiod_sharpe", fig, "Strategy and buy-and-hold SPY Sharpe during major stress episodes, with the sample "
         "phase (training, test or before training) of each window.", [f"results/{PAIR}/subperiod_sharpe.csv"])
    save("walk_forward", fig, "Alias for the dashboard's standard walk-forward chart slot.",
         [f"results/{PAIR}/subperiod_sharpe.csv"])


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_monthly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    add_contraction_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df["hsn1f"], name="New home sales", line=dict(color=C_IND)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_TGT)), secondary_y=True)
    nber_legend(fig)
    contraction_legend(fig)
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="HSN1F (thousands, SAAR)", secondary_y=False)
    fig.update_yaxes(title_text="SPY", secondary_y=True)
    from harness.charts import zoom_dual_panel  # VIZ-V1: indicator and target in stacked panels
    fig = zoom_dual_panel(fig)
    save(f"history_zoom_{slug}", fig, f"{title}; gray bands are NBER recessions and pink bands mark new home sales "
         "below their year-earlier level.", [f"data/{PAIR}_monthly_latest.parquet"])


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
    chart_history_zoom("dotcom", "Dot-Com Bust: Home Sales Held Up While Equities Fell", "1999-01-31", "2003-12-31")
    chart_history_zoom("gfc", "Housing Bust and Financial Crisis: Home Sales Fell Years Before Equities",
                       "2004-01-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock: Brief Collapse and Fast Rebound in Home Sales", "2018-01-31", "2021-12-31")
    chart_history_zoom("inflation_2022", "2022 Rate-Hike Cycle: Home Sales Fell as Mortgage Rates Rose",
                       "2021-01-31", "2025-12-31")
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
