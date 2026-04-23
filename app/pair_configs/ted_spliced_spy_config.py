"""Spliced TED × SPY pair configuration (Rule APP-PT1).

Wave 10I.A Part 3b — Ray narrative port (commit supersedes Part 2 stubs).
Source content ported from the deleted 3-in-1 TED composite
(app/pages/6_ted_variants_*.py pre-commit a9d493e~1), re-authored
pair-specifically for Variant C.

Pair ID: ted_spliced_spy  (Variant C — Official TEDRATE pre-2022 spliced with
affine-adjusted DFF-TED post-2022; 1993-present)
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Spliced TED Spread as an Equity Signal"
    PAGE_SUBTITLE = (
        "Can we extend the classic LIBOR-TED history past its 2022 end-date "
        "by splicing in an affine-adjusted Fed-Funds proxy — and does the "
        "resulting 30-year spread predict S&P 500 returns?"
    )

    HEADLINE_H2 = (
        "## Spliced TED (official 1993-2022 + DFF-adjusted 2022+) as an "
        "extended-history funding-stress signal for SPY"
    )

    PLAIN_ENGLISH = (
        "Variant C is a compromise. It takes the official LIBOR-based TED spread "
        "for the 1993–2022 window — the original indicator — and extends it past "
        "LIBOR's 2022 retirement by adding the Fed-Funds-based proxy, mean-and-"
        "volatility matched so the two stitch together without a visible seam. "
        "The result is a single 30-year series that keeps the legacy indicator "
        "intact where it existed and continues it credibly where it did not."
    )

    WHERE_THIS_FITS = (
        "This is the *extended-history continuity* variant. It honours the legacy "
        "TED concept by using the real TEDRATE series wherever available, and "
        "paying a structural-assumption cost only in the post-2022 tail. Compared "
        "to Variant A (SOFR, purist but short) it gives up definitional modernity "
        "for 30 years of history; compared to Variant B (DFF-TED, single homogeneous "
        "series) it gives up homogeneity for fidelity to the original indicator "
        "where that indicator existed."
    )

    ONE_SENTENCE_THESIS = (
        "The spliced TED series delivers the strongest long-sample tournament "
        "KPIs of the three variants, at the cost of one structural assumption: "
        "that the affine adjustment fitted on the 1993-2022 overlap continues "
        "to hold out-of-sample."
    )

    KPI_CAPTION = (
        "Winner strategy KPIs: OOS Sharpe 1.19 on ~8 years of out-of-sample data "
        "(2018-01 onwards). Higher than the DFF variant, slightly lower than the "
        "SOFR headline, and — uniquely — tested across GFC, COVID, and the "
        "post-2022 rate-hiking cycle."
    )

    HERO_TITLE = "Spliced TED Spread (1993-2025) vs. S&P 500"
    HERO_CHART_NAME = "ted_spliced_spy_hero"
    HERO_CAPTION = (
        "Spliced TED: the official FRED TEDRATE series through January 2022, "
        "then extended by an affine-adjusted DFF-TED continuation. The 2008 GFC "
        "spike dwarfs all other episodes; dot-com, European sovereign, 2015 "
        "China wobble, and COVID are each clearly visible."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by Spliced-TED Stress Regime"
    REGIME_CHART_NAME = "ted_spliced_spy_regime_stats"
    REGIME_CAPTION = (
        "SPY Sharpe ratios sorted by Spliced-TED quartile over 1993-2025. "
        "Q1 = calmest funding conditions; Q4 = highest stress. The counter-"
        "cyclical pattern is the strongest of the three variants, reflecting "
        "the richer crisis content of the long sample."
    )

    NARRATIVE_SECTION_1 = """
### What Is the TED Spread — and Why Splice?

The TED spread measures the gap between what banks pay to borrow short-term cash and the risk-free government rate. When banks trust each other, this gap is small; when credit or liquidity fear rises, it widens dramatically. The classic TED spread used LIBOR as the bank-borrowing leg.

**The splice problem.** FRED's official TED series (`TEDRATE`) ends in January 2022 because LIBOR itself was retired. That leaves us with a 29-year series of the *right* indicator, and no principled way to extend it using the replacement rate (SOFR) — because SOFR and LIBOR measure fundamentally different things (the overlap correlation between SOFR-DTB3 and TEDRATE is only −0.04, i.e. no relationship).

**The splice solution.** The Fed Funds rate minus T-Bill (DFF-TED) has a +0.63 overlap correlation with TEDRATE. That is not identical, but it is close enough to extend the history credibly *if* we calibrate an affine adjustment: `adjusted_post_2022 = DFF_TED × scale + shift`, where `scale` and `shift` are chosen on the 1993-2022 overlap so the two series have matching mean and standard deviation. The result is Variant C — the actual TEDRATE where it exists, and a mean-and-variance-matched DFF-TED where it does not.
"""

    NARRATIVE_SECTION_2 = """
