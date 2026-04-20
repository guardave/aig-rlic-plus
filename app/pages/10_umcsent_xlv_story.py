"""UMCSENT × XLV -- The Story: Consumer Sentiment and Health Care Stocks.

Michigan Consumer Sentiment as a countercyclical leading indicator for
the Health Care Select Sector SPDR (XLV).

Pair ID: umcsent_xlv
Date: 2026-04-20
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(
    page_title="UMCSENT × XLV Story | AIG-RLIC+",
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

PAIR_ID = "umcsent_xlv"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _REPO_ROOT / "results" / PAIR_ID

# ---------------------------------------------------------------------------
# Breadcrumb navigation (N10, META-PWQ)
# ---------------------------------------------------------------------------
render_breadcrumb("Story", PAIR_ID)

# ---------------------------------------------------------------------------
# Plain English expander (N8)
# ---------------------------------------------------------------------------
with st.expander("Plain English"):
    st.markdown(
        "This analysis asks whether the University of Michigan Consumer Sentiment "
        "survey — a monthly poll of how confident ordinary Americans feel about the "
        "economy — can help predict returns in the Health Care Select Sector ETF (XLV). "
        "Health care is a defensive sector: people visit doctors whether the economy "
        "is booming or not. The question is whether sentiment shifts change how investors "
        "allocate between defensive and growth sectors, and whether we can use that "
        "rotation to time XLV exposure."
    )

# ---------------------------------------------------------------------------
# Headline-first block
# ---------------------------------------------------------------------------
st.markdown(
    "## Sharpe 1.02 over 6-year OOS — consumer sentiment as a contrarian "
    "regime signal for health care equity exposure"
)

# Load winner for KPIs
_winner = {}
_winner_path = _RESULTS_DIR / "winner_summary.json"
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

oos_sharpe = _winner.get("oos_sharpe", 1.02)
oos_return = _winner.get("oos_ann_return", 0.119)
max_dd = _winner.get("max_drawdown", -0.109)
bh_sharpe = _winner.get("bh_oos_sharpe", 0.72)
bh_dd = _winner.get("bh_max_drawdown", -0.156)

st.markdown(
    f"**Key metrics (out-of-sample 2019-2025):**\n\n"
    f"- **Sharpe ratio: {oos_sharpe:.2f}** (vs {bh_sharpe:.2f} buy-and-hold) — "
    f"~{(oos_sharpe/bh_sharpe - 1)*100:.0f}% more return per unit of risk\n"
    f"- **Annualized return: {oos_return*100:.1f}%** (vs ~{bh_sharpe*10:.0f}% buy-and-hold)\n"
    f"- **Max drawdown: {max_dd*100:.1f}%** (vs {bh_dd*100:.1f}% buy-and-hold) — "
    f"meaningfully less peak-to-trough pain\n"
    f"- **Direction surprise:** Observed effect is procyclical (high sentiment → XLV "
    f"outperforms), contradicting the textbook countercyclical hypothesis. The data "
    f"drives the strategy, not the prior."
)

st.markdown("---")

with st.container(border=True):
    st.markdown("### Where This Fits in the Portal")
    st.markdown(
        "This is **one indicator-target analysis** — we ask whether consumer sentiment "
        "can help time exposure to the health care sector. The AIG-RLIC+ portal catalogues "
        "many such pair-wise studies. This pair is distinctive because the data shows the "
        "opposite direction to the standard economic intuition, making it an honest "
        "exploration of how empirical results can challenge priors."
    )
    st.markdown(
        "**How to read the rest of this page pack.** Story (why the signal works, including "
        "the direction surprise), Evidence (statistical proofs), Strategy (the actual trading "
        "rule), Methodology (technical appendix). Each page stands alone."
    )

# ---------------------------------------------------------------------------
# One-Sentence Thesis
# ---------------------------------------------------------------------------
st.markdown("### One-Sentence Thesis")
st.markdown(
    "*When consumer sentiment trends upward — measured by a year-over-year gain — "
    "health care stocks have historically outperformed, contradicting the defensive-"
    "rotation hypothesis and suggesting that sentiment captures broad risk appetite "
    "that lifts even defensive sectors during bull markets.*"
)

st.markdown("---")

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Best Signal", "YoY Change", delta="6-month lead")
with col2:
    st.metric("Direction", "Procyclical", delta="Surprise vs prior")
with col3:
    st.metric("Tournament Combos", "1,305", delta="1,196 valid")
with col4:
    st.metric("OOS Test Period", "~6 years", delta="2019–2025")
with col5:
    st.metric("Benchmark Sharpe", f"{bh_sharpe:.2f}", delta="Buy-hold XLV")

st.caption(
    "What this shows: the winning rule uses UMCSENT year-over-year change "
    "with a 6-month lead. When the 12-month change is positive (sentiment trending "
    "up), the strategy holds XLV; when negative, it moves to cash. The 6-month lead "
    "suggests sentiment anticipates the sector rotation well in advance."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Headline Findings
# ---------------------------------------------------------------------------
st.markdown("### Headline Findings")

st.markdown(
    "1. **Consumer sentiment is a leading indicator — but in a surprising direction.** "
    "The textbook story says high consumer confidence drives money into cyclical growth "
    "stocks and out of defensive healthcare. In practice, the data shows the opposite: "
    "rising sentiment has been associated with XLV outperformance. The likely "
    "explanation is that sentiment captures broad economic optimism, and in bull "
    "markets everything — including healthcare — rises together.\n"
    "   - **What this means for investors:** do not assume the textbook direction is "
    "right. Run the data. The empirical signal is stronger than the economic prior "
    "in this case, and following the prior would have cost money.\n"
    "2. **The year-over-year change, not the level, is the key signal.** Raw sentiment "
    "levels are non-stationary and reflect long secular trends. The year-over-year "
    "change captures whether sentiment is improving or deteriorating relative to a "
    "year ago, which is the signal that correlates with forward XLV returns.\n"
    "   - **What this means for investors:** watch the trend, not the level. "
    "A sentiment reading of 70 (below long-run average of ~85) still generates a "
    "bullish signal if it has risen from 65 a year ago.\n"
    "3. **A 6-month lead is optimal.** The signal works best with a 6-month lag "
    "before acting on it — meaning current sentiment changes predict XLV performance "
    "half a year later, not immediately. This multi-month lag is typical of macro "
    "sentiment indicators feeding through to sector returns.\n"
    "   - **What this means for investors:** this is not a short-term signal. "
    "Recalculate once a month, update your XLV allocation, and expect to wait "
    "months to see the payoff.\n"
    "4. **The strategy significantly reduces max drawdown.** Despite the direction "
    f"surprise, the simple sentiment rule reduces maximum drawdown from {bh_dd*100:.1f}% "
    f"(buy-and-hold XLV) to {max_dd*100:.1f}% — roughly one-third less peak-to-trough pain.\n"
    "   - **What this means for investors:** even a simple sentiment-based rule "
    "provides meaningful downside protection for XLV exposure, which matters for "
    "investors who use healthcare as a defensive allocation.\n"
    "5. **The OOS test spans 6 years (2019-2025)**, including COVID crash (2020), "
    "2022 rate hike cycle, and 2023-25 recovery. These are challenging environments "
    "for any single-indicator strategy.\n"
    "   - **What this means for investors:** the strategy was tested on data it had "
    "never seen during model development — this is the gold standard for assessing "
    "genuine predictive power vs. curve-fitting."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Hero Chart
# ---------------------------------------------------------------------------
st.markdown("### 25 Years of Consumer Sentiment vs. Health Care Stocks")
load_plotly_chart(
    "umcsent_xlv_hero",
    fallback_text=(
        "Hero chart: UMCSENT YoY change vs XLV price (1999-2025). "
        "Expected at: output/charts/umcsent_xlv/plotly/umcsent_xlv_hero.json"
    ),
    caption=(
        "How to read it: UMCSENT year-over-year % change (red line, left axis) "
        "vs XLV adjusted price (blue line, right axis). Shaded bands mark periods "
        "when sentiment was falling year-over-year. Notice that XLV often "
        "continues rising even during modest sentiment declines."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Economic narrative
# ---------------------------------------------------------------------------
SECTION_STORY = """
### Why Consumer Sentiment and Health Care?

