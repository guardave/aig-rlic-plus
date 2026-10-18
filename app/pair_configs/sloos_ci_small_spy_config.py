"""SLOOS C&I lending standards (DRTSCILM) x SPY pair configuration (Rule APP-PT1).

QUARTERLY credit-survey pair. The data is the net percentage of banks tightening C&I standards for LARGE and
MIDDLE-MARKET firms (FRED DRTSCILM), not the small-firm series DRTSCIS that the pair id names. Phase B: every result
number is rendered from the structured winner fields (results/sloos_ci_small_spy/winner_summary.json
`winner_fields`, via components.winner_fields) or from the evidence tables listed in evidence_facts; none is typed
here (scripts/gate_structured_prose.py, scripts/gate_number_provenance.py). MAIN = as known at the time (real-time
DRTSCILM vintages, archive from 2010); COMPARISON = as revised today (hindsight). The previously published rule was
the raw in-sample Sharpe argmax on revised data with fixed lags; it replays through the harness.
"""

from __future__ import annotations

from pathlib import Path

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

PAIR = "sloos_ci_small_spy"
W = load(PAIR)
_RES = Path(__file__).resolve().parents[2] / "results" / PAIR
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_CORE = _RES / f"core_models_{_TAG}"
_Q = P.col_dict(P.csv_file(_RES / "regime_quartile_returns.csv"), "quartile", "sharpe")
_G = P.csv_file(_RES / "granger_by_lag.csv")
_G_MIN = P.colmin(_G, "p_value")
_G_MIN_HOLM = P.colmin(_G, "p_holm")
_C = P.csv_file(_CORE / "correlations.csv")
_C_MAX = P.colmaxabs(_C, "value")
_C_MINP = P.colmin(_C, "p_value")
_CCF = P.csv_file(_CORE / "ccf_prewhitened.csv")
_CCF_SIG = _CCF[_CCF["significant"].astype(bool)]
_CCF_POS = [int(x) for x in _CCF_SIG["lag"] if x > 0]
_CCF_TXT = ", ".join(str(x) for x in _CCF_SIG["lag"]) if len(_CCF_SIG) else "none"
_LP = P.csv_file(_CORE / "local_projections.csv")
_LP_MINP = P.colmin(_LP, "p_value")
_QT = P.json_file(_CORE / "quantile_equality_test.json")
_SP = P.csv_file(_RES / "subperiod_sharpe.csv")
_SB = P.json_file(_RES / f"structural_break_{PAIR}.json")
_ST = P.csv_file(_RES / f"stationarity_tests_{_TAG}.csv").set_index(["variable", "test"])["p_value"]
_TS = P.json_file(_RES / "track_summary.json")
_NT = _TS.get("null_tournament") or {}
_EV = P.json_file(_RES / f"evidence_facts_{_TAG}.json")["derived"]
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_GRID = P.lead_grid(PAIR)
_GRID_RANGE = f"L{_GRID[0]}-L{_GRID[-1]}"
_VIN0 = P.year(_WS["tracks"]["main"]["sample"]["first_vintage"])  # first archived real-time vintage (year)
_EDGE = bool(((_WS.get("tracks") or {}).get("main") or {}).get("plateau", {}).get("grid_edge"))
_HZ = list(_LP["horizon"])
_HZ_TXT = ", ".join(str(h) for h in _HZ[:-1]) + f" and {_HZ[-1]}"
_ANY_SIG = bool(_C_MINP < 0.05 or _G_MIN_HOLM < 0.05 or _LP_MINP < 0.05)

SIGNAL_TEXT = P.definitions({
    "level": "net share of banks tightening",
    "diff_1q": "quarterly change in the net share of banks tightening",
    "chg_4q": "4-quarter change in the net share of banks tightening",
    "zscore_20q": "net share of banks tightening versus its 5-year history (20-quarter z-score)",
})
THRESHOLD_TEXT = P.definitions({
    "T0_zero": "zero", "T_z_0": "zero", "T_z_1.0": "a z-score of 1.0",
    "T_roll_p50": "its rolling 20-quarter median", "T_roll_p75": "its rolling 20-quarter 75th percentile",
})
SIDE = {"countercyclical": "at or below", "procyclical": "at or above"}
LEAN = {"countercyclical": "countercyclical, the credit-crunch prior (hold equities when bank tightening is low or "
                           "falling)",
        "procyclical": "procyclical, against the credit-crunch prior (hold equities when bank tightening is high or "
                       "rising)"}


def _rule(prefix: str = "") -> str:
    """Plain-English rule of a track's winner, from its structured fields (P1 long/cash only on this pair)."""
    g = lambda n: W.text(prefix + n)  # noqa: E731
    return (f"hold SPY when the {SIGNAL_TEXT.get(W.value(prefix + 'signal_code'), g('signal_code'))} from "
            f"{g('lead_word')} quarters earlier is {SIDE.get(W.value(prefix + 'direction'), g('direction'))} "
            f"{THRESHOLD_TEXT.get(W.value(prefix + 'threshold_code'), g('threshold_code'))}; otherwise hold cash")


