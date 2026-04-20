"""Pair 14 — The Evidence: INDPRO → XLP Statistical Analysis.

8-element template blocks per SOP 3.9.
Pair ID: indpro_xlp
Date: 2026-04-20

Wave 10D fix: restructured from flat 4-tab layout to Level 1 / Level 2
hierarchy matching the reference template (umcsent_xlv_evidence.py).
"""

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="INDPRO × XLP Evidence | AIG-RLIC+",
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

PAIR_ID = "indpro_xlp"

render_breadcrumb("Evidence", PAIR_ID)

with st.expander("Plain English"):
    st.markdown(
        "This section shows the statistical evidence for the relationship between "
        "industrial production (INDPRO) and consumer staples ETF (XLP) returns. "
        "Multiple methods all converge on the same direction: when industrial production "
        "accelerates, XLP tends to underperform — investors rotate away from defensive "
        "staples toward cyclical growth sectors. The winning signal (IP acceleration) "
        "works because markets are forward-looking: the inflection point in factory "
        "output growth anticipates the sector rotation before the full level shift occurs."
    )

st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We subjected 27 years of monthly data to multiple complementary statistical methods. "
    "Each is designed to test a different aspect of the INDPRO-XLP relationship. "
    "All converge on the same direction: countercyclical — rising IP is bearish for XLP, "
    "falling IP is bullish for XLP.*"
)
st.markdown("---")

st.markdown(
    "Each method follows the same 8-part structure: what the method is, the question "
    "it answers, how to read the chart, what we observe, deeper technical detail, "
    "economic interpretation, and the key message. Read in order for the full picture, "
    "or skip to the **Key message** lines for a quick summary."
)
st.markdown("---")


# ---------------------------------------------------------------------------
# 8-Element Render Helper (SOP 3.9)
# ---------------------------------------------------------------------------
REQUIRED_ELEMENTS = [
    "method_name", "method_theory", "question", "how_to_read",
    "observation", "interpretation", "key_message",
]


def render_method_block(content: dict):
    missing = [k for k in REQUIRED_ELEMENTS if not content.get(k)]
    if missing:
        st.error(
            f"Method block incomplete: missing required element(s) {missing}. "
            "Gate failure per SOP Rule 3.9.\n\n"
            "Plain English: this evidence block is missing required parts and was "
            "not rendered to avoid showing an incomplete write-up."
        )
        return

    method_name = content["method_name"]
    chart_status = content.get("chart_status", "ready")

    why = content.get("why_this_matters")
    if why:
        st.markdown(f"**Why this matters:** {why}")

    st.markdown(f"### {method_name}")
    st.markdown(content["method_theory"])
    st.markdown(f"> *{content['question']}*")
    st.markdown(f"**How to read it:** {content['how_to_read']}")

    chart_name = content.get("chart_name")
    if chart_status == "ready" and chart_name:
        load_plotly_chart(
            chart_name,
            pair_id=PAIR_ID,
            caption=content.get("chart_caption", ""),
            fallback_text=(
                f"{method_name} chart — expected at "
                f"output/charts/{PAIR_ID}/plotly/{chart_name}.json"
            ),
        )
    else:
        st.warning(
            "Chart pending — method block rendered from narrative only.\n\n"
            "Plain English: the chart for this analysis has not been generated yet. "
            "The interpretation below is based on the underlying statistics."
        )

    st.markdown(f"**What this shows:** {content['observation']}")

    deep_title = content.get("deep_dive_title")
    deep_content = content.get("deep_dive_content")
    if deep_title and deep_content:
        with st.expander("Deeper dive"):
            st.markdown(f"*{deep_title}*\n\n{deep_content}")

    st.markdown(f"**Why this matters:** {content['interpretation']}")
    st.info(f"**Key message:** {content['key_message']}")


# ---------------------------------------------------------------------------
# Method Blocks
# ---------------------------------------------------------------------------

CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "A **Pearson correlation** measures the linear relationship between two variables "
        "on a scale from -1 (perfectly opposing) to +1 (perfectly aligned). We test "
        "multiple INDPRO-derived signals (level, YoY growth, MoM change, z-score, "
        "acceleration) against XLP forward returns at four horizons (1M, 3M, 6M, 12M). "
        "A rolling correlation view shows how the relationship has evolved over time."
    ),
    question=(
        "Do any INDPRO-derived signals show a statistically meaningful linear "
        "relationship with future XLP returns — and in which direction?"
    ),
    how_to_read=(
        "The chart shows rolling 12M and 36M Pearson correlations between INDPRO YoY "
        "growth and XLP monthly return over the full sample. A consistently negative "
        "reading confirms the countercyclical hypothesis: higher IP growth coincides "
        "with weaker XLP returns. The dashed vertical line marks the start of the "
        "out-of-sample period (2019-01)."
    ),
    chart_name="indpro_xlp_correlations",
    chart_caption=(
        "What this shows: rolling Pearson correlation between INDPRO YoY growth and "
        "XLP monthly return. Negative values (below zero) confirm countercyclical "
        "behavior — rising industrial production is associated with weaker consumer "
        "staples performance. The relationship has been persistent but not constant."
    ),
    observation=(
        "Rolling correlations are predominantly negative across the full sample, "
        "confirming the countercyclical hypothesis. The 12M rolling correlation "
        "oscillates between roughly -0.4 and +0.2, with the most negative readings "
        "during industrial expansions. The static Pearson correlation table shows "
        "the IP z-score has the strongest link to 12M forward XLP returns "
        "(r=-0.187, p=0.002). The acceleration signal shows weaker point correlation "
        "but higher predictive utility in the tournament — consistent with a "
        "nonlinear, threshold-based relationship."
    ),
    deep_dive_title="Why does IP z-score outperform IP level in static correlations?",
    deep_dive_content=(
        "The z-score normalizes the level of IP growth relative to its recent history, "
        "which removes the long-run trend in industrial production. Over 27 years, IP "
        "has a mild upward trend, so the raw level is partly a proxy for time. The "
        "z-score, by standardizing against a rolling window, captures whether current "
        "production is *unusually* high or low relative to recent norms — which is the "
        "economically relevant signal for sector rotation decisions. Investors rotate "
        "away from defensives not when IP is high in absolute terms, but when it is "
        "high relative to recent expectations."
    ),
    interpretation=(
        "Correlation analysis confirms a real countercyclical link between IP signals "
        "and XLP forward returns. The relationship is most pronounced at the 12-month "
        "horizon and for normalized signals (z-score). The rolling correlation view "
        "shows the relationship is persistent but regime-dependent — it strengthens "
        "during clear industrial cycles and weakens during idiosyncratic shocks (COVID)."
    ),
    key_message=(
        "INDPRO z-score shows a statistically significant negative correlation with "
        "12-month forward XLP returns (r=-0.187, p=0.002): higher industrial production "
        "relative to recent history is associated with XLP underperformance — "
        "the classic defensive rotation signal."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "**Granger causality** asks whether past INDPRO values improve forecasts of "
        "future XLP returns, above what XLP's own recent history already predicts. "
        "We test both directions (INDPRO → XLP and XLP → INDPRO) at lags 1-6 months, "
        "using F-tests on augmented VAR regressions with HC3 robust standard errors. "
        "The cross-correlation function (CCF) serves as the primary visual for "
        "lead-lag structure."
    ),
    question=(
        "Does industrial production carry information about future consumer staples "
        "equity returns that is not already priced into the XLP return series itself — "
        "and at what lag does this predictive content peak?"
    ),
    how_to_read=(
        "The CCF chart shows bars at lags -12 to +12 months. Negative lags mean "
        "INDPRO leads XLP (IP first, then XLP reacts). Bars outside the dashed "
        "95% confidence bands are statistically significant. A cluster of significant "
        "negative bars would confirm IP as a leading indicator for XLP."
    ),
    chart_name="indpro_xlp_ccf",
    chart_caption=(
        "What this shows: cross-correlation function between INDPRO YoY growth "
        "and XLP monthly return at lags -12 to +12 months. Red bars are statistically "
        "significant at 95% confidence. Bars at negative lags indicate IP leading XLP."
    ),
    observation=(
        "The CCF confirms that INDPRO carries predictive content for XLP at negative "
        "lags (IP leading XLP), with the most significant bars at lags -1 to -6 months. "
        "INDPRO is a coincident indicator (released with a 6-week lag), so the practical "
        "tradable lead comes from the publication lag rather than true economic advance. "
        "The formal Granger causality tests show INDPRO YoY Granger-causes XLP returns "
        "at lags 1-3 (p < 0.05). The reverse direction (XLP → INDPRO) is not "
        "significant, confirming the directional relationship."
    ),
    deep_dive_title="If INDPRO is a coincident indicator, how can it be used predictively?",
    deep_dive_content=(
        "INDPRO measures current industrial output, not future output. However, "
        "two sources of practical predictive content exist. First, publication lag: "
        "INDPRO for month T is released roughly 6 weeks later, giving investors "
        "a window to act on confirmed industrial acceleration before equity prices "
        "fully reflect it. Second, momentum persistence: IP acceleration in month T "
        "tends to continue for 2-3 months, creating a short-lived lead for the "
        "portfolio signal. The tournament winner exploits the publication lag by "
        "using a 3-month lead parameter (L3), which effectively says 'act on data "
        "confirmed 3 months ago but still informative about the current regime.'"
    ),
    interpretation=(
        "Industrial production Granger-causes XLP returns at lags 1-3 months, "
        "while XLP does not Granger-cause INDPRO. The one-directional pattern is "
        "economically sensible: factory output feeds through to sector rotation "
        "over weeks to months as institutional investors rebalance, but equity "
        "prices do not drive manufacturing decisions."
    ),
    key_message=(
        "INDPRO leads XLP at 1-3 month lags in Granger causality tests — "
        "a one-way relationship consistent with industrial output as an input to "
        "sector rotation decisions, not a consequence of equity performance."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Descriptive Statistics)",
    method_theory=(
        "We sort all monthly observations into four quartiles based on the INDPRO "
        "acceleration signal and compute full return statistics for XLP in each "
        "quartile. This is the simplest possible regime test: does XLP performance "
        "differ systematically across IP acceleration regimes, without any "
        "model-imposed structure?"
    ),
    question=(
        "If we had done nothing more sophisticated than 'hold XLP when IP is "
        "decelerating and move to cash when IP is accelerating,' how would "
        "that strategy have performed across historical regimes?"
    ),
    how_to_read=(
        "The chart shows annualized Sharpe ratio and return for XLP in each quartile "
        "of the INDPRO signal. Q1 = lowest signal values (IP decelerating most). "
        "Q4 = highest signal values (IP accelerating most). A clear gradient from "
        "Q1 (highest XLP Sharpe) to Q4 (lowest) would confirm the countercyclical "
        "defensive rotation hypothesis."
    ),
    chart_name="indpro_xlp_regime_stats",
    chart_caption=(
        "What this shows: annualized XLP Sharpe ratio and return by quartile "
        "of the INDPRO acceleration signal. Q1 = IP decelerating most (best XLP "
        "regime), Q4 = IP accelerating most (worst XLP regime). The gradient "
        "reveals the countercyclical relationship."
    ),
    observation=(
        "The regime statistics show a clear gradient confirming the countercyclical "
        "hypothesis: XLP earns its highest risk-adjusted returns in Q1 and Q2 (low "
        "or negative IP acceleration), while Q3 and Q4 (strong IP acceleration) "
        "are associated with the weakest XLP Sharpe ratios. The OOS strategy "
        "(Sharpe 1.1147, annualized return 14.1%, max drawdown -13.5% over 84 months) "
        "exploits precisely this regime differential by holding XLP only when the "
        "INDPRO acceleration signal is below the 0.75 threshold (upper quartile rule)."
    ),
    deep_dive_title="Why does the 0.75 threshold outperform a simple median split?",
    deep_dive_content=(
        "The tournament tested 7 threshold methods including percentile splits at "
        "0.25, 0.50, and 0.75 (upper quartile). The 0.75 upper quartile threshold "
        "won because XLP's defensive properties are most consistently present across "
        "a broad range of IP conditions — the asset class is defensive even in mild "
        "expansions. The signal is most useful for identifying the *extreme* IP "
        "acceleration regime (top quartile) when the rotation away from defensives "
        "is strongest and most sustained. A median split generates too many false "
        "exits from XLP during normal expansionary months where the defensive "
        "benefit is still available."
    ),
    interpretation=(
        "The regime analysis confirms the countercyclical direction: Q1 (IP "
        "decelerating) is the best regime for XLP on a risk-adjusted basis, while "
        "Q4 (IP strongly accelerating) is the worst. The strategy captures this "
        "by using an upper-quartile threshold (0.75) to identify only the most "
        "adverse regime for XLP, staying invested otherwise."
    ),
    key_message=(
        "IP acceleration above the 75th percentile (Q4) is the worst regime for "
        "XLP returns. The tournament winner exploits this by moving to cash only "
        "in the top IP quartile — holding XLP through all other conditions and "
        "achieving OOS Sharpe of 1.1147 vs 0.9 buy-and-hold."
    ),
)


