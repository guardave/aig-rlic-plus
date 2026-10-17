"""UNRATE x SPY pair configuration (Rule APP-PT1).

Phase B: every result number is rendered from the structured winner fields (results/unrate_spy/winner_summary.json
`winner_fields`, via components.winner_fields) or from the evidence CSVs; none is typed here
(scripts/gate_structured_prose.py). MAIN = as known at the time (real-time UNRATE vintages);
COMPARISON = as revised today (hindsight).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import lead_grid, load

W = load("unrate_spy")
_RES = Path(__file__).resolve().parents[2] / "results" / "unrate_spy"
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_QR = P.col_dict(P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv"), "quantile", "coef")
_QT = P.json_file(_RES / f"core_models_{_TAG}" / "quantile_equality_test.json")
_G_MIN_P = P.colmin(P.csv_file(_RES / "granger_by_lag.csv"), "p_value")
_TS = P.json_file(_RES / "track_summary.json")
_NT = _TS.get("null_tournament") or {}
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = lead_grid("unrate_spy")
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"


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
            "(the R7.1 check); here they do not meet it. " + body + " Where the check is not met, that track's chance-check "
            "percentile compares its winner against a null that carries the same effect.\n")


_R71_CAVEAT = _r71_caveat()

THRESHOLD_TEXT = P.definitions({
    "T_roll_p75": "its rolling 60-month 75th percentile", "T_roll_p90": "its rolling 60-month 90th percentile",
    "T_roll_p25": "its rolling 60-month 25th percentile", "T0_zero": "zero", "T_z_1.0": "a z-score of 1.0",
    "T_sahm_0.5": "the Sahm-rule level of 0.5",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}


def _low(text: str) -> str:
    """Sentence-case a display name inside a sentence (proper nouns such as Sahm keep their capital)."""
    return text if text.startswith("Sahm") else text[:1].lower() + text[1:]


def _rule(prefix: str = "") -> str:
    """Plain-English rule of a track's winner, from its structured fields."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    return (f"hold SPY when the {_low(g('signal_display'))} from {g('lead_word')} months earlier is "
            f"{SIDE.get(W.value(prefix + 'direction'), g('direction'))} {THRESHOLD_TEXT.get(g('threshold_code'), g('threshold_code'))}; "
            "otherwise hold cash")


_RULE = _rule()
_RULE_REVISED = _rule("comparison_")
_SAME_RULE = W.value("signal_code") == W.value("comparison_signal_code") and W.value("lead") == W.value("comparison_lead") \
    and W.value("threshold_code") == W.value("comparison_threshold_code")


