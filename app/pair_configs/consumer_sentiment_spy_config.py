"""U. Michigan headline Consumer Sentiment (UMCSENT) x SPY pair configuration (Rule APP-PT1).

Phase B: every result number is rendered from the structured winner fields (results/consumer_sentiment_spy/
winner_summary.json `winner_fields`, via components.winner_fields), the track summary, or the evidence tables and
derived facts declared in evidence_facts_<tag>.json; none is typed here (scripts/gate_structured_prose.py,
scripts/gate_number_provenance.py). MAIN = as known at the time (real-time UMCSENT vintages); COMPARISON = as
revised today (hindsight). The correction banner names the rule the main site shows (run 20261009, OOS-selected;
winner_summary selection.legacy_oos_selected_row) and the earlier development run (20261015, raw in-sample Sharpe
argmax, fixed lags; never on the main site), which the harness replays exactly (previous_* fields).
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "consumer_sentiment_spy"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_CORE = _RES / f"core_models_{_TAG}"
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_QR_T = P.csv_file(_CORE / "quantile_regression.csv")
_QR = P.col_dict(_QR_T, "quantile", "coef")
_QR_P = P.col_dict(_QR_T, "quantile", "p_value")
_QT = P.json_file(_CORE / "quantile_equality_test.json")
_LP_T = P.csv_file(_CORE / "local_projections.csv")
_LP_COEF = P.col_dict(_LP_T, "horizon", "coef")
_LP_P = P.col_dict(_LP_T, "horizon", "p_value")
_LP_LAGS = P.col_dict(_LP_T, "horizon", "nw_lags")
_TS = P.json_file(_RES / "track_summary.json")
_EV = P.json_file(_RES / f"evidence_facts_{_TAG}.json")["derived"]
_G_P = _EV["granger_min_p"]
_G_PADJ = _EV["granger_min_p_bonferroni"]
_ALPHA = _EV["significance_p"]
_G_SIG = bool(_G_PADJ < _ALPHA)
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_EDGE = bool(((_WS.get("tracks") or {}).get("main") or {}).get("plateau", {}).get("grid_edge"))
_CCF_LEAD = _EV["ccf_sentiment_first"]["lag"]
_CCF_LAG = _EV["ccf_spy_first"]["lag"]
_TR_GFC = _EV["trough_gfc"]
_TR_22 = _EV["trough_rates_2022"]
# the rule the main site shows (run 20261009, chosen on its test-period Sharpe), recorded by the pipeline
_MS = _WS["selection"]["legacy_oos_selected_row"]
_MS_RULE = f"{_MS['signal']} / {_MS['threshold']} / L{_MS['lead_value']}"


def _lags(v) -> str:
    return ", ".join(str(x) for x in v) if len(v) else "none"


def _r71_caveat() -> str:
    """Chance-check calibration disclosure (R7.1), rendered from the null diagnosis in track_summary.json."""
    fails = [(lbl, d) for lbl, ok, d in (("as known at the time", _NT.get("r71_pass"), _NT.get("r71_diagnosis")),
                                         ("as revised today", _NT.get("revised_r71_pass"), _NT.get("revised_r71_diagnosis")))
             if ok is False]
    if not fails:
        return ""
    body = " ".join(f"On data {lbl}: {d['reading']}" if d else f"On data {lbl}: no diagnosis recorded."
                    for lbl, d in fails)
    return ("- **Chance-check calibration.** The scrambled contests should show no timing skill on average "
            "(the R7.1 check); here they do not meet it. " + body + " Where the check is not met, that track's "
            "chance-check percentile compares its winner against a null that carries the same effect.\n")


_R71_CAVEAT = _r71_caveat()
_CHANCE_TEXT = (f"the real winner's stable-range score is above the winners of all {W.null_draws} scrambled contests"
                if W.value("null_percentile") == 1 else
                f"the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores")

THRESHOLD_TEXT = P.definitions({
    "T_roll_p25": "its rolling 60-month 25th percentile",
    "T_roll_p50": "its rolling 60-month median",
    "T_roll_p75": "its rolling 60-month 75th percentile",
    "T0_zero": "zero",
    "T_z_0": "zero (its 60-month average)",
    "T_z_1.0": "1.0 (one standard deviation above its 60-month average)",
})
SIGNAL_TEXT = P.definitions({
    "level": "consumer sentiment level",
    "diff_1m": "month-on-month change in consumer sentiment",
    "chg_12m": "12-month change in consumer sentiment",
    "zscore_60m": "consumer sentiment z-score versus its 60-month history",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}


def _rule(prefix: str = "") -> str:
    """Plain-English long/cash rule of a track's winner, from its structured fields."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    sig = f"the {SIGNAL_TEXT.get(W.value(prefix + 'signal_code'), g('signal_code'))} from {g('lead_word')} months earlier"
    side = SIDE.get(W.value(prefix + "direction"), g("direction"))
    thr = THRESHOLD_TEXT.get(W.value(prefix + "threshold_code"), g("threshold_code"))
    return f"hold SPY when {sig} is {side} {thr}; otherwise hold cash"


