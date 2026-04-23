"""DFF-TED × SPY pair configuration (Rule APP-PT1).

Wave 10I.A Part 3b — Ray narrative port (commit supersedes Part 2 stubs).
Source content ported from the deleted 3-in-1 TED composite
(app/pages/6_ted_variants_*.py pre-commit a9d493e~1), re-authored
pair-specifically for Variant B.

Pair ID: dff_ted_spy  (Variant B — Fed Funds minus 3M T-Bill, 1993-present)
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: DFF-TED Spread as an Equity Signal"
    PAGE_SUBTITLE = (
        "Does the Fed-Funds-based funding-stress proxy (DFF - DTB3) — "
        "the most conservative TED variant — predict S&P 500 returns?"
    )

    HEADLINE_H2 = (
        "## DFF - DTB3 as a long-history funding-stress signal for SPY — "
        "OOS Sharpe vs buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "Variant B measures funding stress using the Fed Funds rate (what U.S. banks "
        "pay each other for overnight reserves) minus the 3-month T-Bill yield. It is "
        "not the original TED spread, but it tracks the same underlying premium — and "
        "crucially, it has daily data back to 1993, covering the dot-com bust, Global "
        "Financial Crisis, and COVID panic. It is the most conservative of our three "
        "TED variants: no splicing assumptions, and the longest continuous history."
    )

    WHERE_THIS_FITS = (
        "This is the *long-history, pragmatic* variant. It trades definitional purity "
        "(DFF is not LIBOR) for a 30+ year window that spans three major stress events. "
        "It is the best variant for statistical confidence; it is the weakest variant "
        "for regulatory fidelity to the legacy TED concept. The sibling Variant A "
        "(SOFR-TED) is the modern purist view; Variant C (Spliced) stitches the old "
        "LIBOR-TED to a DFF-based extension."
    )

    ONE_SENTENCE_THESIS = (
        "Wider DFF-TED spreads have historically been followed by softer SPY returns, "
        "but the predictive edge is modest and survives only within a disciplined "
        "tournament-selected rule."
    )

    KPI_CAPTION = (
        "Winner strategy KPIs: OOS Sharpe 0.97 on ~8 years of out-of-sample data "
        "(2018-01 onwards) — lower than the SOFR variant's headline but built on "
        "far more observations, making it the most statistically reliable of the three."
    )

    HERO_TITLE = "Fed Funds - 3M T-Bill (1993-2025) vs. S&P 500"
    HERO_CHART_NAME = "dff_ted_spy_hero"
    HERO_CAPTION = (
        "DFF minus 3M T-Bill, 1993-2025. Visible funding-stress episodes: the 2000 "
        "dot-com bust, the 2008 Global Financial Crisis (the largest spike), the 2015 "
        "China-devaluation wobble, and COVID-March-2020. The 2022-2023 rate-hiking "
        "cycle is also visible as a sustained elevated spread."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by DFF-TED Stress Regime"
    REGIME_CHART_NAME = "dff_ted_spy_regime_stats"
    REGIME_CAPTION = (
        "SPY Sharpe ratios sorted by DFF-TED quartile across 30+ years. Q1 = calmest "
        "funding conditions; Q4 = highest stress. The counter-cyclical pattern "
        "survives across multiple business cycles — the key advantage of Variant B's "
        "long history."
    )

    NARRATIVE_SECTION_1 = """
### What Is the TED Spread, and Why a Fed-Funds Proxy?

The TED spread measures the gap between what banks pay to borrow short-term cash and the risk-free government rate. When banks trust each other, this gap is small (10–30 basis points); when credit fear or liquidity stress rises, it widens dramatically.

The classic TED spread used LIBOR as the bank-borrowing leg. LIBOR was retired in 2022 after the manipulation scandal, leaving a discontinuity in the legacy series. But the *economic concept* — a funding premium over T-bills — can be reconstructed from the Fed Funds rate.