class StoryConfig:
    PAGE_TITLE = "The Story: Unemployment Rate as a Defensive SPY Timing Signal"
    PAGE_SUBTITLE = (
        "U.S. unemployment rate (FRED UNRATE) x S&P 500 (SPY), monthly "
        "labor-market stress signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, "
        "using unemployment data as known at the time"
    )

    PLAIN_ENGLISH = (
        "UNRATE is the U.S. civilian unemployment rate. It measures the share "
        "of the labor force that is unemployed and actively looking for work. "
        "This pair tests whether unemployment level and change signals can "
        "improve SPY timing. Because unemployment is usually lagging, the "
        "result should be read as regime context, not as an early recession "
        "alarm. The headline uses the unemployment figures that were published "
        "at each date, not today's revised figures."
    )

    WHERE_THIS_FITS = (
        "This is a labor-market stress signal for broad U.S. equities. It "
        "belongs in the portal as a defensive macro overlay: useful for "
        "context and drawdown control, but not a standalone forecast."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; in the "
        f"test period it scored Sharpe {W.oos_sharpe} against {W.bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{W.signal_display}, {W.threshold_code}, lead {W.lead_text}. Test-period Sharpe {W.oos_sharpe} versus "
        f"{W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end})."
    )

    HERO_TITLE = "U.S. Unemployment Rate vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: UNRATE is shown with SPY on the same time axis. "
        "Recession bands and Sahm-style labor-stress shading show when the "
        "labor market was under pressure."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by UNRATE Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1, the lowest unemployment "
        "regime, to Q4, the highest unemployment regime. In this sample, "
        "higher UNRATE quartiles have higher same-month SPY Sharpe, which fits "
        "a lagging-cycle or recovery setup more than a clean warning signal."
    )

    NARRATIVE_SECTION_1 = f"""
### Headline Findings

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: every month the rule reads the unemployment rate as it was published then, not today's revised figures.

The winning rule is a **{_low(W.signal_display)} rule**. It reads that signal from {W.lead_word} months earlier and holds SPY only when it is {SIDE.get(W.value("direction"), W.direction)} {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}; otherwise it holds cash. It was selected on the training period ({W.is_start} to {W.is_end}) by {W.selection_objective} (stable lead range {W.plateau_range}), out of {W.n_valid} valid combinations. In the test period ({W.oos_start} to {W.oos_end}) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

On today's revised data (hindsight, for comparison only) the selected rule is to {_RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

### The Labor-Market Hypothesis

The unemployment rate is one of the clearest indicators of economic stress, but it usually moves late. Companies tend to cut jobs after demand has already slowed, and unemployment can keep rising after markets have started to recover.

That makes the hypothesis different from a classic leading indicator. A rising unemployment signal may identify a stressed regime, but the best equity opportunity can arrive after the stress is visible and policy or market expectations have already adjusted.

### Why Timing Is Difficult

UNRATE can stay elevated while SPY rallies. It can also rise sharply during recessions, when equity risk is still high. This dashboard therefore treats the pair as a searched labor-cycle overlay; the economics should not be overstated as direct causality.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "UNRATE rose after the equity bear market had already begun. "
                "This episode shows why labor data can register stress after "
                "the first market move rather than warn before it."
            ),
            "caption": "Dot-Com: labor stress followed the market break.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The unemployment rate climbed through the Global Financial "
                "Crisis and remained high into the early recovery. The signal "
                "is useful for stress context, but exact equity timing is hard."
            ),
            "caption": "GFC: clear stress signal, late market timing.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "UNRATE spiked suddenly during coronavirus disease 2019 "
                "(COVID-19). The shock was exogenous, and the labor-market "
                "series moved too abruptly to be a normal cycle guide."
            ),
            "caption": "COVID: extreme labor shock, fast market recovery.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022 rate-hike shock, unemployment stayed low "
                "while SPY sold off. This is the key caveat: labor data can "
                "miss valuation-driven equity drawdowns."
            ),
            "caption": "2022: low unemployment did not prevent an equity drawdown.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is useful but imperfect. UNRATE registers recessions and labor stress clearly, but it often moves after markets have moved. The strongest reading is not "unemployment predicts every drawdown"; it is that labor-market regimes can help size equity exposure after stress has become visible.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this labor-market story survives "
        "correlation, lead-lag, regime, and strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether UNRATE and future SPY returns move "
        "together in a roughly linear way."
    ),
    question="Does a higher unemployment rate line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and correlation type. Positive values "
        "mean higher labor stress lines up with stronger future SPY returns; "
        "negative values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the relationship is not a simple recession-warning "
        "line. The pair behaves more like a lagged cycle signal."
    ),
    observation=(
        "UNRATE is persistent and lagging, so the linear relationship depends "
        "on horizon and on whether the market is already looking past the "
        "labor downturn."
    ),
    interpretation=(
        "Correlation alone is not enough to trade the pair. The more relevant "
        "question is whether a lagged unemployment-change threshold improves "
        "portfolio behavior."
    ),
    key_message="UNRATE is useful as regime context, not as a simple linear SPY predictor.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does UNRATE lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show F-statistics by monthly lag. The source CSV p-values show "
        "whether the relationship is statistically meaningful."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"What this shows: the smallest UNRATE-to-SPY Granger p-value across lags 1-12 is {_G_MIN_P:.2f}."
    ),
    observation=(
        f"The Granger table shows no UNRATE-to-SPY lag with p below {_G_MIN_P:.2f}."
    ),
    interpretation=(
        "This prevents a strong causal claim. The strategy should be framed "
        "as a searched allocation overlay, not proof that unemployment causes "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is weak; use the signal cautiously.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by UNRATE level and compares "
        "subsequent SPY returns across labor-market regimes."
    ),
    question="Do low and high unemployment regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest unemployment regime; Q4 is the highest unemployment "
        "regime. Compare Sharpe, average return, and sample size across the "
        "four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: concurrent SPY Sharpe by unemployment quartile, from {_Q['Q1']:.2f} in Q1 (lowest "
        f"unemployment) to {_Q['Q4']:.2f} in Q4 (highest)."
    ),
    observation=(
        f"SPY Sharpe in the same months rises from {_Q['Q1']:.2f} in Q1 to {_Q['Q4']:.2f} in Q4 "
        f"(Q2 {_Q['Q2']:.2f}, Q3 {_Q['Q3']:.2f})."
    ),
    interpretation=(
        "This is consistent with a lagging-cycle setup: by the time "
        "unemployment is high, equity markets may already be pricing recovery "
        "or policy support."
    ),
    key_message="High unemployment regimes are not automatically bad for forward SPY returns.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters persistence before testing "
        "whether one series tends to move before or after the other."
    ),
    question="At which offsets does the unemployment signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the confidence band mark unusual lead-lag correlation "
        "after filtering autocorrelation."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the relationship is timing-sensitive and should "
        "not be read as a stable clock."
    ),
    observation=(
        "UNRATE is highly persistent, so filtering persistence is important "
        "before reading lead-lag bars."
    ),
    interpretation=(
        "The chart supports treating the pair as a regime overlay with "
        "variable timing rather than a mechanical forecast."
    ),
    key_message="Labor-cycle timing is irregular.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the unemployment signal."
    ),
    question="How does SPY respond after the unemployment rate changes?",
    how_to_read=(
        "Each point is an estimated future SPY response after a one-unit move "
        "in the 3-month UNRATE change signal. Confidence bands show estimation "
        "uncertainty."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: the local-projection results test the raw labor "
        "signal, not the final lagged tournament rule."
    ),
    observation=(
        "The chart helps separate raw macro relationships from the searched "
        "allocation rule."
    ),
    interpretation=(
        "If the response varies by horizon, that supports using explicit "
        "lead times in the tournament instead of assuming an immediate effect."
    ),
    key_message="The horizon matters for UNRATE signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the unemployment signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does UNRATE behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means the unemployment signal has a stronger association "
        "with that part of the SPY return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: quantile-regression slopes of 3-month forward SPY returns on the 3-month UNRATE change: "
        f"{_QR[0.1]:+.3f} at tau=0.10 and {_QR[0.5]:+.3f} at tau=0.50; a cross-quantile equality test does "
        f"{'not ' if not _QT['reject_equality'] else ''}reject a uniform slope (Wald p={_QT['p_value']:.2f})."
    ),
    observation=(
        f"Individual quantile slopes vary in sign, and the bootstrap Wald test "
        f"{'does not reject' if not _QT['reject_equality'] else 'rejects'} slope equality across quantiles "
        f"(p={_QT['p_value']:.2f}); the tail estimates carry wide confidence intervals."
    ),
    interpretation=(
        "The point estimates hint at state-dependence, but tail asymmetry is only established if the equality "
        "test rejects; read the slopes as imprecise."
    ),
    key_message=f"UNRATE's per-quantile SPY slopes are imprecise (cross-quantile equality Wald p={_QT['p_value']:.2f}).",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: UNRATE Is Useful, but Mostly as Lagging Regime Context",
    "overview": (
        "The tests below describe a labor-cycle overlay, not a forecast. Formal lead-lag evidence is weak and the "
        f"indicator is economically lagging; the selected rule's test-period Sharpe is {W.oos_sharpe} versus "
        f"{W.bh_oos_sharpe} for buy-and-hold on data as known at the time."
    ),
    "plain_english": (
        "This page asks whether the unemployment rate helps with SPY timing. "
        "The selected rule uses a delayed unemployment signal, so it should be "
        "treated as a regime and recovery signal, not as an early warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        f"The tournament tested {W.n_candidates} strategy combinations ({W.n_valid} valid on the training period) "
        f"across {P.length(_MAN['signals'])} UNRATE transforms, fixed and rolling thresholds, both orientations and the lead grid "
        f"{_GRID_RANGE} months, on data as known at the time. The selected winner is `{W.signal_code} / {W.threshold_code} / "
        f"{W.strategy_family} / L{W.lead}`, chosen on the training period by {W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the evidence is useful but not causal. The Strategy "
        "page shows the exact long/cash rule, threshold, and deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged UNRATE Long/Cash Overlay"
    PAGE_SUBTITLE = (
        f"A searched SPY allocation rule: {_low(W.signal_display)}, {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} "
        f"threshold, lead {W.lead_text}, on unemployment data as known at the time."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-17). This page previously reported the rule {W.previous_rule} (test-period Sharpe "
        f"{W.previous_oos_sharpe}, published {W.previous_tag}), which was the single highest training Sharpe on "
        "today's revised data with fixed release lags. It now reports the rule selected on data as known at the "
        "time, with point-in-time release dates and the stable-lead-range rule; today's revised data are shown "
        "for comparison only."
    )

    PLAIN_ENGLISH = (
        f"The rule is to {_RULE}. This is a lagged labor-cycle rule, not a real-time recession forecast."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); this text states
    # facts only.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from unemployment data as known at the time; it has not faced a "
            "frozen-rule hold-out test."
        ),
        strengths=[
            f"Point-in-time unemployment figures give a training period of {W.is_n} months ({W.is_start} to "
            f"{W.is_end}).",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"No forecasting mechanism in the formal tests: smallest Granger p-value {_G_MIN_P:.2f}.",
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to "
            f"{W.ci_high}.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}).",
        ],
        conclusion=(
            f"Rule {W.signal_code} / {W.threshold_code} / L{W.lead}: test-period Sharpe {W.oos_sharpe} versus "
            f"{W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end}), maximum drawdown "
            f"{W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, on unemployment data as known at the time."
        ),
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/unrate_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/unrate_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/unrate_spy/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/unrate_spy/hindsight_tournament_results_{_TAG}.csv"},
        {"label": "Stationarity tests", "path": f"results/unrate_spy/stationarity_tests_{_TAG}.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule in plain English:** {_RULE}.

If-then form:
- **IF** `{W.signal_code}` from {W.lead_word} months earlier is {SIDE.get(W.value("direction"), W.direction)} {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} -> hold SPY.
- **ELSE** -> hold cash.

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} test-period trades; annual turnover {W.annual_turnover}.
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
First, at each month end the process takes the unemployment rate (`UNRATE`) as it was published on that date (the published figures visible when the month's return window opens). Second, inside that vintage it computes the {_low(W.signal_display)} and its threshold. Third, it uses the reading from {W.lead_word} months earlier. Finally, the reading is compared with {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of test-period months with positive strategy return.
"""

    MANUAL_USE_MD = f"""
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. At month end, read UNRATE as currently published.
2. Compute the {_low(W.signal_display)} from that published series.
3. Take its value from {W.lead_word} months earlier and compare it with {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}.
4. Hold SPY when the reading is {SIDE.get(W.value("direction"), W.direction)} the threshold; otherwise hold cash.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. It is not designed to make every crisis profitable."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 3-month change in the U.S. "
            "unemployment rate; the target is SPY returns. The rolling "
            "correlation tests whether their linear relationship is stable "
            "through time. Large swings mean the strategy needs rolling "
            "thresholds and ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break test asks whether the "
            "UNRATE-SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship changed more materially across periods."
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

1. UNRATE is lagging; it often registers stress after markets have already moved.
2. Granger causality is weak in the generated test results, so this is not a proven causal forecast.
3. The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
4. The headline uses unemployment data as known at the time. On today's revised data the selected rule {'is the same' if _SAME_RULE else 'is different'} (test-period Sharpe {W.comparison_oos_sharpe}, hindsight).
5. The unemployment rate for October 2025 was never published (federal shutdown); the rule uses the latest published reading in that month.
{_R71_CAVEAT}
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        f"BUY when the {_low(W.signal_display)} reading moves {SIDE.get(W.value('direction'), W.direction)} "
        f"{THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when the condition no longer holds."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": f"{W.strategy_family}: {W.signal_code} {SIDE.get(W.value('direction'), W.direction)} {W.threshold_code}; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (FRED vintages, pinned in data/release_calendar/vintages/UNRATE.csv.gz) | `UNRATE`, civilian unemployment rate, every published vintage | Monthly |
| Indicator (as revised today) | FRED (latest vintage of the same file) | `UNRATE` | Monthly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per month | Monthly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted month-end close | Monthly |
""")

