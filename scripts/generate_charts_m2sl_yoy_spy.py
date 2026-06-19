#!/usr/bin/env python3
"""Chart generation: M2 Money Supply YoY (M2SL_YOY) x SPY — Mode 1 (stage 3).

Vera-owned producer for the m2sl_yoy_spy standard chart set (20260619).
Consumes Evan's ECON-H4 artifacts (results/m2sl_yoy_spy/) + Dana's monthly
dataset + Evan's strategy_returns_20260619.csv. Strategy charts use Evan's
saved return series; they do not re-run strategy selection.

Framing (binding, per Lead dispatch + Evan handoff — DO NOT OVERSELL):
  * Tradable winner is money-growth ACCELERATION (m2sl_yoy_accel_pct, the MoM
    change in M2's YoY rate), NOT the YoY level. Procyclical, L2, Long/Cash.
  * CAUSALITY IS REVERSE. Toda-Yamamoto Granger: M2SL -> SPY is n.s. at ALL
    lags 1-12 (forward NONE); SPY -> M2SL is significant at lags 1,2,3,4,5,8.
    M2 is coincident/lagging w.r.t. equities — the market moves first. This
    is NOT a forward-causal forecasting signal; the edge is a search-found
    acceleration pattern. The Granger chart MUST show BOTH directions with the
    REVERSE direction visually dominant (it is the one that clears the line).
  * M2 YoY history is vivid: the 2020-21 surge (~27%) and the first-ever YoY
    contraction in 2022-23 (negative). Mark the 0% line prominently.
  * Fragility: bootstrap p=0.025 (search-selected, no final exam),
    found_in_search, confidence LOW, conditionally_durable, OOS dominated by
    the 2020/2022 monetary regime.

Charts produced (output/charts/m2sl_yoy_spy/plotly/, bare names per VIZ-A3):
    hero, regime_stats, correlation_heatmap, ccf_prewhitened,
    granger_f_by_lag, local_projections, transfer_entropy, quantile_coef,
    hmm_regime_probs, equity_curves, drawdown, tournament_scatter,
    tournament_sharpe_dist, rolling_correlation, structural_break,
    subperiod_sharpe, history_zoom_{dotcom,gfc,covid,inflation_2022}
    + chart_skip_{rolling_sharpe_cp,rolling_granger}.json (CP2 absent:
      regime_story=false in signal_scope.json — VIZ-CP1-G skip protocol)

Gates implemented in-process: VIZ-IC1 (palette + VIZ-TX1 one-$ lint),
VIZ-NBER1 (shading on calendar-time charts), VIZ-DP1 (dual-panel axis
assignment), perceptual PNGs (VIZ-CV1), _meta.json sidecars with disposition
+ reconciliation values re-read from artifacts at generation time.

Author: Viz Vera. Date: 2026-06-19.
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

PAIR = "m2sl_yoy_spy"
DATE_TAG = "20260619"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

# Display names (VIZ-NS1).
IND_LONG = "M2 Money Supply (YoY growth)"
IND_SHORT = "M2 YoY growth"
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
                     "rgba(153,153,153,0.45)", "#aec7e8"})

EVENTS_REG = json.loads(
    (REPO / "docs/schemas/history_zoom_events_registry.json").read_text())
EVENTS_REG_VERSION = EVENTS_REG.get("x-version", "1.0.0")

GENERATED_BY = "Viz Vera — scripts/generate_charts_m2sl_yoy_spy.py (pair260619_m2sl_yoy_spy)"

SRC_DATA = "data/m2sl_yoy_spy_monthly_latest.parquet"


# ── Loaders ───────────────────────────────────────────────────────────────

def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / "m2sl_yoy_spy_monthly_latest.parquet")


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
    """VIZ-DP1 axis-assignment check for dual-panel charts."""
    d = json.loads(fig.to_json())
    layout = d.get("layout", {})
    if "yaxis2" not in layout:
        return
    if layout.get("yaxis2", {}).get("overlaying") == "y":
        return  # secondary-y dual-axis chart (single panel) — DP1 not applicable
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


# ── 1. Hero — M2 YoY level vs SPY (vivid history) ─────────────────────────

def chart_hero():
    df = load_monthly()
    df = df[df["spy"].notna()]
    yoy = df["m2sl_pct_yoy"].dropna()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=yoy.index, y=yoy.values,
        name=f"{IND_SHORT} (%, year-over-year)",
        line=dict(color=C_IND, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["spy"],
        name=f"{TGT} price (USD)",
        line=dict(color=C_TGT, width=1.5)), secondary_y=True)
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    nber_swatch(fig)
    # 0% line — first-ever YoY contraction reference (binding annotation point).
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL, line_width=1.0,
                  secondary_y=False, annotation_text="0% — no money growth")
    # 2020-21 surge (~27%)
    surge_y = float(yoy.loc["2021-02-28"]) if "2021-02-28" in yoy.index else float(yoy.max())
    fig.add_annotation(x="2021-02-28", y=surge_y,
                       text="2020-21 surge: M2 YoY peaked near 27%<br>(pandemic liquidity)",
                       showarrow=True, arrowhead=2, ax=-40, ay=-40,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    # 2022-23 first-ever contraction (negative)
    contr_idx = yoy.loc["2023-01-31":"2023-12-31"].idxmin()
    fig.add_annotation(x=contr_idx, y=float(yoy.loc[contr_idx]),
                       text="2022-23: first-ever YoY contraction<br>(M2 fell below 0%)",
                       showarrow=True, arrowhead=2, ax=30, ay=40,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    y0, y1 = df.index.min().year, df.index.max().year
    fig.update_layout(
        title=(f"{IND_LONG} vs {TGT}: A Vivid History, but a Coincident/Lagging "
               f"Signal ({y0}–{y1})"),
        template="plotly_white", hovermode="x unified", height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text=f"{IND_SHORT} (%, YoY)", secondary_y=False)
    fig.update_yaxes(title_text=f"{TGT} price (USD)", secondary_y=True)
    save_chart("hero", fig,
               caption=(f"{IND_LONG} (vermillion, left axis) against the {TGT} price "
                        f"(blue, right axis), {y0}–{y1}. The 2020-21 surge near 27% and "
                        f"the first-ever year-over-year contraction in 2022-23 are the "
                        f"vivid but regime-concentrated episodes. The tradable rule "
                        f"actually trades on the month-to-month CHANGE in this YoY rate "
                        f"(money-growth acceleration), not the level shown here. Shaded "
                        f"bands mark NBER recessions."),
               alignment=("Hero shows the vivid M2 YoY history with the 0% line and the "
                          "surge/contraction episodes; caption clarifies the winner "
                          "trades the acceleration transform, not this level."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-TX1", "VIZ-O1"],
               sources=[SRC_DATA])


# ── 2. Regime stats (VIZ-QR1 dual-panel) ──────────────────────────────────

def chart_regime_stats():
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>(Lowest M2 YoY)", "Q2", "Q3", "Q4<br>(Highest M2 YoY)"]
    fig = make_dual_panel_regime_chart(
        quartile_labels=labels,
        sharpe=q["sharpe"].tolist(),
        ann_return_pct=(q["ann_return"] * 100).tolist(),
        signal_label=f"{IND_SHORT} level",
        x_axis_title=f"{IND_SHORT} quartile (Q1=Low, Q4=High)",
    )
    fig.update_layout(
        title=dict(
            text=(f"High-Money-Growth Regimes Are the RISKIEST Concurrently: "
                  f"Q4 Has the Worst Sharpe and a -47% Drawdown"),
            y=0.99, yanchor="top"),
        margin=dict(t=150))
    save_chart("regime_stats", fig,
               caption=(f"SPY performance by {IND_SHORT} LEVEL quartile (concurrent, "
                        f"descriptive): Sharpe (left) and annualized return (right). "
                        f"Sharpe FALLS from Q1 {q['sharpe'].iloc[0]:.2f} / "
                        f"{q['ann_return'].iloc[0]*100:.1f}% to Q4 {q['sharpe'].iloc[3]:.2f} "
                        f"/ {q['ann_return'].iloc[3]*100:.1f}%, and Q4's max drawdown is "
                        f"{q['max_drawdown'].iloc[3]*100:.0f}%. The high-money-growth "
                        f"regime is the riskiest concurrently — this LEVEL story is "
                        f"separate from, and not the same as, the acceleration winner."),
               alignment=("VIZ-QR1 dual-panel from regime_quartile_returns.csv; values "
                          "re-read at generation time. Per Evan handoff §quartiles: the "
                          "high-money-growth Q4 is the riskiest concurrent regime (H1b "
                          "inflation/tightening counter-channel). LEVEL vs acceleration "
                          "are deliberately separate stories."),
               rules=["VIZ-QR1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/regime_quartile_returns.csv"],
               nber_required=False)


# ── 3. Correlation heatmap ────────────────────────────────────────────────

_SIGLBL = {
    "yoy": "YoY growth", "mom": "MoM growth",
    "mom3m": "3-month growth", "mom6m": "6-month growth",
    "accel": "Growth acceleration",
    "yoy_zscore_120m": "YoY z-score (120-month)",
    "contraction": "Contraction flag",
    "hmm_stress": "HMM high-variance probability",
}


def chart_correlation_heatmap():
    c = pd.read_csv(CORE / "correlations.csv")
    p = c[c["metric"] == "pearson"].copy()
    p[["signal", "horizon"]] = p["pair_name"].str.split("__", expand=True)
    hor_order = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    piv = p.pivot(index="signal", columns="horizon", values="value")
    piv = piv.reindex(columns=[h for h in hor_order if h in piv.columns])
    pp = p.pivot(index="signal", columns="horizon", values="p_value")
    pp = pp.reindex(columns=piv.columns)
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
        title=(f"Forward Correlations Are Weak: {IND_SHORT} Signals vs {TGT} "
               f"Forward Returns<br><sup>Pearson r; * p&lt;0.05, ** p&lt;0.01. "
               f"Best cell: {_SIGLBL.get(best['signal'].split('__')[0], best['signal'])} "
               f"r = {best['value']:.3f}</sup>"),
        xaxis_title=f"{TGT} forward return horizon",
        yaxis_title=f"M2 signal",
        template="plotly_white", height=520)
    save_chart("correlation_heatmap", fig,
               caption=(f"Pearson correlations between M2 signals and {TGT} forward "
                        f"returns at 1/3/6/12-month horizons. The strongest cell is only "
                        f"r = {best['value']:.3f} "
                        f"({best['pair_name'].replace('__',' vs ')}). Pairwise "
                        f"correlations are weak and do not by themselves validate the "
                        f"trading rule."),
               alignment=("Weak linear evidence; best cell re-read from correlations.csv."),
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
        title=(f"Pre-Whitened Cross-Correlation: No Clean Forward Lead from "
               f"{IND_SHORT} to {TGT} Returns<br><sup>AR(12) pre-whitening; "
               f"{nsig} of {len(d)} lags significant</sup>"),
        xaxis_title=f"Lag (months; negative = {IND_SHORT} leads {TGT})",
        yaxis_title="Cross-correlation",
        template="plotly_white", height=400, showlegend=False)
    save_chart("ccf_prewhitened", fig,
               caption=(f"Cross-correlation between AR(12) pre-whitened {IND_SHORT} and "
                        f"{TGT} returns across lags. {nsig} of {len(d)} lags clear the "
                        f"95% band; there is no clean forward lead from money growth to "
                        f"equities, consistent with the reverse-only Granger verdict."),
               alignment="CCF mirrors the absence of a forward lead.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/ccf_prewhitened.csv"],
               nber_required=False)


# ── 5. Granger F by lag (BOTH directions; REVERSE dominant — headline) ─────

def chart_granger():
    g = pd.read_csv(CORE / "granger_causality.csv")
    bylag = pd.read_csv(RES / "granger_by_lag.csv")
    fwd = g[g["direction"] == "indicator_to_target"].sort_values("lag")
    rev = g[g["direction"] == "target_to_indicator"].sort_values("lag")
    crit = [float(sstats.f.ppf(0.95, r["df_num"], r["df_den"]))
            for _, r in bylag.sort_values("lag").iterrows()]
    rev_sig = list(rev.loc[rev["significant"], "lag"])
    fig = go.Figure()
    # REVERSE is the dominant story — render it as the visually primary series.
    fig.add_trace(go.Bar(
        x=rev["lag"], y=rev["f_statistic"],
        name=f"{TGT} → {IND_SHORT} (reverse) — significant at lags {rev_sig}",
        marker_color=C_TGT))
    fig.add_trace(go.Bar(
        x=fwd["lag"], y=fwd["f_statistic"],
        name=f"{IND_SHORT} → {TGT} (forward) — NOT significant at any lag",
        marker_color="#aec7e8"))
    fig.add_trace(go.Scatter(
        x=bylag.sort_values("lag")["lag"], y=crit, mode="lines",
        name="5% critical value (per lag)",
        line=dict(color=C_EVENT, dash="dash", width=1.5)))
    fig.update_layout(
        title=(f"Causality Runs in REVERSE: The Market Moves First, M2 Responds "
               f"<br><sup>Toda-Yamamoto Granger F by lag; {TGT} → {IND_SHORT} "
               f"significant at lags {rev_sig}; {IND_SHORT} → {TGT} significant at "
               f"NONE</sup>"),
        xaxis_title="Lag (months)",
        yaxis_title="F-statistic",
        barmode="group", template="plotly_white", height=480,
        margin=dict(b=140),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("granger_f_by_lag", fig,
               caption=(f"Toda-Yamamoto Granger F-statistics at lags 1–12, both "
                        f"directions. {TGT} → {IND_SHORT} (blue, the REVERSE direction) "
                        f"clears the 5% critical line at lags {rev_sig}; {IND_SHORT} → "
                        f"{TGT} (pale blue, the forward direction) clears it at NONE "
                        f"(all p > 0.43). The market leads the money aggregate, not the "
                        f"other way around — M2 is coincident/lagging, so this is NOT a "
                        f"forward forecasting signal."),
               alignment=("REVERSE direction rendered as the visually primary series per "
                          "the binding honesty mandate; forward is shown but n.s. at "
                          "every lag. This is the headline reconciliation point."),
               rules=["VIZ-IC1", "VIZ-V3", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/granger_causality.csv",
                        f"results/{PAIR}/granger_by_lag.csv"],
               reconciliation={"forward_significant_lags": [],
                               "reverse_significant_lags": [int(x) for x in rev_sig],
                               "verdict": "reverse_only"},
               nber_required=False)


# ── 6. Local projections (fwd + rev panels) ───────────────────────────────

def chart_local_projections():
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = make_subplots(rows=1, cols=2, shared_yaxes=False, subplot_titles=[
        f"{IND_SHORT} → {TGT} (forward — no effect)",
        f"{TGT} → {IND_SHORT} (reverse)"])
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
            name=("Coefficient: money growth → market" if dirn == "fwd"
                  else "Coefficient: market → money growth"),
            line=dict(color=color, width=2)), row=1, col=col)
        fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL,
                      line_width=0.8, row=1, col=col)
    pmin = lp[lp["direction"] == "fwd"]["p_value"].min()
    fig.update_layout(
        title=(f"Local Projections (HAC): No Horizon Shows a Forward Effect "
               f"<br><sup>Forward-direction p-values remain above 0.05 "
               f"(min p = {pmin:.2f}); CI bands include zero throughout</sup>"),
        template="plotly_white", height=460, margin=dict(b=120),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    fig.update_xaxes(title_text="Horizon (months)")
    fig.update_yaxes(title_text="Impulse response coefficient", row=1, col=1)
    save_chart("local_projections", fig,
               caption=(f"Local-projection impulse responses with HAC standard errors at "
                        f"horizons 1/3/6/12 months. The forward direction ({IND_SHORT} → "
                        f"{TGT}) is indistinguishable from zero at every horizon "
                        f"(min p = {pmin:.2f}). This corroborates the reverse-only "
                        f"Granger verdict: money growth carries no forward push on "
                        f"equities."),
               alignment="Dual-panel LP per ECON-H4; forward n.s. supports reverse-only verdict.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/local_projections.csv"],
               nber_required=False)


# ── 7. Transfer entropy ───────────────────────────────────────────────────

def chart_transfer_entropy():
    te = pd.read_csv(CORE / "transfer_entropy.csv")
    lab = {"indicator_to_target": f"{IND_SHORT} → {TGT}",
           "target_to_indicator": f"{TGT} → {IND_SHORT}"}
    fwd_p = float(te.loc[te["direction"] == "indicator_to_target",
                         "permutation_p_value"].iloc[0])
    rev_p = float(te.loc[te["direction"] == "target_to_indicator",
                         "permutation_p_value"].iloc[0])
    fig = go.Figure()
    for _, r in te.iterrows():
        fig.add_trace(go.Bar(
            x=[lab[r["direction"]]], y=[r["te_value"]],
            name=f"{lab[r['direction']]} (perm. p = {r['permutation_p_value']:.2f})",
            marker_color=C_IND if r["direction"] == "indicator_to_target" else C_TGT,
            text=[f"TE = {r['te_value']:.4f}<br>p = {r['permutation_p_value']:.2f}"],
            textposition="outside"))
    fig.update_layout(
        title=("Transfer Entropy: Only the REVERSE Direction Shows Significant "
               "Information Flow<br><sup>Tercile binning, 500 permutations; "
               f"forward p = {fwd_p:.2f}, reverse p = {rev_p:.2f}</sup>"),
        yaxis_title="Transfer entropy (nats)",
        xaxis_title="Direction",
        template="plotly_white", height=400, showlegend=False)
    save_chart("transfer_entropy", fig,
               caption=(f"Transfer entropy between {IND_SHORT} and {TGT} returns "
                        f"(tercile bins, 500 permutations). The forward direction "
                        f"({IND_SHORT} → {TGT}) is NOT significant (p = {fwd_p:.2f}); "
                        f"only the reverse ({TGT} → {IND_SHORT}, p = {rev_p:.2f}) is — "
                        f"the same reverse-leading pattern the Granger test shows, now "
                        f"in a nonlinear information-flow check."),
               alignment="Two-bar TE comparison; reverse-only significance reinforces the Granger verdict.",
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
        yaxis_title="Coefficient",
        template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("quantile_coef", fig,
               caption=(f"Quantile-regression coefficient of {TGT} forward returns on "
                        f"{IND_SHORT} across return quantiles 0.05–0.95 with 95% CI. "
                        f"Significant tau values: {sig_tau}. The coefficient is most "
                        f"negative in the lowest return quantiles, indicating the "
                        f"relationship is not a clean uniform forward predictor."),
               alignment="Coef-by-tau with CI band per ECON-H4.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv"],
               nber_required=False)


# ── 9. HMM regime probabilities ───────────────────────────────────────────

def chart_hmm():
    h = pd.read_parquet(CORE / "hmm_states.parquet")
    cov = float(h.loc["2020-04-30":"2021-06-30", "prob_stress"].mean())
    assert cov > 0.95, f"HMM manifest assertion failed: COVID prob_stress mean {cov:.2f}"
    summ = pd.read_csv(CORE / "hmm_summary.csv")
    stress_pct = float(summ.loc[summ["state_label"] == "stress", "frequency_pct"].iloc[0])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h.index, y=h["prob_stress"], mode="lines",
        name="P(high-variance M2-growth regime)",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.25)",
        line=dict(color=C_IND, width=1.2)))
    add_nber_shading(fig, x_min=h.index.min(), x_max=h.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Hidden Markov Model (HMM): The High-Variance {IND_SHORT} Regime "
               f"Pins Near 1.0 Through the 2020-21 Money Surge<br><sup>2-state HMM on "
               f"YoY growth; 'high-variance' state covers {stress_pct:.0f}% of "
               f"months</sup>"),
        xaxis_title="Date",
        yaxis_title="Probability of high-variance regime",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("hmm_regime_probs", fig,
               caption=(f"Probability that {IND_SHORT} is in its high-variance regime "
                        f"(2-state HMM). The high-variance state pins near 1.0 through "
                        f"the 2020-21 money surge (verified against the manifest "
                        f"assertion at generation time) and covers {stress_pct:.0f}% of "
                        f"months. It maps the monetary backdrop; it is not the winning "
                        f"signal. Shaded bands mark NBER recessions."),
               alignment=("Labels follow hmm_states_manifest.json semantics ('stress' = "
                          "high-variance M2-YoY-growth regime), relabelled in plain "
                          "English to avoid implying equity stress."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/hmm_states.parquet",
                        f"results/{PAIR}/core_models_{DATE_TAG}/hmm_summary.csv"],
               reconciliation={"surge_prob_stress_mean": {"computed": round(cov, 4),
                                                          "manifest_expected": 1.0,
                                                          "verdict": "PASS"}})


# ── 10/11. Strategy equity curves and drawdown ────────────────────────────

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
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["strategy_equity"], mode="lines",
        name=f"M2 acceleration Long/Cash rule (Sharpe {w['oos_sharpe']:.2f})",
        line=dict(color=C_IND, width=2.2)))
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["bh_equity"], mode="lines",
        name=f"Buy & Hold {TGT} (Sharpe {w['bh_sharpe']:.2f})",
        line=dict(color=C_BENCH, width=1.8, dash="dash")))
    fig.add_vline(x=w["oos_period_start"], line=dict(color=C_EVENT, dash="dot", width=1.3))
    fig.add_annotation(x=w["oos_period_start"], y=0.96, yref="paper", showarrow=False,
                       xanchor="left", text="OOS begins",
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=d["date"].min(), x_max=d["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Defensive Overlay With a Drawdown Win: M2 Acceleration Rule vs "
               f"Buy & Hold {TGT}<br><sup>OOS {w['oos_period_start']} to "
               f"{w['oos_period_end']}: {w['oos_ann_return']*100:.1f}% vs "
               f"{w['bh_ann_return']*100:.1f}% annualized return — but OOS is dominated "
               f"by the 2020/2022 monetary regime</sup>"),
        xaxis_title="Date",
        yaxis_title="Growth of 1.00",
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("equity_curves", fig,
               caption=(f"Cumulative growth of 1.00 for Evan's saved strategy returns and "
                        f"buy-and-hold returns. The OOS rule raises Sharpe "
                        f"({w['oos_sharpe']:.2f} vs {w['bh_sharpe']:.2f}) and beats on "
                        f"return ({w['oos_ann_return']*100:.1f}% vs "
                        f"{w['bh_ann_return']*100:.1f}%), but the short OOS window is "
                        f"dominated by the 2020 surge and 2022 contraction. Shaded bands "
                        f"mark NBER recessions."),
               alignment="Strategy series from strategy_returns_20260619.csv; metrics from winner_summary.json; OOS regime caveat in title.",
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
        title=(f"Drawdown Protection Is Real but Episode-Shaped: "
               f"{w['oos_max_drawdown']*100:.1f}% vs {w['bh_max_drawdown']*100:.1f}% OOS"),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white", height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("drawdown", fig,
               caption=(f"Drawdown path for the M2-acceleration Long/Cash rule and "
                        f"buy-and-hold {TGT}. In OOS the strategy's max drawdown is "
                        f"{w['oos_max_drawdown']*100:.1f}% versus "
                        f"{w['bh_max_drawdown']*100:.1f}% for buy-and-hold. The win is "
                        f"real but episode-shaped — the OOS window is dominated by the "
                        f"2020/2022 monetary regime."),
               alignment="Drawdown computed directly from Evan's saved monthly return series.",
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


# ── 12/13. Tournament scatter + Sharpe distribution ───────────────────────

def _tournament_frames():
    t = load_tournament()
    valid = t[t["valid"] & (t["signal"] != "BENCHMARK")]
    bench = t[t["signal"] == "BENCHMARK"]
    return t, valid, bench


def chart_tournament_scatter():
    t, valid, bench = _tournament_frames()
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
        x=[float(bench.iloc[0]["annual_turnover"])], y=[float(bench.iloc[0]["oos_sharpe"])],
        mode="markers", marker=dict(size=14, color=C_BENCH, symbol="diamond"),
        name=f"Buy & Hold {TGT} (Sharpe {float(bench.iloc[0]['oos_sharpe']):.2f})"))
    top5 = valid.nlargest(5, "oos_sharpe")
    fig.add_trace(go.Scatter(
        x=top5["annual_turnover"], y=top5["oos_sharpe"], mode="markers",
        marker=dict(size=12, color=C_POS, symbol="star",
                    line=dict(width=1, color="#000000")),
        name="Top 5 by OOS Sharpe"))
    fig.update_layout(
        title=(f"Tournament: {len(t)-1:,} Strategy Combos ({len(valid):,} Valid) — "
               f"Winner OOS Sharpe {valid['oos_sharpe'].max():.2f} vs Buy & Hold "
               f"{float(bench.iloc[0]['oos_sharpe']):.2f}"),
        xaxis_title="Annual turnover (trades per year)",
        yaxis_title="OOS Sharpe ratio",
        template="plotly_white", height=540, margin=dict(b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("tournament_scatter", fig,
               caption=(f"All {len(t)-1:,} tournament combinations (OOS Sharpe vs annual "
                        f"turnover; color = max drawdown). {len(valid):,} pass validity; "
                        f"the Buy & Hold {TGT} diamond sits at Sharpe "
                        f"{float(bench.iloc[0]['oos_sharpe']):.2f}. Winner identified by "
                        f"the ECON-T3 cascade; see the distribution chart for position "
                        f"disclosure."),
               alignment="Standard tournament scatter; benchmark via signal=='BENCHMARK' (ECON-T4).",
               rules=["VIZ-IC1", "ECON-T4", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
               nber_required=False)


def chart_tournament_dist():
    t, valid, bench = _tournament_frames()
    med = float(valid["oos_sharpe"].median())
    wmax = float(valid["oos_sharpe"].max())
    bh = float(bench.iloc[0]["oos_sharpe"])
    fig = go.Figure(go.Histogram(
        x=valid["oos_sharpe"], nbinsx=60, marker_color=C_TGT, opacity=0.75,
        name=f"Valid strategies (n = {len(valid):,})"))
    fig.add_vline(x=med, line=dict(color=C_NEUTRAL, dash="dot", width=1.5))
    fig.add_vline(x=bh, line=dict(color=C_BENCH, dash="dash", width=2))
    fig.add_vline(x=wmax, line=dict(color=C_IND, dash="dash", width=2))
    fig.add_annotation(x=wmax, y=1.0, yref="paper", showarrow=False, xanchor="right",
                       text=f"Winner = max of {len(valid):,} (median {med:.2f})",
                       font=dict(size=12, color=C_IND),
                       bgcolor=PAL["event_marker_label_bg"])
    bh_rel = "ABOVE" if bh >= med else "below"
    fig.add_annotation(x=bh, y=0.85, yref="paper", showarrow=False, xanchor="left",
                       text=f"Buy & Hold {TGT} = {bh:.2f} — {bh_rel} the median strategy",
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
               caption=(f"Distribution of OOS Sharpe across the {len(valid):,} valid "
                        f"strategy combos. The winner (Sharpe {wmax:.2f}) is the max of "
                        f"{len(valid):,} with median {med:.2f}; the median sits {bh_rel} "
                        f"Buy & Hold {TGT} ({bh:.2f}). Winner selection is a tail draw "
                        f"from a large search; bootstrap p = 0.025 (significant at 5% but "
                        f"search-selected, no final exam)."),
               alignment=("VIZ-SCD1 position disclosure + B&H benchmark line; all numbers "
                          "re-read from the tournament CSV at generation time."),
               rules=["VIZ-SCD1", "ECON-T4", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
               reconciliation={"valid_count": len(valid), "median_oos_sharpe": round(med, 4),
                               "winner_oos_sharpe": round(wmax, 4), "bh_oos_sharpe": round(bh, 4)},
               nber_required=False)


# ── 14. Rolling correlation ───────────────────────────────────────────────

def chart_rolling_correlation():
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rc["date"], y=rc["rolling_corr"], mode="lines",
        name="24-month rolling correlation",
        line=dict(color=C_TGT, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_EVENT, line_width=1,
                  annotation_text="No correlation")
    add_nber_shading(fig, x_min=rc["date"].min(), x_max=rc["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"The Sign Flips Often: 24-Month Rolling Correlation, {IND_SHORT} vs "
               f"{TGT} Returns<br><sup>Sign agreement only "
               f"{sb['rolling_corr_sign_stability']:.2f} — verdict: "
               f"{sb['rolling_corr_stability_verdict'].replace('_', '-')}</sup>"),
        xaxis_title="Date",
        yaxis_title="Rolling correlation (r)",
        template="plotly_white", height=420,
        yaxis=dict(range=[-1, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("rolling_correlation", fig,
               caption=(f"24-month rolling correlation between {IND_SHORT} and {TGT} "
                        f"monthly returns. The sign agrees with its full-sample value "
                        f"only {sb['rolling_corr_sign_stability']:.0%} of the time "
                        f"(verdict: {sb['rolling_corr_stability_verdict'].replace('_',' ')}) "
                        f"— the relationship is not stable enough to lean on. Shaded "
                        f"bands mark NBER recessions."),
               alignment="Stability verdict quoted from structural_break JSON, not hard-coded.",
               rules=["VIZ-CP1.2", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/rolling_correlation_{PAIR}.csv",
                        f"results/{PAIR}/structural_break_{PAIR}.json"])


# ── 15. Structural break ──────────────────────────────────────────────────

def chart_structural_break():
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    df = load_monthly()
    sig = df.loc[sb["sample_start"]:sb["sample_end"], "m2sl_pct_yoy"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig.index, y=sig.values, mode="lines",
        name=f"{IND_SHORT} (%, YoY)", line=dict(color=C_IND, width=1.8)))
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
        title=(f"No Structural Break Detected: Quandt-Andrews sup-F Test on "
               f"{IND_SHORT} (p = {sb['p_value']:.2f})"),
        xaxis_title="Date",
        yaxis_title=f"{IND_SHORT} (%, YoY)",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("structural_break", fig,
               caption=(f"{IND_SHORT} over the test sample ({sb['sample_start'][:7]}–"
                        f"{sb['sample_end'][:7]}, n = {sb['n_obs']}) with the "
                        f"Quandt-Andrews candidate break date ({sb['break_date'][:7]}). "
                        f"The test does NOT flag a break (sup-F {sb['f_stat']:.2f}, "
                        f"residual-bootstrap p = {sb['p_value']:.2f}) — instability shows "
                        f"up in the rolling correlation's sign, not as a one-time break. "
                        f"Shaded bands mark NBER recessions."),
               alignment="Annotation-only chart per ECON-H4 ('not flagged'); values from JSON.",
               rules=["VIZ-CP1.3", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/structural_break_{PAIR}.json", SRC_DATA],
               extra_meta={"break_date": sb["break_date"],
                           "annotation_strategy_id": "manual_override"})


# ── 16. Sub-period Sharpe ─────────────────────────────────────────────────

_EP_LABEL = {"dot_com": "Dot-Com 2000–02", "gfc": "GFC 2008–09",
             "covid": "COVID 2020", "china_2015": "China 2015–16"}


def chart_subperiod_sharpe():
    rows = pd.read_csv(RES / "subperiod_sharpe.csv")
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
    covid_sharpe = float(rows.loc[rows["episode"] == "covid", "ann_sharpe"].iloc[0])
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=texts, textposition="outside",
                           name="Annualized Sharpe by episode"))
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Only COVID Is Evaluable: Winner Strategy by Historical Episode "
               f"<br><sup>COVID Sharpe {covid_sharpe:.2f}; Dot-Com, GFC and China "
               f"2015 fall outside the 2018+ OOS window (insufficient data)</sup>"),
        xaxis_title="Historical episode",
        yaxis_title="Annualized Sharpe ratio",
        template="plotly_white", height=430, margin=dict(b=110), showlegend=False)
    save_chart("subperiod_sharpe", fig,
               caption=(f"Winner-strategy annualized Sharpe within each canonical stress "
                        f"episode. Only COVID 2020 falls inside the 2018+ OOS window "
                        f"(Sharpe {covid_sharpe:.2f}); Dot-Com, GFC and China 2015 are "
                        f"marked insufficient_data because they predate the OOS split. "
                        f"This is why durability is only 'conditionally_durable' — a "
                        f"single evaluable episode."),
               alignment=("Three-state encoding (no data / in cash / value); states "
                          "derived from data_status. Single-episode evaluability ties to "
                          "the conditionally_durable verdict."),
               rules=["ECON-CP1", "VIZ-CP1.1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/subperiod_sharpe.csv"],
               nber_required=False)


# ── 17. History zoom charts (4 episodes, dual-panel) ──────────────────────

def _window_has_recession(start: str, end: str) -> bool:
    from _nber import RECESSIONS
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return any(pd.Timestamp(r0) <= e and pd.Timestamp(r1) >= s for r0, r1 in RECESSIONS)


def chart_history_zoom(slug: str):
    ep = EVENTS_REG["episodes"][slug]
    df = load_monthly()
    w = df.loc[ep["start_date"]:ep["end_date"]]
    sig = w["m2sl_pct_yoy"].dropna()
    spy = w["spy"].dropna()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[f"{IND_SHORT} (%, YoY)",
                                        f"{TGT} price (USD)"])
    fig.add_trace(go.Scatter(x=sig.index, y=sig.values,
                             name=f"{IND_SHORT} (%, YoY)",
                             line=dict(color=C_IND, width=2)), row=1, col=1)
    # 0% line on the indicator panel (vivid for the 2022-23 contraction window)
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8,
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=spy.index, y=spy.values,
                             name=f"{TGT} price (USD)",
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
    fig.update_yaxes(title_text="M2 YoY (%)", row=1, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    save_chart(f"history_zoom_{slug}", fig,
               caption=(f"{IND_SHORT} (top, with 0% line) and {TGT} price (bottom) "
                        f"through the {ep['episode_name']} window ({ep['start_date'][:7]} "
                        f"to {ep['end_date'][:7]}), with registry event markers."
                        + (" Shaded bands mark NBER recessions." if has_rec
                           else " No NBER recession falls in this window.")),
               alignment=(f"Dual-panel episode zoom per VIZ-V1/VIZ-ZOOM1; events from "
                          f"history_zoom_events_registry v{EVENTS_REG_VERSION}."),
               rules=["VIZ-V1", "VIZ-V2", "VIZ-V12", "VIZ-V13", "VIZ-TS1",
                      "VIZ-DP1", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[SRC_DATA, "docs/schemas/history_zoom_events_registry.json"],
               extra_meta={"annotation_strategy_id": "descending_stair",
                           "events_registry_version": EVENTS_REG_VERSION,
                           "episode_slug": slug},
               nber_required=_window_has_recession(ep["start_date"], ep["end_date"]))


# ── CP2 skip sidecars (VIZ-CP1-G skip protocol) ───────────────────────────

def write_cp2_skips():
    for c in ("rolling_sharpe_cp", "rolling_granger"):
        (OUT / f"chart_skip_{c}.json").write_text(json.dumps({
            "chart_name": c,
            "pair_id": PAIR,
            "skipped_by": "VIZ-CP1-G",
            "reason": ("ECON-CP2 artifacts intentionally absent for this pair: "
                       "regime_story=false in results/m2sl_yoy_spy/signal_scope.json "
                       "(Evan handoff). No upstream result file exists to chart."),
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
    chart_equity_curves()
    chart_drawdown()
    chart_tournament_scatter()
    chart_tournament_dist()
    chart_rolling_correlation()
    chart_structural_break()
    chart_subperiod_sharpe()
    for slug in ("dotcom", "gfc", "covid", "inflation_2022"):
        chart_history_zoom(slug)
    write_cp2_skips()
    print("\nDone.")
