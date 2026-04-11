"""HY-IG v2 -- The Evidence: Analytical Detail.

Rebuilt to render Ray's narrative using the 8-Element Template (SOP 3.9).
Each method block follows: (1) Method, (2) Question, (3) How to read,
(4) Graph, (5) Observation, (6) Deep Dive, (7) Interpretation, (8) Key Message.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
# Page Header
# ---------------------------------------------------------------------------
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We subjected 25 years of daily data to five complementary statistical tests, "
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
# 8-Element Render Helper
# ---------------------------------------------------------------------------
def render_method_block(
    method_name: str,
    method_theory: str,
    question: str,
    how_to_read: str,
    chart_name: str | None,
    chart_caption: str,
    observation: str,
    deep_dive_title: str | None,
    deep_dive_content: str | None,
    interpretation: str,
    key_message: str,
):
    """Render a single method block in the 8-element template order.

    Mandatory elements: 1 (Method), 2 (Question), 3 (How to Read),
    4 (Graph) [may be None], 5 (Observation), 7 (Interpretation), 8 (Key Message).
    Element 6 (Deep Dive) is optional but encouraged for technical methods.
    """
    # 1. The Method
    st.markdown(f"### {method_name}")
    st.markdown(method_theory)

    # 2. The Question It Answers
    st.markdown(f"> *{question}*")

    # 3. How to Read the Graph
    st.markdown(f"**How to read this chart:** {how_to_read}")

    # 4. Graph
    if chart_name:
        load_plotly_chart(
            chart_name,
            pair_id=PAIR_ID,
            caption=chart_caption,
            fallback_text=f"{method_name} chart -- awaiting render.",
        )

    # 5. Observation
    st.markdown(f"**What the chart shows:** {observation}")

    # 6. Deep Dive (optional)
    if deep_dive_title and deep_dive_content:
        with st.expander(deep_dive_title):
            st.markdown(deep_dive_content)

    # 7. Interpretation
    st.markdown(f"**What this means:** {interpretation}")

    # 8. Key Message
    st.info(f"**Key message:** {key_message}")


# ---------------------------------------------------------------------------
# Method Block Content (verbatim from Ray's narrative, 2026-04-10)
# ---------------------------------------------------------------------------

CORRELATION_BLOCK = dict(
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
        "Pearson correlations between HY-IG spread transformations (rows) and "
        "forward SPY returns at multiple horizons (columns). Darker colours indicate "
        "stronger linear relationships."
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
        "The Granger test output is a paired bar plot where, for each lag length "
        "(1 through 5 days), two bars show the F-statistic for 'HY-IG predicts SPY' "
        "and 'SPY predicts HY-IG.' Bigger bars mean stronger predictive evidence; a "
        "5% significance cutoff is marked with a dotted line. A standalone chart is "
        "not yet rendered for this block, so the local projections panel below "
        "serves as the visual proxy -- the impulse-response line and its confidence "
        "band tell the same story (does credit carry information for future equity?) "
        "in a complementary shape. Read the test statistics in the observation text "
        "below, then look at the LP chart in the next block for the continuous view."
    ),
    # Granger standalone chart is not yet produced; fall back to local_projections.
    chart_name="local_projections",
    chart_caption=(
        "Local projections panel stands in for the Granger bar plot: the "
        "cumulative impulse response tells the same credit-leads-equity story in "
        "continuous-horizon form, with a 95% confidence band that crosses zero "
        "until the 63-day mark."
    ),
    observation=(
        "The SPY -> HY-IG direction completely dominates the test. At every lag "
        "from 1 to 5 days, the F-statistic for 'stocks predict credit' is enormous "
        "(lag 1: F = 331, p < 0.001) and dwarfs the reverse direction. The "
        "HY-IG -> SPY bars are small at lags 1 and 2 (p = 0.78 and 0.31 "
        "respectively -- not significant) but lift above the 5% line at lags 3 "
        "through 5 (F ~ 3.0, p-values of 0.011, 0.015, and 0.014). In short: "
        "equity-leads-credit is overwhelming at all lags; credit-leads-equity is "
        "modest but statistically real starting three days out."
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
        "Cumulative SPY return response to a 1-unit shock in the HY-IG spread, "
        "estimated separately at each horizon with HC3 robust standard errors. "
        "The 95% confidence band crosses zero at short horizons and stays below "
        "it from the 63-day point onward."
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
        "HMM-inferred probability of being in the calm vs stress regime each day "
        "from 2000-2025, with SPY overlaid. Stress spikes align tightly with the "
        "dot-com bust, GFC, COVID, and the 2022 rate shock."
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
        "Quantile-regression coefficients for the HY-IG spread across the full "
        "range of forward SPY return percentiles, with 95% confidence bars. The "
        "monotone slope from negative (left tail) to positive (right tail) is "
        "the 'Vulnerable Growth' fingerprint."
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


# ---------------------------------------------------------------------------
# Tab Layout -- one tab per method block
# ---------------------------------------------------------------------------
tab_corr, tab_granger, tab_lp, tab_regime, tab_qr = st.tabs(
    [
        "Correlation Analysis",
        "Granger Causality",
        "Local Projections",
        "Regime Analysis",
        "Quantile Regression",
    ]
)

with tab_corr:
    render_method_block(**CORRELATION_BLOCK)

with tab_granger:
    render_method_block(**GRANGER_BLOCK)

with tab_lp:
    render_method_block(**LOCAL_PROJECTIONS_BLOCK)

with tab_regime:
    render_method_block(**REGIME_BLOCK)

with tab_qr:
    render_method_block(**QUANTILE_BLOCK)


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
    "See `results/hy_ig_v2_spy/tournament_results_20260410.csv` for the full "
    "leaderboard."
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
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12 | "
    "~6,500 daily observations | Narrative: portal_narrative_hy_ig_v2_spy_20260410.md"
)
