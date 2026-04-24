"""VIX/VIX3M × SPY pair configuration (Rule APP-PT1).

Wave 10I.A narrative port (Ray): prose fields authored from legacy
app/pages/8_vix_vix3m_spy_*.py (pre-migration, commit 24e2f16~1),
cross-checked against results/vix_vix3m_spy/winner_summary.json.

Pair ID: vix_vix3m_spy  (legacy Pair #11 — VIX term-structure ratio → SPY)
Winner (winner_summary.json, authoritative): S3_z126 / T2_rp75 / P1_long_cash /
L0 — OOS Sharpe 1.13, OOS return +15.31%, Max DD -21.15%, turnover 23.3/yr.
Regime context: strongest Q1 vs Q4 spread in the portal (Q1 Sharpe 6.53
vs Q4 -2.38 — 9-point differential).
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
        "The VIX/VIX3M ratio compares the 30-day 'fear gauge' to its 3-month "
        "cousin. When the short-dated number exceeds the longer-dated one "
        "(ratio above 1.0), it means traders are paying up for immediate "
        "protection faster than they are hedging over longer horizons — a "
        "signature of panic. When the ratio is below 1.0, markets are calm. "
        "This page asks whether that single ratio, computed daily from "
        "publicly available CBOE data, can time SPY exposure."
    )

    WHERE_THIS_FITS = (
        "This pair anchors the **Volatility / Options** family in the portal. "
        "It is the only daily-frequency pair among the four Wave 10I.A "
        "non-TED migrations — the other three (INDPRO, Permits, UMCSENT) are "
        "monthly macro signals. It also delivers the largest regime Sharpe "
        "spread we have observed anywhere in the catalogue."
    )

    ONE_SENTENCE_THESIS = (
        "*A 126-day z-score of the VIX/VIX3M ratio, thresholded at its "
        "75th rolling percentile, switched SPY to cash during acute term-"
        "structure backwardation and delivered an out-of-sample Sharpe of "
        "1.13 with a max drawdown of -21% versus -34% for buy-and-hold over "
        "the COVID-inclusive 2020-2025 window.*"
    )

    KPI_CAPTION = (
        "Turnover is ~23 round-trips per year — high relative to the monthly "
        "pairs but well within daily-rebalance execution budgets. The OOS "
        "annualised return is essentially in line with buy-and-hold (+15.3% "
        "vs. +15.7%); the Sharpe gain comes from drawdown compression, "
        "not from higher returns."
    )

    HERO_TITLE = "VIX Term Structure (VIX / VIX3M) vs. S&P 500"
    HERO_CHART_NAME = "vix_vix3m_spy_hero"
    HERO_CAPTION = (
        "Dual-axis view: VIX/VIX3M ratio (left) and SPY price (right). The "
        "dashed line at ratio = 1.0 marks the backwardation boundary. Every "
        "major equity drawdown — the 2008 crisis, the 2011 debt ceiling, "
        "the 2018 Volmageddon, and the 2020 COVID crash — was accompanied "
        "by a spike above 1.0. Calm, rising markets correspond to the ratio "
        "sitting well below 1.0 in contango."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by VIX/VIX3M Quartile"
    REGIME_CHART_NAME = "vix_vix3m_spy_regime_stats"
    REGIME_CAPTION = (
        "Equity performance across VIX/VIX3M ratio regimes. Q1 (low ratio, "
        "deep contango) delivers a Sharpe of **6.53**; Q4 (high ratio, "
        "backwardation / panic) delivers **-2.38**. This nearly 9-point "
        "spread is the largest regime differential observed across any pair "
        "in the portal — more than three times wider than credit spreads "
        "(~3 points) and dwarfing the IP or permits spreads."
    )

    NARRATIVE_SECTION_1 = (
        "### Why Should Stock Investors Care About the VIX Term Structure?\n\n"
        "The VIX index measures 30-day implied volatility derived from S&P 500 "
        "options. VIX3M measures the same thing over a 3-month horizon. In "
        "normal markets, longer-dated options carry a higher volatility "
        "premium (contango), so VIX/VIX3M sits below 1.0. When markets panic, "
        "traders bid up near-term protection aggressively, pushing the ratio "
        "above 1.0 into **backwardation**.\n\n"
        "This ratio captures something fundamentally important: the "
        "**urgency of fear**. It functions as a real-time put/call sentiment "
        "proxy — when near-term put demand surges relative to longer-term "
        "hedging, the ratio spikes. Unlike the VIX level alone (which can "
        "stay elevated for extended periods), the term-structure ratio "
        "reveals whether the market is experiencing acute stress versus "
        "chronic anxiety.\n\n"
        "### The Term Structure as a Fear Gauge\n\n"
        "Our analysis examines 18 years of daily data (2007-2025) to test "
        "whether the VIX/VIX3M ratio predicts S&P 500 returns. The economic "
        "logic is direct: ratio below 1.0 (contango) is the normal state — "
        "markets are calm, hedging demand is balanced, equities tend to "
        "grind higher, and the bulk of positive equity returns occur here. "
        "Ratio above 1.0 (backwardation) is acute stress — near-term put "
        "demand exceeds longer-term hedging, signalling panic, and equities "
        "underperform or crash.\n\n"
        "The backwardation line at 1.0 is not an arbitrary percentile — it "
        "is a **structural boundary** derived from options pricing theory, "
        "making it one of the most economically meaningful thresholds in "
        "the entire catalogue. This is a **counter-cyclical** relationship: "
        "the indicator rises when the stock market falls, and vice versa."
    )

    NARRATIVE_SECTION_2 = (
        "### Nuance and Limits\n\n"
        "Four historical episodes illustrate the signal's power — and its "
        "limits:\n\n"
        "1. **Global Financial Crisis (2008-2009).** The ratio spiked to "
        "extreme backwardation as Lehman Brothers collapsed. Near-term VIX "
        "exceeded 80 while VIX3M, though elevated, lagged behind. The term-"
        "structure inversion preceded the worst of the equity drawdown.\n\n"
        "2. **Debt-ceiling crisis (August 2011).** A sharp, brief "
        "backwardation spike coincided with the S&P downgrade of U.S. "
        "sovereign debt. SPY fell ~19% peak to trough; the ratio reverted "
        "to contango as the market recovered.\n\n"
        "3. **Volmageddon (February 2018).** The XIV (inverse VIX) blow-up "
        "caused a violent term-structure inversion. This was a volatility-"
        "specific event rather than a macro crisis, yet the signal correctly "
        "flagged the equity sell-off.\n\n"
        "4. **COVID crash (March 2020).** The ratio surged above 1.0 as the "
        "pandemic triggered the fastest bear market in history. The OOS "
        "period (2020-2025) includes this extreme event, providing a severe "
        "stress test for the signal.\n\n"
        "The main limit is **sample length**: VIX3M data begins in 2007, "
        "so the full sample covers only 18 years and roughly three full "
        "market cycles. Relationships calibrated on pre-2018 data may not "
        "fully capture the post-Volmageddon microstructure — a caveat "
        "worth keeping in mind before scaling capital to this rule."
    )

    SCOPE_NOTE = (
        "*Scope discipline (ECON-SD).* Only the VIX/VIX3M ratio and SPY are "
        "in-scope primary signals for this pair. The VIX3M series begins "
        "2007-12, which defines the sample start. DFF and USREC are used "
        "only as regression controls, not as trading signals."
    )

    TRANSITION_TEXT = (
        "The VIX term structure offers the most powerful regime "
        "differentiation we have observed across all indicator pairs. But "
        "does the econometric evidence confirm a statistically robust and "
        "exploitable relationship with equity returns?"
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": "The VIX/VIX3M ratio spiked into extreme backwardation in October 2008 when the VIX hit 80 while the 3-month vol surface was far less elevated. This is the defining event for this indicator: the ratio's 126-day z-score was off the charts, and SPY fell ~20% in the following two weeks. A clear long-lead case — backwardation signaled extreme panic before the final equity capitulation in March 2009.",
            "caption": "Oct 2008 VIX hit 80, ratio in extreme backwardation — z-score signal fired well before March 2009 equity trough",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": "In March 2020, the VIX spiked to 85 (exceeding GFC levels) while VIX3M remained lower — creating the sharpest and most rapid backwardation in the ratio's history. The 126-day z-score hit extreme readings. SPY fell 34% in 33 days. The Long/Cash strategy moved to cash rapidly, avoiding most of the drawdown. The signal reverted just as fast — this is a textbook coincident case for a high-frequency fear indicator.",
            "caption": "March 2020 VIX hit 85, ratio backwardation extreme — Long/Cash moved to cash within days, avoided SPY -34% crash",
        },
        {
            "slug": "rates_2022",
            "title": "Fed Hiking Cycle (2022)",
            "narrative": "Unlike the GFC or COVID, the 2022 bear market was a slow grind rather than a panic spike. VIX rose steadily (peaking around 35) but did not create sustained extreme backwardation in the ratio — the vol term structure remained relatively flat. The z-score signal fired intermittently rather than with the conviction of a panic episode. This is a partial failure case: the indicator is better suited to shock events than sustained macro-driven bear markets.",
            "caption": "2022 bear market was a grind, not a panic — VIX/VIX3M ratio never hit extreme backwardation; signal fired intermittently",
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
        "Pearson and Spearman correlations between VIX/VIX3M signal variants "
        "(ratio level, 63/126/252-day z-score, rolling percentile, ratio "
        "change, momentum, backwardation dummy) and SPY forward returns at "
        "1, 5, 10, and 21 trading-day horizons."
    ),
    question=(
        "Which transforms of the VIX/VIX3M ratio show the strongest — and "
        "most directionally consistent — relationship with forward SPY "
        "returns, and at what horizon?"
    ),
    how_to_read=(
        "Rows: ratio transforms. Columns: forward SPY return horizons in "
        "trading days. Cool colours = negative (counter-cyclical). Stars "
        "mark conventional significance."
    ),
    chart_name="vix_vix3m_spy_correlations",
    chart_caption=(
        "Pearson correlations between VIX/VIX3M signal variants and forward "
        "return horizons. Cool colours = negative (counter-cyclical). The "
        "z-score and rolling percentile signals show the strongest negative "
        "correlations with forward equity returns, confirming that elevated "
        "ratios precede weak performance."
    ),
    observation=(
        "The correlation structure is uniformly negative across signal "
        "variants and forward horizons — exactly what a counter-cyclical "
        "fear gauge should look like. The strongest correlations appear at "
        "the 1-5 trading-day horizon, consistent with the high-frequency, "
        "options-derived nature of the signal."
    ),
    interpretation=(
        "Unlike pro-cyclical macro indicators (where higher values "
        "correlate with better returns), higher VIX/VIX3M ratios are "
        "associated with *lower* forward equity returns across every "
        "variant and every horizon tested. There is no ambiguity: when "
        "near-term fear dominates, stocks suffer."
    ),
    key_message=(
        "Every transform and every horizon agrees: higher VIX/VIX3M → "
        "lower forward SPY returns. This is the cleanest directional "
        "picture in the portal."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "Jordà (2005) local projections estimate cumulative SPY response to "
        "a 1-standard-deviation VIX/VIX3M z-score shock at each horizon "
        "independently, with HAC (Newey-West) standard errors. Daily "
        "frequency provides substantially more observations than monthly "
        "macro pairs, tightening confidence bands."
    ),
    question=(
        "How does SPY respond to a VIX/VIX3M shock over the next few weeks, "
        "and over what horizon is the effect statistically significant?"
    ),
    how_to_read=(
        "X-axis: horizon in trading days. Y-axis: cumulative SPY response "
        "to a 1-σ VIX/VIX3M z-score shock. Shaded area = 95% HAC confidence "
        "band."
    ),
    chart_name="vix_vix3m_spy_local_projections",
    chart_caption=(
        "Jordà (2005) local projections with HAC (Newey-West) standard "
        "errors. Stars indicate significance at p<0.05. The coefficient "
        "shows the marginal effect of a 1-unit increase in VIX/VIX3M "
        "z-score on forward SPY returns."
    ),
    observation=(
        "The impulse response is negative, strongest at 1-5 trading days, "
        "and remains significant out to about 21 trading days. A 1-σ "
        "increase in the VIX/VIX3M ratio is associated with meaningfully "
        "lower cumulative SPY returns over the subsequent month. The "
        "confidence bands are tighter than for any monthly pair because "
        "~4,500 daily observations provide substantial statistical power."
    ),
    interpretation=(
        "The effect is both statistically and economically significant. "
        "It is consistent with — and quantitatively much larger than — "
        "what one would predict from the massive regime Sharpe differential "
        "observed in the Story page (Q1 6.53 vs Q4 -2.38). The LP result "
        "directly underwrites the L0 (no-lead) design of the trading rule: "
        "the information is embedded in the same-day signal."
    ),
    key_message=(
        "SPY responds sharply and significantly to VIX/VIX3M shocks over "
        "the subsequent month — the econometric basis for a same-day "
        "(L0-lead) Long/Cash rule."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We tested the VIX-term-structure-equity relationship with multiple "
        "econometric methods across 18 years of daily data. Two method "
        "blocks are foregrounded — correlations (for breadth across "
        "transforms and horizons) and local projections (for the dynamic "
        "response). The full battery (Granger, quantile, Markov-switching, "
        "RF walk-forward) is archived in "
        "`results/vix_vix3m_spy/core_models_20260314/`."
    ),
    "plain_english": (
        "Both statistical lenses agree: the direction is unambiguously "
        "counter-cyclical, the effect is strongest at 1-5 trading days, "
        "and remains significant for about a month. This is the cleanest "
        "econometric picture in the portal."
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "With the statistical case firmly established, we swept a "
        "5-dimensional tournament over signal transforms, threshold "
        "methods, strategy families, lead times (in trading days, since "
        "this is a daily pair), and lookback windows — 916 raw "
        "specifications pruned to 332 valid combinations. The winner is "
        "detailed on the Strategy page."
    ),
    "transition": (
        "The statistical evidence confirms a powerful counter-cyclical "
        "relationship between the VIX term structure and equity returns. "
        "The signal operates at daily frequency with strong significance. "
        "The practical question is whether investors can translate this "
        "into a profitable strategy."
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
        "The tournament winner asks one question each day: is the VIX/VIX3M "
        "ratio unusually high compared to its own recent history? Take the "
        "z-score of the ratio over the last six months of trading days; if "
        "that z-score is in the top quartile of its own recent distribution, "
        "move SPY to cash. Otherwise, stay long. No lead, no lag — just "
        "today's reading against today's threshold."
    )

    SIGNAL_RULE_MD = (
        "**Tournament winner:** Signal `S3_z126` (126-day z-score of the "
        "VIX/VIX3M ratio) / Threshold `T2_rp75` (rolling 75th percentile) / "
        "Strategy `P1_long_cash` / Lead 0 (same-day).\n\n"
        "Compute the VIX/VIX3M ratio's z-score over a trailing 126-day "
        "(6-month) window. When this z-score is below its rolling 75th "
        "percentile — meaning term-structure stress is not extreme — stay "
        "long SPY. When the z-score exceeds the 75th percentile (acute "
        "backwardation / panic), move to cash. No leverage, no shorting."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "1. **Pull VIX and VIX3M.** Yahoo Finance tickers `^VIX` and "
        "`^VIX3M`. Daily.\n"
        "2. **Compute the ratio.** `ratio_t = VIX_t / VIX3M_t`.\n"
        "3. **Compute the 126-day z-score.** Rolling 126-day mean and "
        "standard deviation of the ratio; `z_t = (ratio_t - mean) / std`.\n"
        "4. **Compute the rolling 75th-percentile threshold.** Rolling "
        "quantile of the z-score over the same 126-day window.\n"
        "5. **Translate to position.** If `z_t` < threshold → long SPY "
        "(+1). Otherwise → cash (0). Rebalance at the next market open."
    )

    MANUAL_USE_MD = (
        "This is a daily-cadence rule, so it is most practical with a "
        "simple spreadsheet or a five-line Python script rather than eyeball "
        "calculation. Pipeline-reproducible steps:\n\n"
        "1. Daily download of `^VIX` and `^VIX3M` closes from Yahoo.\n"
        "2. Keep the last 126 business days in a ring buffer.\n"
        "3. Compute ratio, z-score, and rolling 75th-percentile threshold.\n"
        "4. Rebalance SPY position at next open based on today's close.\n\n"
        "Turnover is ~23 round-trips per year — meaningful but well inside "
        "daily-rebalance execution budgets."
    )

    # No equity_curves / drawdown / walk_forward charts on disk — same
    # data gap as permit_spy. Template renders "chart pending" for those.
    TOURNAMENT_SCATTER_CHART_NAME = "vix_vix3m_spy_tournament_scatter"

    CAVEATS_MD = (
        "1. **VIX3M only available since 2007.** The sample is 18 years — "
        "shorter than for macro indicators with 30+ year histories. This "
        "limits the number of independent market cycles observed (essentially "
        "2-3 full cycles).\n\n"
        "2. **COVID-crash dominance in the OOS window.** The out-of-sample "
        "period (2020-2025) includes the March 2020 crash, which is the "
        "most extreme VIX term-structure event in the sample. The strategy's "
        "OOS performance is partly driven by correctly navigating this "
        "single event.\n\n"
        "3. **Structural changes in volatility markets.** The growth of VIX "
        "ETPs (VXX, UVXY) since 2009 and the XIV blow-up in 2018 have "
        "changed the dynamics of volatility term structure. Relationships "
        "calibrated on pre-2018 data may not fully capture post-Volmageddon "
        "microstructure.\n\n"
        "4. **Transaction-cost sensitivity.** At 23 round-trips per year, "
        "execution quality materially affects net Sharpe. Investors should "
        "verify that realistic execution costs do not erode the Sharpe "
        "advantage."
    )

    TRADE_LOG_EXAMPLE_MD = (
        "**Crisis anchor — March 2020 COVID crash.** From "
        "`results/vix_vix3m_spy/winner_trade_log.csv`:\n\n"
        "- **2020-01-24 → 2020-04-03 (Cash, 70 days).** The rule had moved "
        "SPY to cash on 24-Jan-2020, weeks before the broader market "
        "recognised the COVID threat. The VIX/VIX3M 126-day z-score had "
        "already pushed above its rolling 75th-percentile threshold as "
        "Asian markets began pricing pandemic tail risk. Holding cash "
        "through the 20-Feb-to-23-Mar crash avoided SPY's worst monthly "
        "return in a generation.\n"
        "- **2020-04-03 → 2020-10-06 (Long, 186 days, +36.09%).** The rule "
        "flipped back to long on 3-Apr-2020 as the VIX term structure "
        "normalised after unprecedented Fed intervention. Holding through "
        "the spring-summer rebound captured +36% over 186 calendar days — "
        "a direct contribution to the strategy's +15.3% OOS annualised "
        "return.\n"
        "- **Economic interpretation.** This episode is the archetypal "
        "use case: the term structure warned of coming stress before "
        "equities broke, then waved the all-clear before the recovery was "
        "obvious. The rule's same-day (L0) design is what made capture "
        "possible — any lead > 0 would have missed both the exit and the "
        "re-entry.\n"
        "- **Broker-style artefact not yet generated.** Per APP-TL1, the "
        "canonical `winner_trades_broker_style.csv` exists only for "
        "`umcsent_xlv`. Flag for Vera/Ace: promote `vix_vix3m_spy` to the "
        "broker-style artefact set in a future wave."
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
    "**VIX/VIX3M ratio.** Computed as `^VIX / ^VIX3M` at daily close. "
    "Ratio > 1 = backwardation (near-term fear dominates long-term "
    "hedging demand, signalling acute stress). Ratio < 1 = contango "
    "(the normal regime). Derived signals entered into the tournament:\n\n"
    "| Signal | Formula | Intent |\n"
    "|:-------|:--------|:-------|\n"
    "| `ratio` | VIX / VIX3M | raw ratio |\n"
    "| `ratio_z63` | 63-day z-score | short-window deviation |\n"
    "| `ratio_z126` | 126-day z-score | **winner** |\n"
    "| `ratio_z252` | 252-day z-score | annual z-score |\n"
    "| `ratio_rpct` | rolling percentile rank | distribution-free signal |\n"
    "| `ratio_chg` | day-over-day change | acceleration |\n"
    "| `backwardation` | dummy (ratio > 1) | regime indicator |\n\n"
    "SPY daily adjusted closes from Yahoo Finance; forward returns "
    "computed in trading days at horizons h = 1, 5, 10, 21."
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
| **Signals** | VIX/VIX3M level, z-score (63d/126d/252d), rolling percentile, ratio change, backwardation dummy |
| **Threshold methods** | Fixed percentile (p25/p50/p75), rolling percentile (winner = rolling p75), rolling z-score, natural boundary (ratio=1.0), HMM prob, Markov-Switching prob |
| **Strategies** | Long/Cash (P1), Signal-Strength (P2), Long/Short (P3) |
| **Lead times** | L0 (same-day, winner), L1, L2, L5, L10, L21 trading days |
| **Orientation** | Counter-cyclical (backwardation / ratio > 1 → reduce SPY exposure) |

Ranked by out-of-sample Sharpe. Winner (per
`results/vix_vix3m_spy/winner_summary.json`, authoritative): **S3_z126 /
T2_rp75 / P1_long_cash / L0 → OOS Sharpe 1.1295, OOS annualised return
+15.31%, max drawdown −21.15%, annual turnover 23.3.** Regime spread:
Q1 Sharpe 6.53 vs Q4 −2.38 — strongest regime discriminator in the portal.
"""

_REFERENCES_MD = """
- Whaley, R. E. (2000). The investor fear gauge. *Journal of Portfolio Management*, 26(3), 12–17.
- Mixon, S. (2007). The implied volatility term structure of stock index options. *Journal of Empirical Finance*, 14(3), 333-354.
- Eraker, B. (2004). Do stock prices and volatility jump? Reconciling evidence from spot and option prices. *Journal of Finance*, 59(3), 1367-1404.
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
        "Full sample: 2007-01 to 2025-12 (~4,500 daily observations). "
        "In-sample: 2007-01 to 2019-12 (13 years, model estimation). "
        "Out-of-sample: 2020-01 to 2025-12 (6 years, strategy evaluation). "
        "The OOS window is short relative to macro pairs (8 years) because "
        "VIX3M begins 2007-12; OOS performance is partly driven by the "
        "single March 2020 COVID event — read Sharpe with that caveat in mind."
    ),
    plain_english=(
        "This section is the technical appendix — data sources, signal "
        "definitions, statistical tests, and how to reproduce every "
        "number in the preceding pages. Non-specialists can skip it."
    ),
)
