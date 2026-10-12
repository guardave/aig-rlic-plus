"""Retail Inventories-to-Sales Ratio x SPY pair configuration (Rule APP-PT1).

MONTHLY demand-stress pair. The Retail Inventories-to-Sales Ratio (Census
RETAILIRSA, Data Master; dimensionless ratio, monthly) is a COINCIDENT,
production-side indicator. Its economic PRIOR is COUNTERCYCLICAL: a HIGH
inventories-to-sales ratio means stock is piling up faster than it sells --
inventory overhang / weakening demand -- which typically precedes production
cuts and equity weakness, so the prior says REDUCE equity when the ratio is
high. The traded signal is the ratio LEVEL used directly (it is an economically
bounded, mean-reverting series), with a rolling-median threshold; diff_1m,
chg_12m, and a 60-month z-score are the other tested transforms.

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge, and its confidence is LOW. Every number below is sourced from
results/retail_inv_sales_spy/*:
  - The tournament winner (`level` / T_roll_p50 rolling-median / P1_long_cash /
    PROCYCLICAL / ratio from three months earlier; OOS Sharpe 1.23 vs 0.91 B&H) is the grid maximum
    over 168 valid combinations (all 168 valid). The MEDIAN valid combo scores
    0.701 -- it UNDERPERFORMS buy-and-hold (0.91) (winner_summary.json).
  - DIRECTION CONTRADICTS THE PRIOR. The economic prior is countercyclical
    (reduce equity when the ratio is high), yet the search selected a
    PROCYCLICAL rule: hold SPY when the ratio from three months earlier is AT OR ABOVE its
    five-year rolling median (i.e. long when the ratio is HIGH). That is the
    OPPOSITE of the hypothesis. `interpretation_metadata.json` records
    expected_direction = countercyclical, observed_direction = procyclical,
    direction_consistent = false, confidence = low. A plausible post-hoc read
    is that the ratio spikes during recessions (sales collapse faster than
    inventories) and "long when the ratio is high, lagged 3 months" is catching
    post-stress recovery rebounds -- but that is a rationalization of a
    search-selected result, NOT a validated mechanism. Treat it as a red flag.
  - The concurrent evidence is a WEAK, NON-MONOTONIC tilt, not a clean
    countercyclical gradient: sorting months by the 12-month CHANGE in the ratio,
    the extreme rising-ratio quartile Q4 (demand weakening) is the WEAKEST
    concurrent SPY Sharpe (0.49), but the pattern does not rise monotonically as
    the ratio falls -- Q2 is highest (1.10), with Q1 0.82 and Q3 0.59
    (regime_quartile_returns.csv). So the concurrent data give only a soft hint
    that a rising ratio coincides with weaker equities, not the clean
    countercyclical gradient the prior would predict. (This 12-month-change
    evidence was recomputed after a diff-window bug fix: the signal had been
    mistakenly built as a 4-month change and is now a true 12-month change.)
  - No lead-lag forecast. The 12-month change in the ratio does NOT Granger-
    cause SPY at any tested lag (minimum p = 0.439 at lag 4) (granger_by_lag.csv).
    Linear correlation with forward SPY is near zero at every horizon; the only
    nominally significant cell is the 60-month z-score vs 6-month-forward SPY
    (r = 0.11, p = 0.03), a weak positive (core_models_20260912/correlations.csv).
    Local projections are near-null at every horizon (no coefficient significant;
    trivial R^2), with coefficients close to zero and mixed in sign
    (local_projections.csv).
  - SECONDARY OBSERVATIONS on the Sharpe-selected rule: OOS max drawdown
    -8.8% vs -23.9% for buy-and-hold, at a slightly LOWER annual return
    (12.1% vs 14.4%) and lower volatility (9.7%). The rule was selected for
    maximum search-period OOS Sharpe, not minimum drawdown; both benefits need
    a fresh frozen-rule holdout before independent validation. In-sample the rule sat
    defensive through the GFC, COVID and 2022 stress windows
    (subperiod_sharpe.csv). Turnover is moderate (1.96/yr, 16 OOS trades).
    A stationary block bootstrap puts the winner's Sharpe at p < 0.01
    (tournament_validation_20260912/bootstrap.csv), but that is an in-sample
    significance check, not out-of-sample validation.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - Stationarity nuance: the ratio is economically bounded and mean-reverting,
    but on this 1993-2025 sample ADF does NOT reject a unit root (p = 0.37) and
    KPSS rejects stationarity -- the level drifts slowly across decades. That is
    precisely why the winner pairs the level with a 60-month ROLLING-median
    threshold that re-centers on recent history, not a fixed cut
    (stationarity_tests_20260912.csv).

MONTHLY conventions: strategy timing offsets are in months; Sharpe annualized by
sqrt(12); OOS window 2017-06-30 -> 2025-07-31 (98 months). Numbers sourced from
results/retail_inv_sales_spy/ (winner_summary.json, kpis.json,
evidence_status.json, interpretation_metadata.json, core_models_20260912/*,
regime_quartile_returns.csv, subperiod_sharpe.csv, granger_by_lag.csv,
stationarity_tests_20260912.csv, structural_break_retail_inv_sales_spy.json,
tournament_results_20260912.csv, tournament_validation_20260912/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Retail Inventories-to-Sales as a Candidate SPY Overlay"
    PAGE_SUBTITLE = (
        "Retail Inventories-to-Sales Ratio (Data Master / Census RETAILIRSA) x "
        "S&P 500 (SPY), a monthly demand-stress signal tested against SPY "
        "returns."
    )

    HEADLINE_H2 = (
        "## Selected for maximum search-period OOS Sharpe (1.23); lower "
        "drawdown (-8.8% vs -23.9%) is a secondary observation -- neither "
        "benefit is independently validated"
    )

    PLAIN_ENGLISH = (
        "The retail inventories-to-sales ratio is the dollar value of stock on "
        "retailers' shelves divided by their monthly sales -- roughly, how many "
        "months of inventory they are holding. It is a COINCIDENT indicator: a "
        "HIGH or rising ratio means goods are piling up faster than they sell "
        "(inventory overhang, weakening demand), and the economic prior is "
        "therefore countercyclical -- reduce equity exposure when the ratio is "
        "high. This pair tests whether the ratio can improve SPY timing. Read "
        "the result as a candidate demand-stress overlay, not as a "
        "forecast: the formal lead-lag tests find no predictive edge, and the "
        "rule the search selected runs the opposite way to the economic prior "
        "(buy when the ratio from three months earlier is high). The result is "
        "potentially affected by selection bias and not independently validated."
    )

    WHERE_THIS_FITS = (
        "This is a demand-stress overlay for broad U.S. equities. It belongs in "
        "the portal as a candidate defensive overlay: lower drawdown was "
        "observed in the searched sample, but needs fresh holdout validation. "
        "It is not a standalone forecast, and not evidence "
        "that the ratio leads the market. Readers wanting the economically "
        "sensible reading should note the concurrent evidence is only a weak, "
        "non-monotonic tilt (the extreme rising-ratio quartile is the weakest, "
        "but the gradient is not clean), and treat the procyclical winner, which "
        "uses the ratio from three months earlier, with skepticism."
    )

    ONE_SENTENCE_THESIS = (
        "The inventories-to-sales ratio shows only a WEAK, NON-MONOTONIC "
        "concurrent tilt with equities (the extreme rising-ratio quartile has "
        "the worst SPY Sharpe, 0.49, but the pattern is non-monotonic -- Q2 is "
        "highest at 1.10), while the tested Granger specification finds no "
        "statistically significant incremental predictive information at lags "
        "1-6 (min p = 0.439), and local "
        "projections are null -- so the search's best rule, a PROCYCLICAL filter "
        "using the ratio from three months earlier, is a drawdown-reduction candidate (-8.8% vs -23.9% "
        "max drawdown) whose direction contradicts the economic prior and "
        "whose result is potentially affected by selection bias and not "
        "independently validated."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-06-30 -> 2025-07-31). The winner was found "
        "as the best of 168 valid combinations, and the MEDIAN valid combo "
        "(0.701) UNDERPERFORMS buy-and-hold (0.91) -- the typical rule subtracts "
        "value. Selection maximized OOS Sharpe (1.23 vs 0.91); the lower "
        "max drawdown (-8.8% vs -23.9%) is a secondary observation at a "
        "slightly LOWER return (12.1% vs 14.4%) and lower volatility (9.7%) -- "
        "both benefits describe the same selected rule and sample, and neither "
        "has independent validation. A fresh frozen-rule holdout must test "
        "both. Sharpe ratios use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "Retail Inventories-to-Sales Ratio vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the inventories-to-sales ratio (left axis) is shown "
        "with SPY on the same time axis, NBER recessions shaded. The ratio is "
        "bounded and mean-reverting -- it spikes in recessions (sales collapse "
        "faster than inventories) and drifts lower in expansions. The traded "
        "signal is the ratio LEVEL compared with its own five-year rolling "
        "median. Watch the shaded recessions: the ratio jumps as demand falls."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Inventories-to-Sales Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted by the 12-month CHANGE in the ratio, "
        "from Q1 (ratio falling fastest -- demand improving) to Q4 (ratio rising "
        "fastest -- demand weakening), with concurrent SPY Sharpe in each. The "
        "extreme rising-ratio quartile Q4 is the WEAKEST (0.49), but the pattern "
        "is NON-MONOTONIC -- Q2 is highest (1.10), with Q1 0.82 and Q3 0.59 -- so "
        "this is a weak, non-monotonic tilt rather than a clean relationship. "
        "This descriptive sort tests whether the ratio is RISING over 12 months; "
        "the winning rule instead trades whether the ratio LEVEL is HIGH relative "
        "to its rolling median. They are different signals, so this chart is not "
        "a direct opposite-direction test of the winner. Descriptive and "
        "concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical inventories-to-sales filter that uses the ratio from three months earlier**, selected for the **highest search-period OOS Sharpe among 168 valid combinations**. It holds SPY when that earlier ratio was at or above its rolling five-year median -- that is, when the ratio was *high* -- and holds cash otherwise. On that search-period OOS window (2017-06 to 2025-07), it records Sharpe 1.23 versus 0.91 for buy-and-hold, maximum drawdown **-8.8% versus -23.9%**, and annualized return 12.1% versus 14.4%. Lower drawdown and volatility are secondary observations on the same selected rule and sample, not the selection criterion or independently validated benefits. Both the Sharpe and drawdown results need confirmation on a fresh holdout with the rule frozen in advance.

### The Demand-Stress Hypothesis

The retail inventories-to-sales ratio measures how much stock retailers hold relative to how fast it sells. Because a rising ratio means goods are accumulating faster than demand can clear them, it is read as a **coincident** demand-stress gauge. The economic prior is **countercyclical**: a high or rising ratio signals inventory overhang and weakening demand -- a reason to *reduce* equity exposure -- while a low or falling ratio signals healthy demand.

The concurrent evidence gives only a weak, non-monotonic hint in that direction: it sorts months by the **12-month change** in the ratio, so “rising” means the ratio increased over the prior year. The extreme rising-ratio quartile (demand weakening) has the weakest concurrent SPY Sharpe (0.49), but the pattern does not fall monotonically as the ratio rises -- Q2 is the highest (1.10), with Q1 0.82 and Q3 0.59. The tournament winner uses a different signal: the **ratio level** relative to its five-year rolling median, so “high” means above that moving benchmark even if the ratio is not currently rising. The quartile sort and winning rule therefore are not directly opposite tests of the same signal. The winner is still procyclical relative to the level-based economic prior because it buys SPY when the ratio from three months earlier is high, but the change-based quartile chart does not directly validate or contradict that rule. (This 12-month-change evidence was recomputed after a diff-window bug fix; the signal had been mistakenly built as a 4-month change.)

### Why This Is Not a Forecast

The tested Granger specification finds **no statistically significant incremental predictive information at lags 1-6** (minimum p = 0.439), forward-return correlations are near zero at every horizon, and local projections are essentially null (coefficients near zero and mixed in sign, none significant). Failure to reject the Granger-test null does not prove that no relationship exists; it means this specification and sample do not establish incremental predictability at those lags. Conversely, even a significant Granger result would describe predictive ordering rather than economic causation. The unexpected direction and weak statistical evidence justify skepticism about the procyclical 3-month rule, but do not establish what caused its result. That result is potentially affected by selection bias and not independently validated. A tempting post-hoc story -- that the ratio spikes in recessions and "buy when it is high" catches recovery rebounds -- is a rationalization of a search-selected result, not a validated mechanism. This dashboard therefore treats the pair as a searched demand-stress overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "The ratio rose as goods demand softened in the 2001 slowdown. "
                "The searched rule lost less than buy-and-hold in this window "
                "(-0.55 vs -0.70 subperiod Sharpe), but still fell -- an uneven, "
                "partial defense."
            ),
            "caption": "Dot-Com: the ratio rose as demand softened; the rule lost slightly less than SPY.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The ratio spiked violently through 2008-09 as sales collapsed "
                "faster than inventories. In-sample the rule was defensive here "
                "(subperiod Sharpe +0.30 vs -1.03 for SPY) -- part of its "
                "drawdown story."
            ),
            "caption": "GFC: the ratio spiked as sales collapsed; the rule was defensive vs SPY.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The ratio jumped in spring 2020 as retail sales cratered, then "
                "reversed sharply. This is an extreme, exogenous in-window "
                "outlier that can dominate the backtest fit -- read any rule "
                "that leans on it with caution."
            ),
            "caption": "COVID: extreme ratio spike and reversal, an outlier that can dominate the fit.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "The ratio stayed low through 2022 (lean inventories, resilient "
                "nominal sales) even as equities de-rated on rate hikes. The "
                "rule sat in cash (flat) through the drawdown while SPY fell -- "
                "the demand signal was quiet exactly when the market's problem "
                "was rates, not demand."
            ),
            "caption": "2022: the ratio stayed low while SPY sold off on rates; the rule sat in cash.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is at best a weak concurrent demand gauge and imperfect as a forecast. The ratio rose in the Dot-Com and GFC downturns and spiked in COVID as sales collapsed -- but the searched rule's protection was uneven: it lost slightly less than buy-and-hold in the Dot-Com bear, was clearly defensive in the GFC (+0.30 vs -1.03 subperiod Sharpe) and COVID (+1.55 vs -0.08), and sat in cash (flat) through the 2022 rate shock while SPY fell. In 2022 the ratio stayed low because the market's problem was rates, not demand. The stress episodes show where the selected rule's lower drawdown arose in the search sample; they do not independently validate drawdown protection, and the rule's direction still contradicts the economic prior.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this demand-stress story survives "
        "correlation, lead-lag, regime, and strategy checks. It largely does "
        "not survive as a forecast, and the winner's procyclical direction "
        "contradicts the countercyclical prior. Its lower drawdown is an "
        "observation from the search, not independent evidence of protection."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether the inventories-to-sales signal and "
        "future SPY returns move together in a roughly linear way."
    ),
    question="Does a higher or rising inventories-to-sales ratio line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values mean "
        "a higher ratio signal lines up with stronger future SPY returns; pale "
        "cells mean no association."
    ),
    chart_name="correlation_heatmap",
    observation=(
        "The linear association is essentially zero at every tradeable horizon. "
        "The level-vs-forward cells are near zero (|r| < 0.04), and the only "
        "nominally significant cell is the 60-month z-score versus 6-month-forward "
        "SPY (r = 0.11, p = 0.03), a weak positive rather than a usable forecast."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair. The more relevant "
        "question is whether a rule using an earlier ratio level improves portfolio behavior "
        "in the searched sample."
    ),
    key_message="The inventories-to-sales ratio is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does the inventories-to-sales ratio lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    observation=(
        "The tested specification finds no statistically significant incremental "
        "predictive information at lags 1-6: the signal->SPY p-value never falls "
        "below 0.439 (at lag 4), and all F-statistics are below one."
    ),
    interpretation=(
        "Failure to reject the null does not prove that no relationship exists; "
        "it means this specification and sample do not provide statistically "
        "significant evidence of incremental predictability at the tested lags. "
        "Granger predictability, if detected, would establish predictive ordering "
        "rather than an economic causal mechanism."
    ),
    key_message=(
        "The tested specification finds no statistically significant incremental "
        "predictive information at lags 1-6 (min p = 0.439); this is not proof of "
        "no relationship, and the test does not establish economic causation."
    ),
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts the 379 months with both a valid 12-month "
        "change in the inventories-to-sales ratio and a concurrent SPY return "
        "from January 1994 through July 2025. The cut points are the full-sample "
        "25th, 50th, and 75th percentiles of that change series."
    ),
    question="Do improving and deteriorating demand regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 covers changes from -0.58 through -0.04; Q2 is above -0.04 through "
        "0.00; Q3 is above 0.00 through 0.03; and Q4 is above 0.03 through 0.20, "
        "in ratio points. Q1 is the fastest-falling regime and Q4 the fastest-"
        "rising regime. Intervals are closed on the right, so a value exactly "
        "on an internal boundary goes into the lower bucket."
    ),
    chart_name="regime_stats",
    observation=(
        "Concurrent SPY Sharpe is highest in Q2 (1.10) and lowest in the extreme "
        "rising-ratio quartile (Q4 0.49), with Q1 0.82 and Q3 0.59 -- a "
        "non-monotonic pattern in which only the extreme rising-ratio bucket "
        "clearly underperforms. Counts are Q1 101, Q2 117, Q3 73, and Q4 88. "
        "They are unequal because the two-decimal source series creates ties at "
        "the cut points: 16 observations equal -0.04, 33 equal 0.00, and 14 equal "
        "0.03, and each tied group stays in the lower interval. All 379 eligible "
        "months are assigned exactly once; none are missing or misassigned. "
        "This descriptive chart sorts the 12-month CHANGE "
        "(rising versus falling); the winner trades the LEVEL relative to its "
        "rolling median (high versus low), so this is not a direct opposite-"
        "direction test of the winning signal."
    ),
    deep_dive_title="Quartile construction and count reconciliation",
    deep_dive_content=(
        "The underlying level sample has 391 monthly observations from January "
        "1993 through July 2025. Computing `level[t] - level[t-12]` consumes the "
        "first 12 months, leaving 379 construction observations from January "
        "1994 through July 2025; every one also has a concurrent SPY return. "
        "`pandas.qcut(..., 4)` produces boundaries `[-0.58, -0.04, 0.00, 0.03, "
        "0.20]`. Its right-closed interval rule assigns boundary ties to the "
        "lower bucket, producing counts `101 + 117 + 73 + 88 = 379`. The count "
        "difference is therefore a consequence of preserving ties, not missing "
        "or misassigned observations."
    ),
    interpretation=(
        "The concurrent pattern is a weak, non-monotonic tilt in the 12-month "
        "CHANGE, so it only softly favours the demand-stress reading. The "
        "winner instead uses the ratio LEVEL relative to its rolling median; "
        "this descriptive sort therefore does not directly test the winner's "
        "high-versus-low signal. The winner remains contrary to the level-based "
        "economic prior, and its result is potentially affected by selection "
        "bias and not independently validated."
    ),
    key_message="Only the extreme rising-ratio quartile clearly underperforms (0.49), and the pattern is non-monotonic (Q2 highest, 1.10). This 12-month-change sort is descriptive and does not directly test the winner's high-versus-low level signal.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the inventories-to-sales signal."
    ),
    question="How does SPY respond after the inventories-to-sales ratio changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "inventories-to-sales signal. Coefficients near zero mean no detectable "
        "effect."
    ),
    chart_name="local_projections",
    observation=(
        "Point estimates are close to zero at every horizon (about -0.01 at 1 "
        "and 3 months, +0.03 at 6 months), with mixed signs, p-values from 0.71 "
        "to 0.87, and negligible explained variance. No coefficient is "
        "statistically significant or usable as a signal."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. The "
        "near-zero, mixed-sign coefficients do not rescue a forward-looking "
        "reading of the indicator."
    ),
    key_message="Local projections are null; the ratio carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the inventories-to-sales signal "
        "matters differently in weak, normal, and strong SPY return "
        "environments."
    ),
    question="Does the inventories-to-sales ratio behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    observation=(
        "The estimated coefficient is small, negative, and essentially flat "
        "across the tested quantiles (about -0.01, p = 0.87). There is no "
        "material tail sensitivity, consistent with the near-null correlation "
        "and local-projection results."
    ),
    interpretation=(
        "The ratio does not flag elevated crash risk or exceptional upside -- "
        "there is no tail channel to trade."
    ),
    key_message="The inventories-to-sales ratio shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Inventories-to-Sales Is Weak Concurrent Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a cautious demand-stress overlay -- and nothing "
        "stronger. The strategy winner improves search-phase OOS Sharpe, but "
        "the tested Granger specification finds no significant incremental "
        "predictive information at lags 1-6 (min p = 0.439), while local "
        "projections are null, and the winner's PROCYCLICAL rule using the ratio "
        "from three months earlier contradicts the countercyclical demand-stress prior."
    ),
    "plain_english": (
        "This page asks whether the inventories-to-sales ratio helps time SPY. "
        "The answer is: not as a forecast. Concurrent quartiles show only a "
        "weak, non-monotonic tilt (the extreme rising-ratio bucket is the "
        "weakest, but the gradient is not clean), the tested Granger specification "
        "finds no significant incremental predictive information at lags 1-6, "
        "and the best rule runs the opposite way (buy when the "
        "ratio from three months earlier is high relative to its rolling median). "
        "Because the quartiles sort the 12-month change while the winner trades "
        "the level, they are not directly opposite tests. The Sharpe-selected rule's lower "
        "drawdown is a secondary observation on the same search sample; both benefits "
        "still require fresh holdout validation."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 168 strategy combinations (all 168 valid) across "
        "four inventories-to-sales transforms (level, 1-month change, 12-month "
        "change, 60-month z-score), fixed and rolling thresholds, a long/cash "
        "strategy, and leads from 0 to 12 months. The selected winner is "
        "`level / T_roll_p50 / P1_long_cash`, using the ratio from three months "
        "earlier and selected for maximum search-period OOS Sharpe (1.23), not minimum drawdown. The "
        "MEDIAN valid combo scores 0.701 -- below buy-and-hold's 0.91 -- and the "
        "runner-up (`level / T_roll_p50 / L1`, 1.19) shares the same signal and "
        "rolling-median threshold at a shorter lead, so the search surface "
        "concentrates on short-lead level rules, not a robust economic edge."
    ),
    "transition": (
        "**Transition:** the evidence is weak concurrent context, not causation, "
        "and the winner runs against the prior. The Strategy page shows the "
        "exact long/cash rule and its lower observed drawdown on the search "
        "sample; neither that benefit nor its selected Sharpe has independent "
        "validation."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical Inventories-to-Sales Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the inventories-to-sales ratio "
        "level, a rolling-median threshold, a procyclical orientation, and a "
        "the ratio from three months earlier -- selected for maximum search-period Sharpe, with lower "
        "drawdown as a secondary observation; both remain unvalidated."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the inventories-to-sales ratio from three "
        "months earlier was at or above its five-year rolling median (i.e. when "
        "the ratio was *high*); otherwise it holds cash. This is a "
        "PROCYCLICAL filter -- the opposite of the countercyclical prior, which "
        "says reduce equity when the ratio is high -- not a validated recession "
        "forecast. It was selected for maximum search-period Sharpe; its "
        "shallower drawdown (-8.8% vs -23.9%) and lower volatility are "
        "secondary observations on the same sample, not independent validation."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/retail_inv_sales_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/retail_inv_sales_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/retail_inv_sales_spy/tournament_results_20260912.csv"},
        {"label": "Stationarity tests", "path": "results/retail_inv_sales_spy/stationarity_tests_20260912.csv"},
    ]

    WINNER_HEADING = (
        "Tournament Winner: Ratio Level vs Rolling Five-Year Median / "
        "P1 Long/Cash / L3 (uses the ratio from three months earlier)"
    )
    TIMING_SUMMARY = "uses the ratio from three months earlier"

    SIGNAL_RULE_MD = """
