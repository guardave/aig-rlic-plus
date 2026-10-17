"""Credit Card Delinquency Rate x SPY pair configuration (Rule APP-PT1).

QUARTERLY credit pair (FRB DRCCLACBN, not seasonally adjusted). Phase B: every result number is rendered
from the structured winner fields (results/cc_delinquency_spy/winner_summary.json `winner_fields`, via
components.winner_fields) or read from the evidence CSVs; none is typed here (scripts/gate_structured_prose.py).
MAIN = as known at the time (real-time DRCCLACBN vintages, archive from 2011); COMPARISON = as revised today.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from components.page_templates import MethodologyConfig
from components.winner_fields import load

W = load("cc_delinquency_spy")
_RES = Path(__file__).resolve().parents[2] / "results" / "cc_delinquency_spy"
_WS = json.loads((_RES / "winner_summary.json").read_text())
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_CORE = _RES / f"core_models_{_TAG}"
_Q = pd.read_csv(_RES / "regime_quartile_returns.csv").set_index("quartile")["sharpe"].to_dict()
_G = pd.read_csv(_RES / "granger_by_lag.csv")
_G_P = " / ".join(f"{p:.2f}" for p in _G["p_value"])
_G_MIN = float(_G["p_value"].min())
_C = pd.read_csv(_CORE / "correlations.csv")
_C_MAX = float(_C["value"].abs().max())
_C_MINP = float(_C["p_value"].min())
_CCF = pd.read_csv(_CORE / "ccf_prewhitened.csv")
_CCF_SIG = _CCF[_CCF["significant"]]
_CCF_TXT = (", ".join(str(int(x)) for x in _CCF_SIG["lag"]) if len(_CCF_SIG) else "none")
_LP = pd.read_csv(_CORE / "local_projections.csv")
_QT = json.loads((_CORE / "quantile_equality_test.json").read_text())
_SB = json.loads((_RES / "structural_break_cc_delinquency_spy.json").read_text())["max_abs_z"]
_ST = pd.read_csv(_RES / f"stationarity_tests_{_TAG}.csv").set_index(["variable", "test"])["p_value"]

SIGNAL_TEXT = {
    "level": "delinquency rate", "diff_1q": "quarter-on-quarter change in the delinquency rate",
    "chg_4q": "4-quarter change in the delinquency rate", "zscore_20q": "delinquency rate versus its 5-year history (z-score)",
}
THRESHOLD_TEXT = {
    "T0_zero": "zero", "T_z_0": "zero", "T_z_1.0": "a z-score of 1.0",
    "T_roll_p50": "its rolling 20-quarter median", "T_roll_p75": "its rolling 20-quarter 75th percentile",
}
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}
LEAN = {"countercyclical": "countercyclical (the credit-stress prior: hold equities when delinquency is low or falling)",
        "procyclical": "procyclical (hold equities when delinquency is high or rising, against the credit-stress prior)"}


def _rule(prefix: str = "") -> str:
    g = lambda n: getattr(W, prefix + n)  # noqa: E731
    return (f"hold SPY when the {SIGNAL_TEXT.get(g('signal_code'), g('signal_code'))} from {g('lead_word')} quarters "
            f"earlier is {SIDE.get(W.value(prefix + 'direction'), g('direction'))} "
            f"{THRESHOLD_TEXT.get(g('threshold_code'), g('threshold_code'))}; otherwise hold cash")


_RULE = _rule()
_RULE_REVISED = _rule("comparison_")
_DIR = W.value("direction")


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Credit-Card Delinquency as a Credit-Stress Overlay"
    PAGE_SUBTITLE = (
        "Credit-Card Delinquency Rate (not seasonally adjusted, FRB series DRCCLACBN, % of balances 30+ days past "
        "due) x S&P 500 (SPY). QUARTERLY; a LAGGING credit indicator: all leads and windows are in QUARTERS."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, on delinquency data "
        "as known at the time (archive from 2011)"
    )

    PLAIN_ENGLISH = (
        "The credit-card delinquency rate is the share of card balances at least 30 days past due, a quarterly "
        "read on household financial stress. The economic prior is countercyclical: when delinquency is high or "
        "rising, consumers are struggling, recession risk is elevated, and you would want less equity. The "
        "headline result uses the delinquency figures as they were published at each date. Those published "
        "figures are archived only from 2011, so the training period for the headline result is short, and the "
        "rule should be read as a candidate, not a validated edge."
    )

    WHERE_THIS_FITS = (
        "This is a lagging CREDIT-STRESS context overlay for broad U.S. equities. Rising credit-card delinquency "
        "is a genuine household-stress gauge that climbed into the 2001, 2008, and post-2022 stress episodes; the "
        "formal tests do not find it forecasting SPY, so use it to read the credit cycle."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; it is "
        f"{LEAN.get(_DIR, _DIR)}, and in the test period it scored Sharpe {W.oos_sharpe} against "
        f"{W.bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}, {W.is_n} quarters as known at the time) by "
        f"{W.selection_objective}. Test period {W.oos_start} to {W.oos_end} ({W.oos_n} quarters). Sharpe ratios "
        "use quarterly annualization. Treat it as a candidate, not a verdict."
    )

    HERO_TITLE = "Credit-Card Delinquency Rate vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view of the credit-card delinquency rate (% of balances 30+ days past due, "
        "quarterly) and the S&P 500 (SPY) on a common time axis, NBER recessions shaded. Delinquency climbed "
        "through the 2001 and 2008 downturns and again after 2022: the signature of a lagging credit gauge."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Delinquency Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: concurrent S&P 500 (SPY) performance in each quartile of the 4-quarter change in "
        f"delinquency, from lowest (Q1) to highest (Q4). Concurrent SPY Sharpe is {_Q['Q1']:.2f} in Q1 and "
        f"{_Q['Q4']:.2f} in Q4. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = f"""
