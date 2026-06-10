#!/usr/bin/env python3
"""
Visualization Pipeline: gold_copper_xli (Mode 2 Phase 4, Vera hat)

Essential chart subset (11 charts):
  hero, signal_timeseries, equity_curves, drawdown,
  quartile_returns, regime_quartile_returns, correlation_heatmap,
  history_zoom_{gfc, china_2015, covid, rates_2022}

Each chart:
  - plotly JSON  -> output/charts/gold_copper_xli/plotly/<name>.json
  - sidecar JSON -> output/charts/gold_copper_xli/plotly/<name>_meta.json
  - perceptual PNG (kaleido) per VIZ-CV1
  - VIZ-DP1: dual-panel traces use xaxis=x/x2 + yaxis=y/y2 consistently
  - GATE-VIZ-NBER2: NBER shading only on recession-overlapping episodes
    (gfc, covid), absent on non-recession ones (china_2015, rates_2022)
"""

import os, json, time
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

PAIR_ID = "gold_copper_xli"
DATE_TAG = "20260526"
BASE = "/workspaces/aig-rlic-plus"
DATA = os.path.join(BASE, "data", f"{PAIR_ID}_daily_{DATE_TAG}.parquet")
RESULTS = os.path.join(BASE, "results", PAIR_ID)
OUTDIR = os.path.join(BASE, "output", "charts", PAIR_ID, "plotly")
os.makedirs(OUTDIR, exist_ok=True)

NBER = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]
NBER_FILL = "rgba(150,120,120,0.22)"

EPISODES = {
    "gfc":         ("2007-12-01", "2009-06-30", "GFC",            True),
    "china_2015":  ("2015-06-01", "2016-02-29", "China/EM Shock", False),
    "covid":       ("2020-02-01", "2020-12-31", "COVID Shock",    True),
    "rates_2022":  ("2022-01-01", "2022-12-31", "2022 Rates Shock", False),
}


def log(m): print(f"[viz] {m}", flush=True)


def save_chart(fig, name, palette_id, rules_applied, alignment_note):
    p = os.path.join(OUTDIR, f"{name}.json")
    pio.write_json(fig, p, pretty=False)
    meta = {
        "chart_name": name,
        "pair_id": PAIR_ID,
        "palette_id": palette_id,
        "rules_applied": rules_applied,
        "narrative_alignment_note": alignment_note,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "Lead Lesandro (Mode 2 maker — Vera hat)",
    }
    with open(p.replace(".json", "_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    # Perceptual PNG per VIZ-CV1
    try:
        png_path = os.path.join(OUTDIR, f"_perceptual_check_{name}.png")
        fig.write_image(png_path, width=900, height=540, scale=1)
    except Exception as e:
        log(f"  PNG fail for {name}: {e}")
    log(f"  wrote {name}")


def add_nber_shapes(fig, xref="x", y0=0, y1=1, yref="paper"):
    for s, e in NBER:
        fig.add_shape(type="rect", xref=xref, yref=yref,
                      x0=s, x1=e, y0=y0, y1=y1,
                      fillcolor=NBER_FILL, line=dict(width=0), layer="below")


def make_hero(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["gold_copper_ratio"],
                             name="Gold/Copper Ratio", yaxis="y",
                             line=dict(color="#b87333", width=1.4)))
    fig.add_trace(go.Scatter(x=df.index, y=df["xli"],
                             name="XLI ($)", yaxis="y2",
                             line=dict(color="#1f77b4", width=1.4)))
    add_nber_shapes(fig, yref="paper", y0=0, y1=1)
    fig.update_layout(
        title="Gold/Copper Ratio vs XLI — full sample with NBER recessions",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Gold/Copper Ratio", side="left"),
        yaxis2=dict(title="XLI ($)", side="right", overlaying="y"),
        hovermode="x unified", template="plotly_white", height=520,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
    )
    save_chart(fig, "hero", palette_id="dual_asset_v1",
               rules_applied=["VIZ-NBER1", "VIZ-IC1"],
               alignment_note="Hero chart: ratio (left axis) vs XLI (right axis), NBER recessions shaded. Aligned with Story page mechanism section.")


def make_signal_timeseries(df, summary):
    sig_col = summary["signal_column"]
    thr = summary["threshold_value"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[sig_col], name=sig_col,
                             line=dict(color="#b87333", width=1.0)))
    fig.add_hline(y=thr, line=dict(color="#d62728", dash="dash"),
                  annotation_text=f"Winner threshold = {thr:.3f}")
    add_nber_shapes(fig, yref="paper")
    fig.update_layout(title=f"Winning signal: {sig_col}",
                      xaxis=dict(title="Date"), yaxis=dict(title="Z-Score"),
                      template="plotly_white", height=420)
    save_chart(fig, "signal_timeseries", palette_id="single_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Signal time series with winner threshold dashed. Long when below the line.")


