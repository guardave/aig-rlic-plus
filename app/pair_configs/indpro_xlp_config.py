"""INDPRO × XLP pair configuration (Rule APP-PT1).

Pair-specific narrative content for the Story / Evidence / Strategy /
Methodology templates. Only content that cannot be derived from the
producer JSON / CSV artifacts lives here.

Content provenance (all text migrated from the prior hand-written pages
under `app/pages/14_indpro_xlp_*.py`, 2026-04-20 wave, AppDev Ace):
  - Story narrative (SECTION_STORY, SECTION_NUANCE, thesis, plain English,
    expanders) — originally from `14_indpro_xlp_story.py`.
  - Evidence method blocks (CORRELATION, GRANGER, REGIME) — originally
    from `14_indpro_xlp_evidence.py`.
  - Strategy plain-English + caveats + signal generation — originally
    from `14_indpro_xlp_strategy.py`.
  - Methodology data-sources / methods / tournament / references —
    originally from `14_indpro_xlp_methodology.py`.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    """Story-page content object (passed to `render_story_page`)."""

    PAGE_TITLE = "The Story: When the Factory Hums, Staples Stumble"
    PAGE_SUBTITLE = (
        "Does industrial activity predict returns in the defensive "
        "consumer staples sector?"
    )

    HEADLINE_H2 = (
        "## Factory-output acceleration as a defensive sector timing signal"
    )

    PLAIN_ENGLISH = (
        "When factories are running at full speed and the economy is "
        "growing, investors tend to shift money away from boring, defensive "
        "stocks like soap and cereal companies — and toward more exciting, "
        "growth-oriented ones. This research asks: can we use factory "
        "output data to predict when that rotation happens? It turns out "
        "you can — at least partially. When industrial production is "
        "accelerating, consumer staples ETF (XLP) tends to lag behind. The "
        "signal isn't perfect, but it can help reduce how badly you lose "
        "during bad periods."
    )

    WHERE_THIS_FITS = (
        "This is **one indicator-target analysis** — we ask whether INDPRO "
        "momentum can help time exposure to the consumer staples sector "
        "(XLP). Consumer staples are defensive stocks: companies that sell "
        "essential goods like food, beverages, and household products. "
        "They tend to outperform when the economy weakens and underperform "
        "when the economy accelerates — the opposite of the broad market."
    )

    ONE_SENTENCE_THESIS = (
        "Rising industrial production signals economic expansion, which "
        "triggers rotation away from defensive consumer staples — and "
        "watching that signal can help investors avoid the worst periods "
        "in XLP while capturing the defensive upside during slowdowns."
    )

    KPI_CAPTION = (
        "the tournament winner uses IP acceleration (the rate of change of "
        "MoM IP growth) as the signal, with a 3-month lead time. The "
        "countercyclical orientation means we hold XLP when IP momentum "
        "is slowing — the defensive trade."
    )

    HERO_TITLE = "27 Years of Industrial Production vs. Consumer Staples (XLP)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — IP YoY growth (left, red) and "
        "XLP price (right, blue) on a common time axis. Red shaded bands "
        "mark industrial contraction periods (YoY growth < 0). Notice how "
        "XLP often holds up or outperforms during contractions — the "
        "defensive effect."
    )

    REGIME_TITLE = "What History Shows: XLP Returns by IP Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: XLP annualized Sharpe ratio in each of the four "
        "IP growth quartile regimes. Q1 (lowest IP growth) and Q2 tend to "
        "be where XLP earns its keep; Q3 and Q4 (highest IP growth) are "
        "less favorable for this defensive ETF."
    )

    NARRATIVE_SECTION_1 = """
### Why Should XLP Investors Care About Factory Output?

Consumer staples are the ultimate defensive sector. Companies like Procter & Gamble, Coca-Cola, and Walmart sell products people need regardless of the economic cycle — toothpaste, soft drinks, and groceries don't disappear during recessions. This is exactly why they behave differently from the broad market.

