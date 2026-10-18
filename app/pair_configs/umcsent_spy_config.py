"""University of Michigan Expected Business Conditions x SPY pair configuration (Rule APP-PT1). Pair `umcsent_spy`,
page 36.

Phase B: every result number is rendered from the structured winner fields (results/umcsent_spy/winner_summary.json
`winner_fields`, via components.winner_fields) or from the evidence tables listed in evidence_facts; none is typed
here (scripts/gate_structured_prose.py, scripts/gate_number_provenance.py).

The series is the Michigan survey's EXPECTED BUSINESS CONDITIONS index from Data Master (sheet
UoM_ExptdChgBinesCyle), not the headline Consumer Sentiment index (FRED UMCSENT, used by umcsent_xlv and
consumer_sentiment_spy). UMCSENT appears here only as the source of the survey's release dates (timing).

ONE track (track_policy single_revised_no_archive): no public archive of past values of this index exists
(registry value_vintage revised_no_archive), so the backtest uses today's values with release-calendar timing; the
shared data-basis strip states that from track_summary.json. The previous rule of this page is the one shown on the
main site (20260912 run, commit d1b68ecd, selected on test-period Sharpe), replayed exactly by the harness and named
from the previous_* fields (heading "Correction"). A later development run (branch spike261015_is_oos_floor) is named as an earlier research run from its own
selection record.
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "umcsent_spy"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_QR = P.col_dict(P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv"), "quantile", "coef")
_QR_P = P.col_dict(P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv"), "quantile", "p_value")
_QT = P.json_file(_RES / f"core_models_{_TAG}" / "quantile_equality_test.json")
_LP_T = P.csv_file(_RES / f"core_models_{_TAG}" / "local_projections.csv")
_LP_COEF = P.col_dict(_LP_T, "horizon", "coef")
_LP_P = P.col_dict(_LP_T, "horizon", "p_value")
_TS = P.json_file(_RES / "track_summary.json")
_EV = P.json_file(_RES / f"evidence_facts_{_TAG}.json")["derived"]
_G_SIG = bool(_EV["granger_min_p_holm"] < 0.05)
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_PLATEAU = W.value("plateau_leads") or []
_AT_TOP = bool(_PLATEAU) and _PLATEAU[-1] == _GRID[-1]
_QR_T = P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv")
_QR_ALL_CI_ZERO = bool(((_QR_T["ci_low"] <= 0) & (_QR_T["ci_high"] >= 0)).all())
# the earlier research run (development branch only, never on the main site): its own selection record
_EARLY_SEL = P.csv_file(_RES / "legacy_oos_selection_20261015.csv")
_EARLY = _EARLY_SEL[_EARLY_SEL["role"] == "primary_is_selected_common_start"].iloc[0]
_EARLY_RULE = f"{_EARLY['signal']} / {_EARLY['threshold']} / {_EARLY['direction']} / L{_EARLY['lead_months']}"
_EARLY_BRANCH = "spike261015_is_oos_floor"     # the development branch that holds the earlier research run
_PREV_DIRECTION = str(W.value("previous_rule")).split("|")[3]   # orientation of the main-site rule (its key)


def _r71_caveat() -> str:
    """Chance-check calibration disclosure (R7.1), rendered from the null diagnosis in track_summary.json."""
    if _NT.get("r71_pass") is not False:
        return ""
    d = _NT.get("r71_diagnosis")
    return ("- **Chance-check calibration.** The scrambled contests should show no timing skill on average "
            "(the R7.1 check); here they do not meet it. " + (d["reading"] if d else "No diagnosis recorded.")
            + " The chance-check percentile therefore compares the winner against a null that carries the same "
            "effect.\n")


_R71_CAVEAT = _r71_caveat()
_CHANCE_TEXT = (f"the real winner's stable-range score is above the winners of all {W.null_draws} scrambled contests"
                if W.value("null_percentile") == 1 else
                f"the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores")

THRESHOLD_TEXT = P.definitions({
    "T0_zero": "zero",
    "T_z_0": "zero (its own five-year average)",
    "T_z_1.0": "a z-score of one",
    "T_roll_p25": "its rolling 60-month 25th percentile",
    "T_roll_p50": "its rolling 60-month median",
    "T_roll_p75": "its rolling 60-month 75th percentile",
})
SIGNAL_TEXT = P.definitions({
    "level": "Expected Business Conditions level",
    "diff_1m": "month-on-month change in Expected Business Conditions",
    "chg_12m": "12-month change in Expected Business Conditions",
    "zscore_60m": "z-score of Expected Business Conditions against its own five-year history",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}
_EVID_SIG = SIGNAL_TEXT["level"]      # the transform the descriptive tests use (pipeline EVIDENCE_SIGNAL)
_NO_ARCHIVE = ("No archive of earlier values of this index exists, so every result on these pages uses values as "
               "revised today: any month that was revised after its first publication may differ from what was "
               "known at the time, and that hindsight cannot be measured.")
_SERIES = ("the University of Michigan Expected Business Conditions index (from the project's Data Master workbook; "
           "not the headline Consumer Sentiment index)")


def _rule() -> str:
    """Plain-English rule of the winner (long/cash), from its structured fields."""
    sig = f"the {SIGNAL_TEXT.get(W.value('signal_code'), W.signal_code)} from {W.lead_word} months earlier"
    side = SIDE.get(W.value("direction"), W.direction)
    thr = THRESHOLD_TEXT.get(W.value("threshold_code"), W.threshold_code)
    return f"hold SPY when {sig} is {side} {thr}; otherwise hold cash"


_SIG = SIGNAL_TEXT.get(W.value("signal_code"), W.signal_code)
_THR = THRESHOLD_TEXT.get(W.value("threshold_code"), W.threshold_code)
_RULE = _rule()
_RID = " / ".join([W.signal_code, W.threshold_code, W.strategy_family, f"L{W.lead}"])
_IF_THEN = (
    f"- **IF** `{W.signal_code}` from {W.lead_word} months earlier is {SIDE.get(W.value('direction'), W.direction)} "
    f"{_THR} -> hold SPY.\n"
    "- **ELSE** -> hold cash."
)
_MAIN_TAIL = (
    f" The test period ends with {W.tail_n_periods} month(s) without a defined position ({W.tail_first_date} to "
    f"{W.tail_last_date}), held in cash under the undefined-means-cash rule; holding the last position instead would "
    f"give a test-period Sharpe of {W.tail_hold_last_sharpe}."
    if W.has("tail_n_periods") else "")


class StoryConfig:
    PAGE_TITLE = "The Story: Michigan Expected Business Conditions as a Signal for SPY"
    PAGE_SUBTITLE = (
        "U. Michigan Expected Business Conditions x S&P 500 (SPY): a monthly household survey of the business outlook "
        "tested as a timing signal for SPY."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, "
        "on values as revised today (no archive of earlier values)"
    )

    PLAIN_ENGLISH = (
        "Every month the University of Michigan Surveys of Consumers ask households whether they expect business "
        "conditions in the country to be better or worse a year from now. This pair uses "
        + _SERIES + ". The survey is released twice a month (a preliminary reading in mid-month and a final one at or "
        "before the end of the survey month); the backtest takes its timing from the release dates of the "
        "survey's headline index (FRED series UMCSENT), which comes out in the same release. This pair tests whether "
        "the business outlook of households can improve SPY timing. "
        + _NO_ARCHIVE
    )

    WHERE_THIS_FITS = (
        "Expected Business Conditions is a survey of expectations, not a price: it is bounded and swings within a "
        "range rather than trending. In the portal it is a sentiment signal for broad U.S. equities. It is a "
        "different indicator from the headline Consumer Sentiment index used by the other Michigan pairs."
    )

    ONE_SENTENCE_THESIS = (
        f"On values as revised today, the rule selected on the training period is to {_RULE}; in the test period it "
        f"scored Sharpe {W.oos_sharpe} against {W.bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{_SIG}, {W.threshold_code}, long/cash, {W.direction}, lead {W.lead_text}. Test-period Sharpe {W.oos_sharpe} "
        f"versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end}). One data track: values as revised "
        "today (no archive of earlier values)."
    )

    HERO_TITLE = "Michigan Expected Business Conditions vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the Expected Business Conditions index (left axis) is shown with SPY (right axis) on the "
        "same time axis. Gray bands are NBER recessions. The values are today's; no archive of earlier values exists."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Expected-Conditions Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        f"What this shows: months sorted by the {_EVID_SIG}, from Q1 (lowest) to Q4 (highest). "
        f"Same-month SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, {_Q['Q3']:.2f} in Q3 and "
        f"{_Q['Q4']:.2f} in Q4."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses one data track: values as revised today, read with point-in-time release dates (a month's reading is used only after the survey release that publishes it). {_NO_ARCHIVE} The sample runs from {W.is_start} to {W.oos_end}, where the series in the project's data ends.

The winning rule trades on the **{_SIG}** (long/cash): {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations ({W.n_distinct} distinct position series). In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

### The Sentiment Hypothesis

The usual prior is procyclical: households that expect better business conditions spend more, which supports earnings and equities, so a rule would hold SPY while expectations are strong. The survey asks about the change expected over the next year, though, not about conditions today, and in this data the index rose during the 2001 and 2020 recessions and late in the 2008-09 recession, when conditions were bad but expected to improve. A high reading can therefore mark a weak economy that households expect to recover, which is why the tournament tests both orientations. The selected rule is {W.direction}.

### Why Timing Is Difficult

Equity prices anticipate the cycle too, and they often turn before survey expectations settle. The selected rule reacts to the reading from {W.lead_word} months earlier, so it responds to the household outlook with a long delay.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust",
            "narrative": (
                "The index rose through the 2001 recession and peaked in early 2002, while SPY kept falling into late "
                "2002: households expected conditions to improve from a weak base, which is not the same as conditions "
                "being good."
            ),
            "caption": "Dot-Com: the index rose through the 2001 recession and peaked in early 2002.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The index stayed low until late 2008 and then rose through 2009, while the recession was still "
                "under way. SPY reached its low in early 2009, and both recovered through 2009."
            ),
            "caption": "GFC: the index stayed low until late 2008, then rose through 2009.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The index jumped to its highest reading in the project's data in April 2020, in the middle of the "
                "crash: households expected business conditions to recover from a sudden collapse. A rule that reads "
                "a high value as good news would have been invested through the shock."
            ),
            "caption": "COVID: the index jumped to its highest reading in April 2020.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "The index slid from its 2021 peak through 2022 as inflation rose and the Federal Reserve raised rates, "
                "and it stayed well below that peak through 2025 while SPY recovered from late 2022."
            ),
            "caption": "2022: the index slid from its 2021 peak and stayed well below it.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The episodes show that this index often moves against the cycle in the short run: it rose in the 2001 and 2020 recessions, when households expected a recovery, and it stayed well below its 2021 peak through the equity recovery that began in late 2022. These episodes are context for reading the strategy result, not evidence that the rule adds value; the test-period comparison with buy-and-hold is on the Strategy page.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this sentiment story survives correlation, lead-lag, regime, and "
        "strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether Expected Business Conditions signals and future SPY returns move together in a "
        "roughly linear way."
    ),
    question="Do higher expected-conditions readings line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by signal and horizon. Positive values mean a higher reading lines up with stronger future "
        "SPY returns; negative values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: linear correlations between each expected-conditions signal and forward SPY returns at "
        "several horizons."
    ),
    observation=(
        "The index is persistent and forward returns overlap, so p-values for these correlations use Newey-West errors "
        "with at least one lag fewer than the horizon."
    ),
    interpretation=(
        "Correlation alone is not enough to trade the pair; the tournament asks whether a lagged rule improves "
        "portfolio behavior."
    ),
    key_message="Correlations describe the pair; they do not select the rule.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve forecasts of another after accounting "
        "for its own history."
    ),
    question=f"Does the past {_EVID_SIG} help forecast SPY returns in a formal lag test?",
    how_to_read=(
        f"Bars show the p-value of the test at each of the {_EV['n_granger_lags']} monthly lags; diamonds show the "
        "same p-values after a Holm adjustment for testing every lag. Only an adjusted value below the 0.05 line "
        "counts as evidence once the best lag has been picked."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"What this shows: the smallest single-lag p-value is {_EV['granger_min_p_single']:.3f} at lag "
        f"{_EV['granger_best']['lag']}; after the Holm adjustment across the {_EV['n_granger_lags']} lags it is "
        f"{_EV['granger_min_p_holm']:.3f}."
    ),
    observation=(
        f"Best lag {_EV['granger_best']['lag']}: p {_EV['granger_min_p_single']:.3f} on its own, "
        f"{_EV['granger_min_p_holm']:.3f} after the Holm adjustment"
        + (", below the 0.05 line." if _G_SIG else "; no lag is below the 0.05 line after the adjustment.")
    ),
    interpretation=(
        "A Granger result is a statement about linear forecasting on today's values, not proof that household "
        "expectations cause SPY returns."
    ),
    key_message="Formal lead-lag evidence is reported as tested; read it with the tournament, not instead of it.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        f"Quartile analysis sorts months by the {_EVID_SIG} and compares SPY returns across the quartile groups."
    ),
    question="Do low and high expected-conditions regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 holds the lowest readings; Q4 the highest. Compare Sharpe, average return and sample size."
    ),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-month SPY Sharpe by expected-conditions quartile, {_Q['Q1']:.2f} in Q1 (lowest) and "
        f"{_Q['Q4']:.2f} in Q4 (highest)."
    ),
    observation=(
        f"SPY Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}."
    ),
    interpretation=(
        "Quartiles are concurrent, not predictive: they show the backdrop, while the tournament tests lagged rules."
    ),
    key_message="Expected-conditions regimes describe the equity backdrop.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Cross-correlation on first differences filters persistence before testing whether one series tends to "
        "move before or after the other."
    ),
    question="At which offsets do monthly changes in the index line up with SPY returns?",
    how_to_read="Bars outside the dashed band mark offsets with unusually large correlation; positive lags mean the index moves first.",
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: correlation of monthly changes in the index with SPY returns at offsets in months."
    ),
    observation="The index level is persistent from month to month, so differencing matters before reading lead-lag "
                "bars.",
    interpretation="Isolated significant bars are expected by chance across many offsets.",
    key_message="Read the bars at positive lags for the index moving first.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns line up with the index over several horizons."
    ),
    question=f"How do forward SPY returns relate to the {_EVID_SIG} at different horizons?",
    how_to_read=(
        f"Each bar is the estimated forward SPY return per point of the {_EVID_SIG}; whiskers are 95% confidence "
        "intervals from Newey-West errors with at least one lag fewer than the horizon."
    ),
    chart_name="local_projections",
    chart_caption=(
        f"What this shows: slopes from {_LP_COEF[1]:+.4f} at the 1-month horizon to "
        f"{_LP_COEF[12]:+.4f} at the 12-month horizon (p {_LP_P[12]:.2f} at the 12-month horizon)."
    ),
    observation="The raw macro relationship is shown here, not the final lagged tournament rule.",
    interpretation=(
        "Overlapping horizons share observations; the Newey-West errors widen the longer-horizon intervals for that "
        "reason."
    ),
    key_message="The horizon matters for expected-conditions signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the index matters differently in weak, normal and strong SPY return "
        "environments."
    ),
    question="Does the index behave differently in market tails?",
    how_to_read=(
        f"Compare the coefficient across the quantiles of {_EV['n_months_qr_horizon']}-month forward SPY returns; "
        f"whiskers and the equality test come from a moving-block bootstrap (blocks of {_EV['n_months_qr_block']} months) "
        "because the forward returns overlap."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: slopes of {_EV['n_months_qr_horizon']}-month forward SPY returns on the {_EVID_SIG}, "
        f"{_QR[0.1]:+.4f} at tau=0.10 and {_QR[0.5]:+.4f} at tau=0.50; a cross-quantile equality test does "
        f"{'not ' if not _QT['reject_equality'] else ''}reject a uniform slope (Wald p={_QT['p_value']:.4f})."
    ),
    observation=(
        f"The block-bootstrap Wald test {'does not reject' if not _QT['reject_equality'] else 'rejects'} slope "
        f"equality across quantiles (p={_QT['p_value']:.4f})"
        + ("." if not _QR_ALL_CI_ZERO else "; every quantile's own 95% interval includes zero (smallest single-slope "
                                           f"p-value {min(_QR_P.values()):.2f}), so the evidence is about the slopes "
                                           "differing from one another, not about any one of them.")
    ),
    interpretation=(
        "Tail asymmetry is only established if the equality test rejects; even then, read the individual slopes "
        "with their intervals."
    ),
    key_message=f"Cross-quantile equality Wald p={_QT['p_value']:.4f}.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Michigan Expected Business Conditions and SPY",
    "overview": (
        "The tests below describe a sentiment overlay. The selected rule's test-period Sharpe is "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, on values as revised today (no archive of "
        "earlier values)."
    ),
    "plain_english": (
        "This page asks whether the University of Michigan Expected Business Conditions index (not the headline "
        "Consumer Sentiment index) helps with SPY timing, first with descriptive tests, then with the tournament. "
        "All of it uses values as revised today, because no archive of earlier values exists."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} declared strategy combinations ({W.n_valid} valid on the training "
        f"period; {W.n_distinct} distinct position series) across {P.length(_MAN['signals'])} expected-conditions signals, zero, "
        f"z-score and rolling-percentile thresholds, the long/cash strategy, both orientations and the lead grid "
        f"{_GRID_RANGE} months, on values as revised today. The selected winner is `{_RID}`, chosen on the training "
        f"period by {W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the Strategy page shows the exact rule, its threshold and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged Expected Business Conditions Overlay for SPY"
    PAGE_SUBTITLE = (
        f"A searched SPY allocation rule: {_SIG}, long/cash, lead {W.lead_text}, on values as revised today (no "
        "archive of earlier values)."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-18). The main site previously showed the rule {W.previous_rule} (test-period Sharpe "
        f"{W.previous_oos_sharpe}, run of {W.previous_tag}), {_PREV_DIRECTION}. That previously published rule was "
        "chosen by its test-period score, on a different lead grid with fixed lags, so its test-period result was "
        "not a held-out result. An earlier research run (on the development branch "
        f"`{_EARLY_BRANCH}`, never shown on the main site) picked {_EARLY_RULE} as the single highest training "
        "Sharpe with fixed lags. The page now reports the "
        "rule selected on the training period with point-in-time release dates and the stable-lead-range rule. There "
        "is one data track: no archive of earlier values of this index exists, so every result uses values as "
        "revised today."
    )

    PLAIN_ENGLISH = (
        f"The rule is to {_RULE}. It is a lagged sentiment rule, not a forecast of the survey or of a recession."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from values as revised today (no archive of earlier values); it has "
            "not faced a frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time release dates and a long training period: {W.is_n} months ({W.is_start} to "
            f"{W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to "
            f"{W.ci_high}.",
            "No archive of earlier values of this index exists, so the backtest uses values as revised today; any "
            "hindsight from revisions cannot be measured.",
            f"The single highest training Sharpe in the grid ({W.raw_argmax_rule} at L{W.raw_argmax_lead}) lies "
            f"{W.raw_argmax_position}; it was not chosen.",
            f"The rule previously shown on the main site ({W.previous_rule}) was chosen by its test-period score.",
        ] + ([f"The stable lead range {W.plateau_range} reaches the top of the declared lead grid ({_GRID_RANGE} "
              "months); longer leads were not tested."] if _AT_TOP else []),
        conclusion=(
            f"Rule {_RID}: test-period Sharpe "
            f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end}), maximum "
            f"drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on values as revised today."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Tournament results (values as revised today)", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": f"Main-site rule's tournament (run of {W.previous_tag}, replayed exactly)",
         "path": f"results/{PAIR}/tournament_results_{W.value('previous_tag')}.csv"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

If-then form:
{_IF_THEN}

Test-period results on values as revised today ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} switches between SPY and cash within the test period (each moves the whole position); annual turnover {W.annual_turnover}; in SPY {W.oos_exposure} of the test-period months.{_MAIN_TAIL}
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, the process takes the Expected Business Conditions index as it stands today (no archive of earlier values exists) and computes the {_SIG} and its threshold on the survey's own monthly dates. Second, for each month it uses only readings already published when the month's return window opens (the survey month's reading is released by the end of that month; the release dates come from the survey's headline index, FRED UMCSENT, published in the same release), taking the reading from {W.lead_word} months earlier. Finally, the reading is compared with {_THR}.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read the Michigan Expected Business Conditions index as currently published.
2. Compute the threshold ({_THR}) from the published series.
3. Take the reading from {W.lead_word} months earlier and compare it with that threshold.
4. Set the position as the rule says (long/cash) and hold it for the following month.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod chart compares the searched rule "
        "with buy-and-hold SPY during major stress windows; each label says whether the window falls in the "
        "training period or in the test period, and how many months it holds. Annualized Sharpe ratios over windows "
        "of a few months are noisy; read the window length on each label."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            f"How to read it: the indicator is the {_EVID_SIG}; the target is SPY returns. The rolling correlation "
            "tests whether their linear relationship is stable through time."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the expected-conditions/SPY relationship changes "
            "enough that one "
            "fixed model is unlikely to describe the whole sample."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: test-period Sharpe distribution across valid searched strategy combinations by lead. The "
        "winner is chosen on the training period, not on this test-period score."
    )

    CAVEATS_MD = f"""
