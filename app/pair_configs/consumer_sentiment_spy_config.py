"""U. Michigan headline Consumer Sentiment x SPY pair configuration (Rule APP-PT1).

NEW pair, MONTHLY sentiment pair. The University of Michigan Index of Consumer
Sentiment (FRED series `UMCSENT`, the HEADLINE index, range ~50-112; canonical
column `umcsent`) is the classic consumer-confidence gauge and a LEADING
sentiment indicator. Its economic PRIOR is PROCYCLICAL (rising sentiment ->
consumer optimism -> stronger spending / risk-on -> favor SPY).

WHY THIS PAIR EXISTS. Headline consumer sentiment was previously paired only
with XLV (`umcsent_xlv`); the SPY slot carried a DIFFERENT Michigan series --
the "expected change in business conditions" diffusion (`umcsent_spy`, range
~13-58). This pair fills the gap: the HEADLINE sentiment index against SPY.
`umcsent_spy` and `umcsent_xlv` are left untouched; read this alongside them.

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, not a validated
edge. Every number below is sourced from results/consumer_sentiment_spy/*:
  - The tournament winner is `diff_1m` (1-month change) / `T_roll_p75` (60-month
    rolling 75th-percentile threshold) / COUNTERCYCLICAL / L12 months /
    P1_long_cash; OOS Sharpe 1.25 vs 0.95 B&H over 101 months
    (2018-04-30 -> 2026-08-31). It is the grid maximum over 312 combinations
    (all 312 valid). The MEDIAN valid combo scores 0.68 -- it UNDERPERFORMS
    buy-and-hold (0.95) (winner_summary.json).
  - DIRECTION CONTRADICTS THE PRIOR. The economic prior is procyclical, but the
    search selected a COUNTERCYCLICAL rule: hold SPY when the 1-month change in
    sentiment is AT OR BELOW its 60-month rolling 75th percentile, and step to
    cash when sentiment momentum is in its top quartile. Economically this is a
    "fade the euphoria" / mean-reversion reading (extreme positive sentiment
    surges precede weaker equity months), which is a coherent BEHAVIORAL story
    -- but it is the OPPOSITE of the naive procyclical prior.
    `interpretation_metadata.json` records expected_direction procyclical vs
    observed_direction countercyclical, direction_consistent = FALSE, confidence
    = low. The direction is a result to be explained, not a confirmation.
  - THE HEADLINE LEVEL IS NON-STATIONARY. Unlike the bounded expected-conditions
    diffusion, the headline sentiment LEVEL carries a multi-decade drift: ADF
    does NOT reject a unit root (p = 0.68) and KPSS rejects stationarity. The
    traded signal is therefore the 1-month CHANGE (`umcsent_diff_1m`), which IS
    stationary (ADF p ~ 1e-16; KPSS does not reject). Do not trade the level.
  - NO FORMAL LEAD-LAG. The 1-month change does NOT Granger-cause SPY at any
    tested lag (minimum p = 0.135 at lag 6) (granger_by_lag.csv).
  - There IS modest, horizon-dependent linear content, but it runs PROCYCLICAL,
    not countercyclical: the 60-month z-score and the 12-month change correlate
    positively and significantly with 3-6 month forward SPY (largest r = 0.19
    for the z-score vs 6-month-forward SPY, p = 0.0002; 12-month change vs
    6-month-forward r = 0.17, p = 0.0008) (core_models_20261009/correlations.csv,
    local_projections.csv). So the (weak) forecasting sign disagrees with the
    traded countercyclical rule -- another reason confidence is LOW.
  - The concurrent regime evidence (quartiles by 12-month change) is
    non-monotone: sorting months by the 12-month change, the most-negative
    quartile Q1 has the lowest concurrent SPY Sharpe (-0.04) while the middle/
    upper quartiles are higher (Q2 1.38, Q3 0.91, Q4 1.34)
    (regime_quartile_returns.csv).
  - Re-shuffle (bootstrap) significance IS present: the winner's OOS Sharpe
    beats the resampled distribution with p = 0.003 (bootstrap.csv) -- stronger
    than most pairs -- but a low bootstrap p on a selection maximum is a
    necessary, not sufficient, condition; the final exam is still owed.
  - THE PERFORMANCE EDGE IS MODEST ON BOTH AXES: OOS annualized return 17.9% vs
    15.3% and max drawdown -20.3% vs -23.9% -- a small return advantage and a
    small drawdown improvement, at higher turnover (4.3/yr, 36 OOS trades): the
    rule flips about four times a year, so costs matter.
  - LEAD DURABILITY CAVEAT. The winner uses a 12-month lead (L12), the TOP of
    the floored grid [1..13]. The runner-up (`diff_1m / T_roll_p50 / L12`, 1.24)
    shares the same signal and lead at an adjacent threshold, so the signal/lead
    choice is fairly stable but the exact threshold is not uniquely robust
    (analyst_suggestions.json). A 12-month lead on a monthly survey with few
    cycles needs adjacent-lead durability checking.
  - Status is `found_in_search` (evidence_status.json): the winner still needs a
    frozen-rule holdout / final exam.

MONTHLY conventions: leads in MONTHS, FLOORED to L1 (#255 publication-lag
discipline; searched grid is the contiguous shifted grid [1..13]); winner L12.
Sharpe annualized by sqrt(12); OOS window 2018-04-30 -> 2026-08-31 (101 months).
Numbers sourced from results/consumer_sentiment_spy/ (winner_summary.json,
kpis.json, evidence_status.json, interpretation_metadata.json,
core_models_20261009/*, regime_quartile_returns.csv, subperiod_sharpe.csv,
granger_by_lag.csv, stationarity_tests_20261009.csv,
structural_break_consumer_sentiment_spy.json, tournament_results_20261009.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: U. Michigan Consumer Sentiment as a Countercyclical SPY Overlay"
    PAGE_SUBTITLE = (
        "U. Michigan headline Consumer Sentiment (FRED UMCSENT) x S&P 500 (SPY), "
        "a monthly sentiment index tested against SPY returns. NEW pair -- read "
        "alongside umcsent_xlv (same series vs XLV) and umcsent_spy (the "
        "expected-business-conditions diffusion vs SPY)."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.25 OOS versus 0.95 buy-and-hold with a significant re-shuffle "
        "test (p = 0.003) -- but the winning rule is COUNTERCYCLICAL, the OPPOSITE "
        "of the sentiment prior, it does not Granger-lead SPY, and it is a "
        "found-in-search candidate on a 12-month lead that still needs a holdout"
    )

    PLAIN_ENGLISH = (
        "The University of Michigan Index of Consumer Sentiment is the classic "
        "gauge of how optimistic households feel about the economy. The intuitive "
        "prior is procyclical: more optimism should mean more spending and "
        "risk-on equities. This pair tests whether headline sentiment can improve "
        "SPY timing -- and the search's answer is a surprise. The winning rule is "
        "COUNTERCYCLICAL: it holds SPY in most months but steps to cash when the "
        "one-month jump in sentiment is in its top quartile, i.e. it FADES "
        "sentiment euphoria. That is a coherent mean-reversion story, but it runs "
        "opposite to the naive prior, so read the direction as a finding to "
        "explain, not a confirmation. The rule beats buy-and-hold modestly on "
        "both return and drawdown and clears a re-shuffle significance test, but "
        "it shows no formal forecasting lead, the typical rule underperforms "
        "buy-and-hold, and the exact 12-month lead needs a fresh holdout."
    )

    WHERE_THIS_FITS = (
        "This is a headline-sentiment overlay for broad U.S. equities, and a "
        "method-comparison companion to two existing pairs: umcsent_xlv (the same "
        "UMCSENT series against healthcare XLV) and umcsent_spy (a different "
        "Michigan series -- expected business conditions -- against SPY). Its "
        "place in the portal is a cautious, contrarian sentiment context signal: "
        "it clears a bootstrap test and improves portfolio behavior modestly in "
        "the searched sample, but its countercyclical direction contradicts the "
        "prior and it is not a validated forecast."
    )

    ONE_SENTENCE_THESIS = (
        "Headline consumer sentiment is procyclical BY PRIOR, but the search's "
        "best SPY rule is COUNTERCYCLICAL -- fade top-quartile sentiment surges, "
        "at a 12-month lead -- and although it beats buy-and-hold (Sharpe 1.25 vs "
        "0.95) with a significant re-shuffle test (p = 0.003) and a modest edge "
        "on both return (17.9% vs 15.3%) and drawdown (-20.3% vs -23.9%), it does "
        "NOT Granger-lead SPY (min p = 0.135), its (weak, significant) linear "
        "content runs the OTHER way (procyclical, r up to 0.19 at 6 months), the "
        "median valid combo underperforms buy-and-hold (0.68 vs 0.95), and it "
        "rests on a found-in-search 12-month lead that needs a final exam."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 101-month window (2018-04-30 -> 2026-08-31). The winner was found "
        "as the best of 312 valid combinations, and the MEDIAN valid combo "
        "(0.68) UNDERPERFORMS buy-and-hold (0.95) -- the typical rule subtracts "
        "value. The winner's edge is modest on BOTH axes: return 17.9% vs 15.3% "
        "and max drawdown -20.3% vs -23.9%, at higher turnover (4.3/yr). The "
        "re-shuffle (bootstrap) p-value is 0.003 (significant), but on a "
        "selection maximum that is necessary, not sufficient. Sharpe ratios use "
        "monthly sqrt(12) annualization."
    )

    HERO_TITLE = "U. Michigan Consumer Sentiment vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the headline consumer-sentiment index (left axis) is "
        "shown with SPY on the same time axis, NBER recessions shaded. Note the "
        "multi-decade drift in the level -- unlike the bounded expected-"
        "conditions diffusion, this headline LEVEL is non-stationary, so the "
        "traded signal is its 1-month change, not the level itself. Sentiment "
        "sagged into the shaded recessions, as a leading sentiment gauge "
        "typically does."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Sentiment-Change Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted by the 12-month change in sentiment, "
        "from Q1 (biggest decline) to Q4 (biggest rise), with concurrent SPY "
        "Sharpe in each. The pattern is non-monotone: the most-negative quartile "
        "Q1 has the LOWEST concurrent SPY Sharpe (-0.04) while the middle and "
        "upper quartiles are higher (Q2 1.38, Q3 0.91, Q4 1.34). That concurrent "
        "gradient leans procyclical, which sits awkwardly next to the winner's "
        "countercyclical traded rule -- one reason confidence is LOW. Descriptive "
        "and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **countercyclical, 12-month-lagged sentiment-momentum filter**. It holds SPY when the one-month change in consumer sentiment from twelve months earlier was at or below its 60-month rolling 75th percentile, and moves to cash when that one-month change is in its top quartile (a sentiment surge). Out-of-sample (2018-04 to 2026-08, 101 months), this rule earns a Sharpe of 1.25 versus 0.95 for buy-and-hold, with an annualized return of **17.9% versus 15.3%** and a maximum drawdown of **-20.3% versus -23.9%**. The edge is real but modest on both axes, and it comes at higher turnover (4.3 trades/yr).

### The Sentiment Hypothesis -- and the Surprise

Headline consumer sentiment measures household optimism, and the economic prior is **procyclical**: more optimism should be risk-on for equities. The search, however, selected a **countercyclical** rule -- it *fades* top-quartile sentiment surges. That is a coherent mean-reversion / behavioral story (euphoric one-month jumps in sentiment have tended to precede weaker equity months in this sample), but it is the **opposite** of the naive prior, so `direction_consistent = false`. We report the direction as a finding to be explained, not as a confirmation of the sentiment hypothesis.

Complicating the picture, the (weak but statistically significant) linear forecasting content runs the **procyclical** way: the 60-month z-score and the 12-month change correlate positively with 3-6 month forward SPY (largest r = 0.19 for the z-score at six months, p = 0.0002). So the small amount of genuine predictive signal points one way while the traded rule points the other -- a tension that keeps confidence LOW.

### Why This Is Not (Yet) a Validated Edge

The formal lead-lag test is blunt: the one-month change does **not** Granger-cause SPY at any tested lag (minimum p = 0.135). The concurrent quartile gradient is non-monotone. The median valid combo (0.68) underperforms buy-and-hold (0.95), so the typical rule built on this indicator subtracts value. The winner does clear a re-shuffle (bootstrap) significance test (p = 0.003), and its runner-up shares the same signal and 12-month lead at an adjacent threshold (1.24) -- so the signal and lead are fairly stable -- but a 12-month lead sits at the top of the floored grid and still needs adjacent-lead durability checking and a frozen-rule final exam. Treat this as a searched, contrarian sentiment overlay with a promising bootstrap, not a proven forecast.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "Sentiment softened as the tech bust and 2001 recession "
                "unfolded. The searched rule lost less than buy-and-hold in this "
                "window (subperiod Sharpe -0.55 vs -0.70), an early piece of its "
                "defensive story, but still fell."
            ),
            "caption": "Dot-Com: sentiment sagged; the rule lost less than SPY (-0.55 vs -0.70).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Sentiment collapsed through 2008-09 as the outlook darkened. "
                "The rule lost less than buy-and-hold here (subperiod Sharpe "
                "-0.65 vs -1.03), though it still took a loss -- the long lead "
                "limits how early it can step aside."
            ),
            "caption": "GFC: the rule lost less than SPY (-0.65 vs -1.03).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Sentiment plunged in spring 2020 and rebounded. In this window "
                "the rule's best stretch shows up (subperiod Sharpe +1.81 vs "
                "-0.08 for SPY) -- but COVID is an extreme, exogenous in-window "
                "outlier, so read any rule that leans on it with caution."
            ),
            "caption": "COVID: the rule's best window (+1.81 vs -0.08), but an extreme outlier.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Sentiment fell to multi-decade lows in 2022 as inflation bit. "
                "The rule lost less than buy-and-hold (subperiod Sharpe -0.33 vs "
                "-0.76) -- a partial defensive win, not a clean sidestep."
            ),
            "caption": "2022: the rule lost less than SPY (-0.33 vs -0.76).",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show an uneven but consistently *less-bad* defense. Across the Dot-Com bear (-0.55 vs -0.70), the GFC (-0.65 vs -1.03) and the 2022 rate shock (-0.33 vs -0.76), the countercyclical rule lost less than buy-and-hold, and in the COVID window it posted its strongest stretch (+1.81 vs -0.08). The honest reading is not "sentiment predicts drawdowns"; it is that a contrarian, lagged filter that fades sentiment surges happened to carry lighter exposure into several stress windows, which is where its modest drawdown advantage was earned -- with COVID, an exogenous outlier, flattering the average.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this contrarian sentiment story survives "
        "correlation, lead-lag, regime, and strategy checks. It clears a "
        "bootstrap test, but its countercyclical direction contradicts the prior, "
        "the small genuine linear signal runs the other (procyclical) way, formal "
        "lead-lag causality is absent, and the 12-month lead needs a holdout."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether the sentiment signal and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does stronger consumer sentiment line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values mean "
        "stronger/rising sentiment lines up with stronger future SPY returns; "
        "pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the association is weak but, for two transforms at "
        "longer horizons, statistically significant and POSITIVE (procyclical). "
        "The largest |r| anywhere is the 60-month z-score vs 6-month-forward SPY "
        "(r = 0.19, p = 0.0002); the 12-month change vs 6-month-forward is "
        "r = 0.17 (p = 0.0008). The 1-month change (the traded signal) is near "
        "zero."
    ),
    observation=(
        "The strongest linear cells are the 60-month z-score and the 12-month "
        "change against 3-6 month forward SPY (positive, significant); the "
        "traded 1-month change shows little linear association at any horizon."
    ),
    interpretation=(
        "There is modest, horizon-dependent procyclical content -- but it lives "
        "in different transforms than the traded (countercyclical, 1-month-change) "
        "rule, so correlation alone does not validate the winner and points the "
        "other way directionally."
    ),
    key_message="Weak but significant POSITIVE (procyclical) correlation at 3-6 months -- opposite to the traded countercyclical rule.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does the sentiment signal lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-6 is 0.135 -- the sentiment signal does not Granger-cause "
        "SPY returns."
    ),
    observation=(
        "Across the tested monthly lags the signal->SPY p-value never falls "
        "below 0.135; the F-statistics are small. There is no formal evidence of "
        "lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal claim. The strategy must be framed as a "
        "searched sentiment overlay, not proof that sentiment causes future SPY "
        "returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.135); sentiment does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the 12-month change in sentiment and "
        "compares concurrent SPY returns across regimes."
    ),
    question="Do falling-sentiment and rising-sentiment regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the biggest-decline regime; Q4 is the biggest-rise. Compare "
        "Sharpe, average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: concurrent Sharpe is non-monotone -- the most-negative "
        "quartile Q1 is the LOWEST (-0.04) while the middle/upper quartiles are "
        "higher (Q2 1.38, Q3 0.91, Q4 1.34). The concurrent gradient leans "
        "procyclical, which sits awkwardly next to the winner's countercyclical "
        "rule."
    ),
    observation=(
        "Concurrent SPY Sharpe is lowest when sentiment is falling hardest "
        "(Q1 -0.04) and higher in the other quartiles (Q2 1.38, Q3 0.91, "
        "Q4 1.34) -- a non-monotone, broadly procyclical concurrent pattern."
    ),
    interpretation=(
        "The concurrent pattern leans procyclical, the opposite of the traded "
        "countercyclical rule. It neither cleanly supports nor refutes the "
        "winner; it is another reason to keep confidence LOW."
    ),
    key_message="Concurrent gradient leans procyclical (worst when sentiment falls hardest) -- opposite to the traded countercyclical rule.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does the sentiment signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "sentiment leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the cross-correlation structure is small at every "
        "offset. There is no clean, large sentiment-leads spike that would mark a "
        "strong forecasting signal."
    ),
    observation=(
        "Cross-correlations are small across offsets; no offset shows a large, "
        "clean sentiment-leads correlation."
    ),
    interpretation=(
        "There is no coherent window in which the 1-month sentiment change "
        "strongly foreshadows SPY, consistent with the insignificant Granger "
        "result."
    ),
    key_message="No offset shows a strong sentiment-leads spike; the lead-lag echo is weak.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the sentiment signal."
    ),
    question="How does SPY respond after sentiment changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "sentiment signal. Coefficients near zero mean no detectable effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are positive and rise with horizon, "
        "becoming significant by 3-6 months (3m p = 0.014; 6m p = 0.0008), "
        "though the explained variance stays small (R^2 ~ 0.03 at 6 months)."
    ),
    observation=(
        "Point estimates are positive and grow with horizon; the 3- and 6-month "
        "responses are statistically significant, with small R^2."
    ),
    interpretation=(
        "There is modest, procyclical linear predictive content at 3-6 months -- "
        "directionally opposite to the traded countercyclical rule, and small in "
        "magnitude, so it does not by itself validate the winner."
    ),
    key_message="Modest, significant POSITIVE (procyclical) response at 3-6 months -- small, and opposite to the traded rule.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the sentiment signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does sentiment behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is small across quantiles -- no large "
        "tail sensitivity for the sentiment signal, consistent with the modest "
        "overall linear content."
    ),
    observation=(
        "The estimated coefficient is small across the tested quantiles, "
        "consistent with the near-null short-horizon correlation."
    ),
    interpretation=(
        "Sentiment does not flag a strong tail channel to trade; the usable "
        "content, such as it is, is the modest 3-6 month mean response."
    ),
    key_message="No material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: A Contrarian Rule That Clears a Bootstrap but Contradicts the Prior",
    "overview": (
        "The evidence supports a cautious, contrarian sentiment overlay -- and "
        "nothing stronger. The strategy winner improves search-phase OOS Sharpe "
        "and clears a re-shuffle test (p = 0.003), but its direction is "
        "COUNTERCYCLICAL (opposite the prior), the small genuine linear content "
        "runs the other (procyclical) way, formal lead-lag causality is absent "
        "(Granger min p = 0.135), the concurrent quartiles lean procyclical, and "
        "the exact 12-month lead needs a holdout."
    ),
    "plain_english": (
        "This page asks whether headline consumer sentiment helps time SPY. The "
        "answer is: maybe, but contrarily and not as a forecast. The winning "
        "rule fades sentiment surges (countercyclical), which contradicts the "
        "procyclical prior; the small amount of genuine linear signal actually "
        "points procyclical; and the causal tests find no lead. The rule does "
        "clear a bootstrap test, so treat it as a promising-but-unvalidated "
        "contrarian overlay, not an early-warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 312 strategy combinations (all 312 valid) across "
        "four sentiment transforms (level, 1-month change, 12-month change, "
        "60-month rolling z-score), fixed and rolling thresholds, a long/cash "
        "strategy, procyclical/countercyclical orientations, and leads from 1 to "
        "13 months (floored to L1 per the #255 publication-lag standard). The "
        "selected winner is `diff_1m / T_roll_p75 / P1_long_cash countercyclical "
        "/ L12`, with OOS Sharpe 1.25. The MEDIAN valid combo scores 0.68 -- "
        "below buy-and-hold's 0.95 -- and the runner-up (`diff_1m / T_roll_p50 / "
        "L12`, 1.24) shares the same signal and lead at an adjacent threshold, so "
        "the signal/lead pairing is fairly stable but the threshold is not "
        "uniquely robust."
    ),
    "transition": (
        "**Transition:** the evidence is a contrarian overlay with a significant "
        "bootstrap but a direction that contradicts the prior. The Strategy page "
        "shows the exact long/cash rule, the modest return and drawdown edge, and "
        "the deployment caveats -- including the direction and lead-durability "
        "cautions."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Countercyclical, Lagged Sentiment-Momentum Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 1-month change in U. Michigan "
        "consumer sentiment, a 60-month rolling 75th-percentile threshold, a "
        "COUNTERCYCLICAL orientation (fade sentiment surges), and a 12-month lead "
        "-- a found-in-search candidate that clears a bootstrap but contradicts "
        "the procyclical prior."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 1-month change in consumer sentiment from "
        "twelve months earlier was at or below its 60-month rolling 75th "
        "percentile; otherwise (when sentiment momentum is in its top quartile) "
        "it holds cash. This is a lagged, COUNTERCYCLICAL filter that fades "
        "sentiment euphoria -- the OPPOSITE of the procyclical prior for a "
        "leading indicator. Judge it by its modest edge on both return "
        "(17.9% vs 15.3%) and drawdown (-20.3% vs -23.9%), and weigh its higher "
        "turnover and unvalidated 12-month lead."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/consumer_sentiment_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/consumer_sentiment_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/consumer_sentiment_spy/tournament_results_20261009.csv"},
        {"label": "Stationarity tests", "path": "results/consumer_sentiment_spy/stationarity_tests_20261009.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 1-month change in consumer sentiment, taken from twelve months earlier, was at or below its 60-month rolling 75th percentile (i.e. when sentiment was *not* surging); step to cash when that lagged 1-month change is in its top quartile. This is a countercyclical rule -- it runs OPPOSITE to the procyclical prior, fading sentiment euphoria.

If-then form:
- **IF** `umcsent_diff_1m` from 12 months earlier is at or below its 60-month rolling 75th percentile -> hold SPY.
- **ELSE** (sentiment surge) -> hold cash.

Search-phase OOS results (2018-04-30 to 2026-08-31, 101 months): Sharpe 1.25 versus 0.95 buy-and-hold; annualized return 17.9% versus 15.3%; maximum drawdown **-20.3% versus -23.9%**; annualized volatility 14.0%; win rate 55.5%; 36 trades; annual turnover 4.3 (moderate-to-high). The edge is modest on both return and drawdown; the higher turnover means transaction costs matter.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the University of Michigan headline Consumer Sentiment index (`umcsent`, FRED `UMCSENT`) at month-end. Second, it computes the 1-month change (`umcsent_diff_1m`, this month's level minus last month's). Third, it applies a 12-month lag before the SPY allocation is set. Finally, the lagged signal is compared with its 60-month rolling 75th percentile: when the lagged 1-month change is at or below that rolling threshold, hold SPY; when it is above (a top-quartile sentiment surge), hold cash (the countercyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the U. Michigan headline Consumer Sentiment index (`umcsent`) at month end.
2. Compute the 1-month change (this month's level minus last month's).
3. Take the value from 12 months earlier and compare it with its 60-month rolling 75th percentile.
4. Hold SPY when that lagged 1-month change was at or below its rolling 75th percentile; otherwise (a sentiment surge) hold cash.
5. Recheck monthly. Turnover is moderate-to-high (4.3/yr): the rule flips about four times a year.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod "
        "chart compares the searched rule with buy-and-hold SPY during major "
        "stress windows. The rule loses LESS than buy-and-hold in the Dot-Com "
        "bear (-0.55 vs -0.70), the GFC (-0.65 vs -1.03) and the 2022 rate shock "
        "(-0.33 vs -0.76), and posts its strongest stretch in the COVID window "
        "(+1.81 vs -0.08) -- though COVID is an extreme outlier. The stress "
        "defense is consistent but modest outside COVID."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the sentiment signal; the target "
            "is SPY returns. The rolling correlation tests whether their linear "
            "relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "sentiment/SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship shifted more materially across periods (here "
            "the max absolute rolling-correlation z-score reaches 2.1)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.25) is a right-tail maximum; the "
        "median valid combo (0.68) sits BELOW buy-and-hold (0.95), so the typical "
        "rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The result is marked `found_in_search`; the median valid combo underperforms buy-and-hold, and the winner still needs a frozen-rule holdout confirmation before it can be called deployable. Confidence is LOW.
2. **Direction contradicts the prior.** The economic prior is procyclical, but the winner is COUNTERCYCLICAL (it fades sentiment surges). `direction_consistent = false`. The contrarian story is coherent but unproven, and the small genuine linear signal actually runs procyclical.
3. The winner uses a 12-month lead (L12), the TOP of the floored grid [1..13]. The runner-up at the same signal and lead but an adjacent threshold (`diff_1m / T_roll_p50 / L12`, 1.24) is close behind, so the threshold is not uniquely robust; a 12-month lead on a monthly survey with few cycles needs adjacent-lead durability checking.
4. Granger causality is insignificant at every lag (min p = 0.135), so this is not a proven causal forecast.
5. The edge is modest on both axes (return 17.9% vs 15.3%, max drawdown -20.3% vs -23.9%) and comes at higher turnover (4.3/yr), so transaction costs matter more than for a low-turnover rule.
6. The headline sentiment LEVEL is non-stationary (ADF p = 0.68); only its changes are traded. Do not trade the level.
7. This is the University of Michigan *headline consumer sentiment* index (UMCSENT), distinct from the *expected business conditions* diffusion used in `umcsent_spy`; read the two as a method comparison and do not conflate them.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 12-month-lagged 1-month change in sentiment sat at or below "
        "its 60-month rolling 75th percentile, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when that lagged 1-month change rose into "
        "its top quartile (a sentiment surge)."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2019-03-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: diff_1m countercyclical rule crossed T_roll_p75; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED (University of Michigan Surveys of Consumers) | `UMCSENT`, U. Michigan Index of Consumer Sentiment (headline, ~50-112) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the University of Michigan headline Index of Consumer "
    "Sentiment (FRED `UMCSENT`), the classic consumer-confidence gauge -- "
    "distinct from the expected-business-conditions diffusion used by the "
    "`umcsent_spy` pair. Unlike that bounded diffusion, the headline LEVEL is "
    "non-stationary (ADF does not reject a unit root, p = 0.68; KPSS rejects "
    "stationarity), so the level is NOT traded. The pipeline constructs the "
    "level, its 1-month change, its 12-month change, and a 60-month rolling "
    "z-score; the 1-month and 12-month changes are stationary. The winning "
    "signal is `umcsent_diff_1m`, the 1-month change, used with a 12-month lead, "
    "a 60-month rolling 75th-percentile threshold, and a COUNTERCYCLICAL "
    "orientation (long SPY when the lagged 1-month change is at or below its "
    "rolling 75th percentile -- i.e. unless sentiment is surging)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the sentiment signal move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do falling- and rising-sentiment regimes behave differently? | Makes the sentiment story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past sentiment information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: sentiment transforms (level, 1-month change, 12-month change, 60-month rolling z-score) x fixed and rolling thresholds x a long/cash strategy x procyclical/countercyclical orientations x lead times (1-13 months, floored to L1 per the #255 publication-lag standard). The final tournament has 312 combinations, all 312 valid. The winning rule is `umcsent_diff_1m / T_roll_p75 / P1_long_cash countercyclical / L12`, the maximum OOS Sharpe (1.25). The median valid combo (0.68) underperforms buy-and-hold (0.95), and the runner-up (`diff_1m / T_roll_p50 / L12`, 1.24) shares the same signal and 12-month lead at an adjacent threshold -- read the winner as a selection maximum whose signal/lead pairing is fairly stable but whose exact threshold is not uniquely robust. The winner's direction is countercyclical, which CONTRADICTS the leading-indicator procyclical prior (`direction_consistent = false`); the winner does, however, clear a re-shuffle (bootstrap) significance test (p = 0.003).
"""

_REFERENCES_MD = """
1. University of Michigan, Surveys of Consumers, Index of Consumer Sentiment.
2. Federal Reserve Economic Data (FRED), `UMCSENT`, University of Michigan: Consumer Sentiment.
3. The Conference Board, Consumer Confidence Index (a related gauge).
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
        "Monthly sample from 1993-01-31 to 2026-08-31, with out-of-sample "
        "window 2018-04-30 to 2026-08-31 (101 months). SPY history limits the "
        "usable sample even though the survey begins earlier."
    ),
    plain_english=(
        "This page documents how the U. Michigan headline consumer-sentiment "
        "index was turned into stationary signals (the level is non-stationary, "
        "so changes are used), how the econometric checks were run, and how the "
        "tournament selected the final SPY allocation rule -- along with the "
        "honest caveat that the selection maximum is a COUNTERCYCLICAL rule whose "
        "direction contradicts the prior and whose 12-month lead is not yet a "
        "validated edge, even though it clears a bootstrap test."
    ),
)