When the economy is expanding (factories busy, unemployment low, corporate earnings rising), investors typically shift money from defensive sectors toward growth-oriented ones — technology, industrials, consumer discretionary. This "rotation away from defensives" causes XLP to underperform relative to the broad market.

When the economy contracts (factories idle, layoffs rising, earnings falling), the rotation reverses. Investors seek safety in the reliable cash flows of staples companies. XLP outperforms.

<!-- expander: What is XLP and what does it hold? -->
XLP (Consumer Staples Select Sector SPDR Fund) is an exchange-traded fund that tracks the S&P 500 Consumer Staples sector. It holds roughly 35-40 large-cap US companies in food, beverages, tobacco, household products, and personal care. Top holdings include Procter & Gamble, Coca-Cola, PepsiCo, Costco, and Walmart. The ETF has been trading since December 1998.

Key characteristics:
- **Beta < 1**: Less volatile than the broad market (historically ~0.55-0.65)
- **Dividend yield**: Higher than average — staples companies are reliable dividend payers
- **Sector concentration**: Top 5 holdings represent ~45% of the ETF's weight
- **Defensive behavior**: Historically outperforms in recessions and underperforms in bull markets
<!-- /expander -->

### The INDPRO-XLP Connection

Our analysis tests whether Industrial Production growth rates predict XLP returns. The economic logic operates through two channels:

**Channel 1: The Rotation Mechanism.** Rising IP signals expanding manufacturing activity. When IP accelerates, institutional investors — pension funds, endowments, hedge funds — rotate their equity exposure away from defensive sectors (staples, utilities, healthcare) toward cyclical sectors (industrials, materials, technology). This rotation reduces demand for XLP shares, depressing its relative performance.

**Channel 2: The Earnings Effect.** Consumer staples companies are relatively insulated from IP cycles because their revenues depend on consumer spending, not industrial production. But during strong expansions, raw material costs rise (packaging, agricultural inputs), squeezing staples margins, while revenues remain flat. This creates a mild earnings headwind that stock prices gradually reflect.

The combined prediction: **rising IP → XLP underperformance; falling IP → XLP outperformance.** This is the opposite of what we expect for the broad S&P 500, where rising IP is bullish. XLP is the defensive case.

### The Acceleration Signal

Our tournament found that the winning signal is not IP *level* or IP *YoY growth*, but IP *acceleration* — the change in the month-over-month growth rate. This is mathematically the second derivative of the production index: not "how fast are factories growing?" but "is that growth speeding up or slowing down?"

Why acceleration? Because financial markets are forward-looking. By the time IP *level* or *YoY growth* signal a regime shift, the rotation has already begun. IP acceleration, however, can detect the early inflection point — the moment growth begins to slow before a full contraction arrives, or the moment recovery begins to gain steam.

<!-- expander: How does IP acceleration differ from IP momentum? -->
**IP Momentum (MoM):** Monthly percentage change in the IP index. Measures current expansion or contraction speed. Positive = factories expanding, negative = contracting.

**IP Acceleration:** The change in MoM percentage change from one month to the next. Positive acceleration = expansion is speeding up. Negative acceleration = expansion is slowing (may signal approaching peak or contraction).

The acceleration signal is inherently noisier than level or momentum signals (because differentiation amplifies high-frequency variation), which is why it benefits from a smoothing lag (L3 = 3-month lead in the winner). But its early-warning property outweighs the noise cost in the OOS period.
<!-- /expander -->
"""

    NARRATIVE_SECTION_2 = """
### The Nuance: XLP Is Not a Mechanical Inverse of the IP Cycle

If XLP perfectly mirrored the inverse of industrial production, building a profitable strategy would be trivial. Reality is more complex:

- **XLP still earns positive absolute returns** in expansion periods — defensive stocks grow earnings over time even if they rotate out temporarily. The countercyclical relationship is about *relative* performance, not absolute losses.
- **The relationship has regime-dependent strength.** During deep contractions (Q1 of IP growth), XLP's defensive properties shine. During mild slowdowns, the advantage is more modest.
- **Dividend yield provides a floor.** XLP's historically higher-than-market dividend yield (around 2.5-3%) cushions performance during mild underperformance periods.
- **COVID distorted the signal.** The COVID shock (April 2020: IP -12.7% MoM) was extreme and indiscriminate — everything fell, and then everything bounced, overwhelming normal regime patterns.

