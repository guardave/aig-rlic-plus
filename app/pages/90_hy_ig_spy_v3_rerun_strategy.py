"""Page 90 — HY-IG × SPY v3 Rerun | Strategy (experiment fork).

Thin wrapper per APP-PT1. Renders Ray's strategy narrative and Vera's
equity curve and drawdown charts. Experiment fork — not a production pair.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from components.charts import load_plotly_chart
from pair_configs.hy_ig_spy_v3_rerun_config import (
    display_name,
    pair_id,
    strategy_narrative,
    winner_summary,
)

st.set_page_config(
    page_title=f"{display_name} Strategy | AIG-RLIC+",
    page_icon="⚗️",
    layout="wide",
)

# ── EXPERIMENT FORK BANNER ──────────────────────────────────────────────────
st.warning(
    "⚗️ EXPERIMENT FORK — not a production pair. "
    "Results are for comparison purposes only."
)

st.title(f"Strategy — {display_name}")
st.caption(
    f"Winner: {winner_summary['signal_code']} / {winner_summary['threshold_code']} / "
    f"{winner_summary['strategy_code']} / L{winner_summary['lead_days']}  |  "
    f"Validation Sharpe: {winner_summary['val_oos_sharpe']:.2f}  |  "
    f"Holdout Sharpe: {winner_summary['holdout_sharpe']:.4f}"
)

st.divider()

# ── KPI SUMMARY ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Validation Sharpe", f"{winner_summary['val_oos_sharpe']:.2f}", delta="1,638 days")
col2.metric("Holdout Sharpe", f"{winner_summary['holdout_sharpe']:.2f}", delta="251 days")
col3.metric("Holdout MDD", "−5.1%", delta="vs B&H −18.8%", delta_color="inverse")
col4.metric("Holdout Ann. Return", "5.24%", delta="B&H 19.7%", delta_color="off")

st.divider()

# ── STRATEGY NARRATIVE (Ray) ─────────────────────────────────────────────────
st.subheader("Strategy Summary")
st.markdown(strategy_narrative)

st.divider()

# ── EQUITY CURVES — HOLDOUT (Vera) ───────────────────────────────────────────
st.subheader("Equity Curves — Holdout Period (2025-01-14 to 2025-12-31)")
load_plotly_chart(
    "equity_curves_holdout",
    pair_id=pair_id,
    fallback_text="Equity curves (holdout) chart pending (GATE-25 placeholder).",
    caption=(
        "Cumulative equity curves for the strategy (S2a_zscore_252d / T2_rp75 / P1) "
        "vs. buy-and-hold SPY over the sealed holdout period. "
        "Holdout Sharpe: 0.85 vs. B&H MDD: −18.8%."
    ),
)

st.divider()

# ── EQUITY CURVES — VALIDATION (Vera) ────────────────────────────────────────
st.subheader("Equity Curves — Validation Period (2018-10-04 to 2025-01-13)")
load_plotly_chart(
    "equity_curves_validation",
    pair_id=pair_id,
    fallback_text="Equity curves (validation) chart pending (GATE-25 placeholder).",
    caption=(
        "Cumulative equity curves over the full validation OOS window. "
        "Validation Sharpe: 1.20."
    ),
)

st.divider()

# ── DRAWDOWN COMPARISON (Vera) ───────────────────────────────────────────────
st.subheader("Drawdown Comparison")
load_plotly_chart(
    "drawdown_comparison",
    pair_id=pair_id,
    fallback_text="Drawdown comparison chart pending (GATE-25 placeholder).",
    caption=(
        "Strategy max drawdown vs. buy-and-hold SPY. "
        "Holdout MDD: −5.1% vs. B&H −18.8% — C07 PASS."
    ),
)

st.divider()

# ── NAVIGATION ───────────────────────────────────────────────────────────────
st.markdown(
    "**Pages:** "
    "[Story](90_hy_ig_spy_v3_rerun_story) · "
    "[Evidence](90_hy_ig_spy_v3_rerun_evidence) · "
    "📄 Strategy · "
    "[Methodology](90_hy_ig_spy_v3_rerun_methodology)"
)
