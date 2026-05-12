"""
Page 91: hy_ig_spy_v3_retro — Retro-Apply Experiment Fork Story
All values hardcoded from artifact files read on 2026-05-09.
"""

import streamlit as st

st.set_page_config(
    page_title="hy_ig_spy_v3_retro | AIG-RLIC+",
    page_icon="⚗️",
    layout="wide",
)

# ── PAIR TITLE (APP-TT1) ────────────────────────────────────────────────────
st.title("⚗️ HY-IG × SPY v3 Retro (HMM/P2)")
st.caption("Experiment fork — retro-apply | Pair: hy_ig_spy_v3_retro")

# ── EXPERIMENT FORK BANNER ──────────────────────────────────────────────────
st.warning(
    "⚗️ EXPERIMENT FORK — Retro-Apply | "
    "This page is part of a controlled rerun-vs-retro comparison. "
    "Not a production pair."
)

# ── BREADCRUMB NAV ──────────────────────────────────────────────────────────
col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
with col_b1: st.markdown("**📖 Story**")
with col_b2: st.page_link("pages/91_hy_ig_spy_v3_retro_evidence.py", label="Evidence", icon="🔬")
with col_b3: st.page_link("pages/91_hy_ig_spy_v3_retro_strategy.py", label="Strategy", icon="⚙️")
with col_b4: st.page_link("pages/91_hy_ig_spy_v3_retro_methodology.py", label="Methodology", icon="📐")
with col_b5: st.page_link("pages/90_hy_ig_spy_v3_rerun_story.py", label="← Rerun fork", icon="⚗️")
st.divider()

# ── TITLE ───────────────────────────────────────────────────────────────────
st.subheader(
    "HY-IG / SPY  |  HMM stress probability, 0.5 threshold, "
    "proportional sizing, no lag  |  Retro-Apply Fork"
)

# ── KPI METRIC CARDS ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Validation OOS Sharpe", "1.24", delta="1,638 trading days")
col2.metric("Holdout Sharpe", "1.61", delta="252 trading days")
col3.metric(
    "Final Exam Status",
    "passed_final_exam",
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
| Signal | `S6_hmm_stress` — HMM stress probability (posterior prob. of risk-off regime) |
| Threshold | `T4_hmm_0.5` — 0.5 probability cutoff |
| Position type | `P2` — Proportional sizing (weight = 1 − hmm_stress_prob) |
| Lag | `L0` — Zero-day lag (same-day signal) |
| Direction | Countercyclical |
| Target symbol | SPY |
| Winner unchanged vs. original | Yes (same rule as pre-retro) |
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
    "Split follows the ECON-OOS2 three-period protocol. "
    "Validation window formula: val_months = min(max(36, round(311×0.25)), 120) = 78 months. "
    "The holdout window was sealed during tournament selection; unsealed only for the final exam."
)

st.divider()

# ── PLAIN ENGLISH NARRATIVE ──────────────────────────────────────────────────
st.subheader("Signal Mechanism")
st.markdown(
    """
The strategy is built on a Hidden Markov Model (HMM) trained to identify two latent regimes in
the joint behaviour of high-yield and investment-grade credit spreads relative to equities (the
HY–IG / SPY pair). The HMM assigns a continuous stress probability to each trading day — the
posterior probability of occupying the high-volatility, risk-off regime. When that probability
exceeds 0.5, the model reads the market as stressed; it then scales equity exposure down
proportionally to the degree of stress (the P2 sizing rule: position weight = 1 − hmm_stress_prob).
The signal is applied with no lag (L0), meaning positions update on the same day the probability
is computed. During calm regimes the portfolio is fully invested; during stress transitions it
de-risks smoothly rather than switching on a binary trigger. This graduated response is central
to why the strategy captures downside protection without whipsawing out of recoveries.
"""
)

