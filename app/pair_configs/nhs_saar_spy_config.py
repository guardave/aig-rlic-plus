"""New Home Sales (SAAR) x SPY pair configuration (Rule APP-PT1).

Pair `nhs_saar_spy`, page 28. This is the SEASONALLY-ADJUSTED (SAAR, FRED
HSN1F) counterpart to the existing `nhs_spy` pair, which uses the
NOT-seasonally-adjusted series (HSN1FNSA) and must deseasonalise every signal.
Because HSN1F is already seasonally adjusted, growth and level signals are used
directly.

Framing (procyclical, low-confidence): New Home Sales is an early-cycle
housing leading indicator. The searched winner is the monthly growth signal
with a rolling 60-month median threshold, a 2-month lead, and a procyclical
orientation (hold SPY when home-sales momentum is above its rolling median).
OOS Sharpe 1.45 versus 0.99 buy-and-hold, max drawdown -13.1% versus -23.9%.
The direction comes out procyclical as expected, and Granger evidence is
significant at short lags (1-2 months), but the rule trades often (68 OOS
trades, ~7.2/year turnover) and the regime quartiles are hump-shaped (Q2
strongest, not a clean monotonic rise), so confidence is low. Values come from
`results/nhs_saar_spy/winner_summary.json`.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: New Home Sales (SAAR) as an Early-Cycle Housing Timing Overlay"
    PAGE_SUBTITLE = (
        "New Home Sales, seasonally adjusted annual rate (FRED HSN1F) x S&P "
        "500 (SPY), monthly housing-momentum signals tested against SPY "
        "returns with release-lag discipline."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.45 OOS, drawdown -13.1%: a housing-momentum timing "
        "overlay -- procyclical as expected, but it trades often and "
        "confidence is low"
    )

    PLAIN_ENGLISH = (
        "New Home Sales measures how many new single-family houses are sold "
        "each month, reported at a seasonally adjusted annual rate. Buyers "
        "commit before construction, so sales lead housing starts, permits, "
        "and the activity they drive. The natural prior is procyclical: "
        "stronger home-sales momentum should coincide with a healthier "
        "expansion and better equities. The searched winner holds SPY when "
        "monthly home-sales growth is above its rolling median and moves to "
        "cash otherwise. It improves risk-adjusted return and cuts drawdown, "
        "but it changes position often, so treat it as a search-found timing "
        "overlay, not a forecast."
    )

    WHERE_THIS_FITS = (
        "This is a housing leading-indicator signal tested against broad U.S. "
        "equities. It is the seasonally adjusted (SAAR) sibling of the "
        "not-seasonally-adjusted New Home Sales pair. The honest reading: the "
        "procyclical direction is genuine, but the tradable rule is a searched "
        "momentum overlay whose out-of-sample edge still needs a frozen-rule "
        "holdout confirmation."
    )

    ONE_SENTENCE_THESIS = (
        "SPY timing improves in the searched sample when monthly New Home "
        "Sales growth is above its rolling median, applied with a 2-month "
        "lead, but the rule trades frequently and the economics are "
        "regime-dependent."
    )

    KPI_CAPTION = (
        "the search-phase OOS winner uses monthly New Home Sales growth, a "
        "rolling 60-month median threshold, and a 2-month lead. It earns "
        "Sharpe 1.45 versus 0.99 for buy-and-hold, with drawdown -13.1% "
        "versus -23.9%."
    )

    HERO_TITLE = "New Home Sales (SAAR) vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: New Home Sales (SAAR) is shown with SPY on the same "
        "time axis. Gray bands are NBER recessions; pink bands mark periods "
        "when home sales were contracting year over year."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by New Home Sales Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1, the lowest home-sales "
        "regime, to Q4, the highest. In this sample forward SPY Sharpe is "
        "hump-shaped -- weakest in Q1 and strongest in the middle regimes -- "
        "rather than rising cleanly, which is why the tradable signal uses "
        "momentum rather than the raw level."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning strategy is a **monthly home-sales momentum rule**. It looks at the one-month growth in New Home Sales (SAAR), waits two months before applying the signal, and holds SPY only when that lagged growth is above its rolling 60-month median. Out-of-sample, this rule earns a Sharpe ratio of 1.45 versus 0.99 for buy-and-hold, with maximum drawdown of -13.1% versus -23.9%.

### The Housing-Cycle Hypothesis

New Home Sales is one of the earliest housing signals. A buyer signs a contract before a house is built, so sales turn before starts, before completions, and before the construction jobs and spending they generate. That makes New Home Sales a classic early-cycle leading indicator, and the natural hypothesis is procyclical: when housing demand accelerates, the broader expansion tends to be intact and equities tend to do well.

Here the direction comes out procyclical as expected, and short-lag Granger tests are statistically significant. The two-month lead is consistent with a signal that needs a little time to be confirmed before it is acted on.

### Why Timing Is Difficult

New Home Sales is volatile month to month and is revised after its initial release. The rolling-median momentum rule reacts to that noise by changing position often -- roughly seven position changes a year in the out-of-sample window. The regime quartiles are also hump-shaped rather than cleanly monotonic: forward SPY Sharpe is weakest when home sales are lowest but peaks in the middle regimes, not the highest. This dashboard therefore treats the pair as a searched housing-momentum overlay: useful for improving the risk-adjusted path, but not a clean, low-turnover forecast.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "Housing held up relatively well while equities fell through "
                "the dot-com bear market. New Home Sales stayed firm on low "
                "rates, so the housing signal did not warn of the equity "
                "drawdown."
            ),
            "caption": "Dot-Com: housing stayed firm as equities fell.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "New Home Sales collapsed ahead of and through the Global "
                "Financial Crisis. This is the episode where the early-cycle "
                "housing signal was most informative about broad economic "
                "stress."
            ),
            "caption": "GFC: home sales collapsed early and hard.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "During coronavirus disease 2019 (COVID-19), New Home Sales "
                "dropped abruptly and then rebounded sharply as rates fell. "
                "The move was fast and policy-driven rather than a normal "
                "cycle turn."
            ),
            "caption": "COVID: sharp drop then a rapid rate-driven rebound.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "In the 2022 rate-hike cycle, higher mortgage rates slowed "
                "New Home Sales while SPY also sold off. Housing weakness and "
                "equity weakness moved together in this episode."
            ),
            "caption": "2022: higher rates slowed sales as equities fell.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The zoom charts show why the signal is useful but imperfect. New Home Sales was highly informative in the Global Financial Crisis, when it collapsed early, but it held firm through the dot-com equity bear market and moved abruptly during COVID. The strongest reading is not "housing predicts every drawdown"; it is that home-sales momentum can help size equity exposure through the housing cycle.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this housing-momentum story survives "
        "correlation, lead-lag, regime, and strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether New Home Sales signals and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster home-sales growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal. Positive values mean stronger "
        "home-sales growth lines up with stronger future SPY returns; negative "
        "values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the raw linear relationship is modest, which is why "
        "the tradable rule uses a lagged momentum threshold rather than the "
        "correlation directly."
    ),
    observation=(
        "New Home Sales growth is noisy, so the linear correlation with "
        "forward SPY returns is modest and depends on the horizon."
    ),
    interpretation=(
        "Correlation alone is not enough to trade the pair. The more relevant "
        "question is whether a lagged home-sales momentum threshold improves "
        "portfolio behavior."
    ),
    key_message="New Home Sales is useful as early-cycle context, not as a simple linear SPY predictor.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does New Home Sales lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag. Values below the 0.05 line mark "
        "lags where past home-sales growth adds statistically significant "
        "forecast information."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: New Home Sales-to-SPY p-values are significant at "
        "short lags (1-2 months) in the generated table, consistent with an "
        "early-cycle lead."
    ),
    observation=(
        "The generated Granger table shows significant home-sales-to-SPY "
        "evidence at lags 1-2, fading at longer lags."
    ),
    interpretation=(
        "This supports a short-horizon lead but does not prove causality. The "
        "strategy should still be framed as a searched allocation overlay."
    ),
    key_message="Short-lag lead-lag evidence is present but modest; use the signal cautiously.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the New Home Sales level and "
        "compares subsequent SPY returns across housing regimes."
    ),
    question="Do low and high home-sales regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest home-sales regime; Q4 is the highest. Compare "
        "Sharpe, average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: forward SPY Sharpe is hump-shaped -- lowest in Q1 "
        "and highest in the middle regimes (Q2), not rising cleanly to Q4."
    ),
    observation=(
        "Forward SPY Sharpe rises from about 0.38 in Q1 to a peak near 1.10 "
        "in Q2, then eases through Q3 and Q4."
    ),
    interpretation=(
        "The raw level is not cleanly monotonic, which is why the tradable "
        "rule uses momentum (the change in home sales) rather than the level."
    ),
    key_message="Home-sales momentum is more informative than the raw level.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters persistence before testing "
        "whether one series tends to move before or after the other."
    ),
    question="At which offsets does the home-sales signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the confidence band mark unusual lead-lag correlation "
        "after filtering autocorrelation."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the relationship is timing-sensitive and should not "
        "be read as a stable clock."
    ),
    observation=(
        "New Home Sales growth is noisy, so most cross-correlation bars sit "
        "inside the confidence band; the informative offsets are short."
    ),
    interpretation=(
        "The chart supports treating the pair as a short-horizon momentum "
        "overlay with variable timing rather than a mechanical forecast."
    ),
    key_message="Housing-to-equity timing is short-horizon and irregular.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the home-sales growth signal."
    ),
    question="How does SPY respond after New Home Sales growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a one-unit move in "
        "the 6-month New Home Sales growth signal. The sign shows the "
        "direction of the response by horizon."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: the local-projection results test the raw home-sales "
        "signal, not the final lagged tournament rule."
    ),
    observation=(
        "The chart helps separate raw housing relationships from the searched "
        "allocation rule."
    ),
    interpretation=(
        "If the response varies by horizon, that supports using explicit lead "
        "times in the tournament instead of assuming an immediate effect."
    ),
    key_message="The horizon matters for New Home Sales signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the home-sales signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does New Home Sales behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means the home-sales signal has a stronger association "
        "with that part of the SPY return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the signal can matter differently across weak and "
        "strong return states."
    ),
    observation=(
        "Tail sensitivity is relevant because housing turns are most "
        "informative around recessions and recoveries."
    ),
    interpretation=(
        "A state-dependent result is more plausible than one constant "
        "home-sales effect across all markets."
    ),
    key_message="New Home Sales should be read through regimes and tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: New Home Sales Leads, but the Tradable Edge Is a Searched Momentum Overlay",
    "overview": (
        "The evidence supports a cautious early-cycle housing overlay. The "
        "strategy winner improves search-phase OOS Sharpe and short-lag "
        "Granger tests are significant, but the rule trades often and the raw "
        "regime relationship is hump-shaped rather than monotonic."
    ),
    "plain_english": (
        "This page asks whether New Home Sales helps with SPY timing. The "
        "answer is: partly. The best rule uses lagged home-sales momentum, so "
        "it should be treated as an early-cycle housing overlay, not a "
        "low-turnover forecast."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 252 valid strategy combinations across six New "
        "Home Sales transforms, fixed and rolling thresholds, procyclical and "
        "countercyclical orientations, and leads from 0 to 12 months. The "
        "selected winner is `nhs_mom / T_roll_p50 / P1_long_cash / L2` with a "
        "procyclical orientation."
    ),
    "transition": (
        "**Transition:** the evidence is useful but the edge is searched. The "
        "Strategy page shows the exact long/cash rule, threshold, and "
        "deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged New Home Sales Momentum Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using monthly New Home Sales (SAAR) "
        "growth, a rolling 60-month median threshold, and a 2-month lead."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when monthly New Home Sales growth from two months "
        "earlier is above its rolling median. Otherwise it holds cash. This is "
        "a lagged housing-momentum rule, not a real-time recession forecast."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/nhs_saar_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/nhs_saar_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/nhs_saar_spy/tournament_results_20260804.csv"},
        {"label": "Stationarity tests", "path": "results/nhs_saar_spy/stationarity_tests_20260804.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the lagged monthly growth in New Home Sales (SAAR) is above its rolling 60-month median threshold; otherwise hold cash.

If-then form:
- **IF** `nhs_mom` from 2 months earlier is above the rolling 60-month median threshold -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2026-06-30): Sharpe 1.45 versus 0.99 buy-and-hold; annualized return 16.7% versus 15.4%; maximum drawdown -13.1% versus -23.9%; 68 OOS trades; annual turnover 7.2.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads New Home Sales at a seasonally adjusted annual rate (`HSN1F`) and converts it to month-end observations. Second, it computes the one-month growth in New Home Sales. Third, it applies a 2-month lag before the SPY allocation is set. Finally, the lagged signal is compared with a rolling 60-month median threshold.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read New Home Sales (SAAR) at month end.
2. Compute the one-month growth in New Home Sales.
3. Compare the value from 2 months earlier with its rolling 60-month median threshold.
4. Hold SPY when the lagged signal is above the threshold; otherwise hold cash.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule reduces damage in several "
        "periods, but it is not designed to make every crisis profitable."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 6-month growth in New Home "
            "Sales; the target is SPY returns. The rolling correlation tests "
            "whether their linear relationship is stable through time. Large "
            "swings mean the strategy needs rolling thresholds and ongoing "
            "monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break test asks whether the New "
            "Home Sales-SPY relationship changes enough that one fixed model "
            "is unlikely to describe the whole sample. A larger break "
            "statistic means the relationship changed more materially across "
            "periods."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "strategy combinations, with the selected rule highlighted as the "
        "best search-phase result."
    )

    CAVEATS_MD = """
