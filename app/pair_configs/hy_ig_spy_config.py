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

from components.page_templates import MethodologyConfig
from components.winner_fields import load

W = load("hy_ig_spy")
_RES = Path(__file__).resolve().parents[2] / "results" / "hy_ig_spy"
_WS = json.loads((_RES / "winner_summary.json").read_text())
_TAG = _WS["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
_T = pd.read_csv(_RES / f"tournament_results_{_TAG}.csv")
_T = _T[_T["signal"] != "BENCHMARK"]
_TV = _T[_T["valid"].astype(str).str.lower() == "true"]
_HMM = _TV[_TV["signal"] == "S6_hmm_stress"].sort_values("is_sharpe", ascending=False).head(1)
_AUD = {(r["probabilities"], r["lead_days"]): r for r in json.loads((_RES / f"hmm_lookahead_audit_{_TAG}.json").read_text())["rows"]}
_LC = pd.read_csv(_RES / f"lead_correlation_{_TAG}.csv").set_index("transform")
_WC = pd.read_csv(_RES / f"lead_winner_curve_{_TAG}.csv")
_SUB = pd.read_csv(_RES / "subperiod_sharpe.csv").set_index("period_name")
_COST = pd.read_csv(_RES / f"tournament_validation_{_TAG}" / "transaction_costs.csv")
_COST = _COST[_COST["rank"] == 1].set_index("tx_cost_bps")["net_sharpe_approx"]
_WF = pd.read_csv(_RES / f"tournament_validation_{_TAG}" / "walk_forward.csv")
_WF = _WF[_WF["rank"] == 1]
_SB = json.loads((_RES / "structural_break_hy_ig_spy.json").read_text())
_RSH = pd.read_csv(_RES / "rolling_sharpe_hy_ig_spy.csv")["rolling_sharpe_24m"]
_RCO = pd.read_csv(_RES / "rolling_correlation_hy_ig_spy.csv")["rolling_corr_24m"]
_RGR = pd.read_csv(_RES / "rolling_granger_hy_ig_spy.csv")["p_value_24m"]
_SIGCOL = _WS["signal_column"]
_HP = pd.read_parquet(_RES / f"signals_{_TAG}.parquet")["hmm_2state_prob_stress"]
_SPY = pd.read_parquet(Path(__file__).resolve().parents[2] / "data" / "hy_ig_spy_daily_20000101_20260422.parquet")["spy_ret"]
_HP = _HP.reindex(_SPY.index, method="ffill")


def _regime(mask):
    r = _SPY[mask].dropna()
    return (r.mean() * 252) / (r.std() * 252 ** 0.5), r.mean() * 252


_CALM = _regime((_HP <= 0.5) & _HP.notna())
_STRESS = _regime(_HP > 0.5)
_LCW = _LC.loc[_SIGCOL] if _SIGCOL in _LC.index else None
_LEADS = [1, 5, 21, 63, 126, 252]


def _f(v, nd=2):
    return "n/a" if v is None or pd.isna(v) else f"{float(v):.{nd}f}"


THRESHOLD_TEXT = {
    "T2_rp75": "the 75th percentile of its own trailing 504 trading days", "T2_rp85": "the 85th percentile of its own trailing 504 trading days",
    "T2_rp95": "the 95th percentile of its own trailing 504 trading days", "T1_p75": "its in-sample 75th percentile",
    "T1_p85": "its in-sample 85th percentile", "T1_p95": "its in-sample 95th percentile",
    "T3_z1.5": "a trailing 504-day z-score of 1.5", "T3_z2.0": "a trailing 504-day z-score of 2.0",
    "T3_z2.5": "a trailing 504-day z-score of 2.5", "T4_hmm_0.5": "0.5", "T4_hmm_0.7": "0.7", "T5_ms_0.5": "0.5",
    "T5_ms_0.7": "0.7", "-": "its trailing 504-day range (sizing; no threshold)",
}
_THR = THRESHOLD_TEXT.get(W.threshold_code, W.threshold_code)
_SIG = (W.signal_display if W.signal_display[:2].isupper() else W.signal_display[:1].lower() + W.signal_display[1:])
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

    HERO_TITLE = "26 Years of the HY-IG Credit Spread and SPY"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: HY-IG spread (left axis, inverted, orange) and SPY price (right "
        "axis, blue), 2000-01-03 to 2026-04-22. Shaded bands mark NBER recessions. The "
        "spread's highest peaks (8.5 pp in 2002, 15.3 in 2008, 6.9 in 2020) fell inside the "
        "three largest SPY drawdowns. The 2016 energy-sector peak (6.7) came with a much "
        "smaller SPY decline."
    )

    REGIME_TITLE = "SPY Returns in Calm and Stress Regimes of a Causal HMM"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: same-day SPY performance when a 2-state HMM (fit on 2000-2019 data "
        f"only, forward-filtered) puts the stress probability at or below 0.5 (calm, regime Sharpe {_CALM[0]:.2f}, "
        f"{_CALM[1] * 100:.1f}% a year) versus above 0.5 (stress, regime Sharpe {_STRESS[0]:.2f}, {_STRESS[1] * 100:.1f}% a year). "
        "These are concurrent returns: the chart describes the regimes, it is not a "
        "forecast. As a trading signal the same probability did not beat buy-and-hold "
        "out of sample (Evidence page, HMM block)."
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

**Channel 3: Financial conditions (1-6 months).** Credit spreads are a large component
of financial-conditions indices. Tighter conditions weigh on both expected earnings and
valuation multiples. **What this would mean for an SPY holder:** returns would be weaker
for some months after conditions tighten.

The combined hypothesis is **countercyclical**: rising HY-IG spreads go with weaker
SPY returns.

### What This Pair's Data Show

- **Same day:** strong. The daily spread change and the same-day SPY return have a
  correlation of -0.44.
- **Forward, at daily to quarterly horizons:** weak. Predictive regressions of SPY
  forward returns on the spread level are insignificant at 1 to 126 trading days with
  overlap-robust (HAC) errors, and the local projections are insignificant at 5, 21 and
  63 days.
- **Monthly Granger test:** rejects "no predictive content" at lags of 3 to 12 months
  (homoskedastic F-test).
- **Next-month return by spread quartile:** lower in the widest-spread quartile, but the
  differences are not statistically significant and not monotonic.
"""
    NARRATIVE_SECTION_1 += (
        f"- **Tradable rule:** the rule selected on in-sample data (stable lead range {W.plateau_range}) has an "
        f"out-of-sample Sharpe of {W.oos_sharpe} versus {W.bh_oos_sharpe} for SPY buy-and-hold.\n"
    )

    NARRATIVE_SECTION_2 = f"""
### Nuance and Limits

**Corrections.** This page previously reported a winner built on an HMM stress probability (S6_hmm_stress, L0) with an out-of-sample Sharpe of {_f(_AUD[('smoothed_fullsample', 0)]['oos_sharpe'])} (HAC t {_f(_AUD[('smoothed_fullsample', 0)]['hac_t'])}). That probability came from a model fitted on the full 2000-2026 sample with forward-backward smoothing, so the value on each day used later data; rebuilt causally, the same rule scores {_f(_AUD[('causal_filtered', 0)]['oos_sharpe'])} at L0 and {_f(_AUD[('causal_filtered', 1)]['oos_sharpe'])} at the L1 floor (file `hmm_lookahead_audit_{_TAG}.json`). The page then reported the rule {W.previous_rule} (out-of-sample Sharpe {W.previous_oos_sharpe}, published {W.previous_tag}), which was the single highest in-sample Sharpe in the grid, at the top edge of the lead grid; it was superseded on 2026-10-17 by the stable-lead-range selection.

**Publication lag.** ICE BofA OAS values appear on FRED about one business day after their value date. Every traded rule therefore reads the spread at least one day back, then trades the next day, so the effective lag is at least two trading days.

**2022.** SPY fell 24.5% between 2022-01-03 and 2022-10-12, during the fastest Federal Reserve tightening in 40 years. Over the same window the HY-IG spread rose from 2.08 to a peak of 4.32 percentage points. In the 2022 sub-period the selected rule's Sharpe was {_f(_SUB.loc['2022 Rates Shock', 'sharpe'])} (SPY {_f(_SUB.loc['2022 Rates Shock', 'bh_sharpe'])}).

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
                "SPY (adjusted) fell 47.5% from its 2000-03-24 peak to its 2002-10-09 trough. "
                "The HY-IG spread was already 3.52 percentage points on 2000-01-03. It widened "
                "through 2000, reaching 6.97 by year-end, and peaked at 8.50 on 2002-10-09, the "
                "same day as the SPY trough. Telecom and technology issuers that had financed "
                "network build-outs with high-yield debt were at the centre of the credit "
                "deterioration."
            ),
            "caption": (
                "The spread widened through 2000 while SPY was falling, and peaked on the day of "
                "the SPY low (2002-10-09)."
            ),
        },
        {
            "slug": "gfc",
            "title": "The Global Financial Crisis (2007-2009)",
            "narrative": (
                "The HY-IG spread reached a low of 1.47 percentage points on 2007-06-01. It rose "
                "to 2.90 by the end of July and 3.10 by the end of August 2007, months before SPY "
                "peaked on 2007-10-09. SPY then fell 55.2% to its 2009-03-09 trough, while the "
                "spread peaked at 15.31 on 2008-12-15. In this episode the spread moved before "
                "the equity peak. This episode is in-sample: the selected rule was chosen on data "
                "that include it (its sub-period result is on the Strategy page)."
            ),
            "caption": (
                "The spread rose from 1.47 (June 2007) to 3.10 (August 2007) before the SPY peak "
                "on 2007-10-09, and peaked at 15.31 in December 2008."
            ),
        },
        {
            "slug": "covid",
            "title": "The COVID Shock (2020)",
            "narrative": (
                "SPY fell 33.7% between 2020-02-19 and 2020-03-23. The HY-IG spread rose from "
                "2.39 percentage points (2020-01-20) to 6.86 on 2020-03-23, the same day as the "
                "SPY low, then eased to about 4.9 by the end of May after the Federal Reserve's "
                "corporate-credit facilities. The spread and SPY moved together rather than one "
                "leading the other. This episode is out-of-sample for the selected rule (its "
                "sub-period result is on the Strategy page)."
            ),
            "caption": (
                "Spread and SPY moved together: both extremes fell on 2020-03-23."
            ),
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 8-element method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "A **Pearson correlation** measures linear co-movement on a -1 to +1 scale. The chart "
        "shows a rolling 252-day correlation between the spread LEVEL and the SAME-DAY SPY "
        "return. The downloadable table adds static correlations of each spread signal with "
        "SPY forward returns at 1 to 252 trading days."
    ),
    question=(
        "How do the spread and SPY returns co-move, and do spread signals correlate with "
        "future SPY returns?"
    ),
    how_to_read=(
        "Values below zero mean that a higher spread coincides with lower same-day SPY "
        "returns. Gray bands are NBER recessions. Forward-return correlations use "
        "overlapping windows, so their iid p-values overstate significance."
    ),
    chart_name="correlations",
    chart_caption=(
        "Rolling 252-day Pearson correlation between the spread level and same-day SPY daily "
        "returns. It is negative in 58% of windows."
    ),
    observation=(
        "The rolling same-day correlation is negative in 58% of windows and changes sign over "
        "time. Static correlations of the spread level with SPY forward returns are small: "
        "-0.033 at 63 trading days, +0.024 at 126 and +0.070 at 252. These are iid p-values "
        "on overlapping windows, which are not reliable."
    ),
    interpretation=(
        "The level of the spread has little linear relationship with future SPY returns at "
        "the horizons tested. The sign at 252 days is positive, the opposite of the "
        "countercyclical hypothesis. The strongest co-movement is same-day (see the "
        "cross-correlation block)."
    ),
    key_message=(
        "Spread-level correlations with SPY forward returns are small (|r| ≤ 0.07) and change "
        "sign across horizons; the clear relationship is same-day, not forward."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "**Granger causality** tests whether past values of one series improve forecasts of "
        "another beyond its own past. The chart tests month-end changes in the HY-IG spread "
        "against the compounded monthly SPY return, at lags 1-12 months. The spread enters "
        "as a monthly change because its level is highly persistent. The downloadable daily "
        "table tests both directions on daily spread changes and SPY returns, at lags 1-5 "
        "days."
    ),
    question=(
        "Do past spread changes help predict SPY returns beyond SPY's own history, and does "
        "the reverse also hold?"
    ),
    how_to_read=(
        "Each bar is the F-statistic at that lag, with its p-value. The dashed line is the 5% "
        "critical value for that lag, which falls as the lag count rises. Vermillion bars "
        "have p < 0.05. These are homoskedastic F-tests; monthly equity returns are "
        "heteroskedastic, so the p-values are approximate."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "Monthly Granger F-tests, spread change → SPY monthly return, 315 months. p < 0.05 at "
        "10 of 12 lags (lags 3-12); lags 1 and 2 are not significant (p = 0.59 and 0.56)."
    ),
    observation=(
        "Monthly: lagged spread changes add predictive content for SPY monthly returns at lags "
        "3 to 12 (p from 0.0007 to 0.0064). Daily: the test rejects in both directions, but "
        "much more strongly from SPY to the spread (F = 166.5 at lag 1) than from the spread "
        "to SPY (F = 4.18, p = 0.041)."
    ),
    interpretation=(
        "At a monthly frequency the test is consistent with the credit-cycle channel: spread "
        "changes carry some information about SPY returns several months later. At a daily "
        "frequency the feedback runs mainly from equities to credit. Neither is causal "
        "identification. The forward-return regressions and local projections, which use "
        "overlap-robust errors, do not find a significant effect of the spread level."
    ),
    key_message=(
        "Monthly spread changes Granger-cause SPY monthly returns at lags 3-12 (p < 0.01). "
        "Daily, SPY returns predict spread changes far more strongly than the reverse."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Cross-Correlation Function (daily changes)",
    method_theory=(
        "The **cross-correlation function** correlates the daily change in the HY-IG spread "
        "with the SPY daily return at lags of -20 to +20 trading days. SPY returns are close "
        "to serially uncorrelated, so they are used as they are; the spread is differenced "
        "because its level is persistent. (An earlier version differenced the returns too, "
        "which creates an artificial negative lag-1 pattern.)"
    ),
    question=(
        "Do spread changes come before SPY moves, after them, or on the same day?"
    ),
    how_to_read=(
        "Negative lags (e.g. -5) pair today's SPY return with the spread change at lag -5 "
        "(spread first). Positive lags pair today's spread change with the SPY "
        "return k days earlier (SPY first). The dashed lines are iid ±95% bands."
    ),
    chart_name="ccf",
    chart_caption=(
        "Daily spread change vs SPY daily return, lags -20 to +20 trading days. Lag 0: r = "
        "-0.444. SPY-first lags +1 and +2: -0.215 and -0.090. Spread-first lags outside the "
        "band: -1 (+0.061), -6 (+0.026), -13 (+0.029)."
    ),
    observation=(
        "The dominant correlation is same-day (r = -0.444). The next largest are at lags +1 "
        "and +2 (-0.215, -0.090), where the SPY return comes first and the spread widens "
        "afterwards. Three spread-first lags fall outside the iid band, all small and "
        "positive (+0.026 to +0.061)."
    ),
    interpretation=(
        "At a daily frequency the spread does not lead SPY. The relationship is same-day, "
        "with the spread catching up to equity moves over the following one to two days. "
        "That matches the daily Granger result and the publication lag: by the time the OAS "
        "value is published, the same-day co-movement has already happened."
    ),
    key_message=(
        "Daily spread changes and SPY returns move together on the same day (r = -0.44); "
        "spread widening tends to follow SPY declines by 1-2 days rather than precede them."
    ),
)


