"""10Y-3M Treasury Spread (rebuilt, floored) x SPY pair configuration (Rule APP-PT1).

Pair `t10y3m_rebuilt_spy`, Mode 2. This is the #255 publication-lag-floored
REBUILD of the existing `t10y3m_spy` pair.

================================  READ FIRST  ================================
A PARALLEL ORIGINAL pair `t10y3m_spy` ALREADY EXISTS on the portal, built by
**rekkusuri** with data assembled through **Dana's pipeline**. That original is
left COMPLETELY UNTOUCHED. `t10y3m_rebuilt_spy` is a #255 publication-lag-floored
rebuild: the monthly dataset was reconstructed from the live FRED API (`T10Y3M`,
a DAILY series sampled to month-end) plus yfinance SPY on 2026-10-08 (NOT the
original pair's committed parquet), and the lead axis is floored to L1. The
reader is meant to COMPARE the two side by side: the pre-floor original
(`t10y3m_spy`) vs this floored rebuild (`t10y3m_rebuilt_spy`). The comparison is
the entire point of this pair.
=============================================================================

Evidence status is `found_in_search` (confidence MEDIUM), so headline
performance is a search-phase OOS result with no untouched final exam yet.
Headline values come from `results/t10y3m_rebuilt_spy/winner_summary.json`
(DATE_TAG 20261008).

Framing (binding — HONEST, SKEPTICAL):
  * Winner is `t10y3m_3m_chg` -- the 3-month CHANGE in the 10Y-3M term spread.
    The spread is already expressed in percentage points, so the signal is a
    DIFFERENCE (change in pp), NOT a percent change. T2_roll_p75 threshold,
    rule `gt`, strategy P1_long_cash, PROCYCLICAL, lead L6 (6 months),
    lookback LB60.
  * OOS Sharpe 1.34 vs 0.94 buy-and-hold; annualized return 10.7% vs 15.5%;
    max drawdown -4.7% vs -23.9%; 18 trades; annual turnover 1.95; OOS
    2018-06-30 to 2026-10-31 (101 months).
  * WIN RATE IS 24.7% -- very low. The rule is in cash most of the time and
    wins NOT by a high hit rate but by SITTING OUT drawdowns (its -4.7% max DD
    is a fifth of buy-and-hold's). A low win rate is expected for a mostly-cash
    overlay and is not itself a red flag, but it means the edge is drawdown
    avoidance, not stock-picking skill.
  * The rebuild RE-SELECTS the SAME rule shape as the untouched original
    (chg_3m / T2_roll_p75 / P1_long_cash / L6 / LB60, Sharpe ~1.3 vs ~0.93 B&H).
    That convergence across an independently reconstructed dataset is the most
    useful comparison result -- but convergence of a search is not validation.
  * Formal lead-lag evidence is WEAK: Toda-Yamamoto Granger finds NO significant
    lag in EITHER direction at lags 1-12; the pre-whitened CCF has no
    significant offset; the winning change-signal's linear correlation with
    forward SPY is negative and modest (r approx -0.13 at 3m, -0.20 at 6m). The
    OOS Sharpe therefore rests on threshold/regime timing in a short window, not
    on a clean, significant forward channel.
  * MONTHLY-AXIS CHOICE (binding honesty note): T10Y3M is a DAILY FRED series.
    This rebuild keeps the original pair's canonical MONTHLY axis (sampled to
    month-end), floored at L1 for the ~1-day publication lag. A daily-signal
    treatment would be a different pair; the monthly axis is a deliberate,
    comparable choice, not an oversight.
  * Everything is search-found, confidence MEDIUM, no frozen-rule final exam.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# Shared banner surfaced in Story + Methodology so the reader always knows the
# parallel original exists and that the two are meant to be compared.
_PARALLEL_NOTE = (
    "**Compare with the original `t10y3m_spy` pair.** A parallel original "
    "10Y-3M Treasury Spread x SPY pair (`t10y3m_spy`), built by rekkusuri with "
    "data assembled through Dana's pipeline, already exists on this portal and "
    "is left completely untouched. THIS pair (`t10y3m_rebuilt_spy`) is the #255 "
    "publication-lag-floored REBUILD: the monthly dataset is reconstructed from "
    "the live FRED API (`T10Y3M`, a daily series sampled to month-end) plus "
    "Yahoo Finance SPY, and the lead axis is floored to L1 to respect the "
    "roughly one-day release lag of the daily series. Read the two together: "
    "the original is the pre-floor build, and this rebuild re-runs the search "
    "on an independently reconstructed dataset. Notably, the rebuild lands on "
    "the SAME winning rule shape as the original (the 3-month change in the "
    "spread, a rolling 75th-percentile threshold, a 6-month lead), which is the "
    "central comparison finding -- though a search converging on itself is a "
    "reassurance, not a validation. The whole purpose of this page is the "
    "side-by-side comparison."
)


class StoryConfig:
    PAGE_TITLE = (
        "The Story: Yield-Curve Steepening as a Risk-On SPY Signal "
        "-- a Floored Rebuild"
    )
    PAGE_SUBTITLE = (
        "10-year minus 3-month Treasury spread (FRED T10Y3M, rebuilt from the "
        "live API and sampled to month-end) x S&P 500 (SPY), monthly rules "
        "tested against forward SPY returns. The #255 floored rebuild of the "
        "parallel original t10y3m_spy pair."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.34 OOS, drawdown -4.7%: the rule buys SPY after the 10Y-3M "
        "spread has been steepening for three months -- a floored rebuild that "
        "re-selects the original pair's winner"
    )

    PLAIN_ENGLISH = (
        "The 10Y-3M US Treasury spread is the 10-year US Treasury yield minus "
        "the 3-month US Treasury yield, in percentage points. An inverted "
        "curve, where the spread falls below zero, is a common recession "
        "warning sign. This pair tests whether that rates signal can improve "
        "SPY timing. The winning rule does not trade the level of the curve; it "
        "trades the recent CHANGE in the curve (steepening momentum), lagged "
        "six months. Because the spread is already in percentage points, that "
        "'change' is a simple difference in pp, not a percent change.\n\n"
        + _PARALLEL_NOTE
    )

    WHERE_THIS_FITS = (
        "This is a rates and recession-risk signal for broad U.S. equities -- "
        "and, equally, it is a METHOD-COMPARISON pair. "
        + _PARALLEL_NOTE
        + "\n\nThe honest reading of the rebuilt winner: it beats buy-and-hold "
        "on Sharpe and drawdown in a short out-of-sample window, but its win "
        "rate is only 24.7% (it wins by sitting in cash through drawdowns, not "
        "by a high hit rate), its formal lead-lag tests are weak, and it is "
        "search-found with no final exam. Use it as risk-cycle context, not a "
        "standalone trading system."
    )

    ONE_SENTENCE_THESIS = (
        "SPY tends to avoid its worst drawdowns when the rule sits in cash "
        "unless the 10Y-3M spread has recently steepened, and this floored "
        "rebuild re-selects the original pair's exact rule -- but curve signals "
        "are early, the win rate is low, formal causality is weak, and the "
        "result is search-found, so treat it as risk-cycle context, not precise "
        "market timing."
    )

    KPI_CAPTION = (
        "the search-phase OOS winner uses the 3-month change in the 10Y-3M "
        "spread (a difference in percentage points), a rolling 60-month 75th "
        "percentile threshold, and a 6-month lead. It earns Sharpe 1.34 versus "
        "0.94 for buy-and-hold, with a -4.7% max drawdown versus -23.9%. The "
        "win rate is only 24.7% -- the rule is mostly in cash and wins by "
        "avoiding drawdowns. Selected from 1,435 valid combinations; "
        "found_in_search, confidence medium."
    )

    HERO_TITLE = "10Y-3M Treasury Spread vs the S&P 500 (SPY) -- Rebuilt Data"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the 10Y-3M spread (rebuilt from the live FRED API, "
        "sampled to month-end) is shown with SPY on the same time axis. Shaded "
        "recession bands and pink inversion bands provide historical context. "
        "Values below zero mark yield-curve inversion; rising values mark "
        "steepening. The winning rule trades the 3-month CHANGE in this spread, "
        "not its level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by 10Y-3M Spread Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (inverted or flat curve) to "
        "Q4 (steep curve). In this rebuilt sample Q1 (Sharpe 1.14) and Q2 "
        "(0.97) have STRONGER forward Sharpe than the steepest Q4 bucket "
        "(0.49), so the level relationship is NOT a simple 'steeper is always "
        "better' story -- the same non-monotonic pattern the original pair "
        "found, which is exactly why the winning rule trades the change, not "
        "the level."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning strategy is a **3-month steepening rule**. It looks at the 3-month change in the 10Y-3M Treasury spread (a difference in percentage points, since the spread is already in pp), waits six months before applying the signal, and holds SPY only when the lagged signal is above its rolling 60-month 75th percentile threshold; otherwise it holds cash. Out-of-sample (2018-06 to 2026-10, 101 months), this rule earns a Sharpe ratio of 1.34 versus 0.94 for buy-and-hold, with a maximum drawdown of -4.7% versus -23.9% and an annualized return of 10.7% versus 15.5%.

**Read every one of those numbers as search-found, not validated.** They come from the window used to SELECT the rule, not from an untouched final exam. The evidence status is `found_in_search`, confidence medium.

**The win rate is only 24.7% -- and that is by design, not a defect.** The rule is in cash for most of the out-of-sample window and only takes SPY exposure when the lagged steepening signal clears its threshold. A mostly-cash overlay has a low share of positive months almost mechanically; what it buys is drawdown avoidance. Its -4.7% maximum drawdown is roughly a fifth of buy-and-hold's -23.9%. The edge here is *sitting out losses*, not a high hit rate -- so the lower annualized return (10.7% vs 15.5%) is the price of that protection.

### A Rebuild, Meant to be Compared

This pair is the #255 publication-lag-floored REBUILD of the parallel original `t10y3m_spy` (rekkusuri; data via Dana's pipeline), which is left untouched. The data here is reconstructed from the live FRED API (`T10Y3M`, a daily series sampled to month-end) plus Yahoo Finance SPY, and the lead axis is floored to L1 for the roughly one-day release lag. The striking comparison result is **convergence**: searching an independently rebuilt dataset, the tournament re-selected the SAME rule the original found -- `t10y3m_3m_chg / T2_roll_p75 / P1_long_cash / L6 / LB60`. A search converging on itself across two data builds is reassuring, but it is not a holdout validation.

### The Yield-Curve Hypothesis

The economic idea is that a steepening yield curve usually signals easier future financial conditions and lower near-term recession risk, while a flat or inverted curve warns that restrictive policy may pressure future equity returns. The observed direction here is PROCYCLICAL and consistent with that prior. But the tested result is more nuanced than the textbook story: the winning signal is not the level of the curve, it is the **recent change** in the curve, lagged six months -- the rule responds to steepening momentum, not to whether the curve is high, low, or inverted today.

### Why Timing Is Difficult

Yield-curve signals are often early. The curve can invert long before equities fall, and it can stay inverted while the market rallies. The selected 6-month lead says the historical edge appears after a delay, not immediately. That is why this dashboard treats the signal as recession-risk context and tests many lags rather than claiming a precise market-timing tool.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The curve inverted before the 2001 recession and equity "
                "drawdown, showing why the 10Y-3M spread is watched as an "
                "early recession-risk indicator. This episode predates the "
                "2018+ OOS window, so it informs the story, not the measured "
                "strategy performance."
            ),
            "caption": "Dot-Com: inversion arrived before the recession window (pre-OOS).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The curve inverted in 2006 before the Global Financial "
                "Crisis. The warning was early, which is useful for risk "
                "management but hard for exact trade timing -- and it, too, "
                "predates the OOS window."
            ),
            "caption": "GFC: useful warning, but with a long lead time (pre-OOS).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "The curve briefly inverted before the coronavirus disease "
                "2019 (COVID-19) shock, but the pandemic itself was an "
                "exogenous event. Treat this as a stress-context chart, not "
                "proof that the curve caused the drawdown. COVID falls inside "
                "the OOS window."
            ),
            "caption": "COVID: stress context inside the OOS window, not a causal explanation.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "The 2022-24 inversion was deep and persistent while SPY "
                "eventually recovered. This is the central caveat and the "
                "dominant OOS regime: inversion can warn about macro pressure "
                "without giving precise market entry and exit dates."
            ),
            "caption": "2022-24: inversion stayed cautionary while equities recovered -- the dominant OOS regime.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show the main strength and weakness of yield-curve timing. Before the Dot-Com and Global Financial Crisis recessions, inversion gave an early warning (both predate the OOS window). Around COVID-19, the signal was less clean because the shock was not caused by the rates cycle. During 2022-24, inversion stayed severe while equities recovered, proving that the curve can be directionally useful but tactically early -- and that 2022-24 regime dominates this pair's out-of-sample window.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this rates story survives formal "
        "correlation, lead-lag, regime, and strategy checks -- and it is "
        "candid that the formal tests are weak. The Methodology page spells "
        "out the rebuild, the monthly-axis choice, and the comparison with the "
        "untouched original t10y3m_spy."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether the yield-curve signal and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does a higher 10Y-3M spread (or a larger 3-month change) line up with better future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean higher curve readings line up with stronger future SPY returns; "
        "negative values mean the opposite. The p-value columns in the CSV "
        "show whether the relationship is statistically distinguishable from "
        "noise."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear relationships are modest and mostly "
        "negative-signed. The winning signal, the 3-month change, has Pearson "
        "r about -0.13 at 3 months and -0.20 at 6 months -- statistically "
        "distinguishable from noise but small, and the WRONG sign for a naive "
        "'more steepening is immediately bullish' reading."
    ),
    observation=(
        "The raw change signals correlate negatively with 3-, 6-, and "
        "12-month forward SPY returns in this rebuilt sample (the 3-month "
        "change: r approx -0.13 at 3m, -0.20 at 6m). The raw spread level and "
        "the inversion flag are essentially uncorrelated at these horizons."
    ),
    interpretation=(
        "Linear correlation alone does not justify the pair, and its sign even "
        "cuts against the procyclical winner. That is the central honesty "
        "point: the edge is not a clean linear lead-lag; it is a "
        "threshold/regime effect that the simple correlation cannot capture."
    ),
    key_message="Linear correlations are modest and negative-signed; the tradable feature is a thresholded change, not a clean linear relationship.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Toda-Yamamoto-style Granger causality tests whether past values of "
        "one series improve forecasts of the other after accounting for its "
        "own history."
    ),
    question="Does the 10Y-3M spread lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show F-statistics by monthly lag. The p-values in the source "
        "CSV determine significance; lower p-values indicate stronger evidence "
        "that one series adds forecasting information for the other."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: NO lag clears conventional significance in EITHER "
        "direction (every p-value exceeds 0.14 at lags 1-12), so the page "
        "frames the yield curve as a searched risk overlay rather than a "
        "proven causal forecast."
    ),
    observation=(
        "In the rebuilt data, neither 10Y-3M-to-SPY nor SPY-to-10Y-3M Granger "
        "causality is significant at any lag from 1 to 12; the smallest "
        "forward p-value is about 0.14 (lag 1)."
    ),
    interpretation=(
        "This weak formal lead-lag evidence lowers confidence. It does not "
        "erase the strategy result, but it prevents any causal claim -- the "
        "signal is risk-cycle context, not a proven forecast."
    ),
    key_message="No Granger significance in either direction -- use the signal as risk-cycle evidence, not proof of causality.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the 10Y-3M spread level and "
        "compares subsequent SPY returns across curve regimes."
    ),
    question="Do inverted, normal, and steep-curve regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest or most inverted curve regime; Q4 is the steepest "
        "curve regime. Compare Sharpe and average return across the four "
        "buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Q1 and Q2 have stronger forward Sharpe than the "
        "steepest Q4 bucket in this rebuilt sample -- a non-monotonic pattern."
    ),
    observation=(
        "Q1 inverted/flat has Sharpe 1.14, Q2 has 0.97, Q3 has 0.51, and "
        "Q4 steep has 0.49."
    ),
    interpretation=(
        "The level quartiles do not support a simple monotonic story. This "
        "reinforces why the winning rule uses curve steepening momentum (the "
        "3-month change) rather than the raw level alone -- and it matches the "
        "shape the untouched original pair found."
    ),
    key_message="The level regime is descriptive and non-monotonic; the winning signal is the 3-month change.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters autocorrelation before testing "
        "whether one series tends to move before or after the other."
    ),
    question="At which offsets does the yield-curve signal echo SPY returns?",
    how_to_read=(
        "Bars outside the confidence band mark statistically unusual "
        "lead-lag correlation after filtering persistence from the series."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: no offset clears the confidence band, so the "
        "relationship is not a clean mechanical lead-lag pattern."
    ),
    observation=(
        "After pre-whitening, no lead or lag offset is statistically "
        "significant in the rebuilt data."
    ),
    interpretation=(
        "The yield curve may contain macro timing information, but the timing "
        "is irregular and does not show up as a clean pre-whitened echo. That "
        "matches the economic caveat that inversion and steepening lead market "
        "outcomes by variable amounts."
    ),
    key_message="No significant pre-whitened offset -- the timing link, if any, is not clockwork.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a move in the 10Y-3M spread signal."
    ),
    question="How does SPY respond over time after the 10Y-3M signal moves?",
    how_to_read=(
        "Each point is an estimated SPY response at a forward horizon after "
        "the yield-curve signal moves. Confidence bands show uncertainty "
        "around the estimate; bands crossing zero mean weak evidence."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: the estimated SPY response is NEGATIVE across the "
        "tested horizons. The 3-month and 6-month readings are statistically "
        "meaningful (p approx 0.010 and 0.005), the 12-month is borderline "
        "(p approx 0.03), and the 1-month is not significant. A higher/wider "
        "spread does not lead to immediately stronger SPY returns."
    ),
    observation=(
        "The coefficients are about -0.25% at 1 month (n.s.), -0.75% at 3 "
        "months, -1.16% at 6 months, and -1.25% at 12 months, with the 3- and "
        "6-month readings clearly significant."
    ),
    interpretation=(
        "Local projections support caution. The raw yield-curve response is "
        "not a clean bullish effect, which is why the dashboard separates the "
        "broad economic story from the winning rule: the tradable edge comes "
        "from a lagged, thresholded 3-month change, not from a blanket "
        "assumption that every wider spread is immediately positive for SPY."
    ),
    key_message=(
        "Local projections weaken the simple bullish-steepening story; the "
        "edge is the specific lagged threshold rule, not a uniformly positive "
        "raw response."
    ),
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the signal matters differently in "
        "weak, normal, and strong SPY return environments."
    ),
    question="Does the yield-curve signal behave differently in market tails?",
    how_to_read=(
        "Compare the spread coefficient across return quantiles. A negative "
        "coefficient means a higher spread signal is associated with lower "
        "future SPY return at that part of the return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is negative through most of the "
        "distribution and fades toward zero in the strongest-return tail. Only "
        "the median is clearly significant (p approx 0.013); the lower quartile "
        "is borderline and the upper tail is weak. The signal is not a broad "
        "upside accelerator; it behaves like a state-dependent risk signal."
    ),
    observation=(
        "The estimated coefficient is about -1.5% at the 5th percentile, -1.3% "
        "at the 10th, -0.75% at the 25th, -0.73% at the median (the one "
        "clearly significant point), -0.51% at the 75th, and near zero at the "
        "90th percentile."
    ),
    interpretation=(
        "Quantile regression reinforces the caution from local projections. "
        "The signal does not produce a clean positive payoff across all SPY "
        "return states; it is more relevant when returns are weak to normal "
        "and much less relevant when SPY is already in a strong upside regime "
        "-- consistent with using it as a timing and risk overlay."
    ),
    key_message=(
        "A state-dependent, mostly negative raw relationship; the strategy "
        "depends on the lagged threshold rule, not a uniformly bullish "
        "quantile effect."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Yield-Curve Timing Is Useful but Early -- and the Formal Tests Are Weak",
    "overview": (
        "The evidence supports a medium-confidence rates overlay. The strategy "
        "winner is strong on Sharpe and drawdown in the search-phase OOS "
        "window, and the floored rebuild re-selects the original pair's rule, "
        "but the formal lead-lag tests are not decisive: Granger causality is "
        "insignificant at every lag in both directions, the pre-whitened CCF "
        "has no significant offset, and the winning change-signal's linear "
        "correlation with forward SPY is modest and negative-signed. The level "
        "quartiles are non-monotonic (Q1/Q2 beat Q4)."
    ),
    "plain_english": (
        "This page asks whether the 10Y-3M Treasury spread really helps with "
        "SPY timing. The answer is: partly. The strategy result and the "
        "cross-build convergence are useful, but the statistical evidence says "
        "to treat it as a risk overlay, not a guaranteed forecast -- the "
        "formal causality tests here are weak."
    ),
    "downloads": [
        {"label": "Granger causality by lag", "path": "results/t10y3m_rebuilt_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/t10y3m_rebuilt_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/t10y3m_rebuilt_spy/tournament_results_20261008.csv"},
        {"label": "Subperiod Sharpe checks", "path": "results/t10y3m_rebuilt_spy/subperiod_sharpe.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 1,872 benchmark-excluded strategy combinations, "
        "of which 1,435 passed validity filters. The selected winner is "
        "`t10y3m_3m_chg / T2_roll_p75 / P1_long_cash / L6 / LB60` -- the same "
        "rule shape the untouched original pair selected on its separate data "
        "build. The winner's lead (L6) sits INSIDE the floored grid [1..13], "
        "not at a ceiling."
    ),
    "transition": (
        "**Transition:** the evidence is useful but not absolute, and the "
        "formal lead-lag tests are weak. The Strategy page shows the exact "
        "rule, thresholds, and deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A 10Y-3M Steepening Long/Cash Overlay (Rebuilt)"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 3-month change in the 10Y-3M "
        "Treasury spread (a difference in percentage points), a rolling 75th "
        "percentile threshold, and a 6-month lead. Found_in_search, confidence "
        "medium; wins by drawdown avoidance, not a high hit rate."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 10Y-3M spread had steepened enough six "
        "months earlier; otherwise it holds cash. The idea is that a clear "
        "steepening move can signal improving future conditions, but the lag "
        "keeps the rule from reacting too early. Because it is in cash most of "
        "the time, its win rate is low (24.7%) -- what it delivers is a much "
        "smaller maximum drawdown (-4.7% vs -23.9%), not a higher return."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/t10y3m_rebuilt_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/t10y3m_rebuilt_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/t10y3m_rebuilt_spy/tournament_results_20261008.csv"},
        {"label": "Subperiod Sharpe checks", "path": "results/t10y3m_rebuilt_spy/subperiod_sharpe.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the lagged 3-month change in the 10Y-3M Treasury spread is above its rolling 60-month 75th percentile threshold; otherwise hold cash. The spread is in percentage points, so the "change" is a difference in pp (not a percent change).

If-then form:
- **IF** `t10y3m_3m_chg` from 6 months earlier is above the rolling 75th percentile threshold (latest value approximately 0.31 pp) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2018-06-30 to 2026-10-31, 101 months): Sharpe 1.34 versus 0.94 buy-and-hold; annualized return 10.7% versus 15.5%; maximum drawdown -4.7% versus -23.9%; 18 OOS trades; annual turnover 1.95; win rate 24.7%. The low win rate reflects a mostly-in-cash overlay whose edge is drawdown avoidance.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the 10-year minus 3-month Treasury spread (`T10Y3M`) from the live FRED API -- a DAILY series -- and samples it to month-end observations (this rebuild does NOT reuse the original pair's committed parquet). Second, it computes the 3-month change in that spread, so the signal measures steepening or flattening momentum rather than the raw level; because the spread is already in percentage points, this is a simple difference. Third, it applies a 6-month lag before the SPY allocation is set. Finally, the lagged signal is compared with a rolling 60-month 75th percentile threshold.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return -- low here because the rule is in cash much of the time.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the 10Y-3M Treasury spread (`T10Y3M`) from the live FRED API and sample it at month end.
2. Compute the 3-month change in the spread (a difference in percentage points).
3. Compare the value from 6 months earlier with its rolling 60-month 75th percentile threshold.
4. Hold SPY when the lagged signal is above the threshold; otherwise hold cash.
5. Recheck monthly.

The warning label is central: this is `found_in_search` (confidence medium), NOT confirmed by a holdout final exam; the formal lead-lag tests are weak; and the win rate is low because the rule sits in cash most of the time. Compare it against the untouched original `t10y3m_spy`, which the search re-selected on a separate data build.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility; higher is "
        "better, and negative Sharpe means investors were not compensated for "
        "the risk taken. This chart shows the buy-and-hold SPY Sharpe during "
        "major stress windows used to judge durability. Dot-Com (-0.70), the "
        "Global Financial Crisis (-1.79), COVID (-0.08), and the 2022 rate "
        "hike shock (-0.19) are all negative, so these were hostile market "
        "environments. Durability should be judged by whether the strategy "
        "reduces damage in these periods, not by expecting the signal to make "
        "every crisis profitable -- and only COVID and the 2022 shock fall "
        "inside the pair's 2018+ OOS window."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 10-year minus 3-month "
            "US Treasury spread signal; the target is SPY returns. The rolling "
            "60-month correlation tests whether their linear relationship is "
            "stable through time. For this rebuilt pair the line changes sign "
            "and stays weak on average, so the spread signal should not be read "
            "as a simple always-positive or always-negative linear "
            "relationship with SPY; its usefulness depends on regime and on the "
            "threshold rule used by the strategy."
        ),
        "structural_break": (
            "How to read it: the structural break test asks whether the "
            "spread-SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. The generated proxy reports "
            "a rolling-correlation z-score; larger absolute values point to "
            "larger regime shifts. The practical interpretation is that this "
            "signal should be monitored with rolling thresholds and durability "
            "checks, not treated as one constant relationship from 1993 to "
            "2026."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = False
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across the 1,435 valid "
        "searched strategy combinations, with the selected rule highlighted as "
        "the best search-phase result."
    )

    CAVEATS_MD = """
