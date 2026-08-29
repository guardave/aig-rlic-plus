"""Manufacturers' New Orders x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY factory-demand pair. Manufacturers' New Orders (total
manufacturing, nominal $, monthly; Data Master NEWORDER / Census M3 / FRED
NEWORDER) is a classic LEADING indicator -- a Conference Board LEI component --
whose economic PRIOR is PROCYCLICAL (rising orders growth -> risk-on). The
nominal-dollar LEVEL is non-stationary (ADF fails to reject a unit root; KPSS
rejects stationarity), so every tested signal is a growth transform
(MoM/3m/6m/YoY %, YoY z-score, acceleration).

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/mfg_new_orders_spy/*:
  - The tournament winner (`yoy` YoY growth / T_roll_p50 rolling-median /
    COUNTERCYCLICAL / L12 months / P1_long_cash; OOS Sharpe 1.56 vs 0.96 B&H)
    is the grid maximum over 252 combinations (all 252 valid). The MEDIAN
    valid combo scores 0.684 -- it UNDERPERFORMS buy-and-hold (0.96)
    (winner_summary.json).
  - DIRECTION CONTRADICTS THE PRIOR. New-orders growth is procyclical and a
    LEADING indicator, yet the search selected a COUNTERCYCLICAL rule (hold SPY
    when 12-month-lagged growth is AT OR BELOW its 5-year rolling median) at a
    12-MONTH lead. This is flagged as a likely search artifact -- part of the
    fleet-wide long-lead pattern (issue #28) -- NOT as a real inverse-12-month
    signal. `interpretation_metadata.json` records expected_direction
    procyclical vs observed_direction countercyclical, direction_consistent
    = false, confidence = low.
  - The concurrent evidence points the ORDINARY procyclical way: sorting
    months by YoY new-orders growth, the weakest-growth quartile Q1 has the
    worst concurrent SPY Sharpe (0.14), and higher-growth quartiles are better
    (Q2 1.30, Q3 0.90, Q4 0.95) (regime_quartile_returns.csv). That tension --
    procyclical concurrently, but a countercyclical winner at a 12-month lead
    -- is the central caveat of this pair.
  - No lead-lag forecast. New-orders growth does NOT Granger-cause SPY at any
    tested lag (minimum p = 0.44 at lag 6) (granger_by_lag.csv). Linear
    correlation with forward SPY is near zero at every horizon; the only
    nominally significant cell is MoM growth vs 1-month-forward SPY (r = 0.12,
    p = 0.02), a weak positive (core_models_20260830/correlations.csv). Local
    projections are near-null at every horizon (no coefficient significant;
    trivial R^2) (local_projections.csv). Pre-whitened cross-correlation is
    significant ONLY at NEGATIVE lags (SPY tends to move BEFORE new orders) --
    the reverse of a forecasting signal -- with no significant lead-side bars
    (ccf_prewhitened.csv).
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: OOS max drawdown
    -6.1% vs -23.9% for buy-and-hold, at a slightly LOWER annual return
    (13.9% vs 14.8%) and much lower volatility (8.6%) -- read the Sharpe as
    volatility avoidance, not a return advantage. Turnover is LOW (0.81/yr,
    7 OOS trades): the rule sits in or out for long stretches. A stationary
    block bootstrap puts the winner's Sharpe at p = 0.004
    (tournament_validation_20260830/bootstrap.csv), but that is an in-sample
    significance check, not out-of-sample validation.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - Nominal (not inflation-adjusted), revised in later Census M3 releases;
    COVID 2020-21 collapse/rebound is an extreme in-window outlier that can
    dominate the fit.

MONTHLY conventions: leads in MONTHS (winner L12); Sharpe annualized by
sqrt(12); OOS window 2017-01-31 -> 2025-08-31 (104 months). Numbers sourced
from results/mfg_new_orders_spy/ (winner_summary.json, kpis.json,
evidence_status.json, interpretation_metadata.json, core_models_20260830/*,
regime_quartile_returns.csv, subperiod_sharpe.csv, granger_by_lag.csv,
stationarity_tests_20260830.csv, structural_break_mfg_new_orders_spy.json,
tournament_results_20260830.csv, tournament_validation_20260830/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Factory New Orders as a Defensive SPY Overlay"
    PAGE_SUBTITLE = (
        "Manufacturers' New Orders (Data Master / Census M3 NEWORDER) x "
        "S&P 500 (SPY), monthly factory-demand growth signals tested against "
        "SPY returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.56 OOS, but the honest headline is the drawdown "
        "(-6.1% vs -23.9%) -- and the winning rule is COUNTERCYCLICAL at a "
        "12-month lead, the opposite of what a leading factory-demand "
        "indicator should be"
    )

    PLAIN_ENGLISH = (
        "Manufacturers' New Orders is the dollar value of new orders U.S. "
        "factories booked each month for goods yet to be produced. Because "
        "companies order ahead of production, it is a classic LEADING "
        "indicator -- one of the components of the Conference Board's Leading "
        "Economic Index -- and the economic prior is procyclical: rising "
        "orders growth signals expansion and risk-on equities. This pair tests "
        "whether new-orders growth can improve SPY timing. Read the result as "
        "factory-demand context and drawdown control, not as a forecast: the "
        "formal lead-lag tests find no predictive edge, and the rule the "
        "search selected runs the WRONG way (buy when growth is weak) at a "
        "12-month lag -- most likely a search artifact, not a real signal."
    )

    WHERE_THIS_FITS = (
        "This is a factory-demand overlay for broad U.S. equities. It belongs "
        "in the portal as a defensive context signal: useful for drawdown "
        "control in the searched sample, but not a standalone forecast, and "
        "not evidence that new orders lead the market. Readers wanting genuine "
        "advance warning should treat the concurrent, procyclical reading "
        "(stronger orders = better equity conditions) as the economically "
        "sensible one and the countercyclical 12-month winner with skepticism."
    )

    ONE_SENTENCE_THESIS = (
        "New-orders growth is procyclical with equities CONCURRENTLY (weakest "
        "growth quartile has the worst SPY Sharpe, 0.14) but does NOT lead SPY "
        "-- Granger is insignificant at every lag (min p = 0.44) and local "
        "projections are null -- so the search's best rule, a COUNTERCYCLICAL "
        "filter at a 12-month lead, is a drawdown-reduction candidate "
        "(-6.1% vs -23.9% max drawdown) whose direction and lead contradict "
        "the economic prior and are most likely a search artifact (issue #28)."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 104-month window (2017-01-31 -> 2025-08-31). The winner was "
        "found as the best of 252 valid combinations, and the MEDIAN valid "
        "combo (0.684) UNDERPERFORMS buy-and-hold (0.96) -- the typical rule "
        "subtracts value. The defensible number is the max drawdown "
        "(-6.1% vs -23.9%) at a slightly LOWER return (13.9% vs 14.8%) and "
        "much lower volatility (8.6%) -- read the Sharpe (1.56 vs 0.96) as "
        "volatility avoidance, not stock-picking skill. Sharpe ratios use "
        "monthly sqrt(12) annualization."
    )

    HERO_TITLE = "Manufacturers' New Orders vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the new-orders level (nominal $, left axis) is shown "
        "with SPY on the same time axis, NBER recessions shaded. Both trend up "
        "over decades; the traded signal is not the level (it is "
        "non-stationary) but its year-over-year growth. Watch the shaded "
        "recessions -- new orders fell during them, but as a leading "
        "indicator it typically rolled over into, not long before, the equity "
        "downturns in this window."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by New-Orders Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest new-orders "
        "growth) to Q4 (strongest), with concurrent SPY Sharpe in each. The "
        "weakest-growth quartile Q1 is clearly the worst (Sharpe 0.14), and "
        "the stronger-growth quartiles are better (Q2 1.30, Q3 0.90, Q4 0.95) "
        "-- broadly PROCYCLICAL concurrently. This is the economically "
        "sensible reading, and it runs OPPOSITE to the countercyclical rule "
        "the tournament selected. Descriptive and concurrent, not a "
        "tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **countercyclical, 12-month-lagged new-orders-growth filter**. It holds SPY when year-over-year new-orders growth from twelve months earlier was at or below its five-year rolling median, and holds cash otherwise. Out-of-sample (2017-01 to 2025-08), this rule earns a Sharpe of 1.56 versus 0.96 for buy-and-hold, with a maximum drawdown of **-6.1% versus -23.9%** at an annualized return of 13.9% versus 14.8%. Read that as the honest headline: the rule's edge is a much shallower worst-case loss and lower volatility, **not** a return advantage.

### The Factory-Demand Hypothesis

Manufacturers' new orders measures forward demand for factory goods -- orders booked now for production later. Because businesses commit ahead of output, it is a **leading** indicator, a component of the Conference Board's Leading Economic Index. The economic prior is that new-orders growth is **procyclical**: firm, rising orders are risk-on for equities; slowing orders are an early sign demand is cooling.

The concurrent evidence supports that prior: sort months by new-orders growth and the weakest-growth quartile has the worst concurrent SPY Sharpe (0.14), with stronger-growth quartiles better. But the tournament's winning rule runs the **opposite** way -- it buys SPY when 12-month-lagged growth is *weak* -- and at a 12-month lead. That direction-and-lead combination contradicts the economic prior.

### Why This Is Not a Forecast

The formal lead-lag tests are blunt. New-orders growth does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.44), forward-return correlations are near zero at every horizon, and local projections are essentially null. The pre-whitened cross-correlation is significant only at *negative* lags -- SPY tends to move *before* new orders -- the reverse of a forecasting signal. So the countercyclical 12-month lead the search selected is economically implausible for a leading, procyclical indicator; it most plausibly reflects the fleet-wide long-lead search pattern (issue #28), not a real inverse channel. This dashboard therefore treats the pair as a searched factory-demand overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "New orders fell with the tech-capex bust. As a leading "
                "indicator it softened around the downturn, but the searched "
                "rule did NOT protect here -- its subperiod Sharpe was worse "
                "than buy-and-hold in this window."
            ),
            "caption": "Dot-Com: new orders fell with the capex bust; the rule did not defend here.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "New orders collapsed through 2008-09 as the goods economy "
                "seized up. The rule lost less than buy-and-hold in this "
                "window, part of its drawdown story, but still fell."
            ),
            "caption": "GFC: new orders collapsed 2008-09; the rule lost less than SPY.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "New orders collapsed in spring 2020 and rebounded violently. "
                "This is an extreme, exogenous in-window outlier that can "
                "dominate the backtest fit -- read any rule that leans on it "
                "with caution."
            ),
            "caption": "COVID: extreme collapse and rebound, an outlier that can dominate the fit.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Nominal new orders stayed elevated through 2022 because "
                "prices were rising, even as equities de-rated. This is the "
                "key caveat of a nominal-dollar series: inflation can keep the "
                "growth signal firm while the market falls."
            ),
            "caption": "2022: nominal orders stayed high on inflation while SPY sold off.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is procyclical but imperfect as a forecast. New orders fell during the Dot-Com, GFC and COVID recessions -- but the searched rule's protection was uneven: it did worse than buy-and-hold in the Dot-Com bear, lost less in the GFC, and sat in cash (flat) through COVID and the 2022 rate shock while SPY fell. In 2022 the nominal series stayed high on inflation, exactly when a demand signal would have been most useful. The strongest honest reading is not "new orders predicts drawdowns"; it is that a lagged, countercyclical filter happened to step to cash during several stress windows, which is where its drawdown advantage was earned.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this factory-demand story survives "
        "correlation, lead-lag, regime, and strategy checks. It largely does "
        "not survive as a forecast -- the value is defensive, not predictive, "
        "and the winner's direction contradicts the procyclical prior."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether new-orders growth and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster new-orders growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean stronger new-orders growth lines up with stronger future SPY "
        "returns; pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon. The only nominally significant cell is MoM growth "
        "vs the 1-month-forward SPY return (r = 0.12, p = 0.02), a weak "
        "positive -- not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; "
        "the YoY-vs-forward cells are near zero (|r| < 0.03), and the largest "
        "cell anywhere is MoM growth vs 1-month-forward SPY at r = 0.12."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair. The more "
        "relevant question is whether a lagged growth filter improves "
        "portfolio behavior in the searched sample."
    ),
    key_message="New-orders growth is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does new-orders growth lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-12 is 0.44 -- new-orders growth does not Granger-cause "
        "SPY returns."
    ),
    observation=(
        "Across all twelve monthly lags the NEWORDERS->SPY p-value never falls "
        "below 0.44; the F-statistics are tiny. There is no formal evidence "
        "of lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal claim. The strategy must be framed as a "
        "searched factory-demand overlay, not proof that new orders cause "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.44); new orders does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by new-orders YoY growth and "
        "compares concurrent SPY returns across factory-demand regimes."
    ),
    question="Do weak and strong factory-demand regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-growth regime; Q4 is the strongest. Compare "
        "Sharpe, average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: broadly PROCYCLICAL -- the weakest-growth quartile "
        "Q1 has the worst concurrent SPY Sharpe (0.14), and higher-growth "
        "quartiles are better (Q2 1.30, Q3 0.90, Q4 0.95). This runs opposite "
        "to the countercyclical winner."
    ),
    observation=(
        "Concurrent SPY Sharpe is far lower in the weakest-growth quartile "
        "(Q1 0.14) than in the stronger-growth quartiles (Q2 1.30, Q3 0.90, "
        "Q4 0.95) -- higher factory-demand growth generally coincides with "
        "better equity conditions."
    ),
    interpretation=(
        "The concurrent pattern fits a procyclical factory-demand story. That "
        "makes the tournament's COUNTERCYCLICAL winner economically "
        "counter-intuitive and reinforces reading it as a search artifact, "
        "not a real inverse relationship."
    ),
    key_message="Stronger factory demand coincides with better SPY conditions -- procyclical, opposite the winner's direction.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does new-orders growth line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "new orders leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the significant bars sit ENTIRELY at negative lags "
        "-- SPY tends to move BEFORE new orders -- with no significant "
        "lead-side (new-orders-leads-SPY) bars. That is the reverse of a "
        "forecasting signal."
    ),
    observation=(
        "Correlations are significant only at negative lags (SPY leading new "
        "orders, ccf up to ~0.24); every positive lead-side offset is inside "
        "the confidence band and insignificant."
    ),
    interpretation=(
        "There is no coherent window in which new-orders growth foreshadows "
        "SPY. If anything the causality runs the other way (markets "
        "anticipating factory demand), which argues against a new-orders "
        "forecast of SPY."
    ),
    key_message="Significant correlation is on the SPY-leads side; new orders shows no forecasting lead over SPY.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the new-orders-growth signal."
    ),
    question="How does SPY respond after new-orders growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "new-orders-growth signal. Coefficients near zero mean no detectable "
        "effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across all "
        "horizons (1, 3, 6, 12 months), none statistically significant "
        "(p from 0.57 to 0.93), with negligible R^2."
    ),
    observation=(
        "Point estimates are near zero at every horizon and no coefficient is "
        "significant; the explained variance is trivial throughout."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. "
        "Nothing here rescues a forward-looking reading of the indicator."
    ),
    key_message="Local projections are null; new-orders growth carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the new-orders signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does new-orders growth behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is close to zero and flat across "
        "quantiles -- no material tail sensitivity for the new-orders signal."
    ),
    observation=(
        "The estimated coefficient is small and essentially unchanged across "
        "the tested quantiles, consistent with the near-null correlation and "
        "local-projection results."
    ),
    interpretation=(
        "New-orders growth does not flag elevated crash risk or exceptional "
        "upside -- there is no tail channel to trade."
    ),
    key_message="New-orders growth shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: New Orders Is Procyclical Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a cautious factory-demand overlay -- and "
        "nothing stronger. The strategy winner improves search-phase OOS "
        "Sharpe, but formal lead-lag evidence is absent (Granger min p = 0.44; "
        "local projections null; CCF significant only on the SPY-leads side), "
        "and the winner's COUNTERCYCLICAL direction at a 12-month lead "
        "contradicts the procyclical, leading-indicator prior."
    ),
    "plain_english": (
        "This page asks whether new-orders growth helps time SPY. The answer "
        "is: not as a forecast. Concurrent quartiles are procyclical (weak "
        "growth = worse market), but the causal tests find no lead, and the "
        "best rule runs the opposite way at a 12-month lag. Treat it as a "
        "defensive, after-the-fact overlay, not an early-warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 252 strategy combinations (all 252 valid) "
        "across six new-orders growth transforms, fixed and rolling "
        "thresholds, procyclical/countercyclical orientations, and leads from "
        "0 to 12 months. The selected winner is `yoy / T_roll_p50 / "
        "P1_long_cash countercyclical / L12`, with OOS Sharpe 1.56. The MEDIAN "
        "valid combo scores 0.684 -- below buy-and-hold's 0.96 -- and the "
        "runner-up (`chg_3m / T_roll_p50 / countercyclical / L12`, 1.482) "
        "shares the same rolling-median threshold and 12-month lead, so the "
        "search surface concentrates on long-lead countercyclical rules "
        "(the fleet-wide issue #28 pattern), not a robust economic edge."
    ),
    "transition": (
        "**Transition:** the evidence is procyclical context, not causation, "
        "and the winner runs against the prior. The Strategy page shows the "
        "exact long/cash rule, the drawdown advantage that is its real "
        "virtue, and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Countercyclical, Lagged New-Orders Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using year-over-year new-orders "
        "growth, a rolling-median threshold, a countercyclical orientation, "
        "and a 12-month lead -- valued for drawdown reduction, not for its "
        "Sharpe, and flagged as running against the economic prior."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when year-over-year new-orders growth from twelve "
        "months earlier was at or below its five-year rolling median; "
        "otherwise it holds cash. This is a lagged, COUNTERCYCLICAL "
        "factory-demand filter -- the opposite of the procyclical prior for a "
        "leading indicator -- not a real-time recession forecast. Judge it by "
        "its shallower drawdown (-6.1% vs -23.9%) and lower volatility, not by "
        "the headline Sharpe."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/mfg_new_orders_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/mfg_new_orders_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/mfg_new_orders_spy/tournament_results_20260830.csv"},
        {"label": "Stationarity tests", "path": "results/mfg_new_orders_spy/stationarity_tests_20260830.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 12-month-lagged year-over-year change in new orders was at or below its five-year rolling median (i.e. when factory-demand growth was *weak* a year earlier); otherwise hold cash. This is a countercyclical rule and runs against the procyclical prior.

If-then form:
- **IF** `mfg_new_orders_yoy` from 12 months earlier is at or below its 60-month rolling median -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2025-08-31, 104 months): Sharpe 1.56 versus 0.96 buy-and-hold; annualized return 13.9% versus 14.8%; **maximum drawdown -6.1% versus -23.9%**; annualized volatility 8.6%; win rate 37.5%; 7 trades; annual turnover 0.81 (low). The drawdown and volatility reduction, not the Sharpe or return, is the defensible result.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads Manufacturers' New Orders (`NEWORDER`, total manufacturing, nominal $) at month-end. Second, it computes the year-over-year percent change in new orders (`mfg_new_orders_yoy`). Third, it applies a 12-month lag before the SPY allocation is set. Finally, the lagged signal is compared with its 60-month rolling median: when the lagged growth is at or below that median, hold SPY; otherwise cash (the countercyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return (low here partly because the rule sits in cash for long stretches).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Manufacturers' New Orders (NEWORDER) at month end.
2. Compute the year-over-year percent change.
3. Take the value from 12 months earlier and compare it with its trailing 60-month rolling median.
4. Hold SPY when that lagged growth was at or below the rolling median; otherwise hold cash.
5. Recheck monthly. Turnover is low (0.81/yr): the rule holds a position for long stretches.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule loses LESS in the GFC "
        "(-0.80 vs -1.03) and sits in cash (flat, Sharpe 0.0) through COVID "
        "and the 2022 rate shock while SPY fell -- but it does WORSE than "
        "buy-and-hold in the Dot-Com bear (-0.92 vs -0.70). The stress "
        "defense is real but uneven."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is new-orders growth; the target "
            "is SPY returns. The rolling correlation tests whether their "
            "linear relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "new-orders/SPY relationship changes enough that one fixed model "
            "is unlikely to describe the whole sample. A larger break "
            "statistic means the relationship shifted more materially across "
            "periods (here the max absolute rolling-correlation z-score "
            "reaches 3.7)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.56) is a right-tail maximum; the "
        "median valid combo (0.684) sits BELOW buy-and-hold (0.96), so the "
        "typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The winner is COUNTERCYCLICAL at a 12-month lead -- the opposite of the procyclical, leading-indicator prior. Concurrent quartiles are procyclical (weak growth = worse market), so the inverse 12-month rule is most likely a search artifact (the fleet-wide long-lead pattern, issue #28), not a real inverse signal.
2. Granger causality is insignificant at every lag (min p = 0.44), local projections are null, and the pre-whitened CCF is significant only on the SPY-leads side -- so this is not a proven causal forecast.
3. The result is marked `found_in_search`; the median valid combo underperforms buy-and-hold, and the winner still needs a frozen-rule holdout confirmation. The bootstrap p = 0.004 is an in-sample significance check, not out-of-sample validation.
4. The defensible virtue is drawdown and volatility reduction, not return: annualized return (13.9%) is slightly BELOW buy-and-hold (14.8%).
5. New orders is nominal: in 2022 inflation kept the growth signal firm while equities fell, and advance figures are revised in later Census M3 releases.
6. COVID 2020-21 is an extreme in-window outlier that can dominate the fit.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 12-month-lagged year-over-year new-orders growth crossed "
        "at or below its rolling median, taking exposure from 0% to 100% SPY. "
        "A SELL moves back to cash when the lagged growth rose above the "
        "rolling median."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1997-12-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: yoy countercyclical rule crossed T_roll_p50; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master (Census M3 / FRED) | `NEWORDER`, Manufacturers' New Orders: Total Manufacturing (nominal $, SA) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is Manufacturers' New Orders, total manufacturing, in "
    "nominal $ (seasonally adjusted). The level is non-stationary (ADF fails "
    "to reject a unit root, p = 0.15; KPSS rejects stationarity), so the "
    "pipeline constructs growth transforms -- month-over-month, three-month, "
    "six-month, and twelve-month percent changes; a 60-month rolling YoY "
    "z-score; and YoY acceleration -- all of which are stationary. The winning "
    "signal is `mfg_new_orders_yoy`, the year-over-year growth, used with a "
    "12-month lead, a 60-month rolling-median threshold, and a countercyclical "
    "orientation (long SPY when lagged growth is at or below the median)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does new-orders growth move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong factory-demand regimes behave differently? | Makes the procyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past new-orders information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: new-orders growth transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x lead times (0-12 months). The final tournament has 252 combinations, all 252 valid. The winning rule is `mfg_new_orders_yoy / T_roll_p50 / P1_long_cash countercyclical / L12`, the maximum OOS Sharpe (1.56). The median valid combo (0.684) underperforms buy-and-hold (0.96), and the runner-up (`chg_3m / T_roll_p50 / countercyclical / L12`, 1.482) shares the winner's rolling-median threshold and 12-month lead -- read the winner as a selection maximum in a long-lead countercyclical cluster, not a validated edge. That cluster contradicts the procyclical, leading-indicator prior and is treated as the fleet-wide long-lead artifact (issue #28).
"""

_REFERENCES_MD = """
1. U.S. Census Bureau, Manufacturers' Shipments, Inventories and Orders (M3), new orders series (`NEWORDER`).
2. Federal Reserve Economic Data (FRED), `NEWORDER`, Manufacturers' New Orders: Total Manufacturing.
3. The Conference Board, Leading Economic Index (new orders is a component).
4. Yahoo Finance, SPY adjusted price history.
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
        "Monthly sample from 1993-01-31 to 2025-08-31, with out-of-sample "
        "window 2017-01-31 to 2025-08-31 (104 months). SPY history limits the "
        "usable sample even though new orders begins earlier."
    ),
    plain_english=(
        "This page documents how Manufacturers' New Orders was turned into "
        "stationary growth signals, how the econometric checks were run, and "
        "how the tournament selected the final SPY allocation rule -- along "
        "with the honest caveat that the selection maximum is a countercyclical "
        "long-lead rule that contradicts the procyclical prior and is not yet a "
        "validated edge."
    ),
)
