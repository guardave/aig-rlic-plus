"""UMCSENT x XLV pair configuration (Rule APP-PT1).

Phase B: every result number is rendered from the structured winner fields (results/umcsent_xlv/winner_summary.json
`winner_fields`, via components.winner_fields), the track summary, or the evidence tables declared in
evidence_facts_<tag>.json; none is typed here (scripts/gate_structured_prose.py, scripts/gate_number_provenance.py).
MAIN = as known at the time (real-time UMCSENT vintages); COMPARISON = as revised today (hindsight).
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "umcsent_xlv"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_EF = P.json_file(_RES / f"evidence_facts_{_TAG}.json")
_D = _EF.get("derived", {})
_EXP = _RES / f"exploratory_{_TAG}"
_CORE = _RES / f"core_models_{_TAG}"
_Q = P.col_dict(P.csv_file(_EXP / "regime_descriptive_stats.csv"), "regime", "sharpe")
_CORR = P.csv_file(_EXP / "correlations.csv")
_CCF = P.csv_file(_EXP / "ccf.csv")
_TS = P.json_file(_RES / "track_summary.json")
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"

_R_YOY6 = _CORR[(_CORR["signal"] == "umcsent_yoy") & (_CORR["horizon"] == "xlv_fwd_6m") & (_CORR["method"] == "Pearson")]
_R_YOY6 = _R_YOY6["correlation"].iloc[0] if len(_R_YOY6) else float("nan")
_LEAD_CCF = _CCF[_CCF["lag"].astype(float) > 0]
_CCF_PEAK = _LEAD_CCF.loc[_LEAD_CCF["ccf"].astype(float).idxmax()] if len(_LEAD_CCF) else None
_CCF_SIG_LAGS = list(_LEAD_CCF.loc[_LEAD_CCF["significant"].astype(bool), "lag"])
_LAG_CCF = _CCF[_CCF["lag"].astype(float) < 0]
_CCF_SIG_REV = [abs(x) for x in _LAG_CCF.loc[_LAG_CCF["significant"].astype(bool), "lag"]]
_G_FWD = _D.get("granger_min_p_umcsent_to_xlv")
_G_REV = _D.get("granger_min_p_xlv_to_umcsent")


def _p(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def _r71_caveat() -> str:
    """Chance-check calibration disclosure (R7.1), rendered from the null diagnosis in track_summary.json."""
    fails = [(lbl, d) for lbl, ok, d in (("as known at the time", _NT.get("r71_pass"), _NT.get("r71_diagnosis")),
                                         ("as revised today", _NT.get("revised_r71_pass"), _NT.get("revised_r71_diagnosis")))
             if ok is False]
    if not fails:
        return ""
    body = " ".join(f"On data {lbl}: {d['reading']}" if d else f"On data {lbl}: no diagnosis recorded."
                    for lbl, d in fails)
    return ("6. **Chance-check calibration.** The scrambled contests should show no timing skill on average "
            "(the R7.1 check); here they do not meet it. " + body + " Where the check is not met, that track's "
            "chance-check percentile compares its winner against a null that carries the same effect.\n")


_R71_CAVEAT = _r71_caveat()

THRESHOLD_TEXT = P.definitions({
    "T1_fixed_p25": "its training-period 25th percentile", "T1_fixed_p50": "its training-period median",
    "T1_fixed_p75": "its training-period 75th percentile",
    "T2_roll_p25": "its rolling 60-month 25th percentile", "T2_roll_p50": "its rolling 60-month median",
    "T2_roll_p75": "its rolling 60-month 75th percentile",
    "T3_zscore_1.0": "its rolling 60-month mean plus 1.0 standard deviation",
    "T3_zscore_1.5": "its rolling 60-month mean plus 1.5 standard deviations",
    "T3_zscore_2.0": "its rolling 60-month mean plus 2.0 standard deviations",
    "T3_zscore_neg_1.0": "its rolling 60-month mean minus 1.0 standard deviation",
    "T3_zscore_neg_1.5": "its rolling 60-month mean minus 1.5 standard deviations",
    "T3_zscore_neg_2.0": "its rolling 60-month mean minus 2.0 standard deviations",
    "T4_zero": "zero", "-": "its trailing 60-month range",
})
SIDE = {"procyclical": "above", "countercyclical": "below"}
SIGNAL_TEXT = P.definitions({
    "S1_level": "consumer sentiment level", "S2_yoy": "year-over-year % change in consumer sentiment",
    "S3_mom": "month-over-month % change in consumer sentiment", "S4_zscore": "36-month consumer sentiment z-score",
    "S5_3m_ma": "3-month average of consumer sentiment", "S6_direction": "direction of the monthly sentiment change",
    "S7_dev_ma": "consumer sentiment minus its 3-month average",
})


def _sig(prefix: str = "") -> str:
    return SIGNAL_TEXT.get(W.value(prefix + "signal_code"), W.text(prefix + "signal_code"))


def _low(text: str) -> str:
    return text[:1].lower() + text[1:]


def _rule(prefix: str = "") -> str:
    """Plain-English rule of a track's winner, from its structured fields."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    fam = str(W.value(prefix + "strategy_family") or "")[:2]
    sig = f"the {_sig(prefix)} from {g('lead_word')} months earlier"
    thr = THRESHOLD_TEXT.get(g("threshold_code"), g("threshold_code"))
    side = SIDE.get(W.value(prefix + "direction"), g("direction"))
    if fam == "P2":
        return (f"size the XLV position by where {sig} sits within {thr}: fully invested at the top of the range, "
                "in cash at the bottom, in proportion in between; the rest is held in cash")
    if fam == "P3":
        return f"hold XLV long when {sig} is {side} {thr}; otherwise hold XLV short"
    return f"hold XLV when {sig} is {side} {thr}; otherwise hold cash"


