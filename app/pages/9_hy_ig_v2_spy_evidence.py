"""HY-IG v2 -- The Evidence: Analytical Detail."""

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

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We tested the credit-equity relationship with multiple econometric methods "
    "across 25 years of daily data. Here is what we found.*"
)
st.markdown("---")

# --- Intro framing ---
st.markdown(
    "Our analysis employed multiple econometric methods, each designed to test a "
    "different aspect of the credit-equity relationship. We deliberately used methods "
    "that approach the question from different angles -- if the finding holds across "
    "multiple techniques, we can be more confident it is real and not an artifact of a "
    "particular statistical method."
)

# --- Key Finding KPI ---
if _metadata.get("key_finding"):
    st.info(f"**Key Finding:** {_metadata['key_finding']}")

# --- Direction badge ---
direction = _metadata.get("observed_direction", "counter_cyclical")
st.markdown(
    f"**Observed Direction:** {direction.replace('_', '-')} "
    f"({'Consistent' if _metadata.get('direction_consistent', True) else 'Inconsistent'} "
    f"with expectation)"
)
st.markdown("---")

# ---------------------------------------------------------------------------
# Tab Layout  (4 tabs)
# ---------------------------------------------------------------------------
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

    st.markdown(
        "**What this means:** When credit spreads widen (investors demand more "
        "compensation for risk), stock returns over the following weeks tend to be "
        "negative. The relationship is strongest at the 1-3 month horizon, suggesting "
        "the credit market prices risk ahead of equities."
    )

# ===================== CAUSALITY TAB =====================
with tab_cause:
    st.markdown("### Granger Causality: Who Leads Whom?")

    st.markdown(
        "**Granger causality** is a statistical test that asks: do past values of one "
        "variable help predict future values of another, above and beyond the second "
        "variable's own history? We used the Toda-Yamamoto variant because it works "
        "correctly even when the data contains trends, which financial data often does. "
        "We also measured **transfer entropy** -- an information-theoretic tool that "
        "captures directed information flow including nonlinear relationships that "
        "correlation-based tests miss."
    )

    st.markdown(
        "Crucially, we ran both tests in **both directions** to check for reverse "
        "causality. We tested at multiple time horizons (1, 5, 21, 63 days) and "
        "separately for stress and calm regimes."
    )

    st.markdown("#### Finding 1 -- The bond market and stock market take turns leading each other.")

    st.markdown(
        "Granger causality tests reveal statistically significant information flow "
        "in both directions (credit-to-equity and equity-to-credit). This is expected "
        "from the Merton model: equity and credit are linked through the same underlying "
        "corporate asset values. However, the credit-to-equity signal strengthens "
        "materially during stress regimes, while the equity-to-credit signal dominates "
        "during calm periods. Transfer entropy (the nonlinear test) shows even stronger "
        "asymmetry between the two directions."
    )

    st.markdown(
        "**What this means:** In calm markets, stock prices set the pace -- equities lead "
        "credit. But when stress builds, the bond market starts sending warnings that "
        "arrive weeks before stocks react. This is consistent with informed trading in "
        "credit markets during stress (Acharya & Johnson 2007) and is the core reason "
        "the credit signal has practical value for equity investors."
    )

    st.markdown("---")

    st.markdown("#### Finding 2 -- Credit spread shocks ripple through stock returns over weeks, not days.")

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
        "The impulse response shape -- a gradual build followed by a plateau -- tells us "
        "that credit information is incorporated into equity prices over weeks, not days."
    )

    st.markdown(
        "**What this means:** When the bond market signals trouble, the stock market does "
        "not adjust immediately. The adjustment plays out over several weeks, which creates "
        "a window for investors to act -- a signal that was fully priced in within 24 hours "
        "would be useless for trading purposes."
    )

# ===================== REGIMES TAB =====================
with tab_regime:
    st.markdown("### Regime-Switching Models")

    st.markdown("#### Finding 3 -- The signal activates at data-driven stress thresholds, not arbitrary cutoffs.")

    st.markdown(
        "Regime-switching models identify a \"stress\" state where the credit-equity "
        "relationship is fundamentally different from the calm state. The transition "
        "probability into the stress state increases sharply when the HY-IG z-score "
        "exceeds approximately 1.5-2.0 standard deviations above its rolling mean. "
        "This threshold is not imposed by us -- it is discovered by the model. It "
        "corresponds roughly to periods when the raw HY-IG spread is above 500-600 "
        "basis points, depending on the prevailing volatility."
    )

    st.markdown(
        "**What this means:** The credit signal does not gradually strengthen as spreads "
        "widen. Instead, it \"switches on\" at a specific stress threshold -- below that "
        "threshold, it is largely noise. A strategy based on this signal should only act "
        "when the model identifies the stress regime, ignoring the noise during calm periods."
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

    st.markdown("#### Finding 4 -- Credit spreads warn of bad outcomes, not good ones.")

    st.markdown(
        "Rather than estimating just the average effect of credit spreads on stock "
        "returns, we examined the entire distribution -- particularly the worst outcomes "
        "(the left tail, at the 5th and 10th percentiles). This approach is consistent "
        "with the \"Vulnerable Growth\" framework of Adrian, Boyarchenko & Giannone (2019)."
    )

    load_plotly_chart(
        "quantile_regression",
        fallback_text=(
            "Quantile regression coefficients across return quantiles "
            "(tau = 0.05 to 0.95)."
        ),
        caption=(
            "Credit spreads have their strongest explanatory power for the worst "
            "stock return outcomes (5th and 10th percentiles). "
            "The median and upper quantiles are largely unaffected."
        ),
        pair_id=PAIR_ID,
    )

    st.markdown(
        "**What this means:** Wide credit spreads are a warning sign for large stock "
        "declines, but narrow credit spreads do not predict large stock rallies. This is "
        "a risk management signal -- it tells you when to get defensive, not when to get "
        "aggressive. Think of it as a fire alarm, not a green light."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Tournament Summary
# ---------------------------------------------------------------------------
st.markdown("### The Combinatorial Tournament")

st.markdown(
    "We tested approximately 1,000+ meaningful combinations of signals (13 types), "
    "thresholds (7 methods), strategies (4 types), lead times (9 values), and lookback "
    "windows (4 lengths). These were ranked by out-of-sample **Sharpe ratio** -- a "
    "measure of risk-adjusted return calculated as (return minus risk-free rate) divided "
    "by volatility, where higher values mean better returns per unit of risk taken -- "
    "over 2018-2025 (data the models never saw during estimation). The top 5 strategies "
    "were then subjected to rigorous walk-forward validation, bootstrap significance "
    "testing, and transaction cost sensitivity analysis."
)

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12"
)
