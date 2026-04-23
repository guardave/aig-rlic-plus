"""INDPRO × SPY pair configuration (Rule APP-PT1).

Wave 10I.A narrative port (Ray): prose fields authored from legacy
app/pages/5_indpro_spy_*.py (pre-migration, commit 24e2f16~1), cross-checked
against results/indpro_spy/winner_summary.json.

Pair ID: indpro_spy  (legacy Pair #1)
Winner (winner_summary.json, authoritative): S6_mom3m / T1_fixed_p75 /
P1_long_cash / L6 — OOS Sharpe 1.10 vs 0.90 B&H SPY, OOS return +7.65%,
Max DD -8.07%.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Factory Output and the Stock Market"
    PAGE_SUBTITLE = (
        "Does the pace of industrial activity predict where stocks are headed?"
    )

    HEADLINE_H2 = (
        "## Industrial Production as a pro-cyclical equity timing signal — "
        "OOS Sharpe vs SPY buy-and-hold"
    )

    PLAIN_ENGLISH = (
        "Every month the Federal Reserve publishes an index of how much stuff "
        "U.S. factories, mines, and utilities produced. That number — "
        "Industrial Production, or INDPRO — turns out to be a useful clue for "
        "when to be in the stock market and when to be in cash. The rule is "
        "simple: when factory output has been trending up strongly for three "
        "months, hold SPY; otherwise step aside."
    )

    WHERE_THIS_FITS = (
        "This pair anchors the **Activity / Survey** family of the portal. "
        "INDPRO is one of the four components of the Conference Board's "
        "Coincident Economic Index and has been tracked by the Fed since 1919. "
        "It complements the forward-looking Building Permits pair and the "
        "consumer-sentiment UMCSENT pair."
    )

    ONE_SENTENCE_THESIS = (
        "*When INDPRO 3-month momentum is strong (above its in-sample 75th "
        "percentile) and applied with a 6-month lead, a simple Long/Cash rule "
        "delivered an out-of-sample Sharpe of 1.10 on SPY with a maximum "
        "drawdown of -8.1% — versus 0.90 and -23.9% for buy-and-hold.*"
    )

    KPI_CAPTION = (
        "The edge comes primarily from drawdown avoidance, not from higher "
        "returns. OOS annualised return is +7.7% versus +14.8% for buy-and-hold, "
        "but the strategy spends roughly two-thirds of its time in cash — "
        "translating into a much smoother ride. A pragmatic use case is as a "
        "risk-management overlay rather than as a stand-alone alpha engine."
    )

    HERO_TITLE = "35 Years of Industrial Production vs. S&P 500"
    HERO_CHART_NAME = "indpro_spy_hero"
    HERO_CAPTION = (
        "Dual-axis view: IP YoY growth (left, red) and SPY price (right, blue). "
        "Red shaded bands mark industrial contraction periods (YoY growth < 0). "
        "Notice how contractions tend to overlap with, or precede, equity "
        "declines — most visibly in 2001, 2008-09 and 2020."
    )

    REGIME_TITLE = "What History Shows: Returns by IP Growth Regime"
    REGIME_CHART_NAME = "indpro_spy_regime_stats"
    REGIME_CAPTION = (
        "Equity performance differs sharply across IP growth regimes. "
        "Stocks perform best during moderate growth (Q2, Sharpe ~1.09) and "
        "high growth (Q4, ~1.15), and worst during deep contractions "
        "(Q1, ~0.31). Q3 sits in between at ~0.69. The pattern is "
        "non-linear — moderate is nearly as good as strong, but weak is "
        "very costly."
    )

    NARRATIVE_SECTION_1 = (
        "### Why Should Stock Investors Care About Factory Output?\n\n"
        "Industrial Production measures the real output of the manufacturing, "
        "mining, and utility sectors. It is one of the four components of the "
        "Conference Board's Coincident Economic Index and has been tracked by "
        "the Federal Reserve Board since 1919. The index is published monthly, "
        "about six weeks after the reference month, seasonally adjusted, and "
        "indexed to 100 in the base year 2017.\n\n"
        "For stock investors, IP matters because it directly connects to "
        "**corporate earnings**. When factories are running at full capacity, "
        "companies are selling more goods, hiring more workers, and generating "
        "higher profits. When production contracts, earnings fall — and so do "
        "stock prices, usually with a lag.\n\n"
        "### The IP–Equity Connection\n\n"
        "Rising IP signals expanding manufacturing activity, higher capacity "
        "utilisation, and growing corporate earnings — bullish for stocks. "
        "Falling IP signals contraction, lower utilisation, and earnings "
        "pressure — bearish. The signal operates with a publication lag of "
        "about six weeks, and markets typically need additional time to price "
        "the information fully. This is what economists call a **pro-cyclical** "
        "relationship: the indicator and the stock market move in the same "
        "direction over the business cycle."
    )

    NARRATIVE_SECTION_2 = (
        "### The Surprise: A Peak-Cycle Warning\n\n"
        "While the overall relationship is pro-cyclical, the IP **z-score** "
        "(how far IP is from its long-term trend) shows a *negative* "
        "relationship with 12-month forward returns. When IP is well above "
        "its 5-year trend, future returns tend to be *lower*.\n\n"
        "**Interpretation.** This is a **peak-cycle effect**. At cycle highs "
        "growth is unsustainable and mean-reverts; investors who buy at the "
        "peak of industrial activity tend to underperform. This is consistent "
        "with Fama & French (1989): business conditions predict stock returns, "
        "but the relationship is nuanced, and the level and the rate of change "
        "carry different information.\n\n"
        "The practical implication is that you should pay attention to "
        "**momentum transforms** (YoY, MoM, 3M momentum) rather than levels "
        "or z-scores when building a trading rule. The tournament winner "
        "below does exactly that."
    )

    SCOPE_NOTE = (
        "*Scope discipline (ECON-SD).* Only INDPRO and SPY are in-scope "
        "primary signals. Controls (VIX, yield spread, UNRATE, capacity "
        "utilisation) are used only in regression controls — not as trading "
        "signals."
    )

    TRANSITION_TEXT = (
        "History and economic logic suggest a real connection between factory "
        "output and stock returns. But does the data confirm this statistically? "
        "We ran nine different econometric models, and the headline result is "
        "that the relationship is real but nuanced — it survives in the "
        "momentum transforms more than in the levels."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson correlations measure the linear co-movement between eight "
        "INDPRO signal variants (level, YoY, MoM, z-score, 3M/6M momentum, "
        "acceleration, contraction dummy) and SPY forward returns at 1M, 3M, "
        "6M and 12M horizons. Spearman rank correlations are run as a "
        "robustness check."
    ),
    question=(
        "Which INDPRO transforms correlate most strongly with forward SPY "
        "returns, and at which horizon?"
    ),
    how_to_read=(
        "Rows are IP signal variants; columns are forward SPY return horizons. "
        "Warm colours = positive (pro-cyclical); cool colours = negative. "
        "Stars mark conventional significance levels."
    ),
    chart_name="indpro_spy_correlations",
    chart_caption=(
        "Pearson correlations between 8 IP signal variants and 4 forward "
        "return horizons. Warm colours = positive (pro-cyclical), cool colours "
        "= negative. Note the z-score's negative correlation at 12M — the "
        "peak-cycle effect."
    ),
    observation=(
        "Momentum transforms (3M, 6M, MoM) show the strongest positive "
        "correlations at 3-6 month forward horizons. The z-score flips sign "
        "at the 12-month horizon — the peak-cycle effect surfaced in the "
        "Story page. Raw levels correlate weakly because INDPRO is "
        "non-stationary."
    ),
    interpretation=(
        "The dominant signal is **direction of change**, not level. The "
        "z-score's 12-month sign flip is a warning that stationary-looking "
        "transforms can still carry counter-intuitive information at longer "
        "horizons — a reminder that blind automation of 'higher is better' "
        "heuristics can destroy alpha."
    ),
    key_message=(
        "Momentum is the winning transform; levels and z-scores can mislead "
        "at longer horizons. The tournament will formalise this."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Cross-Correlation Function (CCF)",
    method_theory=(
        "The cross-correlation function measures the correlation between "
        "INDPRO YoY and SPY monthly returns at lags -12 to +12 months. "
        "Negative lags correspond to IP leading SPY; positive lags to SPY "
        "leading IP. Significance bands are ±1.96/√N."
    ),
    question=(
        "Does IP lead SPY, or does SPY lead IP? Is there a sharp peak "
        "predictive lag, or is the relationship diffuse?"
    ),
    how_to_read=(
        "X-axis: lag in months (negative = IP leads). Y-axis: correlation. "
        "Bars crossing the dashed confidence band are statistically significant."
    ),
    chart_name="indpro_spy_ccf",
    chart_caption=(
        "CCF at lags -12 to +12 months. Red bars are statistically "
        "significant. Negative lags indicate IP leading SPY."
    ),
    observation=(
        "The CCF shows modest but statistically significant correlations at "
        "small positive lags (SPY leading IP by 1-3 months), reflecting IP's "
        "status as a coincident/slightly-lagging indicator once publication "
        "delay is accounted for. Correlations at negative lags (IP leading "
        "SPY) are smaller."
    ),
    interpretation=(
        "IP is more coincident than leading once you strip away the "
        "publication lag. The tradable edge comes from the publication lag "
        "(six weeks) plus the persistence of IP momentum, not from IP truly "
        "leading the market."
    ),
    key_message=(
        "IP is a near-coincident indicator; the 6-month lead in the trading "
        "rule exploits publication delay and momentum persistence rather "
        "than genuine forecasting power."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "Granger causality tests whether past INDPRO readings improve "
        "forecasts of SPY returns beyond what SPY's own history already "
        "provides. F-tests are run on augmented VAR regressions at lags 1 "
        "through 6 months, in both directions."
    ),
    question=(
        "Does IP growth carry predictive content for SPY returns that is not "
        "already in SPY's own history?"
    ),
    how_to_read=(
        "Bars show p-values by lag order. Below the dashed line (p=0.05) "
        "indicates statistically significant Granger causality."
    ),
    chart_name="indpro_spy_granger",
    chart_caption=(
        "Granger causality tests in both directions. Below the dashed line "
        "(p=0.05) indicates statistically significant causality."
    ),
    observation=(
        "Results are mixed. IP growth does not strongly Granger-cause SPY "
        "returns at conventional lag orders. The reverse direction (SPY → IP) "
        "is also weak. This is consistent with IP being a coincident indicator "
        "rather than a true leading indicator — the predictive power comes "
        "from the publication lag and momentum effects, not from IP leading "
        "the economy per se."
    ),
    interpretation=(
        "Absence of Granger causality does not mean absence of tradable edge. "
        "It means the relationship is not a simple one-directional lead-lag "
        "pattern. Momentum-based rules with a 6-month lead still extract "
        "meaningful signal, as the tournament confirms."
    ),
    key_message=(
        "The IP signal is coincident, not leading. The 6-month lead is a "
        "design choice that leverages publication delay and momentum "
        "persistence — not a claim that IP literally forecasts SPY."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "Jordà (2005) local projections trace the cumulative SPY response to "
        "a 1-standard-deviation IP-growth shock at each horizon separately, "
        "with HAC (Newey-West) standard errors. Unlike a VAR, LPs do not "
        "impose parametric propagation assumptions."
    ),
    question=(
        "What is the dynamic path of SPY following an IP-growth shock, and "
        "where does the effect peak?"
    ),
    how_to_read=(
        "Point estimate of the cumulative response at each horizon; shaded "
        "area is the 95% HAC confidence band. Stars mark p<0.05."
    ),
    chart_name="indpro_spy_local_projections",
    chart_caption=(
        "Jordà (2005) local projections with HAC (Newey-West) standard "
        "errors. Stars indicate significance at p<0.05. The coefficient "
        "shows the marginal effect of a 1pp increase in IP YoY growth on "
        "forward SPY returns."
    ),
    observation=(
        "The impulse response is positive and rises through the 3-6 month "
        "horizon, then plateaus before confidence bands widen. The peak "
        "effect is economically meaningful — a one-standard-deviation IP "
        "shock translates into a measurable cumulative SPY return differential "
        "over the subsequent half year."
    ),
    interpretation=(
        "The LP path directly supports the 6-month lead chosen by the "
        "tournament. The effect is strongest at exactly the horizon the "
        "trading rule uses, which is a healthy alignment between the "
        "econometric evidence and the rule's hyperparameter."
    ),
    key_message=(
        "SPY responds significantly to IP shocks out to 6 months — the "
        "econometric justification for the winner's 6-month lead."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression (Koenker & Bassett 1978) estimates the effect of "
        "IP growth on different percentiles of the SPY return distribution, "
        "not just the conditional mean. This reveals whether the signal "
        "affects the tails more than the body."
    ),
    question=(
        "Does IP growth protect against extreme losses (left-tail "
        "protection) or mostly shift the median return?"
    ),
    how_to_read=(
        "X-axis: quantile (0.05 through 0.95). Y-axis: coefficient. A "
        "positive coefficient means higher IP growth shifts that quantile "
        "of forward SPY returns upward."
    ),
    chart_name="indpro_spy_quantile_regression",
    chart_caption=(
        "The effect of IP growth varies across the return distribution. "
        "At the left tail (worst outcomes), the coefficient tends to be "
        "positive — higher IP growth protects against extreme losses."
    ),
    observation=(
        "Coefficients are positive across most of the distribution, with "
        "the largest effects in the left tail (q=0.05-0.25). High IP "
        "growth materially compresses the worst 3-month-forward SPY "
        "outcomes."
    ),
    interpretation=(
        "The bulk of the signal's value is downside protection, not upside "
        "capture. This is exactly what a risk-management overlay should look "
        "like — and is consistent with the winner's characteristic profile "
        "(lower return, much lower drawdown)."
    ),
    key_message=(
        "IP's real contribution is compressing left-tail SPY outcomes. That "
        "is the economic meaning of the strategy's -8% max drawdown vs. "
        "-24% for buy-and-hold."
    ),
)


RF_BLOCK = dict(
    chart_status="ready",
    method_name="Random Forest Feature Importance",
    method_theory=(
        "A Random Forest classifier (200 trees, max_depth=5) is walk-forward-"
        "validated across 20 train/test windows (10-year training / 3-year "
        "testing). Feature importances are averaged across windows to rank "
        "the most informative IP transforms."
    ),
    question=(
        "When we let a machine-learning model decide which IP transforms "
        "matter most, which rise to the top?"
    ),
    how_to_read=(
        "Bars show mean feature importance across 20 walk-forward windows. "
        "Longer bars = more informative."
    ),
    chart_name="indpro_spy_rf_importance",
    chart_caption=(
        "Top features for predicting positive 3M SPY returns. "
        "Yield spread and IP z-score are the most important features, "
        "suggesting both rate and IP cycle information matter."
    ),
    observation=(
        "Walk-forward classification accuracy is **61.4%**, modestly "
        "above the 50% baseline. IP momentum transforms and the yield "
        "spread dominate the importance ranking; raw levels rank low."
    ),
    interpretation=(
        "The RF confirms what the linear methods already showed: IP "
        "provides some information, but simpler momentum-based signals "
        "outperform in the tournament. The ML framing is a useful cross-"
        "check, not a replacement for the econometric pipeline."
    ),
    key_message=(
        "61.4% walk-forward accuracy is modest but positive. The RF "
        "endorses momentum transforms and is consistent with the "
        "tournament's winning specification."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We tested the IP-equity relationship with nine econometric methods "
        "across 35 years of data. Six method blocks are foregrounded here — "
        "correlation, CCF, Granger, local projections, quantile regression, "
        "and a Random Forest importance ranking. Markov-Switching, "
        "cointegration and PELT change-point results are archived in "
        "`results/indpro_spy/core_models_20260314/`."
    ),
    "plain_english": (
        "Six different statistical lenses tell a consistent story: the IP "
        "signal is real, it is strongest in momentum transforms (not levels), "
        "and its primary value is downside protection at 3-6 month horizons."
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
        "With the econometric case established, we swept a 5-dimensional "
        "tournament over 9 signal transforms, 6 threshold methods, 3 strategy "
        "families, 5 lead times, and 3 lookback windows — ~8,100 raw "
        "specifications pruned to 1,666 valid combinations. The winning "
        "specification is on the Strategy page."
    ),
    "transition": (
        "The statistical evidence confirms a real but nuanced IP-equity "
        "relationship. The practical question is whether investors can use "
        "IP signals to improve risk-adjusted outcomes — the next page shows "
        "the winning rule and its full performance profile."
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating IP Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested hundreds of strategy combinations to find the most robust way "
        "to time SPY exposure using the Industrial Production signal."
    )

    PLAIN_ENGLISH = (
        "The tournament winner is a simple on/off rule: when factory output "
        "has been trending strongly for three months, stay fully invested "
        "in SPY; otherwise sit in cash. Act on the signal six months after "
        "you see it — because IP data is published with a lag and the "
        "economic effect on stocks unfolds over several months."
    )

    SIGNAL_RULE_MD = (
        "**Tournament winner:** Signal `S6_mom3m` (3-month IP momentum) / "
        "Threshold `T1_fixed_p75` (75th percentile, fixed in-sample) / "
        "Strategy `P1_long_cash` (Long/Cash binary toggle) / Lead 6 months.\n\n"
        "When the 3-month change in Industrial Production is above its "
        "historical 75th percentile (strong momentum), stay fully invested "
        "in SPY. Otherwise, move to cash. Apply the signal with a 6-month "
        "lead to account for IP's publication lag and the time it takes for "
        "the economy to respond."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "1. **Pull INDPRO.** FRED series `INDPRO`, monthly SA. Released "
        "~6 weeks after the reference month.\n"
        "2. **Compute 3-month momentum.** `mom3m_t = indpro_t / indpro_{t-3} - 1`.\n"
        "3. **Fix the threshold once, in-sample.** Take the 75th percentile of "
        "3-month momentum from 1990-01 to 2017-12 and keep that number.\n"
        "4. **Apply the 6-month lead.** Today's position is determined by the "
        "3-month momentum from 6 months ago.\n"
        "5. **Translate to position.** If the 6-month-lagged mom3m is above "
        "the fixed 75th-percentile threshold → long SPY (+1). Otherwise → "
        "cash (0). Rebalance monthly."
    )

    MANUAL_USE_MD = (
        "Monthly cadence using free public data:\n\n"
        "1. Download `INDPRO` from FRED.\n"
        "2. For the reading six months back, compute the 3-month change.\n"
        "3. Compare to the fixed 75th-percentile threshold (regenerated in "
        "the pipeline notebook; roughly +0.8% as of the 2017 in-sample cut).\n"
        "4. Above → hold SPY. At or below → hold cash or short-duration bills.\n"
        "5. Revisit next month. Turnover averages ~2.2 round-trips per year "
        "— essentially negligible execution cost."
    )

    EQUITY_CHART_NAME = "indpro_spy_equity_curves"
    # DRAWDOWN_CHART_NAME intentionally omitted — no drawdown chart on disk.
    # WALK_FORWARD_CHART_NAME intentionally omitted — no walk_forward chart.
    TOURNAMENT_SCATTER_CHART_NAME = "indpro_spy_tournament_scatter"

    CAVEATS_MD = (
        "1. **Publication lag matters.** IP data is released ~6 weeks after "
        "the reference month. The 6-month lead in the winning strategy "
        "accounts for this delay and is not a theoretical forecast horizon.\n\n"
        "2. **Monthly frequency limits responsiveness.** IP signals update "
        "monthly; fast-moving markets (COVID in March 2020, flash crashes) "
        "can gap before the next data point.\n\n"
        "3. **COVID outlier.** The April 2020 IP drop (-12.7% MoM) is "
        "unprecedented and may distort model estimates. The rule held cash "
        "through much of 2019-2021 which protected capital but also missed "
        "the V-shaped recovery.\n\n"
        "4. **This is a risk-management overlay, not an alpha engine.** The "
        "strategy's annualised OOS return (+7.7%) is below buy-and-hold "
        "(+14.8%). Its edge is Sharpe (1.10 vs. 0.90) and drawdown (-8% vs. "
        "-24%) — useful for investors with tight drawdown budgets, less "
        "useful as a pure return-maximiser."
    )

    TRADE_LOG_EXAMPLE_MD = (
        "**Crisis anchor — 2020 COVID crash.** From "
        "`results/indpro_spy/winner_trade_log.csv`:\n\n"
        "- **2019-03-31 → 2021-01-31 (Cash, 672 days).** Going into 2019, the "
        "6-month-lagged 3-month IP momentum had been decelerating below the "
        "in-sample 75th-percentile threshold. The rule moved to cash at the "
        "end of March 2019 and remained in cash for **22 months straight**, "
        "crossing through the entire COVID crash.\n"
        "- **Why the rule worked here.** The pro-cyclical 3M momentum signal, "
        "with its 6-month lead, had been flagging weak factory trends through "
        "late 2018 (trade war, auto slowdown). The strategy sat in cash while "
        "SPY dropped 34% between 20-Feb-2020 and 23-Mar-2020, then stayed in "
        "cash through the recovery as IP momentum took time to rebuild above "
        "the threshold.\n"
        "- **Cost of caution.** The same 22 months of cash meant the rule "
        "also missed most of the post-COVID rally, which is why OOS "
        "annualised return (+7.65%) trails buy-and-hold (+14.8%). The "
        "payoff is entirely in drawdown: -8.1% for the rule versus -23.9% "
        "for buy-and-hold.\n"
        "- **Broker-style artefact not yet generated.** Per APP-TL1, the "
        "canonical `winner_trades_broker_style.csv` exists only for "
        "`umcsent_xlv` as of Wave 10H.2. Flag for Vera/Ace: promote "
        "`indpro_spy` to the broker-style artefact set in a future wave."
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
    "**Industrial Production (INDPRO).** FRED series measuring real output "
    "of manufacturing, mining, and utilities. Monthly, seasonally adjusted, "
    "indexed to 100 in 2017. Derived signals entered into the tournament:\n\n"
    "| Signal | Formula | Intent |\n"
    "|:-------|:--------|:-------|\n"
    "| `indpro` | raw level | non-stationary; regime context only |\n"
    "| `indpro_yoy` | 12-month growth | year-on-year activity |\n"
    "| `indpro_mom` | 1-month growth | high-frequency momentum |\n"
    "| `indpro_zscore` | 60M rolling z-score | peak-cycle detector |\n"
    "| `indpro_mom3m` | 3-month momentum | **winner** |\n"
    "| `indpro_mom6m` | 6-month momentum | medium-horizon momentum |\n"
    "| `indpro_accel` | change of momentum | acceleration |\n"
    "| `indpro_contract` | dummy (YoY < 0) | contraction regime |\n\n"
    "SPY daily adjusted closes are resampled to monthly last close; forward "
    "returns computed as `spy.shift(-h) / spy - 1` for h = 1, 3, 6, 12 months."
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

The tournament tested all valid combinations and ranked by out-of-sample Sharpe.
Winner (per `results/indpro_spy/winner_summary.json`, authoritative):
**S6_mom3m / T1_fixed_p75 / P1_long_cash / L6 → OOS Sharpe 1.1036,
OOS annualised return +7.65%, max drawdown −8.07%, annual turnover 2.22,
win rate 19.8%, break-even cost ~50 bps.**
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
        "Full sample: 1990-01 to 2025-12 (432 monthly observations). "
        "In-sample: 1990-01 to 2017-12 (28 years, model estimation and "
        "threshold calibration). Out-of-sample: 2018-01 to 2025-12 (8 years, "
        "strategy evaluation). This spans two full NBER cycles (2001, 2008-09) "
        "in-sample and the COVID cycle plus 2022-23 inflation regime "
        "out-of-sample."
    ),
    plain_english=(
        "This section is the technical appendix — which data we used, how we "
        "defined each signal, what statistical tests we ran, and how to "
        "reproduce every number on the Story, Evidence, and Strategy pages. "
        "Most readers can skip it; expert readers can use it to challenge or "
        "extend the analysis."
    ),
)
