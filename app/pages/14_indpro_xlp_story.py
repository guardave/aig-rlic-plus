"""Pair 14 — The Story: Industrial Production vs Consumer Staples (XLP).

This page tells the economic story of why rising industrial production
tends to be bearish for consumer staples ETF (XLP) — the classic
defensive sector rotation mechanism.
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
    page_title="INDPRO × XLP Story | AIG-RLIC+",
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

PAIR_ID = "indpro_xlp"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _REPO_ROOT / "results" / PAIR_ID

# ---------------------------------------------------------------------------
# Breadcrumb navigation
# ---------------------------------------------------------------------------
render_breadcrumb("Story", PAIR_ID)

# ---------------------------------------------------------------------------
# Load winner summary
# ---------------------------------------------------------------------------
_winner = {}
_winner_path = _RESULTS_DIR / "winner_summary.json"
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

_oos_sharpe = _winner.get("oos_sharpe", "N/A")
_bh_sharpe = _winner.get("bh_sharpe", "N/A")
_oos_return_pct = round(_winner.get("oos_ann_return", 0) * 100, 1) if _winner else "N/A"
_oos_dd_pct = round(_winner.get("oos_max_drawdown", 0) * 100, 1) if _winner else "N/A"
_bh_dd_pct = round(_winner.get("bh_max_drawdown", 0) * 100, 1) if _winner else "N/A"
_oos_start = _winner.get("oos_start", "2019-01")[:7]

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("The Story: When the Factory Hums, Staples Stumble")
st.markdown(
    "*Does industrial activity predict returns in the defensive consumer staples sector?*"
)
st.markdown("---")

# ---------------------------------------------------------------------------
# Plain English expander (META-ELI5)
# ---------------------------------------------------------------------------
with st.expander("Plain English: What is this about?"):
    st.markdown(
        "When factories are running at full speed and the economy is growing, "
        "investors tend to shift money away from boring, defensive stocks like "
        "soap and cereal companies — and toward more exciting, growth-oriented "
        "ones. This research asks: can we use factory output data to predict "
        "when that rotation happens? It turns out you can — at least partially. "
        "When industrial production is accelerating, consumer staples ETF (XLP) "
        "tends to lag behind. The signal isn't perfect, but it can help reduce "
        "how badly you lose during bad periods."
    )

# ---------------------------------------------------------------------------
# Headline block
# ---------------------------------------------------------------------------
st.markdown(
    f"## Sharpe {_oos_sharpe} over 7-year OOS — factory output momentum "
    f"as a defensive sector timing signal"
)

st.markdown(
    f"**Key metrics (out-of-sample {_oos_start}–2025):**\n\n"
    f"- **Sharpe ratio: {_oos_sharpe}** (vs {_bh_sharpe} buy-and-hold XLP)\n"
    f"- **Annualized return: {_oos_return_pct}%** with drawdown management\n"
    f"- **Max drawdown: {_oos_dd_pct}%** (vs {_bh_dd_pct}% buy-and-hold XLP)"
)

st.markdown("---")

with st.container(border=True):
    st.markdown("### Where This Fits in the Portal")
    st.markdown(
        "This is **one indicator-target analysis** — we ask whether INDPRO momentum "
        "can help time exposure to the consumer staples sector (XLP). Consumer staples "
        "are defensive stocks: companies that sell essential goods like food, beverages, "
        "and household products. They tend to outperform when the economy weakens and "
        "underperform when the economy accelerates — the opposite of the broad market."
    )
    st.markdown(
        "**How to read the rest of this page pack.** You'll read the **Story** first "
        "(the economic logic), then the **Evidence** (statistical proofs), then the "
        "**Strategy** (the actual trading rule), then the **Methodology** (technical appendix). "
        "Each page stands alone."
    )

# ---------------------------------------------------------------------------
# One-Sentence Thesis
# ---------------------------------------------------------------------------
st.markdown("### One-Sentence Thesis")
st.markdown(
    "*Rising industrial production signals economic expansion, which triggers rotation "
    "away from defensive consumer staples — and watching that signal can help investors "
    "avoid the worst periods in XLP while capturing the defensive upside during slowdowns.*"
)

st.markdown("---")

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("OOS Sharpe", str(_oos_sharpe), delta=f"vs {_bh_sharpe} B&H")
with col2:
    st.metric("OOS Return", f"{_oos_return_pct}%", delta="annualized")
with col3:
    st.metric("Max Drawdown", f"{_oos_dd_pct}%", delta=f"vs {_bh_dd_pct}% B&H", delta_color="inverse")
with col4:
    st.metric("Signal", "IP Acceleration", delta="Winner feature")
with col5:
    st.metric("OOS Period", "7 years", delta=f"{_oos_start}–2025")

st.caption(
    "What this shows: the tournament winner uses IP acceleration (the rate of change "
    "of MoM IP growth) as the signal, with a 3-month lead time. "
    "The countercyclical orientation means we hold XLP when IP momentum is slowing — "
    "the defensive trade."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Hero Chart
# ---------------------------------------------------------------------------
st.markdown("### 27 Years of Industrial Production vs. Consumer Staples (XLP)")
load_plotly_chart(
    "indpro_xlp_hero",
    fallback_text=(
        "Hero chart: INDPRO YoY growth vs XLP price (1998-2025) with "
        "industrial contraction bands. Expected at: "
        "output/charts/indpro_xlp/plotly/indpro_xlp_hero.json"
    ),
    caption=(
        "How to read it: dual-axis view — IP YoY growth (left, red) and XLP "
        "price (right, blue) on a common time axis. Red shaded bands mark "
        "industrial contraction periods (YoY growth < 0). Notice how XLP "
        "often holds up or outperforms during contractions — the defensive effect."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Economic story section
# ---------------------------------------------------------------------------
SECTION_STORY = """
### Why Should XLP Investors Care About Factory Output?

