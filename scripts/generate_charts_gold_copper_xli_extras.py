#!/usr/bin/env python3
"""
Visualization Extras: gold_copper_xli (Mode 2 Phase 4.5, Vera hat ext)

Generates the 11 charts that Phase 4 deferred:
  From existing Phase-3 artifacts (6):
    granger_f_by_lag, walk_forward, drawdown_comparison,
    tournament_sharpe_dist, returns_by_regime, spread_history_annotated
  From new Phase-3.5 econometrics (5):
    hmm_regime_probs, local_projections, quantile_regression,
    transfer_entropy, ccf_prewhitened

Each chart ships with plotly JSON + sidecar _meta.json + perceptual PNG.
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

NBER = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]
NBER_FILL = "rgba(150,120,120,0.22)"


def log(m): print(f"[viz_ext] {m}", flush=True)


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
        "generated_by": "Lead Lesandro (Mode 2 maker — Vera hat ext)",
    }
    with open(p.replace(".json", "_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    try:
        fig.write_image(os.path.join(OUTDIR, f"_perceptual_check_{name}.png"),
                        width=900, height=540, scale=1)
    except Exception as e:
        log(f"  PNG fail for {name}: {e}")
    log(f"  wrote {name}")


def add_nber_shapes(fig, yref="paper", y0=0, y1=1):
    for s, e in NBER:
        fig.add_shape(type="rect", xref="x", yref=yref,
                      x0=s, x1=e, y0=y0, y1=y1,
                      fillcolor=NBER_FILL, line=dict(width=0), layer="below")


# ------------------------------------------------------------------
# From existing Phase-3 artifacts (6 trivial)
# ------------------------------------------------------------------
def make_granger_f_by_lag():
    df = pd.read_csv(os.path.join(RESULTS, "granger_by_lag.csv"))
    colors = ["#2ca02c" if s else "#888" for s in df["significant_5pct"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["lag"].astype(str), y=df["f_stat"],
                         marker_color=colors,
                         text=[f"p={p:.3f}" for p in df["p_value"]],
                         textposition="outside"))
    fig.add_hline(y=df["f_stat"].iloc[0] * 0 + 3.84, line=dict(color="#888", dash="dot"),
                  annotation_text="F crit. (~3.84, p=0.05)")
    fig.update_layout(title="Granger F-statistic by lag (gold/copper -> XLI return)",
                      xaxis=dict(title="Lag (trading days)"),
                      yaxis=dict(title="F-statistic"),
                      template="plotly_white", height=380)
    save_chart(fig, "granger_f_by_lag", palette_id="bar_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Bar chart of Granger F by lag; green = significant at 5%. Companion to granger_by_lag.csv.")


def make_walk_forward():
    sig = pd.read_parquet(os.path.join(RESULTS, f"signals_{DATE_TAG}.parquet"))
    sub = sig.loc["2020-01-01":]
    # Rolling 252d Sharpe of strategy return in OOS
    ret = sub["strategy_return"].fillna(0)
    roll_mean = ret.rolling(252).mean() * 252
    roll_std = ret.rolling(252).std() * np.sqrt(252)
    roll_sharpe = roll_mean / (roll_std + 1e-12)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_sharpe.index, y=roll_sharpe,
                             name="Strategy 252d rolling Sharpe (OOS)",
                             line=dict(color="#2ca02c", width=1.4)))
    fig.add_hline(y=1.27, line=dict(color="#1f77b4", dash="dash"),
                  annotation_text="Reported OOS Sharpe = 1.27")
    fig.add_hline(y=0, line=dict(color="#888", width=0.6, dash="dot"))
    fig.update_layout(title="Walk-forward: rolling 252d Sharpe (OOS 2020-2025)",
                      xaxis=dict(title="Date"),
                      yaxis=dict(title="Annualized Sharpe ratio"),
                      template="plotly_white", height=380)
    save_chart(fig, "walk_forward", palette_id="walk_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Rolling 1y Sharpe over OOS to inspect stability of the 1.27 headline number.")


def make_drawdown_comparison():
    sig = pd.read_parquet(os.path.join(RESULTS, f"signals_{DATE_TAG}.parquet"))
    eq = sig["equity_curve"].dropna()
    bh = sig["buy_and_hold_equity"].dropna()
    dd_s = ((eq / eq.cummax()) - 1) * 100
    dd_b = ((bh / bh.cummax()) - 1) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd_s.index, y=dd_s, name="Strategy",
                             line=dict(color="#2ca02c", width=1.2)))
    fig.add_trace(go.Scatter(x=dd_b.index, y=dd_b, name="Buy & Hold (XLI)",
                             line=dict(color="#888", width=1.2, dash="dot")))
    fig.update_layout(title="Drawdown comparison: strategy vs buy-and-hold (XLI)",
                      xaxis=dict(title="Date"),
                      yaxis=dict(title="Drawdown (%)"),
                      template="plotly_white", height=420,
                      legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"))
    save_chart(fig, "drawdown_comparison", palette_id="dd_compare_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Strategy vs B&H drawdown — visualizes the -8.2% strategy max DD vs deeper B&H drawdowns.")


def make_tournament_sharpe_dist():
    t = pd.read_csv(os.path.join(RESULTS, f"tournament_results_{DATE_TAG}.csv"))
    valid = t[t["valid"]]
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=valid["oos_sharpe"], nbinsx=20,
                               marker_color="#b87333",
                               name="Valid combos"))
    fig.add_vline(x=1.273, line=dict(color="#2ca02c", dash="dash"),
                  annotation_text="Winner = 1.27")
    fig.update_layout(title="Tournament OOS Sharpe distribution (60 valid combos)",
                      xaxis=dict(title="OOS Sharpe"),
                      yaxis=dict(title="Count"),
                      template="plotly_white", height=380)
    save_chart(fig, "tournament_sharpe_dist", palette_id="hist_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Distribution of OOS Sharpe across valid tournament combos; winner marked.")


def make_returns_by_regime():
    """XLI daily-return distribution by HMM regime."""
    sig = pd.read_parquet(os.path.join(RESULTS, f"signals_{DATE_TAG}.parquet"))
    hmm = pd.read_csv(os.path.join(RESULTS, "hmm_regime_probs.csv"), index_col=0,
                      parse_dates=True)
    df = pd.read_parquet(DATA)[["xli_ret"]]
    join = df.join(hmm[["viterbi_state"]], how="inner").dropna()
    fig = go.Figure()
    for s, label, color in [(0, "Regime 0 (stress)", "#d62728"),
                             (1, "Regime 1 (calm)", "#2ca02c")]:
        rets = join.loc[join["viterbi_state"] == s, "xli_ret"] * 100
        fig.add_trace(go.Box(y=rets, name=label, marker_color=color,
                              boxmean="sd"))
    fig.update_layout(title="XLI daily returns by HMM regime",
                      yaxis=dict(title="Daily return (%)"),
                      template="plotly_white", height=420,
                      legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"))
    save_chart(fig, "returns_by_regime", palette_id="box_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Box of XLI daily returns split by HMM Viterbi state — does stress regime have wider/lower returns?")


def make_spread_history_annotated(df):
    """Full-sample ratio with 4 HZE1 episodes annotated as bands."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["gold_copper_ratio"],
                             name="Gold/Copper Ratio",
                             line=dict(color="#b87333", width=1.2)))
    EPISODES = {
        "gfc":         ("2007-12-01", "2009-06-30", "GFC",        "#d62728"),
        "china_2015":  ("2015-06-01", "2016-02-29", "China 2015", "#e8a345"),
        "covid":       ("2020-02-01", "2020-12-31", "COVID",      "#d62728"),
        "rates_2022":  ("2022-01-01", "2022-12-31", "Rates 2022", "#8a2be2"),
    }
    for slug, (s, e, label, color) in EPISODES.items():
        fig.add_shape(type="rect", xref="x", yref="paper",
                      x0=s, x1=e, y0=0, y1=1,
                      fillcolor=color, opacity=0.12, line=dict(width=0),
                      layer="below")
        fig.add_annotation(x=s, y=1.0, xref="x", yref="paper",
                           text=label, showarrow=False,
                           font=dict(size=10, color="#333"),
                           xanchor="left", yanchor="top")
    fig.update_layout(title="Gold/Copper ratio with HZE1 episodes annotated",
                      xaxis=dict(title="Date"),
                      yaxis=dict(title="Gold/Copper Ratio"),
                      template="plotly_white", height=420)
    save_chart(fig, "spread_history_annotated", palette_id="annotated_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Ratio time series with 4 HZE1 episodes overlaid — orientation chart.")