### Credit-card delinquency: a lagging credit-stress gauge

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: each quarter the rule reads the delinquency rate as it was published then. That archive starts in 2011, so the training period is only {W.is_n} quarters.

The credit-card delinquency rate (not seasonally adjusted, FRB series `DRCCLACBN`) is the percentage of credit-card loan balances at commercial banks that are at least 30 days past due. Because it is a lagging-to-coincident credit measure, it tends to rise into and through recessions rather than ahead of them. The economic prior is **countercyclical**: when delinquency is high or rising, equity exposure should be reduced.

**What the search selected.** The rule chosen on the training period is to {_RULE}. Its orientation is {LEAN.get(_DIR, _DIR)}. It was selected by {W.selection_objective} (stable lead range {W.plateau_range}) out of {W.n_valid} valid combinations. In the test period ({W.oos_start} to {W.oos_end}, {W.oos_n} quarters) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

**On today's revised data (hindsight, for comparison only)** the rule selected over the longer revised history is to {_RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

<!-- expander: What exactly is the credit-card delinquency series? -->
The delinquency rate on credit-card loans (FRED/FRB series `DRCCLACBN`) is the ratio of credit-card balances 30+ days past due to total credit-card balances at all commercial banks, expressed as a percentage. It is quarterly, **not seasonally adjusted (NSA)**, published in the Federal Reserve's charge-off and delinquency release roughly seven weeks after quarter end, and it is revised. Because it is NSA, the series carries quarterly seasonal swings of up to ~0.15 pp vs the seasonally adjusted series (DRCCLACBS); signals built on the level relative to a rolling percentile, or on short changes, can be partly driven by that seasonality. Higher readings mean more household distress.
<!-- /expander -->

### A quarterly credit pair: small samples, few cycles, explicit units

