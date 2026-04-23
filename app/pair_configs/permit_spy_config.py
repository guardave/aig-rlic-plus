"""PERMIT × SPY pair configuration (Rule APP-PT1).

Wave 10I.A migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/7_permit_spy_*.py before this commit.
Run `git log --follow app/pages/7_permit_spy_story.py` to see the
pre-migration content.

Pair ID: permit_spy  (legacy Pair #3 — Building Permits → SPY)
Winner (per docs/pair_execution_history.md): OOS Sharpe 1.45 vs 0.90 B&H SPY.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Building Permits as an Economic Leading Indicator for Equity"
    PAGE_SUBTITLE = (
        "Do Building Permits, the most forward-looking housing indicator, "
        "predict S&P 500 returns?"
    )

    HEADLINE_H2 = (
        "## Building Permits as a leading macro signal for SPY — OOS Sharpe vs buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for permit_spy — "
        "port from app/pages/7_permit_spy_story.py"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A): WHERE_THIS_FITS for permit_spy"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A): ONE_SENTENCE_THESIS for permit_spy — "
        "port from app/pages/7_permit_spy_story.py"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A): KPI_CAPTION for permit_spy"
    )

    HERO_TITLE = "Building Permits vs. S&P 500 Over the Business Cycle"
    HERO_CHART_NAME = "permit_spy_hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A): HERO_CAPTION for permit_spy — "
        "port from app/pages/7_permit_spy_story.py"
    )

    REGIME_TITLE = "What History Shows: SPY Returns by Building-Permit Regime"
    REGIME_CHART_NAME = "permit_spy_regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A): REGIME_CAPTION for permit_spy — "
        "port from app/pages/7_permit_spy_story.py"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_1 for permit_spy — "
        "port from app/pages/7_permit_spy_story.py (Why Permits Lead the Cycle)"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_2 for permit_spy — "
        "port from app/pages/7_permit_spy_story.py (Nuance / Limits)"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A): SCOPE_NOTE for permit_spy"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A): TRANSITION_TEXT for permit_spy — "
        "port from app/pages/7_permit_spy_story.py"
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for permit_spy Correlation"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for permit_spy Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for permit_spy Correlation"
    ),
    chart_name="permit_spy_correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for permit_spy Correlation — "
        "port from app/pages/7_permit_spy_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for permit_spy Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for permit_spy Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for permit_spy Correlation"
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for permit_spy Local Projections"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for permit_spy Local Projections"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for permit_spy Local Projections"
    ),
    chart_name="permit_spy_local_projections",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for permit_spy Local Projections — "
        "port from app/pages/7_permit_spy_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for permit_spy Local Projections"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for permit_spy Local Projections"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for permit_spy Local Projections"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A): overview for permit_spy Evidence — "
        "port from app/pages/7_permit_spy_evidence.py"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A): plain_english for permit_spy Evidence"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A): tournament_intro for permit_spy"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A): transition for permit_spy Evidence"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating Permit Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested hundreds of strategy combinations to find the most robust way "
        "to time SPY exposure using Building Permits."
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for permit_spy Strategy"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A): SIGNAL_RULE_MD for permit_spy — "
        "port from app/pages/7_permit_spy_strategy.py"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A): HOW_SIGNAL_IS_GENERATED_MD for permit_spy"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A): MANUAL_USE_MD for permit_spy"
    )

    # No equity_curves / drawdown / walk_forward charts exist for permit_spy
    # on disk (as of Wave 10I.A). Template falls back to "chart pending" for
    # those surfaces — pre-existing data gap, not a regression.
    TOURNAMENT_SCATTER_CHART_NAME = "permit_spy_tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A): CAVEATS_MD for permit_spy — "
        "port from app/pages/7_permit_spy_strategy.py"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A): TRADE_LOG_EXAMPLE_MD for permit_spy"
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Building Permits (Total, SA)** | FRED | PERMIT | Monthly |
| **S&P 500 (Target)** | Yahoo Finance | SPY | Daily → Monthly |
| **NBER Recession Dates** | FRED / NBER | USREC | Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |
| **Treasury yields** | FRED | DGS10 | Daily → Monthly |

*Scope discipline (ECON-SD).* Only PERMIT and SPY are in-scope primary signals.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A): INDICATOR_CONSTRUCTION_MD for permit_spy — "
    "port from app/pages/7_permit_spy_methodology.py"
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|:-------|:--------------------|:----------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline test for Permit-SPY link |
| Local Projections (Jordà) | Full dynamic path of SPY response to Permit shock | Robust IRF without VAR restrictions |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals** | Permit level, YoY growth, MoM change, z-score, 3M/6M momentum |
| **Threshold methods** | Fixed IS percentile, rolling percentile, rolling z-score |
| **Strategies** | Long/Cash (P1), Signal-Strength (P2), Long/Short (P3) |
| **Lead times** | L0 through L6 |
| **Orientation** | Pro-cyclical (rising permits → bullish SPY) |

Winner (per docs/pair_execution_history.md): OOS Sharpe 1.45 vs 0.90 B&H SPY.
"""

_REFERENCES_MD = """
- Stock, J. H., & Watson, M. W. (1989). New indexes of coincident and leading economic indicators. *NBER Macroeconomics Annual*, 4, 351–394.
- Case, K. E., & Shiller, R. J. (2003). Is there a bubble in the housing market? *Brookings Papers on Economic Activity*, 2003(2), 299–362.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23–49.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "# TODO Ray (Wave 10I.A): sample_period_note for permit_spy"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A): plain_english for permit_spy Methodology"
    ),
)