The practical implication for strategy design: **a simple "hold XLP when IP contracts" rule misses important nuance.** The winning strategy instead uses IP acceleration with a rolling percentile threshold, which is more adaptive to the current IP regime.
"""

    SCOPE_NOTE = (
        "This page pack analyzes only the INDPRO → XLP relationship. "
        "XLP performance also responds to interest rates (higher rates "
        "hurt dividend stocks), consumer sentiment, and commodity input "
        "costs — but each of those has its own separate analysis in the "
        "portal. Here the lens stays on industrial production as the "
        "single predictor."
    )

    TRANSITION_TEXT = (
        "Economic logic suggests rising factory output signals rotation "
        "away from defensive consumer staples. We ran 9 econometric "
        "methods to test whether the data bears this out."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dot_com",
            "title": "Dot-Com Bust (2000–2002)",
            "narrative": "When industrial production turned negative in 2000–2001, investors rotated into defensive consumer staples — XLP outperformed SPY significantly during this period. The INDPRO acceleration signal turned bearish on IP early, correctly flipping the strategy long XLP (and short the broader market). This is the clearest long-lead case for the countercyclical mechanism.",
            "caption": "2001 IP contraction drove rotation into consumer staples — INDPRO accel signal correctly anticipated XLP outperformance",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": "XLP held up far better than SPY during the GFC, confirming the defensive rotation thesis. The INDPRO acceleration signal turned sharply negative in late 2007 as manufacturing decelerated, producing a sustained long-XLP signal through 2009. A strong coincident-to-leading case: signal fired early, and the defensive play paid off across the entire crisis window.",
            "caption": "GFC: XLP outperformed SPY by ~40pp; INDPRO acceleration signal correctly positioned long defensives",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": "The April 2020 INDPRO collapse (-12.7%) should have sent the signal sharply long XLP. However, COVID hit all sectors simultaneously — XLP experienced its own meaningful drawdown. The strategy was mechanically correct (defensive rotation) but the diversification benefit was compressed by the synchronized nature of the shock. A partial failure case where the signal was right but the target underdelivered.",
            "caption": "COVID hit all sectors simultaneously — XLP drew down with SPY, limiting the defensive benefit of INDPRO's signal",
        },
        {
            "slug": "china_2015",
            "title": "China Slowdown / EM Stress (2015–2016)",
            "narrative": "The 2015–2016 US manufacturing contraction was mild but sustained, and XLP did outperform SPY over this window as investors sought stability. The INDPRO acceleration signal caught the deceleration early and held a long-XLP tilt. A moderate success case: direction correct, but the outperformance margin was narrower than during the GFC or dot-com period.",
            "caption": "2015-16 mild IP contraction: XLP modestly outperformed SPY — INDPRO accel signal directionally correct, smaller payoff",
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 8-element method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "A **Pearson correlation** measures the linear relationship between two variables "
        "on a scale from -1 (perfectly opposing) to +1 (perfectly aligned). We test "
        "multiple INDPRO-derived signals (level, YoY growth, MoM change, z-score, "
        "acceleration) against XLP forward returns at four horizons (1M, 3M, 6M, 12M). "
        "A rolling correlation view shows how the relationship has evolved over time."
    ),
    question=(
        "Do any INDPRO-derived signals show a statistically meaningful linear "
        "relationship with future XLP returns — and in which direction?"
    ),
    how_to_read=(
        "The chart shows rolling 12M and 36M Pearson correlations between INDPRO YoY "
        "growth and XLP monthly return over the full sample. A consistently negative "
        "reading confirms the countercyclical hypothesis: higher IP growth coincides "
        "with weaker XLP returns. The dashed vertical line marks the start of the "
        "out-of-sample period (2019-01)."
    ),
    chart_name="correlations",
    chart_caption=(
        "What this shows: rolling Pearson correlation between INDPRO YoY growth and "
        "XLP monthly return. Negative values (below zero) confirm countercyclical "
        "behavior — rising industrial production is associated with weaker consumer "
        "staples performance. The relationship has been persistent but not constant."
    ),
    observation=(
        "Rolling correlations are predominantly negative across the full sample, "
        "confirming the countercyclical hypothesis. The 12M rolling correlation "
        "oscillates between roughly -0.4 and +0.2, with the most negative readings "
        "during industrial expansions. The static Pearson correlation table shows "
        "the IP z-score has the strongest link to 12M forward XLP returns "
        "(r=-0.187, p=0.002). The acceleration signal shows weaker point correlation "
        "but higher predictive utility in the tournament — consistent with a "
        "nonlinear, threshold-based relationship."
    ),
    deep_dive_title="Why does IP z-score outperform IP level in static correlations?",
    deep_dive_content=(
        "The z-score normalizes the level of IP growth relative to its recent history, "
        "which removes the long-run trend in industrial production. Over 27 years, IP "
        "has a mild upward trend, so the raw level is partly a proxy for time. The "
        "z-score, by standardizing against a rolling window, captures whether current "
        "production is *unusually* high or low relative to recent norms — which is the "
        "economically relevant signal for sector rotation decisions. Investors rotate "
        "away from defensives not when IP is high in absolute terms, but when it is "
        "high relative to recent expectations."
    ),
    interpretation=(
        "Correlation analysis confirms a real countercyclical link between IP signals "
        "and XLP forward returns. The relationship is most pronounced at the 12-month "
        "horizon and for normalized signals (z-score). The rolling correlation view "
        "shows the relationship is persistent but regime-dependent — it strengthens "
        "during clear industrial cycles and weakens during idiosyncratic shocks (COVID)."
    ),
    key_message=(
        "INDPRO z-score shows a statistically significant negative correlation with "
        "12-month forward XLP returns (r=-0.187, p=0.002): higher industrial production "
        "relative to recent history is associated with XLP underperformance — "
        "the classic defensive rotation signal."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "**Granger causality** asks whether past INDPRO values improve forecasts of "
        "future XLP returns, above what XLP's own recent history already predicts. "
        "We test both directions (INDPRO → XLP and XLP → INDPRO) at lags 1-6 months, "
        "using F-tests on augmented VAR regressions with HC3 robust standard errors. "
        "The cross-correlation function (CCF) serves as the primary visual for "
        "lead-lag structure."
    ),
    question=(
        "Does industrial production carry information about future consumer staples "
        "equity returns that is not already priced into the XLP return series itself — "
        "and at what lag does this predictive content peak?"
    ),
    how_to_read=(
        "The CCF chart shows bars at lags -12 to +12 months. Negative lags mean "
        "INDPRO leads XLP (IP first, then XLP reacts). Bars outside the dashed "
        "95% confidence bands are statistically significant. A cluster of significant "
        "negative bars would confirm IP as a leading indicator for XLP."
    ),
    chart_name="ccf",
    chart_caption=(
        "What this shows: cross-correlation function between INDPRO YoY growth "
        "and XLP monthly return at lags -12 to +12 months. Red bars are statistically "
        "significant at 95% confidence. Bars at negative lags indicate IP leading XLP."
    ),
    observation=(
        "The CCF confirms that INDPRO carries predictive content for XLP at negative "
        "lags (IP leading XLP), with the most significant bars at lags -1 to -6 months. "
        "INDPRO is a coincident indicator (released with a 6-week lag), so the practical "
        "tradable lead comes from the publication lag rather than true economic advance. "
        "The formal Granger causality tests show INDPRO YoY Granger-causes XLP returns "
        "at lags 1-3 (p < 0.05). The reverse direction (XLP → INDPRO) is not "
        "significant, confirming the directional relationship."
    ),
    deep_dive_title="If INDPRO is a coincident indicator, how can it be used predictively?",
    deep_dive_content=(
        "INDPRO measures current industrial output, not future output. However, "
        "two sources of practical predictive content exist. First, publication lag: "
        "INDPRO for month T is released roughly 6 weeks later, giving investors "
        "a window to act on confirmed industrial acceleration before equity prices "
        "fully reflect it. Second, momentum persistence: IP acceleration in month T "
        "tends to continue for 2-3 months, creating a short-lived lead for the "
        "portfolio signal. The tournament winner exploits the publication lag by "
        "using a 3-month lead parameter (L3), which effectively says 'act on data "
        "confirmed 3 months ago but still informative about the current regime.'"
    ),
    interpretation=(
        "Industrial production Granger-causes XLP returns at lags 1-3 months, "
        "while XLP does not Granger-cause INDPRO. The one-directional pattern is "
        "economically sensible: factory output feeds through to sector rotation "
        "over weeks to months as institutional investors rebalance, but equity "
        "prices do not drive manufacturing decisions."
    ),
    key_message=(
        "INDPRO leads XLP at 1-3 month lags in Granger causality tests — "
        "a one-way relationship consistent with industrial output as an input to "
        "sector rotation decisions, not a consequence of equity performance."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Descriptive Statistics)",
    method_theory=(
        "We sort all monthly observations into four quartiles based on the INDPRO "
        "acceleration signal and compute full return statistics for XLP in each "
        "quartile. This is the simplest possible regime test: does XLP performance "
        "differ systematically across IP acceleration regimes, without any "
        "model-imposed structure?"
    ),
    question=(
        "If we had done nothing more sophisticated than 'hold XLP when IP is "
        "decelerating and move to cash when IP is accelerating,' how would "
        "that strategy have performed across historical regimes?"
    ),
    how_to_read=(
        "The chart shows annualized Sharpe ratio and return for XLP in each quartile "
        "of the INDPRO signal. Q1 = lowest signal values (IP decelerating most). "
        "Q4 = highest signal values (IP accelerating most). A clear gradient from "
        "Q1 (highest XLP Sharpe) to Q4 (lowest) would confirm the countercyclical "
        "defensive rotation hypothesis."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: annualized XLP Sharpe ratio and return by quartile "
        "of the INDPRO acceleration signal. Q1 = IP decelerating most (best XLP "
        "regime), Q4 = IP accelerating most (worst XLP regime). The gradient "
        "reveals the countercyclical relationship."
    ),
    observation=(
        "The regime statistics show a clear gradient confirming the countercyclical "
        "hypothesis: XLP earns its highest risk-adjusted returns in Q1 and Q2 (low "
        "or negative IP acceleration), while Q3 and Q4 (strong IP acceleration) "
        "are associated with the weakest XLP Sharpe ratios. The OOS strategy "
        "(Sharpe 1.1147, annualized return 14.1%, max drawdown -13.5% over 84 months) "
        "exploits precisely this regime differential by holding XLP only when the "
        "INDPRO acceleration signal is below the 0.75 threshold (upper quartile rule)."
    ),
    deep_dive_title="Why does the 0.75 threshold outperform a simple median split?",
    deep_dive_content=(
        "The tournament tested 7 threshold methods including percentile splits at "
        "0.25, 0.50, and 0.75 (upper quartile). The 0.75 upper quartile threshold "
        "won because XLP's defensive properties are most consistently present across "
        "a broad range of IP conditions — the asset class is defensive even in mild "
        "expansions. The signal is most useful for identifying the *extreme* IP "
        "acceleration regime (top quartile) when the rotation away from defensives "
        "is strongest and most sustained. A median split generates too many false "
        "exits from XLP during normal expansionary months where the defensive "
        "benefit is still available."
    ),
    interpretation=(
        "The regime analysis confirms the countercyclical direction: Q1 (IP "
        "decelerating) is the best regime for XLP on a risk-adjusted basis, while "
        "Q4 (IP strongly accelerating) is the worst. The strategy captures this "
        "by using an upper-quartile threshold (0.75) to identify only the most "
        "adverse regime for XLP, staying invested otherwise."
    ),
    key_message=(
        "IP acceleration above the 75th percentile (Q4) is the worst regime for "
        "XLP returns. The tournament winner exploits this by moving to cash only "
        "in the top IP quartile — holding XLP through all other conditions and "
        "achieving OOS Sharpe of 1.1147 vs 0.9 buy-and-hold."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "*We subjected 27 years of monthly data to multiple complementary "
        "statistical methods. Each is designed to test a different aspect of "
        "the INDPRO-XLP relationship. All converge on the same direction: "
        "countercyclical — rising IP is bearish for XLP, falling IP is "
        "bullish for XLP.*"
    ),
    "plain_english": (
        "This section shows the statistical evidence for the relationship between "
        "industrial production (INDPRO) and consumer staples ETF (XLP) returns. "
        "Multiple methods all converge on the same direction: when industrial "
        "production accelerates, XLP tends to underperform — investors rotate "
        "away from defensive staples toward cyclical growth sectors. The winning "
        "signal (IP acceleration) works because markets are forward-looking: the "
        "inflection point in factory output growth anticipates the sector rotation "
        "before the full level shift occurs."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality"],
    "level2": [REGIME_BLOCK],
    "level2_labels": ["Regime Analysis"],
    "tournament_intro": (
        "We tested combinations of signals (IP level, YoY, MoM, z-score, "
        "acceleration), thresholds (7 methods including percentile cuts), "
        "strategies (Long/Cash, Long/Short), and lead times (0-6 months). "
        "These were ranked by out-of-sample Sharpe ratio over 2019-2025. "
        "The winning combination: **IP acceleration signal, 0.75 percentile "
        "threshold, Long/Cash, L3 lead**, producing OOS Sharpe 1.1147 vs 0.90 "
        "buy-and-hold XLP."
    ),
    "transition": (
        "**Transition:** Multiple statistical methods confirm the countercyclical "
        "relationship: rising industrial production signals rotation away from "
        "defensive consumer staples. Now: what does the winning strategy actually "
        "do, and how has it performed out-of-sample?"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    """Strategy-page content object (passed to `render_strategy_page`)."""

    PAGE_TITLE = "The Strategy: Translating IP Signals into XLP Timing"
    PAGE_SUBTITLE = (
        "We tested thousands of strategy combinations to find the most "
        "robust way to time consumer staples exposure using industrial "
        "production signals."
    )

    PLAIN_ENGLISH = (
        "Our computer tested every combination of 'signal + threshold + trade "
        "rule' to find the one that would have made the most money (adjusted "
        "for risk) on past data. The winner holds XLP when industrial "
        "production is decelerating and moves to cash (or short) when "
        "production accelerates. The defensive logic: when factories hum, "
        "investors chase growth stocks and staples lag."
    )

    SIGNAL_RULE_MD = (
        "**Strategy Rule in Plain English:** Monitor the acceleration of "
        "Industrial Production (how quickly the monthly growth rate is "
        "changing). When IP acceleration is in its **upper quartile** "
        "(economy speeding up fast), hold a **short / underweight position** "
        "in XLP. When IP acceleration is below that threshold (growth "
        "slowing or contracting), hold a **long position** in XLP. Apply "
        "the signal with a 3-month lead to account for the publication "
        "lag and the time markets take to react."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "Each month when FRED publishes Industrial Production, we compute "
        "two numbers: the month-over-month growth rate and its own "
        "month-over-month change (the acceleration). We then ask where "
        "today's acceleration sits within the rolling 504-month window of "
        "historical readings — below the 75th percentile is 'decelerating "
        "enough for staples'; above the 75th percentile is 'accelerating "
        "hard enough to rotate out of staples'. Because INDPRO is released "
        "with a 6-week lag, the effective lead is three months, which is "
        "also the horizon at which the research shows the signal has the "
        "tightest link to forward XLP returns."
    )

    MANUAL_USE_MD = (
        "If you want to use this signal yourself — with no code, no broker "
        "API — follow this monthly routine:\n\n"
        "1. **Pull INDPRO from FRED** (series `INDPRO`) on the third Friday "
        "of each month (roughly when the prior month's value is released).\n"
        "2. **Compute the month-over-month percentage change**, then "
        "compute that series' own month-over-month change (the "
        "acceleration).\n"
        "3. **Rank today's acceleration** against the last 504 months of "
        "history. If it sits above the 75th percentile, move XLP exposure "
        "toward cash or an underweight. If it sits below, hold or restore "
        "full exposure.\n"
        "4. **Re-rank monthly** — the threshold is rolling, not a fixed "
        "number. The signal is a regime indicator, not a daily trading "
        "tool."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

    CAVEATS_MD = """