def _rid(prefix: str = "") -> str:
    g = lambda n: W.text(prefix + n)  # noqa: E731
    return " / ".join([g("signal_code"), g("threshold_code"), g("strategy_family"), f"L{g('lead')}"])


def _r71_caveat() -> str:
    """R7.1 failures flagged in the caveats from the null diagnosis flags; the numbers (pass or fail) are stated on
    the chance-check panel by components.two_track.r71_note."""
    out = []
    for lbl, key in (("as known at the time", "main"), ("as revised today", "comparison")):
        n = (_WS["tracks"].get(key) or {}).get("null_tournament") or {}
        if n.get("r71_pass") is not False:
            continue
        d = n.get("r71_diagnosis") or {}
        sign = "negative" if str(n.get("timing_sharpe_mean")).startswith("-") else "positive"
        where = ("only in the scrambled contests' selected winners on the real return path, not in unselected "
                 "candidates or with the returns permuted" if d.get("bias_only_in_selected_winners_on_real_returns")
                 else "also without selection or without the real return path")
        out.append(f"on data {lbl} they do not meet it: the average timing Sharpe is {sign}, and the bias appears "
                   f"{where}; its cause is not established (diagnosis in winner_summary.json). Read that track's "
                   "chance-check percentile with this in mind")
    if not out:
        return ""
    return ("6. **Chance-check calibration.** The scrambled contests should show no timing skill on average (the R7.1 "
            "check); " + "; ".join(out) + ".\n")


_RULE = _rule()
_RULE_REVISED = _rule("comparison_")
_RID = _rid()
_RID_REVISED = _rid("comparison_")
_DIR = W.value("direction")
_SIG = SIGNAL_TEXT.get(W.value("signal_code"), W.signal_code)
_THR = THRESHOLD_TEXT.get(W.value("threshold_code"), W.threshold_code)
_SAME_RULE = _RID == _RID_REVISED
_R71 = _r71_caveat()
_CHANCE_TEXT = (f"the real winner's stable-range score is above the winners of all {W.null_draws} scrambled contests"
                if W.value("null_percentile") == 1 else
                f"the real winner's stable-range score ranks at the {W.null_percentile} point of the scrambled scores")
_IS_BELOW_BH = W.value("is_sharpe") < W.value("bh_is_sharpe")
_LOG_OOS_TXT = (f"the trade log has the same {_EV['n_trade_log_rows_test_period']} rows dated in the test period"
                if _EV["n_trade_log_rows_test_period"] == W.value("oos_n_trades") else
                f"the trade log has {_EV['n_trade_log_rows_test_period']} rows dated in the test period, because it "
                "also records the switch into the first test-period quarter")


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Bank Lending Standards as a Credit-Cycle Overlay"
    PAGE_SUBTITLE = (
        "Fed Senior Loan Officer Survey (SLOOS): net share of banks tightening standards for commercial and "
        "industrial loans to large and middle-market firms (FRED DRTSCILM) x S&P 500 (SPY). QUARTERLY: all leads and "
        "windows are in quarters."
    )

    HEADLINE_H2 = (
        f"## Test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, on survey data as known at "
        f"the time (archive from {_VIN0})"
    )

    PLAIN_ENGLISH = (
        "Every quarter the Federal Reserve asks senior loan officers whether their bank has tightened or eased "
        "its standards for business loans. The measure used here is the share of banks that tightened minus the "
        "share that eased, for loans to large and middle-market firms. The economic prior is countercyclical: when "
        "banks tighten, credit becomes scarce, investment slows, and equities have historically struggled. The "
        "headline result uses the survey figures as they were published at each date. Those published figures are "
        f"archived only from {_VIN0}, so the training period for the headline result is short."
    )

    WHERE_THIS_FITS = (
        "This is a credit-cycle overlay for broad U.S. equities. The pair id says small firms, but the series tested "
        "is the large and middle-market one (DRTSCILM); the small-firm series (DRTSCIS) is published in the same "
        "survey and has not been tested here."
    )

    ONE_SENTENCE_THESIS = (
        f"On data as known at the time, the rule selected on the training period is to {_RULE}; it is "
        f"{LEAN.get(_DIR, _DIR)}, and in the test period it scored Sharpe {W.oos_sharpe} against "
        f"{W.bh_oos_sharpe} for buy-and-hold."
    )

    KPI_CAPTION = (
        f"Winner selected on training data ({W.is_start} to {W.is_end}, {W.is_n} quarters as known at the time) by "
        f"{W.selection_objective}. Test period {W.oos_start} to {W.oos_end} ({W.oos_n} quarters). Sharpe ratios use "
        "quarterly annualization."
    )

    HERO_TITLE = "Bank C&I Lending Standards vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the net share of banks tightening (left axis; above zero = more banks tightening than "
        "easing) is shown with SPY (right axis) on the same time axis. Gray bands are NBER recessions; pink bands "
        "mark quarters with net tightening above zero."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Lending-Standards Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: quarters sorted by the 4-quarter change in net tightening, from fastest easing (Q1) to "
        f"fastest tightening (Q4). Same-quarter SPY Sharpe is {_Q['Q1']:.2f} in Q1, {_Q['Q2']:.2f} in Q2, "
        f"{_Q['Q3']:.2f} in Q3 and {_Q['Q4']:.2f} in Q4. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = f"""
