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
    PROCYCLICAL / L3 months; OOS Sharpe 1.23 vs 0.91 B&H) is the grid maximum
    over 168 valid combinations (all 168 valid). The MEDIAN valid combo scores
    0.701 -- it UNDERPERFORMS buy-and-hold (0.91) (winner_summary.json).
  - DIRECTION CONTRADICTS THE PRIOR. The economic prior is countercyclical
    (reduce equity when the ratio is high), yet the search selected a
    PROCYCLICAL rule: hold SPY when the 3-month-lagged ratio is AT OR ABOVE its
    five-year rolling median (i.e. long when the ratio is HIGH). That is the
    OPPOSITE of the hypothesis. `interpretation_metadata.json` records
    expected_direction = countercyclical, observed_direction = procyclical,
    direction_consistent = false, confidence = low. A plausible post-hoc read
    is that the ratio spikes during recessions (sales collapse faster than
    inventories) and "long when the ratio is high, lagged 3 months" is catching
    post-stress recovery rebounds -- but that is a rationalization of a
    search-selected result, NOT a validated mechanism. Treat it as a red flag.
  - The concurrent evidence points the ORDINARY countercyclical way, opposite
    the winner: sorting months by the 12-month CHANGE in the ratio, the
    falling-ratio quartile Q1 (demand improving) has the BEST concurrent SPY
    Sharpe (1.37) and the rising-ratio quartile Q4 (demand weakening) the WORST
    (0.15) (regime_quartile_returns.csv). Rising/high ratio coincides with weak
    equities -- exactly the prior -- so the procyclical winner runs against both
    the prior and the concurrent data.
  - No lead-lag forecast. The 12-month change in the ratio does NOT Granger-
    cause SPY at any tested lag (minimum p = 0.32 at lag 1) (granger_by_lag.csv).
    Linear correlation with forward SPY is near zero at every horizon; the only
    nominally significant cell is the 60-month z-score vs 6-month-forward SPY
    (r = 0.11, p = 0.03), a weak positive (core_models_20260831/correlations.csv).
    Local projections are near-null at every horizon (no coefficient significant;
    trivial R^2), with a weak NEGATIVE tilt consistent with the prior but
    insignificant (local_projections.csv). Pre-whitened cross-correlation is
    significant only at ZERO and NEGATIVE lags (SPY tends to move before the
    ratio), with no significant lead-side bars (ccf_prewhitened.csv).
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: OOS max drawdown
    -8.8% vs -23.9% for buy-and-hold, at a slightly LOWER annual return
    (12.1% vs 14.4%) and lower volatility (9.7%) -- read the Sharpe as
    volatility avoidance, not a return advantage. In-sample the rule sat
    defensive through the GFC, COVID and 2022 stress windows
    (subperiod_sharpe.csv). Turnover is moderate (1.96/yr, 16 OOS trades).
    A stationary block bootstrap puts the winner's Sharpe at p < 0.01
    (tournament_validation_20260831/bootstrap.csv), but that is an in-sample
    significance check, not out-of-sample validation.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - Stationarity nuance: the ratio is economically bounded and mean-reverting,
    but on this 1993-2025 sample ADF does NOT reject a unit root (p = 0.37) and
    KPSS rejects stationarity -- the level drifts slowly across decades. That is
    precisely why the winner pairs the level with a 60-month ROLLING-median
    threshold that re-centers on recent history, not a fixed cut
    (stationarity_tests_20260831.csv).