def _rid(prefix: str = "") -> str:
    g = lambda n: W.text(prefix + n)  # noqa: E731
    return " / ".join([g("signal_code"), g("threshold_code"), g("strategy_family"), f"L{g('lead')}"])


_SIG = SIGNAL_TEXT.get(W.value("signal_code"), W.signal_code)
_THR = THRESHOLD_TEXT.get(W.value("threshold_code"), W.threshold_code)
_RULE = _rule()
_RID = _rid()
_RID_REVISED = _rid("comparison_")
_RULE_REVISED = _rule("comparison_")
_SAME_RULE = all(W.value(k) == W.value("comparison_" + k)
                 for k in ("signal_code", "threshold_code", "lead", "strategy_family", "direction"))
_IF_THEN = (
    f"- **IF** `{W.signal_code}` from {W.lead_word} months earlier is {SIDE.get(W.value('direction'), W.direction)} "
    f"{_THR} -> hold SPY.\n- **ELSE** -> hold cash."
)


class StoryConfig:
    PAGE_TITLE = "The Story: U. Michigan Consumer Sentiment as a Signal for SPY"
    PAGE_SUBTITLE = (
        "University of Michigan headline Consumer Sentiment (FRED UMCSENT) x S&P 500 (SPY): monthly household-"
        "sentiment signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}), "
        "using consumer-sentiment data as known at the time"
    )

    PLAIN_ENGLISH = (
        "Every month the University of Michigan asks households how they feel about their finances and the economy; "
        "the headline answer is the Index of Consumer Sentiment (UMCSENT). A preliminary reading comes out in the "
        "middle of the survey month and a final reading at its end. This pair tests whether the level, recent "
        "changes or the z-score of that index can improve SPY timing. The headline uses the survey values as they "
        "were published at each date, not today's revised values; later revisions of this survey are rare."
    )

    WHERE_THIS_FITS = (
        "This is the headline sentiment index. The portal also pairs it with the health-care sector (umcsent_xlv) "
        "and pairs the share of survey respondents expecting better business conditions with SPY (umcsent_spy). Read them "
        "together."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; in the test period "
        f"it scored Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold SPY."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{_SIG}, {W.threshold_code}, long/cash, lead {W.lead_text}. Test-period Sharpe {W.oos_sharpe} "
        f"versus {W.bh_oos_sharpe} for buy-and-hold SPY ({W.oos_start} to {W.oos_end})."
    )

    HERO_TITLE = "U. Michigan Consumer Sentiment vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the sentiment index (left axis, today's revised values) is shown with SPY (right axis) on "
        "the same time axis. Gray bands are NBER recessions; pink bands mark months when sentiment was below its "
        "year-earlier level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Sentiment-Change Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        f"What this shows: months sorted by the 12-month change in consumer sentiment, from Q1 (largest fall) to Q4 "
        f"(largest rise). Same-month SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, {_Q['Q3']:.2f} in Q3 "
        f"and {_Q['Q4']:.2f} in Q4."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: every month the rule reads consumer sentiment as it was published then, not today's revised values.

The winning rule uses the **{_SIG}** (long/cash): {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations ({W.n_distinct} distinct position series). In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}), with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

On today's revised data (hindsight, for comparison only) the selected rule {'is the same' if _SAME_RULE else 'is to ' + _RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

### The Sentiment Hypothesis

Households that feel better about their finances tend to spend more, and spending drives corporate earnings. Rising sentiment should therefore line up with risk-on equity conditions and falling sentiment with retrenchment, which makes the prior procyclical: hold SPY when sentiment is favorable.

### Why Timing Is Difficult