Leads are in QUARTERS; Sharpe ratios are annualized by the square root of 4. Credit-stress episodes are few, and the as-known-at-the-time archive covers only one of them before the test period, so any lead estimate rests on a small number of episodes.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession (2001)",
            "narrative": (
                "Credit-card delinquency drifted higher into and through the "
                "2001 downturn, the lagging-stress signature the credit prior "
                "expects. The market weakened as household and corporate credit "
                "conditions deteriorated."
            ),
            "caption": "Dot-Com: delinquency drifted higher through the downturn.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": (
                "Credit-card delinquency spiked to its highest levels in the "
                "sample as household balance sheets buckled — the clearest "
                "single illustration of delinquency as a credit-stress gauge. "
                "It rose alongside and after the deepest equity drawdown in the "
                "sample, confirming its lagging character."
            ),
            "caption": "GFC: delinquency spiked to sample highs.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "Fiscal support kept measured delinquency subdued in 2020 even "
                "as the equity crash and rebound played out within two quarters "
                "— far faster than a quarterly, lagging credit series can time. "
                "A reminder that the signal reads the credit cycle, not fast "
                "market shocks."
            ),
            "caption": "COVID: support programs kept delinquency subdued.",
        },
        {
            "slug": "rate_hike_2022",
            "title": "2022–24 Delinquency Upturn (Post-Pandemic Normalization)",
            "narrative": (
                "Delinquency climbed steadily off pandemic lows through the "
                "2022 rate-hike cycle and beyond, while equities fell in 2022 "
                "and recovered afterwards — one episode, inside the test period."
            ),
            "caption": "2022–24: delinquency normalized higher.",
        },
    ]

    NARRATIVE_SECTION_2 = f"""
### What the evidence and the search say together

The Evidence page shows no formal forecasting lead from delinquency to SPY (smallest Granger p-value {_G_MIN:.2f}). The rule on the Strategy page does not overturn that; it is a state description chosen on a short training window. Because the training period as known at the time is short and covers few credit cycles, the result is a candidate pattern awaiting a frozen-rule hold-out exam.

### What this means for investors

- **Read delinquency as credit-cycle context, not a market-timing signal.**
- **Compare the two data views.** The rule selected on revised data differs from the rule selected on data as known at the time; the as-revised-today result is hindsight.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this credit-stress story survives correlation, Granger, regime-quartile, "
        "cross-correlation, local-projection, and quantile checks."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE
# =========================================================================
CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
QUANTILE_CHART_NAME = "quantile_coef"


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Battery",
    method_theory=(
        "Pearson correlations between every delinquency transform (level, quarter-on-quarter change, 4-quarter "
        "change, 20-quarter z-score) and forward SPY returns at 1-, 2-, and 4-quarter horizons."
    ),
    question="Is there any raw statistical association between credit-card delinquency today and stock returns over the coming quarters?",
    how_to_read=(
        "Rows are delinquency transforms, columns are forward-return horizons in QUARTERS; each cell's color "
        "shows the correlation. Pale cells mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        f"What this shows: the largest absolute correlation in the grid is {_C_MAX:.2f}; the smallest p-value is "
        f"{_C_MINP:.2f}."
    ),
    observation=(
        f"No transform shows a strong linear association with forward SPY at any quarterly horizon (largest "
        f"|r| {_C_MAX:.2f}, smallest p {_C_MINP:.2f})."
    ),
    interpretation=(
        "The magnitudes are too small to support a linear trading rule. Treat the heatmap as descriptive triage; "
        "the formal tests carry the weight."
    ),
    key_message="The raw association between delinquency and future stock returns is weak at every quarterly horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of the delinquency signal improve forecasts of SPY returns "
        "after accounting for SPY's own history, across quarterly lags 1-4."
    ),
    question="Does credit-card delinquency lead SPY returns in a formal lag test?",
    how_to_read="Bars show the test statistic at each quarterly lag; the CSV carries the p-values.",
    chart_name=GRANGER_CHART_NAME,
    chart_caption=f"What this shows: delinquency-to-SPY p-values by quarterly lag are {_G_P}.",
    observation=f"Across lags 1-4 quarters the p-values are {_G_P}; the smallest is {_G_MIN:.2f}.",
    interpretation=(
        "This prevents any causal-forecasting claim. Delinquency is framed as a lagging credit-stress context "
        "overlay, not proof that it forecasts SPY."
    ),
    key_message=f"Formal lead-lag evidence is absent (smallest p {_G_MIN:.2f}); use the signal as context only.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory="Quartile analysis sorts quarters by the 4-quarter change in delinquency and compares concurrent SPY returns.",
    question="Do quarters of falling and rising delinquency produce different SPY outcomes?",
    how_to_read="Q1 is the fastest-falling delinquency; Q4 the fastest-rising. Compare Sharpe across the four buckets.",
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: concurrent SPY Sharpe is {_Q['Q1']:.2f} / {_Q['Q2']:.2f} / {_Q['Q3']:.2f} / {_Q['Q4']:.2f} "
        "from Q1 to Q4."
    ),
    observation=(
        f"Concurrent SPY Sharpe is {_Q['Q1']:.2f} (Q1), {_Q['Q2']:.2f} (Q2), {_Q['Q3']:.2f} (Q3) and {_Q['Q4']:.2f} (Q4)."
    ),
    interpretation=(
        "Quarters with falling delinquency coincide with stronger concurrent equity performance in this sample, "
        "the pattern the countercyclical credit prior expects. Descriptive, not a lead."
    ),
    key_message="The concurrent quartile pattern is the clearest evidence on the credit prior; it is not a forecast.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' persistence before testing whether the delinquency "
        "signal tends to move before or after SPY returns."
    ),
    question="At which quarterly offsets does the delinquency signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag correlation after filtering autocorrelation. "
        "Negative offsets are the signal's past relative to the return."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=f"What this shows: offsets outside the band: {_CCF_TXT}.",
    observation=f"After pre-whitening, the offsets outside the confidence band are: {_CCF_TXT}.",
    interpretation="Supports a credit-context reading rather than a mechanical forecast.",
    key_message="No clean predictive lead on the forecasting side.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across 1-, 2-, and 4-quarter horizons after a "
        "change in the delinquency signal."
    ),
    question="How does SPY respond after credit-card delinquency changes?",
    how_to_read="Each bar is an estimated future SPY response after a rise in the 4-quarter delinquency change.",
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        f"What this shows: coefficients {', '.join(f'{c:.3f}' for c in _LP['coef'])} with p-values "
        f"{', '.join(f'{p:.2f}' for p in _LP['p_value'])} at 1, 2 and 4 quarters."
    ),
    observation=f"R-squared is at most {_LP['r_squared'].max():.3f} at any horizon.",
    interpretation="The raw macro relationship carries no measurable forward response.",
    key_message="SPY shows no robust dynamic response to credit-card delinquency changes.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression (statsmodels QuantReg per quantile) checks whether the delinquency signal matters "
        "differently in weak, normal, and strong SPY return environments; a bootstrap Wald test checks equality "
        "of the slopes across quantiles."
    ),
    question="Does credit-card delinquency behave differently in market tails?",
    how_to_read="Compare the signal coefficient across return quantiles; whiskers are 95% intervals.",
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        f"What this shows: the cross-quantile equality test {'rejects' if _QT['reject_equality'] else 'does not reject'} "
        f"a uniform slope (Wald p={_QT['p_value']:.2f})."
    ),
    observation=(
        "This replaces an earlier table that repeated one OLS slope at every quantile; the slopes are now real "
        f"quantile-regression estimates (equality Wald p={_QT['p_value']:.2f})."
    ),
    interpretation="No evidence the signal sharpens in market tails unless the equality test rejects.",
    key_message=f"No established tail asymmetry (equality Wald p={_QT['p_value']:.2f}).",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: A Credit-Stress Gauge With No Forecasting Lead",
    "overview": (
        "*One question, attacked several independent ways: does credit-card delinquency carry information about "
        f"FUTURE S&P 500 (SPY) returns? The tests converge on: not as a forecast (smallest Granger p {_G_MIN:.2f}).*\n\n"
        f"All statistics are computed on QUARTERLY revised data (`results/cc_delinquency_spy/core_models_{_TAG}/`)."
    ),
    "plain_english": (
        "This page asks whether credit-card delinquency helps forecast the stock market. The formal lead-lag tests "
        "(Granger, cross-correlation, local projections) find no reliable way to forecast SPY from delinquency at "
        "any quarterly lag. The Strategy page shows the rule the search selected, with its data basis."
    ),
    "downloads": [
        {"label": "Granger by lag, delinquency to SPY", "path": "results/cc_delinquency_spy/granger_by_lag.csv"},
        {"label": "Correlation battery", "path": f"results/cc_delinquency_spy/core_models_{_TAG}/correlations.csv"},
        {"label": "Pre-whitened CCF", "path": f"results/cc_delinquency_spy/core_models_{_TAG}/ccf_prewhitened.csv"},
        {"label": "Local projections", "path": f"results/cc_delinquency_spy/core_models_{_TAG}/local_projections.csv"},
        {"label": "Quantile regression", "path": f"results/cc_delinquency_spy/core_models_{_TAG}/quantile_regression.csv"},
        {"label": "Regime quartile returns", "path": "results/cc_delinquency_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe", "path": "results/cc_delinquency_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/cc_delinquency_spy/rolling_correlation_cc_delinquency_spy.csv"},
        {"label": "Stationarity tests (ADF/KPSS)", "path": f"results/cc_delinquency_spy/stationarity_tests_{_TAG}.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "level2_summary": {
        "title": "What the evidence adds up to",
        "body": (
            f"The correlation battery is weak at every quarterly horizon (largest |r| {_C_MAX:.2f}); Granger "
            f"p-values by lag are {_G_P}; the pre-whitened CCF offsets outside the band are {_CCF_TXT}; local "
            "projections and quantile regression show no measurable forward response. The clearest pattern is "
            "concurrent (the quartile sort). **Bottom line:** credit-card delinquency is a lagging credit-stress "
            "gauge, not a forecasting signal for SPY."
        ),
        "key_message": f"No forecasting lead (smallest Granger p {_G_MIN:.2f}).",
    },
    "tournament_intro": (
        "The statistical tests above ask whether the indicator forecasts. The tournament asks a pragmatic "
        "question: across the declared QUARTERLY trading rules built from this series, which one did best on the "
        f"training period? We tested {W.n_candidates} combinations ({W.n_valid} valid as known at the time): 4 signal "
        "transforms x threshold schemes x long/cash x both orientations x quarterly leads L2-L5. The winner is "
        f"`{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, chosen on the training period by "
        f"{W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is no forecasting lead. The next page shows the single rule the "
        "search selected on each data track, with its fragility flags."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Quarterly Long/Cash Credit Overlay"
    PAGE_SUBTITLE = (
        f"The rule selected on the training period from data as known at the time ({W.is_n} quarters from 2011); "
        "no frozen-rule hold-out test has been run yet."
    )

    PLAIN_ENGLISH = (
        f"The rule is to {_RULE}. In the test period ({W.oos_start} to {W.oos_end}) it scored Sharpe "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} "
        f"versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval "
        f"{W.ci_low} to {W.ci_high}). Read it as a candidate overlay found by search; its final exam on untouched "
        "data has not been run."
    )

    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="Candidate",
        status_detail=(
            "A FOUND-IN-SEARCH candidate selected on a short as-known-at-the-time training period; it has not faced "
            "a frozen-rule hold-out final exam."
        ),
        strengths=[
            "Credit-card delinquency is a genuine lagging credit-stress gauge with real economic content as "
            "credit-cycle context.",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}) rather than an isolated peak.",
        ],
        risks=[
            f"No forecasting mechanism: delinquency does not Granger-cause SPY at any tested quarterly lag "
            f"(smallest p {_G_MIN:.2f}).",
            f"Short training period as known at the time: {W.is_n} quarters ({W.is_start} to {W.is_end}).",
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to {W.ci_high}.",
            f"The rule selected on revised data differs (hindsight test-period Sharpe {W.comparison_oos_sharpe}).",
            f"The rolling correlation is sign-unstable; a structural-break proxy shows max |z| = {_SB:.2f}.",
        ],
        conclusion=(
            f"This long/cash overlay is a found-in-search candidate: rule {W.signal_code} / {W.threshold_code} / "
            f"L{W.lead}, test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe}, on a short as-known-at-the-time "
            "history with no forecasting lead in the formal tests. Suggestion from the as-known-at-the-time result; "
            "you judge."
        ),
    )

    DOWNLOADS = [
        {"label": "Winner summary", "path": "results/cc_delinquency_spy/winner_summary.json"},
        {"label": "Granger causality by lag", "path": "results/cc_delinquency_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/cc_delinquency_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/cc_delinquency_spy/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/cc_delinquency_spy/hindsight_tournament_results_{_TAG}.csv"},
        {"label": "Bootstrap validation", "path": f"results/cc_delinquency_spy/tournament_validation_{_TAG}/bootstrap.csv"},
        {"label": "Stationarity tests", "path": f"results/cc_delinquency_spy/stationarity_tests_{_TAG}.csv"},
        {"label": "Winner trade log (broker style)", "path": "results/cc_delinquency_spy/winner_trades_broker_style.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule:** {_RULE}. Orientation: {LEAN.get(_DIR, _DIR)}. (Family: {W.strategy_family}; signal `{W.signal_code}`, threshold `{W.threshold_code}`, lead L{W.lead} quarters, per `winner_summary.json`.)

If-then form (evaluated once per quarter):
- **IF** the {SIGNAL_TEXT.get(W.signal_code, W.signal_code)} from {W.lead_word} quarters earlier is {SIDE.get(_DIR, _DIR)} {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)} -> **HOLD SPY (100% invested)**.
- **ELSE** -> **HOLD CASH**.

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}, {W.oos_n} quarters; Sharpe annualized by the square root of 4): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} test-period trades (annual turnover {W.annual_turnover}).

**Read this as a candidate, not a validated edge.** The training period as known at the time is {W.is_n} quarters and the formal tests find no forecasting lead.
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
No formulas, three steps:

**What changes in the world:** households fall further behind on their credit-card payments, so the delinquency rate rises; or they catch up, and it falls. The Federal Reserve reports this quarterly (series `DRCCLACBN`, not seasonally adjusted), with a lag and subject to revision.

**What the signal measures:** each quarter, the rule takes the delinquency rate as it was published at that date, computes the {SIGNAL_TEXT.get(W.signal_code, W.signal_code)} inside that published series, and reads its value from {W.lead_word} quarters earlier against {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}.

**What decision it drives:** {SIDE.get(_DIR, _DIR)} the threshold -> HOLD the market; otherwise -> HOLD cash.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule works so you can replicate and audit "
        "it; it is **not** a recommendation to trade it. The quarterly routine is:\n\n"
        "1. **Pull the credit series** as currently published: FRB/FRED series `DRCCLACBN`.\n"
        f"2. **Compute the signal**: the {SIGNAL_TEXT.get(W.signal_code, W.signal_code)}.\n"
        f"3. **Apply the delay**: use the value from {W.lead_word} quarters earlier.\n"
        f"4. **Check the threshold**: is it {SIDE.get(_DIR, _DIR)} {THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}? "
        "See `winner_trade_log.csv` for the full signal/threshold path.\n"
        "5. **Take the position**: yes -> HOLD SPY (100%); otherwise -> HOLD cash. Re-evaluate once a QUARTER."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy vs buy-and-hold Sharpe across major credit-stress episodes. Episodes before "
        "2011 precede the as-known-at-the-time archive, so the rule holds cash there."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 4-quarter change in the credit-card delinquency rate; the target "
            "is SPY returns. The rolling correlation tests whether their linear relationship is stable through time."
        ),
        "structural_break": (
            "How to read it: the structural-break proxy asks whether the delinquency-SPY relationship changes enough "
            f"that one fixed model is unlikely to describe the whole sample; here max |z| = {_SB:.2f}."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: test-period Sharpe distribution across valid searched combinations by lead (data as known "
        "at the time). The winner is chosen on the training period, not on this test-period score."
    )

    CAVEATS_MD = f"""
