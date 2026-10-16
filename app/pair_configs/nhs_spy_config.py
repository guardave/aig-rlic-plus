"""New Home Sales (NSA) x SPY pair configuration (Rule APP-PT1).

Pair `nhs_spy`. Narrative rewritten for the 20261016 run (causal regime port + in-sample
selection, branch fix261016_hmm_port_eci_nhs). Every number below is read from
results/nhs_spy/ (winner_summary.json, hmm_lookahead_audit_20261016.json,
tournament_results_20261016.csv, legacy_oos_selection_20261016.csv,
tournament_validation_20261016/*, structural_break_nhs_spy.json, subperiod_sharpe.csv,
core_models_20261016/*, regime_quartile_returns.csv, granger_by_lag.csv).

What changed on 2026-10-16:
  - The 20260703 winner (hmm_stress / T2_roll_p25 / LB60 / P1_long_cash pro / L0, OOS Sharpe
    1.49, HAC t 4.53) traded a 2-state HMM probability fit on the full sample and read with
    forward-backward smoothing (look-ahead), at lead L0, below the L2 publication-lag floor,
    and was selected by OOS Sharpe. Same rule on the causal HMM: 1.36 at L0, 0.85 at L2.
  - Regime models are now fit on in-sample months only and read with a forward filter
    (scripts/_regime_causal.py). The lead grid is [2, 3, 6, 9, 12].
  - Winner by in-sample Sharpe (common IS window 2002-11-30..2018-01-31): contraction /
    P2_signal_strength counter / L9 / LB36. On the 0/1 contraction flag this is long SPY when
    NHS YoY growth nine months earlier was not negative and cash when it was; its OOS positions
    equal the long/cash version of the rule. IS Sharpe 1.46 (B&H 0.79); OOS Sharpe 0.93
    (B&H 0.89), annualized return 11.9% vs 14.8%, max drawdown -13.5% vs -23.9%.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: New Home Sales as an Early-Cycle Housing Timing Overlay"
    PAGE_SUBTITLE = (
        "New Home Sales, year-over-year growth (FRED HSN1FNSA, not seasonally "
        "adjusted) x S&P 500 (SPY), monthly decision rules with release-lag "
        "discipline."
    )

    HEADLINE_H2 = (
        "## The in-sample-selected rule — hold SPY unless New Home Sales growth was "
        "negative nine months earlier — has an out-of-sample Sharpe of 0.93 against "
        "0.89 for buy-and-hold, with a smaller drawdown (−13.5% vs −23.9%) and a lower "
        "return (11.9% vs 14.8% a year)"
    )

    PLAIN_ENGLISH = (
        "New Home Sales is an early-cycle housing indicator: buyers commit "
        "before construction, so sales lead starts, permits, and the jobs and "
        "spending they drive. The natural prior is procyclical -- stronger "
        "home-sales demand should coincide with better equities -- and the "
        "descriptive quartiles rise from weak to strong growth. A search over "
        "5,500 monthly rules picked the one with the best record before 2018: "
        "hold SPY unless home-sales growth was negative nine months earlier. "
        "From 2018 to mid-2026 it earned a Sharpe ratio of 0.93 versus 0.89 for "
        "holding SPY, with a smaller drawdown and a lower return."
    )

    WHERE_THIS_FITS = (
        "This is a housing leading-indicator signal tested against broad U.S. "
        "equities. The procyclical direction is clear in the descriptive "
        "quartiles; the formal forward-causality tests are weak (one long lag). "
        "The tradable rule is a long/cash overlay that steps out of SPY after "
        "home-sales contractions."
    )

    ONE_SENTENCE_THESIS = (
        "Stronger New Home Sales growth coincides with better equity returns, "
        "and the in-sample-selected rule (cash when home-sales growth was "
        "negative nine months earlier) scores an out-of-sample Sharpe of 0.93 "
        "versus 0.89 for buy-and-hold, while forward Granger causality is "
        "significant only at a single 11-month lag."
    )

    KPI_CAPTION = (
        "the rule was chosen by its in-sample Sharpe (2002-11-30 to "
        "2018-01-31) from 5,344 valid combinations, then scored once on "
        "2018-02-28 to 2026-05-31 (100 months). No frozen-rule final exam has "
        "been run."
    )

    HERO_TITLE = "New-Home-Sales YoY Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: New Home Sales year-over-year growth (which strips out "
        "the regular spring-vs-winter selling swing, since the raw Census "
        "series is not seasonally adjusted) is shown against SPY on a shared "
        "time axis, with the 0% line marked and the 2008-09 collapse and "
        "2022-23 rate-shock contraction annotated. The selected rule trades the "
        "sign of this growth series (negative = contraction), not the raw level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by New-Home-Sales Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by New Home Sales "
        "YoY-growth quartile. The gradient runs the RIGHT way -- Sharpe RISES "
        "monotonically from Q1 (weakest growth) at 0.20 to Q4 (strongest) at "
        "1.50, and Q1 carries a -51% drawdown versus Q4's -10%. Stronger "
        "housing demand coincides with better, calmer equities -- the "
        "procyclical prior holds cleanly."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The rule was selected by its in-sample record (2002-11-30 to 2018-01-31) and then tested once on data not used to pick it (out-of-sample, OOS: 2018-02-28 to 2026-05-31). OOS, it earns a Sharpe ratio -- return per unit of volatility -- of 0.93 versus 0.89 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- is -13.5% versus -23.9%, and its annualized return is lower, 11.9% versus 14.8%; it was invested 62% of the time.

New Home Sales is a classic early-cycle housing indicator: buyers commit before construction begins, so sales sit one step ahead of housing starts, permits, and the employment and consumption they drive. The natural prior is **procyclical** -- stronger home-sales demand should coincide with a healthier economy and better equities -- and the descriptive quartiles point that way.

### A Seasonally-Raw Series, Read Year-over-Year

The one technical wrinkle that shapes everything: the Census new-home-sales series (FRED `HSN1FNSA`) is **not seasonally adjusted**. Raw sales swing predictably every year -- a spring selling-season peak, a winter trough -- so the raw level and its month-to-month change are dominated by the calendar, not the cycle. Every signal on this page is therefore **deseasonalised**: the headline transform is year-over-year growth (this month versus the same month a year earlier), which cancels a fixed seasonal, backed by a statistically seasonally-adjusted (STL) alternative. We never trade or chart the raw level as a signal.

### The Selected Rule

The rule reads one fact: was New Home Sales year-over-year growth **negative** (a contraction) nine months earlier? If not, it holds SPY; if so, it holds cash. In the 2018-2026 test window that put it in cash for 38 of 100 months, including most of 2022-23.

### Correction to the earlier version of this page

This page previously reported a rule on a Hidden Markov Model (HMM) regime probability with an OOS Sharpe of **1.49**. That probability was estimated on the whole sample and smoothed with later data, so each month's value used information from after that month (look-ahead); the rule also used the current month's reading (lead 0), although Census publishes each month's figure near the end of the following month; and it was picked by its OOS score. With the HMM fitted on in-sample months only and read forward, the same rule scores **1.36** at lead 0 and **0.85** at the earliest tradable lead (2 months) (`hmm_lookahead_audit_20261016.json`).

<!-- expander: Why is the forward evidence called weak? -->
The procyclical direction is clear in the descriptive quartiles, but "the direction is right" and "this forecasts the market" are different claims. The formal forward-causality tests are weak: New Home Sales growth Granger-causes SPY only at a single long lag (11 months), while SPY leads home sales at short lags (1, 2).
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
                "This is the strongest leading-indicator episode for the pair."
            ),
            "caption": "GFC: home sales turned down years ahead of the equity bear -- the leading case.",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During the coronavirus disease 2019 (COVID-19) shock, New Home "
                "Sales spiked on record-low mortgage rates while SPY crashed "
                "and rapidly recovered -- housing demand and the market moved "
                "together in a fast-recovery regime."
            ),
            "caption": "COVID: sales spiked on low rates as SPY recovered.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022-23 mortgage-rate shock, New Home Sales "
                "contracted sharply as 30-year rates jumped. The selected "
                "rule, which steps to cash after home-sales contractions, was "
                "in cash for most of 2022-23."
            ),
            "caption": (
                "2022-23: rate shock crushed sales -- the dominant OOS regime."
                "Event markers are dated to the day while the "
                "plotted series is month-end, so the Jan-2022 peak and Oct-2022 "
                "low markers each sit about a month from the visible extremum."
                ),
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history-zoom charts make the leading-indicator character tangible. During the **2008-09 Global Financial Crisis**, new home sales collapsed roughly 80% from their 2005 peak and turned down well ahead of the equity bear market -- the textbook case for housing as an early-cycle signal. During **COVID-19**, sales spiked on record-low mortgage rates as SPY recovered -- a fast-recovery regime. During the **2022-23 rate shock**, sales contracted sharply as mortgage rates jumped -- the strong, recent regime that dominates the out-of-sample window. The Dot-Com window is a continuity confirmer for the portal's standard episode set.
"""

    TRANSITION_TEXT = (
        "The historical story is a genuine early-cycle-housing one, so the full "
        "evidence suite matters. The Evidence page shows the clean procyclical "
        "quartiles alongside the weaker formal causality tests that keep "
        "confidence low."
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
        "for stocks'; here the gradient does rise cleanly."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Sharpe RISES monotonically from Q1 (weakest NHS YoY) "
        "at 0.20 to Q4 (strongest) at 1.50, and Q1 carries a -51% drawdown "
        "versus Q4's -10%."
    ),
    observation=(
        "The gradient is monotonic and procyclical: the strongest-growth "
        "quartile has the best forward Sharpe and the shallowest drawdown."
    ),
    interpretation=(
        "Stronger housing demand coincides with better, calmer equity returns. "
        "The procyclical prior holds cleanly here -- a contrast with the "
        "money-supply and industrial-production pairs, where the level story "
        "inverted."
    ),
    key_message=(
        "Procyclical and monotonic: stronger home-sales growth lines up with "
        "better, calmer equity returns."
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
        "only at lag 11; the reverse direction (SPY to NHS) is significant at "
        "lags 1 and 2."
    ),
    observation=(
        "Forward Granger support is weak -- significant only at a single long "
        "lag (11 months); reverse SPY-to-NHS support is present at short lags "
        "(1, 2)."
    ),
    deep_dive_title="Why does a single long lag mean low confidence?",
    deep_dive_content=(
        "A robust leading indicator clears the significance line across a band "
        "of plausible horizons. A single isolated long lag (11 months) is more "
        "consistent with a coincidence in the search than a dependable forward "
        "channel -- especially when the reverse direction (market leading "
        "housing) is significant at short lags."
    ),
    interpretation=(
        "Forward causality is weak and long-horizon, alongside clean "
        "procyclical quartiles."
    ),
    key_message="Forward causality is weak (a single long lag); confidence stays low.",
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
        "That pattern is consistent with a regime effect rather than a simple "
        "linear forward channel from home-sales growth to SPY."
    ),
    key_message="Quantile evidence points to a regime effect, not a linear predictor.",
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
    method_name="HMM Regime Map",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the home-sales growth series into two "
        "latent states. It is fit on in-sample months only (1991-2018) and "
        "read with a forward filter, so each month's probability uses data up "
        "to that month. The state labelled 'stress' in the data files (the one "
        "with the slightly higher in-sample variance) is in fact the normal "
        "state: about 80% of months at roughly +8.8% average year-over-year "
        "growth; the other state averages about -23.5% and captures housing "
        "busts."
    ),
    question="When is housing demand in its normal state -- and does timing SPY on it help?",
    how_to_read=(
        "The line is the forward-filtered probability of the normal (labelled "
        "'stress') state. It sits near 1 for most of the sample and falls "
        "toward zero when housing turns down. The vertical line marks the start "
        "of the out-of-sample window, after which the model is frozen."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the in-sample-fitted, forward-filtered probability "
        "of the normal housing state; it falls toward zero in the 2007-09 "
        "housing bust and in 2022-23."
    ),
    observation=(
        "The HMM separates normal housing-demand months from outright "
        "contractions; the probability is close to 0 or 1 most of the time. "
        "Rules built on it are in the tournament; the best one ranks 31st by "
        "in-sample Sharpe (1.35) and scores 0.65 out of sample."
    ),
    interpretation=(
        "The earlier winner traded this probability, estimated with look-ahead "
        "(full sample, smoothed) and read at lead 0. Built causally and read at "
        "the 2-month floor, the same rule scores 0.85 out of sample."
    ),
    key_message="The causal HMM probability is a tournament signal but not the winner.",
)

EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence: a clean procyclical direction, but weak forward causality",
    "overview": (
        "The regime quartiles are cleanly monotonic -- stronger home-sales "
        "growth lines up with better, calmer SPY returns, confirming the "
        "procyclical prior. But the formal forward-causality tests are weak: "
        "New Home Sales growth Granger-causes SPY only at a single long lag "
        "(11 months), while SPY leads home sales at short lags (1, 2). "
        "Supporting checks (local projections, transfer entropy, quantile "
        "regression) are consistent with a weak forward relationship."
    ),
    "plain_english": (
        "This section asks whether New Home Sales really helps predict future "
        "SPY performance. The direction is right and clean in the descriptive "
        "sort, and the formal lead-lag tests are weak. The Strategy page shows "
        "the rule selected in-sample and its out-of-sample record against "
        "buy-and-hold."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/nhs_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/nhs_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/nhs_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/nhs_spy/rolling_correlation_nhs_spy.csv"},
        {"label": "Stationarity tests", "path": "results/nhs_spy/stationarity_tests_20260703.csv"},
    ],
    "level1": [QUARTILE_BLOCK, GRANGER_BLOCK, HMM_BLOCK, CCF_BLOCK],
    "level1_labels": ["Growth Quartiles", "Granger Causality", "HMM Regimes", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy"],
    "tournament_intro": (
        "The tournament tested 5,500 benchmark-excluded strategy combinations "
        "on the lead grid 2, 3, 6, 9 and 12 months; 5,344 passed the in-sample "
        "validity checks. The winner is the valid rule with the highest "
        "in-sample Sharpe (2002-11-30 to 2018-01-31); its out-of-sample Sharpe "
        "is 0.93 against 0.89 for buy-and-hold, at the 89th percentile of all "
        "valid rules (median 0.63)."
    ),
    "transition": (
        "**Transition:** the direction is procyclical and clean, but forward "
        "causality is weak. The strategy page shows the in-sample-selected "
        "rule: a long/cash overlay that steps out of SPY after home-sales "
        "contractions."
    ),
}