Consumer staples are the ultimate defensive sector. Companies like Procter & Gamble, Coca-Cola, and Walmart sell products people need regardless of the economic cycle — toothpaste, soft drinks, and groceries don't disappear during recessions. This is exactly why they behave differently from the broad market.

When the economy is expanding (factories busy, unemployment low, corporate earnings rising), investors typically shift money from defensive sectors toward growth-oriented ones — technology, industrials, consumer discretionary. This "rotation away from defensives" causes XLP to underperform relative to the broad market.

When the economy contracts (factories idle, layoffs rising, earnings falling), the rotation reverses. Investors seek safety in the reliable cash flows of staples companies. XLP outperforms.

<!-- expander: What is XLP and what does it hold? -->
XLP (Consumer Staples Select Sector SPDR Fund) is an exchange-traded fund that tracks the S&P 500 Consumer Staples sector. It holds roughly 35-40 large-cap US companies in food, beverages, tobacco, household products, and personal care. Top holdings include Procter & Gamble, Coca-Cola, PepsiCo, Costco, and Walmart. The ETF has been trading since December 1998.

Key characteristics:
- **Beta < 1**: Less volatile than the broad market (historically ~0.55-0.65)
- **Dividend yield**: Higher than average — staples companies are reliable dividend payers
- **Sector concentration**: Top 5 holdings represent ~45% of the ETF's weight
- **Defensive behavior**: Historically outperforms in recessions and underperforms in bull markets
<!-- /expander -->

### The INDPRO-XLP Connection

Our analysis tests whether Industrial Production growth rates predict XLP returns. The economic logic operates through two channels:

**Channel 1: The Rotation Mechanism.** Rising IP signals expanding manufacturing activity. When IP accelerates, institutional investors — pension funds, endowments, hedge funds — rotate their equity exposure away from defensive sectors (staples, utilities, healthcare) toward cyclical sectors (industrials, materials, technology). This rotation reduces demand for XLP shares, depressing its relative performance.

**Channel 2: The Earnings Effect.** Consumer staples companies are relatively insulated from IP cycles because their revenues depend on consumer spending, not industrial production. But during strong expansions, raw material costs rise (packaging, agricultural inputs), squeezing staples margins, while revenues remain flat. This creates a mild earnings headwind that stock prices gradually reflect.

The combined prediction: **rising IP → XLP underperformance; falling IP → XLP outperformance.** This is the opposite of what we expect for the broad S&P 500, where rising IP is bullish. XLP is the defensive case.