**Why DFF-DTB3 is a valid TED proxy.** In the overlap period (1993–2022), the correlation between the official TEDRATE and DFF-DTB3 is **+0.63**. Both series capture the same "funding premium over T-bills" concept; DFF simply replaces LIBOR (a survey-based unsecured rate) with the observed effective Fed Funds rate. The two are not identical — DFF omits the bank-credit component that LIBOR carried — but they co-move strongly enough to make DFF-TED a useful long-history stand-in.
"""

    NARRATIVE_SECTION_2 = """
### Why Variant B Is the Most Conservative Choice

Of the three TED variants we study, DFF-TED is the one a cautious researcher would reach for first:

- **Longest continuous history.** ~8,600 daily observations back to 1993 — more than 4× the SOFR variant.
- **No splicing.** Variant C stitches two different series with an affine adjustment. Variant B is a single, homogeneous series end-to-end.
- **Spans multiple regimes.** Dot-com, GFC, euro crisis, COVID, rate-hike cycles all in-sample.

The cost is that DFF-TED is a *proxy*, not the original indicator. The Sharpe numbers will look less spectacular than Variant A's short-sample headline, but they are earned on far more observations and cross multiple true out-of-sample crises.
"""

    SCOPE_NOTE = (
        "Scope discipline: only DFF and DTB3 are the in-scope primary signals for "
        "this pair. TEDRATE appears only for the overlap-period correlation check "
        "that justifies using DFF-TED as a proxy; it is not a trading input."
    )

    TRANSITION_TEXT = (
        "The regime view suggests the counter-cyclical pattern is robust across "
        "business cycles. The evidence page formalises this with correlation and "
        "impulse-response analysis over the full 30-year window."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson and rolling correlations measure linear co-movement between the "
        "DFF-TED spread (and derived signals) and forward SPY returns across "
        "multiple horizons. With 30+ years of data, the estimates are far more "
        "precise than for Variant A."
    ),
    question=(
        "Does DFF-TED stress co-move negatively with forward SPY returns across "
        "short (5d), medium (21d), and long (63d) horizons?"
    ),
    how_to_read=(
        "Darker blue = stronger negative correlation (funding stress up → forward "
        "returns down). Red cells indicate the opposite. Near-zero cells indicate "
        "no linear relationship at that horizon."
    ),
    chart_name="dff_ted_spy_correlations",
    chart_caption=(
        "Correlation heatmap of DFF-TED signals versus forward SPY returns, "
        "full-sample 1993-2025. Negative cells are consistent with the thesis."
    ),
    observation=(
        "Consistent negative correlations across RoC and momentum variants at "
        "21-day horizons. Level-based signals are weaker than change-based "
        "signals — the now-familiar RoC-dominates-level finding."
    ),
    interpretation=(
        "Across 30 years, the linear relationship is directionally correct and "
        "robust. Magnitudes are modest (as is usual for macro-credit signals "
        "versus equities), but their statistical significance is high given the "
        "sample size."
    ),
    key_message=(
        "The correlation view confirms a stable, directionally correct linear "
        "relationship over the full DFF-TED history."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "Local projections (Jordà 2005) estimate SPY's impulse response to a "
        "DFF-TED shock horizon-by-horizon without a VAR's parametric structure. "
        "HAC (Newey-West) standard errors correct the overlapping-horizon "
        "autocorrelation."
    ),
    question=(
        "After a +1σ DFF-TED shock today, what is the expected path of SPY "
        "returns over the following 5, 21, and 63 days?"
    ),
    how_to_read=(
        "Each point is the estimated SPY response at that horizon after a +1σ "
        "DFF-TED shock. Shaded bands are 95% HAC confidence intervals. Bands "
        "excluding zero indicate statistical significance."
    ),
    chart_name="dff_ted_spy_local_projections",
    chart_caption=(
        "Impulse-response of SPY returns to a +1σ DFF-TED spread shock, "
        "1993-2025. Significant negative response at short horizons."
    ),
    observation=(
        "Negative point estimates at 5- and 21-day horizons, with confidence "
        "bands excluding zero at 21 days. The response fades to zero by 63 days."
    ),
    interpretation=(
        "The impulse-response confirms the correlation finding with proper "
        "standard errors: funding stress Granger-causes short-horizon SPY "
        "underperformance. The effect is modest in magnitude but statistically "
        "robust over 30 years."
    ),
    key_message=(
        "Impulse-response pattern is clean and statistically significant at the "
        "21-day horizon — the most reliable TED-variant signal in our study."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We test the DFF-TED → SPY relationship with correlation analysis and "
        "Jordà local projections over the full 1993-2025 sample. Both methods "
        "point the same way, with narrower confidence bands than Variant A "
        "thanks to the longer sample."
    ),
    "plain_english": (
        "Method 1: do the two series move together over 30 years? Method 2: "
        "if funding stress jumps today, what happens to the S&P over the "
        "following weeks, with proper statistical controls?"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "The econometrics confirms a small but robust predictive edge. The "
        "tournament page asks whether a rule built on that edge beats buy-and-hold."
    ),
    "transition": (
        "Continue to the Strategy page for the tournament winner and its KPIs."
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating DFF-TED Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested ~991 strategy combinations on DFF - DTB3 (Variant B) — "
        "the longest-history TED variant — to find the most robust timing rule."
    )

    PLAIN_ENGLISH = (
        "The tournament winner on Variant B is a signal-strength rule: watch the "
        "21-day rate of change in DFF-TED, and scale SPY exposure from 0% to 100% "
        "depending on how far the signal has moved below the 25th-percentile "
        "threshold. A 5-day lead lag applies before each rebalancing."
    )

    SIGNAL_RULE_MD = """