### Bank lending standards: the credit channel

This result uses data as known at the time, covering {W.is_start} to {W.oos_end}: each quarter the rule reads the survey as it was published then. That archive starts in {_VIN0}, so the training period is only {W.is_n} quarters and contains no recession.

The Senior Loan Officer Opinion Survey asks banks whether their standards for commercial and industrial (C&I) loans have tightened or eased since the previous survey. The net share tightening (FRED series `DRTSCILM`) rose sharply before and during the 2001 and 2008 recessions and again in 2020 and 2022-23. The economic prior is **countercyclical**: when more banks tighten, firms lose access to credit, and equity exposure should be reduced.

**What the search selected.** The rule chosen on the training period is to {_RULE}. Its orientation is {LEAN.get(_DIR, _DIR)}. It was selected by {W.selection_objective} (stable lead range {W.plateau_range}) out of {W.n_valid} valid combinations. In the test period ({W.oos_start} to {W.oos_end}, {W.oos_n} quarters) it records Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}).

**On today's revised data (hindsight, for comparison only)** the rule selected over the longer revised history is to {_RULE_REVISED}; its test-period Sharpe is {W.comparison_oos_sharpe}.

<!-- expander: What exactly is the SLOOS tightening series? -->
`DRTSCILM` is the net percentage of domestic banks reporting tighter standards for C&I loans to large and middle-market firms (the survey's larger-firm size class): the share reporting tighter standards minus the share reporting easier standards. It is a quarterly diffusion measure, bounded because it is a difference of shares, published in the Fed's survey release in early February, May, August and November, inside the quarter it describes. The archive of published figures (ALFRED) starts in {_VIN0}; a later vintage revised the history. The small-firm series `DRTSCIS` comes from the same survey.
<!-- /expander -->

### A quarterly credit pair: small samples, few cycles, explicit units

Leads are in QUARTERS; Sharpe ratios are annualized by the square root of 4. Credit cycles are few, and the as-known-at-the-time training period covers none of the past recessions, so any lead estimate rests on a small number of episodes.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust (2000-2002)",
            "narrative": (
                "Banks tightened C&I standards through 2000 and 2001 as corporate credit quality deteriorated, "
                "while the equity bear market ran from 2000 to 2002. The real-time survey archive does not reach "
                "back this far."
            ),
            "caption": "Dot-Com: banks tightened through the downturn.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007-2009)",
            "narrative": (
                "Net tightening rose from near zero in mid-2007 to its survey highs in late 2008, alongside the "
                "deepest equity drawdown in the sample, and fell back as equities recovered in 2009."
            ),
            "caption": "GFC: net tightening reached its survey highs.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "Tightening jumped in the second and third quarters of 2020, after the equity crash had already "
                "happened and while equities were recovering. A quarterly survey cannot time a shock that plays out "
                "within weeks."
            ),
            "caption": "COVID: a sharp, brief tightening after the crash.",
        },
        {
            "slug": "rate_hike_2022",
            "title": "2022-2024 Rate Hikes",
            "narrative": (
                "Banks tightened again from late 2022 into 2023 as policy rates rose and regional banks came under "
                "stress, while equities fell in 2022 and recovered through 2023-24. This episode lies inside the "
                "test period."
            ),
            "caption": "2022-2024: tightening rose again as rates climbed.",
        },
    ]

    NARRATIVE_SECTION_2 = f"""
### What the evidence and the search say together

The Evidence page reports the formal lead-lag tests (smallest Granger p-value across the {P.length(_G)} lags {_G_MIN:.2f}, Holm-adjusted {_G_MIN_HOLM:.2f}). The rule on the Strategy page is a state description chosen on a short training window. Because that window covers no recession, the result is a candidate pattern awaiting a frozen-rule hold-out exam.

### What this means for investors

- **Read bank lending standards as credit-cycle context.** Tightening has accompanied every recession in the sample.
- **Compare the two data views.** The rule selected on revised data {'is the same' if _SAME_RULE else 'differs from the rule selected on data as known at the time'}; the as-revised-today result is hindsight.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this credit-cycle story survives correlation, Granger, regime-quartile, "
        "cross-correlation, local-projection and quantile checks."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Battery",
    method_theory=(
        "Pearson correlations between every tightening transform (level, quarterly change, 4-quarter change, "
        f"20-quarter z-score) and forward SPY returns at horizons of {_HZ_TXT} quarters. p-values use HAC "
        "(Newey-West) errors because multi-quarter forward returns overlap."
    ),
    question="Is there any raw association between bank tightening today and stock returns over the coming quarters?",
    how_to_read=(
        "Rows are tightening transforms, columns are forward-return horizons in QUARTERS; each cell shows the "
        "correlation and its p-value. Pale cells mean little association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        f"What this shows: the largest absolute correlation in the grid is {_C_MAX:.2f}; the smallest HAC p-value is "
        f"{_C_MINP:.2f}."
    ),
    observation=(
        f"The largest |r| is {_C_MAX:.2f} and the smallest p-value {_C_MINP:.2f}"
        + ("; no cell is statistically significant at conventional levels." if _C_MINP >= 0.05 else ".")
    ),
    interpretation=(
        "Correlations this small do not support a linear trading rule on their own; the tournament asks whether a "
        "lagged threshold rule changes portfolio behavior."
    ),
    key_message=f"Raw association: largest |r| {_C_MAX:.2f}, smallest p {_C_MINP:.2f}.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of the 4-quarter change in net tightening improve forecasts of "
        "SPY returns after accounting for SPY's own history, at each quarterly lag up to "
        f"{P.length(_G)}. Because the smallest of these p-values is the one quoted, it is Holm-adjusted."
    ),
    question="Does bank tightening lead SPY returns in a formal lag test?",
    how_to_read="Bars show the p-value at each quarterly lag; diamonds the Holm-adjusted p-values across all lags.",
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"What this shows: the smallest p-value across lags is {_G_MIN:.2f} (Holm-adjusted {_G_MIN_HOLM:.2f})."
    ),
    observation=(
        f"The smallest p-value across the {P.length(_G)} lags is {_G_MIN:.2f}; adjusted for testing all of them it "
        f"is {_G_MIN_HOLM:.2f}" + ("; no lag is significant at conventional levels." if _G_MIN_HOLM >= 0.05 else ".")
    ),
    interpretation=(
        "A Granger result is a statement about linear forecasting on revised data, not proof that lending standards "
        "cause SPY returns."
    ),
    key_message=f"Formal lead-lag test: Holm-adjusted smallest p {_G_MIN_HOLM:.2f}.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory="Quartile analysis sorts quarters by the 4-quarter change in net tightening and compares same-quarter SPY returns.",
    question="Do quarters of easing and tightening produce different SPY outcomes?",
    how_to_read="Q1 is the fastest easing; Q4 the fastest tightening. Compare Sharpe, average return and sample size.",
    chart_name="regime_stats",
    chart_caption=(
        f"What this shows: same-quarter SPY Sharpe is {_Q['Q1']:.2f} / {_Q['Q2']:.2f} / {_Q['Q3']:.2f} / "
        f"{_Q['Q4']:.2f} from Q1 to Q4."
    ),
    observation=(
        f"Same-quarter SPY Sharpe is {_Q['Q1']:.2f} (Q1), {_Q['Q2']:.2f} (Q2), {_Q['Q3']:.2f} (Q3) and "
        f"{_Q['Q4']:.2f} (Q4)."
    ),
    interpretation=(
        "Quartiles are concurrent, not predictive: they describe the equity backdrop in each credit regime, while the "
        "tournament tests lagged rules."
    ),
    key_message="Lending-standards regimes describe the equity backdrop; they are not a forecast.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Both series are filtered with the same autoregressive model fitted to the 4-quarter change in net "
        "tightening (Box-Jenkins pre-whitening) before testing whether one tends to move before the other."
    ),
    question="At which quarterly offsets does the change in tightening line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed 95% band mark unusual correlation after filtering persistence. Positive offsets "
        "mean the tightening change comes first; negative offsets mean the SPY return comes first."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=f"What this shows: offsets outside the band: {_CCF_TXT}.",
    observation=(
        f"After pre-whitening, the offsets outside the 95% band are: {_CCF_TXT}"
        + (" (none with the tightening change first)." if not _CCF_POS else ".")
    ),
    interpretation=(f"With {P.length(_CCF)} offsets tested, an isolated bar outside a 95% band is about what chance "
                    "alone produces."),
    key_message="No clean lead from tightening to SPY returns." if not _CCF_POS else "Read isolated bars with care.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        f"Local projections regress the forward SPY return at horizons of {_HZ_TXT} quarters on the 4-quarter "
        "change in net tightening, with HAC errors (lags at least h-1)."
    ),
    question="How do forward SPY returns relate to the change in tightening at different horizons?",
    how_to_read=("Each bar is the forward SPY return for a rise in the 4-quarter change (the axis states the scale); "
                 "whiskers are 95% intervals."),
    chart_name="local_projections",
    chart_caption=(
        f"What this shows: HAC p-values {', '.join(f'{p:.2f}' for p in _LP['p_value'])} at horizons of {_HZ_TXT} "
        "quarters."
    ),
    observation=f"The largest R-squared across horizons is {P.colmax(_LP, 'r_squared'):.3f}; the smallest p-value {_LP_MINP:.2f}.",
    interpretation="Overlapping horizons share observations, so the longer-horizon estimates are less independent than they look.",
    key_message=f"Forward response: smallest HAC p {_LP_MINP:.2f}.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression (statsmodels QuantReg per quantile) of the next quarter's SPY return on the 4-quarter "
        "change in net tightening; next-quarter returns do not overlap. A bootstrap Wald test checks equality of the "
        "slopes across quantiles."
    ),
    question="Does bank tightening matter differently in weak and strong market quarters?",
    how_to_read="Compare the coefficient across return quantiles; whiskers are 95% intervals.",
    chart_name="quantile_coef",
    chart_caption=(
        f"What this shows: the cross-quantile equality test {'rejects' if _QT['reject_equality'] else 'does not reject'} "
        f"a uniform slope (Wald p={_QT['p_value']:.2f})."
    ),
    observation=(
        f"The bootstrap Wald test {'rejects' if _QT['reject_equality'] else 'does not reject'} slope equality across "
        f"quantiles (p={_QT['p_value']:.2f})."
    ),
    interpretation="Tail asymmetry is only established if the equality test rejects; otherwise read the slopes as imprecise.",
    key_message=f"Cross-quantile equality Wald p={_QT['p_value']:.2f}.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Bank Lending Standards and SPY",
    "overview": (
        "*One question, asked several ways: does the net share of banks tightening carry information about FUTURE "
        f"S&P 500 (SPY) returns? Smallest Holm-adjusted Granger p {_G_MIN_HOLM:.2f}; smallest correlation p "
        f"{_C_MINP:.2f}.*\n\n"
        f"All statistics on this page are computed on QUARTERLY revised data (`results/{PAIR}/core_models_{_TAG}/`)."
    ),
    "plain_english": (
        "This page asks whether bank lending standards help forecast the stock market, first with descriptive tests "
        "on today's revised data, then with the tournament on data as known at the time."
    ),
    "downloads": [
        {"label": "Granger by lag, tightening to SPY", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Correlation battery", "path": f"results/{PAIR}/core_models_{_TAG}/correlations.csv"},
        {"label": "Pre-whitened CCF", "path": f"results/{PAIR}/core_models_{_TAG}/ccf_prewhitened.csv"},
        {"label": "Local projections", "path": f"results/{PAIR}/core_models_{_TAG}/local_projections.csv"},
        {"label": "Quantile regression", "path": f"results/{PAIR}/core_models_{_TAG}/quantile_regression.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Stress-episode returns", "path": f"results/{PAIR}/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": f"results/{PAIR}/rolling_correlation_{PAIR}.csv"},
        {"label": "Structural break test", "path": f"results/{PAIR}/structural_break_{PAIR}.json"},
        {"label": "Stationarity tests (ADF/KPSS)", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "level2_summary": {
        "title": "What the evidence adds up to",
        "body": (
            f"Correlations: largest |r| {_C_MAX:.2f}, smallest HAC p {_C_MINP:.2f}. Granger: smallest p {_G_MIN:.2f}, "
            f"Holm-adjusted {_G_MIN_HOLM:.2f}. Pre-whitened CCF offsets outside the band: {_CCF_TXT}. Local "
            f"projections: smallest HAC p {_LP_MINP:.2f}. Quantile slopes: equality Wald p {_QT['p_value']:.2f}. "
            + ("**Bottom line:** none of the formal tests finds a statistically significant forecasting lead from "
               "bank tightening to SPY; the quartile sort is descriptive and concurrent."
               if not _ANY_SIG else
               "**Bottom line:** at least one formal test is statistically significant; read it with the number of "
               "tests in mind.")
        ),
        "key_message": f"Smallest Holm-adjusted Granger p {_G_MIN_HOLM:.2f}.",
    },
    "tournament_intro": (
        "The statistical tests above ask whether the indicator forecasts. The tournament asks a pragmatic question: "
        "across the declared QUARTERLY trading rules built from this series, which one did best on the training "
        f"period? We tested {W.n_candidates} combinations ({W.n_valid} valid as known at the time; {W.n_distinct} "
        f"distinct position series): {P.length(_MAN['signals'])} signal transforms x threshold schemes x long/cash x "
        f"both orientations x quarterly leads {_GRID_RANGE}. The winner is `{_RID}`, chosen on the training period by "
        f"{W.selection_objective}."
    ),
    "transition": (
        "**Transition:** the next page shows the single rule the search selected on each data track, with its "
        "caveats."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Quarterly Long/Cash Lending-Standards Overlay"
    PAGE_SUBTITLE = (
        f"The rule selected on the training period from survey data as known at the time ({W.is_n} quarters from "
        f"{_VIN0}); no frozen-rule hold-out test has been run yet."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-18). This page previously reported the rule {W.previous_rule} (training Sharpe "
        f"{W.previous_is_sharpe}, test-period Sharpe {W.previous_oos_sharpe}, published {W.previous_tag}), which "
        "was the single highest training Sharpe on revised data with fixed lags, using the survey figures as "
        "downloaded for that run. It now reports the rule selected on data as known at the time, with point-in-time "
        "release dates and the stable-lead-range rule; today's revised data are shown for comparison only."
    )

    PLAIN_ENGLISH = (
        f"The rule is to {_RULE}. In the test period ({W.oos_start} to {W.oos_end}) it scored Sharpe "
        f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold, with maximum drawdown {W.oos_max_drawdown} "
        f"versus {W.bh_oos_max_drawdown}. The test-period Sharpe difference is {W.sharpe_gap} (95% interval "
        f"{W.ci_low} to {W.ci_high}). It is a candidate overlay found by search; its final exam on untouched data has "
        "not been run."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); facts only here.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Found in search: selected on a short as-known-at-the-time training period; it has not faced a "
            "frozen-rule hold-out final exam."
        ),
        strengths=[
            "Bank lending standards are a direct read on credit supply, and net tightening rose around every "
            "recession in the sample.",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}) rather than an isolated peak.",
        ],
        risks=[
            f"Short training period as known at the time: {W.is_n} quarters ({W.is_start} to {W.is_end}), with no "
            "recession in it.",
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to {W.ci_high}.",
            f"The orientation is {LEAN.get(_DIR, _DIR)}.",
            f"The rule selected on revised data {'is the same' if _SAME_RULE else 'differs'} (hindsight test-period "
            f"Sharpe {W.comparison_oos_sharpe}, 95% interval {W.comparison_ci_low} to {W.comparison_ci_high}).",
        ] + ([f"The winner's training Sharpe ({W.is_sharpe}) is below buy-and-hold's over the same training quarters "
              f"({W.bh_is_sharpe})."] if _IS_BELOW_BH else [])
          + ([f"The stable lead range {W.plateau_range} sits at the edge of the declared lead grid ({_GRID_RANGE} "
              "quarters); leads beyond the grid were not tested."] if _EDGE else []),
        conclusion=(
            f"Rule {_RID}: test-period Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold "
            f"({W.oos_start} to {W.oos_end}), maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}, "
            "on survey data as known at the time."
        ),
    )

    DOWNLOADS = [
        {"label": "Winner summary", "path": f"results/{PAIR}/winner_summary.json"},
        {"label": "Granger causality by lag", "path": f"results/{PAIR}/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": f"results/{PAIR}/regime_quartile_returns.csv"},
        {"label": "Tournament results (as known at the time)", "path": f"results/{PAIR}/tournament_results_{_TAG}.csv"},
        {"label": "Tournament results (as revised today, hindsight)",
         "path": f"results/{PAIR}/hindsight_tournament_results_{_TAG}.csv"},
        {"label": "Previously published tournament", "path": f"results/{PAIR}/tournament_results_20261015.csv"},
        {"label": "Bootstrap validation", "path": f"results/{PAIR}/tournament_validation_{_TAG}/bootstrap.csv"},
        {"label": "Stationarity tests", "path": f"results/{PAIR}/stationarity_tests_{_TAG}.csv"},
        {"label": "Winner trade log (broker style)", "path": f"results/{PAIR}/winner_trades_broker_style.csv"},
    ]

    SIGNAL_RULE_MD = f"""