def make_equity_curves(signals_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=signals_df.index, y=signals_df["equity_curve"],
                             name="Strategy", line=dict(color="#2ca02c", width=1.6)))
    fig.add_trace(go.Scatter(x=signals_df.index, y=signals_df["buy_and_hold_equity"],
                             name="Buy & Hold (XLI)", line=dict(color="#888", width=1.2, dash="dot")))
    fig.update_layout(title="Equity curves: strategy vs buy-and-hold (XLI)",
                      xaxis=dict(title="Date"), yaxis=dict(title="Cumulative growth"),
                      template="plotly_white", height=460,
                      legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"))
    save_chart(fig, "equity_curves", palette_id="strategy_vs_bh_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Strategy vs buy-and-hold full sample. Strategy is from signals parquet.")


def make_drawdown(signals_df):
    eq = signals_df["equity_curve"].dropna()
    dd = (eq / eq.cummax() - 1) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd.index, y=dd, name="Strategy DD (%)",
                             fill="tozeroy", line=dict(color="#d62728", width=1.0)))
    fig.update_layout(title="Strategy drawdown (%)",
                      xaxis=dict(title="Date"), yaxis=dict(title="Drawdown (%)"),
                      template="plotly_white", height=380)
    save_chart(fig, "drawdown", palette_id="dd_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Strategy drawdown from peak equity. Used on Strategy page Performance tab.")


def make_quartile_returns():
    """VIZ-QR1 (2026-06-10): dual-panel — Annualized Sharpe (left) +
    Annualized Return % (right) by quartile, via the shared helper.
    Derivations from 63d forward-return stats (matches the KS-108 fix
    convention): sharpe = mean/std * sqrt(252/63); ann_return = mean * 4.
    """
    import sys as _sys
    _sys.path.insert(0, BASE)
    from scripts._quartile_chart import make_dual_panel_regime_chart
    import numpy as np

    df = pd.read_csv(os.path.join(RESULTS, "regime_quartile_returns.csv"))
    ann_factor = 252.0 / 63.0  # = 4
    sharpe = ((df["mean"] / df["std"]) * np.sqrt(ann_factor)).round(2).tolist()
    ann_return_pct = (df["mean"] * ann_factor * 100).round(1).tolist()
    label_map = {
        "Q1_low": "Q1<br>(Low ratio — risk-on)",
        "Q2": "Q2",
        "Q3": "Q3",
        "Q4_high": "Q4<br>(High ratio — risk-off)",
    }
    labels = [label_map.get(q, q) for q in df["quartile"]]

    fig = make_dual_panel_regime_chart(
        quartile_labels=labels,
        sharpe=sharpe,
        ann_return_pct=ann_return_pct,
        signal_label="Gold/Copper Z-Score",
        x_axis_title="Z-Score Quartile",
    )
    save_chart(fig, "quartile_returns", palette_id="quartile_v1",
               rules_applied=["VIZ-QR1", "VIZ-IC1"],
               alignment_note="VIZ-QR1 dual-panel (Sharpe + Ann Return) by z-score quartile via scripts/_quartile_chart.py. Derived from 63d fwd-return stats: sharpe=mean/std*2, ann_return=mean*4.")


def make_regime_quartile_returns():
    """Same data, different framing — explicit regime quartile labels."""
    df = pd.read_csv(os.path.join(RESULTS, "regime_quartile_returns.csv"))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["quartile"], y=df["mean_pct"], name="Mean",
                         marker_color="#b87333"))
    fig.add_trace(go.Bar(x=df["quartile"], y=df["median_pct"], name="Median",
                         marker_color="#1f77b4"))
    fig.update_layout(title="Regime quartile returns (mean vs median)",
                      xaxis=dict(title="Signal quartile"),
                      yaxis=dict(title="XLI 63d fwd return (%)"),
                      barmode="group", template="plotly_white", height=420,
                      legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"))
    save_chart(fig, "regime_quartile_returns", palette_id="quartile_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Mean vs median by quartile — robustness check on quartile_returns chart.")


def make_correlation_heatmap(df):
    cols = ["gold_copper_zscore_252d", "gold_copper_zscore_126d",
            "gold_copper_pctrank_504d", "gold_copper_roc_63d",
            "gold_copper_roc_126d",
            "xli_fwd_5d", "xli_fwd_21d", "xli_fwd_63d", "xli_fwd_126d"]
    sub = df[cols].dropna()
    corr = sub.corr().round(3)
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale="RdBu", zmid=0, zmin=-0.3, zmax=0.3,
        text=corr.values, texttemplate="%{text:.2f}", textfont=dict(size=10)))
    fig.update_layout(title="Correlation heatmap — signals vs XLI forward returns",
                      template="plotly_white", height=520,
                      xaxis=dict(tickangle=-30))
    save_chart(fig, "correlation_heatmap", palette_id="diverging_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Pearson correlation: each signal transform x each forward return horizon. Negative = countercyclical.")


