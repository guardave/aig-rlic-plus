"""VIX/VIX3M × SPY pair configuration (Rule APP-PT1).

Wave 10I.A migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/8_vix_vix3m_spy_*.py before this commit.
Run `git log --follow app/pages/8_vix_vix3m_spy_story.py` to see the
pre-migration content.

Pair ID: vix_vix3m_spy  (legacy Pair #11 — VIX term-structure ratio → SPY)
Winner (per docs/pair_execution_history.md): OOS Sharpe 1.13.
Regime context: strongest Q1 vs Q4 spread in the portal
(Q1 Sharpe 6.53 vs Q4 -2.38 — 9-point differential).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: The VIX Term Structure as a Fear Barometer for SPY"
    PAGE_SUBTITLE = (
        "Does the ratio of near-term to medium-term implied volatility predict "
        "S&P 500 returns?"
    )

    HEADLINE_H2 = (
        "## VIX/VIX3M ratio as a volatility-regime signal for SPY — "
        "OOS Sharpe vs buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_story.py"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A): WHERE_THIS_FITS for vix_vix3m_spy"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A): ONE_SENTENCE_THESIS for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_story.py"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A): KPI_CAPTION for vix_vix3m_spy"
    )

    HERO_TITLE = "VIX Term Structure (VIX / VIX3M) vs. S&P 500"
    HERO_CHART_NAME = "vix_vix3m_spy_hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A): HERO_CAPTION for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_story.py"
    )

    REGIME_TITLE = "What History Shows: SPY Returns by VIX/VIX3M Quartile"
    REGIME_CHART_NAME = "vix_vix3m_spy_regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A): REGIME_CAPTION for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_story.py "
        "(Q1 Sharpe 6.53 vs Q4 -2.38 — strongest regime discriminator in portal)"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_1 for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_story.py "
        "(Term-structure mechanics and risk-appetite framing)"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_2 for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_story.py (Nuance / Limits)"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A): SCOPE_NOTE for vix_vix3m_spy"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A): TRANSITION_TEXT for vix_vix3m_spy"
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for vix_vix3m_spy Correlation"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for vix_vix3m_spy Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for vix_vix3m_spy Correlation"
    ),
    chart_name="vix_vix3m_spy_correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for vix_vix3m_spy Correlation — "
        "port from app/pages/8_vix_vix3m_spy_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for vix_vix3m_spy Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for vix_vix3m_spy Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for vix_vix3m_spy Correlation"
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for vix_vix3m_spy Local Projections"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for vix_vix3m_spy Local Projections"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for vix_vix3m_spy Local Projections"
    ),
    chart_name="vix_vix3m_spy_local_projections",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for vix_vix3m_spy Local Projections — "
        "port from app/pages/8_vix_vix3m_spy_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for vix_vix3m_spy Local Projections"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for vix_vix3m_spy Local Projections"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for vix_vix3m_spy Local Projections"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A): overview for vix_vix3m_spy Evidence"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A): plain_english for vix_vix3m_spy Evidence"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A): tournament_intro for vix_vix3m_spy"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A): transition for vix_vix3m_spy Evidence"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating VIX Term-Structure Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested hundreds of strategy combinations to find the most robust way "
        "to time SPY exposure using the VIX/VIX3M ratio."
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for vix_vix3m_spy Strategy"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A): SIGNAL_RULE_MD for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_strategy.py"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A): HOW_SIGNAL_IS_GENERATED_MD for vix_vix3m_spy"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A): MANUAL_USE_MD for vix_vix3m_spy"
    )

    # No equity_curves / drawdown / walk_forward charts on disk — same
    # data gap as permit_spy. Template renders "chart pending" for those.
    TOURNAMENT_SCATTER_CHART_NAME = "vix_vix3m_spy_tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A): CAVEATS_MD for vix_vix3m_spy — "
        "port from app/pages/8_vix_vix3m_spy_strategy.py"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A): TRADE_LOG_EXAMPLE_MD for vix_vix3m_spy"
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **VIX (1-month implied vol)** | Yahoo Finance / CBOE | ^VIX | Daily |
| **VIX3M (3-month implied vol)** | Yahoo Finance / CBOE | ^VIX3M | Daily |
| **S&P 500 (Target)** | Yahoo Finance | SPY | Daily → Monthly |
| **NBER Recession Dates** | FRED / NBER | USREC | Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |

*Scope discipline (ECON-SD).* Only the VIX/VIX3M ratio and SPY are in-scope
primary signals. VIX3M series begins 2007-12, defining the sample start.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A): INDICATOR_CONSTRUCTION_MD for vix_vix3m_spy — "
    "port from app/pages/8_vix_vix3m_spy_methodology.py "
    "(ratio = VIX / VIX3M; >1 = backwardation / stress; <1 = contango / calm)"
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|:-------|:--------------------|:----------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline VIX/VIX3M-SPY test |
| Local Projections (Jordà) | Full dynamic path of SPY response to ratio shock | Robust IRF without VAR restrictions |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals** | VIX/VIX3M level, z-score, 3M/6M momentum, contango dummy |
| **Threshold methods** | Fixed percentile (p25/p50/p75), rolling percentile, rolling z-score |
| **Strategies** | Long/Cash (P1), Signal-Strength (P2), Long/Short (P3) |
| **Lead times** | L0 (daily signal — no lag required) |
| **Orientation** | Countercyclical (backwardation / ratio > 1 → reduce SPY exposure) |

Winner (per docs/pair_execution_history.md): OOS Sharpe 1.13. Regime
spread: Q1 Sharpe 6.53 vs Q4 -2.38 — strongest regime discriminator
observed in the portal.
"""

_REFERENCES_MD = """
- Whaley, R. E. (2000). The investor fear gauge. *Journal of Portfolio Management*, 26(3), 12–17.
- Bollerslev, T., Tauchen, G., & Zhou, H. (2009). Expected stock returns and variance risk premia. *Review of Financial Studies*, 22(11), 4463–4492.
- Johnson, T. L. (2017). Risk premia and the VIX term structure. *Journal of Financial and Quantitative Analysis*, 52(6), 2461–2490.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "# TODO Ray (Wave 10I.A): sample_period_note for vix_vix3m_spy — "
        "VIX3M begins 2007-12; short OOS window caveat applies"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A): plain_english for vix_vix3m_spy Methodology"
    ),
)
