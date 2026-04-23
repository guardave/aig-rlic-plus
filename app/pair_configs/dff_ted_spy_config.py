"""DFF-TED × SPY pair configuration (Rule APP-PT1).

Wave 10I.A Part 2 migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/6_ted_variants_*.py before this commit
(tab B: "DFF-DTB3 (Fed Funds)" of the 3-in-1 TED composite page).

Structural fields (chart names, data-source table, tournament design,
references, methods table) filled in-place by Ace from the legacy composite.
Narrative prose left as TODO stubs for Ray (RES-NR1 owner).

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
        "# TODO Ray (Wave 10I.A Part 2): PLAIN_ENGLISH for dff_ted_spy — "
        "port from app/pages/6_ted_variants_story.py (Variant B framing, lines 52-53)"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A Part 2): WHERE_THIS_FITS for dff_ted_spy"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A Part 2): ONE_SENTENCE_THESIS for dff_ted_spy"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): KPI_CAPTION for dff_ted_spy"
    )

    HERO_TITLE = "Fed Funds - 3M T-Bill (1993-2025) vs. S&P 500"
    HERO_CHART_NAME = "dff_ted_spy_hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): HERO_CAPTION for dff_ted_spy — "
        "port from app/pages/6_ted_variants_story.py line 73 "
        "(dot-com, GFC, COVID funding-stress episodes)"
    )

    REGIME_TITLE = "What History Shows: SPY Returns by DFF-TED Stress Regime"
    REGIME_CHART_NAME = "dff_ted_spy_regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): REGIME_CAPTION for dff_ted_spy — "
        "port from app/pages/6_ted_variants_story.py line 93 "
        "(Sharpe by spread quartile across 30+ years)"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A Part 2): NARRATIVE_SECTION_1 for dff_ted_spy — "
        "port from app/pages/6_ted_variants_story.py lines 36-46 "
        "(TED spread concept, why DFF-DTB3 is a valid TED proxy: r=+0.63 to TEDRATE)"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A Part 2): NARRATIVE_SECTION_2 for dff_ted_spy — "
        "author Variant-B-specific framing: longest continuous history, "
        "no splicing assumptions, most conservative choice of the three variants"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A Part 2): SCOPE_NOTE for dff_ted_spy — "
        "author scope-discipline note (DFF and DTB3 are the in-scope primary signals)"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A Part 2): TRANSITION_TEXT for dff_ted_spy — "
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
        "# TODO Ray (Wave 10I.A Part 2): method_theory for dff_ted_spy Correlation"
    ),
    question=(
        "# TODO Ray (Wave 10I.A Part 2): question for dff_ted_spy Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A Part 2): how_to_read for dff_ted_spy Correlation"
    ),
    chart_name="dff_ted_spy_correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A Part 2): chart_caption for dff_ted_spy Correlation — "
        "port from app/pages/6_ted_variants_evidence.py lines 31-37"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A Part 2): observation for dff_ted_spy Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A Part 2): interpretation for dff_ted_spy Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A Part 2): key_message for dff_ted_spy Correlation"
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "# TODO Ray (Wave 10I.A Part 2): method_theory for dff_ted_spy Local Projections"
    ),
    question=(
        "# TODO Ray (Wave 10I.A Part 2): question for dff_ted_spy Local Projections"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A Part 2): how_to_read for dff_ted_spy Local Projections"
    ),
    chart_name="dff_ted_spy_local_projections",
    chart_caption=(
        "# TODO Ray (Wave 10I.A Part 2): chart_caption for dff_ted_spy Local Projections — "
        "port from app/pages/6_ted_variants_evidence.py lines 39-45"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A Part 2): observation for dff_ted_spy Local Projections"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A Part 2): interpretation for dff_ted_spy Local Projections"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A Part 2): key_message for dff_ted_spy Local Projections"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A Part 2): overview for dff_ted_spy Evidence"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A Part 2): plain_english for dff_ted_spy Evidence"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A Part 2): tournament_intro for dff_ted_spy"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A Part 2): transition for dff_ted_spy Evidence"
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
        "# TODO Ray (Wave 10I.A Part 2): PLAIN_ENGLISH for dff_ted_spy Strategy"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): SIGNAL_RULE_MD for dff_ted_spy — "
        "port from app/pages/6_ted_variants_strategy.py winner spotlight "
        "(read results/dff_ted_spy/winner_summary.json for canonical params)"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A Part 2): HOW_SIGNAL_IS_GENERATED_MD for dff_ted_spy"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): MANUAL_USE_MD for dff_ted_spy"
    )

    # No equity_curves / drawdown / walk_forward charts exist on disk for
    # dff_ted_spy (as of Wave 10I.A Part 2). Template falls back to
    # "chart pending" — pre-existing data gap.
    TOURNAMENT_SCATTER_CHART_NAME = "dff_ted_spy_tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A Part 2): CAVEATS_MD for dff_ted_spy — "
        "port from app/pages/6_ted_variants_strategy.py lines 146-152 "
        "(Variant B is the most conservative choice: longest continuous history, "
        "no splicing, but DFF-DTB3 is a proxy not the original LIBOR-TED)"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): TRADE_LOG_EXAMPLE_MD for dff_ted_spy — "
        "author from results/dff_ted_spy/winner_trade_log.csv"
    )


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

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A Part 2): INDICATOR_CONSTRUCTION_MD for dff_ted_spy — "
    "port from app/pages/6_ted_variants_methodology.py (Variant B formula: "
    "DFF - DTB3, 1993-01 onwards, 8,589 daily obs; derived signals: level, "
    "z-score 126d/252d, RoC 21d/63d, momentum 21d/63d, percentile rank)"
)

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
        "# TODO Ray (Wave 10I.A Part 2): sample_period_note for dff_ted_spy — "
        "1993-01 to 2025-12, ~8,589 daily obs; ADF statistic -3.908 (p=0.0020, stationary)"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A Part 2): plain_english for dff_ted_spy Methodology"
    ),
)