### The Acceleration Signal

Our tournament found that the winning signal is not IP *level* or IP *YoY growth*, but IP *acceleration* — the change in the month-over-month growth rate. This is mathematically the second derivative of the production index: not "how fast are factories growing?" but "is that growth speeding up or slowing down?"

Why acceleration? Because financial markets are forward-looking. By the time IP *level* or *YoY growth* signal a regime shift, the rotation has already begun. IP acceleration, however, can detect the early inflection point — the moment growth begins to slow before a full contraction arrives, or the moment recovery begins to gain steam.

<!-- expander: How does IP acceleration differ from IP momentum? -->
**IP Momentum (MoM):** Monthly percentage change in the IP index. Measures current expansion or contraction speed. Positive = factories expanding, negative = contracting.

**IP Acceleration:** The change in MoM percentage change from one month to the next. Positive acceleration = expansion is speeding up. Negative acceleration = expansion is slowing (may signal approaching peak or contraction).

The acceleration signal is inherently noisier than level or momentum signals (because differentiation amplifies high-frequency variation), which is why it benefits from a smoothing lag (L3 = 3-month lead in the winner). But its early-warning property outweighs the noise cost in the OOS period.
<!-- /expander -->
"""

render_narrative(SECTION_STORY)

st.markdown("---")

# ---------------------------------------------------------------------------
# Regime Chart
# ---------------------------------------------------------------------------
st.markdown("### What History Shows: XLP Returns by IP Growth Regime")
load_plotly_chart(
    "indpro_xlp_regime_stats",
    fallback_text=(
        "XLP Sharpe ratio by INDPRO YoY growth quartile. "
        "Expected at: output/charts/indpro_xlp/plotly/indpro_xlp_regime_stats.json"
    ),
    caption=(
        "What this shows: XLP annualized Sharpe ratio in each of the four IP growth "
        "quartile regimes. Q1 (lowest IP growth) and Q2 tend to be where XLP earns its "
        "keep; Q3 and Q4 (highest IP growth) are less favorable for this defensive ETF."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# The Countercyclical Nuance
# ---------------------------------------------------------------------------
SECTION_NUANCE = """
### The Nuance: It Is Not a Perfect Inverse of the S&P 500

If XLP perfectly mirrored the inverse of industrial production, building a profitable strategy would be trivial. Reality is more complex:

- **XLP still earns positive absolute returns** in expansion periods — defensive stocks grow earnings over time even if they rotate out temporarily. The countercyclical relationship is about *relative* performance, not absolute losses.
- **The relationship has regime-dependent strength.** During deep contractions (Q1 of IP growth), XLP's defensive properties shine. During mild slowdowns, the advantage is more modest.
- **Dividend yield provides a floor.** XLP's historically higher-than-market dividend yield (around 2.5-3%) cushions performance during mild underperformance periods.
- **COVID distorted the signal.** The COVID shock (April 2020: IP -12.7% MoM) was extreme and indiscriminate — everything fell, and then everything bounced, overwhelming normal regime patterns.

The practical implication for strategy design: **a simple "hold XLP when IP contracts" rule misses important nuance.** The winning strategy instead uses IP acceleration with a rolling percentile threshold, which is more adaptive to the current IP regime.
"""

render_narrative(SECTION_NUANCE)

st.markdown("---")

# ---------------------------------------------------------------------------
# Scope note
# ---------------------------------------------------------------------------
st.markdown(
    "**Scope note.** This page pack analyzes only the INDPRO → XLP relationship. "
    "XLP performance also responds to interest rates (higher rates hurt dividend "
    "stocks), consumer sentiment, and commodity input costs — but each of those has "
    "its own separate analysis in the portal. Here the lens stays on industrial "
    "production as the single predictor."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
render_transition(
    "Economic logic suggests rising factory output signals rotation away from defensive "
    "consumer staples. We ran 9 econometric methods to test whether the data bears this out."
)

st.page_link(
    "pages/14_indpro_xlp_evidence.py",
    label="Continue to The Evidence",
    icon="🔬",
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Data: INDPRO (FRED, 1998-01 to 2025-12) | XLP (Yahoo Finance, 1998-12 to 2025-12) | "
    "336 monthly observations"
)