**Rule:** {_RULE}. Orientation: {LEAN.get(_DIR, _DIR)}. (Family: {W.strategy_family}; signal `{W.signal_code}`, threshold `{W.threshold_code}`, lead L{W.lead} quarters, per `winner_summary.json`.)

If-then form (evaluated once per quarter):
- **IF** the {_SIG} from {W.lead_word} quarters earlier is {SIDE.get(_DIR, _DIR)} {_THR} -> **HOLD SPY (100% invested)**.
- **ELSE** -> **HOLD CASH**.

Test-period results on data as known at the time ({W.oos_start} to {W.oos_end}, {W.oos_n} quarters; Sharpe annualized by the square root of 4): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} position changes between consecutive test-period quarters, each a full switch between SPY and cash ({_LOG_OOS_TXT}); annual turnover {W.annual_turnover}; in SPY {W.oos_exposure} of the test-period quarters.
"""

    HOW_SIGNAL_IS_GENERATED_MD = f"""
No formulas, three steps:

**What changes in the world:** banks tighten or ease the terms on which they lend to businesses. The Federal Reserve surveys senior loan officers every quarter and publishes the net share tightening (series `DRTSCILM`) inside the same quarter.

**What the signal measures:** each quarter, the rule takes the survey series as it was published at that date, computes the {_SIG} inside that published series, and reads its value from {W.lead_word} quarters earlier against {_THR} (also computed inside that published series).

