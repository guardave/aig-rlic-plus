"""Finding 4 — The Evidence: PERMIT → SPY Analytical Detail."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="Permits Evidence | AIG-RLIC+",
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
    "*We tested the permits-equity relationship with multiple econometric methods "
    "across 35 years of data. Here is what we found.*"
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
        "permit_spy_correlations",
        fallback_text="Correlation heatmap: Permits signals vs SPY forward returns",
        caption=(
            "Pearson correlations between Building Permits signal variants and "
            "forward return horizons. Warm colors = positive (pro-cyclical). "
            "Permits YoY growth and momentum signals show the strongest positive "
            "correlations with 3-6 month forward returns."
        ),
        pair_id="permit_spy",
    )

    st.markdown("---")

    st.markdown(
        '<div class="narrative-block">'
        "<b>Interpretation:</b> The correlation structure confirms the pro-cyclical "
        "relationship. Unlike Industrial Production (which showed a counter-intuitive "
        "peak-cycle z-score effect), permits correlations are consistently positive "
        "across signal types and horizons. This aligns with the leading indicator "
        "status: permits signal direction, and the direction is consistent."
        "</div>",
        unsafe_allow_html=True,
    )

# ===================== LOCAL PROJECTIONS TAB =====================
with tab_lp:
    st.markdown("### Local Projections: Impulse Response by Horizon")

    load_plotly_chart(
        "permit_spy_local_projections",
        fallback_text="Local projection coefficients by forecast horizon",
        caption=(
            "Jorda (2005) local projections with HAC (Newey-West) standard errors. "
            "Stars indicate significance at p<0.05. The coefficient shows the marginal "
            "effect of a 1pp increase in Permits YoY growth on forward SPY returns."
        ),
        pair_id="permit_spy",
    )

    st.markdown("---")

    st.markdown(
        '<div class="narrative-block">'
        "<b>Interpretation:</b> Local projections show a positive impulse response "
        "that is strongest at the 3-6 month horizon, consistent with permits' role "
        "as a leading indicator. The effect is economically meaningful: a 1 standard "
        "deviation increase in permits growth is associated with higher cumulative "
        "SPY returns over the subsequent 6 months. The confidence bands widen at "
        "longer horizons, reflecting greater uncertainty."
        "</div>",
        unsafe_allow_html=True,
    )

# --- Transition ---
st.markdown("---")
st.markdown(
    '<div class="transition-text">'
    "The statistical evidence confirms a genuine pro-cyclical relationship between "
    "building permits and equity returns, with permits leading by 3-6 months. "
    "The practical question is: can investors translate this into a profitable strategy?"
    "</div>",
    unsafe_allow_html=True,
)

st.page_link("pages/7_permit_spy_strategy.py", label="Continue to The Strategy", icon="🎯")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
