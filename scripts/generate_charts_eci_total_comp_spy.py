#!/usr/bin/env python3
"""Chart (re)generation: Employment Cost Index (Total Compensation, ECIALLCIV) x SPY.

Regenerates the charts that depend on the winner, the tournament, the regime model or the
cross-period artifacts for the 20261016 run (causal regime port + in-sample selection):

  * The 20261008 winner (hmm_stress / T3_zscore_1.0 / LB12 / P1 counter / L4q, OOS Sharpe 1.41)
    traded a full-sample, forward-backward-smoothed HMM probability (look-ahead). The causal
    helper (scripts/_regime_causal.py) needs >= 100 in-sample rows for a traded regime signal;
    ECI has 72 in-sample quarters, so the HMM and Markov-switching signals are not in the
    20261016 tournament. hmm_regime_probs now shows a causal DIAGNOSTIC fit (not traded).
  * The winner is the IS-valid combo with the highest in-sample Sharpe; every number in a title
    or caption is read from the results artifacts at run time.

Charts REGENERATED (output/charts/eci_total_comp_spy/plotly/):
    equity_curves, drawdown, walk_forward, lead_sharpe_distribution,
    tournament_scatter, tournament_sharpe_dist, subperiod_sharpe,
    rolling_correlation, structural_break, transfer_entropy, hmm_regime_probs,
    correlation_heatmap (hmm_stress / markov_regime rows removed).

Charts LEFT UNTOUCHED (winner-independent; input series and core models unchanged):
    hero, regime_stats, correlations_lead_view,
    granger_f_by_lag, ccf_prewhitened, local_projections, quantile_coef,
    history_zoom_{gfc,covid,inflation_2022}, chart_skip_* .
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from _nber import add_nber_shading  # noqa: E402
from _quartile_chart import QUARTILE_COLORS  # noqa: E402

PAIR = "eci_total_comp_spy"
DATE_TAG = "20261016"
RES = REPO / "results" / PAIR
CORE = RES / f"core_models_{DATE_TAG}"
OUT = REPO / "output" / "charts" / PAIR / "plotly"
OUT.mkdir(parents=True, exist_ok=True)

IND_LONG = "Employment Cost Index (Total Compensation)"
IND_SHORT = "ECI wage growth"
IND_YOY = "ECI YoY wage growth"
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

GENERATED_BY = "Viz — scripts/generate_charts_eci_total_comp_spy.py (causal HMM port + IS selection, 20261016)"
SRC_DATA = "data/eci_total_comp_spy_quarterly_latest.parquet"
YOY_COL = "eci_total_comp_pct_yoy"

# ── Loaders ─────────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    return pd.read_parquet(REPO / "data" / f"{PAIR}_quarterly_latest.parquet")


def load_tournament() -> pd.DataFrame:
    return pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")


def load_winner() -> dict:
    return json.loads((RES / "winner_summary.json").read_text())


# ── Gates ─────────────────────────────────────────────────────────────────
def _all_text(fig: go.Figure):
    if fig.layout.title and fig.layout.title.text:
        yield fig.layout.title.text
    for a in fig.layout.annotations or ():
        if a.text:
            yield a.text
    for tr in fig.data:
        if getattr(tr, "name", None):
            yield tr.name


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


# ── Transfer entropy ──────────────────────────────────────────────────────
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
        title=("Transfer Entropy: No Information Flow in Either Direction Between "
               f"{IND_SHORT} and {TGT}<br><sup>Tercile binning, 500 permutations "
               f"(~97 quarterly obs, low power); forward p = {fwd_p:.2f}, reverse "
               f"p = {rev_p:.2f} — neither significant</sup>"),
        yaxis_title="Transfer entropy (nats)", xaxis_title="Direction",
        template="plotly_white", height=400, showlegend=False)
    save_chart("transfer_entropy", fig,
               caption=(f"Transfer entropy between {IND_YOY} and {TGT} returns (tercile "
                        f"bins, 500 permutations). Forward (wages → {TGT}) p = {fwd_p:.2f}; "
                        f"reverse ({TGT} → wages) p = {rev_p:.2f}. Neither clears 5% — no "
                        f"non-linear channel rescues a forward reading, consistent with the "
                        f"absent forward Granger result (the indicator is lagging). On ~97 "
                        f"quarterly observations transfer entropy has low power, so read it "
                        f"as a directional check only."),
               alignment="Two-bar TE comparison; p-values read from transfer_entropy.csv.",
               rules=["VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/transfer_entropy.csv"],
               nber_required=False)


# ── Correlation heatmap (rows rebuilt from this run's correlations.csv) ─────
def chart_correlation_heatmap():
    """Rebuild the heatmap cells from core_models_{DATE_TAG}/correlations.csv. The 20260706
    figure also carried hmm_stress / markov_regime rows built from full-sample smoothed regime
    probabilities (and an MS model with spy_ret in its likelihood); those signals are no longer
    produced, so their rows are dropped. Layout and styling are kept from the committed figure."""
    import plotly.io as pio
    path = OUT / "correlation_heatmap.json"
    fig = pio.from_json(path.read_text())
    corr = pd.read_csv(CORE / "correlations.csv")
    pear = corr[corr["metric"] == "pearson"].copy()
    pear[["signal", "fwd"]] = pear["pair_name"].str.split("__", expand=True)
    hz = {"spy_fwd_1q": "1Q fwd", "spy_fwd_2q": "2Q fwd", "spy_fwd_4q": "4Q fwd"}
    tab = pear.pivot(index="signal", columns="fwd", values="value")
    rows = [r for r in fig.data[0].y if r in tab.index]
    cols = list(fig.data[0].x)
    inv = {v: k for k, v in hz.items()}
    z = [[float(tab.loc[r, inv[c]]) for c in cols] for r in rows]
    fig.data[0].update(y=rows, z=z, text=[[f"{v:.2f}" for v in row] for row in z])
    src = f"results/{PAIR}/core_models_{DATE_TAG}/correlations.csv"
    anns = list(fig.layout.annotations or ())
    for a in anns:
        if a.text and a.text.startswith("Source:"):
            a.text = f"Source: {src}. Pearson r, concurrent-quarter alignment."
    fig.update_layout(annotations=anns)
    save_chart("correlation_heatmap", fig,
               caption=(f"Pearson correlations between {len(rows)} ECI signal transforms and {TGT} forward "
                        f"returns at 1Q/2Q/4Q horizons (concurrent-quarter alignment). Range "
                        f"{min(min(r) for r in z):+.2f} to {max(max(r) for r in z):+.2f}."),
               alignment="Cells read from this run's correlations.csv; regime-model rows removed (not produced causally).",
               rules=["VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               sources=[src], nber_required=False)


# ── HMM regime probabilities — causal DIAGNOSTIC (not traded) ───────────────
def chart_hmm():
    h = pd.read_parquet(CORE / "hmm_states.parquet")
    summ = pd.read_csv(CORE / "hmm_summary.csv")
    reg = json.loads((CORE / "regime_models.json").read_text())
    diag = reg["models"]["hmm_diagnostic"]
    hi = summ.loc[summ["state_label"] == "high_wage_inflation"].iloc[0]
    hi_pct = float(hi["frequency_pct"])
    oos_start = reg["oos_start"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h.index, y=h["prob_stress"], mode="lines",
        name="P(high-wage-inflation state), forward-filtered",
        fill="tozeroy", fillcolor="rgba(213,94,0,0.25)",
        line=dict(color=C_IND, width=1.2)))
    fig.add_vline(x=pd.Timestamp(oos_start).timestamp() * 1000, line=dict(color=C_EVENT, dash="dot", width=1.3))
    fig.add_annotation(x=oos_start, y=0.96, yref="paper", showarrow=False, xanchor="left",
                       text="OOS begins (model frozen)", font=dict(size=11, color=C_EVENT),
                       bgcolor=PAL["event_marker_label_bg"])
    add_nber_shading(fig, x_min=h.index.min(), x_max=h.index.max())
    nber_swatch(fig)
    fig.update_layout(
        title=(f"Hidden Markov Model (diagnostic, not traded): High-Wage-Inflation State Probability"
               f"<br><sup>2-state HMM on {IND_YOY}, fit on {diag['n_fit']} in-sample quarters "
               f"({diag['fit_start'][:7]}–{diag['fit_end'][:7]}), read with a forward filter; "
               f"high state {hi_pct:.0f}% of quarters</sup>"),
        xaxis_title="Date", yaxis_title="Probability of high-wage-inflation state",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("hmm_regime_probs", fig,
               caption=(f"Probability that {IND_SHORT} is in its high-wage-inflation state from a 2-state "
                        f"HMM. The model is fit on the {diag['n_fit']} in-sample quarters only and each "
                        f"quarter's value uses data up to that quarter (forward filter). This series is "
                        f"NOT in the tournament: a traded regime signal needs at least 100 in-sample "
                        f"observations and ECI has {diag['n_fit']}. The high state covers {hi_pct:.0f}% of "
                        f"quarters. Shaded bands mark NBER recessions."),
               alignment="Causal diagnostic HMM (IS-only fit, forward filter); stated as not traded.",
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/core_models_{DATE_TAG}/hmm_states.parquet",
                        f"results/{PAIR}/core_models_{DATE_TAG}/hmm_summary.csv",
                        f"results/{PAIR}/core_models_{DATE_TAG}/regime_models.json"])


# ── Lead-Sharpe distribution (VIZ-LEAD1, GH #13) ───────────────────────────
def chart_lead_sharpe_distribution():
    lt = pd.read_csv(RES / f"lead_tournament_{DATE_TAG}.csv").sort_values("lead_quarters")
    wc = pd.read_csv(RES / f"lead_winner_curve_{DATE_TAG}.csv").sort_values("lead_quarters")
    w = load_winner()
    win_lead = int(w["lead_value"])
    bh = float(w["bh_sharpe"])
    leads = lt["lead_quarters"].tolist()
    grid_lo, grid_hi = int(min(leads)), int(max(leads))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=lt["lead_quarters"], y=lt["best_oos_sharpe"],
        marker_color=C_TGT, opacity=0.55,
        name="Best OOS Sharpe of any IS-valid combo per lead (OOS-picked, context)"))
    fig.add_trace(go.Scatter(
        x=wc["lead_quarters"], y=wc["is_sharpe"], mode="lines+markers",
        line=dict(color=C_NEUTRAL, width=1.8, dash="dot"), marker=dict(size=6, color=C_NEUTRAL),
        name="Selected rule: in-sample Sharpe by lead"))
    fig.add_trace(go.Scatter(
        x=wc["lead_quarters"], y=wc["oos_sharpe"], mode="lines+markers",
        line=dict(color=C_IND, width=2.2), marker=dict(size=7, color=C_IND),
        name="Selected rule, winner's own curve: OOS Sharpe by lead"))
    fig.add_trace(go.Scatter(
        x=[win_lead], y=[float(w["oos_sharpe"])], mode="markers",
        marker=dict(size=16, color=C_POS, symbol="star", line=dict(width=1, color="#000000")),
        name=f"Selected L{win_lead}q (OOS Sharpe {w['oos_sharpe']:.2f})"))
    fig.add_hline(y=bh, line=dict(color=C_BENCH, dash="dash", width=1.8),
                  annotation_text=f"Buy & Hold {TGT} OOS = {bh:.2f}",
                  annotation_position="bottom right")
    fig.update_layout(
        title=(f"Lead Sweep: Winner Rule by Quarterly Lead (L{grid_lo}–L{grid_hi})<br><sup>Selected "
               f"at L{win_lead}q by in-sample Sharpe; OOS Sharpe {w['oos_sharpe']:.2f} vs buy & hold "
               f"{bh:.2f}</sup>"),
        xaxis_title="Signal lead (quarters)", yaxis_title="Sharpe ratio",
        template="plotly_white", height=480, margin=dict(b=170),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0))
    fig.update_xaxes(dtick=1)
    oos_txt = ", ".join(f"L{int(a)} {b:.2f}" for a, b in zip(wc["lead_quarters"], wc["oos_sharpe"]))
    is_txt = ", ".join(f"L{int(a)} {b:.2f}" for a, b in zip(wc["lead_quarters"], wc["is_sharpe"]))
    save_chart("lead_sharpe_distribution", fig,
               caption=(f"The selected rule ({w['signal_display_name']}, {w['threshold_code']}, "
                        f"{w['strategy_display_name']}) evaluated at every lead of the floored quarterly grid "
                        f"L{grid_lo}–L{grid_hi}. In-sample Sharpe: {is_txt}. OOS Sharpe: {oos_txt}. Bars are "
                        f"the best OOS Sharpe of any IS-valid combo at each lead; they are picked after "
                        f"seeing OOS results and are shown as context only. Buy & hold OOS Sharpe {bh:.2f}."),
               alignment="Winner rule IS and OOS Sharpe per lead; OOS envelope labelled as OOS-picked context.",
               rules=["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               sources=[f"results/{PAIR}/lead_tournament_{DATE_TAG}.csv",
                        f"results/{PAIR}/lead_winner_curve_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               reconciliation={"winner_lead": win_lead,
                               "winner_oos_sharpe": round(float(w["oos_sharpe"]), 4),
                               "bh_sharpe": round(bh, 4)},
               extra_meta={"method_name": "lead_sharpe_distribution",
                           "expected_chart_type": "bar", "gh_issue": "13"},
               nber_required=False)


# ── Equity curves + drawdown ───────────────────────────────────────────────
def _strategy_returns() -> pd.DataFrame:
    d = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"])
    d["strategy_equity"] = (1 + d["strategy_return"]).cumprod()
    d["bh_equity"] = (1 + d["bh_return"]).cumprod()
    d["strategy_drawdown"] = d["strategy_equity"] / d["strategy_equity"].cummax() - 1
    d["bh_drawdown"] = d["bh_equity"] / d["bh_equity"].cummax() - 1
    return d


def _rule_label(w) -> str:
    return f"{w['signal_display_name']} {w['strategy_display_name']} rule"


def chart_equity_curves():
    d = _strategy_returns()
    w = load_winner()
    oos = d[d["date"] >= w["oos_period_start"]]
    n_in = int((oos["position"] > 0).sum())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["strategy_equity"], mode="lines",
        name=f"{_rule_label(w)} (OOS Sharpe {w['oos_sharpe']:.2f})",
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
        title=(f"ECI Rule vs Buy & Hold {TGT}<br><sup>OOS {w['oos_period_start']} to "
               f"{w['oos_period_end']} ({w['oos_n']} quarters): {w['oos_ann_return']*100:.1f}% vs "
               f"{w['bh_ann_return']*100:.1f}% annualized; Sharpe {w['oos_sharpe']:.2f} vs "
               f"{w['bh_sharpe']:.2f}</sup>"),
        xaxis_title="Date", yaxis_title="Growth of 1.00",
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("equity_curves", fig,
               caption=(f"Cumulative growth of 1.00 for the selected rule and buy-and-hold {TGT}. Over the "
                        f"{w['oos_n']}-quarter OOS window the rule held {TGT} in {n_in} quarters and cash in "
                        f"the rest: {w['oos_ann_return']*100:.1f}% annualized vs {w['bh_ann_return']*100:.1f}% "
                        f"for buy-and-hold, Sharpe {w['oos_sharpe']:.2f} vs {w['bh_sharpe']:.2f} "
                        f"(HAC t {w['oos_hac_t']:.2f}). Shaded bands mark NBER recessions."),
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
                        f"{w['oos_max_drawdown']*100:.1f}% for the rule and {w['bh_max_drawdown']*100:.1f}% for "
                        f"buy-and-hold. The rule is in cash for most OOS quarters, so it also misses most "
                        f"of the gains (annualized {w['oos_ann_return']*100:.1f}% vs "
                        f"{w['bh_ann_return']*100:.1f}%). Shaded bands mark NBER recessions."),
               alignment="Drawdown from the saved quarterly return series.",
               rules=["VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


# ── Tournament scatter + distribution ──────────────────────────────────────
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
    for i, strat in enumerate(sorted(valid["strategy"].unique())):
        sub = valid[valid["strategy"] == strat]
        fig.add_trace(go.Scatter(
            x=sub["is_sharpe"], y=sub["oos_sharpe"], mode="markers",
            marker=dict(size=5, color=C_EXT[i % len(C_EXT)], opacity=0.55), name=strat,
            text=[f"{r['signal']}/{r['threshold']}/{r['lookback']}/L{r['lead_quarters']}q" for _, r in sub.iterrows()],
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
                        f"Spearman rank correlation between IS and OOS Sharpe across the grid: {rho:.2f}. "
                        f"Dashed lines: buy-and-hold {TGT}."),
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
    fig.add_annotation(x=wsharpe, y=1.0, yref="paper", showarrow=False, xanchor="right",
                       text=f"Selected rule = {wsharpe:.2f} (median {med:.2f})",
                       font=dict(size=12, color=C_IND), bgcolor=PAL["event_marker_label_bg"])
    fig.add_annotation(x=bh, y=0.85, yref="paper", showarrow=False, xanchor="left",
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
                        f"{wsharpe:.2f}, the {pct:.0f}th percentile of the distribution. Median {med:.2f}; "
                        f"buy & hold {bh:.2f}; {n_beat:,} of {len(valid):,} combos have a higher OOS Sharpe "
                        f"than buy & hold."),
               alignment="VIZ-SCD1 position disclosure + B&H line; percentile computed from the CSV.",
               rules=["VIZ-SCD1", "ECON-T4", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/tournament_results_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"],
               reconciliation={"valid_count": len(valid), "median_oos_sharpe": round(med, 4),
                               "winner_oos_sharpe": round(wsharpe, 4),
                               "bh_oos_sharpe": round(bh, 4)},
               nber_required=False)


# ── Rolling correlation ────────────────────────────────────────────────────
def chart_rolling_correlation():
    rc = pd.read_csv(RES / f"rolling_correlation_{PAIR}.csv", parse_dates=["date"])
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    w = load_winner()
    win = int(rc["n_obs"].iloc[0])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rc["date"], y=rc["rolling_corr"], mode="lines",
        name=f"{win}-quarter rolling correlation", line=dict(color=C_TGT, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color=C_EVENT, line_width=1,
                  annotation_text="No correlation")
    add_nber_shading(fig, x_min=rc["date"].min(), x_max=rc["date"].max())
    nber_swatch(fig)
    verdict = sb["rolling_corr_stability_verdict"]
    fig.update_layout(
        title=(f"{win}-Quarter Rolling Correlation: Selected Signal (lagged {w['lead_value']}q) vs "
               f"Next-Quarter {TGT} Return<br><sup>Share of windows with the full-sample sign "
               f"{sb['rolling_corr_sign_stability']:.2f} ({verdict.replace('_', ' ')})</sup>"),
        xaxis_title="Date", yaxis_title="Rolling correlation (r)",
        template="plotly_white", height=420, yaxis=dict(range=[-1, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("rolling_correlation", fig,
               caption=(f"{win}-quarter rolling correlation between the selected signal "
                        f"({w['signal_display_name']}, lagged {w['lead_value']} quarter(s)) and the next-quarter "
                        f"{TGT} return. The sign matches the full-sample sign in "
                        f"{sb['rolling_corr_sign_stability']:.0%} of windows ({verdict.replace('_',' ')}). "
                        f"Shaded bands mark NBER recessions."),
               alignment="Series and stability verdict read from the rolling-correlation CSV and structural_break JSON.",
               rules=["VIZ-CP1.2", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/rolling_correlation_{PAIR}.csv",
                        f"results/{PAIR}/structural_break_{PAIR}.json"])


# ── Structural break ───────────────────────────────────────────────────────
def chart_structural_break():
    sb = json.loads((RES / f"structural_break_{PAIR}.json").read_text())
    w = load_winner()
    sig_col = w["signal_column"]
    df = load_data()
    sig = df.loc[sb["sample_start"]:sb["sample_end"], sig_col].dropna()
    flagged = bool(sb["flagged"])
    verdict_txt = "Structural Break Flagged" if flagged else "No Structural Break Flagged"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig.index, y=sig.values, mode="lines",
        name=w["signal_display_name"], line=dict(color=C_IND, width=1.8)))
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
        xaxis_title="Date", yaxis_title=w["signal_display_name"],
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("structural_break", fig,
               caption=(f"Quandt-Andrews unknown-breakpoint test on the regression of the quarterly {TGT} return "
                        f"on the selected signal lagged {w['lead_value']} quarter(s) "
                        f"({sb['sample_start'][:7]}–{sb['sample_end'][:7]}, n = {sb['n_obs']} quarters). The line "
                        f"plots the signal (unlagged); the dashed marker is the candidate break "
                        f"{sb['break_date'][:7]}: sup-F {sb['f_stat']:.2f}, residual-bootstrap p = "
                        f"{sb['p_value']:.2f} — {'flagged' if flagged else 'not flagged'} at 10%. Shaded "
                        f"bands mark NBER recessions."),
               alignment="Annotation-driven; flagged state and values read from JSON.",
               rules=["VIZ-CP1.3", "VIZ-NBER1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/structural_break_{PAIR}.json", SRC_DATA],
               extra_meta={"break_date": sb["break_date"],
                           "annotation_strategy_id": "manual_override"})


# ── Sub-period Sharpe ──────────────────────────────────────────────────────
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
            labels.append(f"{lab}<br>(outside {oos_y}+ OOS window)")
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
        title=(f"Selected Rule by Historical Episode<br><sup>{n_eval} of {len(rows)} canonical "
               f"episodes fall inside the {oos_y}+ OOS window; the others predate the OOS split</sup>"),
        xaxis_title="Historical episode", yaxis_title="Annualized Sharpe ratio",
        template="plotly_white", height=430, margin=dict(b=110), showlegend=False)
    save_chart("subperiod_sharpe", fig,
               caption=(f"Selected-rule annualized Sharpe within each canonical stress episode. {n_eval} of "
                        f"{len(rows)} episodes fall inside the {oos_y}+ OOS window; the others predate the "
                        f"OOS split and are not scored here. Durability label: "
                        f"'{rows['durability_verdict'].dropna().iloc[-1] if rows['durability_verdict'].notna().any() else 'n/a'}'."),
               alignment="Three-state encoding; counts and verdict read from subperiod_sharpe.csv.",
               rules=["ECON-CP1", "VIZ-CP1.1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/subperiod_sharpe.csv"],
               nber_required=False)


# ── Walk-forward rolling Sharpe ────────────────────────────────────────────
def chart_walk_forward():
    d = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    w = load_winner()
    oos = d[(d.index >= w["oos_period_start"]) & (d.index <= w["oos_period_end"])]
    window, min_p, ann = 8, 6, 4  # QUARTERLY: 8-quarter (2yr) window, sqrt(4) annualization
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
                             name=f"Strategy rolling {window}-quarter Sharpe",
                             line=dict(color=C_IND, width=2)))
    add_nber_shading(fig, x_min=oos.index.min(), x_max=oos.index.max())
    nber_swatch(fig)
    fig.add_hline(y=reported, line=dict(color=C_POS, dash="dash", width=1.2),
                  annotation_text=f"Reported OOS Sharpe = {reported:.2f}",
                  annotation_position="top left")
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Walk-Forward: Rolling 8-Quarter Sharpe vs Reported OOS Sharpe "
               f"{reported:.2f} (OOS {y0}–{y1})"),
        xaxis_title="Date", yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    save_chart("walk_forward", fig,
               caption=(f"Rolling 8-quarter (2-year) annualized Sharpe of the selected rule vs buy-and-hold "
                        f"{TGT} over the {w['oos_n']}-quarter out-of-sample window; the dashed reference line "
                        f"marks the reported OOS Sharpe ({reported:.2f}). Windows in which the rule was in "
                        f"cash throughout have no defined Sharpe and are left blank."),
               alignment="Rolling-Sharpe walk-forward; quarterly window; reference line reconciles with winner_summary OOS Sharpe.",
               rules=["ECON-SR1", "VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               sources=[f"results/{PAIR}/strategy_returns_{DATE_TAG}.csv",
                        f"results/{PAIR}/winner_summary.json"])


def main():
    print(f"Regenerating winner-dependent charts for {PAIR} (DATE_TAG {DATE_TAG})")
    chart_correlation_heatmap()
    chart_transfer_entropy()
    chart_hmm()
    chart_lead_sharpe_distribution()
    chart_equity_curves()
    chart_drawdown()
    chart_tournament_scatter()
    chart_tournament_dist()
    chart_rolling_correlation()
    chart_structural_break()
    chart_subperiod_sharpe()
    chart_walk_forward()
    print("Done. (hero/regime_stats/correlations_lead_view/"
          "granger/ccf/local_projections/quantile/history_zoom left untouched — "
          "winner-independent, data unchanged.)")


if __name__ == "__main__":
    main()
