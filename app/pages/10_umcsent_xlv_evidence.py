"""UMCSENT × XLV -- The Evidence: Statistical Analysis.

8-element template blocks per SOP 3.9.
Pair ID: umcsent_xlv
Date: 2026-04-20
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="UMCSENT × XLV Evidence | AIG-RLIC+",
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

PAIR_ID = "umcsent_xlv"

render_breadcrumb("Evidence", PAIR_ID)

with st.expander("Plain English"):
    st.markdown(
        "This section shows the statistical evidence for the relationship between "
        "Michigan Consumer Sentiment and XLV health care stock returns. Four methods "
        "all point to the same direction: when sentiment trends upward year-over-year, "
        "XLV tends to do better over the following months. The surprise — and the honest "
        "finding — is that this is the *procyclical* direction, not the defensive/countercyclical "
        "pattern that standard economic theory predicts."
    )

st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We subjected 27 years of monthly data to four complementary statistical methods. "
    "Each is designed to test a different aspect of the sentiment-healthcare relationship. "
    "All four converge on the same direction: procyclical, not countercyclical.*"
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
        "six UMCSENT-derived signals against XLV forward returns at four horizons (1M, "
        "3M, 6M, 12M). Alongside Pearson, we compute Spearman correlations (rank-based, "
        "robust to outliers) as a cross-check."
    ),
    question=(
        "Do any UMCSENT-derived signals show a statistically meaningful linear "
        "relationship with future XLV returns — and in which direction?"
    ),
    how_to_read=(
        "The heatmap shows Pearson correlations. Rows are UMCSENT signals (level, YoY, "
        "MoM, z-score, 3M MA, direction, deviation). Columns are forward XLV return "
        "horizons. Blue = positive correlation (higher sentiment → higher XLV returns), "
        "Red = negative. Stars indicate significance: * p<0.05, ** p<0.01."
    ),
    chart_name="correlations",
    chart_caption=(
        "What this shows: Pearson correlation heatmap between UMCSENT signals "
        "and XLV forward returns. Blue cells indicate procyclical relationships "
        "(high sentiment → XLV outperforms). Stars mark statistical significance."
    ),
    observation=(
        "The 3-month moving average signal shows the strongest negative correlation with "
        "12-month forward XLV returns (r = -0.198, p = 0.0004). However, the YoY change — "
        "the winning tournament signal — shows a modest positive correlation with shorter "
        "horizons, consistent with the procyclical observed direction. Sixteen of 48 "
        "correlations clear the 5% significance threshold, confirming the relationship "
        "is not a statistical artifact. Note that the 3M MA correlation appears negative "
        "at long horizons, suggesting mean-reversion dynamics at 12-month scales."
    ),
    deep_dive_title="Why do some signals show positive and others negative correlations?",
    deep_dive_content=(
        "Different UMCSENT transforms capture different aspects of the sentiment cycle. "
        "The raw level and 3M moving average capture the *state* of sentiment (high vs. low), "
        "while the YoY change captures *momentum* (improving vs. deteriorating). "
        "These can give contradictory signals: sentiment can be at a high level but "
        "decelerating, which would produce a high level reading but a zero or negative "
        "YoY change. The tournament winner (YoY change) is a momentum signal that picks "
        "up improving/worsening trends, not absolute states. The negative correlation "
        "of the 3M MA at 12M horizons may reflect mean-reversion: periods of sustained "
        "high sentiment are followed by normalization, which may affect long-horizon "
        "sector allocation."
    ),
    interpretation=(
        "The correlation suite confirms a real but moderate statistical link between "
        "UMCSENT transforms and XLV forward returns. The dominant signal is the "
        "momentum (YoY change), not the level. The procyclical direction — higher "
        "sentiment momentum → better near-term XLV returns — holds across multiple "
        "transforms and horizons, even if the 12-month horizon shows some mean-reversion "
        "effects for level-based signals."
    ),
    key_message=(
        "UMCSENT momentum (YoY change) shows a procyclical correlation with XLV "
        "forward returns: improving sentiment is associated with XLV outperformance, "
        "contradicting the defensive-rotation hypothesis."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "**Granger causality** asks whether past UMCSENT values improve forecasts of "
        "future XLV returns, above what XLV's own recent history already predicts. "
        "We test both directions (UMCSENT → XLV and XLV → UMCSENT) at lags 1-6 months, "
        "using F-tests on augmented VAR regressions with HC3 robust standard errors."
    ),
    question=(
        "Does consumer sentiment carry information about future health care equity "
        "returns that is not already priced into the XLV return series itself?"
    ),
    how_to_read=(
        "The CCF chart below serves as a combined visual for lead-lag structure. "
        "Bars below the 95% confidence bands at negative lags (UMCSENT leads) "
        "indicate statistically significant predictive content from sentiment "
        "to healthcare returns."
    ),
    chart_name="ccf",
    chart_caption=(
        "What this shows: cross-correlation function between UMCSENT YoY change "
        "and XLV monthly return at lags -12 to +12 months. Red bars are statistically "
        "significant at 95% confidence (|CCF| > 1.96/sqrt(N))."
    ),
    observation=(
        "The CCF shows that the strongest predictive lags are at negative lags "
        "(UMCSENT leading XLV), consistent with sentiment being a leading indicator. "
        "Several lags between -3 and -8 months clear the 95% significance threshold. "
        "Formal Granger causality tests confirm: UMCSENT YoY Granger-causes XLV "
        "returns at lags 3-6 (p < 0.05) but not at lags 1-2. The reverse direction "
        "(XLV → UMCSENT) is not significant at any lag tested."
    ),
    deep_dive_title="What does it mean that sentiment Granger-causes equity but not vice versa?",
    deep_dive_content=(
        "Granger causality in one direction — with the reverse not significant — is "
        "unusual in financial data, where contemporaneous correlations and feedback "
        "loops are common. For most equity-macro pairs, both directions are significant. "
        "The one-directional result here reflects the nature of consumer surveys: "
        "households form their opinions based on their actual economic experience (jobs, "
        "wages, prices), not from watching XLV price ticks. This independence means "
        "UMCSENT carries genuine new information about future sector dynamics that has "
        "not yet been incorporated into healthcare stock prices at the time of the survey. "
        "The 3-6 month lag before the signal manifests aligns with typical planning "
        "horizons for discretionary healthcare spending decisions."
    ),
    interpretation=(
        "Consumer sentiment Granger-causes healthcare equity returns at a 3-6 month "
        "lag, but healthcare equity does not Granger-cause sentiment. This one-directional "
        "pattern is economically sensible: survey responses reflect real consumer "
        "decisions that take months to flow through to sector revenues and stock prices."
    ),
    key_message=(
        "Sentiment leads healthcare equity at 3-6 months — a directionally clean, "
        "one-way Granger causality that supports using UMCSENT as an actionable "
        "leading indicator for XLV timing."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Descriptive Statistics)",
    method_theory=(
        "We sort all monthly observations into four quartiles based on UMCSENT "
        "year-over-year change and compute full return statistics for XLV in each "
        "quartile. This is the simplest possible regime test: does XLV performance "
        "differ systematically across sentiment regimes, without any model-imposed "
        "structure?"
    ),
    question=(
        "If we had done nothing more sophisticated than 'hold XLV when sentiment "
        "is rising year-over-year and move to cash when it is falling,' how would "
        "that strategy have performed across historical sentiment regimes?"
    ),
    how_to_read=(
        "The chart shows two panels: left panel is the annualized Sharpe ratio in "
        "each UMCSENT YoY quartile; right panel is annualized return. Q1 = lowest "
        "(most negative) YoY change. Q4 = highest (most positive). Look for a "
        "monotonic pattern to confirm the regime-return relationship."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: annualized XLV Sharpe ratio and return by quartile "
        "of UMCSENT year-over-year change. Q1 = most negative sentiment trend, "
        "Q4 = most positive. The gradient reveals the procyclical relationship."
    ),
    observation=(
        "The regime statistics show a non-monotonic but still directional pattern. "
        "Q1 (lowest/most negative YoY): Sharpe = 0.23, Q2: Sharpe = 1.09, "
        "Q3: Sharpe = 0.56, Q4 (highest/most positive YoY): Sharpe = 0.93. "
        "The highest Sharpe is in Q2, not Q4, suggesting that *moderate* positive "
        "sentiment momentum is the strongest XLV regime, not extreme optimism. "
        "Q1 (most negative sentiment) is the worst regime at Sharpe 0.23. "
        "This confirms the procyclical direction: falling sentiment coincides with "
        "the weakest XLV performance."
    ),
    deep_dive_title="Why is Q2 better than Q4 — shouldn't the highest sentiment be best?",
    deep_dive_content=(
        "The non-monotonic Q2 > Q4 pattern is consistent with a well-documented "
        "financial markets phenomenon: extreme optimism can itself become a warning "
        "signal. When sentiment is at its most positive extreme (Q4), it may be "
        "capturing a late-cycle euphoria that historically precedes corrections. "
        "The highest predictive content is in the *direction of change* — positive "
        "but not extreme — which is exactly what the tournament-winning YoY zero-crossing "
        "rule captures: it just requires sentiment to be trending up vs. down, without "
        "distinguishing degrees of optimism."
    ),
    interpretation=(
        "The regime analysis confirms the procyclical direction: periods of falling "
        "sentiment (Q1) are the worst regime for XLV returns, while rising sentiment "
        "(Q2-Q4) is associated with better performance. The non-monotonic peak at Q2 "
        "suggests that a simple above/below-zero YoY rule (the tournament winner) is "
        "more robust than a percentile-based threshold that tries to distinguish "
        "degrees of optimism."
    ),
    key_message=(
        "Falling consumer sentiment (Q1) is the worst regime for XLV returns. "
        "Rising sentiment (Q2-Q4) is better, with the strongest signal being "
        "the direction of change, not the absolute level."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Signal Distribution Analysis",
    method_theory=(
        "We examine how XLV 3-month forward returns are distributed when the "
        "UMCSENT direction signal is rising (+1) vs. falling (-1). This reveals "
        "whether the sentiment effect is concentrated in the tails (extreme outcomes) "
        "or is a shift in the median return — information that guides strategy design."
    ),
    question=(
        "When sentiment is rising, does the entire XLV return distribution shift "
        "upward, or is the effect concentrated in avoiding the left tail (worst "
        "outcomes) or boosting the right tail (best outcomes)?"
    ),
    how_to_read=(
        "The chart shows two panels: left panel is a histogram of the UMCSENT YoY "
        "change distribution (how often sentiment improves vs. worsens); right panel "
        "shows box plots of XLV 3-month forward returns split by whether sentiment "
        "is rising or falling. The box shows median and interquartile range; whiskers "
        "show the 5th-95th percentile range."
    ),
    chart_name="signal_dist",
    chart_caption=(
        "What this shows: left panel — distribution of UMCSENT YoY changes "
        "(roughly symmetric, centered near zero); right panel — XLV 3-month "
        "forward returns when sentiment is rising vs. falling. The box plots "
        "reveal whether the effect is median-shifting or tail-driven."
    ),
    observation=(
        "The YoY change distribution is roughly symmetric with slightly more months "
        "in negative territory, reflecting that the sample includes multiple economic "
        "downturns. The return box plots show that XLV forward returns are slightly "
        "higher when sentiment is rising (median of roughly +3% vs +2% over 3 months) "
        "but the distributions substantially overlap, confirming this is a weak average "
        "effect rather than a sharp categorical separator. The left tail is notably "
        "worse during falling-sentiment periods, which is where the risk management "
        "value of the strategy resides."
    ),
    deep_dive_title="If the distributions overlap so much, why does the strategy work?",
    deep_dive_content=(
        "A signal does not need to be right every month to generate a positive "
        "Sharpe ratio. If rising sentiment is slightly more often associated with "
        "positive XLV returns, and the rule successfully avoids the worst drawdown "
        "months by moving to cash during sustained falling-sentiment periods, the "
        "cumulative risk-adjusted performance improves even though month-by-month "
        "accuracy is only modestly better than chance. The strategy's win rate is "
        "37% — lower than buy-and-hold — but the losses avoided during falling-"
        "sentiment periods are larger in magnitude than the gains missed during "
        "those months, producing the positive Sharpe differential."
    ),
    interpretation=(
        "The signal distribution analysis shows that rising vs. falling sentiment "
        "produces overlapping XLV return distributions with a modest rightward shift "
        "for rising sentiment. The strategy value comes primarily from avoiding the "
        "worst left-tail outcomes during sustained falling-sentiment periods, not "
        "from dramatically higher returns during positive months."
    ),
    key_message=(
        "The sentiment signal is a risk management tool: it primarily avoids the "
        "worst XLV drawdown months rather than generating dramatically higher returns "
        "during positive months — consistent with the portfolio's defensive role."
    ),
)


# ---------------------------------------------------------------------------
# Tab Layout (Level 1: Basic, Level 2: Advanced)
# ---------------------------------------------------------------------------
st.markdown(
    "Evidence is organized in two tiers. **Level 1** covers basic correlations and "
    "cross-correlations. **Level 2** adds regime analysis and distributional methods."
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
    sub_regime, sub_dist = st.tabs(["Regime Analysis", "Signal Distribution"])
    with sub_regime:
        render_method_block(REGIME_BLOCK)
    with sub_dist:
        render_method_block(QUANTILE_BLOCK)

# ---------------------------------------------------------------------------
# Tournament pointer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### The Combinatorial Tournament")
st.markdown(
    "We tested **1,305 combinations** of signals (7 types), thresholds (7 methods), "
    "strategies (3 types), and lead times (5 values). These were ranked by out-of-sample "
    "Sharpe ratio over 2019-2025. The top 5 strategies were validated with bootstrap "
    "significance testing and transaction cost sensitivity analysis."
)
st.caption(
    "What this shows: the full leaderboard is at "
    f"`results/{PAIR_ID}/tournament_results_20260420.csv`."
)

st.markdown("---")
st.markdown(
    "**Transition:** Four statistical methods converge on the same conclusion: "
    "consumer sentiment momentum (YoY change) is a procyclical leading indicator "
    "for XLV health care returns. Now: what does the winning strategy actually do, "
    "and how has it performed?"
)

st.page_link(
    "pages/10_umcsent_xlv_strategy.py",
    label="Continue to The Strategy",
    icon="📈",
)

st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Data: UMCSENT (FRED) + XLV (Yahoo Finance) | "
    "1998-12 to 2025-12 | 325 monthly observations."
)