HMM_BLOCK = dict(
    chart_status="ready",
    method_name="Hidden Markov Model (HMM) Regime Analysis",
    method_theory=(
        "A 2-state Gaussian **Hidden Markov Model** is fitted to two daily features: the "
        "change in the HY-IG spread and the VIX level. It is estimated on in-sample data only "
        "(2000-01-05 to 2019-09-30), standardised with in-sample means and standard "
        "deviations. The stress probability on each day is the forward-filtered probability "
        "given data up to that day. The stress state is the one with the higher in-sample "
        "mean spread change. The probability enters the tournament as signal S6_hmm_stress."
    ),
    question=(
        "Do the HMM regimes separate good and bad SPY periods, and is the stress probability "
        "a useful trading signal once it is computed without future data?"
    ),
    how_to_read=(
        "The shaded area is the stress probability (left axis) and the line is SPY (right "
        "axis). Pink bands mark days with probability above 0.5. Gray bands are NBER "
        "recessions."
    ),
    regime_context=(
        "The filtered stress probability is above 0.5 on 45.1% of days (43.5% in-sample, "
        "50.1% out-of-sample). The superseded version of this signal was a full-sample, "
        "forward-backward smoothed probability. On 2020-02-21 it read 0.085, while the "
        "causal filter read 0.001; both read 1.00 on 2020-02-24."
    ),
    chart_name="hmm_regime_probs",
    chart_caption=(
        "Causal HMM stress probability (fit 2000-01 to 2019-09, forward-filtered) and SPY. "
        "Probability above 0.5 on 45% of days."
    ),
    observation=(
        f"Same-day SPY performance differs sharply between the regimes (Story page): regime Sharpe {_CALM[0]:.2f} "
        f"in the calm state and {_STRESS[0]:.2f} in the stress state. As a trading signal, the best "
        f"in-sample-valid HMM rule ({_HMM['strategy'].iloc[0]}, {int(_HMM['lead_days'].iloc[0])}-day lead) has an "
        f"in-sample Sharpe of {_f(_HMM['is_sharpe'].iloc[0])} and an out-of-sample Sharpe of "
        f"{_f(_HMM['oos_sharpe'].iloc[0])}. The previously published HMM rule (P2, L0) scores "
        f"{_f(_AUD[('causal_filtered', 0)]['oos_sharpe'])} at L0 and {_f(_AUD[('causal_filtered', 1)]['oos_sharpe'])} "
        "at the L1 floor when computed causally, against "
        f"{_f(_AUD[('smoothed_fullsample', 0)]['oos_sharpe'])} with the smoothed full-sample probabilities."
    ),
    interpretation=(
        "The HMM describes the regimes well on the same day, but a causal reading of it "
        "does not beat SPY buy-and-hold out of sample. Most of the earlier 1.41 came from "
        "smoothing. In the out-of-sample window, the gap between the smoothed and filtered "
        "probabilities is correlated with the next day's SPY return (r = -0.087), so the "
        "smoothed series contained information about returns that had not yet happened."
    ),
    key_message=(
        f"The causal HMM stress probability separates same-day regimes (regime Sharpe {_CALM[0]:.2f} vs {_STRESS[0]:.2f}), "
        f"but as a traded signal its best in-sample rule has an out-of-sample Sharpe of {_f(_HMM['oos_sharpe'].iloc[0])} "
        f"against SPY's {W.bh_oos_sharpe}. The earlier published HMM result depended on look-ahead smoothing."
    ),
)