**Rule in plain English:** the rule uses the ratio from three months earlier. Hold SPY when that ratio was at or above its rolling five-year median (i.e. when the ratio was *high* a quarter earlier); otherwise hold cash. This is a procyclical rule and runs against the countercyclical prior, which says reduce equity when the ratio is high.

If-then form:
- **IF** `invsales_level` from 3 months earlier is at or above its 60-month rolling median -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-06-30 to 2025-07-31, 98 months): Sharpe 1.23 versus 0.91 buy-and-hold; annualized return 12.1% versus 14.4%; **maximum drawdown -8.8% versus -23.9%**; annualized volatility 9.7%; win rate 42.9%; 16 trades; annual turnover 1.96 (moderate). Selection maximized Sharpe; lower drawdown and volatility are secondary observations on that selected rule and sample. Both the Sharpe and drawdown benefits need a fresh frozen-rule holdout test.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Retail Inventories-to-Sales Ratio (`RETAILIRSA`, Census / Data Master) at month-end. Second, it takes the ratio level directly (`invsales_level`). Third, at each monthly decision date it uses the ratio from three months earlier. Finally, that earlier level is compared with its rolling five-year median: when it is at or above the median, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return (low here partly because the rule sits in cash for stretches).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the Retail Inventories-to-Sales Ratio (RETAILIRSA) at month end.
2. Take the ratio level directly.
3. At each monthly decision date, take the value from 3 months earlier and compare it with the 60-month rolling median applicable on that date.
4. Set the target allocation to 100% SPY when that earlier level is at or above the rolling median; otherwise set it to 100% cash.
5. Recompute this binary target monthly. There is no hover zone, hysteresis, or partial position, and the prior allocation does not change the threshold comparison. Turnover is moderate (1.96/yr).
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod "
        "chart compares the searched rule with buy-and-hold SPY during major "
        "stress windows. In-sample the rule is defensive in the GFC "
        "(+0.30 vs -1.03), COVID (+1.55 vs -0.08), and the 2022 rate shock "
        "(0.0 in cash vs -0.76), and loses slightly less in the Dot-Com bear "
        "(-0.55 vs -0.70). These episodes show where the selected rule's lower "
        "drawdown arose, but do not independently validate protection; the "
        "direction still contradicts the prior."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the inventories-to-sales 12-month "
            "change; the target is SPY returns. The rolling correlation tests "
            "whether their linear relationship is stable through time. Large "
            "swings mean the relationship is unstable and the rule needs ongoing "
            "monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "inventories-to-sales/SPY relationship changes enough that one fixed "
            "model is unlikely to describe the whole sample. A larger break "
            "statistic means the relationship shifted more materially across "
            "periods (here the max absolute rolling-correlation z-score reaches "
            "2.6)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.23) is a right-tail maximum; the "
        "median valid combo (0.701) sits BELOW buy-and-hold (0.91), so the "
        "typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The winner is PROCYCLICAL and uses the ratio from three months earlier -- the opposite of the level-based countercyclical prior, which says reduce equity when the ratio level is high relative to its rolling median. The concurrent quartiles use a different signal: they sort the ratio's 12-month change, where the extreme rising-ratio bucket is weakest but the pattern is non-monotonic. That descriptive change-based result is not a direct opposite-direction test of the winner's high-versus-low level rule. The unexpected winner still warrants skepticism, but the evidence does not establish the cause of its result: it is potentially affected by selection bias and not independently validated.
