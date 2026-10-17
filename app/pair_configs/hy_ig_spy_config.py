"""HY-IG x SPY pair configuration (Rule APP-PT1).

Pair-specific narrative content for the Story / Evidence / Strategy / Methodology templates.
Phase B: every result number about the winner is rendered from the structured winner fields
(results/hy_ig_spy/winner_summary.json `winner_fields`, via components.winner_fields) or read from the
pipeline's CSV / JSON artifacts at import; none is typed here (scripts/gate_structured_prose.py).
Single track: ICE BofA OAS is market data and is not revised.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from components import provenance as P
from components.page_templates import MethodologyConfig
from components.winner_fields import load

W = load("hy_ig_spy")
_RES = Path(__file__).resolve().parents[2] / "results" / "hy_ig_spy"
_WS = P.json_file(_RES / "winner_summary.json")
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_AUD = {(r["probabilities"], r["lead_days"]): r for r in P.json_file(_RES / f"hmm_lookahead_audit_{_TAG}.json")["rows"]}
_LC = P.csv_file(_RES / f"lead_correlation_{_TAG}.csv").set_index("transform")
_WC = P.csv_file(_RES / f"lead_winner_curve_{_TAG}.csv")
_SUB = P.csv_file(_RES / "subperiod_sharpe.csv").set_index("period_name")
_COST = P.csv_file(_RES / f"tournament_validation_{_TAG}" / "transaction_costs.csv")
_COST = _COST[_COST["rank"] == 1].set_index("tx_cost_bps")["net_sharpe_approx"]
_WF = P.csv_file(_RES / f"tournament_validation_{_TAG}" / "walk_forward.csv")
_WF = _WF[_WF["rank"] == 1]
_SB = P.json_file(_RES / "structural_break_hy_ig_spy.json")
_SIGCOL = _WS["signal_column"]
_EF = P.json_file(_RES / f"evidence_facts_{_TAG}.json")
_H = _EF["history"]
_PREV_HMM = next((p for p in _WS["selection"].get("previously_published", []) if "combo" in p), {})
_GRID = P.lead_grid("hy_ig_spy")
_MAN = P.json_file(_RES / f"candidates_manifest_{_TAG}.json")
_PPY = _MAN["ppy"]
_GRID_SET = "{" + ", ".join(str(x) for x in _GRID) + "}"
_N_STRAT = P.length(_MAN["strategies"])
_QR_H = _EF["quantile_horizon_days"]


def _pct(v, nd=1):
    return f"{abs(v):.{nd}%}"


_D = _EF["derived"]                      # facts from large files, computed by the pipeline
_N_THR = _D["n_threshold_labels"]
_OOS_MONTHS = _D["oos_months"]
_QT_TAILS, _WF1 = _D["quantile_tails"], _D["walk_forward_rank1"]
_HB = _D["best_hmm_rule"]


def _yrs():
    return f"{_D['history_years']}"


_CALM = (_D["hmm_regime_calm"]["sharpe"], _D["hmm_regime_calm"]["ann_return"])
_STRESS = (_D["hmm_regime_stress"]["sharpe"], _D["hmm_regime_stress"]["ann_return"])
_RSH, _RCO, _RGR = _D["rolling_sharpe"], _D["rolling_correlation"], _D["rolling_granger"]
_LCW = _LC.loc[_SIGCOL] if _SIGCOL in _LC.index else None
_LEADS = _GRID


def _f(v, nd=2):
    return "n/a" if v is None or pd.isna(v) else f"{v:.{nd}f}"


THRESHOLD_TEXT = P.definitions({
    "T2_rp75": "the 75th percentile of its own trailing 504 trading days", "T2_rp85": "the 85th percentile of its own trailing 504 trading days",
    "T2_rp95": "the 95th percentile of its own trailing 504 trading days", "T1_p75": "its 75th percentile over the in-sample readings before each day (frozen at the in-sample end)",
    "T1_p85": "its 85th percentile over the in-sample readings before each day (frozen at the in-sample end)", "T1_p95": "its 95th percentile over the in-sample readings before each day (frozen at the in-sample end)",
    "T3_z1.5": "a trailing 504-day z-score of 1.5", "T3_z2.0": "a trailing 504-day z-score of 2.0",
    "T3_z2.5": "a trailing 504-day z-score of 2.5", "T4_hmm_0.5": "0.5", "T4_hmm_0.7": "0.7", "T5_ms_0.5": "0.5",
    "T5_ms_0.7": "0.7", "-": "its trailing 504-day range (sizing; no threshold)",
})
_THR = THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)
SIGNAL_TEXT = P.definitions({
    "S1_spread_level": "HY-IG spread level", "S2a_zscore_252d": "HY-IG spread's 252-day z-score",
    "S2b_zscore_504d": "HY-IG spread's 504-day z-score", "S3a_pctrank_504d": "HY-IG spread's 504-day percentile rank",
    "S3b_pctrank_1260d": "HY-IG spread's 1260-day percentile rank", "S4a_roc_21d": "HY-IG spread's 21-day % change",
    "S4b_roc_63d": "HY-IG spread's 63-day % change", "S4c_roc_126d": "HY-IG spread's 126-day % change",
    "S5_ccc_bb_spread": "CCC-BB quality spread", "S6_hmm_stress": "causal HMM stress probability",
    "S7_ms_stress": "causal Markov-switching stress probability", "S10_mom_21d": "HY-IG spread's 21-day change",
    "S11_mom_63d": "HY-IG spread's 63-day change", "S12_mom_252d": "HY-IG spread's 252-day change",
    "S13_acceleration": "HY-IG spread acceleration",
})
_SIG = SIGNAL_TEXT.get(W.signal_code, W.signal_display)
_RULE = (f"each day, take the {_SIG} as it stood {W.lead_text} earlier and compare it with {_THR}; hold 100% SPY "
         "when it is below, otherwise hold cash")


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    """Story-page content object (passed to `render_story_page`)."""

    PAGE_TITLE = "The Story: HY-IG Credit Spreads and SPY"
    PAGE_SUBTITLE = (
        "Does the high-yield minus investment-grade credit spread carry information about "
        "SPY returns that a rule could trade?"
    )

    HEADLINE_H2 = (
        "## HY-IG credit spread → SPY: the out-of-sample record against buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "When companies borrow money, lenders charge riskier companies higher rates. "
        "The gap between the rates paid by high-yield (riskier) and investment-grade "
        "(safer) borrowers is the HY-IG credit spread. It rises when investors worry "
        "about defaults. This study asks whether that gap, observed daily, helps an "
        "SPY (S&P 500 ETF) investor time exposure, and reports the result as measured, "
        "including where it falls short of simply holding SPY."
    )

    WHERE_THIS_FITS = """This is a **single indicator-target analysis**: does the HY-IG credit spread carry
information about SPY returns? The portal contains dozens of such pair studies. Here the
lens is fixed on corporate credit spreads and broad US equity returns measured via SPY.

