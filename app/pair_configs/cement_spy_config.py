"""Portland Cement Shipments x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY construction-activity pair. Portland Cement Shipments
(nominal $, monthly; Data Master) is a LEADING, production-class indicator
whose economic PRIOR is PROCYCLICAL (firm/rising shipment growth -> risk-on).
The nominal-dollar LEVEL is non-stationary (ADF fails to reject a unit root,
p = 0.22; KPSS rejects stationarity), so every tested signal is a growth
transform (MoM/3m/6m/YoY %, YoY z-score, acceleration).

HONEST FRAMING (binding). This is a FOUND-IN-SEARCH candidate at LOW
confidence, not a validated or deployable edge. Every number below is sourced
from results/cement_spy/*:
  - The tournament winner (`chg_6m` 6-month growth / T_roll_p25 rolling-25th-
    percentile / PROCYCLICAL / L0 months / P1_long_cash; OOS Sharpe 1.197 vs
    0.935 buy-and-hold) is the grid maximum over 252 combinations (all 252
    valid). The MEDIAN valid combo scores 0.653 -- it UNDERPERFORMS buy-and-
    hold (0.935) (winner_summary.json). The typical rule built on this
    indicator subtracts value.
  - DIRECTION AGREES WITH THE PRIOR. Cement-shipment growth is procyclical and
    the search selected a PROCYCLICAL rule (hold SPY when 6-month growth is at
    or above its rolling 25th percentile -- i.e. when growth is firm), at a
    ZERO-month lead. `interpretation_metadata.json` records expected_direction
    procyclical, observed_direction procyclical, direction_consistent = true,
    confidence = low. This is the honest strength of the pair -- but a
    direction-consistent, single-sample search maximum is still not a validated
    edge.
  - IT IS A CONCURRENT REGIME FILTER, NOT A FORECAST. The winner sits at L0:
    it uses the LATEST 6-month cement growth to set exposure, so it makes no
    forward-lead claim. The formal lead-lag tests confirm there is no forecast
    to claim: cement growth does NOT Granger-cause SPY at any tested lag
    (minimum p = 0.14 at lag 2) (granger_by_lag.csv); forward-return
    correlations are near zero at every horizon (largest anywhere is
    acceleration vs 1-month-forward SPY, r = 0.12, p = 0.085 -- not significant)
    (core_models_20260830/correlations.csv); local projections are null at
    every horizon (no coefficient significant; trivial R^2)
    (local_projections.csv); and the pre-whitened cross-correlation has NO
    significant bar at any offset, lead or lag (ccf_prewhitened.csv).
  - The concurrent evidence is broadly procyclical: sorting months by cement
    YoY growth, the weakest-growth quartile Q1 has the worst concurrent SPY
    Sharpe (0.33) and the strongest quartile Q4 the best (1.12), with a
    non-monotonic middle (Q2 1.06, Q3 0.62) (regime_quartile_returns.csv).
  - The winner's edge over buy-and-hold is modest and mixed: OOS annualized
    return 15.3% vs 14.6%, OOS max drawdown -20.9% vs -23.9%, OOS volatility
    12.6%, win rate 54.9%. Turnover is HIGH (3.76/yr, 32 OOS trades): this is
    an active in/out rule, not a set-and-forget overlay. A stationary block
    bootstrap puts the winner's Sharpe at p = 0.004
    (tournament_validation_20260830/bootstrap.csv), but that is an in-sample
    significance check, not out-of-sample validation.
  - Stress behavior is uneven. The rule stepped to cash and lost far less than
    buy-and-hold in the GFC (subperiod Sharpe 0.79 vs -1.03) and COVID
    (0.02 vs -0.66), but did MUCH WORSE than buy-and-hold in the 2022 rate
    shock (-1.68 vs -0.76) (subperiod_sharpe.csv).
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.
  - CAVEATS: the sample is SHORT, starting 2005-11 (SPY-and-cement overlap; no
    Dot-Com coverage). Cement shipments are NOT a Conference Board LEI
    component and NOT "new orders" -- they are a construction-activity series.
    The figures are nominal (not inflation-adjusted): in 2022 nominal sales
    stayed firm on rising prices even as equities de-rated. COVID 2020-21 is an
    extreme in-window outlier that can dominate the fit.

MONTHLY conventions: leads in MONTHS (winner L0); Sharpe annualized by
sqrt(12); OOS window 2017-01-31 -> 2025-06-30 (102 months). Numbers sourced
from results/cement_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20260830/*,
regime_quartile_returns.csv, subperiod_sharpe.csv, granger_by_lag.csv,
stationarity_tests_20260830.csv, structural_break_cement_spy.json,
tournament_results_20260830.csv, tournament_validation_20260830/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Cement Shipments as a Procyclical SPY Overlay"
    PAGE_SUBTITLE = (
        "Portland Cement Shipments (Data Master) x S&P 500 (SPY), monthly "
        "construction-activity growth signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        "## A search-phase rule with OOS Sharpe 1.20 vs 0.93 buy-and-hold -- "
        "procyclical and direction-consistent with the prior, but found-in-"
        "search on a short 2005-start sample, with no formal predictive edge "
        "and a bad 2022"
    )

    PLAIN_ENGLISH = (
        "Portland Cement Shipments is the volume of cement U.S. producers ship "
        "each month -- an input to construction and infrastructure. Because "
        "cement is poured into projects that track the real-investment cycle, "
        "it is a LEADING, construction-activity indicator, and the economic "
        "prior is procyclical: firm, rising shipment growth signals an "
        "investment upswing and risk-on equities; falling shipments signal a "
        "construction slowdown. This pair tests whether cement-shipment growth "
        "can improve SPY timing. Read the result as procyclical context and a "
        "concurrent regime filter, not as a forecast: the formal lead-lag "
        "tests find no predictive edge, and the winning rule uses the LATEST "
        "growth reading (a zero-month lead), so it makes no advance-warning "
        "claim. It is a grid-search candidate at LOW confidence, not a "
        "validated or deployable edge."
    )

    WHERE_THIS_FITS = (
        "This is a construction-activity overlay for broad U.S. equities. It "
        "belongs in the portal as a procyclical context signal: the direction "
        "agrees with the economic prior (firm cement growth = risk-on), which "
        "is a point in its favor, but it is a concurrent regime filter on a "
        "short sample, not an early-warning forecast and not a validated edge. "
        "Readers should weigh the modest, mixed edge over buy-and-hold and the "
        "found-in-search status before taking it as anything more than a "
        "candidate."
    )

    ONE_SENTENCE_THESIS = (
        "Cement-shipment growth is procyclical with equities CONCURRENTLY "
        "(weakest-growth quartile has the worst SPY Sharpe, 0.33; strongest "
        "the best, 1.12) but does NOT lead SPY -- Granger is insignificant at "
        "every lag (min p = 0.14), local projections are null, and the "
        "pre-whitened cross-correlation has no significant bar at any offset -- "
        "so the search's best rule, a PROCYCLICAL zero-lead long/cash filter "
        "with OOS Sharpe 1.20 vs 0.93, is a direction-consistent but "
        "found-in-search candidate on a short 2005-start sample, not a "
        "validated edge."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 102-month window (2017-01-31 -> 2025-06-30). The winner was found "
        "as the best of 252 valid combinations, and the MEDIAN valid combo "
        "(0.653) UNDERPERFORMS buy-and-hold (0.935) -- the typical rule "
        "subtracts value. The winner's edge is modest and mixed: OOS annualized "
        "return 15.3% vs 14.6%, max drawdown -20.9% vs -23.9%, volatility "
        "12.6%. Turnover is HIGH (3.76/yr, 32 trades). Read the Sharpe "
        "(1.20 vs 0.93) as a single-sample search result, not a proven edge. "
        "Sharpe ratios use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "Portland Cement Shipments vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the cement-shipment level (nominal $, left axis) is "
        "shown with SPY on the same time axis, NBER recessions shaded. The "
        "series begins in 2005 (SPY-and-cement overlap), so there is no "
        "Dot-Com coverage. The traded signal is not the level (it is "
        "non-stationary) but its 6-month growth. Watch the shaded recessions -- "
        "cement shipments collapsed through the 2008-09 housing bust and dipped "
        "in the 2020 COVID shock."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Cement-Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest cement-shipment "
        "growth) to Q4 (strongest), with concurrent SPY Sharpe in each. The "
        "weakest-growth quartile Q1 is the worst (Sharpe 0.33) and the "
        "strongest Q4 the best (1.12), with a non-monotonic middle (Q2 1.06, "
        "Q3 0.62) -- broadly PROCYCLICAL concurrently. This matches the "
        "procyclical direction the tournament selected. Descriptive and "
        "concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical, zero-lead cement-growth filter**. It holds SPY when the latest 6-month growth in cement shipments is at or above its five-year rolling 25th percentile (i.e. when construction-activity growth is *firm*), and holds cash otherwise. Out-of-sample (2017-01 to 2025-06, 102 months), this rule earns a Sharpe of 1.20 versus 0.93 for buy-and-hold, with an annualized return of 15.3% versus 14.6% and a maximum drawdown of -20.9% versus -23.9%. The direction agrees with the economic prior, which is a genuine point in its favor -- but the edge over buy-and-hold is modest and the rule is a **found-in-search** candidate on a short sample, not a validated edge.

### The Construction-Activity Hypothesis

Portland cement shipments measure the flow of cement into U.S. construction and infrastructure. Because cement is poured into projects that move with the real-investment cycle, it is a **leading, construction-activity** indicator. The economic prior is that cement-shipment growth is **procyclical**: firm, rising shipments are risk-on for equities; slowing shipments are an early sign that construction and investment are cooling.

The concurrent evidence supports that prior: sort months by cement growth and the weakest-growth quartile has the worst concurrent SPY Sharpe (0.33), while the strongest-growth quartile has the best (1.12). The tournament's winning rule runs the **same** way -- it buys SPY when growth is firm -- and at a zero-month lead, so it is a concurrent regime filter rather than a forecast.

### Why This Is Not a Forecast

The formal lead-lag tests are blunt. Cement-shipment growth does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.14), forward-return correlations are near zero at every horizon (the largest cell anywhere, acceleration vs 1-month-forward SPY, is r = 0.12 and not significant at 5%), and local projections are essentially null. The pre-whitened cross-correlation has **no** significant bar at any offset -- neither a cement-leads-SPY nor a SPY-leads-cement signal. So the pair carries no proven advance-warning content; the winner earns its search-phase Sharpe as a *concurrent* procyclical filter, and this dashboard treats it as a construction-activity overlay whose status is found-in-search, not deployable.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Cement shipments collapsed through 2008-09 as the housing "
                "bust seized up construction. The rule stepped to cash and lost "
                "far less than buy-and-hold in this window (subperiod Sharpe "
                "0.79 vs -1.03) -- its strongest stress episode."
            ),
            "caption": "GFC: cement shipments collapsed with the housing bust 2008-09; the rule lost far less than SPY.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Cement shipments dipped in spring 2020 and rebounded. The rule "
                "sat largely defensive and lost less than buy-and-hold "
                "(0.02 vs -0.66), but this is an extreme, exogenous in-window "
                "outlier that can dominate the backtest fit -- read any rule "
                "that leans on it with caution."
            ),
            "caption": "COVID: sharp dip and rebound, an outlier that can dominate the fit.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Nominal cement sales stayed firm through 2022 because prices "
                "were rising, even as equities de-rated. The rule stayed long "
                "and did MUCH WORSE than buy-and-hold here (subperiod Sharpe "
                "-1.68 vs -0.76) -- the key caveat of a nominal-dollar series: "
                "inflation can keep the growth signal firm while the market "
                "falls."
            ),
            "caption": "2022: nominal sales stayed firm on inflation; the rule stayed long and underperformed SPY.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is procyclical but imperfect as a timing tool. The rule's defense was real but uneven. In the GFC it stepped to cash and lost far less than buy-and-hold (subperiod Sharpe 0.79 vs -1.03); through COVID it stayed largely defensive and lost less (0.02 vs -0.66). But in the 2022 rate shock the nominal series stayed firm on inflation, the rule stayed long, and it did **much worse** than buy-and-hold (-1.68 vs -0.76) -- exactly when a demand signal would have been most useful. The sample starts in 2005, so there is no Dot-Com coverage. The honest reading is not "cement predicts drawdowns"; it is that a concurrent, procyclical filter helped in two goods-economy recessions and hurt badly in one inflation-driven de-rating.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this construction-activity story "
        "survives correlation, lead-lag, regime, and strategy checks. It "
        "survives as procyclical *context* -- the direction is consistent -- "
        "but not as a forecast: the formal lead-lag evidence is absent, and the "
        "winner is a concurrent, found-in-search candidate."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether cement-shipment growth and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster cement-shipment growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean stronger cement growth lines up with stronger future SPY "
        "returns; pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon. The largest cell anywhere is cement acceleration "
        "vs the 1-month-forward SPY return (r = 0.12, p = 0.085) -- not "
        "significant at 5%, and not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; the "
        "6-month-growth cells are near zero (|r| <= 0.07), and the largest cell "
        "anywhere is acceleration vs 1-month-forward SPY at r = 0.12 "
        "(p = 0.085)."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair as a forecast. The "
        "more relevant question is whether a concurrent growth filter improves "
        "portfolio behavior in the searched sample."
    ),
    key_message="Cement growth is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does cement-shipment growth lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-12 is 0.14 (lag 2) -- cement growth does not "
        "Granger-cause SPY returns."
    ),
    observation=(
        "Across all twelve monthly lags the cement->SPY p-value never falls "
        "below 0.14; the F-statistics are small. There is no formal evidence "
        "of lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal forecast claim. The strategy must be framed as "
        "a searched, concurrent construction-activity overlay, not proof that "
        "cement growth causes future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.14); cement does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by cement YoY growth and compares "
        "concurrent SPY returns across construction-activity regimes."
    ),
    question="Do weak and strong construction-activity regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-growth regime; Q4 is the strongest. Compare Sharpe, "
        "average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: broadly PROCYCLICAL -- the weakest-growth quartile "
        "Q1 has the worst concurrent SPY Sharpe (0.33) and the strongest Q4 "
        "the best (1.12), with a non-monotonic middle (Q2 1.06, Q3 0.62). "
        "This matches the procyclical winner's direction."
    ),
    observation=(
        "Concurrent SPY Sharpe is lowest in the weakest-growth quartile "
        "(Q1 0.33) and highest in the strongest (Q4 1.12); the middle is "
        "non-monotonic (Q2 1.06, Q3 0.62). Each quartile has 56 months."
    ),
    interpretation=(
        "The concurrent pattern fits a procyclical construction-activity story "
        "and is DIRECTION-CONSISTENT with the tournament winner. That "
        "coherence is a point in the pair's favor, though the middle quartiles "
        "are noisy and the effect is concurrent, not a proven lead."
    ),
    key_message="Stronger cement growth coincides with better SPY conditions -- procyclical, matching the winner's direction.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does cement growth line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "cement leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: NO bar is significant at any offset -- neither a "
        "cement-leads-SPY nor a SPY-leads-cement signal survives filtering for "
        "autocorrelation. There is no coherent lead-lag echo."
    ),
    observation=(
        "Every cross-correlation, lead-side and lag-side, sits inside the "
        "confidence band; the largest magnitude anywhere (~0.11 at offset -10) "
        "is not significant."
    ),
    interpretation=(
        "There is no window in which cement growth foreshadows SPY, and none in "
        "which SPY foreshadows cement. Consistent with the null Granger and "
        "local-projection results, the pair carries no forecasting lead."
    ),
    key_message="No cross-correlation is significant at any offset; the pair shows no lead-lag forecast.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the cement-growth signal."
    ),
    question="How does SPY respond after cement growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "cement-growth signal. Coefficients near zero mean no detectable "
        "effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across all "
        "horizons (1, 3, 6, 12 months), none statistically significant "
        "(p from 0.28 to 0.99), with negligible R^2."
    ),
    observation=(
        "Point estimates are near zero at every horizon and no coefficient is "
        "significant; the explained variance is trivial throughout (max R^2 "
        "about 0.005 at horizon 1)."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. "
        "Nothing here rescues a forward-looking reading of the indicator."
    ),
    key_message="Local projections are null; cement growth carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the cement signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does cement growth behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is close to zero and flat across "
        "quantiles -- no material tail sensitivity for the cement signal."
    ),
    observation=(
        "The estimated coefficient is small and essentially unchanged across "
        "the tested quantiles, consistent with the near-null correlation and "
        "local-projection results."
    ),
    interpretation=(
        "Cement growth does not flag elevated crash risk or exceptional "
        "upside -- there is no tail channel to trade."
    ),
    key_message="Cement growth shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Cement Is Procyclical Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a cautious, direction-consistent "
        "construction-activity overlay -- and nothing stronger. The strategy "
        "winner improves search-phase OOS Sharpe (1.20 vs 0.93) and its "
        "procyclical direction agrees with both the prior and the concurrent "
        "quartiles, but formal lead-lag evidence is absent (Granger min "
        "p = 0.14; local projections null; CCF has no significant bar at any "
        "offset), so it is a concurrent regime filter, not a forecast."
    ),
    "plain_english": (
        "This page asks whether cement-shipment growth helps time SPY. The "
        "answer is: as concurrent context, maybe; as a forecast, no. "
        "Concurrent quartiles are procyclical (weak growth = worse market) and "
        "the winning rule runs the same way -- but the causal tests find no "
        "lead, and the winner uses the latest reading (zero lead). Treat it as "
        "a procyclical regime overlay, not an early-warning system, and note "
        "it is found-in-search."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 252 strategy combinations (all 252 valid) "
        "across six cement growth transforms, fixed and rolling thresholds, "
        "procyclical/countercyclical orientations, and leads from 0 to 12 "
        "months. The selected winner is `chg_6m / T_roll_p25 / P1_long_cash "
        "procyclical / L0`, with OOS Sharpe 1.197. The MEDIAN valid combo "
        "scores 0.653 -- below buy-and-hold's 0.935 -- and the runner-up "
        "(`chg_6m / T0_zero / procyclical / L0`, 1.194) shares the same signal "
        "and zero lead, so the top of the surface is a tight cluster of "
        "concurrent 6-month-growth rules rather than a single fragile cell. "
        "That is mildly reassuring, but the median result still shows the "
        "typical rule subtracts value."
    ),
    "transition": (
        "**Transition:** the evidence is procyclical context, direction-"
        "consistent but not causal. The Strategy page shows the exact long/cash "
        "rule, its modest and mixed edge over buy-and-hold, the high turnover, "
        "and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical, Zero-Lead Cement-Growth Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using 6-month cement-shipment growth, "
        "a rolling 25th-percentile threshold, a procyclical orientation, and a "
        "zero-month lead -- direction-consistent with the prior, but "
        "found-in-search on a short sample, active (high turnover), and mixed "
        "in stress."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the latest 6-month growth in cement shipments "
        "is at or above its five-year rolling 25th percentile (i.e. when "
        "construction-activity growth is firm); otherwise it holds cash. This "
        "is a concurrent, PROCYCLICAL construction-activity filter -- matching "
        "the economic prior for a leading indicator -- not a real-time "
        "recession forecast. Judge it by its modest, mixed edge over "
        "buy-and-hold (Sharpe 1.20 vs 0.93, return 15.3% vs 14.6%, drawdown "
        "-20.9% vs -23.9%) and remember it is found-in-search and trades "
        "actively (turnover 3.76/yr)."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/cement_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/cement_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/cement_spy/tournament_results_20260830.csv"},
        {"label": "Stationarity tests", "path": "results/cement_spy/stationarity_tests_20260830.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the latest 6-month change in cement shipments is at or above its five-year rolling 25th percentile (i.e. when construction-activity growth is *firm*); otherwise hold cash. This is a procyclical rule and matches the procyclical prior.

If-then form:
- **IF** `cement_6m` (latest, no lead) is at or above its 60-month rolling 25th percentile -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2025-06-30, 102 months): Sharpe 1.20 versus 0.93 buy-and-hold; annualized return 15.3% versus 14.6%; maximum drawdown -20.9% versus -23.9%; annualized volatility 12.6%; win rate 54.9%; 32 trades; annual turnover 3.76 (HIGH -- an active in/out rule). The edge over buy-and-hold is modest and mixed, and the result is found-in-search.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads Portland Cement Shipments (nominal $) at month-end. Second, it computes the 6-month percent change in shipments (`cement_6m`). Third, it applies a zero-month lead, so the allocation uses the latest reading (a concurrent filter, not a forecast). Finally, the signal is compared with its 60-month rolling 25th percentile: when growth is at or above that threshold, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year (high here -- the rule flips in and out frequently). Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Portland Cement Shipments at month end.
2. Compute the 6-month percent change.
3. Compare the latest value with its trailing 60-month rolling 25th percentile.
4. Hold SPY when that growth is at or above the rolling 25th percentile; otherwise hold cash.
5. Recheck monthly. Turnover is high (3.76/yr): the rule flips exposure frequently, so transaction costs matter.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule loses much LESS in the GFC "
        "(0.79 vs -1.03) and COVID (0.02 vs -0.66), but does MUCH WORSE than "
        "buy-and-hold in the 2022 rate shock (-1.68 vs -0.76), when nominal "
        "cement sales stayed firm on inflation and the rule stayed long. The "
        "Dot-Com bar is empty -- the sample starts in 2005. The stress defense "
        "is real but uneven."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is cement-shipment growth; the "
            "target is SPY returns. The rolling correlation tests whether their "
            "linear relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "cement/SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship shifted more materially across periods "
            "(here the max absolute rolling-correlation z-score reaches 2.9)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.20) is a right-tail maximum at "
        "lead 0; the median valid combo (0.653) sits BELOW buy-and-hold "
        "(0.935), so the typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The result is marked `found_in_search` at LOW confidence: the median valid combo (0.653) underperforms buy-and-hold (0.935), and the winner still needs a frozen-rule holdout confirmation. The bootstrap p = 0.004 is an in-sample significance check, not out-of-sample validation.
2. This is a concurrent filter, not a forecast. Granger causality is insignificant at every lag (min p = 0.14), local projections are null, and the pre-whitened CCF has no significant bar at any offset -- there is no proven predictive lead.
3. The edge over buy-and-hold is modest and mixed: OOS return 15.3% vs 14.6% and drawdown -20.9% vs -23.9% are improvements, but the rule did MUCH WORSE than buy-and-hold in the 2022 rate shock (-1.68 vs -0.76).
4. Turnover is HIGH (3.76/yr, 32 OOS trades): this is an active in/out rule and transaction costs matter more than for a set-and-forget overlay.
5. The sample is SHORT, starting 2005-11 (SPY-and-cement overlap; no Dot-Com coverage), which limits durability testing.
6. Cement shipments are nominal: in 2022 inflation kept the growth signal firm while equities fell. COVID 2020-21 is an extreme in-window outlier that can dominate the fit. Cement is a construction-activity series -- NOT a Conference Board LEI component and NOT "new orders".
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the latest 6-month cement growth crossed at or above its "
        "rolling 25th-percentile threshold, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when growth fell below the threshold."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2009-05-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: chg_6m procyclical rule crossed T_roll_p25; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master | Portland Cement Shipments (nominal $, SA) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is Portland Cement Shipments in nominal $ (seasonally "
    "adjusted). The level is non-stationary (ADF fails to reject a unit root, "
    "p = 0.22; KPSS rejects stationarity), so the pipeline constructs growth "
    "transforms -- month-over-month, three-month, and six-month percent "
    "changes; twelve-month (YoY) growth; a 60-month rolling YoY z-score; and "
    "YoY acceleration -- all of which are stationary. The winning signal is "
    "`cement_6m`, the six-month growth, used with a zero-month lead, a 60-month "
    "rolling 25th-percentile threshold, and a procyclical orientation (long "
    "SPY when growth is at or above the threshold)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does cement growth move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong construction-activity regimes behave differently? | Makes the procyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past cement information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: cement growth transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x lead times (0-12 months). The final tournament has 252 combinations, all 252 valid. The winning rule is `cement_6m / T_roll_p25 / P1_long_cash procyclical / L0`, the maximum OOS Sharpe (1.197). The median valid combo (0.653) underperforms buy-and-hold (0.935), and the runner-up (`chg_6m / T0_zero / procyclical / L0`, 1.194) shares the winner's 6-month-growth signal and zero lead -- read the winner as the top of a tight concurrent-procyclical cluster, direction-consistent with the prior but still a selection maximum on a short sample, not a validated edge.
"""

_REFERENCES_MD = """
1. Data Master (internal panel), Portland Cement Shipments (nominal $, SA).
2. U.S. Geological Survey, Mineral Commodity Summaries: Cement (context on cement as a construction-activity gauge).
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
        "Monthly sample from 2005-11-30 to 2025-06-30, with out-of-sample "
        "window 2017-01-31 to 2025-06-30 (102 months). The SPY-and-cement "
        "overlap limits the usable sample to a short 2005 start, with no "
        "Dot-Com coverage."
    ),
    plain_english=(
        "This page documents how Portland Cement Shipments was turned into "
        "stationary growth signals, how the econometric checks were run, and "
        "how the tournament selected the final SPY allocation rule -- along "
        "with the honest caveat that the selection maximum, while "
        "direction-consistent with the procyclical prior, is a concurrent "
        "found-in-search candidate on a short sample and not yet a validated "
        "edge."
    ),
)
