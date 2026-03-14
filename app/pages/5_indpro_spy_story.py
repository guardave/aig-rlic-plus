"""Finding 2 — The Story: Industrial Production as an Equity Signal."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(
    page_title="IP Story | AIG-RLIC+",
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
st.title("The Story: Factory Output and the Stock Market")
st.markdown("*Does the pace of industrial activity predict where stocks are headed?*")
st.markdown("---")

# --- How to Read This (Direction Callout) ---
st.info(
    "**How to Read This:** When Industrial Production is rising (positive YoY growth), "
    "this historically signals expanding manufacturing activity and tends to precede "
    "stronger equity returns. When IP contracts (negative YoY growth), expect weaker "
    "equity performance with a lag of 1-3 months."
)

# --- Hero Chart ---
st.markdown("### 35 Years of Industrial Production vs. S&P 500")
load_plotly_chart(
    "indpro_spy_hero",
    fallback_text="Hero chart: IP YoY growth vs SPY price (1990-2025)",
    caption=(
        "Dual-axis view: IP YoY growth (left, red) and SPY price (right, blue). "
        "Red shaded bands mark industrial contraction periods (YoY growth < 0). "
        "Notice how contractions tend to overlap with equity declines."
    ),
    pair_id="indpro_spy",
)

st.markdown("---")

# --- Why IP Matters ---
SECTION_1 = """
### Why Should Stock Investors Care About Factory Output?

Industrial Production measures the real output of the manufacturing, mining, and utility sectors. It is one of the four components of the Conference Board's Coincident Economic Index and has been tracked by the Federal Reserve since 1919.

For stock investors, IP matters because it directly connects to **corporate earnings**. When factories are running at full capacity, companies are selling more goods, hiring more workers, and generating higher profits. When production contracts, earnings fall — and so do stock prices, usually with a lag.

<!-- expander: What is Industrial Production (INDPRO)? -->
The Industrial Production Index (INDPRO) is published monthly by the Federal Reserve Board. It measures the real output of manufacturing, mining, and electric and gas utilities. The index is set to 100 for the base year 2017. Key features:

- **Monthly frequency** (released ~6 weeks after the reference month)
- **Seasonally adjusted** (SA) — seasonal patterns are removed
- **Real output** — not revenue, but physical quantities produced
- **Covers ~16% of GDP** but is a leading indicator for the broader economy
<!-- /expander -->

### The IP-Equity Connection

Our analysis examines 35 years of data (1990-2025) to test whether IP growth rates predict S&P 500 returns. The economic logic is straightforward:

- **Rising IP** signals expanding manufacturing activity, higher capacity utilization, and growing corporate earnings — bullish for stocks
- **Falling IP** signals contraction, lower utilization, and earnings pressure — bearish for stocks
- The signal operates with a **lag** because IP data is released ~6 weeks after the reference month, and markets may not fully price the information immediately

This is what economists call a **pro-cyclical** relationship: the indicator and the stock market move in the same direction over the business cycle.
"""

render_narrative(SECTION_1)

st.markdown("---")

# --- Regime Analysis ---
st.markdown("### What History Shows: Returns by IP Growth Regime")

load_plotly_chart(
    "indpro_spy_regime_stats",
    fallback_text="SPY Sharpe by IP growth quartile",
    caption=(
        "Equity performance differs dramatically across IP growth regimes. "
        "Stocks perform best during moderate-to-high IP growth (Q2 and Q4), "
        "and worst during deep contractions (Q1)."
    ),
    pair_id="indpro_spy",
)

st.markdown(
    '<div class="narrative-block">'
    "<b>Key finding:</b> The relationship is not perfectly linear. Stocks perform well "
    "during moderate growth (Q2, Sharpe 1.09) and high growth (Q4, Sharpe 1.15), "
    "but poorly during deep contractions (Q1, Sharpe 0.31). The Q3 regime (moderate-high) "
    "has a Sharpe of 0.69 — still positive but below Q2."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- Surprise Finding ---
st.markdown("### The Surprise: A Peak-Cycle Warning")

st.warning(
    "**Counter-intuitive finding:** While the overall relationship is pro-cyclical, "
    "the IP z-score (how far IP is from its long-term trend) shows a *negative* "
    "relationship with 12-month forward returns. When IP is well above its 5-year "
    "trend, future returns tend to be *lower*.\n\n"
    "**Interpretation:** This is a **peak-cycle effect**. At cycle highs, growth "
    "is unsustainable and mean-reverts. Investors who buy at the peak of industrial "
    "activity tend to underperform. This is consistent with Fama & French (1989): "
    "business conditions predict stock returns, but the relationship is nuanced."
)

# --- Transition ---
st.markdown("---")
render_transition(
    "History and economic logic suggest a real connection between factory output and stock returns. "
    "But does the data confirm this statistically? We ran 9 different econometric models to find out."
)

st.page_link("pages/5_indpro_spy_evidence.py", label="Continue to The Evidence", icon="🔬")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12 | "
    "432 monthly observations"
    "</div>",
    unsafe_allow_html=True,
)