**How to navigate the four pages.** The Story page explains the economic hypothesis and
the historical episodes. The Evidence page presents the statistical tests and what each
one found. The Strategy page describes the selected trading rule and its out-of-sample
record. The Methodology page is the technical appendix.
"""

    ONE_SENTENCE_THESIS = (
        "The hypothesis tested here: the HY-IG credit spread reflects aggregate default risk, "
        "and rising credit stress is followed by weaker SPY returns (a countercyclical "
        "relationship); the evidence on this page measures how much of that a daily rule "
        "could have used out of sample."
    )

    KPI_CAPTION = (
        f"Winner selected on in-sample data ({W.is_start} to {W.is_end}) by {W.selection_objective}: "
        f"{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}, stable lead range "
        f"{W.plateau_range}. Out of sample ({W.oos_start} to {W.oos_end}) its Sharpe is {W.oos_sharpe} against "
        f"{W.bh_oos_sharpe} for SPY buy-and-hold."
    )

    HERO_TITLE = f"{_yrs()} Years of the HY-IG Credit Spread and SPY"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: HY-IG spread (left axis, inverted, orange) and SPY price (right "
        "axis, blue), 2000-01-03 to 2026-04-22. Shaded bands mark NBER recessions. The spread's highest peaks "
        f"({_H['peaks']['dotcom'][0]:.1f} pp on {_H['peaks']['dotcom'][1]}, {_H['peaks']['gfc'][0]:.1f} on "
        f"{_H['peaks']['gfc'][1]}, {_H['peaks']['covid'][0]:.1f} on {_H['peaks']['covid'][1]}) fell inside the "
        "largest SPY drawdowns. The energy-sector peak "
        f"({_H['peaks']['energy'][0]:.1f} on {_H['peaks']['energy'][1]}) came with a much smaller SPY decline."
    )

    REGIME_TITLE = "SPY Returns in Calm and Stress Regimes of a Causal HMM"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: same-day SPY performance when a 2-state HMM (fit on 2000-2019 data "
        f"only, forward-filtered) puts the stress probability at or below 0.5 (calm, regime Sharpe {_CALM[0]:.2f}, "
        f"{_CALM[1] * 100:.1f}% a year) versus above 0.5 (stress, regime Sharpe {_STRESS[0]:.2f}, {_STRESS[1] * 100:.1f}% a year). "
        "These are concurrent returns: the chart describes the regimes, it is not a "
        "forecast. As a trading signal the same probability's out-of-sample record is on the Evidence page "
        "(HMM block)."
    )

    NARRATIVE_SECTION_1 = """
### Why SPY Investors Watch Corporate Bond Spreads

Academic work going back to Gertler and Lown (1999) and Gilchrist and Zakrajšek (2012)
finds that credit spreads carry information about future economic conditions. Bondholders
and equity holders look at the same companies through different lenses. Equity holders
own the upside; bondholders care mainly about being repaid. When credit investors demand
a higher spread, they are pricing a higher probability of corporate distress.

The HY-IG spread used here is the option-adjusted spread of the ICE BofA US High Yield
Index minus that of the ICE BofA US Corporate (investment-grade) Index (FRED
BAMLH0A0HYM2 minus BAMLC0A0CM). Both legs are option-adjusted spreads over Treasuries,
so the difference isolates the extra compensation for high-yield credit risk.

### The Hypothesised Channels

The literature proposes three channels from wider spreads to weaker SPY returns. They
are hypotheses that this pair's tests then check.

**Channel 1: Credit-cycle tightening (months).** Wider spreads accompany tighter lending
terms, lower investment and weaker earnings expectations across the S&P 500. **What this
would mean for an SPY holder:** a sustained widening would be followed by weaker returns
over the next several months.

**Channel 2: Risk appetite (days to weeks).** Multi-asset allocators cut credit and
equity risk together, so spread widening and SPY selling arrive close together.
**What this would mean for an SPY holder:** the two series move on the same days, which
leaves little time to react.

**Channel 3: Financial conditions (several months).** Credit spreads are a large component
of financial-conditions indices. Tighter conditions weigh on both expected earnings and
valuation multiples. **What this would mean for an SPY holder:** returns would be weaker
for some months after conditions tighten.

The combined hypothesis is **countercyclical**: rising HY-IG spreads go with weaker
SPY returns.

### What This Pair's Data Show

"""
    NARRATIVE_SECTION_1 += (
        f"- **Same day:** the daily spread change and the same-day SPY return have a correlation of "
        f"{_EF['ccf']['lag0']:+.2f}.\n"
        "- **Forward, at daily to quarterly horizons:** predictive regressions of SPY forward returns on the spread "
        "level and the local projections are not significant with overlap-robust (HAC) errors (Evidence page).\n"
        f"- **Monthly Granger test:** rejects \"no predictive content\" at {_EF['granger_monthly']['n_sig']} of "
        f"{_EF['granger_monthly']['n_lags']} monthly lags (homoskedastic F-test).\n"
        "- **Next-month return by spread quartile:** lower in the widest-spread quartile, but the differences are "
        "not statistically significant and not monotonic.\n"
    )
    NARRATIVE_SECTION_1 += (
        f"- **Tradable rule:** the rule selected on in-sample data (stable lead range {W.plateau_range}) has an "
        f"out-of-sample Sharpe of {W.oos_sharpe} versus {W.bh_oos_sharpe} for SPY buy-and-hold.\n"
    )

    NARRATIVE_SECTION_2 = f"""
### Nuance and Limits

**Corrections.** This page previously reported a winner built on an HMM stress probability ({_PREV_HMM.get('combo')}) with an out-of-sample Sharpe of {_f(_AUD[('smoothed_fullsample', 0)]['oos_sharpe'])} (HAC t {_f(_AUD[('smoothed_fullsample', 0)]['hac_t'])}). That probability came from a model fitted on the full sample with forward-backward smoothing, so the value on each day used later data; rebuilt causally, that superseded rule scores {_f(_AUD[('causal_filtered', 0)]['oos_sharpe'])} as published and {_f(_AUD[('causal_filtered', 1)]['oos_sharpe'])} at the lowest grid lead L{_GRID[0]} (file `hmm_lookahead_audit_{_TAG}.json`). The page then reported the since superseded rule {W.previous_rule} (out-of-sample Sharpe {W.previous_oos_sharpe}, published {W.previous_tag}), which was the single highest in-sample Sharpe in the grid, at the top edge of the lead grid; it was superseded on 2026-10-17 by the stable-lead-range selection.

**Publication lag.** ICE BofA OAS values appear on FRED about one business day after their value date. Every traded rule therefore reads the spread at least one day back, and the effective lag is at least two trading days.

**2022.** SPY fell {_pct(_H['spy_drawdown']['rates_2022'])} from its peak during the 2022 Federal Reserve tightening, while the HY-IG spread rose from {_H['spread_at']['2022-01-03']:.2f} (2022-01-03) to a peak of {_H['peaks']['rates'][0]:.2f} percentage points ({_H['peaks']['rates'][1]}). In the 2022 sub-period the selected rule's Sharpe was {_f(_SUB.loc['2022 Rates Shock', 'sharpe'])} (SPY {_f(_SUB.loc['2022 Rates Shock', 'bh_sharpe'])}).

