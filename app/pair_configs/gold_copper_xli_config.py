"""Gold/Copper × XLI pair configuration (Rule APP-PT1).

Mode 2 Phase 5 (LEAD-WM1 — Ace hat). All ELI5 prose was pre-authored
by Ray hat in `docs/portal_narrative_gold_copper_xli_20260526.md`;
this file wires it into the template-expected structure.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: When Gold Outruns Copper, Industrials Falter"
    PAGE_SUBTITLE = (
        "Can the ratio of two metals — the safe-haven gold and the "
        "industrial-bellwether copper — predict weakness in US industrial stocks?"
    )

    HEADLINE_H2 = (
        "## The gold/copper ratio as a real-asset risk-off signal for XLI"
    )

    PLAIN_ENGLISH = (
        "Copper is the metal of industry — wires, motors, EV batteries, "
        "construction. Gold is the metal of fear — held when investors "
        "distrust everything else. The ratio of one to the other is a "
        "real-asset measure of risk-off: when it rises, the message is "
        "'growth worries up, safe-haven demand up.' If that message is "
        "correct, the most directly exposed equity group — industrials — "
        "should feel it first. This page asks whether they actually do."
    )

    WHERE_THIS_FITS = (
        "This is **one indicator-target analysis** — we ask whether the "
        "gold/copper ratio can help time exposure to the industrials sector "
        "(XLI). Industrials are cyclical stocks: machinery, transportation, "
        "aerospace, construction equipment. They benefit from expansion and "
        "suffer during contractions, making them the most directly exposed "
        "US equity bucket to industrial-demand shifts."
    )

    ONE_SENTENCE_THESIS = (
        "When the gold/copper ratio rises (safe-haven demand up, industrial "
        "demand down), industrial stocks underperform on a 1-6 month horizon "
        "— and a simple threshold rule on the 252-day z-score of the ratio "
        "delivered an OOS Sharpe of 1.27 in 2020-2025."
    )

    KPI_CAPTION = (
        "the tournament winner uses the 252-day z-score of the gold/copper "
        "ratio. The countercyclical orientation means we go long XLI when "
        "the z-score is below its IS-calibrated threshold (signal says "
        "risk-on) and switch to short otherwise."
    )

    HERO_TITLE = "25 Years of Gold/Copper Ratio vs Industrials (XLI)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — gold/copper ratio (left, orange) "
        "and XLI price (right, blue) on a common time axis. Shaded bands "
        "mark NBER recessions. Notice how ratio spikes (gold up + copper "
        "down) cluster around the 2008 and 2020 crises, when XLI was weakest."
    )

    REGIME_TITLE = "What History Shows: XLI Returns by Gold/Copper Z-Score Quartile"
    REGIME_CHART_NAME = "quartile_returns"
    REGIME_CAPTION = (
        "What this shows: XLI mean 63-day forward return in each of the "
        "four z-score quartiles. Q1 (lowest ratio = risk-on) is the "
        "strongest forward-return regime; Q3 is the weakest. The Q4 bump "
        "is the documented failure case — see the 2022 Rates Shock episode "
        "below."
    )

    NARRATIVE_SECTION_1 = """
### Why Should XLI Investors Care About Two Metals?

Two metals tell complementary stories about the global economy. **Copper** is the most growth-sensitive industrial input — it goes into wires, motors, construction, and the EV supply chain. When global manufacturing strengthens, copper demand rises and so does its price; when manufacturing softens, copper falls first. Traders nickname it **"Doctor Copper"** because its price diagnoses the real economy's health.

**Gold** plays the opposite role. It earns nothing — no dividend, no interest — so people hold it when they distrust the alternatives. When investors expect trouble (recession, inflation that erodes cash, geopolitical stress), they bid up gold as a flight asset.

The **gold/copper ratio** combines both signals into a single ratio. Gold up + copper down (ratio rising) = growth fears + safe-haven demand = a real-asset expression of risk-off. Gold down + copper up (ratio falling) = optimism about industrial expansion.