_INDICATOR_CONSTRUCTION_MD = P.definition_text(
    "The raw indicator is the U.S. civilian unemployment rate, in percent. "
    "The pipeline constructs the month-on-month change and multi-month changes (signal codes "
    f"{', '.join(f'`{c}`' for c in _MAN['signals'] if c.startswith('chg_'))}); a 60-month rolling z-score; and a "
    "Sahm-style labor stress measure. On the as-known-at-the-time track every signal and rolling threshold is recomputed inside "
    "the vintage published when each month's return window opens. "
    f"The winning signal is `{W.signal_code}` ({_low(W.signal_display)}), used with a lead of {W.lead_text} and "
    f"{THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} as threshold."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does UNRATE move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high unemployment regimes behave differently? | Makes the labor-cycle story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past UNRATE information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range rather than an isolated peak? | Guards against picking a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests run on scrambled signals? | Measures how much selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: UNRATE transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x leads {_GRID_RANGE} months ({W.n_candidates} combinations, {W.n_distinct} distinct position series). Each data track selects its own winner on the training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe}, test-period Sharpe {W.oos_sharpe}. The single highest training Sharpe on this track ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}; it is shown for reference and is not the selection rule.
- As revised today (hindsight): `{W.comparison_signal_code} / {W.comparison_threshold_code} / L{W.comparison_lead}`, training Sharpe {W.comparison_is_sharpe}, test-period Sharpe {W.comparison_oos_sharpe}.
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.
- Chance check: across {W.null_draws} contests run on circularly shifted unemployment data, the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores.
"""

_REFERENCES_MD = """
1. Federal Reserve Bank of St. Louis, ALFRED / FRED `UNRATE`, Civilian Unemployment Rate (all vintages).
2. Yahoo Finance, SPY adjusted price history.
3. Sahm, C. (2019). "Direct Stimulus Payments to Individuals."
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
        f"{W.oos_end} on data as known at the time. SPY history limits the usable sample even though UNRATE "
        "begins earlier."
    ),
    plain_english=(
        "This page documents how UNRATE was turned into testable signals, "
        "how the econometric checks were run, and how the tournament selected "
        "the final SPY allocation rule on each data track."
    ),
)