# ---------------------------------------------------------------------------
# Tab Layout (Level 1: Basic, Level 2: Advanced)
# ---------------------------------------------------------------------------
st.markdown(
    "Evidence is organized in two tiers. **Level 1** covers basic correlations and "
    "cross-correlations (Granger causality). **Level 2** adds regime analysis."
)
st.markdown("")

tier1, tier2 = st.tabs(
    ["Level 1 — Basic Analysis", "Level 2 — Advanced Analysis"]
)

with tier1:
    sub_corr, sub_granger = st.tabs(["Correlation", "Granger Causality"])
    with sub_corr:
        render_method_block(CORRELATION_BLOCK)
    with sub_granger:
        render_method_block(GRANGER_BLOCK)

with tier2:
    sub_regime, = st.tabs(["Regime Analysis"])
    with sub_regime:
        render_method_block(REGIME_BLOCK)

# ---------------------------------------------------------------------------
# Tournament pointer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### The Combinatorial Tournament")
st.markdown(
    "We tested combinations of signals (IP level, YoY, MoM, z-score, acceleration), "
    "thresholds (7 methods including percentile cuts), strategies (Long/Cash, "
    "Long/Short), and lead times (0-6 months). These were ranked by out-of-sample "
    "Sharpe ratio over 2019-2025. The winning combination: "
    "**IP acceleration signal, 0.75 percentile threshold, Long/Cash, L3 lead**, "
    "producing OOS Sharpe 1.1147 vs 0.90 buy-and-hold XLP."
)
st.caption(
    f"What this shows: full leaderboard at `results/{PAIR_ID}/tournament_results.csv`."
)

st.markdown("---")
st.markdown(
    "**Transition:** Multiple statistical methods confirm the countercyclical "
    "relationship: rising industrial production signals rotation away from defensive "
    "consumer staples. Now: what does the winning strategy actually do, "
    "and how has it performed out-of-sample?"
)

st.page_link(
    "pages/14_indpro_xlp_strategy.py",
    label="Continue to The Strategy",
    icon="🎯",
)

st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Data: INDPRO (FRED) + XLP (Yahoo Finance) | "
    "1998-01 to 2025-12 | 336 monthly observations."
)
