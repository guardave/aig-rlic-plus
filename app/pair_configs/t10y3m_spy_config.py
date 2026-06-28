"""10Y-3M Treasury Spread x SPY pair configuration (Rule APP-PT1)."""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Yield-Curve Steepening as a Risk-On SPY Signal"
    PAGE_SUBTITLE = (
        "10-year minus 3-month Treasury spread (FRED T10Y3M) x S&P 500 (SPY), "
        "monthly rules tested against forward SPY returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.32 OOS: the winning rule buys SPY after the 10Y-3M spread "
        "has been steepening for three months"
    )

    PLAIN_ENGLISH = (
        "The 10Y-3M US Treasury spread is the 10-year US Treasury yield minus the "
        "3-month US Treasury yield. An inverted curve, where the spread falls "
        "below zero, is a common "
        "warning sign. This pair tests whether that rates signal can improve "
        "SPY timing."
    )

    WHERE_THIS_FITS = (
        "This is a rates and recession-risk signal for broad U.S. equities. "
        "It belongs in the portal as a macro timing overlay: useful for "
        "risk-on/risk-off context, but not a standalone trading system."
    )

    ONE_SENTENCE_THESIS = (
        "SPY tends to perform better when the 10Y-3M spread has recently "
        "steepened, but curve signals can be early and must be treated as "
        "risk-cycle context rather than precise market timing."
    )

    KPI_CAPTION = (
        "the search-phase OOS winner uses the 3-month change in the 10Y-3M "
        "spread, a rolling 60-month 75th percentile threshold, and a 6-month "
        "lead. It earns Sharpe 1.32 versus 0.93 for buy-and-hold."
    )

    HERO_TITLE = "10Y-3M Treasury Spread vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the 10Y-3M spread is shown with SPY on the same time "
        "axis. Shaded recession bands provide historical context. Values below "
        "zero mark yield-curve inversion; rising values mark steepening."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by 10Y-3M Spread Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (inverted or flat curve) "
        "to Q4 (steep curve). In this sample Q1 and Q2 have stronger forward "
        "Sharpe than the steepest quartile, which means the level relationship "
        "is not a simple 'steeper is always better' story."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning strategy is a **3-month steepening rule**. It looks at the 3-month change in the 10Y-3M Treasury spread, waits six months before applying the signal, and holds SPY only when the lagged signal is above its rolling 60-month 75th percentile threshold. Out-of-sample, this rule earns a Sharpe ratio of 1.32 versus 0.93 for buy-and-hold, with maximum drawdown of -4.7% versus -23.9%.

### The Yield-Curve Hypothesis

The economic idea is straightforward. A steepening yield curve usually means short rates are no longer tight relative to long rates, or markets expect easier policy and better growth ahead. That setting can support equity risk-taking. A flat or inverted curve usually means policy is restrictive and recession risk is higher, which can make future SPY returns more fragile.

The tested result is more nuanced than the textbook story. The winning signal is not the level of the curve. It is the **recent change** in the curve. The rule responds to steepening momentum, not just whether the curve is high, low, or inverted.

### Why Timing Is Difficult