### Caveats Specific to Variant C

Variant C's main advantage — 30 years of the *original* indicator plus a continuous extension — comes with one genuine structural assumption:

- **The affine adjustment must continue to hold out-of-sample.** We fit `scale` and `shift` on the 1993-2022 overlap, where both TEDRATE and DFF-TED were observable. For 2022-onwards, we are assuming the same two numbers still describe the relationship. If the post-LIBOR credit-vs-repo dynamics shift materially, the extension could drift.
- **Different risk mixes across the splice boundary.** Pre-2022 the series reflects LIBOR-based credit stress; post-2022 it reflects a DFF-based funding premium. Mean and standard deviation are matched, but the underlying economic drivers are not identical.
- **OOS window straddles the splice.** Only the 2022-onwards portion of the out-of-sample data uses the adjusted-DFF continuation. This limits the degree to which the splice assumption has been stress-tested live.

For a structurally clean alternative, consult Variant B (DFF-TED) — no splice, but a proxy throughout.
"""

    SCOPE_NOTE = (
        "Scope discipline: TEDRATE, DFF, and DTB3 are the in-scope primary inputs "
        "for constructing the spliced series. SPY is the target. Controls appear "
        "only in regressions, never as trading signals."
    )

    TRANSITION_TEXT = (
        "The regime view shows the strongest counter-cyclical spread of the three "
        "TED variants. The evidence page formalises this with econometric tests "
        "that exploit the 30-year window — including crisis-rich episodes that "
        "Variant A cannot see."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson and rolling correlations measure the linear co-movement between "
        "the spliced TED spread and forward SPY returns at multiple horizons. "
        "Because the series spans three decades, precision is high; the splice "
        "itself does not distort correlation estimates because the overlap "
        "calibration matches both moments used by Pearson's formula."
    ),
    question=(
        "Does the spliced TED spread co-move negatively with forward SPY returns "
        "over 5-, 21-, and 63-day horizons across 1993-2025?"
    ),
    how_to_read=(
        "Darker blue = stronger negative correlation (stress up → forward returns "
        "down). Red cells are positive co-movement. Near-zero cells mean no linear "
        "relationship at that horizon."
    ),
    chart_name="ted_spliced_spy_correlations",
    chart_caption=(
        "Correlation heatmap of Spliced-TED signals versus forward SPY returns, "
        "1993-2025. Negative-signed cells are consistent with the counter-"
        "cyclical thesis."
    ),
    observation=(
        "Consistently negative correlations across RoC and momentum signals at "
        "21-day horizons, with magnitudes at least as large as Variant B's. "
        "The inclusion of GFC in the sample sharpens the signal."
    ),
    interpretation=(
        "The spliced series inherits Variant B's robust linear relationship and "
        "adds the information content of the original LIBOR-based data during "
        "GFC and earlier episodes. The correlation view is the cleanest of the "
        "three variants."
    ),
    key_message=(
        "Negative, directionally correct, and statistically sharp — the spliced "
        "series is the highest-information TED variant at the correlation level."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "Local projections (Jordà 2005) estimate SPY's impulse response to a "
        "Spliced-TED shock horizon-by-horizon, with HAC (Newey-West) standard "
        "errors for overlapping-horizon autocorrelation."
    ),
    question=(
        "After a +1σ Spliced-TED shock today, what is the expected path of "
        "SPY returns over the following 5, 21, and 63 days — across a sample "
        "that includes dot-com, GFC, and COVID?"
    ),
    how_to_read=(
        "Each point is the estimated SPY response at that horizon. Shaded "
        "bands are 95% HAC confidence intervals. Bands excluding zero indicate "
        "statistical significance."
    ),
    chart_name="ted_spliced_spy_local_projections",
    chart_caption=(
        "Impulse-response of SPY returns to a +1σ Spliced-TED shock, 1993-2025."
    ),
    observation=(
        "Significant negative response at 5- and 21-day horizons, with the "
        "most precise point estimates among the three variants. Effect fades "
        "toward zero at 63 days."
    ),
    interpretation=(
        "The impulse-response is the cleanest of the three TED variants — same "
        "directional pattern as Variants A and B, but tighter confidence bands "
        "thanks to 30 years of data including three major crises."
    ),
    key_message=(
        "Strongest statistical evidence of the three TED variants. If one only "
        "looks at impulse-responses, Variant C is the one to cite."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We test the Spliced-TED → SPY relationship with correlation analysis "
        "and Jordà local projections over 1993-2025. The long sample and the "
        "use of the original TEDRATE data pre-2022 give this variant the "
        "strongest impulse-response evidence in our study."
    ),
    "plain_english": (
        "Method 1: do the two series move together over 30 years? Method 2: "
        "if funding stress jumps today, what happens to the S&P over the "
        "following weeks, across three major crises?"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "The econometrics give Variant C the strongest statistical case. The "
        "tournament page asks whether that translates into the best trading rule."
    ),
    "transition": (
        "Continue to the Strategy page for the tournament winner and its KPIs."
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating Spliced-TED Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested ~991 strategy combinations on the Spliced-TED series (Variant C) "
        "to find the most robust extended-history timing rule."
    )

    PLAIN_ENGLISH = (
        "The tournament winner on Variant C is a short-lead, signal-strength rule. "
        "Watch the 21-day rate of change in Spliced-TED. When the RoC moves below "
        "its in-sample 25th-percentile threshold, scale SPY exposure proportionally "
        "from 0% up to 100%. A one-day lead lag applies — positioning is implemented "
        "the next business day."
    )

    SIGNAL_RULE_MD = """