**Selection.** The winner comes from {W.n_valid} in-sample-valid rules ({W.n_distinct} distinct position series). The best in-sample Sharpe from that many candidates overstates what a rule can be expected to deliver; across {W.null_draws} contests run on time-shifted spread data, the winner's stable-range score ranks at the {W.null_percentile} point.
"""

    SCOPE_NOTE = (
        "This page pack analyzes only the HY-IG spread → SPY relationship. SPY also responds to "
        "interest-rate cycles, earnings momentum, valuation multiples, and macro surprises — each "
        "has its own separate analysis in the portal. The portal's separate Yield Curve × SPY "
        "analysis covers the rate cycle."
    )

    TRANSITION_TEXT = (
        "The economic hypotheses point to a countercyclical link. The Evidence page tests it "
        "with correlation, lead-lag, Granger, regime, quantile and local-projection methods, "
        "and reports what each test found."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "The Dot-Com Crash (2000-2002)",
            "narrative": (
                f"SPY (adjusted) fell {_pct(_H['spy_drawdown']['dotcom'])} from its 2000 peak to its 2002 trough. The "
                f"HY-IG spread was already {_H['spread_at']['2000-01-03']:.2f} percentage points on 2000-01-03. It "
                f"widened through 2000, reaching {_H['spread_at']['2000-12-29']:.2f} by year-end, and peaked at "
                f"{_H['peaks']['dotcom'][0]:.2f} on {_H['peaks']['dotcom'][1]}. Telecom and technology issuers that had "
                "financed network build-outs with high-yield debt were at the centre of the credit deterioration."
            ),
            "caption": "The spread widened through 2000 while SPY was falling, and peaked near the SPY low.",
        },
        {
            "slug": "gfc",
            "title": "The Global Financial Crisis (2007-2009)",
            "narrative": (
                f"The HY-IG spread reached a low of {_H['spread_low_2007'][0]:.2f} percentage points on "
                f"{_H['spread_low_2007'][1]}. It rose to {_H['spread_at']['2007-07-31']:.2f} by the end of July and "
                f"{_H['spread_at']['2007-08-31']:.2f} by the end of August 2007, months before SPY peaked on "
                f"2007-10-09. SPY then fell {_pct(_H['spy_drawdown']['gfc'])} to its 2009 trough, while the spread "
                f"peaked at {_H['peaks']['gfc'][0]:.2f} on {_H['peaks']['gfc'][1]}. In this episode the spread moved "
                "before the equity peak. This episode lies in the in-sample period, so the selected rule was chosen on "
                "data that include it (its sub-period result is on the Strategy page)."
            ),
            "caption": "The spread rose from its mid-2007 low before the SPY peak and peaked in late 2008.",
        },
        {
            "slug": "covid",
            "title": "The COVID Shock (2020)",
            "narrative": (
                f"SPY fell {_pct(_H['spy_drawdown']['covid'])} from its February 2020 peak to its March low. The "
                f"HY-IG spread rose from {_H['spread_at']['2020-01-20']:.2f} percentage points (2020-01-20) to "
                f"{_H['peaks']['covid'][0]:.2f} on {_H['peaks']['covid'][1]}, then eased to "
                f"{_H['spread_at']['2020-05-29']:.2f} by the end of May after the Federal Reserve's corporate-credit "
                "facilities. The spread and SPY moved together rather than one leading the other. The selected rule's "
                "result in this episode (its test period) is in the sub-period table on the Strategy page."
            ),
            "caption": "Spread and SPY moved together: both extremes fell on the same day in March 2020.",
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 8-element method blocks
# =========================================================================
_LPC = P.csv_file(_RES / f"core_models_{_TAG}" / "local_projections.csv")
_QRC = P.csv_file(_RES / f"core_models_{_TAG}" / "quantile_regression.csv").set_index("quantile")
_FT = P.csv_file(_RES / f"regime_quartile_forward_tests_{_TAG}.csv").set_index("horizon_months")
_GM, _GD, _CC, _HM = _EF["granger_monthly"], _EF["granger_daily_lag1"], _EF["ccf"], _EF["hmm"]
_SC = _EF["static_corr_level_fwd"]
_TE = _EF["transfer_entropy_proxy_mean"]


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "A **Pearson correlation** measures linear co-movement on a scale from minus one to plus one. The chart "
        "shows a rolling 252-day correlation between the spread LEVEL and the SAME-DAY SPY return. The downloadable "
        "table adds static correlations of each spread signal with SPY forward returns."
    ),
    question=(
        "How do the spread and SPY returns co-move, and do spread signals correlate with future SPY returns?"
    ),
    how_to_read=(
        "Values below zero mean that a higher spread coincides with lower same-day SPY returns. Gray bands are NBER "
        "recessions. Forward-return correlations use overlapping windows, so their iid p-values overstate "
        "significance."
    ),
    chart_name="correlations",
    chart_caption=(
        "Rolling 252-day Pearson correlation between the spread level and same-day SPY daily returns. It is "
        f"negative in {_pct(_EF['rolling_corr_same_day_neg_share'], 0)} of windows."
    ),
    observation=(
        f"The rolling same-day correlation is negative in {_pct(_EF['rolling_corr_same_day_neg_share'], 0)} of "
        "windows and changes sign over time. Static correlations of the spread level with SPY forward returns are "
        f"small: {'; '.join(f'{v:+.3f} at {h} trading days' for h, v in P.items(_SC))}. Their iid "
        "p-values on overlapping windows are not reliable."
    ),
    interpretation=(
        "The level of the spread has little linear relationship with future SPY returns at the horizons tested. The "
        "sign at the longest horizon is positive, the opposite of the countercyclical hypothesis. The strongest "
        "co-movement is same-day (see the cross-correlation block)."
    ),
    key_message=(
        "Spread-level correlations with SPY forward returns are small and change sign across horizons; the clear "
        "relationship is same-day, not forward."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "**Granger causality** tests whether past values of one series improve forecasts of another beyond its own "
        "past. The chart tests month-end changes in the HY-IG spread against the compounded monthly SPY return, at "
        "lags 1-12 months. The spread enters as a monthly change because its level is highly persistent. The "
        "downloadable daily table tests both directions on daily spread changes and SPY returns, at lags 1-5 days."
    ),
    question=(
        "Do past spread changes help predict SPY returns beyond SPY's own history, and does the reverse also hold?"
    ),
    how_to_read=(
        "Each bar is the F-statistic at that lag, with its p-value. The dashed line is the 5% critical value for "
        "that lag. Vermillion bars have p < 0.05. These are homoskedastic F-tests; monthly equity returns are "
        "heteroskedastic, so the p-values are approximate."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        f"Monthly Granger F-tests, spread change to SPY monthly return, {_GM['n_months']} monthly observations. "
        f"p < 0.05 at {_GM['n_sig']} of {_GM['n_lags']} lags (lags {_GM['sig_lag_min']}-{_GM['sig_lag_max']}); "
        + ", ".join(f"lag {x['lag']} is not significant (p = {x['p']:.2f})" for x in _GM["nonsig"]) + "."
    ),
    observation=(
        f"Monthly: lagged spread changes add predictive content for SPY monthly returns at lags {_GM['sig_lag_min']} "
        f"to {_GM['sig_lag_max']} (p from {_GM['sig_p_min']:.4f} to {_GM['sig_p_max']:.4f}). Daily: the test rejects "
        f"in both directions, but much more strongly from SPY to the spread (F = {_GD['spy_to_spread_f']:.1f} at lag "
        f"1) than from the spread to SPY (F = {_GD['spread_to_spy_f']:.2f}, p = {_GD['spread_to_spy_p']:.3f})."
    ),
    interpretation=(
        "At a monthly frequency the test is consistent with the credit-cycle channel: spread changes carry some "
        "information about SPY returns several months later. At a daily frequency the feedback runs mainly from "
        "equities to credit. Neither is causal identification. The forward-return regressions and local projections, "
        "which use overlap-robust errors, do not find a significant effect of the spread level."
    ),
    key_message=(
        f"Monthly spread changes Granger-cause SPY monthly returns at lags {_GM['sig_lag_min']}-{_GM['sig_lag_max']} "
        "(p < 0.01). Daily, SPY returns predict spread changes far more strongly than the reverse."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Cross-Correlation Function (daily changes)",
    method_theory=(
        "The **cross-correlation function** correlates the daily change in the HY-IG spread with the SPY daily "
        "return at lags -20 to +20 trading days. SPY returns are close to serially uncorrelated, so they are used "
        "as they are; the spread is differenced because its level is persistent. (An earlier version differenced the "
        "returns too, which creates an artificial negative pattern at the first lag.)"
    ),
    question="Do spread changes come before SPY moves, after them, or on the same day?",
    how_to_read=(
        "Negative lags pair today's SPY return with an earlier spread change (spread first). Positive lags pair "
        "today's spread change with an earlier SPY return (SPY first). The dashed lines are iid ±95% bands."
    ),
    chart_name="ccf",
    chart_caption=(
        f"Daily spread change vs SPY daily return, lags -20 to +20 trading days. Same day: r = {_CC['lag0']:+.3f}. "
        f"SPY-first lags +1 and +2: {_CC['lag1']:+.3f} and {_CC['lag2']:+.3f}. Spread-first lags outside the band: "
        + ", ".join(f"{x['lag']} ({x['r']:+.3f})" for x in _CC["spread_first_outside_band"]) + "."
    ),
    observation=(
        f"The dominant correlation is same-day (r = {_CC['lag0']:+.3f}). The next largest are at lags +1 and +2 "
        f"({_CC['lag1']:+.3f}, {_CC['lag2']:+.3f}), where the SPY return comes first and the spread widens afterwards. "
        "The spread-first lags outside the iid band are small: "
        + ", ".join(f"{x['r']:+.3f}" for x in _CC["spread_first_outside_band"]) + "."
    ),
    interpretation=(
        "At a daily frequency the spread does not lead SPY. The relationship is same-day, with the spread catching up "
        "to equity moves over the following days. That matches the daily Granger result and the publication lag: by "
        "the time the OAS value is published, the same-day co-movement has already happened."
    ),
    key_message=(
        f"Daily spread changes and SPY returns move together on the same day (r = {_CC['lag0']:+.2f}); spread "
        "widening tends to follow SPY declines rather than precede them."
    ),
)


HMM_BLOCK = dict(
    chart_status="ready",
    method_name="Hidden Markov Model (causal)",
    method_theory=(
        "A 2-state Gaussian **Hidden Markov Model** is fitted to the daily change in the HY-IG spread and the VIX "
        f"level. It is estimated on in-sample data only (to {W.is_end}), standardised with in-sample means and "
        "standard deviations. The stress probability on each day is the forward-filtered probability given data up "
        "to that day. The stress state is the state with the higher in-sample mean spread change. The probability "
        "enters the tournament as signal S6_hmm_stress."
    ),
    question=(
        "Do the HMM regimes separate good and bad SPY periods, and is the stress probability a useful trading signal "
        "once it is computed without future data?"
    ),
    how_to_read=(
        "The shaded area is the stress probability (left axis) and the line is SPY (right axis). Pink bands mark days "
        "with probability above 0.5. Gray bands are NBER recessions."
    ),
    regime_context=(
        f"The filtered stress probability is above 0.5 on {_HM['pct_stress_days']:.1f}% of days "
        f"({_HM['pct_is']:.1f}% in-sample, {_HM['pct_oos']:.1f}% out-of-sample). The superseded version of this "
        "signal was a full-sample, forward-backward smoothed probability. "
        + " ".join(f"On {x['date']} it read {x['smoothed']:.3f} while the causal filter read {x['causal']:.3f}."
                   for x in _HM["smoothed_vs_causal"])
    ),
    chart_name="hmm_regime_probs",
    chart_caption=(
        "Causal HMM stress probability (fit on in-sample data only, forward-filtered) and SPY. Probability above 0.5 "
        f"on {_HM['pct_stress_days']:.0f}% of days."
    ),
    observation=(
        f"Same-day SPY performance differs sharply between the regimes (Story page): regime Sharpe {_CALM[0]:.2f} "
        f"in the calm state and {_STRESS[0]:.2f} in the stress state. As a trading signal, the best "
        f"in-sample-valid HMM rule ({_HB['strategy']}, lead L{_HB['lead_days']}) has an "
        f"in-sample Sharpe of {_f(_HB['is_sharpe'])} and an out-of-sample Sharpe of "
        f"{_f(_HB['oos_sharpe'])}. The previously published HMM rule scores "
        f"{_f(_AUD[('causal_filtered', 0)]['oos_sharpe'])} as published and {_f(_AUD[('causal_filtered', 1)]['oos_sharpe'])} "
        f"at the lowest grid lead when computed causally, against {_f(_AUD[('smoothed_fullsample', 0)]['oos_sharpe'])} "
        "with the smoothed full-sample probabilities."
    ),
    interpretation=(
        "The HMM describes the regimes on the same day, but a causal reading of it does not exceed SPY buy-and-hold "
        "out of sample. Most of the previously published result came from smoothing. In the out-of-sample window, the "
        "gap between the smoothed and filtered probabilities is correlated with the next day's SPY return "
        f"(r = {_HM['gap_corr_next_day_oos']:+.3f}), so the smoothed series contained information about returns that "
        "had not yet happened."
    ),
    key_message=(
        f"The causal HMM stress probability separates same-day regimes (regime Sharpe {_CALM[0]:.2f} vs "
        f"{_STRESS[0]:.2f}), but as a traded signal its best in-sample rule has an out-of-sample Sharpe of "
        f"{_f(_HB['oos_sharpe'])} against SPY's {W.bh_oos_sharpe}. The previously published HMM result "
        "depended on look-ahead smoothing."
    ),
)


REGIME_QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Returns (forward)",
    method_theory=(
        "Month-end HY-IG spreads are split into four equal-count quartiles (Q1 = tightest, Q4 = widest). The test "
        "then measures SPY's return over the **next** 1, 3 and 6 months after each month-end, so it is a forward "
        "test. The Q4 minus Q1 difference and a joint test that all four quartile means are equal use HAC standard "
        "errors. Quartile breakpoints come from the full-sample distribution: they are descriptive bins, not a "
        "trading rule."
    ),
    question=(
        "Are SPY's subsequent returns lower after wide-spread months than after tight-spread months, and is the "
        "pattern monotonic?"
    ),
    how_to_read=(
        "Bars show annualised next-month SPY returns per quartile and the Sharpe ratio. The title gives the Q4-Q1 "
        "difference per month and its HAC t-statistic."
    ),
    regime_context=(
        "The same quartiles look very different on a same-day basis: daily SPY returns run at "
        f"{_EF['quartile_concurrent_ann_return_pct']['Q1']:.1f}% a year in Q1 and "
        f"{_EF['quartile_concurrent_ann_return_pct']['Q4']:.1f}% a year in Q4. That concurrent gradient reflects "
        "spreads widening while equities fall. It is not a forecast, which is why this block uses forward returns."
    ),
    chart_name="regime_quartile_returns",
    chart_caption=(
        f"SPY next-month return by month-end spread quartile, {_FT.loc[1, 'n_months']} months. Annualised: "
        f"Q1 {_pct(_D['quartile_next_month_ann_return']['Q1'])}, Q2 {_pct(_D['quartile_next_month_ann_return']['Q2'])}, Q3 {_pct(_D['quartile_next_month_ann_return']['Q3'])}, "
        f"Q4 {_pct(_D['quartile_next_month_ann_return']['Q4'])}. Q4-Q1 = {_FT.loc[1, 'q4_minus_q1'] * 100:+.2f} pp per month (HAC t "
        f"{_FT.loc[1, 'q4_minus_q1_hac_t']:.2f})."
    ),
    observation=(
        f"Annualised next-month SPY returns are {_pct(_D['quartile_next_month_ann_return']['Q1'])} (Q1), {_pct(_D['quartile_next_month_ann_return']['Q2'])} (Q2), "
        f"{_pct(_D['quartile_next_month_ann_return']['Q3'])} (Q3) and {_pct(_D['quartile_next_month_ann_return']['Q4'])} (Q4). The Q4-Q1 difference is "
        + "; ".join(f"{_FT.loc[h, 'q4_minus_q1'] * 100:+.2f} pp (HAC t {_FT.loc[h, 'q4_minus_q1_hac_t']:.2f}) at "
                    f"{h} month(s)" for h in _FT.index)
        + ". The joint tests of equal means have p = "
        + ", ".join(f"{_FT.loc[h, 'joint_wald_p']:.2f}" for h in _FT.index)
        + (". The pattern is not monotonic at any horizon." if not _FT["monotonic_decreasing"].any() else ".")
    ),
    interpretation=(
        "After the widest-spread months SPY's next-month return was lowest on average in this sample. The difference "
        "from the tightest quartile is small relative to its uncertainty, and Q1 is not the best quartile. The forward "
        "test does not show a reliable gradient."
    ),
    key_message=(
        f"SPY returns after wide-spread months are lower on average (Q4 {_pct(_D['quartile_next_month_ann_return']['Q4'])} vs Q1 "
        f"{_pct(_D['quartile_next_month_ann_return']['Q1'])} annualised, next month), but the difference is not significant (HAC t "
        f"{_FT.loc[1, 'q4_minus_q1_hac_t']:.2f}) and the quartiles are not monotonic."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy (proxy)",
    method_theory=(
        "The chart is a **proxy**, not a full transfer-entropy estimate. Both series are converted to quintile ranks. "
        "Over rolling 504-day windows, stepped monthly, it measures how much the lagged other series adds to the "
        "squared correlation with today's value, beyond the series' own lag, in each direction. It reports no bits "
        "and runs no surrogate or significance test."
    ),
    question=(
        "In the proxy measure, is lagged information flow larger from the spread to SPY or from SPY to the spread?"
    ),
    how_to_read=(
        "Orange: spread to SPY. Blue dashed: SPY to spread. Higher values mean the lagged series adds more to the "
        "squared correlation. Values are small, and without a significance test the lines are descriptive."
    ),
    chart_name="transfer_entropy",
    chart_caption=(
        f"Transfer-entropy proxy over rolling 504-day windows: mean {_TE['spread_to_spy']:.4f} for spread to SPY and "
        f"{_TE['spy_to_spread']:.4f} for SPY to spread. No significance test."
    ),
    observation=(
        f"Over the sample the proxy averages {_TE['spread_to_spy']:.4f} from the spread to SPY and "
        f"{_TE['spy_to_spread']:.4f} in the other direction. Both are small (squared-correlation increments near zero) "
        "and the series is noisy across windows."
    ),
    interpretation=(
        "The proxy shows a slightly larger lagged increment from the spread to SPY than the reverse. It runs on "
        "quintile ranks and does not test significance, so it adds little beyond the Granger and cross-correlation "
        "results."
    ),
    key_message=(
        f"A rank-based transfer-entropy proxy is small in both directions ({_TE['spread_to_spy']:.4f} vs "
        f"{_TE['spy_to_spread']:.4f}) and has no significance test; read it as descriptive."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "**Local projections** (Jordà, 2005) regress the SPY forward return over h trading days on today's spread "
        "level, with the VIX and the 10y-3m Treasury spread as controls, at horizons of "
        + ", ".join(str(h) for h in _LPC["horizon_days"]) + " trading days. Forward windows overlap, so "
        "standard errors are Newey-West HAC with maxlags = max(0.75·n^(1/3), h-1): "
        + ", ".join(str(x) for x in _LPC["hac_maxlags"]) + "."
    ),
    question=(
        "After controlling for VIX and the yield curve, does a higher spread level predict lower SPY returns over the "
        "next week, month or quarter?"
    ),
    how_to_read=(
        "The line is the coefficient (return per percentage point of spread) at each horizon. The band is the 95% HAC "
        "confidence interval. A band that excludes zero would indicate significance."
    ),
    chart_name="local_projections",
    chart_caption=(
        "Local projections of SPY forward returns on the spread level (controls: VIX, 10y-3m), HAC maxlags ≥ h-1. "
        + "; ".join(f"h = {r.horizon_days}d: t {r.t_stat:.2f}" for r in _LPC.itertuples())
        + (". None significant." if (_LPC["p_value"] >= 0.05).all() else ".")
    ),
    observation=(
        "The coefficients are "
        + ", ".join(f"{r.coef:+.4f} ({r.horizon_days} days, p = {r.p_value:.2f})" for r in _LPC.itertuples())
        + " per percentage point. An earlier version of this table used too short a HAC lag for the overlapping "
        "long-horizon returns and reported a significant effect; with the lag set to at least h-1 it is not."
    ),
    interpretation=(
        "The point estimates have the countercyclical sign, but the data do not distinguish them from zero once the "
        "overlap in forward returns is accounted for."
    ),
    key_message=(
        "The spread level's effect on SPY forward returns is negative but not statistically significant at any "
        f"horizon tested (HAC t between {P.colmin(_LPC, 't_stat'):.2f} and {P.colmax(_LPC, 't_stat'):.2f})."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "**Quantile regression** estimates the slope of the SPY 21-trading-day forward return on the spread level at "
        "quantiles across the return distribution. The aim is to see whether the spread shifts the whole "
        "distribution, or mainly one tail."
    ),
    question=(
        "Does a wider spread mainly lower the worst outcomes, or does it widen the distribution in both directions?"
    ),
    how_to_read=(
        "Each point is the slope at that quantile; the band is its 95% interval. Negative slopes in the low quantiles "
        "and positive slopes in the high quantiles of similar size mean the spread widens the distribution "
        "symmetrically."
    ),
    chart_name="quantile_regression",
    chart_caption=(
        "Quantile slopes of the 21-day forward SPY return on the spread level: "
        + ", ".join(f"tau={q:.2f} {r.coef:+.4f}" for q, r in _QRC.iterrows()) + "."
    ),
    observation=(
        f"The lowest and highest quantile slopes are {_QRC['coef'].iloc[0]:+.4f} and {_QRC['coef'].iloc[-1]:+.4f}; the "
        f"median slope is {_QRC.loc[0.5, 'coef']:+.4f} (p = {_QRC.loc[0.5, 'p_value']:.2f}). Slopes other than the "
        f"median have p < 0.05 at {_QT_TAILS['n_sig_05']} of "
        f"{_QT_TAILS['n']} quantiles."
    ),
    interpretation=(
        f"A wider spread goes with a wider spread of {_QR_H}-day SPY outcomes in both directions, a volatility effect, rather "
        "than a lower median or a mainly left-tail effect. The data do not show an asymmetric downside effect."
    ),
    key_message=(
        f"Wider HY-IG spreads widen the {_QR_H}-day SPY return distribution about equally in both tails (lowest quantile "
        f"{_QRC['coef'].iloc[0]:+.4f}, highest {_QRC['coef'].iloc[-1]:+.4f}); the median effect is near zero."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        f"Each spread signal is shifted by every lead in the traded grid {_GRID_SET} (trading days) and "
        "correlated with SPY's next-day return. The grid starts at the first lead because "
        "ICE BofA OAS values are published about one business day late. The axis is the "
        "pair's native daily axis."
    ),
    question=(
        "At which daily lead, if any, do the spread signals correlate with SPY's next-day "
        "return?"
    ),
    how_to_read=(
        "Rows are signal transforms; columns are leads in trading days. Cell colour and text "
        "show Pearson r. Stars mark iid p < 0.05 (*) and p < 0.01 (**)."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson r between each signal, shifted by each lead in the grid, and SPY's next-day return. Stars mark iid p < 0.05."
    ),
    observation=(
        f"The winner's signal ({_SIGCOL}) has r "
        + (", ".join(f"{_LCW[f'L{int(L)}']} at {L} days" for L in _LEADS) if _LCW is not None else "n/a")
        + "."
    ),
    interpretation=(
        "At a daily frequency the spread signals carry very little linear information about "
        "the next day's SPY return at any lead in the grid. Any trading value has to come "
        "from position rules (thresholds, sizing) rather than a linear lead relationship."
    ),
    key_message=(
        f"On the daily lead grid ({_GRID[0]} to {_GRID[-1]} trading days) the spread signals' linear correlation with SPY's "
        "next-day return is small."
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        f"The orange line takes the winning rule ({W.signal_code} / {W.threshold_code} / {W.strategy_family}) "
        f"and shows its out-of-sample Sharpe at each lead in the daily grid {_GRID_SET} trading days. "
        "The winner was chosen on IN-SAMPLE data. The grey bars show the highest out-of-sample Sharpe that any "
        "in-sample-valid rule reached at each lead; that is an out-of-sample maximum, so it is biased upward."
    ),
    question=(
        "How does the selected rule perform out of sample at each lead, and how does that compare with "
        "buy-and-hold?"
    ),
    how_to_read=(
        "Orange line and star: the winning rule's out-of-sample Sharpe by lead, with the star at its traded lead. "
        "Grey bars: the best out-of-sample Sharpe at each lead (selection-biased context). Dashed: SPY "
        "buy-and-hold. The stable-lead-range chart below the tabs shows the in-sample scores used for selection."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "The winning rule's out-of-sample Sharpe by lead: "
        + ", ".join(f"{r.lead_days}d {_f(r.oos_sharpe)}" for r in _WC.itertuples())
        + f" (traded L{W.lead}). SPY buy-and-hold: {W.bh_oos_sharpe}."
    ),
    observation=(
        f"The winner, {W.signal_code} / {W.threshold_code} / {W.strategy_family} at L{W.lead}, was selected on "
        f"in-sample data: its stable lead range {W.plateau_range} has the best lowest in-sample Sharpe in the grid. "
        f"Its out-of-sample Sharpe is {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold."
    ),
    interpretation=(
        "In-sample rank carries limited information about out-of-sample rank in this grid "
        f"(Spearman {_WS['tracks']['main']['spearman_is_oos']} across the in-sample-valid rules)."
    ),
    key_message=(
        f"The selected rule {W.signal_code} / {W.threshold_code} / {W.strategy_family} at L{W.lead} has an "
        f"out-of-sample Sharpe of {W.oos_sharpe} against {W.bh_oos_sharpe} for SPY buy-and-hold."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "*The HY-IG spread and SPY are tested with correlation, lead-lag, Granger, regime, "
        "quantile and local-projection methods on daily data from 2000-01-03 to 2026-04-22 "
        "(monthly aggregates where stated). The tests agree on a strong same-day "
        "relationship. They disagree on forward predictability: the monthly Granger test "
        "finds some, while the overlap-robust regressions and the quartile forward test do "
        "not find a significant effect.*"
    ),
    "downloads": [
        {"label": "Granger causality, daily, both directions",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/granger_causality.csv"},
        {"label": "Predictive regressions, HAC",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/predictive_regressions.csv"},
        {"label": "Quantile regression of forward SPY returns",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/quantile_regression.csv"},
        {"label": "Local projections, HAC",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/local_projections.csv"},
        {"label": "Regime quartile forward tests",
         "path": f"results/hy_ig_spy/regime_quartile_forward_tests_{_TAG}.csv"},
        {"label": "Diagnostics summary",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/diagnostics_summary.csv"},
        {"label": "HMM 2-state summary (causal fit; JSON body)",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/hmm_summary.csv"},
        {"label": "HMM look-ahead audit (smoothed vs causal, same rule)",
         "path": f"results/hy_ig_spy/hmm_lookahead_audit_{_TAG}.json"},
    ],
    "plain_english": (
        "This section runs several statistical tests on one question: does the HY-IG credit "
        "spread carry useful information about future SPY returns? Each block states what the "
        "test found, including where the result is weak or not significant."
    ),
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Lead Analysis", "Lead Tournament", "Granger Causality", "Cross-Correlation"],
    "level2": [
        HMM_BLOCK,
        REGIME_QUARTILE_BLOCK,
        TRANSFER_ENTROPY_BLOCK,
        LOCAL_PROJECTIONS_BLOCK,
        QUANTILE_BLOCK,
    ],
    "level2_labels": [
        "HMM Regime Analysis",
        "Regime Quartile Returns",
        "Transfer Entropy (proxy)",
        "Local Projections",
        "Quantile Regression",
    ],
    "tournament_intro": (
        f"The tournament combined {P.length(_MAN['signals'])} signals (spread level, z-scores, percentile ranks, rates of "
        "change, momentum, acceleration, the CCC-BB spread, and causal HMM and Markov-switching stress probabilities) "
        f"with their threshold labels, {_N_STRAT} strategies (Long/Cash, Signal-Strength, Long/Short; Signal-Strength "
        f"ignores the threshold and is declared once per signal) and the lead grid {_GRID_SET} (trading days): "
        f"{W.n_candidates} combinations, {W.n_valid} in-sample-valid ({W.n_distinct} distinct position series). Each "
        "window of three neighbouring leads was scored by its lowest in-sample Sharpe; the winner is the highest "
        f"in-sample Sharpe inside the best window: **{W.signal_code} / {W.threshold_code} / {W.strategy_family} / "
        f"L{W.lead}** (stable lead range {W.plateau_range}), in-sample Sharpe {W.is_sharpe} against {W.bh_is_sharpe} "
        f"for SPY over {W.is_start} to {W.is_end}. On the held-out {W.oos_start} to {W.oos_end} window it scored "
        f"{W.oos_sharpe}, against {W.bh_oos_sharpe} for SPY buy-and-hold. The single highest in-sample Sharpe in the "
        f"grid ({W.raw_argmax_rule} at L{W.raw_argmax_lead}, {W.raw_argmax_is_sharpe}) is {W.raw_argmax_is_winner}, "
        f"{W.raw_argmax_position}; it is shown for reference and is not the selection rule."
    ),
    "transition": (
        "**Transition:** the tests show a strong same-day link and weak forward "
        "predictability. Next: what the selected rule does and how it performed out of "
        "sample."
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    """Strategy-page content object (passed to `render_strategy_page`)."""

    PAGE_TITLE = "The Strategy: A Credit-Spread Rule for SPY, Selected on In-Sample Data"
    PAGE_SUBTITLE = (
        f"{W.n_candidates} rule combinations were scored. The rule selected on in-sample data by the stable-lead-range "
        "rule is reported here, with its out-of-sample record against buy-and-hold."
    )

    STATISTICAL_FRAMING_BANNER = (
        f"Correction (2026-10-17). This page previously reported the rule {W.previous_rule} (out-of-sample Sharpe "
        f"{W.previous_oos_sharpe}, published {W.previous_tag}), the single highest in-sample Sharpe in the grid at "
        "the top edge of the lead grid. It now reports the rule selected by the stable-lead-range rule. Before "
        "2026-10-16 the page reported an HMM rule whose result relied on look-ahead smoothing (see the caveats)."
    )

    PLAIN_ENGLISH = (
        f"The rule moves between SPY and cash: {_RULE}. This section explains the rule, its numbers and its "
        "limitations."
    )

    # Status and badge rule come from track_summary.json (components.two_track.badge_status); this text states
    # facts only.
    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="",
        status_detail=(
            "Selected on the training period from market data (one track: credit spreads are not revised); it has "
            "not faced a frozen-rule hold-out test."
        ),
        strengths=[
            f"Long daily history: training period {W.is_start} to {W.is_end}.",
            f"The chosen lead sits in a stable lead range ({W.plateau_range}).",
        ],
        risks=[
            f"Test-period Sharpe difference versus buy-and-hold {W.sharpe_gap}, 95% interval {W.ci_low} to "
            f"{W.ci_high}.",
            f"Forward predictability: daily Granger p-value {_GD['spread_to_spy_p']:.3f} from spread to SPY, "
            f"against F {_GD['spy_to_spread_f']:.1f} from SPY to spread (the market moves the spread more than the "
            "reverse).",
            f"Costs: at 5 bps per unit of position change the test-period Sharpe is {W.oos_sharpe_net_5bp}.",
        ],
        conclusion=(
            f"Rule {W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}: test-period Sharpe "
            f"{W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold ({W.oos_start} to {W.oos_end}), maximum "
            f"drawdown {W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}."
        ),
    )

    SIGNAL_RULE_MD = (
        f"**Strategy Rule in Plain English:** {_RULE}. The position takes effect from the next day's close "
        f"(signal lead {W.lead_text} plus a one-day execution lag). Countercyclical orientation: a high reading "
        "means cash. "
        f"Test-period record ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} "
        f"buy-and-hold; annualized return {W.oos_ann_return} versus {W.bh_oos_ann_return}; maximum drawdown "
        f"{W.oos_max_drawdown} versus {W.bh_oos_max_drawdown}; {W.oos_n_trades} position changes."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "The HY-IG spread is ICE BofA US High Yield OAS minus ICE BofA US Corporate OAS (FRED BAMLH0A0HYM2 and "
        f"BAMLC0A0CM), in percentage points, on business days. The signal is the {_SIG}. The rule reads it "
        f"{W.lead_text} back (the value is published about one business day after its date) and compares it with "
        f"{_THR}. It rebalances daily: {W.oos_n_trades} position changes in the out-of-sample window. The rule fits "
        "no model; any rolling statistic is recomputed each day from trailing data."
    )

    MANUAL_USE_MD = (
        "If you want to follow this rule with minimal code:\n\n"
        "1. **Pull HY and IG OAS from FRED** (BAMLH0A0HYM2 and BAMLC0A0CM), daily. They post about one business "
        "day after the value date.\n"
        "2. **Compute the spread**: HY OAS minus IG OAS (percentage points).\n"
        f"3. **Compute the signal**: the {_SIG}.\n"
        f"4. **Take its value from {W.lead_text} ago** and compare it with {_THR}.\n"
        "5. **Hold SPY** if it is below; **hold cash** otherwise. Apply the change at the next close.\n"
        f"6. **Expect the documented record**: out-of-sample Sharpe {W.oos_sharpe} vs {W.bh_oos_sharpe} for SPY over "
        f"{W.oos_start} to {W.oos_end}."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

    WALK_FORWARD_TITLE = "Calendar-Year Sharpe of the Winning Rule vs SPY"
    WALK_FORWARD_CAPTION = (
        f"What this shows: the rule's Sharpe in each calendar year {_WF1['first_year']}-{_WF1['last_year']} "
        "(bars) next to SPY's Sharpe in the same year (markers). Positive in "
        f"{_WF1['n_positive']} of {_WF1['n_years']} years and above SPY in "
        f"{_WF1['n_above_bh']} of {_WF1['n_years']}. Years before 2019-10 are in-sample: the "
        "rule was selected on them."
    )

    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: each point is one in-sample-valid rule, plotted by in-sample Sharpe (x) and out-of-sample "
        f"Sharpe (y). The star is the winner (in-sample {W.is_sharpe}, out-of-sample {W.oos_sharpe}). Spearman rank "
        f"correlation of in-sample vs out-of-sample: {_WS['tracks']['main']['spearman_is_oos']}."
    )

    LEADERBOARD_NOTE_MD = (
        "Rows ranked by in-sample Sharpe. Strategy P2 sizes on the signal's trailing 504-day range and ignores the "
        f"threshold, so it is declared once per signal and lead ({W.n_valid} valid rows, {W.n_distinct} distinct "
        "series)."
    )

    CROSS_PERIOD_CAPTIONS = {
        "subperiod_sharpe": (
            "How to read it: the rule's Sharpe in each stress episode and in the full in-sample and out-of-sample "
            "windows, next to SPY's: "
            + "; ".join(f"{k} {_f(r.sharpe)} (SPY {_f(r.bh_sharpe)})" for k, r in _SUB.iterrows() if pd.notna(r.sharpe))
            + ". Blank episodes are before the rule's first position."
        ),
        "rolling_sharpe_cp": (
            f"How to read it: 504-trading-day rolling Sharpe of the rule's daily returns. It is positive in "
            f"{_RSH['pos_share'] * 100:.0f}% of windows and ranges from {_f(_RSH['min'])} to {_f(_RSH['max'])}."
        ),
        "rolling_granger": (
            "How to read it: rolling 504-day Granger test, winner signal -> SPY daily return, lags 1-3, every 5 "
            "trading days; the F shown is the largest of the three lags, so read the p-value line. p < 0.05 in "
            f"{_RGR['sig_share'] * 100:.0f}% of windows."
        ),
        "rolling_correlation": (
            "How to read it: rolling 504-day correlation between the winner signal (lagged by its lead plus one "
            f"execution day) and SPY's daily return. It ranges from {_RCO['min']:+.3f} to {_RCO['max']:+.3f} and is "
            f"negative in {_RCO['neg_share'] * 100:.0f}% of windows. For this countercyclical rule the expected sign "
            "is negative."
        ),
        "structural_break": (
            "How to read it: Quandt likelihood-ratio (sup-F) test for a break in the regression of SPY daily returns "
            f"on the lagged winner signal (HAC, 15% trimming). {_SB['conclusion']}."
        ),
    }

    CAVEATS_MD = f"""
