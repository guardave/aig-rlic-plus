#!/usr/bin/env python3
"""
Chart Generation: HY-IG Credit Spread (fresh) -> S&P 500 (SPY)
===============================================================
Pair ID: hy_ig_spy  (Wave 10G.4D 22-chart suite; 2026-10-16 rebuild reads RUN_TAG 20261016 artifacts)

Produces 22 Plotly JSON charts + 22 _meta.json sidecars, all with
bare filenames per VIZ-NM1 (no pair_id prefix in filename).

Palette: okabe_ito_2026 aliases
  indicator   → primary_data_trace   #D55E00
  target      → secondary_data_trace #0072B2
  benchmark   → benchmark_trace      #6C7A89

Author: Viz Vera
Date:   2026-04-22
"""

import os
import sys
import json
import datetime  # noqa: F401  (kept for backward compat with downstream imports)
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _stamp import iso_utc_now  # noqa: E402
import chart_provenance  # noqa: E402  (records chart inputs; imported before any data is read)

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paths ────────────────────────────────────────────────────────────────
BASE_DIR   = str(Path(__file__).resolve().parents[1])
RUN_TAG    = "20261017"   # results vintage consumed (Phase B harness pilot)
PAIR_ID    = "hy_ig_spy"
DATA_DIR   = os.path.join(BASE_DIR, "data")
RESULTS    = os.path.join(BASE_DIR, "results", PAIR_ID)
CHART_DIR  = os.path.join(BASE_DIR, "output", "charts", PAIR_ID, "plotly")
os.makedirs(CHART_DIR, exist_ok=True)

# ── Palette (okabe_ito_2026 v1.1.0) ──────────────────────────────────────
PALETTE_ID  = "okabe_ito_2026"
C_INDICATOR = "#D55E00"   # primary_data_trace  → indicator (HY-IG spread)
C_TARGET    = "#0072B2"   # secondary_data_trace → target (SPY)
C_TERTIARY  = "#009E73"   # tertiary_data_trace
C_BENCHMARK = "#6C7A89"   # benchmark_trace      → B&H comparison lines
C_ALERT     = "#CC79A7"   # pink (stress)
C_NEUTRAL   = "#999999"   # hold/neutral
C_YELLOW    = "#E69F00"
NBER_SHADING = "rgba(150,120,120,0.22)"
EVENT_LINE   = "#4D4D4D"
TEMPLATE     = "plotly_white"

# Quartile gradient: green→yellow→orange→red (Q1 tight/bullish → Q4 wide/bearish)
C_Q = ["#009E73", "#F0E442", "#E69F00", "#D55E00"]

# Categorical extended palette
C_CAT = ["#D55E00", "#0072B2", "#009E73", "#E69F00", "#CC79A7", "#F0E442", "#56B4E9", "#000000"]

# ── Rules applied (for sidecars) ─────────────────────────────────────────
RULES_APPLIED = ["VIZ-V8", "VIZ-V11", "VIZ-NM1", "VIZ-IC1"]

# ── NBER Recessions ───────────────────────────────────────────────────────
RECESSIONS = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

# ── Event timeline (from Ray's CSV, top events) ──────────────────────────
EVENT_CSV = os.path.join(BASE_DIR, "docs", "event_timeline_hy_ig_spy_20260422.csv")
_evt_cache = None

def _load_events():
    global _evt_cache
    if _evt_cache is None:
        if os.path.exists(EVENT_CSV):
            _evt_cache = pd.read_csv(EVENT_CSV, parse_dates=["date"])
        else:
            _evt_cache = pd.DataFrame(columns=["date", "event", "expected_direction", "source"])
    return _evt_cache

# Key events for annotation (max 5 spread over full history)
KEY_EVENTS = [
    ("2001-09-11", "9/11"),
    ("2008-09-15", "Lehman"),
    ("2020-03-23", "COVID Low"),
    ("2022-06-16", "Rate Shock"),
]

# ── Data loaders ─────────────────────────────────────────────────────────
def _load_master():
    return pd.read_parquet(
        os.path.join(DATA_DIR, "hy_ig_spy_daily_20000101_20260422.parquet")
    )

def _load_signals():
    """Latest committed signals parquet (causal HMM/MS since 20261016)."""
    return pd.read_parquet(os.path.join(RESULTS, f"signals_{RUN_TAG}.parquet"))


def _load_winner():
    with open(os.path.join(RESULTS, "winner_summary.json")) as f:
        return json.load(f)

def _oos_start():
    return "2019-10-01"

def _drawdown(cum):
    peak = cum.expanding().max()
    return (cum / peak - 1)

def _build_winner_curve(df, oos_start):
    """ECON-SR1: read the canonical winner series (no re-derivation)."""
    sr = pd.read_csv(os.path.join(RESULTS, f"strategy_returns_{RUN_TAG}.csv"), parse_dates=["date"]).set_index("date")
    sr = sr[sr.index >= oos_start]
    return sr.index, sr["strategy_return"].fillna(0), sr["benchmark_return"].fillna(0)


def _winner_label():
    w = _load_winner()
    return f"{w['signal_code']}/{w['threshold_code']}/{w['strategy_code']}/L{w['lead_value']}"


def _sh(r):
    r = pd.Series(r).dropna()
    return float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else float("nan")


def _add_recessions(fig, idx_min, idx_max, row=None, col=None):
    """Add NBER recession shading. For multi-panel, pass row/col."""
    for s, e in RECESSIONS:
        ts, te = pd.Timestamp(s), pd.Timestamp(e)
        if te < idx_min or ts > idx_max:
            continue
        kwargs = dict(
            x0=max(ts, idx_min), x1=min(te, idx_max),
            fillcolor=NBER_SHADING, layer="below", line_width=0,
        )
        if row is not None:
            fig.add_vrect(row=row, col=col, **kwargs)
        else:
            fig.add_vrect(**kwargs)


def _note(fig, text, y=-0.12, size=9, yanchor="auto"):
    fig.add_annotation(
        text=text, xref="paper", yref="paper",
        x=0, y=y, showarrow=False,
        font=dict(size=size, color="#666666" if size > 9 else "#888888"), xanchor="left", yanchor=yanchor,
        align="left",
    )


def _save_chart(fig, name, narrative_note, method_name=None, expected_chart_type="line"):
    """Save chart JSON + sidecar _meta.json. Run VIZ-IC1 pre-save assertions."""
    # VIZ-IC1 assertions
    fig_dict = json.loads(fig.to_json())
    assert fig_dict.get("data"), f"VIZ-IC1 FAIL {name}: no data traces"
    assert fig_dict.get("layout", {}).get("title", {}).get("text"), f"VIZ-IC1 FAIL {name}: no title"
    traces = fig_dict["data"]
    assert len(traces) >= 1, f"VIZ-IC1 FAIL {name}: 0 traces"

    # Save chart
    chart_path = os.path.join(CHART_DIR, f"{name}.json")
    with open(chart_path, "w") as f:
        json.dump(fig_dict, f)
    chart_provenance.record(PAIR_ID, chart_path, (), "scripts/generate_charts_hy_ig_spy.py")

    # Save sidecar (VIZ-O1: disposition mandate; default "consumed" — every
    # chart this generator emits is rendered by a page_template slot. If a
    # future variant of this generator produces an exploratory chart, pass
    # `exploratory=True` + `vera_rationale` and route it via
    # analyst_suggestions.json per VIZ-E1.)
    meta = {
        "chart_name": name,
        "pair_id": PAIR_ID,
        "palette_id": PALETTE_ID,
        "rules_applied": RULES_APPLIED + ["VIZ-O1"],
        "disposition": "consumed",
        "narrative_alignment_note": narrative_note,
        "created_at": iso_utc_now(),
        "method_name": method_name or name,
        "expected_chart_type": expected_chart_type,
    }
    meta_path = os.path.join(CHART_DIR, f"{name}_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  OK  {name}.json + _meta.json  [{len(traces)} trace(s)]")
    return fig_dict