REGIME_QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Returns Analysis",
    method_theory=(
        "Month-end HY-IG spreads are split into four equal-count quartiles (Q1 = tightest, "
        "Q4 = widest). The test then measures SPY's return over the **next** 1, 3 and 6 "
        "months after each month-end, so it is a forward test. The Q4 minus Q1 difference "
        "and a joint test that all four quartile means are equal use HAC standard errors. "
        "Quartile breakpoints come from the full-sample distribution: they are descriptive "
        "bins, not a trading rule."
    ),
    question=(
        "Are SPY's subsequent returns lower after wide-spread months than after tight-spread "
        "months, and is the pattern monotonic?"
    ),
    how_to_read=(
        "Bars show annualised next-month SPY returns per quartile (labelled with each "
        "quartile's spread range in percentage points) and the Sharpe ratio. The title gives "
        "the Q4-Q1 difference per month and its HAC t-statistic."
    ),
    regime_context=(
        "The same quartiles look very different on a same-day basis: daily SPY returns run "
        "at 17.1% a year in Q1 and -1.5% a year in Q4. That concurrent gradient reflects "
        "spreads widening while equities fall. It is not a forecast, which is why this block "
        "uses forward returns."
    ),
    chart_name="regime_quartile_returns",
    chart_caption=(
        "SPY next-month return by month-end spread quartile, 315 months. Annualised: Q1 7.9%, "
        "Q2 13.2%, Q3 11.3%, Q4 4.1%. Q4-Q1 = -0.32 pp per month (HAC t -0.40)."
    ),
    observation=(
        "Annualised next-month SPY returns are 7.9% (Q1), 13.2% (Q2), 11.3% (Q3) and 4.1% (Q4). "
        "The Q4-Q1 difference is -0.32 pp a month (HAC t -0.40) at 1 month, -1.18 pp (t -0.59) "
        "at 3 months and -1.65 pp (t -0.44) at 6 months. The joint test of equal means has "
        "p = 0.71, 0.56 and 0.48. The pattern is not monotonic at any horizon."
    ),
    interpretation=(
        "After the widest-spread months SPY's next-month return was lowest on average. The "
        "difference from the tightest quartile is small relative to its uncertainty, and "
        "Q1 is not the best quartile. The forward test does not show a reliable gradient."
    ),
    key_message=(
        "SPY returns after wide-spread months are lower on average (Q4 4.1% vs Q1 7.9% "
        "annualised, next month), but the difference is not significant (HAC t -0.40) and "
        "the quartiles are not monotonic."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Information Flow (transfer-entropy proxy)",
    method_theory=(
        "The chart is a **proxy**, not a full transfer-entropy estimate. Both series are "
        "converted to quintile ranks. Over rolling 504-day windows, stepped monthly, it "
        "measures how much the lagged other series adds to the squared correlation with "
        "today's value, beyond the series' own lag (lag 1 day), in each direction. It "
        "reports no bits and runs no surrogate or significance test."
    ),
    question=(
        "In the proxy measure, is lagged information flow larger from the spread to SPY or "
        "from SPY to the spread?"
    ),
    how_to_read=(
        "Orange: spread → SPY. Blue dashed: SPY → spread. Higher values mean the lagged "
        "series adds more to the squared correlation. Values are small, and without a "
        "significance test the lines are descriptive."
    ),
    chart_name="transfer_entropy",
    chart_caption=(
        "Transfer-entropy proxy over rolling 504-day windows: mean 0.0011 for spread → SPY "
        "and 0.0001 for SPY → spread. No significance test."
    ),
    observation=(
        "Over the sample the proxy averages 0.0011 from the spread to SPY and 0.0001 in the "
        "other direction. Both are small (squared-correlation increments near zero) and the "
        "series is noisy across windows."
    ),
    interpretation=(
        "The proxy shows a slightly larger one-day-lagged increment from the spread to SPY "
        "than the reverse. It runs on quintile ranks and does not test significance, so it "
        "adds little beyond the Granger and cross-correlation results."
    ),
    key_message=(
        "A rank-based transfer-entropy proxy is small in both directions (0.0011 vs 0.0001) "
        "and has no significance test; read it as descriptive."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "**Local projections** (Jordà, 2005) regress the SPY forward return over h trading "
        "days on today's spread level, with the VIX and the 10y-3m Treasury spread as "
        "controls. Horizons are h = 5, 21 and 63 trading days. Forward windows overlap, so "
        "standard errors are Newey-West HAC with maxlags = max(0.75·n^(1/3), h-1): 14, 20 "
        "and 62."
    ),
    question=(
        "After controlling for VIX and the yield curve, does a higher spread level predict "
        "lower SPY returns over the next week, month or quarter?"
    ),
    how_to_read=(
        "The line is the coefficient (return per percentage point of spread) at each "
        "horizon. The band is the 95% HAC confidence interval. A band that excludes zero "
        "would indicate significance."
    ),
    chart_name="local_projections",
    chart_caption=(
        "Local projections of SPY forward returns on the spread level (controls: VIX, 10y-3m), "
        "HAC maxlags ≥ h-1. h = 5d: t -0.99; 21d: t -1.37; 63d: t -1.35. None significant."
    ),
    observation=(
        "The coefficients are negative at all three horizons, -0.0008 (5 days), -0.0032 "
        "(21 days) and -0.0083 (63 days) per percentage point, with p = 0.32, 0.17 and 0.18. "
        "The earlier reading of a significant 63-day effect (p = 0.038) used a HAC lag of 14 "
        "for 63-day overlapping returns. With the lag set to 62, it is not significant."
    ),
    interpretation=(
        "The point estimates have the countercyclical sign, but the data do not distinguish "
        "them from zero once the overlap in forward returns is accounted for."
    ),
    key_message=(
        "The spread level's effect on SPY forward returns is negative but not statistically "
        "significant at 5, 21 or 63 trading days (HAC t between -0.99 and -1.37)."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "**Quantile regression** estimates the slope of the SPY 21-trading-day forward return "
        "on the spread level at quantiles 5% to 95% of the return distribution. The aim is to "
        "see whether the spread shifts the whole distribution, or mainly one tail."
    ),
    question=(
        "Does a wider spread mainly lower the worst outcomes, or does it widen the "
        "distribution in both directions?"
    ),
    how_to_read=(
        "Each point is the slope at that quantile; the band is its 95% interval. Negative "
        "slopes in the low quantiles and positive slopes in the high quantiles of similar "
        "size mean the spread widens the distribution symmetrically."
    ),
    chart_name="quantile_regression",
    chart_caption=(
        "Quantile slopes of the 21-day forward SPY return on the spread level: q05 -0.0117, "
        "q25 -0.0050, q50 +0.0003 (p = 0.27), q75 +0.0047, q95 +0.0118."
    ),
    observation=(
        "The slopes are close to mirror images: -0.0117 at the 5th percentile and +0.0118 at "
        "the 95th, -0.0091 at the 10th and +0.0084 at the 90th. The median slope is about "
        "zero (+0.0003, p = 0.27). Every slope except the median is significant."
    ),
    interpretation=(
        "A wider spread goes with a wider spread of 21-day SPY outcomes in both directions, "
        "a volatility effect, rather than a lower median or a mainly left-tail effect. The "
        "data do not show an asymmetric downside effect."
    ),
    key_message=(
        "Wider HY-IG spreads widen the 21-day SPY return distribution about equally in both "
        "tails (q05 -0.0117, q95 +0.0118); the median effect is near zero."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "Each spread signal is lagged L trading days, for L in the traded grid {1, 5, 21, 63, "
        "126, 252}, and correlated with SPY's next-day return. The grid starts at 1 because "
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
        "Pearson r between each signal lagged L trading days and SPY's next-day return. Stars mark iid p < 0.05."
    ),
    observation=(
        f"The winner's signal ({_SIGCOL}) has r "
        + (", ".join(f"{_LCW[f'L{L}']} at {L} days" for L in _LEADS) if _LCW is not None else "n/a")
        + "."
    ),
    interpretation=(
        "At a daily frequency the spread signals carry very little linear information about "
        "the next day's SPY return at any lead in the grid. Any trading value has to come "
        "from position rules (thresholds, sizing) rather than a linear lead relationship."
    ),
    key_message=(
        "On the daily lead grid (1 to 252 trading days) the spread signals' linear correlation with SPY's "
        "next-day return is small."
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        f"The orange line takes the winning rule ({W.signal_code} / {W.threshold_code} / {W.strategy_family}) "
        "and shows its out-of-sample Sharpe at each lead in the daily grid {1, 5, 21, 63, 126, 252} trading days. "
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
        + ", ".join(f"{int(r.lead_days)}d {_f(r.oos_sharpe)}" for r in _WC.itertuples())
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
        {"label": "Quantile regression (7 quantiles of 21-day forward SPY)",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/quantile_regression.csv"},
        {"label": "Local projections, HAC (3 horizons)",
         "path": f"results/hy_ig_spy/core_models_{_TAG}/local_projections.csv"},
        {"label": "Regime quartile forward tests (1/3/6 months)",
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
        "The tournament combined 15 signals (spread level, z-scores, percentile ranks, rates of change, momentum, "
        "acceleration, the CCC-BB spread, and causal HMM and Markov-switching stress probabilities) with their "
        "threshold labels, 3 strategies (Long/Cash, Signal-Strength, Long/Short; Signal-Strength ignores the "
        "threshold and is declared once per signal) and 6 leads {1, 5, 21, 63, 126, 252} trading days: "
        f"{W.n_candidates} combinations, {W.n_valid} in-sample-valid ({W.n_distinct} distinct position series). Each "
        "window of three neighbouring leads was scored by its lowest in-sample Sharpe; the winner is the highest "
        f"in-sample Sharpe inside the best window: **{W.signal_code} / {W.threshold_code} / {W.strategy_family} / "
        f"L{W.lead}** (stable lead range {W.plateau_range}), in-sample Sharpe {W.is_sharpe} against {W.bh_is_sharpe} "
        f"for SPY over {W.is_start} to {W.is_end}. On the held-out {W.oos_start} to {W.oos_end} window it scored "
        f"{W.oos_sharpe}, against {W.bh_oos_sharpe} for SPY buy-and-hold. The single highest in-sample Sharpe in the "
        f"grid (lead L{W.raw_argmax_lead}, {W.raw_argmax_is_sharpe}) is an isolated-peak sensitivity row, not the "
        "selection rule."
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
        f"What this shows: the rule's Sharpe in each calendar year {int(_WF['test_year'].min())}-{int(_WF['test_year'].max())} "
        "(bars) next to SPY's Sharpe in the same year (markers). Positive in "
        f"{int((_WF['oos_sharpe'] > 0).sum())} of {len(_WF)} years and above SPY in "
        f"{int((_WF['oos_sharpe'] > _WF['bh_sharpe']).sum())} of {len(_WF)}. Years before 2019-10 are in-sample: the "
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
            f"{(_RSH > 0).mean() * 100:.0f}% of windows and ranges from {_f(_RSH.min())} to {_f(_RSH.max())}."
        ),
        "rolling_granger": (
            "How to read it: rolling 504-day Granger test, winner signal -> SPY daily return, lags 1-3, every 5 "
            "trading days; the F shown is the largest of the three lags, so read the p-value line. p < 0.05 in "
            f"{(_RGR < 0.05).mean() * 100:.0f}% of windows."
        ),
        "rolling_correlation": (
            "How to read it: rolling 504-day correlation between the winner signal (lagged by its lead plus one "
            f"execution day) and SPY's daily return. It ranges from {_RCO.min():+.3f} to {_RCO.max():+.3f} and is "
            f"negative in {(_RCO < 0).mean() * 100:.0f}% of windows. For this countercyclical rule the expected sign "
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

2. **Superseded results.** The earlier HMM rule (S6_hmm_stress / P2 / L0, previously published out-of-sample Sharpe {_f(_AUD[('smoothed_fullsample', 0)]['oos_sharpe'])}) relied on full-sample, forward-backward smoothed HMM probabilities (look-ahead); its causal rebuild scores {_f(_AUD[('causal_filtered', 0)]['oos_sharpe'])} at L0 and {_f(_AUD[('causal_filtered', 1)]['oos_sharpe'])} at the L1 lead floor. The rule previously published on {W.previous_tag} ({W.previous_rule}, out-of-sample Sharpe {W.previous_oos_sharpe}) was an isolated top-edge peak.

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
_DATA_SOURCES_MD = """
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
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The primary indicator is the HY-IG credit spread, built daily as the ICE BofA US High "
    "Yield Index option-adjusted spread (FRED: BAMLH0A0HYM2) minus the ICE BofA US Corporate "
    "Index option-adjusted spread (FRED: BAMLC0A0CM), in percentage points. From it the "
    "pipeline derives the level, 252/504-day rolling z-scores, 504/1260-day percentile ranks, "
    "21/63/126-day percent changes, 21/63/252-day changes, an acceleration term and the "
    "CCC-BB quality spread. It also builds two causal regime probabilities: a 2-state "
    "Gaussian HMM on [daily spread change, VIX], and a 2-state Markov-switching model of "
    "the daily spread change. Both are fitted on in-sample data only (to 2019-09-30) and "
    "forward-filtered, so the value on day t uses data up to t only "
    "(scripts/_regime_causal.py). "
    f"The winning signal is `{W.signal_code}` ({_SIG}). The authoritative list of derivatives is rendered from "
    "`signal_scope.json` in the Signal Universe section below."
)

_METHODS_TABLE_MD = """
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
"""

_TOURNAMENT_DESIGN_MD = f"""
| Dimension | Values |
|:----------|:-------|
| **Signals (15)** | spread level; z-score 252d/504d; percentile rank 504d/1260d; % change 21d/63d/126d; change 21d/63d/252d; acceleration; CCC-BB spread; causal HMM stress prob (S6); causal Markov-switching prob (S7) |
| **Thresholds (13 labels)** | T1 in-sample percentile p75/p85/p95; T2 rolling-504d percentile rp75/rp85/rp95; T3 rolling-504d z-score 1.5/2.0/2.5; T4/T5 probability 0.5/0.7 (S6/S7 only) |
| **Strategies (3)** | Long/Cash (P1), Signal-Strength sizing on the trailing-504d range (P2; ignores the threshold, declared once per signal and lead), Long/Short (P3) |
| **Lead times (trading days)** | 1, 5, 21, 63, 126, 252, the standard daily grid floored at 1 for the OAS publication lag; plus a 1-day execution lag |
| **Orientation** | Countercyclical (high signal -> reduce SPY exposure) |
| **Selection** | Stable lead range (D9): each window of three neighbouring leads scored by its lowest in-sample Sharpe on the common window, winner = highest in-sample Sharpe inside the best window, among in-sample-valid rules (>= 1,260 IS days, IS exposure 5-95%, IS turnover < 24/yr, >= 10 IS trades; undefined positions held as cash) |

{W.n_candidates} combinations, {W.n_valid} in-sample-valid ({W.n_distinct} distinct position series). Winner: **{W.signal_code} / {W.threshold_code} / {W.strategy_family} / L{W.lead}**, stable lead range {W.plateau_range}, in-sample Sharpe {W.is_sharpe} (SPY {W.bh_is_sharpe}). Out of sample ({W.oos_start} to {W.oos_end}): Sharpe {W.oos_sharpe} vs SPY {W.bh_oos_sharpe}, annual return {W.oos_ann_return} vs {W.bh_oos_ann_return}, maximum drawdown {W.oos_max_drawdown} vs {W.bh_oos_max_drawdown}. Isolated-peak sensitivity row (not the selection rule): L{W.raw_argmax_lead}, in-sample Sharpe {W.raw_argmax_is_sharpe}.
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
        f"79 months ({W.oos_start} -> {W.oos_end}). In-sample selection uses the common window {W.is_start} -> "
        f"{W.is_end}, which starts when the longest-warm-up eligible candidate has its first return. The dot-com bust "
        "and the GFC are in-sample; COVID 2020 and the 2022 rate shock are out-of-sample. Regime models are fitted on "
        "data up to 2019-09-30 only."
    ),
    plain_english=(
        "This section covers the technical decisions — data sources, sample period, "
        "model specifications, and known limitations. Readers who want to replicate or "
        "challenge the analysis will find what they need here."
    ),
)