**What decision it drives:** {SIDE.get(_DIR, _DIR)} the threshold -> HOLD SPY for the next quarter; otherwise -> HOLD cash.

OOS Sharpe means test-period (out-of-sample) risk-adjusted return. OOS Return is the annualized test-period return. Maximum Drawdown is the largest peak-to-trough loss at quarter ends. Turnover is the sum of position changes per year. Win Rate is the share of test-period quarters with positive strategy return.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule works so you can replicate and audit "
        "it; it is **not** a recommendation to trade it. The quarterly routine is:\n\n"
        "1. **Pull the survey series** as currently published: FRED series `DRTSCILM`.\n"
        f"2. **Compute the signal**: the {_SIG}.\n"
        f"3. **Apply the delay**: use the value from {W.lead_word} quarters earlier.\n"
        f"4. **Check the threshold**: is it {SIDE.get(_DIR, _DIR)} {_THR}? See `winner_trade_log.csv` for the full "
        "signal and threshold path.\n"
        "5. **Take the position** at the quarter end: yes -> HOLD SPY (100%); otherwise -> HOLD cash. Re-evaluate "
        "once a QUARTER."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_TITLE = "Stress Episodes"
    WALK_FORWARD_CAPTION = (
        "What this shows: cumulative return of the as-known-at-the-time winner, the hindsight winner and buy-and-hold "
        f"SPY in {P.length(_SP)} stress episodes. Episodes before {_VIN0} precede the as-known-at-the-time archive, so the "
        "headline rule has no position there."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 4-quarter change in net tightening; the target is SPY returns in "
            "the same quarter. The 20-quarter rolling correlation shows whether their linear relationship is stable "
            "through time."
        ),
        "structural_break": (
            f"How to read it: a Quandt-Andrews test for one break in the regression of SPY returns on the lagged "
            f"tightening change; the largest F is {_SB['statistic']:.2f} at {_SB['breakpoint_date']} with "
            f"bootstrap p {_SB['p_value']:.2f}."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: test-period Sharpe of every valid searched combination by lead (data as known at the "
        "time). The winner is chosen on the training period, not on this test-period score."
    )

    CAVEATS_MD = f"""
**Main caveats:**

1. **Short history as known at the time.** Published (real-time) survey figures are archived from {_VIN0}, so the training period is {W.is_n} quarters ({W.is_start} to {W.is_end}) and the test period {W.oos_n} quarters; the training period contains no recession.
2. **Search selection.** The winner is one of {W.n_valid} valid combinations; across {W.null_draws} contests run on data shifted against the returns by a fixed number of quarters (wrapping around once), {_CHANCE_TEXT}.
3. **Two data views.** On today's revised data the selected rule is to {_RULE_REVISED} (hindsight; test-period Sharpe {W.comparison_oos_sharpe}).
4. **The series is the large and middle-market one.** The pair id names small firms; the small-firm series (DRTSCIS) has not been tested.
5. **Data character.** QUARTERLY, bounded diffusion measure; a later vintage revised part of the early history. The level's ADF p-value is {_ST[('sloos_level', 'ADF')]:.2f}; the 4-quarter change's is {_ST[('sloos_chg_4q', 'ADF')]:.2f}.
{_R71}
**What this means:** the result was found in search and has not been tested on untouched data. The prescribed next step is a final exam: freeze this rule and test it once on an untouched window.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a BUY when the lagged "
        f"{_SIG} moves {SIDE.get(_DIR, _DIR)} {_THR}, taking exposure from 0% to 100% SPY. A SELL moves back to "
        f"cash when the condition no longer holds. The log has {_EV['n_trade_log_rows']} rows over the full history; "
        f"every row is in `winner_trades_broker_style.csv`."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "quarter end",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": f"{W.signal_code} {_DIR} rule crossed {W.threshold_code}",
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator (as known at the time) | ALFRED (Fed SLOOS vintages, pinned: data/release_calendar/vintages/DRTSCILM.csv.gz) | `DRTSCILM`, net % of banks tightening C&I standards, large and middle-market firms, every published vintage | Quarterly |
| Indicator (as revised today) | Latest vintage of the same file | `DRTSCILM` | Quarterly |
| Release dates | data/release_calendar/release_calendar.csv | first publication date per quarter | Quarterly |
| Target | Yahoo Finance (pinned: data/phaseB_inputs/spy_month_end_20261017.csv) | SPY adjusted quarter-end close | Quarterly |

QUARTERLY credit-survey pair. The survey is published inside the quarter it describes, so even the shortest lead in the grid uses only published data.
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the net percentage of banks tightening C&I standards for large and middle-market firms. "
    "The pipeline builds the level, the quarterly change, the 4-quarter change and a 20-quarter rolling z-score; "
    "rolling thresholds use 20-quarter windows. On the as-known-at-the-time track every signal and threshold is "
    "recomputed inside the vintage published when each quarter's return window opens. The tradeable lead grid runs "
    f"{_GRID_RANGE} QUARTERS (strict publication floor); the winner uses `{W.signal_code}` ({_SIG}) at L{W.lead}."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson, HAC p-values) | Any raw association at any quarterly horizon? | Cheap triage before formal tests |
| Granger causality (lags 1-4q, Holm-adjusted minimum) | Does past tightening forecast SPY? | Formal lead-lag check |
| Regime quartiles | Do easing and tightening quarters behave differently? | Makes the credit story interpretable |
| Pre-whitened CCF (offsets -4..+4q) | At which quarterly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections (HAC) | Where is SPY h quarters after a tightening move? | Horizon-by-horizon view |
| Quantile regression (QuantReg + equality Wald test) | Does the signal matter more in market tails? | Credit signals sometimes work in the left tail only |
| Structural break (Quandt-Andrews) / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
| Lead-plateau selection (D9) | Is the chosen lead part of a stable range? | Guards against a lucky single lead |
| Chance check (null tournament) | How does the winner compare with contests on scrambled signals? | Measures what selection alone can produce |
| Paired block bootstrap | How uncertain is the Sharpe difference versus buy-and-hold? | Interval for the headline comparison |
""")