MONTHLY conventions: leads in MONTHS (winner L3); Sharpe annualized by
sqrt(12); OOS window 2017-06-30 -> 2025-07-31 (98 months). Numbers sourced from
results/retail_inv_sales_spy/ (winner_summary.json, kpis.json,
evidence_status.json, interpretation_metadata.json, core_models_20260831/*,
regime_quartile_returns.csv, subperiod_sharpe.csv, granger_by_lag.csv,
stationarity_tests_20260831.csv, structural_break_retail_inv_sales_spy.json,
tournament_results_20260831.csv, tournament_validation_20260831/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Retail Inventories-to-Sales as a Defensive SPY Overlay"
    PAGE_SUBTITLE = (
        "Retail Inventories-to-Sales Ratio (Data Master / Census RETAILIRSA) x "
        "S&P 500 (SPY), a monthly demand-stress signal tested against SPY "
        "returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.23 OOS, but the honest headline is the drawdown "
        "(-8.8% vs -23.9%) -- and the winning rule is PROCYCLICAL (buy when the "
        "ratio is HIGH), the OPPOSITE of the countercyclical economic prior"
    )

    PLAIN_ENGLISH = (
        "The retail inventories-to-sales ratio is the dollar value of stock on "
        "retailers' shelves divided by their monthly sales -- roughly, how many "
        "months of inventory they are holding. It is a COINCIDENT indicator: a "
        "HIGH or rising ratio means goods are piling up faster than they sell "
        "(inventory overhang, weakening demand), and the economic prior is "
        "therefore countercyclical -- reduce equity exposure when the ratio is "
        "high. This pair tests whether the ratio can improve SPY timing. Read "
        "the result as demand-stress context and drawdown control, not as a "
        "forecast: the formal lead-lag tests find no predictive edge, and the "
        "rule the search selected runs the WRONG way (buy when the ratio is "
        "high) at a 3-month lag -- most likely a search artifact, not a "
        "validated signal."
    )

    WHERE_THIS_FITS = (
        "This is a demand-stress overlay for broad U.S. equities. It belongs in "
        "the portal as a defensive context signal: useful for drawdown control "
        "in the searched sample, but not a standalone forecast, and not evidence "
        "that the ratio leads the market. Readers wanting the economically "
        "sensible reading should treat the concurrent, countercyclical pattern "
        "(rising/high ratio = worse equity conditions) as the sound one, and the "
        "procyclical 3-month winner with skepticism."
    )

    ONE_SENTENCE_THESIS = (
        "The inventories-to-sales ratio is countercyclical with equities "
        "CONCURRENTLY (the falling-ratio quartile has the best SPY Sharpe, 1.37, "
        "and the rising-ratio quartile the worst, 0.15) but does NOT lead SPY -- "
        "Granger is insignificant at every lag (min p = 0.32) and local "
        "projections are null -- so the search's best rule, a PROCYCLICAL filter "
        "at a 3-month lead, is a drawdown-reduction candidate (-8.8% vs -23.9% "
        "max drawdown) whose direction contradicts the economic prior and is "
        "most likely a search artifact."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-06-30 -> 2025-07-31). The winner was found "
        "as the best of 168 valid combinations, and the MEDIAN valid combo "
        "(0.701) UNDERPERFORMS buy-and-hold (0.91) -- the typical rule subtracts "
        "value. The defensible number is the max drawdown (-8.8% vs -23.9%) at a "
        "slightly LOWER return (12.1% vs 14.4%) and lower volatility (9.7%) -- "
        "read the Sharpe (1.23 vs 0.91) as volatility avoidance, not "
        "stock-picking skill. Sharpe ratios use monthly sqrt(12) annualization."
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
        "falling-ratio quartile Q1 has the BEST concurrent SPY Sharpe (1.37) and "
        "the rising-ratio quartile Q4 the WORST (0.15) -- broadly "
        "COUNTERCYCLICAL concurrently (a deteriorating ratio coincides with "
        "weaker equities). This is the economically sensible reading, and it "
        "runs OPPOSITE to the procyclical rule the tournament selected. "
        "Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical, 3-month-lagged inventories-to-sales filter**. It holds SPY when the ratio from three months earlier was at or above its five-year rolling median -- that is, when the ratio was *high* -- and holds cash otherwise. Out-of-sample (2017-06 to 2025-07), this rule earns a Sharpe of 1.23 versus 0.91 for buy-and-hold, with a maximum drawdown of **-8.8% versus -23.9%** at an annualized return of 12.1% versus 14.4%. Read that as the honest headline: the rule's edge is a much shallower worst-case loss and lower volatility, **not** a return advantage.

### The Demand-Stress Hypothesis

The retail inventories-to-sales ratio measures how much stock retailers hold relative to how fast it sells. Because a rising ratio means goods are accumulating faster than demand can clear them, it is read as a **coincident** demand-stress gauge. The economic prior is **countercyclical**: a high or rising ratio signals inventory overhang and weakening demand -- a reason to *reduce* equity exposure -- while a low or falling ratio signals healthy demand.

The concurrent evidence supports that prior: sort months by the 12-month change in the ratio and the falling-ratio quartile (demand improving) has the best concurrent SPY Sharpe (1.37), the rising-ratio quartile (demand weakening) the worst (0.15). But the tournament's winning rule runs the **opposite** way -- it buys SPY when the 3-month-lagged ratio is *high*. That direction contradicts the economic prior and the concurrent data.

### Why This Is Not a Forecast

The formal lead-lag tests are blunt. The 12-month change in the ratio does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.32), forward-return correlations are near zero at every horizon, and local projections are essentially null (a weak negative tilt, consistent with the prior, but insignificant). The pre-whitened cross-correlation is significant only at *zero and negative* lags -- SPY tends to move *before* the ratio -- the reverse of a forecasting signal. So the procyclical 3-month rule the search selected is economically implausible; it most plausibly reflects a search artifact rather than a real channel. A tempting post-hoc story -- that the ratio spikes in recessions and "buy when it is high" catches recovery rebounds -- is a rationalization of a search-selected result, not a validated mechanism. This dashboard therefore treats the pair as a searched demand-stress overlay whose value, if any, is defensive.
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

The stress charts show why the signal is countercyclical concurrently but imperfect as a forecast. The ratio rose in the Dot-Com and GFC downturns and spiked in COVID as sales collapsed -- but the searched rule's protection was uneven: it lost slightly less than buy-and-hold in the Dot-Com bear, was clearly defensive in the GFC (+0.30 vs -1.03 subperiod Sharpe) and COVID (+1.55 vs -0.08), and sat in cash (flat) through the 2022 rate shock while SPY fell. In 2022 the ratio stayed low because the market's problem was rates, not demand. The strongest honest reading is not "the ratio predicts drawdowns"; it is that a lagged, procyclical filter happened to step to cash during several stress windows, which is where its drawdown advantage was earned -- and that its direction still contradicts the economic prior.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this demand-stress story survives "
        "correlation, lead-lag, regime, and strategy checks. It largely does "
        "not survive as a forecast -- the value is defensive, not predictive, "
        "and the winner's procyclical direction contradicts the countercyclical "
        "prior."
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
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon. The only nominally significant cell is the 60-month "
        "z-score vs the 6-month-forward SPY return (r = 0.11, p = 0.03), a weak "
        "positive -- not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; the "
        "level-vs-forward cells are near zero (|r| < 0.04), and the largest cell "
        "anywhere is the 60-month z-score vs 6-month-forward SPY at r = 0.11."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair. The more relevant "
        "question is whether a lagged level filter improves portfolio behavior "
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
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-6 is 0.32 -- the ratio does not Granger-cause SPY "
        "returns."
    ),
    observation=(
        "Across all six monthly lags the signal->SPY p-value never falls below "
        "0.32; the F-statistics are near one. There is no formal evidence of "
        "lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal claim. The strategy must be framed as a "
        "searched demand-stress overlay, not proof that the ratio causes future "
        "SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.32); the ratio does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the 12-month change in the "
        "inventories-to-sales ratio and compares concurrent SPY returns across "
        "demand regimes."
    ),
    question="Do improving and deteriorating demand regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the falling-ratio regime (demand improving); Q4 is the "
        "rising-ratio regime (demand weakening). Compare Sharpe, average return, "
        "and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: broadly COUNTERCYCLICAL -- the falling-ratio quartile "
        "Q1 has the BEST concurrent SPY Sharpe (1.37) and the rising-ratio "
        "quartile Q4 the WORST (0.15). A deteriorating ratio coincides with "
        "weaker equities. This runs opposite to the procyclical winner."
    ),
    observation=(
        "Concurrent SPY Sharpe is highest in the falling-ratio quartile (Q1 "
        "1.37) and lowest in the rising-ratio quartile (Q4 0.15), with the "
        "middle quartiles non-monotonic (Q2 0.56, Q3 1.03) -- a rising ratio "
        "generally coincides with worse equity conditions."
    ),
    interpretation=(
        "The concurrent pattern fits a countercyclical demand-stress story. "
        "That makes the tournament's PROCYCLICAL winner economically "
        "counter-intuitive and reinforces reading it as a search artifact, not "
        "a real relationship."
    ),
    key_message="A deteriorating ratio coincides with worse SPY conditions -- countercyclical, opposite the winner's direction.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does the inventories-to-sales ratio line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean the "
        "ratio leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the significant bars sit at ZERO and NEGATIVE lags -- "
        "SPY tends to move BEFORE the ratio -- with no significant lead-side "
        "(ratio-leads-SPY) bars. That is the reverse of a forecasting signal."
    ),
    observation=(
        "Correlations are significant only at lag 0 and negative lags (SPY "
        "leading the ratio, ccf down to -0.24 at lag -1); every positive "
        "lead-side offset is inside the confidence band and insignificant."
    ),
    interpretation=(
        "There is no coherent window in which the ratio foreshadows SPY. If "
        "anything the causality runs the other way (markets moving before the "
        "ratio), which argues against a ratio-based forecast of SPY."
    ),
    key_message="Significant correlation is at lag 0 and on the SPY-leads side; the ratio shows no forecasting lead over SPY.",
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
    chart_caption=(
        "What this shows: coefficients are essentially zero across all horizons "
        "(1, 3, 6 months), none statistically significant (p from 0.13 to 0.32), "
        "with negligible R^2. The sign is weakly negative -- consistent with the "
        "countercyclical prior, but not significant."
    ),
    observation=(
        "Point estimates are small and negative at every horizon (-0.04 to "
        "-0.17) and no coefficient is significant; the explained variance is "
        "trivial throughout."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. The "
        "weak negative tilt aligns with the prior but does not rescue a "
        "forward-looking reading of the indicator."
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
    chart_caption=(
        "What this shows: the coefficient is small, negative, and flat across "
        "quantiles (about -0.08, p = 0.29) -- no material tail sensitivity for "
        "the inventories-to-sales signal."
    ),
    observation=(
        "The estimated coefficient is small and essentially unchanged across the "
        "tested quantiles, consistent with the near-null correlation and "
        "local-projection results."
    ),
    interpretation=(
        "The ratio does not flag elevated crash risk or exceptional upside -- "
        "there is no tail channel to trade."
    ),
    key_message="The inventories-to-sales ratio shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Inventories-to-Sales Is Countercyclical Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a cautious demand-stress overlay -- and nothing "
        "stronger. The strategy winner improves search-phase OOS Sharpe, but "
        "formal lead-lag evidence is absent (Granger min p = 0.32; local "
        "projections null; CCF significant only at lag 0 and on the SPY-leads "
        "side), and the winner's PROCYCLICAL direction at a 3-month lead "
        "contradicts the countercyclical, demand-stress prior."
    ),
    "plain_english": (
        "This page asks whether the inventories-to-sales ratio helps time SPY. "
        "The answer is: not as a forecast. Concurrent quartiles are "
        "countercyclical (rising ratio = worse market), but the causal tests "
        "find no lead, and the best rule runs the opposite way (buy when the "
        "ratio is high) at a 3-month lag. Treat it as a defensive, after-the-"
        "fact overlay, not an early-warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 168 strategy combinations (all 168 valid) across "
        "four inventories-to-sales transforms (level, 1-month change, 12-month "
        "change, 60-month z-score), fixed and rolling thresholds, a long/cash "
        "strategy, and leads from 0 to 12 months. The selected winner is "
        "`level / T_roll_p50 / P1_long_cash / L3`, with OOS Sharpe 1.23. The "
        "MEDIAN valid combo scores 0.701 -- below buy-and-hold's 0.91 -- and the "
        "runner-up (`level / T_roll_p50 / L1`, 1.19) shares the same signal and "
        "rolling-median threshold at a shorter lead, so the search surface "
        "concentrates on short-lead level rules, not a robust economic edge."
    ),
    "transition": (
        "**Transition:** the evidence is countercyclical context, not causation, "
        "and the winner runs against the prior. The Strategy page shows the "
        "exact long/cash rule, the drawdown advantage that is its real virtue, "
        "and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical, Lagged Inventories-to-Sales Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the inventories-to-sales ratio "
        "level, a rolling-median threshold, a procyclical orientation, and a "
        "3-month lead -- valued for drawdown reduction, not for its Sharpe, and "
        "flagged as running against the economic prior."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the inventories-to-sales ratio from three "
        "months earlier was at or above its five-year rolling median (i.e. when "
        "the ratio was *high*); otherwise it holds cash. This is a lagged, "
        "PROCYCLICAL filter -- the opposite of the countercyclical prior, which "
        "says reduce equity when the ratio is high -- not a validated recession "
        "forecast. Judge it by its shallower drawdown (-8.8% vs -23.9%) and "
        "lower volatility, not by the headline Sharpe."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/retail_inv_sales_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/retail_inv_sales_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/retail_inv_sales_spy/tournament_results_20260831.csv"},
        {"label": "Stationarity tests", "path": "results/retail_inv_sales_spy/stationarity_tests_20260831.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 3-month-lagged inventories-to-sales ratio was at or above its five-year rolling median (i.e. when the ratio was *high* a quarter earlier); otherwise hold cash. This is a procyclical rule and runs against the countercyclical prior, which says reduce equity when the ratio is high.

If-then form:
- **IF** `invsales_level` from 3 months earlier is at or above its 60-month rolling median -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-06-30 to 2025-07-31, 98 months): Sharpe 1.23 versus 0.91 buy-and-hold; annualized return 12.1% versus 14.4%; **maximum drawdown -8.8% versus -23.9%**; annualized volatility 9.7%; win rate 42.9%; 16 trades; annual turnover 1.96 (moderate). The drawdown and volatility reduction, not the Sharpe or return, is the defensible result.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Retail Inventories-to-Sales Ratio (`RETAILIRSA`, Census / Data Master) at month-end. Second, it takes the ratio level directly (`invsales_level`). Third, it applies a 3-month lag before the SPY allocation is set. Finally, the lagged level is compared with its 60-month rolling median: when the lagged level is at or above that median, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return (low here partly because the rule sits in cash for stretches).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the Retail Inventories-to-Sales Ratio (RETAILIRSA) at month end.
2. Take the ratio level directly.
3. Take the value from 3 months earlier and compare it with its trailing 60-month rolling median.
4. Hold SPY when that lagged level was at or above the rolling median; otherwise hold cash.
5. Recheck monthly. Turnover is moderate (1.96/yr).
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
        "(-0.55 vs -0.70). The stress defense is where its drawdown edge was "
        "earned, but it is in-sample and the direction still contradicts the "
        "prior."
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
            "2.3)."
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

1. The winner is PROCYCLICAL at a 3-month lead -- the opposite of the countercyclical prior, which says reduce equity when the ratio is high. Concurrent quartiles are countercyclical (rising ratio = worse market), so the procyclical rule is most likely a search artifact, not a real relationship.
2. Granger causality is insignificant at every lag (min p = 0.32), local projections are null, and the pre-whitened CCF is significant only at lag 0 and on the SPY-leads side -- so this is not a proven causal forecast.
3. The result is marked `found_in_search`; the median valid combo underperforms buy-and-hold, and the winner still needs a frozen-rule holdout confirmation. The bootstrap p < 0.01 is an in-sample significance check, not out-of-sample validation.
4. The defensible virtue is drawdown and volatility reduction, not return: annualized return (12.1%) is slightly BELOW buy-and-hold (14.4%).
5. A tempting post-hoc rationale -- that the ratio spikes in recessions and "buy when high" catches recovery rebounds -- is a story fitted to a search-selected result, not a validated mechanism.
6. COVID 2020 is an extreme in-window outlier (the ratio spiked and reversed) that can dominate the fit. The ratio's level also drifts across decades, which is why a rolling-median threshold is used.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 3-month-lagged inventories-to-sales level crossed at or "
        "above its rolling median, taking exposure from 0% to 100% SPY. A SELL "
        "moves back to cash when the lagged level fell below the rolling median."
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
    "The winning signal is `invsales_level`, the ratio level used directly, with "
    "a 3-month lead, a 60-month rolling-median threshold (which re-centers on "
    "recent history and absorbs the level's drift), and a procyclical "
    "orientation (long SPY when the lagged level is at or above the median)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the inventories-to-sales signal move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do improving and deteriorating demand regimes behave differently? | Makes the countercyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past inventories-to-sales information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: inventories-to-sales transforms (level, 1-month change, 12-month change, 60-month z-score) x fixed and rolling thresholds x long/cash strategy x lead times (0-12 months). The final tournament has 168 combinations, all 168 valid. The winning rule is `invsales_level / T_roll_p50 / P1_long_cash procyclical / L3`, the maximum OOS Sharpe (1.23). The median valid combo (0.701) underperforms buy-and-hold (0.91), and the runner-up (`invsales_level / T_roll_p50 / L1`, 1.19) shares the winner's signal and rolling-median threshold at a shorter lead -- read the winner as a selection maximum in a short-lead level cluster, not a validated edge. That direction (long when the ratio is high) contradicts the countercyclical prior and is treated as a search artifact.
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