_RULE = _rule()
_RULE_REVISED = _rule("comparison_")
_SAME_RULE = all(W.value(k) == W.value("comparison_" + k) for k in ("signal_code", "threshold_code", "lead",
                                                                    "strategy_family"))


class StoryConfig:
    PAGE_TITLE = "The Story: University of Michigan Consumer Sentiment and the Healthcare Sector"
    PAGE_SUBTITLE = (
        "Does University of Michigan consumer sentiment help time exposure to the defensive Health Care Select "
        "Sector SPDR Fund (XLV)?"
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold XLV, "
        "using consumer-sentiment data as known at the time"
    )

    PLAIN_ENGLISH = (
        "The University of Michigan survey (UMCSENT) asks households how confident they feel about their finances "
        "and the economy. This page asks whether that monthly reading can help time exposure to the Health Care "
        "Select Sector SPDR Fund (XLV). Health care is a defensive sector: people need care in good and bad times. "
        "The working hypothesis is procyclical: higher or improving sentiment should coincide with better XLV "
        "returns. The headline uses the survey values as they were published at each date, not today's revised "
        "values."
    )

    WHERE_THIS_FITS = (
        "This is a household-sentiment signal for a defensive equity sector. It belongs in the portal as regime "
        "context and a possible exposure filter, not as a standalone forecast."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; in the test "
        f"period it scored Sharpe {W.oos_sharpe} against {W.bh_oos_sharpe} for buy-and-hold XLV."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{_sig()}, {W.threshold_code}, {W.strategy_family}, lead {W.lead_text}. Test-period Sharpe "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold XLV ({W.oos_start} to {W.oos_end})."
    )

    HERO_TITLE = "UMCSENT Year-over-Year Change vs. Health Care Select Sector SPDR Fund (XLV)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the year-over-year change in UMCSENT is on the left axis and the XLV adjusted price on "
        "the right axis. Shaded bands mark months with a negative year-over-year change. Prices often react "
        "first, while household sentiment updates through a monthly survey."
    )

    REGIME_TITLE = "What History Shows: XLV Returns by Consumer-Sentiment Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted into quartiles of the year-over-year change in UMCSENT, from Q1 "
        f"(largest declines) to Q4 (largest gains). XLV Sharpe in the same months: Q1 {_Q['Q1_low']:.2f}, "
        f"Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4_high']:.2f}."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: every month the rule reads consumer sentiment as it was published then, not today's revised values.