# ════════════════════════════════════════════════════════════════════════
# STORY PAGE (4 + 3 zoom)
# ════════════════════════════════════════════════════════════════════════

def chart_hero():
    """HY-IG OAS spread (left) + SPY price (right), full 2000-2026 dual-axis."""
    df = _load_master()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["hy_ig_spread_pct"],
            name="HY-IG OAS Spread (%)",
            line=dict(color=C_INDICATOR, width=1.5),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["spy"],
            name="SPY (adj. close $)",
            line=dict(color=C_TARGET, width=1.5),
        ),
        secondary_y=True,
    )

    _add_recessions(fig, df.index.min(), df.index.max())

    # Key event annotations
    for dt_str, label in KEY_EVENTS:
        dt = pd.Timestamp(dt_str)
        if dt < df.index.min() or dt > df.index.max():
            continue
        idx = df.index.get_indexer([dt], method="nearest")[0]
        y_val = df["hy_ig_spread_pct"].iloc[idx]
        fig.add_annotation(
            x=dt, y=y_val, text=label, showarrow=True,
            arrowhead=2, arrowsize=0.8, ax=0, ay=-40,
            font=dict(size=9, color=EVENT_LINE),
            bgcolor="rgba(255,255,255,0.82)", borderpad=2,
        )

    fig.update_layout(
        title=dict(text="HY-IG Credit Spread (inverted axis) and SPY Price, 2000-2026"),
        template=TEMPLATE, hovermode="x unified", height=520,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    fig.update_yaxes(title_text="HY-IG OAS Spread (%)", secondary_y=False, autorange="reversed")
    fig.update_yaxes(title_text="SPY Price ($)", secondary_y=True)
    _note(fig, "Source: ICE BofA HY OAS minus US Corporate OAS (FRED BAMLH0A0HYM2 - BAMLC0A0CM); SPY via Yahoo Finance. Gray = NBER recessions.")
    _save_chart(fig, "hero",
                narrative_note="Descriptive history of the HY-IG OAS spread (inverted left axis) and SPY price, 2000-2026.",
                expected_chart_type="dual_axis_line")


def chart_regime_stats():
    """Annualized SPY returns bar chart grouped by HMM regime (calm vs stress)."""
    df = _load_master()
    sig_df = _load_signals()

    prob_col = "hmm_2state_prob_stress"
    # A day with an undefined stress probability (the first day: no filtered estimate exists)
    # is neither calm nor stress; `NaN > 0.5` is False and would count it as calm.
    prob = sig_df[prob_col].reindex(df.index, method="ffill")
    stress = prob > 0.5
    calm = (prob <= 0.5) & prob.notna()

    spy_ret = df["spy_ret"] if "spy_ret" in df.columns else df["spy"].pct_change()

    calm_ret = spy_ret[calm].dropna()
    stress_ret = spy_ret[stress].dropna()

    def stats(r):
        ann_ret = r.mean() * 252
        ann_vol = r.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        return ann_ret * 100, ann_vol * 100, sharpe

    regimes = ["Calm (filtered stress prob ≤ 0.5)", "Stress (filtered stress prob > 0.5)"]
    ann_rets = []
    ann_vols = []
    sharpes = []

    for r in [calm_ret, stress_ret]:
        ar, av, sr = stats(r)
        ann_rets.append(ar)
        ann_vols.append(av)
        sharpes.append(sr)

    # VIZ-QR1 (2026-06-10, fix260610_xpair_general): dual-panel Sharpe +
    # Return side-by-side on the pair's native regime axis (HMM Calm/Stress
    # here — this pair's regime conditioning is HMM-state-based, not
    # quartile-based). Shared helper keeps the layout consistent with the
    # quartile pairs.
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts._quartile_chart import make_dual_panel_regime_chart

    fig = make_dual_panel_regime_chart(
        quartile_labels=regimes,
        sharpe=[round(s, 2) for s in sharpes],
        ann_return_pct=[round(r, 1) for r in ann_rets],
        signal_label="HMM Credit Regime",
        x_axis_title="HMM-Identified Regime (stress probability threshold 0.5)",
        axis_noun="",
        sample_sizes=[int(calm_ret.shape[0]), int(stress_ret.shape[0])],
    )
    fig.update_layout(title=dict(
        text="Same-Day SPY Sharpe and Return by Causal HMM Credit Regime (2000-2026)"))

    _note(fig, "2-state HMM on [daily spread change, VIX], fit on 2000-2019-09 only, forward-filtered. Same-day (concurrent) returns: descriptive, not a forecast.")
    _save_chart(fig, "regime_stats",
                narrative_note="Concurrent SPY Sharpe/return in the causal HMM calm vs stress states (descriptive). VIZ-QR1 dual-panel.",
                method_name="HMM 2-State",
                expected_chart_type="bar")


def _chart_history_zoom(name, start_str, end_str, title, episode_label):
    """Dual-panel zoom chart for a historical episode."""
    df = _load_master()
    sig_df = _load_signals()

    ts, te = pd.Timestamp(start_str), pd.Timestamp(end_str)
    zoom = df[(df.index >= ts) & (df.index <= te)].copy()
    if zoom.empty:
        print(f"  SKIP  {name} (no data in range)")
        return

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.4], vertical_spacing=0.05,
        subplot_titles=[f"HY-IG Spread (%)", f"SPY Price ($)"],
    )

    # Panel 1: HY-IG spread
    fig.add_trace(
        go.Scatter(x=zoom.index, y=zoom["hy_ig_spread_pct"],
                   name="HY-IG Spread (%)", line=dict(color=C_INDICATOR, width=1.8)),
        row=1, col=1,
    )

    # Panel 2: SPY
    fig.add_trace(
        go.Scatter(x=zoom.index, y=zoom["spy"],
                   name="SPY ($)", line=dict(color=C_TARGET, width=1.8)),
        row=2, col=1,
    )

    # NBER recession shading per panel
    _add_recessions(fig, ts, te, row=1, col=1)
    _add_recessions(fig, ts, te, row=2, col=1)

    # Event annotations from Ray's timeline
    evts = _load_events()
    ep_evts = evts[(evts["date"] >= ts) & (evts["date"] <= te)].head(5)
    for _, row_ev in ep_evts.iterrows():
        dt = row_ev["date"]
        if dt < zoom.index.min() or dt > zoom.index.max():
            continue
        idx = zoom.index.get_indexer([dt], method="nearest")[0]
        y_val = zoom["hy_ig_spread_pct"].iloc[idx]
        short_label = row_ev["event"][:40] if len(str(row_ev["event"])) > 40 else str(row_ev["event"])
        fig.add_annotation(
            x=dt, y=y_val, text=short_label[:30],
            showarrow=True, arrowhead=2, arrowsize=0.7, ax=0, ay=-35,
            font=dict(size=8, color=EVENT_LINE),
            bgcolor="rgba(255,255,255,0.82)", borderpad=2,
            row=1, col=1,
        )

    fig.update_layout(
        title=dict(text=title),
        template=TEMPLATE, height=520, hovermode="x unified",
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    fig.update_yaxes(title_text="HY-IG Spread (%)", row=1, col=1)
    fig.update_yaxes(title_text="SPY Price ($)", row=2, col=1)
    _note(fig, f"Zoom: {episode_label}. Source: FRED / Yahoo Finance. Gray = NBER recession.")
    _save_chart(fig, name,
                narrative_note=f"Episode zoom ({episode_label}): HY-IG spread and SPY price over the episode window.",
                method_name="History Zoom",
                expected_chart_type="dual_panel_line")


def chart_history_zoom_dotcom():
    _chart_history_zoom(
        "history_zoom_dotcom", "2000-01-01", "2002-12-31",
        "Dot-Com Bust (2000-2002): HY-IG Spread and SPY",
        "Dot-Com 2000-2002",
    )


def chart_history_zoom_gfc():
    _chart_history_zoom(
        "history_zoom_gfc", "2007-01-01", "2009-12-31",
        "Global Financial Crisis (2007-2009): HY-IG Spread and SPY",
        "GFC 2007-2009",
    )


def chart_history_zoom_covid():
    _chart_history_zoom(
        "history_zoom_covid", "2019-06-01", "2021-06-30",
        "COVID Shock (2019-2021): HY-IG Spread and SPY",
        "COVID 2019-2021",
    )


# ════════════════════════════════════════════════════════════════════════
# EVIDENCE PAGE LEVEL 1 (3)
# ════════════════════════════════════════════════════════════════════════

def chart_correlations():
    """Rolling 252d correlation: HY-IG spread LEVEL vs SPY same-day daily return (descriptive)."""
    df = _load_master()
    spy_ret = df["spy_ret"] if "spy_ret" in df.columns else df["spy"].pct_change()
    spread  = df["hy_ig_spread_pct"]
    rolling_corr = spread.rolling(252).corr(spy_ret)
    rc = rolling_corr.dropna()
    share_neg = float((rc < 0).mean() * 100)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rolling_corr.index, y=rolling_corr.values,
        name="Rolling 252d Correlation",
        line=dict(color=C_INDICATOR, width=1.5),
        fill="tozeroy", fillcolor="rgba(213,94,0,0.10)",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=C_NEUTRAL, line_width=0.8)
    _add_recessions(fig, df.index.min(), df.index.max())
    fig.update_layout(
        title=dict(text="Rolling 252-Day Correlation: HY-IG Spread Level vs Same-Day SPY Return"),
        xaxis_title="Date",
        yaxis_title="Rolling 252-Day Correlation",
        template=TEMPLATE, height=450, margin=dict(r=180, b=80),
    )
    _note(fig, f"Same-day (not forward) Pearson r between the spread level (pp) and SPY daily returns; negative on {share_neg:.0f}% of days. Gray = NBER recessions.")
    _save_chart(fig, "correlations",
                narrative_note=f"Descriptive same-day correlation of spread level with SPY daily return; negative on {share_neg:.0f}% of rolling windows.",
                method_name="Rolling Correlation",
                expected_chart_type="line")