**Main caveats:**

1. New Home Sales is volatile month to month and is revised after its initial release.
2. The rule trades often (about seven position changes a year out-of-sample), so transaction costs and slippage matter more than for a slow signal.
3. The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
4. SPY price sourcing can fall back to an existing local monthly panel if the live Yahoo Finance call is rate-limited.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged monthly New Home Sales growth signal moves above "
        "its rolling median threshold, taking exposure from 0% to 100% SPY. A "
        "SELL moves back to cash when the condition no longer holds."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-08-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged nhs_mom above rolling p50; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED | `HSN1F`, New Home Sales, seasonally adjusted annual rate | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is New Home Sales at a seasonally adjusted annual rate, "
    "in thousands of units. Because HSN1F is already seasonally adjusted, no "
    "deseasonalisation is applied (unlike the not-seasonally-adjusted `nhs_spy` "
    "pair). The pipeline constructs one-month, three-month, six-month, and "
    "twelve-month growth rates; a 60-month rolling z-score; a six-month change "
    "in the level; and a housing-contraction flag. The winning signal is "
    "`nhs_mom`, the one-month growth in New Home Sales, used with a 2-month "
    "lead and a rolling 60-month median threshold."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does New Home Sales move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high home-sales regimes behave differently? | Makes the housing-cycle story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past New Home Sales information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: New Home Sales transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x lead times. The final tournament has 252 valid strategy combinations. The winning rule is `nhs_mom / T_roll_p50 / P1_long_cash / L2` with a procyclical orientation.
"""

_REFERENCES_MD = """
1. Federal Reserve Economic Data (FRED), `HSN1F`, New One Family Houses Sold: United States (SAAR).
2. Yahoo Finance, SPY adjusted price history.
3. U.S. Census Bureau and U.S. Department of Housing and Urban Development, New Residential Sales.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Monthly sample from 1993-01-31 to 2026-06-30, with out-of-sample "
        "window 2017-01-31 to 2026-06-30. SPY history limits the usable "
        "sample even though HSN1F begins in 1963."
    ),
    plain_english=(
        "This page documents how New Home Sales (SAAR) was turned into "
        "testable signals, how the econometric checks were run, and how the "
        "tournament selected the final SPY allocation rule."
    ),
)
