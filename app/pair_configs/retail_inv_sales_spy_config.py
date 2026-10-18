"""Retail Inventories-to-Sales Ratio (RETAILIRSA) x SPY pair configuration (Rule APP-PT1). Pair `retail_inv_sales_spy`,
page 37.

Phase B: every result number is rendered from the structured winner fields (results/retail_inv_sales_spy/
winner_summary.json `winner_fields`, via components.winner_fields), from tagged artifact values (components.provenance)
or from the evidence tables listed in evidence_facts; none is typed here (scripts/gate_structured_prose.py,
scripts/gate_number_provenance.py).

MAIN = as known at the time (real-time RETAILIRSA vintages). For this pair MAIN has NO winner: the ALFRED archive
starts too late for the training window (track_state rt_insufficient; the reason is read from
winner_summary.tracks.main.insufficient_reason). The page is unranked and says so; the as-revised-today (hindsight)
result is shown for comparison only, labelled as such, never as the headline. The previous rule of this page
(20261016 run, commit 1d06839f) is replayed exactly by the harness and named in the correction banner from the
previous_* fields.
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "retail_inv_sales_spy"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
# run tag of the current artifacts (MAIN has no selection block to read it from)
_TAG = sorted(_RES.glob("evidence_facts_*.json"))[-1].stem.removeprefix("evidence_facts_")
_MAIN = _WS["tracks"]["main"]
_IR = _MAIN["insufficient_reason"]
_FIRST_VINTAGE = _MAIN["sample"]["first_vintage"]
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_QR = P.col_dict(P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv"), "quantile", "coef")
_QT = P.json_file(_RES / f"core_models_{_TAG}" / "quantile_equality_test.json")
_LP_T = P.csv_file(_RES / f"core_models_{_TAG}" / "local_projections.csv")
_LP_COEF = P.col_dict(_LP_T, "horizon", "coef")
_LP_P = P.col_dict(_LP_T, "horizon", "p_value")
_EV = P.json_file(_RES / f"evidence_facts_{_TAG}.json")["derived"]
_G_SIG = bool(_EV["granger_min_p_holm"] < 0.05)
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_CE = (_WS.get("cross_eval") or {}).get("revised_winner_on_main") or {}
_HIND_NULL = (_WS["tracks"]["comparison"] or {}).get("null_tournament") or {}


def _r71_caveat() -> str:
    """Chance-check calibration disclosure (R7.1) of the hindsight track's null, when it fails."""
    if _HIND_NULL.get("r71_pass") is not False:
        return ""
    d = _HIND_NULL.get("r71_diagnosis")
    return ("- **Chance-check calibration (as revised today).** The scrambled contests should show no timing skill on "
            "average (the R7.1 check); here they do not meet it. "
            + (d["reading"] if d else "No diagnosis recorded.") + "\n")


_R71_CAVEAT = _r71_caveat()
if W.has("comparison_null_percentile"):
    _CHANCE_TEXT = (
        f"across {W.comparison_null_draws} contests run on circularly shifted revised data, the hindsight winner's "
        "stable-range score is "
        + (f"above the winners of all {W.comparison_null_draws} scrambled contests"
           if W.value("comparison_null_percentile") == 1 else
           f"at the {W.comparison_null_percentile} point of the scrambled scores") + ".")
else:
    _CHANCE_TEXT = "the chance check was not run for the hindsight track."

