"""Import Price Index (IR) x SPY pair configuration (Rule APP-PT1). Pair `import_price_spy`, page 33.

Phase B: every result number is rendered from the structured winner fields (results/import_price_spy/
winner_summary.json `winner_fields`, via components.winner_fields) or from the evidence tables listed in
evidence_facts; none is typed here (scripts/gate_structured_prose.py, scripts/gate_number_provenance.py).
MAIN = as known at the time (real-time IR vintages, ALFRED, from 2010-03 only); COMPARISON = as revised today
(hindsight). The earlier research run (20261016, commit 1d06839f on branch feat261016_pit_release, never on the main
site) is replayed exactly by the harness and named from the previous_* fields. The main site still shows an older rule.
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "import_price_spy"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_QR = P.col_dict(P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv"), "quantile", "coef")
_QT = P.json_file(_RES / f"core_models_{_TAG}" / "quantile_equality_test.json")
_LP_T = P.csv_file(_RES / f"core_models_{_TAG}" / "local_projections.csv")
_LP_COEF = P.col_dict(_LP_T, "horizon", "coef")
_LP_P = P.col_dict(_LP_T, "horizon", "p_value")
_TS = P.json_file(_RES / "track_summary.json")
_FIRST_VINTAGE = _WS["tracks"]["main"]["sample"]["first_vintage"]     # first ALFRED vintage of IR
_EV = P.json_file(_RES / f"evidence_facts_{_TAG}.json")["derived"]
_G_SIG = bool(_EV["granger_min_p_holm"] < 0.05)
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_PLATEAU = W.value("plateau_leads") or []
_AT_TOP = bool(_PLATEAU) and _PLATEAU[-1] == _GRID[-1]
_C_PLATEAU = W.value("comparison_plateau_leads") or []
_C_AT_TOP = bool(_C_PLATEAU) and _C_PLATEAU[-1] == _GRID[-1]


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
    "T0_zero": "zero",
    "T_z_0": "zero (its own five-year average)",
    "T_z_1.0": "a z-score of one",
    "T_roll_p25": "its rolling 60-month 25th percentile",
    "T_roll_p50": "its rolling 60-month median",
})
SIGNAL_TEXT = P.definitions({
    "yoy": "year-over-year growth in import prices",
    "mom": "month-over-month growth in import prices",
    "chg_3m": "3-month growth in import prices",
    "chg_6m": "6-month growth in import prices",
    "yoy_zscore_60m": "z-score of year-over-year import-price growth against its own five-year history",
    "accel": "change in year-over-year import-price growth (acceleration)",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}
_EVID_SIG = SIGNAL_TEXT["yoy"]      # the transform the descriptive tests use (pipeline EVIDENCE_SIGNAL)


def _rule(prefix: str = "") -> str:
    """Plain-English rule of a track's winner (long/cash), from its structured fields."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    sig = f"the {SIGNAL_TEXT.get(W.value(prefix + 'signal_code'), g('signal_code'))} from {g('lead_word')} months earlier"
    side = SIDE.get(W.value(prefix + "direction"), g("direction"))
    thr = THRESHOLD_TEXT.get(W.value(prefix + "threshold_code"), g("threshold_code"))
    return f"hold SPY when {sig} is {side} {thr}; otherwise hold cash"