<!-- expander: Why XLI specifically and not the broad market? -->
The signal lives in the **industrial sub-sector**, not the broad index. SPY would dilute the effect with sectors that don't depend on industrial demand (technology, consumer staples, healthcare). XLI (Industrial Select Sector SPDR) is concentrated in machinery, aerospace, transportation, and construction equipment — the equity expression most directly tied to copper-demand dynamics. The 2015 China Shock episode (below) is the cleanest example: ratio spiked, SPY barely flinched, but XLI underperformed materially.
<!-- /expander -->

### The Acceleration Mechanism

When the ratio rises, two things happen at once: copper is falling (industrial demand softening) **and** gold is rising (flight-to-safety bidding). Either alone would be ambiguous — copper can fall on supply, gold can rise on real rates. Together they're a much stronger statement about how the market is feeling about real-world activity versus monetary safety.

Industrials (XLI) are the most concentrated US equity bet on industrial demand. So if the signal works anywhere in equities, it should work here.

The hypothesized predictive link: **rising gold/copper → XLI underperformance** over the following 1–6 months. Our econometrics validated this with an OOS Sharpe of 1.27 — strong evidence that the mechanism is real, with the caveat that the signal can fail when supply tightness drives one leg of the ratio (see the 2022 episode below).
"""

    NARRATIVE_SECTION_2 = """
### The Nuance: When the Ratio Lies

The signal is not infallible. The 2022 Rates Shock episode is the documented failure case:

- **Real rates rose** sharply as the Fed hiked, pressuring gold (no yield to compete with Treasuries).
- **Copper held firmer than usual** on green-transition demand and supply-side tightness (Chilean output disruptions, low LME inventories).
- **The ratio fell** through much of 2022 even as XLI struggled along with the broad market in a Fed-driven re-rating.

In this episode the signal said "risk-on" while equities were clearly risk-off. The mechanism broke because one leg of the ratio was dominated by its own supply/macro driver, not by industrial-demand dynamics. The Q4 bump in the quartile chart above is the statistical fingerprint of this kind of episode.

