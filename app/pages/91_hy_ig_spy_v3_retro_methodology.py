"""Page 91 — HY-IG × SPY v3 Retro | Methodology (experiment fork).

Thin wrapper per APP-PT1. Renders Ray's methodology narrative and the
ECON-FE1 condition table. Experiment fork — not a production pair.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from pair_configs.hy_ig_spy_v3_retro_config import (
    display_name,
    methodology_narrative,
    winner_summary,
)

st.set_page_config(
    page_title=f"{display_name} Methodology | AIG-RLIC+",
    page_icon="⚗️",
    layout="wide",
)

# ── PAIR TITLE (APP-TT1) ────────────────────────────────────────────────────
st.title(f"{display_name}")
st.subheader("Methodology")

# ── EXPERIMENT FORK BANNER ──────────────────────────────────────────────────
st.warning(
    "⚗️ EXPERIMENT FORK — not a production pair. "
    "Results are for comparison purposes only."
)
st.caption(
    f"Winner: {winner_summary['winner_signal']} / {winner_summary['winner_threshold']} / "
    f"{winner_summary['winner_strategy']} / L{winner_summary['lead_days']}  |  "
    f"Validation Sharpe: {winner_summary['val_sharpe']:.4f}  |  "
    f"Winner unchanged vs. original: {winner_summary['winner_changed_vs_original']}"
)

st.divider()

# ── ECON-OOS4 RETRO-APPLY CAVEAT ─────────────────────────────────────────────
st.info(
    "**ECON-OOS4 retro-apply caveat:** the winner was inherited from the original "
    "hy_ig_spy pipeline, not re-selected blind on the corrected data. "
    "This means the tournament selection was not prospectively blind on the "
    "corrected data, making this fork methodologically weaker than the rerun fork "
    "(90_hy_ig_spy_v3_rerun), even though the winner is identical in both."
)

st.divider()

# ── METHODOLOGY NARRATIVE (Ray) ──────────────────────────────────────────────
st.subheader("Methodology")
st.markdown(methodology_narrative)

st.divider()

# ── THREE-PERIOD SPLIT ────────────────────────────────────────────────────────
st.subheader("ECON-OOS4 Three-Period Split")
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
    "Winner inherited from original pipeline (retro-apply constraint). "
    "Holdout evaluated once, blind."
)

st.divider()

# ── ECON-FE1 CONDITIONS ───────────────────────────────────────────────────────
st.subheader("ECON-FE1 Final Exam Results")

conditions = [
    ("C01", "Holdout Sharpe > 0",                          True,  "1.6116",   "> 0.0"),
    ("C02", "Holdout Sharpe ≥ 0.30 (equity validity)",     True,  "1.6116",   "≥ 0.30"),
    ("C03", "Block bootstrap 2.5th pct > 0",               False, "−0.3455",  "> 0.0"),
    ("C04", "DSR p-value ≥ 0.05 (not over-fitted)",        False, "0.0000",   "≥ 0.05"),
    ("C05", "Excess ann. return vs B&H > 0",               False, "−5.1%",    "> 0%"),
    ("C06", "Max drawdown > −30%",                         True,  "−5.9%",    "> −30%"),
    ("C07", "Strategy max DD shallower than B&H",          True,  "+12.9 pp", "> 0"),
    ("C08", "Validation OOS Sharpe ≥ 0.30 (no collapse)",  True,  "1.2427",   "≥ 0.30"),
    ("C09", "Holdout N ≥ 200 observations",                True,  "252",      "≥ 200"),
    ("C10", "Sharpe degradation val→holdout ≤ 0.50",       True,  "−0.3689",  "≤ 0.50"),
]

header = "| ID | Description | Result | Value | Threshold |\n|---|---|---|---|---|\n"
rows = ""
for cid, desc, passed, value, threshold in conditions:
    badge = "✅ PASS" if passed else "❌ FAIL"
    rows += f"| {cid} | {desc} | {badge} | {value} | {threshold} |\n"
st.markdown(header + rows)

n_pass = sum(1 for _, _, p, _, _ in conditions if p)
st.info(f"**Summary:** {n_pass} / 10 conditions pass. Overall status: **needs_final_exam**")

st.divider()

# ── DATA SOURCES ──────────────────────────────────────────────────────────────
st.subheader("Data Sources")
st.markdown(
    """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| HY-IG Spread (HY leg) | FRED | BAMLH0A0HYM2EY | Daily |
| HY-IG Spread (IG leg) | FRED | BAMLC0A0CMEY | Daily |
| SPY (Target) | Yahoo Finance | SPY | Daily |
| NBER Recession Dates | FRED / NBER | USREC | Monthly |
"""
)
st.caption(
    "Signal S6_hmm_stress sourced from results/hy_ig_spy/signals_20260422.parquet "
    "(hmm_2state_prob_stress, 6,863 observations, full history). "
    "Threshold T4_hmm_0.5: fixed at 0.5 (not a data-derived percentile). "
    "Cost assumption: 5 bps one-way per trade."
)

st.divider()

# ── NAVIGATION ───────────────────────────────────────────────────────────────
col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
with col_b1: st.page_link("pages/91_hy_ig_spy_v3_retro_story.py", label="Story", icon="📖")
with col_b2: st.page_link("pages/91_hy_ig_spy_v3_retro_evidence.py", label="Evidence", icon="🔬")
with col_b3: st.page_link("pages/91_hy_ig_spy_v3_retro_strategy.py", label="Strategy", icon="⚙️")
with col_b4: st.markdown("**📐 Methodology**")
with col_b5: st.page_link("pages/90_hy_ig_spy_v3_rerun_story.py", label="← Rerun fork", icon="⚗️")