The winning rule is a **{_sig()} rule**: {_RULE}. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations. In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold XLV, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

On today's revised data (hindsight, for comparison only) the selected rule is to {_RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

### Why Consumer Sentiment and Health Care?

The Michigan index is one of the most watched household surveys: respondents describe their own finances, the economy over the next year and conditions further out. Because it is published within the survey month, it is available to an investor almost immediately and is rarely revised afterwards.

### The Defensive-Healthcare Hypothesis

When households feel confident they spend more freely, including on discretionary health services, and risk appetite tends to be higher. When confidence falls, spending is cut back. Health care is partly defensive, so the sentiment effect on XLV may be weaker than on cyclical sectors; that is exactly what this pair tests.
"""

    NARRATIVE_SECTION_2 = f"""
### What History Shows

The quartile chart sorts months by the year-over-year change in sentiment. XLV's Sharpe in the lowest quartile is {_Q['Q1_low']:.2f} and in the highest {_Q['Q4_high']:.2f}; the middle quartiles are {_Q['Q2']:.2f} and {_Q['Q3']:.2f}. The relationship is descriptive and concurrent: it is not the lagged trading rule.

The main limits are sample length (XLV starts in {_D.get('xlv_first_month', '[missing: xlv_first_month]')}) and the sector-specific forces on XLV (health-care policy, drug pricing, demographics, the COVID-19 pandemic) that move the sector independently of household sentiment.
"""

    SCOPE_NOTE = (
        "*Scope discipline.* Only University of Michigan Consumer Sentiment transforms are trading signals. The "
        "unemployment rate, the Treasury yield (DGS10) and the CBOE Volatility Index (VIX) are used only as "
        "regression controls."
    )

    TRANSITION_TEXT = (
        "The Evidence page tests whether this sentiment story survives correlation, lead-lag, regime and "
        "distribution checks."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust (2000-2002)",
            "narrative": (
                "Consumer sentiment deteriorated through 2001 as the economy contracted and unemployment rose, while "
                "XLV, a defensive holding, held up comparatively well."
            ),
            "caption": "2001 sentiment decline alongside a defensive XLV. NBER recession shading marks the official recession window.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007-2009)",
            "narrative": (
                "Sentiment collapsed through 2008-2009 as unemployment surged and household wealth fell. XLV declined "
                "as well, though less than the broad market."
            ),
            "caption": "Global Financial Crisis: sentiment and XLV both fell. NBER recession shading marks the official recession window.",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": (
                "Sentiment plunged in April 2020. XLV had a short drawdown and then recovered quickly on health-care "
                "demand, an example of a monthly survey lagging a fast market recovery."
            ),
            "caption": "COVID: sentiment collapsed in April 2020; XLV recovered quickly. NBER recession shading marks the official recession window.",
        },
        {
            "slug": "inflation_2022",
            "title": "Fed Hiking Cycle (2022)",
            "narrative": (
                "Sentiment reached multi-decade lows in mid-2022 on inflation and rising rates, while XLV held up "
                "better than the broad market: weak sentiment can coexist with defensive-sector strength."
            ),
            "caption": "2022: record-low sentiment while XLV held up defensively.",
        },
    ]


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Sector Correlation Analysis",
    method_theory=(
        "This test asks whether the indicator and target move together in a roughly straight-line way. Pearson "
        "correlation fits a broadly linear cloud; Spearman rank correlation is the backup when the relationship is "
        "monotonic but curved or affected by extreme observations."
    ),
    question="Does a higher year-over-year change in UMCSENT line up with stronger future XLV returns?",
    how_to_read=(
        "Each point is a monthly observation. The x-axis is the year-over-year change in UMCSENT; the y-axis is XLV's 6-month "
        "forward return. A tilted straight-line cloud means linear correlation summarizes the relationship well."
    ),
    chart_name="correlation_scatter",
    chart_caption=(
        f"What this shows: the Pearson correlation between the year-over-year change in UMCSENT and XLV's 6-month "
        f"forward return is {_R_YOY6:.2f} on the revised data."
    ),
    observation=(
        f"The point cloud has a Pearson correlation of {_R_YOY6:.2f}, with wide scatter around the fit line: the "
        "relationship is not a precise month-by-month forecast."
    ),
    interpretation=(
        "Linear correlation is a first diagnostic only; the Evidence page also uses quartile regimes, distribution "
        "analysis and lead-lag tests."
    ),
    key_message="UMCSENT's linear relationship with future XLV returns is noisy; regime and distribution checks are needed.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality and Cross-Correlation",
    method_theory=(
        "Granger causality asks whether past UMCSENT values improve forecasts of XLV returns beyond XLV's own recent "
        "history. Both directions are tested at lags 1-6 months. The cross-correlation chart shows the "
        "lead-lag pattern of the standardized series."
    ),
    question=(
        "Does consumer sentiment carry information about future health-care equity returns that is not already "
        "priced into XLV itself?"
    ),
    how_to_read=(
        "Positive lags on the chart mean UMCSENT moved before XLV returns. Bars outside the dashed 95% band are "
        "statistically notable. Granger p-values are read separately; p < 0.05 indicates predictive content."
    ),
    chart_name="ccf",
    chart_caption=(
        "Cross-correlation between the year-over-year change in UMCSENT and the XLV monthly return at lags -12 to "
        "+12 months. Highlighted bars are significant at 95% confidence."
    ),
    observation=(
        (f"Among the lags where UMCSENT leads, the cross-correlation peaks at lag {_CCF_PEAK['lag']} "
         f"({_CCF_PEAK['ccf']:.2f}); significant leading lags: "
         f"{', '.join(str(x) for x in _CCF_SIG_LAGS) if _CCF_SIG_LAGS else 'none'}. " if _CCF_PEAK is not None else "")
        + ("Significant lags where XLV returns move first (months): "
           f"{', '.join(str(x) for x in _CCF_SIG_REV) if _CCF_SIG_REV else 'none'}. ")
        + f"The smallest Granger p-value from UMCSENT to XLV is {_p(_G_FWD)}; from XLV to UMCSENT it is "
        f"{_p(_G_REV)}."
    ),
    interpretation=(
        "Market and economic conditions also shape household confidence, so price information can explain later "
        "sentiment. The lead-lag evidence is not a clean one-way causal story; the strategy is a searched allocation "
        "overlay."
    ),
    key_message=f"Formal Granger evidence from UMCSENT to XLV is weak (smallest p-value {_p(_G_FWD)}).",
)

REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Descriptive Statistics)",
    method_theory=(
        "Months are sorted into four quartiles of the year-over-year change in UMCSENT and XLV return statistics "
        "are computed in each: the simplest regime test, with no model structure."
    ),
    question="Does XLV performance differ systematically across sentiment regimes?",
    how_to_read=(
        "Left panel: annualized Sharpe ratio in each quartile. Right panel: annualized return. Q1 holds the largest "
        "declines in sentiment, Q4 the largest gains."
    ),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: XLV Sharpe by sentiment quartile, Q1 {_Q['Q1_low']:.2f}, Q2 {_Q['Q2']:.2f}, "
        f"Q3 {_Q['Q3']:.2f}, Q4 {_Q['Q4_high']:.2f} (concurrent months, revised data)."
    ),
    observation=(
        f"Sharpe in the lowest-change quartile is {_Q['Q1_low']:.2f}; in the other quartiles {_Q['Q2']:.2f}, "
        f"{_Q['Q3']:.2f} and {_Q['Q4_high']:.2f}."
    ),
    interpretation=(
        "The regime pattern is concurrent, not lagged; it describes the sentiment backdrop rather than a trading "
        "rule. Whether extreme optimism is itself a late-cycle sign cannot be settled from four buckets."
    ),
    key_message="XLV returns differ across sentiment regimes; read the pattern as context, not a forecast.",
)

SIGNAL_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Signal Distribution Analysis",
    method_theory=(
        "XLV 3-month forward returns are compared between months when sentiment rose and months when it fell, to "
        "see whether the effect shifts the whole distribution or mainly the tails."
    ),
    question="When sentiment is rising, does the whole XLV return distribution shift, or only its tails?",
    how_to_read=(
        "Left panel: histogram of the year-over-year change in UMCSENT. Right panel: box plots of XLV 3-month "
        "forward returns when sentiment rose or fell over the month. Points beyond the whiskers are extreme "
        "observations, not data errors."
    ),
    chart_name="signal_dist",
    chart_caption=(
        "Left: distribution of the year-over-year change in UMCSENT. Right: XLV 3-month forward returns when "
        "sentiment rose or fell."
    ),
    observation=(
        "The return distributions of rising and falling months overlap substantially; compare their medians and lower whiskers on the chart."
    ),
    interpretation=(
        "This describes distribution shape, not trade win rate. A large overlap points to a weak average effect, "
        "which fits using the signal as a risk filter rather than a return forecast."
    ),
    key_message="Rising and falling sentiment months have overlapping XLV return distributions.",
)


_LP = P.col_dict(P.csv_file(_CORE / "local_projections.csv"), "horizon_months", "coef_umcsent_yoy")
_LPP = P.col_dict(P.csv_file(_CORE / "local_projections.csv"), "horizon_months", "p_value")
_LPDF = P.csv_file(_CORE / "local_projections.csv")
_LP_END = _LPDF["sample_end"].iloc[0]
_QRC = P.col_dict(P.csv_file(_CORE / "quantile_regression.csv"), "quantile", "coef_umcsent_yoy")
_QRP = P.col_dict(P.csv_file(_CORE / "quantile_regression.csv"), "quantile", "p_value")

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections regress XLV forward returns at several horizons on the year-over-year change in UMCSENT, "
        "with VIX and the Treasury yield (DGS10) as controls and HAC standard errors that allow for overlapping "
        "returns."
    ),
    question="How do XLV returns over the following months line up with the year-over-year change in sentiment?",
    how_to_read=(
        "Each bar is the change in the XLV forward return, in percentage points, per point of year-over-year "
        "change in UMCSENT; whiskers are 95% intervals. Whiskers that cross zero mean no clear effect. "
        f"The control series were pinned with the published run, so this regression sample ends in {_LP_END}."
    ),
    chart_name="local_projections",
    chart_caption="What this shows: the descriptive response of XLV forward returns across horizons, not the lagged trading rule.",
    observation=(
        "Slope p-values by horizon: " + "; ".join(f"{pv:.2f} at the {h}-month horizon" for h, pv in _LPP.items()) + "."
    ),
    interpretation=(
        "The slopes are small relative to their uncertainty, so the sentiment trend explains little of XLV's "
        "forward return variation."
    ),
    key_message="XLV's forward-return response to the sentiment trend is imprecisely estimated.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the sentiment trend relates differently to weak, typical and strong "
        "XLV 3-month forward returns."
    ),
    question="Does the year-over-year change in UMCSENT matter more in the tails of XLV returns?",
    how_to_read=(
        "Compare the slope across return quantiles; whiskers are 95% intervals from a moving-block bootstrap, "
        "because the overlapping 3-month returns make the default errors too small. A slope that changes sign or size "
        "across quantiles points to state-dependence, but only if the intervals separate."
    ),
    chart_name="quantile_coef",
    chart_caption="What this shows: the slope of the XLV 3-month forward return on the sentiment trend at each return quantile.",
    observation=(
        "Slope p-values by return quantile: " + "; ".join(f"{pv:.2f} at the {q:.2f} quantile" for q, pv in _QRP.items())
        + ". No cross-quantile equality test was run."
    ),
    interpretation=(
        "Read the per-quantile slopes as a description, not as evidence of tail asymmetry."
    ),
    key_message=("The quantile slopes are imprecise: an interval that excludes zero is isolated rather than a pattern, "
                 "and slope equality across quantiles was not tested."),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Consumer Sentiment and XLV",
    "overview": (
        "The tests below describe a sentiment overlay for a defensive sector, not a forecast. The selected rule's "
        f"test-period Sharpe is {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold XLV on data as known at "
        "the time."
    ),
    "plain_english": (
        "This page asks whether household sentiment helps with XLV timing, and how strong and stable that "
        "relationship is."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, REGIME_BLOCK, SIGNAL_DIST_BLOCK],
    "level1_labels": ["Correlation", "Granger / CCF", "Regimes", "Distribution"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} strategy combinations ({W.n_valid} valid on the training period) "
        f"across {P.length(_MAN['signals'])} UMCSENT transforms, fixed and rolling thresholds, long/cash, signal-strength "
        f"and long/short positions and the lead grid {_GRID_RANGE} months, on data as known at the time. The "
        f"selected winner is `{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, chosen on the "
        f"training period by {W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the evidence is useful but not causal. The Strategy page shows the exact rule, its "
        "threshold and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating UMCSENT Signals into XLV Positioning"
    PAGE_SUBTITLE = (
        f"A searched XLV allocation rule: {_sig()}, {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}, "
        f"lead {W.lead_text}, on consumer-sentiment data as known at the time."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-17). This page previously reported the rule {W.previous_rule} (test-period Sharpe "
        f"{W.previous_oos_sharpe}, published {W.previous_tag}), which was selected on its out-of-sample Sharpe "
        "(legacy method), on the data as downloaded for that run, with fixed lags. It now reports the rule selected on the "
        "training period only, on data as known at the time, with point-in-time release dates and the "
        "stable-lead-range rule; today's revised data are shown for comparison only."
    )

    PLAIN_ENGLISH = f"The rule is to {_RULE}. It is a lagged sentiment rule, not a real-time forecast."

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); this text states
    # facts only.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from consumer-sentiment data as known at the time; it has not faced a "
            "frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time sentiment values give a training period of {W.is_n} months ({W.is_start} to "
            f"{W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Formal lead-lag evidence is weak: smallest UMCSENT-to-XLV Granger p-value {_p(_G_FWD)}.",
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to "
            f"{W.ci_high}.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}).",
        ],
        conclusion=(
            f"Rule {W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}: test-period Sharpe "
            f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold XLV ({W.oos_start} to {W.oos_end}), maximum "
            f"drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on consumer-sentiment data as known at "
            "the time."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality", "path": f"results/{PAIR}/core_models_{_TAG}/granger_causality.csv"},
        {"label": "Regime quartile statistics", "path": f"results/{PAIR}/exploratory_{_TAG}/regime_descriptive_stats.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/{PAIR}/hindsight_tournament_results_{_TAG}.csv"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; position changes over the test period summing to {_D['oos_sum_abs_position_change']} full XLV units, with {_D['oos_months_position_change_gt_5pct']} months in which the position moved by more than {_D['position_change_threshold_pp']} percentage points (counted from the trade log's {_D['n_oos_trade_log_rows']} test-period rows, including the move into the first test month); annual turnover {W.annual_turnover}.
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, at each month end the process takes UMCSENT as it was published on that date (the vintage visible when the next month's return window opens). Second, inside that vintage it computes the {_sig()} and its threshold. Third, it uses the reading from {W.lead_word} months earlier. Finally, the reading is set against {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} and the position is held through the following month.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read UMCSENT as currently published.
2. Compute the {_sig()} from that published series.
3. Take its value from {W.lead_word} months earlier and read it against {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}.
4. Set the position as the rule says: {_RULE}.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Calendar-Year Sharpe"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_CAPTION = (
        "What this shows: test-period Sharpe of the rule by full calendar year against buy-and-hold XLV. It is not "
        "designed to make every year profitable."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_granger": (
            "How to read it: in each 24-month window the test asks whether lags of the year-over-year change in "
            "UMCSENT improve forecasts of the XLV return. Several lags are tried (the chart title names them), so the "
            "plotted p-value is the smallest lag p-value multiplied by the number of lags tried (Bonferroni). "
            "Periods below p = 0.05 indicate evidence in "
            "that window; the F statistic (at the lag with the smallest p-value) is supporting context."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: training versus test-period Sharpe across searched combinations (data as known at the "
        "time). The winner is chosen on the training period, not on its test-period score."
    )

    CAVEATS_MD = f"""
