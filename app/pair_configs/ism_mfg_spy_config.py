"""ISM Manufacturing PMI x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY business-cycle pair. The ISM Manufacturing PMI (Data Master
NAPM; the Institute for Supply Management's manufacturing diffusion index) is a
classic LEADING indicator whose economic PRIOR is PROCYCLICAL: readings above
~50 mark expansion and risk-on conditions, below 50 mark contraction. Unlike a
nominal-dollar level, the PMI is a BOUNDED, MEAN-REVERTING diffusion index --
it is LEVEL-STATIONARY (ADF rejects a unit root, p ~ 3.8e-5; KPSS does not
reject stationarity), so the level can be used directly. The tested signals are
the PMI level, its one-month change (diff_1m), its 12-month change (chg_12m),
and a 60-month z-score -- NOT growth/YoY transforms.

CORRECTION NOTE. An earlier run's winner (`diff_1m` / rolling-median threshold)
rested on a mislabeled "12-month change" that was in fact computed as a 4-month
change (diff(4)); with the properly computed 12-month change (diff(12)) the
tournament re-selected, and the winner is now `chg_12m` / T0_zero / L0 at OOS
Sharpe 1.44.

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/ism_mfg_spy/*:
  - The tournament winner (`chg_12m` 12-month PMI change / T0_zero zero
    threshold / PROCYCLICAL / L0 months / P1_long_cash; OOS Sharpe 1.44
    vs 0.95 B&H) is the grid maximum over 168 combinations (all 168 valid).
    The MEDIAN valid combo scores 0.70 -- it UNDERPERFORMS buy-and-hold (0.95)
    (winner_summary.json).
  - DIRECTION IS CONSISTENT WITH THE PRIOR. The PMI is procyclical and the
    search selected a PROCYCLICAL rule (hold SPY when the 12-month change in
    the PMI is at or above zero, i.e. when the PMI is at or above its level a
    year ago -- expanding year-over-year). `interpretation_metadata.json`
    records expected_direction procyclical, observed_direction procyclical,
    direction_consistent = true, confidence = low.
  - CONSISTENT CONCURRENT EVIDENCE. Sorting months by PMI level, the
    weakest-PMI quartiles Q1 and Q2 have the lower concurrent SPY Sharpe
    (0.44 and 0.43) and the strong-PMI quartiles Q3 and Q4 the higher (1.56
    and 0.95) -- broadly procyclical, though not perfectly monotonic (Q3, not
    Q4, is the peak) (regime_quartile_returns.csv). The sign of the winner
    agrees with this concurrent, procyclical reading -- a point in the pair's
    favor relative to the fleet's long-lead artifacts.
  - BUT NOT A FORECAST. The winner is CONCURRENT (L0), not predictive. PMI
    changes do NOT Granger-cause SPY at any tested lag (minimum p = 0.31 at
    lag 2) (granger_by_lag.csv). Forward-return correlations are near zero and
    none is significant at any horizon (largest |r| ~ 0.07, diff_1m vs
    6-month-forward SPY, p = 0.15; the winning 12-month change is near zero,
    |r| ~ 0.03) (core_models_20260912/correlations.csv). Local projections are
    null at every horizon (no coefficient significant; trivial R^2)
    (local_projections.csv). Pre-whitened cross-correlation is significant
    ONLY at NEGATIVE lags (SPY tends to move BEFORE the PMI); the concurrent
    (lag 0) and every lead-side (PMI-leads-SPY) bar sit inside the confidence
    band (ccf_prewhitened.csv). Read the rule as a coincident risk-regime
    overlay, not an early-warning forecast.
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: OOS max drawdown
    -6.3% vs -23.9% for buy-and-hold, at a LOWER annual return (12.7% vs
    15.1%) and much lower volatility (8.6%) -- read the Sharpe (1.44 vs 0.95)
    as volatility avoidance, not a return advantage.
  - TURNOVER IS LOW. The 12-month change crossing zero is a slow regime signal
    that flips rarely: annual turnover 1.22, 10 OOS trades. Transaction costs
    (assumed 5 bps) are a minor drag here -- a point in the rule's favor versus
    a fast filter.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - This is ISM MANUFACTURING, distinct from the separate ISM Services pair.
    PMI is survey-based (diffusion of respondents reporting improvement),
    lightly revised via seasonal-factor updates; the COVID 2020 collapse and
    violent rebound is an extreme in-window episode that can dominate the fit.

MONTHLY conventions: leads in MONTHS (winner L0); Sharpe annualized by
sqrt(12); OOS window 2017-09-30 -> 2025-10-31 (98 months). Numbers sourced from
results/ism_mfg_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20260912/*, regime_quartile_returns.csv,
subperiod_sharpe.csv, granger_by_lag.csv, stationarity_tests_20260912.csv,
structural_break_ism_mfg_spy.json, tournament_results_20260912.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: ISM Manufacturing PMI as a Procyclical SPY Overlay"
    PAGE_SUBTITLE = (
        "ISM Manufacturing PMI (Data Master NAPM diffusion index) x "
        "S&P 500 (SPY), monthly business-cycle signals tested against SPY "
        "returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.44 OOS vs 0.95 buy-and-hold, and the direction is the "
        "RIGHT way round for once (procyclical) -- but the honest headline is "
        "drawdown control (-6.3% vs -23.9%) at a LOWER return, and the rule "
        "is CONCURRENT, not a forecast"
    )

    PLAIN_ENGLISH = (
        "The ISM Manufacturing PMI is a monthly survey diffusion index: a "
        "reading above 50 means more factory managers report conditions "
        "improving than worsening (expansion), below 50 means the reverse "
        "(contraction). It is a classic LEADING indicator of the business "
        "cycle, and the economic prior is procyclical: a firm or rising PMI is "
        "risk-on for equities; a falling PMI is an early sign growth is "
        "cooling. This pair tests whether the PMI can improve SPY timing. The "
        "search's best rule keys off the 12-month CHANGE in the PMI and runs "
        "the economically sensible way (hold equity when the PMI is higher than "
        "it was a year ago, otherwise cash). But read it as a same-month "
        "risk-regime overlay and drawdown control, not a forecast: the formal "
        "lead-lag tests find no predictive edge, the rule is concurrent (zero "
        "lead), and -- being a slow year-over-year signal -- it trades rarely."
    )

    WHERE_THIS_FITS = (
        "This is a business-cycle overlay for broad U.S. equities. It belongs "
        "in the portal as a coincident risk-regime signal: useful for drawdown "
        "control in the searched sample, with a direction that matches both "
        "the economic prior and the concurrent evidence -- but it is not a "
        "standalone forecast, and it does not lead the market. Readers should "
        "treat it as 'ride equity while the factory cycle is expanding "
        "year-over-year, step aside when the PMI drops below its year-ago "
        "level', judged on risk reduction rather than on beating "
        "buy-and-hold's return."
    )

    ONE_SENTENCE_THESIS = (
        "The PMI is procyclical with equities CONCURRENTLY (the weak-PMI "
        "quartiles have the lower SPY Sharpe, 0.44/0.43; the strong-PMI "
        "quartiles the higher, 1.56/0.95) and the search's best rule agrees "
        "in sign, but the PMI does NOT lead SPY -- Granger is insignificant at "
        "every lag (min p = 0.31) and local projections are null -- so the "
        "winner, a procyclical 12-month-change filter at ZERO lead, is a "
        "coincident drawdown-reduction candidate (-6.3% vs -23.9% max "
        "drawdown) at a LOWER return (12.7% vs 15.1%) and low turnover, found "
        "in search and not yet validated."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-09-30 -> 2025-10-31). The winner was found "
        "as the best of 168 valid combinations, and the MEDIAN valid combo "
        "(0.70) UNDERPERFORMS buy-and-hold (0.95) -- the typical rule "
        "subtracts value. The defensible number is the max drawdown (-6.3% vs "
        "-23.9%) at a LOWER return (12.7% vs 15.1%) and much lower volatility "
        "(8.6%) -- read the Sharpe (1.44 vs 0.95) as volatility avoidance, not "
        "stock-picking skill. Turnover is low (1.22/yr, 10 trades), so costs "
        "are a minor drag. Sharpe ratios use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "ISM Manufacturing PMI vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the PMI level (left axis, with the 50 expansion/"
        "contraction line marked) is shown with SPY on the same time axis, "
        "NBER recessions shaded. The PMI is a bounded, mean-reverting diffusion "
        "index -- it oscillates around 50 rather than trending -- so it can be "
        "used directly (it is stationary). Watch the shaded recessions: the PMI "
        "dropped below 50 into each one. The traded signal is not the level but "
        "its 12-month change (whether the PMI is higher or lower than a year "
        "ago)."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by PMI Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest PMI) to Q4 "
        "(strongest), with concurrent SPY Sharpe in each. It is broadly "
        "PROCYCLICAL -- the two weakest-PMI quartiles (Q1 0.44, Q2 0.43) trail "
        "the two strongest (Q3 1.56, Q4 0.95), though the pattern is not "
        "perfectly monotonic (Q3, not Q4, is the peak). This matches the "
        "economic prior AND the sign of the tournament winner. Descriptive and "
        "concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical, concurrent PMI-momentum filter**. It holds SPY when the 12-month change in the ISM Manufacturing PMI is at or above zero (i.e. when the PMI is at or above its level a year ago -- expanding year-over-year), and holds cash otherwise -- with **zero lead**. Out-of-sample (2017-09 to 2025-10), this rule earns a Sharpe of 1.44 versus 0.95 for buy-and-hold, with a maximum drawdown of **-6.3% versus -23.9%** at an annualized return of 12.7% versus 15.1%. Read that as the honest headline: the rule's edge is a shallower worst-case loss and lower volatility (8.6%), **not** a return advantage. Because the signal is a slow year-over-year change, it trades rarely (turnover 1.22/yr, 10 OOS trades), so transaction costs are a minor drag.

### The Business-Cycle Hypothesis

The ISM Manufacturing PMI is a monthly diffusion index built from a survey of purchasing managers -- the share reporting improving conditions, netted against those reporting deterioration. Above 50 signals expansion, below 50 contraction. Because purchasing managers see order books and supplier deliveries early, the PMI is a **leading** indicator of the business cycle, and the economic prior is **procyclical**: a firm or rising PMI is risk-on for equities; a falling PMI warns that demand is cooling.

The concurrent evidence supports that prior: sort months by PMI level and the weak-PMI quartiles have the lower concurrent SPY Sharpe (0.44, 0.43), while the strong-PMI quartiles have the higher (1.56, 0.95) -- broadly procyclical, though not perfectly monotonic. The tournament's winning rule runs the **same** way -- it holds SPY when the PMI is expanding year-over-year -- so unlike several other pairs in the fleet, the direction here is economically sensible and internally consistent.

### Why This Is Still Not a Forecast

The sign is right, but the timing is coincident, not predictive. The formal lead-lag tests are blunt: the PMI change does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.31), forward-return correlations are near zero at every horizon (none significant), and local projections are essentially null. The pre-whitened cross-correlation is significant only at *negative* lags -- SPY tends to move *before* the PMI -- while the concurrent (lag 0) and every lead-side bar sits inside the confidence band. So the winner earns its keep by riding the *current* risk regime, not by seeing ahead. This dashboard therefore treats the pair as a coincident business-cycle overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "The PMI slid below 50 as the tech-capex bust hit "
                "manufacturing, and its 12-month change turned negative. The "
                "searched rule stepped to cash and lost LESS than buy-and-hold "
                "(subperiod Sharpe -0.46 vs -0.70; return -16.7% vs -33.4%)."
            ),
            "caption": "Dot-Com: PMI fell below 50 and year-over-year; the rule stepped aside and lost less than SPY.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The PMI collapsed into the low 30s through 2008-09 as the "
                "goods economy seized up, and the 12-month change went deeply "
                "negative. The rule lost far LESS than buy-and-hold "
                "(Sharpe -0.79 vs -1.03; return -6.0% vs -35.5%) -- the "
                "year-over-year contraction kept it in cash for much of the "
                "decline."
            ),
            "caption": "GFC: PMI collapsed 2008-09; the rule sat in cash and lost far less than SPY.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The PMI plunged in spring 2020 and rebounded violently. The "
                "12-month-change signal held cash into the collapse and this is "
                "the rule's best subperiod (Sharpe +1.55 vs -0.08). Read it "
                "with caution: it is one extreme, exogenous episode that can "
                "dominate the backtest fit, and a slow signal can be late to "
                "re-enter on the rebound."
            ),
            "caption": "COVID: the year-over-year signal was in cash into the collapse -- the rule's best, but a single outlier episode.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "The PMI ground lower through 2022 toward 50 as rate hikes bit, "
                "and it fell below its year-ago level. The rule sat in cash for "
                "the whole window (Sharpe 0.00, flat) and sidestepped SPY's "
                "rate-hike bear (-0.76) -- a sustained year-over-year decline is "
                "exactly where this slow filter helps most."
            ),
            "caption": "2022: PMI fell year-over-year through the rate-hike bear; the rule stayed in cash and avoided the drawdown.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is procyclical and defends concurrently through sustained downturns. The PMI fell below 50 into the Dot-Com, GFC and COVID recessions, and below its year-ago level through the 2022 rate-hike bear -- and the 12-month-change rule stepped to cash in each: it lost less than buy-and-hold in the Dot-Com bear and the GFC, sat entirely in cash through 2022 (avoiding an -18% SPY drawdown), and was net positive through COVID. Because it keys off a slow year-over-year change rather than a noisy one-month move, it does not whipsaw in choppy tape -- the trade-off is the opposite: a slow signal can be LATE to turn, both stepping aside after a decline is underway and re-entering after a bottom. The strongest honest reading is not "the PMI predicts drawdowns"; it is that a procyclical, same-month year-over-year filter tends to sit in cash while the factory cycle is contracting, which is where its drawdown advantage was earned -- at the cost of lag around turning points.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this business-cycle story survives "
        "correlation, lead-lag, regime, and strategy checks. The direction "
        "survives -- the concurrent evidence is procyclical and matches the "
        "winner -- but the forecast does not: the value is coincident and "
        "defensive, not predictive."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether the PMI signals and future SPY returns "
        "move together in a roughly linear way."
    ),
    question="Does a firmer PMI line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean a firmer PMI lines up with stronger future SPY returns; pale "
        "cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon and none of the cells is statistically significant. "
        "The largest cell anywhere is the one-month PMI change vs the "
        "6-month-forward SPY return (r = 0.07, p = 0.15), a weak positive; the "
        "winning 12-month-change signal correlates near zero with forward SPY "
        "(|r| ~ 0.03) -- not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; "
        "all |r| values are below ~0.07 and every p-value exceeds 0.14, so no "
        "cell is significant."
    ),
    interpretation=(
        "Correlation alone does not support forecasting the pair. The more "
        "relevant question is whether a concurrent PMI-momentum filter "
        "improves portfolio behavior in the searched sample."
    ),
    key_message="The PMI is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does the PMI change lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across the tested lags is 0.31 (lag 2) -- the PMI change does not "
        "Granger-cause SPY returns."
    ),
    observation=(
        "Across all tested monthly lags the PMI->SPY p-value never falls below "
        "0.31; the F-statistics are tiny. There is no formal evidence of "
        "lead-lag causality."
    ),
    interpretation=(
        "This rules out a forecasting claim. The strategy must be framed as a "
        "concurrent business-cycle overlay, not proof that the PMI causes "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.31); the PMI does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by PMI level and compares concurrent "
        "SPY returns across business-cycle regimes."
    ),
    question="Do weak and strong PMI regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-PMI regime; Q4 is the strongest. Compare Sharpe, "
        "average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: broadly PROCYCLICAL -- the weak-PMI quartiles Q1 and "
        "Q2 have the lower concurrent SPY Sharpe (0.44, 0.43) and the "
        "strong-PMI quartiles Q3 and Q4 the higher (1.56, 0.95), though the "
        "pattern is not perfectly monotonic (Q3 is the peak). This matches the "
        "winner's direction."
    ),
    observation=(
        "Concurrent SPY Sharpe is higher in the strong-PMI quartiles "
        "(Q1 0.44, Q2 0.43, Q3 1.56, Q4 0.95) -- a firmer PMI broadly "
        "coincides with better equity conditions, though not monotonically."
    ),
    interpretation=(
        "The concurrent pattern fits a procyclical business-cycle story and "
        "agrees with the tournament winner's direction -- a coherence point "
        "in the pair's favor, though still concurrent rather than predictive."
    ),
    key_message="A firmer PMI broadly coincides with better SPY conditions -- procyclical, matching the winner's direction.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does the PMI change line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "the PMI leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the significant bars sit at NEGATIVE lags (-6 to -1) "
        "-- SPY tends to move BEFORE the PMI -- while the concurrent (lag 0) "
        "and every lead-side (PMI-leads-SPY) bar is inside the band. That is "
        "the reverse of a forecasting signal."
    ),
    observation=(
        "Correlations are significant only at lags -6 to -1 (SPY leading the "
        "PMI, ccf up to ~0.17); the concurrent bar (lag 0) and every positive "
        "lead-side offset are inside the confidence band and insignificant."
    ),
    interpretation=(
        "There is no window in which the PMI change foreshadows SPY. If "
        "anything the market anticipates the PMI, which is why the winning "
        "rule is best used concurrently rather than as a forecast."
    ),
    key_message="Significant correlation is on the SPY-leads side; the PMI shows no significant concurrent or forecasting lead over SPY.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the PMI signal."
    ),
    question="How does SPY respond after the PMI changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the PMI "
        "signal. Coefficients near zero mean no detectable effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across all "
        "horizons (1, 3, 6 months), none statistically significant "
        "(p from 0.49 to 0.54), with negligible R^2."
    ),
    observation=(
        "Point estimates are near zero at every horizon and no coefficient is "
        "significant; the explained variance is trivial throughout."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. "
        "Nothing here rescues a forward-looking reading of the indicator."
    ),
    key_message="Local projections are null; the PMI carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the PMI signal matters differently "
        "in weak, normal, and strong SPY return environments."
    ),
    question="Does the PMI behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is close to zero and flat across "
        "quantiles -- no material tail sensitivity for the PMI signal."
    ),
    observation=(
        "The estimated coefficient is small and essentially unchanged across "
        "the tested quantiles, consistent with the near-null correlation and "
        "local-projection results."
    ),
    interpretation=(
        "The PMI does not flag elevated crash risk or exceptional upside -- "
        "there is no tail channel to trade."
    ),
    key_message="The PMI shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: The PMI Is Procyclical Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a coincident business-cycle overlay -- and "
        "nothing stronger. The strategy winner improves search-phase OOS "
        "Sharpe and its PROCYCLICAL direction matches both the economic prior "
        "and the concurrent quartiles, but formal lead-lag evidence is absent "
        "(Granger min p = 0.31; local projections null; CCF significant only "
        "on the SPY-leads side). The winner's zero lead confirms the signal "
        "works same-month, not ahead of the market."
    ),
    "plain_english": (
        "This page asks whether the PMI helps time SPY. The answer is: same "
        "month, yes; ahead of time, no. Concurrent quartiles are broadly "
        "procyclical (weak PMI = worse market) and the winning rule agrees in "
        "sign, but the causal tests find no lead, and the winner uses zero "
        "lead. Treat it as a coincident risk-regime overlay, not an "
        "early-warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 168 strategy combinations (all 168 valid) "
        "across four PMI signals (level, one-month change, 12-month change, "
        "60-month z-score), fixed and rolling thresholds, a procyclical "
        "long/cash strategy, and leads from 0 to 12 months. The selected "
        "winner is `chg_12m / T0_zero / P1_long_cash procyclical / L0`, "
        "with OOS Sharpe 1.44. The MEDIAN valid combo scores 0.70 -- below "
        "buy-and-hold's 0.95 -- and the runner-up (`chg_12m / T_roll_p50 / "
        "procyclical / L1`, 1.41) is the SAME 12-month-change signal with a "
        "rolling-median threshold at one-month lead, so the top of the search "
        "surface is consistent around the 12-month change. Read the winner as "
        "a selection maximum, not a validated edge."
    ),
    "transition": (
        "**Transition:** the evidence is procyclical context that works "
        "concurrently, not causation ahead of the market. The Strategy page "
        "shows the exact long/cash rule, the drawdown advantage that is its "
        "real virtue, the low-turnover cost profile, and the deployment "
        "caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical, Concurrent PMI Year-over-Year Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 12-month change in the ISM "
        "Manufacturing PMI, a zero threshold, a procyclical orientation, and "
        "zero lead -- valued for drawdown reduction, not for beating "
        "buy-and-hold's return, and flagged as concurrent (not predictive) and "
        "low-turnover."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 12-month change in the ISM Manufacturing "
        "PMI is at or above zero (the PMI is at or above its level a year "
        "ago); otherwise it holds cash. This is a same-month, PROCYCLICAL "
        "year-over-year filter -- the direction the economic prior expects -- "
        "not a real-time recession forecast (it uses zero lead and does not "
        "lead the market). Judge it by its shallower drawdown (-6.3% vs "
        "-23.9%) and lower volatility, not by beating buy-and-hold on return "
        "(it does not: 12.7% vs 15.1%)."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/ism_mfg_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/ism_mfg_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/ism_mfg_spy/tournament_results_20260912.csv"},
        {"label": "Stationarity tests", "path": "results/ism_mfg_spy/stationarity_tests_20260912.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 12-month change in the ISM Manufacturing PMI is at or above zero (i.e. when the PMI is at or above its level a year ago -- expanding year-over-year); otherwise hold cash. This is a procyclical rule and matches the economic prior. It uses **zero lead** -- the current month's 12-month change sets the current allocation.

If-then form:
- **IF** the 12-month PMI change `ism_chg_12m` is at or above zero (the PMI is at or above its level 12 months ago) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-09-30 to 2025-10-31, 98 months): Sharpe 1.44 versus 0.95 buy-and-hold; annualized return 12.7% versus 15.1%; **maximum drawdown -6.3% versus -23.9%**; annualized volatility 8.6%; win rate 37.8%; 10 trades; annual turnover 1.22 (low). The drawdown and volatility reduction, not the Sharpe or return, is the defensible result -- and the low turnover means costs are only a minor drag.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the ISM Manufacturing PMI (`NAPM`, diffusion index) at month-end. Second, it computes the 12-month change in the PMI (`ism_chg_12m`), this month's level minus the level 12 months ago. Third, no additional lag is applied (L0): the current-month change sets the current allocation. Finally, the change is compared with zero, a fixed threshold: when the 12-month change is at or above zero, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year (low here -- the 12-month change crossing zero is a slow signal that flips rarely). Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the ISM Manufacturing PMI (NAPM) at month end.
2. Compute the 12-month change (this month's PMI minus the level 12 months ago).
3. Check whether that change is at or above zero (is the PMI higher than a year ago?).
4. Hold SPY when the change is at or above zero; otherwise hold cash.
5. Recheck monthly. Turnover is low (1.22/yr, 10 OOS trades): the year-over-year change crosses zero rarely, so transaction costs are a minor consideration.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The defense is consistent: the rule "
        "lost less in the Dot-Com bear (-0.46 vs -0.70) and the GFC (-0.79 vs "
        "-1.03), sat entirely in cash through the 2022 rate shock (0.00 vs "
        "-0.76), and was strongly positive through COVID (+1.55 vs -0.08, a "
        "single striking episode). The slow year-over-year signal steps aside "
        "through sustained downturns rather than whipsawing."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the PMI change; the target is "
            "SPY returns. The rolling correlation tests whether their linear "
            "relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "PMI/SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship shifted more materially across periods "
            "(here the max absolute rolling-correlation z-score reaches 2.4)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.44) is a right-tail maximum at "
        "zero lead; the median valid combo (0.70) sits BELOW buy-and-hold "
        "(0.95), so the typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The winner is CONCURRENT (zero lead), not a forecast. Granger causality is insignificant at every lag (min p = 0.31), local projections are null, and the pre-whitened CCF is significant only on the SPY-leads side -- so this rides the current risk regime rather than predicting it.
2. The result is marked `found_in_search`; the median valid combo (0.70) underperforms buy-and-hold (0.95), and the winner still needs a frozen-rule holdout confirmation. Confidence is LOW.
3. The defensible virtue is drawdown and volatility reduction, not return: annualized return (12.7%) is BELOW buy-and-hold (15.1%).
4. Turnover is LOW (1.22/yr, 10 OOS trades). The 12-month change crossing zero is a slow signal, so transaction costs at the assumed 5 bps per trade are only a minor drag -- but the trade-off of a slow filter is LAG around turning points (late to step aside, late to re-enter).
5. The direction and concurrent evidence are coherent (procyclical, matching the prior and the quartiles) -- a point in the pair's favor -- but coherence is not validation.
6. COVID 2020 is an extreme in-window episode that drives the winner's best subperiod and can dominate the fit; the PMI is survey-based and lightly revised via seasonal-factor updates.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 12-month PMI change crossed to at or above zero (the PMI "
        "back at or above its year-ago level), taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when the 12-month change fell below "
        "zero. Because the year-over-year change crosses zero rarely, the log "
        "has few round-trips (10 OOS trades)."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1995-01-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: chg_12m procyclical rule crossed T0_zero; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master (Institute for Supply Management) | `NAPM`, ISM Manufacturing PMI (diffusion index, SA) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the ISM Manufacturing PMI, a diffusion index bounded "
    "roughly between 30 and 65 and centered near 50 (the expansion/contraction "
    "line). Unlike a nominal-dollar level, the PMI is LEVEL-STATIONARY: it "
    "mean-reverts around ~50, ADF rejects a unit root (p ~ 3.8e-5) and KPSS "
    "does not reject stationarity, so the level can be used directly. The "
    "pipeline also constructs the one-month change, the 12-month change, and a "
    "60-month rolling z-score -- all stationary. The winning signal is "
    "`ism_chg_12m`, the 12-month change in the PMI, used with zero lead, a "
    "fixed zero threshold (the natural expansion/contraction pivot -- the PMI "
    "above versus below its year-ago level), and a procyclical orientation "
    "(long SPY when the 12-month change is at or above zero)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the PMI move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong PMI regimes behave differently? | Makes the procyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past PMI information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: four PMI signals (level, one-month change, 12-month change, 60-month z-score) x fixed and rolling thresholds x a procyclical long/cash strategy x lead times (0-12 months). The final tournament has 168 combinations, all 168 valid. The winning rule is `ism_chg_12m / T0_zero / P1_long_cash procyclical / L0`, the maximum OOS Sharpe (1.44). The median valid combo (0.70) underperforms buy-and-hold (0.95), and the runner-up (`chg_12m / T_roll_p50 / procyclical / L1`, 1.41) is the SAME 12-month-change signal with a rolling-median threshold at one-month lead -- so the top of the surface is consistent around the 12-month change, though a single robust structure is not proven. Its direction (procyclical) and zero lead are economically sensible and match the concurrent quartile evidence, but that coherence is not out-of-sample validation.
"""

_REFERENCES_MD = """
1. Institute for Supply Management, Manufacturing ISM Report On Business (PMI diffusion index).
2. Data Master, ISM Manufacturing PMI series (`NAPM`).
3. The Conference Board, Leading Economic Index (the ISM new-orders component is related).
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
        "Monthly sample from 1993-01-31 to 2025-10-31, with out-of-sample "
        "window 2017-09-30 to 2025-10-31 (98 months). SPY history limits the "
        "usable sample even though the PMI begins earlier."
    ),
    plain_english=(
        "This page documents how the ISM Manufacturing PMI was turned into "
        "stationary signals (the level itself is usable, being a bounded, "
        "mean-reverting diffusion index), how the econometric checks were run, "
        "and how the tournament selected the final SPY allocation rule -- along "
        "with the honest caveat that the selection maximum is a concurrent "
        "(zero-lead) year-over-year rule whose direction is sensible but whose "
        "edge is drawdown reduction, low-turnover, and not yet validated."
    ),
)
