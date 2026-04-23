"""SOFR-TED × SPY pair configuration (Rule APP-PT1).

Wave 10I.A Part 3b — Ray narrative port (commit supersedes Part 2 stubs).
Source content ported from the deleted 3-in-1 TED composite
(app/pages/6_ted_variants_*.py pre-commit a9d493e~1), re-authored
pair-specifically for Variant A.

Pair ID: sofr_ted_spy  (Variant A — SOFR minus 3M T-Bill, 2018-present)
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: SOFR-TED Spread as an Equity Signal"
    PAGE_SUBTITLE = (
        "Does the modern (SOFR-based) funding-stress measure predict S&P 500 returns?"
    )

    HEADLINE_H2 = (
        "## SOFR - DTB3 as a post-LIBOR funding-stress signal for SPY — "
        "OOS Sharpe vs buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "The SOFR-TED spread is the modern successor to the classic TED spread. "
        "It measures the gap between the Secured Overnight Financing Rate (SOFR) — "
        "what banks pay for overnight cash backed by Treasury collateral — and the "
        "3-month T-Bill yield. When the gap widens, it tells us the repo plumbing "
        "of the financial system is under stress. When it narrows, funding conditions "
        "are calm. We test whether this post-2018 indicator helps time the S&P 500."
    )

    WHERE_THIS_FITS = (
        "This is the *modern, pure* variant in our three-way TED study. It uses the "
        "post-LIBOR benchmark that regulators adopted in 2018, so it captures repo and "
        "collateral stress accurately — but only for the short post-2018 window. The "
        "two sibling variants (DFF-TED and Spliced TED) trade some purity for a much "
        "longer sample period; this one trades sample length for definitional cleanness."
    )

    ONE_SENTENCE_THESIS = (
        "High or rising SOFR-TED spreads signal repo-market stress that has historically "
        "been followed by softer SPY returns over the next 1–3 weeks."
    )

    KPI_CAPTION = (
        "Winner strategy KPIs: OOS Sharpe 1.89 on 3 years of out-of-sample data "
        "(2023-01 onwards) — strong headline, but confidence intervals are wide "
        "given only ~2,000 daily observations."
    )

    HERO_TITLE = "SOFR - 3M T-Bill (2018-2025) vs. S&P 500"
    HERO_CHART_NAME = "sofr_ted_spy_hero"
    HERO_CAPTION = (
        "SOFR minus 3M T-Bill, 2018-2025. Note the extreme spike in March 2020 — "
        "COVID-era repo stress — and the more modest widening during the 2022-2023 "
        "rate-hiking cycle. Most of the time the spread sits in a narrow band."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by SOFR-TED Stress Regime"
    REGIME_CHART_NAME = "sofr_ted_spy_regime_stats"
    REGIME_CAPTION = (
        "SPY Sharpe ratios sorted by SOFR-TED quartile. Q1 = calmest funding "
        "conditions; Q4 = most stressed. Counter-cyclical pattern: equity risk-adjusted "
        "returns are systematically higher in low-stress quartiles."
    )

    NARRATIVE_SECTION_1 = """
### What Is the TED Spread?

The TED spread measures the gap between what banks pay to borrow short-term cash and the risk-free government rate. When banks trust each other and collateral is plentiful, this gap is small (typically 10–30 basis points). When fear rises — because of credit concerns, liquidity squeezes, or systemic risk — the gap widens, sometimes dramatically.

The classic TED spread used LIBOR (the London Interbank Offered Rate) as the bank-borrowing leg. After the LIBOR manipulation scandal, U.S. regulators replaced it with SOFR (the Secured Overnight Financing Rate) in 2018. Crucially, SOFR and LIBOR are *not* the same thing:

- **LIBOR** measured *unsecured* interbank lending — it embedded bank credit risk.
- **SOFR** measures *secured* overnight repo backed by Treasury collateral — so it reflects liquidity and collateral-market stress rather than credit risk per se.

For this Variant A surface, we take the purist view: measure today's funding stress with today's benchmark (SOFR), accept the short history, and let the 2018-onwards data speak.
"""

    NARRATIVE_SECTION_2 = """
