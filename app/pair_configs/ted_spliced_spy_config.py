"""Spliced TED × SPY pair configuration (Rule APP-PT1).

Wave 10I.A Part 2 migration note — Ray: narrative fields carry TODO-Ray stubs.
Source content lived in app/pages/6_ted_variants_*.py before this commit
(tab C: "Spliced TED" of the 3-in-1 TED composite page).

Structural fields (chart names, data-source table, tournament design,
references, methods table) filled in-place by Ace from the legacy composite.
Narrative prose left as TODO stubs for Ray (RES-NR1 owner).

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
        "# TODO Ray (Wave 10I.A Part 2): PLAIN_ENGLISH for ted_spliced_spy — "
        "port from app/pages/6_ted_variants_story.py (Variant C framing, lines 55-56)"
    )

    WHERE_THIS_FITS = (
        "# TODO Ray (Wave 10I.A Part 2): WHERE_THIS_FITS for ted_spliced_spy"
    )

    ONE_SENTENCE_THESIS = (
        "# TODO Ray (Wave 10I.A Part 2): ONE_SENTENCE_THESIS for ted_spliced_spy"
    )

    KPI_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): KPI_CAPTION for ted_spliced_spy"
    )

    HERO_TITLE = "Spliced TED Spread (1993-2025) vs. S&P 500"
    HERO_CHART_NAME = "ted_spliced_spy_hero"
    HERO_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): HERO_CAPTION for ted_spliced_spy — "
        "port from app/pages/6_ted_variants_story.py line 77 "
        "(official TEDRATE 1993-2022 + affine-adjusted DFF-TED 2022-2025)"
    )

    REGIME_TITLE = "What History Shows: SPY Returns by Spliced-TED Stress Regime"
    REGIME_CHART_NAME = "ted_spliced_spy_regime_stats"
    REGIME_CAPTION = (
        "# TODO Ray (Wave 10I.A Part 2): REGIME_CAPTION for ted_spliced_spy — "
        "port from app/pages/6_ted_variants_story.py line 93"
    )

    NARRATIVE_SECTION_1 = (
        "# TODO Ray (Wave 10I.A Part 2): NARRATIVE_SECTION_1 for ted_spliced_spy — "
        "port from app/pages/6_ted_variants_story.py lines 36-46 "
        "(TED spread concept) + splice motivation"
    )

    NARRATIVE_SECTION_2 = (
        "# TODO Ray (Wave 10I.A Part 2): NARRATIVE_SECTION_2 for ted_spliced_spy — "
        "author Variant-C-specific framing: splice assumption (affine adjustment "
        "fitted on overlap), risk that adjustment may not hold out-of-sample"
    )

    SCOPE_NOTE = (
        "# TODO Ray (Wave 10I.A Part 2): SCOPE_NOTE for ted_spliced_spy — "
        "author scope-discipline note (TEDRATE and DFF-DTB3 are in-scope "
        "primary inputs for the splice construction)"
    )

    TRANSITION_TEXT = (
        "# TODO Ray (Wave 10I.A Part 2): TRANSITION_TEXT for ted_spliced_spy — "
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
        "# TODO Ray (Wave 10I.A Part 2): method_theory for ted_spliced_spy Correlation"
    ),
    question=(
        "# TODO Ray (Wave 10I.A Part 2): question for ted_spliced_spy Correlation"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A Part 2): how_to_read for ted_spliced_spy Correlation"
    ),
    chart_name="ted_spliced_spy_correlations",
    chart_caption=(
        "# TODO Ray (Wave 10I.A Part 2): chart_caption for ted_spliced_spy Correlation — "
        "port from app/pages/6_ted_variants_evidence.py lines 31-37"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A Part 2): observation for ted_spliced_spy Correlation"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A Part 2): interpretation for ted_spliced_spy Correlation"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A Part 2): key_message for ted_spliced_spy Correlation"
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "# TODO Ray (Wave 10I.A Part 2): method_theory for ted_spliced_spy Local Projections"
    ),
    question=(
        "# TODO Ray (Wave 10I.A Part 2): question for ted_spliced_spy Local Projections"
    ),
    how_to_read=(
        "# TODO Ray (Wave 10I.A Part 2): how_to_read for ted_spliced_spy Local Projections"
    ),
    chart_name="ted_spliced_spy_local_projections",
    chart_caption=(
        "# TODO Ray (Wave 10I.A Part 2): chart_caption for ted_spliced_spy Local Projections — "
        "port from app/pages/6_ted_variants_evidence.py lines 39-45"
    ),
    observation=(
        "# TODO Ray (Wave 10I.A Part 2): observation for ted_spliced_spy Local Projections"
    ),
    interpretation=(
        "# TODO Ray (Wave 10I.A Part 2): interpretation for ted_spliced_spy Local Projections"
    ),
    key_message=(
        "# TODO Ray (Wave 10I.A Part 2): key_message for ted_spliced_spy Local Projections"
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "# TODO Ray (Wave 10I.A Part 2): overview for ted_spliced_spy Evidence"
    ),
    "plain_english": (
        "# TODO Ray (Wave 10I.A Part 2): plain_english for ted_spliced_spy Evidence"
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "# TODO Ray (Wave 10I.A Part 2): tournament_intro for ted_spliced_spy"
    ),
    "transition": (
        "# TODO Ray (Wave 10I.A Part 2): transition for ted_spliced_spy Evidence"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating Spliced-TED Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested ~991 strategy combinations on the spliced TED spread "
        "(Variant C: TEDRATE 1993-2022 + affine-adjusted DFF-TED 2022+)."
    )

    PLAIN_ENGLISH = (
        "# TODO Ray (Wave 10I.A Part 2): PLAIN_ENGLISH for ted_spliced_spy Strategy"
    )

    SIGNAL_RULE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): SIGNAL_RULE_MD for ted_spliced_spy — "
        "port from app/pages/6_ted_variants_strategy.py winner spotlight "
        "(read results/ted_spliced_spy/winner_summary.json for canonical params)"
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "# TODO Ray (Wave 10I.A Part 2): HOW_SIGNAL_IS_GENERATED_MD for ted_spliced_spy"
    )

    MANUAL_USE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): MANUAL_USE_MD for ted_spliced_spy"
    )

    # No equity_curves / drawdown / walk_forward charts exist on disk for
    # ted_spliced_spy (as of Wave 10I.A Part 2). Template falls back to
    # "chart pending" — pre-existing data gap.
    TOURNAMENT_SCATTER_CHART_NAME = "ted_spliced_spy_tournament_scatter"

    CAVEATS_MD = (
        "# TODO Ray (Wave 10I.A Part 2): CAVEATS_MD for ted_spliced_spy — "
        "port from app/pages/6_ted_variants_strategy.py lines 146-152 "
        "(Variant C splice assumes affine adjustment holds OOS — a structural assumption)"
    )

    TRADE_LOG_EXAMPLE_MD = (
        "# TODO Ray (Wave 10I.A Part 2): TRADE_LOG_EXAMPLE_MD for ted_spliced_spy — "
        "author from results/ted_spliced_spy/winner_trade_log.csv"
    )


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

_INDICATOR_CONSTRUCTION_MD = (
    "# TODO Ray (Wave 10I.A Part 2): INDICATOR_CONSTRUCTION_MD for ted_spliced_spy — "
    "port from app/pages/6_ted_variants_methodology.py (Variant C formula: "
    "TEDRATE for 1993-2022 + affine-adjusted DFF-TED for 2022-present, 8,589 daily obs; "
    "derived signals: level, z-score 126d/252d, RoC 21d/63d, momentum, percentile rank)"
)

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
        "# TODO Ray (Wave 10I.A Part 2): sample_period_note for ted_spliced_spy — "
        "1993-01 to 2025-12, ~8,589 daily obs; ADF statistic -4.074 (p=0.0011, stationary)"
    ),
    plain_english=(
        "# TODO Ray (Wave 10I.A Part 2): plain_english for ted_spliced_spy Methodology"
    ),
)
