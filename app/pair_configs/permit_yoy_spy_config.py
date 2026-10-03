"""Building Permits YoY x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY leading-housing pair. Building Permits YoY is the
year-over-year percent change of US building permits (computed from the H Permit
level in Data Master). It is a zero-centred GROWTH RATE: > 0 = permits higher
than a year ago (housing/construction expanding), < 0 = contracting. Building
permits are a classic LEADING indicator of the business cycle -- a Conference
Board LEI component -- so the leading-indicator framing is genuinely apt here.
This is NOT a diffusion index; there is no ">50 = expansion" reading. Signals are
built on the YoY series: level (of the YoY, zero-centred), 1-month change
(diff_1m), 12-month change (chg_12m), and a 60-month z-score (zscore_60m).

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/permit_yoy_spy/*:
  - The tournament winner (`chg_12m` 12-month change / T_roll_p50 rolling-median
    / PROCYCLICAL / L9 months / P1_long_cash; OOS Sharpe 1.31 vs 0.92 B&H) is
    the grid maximum over 168 combinations (all 168 valid). The MEDIAN valid
    combo scores 0.653 -- it UNDERPERFORMS buy-and-hold (0.92)
    (winner_summary.json).
  - DIRECTION IS CONSISTENT WITH THE PRIOR. Permit growth is procyclical and a
    LEADING indicator, and the search selected a PROCYCLICAL rule (hold SPY when
    9-month-lagged permit-YoY growth is at or above its 5-year rolling median).
    `interpretation_metadata.json` records expected_direction procyclical vs
    observed_direction procyclical, direction_consistent = true, confidence =
    low. That is a genuine point in the pair's favour -- but it is still
    found-in-search.
  - THE RETURN IS BELOW BUY-AND-HOLD. OOS annualized return is 13.0% versus
    14.6% for buy-and-hold. The Sharpe edge (1.31 vs 0.92) is therefore a
    volatility/drawdown story, NOT a return advantage: OOS max drawdown is
    -8.1% versus -23.9%, at a much lower volatility (9.7%). Read the Sharpe as
    drawdown avoidance, not stock-picking skill.
  - TURNOVER IS HIGH. Annual turnover is 3.55/yr across 29 OOS trades -- the
    rule flips exposure often, so the result is sensitive to transaction costs
    (only 5 bps assumed). This is a prominent deployment caveat.
  - No lead-lag forecast. Permit-YoY does NOT Granger-cause SPY at any tested
    lag (minimum p = 0.33 at lag 4) (granger_by_lag.csv). Linear correlation
    with forward SPY is near zero at every horizon; the largest cell anywhere is
    the permit-YoY level vs 6-month-forward SPY (r = 0.10, p = 0.05, borderline)
    and the WINNING signal (chg_12m) vs forward SPY is essentially zero
    (|r| <= 0.04) (core_models_20260912/correlations.csv). Local projections are
    near-null at every horizon (no coefficient significant; trivial R^2)
    (local_projections.csv). Pre-whitened cross-correlation shows NO significant
    bar at any offset from -6 to +6 months -- no coherent lead-lag echo in
    either direction (ccf_prewhitened.csv).
  - The concurrent quartile evidence is MODEST and, if anything, mildly INVERSE:
    sorting months by permit-YoY, the weakest-growth quartile Q1 has the BEST
    concurrent SPY Sharpe (0.94) and the strongest-growth quartile Q4 the worst
    (0.50), declining monotonically (Q2 0.78, Q3 0.78)
    (regime_quartile_returns.csv). So the concurrent reading does NOT cleanly
    corroborate the procyclical winner; treat it as descriptive, not a tradable
    lead.
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: across every stress
    window in subperiod_sharpe.csv the rule beat buy-and-hold SPY (Dot-Com
    -0.18 vs -0.70, GFC +0.14 vs -1.03, COVID +2.18 vs -0.08, 2022 rate hike
    -0.58 vs -0.76). A stationary block bootstrap puts the winner's Sharpe at
    p = 0.00 (tournament_validation_20260912/bootstrap.csv), but that is an
    in-sample significance check, not out-of-sample validation.
  - The L9 (9-month) lead is economically plausible -- permits genuinely lead
    the housing cycle -- but a 9-month lead still needs adjacent-lead durability
    checking, and the sample holds only a few full cycles (analyst_suggestions
    .json). The runner-up is the SAME signal/threshold/strategy at L2
    (objective 1.171), so the top of the surface concentrates on chg_12m /
    T_roll_p50 / P1 across leads, not a single isolated lead.
  - Status is `found_in_search` (evidence_status.json): the winner still needs a
    frozen-rule holdout / final exam.

MONTHLY conventions: leads in MONTHS (winner L9); Sharpe annualized by sqrt(12);
OOS window 2017-07-31 -> 2025-08-31 (98 months). Numbers sourced from
results/permit_yoy_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, signal_scope.json, analyst_suggestions.json,
core_models_20260912/*, regime_quartile_returns.csv, subperiod_sharpe.csv,
granger_by_lag.csv, stationarity_tests_20260912.csv,
structural_break_permit_yoy_spy.json, tournament_results_20260912.csv,
tournament_validation_20260912/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Building Permits Growth as a Defensive SPY Overlay"
    PAGE_SUBTITLE = (
        "Building Permits YoY (Data Master, from the H Permit level) x "
        "S&P 500 (SPY), monthly housing-cycle growth signals tested against "
        "SPY returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.31 OOS vs 0.92 buy-and-hold, but the honest headline is the "
        "drawdown (-8.1% vs -23.9%) -- the winning rule earns LESS than SPY "
        "(13.0% vs 14.6%) and trades often (turnover 3.55/yr), so read it as "
        "risk reduction, not a return edge"
    )

    PLAIN_ENGLISH = (
        "Building Permits YoY is the year-over-year percent change in the number "
        "of new US building permits -- a zero-centred growth rate where above "
        "zero means permits are higher than a year ago (housing expanding) and "
        "below zero means they are contracting. Because builders pull permits "
        "before they break ground, permits are a classic LEADING indicator of "
        "the business cycle -- one of the components of the Conference Board's "
        "Leading Economic Index -- and the economic prior is procyclical: rising "
        "permit growth signals expansion and risk-on equities. This pair tests "
        "whether permit growth can improve SPY timing. Encouragingly, the rule "
        "the search selected runs the RIGHT way (buy when permit growth is "
        "healthy) at a plausible 9-month lead -- but the formal lead-lag tests "
        "find no predictive edge, the rule earns slightly less than simply "
        "holding SPY, and it trades often. Read the result as housing-cycle "
        "context and drawdown control, not as a forecast."
    )

    WHERE_THIS_FITS = (
        "This is a housing-cycle overlay for broad U.S. equities. It belongs in "
        "the portal as a defensive context signal: useful for drawdown control "
        "in the searched sample, but not a standalone forecast. Its winning "
        "direction is procyclical, which matches the leading-housing prior -- a "
        "genuine point in its favour -- but the formal causal tests are blunt "
        "and the rule's turnover is high, so it should be treated as a "
        "found-in-search candidate that still needs a fresh holdout before any "
        "deployment weight is placed on it."
    )

    ONE_SENTENCE_THESIS = (
        "Building-permit growth is a genuine leading indicator, and the search's "
        "best rule -- a procyclical long/cash filter at a 9-month lead -- is "
        "direction-consistent with that prior (OOS Sharpe 1.31 vs 0.92) and cuts "
        "max drawdown sharply (-8.1% vs -23.9%), but it earns LESS than SPY "
        "(13.0% vs 14.6%), trades often (turnover 3.55/yr), and finds no formal "
        "lead-lag support (Granger min p = 0.33; local projections null; no "
        "significant cross-correlation at any offset), so it is a "
        "drawdown-reduction candidate, found in search, at low confidence."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-07-31 -> 2025-08-31). The winner was found "
        "as the best of 168 valid combinations, and the MEDIAN valid combo "
        "(0.653) UNDERPERFORMS buy-and-hold (0.92) -- the typical rule subtracts "
        "value. The defensible number is the max drawdown (-8.1% vs -23.9%) at a "
        "slightly LOWER return (13.0% vs 14.6%) and much lower volatility "
        "(9.7%) -- read the Sharpe (1.31 vs 0.92) as volatility avoidance, not "
        "a return edge. Turnover is HIGH (3.55/yr, 29 trades), so the result is "
        "cost-sensitive. Sharpe ratios use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "Building Permits YoY vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the permit-YoY growth rate (left axis, zero-centred -- "
        "above 0 = permits growing vs a year ago, below 0 = contracting) is "
        "shown with SPY on the same time axis, NBER recessions shaded. Watch the "
        "shaded recessions -- permit growth typically turned negative going "
        "into, and often ahead of, the equity downturns in this window, which is "
        "the leading-indicator behaviour the pair is built on."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Permit-Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest permit growth) to "
        "Q4 (strongest), with concurrent SPY Sharpe in each. The spread is "
        "modest and, if anything, mildly INVERSE -- the weakest-growth quartile "
        "Q1 has the BEST concurrent SPY Sharpe (0.94) and the strongest-growth "
        "quartile Q4 the worst (0.50), declining through Q2 (0.78) and Q3 "
        "(0.78). This concurrent reading does not cleanly corroborate the "
        "procyclical winner; it is descriptive, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical, 9-month-lagged permit-growth filter**. It holds SPY when the 12-month change in building-permit YoY from nine months earlier was at or above its five-year rolling median, and holds cash otherwise. Out-of-sample (2017-07 to 2025-08), this rule earns a Sharpe of 1.31 versus 0.92 for buy-and-hold, with a maximum drawdown of **-8.1% versus -23.9%** at an annualized return of **13.0% versus 14.6%**. Read that as the honest headline: the rule's edge is a much shallower worst-case loss and lower volatility, **not** a return advantage -- and it trades often (annual turnover 3.55, 29 trades), so it is sensitive to transaction costs.

### The Housing-Cycle Hypothesis

Building permits measure intended future construction -- authorizations pulled now for homes built later. Because they are committed ahead of activity, permits are a **leading** indicator, a component of the Conference Board's Leading Economic Index. The economic prior is that permit growth is **procyclical**: firm, rising permit growth is risk-on for equities; falling permit growth is an early sign the cycle is cooling. This pair's winning rule is direction-consistent with that prior -- it buys SPY when permit growth is healthy -- which is a genuine point in its favour, unlike a search that runs against the prior.

### Why This Is Still Not a Forecast

The formal lead-lag tests are blunt. Permit-YoY does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.33), forward-return correlations are near zero at every horizon, and local projections are essentially null. The pre-whitened cross-correlation shows no significant bar at any offset from -6 to +6 months -- no coherent lead-lag echo in either direction. And the concurrent quartile spread is modest and mildly *inverse*, not a clean procyclical corroboration. So while a 9-month lead is economically plausible for a leading housing indicator, the statistical support for a *forecast* is thin. This dashboard therefore treats the pair as a searched housing-cycle overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "Permit growth softened around the 2001 downturn. The searched "
                "rule lost less than buy-and-hold in this window (subperiod "
                "Sharpe -0.18 vs -0.70), an early instance of its defensive "
                "behaviour rather than a forecast."
            ),
            "caption": "Dot-Com: permit growth softened; the rule lost less than SPY (-0.18 vs -0.70).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Permit growth collapsed through the 2007-09 housing bust -- the "
                "clearest case of permits leading the cycle. The rule was "
                "roughly flat-to-positive here (+0.14) while buy-and-hold "
                "cratered (-1.03), its strongest defensive episode alongside "
                "COVID."
            ),
            "caption": "GFC: permit growth collapsed; the rule held up (+0.14) while SPY fell (-1.03).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Permits plunged in spring 2020 and rebounded fast. This is an "
                "extreme, exogenous in-window outlier that can dominate the "
                "backtest fit -- the rule's very high subperiod Sharpe here "
                "(+2.18) should be read with that caution."
            ),
            "caption": "COVID: extreme collapse and rebound; the rule's +2.18 leans on an outlier.",
        },
        {
            "slug": "rate_hike_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Higher mortgage rates pushed permit growth sharply negative "
                "through 2022 as equities de-rated. The rule lost less than "
                "buy-and-hold (-0.58 vs -0.76) but still fell -- the defence is "
                "real but partial."
            ),
            "caption": "2022: rates cut permit growth; the rule lost less than SPY (-0.58 vs -0.76).",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is a plausible leading indicator but imperfect as a forecast. Permit growth turned negative during the Dot-Com, GFC, COVID and 2022 stress windows -- and in every one of them the searched rule lost less than buy-and-hold: it was flat-to-positive through the GFC and COVID (its two strongest episodes) and lost less in the Dot-Com and 2022 drawdowns. That is where its drawdown advantage was earned. The honest reading is not "permit growth predicts drawdowns"; it is that a procyclical, lagged filter stepped to cash during several housing-led stress windows, which is exactly when a leading housing indicator should help. COVID is an extreme outlier that flatters the fit, so weight the GFC -- a genuine housing-led recession -- most heavily as evidence.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this housing-cycle story survives "
        "correlation, lead-lag, regime, and strategy checks. The direction is "
        "consistent with the leading-housing prior, but the value is defensive, "
        "not predictive -- the formal lead-lag tests find no forecast."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether permit-growth signals and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster permit growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean stronger permit growth lines up with stronger future SPY returns; "
        "pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon. The largest cell anywhere is the permit-YoY level "
        "vs the 6-month-forward SPY return (r = 0.10, p = 0.05, borderline); "
        "the winning signal (12-month change) vs forward SPY is near zero "
        "(|r| <= 0.04) -- not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; the "
        "chg_12m-vs-forward cells are near zero (|r| <= 0.04), and the largest "
        "cell anywhere is the permit-YoY level vs 6-month-forward SPY at "
        "r = 0.10 (borderline, p = 0.05)."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair. The more relevant "
        "question is whether a lagged growth filter improves portfolio "
        "behavior in the searched sample."
    ),
    key_message="Permit growth is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does permit growth lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-6 is 0.33 -- permit growth does not Granger-cause SPY "
        "returns."
    ),
    observation=(
        "Across all six monthly lags the permit->SPY p-value never falls below "
        "0.33; the F-statistics are small. There is no formal evidence of "
        "lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal claim. The strategy must be framed as a "
        "searched housing-cycle overlay, not proof that permits cause future "
        "SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.33); permits do not Granger-cause SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by permit YoY growth and compares "
        "concurrent SPY returns across housing-cycle regimes."
    ),
    question="Do weak and strong permit-growth regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-growth regime; Q4 is the strongest. Compare Sharpe, "
        "average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: the concurrent spread is modest and mildly INVERSE -- "
        "the weakest-growth quartile Q1 has the BEST concurrent SPY Sharpe "
        "(0.94) and the strongest-growth quartile Q4 the worst (0.50), "
        "declining through Q2 (0.78) and Q3 (0.78). This does not cleanly "
        "corroborate the procyclical winner."
    ),
    observation=(
        "Concurrent SPY Sharpe is highest in the weakest-growth quartile "
        "(Q1 0.94) and lowest in the strongest (Q4 0.50), with Q2 and Q3 in "
        "between (0.78 each) -- a modest, mildly inverse concurrent pattern."
    ),
    interpretation=(
        "The concurrent quartile evidence is weak and does not line up with the "
        "procyclical, lagged winner. Read it as descriptive context, not a "
        "tradable concurrent signal, and lean on the strategy backtest and the "
        "leading-indicator prior for the direction."
    ),
    key_message="The concurrent quartile spread is modest and mildly inverse -- descriptive, not a clean confirmation.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does permit growth line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "permits lead; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: NO bar is significant at any offset from -6 to +6 "
        "months -- every cross-correlation sits inside the confidence band. "
        "After filtering persistence there is no coherent lead-lag echo in "
        "either direction."
    ),
    observation=(
        "All cross-correlations from lag -6 to +6 are inside the confidence "
        "band (|ccf| <= 0.07); none is significant on the permit-leads side or "
        "the SPY-leads side."
    ),
    interpretation=(
        "There is no coherent window in which permit growth foreshadows SPY "
        "once persistence is removed. Any timing value the strategy shows comes "
        "from the lagged filter's regime behaviour, not a clean cross-"
        "correlation lead."
    ),
    key_message="No significant cross-correlation at any offset; no clean lead-lag echo either way.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the permit-growth signal."
    ),
    question="How does SPY respond after permit growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "permit-growth signal. Coefficients near zero mean no detectable "
        "effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across all horizons "
        "(1, 3, 6 months), none statistically significant (p from 0.48 to "
        "0.66), with negligible R^2."
    ),
    observation=(
        "Point estimates are near zero at every horizon and no coefficient is "
        "significant; the explained variance is trivial throughout."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. "
        "Nothing here rescues a forward-looking reading of the indicator."
    ),
    key_message="Local projections are null; permit growth carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the permit signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does permit growth behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is close to zero and flat across "
        "quantiles -- no material tail sensitivity for the permit signal."
    ),
    observation=(
        "The estimated coefficient is small and essentially unchanged across "
        "the tested quantiles, consistent with the near-null correlation and "
        "local-projection results."
    ),
    interpretation=(
        "Permit growth does not flag elevated crash risk or exceptional upside "
        "-- there is no tail channel to trade."
    ),
    key_message="Permit growth shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Permit Growth Is a Direction-Consistent Overlay, Not a SPY Forecast",
    "overview": (
        "The evidence supports a cautious housing-cycle overlay -- and nothing "
        "stronger. The strategy winner improves search-phase OOS Sharpe and "
        "runs the procyclical way the leading-housing prior expects, but formal "
        "lead-lag evidence is absent (Granger min p = 0.33; local projections "
        "null; no significant cross-correlation at any offset), the concurrent "
        "quartiles are mildly inverse rather than confirming, and the OOS "
        "return is below buy-and-hold."
    ),
    "plain_english": (
        "This page asks whether permit growth helps time SPY. The answer is: "
        "not as a forecast. The winning rule points the sensible way (buy when "
        "permit growth is healthy) and cuts drawdowns, but the causal tests "
        "find no lead and it earns slightly less than just holding SPY. Treat "
        "it as a defensive, direction-consistent overlay, not an early-warning "
        "system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 168 strategy combinations (all 168 valid) across "
        "four permit-growth transforms, fixed and rolling thresholds, a "
        "long/cash strategy, a procyclical orientation, and leads of 0, 1, 2, "
        "3, 6, 9 and 12 months. The selected winner is `chg_12m / T_roll_p50 / "
        "P1_long_cash procyclical / L9`, with OOS Sharpe 1.31. The MEDIAN valid "
        "combo scores 0.653 -- below buy-and-hold's 0.92 -- and the runner-up "
        "(`chg_12m / T_roll_p50 / P1_long_cash / L2`, 1.171) shares the same "
        "signal, rolling-median threshold and strategy, so the search surface "
        "concentrates on the chg_12m rolling-median rule across leads rather "
        "than on one isolated cell."
    ),
    "transition": (
        "**Transition:** the direction is consistent with the prior, but the "
        "evidence is context, not causation. The Strategy page shows the exact "
        "long/cash rule, the drawdown advantage that is its real virtue, the "
        "high turnover, and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical, Lagged Permit-Growth Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 12-month change in "
        "building-permit YoY, a rolling-median threshold, a procyclical "
        "orientation, and a 9-month lead -- valued for drawdown reduction, not "
        "for its return, and flagged for high turnover."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 12-month change in building-permit YoY "
        "from nine months earlier was at or above its five-year rolling median; "
        "otherwise it holds cash. This is a lagged, PROCYCLICAL housing-cycle "
        "filter -- consistent with the leading-indicator prior, not a "
        "real-time recession forecast. Judge it by its shallower drawdown "
        "(-8.1% vs -23.9%) and lower volatility, not by the headline return, "
        "which is BELOW buy-and-hold (13.0% vs 14.6%), and note the high "
        "turnover (3.55/yr)."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/permit_yoy_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/permit_yoy_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/permit_yoy_spy/tournament_results_20260912.csv"},
        {"label": "Stationarity tests", "path": "results/permit_yoy_spy/stationarity_tests_20260912.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 12-month change in building-permit YoY from nine months earlier was at or above its five-year rolling median (i.e. when permit-growth momentum was *healthy* nine months earlier); otherwise hold cash. This is a procyclical rule, consistent with the leading-housing prior.

If-then form:
- **IF** `permit_yoy_chg_12m` from 9 months earlier is at or above its 60-month rolling median -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-07-31 to 2025-08-31, 98 months): Sharpe 1.31 versus 0.92 buy-and-hold; annualized return **13.0% versus 14.6%** (below); **maximum drawdown -8.1% versus -23.9%**; annualized volatility 9.7%; Sortino 2.27; Calmar 1.61; win rate 36.7%; 29 trades; annual turnover **3.55 (HIGH)**. The drawdown and volatility reduction, not the Sharpe or return, is the defensible result -- and the high turnover makes it sensitive to transaction costs.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads Building Permits from Data Master (the H Permit level) at month-end and computes its year-over-year percent change (`permit_yoy`, a zero-centred growth rate). Second, it takes the 12-month change of that YoY series (`permit_yoy_chg_12m`). Third, it applies a 9-month lag before the SPY allocation is set. Finally, the lagged signal is compared with its 60-month rolling median: when the lagged 12-month change is at or above that median, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year (high here, 3.55). Win Rate is the share of out-of-sample months with positive strategy return (low partly because the rule sits in cash for stretches).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Building Permits (H Permit level) at month end and compute its year-over-year percent change.
2. Compute the 12-month change of that YoY series.
3. Take the value from 9 months earlier and compare it with its trailing 60-month rolling median.
4. Hold SPY when that lagged 12-month change was at or above the rolling median; otherwise hold cash.
5. Recheck monthly. Turnover is high (3.55/yr): the rule flips exposure often, so account for transaction costs.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule beat buy-and-hold in ALL four: "
        "GFC (+0.14 vs -1.03) and COVID (+2.18 vs -0.08) are its strongest "
        "episodes, and it lost less in the Dot-Com (-0.18 vs -0.70) and 2022 "
        "rate shock (-0.58 vs -0.76). The stress defense is consistent, though "
        "COVID is an outlier that flatters the picture."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is permit growth; the target is SPY "
            "returns. The rolling correlation tests whether their linear "
            "relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "permit/SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship shifted more materially across periods "
            "(here the max absolute rolling-correlation z-score reaches 2.9)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.31) is a right-tail maximum; the "
        "median valid combo (0.653) sits BELOW buy-and-hold (0.92), so the "
        "typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The result is marked `found_in_search`: the winner is the grid maximum over 168 combinations, the median valid combo (0.653) underperforms buy-and-hold, and it still needs a frozen-rule holdout confirmation. The bootstrap p = 0.00 is an in-sample significance check, not out-of-sample validation.
2. The OOS return (13.0%) is BELOW buy-and-hold (14.6%). The Sharpe edge is drawdown and volatility reduction (-8.1% vs -23.9% max drawdown, 9.7% vol), not a return advantage.
3. Turnover is HIGH (3.55/yr, 29 trades). At the assumed 5 bps cost the edge survives, but the result is sensitive to higher real-world transaction costs and slippage.
4. Formal lead-lag support is absent: Granger is insignificant at every lag (min p = 0.33), local projections are null, and the pre-whitened CCF has no significant bar at any offset. The strategy is not a proven causal forecast.
5. The concurrent quartile spread is modest and mildly inverse (weak-growth Q1 best, strong-growth Q4 worst), so the concurrent evidence does not cleanly confirm the procyclical winner.
6. The 9-month lead is economically plausible (permits lead the housing cycle), but the sample holds only a few full cycles, so the lead needs adjacent-lead durability checking. COVID 2020-21 is an extreme in-window outlier that can dominate the fit.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 9-month-lagged 12-month change in permit-YoY crossed at "
        "or above its rolling median, taking exposure from 0% to 100% SPY. A "
        "SELL moves back to cash when the lagged signal fell below the rolling "
        "median."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2017-07-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: chg_12m procyclical rule crossed T_roll_p50; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master.xlsx (H Permit sheet) | Building Permits, year-over-year % change (`permit_yoy`, from the PERMIT level) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the year-over-year percent change of US building "
    "permits, computed from the H Permit level in Data Master -- a zero-centred "
    "growth rate (> 0 = permits higher than a year ago, < 0 = contracting). It "
    "is NOT a diffusion index, so there is no '>50 = expansion' reading. The "
    "level of the YoY series is borderline non-stationary (ADF p = 0.08, KPSS "
    "does not reject stationarity), so the pipeline also builds clearly "
    "stationary transforms -- the 1-month change (`permit_yoy_diff_1m`), the "
    "12-month change (`permit_yoy_chg_12m`), and a 60-month rolling z-score "
    "(`permit_yoy_zscore_60m`). The winning signal is `permit_yoy_chg_12m`, the "
    "12-month change of the YoY series, used with a 9-month lead, a 60-month "
    "rolling-median threshold, and a procyclical orientation (long SPY when the "
    "lagged signal is at or above the median)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does permit growth move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong permit-growth regimes behave differently? | Makes the housing-cycle story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past permit information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: permit-growth transforms x fixed and rolling thresholds x a long/cash strategy x a procyclical orientation x lead times (0, 1, 2, 3, 6, 9, 12 months). The final tournament has 168 combinations, all 168 valid. The winning rule is `permit_yoy_chg_12m / T_roll_p50 / P1_long_cash procyclical / L9`, the maximum OOS Sharpe (1.31). The median valid combo (0.653) underperforms buy-and-hold (0.92), and the runner-up (`chg_12m / T_roll_p50 / P1_long_cash / L2`, 1.171) shares the winner's signal, rolling-median threshold and strategy -- read the winner as a selection maximum in a chg_12m rolling-median cluster, direction-consistent with the procyclical prior but not yet a validated edge.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau, Building Permits Survey, new privately-owned housing units authorized (PERMIT).
2. Federal Reserve Economic Data (FRED), `PERMIT`, New Privately-Owned Housing Units Authorized by Building Permits.
3. The Conference Board, Leading Economic Index (building permits is a component).
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
        "window 2017-07-31 to 2025-08-31 (98 months). SPY history limits the "
        "usable sample."
    ),
    plain_english=(
        "This page documents how Building Permits YoY was turned into stationary "
        "growth signals, how the econometric checks were run, and how the "
        "tournament selected the final SPY allocation rule -- along with the "
        "honest caveat that the selection maximum is a procyclical long-lead "
        "rule that is direction-consistent with the prior but not yet a "
        "validated edge, and that its return trails buy-and-hold at high "
        "turnover."
    ),
)
