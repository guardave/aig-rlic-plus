"""Page 90 — HY-IG × SPY v3 Rerun | Methodology (experiment fork).

Thin wrapper per APP-PT1. Renders Ray's methodology narrative and the
ECON-FE1 condition table. Experiment fork — not a production pair.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from pair_configs.hy_ig_spy_v3_rerun_config import (
    display_name,
    methodology_narrative,
    winner_summary,
)

st.set_page_config(
    page_title=f"{display_name} Methodology | AIG-RLIC+",
    page_icon="⚗️",
    layout="wide",
)

# ── EXPERIMENT FORK BANNER ──────────────────────────────────────────────────
st.warning(
    "⚗️ EXPERIMENT FORK — not a production pair. "
    "Results are for comparison purposes only."
)

st.title(f"Methodology — {display_name}")
st.caption(
    f"Winner: {winner_summary['signal_code']} / {winner_summary['threshold_code']} / "
    f"{winner_summary['strategy_code']} / L{winner_summary['lead_days']}  |  "
    f"Validation Sharpe: {winner_summary['val_oos_sharpe']:.2f}  |  "
    f"Holdout Sharpe: {winner_summary['holdout_sharpe']:.4f}"
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
    "Winner selected on validation Sharpe; holdout evaluated once, blind. "
    "No re-fitting after the in-sample period."
)

st.divider()

# ── ECON-FE1 CONDITIONS ───────────────────────────────────────────────────────
st.subheader("ECON-FE1 Final Exam Results")

conditions = [
    ("C01", "Holdout Sharpe > 0",                          True,  "0.8459",   "> 0.0"),
    ("C02", "Holdout Sharpe ≥ 0.30 (equity validity)",     True,  "0.8459",   "≥ 0.30"),
    ("C03", "Block bootstrap 2.5th pct > 0",               False, "−1.1895",  "> 0.0"),
    ("C04", "DSR p-value ≥ 0.05 (not over-fitted)",        False, "0.0000",   "≥ 0.05"),
    ("C05", "Excess ann. return vs B&H > 0",               False, "−14.4%",   "> 0%"),
    ("C06", "Max drawdown > −30%",                         True,  "−5.1%",    "> −30%"),
    ("C07", "Strategy max DD shallower than B&H",          True,  "+13.7 pp", "> 0"),
    ("C08", "Validation OOS Sharpe ≥ 0.30 (no collapse)",  True,  "1.2000",   "≥ 0.30"),
    ("C09", "Holdout N ≥ 200 observations",                True,  "251",      "≥ 200"),
    ("C10", "Sharpe degradation val→holdout ≤ 0.50",       True,  "0.3541",   "≤ 0.50"),
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
    "Signal S2a_zscore_252d sourced from results/hy_ig_spy/signals_20260422.parquet "
    "(6,664 non-NaN values from 2000-10-06). "
    "Cost assumption: 5 bps one-way per trade."
)

st.divider()

# ── NAVIGATION ───────────────────────────────────────────────────────────────
st.markdown(
    "**Pages:** "
    "[Story](90_hy_ig_spy_v3_rerun_story) · "
    "[Evidence](90_hy_ig_spy_v3_rerun_evidence) · "
    "[Strategy](90_hy_ig_spy_v3_rerun_strategy) · "
    "📄 Methodology"
)
