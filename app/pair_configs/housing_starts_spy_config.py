"""Housing Starts (SAAR) x SPY pair configuration (Rule APP-PT1).

Pair `housing_starts_spy`, Mode 2. Prose is sourced from Research Ray's
`docs/portal_narrative_housing_starts_spy_20260814.md`; this file wires that
prose to the shared Streamlit templates and Vera's bare-name chart artifacts.

Evidence status is `found_in_search`, so headline performance is labelled
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template. Headline
values come from `results/housing_starts_spy/winner_summary.json`.

Framing (COUNTERCYCLICAL, low-confidence): Housing Starts (FRED HOUST) is a
canonical rate-sensitive early-cycle indicator, so the natural prior is
procyclical-leading. The data disagrees. The regime quartiles are NON-monotonic
(hump-shaped: Q2 best, strong-growth Q4 worst), and the searched winner is a
COUNTER orientation -- long SPY when the 3-month change in starts is BELOW its
median (2-month lead). Forward Granger is EMPTY (starts do not lead SPY at any
lag 1-12) while the reverse channel (SPY -> starts) is significant at EVERY lag
1-12. The winner is the best of 4,850 valid searched combos with a
non-significant bootstrap p (0.127), a structural break flagged at 2009, and a
sign-unstable rolling correlation. HOUST is seasonally adjusted at source
(SAAR), so MoM is a valid signal and NO deseasonalisation is applied -- the key
contrast with nhs_spy. The raw SAAR level is non-stationary and excluded.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Housing Starts as a Countercyclical Timing Overlay"
    PAGE_SUBTITLE = (
        "Housing Starts, 3-month change (FRED HOUST, seasonally adjusted annual "
        "rate) x S&P 500 (SPY), monthly decision rules with release-lag "
        "discipline."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.37 OOS, drawdown -13%: a countercyclical housing timing "
        "overlay -- the procyclical prior did NOT hold, forward causality is "
        "absent, and confidence is low"
    )

    PLAIN_ENGLISH = (
        "Housing starts are a classic rate-sensitive early-cycle indicator, so "
        "the natural guess is procyclical -- more building should coincide with "
        "a healthier economy and better equities. The data says the opposite. "
        "The best rule the search found is COUNTERCYCLICAL: it holds SPY when "
        "the 3-month change in housing starts is BELOW its historical median "
        "(i.e. when construction is softening) and steps to cash otherwise. That "
        "behaves like a 'bad-news-is-good-news' rate-expectations effect -- "
        "weaker building foreshadows easier policy. It improved risk-adjusted "
        "return and roughly halved the drawdown in the search window, but the "
        "formal forward-causality tests are empty, so treat the edge as a "
        "search-found timing overlay, not a forecast."
    )

    WHERE_THIS_FITS = (
        "This is a housing activity signal tested against broad U.S. equities. "
        "The honest reading: the tradable edge is countercyclical and modest, "
        "and it sits on top of a relationship where the market actually leads "
        "housing, not the other way round. It is suggestive that softening "
        "construction lines up with better forward equities via the rate "
        "channel -- not proof that housing starts forecast the S&P 500."
    )

    ONE_SENTENCE_THESIS = (
        "The winning Housing-Starts rule is a countercyclical Long/Cash overlay "
        "that improves Sharpe and drawdown out-of-sample, but the procyclical "
        "prior failed, forward causality is absent (the market leads housing, "
        "not vice versa), and the winner is a large-search tail with a "
        "non-significant bootstrap p -- a low-confidence searched candidate "
        "awaiting a final exam."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final holdout "
        "result. The winner was selected from 4,850 valid strategy "
        "combinations, with bootstrap p=0.127 (above the 5% bar) and low "
        "confidence -- and Housing Starts do NOT Granger-cause SPY at any lag."
    )

    HERO_TITLE = "Housing-Starts Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: Housing Starts year-over-year growth (FRED HOUST, "
        "seasonally adjusted at an annual rate) is shown against SPY on a shared "
        "time axis, with the 0% line marked and the 2008-09 collapse and "
        "2022-24 rate-shock contraction annotated. The winning rule trades the "
        "3-month change in starts, not the raw level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Housing-Starts Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by Housing Starts "
        "YoY-growth quartile. The gradient is NON-monotonic (hump-shaped): "
        "Sharpe peaks in Q2 (1.06) and is LOWEST at the strong-growth extreme "
        "Q4 (0.64), while the weak-growth quartile Q1 carries by far the deepest "
        "drawdown (-51%). This is not a clean procyclical gradient -- it is "
        "consistent with the countercyclical winner."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning rule earns a Sharpe ratio -- return per unit of volatility -- of 1.37 versus 0.91 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves to -13.0% from -23.9%, while annualized return is essentially matched (14.2% versus 15.0%).

Housing starts are a canonical rate-sensitive early-cycle indicator, so the natural prior is **procyclical-leading**. This pair does **not** confirm that prior. The regime quartiles are hump-shaped rather than rising, and the searched winner is a **countercyclical** rule.

### A Seasonally-Adjusted Series -- No Deseasonalisation Needed

Unlike the not-seasonally-adjusted new-home-sales pair, the Census/HUD housing-starts series (FRED `HOUST`) is published at a **seasonally adjusted annual rate**. That means month-over-month change is already a valid momentum input and no year-over-year or STL deseasonalisation is required to make a signal usable. The one exclusion is the raw level itself: it is trend-dominated and non-stationary (an augmented Dickey-Fuller test does not reject a unit root), so we never trade or chart it as a signal. Every traded signal is a stationary growth transform.

### The Direction Surprise

The winning rule trades the **3-month change** in housing starts with a **counter** orientation: hold SPY when that change is **below** its median (construction softening), step to cash when it is above. Economically this reads like a peak-cycle mean-reversion / "bad-news-is-good-news" rate channel -- softening starts foreshadow easier policy and better forward equities -- and it mirrors the INDPRO precedent, where the level story inverted at extremes.

<!-- expander: If housing starts lead the economy, why is the winner countercyclical and low-confidence? -->
Two different claims are in play. "Housing starts lead the business cycle" can be true while "housing starts forecast the S&P 500" is not -- and here the formal forward tests are empty: starts do not Granger-cause SPY at any lag 1-12, while SPY leads starts at every lag. The countercyclical rule is what the search maximised out of 4,850 valid combinations, with a re-shuffle p-value (0.127) above the 5% bar. So we report a genuine, modest countercyclical timing edge AND low confidence -- on purpose, and separately.
<!-- /expander -->
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The Dot-Com chart is included as a confirmer for continuity "
                "across the portal's standard episode set. Read it as "
                "contextual background, not the strongest validation case."
            ),
            "caption": "Contextual background; a continuity confirmer, not validation.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The GFC is the textbook case for housing starts as an early-"
                "cycle signal: starts collapsed roughly 75% from their 2006 "
                "peak and turned down well ahead of the 2008-09 equity bear "
                "market. It is the episode that makes a procyclical prior "
                "tempting -- even though the tradable edge turns out "
                "countercyclical."
            ),
            "caption": "GFC: starts turned down years ahead of the equity bear.",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During the coronavirus disease 2019 (COVID-19) shock, housing "
                "starts dipped then surged on record-low mortgage rates while "
                "SPY crashed and rapidly recovered. COVID is the only stress "
                "episode that falls inside the out-of-sample window and is "
                "evaluable."
            ),
            "caption": "COVID: starts dipped then surged on low rates as SPY recovered.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022-24 mortgage-rate shock, housing starts "
                "contracted materially as 30-year rates jumped -- the strong, "
                "recent regime that dominates the out-of-sample window and "
                "drives much of the strategy's drawdown avoidance."
            ),
            "caption": "2022-24: rate shock cut starts -- the dominant OOS regime.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history-zoom charts make the cyclical character tangible. During the **2008-09 Global Financial Crisis**, housing starts collapsed roughly 75% from their 2006 peak and turned down well ahead of the equity bear market -- the textbook case for housing as an early-cycle signal. During **COVID-19**, starts dipped then surged on record-low mortgage rates as SPY recovered. During the **2022-24 rate shock**, starts contracted sharply as mortgage rates jumped -- the strong, recent regime that dominates the out-of-sample window. The Dot-Com window is a continuity confirmer for the portal's standard episode set.
"""

    TRANSITION_TEXT = (
        "The historical story looks like an early-cycle-housing one, which is "
        "exactly why the full evidence suite matters. The Evidence page shows "
        "the hump-shaped (non-monotonic) quartiles alongside the empty "
        "forward-causality tests that keep confidence low."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
QUANTILE_CHART_NAME = "quantile_coef"
TRANSFER_ENTROPY_CHART_NAME = "transfer_entropy"
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Growth Quartile Gradient",
    method_theory=(
        "Quartile analysis sorts months into four buckets by Housing Starts "
        "YoY-growth and compares subsequent SPY performance. It is descriptive "
        "(concurrent), not the trading rule."
    ),
    question="Do stronger or weaker starts growth line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 (weakest starts growth) to Q4 (strongest). A "
        "clean rising gradient would support 'more building is better for "
        "stocks'; here the gradient is hump-shaped, not rising."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Sharpe is NON-monotonic -- it peaks in Q2 (1.06) and "
        "is lowest at the strong-growth extreme Q4 (0.64); Q1 (weakest growth) "
        "carries a -51% drawdown versus Q4's -18%."
    ),
    observation=(
        "The gradient is hump-shaped, not monotonic: the strongest-growth "
        "quartile does NOT have the best forward Sharpe, and the weakest "
        "quartile carries the deepest drawdown."
    ),
    interpretation=(
        "The procyclical prior does NOT hold cleanly. The weak-at-both-extremes "
        "shape is consistent with the countercyclical winner and a peak-cycle "
        "mean-reversion reading, echoing the INDPRO and money-supply pairs "
        "where the level story inverted."
    ),
    key_message=(
        "Non-monotonic and NOT cleanly procyclical -- consistent with the "
        "countercyclical winning rule."
    ),
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag (Both Directions)",
    method_theory=(
        "Toda-Yamamoto Granger causality tests whether past values of one "
        "series improve forecasts of the other beyond its own history, in a "
        "form robust to integration order."
    ),
    question="Does Housing Starts growth lead SPY -- or does SPY lead housing?",
    how_to_read=(
        "Bars are F-statistics by monthly lag; bars above the dashed line are "
        "significant at the 5% level. The vermillion bars are starts leading "
        "SPY; the pale-blue bars are SPY leading starts."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: the forward direction (starts to SPY) clears the line "
        "at NO lag; the reverse direction (SPY to starts) is significant at "
        "EVERY lag 1-12."
    ),
    observation=(
        "Forward Granger support is absent at all lags 1-12; the reverse "
        "SPY-to-starts direction is significant at every lag 1-12."
    ),
    deep_dive_title="What does 'the market leads housing' mean for this rule?",
    deep_dive_content=(
        "A dependable leading indicator clears the significance line in the "
        "forward direction across a band of horizons. Here the opposite holds: "
        "equities lead housing starts at every lag, consistent with financial "
        "conditions and wealth driving construction. The tradable rule is "
        "therefore best read as a coincident/contrarian timing overlay, not a "
        "forward forecast -- which is why confidence is low."
    ),
    interpretation=(
        "Forward causality is empty and the reverse channel is pervasive. This "
        "is the central reason confidence is low despite the strong headline "
        "Sharpe."
    ),
    key_message="Starts do NOT lead SPY; SPY leads starts at every lag -- confidence stays low.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation removes each series' own persistence "
        "before checking whether one echoes the other at monthly offsets."
    ),
    question="Is there a clean forward lead-lag echo after removing autocorrelation?",
    how_to_read=(
        "Bars outside the confidence band indicate statistically meaningful "
        "offsets. Negative lags would mark starts growth leading SPY."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF does not establish a clean forward lead from "
        "starts growth to SPY, consistent with the empty Granger result."
    ),
    observation=(
        "The cross-correlation does not produce a clean forward-lead signal."
    ),
    interpretation=(
        "The CCF reinforces the Granger conclusion: the forward lead from "
        "starts growth to SPY is weak-to-absent."
    ),
    key_message="The cross-correlation check does not support a forward lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after a move in starts growth, with a reverse-direction "
        "check for causality."
    ),
    question="Does a starts-growth move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward starts-to-SPY responses are weak and "
        "imprecisely estimated; the confidence bands are wide relative to the "
        "point estimates."
    ),
    observation=(
        "Forward responses are weak across 1, 3, 6, and 12 months."
    ),
    interpretation=(
        "Local projections tell the same weak-forward story as Granger and the "
        "CCF: limited forward predictive content."
    ),
    key_message="Local projections corroborate the weak forward relationship.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression asks whether the relationship differs in weak, "
        "normal, and strong SPY-return environments."
    ),
    question="Is the signal coherent across the return distribution?",
    how_to_read=(
        "Read coefficient estimates across return quantiles. A clean forward "
        "predictor would show a coherent, stable pattern."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: the coefficient varies across return quantiles rather "
        "than holding a single stable sign -- not the profile of a clean, "
        "uniform forward predictor."
    ),
    observation=(
        "The quantile estimates vary across the return distribution."
    ),
    interpretation=(
        "That pattern is consistent with a regime / mean-reversion effect "
        "rather than a simple linear forward channel from starts to SPY."
    ),
    key_message="Quantile evidence points to a regime effect, not a linear predictor.",
)

TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy is a nonlinear information-flow check that can catch "
        "relationships missed by linear tests."
    ),
    question="Is there nonlinear directed information flow, and in which direction?",
    how_to_read=(
        "Small permutation p-values indicate genuine directed information "
        "flow. Compare the forward and reverse channels."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: neither the forward (starts to SPY) nor the reverse "
        "channel shows strong nonlinear information flow."
    ),
    observation=(
        "Both directions are weak under the nonlinear information-flow test."
    ),
    interpretation=(
        "Transfer entropy is consistent with the weak linear lead-lag: no "
        "strong directed information flow either way."
    ),
    key_message="Even the nonlinear check finds only weak information flow.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map (Backdrop)",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the starts-growth series into latent "
        "regimes -- a calm state and a high-variance, turning-point state."
    ),
    question="When is construction activity in a high-variance regime?",
    how_to_read=(
        "Higher probability marks months where starts growth behaves unusually "
        "(high-variance). Here the HMM is contextual backdrop, NOT the winning "
        "signal."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the high-variance regime probability spikes around "
        "housing turning points (GFC, COVID, the 2022 rate shock). Unlike some "
        "pairs, this regime probability is NOT the winning trading signal -- "
        "the winner is the simple 3-month change in starts."
    ),
    observation=(
        "The HMM cleanly separates calm construction regimes from high-variance "
        "turning points."
    ),
    interpretation=(
        "The regime map is useful context for the episode story, but the "
        "tournament winner is a plain 3-month-change rule, not the HMM "
        "probability. It does not change the weak-forward, low-confidence "
        "verdict."
    ),
    key_message="The HMM is backdrop here -- the winner is the 3-month-change rule.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence: a countercyclical edge on a market-leads-housing relationship",
    "overview": (
        "The regime quartiles are hump-shaped, not rising -- the procyclical "
        "prior does not hold. The formal forward-causality tests are empty: "
        "Housing Starts do NOT Granger-cause SPY at any lag 1-12, while SPY "
        "leads starts at EVERY lag 1-12. Supporting checks (local projections, "
        "the pre-whitened CCF, transfer entropy, quantile regression) all "
        "corroborate the weak-forward, mean-reversion-flavoured reading."
    ),
    "plain_english": (
        "This section asks whether Housing Starts really helps predict future "
        "SPY performance. The direction is countercyclical and the formal "
        "lead-lag tests show the market leading housing, not the reverse, so "
        "the strong headline Sharpe is treated as a low-confidence searched "
        "result -- a contrarian timing overlay, not a forecast."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/housing_starts_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/housing_starts_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/housing_starts_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/housing_starts_spy/rolling_correlation_housing_starts_spy.csv"},
        {"label": "Stationarity tests", "path": "results/housing_starts_spy/stationarity_tests_20260814.csv"},
    ],
    "level1": [QUARTILE_BLOCK, GRANGER_BLOCK, CCF_BLOCK, HMM_BLOCK],
    "level1_labels": ["Growth Quartiles", "Granger Causality", "Pre-Whitened CCF", "HMM Regimes"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy"],
    "tournament_intro": (
        "The tournament tested 6,860 benchmark-excluded strategy combinations, "
        "of which 4,850 passed validity filters. The winning rule is the best "
        "of that valid searched set, so its Sharpe advantage must be read with "
        "the search-position warning attached."
    ),
    "transition": (
        "**Transition:** the direction is countercyclical and forward causality "
        "is absent. The strategy page shows what the rule actually is: a "
        "search-found Long/Cash overlay -- long SPY when 3-month starts growth "
        "is below its median -- whose drawdown win is concentrated in a short, "
        "episode-heavy OOS window."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Countercyclical Housing Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched timing overlay: better Sharpe and drawdown than "
        "buy-and-hold in the OOS window -- but countercyclical (the prior "
        "failed), forward causality absent, found_in_search, and low "
        "statistical confidence."
    )

    PLAIN_ENGLISH = (
        "The rule is simple: when the 3-month change in Housing Starts is BELOW "
        "its historical median (construction softening), hold SPY; otherwise "
        "hold cash. The signal is used with a 2-month lead to respect the "
        "release calendar. It improved Sharpe and roughly halved the drawdown "
        "in the search-phase OOS window, but the forward-causality tests are "
        "empty, so this is a contrarian timing overlay, not a forecast."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 3-month change in Housing Starts (FRED HOUST) is **below** its in-sample median threshold; otherwise hold cash. The signal is lagged **2 months** (L2) to respect the Census/HUD release calendar. This is a countercyclical (contrarian) orientation: softening construction = risk-on.

If-then form:
- **IF** the lagged 3-month change in starts is **below** its median threshold (approximately +0.57%) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2018-03-31 to 2026-06-30, no holdout final exam yet): Sharpe 1.37 vs 0.91 buy-and-hold; annualized return 14.2% vs 15.0%; maximum drawdown -13.0% vs -23.9%; 48 OOS position changes; annual turnover 5.8; OOS win rate 39%.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Census/HUD monthly housing-starts release (FRED series HOUST) at its current vintage. Because the series is already seasonally adjusted at an annual rate, no deseasonalisation is needed. Second, it computes the 3-month percent change in the level -- a short-horizon momentum measure of construction activity. Third, it compares that change against a fixed in-sample median threshold and, because the winning orientation is countercyclical, takes a long-SPY position when the change is BELOW the threshold (construction softening), stepping to cash otherwise. The signal is lagged two months so the rule only ever uses data that had been publicly released.

This is intentionally simple. It does not forecast mortgage rates, model the Fed, or claim that housing drives stocks. It asks whether construction momentum is soft enough to imply a supportive rate/liquidity backdrop and times SPY on that -- and, as the Evidence page is careful to say, starts do not Granger-cause SPY at any lag.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Housing Starts (`HOUST`) from the live FRED API at the current vintage.
2. Compute the 3-month percent change in the level (no deseasonalisation needed -- the series is SA).
3. Compare that change with its fixed in-sample median threshold (approximately +0.57%).
4. Because the orientation is countercyclical, hold SPY when the change is BELOW the threshold; otherwise hold cash.
5. Apply a 2-month lag so only released data is used.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam, and Housing Starts do NOT Granger-cause SPY at any lag (the market leads housing).
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Only COVID 2020 "
        "falls inside the 2018-onward OOS window and is evaluable; the "
        "Dot-Com, GFC, and China 2015 episodes predate the OOS split and are "
        "marked insufficient data -- which is why durability is only "
        "conditionally durable."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 4,850 valid "
        "searched combinations, with buy-and-hold above the median. The "
        "winner's 1.37 Sharpe is near the top of the search, not a typical "
        "result -- and its bootstrap p-value (0.127) is above the 5% bar."
    )

    CAVEATS_MD = """
**Why confidence is low (and the prior failed):**

1. Forward causality is absent: Toda-Yamamoto Granger finds Housing Starts do NOT lead SPY at any lag 1-12, while SPY leads starts at EVERY lag 1-12. The market leads housing, not the reverse.
2. The direction is countercyclical, not the procyclical prior -- and the regime quartiles are hump-shaped (Q2 best, strong-growth Q4 worst), not a clean rising gradient.
3. The winner came from 4,850 valid searched combinations; its bootstrap p-value is 0.127 -- **above the 5% bar**, so it does not clear conventional significance.
4. The rule is marked `found_in_search` -- it has NOT been confirmed on an untouched final-exam window, and a structural break is flagged at 2009-03 with a sign-unstable rolling correlation.
5. Durability is only `conditionally_durable`: the OOS window (2018-2026) is short and dominated by the 2022-24 rate shock; COVID is the only evaluable stress episode.
6. The winning signal is the 3-month change in starts; the raw SAAR level is non-stationary and excluded from the signal set.

**What this means:** use the page as evidence for a modest, contrarian housing-timing overlay on a market-leads-housing relationship -- not as proof that Housing Starts forecast the S&P 500.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged 3-month change in Housing Starts drops back below "
        "its median threshold (construction softening), moving from 0% to 100% "
        "SPY exposure, and a SELL back to cash when the change rises above the "
        "threshold. Over the OOS window the rule made 48 such position changes."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-05-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash (counter): Housing Starts 3M change < p50 threshold; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Census / HUD via live FRED API (current vintage) | `HOUST` New Privately-Owned Housing Units Started (thousands, seasonally adjusted annual rate) | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "Housing Starts (`HOUST`) is seasonally adjusted at an annual rate, so -- "
    "unlike the not-seasonally-adjusted new-home-sales series -- month-over-"
    "month change is a valid signal and NO deseasonalisation is applied. "
    "Signals are stationary growth transforms: year-over-year growth (primary), "
    "month-over-month change, 3-month change, 3-month-average YoY, YoY "
    "acceleration, and a rolling z-score of YoY growth. The raw SAAR level is "
    "non-stationary (augmented Dickey-Fuller does not reject a unit root) and is "
    "excluded from the signal set. The winning signal is the 3-month change in "
    "starts, evaluated against a fixed in-sample median threshold with a "
    "countercyclical orientation and a 2-month lead (L2). The daily panel "
    "carries the latest released monthly value forward from the Census/HUD "
    "release date (approximately the 17th of the following month), so the "
    "strategy does not use future information. Starts are revised; the live FRED "
    "API is treated as ground truth."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger | Do lagged starts values improve SPY forecasts -- or the reverse? | Formal lead-lag test, robust to integration order |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM / Markov regimes | Which months are calm vs high-variance construction regimes? | Regime backdrop for the episode story |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: Housing-Starts transforms x threshold rules x strategy families x orientations x monthly leads (L0-12) x lookbacks. The final tournament file has 6,860 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 4,850 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `chg_3m / T1_fixed_p50 / P1_long_cash (counter) / L2 / LB_NA`.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/housing_starts_spy/evidence_status.json` marks the pair `found_in_search`. Forward Granger causality is absent at all lags while the reverse direction is pervasive, reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau & HUD, New Residential Construction (Housing Starts, HOUST), via FRED.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." (Markov-switching / HMM)
7. Stock, J. H. & Watson, M. W. (2003). "Forecasting Output and Inflation: The Role of Asset Prices." (leading indicators)
8. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Out-of-sample window 2018-03-31 to 2026-06-30, 100 monthly "
        "observations; in-sample ends before the 2018 split. Total tournament "
        "count is 6,860 benchmark-excluded strategy combinations; 4,850 are "
        "valid. Evidence status: found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the Housing Starts analysis. The most "
        "important points: the indicator is seasonally adjusted (so MoM is a "
        "valid signal and no deseasonalisation is applied), the direction is "
        "countercyclical (the procyclical prior failed), forward causality is "
        "absent (the market leads housing), and the winning rule still needs a "
        "frozen-rule holdout test."
    ),
)
