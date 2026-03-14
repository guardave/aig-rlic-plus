"""Finding 2 — The Evidence: INDPRO → SPY Analytical Detail."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="IP Evidence | AIG-RLIC+",
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
    "*We tested the IP-equity relationship with 9 econometric methods across 35 years of data. "
    "Here is what we found.*"
)
st.markdown("---")

# --- Tab Layout ---
tab_corr, tab_cause, tab_regime, tab_ml = st.tabs(
    ["Correlations", "Causality & Projections", "Regimes", "Machine Learning"]
)

# ===================== CORRELATIONS TAB =====================
with tab_corr:
    st.markdown("### Correlation Structure")

    load_plotly_chart(
        "indpro_spy_correlations",
        fallback_text="Correlation heatmap: IP signals vs SPY forward returns",
        caption=(
            "Pearson correlations between 8 IP signal variants and 4 forward return horizons. "
            "Warm colors = positive (pro-cyclical), cool colors = negative. "
            "Note the z-score's negative correlation at 12M — the peak-cycle effect."
        ),
        pair_id="indpro_spy",
    )

    st.markdown("---")

    st.markdown("### Cross-Correlation Function")

    load_plotly_chart(
        "indpro_spy_ccf",
        fallback_text="Cross-correlation function: IP YoY vs SPY monthly return",
        caption=(
            "CCF at lags -12 to +12 months. Red bars are statistically significant. "
            "Negative lags indicate IP leading SPY."
        ),
        pair_id="indpro_spy",
    )

# ===================== CAUSALITY TAB =====================
with tab_cause:
    st.markdown("### Granger Causality: Who Leads Whom?")

    load_plotly_chart(
        "indpro_spy_granger",
        fallback_text="Granger causality p-values by lag order",
        caption=(
            "Granger causality tests in both directions. "
            "Below the dashed line (p=0.05) indicates statistically significant causality."
        ),
        pair_id="indpro_spy",
    )

    st.markdown(
        '<div class="narrative-block">'
        "<b>Interpretation:</b> The Granger causality results show mixed evidence. "
        "IP growth does not strongly Granger-cause SPY returns at conventional lag orders. "
        "This is consistent with IP being a <b>coincident</b> indicator rather than a "
        "leading indicator — the predictive power comes from the publication lag (6 weeks) "
        "and momentum effects, not from IP leading the economy."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### Local Projections: Impulse Response by Horizon")

    load_plotly_chart(
        "indpro_spy_local_projections",
        fallback_text="Local projection coefficients by forecast horizon",
        caption=(
            "Jorda (2005) local projections with HAC (Newey-West) standard errors. "
            "Stars indicate significance at p<0.05. The coefficient shows the marginal "
            "effect of a 1pp increase in IP YoY growth on forward SPY returns."
        ),
        pair_id="indpro_spy",
    )

# ===================== REGIMES TAB =====================
with tab_regime:
    st.markdown("### Quantile Regression: Tail Risk Channel")

    load_plotly_chart(
        "indpro_spy_quantile_regression",
        fallback_text="Quantile regression coefficients across return quantiles",
        caption=(
            "The effect of IP growth varies across the return distribution. "
            "At the left tail (worst outcomes), the coefficient tends to be positive — "
            "higher IP growth protects against extreme losses."
        ),
        pair_id="indpro_spy",
    )

    st.markdown("---")

    st.markdown("### Markov-Switching Regression")

    st.markdown(
        '<div class="narrative-block">'
        "A 2-state Markov-Switching regression was estimated, identifying expansion and "
        "contraction regimes with different volatility characteristics. The model captured "
        "the major regime transitions (2001, 2008-09, 2020) consistent with NBER recession dates."
        "</div>",
        unsafe_allow_html=True,
    )

# ===================== ML TAB =====================
with tab_ml:
    st.markdown("### Random Forest Feature Importance")

    load_plotly_chart(
        "indpro_spy_rf_importance",
        fallback_text="RF feature importance from last walk-forward window",
        caption=(
            "Top features for predicting positive 3M SPY returns. "
            "Yield spread and IP z-score are the most important features, "
            "suggesting both rate and IP cycle information matter."
        ),
        pair_id="indpro_spy",
    )

    st.markdown(
        '<div class="narrative-block">'
        "<b>Walk-forward accuracy: 61.4%</b> across 20 test windows (10yr train / 3yr test). "
        "Modestly better than the 50% baseline, but not a strong standalone predictor. "
        "The RF confirms that IP provides some information, but simpler momentum-based "
        "signals outperform in the tournament."
        "</div>",
        unsafe_allow_html=True,
    )

# --- Transition ---
st.markdown("---")
st.markdown(
    '<div class="transition-text">'
    "The statistical evidence confirms a real but nuanced IP-equity relationship. "
    "The practical question is: can investors use IP signals to improve their outcomes?"
    "</div>",
    unsafe_allow_html=True,
)

st.page_link("pages/5_indpro_spy_strategy.py", label="Continue to The Strategy", icon="🎯")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