def chart_ccf():
    """CCF of daily spread CHANGE vs SPY daily return, lags -20..+20 trading days.
    Returns are not differenced (they are already close to white noise); differencing them
    induces an MA(1) artefact, which the earlier version of this chart did."""
    df = _load_master()
    d = pd.DataFrame({"ds": df["hy_ig_spread_pct"].diff(), "r": df["spy"].pct_change()}).dropna()
    lags = list(range(-20, 21))
    vals = []
    for k in lags:   # k<0: spread change k days EARLIER vs today's return (spread leads)
        vals.append(d["ds"].shift(-k).corr(d["r"]))
    n = len(d)
    sig_band = 1.96 / np.sqrt(n)
    colors = [C_INDICATOR if v < 0 else C_TARGET for v in vals]
    k0 = vals[lags.index(0)]
    lead_sig = [(k, v) for k, v in zip(lags, vals) if k < 0 and abs(v) > sig_band]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=lags, y=vals, marker_color=colors, name="Cross-Correlation"))
    fig.add_hline(y=sig_band, line_dash="dash", line_color=C_NEUTRAL, line_width=1,
                  annotation_text=f"\u00b195% band ({sig_band:.3f})", annotation_font_size=9)
    fig.add_hline(y=-sig_band, line_dash="dash", line_color=C_NEUTRAL, line_width=1)
    fig.add_hline(y=0, line_color="black", line_width=0.5)
    fig.update_layout(
        title=dict(text=f"Cross-Correlation: Daily Spread Change vs SPY Daily Return (lag 0 r = {k0:+.3f})"),
        xaxis_title="Lag (trading days; negative = spread change precedes the SPY return)",
        yaxis_title="Cross-Correlation",
        template=TEMPLATE, height=450, showlegend=False, margin=dict(r=180, b=80),
    )
    _note(fig, f"Daily spread change (pp) vs SPY daily return, {n} days. {len(lead_sig)} of 20 negative lags outside the iid \u00b195% band.")
    _save_chart(fig, "ccf",
                narrative_note=f"Lag-0 r={k0:+.3f}; {len(lead_sig)} of 20 spread-leads lags outside the iid 95% band.",
                method_name="Cross-correlation (daily changes)",
                expected_chart_type="bar")


def chart_granger_f_by_lag():
    """Granger F by monthly lag 1-12 (monthly spread change -> compounded monthly SPY return),
    with the per-lag 5% F critical value."""
    from scipy.stats import f as fdist
    gdf = pd.read_csv(os.path.join(RESULTS, "granger_by_lag.csv"))
    crit = [fdist.ppf(0.95, int(r.df_num), int(r.df_den)) for r in gdf.itertuples()]
    bar_colors = [C_INDICATOR if p < 0.05 else C_NEUTRAL for p in gdf["p_value"]]
    n_sig = int((gdf["p_value"] < 0.05).sum())
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=gdf["lag"], y=gdf["f_statistic"], marker_color=bar_colors, name="Granger F-stat",
        text=[f"p={p:.3f}" for p in gdf["p_value"]], textposition="outside", textfont=dict(size=9),
    ))
    fig.add_trace(go.Scatter(x=gdf["lag"], y=crit, mode="lines+markers", name="5% critical F (per lag)",
                             line=dict(color=C_BENCHMARK, dash="dash", width=1.5), marker=dict(size=5)))
    fig.update_layout(
        title=dict(text=f"Granger F-Test, Monthly Spread Change \u2192 SPY Monthly Return: p<0.05 at {n_sig} of 12 Lags"),
        xaxis_title="Lag (months)",
        yaxis_title="Granger F-Statistic",
        template=TEMPLATE, height=450, showlegend=True, margin=dict(r=180, b=80),
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
    )
    _note(fig, "Month-end spread change vs compounded monthly SPY return (2000-2026). Homoskedastic F-test. Vermillion = p<0.05.")
    _save_chart(fig, "granger_f_by_lag",
                narrative_note=f"Monthly Granger test (spread change -> SPY return): p<0.05 at {n_sig} of 12 lags.",
                method_name="Granger Causality",
                expected_chart_type="bar")