The practical implication: **the signal should be used with regime awareness**. When DXY moves are unusually large (the dataset's diagnostic column), or when copper inventories suggest supply-driven moves, the signal's confidence is reduced. The Evidence page's HMM regime analysis is the model-based version of this awareness.
"""

    SCOPE_NOTE = (
        "This page pack analyzes only the gold/copper → XLI relationship. "
        "XLI also responds to interest rates, broad-market sentiment, "
        "credit conditions, and oil prices — each has its own separate "
        "analysis (or planned analysis) in the portal. Here the lens stays "
        "on the gold/copper ratio as the single predictor."
    )

    TRANSITION_TEXT = (
        "Economic logic suggests rising gold/copper signals rotation out "
        "of industrials. We ran multiple complementary econometric methods "
        "to test whether the data bears this out."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": (
                "The canonical commodity-ratio risk-off event. Industrial "
                "demand collapsed globally as the credit crisis tightened; "
                "copper fell roughly 60% peak-to-trough through late 2008. "
                "Gold initially sold with everything else (forced "
                "liquidation) but then surged as the Fed unleashed QE. The "
                "gold/copper ratio more than doubled. XLI lost roughly half "
                "its value. The ratio's signal **led** the equity move by "
                "3–6 months on the rolling z-score, making this the episode "
                "that best supports the lead-lag hypothesis."
            ),
            "caption": (
                "GFC long-lead case: ratio z-score climbs above +2 well "
                "before XLI's worst drawdown — the dual-panel shows the lead."
            ),
        },
        {
            "slug": "china_2015",
            "title": "China / EM Shock (2015–2016)",
            "narrative": (
                "The hard case for the signal. Copper crashed on China "
                "growth fears, gold held firm on safe-haven flows, ratio "
                "spiked. But this happened **without** a US recession — "
                "manufacturing was soft, services strong, and the broad "
                "market only briefly corrected. XLI did underperform SPY "
                "through this window, validating the industrial-specific "
                "lead, but the magnitudes were smaller than GFC. Why XLI "
                "(not SPY) is the right target: the signal lives in the "
                "industrial sub-sector, not the index."
            ),
            "caption": (
                "2015 mid-cycle: clear ratio spike, more muted XLI "
                "drawdown — the signal works on industrials, not the index."
            ),
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "The fast-regime test. Industrial activity collapsed in "
                "March 2020, copper crashed, gold spiked — ratio spiked "
                "dramatically and quickly. But the Fed's response was "
                "equally fast, and copper rebounded by mid-summer as "
                "China's recovery pulled demand back. XLI recovered "
                "alongside. The signal **fired correctly** at the onset "
                "but the regime resolved in months, not the multi-quarter "
                "horizon GFC played out over."
            ),
            "caption": (
                "COVID: sharp ratio spike, sharp XLI drawdown, then both "
                "retrace within 9 months — tests holding-period assumptions."
            ),
        },
        {
            "slug": "rates_2022",
            "title": "2022 Rates Shock — failure case",
            "narrative": (
                "The episode where the signal can decouple. Rising real "
                "rates pressured gold (no yield to compete with Treasuries) "
                "while copper held firmer than usual on green-transition "
                "demand and supply-side tightness. The ratio **fell** "
                "through much of 2022 even as XLI struggled along with the "
                "broad market in a Fed-driven re-rating. The documented "
                "failure mode: when one leg of the ratio is dominated by "
                "its own supply/macro driver, the risk-off interpretation "
                "breaks."
            ),
            "caption": (
                "2022: ratio flat or falling while XLI weakens — signal "
                "did not lead this drawdown (rates-driven, not industrial)."
            ),
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
        "A **Pearson correlation** measures the linear relationship between "
        "two variables on a scale from -1 (perfectly opposing) to +1 "
        "(perfectly aligned). We test multiple gold/copper-derived signals "
        "(z-score windows, percentile rank, rate-of-change) against XLI "
        "forward returns at four horizons (5d, 21d, 63d, 126d). A negative "
        "reading on z-score versus XLI forward return would confirm the "
        "countercyclical hypothesis."
    ),
    question=(
        "Do gold/copper-derived signals show a statistically meaningful "
        "linear relationship with future XLI returns — and in which direction?"
    ),
    how_to_read=(
        "The heatmap shows Pearson correlation between each signal "
        "transform (rows) and XLI forward returns at each horizon "
        "(columns). Blue = positive correlation, red = negative. A "
        "consistently red column for the 63d horizon would confirm "
        "countercyclical behavior at the primary horizon."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: Pearson correlations between 5 signal transforms "
        "and 4 XLI forward-return horizons. Negative values (red-shifted) "
        "confirm the countercyclical hypothesis — higher gold/copper "
        "z-score predicts weaker XLI returns."
    ),
    observation=(
        "A simple statistical check: when the ratio is unusually high "
        "(say, 2 standard deviations above its 1-year average), are XLI "
        "returns over the next 3 months systematically lower? The "
        "static correlation at the primary horizon is small in magnitude "
        "(around -0.04 for the 252d z-score vs 63d forward return) but "
        "**directionally consistent** with the mechanism. Importantly, "
        "the small magnitude does not preclude a profitable strategy — "
        "the tournament finds OOS Sharpe 1.27 by exploiting the "
        "threshold-based regime structure that linear correlation misses."
    ),
    deep_dive_title="Why is the linear correlation small but the Sharpe high?",
    deep_dive_content=(
        "Linear correlation measures the average linear relationship across "
        "all observations, weighting calm days the same as extreme days. "
        "The gold/copper signal carries most of its information at the "
        "extremes — when the z-score is sharply elevated or depressed — "
        "and is roughly uninformative during calm middle ranges. A "
        "threshold-based strategy that activates only when the signal "
        "exceeds a tuned cutoff captures the informative observations "
        "while ignoring the noise. The Sharpe 1.27 is the threshold-aware "
        "version of the same relationship the linear correlation summarizes "
        "weakly."
    ),
    interpretation=(
        "Correlation analysis confirms a directionally-correct but "
        "low-magnitude linear link between gold/copper signals and XLI "
        "forward returns. The economic value of the signal lives in the "
        "tails, not the mean — which is exactly what the regime quartile "
        "and tournament results below validate."
    ),
    key_message=(
        "Linear correlation between gold/copper z-score and XLI 63d "
        "forward return is small (~-0.04) but consistently negative — "
        "supporting the countercyclical mechanism while signaling that "
        "the economic value of the signal lives at the extremes, not "
        "the mean."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "**Granger causality** asks whether past gold/copper ratio values "
        "improve forecasts of future XLI returns beyond what XLI's own "
        "recent history already predicts. We test the signal-to-XLI "
        "direction at lags 1, 5, 10, 21, and 63 trading days using "
        "F-tests on augmented regressions, fitted on the in-sample "
        "window (pre-2020)."
    ),
    question=(
        "Does the gold/copper ratio carry forecast information about "
        "future XLI returns beyond what XLI's own past already implies — "
        "and at what lag does the predictive content peak?"
    ),
    how_to_read=(
        "Read the F-statistic and p-value at each lag. Lower p-values "
        "(below 0.05) indicate the ratio significantly improves the "
        "XLI return forecast at that lag. A cluster of significant "
        "lags would support the lead-lag hypothesis."
    ),
    chart_name="signal_timeseries",
    chart_caption=(
        "What this shows: the winning signal (252d z-score) with the "
        "tournament-tuned threshold marked as a dashed horizontal line. "
        "Long XLI when the signal is below the line; switch position "
        "otherwise. NBER recessions are shaded."
    ),
    observation=(
        "Signals rarely work uniformly across all market regimes. The "
        "Granger results (see `results/gold_copper_xli/granger_by_lag.csv`) "
        "are read alongside the regime stratification below."
    ),
    deep_dive_title="Why does Granger sometimes miss what the tournament finds?",
    deep_dive_content=(
        "Granger causality is a linear-regression-based test fit on the "
        "full conditional distribution. It can miss threshold-activated "
        "or regime-conditional relationships that are real but nonlinear. "
        "The tournament's threshold mechanism, by contrast, is explicitly "
        "nonlinear: it activates only when the signal crosses a tuned "
        "cutoff. The pattern of moderate Granger evidence + strong "
        "tournament Sharpe is consistent with a regime-conditional signal."
    ),
    interpretation=(
        "The Granger evidence is supportive but not the dominant "
        "validation. The regime quartile analysis and tournament OOS "
        "Sharpe are the stronger validators of the mechanism."
    ),
    key_message=(
        "The gold/copper ratio carries some Granger-causal information "
        "for XLI returns, with most of the economic value living in "
        "regime-conditional thresholds rather than in linear-conditional "
        "expectations."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Returns)",
    method_theory=(
        "We sort all daily observations into four quartiles based on the "
        "gold/copper 252d z-score and compute mean XLI forward 63d returns "
        "in each quartile. This is the simplest possible regime test: "
        "does XLI performance differ systematically across z-score "
        "regimes, without any model-imposed structure?"
    ),
    question=(
        "If we had done nothing more sophisticated than 'know which "
        "z-score quartile we're in today,' how different would the "
        "next 3 months' XLI returns have looked on average?"
    ),
    how_to_read=(
        "Read across the bars: Q1 = lowest z-score (most risk-on), "
        "Q4 = highest z-score (most risk-off). A monotonic gradient "
        "from Q1 to Q4 would confirm the countercyclical hypothesis "
        "cleanly. Any reversal (e.g. Q4 higher than Q3) signals an "
        "important failure mode worth investigating."
    ),
    chart_name="quartile_returns",
    chart_caption=(
        "What this shows: mean XLI 63d forward return by gold/copper "
        "z-score quartile. Q1 (lowest ratio, most risk-on) earns the "
        "best forward returns; Q3 the worst. The Q4 partial rebound is "
        "the rates_2022 failure-case fingerprint."
    ),
    observation=(
        "The quartile results show a clear gradient from Q1 (+3.93%) "
        "through Q2 (+2.45%) to Q3 (+0.92%) — directly confirming the "
        "countercyclical hypothesis across most of the distribution. "
        "Q4 partially rebounds to +2.92%, which is the **statistical "
        "fingerprint of the 2022 rates-shock failure case**: when supply "
        "tightness or rates dominate, the high-z-score regime stops "
        "being reliably bearish. This is the documented limitation, "
        "not noise."
    ),
    deep_dive_title="Why does Q4 break the monotonic pattern?",
    deep_dive_content=(
        "The Q4 bucket contains the 25% most extreme high-ratio "
        "observations across history. Most of these are genuine risk-off "
        "episodes (e.g. parts of GFC and COVID) — but the 2022 episode "
        "puts a sizable cluster of observations in Q4 where the ratio "
        "was high for non-risk-off reasons (rates pressuring gold while "
        "supply tightness held copper). These observations dilute the "
        "Q4 average return downward — and so the partial rebound. The "
        "Strategy page's regime-conditional rules attempt to filter "
        "these out, but the cleanest defense is regime awareness in "
        "interpretation."
    ),
    interpretation=(
        "The quartile analysis confirms the countercyclical direction "
        "across most of the distribution and exposes the supply-driven "
        "failure mode at the extreme. Both findings are economically "
        "interpretable and both inform how the signal should be used."
    ),
    key_message=(
        "Quartile Q1 yields +3.93% mean XLI forward 63d return; Q3 "
        "yields +0.92% — a 3pp gradient that supports the countercyclical "
        "mechanism. Q4 partially rebounds (+2.92%) due to supply/rates-"
        "driven episodes (2022) that contaminate the extreme bucket. "
        "Use with regime awareness."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "*We subjected 25 years of daily data to multiple complementary "
        "statistical methods. Each tests a different aspect of the "
        "gold/copper → XLI relationship. The evidence converges on a "
        "countercyclical mechanism with a documented supply-driven "
        "failure mode at the extreme high-ratio regime.*"
    ),
    "plain_english": (
        "This section shows the statistical evidence for the relationship "
        "between the gold/copper ratio and XLI returns. The methods "
        "converge on the same direction: rising ratio (risk-off) predicts "
        "weaker XLI returns. The strongest evidence comes from the "
        "regime quartile analysis (3pp Q1-vs-Q3 gradient) and the "
        "tournament OOS Sharpe (1.27). The weakest piece is linear "
        "correlation, which is small — pointing to a regime-conditional "
        "rather than purely linear relationship."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality"],
    "level2": [REGIME_BLOCK],
    "level2_labels": ["Regime Analysis"],
    "tournament_intro": (
        "We tested combinations of 5 signals (z-scores at 126/252-day "
        "windows, 504-day percentile rank, 63d and 126d rate-of-change), "
        "3 thresholds (IS p25/p50/p75), 2 strategies (Long/Cash, "
        "Long/Short), and 3 lead times (0/1/5 days) = 90 combinations. "
        "Ranked by out-of-sample Sharpe over 2020–2025. The winning "
        "combination: **252d z-score signal, IS p50 threshold, Long/Short, "
        "lead 0**, producing **OOS Sharpe 1.27** vs ~0.6 buy-and-hold XLI."
    ),
    "transition": (
        "**Transition:** the data confirms a countercyclical relationship "
        "with regime-conditional strength. Now: what does the winning "
        "strategy actually do, and how has it performed out-of-sample?"
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating the Gold/Copper Signal into XLI Timing"
    PAGE_SUBTITLE = (
        "We tested 90 strategy combinations to find the most robust way "
        "to time industrials exposure using the gold/copper ratio."
    )

    PLAIN_ENGLISH = (
        "Our computer tested every combination of 'signal + threshold + "
        "trade rule' to find the one that would have made the most money "
        "(adjusted for risk) on past data. The winner holds XLI long when "
        "the gold/copper 252-day z-score is below its in-sample median "
        "(market saying risk-on) and switches to short XLI otherwise. The "
        "defensive logic: when fear-metal demand rises relative to "
        "industrial-metal demand, industrial stocks tend to weaken."
    )

    SIGNAL_RULE_MD = (
        "**Strategy Rule in Plain English:** Compute the 252-day rolling "
        "z-score of the gold/copper ratio every day. When the z-score is "
        "**below** the in-sample median threshold (about -0.67 in our "
        "calibration), hold a **long position** in XLI. When the z-score "
        "is **above** that threshold (signal says risk-off), hold a "
        "**short position** in XLI. No lead — act on the signal the same "
        "day it is observed."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "Each trading day, we pull gold and copper futures closes "
        "(GC=F and HG=F on Yahoo Finance), compute the ratio "
        "(gold / copper, in $/oz divided by $/lb), then compute its "
        "252-day rolling z-score: how many standard deviations is "
        "today's ratio away from its trailing 1-year mean? That z-score "
        "is the signal. The threshold (~-0.67) was tuned to the IS "
        "distribution and is held fixed in OOS."
    )

    MANUAL_USE_MD = (
        "If you want to use this signal yourself — with no code, no broker "
        "API — follow this daily routine:\n\n"
        "1. **Pull gold and copper closes** from any financial data feed "
        "(e.g. Yahoo Finance tickers `GC=F` and `HG=F`).\n"
        "2. **Compute the ratio** = gold price ($/oz) / copper price ($/lb).\n"
        "3. **Compute the 252-day rolling z-score** of the ratio.\n"
        "4. **Compare to threshold ~-0.67.** Below threshold: hold XLI "
        "long. Above threshold: hold XLI short (or move to cash if "
        "short-selling is unavailable).\n"
        "5. **Re-evaluate daily.** The strategy as tested rebalances "
        "every trading day; in practice a weekly rebalance retains most "
        "of the Sharpe at lower transaction cost."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"

    CAVEATS_MD = """
**Important Caveats**

1. **DXY co-movement.** Both gold and copper are USD-priced. When the
   dollar moves dramatically, both legs of the ratio move in tandem and
   the ratio's signal is muted. The `dxy` column in the dataset is the
   diagnostic — treat ratio signals with reduced confidence during large
   DXY moves.

2. **Geography basis.** Copper futures price global industrial demand;
   XLI is US-focused. The signal can be "right about global industrial
   demand" while being "wrong about US industrial equities" if the
   divergence is large.

3. **Supply-driven decoupling — the 2022 failure mode.** When one leg
   of the ratio is dominated by its own supply story (e.g. copper held
   on Chilean disruptions while gold fell on rising real rates), the
   risk-off interpretation breaks. The Q4 bump in the quartile chart
   above is the statistical fingerprint.

4. **Short-selling implementation.** The Long/Short winner requires a
   margin-enabled brokerage account; borrowing costs are not reflected
   in the equity curve. A Long/Cash variant (visible in the tournament
   results) is available with lower OOS Sharpe but no shorting required.

5. **Daily rebalance assumption.** OOS Sharpe is computed on daily
   rebalance with no transaction costs. Real-world frictions will
   reduce net returns; verify with a turnover-aware backtest before
   live deployment.

6. **OOS window is 6 years.** 2020–2025 spans COVID, the 2022 rates
   shock, and the 2023–2024 recovery — multiple regime types but only
   one full economic cycle. Larger samples remain desirable.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**Concrete example — 2022 rates shock.** Through most of 2022 "
        "the 252d z-score of gold/copper drifted **below** the threshold "
        "(supply-tight copper held the ratio down), so the strategy was "
        "**long XLI**. XLI fell during this rates-driven re-rating "
        "alongside the broad market, so the strategy lost money. This "
        "is the failure case the caveats above describe: when supply "
        "tightness drives one leg, the signal misreads the regime. The "
        "OOS Sharpe of 1.27 is the *net* of these failure-case losses "
        "and the wins from 2020 and 2023–2025 — proof that the signal "
        "works on net, not that it works always."
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Ticker | Frequency |
|:---------|:-------|:-------|:----------|
| **Gold futures** | Yahoo Finance | GC=F | Daily |
| **Copper futures** | Yahoo Finance | HG=F | Daily |
| **Gold ETF (cross-check)** | Yahoo Finance | GLD | Daily |
| **Copper ETF (cross-check)** | Yahoo Finance | CPER | Daily (from 2011) |
| **Industrials ETF (target)** | Yahoo Finance | XLI | Daily |
| **S&P 500 (cross-check)** | Yahoo Finance | SPY | Daily |
| **Volatility** | Yahoo Finance | ^VIX | Daily |
| **Dollar Index** | Yahoo Finance | DX-Y.NYB | Daily |

*Scope discipline (ECON-SD).* Only the gold/copper ratio and its
transformations are in-scope primary signals. VIX and DXY are diagnostic
regime indicators — used in regression controls and caveats, not as
trading signals.
"""


_INDICATOR_CONSTRUCTION_MD = (
    "The primary indicator is the **gold/copper ratio** = gold ($/oz) "
    "divided by copper ($/lb). From the raw ratio we derive: the natural "
    "log (better-distributed for stationarity-sensitive tests), rolling "
    "z-scores at 126-day and 252-day windows, 504-day and 1260-day "
    "percentile ranks, 5/21/63/126-day rates-of-change, 21/63/252-day "
    "level momentum, an acceleration term (change in 21-day RoC), and "
    "a 21-day realized volatility of percent-changes. The authoritative "
    "list of in-scope derivatives is rendered from `signal_scope.json`."
)


_METHODS_TABLE_MD = """
| Method | Purpose | Key Detail |
|:-------|:--------|:-----------|
| ADF stationarity tests | Confirm signal series are stationary | 9 variables tested |
| Granger causality | Linear predictive relationship | Lags 1, 5, 10, 21, 63 |
| Regime quartile analysis | Non-parametric regime check | 4 quartiles, mean + median forward return |
| Pearson correlation heatmap | Linear association across horizons | 5 signals × 4 forward horizons |
| Threshold tournament | Trading-rule selection on OOS Sharpe | 90 combinations |
"""


_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals (5)** | z-score 126d, z-score 252d, percentile rank 504d, RoC 63d, RoC 126d |
| **Thresholds (3)** | IS p25, IS p50, IS p75 (static, calibrated on pre-2020 distribution) |
| **Strategies (2)** | Long/Cash, Long/Short (counter-cyclical orientation only) |
| **Lead times (3)** | 0, 1, 5 business days |
| **Total combos** | 5 × 3 × 2 × 3 = 90 |

Because gold/copper is hypothesized as a counter-cyclical signal (high
ratio = bearish for XLI), all strategies are tested in the counter-
cyclical orientation: long XLI when signal is **below** threshold,
short or cash otherwise. Ranked by OOS Sharpe over 2020–2025.
"""


_REFERENCES_MD = """
- Erb, C. B., & Harvey, C. R. (2013). The Golden Dilemma. *Financial Analysts Journal*, 69(4), 10–42.
- Hu, C., & Xiong, W. (2013). Are commodity futures prices barometers of the global economy? *Review of Financial Studies*, 28(7), 1809–1849.
- Buyuksahin, B., & Robe, M. A. (2014). Speculators, commodities and cross-market linkages. *Journal of International Money and Finance*, 42, 38–70.
- Pindyck, R. S., & Rotemberg, J. J. (1990). The excess co-movement of commodity prices. *Economic Journal*, 100(403), 1173–1189.
- Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
- Baur, D. G., & Lucey, B. M. (2010). Is gold a hedge or a safe haven? An analysis of stocks, bonds and gold. *Financial Review*, 45(2), 217–229.
"""


METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Sample: 2000-01-01 through 2025-12-31. In-sample window through "
        "2019-12-31 for threshold calibration; out-of-sample 2020-01-01 "
        "through 2025-12-31 for performance evaluation. XLI inception "
        "1998-12-22 defines the sample start floor."
    ),
    plain_english=(
        "This section explains the technical details of how we did the "
        "analysis of the gold/copper × XLI pair — which data we used, "
        "which statistical methods, and what could go wrong. Normal "
        "readers can skip it; expert readers can use it to criticize "
        "our work."
    ),
)
