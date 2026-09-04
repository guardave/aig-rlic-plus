#!/usr/bin/env python3
"""Chart generation: Cass Freight Index (Shipments, FRGSHPUSM649NCIS) x SPY.

Producer for the cass_freight_spy standard chart set (rebuilt 20260829 after the
Step C #198 Data Master history splice extended the pair to 1990-2026). Consumes
results/cass_freight_spy/ (winner_summary.json, tournament_results_20260829.csv,
strategy_returns_20260829.csv, subperiod_sharpe.csv, regime_quartile_returns.csv,
granger_by_lag.csv, core_models_20260829/*, rolling_correlation_*.csv,
structural_break_*.json, lead_correlation_20260829.csv, lead_tournament_20260829.csv)
plus Dana's monthly dataset. Strategy charts use the saved return series; they do
NOT re-run strategy selection.

Framing (binding — do NOT oversell; every number sourced from results/):
  * Winner = cass_freight_contraction (freight-recession flag) / T3_zscore_neg_1.0 /
    P1 Long-Cash, PROCYCLICAL orientation / L9 (9-month lead) / LB36.
    OOS Sharpe 1.30 vs B&H 0.93; ann return 17.4% vs 15.4%; max DD -19.5% vs -23.9%.
    OOS window 2018-04-30 -> 2026-07-31 (100 months ~= 8.3 years) — now CLEARS the
    5-year reliability floor (the old <5yr caveat is retired).
  * Still a FOUND-IN-SEARCH CANDIDATE: median valid combo Sharpe 0.77 UNDERPERFORMS
    B&H 0.93; winner is the right tail of a 16,080-combo search (11,501 valid);
    bootstrap p = 0.0852 (NOT significant at 5%); IS Sharpe 0.61 vs OOS 1.30.
  * Causality: forward Granger NONE (Cass does NOT Granger-cause SPY; min p 0.39);
    reverse SPY->Cass significant at lags [1,2,3,5,6] -> classified 'lagging'.
    Freight is a procyclical coincident/lagging demand overlay, NOT a forecast.
  * L9 lead is a likely search artifact (freight is coincident; issue #28 tracks the
    fleet-wide L9 pattern). Adjacent-lead durability is a caution.
  * Drawdown reduction (-19.5% vs -23.9%) is the defensible virtue — read the Sharpe
    edge as volatility avoidance (sitting out deep-contraction months).
  * NSA: the Cass source is NOT seasonally adjusted; MoM/3M/6M/level-zscore signals
    are seasonally contaminated. The winner (contraction) is on the seasonally-CLEAN
    set. The globally highest raw combo (accel/L3, OOS Sharpe 1.47) is contaminated
    and excluded by design.
  * History now spans dot-com, GFC, COVID, 2022. The strategy OOS window is 2018+, so
    dot-com/GFC remain insufficient_data for the STRATEGY (in-sample); the indicator
    history-zoom charts DO now show those episodes.

Charts produced (output/charts/cass_freight_spy/plotly/, bare names):
    hero, regime_stats, correlation_heatmap, correlations_lead_view,
    lead_sharpe_distribution, ccf_prewhitened, granger_f_by_lag, local_projections,
    transfer_entropy, quantile_coef, hmm_regime_probs, equity_curves, drawdown,
    tournament_scatter, tournament_sharpe_dist, rolling_correlation, structural_break,
    subperiod_sharpe, walk_forward, history_zoom_{dotcom,gfc,covid,inflation_2022}
    + chart_skip_{rolling_sharpe_cp,rolling_granger}.json (CP2 absent: regime_story=false).

Author: Viz (rebuild). Date: 2026-08-29.
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

PAIR = "cass_freight_spy"
DATE_TAG = "20260829"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

IND_LONG = "Cass Freight Index (Shipments)"
IND_SHORT = "Cass Freight"
IND_YOY = "Cass Freight YoY"
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

GENERATED_BY = "Viz — scripts/generate_charts_cass_freight_spy.py (cass_freight_spy rebuild)"
SRC_DATA = "data/cass_freight_spy_monthly_latest.parquet"
YOY_COL = "cass_freight_pct_yoy"

# Winner combo coordinates (winner_summary.json raw_winner_row).
WIN_SIGNAL_RAW = "contraction"
WIN_THRESHOLD = "T3_zscore_neg_1.0"
WIN_STRATEGY_RAW = "P1_long_cash_counter"
WIN_LOOKBACK = "LB36"
WIN_LEAD = 9
BOOT_P = 0.0852  # winner_summary.notes: winner bootstrap p=0.0852 (vs resampled B&H)


# ── Loaders ─────────────────────────────────────────────────────────────────
def load_monthly() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / f"{PAIR}_monthly_latest.parquet")


def load_tournament() -> pd.DataFrame:
    return pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")


def load_winner() -> dict:
    return json.loads((RES / "winner_summary.json").read_text())


# ── Gates ─────────────────────────────────────────────────────────────────
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
    for txt in _all_text(fig):
        if str(txt).count("$") > 1:
            violations.append(f"VIZ-TX1: text has >1 literal '$': {txt!r}")
    if violations:
        for v in violations:
            print(f"    VIZ-IC1 VIOLATION [{name}]: {v}")
        raise SystemExit(f"VIZ-IC1 pre-save check failed for {name}; save blocked.")
    print(f"    VIZ-IC1 PASS [{name}]")


def _all_text(fig: go.Figure):
    if fig.layout.title and fig.layout.title.text:
        yield fig.layout.title.text
    for a in fig.layout.annotations or ():
        if a.text:
            yield a.text
    for tr in fig.data:
        if getattr(tr, "name", None):
            yield tr.name


def assert_nber(fig: go.Figure, name: str) -> None:
    n = sum(1 for s in (fig.layout.shapes or ())
            if s.fillcolor and "rgba(150" in s.fillcolor.replace(" ", ""))
    if n == 0:
        raise SystemExit(f"VIZ-NBER1 FAIL: {name} has no NBER shading shapes.")
    print(f"    VIZ-NBER1 PASS [{name}]: {n} shape(s)")


def save_chart(name: str, fig: go.Figure, *, caption: str, alignment: str,
               rules: list, sources: list,
               reconciliation: dict | None = None,
               extra_meta: dict | None = None,
               nber_required: bool = True) -> None:
    if fig.layout.title is None or not fig.layout.title.text:
        raise SystemExit(f"{name} has no self-title (VIZ-O1).")
    validate_intra_chart_consistency(fig, name)
    if nber_required:
        assert_nber(fig, name)
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
    except Exception as exc:  # Kaleido/Chrome may be unavailable; JSON is what matters.
        png = f" (png skipped: {type(exc).__name__})"
    print(f"  wrote {name}.json (+sidecar{png})")


def nber_swatch(fig: go.Figure) -> None:
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square"),
        name="NBER recession (shaded)", hoverinfo="skip"))


# ── 1. Hero — Cass Freight YoY vs SPY ─────────────────────────────────────
def chart_hero():
    df = load_monthly()
    df = df[df["spy"].notna()]
    yoy = df[YOY_COL].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=yoy.index, y=yoy.values, name=f"{IND_YOY} (%)",
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
                       text="2009: GFC freight trough<br>(fell with the market)",
                       showarrow=True, arrowhead=2, ax=-40, ay=-40,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    fr_idx = yoy.loc["2022-06-30":"2024-06-30"].idxmin()
    fig.add_annotation(x=fr_idx.strftime("%Y-%m-%d"), y=float(yoy.loc[fr_idx]),
                       text="2022-24: freight recession<br>(coincided with the equity de-rating)",
                       showarrow=True, arrowhead=2, ax=30, ay=40,
                       font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    y0, y1 = df.index.min().year, df.index.max().year
    fig.update_layout(
        title=(f"Cass Freight Year-over-Year Growth vs {TGT}: A Procyclical "
               f"Goods-Economy Gauge ({y0}–{y1})"),
        template="plotly_white", hovermode="x unified", height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text=f"{IND_YOY} (%)", secondary_y=False)
    fig.update_yaxes(title_text=f"{TGT} price (USD)", secondary_y=True)
    save_chart("hero", fig,
               caption=(f"Cass Freight year-over-year shipment growth (FRED FRGSHPUSM649NCIS, "
                        f"NSA; vermillion, left axis) against the {TGT} price (blue, right "
                        f"axis), {y0}–{y1}. The two series broadly rise and fall together "
                        f"(the 2009 GFC trough and the 2022–24 freight recession are the "
                        f"key episodes) — the signature of a procyclical, coincident/lagging "
                        f"indicator, not a leading one. The source is not seasonally adjusted, so "
                        f"the year-over-year change is shown as the seasonally-robust growth "
                        f"signal. Shaded bands mark NBER recessions."),
               alignment=("Hero shows YoY growth (seasonally-robust; never the raw NSA level) "
                          "with the 0% line and the two freight episodes."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-TX1", "VIZ-O1"],
               sources=[SRC_DATA])


# ── 2. Regime stats (dual-panel quartiles) ────────────────────────────────
def chart_regime_stats():
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    labels = ["Q1<br>(Weakest freight growth)", "Q2", "Q3", "Q4<br>(Strongest freight growth)"]
    fig = make_dual_panel_regime_chart(
        quartile_labels=labels,
        sharpe=q["sharpe"].tolist(),
        ann_return_pct=(q["ann_return"] * 100).tolist(),
        signal_label="Cass Freight growth",
        x_axis_title="Cass Freight growth quartile (Q1=Weak, Q4=Strong)",
    )
    fig.update_layout(
        title=dict(
            text=(f"Broadly Procyclical Quartile Pattern: SPY Performance by Cass Freight "
                  f"Growth Quartile<br>"
                  f"<sup>Q1={q['sharpe'].iloc[0]:.2f} / Q2={q['sharpe'].iloc[1]:.2f} / "
                  f"Q3={q['sharpe'].iloc[2]:.2f} / Q4={q['sharpe'].iloc[3]:.2f} — highest at "
                  f"Q4 (strong freight = risk-on); mild non-monotonicity at Q2–Q3</sup>"),
            ),  # #186-class fix: no y/yanchor override — let plotly auto-place the
                # 2-line title in the top margin so the first line is not clipped
        margin=dict(t=160))
    save_chart("regime_stats", fig,
               caption=(f"SPY performance by Cass Freight growth quartile (concurrent, "
                        f"descriptive): Sharpe and annualized return. The gradient is broadly "
                        f"procyclical — Sharpe is lowest in the weakest-freight quartile "
                        f"(Q1 {q['sharpe'].iloc[0]:.2f}) and highest in the strongest "
                        f"(Q4 {q['sharpe'].iloc[3]:.2f}), with a mild non-monotonicity between "
                        f"Q2 ({q['sharpe'].iloc[1]:.2f}) and Q3 ({q['sharpe'].iloc[2]:.2f}). "
                        f"This matches the procyclical winner (long SPY when freight is not "
                        f"contracting). Descriptive, not a forecast."),
               alignment=("VIZ-QR1 dual-panel from regime_quartile_returns.csv; broadly "
                          "procyclical gradient with honest note on the Q2–Q3 wobble."),
               rules=["VIZ-QR1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/regime_quartile_returns.csv"],
               nber_required=False)


# ── 3. Correlation heatmap ────────────────────────────────────────────────
_SIGLBL = {
    "yoy": "YoY growth", "mom": "MoM growth", "mom3m": "3M change",
    "mom6m": "6M change", "3m": "3M change", "6m": "6M change",
    "dev_trend": "Trend deviation", "accel": "Acceleration",
    "level_zscore_60m": "Level z-score (60m)", "zscore_60m": "Level z-score (60m)",
    "yoy_zscore_60m": "YoY z-score (60m)", "yoy_zscore": "YoY z-score",
    "contraction": "Contraction flag (winner signal)",
    "hmm_stress": "HMM high-variance probability",
    "markov_regime": "Markov high-variance probability",
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
        title=(f"Forward Correlations: Cass Freight Signals vs {TGT} Forward Returns"
               f"<br><sup>Pearson r; * p&lt;0.05, ** p&lt;0.01. "
               f"Strongest cell: {_SIGLBL.get(best['signal'].split('__')[0], best['signal'].split('__')[0])} "
               f"r = {best['value']:.3f}</sup>"),
        xaxis_title=f"{TGT} forward return horizon",
        yaxis_title="Cass Freight signal",
        template="plotly_white", height=540)
    save_chart("correlation_heatmap", fig,
               caption=(f"Pearson correlations between Cass Freight signals and {TGT} forward "
                        f"returns at 1/3/6/12-month horizons. The grid is pale at every "
                        f"tradeable horizon — the strongest cell is only "
                        f"r = {best['value']:.3f} ({best['pair_name'].replace('__',' vs ')}). "
                        f"Consistent with a coincident/lagging series carrying little forward "
                        f"linear content."),
               alignment="Modest/near-zero forward linear evidence; triage before formal tests.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/correlations.csv"],
               nber_required=False)


# ── 3b. Lead-correlation heatmap (VIZ-LEAD1) ───────────────────────────────
_LEAD_SIGLBL = {
    "cass_freight_pct_yoy": "YoY growth",
    "cass_freight_pct_mom": "MoM growth",
    "cass_freight_3m_pct": "3M change",
    "cass_freight_6m_pct": "6M change",
    "cass_freight_dev_trend_pct": "Trend deviation",
    "cass_freight_zscore_60m": "Level z-score (60m)",
    "cass_freight_yoy_zscore_60m": "YoY z-score (60m)",
    "cass_freight_accel_pct": "Acceleration",
    "cass_freight_contraction": "Contraction flag (winner signal)",
}


def _parse_lead_cell(s: str):
    """Return (float, star_suffix) from a cell like '+0.113*' or '-0.015'."""
    s = str(s).strip()
    star = ""
    while s.endswith("*"):
        star += "*"
        s = s[:-1]
    try:
        return float(s), star
    except ValueError:
        return float("nan"), star


def chart_correlations_lead_view():
    d = pd.read_csv(RES / f"lead_correlation_{DATE_TAG}.csv")
    lead_cols = [c for c in d.columns if c.startswith("L") and c[1:].isdigit()]
    lead_cols = sorted(lead_cols, key=lambda c: int(c[1:]))
    z, txt, ylabels = [], [], []
    for _, r in d.iterrows():
        vals, cells = [], []
        for lc in lead_cols:
            v, star = _parse_lead_cell(r[lc])
            vals.append(v)
            cells.append(("" if pd.isna(v) else f"{v:+.2f}") + star)
        z.append(vals)
        txt.append(cells)
        ylabels.append(_LEAD_SIGLBL.get(r["transform"], r["transform"]))
    xlabels = [f"L{int(c[1:])}" for c in lead_cols]
    fig = go.Figure(go.Heatmap(
        z=z, x=xlabels, y=ylabels, colorscale="RdBu", zmid=0,
        zmin=-0.25, zmax=0.25, text=txt, texttemplate="%{text}",
        textfont={"size": 9}, name="Pearson r", showlegend=False))
    fig.update_layout(
        title=(f"Lead View: Cass Freight Signals (Lagged L Months) vs {TGT} 1-Month "
               f"Forward Return<br><sup>Pearson r; * p&lt;0.05. No lead carries stable "
               f"forward content — the winner signal (contraction) peaks only at "
               f"L{WIN_LEAD} (r ≈ +0.07)</sup>"),
        xaxis_title="Signal lead (months; L0 contemporaneous, non-tradable)",
        yaxis_title="Cass Freight signal transform",
        template="plotly_white", height=520)
    save_chart("correlations_lead_view", fig,
               caption=(f"Pearson correlations between each Cass Freight signal lagged L "
                        f"months and the {TGT} 1-month forward return. Cells are small at "
                        f"nearly every lead and the few starred ones are scattered and flip "
                        f"sign across transforms — the signature of a coincident series "
                        f"with no stable predictive lead. The winner's own signal (the "
                        f"contraction flag) is weak across the whole row, peaking only at "
                        f"L{WIN_LEAD} — which is why the deployed L{WIN_LEAD} lead is best "
                        f"read as a likely search artifact (issue #28)."),
               alignment=(f"Honest near-null lead view; winner signal 'contraction' peaks "
                          f"at L{WIN_LEAD} but weakly."),
               rules=["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               sources=[f"results/{PAIR}/lead_correlation_{DATE_TAG}.csv"],
               extra_meta={"method_name": "lead_correlation_view",
                           "expected_chart_type": "heatmap"},
               nber_required=False)


# ── 3c. Lead-Sharpe distribution (VIZ-LEAD1, GH #13) ───────────────────────
def chart_lead_sharpe_distribution():
    lt = pd.read_csv(RES / f"lead_tournament_{DATE_TAG}.csv").sort_values("lead_months")
    t = load_tournament()
    w = load_winner()
    bh = float(w["bh_sharpe"])
    # Clean-signal best OOS Sharpe per lead — the population the winner is chosen from.
    valid = t[(t["valid"]) & (t["signal"] != "BENCHMARK") & (t["seasonally_clean"])]
    clean_env = valid.groupby("lead_months")["oos_sharpe"].max().reindex(lt["lead_months"].values)
    # Winner signal's OWN Sharpe-by-lead curve.
    wc = t[(t["signal"] == WIN_SIGNAL_RAW) & (t["threshold"] == WIN_THRESHOLD)
           & (t["strategy"] == WIN_STRATEGY_RAW) & (t["lookback"] == WIN_LOOKBACK)]
    wc = wc.set_index("lead_months")["oos_sharpe"].reindex(lt["lead_months"].values)
    raw_env = lt.set_index("lead_months")["best_oos_sharpe"]
    raw_peak_lead = int(raw_env.idxmax())
    raw_peak = float(raw_env.max())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=lt["lead_months"], y=clean_env.values,
        marker_color=C_TGT, opacity=0.55,
        name="Best seasonally-CLEAN combo per lead (selection population)"))
    fig.add_trace(go.Scatter(
        x=lt["lead_months"], y=raw_env.values, mode="lines+markers",
        line=dict(color=C_NEUTRAL, width=1.4, dash="dot"),
        marker=dict(size=6, color=C_NEUTRAL),
        name="Best of ANY signal per lead (incl. seasonally-contaminated, excluded)"))
    fig.add_trace(go.Scatter(
        x=wc.index, y=wc.values, mode="lines+markers",
        line=dict(color=C_IND, width=2.2), marker=dict(size=7, color=C_IND),
        name="Winner signal (contraction) traced across leads"))
    fig.add_trace(go.Scatter(
        x=[WIN_LEAD], y=[float(w["oos_sharpe"])], mode="markers",
        marker=dict(size=16, color=C_POS, symbol="star", line=dict(width=1, color="#000000")),
        name=f"Published winner L{WIN_LEAD} (Sharpe {w['oos_sharpe']:.2f})"))
    fig.add_hline(y=bh, line=dict(color=C_BENCH, dash="dash", width=1.8),
                  annotation_text=f"Buy & Hold {TGT} = {bh:.2f}",
                  annotation_position="bottom right")
    fig.update_layout(
        title=(f"Lead Sweep: OOS Sharpe by Monthly Lead — Published Winner L{WIN_LEAD} "
               f"({w['oos_sharpe']:.2f}) Is the Best CLEAN Combo<br><sup>The taller raw bar at "
               f"L{raw_peak_lead} ({raw_peak:.2f}) is a seasonally-contaminated signal excluded "
               f"by design; OOS now 100 months (≈8.3yr, clears the 5yr floor)</sup>"),
        xaxis_title="Signal lead (months)", yaxis_title="OOS Sharpe ratio",
        template="plotly_white", height=480, margin=dict(b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0))
    fig.update_xaxes(dtick=1)
    save_chart("lead_sharpe_distribution", fig,
               caption=(f"OOS Sharpe across the tradable monthly lead grid L1–L12. Bars are "
                        f"the best seasonally-CLEAN combo at each lead (the population the "
                        f"winner is drawn from); the vermillion line traces the winner's own "
                        f"signal (the contraction flag). The published winner (star) sits at "
                        f"L{WIN_LEAD} with OOS Sharpe {w['oos_sharpe']:.2f}. The grey dotted "
                        f"line (best of ANY signal) peaks higher at L{raw_peak_lead} "
                        f"({raw_peak:.2f}), but that peak rides a seasonally-contaminated "
                        f"transform (the Cass source is NSA) and is excluded. Read the "
                        f"uneven, adjacent-lead profile as a caution: L{WIN_LEAD} is a likely "
                        f"search artifact for a coincident series (issue #28)."),
               alignment=(f"Published L{WIN_LEAD} winner is the best CLEAN combo; the taller "
                          f"raw bar at L{raw_peak_lead} is contaminated and excluded."),
               rules=["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               sources=[f"results/{PAIR}/lead_tournament_{DATE_TAG}.csv",
                        f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               reconciliation={"winner_lead": WIN_LEAD,
                               "winner_oos_sharpe": round(float(w["oos_sharpe"]), 4),
                               "raw_envelope_peak_lead": raw_peak_lead,
                               "raw_envelope_peak": round(raw_peak, 4),
                               "bh_sharpe": round(bh, 4)},
               extra_meta={"method_name": "lead_sharpe_distribution",
                           "expected_chart_type": "bar", "gh_issue": "13"},
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
    sig_lags = [int(x) for x in d.loc[d["significant"], "lag"].tolist()]
    fig.update_layout(
        title=(f"Pre-Whitened Cross-Correlation: {IND_YOY} vs {TGT} Returns "
               f"<br><sup>AR pre-whitening; {nsig} of {len(d)} lags significant, all on the "
               f"stocks-lead side (negative lags) — none where freight leads</sup>"),
        xaxis_title=f"Lag (months; negative = {TGT} leads {IND_SHORT} / freight lags)",
        yaxis_title="Cross-correlation",
        template="plotly_white", height=400, showlegend=False)
    save_chart("ccf_prewhitened", fig,
               caption=(f"Cross-correlation between pre-whitened {IND_YOY} and {TGT} returns. "
                        f"{nsig} of {len(d)} lags clear the 95% band, at lags {sig_lags} — "
                        f"all on the side where the market leads freight, none on the "
                        f"freight-leads side. No forward Granger causality was found, "
                        f"consistent with the coincident/lagging classification."),
               alignment="CCF corroborates the absent forward lead; only stocks-lead bars survive.",
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
        name=f"{IND_SHORT} → {TGT} (forward) — significant at lags {fwd_sig or 'NONE'}",
        marker_color=C_IND))
    fig.add_trace(go.Bar(
        x=rev["lag"], y=rev["f_statistic"],
        name=f"{TGT} → {IND_SHORT} (reverse) — significant at lags {rev_sig or 'NONE'}",
        marker_color="#aec7e8"))
    fig.add_trace(go.Scatter(
        x=bylag.sort_values("lag")["lag"], y=crit, mode="lines",
        name="5% critical value (per lag)",
        line=dict(color=C_EVENT, dash="dash", width=1.5)))
    fig.update_layout(
        title=(f"Reverse-Only Causality: {TGT} Leads Freight; Forward Is Absent"
               f"<br><sup>Toda-Yamamoto Granger F by lag; forward ({IND_SHORT}→{TGT}) "
               f"significant at {fwd_sig or 'NONE'}; reverse ({TGT}→{IND_SHORT}) at "
               f"{rev_sig or 'NONE'}</sup>"),
        xaxis_title="Lag (months)", yaxis_title="F-statistic",
        barmode="group", template="plotly_white", height=480, margin=dict(b=160),
        legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="left", x=0))
    save_chart("granger_f_by_lag", fig,
               caption=(f"Toda-Yamamoto Granger F-statistics at lags 1–12, both "
                        f"directions. {IND_SHORT} → {TGT} (vermillion, forward) does NOT "
                        f"clear the 5% line at any lag (min p 0.39). {TGT} → {IND_SHORT} "
                        f"(pale blue, reverse) is significant at lags {rev_sig}. This "
                        f"reverse-only pattern says equities move first and freight follows — "
                        f"freight is a coincident/lagging demand overlay, not a forward "
                        f"forecaster."),
               alignment=("Both directions shown; forward absent, reverse dominates — the "
                          "honest lagging-indicator causality picture."),
               rules=["VIZ-IC1", "VIZ-V3", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/granger_causality.csv",
                        f"results/{PAIR}/granger_by_lag.csv"],
               reconciliation={"forward_significant_lags": [int(x) for x in fwd_sig],
                               "reverse_significant_lags": [int(x) for x in rev_sig],
                               "verdict": "no_forward_causality_lagging"},
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
            name=("Coefficient: freight → market" if dirn == "fwd"
                  else "Coefficient: market → freight"),
            line=dict(color=color, width=2)), row=1, col=col)
        fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL,
                      line_width=0.8, row=1, col=col)
    pmin = lp[lp["direction"] == "fwd"]["p_value"].min()
    fig.update_layout(
        title=(f"Local Projections (HAC): Forward Impulse Response of {TGT} to "
               f"{IND_YOY}<br><sup>Forward-direction minimum p = {pmin:.2f}; no forward "
               f"predictive content at any horizon</sup>"),
        template="plotly_white", height=460, margin=dict(b=120),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    fig.update_xaxes(title_text="Horizon (months)")
    fig.update_yaxes(title_text="Impulse response coefficient", row=1, col=1)
    save_chart("local_projections", fig,
               caption=(f"Local-projection impulse responses with HAC standard errors at "
                        f"horizons 1/3/6/12 months, both directions. The forward direction "
                        f"({IND_SHORT} → {TGT}) has minimum p = {pmin:.2f}; the response is "
                        f"indistinguishable from zero at every horizon, matching the "
                        f"no-forward Granger verdict."),
               alignment="Dual-panel LP; forward weakness supports the coincident/lagging framing.",
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
               f"forward p = {fwd_p:.2f}, reverse p = {rev_p:.2f} — neither significant</sup>"),
        yaxis_title="Transfer entropy (nats)", xaxis_title="Direction",
        template="plotly_white", height=400, showlegend=False)
    save_chart("transfer_entropy", fig,
               caption=(f"Transfer entropy between {IND_YOY} and {TGT} returns (tercile bins, "
                        f"500 permutations). Forward p = {fwd_p:.2f}, reverse p = {rev_p:.2f}; "
                        f"neither direction clears 5% — no non-linear channel rescues the "
                        f"indicator, consistent with the absent forward Granger result."),
               alignment="Two-bar TE comparison; no significant flow either way.",
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
        title=(f"Quantile Regression: {IND_YOY} on {TGT} Forward Returns "
               f"<br><sup>Coefficient by return quantile; significant tau: "
               f"{sig_tau or 'NONE at the tradeable tails'}</sup>"),
        xaxis_title=f"Return quantile (tau) of {TGT}",
        yaxis_title="Coefficient", template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("quantile_coef", fig,
               caption=(f"Quantile-regression coefficient of {TGT} forward returns on "
                        f"{IND_YOY} across return quantiles with 95% CI. Significant tau "
                        f"values: {sig_tau or 'none at the tradeable tails'}. Any tilt is "
                        f"small and confined to isolated quantiles — freight growth does "
                        f"not flag elevated crash risk either."),
               alignment="Coef-by-tau with CI band; weak/absent tail-risk channel.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/quantile_regression.csv"],
               nber_required=False)


# ── 9. HMM regime probabilities ───────────────────────────────────────────
def chart_hmm():
    h = pd.read_parquet(CORE / "hmm_states.parquet")
    summ = pd.read_csv(CORE / "hmm_summary.csv")
    stress_pct = float(summ.loc[summ["state_label"] == "stress", "frequency_pct"].iloc[0])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h.index, y=h["prob_stress"], mode="lines",
        name="P(high-variance freight regime)",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.25)",
        line=dict(color=C_IND, width=1.2)))
    add_nber_shading(fig, x_min=h.index.min(), x_max=h.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Hidden Markov Model: 2-State Regime Probability for {IND_YOY}"
               f"<br><sup>High-variance state covers {stress_pct:.0f}% of months; "
               f"spikes around freight-cycle turning points</sup>"),
        xaxis_title="Date", yaxis_title="Probability of high-variance regime",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("hmm_regime_probs", fig,
               caption=(f"Probability that {IND_YOY} is in its high-variance regime (2-state "
                        f"HMM). The high-variance state covers {stress_pct:.0f}% of months and "
                        f"spikes at freight-cycle turning points (GFC, COVID, 2022–24 "
                        f"freight recession). The winner signal for this pair is the "
                        f"contraction flag, not the HMM probability — the HMM is supporting "
                        f"regime context. Shaded bands mark NBER recessions."),
               alignment=("HMM is backdrop context; winner is the contraction flag, not "
                          "hmm_stress. Labelled accordingly."),
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/hmm_states.parquet",
                        f"results/{PAIR}/core_models_{DATE_TAG}/hmm_summary.csv"])


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
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["strategy_equity"], mode="lines",
        name=f"Cass Freight procyclical Long/Cash (Sharpe {w['oos_sharpe']:.2f})",
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
        title=(f"Procyclical Overlay With a Drawdown Win: Cass Freight Rule vs Buy & Hold "
               f"{TGT}<br><sup>OOS {w['oos_period_start']} to {w['oos_period_end']} "
               f"({w['oos_n']} months ≈ 8.3yr): {w['oos_ann_return']*100:.1f}% vs "
               f"{w['bh_ann_return']*100:.1f}% annualized; bootstrap p={BOOT_P:.3f} "
               f"(NOT significant) — found-in-search candidate</sup>"),
        xaxis_title="Date", yaxis_title="Growth of 1.00",
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("equity_curves", fig,
               caption=(f"Cumulative growth of 1.00 for the saved strategy returns and "
                        f"buy-and-hold {TGT}. The OOS window is now {w['oos_n']} months "
                        f"(≈8.3yr, clearing the 5-year floor); the rule raises Sharpe "
                        f"({w['oos_sharpe']:.2f} vs {w['bh_sharpe']:.2f}) mostly by cutting "
                        f"drawdown, but the median valid combo (0.77) UNDERPERFORMS B&H, the "
                        f"bootstrap p ({BOOT_P:.3f}) is NOT significant at 5%, forward Granger "
                        f"causality is absent, and this is found-in-search. Shaded bands mark "
                        f"NBER recessions."),
               alignment="Strategy series from strategy_returns; metrics from winner_summary; fragility in title.",
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
        title=(f"Drawdown Protection Is the Defensible Virtue: "
               f"{w['oos_max_drawdown']*100:.1f}% vs {w['bh_max_drawdown']*100:.1f}% OOS"),
        xaxis_title="Date", yaxis_title="Drawdown (%)",
        template="plotly_white", height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("drawdown", fig,
               caption=(f"Drawdown path for the Cass Freight procyclical Long/Cash rule and "
                        f"buy-and-hold {TGT}. In OOS the strategy's max drawdown is "
                        f"{w['oos_max_drawdown']*100:.1f}% versus "
                        f"{w['bh_max_drawdown']*100:.1f}% for buy-and-hold — the reduction "
                        f"achieved by stepping to cash in deep freight contractions is the "
                        f"rule's most defensible feature; read the Sharpe edge as volatility "
                        f"avoidance."),
               alignment="Drawdown from the saved monthly return series; frames Sharpe as vol avoidance.",
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
    invalid = t[(~t["valid"]) & (t["signal"] != "BENCHMARK")]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=invalid["annual_turnover"], y=invalid["oos_sharpe"], mode="markers",
        marker=dict(size=3, color="rgba(153,153,153,0.45)"), name="Invalid combos"))
    fig.add_trace(go.Scatter(
        x=valid["annual_turnover"], y=valid["oos_sharpe"], mode="markers",
        marker=dict(size=5, color=(valid["max_drawdown"] * 100),
                    colorscale="RdYlGn", colorbar=dict(title="Max DD (%)"), opacity=0.6),
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
        marker=dict(size=12, color=C_POS, symbol="star", line=dict(width=1, color="#000000")),
        name="Top 5 by OOS Sharpe (incl. excluded contaminated combos)"))
    fig.update_layout(
        title=(f"Tournament: {len(t)-1:,} Strategy Combos ({len(valid):,} Valid) — "
               f"Winner OOS Sharpe {float(load_winner()['oos_sharpe']):.2f} vs Buy & Hold "
               f"{float(bench.iloc[0]['oos_sharpe']):.2f}"),
        xaxis_title="Annual turnover (trades per year)", yaxis_title="OOS Sharpe ratio",
        template="plotly_white", height=540, margin=dict(b=150),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0))
    save_chart("tournament_scatter", fig,
               caption=(f"All {len(t)-1:,} tournament combinations (OOS Sharpe vs annual "
                        f"turnover; color = max drawdown). {len(valid):,} pass validity; the "
                        f"Buy & Hold {TGT} diamond sits at Sharpe "
                        f"{float(bench.iloc[0]['oos_sharpe']):.2f}. The top raw scorers include "
                        f"seasonally-contaminated combos excluded from selection; the published "
                        f"winner is the best seasonally-CLEAN combo (ECON-T3 cascade)."),
               alignment="Standard tournament scatter; benchmark via signal=='BENCHMARK' (ECON-T4).",
               rules=["VIZ-IC1", "ECON-T4", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv"],
               nber_required=False)


def chart_tournament_dist():
    t, valid, bench = _tournament_frames()
    w = load_winner()
    med = float(valid["oos_sharpe"].median())
    wsharpe = float(w["oos_sharpe"])
    bh = float(bench.iloc[0]["oos_sharpe"])
    fig = go.Figure(go.Histogram(
        x=valid["oos_sharpe"], nbinsx=60, marker_color=C_TGT, opacity=0.75,
        name=f"Valid strategies (n = {len(valid):,})"))
    fig.add_vline(x=med, line=dict(color=C_NEUTRAL, dash="dot", width=1.5))
    fig.add_vline(x=bh, line=dict(color=C_BENCH, dash="dash", width=2))
    fig.add_vline(x=wsharpe, line=dict(color=C_IND, dash="dash", width=2))
    fig.add_annotation(x=wsharpe, y=1.0, yref="paper", showarrow=False, xanchor="right",
                       text=f"Winner = {wsharpe:.2f} (median {med:.2f})",
                       font=dict(size=12, color=C_IND), bgcolor=PAL["event_marker_label_bg"])
    bh_rel = "ABOVE" if bh >= med else "below"
    fig.add_annotation(x=bh, y=0.85, yref="paper", showarrow=False, xanchor="left",
                       text=f"Buy & Hold {TGT} = {bh:.2f} — {bh_rel} the median strategy",
                       font=dict(size=12, color=C_BENCH), bgcolor=PAL["event_marker_label_bg"])
    fig.update_layout(
        title=(f"Winner Is the Right Tail of a {len(valid):,}-Combo Search; the Median Rule "
               f"Underperforms Buy & Hold<br><sup>Median valid Sharpe {med:.2f} &lt; "
               f"Buy & Hold {bh:.2f} — the typical rule subtracts value</sup>"),
        xaxis_title="OOS Sharpe ratio", yaxis_title="Number of strategies",
        template="plotly_white", height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("tournament_sharpe_dist", fig,
               caption=(f"Distribution of OOS Sharpe across the {len(valid):,} valid strategy "
                        f"combos. The winner (Sharpe {wsharpe:.2f}) is the right tail; the "
                        f"median valid combo ({med:.2f}) sits BELOW buy & hold ({bh:.2f}) — "
                        f"i.e. the typical rule subtracts value, so the winner is a "
                        f"found-in-search draw (bootstrap p = {BOOT_P:.3f}, not significant at "
                        f"5%; no fresh final-exam holdout). Treat as a candidate, not a "
                        f"validated edge."),
               alignment=("VIZ-SCD1 position disclosure + B&H line; median&lt;B&H stated "
                          "explicitly; fragility flags in caption."),
               rules=["VIZ-SCD1", "ECON-T4", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               reconciliation={"valid_count": len(valid), "median_oos_sharpe": round(med, 4),
                               "winner_oos_sharpe": round(wsharpe, 4),
                               "bh_oos_sharpe": round(bh, 4)},
               nber_required=False)


# ── 14. Rolling correlation ───────────────────────────────────────────────
def chart_rolling_correlation():
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rc["date"], y=rc["rolling_corr"], mode="lines",
        name="24-month rolling correlation", line=dict(color=C_TGT, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_EVENT, line_width=1,
                  annotation_text="No correlation")
    add_nber_shading(fig, x_min=rc["date"].min(), x_max=rc["date"].max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Sign-Stable but Variable Correlation: 24-Month Rolling Correlation, "
               f"{IND_YOY} vs {TGT} Returns<br><sup>Sign agreement "
               f"{sb['rolling_corr_sign_stability']:.2f} — verdict: "
               f"{sb['rolling_corr_stability_verdict'].replace('_', '-')}</sup>"),
        xaxis_title="Date", yaxis_title="Rolling correlation (r)",
        template="plotly_white", height=420, yaxis=dict(range=[-1, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("rolling_correlation", fig,
               caption=(f"24-month rolling correlation between {IND_YOY} and {TGT} monthly "
                        f"returns. The sign agrees with its full-sample value "
                        f"{sb['rolling_corr_sign_stability']:.0%} of the time "
                        f"(verdict: {sb['rolling_corr_stability_verdict'].replace('_',' ')}). "
                        f"Shaded bands mark NBER recessions."),
               alignment="Stability verdict from structural_break JSON.",
               rules=["VIZ-CP1.2", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/rolling_correlation_{PAIR}.csv",
                        f"results/{PAIR}/structural_break_{PAIR}.json"])


# ── 15. Structural break ──────────────────────────────────────────────────
def chart_structural_break():
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    df = load_monthly()
    sig = df.loc[sb["sample_start"]:sb["sample_end"], YOY_COL].dropna()
    flagged = bool(sb["flagged"])
    verdict_txt = "A Structural Break IS Flagged" if flagged else "No Structural Break Detected"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig.index, y=sig.values, mode="lines",
        name=f"{IND_YOY} (%)", line=dict(color=C_IND, width=1.8)))
    fig.add_vline(x=pd.Timestamp(sb["break_date"]).timestamp() * 1000,
                  line=dict(color=C_EVENT, dash="dash", width=2))
    fig.add_annotation(x=sb["break_date"], y=0.95, yref="paper", showarrow=False,
                       xanchor="left",
                       text=(f"Candidate break {sb['break_date'][:7]}: sup-F "
                             f"{sb['f_stat']:.2f}, bootstrap p = {sb['p_value']:.2f} "
                             f"— {'significant' if flagged else 'NOT significant'}"),
                       font=dict(size=12, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=sig.index.min(), x_max=sig.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"{verdict_txt}: Quandt-Andrews sup-F Test on {IND_YOY} "
               f"(break {sb['break_date'][:7]}, p = {sb['p_value']:.2f})"),
        xaxis_title="Date", yaxis_title=f"{IND_YOY} (%)",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("structural_break", fig,
               caption=(f"{IND_YOY} over the test sample ({sb['sample_start'][:7]}–"
                        f"{sb['sample_end'][:7]}, n = {sb['n_obs']}) with the Quandt-Andrews "
                        f"candidate break date ({sb['break_date'][:7]}, at the COVID shock). "
                        f"sup-F {sb['f_stat']:.2f}, bootstrap p = {sb['p_value']:.2f} "
                        f"— {'a break is flagged' if flagged else 'no break flagged'}. "
                        f"On a longer 1993+ sample the COVID dislocation is now detectable. "
                        f"Shaded bands mark NBER recessions."),
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
    labels, values, colors, texts = [], [], [], []
    for _, r in rows.iterrows():
        lab = _EP_LABEL.get(r["episode"], r["episode"])
        if r["data_status"] == "insufficient_data" or pd.isna(r["ann_sharpe"]):
            labels.append(f"{lab}<br>(outside 2018+ OOS window)")
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
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=texts, textposition="outside",
                           name="Annualized Sharpe by episode"))
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Episode Durability Is Limited: Winner Strategy by Historical Episode "
               f"<br><sup>{n_eval} of 4 canonical episodes fall inside the 2018+ OOS "
               f"window — dot-com and GFC are in-sample (insufficient data for the "
               f"STRATEGY), though the indicator history charts now show them</sup>"),
        xaxis_title="Historical episode", yaxis_title="Annualized Sharpe ratio",
        template="plotly_white", height=430, margin=dict(b=110), showlegend=False)
    save_chart("subperiod_sharpe", fig,
               caption=(f"Winner-strategy annualized Sharpe within each canonical stress "
                        f"episode. Only {n_eval} of 4 (COVID) falls inside the 2018+ OOS "
                        f"window; dot-com, GFC and China 2015 predate the OOS split and are "
                        f"in-sample for the strategy (insufficient data). The full 1990+ "
                        f"indicator history now covers dot-com and GFC on the history-zoom "
                        f"charts, but the STRATEGY cannot be scored there. This limited "
                        f"evaluable coverage is why durability is 'conditionally_durable'."),
               alignment=("Three-state encoding; only COVID is inside the 2018+ OOS window; "
                          "dot-com/GFC in-sample for the strategy despite the longer history."),
               rules=["ECON-CP1", "VIZ-CP1.1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/subperiod_sharpe.csv"],
               nber_required=False)


# ── 17. Walk-forward rolling Sharpe ───────────────────────────────────────
def chart_walk_forward():
    d = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    w = load_winner()
    oos = d[(d.index >= w["oos_period_start"]) & (d.index <= w["oos_period_end"])]
    window, min_p, ann = 12, 8, 12
    r_s = oos["strategy_return"].astype(float)
    r_b = oos["bh_return"].astype(float)
    roll_s = (r_s.rolling(window, min_periods=min_p).mean() * ann) / \
             (r_s.rolling(window, min_periods=min_p).std() * np.sqrt(ann) + 1e-12)
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
               caption=(f"Rolling 12-month annualized Sharpe of the winner strategy vs "
                        f"buy-and-hold {TGT} over the {w['oos_n']}-month out-of-sample window; "
                        f"the dashed reference line marks the reported OOS Sharpe "
                        f"({reported:.2f}). The rolling path swings widely around it — the "
                        f"headline is an average over a variable ride, not a stable level."),
               alignment="Rolling-Sharpe walk-forward; reference line reconciles with winner_summary OOS Sharpe.",
               rules=["ECON-SR1", "VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


# ── 18. History zoom charts ───────────────────────────────────────────────
def _window_has_recession(start: str, end: str) -> bool:
    from _nber import RECESSIONS
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return any(pd.Timestamp(r0) <= e and pd.Timestamp(r1) >= s for r0, r1 in RECESSIONS)


def chart_history_zoom(slug: str):
    ep = EVENTS_REG["episodes"][slug]
    df = load_monthly()
    w = df.loc[ep["start_date"]:ep["end_date"]]
    sig = w[YOY_COL].dropna()
    spy = w["spy"].dropna()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[f"{IND_YOY} (%)", f"{TGT} price (USD)"])
    fig.add_trace(go.Scatter(x=sig.index, y=sig.values, name=f"{IND_YOY} (%)",
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
        title=(f"{IND_YOY} and {TGT} During the {ep['episode_name']}, "
               f"{ep['start_date'][:4]}–{ep['end_date'][:4]}"),
        template="plotly_white", height=560,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1))
    fig.update_xaxes(matches="x2", showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=True, title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text=f"{IND_YOY} (%)", row=1, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    save_chart(f"history_zoom_{slug}", fig,
               caption=(f"{IND_YOY} (top, NSA, with 0% line) and {TGT} price (bottom) through "
                        f"the {ep['episode_name']} window ({ep['start_date'][:7]} to "
                        f"{ep['end_date'][:7]}), with registry event markers. The 1990+ Data "
                        f"Master splice makes this episode a real chart (freight and equities "
                        f"move broadly together)."
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


# ── CP2 skip sidecars ─────────────────────────────────────────────────────
def write_cp2_skips():
    for c in ("rolling_sharpe_cp", "rolling_granger"):
        (OUT / f"chart_skip_{c}.json").write_text(json.dumps({
            "chart_name": c, "pair_id": PAIR, "skipped_by": "VIZ-CP1-G",
            "reason": ("ECON-CP2 artifacts intentionally absent for this pair: "
                       "regime_story=false in results/cass_freight_spy/signal_scope.json "
                       "(CP2 skipped). No upstream result file exists to chart."),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": GENERATED_BY,
        }, indent=2) + "\n")
        print(f"  wrote chart_skip_{c}.json")


def clear_stale_history_skips():
    """The 1990+ splice makes dot-com/GFC real charts; remove the old skip markers."""
    for slug in ("dotcom", "gfc"):
        f = OUT / f"chart_skip_history_zoom_{slug}.json"
        if f.exists():
            f.unlink()
            print(f"  removed stale chart_skip_history_zoom_{slug}.json")


# ── MAIN ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generating charts for {PAIR}...")
    chart_hero()
    chart_regime_stats()
    chart_correlation_heatmap()
    chart_correlations_lead_view()
    chart_lead_sharpe_distribution()
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
    chart_walk_forward()
    for slug in ("dotcom", "gfc", "covid", "inflation_2022"):
        chart_history_zoom(slug)
    write_cp2_skips()
    clear_stale_history_skips()
    print("\nDone.")
