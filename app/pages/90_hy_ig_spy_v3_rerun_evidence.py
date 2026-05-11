"""Page 90 — HY-IG × SPY v3 Rerun | Evidence (experiment fork).

Thin wrapper per APP-PT1. Renders Ray's evidence narrative and Vera's
signal_distribution chart. Experiment fork — not a production pair.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from components.charts import load_plotly_chart
from pair_configs.hy_ig_spy_v3_rerun_config import (
    display_name,
    evidence_narrative,
    pair_id,
    winner_summary,
)

st.set_page_config(
    page_title=f"{display_name} Evidence | AIG-RLIC+",
    page_icon="⚗️",
    layout="wide",
)

# ── PAIR TITLE (APP-TT1) ────────────────────────────────────────────────────
st.title(f"{display_name}")
st.subheader("Evidence")

# ── EXPERIMENT FORK BANNER ──────────────────────────────────────────────────
st.warning(
    "⚗️ EXPERIMENT FORK — not a production pair. "
    "Results are for comparison purposes only."
)
st.caption(
    f"Winner: {winner_summary['signal_code']} / {winner_summary['threshold_code']} / "
    f"{winner_summary['strategy_code']} / L{winner_summary['lead_days']}  |  "
    f"Validation Sharpe: {winner_summary['val_oos_sharpe']:.2f}  |  "
    f"Holdout Sharpe: {winner_summary['holdout_sharpe']:.4f}"
)

st.divider()

# ── EVIDENCE NARRATIVE (Ray) ─────────────────────────────────────────────────
st.subheader("Evidence Summary")
st.markdown(evidence_narrative)

st.divider()

# ── SIGNAL DISTRIBUTION CHART (Vera) ────────────────────────────────────────
st.subheader("Signal Distribution")
load_plotly_chart(
    "signal_distribution",
    pair_id=pair_id,
    fallback_text="Signal distribution chart pending (GATE-25 placeholder).",
    caption=(
        "Distribution of the 252-day z-score of the HY-IG credit spread "
        "(S2a_zscore_252d) across in-sample, validation, and holdout periods. "
        "The rolling 75th-percentile threshold (T2_rp75) is overlaid."
    ),
)

st.divider()

# ── NAVIGATION ───────────────────────────────────────────────────────────────
col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
with col_b1: st.page_link("pages/90_hy_ig_spy_v3_rerun_story.py", label="Story", icon="📖")
with col_b2: st.markdown("**🔬 Evidence**")
with col_b3: st.page_link("pages/90_hy_ig_spy_v3_rerun_strategy.py", label="Strategy", icon="⚙️")
with col_b4: st.page_link("pages/90_hy_ig_spy_v3_rerun_methodology.py", label="Methodology", icon="📐")
with col_b5: st.page_link("pages/91_hy_ig_spy_v3_retro_story.py", label="Retro fork →", icon="⚗️")
