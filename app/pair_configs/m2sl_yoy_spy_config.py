"""M2 Money Supply (YoY) x SPY pair configuration (Rule APP-PT1).

Pair `m2sl_yoy_spy`, Mode 1. Prose is sourced from Research Ray's
`docs/portal_narrative_m2sl_yoy_spy_20260619.md`; this file wires that prose
to the shared Streamlit templates and Vera's bare-name chart artifacts.

Evidence status is `found_in_search`, so headline performance is labelled as
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/m2sl_yoy_spy/winner_summary.json`.

This is a low-confidence, reverse-causal winner (modelled on
`ism_services_spy_config.py`): Toda-Yamamoto Granger finds NO forward signal
from M2 YoY growth to SPY at any lag, while SPY Granger-predicts M2 at lags
[1,2,3,4,5,8] -- the market moves first, money responds. The tradable signal
is money-growth ACCELERATION (the month-to-month change in M2's YoY rate), not
the level. The config deliberately frames the pair as a search-found
defensive/timing overlay, NOT as evidence that M2 leads the S&P 500.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Money-Growth Acceleration as a Low-Confidence Timing Overlay"
    PAGE_SUBTITLE = (
        "M2 money supply, year-over-year growth (FRED M2SL) x S&P 500 (SPY), "
        "monthly decision rules with release-lag discipline."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.69 OOS, drawdown -4.0%: a money-growth acceleration "
        "overlay -- but causality runs in reverse and confidence is low"
    )

    PLAIN_ENGLISH = (
        "M2 is the Federal Reserve's broad money aggregate. The natural prior "
        "is procyclical: easing liquidity should support stocks. The searched "
        "winner trades on whether money growth is SPEEDING UP or slowing down "
        "(the acceleration of M2's year-over-year growth), not on whether money "
        "growth is high or low. It improves risk-adjusted return, but the "
        "lead-lag tests run backward: the market predicts the money aggregate, "
        "not the other way around. Treat the edge as a search-found timing "
        "overlay, not a forecast."
    )

    WHERE_THIS_FITS = (
        "This is a monetary/liquidity macro signal tested against broad U.S. "
        "equities. The honest reading is narrow: the rule is a searched timing "
        "overlay whose edge is concentrated in one extraordinary monetary "
        "regime (the 2020-22 surge and contraction). It is NOT evidence that "
        "M2 money growth leads the S&P 500."
    )

    ONE_SENTENCE_THESIS = (
        "The winning M2-acceleration rule improves risk-adjusted return and "
        "drawdown, but it contradicts the direction of causality (SPY leads "
        "M2), trades a second-derivative transform rather than the level, and "
        "should be treated as a low-confidence searched candidate awaiting a "
        "final exam."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final "
        "holdout result. The winner was selected from 3,369 valid strategy "
        "combinations, with bootstrap p=0.025, and low confidence -- and the "
        "lead-lag evidence runs from SPY to M2, not the reverse."
    )

    HERO_TITLE = "M2 Money-Supply YoY Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: M2 year-over-year growth is shown against SPY on a "
        "shared time axis, with the 0% line marked and the 2020-21 surge "
        "(~27%) and first-ever 2022-23 contraction annotated. The winning rule "
        "trades the ACCELERATION of this growth (month-to-month change), not "
        "the level shown here."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by M2 Money-Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by M2 YoY-growth "
        "LEVEL quartile. The gradient runs the 'wrong' way -- Sharpe FALLS from "
        "Q1 (lowest money growth) at 1.06 to Q4 (highest) at 0.53, and Q4 "
        "carries a -47% drawdown. The highest-money-growth regime is the "
        "riskiest for equities concurrently -- a separate story from the "
        "acceleration winner."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning rule earns a Sharpe ratio -- return per unit of volatility -- of 1.69 versus 0.90 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves to -4.0% (400 basis points) from -23.9%, and annualized return is also higher, 17.6% versus 14.9%.

Those numbers look strong. Before trusting them, two honest framings matter and shape everything below: the signal is about whether money growth is **speeding up or slowing down**, not whether it is high or low; and the statistical tests say money does **not** lead the market -- if anything, the market leads money.

### The Honest Headline: Causality Runs in Reverse

The single most important result on this page is a negative one. Toda-Yamamoto Granger causality -- a test of whether the past values of one series help forecast another -- shows **no forward signal at all**: M2 year-over-year (YoY) growth does not Granger-cause SPY at any lag from 1 to 12 months. The reverse is what is significant: SPY Granger-causes M2 YoY growth at lags 1, 2, 3, 4, 5, and 8 months.

The honest reading is that the stock market moves first and the broad money aggregate responds afterward. M2 behaves as a coincident or lagging series with respect to equities, not a leading one. This pair is **not** evidence that watching the money supply lets you forecast stocks. The trading edge below comes from a search-found pattern in the *acceleration* of money growth, and it should be read as a timing overlay, not a forecast.

### Acceleration, Not Level

The tradable signal is **money-growth acceleration** -- the month-to-month change in M2's YoY growth rate (a "second-derivative" transform), not the YoY level itself. In plain terms, the rule asks "is money growth speeding up or slowing down?" rather than "is money growth high or low?" The first question beat the second in the strategy search.

The credible economic story is a hypothesis, not a fact: when money growth is accelerating, liquidity and credit conditions are easing, which can act as a risk-on tailwind for equities over the following couple of months. That is the pro-cyclical -- moving with the market cycle -- mechanism the search favored. It is plausible, but the reverse-causality verdict above means we cannot claim it as a proven forecasting channel.

<!-- expander: Why acceleration, not the level? -->
The level of money growth and the change in money growth tell different stories. The level quartiles (see the Evidence page) actually show that the *highest* money-growth regime is the *riskiest* for stocks concurrently -- high money growth often coincides with inflation and tightening worries. The acceleration transform sidesteps that by asking about direction of travel. The search found the acceleration framing tradable; it did not find the level framing tradable in the same way. We report them as two separate stories on purpose.
<!-- /expander -->
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The Dot-Com chart is included as a confirmer for continuity "
                "across the portal's standard episode set. Read it as "
                "contextual background, not the strongest validation case."
            ),
            "caption": "Contextual background; a continuity confirmer, not validation.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "During the Global Financial Crisis, M2 YoY growth gave no "
                "advance warning of the equity bear market -- a failure case "
                "for any forward-leading claim."
            ),
            "caption": "GFC: money gave no advance warning -- a failure case.",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During the coronavirus disease 2019 (COVID-19) shock, M2 YoY "
                "growth surged toward 27% while SPY crashed and then recovered "
                "-- money and the market moved together in the same window, a "
                "coincident episode rather than money leading."
            ),
            "caption": "COVID: money and market moved together (coincident, not leading).",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022 inflation shock, M2 YoY growth fell below 0% "
                "for the first time in the modern record while the Fed "
                "tightened and equities fell -- a second failure case for "
                "forward causality, and the vivid first-ever contraction."
            ),
            "caption": "2022: first-ever M2 contraction during the drawdown -- a failure case.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history zoom charts make the caveats tangible, and they are chosen to teach the lagging character honestly. During COVID-19, M2 YoY growth surged toward 27% while SPY crashed and then recovered -- money and the market moved together, a coincident episode rather than money leading. During the GFC, M2 YoY growth gave no advance warning of the equity bear market -- a failure case for any forward-leading claim. During the 2022 inflation shock, M2 YoY growth fell below 0% for the first time in the modern record while the Fed tightened and equities fell -- a second failure case, and the vivid first-ever contraction. The Dot-Com window is a confirmer for continuity across the portal's standard episode set, not a validation case.
"""

    TRANSITION_TEXT = (
        "The historical story is a lagging-money one, so the full evidence "
        "suite matters. The Evidence page leads with the causality result -- "
        "which runs backward -- before the supporting checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
QUANTILE_CHART_NAME = "quantile_coef"
TRANSFER_ENTROPY_CHART_NAME = "transfer_entropy"
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag (Both Directions)",
    method_theory=(
        "Toda-Yamamoto Granger causality tests whether past values of one "
        "series improve forecasts of the other beyond its own history, in a "
        "form robust to integration order."
    ),
    question="Does M2 money growth lead SPY -- or does SPY lead the money aggregate?",
    how_to_read=(
        "Bars are F-statistics by monthly lag; bars above the dashed line are "
        "significant at the 5% level. The dark-blue bars are SPY leading M2; "
        "the pale-blue bars are M2 leading SPY. A leading indicator would have "
        "the pale-blue bars crossing the line -- they do not."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: the forward direction (M2 to SPY) clears the line at "
        "NO lag; the reverse direction (SPY to M2) is significant at lags "
        "1, 2, 3, 4, 5, and 8."
    ),
    observation=(
        "Forward Granger support is absent at all lags 1-12; reverse "
        "SPY-to-M2 support is present at lags 1, 2, 3, 4, 5, and 8."
    ),
    deep_dive_title="Why is reverse causality the headline?",
    deep_dive_content=(
        "If SPY moves first and the money aggregate follows, M2 is summarizing "
        "conditions investors have already priced. That makes M2 a "
        "coincident/lagging reflection of the market, not a leading indicator "
        "of it -- so any forward-trading edge is suspect."
    ),
    interpretation=(
        "The lead-lag evidence points backward. This is the central reason "
        "confidence is low despite the headline Sharpe."
    ),
    key_message="Causality runs from SPY to M2, not the reverse.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Level Quartile Gradient",
    method_theory=(
        "Quartile analysis sorts months into four buckets by M2 YoY-growth "
        "LEVEL and compares subsequent SPY performance. It is descriptive "
        "(concurrent), not the trading rule."
    ),
    question="Do higher or lower money-growth levels line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 (lowest money growth) to Q4 (highest). A clean "
        "rising gradient would support 'more money is better for stocks'; the "
        "actual gradient runs the other way."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Sharpe FALLS from Q1 (lowest M2 YoY) at 1.06 to Q4 "
        "(highest) at 0.53, and Q4 carries a -47% drawdown."
    ),
    observation=(
        "The gradient is inverted: the highest-money-growth quartile has the "
        "worst forward Sharpe and the deepest drawdown."
    ),
    interpretation=(
        "The highest-money-growth regime is the riskiest for equities "
        "concurrently -- consistent with very fast money growth coinciding "
        "with inflation and tightening risk. This is a separate story from the "
        "acceleration winner, kept separate on purpose."
    ),
    key_message=(
        "High money growth is the riskiest regime -- the level story is "
        "contrarian, not 'more money is better'."
    ),
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation removes each series' own persistence "
        "before checking whether one echoes the other at monthly offsets."
    ),
    question="Is there a clean forward lead-lag echo after removing autocorrelation?",
    how_to_read=(
        "Bars outside the confidence band indicate statistically meaningful "
        "offsets. Positive lags would mark M2 growth leading SPY."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF does not establish a clean forward lead from "
        "M2 growth to SPY, consistent with the Granger result."
    ),
    observation=(
        "The cross-correlation does not produce a clean forward-lead signal."
    ),
    interpretation=(
        "The CCF reinforces the same conclusion as Granger: there is no "
        "reliable forward lead from money growth to SPY."
    ),
    key_message="The cross-correlation check does not support a forward lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after a move in money growth."
    ),
    question="Does an M2-growth move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward M2-to-SPY responses are not statistically "
        "significant at any horizon (minimum p approximately 0.62); the "
        "confidence bands include zero throughout."
    ),
    observation=(
        "Forward responses are insignificant at 1, 3, 6, and 12 months."
    ),
    interpretation=(
        "Local projections tell the same backward-causality story as Granger "
        "and CCF: no forward predictive content."
    ),
    key_message="Local projections also point backward, not forward.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression asks whether the relationship differs in weak, "
        "normal, and strong SPY-return environments."
    ),
    question="Is the signal coherent across the return distribution?",
    how_to_read=(
        "Read coefficient estimates across return quantiles. A clean forward "
        "predictor would show a coherent, stable pattern."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: coefficients are most negative in the lowest return "
        "quantiles -- not the profile of a clean forward predictor."
    ),
    observation=(
        "The quantile estimates are most negative in the low return quantiles."
    ),
    interpretation=(
        "That pattern does not support a simple, coherent forward channel from "
        "money growth to SPY."
    ),
    key_message="Quantile evidence is not the profile of a forward predictor.",
)

TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy is a nonlinear information-flow check that can catch "
        "relationships missed by linear tests."
    ),
    question="Is there nonlinear directed information flow, and in which direction?",
    how_to_read=(
        "Small permutation p-values indicate genuine directed information "
        "flow. Compare the forward and reverse channels."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: forward M2-to-SPY is not significant (p approximately "
        "0.20); only the reverse SPY-to-M2 channel is (p approximately 0.03)."
    ),
    observation=(
        "The reverse channel is the significant one even under a nonlinear test."
    ),
    interpretation=(
        "Transfer entropy is reverse-only too, consistent with the rest of "
        "the evidence bundle."
    ),
    key_message="Even the nonlinear check is reverse-only.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the money-growth series into latent "
        "high-variance regimes."
    ),
    question="When did M2 money growth sit in unusual regimes?",
    how_to_read=(
        "Higher regime probability marks months where money-growth behavior "
        "looks unusual relative to the long sample."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the high-variance regime probability pins near 1.0 "
        "through the 2020-21 money surge -- useful as context, not as the "
        "winning trading signal."
    ),
    observation=(
        "The HMM highlights the 2020-21 surge and other high-variance money "
        "environments."
    ),
    interpretation=(
        "The regime map explains the monetary backdrop, but the winning rule "
        "is the acceleration threshold, not HMM probability; it does not "
        "rescue the statistical fragility."
    ),
    key_message="The HMM explains backdrop; it does not validate the winner.",
)

EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence leads with causality -- and the causality runs backward",
    "overview": (
        "The headline lead-lag tests find no forward signal from M2 money "
        "growth to SPY, while SPY predicts the money aggregate at lags "
        "1, 2, 3, 4, 5, and 8. The level quartiles show high money growth is "
        "the riskiest regime, and supporting checks (local projections, "
        "transfer entropy, quantile regression) tell the same backward, "
        "low-confidence story."
    ),
    "plain_english": (
        "This section asks whether M2 money growth really helps predict future "
        "SPY performance. The tests point the other way: the market appears to "
        "lead the money aggregate, not vice versa. That is why the strong "
        "headline Sharpe is treated as a low-confidence searched result."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/m2sl_yoy_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/m2sl_yoy_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/m2sl_yoy_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/m2sl_yoy_spy/rolling_correlation_m2sl_yoy_spy.csv"},
        {"label": "Stationarity tests", "path": "results/m2sl_yoy_spy/stationarity_tests_20260619.csv"},
    ],
    "level1": [GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Granger Causality", "Level Quartiles", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK, HMM_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy", "HMM Regimes"],
    "tournament_intro": (
        "The tournament tested 4,720 benchmark-excluded strategy combinations, "
        "of which 3,369 passed validity filters. The winning rule is the best "
        "of that valid searched set, so its Sharpe advantage must be read with "
        "the search-position warning attached."
    ),
    "transition": (
        "**Transition:** the evidence does not support a forward-leading "
        "signal. The strategy page shows what the rule actually is: a "
        "search-found Long/Cash acceleration overlay whose drawdown win is "
        "concentrated in one monetary regime."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Money-Growth Acceleration Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched timing overlay: better Sharpe, drawdown, and return than "
        "buy-and-hold in the OOS window -- but no forward causality, "
        "found_in_search, and low statistical confidence."
    )

    PLAIN_ENGLISH = (
        "The rule is simple: when money-growth acceleration (the month-to-month "
        "change in M2's YoY growth rate) two months earlier was above its "
        "historical-median pace, hold SPY; otherwise hold cash. It improved "
        "Sharpe and drawdown in the search-phase OOS window, but the lead-lag "
        "tests say money does not lead the market, so this is a timing overlay, "
        "not a forecast."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when money-growth acceleration (the month-to-month change in M2's year-over-year growth rate) from two months ago is greater than 0.0523 percentage points; otherwise hold cash.

If-then form:
- **IF** `m2sl_yoy_accel_pct` from 2 months ago is **above 0.0523** -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2018-01-31 to 2026-04-30, no holdout final exam yet): Sharpe 1.69 vs 0.90 buy-and-hold; annualized return 17.6% vs 14.9%; maximum drawdown -4.0% vs -23.9%; 31 OOS position changes; annual turnover 3.72; OOS win rate 37%.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Federal Reserve's monthly M2 money-stock release (FRED series M2SL) and computes its year-over-year growth -- this month's money stock versus the same month a year ago. Second, it takes the change in that growth rate from one month to the next; this is the "acceleration" -- is money growth speeding up or slowing down? Third, it compares the value from two months earlier (respecting the publication lag, so no future information is used) against the historical-median threshold and converts that comparison into a SPY-or-cash position.

This is intentionally simple. It does not forecast inflation, model the Fed's reaction function, or claim that money drives stocks. It asks whether one summary of the liquidity backdrop has historically lined up with a better or worse SPY allocation -- and, as the Evidence page is careful to say, the statistical tests do not establish that money leads the market.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read M2 money supply (`M2SL`) from the live FRED API at the current vintage.
2. Compute year-over-year growth, then the month-to-month change in that growth rate (the acceleration transform).
3. Apply the 2-month lag (the publication-lag-respecting floor) before making the monthly SPY allocation decision.
4. Compare the lagged acceleration with the fixed threshold `0.0523`.
5. Hold SPY when the lagged signal is greater than the threshold; otherwise hold cash.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam, and the lead-lag evidence runs from SPY to M2, not the reverse.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Only COVID 2020 "
        "falls inside the 2018-onward OOS window and is evaluable; the "
        "Dot-Com, GFC, and China 2015 episodes predate the OOS split and are "
        "marked insufficient data -- which is why durability is only "
        "conditionally durable."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 3,369 valid "
        "searched combinations, with the median below buy-and-hold. The "
        "winner's 1.69 Sharpe is the maximum of the search, not a typical "
        "result."
    )

    CAVEATS_MD = """
**Why confidence is low:**

1. The lead-lag evidence runs backward: SPY Granger-predicts M2 YoY growth at lags 1, 2, 3, 4, 5, and 8, while M2 predicts SPY at none. M2 behaves as a coincident/lagging reflection of the market.
2. The signal is an ACCELERATION (second-derivative) transform, not the level -- and the level quartiles separately show high money growth is the riskiest regime.
3. The winner came from 3,369 valid searched combinations; bootstrap p-value is 0.025 (clears the 5% bar) but is search-conditioned, not a fresh confirmation.
4. The rule is marked `found_in_search` -- it has NOT been confirmed on an untouched final-exam window. In-sample Sharpe is 0.36 versus OOS 1.69.
5. Durability is only `conditionally_durable`: the OOS window (2018-2026) is dominated by the 2020 money surge and the 2022 contraction -- a single unusual monetary regime -- and COVID is the only evaluable stress episode.
6. The drawdown win (-4.0% versus -23.9%) is real but **episode-shaped** -- it leans heavily on stepping aside during 2022.

**What this means:** use the page as evidence for a candidate search-found timing overlay, not as proof that M2 money growth leads the S&P 500.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged money-growth acceleration crosses back above its "
        "0.0523 median threshold, moving from 0% to 100% SPY exposure, and a "
        "SELL back to cash when the lagged acceleration falls below the "
        "threshold. Over the OOS window the rule made 31 such position changes."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: m2sl_yoy_accel_pct > 0.0523; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Federal Reserve via live FRED API (current vintage) | `M2SL` M2 money stock (seasonally adjusted) | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw M2 **level** is non-stationary (augmented Dickey-Fuller p "
    "approximately 0.99) and is therefore EXCLUDED from the signal set. Only "
    "stationary growth and transform series are used: year-over-year growth, "
    "month-over-month growth, 3- and 6-month growth, the acceleration "
    "transform (the month-to-month change in YoY growth), and a rolling "
    "z-score. The winning signal is `m2sl_yoy_accel_pct`, money-growth "
    "acceleration, evaluated against a fixed median threshold of 0.0523 with a "
    "2-month lead. The daily panel carries the latest released monthly value "
    "forward, so the strategy does not use future money-supply information. M2 "
    "is heavily revised; the live FRED API is treated as ground truth (the "
    "project Data Master snapshot is a stale vintage about 0.5% above current "
    "FRED at recent dates)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger | Do lagged money values improve SPY forecasts -- or the reverse? | Formal lead-lag test, robust to integration order |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM regimes | Which months are unusual money-growth regimes? | Backdrop and regime context, not the winning signal |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: M2 transforms x threshold rules x strategy families x orientations x leads x lookbacks. The final tournament file has 4,720 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 3,369 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `m2sl_yoy_accel_pct / T1_fixed_p50 / P1_long_cash / L2 / LB_NA`.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/m2sl_yoy_spy/evidence_status.json` marks the pair `found_in_search`. The lead-lag evidence runs from SPY to M2, reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. Board of Governors of the Federal Reserve System, H.6 Money Stock Measures (M2SL), via FRED.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Simonsohn, U., Simmons, J. P. & Nelson, L. D. (2020). "Specification curve analysis."
7. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Out-of-sample window 2018-01-31 to 2026-04-30, 100 monthly "
        "observations; in-sample ends before the 2018 split. Total tournament "
        "count is 4,720 benchmark-excluded strategy combinations; 3,369 are "
        "valid. Evidence status: found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the M2 money-growth analysis. The most "
        "important limitation is that the lead-lag tests point backward (SPY "
        "predicts M2), the tradable signal is an acceleration transform rather "
        "than the level, and the winning rule still needs a frozen-rule "
        "holdout test."
    ),
)