**Main caveats:**

1. Household sentiment and XLV influence each other; the Granger evidence from UMCSENT to XLV is weak (smallest p-value {_p(_G_FWD)}), so this is not a proven causal forecast.
2. XLV history begins in {_D.get('xlv_first_month', '[missing: xlv_first_month]')}, which limits the training and test periods.
3. The result is marked `found_in_search`; it still needs a frozen-rule hold-out confirmation.
4. The headline uses consumer-sentiment data as known at the time. On today's revised data the selected rule {'is the same' if _SAME_RULE else 'is different'} (test-period Sharpe {W.comparison_oos_sharpe}, hindsight); UMCSENT is rarely revised after publication.
5. Health-care policy, drug pricing and demographics move XLV independently of household sentiment.
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a trade each time the rule changes "
        f"the XLV position: {_RULE}."
    )


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (FRED vintages, pinned in data/release_calendar/vintages/UMCSENT.csv.gz) | `UMCSENT`, University of Michigan consumer sentiment, every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest vintage of the same file) | `UMCSENT` | Monthly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per month | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/xlv_month_end_20261017.csv) | XLV adjusted month-end close | Monthly |
| Regression controls | FRED / Yahoo Finance (pinned in data/phaseB_inputs/umcsent_xlv_monthly_legacy_20261008.csv) | `UNRATE`, `DGS10`, VIX | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the University of Michigan index of consumer sentiment. The pipeline constructs the "
    "year-over-year percent change, the month-over-month percent change, a 36-month rolling z-score, the 3-month "
    "average, the direction of the monthly change and the deviation from the 3-month average. On the "
    "as-known-at-the-time track every signal and rolling threshold is recomputed inside the vintage published when "
    f"each month's return window opens. The winning signal is `{W.signal_code}` ({_sig()}), used "
    f"with a lead of {W.lead_text} and {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} as threshold."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does UMCSENT move linearly with future XLV returns? | Simple baseline before richer tests |