**Winner (from `results/dff_ted_spy/winner_summary.json`):**

| Field | Value |
|:---|:---|
| Signal | Spread 21-Day Rate of Change (`spread_roc_21d`) |
| Threshold | 25th percentile, fixed in-sample (`T1_p25`) |
| Strategy | Signal-Strength / Proportional (P2) |
| Lead time | 5 days |
| Direction | Counter-cyclical — scale long exposure as RoC drops below threshold |
| OOS Sharpe | **0.97** |
| OOS annualised return | **+11.04%** |
| Max drawdown | **−14.71%** |
| Annual turnover | ~10 round-trips |
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
1. Compute the daily DFF-TED spread (`DFF − DTB3`).
2. Compute its 21-day rate of change: `roc_21 = spread_t / spread_{t-21} − 1`.
3. Fix the 25th-percentile threshold on the in-sample window (1993-01 to 2017-12).
4. Each day, map the gap between today's `roc_21` and the threshold to a proportional position size in [0, 100%] SPY exposure.
5. Apply a 5-day lead lag — today's signal drives positioning five business days hence.
"""

    MANUAL_USE_MD = """
A human operator replicating the rule would:

1. Pull daily DFF and DTB3 from FRED.
2. Maintain a rolling 21-day RoC series.
3. Compare today's RoC to the fixed 25th-percentile benchmark (in the methodology appendix).
4. Scale SPY position size proportionally to the gap below the threshold; exit to cash when the signal is above.
5. Review weekly — annual turnover is low (~10 trades), so weekly monitoring is sufficient.
"""

    TOURNAMENT_SCATTER_CHART_NAME = "dff_ted_spy_tournament_scatter"

    CAVEATS_MD = """
- **Proxy, not the original.** DFF-DTB3 is a valid long-history stand-in (r = +0.63 vs TEDRATE in overlap) but it omits the bank-credit component that LIBOR-TED carried. Treat the signal as a funding-stress proxy, not a direct measure of interbank credit fear.
- **Most conservative choice of the three.** Longest history, no splicing, spans multiple crises — but also the lowest headline Sharpe. This is the variant to trust when statistical reliability matters more than peak KPIs.
- **Larger drawdown.** −14.7% max drawdown is meaningfully worse than Variant A's −3.6% — partly because Variant B actually lived through GFC and dot-com, while Variant A did not.
- **Missing artefacts.** `equity_curves`, `drawdown`, and `walk_forward` charts are not yet generated (tracked under BL-CHART-GAPS-LEGACY); Performance tab shows "chart pending" placeholders.
"""

    TRADE_LOG_EXAMPLE_MD = """