THRESHOLD_TEXT = P.definitions({
    "T0_zero": "zero",
    "T_z_0": "zero (its own five-year average)",
    "T_z_1.0": "one standard deviation above its own five-year average",
    "T_roll_p25": "its rolling 60-month 25th percentile",
    "T_roll_p50": "its rolling 60-month median",
    "T_roll_p75": "its rolling 60-month 75th percentile",
})
SIGNAL_TEXT = P.definitions({
    "level": "retail inventories-to-sales ratio",
    "diff_1m": "month-on-month change in the ratio",
    "chg_12m": "12-month change in the ratio",
    "zscore_60m": "60-month z-score of the ratio (the level against its own five-year history)",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}
_EVID_SIG = SIGNAL_TEXT["chg_12m"]      # the transform the descriptive tests use (pipeline EVIDENCE_SIGNAL)


def _rule(prefix: str = "comparison_") -> str:
    """Plain-English rule of a track's winner (long/cash), from its structured fields."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    sig = f"the {SIGNAL_TEXT.get(W.value(prefix + 'signal_code'), g('signal_code'))} from {g('lead_word')} months earlier"
    side = SIDE.get(W.value(prefix + "direction"), g("direction"))
    thr = THRESHOLD_TEXT.get(W.value(prefix + "threshold_code"), g("threshold_code"))
    return f"hold SPY when {sig} is {side} {thr}; otherwise hold cash"


def _rid(prefix: str = "comparison_") -> str:
    """Rule id `signal / threshold / strategy family / L<lead>`."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    return " / ".join([g("signal_code"), g("threshold_code"), g("strategy_family"), f"L{g('lead')}"])


_SIG_H = SIGNAL_TEXT.get(W.value("comparison_signal_code"), W.comparison_signal_code)
_THR_H = THRESHOLD_TEXT.get(W.value("comparison_threshold_code"), W.comparison_threshold_code)
_RULE_H = _rule()
_RID_H = _rid()
_SAME_AS_PREV = W.value("previous_rule") == "|".join(
    str(W.value("comparison_" + k)) for k in ("signal_code", "threshold_code", "strategy_family", "direction", "lead")
).replace("_long_cash", "").replace("_signal_strength", "").replace("_long_short", "")
_AGAINST_PRIOR = W.value("comparison_direction") == "procyclical"
_IF_THEN = (
    f"- **IF** (hindsight rule) `{W.comparison_signal_code}` from {W.comparison_lead_word} months earlier is "
    f"{SIDE.get(W.value('comparison_direction'), W.comparison_direction)} {_THR_H} -> hold SPY.\n"
    "- **ELSE** -> hold cash."
)
_COMP_TAIL = (
    f" Its test period ends with {W.comparison_tail_n_periods} month(s) without a defined position "
    + (f"({W.comparison_tail_first_date})" if W.value("comparison_tail_first_date") == W.value("comparison_tail_last_date")
       else f"({W.comparison_tail_first_date} to {W.comparison_tail_last_date})")
    + ", held in cash under the undefined-means-cash "
    f"rule; holding the last position instead would give a test-period Sharpe of {W.comparison_tail_hold_last_sharpe}."
    if W.has("comparison_tail_n_periods") else "")
_WHY_UNRANKED = (
    f"The archive of the ratio as it was published at each date (ALFRED vintages) starts {_FIRST_VINTAGE}. The first "
    f"month a rule could trade on a published reading is {_IR['rt_start']}. Up to the start of the test period "
    f"({W.comparison_oos_start}) the longest training window any candidate gets is {_IR['n_is_rows']} months, "
    f"shorter than the {_IR['min_required']} the method requires. No candidate meets that minimum, so there is no winner on data as known at the time."
)
_CE_TEXT = (
    f"Applied to data as known at the time, the same hindsight rule records a test-period Sharpe of "
    f"{W.ce_revised_on_main_oos_sharpe} ({W.comparison_oos_start} to {W.comparison_oos_end}); it could not have been "
    "selected on that data, because no training window exists there."
    if W.has("ce_revised_on_main_oos_sharpe") else "")


class StoryConfig:
    PAGE_TITLE = "The Story: Retail Inventories-to-Sales and SPY (Unranked)"
    PAGE_SUBTITLE = (
        "Retail inventories-to-sales ratio (Census, FRED RETAILIRSA) x S&P 500 (SPY): a monthly demand-softness "
        "gauge tested against SPY returns. No ranked result: the archive of past releases is too short."
    )

    HEADLINE_H2 = "## No ranked result: the ratio's history as known at the time is too short to train a rule"

    PLAIN_ENGLISH = (
        "The retail inventories-to-sales ratio is the value of goods on retailers' shelves divided by their monthly "
        "sales, roughly how many months of stock they hold. A high or rising ratio means goods pile up faster than "
        "they sell, so the economic prior is countercyclical: reduce equity exposure when the ratio is high. This "
        "portal ranks a pair only on the figures that were published at each date, before later revisions. For this "
        f"ratio that archive is too short. {_WHY_UNRANKED} A rule found on today's revised figures is shown further "
        "down for comparison only; it uses hindsight."
    )

    WHERE_THIS_FITS = (
        "This is a demand-softness gauge for broad U.S. equities. It is listed but unranked: there is no result on "
        "data as known at the time, so it carries no Candidate, Watchlist or Reject status. The as-revised-today "
        "result is context, not a recommendation."
    )

    ONE_SENTENCE_THESIS = (
        "No rule can be trained on the ratio as it was known at the time; on today's revised figures (hindsight) the "
        f"rule selected on the training period is to {_RULE_H}, with test-period Sharpe {W.comparison_oos_sharpe} "
        f"against {W.comparison_bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        "There is no headline result: the cards above stay empty because no rule exists on data as known at the time. "
        f"Hindsight comparison: the rule selected on the revised training period ({W.comparison_is_start} to "
        f"{W.comparison_is_end}) is `{_RID_H}`, test-period Sharpe {W.comparison_oos_sharpe} versus "
        f"{W.comparison_bh_oos_sharpe} for buy-and-hold ({W.comparison_oos_start} to {W.comparison_oos_end})."
    )

    HERO_TITLE = "Retail Inventories-to-Sales Ratio vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the inventories-to-sales ratio (left axis, today's revised values) is shown with SPY (right "
        "axis) on the same time axis; gray bands are NBER recessions. The ratio jumps when sales fall faster than "
        "inventories and drifts with how retailers manage stock."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Inventories-to-Sales Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        f"What this shows: months sorted by the {_EVID_SIG}, from Q1 (ratio falling most) to Q4 (ratio rising most). "
        f"Same-month SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, {_Q['Q3']:.2f} in Q3 and "
        f"{_Q['Q4']:.2f} in Q4. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

**No ranked result.** {_WHY_UNRANKED}

**Hindsight comparison (today's revised data).** On today's revised data (hindsight), with each month's reading dated by its first release, the rule selected on the training period ({W.comparison_is_start} to {W.comparison_is_end}) by {W.comparison_selection_objective} (stable lead range {W.comparison_plateau_range}) is to {_RULE_H}. In the test period ({W.comparison_oos_start} to {W.comparison_oos_end}) it records Sharpe {W.comparison_oos_sharpe} versus {W.comparison_bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.comparison_oos_max_drawdown} versus {W.comparison_bh_oos_max_drawdown}. The test-period Sharpe difference is {W.comparison_sharpe_gap} (95% interval {W.comparison_ci_low} to {W.comparison_ci_high}). {_CE_TEXT}

{"The hindsight rule is procyclical: it holds SPY when the ratio is high, the opposite of the countercyclical prior." if _AGAINST_PRIOR else "The hindsight rule is countercyclical, in line with the prior."}

### The Demand-Softness Hypothesis

When sales slow, goods stay on shelves and the ratio rises; retailers then cut orders, and the slowdown passes to wholesalers and manufacturers. A high or rising ratio is therefore read as a sign of weakening demand and a reason to hold less equity, while a low or falling ratio signals healthy demand.

### Why Timing Is Difficult

The ratio also moves for reasons unrelated to demand: supply disruptions, retailers' inventory strategies and the long downward drift of the ratio as stock management improved. It spikes in recessions, when sales collapse faster than inventories, and those spikes come at or after the equity sell-off, not before it.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "The ratio stayed near its range through the 2001 recession, apart from a spike in "
                "September 2001 and a drop the next month as sales rebounded. The equity bear market was driven by "
                "technology valuations, not by retail inventories."
            ),
            "caption": "Dot-Com: a brief spike and drop in the ratio in late 2001.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Sales collapsed faster than inventories in late 2008, so the ratio spiked during the recession, at "
                "the same time as the equity sell-off rather than ahead of it."
            ),
            "caption": "GFC: the ratio spiked in late 2008.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Store closures sent the ratio to a spike in spring 2020; stimulus-fuelled sales and supply shortages "
                "then pushed it to record lows in 2021. Both moves came with or after the equity moves."
            ),
            "caption": "COVID: spike and sharp reversal.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "The ratio rebuilt from its record lows as supply chains normalised while equities sold off on higher "
                "rates. A rising ratio here reflected restocking more than collapsing demand."
            ),
            "caption": "2022: the ratio rose from record lows while SPY sold off.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The episodes suggest the ratio moves with recessions rather than ahead of them, and that supply shocks can move it as much as demand does. They are context, not evidence that a rule adds value; the hindsight comparison with buy-and-hold is on the Strategy page.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether the demand-softness story survives correlation, lead-lag, regime and "
        "strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether inventories-to-sales signals and future SPY returns move together in a roughly "
        "linear way."
    ),
    question="Do higher inventories-to-sales readings line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by signal and horizon. Positive values mean higher ratio readings line up with stronger "
        "future SPY returns; negative values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: linear correlations between each inventories-to-sales transform and forward SPY returns at "
        "several horizons (today's revised data)."
    ),
    observation=(
        "The ratio and its changes are persistent and forward returns overlap, so p-values for these correlations "
        "use Newey-West errors with at least one lag fewer than the horizon."
    ),
    interpretation=(
        "Correlation alone is not enough to trade the pair; the tournament asks whether a lagged rule improves "
        "portfolio behavior."
    ),
    key_message="Correlations describe the pair; they do not select a rule.",
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
        f"What this shows: the smallest single-lag p-value is {_EV['granger_min_p_single']:.2f} at lag "
        f"{_EV['granger_best']['lag']}; after the Holm adjustment across the {_EV['n_granger_lags']} lags it is "
        f"{_EV['granger_min_p_holm']:.2f}."
    ),
    observation=(
        f"Best lag {_EV['granger_best']['lag']}: p {_EV['granger_min_p_single']:.2f} on its own, "
        f"{_EV['granger_min_p_holm']:.2f} after the Holm adjustment"
        + (", below the 0.05 line." if _G_SIG else "; no lag is below the 0.05 line after the adjustment.")
    ),
    interpretation=(
        "A Granger result is a statement about linear forecasting on revised data, not proof that inventories cause "
        "SPY returns; a non-rejection does not prove that no relationship exists."
    ),
    key_message="Formal lead-lag evidence is reported as tested.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        f"Quartile analysis sorts months by the {_EVID_SIG} and compares SPY returns across the quartile groups."
    ),
    question="Do falling-ratio and rising-ratio regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 holds the months when the ratio fell most over the year; Q4 those when it rose most. Compare Sharpe, "
        "average return and sample size. Readings tied at a quartile boundary stay in the lower group, so group "
        "sizes differ slightly."
    ),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-month SPY Sharpe by quartile of the {_EVID_SIG}, {_Q['Q1']:.2f} in Q1 (falling most) "
        f"and {_Q['Q4']:.2f} in Q4 (rising most)."
    ),
    observation=(
        f"SPY Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}."
    ),
    interpretation=(
        "Quartiles are concurrent, not predictive: they show the backdrop, while the tournament tests lagged rules. "
        "The quartile signal (12-month change) also differs from the tournament's level signals."
    ),
    key_message="Inventory regimes describe the equity backdrop.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns line up with the change in the ratio over several "
        "horizons."
    ),
    question=f"How do forward SPY returns relate to the {_EVID_SIG} at different horizons?",
    how_to_read=(
        f"Each bar is the estimated forward SPY return per unit of the {_EVID_SIG}; whiskers are 95% confidence "
        "intervals from Newey-West errors with at least one lag fewer than the horizon."
    ),
    chart_name="local_projections",
    chart_caption=(
        f"What this shows: slopes from {_LP_COEF[1]:+.4f} at the 1-month horizon to "
        f"{_LP_COEF[12]:+.4f} at the 12-month horizon (p {_LP_P[12]:.2f} at the 12-month horizon)."
    ),
    observation="The raw macro relationship is shown here, not the lagged tournament rule.",
    interpretation=(
        "Overlapping horizons share observations; the Newey-West errors widen the longer-horizon intervals for that "
        "reason."
    ),
    key_message="Horizon-specific slopes, reported with their uncertainty.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the change in the ratio matters differently in weak, normal and strong "
        "SPY return environments."
    ),
    question="Does the change in the ratio behave differently in market tails?",
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
    "title": "The Evidence: Retail Inventories-to-Sales and SPY",
    "overview": (
        "The tests below describe a demand-softness overlay on today's revised data. There is no tournament result on "
        "data as known at the time for this pair (the archive is too short); the as-revised-today rule's test-period "
        f"Sharpe is {W.comparison_oos_sharpe} versus {W.comparison_bh_oos_sharpe} for buy-and-hold (hindsight)."
    ),
    "plain_english": (
        "This page asks whether the retail inventories-to-sales ratio helps with SPY timing, with descriptive tests "
        "on today's revised data and the tournament summary below."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament declares {W.comparison_n_candidates} strategy combinations across "
        f"{P.length(_MAN['signals'])} inventories-to-sales transforms, zero, z-score and rolling-percentile thresholds, "
        f"the long/cash strategy, both orientations and the lead grid {_GRID_RANGE} months. On data as known at the "
        f"time none is eligible (longest training window {_IR['n_is_rows']} months, {_IR['min_required']} required). On "
        f"today's revised data (hindsight) {W.comparison_n_valid} are valid on the training period and the selected "
        f"rule is `{_RID_H}`, chosen by {W.comparison_selection_objective}."
    ),
    "transition": (
        "**Transition:** the Strategy page shows why there is no ranked rule and the hindsight rule with its caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: No Ranked Rule for Retail Inventories-to-Sales"
    PAGE_SUBTITLE = (
        "No rule exists on data as known at the time (the archive of past releases is too short). The rule found on "
        "today's revised data is shown as hindsight."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-18). This page previously reported a ranked rule: {W.previous_rule} (run of "
        f"{W.previous_tag}), chosen as the single highest training Sharpe on revised "
        "data with fixed release lags; an earlier version reported a rule picked on its test-period score. The page "
        "now ranks only results on data as known at the time. For this pair that archive is too short, so there is "
        "no ranked rule; the revised-data result is shown as hindsight"
        + (", and it is the same rule as the previous one." if _SAME_AS_PREV else ".")
    )

    WINNER_HEADING = "No winner on data as known at the time"

    PLAIN_ENGLISH = (
        f"{_WHY_UNRANKED} For comparison only, the rule selected on today's revised data is to {_RULE_H}."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Unranked: no rule exists on data as known at the time, so the pair has no Candidate, Watchlist or Reject "
            "status."
        ),
        strengths=[
            f"On today's revised data (hindsight) the selected lead sits in a stable lead range "
            f"({W.comparison_plateau_range}).",
        ],
        risks=[
            f"No result as known at the time: longest training window {_IR['n_is_rows']} months, "
            f"{_IR['min_required']} required.",
            f"Hindsight test-period Sharpe difference versus buy-and-hold {W.comparison_sharpe_gap}, 95% interval "
            f"{W.comparison_ci_low} to {W.comparison_ci_high}.",
        ] + (["The hindsight rule is procyclical, opposite to the countercyclical prior."] if _AGAINST_PRIOR else []),
        conclusion=(
            f"No ranked rule. Hindsight rule {_RID_H}: test-period Sharpe {W.comparison_oos_sharpe} versus "
            f"{W.comparison_bh_oos_sharpe} for buy-and-hold ({W.comparison_oos_start} to {W.comparison_oos_end}), "
            f"maximum drawdown {W.comparison_oos_max_drawdown} versus {W.comparison_bh_oos_max_drawdown}, on today's "
            "revised data."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time; no candidate eligible)",
         "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/{PAIR}/hindsight_tournament_results_{_TAG}.csv"},
        {"label": f"Previous rule's tournament (run of {W.previous_tag}, replayed exactly)",
         "path": f"results/{PAIR}/tournament_results_{W.value('previous_tag')}.csv"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**No rule on data as known at the time.** {_WHY_UNRANKED}

**Hindsight rule (today's revised data, comparison only):** {_RULE_H}.

If-then form:
{_IF_THEN}

Hindsight test-period results ({W.comparison_oos_start} to {W.comparison_oos_end}): Sharpe {W.comparison_oos_sharpe} versus {W.comparison_bh_oos_sharpe} buy-and-hold; annualized return {W.comparison_oos_ann_return} versus {W.comparison_bh_oos_ann_return}; maximum drawdown {W.comparison_oos_max_drawdown} versus {W.comparison_bh_oos_max_drawdown}; {W.comparison_oos_n_trades} switches between SPY and cash within the test period (each moves the whole position; {_EV['comparison_oos_months_position_change_gt_5pct']} months with a position move larger than {_EV['position_change_threshold_pp']} percentage points); annual turnover {W.comparison_annual_turnover}.{_COMP_TAIL}
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
On data as known at the time, the process would take the ratio (`RETAILIRSA`) as published on each month end and compute the signals inside that vintage; that archive starts {_FIRST_VINTAGE}, too late for a training window. The hindsight rule instead uses today's revised series: at each month end it takes the reading from {W.comparison_lead_word} months earlier (dated by its first release), computes the {_SIG_H} and compares it with {_THR_H}.

The cards above are empty because there is no result as known at the time. In the hindsight figures, test-period Sharpe means risk-adjusted return outside the training period; maximum drawdown is the largest peak-to-trough loss; turnover is how often the rule changes exposure each year.
"""

    MANUAL_USE_MD = f"""
This describes the hindsight rule so it can be audited; it is not a trading recommendation, and it was not selectable on data as known at the time.

1. At month end, read RETAILIRSA as currently published.
2. Hindsight rule: take the {_SIG_H} from {W.comparison_lead_word} months earlier and compare it with {_THR_H}.
3. Set the position as the rule says (long/cash) and hold it for the following month.
4. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability (Hindsight Rule)"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod chart compares the hindsight rule "
        "(today's revised data) with buy-and-hold SPY during major stress windows; each label says whether the "
        "window falls before the training period, in it, or in the test period, and how many months it holds."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            f"How to read it: the indicator is the {_EVID_SIG}; the target is SPY returns. The rolling correlation "
            "tests whether their linear relationship is stable through time."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the inventories-to-sales / SPY relationship "
            "changes enough that one fixed model is unlikely to describe the whole sample."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: test-period Sharpe distribution across valid searched combinations by lead on today's "
        "revised data (hindsight; no combination is eligible on data as known at the time). The rule is chosen on "
        "the training period, not on this score."
    )

    CAVEATS_MD = f"""
**Main caveats:**

- No result exists on data as known at the time, so the pair is unranked. Everything below the headline is hindsight on today's revised figures.
- The hindsight result is marked `found_in_search`; it would need a frozen-rule test on data released after this run.
- The previous rule of this page ({W.previous_rule}, run of {W.previous_tag}) was the single highest training Sharpe on revised data with fixed lags; the new framework replays that run exactly.
- {"The hindsight rule is procyclical (long when the ratio is high), opposite to the countercyclical prior." if _AGAINST_PRIOR else "The hindsight rule is countercyclical, in line with the prior."}
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair (hindsight rule, today's revised data):** the broker-style log records "
        f"each switch between SPY and cash that the rule makes when the {_SIG_H} reading crosses {_THR_H}. It covers "
        f"the full reconstructed history ({_EV['n_trade_log_rows']} rows), not only the test period."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "month end",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "target weight after the trade",
        "commission_bps": "5",
        "reason": f"{W.comparison_signal_code} {W.comparison_direction} rule crossed {W.comparison_threshold_code} "
                  "(as revised today, hindsight)",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (FRED vintages, pinned in data/release_calendar/vintages/RETAILIRSA.csv.gz) | `RETAILIRSA`, retailers' inventories-to-sales ratio (seasonally adjusted), every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest vintage of the same file) | `RETAILIRSA` | Monthly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per month | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the retail inventories-to-sales ratio (a dimensionless ratio, seasonally adjusted), so no "
    f"further filter is applied. The pipeline constructs the {SIGNAL_TEXT['level']} itself; the "
    f"{SIGNAL_TEXT['diff_1m']}; the {SIGNAL_TEXT['chg_12m']}; and the {SIGNAL_TEXT['zscore_60m']}. On the "
    "as-known-at-the-time track every signal and rolling threshold would be recomputed inside the vintage published "
    "when each month's return window opens; that archive is too short for a training window. The hindsight rule uses "
    f"`{W.comparison_signal_code}` ({_SIG_H}) with a lead of {W.comparison_lead_text}, compared with {_THR_H}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis (Newey-West p-values) | Do inventories-to-sales signals move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do falling-ratio and rising-ratio regimes behave differently? | Makes the demand story interpretable |
| Granger causality (Holm-adjusted across lags) | Does the past change in the ratio improve SPY forecasts? | Formal lead-lag check |
| Local projections (Newey-West errors) | How do forward SPY returns relate to the change in the ratio over horizons? | Shows horizon-specific effects |
| Quantile regression (moving-block bootstrap) | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: inventories-to-sales transforms x zero, z-score and rolling-percentile thresholds x the long/cash strategy x procyclical/countercyclical orientations x leads {_GRID_RANGE} months, where the lead is the whole gap between the reading month and the month whose return it trades ({W.comparison_n_candidates} declared combinations). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it. A candidate needs at least {_IR['min_required']} training months to be eligible.

- As known at the time (headline): no winner. {_WHY_UNRANKED}
- As revised today (hindsight): `{_RID_H}`, stable lead range {W.comparison_plateau_range}, training Sharpe {W.comparison_is_sharpe}, test-period Sharpe {W.comparison_oos_sharpe}. The raw argmax, the single highest training Sharpe on the hindsight track ({W.comparison_raw_argmax_rule} at L{W.comparison_raw_argmax_lead}, Sharpe {W.comparison_raw_argmax_is_sharpe}) is {W.comparison_raw_argmax_is_winner}, {W.comparison_raw_argmax_position}.{_COMP_TAIL}
- Cross-evaluation: {_CE_TEXT}
- Chance check (hindsight track): {_CHANCE_TEXT}
- Previous rule of this page: `{W.previous_rule}` ({W.previous_selection}; run of {W.previous_tag}). The new framework replays that run exactly (same rows, same winner, same returns).
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `RETAILIRSA`, Retailers: Inventories to Sales Ratio (all vintages).
2. U.S. Census Bureau, Monthly Retail Trade Survey and Manufacturing and Trade Inventories and Sales.
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Newey, W. K., and West, K. D. (1987). "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix."
7. Holm, S. (1979). "A Simple Sequentially Rejective Multiple Test Procedure."
8. Politis, D. N., and Romano, J. P. (1994). "The Stationary Bootstrap."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"Monthly sample. As known at the time: no training window (vintage archive from {_FIRST_VINTAGE}). As revised "
        f"today (hindsight): training period {W.comparison_is_start} to {W.comparison_is_end} and test period "
        f"{W.comparison_oos_start} to {W.comparison_oos_end}."
    ),
    plain_english=(
        "This page documents how the retail inventories-to-sales ratio was turned into testable signals, how the "
        "econometric checks were run, and why the tournament has no winner on data as known at the time."
    ),
)