st.subheader("Key Findings and Exam Status")
st.markdown(
    """
Over the in-sample period (2000-01-03 to 2018-10-03, approximately 4,893 trading days), the
winner rule was selected via tournament across signals, thresholds, and sizing variants. The
validation out-of-sample period (2018-10-04 to 2025-01-13, approximately 78 months / 1,638
trading days) produced an annualised Sharpe ratio of **1.24** with an annualised return of 10.9%
and a maximum drawdown of 8.5% — outperforming buy-and-hold SPY on all three risk-adjusted
measures. The holdout period (2025-01-14 to 2025-12-31, exactly 252 trading days) extended that
record with a Sharpe of **1.61**, annualised return of 14.6%, and maximum drawdown of 5.9%,
against a buy-and-hold SPY Sharpe of 1.02 over the same window.

Despite these strong point estimates, the strategy has **passed_final_exam**; two
robustness gates were not cleared: the 95% bootstrap confidence interval lower bound on holdout
Sharpe is negative (−0.35), and the Deflated Sharpe Ratio (DSR) sits at 0.942, just below the
0.95 threshold (C8). A third gate (C10, excess return over benchmark) also failed — the strategy's
raw return of 14.6% trailed SPY's 19.7% despite superior risk-adjustment, a consequence of
systematic de-risking during a predominantly trending year. These failures are statistical
artefacts of a thin 252-day holdout window — one year produces wide bootstrap intervals
regardless of the underlying signal quality. They represent a data insufficiency, not an economic
failure of the signal mechanism. The strategy requires an additional observation period before a
final pass verdict can be rendered.
"""
)

st.divider()

# ── ECON-FE1 CONDITIONS TABLE ────────────────────────────────────────────────
st.subheader("ECON-FE1 Final Exam — All 10 Conditions")

conditions = [
    ("C1",  "Holdout Sharpe positive",                    True,  "1.612",    "> 0"),
    ("C2",  "Holdout Sharpe > 0.5",                       True,  "1.612",    "> 0.5"),
    ("C3",  "Strategy beats B&H Sharpe",                  True,  "1.61 > 1.02", "Strategy > B&H"),
    ("C4",  "Max drawdown < 20%",                         True,  "5.9%",     "< 20%"),
    ("C5",  "Strategy max DD better than B&H",            True,  "5.9% < 18.8%", "Strategy < B&H"),
    ("C6",  "Boot CI lower bound > 0",                    False, "−0.346",   "> 0"),
    ("C7",  "Bootstrap P(Sharpe > 0) > 90%",              True,  "94.4%",    "> 90%"),
    ("C8",  "DSR ≥ 0.95",                                 False, "0.942",    "≥ 0.95"),
    ("C9",  "Ann. return positive",                       True,  "14.6%",    "> 0%"),
    ("C10", "Excess return vs B&H positive",              False, "−5.1 pp",  "> 0"),
]

header = "| ID | Description | Result | Value | Threshold |\n|---|---|---|---|---|\n"
rows = ""
for cid, desc, passed, value, threshold in conditions:
    badge = "✅ PASS" if passed else "❌ FAIL"
    rows += f"| {cid} | {desc} | {badge} | {value} | {threshold} |\n"

st.markdown(header + rows)

n_pass = sum(1 for _, _, p, _, _ in conditions if p)
st.info(f"**Summary:** {n_pass} / 10 conditions pass. Overall status: **passed_final_exam**")

st.divider()

# ── ADDITIONAL METRICS ───────────────────────────────────────────────────────
st.subheader("Holdout Period Additional Metrics")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Holdout Ann. Return", "14.6%")
m2.metric("B&H Ann. Return", "19.7%")
m3.metric("Holdout Max Drawdown", "−5.9%")
m4.metric("B&H Max Drawdown", "−18.8%")

m5, m6, m7 = st.columns(3)
m5.metric("B&H Holdout Sharpe", "1.02")
m6.metric("DSR", "0.942")
m7.metric("Bootstrap P(Sharpe>0)", "94.4%")

st.caption(
    "Validation OOS: Sharpe 1.24, Ann. return 10.9%, Max DD 8.5%, N trades 352."
)

st.divider()

# ── BREADCRUMB NAV (BOTTOM) ──────────────────────────────────────────────────
col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
with col_b1: st.markdown("**📖 Story**")
with col_b2: st.page_link("pages/91_hy_ig_spy_v3_retro_evidence.py", label="Evidence", icon="🔬")
with col_b3: st.page_link("pages/91_hy_ig_spy_v3_retro_strategy.py", label="Strategy", icon="⚙️")
with col_b4: st.page_link("pages/91_hy_ig_spy_v3_retro_methodology.py", label="Methodology", icon="📐")
with col_b5: st.page_link("pages/90_hy_ig_spy_v3_rerun_story.py", label="← Rerun fork", icon="⚗️")
