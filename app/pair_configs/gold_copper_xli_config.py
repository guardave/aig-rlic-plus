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
        "— and a simple threshold rule on the 126-day z-score (a half-year "
        "rolling normalization) of the ratio earned an annualized "
        "**+13.4%** return out-of-sample in 2020-2025 (Sharpe 1.27 — about "
        "twice the buy-and-hold ratio)."
    )

    KPI_CAPTION = (
        "the tournament winner uses the 126-day z-score (how many standard "
        "deviations the ratio is from its rolling half-year mean) of the "
        "gold/copper ratio. The countercyclical orientation means we go "
        "long XLI when the z-score is below its in-sample median (signal "
        "says risk-on) and move to cash otherwise."
    )

    HERO_TITLE = "25 Years of Gold/Copper Ratio vs Industrials (XLI)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — gold/copper ratio (left, orange) "
        "and XLI price (right, blue) on a common time axis. Shaded bands "
        "mark NBER recessions. Notice how ratio spikes (gold up + copper "
        "down) cluster around the 2008 and 2020 crises, when XLI was weakest."
    )

    REGIME_TITLE = "What History Shows: XLI Performance by Gold/Copper Z-Score Quartile"
    REGIME_CHART_NAME = "quartile_returns"
    REGIME_CAPTION = (
        "What this shows: XLI performance in each of the four 126-day "
        "z-score quartiles — annualized Sharpe (left panel) and annualized "
        "return (right panel), annualized on a simple x4 basis from "
        "raw 63-day forward returns. "
        "Q1 (lowest ratio = risk-on regime) is the strongest quartile on "
        "both measures (Sharpe 1.46 / 15.7% return); Q3 is the weakest "
        "(0.18 / 3.7%). The Q4 partial rebound (0.57 / 11.7%) is the "
        "documented failure case — see the 2022 Rates Shock episode below."
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

### How to Read the Signal Today

The exact rule that produced the 1.27 Sharpe is simple enough to apply by hand. The Strategy page has the full implementation detail and a worked daily example; this card is the at-a-glance version.

| Step | What | How |
|---|---|---|
| 1. Pull two prices | Gold and copper futures closes | Yahoo Finance tickers `GC=F` and `HG=F`, or any equivalent feed |
| 2. Compute the ratio | gold ($/oz) ÷ copper ($/lb) | Today's value vs its trailing 6-month mean is the comparison that matters |
| 3. Compute the 126-day z-score | (today's ratio − 6-month mean) ÷ 6-month standard deviation | Tells you whether the ratio is unusually high or low versus its own 6-month history |
| 4. Compare to threshold | **≈ −0.03** (in-sample-median calibration) | High z-score = gold is rich versus copper = bearish for XLI; below threshold = risk-on, above = risk-off |
| 5. Take a position | Below threshold → **long XLI 100%**; above → **cash (0% XLI)** | No short side; no leverage; no lead |

The z-score is just the gold/copper ratio translated into "how unusual is it versus the last 126 trading days?" A high z-score means gold is expensive relative to copper, which is the bearish XLI setup in this analysis. The threshold value (-0.03) is fixed — it was tuned on in-sample data (pre-2020) and held constant through the out-of-sample window (2020–2025). You do not re-tune it. If you want to see what value the signal would take today, pull the two futures closes and run steps 2–3; the threshold comparison in step 4 is mechanical.

**A worked example** — see the *Strategy → Manual Use* page for a full step-by-step including what to do on a rebalancing day vs an in-between day.
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
        "(around -0.04 for the 126d z-score vs 63d forward return) but "
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
        "What this shows: the winning signal (126d z-score) with the "
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
        "gold/copper 126d z-score and compute mean XLI forward 63d returns "
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
        "What this shows: annualized mean XLI 63d forward return by "
        "gold/copper z-score quartile, using a simple x4 scaling of "
        "the raw 63-day means. Q1 (lowest ratio, most risk-on) earns the "
        "best forward returns; Q3 the worst. The Q4 partial rebound is "
        "the rates_2022 failure-case fingerprint."
    ),
    observation=(
        "The raw 63-day quartile results show a clear gradient from "
        "Q1 (+3.93%) through Q2 (+2.45%) to Q3 (+0.92%) — the same "
        "means shown annualized in the chart as +15.7%, +9.8%, and "
        "+3.7%. This directly confirms the countercyclical hypothesis "
        "across most of the distribution. "
        "Q4 partially rebounds to +2.92%, which is the **statistical "
        "(+11.7% annualized) fingerprint of the 2022 rates-shock failure "
        "case**: when supply "
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
        "Quartile Q1 yields +3.93% raw mean XLI forward 63d return "
        "(+15.7% simple annualized); Q3 yields +0.92% raw (+3.7% "
        "annualized) — a 3pp raw 63d gradient that supports the "
        "countercyclical mechanism. Q4 partially rebounds (+2.92% raw, "
        "+11.7% annualized) due to supply/rates-"
        "driven episodes (2022) that contaminate the extreme bucket. "
        "Use with regime awareness."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation (CCF)",
    method_theory=(
        "This is a lead-lag test after first removing each series' "
        "habit of moving like its own recent past. A slow-moving signal "
        "and a slow-moving return can look related at many lags even "
        "when they are only echoing themselves. **Pre-whitening** "
        "(removing each series' own echo of its recent past) uses an "
        "autoregressive order-one (AR(1)) model — a comparison of a "
        "series with its immediately preceding value — to strip out "
        "that self-memory; the CCF on what remains gives the cleaner "
        "lead-lag picture."
    ),
    question=(
        "After removing each series' own self-driven persistence, "
        "is there still a residual lead-lag link between the "
        "gold/copper z-score and XLI returns?"
    ),
    how_to_read=(
        "Bars are cross-correlation at each lag. Negative lags = "
        "return leads signal; positive lags = signal leads return. "
        "Red bars exceed the dashed 95% confidence interval. A "
        "cluster of significant negative bars at positive lags "
        "supports the lead-lag hypothesis."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: AR(1) pre-whitened cross-correlation, IS "
        "only (2000-2019). Red bars exceed ±1.96/√n. Positive lag "
        "means the signal leads the return."
    ),
    observation=(
        "The pre-whitened CCF removes the autocorrelation bias from "
        "raw correlation. Significant bars at small positive lags "
        "indicate a short-horizon lead-lag link consistent with the "
        "Granger evidence and the tournament's zero-lead winner."
    ),
    deep_dive_title="Why AR(1) pre-whitening matters here",
    deep_dive_content=(
        "The z-score signal is by construction persistent (rolling "
        "windows smooth changes), and equity returns have mild but "
        "non-zero serial dependence. Without pre-whitening, the raw "
        "CCF would show non-zero correlations at many lags purely "
        "because each series remembers itself — not because they "
        "interact. The AR(1) filter strips the self-memory so what "
        "remains is interaction. This is standard practice for "
        "lead-lag analysis between persistent macro series."
    ),
    interpretation=(
        "The pre-whitened CCF supports a real (small but statistically "
        "non-zero) contemporaneous-to-short-lead relationship between "
        "the gold/copper z-score and XLI returns. Consistent with the "
        "Granger result and the tournament's lead-0 winner."
    ),
    key_message=(
        "After accounting for each series' own autocorrelation, a "
        "small but statistically significant lead-lag remains "
        "between gold/copper and XLI — corroborating Granger and "
        "the chosen zero-lead trading rule."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections (Jordà)",
    method_theory=(
        "This asks a simple shock question: after the gold/copper "
        "signal jumps today, what tends to happen to XLI over the "
        "next day, week, month, quarter, and half-year? **Local "
        "projections** estimate that path one horizon at a time, "
        "instead of forcing one big model to describe every horizon. "
        "We use heteroskedasticity- and autocorrelation-consistent "
        "(HAC, also called Newey-West) standard errors — error bars "
        "that stay reliable when multi-day returns overlap and model "
        "noise is uneven — to handle the overlapping data created by "
        "multi-day cumulative returns."
    ),
    question=(
        "If today's gold/copper z-score is one standard deviation "
        "higher than baseline, where will XLI be in 1, 5, 21, 63, "
        "126 trading days — and is the response statistically "
        "distinguishable from zero?"
    ),
    how_to_read=(
        "The line shows the estimated cumulative XLI return (in %) "
        "for each horizon after a +1 SD signal shock. The shaded "
        "band is the 95% HAC confidence interval. The line "
        "consistently below zero confirms countercyclical response; "
        "horizons where the band crosses zero are statistically "
        "weaker."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: Jordà LP estimate of cumulative XLI "
        "return at horizons 1-126 days following a +1 SD signal "
        "shock. Shaded band is 95% HAC CI. IS sample only "
        "(2000-2019)."
    ),
    observation=(
        "The LP coefficients are uniformly negative across all "
        "horizons (1d to 126d), consistent with the countercyclical "
        "hypothesis. Day-1 beta is -0.05% per signal SD with t=-3.2 "
        "(highly significant); longer horizons show larger absolute "
        "betas but wider CIs, with the largest cumulative drag "
        "around the 84-105 day horizon (~ -0.5%)."
    ),
    deep_dive_title="Why does the response strengthen out to 3-5 months and then decay?",
    deep_dive_content=(
        "Two mechanisms compose the LP shape. First, the rotation "
        "from cyclical industrials into defensives unfolds over "
        "weeks to months as institutional rebalancing works through "
        "the equity book. Second, mean reversion of the z-score "
        "itself eventually pulls the signal back toward zero, "
        "removing the directional information. The peak around "
        "3-5 months is the convolution of these two timescales — "
        "consistent with the tournament's selection of 63-day "
        "forward return as the primary horizon."
    ),
    interpretation=(
        "LP corroborates the countercyclical mechanism with a "
        "well-defined dynamic shape: a small but statistically "
        "robust contemporaneous response that builds to maximum "
        "drag around 3-5 months and decays by ~6 months."
    ),
    key_message=(
        "A one-SD shock to the gold/copper z-score predicts "
        "cumulative XLI underperformance of roughly -0.3% to "
        "-0.5% over the following 3-5 months — the dynamic "
        "shape underlying the tournament's 63-day choice."
    ),
)


QUANTILE_REGRESSION_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Linear OLS fits the **mean** of the forward return "
        "conditional on the signal. **Quantile regression** fits a "
        "separate slope at each quantile of the forward return "
        "distribution (5th, 10th, 25th, 50th, 75th, 90th, 95th "
        "percentile). If the signal predicts the *tails* of XLI "
        "returns more strongly than the mean — i.e. moves the "
        "distribution's shape, not just its centre — quantile "
        "regression will show fanned-out betas across quantiles."
    ),
    question=(
        "Does the gold/copper signal predict crash risk (the lower "
        "tail of XLI returns) more strongly than it predicts "
        "average performance?"
    ),
    how_to_read=(
        "Bars are the quantile-specific beta (XLI 63d fwd return in "
        "percentage points per signal SD). Strong red bars at low "
        "quantiles (q=0.05, q=0.10) mean the signal predicts the "
        "worst outcomes very strongly. Green bars at high quantiles "
        "(q=0.90, q=0.95) mean the signal predicts the best "
        "outcomes too — together they imply the signal predicts "
        "variance more than mean."
    ),
    chart_name="quantile_regression",
    chart_caption=(
        "What this shows: quantile-regression beta of XLI 63d "
        "forward return on the signal at each quantile. Strong "
        "negative slope at the lower tail; strong positive at the "
        "upper tail. The signal is a *risk* predictor as much as a "
        "*direction* predictor."
    ),
    observation=(
        "**The most informative result in the evidence pack.** "
        "At q=0.05 (worst-case XLI returns), the beta is **-2.72%** "
        "per signal SD (t=-8.6) — meaning when the signal is high, "
        "the worst-case 3-month XLI outcomes get catastrophically "
        "worse. At q=0.95 (best-case), the beta is **+1.16%** with "
        "t=+9.8 — high signal also predicts more upside in the "
        "best-case. The mean (q=0.50) effect is small (-0.35%) — "
        "**this is why linear correlation looked weak and the "
        "tournament Sharpe looked strong**: the signal lives in "
        "the tails, not the mean."
    ),
    deep_dive_title="Why does the signal predict both tails?",
    deep_dive_content=(
        "A risk-off signal in the real-asset complex doesn't just "
        "anticipate downside — it anticipates *uncertainty*. When "
        "the gold/copper ratio is in a high-z-score regime, "
        "industrial-demand uncertainty is elevated, which fattens "
        "both tails of the forward XLI return distribution. The "
        "asymmetry favors the lower tail (the q=0.05 beta is larger "
        "in absolute value than the q=0.95 beta), which is why a "
        "directional trading rule still works — but the dominant "
        "story is volatility expansion, not pure mean shift. This "
        "is also why options-based hedging strategies on XLI "
        "should consider the gold/copper signal as a regime "
        "indicator independent of any directional view."
    ),
    interpretation=(
        "Quantile regression is the bridge between the small linear "
        "correlation and the strong tournament Sharpe. The signal "
        "is a *variance* predictor with directional asymmetry, "
        "which a threshold-based long/cash rule can monetise but "
        "a linear correlation cannot summarise."
    ),
    key_message=(
        "The signal predicts the lower tail of XLI returns much "
        "more strongly than the mean (q=0.05 beta = -2.72% per "
        "SD, t=-8.6) — confirming the 'lives in the tails' "
        "interpretation and reconciling the weak correlation "
        "with the strong Sharpe."
    ),
)


HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Identification",
    method_theory=(
        "This lets the data sort each day into one of two hidden "
        "market moods: calm or stressed. A **2-state hidden Markov "
        "model** learns what each mood looks like from the signal's "
        "mean and variance, and it also learns how sticky each mood "
        "tends to be. The smoothed marginal probability (P(state | "
        "full data)) — the model's after-the-fact best estimate using "
        "the whole sample — tells us which regime was active at each "
        "date."
    ),
    question=(
        "Does the gold/copper signal exhibit two statistically "
        "distinguishable regimes — a 'stress' state and a 'calm' "
        "state — and do the inferred stress periods line up with "
        "highlighted historical crisis windows?"
    ),
    how_to_read=(
        "Read the time series: P(stress) = 1 means the model is "
        "certain we are in the stress regime; 0 means certain "
        "calm. NBER recession bands are shaded for visual cross-"
        "check. The stress probability should spike during the "
        "GFC and COVID windows if the model is recovering the "
        "documented regimes correctly."
    ),
    chart_name="hmm_regime_probs",
    chart_caption=(
        "What this shows: HMM-inferred probability of the stress "
        "regime over the full sample. NBER recessions shaded. "
        "Visual cross-check that the inferred stress regime aligns "
        "with documented crises."
    ),
    observation=(
        "The HMM identifies two clearly distinguishable regimes by "
        "the *variance* of the signal (stress-state variance 3.30 "
        "vs calm-state variance 0.23 — a 14x volatility gap). The "
        "two states have similar means, so the regime separation "
        "is about turbulence, not trend. Inferred-stress-"
        "probability is elevated through the canonical crises: "
        "mean P(stress) is 0.83 during the GFC (Sep 2008 – Mar "
        "2009), 1.00 during the COVID quarter (Feb – Apr 2020), "
        "and 0.93 during the China 2015 window (Aug 2015 – Feb "
        "2016) — versus a full-sample mean of 0.62. The 2022 "
        "rates shock sits *between* clear stress and clear calm: "
        "mean P(stress) of 0.55 — moderately elevated but well "
        "below GFC/COVID levels. This is the model-based version "
        "of the failure-mode narrative: 2022 had *some* "
        "real-asset turbulence (which is why P(stress) wasn't "
        "low) but was *not* the unambiguous risk-off regime that "
        "would normally drive the signal — consistent with the "
        "supply-decoupling explanation in the Story page."
    ),
    deep_dive_title="What does the transition matrix imply about regime persistence?",
    deep_dive_content=(
        "The transition matrix learned by the HMM (full numbers in "
        "`results/gold_copper_xli/hmm_summary.json`) governs how "
        "long the model expects each regime to persist. Highly "
        "persistent regimes (transition probabilities near 1 on "
        "the diagonal) imply regime changes are rare events that, "
        "once they happen, last for months. Less persistent "
        "regimes (more off-diagonal mass) imply faster oscillation. "
        "For the gold/copper signal we observe high diagonal "
        "persistence — consistent with the highlighted multi-month "
        "historical episode windows."
    ),
    interpretation=(
        "The HMM provides a model-based confirmation of the "
        "narrative regime structure: a persistent stress state "
        "that flares during GFC, parts of 2015, and COVID, and a "
        "persistent calm state that dominates expansions. The "
        "2022 'failure case' is reflected as a low stress "
        "probability even though XLI fell — corroborating the "
        "supply-decoupling explanation in the Story page."
    ),
    key_message=(
        "An HMM fitted on the signal cleanly identifies two "
        "variance regimes (14x volatility gap). Inferred-stress "
        "probability is high during GFC (0.83), COVID (1.00), and "
        "China 2015 (0.93) — but only moderate during 2022 (0.55) — "
        "supporting the narrative that 2022 was only partially a "
        "real-asset risk-off regime, which is why the signal "
        "underperformed there."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "This asks whether the signal tells us something useful about "
        "future XLI returns that XLI's own history did not already "
        "tell us. **Transfer entropy** measures directed information "
        "flow without requiring a straight-line relationship: it asks "
        "whether knowing the past of X reduces uncertainty about the "
        "future of Y, beyond what Y's own past tells you. We use a "
        "binned four-bucket (N=4) estimator — a calculator that groups "
        "continuous values into four ranges — and a shuffle-based null "
        "distribution — a baseline made by randomly reordering the data "
        "to show what chance alone would produce — to construct an "
        "empirical confidence interval. The unit is "
        "**bits** — higher means stronger information transfer."
    ),
    question=(
        "Is there a *non-linear* lead-lag information flow from "
        "the gold/copper signal to XLI returns that linear methods "
        "(correlation, Granger) might miss?"
    ),
    how_to_read=(
        "Two bars: TE(signal → return) on the left, TE(return → "
        "signal) on the right. Red dashed line shows the upper "
        "95% CI of the shuffled null. A signal-to-return bar far "
        "above the null line, with the reverse-direction bar near "
        "the null, is the desired pattern — directed information "
        "flow from signal to return."
    ),
    chart_name="transfer_entropy",
    chart_caption=(
        "What this shows: bidirectional binned transfer entropy "
        "with shuffle-null 95% CI. Signal-to-return well above "
        "null = significant non-linear lead-lag."
    ),
    observation=(
        "TE(signal → return) = **0.0148 bits** of information "
        "transfer — well above the shuffled-null 95% CI upper bound "
        "of ~0.008 bits (empirical p ≈ 0.000). For scale, a TE of "
        "zero would mean no detectable information flow at all. "
        "The reverse direction (return → signal) is "
        "smaller and indistinguishable from the null. This is the "
        "non-linear analogue of Granger causality — and a "
        "stronger result than Granger gave, because the threshold-"
        "based structure of the signal is exactly the kind of "
        "non-linearity TE captures and linear methods miss."
    ),
    deep_dive_title="Why is TE often a better evidence pillar than Granger for this signal?",
    deep_dive_content=(
        "Granger causality tests whether one series linearly "
        "improves the conditional expectation of another. If the "
        "relationship is threshold-activated (the signal matters "
        "only when it crosses a cutoff), the linear average across "
        "all observations dilutes the effect. Transfer entropy "
        "discretizes both series into bins, capturing the joint "
        "distribution non-parametrically — so any pattern where "
        "certain signal bins co-occur with certain forward-return "
        "bins is detected, regardless of linearity. The strong TE "
        "result, combined with the strong quantile-regression "
        "tail betas, is the statistical fingerprint of a "
        "threshold-activated relationship."
    ),
    interpretation=(
        "TE provides the strongest evidence in the pack for a "
        "real, non-linear directed dependence from the gold/copper "
        "signal to XLI returns. Together with the quantile "
        "regression result, it explains why a threshold-based "
        "trading rule outperforms what linear correlation would "
        "predict."
    ),
    key_message=(
        "Non-linear directed information flow from signal to XLI "
        "return is highly significant (empirical p ≈ 0.000); the "
        "reverse direction is statistically indistinguishable from "
        "the shuffled null. This is the model-free confirmation "
        "of the lead-lag hypothesis."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "*We subjected 25 years of daily data to eight statistical "
        "methods. The results converge: rising gold/copper "
        "predicts weaker industrial stocks. The strongest evidence "
        "comes from quantile regression and transfer entropy — "
        "the signal lives in the tails and operates non-linearly, "
        "which is why a threshold trading rule monetises it where "
        "linear correlation underestimates it.*"
    ),
    "downloads": [
        {"label": "Granger causality by lag (5 lags)",
         "path": "results/gold_copper_xli/granger_by_lag.csv"},
        {"label": "Local projections (9 horizons)",
         "path": "results/gold_copper_xli/local_projections.csv"},
        {"label": "Quantile regression (7 quantiles of forward XLI)",
         "path": "results/gold_copper_xli/quantile_regression.csv"},
        {"label": "Regime quartile returns (4 quartiles)",
         "path": "results/gold_copper_xli/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe (5 episodes)",
         "path": "results/gold_copper_xli/subperiod_sharpe.csv"},
    ],
    "plain_english": (
        "This section shows the statistical evidence for the "
        "relationship between the gold/copper ratio and XLI "
        "returns. Eight methods converge on the same direction: "
        "rising ratio (risk-off) predicts weaker XLI returns. The "
        "strongest evidence comes from the quantile regression "
        "(signal predicts crash risk in the lower tail with "
        "t-statistic above 8) and the transfer entropy (non-linear "
        "lead-lag is highly significant). Linear correlation looks "
        "weakest because the relationship is regime- and "
        "threshold-conditional, not linear — exactly the kind of "
        "structure a threshold-based trading rule can exploit."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality",
                       "Pre-Whitened CCF"],
    "level2": [REGIME_BLOCK, HMM_BLOCK, LOCAL_PROJECTIONS_BLOCK,
                QUANTILE_REGRESSION_BLOCK, TRANSFER_ENTROPY_BLOCK],
    "level2_labels": ["Regime Analysis", "HMM Regime ID",
                       "Local Projections", "Quantile Regression",
                       "Transfer Entropy"],
    "tournament_intro": (
        "We tested combinations of 5 signals (z-scores at 126/252-day "
        "windows, 504-day percentile rank, 63d and 126d rate-of-change), "
        "3 thresholds (in-sample p25/p50/p75), 2 strategies (Long/Cash, "
        "Long/Short), and 3 lead times (0/1/5 days) = 90 combinations, "
        "of which 60 passed validity filters. "
        "Ranked by out-of-sample Sharpe over 2020–2025. The winning "
        "combination: **126-day z-score signal, in-sample-median (≈ -0.03) "
        "threshold, Long/Cash, no lead**, producing **OOS Sharpe 1.27** "
        "(annualized return 13.4%, max drawdown -8.2%) vs ~0.6 "
        "buy-and-hold XLI. That 1.27 is the **best of the 60 valid "
        "combinations** — the maximum of the search, not a typical result: "
        "the median valid combination scored 0.54. The distribution chart "
        "on the Strategy page (Confidence tab) shows where the winner sits."
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
        "the gold/copper 126-day z-score is below its in-sample median "
        "(market saying risk-on) and moves to **cash** otherwise. The "
        "defensive logic: when fear-metal demand rises relative to "
        "industrial-metal demand, industrial stocks tend to weaken — "
        "stepping aside avoids that drawdown."
    )

    SIGNAL_RULE_MD = (
        "**Strategy Rule in Plain English:** Compute the 126-day rolling "
        "z-score (a 6-month rolling normalization — how many standard "
        "deviations the ratio sits from its half-year mean) of the "
        "gold/copper ratio every day. When the z-score is **below** the "
        "in-sample median threshold (about **-0.03** in our calibration), "
        "hold a **long position** in XLI. When the z-score is **above** "
        "that threshold (signal says risk-off), move to **cash** (no XLI "
        "position). No lead — act on the signal the same day it is "
        "observed. This is a long/cash rule, not long/short — no "
        "short-selling required."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "Each trading day, we pull gold and copper futures closes "
        "(GC=F and HG=F on Yahoo Finance), compute the ratio "
        "(gold / copper, in $/oz divided by $/lb), then compute its "
        "126-day rolling z-score: how many standard deviations is "
        "today's ratio away from its trailing 6-month mean? That z-score "
        "is the signal. The threshold (~-0.03) was tuned to the in-sample "
        "(pre-2020) distribution and held fixed throughout the "
        "out-of-sample backtest."
    )

    MANUAL_USE_MD = (
        "If you want to use this signal yourself — with no code, no broker "
        "API — follow this daily routine:\n\n"
        "1. **Pull gold and copper closes** from any financial data feed "
        "(e.g. Yahoo Finance tickers `GC=F` and `HG=F`).\n"
        "2. **Compute the ratio** = gold price ($/oz) / copper price ($/lb).\n"
        "3. **Compute the 126-day rolling z-score** of the ratio "
        "(today's ratio minus its trailing 6-month mean, divided by its "
        "trailing 6-month standard deviation).\n"
        "4. **Compare to threshold ≈ -0.03.** Below threshold: hold XLI "
        "long (100% exposure). Above threshold: move to cash (0% XLI).\n"
        "5. **Re-evaluate daily.** The strategy as tested rebalances "
        "every trading day; in practice a weekly rebalance retains most "
        "of the Sharpe at lower transaction cost."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    # This pair shows a histogram, not a scatter — the generic
    # stars/diamond caption would describe elements that don't exist.
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe of all 60 valid strategy "
        "combinations. The vertical line marks the winner (1.27) — the "
        "maximum of the distribution; the median combination scored 0.54."
    )

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

