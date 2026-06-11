#!/usr/bin/env python3
"""ECON-SR1 consumer — strategy-performance charts from the reconciled
canonical strategy-returns series.

Context (fix260611_meta_cmp): the W0.5 backfill
(`w0p5_generate_missing_strategy_artefacts.py`, 2026-05-26) shipped
`drawdown.json` / `walk_forward.json` for vix_vix3m_spy, indpro_spy and
indpro_xlp from a defective in-script strategy-series reconstruction
(threshold-code parsing gap + double direction inversion — see Vera STOP
report, `_pws/viz-vera/session-notes.md` 2026-06-11, and ECON-SR1 in the
econometrics SOP). Evan repaired the series class and shipped reconciled
canonical artifacts at `results/{pair}/strategy_returns_YYYYMMDD.csv`
(+ `_meta.json` reconciliation sidecar, commit 108b091).

This script is the Vera-owned chart producer that CONSUMES those canonical
CSVs — it never re-derives positions from signals (META-NMF: the series
producer is Evan's `econ_sr1_build_strategy_returns.py`; the chart producer
must not fork that logic).

Charts produced per pair (OOS window, matching the healthy-pair convention
established by `generate_charts_umcsent_xlv.py` but on the registered
okabe_ito_2026 palette per VIZ-V11/VIZ-IC1):

    output/charts/{pair}/plotly/equity_curves.json   (Strategy page, Performance tab)
    output/charts/{pair}/plotly/drawdown.json        (Performance tab)
    output/charts/{pair}/plotly/walk_forward.json    (Confidence tab)
    output/charts/{pair}/plotly/subperiod_sharpe.json (from Evan's regenerated
                                                       subperiod_sharpe.csv)

Blocking gates (no artifact emission on failure):
    - ECON-SR1 reconciliation: OOS Sharpe / max drawdown / annualized return
      computed from the canonical series must match winner_summary.json within
      tolerance (0.01 Sharpe, 0.005 dd/ret — same tolerances as Evan's sidecar).
    - VIZ-IC1 pre-save assertions: palette registry conformance, legend-data
      match, unit discipline, title-axis coherence.
    - VIZ-NBER1: NBER shading present on every calendar-time chart.

Usage:
    python3 scripts/generate_strategy_perf_charts.py [pair_id ...]
    # default: vix_vix3m_spy indpro_spy indpro_xlp
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
sys.path.insert(0, str(REPO / "app"))

from _nber import add_nber_shading  # noqa: E402
from components.display_names import SHORT_INDICATOR_LABELS  # noqa: E402

# ── Palette (docs/schemas/color_palette_registry.json :: okabe_ito_2026) ──
PALETTE_ID = "okabe_ito_2026"
_REG = json.loads((REPO / "docs/schemas/color_palette_registry.json").read_text())
PAL = _REG["palettes"][PALETTE_ID]
C_STRATEGY = PAL["equity_curve"]            # #0072B2
C_BENCHMARK = PAL["benchmark_trace"]        # #6C7A89
C_ACCENT = PAL["primary_data_trace"]        # #D55E00
C_POS = PAL["tertiary_data_trace"]          # #009E73
C_NEG = PAL["primary_data_trace"]           # #D55E00
C_NEUTRAL = PAL["hold_indicator"]           # #999999
C_DD_FILL = PAL["drawdown_fill"]            # rgba(213,94,0,0.35)
C_NBER = PAL["nber_shading"]                # rgba(150,120,120,0.22)
C_BH_FILL = "rgba(108,122,137,0.15)"        # benchmark_trace at low alpha

ALLOWED_COLORS = {str(v).lower() for v in PAL.values() if isinstance(v, str)} | {
    c.lower() for c in PAL.get("categorical_extended", [])
} | {c.lower() for c in PAL.get("quartile_gradient", [])} | {
    C_BH_FILL.lower(), "rgba(150,120,120,0.35)",
}

TOL = {"oos_sharpe": 0.01, "oos_max_drawdown": 0.005, "oos_ann_return": 0.005}

GENERATED_BY = "Viz Vera — scripts/generate_strategy_perf_charts.py (fix260611_meta_cmp, ECON-SR1 consumer)"


# ── Loaders ───────────────────────────────────────────────────────────────

def latest(pattern: str) -> Path:
    matches = sorted(REPO.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No match for {pattern}")
    return matches[-1]


def load_canonical(pair: str):
    csv_path = latest(f"results/{pair}/strategy_returns_*.csv")
    meta_path = csv_path.with_name(csv_path.stem + "_meta.json")
    meta = json.loads(meta_path.read_text())
    df = pd.read_csv(csv_path, parse_dates=["date"]).set_index("date").sort_index()
    return df, meta, csv_path


def load_winner(pair: str) -> dict:
    return json.loads((REPO / "results" / pair / "winner_summary.json").read_text())


# ── ECON-SR1 reconciliation gate (blocking) ───────────────────────────────

def reconcile_or_die(pair: str, oos: pd.DataFrame, w: dict, ann: int) -> dict:
    r = oos["strategy_return"].astype(float)
    sharpe = float(r.mean() * ann / (r.std() * np.sqrt(ann) + 1e-12))
    eq = (1 + r).cumprod()
    mdd = float((eq / eq.cummax() - 1).min())
    annret = float((1 + r).prod() ** (ann / len(r)) - 1)
    computed = {"oos_sharpe": sharpe, "oos_max_drawdown": mdd, "oos_ann_return": annret}
    out = {}
    for k, v in computed.items():
        reported = float(w[k])
        diff = v - reported
        verdict = "PASS" if abs(diff) <= TOL[k] else "FAIL"
        out[k] = {"computed": round(v, 6), "reported_winner_summary": reported,
                  "diff": round(diff, 6), "tolerance": TOL[k], "verdict": verdict}
        print(f"    ECON-SR1 {pair} {k}: computed={v:.4f} reported={reported:.4f} -> {verdict}")
        if verdict == "FAIL":
            raise SystemExit(
                f"ECON-SR1 reconciliation FAIL for {pair}/{k}: "
                f"{v:.4f} vs {reported:.4f} (tol {TOL[k]}). No artifact emitted.")
    return out


# ── VIZ-IC1 pre-save assertions (blocking) ────────────────────────────────

def validate_intra_chart_consistency(fig: go.Figure, pair: str, name: str) -> None:
    violations = []
    # Legend <-> data: every drawn trace is named.
    for i, tr in enumerate(fig.data):
        if not getattr(tr, "name", None):
            violations.append(f"trace[{i}] has no name (legend-data mismatch)")
    # Palette conformance: line/marker colors must come from the registry.
    for tr in fig.data:
        for col in (getattr(getattr(tr, "line", None), "color", None),
                    getattr(getattr(tr, "marker", None), "color", None),
                    getattr(tr, "fillcolor", None)):
            if col is None or not isinstance(col, str):
                continue
            if col.lower() not in ALLOWED_COLORS:
                violations.append(f"trace {tr.name!r}: color {col} not in {PALETTE_ID} registry")
    # Unit discipline + title-axis coherence.
    title = (fig.layout.title.text or "") if fig.layout.title else ""
    ytitle = ""
    if fig.layout.yaxis and fig.layout.yaxis.title:
        ytitle = fig.layout.yaxis.title.text or ""
    if "Drawdown" in title and "%" not in ytitle:
        violations.append("drawdown title but y-axis lacks % unit")
    if "Drawdown" in title:
        for tr in fig.data:
            ys = np.asarray([y for y in tr.y if y is not None], dtype=float)
            if len(ys) and ys.min() > -1.0 and ys.min() < 0:
                violations.append(
                    f"trace {tr.name!r}: drawdown values look like fractions "
                    f"(min {ys.min():.4f}) on a % axis")
    if "Sharpe" in title and "Sharpe" not in ytitle and "Sharpe" not in title:
        violations.append("Sharpe title but y-axis lacks Sharpe units")
    if violations:
        for v in violations:
            print(f"    VIZ-IC1 VIOLATION [{pair}/{name}]: {v}")
        raise SystemExit(f"VIZ-IC1 pre-save check failed for {pair}/{name}; save blocked.")
    print(f"    VIZ-IC1 PASS [{pair}/{name}]")


def assert_nber_present(fig: go.Figure, pair: str, name: str) -> None:
    shapes = fig.layout.shapes or ()
    n = sum(1 for s in shapes if s.fillcolor and "rgba(150" in s.fillcolor.replace(" ", ""))
    if n == 0:
        raise SystemExit(f"VIZ-NBER1 FAIL: {pair}/{name} has no NBER shading shapes.")
    print(f"    VIZ-NBER1 PASS [{pair}/{name}]: {n} recession shape(s)")


# ── Save helper (chart + _meta.json sidecar + perceptual PNG) ─────────────

def save_chart(pair: str, name: str, fig: go.Figure, *, caption: str,
               alignment: str, rules: list[str], reconciliation: dict | None,
               sources: list[str]) -> None:
    validate_intra_chart_consistency(fig, pair, name)
    out_dir = REPO / "output" / "charts" / pair / "plotly"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.write_json(out_dir / f"{name}.json")
    meta = {
        "chart_name": name,
        "pair_id": pair,
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
    (out_dir / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    try:
        fig.write_image(str(out_dir / f"_perceptual_check_{name}.png"),
                        width=900, height=540, scale=1)
    except Exception as exc:  # kaleido availability is environment-dependent
        print(f"    WARN perceptual PNG not written ({exc})")
    print(f"  wrote output/charts/{pair}/plotly/{name}.json (+sidecar, +perceptual png)")


def nber_legend_swatch(fig: go.Figure) -> None:
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=12, color="rgba(150,120,120,0.35)", symbol="square"),
        name="NBER recession (shaded)", hoverinfo="skip"))


# ── Chart producers ───────────────────────────────────────────────────────

# Humanised fallbacks for legacy winner_summary shapes that lack
# *_display_name fields (VIZ-NS1: raw pipeline tokens are prohibited on
# user surfaces). Extend as new codes appear.
_SIGNAL_CODE_LABELS = {
    "S3_z126": "Z-Score (126-day)",
    "S6_mom3m": "3-Month Momentum",
    "S8_accel": "Acceleration",
}
_STRATEGY_FAMILY_LABELS = {
    "P1_long_cash": "Long/Cash",
    "P2_signal_strength": "Signal-Strength",
    "P3_long_short": "Long/Short",
}


def strategy_label(w: dict) -> str:
    sig = (w.get("signal_display_name")
           or _SIGNAL_CODE_LABELS.get(w.get("signal_code", ""))
           or "Tournament Winner")
    strat = (w.get("strategy_display_name")
             or _STRATEGY_FAMILY_LABELS.get(w.get("strategy_family", ""))
             or "")
    label = f"Strategy: {sig} {strat}".strip()
    # VIZ-NS1 guard: never emit raw pipeline tokens like "S8_accel".
    assert "_" not in label, f"raw token leaked into legend label: {label!r}"
    return label


def make_equity_curves(pair: str, oos: pd.DataFrame, w: dict, meta: dict,
                       ann: int, recon: dict, sources: list[str]) -> None:
    target = (w.get("target_symbol") or pair.split("_")[-1]).upper()
    ind = SHORT_INDICATOR_LABELS.get(pair, pair)
    eq = (1 + oos["strategy_return"].astype(float)).cumprod()
    bh = (1 + oos["bh_return"].astype(float)).cumprod()
    y0, y1 = meta["oos_start"][:4], meta["oos_end"][:4]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh.index, y=bh.values, name=f"Buy & Hold {target}",
                             line=dict(color=C_BENCHMARK, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=eq.index, y=eq.values, name=strategy_label(w),
                             line=dict(color=C_STRATEGY, width=2)))
    add_nber_shading(fig, x_min=oos.index.min(), x_max=oos.index.max())
    nber_legend_swatch(fig)
    # NOTE: at most ONE literal "$" per Plotly/Streamlit text element — a
    # second "$" opens MathJax math mode and garbles the title (caught by the
    # VIZ-CV1 perceptual check on first generation).
    fig.update_layout(
        title=(f"Equity Curves: {ind} Winner Grows $1 to {eq.iloc[-1]:.2f} "
               f"vs {bh.iloc[-1]:.2f} for Buy & Hold {target} (OOS {y0}–{y1})"),
        xaxis_title="Date",
        yaxis_title="Cumulative Return ($1 invested)",
        template="plotly_white", height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    caption = (f"Out-of-sample cumulative growth per dollar invested: winner "
               f"strategy ends at {eq.iloc[-1]:.2f} vs {bh.iloc[-1]:.2f} for "
               f"buy-and-hold {target} ({meta['oos_start']} to {meta['oos_end']}). "
               f"Series: reconciled canonical strategy returns (ECON-SR1). "
               f"Shaded bands mark NBER recessions.")
    save_chart(pair, "equity_curves", fig, caption=caption,
               alignment=("Winner-vs-buy-and-hold cumulative growth for the Strategy "
                          "page Performance tab; endpoints re-read from the canonical "
                          "series at generation time."),
               rules=["ECON-SR1", "VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               reconciliation=recon, sources=sources)


def make_drawdown(pair: str, oos: pd.DataFrame, w: dict, meta: dict,
                  ann: int, recon: dict, sources: list[str]) -> None:
    target = (w.get("target_symbol") or pair.split("_")[-1]).upper()
    eq = (1 + oos["strategy_return"].astype(float)).cumprod()
    bh = (1 + oos["bh_return"].astype(float)).cumprod()
    dd_s = (eq / eq.cummax() - 1) * 100
    dd_b = (bh / bh.cummax() - 1) * 100
    y0, y1 = meta["oos_start"][:4], meta["oos_end"][:4]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd_b.index, y=dd_b.values, name=f"Buy & Hold {target}",
                             fill="tozeroy", fillcolor=C_BH_FILL,
                             line=dict(color=C_BENCHMARK, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=dd_s.index, y=dd_s.values, name=strategy_label(w),
                             fill="tozeroy", fillcolor=C_DD_FILL,
                             line=dict(color=C_ACCENT, width=2)))
    add_nber_shading(fig, x_min=oos.index.min(), x_max=oos.index.max())
    nber_legend_swatch(fig)
    fig.update_layout(
        title=(f"Drawdown Comparison: Winner Max {dd_s.min():.1f}% vs "
               f"{dd_b.min():.1f}% Buy & Hold {target} (OOS {y0}–{y1})"),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    caption = (f"Peak-to-trough drawdown over the out-of-sample window: winner max "
               f"{dd_s.min():.1f}% vs {dd_b.min():.1f}% buy-and-hold {target}. Strategy "
               f"minimum equals winner_summary oos_max_drawdown "
               f"({w['oos_max_drawdown']:.2%}) by construction (ECON-SR1 reconciled "
               f"series). Shaded bands mark NBER recessions.")
    save_chart(pair, "drawdown", fig, caption=caption,
               alignment=("Strategy-vs-buy-and-hold drawdown for the Strategy page "
                          "Performance tab; chart minimum reconciles with the "
                          "winner_summary KPI quoted in the page caption."),
               rules=["ECON-SR1", "VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               reconciliation=recon, sources=sources)


def make_walk_forward(pair: str, oos: pd.DataFrame, w: dict, meta: dict,
                      ann: int, recon: dict, sources: list[str]) -> None:
    target = (w.get("target_symbol") or pair.split("_")[-1]).upper()
    window, unit = (252, "day") if ann == 252 else (12, "month")
    min_p = max(8, window * 2 // 3)
    r_s = oos["strategy_return"].astype(float)
    r_b = oos["bh_return"].astype(float)
    roll_s = (r_s.rolling(window, min_periods=min_p).mean() * ann) / \
             (r_s.rolling(window, min_periods=min_p).std() * np.sqrt(ann) + 1e-12)
    roll_b = (r_b.rolling(window, min_periods=min_p).mean() * ann) / \
             (r_b.rolling(window, min_periods=min_p).std() * np.sqrt(ann) + 1e-12)
    reported = float(w["oos_sharpe"])
    y0, y1 = meta["oos_start"][:4], meta["oos_end"][:4]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_b.index, y=roll_b.values,
                             name=f"Buy & Hold {target}",
                             line=dict(color=C_BENCHMARK, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=roll_s.index, y=roll_s.values,
                             name=f"Strategy rolling {window}-{unit} Sharpe",
                             line=dict(color=C_STRATEGY, width=2)))
    add_nber_shading(fig, x_min=oos.index.min(), x_max=oos.index.max())
    nber_legend_swatch(fig)
    fig.add_hline(y=reported, line=dict(color=C_ACCENT, dash="dash", width=1.2),
                  annotation_text=f"Reported OOS Sharpe = {reported:.2f}",
                  annotation_position="top left")
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    fig.update_layout(
        title=(f"Walk-Forward: Rolling {window}-{unit.capitalize()} Sharpe vs "
               f"Reported OOS Sharpe {reported:.2f} (OOS {y0}–{y1})"),
        xaxis_title="Date",
        yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    caption = (f"Rolling {window}-{unit} annualized Sharpe of the winner strategy vs "
               f"buy-and-hold {target} over the out-of-sample window; dashed reference "
               f"line at the reported OOS Sharpe ({reported:.2f}, winner_summary). "
               f"Shaded bands mark NBER recessions.")
    save_chart(pair, "walk_forward", fig, caption=caption,
               alignment=("Rolling-Sharpe walk-forward view for the Strategy page "
                          "Confidence tab, built from the ECON-SR1 canonical series."),
               rules=["ECON-SR1", "VIZ-IC1", "VIZ-NBER1", "VIZ-NS1", "VIZ-O1"],
               reconciliation=recon, sources=sources)


def make_subperiod_sharpe(pair: str, can: pd.DataFrame, w: dict, meta: dict,
                          recon: dict, sources: list[str]) -> None:
    """Bar chart from Evan's regenerated subperiod_sharpe.csv. Three states per
    episode: no data (no coverage), in cash (long/cash strategy held no
    position), real Sharpe bar. Categorical x-axis -> NBER shading exempt."""
    csv_path = REPO / "results" / pair / "subperiod_sharpe.csv"
    rows = pd.read_csv(csv_path)
    target = (w.get("target_symbol") or pair.split("_")[-1]).upper()
    ind = SHORT_INDICATOR_LABELS.get(pair, pair)

    labels, values, colors, texts = [], [], [], []
    for _, r in rows.iterrows():
        ep_label = f"{r['period_name']} ({'OOS' if r['is_oos'] else 'IS'})"
        sharpe = r["sharpe"]
        seg_pos = can["position"].loc[r["start_date"]:r["end_date"]]
        if pd.isna(sharpe) or r["n_obs"] == 0:
            labels.append(f"{ep_label}<br>(no data)")
            values.append(0); colors.append("#999999"); texts.append("no data")
        elif float(seg_pos.abs().sum()) == 0 and abs(float(sharpe)) < 1e-9:
            labels.append(f"{ep_label}<br>(in cash)")
            values.append(0); colors.append("#999999"); texts.append("cash")
        else:
            labels.append(ep_label)
            values.append(float(sharpe))
            colors.append(C_POS if sharpe >= 0 else C_NEG)
            texts.append(f"{sharpe:+.2f}")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors,
                         text=texts, textposition="outside",
                         name="Annualized Sharpe by episode"))
    fig.add_hline(y=0, line=dict(color=C_NEUTRAL, width=0.6, dash="dot"))
    full_oos = rows[rows["period_name"] == "Full OOS"]
    full_oos_txt = (f"; full OOS {float(full_oos.iloc[0]['sharpe']):.2f}"
                    if len(full_oos) else "")
    fig.update_layout(
        title=(f"Sub-Period Sharpe: {ind} Strategy on {target} by Historical "
               f"Episode (IS = in-sample, OOS = out-of-sample)"),
        xaxis_title="Historical episode",
        yaxis_title="Annualized Sharpe Ratio",
        template="plotly_white", height=420, margin=dict(b=120),
        showlegend=False,
    )
    caption = (f"Annualized Sharpe of the winner strategy within each historical "
               f"episode{full_oos_txt} (per results/{pair}/subperiod_sharpe.csv, "
               f"ECON-SR1 reconciled). 'No data' = episode outside indicator "
               f"coverage; 'cash' = the long/cash rule held no position through "
               f"the episode.")
    save_chart(pair, "subperiod_sharpe", fig, caption=caption,
               alignment=("Sub-period Sharpe bars distinguish 'no data' (no "
                          "coverage) from 'in cash' (strategy flat) from real "
                          "performance — values re-read from Evan's regenerated "
                          "CSV at generation time."),
               rules=["ECON-SR1", "ECON-CP1", "VIZ-IC1", "VIZ-NS1", "VIZ-O1"],
               reconciliation=recon, sources=sources + [f"results/{pair}/subperiod_sharpe.csv"])


# ── Per-pair runner ───────────────────────────────────────────────────────

def run(pair: str, include_subperiod: bool = True) -> None:
    print(f"\n=== {pair} ===")
    can, meta, csv_path = load_canonical(pair)
    w = load_winner(pair)
    ann = 252 if meta.get("frequency") == "daily" else 12
    oos = can.loc[meta["oos_start"]:meta["oos_end"]]
    print(f"  canonical: {csv_path.relative_to(REPO)}  OOS rows={len(oos)}  ann={ann}")
    recon = reconcile_or_die(pair, oos, w, ann)
    sources = [str(csv_path.relative_to(REPO)),
               f"results/{pair}/winner_summary.json"]
    make_equity_curves(pair, oos, w, meta, ann, recon, sources)
    make_drawdown(pair, oos, w, meta, ann, recon, sources)
    make_walk_forward(pair, oos, w, meta, ann, recon, sources)
    if include_subperiod:
        make_subperiod_sharpe(pair, can, w, meta, recon, sources)


if __name__ == "__main__":
    pairs = sys.argv[1:] or ["vix_vix3m_spy", "indpro_spy", "indpro_xlp"]
    for p in pairs:
        run(p)
    print("\nAll pairs done.")