**Why we do not call this a validated edge:**

1. **Short history as known at the time.** Published (real-time) delinquency figures are archived from 2011, so the training period is {W.is_n} quarters ({W.is_start} to {W.is_end}) and the test period {W.oos_n} quarters.
2. **No forecasting lead.** Delinquency to SPY Granger p-values by lag are {_G_P}; the rule reads a *state*, it does not forecast.
3. **Search selection.** The winner is one of {W.n_valid} valid combinations; across {W.null_draws} contests run on circularly shifted data, the winner's stable-range score ranks at the {W.null_percentile} point.
4. **Two data views disagree.** On today's revised data the selected rule is to {_RULE_REVISED} (hindsight).
5. **Data character.** QUARTERLY, revised, LAGGING and not seasonally adjusted. The raw level's ADF p-value is {_ST[('ccdelinq_level', 'ADF')]:.2f} (unit root not rejected); the 4-quarter change's is {_ST[('ccdelinq_chg_4q', 'ADF')]:.2f}.

**What this means:** the honest label is a **found-in-search CANDIDATE**. The prescribed next step is a final exam: freeze this rule and test it once on an untouched window.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a BUY when the lagged "
        f"{SIGNAL_TEXT.get(W.signal_code, W.signal_code)} moves {SIDE.get(_DIR, _DIR)} "
        f"{THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)}, taking exposure from 0% to 100% SPY. A SELL moves "
        "back to cash when the condition no longer holds. Every row is in `winner_trades_broker_style.csv`."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": f"{W.signal_code} {_DIR} rule crossed {W.threshold_code}; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (FRB vintages, pinned: data/release_calendar/vintages/DRCCLACBN.csv.gz) | `DRCCLACBN`, every published vintage (archive from 2011-05) | Quarterly |
