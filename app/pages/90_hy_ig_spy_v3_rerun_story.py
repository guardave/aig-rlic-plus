"""
Page 90: hy_ig_spy_v3_rerun — Clean Rerun Experiment Fork Story
All values hardcoded from artifact files read on 2026-05-09.
"""

import streamlit as st

st.set_page_config(
    page_title="hy_ig_spy_v3_rerun | AIG-RLIC+",
    page_icon="⚗️",
    layout="wide",
)

# ── EXPERIMENT FORK BANNER ──────────────────────────────────────────────────
st.warning(
    "⚗️ EXPERIMENT FORK — Clean Rerun | "
    "This page is part of a controlled rerun-vs-retro comparison. "
    "Not a production pair."
)

# ── BREADCRUMB NAV ──────────────────────────────────────────────────────────
st.markdown(
    "**Pair comparison:** "
    "📄 You are here: `hy_ig_spy_v3_rerun` (Clean Rerun, page 90) "
    "· "
    "[→ Retro-Apply fork (page 91)](91_hy_ig_spy_v3_retro_story)",
    unsafe_allow_html=False,
)
st.divider()

# ── TITLE ───────────────────────────────────────────────────────────────────
st.title("hy_ig_spy_v3_rerun")
st.subheader(
    "HY-IG Spread → SPY  |  252-day z-score, rolling 75th-pct threshold, "
    "binary long/flat, no lag  |  Clean Rerun Fork"
)

# ── KPI METRIC CARDS ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Validation OOS Sharpe", "1.20", delta="1,638 trading days")
col2.metric("Holdout Sharpe", "0.85", delta="252 trading days")
col3.metric(
    "Final Exam Status",
    "needs_final_exam",
    delta="7 / 10 conditions pass",
    delta_color="off",
)

st.divider()

# ── WINNER RULE ─────────────────────────────────────────────────────────────
st.subheader("Winner Rule")
st.markdown(
    """
| Field | Value |
|---|---|
| Signal | `S2a_zscore_252d` — 252-day z-score of HY-IG spread |
| Threshold | `T2_rp75` — Rolling 75th percentile |
| Position type | `P1` — Binary long / flat |
| Lag | `L0` — Zero-day lag (same-day signal) |
| Direction | Countercyclical |
| Target symbol | SPY |
| Indicator | `hy_ig_spread_pct` |
| Cost assumption | 5 bps one-way per trade |
"""
)

st.divider()

# ── THREE-PERIOD SPLIT DESIGN ────────────────────────────────────────────────
st.subheader("Three-Period Split Design")
st.markdown(
    """
| Window | Start | End | N Trading Days |
|---|---|---|---|
| In-Sample (IS) | 2000-01-03 | 2018-10-03 | 4,893 |
| Validation OOS | 2018-10-04 | 2025-01-13 | 1,638 |
| Holdout (sealed) | 2025-01-14 | 2025-12-31 | 252 |
"""
)
st.caption(
    "Split follows the ECON-OOS4 three-period protocol. "
    "The holdout window was sealed during tournament selection and threshold "
    "tuning; it was unsealed only for the final exam."
)

st.divider()

# ── PLAIN ENGLISH NARRATIVE ──────────────────────────────────────────────────
st.subheader("Signal Mechanism")
st.markdown(
    """
The HY-IG spread measures the yield premium that high-yield (junk) bond issuers must pay above
investment-grade issuers. When credit markets grow fearful — as they do before and during equity
drawdowns — this spread widens, signalling elevated default risk and deteriorating risk appetite.
The winner rule exploits this relationship in a strictly rules-based, countercyclical way: each
day the 252-trading-day z-score of the HY-IG spread is computed and compared against its own
rolling 75th percentile (T2_rp75). When the z-score exceeds that threshold — indicating the
spread is elevated relative to its recent history — the strategy moves to cash (flat, zero equity
exposure). When the z-score is at or below the threshold, the strategy holds SPY in full. There
is no look-ahead: the signal fires at the close of the same day the z-score is observed (L0,
zero-day lag), with a one-way cost assumption of 5 bps per trade.
"""
)