### Caveats Specific to Variant A

The SOFR-DTB3 series has only existed since April 2018, giving roughly 2,000 daily observations and only ~3 years of out-of-sample data after the 2022 in-sample cutoff. That means:

- **Confidence intervals around the OOS Sharpe are wide.** A headline Sharpe of 1.89 is attractive, but the small sample means the true risk-adjusted return could realistically lie anywhere from ~1.0 to ~2.5.
- **One regime only.** The entire sample is post-LIBOR-transition, post-QE-4, and spans only one Fed hiking cycle. We cannot test how the signal behaves in dot-com or GFC-type stress.
- **Structural purity comes at a cost.** For a longer-history view, consult the sibling DFF-TED (Variant B) and Spliced TED (Variant C) surfaces.
"""

    SCOPE_NOTE = (
        "Scope discipline: only SOFR and DTB3 are the in-scope primary signals for "
        "this pair. VIX, 10Y yields, and yield-curve slopes appear only as regression "
        "controls, never as standalone trading signals."
    )

    TRANSITION_TEXT = (
        "The regime view suggests a counter-cyclical pattern. The evidence page "
        "digs into the econometric detail — correlation structure and local-projection "
        "impulse responses — to test whether the pattern survives formal specification."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson and rolling correlation quantify the *linear* co-movement between "
        "the SOFR-TED spread (and its derived signals) and forward SPY returns "
        "across multiple horizons. It is the first, simplest filter: if no "
        "contemporaneous or lagged co-movement exists, a predictive relationship "
        "is unlikely to be found by more elaborate methods."
    ),
    question=(
        "Is there a stable, directionally consistent linear relationship between "
        "SOFR-TED stress and subsequent SPY returns at 5-, 21-, and 63-day horizons?"
    ),
    how_to_read=(
        "Darker blue cells indicate stronger negative correlation (stress up → SPY "
        "returns down). Darker red indicates positive correlation. Cells near zero "
        "mean no linear relationship at that horizon."
    ),
    chart_name="sofr_ted_spy_correlations",
    chart_caption=(
        "Correlation heatmap of SOFR-TED signals versus forward SPY returns. "
        "Negative-signed cells are consistent with the counter-cyclical thesis."
    ),
    observation=(
        "Rate-of-change (RoC) signals show modestly negative correlations with "
        "forward SPY returns, strongest at the 21-day horizon. Level and z-score "
        "signals are weaker and noisier — consistent with the short sample."
    ),
    interpretation=(
        "In the post-2018 sample the SOFR-TED spread carries a weak but directionally "
        "correct predictive signal. RoC dominates level — changes in funding stress "
        "matter more than its absolute value, which is what one would expect when the "
        "sample spans a narrow range of regimes."
    ),
    key_message=(
        "Negative signs are there, magnitudes are small. The correlation view is "
        "supportive but not decisive — formal impulse-response analysis is needed."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "Local projections (Jordà 2005) estimate the dynamic response of SPY returns "
        "to a shock in the SOFR-TED spread, horizon-by-horizon, without imposing a "
        "VAR's parametric structure. HAC (Newey-West) standard errors correct for "
        "the overlapping-horizon autocorrelation."
    ),
    question=(
        "If the SOFR-TED spread widens by one standard deviation today, what is the "
        "expected path of SPY returns over the following 5, 21, and 63 days?"
    ),
    how_to_read=(
        "Each point is the estimated SPY return response at that horizon after a "
        "+1σ SOFR-TED shock today. Shaded bands are HAC 95% confidence intervals. "
        "If the band excludes zero, the response is statistically significant."
    ),
    chart_name="sofr_ted_spy_local_projections",
    chart_caption=(
        "Impulse-response of SPY returns to a +1σ SOFR-TED spread shock. Points "
        "below zero indicate the counter-cyclical response predicted by the thesis."
    ),
    observation=(
        "Point estimates are negative at the 5- and 21-day horizons — the expected "
        "sign. At 63 days the effect fades. Confidence bands are wide, however, "
        "reflecting the short sample."
    ),
    interpretation=(
        "The impulse-response is economically meaningful but statistically fragile. "
        "The sign and decay pattern are consistent with the thesis; the precision "
        "is limited by the ~2,000-observation sample."
    ),
    key_message=(
        "Direction and decay are right; precision is weak. This is the single "
        "biggest caveat to the attractive OOS Sharpe — treat point estimates with care."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We test the SOFR-TED → SPY relationship with two complementary methods: "
        "correlation analysis (model-free, multiple horizons) and Jordà local "
        "projections (impulse-response, HAC-corrected). Both target the same "
        "question from different angles."
    ),
    "plain_english": (
        "Method 1 asks: do the two series move together? Method 2 asks: if funding "
        "stress jumps today, what happens to the S&P over the following weeks?"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "Econometric evidence points in the right direction; the next step is to "
        "ask whether a disciplined trading rule built on this signal actually "
        "outperforms buy-and-hold. The strategy page reports the tournament winner."
    ),
    "transition": (
        "Continue to the Strategy page for the tournament winner and its KPIs."
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating SOFR-TED Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested ~991 strategy combinations on SOFR - DTB3 (Variant A) "
        "to find the most robust funding-stress timing rule."
    )

    PLAIN_ENGLISH = (
        "From the tournament of roughly a thousand combinations of signal × threshold × "
        "strategy × lead time, the winner is a rule that watches the 63-day rate of "
        "change in SOFR-TED. When the RoC falls into the lowest 25% of historical "
        "values (funding stress easing), the rule goes fully long SPY with a 10-day "
        "lead; otherwise it sits in cash."
    )

    SIGNAL_RULE_MD = """