# ════════════════════════════════════════════════════════════════════════
# EVIDENCE PAGE LEVEL 2 (5)
# ════════════════════════════════════════════════════════════════════════

def chart_hmm_regime_probs():
    """Smoothed HMM stress probability time series with SPY overlay."""
    sig_df = _load_signals()
    df = _load_master()

    prob_col = "hmm_2state_prob_stress"

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Stress probability fill
    fig.add_trace(
        go.Scatter(
            x=sig_df.index, y=sig_df[prob_col],
            fill="tozeroy",
            fillcolor="rgba(204,121,167,0.15)",
            line=dict(color=C_ALERT, width=1),
            name="P(Stress State)",
        ),
        secondary_y=False,
    )

    # Shade stress episodes
    stress = sig_df[prob_col] > 0.5
    if stress.any():
        starts = sig_df.index[stress & ~stress.shift(1, fill_value=False)]
        ends   = sig_df.index[stress & ~stress.shift(-1, fill_value=False)]
        for s_, e_ in zip(starts, ends):
            fig.add_vrect(x0=s_, x1=e_,
                          fillcolor="rgba(204,121,167,0.10)",
                          layer="below", line_width=0)

    # SPY secondary
    spy_aligned = df["spy"].reindex(sig_df.index, method="ffill")
    fig.add_trace(
        go.Scatter(x=sig_df.index, y=spy_aligned,
                   name="SPY Price ($)",
                   line=dict(color=C_TARGET, width=1.5)),
        secondary_y=True,
    )

    # 0.5 threshold
    fig.add_hline(y=0.5, line_dash="dash", line_color=C_NEUTRAL, line_width=1,
                  annotation_text="0.5", annotation_font_size=9)

    _add_recessions(fig, sig_df.index.min(), sig_df.index.max())

    fig.update_layout(
        title=dict(text=f"Causal HMM Stress Probability (IS-fit, forward-filtered) and SPY: {(sig_df[prob_col].dropna() > 0.5).mean()*100:.0f}% of Days Above 0.5"),
        template=TEMPLATE, hovermode="x unified", height=500,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    fig.update_yaxes(title_text="P(Stress State)", range=[0, 1.05], secondary_y=False)
    fig.update_yaxes(title_text="SPY Price ($)", secondary_y=True)
    _note(fig, "2-state Gaussian HMM fit on 2000-01..2019-09 only; P(stress_t | data to t). Pink = P > 0.5. Gray = NBER recessions.")
    _save_chart(fig, "hmm_regime_probs",
                narrative_note="Causal (filtered) HMM stress probability over 2000-2026; IS-fit params; no smoothing.",
                method_name="HMM 2-State",
                expected_chart_type="line")


def chart_regime_quartile_returns():
    """SPY NEXT-MONTH annualised return by month-end spread quartile (forward test)."""
    rdf = pd.read_csv(os.path.join(RESULTS, "regime_quartile_returns.csv"))
    ft = pd.read_csv(os.path.join(RESULTS, f"regime_quartile_forward_tests_{RUN_TAG}.csv")).set_index("horizon_months")
    rdf["ann_return_pct"] = rdf["ann_return"] * 100
    bar_text = [f"{row['ann_return_pct']:.1f}%<br>Sharpe {row['sharpe']:.2f}" for _, row in rdf.iterrows()]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{q}<br>({lo:.2f}-{hi:.2f} pp)" for q, lo, hi in zip(rdf["quartile"], rdf["spread_low"], rdf["spread_high"])],
        y=rdf["ann_return_pct"], marker_color=C_Q[:len(rdf)],
        text=bar_text, textposition="outside", textfont=dict(size=11), name="Ann. next-month return (%)",
    ))
    r1, r3 = ft.loc[1], ft.loc[3]
    fig.update_layout(
        title=dict(text=f"SPY Next-Month Return by HY-IG Spread Quartile: Q4-Q1 = {r1.q4_minus_q1*100:+.2f} pp/month (HAC t {r1.q4_minus_q1_hac_t:.2f})"),
        xaxis_title="Month-end HY-IG spread quartile (Q1 = tightest, Q4 = widest)",
        yaxis_title="Annualized next-month SPY return (%)",
        template=TEMPLATE, height=450, showlegend=False, margin=dict(r=180, b=80),
    )
    _note(fig, f"Forward test, {int(r1.n_months)} months. 3-month: Q4-Q1 {r3.q4_minus_q1*100:+.2f} pp, HAC t {r3.q4_minus_q1_hac_t:.2f}. Not monotonic.")
    _save_chart(fig, "regime_quartile_returns",
                narrative_note=f"Forward 1m Q4-Q1 {r1.q4_minus_q1*100:+.2f} pp (t {r1.q4_minus_q1_hac_t:.2f}); 3m {r3.q4_minus_q1*100:+.2f} pp (t {r3.q4_minus_q1_hac_t:.2f}); not monotonic.",
                method_name="Quartile Returns",
                expected_chart_type="bar")


