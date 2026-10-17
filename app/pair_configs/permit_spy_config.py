"""PERMIT x SPY pair configuration (Rule APP-PT1).

Phase B: every result number is rendered from the structured winner fields (results/permit_spy/winner_summary.json
`winner_fields`, via components.winner_fields) or from the evidence tables listed in evidence_facts; none is typed
here (scripts/gate_structured_prose.py, scripts/gate_number_provenance.py). MAIN = as known at the time (real-time
PERMIT vintages); COMPARISON = as revised today (hindsight). The previously published rule was selected on its
test-period score by the legacy method and is not replayable through the harness; the correction banner names it
from the previous_* fields.
"""

from __future__ import annotations

from pathlib import Path


from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

W = load("permit_spy")
_RES = Path(__file__).resolve().parents[2] / "results" / "permit_spy"
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_QR = P.col_dict(P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv"), "quantile", "coef")
_QT = P.json_file(_RES / f"core_models_{_TAG}" / "quantile_equality_test.json")
_LP_T = P.csv_file(_RES / f"core_models_{_TAG}" / "local_projections.csv")
_LP_COEF = P.col_dict(_LP_T, "horizon", "coef")
_LP_P = P.col_dict(_LP_T, "horizon", "p_value")
_G_MIN_P = P.colmin(P.csv_file(_RES / "granger_by_lag.csv"), "p_value")
_G_SIG = bool(_G_MIN_P < 0.05)
_TS = P.json_file(_RES / "track_summary.json")
_EV = P.json_file(_RES / f"evidence_facts_{_TAG}.json")["derived"]
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid("permit_spy")
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_EDGE = bool(((_WS.get("tracks") or {}).get("main") or {}).get("plateau", {}).get("grid_edge"))


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

THRESHOLD_TEXT = P.definitions({
    "T1_p25": "the 25th percentile of its earlier training-period readings",
    "T1_p50": "the median of its earlier training-period readings",
    "T1_p75": "the 75th percentile of its earlier training-period readings",
    "T2_rp25": "its rolling 60-month 25th percentile",
    "T2_rp50": "its rolling 60-month median",
    "T2_rp75": "its rolling 60-month 75th percentile",
    "T4_zero": "zero",
    "T_flag": "the contraction flag (year-over-year permit growth below zero)",
    "-": "its trailing 60-month range",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}
STRATEGY_TEXT = {"P1_long_cash": "long/cash", "P2_signal_strength": "signal-strength sizing",
                 "P3_long_short": "long/short"}


def _low(text: str) -> str:
    return text[:1].lower() + text[1:]


def _rule(prefix: str = "") -> str:
    """Plain-English rule of a track's winner, from its structured fields."""
    g = lambda n: getattr(W, prefix + n)  # noqa: E731
    fam = W.value(prefix + "strategy_family")
    sig = f"the {_low(g('signal_display'))} from {g('lead_word')} months earlier"
    if fam == "P2_signal_strength":
        more = "higher" if W.value(prefix + "direction") == "procyclical" else "lower"
        return (f"hold a share of SPY set by where {sig} sits in its trailing 60-month range (a {more} reading "
                "means more SPY), with the rest in cash")
    side = SIDE.get(W.value(prefix + "direction"), g("direction"))
    thr = THRESHOLD_TEXT.get(g("threshold_code"), g("threshold_code"))
    other = "short SPY" if fam == "P3_long_short" else "hold cash"
    return f"hold SPY when {sig} is {side} {thr}; otherwise {other}"


def _rid(prefix: str = "") -> str:
    """Rule id `signal / threshold / strategy family / L<lead>`; P2 sizes on the trailing range and has no threshold."""
    g = lambda n: getattr(W, prefix + n)  # noqa: E731
    parts = [g("signal_code")] + ([] if W.value(prefix + "threshold_code") == "-" else [g("threshold_code")])
    return " / ".join(parts + [g("strategy_family"), f"L{g('lead')}"])


_RULE = _rule()
_FINAL_STEP = ("the position is set by where that reading sits in its trailing 60-month range"
               if W.value("strategy_family") == "P2_signal_strength" else
               f"the reading is compared with {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}")
_RID = _rid()
_RID_REVISED = _rid("comparison_")
_RULE_REVISED = _rule("comparison_")
_SAME_RULE = W.value("signal_code") == W.value("comparison_signal_code") and W.value("lead") == W.value("comparison_lead") \
    and W.value("threshold_code") == W.value("comparison_threshold_code") \
    and W.value("strategy_family") == W.value("comparison_strategy_family")
_STRAT = STRATEGY_TEXT.get(W.value("strategy_family"), W.strategy_family)
_IS_P2 = W.value("strategy_family") == "P2_signal_strength"
_IF_THEN = (
    f"- **IF** `{W.signal_code}` from {W.lead_word} months earlier is at the top of its trailing 60-month range -> "
    "full SPY; at the bottom -> cash; in between -> the matching share of SPY"
    + (" (the scale is inverted for this countercyclical rule)." if W.value("direction") == "countercyclical" else ".")
    if _IS_P2 else
    f"- **IF** `{W.signal_code}` from {W.lead_word} months earlier is {SIDE.get(W.value('direction'), W.direction)} "
    f"{THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} -> hold SPY.\n"
    f"- **ELSE** -> {'short SPY' if W.value('strategy_family') == 'P3_long_short' else 'hold cash'}."
)


class StoryConfig:
    PAGE_TITLE = "The Story: Building Permits as a Leading Signal for SPY"
    PAGE_SUBTITLE = (
        "U.S. building permits (FRED PERMIT) x S&P 500 (SPY), monthly housing-cycle signals tested against SPY "
        "returns."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, "
        "using building-permit data as known at the time"
    )

    PLAIN_ENGLISH = (
        "Every month the Census Bureau reports how many new housing units local governments authorized. Builders "
        "apply for permits before they break ground, so the count is an early read on residential construction "
        "and the wider economy. This pair tests whether permit level, growth and momentum signals can improve SPY "
        "timing. The headline uses the permit figures that were published at each date, not today's revised "
        "figures; permits are revised every month and again each year when seasonal factors are updated."
    )

    WHERE_THIS_FITS = (
        "Building permits are a component of the Conference Board Leading Economic Index and one of the oldest "
        "leading indicators in the catalogue. In the portal it is a housing-cycle signal for broad U.S. equities."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; in the "
        f"test period it scored Sharpe {W.oos_sharpe} against {W.bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{W.signal_display}, {'trailing-range sizing' if _IS_P2 else W.threshold_code}, {_STRAT}, lead {W.lead_text}. "
        f"Test-period Sharpe {W.oos_sharpe} "
        f"versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end})."
    )

    HERO_TITLE = "Building Permits vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the permit level (left axis) is shown with SPY (right axis) on the same time axis. Gray "
        "bands are NBER recessions; pink bands mark months when year-over-year permit growth was negative."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Permit-Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        f"What this shows: months sorted by year-over-year permit growth, from Q1 (weakest) to Q4 (strongest). "
        f"Same-month SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, {_Q['Q3']:.2f} in Q3 and "
        f"{_Q['Q4']:.2f} in Q4."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: every month the rule reads building permits as they were published then, not today's revised figures.

The winning rule is a **{_low(W.signal_display)} rule** ({_STRAT}): {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations ({W.n_distinct} distinct position series). In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

On today's revised data (hindsight, for comparison only) the selected rule is to {_RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

### The Housing-Cycle Hypothesis

Permits are a commitment to future construction. When builders expect demand they file more permits; when credit tightens or demand fades they stop. Construction then feeds employment, materials demand and household wealth, so a turn in permits can precede a turn in the broader economy and in corporate earnings.

### Why Timing Is Difficult

Housing is one cycle among several. Equity drawdowns driven by technology valuations, by a pandemic or by an inflation and rate shock need not show up in permits first, and permits respond to mortgage rates that also move equity valuations directly.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust",
            "narrative": (
                "Permits held up through the dot-com bust: the downturn was concentrated in technology and "
                "business investment, not housing. A housing signal had little to say about this equity bear market."
            ),
            "caption": "Dot-Com: housing held up while equities fell.",
        },
        {
            "slug": "gfc",
            "title": "Housing Bust and Global Financial Crisis",
            "narrative": (
                "Permits peaked and fell for several years before and during the financial crisis. This is the "
                "episode where housing led the equity cycle most clearly."
            ),
            "caption": "Housing bust: permits fell well before the equity peak.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Permits collapsed briefly in spring 2020 and rebounded within months on pandemic-era housing demand. "
                "The shock was external and fast, so any lagged monthly signal reacted late."
            ),
            "caption": "COVID: brief permit collapse and fast rebound.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "As mortgage rates rose in 2022, permits turned down while equities sold off on higher discount "
                "rates. Both reacted to the same rate shock, which is one reason housing and equity signals overlap."
            ),
            "caption": "2022: permits and equities both reacted to higher rates.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The episodes suggest permits carry the most information in slow, housing-led cycles and little about shocks that start elsewhere. They are context for reading the strategy result, not evidence that the rule adds value; the test-period comparison with buy-and-hold is on the Strategy page.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this housing-cycle story survives correlation, lead-lag, regime, and "
        "strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether permit signals and future SPY returns move together in a roughly linear way."
    ),
    question="Do stronger permit readings line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by signal and horizon. Positive values mean stronger permit readings line up with "
        "stronger future SPY returns; negative values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: linear correlations between each permit transform and forward SPY returns at several "
        "horizons."
    ),
    observation=(
        "Levels and growth rates are persistent, so overlapping forward-return correlations overstate how much "
        "independent evidence there is."
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
    question="Does past permit growth help forecast SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show the p-value of the test at each monthly lag; bars below the 0.05 line mark lags where past "
        "permit growth adds forecasting information."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"What this shows: the smallest permit-to-SPY Granger p-value across lags is {_G_MIN_P:.2f}."
    ),
    observation=(
        f"The smallest p-value across lags is {_G_MIN_P:.2f}"
        + (", below the 0.05 line." if _G_SIG else "; no lag is below the 0.05 line.")
    ),
    interpretation=(
        "A Granger result is a statement about linear forecasting on revised data, not proof that permits cause "
        "SPY returns."
    ),
    key_message="Formal lead-lag evidence is reported as tested; read it with the tournament, not instead of it.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by year-over-year permit growth and compares SPY returns across the quartile "
        "groups."
    ),
    question="Do weak and strong permit-growth regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 holds the weakest permit growth; Q4 the strongest. Compare Sharpe, average return and sample size."
    ),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-month SPY Sharpe by permit-growth quartile, {_Q['Q1']:.2f} in Q1 (weakest) and "
        f"{_Q['Q4']:.2f} in Q4 (strongest)."
    ),
    observation=(
        f"SPY Sharpe in the same months: Q1 {_Q['Q1']:.2f}, Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4']:.2f}."
    ),
    interpretation=(
        "Quartiles are concurrent, not predictive: they show the backdrop, while the tournament tests lagged rules."
    ),
    key_message="Permit-growth regimes describe the equity backdrop.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Cross-correlation on first differences filters persistence before testing whether one series tends to "
        "move before or after the other."
    ),
    question="At which offsets do changes in permit growth line up with SPY returns?",
    how_to_read="Bars outside the dashed band mark offsets with unusually large correlation.",
    chart_name="ccf_prewhitened",
    chart_caption="What this shows: correlation of changes in permit growth with SPY returns at offsets in months.",
    observation="Permit growth is highly persistent, so differencing matters before reading lead-lag bars.",
    interpretation="Isolated significant bars are expected by chance across many offsets.",
    key_message="Housing-cycle timing is irregular.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns line up with permit growth over several horizons."
    ),
    question="How do forward SPY returns relate to year-over-year permit growth at different horizons?",
    how_to_read=(
        "Each bar is the estimated forward SPY return per percentage point of permit growth; whiskers are 95% "
        "confidence intervals."
    ),
    chart_name="local_projections",
    chart_caption=(
        f"What this shows: slopes from {_LP_COEF[1]:+.4f} at the 1-month horizon to "
        f"{_LP_COEF[12]:+.4f} at the 12-month horizon (p {_LP_P[12]:.2f} at the 12-month horizon)."
    ),
    observation="The raw macro relationship is shown here, not the final lagged tournament rule.",
    interpretation=(
        "Overlapping horizons share observations, so the longer-horizon estimates are less independent than they "
        "look."
    ),
    key_message="The horizon matters for permit signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether permit growth matters differently in weak, normal and strong SPY "
        "return environments."
    ),
    question="Does permit growth behave differently in market tails?",
    how_to_read="Compare the permit-growth coefficient across the quantiles of 3-month forward SPY returns.",
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: slopes of 3-month forward SPY returns on permit growth, {_QR[0.1]:+.4f} at tau=0.10 and "
        f"{_QR[0.5]:+.4f} at tau=0.50; a cross-quantile equality test does "
        f"{'not ' if not _QT['reject_equality'] else ''}reject a uniform slope (Wald p={_QT['p_value']:.2f})."
    ),
    observation=(
        f"The bootstrap Wald test {'does not reject' if not _QT['reject_equality'] else 'rejects'} slope equality "
        f"across quantiles (p={_QT['p_value']:.2f})."
    ),
    interpretation=(
        "Tail asymmetry is only established if the equality test rejects; otherwise read the slopes as imprecise."
    ),
    key_message=f"Cross-quantile equality Wald p={_QT['p_value']:.2f}.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Building Permits and SPY",
    "overview": (
        "The tests below describe a housing-cycle overlay. The selected rule's test-period Sharpe is "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold on data as known at the time."
    ),
    "plain_english": (
        "This page asks whether building permits help with SPY timing, first with descriptive tests on today's "
        "revised data, then with the tournament on data as known at the time."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} declared strategy combinations ({W.n_valid} valid on the training "
        f"period; {W.n_distinct} distinct position series, the others repeat a series exactly) "
        f"across {P.length(_MAN['signals'])} permit transforms, fixed and rolling thresholds, long/cash, signal-strength "
        f"and long/short strategies, both orientations and the lead grid {_GRID_RANGE} months, on data as known at "
        f"the time. The selected winner is `{_RID}`, "
        f"chosen on the training period by {W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the Strategy page shows the exact rule, its threshold and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged Building-Permit Overlay for SPY"
    PAGE_SUBTITLE = (
        f"A searched SPY allocation rule: {_low(W.signal_display)}, {_STRAT}, lead {W.lead_text}, on building-permit "
        "data as known at the time."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-17). This page previously reported the rule {W.previous_rule} "
        f"({W.previous_selection}: test-period Sharpe {W.previous_oos_sharpe}, published {W.previous_tag}). That "
        "previously published rule was chosen by its test-period score with fixed lags, so its test-period result "
        f"was not a held-out result. That run used building permits as published on {W.previous_tag}. "
        "The page now reports the rule selected on the training period from "
        "data as known at the time, with point-in-time release dates and the stable-lead-range rule; today's "
        "revised data are shown for comparison only."
    )

    PLAIN_ENGLISH = (
        f"The rule is to {_RULE}. It is a lagged housing-cycle rule, not a real-time recession forecast."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from building-permit data as known at the time; it has not faced a "
            "frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time permit figures give a training period of {W.is_n} months ({W.is_start} to {W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to "
            f"{W.ci_high}.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}).",
            f"The previously published rule ({W.previous_rule}) was selected on its test-period score.",
        ] + ([f"The stable lead range {W.plateau_range} sits at the edge of the declared lead grid ({_GRID_RANGE} "
              "months); leads beyond the grid were not tested."] if _EDGE else []),
        conclusion=(
            f"Rule {_RID}: test-period Sharpe "
            f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end}), maximum "
            f"drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on building-permit data as known at the "
            "time."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/permit_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/permit_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/permit_spy/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/permit_spy/hindsight_tournament_results_{_TAG}.csv"},
        {"label": "Legacy reproduction of the previously published rule",
         "path": "results/permit_spy/legacy_reproduction_20260314.json"},
        {"label": "Stationarity tests", "path": f"results/permit_spy/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

If-then form:
{_IF_THEN}

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; position changes summing to {W.oos_n_trades} full SPY units over the test period (whole units; exact sum {_EV['oos_sum_abs_position_change']}), with {_EV['oos_months_position_change_gt_5pct']} months in which the position moved by more than {_EV['position_change_threshold_pp']} percentage points; annual turnover {W.annual_turnover}.
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, at each month end the process takes building permits (`PERMIT`) as they were published on that date (the figures visible when the month's return window opens). Second, inside that vintage it computes the {_low(W.signal_display)} and its threshold. Third, it uses the reading from {W.lead_word} months earlier, and the position is applied to the following month's return. Finally, {_FINAL_STEP}.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read PERMIT as currently published.
2. Compute the {_low(W.signal_display)} from that published series.
3. Take its value from {W.lead_word} months earlier; {_FINAL_STEP}.
4. Set the position as the rule says ({_STRAT}) and hold it for the following month.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The subperiod chart compares the searched rule "
        "with buy-and-hold SPY during major stress windows."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is year-over-year growth in building permits; the target is SPY "
            "returns. The rolling correlation tests whether their linear relationship is stable through time."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the PERMIT-SPY relationship changes enough "
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
- The headline uses permit data as known at the time. On today's revised data the selected rule {'is the same' if _SAME_RULE else 'is different'} (test-period Sharpe {W.comparison_oos_sharpe}, hindsight).
- The previously published rule ({W.previous_rule}, {W.previous_selection}) was chosen by its test-period score; it was reproduced from the legacy code (results/permit_spy/legacy_reproduction_20260314.json) but cannot be replayed on the new framework.
- Housing is one cycle among several; equity drawdowns that start elsewhere need not show up in permits first.
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records each change in the SPY position the "
        f"rule makes ({_STRAT}) "
        + (f"as the {_low(W.signal_display)} reading moves within its trailing 60-month range."
           if _IS_P2 else
           f"when the {_low(W.signal_display)} reading crosses {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}.")
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "month end",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "position change",
        "commission_bps": "5",
        "reason": f"{W.signal_code} {W.direction} "
                  + ("position resized to the trailing-range reading" if _IS_P2 else f"rule crossed {W.threshold_code}"),
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (FRED vintages, pinned in data/release_calendar/vintages/PERMIT.csv.gz) | `PERMIT`, new private housing units authorized by building permits, every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest vintage of the same file) | `PERMIT` | Monthly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per month | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is new private housing units authorized by building permits, in thousands at a seasonally "
    "adjusted annual rate. The pipeline constructs the level, year-over-year and month-over-month percent changes, "
    "the deviation from a 12-month average, a 60-month z-score, the 3-month change, the 6-month change, the acceleration of "
    "the monthly change and a contraction flag (year-over-year growth below zero). On the as-known-at-the-time "
    "track every signal and rolling threshold is recomputed inside the vintage published when each month's return "
    "window opens; training-period percentile thresholds use only earlier training readings. "
    f"The winning signal is `{W.signal_code}` ({_low(W.signal_display)}), used with a lead of {W.lead_text}; "
    f"{_FINAL_STEP}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Do permit signals move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong permit-growth regimes behave differently? | Makes the housing-cycle story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past permit growth improve SPY forecasts? | Formal lead-lag check |
| Local projections | How do forward SPY returns relate to permit growth over horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: permit transforms x training-percentile, rolling-percentile and zero thresholds x long/cash, signal-strength and long/short strategies x procyclical/countercyclical orientations x leads {_GRID_RANGE} months, with each position applied to the return of the month after it is set ({W.n_candidates} declared combinations; {W.n_distinct} distinct position series, the others repeat a series exactly). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{_RID}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe}, test-period Sharpe {W.oos_sharpe}. The single highest training Sharpe on this track ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}; it is shown for reference and is not the selection rule.
- As revised today (hindsight): `{_RID_REVISED}`, training Sharpe {W.comparison_is_sharpe}, test-period Sharpe {W.comparison_oos_sharpe}.
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.
- Chance check: across {W.null_draws} contests run on circularly shifted permit data, the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores.
- Previously published rule: `{W.previous_rule}` ({W.previous_selection}), test-period Sharpe {W.previous_oos_sharpe}; reproduced from the legacy code, not replayable on the new framework.
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `PERMIT`, New Private Housing Units Authorized by Building Permits (all vintages).
2. U.S. Census Bureau, New Residential Construction.
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Politis, D. N., and Romano, J. P. (1994). "The Stationary Bootstrap."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"Monthly sample; training period {W.is_start} to {W.is_end} and test period {W.oos_start} to "
        f"{W.oos_end} on data as known at the time. The permit vintage archive limits the as-known-at-the-time "
        "sample; the revised comparison uses the full SPY history."
    ),
    plain_english=(
        "This page documents how building permits were turned into testable signals, how the econometric checks "
        "were run, and how the tournament selected the final SPY allocation rule on each data track."
    ),
)
