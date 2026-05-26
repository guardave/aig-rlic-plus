#!/usr/bin/env python3
"""
Cross-Period Consistency: gold_copper_xli

Produces the 5 charts the Evidence template (ECON-CP1/CP2 + VIZ-CP1) expects:
  subperiod_sharpe       — strategy Sharpe in distinct historical sub-periods
  rolling_correlation    — 252d rolling Pearson corr(z_252d, xli_fwd_63d)
  structural_break       — Quandt-Andrews-style sup-F break-test scan
  rolling_sharpe_cp      — 252d rolling Sharpe of strategy returns
  rolling_granger        — rolling 504d Granger F-stat (signal -> return)

Each chart ships with plotly JSON + sidecar _meta.json + perceptual PNG,
following the Phase 4 pattern. Underlying CSVs are also persisted for
auditability.
"""

import os, json, time, warnings
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

warnings.filterwarnings("ignore")

PAIR_ID = "gold_copper_xli"
DATE_TAG = "20260526"
BASE = "/workspaces/aig-rlic-plus"
DATA = os.path.join(BASE, "data", f"{PAIR_ID}_daily_{DATE_TAG}.parquet")
RESULTS = os.path.join(BASE, "results", PAIR_ID)
OUTDIR = os.path.join(BASE, "output", "charts", PAIR_ID, "plotly")
SIGNAL_COL = "gold_copper_zscore_252d"


def log(m): print(f"[cp] {m}", flush=True)


def save_chart(fig, name, palette_id, rules_applied, alignment_note):
    p = os.path.join(OUTDIR, f"{name}.json")
    pio.write_json(fig, p, pretty=False)
    meta = {
        "chart_name": name, "pair_id": PAIR_ID,
        "palette_id": palette_id,
        "rules_applied": rules_applied,
        "narrative_alignment_note": alignment_note,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "Lead Lesandro (Mode 2 maker — Vera hat — Cross-Period)",
    }
    with open(p.replace(".json", "_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    try:
        fig.write_image(os.path.join(OUTDIR, f"_perceptual_check_{name}.png"),
                        width=900, height=540, scale=1)
    except Exception as e:
        log(f"  PNG fail for {name}: {e}")
    log(f"  wrote {name}")


# ------------------------------------------------------------------
def make_subperiod_sharpe(signals):
    """Strategy Sharpe in 5 distinct historical sub-periods."""
    log("subperiod_sharpe")
    ret = signals["strategy_return"].dropna()
    periods = [
        ("2000-2004", "2000-01-01", "2004-12-31"),
        ("2005-2009", "2005-01-01", "2009-12-31"),
        ("2010-2014", "2010-01-01", "2014-12-31"),
        ("2015-2019", "2015-01-01", "2019-12-31"),
        ("2020-2025", "2020-01-01", "2025-12-31"),
    ]
    rows = []
    for label, s, e in periods:
        r = ret.loc[s:e]
        if len(r) < 50: continue
        sharpe = (r.mean() * 252) / (r.std() * np.sqrt(252) + 1e-12)
        rows.append({"period": label, "sharpe": round(float(sharpe), 3), "n": int(len(r))})
    df = pd.DataFrame(rows)
    out_csv = os.path.join(RESULTS, "subperiod_sharpe.csv")
    df.to_csv(out_csv, index=False)
    colors = ["#2ca02c" if s >= 0 else "#d62728" for s in df["sharpe"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["period"], y=df["sharpe"],
                         marker_color=colors,
                         text=[f"{s:+.2f}" for s in df["sharpe"]],
                         textposition="outside"))
    fig.add_hline(y=0, line=dict(color="#888", width=0.6, dash="dot"))
    fig.update_layout(title="Strategy Sharpe by historical sub-period",
                      xaxis=dict(title="Period"),
                      yaxis=dict(title="Annualized Sharpe ratio"),
                      template="plotly_white", height=400)
    save_chart(fig, "subperiod_sharpe", palette_id="bar_v1",
               rules_applied=["VIZ-CP1", "VIZ-IC1"],
               alignment_note="Strategy Sharpe in 5 sub-periods. Consistent positive bars across all periods = robust signal; vanishing in one era = fragile.")


def make_rolling_correlation(df):
    log("rolling_correlation")
    sub = df[[SIGNAL_COL, "xli_fwd_63d"]].dropna()
    roll = sub[SIGNAL_COL].rolling(252).corr(sub["xli_fwd_63d"])
    out_csv = os.path.join(RESULTS, f"rolling_correlation_{PAIR_ID}.csv")
    roll.dropna().rename("rolling_corr_252d").to_csv(out_csv)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll.index, y=roll, name="252d rolling Pearson",
                             line=dict(color="#1f77b4", width=1.2)))
    fig.add_hline(y=0, line=dict(color="#888", width=0.6, dash="dot"))
    fig.add_vline(x=pd.Timestamp("2020-01-01"), line=dict(color="#888", width=0.6, dash="dash"))
    fig.add_annotation(x=pd.Timestamp("2020-01-01"), y=1, yref="paper",
                       text="OOS start", showarrow=False,
                       xanchor="left", yanchor="top",
                       font=dict(size=10, color="#666"))
    fig.update_layout(title="Rolling 252d correlation: G/C z-score vs XLI 63d fwd return",
                      xaxis=dict(title="Date"),
                      yaxis=dict(title="Pearson correlation"),
                      template="plotly_white", height=420)
    save_chart(fig, "rolling_correlation", palette_id="single_v1",
               rules_applied=["VIZ-CP1", "VIZ-IC1"],
               alignment_note="Time-varying linear correlation. A flat stable line = relationship not regime-dependent; large swings = regime-conditional (consistent with our QR finding).")