class StrategyConfig:
    PAGE_TITLE = "The Strategy: An In-Sample-Selected Housing-Contraction Rule for SPY"
    PAGE_SUBTITLE = (
        "5,500 rule combinations were scored. The one with the best in-sample "
        "Sharpe is reported here, with its out-of-sample record against "
        "buy-and-hold."
    )

    STATISTICAL_FRAMING_BANNER = (
        "Correction (2026-10-16). This page previously reported hmm_stress / "
        "T2_roll_p25 / Long/Cash / L0 with an OOS Sharpe of 1.49 (HAC t 4.53). "
        "That result relied on HMM probabilities fitted on the full sample and "
        "smoothed with future data (look-ahead), used a lead of 0 months although "
        "each month's figure is published near the end of the next month, and the "
        "rule was picked by its OOS score. Rebuilt without look-ahead, with a "
        "2-month lead floor and in-sample selection, the winner below has an OOS "
        "Sharpe of 0.93 against 0.89 for SPY buy-and-hold."
    )

    PLAIN_ENGLISH = (
        "The rule moves between SPY and cash once a month. It holds SPY unless "
        "New Home Sales year-over-year growth, as it stood nine months earlier, "
        "was negative; then it holds cash. It was chosen because it had the "
        "highest in-sample Sharpe (1.46 vs 0.79 for buy-and-hold, 2002-2018). "
        "Out of sample (2018-02-28 to 2026-05-31, 100 months) it scored a Sharpe "
        "of 0.93 versus 0.89, an annualized return of 11.9% versus 14.8%, and a "
        "maximum drawdown of -13.5% versus -23.9%."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** each month, look at the New Home Sales year-over-year contraction flag (`nhs_yoy_contraction_flag`: 1 when YoY growth is below 0) **as it stood nine months earlier** (lead L9). If the flag was 0, hold **100% SPY**; if it was 1, hold **cash**. Countercyclical orientation on the flag (contraction = cash).

Tournament form: `contraction / P2_signal_strength (counter) / L9 / LB36`. Signal-strength sizing scales exposure by the flag's position in its trailing 36-month min-max range; on a 0/1 flag that is 100% or 0%, and when the flag did not change over the trailing 36 months the size is undefined (held as cash). The threshold label `T2_roll_p25` is not used by this sizing rule. Over the OOS window the positions are identical to the long/cash version of the rule (`T1_fixed_p25`, OOS Sharpe 0.93). In-sample, the sizing rule is undefined for 10 months (2009-09 to 2010-06) that the long/cash version holds in cash; excluding them gives the IS Sharpe of 1.46 versus 1.42 for the long/cash version.

If-then form:
- **IF** NHS YoY growth nine months ago was **not negative** -> hold SPY.
- **ELSE** -> hold cash.

Selection: highest in-sample Sharpe among 5,344 IS-valid rules on 2002-11-30 to 2018-01-31: 1.46 vs 0.79 for buy-and-hold.

Out-of-sample (2018-02-28 to 2026-05-31, 100 months): Sharpe 0.93 vs 0.89 buy-and-hold (HAC t of the mean return 3.26); annualized return 11.9% vs 14.8%; maximum drawdown -13.5% vs -23.9%; 20 position changes (2.4 per year); invested 62% of months.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Census monthly new-home-sales release (FRED series HSN1FNSA) and computes its year-over-year growth -- this month's sales versus the same month a year ago. Because the raw series is not seasonally adjusted, the year-over-year change is what strips out the regular spring-vs-winter selling swing. Second, it marks a contraction when that growth is below zero. Third, it applies a nine-month delay (each month's figure is published near the end of the following month; nine months is the lead with the highest in-sample Sharpe on the grid 2, 3, 6, 9, 12) and holds SPY unless the delayed reading shows a contraction.