def chart_transfer_entropy():
    """Transfer entropy: HY-IG → SPY vs SPY → HY-IG (directional information flow)."""
    # Transfer entropy computed via rolling mutual information proxy
    df = _load_master()
    sig_df = _load_signals()

    spy_ret = df["spy_ret"].dropna() if "spy_ret" in df.columns else df["spy"].pct_change().dropna()
    spread  = sig_df["hy_ig_spread_pct"].dropna() if "hy_ig_spread_pct" in sig_df.columns else df["hy_ig_spread_pct"].dropna()

    common = spy_ret.index.intersection(spread.index)
    r = spy_ret.loc[common]
    s = spread.loc[common]

    # Discretize into quintiles for entropy
    r_q = pd.qcut(r, 5, labels=False, duplicates="drop")
    s_q = pd.qcut(s, 5, labels=False, duplicates="drop")

    # Rolling window transfer entropy proxy: conditional mutual info
    window = 504  # 2 years
    dates = []
    te_hy_spy = []
    te_spy_hy = []

    for i in range(window, len(common), 21):  # step by month
        w_r = r_q.iloc[i-window:i].dropna()
        w_s = s_q.iloc[i-window:i].dropna()
        idx = w_r.index.intersection(w_s.index)
        wr  = w_r.loc[idx].values
        ws  = w_s.loc[idx].values

        def _te(x, y, lag=1):
            """Approximate transfer entropy x→y via conditional correlation proxy."""
            n = len(x) - lag
            if n < 20:
                return 0.0
            x_lag = x[:n]
            y_curr = y[lag:]
            y_lag  = y[:n]
            # Simple MI proxy: corr²
            try:
                c1 = np.corrcoef(x_lag, y_curr)[0, 1] ** 2
                c2 = np.corrcoef(y_lag, y_curr)[0, 1] ** 2
                return max(0, c1 - c2)
            except Exception:
                return 0.0

        te_hy_spy.append(_te(ws, wr))
        te_spy_hy.append(_te(wr, ws))
        dates.append(common[i])

    te_df = pd.DataFrame({"date": dates, "HY_to_SPY": te_hy_spy, "SPY_to_HY": te_spy_hy})
    te_df = te_df.set_index("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=te_df.index, y=te_df["HY_to_SPY"],
        name="HY-IG → SPY",
        line=dict(color=C_INDICATOR, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=te_df.index, y=te_df["SPY_to_HY"],
        name="SPY → HY-IG",
        line=dict(color=C_TARGET, width=2, dash="dash"),
    ))

    fig.update_layout(
        title=dict(text=f"Proxy Information Flow (Rolling 504d): Mean HY-IG\u2192SPY {te_df['HY_to_SPY'].mean():.4f} vs SPY\u2192HY-IG {te_df['SPY_to_HY'].mean():.4f}"),
        xaxis_title="Date",
        yaxis_title="Transfer Entropy Proxy (rolling 504d)",
        template=TEMPLATE, height=450,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    _note(fig, "Not a true transfer entropy: squared-correlation difference on quintile ranks (lag 1 day). No significance test.")
    _save_chart(fig, "transfer_entropy",
                narrative_note="Proxy (squared-correlation difference) of lagged information flow in both directions; no significance test.",
                method_name="Transfer Entropy",
                expected_chart_type="line")


def chart_local_projections():
    """Local projections: spread level -> SPY forward return at 5/21/63 trading days (HAC, maxlags >= h-1)."""
    lp = pd.read_csv(os.path.join(RESULTS, f"core_models_{RUN_TAG}", "local_projections.csv"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(lp["horizon_days"]) + list(lp["horizon_days"][::-1]),
        y=list(lp["ci_upper"]) + list(lp["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(0,114,178,0.15)", line=dict(color="rgba(0,0,0,0)"), name="95% CI (HAC)",
    ))
    fig.add_trace(go.Scatter(x=lp["horizon_days"], y=lp["coef"], mode="lines+markers",
                             line=dict(color=C_TARGET, width=2.5), marker=dict(size=10), name="Coefficient"))
    sig = lp[lp["p_value"] < 0.05]
    if len(sig) > 0:
        fig.add_trace(go.Scatter(x=sig["horizon_days"], y=sig["coef"], mode="markers",
                                 marker=dict(size=14, color=C_INDICATOR, symbol="star"), name="p < 0.05"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.7)
    fig.update_layout(
        title=dict(text=f"Local Projections, Spread Level \u2192 SPY Forward Return: p<0.05 at {len(sig)} of {len(lp)} Horizons"),
        xaxis_title="Forecast Horizon (trading days)",
        yaxis_title="Coefficient (return per pp of spread)",
        template=TEMPLATE, height=450, margin=dict(r=180, b=80),
    )
    _note(fig, "Controls: VIX, 10y-3m. Newey-West HAC SE with maxlags = max(0.75 n^(1/3), h-1). Overlapping windows.")
    _save_chart(fig, "local_projections",
                narrative_note=", ".join(f"h={r.horizon_days}d t={r.t_stat:.2f} p={r.p_value:.3f}" for r in lp.itertuples()),
                method_name="Local Projections",
                expected_chart_type="line")


def chart_quantile_regression():
    """Quantile regression slope of the 21-day forward SPY return on the spread level."""
    qr = pd.read_csv(os.path.join(RESULTS, f"core_models_{RUN_TAG}", "quantile_regression.csv"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(qr["quantile"]) + list(qr["quantile"][::-1]),
        y=list(qr["ci_upper"]) + list(qr["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(0,114,178,0.15)", line=dict(color="rgba(0,0,0,0)"), name="95% CI",
    ))
    fig.add_trace(go.Scatter(x=qr["quantile"], y=qr["coef"], mode="lines+markers",
                             line=dict(color=C_TARGET, width=2.5), marker=dict(size=10), name="QR Coefficient"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.7)
    lo, hi = qr.loc[qr["quantile"] == 0.05, "coef"].iloc[0], qr.loc[qr["quantile"] == 0.95, "coef"].iloc[0]
    fig.update_layout(
        title=dict(text=f"Quantile Regression: Slope {lo:+.4f} at q05, {hi:+.4f} at q95 (Spread Widens the Distribution)"),
        xaxis_title="Quantile of the 21-day forward SPY return",
        yaxis_title="Coefficient (return per pp of spread)",
        template=TEMPLATE, height=450, margin=dict(r=180, b=80),
    )
    _note(fig, "Quantile regression of the SPY 21-trading-day forward return on the HY-IG spread level, daily 2000-2026.")
    _save_chart(fig, "quantile_regression",
                narrative_note=f"Slopes roughly symmetric around zero: q05 {lo:+.4f}, q95 {hi:+.4f}; wider spreads widen both tails.",
                method_name="Quantile Regression",
                expected_chart_type="line")


# ════════════════════════════════════════════════════════════════════════
# STRATEGY PAGE (4)
# ════════════════════════════════════════════════════════════════════════

def chart_equity_curves():
    """Winner vs buy-and-hold SPY, OOS growth of $1 (canonical strategy_returns series)."""
    df = _load_master()
    oos_start = _oos_start()
    _, strat_ret, spy_ret = _build_winner_curve(df, oos_start)
    w = _load_winner()
    bh_cum, strat_cum = (1 + spy_ret).cumprod(), (1 + strat_ret).cumprod()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat_cum.index, y=strat_cum.values,
                             name=f"Winner {_winner_label()} (Sharpe {w['oos_sharpe']:.2f})",
                             line=dict(color=C_TERTIARY, width=2.5)))
    fig.add_trace(go.Scatter(x=bh_cum.index, y=bh_cum.values, name=f"Buy & Hold SPY (Sharpe {w['bh_sharpe']:.2f})",
                             line=dict(color=C_BENCHMARK, width=2, dash="dash")))
    _add_recessions(fig, bh_cum.index.min(), bh_cum.index.max())
    fig.update_layout(
        title=dict(text=f"OOS Growth of $1: Winner Sharpe {w['oos_sharpe']:.2f} vs SPY Buy-and-Hold {w['bh_sharpe']:.2f} (from {oos_start})"),
        xaxis_title="Date", yaxis_title="Growth of $1", template=TEMPLATE, height=480,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"), margin=dict(r=180, b=130),
    )
    _net = ((w.get("winner_fields") or {}).get("oos_sharpe_net_5bp") or {}).get("text", "n/a")
    _note(fig, f"OOS {oos_start} to {w['oos_period_end']}. Rule selected on in-sample data.<br>Returns gross of costs; "
               f"at the trade log's 5 bp per position change the OOS Sharpe is {_net}.",
          y=-0.2, size=12, yanchor="top")
    _save_chart(fig, "equity_curves",
                narrative_note=f"OOS growth of $1: winner {strat_cum.iloc[-1]:.2f}, SPY {bh_cum.iloc[-1]:.2f}.",
                method_name="Strategy Backtest", expected_chart_type="line")


def chart_drawdown():
    """Winner OOS drawdown."""
    df = _load_master()
    oos_start = _oos_start()
    _, strat_ret, _ = _build_winner_curve(df, oos_start)
    strat_dd = _drawdown((1 + strat_ret).cumprod()) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat_dd.index, y=strat_dd.values, fill="tozeroy",
                             fillcolor="rgba(213,94,0,0.35)", line=dict(color=C_INDICATOR, width=1.5),
                             name=f"Drawdown (max {strat_dd.min():.1f}%)"))
    worst_idx = strat_dd.idxmin()
    fig.add_annotation(x=worst_idx, y=strat_dd.min(), text=f"MDD: {strat_dd.min():.1f}%",
                       showarrow=True, arrowhead=2, ax=40, ay=-20, font=dict(size=10, color=C_INDICATOR))
    fig.update_layout(
        title=dict(text=f"Winner OOS Drawdown: Max {strat_dd.min():.1f}% ({worst_idx.date()})"),
        xaxis_title="Date", yaxis_title="Drawdown from Peak (%)",
        template=TEMPLATE, height=400, showlegend=True, margin=dict(r=180, b=80),
    )
    _note(fig, f"OOS drawdown of the winner {_winner_label()} (canonical strategy_returns series).")
    _save_chart(fig, "drawdown", narrative_note=f"Winner OOS max drawdown {strat_dd.min():.1f}%.",
                method_name="Drawdown Analysis", expected_chart_type="area")


def chart_drawdown_comparison():
    """Winner vs B&H OOS drawdown overlay."""
    df = _load_master()
    oos_start = _oos_start()
    _, strat_ret, spy_ret = _build_winner_curve(df, oos_start)
    bh_dd = _drawdown((1 + spy_ret).cumprod()) * 100
    strat_dd = _drawdown((1 + strat_ret).cumprod()) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh_dd.index, y=bh_dd.values, fill="tozeroy", fillcolor="rgba(108,122,137,0.20)",
                             line=dict(color=C_BENCHMARK, width=1.5), name=f"Buy & Hold (max {bh_dd.min():.1f}%)"))
    fig.add_trace(go.Scatter(x=strat_dd.index, y=strat_dd.values, fill="tozeroy", fillcolor="rgba(0,158,115,0.15)",
                             line=dict(color=C_TERTIARY, width=1.5), name=f"Winner (max {strat_dd.min():.1f}%)"))
    fig.update_layout(
        title=dict(text=f"OOS Drawdowns: Winner {strat_dd.min():.1f}% vs SPY Buy-and-Hold {bh_dd.min():.1f}%"),
        xaxis_title="Date", yaxis_title="Drawdown from Peak (%)", template=TEMPLATE, height=450,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"), margin=dict(r=180, b=80),
    )
    _note(fig, f"OOS {oos_start} to 2026-04-22. Winner {_winner_label()}.")
    _save_chart(fig, "drawdown_comparison",
                narrative_note=f"OOS max drawdown: winner {strat_dd.min():.1f}%, SPY {bh_dd.min():.1f}%.",
                method_name="Drawdown Comparison", expected_chart_type="area")


def chart_walk_forward():
    """Calendar-year Sharpe of the winner rule vs SPY's Sharpe in the same year."""
    wf = pd.read_csv(os.path.join(RESULTS, f"tournament_validation_{RUN_TAG}", "walk_forward.csv"))
    w = wf[wf["rank"] == 1].sort_values("test_year")
    oos = w[w["is_oos_year"]]
    n_pos = int((w["oos_sharpe"] > 0).sum())
    n_beat = int((w["oos_sharpe"] > w["bh_sharpe"]).sum())
    n_pos_o = int((oos["oos_sharpe"] > 0).sum())
    n_beat_o = int((oos["oos_sharpe"] > oos["bh_sharpe"]).sum())
    colors = [C_TERTIARY if a > b else C_INDICATOR for a, b in zip(w["oos_sharpe"], w["bh_sharpe"])]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=w["test_year"].astype(str), y=w["oos_sharpe"], marker_color=colors,
                         name="Winner rule, calendar-year Sharpe",
                         text=[f"{v:.2f}" for v in w["oos_sharpe"]], textposition="outside", textfont=dict(size=9)))
    fig.add_trace(go.Scatter(x=w["test_year"].astype(str), y=w["bh_sharpe"], mode="markers", name="SPY same year",
                             marker=dict(symbol="line-ew-open", size=18, color=C_BENCHMARK, line=dict(width=3))))
    yrs = list(w["test_year"])
    if 2020 in yrs:
        fig.add_vline(x=yrs.index(2020) - 0.5, line_dash="dot", line_color=C_NEUTRAL, line_width=1,
                      annotation_text="OOS years", annotation_font_size=9)
    fig.add_hline(y=0, line_color="black", line_width=0.5)
    fig.update_layout(
        title=dict(text=f"Calendar-Year Sharpe: Positive {n_pos}/{len(w)} Years, Above SPY {n_beat}/{len(w)}; OOS Years {n_pos_o}/{len(oos)} and {n_beat_o}/{len(oos)}"),
        xaxis_title="Calendar Year", yaxis_title="Sharpe Ratio", template=TEMPLATE, height=480, showlegend=True,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"), margin=dict(r=180, b=80),
    )
    _note(fig, "Green = above SPY that year. Years before 2019-10 are in-sample (the rule was selected on them).")
    _save_chart(fig, "walk_forward",
                narrative_note=f"Positive {n_pos}/{len(w)} years, above SPY {n_beat}/{len(w)}; OOS years 2020-2026: positive {n_pos_o}/{len(oos)}, above SPY {n_beat_o}/{len(oos)}.",
                method_name="Walk-Forward Validation", expected_chart_type="bar")