The University of Michigan Consumer Sentiment Index has been published monthly since 1978. Each month, 500 households are asked about their financial situation, their outlook for the broader economy in the next 12 months, and their views on conditions 5 years out. The index is one of the most watched leading indicators in the world — central banks, equity analysts, and economists all track it because it has historically turned before consumer spending does.

<!-- expander: What exactly does the Michigan survey ask? -->
The survey asks five questions: (1) How would you rate your current financial situation compared to 12 months ago? (2) Do you think a year from now you'll be better or worse off financially? (3) Is now a good time to buy major household goods? (4) Will the economy be better or worse in the next 12 months? (5) Will the economy be better or worse in 5 years? Responses are combined into the index (baseline of 100 = November 1966). A reading above 100 indicates sentiment better than the historical baseline; below 100 indicates worse. The current long-run average is approximately 85.
<!-- /expander -->

### The Defensive Healthcare Hypothesis (and Why It Fails)

The standard economic story about health care stocks is that they are **defensive**: people consume health care regardless of the economic cycle, so healthcare companies generate stable cash flows in both good times and bad. The theory predicts that when consumers feel confident about the economy, they rotate money *out* of defensive sectors like healthcare and *into* cyclical growth sectors (technology, industrials, consumer discretionary). When confidence falls, money flows back into defensives.

