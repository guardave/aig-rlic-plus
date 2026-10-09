"""Housing Starts (rebuilt, floored) x SPY pair configuration (Rule APP-PT1).

Pair `housing_starts_rebuilt_spy`, Mode 2. This is the #255 publication-lag-
floored REBUILD of the existing `housing_starts_spy` pair.

================================  READ FIRST  ================================
A PARALLEL ORIGINAL pair `housing_starts_spy` ALREADY EXISTS on the portal,
built by **Vichua4b** on data produced via **Dana's pipeline**. That original is
left COMPLETELY UNTOUCHED. `housing_starts_rebuilt_spy` is a #255 publication-
lag-floored rebuild: the Housing Starts series was reconstructed from the live
FRED API (HOUST) plus Yahoo Finance SPY on 2026-10-08 (NOT the original
committed dataset), and the lead axis is FLOORED (floor L1, grid [1..13]) to
respect the ~mid-month (~17th of M+1) Census/HUD New Residential Construction
publication lag. The reader is meant to COMPARE the two side by side: the
pre-floor original (`housing_starts_spy`, winner = 3-month change,
COUNTERCYCLICAL, long/cash, L2) vs this floored rebuild
(`housing_starts_rebuilt_spy`, winner = binary YoY-contraction flag, long/cash,
L8). The comparison is the entire point of this pair.
=============================================================================

Evidence status is `found_in_search`, so headline performance is labelled
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/housing_starts_rebuilt_spy/winner_summary.json`
(DATE_TAG 20261008).

Framing (binding — WEAK, CAUTIONARY result):
  * Winner is a BINARY YoY-CONTRACTION FLAG (hst_yoy_contraction_flag: 1 when
    Housing Starts year-over-year growth is below zero, else 0), threshold
    T1_fixed_p25 at 0.0, rule gt, strategy family P1 Long/Cash (the pipeline's
    "procyclical" long-when-signal-high construction), lead L8 (8 months),
    lookback N/A. OOS Sharpe 1.45 vs B&H 0.95, max drawdown -8.3% vs -23.9%.
  * The construction is a plain on/off switch: hold SPY LONG when the 8-month-
    lagged contraction flag equals 1 (i.e. starts were contracting year-on-year
    eight months earlier), otherwise sit in CASH. Mean OOS exposure is only
    0.46 and the OOS win rate is just 34.6% — it "wins" by sitting out
    drawdowns, not by being right often. The "procyclical" family label
    describes the long-when-flag-high mechanic, NOT a validated economic story;
    going long eight months after housing weakness is counterintuitive and
    reads as a search artefact.
  * Granger: there is NO forward causality. Toda-Yamamoto finds Housing Starts
    does NOT Granger-cause SPY at any lag; the reverse (SPY -> Housing Starts)
    is significant at ALL lags 1-12. On this rebuilt window housing starts LAG
    the market rather than lead it.
  * Bootstrap p = 0.106 (NOT significant at 5%) -> confidence LOW.
  * The descriptive regime quartiles are NON-MONOTONIC (hump at Q2), not a clean
    procyclical gradient — the direction story does not resolve cleanly either.
  * Every figure is search-found, NOT holdout-validated. In-sample Sharpe 0.23
    vs OOS 1.45 — a very large gap. No final exam has been run.
  * Housing Starts (FRED HOUST) is SEASONALLY ADJUSTED (SAAR); signals are
    stationary growth / z-score / flag transforms, the raw SAAR level excluded.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# Shared banner surfaced in Story + Methodology so the reader always knows the
# parallel original exists and that the two are meant to be compared.
_PARALLEL_NOTE = (
    "**Compare with the original `housing_starts_spy` pair.** A parallel "
    "original Housing Starts x SPY pair (`housing_starts_spy`), built by "
    "Vichua4b on data produced via Dana's pipeline, already exists on this "
    "portal and is left completely untouched. THIS pair "
    "(`housing_starts_rebuilt_spy`) is the #255 publication-lag-floored REBUILD: "
    "the Housing Starts series is reconstructed from the live FRED API (HOUST) "
    "plus Yahoo Finance SPY, and the signal lead is floored (floor L1, grid "
    "[1..13]) to respect the ~mid-month Census release lag. Read the two "
    "together: the original's winner is a 3-month-change, COUNTERCYCLICAL, "
    "long/cash rule at L2; this rebuild's winner is a binary YoY-contraction "
    "flag, long/cash, at L8. The whole purpose of this page is the side-by-side "
    "comparison of a pre-floor build against a floored rebuild."
)


class StoryConfig:
    PAGE_TITLE = (
        "The Story: Housing Starts (Rebuilt, Floored) as an SPY Timing Overlay "
        "— a Cautionary Rebuild"
    )
    PAGE_SUBTITLE = (
        "Housing Starts, year-over-year growth and a binary contraction flag "
        "(FRED HOUST, seasonally adjusted SAAR, rebuilt from the live API) x "
        "S&P 500 (SPY), monthly decision rules with a floored (L1) release-lag "
        "discipline. The #255 rebuild of the parallel original "
        "housing_starts_spy pair."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.45 OOS, drawdown -8.3%: an 8-month-lead binary "
        "housing-contraction switch -- but it has no forward causality, a "
        "non-significant bootstrap p-value, and a 34.6% win rate, so read it as "
        "a cautionary rebuild, not a validated edge"
    )

    PLAIN_ENGLISH = (
        "Housing Starts is an early-cycle construction indicator: builders break "
        "ground before the jobs, materials, and spending that follow, so starts "
        "are classically read as a PROCYCLICAL leading signal. BUT the rule the "
        "search picked here is not a clean growth rule at all: it is a BINARY "
        "on/off switch built on a CONTRACTION FLAG (1 when year-over-year starts "
        "growth is negative), lagged 8 months. It holds SPY only when starts "
        "were contracting eight months earlier, and sits in cash the rest of the "
        "time. It beats buy-and-hold on Sharpe and drawdown in the short "
        "out-of-sample window -- but it is right on only 34.6% of its trades "
        "(it 'wins' by sitting out losses), the formal causality test finds "
        "housing starts do NOT lead the market on this data, and the re-shuffle "
        "test is not significant. Treat this as a search result awaiting a "
        "durability check, not a forecast.\n\n"
        + _PARALLEL_NOTE
    )

    WHERE_THIS_FITS = (
        "This is a housing leading-indicator signal tested against broad U.S. "
        "equities -- and, more importantly, it is a METHOD-COMPARISON pair. "
        + _PARALLEL_NOTE
        + "\n\nThe honest reading of the rebuilt winner: it beats buy-and-hold "
        "on Sharpe and drawdown in the short out-of-sample window, but forward "
        "Granger causality is absent (starts do not lead SPY here; the market "
        "leads starts), its re-shuffle p-value is 0.106 (above the 5% bar), its "
        "win rate is only 34.6%, and it is a binary flag chosen out of a "
        "14,300-combination search. Every one of those is a fragility flag."
    )

    ONE_SENTENCE_THESIS = (
        "The rebuilt Housing-Starts winner improves OOS Sharpe and drawdown "
        "versus buy-and-hold, but it is a binary contraction-flag switch at an "
        "8-month lead with NO forward causality, a non-significant bootstrap "
        "p-value (0.106), and a 34.6% win rate -- so it is a low-confidence, "
        "cautionary rebuild of the untouched original housing_starts_spy, to be "
        "compared against it and adjudicated, not deployed."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final holdout "
        "result. The winner was selected from 10,378 valid strategy "
        "combinations (of 14,300), is a binary YoY-contraction flag at L8, with "
        "bootstrap p=0.106 (above the 5% bar) and LOW confidence. Forward "
        "Granger causality is ABSENT, and the OOS win rate is only 34.6% -- the "
        "edge is drawdown avoidance, not forecasting accuracy."
    )

    HERO_TITLE = "Housing Starts YoY Growth vs the S&P 500 (SPY) -- Rebuilt Data"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: Housing Starts year-over-year growth (FRED HOUST, "
        "seasonally adjusted at source) is shown against SPY on a shared time "
        "axis, with the 0% line marked and the 2006-09 collapse and 2022-23 "
        "rate-shock contraction annotated. This series is rebuilt from the live "
        "FRED API, not the original committed dataset. The winning rule trades a "
        "BINARY flag derived from this growth -- whether YoY growth is below "
        "zero -- lagged 8 months, not the raw level or the growth rate itself."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Housing-Starts Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by Housing Starts "
        "YoY-growth quartile. The gradient is NON-MONOTONIC -- Sharpe peaks at "
        "Q2 (1.07) rather than rising cleanly from Q1 (0.64) to Q4 (0.67), and "
        "Q1 (weakest growth) carries a -51% drawdown. This hump is NOT the clean "
        "procyclical gradient a textbook leading indicator would show, which is "
        "one more reason to treat the searched winner with caution."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning rule earns a Sharpe ratio -- return per unit of volatility -- of 1.45 versus 0.95 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves sharply to -8.3% from -23.9%. Its annualized return is actually slightly LOWER, 13.2% versus 15.6%: the Sharpe gain comes from much lower volatility and drawdown, not from higher returns. The OOS win rate is just 34.6% over 30 trades (annual turnover 3.6), and mean OOS exposure is 0.46 -- the rule is in cash more than half the time.

**Read every one of those numbers as search-found, not validated.** They come from the window used to SELECT the rule, not from an untouched final exam. In-sample Sharpe is 0.23 -- less than a sixth of the 1.45 OOS figure.

### A Rebuild, Meant to be Compared

This pair is the #255 publication-lag-floored REBUILD of the parallel original `housing_starts_spy` (built by Vichua4b, data via Dana's pipeline), which is left untouched. The data here is reconstructed from the live FRED API (`HOUST`) plus Yahoo Finance SPY, and the lead axis is floored (floor L1, grid [1..13]) to respect the ~mid-month (~17th of M+1) Census release lag. The original deploys a 3-month-change, countercyclical, long/cash rule at L2; this rebuild's winner is a binary YoY-contraction flag, long/cash, at L8. The intended use is the side-by-side comparison of the two.

### The Winner is a Binary Contraction-Flag Switch -- Handle With Care

The winning rule trades a **binary 0/1 flag** -- is Housing Starts year-over-year growth below zero? -- lagged **8 months**. It holds SPY LONG when the 8-month-lagged flag equals 1 (starts were contracting a year-on-year eight months earlier) and sits in CASH otherwise. Four things make this a cautionary, not a celebratory, result:

1. **No forward causality.** Toda-Yamamoto Granger finds Housing Starts does NOT Granger-cause SPY at any lag 1-12, while the reverse (SPY -> starts) is significant at ALL twelve lags. On this rebuilt window the market LEADS housing, not the other way round.
2. **A 34.6% win rate.** The rule is right on barely a third of its trades; its Sharpe edge is drawdown avoidance (sitting in cash through bad stretches), not forecasting accuracy.
3. **A binary on/off construction at a long lead.** An 8-month-lagged contraction flag is a very coarse signal, and going long eight months after housing weakness is economically counterintuitive -- the classic shape of a search artefact.
4. **Bootstrap p = 0.106**, above the 5% bar, so it does not clear conventional significance.

<!-- expander: Why surface a result this weak at all? -->
Because the comparison is the point. The original `housing_starts_spy` found a 3-month-change, countercyclical long/cash rule at L2; this floored rebuild, searching a shifted lead grid on independently reconstructed data, lands on a binary contraction-flag rule at L8. That the two disagree -- on signal, on lead, on the direction story -- is itself the finding: it tells you how much of each "winner" is mechanism and how much is search luck. We report the rebuilt winner honestly, with every fragility flag attached, precisely so it can be weighed against the original.
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
                "The GFC is the textbook case for Housing Starts as an early-"
                "cycle signal: starts peaked in early 2006 and fell roughly 75% "
                "into 2009, turning down well ahead of the 2008-09 equity bear "
                "market. This is the strongest leading-indicator episode for the "
                "indicator -- but note it predates the 2018+ OOS window, so it "
                "informs the story, not the strategy's measured performance."
            ),
            "caption": "GFC: starts turned down years ahead of the equity bear -- the leading case (pre-OOS).",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During the coronavirus disease 2019 (COVID-19) shock, Housing "
                "Starts dipped and rebounded fast on record-low mortgage rates "
                "while SPY crashed and rapidly recovered. COVID is the one stress "
                "episode that falls inside the OOS window and is evaluable."
            ),
            "caption": "COVID: starts dipped and rebounded on low rates as SPY recovered -- the one evaluable OOS stress episode.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022-23 mortgage-rate shock, Housing Starts "
                "contracted sharply as 30-year rates jumped -- the strong, "
                "recent regime that dominates the out-of-sample window and "
                "drives much of the strategy's drawdown avoidance."
            ),
            "caption": (
                "2022-23: rate shock crushed starts -- the dominant OOS regime. "
                "Event markers are dated to the day while the plotted series is "
                "month-end, so the peak and trough markers each sit about a "
                "month from the visible extremum."
            ),
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history-zoom charts make the leading-indicator character tangible. During the **2008-09 Global Financial Crisis**, housing starts peaked in early 2006 and fell roughly 75% into 2009, turning down well ahead of the equity bear market -- the textbook case for housing as an early-cycle signal (but it predates the 2018+ OOS window). During **COVID-19**, starts dipped and rebounded fast on record-low mortgage rates as SPY recovered -- the one evaluable OOS stress episode. During the **2022-23 rate shock**, starts contracted sharply as mortgage rates jumped -- the strong, recent regime that dominates the out-of-sample window. The Dot-Com window is a continuity confirmer for the portal's standard episode set.
"""

    TRANSITION_TEXT = (
        "The historical story is a genuine early-cycle-housing one, but the "
        "descriptive quartiles are non-monotonic and the searched winner is a "
        "binary contraction flag with no forward causality. The Evidence page "
        "lays the quartile hump alongside the formal causality tests that keep "
        "confidence low, and the Methodology page spells out the rebuild and "
        "the comparison with the original housing_starts_spy."
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
        "Quartile analysis sorts months into four buckets by Housing Starts "
        "YoY-growth and compares subsequent SPY performance. It is descriptive "
        "(concurrent), not the trading rule."
    ),
    question="Do stronger or weaker housing-starts growth line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 (weakest starts growth) to Q4 (strongest). A "
        "clean rising gradient would support 'stronger construction is better "
        "for stocks'; here the gradient is non-monotonic, peaking at Q2."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Sharpe peaks at Q2 (1.07) rather than rising cleanly "
        "from Q1 (0.64) to Q4 (0.67); Q1 (weakest growth) carries a -51% "
        "drawdown. A hump, not a clean procyclical gradient."
    ),
    observation=(
        "The gradient is non-monotonic: Q2 has the best forward Sharpe, and the "
        "extremes (Q1 weakest, Q4 strongest) are both weaker."
    ),
    interpretation=(
        "The clean 'stronger housing = better stocks' prior does NOT hold "
        "tidily in the descriptive sort. A hump pattern is consistent with a "
        "state/regime effect rather than a monotone relationship -- and it "
        "offers no clean endorsement of the searched binary-flag winner."
    ),
    key_message=(
        "Non-monotonic (hump at Q2) -- not the clean procyclical gradient a "
        "textbook leading indicator would show."
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
    question="Does Housing Starts growth lead SPY -- and at what horizon?",
    how_to_read=(
        "Bars are F-statistics by monthly lag; bars above the dashed line are "
        "significant at the 5% level. The vermillion bars are housing starts "
        "leading SPY; the pale-blue bars are SPY leading housing starts."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: the forward direction (Housing Starts to SPY) does "
        "NOT clear the line at ANY lag; the reverse direction (SPY to Housing "
        "Starts) is significant at ALL twelve lags."
    ),
    observation=(
        "Forward Granger support is ABSENT at every lag 1-12; the reverse "
        "channel (SPY leads starts) is significant at all twelve lags."
    ),
    deep_dive_title="Why does the absence of forward causality mean low confidence?",
    deep_dive_content=(
        "A robust leading indicator clears the significance line across a band "
        "of plausible forward horizons. Here NONE clear it, while the reverse "
        "direction (the market leading housing) is significant at every lag. "
        "That reverse-only pattern means equities respond to the broader cycle "
        "and housing follows -- so an 8-month-lagged housing flag that appears "
        "to 'predict' SPY is best read as a search-found counter-signal, not a "
        "dependable forward forecaster."
    ),
    interpretation=(
        "Forward causality is absent and the reverse dominates. This is the "
        "central reason confidence is low despite the strong headline Sharpe."
    ),
    key_message="No forward causality (starts lag the market here); confidence stays low.",
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
        "offsets. Negative lags would mark housing-starts growth leading SPY."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF does not establish a clean forward lead from "
        "housing-starts growth to SPY, consistent with the absent forward "
        "Granger result."
    ),
    observation=(
        "The cross-correlation does not produce a clean forward-lead signal."
    ),
    interpretation=(
        "The CCF reinforces the Granger conclusion: the forward lead from "
        "housing-starts growth to SPY is weak or absent."
    ),
    key_message="The cross-correlation check does not support a forward lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after a move in housing-starts growth."
    ),
    question="Does a housing-starts-growth move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward housing-starts-to-SPY responses are weak and "
        "imprecisely estimated; the confidence bands are wide relative to the "
        "point estimates."
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
        "simple linear forward channel from housing-starts growth to SPY."
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
        "What this shows: neither the forward (Housing Starts to SPY) nor the "
        "reverse channel shows strong nonlinear information flow."
    ),
    observation=(
        "Both directions are weak under the nonlinear information-flow test."
    ),
    interpretation=(
        "Transfer entropy is consistent with the weak/absent linear lead-lag: "
        "no strong directed information flow either way."
    ),
    key_message="Even the nonlinear check finds only weak information flow.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map (Context, NOT the Winner)",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the housing-starts growth series into "
        "two latent regimes: a calm state covering most months and a high-"
        "variance state that captures housing turning points. Here the HMM is "
        "descriptive BACKDROP -- the HMM regime probability is NOT the winning "
        "signal in this rebuild."
    ),
    question="When is housing starts in its high-variance regime -- and how does that relate to the winner?",
    how_to_read=(
        "The line is the probability that housing-starts growth is in the "
        "high-variance regime. It spikes around housing turning points. The "
        "winning rule here does NOT trade this probability -- it trades the "
        "8-month-lagged binary YoY-contraction flag."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the high-variance-regime probability spikes in the "
        "2007-09 housing bust, COVID, and the 2022-23 rate shock. In THIS "
        "rebuild it is context, not the traded signal -- the winner is the "
        "binary YoY-contraction flag (hst_yoy_contraction_flag)."
    ),
    observation=(
        "The HMM separates calm housing-growth regimes from high-variance "
        "turning points; the high-variance state is concentrated around busts."
    ),
    interpretation=(
        "A useful backdrop for reading the cycle, but it is not the rebuilt "
        "winner. The winner is a simpler binary contraction flag; the HMM is "
        "shown only to place the cycle context around it."
    ),
    key_message="The HMM is context here, not the winner -- the winner is the binary contraction flag.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence: a non-monotonic sort and NO forward causality behind a search-found binary-flag winner",
    "overview": (
        "The regime quartiles are non-monotonic -- Sharpe peaks at Q2 rather "
        "than rising cleanly from Q1 to Q4 -- so the descriptive direction does "
        "not resolve into a clean procyclical gradient. The formal forward-"
        "causality tests are worse: Housing Starts does NOT Granger-cause SPY at "
        "ANY lag 1-12, while SPY leads housing starts at ALL twelve lags. The "
        "searched winner is a binary YoY-contraction flag at an 8-month lead -- "
        "a coarse, counterintuitive construction. Supporting checks (local "
        "projections, transfer entropy, quantile regression) corroborate the "
        "weak/absent-forward, state-driven reading."
    ),
    "plain_english": (
        "This section asks whether Housing Starts really helps predict future "
        "SPY performance. The descriptive sort is non-monotonic, and the formal "
        "lead-lag tests find starts do NOT lead the market (the market leads "
        "starts) -- so the strong headline Sharpe is treated as a low-confidence "
        "searched result, not evidence of a forecasting signal."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/housing_starts_rebuilt_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/housing_starts_rebuilt_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/housing_starts_rebuilt_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/housing_starts_rebuilt_spy/rolling_correlation_housing_starts_rebuilt_spy.csv"},
    ],
    "level1": [QUARTILE_BLOCK, GRANGER_BLOCK, HMM_BLOCK, CCF_BLOCK],
    "level1_labels": ["Growth Quartiles", "Granger Causality", "HMM Regimes (Context)", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy"],
    "tournament_intro": (
        "The tournament tested 14,300 benchmark-excluded strategy combinations, "
        "of which 10,378 passed validity filters. The winning rule is the best "
        "of that valid searched set -- a binary YoY-contraction flag at L8 -- so "
        "its Sharpe advantage must be read with the search-selection and "
        "absent-forward-causality warnings attached. The median valid combo "
        "scored just 0.78, below buy-and-hold's 0.95."
    ),
    "transition": (
        "**Transition:** the descriptive direction is a non-monotonic hump and "
        "forward causality is absent. The strategy page shows what the rule "
        "actually is: a search-found binary-flag Long/Cash overlay at an "
        "8-month lead whose edge is drawdown avoidance in a short, episode-heavy "
        "OOS window, not forecasting accuracy."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: An 8-Month-Lead Binary Housing-Contraction Long/Cash Switch"
    PAGE_SUBTITLE = (
        "A searched timing overlay: better Sharpe and drawdown than buy-and-hold "
        "in the OOS window -- but a binary contraction flag at L8, with NO "
        "forward causality, a 34.6% win rate, found_in_search, and a "
        "non-significant bootstrap p-value. Low confidence."
    )

    PLAIN_ENGLISH = (
        "The rule trades a binary 0/1 flag -- is Housing Starts year-over-year "
        "growth below zero? -- lagged 8 months. When the lagged flag equals 1 "
        "(starts were contracting a year earlier, eight months ago) it holds "
        "SPY LONG; otherwise it sits in CASH. It improved Sharpe and roughly "
        "cut the drawdown by two-thirds in the search-phase OOS window, but it "
        "is right on only 34.6% of trades (it wins by sitting out losses), "
        "housing starts do NOT lead the market on this data, and the bootstrap "
        "p-value is 0.106 -- so this is a cautionary overlay, not a forecast."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** take the binary Housing Starts YoY-contraction flag (1 when year-over-year starts growth is below zero, else 0), lag it 8 months, and compare it to a fixed threshold of 0.0 with a greater-than rule. Hold SPY LONG when the lagged flag equals 1; otherwise sit in CASH. This is a binary on/off switch, strategy family P1 Long/Cash (the pipeline's "procyclical" long-when-signal-high construction), no lookback, at an 8-month lead (L8).

If-then form:
- **IF** the 8-month-lagged Housing Starts YoY-contraction flag **equals 1** (starts were contracting year-on-year eight months earlier) -> hold SPY LONG.
- **ELSE** -> hold CASH.

Search-phase OOS results (2018-04-30 to 2026-08-31, 101 months, no holdout final exam yet): Sharpe 1.45 vs 0.95 buy-and-hold; annualized return 13.2% vs 15.6% (LOWER return, higher Sharpe via lower vol); maximum drawdown -8.3% vs -23.9%; 30 trades; annual turnover 3.6; OOS win rate 34.6%; mean OOS exposure 0.46.

**Three warnings travel with this rule:** (1) there is NO forward Granger causality -- starts do not lead SPY on this window, the market leads starts; (2) the win rate is only 34.6% -- the edge is drawdown avoidance, not forecasting; (3) it is a coarse binary flag at an 8-month lead chosen out of a 14,300-combination search, with bootstrap p=0.106 (above the 5% bar).
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Census/HUD monthly Housing Starts release (FRED series `HOUST`, seasonally adjusted at an annual rate) FROM THE LIVE API and computes its year-over-year growth -- this month's starts versus the same month a year ago. Because `HOUST` is already seasonally adjusted, no deseasonalisation is applied; year-over-year growth is used as the headline transform and month-on-month change is a valid input. Second, it derives a BINARY contraction flag: 1 when that YoY growth is below zero, else 0. Third, it lags the flag 8 months (the winning lead), compares it to a fixed 0.0 threshold, and converts the comparison into a LONG-or-CASH SPY position.

This is intentionally simple -- but it is also a search result that fails the forward-causality test. It does not forecast mortgage rates, model the Fed, or claim that housing drives stocks. It asks whether a lagged housing-contraction flag times SPY -- and, as the Evidence page is careful to say, the formal forward-causality tests find no forward lead at all.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Housing Starts (`HOUST`) from the live FRED API at the current vintage (this rebuild does NOT reuse the original committed dataset).
2. Compute year-over-year growth, then set the contraction flag to 1 when that growth is below zero, else 0.
3. Lag the flag 8 months (L8) and compare it to the fixed 0.0 threshold (greater-than rule).
4. Hold SPY LONG when the lagged flag equals 1; otherwise hold CASH.

The warning label is central: this is `found_in_search`, NOT confirmed by a holdout final exam; forward Granger causality is absent; the OOS win rate is only 34.6%; and its bootstrap p-value is 0.106. Compare it against the untouched original `housing_starts_spy` (3-month change, countercyclical, long/cash, L2) rather than reading it in isolation.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Only COVID 2020 "
        "falls inside the 2018-onward OOS window and is evaluable (Sharpe ~1.04, "
        "win rate low); the Dot-Com, GFC, and China 2015 episodes predate the "
        "OOS split and are marked insufficient data -- which is why durability "
        "is only conditionally durable."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 10,378 valid "
        "searched combinations, with buy-and-hold (0.95) ABOVE the median "
        "(0.78). The winner's 1.45 Sharpe is the maximum of the search, not a "
        "typical result -- and its bootstrap p-value (0.106) is above the 5% "
        "bar."
    )

    CAVEATS_MD = """
**Why confidence is low:**

1. **No forward causality.** Toda-Yamamoto Granger finds Housing Starts does NOT Granger-cause SPY at any lag 1-12, while the reverse (SPY -> starts) is significant at ALL twelve lags. On this rebuilt window the market leads housing, not the other way round -- the single most important caveat.
2. **A 34.6% win rate.** The rule is right on barely a third of its trades. Its Sharpe edge comes from drawdown avoidance (mean OOS exposure 0.46 -- in cash more than half the time), not forecasting accuracy.
3. **Non-monotonic descriptive sort.** The regime quartiles hump at Q2 (Sharpe 1.07) rather than rising cleanly from Q1 (0.64) to Q4 (0.67) -- no clean procyclical gradient to anchor the signal.
4. **Not significant.** The winner is the max of 10,378 valid searched combinations; its bootstrap p-value is 0.106 -- above the 5% bar.
5. **Search-found, huge IS/OOS gap.** Marked `found_in_search`; it has NOT been confirmed on an untouched final-exam window. In-sample Sharpe is 0.23 versus OOS 1.45 -- a more than sixfold gap.
6. **Coarse binary construction at a long lead.** An 8-month-lagged 0/1 contraction flag is a very coarse signal, and going long eight months after housing weakness is economically counterintuitive -- the classic shape of a search artefact.
7. **Short, episode-heavy OOS.** The OOS window (2018-2026, 101 months) is dominated by the 2022-23 rate shock; COVID is the only evaluable stress episode and durability is only `conditionally_durable` (rolling correlation `moderately_stable`, sign stability 0.67). A structural break is flagged at 2009-03-31.

**What this means:** use this page as a CAUTIONARY rebuild to be compared against the untouched original `housing_starts_spy` -- not as proof that Housing Starts forecasts the S&P 500. The honest verdict is a low-confidence, search-found candidate awaiting a frozen-rule final exam.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY to 100% LONG SPY when the 8-month-lagged Housing-Starts "
        "contraction flag equals 1, and a SELL back to 0% (CASH) when it falls "
        "to 0. Over the OOS window the rule made 30 such trades (annual "
        "turnover 3.6) and spent more than half the time in cash -- which is "
        "how it cut the drawdown while winning only 34.6% of trades."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1993-10-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash_pro: contraction (hst_yoy_contraction_flag, L8) = 1.000 vs threshold 0.000; position 0% → 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Census / HUD via live FRED API (REBUILT 2026-10-08, NOT the original committed dataset) | `HOUST` New Privately-Owned Housing Units Started (thousands, SEASONALLY ADJUSTED annual rate, SAAR) | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "This pair is the #255 publication-lag-floored REBUILD of "
    "`housing_starts_spy`. The Housing Starts series was reconstructed from the "
    "live FRED API (`HOUST`) plus Yahoo Finance SPY on 2026-10-08 -- it does NOT "
    "reuse the original committed dataset, so the two pairs can be compared as "
    "independent builds. `HOUST` is SEASONALLY ADJUSTED (SAAR), so no "
    "deseasonalisation is required and month-on-month change is a valid input. "
    "The raw SAAR level (`hst_level`) is trend-dominated and non-stationary "
    "(augmented Dickey-Fuller does not reject a unit root) and is EXCLUDED as a "
    "signal. Signals are stationary transforms: year-over-year growth (the "
    "headline), month-on-month growth, 3-month change, YoY of the 3-month "
    "average, YoY acceleration, a rolling 120-month z-score of YoY growth, and a "
    "BINARY YoY-contraction flag (1 when YoY growth is below zero). The winning "
    "signal is the 8-month-lagged binary contraction flag, evaluated against a "
    "fixed 0.0 threshold (greater-than rule), traded Long/Cash (P1), no "
    "lookback. The lead axis is FLOORED (floor L1, grid [1..13]) to respect the "
    "~mid-month (~17th of M+1) Census/HUD New Residential Construction release "
    "lag, so the strategy does not use future information. Housing starts are "
    "revised; the live FRED API is treated as ground truth."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger | Do lagged housing-starts values improve SPY forecasts -- or the reverse? | Formal lead-lag test, robust to integration order |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM / Markov regimes | Which months are calm vs high-variance housing turning points? | Descriptive regime backdrop (NOT the winner in this rebuild) |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: Housing-Starts transforms x threshold rules x strategy families x orientations x FLOORED monthly leads (L1-13, floor L1) x lookbacks. The final tournament file has 14,300 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 10,378 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `contraction / T1_fixed_p25 / P1_long_cash (pro) / L8 / LB_NA`, selected by max OOS Sharpe (ECON-T3 cascade, resolved at step 5 with 25 tied at step 1). The median valid combo scored 0.78 -- below buy-and-hold's 0.95; the winner's 1.45 is the search maximum.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/housing_starts_rebuilt_spy/evidence_status.json` marks the pair `found_in_search`. Forward Granger causality is ABSENT at every lag, the reverse direction is significant at all twelve lags, and the winner is a coarse binary flag at an 8-month lead with a 34.6% win rate -- reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau & HUD, New Residential Construction (Housing Starts, HOUST), via FRED.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." (Markov-switching / HMM)
7. Andrews, D. W. K. (1993). "Tests for Parameter Instability and Structural Change with Unknown Change Point." (Quandt-Andrews sup-F)
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
        "original housing_starts_spy (built by Vichua4b, data via Dana's "
        "pipeline), which is left untouched; the two are meant to be compared. "
        "Out-of-sample window 2018-04-30 to 2026-08-31, 101 monthly "
        "observations. Total tournament count is 14,300 benchmark-excluded "
        "strategy combinations; 10,378 are valid. The winner is a binary "
        "YoY-contraction flag at L8 on the floored grid [1..13]. Evidence "
        "status: found_in_search; bootstrap p=0.106; forward Granger causality "
        "absent."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the REBUILT Housing Starts analysis. "
        + _PARALLEL_NOTE
        + " The most important points: the indicator is seasonally adjusted at "
        "source (so no deseasonalisation is applied and month-on-month change is "
        "valid); the descriptive sort is a non-monotonic hump; forward causality "
        "is ABSENT (starts lag the market here); and the winning rule is a "
        "coarse binary contraction flag at an 8-month lead with a 34.6% win "
        "rate and a non-significant bootstrap p-value -- it still needs a "
        "frozen-rule holdout test."
    ),
)