# ════════════════════════════════════════════════════════════════════════
# STRATEGY CONFIDENCE + METHODOLOGY (3)
# ════════════════════════════════════════════════════════════════════════

def chart_tournament_scatter():
    """IS Sharpe (selection objective) vs OOS Sharpe for every IS-valid combo."""
    tdf = pd.read_csv(os.path.join(RESULTS, f"tournament_results_{RUN_TAG}.csv"))
    w = _load_winner()
    valid = tdf[(tdf["valid"]) & (tdf["signal"] != "BENCHMARK")].copy()
    bh = tdf[tdf["signal"] == "BENCHMARK"].iloc[0]
    rho = valid[["is_sharpe", "oos_sharpe"]].corr(method="spearman").iloc[0, 1]
    fig = go.Figure()
    for i, strat in enumerate(sorted(valid["strategy"].unique())):
        sub = valid[valid["strategy"] == strat]
        fig.add_trace(go.Scatter(
            x=sub["is_sharpe"], y=sub["oos_sharpe"], mode="markers",
            marker=dict(size=5, color=C_CAT[i % len(C_CAT)], opacity=0.55), name=strat,
            text=[f"{r.signal}/{r.threshold}/L{r.lead_days}" for r in sub.itertuples()],
            hovertemplate="%{text}<br>IS Sharpe: %{x:.2f}<br>OOS Sharpe: %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[w["is_sharpe"]], y=[w["oos_sharpe"]], mode="markers",
                             marker=dict(size=18, color=C_TERTIARY, symbol="star", line=dict(color="black", width=1)),
                             name=f"Winner (IS {w['is_sharpe']:.2f}, OOS {w['oos_sharpe']:.2f})"))
    fig.add_hline(y=float(bh["oos_sharpe"]), line_dash="dash", line_color=C_BENCHMARK, line_width=1.2,
                  annotation_text=f"SPY OOS {bh['oos_sharpe']:.2f}", annotation_font_size=9)
    fig.add_vline(x=float(bh["is_sharpe"]), line_dash="dot", line_color=C_BENCHMARK, line_width=1.2,
                  annotation_text=f"SPY IS {bh['is_sharpe']:.2f}", annotation_font_size=9)
    fig.update_layout(
        title=dict(text=f"Tournament: {len(valid)} IS-Valid Combos, In-Sample vs Out-of-Sample Sharpe (Spearman {rho:.2f})"),
        xaxis_title="In-sample Sharpe (selection objective)", yaxis_title="OOS Sharpe",
        template=TEMPLATE, height=500,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"), margin=dict(r=180, b=80),
    )
    _note(fig, f"Source: tournament_results_{RUN_TAG}.csv. Winner = stable lead range rule on in-sample data (D9). P2 is declared once per signal and lead.")
    _save_chart(fig, "tournament_scatter",
                narrative_note=f"{len(valid)} IS-valid combos; Spearman(IS, OOS) {rho:.2f}; winner IS {w['is_sharpe']:.2f} / OOS {w['oos_sharpe']:.2f}.",
                method_name="5D Tournament", expected_chart_type="scatter")