**Winner (from `results/ted_spliced_spy/winner_summary.json`):**

| Field | Value |
|:---|:---|
| Signal | Spread 21-Day Rate of Change (`spread_roc_21d`) |
| Threshold | 25th percentile, fixed in-sample (`T1_p25`) |
| Strategy | Signal-Strength / Proportional (P2) |
| Lead time | 1 day |
| Direction | Counter-cyclical — scale long exposure as RoC drops below threshold |
| OOS Sharpe | **1.19** |
| OOS annualised return | **+13.42%** |
| Max drawdown | **−12.78%** |
| Annual turnover | ~14 round-trips |
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
1. Construct the spliced daily series: TEDRATE for 1993-01 through 2022-01, then `adjusted_DFF_TED = DFF_TED × scale + shift` (calibrated on overlap) from 2022-02 onwards.
2. Compute its 21-day rate of change.
3. Fix the 25th-percentile threshold on the in-sample window (1993-01 to 2017-12).
4. Map the gap between today's RoC and the threshold to a proportional SPY exposure in [0, 100%].
5. Apply a 1-day lead lag — today's signal implements tomorrow's position.
"""

    MANUAL_USE_MD = """
A human operator replicating the rule would:

1. Pull the latest TEDRATE (through 2022) and DFF, DTB3 (through today) from FRED.
2. Apply the published affine adjustment to extend TEDRATE post-2022.
3. Maintain a rolling 21-day RoC series.
4. Compare today's RoC to the fixed 25th-percentile benchmark; scale SPY position proportionally when below.
5. Rebalance next business day (1-day lead). Monthly review is sufficient given ~14 round-trips per year.
"""

    TOURNAMENT_SCATTER_CHART_NAME = "ted_spliced_spy_tournament_scatter"

    CAVEATS_MD = """
- **Splice assumption.** The `scale` and `shift` parameters are calibrated on the 1993-2022 overlap and assumed to hold out-of-sample for 2022-onwards. A regime shift in the LIBOR-to-Fed-Funds relationship would invalidate the extension. This is the single biggest structural risk of Variant C.
- **Heterogeneous economic drivers across the splice boundary.** Pre-2022 reflects LIBOR-based bank credit risk; post-2022 reflects Fed-Funds-based funding premia. Mean and variance are matched, but the underlying stress mechanisms are not identical.
- **Drawdown closer to Variant B.** −12.8% max drawdown — well above Variant A's −3.6% but modestly better than Variant B's −14.7%.
- **Missing artefacts.** `equity_curves`, `drawdown`, and `walk_forward` charts are not yet generated (tracked under BL-CHART-GAPS-LEGACY); Performance tab shows "chart pending" placeholders.
"""

    TRADE_LOG_EXAMPLE_MD = """
**Crisis-era trade citation (Global Financial Crisis episode).**

From `results/ted_spliced_spy/winner_trade_log.csv`:

| Entry | Exit | Direction | Holding | Return |
|:---|:---|:---|:---:|:---:|
| 2008-10-27 | 2008-10-28 | Long | 1 day | **+10.09%** |

