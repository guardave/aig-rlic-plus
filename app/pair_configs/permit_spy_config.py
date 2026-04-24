"""PERMIT × SPY pair configuration (Rule APP-PT1).

Wave 10I.A narrative port (Ray): prose fields authored from legacy
app/pages/7_permit_spy_*.py (pre-migration, commit 24e2f16~1) and
cross-checked against results/permit_spy/winner_summary.json.

Pair ID: permit_spy  (legacy Pair #3 — Building Permits → SPY)
Winner (winner_summary.json, authoritative): S3_mom / T1_p25 / P3_long_short /
L6 — OOS Sharpe 1.45 vs 0.90 B&H SPY, OOS return +22.7%, Max DD -19.4%.
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
        "Every month the U.S. Census Bureau publishes the number of new housing "
        "units that have been authorized by local governments. Builders don't "
        "pull permits unless they believe houses will sell, so the count is an "
        "early read on where the economy is headed. This page asks a simple "
        "question: when permits are rising, do stocks tend to rise too — and "
        "can you actually trade on it?"
    )

    WHERE_THIS_FITS = (
        "This pair sits in the **Activity / Survey** indicator family of the "
        "portal. Building Permits has been part of the Conference Board's "
        "Leading Economic Index since 1959, so it is one of the oldest and "
        "best-pedigreed leading indicators in the catalogue. It complements "
        "the Industrial Production pair (a coincident activity measure) and "
        "the UMCSENT consumer-sentiment pair (a survey measure)."
    )

    ONE_SENTENCE_THESIS = (
        "*Monthly Building Permits growth (MoM change, 6-month lead) is a "
        "pro-cyclical signal that historically delivered an out-of-sample "
        "Sharpe of 1.45 on SPY versus 0.90 for buy-and-hold.*"
    )

    KPI_CAPTION = (
        "The OOS period runs 2018-01 to 2025-12. The winning Long/Short strategy "
        "doubles gross exposure versus the Long/Cash benchmark, which explains "
        "part of the return premium but also the tighter max-drawdown profile."
    )

    HERO_TITLE = "Building Permits vs. S&P 500 Over the Business Cycle"
    HERO_CHART_NAME = "permit_spy_hero"
    HERO_CAPTION = (
        "Dual-axis view: Building Permits (left, red) and SPY price (right, blue). "
        "Permits peaked before the 2001 and 2008 recessions and collapsed during "
        "the housing crisis, providing an early warning signal for equity declines. "
        "The 2020 COVID dip was shorter and V-shaped, and permits led the recovery "
        "by several months."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by Building-Permit Regime"
    REGIME_CHART_NAME = "permit_spy_regime_stats"
    REGIME_CAPTION = (
        "SPY Sharpe by Building Permits growth quartile. The high-growth regime "
        "(Q4) delivers a Sharpe near 0.95; the deep-contraction regime (Q1) falls "
        "to roughly 0.75. The spread is narrower than for VIX/VIX3M (9 Sharpe "
        "points) or credit spreads (3 points), suggesting permits work best as a "
        "directional signal rather than as a stand-alone regime-timing tool."
    )

    NARRATIVE_SECTION_1 = (
        "### Why Permits Lead the Business Cycle\n\n"
        "Building Permits (FRED: `PERMIT`) count the number of new privately-owned "
        "housing units authorised by building permits each month. They have been a "
        "component of the Conference Board's Leading Economic Index since 1959 — "
        "one of the longest-tenured leading indicators in macroeconomics — and are "
        "published by the U.S. Census Bureau approximately 2-3 weeks after the "
        "reference month, seasonally adjusted at an annual rate.\n\n"
        "For stock investors, permits matter because **housing is the leading "
        "sector of the economy**. Residential construction accounts for roughly "
        "15-18% of GDP once you include direct construction, furnishings, and the "
        "wealth effect from home equity. When permits rise, it signals future "
        "construction activity, construction employment, consumer spending on "
        "durables, and eventually corporate earnings. When permits fall, a broader "
        "slowdown typically follows within 3-6 months.\n\n"
        "The economic logic is straightforward. Rising permits signal expanding "
        "housing demand, future construction jobs, household wealth accumulation, "
        "and consumer confidence — all bullish for stocks. Falling permits signal "
        "housing weakness, reduced construction, and a cooling economy — bearish "
        "for stocks. Permits precede actual construction starts by 1-3 months and "
        "broader economic activity by 3-6 months, which is why a 6-month lead in "
        "the trading rule is the tournament optimum. As Edward Leamer argued in "
        "his 2007 Jackson Hole paper, 'Housing IS the business cycle.'"
    )

    NARRATIVE_SECTION_2 = (
        "### Nuance and Limits\n\n"
        "Three episodes dominate the permits data and every user of this signal "
        "should understand them:\n\n"
        "1. **Housing bubble (2003-2007).** Permits surged to record highs on the "
        "back of subprime lending and speculation. The pro-cyclical signal was "
        "correct — stocks did rise — but the bubble masked underlying credit risk, "
        "and the eventual collapse was unprecedented in modern data.\n\n"
        "2. **Great Recession (2008-2009).** Permits fell more than 50% peak to "
        "trough, one of the deepest contractions on record. Here the signal worked "
        "as advertised: permits flagged severe weakness well before equities "
        "finished falling.\n\n"
        "3. **COVID collapse (April 2020).** Permits plunged as construction "
        "halted, then recovered on a V-shape driven by mortgage forbearance, "
        "fiscal stimulus, and a shift to suburban demand. Post-COVID supply-chain "
        "distortions (2021-2022) created additional noise in the signal that "
        "persisted until lumber and labour bottlenecks cleared.\n\n"
        "The practical limit is that permits are monthly and publication-lagged — "
        "the strategy cannot react to a fast crash the way a daily options-based "
        "signal (see the VIX × VIX3M pair) can. It captures durable business-cycle "
        "turns, not short-term market moves."
    )

    SCOPE_NOTE = (
        "*Scope discipline (ECON-SD).* Only PERMIT and SPY are in-scope primary "
        "signals for this pair. UNRATE, DGS10, DFF, and VIX are retained only as "
        "regression controls in the Methodology section and are not traded."
    )

    TRANSITION_TEXT = (
        "History and economic theory position building permits as one of the "
        "strongest leading indicators available. But does the econometric "
        "evidence actually confirm a statistically significant, tradable "
        "relationship with equity returns?"
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dot_com",
            "title": "Dot-Com Bust (2000–2002)",
            "narrative": "Building permits actually held up surprisingly well through the 2000–2002 recession — the bust was concentrated in the technology sector, not housing construction. Permits dipped modestly and recovered quickly. The 1-month momentum signal may have briefly turned negative but quickly reverted. This is a failure case: the indicator correctly reflected housing resilience, but that resilience did not prevent SPY from falling ~50%.",
            "caption": "2001: Building permits held up through dot-com bust — housing was fine, but SPY fell 50% on tech collapse",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": "Permits peaked in January 2006 and fell for nearly four years — one of the longest and deepest collapses in the series history. The 1-month momentum signal turned bearish in 2006, well before the equity market peaked in October 2007. This is the strongest long-lead case in the series: permits led the equity top by ~18 months. The Long/Short strategy would have been short SPY during most of the crash.",
            "caption": "Permits peaked Jan 2006, fell 4 years — the GFC's earliest macro warning, leading equity top by 18 months",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": "Permits collapsed briefly in April 2020 but recovered sharply by June 2020 on a wave of pandemic-era housing demand. The 1-month momentum signal fired bearish, then turned bullish almost immediately — a fast coincident case. The signal correctly called the turn but the trade window was extremely short, and the strategy's 6-month lead would have carried stale bearish positioning well into the recovery.",
            "caption": "COVID permits: brief April 2020 collapse, then V-shaped recovery — 6-month lead lag caused stale bearish carry",
        },
        {
            "slug": "china_2015",
            "title": "China Slowdown / EM Stress (2015–2016)",
            "narrative": "US permits grew steadily through 2015–2016 despite global headwinds, reflecting strong domestic housing demand and low mortgage rates. The momentum signal stayed positive. SPY was volatile but did not crash. A success case for the signal's \"stay long\" reading, though the narrow equity upside limited realized outperformance.",
            "caption": "2015-16: US permits continued rising despite EM stress — signal correctly stayed long SPY through the volatility",
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson correlations measure the linear co-movement between permit "
        "signal variants (level, YoY growth, MoM change, z-score, 3M/6M momentum) "
        "and SPY forward returns at 1M, 3M, 6M, and 12M horizons. Spearman "
        "correlations are run in parallel as a rank-based robustness check."
    ),
    question=(
        "Do any of the permit-derived signals show a statistically meaningful "
        "linear relationship with future SPY returns, and in which direction?"
    ),
    how_to_read=(
        "Rows are permit signal variants; columns are forward SPY return horizons. "
        "Warm colours (blue→green) indicate positive (pro-cyclical) correlation; "
        "cool colours (red) indicate negative. Stars mark conventional significance "
        "levels (* p<0.05, ** p<0.01)."
    ),
    chart_name="permit_spy_correlations",
    chart_caption=(
        "Pearson correlations between Building Permits signal variants and forward "
        "return horizons. Warm colours = positive (pro-cyclical). Permits YoY "
        "growth and momentum signals show the strongest positive correlations with "
        "3-6 month forward returns."
    ),
    observation=(
        "The correlation heatmap is consistently positive across signal variants "
        "and forward horizons, with the strongest correlations appearing on the "
        "momentum transforms (MoM and 3M momentum) at 3-6 month forward windows. "
        "Level-based signals are weaker — consistent with the non-stationary "
        "nature of the raw permit series."
    ),
    interpretation=(
        "The structure confirms the pro-cyclical relationship that economic "
        "theory predicts. Unlike Industrial Production (where the z-score showed "
        "a counter-intuitive peak-cycle effect), permits correlations are "
        "consistently positive across signal types and horizons. Permits signal "
        "direction, and the direction is consistent."
    ),
    key_message=(
        "Rising permits correlate with better forward SPY returns across "
        "multiple signal definitions and horizons — a clean, directionally "
        "consistent pro-cyclical relationship."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "Jordà (2005) local projections estimate the cumulative SPY response to "
        "a one-standard-deviation permit shock at each forward horizon "
        "independently, using HAC (Newey-West) standard errors. Unlike a VAR, "
        "LPs do not impose a parametric propagation structure, which makes them "
        "robust to model mis-specification at longer horizons."
    ),
    question=(
        "What is the dynamic path of SPY's response to a permit-growth shock "
        "over the next 12 months, and at which horizon does it peak?"
    ),
    how_to_read=(
        "X-axis: forecast horizon in months. Y-axis: cumulative SPY response to a "
        "1-standard-deviation permit-growth shock. Shaded area = 95% HAC confidence "
        "band. Stars mark significance at p<0.05."
    ),
    chart_name="permit_spy_local_projections",
    chart_caption=(
        "Jordà (2005) local projections with HAC (Newey-West) standard errors. "
        "Stars indicate significance at p<0.05. The coefficient shows the marginal "
        "effect of a 1pp increase in Permits YoY growth on forward SPY returns."
    ),
    observation=(
        "The impulse response is positive, rising through the 3-6 month horizon, "
        "and remains significant out to about 9 months before confidence bands "
        "widen. A one-standard-deviation increase in permit growth is associated "
        "with meaningfully higher cumulative SPY returns over the subsequent 6 "
        "months."
    ),
    interpretation=(
        "The LP result aligns precisely with permits' role as a leading indicator: "
        "the effect is economically meaningful, statistically significant, and "
        "peaks at the horizon (3-6 months) that economic theory would predict. "
        "This is the empirical foundation for choosing a 6-month lead in the "
        "trading rule."
    ),
    key_message=(
        "SPY responds positively and significantly to permit shocks, with the "
        "peak effect at 3-6 months — direct support for the 6-month lead in the "
        "winning strategy."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We tested the permits-equity relationship with complementary econometric "
        "methods across 35 years of monthly data. Two method blocks are reported "
        "here — correlations (for breadth across signal variants and horizons) "
        "and local projections (for the dynamic impulse-response path). The full "
        "battery is archived in `results/permit_spy/core_models_20260314/`."
    ),
    "plain_english": (
        "Correlations ask 'do they move together?'. Local projections ask 'if "
        "permits jump today, what happens to SPY over the next 12 months?'. Both "
        "tests agree: the relationship is real, pro-cyclical, and strongest at a "
        "3-6 month lead."
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "With the econometric case established, we then swept a 5-dimensional "
        "tournament over signal transforms, threshold methods, strategy families, "
        "lead times, and lookback windows. The leaderboard lives on the Strategy "
        "page; the key headline is a winning OOS Sharpe of 1.45 versus 0.90 for "
        "SPY buy-and-hold."
    ),
    "transition": (
        "The statistical evidence confirms a genuine pro-cyclical relationship "
        "between building permits and equity returns, with permits leading by 3-6 "
        "months. The practical question is whether investors can translate this "
        "into a profitable, execution-ready strategy."
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
        "The tournament winner uses a one-month change in permits: if last "
        "month's permit count was meaningfully higher than recent history, hold "
        "SPY long; if it collapsed, go short. Apply the signal with a 6-month "
        "delay because permits lead the economy by about half a year. Update the "
        "position once a month, using publicly available FRED data."
    )

    SIGNAL_RULE_MD = (
        "**Tournament winner:** Signal `S3_mom` (1-month momentum) / Threshold "
        "`T1_p25` (25th percentile, fixed in-sample) / Strategy `P3_long_short` "
        "(Long/Short) / Lead 6 months.\n\n"
        "When the month-over-month change in Building Permits is above its "
        "historical 25th percentile (i.e., not deeply negative), go long SPY. "
        "When permits momentum falls below the 25th percentile (sharp decline), "
        "go short. Apply the signal with a 6-month lead to exploit permits' role "
        "as a leading indicator."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "1. **Pull PERMIT.** FRED series `PERMIT`, monthly SAAR. Released "
        "~2-3 weeks after the reference month.\n"
        "2. **Compute MoM momentum.** `mom_t = permit_t / permit_{t-1} - 1`.\n"
        "3. **Fix the threshold once, in-sample.** Take the 25th percentile of "
        "MoM momentum from 1990-01 to 2017-12 and keep that number as the "
        "threshold for the entire OOS period.\n"
        "4. **Apply the 6-month lead.** Today's position uses the MoM reading "
        "from 6 months ago.\n"
        "5. **Translate to position.** If the 6-month-lagged MoM is above the "
        "fixed 25th-percentile threshold → long SPY (+1). Otherwise → short SPY "
        "(-1). Rebalance monthly."
    )

    MANUAL_USE_MD = (
        "You do not need software to run this rule. Each month:\n\n"
        "1. Download the latest `PERMIT` CSV from FRED.\n"
        "2. Compute the month-over-month percentage change for the reading six "
        "months ago.\n"
        "3. Compare that number to -2.1% (the fixed in-sample 25th percentile; "
        "exact value is regenerated in the pipeline notebook).\n"
        "4. If the number is above -2.1% → hold SPY long. Below → short.\n"
        "5. Revisit next month.\n\n"
        "Turnover averages about 9 round-trips per year — well inside any "
        "retail-friendly execution envelope."
    )

    # No equity_curves / drawdown / walk_forward charts exist for permit_spy
    # on disk (as of Wave 10I.A). Template falls back to "chart pending" for
    # those surfaces — pre-existing data gap, not a regression.
    TOURNAMENT_SCATTER_CHART_NAME = "permit_spy_tournament_scatter"

    CAVEATS_MD = (
        "1. **Housing-bubble distortion (2003-2007).** Permits reached "
        "unsustainable levels during the subprime boom. The signal was "
        "pro-cyclical during this period, but the subsequent crash was "
        "unprecedented in modern data; a rule calibrated only on post-2009 data "
        "would look materially different.\n\n"
        "2. **COVID collapse (April 2020).** Permits plunged as construction "
        "halted nationwide. The V-shaped recovery was driven by unique policy "
        "responses (mortgage forbearance, stimulus) that may not repeat.\n\n"
        "3. **Post-COVID supply-chain noise (2021-2022).** Lumber shortages, "
        "labour constraints, and zoning backlogs distorted the permits-to-"
        "construction pipeline, reducing signal reliability.\n\n"
        "4. **Long/Short amplifies both gains and losses.** The winning strategy "
        "uses Long/Short, which doubles gross exposure compared to Long/Cash. "
        "The higher Sharpe comes with commensurately higher risk in adverse "
        "scenarios — read the drawdown profile carefully before sizing."
    )

    TRADE_LOG_EXAMPLE_MD = (
        "**Crisis anchor — 2008 Great Financial Crisis.** From "
        "`results/permit_spy/winner_trade_log.csv`:\n\n"
        "- **2008-06-30 → 2008-10-31 (Short, 123 days, +26.65%).** Building "
        "permits had been collapsing since mid-2006. By June 2008 the 6-month-"
        "lagged MoM signal (reflecting December 2007 permit data) had been "
        "deeply negative for more than a year, pushing the rule into a short "
        "SPY position. The short was held through the Lehman bankruptcy and the "
        "October 2008 market trough, returning +26.65% over 123 calendar days.\n"
        "- **2008-10-31 → 2009-01-31 (Long, 92 days, -13.76%).** The rule "
        "flipped long too early. Permits MoM (6 months prior = April 2008) "
        "briefly clawed above the fixed 25th-percentile threshold, but equities "
        "continued falling into the March 2009 low. This is the kind of whipsaw "
        "the caveats above warn about — a pro-cyclical 6-month-lead rule cannot "
        "perfectly time a credit-driven crash.\n"
        "- **Net take-away.** Even with the January 2009 whipsaw, the 2008 "
        "regime contributed a large portion of the strategy's full-sample alpha. "
        "The short capture during the core crash dominated the subsequent "
        "drawdown. The broker-style CSV (APP-TL1 artefact) is not yet generated "
        "for permit_spy — this example is reconstructed from the raw "
        "`winner_trade_log.csv`. Flag for Vera/Ace: promote permit_spy to the "
        "broker-style artefact set in a future wave."
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
    "**Building Permits (PERMIT).** FRED series measuring new privately-owned "
    "housing units authorised each month, seasonally adjusted at annual rate "
    "(SAAR). Derived signals entered into the tournament:\n\n"
    "| Signal | Formula | Intent |\n"
    "|:-------|:--------|:-------|\n"
    "| `permit` | raw level | non-stationary; regime reference only |\n"
    "| `permit_yoy` | (permit_t / permit_{t-12}) - 1 | year-on-year growth |\n"
    "| `permit_mom` | (permit_t / permit_{t-1}) - 1 | 1-month momentum — **winner** |\n"
    "| `permit_zscore` | rolling 36M z-score of level | standardised deviation |\n"
    "| `permit_mom3m` | 3-month momentum | medium-horizon momentum |\n"
    "| `permit_mom6m` | 6-month momentum | lowest-frequency momentum |\n\n"
    "SPY daily adjusted closes (Yahoo Finance, `auto_adjust=True`) are resampled "
    "to monthly last close; forward returns are computed as "
    "`spy.shift(-h) / spy - 1` for h = 1, 3, 6, 12 months."
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

Ranked by out-of-sample Sharpe. Winner (per `results/permit_spy/winner_summary.json`,
authoritative): **S3_mom / T1_p25 / P3_long_short / L6 → OOS Sharpe 1.4454,
OOS annualised return +22.66%, max drawdown −19.42%.**
"""