_TOURNAMENT_DESIGN_MD = f"""
Grid: {P.length(_MAN['signals'])} signal transforms x threshold schemes x long/cash x both orientations x QUARTERLY leads {_GRID_RANGE} ({W.n_candidates} combinations; {W.n_distinct} distinct position series). Each position is held for the quarter after it is set. Each data track selects its own winner on its training period: every window of three neighbouring leads is scored by its lowest training Sharpe, the best window is the stable lead range, and the winner is the highest training Sharpe inside it.

- As known at the time (headline): `{_RID}`, stable lead range {W.plateau_range}, training Sharpe {W.is_sharpe} ({W.is_start} to {W.is_end}), test-period Sharpe {W.oos_sharpe}. The single highest training Sharpe on this track ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, Sharpe {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, {W.raw_argmax_position}, shown for reference and not the selection rule.
- As revised today (hindsight): `{_RID_REVISED}`, training Sharpe {W.comparison_is_sharpe} ({W.comparison_is_start} to {W.comparison_is_end}), test-period Sharpe {W.comparison_oos_sharpe}.
- Cross-evaluation: the headline rule scored on revised data has test-period Sharpe {W.ce_main_on_revised_oos_sharpe}; the hindsight rule scored on data as known at the time has {W.ce_revised_on_main_oos_sharpe}.
- Chance check: across {W.null_draws} contests run on circularly shifted survey data, {_CHANCE_TEXT}.
- Previously published rule: `{W.previous_rule}` ({W.previous_selection}), training Sharpe {W.previous_is_sharpe}, test-period Sharpe {W.previous_oos_sharpe}; the harness replays it exactly from the published panel.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_{PAIR}.py` (harness spec `scripts/pair_spec_{PAIR}.py`), deterministic with fixed seeds. Charts: `scripts/generate_charts_{PAIR}.py`.
"""