**Important Caveats**

1. **Simulated, not executed.** All performance statistics are hypothetical, from rules applied to historical data. Returns are gross of costs. At 5 bps per unit of position change the out-of-sample Sharpe is {W.oos_sharpe_net_5bp} (higher cost levels: `tournament_validation_{_TAG}/transaction_costs.csv`).

2. **Superseded results.** The earlier HMM rule ({_PREV_HMM.get('combo')}, previously published out-of-sample Sharpe {_f(_AUD[('smoothed_fullsample', 0)]['oos_sharpe'])}) relied on full-sample, forward-backward smoothed HMM probabilities (look-ahead); its causal rebuild scores {_f(_AUD[('causal_filtered', 0)]['oos_sharpe'])} as published and {_f(_AUD[('causal_filtered', 1)]['oos_sharpe'])} at the lowest grid lead L{_GRID[0]}. The rule previously published on {W.previous_tag} ({W.previous_rule}, out-of-sample Sharpe {W.previous_oos_sharpe}) was an isolated top-edge peak.

3. **Selection.** The winner comes from {W.n_valid} valid rules ({W.n_distinct} distinct position series). The test-period Sharpe difference versus buy-and-hold is {W.sharpe_gap} (95% interval {W.ci_low} to {W.ci_high}); across {W.null_draws} contests on time-shifted spread data its stable-range score ranks at the {W.null_percentile} point.