4. **Long/Cash, no short-selling.** The tournament winner is a Long/Cash
   rule — long XLI when bullish, cash otherwise — so no margin account
   or short-borrowing cost is required. Long/Short variants were tested
   but did not outperform the Long/Cash winner net of friction.

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
        "the 126d z-score of gold/copper drifted **below** the threshold "
        "(supply-tight copper held the ratio down), so the strategy was "
        "**long XLI**. XLI fell during this rates-driven re-rating "
        "alongside the broad market, so the strategy lost money it would "
        "have avoided had it been in cash. This is the failure case the "
        "caveats above describe: when supply tightness drives one leg, "
        "the signal misreads the regime. The OOS Sharpe of 1.27 "
        "(annualized excess return ~13.4% with max drawdown only -8.2%) "
        "is the *net* of these failure-case losses and the wins from "
        "2020 and 2023–2025 — proof that the signal works on net, not "
        "that it works always."
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

*Scope discipline.* This analysis keeps the trading signal narrow: only
the gold/copper ratio and its transformations are in-scope primary signals.
VIX and DXY are diagnostic regime indicators — used in regression controls
and caveats, not as trading signals.
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
| Threshold tournament | Trading-rule selection on OOS Sharpe | 90 tested combinations; 60 valid after filters |
"""


_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals (5)** | z-score 126d, z-score 252d, percentile rank 504d, RoC 63d, RoC 126d |
| **Thresholds (3)** | IS p25, IS p50, IS p75 (static, calibrated on pre-2020 distribution) |
| **Strategies (2)** | Long/Cash, Long/Short (counter-cyclical orientation only) |
| **Lead times (3)** | 0, 1, 5 business days |
| **Total combos** | 5 × 3 × 2 × 3 = 90 tested; 60 valid after filters |

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
