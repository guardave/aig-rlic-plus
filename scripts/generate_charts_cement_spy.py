#!/usr/bin/env python3
"""Chart generation for Portland cement shipments (Texas through 2023-12, then the U.S. portland-only MIS Table 2a
total) x SPY (Phase B, single track: today's revised values, no archive).

Presentational layer only: every series and every number in a title or caption is read from the pipeline artifacts
(results/cement_spy, data/cement_spy_monthly_latest.parquet). The lead plateau and chance-check charts are written by
the harness (scripts/harness/charts.py) during the pipeline run. The shipment column has a basis break at the month
recorded in data_integrity_<tag>.json (equal to the Texas total before it); charts that span it mark it.
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
from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart  # noqa: E402

PAIR = "cement_spy"
DATE_TAG = "20261020"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)
PANEL = "data/cement_spy_monthly_latest.parquet"
INTEGRITY = f"results/{PAIR}/data_integrity_{DATE_TAG}.json"

C_IND = "#D55E00"
C_TGT = "#0072B2"
C_STRAT = "#009E73"
C_BENCH = "#6C7A89"
C_LINE = "#4D4D4D"
C_BREAK = "#CC79A7"
SIGNAL_LABEL = {"cement_yoy": "YoY", "cement_mom": "MoM", "cement_3m": "3-month", "cement_6m": "6-month",
                "cement_yoy_zscore_60m": "YoY z-score (60m)", "cement_accel": "YoY acceleration"}


def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / PANEL)


def integrity() -> dict:
    return json.loads((REPO / INTEGRITY).read_text())


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    chart_provenance.record(PAIR, OUT / f"{name}.json", sources, "scripts/generate_charts_cement_spy.py")
    try:
        fig.write_image(OUT / f"_perceptual_check_{name}.png", width=1200, height=600, scale=1)
    except Exception as exc:  # noqa: BLE001 - PNG is a secondary perceptual-check artifact
        print(f"  (perceptual PNG skipped for {name}: {exc.__class__.__name__})")
    meta = {"chart_name": name, "pair_id": PAIR, "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "scripts/generate_charts_cement_spy.py", "caption": caption,
            "narrative_alignment_note": caption, "disposition": "consumed", "source_artifacts": sources}
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  wrote {name}.json")


def nber_legend(fig: go.Figure) -> None:
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="NBER recession period", hoverinfo="skip",
                             marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square")))


def mark_break(fig: go.Figure, start=None, end=None) -> None:
    """Dotted vertical line at the first month of the shipment column's basis break (paper y-range, so it works on
    secondary-y and stacked panels), with a legend entry."""
    b = (pd.Timestamp(integrity()["first_month_not_equal"]) + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
    if (start is not None and b < start) or (end is not None and b > end):
        return
    fig.add_shape(type="line", x0=b, x1=b, xref="x", yref="paper", y0=0, y1=1,
                  line=dict(color=C_BREAK, width=2, dash="dot"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Coverage change: Texas to U.S. portland-only",
                             line=dict(color=C_BREAK, width=2, dash="dot"), hoverinfo="skip"))


def chart_hero() -> None:
    df = load_monthly()
    it = integrity()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    fig.add_trace(go.Scatter(x=df.index, y=df["cement"], name="Cement shipments (Texas, then U.S. portland-only)",
                             line=dict(color=C_IND, width=2),
                             hovertemplate="%{x|%Y-%m}<br>Shipments: %{y:,.0f}<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY price", line=dict(color=C_TGT, width=1.6),
                             hovertemplate="%{x|%Y-%m}<br>SPY: %{y:.2f}<extra></extra>"), secondary_y=True)
    nber_legend(fig)
    mark_break(fig)
    fig.update_layout(title="Portland Cement Shipments (Texas, then U.S. Portland-Only; USGS) vs SPY", template="plotly_white",
                      height=520, hovermode="x unified", legend=dict(orientation="v", x=1.08, y=1), margin=dict(r=260))
    fig.update_yaxes(title_text="Shipments (metric tons)", secondary_y=False)
    fig.update_yaxes(title_text="SPY price", secondary_y=True)
    save("hero", fig, (f"Shipment level and SPY with NBER recession bands. Through {it['last_month_equal_texas_total']} "
                       f"the series is Texas Portland cement shipments; the dotted line marks "
                       f"{it['first_month_not_equal']}, where it changes to the U.S. portland-only total (USGS MIS "
                       "Table 2a)."), [PANEL, INTEGRITY])


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>Weakest growth", "Q2", "Q3", "Q4<br>Strongest growth"]
    fig = make_dual_panel_regime_chart(
        labels, q["sharpe"].astype(float).tolist(), (q["mean_return"].astype(float) * 12 * 100).tolist(),
        signal_label="Cement YoY growth", x_axis_title="Cement YoY growth quartile", axis_noun="",
        sample_sizes=q["n"].astype(int).tolist())
    fig.update_layout(title="SPY Returns in the Same Month by Cement-Growth Quartile")
    save("regime_stats", fig, "SPY Sharpe and annualized return in the same month, by quartile of year-over-year "
                              "cement shipment growth (concurrent, descriptive).",
         [f"results/{PAIR}/regime_quartile_returns.csv"])


def chart_correlation_heatmap() -> None:
    c = pd.read_csv(CORE / "correlations.csv")
    piv = c.pivot_table(index="signal", columns="horizon_months", values="correlation", aggfunc="first")
    pv = c.pivot_table(index="signal", columns="horizon_months", values="p_value", aggfunc="first")
    order = [s for s in SIGNAL_LABEL if s in piv.index]
    piv, pv = piv.loc[order], pv.loc[order]
    text = [[f"{v:.2f}{'*' if p < 0.05 else ''}" for v, p in zip(rv, rp)] for rv, rp in zip(piv.values, pv.values)]
    fig = go.Figure(go.Heatmap(z=piv.values, x=[f"{h}m" for h in piv.columns], y=[SIGNAL_LABEL[s] for s in order],
                               colorscale="RdBu", zmid=0, text=text, texttemplate="%{text}", colorbar=dict(title="r")))
    fig.update_layout(title="Correlation: Cement Growth Signals vs Forward SPY Returns", template="plotly_white",
                      height=520, xaxis_title="Forward SPY return horizon")
    save("correlation_heatmap", fig, "Pearson correlations of each cement growth transform with forward SPY returns; "
                                     "* marks a HAC p-value below 0.05 (lags at least horizon - 1).",
         [f"results/{PAIR}/core_models_{DATE_TAG}/correlations.csv"])


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"].astype(bool), C_IND, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="Cross-correlation"))
    fig.add_hline(y=ccf["upper_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="95% band", line=dict(color=C_LINE, dash="dash"),
                             hoverinfo="skip"))
    fig.add_hline(y=ccf["lower_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Cross-Correlation: Change in Cement YoY Growth vs SPY Return",
                      xaxis_title="Lag (months): positive = cement leads, negative = SPY leads",
                      yaxis_title="Correlation", template="plotly_white", height=430)
    save("ccf_prewhitened", fig, "Cross-correlation of the monthly change in year-over-year cement growth (first "
                                 "difference) with SPY returns; dashed lines are the 95% band.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/ccf_prewhitened.csv"])


def chart_granger() -> None:
    gr = pd.read_csv(CORE / "granger_causality.csv")
    fig = go.Figure()
    for d, lab, col in (("cement_to_SPY", "Cement growth -> SPY", C_IND), ("SPY_to_cement", "SPY -> cement growth",
                                                                           C_TGT)):
        s = gr[gr["direction"] == d]
        fig.add_trace(go.Bar(x=s["lag"], y=s["p_value"], name=lab, marker_color=col))
    fig.add_hline(y=0.05, line_dash="dash", line_color=C_LINE)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="p = 0.05 (one lag, unadjusted)",
                             line=dict(color=C_LINE, dash="dash"), hoverinfo="skip"))
    fig.update_layout(title="Granger Causality p-values by Lag (both directions)", xaxis_title="Lag (months)",
                      yaxis_title="p-value", barmode="group", template="plotly_white", height=430)
    save("granger_f_by_lag", fig, "Granger p-values by lag for year-over-year cement growth and SPY returns, both "
                                  "directions; the lags are tried one by one, so a single p below 0.05 is not "
                                  "adjusted for the number of lags.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/granger_causality.csv"])


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    scale = 1000.0   # percentage points of forward return per 10 points of YoY growth: coef * 10 * 100
    fig = go.Figure(go.Bar(x=lp["horizon"].astype(str) + "m", y=lp["coef"] * scale, marker_color=C_IND,
                           name="Coefficient (95% HAC CI)",
                           error_y=dict(type="data", array=1.96 * lp["se"] * scale, visible=True, thickness=1.5,
                                        color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Local Projections: Forward SPY Return per 10 Points of Cement YoY Growth",
                      xaxis_title="Forward horizon", yaxis_title="Percentage points (95% HAC whiskers)",
                      template="plotly_white", height=430)
    save("local_projections", fig, "Slope of the forward SPY return on year-over-year cement growth by horizon; "
                                   "whiskers are 95% HAC (Newey-West) intervals with lags at least horizon - 1.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/local_projections.csv"])


def chart_quantile() -> None:
    q = pd.read_csv(CORE / "quantile_regression.csv")
    t = json.loads((CORE / "quantile_equality_test.json").read_text())
    scale = 1000.0
    fig = go.Figure(go.Scatter(x=q["quantile"], y=q["coef"] * scale, mode="lines+markers",
                               name="Coefficient (95% block-bootstrap CI)", line=dict(color=C_IND),
                               error_y=dict(type="data", symmetric=False,
                                            array=(q["ci_high"] - q["coef"]).clip(lower=0) * scale,
                                            arrayminus=(q["coef"] - q["ci_low"]).clip(lower=0) * scale,
                                            visible=True, thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.add_annotation(text=f"Equal-slopes Wald test (block bootstrap): p = {t['p_value']:.2f}", xref="paper",
                       yref="paper", x=0, y=1.12, showarrow=False, font=dict(size=12), align="left")
    fig.update_layout(margin=dict(t=110), title=dict(text="Quantile Regression: 3-Month SPY Return on Cement YoY "
                                                          "Growth", y=0.97),
                      xaxis_title="SPY 3-month return quantile",
                      yaxis_title="Percentage points per 10 points of YoY growth", template="plotly_white", height=450)
    save("quantile_coef", fig, "Quantile-regression slope of the 3-month forward SPY return on year-over-year cement "
                               "growth at each return quantile; intervals and the equal-slopes test use a moving-block "
                               "bootstrap because the 3-month returns overlap.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv",
          f"results/{PAIR}/core_models_{DATE_TAG}/quantile_equality_test.json"])


def _strategy() -> pd.DataFrame:
    s = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    return s[s["sample"] != "pre_IS"]


def chart_equity_drawdown() -> None:
    s = _strategy()
    oos0 = s.index[s["sample"] == "OOS"][0].strftime("%Y-%m-%d")
    eq_s = (1 + s["strategy_return"]).cumprod()
    eq_b = (1 + s["benchmark_return"]).cumprod()
    src = [f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv", INTEGRITY]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=eq_s, name="Winner rule (as revised today)", line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=s.index, y=eq_b, name="Buy-and-hold SPY", line=dict(color=C_BENCH, width=2, dash="dash")))
    fig.add_shape(type="line", x0=oos0, x1=oos0, xref="x", yref="paper", y0=0, y1=1, line=dict(color=C_LINE, dash="dash"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Test period starts",
                             line=dict(color=C_LINE, dash="dash")))
    mark_break(fig)
    fig.update_layout(title="Growth of $1: Cement Rule vs Buy-and-Hold SPY (from the training start)",
                      yaxis_title="Growth of $1", template="plotly_white", height=460,
                      legend=dict(orientation="v", x=1.02, y=1), margin=dict(r=260))
    save("equity_curves", fig, "Winner rule (single track: today's revised cement values with release-date timing) "
                               "against buy-and-hold SPY from the training start; dashed line = test-period start.", src)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=s.index, y=(eq_s / eq_s.cummax() - 1) * 100, name="Winner rule",
                              line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=s.index, y=(eq_b / eq_b.cummax() - 1) * 100, name="Buy-and-hold SPY",
                              line=dict(color=C_BENCH, width=2, dash="dash")))
    fig2.add_shape(type="line", x0=oos0, x1=oos0, xref="x", yref="paper", y0=0, y1=1, line=dict(color=C_LINE, dash="dash"))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Test period starts",
                              line=dict(color=C_LINE, dash="dash")))
    fig2.update_layout(title="Drawdown: Cement Rule vs Buy-and-Hold SPY", yaxis_title="Drawdown (%)",
                       template="plotly_white", height=430, legend=dict(orientation="v", x=1.02, y=1),
                       margin=dict(r=220))
    save("drawdown", fig2, "Drawdown of the winner rule and of buy-and-hold SPY from the training start.", src)


def chart_tournament() -> None:
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    v = t[t["valid"].astype(bool)]
    src = [f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"]
    fig = go.Figure(go.Box(x=v["lead_months"].astype(str), y=v["oos_sharpe"], name="Valid rules", marker_color=C_IND))
    fig.update_layout(title="Test-Period Sharpe of Valid Rules by Lead", xaxis_title="Lead (months)",
                      yaxis_title="Test-period Sharpe", template="plotly_white", height=450)
    save("tournament_sharpe_dist", fig, "Test-period Sharpe of the valid rules by lead (the winner is chosen on "
                                        "training data, not on this score).", src)
    w = v[v["selected"].astype(bool)]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=v["is_sharpe"], y=v["oos_sharpe"], mode="markers", name="Valid rules",
                              marker=dict(color=C_BENCH, size=6, opacity=0.6)))
    fig2.add_trace(go.Scatter(x=w["is_sharpe"], y=w["oos_sharpe"], mode="markers", name="Selected winner",
                              marker=dict(color=C_STRAT, size=14, symbol="diamond")))
    fig2.update_layout(title="Training vs Test-Period Sharpe of Valid Rules", xaxis_title="Training (in-sample) Sharpe",
                       yaxis_title="Test-period Sharpe", template="plotly_white", height=450)
    save("tournament_scatter", fig2, "Training versus test-period Sharpe of every valid rule; the winner is chosen on "
                                     "training data by the stable-lead-range rule.", src)


def chart_rolling_correlation() -> None:
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=rc["date"], y=rc["rolling_corr"], name="60-month rolling correlation",
                               line=dict(color=C_IND)))
    fig.add_hline(y=0, line_color=C_LINE)
    mark_break(fig)
    fig.update_layout(title="Rolling 60-Month Correlation: Cement YoY Growth vs SPY Return", yaxis_title="Correlation",
                      template="plotly_white", height=430, legend=dict(orientation="v", x=1.02, y=1),
                      margin=dict(r=260))
    save("rolling_correlation", fig, "Rolling 60-month correlation between year-over-year cement growth and the SPY "
                                     "monthly return.", [f"results/{PAIR}/rolling_correlation_{PAIR}.csv", INTEGRITY])


def chart_structural_break() -> None:
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=rc["date"], y=rc["rolling_corr"], mode="lines", name="60-month rolling correlation",
                               line=dict(color=C_IND, width=1.5)))
    fig.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1)
    bp = sb["breakpoint_date"]
    fig.add_shape(type="line", x0=bp, x1=bp, xref="x", yref="paper", y0=0, y1=1,
                  line=dict(color=C_STRAT, width=2, dash="dot"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Most likely break date (sup-F)",
                             line=dict(color=C_STRAT, width=2, dash="dot")))
    fig.update_layout(title=f"Break Test (Quandt-Andrews sup-F {sb['sup_f']:.2f}, bootstrap p {sb['p_value']:.2f})",
                      xaxis_title="Date", yaxis_title="Rolling 60-month correlation", template="plotly_white",
                      height=420, legend=dict(orientation="v", x=1.02, y=1), margin=dict(r=240))
    save("structural_break", fig, (f"Quandt-Andrews sup-F test (15% trimming) for a break in the regression of the "
                                   f"SPY return on lagged year-over-year cement growth: most likely break "
                                   f"{sb['breakpoint_date'][:7]}, bootstrap p-value {sb['p_value']:.2f}."),
         [f"results/{PAIR}/structural_break_{PAIR}.json", f"results/{PAIR}/rolling_correlation_{PAIR}.csv"])


def chart_subperiod() -> None:
    sp = pd.read_csv(RES / "subperiod_sharpe.csv")
    lab = [f"{p}<br>({ph})" for p, ph in zip(sp["period"], sp["phase"])]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=lab, y=sp["strategy_sharpe"], name="Winner rule Sharpe", marker_color=C_STRAT))
    fig.add_trace(go.Bar(x=lab, y=sp["buy_hold_sharpe"], name="Buy-and-hold SPY Sharpe", marker_color=C_BENCH))
    fig.update_layout(title="Sharpe in Stress Episodes and the Full Test Period", yaxis_title="Sharpe",
                      barmode="group", template="plotly_white", height=430)
    save("subperiod_sharpe", fig, "Winner-rule and buy-and-hold Sharpe by episode; the label gives the episode's "
                                  "phase (before training, training or test).", [f"results/{PAIR}/subperiod_sharpe.csv"])


def chart_walk_forward() -> None:
    wf = pd.read_csv(RES / "walk_forward_calendar_year.csv")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=wf["year"].astype(str), y=wf["strategy_sharpe"], name="Winner rule", marker_color=C_STRAT))
    fig.add_trace(go.Bar(x=wf["year"].astype(str), y=wf["buy_hold_sharpe"], name="Buy-and-hold SPY",
                         marker_color=C_BENCH))
    fig.update_layout(title="Calendar-Year Sharpe in the Test Period (full years only)", xaxis_title="Year",
                      yaxis_title="Sharpe", barmode="group", template="plotly_white", height=430)
    save("walk_forward", fig, "Sharpe of the winner rule and of buy-and-hold SPY in each full calendar year of the "
                              "test period.", [f"results/{PAIR}/walk_forward_calendar_year.csv"])


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_monthly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    fig.add_trace(go.Scatter(x=df.index, y=df["cement_yoy"], name="Cement YoY growth (%)", line=dict(color=C_IND)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_TGT)), secondary_y=True)
    nber_legend(fig)
    mark_break(fig, start, end)
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="Cement YoY growth (%)", secondary_y=False)
    fig.update_yaxes(title_text="SPY", secondary_y=True)
    from harness.charts import zoom_dual_panel  # VIZ-V1: indicator and target in stacked panels
    fig = zoom_dual_panel(fig)
    save(f"history_zoom_{slug}", fig, f"{title}; gray bands are NBER recessions.", [PANEL, INTEGRITY])


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
    chart_walk_forward()
    chart_history_zoom("gfc", "Global Financial Crisis: Cement Shipments and SPY, 2006-2010", "2006-01-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock: Cement Shipments and SPY, 2018-2021", "2018-01-31", "2021-12-31")
    chart_history_zoom("inflation_2022", "2022 Rate Shock and After: Cement Shipments and SPY, 2021-2025 (coverage change marked)",
                       "2021-01-31", "2025-06-30")
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