Sentiment reacts to the same news that moves stock prices, often in the same month, including gasoline prices, inflation and the stock market itself. A survey reading can therefore follow the market as much as lead it, and very low readings have sometimes come near market lows rather than before declines.
"""

    HISTORY_ZOOM_EPISODES = [
        {"slug": "dotcom", "title": "Dot-Com Bust",
         "narrative": ("Sentiment was near record highs when the equity bear market began in 2000 and fell only "
                       "gradually; the decline was led by technology valuations rather than household finances."),
         "caption": "Dot-Com: sentiment stayed high into the equity decline."},
        {"slug": "gfc", "title": "Global Financial Crisis",
         "narrative": ("Sentiment slid from early 2007 as house prices and jobs weakened, and equities fell with "
                       "it. Sentiment reached its low in late 2008 and SPY in early 2009."),
         "caption": "GFC: sentiment reached its low in late 2008, SPY in early 2009."},
        {"slug": "covid", "title": "COVID Shock",
         "narrative": ("Sentiment dropped sharply in spring 2020 and recovered slowly, while SPY rebounded within "
                       "months. A rule waiting for sentiment to improve stayed out of much of the rebound."),
         "caption": "COVID: sentiment collapsed and recovered slowly."},
        {"slug": "inflation_2022", "title": "2022 Inflation Shock",
         "narrative": ("High inflation pushed sentiment to very low levels in 2022 while equities fell on higher "
                       "rates; sentiment stayed low through the following recovery in equity prices."),
         "caption": "2022: very low sentiment during the rate shock."},
    ]

    NARRATIVE_SECTION_2 = f"""
### What History Shows