st.subheader("Key Findings")
st.markdown(
    """
Over the 18-year in-sample period (2000-01-03 to 2018-10-03, 4,893 trading days), the rule was
selected from a tournament of 2,143 raw candidates (150 effective after correlation pruning). In
the validation out-of-sample window (2018-10-04 to 2025-01-13, 1,638 trading days), the strategy
produced a Sharpe ratio of **1.20** — a clean demonstration that the credit-to-equity
lead-indicator relationship persisted through trade wars, a global pandemic, and the 2022 rate
shock. The holdout period (2025-01-14 to 2025-12-31, 252 trading days) delivered a Sharpe of
**0.85** — positive and above the 0.30 validity floor, but with an annualised excess return of
−14.4% versus buy-and-hold SPY (5.2% vs 19.7%).

The final exam status is **needs_final_exam**: 7 of 10 ECON-FE1 conditions pass, but three fail
— C03 (block bootstrap 2.5th percentile dips to −1.19, below zero), C04 (deflated Sharpe ratio
p-value is effectively 0.00, flagging over-fit risk given the large raw trial count), and C05
(excess annual return is negative). The economic interpretation is straightforward: 2025 was a
strong bull year for U.S. equities; a defensive strategy that reduces equity exposure when credit
stress is elevated will mechanically lag a rising market. The strategy avoided the Q1 2025
drawdown (max drawdown −5.1% vs −18.8% for SPY) but gave back that cushion in foregone upside.
Whether this is a permanent regime shift or a transient bull-year penalty is the open question
the final exam is designed to resolve.
"""
)

st.divider()

# ── ECON-FE1 CONDITIONS TABLE ────────────────────────────────────────────────
st.subheader("ECON-FE1 Final Exam — All 10 Conditions")

conditions = [
    ("C01", "Holdout Sharpe > 0",                         True,  "0.846",    "> 0.0"),
    ("C02", "Holdout Sharpe ≥ 0.30 (equity validity)",    True,  "0.846",    "≥ 0.30"),
    ("C03", "Block bootstrap 2.5th pct > 0",              False, "−1.190",   "> 0.0"),
    ("C04", "DSR p-value ≥ 0.05 (not over-fitted)",       False, "0.000",    "≥ 0.05"),
    ("C05", "Excess ann. return vs B&H > 0",              False, "−14.4%",   "> 0%"),
    ("C06", "Max drawdown > −30%",                        True,  "−5.1%",    "> −30%"),
    ("C07", "Strategy max DD shallower than B&H",         True,  "+13.7 pp", "> 0"),
    ("C08", "Validation OOS Sharpe ≥ 0.30 (no collapse)", True,  "1.20",     "≥ 0.30"),
    ("C09", "Holdout N ≥ 200 observations",               True,  "251",      "≥ 200"),
    ("C10", "Sharpe degradation val→holdout ≤ 0.50",      True,  "0.354",    "≤ 0.50"),
]

header = "| ID | Description | Result | Value | Threshold |\n|---|---|---|---|---|\n"
rows = ""
for cid, desc, passed, value, threshold in conditions:
    badge = "✅ PASS" if passed else "❌ FAIL"
    rows += f"| {cid} | {desc} | {badge} | {value} | {threshold} |\n"

st.markdown(header + rows)

# Summary
n_pass = sum(1 for _, _, p, _, _ in conditions if p)
st.info(f"**Summary:** {n_pass} / 10 conditions pass. Overall status: **needs_final_exam**")

st.divider()

# ── ADDITIONAL METRICS ───────────────────────────────────────────────────────
st.subheader("Holdout Period Additional Metrics")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Holdout Ann. Return", "5.24%")
m2.metric("B&H Ann. Return", "19.69%")
m3.metric("Holdout Max Drawdown", "−5.1%")
m4.metric("B&H Max Drawdown", "−18.8%")

m5, m6, m7 = st.columns(3)
m5.metric("N Trials (raw)", "2,143")
m6.metric("N Trials (effective)", "150")
m7.metric("N Holdout Trades", "16")

st.divider()

# ── BREADCRUMB NAV (BOTTOM) ──────────────────────────────────────────────────
st.markdown(
    "**Pair comparison:** "
    "📄 You are here: `hy_ig_spy_v3_rerun` (Clean Rerun, page 90) "
    "· "
    "[→ Retro-Apply fork (page 91)](91_hy_ig_spy_v3_retro_story)"
)
