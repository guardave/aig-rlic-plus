#!/usr/bin/env python3
"""Chart generation: PHLX Semiconductor Index (SOX) x SPY — Mode 1 (daily).

Vera-owned producer for the phlxsox_spy standard chart set (20260619).
Consumes Evan's ECON-H4 handoff artifacts (results/phlxsox_spy/) and Dana's
daily dataset. Strategy charts use Evan's saved strategy_returns CSV; the
SPY-own-momentum benchmark line is reconstructed deterministically from the
saved SPY daily returns and verified against winner_summary.json (Sharpe 0.83).

Framing (binding, per Lead dispatch + Evan handoff — this winner is FRAGILE):
  1. The signal is SOX/SPY RELATIVE STRENGTH 6-month momentum, NOT raw SOX.
     Both are equities (daily-return corr 0.709 = shared beta / co-movement),
     so the ratio is used to partial out common market beta.
  2. Causality is BIDIRECTIONAL feedback (Toda-Yamamoto Granger significant
     SOX->SPY AND SPY->SOX at every lag) — NOT a clean semiconductor lead.
  3. The edge over a SPY-own-momentum benchmark is MARGINAL and horizon-
     dependent (adds at 21d p=0.033, NOT at 63d p=0.075; incremental R²~1%).
  4. Fragility: IS Sharpe 0.10 vs OOS 1.57 (favorable 2021-26 semis bull);
     median valid combo 0.67 below B&H 0.82; win-rate 0.20; LOST in every
     pre-OOS crisis (Dot-Com/GFC/COVID); bootstrap p=0.041; confidence LOW.

Two hard chart requirements from the brief:
  - equity_curves is a 3-LINE chart: winner vs Buy&Hold vs SPY-own-momentum.
  - granger_f_by_lag shows BOTH directions, conveying "feedback, not lead."

Author: Viz Vera. Date: 2026-06-19.
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

PAIR = "phlxsox_spy"
DATE_TAG = "20260619"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

# Display names (VIZ-NS1). NOTE: app/components/display_names.py has no
# phlxsox_spy entry yet — gap flagged to Ace in the handoff note; these
# constants are the proposed canonical forms.
IND_LONG = "PHLX Semiconductor Index"
IND_SHORT = "SOX"
RS_LONG = "SOX/SPY relative strength"
TGT = "SPY"

# ── Palette (okabe_ito_2026, VIZ-V11) ─────────────────────────────────────
PALETTE_ID = "okabe_ito_2026"
PAL = json.loads((REPO / "docs/schemas/color_palette_registry.json").read_text())[
    "palettes"][PALETTE_ID]
C_IND = PAL["primary_data_trace"]       # #D55E00 indicator / winner
C_TGT = PAL["secondary_data_trace"]     # #0072B2 target
C_POS = PAL["tertiary_data_trace"]      # #009E73
C_BENCH = PAL["benchmark_trace"]        # #6C7A89 buy&hold
C_NEUTRAL = PAL["hold_indicator"]       # #999999
C_EVENT = PAL["event_marker_line"]      # #4D4D4D
C_NBER = PAL["nber_shading"]
C_EXT = PAL["categorical_extended"]

ALLOWED_COLORS = ({str(v).lower() for v in PAL.values() if isinstance(v, str)}
                  | {c.lower() for c in C_EXT}
                  | {c.lower() for c in PAL["quartile_gradient"]}
                  | {c.lower() for c in QUARTILE_COLORS}
                  | {"rgba(108,122,137,0.15)", "rgba(0,114,178,0.25)",
                     "rgba(213,94,0,0.25)", "rgba(150,120,120,0.35)",
                     "rgba(153,153,153,0.45)", "rgba(213,94,0,0.35)",
                     "#aec7e8"})

EVENTS_REG = json.loads(
    (REPO / "docs/schemas/history_zoom_events_registry.json").read_text())
EVENTS_REG_VERSION = EVENTS_REG.get("x-version", "1.0.0")

GENERATED_BY = "Viz Vera — scripts/generate_charts_phlxsox_spy.py (pair260619_phlxsox_spy)"
SRC_DATA = "data/phlxsox_spy_daily_latest.parquet"


# ── Loaders ───────────────────────────────────────────────────────────────

def load_daily() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / "phlxsox_spy_daily_latest.parquet")


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
        return  # secondary-y dual-axis (single panel) — DP1 not applicable
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


# ── 1. Hero ───────────────────────────────────────────────────────────────

def chart_hero():
    df = load_daily()
    df = df[df["spy"].notna()]
    rs = df["sox_spy_ratio"].dropna()
    y0, y1 = df.index.min().year, df.index.max().year

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=rs.index, y=rs.values,
        name=f"{RS_LONG} ratio (SOX ÷ SPY)",
        line=dict(color=C_IND, width=1.6)), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["spy"],
        name=f"{TGT} price (USD)",
        line=dict(color=C_TGT, width=1.3)), secondary_y=True)
    add_nber_shading(fig, x_min=df.index.min(), x_max=df.index.max())
    nber_swatch(fig)
    fig.add_annotation(x="2000-03-10", y=float(rs.loc[:"2000-03-31"].iloc[-1]),
                       text="Dot-Com: semis peaked first,<br>led the broad market down",
                       showarrow=True, arrowhead=2, ax=60, ay=-50,
                       font=dict(size=10, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    fig.update_layout(
        title=(f"The Tradable Signal Is Relative Strength, Not Raw {IND_SHORT}: "
               f"{RS_LONG.title()} vs {TGT} ({y0}–{y1})"),
        template="plotly_white", hovermode="x unified", height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text="SOX ÷ SPY ratio (relative strength)", secondary_y=False)
    fig.update_yaxes(title_text=f"{TGT} price (USD)", secondary_y=True)
    save_chart("hero", fig,
               caption=(f"The {RS_LONG} ratio (vermillion, left axis) — {IND_SHORT} "
                        f"divided by {TGT} — against the {TGT} price (blue, right "
                        f"axis), {y0}–{y1}. Because {IND_SHORT} and {TGT} are both "
                        f"equity indices that co-move about 71% day-to-day, the "
                        f"analysis trades the RATIO, which strips out the shared "
                        f"market beta and isolates any genuine semiconductor "
                        f"leadership. Shaded bands mark NBER recessions."),
               alignment=("Hero shows the relative-strength ratio that the winner "
                          "actually uses, not raw SOX — the co-movement-vs-edge point."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-TX1", "VIZ-O1"],
               sources=[SRC_DATA])


# ── 2. Regime stats (VIZ-QR1 dual-panel) ──────────────────────────────────

def chart_regime_stats():
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>(Weakest rel. strength)", "Q2", "Q3",
              "Q4<br>(Strongest rel. strength)"]
    fig = make_dual_panel_regime_chart(
        quartile_labels=labels,
        sharpe=q["sharpe"].tolist(),
        ann_return_pct=(q["ann_return"] * 100).tolist(),
        signal_label=f"{RS_LONG} 6m momentum",
        x_axis_title=f"{RS_LONG} 6-month momentum quartile",
    )
    fig.update_layout(
        title=dict(
            text=(f"Mid Quartiles Beat the Extremes: {TGT} Performance by Lagged "
                  f"{RS_LONG.title()} Momentum Quartile"),
            y=0.99, yanchor="top"),
        margin=dict(t=150))
    save_chart("regime_stats", fig,
               caption=(f"{TGT} performance sorted by lagged {RS_LONG} 6-month-momentum "
                        f"quartile: Sharpe (left) and annualized return (right). The "
                        f"pattern is hump-shaped, NOT monotonic — Q2 (Sharpe "
                        f"{q['sharpe'].iloc[1]:.2f}) and Q3 ({q['sharpe'].iloc[2]:.2f}) "
                        f"are strongest while the extreme-weak Q1 is negative "
                        f"({q['sharpe'].iloc[0]:.2f}). This is descriptive context, "
                        f"not the tradable rule, and it does not by itself validate a "
                        f"clean procyclical gradient."),
               alignment=("VIZ-QR1 dual-panel from regime_quartile_returns.csv; hump "
                          "shape narrated honestly (not a clean monotone gradient)."),
               rules=["VIZ-QR1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/regime_quartile_returns.csv"],
               nber_required=False)


# ── 3. Correlation heatmap (forward, NOT contemporaneous) ─────────────────

_SIGLBL = {
    "rs_mom1m": "Rel-strength 1m momentum",
    "rs_mom3m": "Rel-strength 3m momentum",
    "rs_mom6m": "Rel-strength 6m momentum (winner)",
    "rs_mom12m": "Rel-strength 12m momentum",
    "rs_zscore126": "Rel-strength z-score (126d)",
    "rs_zscore252": "Rel-strength z-score (252d)",
    "sox_mom1m": "Raw SOX 1m momentum",
    "sox_mom3m": "Raw SOX 3m momentum",
    "sox_mom6m": "Raw SOX 6m momentum",
    "sox_mom12m": "Raw SOX 12m momentum",
    "hmm_stress": "HMM high-variance probability",
}


def chart_correlation_heatmap():
    c = pd.read_csv(CORE / "correlations.csv")
    p = c[c["metric"] == "pearson"].copy()
    p[["signal", "horizon"]] = p["pair_name"].str.split("__", expand=True)
    hor_order = [h for h in ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d",
                             "spy_fwd_63d", "spy_fwd_126d", "spy_fwd_252d"]
                 if h in set(p["horizon"])]
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
        zmin=-0.12, zmax=0.12, text=annot, texttemplate="%{text}",
        textfont={"size": 10}, name="Pearson r", showlegend=False))
    best = p.loc[p["value"].abs().idxmax()]
    # #177: the 0.709 same-day co-movement is referenced repeatedly in the text but
    # was invisible on this heatmap (which deliberately shows only FORWARD/predictive
    # correlations, lag>=1). Readers hunted for a value that wasn't shown. Surface it
    # as a clearly-labeled contemporaneous banner so text and chart align. Value is
    # read from the canonical CCF lag-0 (0.7088), not hardcoded.
    ccf0 = pd.read_csv(CORE / "ccf_prewhitened.csv")
    same_day = float(ccf0.loc[ccf0["lag"] == 0, "ccf"].iloc[0])
    fig.add_annotation(
        xref="paper", yref="paper", x=0.5, y=1.11, showarrow=False,
        text=(f"Same-day (lag 0) co-movement = {same_day:.3f} — shown separately "
              f"because it is shared market beta, NOT a forecast. This heatmap shows "
              f"only PREDICTIVE (forward, lag ≥ 1 day) correlations."),
        font=dict(size=11, color=C_EVENT), align="center",
        bgcolor=PAL["event_marker_label_bg"], borderpad=4)
    fig.update_layout(
        title=(f"Forward Correlations Are Tiny (R²~1%): Lagged Signals vs {TGT} "
               f"FUTURE Returns<br><sup>Pearson r; * p&lt;0.05, ** p&lt;0.01. "
               f"These are PREDICTIVE (forward) correlations, NOT the {same_day:.3f} "
               f"same-day co-movement (banner above).</sup>"),
        xaxis_title=f"{TGT} forward return horizon (trading days)",
        yaxis_title="Lagged signal",
        template="plotly_white", height=560, margin=dict(t=150))
    save_chart("correlation_heatmap", fig,
               caption=(f"Pearson correlations between lagged {IND_SHORT}-based signals "
                        f"and {TGT} FORWARD (future) returns. The largest cell is only "
                        f"r = {best['value']:.3f} — these predictive correlations are "
                        f"an order of magnitude smaller than the {same_day:.3f} same-day "
                        f"co-movement (shown in the banner above the chart), which is "
                        f"shared market beta and NOT a forecast. "
                        f"Relative-strength rows carry slightly more forward signal "
                        f"than raw-SOX rows."),
               alignment=("Heatmap makes the co-movement-vs-forecast distinction "
                          "visual: forward corrs are tiny; best cell re-read from CSV."),
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/correlations.csv"],
               nber_required=False)


# ── 4. CCF (pre-whitened) — emphasize bidirectional / symmetric mass ──────

def chart_ccf():
    d = pd.read_csv(CORE / "ccf_prewhitened.csv")
    # drop lag 0 (contemporaneous co-movement spike) from the bar emphasis by
    # coloring it neutral so the small lead/lag mass on both sides is legible
    colors = []
    for _, r in d.iterrows():
        if r["lag"] == 0:
            colors.append(C_NEUTRAL)
        elif r["significant"]:
            colors.append(C_IND)
        else:
            colors.append("#aec7e8")
    fig = go.Figure(go.Bar(x=d["lag"], y=d["ccf"], marker_color=colors,
                           name="Pre-whitened CCF"))
    ci = float(d["upper_ci"].iloc[0])
    lag0 = float(d.loc[d["lag"] == 0, "ccf"].iloc[0])
    # #179: lag 0 (0.71) dominates and compressed the small lead/lag mass (max ~0.05)
    # that is the actual evidence of bidirectional feedback. Clip the visible y-axis
    # to the lead/lag scale so those bars and the CI band are legible; the lag-0 bar
    # runs off the top and is annotated with its true value (bars are NOT modified —
    # only the view window is clipped, so plotted values remain faithful).
    nz_max = float(d.loc[d["lag"] != 0, "ccf"].abs().max())
    y_top = max(nz_max, ci) * 1.6
    fig.add_hline(y=ci, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8,
                  annotation_text="95% confidence band")
    fig.add_hline(y=-ci, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8)
    # lag-0 runs off the clipped axis: annotate at the top edge with its true value
    fig.add_annotation(x=0, y=y_top, ax=70, ay=-25,
                       text=(f"Lag 0 = {lag0:.3f} same-day co-movement<br>"
                             f"(shared beta — bar runs off the clipped axis)"),
                       showarrow=True, arrowhead=2,
                       font=dict(size=10, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    lead = int((d[(d["lag"] > 0) & d["significant"]]).shape[0])
    lag = int((d[(d["lag"] < 0) & d["significant"]]).shape[0])
    fig.update_layout(
        title=(f"Cross-Correlation Mass Sits on BOTH Sides: {IND_SHORT} vs {TGT} "
               f"Returns<br><sup>AR(1) pre-whitening. Significant cells on the lead "
               f"side ({lead}) and the lag side ({lag}) — feedback, not a one-way "
               f"lead.</sup>"),
        xaxis_title=f"Lag (trading days; positive = {IND_SHORT} leads {TGT})",
        yaxis=dict(title="Cross-correlation (axis clipped; lag 0 off-scale)",
                   range=[-y_top, y_top]),
        template="plotly_white", height=420, showlegend=False)
    save_chart("ccf_prewhitened", fig,
               caption=(f"Cross-correlation between AR(1) pre-whitened {IND_SHORT} and "
                        f"{TGT} daily returns at lags -20..+20. The y-axis is clipped to "
                        f"the lead/lag scale so the small significant cells are legible; "
                        f"the dominant lag-0 co-movement ({lag0:.3f}, shaded grey) runs "
                        f"off the top and is annotated with its true value. The residual "
                        f"significant cells fall on BOTH the lead side ({lead} cells) "
                        f"and the lag side ({lag} cells). This symmetric mass is the "
                        f"visual signature of bidirectional feedback, not a clean "
                        f"semiconductor lead."),
               alignment="CCF chart conveys bidirectional feedback; lag-0 flagged as co-movement.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/ccf_prewhitened.csv"],
               nber_required=False)


# ── 5. Granger F by lag — BOTH directions side by side (feedback) ─────────

def chart_granger():
    g = pd.read_csv(CORE / "granger_causality.csv")
    fwd = g[g["direction"] == "indicator_to_target"].sort_values("lag")
    rev = g[g["direction"] == "target_to_indicator"].sort_values("lag")
    # 5% critical F per lag — recover df grid from granger_by_lag
    bylag = pd.read_csv(RES / "granger_by_lag.csv").sort_values("lag")
    crit = [float(sstats.f.ppf(0.95, r["df_num"], r["df_den"]))
            for _, r in bylag.iterrows()]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=fwd["lag"], y=fwd["f_statistic"],
        name=f"{IND_SHORT} → {TGT} — significant at ALL lags",
        marker_color=C_IND))
    fig.add_trace(go.Bar(
        x=rev["lag"], y=rev["f_statistic"],
        name=f"{TGT} → {IND_SHORT} — ALSO significant at ALL lags",
        marker_color=C_TGT))
    fig.add_trace(go.Scatter(
        x=bylag["lag"], y=crit, mode="lines",
        name="5% critical value (per lag)",
        line=dict(color=C_EVENT, dash="dash", width=1.5)))
    fig.update_layout(
        title=(f"Causality Runs BOTH Ways — Feedback, Not a Clean {IND_SHORT} Lead "
               f"<br><sup>Toda-Yamamoto Granger F-statistics by lag. {IND_SHORT} → "
               f"{TGT} AND {TGT} → {IND_SHORT} both clear the 5% line at every tested "
               f"lag — two high-beta equity series pushing each other.</sup>"),
        xaxis_title="Lag (trading days)",
        # #178: large early-lag F-stats (up to ~40) compressed the later lags (~2-3),
        # making it hard to read whether each bar clears the 5% critical line. A log
        # y-axis equalizes the visual span so significance-vs-threshold — the actual
        # message — reads clearly at every lag. Bars/values are unchanged; only the
        # axis scale is log. The dashed critical-value line is the significance
        # reference to compare each bar against.
        yaxis=dict(title="F-statistic (log scale)", type="log"),
        barmode="group", template="plotly_white", height=480,
        margin=dict(b=140),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("granger_f_by_lag", fig,
               caption=(f"Toda-Yamamoto Granger F-statistics by lag, both directions. "
                        f"{IND_SHORT} → {TGT} (vermillion) AND {TGT} → {IND_SHORT} "
                        f"(blue) BOTH clear the 5% critical line at every tested lag "
                        f"(1, 2, 3, 5, 10, 21). The reverse direction is in fact the "
                        f"stronger of the two at short lags. This is bidirectional "
                        f"feedback between two high-beta equity indices — explicitly "
                        f"NOT evidence that semiconductors cleanly lead the market."),
               alignment=("BOTH directions rendered side by side as co-equal series; "
                          "title and caption state 'feedback, not clean lead' per "
                          "the binding reconciliation mandate."),
               rules=["VIZ-IC1", "VIZ-V3", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/granger_causality.csv",
                        f"results/{PAIR}/granger_by_lag.csv"],
               nber_required=False)


# ── 6. Incremental edge over SPY-own-momentum ─────────────────────────────

def chart_incremental_edge():
    ie = pd.read_csv(CORE / "incremental_edge_vs_spy_momentum.csv").sort_values("fwd_horizon_days")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    bar_colors = [C_POS if r["rs_adds_over_spy_own_momentum"] else C_NEUTRAL
                  for _, r in ie.iterrows()]
    fig.add_trace(go.Bar(
        x=[f"{int(h)}d" for h in ie["fwd_horizon_days"]],
        y=ie["incremental_r2"] * 100,
        marker_color=bar_colors,
        text=[f"+{v*100:.2f}pp<br>p={p:.3f}"
              for v, p in zip(ie["incremental_r2"], ie["rs_p_value"])],
        textposition="outside",
        name="Incremental R² from relative strength (pp)"), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=[f"{int(h)}d" for h in ie["fwd_horizon_days"]],
        y=ie["rs_p_value"], mode="lines+markers",
        name="Relative-strength coefficient p-value",
        line=dict(color=C_EVENT, width=2)), secondary_y=True)
    fig.add_hline(y=0.05, line_dash="dash", line_color=C_IND, line_width=1.2,
                  annotation_text="5% significance", secondary_y=True)
    fig.update_layout(
        title=(f"The Edge Over {TGT}'s OWN Momentum Is Marginal and Horizon-Dependent "
               f"<br><sup>Relative strength adds significantly at 21 days (p=0.033) "
               f"but NOT at 63 days (p=0.075); incremental R² ~1pp either way.</sup>"),
        xaxis_title="Forward return horizon",
        template="plotly_white", height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text="Incremental R² (percentage points)", secondary_y=False)
    fig.update_yaxes(title_text="Coefficient p-value", secondary_y=True,
                     range=[0, 0.15])
    save_chart("incremental_edge", fig,
               caption=(f"How much the lagged {RS_LONG} signal adds OVER {TGT}'s own "
                        f"63-day momentum, in a HAC local-projection regression. Green "
                        f"bars mark horizons where it adds significantly: at 21 days "
                        f"(p=0.033) it does; at 63 days (p=0.075) it does not. The "
                        f"incremental R² is about 1 percentage point at both horizons "
                        f"— a thin, horizon-dependent edge, not a robust one."),
               alignment=("Directly visualizes honesty mandate #3: marginal, horizon-"
                          "dependent edge over SPY-own-momentum; values from CSV."),
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/incremental_edge_vs_spy_momentum.csv"],
               nber_required=False)


# ── 7. Local projections (fwd + rev panels) ───────────────────────────────

def chart_local_projections():
    lp = pd.read_csv(CORE / "local_projections.csv")
    fig = make_subplots(rows=1, cols=2, shared_yaxes=False, subplot_titles=[
        f"{RS_LONG} → {TGT} (forward)",
        f"{TGT} → {RS_LONG} (reverse)"])
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
            name=("Coefficient: relative strength → market" if dirn == "fwd"
                  else "Coefficient: market → relative strength"),
            line=dict(color=color, width=2)), row=1, col=col)
        fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL,
                      line_width=0.8, row=1, col=col)
    pmin = lp[lp["direction"] == "fwd"]["p_value"].min()
    fig.update_layout(
        title=(f"Local Projections (HAC): Forward Coefficients Are Positive but Not "
               f"Significant<br><sup>Forward-direction p-values stay above 0.05 "
               f"(min p = {pmin:.2f}); CI bands include zero at every horizon</sup>"),
        template="plotly_white", height=460, margin=dict(b=120),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    fig.update_xaxes(title_text="Horizon (trading days)")
    fig.update_yaxes(title_text="Impulse response coefficient", row=1, col=1)
    save_chart("local_projections", fig,
               caption=(f"Local-projection impulse responses with HAC standard errors "
                        f"at 1/5/21/63/126-day horizons, both directions. The forward "
                        f"direction ({RS_LONG} → {TGT}, left) has positive point "
                        f"estimates that grow with horizon but never reach 5% "
                        f"significance (min p = {pmin:.2f}); the reverse panel shows a "
                        f"significant NEGATIVE 1-day coefficient — the market's own "
                        f"moves feed back into relative strength."),
               alignment="Dual-panel LP per ECON-H4; forward weak, reverse fed-back.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/local_projections.csv"],
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
        title=(f"Quantile Regression: Signal Bites in the DOWNSIDE, Fades in the Upside "
               f"<br><sup>{RS_LONG} on {TGT} forward returns; significant tau values: "
               f"{sig_tau}</sup>"),
        xaxis_title=f"Return quantile (tau) of {TGT}",
        yaxis_title="Coefficient",
        template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("quantile_coef", fig,
               caption=(f"Quantile-regression coefficient of {TGT} forward returns on "
                        f"the {RS_LONG} signal across return quantiles 0.05–0.95 with "
                        f"95% CI. The coefficient is positive and significant in the "
                        f"LOWER quantiles (tau 0.05–0.50) and fades to zero in the "
                        f"upper quantiles — the relative-strength signal carries more "
                        f"information about avoiding bad outcomes than about chasing "
                        f"big up-moves."),
               alignment="Coef-by-tau with CI band per ECON-H4; downside-tilt narrated.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv"],
               nber_required=False)


# ── 9. HMM regime probabilities ───────────────────────────────────────────

def chart_hmm():
    h = pd.read_parquet(CORE / "hmm_states.parquet")
    sc = "prob_stress" if "prob_stress" in h.columns else \
        [c for c in h.columns if "prob" in c][0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h.index, y=h[sc], mode="lines",
        name="P(high-variance relative-strength regime)",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.25)",
        line=dict(color=C_IND, width=1.0)))
    add_nber_shading(fig, x_min=h.index.min(), x_max=h.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Hidden Markov Model (HMM): High-Variance Regime in {RS_LONG.title()} "
               f"<br><sup>2-state HMM; 'stress' = high-variance regime (manifest "
               f"semantics). Used as a regime map, not the winning signal.</sup>"),
        xaxis_title="Date",
        yaxis_title="Probability of high-variance regime",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("hmm_regime_probs", fig,
               caption=(f"Probability that {RS_LONG} is in its high-variance regime "
                        f"(2-state HMM). The high-variance state clusters around the "
                        f"Dot-Com bust, the GFC, and the 2020/2022 drawdowns. This is "
                        f"a regime backdrop, not the winning signal, and does not "
                        f"rescue the strategy's statistical fragility. Shaded bands "
                        f"mark NBER recessions."),
               alignment=("Labels follow hmm_states_manifest semantics; relabelled in "
                          "plain English to avoid implying equity stress."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/hmm_states.parquet"])


# ── 10/11. Strategy equity curves (3-LINE) and drawdown ───────────────────

def _strategy_returns() -> pd.DataFrame:
    d = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    # Reconstruct SPY-own-momentum benchmark deterministically (verified to
    # reproduce winner_summary.spy_own_momentum_sharpe = 0.83):
    # long when trailing 63d SPY return > 0, lead 1d; else cash. Uses the SAME
    # SPY daily returns Evan saved as bh_return.
    spyret = d["bh_return"]
    mom63 = (1 + spyret).rolling(63).apply(np.prod, raw=True) - 1
    pos_mom = (mom63.shift(1) > 0).astype(float)
    d["spy_mom_return"] = pos_mom * spyret
    d["strategy_equity"] = (1 + d["strategy_return"]).cumprod()
    d["bh_equity"] = (1 + d["bh_return"]).cumprod()
    d["spy_mom_equity"] = (1 + d["spy_mom_return"].fillna(0)).cumprod()
    d["strategy_drawdown"] = d["strategy_equity"] / d["strategy_equity"].cummax() - 1
    d["bh_drawdown"] = d["bh_equity"] / d["bh_equity"].cummax() - 1
    d["spy_mom_drawdown"] = d["spy_mom_equity"] / d["spy_mom_equity"].cummax() - 1
    return d.reset_index()


def _verify_spy_mom(d: pd.DataFrame, w: dict) -> dict:
    oos = d.set_index("date").loc[w["oos_period_start"]:w["oos_period_end"]]
    r = oos["spy_mom_return"].dropna()
    sh = float(r.mean() / r.std() * np.sqrt(252))
    target = float(w["spy_own_momentum_sharpe"])
    verdict = "PASS" if abs(sh - target) <= 0.05 else "FAIL"
    if verdict == "FAIL":
        raise SystemExit(f"SPY-own-momentum reconstruction FAIL: {sh:.3f} vs {target:.3f}")
    return {"reconstructed_spy_mom_oos_sharpe": round(sh, 4),
            "winner_summary_value": target, "verdict": verdict}


def chart_equity_curves():
    d = _strategy_returns()
    w = load_winner()
    recon = _verify_spy_mom(d, w)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["strategy_equity"], mode="lines",
        name=f"{RS_LONG} Long/Cash winner (OOS Sharpe {w['oos_sharpe']:.2f})",
        line=dict(color=C_IND, width=2.4)))
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["bh_equity"], mode="lines",
        name=f"Buy & Hold {TGT} (OOS Sharpe {w['bh_sharpe']:.2f})",
        line=dict(color=C_BENCH, width=1.8, dash="dash")))
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["spy_mom_equity"], mode="lines",
        name=f"{TGT}-own-momentum benchmark (OOS Sharpe {w['spy_own_momentum_sharpe']:.2f})",
        line=dict(color=C_TGT, width=1.8, dash="dot")))
    fig.add_vline(x=w["oos_period_start"], line=dict(color=C_EVENT, dash="dot", width=1.3))
    fig.add_annotation(x=w["oos_period_start"], y=0.96, yref="paper", showarrow=False,
                       xanchor="left", text="OOS begins (2021-06)",
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=d["date"].min(), x_max=d["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Winner Beats BOTH Benchmarks Out-of-Sample — but Only in a "
               f"Favorable Semis-Bull Window<br><sup>The {TGT}-own-momentum line "
               f"(dotted) is the honesty anchor: the winner's edge over it is "
               f"marginal, and the winner LOST in every pre-2021 crisis.</sup>"),
        xaxis_title="Date",
        yaxis_title="Growth of 1.00",
        template="plotly_white", height=520, margin=dict(t=130),
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="left", x=0))
    save_chart("equity_curves", fig,
               caption=(f"Cumulative growth of 1.00 for three strategies: the {RS_LONG} "
                        f"Long/Cash winner (vermillion), Buy & Hold {TGT} (grey dash), "
                        f"and a {TGT}-own-momentum benchmark (blue dot). Out-of-sample "
                        f"(2021-06 onward) the winner's Sharpe ({w['oos_sharpe']:.2f}) "
                        f"beats both Buy & Hold ({w['bh_sharpe']:.2f}) and {TGT}-own-"
                        f"momentum ({w['spy_own_momentum_sharpe']:.2f}) — but that OOS "
                        f"window was a strong semiconductor bull, the in-sample Sharpe "
                        f"was just 0.10, and the rule lost in every prior crisis. The "
                        f"{TGT}-own-momentum line shows how thin the genuine edge is."),
               alignment=("3-LINE equity curve per binding brief requirement; SPY-own-"
                          "momentum reconstructed from saved SPY returns and verified "
                          "against winner_summary (Sharpe 0.83)."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               reconciliation={"spy_own_momentum": recon})


def chart_drawdown():
    # #181 (WINDOW BUG, diagnosed by Evan): drawdown was built from the FULL
    # 1994->2026 equity series, so the troughs read -64.97%@2009 (winner) and
    # -55.19% (B&H) — contradicting the OOS legend (-9.7% / -24.5%). Slice each
    # return series to the OOS window and re-base cummax to oos_period_start so
    # each curve's trough equals the canonical OOS drawdown. (equity_curves is
    # left full-sample on purpose — the "lost in every prior crisis" narrative.)
    d = _strategy_returns()
    w = load_winner()
    o_start, o_end = w["oos_period_start"], w["oos_period_end"]
    dd_df = d.set_index("date")

    def _oos_dd(ret_col):
        r = dd_df[ret_col].fillna(0).loc[o_start:o_end]
        eq = (1 + r).cumprod()  # re-based to 1.0 at OOS start
        return eq / eq.cummax() - 1

    strat_dd = _oos_dd("strategy_return")
    bh_dd = _oos_dd("bh_return")
    spymom_dd = _oos_dd("spy_mom_return")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strat_dd.index, y=strat_dd * 100, mode="lines",
        name=f"Winner drawdown (OOS max {w['oos_max_drawdown']*100:.1f}%)",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.35)",
        line=dict(color=C_IND, width=1.5)))
    fig.add_trace(go.Scatter(
        x=bh_dd.index, y=bh_dd * 100, mode="lines",
        name=f"Buy & Hold drawdown (OOS max {w['bh_max_drawdown']*100:.1f}%)",
        line=dict(color=C_BENCH, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(
        x=spymom_dd.index, y=spymom_dd * 100, mode="lines",
        name=f"{TGT}-own-momentum drawdown (OOS max {w['spy_own_momentum_max_drawdown']*100:.1f}%)",
        line=dict(color=C_TGT, width=1.3, dash="dot")))
    # NBER shading is still attempted, but the OOS window (2021-06 -> 2026-06)
    # contains NO NBER recession (COVID ended 2020-04, before OOS start), so no
    # shading rects are emitted. VIZ-NBER1's shape-presence assert is therefore
    # relaxed for this now-OOS-only chart (nber_required=False): there is
    # genuinely nothing in-window to shade. Before #181 this chart spanned
    # 1994->2026 and did carry recession shading.
    add_nber_shading(fig, x_min=strat_dd.index.min(), x_max=strat_dd.index.max())
    fig.update_layout(
        title=(f"Shallower Drawdowns Are the Rule's Real (Regime-Shaped) Benefit: "
               f"{w['oos_max_drawdown']*100:.1f}% vs {w['bh_max_drawdown']*100:.1f}% OOS"
               f"<br><sup>Out-of-sample window only ({o_start} to {o_end}); "
               f"cummax re-based to OOS start. No NBER recession falls in-window.</sup>"),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white", height=480, margin=dict(t=130, b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("drawdown", fig,
               nber_required=False,
               caption=(f"Drawdown paths for the winner, Buy & Hold {TGT}, and the "
                        f"{TGT}-own-momentum benchmark. In OOS the winner's max "
                        f"drawdown is {w['oos_max_drawdown']*100:.1f}% versus "
                        f"{w['bh_max_drawdown']*100:.1f}% for Buy & Hold — a real "
                        f"improvement, but one shaped by the benign 2021–26 regime "
                        f"rather than a tested all-weather property."),
               alignment=("Drawdown computed on the OOS window only (cummax re-based "
                          "to oos_period_start) from saved returns + reconstructed "
                          "SPY-momentum series, so troughs match the OOS legend."),
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


# ── 12/13. Tournament scatter + Sharpe distribution ───────────────────────

def _tournament_frames():
    t = load_tournament()
    bench_mask = t["signal"].isin(["BENCHMARK", "SPY_OWN_MOMENTUM"])
    valid = t[t["valid"] & ~bench_mask]
    bh = t[t["signal"] == "BENCHMARK"]
    spymom = t[t["signal"] == "SPY_OWN_MOMENTUM"]
    return t, valid, bh, spymom


def chart_tournament_scatter():
    t, valid, bh, spymom = _tournament_frames()
    bench_mask = t["signal"].isin(["BENCHMARK", "SPY_OWN_MOMENTUM"])
    invalid = t[(~t["valid"]) & ~bench_mask]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=invalid["annual_turnover"], y=invalid["oos_sharpe"], mode="markers",
        marker=dict(size=3, color="rgba(153,153,153,0.45)"), name="Invalid combos"))
    fig.add_trace(go.Scatter(
        x=valid["annual_turnover"], y=valid["oos_sharpe"], mode="markers",
        marker=dict(size=5, color=(valid["max_drawdown"] * 100),
                    colorscale="RdYlGn", colorbar=dict(title="Max DD (%)"),
                    opacity=0.6),
        text=[f"{r['signal']}/{r['threshold']}/{r['strategy']}/L{r['lead_days']}"
              for _, r in valid.iterrows()],
        hovertemplate="%{text}<br>Sharpe: %{y:.2f}<br>Turnover: %{x:.1f}/yr<extra></extra>",
        name="Valid strategies"))
    fig.add_trace(go.Scatter(
        x=[float(bh.iloc[0]["annual_turnover"])], y=[float(bh.iloc[0]["oos_sharpe"])],
        mode="markers", marker=dict(size=14, color=C_BENCH, symbol="diamond"),
        name=f"Buy & Hold {TGT} (Sharpe {float(bh.iloc[0]['oos_sharpe']):.2f})"))
    fig.add_trace(go.Scatter(
        x=[float(spymom.iloc[0]["annual_turnover"])], y=[float(spymom.iloc[0]["oos_sharpe"])],
        mode="markers", marker=dict(size=14, color=C_TGT, symbol="diamond"),
        name=f"{TGT}-own-momentum (Sharpe {float(spymom.iloc[0]['oos_sharpe']):.2f})"))
    top5 = valid.nlargest(5, "oos_sharpe")
    fig.add_trace(go.Scatter(
        x=top5["annual_turnover"], y=top5["oos_sharpe"], mode="markers",
        marker=dict(size=12, color=C_POS, symbol="star",
                    line=dict(width=1, color="#000000")),
        name="Top 5 by OOS Sharpe"))
    fig.update_layout(
        title=(f"Tournament: {len(t)-2:,} Strategy Combos ({len(valid):,} Valid) — "
               f"Winner Sharpe {valid['oos_sharpe'].max():.2f} vs Both Benchmarks ~0.82"),
        xaxis_title="Annual turnover (trades per year)",
        yaxis_title="OOS Sharpe ratio",
        template="plotly_white", height=540, margin=dict(b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("tournament_scatter", fig,
               caption=(f"All {len(t)-2:,} tournament combinations (OOS Sharpe vs annual "
                        f"turnover; color = max drawdown). {len(valid):,} pass validity. "
                        f"BOTH benchmark diamonds (Buy & Hold and {TGT}-own-momentum) "
                        f"sit near Sharpe 0.82–0.83; the winner is the best of "
                        f"thousands of tries — see the distribution chart for how the "
                        f"median combo actually fared."),
               alignment="Tournament scatter with BOTH benchmarks plotted (ECON-T4 rows).",
               rules=["VIZ-IC1", "ECON-T4", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
               nber_required=False)


def chart_tournament_dist():
    t, valid, bh, spymom = _tournament_frames()
    med = float(valid["oos_sharpe"].median())
    wmax = float(valid["oos_sharpe"].max())
    bhv = float(bh.iloc[0]["oos_sharpe"])
    fig = go.Figure(go.Histogram(
        x=valid["oos_sharpe"], nbinsx=60, marker_color=C_TGT, opacity=0.75,
        name=f"Valid strategies (n = {len(valid):,})"))
    fig.add_vline(x=med, line=dict(color=C_NEUTRAL, dash="dot", width=1.5))
    fig.add_vline(x=bhv, line=dict(color=C_BENCH, dash="dash", width=2))
    fig.add_vline(x=wmax, line=dict(color=C_IND, dash="dash", width=2))
    fig.add_annotation(x=wmax, y=1.0, yref="paper", showarrow=False, xanchor="right",
                       text=f"Winner = max of {len(valid):,} (median {med:.2f})",
                       font=dict(size=12, color=C_IND),
                       bgcolor=PAL["event_marker_label_bg"])
    fig.add_annotation(x=bhv, y=0.85, yref="paper", showarrow=False, xanchor="left",
                       text=f"Buy & Hold {TGT} = {bhv:.2f} — ABOVE the median strategy",
                       font=dict(size=12, color=C_BENCH),
                       bgcolor=PAL["event_marker_label_bg"])
    fig.add_annotation(x=med, y=0.65, yref="paper", showarrow=False, xanchor="right",
                       text=f"Median {med:.2f}", font=dict(size=11, color=C_NEUTRAL))
    fig.update_layout(
        title=(f"The MEDIAN Searched Strategy LOSES to Buy &amp; Hold: OOS Sharpe "
               f"Distribution Across {len(valid):,} Valid Combos"),
        xaxis_title="OOS Sharpe ratio",
        yaxis_title="Number of strategies",
        template="plotly_white", height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("tournament_sharpe_dist", fig,
               caption=(f"Distribution of OOS Sharpe across the {len(valid):,} valid "
                        f"strategy combos. The winner (Sharpe {wmax:.2f}) is the MAX of "
                        f"{len(valid):,} tries; the median combo scored just {med:.2f} "
                        f"— BELOW Buy & Hold {TGT} ({bhv:.2f}). The search mostly found "
                        f"losers, so the winner is best read as a tail draw, not a "
                        f"validated edge; bootstrap p = 0.041 (marginal)."),
               alignment=("VIZ-SCD1 position disclosure: winner is max of population "
                          "whose median underperforms B&H; numbers re-read from CSV."),
               rules=["VIZ-SCD1", "ECON-T4", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
               reconciliation={"valid_count": len(valid), "median_oos_sharpe": round(med, 4),
                               "winner_oos_sharpe": round(wmax, 4), "bh_oos_sharpe": round(bhv, 4)},
               nber_required=False)


# ── 14. Rolling correlation ───────────────────────────────────────────────

def chart_rolling_correlation():
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    ycol = "rolling_corr" if "rolling_corr" in rc.columns else \
        [c for c in rc.columns if "corr" in c.lower()][0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rc["date"], y=rc[ycol], mode="lines",
        name="Rolling correlation",
        line=dict(color=C_TGT, width=1.6)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_EVENT, line_width=1,
                  annotation_text="No correlation")
    add_nber_shading(fig, x_min=rc["date"].min(), x_max=rc["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"The Sign Is Unstable: Rolling Correlation, {RS_LONG.title()} Momentum "
               f"vs {TGT} Returns<br><sup>Sign agreement only "
               f"{sb['rolling_corr_sign_stability']:.2f} — verdict: "
               f"{sb['rolling_corr_stability_verdict'].replace('_', '-')}</sup>"),
        xaxis_title="Date",
        yaxis_title="Rolling correlation (r)",
        template="plotly_white", height=420,
        yaxis=dict(range=[-1, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("rolling_correlation", fig,
               caption=(f"Rolling correlation between the {RS_LONG} momentum signal and "
                        f"{TGT} returns. The sign agrees with its full-sample value "
                        f"only {sb['rolling_corr_sign_stability']:.0%} of the time "
                        f"(sign-unstable) — the relationship flips too often to lean "
                        f"on. Shaded bands mark NBER recessions."),
               alignment="Stability verdict quoted from structural_break JSON, not hard-coded.",
               rules=["VIZ-CP1.2", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/rolling_correlation_{PAIR}.csv",
                        f"results/{PAIR}/structural_break_{PAIR}.json"])


# ── 15. Structural break ──────────────────────────────────────────────────

def chart_structural_break():
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    df = load_daily()
    sig = df.loc[sb["sample_start"]:sb["sample_end"], "sox_spy_ratio_mom_6m_pct"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig.index, y=sig.values, mode="lines",
        name=f"{RS_LONG} 6-month momentum (%)", line=dict(color=C_IND, width=1.2)))
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
               f"{RS_LONG.title()} Momentum (p = {sb['p_value']:.2f})"),
        xaxis_title="Date",
        yaxis_title=f"{RS_LONG} 6-month momentum (%)",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("structural_break", fig,
               caption=(f"{RS_LONG} 6-month momentum over the test sample "
                        f"({sb['sample_start'][:7]}–{sb['sample_end'][:7]}, n = "
                        f"{sb['n_obs']}) with the Quandt-Andrews candidate break date "
                        f"({sb['break_date'][:7]}). The test does NOT flag a break "
                        f"(sup-F {sb['f_stat']:.2f}, residual-bootstrap p = "
                        f"{sb['p_value']:.2f}); the instability shows up in the rolling "
                        f"correlation's sign, not as a one-time break. Shaded bands "
                        f"mark NBER recessions."),
               alignment="Annotation-only chart per ECON-H4; values from JSON.",
               rules=["VIZ-CP1.3", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/structural_break_{PAIR}.json", SRC_DATA],
               extra_meta={"break_date": sb["break_date"],
                           "annotation_strategy_id": "manual_override"})


# ── 16. Sub-period / crisis Sharpe (stress_tests — winner LOST pre-OOS) ────

_EP_LABEL = {"Dot_Com": "Dot-Com 2000–02", "GFC": "GFC 2008–09",
             "COVID": "COVID 2020", "Rate_Hike_2022": "2022 Rates Shock"}


def chart_subperiod_sharpe():
    st = pd.read_csv(RES / "tournament_validation_20260619" / "stress_tests.csv")
    labels, w_vals, bh_vals = [], [], []
    for _, r in st.iterrows():
        labels.append(_EP_LABEL.get(r["period"], r["period"]))
        w_vals.append(float(r["winner_sharpe"]))
        bh_vals.append(float(r["buy_hold_sharpe"]))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=w_vals,
                         marker_color=[C_POS if v >= 0 else C_IND for v in w_vals],
                         text=[f"{v:+.2f}" for v in w_vals], textposition="outside",
                         name="Winner Sharpe"))
    fig.add_trace(go.Bar(x=labels, y=bh_vals, marker_color=C_BENCH,
                         text=[f"{v:+.2f}" for v in bh_vals], textposition="outside",
                         name=f"Buy & Hold {TGT} Sharpe"))
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"The Winner LOST in Every Pre-OOS Crisis: Sharpe by Historical Episode "
               f"<br><sup>Only the in-sample 2022 rates shock is positive; Dot-Com, "
               f"GFC and COVID are all deep negatives — the OOS bull window is doing "
               f"the heavy lifting.</sup>"),
        xaxis_title="Historical episode",
        yaxis_title="Annualized Sharpe ratio",
        barmode="group", template="plotly_white", height=440, margin=dict(b=90),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("subperiod_sharpe", fig,
               caption=(f"Winner-strategy Sharpe (vermillion/green) versus Buy & Hold "
                        f"{TGT} (grey) within each canonical crisis. The winner is "
                        f"deeply negative in Dot-Com (-1.16), GFC (-1.06) and COVID "
                        f"(-0.95) and only positive in the 2022 rates shock (+0.36) — a "
                        f"blunt reminder that the headline OOS Sharpe rests on the "
                        f"benign 2021–26 semiconductor bull, not on crisis resilience."),
               alignment=("Crisis Sharpe from stress_tests.csv; the pre-OOS losses are "
                          "the central fragility evidence (honesty mandate #4)."),
               rules=["ECON-CP1", "VIZ-CP1.1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_validation_{DATE_TAG}/stress_tests.csv"],
               nber_required=False)


# ── 17. History zoom charts (4 episodes, dual-panel) ──────────────────────

def _window_has_recession(start: str, end: str) -> bool:
    from _nber import RECESSIONS
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return any(pd.Timestamp(r0) <= e and pd.Timestamp(r1) >= s for r0, r1 in RECESSIONS)


def chart_history_zoom(slug: str):
    ep = EVENTS_REG["episodes"][slug]
    df = load_daily()
    w = df.loc[ep["start_date"]:ep["end_date"]]
    rs = w["sox_spy_ratio"].dropna()
    spy = w["spy"].dropna()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[f"{RS_LONG} ratio (SOX ÷ SPY)",
                                        f"{TGT} price (USD)"])
    fig.add_trace(go.Scatter(x=rs.index, y=rs.values,
                             name=f"{RS_LONG} ratio",
                             line=dict(color=C_IND, width=1.8)), row=1, col=1)
    fig.add_trace(go.Scatter(x=spy.index, y=spy.values,
                             name=f"{TGT} price (USD)",
                             line=dict(color=C_TGT, width=1.8)), row=2, col=1)
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
        title=(f"{RS_LONG.title()} and {TGT} During the {ep['episode_name']}, "
               f"{ep['start_date'][:4]}–{ep['end_date'][:4]}"),
        template="plotly_white", height=560,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1))
    fig.update_xaxes(matches="x2", showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=True, title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="SOX ÷ SPY ratio", row=1, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    save_chart(f"history_zoom_{slug}", fig,
               caption=(f"{RS_LONG} ratio (top) and {TGT} price (bottom) through the "
                        f"{ep['episode_name']} window ({ep['start_date'][:7]} to "
                        f"{ep['end_date'][:7]}), with registry event markers."
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
               nber_required=has_rec)


# ── CP2 skip sidecars (VIZ-CP1-G skip protocol) ───────────────────────────

def write_cp2_skips():
    for c in ("rolling_sharpe_cp", "rolling_granger"):
        (OUT / f"chart_skip_{c}.json").write_text(json.dumps({
            "chart_name": c,
            "pair_id": PAIR,
            "skipped_by": "VIZ-CP1-G",
            "reason": ("ECON-CP2 (durability) artifacts intentionally absent for this "
                       "pair: structural_break_phlxsox_spy.json carries cp2_note 'CP2 "
                       "skipped — regime_story not set in signal_scope.json'. No "
                       "upstream rolling-Sharpe or rolling-Granger result file exists "
                       "to chart."),
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
    chart_incremental_edge()
    chart_local_projections()
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
