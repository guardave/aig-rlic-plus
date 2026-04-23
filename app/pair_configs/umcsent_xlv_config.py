"""UMCSENT × XLV pair configuration (Rule APP-PT1).

Wave 10I.A migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/10_umcsent_xlv_*.py before this commit.
Run `git log --follow app/pages/10_umcsent_xlv_story.py` to see the
pre-migration content.

APP-TL1 note: `results/umcsent_xlv/winner_trades_broker_style.csv` is
present (shipped Wave 10H.2, commit 2c11046). Ray should author
TRADE_LOG_EXAMPLE_MD from that file during narrative port.

Pair ID: umcsent_xlv  (richest hand-written pair — 1,563 legacy lines)
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Consumer Sentiment and the Healthcare Sector"
    PAGE_SUBTITLE = (
        "Does University of Michigan consumer sentiment predict returns in "
        "the defensive healthcare sector (XLV)?"
    )

    HEADLINE_H2 = (
        "## UMCSENT as a contrarian signal for XLV — OOS Sharpe vs buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_story.py"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A): WHERE_THIS_FITS for umcsent_xlv"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A): ONE_SENTENCE_THESIS for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_story.py"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A): KPI_CAPTION for umcsent_xlv"
    )

    HERO_TITLE = "Consumer Sentiment vs. Healthcare Sector (XLV)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A): HERO_CAPTION for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_story.py"
    )

    REGIME_TITLE = "What History Shows: XLV Returns by Consumer-Sentiment Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A): REGIME_CAPTION for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_story.py"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_1 for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_story.py "
        "(Why Sentiment Matters for Defensive Sectors — richest Story prose in the portal)"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_2 for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_story.py (Nuance / Limits)"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A): SCOPE_NOTE for umcsent_xlv"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A): TRANSITION_TEXT for umcsent_xlv"
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 4 method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for umcsent_xlv Correlation"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for umcsent_xlv Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for umcsent_xlv Correlation"
    ),
    chart_name="correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for umcsent_xlv Correlation — "
        "port from app/pages/10_umcsent_xlv_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for umcsent_xlv Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for umcsent_xlv Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for umcsent_xlv Correlation"
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for umcsent_xlv Granger"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for umcsent_xlv Granger"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for umcsent_xlv Granger"
    ),
    chart_name="ccf",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for umcsent_xlv Granger/CCF — "
        "port from app/pages/10_umcsent_xlv_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for umcsent_xlv Granger"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for umcsent_xlv Granger"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for umcsent_xlv Granger"
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Descriptive Statistics)",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for umcsent_xlv Regime"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for umcsent_xlv Regime"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for umcsent_xlv Regime"
    ),
    chart_name="regime_stats",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for umcsent_xlv Regime — "
        "port from app/pages/10_umcsent_xlv_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for umcsent_xlv Regime"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for umcsent_xlv Regime"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for umcsent_xlv Regime"
    ),
)


SIGNAL_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Signal Distribution Analysis",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for umcsent_xlv Signal Distribution"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for umcsent_xlv Signal Distribution"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for umcsent_xlv Signal Distribution"
    ),
    chart_name="signal_dist",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for umcsent_xlv Signal Distribution — "
        "port from app/pages/10_umcsent_xlv_evidence.py"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for umcsent_xlv Signal Distribution"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for umcsent_xlv Signal Distribution"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for umcsent_xlv Signal Distribution"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A): overview for umcsent_xlv Evidence"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A): plain_english for umcsent_xlv Evidence"
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality"],
    "level2": [REGIME_BLOCK, SIGNAL_DIST_BLOCK],
    "level2_labels": ["Regime Analysis", "Signal Distribution"],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A): tournament_intro for umcsent_xlv"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A): transition for umcsent_xlv Evidence"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating Consumer Sentiment Signals into XLV Positioning"
    PAGE_SUBTITLE = (
        "We tested hundreds of strategy combinations to find the most robust way "
        "to time healthcare sector (XLV) exposure using consumer sentiment."
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for umcsent_xlv Strategy"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A): SIGNAL_RULE_MD for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_strategy.py"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A): HOW_SIGNAL_IS_GENERATED_MD for umcsent_xlv"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A): MANUAL_USE_MD for umcsent_xlv"
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    # umcsent_xlv uses `wf_sharpe` rather than canonical `walk_forward`.
    WALK_FORWARD_CHART_NAME = "wf_sharpe"
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A): CAVEATS_MD for umcsent_xlv — "
        "port from app/pages/10_umcsent_xlv_strategy.py"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A): TRADE_LOG_EXAMPLE_MD for umcsent_xlv — "
        "author from results/umcsent_xlv/winner_trades_broker_style.csv "
        "(shipped Wave 10H.2, commit 2c11046); legacy hand-rolled example "
        "lives in app/pages/10_umcsent_xlv_strategy.py — extract and recast"
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **UMich Consumer Sentiment** | FRED | UMCSENT | Monthly |
| **Healthcare Sector ETF** | Yahoo Finance | XLV | Daily → Monthly |
| **S&P 500 (benchmark)** | Yahoo Finance | SPY | Daily → Monthly |
| **NBER Recession Dates** | FRED / NBER | USREC | Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |
| **Unemployment** | FRED | UNRATE | Monthly |

*Scope discipline (ECON-SD).* Only UMCSENT and XLV are in-scope primary signals.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A): INDICATOR_CONSTRUCTION_MD for umcsent_xlv — "
    "port from app/pages/10_umcsent_xlv_methodology.py (sentiment level, "
    "YoY change, z-score, momentum, inflection dummies)"
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|:-------|:--------------------|:----------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline UMCSENT-XLV test |
| Granger Causality | One-directional predictive content | Tests sentiment → XLV asymmetry |
| Regime Quartile Returns | Model-free gradient across sentiment distribution | Assumption-light regime check |
| Signal Distribution Analysis | Full empirical distribution of the signal | Diagnostic for threshold choice |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals** | UMCSENT level, YoY change, z-score, 3M/6M momentum, inflection dummies |
| **Threshold methods** | Fixed IS percentile, rolling percentile, rolling z-score |
| **Strategies** | Long/Cash (P1), Signal-Strength (P2), Long/Short (P3) |
| **Lead times** | L0 through L6 (monthly indicator — L6 default) |
| **Orientation** | Both pro- and countercyclical tested |

Ranked by out-of-sample Sharpe ratio. See the Tournament tab on the Evidence
page for the full leaderboard and the winner's parameters.
"""

_REFERENCES_MD = """
- Curtin, R. T. (2007). Consumer sentiment surveys: Worldwide review and assessment. *Journal of Business Cycle Measurement and Analysis*, 2007(1), 7–42.
- Ludvigson, S. C. (2004). Consumer confidence and consumer spending. *Journal of Economic Perspectives*, 18(2), 29–50.
- Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645–1680.
- Lemmon, M., & Portniaguina, E. (2006). Consumer confidence and asset prices: Some empirical evidence. *Review of Financial Studies*, 19(4), 1499–1529.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "# TODO Ray (Wave 10I.A): sample_period_note for umcsent_xlv — "
        "XLV starts 1998-12 (same as XLP); UMCSENT available from 1978"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A): plain_english for umcsent_xlv Methodology"
    ),
)