def chart_tournament_sharpe_dist():
    """Histogram of OOS Sharpe across IS-valid combos, with the IS-selected winner and SPY."""
    tdf = pd.read_csv(os.path.join(RESULTS, f"tournament_results_{RUN_TAG}.csv"))
    w = _load_winner()
    valid = tdf[(tdf["valid"]) & (tdf["signal"] != "BENCHMARK")]
    bh_sharpe = float(tdf[tdf["signal"] == "BENCHMARK"].iloc[0]["oos_sharpe"])
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=valid["oos_sharpe"], nbinsx=50, marker_color=C_TARGET, opacity=0.7,
                               name=f"IS-valid combos ({len(valid)})"))
    fig.add_vline(x=w["oos_sharpe"], line_color=C_TERTIARY, line_width=2.5,
                  annotation_text=f"Winner: {w['oos_sharpe']:.2f}", annotation_font_size=10,
                  annotation_font_color=C_TERTIARY, annotation_position="top right")
    fig.add_vline(x=bh_sharpe, line_color=C_BENCHMARK, line_width=2, line_dash="dash",
                  annotation_text=f"SPY: {bh_sharpe:.2f}", annotation_font_size=10,
                  annotation_font_color=C_BENCHMARK, annotation_position="top left")
    pct_below = float((valid["oos_sharpe"] < w["oos_sharpe"]).mean() * 100)
    pct_above_bh = float((valid["oos_sharpe"] > bh_sharpe).mean() * 100)
    fig.update_layout(
        title=dict(text=f"OOS Sharpe of {len(valid)} IS-Valid Combos: Winner at {pct_below:.0f}th Percentile; {pct_above_bh:.0f}% Above SPY"),
        xaxis_title="Out-of-Sample Sharpe Ratio", yaxis_title="Count",
        template=TEMPLATE, height=450, barmode="overlay", margin=dict(r=180, b=80),
    )
    _note(fig, f"{len(tdf) - 1} combos scanned, {len(valid)} IS-valid. Median OOS Sharpe {valid['oos_sharpe'].median():.2f}.")
    _save_chart(fig, "tournament_sharpe_dist",
                narrative_note=f"Winner OOS {w['oos_sharpe']:.2f} sits at the {pct_below:.0f}th percentile of IS-valid combos; {pct_above_bh:.0f}% of combos exceed SPY {bh_sharpe:.2f}.",
                method_name="5D Tournament", expected_chart_type="histogram")