| Regime quartiles | Do sentiment regimes behave differently? | Makes the sentiment story interpretable |
| Cross-correlation | Where is the lead-lag relationship strongest? | Lead-lag pattern of the standardized series |
| Granger causality | Does past UMCSENT information improve XLV forecasts, and the reverse? | Formal lead-lag check in both directions |
| Predictive and local-projection regressions | How do XLV forward returns respond across horizons? | Horizon-specific effects with robust errors |
| Quantile regression | Is the effect different in weak or strong return states? | Tail sensitivity |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: UMCSENT transforms x fixed, rolling and zero thresholds x long/cash, signal-strength and long/short positions x the procyclical orientation x leads {_GRID_RANGE} months ({W.n_candidates} combinations, {W.n_distinct} distinct position series). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe}, test-period Sharpe {W.oos_sharpe}. The single highest training Sharpe on this track ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}, shown for reference and not the selection rule.
- As revised today (hindsight): `{W.comparison_signal_code} / {W.comparison_threshold_code} / {W.comparison_strategy_family} / L{W.comparison_lead}`, training Sharpe {W.comparison_is_sharpe}, test-period Sharpe {W.comparison_oos_sharpe}.
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.
- Chance check: across {W.null_draws} contests run on circularly shifted sentiment data, the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores.
- Previously published rule: {W.previous_rule} (published {W.previous_tag}), selected on its out-of-sample Sharpe (legacy method).
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `UMCSENT`, University of Michigan: Consumer Sentiment (all vintages).
2. Surveys of Consumers, University of Michigan.
3. Yahoo Finance, XLV adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
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
        f"Monthly sample; training period {W.is_start} to {W.is_end} and test period {W.oos_start} to "
        f"{W.oos_end} on data as known at the time. XLV history limits the usable sample even though UMCSENT "
        "begins earlier."
    ),
    plain_english=(
        "This page documents how UMCSENT was turned into testable signals, how the econometric checks were run, "
        "and how the tournament selected the final XLV allocation rule on each data track."
    ),
)
