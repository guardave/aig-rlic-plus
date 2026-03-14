"""Finding 4 — The Story: Building Permits as an Equity Signal."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(
    page_title="Permits Story | AIG-RLIC+",
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
st.title("The Story: Building Permits and the Stock Market")
st.markdown("*Can the number of new housing permits tell us where stocks are headed?*")
st.markdown("---")

# --- How to Read This (Direction Callout) ---
st.info(
    "**How to Read This:** When Building Permits are rising (positive YoY growth), "
    "this historically signals expanding housing and construction activity, which "
    "tends to precede stronger equity returns. When permits decline (negative YoY "
    "growth), expect weaker equity performance with a lead of up to 6 months. "
    "The relationship is **pro-cyclical**: rising permits, rising stocks."
)

# --- Hero Chart ---
st.markdown("### 35 Years of Building Permits vs. S&P 500")
load_plotly_chart(
    "permit_spy_hero",
    fallback_text="Hero chart: Building Permits vs SPY price (1990-2025)",
    caption=(
        "Dual-axis view: Building Permits (left, red) and SPY price (right, blue). "
        "Permits peaked before the 2001 and 2008 recessions and collapsed during the "
        "housing crisis, providing an early warning signal for equity declines."
    ),
    pair_id="permit_spy",
)

st.markdown("---")

# --- Why Permits Matter ---
SECTION_1 = """
### Why Should Stock Investors Care About Building Permits?

Building Permits (FRED: PERMIT) measure the number of new privately-owned housing units authorized by building permits. They have been a component of the Conference Board's Leading Economic Index (LEI) since 1959 — one of the longest-tenured leading indicators in macroeconomics.

For stock investors, permits matter because housing is a **leading sector** of the economy. Residential construction accounts for roughly 15-18% of GDP when you include direct construction, furnishing, and the wealth effects of home equity. When permits rise, it signals future construction activity, employment growth, and consumer spending. When permits fall, a broader slowdown typically follows.

<!-- expander: What are Building Permits (PERMIT)? -->
Building Permits (PERMIT) are published monthly by the U.S. Census Bureau as part of the New Residential Construction report. Key features:

- **Monthly frequency** (released ~2-3 weeks after the reference month)
- **Seasonally adjusted annual rate (SAAR)** — seasonal patterns are removed
- **Leading indicator** — permits precede actual construction by 1-3 months and broader economic activity by 3-6 months
- **LEI component** — part of the Conference Board's Leading Economic Index since 1959
- **Covers new private housing** — single-family and multi-family units
<!-- /expander -->

### The Permits-Equity Connection

Our analysis examines 35 years of data (1990-2025) to test whether Building Permits predict S&P 500 returns. The economic logic is well-established:

- **Rising permits** signal expanding housing demand, future construction employment, household wealth accumulation, and consumer confidence — bullish for stocks
- **Falling permits** signal housing weakness, reduced construction activity, and a cooling economy — bearish for stocks
- The signal operates as a **leading indicator** because permits precede actual construction starts by months, and housing downturns reliably foreshadow broader recessions

This is what economists call a **pro-cyclical** relationship: the indicator and the stock market move in the same direction over the business cycle. As Edward Leamer famously argued in his 2007 Jackson Hole paper, "Housing IS the business cycle."
"""

render_narrative(SECTION_1)

st.markdown("---")

# --- Regime Analysis ---
st.markdown("### What History Shows: Returns by Permits Growth Regime")

load_plotly_chart(
    "permit_spy_regime_stats",
    fallback_text="SPY Sharpe by Building Permits growth quartile",
    caption=(
        "Equity performance across Building Permits growth regimes. "
        "Stocks perform better during high-growth permit periods (Q4) "
        "and worse during permit contractions (Q1), confirming the "
        "pro-cyclical relationship."
    ),
    pair_id="permit_spy",
)

st.markdown(
    '<div class="narrative-block">'
    "<b>Key finding:</b> The pro-cyclical relationship is confirmed but with modest "
    "differentiation between regimes. The high-growth regime (Q4) delivers a Sharpe of "
    "0.95, while the low-growth regime (Q1) delivers 0.75. The spread is narrower than "
    "for some other indicators, suggesting permits work best as a directional signal "
    "rather than a regime-timing tool."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- Historical Context ---
st.markdown("### Historical Context: Three Defining Episodes")

st.warning(
    "**Three episodes dominate the permits data:**\n\n"
    "1. **Housing Bubble (2003-2007):** Permits surged to record highs driven by "
    "subprime lending and speculation. The signal was pro-cyclical — stocks rose — "
    "but the bubble masked underlying risk. The eventual collapse was catastrophic.\n\n"
    "2. **Great Recession (2008-2009):** Permits fell over 50% from peak, one of the "
    "deepest contractions on record. This correctly signaled severe economic weakness.\n\n"
    "3. **COVID Collapse (April 2020):** Permits plunged as construction halted, "
    "then recovered rapidly. Post-COVID supply chain distortions created noise in "
    "the signal that persisted through 2022."
)

# --- Transition ---
st.markdown("---")
render_transition(
    "History and economic theory position building permits as one of the strongest "
    "leading indicators available. But does the econometric evidence confirm a "
    "statistically significant relationship with equity returns?"
)

st.page_link("pages/7_permit_spy_evidence.py", label="Continue to The Evidence", icon="🔬")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12 | "
    "~420 monthly observations"
    "</div>",
    unsafe_allow_html=True,
)