def make_structural_break(df):
    """Quandt-Andrews-style sup-F break test (manual implementation).
    Slope of xli_fwd_63d on z-score, recursively re-fit; report breakpoint
    candidate dates with biggest F-stat shift."""
    log("structural_break")
    sub = df[[SIGNAL_COL, "xli_fwd_63d"]].dropna().reset_index()
    n = len(sub)
    # Trim 15% each side
    lo, hi = int(n * 0.15), int(n * 0.85)
    rss_full = ((sub["xli_fwd_63d"] - sub["xli_fwd_63d"].mean()) ** 2).sum()
    f_stats = []
    for k in range(lo, hi, max(1, (hi - lo) // 300)):
        a = sub.iloc[:k]
        b = sub.iloc[k:]
        try:
            sa = np.polyfit(a[SIGNAL_COL], a["xli_fwd_63d"], 1)
            sb = np.polyfit(b[SIGNAL_COL], b["xli_fwd_63d"], 1)
            ra = (a["xli_fwd_63d"] - (sa[0] * a[SIGNAL_COL] + sa[1])) ** 2
            rb = (b["xli_fwd_63d"] - (sb[0] * b[SIGNAL_COL] + sb[1])) ** 2
            rss_break = ra.sum() + rb.sum()
            f = ((rss_full - rss_break) / 2) / (rss_break / (n - 4))
            f_stats.append({"date": sub["date"].iloc[k], "f_stat": float(f)})
        except Exception:
            pass
    fdf = pd.DataFrame(f_stats)
    # 5% critical value approx (Andrews 1993) ≈ 8.85 for trimming π=.15
    crit = 8.85
    sup_f_row = fdf.loc[fdf["f_stat"].idxmax()] if len(fdf) else None
    out_json = os.path.join(RESULTS, f"structural_break_{PAIR_ID}.json")
    payload = {
        "method": "Quandt-Andrews sup-F (linear slope, 15% trim)",
        "n_obs": n,
        "trim_lo": lo, "trim_hi": hi,
        "critical_value_5pct": crit,
        "sup_f_stat": float(sup_f_row["f_stat"]) if sup_f_row is not None else None,
        "sup_f_date": str(sup_f_row["date"].date()) if sup_f_row is not None else None,
        "break_significant_5pct": bool(sup_f_row is not None and sup_f_row["f_stat"] > crit),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(out_json, "w") as f:
        json.dump(payload, f, indent=2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["f_stat"],
                             name="F-statistic", line=dict(color="#b87333", width=1.4)))
    fig.add_hline(y=crit, line=dict(color="#d62728", dash="dash"),
                  annotation_text=f"5% critical value = {crit}")
    if sup_f_row is not None:
        fig.add_vline(x=sup_f_row["date"], line=dict(color="#2ca02c", dash="dot"))
        fig.add_annotation(x=sup_f_row["date"], y=1, yref="paper",
                           text=f"sup-F candidate = {sup_f_row['date'].date()}",
                           showarrow=False, xanchor="left", yanchor="top",
                           font=dict(size=10, color="#2ca02c"))
    fig.update_layout(
        title=("Structural break scan (Quandt-Andrews sup-F): "
               f"max F = {payload['sup_f_stat']:.2f}, "
               f"{'SIGNIFICANT' if payload['break_significant_5pct'] else 'NOT significant'}"),
        xaxis=dict(title="Candidate break date"),
        yaxis=dict(title="F-statistic"),
        template="plotly_white", height=420)
    save_chart(fig, "structural_break", palette_id="single_v1",
               rules_applied=["VIZ-CP1", "VIZ-IC1"],
               alignment_note=f"Sup-F break scan with Andrews 1993 critical value. Clean = parameter-stable relationship.")


def make_rolling_sharpe_cp(signals):
    log("rolling_sharpe_cp")
    ret = signals["strategy_return"].dropna()
    bh = signals["buy_and_hold_equity"].pct_change().dropna()
    roll_s = (ret.rolling(504).mean() * 252) / (ret.rolling(504).std() * np.sqrt(252) + 1e-12)
    roll_b = (bh.rolling(504).mean() * 252) / (bh.rolling(504).std() * np.sqrt(252) + 1e-12)
    out_csv = os.path.join(RESULTS, f"rolling_sharpe_{PAIR_ID}.csv")
    pd.DataFrame({"strategy": roll_s, "buy_and_hold": roll_b}).dropna().to_csv(out_csv)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_s.index, y=roll_s, name="Strategy",
                             line=dict(color="#2ca02c", width=1.4)))
    fig.add_trace(go.Scatter(x=roll_b.index, y=roll_b, name="Buy & Hold (XLI)",
                             line=dict(color="#888", width=1.2, dash="dot")))
    fig.add_hline(y=0, line=dict(color="#888", width=0.6, dash="dot"))
    fig.add_vline(x=pd.Timestamp("2020-01-01"), line=dict(color="#888", width=0.6, dash="dash"))
    fig.add_annotation(x=pd.Timestamp("2020-01-01"), y=1, yref="paper",
                       text="OOS start", showarrow=False,
                       xanchor="left", yanchor="top",
                       font=dict(size=10, color="#666"))
    fig.update_layout(title="Rolling 504d (~2y) Sharpe: strategy vs buy-and-hold",
                      xaxis=dict(title="Date"), yaxis=dict(title="Sharpe ratio"),
                      template="plotly_white", height=420,
                      legend=dict(orientation="h", y=-0.15))
    save_chart(fig, "rolling_sharpe_cp", palette_id="dual_v1",
               rules_applied=["VIZ-CP1", "VIZ-IC1"],
               alignment_note="2-year rolling Sharpe. Strategy line consistently above zero (and above B&H) = strategy persists across regimes.")


