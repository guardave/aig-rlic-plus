"""Core capital goods orders (FRED NEWORDER) x SPY pair configuration (Rule APP-PT1).

The indicator is NEWORDER, manufacturers' new orders for nondefense capital goods excluding aircraft ("core capital
goods orders"); it is NOT total manufacturing new orders (AMTMNO), and the `mfg_new_orders*` names are legacy
labels. Phase B: every result number is rendered from the structured winner fields (results/mfg_new_orders_spy/
winner_summary.json `winner_fields`, via components.winner_fields), the track summary, or the evidence tables and
derived facts declared in evidence_facts_<tag>.json; none is typed here (scripts/gate_structured_prose.py,
scripts/gate_number_provenance.py). MAIN = as known at the time (real-time NEWORDER vintages); COMPARISON = as
revised today (hindsight). The banner names the rule the main site shows (run 20260830, OOS-selected; recorded by the
pipeline as winner_summary selection.legacy_oos_selected_row) and the earlier research run (20261016, raw in-sample
Sharpe argmax, fixed lags; never on the main site), which the harness replays exactly (previous_* fields).
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "mfg_new_orders_spy"
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
_CCF_LEAD = _EV["ccf_orders_first"]["lag"]
_CCF_LAG = _EV["ccf_spy_first"]["lag"]


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
_MS = _WS["selection"]["legacy_oos_selected_row"]
_MS_RULE = f"{_MS['signal']} / {_MS['threshold']} / L{_MS['lead_value']}"
_COMP_TAIL = (
    f" On the revised track the last test month ({W.comparison_tail_first_date} to {W.comparison_tail_last_date}) "
    "has no defined position in the track's inputs; the published "
    f"figure counts it as cash, and holding the last defined position instead gives a test-period Sharpe of "
    f"{W.comparison_tail_hold_last_sharpe}."
    if W.has("comparison_tail_n_periods") else "")

THRESHOLD_TEXT = P.definitions({
    "T_roll_p25": "its rolling 60-month 25th percentile",
    "T_roll_p50": "its rolling 60-month median",
    "T0_zero": "zero",
    "T_z_0": "zero (its 60-month average)",
    "T_z_1.0": "1.0 (one standard deviation above its 60-month average)",
})
SIGNAL_TEXT = P.definitions({
    "yoy": "year-over-year growth in core capital goods orders",
    "mom": "month-over-month growth in core capital goods orders",
    "chg_3m": "3-month growth in core capital goods orders",
    "chg_6m": "6-month growth in core capital goods orders",
    "yoy_zscore_60m": "z-score of year-over-year orders growth versus its 60-month history",
    "accel": "change in year-over-year orders growth",
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
    PAGE_TITLE = "The Story: Core Capital Goods Orders as a Signal for SPY"
    PAGE_SUBTITLE = (
        "Core capital goods orders (manufacturers' new orders, nondefense capital goods excluding aircraft; FRED "
        "NEWORDER) x S&P 500 (SPY): monthly business-investment signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}), "
        "using orders data as known at the time"
    )

    PLAIN_ENGLISH = (
        "Every month the Census Bureau reports how many dollars of new orders U.S. manufacturers received for "
        "business equipment, excluding defense goods and aircraft. These core capital goods orders track how much "
        "companies plan to invest. The first estimate comes in the advance durable-goods report, a few weeks after "
        "the month ends, and it is revised in the following full report and again in annual revisions. Because the "
        "dollar level grows over time, this pair tests growth rates of orders, not the level, as SPY timing "
        "signals. The headline uses the values as they were published at each date, not today's revised values."
    )

    WHERE_THIS_FITS = (
        "This is a business-investment indicator. The data is core capital goods orders (NEWORDER), not total "
        "manufacturing new orders (AMTMNO), which this pair does not test. Read it alongside the portal's other "
        "manufacturing pairs, such as the ISM manufacturing index."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; in the test period "
        f"it scored Sharpe {W.oos_sharpe}, and buy-and-hold SPY scored {W.bh_oos_sharpe}."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{_SIG}, {W.threshold_code}, long/cash, lead {W.lead_text}. Test-period Sharpe {W.oos_sharpe}; "
        f"buy-and-hold SPY {W.bh_oos_sharpe} ({W.oos_start} to {W.oos_end})."
    )

    HERO_TITLE = "Core Capital Goods Orders Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: year-over-year growth in core capital goods orders (left axis, today's revised values) is "
        "shown with SPY (right axis, log scale) on the same time axis. Gray bands are NBER recessions; pink bands "
        "mark months when orders were below their year-earlier level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Orders-Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        f"What this shows: months sorted by year-over-year growth in core capital goods orders, from Q1 (weakest) to "
        f"Q4 (strongest). Same-month SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, {_Q['Q3']:.2f} in Q3 "
        f"and {_Q['Q4']:.2f} in Q4."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: every month the rule reads core capital goods orders as they were published then, not today's revised values.

The winning rule uses the **{_SIG}** (long/cash): {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations ({W.n_distinct} distinct position series). In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}), with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

On today's revised data (hindsight, for comparison only) the selected rule {'is the same' if _SAME_RULE else 'is to ' + _RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

### The Capital-Spending Hypothesis

Companies order equipment when they expect demand and profits to grow, so rising orders growth should line up with stronger earnings ahead and risk-on equity conditions, and slowing orders with softening demand. That makes the prior procyclical: hold SPY when orders growth is firm.

### Why Timing Is Difficult

Orders are published a few weeks after the month and revised afterwards, and the stock market often prices the investment cycle before the orders data show it. Orders are also measured in current dollars, so inflation can keep reported growth positive while real investment slows.
"""

    HISTORY_ZOOM_EPISODES = [
        {"slug": "dotcom", "title": "Dot-Com Bust",
         "narrative": ("Orders growth peaked in 2000 and fell below its year-earlier level before the 2001 "
                       "recession; the deepest fall came in 2001, while SPY kept falling until late 2002."),
         "caption": "Dot-Com: orders growth turned negative before the recession; SPY fell until late 2002."},
        {"slug": "gfc", "title": "Global Financial Crisis",
         "narrative": ("Orders fell below their year-earlier level in late 2007, close to the equity peak. The "
                       "deepest fall in orders came in spring 2009, shortly after SPY's low in early 2009."),
         "caption": "GFC: orders growth turned negative near the equity peak and bottomed just after SPY."},
        {"slug": "covid", "title": "COVID Shock",
         "narrative": ("Orders were already slightly below their year-earlier level from mid-2019. They dropped "
                       "sharply in spring 2020 and then grew at the fastest rate of the window in 2021, as SPY "
                       "recovered."),
         "caption": "COVID: orders collapsed in spring 2020 and rebounded strongly in 2021."},
        {"slug": "inflation_2022", "title": "2022 Inflation Shock",
         "narrative": ("Nominal orders kept growing through the 2022 equity decline, helped by inflation, and fell "
                       "below their year-earlier level only in 2023 and 2024, while SPY was recovering."),
         "caption": "2022: nominal orders kept growing while equities fell."},
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

Orders growth turned negative around the start of the 2001 and 2008 downturns but bottomed close to, or after, the equity lows, and in 2022 nominal orders kept growing while equities fell. These episodes are context for reading the strategy result, not evidence that the rule adds value; the test-period comparison with buy-and-hold is on the Strategy page.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this capital-spending story survives correlation, lead-lag, regime and "
        "strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory="Correlation measures whether orders-growth signals and future SPY returns move together in a roughly linear way.",
    question="Does stronger orders growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by signal and horizon. Positive values mean stronger orders growth lines up with "
        f"stronger future SPY returns; negative values mean the opposite. A star marks a p-value below {_ALPHA} "
        "from Newey-West standard errors, which allow for the overlap of multi-month returns."
    ),
    chart_name="correlation_heatmap",
    chart_caption="What this shows: linear correlations between each orders-growth transform and forward SPY returns at several horizons.",
    observation=(
        "Year-over-year growth and its z-score are persistent, so overlapping forward-return correlations carry "
        "less independent evidence than their sample size suggests; the p-values account for that overlap."
    ),
    interpretation="Correlation alone is not enough to trade the pair; the tournament asks whether a lagged rule improves portfolio behavior.",
    key_message="Correlations describe the pair; they do not select the rule.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory="Granger causality tests whether past values of one series improve forecasts of another after accounting for its own history.",
    question="Does past year-over-year orders growth help forecast SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show the unadjusted p-value of the test at each monthly lag. Because several lags are tried, the "
        "smallest p-value is also shown Bonferroni-adjusted (multiplied by the number of lags); the "
        "dotted line is the matching threshold."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"What this shows: the smallest orders-to-SPY Granger p-value across the {_EV['n_granger_lags']} monthly "
        f"lags tried is {_G_P:.3f} (lag {_EV['granger_best']['lag']}), {_G_PADJ:.3f} after the Bonferroni adjustment."
    ),
    observation=(
        f"The smallest p-value is {_G_P:.3f}; adjusted for the {_EV['n_granger_lags']} lags tried it is {_G_PADJ:.3f}"
        + (f", below {_ALPHA}." if _G_SIG else f", not below {_ALPHA}.")
    ),
    interpretation="A Granger result is a statement about linear forecasting on revised data, not proof that orders cause SPY returns.",
    key_message="Formal lead-lag evidence is reported as tested; read it with the tournament, not instead of it.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory="Quartile analysis sorts months by year-over-year orders growth and compares SPY returns across the quartile groups.",
    question="Do months of weak and strong orders growth produce different SPY outcomes?",
    how_to_read=("Q1 holds the months with the weakest year-over-year orders growth; Q4 the months with the "
                 "strongest. Compare Sharpe, average return and sample size."),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-month SPY Sharpe by quartile of year-over-year orders growth, {_Q['Q1']:.2f} in Q1 "
        f"(weakest) and {_Q['Q4']:.2f} in Q4 (strongest)."
    ),
    observation=f"SPY Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}.",
    interpretation="Quartiles are concurrent, not predictive: they show the backdrop, while the tournament tests lagged rules.",
    key_message="Orders-growth regimes describe the equity backdrop.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory="Cross-correlation on first differences filters persistence before testing whether one series tends to move before or after the other.",
    question="At which offsets do changes in orders growth line up with SPY returns?",
    how_to_read="Positive lags mean orders growth moves first; negative lags mean SPY moves first. Bars outside the dashed band mark offsets with unusually large correlation.",
    chart_name="ccf_prewhitened",
    chart_caption="What this shows: correlation of the monthly change in year-over-year orders growth with SPY returns at offsets in months.",
    observation=(
        f"Offsets (months) outside the band where orders growth moves first: {_lags(_CCF_LEAD)}; where SPY moves "
        f"first: {_lags(_CCF_LAG)}."
    ),
    interpretation="Isolated significant bars are expected by chance across many offsets.",
    key_message="Equities often price the investment cycle before the orders data show it.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory="Local projections estimate how future SPY returns line up with year-over-year orders growth over several horizons.",
    question="How do forward SPY returns relate to year-over-year orders growth at different horizons?",
    how_to_read=(
        "Each bar is the estimated forward SPY return per percentage point of year-over-year orders growth; "
        "whiskers are 95% intervals from Newey-West standard errors with at least horizon-minus-one lags."
    ),
    chart_name="local_projections",
    chart_caption=(
        f"What this shows: slopes from {_LP_COEF[1]:+.4f} at the 1-month horizon (p {_LP_P[1]:.2f}) to "
        f"{_LP_COEF[12]:+.4f} at the 12-month horizon (p {_LP_P[12]:.2f}, {_LP_LAGS[12]} Newey-West lags)."
    ),
    observation="The raw macro relationship is shown here, not the final lagged tournament rule.",
    interpretation="Overlapping horizons share observations; the Newey-West errors widen the intervals accordingly.",
    key_message="The horizon matters for orders-growth signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory="Quantile regression checks whether orders growth matters differently in weak, normal and strong SPY return environments.",
    question="Does orders growth behave differently in market tails?",
    how_to_read=(
        "Compare the orders-growth coefficient across quantiles of the 3-month forward SPY return. Intervals and "
        "p-values come from a moving-block bootstrap, which allows for overlapping 3-month returns."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: slopes of the 3-month forward SPY return on year-over-year orders growth, "
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
    "title": "The Evidence: Core Capital Goods Orders and SPY",
    "overview": (
        "The tests below describe a business-investment overlay. The selected rule's test-period Sharpe is "
        f"{W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}) on data as known at the time."
    ),
    "plain_english": (
        "This page asks whether core capital goods orders help with SPY timing, first with descriptive tests on "
        "today's revised data, then with the tournament on data as known at the time."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} declared strategy combinations ({W.n_valid} valid on the training "
        f"period; {W.n_distinct} distinct position series) across {P.length(_MAN['signals'])} orders-growth "
        f"transforms, zero, fixed and rolling-percentile thresholds, the long/cash position rule, both orientations "
        f"and the lead grid {_GRID_RANGE} months, on data as known at the time. The selected winner is `{_RID}`, "
        f"chosen on the training period by {W.selection_objective}."
    ),
    "transition": "**Transition:** the Strategy page shows the exact rule, its threshold and the deployment caveats.",
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged Core Capital Goods Orders Overlay for SPY"
    PAGE_SUBTITLE = (
        f"A searched SPY allocation rule: {_SIG}, long/cash, lead {W.lead_text}, on orders data as known at the time."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-20). The main site shows the rule {_MS_RULE} ({_MS['direction']}), "
        f"which the legacy method chose by its test-period Sharpe of {_MS['oos_sharpe']:.2f}, so that legacy "
        "test-period result was not a held-out result. "
        f"An earlier run (a research run of {W.previous_tag}, never published on the main site) reported the rule "
        f"{W.previous_rule} ({W.previous_selection}: earlier-run training Sharpe {W.previous_is_sharpe}, earlier-run "
        f"test-period Sharpe {W.previous_oos_sharpe}), on orders data as downloaded for that run. The page now "
        "reports the rule selected on the training period from data as known at the time, with point-in-time "
        "release dates and the stable-lead-range rule; today's revised data are shown for comparison only."
    )

    PLAIN_ENGLISH = f"The rule is to {_RULE}. It is a lagged capital-spending rule, not a real-time recession forecast."

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from core capital goods orders as known at the time; it has not faced "
            "a frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time orders readings give a training period of {W.is_n} months ({W.is_start} to {W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to {W.ci_high}.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}).",
            "Orders are nominal: inflation can keep reported growth positive while real investment slows.",
        ] + ([f"The stable lead range {W.plateau_range} sits at the edge of the declared lead grid ({_GRID_RANGE} "
              "months); leads beyond the grid were not tested."] if _EDGE else []),
        conclusion=(
            f"Rule {_RID}: test-period Sharpe {W.oos_sharpe} (buy-and-hold SPY: {W.bh_oos_sharpe}; {W.oos_start} "
            f"to {W.oos_end}), maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on "
            "orders data as known at the time."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/{PAIR}/hindsight_tournament_results_{_TAG}.csv"},
        {"label": f"Earlier research-run tournament ({W.previous_tag})",
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
First, at each month end the process takes core capital goods orders (`NEWORDER`) as they were published on that date (the values visible when the month's return window opens). Second, inside that vintage it computes the {_SIG} and its threshold. Third, it uses the reading for the month {W.lead_word} months before the return month; that lag already includes the time to publication. Finally, the reading is compared with {_THR}.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read NEWORDER as currently published.
2. Compute the {_SIG} from that published series.
3. Take its value for the month {W.lead_word} months before the coming month and compare it with {_THR}.
4. Hold SPY or cash as the rule says for the coming month.
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
            "How to read it: the indicator is year-over-year growth in core capital goods orders; the target is the "
            "SPY monthly return. The rolling correlation tests whether their linear relationship is stable through "
            "time."
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

- The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
- The headline uses orders data as known at the time. On today's revised data the selected rule {'is the same' if _SAME_RULE else 'is different'} (test-period Sharpe {W.comparison_oos_sharpe}, hindsight).
- The main site shows the legacy rule {_MS_RULE}, chosen by the legacy method on its test-period Sharpe; it is not replayed as a selection rule because it consulted the test period.
- The earlier run's rule ({W.previous_rule}, {W.previous_selection}; a research run of {W.previous_tag}, never on the main site) is replayed exactly on the new framework.
- The test window was seen by the earlier runs, so it is not a frozen hold-out.
- The data is core capital goods orders (NEWORDER), not total manufacturing new orders (AMTMNO); orders are nominal, and the 2020-21 collapse and rebound sits inside the test window.
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
| Indicator (as known at the time) | ALFRED (FRED vintages, pinned in data/release_calendar/vintages/NEWORDER.csv.gz) | `NEWORDER`, manufacturers' new orders: nondefense capital goods excluding aircraft (U.S. Census Bureau), every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest vintage of the same file) | `NEWORDER` | Monthly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per month | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = P.definition_text(
    "The raw indicator is the dollar value of core capital goods orders (seasonally adjusted, nominal). Because the "
    "level trends upward, the pipeline uses growth rates only: month-over-month, quarterly, semiannual and "
    "year-over-year percentage growth, the z-score of year-over-year growth against its trailing 60 months, and the "
    f"monthly change in year-over-year growth. Thresholds are zero, {THRESHOLD_TEXT['T_z_1.0']} for the z-score, or "
    "rolling 60-month percentiles of the signal; rolling statistics start after a minimum number of readings. On "
    "the as-known-at-the-time track every signal and rolling threshold is recomputed inside the vintage published "
    f"when each month's return window opens. The winning signal is `{W.signal_code}` ({_SIG}), used with a lead of "
    f"{W.lead_text}; the reading is compared with {_THR}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis (Newey-West p-values) | Do orders-growth signals move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do months of weak and strong orders growth behave differently? | Makes the investment story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality (Bonferroni-adjusted minimum) | Does past orders growth improve SPY forecasts? | Formal lead-lag check |
| Local projections (Newey-West) | How do forward SPY returns relate to orders growth over horizons? | Shows horizon-specific effects |
| Quantile regression (block bootstrap) | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Rolling correlation / stability proxy | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: orders-growth transforms x zero, fixed z-score and rolling-percentile thresholds x the long/cash position rule x procyclical/countercyclical orientations x leads {_GRID_RANGE} months, where the lead is the whole gap between the reading month and the return month ({W.n_candidates} declared combinations; {W.n_distinct} distinct position series). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{_RID}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe}, test-period Sharpe {W.oos_sharpe}. For reference only and not the selection rule, the single raw highest training Sharpe on this track ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}.
- As revised today (hindsight): `{_RID_REVISED}`, training Sharpe {W.comparison_is_sharpe}, test-period Sharpe {W.comparison_oos_sharpe}.{_COMP_TAIL}
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.
- Chance check: across {W.null_draws} contests run on circularly shifted orders data, {_CHANCE_TEXT}.
- Rule shown on the main site (legacy method): `{_MS_RULE}` ({_MS['direction']}), chosen by its legacy test-period Sharpe of {_MS['oos_sharpe']:.2f}; not replayed as a selection rule because it consulted the test period.
- Earlier run (a research run of {W.previous_tag}, never on the main site): `{W.previous_rule}` ({W.previous_selection}), earlier-run test-period Sharpe {W.previous_oos_sharpe}; replayed exactly on the new framework from that run's own data.
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `NEWORDER`, Manufacturers' New Orders: Nondefense Capital Goods Excluding Aircraft (all vintages).
2. U.S. Census Bureau, Advance Report on Durable Goods and Manufacturers' Shipments, Inventories, and Orders (M3).
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
        "data as known at the time. The as-known-at-the-time sample starts with the first archived vintage, whose "
        "history already covers the rolling windows; the revised comparison starts later because today's revised "
        "series begins later and its rolling statistics and leads need several years of readings first."
    ),
    plain_english=(
        "This page documents how core capital goods orders were turned into testable signals, how the econometric "
        "checks were run, and how the tournament selected the final SPY allocation rule on each data track."
    ),
)
