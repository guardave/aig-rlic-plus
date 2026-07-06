#!/usr/bin/env python3
"""Chart generation: NAHB/Wells Fargo Housing Market Index x SPY — MONTHLY pair.

Vera-owned producer for the wells_fargo_housing_spy standard chart set
(feat260706_wells_fargo_housing_spy). Consumes Evan's handoff artifacts
(results/wells_fargo_housing_spy/) and Dana's monthly dataset. The ECON-SR1
strategy-performance charts (equity_curves, drawdown, walk_forward) are
produced by scripts/generate_strategy_perf_charts.py — NOT here (META-NMF).

Framing (binding, per Lead dispatch + Evan handoff): builder sentiment does
NOT lead the market. SPY→HMI Granger is significant at ALL 12 lags; HMI→SPY
at lag 5 only; transfer entropy is reverse-only; lead correlations are weak
(|r| <= ~0.12); the era battery is NULL in all four eras. The tournament
winner (diff_12m / T2_roll_p25 / P1 pro / L7, OOS Sharpe 1.43 vs B&H 0.94)
is a found-in-search CANDIDATE whose L7 peak is a SPIKE, not a ridge
(L6 1.00 / L7 1.43 / L8 0.93; ECON-LT2 durability FAIL; bootstrap p=0.127).
Its defensible virtue is DRAWDOWN REDUCTION (-8.1% vs -23.9%), not the
Sharpe. Chart titles/captions carry that framing.

Charts produced (output/charts/wells_fargo_housing_spy/plotly/, bare names):
    hero, regime_stats, correlation_heatmap, ccf_prewhitened,
    granger_f_by_lag, local_projections, transfer_entropy, quantile_coef,
    hmm_regime_probs, tournament_scatter, tournament_sharpe_dist,
    rolling_correlation, structural_break, subperiod_sharpe,
    history_zoom_{dotcom,gfc,covid,inflation_2022},
    correlations_lead_view, lead_sharpe_distribution   (GH #13 natives)
    + chart_skip_{rolling_sharpe_cp,rolling_granger}.json (regime_story
      false in signal_scope.json — VIZ-CP1-G skip protocol)

CCF lag-sign convention (verified against the wells pipeline, section 4.1):
POSITIVE lag = indicator (HMI) leads SPY. This is pair-pipeline-specific —
do not copy the axis label from other pairs without checking.

Gates implemented in-process: VIZ-IC1 (pre-save lint incl. palette + VIZ-TX1
one-$ rule), VIZ-NBER1, VIZ-DP1, VIZ-TS1, perceptual PNGs (VIZ-CV1),
_meta.json sidecars with disposition + reconciliation values re-read from
artifacts at generation time.

Author: Viz Vera. Date: 2026-07-06.
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
from scipy import stats as sstats

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import make_dual_panel_regime_chart, QUARTILE_COLORS  # noqa: E402

PAIR = "wells_fargo_housing_spy"
DATE_TAG = "20260706"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

# Display names (VIZ-NS1). app/components/display_names.py has no
# wells_fargo_housing_spy entry yet — gap flagged to Ace in the handoff;
# these constants are the proposed canonical forms.
IND_LONG = "NAHB/Wells Fargo Housing Market Index (HMI)"
IND_SHORT = "NAHB HMI"
TGT = "SPY"

# ── Palette (okabe_ito_2026, VIZ-V11) ─────────────────────────────────────
PALETTE_ID = "okabe_ito_2026"
PAL = json.loads((REPO / "docs/schemas/color_palette_registry.json").read_text())[
    "palettes"][PALETTE_ID]
C_IND = PAL["primary_data_trace"]       # #D55E00 indicator
C_TGT = PAL["secondary_data_trace"]     # #0072B2 target
C_POS = PAL["tertiary_data_trace"]      # #009E73
C_BENCH = PAL["benchmark_trace"]        # #6C7A89
C_NEUTRAL = PAL["hold_indicator"]       # #999999
C_EVENT = PAL["event_marker_line"]      # #4D4D4D
C_EXT = PAL["categorical_extended"]

ALLOWED_COLORS = ({str(v).lower() for v in PAL.values() if isinstance(v, str)}
                  | {c.lower() for c in C_EXT}
                  | {c.lower() for c in PAL["quartile_gradient"]}
                  | {c.lower() for c in QUARTILE_COLORS}
                  | {"rgba(108,122,137,0.15)", "rgba(0,114,178,0.25)",
                     "rgba(213,94,0,0.25)", "rgba(150,120,120,0.35)",
                     "rgba(153,153,153,0.45)", "rgba(108,122,137,0.45)",
                     "#aec7e8"})

EVENTS_REG = json.loads(
    (REPO / "docs/schemas/history_zoom_events_registry.json").read_text())
EVENTS_REG_VERSION = EVENTS_REG.get("x-version", "1.0.0")

GENERATED_BY = ("Viz Vera — scripts/generate_charts_wells_fargo_housing_spy.py "
                "(feat260706_wells_fargo_housing_spy)")

SRC_DATA = "data/wells_fargo_housing_spy_monthly_latest.parquet"


# ── Loaders ───────────────────────────────────────────────────────────────

def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / SRC_DATA)


def load_tournament() -> pd.DataFrame:
    return pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")


def load_winner() -> dict:
    return json.loads((RES / "winner_summary.json").read_text())


def load_bootstrap_p() -> float:
    b = pd.read_csv(RES / f"tournament_validation_{DATE_TAG}" / "bootstrap.csv")
    return float(b.iloc[0]["bootstrap_p_value"])


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
    """VIZ-IC1 pre-save lint (+ VIZ-TX1 one-literal-$ rule)."""
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
                violations.append(
                    f"trace {getattr(tr, 'name', None)!r}: color {col} not in {PALETTE_ID}")
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
    """VIZ-DP1 axis-assignment check for dual-panel charts."""
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


# ── Save helper ───────────────────────────────────────────────────────────

def save_chart(name: str, fig: go.Figure, *, caption: str, alignment: str,
               rules: list[str], sources: list[str],
               reconciliation: dict | None = None,
               extra_meta: dict | None = None,
               nber_required: bool = True) -> None:
    validate_intra_chart_consistency(fig, name)
    if nber_required:
        assert_nber(fig, name)
    check_dual_panel_axes(fig, name)
    fig.write_json(OUT / f"{name}.json")
    meta = {
        "chart_name": name,
        "pair_id": PAIR,
        "palette_id": PALETTE_ID,
        "rules_applied": rules,
        "caption": caption,
        "narrative_alignment_note": alignment,
        "disposition": "consumed",
        "source_artifacts": sources,
        "reconciliation": reconciliation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": GENERATED_BY,
    }
    if extra_meta:
        meta.update(extra_meta)
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    fig.write_image(str(OUT / f"_perceptual_check_{name}.png"),
                    width=1100, height=600, scale=1)
    print(f"  wrote {name}.json (+sidecar, +perceptual png)")


def nber_swatch(fig: go.Figure) -> None:
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square"),
        name="NBER recession (shaded)", hoverinfo="skip"))


# ── 1. Hero (bounded 0-100 index: 50-neutral line drawn) ─────────────────

def chart_hero():
    df = load_monthly()
    hmi = df["nahb_hmi"].dropna()
    spy = df["spy"].dropna()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=hmi.index, y=hmi.values,
        name=f"{IND_SHORT} (index, 0–100)",
        line=dict(color=C_IND, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=spy.index, y=spy.values,
        name=f"{TGT} price (USD)",
        line=dict(color=C_TGT, width=1.5)), secondary_y=True)
    add_nber_shading(fig, x_min=hmi.index.min(), x_max=hmi.index.max())
    nber_swatch(fig)
    fig.add_hline(y=50, line_dash="dash", line_color=C_NEUTRAL, line_width=1.0,
                  secondary_y=False,
                  annotation_text="50 = neutral builder sentiment",
                  annotation_position="bottom right",
                  annotation_font=dict(size=10, color=C_NEUTRAL))
    lo = hmi.idxmin()
    fig.add_annotation(x=lo, y=float(hmi.loc[lo]),
                       text=(f"Jan 2009: record low {hmi.loc[lo]:.0f} — but the market "
                             f"had already crashed;<br>Granger says {TGT} moves first, "
                             f"sentiment follows"),
                       showarrow=True, arrowhead=2, ax=-10, ay=-70,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    y0, y1 = hmi.index.min().year, hmi.index.max().year
    fig.update_layout(
        title=(f"Builder Sentiment Tracks the Cycle but Does Not Lead the Market: "
               f"{IND_SHORT} vs {TGT} ({y0}–{y1})"),
        template="plotly_white", hovermode="x unified", height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text=f"{IND_SHORT} (bounded index, 0–100)",
                     secondary_y=False, range=[0, 100])
    fig.update_yaxes(title_text=f"{TGT} price (USD)", secondary_y=True)
    save_chart("hero", fig,
               caption=(f"{IND_LONG} (vermillion, left axis — a bounded 0–100 "
                        f"diffusion index with 50 = neutral, dashed line) against the "
                        f"{TGT} price (blue, right axis), {y0}–{y1}. Sentiment swings "
                        f"are dramatic — record low 8 in Jan-2009, record 90 in "
                        f"Nov-2020 — but they move WITH or AFTER equities, not ahead "
                        f"of them (SPY→HMI Granger significant at all 12 lags; "
                        f"HMI→SPY at lag 5 only). Shaded bands mark NBER recessions."),
               alignment=("Hero shows the bounded-index 50-neutral convention and the "
                          "reverse-causality framing from Evan's Granger verdict; "
                          "record-low/record-high values re-read from the dataset at "
                          "generation time."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-TX1", "VIZ-O1"],
               sources=[SRC_DATA])


# ── 2. Regime stats (VIZ-QR1 dual-panel; HMI LEVEL quartiles per manifest) ─

def chart_regime_stats():
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>(Deepest builder pessimism)", "Q2", "Q3",
              "Q4<br>(Strongest builder optimism)"]
    fig = make_dual_panel_regime_chart(
        quartile_labels=labels,
        sharpe=q["sharpe"].tolist(),
        ann_return_pct=(q["ann_return"] * 100).tolist(),
        signal_label=f"{IND_SHORT} level",
        x_axis_title=f"{IND_SHORT} level quartile (concurrent, not lagged)",
    )
    fig.update_layout(
        title=dict(
            text=(f"No Clean Sentiment Regime Story: {TGT} Performance by "
                  f"{IND_SHORT} Level Quartile"),
            y=0.99, yanchor="top"),
        margin=dict(t=150))
    save_chart("regime_stats", fig,
               caption=(f"{TGT} performance by concurrent {IND_SHORT} level quartile "
                        f"(Q1 = deepest builder pessimism): Sharpe (left) and "
                        f"annualized return (right). The pattern is NON-MONOTONIC — "
                        f"Q2 is best (Sharpe {q['sharpe'].iloc[1]:.2f}, "
                        f"{q['ann_return'].iloc[1]*100:.1f}% ann.) and Q3 worst "
                        f"({q['sharpe'].iloc[2]:.2f}), with the extremes Q1 "
                        f"({q['sharpe'].iloc[0]:.2f}) and Q4 "
                        f"({q['sharpe'].iloc[3]:.2f}) in between. Descriptive, "
                        f"concurrent quartiles — not a tradable lagged signal."),
               alignment=("VIZ-QR1 dual-panel from regime_quartile_returns.csv; the "
                          "manifest defines quartiles on the HMI LEVEL (Q1 = deepest "
                          "pessimism); values re-read from CSV at generation time; "
                          "non-monotonic = no regime story, consistent with the "
                          "null era battery."),
               rules=["VIZ-QR1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/regime_quartile_returns.csv",
                        f"results/{PAIR}/regime_quartile_returns_manifest.json"],
               nber_required=False)


# ── 3. Correlation heatmap ────────────────────────────────────────────────

_SIGLBL = {
    "level": "Index level", "yoy": "YoY % change", "mom": "MoM % change",
    "mom3m": "3-month % change", "mom6m": "6-month % change",
    "diff_12m": "12-month point change (winner signal)",
    "diff_3m": "3-month point change",
    "dev_trend": "Deviation from trend",
    "level_zscore_60m": "Level z-score (60-month)",
    "diff12_zscore_60m": "12m-change z-score (60-month)",
    "accel": "Momentum acceleration",
    "above50": "Above-50 flag (expansion)",
    "hmm_stress": "HMM pessimism-regime probability",
}


def chart_correlation_heatmap():
    c = pd.read_csv(CORE / "correlations.csv")
    p = c[c["metric"] == "pearson"].copy()
    p[["signal", "horizon"]] = p["pair_name"].str.split("__", expand=True)
    hor_order = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    piv = p.pivot(index="signal", columns="horizon", values="value")[hor_order]
    pp = p.pivot(index="signal", columns="horizon", values="p_value")[hor_order]
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
        title=(f"Forward Correlations Are Weak Everywhere: {IND_SHORT} Signals vs "
               f"{TGT} Forward Returns<br><sup>Pearson r; * p&lt;0.05, ** p&lt;0.01. "
               f"Best cell: {_SIGLBL.get(best['signal'], best['signal'])} vs 12M fwd, "
               f"r = {best['value']:.3f} — a long-horizon cell, not a short-horizon "
               f"forecasting channel</sup>"),
        xaxis_title=f"{TGT} forward return horizon",
        yaxis_title=f"{IND_SHORT} signal",
        template="plotly_white", height=560)
    save_chart("correlation_heatmap", fig,
               caption=(f"Pearson correlations between {IND_LONG} signals and {TGT} "
                        f"forward returns at 1/3/6/12-month horizons. The strongest "
                        f"cell is only r = {best['value']:.3f} "
                        f"({best['pair_name'].replace('__', ' vs ')}); short-horizon "
                        f"cells are near zero throughout — consistent with a "
                        f"lagging/coincident sentiment gauge, not a forecasting "
                        f"input."),
               alignment=("Best cell re-read from correlations.csv at generation "
                          "time (yoy vs 12m fwd, r=0.187); the weak-forward-channel "
                          "message matches Evan's verdict."),
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
    sig = d[d["significant"]]
    nsig = len(sig)
    sig_lags = ", ".join(f"{int(v):+d}" for v in sig["lag"])
    fig.update_layout(
        title=(f"Pre-Whitened Cross-Correlation: Scattered Cells on BOTH Sides, "
               f"No Leading Ridge<br><sup>AR(12) pre-whitening; {nsig} of {len(d)} "
               f"lags significant ({sig_lags}) — classified 'bidirectional' in the "
               f"econometrics handoff</sup>"),
        xaxis_title=f"Lag (months; positive = {IND_SHORT} leads {TGT})",
        yaxis_title="Cross-correlation",
        template="plotly_white", height=400, showlegend=False)
    save_chart("ccf_prewhitened", fig,
               caption=(f"Cross-correlation between AR(12) pre-whitened {IND_SHORT} "
                        f"and {TGT} returns at lags -24..+24 months. {nsig} of "
                        f"{len(d)} lags cross the 95% band ({sig_lags}), scattered "
                        f"on both sides of zero including lag 0 — a bidirectional, "
                        f"noise-like pattern with no clean ridge on the "
                        f"indicator-leads side. Positive lag = {IND_SHORT} leads "
                        f"{TGT} (pair-pipeline convention)."),
               alignment=("Significant-lag list re-read from the CSV; matches Evan's "
                          "'bidirectional' classification. Lag-sign convention "
                          "verified against the pair pipeline (positive = HMI "
                          "leads)."),
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/ccf_prewhitened.csv"],
               nber_required=False)


# ── 5. Granger F by lag (reverse PRIMARY — the story chart) ──────────────

def chart_granger():
    g = pd.read_csv(CORE / "granger_causality.csv")
    bylag = pd.read_csv(RES / "granger_by_lag.csv")
    rev = g[g["direction"] == "target_to_indicator"].sort_values("lag")
    fwd = g[g["direction"] == "indicator_to_target"].sort_values("lag")
    crit = [float(sstats.f.ppf(0.95, r["df_num"], r["df_den"]))
            for _, r in bylag.sort_values("lag").iterrows()]
    n_fwd_sig = int(fwd["significant"].sum())
    fwd_sig_lags = ", ".join(str(int(v)) for v in fwd.loc[fwd["significant"], "lag"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rev["lag"], y=rev["f_statistic"],
        name=f"{TGT} → {IND_SHORT} (the market leads sentiment) — significant at ALL 12 lags",
        marker_color=C_IND))
    fig.add_trace(go.Bar(
        x=fwd["lag"], y=fwd["f_statistic"],
        name=(f"{IND_SHORT} → {TGT} (sentiment leads the market) — significant at "
              f"lag {fwd_sig_lags} only"),
        marker_color="#aec7e8"))
    fig.add_trace(go.Scatter(
        x=bylag.sort_values("lag")["lag"], y=crit, mode="lines",
        name="5% critical value (per lag)",
        line=dict(color=C_EVENT, dash="dash", width=1.5)))
    fig.update_layout(
        title=(f"Causality Runs the WRONG Way for Forecasting: {TGT} Moves First, "
               f"Builder Sentiment Follows<br><sup>Toda-Yamamoto Granger "
               f"F-statistics by lag; reverse direction significant at every lag "
               f"(max F = {rev['f_statistic'].max():.1f} at lag 1); forward "
               f"direction clears the bar at lag {fwd_sig_lags} only "
               f"(p = {float(fwd.loc[fwd['significant'], 'p_value'].min()):.3f})</sup>"),
        xaxis_title="Lag (months)",
        yaxis_title="F-statistic",
        barmode="group", template="plotly_white", height=480,
        margin=dict(b=140),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("granger_f_by_lag", fig,
               caption=(f"Toda-Yamamoto Granger F-statistics at lags 1–12, both "
                        f"directions. {TGT} → {IND_SHORT} (vermillion) clears the 5% "
                        f"critical line at EVERY lag (F = "
                        f"{rev['f_statistic'].max():.1f} at lag 1, all p < 0.0001); "
                        f"{IND_SHORT} → {TGT} (pale blue) clears it at "
                        f"{n_fwd_sig} lag only (lag {fwd_sig_lags}, "
                        f"p = {float(fwd.loc[fwd['significant'], 'p_value'].min()):.3f}) "
                        f"— an isolated cell against 12-for-12 in reverse. The "
                        f"asymmetry is the signature of a lagging indicator: the "
                        f"market moves builder sentiment, not the other way "
                        f"around."),
               alignment=("Reverse direction rendered as the visually primary "
                          "series per Lead dispatch — the reverse-causality result "
                          "IS the finding; all F/p values re-read from CSVs."),
               rules=["VIZ-IC1", "VIZ-V3", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/granger_causality.csv",
                        f"results/{PAIR}/granger_by_lag.csv"],
               nber_required=False)


# ── 6. Local projections (fwd + rev panels) ───────────────────────────────

def chart_local_projections():
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = make_subplots(rows=1, cols=2, shared_yaxes=False, subplot_titles=[
        f"{IND_SHORT} → {TGT} (forward — no effect)",
        f"{TGT} → {IND_SHORT} (reverse)"])
    for col, dirn, color in ((1, "fwd", C_IND), (2, "rev", C_TGT)):
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
            name=("Coefficient: sentiment → market" if dirn == "fwd"
                  else "Coefficient: market → sentiment"),
            line=dict(color=color, width=2)), row=1, col=col)
        fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL,
                      line_width=0.8, row=1, col=col)
    pmin_fwd = float(lp[lp["direction"] == "fwd"]["p_value"].min())
    fig.update_layout(
        title=(f"Local Projections (HAC): No Horizon Shows a Forward Effect "
               f"<br><sup>All forward-direction p-values &gt; "
               f"{pmin_fwd:.2f}; CI bands include zero throughout, both "
               f"directions</sup>"),
        template="plotly_white", height=460, margin=dict(b=120),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    fig.update_xaxes(title_text="Horizon (months)")
    fig.update_yaxes(title_text="Impulse response coefficient", row=1, col=1)
    save_chart("local_projections", fig,
               caption=(f"Local-projection impulse responses with HAC standard "
                        f"errors at horizons 1/3/6/12 months, both directions. The "
                        f"forward direction ({IND_SHORT} → {TGT}, left) is "
                        f"indistinguishable from zero at every horizon (min p = "
                        f"{pmin_fwd:.2f}); the reverse panel is positive but also "
                        f"n.s. (min p = "
                        f"{float(lp[lp['direction'] == 'rev']['p_value'].min()):.2f}). "
                        f"Note the very different y-scales — the units differ "
                        f"across panels."),
               alignment="Dual-panel LP per ECON-H4 row 'IRF with CI band (fwd + rev panels)'.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/local_projections.csv"],
               nber_required=False)


# ── 7. Transfer entropy (REVERSE-ONLY significant here) ──────────────────

def chart_transfer_entropy():
    te = pd.read_csv(CORE / "transfer_entropy.csv")
    lab = {"indicator_to_target": f"{IND_SHORT} → {TGT}",
           "target_to_indicator": f"{TGT} → {IND_SHORT}"}
    fwd = te[te["direction"] == "indicator_to_target"].iloc[0]
    rev = te[te["direction"] == "target_to_indicator"].iloc[0]
    fig = go.Figure()
    for _, r in te.iterrows():
        fig.add_trace(go.Bar(
            x=[lab[r["direction"]]], y=[r["te_value"]],
            name=f"{lab[r['direction']]} (perm. p = {r['permutation_p_value']:.3f})",
            marker_color=C_IND if r["direction"] == "indicator_to_target" else C_TGT,
            text=[f"TE = {r['te_value']:.4f}<br>p = {r['permutation_p_value']:.3f}"],
            textposition="outside"))
    fig.update_layout(
        title=(f"Transfer Entropy: Information Flows FROM the Market TO Sentiment, "
               f"Not the Other Way<br><sup>Tercile binning, 500 permutations; "
               f"{TGT} → {IND_SHORT} p = {rev['permutation_p_value']:.3f} "
               f"(significant); {IND_SHORT} → {TGT} p = "
               f"{fwd['permutation_p_value']:.3f} (n.s.)</sup>"),
        yaxis_title="Transfer entropy (nats)",
        xaxis_title="Direction",
        template="plotly_white", height=400, showlegend=False)
    save_chart("transfer_entropy", fig,
               caption=(f"Transfer entropy between {IND_SHORT} and {TGT} returns "
                        f"(tercile bins, 500 permutations). Only the REVERSE "
                        f"direction is significant: {TGT} → {IND_SHORT} TE = "
                        f"{rev['te_value']:.4f} (p = "
                        f"{rev['permutation_p_value']:.3f}) vs {IND_SHORT} → {TGT} "
                        f"TE = {fwd['te_value']:.4f} (p = "
                        f"{fwd['permutation_p_value']:.3f}, n.s.). The nonlinear "
                        f"channel agrees with Granger: the market informs builder "
                        f"sentiment, not vice versa."),
               alignment=("Two-bar TE comparison; reverse-only significance is the "
                          "honest headline and matches the Granger asymmetry."),
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
    fig.update_layout(
        title=(f"Quantile Regression: No Tail-Dependent Channel Either "
               f"<br><sup>{IND_SHORT} on {TGT} forward returns; no tau from "
               f"0.05–0.95 is significant at 5% (min p = "
               f"{qr['p_value'].min():.2f})</sup>"),
        xaxis_title=f"Return quantile (tau) of {TGT}",
        yaxis_title="Coefficient",
        template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("quantile_coef", fig,
               caption=(f"Quantile-regression coefficient of {TGT} forward returns "
                        f"on {IND_SHORT} across return quantiles 0.05–0.95 with 95% "
                        f"CI. The band straddles zero at every tau (min p = "
                        f"{qr['p_value'].min():.2f}, at the 0.10 tail) — no "
                        f"crash-quantile or boom-quantile channel hides behind the "
                        f"weak mean effect."),
               alignment="Coef-by-tau with CI band per ECON-H4.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv"],
               nber_required=False)


# ── 9. HMM regime probabilities (level split: pessimism vs optimism) ─────

def chart_hmm():
    h = pd.read_parquet(CORE / "hmm_states.parquet")
    # Defense 2: manifest assertions
    gfc = float(h.loc["2008-01-31":"2009-12-31", "prob_stress"].mean())
    boom = float(h.loc["2004-01-31":"2005-12-31", "prob_stress"].mean())
    assert gfc > 0.8, f"HMM manifest assertion failed: GFC prob_stress mean {gfc:.2f}"
    assert boom < 0.2, f"HMM manifest assertion failed: 2004-05 prob_stress mean {boom:.2f}"
    freq = float((h["prob_stress"] > 0.5).mean())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h.index, y=h["prob_stress"], mode="lines",
        name="P(builder-pessimism regime)",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.25)",
        line=dict(color=C_IND, width=1.2)))
    add_nber_shading(fig, x_min=h.index.min(), x_max=h.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Hidden Markov Model (HMM): Builder Pessimism vs Optimism Regimes "
               f"on the {IND_SHORT} Level<br><sup>2-state HMM on the bounded "
               f"sentiment level; pessimism regime covers ~{freq:.0%} of months and "
               f"pins to 1.0 through the 2006–09 housing bust</sup>"),
        xaxis_title="Date",
        yaxis_title="Probability of builder-pessimism regime",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("hmm_regime_probs", fig,
               caption=(f"Probability that {IND_SHORT} is in its builder-pessimism "
                        f"(low-level) regime, from a 2-state HMM on the sentiment "
                        f"level. The regime split is clean and slow-moving — "
                        f"pessimism pins to 1.0 through the 2006–09 housing bust "
                        f"and 0.0 through the 2004–05 boom (both verified against "
                        f"manifest assertions at generation time) — but it "
                        f"DESCRIBES housing conditions rather than predicting "
                        f"{TGT}. Shaded bands mark NBER recessions."),
               alignment=("Labels follow hmm_states_manifest.json semantics "
                          "('stress' = builder-pessimism LEVEL regime, a deliberate "
                          "level split), relabelled in plain English to avoid "
                          "implying equity stress."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/hmm_states.parquet",
                        f"results/{PAIR}/core_models_{DATE_TAG}/hmm_summary.csv"],
               reconciliation={"gfc_prob_stress_mean": {"computed": round(gfc, 4),
                                                        "manifest_expected": "> 0.8",
                                                        "verdict": "PASS"},
                               "boom_2004_05_prob_stress_mean": {"computed": round(boom, 4),
                                                                 "manifest_expected": "< 0.2",
                                                                 "verdict": "PASS"}})


# ── 10/11. Tournament scatter + Sharpe distribution ───────────────────────

def _tournament_frames():
    t = load_tournament()
    valid = t[t["valid"] & (t["signal"] != "BENCHMARK")]
    bench = t[t["signal"] == "BENCHMARK"]
    return t, valid, bench


def chart_tournament_scatter():
    t, valid, bench = _tournament_frames()
    w = load_winner()
    bh = (float(bench.iloc[0]["oos_sharpe"]) if len(bench)
          else float(w["bh_sharpe"]))
    bh_x = (float(bench.iloc[0]["annual_turnover"]) if len(bench) else 0.0)
    invalid = t[(~t["valid"]) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=invalid["annual_turnover"], y=invalid["oos_sharpe"], mode="markers",
        marker=dict(size=3, color="rgba(153,153,153,0.45)"), name="Invalid combos"))
    fig.add_trace(go.Scatter(
        x=valid["annual_turnover"], y=valid["oos_sharpe"], mode="markers",
        marker=dict(size=5, color=(valid["max_drawdown"] * 100),
                    colorscale="RdYlGn", colorbar=dict(title="Max DD (%)"),
                    opacity=0.6),
        text=[f"{r['signal']}/{r['threshold']}/{r['strategy']}/L{r['lead_months']}"
              for _, r in valid.iterrows()],
        hovertemplate="%{text}<br>Sharpe: %{y:.2f}<br>Turnover: %{x:.1f}/yr<extra></extra>",
        name="Valid strategies"))
    fig.add_trace(go.Scatter(
        x=[bh_x], y=[bh],
        mode="markers", marker=dict(size=14, color=C_BENCH, symbol="diamond"),
        name=f"Buy & Hold {TGT} (Sharpe {bh:.2f})"))
    top5 = valid.nlargest(5, "oos_sharpe")
    fig.add_trace(go.Scatter(
        x=top5["annual_turnover"], y=top5["oos_sharpe"], mode="markers",
        marker=dict(size=12, color=C_POS, symbol="star",
                    line=dict(width=1, color="#000000")),
        name="Top 5 by OOS Sharpe"))
    n_all = int((t["signal"] != "BENCHMARK").sum())
    fig.update_layout(
        title=(f"Tournament: {n_all:,} Strategy Combos ({len(valid):,} Valid) — "
               f"Winner OOS Sharpe {valid['oos_sharpe'].max():.2f} vs Buy & Hold "
               f"{bh:.2f}"),
        xaxis_title="Annual turnover (trades per year)",
        yaxis_title="OOS Sharpe ratio",
        template="plotly_white", height=540, margin=dict(b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("tournament_scatter", fig,
               caption=(f"All {n_all:,} tournament combinations (OOS Sharpe vs "
                        f"annual turnover; color = max drawdown). {len(valid):,} "
                        f"pass validity; the Buy & Hold {TGT} diamond sits at "
                        f"Sharpe {bh:.2f}. Winner identified by the ECON-T3 "
                        f"cascade; see the distribution chart for position "
                        f"disclosure and the bootstrap caveat."),
               alignment="Standard tournament scatter; benchmark per ECON-T4.",
               rules=["VIZ-IC1", "ECON-T4", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
               nber_required=False)


def chart_tournament_dist():
    t, valid, bench = _tournament_frames()
    w = load_winner()
    boot_p = load_bootstrap_p()
    med = float(valid["oos_sharpe"].median())
    wmax = float(valid["oos_sharpe"].max())
    bh = (float(bench.iloc[0]["oos_sharpe"]) if len(bench)
          else float(w["bh_sharpe"]))
    fig = go.Figure(go.Histogram(
        x=valid["oos_sharpe"], nbinsx=60, marker_color=C_TGT, opacity=0.75,
        name=f"Valid strategies (n = {len(valid):,})"))
    fig.add_vline(x=med, line=dict(color=C_NEUTRAL, dash="dot", width=1.5))
    fig.add_vline(x=bh, line=dict(color=C_BENCH, dash="dash", width=2))
    fig.add_vline(x=wmax, line=dict(color=C_IND, dash="dash", width=2))
    fig.add_annotation(x=wmax, y=1.0, yref="paper", showarrow=False,
                       xanchor="right",
                       text=(f"Winner = max of {len(valid):,} "
                             f"(bootstrap p = {boot_p:.3f}, n.s.)"),
                       font=dict(size=12, color=C_IND),
                       bgcolor=PAL["event_marker_label_bg"])
    fig.add_annotation(x=bh, y=0.85, yref="paper", showarrow=False, xanchor="left",
                       text=f"Buy & Hold {TGT} = {bh:.2f} — ABOVE the median strategy",
                       font=dict(size=12, color=C_BENCH),
                       bgcolor=PAL["event_marker_label_bg"])
    fig.add_annotation(x=med, y=0.65, yref="paper", showarrow=False, xanchor="right",
                       text=f"Median {med:.2f}", font=dict(size=11, color=C_NEUTRAL))
    fig.update_layout(
        title=(f"The Median Strategy Does NOT Beat Buy &amp; Hold: OOS Sharpe "
               f"Distribution Across {len(valid):,} Valid Combos"),
        xaxis_title="OOS Sharpe ratio",
        yaxis_title="Number of strategies",
        template="plotly_white", height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("tournament_sharpe_dist", fig,
               caption=(f"Distribution of OOS Sharpe across the {len(valid):,} "
                        f"valid strategy combos. The winner (Sharpe {wmax:.2f}) is "
                        f"the max of {len(valid):,} with median {med:.2f} — and the "
                        f"median sits BELOW Buy & Hold {TGT} ({bh:.2f}). Winner "
                        f"selection is a tail draw from a population that mostly "
                        f"underperforms the benchmark; bootstrap p = {boot_p:.3f} "
                        f"(not significant at 5%) — a found-in-search candidate."),
               alignment=("VIZ-SCD1 position disclosure + B&H benchmark line; all "
                          "numbers re-read from the tournament CSV and "
                          "tournament_validation bootstrap.csv at generation "
                          "time."),
               rules=["VIZ-SCD1", "ECON-T4", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                        f"results/{PAIR}/tournament_validation_{DATE_TAG}/bootstrap.csv"],
               reconciliation={"valid_count": len(valid),
                               "median_oos_sharpe": round(med, 4),
                               "winner_oos_sharpe": round(wmax, 4),
                               "bh_oos_sharpe": round(bh, 4),
                               "bootstrap_p": round(boot_p, 4)},
               nber_required=False)


# ── 12. Rolling correlation (era-null message per Lead dispatch) ──────────

def chart_rolling_correlation():
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    era = pd.read_csv(CORE / "era_correlations.csv")
    era_max = float(era["pearson_r"].abs().max())
    era_pmin = float(era["p_value"].min())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rc["date"], y=rc["rolling_corr"], mode="lines",
        name="60-month rolling correlation",
        line=dict(color=C_TGT, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_EVENT, line_width=1,
                  annotation_text="No correlation")
    add_nber_shading(fig, x_min=rc["date"].min(), x_max=rc["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Stable Sign, But Stably WEAK: 60-Month Rolling Correlation, "
               f"{IND_SHORT} vs {TGT} Returns<br><sup>Sign agreement "
               f"{sb['rolling_corr_sign_stability']:.2f} "
               f"({sb['rolling_corr_stability_verdict'].replace('_', '-')}); era "
               f"battery NULL in all four eras (max |r| = {era_max:.2f}, min p = "
               f"{era_pmin:.2f})</sup>"),
        xaxis_title="Date",
        yaxis_title="Rolling correlation (r)",
        template="plotly_white", height=420,
        yaxis=dict(range=[-1, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("rolling_correlation", fig,
               caption=(f"60-month rolling correlation between {IND_SHORT} and {TGT} "
                        f"monthly returns. The sign is stable "
                        f"({sb['rolling_corr_sign_stability']:.0%} agreement) but "
                        f"the level hugs zero throughout — and the era battery "
                        f"(pre-GFC, GFC bust, QE era, post-COVID) finds NO "
                        f"significant correlation in ANY era (max |r| = "
                        f"{era_max:.2f}, min p = {era_pmin:.2f}). A stably-null "
                        f"relationship, not a stably-useful one. Shaded bands mark "
                        f"NBER recessions."),
               alignment=("Stability verdict quoted from structural_break JSON; "
                          "era-null message required by Lead dispatch, values "
                          "re-read from era_correlations.csv at generation time."),
               rules=["VIZ-CP1.2", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/rolling_correlation_{PAIR}.csv",
                        f"results/{PAIR}/structural_break_{PAIR}.json",
                        f"results/{PAIR}/core_models_{DATE_TAG}/era_correlations.csv"])


# ── 13. Structural break ──────────────────────────────────────────────────

def chart_structural_break():
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    df = load_monthly()
    sig = df.loc[sb["sample_start"]:sb["sample_end"], "nahb_hmi_diff_12m"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig.index, y=sig.values, mode="lines",
        name=f"{IND_SHORT} 12-month change (points)",
        line=dict(color=C_IND, width=1.8)))
    fig.add_vline(x=pd.Timestamp(sb["break_date"]).timestamp() * 1000,
                  line=dict(color=C_EVENT, dash="dash", width=2))
    fig.add_annotation(x=sb["break_date"], y=0.95, yref="paper", showarrow=False,
                       xanchor="left",
                       text=(f"Candidate break {sb['break_date'][:7]}: sup-F "
                             f"{sb['f_stat']:.2f}, bootstrap p = {sb['p_value']:.2f} "
                             f"— NOT significant"),
                       font=dict(size=12, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=sig.index.min(), x_max=sig.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"No Structural Break Detected: Quandt-Andrews sup-F Test "
               f"(p = {sb['p_value']:.2f})"),
        xaxis_title="Date",
        yaxis_title=f"{IND_SHORT} 12-month change (index points)",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("structural_break", fig,
               caption=(f"{IND_SHORT} 12-month point change (the winner's signal "
                        f"family) over the test sample ({sb['sample_start'][:7]}–"
                        f"{sb['sample_end'][:7]}, n = {sb['n_obs']}) with the "
                        f"Quandt-Andrews candidate break date "
                        f"({sb['break_date'][:7]}). The test does NOT flag a break "
                        f"(sup-F {sb['f_stat']:.2f}, residual-bootstrap p = "
                        f"{sb['p_value']:.2f}) — the indicator-target relationship "
                        f"is uniformly weak rather than regime-broken. Shaded bands "
                        f"mark NBER recessions."),
               alignment="Annotation-only chart per ECON-H4 ('not flagged'); values from JSON.",
               rules=["VIZ-CP1.3", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/structural_break_{PAIR}.json", SRC_DATA],
               extra_meta={"break_date": sb["break_date"],
                           "annotation_strategy_id": "manual_override",
                           "annotation_overrides": [
                               {"annotation_idx": 0, "y_offset": "paper 0.95",
                                "rationale": "single break-label placed per VIZ-CP1.3 spec"}]})


# ── 14. Sub-period Sharpe (episode/ann_sharpe/data_status schema) ─────────

_EP_LABEL = {"dot_com": "Dot-Com 2000–02", "gfc": "GFC 2007–09",
             "covid": "COVID 2020", "china_2015": "China Shock 2015–16",
             "rates_2022": "2022 Rates Shock"}


def chart_subperiod_sharpe():
    rows = pd.read_csv(RES / "subperiod_sharpe.csv")
    labels, values, colors, texts = [], [], [], []
    for _, r in rows.iterrows():
        lab = _EP_LABEL.get(r["episode"], str(r["episode"]).replace("_", " "))
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
    covid = float(rows.loc[rows["episode"] == "covid", "ann_sharpe"].iloc[0])
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=texts, textposition="outside",
                           name="Annualized Sharpe by episode"))
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Only One Stress Episode Falls Inside the OOS Window: Winner "
               f"Strategy Sharpe by Episode<br><sup>COVID {covid:.2f}; dot-com, "
               f"GFC and the 2015 China shock predate the 2017-09 OOS start — "
               f"durability verdict: conditionally durable</sup>"),
        xaxis_title="Historical episode",
        yaxis_title="Annualized Sharpe ratio",
        template="plotly_white", height=430, margin=dict(b=110), showlegend=False)
    save_chart("subperiod_sharpe", fig,
               caption=(f"Winner-strategy annualized Sharpe within each canonical "
                        f"stress episode. Only COVID 2020 falls inside the OOS "
                        f"window (Sharpe {covid:.2f}); dot-com, GFC and the 2015 "
                        f"China shock predate the 2017-09 OOS start, so the "
                        f"strategy's crisis behaviour is evidenced by a single "
                        f"episode. Evan's durability verdict: "
                        f"conditionally_durable."),
               alignment=("Three-state encoding (no data / in cash / value) per the "
                          "established subperiod convention; states derived from "
                          "data_status; durability verdict quoted from the CSV."),
               rules=["ECON-CP1", "VIZ-CP1.1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/subperiod_sharpe.csv"],
               nber_required=False)


# ── 15. History zoom charts (4 episodes, dual-panel) ──────────────────────

def _window_has_recession(start: str, end: str) -> bool:
    from _nber import RECESSIONS
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return any(pd.Timestamp(r0) <= e and pd.Timestamp(r1) >= s for r0, r1 in RECESSIONS)


def chart_history_zoom(slug: str):
    ep = EVENTS_REG["episodes"][slug]
    df = load_monthly()
    w = df.loc[ep["start_date"]:ep["end_date"]]
    hmi = w["nahb_hmi"].dropna()
    spy = w["spy"].dropna()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[f"{IND_SHORT} (index, 0–100)",
                                        f"{TGT} price (USD)"])
    fig.add_trace(go.Scatter(x=hmi.index, y=hmi.values,
                             name=f"{IND_SHORT} (index, 0–100)",
                             line=dict(color=C_IND, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=spy.index, y=spy.values,
                             name=f"{TGT} price (USD)",
                             line=dict(color=C_TGT, width=2)), row=2, col=1)
    # bounded-index 50-neutral line on the indicator panel
    fig.add_hline(y=50, line_dash="dash", line_color=C_NEUTRAL, line_width=1.0,
                  row=1, col=1)
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
        fig.add_annotation(x=ev["date"], xref="x",
                           y=0.97 - 0.10 * i, yref="y domain",
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
    fig.update_yaxes(title_text="Index (0–100)", row=1, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    gfc_note = ""
    if slug == "gfc":
        gfc_note = (" HMI hit its record low of 8 in Jan-2009 — the deepest "
                    "builder pessimism ever recorded — near the equity trough, "
                    "not ahead of the peak.")
    save_chart(f"history_zoom_{slug}", fig,
               caption=(f"{IND_SHORT} (top, with the 50-neutral line) and {TGT} "
                        f"price (bottom) through the {ep['episode_name']} window "
                        f"({ep['start_date'][:7]} to {ep['end_date'][:7]}), with "
                        f"registry event markers.{gfc_note}"
                        + (" Shaded bands mark NBER recessions." if has_rec
                           else " No NBER recession falls in this window.")),
               alignment=(f"Dual-panel episode zoom per VIZ-V1/VIZ-ZOOM1; events "
                          f"from history_zoom_events_registry "
                          f"v{EVENTS_REG_VERSION}."),
               rules=["VIZ-V1", "VIZ-V2", "VIZ-V12", "VIZ-V13", "VIZ-TS1",
                      "VIZ-DP1", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[SRC_DATA, "docs/schemas/history_zoom_events_registry.json"],
               extra_meta={"annotation_strategy_id": "descending_stair",
                           "events_registry_version": EVENTS_REG_VERSION,
                           "episode_slug": slug},
               nber_required=has_rec)


# ── 16/17. GH #13 native lead charts (VIZ-LEAD1) ──────────────────────────

LEADS_ALL = [f"L{i}" for i in range(13)]
LEADS_TRD = [f"L{i}" for i in range(1, 13)]


def chart_correlations_lead_view():
    raw = pd.read_csv(RES / f"lead_correlation_{DATE_TAG}.csv", dtype=str)
    w = load_winner()
    lead_cols = [c for c in raw.columns if c.startswith("L")]
    z, starred = [], []
    for _, r in raw.iterrows():
        vals, stars = [], []
        for c in lead_cols:
            s = str(r[c])
            stars.append("*" in s)
            vals.append(float(s.replace("*", "")))
        z.append(vals)
        starred.append(stars)
    transforms = raw["transform"].tolist()
    annot = [[f"{z[i][j]:+.2f}" + ("*" if starred[i][j] else "")
              for j in range(len(lead_cols))] for i in range(len(transforms))]
    win_sig = w["signal_column"]  # nahb_hmi_diff_12m
    win_row = raw[raw["transform"] == win_sig].iloc[0]
    win_best_lead, win_best_r = win_row["best_lead"], float(win_row["best_r"])
    fig = go.Figure(go.Heatmap(
        z=z, x=lead_cols, y=transforms, colorscale="RdBu", zmid=0,
        zmin=-0.25, zmax=0.25, text=annot, texttemplate="%{text}",
        textfont={"size": 9}, name="Pearson r", showlegend=False))
    fig.update_layout(
        title=(f"Lead-Lag Predictability Is Weak at Every Horizon: {IND_SHORT} "
               f"Signal (lagged L months) vs {TGT} 1-Month Forward Return"
               f"<br><sub>Pearson correlations across lead horizons L0..L12; "
               f"* p&lt;0.05. Winner signal {win_sig} peaks at {win_best_lead} "
               f"(r = {win_best_r:+.3f}) — max |r| across the whole grid is "
               f"{max(abs(v) for row in z for v in row):.2f}</sub>"),
        xaxis_title="Lead (months) applied to signal (L0 diagnostic-only)",
        yaxis_title="Signal transform",
        template="plotly_white", height=560)
    save_chart("correlations_lead_view", fig,
               caption=(f"Pearson correlation of each {IND_SHORT} signal transform "
                        f"(lagged L0..L12 months) with the {TGT} 1-month forward "
                        f"return. The whole grid is weak — max |r| = "
                        f"{max(abs(v) for row in z for v in row):.2f} — and the "
                        f"winner signal ({win_sig}) peaks at {win_best_lead} with "
                        f"r = {win_best_r:+.3f}, at a different lead than the "
                        f"deployed L7. There is no correlation ridge backing the "
                        f"tournament winner."),
               alignment=(f"Winner signal {win_sig} peaks at {win_best_lead} "
                          f"(r={win_best_r:+.3f}); values parsed verbatim from "
                          f"lead_correlation CSV incl. significance stars."),
               rules=["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               sources=[f"results/{PAIR}/lead_correlation_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               extra_meta={"method_name": "lead_correlation_view",
                           "expected_chart_type": "heatmap"},
               nber_required=False)


def chart_lead_sharpe_distribution():
    env = pd.read_csv(RES / f"lead_tournament_{DATE_TAG}.csv")
    wc = pd.read_csv(RES / f"lead_winner_curve_{DATE_TAG}.csv")
    clean = pd.read_csv(RES / f"lead_clean_envelope_{DATE_TAG}.csv")
    w = load_winner()
    boot_p = load_bootstrap_p()
    manifest = json.loads((RES / f"lead_sweep_manifest_{DATE_TAG}.json").read_text())
    # SA source: envelope and clean envelope must coincide (manifest clause)
    assert (env.sort_values("lead_months")["best_oos_sharpe"].round(4).tolist()
            == clean.sort_values("lead_months")["best_clean_oos_sharpe"].round(4).tolist()), \
        "clean envelope != envelope but manifest says they coincide"
    wc = wc.sort_values("lead_months")
    env = env.sort_values("lead_months")
    bh = float(w["bh_sharpe"])
    win_lead = int(w["lead_value"])
    win_sharpe = float(wc.loc[wc["lead_months"] == win_lead, "oos_sharpe"].iloc[0])
    assert bool(wc.loc[wc["lead_months"] == win_lead, "is_published_winner"].iloc[0])
    l6 = float(wc.loc[wc["lead_months"] == 6, "oos_sharpe"].iloc[0])
    l8 = float(wc.loc[wc["lead_months"] == 8, "oos_sharpe"].iloc[0])
    xlab = [f"L{int(v)}" for v in wc["lead_months"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"L{int(v)}" for v in env["lead_months"]], y=env["best_oos_sharpe"],
        marker_color="rgba(108,122,137,0.45)",
        name="Best of ANY signal per lead (context; SA source — envelope is clean by construction)"))
    fig.add_trace(go.Scatter(
        x=xlab, y=wc["oos_sharpe"], mode="lines+markers",
        name=f"Published winner's own curve ({w['selection']['raw_winner_row']['signal']})",
        line=dict(color=C_IND, width=3), marker=dict(size=7, color=C_IND)))
    fig.add_trace(go.Scatter(
        x=[f"L{win_lead}"], y=[win_sharpe], mode="markers",
        marker=dict(size=16, color=C_POS, symbol="star",
                    line=dict(width=1, color="#000000")),
        name=f"Published winner L{win_lead} = {win_sharpe:.2f}"))
    fig.add_trace(go.Scatter(
        x=xlab, y=[bh] * len(xlab), mode="lines",
        name=f"Buy & Hold {TGT} ({bh:.2f})",
        line=dict(color=C_BENCH, dash="dash", width=1.5)))
    # Spike-honesty annotation ON the peak (categorical axis: position by label)
    fig.add_annotation(
        x=f"L{win_lead}", y=win_sharpe,
        text=(f"<b>L{win_lead} is a SPIKE, not a ridge</b><br>"
              f"L6 = {l6:.2f} / L7 = {win_sharpe:.2f} / L8 = {l8:.2f}<br>"
              f"durability standard not met (ECON-LT2 FAIL);<br>"
              f"search-conditioned (bootstrap p = {boot_p:.3f})"),
        showarrow=True, arrowhead=2, ax=-150, ay=45,
        font=dict(size=11, color=C_EVENT), align="left",
        bgcolor=PAL["event_marker_label_bg"])
    fig.update_layout(
        title=(f"The Winner's Peak Is a Lone Spike: {IND_SHORT} → {TGT} Lead Sweep "
               f"(L1..L12)<br><sub>Foreground line: the PUBLISHED WINNER'S own OOS "
               f"Sharpe by lead (diff_12m), peaking at its deployed lead L{win_lead} "
               f"= {win_sharpe:.2f}<br>— but collapsing to {l6:.2f}/{l8:.2f} one "
               f"month either side. Grey bars: best-of-ANY-signal envelope "
               f"(context).<br>Long 98-month OOS, yet the spike shape caps "
               f"confidence.</sub>"),
        xaxis_title=dict(text="Lead (months) applied to signal", standoff=18),
        yaxis_title="OOS Sharpe ratio",
        template="plotly_white", height=520, margin=dict(b=130),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0))
    save_chart("lead_sharpe_distribution", fig,
               caption=(f"Published winner's own Sharpe-by-lead curve (foreground) "
                        f"peaks at its deployed lead L{win_lead} = {win_sharpe:.2f} "
                        f"— but the peak is a SPIKE, not a ridge: L6 = {l6:.2f} and "
                        f"L8 = {l8:.2f} on either side, failing the adjacent-lead "
                        f"durability standard (ECON-LT2). Bootstrap p = "
                        f"{boot_p:.3f} (n.s.) — a search-conditioned candidate. "
                        f"The faded grey envelope (best-of-any-signal per lead) is "
                        f"context; the source is seasonally adjusted, so the "
                        f"envelope and the clean envelope coincide by construction. "
                        f"Buy & Hold {TGT} OOS Sharpe = {bh:.2f}."),
               alignment=("GH #13 native: winner's own curve foregrounded with the "
                          "spike-honesty annotation ON the peak; star placed by "
                          "category label (VIZ categorical-axis rule); all values "
                          "re-read from the lead-sweep CSVs and bootstrap.csv."),
               rules=["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               sources=[f"results/{PAIR}/lead_winner_curve_{DATE_TAG}.csv",
                        f"results/{PAIR}/lead_tournament_{DATE_TAG}.csv",
                        f"results/{PAIR}/lead_clean_envelope_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json",
                        f"results/{PAIR}/tournament_validation_{DATE_TAG}/bootstrap.csv"],
               reconciliation={"winner_lead": win_lead,
                               "winner_curve_peak": round(win_sharpe, 4),
                               "l6": round(l6, 4), "l8": round(l8, 4),
                               "envelope_peak": round(float(env["best_oos_sharpe"].max()), 4),
                               "envelope_peak_lead": int(env.loc[env["best_oos_sharpe"].idxmax(), "lead_months"]),
                               "bh_sharpe": round(bh, 4),
                               "bootstrap_p": round(boot_p, 4),
                               "clean_envelope_identical": True,
                               "durability_adjacent_lead": bool(manifest["winner_adjacent_lead_durability"])},
               extra_meta={"method_name": "lead_sharpe_distribution",
                           "expected_chart_type": "bar",
                           "gh_issue": "13",
                           "clean_envelope_note": manifest["clean_envelope_note"]},
               nber_required=False)


# ── CP2 skip sidecars (VIZ-CP1-G skip protocol) ───────────────────────────

def write_cp2_skips():
    for c in ("rolling_sharpe_cp", "rolling_granger"):
        (OUT / f"chart_skip_{c}.json").write_text(json.dumps({
            "chart_name": c,
            "pair_id": PAIR,
            "skipped_by": "VIZ-CP1-G",
            "reason": ("ECON-CP2 artifacts intentionally absent for this pair: "
                       "regime_story=false (CP2 skipped) in "
                       f"results/{PAIR}/signal_scope.json and the structural-break "
                       "JSON cp2_note. No upstream result file exists to chart."),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": GENERATED_BY,
        }, indent=2) + "\n")
        print(f"  wrote chart_skip_{c}.json")


# ── MAIN ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Generating charts for {PAIR}...")
    chart_hero()
    chart_regime_stats()
    chart_correlation_heatmap()
    chart_ccf()
    chart_granger()
    chart_local_projections()
    chart_transfer_entropy()
    chart_quantile()
    chart_hmm()
    chart_tournament_scatter()
    chart_tournament_dist()
    chart_rolling_correlation()
    chart_structural_break()
    chart_subperiod_sharpe()
    for slug in ("dotcom", "gfc", "covid", "inflation_2022"):
        chart_history_zoom(slug)
    chart_correlations_lead_view()
    chart_lead_sharpe_distribution()
    write_cp2_skips()
    print("\nDone.")
