"""HY-IG v2 — The Evidence: Analytical Detail."""

import json
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="HY-IG v2 Evidence | AIG-RLIC+",
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

PAIR_ID = "hy_ig_v2_spy"

# --- Load interpretation metadata for key metrics ---
_meta_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", PAIR_ID, "interpretation_metadata.json",
)
_metadata = {}
if os.path.exists(_meta_path):
    with open(_meta_path) as f:
        _metadata = json.load(f)

# --- Page Header ---
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We tested the credit-equity relationship with multiple econometric methods "
    "across 25 years of daily data. Here is what we found.*"
)
st.markdown("---")

# --- Key Finding KPI ---
if _metadata.get("key_finding"):
    st.info(f"**Key Finding:** {_metadata['key_finding']}")
    st.markdown("")

# --- Direction badge ---
direction = _metadata.get("observed_direction", "counter_cyclical")
st.markdown(
    f"**Observed Direction:** {direction.replace('_', '-')} "
    f"({'Consistent' if _metadata.get('direction_consistent', True) else 'Inconsistent'} "
    f"with expectation)"
)
st.markdown("---")

# --- Tab Layout ---
tab_corr, tab_cause, tab_regime, tab_quantile = st.tabs(
    ["Correlations", "Causality & Projections", "Regimes", "Quantile Regression"]
)

# ===================== CORRELATIONS TAB =====================
with tab_corr:
    st.markdown("### Correlation Structure")

    st.markdown(
        "We computed correlations between credit spread signals and forward equity "
        "returns at multiple horizons. The HY-IG spread shows a robust negative "
        "relationship with future stock returns, consistent with the counter-cyclical "
        "hypothesis: wider spreads predict weaker equity performance."
    )

    load_plotly_chart(
        "correlation_heatmap",
        fallback_text=(
            "Correlation heatmap: HY-IG signal variants vs SPY forward returns "
            "at 1d, 5d, 21d, 63d horizons."
        ),
        caption=(
            "Pearson correlations between credit spread signal variants and forward "
            "return horizons. Cool colors indicate negative (counter-cyclical) "
            "relationships. The 63-day momentum signal shows the strongest "
            "predictive correlation."
        ),
        pair_id=PAIR_ID,
    )

# ===================== CAUSALITY TAB =====================
with tab_cause:
    st.markdown("### Granger Causality: Who Leads Whom?")

    st.markdown(
        "We tested whether credit spread changes statistically 'cause' (in the Granger "
        "sense -- meaning they help predict) future stock returns, and vice versa. "
        "Crucially, we ran these tests in **both directions** to check for reverse "
        "causality. We tested at multiple lag orders (1, 5, 21, 63 days) and separately "
        "for stress and calm regimes."
    )

    st.markdown(
        "**Finding 1 -- Bidirectional causality with regime asymmetry.** "
        "Granger causality tests reveal statistically significant information flow "
        "in both directions (credit-to-equity and equity-to-credit). This is expected "
        "from the Merton model: equity and credit are linked through the same underlying "
        "corporate asset values. However, the credit-to-equity signal strengthens "
        "materially during stress regimes, while the equity-to-credit signal dominates "
        "during calm periods. Transfer entropy (a nonlinear test that can capture "
        "relationships beyond simple linear correlation) shows even stronger asymmetry."
    )

    st.markdown("---")

    st.markdown("### Local Projections: Impulse Response by Horizon")

    load_plotly_chart(
        "local_projections",
        fallback_text=(
            "Local projection impulse responses: cumulative effect of a 1-SD "
            "credit spread shock on SPY returns at horizons 1d to 63d."
        ),
        caption=(
            "Jorda (2005) local projections with HAC standard errors. "
            "A 1-SD widening in the HY-IG z-score is associated with negative "
            "cumulative stock returns that build over 1-5 weeks before fading. "
            "The effect is 2-3x larger during stress regimes."
        ),
        pair_id=PAIR_ID,
    )

    st.markdown(
        "**Finding 2 -- Credit spread shocks have persistent effects on stock returns.** "
        "The impulse response shape -- a gradual build followed by a plateau -- suggests "
        "that credit information is incorporated into equity prices over weeks, not days."
    )

# ===================== REGIMES TAB =====================
with tab_regime:
    st.markdown("### Regime-Switching Models")

    st.markdown(
        "**Finding 3 -- The signal activates at data-driven stress thresholds.** "
        "Regime-switching models identify a 'stress' state where the credit-equity "
        "relationship is fundamentally different from the calm state. The transition "
        "probability into the stress state increases sharply when the HY-IG z-score "
        "exceeds approximately 1.5-2.0 standard deviations above its rolling mean. "
        "This threshold is not imposed -- it is discovered by the model."
    )

    load_plotly_chart(
        "hmm_regime_probs",
        fallback_text=(
            "HMM regime probability time series: probability of stress state "
            "over the full sample (2000-2025)."
        ),
        caption=(
            "Hidden Markov Model stress probability over time. High values "
            "indicate the model identifies the market as being in a stress regime. "
            "Note the clear spikes during the GFC, COVID, and 2022."
        ),
        pair_id=PAIR_ID,
    )

# ===================== QUANTILE REGRESSION TAB =====================
with tab_quantile:
    st.markdown("### Quantile Regression: Tail Risk Channel")

    st.markdown(
        "**Finding 4 -- Downside equity risk is the primary channel.** "
        "Rather than estimating just the average effect of credit spreads on stock "
        "returns, we examined the entire distribution -- particularly the worst outcomes "
        "(the left tail, at the 5th and 10th percentiles)."
    )

    load_plotly_chart(
        "quantile_regression",
        fallback_text=(
            "Quantile regression coefficients across return quantiles "
            "(tau = 0.05 to 0.95)."
        ),
        caption=(
            "Credit spreads have their strongest explanatory power for the worst "
            "stock return outcomes (5th and 10th percentiles), consistent with the "
            "'Vulnerable Growth' framework of Adrian, Boyarchenko & Giannone (2019). "
            "The median and upper quantiles are largely unaffected."
        ),
        pair_id=PAIR_ID,
    )

    st.markdown(
        "In plain English: credit spreads warn of bad outcomes but say relatively "
        "little about good outcomes."
    )

st.markdown("---")

# --- Tournament Summary ---
st.markdown("### The Combinatorial Tournament")

st.markdown(
    "We tested approximately 800-1,200 meaningful combinations of signals (13 types), "
    "thresholds (7 methods), strategies (4 types), lead times (9 values), and lookback "
    "windows (4 lengths). These were ranked by out-of-sample Sharpe ratio (2018-2025 "
    "-- data the models never saw during estimation), with the top 5 subjected to "
    "rigorous walk-forward validation, bootstrap significance testing, and transaction "
    "cost sensitivity analysis."
)

# --- Transition ---
st.markdown("---")
st.markdown(
    "The statistical evidence confirms that credit spreads carry genuine predictive "
    "information for stock returns, especially during stress. The practical question "
    "is: can an investor use this signal to improve their risk-adjusted returns -- "
    "and at what cost?"
)

st.page_link(
    "pages/9_hy_ig_v2_spy_strategy.py",
    label="Continue to The Strategy",
    icon="🎯",
)

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