This is the winner's single largest log entry — a one-day long position entered during the late-October 2008 GFC capitulation phase. The Spliced-TED series used here is the *original TEDRATE* data (2008 is pre-splice), so this trade citation reflects the rule's behaviour on the authentic LIBOR-based TED spread. The 21-day RoC had crossed below its in-sample 25th-percentile threshold as the Fed's liquidity facilities began to compress the LIBOR-OIS gap; with a 1-day lead and the P2 signal-strength rule scaling to full exposure, the strategy captured the October 28 10% SPY rally. A second large GFC trade (`2008-11-21 → 2008-11-24`, +6.0%) replays the same pattern later in the crisis.
"""


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency | Notes |
|:---------|:-------|:-------|:----------|:------|
| **TED Spread (official)** | FRED | TEDRATE | Daily | LIBOR-based; 1993-01 to 2022-01 |
| **Fed Funds Rate** | FRED | DFF | Daily | Used for post-2022 splice extension |
| **3M T-Bill (Secondary Market)** | FRED | DTB3 | Daily | Risk-free short rate |
| **S&P 500 (Target)** | Yahoo Finance | SPY | Daily | Adjusted close |
| **VIX** | Yahoo Finance | ^VIX | Daily | Control variable |
| **10Y Treasury** | FRED | DGS10 | Daily | For yield-curve control |

*Scope discipline (ECON-SD).* TEDRATE + DFF + DTB3 are in-scope primary
inputs to construct the spliced spread. Splice calibration: affine adjustment
`adjusted = DFF_TED × scale + shift` fitted on the 1993-2022 overlap so the
post-2022 continuation matches TEDRATE's mean and standard deviation.
"""

_INDICATOR_CONSTRUCTION_MD = """
**Core indicator.** Two-segment construction:

1. **1993-01-04 → 2022-01-31:** `Spliced_TED_t = TEDRATE_t` (official FRED series).
2. **2022-02-01 → present:** `Spliced_TED_t = (DFF_t − DTB3_t) × scale + shift`, where `scale` and `shift` are fitted on the 1993-2022 overlap to match TEDRATE's mean and standard deviation.

Total sample: ~8,589 daily observations through the 2026-03-14 cutoff.

**Derived signals used in the tournament (10 total):** Level, z-score (126d, 252d), rate of change (21d, 63d), momentum (21d, 63d), percentile rank, realised volatility, stress dummy.

The splice boundary is visible as a slight change in short-term volatility behaviour around January 2022 — the overlap-matched moments do not enforce higher-moment equivalence. Rate-of-change signals are relatively robust to this because they cancel out the level shift automatically; level-based signals should be treated with more caution across the splice boundary.
"""

_METHODS_TABLE_MD = """
| Method | Question It Answers | Key Parameters |
|:-------|:--------------------|:--------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline test for Spliced-TED ↔ SPY link |
| Granger Causality | Test if spread predicts SPY returns | Up to 5 daily lags |
| Predictive OLS | Baseline regressions with HC3 robust SEs | 3 signals × 3 horizons |
| Local Projections (Jordà) | Impulse response at 5d, 21d, 63d | HAC (Newey-West) SEs |
| Quantile Regression | Tail-risk / asymmetric effects | 7 quantiles (0.05 to 0.95) |
| Combinatorial Tournament | ~991 strategy combinations | 5 leads × 6 thresholds × 3 strategies |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals (10)** | Spread level, z-score (126d, 252d), RoC (21d, 63d), momentum (21d, 63d), percentile rank, realized vol, stress dummy |
| **Thresholds (6)** | Fixed percentile (IS) at 25th/50th/75th, rolling percentile (252d) at 25th/50th/75th |
| **Strategies (3)** | P1 Long/Cash, P2 Signal-Strength, P3 Long/Short |
| **Lead times (5)** | 0, 1, 5, 10, 21 days |
| **Total** | ~991 combinations |
| **Direction** | Counter-cyclical — BELOW threshold = bullish, ABOVE = bearish |
| **IS / OOS split** | 1993-01 → 2017-12 / 2018-01 → present |

See `results/ted_spliced_spy/winner_summary.json` for the canonical winner.
"""

_REFERENCES_MD = """
- Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007-2008. *Journal of Economic Perspectives*, 23(1), 77-100.
- Gilchrist, S., & Zakrajsek, E. (2012). Credit spreads and business cycle fluctuations. *American Economic Review*, 102(4), 1692-1720.
- Duffie, D., & Stein, J. C. (2015). Reforming LIBOR and other financial market benchmarks. *Journal of Economic Perspectives*, 29(2), 191-212.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161-182.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Sample period: 1993-01 to 2025-12, ~8,589 daily observations. "
        "ADF statistic −4.074 (p = 0.0011) — stationary. "
        "IS/OOS split: 1993-01 → 2017-12 / 2018-01 onwards. The post-2022 "
        "portion of the OOS window uses the affine-adjusted DFF extension."
    ),
    plain_english=(
        "We stitched together the official LIBOR-based TED spread (1993-2022) "
        "with an affine-adjusted Fed-Funds proxy (2022-present) to get a "
        "continuous 30-year series. We validated the splice on the overlap, "
        "derived ten measurement variants, ran the standard econometric "
        "battery, and held a ~991-combination tournament. The result is the "
        "best long-sample tournament performance of the three TED variants, "
        "at the cost of one structural assumption about the post-2022 extension."
    ),
)
