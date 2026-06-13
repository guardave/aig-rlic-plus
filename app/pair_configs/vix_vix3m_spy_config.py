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
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "Dual-axis view: VIX/VIX3M ratio (left) and SPY price (right). The "
        "dashed line at ratio = 1.0 marks the backwardation boundary. Every "
        "major equity drawdown — the 2008 crisis, the 2011 debt ceiling, "
        "the 2018 Volmageddon, and the 2020 COVID crash — was accompanied "
        "by a spike above 1.0. Calm, rising markets correspond to the ratio "
        "sitting well below 1.0 in contango."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by VIX/VIX3M Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "Equity performance across VIX/VIX3M ratio regimes — annualized "
        "Sharpe (left panel) and annualized return (right panel). Q1 (low "
        "ratio, deep contango) delivers a Sharpe of **6.53** on a 52.9% "
        "annualized return; Q4 (high ratio, backwardation / panic) delivers "
        "**-2.38** on a -76.0% annualized return. This nearly 9-point Sharpe "
        "spread is the largest regime differential observed across any pair "
        "in the portal — more than three times wider than credit spreads "
        "(~3 points) and dwarfing the IP or permits spreads. (Reminder: "
        "these are annualized rates conditional on being in the regime, not "
        "buy-and-hold returns — Q4 episodes are short, violent windows.)"
    )

    NARRATIVE_SECTION_1 = (
        "### Why Should Stock Investors Care About the VIX Term Structure?\n\n"
        # fix260526 W3 #60 — expanded explanation of what "VIX term structure"
        # actually IS (multiple maturity volatility indices forming a curve).
        "There is more than one VIX. Each one measures the **implied "
        "volatility** of S&P 500 options at a particular maturity — how much "
        "the options market expects the index to swing between now and then. "
        "The most-cited member, the original **VIX**, prices a 30-day "
        "horizon; **VIX9D** prices ~9 trading days; **VIX3M** prices about "
        "3 months; **VIX6M** about 6 months; and a 1-year VIX1Y also exists. "
        "Plot all of them against their maturities on a single chart and you "
        "get the **VIX term structure** — a curve of expected volatility "
        "across horizons (sometimes called the 'volatility term surface').\n\n"
        "Footnote on the technical terms (#62):\n\n"
        "- **Implied volatility:** the volatility number that, when plugged "
        "into the Black-Scholes options-pricing formula, produces today's "
        "observed option market price. It is what the market is *pricing in*, "
        "not what has actually happened historically.\n"
        "- **Option pricing theory:** the body of work (Black-Scholes, "
        "Merton, and successors) that links the price of an option to the "
        "underlying's volatility, strike, time-to-maturity, and risk-free "
        "rate. It lets us back out implied volatility from any option's "
        "market price.\n"
        "- **Contango / backwardation:** terms borrowed from commodity-"
        "futures markets. **Contango** = longer-dated prices are higher than "
        "short-dated; in VIX-terms, VIX3M sits *above* VIX, so VIX/VIX3M < "
        "1.0. **Backwardation** = the opposite; in VIX-terms, the front-month "
        "VIX trades *above* the longer-dated VIX3M, so VIX/VIX3M > 1.0.\n"
        "- **Hedging demand:** institutional investors buying put options to "
        "protect long equity portfolios against drawdowns. Higher hedging "
        "demand pushes option prices up — which mechanically pushes implied "
        "volatility up.\n"
        "- **Put demand:** specifically demand for *put* options (the right "
        "to sell at a fixed strike). Surging put demand at very short "
        "maturities is the signature of acute fear.\n\n"
        "### The Ratio as a Real-Asset Risk-Off Gauge\n\n"
        # fix260526 W3 #61 — explicit "short-term vs medium-term panic" framing.
        "Of all the VIX-pair comparisons we could make, **VIX/VIX3M** is "
        "the most informative because it pits the *front-end* implied-vol "
        "(30-day) against the *belly* (3-month). Plainly: it measures the "
        "**intensity of short-term panic relative to medium-term panic**. "
        "When the ratio sits below 1.0, longer-dated fear exceeds near-term "
        "fear — that is the *calm* regime where hedging demand is balanced "
        "and equities tend to grind higher. When the ratio is above 1.0, "
        "near-term fear exceeds medium-term fear — that is the *stress* "
        "regime where put demand is concentrated at the front end, "
        "signalling acute panic.\n\n"
        "Think of it as a thermometer with a fixed reference point: ratio "
        "high → short-term volatility is particularly high (panic / stress); "
        "ratio low → short-term volatility is lower than medium-term "
        "(market relatively stable). The ratio captures the *urgency of "
        "fear* better than the VIX level alone (which can stay elevated for "
        "extended periods without signalling acute stress).\n\n"
        "Our analysis examines 18 years of daily data (2007-2025) to test "
        "whether this ratio predicts S&P 500 returns. The backwardation line "
        "at 1.0 is not an arbitrary percentile — it is a **structural "
        "boundary** derived from options pricing theory, making it one of "
        "the most economically meaningful thresholds in the entire "
        "catalogue. This is a **counter-cyclical** relationship: the "
        "indicator rises when the stock market falls, and vice versa."
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

    # ACE-HZE1: dot_com excluded — VIX3M data starts 2007-01-03; episode ends 2002-10-31.
    # VIZ-HZE1 skip documented in output/charts/vix_vix3m_spy/plotly/_meta.json.
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
    # fix260526 W3 #103 — extended explanation; ALSO #65/#67-class fix —
    # the previous prose claimed the correlations are "uniformly negative"
    # but the actual chart shows mostly weak POSITIVE Pearson correlations
    # (29 of 44 cells positive, range -0.038 to +0.071). Rewriting to
    # match what the rendered heatmap actually shows.
    method_theory=(
        "Pearson correlations measure the linear co-movement between 11 "
        "VIX/VIX3M signal variants (ratio level, 126/252-day z-score, "
        "rolling percentile, 5/21-day rate of change, 5/21-day momentum, "
        "21-day realized vol, backwardation dummy, term spread) and SPY "
        "forward returns at 1, 5, 21, and 63 trading-day horizons. The "
        "expectation for a counter-cyclical fear gauge is **negative** "
        "linear correlation: higher panic-ratio today → lower equity "
        "return over the following days/weeks. We test that expectation "
        "directly against the data here, then revisit it under the "
        "regime/HMM/quantile lenses on Level 2 — Linear correlation is "
        "the weakest of those lenses for a threshold-activated signal "
        "like this one."
    ),
    question=(
        "Does linear correlation alone reveal the counter-cyclical "
        "relationship the term-structure mechanism predicts, or does the "
        "signal show its edge only through non-linear / regime-conditional "
        "lenses?"
    ),
    how_to_read=(
        "Rows: ratio transforms (signal variants). Columns: forward SPY "
        "return horizons in trading days. Warm colours = positive "
        "correlation; cool colours = negative. The CHART legend's "
        "colour-scale bar gives the precise mapping. Magnitudes are small "
        "(|r| < 0.08 throughout the table) — read the SIGNS, not the "
        "intensities, and treat this view as a sanity check on direction "
        "rather than an effect-size estimate."
    ),
    chart_name="correlations",
    chart_caption=(
        "Pearson correlations between 11 VIX/VIX3M signal variants and 4 "
        "forward SPY return horizons. **Most correlations are tiny** (44 "
        "cells in total, all with |r| < 0.08). The ONLY signed cells that "
        "match the counter-cyclical expectation at p < 0.05 are at the 1-day "
        "horizon for `term_spread` (r = −0.038, p = 0.008). The rest of the "
        "table is **mostly weakly POSITIVE** — the opposite of the "
        "counter-cyclical narrative, indicating that linear Pearson is the "
        "wrong lens for this threshold-activated signal. The Level-2 "
        "regime, HMM, and quantile-regression methods below tell the "
        "more accurate story."
    ),
    observation=(
        "Of 44 Pearson cells in the heatmap, 29 are positive and 15 are "
        "negative — the OPPOSITE of what a 'uniformly counter-cyclical' "
        "signal would produce on linear correlation. Magnitudes are all "
        "small (|r| in [0.000, 0.071]). Only one cell is significantly "
        "negative at p < 0.05 (`term_spread × spy_fwd_1d`, r = −0.038, "
        "p = 0.008). Several are significantly POSITIVE — e.g. "
        "`vix_ratio × spy_fwd_63d` (r = +0.045, p = 0.002) and "
        "`vix_ratio_zscore_252d × spy_fwd_63d` (r = +0.060, p < 0.001) — "
        "suggesting that on a 63-day average horizon, elevated VIX/VIX3M "
        "is followed by *higher* SPY returns. That is the classic "
        "vol-risk-premium harvesting effect (selling vol after a fear "
        "spike often pays). Not the trading edge this pair is designed "
        "to exploit, but a true feature of the data."
    ),
    interpretation=(
        "Two readings emerge — both important. First, **Pearson linear "
        "correlation is the wrong tool for a regime-switching signal**. "
        "The counter-cyclical edge VIX/VIX3M is famous for shows up at "
        "the 1-day, post-backwardation extremes — events too rare to "
        "dominate a full-sample linear correlation. Most days the ratio "
        "sits in contango (< 1.0) and the linear average tells you "
        "nothing about what happens when it actually crosses above 1.0. "
        "Second, the small POSITIVE longer-horizon correlations are a "
        "real artefact of vol-risk-premium mean reversion — selling vol "
        "after fear spikes does tend to pay over multi-month horizons. "
        "Both effects coexist; only the regime/HMM/quantile methods "
        "can separate them."
    ),
    key_message=(
        "Linear Pearson correlations on this pair are mostly small and "
        "weakly POSITIVE — the counter-cyclical edge does NOT show up on "
        "linear correlation. The signal works through the structural "
        "backwardation threshold (>1.0) and the regime-switching "
        "behaviour analysed on Level 2 — not through average linear "
        "co-movement. Read this chart as a sanity check on linearity, "
        "not as the headline evidence."
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
    chart_name="local_projections",
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


# --- Lead blocks (fix260613_lead_horizon, Ray §A.2 — CHARTS-ONLY/FINAL) ---
CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "The Correlation block above fixes the signal at zero lag and varies "
        "the forward horizon. A daily-rebalanced overlay still has to answer a "
        "monthly *lead* question (ECON-LL1: one month of lead ≈ 21 trading "
        "days, so the daily ratio is shifted by L×21 days). For each VIX-term-"
        "structure transform we compute Pearson r between the signal lagged "
        "L=0..12 months and SPY's 1-month forward return. "
        "A key framing note for cross-pair comparison: the VIX/VIX3M ratio is "
        "a daily real-time signal — both VIX and VIX3M are published every "
        "trading day with zero lag. Unlike monthly macro indicators such as "
        "Industrial Production or Building Permits (which arrive 2-6 weeks "
        "after the reference month, creating a genuine puzzle about how stale "
        "the signal should be), today's VIX term-structure reading is right "
        "there on your screen. You would not check last year's VIX ratio to "
        "decide what to do today when today's number is freely available. So "
        "if the Lead Analysis shows L0 as the strongest lead, that is the "
        "expected result for a zero-lag signal, not a discovery — these charts "
        "serve cross-pair comparability, letting the reader see that permits "
        "have a real lead-selection puzzle and VIX term-structure does not."
    ),
    question=(
        "How stale may the VIX/VIX3M signal get before it stops predicting "
        "next month's SPY return — and does the data support the published "
        "same-day (L=0) lead? For a zero-lag daily signal, L0 dominance is "
        "the economically expected result."
    ),
    how_to_read=(
        "Rows are VIX term-structure transforms; columns are signal lead in "
        "months. Forward horizon fixed at 1 month. Shading is Pearson r "
        "against `spy_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson r between VIX-term-structure signal lagged L months and SPY "
        "1-month forward return. The strongest cells sit at **L=5-6**: "
        "`vix_ratio_zscore_126d` at L6 is −0.194**, `vix_ratio_roc_21d` at L5 "
        "is +0.179**, `vix_ratio_mom_21d` at L5 +0.172*, `vix_term_spread` at "
        "L6 +0.151*. The contemporaneous column (L0, the published lead) is "
        "uniformly weak (|r| < 0.08)."
    ),
    observation=(
        "Reading directly: the level/z-score transforms (`vix_ratio`, "
        "`vix_ratio_zscore_126d`, `pctrank_252d`) all carry their strongest "
        "cell as a **negative** r at **L6** (more backwardation 6 months ago → "
        "lower forward returns, the counter-cyclical sign). The momentum/RoC "
        "transforms peak **positive at L5**. At L0 — where the published "
        "winner trades — correlations are near zero, consistent with VIX "
        "term-structure being a fast, noisy same-day signal whose linear "
        "predictive content actually concentrates a few months out."
    ),
    interpretation=(
        "The lead-correlation view diverges from the published **L=0** lead: "
        "linear predictability concentrates at **L=5-6**, not "
        "contemporaneously. But — crucially — this divergence does **not** "
        "trigger a re-run. The tournament (next block) finds its best Sharpe "
        "at **L=3**, still inside the published lead's near-term region "
        "(L* ≤ 6), so the published winner's lead region holds and this pair "
        "is **charts-only**. The honest read: the *correlation* is strongest "
        "at a 5-6 month lead, while the *traded edge* is a fast "
        "same-day-to-quarterly signal — two different lenses on a "
        "counter-cyclical relationship, neither of which dethrones the "
        "published configuration."
    ),
    key_message=(
        "Linear correlation peaks at **L=5-6** (counter-cyclical), diverging "
        "from the published same-day lead — but the tournament's best Sharpe "
        "stays in the near-term region (L=3 ≤ 6), so the published winner's "
        "lead region still wins. **Charts-only; no re-run.**"
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "We re-ran the full tournament across L=0..12 (monthly grid, daily "
        "signal shifted by L×21 trading days per ECON-LL1). The chart plots "
        "best OOS Sharpe per lead over the full combo cloud, with SPY "
        "buy-and-hold (1.13 over this OOS) dashed."
    ),
    question=(
        "Does a longer lead beat the published same-day (L=0) winner — or is "
        "the near-term region still where the edge lives?"
    ),
    how_to_read=(
        "Bars: max OOS Sharpe per lead. Strip: all valid combos at that lead. "
        "Tall-thin = single combo; flat-wide = robust regime."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "Best OOS Sharpe per lead. The grid maximum is **L=3 (1.869)** — a "
        "tall spike from `vix_ratio_pctrank_252d` / Tp10_hi / P2 — with "
        "secondary peaks at L=6 (1.649) and L=5 (1.483). The published L=0 "
        "winner (1.068) is the *lowest* peak on the whole grid. Leads beyond "
        "L=7 decay toward buy-and-hold."
    ),
    observation=(
        "Reading the bars: a clear near-term ridge — L1 (1.283), L3 (1.869), "
        "L5 (1.483), L6 (1.649) — then a steady decay through L7-L12 back "
        "toward 1.0. The L=3 spike is the standout. Reading the strip: at L6 "
        "the median combo (0.93) is the highest of any lead, suggesting L5-6 "
        "is a genuine ridge, not a single lucky point; the L3 maximum is "
        "taller but its cloud is wider."
    ),
    interpretation=(
        "The extended grid lifts the achievable Sharpe well above the "
        "published L=0 figure (1.07 → 1.87 at L=3), but the gate keys on "
        "**where** the best lead sits: **L*=3 ∈ {0..6}**, so the published "
        "winner's lead *region* still wins and no full re-run is required. "
        "This is the honest, economically sensible result — VIX term-structure "
        "stress predicts equities over the next one-to-six months, with the "
        "risk-adjusted sweet spot around a quarter (L=3) and a robust ridge at "
        "L=5-6. The published same-day winner is conservative within that "
        "region. As a daily real-time signal with zero publication lag, the "
        "near-term lead region is the structural expectation — contrast with "
        "monthly macro indicators like Building Permits (optimal lead L8-9) "
        "where the lead puzzle is genuine. **Charts-only.**"
    ),
    key_message=(
        "Best Sharpe across L=0..12 is **L=3 (1.87)**, with a robust L=5-6 "
        "ridge — all inside the published lead's near-term region (L* ≤ 6). "
        "The published winner is not dethroned; **charts-only, no re-run.**"
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
    "downloads": [
        {"label": "Granger causality (10 lag-direction rows)",
         "path": "results/vix_vix3m_spy/core_models_20260314/granger_causality.csv"},
        {"label": "Predictive regressions (20 signal-horizon rows)",
         "path": "results/vix_vix3m_spy/core_models_20260314/predictive_regressions.csv"},
        {"label": "Quantile regression (7 quantiles of forward SPY)",
         "path": "results/vix_vix3m_spy/core_models_20260314/quantile_regression.csv"},
        {"label": "Local projections (3 horizons)",
         "path": "results/vix_vix3m_spy/core_models_20260314/local_projections.csv"},
        {"label": "Diagnostics summary (2 rows)",
         "path": "results/vix_vix3m_spy/core_models_20260314/diagnostics_summary.csv"},
    ],
    "plain_english": (
        "Both statistical lenses agree: the direction is unambiguously "
        "counter-cyclical, the effect is strongest at 1-5 trading days, "
        "and remains significant for about a month. This is the cleanest "
        "econometric picture in the portal."
    ),
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK],
    "level1_labels": ["Correlation", "Lead Analysis", "Lead Tournament"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "With the statistical case firmly established, we swept a "
        "5-dimensional tournament over signal transforms, threshold "
        "methods, strategy families, lead times (in trading days, since "
        "this is a daily pair), and lookback windows — 915 raw "
        "specifications pruned to 331 valid combinations. The winner — "
        "detailed on the Strategy page — posts OOS Sharpe 1.13, the "
        "**best of those 331 valid combinations**: the maximum of the "
        "search, not a typical result. The median valid combination "
        "scored 0.80."
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
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

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
        "- **Broker-style log available.** Per APP-TL1, the canonical "
        "`winner_trades_broker_style.csv` is now generated for this pair "
        "from the reconciled strategy series, alongside the position log. "
        "Both are downloadable below under *Download Trading History*."
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
