#!/usr/bin/env python3
"""Chart generation for SLOOS C&I net tightening (DRTSCILM) x SPY, quarterly (Phase B).

Reads data/sloos_ci_small_spy_quarterly_latest.parquet and results/sloos_ci_small_spy/* at DATE_TAG. Captions
carry no typed results: every number in a caption is read from the pipeline artifacts. The lead_plateau and
chance_check charts are written by the harness (scripts/harness/charts.py) during the pipeline run.
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

PAIR = "sloos_ci_small_spy"
DATE_TAG = "20261020"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)
PANEL = f"data/{PAIR}_quarterly_latest.parquet"
SCRIPT = f"scripts/generate_charts_{PAIR}.py"

# Okabe-Ito / Wong colorblind-safe palette
C_IND = "#D55E00"
C_TGT = "#0072B2"
C_STRAT = "#009E73"
C_HIND = "#E69F00"
C_BENCH = "#6C7A89"
C_LINE = "#4D4D4D"
C_TIGHT = "rgba(204,121,167,0.22)"
ROW_LABEL = {"sloos_level": "Level", "sloos_diff_1q": "1-quarter change", "sloos_chg_4q": "4-quarter change",
             "sloos_zscore_20q": "20-quarter z-score"}
EPISODE_LABEL = {"Dot_Com": "Dot-Com bust", "GFC": "GFC", "COVID": "COVID", "Rate_Hike_2022": "2022 rate hikes"}


def load_quarterly() -> pd.DataFrame:
    return pd.read_parquet(REPO / PANEL)


def winner() -> dict:
    return json.loads((RES / "winner_summary.json").read_text())


def save(name: str, fig: go.Figure, caption: str, sources: list[str]) -> None:
    fig.write_json(OUT / f"{name}.json")
    chart_provenance.record(PAIR, OUT / f"{name}.json", sources, SCRIPT)
    try:
        fig.write_image(OUT / f"_perceptual_check_{name}.png", width=1200, height=600, scale=1)
    except Exception as exc:  # noqa: BLE001 - the PNG is a secondary perceptual-check artifact
        print(f"  (perceptual PNG skipped for {name}: {exc.__class__.__name__})")
    meta = {"chart_name": name, "pair_id": PAIR, "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": SCRIPT, "caption": caption, "narrative_alignment_note": caption,
            "disposition": "consumed", "source_artifacts": sources}
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  wrote {name}.json")


def legend_square(fig: go.Figure, color: str, name: str) -> None:
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=name, hoverinfo="skip",
                             marker=dict(size=12, color=color, symbol="square")))


def add_tightening_shading(fig: go.Figure, df: pd.DataFrame) -> None:
    """Quarters in which more banks tightened than eased (net tightening above zero). add_shape with a paper
    y-range: add_vrect adds nothing on make_subplots(secondary_y) figures."""
    on = df["sloos"].fillna(0) > 0
    starts = on.index[on & ~on.shift(1, fill_value=False)]
    ends = on.index[on & ~on.shift(-1, fill_value=False)]
    for s, e in zip(starts, ends):
        x0 = (s - pd.offsets.QuarterEnd(1)).strftime("%Y-%m-%d")    # the survey quarter starts after the prior end
        fig.add_shape(type="rect", xref="x", yref="paper", x0=x0, x1=e.strftime("%Y-%m-%d"), y0=0, y1=1,
                      fillcolor=C_TIGHT, line_width=0, layer="below")


def chart_hero() -> None:
    df = load_quarterly()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    add_tightening_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df["sloos"], name="Net % of banks tightening (DRTSCILM)",
                             line=dict(color=C_IND, width=2),
                             hovertemplate="%{x|%Y-%m}<br>Net tightening: %{y:.1f}%<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY price", line=dict(color=C_TGT, width=1.6),
                             hovertemplate="%{x|%Y-%m}<br>SPY: %{y:.2f}<extra></extra>"), secondary_y=True)
    legend_square(fig, "rgba(150,120,120,0.35)", "NBER recession period")
    legend_square(fig, "rgba(204,121,167,0.45)", "More banks tightening than easing")
    fig.update_layout(title="Bank C&I Lending Standards (SLOOS) vs SPY", template="plotly_white", height=520,
                      hovermode="x unified", legend=dict(orientation="v", x=1.07, y=1), margin=dict(r=250))
    fig.update_yaxes(title_text="Net % of banks tightening", zeroline=True, zerolinecolor=C_LINE, secondary_y=False)
    fig.update_yaxes(title_text="SPY price", secondary_y=True)
    save("hero", fig, "Net share of banks tightening C&I standards (large and middle-market firms) and SPY, with "
         "NBER recessions (gray) and quarters with net tightening above zero (pink).", [PANEL])


def chart_regime_stats() -> None:
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>Fastest easing", "Q2", "Q3", "Q4<br>Fastest tightening"]
    fig = make_dual_panel_regime_chart(
        labels, q["sharpe"].astype(float).tolist(), (q["mean_return"].astype(float) * 4 * 100).tolist(),
        signal_label="4-quarter change in net tightening",
        x_axis_title="Quartile of the 4-quarter change in net tightening", axis_noun="",
        sample_sizes=q["n"].astype(int).tolist())
    fig.update_layout(title=dict(text="SPY Returns by Lending-Standards Regime", y=0.98), margin=dict(t=150))
    save("regime_stats", fig, "Same-quarter SPY performance across quartiles of the 4-quarter change in net "
         f"tightening: Sharpe {q['sharpe'].iloc[0]:.2f} in Q1 (fastest easing) and {q['sharpe'].iloc[3]:.2f} in Q4 "
         "(fastest tightening).", [f"results/{PAIR}/regime_quartile_returns.csv"])


def chart_correlation_heatmap() -> None:
    corr = pd.read_csv(CORE / "correlations.csv")
    sub = corr[corr["metric"] == "pearson"].copy()
    sub["signal"] = sub["pair_name"].str.replace(r"_to_spy_fwd_\d+q", "", regex=True)
    sub["horizon"] = sub["pair_name"].str.extract(r"fwd_(\d+)q")[0].astype(int)
    piv = sub.pivot_table(index="signal", columns="horizon", values="value", aggfunc="first").sort_index(axis=1)
    pv = sub.pivot_table(index="signal", columns="horizon", values="p_value", aggfunc="first").sort_index(axis=1)
    text = [[f"{r:.2f}<br>p={p:.2f}" for r, p in zip(rr, pp)] for rr, pp in zip(piv.values, pv.values)]
    fig = go.Figure(go.Heatmap(z=piv.values, x=[f"{h}q" for h in piv.columns], y=[ROW_LABEL.get(r, r) for r in piv.index], colorscale="RdBu",
                               zmid=0, zmin=-0.5, zmax=0.5, text=text, texttemplate="%{text}",
                               colorbar=dict(title="r")))
    fig.update_layout(title="Correlation: Lending-Standards Signals vs Forward SPY Returns", template="plotly_white",
                      height=560, margin=dict(b=130), xaxis_title="Forward SPY return horizon (quarters)")
    fig.add_annotation(text="p-values use HAC (Newey-West) errors with lags of at least h-1 for overlapping returns.",
                       xref="paper", yref="paper", x=0, y=0, yshift=-95, yanchor="top", showarrow=False,
                       xanchor="left", font=dict(size=10, color="#666666"))
    save("correlation_heatmap", fig, "Pearson correlations between the four net-tightening transforms and forward "
         f"SPY returns; largest |r| {sub['value'].abs().max():.2f}, smallest HAC p {sub['p_value'].min():.2f}.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/correlations.csv"])


def chart_ccf() -> None:
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = np.where(ccf["significant"], C_IND, C_BENCH)
    fig = go.Figure(go.Bar(x=ccf["lag"], y=ccf["ccf"], marker_color=colors, name="Cross-correlation"))
    fig.add_hline(y=ccf["upper_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.add_hline(y=ccf["lower_ci"].iloc[0], line_dash="dash", line_color=C_LINE)
    fig.update_layout(title="Pre-Whitened Cross-Correlation: Change in Net Tightening vs SPY Return",
                      xaxis_title="Offset in quarters (positive = the SLOOS change comes first)",
                      yaxis_title="Correlation", template="plotly_white", height=430, xaxis=dict(dtick=1))
    sig = ", ".join(str(int(x)) for x in ccf.loc[ccf["significant"], "lag"]) or "none"
    save("ccf_prewhitened", fig, "Cross-correlation of the 4-quarter change in net tightening with SPY returns after "
         f"AR({int(ccf['prewhiten_ar_order'].iloc[0])}) pre-whitening; offsets outside the 95% band: {sig}.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/ccf_prewhitened.csv"])


def chart_granger() -> None:
    gr = pd.read_csv(RES / "granger_by_lag.csv")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=gr["lag"], y=gr["p_value"], name="p-value at this lag", marker_color=C_IND))
    fig.add_trace(go.Scatter(x=gr["lag"], y=gr["p_holm"], name="Holm-adjusted p-value (4 lags)", mode="markers",
                             marker=dict(color=C_LINE, size=11, symbol="diamond")))
    fig.add_trace(go.Scatter(x=[gr["lag"].min() - 0.5, gr["lag"].max() + 0.5], y=[0.05, 0.05], mode="lines",
                             name="p = 0.05", line=dict(color=C_LINE, dash="dash")))   # in the legend, not on a bar
    fig.update_layout(title="Granger Causality: Does Net Tightening Help Forecast SPY?", xaxis_title="Lag (quarters)",
                      yaxis_title="p-value", yaxis=dict(range=[0, 1.05]), xaxis=dict(dtick=1), template="plotly_white", height=430,
                      legend=dict(orientation="h", y=-0.2))
    save("granger_f_by_lag", fig, "Granger p-values by quarterly lag for the 4-quarter change in net tightening "
         f"predicting SPY returns; smallest p {gr['p_value'].min():.2f} (Holm-adjusted {gr['p_holm'].min():.2f}).",
         [f"results/{PAIR}/granger_by_lag.csv"])


def chart_local_projections() -> None:
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = go.Figure(go.Bar(x=lp["horizon"].astype(str) + "q", y=lp["coef"] * 1000, marker_color=C_IND,
                           name="Coefficient (95% HAC interval)",
                           error_y=dict(type="data", array=(1.96 * lp["se"] * 1000).tolist(), visible=True,
                                        thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Local Projections: Forward SPY Return per 10-Point Rise in Tightening",
                      xaxis_title="Forward horizon (quarters)",
                      yaxis_title="SPY return (% per 10 points; 95% CI whiskers)", template="plotly_white", height=430)
    # coef = return (fraction) per 1 point of the 4-quarter change; shown in percent per 10 points (x 10 x 100)
    save("local_projections", fig, "Forward SPY return per 10-point rise in the 4-quarter change in net tightening "
         f"(HAC errors); p-values {', '.join(f'{p:.2f}' for p in lp['p_value'])} at horizons "
         f"{', '.join(str(h) for h in lp['horizon'])} quarters.",
         [f"results/{PAIR}/core_models_{DATE_TAG}/local_projections.csv"])


def chart_quantile() -> None:
    q = pd.read_csv(CORE / "quantile_regression.csv")
    qt = json.loads((CORE / "quantile_equality_test.json").read_text())
    fig = go.Figure(go.Scatter(x=q["quantile"], y=q["coef"] * 1000, mode="lines+markers",
                               name="Coefficient (95% CI)", line=dict(color=C_IND),
                               error_y=dict(type="data", array=(1.96 * q["se"] * 1000).tolist(), visible=True,
                                            thickness=1.5, color=C_LINE)))
    fig.add_hline(y=0, line_color=C_LINE)
    verdict = "rejected" if qt["reject_equality"] else "not rejected"
    fig.add_annotation(text=f"Equal slope across quantiles (bootstrap Wald): p = {qt['p_value']:.2f}, {verdict}",
                       xref="paper", yref="paper", x=0, y=1.12, showarrow=False, font=dict(size=11), align="left")
    fig.update_layout(margin=dict(t=110), title=dict(text="Quantile Regression: Next-Quarter SPY Return", y=0.97),
                      xaxis_title="SPY next-quarter return quantile",
                      yaxis_title="% per 10-point rise in tightening (95% CI)", template="plotly_white", height=430)
    save("quantile_coef", fig, "Slope of the next-quarter SPY return on the 4-quarter change in net tightening at "
         f"each return quantile; cross-quantile equality Wald p = {qt['p_value']:.2f} ({verdict}).",
         [f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv",
          f"results/{PAIR}/core_models_{DATE_TAG}/quantile_equality_test.json"])


def _from_is_start(sr: pd.DataFrame) -> pd.DataFrame:
    s = sr[sr["sample"].isin(["IS", "OOS"])].copy()
    s["strategy_equity"] = (1 + s["strategy_return"]).cumprod()
    s["benchmark_equity"] = (1 + s["benchmark_return"]).cumprod()
    return s


def chart_equity_drawdown() -> None:
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    s = _from_is_start(sr)
    oos0 = s.index[s["sample"] == "OOS"][0].strftime("%Y-%m-%d")   # a string: kaleido cannot encode a Timestamp
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s["strategy_equity"], name="Winner rule (as known at the time)",
                             line=dict(color=C_STRAT, width=2)))
    fig.add_trace(go.Scatter(x=s.index, y=s["benchmark_equity"], name="Buy-and-hold SPY",
                             line=dict(color=C_BENCH, width=2, dash="dash")))
    fig.add_vline(x=oos0, line_dash="dot", line_color=C_LINE)
    fig.add_annotation(x=oos0, y=1, yref="paper", text="test period starts", showarrow=False, xanchor="left",
                       yanchor="bottom", font=dict(size=11, color=C_LINE))
    fig.update_layout(title="Equity Curve: Lending-Standards Rule vs SPY (from the training start)",
                      yaxis_title="Growth of $1", template="plotly_white", height=460,
                      legend=dict(orientation="h", y=-0.15))
    save("equity_curves", fig, f"Growth of $1 from the training start ({s.index[0].date()}) for the winner rule on "
         f"data as known at the time and for buy-and-hold SPY; the test period starts {oos0}.",
         [f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv"])

    dd = pd.DataFrame({"strategy": s["strategy_equity"] / s["strategy_equity"].cummax() - 1,
                       "benchmark": s["benchmark_equity"] / s["benchmark_equity"].cummax() - 1})
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["strategy"] * 100, name="Winner rule", line=dict(color=C_STRAT, width=2)))
    fig2.add_trace(go.Scatter(x=dd.index, y=dd["benchmark"] * 100, name="Buy-and-hold SPY",
                              line=dict(color=C_BENCH, width=2, dash="dash")))
    fig2.add_vline(x=oos0, line_dash="dot", line_color=C_LINE)
    fig2.update_layout(title="Drawdown Comparison (from the training start)", yaxis_title="Drawdown (%)",
                       template="plotly_white", height=430, legend=dict(orientation="h", y=-0.15))
    save("drawdown", fig2, f"Drawdown from the running peak since {s.index[0].date()}: deepest "
         f"{dd['strategy'].min():.1%} for the rule and {dd['benchmark'].min():.1%} for buy-and-hold SPY (quarter-end "
         "data).", [f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv"])


def chart_tournament() -> None:
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    bh = float(winner()["bh_sharpe"])
    valid = t[(t["valid"]) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure(go.Box(x=valid["lead_quarters"].astype(str), y=valid["oos_sharpe"], name="Valid rules",
                           marker_color=C_IND, boxpoints="all", jitter=0.4, pointpos=0))
    leads = sorted(valid["lead_quarters"].astype(str).unique(), key=int)
    fig.add_trace(go.Scatter(x=leads, y=[bh] * len(leads), mode="lines", name=f"Buy-and-hold test Sharpe {bh:.2f}",
                             line=dict(color=C_BENCH, dash="dash")))
    fig.update_layout(title="Test-Period Sharpe of Every Valid Rule, by Lead", xaxis_title="Lead (quarters)",
                      yaxis_title="Test-period Sharpe", template="plotly_white", height=450,
                      legend=dict(orientation="h", y=-0.2))
    cap = (f"Test-period Sharpe of the {len(valid)} valid rules by lead (data as known at the time); median "
           f"{valid['oos_sharpe'].median():.2f} versus buy-and-hold {bh:.2f}. The winner is chosen on the training "
           "period, not on this score.")
    save("tournament_sharpe_dist", fig, cap, [f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                                              f"results/{PAIR}/winner_summary.json"])
    save("tournament_scatter", fig, cap, [f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                                          f"results/{PAIR}/winner_summary.json"])


def chart_rolling_correlation() -> None:
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=rc["date"], y=rc["rolling_corr"], name="20-quarter rolling correlation",
                               line=dict(color=C_IND)))
    fig.add_hline(y=0, line_color=C_LINE)
    fig.update_layout(title="Rolling 20-Quarter Correlation: Change in Net Tightening vs SPY Return",
                      yaxis_title="Correlation", template="plotly_white", height=430)
    save("rolling_correlation", fig, "Rolling 20-quarter correlation between the 4-quarter change in net tightening "
         f"and same-quarter SPY returns; range {rc['rolling_corr'].min():.2f} to {rc['rolling_corr'].max():.2f}.",
         [f"results/{PAIR}/rolling_correlation_{PAIR}.csv"])


def chart_structural_break() -> None:
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    fs = pd.read_csv(RES / f"structural_break_fseq_{PAIR}.csv", parse_dates=["date"])
    fig = go.Figure(go.Scatter(x=fs["date"], y=fs["f_stat"], name="Break F-statistic", line=dict(color=C_IND)))
    fig.add_trace(go.Scatter(x=[sb["breakpoint_date"]], y=[sb["statistic"]], mode="markers",
                             name=f"Largest F ({sb['breakpoint_date'][:7]})",
                             marker=dict(color=C_LINE, size=11, symbol="diamond")))
    fig.update_layout(title="Structural Break Test (Quandt-Andrews): SPY Return on Lagged Tightening Change",
                      yaxis_title="F-statistic for a break at this date", template="plotly_white", height=430,
                      legend=dict(orientation="h", y=-0.15))
    fig.add_annotation(text=f"Largest F = {sb['statistic']:.2f}; bootstrap p = {sb['p_value']:.2f} (no-break null)",
                       xref="paper", yref="paper", x=1, y=1.06, xanchor="right", showarrow=False,
                       font=dict(size=11, color=C_LINE))
    save("structural_break", fig, f"Sup-F {sb['statistic']:.2f} at {sb['breakpoint_date']}; bootstrap p = "
         f"{sb['p_value']:.2f} ({sb['p_value_method']}).",
         [f"results/{PAIR}/structural_break_{PAIR}.json", f"results/{PAIR}/structural_break_fseq_{PAIR}.csv"])


def chart_subperiod() -> None:
    sp = pd.read_csv(RES / "subperiod_sharpe.csv")
    x = [f"{EPISODE_LABEL.get(p, p)}<br>({n} quarters)" for p, n in zip(sp["period"], sp["n_quarters"])]

    def labels(ret: pd.Series, defined: pd.Series) -> list[str]:
        # a bar of exactly 0 is invisible: say what it is (cash all episode, or no data)
        return ["no real-time data" if d == 0 else ("in cash" if r == 0 else f"{r * 100:.1f}%")
                for r, d in zip(ret.fillna(0), defined)]
    fig = go.Figure()
    for col, name, color, ndef in (
            ("strategy_return", "Winner rule, as known at the time", C_STRAT, sp["n_main_defined"]),
            ("hindsight_return", "Hindsight winner (revised data)", C_HIND, sp["n_hindsight_defined"]),
            ("buy_hold_return", "Buy-and-hold SPY", C_BENCH, sp["n_quarters"])):
        fig.add_trace(go.Bar(x=x, y=sp[col].fillna(0) * 100, name=name, marker_color=color,
                             text=labels(sp[col], ndef), textposition="outside", textfont=dict(size=10),
                             cliponaxis=False))
    fig.add_hline(y=0, line_color=C_LINE)
    lo = float(min(sp[["strategy_return", "hindsight_return", "buy_hold_return"]].min().min(), 0)) * 100
    fig.update_layout(title="Cumulative Return During Major Stress Episodes", yaxis_title="Cumulative return (%)",
                      yaxis=dict(range=[lo * 1.25, max(8.0, -lo * 0.25)]), barmode="group", template="plotly_white",
                      height=560, margin=dict(b=150), legend=dict(orientation="h", y=-0.2))
    vin0 = winner()["tracks"]["main"]["sample"]["first_vintage"][:4]
    fig.add_annotation(text="Quarterly data: each episode holds only a few returns. The real-time archive starts in "
                            f"{vin0}, after the Dot-Com and GFC episodes.", xref="paper", yref="paper", x=0, y=-0.33,
                       showarrow=False, xanchor="left", font=dict(size=10, color="#666666"))
    cap = ("Cumulative return of the as-known-at-the-time winner, the hindsight winner and buy-and-hold SPY in four "
           "stress episodes; the real-time archive starts after the Dot-Com and GFC episodes.")
    src = [f"results/{PAIR}/subperiod_sharpe.csv", f"results/{PAIR}/winner_summary.json"]
    save("subperiod_sharpe", fig, cap, src)
    save("walk_forward", fig, cap, src)


def chart_history_zoom(slug: str, title: str, start: str, end: str) -> None:
    df = load_quarterly().loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_nber_shading(fig, x_min=start, x_max=end)
    add_tightening_shading(fig, df)
    fig.add_trace(go.Scatter(x=df.index, y=df["sloos"], name="Net % of banks tightening", line=dict(color=C_IND)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["spy"], name="SPY", line=dict(color=C_TGT)), secondary_y=True)
    legend_square(fig, "rgba(150,120,120,0.35)", "NBER recession period")
    legend_square(fig, "rgba(204,121,167,0.45)", "More banks tightening than easing")
    fig.update_layout(title=title, template="plotly_white", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="Net % tightening", secondary_y=False)
    fig.update_yaxes(title_text="SPY", secondary_y=True)
    from harness.charts import zoom_dual_panel  # VIZ-V1: indicator and target in stacked panels
    fig = zoom_dual_panel(fig)
    save(f"history_zoom_{slug}", fig, f"{title}; gray bands are NBER recessions, pink bands quarters with net "
         "tightening above zero.", [PANEL])


def prune_records() -> None:
    """Drop provenance records of charts this pair no longer has (a renamed chart leaves its old record behind)."""
    mp = chart_provenance.manifest_path(PAIR)
    man = json.loads(mp.read_text())
    keep = {k: v for k, v in man.items() if (OUT / f"{k}.json").is_file()}
    if keep != man:
        mp.write_text(json.dumps(dict(sorted(keep.items())), indent=1) + "\n")
        print(f"  pruned records: {sorted(set(man) - set(keep))}")


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
    chart_history_zoom("dotcom", "Dot-Com Bust: Banks Tightened Through 2000-2001", "1999-03-31", "2003-12-31")
    chart_history_zoom("gfc", "Financial Crisis: Net Tightening Reached Survey Highs", "2006-03-31", "2010-12-31")
    chart_history_zoom("covid", "COVID Shock: A Sharp, Brief Tightening", "2018-03-31", "2021-12-31")
    chart_history_zoom("inflation_2022", "2022-2024 Rate Hikes: Tightening Rose Again", "2021-03-31", "2025-12-31")
    prune_records()
    print(f"Done. Charts saved to {OUT}")


if __name__ == "__main__":
    main()