def _rid(prefix: str = "") -> str:
    """Rule id `signal / threshold / strategy family / L<lead>`."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    return " / ".join([g("signal_code"), g("threshold_code"), g("strategy_family"), f"L{g('lead')}"])


_SIG = SIGNAL_TEXT.get(W.value("signal_code"), W.signal_code)
_THR = THRESHOLD_TEXT.get(W.value("threshold_code"), W.threshold_code)
_RULE = _rule()
_RID = _rid()
_RID_REVISED = _rid("comparison_")
_RULE_REVISED = _rule("comparison_")
_SAME_RULE = all(W.value(k) == W.value("comparison_" + k)
                 for k in ("signal_code", "lead", "threshold_code", "strategy_family", "direction"))
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
_COMP_TAIL = (
    f" On the revised track the test period ends with {W.comparison_tail_n_periods} month(s) without a defined position "
    f"({W.comparison_tail_first_date} to {W.comparison_tail_last_date}), held in cash under the undefined-means-cash "
    f"rule; holding the last position instead would give a test-period Sharpe of {W.comparison_tail_hold_last_sharpe}."
    if W.has("comparison_tail_n_periods") else "")


class StoryConfig:
    PAGE_TITLE = "The Story: Import-Price Growth as an Inflation Signal for SPY"
    PAGE_SUBTITLE = (
        "BLS Import Price Index, all commodities (FRED IR) x S&P 500 (SPY): monthly import-price growth signals "
        "tested against SPY returns."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, "
        "using import-price data as known at the time"
    )

    PLAIN_ENGLISH = (
        "Every month the Bureau of Labor Statistics reports what U.S. importers paid for goods bought abroad. When "
        "import prices rise quickly, businesses face higher input costs and consumers face imported inflation, which "
        "can push interest rates up and squeeze profit margins. This pair tests whether import-price growth can "
        "improve SPY timing by stepping aside when imported inflation is running hot. The index level only trends "
        "upward over time, so every signal is a growth rate. The headline uses the figures that were published at "
        f"each date, not today's revised figures; the archive of published figures starts on {_FIRST_VINTAGE}."
    )

    WHERE_THIS_FITS = (
        "Import prices sit early in the price chain: they feed producer prices and then consumer prices, and they "
        "move closely with oil prices and the dollar. In the portal this is an inflation and cost-pressure signal for "
        "broad U.S. equities, not a measure of economic activity."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; in the "
        f"test period it scored Sharpe {W.oos_sharpe} against {W.bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{_SIG}, {W.threshold_code}, long/cash, {W.direction}, lead {W.lead_text}. Test-period Sharpe {W.oos_sharpe} "
        f"versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end})."
    )

    HERO_TITLE = "Import Prices vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the Import Price Index (left axis, index level) is shown with SPY (right axis) on the same "
        "time axis. Gray bands are NBER recessions; pink bands mark months when import prices were below their "
        "year-earlier level. The short gap near the end of the line is a month with no published reading (it was "
        "skipped during a federal government shutdown)."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Import-Price Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        f"What this shows: months sorted by {_EVID_SIG}, from Q1 (lowest) to Q4 (highest). "
        f"Same-month SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, {_Q['Q3']:.2f} in Q3 and "
        f"{_Q['Q4']:.2f} in Q4."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: every month the rule reads import prices as they were published then, not today's revised figures. The archive of published import-price figures starts on {_FIRST_VINTAGE}, so the training period on this track is short ({W.is_n} months).

The winning rule is a **{_SIG} rule** (long/cash): {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations ({W.n_distinct} distinct position series). In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

On today's revised data (hindsight, for comparison only, with a training period from {W.comparison_is_start}) the selected rule is to {_RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

### The Imported-Inflation Hypothesis

Rising import prices raise costs for firms that buy foreign inputs and lift consumer prices for imported goods. Fast import-price growth tends to come with higher inflation expectations, tighter monetary policy and pressure on profit margins, all of which weigh on equity valuations; slow or falling import-price growth removes that pressure. A countercyclical rule therefore holds SPY when import-price growth is low and steps aside when it runs hot.

### Why Timing Is Difficult

Import prices are dominated by fuel and by the dollar. Falling import prices can mean a benign supply shock (cheaper oil) or a collapse in global demand (a recession), and these have opposite meanings for equities. The selected rule reacts to import prices from {W.lead_word} months earlier, so it responds to inflation conditions with a delay.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust",
            "narrative": (
                "Import prices fell through 2001 as global demand weakened and oil prices dropped. Low import-price "
                "growth here came with an equity bear market driven by technology valuations, the opposite of what a "
                "simple low-inflation-is-good rule assumes."
            ),
            "caption": "Dot-Com: import prices fell while equities fell.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Import prices climbed with oil into mid-2008 and then collapsed as the recession deepened. The "
                "surge in import-price growth came before the worst of the equity decline, and the collapse came "
                "with it."
            ),
            "caption": "GFC: import prices peaked with oil in 2008, then collapsed.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Import prices dropped with oil in spring 2020 and then rose sharply through 2021 as supply chains "
                "jammed and demand recovered. The shock was fast, so any lagged monthly signal reacted late."
            ),
            "caption": "COVID: import prices dropped, then rebounded sharply.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "Import-price growth peaked in early 2022 and the index itself by mid-2022, as the Federal Reserve "
                "began raising rates and equities sold off. This is the episode the imported-inflation hypothesis "
                "describes most directly."
            ),
            "caption": "2022: import prices peaked in mid-2022 as equities sold off on rate hikes. The gap near the end "
                       "of the line is a month with no published reading (federal government shutdown).",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The episodes suggest import-price growth carries the most information when inflation itself drives the equity cycle, as in 2022, and can mislead when falling import prices reflect a demand collapse. They are context for reading the strategy result, not evidence that the rule adds value; the test-period comparison with buy-and-hold is on the Strategy page.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this imported-inflation story survives correlation, lead-lag, regime, and "
        "strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether import-price growth signals and future SPY returns move together in a roughly "
        "linear way."
    ),
    question="Do faster import-price growth readings line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by signal and horizon. Positive values mean faster import-price growth lines up with "
        "stronger future SPY returns; negative values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: linear correlations between each import-price growth transform and forward SPY returns at "
        "several horizons."
    ),
    observation=(
        "Growth rates are persistent and forward returns overlap, so p-values for these correlations use "
        "Newey-West errors with at least one lag fewer than the horizon."
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
        "A Granger result is a statement about linear forecasting on revised data, not proof that import prices "
        "cause SPY returns."
    ),
    key_message="Formal lead-lag evidence is reported as tested; read it with the tournament, not instead of it.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        f"Quartile analysis sorts months by {_EVID_SIG} and compares SPY returns across the quartile groups."
    ),
    question="Do low and high import-price growth regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 holds the lowest growth readings; Q4 the highest. Compare Sharpe, average return and sample size."
    ),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-month SPY Sharpe by import-price growth quartile, {_Q['Q1']:.2f} in Q1 (lowest) and "
        f"{_Q['Q4']:.2f} in Q4 (highest)."
    ),
    observation=(
        f"SPY Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}."
    ),
    interpretation=(
        "Quartiles are concurrent, not predictive: they show the backdrop, while the tournament tests lagged rules."
    ),
    key_message="Import-price growth regimes describe the equity backdrop.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Cross-correlation on first differences filters persistence before testing whether one series tends to "
        "move before or after the other."
    ),
    question=f"At which offsets do changes in the {_EVID_SIG} line up with SPY returns?",
    how_to_read="Bars outside the dashed band mark offsets with unusually large correlation; positive lags mean import prices move first.",
    chart_name="ccf_prewhitened",
    chart_caption=(
        f"What this shows: correlation of monthly changes in the {_EVID_SIG} with SPY returns at offsets in months."
    ),
    observation="Year-over-year growth rates overlap heavily between consecutive months, so differencing matters "
                "before reading lead-lag bars.",
    interpretation="Isolated significant bars are expected by chance across many offsets.",
    key_message="Import-price timing is irregular.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns line up with import-price growth over several horizons."
    ),
    question=f"How do forward SPY returns relate to the {_EVID_SIG} at different horizons?",
    how_to_read=(
        f"Each bar is the estimated forward SPY return per percentage point of the {_EVID_SIG}; whiskers are 95% "
        "confidence intervals from Newey-West errors with at least one lag fewer than the horizon."
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
    key_message="The horizon matters for import-price signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether import-price growth matters differently in weak, normal and strong SPY "
        "return environments."
    ),
    question="Does import-price growth behave differently in market tails?",
    how_to_read=(
        f"Compare the coefficient across the quantiles of {_EV['n_months_qr_horizon']}-month forward SPY returns; "
        f"whiskers and the equality test come from a moving-block bootstrap (blocks of {_EV['n_months_qr_block']} months) "
        "because the forward returns overlap."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: slopes of {_EV['n_months_qr_horizon']}-month forward SPY returns on the {_EVID_SIG}, "
        f"{_QR[0.1]:+.4f} at tau=0.10 and {_QR[0.5]:+.4f} at tau=0.50; a cross-quantile equality test does "
        f"{'not ' if not _QT['reject_equality'] else ''}reject a uniform slope (Wald p={_QT['p_value']:.2f})."
    ),
    observation=(
        f"The block-bootstrap Wald test {'does not reject' if not _QT['reject_equality'] else 'rejects'} slope "
        f"equality across quantiles (p={_QT['p_value']:.2f})."
    ),
    interpretation=(
        "Tail asymmetry is only established if the equality test rejects; otherwise read the slopes as imprecise."
    ),
    key_message=f"Cross-quantile equality Wald p={_QT['p_value']:.2f}.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Import Prices and SPY",
    "overview": (
        "The tests below describe an imported-inflation overlay. The selected rule's test-period Sharpe is "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold on data as known at the time."
    ),
    "plain_english": (
        "This page asks whether import-price growth helps with SPY timing, first with descriptive tests on today's "
        "revised data, then with the tournament on data as known at the time."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} declared strategy combinations ({W.n_valid} valid on the training "
        f"period; {W.n_distinct} distinct position series, the others repeat a series exactly) "
        f"across {P.length(_MAN['signals'])} import-price growth transforms, zero, z-score and rolling-percentile "
        f"thresholds, the long/cash strategy, both orientations and the lead grid {_GRID_RANGE} months, on data as "
        f"known at the time. The selected winner is `{_RID}`, chosen on the training period by {W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the Strategy page shows the exact rule, its threshold and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged Import-Price Overlay for SPY"
    PAGE_SUBTITLE = (
        f"A searched SPY allocation rule: {_SIG}, long/cash, lead {W.lead_text}, on import-price data as known at "
        "the time."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Earlier research run. A research run of {W.previous_tag} on the branch feat261016_pit_release reported the "
        f"rule {W.previous_rule} (earlier research run: test-period Sharpe {W.previous_oos_sharpe}). That run was never "
        "shown on the main site, which still shows an older rule from an earlier run with a different lead grid and "
        "selection method. The earlier research run's rule was the single highest training Sharpe on revised data "
        "with fixed release lags. The page now reports the rule "
        "selected on the training period from data as known at the time, with point-in-time release dates and the "
        "stable-lead-range rule; today's revised data are shown for comparison only."
    )

    PLAIN_ENGLISH = (
        f"The rule is to {_RULE}. It is a lagged imported-inflation rule, not a forecast of inflation or of a "
        "recession."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from import-price data as known at the time; it has not faced a "
            "frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time import-price figures give a training period of {W.is_n} months ({W.is_start} to "
            f"{W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to "
            f"{W.ci_high}.",
            f"The archive of published import-price figures starts on {_FIRST_VINTAGE}, so the training period on data as known "
            f"at the time ({W.is_start} to {W.is_end}) covers no recession.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}).",
            f"The earlier research run's rule ({W.previous_rule}) was the single highest training Sharpe on revised "
            "data with fixed lags.",
        ] + ([f"The stable lead range {W.plateau_range} reaches the top of the declared lead grid ({_GRID_RANGE} "
              "months); longer leads were not tested."] if _AT_TOP else []),
        conclusion=(
            f"Rule {_RID}: test-period Sharpe "
            f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end}), maximum "
            f"drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on import-price data as known at the "
            "time."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/{PAIR}/hindsight_tournament_results_{_TAG}.csv"},
        {"label": f"Earlier research run tournament ({W.previous_tag}, replayed exactly)",
         "path": f"results/{PAIR}/tournament_results_{W.value('previous_tag')}.csv"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

If-then form:
{_IF_THEN}

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} switches between SPY and cash within the test period (each moves the whole position; {_EV['oos_months_position_change_gt_5pct']} months with a position move larger than {_EV['position_change_threshold_pp']} percentage points); annual turnover {W.annual_turnover}.{_MAIN_TAIL}
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, at each month end the process takes the Import Price Index (`IR`) as it was published on that date (the figures visible when the month's return window opens). Second, inside that vintage it computes the {_SIG} and its threshold. Third, it uses the reading from {W.lead_word} months earlier for the following month's return. Finally, the reading is compared with {_THR}.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read IR as currently published.
2. Compute the {_SIG} from that published series.
3. Take its value from {W.lead_word} months earlier and compare it with {_THR}.
4. Set the position as the rule says (long/cash) and hold it for the following month.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod chart compares the searched rule "
        "with buy-and-hold SPY during major stress windows; each label says whether the window falls before the "
        "training period, in it, or in the test period, and how many months it holds."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            f"How to read it: the indicator is the {_EVID_SIG}; the target is SPY returns. The rolling correlation "
            "tests whether their linear relationship is stable through time."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the import-price/SPY relationship changes enough "
            "that one fixed model is unlikely to describe the whole sample."
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

- The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
- The headline uses import-price data as known at the time; that archive starts on {_FIRST_VINTAGE}, so its training period ({W.is_start} to {W.is_end}) is short and contains no recession. On today's revised data the selected rule {'is the same' if _SAME_RULE else 'is different'} (test-period Sharpe {W.comparison_oos_sharpe}, hindsight).
- The earlier research run's rule ({W.previous_rule}, research run of {W.previous_tag} on the branch feat261016_pit_release, never on the main site) was the single highest training Sharpe on revised data with fixed lags; the new framework replays it exactly and no longer selects it.
- All-commodity import prices move closely with oil and the dollar; falling import prices can signal a demand collapse as easily as relief from inflation.
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records each switch between SPY and cash "
        f"that the rule makes when the {_SIG} reading crosses {_THR}. It covers the full reconstructed history "
        f"({_EV['n_trade_log_rows']} rows), not only the test period. Of those rows, {_EV['n_trade_log_rows_oos']} are "
        f"dated in the test period; the headline's {W.oos_n_trades} switches count only changes between consecutive test-period "
        "months" + (", so the switch made at the first test month is in the log but not in the headline count."
                    if _EV['n_trade_log_rows_oos'] - W.value('oos_n_trades') == 1 else ".")
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
| Indicator (as known at the time) | ALFRED (FRED vintage archive, pinned copy) | `IR`, Import Price Index (end use), all commodities, not seasonally adjusted, every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest vintage of the same archive) | `IR` | Monthly (quarterly in the early years) |
| Release dates | Release calendar (first publication date of each month's reading) | `IR` | Monthly |
| Target | Yahoo Finance (pinned copy) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the BLS Import Price Index for all commodities (an index level). The level is a trending "
    "price index, so it is never traded; the pipeline constructs the "
    f"{SIGNAL_TEXT['yoy']}; the {SIGNAL_TEXT['mom']}; the {SIGNAL_TEXT['chg_3m']}; the {SIGNAL_TEXT['chg_6m']}; the "
    f"{SIGNAL_TEXT['yoy_zscore_60m']}; and the {SIGNAL_TEXT['accel']}. On the as-known-at-the-time track every signal "
    "and rolling threshold is recomputed inside the vintage published when each month's return window opens. "
    f"The winning signal is `{W.signal_code}` ({_SIG}), used with a lead of {W.lead_text}; the reading is compared "
    f"with {_THR}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis (Newey-West p-values) | Do import-price signals move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high import-price growth regimes behave differently? | Makes the imported-inflation story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality (Holm-adjusted across lags) | Does past import-price growth improve SPY forecasts? | Formal lead-lag check |
| Local projections (Newey-West errors) | How do forward SPY returns relate to import-price growth over horizons? | Shows horizon-specific effects |
| Quantile regression (moving-block bootstrap) | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_CE = _WS.get("cross_eval") or {}
_CE_NOTE = {True: "", False: " (that rule does not pass the training validity filters on this data)"}.get(
    bool((_CE.get("revised_winner_on_main") or {}).get("valid", True)), "")
_C_TOP_TEXT = (f" Its stable lead range {W.comparison_plateau_range} reaches the top of the declared lead grid; longer "
               "leads were not tested." if _C_AT_TOP else "")

_TOURNAMENT_DESIGN_MD = f"""
Grid: import-price growth transforms x zero, z-score and rolling-percentile thresholds x the long/cash strategy x procyclical/countercyclical orientations x leads {_GRID_RANGE} months, where the lead is the whole gap between the reading month and the month whose return it trades ({W.n_candidates} declared combinations; {W.n_distinct} distinct position series, the others repeat a series exactly). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{_RID}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe} ({W.is_start} to {W.is_end}), test-period Sharpe {W.oos_sharpe}. The raw single highest training Sharpe on this track (argmax, {W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}; it is shown for reference and is not the selection rule.{_MAIN_TAIL}
- As revised today (hindsight): `{_RID_REVISED}`, stable lead range {W.comparison_plateau_range}, training Sharpe {W.comparison_is_sharpe} ({W.comparison_is_start} to {W.comparison_is_end}), test-period Sharpe {W.comparison_oos_sharpe}.{_C_TOP_TEXT}{_COMP_TAIL}
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}{_CE_NOTE}.
- Chance check: across {W.null_draws} contests run on circularly shifted import-price data, {_CHANCE_TEXT}.
- Earlier research run (a research run of {W.previous_tag} on the branch feat261016_pit_release, never on the main site): `{W.previous_rule}` ({W.previous_selection}), earlier-research-run test-period Sharpe {W.previous_oos_sharpe}. The new framework replays that run exactly (same rows, same winner, same returns).
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `IR`, Import Price Index (End Use): All Commodities (all vintages).
2. U.S. Bureau of Labor Statistics, Import/Export Price Indexes.
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
        f"{W.oos_end} on data as known at the time. The import-price vintage archive starts on {_FIRST_VINTAGE} and limits the "
        f"as-known-at-the-time sample; the revised comparison trains from {W.comparison_is_start}."
    ),
    plain_english=(
        "This page documents how import prices were turned into testable signals, how the econometric checks "
        "were run, and how the tournament selected the final SPY allocation rule on each data track."
    ),
)
