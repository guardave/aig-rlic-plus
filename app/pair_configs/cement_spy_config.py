"""Portland cement shipments x SPY pair configuration (Rule APP-PT1).

Phase B, single track: USGS cement shipments have no archive of first-published values (registry value_vintage
revised_no_archive), so the rule uses today's revised values with point-in-time release dates. Every result number
is rendered from the structured winner fields (results/cement_spy/winner_summary.json `winner_fields`, via
components.winner_fields), the track summary, or the evidence tables declared in evidence_facts_<tag>.json; none is
typed here (scripts/gate_structured_prose.py, scripts/gate_number_provenance.py). The shipment column's basis check
(data_integrity_<tag>.json) is disclosed on every page.
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "cement_spy"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_EF = P.json_file(_RES / f"evidence_facts_{_TAG}.json")
_D = _EF.get("derived", {})
_CORE = _RES / f"core_models_{_TAG}"
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_TS = P.json_file(_RES / "track_summary.json")
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_IT = P.json_file(_RES / f"data_integrity_{_TAG}.json")
_SB = P.json_file(_RES / f"structural_break_{PAIR}.json")
_LPP = P.col_dict(P.csv_file(_CORE / "local_projections.csv"), "horizon", "p_value")
_QRDF = P.csv_file(_CORE / "quantile_regression.csv")
_QRP = P.col_dict(_QRDF, "quantile", "p_value")
_QT = P.json_file(_CORE / "quantile_equality_test.json")
_CCF = P.csv_file(_CORE / "ccf_prewhitened.csv")
_CCF_SIG_LEAD = list(_CCF.loc[(_CCF["lag"].astype(float) > 0) & _CCF["significant"].astype(bool), "lag"])
_CCF_SIG_LAG = [abs(x) for x in _CCF.loc[(_CCF["lag"].astype(float) < 0) & _CCF["significant"].astype(bool), "lag"]]
_CORR = P.csv_file(_CORE / "correlations.csv")
_N_CORR = P.length(_CORR)
_N_CORR_SIG = P.count(_CORR, "p_value", "<", float(_D["significance_p"]))


def _p(x) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def _r71_caveat() -> str:
    """Chance-check calibration disclosure (R7.1), from the tagged null summary in winner_summary.json."""
    nt = (_WS.get("tracks") or {}).get("main", {}).get("null_tournament") or {}
    if nt.get("r71_pass") is not False:
        return ""
    d = nt.get("r71_diagnosis") or {}
    where = ("The bias appears only in the selected winners on the real return path, not in unselected candidates or "
             "with the returns permuted." if d.get("bias_only_in_selected_winners_on_real_returns") else
             "The bias also appears without selection or without the return path.")
    return ("**Chance-check calibration.** The scrambled contests should show no timing skill on average (the R7.1 "
            "check); here the selected winners of the scrambled contests average a timing skill outside the "
            f"tolerance (track_summary.json). {where} Cause unproven. The chance-check percentile therefore compares "
            "the winner against a null that carries the same effect.")


_R71_CAVEAT = _r71_caveat()

THRESHOLD_TEXT = P.definitions({
    "T0_zero": "zero", "T_roll_p25": "its rolling 60-month 25th percentile", "T_roll_p50": "its rolling 60-month median",
    "T_z_0": "zero (its 60-month average)", "T_z_1.0": "one standard deviation above its 60-month average",
})
SIDE = {"procyclical": "at or above", "countercyclical": "at or below"}
SIGNAL_TEXT = P.definitions({
    "yoy": "year-over-year growth in cement shipments", "mom": "month-over-month growth in cement shipments",
    "chg_3m": "3-month growth in cement shipments", "chg_6m": "6-month growth in cement shipments",
    "yoy_zscore_60m": "60-month z-score of year-over-year cement shipment growth",
    "accel": "change in year-over-year cement shipment growth",
})


def _sig() -> str:
    return SIGNAL_TEXT.get(W.value("signal_code"), W.text("signal_code"))


def _thr() -> str:
    return THRESHOLD_TEXT.get(W.value("threshold_code"), W.text("threshold_code"))


_RULE = (f"hold SPY when the {_sig()} from {W.lead_word} months earlier (or the latest month released by then) is "
         f"{SIDE.get(W.value('direction'), W.text('direction'))} {_thr()}; otherwise hold cash")

_DATA_NOTE = (
    f"**Data note: the cement series is not what its label says for most of the sample.** The Data Master column used "
    f"here equals the Texas total in the same sheet (Northern plus Southern Texas) in {_IT['n_months_equal_texas_total']} "
    f"of {_IT['n_months']} months, through {_IT['last_month_equal_texas_total']}. From {_IT['first_month_not_equal']} "
    f"it is several times the Texas total, an undocumented change of basis, so year-over-year growth reads up to "
    f"{_IT['max_yoy_growth_pct']:.0f}% ({_IT['max_yoy_growth_month']}). Growth rates that span that month are not "
    "economic changes. The results below are computed on the series as published in Data Master. Sensitivity, not "
    f"the rule: on the test sub-period that ends before the change ({W.oos_start} to {_D['pre_break_oos_end']}, "
    f"{_D['pre_break_oos_n']} observations) the rule's Sharpe is {_D['pre_break_oos_sharpe']:.2f} and "
    f"buy-and-hold's is {_D['pre_break_bh_oos_sharpe']:.2f}."
)
_VINTAGE_NOTE = (
    "USGS revises earlier months and keeps no archive of the values first published, so every result uses today's "
    "values: the rule may contain hindsight from later revisions, which cannot be measured. Each month's reading is "
    "used only after its release date."
)


class StoryConfig:
    PAGE_TITLE = "The Story: Cement Shipments and the S&P 500"
    PAGE_SUBTITLE = ("Does growth in Portland cement shipments, a construction-activity indicator, help time exposure "
                     "to the S&P 500 (SPY)?")

    HEADLINE_H2 = (f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold SPY, on today's "
                   "revised cement values (no archive of first releases)")

    PLAIN_ENGLISH = (
        "Portland cement is poured into buildings, roads and other construction projects, so shipments follow the "
        "construction and infrastructure cycle. The working hypothesis is procyclical: firm shipment growth marks "
        "an upswing in real investment and should coincide with better equity returns. The shipment level trends "
        "over time, so only growth rates are tested. Cement data are published several months after the month "
        "they describe, which is why the shortest lead tested is long."
    )

    WHERE_THIS_FITS = (
        "This is a construction-activity filter for broad U.S. equities. It belongs in the portal as context and as a "
        "possible exposure filter, not as a standalone forecast, and only after the data note below is resolved."
    )

    ONE_SENTENCE_THESIS = (
        f"The rule selected on the training period is to {_RULE}; in the test period it scored Sharpe {W.oos_sharpe} "
        f"against {W.bh_oos_sharpe} for buy-and-hold SPY."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: {_sig()}, "
        f"{W.threshold_code}, {W.strategy_family}, lead {W.lead_text}. Test-period Sharpe {W.oos_sharpe} versus "
        f"{W.bh_oos_sharpe} for buy-and-hold SPY ({W.oos_start} to {W.oos_end}). One data track: today's revised "
        "values with release-date timing."
    )

    HERO_TITLE = "Portland Cement Shipments vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the shipment level as published in Data Master is on the left axis and SPY on the right; "
        "grey bands are NBER recessions. The dotted line marks the month where the series changes basis (see the "
        "data note). The traded signals are growth rates, not the level."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by Cement-Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest year-over-year cement growth) to Q4 (strongest), with "
        f"SPY's Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}. "
        "Concurrent and descriptive: a month's cement reading is not public until months later."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

{_DATA_NOTE}

{_VINTAGE_NOTE}

The winning rule is a **{_sig()} rule**: {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}, {W.is_n} months) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations. In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold SPY, an annualized return of {W.oos_ann_return} versus {W.bh_oos_ann_return}, and a maximum drawdown of {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

### The Construction-Activity Hypothesis

Cement demand comes from residential, commercial and public construction. When construction is expanding, shipments grow; when projects are cancelled or delayed, they fall. Construction responds to interest rates and credit conditions and feeds employment and materials demand, so firm shipment growth should go with a stronger economy and better equity returns. The selected rule is {W.direction}, the direction of that prior.
"""

    NARRATIVE_SECTION_2 = f"""
### What History Shows

Sorting months by year-over-year cement growth, SPY's Sharpe in the weakest quartile is {_Q['Q1']:.2f} and in the strongest {_Q['Q4']:.2f}; the middle quartiles are {_Q['Q2']:.2f} and {_Q['Q3']:.2f}. This is concurrent: cement data arrive months later, so the sort is not a trading rule. The series starts in {_D['cement_first_month']}, so it covers the housing-bust recession before the training period and the COVID recession inside the test period.
"""

    SCOPE_NOTE = "*Scope discipline.* Only cement shipment growth transforms are trading signals; the level is never traded."

    TRANSITION_TEXT = (
        "The Evidence page tests whether the construction story survives correlation, lead-lag, regime and "
        "distribution checks."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007-2009)",
            "narrative": (
                "Cement shipment growth fell steeply through the housing bust, well before and during the equity "
                "decline. This window is before the training period."
            ),
            "caption": "Housing bust: cement growth and SPY, before the training period. Grey bands are NBER recessions.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "Shipment growth dipped around the 2020 shock and stayed choppy afterwards, while SPY recovered "
                "quickly. This window is in the test period."
            ),
            "caption": "COVID: cement growth stayed choppy while SPY recovered. Grey bands are NBER recessions.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock and After (2021-2025)",
            "narrative": (
                "Equities fell in 2022 as interest rates rose. The dotted line marks the month the cement series "
                "changes basis; the jump in growth after it is a data artefact, not a construction boom."
            ),
            "caption": "2022 onwards: SPY and cement growth; the dotted line is the series' basis change.",
        },
    ]


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson correlation measures how closely each cement growth transform moves with forward SPY returns. "
        "Forward returns over several months overlap, so p-values use HAC (Newey-West) errors with lags at least "
        "the horizon minus one."
    ),
    question="Does stronger cement shipment growth line up with stronger SPY returns over the following months?",
    how_to_read=(
        "Rows are cement growth transforms, columns are forward SPY return horizons. Blue is positive, red negative; "
        "a star marks a HAC p-value below "
        f"{_D['significance_p']:.2f}."
    ),
    chart_name="correlation_heatmap",
    chart_caption="Correlations of cement growth transforms with forward SPY returns (descriptive, month-stamp alignment).",
    observation=(f"{_N_CORR_SIG} of the {_N_CORR} correlations have a HAC p-value below "
                 f"{_D['significance_p']:.2f}; the correlations are small throughout."),
    interpretation=(
        "With this many cells tested, a few small p-values can arise by chance. The month stamps are aligned, but a "
        "month's cement reading is published months later, so these are not tradable forecasts."
    ),
    key_message="Cement growth has weak linear association with forward SPY returns.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "Granger causality asks whether past cement growth improves forecasts of SPY returns beyond SPY's own "
        "history, and the reverse. Each lag is tested separately, so the smallest p-value across lags is also "
        "shown multiplied by the number of lags tried (Bonferroni)."
    ),
    question="Does past cement growth carry information about future SPY returns?",
    how_to_read=f"Each bar is a p-value at one lag, for each direction. Bars below the dashed line are below {_D['significance_p']:.2f} before adjustment.",
    chart_name="granger_f_by_lag",
    chart_caption="Granger p-values by lag, cement growth to SPY and SPY to cement growth.",
    observation=(
        f"Smallest p-value from cement growth to SPY: {_p(_D['granger_min_p_cement_to_spy'])} at lag "
        f"{_D['granger_cement_to_spy_best_lead']} ({_p(_D['granger_min_p_bonf_cement_to_spy'])} after adjusting for "
        f"{_D['n_granger_lags']} lags). From SPY to cement growth: {_p(_D['granger_min_p_spy_to_cement'])} at lag "
        f"{_D['granger_spy_to_cement_best_lead']} ({_p(_D['granger_min_p_bonf_spy_to_cement'])} adjusted)."
    ),
    interpretation="No lag reaches conventional significance in either direction.",
    key_message="Formal lead-lag evidence from cement growth to SPY is absent.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Cross-Correlation",
    method_theory=(
        "The cross-correlation of the monthly change in year-over-year cement growth (first difference, which "
        "removes most of its persistence) with SPY returns, at leads and lags of up to "
        f"{P.colmax(_CCF, 'lag'):.0f} months."
    ),
    question="At which offset, if any, do cement growth changes and SPY returns move together?",
    how_to_read="Positive lags mean cement moved first. Bars outside the dashed 95% band are highlighted.",
    chart_name="ccf_prewhitened",
    chart_caption="Cross-correlation of the change in cement YoY growth with SPY returns.",
    observation=(
        "Significant lags where cement moves first: "
        f"{', '.join(str(x) for x in _CCF_SIG_LEAD) if _CCF_SIG_LEAD else 'none'}; where SPY moves first: "
        f"{', '.join(str(x) for x in _CCF_SIG_LAG) if _CCF_SIG_LAG else 'none'}."
    ),
    interpretation="Isolated bars outside the band are expected by chance when this many offsets are tested.",
    key_message="No consistent lead-lag pattern between cement growth changes and SPY returns.",
)

REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartiles)",
    method_theory="Months are sorted into quartiles of year-over-year cement growth and SPY statistics are computed in each.",
    question="Does SPY perform differently in strong and weak construction months?",
    how_to_read="Left: Sharpe ratio by quartile; right: annualized return. Q1 = weakest growth, Q4 = strongest.",
    chart_name="regime_stats",
    chart_caption=(f"SPY Sharpe by cement-growth quartile: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, "
                   f"Q4 {_Q['Q4']:.2f} (same months)."),
    observation=f"The weakest-growth quartile has Sharpe {_Q['Q1']:.2f}; the strongest {_Q['Q4']:.2f}.",
    interpretation=(
        "The sort is concurrent, not lagged, and the top quartile includes the months after the series' basis "
        "change, when growth rates are artefacts."
    ),
    key_message="SPY returns differ across cement-growth quartiles, but the pattern is concurrent and noisy.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Forward SPY returns at several horizons are regressed on year-over-year cement growth, with HAC "
        "(Newey-West) errors whose lags are at least the horizon minus one."
    ),
    question="How do SPY returns over the following months line up with year-over-year cement growth?",
    how_to_read=(f"Each bar is the slope of the forward return on YoY growth (scaled as the axis title says); whiskers are "
                 f"{_D['interval_pct']:.0f}% intervals."),
    chart_name="local_projections",
    chart_caption="Descriptive response of forward SPY returns to cement growth by horizon (not the lagged trading rule).",
    observation="Slope p-values by horizon: " + "; ".join(f"{pv:.2f} at the {h}-month horizon" for h, pv in _LPP.items()) + ".",
    interpretation=(
        (f"Horizons with a p-value below {_D['significance_p']:.2f}: {', '.join(f'{h}-month' for h, pv in _LPP.items() if pv < 0.05)}; the "
         "other horizons do not show it, and with several horizons tested a single small p-value is weak evidence."
         if any(pv < 0.05 for pv in _LPP.values()) else f"No horizon has a p-value below {_D['significance_p']:.2f}.")
        + " The extreme growth readings after the series' basis change are part of the sample."
    ),
    key_message="The forward-return response to cement growth is not consistent across horizons.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression (one fit per quantile) checks whether cement growth relates differently to weak, "
        "typical and strong 3-month SPY returns. The 3-month returns overlap, so intervals, p-values and the "
        "equal-slopes Wald test use a moving-block bootstrap."
    ),
    question="Does cement growth matter more in the tails of SPY returns?",
    how_to_read=f"Compare the slope across quantiles; whiskers are {_D['interval_pct']:.0f}% bootstrap intervals.",
    chart_name="quantile_coef",
    chart_caption="Slope of the 3-month forward SPY return on cement YoY growth at each return quantile.",
    observation=("Slope p-values by quantile: " + "; ".join(f"{pv:.2f} at the {q:.2f} quantile" for q, pv in _QRP.items())
                 + f". Equal-slopes Wald test p-value {_QT['p_value']:.2f}."),
    interpretation=("The test rejects equal slopes across quantiles." if _QT["reject_equality"] else
                    "The test does not reject equal slopes across quantiles: no evidence of tail asymmetry."),
    key_message=(f"{P.count(_QRDF, 'p_value', '<', float(_D['significance_p']))} of the {P.length(_QRDF)} quantile slopes have a p-value "
                 f"below {_D['significance_p']:.2f}."),
)

EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Cement Shipments and SPY",
    "overview": (
        "The tests below are descriptive, on today's revised cement values. The selected rule's test-period Sharpe is "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold SPY. {_DATA_NOTE}"
    ),
    "plain_english": "This page asks whether cement shipment growth carries information about SPY returns, and how strong it is.",
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, CCF_BLOCK, REGIME_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Cross-correlation", "Regimes"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} combinations ({W.n_valid} valid on the training period, "
        f"{W.n_distinct} distinct position series) across {P.length(_MAN['signals'])} cement growth transforms, "
        f"constant and rolling thresholds, long/cash positions, both directions and the lead grid {_GRID_RANGE} "
        f"months. The selected winner is `{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, "
        f"chosen on the training period by {W.selection_objective}."
    ),
    "transition": "**Transition:** the evidence is weak and not causal. The Strategy page shows the exact rule and its caveats.",
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating Cement Shipment Growth into SPY Positioning"
    PAGE_SUBTITLE = (f"A searched SPY allocation rule: {_sig()}, {_thr()}, lead {W.lead_text}, on today's revised "
                     "cement values with release-date timing.")

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-18). This page previously reported the rule {W.previous_rule} (test-period Sharpe "
        f"{W.previous_oos_sharpe}, published {W.previous_tag}), which was the single highest training Sharpe in the "
        "grid with fixed month-end lags. It now reports the rule selected by the stable-lead-range rule, with each "
        "reading used only after its release date. The data note below applies to both."
    )

    PLAIN_ENGLISH = f"The rule is to {_RULE}. It is a lagged construction-activity rule, not a real-time forecast."

    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=("Selected on the training period from today's revised cement values (no archive of first "
                       "releases); it has not faced a frozen-rule hold-out test."),
        strengths=[
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
            f"Each reading is used only after its release date (training period {W.is_start} to {W.is_end}).",
        ],
        risks=[
            (f"The cement column equals the Texas total through {_IT['last_month_equal_texas_total']} and changes "
             f"basis in {_IT['first_month_not_equal']}; on the test sub-period that ends before that, the rule's Sharpe "
             f"is {_D['pre_break_oos_sharpe']:.2f} and buy-and-hold's is {_D['pre_break_bh_oos_sharpe']:.2f}."),
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to {W.ci_high}.",
            f"Short training period ({W.is_n} months) and no archive of first-published values.",
            f"No Granger evidence from cement growth to SPY (smallest p-value {_p(_D['granger_min_p_cement_to_spy'])}, "
            f"{_p(_D['granger_min_p_bonf_cement_to_spy'])} after the {_D['n_granger_lags']}-lag adjustment).",
        ],
        conclusion=(
            f"Rule {W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}: test-period Sharpe "
            f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold SPY ({W.oos_start} to {W.oos_end}), maximum "
            f"drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}."
        ),
    )

    DOWNLOADS = [
        {"label": "Tournament results", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Granger causality", "path": f"results/{PAIR}/core_models_{_TAG}/granger_causality.csv"},
        {"label": "Regime quartile statistics", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Data basis check", "path": f"results/{PAIR}/data_integrity_{_TAG}.json"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

Test-period results ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {_D['n_oos_trade_log_rows']} position changes in the test period (each a full switch between SPY and cash, counted from the trade log, including any move into the first test month); annual turnover {W.annual_turnover}; time in SPY {W.oos_exposure}.

{_DATA_NOTE}
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, at each month end the process takes the cement series as it stands today (no archive of earlier values exists) and computes the {_sig()}. Second, it uses the reading from {W.lead_word} months earlier; if that month had not yet been published by then (USGS publishes several months after the month), it uses the latest published month instead. Finally, the reading is compared with {_thr()} and the position is held through the following month.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, take the latest published USGS cement shipment figures.
2. Compute the {_sig()}.
3. Take its value from {W.lead_word} months earlier (or the latest month published by then) and compare it with {_thr()}.
4. Set the position as the rule says: {_RULE}.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Calendar-Year Sharpe"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe of the rule and of buy-and-hold SPY in each full calendar year of the test period. "
        "It is not designed to make every year profitable."
    )
    CROSS_PERIOD_CAPTIONS = {
        "subperiod_sharpe": ("How to read it: Sharpe of the rule and of buy-and-hold SPY in each stress episode and over "
                             "the full test period; the label gives the episode's phase "
                             "(before training, training or test)."),
        "structural_break": (f"How to read it: the Quandt-Andrews test looks for a single break in the regression of the "
                             f"SPY return on lagged cement growth. The most likely break is "
                             f"{_SB['breakpoint_date']}, with a bootstrap p-value of "
                             f"{_SB['p_value']:.2f}."),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: training versus test-period Sharpe across the valid combinations. The winner is chosen on "
        "the training period, not on its test-period score."
    )

    CAVEATS_MD = f"""
**Main caveats:**

- {_DATA_NOTE}
- {_VINTAGE_NOTE}
- The training period is short ({W.is_n} months, {W.is_start} to {W.is_end}), because the series starts in {_D['cement_first_month']} and the rolling thresholds need several years of history. Data Master ends in {_D['cement_last_month']}, so later months are not tested.
- There is no Granger evidence from cement growth to SPY (smallest p-value {_p(_D['granger_min_p_cement_to_spy'])}; {_p(_D['granger_min_p_bonf_cement_to_spy'])} after adjusting for {_D['n_granger_lags']} lags).
- The result is marked `found_in_search`; it still needs a frozen-rule hold-out confirmation.
{('- ' + _R71_CAVEAT) if _R71_CAVEAT else ''}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a trade each time the rule switches "
        f"between SPY and cash: {_RULE}."
    )


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as revised today; no archive) | Data Master.xlsx sheet 'Portland Cement' (pinned: data/release_calendar/snapshots/20261016T232733Z/USGS_CEMENT.csv) | USGS Portland cement shipments column ('Mat - Portland Cment Shipmts'; see the data note) | Monthly |
| Release dates | data/release_calendar/release_calendar.csv | `USGS_CEMENT_MIS`: USGS Mineral Industry Surveys publication date, else a conservative fallback | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the cement shipment column of Data Master. Because the level trends, the pipeline uses "
    "growth rates only: the 12-month change, 1-month change, 3-month change and 6-month change (in percent), the "
    "60-month z-score of the 12-month change, and the month-to-month difference of the 12-month change. Every signal and rolling threshold is computed on the revised series and then "
    f"lagged so that each month's reading is used only after its release date. The winning signal is `{W.signal_code}` "
    f"({_sig()}), used with a lead of {W.lead_text} and {_thr()} as threshold. " + _DATA_NOTE
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis (HAC p-values) | Does cement growth move with forward SPY returns? | Simple baseline, robust to overlapping returns |
| Regime quartiles | Do construction regimes behave differently? | Makes the story interpretable |
| Cross-correlation | Where is the lead-lag relationship strongest? | Lead-lag pattern of the differenced series |
| Granger causality (Bonferroni across lags) | Does past cement growth improve SPY forecasts, and the reverse? | Formal lead-lag check in both directions |
| Local projections (HAC) | How do forward SPY returns respond across horizons? | Horizon-specific effects with robust errors |
| Quantile regression (block bootstrap, Wald test) | Is the effect different in weak or strong return states? | Tail sensitivity |
| Quandt-Andrews break test | Does the relationship change at one point in time? | Stability check |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: cement growth transforms x constant and rolling thresholds x long/cash x both directions x leads {_GRID_RANGE} months ({W.n_candidates} combinations, {W.n_distinct} distinct position series). One data track: today's revised values (no archive of first releases), with each reading used only after its release date. Every window of three neighbouring leads is scored by its lowest training Sharpe; the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- Winner: `{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe}, test-period Sharpe {W.oos_sharpe} (buy-and-hold {W.bh_oos_sharpe}). The single highest training Sharpe ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}, shown for reference and not the selection rule.
- Chance check: across {W.null_draws} contests run on circularly shifted cement data, the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores.
- Previously published rule: {W.previous_rule} (published {W.previous_tag}), selected as the single highest training Sharpe with fixed month-end lags; the harness replays it exactly.
"""

_REFERENCES_MD = """
1. U.S. Geological Survey, Mineral Industry Surveys, "Cement" (monthly).
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
5. Koenker, R., and Bassett, G. (1978). "Regression Quantiles."
6. Politis, D. N., and Romano, J. P. (1992). "A Circular Block-Resampling Procedure for Stationary Data."
7. Andrews, D. W. K. (1993). "Tests for Parameter Instability and Structural Change with Unknown Change Point."
8. Newey, W. K., and West, K. D. (1987). "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"Monthly sample; training period {W.is_start} to {W.is_end} and test period {W.oos_start} to {W.oos_end}, "
        "on today's revised cement values with release-date timing."
    ),
    plain_english=(
        "This page documents how the cement series was turned into testable signals, how the checks were run, and "
        "how the tournament selected the SPY allocation rule."
    ),
)
