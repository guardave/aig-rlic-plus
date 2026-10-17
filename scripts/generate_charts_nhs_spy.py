#!/usr/bin/env python3
"""Chart generation: New Home Sales (NSA, HSN1FNSA) x SPY.

Producer for the nhs_spy chart set. 20261016 run (causal regime port + in-sample selection):
  * The 20260703 winner (hmm_stress / T2_roll_p25 / LB60 / P1 pro / L0, OOS Sharpe 1.49) traded a
    full-sample, forward-backward-smoothed HMM probability at L0, below the L2 lead floor. Regime
    models are now fit on in-sample months only and read with a forward filter
    (scripts/_regime_causal.py); the lead grid is [2, 3, 6, 9, 12]; the winner is the IS-valid row
    with the highest in-sample Sharpe.
  * Every number in a title or caption is read from the results artifacts at run time.
  * NHS is NOT seasonally adjusted; charts never plot the raw NSA level as a signal.

Default run regenerates: correlation_heatmap, hmm_regime_probs, equity_curves, drawdown,
tournament_scatter, tournament_sharpe_dist, rolling_correlation, structural_break,
subperiod_sharpe, walk_forward. `--all` also rebuilds hero, regime_stats, ccf_prewhitened,
granger_f_by_lag, local_projections, transfer_entropy, quantile_coef, history_zoom_* and the
CP2 skip sidecars.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats as sstats

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart, QUARTILE_COLORS  # noqa: E402

PAIR = "nhs_spy"
DATE_TAG = "20261016"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

IND_LONG = "New Home Sales (year-over-year growth)"
IND_SHORT = "New Home Sales YoY"
TGT = "SPY"

PALETTE_ID = "okabe_ito_2026"
PAL = json.loads((REPO / "docs/schemas/color_palette_registry.json").read_text())[
    "palettes"][PALETTE_ID]
C_IND = PAL["primary_data_trace"]
C_TGT = PAL["secondary_data_trace"]
C_POS = PAL["tertiary_data_trace"]
C_BENCH = PAL["benchmark_trace"]
C_NEUTRAL = PAL["hold_indicator"]
C_EVENT = PAL["event_marker_line"]
C_EXT = PAL["categorical_extended"]

ALLOWED_COLORS = ({str(v).lower() for v in PAL.values() if isinstance(v, str)}
                  | {c.lower() for c in C_EXT}
                  | {c.lower() for c in PAL["quartile_gradient"]}
                  | {c.lower() for c in QUARTILE_COLORS}
                  | {"rgba(108,122,137,0.15)", "rgba(0,114,178,0.25)",
                     "rgba(213,94,0,0.25)", "rgba(150,120,120,0.35)",
                     "rgba(213,94,0,0.35)", "rgba(153,153,153,0.45)", "#aec7e8"})

EVENTS_REG = json.loads(
    (REPO / "docs/schemas/history_zoom_events_registry.json").read_text())
EVENTS_REG_VERSION = EVENTS_REG.get("x-version", "1.0.0")

GENERATED_BY = "Viz — scripts/generate_charts_nhs_spy.py (causal HMM port + IS selection, 20261016)"
SRC_DATA = "data/nhs_spy_monthly_latest.parquet"


# ── Loaders ─────────────────────────────────────────────────────────────────
def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / "nhs_spy_monthly_latest.parquet")


def load_tournament() -> pd.DataFrame:
    return pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")


def load_winner() -> dict:
    return json.loads((RES / "winner_summary.json").read_text())


# ── Gates ─────────────────────────────────────────────────────────────────
def _all_text_elements(fig: go.Figure):
    if fig.layout.title and fig.layout.title.text:
        yield "layout.title", fig.layout.title.text
    for i, a in enumerate(fig.layout.annotations or ()):
        if a.text:
            yield f"layout.annotations[{i}]", a.text
    for i, tr in enumerate(fig.data):
        if getattr(tr, "name", None):
            yield f"data[{i}].name", tr.name


def validate_intra_chart_consistency(fig: go.Figure, name: str) -> None:
    violations = []
    for i, tr in enumerate(fig.data):
        if not getattr(tr, "name", None) and getattr(tr, "showlegend", None) is not False:
            if tr.type not in ("heatmap",):
                violations.append(f"trace[{i}] ({tr.type}) unnamed with legend on")
    for tr in fig.data:
        cols = [getattr(getattr(tr, "line", None), "color", None),
                getattr(getattr(tr, "marker", None), "color", None),
                getattr(tr, "fillcolor", None)]
        mc = getattr(getattr(tr, "marker", None), "color", None)
        if isinstance(mc, (list, tuple)):
            cols.extend(mc)
        for col in cols:
            if isinstance(col, str) and col.lower() not in ALLOWED_COLORS \
                    and not col.lower().startswith("rgba(255,255,255"):
                violations.append(f"trace {getattr(tr,'name',None)!r}: color {col} not in {PALETTE_ID}")
    for where, txt in _all_text_elements(fig):
        if str(txt).count("$") > 1:
            violations.append(f"VIZ-TX1: {where} has >1 literal '$': {txt!r}")
    if violations:
        for v in violations:
            print(f"    VIZ-IC1 VIOLATION [{name}]: {v}")
        raise SystemExit(f"VIZ-IC1 pre-save check failed for {name}; save blocked.")
    print(f"    VIZ-IC1 PASS [{name}]")


def assert_nber(fig: go.Figure, name: str) -> None:
    n = sum(1 for s in (fig.layout.shapes or ())
            if s.fillcolor and "rgba(150" in s.fillcolor.replace(" ", ""))
    if n == 0:
        raise SystemExit(f"VIZ-NBER1 FAIL: {name} has no NBER shading shapes.")
    print(f"    VIZ-NBER1 PASS [{name}]: {n} shape(s)")


def check_dual_panel_axes(fig: go.Figure, name: str) -> None:
    d = json.loads(fig.to_json())
    layout = d.get("layout", {})
    if "yaxis2" not in layout:
        return
    if layout.get("yaxis2", {}).get("overlaying") == "y":
        return
    violations = []
    if layout.get("yaxis2", {}).get("anchor", "x2") != "x2":
        violations.append("yaxis2 not anchored to x2")
    for tr in d.get("data", []):
        ya, xa = tr.get("yaxis", "y"), tr.get("xaxis", "x")
        nm = tr.get("name", "?")
        if ya == "y" and xa != "x":
            violations.append(f"top-panel trace {nm}: xaxis={xa}")
        if ya == "y2" and xa != "x2":
            violations.append(f"bottom-panel trace {nm}: xaxis={xa}")
    if violations:
        raise SystemExit(f"VIZ-DP1 FAIL [{name}]: {violations}")
    print(f"    VIZ-DP1 PASS [{name}]")


def save_chart(name: str, fig: go.Figure, *, caption: str, alignment: str,
               rules: list, sources: list,
               reconciliation: dict | None = None,
               extra_meta: dict | None = None,
               nber_required: bool = True) -> None:
    validate_intra_chart_consistency(fig, name)
    if nber_required:
        assert_nber(fig, name)
    check_dual_panel_axes(fig, name)
    fig.write_json(OUT / f"{name}.json")
    meta = {
        "chart_name": name, "pair_id": PAIR, "palette_id": PALETTE_ID,
        "rules_applied": rules, "caption": caption,
        "narrative_alignment_note": alignment, "disposition": "consumed",
        "source_artifacts": sources, "reconciliation": reconciliation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": GENERATED_BY,
    }
    if extra_meta:
        meta.update(extra_meta)
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    try:
        fig.write_image(str(OUT / f"_perceptual_check_{name}.png"),
                        width=1100, height=600, scale=1)
        png = " +perceptual png"
    except Exception as exc:  # Kaleido/Chrome may be unavailable; JSON is what the app reads.
        png = f" (png skipped: {type(exc).__name__})"
    print(f"  wrote {name}.json (+sidecar{png})")


def nber_swatch(fig: go.Figure) -> None:
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square"),
        name="NBER recession (shaded)", hoverinfo="skip"))


# ── 1. Hero — NHS YoY (deseasonalised) vs SPY ─────────────────────────────
def chart_hero():
    df = load_monthly()
    df = df[df["spy"].notna()]
    yoy = df["nhs_pct_yoy"].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=yoy.index, y=yoy.values, name=f"{IND_SHORT} (%, deseasonalised)",
        line=dict(color=C_IND, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["spy"], name=f"{TGT} price (USD)",
        line=dict(color=C_TGT, width=1.5)), secondary_y=True)
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    nber_swatch(fig)
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL, line_width=1.0,
                  secondary_y=False, annotation_text="0% — flat vs a year ago")
    gfc_idx = yoy.loc["2008-01-31":"2009-12-31"].idxmin()
    fig.add_annotation(x=gfc_idx.strftime("%Y-%m-%d"), y=float(yoy.loc[gfc_idx]),
                       text="2008-09: new-home-sales collapse<br>(led the GFC)",
                       showarrow=True, arrowhead=2, ax=-40, ay=-40,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    rate_idx = yoy.loc["2022-06-30":"2023-06-30"].idxmin()
    fig.add_annotation(x=rate_idx.strftime("%Y-%m-%d"), y=float(yoy.loc[rate_idx]),
                       text="2022-23: mortgage-rate shock<br>(sales contract sharply)",
                       showarrow=True, arrowhead=2, ax=30, ay=40,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    y0, y1 = df.index.min().year, df.index.max().year
    fig.update_layout(
        title=(f"{IND_LONG} vs {TGT}: An Early-Cycle Housing Signal "
               f"({y0}–{y1})"),
        template="plotly_white", hovermode="x unified", height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text=f"{IND_SHORT} (%)", secondary_y=False)
    fig.update_yaxes(title_text=f"{TGT} price (USD)", secondary_y=True)
    save_chart("hero", fig,
               caption=(f"{IND_LONG} (vermillion, left axis; year-over-year change, which "
                        f"strips out the regular spring-vs-winter selling swing since the "
                        f"raw Census series is not seasonally adjusted) against the {TGT} "
                        f"price (blue, right axis), {y0}–{y1}. The 2008-09 collapse "
                        f"(sales led the GFC) and the 2022-23 rate-shock contraction are "
                        f"the vivid episodes. Shaded bands mark NBER recessions."),
               alignment=("Hero shows the deseasonalised YoY signal (never the raw NSA "
                          "level) with the 0% line and the housing episodes."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-TX1", "VIZ-O1"],
               sources=[SRC_DATA])


# ── 2. Regime stats (dual-panel) ──────────────────────────────────────────
def chart_regime_stats():
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>(Weakest NHS YoY)", "Q2", "Q3", "Q4<br>(Strongest NHS YoY)"]
    fig = make_dual_panel_regime_chart(
        quartile_labels=labels,
        sharpe=q["sharpe"].tolist(),
        ann_return_pct=(q["ann_return"] * 100).tolist(),
        signal_label=f"{IND_SHORT}",
        x_axis_title=f"{IND_SHORT} quartile (Q1=Weak, Q4=Strong)",
        sample_sizes=q["n_months"].astype(int).tolist(),
    )
    fig.update_layout(
        title=dict(
            text=(f"Procyclical and Monotonic: SPY Sharpe Rises From Q1 "
                  f"{q['sharpe'].iloc[0]:.2f} to Q4 {q['sharpe'].iloc[3]:.2f} as "
                  f"Home-Sales Growth Strengthens"),
            y=0.99, yanchor="top"),
        margin=dict(t=150))
    save_chart("regime_stats", fig,
               caption=(f"SPY performance by {IND_SHORT} quartile (concurrent, "
                        f"descriptive): Sharpe (left) and annualized return (right). "
                        f"Sharpe RISES monotonically from Q1 {q['sharpe'].iloc[0]:.2f} / "
                        f"{q['ann_return'].iloc[0]*100:.1f}% to Q4 {q['sharpe'].iloc[3]:.2f} "
                        f"/ {q['ann_return'].iloc[3]*100:.1f}%, and Q1's max drawdown is "
                        f"{q['max_drawdown'].iloc[0]*100:.0f}% vs Q4's "
                        f"{q['max_drawdown'].iloc[3]*100:.0f}%. Stronger housing demand "
                        f"coincides with better, calmer equity returns — the procyclical "
                        f"prior holds."),
               alignment=("VIZ-QR1 dual-panel from regime_quartile_returns.csv; the "
                          "monotonic Q1->Q4 rise is the procyclical confirmation."),
               rules=["VIZ-QR1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/regime_quartile_returns.csv"],
               nber_required=False)


# ── 3. Correlation heatmap ────────────────────────────────────────────────
_SIGLBL = {
    "yoy": "YoY growth", "yoy_accel": "YoY acceleration",
    "yoy_3m": "3-month-avg YoY", "sa_mom": "SA MoM growth",
    "sa_3m": "SA 3-month growth", "yoy_zscore_120m": "YoY z-score (120-month)",
    "contraction": "Contraction flag",
    "hmm_stress": "HMM higher-variance-state probability (causal)",
    "markov_regime": "Markov higher-variance-regime probability (causal)",
}


def chart_correlation_heatmap():
    c = pd.read_csv(CORE / "correlations.csv")
    p = c[c["metric"] == "pearson"].copy()
    p[["signal", "horizon"]] = p["pair_name"].str.split("__", expand=True)
    hor_order = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    piv = p.pivot(index="signal", columns="horizon", values="value")
    piv = piv.reindex(columns=[h for h in hor_order if h in piv.columns])
    pp = p.pivot(index="signal", columns="horizon", values="p_value").reindex(columns=piv.columns)
    piv = piv.reindex(piv.abs().max(axis=1).sort_values(ascending=False).index)
    pp = pp.reindex(piv.index)
    rows = [_SIGLBL.get(s, s.replace("_", " ")) for s in piv.index]
    cols = [h.replace("spy_fwd_", "").upper() + " fwd" for h in piv.columns]
    annot = [[f"{piv.iloc[i, j]:.3f}" +
              ("**" if pp.iloc[i, j] < 0.01 else "*" if pp.iloc[i, j] < 0.05 else "")
              for j in range(piv.shape[1])] for i in range(piv.shape[0])]
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=cols, y=rows, colorscale="RdBu", zmid=0,
        zmin=-0.3, zmax=0.3, text=annot, texttemplate="%{text}",
        textfont={"size": 10}, name="Pearson r", showlegend=False))
    best = p.loc[p["value"].abs().idxmax()]
    fig.update_layout(
        title=(f"Forward Correlations Are Modest: {IND_SHORT} Signals vs {TGT} "
               f"Forward Returns<br><sup>Pearson r; * p&lt;0.05, ** p&lt;0.01. "
               f"Best cell: {_SIGLBL.get(best['signal'].split('__')[0], best['signal'])} "
               f"r = {best['value']:.3f}</sup>"),
        xaxis_title=f"{TGT} forward return horizon",
        yaxis_title="New Home Sales signal",
        template="plotly_white", height=520)
    save_chart("correlation_heatmap", fig,
               caption=(f"Pearson correlations between New Home Sales signals and {TGT} "
                        f"forward returns at 1/3/6/12-month horizons. The strongest cell "
                        f"is r = {best['value']:.3f} "
                        f"({best['pair_name'].replace('__',' vs ')}). Pairwise "
                        f"correlations are modest. Regime-probability rows use the in-sample-fitted, "
                        f"forward-filtered HMM / Markov-switching models."),
               alignment="Modest linear evidence; best cell re-read from correlations.csv.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/correlations.csv"],
               nber_required=False)


# ── 4. CCF ────────────────────────────────────────────────────────────────
def chart_ccf():
    d = pd.read_csv(CORE / "ccf_prewhitened.csv")
    colors = [C_IND if s else "#aec7e8" for s in d["significant"]]
    fig = go.Figure(go.Bar(x=d["lag"], y=d["ccf"], marker_color=colors,
                           name="Pre-whitened CCF"))
    ci = float(d["upper_ci"].iloc[0])
    fig.add_hline(y=ci, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8,
                  annotation_text="95% confidence band")
    fig.add_hline(y=-ci, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8)
    nsig = int(d["significant"].sum())
    fig.update_layout(
        title=(f"Pre-Whitened Cross-Correlation: {IND_SHORT} vs {TGT} Returns "
               f"<br><sup>AR pre-whitening; {nsig} of {len(d)} lags significant</sup>"),
        xaxis_title=f"Lag (months; negative = {IND_SHORT} leads {TGT})",
        yaxis_title="Cross-correlation",
        template="plotly_white", height=400, showlegend=False)
    save_chart("ccf_prewhitened", fig,
               caption=(f"Cross-correlation between pre-whitened {IND_SHORT} and {TGT} "
                        f"returns across lags. {nsig} of {len(d)} lags clear the 95% band; "
                        f"the forward lead from home-sales growth to equities is weak, "
                        f"consistent with the weak-forward Granger verdict."),
               alignment="CCF mirrors the weak forward lead.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/ccf_prewhitened.csv"],
               nber_required=False)


# ── 5. Granger F by lag (both directions) ─────────────────────────────────
def chart_granger():
    g = pd.read_csv(CORE / "granger_causality.csv")
    bylag = pd.read_csv(RES / "granger_by_lag.csv")
    fwd = g[g["direction"] == "indicator_to_target"].sort_values("lag")
    rev = g[g["direction"] == "target_to_indicator"].sort_values("lag")
    crit = [float(sstats.f.ppf(0.95, r["df_num"], r["df_den"]))
            for _, r in bylag.sort_values("lag").iterrows()]
    fwd_sig = list(fwd.loc[fwd["significant"], "lag"])
    rev_sig = list(rev.loc[rev["significant"], "lag"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=fwd["lag"], y=fwd["f_statistic"],
        name=f"{IND_SHORT} → {TGT} (forward) — significant at lags {fwd_sig or 'none'}",
        marker_color=C_IND))
    fig.add_trace(go.Bar(
        x=rev["lag"], y=rev["f_statistic"],
        name=f"{TGT} → {IND_SHORT} (reverse) — significant at lags {rev_sig or 'none'}",
        marker_color="#aec7e8"))
    fig.add_trace(go.Scatter(
        x=bylag.sort_values("lag")["lag"], y=crit, mode="lines",
        name="5% critical value (per lag)",
        line=dict(color=C_EVENT, dash="dash", width=1.5)))
    fig.update_layout(
        title=(f"Weak Forward Causality: {IND_SHORT} Leads {TGT} Only at a Long Lag "
               f"<br><sup>Toda-Yamamoto Granger F by lag; forward significant at "
               f"{fwd_sig or 'NONE'}; reverse ({TGT}→NHS) at {rev_sig or 'NONE'}</sup>"),
        xaxis_title="Lag (months)", yaxis_title="F-statistic",
        barmode="group", template="plotly_white", height=480, margin=dict(b=140),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("granger_f_by_lag", fig,
               caption=(f"Toda-Yamamoto Granger F-statistics at lags 1–12, both "
                        f"directions. {IND_SHORT} → {TGT} (vermillion, forward) clears the "
                        f"5% line only at lag(s) {fwd_sig or 'NONE'}; {TGT} → {IND_SHORT} "
                        f"(pale blue, reverse) at {rev_sig or 'NONE'}. Forward causality is "
                        f"weak and long-horizon — treat the winning rule as a search-found "
                        f"regime signal, not a validated forward forecaster."),
               alignment=("Both directions shown; forward is weak (single long lag), "
                          "reverse present at short lags — the honest lead-lag picture."),
               rules=["VIZ-IC1", "VIZ-V3", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/granger_causality.csv",
                        f"results/{PAIR}/granger_by_lag.csv"],
               reconciliation={"forward_significant_lags": [int(x) for x in fwd_sig],
                               "reverse_significant_lags": [int(x) for x in rev_sig],
                               "verdict": "weak_forward"},
               nber_required=False)


# ── 6. Local projections ──────────────────────────────────────────────────
def chart_local_projections():
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = make_subplots(rows=1, cols=2, shared_yaxes=False, subplot_titles=[
        f"{IND_SHORT} → {TGT} (forward)", f"{TGT} → {IND_SHORT} (reverse)"])
    have_rev = (lp["direction"] == "rev").any()
    panels = [(1, "fwd", C_IND)] + ([(2, "rev", C_TGT)] if have_rev else [])
    for col, dirn, color in panels:
        d = lp[lp["direction"] == dirn].sort_values("horizon")
        band_fill = "rgba(213,94,0,0.25)" if dirn == "fwd" else "rgba(0,114,178,0.25)"
        fig.add_trace(go.Scatter(
            x=list(d["horizon"]) + list(d["horizon"][::-1]),
            y=list(d["ci_upper"]) + list(d["ci_lower"][::-1]),
            fill="toself", fillcolor=band_fill, mode="lines",
            line=dict(width=0), name=f"95% CI ({dirn})",
            showlegend=False, hoverinfo="skip"), row=1, col=col)
        fig.add_trace(go.Scatter(
            x=d["horizon"], y=d["coef"], mode="lines+markers",
            name=("Coefficient: home sales → market" if dirn == "fwd"
                  else "Coefficient: market → home sales"),
            line=dict(color=color, width=2)), row=1, col=col)
        fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL,
                      line_width=0.8, row=1, col=col)
    pmin = lp[lp["direction"] == "fwd"]["p_value"].min()
    fig.update_layout(
        title=(f"Local Projections (HAC): Forward Impulse Response of {TGT} to "
               f"{IND_SHORT}<br><sup>Forward-direction minimum p = {pmin:.2f}; "
               f"CI bands wide relative to the point estimates</sup>"),
        template="plotly_white", height=460, margin=dict(b=120),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    fig.update_xaxes(title_text="Horizon (months)")
    fig.update_yaxes(title_text="Impulse response coefficient", row=1, col=1)
    save_chart("local_projections", fig,
               caption=(f"Local-projection impulse responses with HAC standard errors at "
                        f"horizons 1/3/6/12 months, both directions. The forward direction "
                        f"({IND_SHORT} → {TGT}) has minimum p = {pmin:.2f}; the response is "
                        f"weak and imprecisely estimated, matching the weak-forward Granger "
                        f"verdict."),
               alignment="Dual-panel LP; forward weakness supports the search-signal framing.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/local_projections.csv"],
               nber_required=False)


# ── 7. Transfer entropy ───────────────────────────────────────────────────
def chart_transfer_entropy():
    te = pd.read_csv(CORE / "transfer_entropy.csv")
    lab = {"indicator_to_target": f"{IND_SHORT} → {TGT}",
           "target_to_indicator": f"{TGT} → {IND_SHORT}"}
    fwd_p = float(te.loc[te["direction"] == "indicator_to_target", "permutation_p_value"].iloc[0])
    rev_p = float(te.loc[te["direction"] == "target_to_indicator", "permutation_p_value"].iloc[0])
    fig = go.Figure()
    for _, r in te.iterrows():
        fig.add_trace(go.Bar(
            x=[lab[r["direction"]]], y=[r["te_value"]],
            name=f"{lab[r['direction']]} (perm. p = {r['permutation_p_value']:.2f})",
            marker_color=C_IND if r["direction"] == "indicator_to_target" else C_TGT,
            text=[f"TE = {r['te_value']:.4f}<br>p = {r['permutation_p_value']:.2f}"],
            textposition="outside"))
    fig.update_layout(
        title=("Transfer Entropy: Nonlinear Information Flow Between "
               f"{IND_SHORT} and {TGT}<br><sup>Tercile binning, 500 permutations; "
               f"forward p = {fwd_p:.2f}, reverse p = {rev_p:.2f}</sup>"),
        yaxis_title="Transfer entropy (nats)", xaxis_title="Direction",
        template="plotly_white", height=400, showlegend=False)
    save_chart("transfer_entropy", fig,
               caption=(f"Transfer entropy between {IND_SHORT} and {TGT} returns (tercile "
                        f"bins, 500 permutations). Forward p = {fwd_p:.2f}, reverse "
                        f"p = {rev_p:.2f}; neither direction shows strong nonlinear "
                        f"information flow, consistent with the weak linear lead-lag."),
               alignment="Two-bar TE comparison; weak significance both ways.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/transfer_entropy.csv"],
               nber_required=False)


# ── 8. Quantile regression ────────────────────────────────────────────────
def chart_quantile():
    qr = pd.read_csv(CORE / "quantile_regression.csv").sort_values("tau")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(qr["tau"]) + list(qr["tau"][::-1]),
        y=list(qr["ci_upper"]) + list(qr["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(0,114,178,0.25)", mode="lines",
        line=dict(width=0), name="95% CI", hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=qr["tau"], y=qr["coef"], mode="lines+markers",
        name="Quantile coefficient", line=dict(color=C_TGT, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8)
    sig_tau = qr.loc[qr["p_value"] < 0.05, "tau"].tolist()
    fig.update_layout(
        title=(f"Quantile Regression: {IND_SHORT} on {TGT} Forward Returns "
               f"<br><sup>Coefficient by return quantile; significant tau values: "
               f"{sig_tau}</sup>"),
        xaxis_title=f"Return quantile (tau) of {TGT}",
        yaxis_title="Coefficient", template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("quantile_coef", fig,
               caption=(f"Quantile-regression coefficient of {TGT} forward returns on "
                        f"{IND_SHORT} across return quantiles 0.05–0.95 with 95% CI. "
                        f"Significant tau values: {sig_tau}. The relationship varies "
                        f"across the return distribution rather than being a clean uniform "
                        f"forward predictor."),
               alignment="Coef-by-tau with CI band.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv"],
               nber_required=False)


# ── 9. HMM regime probabilities (causal: IS-only fit, forward filter) ─────
def chart_hmm():
    h = pd.read_parquet(CORE / "hmm_states.parquet")
    summ = pd.read_csv(CORE / "hmm_summary.csv")
    reg = json.loads((CORE / "regime_models.json").read_text())
    fit = reg["models"]["hmm_2state_prob_stress"]
    st = summ.set_index("state_label")
    stress_pct = float(st.loc["stress", "frequency_pct"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h.index, y=h["prob_stress"], mode="lines",
        name="P(higher-variance state), forward-filtered",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.25)",
        line=dict(color=C_IND, width=1.2)))
    fig.add_vline(x=pd.Timestamp(reg["oos_start"]).timestamp() * 1000, line=dict(color=C_EVENT, dash="dot", width=1.3))
    fig.add_annotation(x=reg["oos_start"], y=0.96, yref="paper", showarrow=False, xanchor="left",
                       text="OOS begins (model frozen)", font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=h.index.min(), x_max=h.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Hidden Markov Model on {IND_SHORT}: Probability of the Higher-Variance State<br><sup>"
               f"Fit on {fit['n_fit']} in-sample months ({fit['fit_start'][:7]}–{fit['fit_end'][:7]}), "
               f"forward filter; this state averages {float(st.loc['stress', 'mean_yoy_growth']):+.1f}% YoY "
               f"and covers {stress_pct:.0f}% of months</sup>"),
        xaxis_title="Date", yaxis_title="Probability of higher-variance state",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("hmm_regime_probs", fig,
               caption=(f"Probability that {IND_SHORT} is in the HMM state with the higher in-sample "
                        f"variance (labelled 'stress' in the data files, as in the earlier version). The "
                        f"model is fit on in-sample months only and each month's value uses data up to "
                        f"that month. The two states differ mainly in their mean: the labelled state "
                        f"averages {float(st.loc['stress', 'mean_yoy_growth']):+.1f}% YoY growth "
                        f"({stress_pct:.0f}% of months), the other "
                        f"{float(st.loc['calm', 'mean_yoy_growth']):+.1f}% (housing downturns). "
                        f"Shaded bands mark NBER recessions."),
               alignment="Causal HMM (IS-only fit, forward filter); state label semantics stated.",
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/hmm_states.parquet",
                        f"results/{PAIR}/core_models_{DATE_TAG}/hmm_summary.csv",
                        f"results/{PAIR}/core_models_{DATE_TAG}/regime_models.json"])


# ── 10/11. Equity curves + drawdown ───────────────────────────────────────
def _strategy_returns() -> pd.DataFrame:
    d = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"])
    d["strategy_equity"] = (1 + d["strategy_return"]).cumprod()
    d["bh_equity"] = (1 + d["bh_return"]).cumprod()
    d["strategy_drawdown"] = d["strategy_equity"] / d["strategy_equity"].cummax() - 1
    d["bh_drawdown"] = d["bh_equity"] / d["bh_equity"].cummax() - 1
    return d


def chart_equity_curves():
    d = _strategy_returns()
    w = load_winner()
    oos = d[d["date"] >= w["oos_period_start"]]
    expo = float(oos["position"].mean())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["strategy_equity"], mode="lines",
        name=f"NHS contraction-flag rule (OOS Sharpe {w['oos_sharpe']:.2f})",
        line=dict(color=C_IND, width=2.2)))
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["bh_equity"], mode="lines",
        name=f"Buy & Hold {TGT} (OOS Sharpe {w['bh_sharpe']:.2f})",
        line=dict(color=C_BENCH, width=1.8, dash="dash")))
    fig.add_vline(x=w["oos_period_start"], line=dict(color=C_EVENT, dash="dot", width=1.3))
    fig.add_annotation(x=w["oos_period_start"], y=0.96, yref="paper", showarrow=False,
                       xanchor="left", text="OOS begins",
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=d["date"].min(), x_max=d["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"NHS Rule vs Buy & Hold {TGT}<br><sup>OOS {w['oos_period_start']} to "
               f"{w['oos_period_end']} ({w['oos_n']} months): {w['oos_ann_return']*100:.1f}% vs "
               f"{w['bh_ann_return']*100:.1f}% annualized; Sharpe {w['oos_sharpe']:.2f} vs "
               f"{w['bh_sharpe']:.2f}</sup>"),
        xaxis_title="Date", yaxis_title="Growth of 1.00",
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("equity_curves", fig,
               caption=(f"Cumulative growth of 1.00 for the selected rule and buy-and-hold {TGT}. Over the "
                        f"{w['oos_n']}-month OOS window the rule averaged {expo:.0%} invested: "
                        f"{w['oos_ann_return']*100:.1f}% annualized vs {w['bh_ann_return']*100:.1f}%, "
                        f"Sharpe {w['oos_sharpe']:.2f} vs {w['bh_sharpe']:.2f} (HAC t {w['oos_hac_t']:.2f}), "
                        f"maximum drawdown {w['oos_max_drawdown']*100:.1f}% vs "
                        f"{w['bh_max_drawdown']*100:.1f}%. Shaded bands mark NBER recessions."),
               alignment="Strategy series from strategy_returns; metrics from winner_summary.",
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


def chart_drawdown():
    d = _strategy_returns()
    w = load_winner()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["strategy_drawdown"] * 100, mode="lines",
        name=f"Strategy drawdown (OOS max {w['oos_max_drawdown']*100:.1f}%)",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.35)",
        line=dict(color=C_IND, width=1.5)))
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["bh_drawdown"] * 100, mode="lines",
        name=f"Buy & Hold drawdown (OOS max {w['bh_max_drawdown']*100:.1f}%)",
        line=dict(color=C_BENCH, width=1.5, dash="dash")))
    fig.add_vline(x=w["oos_period_start"], line=dict(color=C_EVENT, dash="dot", width=1.3))
    add_nber_shading(fig, x_min=d["date"].min(), x_max=d["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Drawdown: Rule {w['oos_max_drawdown']*100:.1f}% vs Buy & Hold "
               f"{w['bh_max_drawdown']*100:.1f}% (OOS maximum)"),
        xaxis_title="Date", yaxis_title="Drawdown (%)",
        template="plotly_white", height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("drawdown", fig,
               caption=(f"Drawdown path for the selected rule and buy-and-hold {TGT}. OOS maximum drawdown "
                        f"{w['oos_max_drawdown']*100:.1f}% for the rule and {w['bh_max_drawdown']*100:.1f}% "
                        f"for buy-and-hold. Shaded bands mark NBER recessions."),
               alignment="Drawdown computed directly from the saved monthly return series.",
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


# ── 12/13. Tournament scatter + distribution ──────────────────────────────
def _tournament_frames():
    t = load_tournament()
    valid = t[t["valid"] & (t["signal"] != "BENCHMARK")]
    bench = t[t["signal"] == "BENCHMARK"]
    return t, valid, bench


def chart_tournament_scatter():
    t, valid, bench = _tournament_frames()
    w = load_winner()
    sel = w["selection"]
    rho = float(sel["grid_scanned"]["spearman_is_vs_oos"])
    fig = go.Figure()
    for i, fam in enumerate(["P1_long_cash", "P2_signal_strength", "P3_long_short"]):
        sub = valid[valid["strategy"].str.startswith(fam)]
        fig.add_trace(go.Scatter(
            x=sub["is_sharpe"], y=sub["oos_sharpe"], mode="markers",
            marker=dict(size=4, color=C_EXT[i % len(C_EXT)], opacity=0.45), name=fam,
            text=[f"{r['signal']}/{r['threshold']}/{r['strategy']}/L{r['lead_months']}/{r['lookback']}"
                  for _, r in sub.iterrows()],
            hovertemplate="%{text}<br>IS Sharpe: %{x:.2f}<br>OOS Sharpe: %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[float(w["is_sharpe"])], y=[float(w["oos_sharpe"])], mode="markers",
        marker=dict(size=16, color=C_POS, symbol="star", line=dict(width=1, color="#000000")),
        name=f"Selected (highest IS Sharpe {float(w['is_sharpe']):.2f}; OOS {float(w['oos_sharpe']):.2f})"))
    fig.add_hline(y=float(bench.iloc[0]["oos_sharpe"]), line=dict(color=C_BENCH, dash="dash", width=1.2),
                  annotation_text=f"B&H OOS {float(bench.iloc[0]['oos_sharpe']):.2f}", annotation_position="bottom right")
    fig.add_vline(x=float(bench.iloc[0]["is_sharpe"]), line=dict(color=C_BENCH, dash="dot", width=1.2),
                  annotation_text=f"B&H IS {float(bench.iloc[0]['is_sharpe']):.2f}", annotation_position="top left")
    fig.update_layout(
        title=(f"Tournament: {len(valid):,} IS-Valid Combos, In-Sample vs Out-of-Sample Sharpe "
               f"(Spearman {rho:.2f})"),
        xaxis_title="In-sample Sharpe (selection objective)", yaxis_title="OOS Sharpe",
        template="plotly_white", height=540, margin=dict(b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0))
    save_chart("tournament_scatter", fig,
               caption=(f"Each dot is one of the {len(valid):,} IS-valid combinations ({len(t)-1:,} scanned), "
                        f"plotted by in-sample Sharpe (common window {sel['is_window']['start']} to "
                        f"{sel['is_window']['end']}) and OOS Sharpe ({w['oos_period_start']} to "
                        f"{w['oos_period_end']}). The star is the selected rule: the highest in-sample Sharpe. "
                        f"Spearman rank correlation between IS and OOS Sharpe: {rho:.2f}. Dashed lines: "
                        f"buy-and-hold {TGT}."),
               alignment="IS vs OOS scatter; selection by IS Sharpe; benchmark via signal=='BENCHMARK' (ECON-T4).",
               rules=["VIZ-IC1", "ECON-T4", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               nber_required=False)


def chart_tournament_dist():
    t, valid, bench = _tournament_frames()
    w = load_winner()
    med = float(valid["oos_sharpe"].median())
    wsharpe = float(w["oos_sharpe"])
    bh = float(bench.iloc[0]["oos_sharpe"])
    pct = float((valid["oos_sharpe"] < wsharpe).mean() * 100)
    n_beat = int((valid["oos_sharpe"] > bh).sum())
    fig = go.Figure(go.Histogram(
        x=valid["oos_sharpe"], nbinsx=60, marker_color=C_TGT, opacity=0.75,
        name=f"IS-valid strategies (n = {len(valid):,})"))
    fig.add_vline(x=med, line=dict(color=C_NEUTRAL, dash="dot", width=1.5))
    fig.add_vline(x=bh, line=dict(color=C_BENCH, dash="dash", width=2))
    fig.add_vline(x=wsharpe, line=dict(color=C_IND, dash="dash", width=2))
    fig.add_annotation(x=wsharpe, y=1.0, yref="paper", showarrow=False, xanchor="left",
                       text=f"Selected rule = {wsharpe:.2f} (median {med:.2f})",
                       font=dict(size=12, color=C_IND), bgcolor=PAL["event_marker_label_bg"])
    fig.add_annotation(x=bh, y=0.85, yref="paper", showarrow=False, xanchor="right",
                       text=f"Buy & Hold {TGT} = {bh:.2f}",
                       font=dict(size=12, color=C_BENCH), bgcolor=PAL["event_marker_label_bg"])
    fig.update_layout(
        title=(f"OOS Sharpe Across {len(valid):,} IS-Valid Combos<br><sup>Selected rule {wsharpe:.2f} "
               f"({pct:.0f}th percentile); median {med:.2f}; buy & hold {bh:.2f}; "
               f"{n_beat:,} combos above buy & hold</sup>"),
        xaxis_title="OOS Sharpe ratio", yaxis_title="Number of strategies",
        template="plotly_white", height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("tournament_sharpe_dist", fig,
               caption=(f"Distribution of OOS Sharpe across the {len(valid):,} IS-valid combinations. The "
                        f"selected rule (chosen by in-sample Sharpe, before looking at OOS) scores "
                        f"{wsharpe:.2f}, the {pct:.0f}th percentile. Median {med:.2f}; buy & hold {bh:.2f}; "
                        f"{n_beat:,} of {len(valid):,} combos have a higher OOS Sharpe than buy & hold."),
               alignment="VIZ-SCD1 position disclosure + B&H line; percentile computed from the CSV.",
               rules=["VIZ-SCD1", "ECON-T4", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               reconciliation={"valid_count": len(valid), "median_oos_sharpe": round(med, 4),
                               "winner_oos_sharpe": round(wsharpe, 4), "bh_oos_sharpe": round(bh, 4)},
               nber_required=False)


# ── 14. Rolling correlation ───────────────────────────────────────────────
def chart_rolling_correlation():
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    w = load_winner()
    win = int(rc["n_obs"].iloc[0])
    verdict = sb["rolling_corr_stability_verdict"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rc["date"], y=rc["rolling_corr"], mode="lines",
        name=f"{win}-month rolling correlation", line=dict(color=C_TGT, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_EVENT, line_width=1,
                  annotation_text="No correlation")
    add_nber_shading(fig, x_min=rc["date"].min(), x_max=rc["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"{win}-Month Rolling Correlation: Selected Signal (lagged {w['lead_value']}m) vs "
               f"Next-Month {TGT} Return<br><sup>Share of windows with the full-sample sign "
               f"{sb['rolling_corr_sign_stability']:.2f} ({verdict.replace('_', ' ')})</sup>"),
        xaxis_title="Date", yaxis_title="Rolling correlation (r)",
        template="plotly_white", height=420, yaxis=dict(range=[-1, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("rolling_correlation", fig,
               caption=(f"{win}-month rolling correlation between the selected signal "
                        f"({w['signal_display_name']}, lagged {w['lead_value']} months) and the next-month "
                        f"{TGT} return. The sign matches the full-sample sign in "
                        f"{sb['rolling_corr_sign_stability']:.0%} of windows ({verdict.replace('_',' ')}). "
                        f"Shaded bands mark NBER recessions."),
               alignment="Series and stability verdict read from the rolling-correlation CSV and structural_break JSON.",
               rules=["VIZ-CP1.2", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/rolling_correlation_{PAIR}.csv",
                        f"results/{PAIR}/structural_break_{PAIR}.json"])


# ── 15. Structural break ──────────────────────────────────────────────────
def chart_structural_break():
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    w = load_winner()
    df = load_monthly()
    sig = df.loc[sb["sample_start"]:sb["sample_end"], "nhs_pct_yoy"].dropna()
    flagged = bool(sb["flagged"])
    verdict_txt = "Structural Break Flagged" if flagged else "No Structural Break Flagged"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig.index, y=sig.values, mode="lines",
        name=f"{IND_SHORT} (%)", line=dict(color=C_IND, width=1.8)))
    fig.add_vline(x=pd.Timestamp(sb["break_date"]).timestamp() * 1000,
                  line=dict(color=C_EVENT, dash="dash", width=2))
    fig.add_annotation(x=sb["break_date"], y=0.95, yref="paper", showarrow=False,
                       xanchor="left",
                       text=(f"Candidate break {sb['break_date'][:7]}: sup-F "
                             f"{sb['f_stat']:.2f}, bootstrap p = {sb['p_value']:.2f}"),
                       font=dict(size=12, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=sig.index.min(), x_max=sig.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"{verdict_txt}: Quandt-Andrews sup-F Test, {TGT} Return on the Selected Signal "
               f"(candidate {sb['break_date'][:7]}, p = {sb['p_value']:.2f})"),
        xaxis_title="Date", yaxis_title=f"{IND_SHORT} (%)",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("structural_break", fig,
               caption=(f"Quandt-Andrews unknown-breakpoint test on the regression of the monthly {TGT} return "
                        f"on the selected signal ({w['signal_display_name']}) lagged {w['lead_value']} months "
                        f"({sb['sample_start'][:7]}–{sb['sample_end'][:7]}, n = {sb['n_obs']}). The line plots "
                        f"{IND_SHORT} for context; the dashed marker is the candidate break "
                        f"{sb['break_date'][:7]}: sup-F {sb['f_stat']:.2f}, residual-bootstrap p = "
                        f"{sb['p_value']:.2f} — {'flagged' if flagged else 'not flagged'} at 10%. Shaded bands "
                        f"mark NBER recessions."),
               alignment="Annotation-driven; flagged state and values read from JSON.",
               rules=["VIZ-CP1.3", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/structural_break_{PAIR}.json", SRC_DATA],
               extra_meta={"break_date": sb["break_date"],
                           "annotation_strategy_id": "manual_override"})


# ── 16. Sub-period Sharpe ─────────────────────────────────────────────────
_EP_LABEL = {"dot_com": "Dot-Com 2000–02", "gfc": "GFC 2008–09",
             "covid": "COVID 2020", "china_2015": "China 2015–16"}


def chart_subperiod_sharpe():
    rows = pd.read_csv(RES / "subperiod_sharpe.csv")
    w = load_winner()
    oos_y = w["oos_period_start"][:4]
    labels, values, colors, texts = [], [], [], []
    for _, r in rows.iterrows():
        lab = _EP_LABEL.get(r["episode"], r["episode"])
        if r["data_status"] == "insufficient_data" or pd.isna(r["ann_sharpe"]):
            labels.append(f"{lab}<br>(outside OOS window)")
            values.append(0.0); colors.append(C_NEUTRAL); texts.append("no data")
        elif abs(float(r["ann_sharpe"])) < 1e-9:
            labels.append(f"{lab}<br>(strategy in cash)")
            values.append(0.0); colors.append(C_NEUTRAL); texts.append("cash")
        else:
            labels.append(lab)
            values.append(float(r["ann_sharpe"]))
            colors.append(C_POS if r["ann_sharpe"] >= 0 else C_IND)
            texts.append(f"{float(r['ann_sharpe']):+.2f}")
    n_eval = int(((rows["data_status"] == "validated") & rows["ann_sharpe"].notna()).sum())
    verdict = rows["durability_verdict"].dropna()
    verdict = verdict.iloc[-1] if len(verdict) else "n/a"
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=texts, textposition="outside",
                           name="Annualized Sharpe by episode"))
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Selected Rule by Historical Episode<br><sup>{n_eval} of {len(rows)} canonical episodes "
               f"fall inside the {oos_y}+ OOS window; the others predate the OOS split</sup>"),
        xaxis_title="Historical episode", yaxis_title="Annualized Sharpe ratio",
        template="plotly_white", height=430, margin=dict(b=110), showlegend=False)
    save_chart("subperiod_sharpe", fig,
               caption=(f"Selected-rule annualized Sharpe within each canonical stress episode. {n_eval} of "
                        f"{len(rows)} fall inside the {oos_y}+ OOS window; the others predate the OOS split and "
                        f"are marked insufficient_data. Durability label: '{verdict}'."),
               alignment="Three-state encoding; counts and verdict read from subperiod_sharpe.csv.",
               rules=["ECON-CP1", "VIZ-CP1.1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/subperiod_sharpe.csv"],
               nber_required=False)


# ── 17. History zoom charts ───────────────────────────────────────────────
def _window_has_recession(start: str, end: str) -> bool:
    from _nber import RECESSIONS
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return any(pd.Timestamp(r0) <= e and pd.Timestamp(r1) >= s for r0, r1 in RECESSIONS)


def chart_history_zoom(slug: str):
    ep = EVENTS_REG["episodes"][slug]
    df = load_monthly()
    w = df.loc[ep["start_date"]:ep["end_date"]]
    sig = w["nhs_pct_yoy"].dropna()
    spy = w["spy"].dropna()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[f"{IND_SHORT} (%)", f"{TGT} price (USD)"])
    fig.add_trace(go.Scatter(x=sig.index, y=sig.values, name=f"{IND_SHORT} (%)",
                             line=dict(color=C_IND, width=2)), row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8, row=1, col=1)
    fig.add_trace(go.Scatter(x=spy.index, y=spy.values, name=f"{TGT} price (USD)",
                             line=dict(color=C_TGT, width=2)), row=2, col=1)
    has_rec = _window_has_recession(ep["start_date"], ep["end_date"])
    if has_rec:
        add_nber_shading(fig, x_min=w.index.min(), x_max=w.index.max(),
                         xref="x", yref="y domain")
        add_nber_shading(fig, x_min=w.index.min(), x_max=w.index.max(),
                         xref="x2", yref="y2 domain")
        nber_swatch(fig)
    for i, ev in enumerate(ep["key_events"]):
        for xref, yref in (("x", "y domain"), ("x2", "y2 domain")):
            fig.add_shape(type="line", x0=ev["date"], x1=ev["date"], y0=0, y1=1,
                          xref=xref, yref=yref,
                          line=dict(color=C_EVENT, dash="dash", width=1.2))
        fig.add_annotation(x=ev["date"], xref="x", y=0.97 - 0.10 * i, yref="y domain",
                           text=ev["label"], showarrow=False, xanchor="left",
                           font=dict(size=10, color=C_EVENT),
                           bgcolor=PAL["event_marker_label_bg"])
    fig.update_layout(
        title=(f"{IND_LONG} and {TGT} During the {ep['episode_name']}, "
               f"{ep['start_date'][:4]}–{ep['end_date'][:4]}"),
        template="plotly_white", height=560,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1))
    fig.update_xaxes(matches="x2", showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=True, title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="NHS YoY (%)", row=1, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    save_chart(f"history_zoom_{slug}", fig,
               caption=(f"{IND_SHORT} (top, with 0% line) and {TGT} price (bottom) through "
                        f"the {ep['episode_name']} window ({ep['start_date'][:7]} to "
                        f"{ep['end_date'][:7]}), with registry event markers."
                        + (" Shaded bands mark NBER recessions." if has_rec
                           else " No NBER recession falls in this window.")),
               alignment=(f"Dual-panel episode zoom; events from "
                          f"history_zoom_events_registry v{EVENTS_REG_VERSION}."),
               rules=["VIZ-V1", "VIZ-V2", "VIZ-V12", "VIZ-V13", "VIZ-TS1",
                      "VIZ-DP1", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[SRC_DATA, "docs/schemas/history_zoom_events_registry.json"],
               extra_meta={"annotation_strategy_id": "descending_stair",
                           "events_registry_version": EVENTS_REG_VERSION,
                           "episode_slug": slug},
               nber_required=has_rec)


# ── 18. Walk-forward rolling Sharpe (Confidence tab) ──────────────────────
def chart_walk_forward():
    import numpy as np
    d = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    w = load_winner()
    oos = d[(d.index >= w["oos_period_start"]) & (d.index <= w["oos_period_end"])]
    window, min_p, ann = 12, 8, 12
    r_s = oos["strategy_return"].astype(float)
    r_b = oos["bh_return"].astype(float)
    roll_s = (r_s.rolling(window, min_periods=min_p).mean() * ann) / \
             (r_s.rolling(window, min_periods=min_p).std() * np.sqrt(ann) + 1e-12)
    roll_s = roll_s.where(r_s.rolling(window, min_periods=min_p).std() > 0)
    roll_b = (r_b.rolling(window, min_periods=min_p).mean() * ann) / \
             (r_b.rolling(window, min_periods=min_p).std() * np.sqrt(ann) + 1e-12)
    reported = float(w["oos_sharpe"])
    y0, y1 = w["oos_period_start"][:4], w["oos_period_end"][:4]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_b.index, y=roll_b.values,
                             name=f"Buy & Hold {TGT}",
                             line=dict(color=C_BENCH, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=roll_s.index, y=roll_s.values,
                             name=f"Strategy rolling {window}-month Sharpe",
                             line=dict(color=C_IND, width=2)))
    add_nber_shading(fig, x_min=oos.index.min(), x_max=oos.index.max())
    nber_swatch(fig)
    fig.add_hline(y=reported, line=dict(color=C_POS, dash="dash", width=1.2),
                  annotation_text=f"Reported OOS Sharpe = {reported:.2f}",
                  annotation_position="top left")
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Walk-Forward: Rolling 12-Month Sharpe vs Reported OOS Sharpe "
               f"{reported:.2f} (OOS {y0}–{y1})"),
        xaxis_title="Date", yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("walk_forward", fig,
               caption=(f"Rolling 12-month annualized Sharpe of the selected rule vs "
                        f"buy-and-hold {TGT} over the out-of-sample window; the dashed "
                        f"reference line marks the reported OOS Sharpe ({reported:.2f})."),
               alignment=("Rolling-Sharpe walk-forward for the Strategy page Confidence "
                          "tab; reference line reconciles with winner_summary OOS Sharpe."),
               rules=["ECON-SR1", "VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


# ── CP2 skip sidecars ─────────────────────────────────────────────────────
def write_cp2_skips():
    for c in ("rolling_sharpe_cp", "rolling_granger"):
        (OUT / f"chart_skip_{c}.json").write_text(json.dumps({
            "chart_name": c, "pair_id": PAIR, "skipped_by": "VIZ-CP1-G",
            "reason": ("ECON-CP2 artifacts intentionally absent for this pair: "
                       "regime_story=false in results/nhs_spy/signal_scope.json "
                       "(Evan handoff). No upstream result file exists to chart."),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": GENERATED_BY,
        }, indent=2) + "\n")
        print(f"  wrote chart_skip_{c}.json")


# ── MAIN ──────────────────────────────────────────────────────────────────
# Default: regenerate only the charts that depend on the winner, the tournament, the regime
# models or the cross-period artifacts. The evidence charts (hero, regime_stats, ccf, granger,
# local_projections, transfer_entropy, quantile_coef, history_zoom_*) carry later hand fixes
# (#242/#243) and their inputs did not change in the 20261016 run; pass --all to rebuild them.
if __name__ == "__main__":
    print(f"Generating charts for {PAIR} (DATE_TAG {DATE_TAG})...")
    if "--all" in sys.argv:
        chart_hero()
        chart_regime_stats()
        chart_ccf()
        chart_granger()
        chart_local_projections()
        chart_transfer_entropy()
        chart_quantile()
        for slug in ("dotcom", "gfc", "covid", "inflation_2022"):
            chart_history_zoom(slug)
        write_cp2_skips()
    chart_correlation_heatmap()
    chart_hmm()
    chart_equity_curves()
    chart_drawdown()
    chart_tournament_scatter()
    chart_tournament_dist()
    chart_rolling_correlation()
    chart_structural_break()
    chart_subperiod_sharpe()
    chart_walk_forward()
    print("\nDone.")