| Indicator (as revised today) | Latest vintage of the same file | `DRCCLACBN` (delinquency rate on credit-card loans, all commercial banks, %, NSA) | Quarterly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per quarter | Quarterly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted quarter-end close | Quarterly |

QUARTERLY credit pair. The delinquency series is native quarterly, not seasonally adjusted (NSA), revised and lagging. No seasonal adjustment is applied in this pipeline.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the credit-card delinquency rate (% of balances 30+ days past due). The pipeline builds "
    "the level, the quarter-on-quarter change, the 4-quarter change and a 20-quarter rolling z-score; rolling "
    "thresholds use 20-quarter windows. On the as-known-at-the-time track every signal and threshold is "
    "recomputed inside the vintage published when each quarter's return window opens. The tradeable lead grid "
    f"runs L2-L5 QUARTERS (strict publication floor); the winner uses `{W.signal_code}` at L{W.lead}."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson) | Any raw association at any quarterly horizon? | Cheap triage before formal tests |
| Granger causality (lags 1-4q) | Does past delinquency forecast SPY? | Formal lead-lag check |
| Regime quartiles | Do falling- and rising-delinquency quarters behave differently? | Makes the credit story interpretable |
| Pre-whitened CCF (offsets -4..+4q) | At which quarterly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections | Where is SPY h quarters after a delinquency move? | Horizon-by-horizon honesty |
| Quantile regression (QuantReg + equality Wald test) | Does the signal predict tail risk? | Cyclical signals sometimes work at the left tail only |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range? | Guards against a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests on scrambled signals? | Measures what selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
"""

_TOURNAMENT_DESIGN_MD = f"""
Grid: 4 signal transforms x threshold schemes x long/cash x both orientations x QUARTERLY leads L2-L5 ({W.n_candidates} combinations). Each data track selects its own winner on its training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe} ({W.is_start} to {W.is_end}), test-period Sharpe {W.oos_sharpe}; {W.n_valid} valid combinations, {W.n_distinct} distinct position series.
- As revised today (hindsight): `{W.comparison_signal_code} / {W.comparison_threshold_code} / L{W.comparison_lead}`, training Sharpe {W.comparison_is_sharpe} ({W.comparison_is_start} to {W.comparison_is_end}), test-period Sharpe {W.comparison_oos_sharpe}.
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_cc_delinquency_spy.py` (harness spec `scripts/pair_spec_cc_delinquency_spy.py`), deterministic with fixed seeds. Charts: `scripts/generate_charts_cc_delinquency_spy.py`.
"""

_REFERENCES_MD = """
1. Board of Governors of the Federal Reserve System, *Charge-Off and Delinquency Rates on Loans and Leases at Commercial Banks*.
2. Federal Reserve Bank of St. Louis, ALFRED / FRED series `DRCCLACBN` (all vintages).
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods." *Econometrica*, 37(3), 424-438.
5. Mian, A. & Sufi, A. (2010). "Household Leverage and the Recession of 2007-09." *IMF Economic Review*, 58(1), 74-117.
6. Jorda, O. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161-182.
7. Politis, D. N., and Romano, J. P. (1994). "The Stationary Bootstrap." *JASA*, 89(428), 1303-1313.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"QUARTERLY credit pair. As known at the time: training {W.is_start} to {W.is_end} ({W.is_n} quarters), "
        f"test {W.oos_start} to {W.oos_end} ({W.oos_n} quarters). As revised today: training {W.comparison_is_start} "
        f"to {W.comparison_is_end}. Sharpe ratios use quarterly annualization; leads are in quarters."
    ),
    plain_english=(
        "One QUARTERLY credit series (the credit-card delinquency rate) and the S&P 500 ETF (SPY). The headline "
        "uses the delinquency figures as they were published at each date, which are archived from 2011; the "
        "as-revised-today view uses today's corrected figures over the longer history and is shown for comparison "
        "only. Every number on these pages is reproduced by one deterministic script."
    ),
)
