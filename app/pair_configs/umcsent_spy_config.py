"""U. Michigan Expected Business Conditions x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY sentiment pair. The University of Michigan
"expected change in business conditions" survey diffusion (Data Master /
University of Michigan; canonical column `umcsent`) is a forward-looking
consumer-SENTIMENT sub-series and a classic LEADING indicator. Its economic
PRIOR is PROCYCLICAL (rising expected business conditions -> consumer optimism
-> stronger spending / risk-on -> favor SPY). NOTE: this is the expected-
conditions sub-series, DISTINCT from the separate headline "University of
Michigan Consumer Sentiment" used in the umcsent_xlv pair -- use the display
name "U. Michigan Expected Business Conditions" and do not call it headline
consumer sentiment.

Unlike a nominal-dollar level, this diffusion LEVEL is bounded and mean-
reverting, so it is STATIONARY (ADF rejects a unit root, p = 0.0002; KPSS does
not reject stationarity). The tested signals are therefore the level itself and
transforms of it -- level, 1-month change, 12-month change (measured over a
full year), and a 60-month rolling z-score -- NOT growth-rate transforms.

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/umcsent_spy/*:
  - CORRECTION (2026-09): an earlier version of this pair computed the
    "12-month change" signal as a 4-month change (diff(4)) by mistake. With the
    properly computed 12-month change (diff(12), a full year) the tournament
    re-selected the winner as `chg_12m / T_roll_p50 / L9` at OOS Sharpe 1.43
    (up from the buggy 1.23), and every figure below reflects the corrected
    2026-09-12 run.
  - The tournament winner (`chg_12m` 12-month change / T_roll_p50 60-month
    rolling-median threshold / PROCYCLICAL / L9 months / P1_long_cash; OOS
    Sharpe 1.43 vs 0.93 B&H) is the grid maximum over 168 combinations (all 168
    valid). The MEDIAN valid combo scores 0.659 -- it UNDERPERFORMS buy-and-hold
    (0.93) (winner_summary.json).
  - DIRECTION IS CONSISTENT WITH THE PRIOR. Expected-conditions optimism is
    procyclical and a LEADING indicator, and the search also selected a
    PROCYCLICAL rule (hold SPY when the 9-month-lagged 12-month change is at or
    above its 60-month rolling median -- i.e. when year-over-year expectations
    are improving relative to their recent norm).
    `interpretation_metadata.json` records expected_direction procyclical vs
    observed_direction procyclical, direction_consistent = true, confidence =
    low. So the strategy orientation is economically sensible; the caution is
    about validation and lead durability.
  - The concurrent regime evidence does NOT corroborate a clean procyclical
    gradient: sorting months by the expected-conditions level, the strongest-
    optimism quartile Q4 has the LOWEST concurrent SPY Sharpe (0.67) and the
    weakest-optimism Q1 the highest (0.86), with Q2 0.71 and Q3 0.81 -- an
    essentially flat, non-monotone pattern (regime_quartile_returns.csv). The
    direction claim therefore rests on the strategy orientation and the prior,
    not on a concurrent optimism gradient -- another reason confidence is LOW.
  - No lead-lag forecast. The 12-month-change signal does NOT Granger-cause SPY
    at any tested lag (minimum p = 0.22 at lag 5) (granger_by_lag.csv). Linear
    correlation with forward SPY is near zero at every horizon and no cell is
    significant; the largest |r| anywhere is the level vs 6-month-forward SPY
    (r = 0.07, p = 0.17) (core_models_20260912/correlations.csv). Local
    projections are near-null at every horizon (no coefficient significant;
    trivial R^2) (local_projections.csv). Pre-whitened cross-correlation clears
    the confidence band at NO offset; what little structure exists sits on the
    SPY-leads side (|ccf| up to ~0.10 at lag -1, at the band edge), the reverse
    of a forecasting signal, while the optimism-leads side is uniformly small
    (ccf_prewhitened.csv).
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: OOS max drawdown
    -7.6% vs -23.9% for buy-and-hold, at an essentially MATCHED annual return
    (14.8% vs 14.8%) and lower volatility (10.1%) -- read the Sharpe as
    volatility/drawdown avoidance, not a return advantage. Turnover is LOW
    (1.22/yr, 10 OOS trades): the rule flips about once a year.
  - LEAD DURABILITY CAVEAT. The winner uses a 9-month lead (L9) on a survey.
    A 9-month lead on a monthly sentiment series with few cycles in the sample
    needs adjacent-lead durability checking -- and the runner-up
    (`chg_12m / T0_zero / L6`, 1.396) is close but at a different threshold and
    a 6-month lead, so the exact L9 / rolling-median choice is not uniquely
    robust (analyst_suggestions.json).
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam.

MONTHLY conventions: leads in MONTHS (winner L9); Sharpe annualized by
sqrt(12); OOS window 2017-08-31 -> 2025-09-30 (98 months). Numbers sourced from
results/umcsent_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20260912/*,
regime_quartile_returns.csv, subperiod_sharpe.csv, granger_by_lag.csv,
stationarity_tests_20260912.csv, structural_break_umcsent_spy.json,
tournament_results_20260912.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Expected Business Conditions as a Procyclical SPY Overlay"
    PAGE_SUBTITLE = (
        "U. Michigan Expected Business Conditions (Data Master / University of "
        "Michigan) x S&P 500 (SPY), a monthly forward-looking sentiment "
        "diffusion tested against SPY returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.43 OOS versus 0.93 buy-and-hold, direction matches the "
        "procyclical prior -- but the honest headline is the drawdown "
        "(-7.6% vs -23.9%), and this is a found-in-search candidate on a "
        "9-month lead that still needs a fresh holdout"
    )

    PLAIN_ENGLISH = (
        "The University of Michigan expected-change-in-business-conditions "
        "series is a consumer survey diffusion of how households expect the "
        "economy to fare over the year ahead. Because people spend and take "
        "risk on their outlook, it is a forward-looking, LEADING sentiment "
        "indicator, and the economic prior is procyclical: rising optimism "
        "signals expansion and risk-on equities. This pair tests whether that "
        "optimism can improve SPY timing. The winning rule runs the "
        "economically sensible way -- hold SPY when year-over-year optimism is "
        "improving relative to its recent norm -- so its direction matches the "
        "prior. Read the result as a sentiment overlay and drawdown control, "
        "not as a forecast: the formal lead-lag tests find no predictive edge, "
        "the typical rule underperforms buy-and-hold, the concurrent quartile "
        "evidence is flat, and the exact 9-month lead is not robust."
    )

    WHERE_THIS_FITS = (
        "This is a sentiment overlay for broad U.S. equities. It belongs in "
        "the portal as a procyclical context signal: useful for drawdown "
        "control in the searched sample, and pointed the economically sensible "
        "way, but not a standalone forecast. Readers should treat the direction "
        "as sensible (it matches the procyclical prior) but treat the precise "
        "9-month lead with skepticism until adjacent leads and a fresh holdout "
        "confirm it."
    )

    ONE_SENTENCE_THESIS = (
        "Expected-conditions optimism is procyclical BY PRIOR and the search's "
        "best rule -- a procyclical filter at a 9-month lead -- runs that way, "
        "but the concurrent quartile evidence is flat and non-monotone "
        "(strongest-optimism Q4 is the WEAKEST by Sharpe, 0.67 vs Q1 0.86) and "
        "the signal does NOT lead SPY (Granger min p = 0.22; local projections "
        "null; CCF clears the band at no offset), so it is a drawdown-reduction "
        "candidate (-7.6% vs -23.9% max drawdown) that is found-in-search, "
        "underperforms buy-and-hold at the median (0.659 vs 0.93), and rests on "
        "a 9-month lead that needs adjacent-lead durability checking."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 98-month window (2017-08-31 -> 2025-09-30). The winner was found "
        "as the best of 168 valid combinations, and the MEDIAN valid combo "
        "(0.659) UNDERPERFORMS buy-and-hold (0.93) -- the typical rule "
        "subtracts value. The defensible number is the max drawdown "
        "(-7.6% vs -23.9%) at an essentially MATCHED return (14.8% vs 14.8%) "
        "and lower volatility (10.1%) -- read the Sharpe (1.43 vs 0.93) as "
        "volatility/drawdown avoidance, not stock-picking skill. Sharpe ratios "
        "use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "Expected Business Conditions vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the expected-conditions diffusion level (left axis) is "
        "shown with SPY on the same time axis, NBER recessions shaded. Unlike a "
        "price level, this survey series is bounded and mean-reverting (it is "
        "stationary), so it oscillates rather than trending. The traded signal "
        "is its 12-month change (the change over a full year), not the level "
        "itself. Watch the shaded recessions -- optimism sagged into them, as a "
        "leading sentiment gauge typically does."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Expected-Conditions Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest optimism) to Q4 "
        "(strongest), with concurrent SPY Sharpe in each. The pattern is "
        "essentially FLAT and non-monotone: the strongest-optimism quartile Q4 "
        "is actually the LOWEST (Sharpe 0.67) while the weakest-optimism Q1 is "
        "the highest (0.86), with Q2 0.71 and Q3 0.81. So the concurrent regime "
        "evidence does NOT corroborate a clean procyclical gradient -- one "
        "reason confidence is LOW. Descriptive and concurrent, not a tradable "
        "lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **procyclical, 9-month-lagged expected-conditions filter**. It holds SPY when the 12-month change in expected business conditions from nine months earlier was at or above its 60-month rolling median (optimism improving relative to its recent norm), and holds cash otherwise. Out-of-sample (2017-08 to 2025-09), this rule earns a Sharpe of 1.43 versus 0.93 for buy-and-hold, with a maximum drawdown of **-7.6% versus -23.9%** at an essentially matched annualized return of 14.8% versus 14.8%. Read that as the honest headline: the rule's edge is a much shallower worst-case loss and lower volatility, **not** a return advantage. (Correction: an earlier version of this pair rested on a mislabeled 4-month change; with the properly computed 12-month change the winner is `chg_12m / T_roll_p50 / L9` at OOS Sharpe 1.43.)

### The Sentiment Hypothesis

Expected business conditions measures how consumers expect the economy to do over the coming year -- a forward-looking sentiment reading. Because households spend and take risk on their outlook, it is a **leading** indicator, and the economic prior is that optimism is **procyclical**: rising expectations are risk-on for equities; falling expectations are an early sign demand is cooling.

The winning rule runs the **same** way as that prior -- it buys SPY when year-over-year optimism is improving relative to its recent norm -- so direction is consistent with the economic prior (`direction_consistent = true`). But the concurrent regime evidence does **not** corroborate a clean gradient: sorting months by the expected-conditions level, the strongest-optimism quartile Q4 has the *lowest* concurrent SPY Sharpe (0.67), not the highest, and the four quartiles are essentially flat (Q1 0.86, Q2 0.71, Q3 0.81, Q4 0.67). The caution here is not a sign flip; it is validation, a weak concurrent signal, and lead durability.

### Why This Is Not a Forecast

The formal lead-lag tests are blunt. The 12-month change does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.22), forward-return correlations are near zero at every horizon (no significant cell), and local projections are essentially null. The pre-whitened cross-correlation clears the confidence band at no offset, and what little structure exists sits on the *SPY-leads* side -- the reverse of a forecasting signal. So while the winner's *direction* is sensible, its *predictive lead* is not established, and the precise 9-month lag it uses is not robust: a runner-up at a 6-month lead (and a zero threshold) is close behind. This dashboard therefore treats the pair as a searched sentiment overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "Expected conditions softened as the tech bust and 2001 "
                "recession unfolded. The searched rule lost less than "
                "buy-and-hold in this window (subperiod Sharpe -0.19 vs "
                "-0.70), an early piece of its drawdown story, but still fell."
            ),
            "caption": "Dot-Com: optimism sagged; the rule lost less than SPY (-0.19 vs -0.70).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Expected conditions collapsed through 2008-09 as the outlook "
                "darkened. Here the long 9-month lead kept the rule invested "
                "into the decline, and it did WORSE than buy-and-hold "
                "(-1.36 vs -1.03) -- the window where the lag hurt most."
            ),
            "caption": "GFC: the long lead kept it invested; the rule did worse than SPY (-1.36 vs -1.03).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Expected conditions plunged in spring 2020 and rebounded. In "
                "this crash window the rule was in cash (subperiod Sharpe 0.0 "
                "vs -0.08 for SPY), so it sidestepped the loss -- but COVID is "
                "an extreme, exogenous in-window outlier, so read any rule that "
                "leans on it with caution."
            ),
            "caption": "COVID: the rule sat in cash through the crash (0.0 vs -0.08).",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Expected conditions fell to multi-decade lows in 2022 as "
                "inflation bit. Here the rule stepped to cash and avoided the "
                "drawdown (subperiod Sharpe 0.0 vs -0.76 for SPY) -- a "
                "defensive win, though it reflects being flat, not a timed "
                "re-entry."
            ),
            "caption": "2022: the rule sat in cash and avoided the loss (0.0 vs -0.76).",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal defends unevenly and is imperfect as a forecast. Expected conditions fell during the Dot-Com, GFC and COVID recessions. The searched rule lost less than buy-and-hold in the Dot-Com bear (-0.19 vs -0.70), and it was in cash -- so it sidestepped the loss -- through both the COVID crash (0.0 vs -0.08) and the 2022 rate shock (0.0 vs -0.76). But in the GFC it did **worse** than buy-and-hold (-1.36 vs -1.03): the long 9-month lead kept it invested into the decline. The strongest honest reading is not "expected conditions predicts drawdowns"; it is that a lagged, procyclical filter happened to sit in cash during several stress windows, which is where its drawdown advantage was earned -- and in the GFC the lag worked against it.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this sentiment story survives "
        "correlation, lead-lag, regime, and strategy checks. The winner's "
        "direction matches the procyclical prior, but it does not survive as a "
        "forecast: the value is defensive, not predictive, the concurrent "
        "quartiles are flat, and the 9-month lead is not robust."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether the expected-conditions signal and "
        "future SPY returns move together in a roughly linear way."
    ),
    question="Does stronger expected-conditions optimism line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean stronger optimism lines up with stronger future SPY returns; "
        "pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon and no cell is statistically significant. The "
        "largest |r| anywhere is the level vs 6-month-forward SPY (r = 0.07, "
        "p = 0.17) -- not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; "
        "the 12-month-change cells are near zero (|r| <= 0.04), and the largest "
        "cell anywhere is the level vs 6-month-forward SPY at r = 0.07 "
        "(insignificant)."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair. The more "
        "relevant question is whether a lagged optimism filter improves "
        "portfolio behavior in the searched sample."
    ),
    key_message="Expected conditions is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does the expected-conditions signal lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-6 is 0.22 -- the expected-conditions signal does not "
        "Granger-cause SPY returns."
    ),
    observation=(
        "Across the tested monthly lags the signal->SPY p-value never falls "
        "below 0.22; the F-statistics are tiny. There is no formal evidence of "
        "lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal claim. The strategy must be framed as a "
        "searched sentiment overlay, not proof that expected conditions cause "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.22); expected conditions does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the expected-conditions level and "
        "compares concurrent SPY returns across optimism regimes."
    ),
    question="Do weak and strong optimism regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-optimism regime; Q4 is the strongest. Compare "
        "Sharpe, average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: the concurrent Sharpe is essentially FLAT and "
        "non-monotone across optimism regimes -- the strongest-optimism "
        "quartile Q4 is the LOWEST (0.67) and the weakest-optimism Q1 the "
        "highest (0.86), with Q2 0.71 and Q3 0.81. It does NOT corroborate a "
        "clean procyclical gradient."
    ),
    observation=(
        "Concurrent SPY Sharpe is highest in the weakest-optimism quartile "
        "(Q1 0.86) and lowest in the strongest (Q4 0.67), with the middle "
        "buckets in between (Q2 0.71, Q3 0.81) -- a flat, non-monotone pattern."
    ),
    interpretation=(
        "The concurrent pattern does not support a procyclical sentiment "
        "gradient; the winner's procyclical orientation rests on the economic "
        "prior and strategy direction, not on this evidence. It is another "
        "reason to keep confidence LOW."
    ),
    key_message="Concurrent optimism regimes show no clean gradient -- the strongest-optimism quartile is the weakest, so this does not corroborate the procyclical reading.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does the expected-conditions signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "expected conditions leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: no offset clears the confidence band. What little "
        "structure exists sits on the SPY-leads (negative-lag) side (|ccf| up "
        "to ~0.10 at lag -1, right at the band edge), while every optimism-"
        "leads offset is small (<= 0.04). That is the reverse of a forecasting "
        "signal."
    ),
    observation=(
        "No cross-correlation is statistically significant at any offset; the "
        "largest values are on the SPY-leads side (|ccf| ~0.10 at lag -1, "
        "~0.08 at lag -6) and the optimism-leads side is uniformly small."
    ),
    interpretation=(
        "There is no coherent window in which expected conditions foreshadows "
        "SPY. If anything the (insignificant) structure runs the other way "
        "(markets anticipating sentiment), which argues against an expected-"
        "conditions forecast of SPY."
    ),
    key_message="No offset is significant; the largest correlation is on the SPY-leads side, so expected conditions shows no forecasting lead over SPY.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the expected-conditions signal."
    ),
    question="How does SPY respond after expected conditions changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "expected-conditions signal. Coefficients near zero mean no detectable "
        "effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across all "
        "horizons (1, 3, 6 months), none statistically significant "
        "(p from 0.43 to 0.91), with negligible R^2."
    ),
    observation=(
        "Point estimates are near zero at every horizon and no coefficient is "
        "significant; the explained variance is trivial throughout."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. "
        "Nothing here rescues a forward-looking reading of the indicator."
    ),
    key_message="Local projections are null; expected conditions carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the expected-conditions signal "
        "matters differently in weak, normal, and strong SPY return "
        "environments."
    ),
    question="Does expected conditions behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is close to zero and flat across "
        "quantiles -- no material tail sensitivity for the expected-conditions "
        "signal."
    ),
    observation=(
        "The estimated coefficient is small and essentially unchanged across "
        "the tested quantiles, consistent with the near-null correlation and "
        "local-projection results."
    ),
    interpretation=(
        "Expected conditions does not flag elevated crash risk or exceptional "
        "upside -- there is no tail channel to trade."
    ),
    key_message="Expected conditions shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Direction Matches the Procyclical Prior, but It Does Not Forecast SPY",
    "overview": (
        "The evidence supports a cautious sentiment overlay -- and nothing "
        "stronger. The strategy winner improves search-phase OOS Sharpe and "
        "its direction is procyclical, matching the prior, but the concurrent "
        "quartiles are flat, formal lead-lag evidence is absent (Granger min "
        "p = 0.22; local projections null; CCF clears the band at no offset), "
        "and the exact 9-month lead is not robust (a 6-month-lead runner-up is "
        "close behind)."
    ),
    "plain_english": (
        "This page asks whether expected conditions helps time SPY. The answer "
        "is: not as a forecast. The winning rule's direction matches the "
        "procyclical prior, but the concurrent quartiles are flat (the "
        "strongest-optimism bucket is not the best) and the causal tests find "
        "no lead. Treat it as a defensive, procyclical-by-prior overlay, not an "
        "early-warning system, and be skeptical of the precise 9-month lag."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 168 strategy combinations (all 168 valid) "
        "across four expected-conditions transforms (level, 1-month change, "
        "12-month change, 60-month rolling z-score), fixed and rolling "
        "thresholds, a long/cash strategy, and leads from 0 to 12 months. The "
        "selected winner is `chg_12m / T_roll_p50 / P1_long_cash procyclical / "
        "L9`, with OOS Sharpe 1.43. The MEDIAN valid combo scores 0.659 -- "
        "below buy-and-hold's 0.93 -- and the runner-up (`chg_12m / T0_zero / "
        "P1_long_cash / L6`, 1.396) is close behind but at a different "
        "threshold and a 6-month lead, so the exact 9-month lead is a fragile "
        "choice rather than a robust economic edge."
    ),
    "transition": (
        "**Transition:** the evidence is a procyclical-by-prior overlay that "
        "matches the direction, not causation. The Strategy page shows the "
        "exact long/cash rule, the drawdown advantage that is its real virtue, "
        "and the deployment caveats -- including the lead-durability caution."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical, Lagged Expected-Conditions Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 12-month change in expected "
        "business conditions, a 60-month rolling-median threshold, a "
        "procyclical orientation, and a 9-month lead -- valued for drawdown "
        "reduction, not for its Sharpe, and flagged as resting on a lead that "
        "needs durability checking."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 12-month change in expected business "
        "conditions from nine months earlier was at or above its 60-month "
        "rolling median (optimism improving relative to its recent norm); "
        "otherwise it holds cash. This is a lagged, PROCYCLICAL sentiment "
        "filter -- consistent with the prior for a leading indicator -- not a "
        "real-time recession forecast. Judge it by its shallower drawdown "
        "(-7.6% vs -23.9%) and lower volatility, not by the headline Sharpe."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/umcsent_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/umcsent_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/umcsent_spy/tournament_results_20260912.csv"},
        {"label": "Stationarity tests", "path": "results/umcsent_spy/stationarity_tests_20260912.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 12-month change in expected business conditions, taken from nine months earlier, was at or above its 60-month rolling median (i.e. when year-over-year optimism was *improving* relative to its recent norm); otherwise hold cash. This is a procyclical rule and runs the same way as the economic prior.

If-then form:
- **IF** `umcsent_chg_12m` from 9 months earlier is at or above its 60-month rolling median -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-08-31 to 2025-09-30, 98 months): Sharpe 1.43 versus 0.93 buy-and-hold; annualized return 14.8% versus 14.8%; **maximum drawdown -7.6% versus -23.9%**; annualized volatility 10.1%; win rate 43.9%; 10 trades; annual turnover 1.22 (low). The drawdown and volatility reduction, not the Sharpe or the (essentially matched) return, is the defensible result.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the University of Michigan expected-change-in-business-conditions diffusion (`umcsent`) at month-end. Second, it computes the 12-month change (`umcsent_chg_12m`, the level today minus the level twelve months earlier -- now correctly measured over a full year). Third, it applies a 9-month lag before the SPY allocation is set. Finally, the lagged signal is compared with its 60-month rolling median: when the lagged 12-month change is at or above that rolling median, hold SPY; otherwise cash (the procyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return (below half here partly because the rule holds cash for stretches).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the U. Michigan expected-conditions diffusion (`umcsent`) at month end.
2. Compute the 12-month change (today's level minus the level twelve months earlier).
3. Take the value from 9 months earlier and compare it with its 60-month rolling median.
4. Hold SPY when that lagged 12-month change was at or above its rolling median; otherwise hold cash.
5. Recheck monthly. Turnover is low (1.22/yr): the rule flips about once a year.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule loses LESS in the Dot-Com bear "
        "(-0.19 vs -0.70) and sits in cash -- avoiding the loss -- through the "
        "COVID crash (0.0 vs -0.08) and the 2022 rate shock (0.0 vs -0.76), but "
        "it does WORSE than buy-and-hold in the GFC (-1.36 vs -1.03) because "
        "the long lead kept it invested. The stress defense is real but not "
        "universal."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the expected-conditions signal; "
            "the target is SPY returns. The rolling correlation tests whether "
            "their linear relationship is stable through time. Large swings "
            "mean the relationship is unstable and the rule needs ongoing "
            "monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "expected-conditions/SPY relationship changes enough that one "
            "fixed model is unlikely to describe the whole sample. A larger "
            "break statistic means the relationship shifted more materially "
            "across periods (here the max absolute rolling-correlation z-score "
            "reaches 3.1)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.43) is a right-tail maximum; the "
        "median valid combo (0.659) sits BELOW buy-and-hold (0.93), so the "
        "typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The result is marked `found_in_search`; the median valid combo underperforms buy-and-hold, and the winner still needs a frozen-rule holdout confirmation before it can be called deployable. Confidence is LOW.
2. The winner uses a 9-month lead (L9) on a monthly survey with few cycles in the sample. A 9-month lead needs adjacent-lead durability checking -- and the runner-up at a 6-month lead (`chg_12m / T0_zero / L6`, 1.396) is close behind at a different threshold, so the precise 9-month choice is fragile.
3. Granger causality is insignificant at every lag (min p = 0.22), local projections are null, and the pre-whitened CCF clears the band at no offset (the largest values are on the SPY-leads side) -- so this is not a proven causal forecast, even though the direction is sensible.
4. The defensible virtue is drawdown and volatility reduction, not return: the annualized return (14.8%) is essentially matched to buy-and-hold (14.8%), so read the Sharpe as volatility/drawdown avoidance.
5. The stress defense is uneven: the rule did WORSE than buy-and-hold in the GFC (-1.36 vs -1.03) because the long lead kept it invested into the decline.
6. Corrected pair: an earlier winner rested on a mislabeled 4-month change; with the properly computed 12-month change the winner is `chg_12m / T_roll_p50 / L9` at OOS Sharpe 1.43.
7. This is the University of Michigan *expected business conditions* sub-series (forward-looking), distinct from the headline consumer-sentiment index; do not conflate the two.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 9-month-lagged 12-month change in expected conditions "
        "crossed at or above its 60-month rolling median, taking exposure from "
        "0% to 100% SPY. A SELL moves back to cash when the lagged 12-month "
        "change fell below its rolling median."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1996-09-30",
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
| Indicator | Data Master (University of Michigan) | `UMCSENT`, U. Michigan Expected Business Conditions (forward-looking survey diffusion) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the University of Michigan expected-change-in-"
    "business-conditions diffusion (a forward-looking sentiment sub-series, "
    "distinct from the headline consumer-sentiment index). Unlike a "
    "nominal-dollar price level, this survey diffusion is bounded and "
    "mean-reverting, so the LEVEL itself is stationary (ADF rejects a unit "
    "root, p = 0.0002; KPSS does not reject stationarity). The pipeline "
    "constructs the level, its 1-month change, its 12-month change, and a "
    "60-month rolling z-score -- all stationary. The winning signal is "
    "`umcsent_chg_12m`, the 12-month change (now correctly measured over a "
    "full year; an earlier version mislabeled a 4-month change), used with a "
    "9-month lead, a 60-month rolling-median threshold, and a procyclical "
    "orientation (long SPY when the lagged 12-month change is at or above its "
    "rolling median)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the expected-conditions signal move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong optimism regimes behave differently? | Makes the procyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past expected-conditions information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: expected-conditions transforms (level, 1-month change, 12-month change, 60-month rolling z-score) x fixed and rolling thresholds x a long/cash strategy x procyclical/countercyclical orientations x lead times (0-12 months). The final tournament has 168 combinations, all 168 valid. The winning rule is `umcsent_chg_12m / T_roll_p50 / P1_long_cash procyclical / L9`, the maximum OOS Sharpe (1.43). The median valid combo (0.659) underperforms buy-and-hold (0.93), and the runner-up (`chg_12m / T0_zero / P1_long_cash / L6`, 1.396) is close behind but at a different threshold and a 6-month lead -- read the winner as a selection maximum whose exact 9-month lead is fragile, not a validated edge. The winner's direction is procyclical, consistent with the leading-indicator prior (`direction_consistent = true`).
"""

_REFERENCES_MD = """
1. University of Michigan, Surveys of Consumers, expected change in business conditions (index of consumer expectations component).
2. Federal Reserve Economic Data (FRED), `UMCSENT`, University of Michigan: Consumer Sentiment (parent survey).
3. The Conference Board, Leading Economic Index (consumer expectations is a component).
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
        "Monthly sample from 1993-01-31 to 2025-09-30, with out-of-sample "
        "window 2017-08-31 to 2025-09-30 (98 months). SPY history limits the "
        "usable sample even though the survey begins earlier."
    ),
    plain_english=(
        "This page documents how the U. Michigan expected-conditions diffusion "
        "was turned into stationary signals (its level is already stationary), "
        "how the econometric checks were run, and how the tournament selected "
        "the final SPY allocation rule -- along with the honest caveat that the "
        "selection maximum is a procyclical rule whose direction is sensible "
        "but whose 9-month lead is fragile and not yet a validated edge."
    ),
)
