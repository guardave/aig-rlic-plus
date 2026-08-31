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

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/ism_mfg_spy/*:
  - The tournament winner (`diff_1m` one-month PMI change / T_roll_p50
    rolling-median / PROCYCLICAL / L0 months / P1_long_cash; OOS Sharpe 1.30
    vs 0.95 B&H) is the grid maximum over 168 combinations (all 168 valid).
    The MEDIAN valid combo scores 0.710 -- it UNDERPERFORMS buy-and-hold (0.95)
    (winner_summary.json).
  - DIRECTION IS CONSISTENT WITH THE PRIOR. The PMI is procyclical and the
    search selected a PROCYCLICAL rule (hold SPY when the one-month change in
    the PMI is at or above its 60-month rolling median, i.e. when momentum is
    not deteriorating). `interpretation_metadata.json` records
    expected_direction procyclical, observed_direction procyclical,
    direction_consistent = true, confidence = low.
  - CONSISTENT CONCURRENT EVIDENCE. Sorting months by PMI level, the
    weakest-PMI quartile Q1 has the worst concurrent SPY Sharpe (0.40) and the
    strongest-PMI quartile Q4 the best (1.45), rising monotonically
    (Q2 0.74, Q3 0.74) (regime_quartile_returns.csv). The sign of the winner
    agrees with this concurrent, procyclical reading -- a point in the pair's
    favor relative to the fleet's long-lead artifacts.
  - BUT NOT A FORECAST. The winner is CONCURRENT (L0), not predictive. PMI
    changes do NOT Granger-cause SPY at any tested lag (minimum p = 0.42 at
    lag 2) (granger_by_lag.csv). Forward-return correlations are near zero and
    none is significant at any horizon (largest |r| ~ 0.08, chg_12m vs
    3-month-forward SPY, p = 0.13) (core_models_20260831/correlations.csv).
    Local projections are null at every horizon (no coefficient significant;
    trivial R^2) (local_projections.csv). Pre-whitened cross-correlation is
    significant ONLY at zero and NEGATIVE lags (SPY tends to move BEFORE the
    PMI, plus a concurrent tie at lag 0) -- there is no significant lead-side
    (PMI-leads-SPY) bar (ccf_prewhitened.csv). Read the rule as a coincident
    risk-regime overlay, not an early-warning forecast.
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: OOS max drawdown
    -15.0% vs -23.9% for buy-and-hold, at a LOWER annual return (11.5% vs
    15.1%) and much lower volatility (8.7%) -- read the Sharpe (1.30 vs 0.95)
    as volatility avoidance, not a return advantage.
  - TURNOVER IS HIGH. The one-month change is a noisy momentum signal that
    flips often: annual turnover 6.73, 55 OOS trades. Transaction costs
    (assumed 5 bps) bite more here than for a slow filter -- a real caveat.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - This is ISM MANUFACTURING, distinct from the separate ISM Services pair.
    PMI is survey-based (diffusion of respondents reporting improvement),
    lightly revised via seasonal-factor updates; the COVID 2020 collapse and
    violent rebound is an extreme in-window episode that can dominate the fit.

MONTHLY conventions: leads in MONTHS (winner L0); Sharpe annualized by
sqrt(12); OOS window 2017-09-30 -> 2025-10-31 (98 months). Numbers sourced from
results/ism_mfg_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20260831/*, regime_quartile_returns.csv,
subperiod_sharpe.csv, granger_by_lag.csv, stationarity_tests_20260831.csv,
structural_break_ism_mfg_spy.json, tournament_results_20260831.csv).
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
        "## Sharpe 1.30 OOS vs 0.95 buy-and-hold, and the direction is the "
        "RIGHT way round for once (procyclical) -- but the honest headline is "
        "drawdown control (-15.0% vs -23.9%) at a LOWER return, and the rule "
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
        "search's best rule keys off the one-month CHANGE in the PMI and runs "
        "the economically sensible way (hold equity when momentum is not "
        "deteriorating). But read it as a same-month risk-regime overlay and "
        "drawdown control, not a forecast: the formal lead-lag tests find no "
        "predictive edge, the rule is concurrent (zero lead), and it trades "
        "often."
    )

    WHERE_THIS_FITS = (
        "This is a business-cycle overlay for broad U.S. equities. It belongs "
        "in the portal as a coincident risk-regime signal: useful for drawdown "
        "control in the searched sample, with a direction that matches both "
        "the economic prior and the concurrent evidence -- but it is not a "
        "standalone forecast, and it does not lead the market. Readers should "
        "treat it as 'ride equity while the factory cycle is firming, step "
        "aside when momentum rolls over', judged on risk reduction rather than "
        "on beating buy-and-hold's return."
    )

    ONE_SENTENCE_THESIS = (
        "The PMI is procyclical with equities CONCURRENTLY (weakest-PMI "
        "quartile has the worst SPY Sharpe, 0.40; strongest 1.45) and the "
        "search's best rule agrees in sign, but the PMI does NOT lead SPY -- "
        "Granger is insignificant at every lag (min p = 0.42) and local "
        "projections are null -- so the winner, a procyclical one-month-change "
        "filter at ZERO lead, is a coincident drawdown-reduction candidate "
        "(-15.0% vs -23.9% max drawdown) at a LOWER return (11.5% vs 15.1%) "
        "and high turnover, found in search and not yet validated."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-09-30 -> 2025-10-31). The winner was found "
        "as the best of 168 valid combinations, and the MEDIAN valid combo "
        "(0.710) UNDERPERFORMS buy-and-hold (0.95) -- the typical rule "
        "subtracts value. The defensible number is the max drawdown (-15.0% vs "
        "-23.9%) at a LOWER return (11.5% vs 15.1%) and much lower volatility "
        "(8.7%) -- read the Sharpe (1.30 vs 0.95) as volatility avoidance, not "
        "stock-picking skill. Turnover is high (6.73/yr, 55 trades), so costs "
        "matter. Sharpe ratios use monthly sqrt(12) annualization."
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
        "its one-month change."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by PMI Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest PMI) to Q4 "
        "(strongest), with concurrent SPY Sharpe in each. It is cleanly "
        "PROCYCLICAL -- the weakest-PMI quartile Q1 is the worst (Sharpe 0.40) "
        "and the strongest Q4 the best (1.45), rising monotonically "
        "(Q2 0.74, Q3 0.74). This matches the economic prior AND the sign of "
        "the tournament winner. Descriptive and concurrent, not a tradable "
        "lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical, concurrent PMI-momentum filter**. It holds SPY when the one-month change in the ISM Manufacturing PMI is at or above its five-year rolling median (i.e. when factory-cycle momentum is not deteriorating), and holds cash otherwise -- with **zero lead**. Out-of-sample (2017-09 to 2025-10), this rule earns a Sharpe of 1.30 versus 0.95 for buy-and-hold, with a maximum drawdown of **-15.0% versus -23.9%** at an annualized return of 11.5% versus 15.1%. Read that as the honest headline: the rule's edge is a shallower worst-case loss and lower volatility (8.7%), **not** a return advantage. It also trades often (turnover 6.73/yr, 55 OOS trades), so transaction costs matter.

### The Business-Cycle Hypothesis

The ISM Manufacturing PMI is a monthly diffusion index built from a survey of purchasing managers -- the share reporting improving conditions, netted against those reporting deterioration. Above 50 signals expansion, below 50 contraction. Because purchasing managers see order books and supplier deliveries early, the PMI is a **leading** indicator of the business cycle, and the economic prior is **procyclical**: a firm or rising PMI is risk-on for equities; a falling PMI warns that demand is cooling.

The concurrent evidence supports that prior cleanly: sort months by PMI level and the weakest-PMI quartile has the worst concurrent SPY Sharpe (0.40), rising monotonically to the strongest quartile (1.45). The tournament's winning rule runs the **same** way -- it holds SPY when PMI momentum is firm -- so unlike several other pairs in the fleet, the direction here is economically sensible and internally consistent.

### Why This Is Still Not a Forecast

The sign is right, but the timing is coincident, not predictive. The formal lead-lag tests are blunt: the PMI change does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.42), forward-return correlations are near zero at every horizon (none significant), and local projections are essentially null. The pre-whitened cross-correlation is significant only at zero and *negative* lags -- SPY tends to move *before* the PMI, with a concurrent tie -- and shows no significant lead-side bar. So the winner earns its keep by riding the *current* risk regime, not by seeing ahead. This dashboard therefore treats the pair as a coincident business-cycle overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "The PMI slid below 50 as the tech-capex bust hit "
                "manufacturing. The searched rule did NOT protect here -- its "
                "subperiod Sharpe (-1.65) was worse than buy-and-hold (-0.70), "
                "as choppy month-to-month PMI changes whipsawed the momentum "
                "filter."
            ),
            "caption": "Dot-Com: PMI fell below 50; the change-based rule whipsawed and did worse than SPY.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The PMI collapsed into the low 30s through 2008-09 as the "
                "goods economy seized up. Here the rule lost LESS than "
                "buy-and-hold (Sharpe -0.56 vs -1.03), part of its drawdown "
                "story -- the deteriorating momentum kept it in cash for "
                "stretches of the decline."
            ),
            "caption": "GFC: PMI collapsed 2008-09; the rule lost less than SPY.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The PMI plunged in spring 2020 and rebounded violently. The "
                "one-month-change signal stepped to cash on the collapse and "
                "re-entered on the sharp rebound, and this single episode is "
                "the rule's best subperiod (Sharpe +2.18 vs -0.08). Read it "
                "with caution: it is one extreme, exogenous episode that can "
                "dominate the backtest fit."
            ),
            "caption": "COVID: the change signal dodged the collapse and caught the rebound -- one outlier episode.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "The PMI ground lower through 2022 toward 50 as rate hikes bit, "
                "but the descent was gradual and choppy. The momentum filter "
                "flipped in and out and did WORSE than buy-and-hold (Sharpe "
                "-1.40 vs -0.76) -- a grinding, whipsaw-prone bear is the rule's "
                "weakest environment."
            ),
            "caption": "2022: a slow, choppy PMI decline whipsawed the rule; it underperformed SPY.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is procyclical but works only concurrently and unevenly. The PMI fell below 50 into the Dot-Com, GFC and COVID recessions -- but the change-based rule's protection was mixed: it did worse than buy-and-hold in the Dot-Com bear and the 2022 grind (choppy PMI changes whipsawed it), lost less in the GFC, and stepped aside then re-entered profitably through COVID. In 2022 the PMI descent was gradual, exactly when a sharp momentum signal is least helpful. The strongest honest reading is not "the PMI predicts drawdowns"; it is that a procyclical, same-month momentum filter tends to sit in cash while the factory cycle is deteriorating sharply, which is where its drawdown advantage was earned -- at the cost of whipsaws in slow declines and high turnover.
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
        "The largest cell anywhere is the 12-month PMI change vs the "
        "3-month-forward SPY return (r = 0.08, p = 0.13), a weak positive -- "
        "not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; "
        "all |r| values are below ~0.08 and every p-value exceeds 0.12, so no "
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
        "across the tested lags is 0.42 (lag 2) -- the PMI change does not "
        "Granger-cause SPY returns."
    ),
    observation=(
        "Across all tested monthly lags the PMI->SPY p-value never falls below "
        "0.42; the F-statistics are tiny. There is no formal evidence of "
        "lead-lag causality."
    ),
    interpretation=(
        "This rules out a forecasting claim. The strategy must be framed as a "
        "concurrent business-cycle overlay, not proof that the PMI causes "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.42); the PMI does not lead SPY.",
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
        "What this shows: cleanly PROCYCLICAL -- the weakest-PMI quartile Q1 "
        "has the worst concurrent SPY Sharpe (0.40) and the strongest Q4 the "
        "best (1.45), rising monotonically (Q2 0.74, Q3 0.74). This matches "
        "the winner's direction."
    ),
    observation=(
        "Concurrent SPY Sharpe rises monotonically across PMI quartiles "
        "(Q1 0.40, Q2 0.74, Q3 0.74, Q4 1.45) -- a firmer PMI coincides with "
        "better equity conditions."
    ),
    interpretation=(
        "The concurrent pattern fits a procyclical business-cycle story and "
        "agrees with the tournament winner's direction -- a coherence point "
        "in the pair's favor, though still concurrent rather than predictive."
    ),
    key_message="A firmer PMI coincides with better SPY conditions -- procyclical, matching the winner's direction.",
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
        "What this shows: the significant bars sit at zero and NEGATIVE lags "
        "-- SPY tends to move BEFORE the PMI, with a concurrent tie at lag 0 "
        "-- and there is no significant lead-side (PMI-leads-SPY) bar. That is "
        "the reverse of a forecasting signal."
    ),
    observation=(
        "Correlations are significant only at lags -4 to 0 (SPY leading the "
        "PMI, plus a concurrent bar, ccf up to ~0.25); every positive "
        "lead-side offset is inside the confidence band and insignificant."
    ),
    interpretation=(
        "There is no window in which the PMI change foreshadows SPY. If "
        "anything the market anticipates the PMI, which is why the winning "
        "rule is best used concurrently rather than as a forecast."
    ),
    key_message="Significant correlation is on the SPY-leads/concurrent side; the PMI shows no forecasting lead over SPY.",
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
        "(p from 0.13 to 0.42), with negligible R^2."
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
        "(Granger min p = 0.42; local projections null; CCF significant only "
        "on the SPY-leads/concurrent side). The winner's zero lead confirms "
        "the signal works same-month, not ahead of the market."
    ),
    "plain_english": (
        "This page asks whether the PMI helps time SPY. The answer is: same "
        "month, yes; ahead of time, no. Concurrent quartiles are cleanly "
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
        "winner is `diff_1m / T_roll_p50 / P1_long_cash procyclical / L0`, "
        "with OOS Sharpe 1.30. The MEDIAN valid combo scores 0.710 -- below "
        "buy-and-hold's 0.95 -- and the runner-up (`zscore_60m / T_z_0 / "
        "procyclical / L12`, 1.278) is a long-lead z-score rule, so the search "
        "surface is not dominated by a single robust structure. Read the "
        "winner as a selection maximum, not a validated edge."
    ),
    "transition": (
        "**Transition:** the evidence is procyclical context that works "
        "concurrently, not causation ahead of the market. The Strategy page "
        "shows the exact long/cash rule, the drawdown advantage that is its "
        "real virtue, the high-turnover cost caveat, and the deployment "
        "caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical, Concurrent PMI-Momentum Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the one-month change in the ISM "
        "Manufacturing PMI, a rolling-median threshold, a procyclical "
        "orientation, and zero lead -- valued for drawdown reduction, not for "
        "beating buy-and-hold's return, and flagged as concurrent (not "
        "predictive) and high-turnover."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the one-month change in the ISM Manufacturing "
        "PMI is at or above its five-year rolling median; otherwise it holds "
        "cash. This is a same-month, PROCYCLICAL momentum filter -- the "
        "direction the economic prior expects -- not a real-time recession "
        "forecast (it uses zero lead and does not lead the market). Judge it "
        "by its shallower drawdown (-15.0% vs -23.9%) and lower volatility, "
        "not by beating buy-and-hold on return (it does not: 11.5% vs 15.1%)."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/ism_mfg_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/ism_mfg_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/ism_mfg_spy/tournament_results_20260831.csv"},
        {"label": "Stationarity tests", "path": "results/ism_mfg_spy/stationarity_tests_20260831.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the one-month change in the ISM Manufacturing PMI is at or above its five-year rolling median (i.e. when factory-cycle momentum is firm or improving); otherwise hold cash. This is a procyclical rule and matches the economic prior. It uses **zero lead** -- the current month's PMI change sets the current allocation.

If-then form:
- **IF** the one-month PMI change `ism_diff_1m` is at or above its 60-month rolling median (about -0.25 index points) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-09-30 to 2025-10-31, 98 months): Sharpe 1.30 versus 0.95 buy-and-hold; annualized return 11.5% versus 15.1%; **maximum drawdown -15.0% versus -23.9%**; annualized volatility 8.7%; win rate 38.8%; 55 trades; annual turnover 6.73 (high). The drawdown and volatility reduction, not the Sharpe or return, is the defensible result -- and the high turnover means costs matter.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the ISM Manufacturing PMI (`NAPM`, diffusion index) at month-end. Second, it computes the one-month change in the PMI (`ism_diff_1m`), the level's month-on-month move. Third, no additional lag is applied (L0): the current-month change sets the current allocation. Finally, the change is compared with its 60-month rolling median: when the change is at or above that median, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year (high here -- the one-month change is a noisy signal that flips often). Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the ISM Manufacturing PMI (NAPM) at month end.
2. Compute the one-month change (this month's PMI minus last month's).
3. Compare that change with its trailing 60-month rolling median.
4. Hold SPY when the change is at or above the rolling median; otherwise hold cash.
5. Recheck monthly. Turnover is high (6.73/yr, 55 OOS trades): the change signal flips often, so account for transaction costs.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The defense is real but UNEVEN: the rule "
        "lost less in the GFC (-0.56 vs -1.03) and was strongly positive "
        "through COVID (+2.18 vs -0.08, a single striking episode), but did "
        "WORSE than buy-and-hold in the Dot-Com bear (-1.65 vs -0.70) and the "
        "2022 rate shock (-1.40 vs -0.76), where choppy PMI changes whipsawed "
        "the momentum filter."
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
        "combinations by lead. The winner (1.30) is a right-tail maximum at "
        "zero lead; the median valid combo (0.710) sits BELOW buy-and-hold "
        "(0.95), so the typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The winner is CONCURRENT (zero lead), not a forecast. Granger causality is insignificant at every lag (min p = 0.42), local projections are null, and the pre-whitened CCF is significant only on the SPY-leads/concurrent side -- so this rides the current risk regime rather than predicting it.
2. The result is marked `found_in_search`; the median valid combo (0.710) underperforms buy-and-hold (0.95), and the winner still needs a frozen-rule holdout confirmation. Confidence is LOW.
3. The defensible virtue is drawdown and volatility reduction, not return: annualized return (11.5%) is BELOW buy-and-hold (14.8-15.1%).
4. Turnover is HIGH (6.73/yr, 55 OOS trades). The one-month change is a noisy momentum signal that flips often; at the assumed 5 bps per trade, costs meaningfully erode the edge, and the stress defense is uneven (worse than SPY in the Dot-Com and 2022 bears).
5. The direction and concurrent evidence are coherent (procyclical, matching the prior and the quartiles) -- a point in the pair's favor -- but coherence is not validation.
6. COVID 2020 is an extreme in-window episode that drives the winner's best subperiod and can dominate the fit; the PMI is survey-based and lightly revised via seasonal-factor updates.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the one-month PMI change crossed at or above its rolling "
        "median, taking exposure from 0% to 100% SPY. A SELL moves back to "
        "cash when the change fell below the rolling median. Because the "
        "change flips often, the log has many round-trips (55 OOS trades)."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1995-01-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: diff_1m procyclical rule crossed T_roll_p50; position 0% to 100%",
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
    "`ism_diff_1m`, the one-month change in the PMI, used with zero lead, a "
    "60-month rolling-median threshold, and a procyclical orientation (long "
    "SPY when the change is at or above the median)."
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
Grid: four PMI signals (level, one-month change, 12-month change, 60-month z-score) x fixed and rolling thresholds x a procyclical long/cash strategy x lead times (0-12 months). The final tournament has 168 combinations, all 168 valid. The winning rule is `ism_diff_1m / T_roll_p50 / P1_long_cash procyclical / L0`, the maximum OOS Sharpe (1.30). The median valid combo (0.710) underperforms buy-and-hold (0.95), and the runner-up (`zscore_60m / T_z_0 / procyclical / L12`, 1.278) is a long-lead z-score rule -- read the winner as a selection maximum, not a validated edge. Its direction (procyclical) and zero lead are economically sensible and match the concurrent quartile evidence, but that coherence is not out-of-sample validation.
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
        "(zero-lead) momentum rule whose direction is sensible but whose edge "
        "is drawdown reduction, high-turnover, and not yet validated."
    ),
)