2. The tested Granger specification finds no statistically significant incremental predictive information at lags 1-6 (min p = 0.439), while local projections are null. Failure to reject the Granger null does not prove no relationship exists, and Granger predictability would not establish economic causation even if it were detected.
3. The result is marked `found_in_search`; the median valid combo underperforms buy-and-hold, and both the selected Sharpe and observed drawdown benefits still need fresh frozen-rule holdout confirmation. The bootstrap p < 0.01 is an in-sample significance check, not out-of-sample validation.
4. The rule was selected for maximum search-period OOS Sharpe, not drawdown reduction. Lower drawdown and volatility are secondary observations on the same selected rule and sample, not independent validation; annualized return (12.1%) is slightly BELOW buy-and-hold (14.4%).
5. A tempting post-hoc rationale -- that the ratio spikes in recessions and "buy when high" catches recovery rebounds -- is a story fitted to a search-selected result, not a validated mechanism.
6. COVID 2020 is an extreme in-window outlier (the ratio spiked and reversed) that can dominate the fit. The ratio's level also drifts across decades, which is why a rolling-median threshold is used.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the ratio from three months earlier was at or above its rolling "
        "five-year median, taking exposure from 0% to 100% SPY. A SELL moves back "
        "to cash when that earlier level was below the rolling median."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1995-03-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: level procyclical rule crossed T_roll_p50; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master (Census) | `RETAILIRSA`, Retail Inventories-to-Sales Ratio (dimensionless, SA) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the Retail Inventories-to-Sales Ratio -- retail "
    "inventories divided by retail sales -- a dimensionless, seasonally "
    "adjusted monthly ratio. It is economically bounded and mean-reverting, but "
    "on this 1993-2025 sample the level is not formally stationary (ADF fails to "
    "reject a unit root, p = 0.37; KPSS rejects stationarity), reflecting slow "
    "drift across decades. The pipeline also constructs stationary transforms -- "
    "the 1-month change, the 12-month change, and a 60-month rolling z-score. "
    "The winning signal is `invsales_level`, using the ratio from three months "
    "earlier with a rolling five-year median threshold (which re-centers on "
    "recent history and absorbs the level's drift), and a procyclical "
    "orientation (long SPY when the ratio from three months earlier is at or above the median)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the inventories-to-sales signal move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do improving and deteriorating demand regimes behave differently? | Makes the countercyclical story interpretable |
