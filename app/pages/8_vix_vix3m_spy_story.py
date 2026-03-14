"""Finding 5 — The Story: VIX/VIX3M Volatility Term Structure as an Equity Signal."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(
    page_title="VIX/VIX3M Story | AIG-RLIC+",
    page_icon="📖",
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
st.title("The Story: VIX Term Structure and the Stock Market")
st.markdown("*When near-term fear exceeds longer-term fear, stocks are in trouble.*")
st.markdown("---")

# --- How to Read This (Direction Callout) ---
st.info(
    "**How to Read This:** The VIX/VIX3M ratio compares 30-day implied volatility (VIX) "
    "to 3-month implied volatility (VIX3M). When the ratio exceeds 1.0, the term structure "
    "is in **backwardation** — near-term fear exceeds longer-term fear — which signals panic "
    "and precedes weak equity returns. When the ratio is below 1.0, the term structure is in "
    "**contango** (the normal state), signaling calm markets and strong equity performance. "
    "The relationship is **counter-cyclical**: a rising ratio means falling stocks."
)

# --- Hero Chart ---
st.markdown("### 18 Years of VIX Term Structure vs. S&P 500")
load_plotly_chart(
    "vix_vix3m_spy_hero",
    fallback_text="Hero chart: VIX/VIX3M ratio vs SPY price (2007-2025)",
    caption=(
        "Dual-axis view: VIX/VIX3M ratio (left) and SPY price (right). "
        "The dashed line at ratio = 1.0 marks the backwardation boundary. "
        "Every major equity drawdown — the 2008 crisis, the 2011 debt ceiling, "
        "the 2018 vol-mageddon, and the 2020 COVID crash — was accompanied by "
        "a spike above 1.0. Calm, rising markets correspond to the ratio "
        "sitting well below 1.0 in contango."
    ),
    pair_id="vix_vix3m_spy",
)

st.markdown("---")

# --- Why VIX Term Structure Matters ---
SECTION_1 = """
### Why Should Stock Investors Care About the VIX Term Structure?

The VIX index measures 30-day implied volatility derived from S&P 500 options. VIX3M measures the same thing over a 3-month horizon. In normal markets, longer-dated options carry a higher volatility premium (contango), so VIX/VIX3M sits below 1.0. When markets panic, traders bid up near-term protection aggressively, pushing the ratio above 1.0 into backwardation.

This ratio captures something fundamentally important: the **urgency of fear**. It functions as a real-time put/call sentiment proxy — when near-term put demand surges relative to longer-term hedging, the ratio spikes. Unlike the VIX level alone (which can stay elevated for extended periods), the term structure ratio reveals whether the market is experiencing acute stress versus chronic anxiety.

<!-- expander: What is VIX/VIX3M and why is the 1.0 line special? -->
The VIX/VIX3M ratio is the quotient of the CBOE 30-day Volatility Index (VIX) and the CBOE 3-month Volatility Index (VIX3M). Key features:

- **Daily frequency** — real-time options-derived signal
- **Natural threshold at 1.0** — backwardation (>1.0) vs contango (<1.0) has structural economic meaning
- **Counter-cyclical** — rises during stress, falls during calm
- **VIX3M available since 2007** — sample begins January 2007
- **Put/Call proxy** — captures the same near-term put demand that drives high P/C ratios
- **Mixon (2007)** documented that the volatility term structure is mean-reverting but regime-dependent
<!-- /expander -->

### The Term Structure as a Fear Gauge

Our analysis examines 18 years of daily data (2007-2025) to test whether the VIX/VIX3M ratio predicts S&P 500 returns. The economic logic is direct:

- **Ratio below 1.0 (contango)** — the normal state. Markets are calm, hedging demand is balanced, and equities tend to grind higher. This is where the bulk of positive equity returns occur.
- **Ratio above 1.0 (backwardation)** — acute stress. Near-term put demand exceeds longer-term hedging, signaling panic. Equities underperform or crash during these episodes.
- The backwardation line at 1.0 is not an arbitrary percentile — it is a **structural boundary** derived from options pricing theory, making it one of the most economically meaningful thresholds in our entire catalog.

This is what economists call a **counter-cyclical** relationship: the indicator rises when the stock market falls, and vice versa. As Eraker (2004) showed, VIX dynamics are driven by jump risk premia that spike during dislocations.
"""

render_narrative(SECTION_1)

st.markdown("---")

# --- Regime Analysis ---
st.markdown("### What History Shows: Returns by Term Structure Regime")

load_plotly_chart(
    "vix_vix3m_spy_regime_stats",
    fallback_text="SPY Sharpe by VIX/VIX3M ratio quartile",
    caption=(
        "Equity performance across VIX/VIX3M ratio regimes. "
        "Q1 (low ratio, deep contango) delivers a Sharpe of 6.53, while "
        "Q4 (high ratio, backwardation/panic) delivers -2.38. This is the "
        "largest regime spread observed across all indicator pairs in our catalog."
    ),
    pair_id="vix_vix3m_spy",
)

st.markdown(
    '<div class="narrative-block">'
    "<b>Key finding:</b> The regime differentiation here is extraordinary — "
    "the strongest we have seen across all pairs studied. When the VIX term "
    "structure is in deep contango (Q1, ratio well below 1.0), equities deliver "
    "a Sharpe of <b>6.53</b>. When the term structure flips to backwardation "
    "(Q4, ratio above 1.0), the Sharpe collapses to <b>-2.38</b>. The spread of "
    "nearly 9 Sharpe points dwarfs what we see with credit spreads (~3 points), "
    "industrial production (~2 points), or building permits (~0.2 points). "
    "This makes VIX/VIX3M the single most powerful regime signal in our toolkit."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- Historical Context ---
st.markdown("### Historical Context: Four Defining Episodes")

st.warning(
    "**Four episodes illustrate the signal's power:**\n\n"
    "1. **Global Financial Crisis (2008-2009):** The ratio spiked to extreme "
    "backwardation as Lehman Brothers collapsed. Near-term VIX exceeded 80 while "
    "VIX3M, though elevated, lagged behind. The term structure inversion preceded "
    "the worst of the equity drawdown.\n\n"
    "2. **Debt Ceiling Crisis (August 2011):** A sharp, brief backwardation spike "
    "coincided with the S&P downgrade of U.S. sovereign debt. SPY fell ~19% peak "
    "to trough; the ratio reverted to contango as the market recovered.\n\n"
    "3. **Volmageddon (February 2018):** The XIV (inverse VIX) blow-up caused a "
    "violent term structure inversion. This was a volatility-specific event rather "
    "than a macro crisis, yet the signal correctly flagged the equity selloff.\n\n"
    "4. **COVID Crash (March 2020):** The ratio surged above 1.0 as the pandemic "
    "triggered the fastest bear market in history. The OOS period (2020-2025) "
    "includes this extreme event, providing a severe stress test for the signal."
)

# --- Transition ---
st.markdown("---")
render_transition(
    "The VIX term structure offers the most powerful regime differentiation we have "
    "observed across all indicator pairs. But does the econometric evidence confirm "
    "a statistically robust and exploitable relationship with equity returns?"
)

st.page_link("pages/8_vix_vix3m_spy_evidence.py", label="Continue to The Evidence", icon="🔬")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2007-01 to 2025-12 | "
    "~4,500 daily observations"
    "</div>",
    unsafe_allow_html=True,
)