4. **Lead robustness.** The stable lead range is {W.plateau_range}; the single highest in-sample Sharpe in the grid (L{W.raw_argmax_lead}, {W.raw_argmax_is_sharpe}) was not chosen.

5. **OAS publication lag.** ICE BofA OAS post on FRED about one business day after the value date. The shortest lead in the traded grid is one trading day, and positions take effect after a further execution day.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**Reading the trade log.** Each row of `winner_trades_broker_style.csv` is one position change: the entry "
        "date, the side (Long or Cash), the SPY price, how long the position was held and the signal value on the "
        "entry date. Rows are tagged IS or OOS."
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = P.definition_text("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **HY-IG Spread (HY leg)** | FRED (ICE BofA US High Yield Index OAS) | BAMLH0A0HYM2 | Daily (business days; ~1-day publication lag) |
| **HY-IG Spread (IG leg)** | FRED (ICE BofA US Corporate Index OAS) | BAMLC0A0CM | Daily (business days; ~1-day publication lag) |
| **SPY (Target)** | Yahoo Finance | SPY adjusted close | Daily |
| **VIX (HMM feature, LP control)** | Yahoo Finance | ^VIX | Daily |
| **10y-3m Treasury spread (LP control)** | FRED | DGS10 - DTB3 | Daily |
| **NBER Recession Dates (chart shading)** | FRED / NBER | USREC | Monthly |

*Scope discipline.* Only HY-IG spread derivatives (and the causal regime probabilities built
from the spread and VIX) are trading signals. VIX and the 10y-3m spread enter only as the HMM
feature and as regression controls. Pre-2023 OAS history is spliced from the archived v1 data
(see `interpretation_metadata.json` caveats).
""")

_INDICATOR_CONSTRUCTION_MD = (
    "The primary indicator is the HY-IG credit spread, built daily as the ICE BofA US High "
    "Yield Index option-adjusted spread (FRED: BAMLH0A0HYM2) minus the ICE BofA US Corporate "
    "Index option-adjusted spread (FRED: BAMLC0A0CM), in percentage points. From it the "
    "pipeline derives the level, 252/504-day rolling z-scores, 504/1260-day percentile ranks, "
    "21/63/126-day percent changes, 21/63/252-day changes, an acceleration term and the "
    "CCC-BB quality spread. It also builds causal regime probabilities: a 2-state "
    "Gaussian HMM on [daily spread change, VIX], and a 2-state Markov-switching model of "
    "the daily spread change. Both are fitted on in-sample data only (to 2019-09-30) and "
    "forward-filtered, so the value on day t uses data up to t only "
    "(scripts/_regime_causal.py). "
    f"The winning signal is `{W.signal_code}` ({_SIG}). The authoritative list of derivatives is rendered from "
    "`signal_scope.json` in the Signal Universe section below."
)

_METHODS_TABLE_MD = P.definition_text("""
| Method | Question It Answers | Specification |
|:-------|:--------------------|:--------------|
| Pearson / Rolling Correlation | Same-day and forward co-movement | Rolling 252d same-day; static vs 1-252d forward returns (iid p-values, overlapping) |
| Granger Causality | Do lagged spread changes help forecast SPY (and vice versa)? | Monthly: month-end spread change → compounded monthly SPY return, lags 1-12 (F-test). Daily: both directions, lags 1-5 |
| Cross-Correlation Function | Same-day vs lead/lag timing | Daily spread change vs SPY daily return, lags ±20 trading days |
| Hidden Markov Model (2-state) | Latent credit regimes | GaussianHMM on [spread change, VIX]; in-sample fit to 2019-09; forward-filtered probabilities |
| Markov-switching model | High-variance regime of spread changes | 2-regime switching mean/variance on daily spread change; in-sample fit; Hamilton-filtered |
| Regime Quartile Returns | Forward SPY return after tight vs wide spreads | Month-end spread quartiles vs next 1/3/6-month SPY return; HAC tests |
| Transfer-entropy proxy | Lagged information flow, both directions | Squared-correlation increment on quintile ranks, rolling 504d; no significance test |
| Local Projections (Jordà) | Spread level → SPY forward return at 5/21/63 days | Controls VIX, 10y-3m; HAC maxlags = max(0.75 n^(1/3), h-1) |
| Predictive regressions | 12 signals × 5 horizons | OLS with HAC maxlags = max(0.75 n^(1/3), h-1) |
| Quantile Regression | Effect across the 21-day forward return distribution | Quantiles 5%-95% |
""")

_GRID_TABLE_MD = P.definition_text(f"""
| Dimension | Values |
|:----------|:-------|
| **Signals ({P.length(_MAN['signals'])})** | {"; ".join(SIGNAL_TEXT.get(k, k) for k in _MAN['signals'])} |
| **Thresholds ({_N_THR} labels)** | T1 in-sample percentile p75/p85/p95 (expanding over the in-sample readings before each day, 400-day warm-up, frozen at the in-sample end); T2 rolling-504d percentile rp75/rp85/rp95; T3 rolling-504d z-score 1.5/2.0/2.5; T4/T5 probability 0.5/0.7 (S6/S7 only) |
| **Strategies ({_N_STRAT})** | Long/Cash (P1), Signal-Strength sizing on the trailing-504d range (P2; ignores the threshold, declared once per signal and lead), Long/Short (P3) |
| **Lead times (trading days)** | {", ".join(str(x) for x in _MAN['leads'])}, the standard daily grid floored for the OAS publication lag; plus a {_MAN['position_shift']}-day execution lag |
| **Orientation** | Countercyclical (high signal -> reduce SPY exposure) |
| **Selection** | Stable lead range (D9): each window of three neighbouring leads scored by its lowest in-sample Sharpe on the common window, winner = highest in-sample Sharpe inside the best window, among in-sample-valid rules (>= {_MAN['min_is_n']:,} IS days, IS exposure {_MAN['exposure_bounds'][0]:.0%}-{_MAN['exposure_bounds'][1]:.0%}, IS turnover < {_MAN['max_is_turnover']}/yr, >= {_MAN['min_is_trades']} IS trades; undefined positions held as cash) |
""")

_TOURNAMENT_DESIGN_MD = f"""{_GRID_TABLE_MD}
{W.n_candidates} combinations, {W.n_valid} in-sample-valid ({W.n_distinct} distinct position series). Winner: **{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}**, stable lead range {W.plateau_range}, in-sample Sharpe {W.is_sharpe} (SPY {W.bh_is_sharpe}). Out of sample ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} vs SPY {W.bh_oos_sharpe}, annual return {W.oos_ann_return} vs {W.bh_oos_ann_return}, maximum drawdown {W.oos_max_drawdown} vs {W.bh_oos_max_drawdown}. Highest single in-sample Sharpe in the grid (reference only, not the selection rule): {W.raw_argmax_rule} at L{W.raw_argmax_lead}, in-sample Sharpe {W.raw_argmax_is_sharpe}, {W.raw_argmax_is_winner}, {W.raw_argmax_position}.
"""

_REFERENCES_MD = """
#### Credit Markets and Equity Prediction
- Gertler, M., & Lown, C. S. (1999). The information in the high yield bond spread for the business cycle. *Oxford Review of Economic Policy*, 15(3), 132–150.
- Gilchrist, S., & Zakrajšek, E. (2012). Credit spreads and business cycle fluctuations. *American Economic Review*, 102(4), 1692–1720.
- Mueller, P. (2009). Credit spreads and real activity. *Working Paper, Columbia Business School*.