It does not forecast mortgage rates, model the Fed, or claim that housing drives stocks. The Evidence page finds the formal forward-causality tests weak.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read New Home Sales (`HSN1FNSA`) from FRED.
2. Compute year-over-year growth (this deseasonalises the not-seasonally-adjusted series).
3. Look up the growth figure for the month nine months before the current month.
4. If it is negative, hold cash; otherwise hold SPY. Re-evaluate monthly.

The pair's `evidence_status` is `found_in_search`: the rule has not been tested on data released after it was frozen.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Only COVID 2020 "
        "falls inside the 2018-onward OOS window (Sharpe 1.07); the Dot-Com, "
        "GFC and China 2015 episodes predate the OOS split and are marked "
        "insufficient data."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 5,344 IS-valid "
        "combinations. The rule selected in-sample scores 0.93, the 89th "
        "percentile; the median is 0.63 and buy-and-hold 0.89; 852 combinations "
        "have a higher OOS Sharpe than buy-and-hold."
    )

    CAVEATS_MD = """
**Limitations** (from `winner_summary.json`, `hmm_lookahead_audit_20261016.json`, `structural_break_nhs_spy.json` and `tournament_validation_20261016/`):

1. **Margin over buy-and-hold.** OOS Sharpe 0.93 vs 0.89; annualized return 11.9% vs 14.8%. The Sharpe gap comes from lower volatility and drawdown (-13.5% vs -23.9%), not higher return. Bootstrap share of resampled buy-and-hold Sharpes at or above 0.93: 0.47.
2. **Selection.** 5,500 combinations were scored (5,344 IS-valid, about 3,974 distinct position series); the expected maximum |z| among that many unrelated rules with no skill is about 3.66. Across the grid, IS and OOS Sharpe have a rank correlation of 0.69.
3. **Sizing-rule artefact.** The winner's IS Sharpe (1.46) excludes 10 months in which its sizing is undefined; the long/cash version with identical OOS positions has IS Sharpe 1.42.
4. **Forward causality is weak.** Toda-Yamamoto Granger finds NHS YoY leads SPY only at lag 11; SPY leads home sales at lags 1 and 2.
5. **Durability.** Only COVID falls inside the OOS window (episode Sharpe 1.07). No structural break is flagged (candidate 2009-03, sup-F 2.58, bootstrap p = 0.53).
6. **Earlier winner withdrawn.** The 1.49 HMM rule used look-ahead regime probabilities and a lead below the 2-month publication floor; causal and floored, it scores 0.85.
7. **Input data.** The tournament uses the indicator transforms as published in July 2026 (`signals_20260703.parquet`); later FRED revisions (2026-04/05) are not included. The STL-adjusted signals (`sa_mom`, `sa_3m`) come from a full-sample seasonal decomposition.

**Costs.** Returns are gross of costs; at 50 bps per trade the OOS Sharpe is 0.84 (`tournament_validation_20261016/transaction_costs.csv`).
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records "
        "a SELL to cash dated 2022-03-31, when the contraction flag read nine "
        "months earlier turned on; apart from one invested month (2022-11) the "
        "rule stayed in cash until a BUY dated 2024-01-31. Each row's date is the end of the month the "
        "position applies to. Over the OOS window the rule made 20 position "
        "changes."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2022-03-31",
        "side": "SELL",
        "instrument": "SPY",
        "quantity_pct": "0.0",
        "commission_bps": "5",
        "reason": "P2_signal_strength_counter: contraction flag (lagged 9 months) = 1 — position 100% → 0%",
    }

STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Census via FRED (vintage of the July 2026 data pull; transforms as published in `signals_20260703.parquet`) | `HSN1FNSA` New One-Family Houses Sold (thousands, NOT seasonally adjusted) | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "New Home Sales (`HSN1FNSA`) is NOT seasonally adjusted, so the raw level "
    "and raw month-to-month change are dominated by a fixed annual seasonal and "
    "are EXCLUDED as signals. Signals are deseasonalised: year-over-year growth "
    "(the primary transform; a 12-month difference cancels the fixed seasonal), "
    "its acceleration and 3-month-average variant, a statistically seasonally-"
    "adjusted (STL) level and its month-over-month and 3-month growth, a "
    "rolling z-score of YoY growth, a 0/1 contraction flag (YoY < 0), and two "
    "regime probabilities (HMM and Markov-switching on YoY growth, fit on "
    "in-sample months only and read with a forward filter). The STL "
    "decomposition is computed on the full sample, so the STL-based signals "
    "use later data. The selected signal is the contraction flag at a "
    "nine-month lead. Census publishes each month's figure near the end of the "
    "following month, so the lead floor is 2 months; the tradable grid is 2, "
    "3, 6, 9 and 12 months."
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
| HMM / Markov regimes (in-sample fit, forward filter) | Which months are housing expansions vs contractions? | Regime-probability signals for the tournament |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: New-Home-Sales transforms (9 signals) x threshold rules x strategy families (long/cash, signal-strength sizing, long/short) x orientations x monthly leads {2, 3, 6, 9, 12} x lookbacks. The legacy grid's leads 0 and 1 are removed: Census publishes each month's figure near the end of the following month. The tournament file has 5,500 benchmark-excluded strategy combinations plus one BENCHMARK row.

**Selection (2026-10-16).** Validity uses in-sample data only (at least 60 in-sample months, in-sample exposure 5%-95%, turnover below 24 changes per year): 5,344 combinations pass. The winner is the valid row with the highest in-sample Sharpe on the common window 2002-11-30 to 2018-01-31 (the start is set by the latest-starting signal, the 120-month YoY z-score at lead 12); ties are broken by in-sample return, drawdown, trade count, then name. Winner: `contraction / T2_roll_p25 / P2_signal_strength (counter) / L9 / LB36`. For comparison only, the highest OOS Sharpe on this grid is sa_3m / T2_roll_p75 / long-short countercyclical / L2 / LB60 (1.30), ranked 3,501st in-sample (`legacy_oos_selection_20261016.csv`).

**Regime signals and input.** HMM and Markov-switching probabilities come from `scripts/_regime_causal.py` (in-sample fit, forward filter, no SPY return in the likelihood). The 20260703 winner and its causal replay are in `hmm_lookahead_audit_20261016.json`. The input frame uses the indicator transforms as published in `signals_20260703.parquet` with SPY re-pulled from Yahoo (monthly returns within 1.6e-6 of the July file).

`results/nhs_spy/evidence_status.json` marks the pair `found_in_search`: no frozen-rule final exam has been run.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau & HUD, New Residential Sales (New One-Family Houses Sold, HSN1FNSA), via FRED.
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
        "In-sample comparison window 2002-11-30 to 2018-01-31 (the selection "
        "objective is in-sample Sharpe; regime models are fit on 1991-2018); "
        "out-of-sample window 2018-02-28 to 2026-05-31, 100 monthly "
        "observations, scored once after selection. 5,500 benchmark-excluded "
        "combinations, 5,344 IS-valid. Evidence status: found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the New Home Sales analysis. The indicator is "
        "not seasonally adjusted (so every signal is deseasonalised via "
        "year-over-year growth or STL) and forward causality is weak. The "
        "winning rule (countercyclical on the contraction flag: cash after a "
        "contraction) was picked on pre-2018 data and then scored on 2018-2026."
    ),
)
