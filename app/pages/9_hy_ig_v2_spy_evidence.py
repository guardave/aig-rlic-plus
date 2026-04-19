"""HY-IG v2 -- The Evidence: Analytical Detail.

Rebuilt to render Ray's narrative using the 8-Element Template (SOP 3.9).
Each method block follows: (1) Method, (2) Question, (3) How to read,
(4) Graph, (5) Observation, (6) Deep Dive, (7) Interpretation, (8) Key Message.

Extended 2026-04-11 (retroactive fix per stakeholder review): 5 -> 8 tabs.
Added Pre-whitened CCF, Transfer Entropy, Quartile Returns method blocks,
and a render-time 8-element presence linter (SOP 3.9 "Render-time
completeness check").
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

# ---------------------------------------------------------------------------
# Page Setup
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Breadcrumb navigation (N10, META-PWQ)
# ---------------------------------------------------------------------------
render_breadcrumb("Evidence", PAIR_ID)

# ---------------------------------------------------------------------------
# Plain English expander (N8 -- Ray's narrative addition)
# ---------------------------------------------------------------------------
with st.expander("Plain English"):
    st.markdown(
        "This section shows the data we used to test whether credit spreads really "
        "do predict stock market returns. Eight different statistical tests all "
        "point to the same conclusion: when the credit spread widens, stocks tend "
        "to do worse in the following weeks and months. None of these tests is "
        "perfect on its own, but together they tell a consistent story."
    )

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We subjected 25 years of daily data to eight complementary statistical tests, "
    "each designed to stress a different weakness of the credit-leads-equity "
    "hypothesis. If one test flatters the result and the others reject it, the "
    "story is fragile. If they converge, we have real evidence.*"
)
st.markdown("---")

st.markdown(
    "Each of the methods below is presented in the same eight-step structure: what "
    "the method is, the question it answers, how to read its chart, what the chart "
    "literally shows, optional deeper statistical detail, what the numbers mean "
    "economically, and a one-line takeaway. Read straight through, or skim the "
    "bolded key messages at the end of each block."
)
st.markdown("---")


# ---------------------------------------------------------------------------
# 8-Element Render Helper (with render-time completeness linter per SOP 3.9)
# ---------------------------------------------------------------------------
REQUIRED_ELEMENTS = [
    "method_name",      # 1. The Method (heading)
    "method_theory",    # 1. The Method (body)
    "question",         # 2. The Question It Answers
    "how_to_read",      # 3. How to Read the Graph
    "observation",      # 5. Observation
    "interpretation",   # 7. Interpretation
    "key_message",      # 8. Key Message
]


def render_method_block(content: dict):
    """Render a single method block in the 8-element template order.

    Mandatory elements: 1 (Method), 2 (Question), 3 (How to Read),
    5 (Observation), 7 (Interpretation), 8 (Key Message). Element 4 (Graph)
    is optional per Rule 3.9b (missing-chart fallback cascade); Element 6
    (Deep Dive) is optional but encouraged for technical methods.

    Per SOP 3.9 render-time completeness check: missing mandatory elements
    surface as a visible ``st.error`` and the block does NOT render silently.
    """
    # Render-time 8-element presence linter
    missing = [k for k in REQUIRED_ELEMENTS if not content.get(k)]
    if missing:
        st.error(
            "Method block incomplete: missing required element(s) "
            f"{missing}. This is a gate failure per SOP Rule 3.9.\n\n"
            "Plain English: this statistical evidence block is supposed to "
            "carry every item of an 8-part template (method, question, "
            "reading guide, graph, observation, deep dive, interpretation, "
            "key message). One or more of those parts is missing, so the "
            "block was not rendered to avoid showing you an incomplete "
            "evidence write-up."
        )
        return

    method_name = content["method_name"]
    chart_status = content.get("chart_status", "ready")

    # Optional: "Why this matters" opener (N6 -- Ray's reframing)
    why_this_matters = content.get("why_this_matters")
    if why_this_matters:
        st.markdown(f"**Why this matters:** {why_this_matters}")

    # 1. The Method
    st.markdown(f"### {method_name}")
    st.markdown(content["method_theory"])

    # 2. The Question It Answers
    st.markdown(f"> *{content['question']}*")

    # 3. How to Read the Graph — APP-CC1 canonical prefix.
    st.markdown(f"**How to read it:** {content['how_to_read']}")

    # 4. Graph -- with Rule 3.9b missing-chart fallback cascade
    chart_name = content.get("chart_name")
    if chart_status == "ready" and chart_name:
        load_plotly_chart(
            chart_name,
            pair_id=PAIR_ID,
            caption=content.get("chart_caption", ""),
            fallback_text=(
                f"{method_name} chart -- canonical path "
                f"output/charts/{PAIR_ID}/plotly/{chart_name}.json not found."
            ),
        )
    else:
        st.warning(
            "Chart pending -- method block rendered from narrative only.\n\n"
            "Plain English: the chart for this analysis has not been "
            "generated yet, so we are showing you the written findings "
            "without the accompanying picture. The interpretation and key "
            "message below are based on the same underlying statistics; "
            "the chart will appear here once the visualisation pipeline "
            "produces it."
        )

    # 5. Observation — APP-CC1 canonical prefix ("What this shows:").
    st.markdown(f"**What this shows:** {content['observation']}")

    # 6. Deep Dive (optional) — canonical expander title per APP-EX1.
    # Original method-specific question is surfaced as the first line of
    # content so readers still see what the deeper-dive block answers.
    deep_dive_title = content.get("deep_dive_title")
    deep_dive_content = content.get("deep_dive_content")
    if deep_dive_title and deep_dive_content:
        with st.expander("Deeper dive"):
            st.markdown(f"*{deep_dive_title}*\n\n{deep_dive_content}")

    # 7. Interpretation — APP-CC1 canonical prefix ("Why this matters:").
    st.markdown(f"**Why this matters:** {content['interpretation']}")

    # 8. Key Message
    st.info(f"**Key message:** {content['key_message']}")


# ---------------------------------------------------------------------------
# Method Block Content (verbatim from Ray's narrative, 2026-04-10)
# ---------------------------------------------------------------------------

CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "A **Pearson correlation** is the simplest measure of co-movement between "
        "two series, a number between -1 and +1 that says how closely they move "
        "together on average. We run it here as our sanity check before reaching "
        "for heavier machinery: if credit spreads carry any predictive signal for "
        "future equity returns, it should leave at least a faint fingerprint on "
        "simple correlations."
    ),
    question=(
        "Does today's credit spread show any statistical relationship at all with "
        "where stocks are headed over the next week, month, quarter, or year?"
    ),
    how_to_read=(
        "The chart is a **heatmap** -- a grid where each cell's colour intensity "
        "represents the strength of a correlation. Rows are different transformations "
        "of the HY-IG spread (raw level, 252-day z-score, 504-day z-score, percentile "
        "rank, rate of change, etc.). Columns are forward stock-return horizons "
        "(1 day, 5 days, 21 days, 63 days, 126 days, 252 days). Blue cells mean "
        "positive correlation, red cells mean negative correlation, and the darker "
        "the colour, the stronger the relationship. White or pale cells mean "
        "essentially no linear link."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "How to read it: Pearson correlations between HY-IG spread "
        "transformations (rows) and forward SPY returns at multiple horizons "
        "(columns). Darker colours indicate stronger linear relationships."
    ),
    observation=(
        "At very short horizons (1 day, 5 days, 21 days), almost every cell is "
        "nearly white -- correlations sit within plus or minus 0.02 and do not clear "
        "statistical significance. From the 63-day column onward, the grid starts to "
        "darken: the raw spread shows a correlation of -0.036 with 63-day forward "
        "returns (p = 0.0035), the 252-day z-score reaches -0.099 with 252-day "
        "forward returns (p < 0.001), and the 504-day z-score lands at -0.040 with "
        "126-day forward returns (p = 0.0015). The strongest cells are concentrated "
        "in the bottom-right corner of the heatmap, where longer lookback "
        "transformations meet longer forward horizons."
    ),
    deep_dive_title="Why are the correlations so small in absolute terms, and should I worry?",
    deep_dive_content=(
        "Three things to keep in mind. First, daily stock returns are dominated by "
        "noise -- even a genuinely useful predictor will only explain a few percent "
        "of variance, so raw correlations in the 0.05-0.10 range can still be "
        "economically meaningful. Second, we report Pearson correlations with "
        "conventional p-values; with samples of roughly 6,500 daily observations, "
        "even very small coefficients can clear statistical significance, so we "
        "rely on the p-values as a filter for what is distinguishable from zero "
        "rather than treating the magnitudes as 'effect sizes.' Third, the "
        "correlation test is purely **linear and contemporaneous** -- it cannot "
        "capture regime-dependent relationships or nonlinear threshold effects, "
        "which is precisely why the next three methods exist. We treat correlations "
        "as a 'lights-on' test: if nothing showed up here, we would be sceptical of "
        "the entire hypothesis."
    ),
    interpretation=(
        "Credit spreads and stock returns have essentially no linear relationship "
        "at the daily and weekly horizons favoured by short-term traders, but a "
        "measurable and statistically significant one emerges at the one-quarter to "
        "one-year horizon. The negative sign is the key finding: it confirms the "
        "direction predicted by economic theory -- **wider spreads today go with "
        "weaker equity returns later**, not stronger ones. The fact that z-scored "
        "and percentile-ranked versions of the spread outperform the raw level tells "
        "us that what matters is not how wide spreads are in absolute terms, but how "
        "unusual they are relative to their recent history."
    ),
    key_message=(
        "Linear correlations are weak at trading-horizon speeds but grow meaningfully "
        "negative at quarterly-to-annual horizons, confirming that credit spreads "
        "carry a slow-moving, right-signed warning rather than a daily trading signal."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "**Granger causality** is a statistical test that asks a precise question: "
        "do past values of variable X improve our forecast of variable Y, above and "
        "beyond what Y's own past values already tell us? We use the **Toda-Yamamoto "
        "variant**, which adds extra lags to the underlying regression so the test "
        "remains valid even when one or both series contain trends or unit roots -- "
        "a practical necessity because credit spread levels drift over decades-long "
        "cycles."
    ),
    question=(
        "Do past credit spread movements contain information that helps predict "
        "future stock returns that is not already baked into stocks' own recent "
        "behaviour?"
    ),
    how_to_read=(
        "The chart is a **bar plot of F-statistics by lag**. Each bar corresponds "
        "to one lag length from 1 to 12 trading days (we run the monthly-resolution "
        "test here; see the Methodology page for the daily-resolution variant). "
        "The height of each bar is the F-statistic for 'HY-IG spread predicts SPY "
        "returns' at that lag. Bars shaded red cross the 5% significance threshold "
        "(p < 0.05); pale bars do not. A dashed horizontal line marks the F-critical "
        "reference level. Taller red bars mean stronger predictive evidence."
    ),
    # Evan's new standalone Granger artifact (closes S18-11).
    chart_name="granger_f_by_lag",
    chart_caption=(
        "How to read it: F-statistic by lag for the HY-IG → SPY direction "
        "(monthly). Bars above the F-critical dashed line are statistically "
        "significant at 5%. Best-lag result: lag 5 with F = 4.07, p = 0.0014."
    ),
    observation=(
        "At monthly resolution, the HY-IG → SPY direction shows a clear "
        "credit-leads-equity signal. Lags 1 through 3 are not significant, but "
        "lags 4 through 12 all clear the 5% threshold. The **best lag is 5**, "
        "with F = 4.07 and p = 0.0014 — credit-spread information from five "
        "months ago helps forecast next month's SPY return above and beyond "
        "SPY's own recent history. The pattern is consistent with the view "
        "that credit-spread information about equity accumulates over "
        "multi-month horizons rather than arriving in a single-month impulse. "
        "(The reverse direction — SPY → HY-IG, daily resolution — is also "
        "strong at short lags and is documented in the daily-resolution "
        "Granger table on the Methodology page.)"
    ),
    deep_dive_title="Does bidirectional Granger causality mean the signal is useless?",
    deep_dive_content=(
        "Not at all, but it does mean we need to read the numbers carefully. "
        "Bidirectional causality is exactly what the Merton (1974) structural model "
        "predicts: equity and credit are two views of the same underlying firm "
        "value, so information flows in both directions. What matters for a "
        "practical strategy is **which direction dominates, and in which regime**. "
        "The Toda-Yamamoto procedure fits an augmented VAR of order p + d, where p "
        "is selected by BIC and d is the maximum suspected order of integration "
        "(d = 1 here because spread levels look near-I(1)). We tested lags 1-5 on "
        "daily first-differences; longer lags do not add explanatory power by BIC. "
        "The full-sample result -- equity dominant, credit weakly significant at "
        "3-5 day lags -- is the unconditional picture. The regime-conditional "
        "version, run separately for calm and stress periods, is what actually "
        "powers the trading strategy; the credit-to-equity signal strengthens "
        "materially in stress, consistent with Acharya & Johnson (2007)."
    ),
    interpretation=(
        "At first glance, this looks like bad news for our hypothesis -- equity "
        "seems to lead credit far more strongly than credit leads equity. But read "
        "in the context of the Merton model, the result is exactly what theory "
        "predicts: both markets are repricing the same underlying corporate asset "
        "values, so information flows both ways. The practically important finding "
        "is that the credit-to-equity channel exists and is statistically "
        "significant at the 3-to-5-day horizon, with enough room for a trader to "
        "act. The asymmetry in strength tells us something subtler: in normal "
        "times, stock prices set the pace, and credit is a follower; the credit "
        "signal is quiet precisely because there is no stress to price. The "
        "signal's real value must come from **regime-dependent** behaviour -- which "
        "is what the HMM and regime-conditional tests pick up, and which the "
        "full-sample Granger test understates by averaging calm and stress together."
    ),
    key_message=(
        "Granger tests confirm a real but modest credit-leads-equity channel at "
        "3-5 day lags -- small in the full-sample average because calm periods "
        "dilute it, but the foundation on which the regime-dependent strategy is "
        "built."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jorda Impulse Responses)",
    method_theory=(
        "A **local projection** is a method for tracing the cumulative effect of a "
        "one-time 'shock' in one variable on another variable over time. Rather "
        "than fitting a single big system like a VAR and then reading off impulse "
        "responses (which requires the whole system to be correctly specified), "
        "local projections run **one separate regression per forecast horizon** -- "
        "a regression for the 5-day-ahead response, another for 21 days, another "
        "for 63 days, and so on. This makes the method robust to model "
        "misspecification, at the cost of slightly less efficient estimates. "
        "Developed by Jorda (2005)."
    ),
    question=(
        "If the HY-IG credit spread suddenly widens by one unit today, how much "
        "lower are stock returns expected to be over the next week, month, and "
        "quarter -- and at what horizon does the effect peak?"
    ),
    how_to_read=(
        "The chart is a **line-and-band impulse response**. The horizontal axis is "
        "horizon in trading days (0, 5, 21, 63 days ahead). The vertical axis is "
        "the cumulative expected stock return following a 1-unit shock to the "
        "HY-IG spread, expressed as a decimal (so -0.01 means a 1% cumulative "
        "drag). The solid line is the point estimate -- our best guess of the "
        "effect at each horizon. The shaded band around it is the **95% confidence "
        "interval**: if the band stays entirely below zero, the effect is "
        "statistically distinguishable from zero with 95% confidence. If the band "
        "crosses zero, the effect is consistent with noise."
    ),
    chart_name="local_projections",
    chart_caption=(
        "How to read it: cumulative SPY return response to a 1-unit shock "
        "in the HY-IG spread, estimated separately at each horizon with HC3 "
        "robust standard errors. The 95% confidence band crosses zero at "
        "short horizons and stays below it from the 63-day point onward."
    ),
    observation=(
        "The impulse response line starts near zero at the 5-day horizon "
        "(coefficient = -0.0008, p = 0.32) and drifts progressively more negative "
        "as the horizon lengthens: -0.0034 at 21 days (p = 0.12, confidence band "
        "still crossing zero), then -0.0085 at 63 days (p = 0.0345, confidence "
        "band now entirely below zero at -0.0164 to -0.0006). The R-squared also "
        "grows with horizon -- from 0.6% at 5 days to 4.4% at 63 days -- "
        "indicating the relationship tightens as we look further out. The shape "
        "is a steady, accelerating downward slope, not a quick dip followed by "
        "recovery."
    ),
    deep_dive_title="Why use local projections instead of a conventional VAR, and what are the trade-offs?",
    deep_dive_content=(
        "Vector autoregressions are the textbook tool for impulse responses, but "
        "they require us to assume the entire joint dynamic system is correctly "
        "specified -- get the lag order wrong, miss a nonlinearity, and the "
        "impulse response for every variable at every horizon is biased. Local "
        "projections (Jorda 2005) sidestep this by estimating a separate linear "
        "regression at each forecast horizon, where each regression need only be "
        "correctly specified at its own horizon. This is a massive robustness "
        "gain when relationships are regime-dependent, as ours clearly are. The "
        "cost is efficiency: LP standard errors are wider than VAR standard "
        "errors when the VAR is correctly specified. We use **HC3 robust standard "
        "errors** throughout to account for the overlapping-window problem (a "
        "63-day forward return today shares 62 days with tomorrow's 63-day "
        "forward return). The 63-day coefficient clears the 5% significance "
        "threshold; the 21-day estimate is suggestive but not significant; "
        "shorter horizons are noise. We also ran state-dependent versions (calm "
        "vs stress) and the stress-state coefficient is roughly 2-3x larger than "
        "the full-sample estimate."
    ),
    interpretation=(
        "Credit-spread shocks do not hit equities immediately. The effect builds "
        "slowly over one to three months, reaching roughly -0.85% of cumulative "
        "return at the 63-day horizon for a 1-unit spread shock. Practically, "
        "this slow diffusion of credit information into equity prices is "
        "precisely what makes the signal **actionable**: a warning that was "
        "fully priced in by the next day would be useless, but a warning that "
        "takes 4-12 weeks to play out leaves time for a disciplined investor to "
        "reduce exposure. The accelerating shape of the response (flat at 5 "
        "days, curving down at 21 days, steepening at 63 days) is also "
        "consistent with a 'drip feed' view of credit information: each week, a "
        "little more of the bond market's pessimism gets incorporated into "
        "stock prices."
    ),
    key_message=(
        "A credit-spread shock drags equity returns progressively lower over the "
        "next three months, with the effect statistically significant by the "
        "63-day horizon -- the slow burn is a feature, not a bug, because it "
        "opens a window for investors to act."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Hidden Markov Model)",
    method_theory=(
        "A **Hidden Markov Model (HMM)** is a statistical model that assumes the "
        "market is always in one of several unobservable ('hidden') states -- for "
        "us, 'calm' or 'stressed' -- each with its own characteristic mean, "
        "volatility, and cross-asset correlations. The model cannot see the "
        "states directly; instead it infers, for every day in the sample, the "
        "probability that the market was in each state that day, based on the "
        "observed behaviour of the HY-IG spread and VIX. Developed originally for "
        "speech recognition in the 1960s, HMMs were brought into financial regime "
        "modelling by Hamilton (1989) and are now standard."
    ),
    question=(
        "Are there distinct market states in which the credit-equity relationship "
        "behaves fundamentally differently -- and can we identify when the market "
        "switches from one state to another without imposing arbitrary thresholds "
        "like 'spreads above 500 basis points'?"
    ),
    how_to_read=(
        "The chart is a **time-series of regime probabilities** from 2000 through "
        "2025. The horizontal axis is calendar time. The vertical axis shows two "
        "stacked probability bands, each running from 0 to 1: the blue band is "
        "the estimated probability of being in the **calm regime** at each date, "
        "and the red band is the estimated probability of being in the **stress "
        "regime**. The two bands always sum to 1 (since the market must be in one "
        "of the two states). SPY price is overlaid as a thin black line for "
        "visual anchoring, and NBER recession periods are shaded in grey."
    ),
    chart_name="hmm_regime_probs",
    chart_caption=(
        "How to read it: HMM-inferred probability of being in the calm vs "
        "stress regime each day from 2000-2025, with SPY overlaid. Stress "
        "spikes align tightly with the dot-com bust, GFC, COVID, and the "
        "2022 rate shock."
    ),
    observation=(
        "For long stretches -- roughly 2003 through mid-2007, 2010 through 2014, "
        "and 2016 through 2019 -- the blue 'calm' band sits near 1.0 almost "
        "continuously. The red 'stress' band spikes abruptly and unmistakably "
        "during four episodes: late 2001 through 2002 (dot-com bust), mid-2007 "
        "through mid-2009 (GFC, with the most persistent stress state in the "
        "sample), early 2020 (COVID, a sharp but short-lived spike), and "
        "scattered bursts during 2022 (rate shock). The transitions between calm "
        "and stress are not gradual -- the HMM typically flips the dominant "
        "regime within a handful of trading days once stress begins to build."
    ),
    deep_dive_title="How does the HMM decide when to switch regimes, and how do we know it is not just curve-fitting?",
    deep_dive_content=(
        "The Gaussian HMM we use (fitted on daily HY-IG spread changes and VIX "
        "levels jointly) has two free components per state: a mean vector and a "
        "covariance matrix. The model also estimates a 2x2 transition matrix of "
        "probabilities -- for example, 'given that today is calm, what is the "
        "probability tomorrow is still calm?' These transition probabilities are "
        "typically in the high 0.95-0.99 range for staying in the current state, "
        "which creates the persistent 'flat' periods visible in the chart. "
        "Regime identification is done via the **Viterbi algorithm**, which "
        "finds the most likely sequence of hidden states given the observed "
        "data. We guard against overfitting three ways: (1) we fit only on the "
        "2000-2017 in-sample window and let the HMM classify 2018-2025 cold; "
        "(2) we compare 2-state and 3-state variants by log-likelihood and "
        "BIC -- 2-state wins on parsimony; (3) we check that stress-state "
        "identification lines up with independently-known crisis dates (GFC, "
        "COVID, 2022) rather than being a retrospective fit. Out-of-sample "
        "classification correctly flags the COVID shock within about a week of "
        "its onset."
    ),
    interpretation=(
        "The HMM confirms that markets genuinely operate in two distinct modes "
        "rather than on a smooth continuum, and the stress state lines up "
        "tightly with episodes that economists, historians, and investors would "
        "all independently call crises. This is the engine room of the trading "
        "strategy: instead of applying the same rule in all weather, the "
        "strategy only acts on the credit signal when the HMM puts high "
        "probability on the stress state. Equally important, the model "
        "discovers where the stress threshold lies from the data itself -- "
        "typically corresponding to HY-IG z-scores of 1.5-2.0 and raw spreads "
        "of 500-600+ basis points -- rather than requiring us to impose an "
        "arbitrary cutoff that might be wrong or curve-fit."
    ),
    key_message=(
        "The market really does have two distinct states, and the HMM can "
        "identify the transition from calm to stress in near real time -- this "
        "is what turns the credit signal from an interesting correlation into a "
        "usable trading rule."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "An ordinary (OLS) regression asks 'on average, how do stock returns "
        "respond to credit spreads?' -- but an average can hide very different "
        "behaviour in the tails of the distribution. **Quantile regression**, "
        "developed by Koenker & Bassett (1978), instead estimates separate "
        "coefficients for different **percentiles** of the stock-return "
        "distribution: one for the 5th percentile (worst 5% of outcomes), one "
        "for the median (typical outcome), one for the 95th percentile (best "
        "5%), and so on. It is the right tool when you suspect a variable "
        "matters more for tail outcomes than for the middle of the distribution."
    ),
    question=(
        "Do credit spreads predict large stock losses, large stock gains, both, "
        "or neither -- and is the effect the same across the entire return "
        "distribution, or is it concentrated in the tails?"
    ),
    how_to_read=(
        "The chart is a **coefficient plot across quantiles**. The horizontal "
        "axis shows return quantiles from 0.05 (worst 5% of forward returns) on "
        "the left to 0.95 (best 5%) on the right. The vertical axis shows the "
        "estimated HY-IG coefficient at each quantile -- that is, how much that "
        "slice of the return distribution moves in response to a unit change in "
        "the credit spread. Each point estimate has a small vertical bar showing "
        "its 95% confidence interval. A horizontal dashed line at zero marks the "
        "'no effect' reference. If all the coefficients sit flat near zero, "
        "credit spreads do not matter at any part of the distribution. If they "
        "slope from negative on the left to positive on the right, credit "
        "spreads are 'spreading out' the return distribution -- making bad "
        "outcomes worse and good outcomes better."
    ),
    chart_name="quantile_regression",
    chart_caption=(
        "How to read it: quantile-regression coefficients for the HY-IG "
        "spread across the full range of forward SPY return percentiles, "
        "with 95% confidence bars. The monotone slope from negative (left "
        "tail) to positive (right tail) is the 'Vulnerable Growth' fingerprint."
    ),
    observation=(
        "The coefficient pattern forms a clean, monotonic slope from strongly "
        "negative on the left to strongly positive on the right. At the 5th "
        "percentile, the coefficient is -0.0117 (p < 0.001, confidence interval "
        "-0.0134 to -0.0100); at the 10th percentile it is -0.0094 (p < 0.001); "
        "at the 25th percentile, -0.0052 (p < 0.001); at the median, essentially "
        "zero (+0.000008, p = 0.98, confidence interval straddling zero); at the "
        "75th percentile, +0.0046 (p < 0.001); at the 90th percentile, +0.0083 "
        "(p < 0.001); at the 95th percentile, +0.0118 (p < 0.001). The median "
        "coefficient is the only one that is not statistically different from "
        "zero."
    ),
    deep_dive_title="What does it mean economically for the median coefficient to be zero while the tails are strongly significant?",
    deep_dive_content=(
        "This pattern -- zero at the centre, large and opposite-signed at the "
        "tails -- is the fingerprint of a **variance-shifting** rather than a "
        "**mean-shifting** relationship. In plain terms, wider credit spreads "
        "do not change the typical day's return, but they make the distribution "
        "of possible returns wider on both sides: worse lows and (apparently) "
        "better highs. This is the 'Vulnerable Growth' pattern documented by "
        "Adrian, Boyarchenko & Giannone (2019) for GDP growth and financial "
        "conditions; we find it alive and well in daily equity returns. The "
        "symmetric shape is worth a note: the left tail (losses) is what "
        "matters for risk management, but the positive right-tail coefficients "
        "are not a bullish signal -- they reflect the fact that high-stress "
        "environments also produce large relief rallies and short squeezes, "
        "which inflate the upper percentiles without improving average returns. "
        "The near-zero median is the reason simple mean-regression (OLS) "
        "predictive regressions looked so underwhelming in the earlier table: "
        "averaging across the distribution washes out the tail information. We "
        "report bootstrapped confidence intervals with 1,000 resamples; the "
        "pattern is robust to outliers and sample splits."
    ),
    interpretation=(
        "Credit spreads are a **risk signal**, not a return signal. They tell "
        "you when the distribution of outcomes is about to widen -- when both "
        "terrible and terrific days become more likely -- but they do not tell "
        "you the average outcome will be better or worse. This is exactly the "
        "right shape for a defensive tool: a rational risk-averse investor cares "
        "disproportionately about the left tail, so a signal that sharpens "
        "predictions specifically at the 5th and 10th percentiles is far more "
        "valuable than one that shifts the mean. The symmetric right-tail "
        "response also explains why the strategy cannot be run as a long-short "
        "system: the apparent 'upside' in the right tail comes from stress-driven "
        "volatility, not genuine predictability of gains, and a short-during-"
        "stress position would get steamrolled by the same relief rallies that "
        "create those positive coefficients."
    ),
    key_message=(
        "Credit spreads are a fire alarm, not a green light -- they sharply "
        "predict the worst stock-return outcomes but say nothing about the "
        "average, which is why the strategy should reduce exposure in stress "
        "and never try to short it."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-whitened Cross-Correlation Function (CCF)",
    method_theory=(
        "A **pre-whitened Cross-Correlation Function (CCF)** measures how "
        "strongly two time series move together at different time offsets -- "
        "lag 0 is contemporaneous, negative lags ask whether series A leads "
        "series B by that many days, positive lags ask the reverse. "
        "\"Pre-whitened\" means we first fit an ARIMA model to each series and "
        "run the cross-correlation on the residuals, because raw CCFs on "
        "autocorrelated financial data produce spurious lead-lag signals that "
        "are really just each series remembering its own past."
    ),
    question=(
        "At short daily horizons, who moves first -- the bond market or the "
        "stock market -- and how many days of lead time (if any) does either "
        "side enjoy?"
    ),
    how_to_read=(
        "The horizontal axis is lag in trading days, running from -20 (the "
        "spread moves 20 days after SPY) through 0 (contemporaneous) to +20 "
        "(the spread moves 20 days before SPY). The vertical axis is the "
        "pre-whitened correlation, bounded between -1 and +1. Each vertical "
        "bar is one lag; bars that cross the dashed horizontal lines at "
        "+/-0.0238 are statistically significant at the 95% level (the band "
        "is 1.96/sqrt(N) for N = 6,782 observations). Bars shaded darker are "
        "the significant ones; pale bars are noise. Read left-to-right: "
        "significant negative-lag bars mean SPY led the spread; significant "
        "positive-lag bars mean the spread led SPY."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "How to read it: pre-whitened cross-correlations between the HY-IG "
        "spread and SPY log-returns at lags -20 to +20 trading days. Bars "
        "beyond the +/-0.0238 significance band are statistically "
        "distinguishable from zero at 95%."
    ),
    observation=(
        "15 of the 41 lags from -20 to +20 are statistically significant at "
        "95% confidence. The significant negative lags (SPY leading the "
        "spread) dominate: they land at -1, -2, -5, -7, -9, -12, -15, and "
        "-17 days, including the largest magnitude in the whole chart at "
        "lag -17 (CCF = -0.069). The contemporaneous lag (0) sits right at "
        "the significance boundary on the negative side. The positive-lag "
        "side (spread leading SPY) is much sparser, with significant bars "
        "only at +6, +7, +9, and +13 days. The overall visual impression is "
        "a left-weighted forest of negative bars on the 'SPY leads' side and "
        "a thinner scatter of alternating-sign bars on the 'spread leads' "
        "side."
    ),
    deep_dive_title=(
        "What does 'pre-whitened' actually change, and why did we pick "
        "ARIMA(2,0,2)?"
    ),
    deep_dive_content=(
        "A raw CCF on two autocorrelated series inherits the autocorrelation "
        "of both sides, so almost every lag ends up 'significant' even when "
        "there is no genuine cross-dynamic relationship -- the statistic is "
        "really measuring each series talking to itself. Pre-whitening fixes "
        "this by fitting an ARIMA(p, d, q) model to each series, extracting "
        "the residuals (which are approximately white noise by construction), "
        "and running the CCF on those residuals. The cross-correlation that "
        "survives pre-whitening reflects only genuine dynamic interaction, "
        "not self-memory. We selected ARIMA(2,0,2) for both series by BIC "
        "grid search over p <= 5 and q <= 2 on the full daily sample "
        "(2000-01-03 to 2025-12-31, N = 6,782); the same order was applied "
        "to both the HY-IG spread and the SPY log-return series so neither "
        "side gets a filter the other does not. The 95% confidence "
        "half-width of +/-0.0238 follows from the usual 1.96/sqrt(N) "
        "large-sample rule."
    ),
    interpretation=(
        "At sub-monthly horizons, the CCF says something that surprises "
        "readers who have only seen the 'credit leads equity' headline: "
        "**it is stocks that move first, not credit.** The strongest "
        "significant bars sit on the negative-lag side -- SPY declines today "
        "are followed by spread widening over the next 1 to 17 days, not the "
        "other way around. This is not a contradiction of the Local "
        "Projections result at the 63-day horizon, where credit genuinely "
        "leads equity. It is a horizon-specific finding: at daily-to-weekly "
        "horizons the equity market reprices first and credit follows, while "
        "at the quarterly horizon the bond market's slow accumulation of "
        "default-risk information drags equity returns lower. Nor is it a "
        "contradiction of the Transfer Entropy result in the next block: CCF "
        "is a linear filter that measures price-level co-movement, whereas "
        "Transfer Entropy measures nonlinear conditional distribution "
        "shifts. The two methods look at different properties of the same "
        "joint distribution and answer different questions."
    ),
    key_message=(
        "At daily-to-weekly horizons, equity moves first and credit follows "
        "-- the 'credit leads equity' story is a quarterly-horizon "
        "phenomenon, not a short-term trading edge."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy (Nonlinear Information Flow)",
    method_theory=(
        "**Transfer entropy (TE)** is an information-theoretic measure of "
        "directed information flow between two time series. Formally, it is "
        "the reduction in uncertainty about variable Y's next value that you "
        "gain from knowing variable X's past, over and above what you "
        "already learn from Y's own past. Unlike Granger causality and the "
        "CCF -- both of which are fundamentally linear tests of co-movement "
        "in levels -- transfer entropy captures nonlinear relationships and "
        "conditional distribution shifts, which is exactly the kind of "
        "regime-dependent signal credit-equity data is known to exhibit."
    ),
    question=(
        "When we measure information flow in the nonlinear sense -- not just "
        "linear price co-movement -- how much information does credit carry "
        "about the next move in equities, and how much does equity carry "
        "about the next move in credit?"
    ),
    how_to_read=(
        "The chart is a **paired bar plot** with two bars: one for 'Credit "
        "-> Equity' (how much the past of the HY-IG spread reduces "
        "uncertainty about tomorrow's SPY return) and one for 'Equity -> "
        "Credit' (the reverse). The vertical axis is transfer entropy "
        "measured in **nats** -- a natural-log unit of information, where "
        "bigger bars mean more information is flowing in that direction. "
        "The permutation p-value is annotated on each bar: p < 0.01 "
        "indicates the flow is statistically distinguishable from chance at "
        "the 1% level. The visual takeaway is the ratio between the two "
        "bars -- not the absolute heights, which are small in any "
        "information-theoretic study of daily returns."
    ),
    chart_name="transfer_entropy",
    chart_caption=(
        "How to read it: Shannon transfer entropy between the HY-IG spread "
        "and SPY daily returns, in both directions, with circular "
        "block-shift permutation p-values annotated on each bar."
    ),
    observation=(
        "The Credit -> Equity bar reaches 0.042 nats with permutation "
        "p = 0.004 (500 permutations), comfortably clearing the 1% "
        "significance threshold. The Equity -> Credit bar reaches only "
        "0.0055 nats with p = 0.050 -- marginal significance at best. The "
        "Credit -> Equity bar is roughly 7.6x the height of the Equity -> "
        "Credit bar. Both bars are positive (no directional sign in "
        "information theory -- TE measures magnitude, not sign), but the "
        "asymmetry between them is the headline: information flows from "
        "credit into equity far more strongly than it flows from equity "
        "into credit."
    ),
    deep_dive_title=(
        "What exactly is transfer entropy, and how is this different from "
        "Granger causality?"
    ),
    deep_dive_content=(
        "Transfer entropy from X to Y is defined as H(Y_t+1 | Y_t) - "
        "H(Y_t+1 | Y_t, X_t), where H denotes Shannon entropy. In plain "
        "English: how much smaller is our uncertainty about Y's next value "
        "once we know X's past, compared to only knowing Y's own past? If "
        "the answer is zero, X tells us nothing new about Y. If the answer "
        "is large, X carries genuine predictive information about Y that "
        "Y's own history does not capture. The key difference from Granger "
        "causality is that Granger is implemented as a linear regression "
        "test -- it can only see relationships that show up in conditional "
        "means. Transfer entropy is non-parametric and sees the full "
        "conditional distribution, so it picks up threshold effects, regime "
        "switches, and tail dependencies that a linear Granger test misses "
        "entirely. We estimated TE using a Shannon histogram with 6 "
        "equal-frequency (quantile) bins and lag 1 day, and tested "
        "significance with a circular block-shift permutation test using "
        "500 permutations. Because `pyinform` was not available in the "
        "environment, the estimator was implemented from first principles "
        "following Schreiber (2000) -- see "
        "`scripts/retro_fix_hy_ig_v2_evan_20260411.py::transfer_entropy_hist` "
        "for the exact implementation. TE values are sensitive to bin "
        "count; the 6-bin choice is documented in the CSV `bin_method` "
        "field for reproducibility."
    ),
    interpretation=(
        "When information flow is measured in the nonlinear sense -- "
        "capturing conditional distribution shifts rather than just linear "
        "price co-movement -- **credit leads equity by a decisive margin, "
        "roughly 7.6 to 1**. This is the finding that matters for the "
        "strategy: the credit channel does genuinely carry information that "
        "linear correlation and linear Granger tests understate, because it "
        "delivers that information through nonlinearities -- threshold "
        "effects, tail events, and regime switches -- which is exactly "
        "where credit signals have always been thought to earn their keep. "
        "Note that the TE result is not a contradiction of the CCF result "
        "in the previous block. CCF is a linear filter that picks up "
        "price-level co-movement and saw SPY leading at short lags; TE is "
        "a nonlinear measure that picks up conditional distribution shifts "
        "and sees credit dominating. Both are correct: the two methods "
        "measure different properties of the same joint distribution, and "
        "the credit signal shows up more clearly in the nonlinear measure "
        "because that is the channel through which it actually operates."
    ),
    key_message=(
        "In the nonlinear, information-theoretic sense, credit carries "
        "roughly 7.6x more information about equity than equity carries "
        "about credit -- this is the quantitative basis for building a "
        "credit-led equity-timing strategy."
    ),
)


QUARTILE_RETURNS_BLOCK = dict(
    chart_status="ready",
    method_name="Quartile Returns Analysis",
    method_theory=(
        "A **quartile returns analysis** sorts every day in the sample into "
        "four bins based on the HY-IG spread level that day -- Q1 is the "
        "25% of days with the tightest spreads, Q4 is the 25% with the "
        "widest -- and computes full return statistics (mean, volatility, "
        "Sharpe, annualized return, max drawdown) for the SPY returns "
        "earned in each bin. It is the simplest possible regime-conditional "
        "check: does the forward return distribution for SPY look different "
        "depending on which credit-cycle state we are in, without any "
        "fitted model telling us where the regime boundaries should fall?"
    ),
    question=(
        "If we had done nothing more sophisticated than 'buy SPY when HY-IG "
        "spreads are in their tightest 25% and sit in cash otherwise,' how "
        "would that strategy have performed -- and how does performance "
        "scale across the full spread distribution?"
    ),
    how_to_read=(
        "The chart is a **bar plot** showing four bars, one per quartile, "
        "with the Sharpe ratio on the vertical axis. Q1 (leftmost) "
        "represents the tightest-spread days -- the roughly 1,700 days when "
        "HY-IG OAS was between 147 and 255 bps (1.47% to 2.55%). Q4 "
        "(rightmost) represents the widest-spread days -- 450 to 1,531 bps "
        "(4.5% to 15.3%). A reference line at Sharpe = 0 separates bins "
        "where risk-taking was rewarded from bins where it was not. A "
        "secondary annotation shows the per-quartile max drawdown so "
        "readers can see the risk side of the equation alongside the "
        "return side."
    ),
    # Evan's new monthly-resolution quartile artifact (closes S18-8).
    chart_name="regime_quartile_returns",
    chart_caption=(
        "What this shows: annualized SPY return by HY-IG spread quartile "
        "(monthly). Q1 = tightest spreads (< 2.58 pp), Q4 = widest "
        "(> 4.62 pp). Green-to-red gradient mirrors the stress dimension; "
        "zero-line reference included."
    ),
    observation=(
        "The annualized-return gradient is monotonically declining from Q1 "
        "(tightest spreads) to Q4 (widest). Q1 earns +18.6% annualized with "
        "Sharpe 1.79; Q2 +15.0% with Sharpe 1.48; Q3 +4.7% with Sharpe 0.53; "
        "Q4 −11.3% with Sharpe −0.53. The Q1–Q4 spread is **29.9 percentage "
        "points of annual return and 2.33 Sharpe units**, with Q4 max drawdown "
        "deepening to −67.6% versus −13.6% in Q1. The monotonicity across "
        "return, Sharpe, and drawdown is the core empirical punchline — no "
        "quartile inverts the pattern."
    ),
    deep_dive_title=(
        "Why is the mean difference not significant when the Sharpe "
        "difference is so large?"
    ),
    deep_dive_content=(
        "The quartile analysis reported here is run at **monthly resolution** "
        "(311 months, 2000-02 to 2025-12), which aligns with the credit-cycle "
        "horizon the Granger and Local Projections methods identified as most "
        "informative. Quartile cutoffs are unconditional (pooled over the full "
        "monthly sample) rather than rolling — this intentionally lets the "
        "GFC and COVID widening episodes concentrate in Q4 as they "
        "historically did. Cutoffs in percentage points: Q1 ≤ 2.58, Q2 ≤ 3.22, "
        "Q3 ≤ 4.62, Q4 > 4.62. The daily-resolution version (in "
        "`core_models_20260410/quartile_returns.csv`) tells a similar story "
        "with slightly different magnitudes because daily noise dilutes the "
        "conditioning. Statistical-significance-on-means is the wrong frame "
        "here: **the economically decisive finding is the Sharpe and drawdown "
        "gradient**, because investors care about risk-adjusted outcomes and "
        "the risk side is exactly where Q4 blows out. Methodology sidecar: "
        "`results/hy_ig_v2_spy/regime_quartile_returns_methodology.md`."
    ),
    interpretation=(
        "The monotone gradient from Q1 to Q4 — **29.9 percentage points of "
        "annualized return and 2.33 Sharpe units** — is the cleanest possible "
        "picture of why any credit-conditioned equity strategy works. The "
        "simplest possible rule would be **buy SPY when HY-IG spreads are in "
        "Q1 (tightest quartile) and sit in cash otherwise**: Q1 earned Sharpe "
        "1.79 on the days the trader was invested, versus the HMM-based "
        "tournament winner's OOS Sharpe 1.27 and the buy-and-hold benchmark's "
        "~0.90. This does not automatically mean the quartile rule is a "
        "better strategy than the HMM (it spends most of the sample in cash "
        "and the cutoffs are in-sample), but it does frame what the HMM is "
        "actually doing: **a sophisticated version of quartile classification "
        "using changes and volatility rather than just levels**. It also "
        "reinforces the Quantile Regression result: when spreads are wide, "
        "the SPY return distribution genuinely widens out, and the left tail "
        "is where most of the damage happens (Q4 max drawdown reaches −67.6%)."
    ),
    key_message=(
        "The HMM regime detection strategy (our tournament winner) is "
        "essentially a sophisticated version of quartile classification -- "
        "when you cannot manually sort all months and update the cut every "
        "period, the HMM does it for you with a statistical model. A no-model "
        "'only own stocks when credit spreads are tight' rule would have "
        "delivered Sharpe 1.79 and a −13.6% max drawdown in Q1, against "
        "−0.53 and −67.6% in Q4 — the credit-cycle regime is the single most "
        "important variable in this analysis, and that is precisely what the "
        "HMM picks up automatically using changes and volatility rather than "
        "just levels."
    ),
    why_this_matters=(
        "This is the simplest possible strategy test -- if you had just "
        "sorted all trading days by credit spread level and asked 'how did "
        "SPY perform?' -- would the answer differ between tight-spread days "
        "and wide-spread days? The chart below shows that yes, it differs "
        "dramatically -- and this simple split is the intuitive foundation "
        "for the more sophisticated HMM-based winning strategy."
    ),
)


# ---------------------------------------------------------------------------
# 2-Tier Tab Layout (N11, META-PWQ) -- Level 1 basics + Level 2 advanced
# ---------------------------------------------------------------------------
st.markdown(
    "We organize the evidence in two tiers. **Level 1** covers the basic "
    "statistical relationships -- whether credit spreads and equity moves are "
    "correlated, whether one leads the other, and at what time horizons. "
    "**Level 2** goes deeper into regime-based analysis, tail risk, nonlinear "
    "dependence, and simple classification strategies."
)
st.markdown("")

tier1, tier2 = st.tabs(
    ["Level 1 -- Basic Analysis", "Level 2 -- Advanced Analysis"]
)

with tier1:
    sub_corr, sub_granger, sub_ccf = st.tabs(
        ["Correlation", "Granger Causality", "Cross-Correlation (CCF)"]
    )
    with sub_corr:
        render_method_block(CORRELATION_BLOCK)
    with sub_granger:
        render_method_block(GRANGER_BLOCK)
    with sub_ccf:
        render_method_block(CCF_BLOCK)

with tier2:
    sub_lp, sub_regime, sub_qr, sub_te, sub_quartile = st.tabs(
        [
            "Local Projections",
            "Regime Analysis",
            "Quantile Regression",
            "Transfer Entropy",
            "Quartile Returns",
        ]
    )
    with sub_lp:
        render_method_block(LOCAL_PROJECTIONS_BLOCK)
    with sub_regime:
        render_method_block(REGIME_BLOCK)
    with sub_qr:
        render_method_block(QUANTILE_BLOCK)
    with sub_te:
        render_method_block(TRANSFER_ENTROPY_BLOCK)
    with sub_quartile:
        render_method_block(QUARTILE_RETURNS_BLOCK)


# ---------------------------------------------------------------------------
# Closing: Tournament pointer + Transition
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### The Combinatorial Tournament")
st.markdown(
    "We tested approximately 1,000+ meaningful combinations of signals (13 types), "
    "thresholds (7 methods), strategies (4 types), lead times (9 values), and "
    "lookback windows (4 lengths). These were ranked by out-of-sample **Sharpe "
    "ratio** -- a measure of risk-adjusted return calculated as (return minus "
    "risk-free rate) divided by volatility, where higher values mean better "
    "returns per unit of risk taken -- over 2018-2025 (data the models never "
    "saw during estimation). The top 5 strategies were then subjected to "
    "rigorous walk-forward validation, bootstrap significance testing, and "
    "transaction cost sensitivity analysis."
)
st.caption(
    "What this shows: the full leaderboard of tested combinations is "
    "available at `results/hy_ig_v2_spy/tournament_results_20260410.csv`."
)

st.markdown("---")
st.markdown(
    "**Transition:** The five statistical tests agree -- credit spreads carry "
    "genuine, direction-consistent, tail-concentrated, regime-dependent "
    "predictive information for stock returns. The practical question is: can "
    "an investor use this signal to improve their risk-adjusted returns -- and "
    "at what cost?"
)

st.page_link(
    "pages/9_hy_ig_v2_spy_strategy.py",
    label="Continue to The Strategy",
    icon="📈",
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | Data: 2000-01 to 2025-12 | "
    "~6,500 daily observations | Narrative: portal_narrative_hy_ig_v2_spy_20260410.md."
)