#### Hidden Markov Models and Regime Detection
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384.
- Guidolin, M., & Timmermann, A. (2007). Asset allocation under multivariate regime switching. *Journal of Economic Dynamics and Control*, 31(11), 3503–3544.

#### Nonlinear Dependence and Information Theory
- Schreiber, T. (2000). Measuring information transfer. *Physical Review Letters*, 85(2), 461–464.

#### Impulse Response and Local Projections
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.

#### Inference and Structural Breaks
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Andrews, D. W. K. (1993). Tests for parameter instability and structural change with unknown change point. *Econometrica*, 61(4), 821–856.

#### Quantile Methods
- Koenker, R., & Bassett, G. (1978). Regression quantiles. *Econometrica*, 46(1), 33–50.
- Adrian, T., Boyarchenko, N., & Giannone, D. (2019). Vulnerable growth. *American Economic Review*, 109(4), 1263–1289.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Data run from 2000-01-03 to 2026-04-22 (business days). The OOS window follows the ECON-OOS2 formula: "
        f"{_OOS_MONTHS} months ({W.oos_start} -> {W.oos_end}). In-sample selection uses the common window {W.is_start} -> "
        f"{W.is_end}, which starts when the longest-warm-up eligible candidate has its first return. The dot-com bust "
        "and the GFC are in-sample; the COVID shock and the post-pandemic rate shock are out-of-sample. Regime models are fitted on "
        "data up to 2019-09-30 only."
    ),
    plain_english=(
        "This section covers the technical decisions — data sources, sample period, "
        "model specifications, and known limitations. Readers who want to replicate or "
        "challenge the analysis will find what they need here."
    ),
)
