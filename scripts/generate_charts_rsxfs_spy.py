#!/usr/bin/env python3
"""Chart generation for advance retail sales ex food services (FRED RSXFS) x SPY (Phase B).

Captions carry no typed results: every number on a chart is read from the pipeline artifacts. The lead-plateau and
chance-check charts are written by the harness (scripts/harness/charts.py) during the pipeline run.
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
import chart_provenance  # noqa: E402  (records chart inputs; imported before any data is read)
from _nber import RECESSIONS, add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart  # noqa: E402

PAIR = "rsxfs_spy"
DATE_TAG = "20261018"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
PANEL = "data/rsxfs_spy_monthly_latest.parquet"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)
SCRIPT = "scripts/generate_charts_rsxfs_spy.py"
FACTS = RES / f"evidence_facts_{DATE_TAG}.json"

C_IND = "#D55E00"
C_TGT = "#0072B2"
C_STRAT = "#009E73"
C_BENCH = "#6C7A89"
C_LINE = "#4D4D4D"
FALL_FILL = "rgba(204,121,167,0.22)"
SIGNAL_LABEL = {"rsxfs_yoy": "YoY growth", "rsxfs_mom": "1-month growth",
                "rsxfs_3m": "3-month growth", "rsxfs_6m": "6-month growth",
                "rsxfs_yoy_zscore_60m": "YoY growth z-score (60m)",
                "rsxfs_accel": "Change in YoY growth"}
YOY = "rsxfs_yoy"
FALL_LABEL = "Retail sales below year-earlier level"
SPY_LOG_TICKS = [25, 50, 100, 200, 400, 800]   # readable major ticks on the log price axis


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def alpha() -> float:
    """Significance level of the evidence stage (pipeline SIGNIFICANCE_P, recorded in evidence_facts)."""
    return float(json.loads(FACTS.read_text())["derived"]["significance_p"])


def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / PANEL)


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    chart_provenance.record(PAIR, OUT / f"{name}.json", sources, SCRIPT)
    try:
        fig.write_image(OUT / f"_perceptual_check_{name}.png", width=1200, height=600, scale=1)
    except Exception as exc:  # noqa: BLE001 - PNG is a secondary perceptual-check artifact
        print(f"  (perceptual PNG skipped for {name}: {exc.__class__.__name__})")
    meta = {"chart_name": name, "pair_id": PAIR, "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": SCRIPT, "caption": caption, "narrative_alignment_note": caption,
            "disposition": "consumed", "source_artifacts": sources}
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  wrote {name}.json")


def legend_square(fig: go.Figure, color: str, name: str) -> None:
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=12, color=color, symbol="square"),
                             name=name, hoverinfo="skip"))


def add_fall_shading(fig: go.Figure, df: pd.DataFrame) -> None:
    """Months when retail sales were below their year-earlier level (YoY growth < 0)."""
    fall = df[YOY].fillna(0) < 0
    starts = fall.index[fall & ~fall.shift(1, fill_value=False)]
    ends = fall.index[fall & ~fall.shift(-1, fill_value=False)]
    for start, end in zip(starts, ends):
        # add_shape with xref/yref paper: add_vrect silently adds nothing on make_subplots(secondary_y) figures
        # each band covers the whole reading month (previous month-end to month-end), so single months show
        x0 = start - pd.offsets.MonthEnd(1)
        fig.add_shape(type="rect", xref="x", yref="paper", x0=x0.strftime("%Y-%m-%d"), x1=end.strftime("%Y-%m-%d"),
                      y0=0, y1=1, fillcolor=FALL_FILL, line_width=0, layer="below")


def chart_hero() -> None:
    df = load_monthly()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    add_fall_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df[YOY], name="Retail sales ex food services, YoY growth (revised)",
                             line=dict(color=C_IND, width=2),
                             hovertemplate="%{x|%Y-%m}<br>Retail sales YoY: %{y:.1f}%<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY price (log scale)", line=dict(color=C_TGT, width=1.6),
                             hovertemplate="%{x|%Y-%m}<br>SPY: %{y:.2f}<extra></extra>"), secondary_y=True)
    legend_square(fig, "rgba(150,120,120,0.35)", "NBER recession period")
    legend_square(fig, "rgba(204,121,167,0.28)", FALL_LABEL)
    fig.update_layout(title="Retail Sales Growth vs SPY", template="plotly_white", height=520,
                      hovermode="x unified", legend=dict(orientation="v", x=1.07, y=1), margin=dict(r=260))
    fig.update_yaxes(title_text="Retail sales, year-over-year growth (%)", zeroline=True, zerolinecolor=C_LINE,
                     secondary_y=False)
    fig.update_yaxes(title_text="SPY price (USD, log scale)", type="log", tickvals=SPY_LOG_TICKS, showgrid=False,
                     secondary_y=True)
    save("hero", fig, "Year-over-year growth in retail sales ex food services (RSXFS, revised) and SPY with NBER "
         "recessions; pink bands mark months when retail sales were below their year-earlier level.", [PANEL])


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>Weakest YoY growth", "Q2", "Q3", "Q4<br>Strongest YoY growth"]
    fig = make_dual_panel_regime_chart(
        labels, q["sharpe"].astype(float).tolist(), (q["mean_return"].astype(float) * 12 * 100).tolist(),
        signal_label="Retail sales YoY growth", x_axis_title="Quartile of YoY growth in retail sales ex food services",
        axis_noun="", sample_sizes=q["n"].astype(int).tolist())
    fig.update_layout(title=dict(text="SPY Returns by Retail Sales Growth Regime", y=0.98),
                      margin=dict(t=150))
    save("regime_stats", fig, "Same-month SPY performance across quartiles of YoY growth in retail sales ex food "
         "services.",
         [rel(RES / "regime_quartile_returns.csv")])


def chart_correlation_heatmap() -> None:
    corr = pd.read_csv(CORE / "correlations.csv")
    sub = corr[corr["metric"] == "pearson"].copy()
    sub["signal"] = sub["pair_name"].str.replace(r"_to_spy_fwd_\d+m", "", regex=True).map(SIGNAL_LABEL)
    sub["h"] = sub["pair_name"].str.extract(r"fwd_(\d+)m")[0].astype(int)
    a = alpha()
    sub["star"] = np.where(sub["p_value"] < a, "*", "")
    piv = sub.pivot_table(index="signal", columns="h", values="value", aggfunc="first").sort_index(axis=1)
    star = sub.pivot_table(index="signal", columns="h", values="star", aggfunc="first").reindex_like(piv)
    text = [[f"{v:.2f}{s}" for v, s in zip(rv, rs)] for rv, rs in zip(piv.values, star.values)]
    fig = go.Figure(go.Heatmap(z=piv.values, x=[f"{h}m" for h in piv.columns], y=piv.index, colorscale="RdBu",
                               zmid=0, text=text, texttemplate="%{text}", colorbar=dict(title="r")))
    fig.update_layout(title="Correlation: Retail Sales Signals vs Forward SPY Returns",
                      template="plotly_white",
                      height=520, xaxis_title="Forward SPY return horizon",
                      annotations=[dict(text=f"* HAC (Newey-West) p < {a}, lags at least horizon - 1", xref="paper",
                                        yref="paper", x=0, y=-0.16, showarrow=False, font=dict(size=11))],
                      margin=dict(l=190, b=110))
    save("correlation_heatmap", fig, "Pearson correlations between retail sales growth transforms and forward SPY "
         "returns; stars mark HAC p-values below the significance level.", [rel(CORE / "correlations.csv"), rel(FACTS)])


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"], C_IND, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="CCF"))
    fig.add_hline(y=ccf["upper_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=ccf["lower_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Cross-Correlation: Monthly Change in Retail Sales YoY Growth vs SPY Return",
                      xaxis_title="Lag in months (positive = retail sales growth moves first)", yaxis_title="Correlation",
                      template="plotly_white", height=430)
    save("ccf_prewhitened", fig, "Cross-correlation between the monthly change in YoY retail sales growth and SPY "
         "returns; dashed lines are approximate 95% bands.", [rel(CORE / "ccf_prewhitened.csv")])


def chart_granger() -> None:
    gr = pd.read_csv(CORE / "granger_causality.csv")
    k, a = len(gr), alpha()
    fig = go.Figure(go.Bar(x=gr["lag"], y=gr["p_value"], name="p-value (unadjusted)", marker_color=C_IND))
    fig.add_hline(y=a, line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=a / k, line_dash="dot", line_color=C_LINE)
    for y, txt, shift in ((a, f"p = {a}", 6), (a / k, f"Bonferroni: {a} / {k} lags", -6)):
        fig.add_annotation(x=1.01, xref="paper", xanchor="left", y=y, yref="y", yshift=shift, text=txt,
                           showarrow=False, font=dict(size=11))
    fig.update_layout(title="Granger Causality: Does Retail Sales YoY Growth Help Forecast SPY?",
                      xaxis_title="Lag (months)", yaxis_title="p-value (unadjusted)", template="plotly_white",
                      height=430, margin=dict(r=190), xaxis=dict(tickmode="linear", dtick=1))
    save("granger_f_by_lag", fig, "Granger p-values by lag for YoY growth in retail sales ex food services predicting "
         "SPY returns, with the significance line and the Bonferroni line for the number of lags tried.",
         [rel(CORE / "granger_causality.csv"), rel(FACTS)])


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = go.Figure(go.Bar(x=lp["horizon"].astype(str) + "m", y=lp["coef"], marker_color=C_IND,
                           name="Coefficient (95% HAC CI)",
                           error_y=dict(type="data", symmetric=False, array=lp["ci_upper"] - lp["coef"],
                                        arrayminus=lp["coef"] - lp["ci_lower"], thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Local Projection: Forward SPY Return per Point of Retail Sales YoY Growth",
                      xaxis_title="Forward horizon", yaxis_title="Coefficient (95% HAC CI whiskers)",
                      template="plotly_white", height=430)
    save("local_projections", fig, "Estimated forward SPY return per percentage point of YoY growth in retail sales "
         "ex food services, with Newey-West 95% intervals (lags at least horizon - 1).", [rel(CORE / "local_projections.csv")])


def chart_quantile() -> None:
    q = pd.read_csv(CORE / "quantile_regression.csv")
    qt = json.loads((CORE / "quantile_equality_test.json").read_text())
    fig = go.Figure(go.Scatter(x=q["quantile"], y=q["coef"], mode="lines+markers", name="Coefficient (95% CI)",
                               line=dict(color=C_IND),
                               error_y=dict(type="data", symmetric=False, array=q["ci_upper"] - q["coef"],
                                            arrayminus=q["coef"] - q["ci_lower"], thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    verdict = ("slopes differ across quantiles" if qt["reject_equality"] else
               "equal slopes across quantiles not rejected")
    fig.add_annotation(text=f"Cross-quantile slope equality, {qt['method']}: p={qt['p_value']:.3f}, {verdict}",
                       xref="paper", yref="paper", x=0, y=1.14, showarrow=False, font=dict(size=11), align="left")
    fig.update_layout(margin=dict(t=110), title=dict(text="Quantile Regression Coefficient", y=0.97),
                      xaxis_title="Quantile of the 3-month forward SPY return",
                      yaxis_title="Retail sales YoY growth coefficient (95% CI)", template="plotly_white", height=430)
    save("quantile_coef", fig, "Coefficient of YoY growth in retail sales ex food services across quantiles of the "
         "3-month forward SPY return; whiskers are moving-block bootstrap 95% intervals.",
         [rel(CORE / "quantile_regression.csv"), rel(CORE / "quantile_equality_test.json")])


def chart_equity_drawdown() -> None:
    src = RES / f"strategy_returns_{DATE_TAG}.csv"
    full = pd.read_csv(src, parse_dates=["date"]).set_index("date")
    # from the first training month: before it the real-time rule has no published vintage (no position at all)
    strat = full.loc[full.index[full["sample"] == "IS"][0]:].copy()
    strat["strategy_equity"] = (1 + strat["strategy_return"]).cumprod()
    strat["benchmark_equity"] = (1 + strat["benchmark_return"]).cumprod()
    oos0 = strat.index[strat["sample"] == "OOS"][0].strftime("%Y-%m-%d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat.index, y=strat["strategy_equity"], name="Winner strategy (as known at the time)",
                             line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=strat.index, y=strat["benchmark_equity"], name="Buy-and-hold SPY",
                             line=dict(color=C_BENCH, width=2, dash="dash")))
    fig.add_shape(type="line", xref="x", yref="paper", x0=oos0, x1=oos0, y0=0, y1=1,
                  line=dict(color=C_LINE, dash="dot"))
    fig.add_annotation(x=oos0, y=1.02, xref="x", yref="paper", text="test period starts", showarrow=False,
                       font=dict(size=11))
    fig.update_layout(title="Equity Curve: Retail Sales Strategy vs SPY", yaxis_title="Growth of $1",
                      template="plotly_white", height=460)
    save("equity_curves", fig, "Winner strategy (as known at the time: real-time RSXFS vintages) equity curve "
         "compared with buy-and-hold SPY, both from the first training month; the dotted line marks the start of the "
         "test period.", [rel(src)])

    dd = pd.DataFrame(index=strat.index)
    dd["strategy"] = strat["strategy_equity"] / strat["strategy_equity"].cummax() - 1
    dd["benchmark"] = strat["benchmark_equity"] / strat["benchmark_equity"].cummax() - 1
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["strategy"] * 100, name="Winner strategy",
                              line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["benchmark"] * 100, name="Buy-and-hold SPY",
                              line=dict(color=C_BENCH, width=2, dash="dash")))
    fig2.update_layout(title="Drawdown Comparison", yaxis_title="Drawdown (%)", template="plotly_white", height=430)
    save("drawdown", fig2, "Drawdown comparison for the winner strategy (as known at the time) and SPY buy-and-hold, "
         "both from the first training month.",
         [rel(src)])


def chart_tournament() -> None:
    src = RES / f"tournament_results_{DATE_TAG}.csv"
    t = pd.read_csv(src)
    valid = t[(t["valid"].astype(bool)) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure(go.Box(x=valid["lead_months"].astype(int), y=valid["oos_sharpe"], name="Valid strategies",
                           marker_color=C_IND))
    fig.update_layout(title="Tournament Test-Period Sharpe Distribution by Lead", xaxis_title="Lead (months)",
                      yaxis_title="Test-period Sharpe", template="plotly_white", height=450,
                      xaxis=dict(tickmode="linear", dtick=1))
    cap = ("Distribution of test-period Sharpe across valid tournament strategies by lead (as known at the time; "
           "the winner is chosen on training data, not on this score).")
    save("tournament_sharpe_dist", fig, cap, [rel(src)])
    save("tournament_scatter", fig, cap, [rel(src)])


def chart_rolling_correlation() -> None:
    src = RES / f"rolling_correlation_{PAIR}.csv"
    rc = pd.read_csv(src, parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=rc["date"], y=rc["rolling_corr"], name="60-month rolling correlation",
                               line=dict(color=C_IND)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Rolling Correlation: Retail Sales YoY Growth vs SPY Return", yaxis_title="Correlation",
                      template="plotly_white", height=430)
    save("rolling_correlation", fig, "Rolling 60-month correlation between YoY growth in retail sales ex food services "
         "and SPY monthly returns.", [rel(src)])


def chart_structural_break() -> None:
    src = RES / f"structural_break_{PAIR}.json"
    sb = json.loads(src.read_text())
    fig = go.Figure(go.Indicator(mode="number", value=sb["max_abs_z"],
                                 title={"text": "Largest absolute z-score of the rolling correlation"}))
    fig.update_layout(title="Stability Proxy (not a formal break test)", template="plotly_white", height=360)
    save("structural_break", fig, "Proxy check for large swings in the retail sales growth-SPY correlation.", [rel(src)])


def chart_subperiod() -> None:
    src = RES / "subperiod_sharpe.csv"
    sp = pd.read_csv(src)
    def phase(r) -> str:
        if r["n_is"] == r["n_obs"]:
            return "training"
        if r["n_oos"] == r["n_obs"]:
            return "test"
        return "mixed"
    x = [f"{r['period']} ({phase(r)}, n={r['n_obs']})" for _, r in sp.iterrows()]
    fig = go.Figure()
    for col, nm, c in (("strategy_sharpe", "Strategy Sharpe", C_STRAT), ("buy_hold_sharpe", "SPY Sharpe", C_BENCH)):
        fig.add_trace(go.Bar(x=x, y=sp[col], name=nm, marker_color=c, text=sp[col], texttemplate="%{text:.2f}",
                             textposition="outside", cliponaxis=False))
    fig.update_layout(title="Sharpe During Major Stress Episodes (annualized; n = months)", yaxis_title="Sharpe",
                      barmode="group", template="plotly_white", height=410)
    cap = ("Strategy and buy-and-hold SPY Sharpe during major stress episodes; each label says whether the window "
           "falls in the training or test period, and n is the number of monthly returns.")
    save("subperiod_sharpe", fig, cap, [rel(src)])
    save("walk_forward", fig, cap, [rel(src)])


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_monthly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    add_fall_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df[YOY], name="Retail sales ex food services, YoY growth",
                             line=dict(color=C_IND)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY price", line=dict(color=C_TGT)), secondary_y=True)
    if any(pd.Timestamp(r0) <= pd.Timestamp(end) and pd.Timestamp(r1) >= pd.Timestamp(start) for r0, r1 in RECESSIONS):
        legend_square(fig, "rgba(150,120,120,0.35)", "NBER recession period")
    legend_square(fig, "rgba(204,121,167,0.28)", FALL_LABEL)
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="Retail sales YoY (%)", zeroline=True, zerolinecolor=C_LINE, secondary_y=False)
    fig.update_yaxes(title_text="SPY (USD)", secondary_y=True)
    from harness.charts import zoom_dual_panel  # VIZ-V1: indicator and target in stacked panels
    fig = zoom_dual_panel(fig)
    save(f"history_zoom_{slug}", fig, f"{title}: YoY growth in retail sales ex food services and SPY; gray bands are NBER "
         "recessions and pink bands mark months when retail sales were below their year-earlier level.", [PANEL])


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
    chart_history_zoom("dotcom", "Dot-Com Bust, 1999-2003", "1999-01-31", "2003-12-31")
    chart_history_zoom("gfc", "Global Financial Crisis, 2006-2010", "2006-01-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock, 2018-2021", "2018-01-31", "2021-12-31")
    chart_history_zoom("inflation_2022", "2022 Inflation and Rate Shock, 2021-2025", "2021-01-31", "2025-12-31")
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