def chart_spread_history_annotated():
    """Full 25-year HY-IG spread with NBER shading + event annotations from Ray's CSV."""
    df = _load_master()
    evts = _load_events()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # HY-IG spread
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["hy_ig_spread_pct"],
            name="HY-IG OAS Spread (%)",
            line=dict(color=C_INDICATOR, width=1.5),
        ),
        secondary_y=False,
    )

    # SPY overlay
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["spy"],
            name="SPY ($)",
            line=dict(color=C_TARGET, width=1.2, dash="dot"),
        ),
        secondary_y=True,
    )

    _add_recessions(fig, df.index.min(), df.index.max())

    # Annotate top events from Ray's timeline (select key ones)
    key_event_dates = [
        "2001-09-11", "2008-09-15", "2009-03-09", "2020-03-23", "2022-06-16"
    ]
    for dt_str in key_event_dates:
        dt = pd.Timestamp(dt_str)
        if dt < df.index.min() or dt > df.index.max():
            continue
        row = evts[evts["date"] == dt]
        if len(row) == 0:
            continue
        label = str(row.iloc[0]["event"])[:35]
        idx = df.index.get_indexer([dt], method="nearest")[0]
        y_val = df["hy_ig_spread_pct"].iloc[idx]
        fig.add_annotation(
            x=dt, y=y_val, text=label, showarrow=True,
            arrowhead=2, arrowsize=0.7, ax=0, ay=-45,
            font=dict(size=8, color=EVENT_LINE),
            bgcolor="rgba(255,255,255,0.82)", borderpad=2,
        )

    fig.update_layout(
        title=dict(text="HY-IG Credit Spread History with Selected Events, 2000-2026"),
        template=TEMPLATE, hovermode="x unified", height=540,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    fig.update_yaxes(title_text="HY-IG OAS Spread (%)", secondary_y=False, autorange="reversed")
    fig.update_yaxes(title_text="SPY Price ($)", secondary_y=True)
    _note(fig, "Source: ICE BofA OAS via FRED; SPY via Yahoo Finance. Gray = NBER recessions. Events from Ray's timeline.")
    _save_chart(fig, "spread_history_annotated",
                narrative_note="Annotated HY-IG spread history (descriptive).",
                method_name="Spread History",
                expected_chart_type="dual_axis_line")


# ════════════════════════════════════════════════════════════════════════
# EVIDENCE EXTRA (3)
# ════════════════════════════════════════════════════════════════════════

def chart_quartile_returns():
    """SPY annualized returns by spread quartile (without regime conditioning)."""
    rdf = pd.read_csv(os.path.join(RESULTS, "regime_quartile_returns.csv"))
    rdf["ann_return_pct"] = rdf["ann_return"] * 100
    rdf["ann_vol_pct"]    = rdf["ann_vol"] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rdf["quartile"],
        y=rdf["ann_return_pct"],
        marker_color=C_Q[:len(rdf)],
        text=[f"{v:.1f}%" for v in rdf["ann_return_pct"]],
        textposition="outside", textfont=dict(size=11),
        name="Ann. Return (%)",
    ))
    # Add a vol overlay as scatter
    fig.add_trace(go.Scatter(
        x=rdf["quartile"], y=rdf["ann_vol_pct"],
        mode="markers+lines",
        marker=dict(size=10, color=C_INDICATOR),
        line=dict(color=C_INDICATOR, dash="dash", width=1.5),
        name="Ann. Vol (%)",
        yaxis="y2",
    ))

    fig.update_layout(
        title=dict(text="SPY Next-Month Return and Volatility by Month-End HY-IG Spread Quartile"),
        xaxis_title="HY-IG Spread Quartile",
        yaxis=dict(title="Annualized Return (%)", side="left"),
        yaxis2=dict(title="Annualized Vol (%)", side="right", overlaying="y"),
        template=TEMPLATE, height=450,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    _note(fig, "Forward (next-month) returns. Q1=tightest spread; Q4=widest. Bars: return (left); dashed: vol (right).")
    _save_chart(fig, "quartile_returns",
                narrative_note="Next-month SPY return/vol by month-end spread quartile (forward test).",
                method_name="Quartile Returns (raw)",
                expected_chart_type="bar")


def chart_returns_by_regime():
    """Boxplot / violin of SPY returns grouped by HMM regime."""
    df = _load_master()
    sig_df = _load_signals()

    spy_ret = df["spy_ret"] if "spy_ret" in df.columns else df["spy"].pct_change()
    prob_col = "hmm_2state_prob_stress"
    prob = sig_df[prob_col].reindex(df.index, method="ffill")
    calm_r   = spy_ret[(prob <= 0.5) & prob.notna()].dropna() * 100
    stress_r = spy_ret[prob > 0.5].dropna() * 100

    fig = go.Figure()
    fig.add_trace(go.Violin(
        y=calm_r.values,
        name="Calm (filtered prob ≤ 0.5)",
        box_visible=True,
        meanline_visible=True,
        fillcolor=f"rgba(0,158,115,0.3)",
        line_color=C_TERTIARY,
    ))
    fig.add_trace(go.Violin(
        y=stress_r.values,
        name="Stress (filtered prob > 0.5)",
        box_visible=True,
        meanline_visible=True,
        fillcolor=f"rgba(213,94,0,0.3)",
        line_color=C_INDICATOR,
    ))

    fig.update_layout(
        title=dict(text="Same-Day SPY Daily Returns by Causal HMM Regime"),
        xaxis_title="HMM Regime",
        yaxis_title="Daily SPY Return (%)",
        template=TEMPLATE, height=480, violinmode="group",
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=180, b=80),
    )
    _note(fig, "Daily SPY returns split by the same-day filtered HMM stress probability (concurrent, descriptive).")
    _save_chart(fig, "returns_by_regime",
                narrative_note="Concurrent daily SPY return distributions in the causal HMM calm vs stress states.",
                method_name="HMM Regime Distribution",
                expected_chart_type="violin")


def chart_correlation_heatmap():
    """Cross-asset correlation heatmap (HY-IG derived signals vs SPY forward returns)."""
    cdf = pd.read_csv(os.path.join(RESULTS, f"exploratory_{RUN_TAG}", "correlations.csv"))

    pivot = cdf.pivot_table(index="signal", columns="horizon", values="correlation", aggfunc="first")

    h_order = [c for c in ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d",
                            "spy_fwd_63d", "spy_fwd_126d", "spy_fwd_252d"]
               if c in pivot.columns]
    pivot = pivot[h_order]
    h_labels = [c.replace("spy_fwd_", "").upper() for c in h_order]
    s_labels = pivot.index.tolist()

    zvals = pivot.values
    text_annots = [[f"{v:.3f}" if not np.isnan(v) else "" for v in row] for row in zvals]

    fig = go.Figure(data=go.Heatmap(
        z=zvals, x=h_labels, y=s_labels,
        colorscale="RdBu_r", zmid=0, zmin=-0.40, zmax=0.40,
        text=text_annots,
        texttemplate="%{text}", textfont={"size": 9},
        colorbar=dict(title="Pearson r"),
    ))

    fig.update_layout(
        title=dict(text="Pearson r: HY-IG Signals vs SPY Forward Returns by Horizon"),
        xaxis_title="SPY Forward Return Horizon",
        yaxis_title="HY-IG Derived Signal",
        template=TEMPLATE, height=650, margin=dict(r=180, l=200, b=80),
    )
    _note(fig, "Daily data 2000-2026; overlapping forward windows. Blue = negative, red = positive (RdBu_r).")
    _save_chart(fig, "correlation_heatmap",
                narrative_note="Pearson r of HY-IG signals vs SPY forward returns (overlapping windows; iid p-values overstate significance).",
                method_name="Correlation Analysis",
                expected_chart_type="heatmap")


# ════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\nGenerating charts for pair: {PAIR_ID}")
    print(f"Output: {CHART_DIR}\n")

    # Story (4 + 3 zoom = 7)
    print("── Story Page ──────────────────────────────")
    chart_hero()
    chart_regime_stats()
    chart_history_zoom_dotcom()
    chart_history_zoom_gfc()
    chart_history_zoom_covid()

    # Evidence L1 (3)
    print("\n── Evidence Level 1 ────────────────────────")
    chart_correlations()
    chart_ccf()
    chart_granger_f_by_lag()

    # Evidence L2 (5)
    print("\n── Evidence Level 2 ────────────────────────")
    chart_hmm_regime_probs()
    chart_regime_quartile_returns()
    chart_transfer_entropy()
    chart_local_projections()
    chart_quantile_regression()

    # Strategy (4)
    print("\n── Strategy Page ───────────────────────────")
    chart_equity_curves()
    chart_drawdown()
    chart_drawdown_comparison()
    chart_walk_forward()

    # Confidence + Methodology (3)
    print("\n── Confidence + Methodology ────────────────")
    chart_tournament_scatter()
    chart_tournament_sharpe_dist()
    chart_spread_history_annotated()

    # Evidence Extra (3)
    print("\n── Evidence Extra ──────────────────────────")
    chart_quartile_returns()
    chart_returns_by_regime()
    chart_correlation_heatmap()

    # Summary
    charts = sorted(f for f in os.listdir(CHART_DIR) if f.endswith(".json") and "_meta" not in f)
    metas  = sorted(f for f in os.listdir(CHART_DIR) if f.endswith("_meta.json"))
    print(f"\n{'='*55}")
    print(f"Charts saved:  {len(charts)}/22")
    print(f"Sidecars saved: {len(metas)}/22")
    for c in charts:
        print(f"  {c}")