_REFERENCES_MD = """
1. Board of Governors of the Federal Reserve System, *Senior Loan Officer Opinion Survey on Bank Lending Practices*.
2. Federal Reserve Bank of St. Louis, ALFRED / FRED series `DRTSCILM` (all vintages).
3. Yahoo Finance, SPY adjusted price history.
4. Lown, C., and Morgan, D. P. (2006). "The Credit Cycle and the Business Cycle: New Findings Using the Loan Officer Opinion Survey." *Journal of Money, Credit and Banking*, 38(6), 1575-1597.
5. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods." *Econometrica*, 37(3), 424-438.
6. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections." *American Economic Review*, 95(1), 161-182.
7. Andrews, D. W. K. (1993). "Tests for Parameter Instability and Structural Change with Unknown Change Point." *Econometrica*, 61(4), 821-856.
8. Politis, D. N., and Romano, J. P. (1992). "A Circular Block-Resampling Procedure for Stationary Data." In *Exploring the Limits of Bootstrap*, Wiley, 263-270.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        f"QUARTERLY credit-survey pair. As known at the time: training {W.is_start} to {W.is_end} ({W.is_n} "
        f"quarters), test {W.oos_start} to {W.oos_end} ({W.oos_n} quarters). As revised today: training "
        f"{W.comparison_is_start} to {W.comparison_is_end}. Sharpe ratios use quarterly annualization; leads are in "
        "quarters."
    ),
    plain_english=(
        "One QUARTERLY bank-credit survey series (net share of banks tightening C&I standards, large and "
        "middle-market firms) and the S&P 500 ETF (SPY). The headline uses the survey figures as they were "
        f"published at each date, archived from {_VIN0}; the as-revised-today view uses today's figures over the "
        "longer history and is shown for comparison only. Every number on these pages is reproduced by one "
        "deterministic script."
    ),
)
