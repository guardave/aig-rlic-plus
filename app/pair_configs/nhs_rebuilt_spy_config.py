"""New Home Sales (rebuilt, floored) x SPY pair configuration (Rule APP-PT1).

Pair `nhs_rebuilt_spy`, Mode 2. This is the #255 publication-lag-floored
REBUILD of the existing `nhs_spy` pair.

================================  READ FIRST  ================================
A PARALLEL ORIGINAL pair `nhs_spy` ALREADY EXISTS on the portal, built and
maintained by **Dana + Vichua4b** on a SEPARATE data pipeline. That original is
left COMPLETELY UNTOUCHED. `nhs_rebuilt_spy` is a #255 publication-lag-floored
rebuild: the data was reconstructed from the live FRED API (HSN1FNSA / HSN1F)
plus yfinance SPY on 2026-10-08 (NOT Dana's committed parquet), and the lead
axis is FLOORED to L2 (floor grid [2..14]) to respect the ~4-week Census
publication lag. The reader is meant to COMPARE the two side by side:
the pre-floor L0 original (`nhs_spy`) vs this floored rebuild
(`nhs_rebuilt_spy`). The comparison is the entire point of this pair.
=============================================================================

Evidence status is `found_in_search`, so headline performance is labelled
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/nhs_rebuilt_spy/winner_summary.json`
(DATE_TAG 20261008).

Framing (binding — WEAK, CAUTIONARY result):
  * Winner is NHS **YoY acceleration** (nhs_yoy_accel_pct: the change in YoY
    home-sales growth, i.e. whether growth is speeding up or slowing),
    T3 z-score ±1.0 band, rule gt, **P3 Long/SHORT**, **countercyclical**,
    lookback LB36, **lead L13 (13 months)**. OOS Sharpe 1.54 vs B&H 0.95,
    max drawdown -13.0% vs -23.9%.
  * The winner sits at **L13 — the very TOP of the floored grid [2..14]**. Per
    the Lead-Grid Frequency Standard Step 4, a grid-ceiling / long-lead winner
    must be ADJUDICATED, not rubber-stamped: it is flagged as likely fragile /
    possibly multiple-testing noise, pending an adjacent-lead durability check.
  * Bootstrap p = 0.069 (NOT significant at 5%) -> confidence LOW.
  * It is P3 LONG/SHORT (shorts SPY in the adverse state) — a more aggressive
    construction than the original's long/cash; the short-side assumption is
    material to the result.
  * Direction is COUNTERCYCLICAL. Housing / NHS is classically a PROCYCLICAL
    early-cycle leading indicator, so a countercyclical acceleration rule at a
    13-month lead is a SURPRISE — a caution flag (likely search artefact), not
    a selling point. The descriptive quartile sort is still cleanly procyclical
    (Q1 Sharpe 0.15 -> Q4 1.50), which deepens, rather than resolves, the
    tension with the countercyclical winner.
  * Every figure is search-found, NOT holdout-validated. In-sample Sharpe 0.67
    vs OOS 1.54 — a large gap. No final exam has been run.
  * The indicator is NSA; all signals are YoY / STL-deseasonalised, raw level
    excluded.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# Shared banner surfaced in Story + Methodology so the reader always knows the
# parallel original exists and that the two are meant to be compared.
_PARALLEL_NOTE = (
    "**Compare with the original `nhs_spy` pair.** A parallel original New "
    "Home Sales x SPY pair (`nhs_spy`), built by Dana and Vichua4b on a "
    "separate data pipeline, already exists on this portal and is left "
    "completely untouched. THIS pair (`nhs_rebuilt_spy`) is the #255 "
    "publication-lag-floored REBUILD: the data is reconstructed from the live "
    "FRED API (HSN1FNSA / HSN1F) plus Yahoo Finance SPY, and the signal lead "
    "is floored to L2 to respect the ~4-week Census release lag. Read the two "
    "together: the original deploys its winner at L0 (coincident, pre-floor), "
    "while this rebuild's winner sits at L13 at the top of the floored grid. "
    "The whole purpose of this page is the side-by-side comparison."
)


class StoryConfig:
    PAGE_TITLE = (
        "The Story: New Home Sales (Rebuilt, Floored) as a Long-Lead SPY "
        "Timing Overlay — a Cautionary Rebuild"
    )
    PAGE_SUBTITLE = (
        "New Home Sales, year-over-year acceleration (FRED HSN1FNSA, not "
        "seasonally adjusted, rebuilt from the live API) x S&P 500 (SPY), "
        "monthly decision rules with a floored (L2) release-lag discipline. "
        "The #255 rebuild of the parallel original nhs_spy pair."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.54 OOS, drawdown -13.0%: a 13-month-lead housing-"
        "acceleration overlay -- but it is a grid-ceiling, countercyclical, "
        "non-significant winner, so read it as a cautionary rebuild, not a "
        "validated edge"
    )

    PLAIN_ENGLISH = (
        "New Home Sales is an early-cycle housing indicator: buyers commit "
        "before construction, so sales lead starts, permits, and the jobs and "
        "spending they drive. The natural prior is PROCYCLICAL -- stronger "
        "home-sales demand should coincide with better equities -- and the "
        "descriptive quartile sort on this rebuilt data does come out that way. "
        "BUT the rule the search picked here does NOT: it is a COUNTERCYCLICAL "
        "rule on home-sales ACCELERATION (whether growth is speeding up or "
        "slowing), lagged 13 months, that goes LONG or SHORT SPY. A "
        "countercyclical rule at a 13-month lead on a procyclical indicator is "
        "a surprise -- the sort of result that usually means the search got "
        "lucky, not that it found a mechanism. Treat this as a cautionary "
        "search result awaiting a durability check, not a forecast.\n\n"
        + _PARALLEL_NOTE
    )

    WHERE_THIS_FITS = (
        "This is a housing leading-indicator signal tested against broad U.S. "
        "equities -- and, more importantly, it is a METHOD-COMPARISON pair. "
        + _PARALLEL_NOTE
        + "\n\nThe honest reading of the rebuilt winner: it beats buy-and-hold "
        "in the short out-of-sample window, but it sits at the very top of the "
        "floored lead grid (L13 of [2..14]), its re-shuffle p-value is 0.069 "
        "(above the 5% bar), its direction contradicts both the economic prior "
        "and this pair's own descriptive quartiles, and it relies on shorting "
        "SPY. Every one of those is a fragility flag."
    )

    ONE_SENTENCE_THESIS = (
        "The rebuilt New-Home-Sales winner improves OOS Sharpe and drawdown "
        "versus buy-and-hold, but it is a grid-ceiling (L13), countercyclical, "
        "long/short, search-found tail with a non-significant bootstrap "
        "p-value (0.069) -- so it is a low-confidence, cautionary rebuild of "
        "the untouched original nhs_spy, to be compared against it and "
        "adjudicated, not deployed."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final "
        "holdout result. The winner was selected from 9,971 valid strategy "
        "combinations (of 14,300), sits at L13 -- the top of the floored lead "
        "grid [2..14] -- with bootstrap p=0.069 (above the 5% bar) and LOW "
        "confidence. Its countercyclical direction contradicts the procyclical "
        "housing prior."
    )

    HERO_TITLE = "New-Home-Sales YoY Growth vs the S&P 500 (SPY) -- Rebuilt Data"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: New Home Sales year-over-year growth (which strips out "
        "the regular spring-vs-winter selling swing, since the raw Census "
        "series is not seasonally adjusted) is shown against SPY on a shared "
        "time axis, with the 0% line marked and the 2008-09 collapse and "
        "2022-23 rate-shock contraction annotated. This series is rebuilt from "
        "the live FRED API, not Dana's committed parquet. The winning rule "
        "trades the ACCELERATION of this growth (its month-on-month change), "
        "lagged 13 months, not the raw level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by New-Home-Sales Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by New Home Sales "
        "YoY-growth quartile. The gradient runs the procyclical way -- Sharpe "
        "RISES monotonically from Q1 (weakest growth) at 0.15 to Q4 (strongest) "
        "at 1.50, and Q1 carries a -51% drawdown versus Q4's -10%. Note the "
        "tension: this concurrent sort is PROCYCLICAL, yet the search winner is "
        "a COUNTERCYCLICAL rule -- a divergence that itself argues for caution."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning rule earns a Sharpe ratio -- return per unit of volatility -- of 1.54 versus 0.95 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves to -13.0% from -23.9%, and annualized return is higher, 24.0% versus 15.6%. The OOS win rate is 72.3% over 28 trades (annual turnover 3.3).

**Read every one of those numbers as search-found, not validated.** They come from the window used to SELECT the rule, not from an untouched final exam. In-sample Sharpe is 0.67 -- less than half the 1.54 OOS figure.

### A Rebuild, Meant to be Compared

This pair is the #255 publication-lag-floored REBUILD of the parallel original `nhs_spy` (Dana + Vichua4b), which is left untouched. The data here is reconstructed from the live FRED API (`HSN1FNSA` NSA, `HSN1F` SAAR) plus Yahoo Finance SPY, and the signal lead is floored to L2 to respect the ~4-week Census release lag. The original deploys its winner at L0 (coincident, pre-floor); this rebuild's winner sits at L13. The intended use is the side-by-side comparison of the two.

### The Winner is a Grid-Ceiling, Countercyclical, Long/Short Rule -- Handle With Care

The winning rule trades New Home Sales **acceleration** -- the month-on-month change in year-over-year growth, i.e. whether home-sales growth is speeding up or slowing -- lagged **13 months**, against a rolling z-score ±1.0 band. It goes LONG SPY when the lagged signal is above the band and SHORT otherwise (a countercyclical orientation). Four things make this a cautionary, not a celebratory, result:

1. **L13 is the very TOP of the floored lead grid [2..14].** Per the Lead-Grid Frequency Standard (Step 4), a grid-ceiling / long-lead winner must be adjudicated -- it is the classic shape of a multiple-testing artefact, and it needs an adjacent-lead durability check before anyone trusts it.
2. **The direction is countercyclical** -- the opposite of the procyclical housing prior AND of this pair's own clean procyclical quartile sort.
3. **It shorts SPY** in the adverse state (P3 long/short), a more aggressive construction than the original's long/cash, with a short-side cost and borrow assumption baked in.
4. **Bootstrap p = 0.069**, above the 5% bar, so it does not clear conventional significance.

<!-- expander: Why surface a result this weak at all? -->
Because the comparison is the point. The original `nhs_spy` found a procyclical long/cash regime rule at L0; this floored rebuild, searching a shifted lead grid on independently reconstructed data, lands on a countercyclical long/short rule at the grid ceiling. That the two disagree -- on direction, on lead, on construction -- is itself the finding: it tells you how much of each "winner" is mechanism and how much is search luck. We report the rebuilt winner honestly, with every fragility flag attached, precisely so it can be weighed against the original.
<!-- /expander -->
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The Dot-Com chart is included as a confirmer for continuity "
                "across the portal's standard episode set. Read it as "
                "contextual background, not the strongest validation case."
            ),
            "caption": (
                "Contextual background; a continuity confirmer, not validation. "
                "The dashed line marks the Nasdaq peak of 10 March 2000 -- SPY's "
                "own month-end high came five months later, so the marker is not "
                "expected to sit on this chart's peak."
            ),
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The GFC is the textbook case for New Home Sales as an early-"
                "cycle signal: sales collapsed roughly 80% from their 2005 peak "
                "and turned down well ahead of the 2008-09 equity bear market. "
                "This is the strongest leading-indicator episode for the pair -- "
                "but note it predates the 2018+ OOS window, so it informs the "
                "story, not the strategy's measured performance."
            ),
            "caption": "GFC: home sales turned down years ahead of the equity bear -- the leading case (pre-OOS).",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During the coronavirus disease 2019 (COVID-19) shock, New Home "
                "Sales spiked on record-low mortgage rates while SPY crashed "
                "and rapidly recovered -- housing demand and the market moved "
                "together in a fast-recovery regime. COVID is the one stress "
                "episode that falls inside the OOS window and is evaluable."
            ),
            "caption": "COVID: sales spiked on low rates as SPY recovered -- the one evaluable OOS stress episode.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022-23 mortgage-rate shock, New Home Sales "
                "contracted sharply as 30-year rates jumped -- the strong, "
                "recent regime that dominates the out-of-sample window and "
                "drives much of the strategy's drawdown avoidance."
            ),
            "caption": (
                "2022-23: rate shock crushed sales -- the dominant OOS regime. "
                "Event markers are dated to the day while the plotted series is "
                "month-end, so the Jan-2022 peak and Oct-2022 low markers each "
                "sit about a month from the visible extremum."
            ),
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history-zoom charts make the leading-indicator character tangible. During the **2008-09 Global Financial Crisis**, new home sales collapsed roughly 80% from their 2005 peak and turned down well ahead of the equity bear market -- the textbook case for housing as an early-cycle signal (but it predates the 2018+ OOS window). During **COVID-19**, sales spiked on record-low mortgage rates as SPY recovered -- the one evaluable OOS stress episode. During the **2022-23 rate shock**, sales contracted sharply as mortgage rates jumped -- the strong, recent regime that dominates the out-of-sample window. The Dot-Com window is a continuity confirmer for the portal's standard episode set.
"""

    TRANSITION_TEXT = (
        "The historical story is a genuine early-cycle-housing one, and the "
        "descriptive quartiles are cleanly procyclical -- but the searched "
        "winner is countercyclical, long-lead, and non-significant. The "
        "Evidence page lays the clean procyclical quartiles alongside the weak "
        "formal causality tests that keep confidence low, and the Methodology "
        "page spells out the rebuild and the comparison with the original "
        "nhs_spy."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
QUANTILE_CHART_NAME = "quantile_coef"
TRANSFER_ENTROPY_CHART_NAME = "transfer_entropy"
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Growth Quartile Gradient",
    method_theory=(
        "Quartile analysis sorts months into four buckets by New Home Sales "
        "YoY-growth and compares subsequent SPY performance. It is descriptive "
        "(concurrent), not the trading rule."
    ),
    question="Do stronger or weaker home-sales growth line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 (weakest home-sales growth) to Q4 (strongest). "
        "A clean rising gradient supports 'stronger housing demand is better "
        "for stocks'; here the gradient does rise cleanly -- which is why the "
        "countercyclical winner is a puzzle."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Sharpe RISES monotonically from Q1 (weakest NHS YoY) "
        "at 0.15 to Q4 (strongest) at 1.50, and Q1 carries a -51% drawdown "
        "versus Q4's -10%."
    ),
    observation=(
        "The gradient is monotonic and procyclical: the strongest-growth "
        "quartile has the best forward Sharpe and the shallowest drawdown."
    ),
    interpretation=(
        "Stronger housing demand coincides with better, calmer equity returns "
        "-- the procyclical prior holds cleanly in the DESCRIPTIVE sort. That "
        "makes the search winner's COUNTERCYCLICAL direction a red flag: a "
        "tradable rule that fights the clean concurrent gradient is more likely "
        "a search artefact than a mechanism."
    ),
    key_message=(
        "Procyclical and monotonic in the sort -- which is exactly why the "
        "countercyclical winner should be treated with suspicion."
    ),
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag (Both Directions)",
    method_theory=(
        "Toda-Yamamoto Granger causality tests whether past values of one "
        "series improve forecasts of the other beyond its own history, in a "
        "form robust to integration order."
    ),
    question="Does New Home Sales growth lead SPY -- and at what horizon?",
    how_to_read=(
        "Bars are F-statistics by monthly lag; bars above the dashed line are "
        "significant at the 5% level. The vermillion bars are home sales "
        "leading SPY; the pale-blue bars are SPY leading home sales."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: the forward direction (NHS to SPY) clears the line "
        "only at lag 11 (p=0.045); the reverse direction (SPY to NHS) is "
        "significant at short lags 1, 2 and 3."
    ),
    observation=(
        "Forward Granger support is weak -- significant only at a single long "
        "lag (11 months); reverse SPY-to-NHS support is present at short lags "
        "(1, 2, 3)."
    ),
    deep_dive_title="Why does a single long lag mean low confidence?",
    deep_dive_content=(
        "A robust leading indicator clears the significance line across a band "
        "of plausible horizons. A single isolated long lag (11 months) is more "
        "consistent with a coincidence in the search than a dependable forward "
        "channel -- especially when the reverse direction (market leading "
        "housing) is significant at short lags. Note too that the winner's "
        "13-month lead does not even coincide with the one significant forward "
        "lag (11)."
    ),
    interpretation=(
        "Forward causality is weak and long-horizon. This is the central "
        "reason confidence is low despite the strong headline Sharpe and the "
        "clean procyclical quartiles."
    ),
    key_message="Forward causality is weak (a single long lag, 11 != the winner's 13); confidence stays low.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation removes each series' own persistence "
        "before checking whether one echoes the other at monthly offsets."
    ),
    question="Is there a clean forward lead-lag echo after removing autocorrelation?",
    how_to_read=(
        "Bars outside the confidence band indicate statistically meaningful "
        "offsets. Negative lags would mark home-sales growth leading SPY."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF does not establish a clean forward lead from "
        "home-sales growth to SPY, consistent with the weak Granger result."
    ),
    observation=(
        "The cross-correlation does not produce a clean forward-lead signal."
    ),
    interpretation=(
        "The CCF reinforces the Granger conclusion: the forward lead from "
        "home-sales growth to SPY is weak."
    ),
    key_message="The cross-correlation check does not support a strong forward lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after a move in home-sales growth."
    ),
    question="Does a home-sales-growth move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward NHS-to-SPY responses are weak and imprecisely "
        "estimated; the confidence bands are wide relative to the point "
        "estimates."
    ),
    observation=(
        "Forward responses are weak across 1, 3, 6, and 12 months."
    ),
    interpretation=(
        "Local projections tell the same weak-forward story as Granger and the "
        "CCF: limited forward predictive content."
    ),
    key_message="Local projections corroborate the weak forward relationship.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression asks whether the relationship differs in weak, "
        "normal, and strong SPY-return environments."
    ),
    question="Is the signal coherent across the return distribution?",
    how_to_read=(
        "Read coefficient estimates across return quantiles. A clean forward "
        "predictor would show a coherent, stable pattern."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: the coefficient varies across return quantiles rather "
        "than holding a single stable sign -- not the profile of a clean, "
        "uniform forward predictor."
    ),
    observation=(
        "The quantile estimates vary across the return distribution."
    ),
    interpretation=(
        "That pattern is consistent with a regime / state effect rather than a "
        "simple linear forward channel from home-sales growth to SPY."
    ),
    key_message="Quantile evidence points to a state effect, not a linear predictor.",
)

TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy is a nonlinear information-flow check that can catch "
        "relationships missed by linear tests."
    ),
    question="Is there nonlinear directed information flow, and in which direction?",
    how_to_read=(
        "Small permutation p-values indicate genuine directed information "
        "flow. Compare the forward and reverse channels."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: neither the forward (NHS to SPY) nor the reverse "
        "channel shows strong nonlinear information flow."
    ),
    observation=(
        "Both directions are weak under the nonlinear information-flow test."
    ),
    interpretation=(
        "Transfer entropy is consistent with the weak linear lead-lag: no "
        "strong directed information flow either way."
    ),
    key_message="Even the nonlinear check finds only weak information flow.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map (Context, NOT the Winner)",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the home-sales growth series into two "
        "latent regimes: a normal expansion state covering most months and a "
        "contraction state that captures outright housing busts. Here the HMM "
        "is descriptive BACKDROP -- unlike the original nhs_spy, the HMM regime "
        "probability is NOT the winning signal in this rebuild."
    ),
    question="When is housing demand in its expansion regime -- and how does that relate to the winner?",
    how_to_read=(
        "The line is the probability that home-sales growth is in the expansion "
        "regime. It sits near 1 for most of the sample and falls toward zero "
        "when housing turns down. The winning rule here does NOT trade this "
        "probability -- it trades the 13-month-lagged YoY ACCELERATION against "
        "a z-score band."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the expansion-regime probability holds near 1 through "
        "expansions and collapses towards zero in the 2007-09 housing bust and "
        "part of the 2022-23 rate shock. In THIS rebuild it is context, not the "
        "traded signal (the original nhs_spy traded the HMM; this pair does "
        "not)."
    ),
    observation=(
        "The HMM cleanly separates normal housing-demand expansions from "
        "outright contractions; the regime probability is near-binary rather "
        "than gradual."
    ),
    interpretation=(
        "A useful backdrop for reading the cycle, but it is not the rebuilt "
        "winner. Comparing the two pairs: the original nhs_spy's winner WAS the "
        "HMM regime probability (procyclical, L0); this rebuild's winner is a "
        "countercyclical acceleration rule (L13). The divergence is a caution "
        "flag about search stability."
    ),
    key_message="The HMM is context here, not the winner -- and it differs from what the original nhs_spy traded.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence: a clean procyclical direction in the sort, but a countercyclical, weakly-caused winner",
    "overview": (
        "The regime quartiles are cleanly monotonic -- stronger home-sales "
        "growth lines up with better, calmer SPY returns, confirming the "
        "procyclical prior. But the formal forward-causality tests are weak: "
        "New Home Sales growth Granger-causes SPY only at a single long lag "
        "(11 months, p=0.045), while SPY leads home sales at short lags "
        "(1, 2, 3). And the searched winner is COUNTERCYCLICAL at a 13-month "
        "lead -- contradicting both the prior and the clean quartile sort. "
        "Supporting checks (local projections, transfer entropy, quantile "
        "regression) corroborate the weak-forward, state-driven reading."
    ),
    "plain_english": (
        "This section asks whether New Home Sales really helps predict future "
        "SPY performance. The descriptive direction is procyclical and clean, "
        "but the formal lead-lag tests are weak AND the search winner points "
        "the opposite (countercyclical) way at a 13-month lead -- so the strong "
        "headline Sharpe is treated as a low-confidence searched result."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/nhs_rebuilt_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/nhs_rebuilt_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/nhs_rebuilt_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/nhs_rebuilt_spy/rolling_correlation_nhs_rebuilt_spy.csv"},
    ],
    "level1": [QUARTILE_BLOCK, GRANGER_BLOCK, HMM_BLOCK, CCF_BLOCK],
    "level1_labels": ["Growth Quartiles", "Granger Causality", "HMM Regimes (Context)", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy"],
    "tournament_intro": (
        "The tournament tested 14,300 benchmark-excluded strategy combinations, "
        "of which 9,971 passed validity filters. The winning rule is the best "
        "of that valid searched set -- and it sits at L13, the top of the "
        "floored lead grid [2..14] -- so its Sharpe advantage must be read with "
        "the search-position and grid-ceiling warnings attached. The median "
        "valid combo scored just 0.79."
    ),
    "transition": (
        "**Transition:** the descriptive direction is procyclical and clean, "
        "but forward causality is weak and the winner is countercyclical at the "
        "grid ceiling. The strategy page shows what the rule actually is: a "
        "search-found Long/SHORT housing-acceleration overlay at a 13-month "
        "lead whose edge is concentrated in a short, episode-heavy OOS window."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A 13-Month-Lead Housing-Acceleration Long/Short Overlay"
    PAGE_SUBTITLE = (
        "A searched timing overlay: better Sharpe, drawdown, and return than "
        "buy-and-hold in the OOS window -- but countercyclical (against the "
        "prior), long/short, at L13 (grid ceiling), found_in_search, with a "
        "non-significant bootstrap p-value. Low confidence."
    )

    PLAIN_ENGLISH = (
        "The rule trades New Home Sales ACCELERATION -- the change in its "
        "year-over-year growth, i.e. whether home-sales growth is speeding up "
        "or slowing -- lagged 13 months, against a rolling z-score ±1.0 band. "
        "When the lagged signal is above the band it holds SPY LONG; otherwise "
        "it SHORTS SPY (a countercyclical orientation). It improved Sharpe and "
        "roughly halved the drawdown in the search-phase OOS window, but it is "
        "a grid-ceiling, countercyclical, long/short winner with p=0.069, so "
        "this is a cautionary overlay, not a forecast."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** take New Home Sales year-over-year ACCELERATION (the month-on-month change in YoY growth), lag it 13 months, and compare it to a rolling z-score ±1.0 band (latest rolling threshold value approximately 12.39). Hold SPY LONG when the lagged signal is above the band; otherwise SHORT SPY. This is a countercyclical, Long/Short construction (strategy family P3), lookback LB36, at a 13-month lead (L13).

If-then form:
- **IF** the 13-month-lagged NHS YoY acceleration is **above** its rolling z-score ±1.0 band (latest value approximately 12.39) -> hold SPY LONG.
- **ELSE** -> SHORT SPY.

Search-phase OOS results (2018-04-30 to 2026-08-31, 101 months, no holdout final exam yet): Sharpe 1.54 vs 0.95 buy-and-hold; annualized return 24.0% vs 15.6%; maximum drawdown -13.0% vs -23.9%; 28 trades; annual turnover 3.3; OOS win rate 72.3%; mean OOS exposure 0.72.

**Three warnings travel with this rule:** (1) L13 is the TOP of the floored lead grid [2..14] -- a grid-ceiling/long-lead winner that the Lead-Grid Standard (Step 4) requires be adjudicated, not rubber-stamped; (2) it SHORTS SPY, so a short-side borrow/cost assumption is embedded; (3) it is countercyclical, against the procyclical housing prior and this pair's own quartile sort.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Census/Federal Reserve monthly new-home-sales release (FRED series `HSN1FNSA`) FROM THE LIVE API and computes its year-over-year growth -- this month's sales versus the same month a year ago. Because the raw series is not seasonally adjusted, the year-over-year change is what strips out the regular spring-vs-winter selling swing. Second, it takes the ACCELERATION of that growth: the month-on-month change in the YoY rate (is growth speeding up or slowing?). Third, it lags the acceleration 13 months (the winning lead), compares it to a rolling z-score ±1.0 band, and converts the comparison into a LONG-or-SHORT SPY position.

This is intentionally simple -- but it is also a search result that contradicts the economic prior. It does not forecast mortgage rates, model the Fed, or claim that housing drives stocks. It asks whether lagged home-sales acceleration times SPY -- and, as the Evidence page is careful to say, the formal forward-causality tests are weak and the direction is countercyclical.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read New Home Sales (`HSN1FNSA`) from the live FRED API at the current vintage (this rebuild does NOT use Dana's committed parquet).
2. Compute year-over-year growth (this deseasonalises the not-seasonally-adjusted series), then its acceleration (the month-on-month change in that YoY rate).
3. Lag the acceleration 13 months (L13) and compute its rolling z-score ±1.0 band.
4. Hold SPY LONG when the lagged signal is above the band; otherwise SHORT SPY.

The warning label is central: this is `found_in_search`, NOT confirmed by a holdout final exam; the winner sits at the top of the floored lead grid (L13 of [2..14]); its bootstrap p-value is 0.069; and its countercyclical direction contradicts the procyclical prior. Compare it against the untouched original `nhs_spy` (L0, procyclical, long/cash) rather than reading it in isolation.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Only COVID 2020 "
        "falls inside the 2018-onward OOS window and is evaluable (Sharpe 1.34, "
        "win rate 73%); the Dot-Com, GFC, and China 2015 episodes predate the "
        "OOS split and are marked insufficient data -- which is why durability "
        "is only conditionally durable."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 9,971 valid "
        "searched combinations, with buy-and-hold (0.95) ABOVE the median "
        "(0.79). The winner's 1.54 Sharpe is the maximum of the search, not a "
        "typical result -- and its bootstrap p-value (0.069) is above the 5% "
        "bar."
    )

    CAVEATS_MD = """
**Why confidence is low (and why the direction is itself a warning):**

1. **Grid-ceiling lead.** The winner sits at L13 -- the very TOP of the floored lead grid [2..14]. Per the Lead-Grid Frequency Standard (Step 4), a grid-ceiling / long-lead winner must be adjudicated, not rubber-stamped: it is the classic shape of a multiple-testing artefact and needs an adjacent-lead durability check.
2. **Countercyclical direction.** New Home Sales is classically a procyclical early-cycle leading indicator, and this pair's own descriptive quartiles are cleanly procyclical (Q1 Sharpe 0.15 -> Q4 1.50). A countercyclical winner fights both -- a surprise to treat as caution, not as an edge.
3. **Weak forward causality.** Toda-Yamamoto Granger finds NHS YoY leads SPY only at a single long lag (11 months, p=0.045) -- which is not even the winner's 13-month lead -- while SPY leads home sales at short lags (1, 2, 3).
4. **Not significant.** The winner is the max of 9,971 valid searched combinations; its bootstrap p-value is 0.069 -- above the 5% bar.
5. **Search-found, large IS/OOS gap.** Marked `found_in_search`; it has NOT been confirmed on an untouched final-exam window. In-sample Sharpe is 0.67 versus OOS 1.54.
6. **Long/Short construction.** It SHORTS SPY in the adverse state (P3), a more aggressive construction than the original's long/cash, embedding a short-side cost/borrow assumption. Mean OOS exposure is 0.72.
7. **Short, episode-heavy OOS.** The OOS window (2018-2026, 101 months) is dominated by the 2022-23 rate shock; COVID is the only evaluable stress episode and durability is only `conditionally_durable` (rolling correlation `moderately_stable`).

**What this means:** use this page as a CAUTIONARY rebuild to be compared against the untouched original `nhs_spy` -- not as proof that New Home Sales forecasts the S&P 500. The honest verdict is a low-confidence, search-found candidate awaiting a frozen-rule final exam and an adjacent-lead durability check.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY to 100% LONG SPY when the 13-month-lagged New-Home-Sales "
        "acceleration crosses above its rolling z-score band, and a flip to "
        "SHORT (-100%) when it falls below. Over the OOS window the rule made "
        "28 such trades (annual turnover 3.3) -- note the SHORT side, which "
        "makes this more aggressive than a long/cash overlay."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-05-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P3_long_short (counter): NHS YoY accel (L13) > rolling z-band; position to +100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Census / Federal Reserve via live FRED API (REBUILT 2026-10-08, NOT Dana's committed parquet) | `HSN1FNSA` New One-Family Houses Sold (thousands, NOT seasonally adjusted); `HSN1F` SAAR used for STL cross-check | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "This pair is the #255 publication-lag-floored REBUILD of `nhs_spy`. The "
    "New Home Sales series was reconstructed from the live FRED API "
    "(`HSN1FNSA` NSA, `HSN1F` SAAR) plus Yahoo Finance SPY on 2026-10-08 -- it "
    "does NOT reuse Dana's committed `nhs_spy` parquet, so the two pairs can be "
    "compared as independent builds. `HSN1FNSA` is NOT seasonally adjusted, so "
    "the raw level and raw month-to-month change are dominated by a fixed "
    "annual seasonal and are EXCLUDED as signals. Signals are deseasonalised: "
    "year-over-year growth (the primary transform; a 12-month difference "
    "cancels the fixed seasonal), its ACCELERATION (the winning transform; the "
    "month-on-month change in YoY growth) and 3-month-average variant, a "
    "statistically seasonally-adjusted (STL) level and its month-over-month and "
    "3-month growth, and a rolling z-score of YoY growth. Both the raw level "
    "and the STL level are non-stationary (augmented Dickey-Fuller does not "
    "reject a unit root) and are excluded from the signal set. The winning "
    "signal is the 13-month-lagged YoY acceleration, evaluated against a "
    "rolling z-score ±1.0 band, traded Long/Short (P3, countercyclical), "
    "lookback LB36. The lead axis is FLOORED to L2 (grid [2..14]) to respect "
    "the ~4-week Census release lag (approximately the fourth Tuesday of the "
    "following month), so the strategy does not use future information. New "
    "home sales are heavily revised; the live FRED API is treated as ground "
    "truth."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger | Do lagged home-sales values improve SPY forecasts -- or the reverse? | Formal lead-lag test, robust to integration order |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM / Markov regimes | Which months are housing expansion vs contraction? | Descriptive regime backdrop (NOT the winner in this rebuild) |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: New-Home-Sales transforms x threshold rules x strategy families x orientations x FLOORED monthly leads (L2-14, floor L2) x lookbacks. The final tournament file has 14,300 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 9,971 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `yoy_accel / T3_zscore_1.0 / P3_long_short (counter) / L13 / LB36`, selected by max OOS Sharpe (ECON-T3 cascade, resolved at step 1). The median valid combo scored 0.79; the winner's 1.54 is the search maximum.

**Grid-ceiling flag (binding).** The winner sits at L13 -- the very top of the floored lead grid [2..14]. Per the Lead-Grid Frequency Standard (Step 4), a grid-ceiling / long-lead winner is adjudicated, not accepted at face value: it is flagged as likely fragile / possibly multiple-testing noise and needs an adjacent-lead durability check.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/nhs_rebuilt_spy/evidence_status.json` marks the pair `found_in_search`. Forward Granger causality is significant only at a single long lag (11, which is not even the winner's 13-month lead), and the winner's direction is countercyclical -- reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau & HUD, New Residential Sales (New One-Family Houses Sold, HSN1FNSA / HSN1F), via FRED.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." (Markov-switching / HMM)
7. Cleveland, R. B. et al. (1990). "STL: A Seasonal-Trend Decomposition Procedure Based on Loess."
8. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "This pair is the #255 publication-lag-floored REBUILD of the parallel "
        "original nhs_spy (Dana + Vichua4b), which is left untouched; the two "
        "are meant to be compared. Out-of-sample window 2018-04-30 to "
        "2026-08-31, 101 monthly observations; in-sample ends 2018-03-31. Total "
        "tournament count is 14,300 benchmark-excluded strategy combinations; "
        "9,971 are valid. The winner sits at L13, the top of the floored lead "
        "grid [2..14]. Evidence status: found_in_search; bootstrap p=0.069."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the REBUILT New Home Sales analysis. "
        + _PARALLEL_NOTE
        + " The most important points: the indicator is not seasonally "
        "adjusted (so every signal is deseasonalised via year-over-year growth "
        "or STL); the descriptive procyclical direction is clean in the "
        "quartiles; but forward causality is weak, the winning rule is "
        "countercyclical at the top of the floored lead grid (L13) with a "
        "non-significant bootstrap p-value, and it still needs a frozen-rule "
        "holdout test and an adjacent-lead durability check."
    ),
)
