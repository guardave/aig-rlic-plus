"""INDPRO × SPY pair configuration (Rule APP-PT1).

Wave 10I.A migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/5_indpro_spy_*.py before this commit.
Run `git log --follow app/pages/5_indpro_spy_story.py` to see the
pre-migration content.

Structural fields (chart names, data-source table, tournament design,
references, methods table) filled in-place by Ace from the legacy pages.
Narrative prose left as TODO stubs for Ray (RES-NR1 owner).

Pair ID: indpro_spy  (legacy Pair #1)
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    """Story-page content object (passed to `render_story_page`)."""

    PAGE_TITLE = "The Story: Factory Output and the Stock Market"
    PAGE_SUBTITLE = (
        "Does the pace of industrial activity predict where stocks are headed?"
    )

    HEADLINE_H2 = (
        "## Industrial Production as a pro-cyclical equity timing signal — "
        "OOS Sharpe vs SPY buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py lines 35-40"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A): WHERE_THIS_FITS for indpro_spy — "
        "port/rewrite from app/pages/5_indpro_spy_story.py"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A): ONE_SENTENCE_THESIS for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A): KPI_CAPTION for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py"
    )

    HERO_TITLE = "35 Years of Industrial Production vs. S&P 500"
    HERO_CHART_NAME = "indpro_spy_hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A): HERO_CAPTION for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py lines 46-53"
    )

    REGIME_TITLE = "What History Shows: Returns by IP Growth Regime"
    REGIME_CHART_NAME = "indpro_spy_regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A): REGIME_CAPTION for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py lines 93-101"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_1 for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py lines 58-83 "
        "(Why Should Stock Investors Care + IP-Equity Connection)"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A): NARRATIVE_SECTION_2 for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py lines 115-127 "
        "(The Surprise: A Peak-Cycle Warning, counter-intuitive z-score finding)"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A): SCOPE_NOTE for indpro_spy — "
        "author scope-discipline note"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A): TRANSITION_TEXT for indpro_spy — "
        "port from app/pages/5_indpro_spy_story.py lines 131-134"
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for indpro_spy Correlation — "
        "port from app/pages/5_indpro_spy_evidence.py (Correlations tab)"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for indpro_spy Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for indpro_spy Correlation"
    ),
    chart_name="indpro_spy_correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for indpro_spy Correlation — "
        "port from app/pages/5_indpro_spy_evidence.py lines 46-55"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for indpro_spy Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for indpro_spy Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for indpro_spy Correlation"
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Cross-Correlation Function (CCF)",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for indpro_spy CCF"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for indpro_spy CCF"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for indpro_spy CCF"
    ),
    chart_name="indpro_spy_ccf",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for indpro_spy CCF — "
        "port from app/pages/5_indpro_spy_evidence.py lines 61-69"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for indpro_spy CCF"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for indpro_spy CCF"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for indpro_spy CCF"
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for indpro_spy Granger"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for indpro_spy Granger"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for indpro_spy Granger"
    ),
    chart_name="indpro_spy_granger",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for indpro_spy Granger — "
        "port from app/pages/5_indpro_spy_evidence.py lines 75-83"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for indpro_spy Granger — "
        "port from app/pages/5_indpro_spy_evidence.py lines 85-94 "
        "(coincident-indicator interpretation)"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for indpro_spy Granger"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for indpro_spy Granger"
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for indpro_spy Local Projections"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for indpro_spy Local Projections"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for indpro_spy Local Projections"
    ),
    chart_name="indpro_spy_local_projections",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for indpro_spy Local Projections — "
        "port from app/pages/5_indpro_spy_evidence.py lines 100-109"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for indpro_spy Local Projections"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for indpro_spy Local Projections"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for indpro_spy Local Projections"
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for indpro_spy Quantile"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for indpro_spy Quantile"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for indpro_spy Quantile"
    ),
    chart_name="indpro_spy_quantile_regression",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for indpro_spy Quantile — "
        "port from app/pages/5_indpro_spy_evidence.py lines 115-124 "
        "(left-tail protection framing)"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for indpro_spy Quantile"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for indpro_spy Quantile"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for indpro_spy Quantile"
    ),
)


RF_BLOCK = dict(
    chart_status="ready",
    method_name="Random Forest Feature Importance",
    method_theory=(
        "# TODO Ray (Wave 10I.A): method_theory for indpro_spy Random Forest"
    ),
    question=(
        "# TODO Ray (Wave 10I.A): question for indpro_spy Random Forest"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A): how_to_read for indpro_spy Random Forest"
    ),
    chart_name="indpro_spy_rf_importance",
    chart_caption=(
        "# TODO Ray (Wave 10I.A): chart_caption for indpro_spy RF — "
        "port from app/pages/5_indpro_spy_evidence.py lines 143-152 "
        "(walk-forward 61.4% accuracy framing in lines 154-162)"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A): observation for indpro_spy RF"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A): interpretation for indpro_spy RF"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A): key_message for indpro_spy RF"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A): overview for indpro_spy Evidence — "
        "port from app/pages/5_indpro_spy_evidence.py lines 30-34"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A): plain_english for indpro_spy Evidence"
    ),
    "level1": [CORRELATION_BLOCK, CCF_BLOCK, GRANGER_BLOCK],
    "level1_labels": ["Correlation", "Cross-Correlation (CCF)", "Granger Causality"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, RF_BLOCK],
    "level2_labels": [
        "Local Projections",
        "Quantile Regression",
        "Random Forest Importance",
    ],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A): tournament_intro for indpro_spy — "
        "port from app/pages/5_indpro_spy_strategy.py"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A): transition for indpro_spy Evidence — "
        "port from app/pages/5_indpro_spy_evidence.py lines 166-171"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    """Strategy-page content object (passed to `render_strategy_page`)."""

    PAGE_TITLE = "The Strategy: Translating IP Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested hundreds of strategy combinations to find the most robust way "
        "to time SPY exposure using the Industrial Production signal."
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A): PLAIN_ENGLISH for indpro_spy Strategy — "
        "port from app/pages/5_indpro_spy_strategy.py"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A): SIGNAL_RULE_MD for indpro_spy — "
        "port from app/pages/5_indpro_spy_strategy.py (winner rule: "
        "3M momentum, L6, Long/Cash per docs/pair_execution_history.md)"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A): HOW_SIGNAL_IS_GENERATED_MD for indpro_spy — "
        "port from app/pages/5_indpro_spy_strategy.py"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A): MANUAL_USE_MD for indpro_spy — "
        "port from app/pages/5_indpro_spy_strategy.py"
    )

    EQUITY_CHART_NAME = "indpro_spy_equity_curves"
    # DRAWDOWN_CHART_NAME intentionally omitted — no drawdown chart on disk.
    # WALK_FORWARD_CHART_NAME intentionally omitted — no walk_forward chart.
    TOURNAMENT_SCATTER_CHART_NAME = "indpro_spy_tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A): CAVEATS_MD for indpro_spy — "
        "port from app/pages/5_indpro_spy_strategy.py"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A): TRADE_LOG_EXAMPLE_MD for indpro_spy — "
        "author from winner_trades_broker_style.csv when available"
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Industrial Production** | FRED | INDPRO | Monthly |
| **S&P 500 (Target)** | Yahoo Finance | SPY | Daily → Monthly |
| **NBER Recession Dates** | FRED / NBER | USREC | Monthly |
| **Treasury yields** | FRED | DGS10, DTB3 | Daily → Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |
| **Unemployment** | FRED | UNRATE | Monthly |
| **Capacity Utilization** | FRED | TCU | Monthly |
| **VIX** | Yahoo Finance | ^VIX | Daily → Monthly |

*Scope discipline (ECON-SD).* Only INDPRO and SPY are in-scope primary signals.
Controls (VIX, yield spread, UNRATE, CAPUT) are used only in regression
controls, not as trading signals.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A): INDICATOR_CONSTRUCTION_MD for indpro_spy — "
    "port from app/pages/5_indpro_spy_methodology.py (INDPRO derived signals: "
    "level, YoY growth, MoM growth, z-score, 3M/6M momentum, acceleration)"
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|:-------|:--------------------|:----------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline test for IP-SPY link |
| Cross-Correlation Function (CCF) | Lead-lag timing structure | Identifies peak predictive lag |
| Granger Causality | One-directional predictive content | Tests IP → SPY vs SPY → IP asymmetry |
| Local Projections (Jordà) | Full dynamic path of SPY response to IP shock | Robust IRF without VAR restrictions |
| Quantile Regression | Asymmetric predictive power across return distribution | Tests left-tail (downside) protection |
| Markov-Switching Regression | 2-state regime identification | NBER-consistent regime dating |
| Random Forest | Walk-forward feature importance | Nonlinear feature ranking with OOS validation |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals** | IP level, YoY growth, MoM change, z-score, 3M/6M momentum, acceleration, contraction dummy |
| **Threshold methods** | Fixed IS percentile (p25/p50/p75), rolling percentile, rolling z-score (±1.0/±1.5) |
| **Strategies** | Long/Cash (P1), Signal-Strength (P2), Long/Short (P3) |
| **Lead times** | L0 through L6 (winner L6) |
| **Orientation** | Pro-cyclical and countercyclical |

The tournament tested all valid combinations and ranked by out-of-sample Sharpe
ratio. Winner (per docs/pair_execution_history.md): **3M momentum signal,
Long/Cash, L6 lead — OOS Sharpe 1.10 vs 0.90 buy-and-hold SPY**.
"""

_REFERENCES_MD = """
#### Business Cycle and Equity Returns
- Chen, N. F., Roll, R., & Ross, S. A. (1986). Economic forces and the stock market. *Journal of Business*, 59(3), 383–403.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23–49.
- Stock, J. H., & Watson, M. W. (1989). New indexes of coincident and leading economic indicators. *NBER Macroeconomics Annual*, 4, 351–394.

#### Impulse Response and Local Projections
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.

#### Regime Models
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384.

#### Quantile Methods
- Koenker, R., & Bassett, G. (1978). Regression quantiles. *Econometrica*, 46(1), 33–50.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "# TODO Ray (Wave 10I.A): sample_period_note for indpro_spy — "
        "port from app/pages/5_indpro_spy_methodology.py (1990-01 to 2025-12, "
        "432 monthly observations per the legacy page footer)"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A): plain_english for indpro_spy Methodology"
    ),
)