**Main caveats:**

1. Yield-curve warnings can be early by many months, so a correct macro signal can still be tactically painful.
2. Granger causality is insignificant at every lag in both directions, and the pre-whitened CCF has no significant offset -- this is not a proven causal forecast.
3. The level quartiles are non-monotonic (Q1/Q2 beat Q4); the winning rule uses steepening momentum, not just the spread level.
4. The winning change-signal's linear correlation with forward SPY is modest and NEGATIVE-signed, so the edge rests on threshold/regime timing, not a clean linear lead-lag.
5. The win rate is only 24.7% -- the rule is in cash most of the time and wins by avoiding drawdowns, at the cost of a lower annualized return than buy-and-hold.
6. The result is marked `found_in_search` (confidence medium); it still needs a frozen-rule holdout confirmation.
7. Monthly-axis choice: T10Y3M is a daily series; this rebuild keeps the original pair's monthly axis (floored at L1). A daily-signal treatment would be a different pair.

**What this means:** use this page as a floored rebuild to be COMPARED against the untouched original `t10y3m_spy` -- the convergence of the two searches is the headline, not a validated edge. The honest verdict is a medium-confidence, search-found rates overlay awaiting a frozen-rule final exam.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged 3-month curve-change signal moves above its "
        "rolling 75th percentile threshold, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when the condition no longer holds. "
        "Over the OOS window the rule made 18 such trades (annual turnover "
        "1.95), spending most months in cash."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged t10y3m_3m_chg above rolling p75; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Live FRED API (REBUILT 2026-10-08, NOT the original pair's committed parquet) | `T10Y3M`, 10-year Treasury yield minus 3-month Treasury yield (percentage points) | Daily, sampled to month-end |
| Target | Yahoo Finance | SPY adjusted close / monthly returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "This pair is the #255 publication-lag-floored REBUILD of `t10y3m_spy`. The "
    "10Y-3M spread was reconstructed from the live FRED API (`T10Y3M`, a daily "
    "series) plus Yahoo Finance SPY on 2026-10-08 -- it does NOT reuse the "
    "original pair's committed parquet, so the two pairs can be compared as "
    "independent builds. The raw indicator is the 10-year Treasury yield minus "
    "the 3-month Treasury yield, in percentage points, sampled to month-end. "
    "The pipeline constructs one-month, three-month, six-month, and "
    "twelve-month CHANGES (differences in pp, since the spread is already in "
    "pp), a 60-month rolling z-score, an inversion flag, and a steepening flag. "
    "The winning signal is `t10y3m_3m_chg`, the 3-month change in the spread, "
    "used with a 6-month lead and a rolling 60-month 75th percentile threshold, "
    "traded long/cash (P1, procyclical), lookback LB60. The lead axis is "
    "FLOORED to L1 (grid [1..13]) to respect the roughly one-day publication "
    "lag of the daily series. MONTHLY-AXIS CHOICE: although T10Y3M is native "
    "daily, this rebuild keeps the original pair's canonical monthly axis "
    "(month-end sampling); a daily-signal treatment would be a different pair."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does the curve move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do inverted, normal, and steep-curve regimes behave differently? | Makes the yield-curve story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past curve information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: yield-curve transforms x fixed and rolling thresholds x long/cash, signal-strength, and long/short strategies x procyclical/countercyclical orientations x FLOORED monthly leads (L1-13, floor L1) x lookbacks. The final tournament has 1,872 benchmark-excluded strategy combinations, of which 1,435 pass validity filters. The winning rule is `t10y3m_3m_chg / T2_roll_p75 / P1_long_cash / L6 / LB60`.

**Cross-build convergence (the comparison finding).** Searching this independently reconstructed dataset, the tournament re-selected the SAME rule shape the untouched original `t10y3m_spy` found (same signal, threshold, strategy family, lead, and lookback). That convergence across two separate data builds is the central comparison result -- but a search converging on itself is a reassurance, not a holdout validation.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding because `results/t10y3m_rebuilt_spy/evidence_status.json` marks the pair `found_in_search` (confidence medium). The winner's lead L6 sits inside the floored grid [1..13], not at a ceiling. Formal lead-lag evidence is weak (no significant Granger lag in either direction, no significant pre-whitened CCF offset), reinforcing the medium-confidence label.
"""

_REFERENCES_MD = """
1. Federal Reserve Economic Data (FRED), `T10Y3M`, 10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity.
2. Yahoo Finance, SPY adjusted price history.
3. Estrella, A. and Mishkin, F. S. (1996). "The Yield Curve as a Predictor of U.S. Recessions."
4. Federal Reserve Bank of New York, Yield Curve as a Leading Indicator.
5. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
6. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
7. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "This pair is the #255 publication-lag-floored REBUILD of the parallel "
        "original t10y3m_spy (rekkusuri; data via Dana's pipeline), which is "
        "left untouched; the two are meant to be compared. Monthly sample from "
        "1993-01-31 to 2026-10-31, with out-of-sample window 2018-06-30 to "
        "2026-10-31 (101 months). Total tournament count is 1,872 "
        "benchmark-excluded strategy combinations; 1,435 are valid. The winner "
        "(L6) sits inside the floored lead grid [1..13]. Evidence status: "
        "found_in_search, confidence medium."
    ),
    plain_english=(
        "This page documents how the REBUILT 10Y-3M spread was turned into "
        "testable signals, how the econometric checks were run, and how the "
        "tournament selected the final SPY allocation rule. "
        + _PARALLEL_NOTE
        + " The most important points: the indicator is a daily FRED series "
        "sampled to a monthly axis (a deliberate, comparable choice); the "
        "winning signal is the 3-month change in the spread (a difference in "
        "pp); the level quartiles are non-monotonic; the formal lead-lag tests "
        "are weak; and the result is search-found (confidence medium), awaiting "
        "a frozen-rule holdout test."
    ),
)