def make_history_zoom(df, slug):
    start, end, label, has_nber = EPISODES[slug]
    sub = df.loc[start:end]

    # Dual-panel layout: top = ratio + xli, bottom = z-score
    # Per VIZ-DP1: top traces use xaxis=x/yaxis=y and yaxis=y2 (overlay).
    # Bottom panel traces use xaxis=x2/yaxis=y3.
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sub.index, y=sub["gold_copper_ratio"],
                             name="G/C Ratio", xaxis="x", yaxis="y",
                             line=dict(color="#b87333", width=1.4)))
    fig.add_trace(go.Scatter(x=sub.index, y=sub["xli"],
                             name="XLI ($)", xaxis="x", yaxis="y2",
                             line=dict(color="#1f77b4", width=1.4)))
    # Bottom panel — 126d z-score is the tournament winner's signal column
    # (per winner_summary.signal_column). KS-109 fix (2026-06-03): was 252d.
    fig.add_trace(go.Scatter(x=sub.index, y=sub["gold_copper_zscore_126d"],
                             name="126d Z-Score", xaxis="x2", yaxis="y3",
                             line=dict(color="#7f4a2e", width=1.2)))
    fig.add_hline(y=0, line=dict(color="#888", width=0.8, dash="dot"), xref="x2", yref="y3")

    # NBER shading per GATE-VIZ-NBER2: only on recession-overlapping episodes
    if has_nber:
        for s, e in NBER:
            s_ts, e_ts = pd.Timestamp(s), pd.Timestamp(e)
            if e_ts >= sub.index.min() and s_ts <= sub.index.max():
                fig.add_shape(type="rect", xref="x", yref="paper",
                              x0=s_ts, x1=e_ts, y0=0.45, y1=1.0,
                              fillcolor=NBER_FILL, line=dict(width=0), layer="below")
                fig.add_shape(type="rect", xref="x2", yref="paper",
                              x0=s_ts, x1=e_ts, y0=0.0, y1=0.42,
                              fillcolor=NBER_FILL, line=dict(width=0), layer="below")

    fig.update_layout(
        title=f"{label} ({start} -> {end})",
        xaxis=dict(domain=[0, 1], anchor="y", showticklabels=False),
        yaxis=dict(domain=[0.45, 1.0], title="Gold/Copper", anchor="x"),
        yaxis2=dict(domain=[0.45, 1.0], title="XLI ($)", anchor="x",
                    overlaying="y", side="right"),
        xaxis2=dict(domain=[0, 1], anchor="y3", title="Date"),
        yaxis3=dict(domain=[0, 0.42], title="126d Z-Score", anchor="x2"),
        template="plotly_white", height=520,
        legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"),
        showlegend=True,
    )
    save_chart(fig, f"history_zoom_{slug}", palette_id="dual_panel_v1",
               rules_applied=["VIZ-DP1", "VIZ-IC1"] + (["GATE-VIZ-NBER2"] if has_nber else []),
               alignment_note=f"HZE1 episode '{slug}'. {'NBER overlay applied (recession overlap).' if has_nber else 'No NBER overlay (episode does not overlap NBER recession).'} Aligned with Story page episode narrative.")


def main():
    t0 = time.time()
    log("Loading data + winner_summary")
    df = pd.read_parquet(DATA)
    with open(os.path.join(RESULTS, "winner_summary.json")) as f:
        summary = json.load(f)
    signals = pd.read_parquet(os.path.join(RESULTS, f"signals_{DATE_TAG}.parquet"))

    make_hero(df)
    make_signal_timeseries(df, summary)
    make_equity_curves(signals)
    make_drawdown(signals)
    make_quartile_returns()
    make_regime_quartile_returns()
    make_correlation_heatmap(df)
    for slug in EPISODES:
        make_history_zoom(df, slug)

    log(f"DONE in {time.time()-t0:.1f}s")
    log(f"  outputs in {OUTDIR}")


if __name__ == "__main__":
    main()