In the financial crisis and the 2022 rate shock the sentiment low came before the SPY low: {_TR_GFC['sentiment_low']} versus {_TR_GFC['spy_low']} ({_TR_GFC['trough_lead']} months apart), and {_TR_22['sentiment_low']} versus {_TR_22['spy_low']} ({_TR_22['trough_lead']} months apart). In the dot-com bust sentiment stayed high into the equity decline, and after the 2020 and 2022 declines it recovered more slowly than SPY. These episodes are context for reading the strategy result, not evidence that the rule adds value; the test-period comparison with buy-and-hold is on the Strategy page.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this sentiment story survives correlation, lead-lag, regime and strategy "
        "checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory="Correlation measures whether sentiment signals and future SPY returns move together in a roughly linear way.",
    question="Do stronger sentiment readings line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by signal and horizon. Positive values mean stronger sentiment readings line up with "
        f"stronger future SPY returns; negative values mean the opposite. A star marks a p-value below {_ALPHA} "
        "from Newey-West standard errors, which allow for the overlap of multi-month returns."
    ),
    chart_name="correlation_heatmap",
    chart_caption="What this shows: linear correlations between each sentiment transform and forward SPY returns at several horizons.",
    observation=(
        "The level and the 12-month change are persistent, so overlapping forward-return correlations carry less "
        "independent evidence than their sample size suggests; the p-values account for that overlap."
    ),
    interpretation="Correlation alone is not enough to trade the pair; the tournament asks whether a lagged rule improves portfolio behavior.",
    key_message="Correlations describe the pair; they do not select the rule.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory="Granger causality tests whether past values of one series improve forecasts of another after accounting for its own history.",
    question="Does the past 12-month change in sentiment help forecast SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show the unadjusted p-value of the test at each monthly lag. Because several lags are tried, the "
        "smallest p-value is also shown Bonferroni-adjusted (multiplied by the number of lags); the dotted line is "
        "the matching threshold."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"What this shows: the smallest sentiment-to-SPY Granger p-value across the {_EV['n_granger_lags']} monthly "
        f"lags tried is {_G_P:.3f} (lag {_EV['granger_best']['lag']}), {_G_PADJ:.3f} after the Bonferroni adjustment."
    ),
    observation=(
        f"The smallest p-value is {_G_P:.3f}; adjusted for the {_EV['n_granger_lags']} lags tried it is {_G_PADJ:.3f}"
        + (f", below {_ALPHA}." if _G_SIG else f", not below {_ALPHA}.")
    ),
    interpretation="A Granger result is a statement about linear forecasting on revised data, not proof that sentiment causes SPY returns.",
    key_message="Formal lead-lag evidence is reported as tested; read it with the tournament, not instead of it.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory="Quartile analysis sorts months by the 12-month change in sentiment and compares SPY returns across the quartile groups.",
    question="Do months of falling and rising sentiment produce different SPY outcomes?",
    how_to_read=("Q1 holds the months where the 12-month change in sentiment was most negative; Q4 the months where it "
                 "was most positive. Compare Sharpe, average return and sample size."),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-month SPY Sharpe by quartile of the 12-month sentiment change, {_Q['Q1']:.2f} in Q1 "
        f"(largest fall) and {_Q['Q4']:.2f} in Q4 (largest rise)."
    ),
    observation=f"SPY Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}.",
    interpretation="Quartiles are concurrent, not predictive: they show the backdrop, while the tournament tests lagged rules.",
    key_message="Sentiment-change regimes describe the equity backdrop.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory="Cross-correlation on first differences filters persistence before testing whether one series tends to move before or after the other.",
    question="At which offsets do changes in sentiment line up with SPY returns?",
    how_to_read="Positive lags mean sentiment moves first; negative lags mean SPY moves first. Bars outside the dashed band mark offsets with unusually large correlation.",
    chart_name="ccf_prewhitened",
    chart_caption="What this shows: correlation of the monthly change in the 12-month sentiment change with SPY returns at offsets in months.",
    observation=(
        f"Offsets (months) outside the band where sentiment moves first: {_lags(_CCF_LEAD)}; where SPY moves "
        f"first: {_lags(_CCF_LAG)}."
    ),
    interpretation="Isolated significant bars are expected by chance across many offsets.",
    key_message="Sentiment and equities often react to the same news.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory="Local projections estimate how future SPY returns line up with the 12-month change in sentiment over several horizons.",
    question="How do forward SPY returns relate to the 12-month change in sentiment at different horizons?",
    how_to_read=(
        "Each bar is the estimated forward SPY return per index point of 12-month sentiment change; whiskers are "
        "95% intervals from Newey-West standard errors with at least horizon-minus-one lags."
    ),
    chart_name="local_projections",
    chart_caption=(
        f"What this shows: slopes from {_LP_COEF[1]:+.4f} at the 1-month horizon (p {_LP_P[1]:.2f}) to "
        f"{_LP_COEF[12]:+.4f} at the 12-month horizon (p {_LP_P[12]:.2f}, {_LP_LAGS[12]} Newey-West lags)."
    ),
    observation="The raw macro relationship is shown here, not the final lagged tournament rule.",
    interpretation="Overlapping horizons share observations; the Newey-West errors widen the intervals accordingly.",
    key_message="The horizon matters for sentiment signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory="Quantile regression checks whether the sentiment change matters differently in weak, normal and strong SPY return environments.",
    question="Does the sentiment change behave differently in market tails?",
    how_to_read=(
        "Compare the sentiment-change coefficient across quantiles of the 3-month forward SPY return. Intervals and "
        "p-values come from a moving-block bootstrap, which allows for overlapping 3-month returns."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: slopes of the 3-month forward SPY return on the 12-month sentiment change, "
        f"{_QR[0.1]:+.4f} at tau=0.10 (p {_QR_P[0.1]:.2f}) and {_QR[0.5]:+.4f} at tau=0.50 (p {_QR_P[0.5]:.2f}); "
        f"a cross-quantile equality test does {'not ' if not _QT['reject_equality'] else ''}reject a uniform slope "
        f"(Wald p={_QT['p_value']:.2f})."
    ),
    observation=(
        f"The block-bootstrap Wald test {'does not reject' if not _QT['reject_equality'] else 'rejects'} slope "
        f"equality across quantiles (p={_QT['p_value']:.2f})."
    ),
    interpretation="Tail asymmetry is only established if the equality test rejects; otherwise read the slopes as imprecise.",
    key_message=f"Cross-quantile equality Wald p={_QT['p_value']:.2f}.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: U. Michigan Consumer Sentiment and SPY",
    "overview": (
        "The tests below describe a household-sentiment overlay. The selected rule's test-period Sharpe is "
        f"{W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}) on data as known at the time."
    ),
    "plain_english": (
        "This page asks whether consumer sentiment helps with SPY timing, first with descriptive tests on today's "
        "revised data, then with the tournament on data as known at the time."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} declared strategy combinations ({W.n_valid} valid on the training "
        f"period; {W.n_distinct} distinct position series) across {P.length(_MAN['signals'])} sentiment transforms, "
        f"zero, fixed and rolling-percentile thresholds, the long/cash position rule, both orientations and the "
        f"lead grid {_GRID_RANGE} months, on data as known at the time. The selected winner is `{_RID}`, chosen on "
        f"the training period by {W.selection_objective}."
    ),
    "transition": "**Transition:** the Strategy page shows the exact rule, its threshold and the deployment caveats.",
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged Consumer-Sentiment Overlay for SPY"
    PAGE_SUBTITLE = (
        f"A searched SPY allocation rule: {_SIG}, long/cash, lead {W.lead_text}, on consumer-sentiment data as known "
        "at the time."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-20). The main site shows the rule {_MS_RULE} ({_MS['direction']}), "
        f"which the legacy method chose by its test-period Sharpe of {_MS['oos_sharpe']:.2f}, so that legacy "
        "test-period result was not a held-out result. "
        f"An earlier run (a development run of {W.previous_tag}, never published on the main site) reported the "
        f"rule {W.previous_rule} ({W.previous_selection}: earlier-run test-period Sharpe {W.previous_oos_sharpe}). "
        "That earlier run's rule was the single highest training-period Sharpe in its grid, on consumer-sentiment "
        "data as downloaded for that run, with each position earning the same month's return. The page now reports the rule selected on the training period "
        "from data as known at the time, with point-in-time release dates, each position applied to the following "
        "month's return and the stable-lead-range rule; today's revised data are shown for comparison only."
    )

    PLAIN_ENGLISH = f"The rule is to {_RULE}. It is a lagged sentiment rule, not a real-time recession forecast."

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from consumer-sentiment data as known at the time; it has not faced a "
            "frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time sentiment readings give a training period of {W.is_n} months ({W.is_start} to {W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to {W.ci_high}.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}).",
            f"The rule shown on the main site ({_MS_RULE}) was chosen by the legacy method on its test-period score.",
            f"The earlier run's rule ({W.previous_rule}, a development run never on the main site) used a lag not in the current grid (each position "
            "earned the same month's return).",
        ] + ([f"The stable lead range {W.plateau_range} sits at the edge of the declared lead grid ({_GRID_RANGE} "
              "months); leads beyond the grid were not tested."] if _EDGE else []),
        conclusion=(
            f"Rule {_RID}: test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold SPY ({W.oos_start} "
            f"to {W.oos_end}), maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on "
            "consumer-sentiment data as known at the time."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/{PAIR}/hindsight_tournament_results_{_TAG}.csv"},
        {"label": f"Earlier run tournament (development run, {W.previous_tag})",
         "path": f"results/{PAIR}/tournament_results_{W.value('previous_tag')}.csv"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

If-then form:
{_IF_THEN}

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}); annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} switches between SPY and cash within the test period (the trade log has {_EV['n_oos_trade_log_rows']} rows dated in the test period{', the first being the move into the first test month' if _EV['oos_entry_move_into_first_test_month'] else ''}); annual turnover {W.annual_turnover}.
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, at each month end the process takes consumer sentiment (`UMCSENT`) as it was published on that date (the values visible when the month's return window opens). Second, inside that vintage it computes the {_SIG} and its threshold. Third, it uses the reading from {W.lead_word} months earlier, and the position is applied to the following month's return. Finally, the reading is compared with {_THR}.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read UMCSENT as currently published.
2. Compute the {_SIG} from that published series.
3. Take its value from {W.lead_word} months earlier and compare it with {_THR}.
4. Hold SPY or cash as the rule says and keep the position for the following month.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod chart compares the searched rule "
        "with buy-and-hold SPY during major stress windows; n is the number of monthly returns in each window."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 12-month change in consumer sentiment; the target is the SPY "
            "monthly return. The rolling correlation tests whether their linear relationship is stable through time."
        ),
        "structural_break": (
            "How to read it: this stability proxy is the largest swing of the rolling correlation, in standard "
            "deviations; it is not a formal break test."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: test-period Sharpe distribution across valid searched strategy combinations by lead "
        "(data as known at the time). The winner is chosen on the training period, not on this test-period score."
    )

    CAVEATS_MD = f"""
**Main caveats:**

- The result is marked as found in the search; it still needs a frozen-rule holdout confirmation.
- The headline uses sentiment data as known at the time. On today's revised data the selected rule {'is the same' if _SAME_RULE else 'is different'} (test-period Sharpe {W.comparison_oos_sharpe}, hindsight).
- The main site shows the legacy rule {_MS_RULE}, chosen by the legacy method on its test-period Sharpe; it is not replayed as a selection rule because it consulted the test period.
- The earlier run's rule ({W.previous_rule}, {W.previous_selection}; a development run of {W.previous_tag}, never on the main site) is replayed exactly on the new framework.
- The earlier run's rule used a signal lag of {W.previous_lead_text} with the position earning the same month's return, which is outside the current grid.
- The test window was seen by the earlier runs, so it is not a frozen hold-out.
- Sentiment reacts to the same news as equities; much of its movement is concurrent with, not ahead of, the market.
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records each switch between SPY and cash the "
        f"rule makes when the {_SIG} reading crosses {_THR}."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "month end",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "position after the trade",
        "commission_bps": "5",
        "reason": f"{W.signal_code} {W.direction} rule crossed {W.threshold_code}",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (FRED archive of every published vintage) | `UMCSENT`, University of Michigan Index of Consumer Sentiment (headline), every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest published values) | `UMCSENT` | Monthly |
| Release dates | FRED / ALFRED release calendar | first publication date per month | Monthly |
| Target | Yahoo Finance | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = P.definition_text(
    "The raw indicator is the University of Michigan Index of Consumer Sentiment (headline index). The pipeline "
    "constructs the level, the month-on-month change, the 12-month change and a z-score against the trailing 60 "
    f"months. Thresholds are zero, {THRESHOLD_TEXT['T_z_1.0']} for the z-score, or rolling 60-month percentiles of "
    "the signal; rolling statistics start after a minimum number of readings. On the as-known-at-the-time track every signal and rolling threshold is "
    "recomputed inside the vintage published when each month's return window opens. "
    f"The winning signal is `{W.signal_code}` ({_SIG}), used with a lead of {W.lead_text}; the reading is compared "
    f"with {_THR}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis (Newey-West p-values) | Do sentiment signals move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do months of falling and rising sentiment behave differently? | Makes the sentiment story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality (Bonferroni-adjusted minimum) | Does the past sentiment change improve SPY forecasts? | Formal lead-lag check |
| Local projections (Newey-West) | How do forward SPY returns relate to the sentiment change over horizons? | Shows horizon-specific effects |
| Quantile regression (block bootstrap) | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Rolling correlation / stability proxy | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: sentiment transforms x zero, fixed z-score and rolling-percentile thresholds x the long/cash position rule x procyclical/countercyclical orientations x leads {_GRID_RANGE} months, with each position applied to the return of the month after it is set ({W.n_candidates} declared combinations; {W.n_distinct} distinct position series). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{_RID}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe}, test-period Sharpe {W.oos_sharpe}. For reference only and not the selection rule, the single raw highest training Sharpe on this track ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}.
- As revised today (hindsight): `{_RID_REVISED}`, training Sharpe {W.comparison_is_sharpe}, test-period Sharpe {W.comparison_oos_sharpe}.
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.
- Chance check: across {W.null_draws} contests run on circularly shifted sentiment data, {_CHANCE_TEXT}.
- Rule shown on the main site (legacy method): `{_MS_RULE}` ({_MS['direction']}), chosen by its legacy test-period Sharpe of {_MS['oos_sharpe']:.2f}; not replayed as a selection rule because it consulted the test period.
- Earlier run (a development run of {W.previous_tag}, never on the main site): `{W.previous_rule}` ({W.previous_selection}), earlier-run test-period Sharpe {W.previous_oos_sharpe}; replayed exactly on the new framework from that run's own data.
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `UMCSENT`, University of Michigan: Consumer Sentiment (all vintages).
2. University of Michigan, Surveys of Consumers.
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Newey, W. K., and West, K. D. (1987). "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix."
7. Politis, D. N., and Romano, J. P. (1992). "A Circular Block-Resampling Procedure for Stationary Data."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"Monthly sample; training period {W.is_start} to {W.is_end} and test period {W.oos_start} to {W.oos_end} on "
        "data as known at the time. The sentiment vintage archive limits the as-known-at-the-time sample; the "
        "revised comparison uses the full SPY history."
    ),
    plain_english=(
        "This page documents how consumer sentiment was turned into testable signals, how the econometric checks "
        "were run, and how the tournament selected the final SPY allocation rule on each data track."
    ),
)