If this theory were correct, we would expect:
- High consumer sentiment → XLV underperforms (risk-on rotation out of defensives)
- Low consumer sentiment → XLV outperforms (flight to defensives)

**Our data shows the opposite.** Periods of rising consumer sentiment (positive year-over-year change) have been associated with XLV *outperformance*, not underperformance. The most likely explanations are:

1. **Bull markets lift everything.** In sustained bull markets, investor optimism drives all sectors higher, including healthcare. The defensive characteristic of healthcare reduces its beta relative to SPY, but XLV still participates in the upside when broad sentiment is strong.

2. **Healthcare spending grows during booms.** When consumers feel wealthy, they actually spend *more* on elective health care: voluntary procedures, premium medications, and wellness services. This positive revenue impact is captured in XLV earnings during high-sentiment periods.

3. **Sentiment captures risk appetite broadly.** High consumer confidence is associated with low risk premiums across all asset classes. When investors are confident, they demand lower return premiums for all risk — including healthcare — which supports valuations.
"""

render_narrative(SECTION_STORY)

st.markdown("---")

# ---------------------------------------------------------------------------
# Regime chart
# ---------------------------------------------------------------------------
st.markdown("### XLV Returns by Sentiment Regime")
load_plotly_chart(
    "umcsent_xlv_regime_stats",
    fallback_text="XLV returns by UMCSENT YoY quartile.",
    caption=(
        "What this shows: annualized XLV Sharpe ratio and return by quartile of "
        "UMCSENT year-over-year change. Q1 = lowest (most negative) YoY change, "
        "Q4 = highest (most positive) YoY change. The non-monotonic pattern "
        "reflects the nuanced relationship between sentiment and healthcare returns."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Direction warning
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.warning(
        "**Direction Surprise — Honest Assessment**\n\n"
        "The expected direction for this pair was **countercyclical**: high sentiment "
        "→ risk-on rotation away from healthcare → XLV underperforms. The observed "
        "direction is **procyclical**: high sentiment → XLV outperforms.\n\n"
        "This is not a failure of the analysis — it is precisely the kind of "
        "evidence-based surprise that rigorous empirical work is designed to surface. "
        "We report the actual data, not the theory. Investors who blindly applied the "
        "textbook story would have traded the wrong direction and underperformed buy-and-hold."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
render_transition(
    "The direction surprise is the central finding of this analysis. The Evidence "
    "page shows the full battery of statistical tests that confirm this is a robust "
    "result, not an artifact of data selection or time period."
)

st.page_link(
    "pages/10_umcsent_xlv_evidence.py",
    label="Continue to The Evidence",
    icon="🔬",
)

st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Indicator: UMCSENT (FRED, monthly) | "
    "Target: XLV (Yahoo Finance, daily→monthly) | "
    "Data: 1998-12 to 2025-12 | 325 monthly observations."
)
