"""Finding 5 — The Evidence: VIX/VIX3M → SPY Analytical Detail."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="VIX/VIX3M Evidence | AIG-RLIC+",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_sidebar()
render_glossary_sidebar()

# --- Page Header ---
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We tested the VIX term structure-equity relationship with multiple econometric "
    "methods across 18 years of daily data. Here is what we found.*"
)
st.markdown("---")

# --- Tab Layout ---
tab_corr, tab_lp = st.tabs(
    ["Correlations", "Local Projections"]
)

# ===================== CORRELATIONS TAB =====================
with tab_corr:
    st.markdown("### Correlation Structure")

    load_plotly_chart(
        "vix_vix3m_spy_correlations",
        fallback_text="Correlation heatmap: VIX/VIX3M signals vs SPY forward returns",
        caption=(
            "Pearson correlations between VIX/VIX3M signal variants and "
            "forward return horizons. Cool colors = negative (counter-cyclical). "
            "The z-score and rolling percentile signals show the strongest "
            "negative correlations with forward equity returns, confirming "
            "that elevated ratios precede weak performance."
        ),
        pair_id="vix_vix3m_spy",
    )

    st.markdown("---")

    st.markdown(
        '<div class="narrative-block">'
        "<b>Interpretation:</b> The correlation structure confirms the counter-cyclical "
        "relationship. Unlike pro-cyclical indicators (e.g., building permits, where "
        "higher values correlate with better returns), higher VIX/VIX3M ratios are "
        "associated with <i>lower</i> forward equity returns across all signal variants "
        "and horizons. The strongest correlations appear at the 1-5 day horizon, "
        "consistent with the high-frequency, options-derived nature of the signal. "
        "The direction is unambiguous: when near-term fear dominates, stocks suffer."
        "</div>",
        unsafe_allow_html=True,
    )

# ===================== LOCAL PROJECTIONS TAB =====================
with tab_lp:
    st.markdown("### Local Projections: Impulse Response by Horizon")

    load_plotly_chart(
        "vix_vix3m_spy_local_projections",
        fallback_text="Local projection coefficients by forecast horizon",
        caption=(
            "Jorda (2005) local projections with HAC (Newey-West) standard errors. "
            "Stars indicate significance at p<0.05. The coefficient shows the marginal "
            "effect of a 1-unit increase in VIX/VIX3M z-score on forward SPY returns."
        ),
        pair_id="vix_vix3m_spy",
    )

    st.markdown("---")

    st.markdown(
        '<div class="narrative-block">'
        "<b>Interpretation:</b> Local projections show a negative impulse response "
        "that is strongest at short horizons (1-5 days) and remains significant out "
        "to 21 trading days. A 1 standard deviation increase in the VIX/VIX3M ratio "
        "is associated with meaningfully lower cumulative SPY returns. The confidence "
        "bands are tighter than for monthly indicators because the daily frequency "
        "provides substantially more observations. The effect is both statistically "
        "and economically significant, consistent with the massive regime Sharpe "
        "differentials observed on the Story page."
        "</div>",
        unsafe_allow_html=True,
    )

# --- Transition ---
st.markdown("---")
st.markdown(
    '<div class="transition-text">'
    "The statistical evidence confirms a powerful counter-cyclical relationship "
    "between the VIX term structure and equity returns. The signal operates at "
    "daily frequency with strong significance. The practical question is: can "
    "investors translate this into a profitable strategy?"
    "</div>",
    unsafe_allow_html=True,
)

st.page_link("pages/8_vix_vix3m_spy_strategy.py", label="Continue to The Strategy", icon="🎯")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2007-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