# ------------------------------------------------------------------
# From new Phase-3.5 econometrics (5)
# ------------------------------------------------------------------
def make_hmm_regime_probs():
    hmm = pd.read_csv(os.path.join(RESULTS, "hmm_regime_probs.csv"),
                      index_col=0, parse_dates=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hmm.index, y=hmm["p_stress"],
                             name="P(stress regime)",
                             line=dict(color="#d62728", width=1.0),
                             fill="tozeroy", fillcolor="rgba(214,39,40,0.15)"))
    add_nber_shapes(fig, yref="paper")
    fig.update_layout(title="HMM 2-state regime: probability of stress state",
                      xaxis=dict(title="Date"),
                      yaxis=dict(title="P(stress)", range=[0, 1.05]),
                      template="plotly_white", height=380)
    save_chart(fig, "hmm_regime_probs", palette_id="prob_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="HMM stress-state probability over time. NBER recessions shaded — visual cross-check that the inferred stress regime aligns with documented crises.")


def make_local_projections():
    lp = pd.read_csv(os.path.join(RESULTS, "local_projections.csv"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lp["horizon_days"], y=lp["beta_pct"],
                             name="LP beta (% per signal SD)",
                             line=dict(color="#1f77b4", width=2),
                             mode="lines+markers"))
    fig.add_trace(go.Scatter(x=lp["horizon_days"], y=lp["ci_high_pct"],
                             line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=lp["horizon_days"], y=lp["ci_low_pct"],
                             line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(31,119,180,0.18)",
                             name="95% CI (HAC)"))
    fig.add_hline(y=0, line=dict(color="#888", width=0.8, dash="dot"))
    fig.update_layout(title="Local projections: cumulative XLI response to +1 SD signal shock",
                      xaxis=dict(title="Horizon (trading days)"),
                      yaxis=dict(title="Cumulative XLI return (%)"),
                      template="plotly_white", height=420,
                      legend=dict(orientation="v", x=1.08, xanchor="left", y=1, yanchor="top"))
    save_chart(fig, "local_projections", palette_id="lp_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Jordà local projections with HAC standard errors. Negative beta = countercyclical response. CI from local_projections.csv.")


def make_quantile_regression():
    qr = pd.read_csv(os.path.join(RESULTS, "quantile_regression.csv"))
    colors = ["#d62728" if q < 0.5 else ("#888" if q == 0.5 else "#2ca02c")
              for q in qr["quantile"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[f"q={q:.2f}" for q in qr["quantile"]], y=qr["beta_pct"],
                         marker_color=colors,
                         text=[f"t={t:+.1f}" for t in qr["t_stat"]],
                         textposition="outside"))
    fig.add_hline(y=0, line=dict(color="#888", width=0.8, dash="dot"))
    fig.update_layout(title="Quantile regression: signal beta on XLI 63d fwd return by quantile",
                      xaxis=dict(title="Quantile of XLI 63d return"),
                      yaxis=dict(title="Beta (% per signal SD)"),
                      template="plotly_white", height=420)
    save_chart(fig, "quantile_regression", palette_id="qr_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="QR betas by quantile. Strong negative at lower tail (q=0.05/0.10) = signal predicts crash risk. Strong positive at upper tail = signal also predicts upside variance — classic asymmetric risk/'lives in the tails'.")


def make_transfer_entropy():
    with open(os.path.join(RESULTS, "transfer_entropy.json")) as f:
        te = json.load(f)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["TE(signal → return)", "TE(return → signal)"],
        y=[te["te_signal_to_return"], te["te_return_to_signal"]],
        marker_color=["#2ca02c", "#888"],
        text=[f"{te['te_signal_to_return']:.4f}",
              f"{te['te_return_to_signal']:.4f}"],
        textposition="outside",
    ))
    null_hi = te["null_ci_95_via_shuffle"][1]
    fig.add_hline(y=null_hi, line=dict(color="#d62728", dash="dash"),
                  annotation_text=f"95% null CI upper = {null_hi:.4f}")
    fig.update_layout(title=f"Transfer entropy (binned, N=4) — signal vs XLI return  "
                            f"(p_emp = {te['p_value_empirical']:.3f})",
                      yaxis=dict(title="Transfer entropy (bits)"),
                      template="plotly_white", height=380)
    save_chart(fig, "transfer_entropy", palette_id="te_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note="Bidirectional TE bars with shuffle null CI overlay. Signal-to-return well above null = significant non-linear lead-lag.")


def make_ccf_prewhitened(df):
    """Cross-correlation of signal residuals vs return residuals after AR(1) pre-whitening."""
    sub = df[["gold_copper_zscore_252d", "xli_ret"]].dropna()
    sub = sub.loc["2000-01-01":"2019-12-31"]  # IS
    # AR(1) pre-whitening
    def prewhiten(s):
        x = s.values
        a = np.polyfit(x[:-1], x[1:], 1)[0]
        return x[1:] - a * x[:-1]
    x_pw = prewhiten(sub["gold_copper_zscore_252d"])
    y_pw = prewhiten(sub["xli_ret"])
    n = min(len(x_pw), len(y_pw))
    x_pw, y_pw = x_pw[-n:], y_pw[-n:]
    lags = np.arange(-30, 31)
    ccf = []
    for k in lags:
        if k < 0:
            r = np.corrcoef(x_pw[:k], y_pw[-k:])[0, 1]
        elif k > 0:
            r = np.corrcoef(x_pw[k:], y_pw[:-k])[0, 1]
        else:
            r = np.corrcoef(x_pw, y_pw)[0, 1]
        ccf.append(r)
    ccf = np.array(ccf)
    ci = 1.96 / np.sqrt(n)
    colors = ["#d62728" if abs(c) > ci else "#888" for c in ccf]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=lags, y=ccf, marker_color=colors,
                         name="CCF (pre-whitened)"))
    fig.add_hline(y=ci, line=dict(color="#888", dash="dot"),
                  annotation_text=f"+95% CI ≈ +{ci:.3f}")
    fig.add_hline(y=-ci, line=dict(color="#888", dash="dot"),
                  annotation_text=f"-95% CI ≈ -{ci:.3f}")
    fig.update_layout(title="Pre-whitened cross-correlation: signal vs XLI return",
                      xaxis=dict(title="Lag (signal leads at positive lag)"),
                      yaxis=dict(title="Cross-correlation"),
                      template="plotly_white", height=380)
    save_chart(fig, "ccf_prewhitened", palette_id="ccf_v1",
               rules_applied=["VIZ-IC1"],
               alignment_note=f"AR(1) pre-whitened CCF, IS only (2000-2019). Red bars exceed ±{ci:.3f} 95% CI. Positive lag = signal leads return.")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    t0 = time.time()
    df = pd.read_parquet(DATA)
    log("trivial-completable from existing artifacts:")
    make_granger_f_by_lag()
    make_walk_forward()
    make_drawdown_comparison()
    make_tournament_sharpe_dist()
    make_returns_by_regime()
    make_spread_history_annotated(df)
    log("from new Phase-3.5 econometrics:")
    make_hmm_regime_probs()
    make_local_projections()
    make_quantile_regression()
    make_transfer_entropy()
    make_ccf_prewhitened(df)
    log(f"DONE in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