**Important Caveats**

1. **Countercyclical orientation.** The winning strategy bets *against* high IP
   acceleration — it holds XLP when factories are slowing down. This is the
   opposite of the INDPRO × SPY strategy. Investors must not mix the two signals.

2. **Publication lag.** IP data is released ~6 weeks after the reference month.
   The 3-month lead in the winning strategy accounts for this delay.

3. **Long/short implementation.** The winning strategy uses a long/short
   orientation. Short-selling XLP requires a brokerage account with margin
   privileges and incurs borrowing costs not reflected in these results.

4. **High turnover (≈10x/yr).** Monthly rebalancing is required. Transaction
   costs and slippage will reduce net returns; verify robustness with the
   transaction cost sensitivity table.

5. **COVID outlier.** April 2020 IP contraction (-12.7% MoM) is extreme.
   The model parameters may be distorted by this observation.

6. **XLP sample starts 1998.** Only 27 years of history — less than the
   INDPRO × SPY pair's 35-year history. OOS period (84 months) is substantial
   but one full cycle remains desirable for confirmation.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**Concrete example — COVID 2020 industrial shock.** On "
        "**2020-02-29** the signal read industrial-production "
        "acceleration of **+0.992** (a firming manufacturing pulse), "
        "and the countercyclical rule told us to **SELL XLP to 0%** "
        "(cash) at a close of **$49.18**. One month later, on "
        "**2020-03-31**, the COVID lockdown wrecked the factory data: "
        "INDPRO acceleration collapsed to **-4.248**, a deep-negative "
        "reading that deliberately fires the long leg — so the log "
        "shows a **BUY back to 100% XLP** at **$46.46**, buying "
        "consumer staples into the worst of the equity sell-off. That "
        "sequence (rows dated 2020-02-29 and 2020-03-31 in "
        "`winner_trades_broker_style.csv`) is exactly the "
        "countercyclical logic the tournament selected: lean defensive "
        "when the economy is accelerating hard (staples underperform "
        "growth) and lean back into staples when the industrial cycle "
        "is collapsing. By **2020-05-31** acceleration had "
        "mean-reverted sharply to **+14.8%** and the log exits again, "
        "crystallising the gain."
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Industrial Production** | FRED | INDPRO | Monthly |
| **Consumer Staples ETF** | Yahoo Finance | XLP | Daily → Monthly |
| **S&P 500 (benchmark)** | Yahoo Finance | SPY | Daily → Monthly |
| **Volatility** | Yahoo Finance | ^VIX | Daily → Monthly |
| **Treasury yields** | FRED | DGS10, DTB3 | Daily → Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |
| **Unemployment** | FRED | UNRATE | Monthly |
| **Capacity Utilization** | FRED | TCU | Monthly |