**Crisis-era trade citation (Global Financial Crisis episode).**

From `results/dff_ted_spy/winner_trade_log.csv`:

| Entry | Exit | Direction | Holding | Return |
|:---|:---|:---|:---:|:---:|
| 2008-10-10 | 2008-10-13 | Long | 3 days | **+10.50%** |

This is the winner's largest single trade in the log — a short-dated long entry near the GFC panic low of mid-October 2008. The DFF-TED spread had spiked to crisis levels by early October and the 21-day RoC then *rolled over* as the Fed's liquidity facilities began to bite, dropping the signal below its in-sample 25th-percentile threshold. The P2 signal-strength rule scaled into a long position 5 days before entry, capturing the sharp 10.5% October 13 rally. The surrounding GFC trade cluster (3,756–3,796 in the log) shows the rule is not magic — it took −2.3% losses on the initial September leg down — but the net across the crisis window is strongly positive, which is the payoff for being counter-cyclical when it counts.
"""


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency | Notes |
|:---------|:-------|:-------|:----------|:------|
| **Fed Funds Rate** | FRED | DFF | Daily | Effective rate; full history from 1954 |
| **3M T-Bill (Secondary Market)** | FRED | DTB3 | Daily | Risk-free short rate |
| **TED Spread (for overlap calibration)** | FRED | TEDRATE | Daily | LIBOR-based; ends January 2022 |
| **S&P 500 (Target)** | Yahoo Finance | SPY | Daily | Adjusted close |
| **VIX** | Yahoo Finance | ^VIX | Daily | Control variable |
| **10Y Treasury** | FRED | DGS10 | Daily | For yield-curve control |

*Scope discipline (ECON-SD).* Only DFF and DTB3 are in-scope primary signals.
TEDRATE is used only for overlap-period validity check (r = +0.63 with DFF-DTB3).
"""

_INDICATOR_CONSTRUCTION_MD = """
**Core indicator.** `DFF_TED_t = DFF_t − DTB3_t`, in percentage points, daily.
Sample: 1993-01-04 onwards, ~8,589 daily observations as of the 2026-03-14 cutoff.

**Derived signals used in the tournament (10 total):**

- **Level** — raw spread value.
- **Z-score (126d, 252d)** — rolling-window standardisation.
- **Rate of Change (21d, 63d)** — proportional change; captures acceleration/easing.
- **Momentum (21d, 63d)** — differenced level; directional shift.
- **Percentile rank** — today's spread as percentile of the 252-day trailing distribution.
- **Realised volatility** — rolling std of daily spread changes.
- **Stress dummy** — binary indicator for the upper quartile of the full-sample distribution.

Rate-of-change variants again dominate the leaderboard. With 30+ years of data, the RoC-over-level pattern is especially well-documented here — the absolute level of DFF-TED varies hugely across Fed regimes (zero-rate era vs 1990s-2000s norm), making level-based rules prone to breaking across regime changes.
"""

_METHODS_TABLE_MD = """
| Method | Question It Answers | Key Parameters |
|:-------|:--------------------|:--------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline test for DFF-TED ↔ SPY link |
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

See `results/dff_ted_spy/winner_summary.json` for the canonical winner.
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
        "ADF statistic −3.908 (p = 0.0020) — stationary. "
        "IS/OOS split: 1993-01 → 2017-12 / 2018-01 onwards (~8 years OOS, "
        "including COVID and the 2022-23 rate-hiking cycle)."
    ),
    plain_english=(
        "We constructed a 30-year daily spread (Fed Funds minus 3-month T-Bill) "
        "from FRED, validated it against the official TED spread in the overlap "
        "window, derived ten measurement variants, ran the standard econometric "
        "battery, and then held a ~991-combination tournament to find the best "
        "out-of-sample rule. Because this variant spans multiple crises, the "
        "results are the most statistically reliable of the three."
    ),
)