**Winner (from `results/sofr_ted_spy/winner_summary.json`):**

| Field | Value |
|:---|:---|
| Signal | Spread 63-Day Rate of Change (`spread_roc_63d`) |
| Threshold | 25th percentile, fixed in-sample (`T1_p25`) |
| Strategy | Long / Cash (P1) |
| Lead time | 10 days |
| Direction | Counter-cyclical — go long when signal is *below* the 25th percentile |
| OOS Sharpe | **1.89** |
| OOS annualised return | **+8.15%** |
| Max drawdown | **−3.58%** |
| Annual turnover | ~23 round-trips |
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
1. Compute the SOFR-TED spread (`SOFR − DTB3`) daily.
2. Compute its 63-day rate of change: `roc_63 = spread_t / spread_{t-63} − 1`.
3. Fix the 25th-percentile threshold on the in-sample window (2018-04 to 2022-12).
4. Each day, compare today's `roc_63` to that fixed threshold.
5. If below the threshold (stress easing), enter Long SPY with a 10-day lead lag; otherwise hold cash.
"""

    MANUAL_USE_MD = """
A human operator wanting to replicate the rule can:

1. Pull the latest SOFR and DTB3 values from FRED.
2. Update a rolling 63-day RoC series.
3. Compare today's value to the fixed 25th-percentile benchmark (published in the methodology appendix).
4. If below, plan a 10-business-day forward switch into SPY; if above, plan the switch into cash.
5. Review monthly — annual turnover is low (~23 trades), so the rule does not require daily monitoring.
"""

    TOURNAMENT_SCATTER_CHART_NAME = "sofr_ted_spy_tournament_scatter"

    CAVEATS_MD = """
- **Short out-of-sample window.** Only ~3 years of OOS data (2023-01 onwards). The 1.89 Sharpe carries a wide confidence interval.
- **One regime only.** Entire sample is post-LIBOR, post-QE-4. Behaviour in a dot-com- or GFC-type stress event is untested for this specific variant.
- **Generalisation risk.** With ~2,000 daily observations, the tournament may have fit idiosyncratic features of the 2023-2025 period. Cross-check against the DFF-TED and Spliced-TED sibling variants before acting.
- **Missing artefacts.** `equity_curves`, `drawdown`, and `walk_forward` charts are not yet generated for this pair (tracked under BL-CHART-GAPS-LEGACY); the Strategy-page Performance tab will show "chart pending" placeholders.
"""

    TRADE_LOG_EXAMPLE_MD = """
**Crisis-era trade citation (COVID repo-stress episode).**

From `results/sofr_ted_spy/winner_trade_log.csv`:

| Entry | Exit | Direction | Holding | Return |
|:---|:---|:---|:---:|:---:|
| 2020-05-12 | 2020-07-01 | Long | 50 days | **+8.80%** |

This is the winning rule's single largest trade in the log. It was entered after the March-2020 repo-stress spike had peaked and SOFR-TED's 63-day RoC rolled back into the bottom quartile — i.e. stress was visibly easing. The 10-day lead lag placed entry in mid-May, capturing the bulk of the post-crisis recovery rally. Behaviour during the March 2020 spike itself (trade id 46: `2020-03-05 → 2020-03-11`, −9.29%) illustrates the counter-cyclical cost: the rule is briefly caught the wrong way when stress *first* erupts, then recoups as stress mean-reverts.
"""


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency | Notes |
|:---------|:-------|:-------|:----------|:------|
| **SOFR** | FRED | SOFR | Daily | Starts April 2018; occasional quarter-end spikes |
| **3M T-Bill (Secondary Market)** | FRED | DTB3 | Daily | Risk-free short rate |
| **S&P 500 (Target)** | Yahoo Finance | SPY | Daily | Adjusted close |
| **VIX** | Yahoo Finance | ^VIX | Daily | Control variable |
| **10Y Treasury** | FRED | DGS10 | Daily | For yield-curve control |

*Scope discipline (ECON-SD).* Only SOFR and DTB3 are in-scope primary signals.
Controls (VIX, yield spread) are used only in regression controls, not as trading
signals.
"""

_INDICATOR_CONSTRUCTION_MD = """
**Core indicator.** `SOFR_TED_t = SOFR_t − DTB3_t`, in percentage points, daily.
Sample: 2018-04-02 onwards, ~2,022 daily observations as of the 2026-03-14 cutoff.

**Derived signals used in the tournament (10 total):**

- **Level** — raw spread value.
- **Z-score (126d, 252d)** — rolling-window standardisation; isolates "unusual" levels.
- **Rate of Change (21d, 63d)** — proportional change over the window; captures stress acceleration/easing.
- **Momentum (21d, 63d)** — differenced level; directional shift in absolute terms.
- **Percentile rank** — today's spread as a percentile of its 252-day trailing distribution.
- **Realised volatility** — rolling std of daily spread changes; regime-volatility proxy.
- **Stress dummy** — binary indicator (above historical 75th percentile).

Rate-of-change and momentum variants dominate the tournament leaderboard, consistent with the finding (replicated across TED variants) that *changes* in funding stress carry more predictive information than the level itself, especially in a sample with a relatively narrow range of absolute spread values.
"""

_METHODS_TABLE_MD = """
| Method | Question It Answers | Key Parameters |
|:-------|:--------------------|:--------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline test for SOFR-TED ↔ SPY link |
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
| **IS / OOS split** | 2018-04 → 2022-12 / 2023-01 → present |

See `results/sofr_ted_spy/winner_summary.json` for the canonical winner.
"""

_REFERENCES_MD = """
- Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007-2008. *Journal of Economic Perspectives*, 23(1), 77-100.
- Duffie, D., & Stein, J. C. (2015). Reforming LIBOR and other financial market benchmarks. *Journal of Economic Perspectives*, 29(2), 191-212.
- ARRC (2017). *The ARRC selects a broad Repo rate as its preferred alternative reference rate.* Federal Reserve Bank of New York.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161-182.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Sample period: 2018-04 to 2025-12, ~2,022 daily observations. "
        "ADF statistic −5.116 (p ≈ 0.0000) — stationary. "
        "IS/OOS split: 2018-04 → 2022-12 / 2023-01 onwards (~3 years OOS)."
    ),
    plain_english=(
        "We used daily SOFR and 3-month T-Bill data from FRED (2018-2025), formed "
        "the spread, and derived ten measurement variants (level, rates of change, "
        "z-scores, momentum). We ran linear, impulse-response, and quantile tests "
        "to confirm a predictive link, then held a tournament of ~991 rule "
        "combinations to find the best out-of-sample risk-adjusted return. "
        "All inputs are public and auditable."
    ),
)