Yield-curve signals are often early. The curve can invert long before equities fall, and it can stay inverted while the market rallies. That is why this dashboard treats the signal as recession-risk context and tests many lags. The selected 6-month lead says the historical edge appears after a delay, not immediately.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The curve inverted before the 2001 recession and equity "
                "drawdown, showing why the 10Y-3M spread is watched as an "
                "early recession-risk indicator."
            ),
            "caption": "Dot-Com: inversion arrived before the recession window.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The curve inverted in 2006 before the Global Financial "
                "Crisis. The warning was early, which is useful for risk "
                "management but hard for exact trade timing."
            ),
            "caption": "GFC: useful warning, but with a long lead time.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The curve briefly inverted before the coronavirus disease "
                "2019 (COVID-19) shock, but the pandemic itself was an "
                "exogenous event. Treat this as a stress-context chart, not "
                "proof that the curve caused the drawdown."
            ),
            "caption": "COVID: stress context, not a causal explanation.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "The 2022-24 inversion was deep and persistent while SPY "
                "eventually recovered. This is the central caveat: inversion "
                "can warn about macro pressure without giving precise market "
                "entry and exit dates."
            ),
            "caption": "2022: inversion stayed cautionary while equities recovered.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show the main strength and weakness of yield-curve timing. Before the Dot-Com and Global Financial Crisis recessions, inversion gave an early warning. Around COVID-19, the signal was less clean because the shock was not caused by the rates cycle. During 2022-24, inversion stayed severe while equities recovered, proving that the curve can be directionally useful but tactically early.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this rates story survives formal "
        "correlation, lead-lag, regime, and strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether the yield-curve signal and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does a higher 10Y-3M spread line up with better future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and correlation type. Positive values "
        "mean higher curve readings line up with stronger future SPY returns; "
        "negative values mean the opposite. The p-value columns in the CSV "
        "show whether the relationship is statistically distinguishable from "
        "noise."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the level relationship is weak and horizon-dependent, "
        "which is why the strategy search favored a change signal rather than "
        "the raw spread level."
    ),
    observation=(
        "The raw spread level has modest negative Pearson correlation with "
        "3- and 6-month forward SPY returns in this sample, while the winning "
        "strategy uses the 3-month change in the spread."
    ),
    interpretation=(
        "Linear correlation alone is not enough to justify the pair. The "
        "economic story depends on rates-cycle change and lag structure, so "
        "the downstream evidence and tournament matter."
    ),
    key_message="The raw level is not the whole signal; steepening momentum is the tradable feature.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does the 10Y-3M spread lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show F-statistics by monthly lag. The p-values in the source "
        "CSV determine significance; lower p-values indicate stronger evidence "
        "that one series adds forecasting information for the other."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: Granger evidence is not strong at conventional "
        "thresholds, so the page frames the yield curve as a searched risk "
        "overlay rather than a proven causal forecast."
    ),
    observation=(
        "The generated Granger table does not show significant 10Y-3M-to-SPY "
        "or SPY-to-10Y-3M causality at lags 1-6 in the displayed result."
    ),
    interpretation=(
        "This weak formal lead-lag evidence lowers confidence. It does not "
        "erase the strategy result, but it prevents a strong causal claim."
    ),
    key_message="Use the signal as risk-cycle evidence, not as proof of causality.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the 10Y-3M spread level and "
        "compares subsequent SPY returns across curve regimes."
    ),
    question="Do inverted, normal, and steep-curve regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest or most inverted curve regime; Q4 is the steepest "
        "curve regime. Compare Sharpe, average return, and drawdown across "
        "the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Q1 and Q2 have stronger forward Sharpe than the "
        "steepest Q4 bucket in this sample."
    ),
    observation=(
        "Q1 inverted/flat has Sharpe 1.12, Q2 has 1.06, Q3 has 0.50, and "
        "Q4 steep has 0.41."
    ),
    interpretation=(
        "The level quartiles do not support a simple monotonic story. This "
        "reinforces why the winning rule uses curve steepening momentum "
        "rather than the raw level alone."
    ),
    key_message="The level regime is descriptive; the winning signal is the 3-month change.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters autocorrelation before testing "
        "whether one series tends to move before or after the other."
    ),
    question="At which offsets does the yield-curve signal echo SPY returns?",
    how_to_read=(
        "Bars outside the confidence band mark statistically unusual "
        "lead-lag correlation after filtering persistence from the series."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the CCF evidence is sparse, so the relationship is "
        "not a clean mechanical lead-lag pattern."
    ),
    observation=(
        "Only a limited number of offsets clear the confidence band, with the "
        "most visible exception around lag -5 in the generated table."
    ),
    interpretation=(
        "The yield curve contains macro timing information, but the timing is "
        "irregular. That matches the economic caveat that inversion and "
        "steepening can lead market outcomes by variable amounts."
    ),
    key_message="The timing link exists, but it is not a clockwork relationship.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the yield-curve signal."
    ),
    question="How does SPY respond over time after the 10Y-3M signal moves?",
    how_to_read=(
        "Each point is an estimated response at a forward horizon. Confidence "
        "bands show uncertainty around the estimate."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: horizon-by-horizon response estimates are mixed, "
        "which supports a medium-confidence rather than high-confidence label."
    ),
    observation=(
        "The response path does not show a uniformly strong positive effect "
        "at every horizon."
    ),
    interpretation=(
        "Local projections support caution: the relationship is economically "
        "plausible but not statistically clean at all horizons."
    ),
    key_message="The response is horizon-dependent, not uniformly strong.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the signal matters differently in "
        "weak, normal, and strong SPY return environments."
    ),
    question="Does the yield-curve signal behave differently in market tails?",
    how_to_read=(
        "Compare coefficients across quantiles. A tail-only effect means the "
        "signal mainly matters in unusually weak or strong return states."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: coefficient strength varies across the distribution, "
        "so the relationship is better read as regime-sensitive."
    ),
    observation=(
        "The signal's effect is not identical across return quantiles."
    ),
    interpretation=(
        "This is consistent with a recession-risk overlay: yield-curve "
        "information may matter most when the market is near transition "
        "points rather than in normal months."
    ),
    key_message="The signal is regime-sensitive, not a uniform monthly predictor.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Yield-Curve Timing Is Useful but Early",
    "overview": (
        "The evidence supports a medium-confidence rates overlay. The strategy "
        "winner is strong in the search-phase OOS window, but formal lead-lag "
        "tests are not decisive and level quartiles are not monotonic."
    ),
    "plain_english": (
        "This page asks whether the 10Y-3M Treasury spread really helps with "
        "SPY timing. The answer is: partly. The strategy result is useful, "
        "but the statistical evidence says to treat it as a risk overlay, not "
        "a guaranteed forecast."
    ),
    "downloads": [
        {"label": "Granger causality by lag", "path": "results/t10y3m_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/t10y3m_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/t10y3m_spy/tournament_results_20260620.csv"},
        {"label": "Stationarity tests", "path": "results/t10y3m_spy/stationarity_tests_20260620.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 1,008 benchmark-excluded strategy combinations, "
        "with 775 valid strategy rows. The selected winner is "
        "`t10y3m_3m_chg / T2_roll_p75 / P1_long_cash / L6 / LB60`."
    ),
    "transition": (
        "**Transition:** the evidence is useful but not absolute. The Strategy "
        "page shows the exact rule, thresholds, and deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A 10Y-3M Steepening Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 3-month change in the "
        "10Y-3M Treasury spread, a rolling 75th percentile threshold, and a "
        "6-month lead."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 10Y-3M spread had steepened enough six "
        "months earlier. Otherwise it holds cash. The idea is that a clear "
        "steepening move can signal improving future conditions, but the lag "
        "keeps the rule from reacting too early."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the lagged 3-month change in the 10Y-3M Treasury spread is above its rolling 60-month 75th percentile threshold; otherwise hold cash.

If-then form:
- **IF** `t10y3m_3m_chg` from 6 months earlier is above the rolling 75th percentile threshold -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-10-31 to 2025-11-30): Sharpe 1.32 versus 0.93 buy-and-hold; annualized return 10.7%; maximum drawdown -4.7% versus -23.9%; 16 OOS trades; annual turnover 1.94.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the 10-year minus 3-month Treasury spread (`T10Y3M`) and converts it to month-end observations. Second, it computes the 3-month change in that spread, so the signal measures steepening or flattening momentum rather than the raw level. Third, it applies a 6-month lag before the SPY allocation is set. Finally, the lagged signal is compared with a rolling 60-month 75th percentile threshold.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the 10Y-3M Treasury spread (`T10Y3M`) at month end.
2. Compute the 3-month change in the spread.
3. Compare the value from 6 months earlier with its rolling 60-month 75th percentile threshold.
4. Hold SPY when the lagged signal is above the threshold; otherwise hold cash.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe across stress episodes. Consistent "
        "positive bars would indicate durable timing; uneven bars mean the "
        "edge depends on the rates regime."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "strategy combinations, with the selected rule highlighted as the "
        "best search-phase result."
    )

    CAVEATS_MD = """
**Main caveats:**

1. Yield-curve warnings can be early by many months, so a correct macro signal can still be tactically painful.
2. Granger causality is weak in the generated test results, so this is not a proven causal forecast.
3. The level quartiles are not monotonic; the winning rule uses steepening momentum, not just the spread level.
4. The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged 3-month curve-change signal moves above its "
        "rolling 75th percentile threshold, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when the condition no longer holds."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged t10y3m_3m_chg above rolling p75; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED / project Data Master workbook | `T10Y3M`, 10-year Treasury yield minus 3-month Treasury yield | Daily, sampled monthly |
| Target | Local SPY monthly parquet derived from Yahoo Finance history | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the 10-year Treasury yield minus the 3-month "
    "Treasury yield, in percentage points. The pipeline constructs one-month, "
    "three-month, six-month, and twelve-month changes; a 60-month rolling "
    "z-score; an inversion flag; and a steepening flag. The winning signal is "
    "`t10y3m_3m_chg`, the 3-month change in the spread, used with a 6-month "
    "lead and a rolling 60-month 75th percentile threshold."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the curve move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do inverted, normal, and steep-curve regimes behave differently? | Makes the yield-curve story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past curve information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: yield-curve transforms x fixed and rolling thresholds x long/cash, signal-strength, and long/short strategies x procyclical/countercyclical orientations x lead times x lookbacks. The final tournament has 1,008 benchmark-excluded strategy combinations, of which 775 pass validity filters. The winning rule is `t10y3m_3m_chg / T2_roll_p75 / P1_long_cash / L6 / LB60`.
"""

_REFERENCES_MD = """
1. Federal Reserve Economic Data (FRED), `T10Y3M`, 10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity.
2. Yahoo Finance, SPY adjusted price history.
3. Estrella, A. and Mishkin, F. S. (1996). "The Yield Curve as a Predictor of U.S. Recessions."
4. Federal Reserve Bank of New York, Yield Curve as a Leading Indicator.
5. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
6. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Monthly sample from 1993-01-31 to 2025-11-30, with out-of-sample "
        "window 2017-10-31 to 2025-11-30. SPY history limits the usable "
        "sample even though T10Y3M begins earlier."
    ),
    plain_english=(
        "This page documents how the 10Y-3M spread was turned into testable "
        "signals, how the econometric checks were run, and how the tournament "
        "selected the final SPY allocation rule."
    ),
)