_REFERENCES_MD = """
- Stock, J. H., & Watson, M. W. (1989). New indexes of coincident and leading economic indicators. *NBER Macroeconomics Annual*, 4, 351–394.
- Case, K. E., & Shiller, R. J. (2003). Is there a bubble in the housing market? *Brookings Papers on Economic Activity*, 2003(2), 299–362.
- Leamer, E. E. (2007). Housing IS the business cycle. *Proceedings — Jackson Hole Economic Policy Symposium*, Federal Reserve Bank of Kansas City, 149-233.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23–49.
- Green, R. K. (1997). Follow the leader: How changes in residential and non-residential investment predict changes in GDP. *Real Estate Economics*, 25(2), 253-270.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Full sample: 1990-01 to 2025-12 (~420 monthly observations). "
        "In-sample: 1990-01 to 2017-12 (28 years, model estimation). "
        "Out-of-sample: 2018-01 to 2025-12 (8 years, strategy evaluation). "
        "The IS/OOS cut is fixed ex-ante at 2018-01 to keep this pair "
        "comparable with INDPRO × SPY and VIX × SPY."
    ),
    plain_english=(
        "This section is the technical appendix — which data we used, how we "
        "defined each signal, what statistical tests we ran, and how to "
        "reproduce every number on the Story, Evidence, and Strategy pages. "
        "Most readers can skip it; expert readers can use it to challenge or "
        "extend the analysis."
    ),
)