| Granger causality | Does past inventories-to-sales information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: inventories-to-sales transforms (level, 1-month change, 12-month change, 60-month z-score) x fixed and rolling thresholds x long/cash strategy x timing offsets (0-12 months). The final tournament has 168 combinations, all 168 valid. The winning rule is `invsales_level / T_roll_p50 / P1_long_cash procyclical`, using the ratio from three months earlier, and was selected for maximum search-period OOS Sharpe (1.23), not minimum drawdown. Its lower drawdown is a secondary observation on the same selected rule and sample. The median valid combo (0.701) underperforms buy-and-hold (0.91), and the runner-up uses the same signal and rolling-median threshold with the ratio from one month earlier (Sharpe 1.19) -- read the winner as a selection maximum in a cluster of rules using earlier ratio observations, not a validated edge. That direction (long when the ratio is high) contradicts the countercyclical prior, which warrants skepticism but does not establish the cause of the result. The result is potentially affected by selection bias and not independently validated.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau, Manufacturing and Trade Inventories and Sales, retail inventories-to-sales ratio (`RETAILIRSA`).
2. Federal Reserve Economic Data (FRED), `RETAILIRSA`, Retailers: Inventories to Sales Ratio.
3. Yahoo Finance, SPY adjusted price history.
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
        "Monthly sample from 1993-01-31 to 2025-07-31, with out-of-sample "
        "window 2017-06-30 to 2025-07-31 (98 months). SPY history and the "
        "rolling-window transforms limit the usable sample."
    ),
    plain_english=(
        "This page documents how the Retail Inventories-to-Sales Ratio was used "
        "as a stationary-transform and level signal, how the econometric checks "
        "were run, and how the tournament selected the final SPY allocation rule "
        "-- along with the honest caveat that the selection maximum is a "
        "procyclical rule (long when the ratio is high) that contradicts the "
        "countercyclical prior and is not yet a validated edge."
    ),
)