**Main caveats:**

- The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
- {_NO_ARCHIVE}
- The series in the project's data ends in {W.oos_end}, so the test period ends there; later SPY months are not tested.
- The series is the Michigan Expected Business Conditions index from the project's Data Master workbook, not the headline Consumer Sentiment index (FRED UMCSENT); UMCSENT supplies only the release dates.
- The rule previously shown on the main site ({W.previous_rule}, run of {W.previous_tag}) was chosen by its test-period score; the new framework replays it exactly and no longer selects it.
- The index measures the change households expect over the next year, so it can rise in a recession; a high reading is not the same as a strong economy.
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records each switch between SPY and cash "
        f"that the rule makes when the {_SIG} reading crosses {_THR}. It covers the full reconstructed history "
        f"({_EV['n_trade_log_rows']} rows), not only the test period."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "month end",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "target weight after the trade",
        "commission_bps": "5",
        "reason": f"{W.signal_code} {W.direction} rule crossed {W.threshold_code}",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (today's values; no archive of earlier values exists) | Data Master workbook (sheet UoM_ExptdChgBinesCyle, University of Michigan Surveys of Consumers), pinned snapshot in data/release_calendar/snapshots/ | `UMICH_EXP_BUS_COND`, U. Michigan Expected Business Conditions (survey index; not the headline Consumer Sentiment index) | Monthly |
| Release dates (timing only) | data/release_calendar/release_calendar.csv, series `UMCSENT` (FRED / ALFRED first-release dates of the survey's headline index, published in the same release) | first publication date per survey month | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the University of Michigan Expected Business Conditions index (Data Master; not the "
    "headline Consumer Sentiment index), a bounded survey index that swings within a range rather than trending, so "
    f"the level itself is a tradable signal. The pipeline constructs the {SIGNAL_TEXT['level']}; the "
    f"{SIGNAL_TEXT['diff_1m']}; the {SIGNAL_TEXT['chg_12m']}; and the {SIGNAL_TEXT['zscore_60m']}. Signals and "
    "rolling thresholds are computed on the survey's own monthly dates from today's values and then aligned to each "
    "month with the release calendar (UMCSENT release dates), so a reading is used only after it was published. The "
    f"winning signal is `{W.signal_code}` ({_SIG}), used with a lead of {W.lead_text}; the reading is compared with "
    f"{_THR}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis (Newey-West p-values) | Do expected-conditions signals move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high expected-conditions regimes behave differently? | Makes the sentiment story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality (Holm-adjusted across lags) | Does the past index improve SPY forecasts? | Formal lead-lag check |
| Local projections (Newey-West errors) | How do forward SPY returns relate to the index over horizons? | Shows horizon-specific effects |
| Quantile regression (moving-block bootstrap) | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: expected-conditions signals x zero, z-score and rolling-percentile thresholds x the long/cash strategy x procyclical/countercyclical orientations x leads {_GRID_RANGE} months, where the lead is the whole gap between the reading month and the month whose return it trades ({W.n_candidates} declared combinations; {W.n_distinct} distinct position series). The winner is selected on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it. There is one data track (values as revised today), so there is no second winner to compare.

- Winner: `{_RID}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe} ({W.is_start} to {W.is_end}; buy-and-hold {W.bh_is_sharpe}), test-period Sharpe {W.oos_sharpe}. The raw single highest training Sharpe (argmax, {W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}; it is shown for reference and is not the selection rule.{_MAIN_TAIL}
- Chance check: across {W.null_draws} contests run on circularly shifted index data, {_CHANCE_TEXT}.
- Rule previously shown on the main site: `{W.previous_rule}` (run of {W.previous_tag}), {_PREV_DIRECTION}, with a previous test-period Sharpe of {W.previous_oos_sharpe}. The previously published rule was chosen by its test-period score on the lead grid of that run, so that score was not a held-out result. The new framework replays that run exactly (same rows in the same order, same test-period scores, same winner, same returns).
- Earlier research run: `{_EARLY_RULE}` (the single highest training Sharpe with fixed lags), on the development branch `{_EARLY_BRANCH}`, never shown on the main site.
"""

_REFERENCES_MD = """
1. University of Michigan, Surveys of Consumers (expected change in business conditions).
2. Federal Reserve Bank of St. Louis, FRED / ALFRED series UMCSENT (release dates of the survey; timing only).
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Newey, W. K., and West, K. D. (1987). "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix."
7. Holm, S. (1979). "A Simple Sequentially Rejective Multiple Test Procedure."
8. Politis, D. N., and Romano, J. P. (1992). "A Circular Block-Resampling Procedure for Stationary Data."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"Monthly sample; training period {W.is_start} to {W.is_end} and test period {W.oos_start} to "
        f"{W.oos_end}, on values as revised today (one track; no archive of earlier values). The sample ends with the "
        "last reading in the project's data."
    ),
    plain_english=(
        "This page documents how the Michigan Expected Business Conditions index was turned into testable signals, how the econometric "
        "checks were run, and how the tournament selected the final SPY allocation rule."
    ),
)
