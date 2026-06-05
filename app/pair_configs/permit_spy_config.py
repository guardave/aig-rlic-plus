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
        "can you actually trade on it?\n\n"
        "**The traded signal on this page is `permit_mom1m` — the 1-month "
        "percentage change (month-over-month, MoM) in the seasonally-adjusted "
        "PERMIT level.** The hero chart below plots a smoother 12-month "
        "(year-over-year, YoY) view because annual change is easier to read "
        "across a 36-year span; the strategy itself uses the noisier 1-month "
        "version because that turned out to be the tournament winner. Keep the "
        "distinction in mind: **YoY for the eye, MoM for the trade.**"
    )

    WHERE_THIS_FITS = (
        "This pair sits in the **Activity / Survey** indicator family of the "
        "portal. Building Permits has been part of the Conference Board's "
        "Leading Economic Index since 1959, so it is one of the oldest and "
        "best-pedigreed leading indicators in the catalogue."
    )

    ONE_SENTENCE_THESIS = (
        "*Monthly Building Permits growth (MoM change, 6-month lead) is a "
        "pro-cyclical signal that historically delivered an out-of-sample "
        "(OOS) Sharpe of 1.45 on SPY versus 0.90 for buy-and-hold. "
        "Plain-English definitions for OOS, in-sample, Sharpe ratio and other "
        "technical terms are available in the sidebar glossary on the left.*"
    )

    KPI_CAPTION = (
        "The out-of-sample (OOS) period runs 2018-01 to 2025-12. The winning "
        "Long/Short strategy doubles gross exposure versus the Long/Cash "
        "benchmark, which explains part of the return premium but also the "
        "tighter max-drawdown profile."
    )

    HERO_TITLE = "Building Permits vs. S&P 500 Over the Business Cycle"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "Dual-axis view: **Permits YoY % growth** (left axis, red — used here for "
        "visual smoothness only) and SPY price (right axis, blue). The traded "
        "signal is the 1-month-momentum (MoM) version of the same series, not "
        "the YoY shown here — see the Methodology page for the exact definition. "
        "Permits peaked before the 2001 and 2008 recessions and collapsed during "
        "the housing crisis, providing an early warning signal for equity declines. "
        "The 2020 COVID dip was shorter and V-shaped, and permits led the recovery "
        "by several months."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by Building-Permit Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "SPY Sharpe by Building Permits growth quartile. The high-growth regime "
        "(Q4) delivers a Sharpe near 0.95; the deep-contraction regime (Q1) falls "
        "to roughly 0.75. The narrow spread suggests permits work best as a "
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
            "narrative": "Permits peaked in January 2006 and fell for nearly four years — one of the longest and deepest collapses in the series history. The 1-month momentum signal turned bearish in 2006, well before the equity market peaked in October 2007. This is the strongest long-lead case in the series: permits led the equity top by ~18 months.",
            "caption": "Permits peaked Jan 2006, fell 4 years — the GFC's earliest macro warning, leading equity top by 18 months",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": "Permits collapsed briefly in April 2020 but recovered sharply by June 2020 on a wave of pandemic-era housing demand. The 1-month momentum signal fired bearish, then turned bullish almost immediately — a fast coincident case. The signal correctly identified the turn but the window was extremely short, illustrating that permits work best for slow business-cycle turns rather than sharp event-driven shocks.",
            "caption": "COVID permits: brief April 2020 collapse, then V-shaped recovery — signal called the turn but the window was extremely short",
        },
        {
            "slug": "china_2015",
            "title": "China Slowdown / EM Stress (2015–2016)",
            "narrative": "US permits grew steadily through 2015–2016 despite global headwinds, reflecting strong domestic housing demand and low mortgage rates. The momentum signal stayed positive. SPY was volatile but did not crash — a success case for the signal's \"stay long\" reading.",
            "caption": "2015-16: US permits continued rising despite EM stress — signal stayed positive through the volatility",
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
        "cool colours (red) indicate negative. **Stars mark statistical "
        "significance — `*` for p<0.05, `**` for p<0.01.** For the precise "
        "definition of each signal variant (`mom`, `yoy`, `zscore_60m`, "
        "`dev_trend`, etc.) see the **Methodology → Indicator Construction** "
        "and **Signal Universe** sections."
    ),
    chart_name="correlations",
    chart_caption=(
        "Pearson correlations between Building Permits signal variants (rows) and "
        "forward SPY return horizons (1, 3, 6, 12 months). Warm colours = positive "
        "(pro-cyclical). The strongest cell on the chart is **`zscore_60m` at 12 "
        "months (+0.217)**, followed by `yoy` at 12 months (+0.178). Magnitudes "
        "are modest in absolute terms — none exceeds 0.25."
    ),
    observation=(
        "Reading the chart directly: correlations are positive almost everywhere, "
        "but most cells are small (≤0.10) and only **6 of the 32 cells are "
        "statistically significant at the 5% level** — all of them in the "
        "6-month and 12-month columns on smoothed transforms. The relationship "
        "strengthens with forward horizon, not weakens — the **largest "
        "correlations sit in the 12-month column** (zscore_60m +0.217**, yoy "
        "+0.178**, dev_trend +0.144**, mom_6m +0.110*, contraction −0.119*). "
        "The traded signal `mom` (1-month momentum) is the weakest of the "
        "transforms tested — peaking only mildly at the 3-month horizon "
        "(+0.075, **not significant at 5%**) and falling back to +0.040 at "
        "12 months. Not a single `mom` cell carries a star."
    ),
    interpretation=(
        "Two honest takeaways. First, the relationship is real and "
        "pro-cyclical — every transform-by-horizon cell except a single "
        "`contraction × 12m` cell is non-negative. Second, the chart does NOT "
        "support a 3-6 month \"peak horizon\" claim: the heatmap peaks at 12 "
        "months, and the smoothed transforms (`zscore_60m`, `yoy`) carry more "
        "linear information than the noisier 1-month momentum that the "
        "tournament eventually picked. The tournament's choice of `mom` reflects "
        "trade-frequency and threshold dynamics, not raw correlation strength — "
        "see Local Projections and the Strategy page for the full picture."
    ),
    key_message=(
        "Permit signals are pro-cyclically correlated with forward SPY returns, "
        "but the linear correlation is modest (≤0.22) and is **strongest at 12 "
        "months on smoothed transforms (z-score, YoY)** — not at 3-6 months on "
        "the noisy 1-month momentum that the tournament selected."
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
        "X-axis: forecast horizon in months (1, 3, 6, 12). Y-axis: cumulative SPY "
        "return response to a 1-standard-deviation permit-growth shock, in "
        "decimal form (0.0025 = 0.25%). The shaded band is the 95% HAC "
        "(Newey-West) confidence interval. **Wherever the shaded band touches "
        "or crosses the zero line, the response at that horizon is not "
        "statistically distinguishable from zero.**"
    ),
    chart_name="local_projections",
    chart_caption=(
        "Jordà (2005) local projections with HAC (Newey-West) standard errors. "
        "The blue line shows cumulative SPY response to a 1-σ shock to Permits "
        "YoY growth; the shaded area is the 95% confidence band. Note that the "
        "lower band sits below zero at every plotted horizon."
    ),
    observation=(
        "Reading the chart directly: the central response is positive and "
        "monotonically rising — h=1: +0.020%, h=3: +0.051%, h=6: +0.119%, "
        "**h=12: +0.255%** (the peak). The rise is not a hump that fades by 6 "
        "months; it is still climbing at the right edge of the chart. The "
        "shaded 95% confidence band, however, dips below zero at every plotted "
        "horizon, including h=12, so the response is not statistically "
        "distinguishable from zero on the strict CI test at the points "
        "evaluated."
    ),
    interpretation=(
        "Two qualifications relative to a standard \"permits lead the cycle\" "
        "story. First, the **point estimate peaks at 12 months, not 3-6** — "
        "consistent with the correlation heatmap, not with the earlier prose "
        "claim of a 3-6 month peak. Second, the **economic magnitude is small** "
        "(a 1-σ permit shock moves cumulative SPY by ~0.25 percentage points "
        "over a year), which is enough to inform a directional bias but is not "
        "by itself a license for size. The 6-month lead in the strategy is a "
        "tournament outcome on out-of-sample Sharpe, not something the LP chart "
        "endorses on its own."
    ),
    key_message=(
        "The LP says permits and SPY co-move pro-cyclically, with the "
        "**point-estimate peak at 12 months and economic magnitude near 0.25%** "
        "per 1-σ permit shock. Confidence bands cross zero at every plotted "
        "horizon, so the LP supports the *direction* of the trade more than its "
        "*size* or its precise timing horizon."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We tested the permits-equity relationship with complementary econometric "
        "methods across 35 years of monthly data. **Two method blocks are "
        "rendered on this page** — Correlation (Level 1, breadth across signal "
        "variants and horizons) and Local Projections (Level 2, the dynamic "
        "impulse-response path).\n\n"
        "**Five additional core-model tests were also run but are not displayed "
        "as charts on this page.** Their CSV outputs sit on disk for "
        "auditability and inform the prose summary below; they are not "
        "rendered inline because each is a small numeric table that adds little "
        "without the chart layer that Correlation and LP already give you. The "
        "headline read on each:\n\n"
        "- **Granger causality** (12 lag-direction rows). Permits→SPY is *not* "
        "Granger-causal at any of lags 1–6 (lowest p-value 0.36). The reverse "
        "direction, SPY→Permits, is highly significant at every lag (p<0.002 "
        "throughout). Honest read: at the monthly frequency on the full "
        "sample, equities lead permits more cleanly than permits lead equities.\n"
        "- **Predictive regressions** (3 signals × 4 horizons). The strongest "
        "single cell is `permit_zscore_60m → spy_fwd_12m` (t=3.32, p=0.0009, "
        "R²≈0.05), reinforcing the Correlation heatmap's reading that the "
        "12-month horizon on smoothed transforms carries more linear "
        "information than the noisier short-horizon signals.\n"
        "- **Quantile regression** (7 quantiles of forward SPY return). The "
        "permit-MoM coefficient is positive in the lower tail (q=0.05, q=0.10, "
        "q=0.25) and *negative and statistically significant in the upper "
        "tail* (q=0.90 p=0.014, q=0.95 p=0.029). Permits help more when SPY "
        "is going badly than when it is going extremely well.\n"
        "- **Local Projections (full table)** — 4 forecast horizons. Same data "
        "the chart renders; CSV adds explicit p-values: h=1 p=0.35, h=3 "
        "p=0.37, h=6 p=0.23, **h=12 p=0.077**. Marginally significant at 12 "
        "months only.\n"
        "- **Diagnostics.** Jarque-Bera p<0.001 (residuals are non-normal — "
        "expected for monthly equity returns) and Durbin-Watson 0.64 "
        "(positive serial correlation in residuals → HAC standard errors are "
        "needed, which the LP chart already uses).\n\n"
        "**Audit trail.** The five CSVs from "
        "`results/permit_spy/core_models_20260314/` are available as direct "
        "downloads via the *Download archived CSVs* expander immediately below."
    ),
    "downloads": [
        {"label": "Granger causality (12 lag-direction rows)",
         "path": "results/permit_spy/core_models_20260314/granger_causality.csv"},
        {"label": "Predictive regressions (3 signals × 4 horizons)",
         "path": "results/permit_spy/core_models_20260314/predictive_regressions.csv"},
        {"label": "Quantile regression (7 quantiles of forward SPY)",
         "path": "results/permit_spy/core_models_20260314/quantile_regression.csv"},
        {"label": "Local projections — full table (4 horizons)",
         "path": "results/permit_spy/core_models_20260314/local_projections.csv"},
        {"label": "Diagnostics summary (Jarque-Bera, Durbin-Watson)",
         "path": "results/permit_spy/core_models_20260314/diagnostics_summary.csv"},
    ],
    "plain_english": (
        "Correlations ask 'do they move together?'. Local projections ask 'if "
        "permits jump today, what happens to SPY over the next 12 months?'. Both "
        "tests agree the relationship is real and pro-cyclical; the chart-vs-"
        "narrative summary at the bottom of this page gives the calibrated read "
        "on at which horizon it is strongest.\n\n"
        "**Raw vs derived — what is being compared?** The hero chart on the "
        "Story page plots a *raw* macro series (Building Permits, smoothed to "
        "YoY) against the *raw* SPY price for visual context. The heatmap and "
        "models on this page do something different: they compare "
        "**transformations** of the permit series — momentum, z-score, YoY "
        "growth, deviation-from-trend — against **forward SPY returns**, not "
        "the price level. The Signal Universe shown in the heatmap is the short "
        "list of transforms the tournament considered worth testing; less "
        "informative variants are filtered out before the heatmap is drawn."
    ),
    "level1": [CORRELATION_BLOCK],
    "level1_labels": ["Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK],
    "level2_labels": ["Local Projections"],
    "tournament_intro": (
        "With the in-sample econometric case established, we then swept a "
        "5-dimensional tournament over signal transforms, threshold methods, "
        "strategy families, lead times, and lookback windows. The leaderboard "
        "lives on the Strategy page; the headline is a winning OOS Sharpe of "
        "1.45 versus 0.90 for SPY buy-and-hold over the 2018–2025 OOS window."
    ),
    "transition": (
        "**Honest read on the cross-period charts above.** The relationship "
        "between Building Permits and SPY is real and pro-cyclical, but it is "
        "not steady across history:\n\n"
        "- **Sub-period Sharpe.** The strategy is *negative* in three of the "
        "four labelled crisis sub-periods (Dot-Com −0.38, GFC −0.36, China/EM "
        "−1.20) and roughly flat through COVID (−0.07). The full-OOS bar "
        "(+1.41) carries the headline; the crisis bars do not.\n"
        "- **Rolling 24M correlation.** The line ranges from about −0.36 to "
        "+0.42 with a mean near zero. Only ~54% of 24-month windows are "
        "positive. The relationship is regime-dependent, not stationary.\n"
        "- **Rolling Granger F.** Average F is 3.16 — just below the 3.84 "
        "critical value at 5% — and the rolling p-value averages 0.20. "
        "Granger-causality is *not* persistently significant across windows; "
        "it appears in pockets.\n"
        "- **Rolling 24M Sharpe.** Range −2.0 to +2.0, mean ~0.0. The "
        "strategy's edge is concentrated in specific regimes, not earned "
        "evenly through time.\n"
        "- **Structural break.** The QLR-proxy p-value is 0.27 — *not* "
        "statistically significant at the 5% level. The chart now reflects "
        "this with the break-date flag suppressed and the test annotation "
        "marked as not-significant. The recession-shaded rectangles remain "
        "for context, but the relationship is treated as stationary across "
        "the sample for tournament purposes.\n\n"
        "**Putting it together.** The Evidence page supports a genuine "
        "pro-cyclical relationship between Building Permits and equity "
        "returns, with the strongest *linear* co-movement at a 12-month "
        "horizon on smoothed transforms. The 6-month lead and 1-month-"
        "momentum signal that won the tournament reflect out-of-sample "
        "Sharpe optimisation — not a direct claim that 6 months is the only "
        "horizon where the relationship exists, and not a guarantee that the "
        "edge will persist evenly across regimes. With those qualifications "
        "in place, the practical question is whether an investor can turn "
        "this into an execution-ready strategy."
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
        "position once a month, using publicly available FRED data.\n\n"
        "**Vocabulary for this page:**\n"
        "- **Tournament** = the same thing as **Strategy** — every \"combo\" "
        "scored below *is* a strategy candidate. We exhaustively enumerated "
        "combinations of (signal transform × threshold rule × strategy family × "
        "lead time × lookback) and ranked them on out-of-sample Sharpe. The "
        "*winner* is the row at the top of that ranking; we call it \"the "
        "strategy\" elsewhere on the page.\n"
        "- **Combo** = one specific (signal, threshold, strategy, lead, lookback) "
        "tuple. For permit_spy the full sweep is **856 combos**, of which "
        "**675 are *valid*** and **181 are excluded**. A combo is excluded "
        "when the threshold rule cannot be evaluated on the in-sample window "
        "(too few crossings, divide-by-zero on a rolling z-score, or the "
        "signal series doesn't exist for the requested lookback).\n"
        "- **Tournament Scatter axes.** The X-axis is **OOS annualised return** "
        "(percent, range ~0.3–17%). The Y-axis is **OOS Sharpe ratio** (range "
        "~0.0–1.5). Each dot is one valid combo plotted at its (return, Sharpe) "
        "outcome on the OOS window. Top-right = high return *and* high "
        "risk-adjusted return. The diamond marker is buy-and-hold SPY (the "
        "benchmark anchor). The star markers are the top 5 combos by Sharpe.\n"
        "- **Why the leaderboard shows 10 rows but the scatter shows hundreds.** "
        "The scatter plots every valid combo as a dot so you can see the full "
        "performance cloud. The leaderboard truncates to the top 10 by OOS "
        "Sharpe — the only rows you would ever consider trading.\n"
        "- **Why the leaderboard's benchmark Max Drawdown reads −23.93%, not "
        "−50%.** The tournament is scored on the **out-of-sample window only "
        "(2018-01 to 2025-12, 96 monthly observations)**. SPY's worst "
        "drawdown in that window is the COVID crash and the 2022 bear market "
        "(both around −24%); the −50% Great Financial Crisis drawdown in "
        "2008–2009 is *in-sample* and is therefore not visible in any column "
        "of the leaderboard. The same is true for every strategy's MaxDD "
        "column — those are OOS-window worst drawdowns. The full-sample "
        "drawdown (including 2008) is shown on the Drawdown chart on the "
        "**Performance** tab below, where the strategy's worst drawdown is "
        "−40.2% (2003-02, dot-com era) versus B&H's worst of −50.8% "
        "(2009-02, GFC).\n"
        "- **About repeated −19.4% values in the leaderboard.** Multiple "
        "tournament rows share the same Max Drawdown because they share the "
        "same *position regime* over the OOS window — small variations in "
        "the threshold parameter (e.g. T1_p25 vs T1_p20) often produce the "
        "exact same trade timing on a sparse monthly grid, and therefore the "
        "exact same drawdown. It is not a bug in the table; it reflects the "
        "discrete-trade nature of the strategy on monthly data.\n\n"
        "**Data-vintage note.** The trade log on this page combines a "
        "vintage-pinned signal column (FRED PERMIT as of April 2026, the same "
        "vintage the tournament was scored on) with current-vintage SPY prices. "
        "Why the split — and why it does not change any of the leaderboard "
        "numbers — is documented in "
        "`docs/data_vintage_note_permit_spy.md`."
    )

    SIGNAL_RULE_MD = (
        "**Tournament winner — code key.** The header above reads "
        "`S3_mom / P3_long_short / L6`. Decoded:\n\n"
        "- **`S3_mom` — Signal.** The S-prefix denotes a *signal transform*. "
        "`S3_mom` = the 1-month-momentum (MoM) transform of the raw PERMIT "
        "series, i.e. `permit_t / permit_{t-1} - 1`. The \"3\" is just a "
        "tournament index, not a 3-month window — momentum here is computed "
        "over **one month**.\n"
        "- **`T1_p25` — Threshold.** T-prefix denotes a *threshold rule*. "
        "`T1_p25` = the 25th percentile of MoM momentum, **fixed once on the "
        "in-sample period (1990–2017) and held constant out-of-sample**. The "
        "numeric value is **−2.73%** (computed on the April-2026 vintage of "
        "FRED PERMIT — the same vintage the tournament was scored on).\n"
        "- **`P3_long_short` — Strategy family.** P-prefix denotes a "
        "*positioning rule*. `P3` = Long/Short (the alternatives are P1 "
        "Long/Cash and P2 Signal-Strength).\n"
        "- **`L6` — Lead.** The position applied today uses the signal value "
        "from **6 months ago**. This is independent of the 1-month signal "
        "computation: every month we re-compute MoM, but we don't act on it "
        "for 6 months.\n\n"
        "**Two windows, not one.** Readers sometimes confuse the *signal "
        "window* (1 month — how the indicator is computed) with the *lead* "
        "(6 months — how long we wait before acting). They are separate "
        "dimensions of the strategy and can take independent values; the "
        "tournament happened to land on 1 month for the first and 6 months "
        "for the second.\n\n"
        "**Behavioural rule.** When the month-over-month change in Building "
        "Permits 6 months ago was above the **−2.73%** threshold (i.e. not "
        "deeply negative), hold SPY long. When that lagged MoM was below "
        "−2.73% (sharp decline), go short. Rebalance monthly."
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
        "3. Compare that number to **−2.73%** (the fixed in-sample 25th "
        "percentile of MoM permit growth over 1990–2017; the exact value is "
        "shown in every row of the trade log under `threshold_value`).\n"
        "4. If the number is above −2.73% → hold SPY long. Below → short.\n"
        "5. Revisit next month."
    )

    # No equity_curves / drawdown / walk_forward charts exist for permit_spy
    # on disk (as of Wave 10I.A). Template falls back to "chart pending" for
    # those surfaces — pre-existing data gap, not a regression.
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

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
        "**Crisis anchor — 2008–2009 Great Financial Crisis.** From "
        "`results/permit_spy/winner_trade_log.csv`:\n\n"
        "- **2008-06-30 → 2008-10-31 (Short, 123 days, +26.65%).** Building "
        "permits had been collapsing since mid-2006. By June 2008 the 6-month-"
        "lagged MoM signal (reflecting December 2007 permit data) had been "
        "deeply negative for more than a year (signal value ≈ −6.13%, well "
        "below the −2.73% threshold), pushing the rule into a short SPY "
        "position. The short was held through the Lehman bankruptcy and the "
        "October 2008 market trough.\n"
        "- **2008-10-31 → 2009-01-31 (Long, 92 days, −13.76%).** The rule "
        "flipped long too early. Permits MoM 6 months prior (April 2008) "
        "briefly clawed above the threshold (signal value +4.24%), but "
        "equities continued falling into the March 2009 low.\n"
        "- **2009-01-31 → 2009-07-31 (Short, 181 days, −20.28%).** The "
        "*catastrophic whipsaw*. The signal pushed back into deeply-negative "
        "territory (lagged July 2008 MoM ≈ −21.95%, the most negative reading "
        "in modern data) and the rule went short — but March 2009 was the "
        "actual market low, and SPY rallied 40%+ over the next six months. "
        "The strategy held the short through the entire trough-to-rebound move "
        "and lost more than 20% on this single position. This trade is not "
        "small print: it is the largest single-trade loss in the entire "
        "150-trade backtest and a worked example of how a 6-month-lead "
        "pro-cyclical rule fails when the recovery is faster than the "
        "indicator's lead. Read the Caveats section before sizing.\n"
        "- **Net take-away.** The 2008 short captured the core crash; the "
        "2009 long entry whipsawed for −13.76%; the 2009 short missed the "
        "March turn for −20.28%. Across the three trades the strategy was "
        "net negative through 2008–2009 — the OOS Sharpe headline (1.45) is "
        "earned in calmer years, not in the crisis itself. The Caveats panel "
        "and the Cross-Period Consistency section on the Evidence page already "
        "flag this regime sensitivity."
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
    "`spy.shift(-h) / spy - 1` for h = 1, 3, 6, 12 months.\n\n"
    "#### Why MoM? — connecting the Stationarity Tests below to the signal choice\n\n"
    "**What stationarity tests do.** A series is *stationary* if its mean and "
    "variance are stable through time. Most econometric tools (correlations, "
    "regressions, Granger causality, local projections) assume stationarity; "
    "running them on a non-stationary series produces unreliable t-statistics "
    "and spurious correlations. The stationarity-test table below reports two "
    "complementary checks for each candidate signal: **ADF** (Augmented "
    "Dickey-Fuller — null hypothesis: the series has a unit root, i.e. is "
    "non-stationary; *low p-value rejects → stationary*) and **KPSS** "
    "(Kwiatkowski-Phillips-Schmidt-Shin — null hypothesis: the series is "
    "stationary; *high p-value fails to reject → stationary*). When ADF and "
    "KPSS agree we have strong evidence one way or the other; when they "
    "disagree the verdict is borderline.\n\n"
    "**What the table tells us about each signal.** The raw `permit` level is "
    "non-stationary on ADF (p≈0.56) but flagged stationary on KPSS (p≈0.14) — "
    "an ambiguous reading that disqualifies it from clean linear modelling. "
    "`permit_yoy` is borderline on ADF (p≈0.06) and stationary on KPSS — "
    "usable but not ideal. **`permit_mom` (MoM momentum) is unambiguously "
    "stationary: ADF p<0.001, KPSS p≈0.38**. This is the only transform where "
    "both tests agree decisively, which is part of why the tournament's "
    "winner is the MoM signal — its statistical properties make all the "
    "downstream tests (Pearson, Granger, LP) interpretable. The table is the "
    "evidence; the choice of MoM is the consequence."
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
