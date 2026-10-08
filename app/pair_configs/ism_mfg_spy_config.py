"""ISM Manufacturing PMI x SPY pair configuration (Rule APP-PT1).

MONTHLY business-cycle pair. The ISM Manufacturing PMI (Data Master NAPM; the
Institute for Supply Management's manufacturing diffusion index) is a classic
LEADING indicator whose economic PRIOR is PROCYCLICAL: readings above ~50 mark
expansion and risk-on conditions, below 50 mark contraction. Unlike a
nominal-dollar level, the PMI is a BOUNDED, MEAN-REVERTING diffusion index --
it is LEVEL-STATIONARY (ADF rejects a unit root, p ~ 3.8e-5; KPSS does not
reject stationarity), so the level can be used directly. The tested signals are
the PMI level, its one-month change (diff_1m), its 12-month change (chg_12m),
and a 60-month z-score -- NOT growth/YoY transforms.

RE-RUN NOTE (Step C #255, publication-lag floor). The lead grid was FLOORED and
SHIFTED to L1-L13 months -- the concurrent, look-ahead L0 lead was removed so no
signal can be read at or before the month it allocates -- and the tournament was
re-run. The winner CHANGED. The prior run's winner (`chg_12m / T0_zero /
PROCYCLICAL / L0 concurrent`, OOS Sharpe 1.44) is replaced by `diff_1m /
T_roll_p50 / COUNTERCYCLICAL / L4` at OOS Sharpe 1.51. The story has FLIPPED
from a procyclical, same-month level filter to a COUNTERCYCLICAL (contrarian)
momentum filter read at a 4-month lead.

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/ism_mfg_spy/*:
  - The tournament winner (`diff_1m` one-month PMI change / `T_roll_p50` rolling
    60-month median threshold, rule "lte", latest median value -0.25 /
    COUNTERCYCLICAL / L4 months / P1_long_cash; OOS Sharpe 1.51 vs 0.95 B&H) is
    the grid maximum over 312 combinations (all 312 valid). The MEDIAN valid
    combo scores 0.68 -- it UNDERPERFORMS buy-and-hold (0.95)
    (winner_summary.json).
  - DIRECTION CONTRADICTS THE PRIOR (flag this, it is a caution not a selling
    point). The PMI's naive prior is procyclical, but the search selected a
    COUNTERCYCLICAL rule: hold SPY when the PMI's one-month change four months
    earlier was AT OR BELOW its rolling median (i.e. when manufacturing momentum
    was WEAK/falling), the OPPOSITE of "ride equity while the factory is
    accelerating". `interpretation_metadata.json` records expected_direction
    procyclical, observed_direction countercyclical, direction_consistent =
    false, confidence = low.
  - THE CONCURRENT LEVEL EVIDENCE IS STILL PROCYCLICAL -- and therefore does NOT
    match the traded winner. Sorting months by PMI LEVEL, the weakest-PMI
    quartiles Q1 and Q2 have the lower concurrent SPY Sharpe (0.44 and 0.43) and
    the strong-PMI quartiles Q3 and Q4 the higher (1.56 and 0.95) -- broadly
    procyclical, though not perfectly monotonic (Q3, not Q4, is the peak)
    (regime_quartile_returns.csv). But that is a CONCURRENT LEVEL relationship;
    the winner trades the 4-month-lagged one-month CHANGE in a COUNTERCYCLICAL
    direction, so the quartile picture and the winner's sign point opposite ways
    -- do not present them as mutually confirming.
  - NOT A FORECAST IN THE FORMAL TESTS EITHER. PMI changes do NOT Granger-cause
    SPY at any tested lag (minimum p = 0.31 at lag 2) (granger_by_lag.csv).
    Forward-return correlations are near zero and none is significant at any
    horizon (largest |r| ~ 0.07, diff_1m vs 6-month-forward SPY, p = 0.15 -- and
    that weak correlation is POSITIVE, the procyclical sign, i.e. the opposite
    of what the countercyclical winner trades) (core_models_20261008/
    correlations.csv). Local projections are null at every horizon (no
    coefficient significant; trivial R^2) (local_projections.csv). Pre-whitened
    cross-correlation is significant ONLY at NEGATIVE lags (SPY tends to move
    BEFORE the PMI); the concurrent (lag 0) bar and every lead-side
    (PMI-leads-SPY) bar -- INCLUDING the winner's +4 offset -- sit inside the
    confidence band (ccf_prewhitened.csv). The 4-month lead is a
    search-surface maximum, not a formally significant forecasting horizon.
  - The defensible virtue is RISK-ADJUSTED and DRAWDOWN behaviour in the
    searched sample: OOS max drawdown -8.9% vs -23.9% for buy-and-hold, lower
    volatility (10.5%), and -- unusually -- a HIGHER annualized return than B&H
    (16.4% vs 15.1%). But the win rate is BELOW 50% (39.8%): the rule wins by
    sidestepping large losses, not by being right most months.
  - TURNOVER IS MODERATE. The one-month change crossing a rolling median is a
    faster signal than a year-over-year filter: annual turnover 6.1, 50 OOS
    trades. Transaction costs (assumed 5 bps) are a more material (though still
    modest) drag than for a slow filter, and a fast monthly filter can whipsaw.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - This is ISM MANUFACTURING, distinct from the separate ISM Services pair.
    PMI is survey-based (diffusion of respondents reporting improvement),
    lightly revised via seasonal-factor updates; the COVID 2020 collapse and
    violent rebound is an extreme in-window episode that can dominate the fit.

MONTHLY conventions: leads in MONTHS (grid L1-L13, winner L4); Sharpe annualized
by sqrt(12); OOS window 2017-09-30 -> 2025-10-31 (98 months). Numbers sourced
from results/ism_mfg_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20261008/*, regime_quartile_returns.csv,
subperiod_sharpe.csv, granger_by_lag.csv, stationarity_tests_20261008.csv,
structural_break_ism_mfg_spy.json, tournament_results_20261008.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: ISM Manufacturing PMI as a Countercyclical SPY Overlay"
    PAGE_SUBTITLE = (
        "ISM Manufacturing PMI (Data Master NAPM diffusion index) x "
        "S&P 500 (SPY), monthly business-cycle signals tested against SPY "
        "returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.51 OOS vs 0.95 buy-and-hold, with a shallower drawdown "
        "(-8.9% vs -23.9%) AND a higher return (16.4% vs 15.1%) -- but the "
        "winning rule runs COUNTERCYCLICAL (buy SPY after WEAK factory "
        "momentum), the OPPOSITE of the procyclical prior, and it is "
        "search-found, not validated"
    )

    PLAIN_ENGLISH = (
        "The ISM Manufacturing PMI is a monthly survey diffusion index: a "
        "reading above 50 means more factory managers report conditions "
        "improving than worsening (expansion), below 50 means the reverse "
        "(contraction). It is a classic LEADING indicator of the business "
        "cycle, and the naive prior is procyclical: a firm or rising PMI is "
        "risk-on for equities. This pair tests whether the PMI can improve SPY "
        "timing. The search's best rule, however, runs the OTHER way: it holds "
        "SPY when the PMI's one-month change FOUR MONTHS EARLIER was at or below "
        "its rolling median -- that is, when factory momentum was weak or "
        "falling -- and holds cash otherwise. Weak momentum predicting BETTER "
        "forward SPY is a CONTRARIAN (countercyclical) reading, and it "
        "contradicts the simple procyclical prior, so treat it with caution. "
        "The economic story, if there is one, is that fading manufacturing "
        "momentum tends to precede policy accommodation and often marks a point "
        "near the cycle's trough, and the four-month lead gives that dynamic "
        "time to play into equities. But read it honestly as a search-found "
        "candidate: the formal lead-lag tests find no predictive edge, the win "
        "rate is below 50%, and the rule trades a few times a year."
    )

    WHERE_THIS_FITS = (
        "This is a contrarian business-cycle overlay for broad U.S. equities. "
        "It belongs in the portal as a search-found candidate whose edge in the "
        "sample was risk reduction -- a shallower worst-case loss and lower "
        "volatility -- while also, unusually, beating buy-and-hold's return. "
        "Readers should treat it as 'lean back INTO equity after factory "
        "momentum has weakened', the reverse of the naive procyclical instinct, "
        "and should weigh that the direction contradicts the economic prior, the "
        "signal shows no formal forecasting power, and the rule has not passed a "
        "frozen-rule holdout."
    )

    ONE_SENTENCE_THESIS = (
        "The search's best rule is CONTRARIAN -- it holds SPY when the ISM PMI's "
        "one-month change four months earlier was AT OR BELOW its rolling median "
        "(weak/falling factory momentum) -- earning OOS Sharpe 1.51 vs 0.95 for "
        "buy-and-hold with a shallower drawdown (-8.9% vs -23.9%) and a higher "
        "return (16.4% vs 15.1%), but this COUNTERCYCLICAL direction contradicts "
        "the procyclical prior AND the procyclical concurrent level quartiles "
        "(Q3 1.56 vs Q1 0.44), the formal lead-lag tests are null (Granger min "
        "p = 0.31, local projections flat, the 4-month lead sits inside the CCF "
        "band), the win rate is below 50% (39.8% -- it wins by avoiding losses, "
        "not by being right often), and the winner is found-in-search, not "
        "validated."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-09-30 -> 2025-10-31). The winner was found "
        "as the best of 312 valid combinations, and the MEDIAN valid combo "
        "(0.68) UNDERPERFORMS buy-and-hold (0.95) -- the typical rule subtracts "
        "value. In the searched sample the winner beats B&H on Sharpe (1.51 vs "
        "0.95), on return (16.4% vs 15.1%) and on max drawdown (-8.9% vs "
        "-23.9%) at lower volatility (10.5%) -- but the win rate is BELOW 50% "
        "(39.8%): it wins by sidestepping losses, not by being right most "
        "months. Turnover is moderate (6.1/yr, 50 trades), so costs are a "
        "modest drag. Sharpe ratios use monthly sqrt(12) annualization."
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
        "its one-month CHANGE (whether the PMI rose or fell versus the prior "
        "month), read with a four-month lead."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by PMI Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest PMI) to Q4 "
        "(strongest), with concurrent SPY Sharpe in each. It is broadly "
        "PROCYCLICAL -- the two weakest-PMI quartiles (Q1 0.44, Q2 0.43) trail "
        "the two strongest (Q3 1.56, Q4 0.95), though the pattern is not "
        "perfectly monotonic (Q3, not Q4, is the peak). Note the TENSION: this "
        "is a concurrent LEVEL relationship and it is procyclical, whereas the "
        "traded winner keys off the 4-month-lagged one-month CHANGE in a "
        "COUNTERCYCLICAL direction -- so the quartiles and the winner point "
        "opposite ways. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **countercyclical, contrarian PMI-momentum filter**. It holds SPY when the one-month change in the ISM Manufacturing PMI, taken **four months earlier**, is at or below its rolling 60-month median (i.e. when factory momentum was weak or falling), and holds cash otherwise. Out-of-sample (2017-09 to 2025-10), this rule earns a Sharpe of 1.51 versus 0.95 for buy-and-hold, with a maximum drawdown of **-8.9% versus -23.9%**, lower volatility (10.5%), and -- unusually -- a slightly **higher** annualized return (16.4% versus 15.1%). The honest caution is the direction: the rule runs **against** the naive procyclical prior, it buys equity *after* manufacturing momentum has faded. Its win rate is **below 50%** (39.8%) -- it earns its keep by avoiding large losses, not by being right most months -- and because it keys off a one-month change it trades a few times a year (turnover 6.1/yr, 50 OOS trades), so costs are a modest but non-trivial drag.

### The Business-Cycle Hypothesis -- and Why the Winner Inverts It

The ISM Manufacturing PMI is a monthly diffusion index built from a survey of purchasing managers -- the share reporting improving conditions, netted against those reporting deterioration. Above 50 signals expansion, below 50 contraction. Because purchasing managers see order books and supplier deliveries early, the PMI is a **leading** indicator, and the naive prior is **procyclical**: a firm or rising PMI is risk-on for equities. The concurrent *level* evidence agrees: sort months by PMI level and the weak-PMI quartiles have the lower concurrent SPY Sharpe (0.44, 0.43), while the strong-PMI quartiles have the higher (1.56, 0.95).

The tournament's winning rule runs the **opposite** way. It does not trade the level, and it does not go long into strength -- it goes long SPY *after* the one-month PMI change was weak four months earlier. A plausible economic reading is contrarian: fading factory momentum tends to precede policy accommodation and often marks a point near the cycle's trough, so a four-month lead lets that dynamic feed through to equities. That is defensible, but it **contradicts** both the simple prior and the procyclical concurrent quartiles -- flag it as a caution, not a confirmation.

### Why This Is Not a Validated Forecast

The sign is contrarian, but the formal timing evidence is simply absent. The PMI change does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.31), forward-return correlations are near zero at every horizon (none significant, and the largest is positive -- the *procyclical* sign, opposite to what the winner trades), and local projections are essentially null. The pre-whitened cross-correlation is significant only at *negative* lags -- SPY tends to move *before* the PMI -- while the concurrent bar and every lead-side offset, **including the winner's four-month lead**, sit inside the confidence band. So the four-month lead is a selection maximum over the search grid, not a horizon with demonstrated forecasting content. This dashboard therefore treats the pair as a search-found contrarian overlay whose sampled value was risk-adjusted, not a proven early-warning signal.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "The PMI slid below 50 as the tech-capex bust hit "
                "manufacturing. Through the bear the contrarian rule lost LESS "
                "in level than buy-and-hold (subperiod return -22.4% vs -33.4%) "
                "though at a similar risk-adjusted Sharpe (-0.70 vs -0.70)."
            ),
            "caption": "Dot-Com: PMI fell below 50; the contrarian rule lost less in level than SPY (-22.4% vs -33.4%).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The PMI collapsed into the low 30s through 2008-09 as the "
                "goods economy seized up. The contrarian momentum rule came "
                "through with a far better Sharpe (-0.54 vs -1.03) and a much "
                "smaller loss (-14.4% vs -35.5%) than buy-and-hold."
            ),
            "caption": "GFC: PMI collapsed 2008-09; the rule lost far less than SPY (-14.4% vs -35.5%).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The PMI plunged in spring 2020 and rebounded violently. The "
                "rule stepped to cash at end-February 2020 (ahead of the "
                "collapse) and bought back at end-April, and this is its best "
                "subperiod (Sharpe +1.81 vs -0.08; return +14.7% vs -3.2%). "
                "Read it with caution: it is one extreme, exogenous episode that "
                "can dominate the backtest fit."
            ),
            "caption": "COVID: the rule was in cash into the collapse and re-entered on the rebound -- its best, but a single outlier episode.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "The PMI ground lower through 2022 toward 50 as rate hikes bit. "
                "The contrarian rule was net positive across the window "
                "(Sharpe +0.62 vs -0.76; return +10.1% vs -18.2%), sidestepping "
                "much of SPY's rate-hike bear."
            ),
            "caption": "2022: PMI fell through the rate-hike bear; the rule was net positive (+10.1%) while SPY lost -18.2%.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show how the contrarian rule navigated sustained downturns. The PMI fell below 50 into the Dot-Com, GFC and COVID recessions, and below its rolling norm through the 2022 rate-hike bear -- and in each the rule came through with a better outcome than buy-and-hold: it lost less in level in the Dot-Com bear, lost far less in the GFC (-14.4% vs -35.5%), was strongly net positive through COVID (+14.7% vs -3.2%, stepping to cash into the February 2020 collapse and re-entering on the rebound), and was positive through the 2022 bear (+10.1% vs -18.2%). Because it buys SPY *after* factory momentum has already weakened, it tends to be positioned defensively going into trouble and to lean back in near troughs -- which is where its drawdown advantage was earned. The honest reading is not "the PMI predicts drawdowns"; it is that a contrarian momentum filter, read at a four-month lead, happened to sit on the right side of several sampled downturns -- a pattern that is search-found and contradicts the procyclical prior, not a validated forecast. A one-month-change signal is also faster and can whipsaw, and COVID is a single episode that flatters the fit.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this business-cycle story survives "
        "correlation, lead-lag, regime, and strategy checks. The direction is "
        "the awkward part -- the concurrent evidence is procyclical while the "
        "winner is countercyclical -- and the forecast does not survive at all: "
        "the formal lead-lag tests are null, so the value is a search-found, "
        "risk-adjusted overlay, not a proven predictor."
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
        "6-month-forward SPY return (r = 0.07, p = 0.15), a weak POSITIVE "
        "(procyclical) association -- the opposite sign to the countercyclical "
        "winner, and insignificant in any case -- so this is not a usable "
        "forecasting signal in either direction."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; "
        "all |r| values are below ~0.07 and every p-value exceeds 0.14, so no "
        "cell is significant. What little sign there is (positive for diff_1m) "
        "runs opposite to the winner's countercyclical rule."
    ),
    interpretation=(
        "Correlation alone does not support forecasting the pair, and the faint "
        "positive tilt it does show disagrees with the winner's direction. The "
        "winner's edge, such as it is, comes from the threshold/lead "
        "combination in the backtest, not from a linear forward correlation."
    ),
    key_message="The PMI is not a linear SPY predictor at any tradeable horizon, and the faint positive tilt runs opposite to the winner.",
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
        "This rules out a forecasting claim, including at the winner's "
        "four-month lead. The strategy must be framed as a search-found "
        "contrarian overlay, not proof that the PMI causes future SPY returns."
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
        "pattern is not perfectly monotonic (Q3 is the peak). This is a "
        "concurrent LEVEL relationship -- and it runs OPPOSITE to the winner, "
        "which is a countercyclical filter on the lagged one-month change."
    ),
    observation=(
        "Concurrent SPY Sharpe is higher in the strong-PMI quartiles "
        "(Q1 0.44, Q2 0.43, Q3 1.56, Q4 0.95) -- a firmer PMI level broadly "
        "coincides with better equity conditions, though not monotonically."
    ),
    interpretation=(
        "The concurrent level pattern is procyclical, matching the economic "
        "prior -- but it therefore DISAGREES with the winner, which is a "
        "countercyclical momentum rule at a lead. Treat the quartiles as "
        "descriptive context, not confirmation of the traded rule."
    ),
    key_message="A firmer PMI level broadly coincides with better SPY conditions (procyclical) -- opposite to the countercyclical winner.",
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
        "and every lead-side (PMI-leads-SPY) bar, INCLUDING the winner's +4 "
        "offset, is inside the band. That is the reverse of a forecasting "
        "signal."
    ),
    observation=(
        "Correlations are significant only at lags -6 to -1 (SPY leading the "
        "PMI, ccf up to ~0.17); the concurrent bar (lag 0, ~0.06) and every "
        "positive lead-side offset -- including lag +4 (~0.01) -- are inside "
        "the confidence band and insignificant."
    ),
    interpretation=(
        "There is no window in which the PMI change foreshadows SPY, and the "
        "winner's four-month lead has no significant correlation. If anything "
        "the market anticipates the PMI, so the winner's lead is a selection "
        "maximum rather than an identified forecasting horizon."
    ),
    key_message="Significant correlation is on the SPY-leads side; the PMI shows no significant lead over SPY, not even at the winner's 4-month offset.",
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
    "title": "The Evidence: The PMI Is Business-Cycle Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a search-found contrarian overlay -- and "
        "nothing stronger. The strategy winner improves search-phase OOS "
        "Sharpe, but its COUNTERCYCLICAL direction contradicts the procyclical "
        "prior AND the procyclical concurrent quartiles, and formal lead-lag "
        "evidence is absent (Granger min p = 0.31; local projections null; CCF "
        "significant only on the SPY-leads side, with the winner's 4-month lead "
        "inside the band). The lead is a selection maximum, not a forecast "
        "horizon."
    ),
    "plain_english": (
        "This page asks whether the PMI helps time SPY. The answer is: not in "
        "the formal tests. Concurrent quartiles are broadly procyclical (weak "
        "PMI level = worse same-month market), but the winning rule runs the "
        "opposite way (it buys after weak momentum), the causal tests find no "
        "lead, and the winner's 4-month lead has no significant correlation. "
        "Treat it as a search-found contrarian overlay, not an early-warning "
        "system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 312 strategy combinations (all 312 valid) "
        "across four PMI signals (level, one-month change, 12-month change, "
        "60-month z-score), fixed and rolling thresholds, a long/cash strategy, "
        "and leads from 1 to 13 months (the publication-lag floor removed the "
        "look-ahead L0 lead). The selected winner is `diff_1m / T_roll_p50 / "
        "P1_long_cash countercyclical / L4`, with OOS Sharpe 1.51. The MEDIAN "
        "valid combo scores 0.68 -- below buy-and-hold's 0.95 -- and the "
        "runner-up (`chg_12m / T_roll_p50 / L1`, 1.41) is a different signal "
        "and lead, so the top of the search surface is NOT a single robust "
        "structure. Read the winner as a selection maximum, not a validated "
        "edge."
    ),
    "transition": (
        "**Transition:** the evidence is business-cycle context, not causation "
        "ahead of the market, and the winner's direction contradicts the "
        "procyclical prior. The Strategy page shows the exact long/cash rule, "
        "the drawdown advantage that is its real virtue, the moderate-turnover "
        "cost profile, and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Countercyclical, Lagged PMI-Momentum Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the one-month change in the ISM "
        "Manufacturing PMI, a rolling-median threshold, a countercyclical "
        "(contrarian) orientation, and a four-month lead -- valued for "
        "risk-adjusted and drawdown behaviour, and flagged as contradicting the "
        "procyclical prior, showing no formal forecasting power, and trading at "
        "moderate turnover."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the one-month change in the ISM Manufacturing "
        "PMI, taken four months earlier, is at or below its rolling 60-month "
        "median (factory momentum was weak or falling); otherwise it holds "
        "cash. This is a COUNTERCYCLICAL (contrarian) momentum filter -- it "
        "buys equity AFTER momentum has faded, the OPPOSITE of the naive "
        "procyclical instinct -- read at a four-month lead. Judge it by its "
        "shallower drawdown (-8.9% vs -23.9%), lower volatility, and sampled "
        "Sharpe/return edge (1.51 vs 0.95; 16.4% vs 15.1%), but weigh that the "
        "direction contradicts the prior, the win rate is below 50%, and the "
        "rule is search-found, not validated."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/ism_mfg_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/ism_mfg_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/ism_mfg_spy/tournament_results_20261008.csv"},
        {"label": "Stationarity tests", "path": "results/ism_mfg_spy/stationarity_tests_20261008.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the one-month change in the ISM Manufacturing PMI, taken **four months earlier**, is at or below its rolling 60-month median (i.e. when factory momentum was weak or falling); otherwise hold cash. This is a **countercyclical** rule -- it buys equity *after* momentum fades, the OPPOSITE of the procyclical prior. It uses a **four-month lead** -- the PMI change from four months ago sets the current allocation.

If-then form:
- **IF** the one-month PMI change `ism_diff_1m` from four months ago is at or below its rolling 60-month median (latest median -0.25 index points) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-09-30 to 2025-10-31, 98 months): Sharpe 1.51 versus 0.95 buy-and-hold; annualized return 16.4% versus 15.1%; **maximum drawdown -8.9% versus -23.9%**; annualized volatility 10.5%; win rate 39.8%; 50 trades; annual turnover 6.1 (moderate). The drawdown and volatility reduction -- alongside a modest return edge -- is the defensible result; the win rate below 50% means the rule wins by avoiding losses, not by being right most months.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the ISM Manufacturing PMI (`NAPM`, diffusion index) at month-end. Second, it computes the one-month change in the PMI (`ism_diff_1m`), this month's level minus last month's. Third, a four-month lead (L4) is applied: the change observed four months ago sets the current allocation (the publication-lag floor removed the look-ahead concurrent lead). Finally, the lagged change is compared with its rolling 60-month median: when the change is at or BELOW the median, hold SPY; otherwise cash (the countercyclical orientation -- buy after weak momentum).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year (moderate here -- the one-month change crosses its rolling median a few times a year). Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the ISM Manufacturing PMI (NAPM) at month end.
2. Compute the one-month change (this month's PMI minus last month's).
3. Take the change from FOUR months ago and compare it with its rolling 60-month median.
4. Hold SPY when that lagged change is at or below the median (momentum was weak); otherwise hold cash.
5. Recheck monthly. Turnover is moderate (6.1/yr, 50 OOS trades): the one-month change crosses its rolling median a few times a year, so transaction costs are a modest consideration.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The defense is consistent: the rule lost "
        "less in level in the Dot-Com bear (return -22.4% vs -33.4%, Sharpe "
        "-0.70 vs -0.70), had a far better GFC (-0.54 vs -1.03), was positive "
        "through the 2022 rate shock (+0.62 vs -0.76), and was strongly "
        "positive through COVID (+1.81 vs -0.08, a single striking episode). "
        "The contrarian momentum rule tended to be positioned defensively into "
        "sustained downturns."
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
            "(here the max absolute rolling-correlation z-score reaches 2.7)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.51) is a right-tail maximum at a "
        "four-month lead; the median valid combo (0.68) sits BELOW buy-and-hold "
        "(0.95), so the typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The winner's direction CONTRADICTS the economic prior. The PMI's naive prior is procyclical, but the winner is COUNTERCYCLICAL (it buys SPY after weak factory momentum) -- and it even disagrees with the procyclical concurrent level quartiles. Treat the direction as a caution, not a feature.
2. It is NOT a forecast in the formal tests. Granger causality is insignificant at every lag (min p = 0.31), local projections are null, and the pre-whitened CCF is significant only on the SPY-leads side -- the winner's four-month lead sits inside the confidence band. The lead is a selection maximum, not an identified forecasting horizon.
3. The result is marked `found_in_search`; the median valid combo (0.68) underperforms buy-and-hold (0.95), the runner-up is a different signal/lead (so the search surface is not a single robust structure), and the winner still needs a frozen-rule holdout confirmation. Confidence is LOW.
4. The win rate is BELOW 50% (39.8%): the rule wins by avoiding large losses, not by being right most months.
5. Turnover is MODERATE (6.1/yr, 50 OOS trades). A one-month-change filter is faster than a year-over-year signal, so transaction costs at the assumed 5 bps per trade are a more material (though still modest) drag, and a fast filter can whipsaw.
6. COVID 2020 is an extreme in-window episode that drives the winner's best subperiod and can dominate the fit; the PMI is survey-based and lightly revised via seasonal-factor updates.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged one-month PMI change fell to at or below its "
        "rolling median (factory momentum weak), taking exposure from 0% to "
        "100% SPY. A SELL moves back to cash when the lagged change rose above "
        "the median. Because the one-month change crosses its median a few "
        "times a year, the log has a moderate number of round-trips (50 OOS "
        "trades)."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1995-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: diff_1m countercyclical rule crossed T_roll_p50; position 0% to 100%",
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
    "`ism_diff_1m`, the one-month change in the PMI, used with a four-month "
    "lead, a rolling 60-month median threshold (rule 'lte'; latest median "
    "-0.25), and a COUNTERCYCLICAL orientation (long SPY when the lagged "
    "one-month change is at or below the rolling median -- i.e. after factory "
    "momentum has weakened). This direction contradicts the procyclical prior "
    "and is flagged as a search-found caution."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the PMI move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong PMI regimes behave differently? | Makes the business-cycle context interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past PMI information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: four PMI signals (level, one-month change, 12-month change, 60-month z-score) x fixed and rolling thresholds x a long/cash strategy x lead times (1-13 months; the publication-lag floor removed the look-ahead L0 concurrent lead). The final tournament has 312 combinations, all 312 valid. The winning rule is `ism_diff_1m / T_roll_p50 / P1_long_cash countercyclical / L4`, the maximum OOS Sharpe (1.51). The median valid combo (0.68) underperforms buy-and-hold (0.95), and the runner-up (`chg_12m / T_roll_p50 / L1`, 1.41) is a DIFFERENT signal and lead -- so the top of the surface is not a single robust structure. The winner's direction (countercyclical) contradicts both the procyclical prior and the procyclical concurrent quartile evidence, so there is no economic-coherence support for it; it is a selection maximum, not an out-of-sample validation.
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
        "with the honest caveat that the selection maximum is a COUNTERCYCLICAL "
        "(contrarian) one-month-change rule read at a four-month lead, whose "
        "direction contradicts the procyclical prior, whose forecasting power "
        "is absent in the formal tests, and whose edge is drawdown reduction "
        "and risk-adjusted behaviour, not yet validated."
    ),
)