def make_rolling_granger(df):
    log("rolling_granger")
    from statsmodels.tsa.stattools import grangercausalitytests
    sub = df[[SIGNAL_COL, "xli_ret"]].dropna()
    window = 504
    rows = []
    # 504-day rolling, step 21
    for i in range(window, len(sub), 21):
        seg = sub.iloc[i - window: i]
        try:
            res = grangercausalitytests(seg[["xli_ret", SIGNAL_COL]],
                                        maxlag=5, verbose=False)
            f = res[5][0]["ssr_ftest"][0]
            rows.append({"date": seg.index[-1], "f_stat": float(f)})
        except Exception:
            pass
    gdf = pd.DataFrame(rows)
    out_csv = os.path.join(RESULTS, f"rolling_granger_{PAIR_ID}.csv")
    gdf.to_csv(out_csv, index=False)
    # 5% critical for F(5, ~500) ≈ 2.23
    crit = 2.23
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gdf["date"], y=gdf["f_stat"],
                             name="Rolling 504d Granger F(5,~500)",
                             line=dict(color="#b87333", width=1.4)))
    fig.add_hline(y=crit, line=dict(color="#d62728", dash="dash"),
                  annotation_text=f"5% critical value ≈ {crit}")
    fig.add_vline(x=pd.Timestamp("2020-01-01"), line=dict(color="#888", width=0.6, dash="dash"))
    fig.add_annotation(x=pd.Timestamp("2020-01-01"), y=1, yref="paper",
                       text="OOS start", showarrow=False,
                       xanchor="left", yanchor="top",
                       font=dict(size=10, color="#666"))
    fig.update_layout(title="Rolling Granger F-statistic: G/C z-score -> XLI return",
                      xaxis=dict(title="Window end date"),
                      yaxis=dict(title="F-statistic (5 lags)"),
                      template="plotly_white", height=420)
    save_chart(fig, "rolling_granger", palette_id="single_v1",
               rules_applied=["VIZ-CP1", "VIZ-IC1"],
               alignment_note="Rolling Granger F. Persistent values above the 5% critical = predictive content is not a sample artefact.")


def main():
    t0 = time.time()
    df = pd.read_parquet(DATA)
    signals = pd.read_parquet(os.path.join(RESULTS, f"signals_{DATE_TAG}.parquet"))
    make_subperiod_sharpe(signals)
    make_rolling_correlation(df)
    make_structural_break(df)
    make_rolling_sharpe_cp(signals)
    make_rolling_granger(df)
    log(f"DONE in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
