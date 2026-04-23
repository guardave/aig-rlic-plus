"""SOFR-TED × SPY pair configuration (Rule APP-PT1).

Wave 10I.A Part 2 migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/6_ted_variants_*.py before this commit
(tab A: "SOFR-DTB3" of the 3-in-1 TED composite page).

Structural fields (chart names, data-source table, tournament design,
references, methods table) filled in-place by Ace from the legacy composite.
Narrative prose left as TODO stubs for Ray (RES-NR1 owner).

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
        "# TODO Ray (Wave 10I.A Part 2): PLAIN_ENGLISH for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_story.py (Variant A framing, lines 49-51)"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A Part 2): WHERE_THIS_FITS for sofr_ted_spy"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A Part 2): ONE_SENTENCE_THESIS for sofr_ted_spy"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): KPI_CAPTION for sofr_ted_spy"
    )

    HERO_TITLE = "SOFR - 3M T-Bill (2018-2025) vs. S&P 500"
    HERO_CHART_NAME = "sofr_ted_spy_hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): HERO_CAPTION for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_story.py line 69 "
        "(COVID March-2020 repo-stress spike framing)"
    )

    REGIME_TITLE = "What History Shows: SPY Returns by SOFR-TED Stress Regime"
    REGIME_CHART_NAME = "sofr_ted_spy_regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): REGIME_CAPTION for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_story.py line 93 "
        "(Sharpe by spread-quartile, Q4 = highest stress)"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A Part 2): NARRATIVE_SECTION_1 for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_story.py lines 36-46 "
        "(What Is the TED Spread? + LIBOR vs SOFR distinction — secured repo)"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A Part 2): NARRATIVE_SECTION_2 for sofr_ted_spy — "
        "author the Variant-A-specific caveats: only ~2,000 observations, "
        "post-LIBOR regime only (2018-present), high-variance OOS"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A Part 2): SCOPE_NOTE for sofr_ted_spy — "
        "author scope-discipline note (SOFR and DTB3 are the in-scope primary signals)"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A Part 2): TRANSITION_TEXT for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_story.py lines 99-101"
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "# TODO Ray (Wave 10I.A Part 2): method_theory for sofr_ted_spy Correlation"
    ),
    question=(
        "# TODO Ray (Wave 10I.A Part 2): question for sofr_ted_spy Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A Part 2): how_to_read for sofr_ted_spy Correlation"
    ),
    chart_name="sofr_ted_spy_correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A Part 2): chart_caption for sofr_ted_spy Correlation — "
        "port from app/pages/6_ted_variants_evidence.py lines 31-37"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A Part 2): observation for sofr_ted_spy Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A Part 2): interpretation for sofr_ted_spy Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A Part 2): key_message for sofr_ted_spy Correlation"
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "# TODO Ray (Wave 10I.A Part 2): method_theory for sofr_ted_spy Local Projections"
    ),
    question=(
        "# TODO Ray (Wave 10I.A Part 2): question for sofr_ted_spy Local Projections"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A Part 2): how_to_read for sofr_ted_spy Local Projections"
    ),
    chart_name="sofr_ted_spy_local_projections",
    chart_caption=(
        "# TODO Ray (Wave 10I.A Part 2): chart_caption for sofr_ted_spy Local Projections — "
        "port from app/pages/6_ted_variants_evidence.py lines 39-45"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A Part 2): observation for sofr_ted_spy Local Projections"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A Part 2): interpretation for sofr_ted_spy Local Projections"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A Part 2): key_message for sofr_ted_spy Local Projections"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A Part 2): overview for sofr_ted_spy Evidence"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A Part 2): plain_english for sofr_ted_spy Evidence"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A Part 2): tournament_intro for sofr_ted_spy"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A Part 2): transition for sofr_ted_spy Evidence"
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
        "# TODO Ray (Wave 10I.A Part 2): PLAIN_ENGLISH for sofr_ted_spy Strategy"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): SIGNAL_RULE_MD for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_strategy.py winner spotlight "
        "(read results/sofr_ted_spy/winner_summary.json for canonical params)"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A Part 2): HOW_SIGNAL_IS_GENERATED_MD for sofr_ted_spy"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): MANUAL_USE_MD for sofr_ted_spy"
    )

    # No equity_curves / drawdown / walk_forward charts exist for sofr_ted_spy
    # on disk (as of Wave 10I.A Part 2). Template falls back to "chart pending"
    # for those surfaces — pre-existing data gap, not a regression.
    TOURNAMENT_SCATTER_CHART_NAME = "sofr_ted_spy_tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A Part 2): CAVEATS_MD for sofr_ted_spy — "
        "port from app/pages/6_ted_variants_strategy.py lines 146-152 "
        "(Variant A: only 3 years OOS, high variance, generalization risk)"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): TRADE_LOG_EXAMPLE_MD for sofr_ted_spy — "
        "author from results/sofr_ted_spy/winner_trade_log.csv"
    )


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

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A Part 2): INDICATOR_CONSTRUCTION_MD for sofr_ted_spy — "
    "port from app/pages/6_ted_variants_methodology.py (Variant A formula: "
    "SOFR - DTB3, 2018-04 onwards, 2,022 daily observations; derived signals: "
    "level, z-score 126d/252d, RoC 21d/63d, momentum, percentile rank, realized vol)"
)

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
        "# TODO Ray (Wave 10I.A Part 2): sample_period_note for sofr_ted_spy — "
        "2018-04 to 2025-12, ~2,022 daily obs; ADF statistic -5.116 (p≈0.0000, stationary)"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A Part 2): plain_english for sofr_ted_spy Methodology"
    ),
)