*Scope discipline (ECON-SD).* Only INDPRO and XLP are in-scope primary signals.
Controls (VIX, yield spread, UNRATE, CAPUT) are used only in regression
controls, not as trading signals. Any predictive value observed in the
controls is logged under Analyst Suggestions below — not added to this
pair's signal universe.
"""


_INDICATOR_CONSTRUCTION_MD = (
    "The primary indicator is the FRED Industrial Production index "
    "(`INDPRO`, monthly). From this raw series we derive: the level, "
    "year-over-year growth (YoY%), month-over-month growth (MoM%), the "
    "deviation from a rolling trend, the z-score against a 252-month "
    "rolling window, momentum (3M and 6M windows), acceleration (the "
    "month-over-month change in MoM%), and a contraction dummy. The "
    "authoritative list of in-scope derivatives is rendered from "
    "`signal_scope.json` in the **Signal Universe** section below. INDPRO "
    "is released with a ~6-week publication lag, so all signal "
    "transformations are computed on lagged data and the strategy applies "
    "an additional lead parameter to account for the time markets take to "
    "react."
)


_METHODS_TABLE_MD = """
| Method | Purpose | Key Detail |
|:-------|:--------|:-----------|
| Granger causality | Linear predictive relationship (both directions) | Up to 6 monthly lags |
| Predictive OLS | Baseline regression with HC3 robust SEs | 3 signals × 4 horizons = 12 regressions |
| Local projections (Jorda) | Impulse response at multiple horizons | HAC (Newey-West) standard errors |
| Regime-dependent LP | Interaction with contraction dummy | Tests asymmetric countercyclical effect |
| Markov-Switching regression | 2-state regime identification | Switching variance, 500 EM iterations |
| Quantile regression | Distributional effects | 7 quantiles (0.05 to 0.95) |
| Johansen cointegration | Long-run equilibrium test | Log levels, det_order=1 |
| PELT change-point detection | Structural breaks in IP YoY | RBF kernel, penalty=10 |
| Random Forest | Walk-forward feature importance | 200 trees, max_depth=5 |
"""


_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals (9)** | IP level, YoY%, MoM%, deviation from trend, z-score, 3M momentum, 6M momentum, acceleration, contraction dummy |
| **Threshold methods (5)** | Fixed IS percentile (p25/p50/p75), rolling percentile (p25/p50/p75), rolling z-score (±1.0/±1.5/±2.0), zero-crossing |
| **Strategies (3×2)** | Long/Cash, Signal-Strength, Long/Short — each in pro-cyclical and counter-cyclical orientation |
| **Lead times (5)** | 0, 1, 2, 3, 6 months |
| **Orientation** | Both pro-cyclical and countercyclical tested for each combo |

Because XLP is a defensive ETF, we expect IP acceleration to be
**negatively** correlated with future XLP returns. Standard threshold
strategies generate a 'long when above threshold' rule (pro-cyclical).
For XLP, the **counter-cyclical** orientation inverts this: *long XLP
when the IP signal is BELOW the threshold* (i.e., when IP growth is slow
or contracting). Both orientations were tested exhaustively; the
counter-cyclical strategies dominated the leaderboard.
"""


_REFERENCES_MD = """
- Chen, N. F., Roll, R., & Ross, S. A. (1986). Economic forces and the stock market. *Journal of Business*, 59(3), 383–403.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23–49.
- Stock, J. H., & Watson, M. W. (1989). New indexes of coincident and leading economic indicators. *NBER Macroeconomics Annual*, 4, 351–394.
- Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384.
- Ang, A., & Bekaert, G. (2007). Stock return predictability: Is it there? *Review of Financial Studies*, 20(3), 651–707.
- Hahn, J., & Lee, H. (2006). Yield spreads as alternative risk factors for size and book-to-market. *Journal of Financial and Quantitative Analysis*, 41(2), 245–269.
"""


METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "OOS window determined by formula: "
        "OOS = min(max(36, round(N×0.25)), 120) = min(max(36, 84), 120) "
        "= 84 months. XLP IPO was December 1998; the sample starts "
        "January 1998 to capture full-year INDPRO context for derived signals."
    ),
    plain_english=(
        "This section explains the technical details of how we did the "
        "analysis of the INDPRO × XLP pair — which data we used, which "
        "statistical methods, and what could go wrong. Normal readers can "
        "skip it. Expert readers can use it to criticise our work and "
        "suggest improvements."
    ),
)
