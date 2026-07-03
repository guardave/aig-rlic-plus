"""New Home Sales (NSA) x SPY pair configuration (Rule APP-PT1).

Pair `nhs_spy`, Mode 2. Prose is sourced from Research Ray's
`docs/portal_narrative_nhs_spy_20260703.md`; this file wires that prose to the
shared Streamlit templates and Vera's bare-name chart artifacts.

Evidence status is `found_in_search`, so headline performance is labelled
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/nhs_spy/winner_summary.json`.

Framing (procyclical, low-confidence): New Home Sales is an early-cycle housing
leading indicator. The regime quartiles are cleanly monotonic (Q1 weak -> Q4
strong Sharpe rises), so the procyclical prior holds — unlike the money-supply
and industrial-production pairs where the level story inverted. BUT forward
Granger causality is weak (NHS->SPY significant only at lag 11; reverse
SPY->NHS at lags 1-2), the winner is the max of 5,297 valid combos with a
non-significant bootstrap p (0.071), and IS Sharpe (0.81) is far below OOS
(1.49). The winning signal is a 2-state HMM regime probability on the
deseasonalised YoY growth, NOT the raw NSA level. The indicator is NSA — every
signal is YoY/STL-deseasonalised.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: New Home Sales as an Early-Cycle Housing Timing Overlay"
    PAGE_SUBTITLE = (
        "New Home Sales, year-over-year growth (FRED HSN1FNSA, not seasonally "
        "adjusted) x S&P 500 (SPY), monthly decision rules with release-lag "
        "discipline."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.49 OOS, drawdown -8.3%: a housing-regime timing overlay -- "
        "procyclical as expected, but forward causality is weak and confidence "
        "is low"
    )

    PLAIN_ENGLISH = (
        "New Home Sales is an early-cycle housing indicator: buyers commit "
        "before construction, so sales lead starts, permits, and the jobs and "
        "spending they drive. The natural prior is procyclical -- stronger "
        "home-sales demand should coincide with better equities -- and here the "
        "direction comes out as expected (the regime quartiles rise cleanly "
        "from weak to strong growth). The searched winner trades a housing-"
        "regime probability (a Hidden Markov Model reading of whether demand is "
        "in its healthy state), holding SPY when the backdrop is favourable and "
        "cash otherwise. It improves risk-adjusted return and drawdown, but the "
        "formal forward-causality tests are weak, so treat the edge as a "
        "search-found timing overlay, not a forecast."
    )

    WHERE_THIS_FITS = (
        "This is a housing leading-indicator signal tested against broad U.S. "
        "equities. The honest reading: the procyclical direction is genuine and "
        "clean in the descriptive quartiles, but the tradable rule is a "
        "searched regime overlay whose out-of-sample edge is concentrated in a "
        "short, episode-heavy window. It is suggestive that housing demand "
        "tracks the equity cycle -- not proof that New Home Sales forecasts the "
        "S&P 500."
    )

    ONE_SENTENCE_THESIS = (
        "The winning New-Home-Sales regime rule improves risk-adjusted return "
        "and drawdown and confirms the procyclical prior in the quartiles, but "
        "forward causality is weak, the winner is a large-search tail with a "
        "non-significant bootstrap p-value, and it should be treated as a "
        "low-confidence searched candidate awaiting a final exam."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final holdout "
        "result. The winner was selected from 5,297 valid strategy "
        "combinations, with bootstrap p=0.071 (above the 5% bar) and low "
        "confidence -- and forward Granger causality is significant only at a "
        "single long lag."
    )

    HERO_TITLE = "New-Home-Sales YoY Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: New Home Sales year-over-year growth (which strips out "
        "the regular spring-vs-winter selling swing, since the raw Census "
        "series is not seasonally adjusted) is shown against SPY on a shared "
        "time axis, with the 0% line marked and the 2008-09 collapse and "
        "2022-23 rate-shock contraction annotated. The winning rule trades a "
        "regime probability derived from this growth series, not the raw level."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by New-Home-Sales Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by New Home Sales "
        "YoY-growth quartile. The gradient runs the RIGHT way -- Sharpe RISES "
        "monotonically from Q1 (weakest growth) at 0.20 to Q4 (strongest) at "
        "1.50, and Q1 carries a -51% drawdown versus Q4's -10%. Stronger "
        "housing demand coincides with better, calmer equities -- the "
        "procyclical prior holds cleanly."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning rule earns a Sharpe ratio -- return per unit of volatility -- of 1.49 versus 0.89 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves to -8.3% from -23.9%, and annualized return is slightly higher, 15.9% versus 14.8%.

New Home Sales is a classic early-cycle housing indicator: buyers commit before construction begins, so sales sit one step ahead of housing starts, permits, and the employment and consumption they drive. The natural prior is **procyclical** -- stronger home-sales demand should coincide with a healthier economy and better equities -- and, unlike several macro pairs in this portal, the direction here comes out the way the prior expects.

### A Seasonally-Raw Series, Read Year-over-Year

The one technical wrinkle that shapes everything: the Census new-home-sales series (FRED `HSN1FNSA`) is **not seasonally adjusted**. Raw sales swing predictably every year -- a spring selling-season peak, a winter trough -- so the raw level and its month-to-month change are dominated by the calendar, not the cycle. Every signal on this page is therefore **deseasonalised**: the headline transform is year-over-year growth (this month versus the same month a year earlier), which cancels a fixed seasonal, backed by a statistically seasonally-adjusted (STL) alternative. We never trade or chart the raw level as a signal.

### The Regime Signal, Not the Raw Number

The winning rule does not trade the year-over-year number directly. It trades a **regime probability**: a Hidden Markov Model (HMM) reads the home-sales growth series and estimates whether housing demand is in its calm, favourable state or its high-variance, turning-point state. The strategy holds SPY when the favourable-regime signal is on and steps to cash otherwise. In plain terms, it asks "is the housing-demand backdrop healthy right now?" and times equity exposure on that.

<!-- expander: Why is confidence low if the direction is right? -->
The procyclical direction is clean in the descriptive quartiles, but "direction is right" and "this is a reliable forecaster" are different claims. The formal forward-causality tests (Granger, local projections) are weak: New Home Sales growth leads SPY only at a single long lag, and the winner is the best of more than five thousand searched combinations with a re-shuffle p-value above the 5% bar. So we report a genuine procyclical relationship AND a low-confidence trading rule -- on purpose, and separately.
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
                "The GFC is the textbook case for New Home Sales as an early-"
                "cycle signal: sales collapsed roughly 80% from their 2005 peak "
                "and turned down well ahead of the 2008-09 equity bear market. "
                "This is the strongest leading-indicator episode for the pair."
            ),
            "caption": "GFC: home sales turned down years ahead of the equity bear -- the leading case.",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During the coronavirus disease 2019 (COVID-19) shock, New Home "
                "Sales spiked on record-low mortgage rates while SPY crashed "
                "and rapidly recovered -- housing demand and the market moved "
                "together in a fast-recovery regime."
            ),
            "caption": "COVID: sales spiked on low rates as SPY recovered.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022-23 mortgage-rate shock, New Home Sales "
                "contracted sharply as 30-year rates jumped -- the strong, "
                "recent regime that dominates the out-of-sample window and "
                "drives much of the strategy's drawdown avoidance."
            ),
            "caption": "2022-23: rate shock crushed sales -- the dominant OOS regime.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history-zoom charts make the leading-indicator character tangible. During the **2008-09 Global Financial Crisis**, new home sales collapsed roughly 80% from their 2005 peak and turned down well ahead of the equity bear market -- the textbook case for housing as an early-cycle signal. During **COVID-19**, sales spiked on record-low mortgage rates as SPY recovered -- a fast-recovery regime. During the **2022-23 rate shock**, sales contracted sharply as mortgage rates jumped -- the strong, recent regime that dominates the out-of-sample window. The Dot-Com window is a continuity confirmer for the portal's standard episode set.
"""

    TRANSITION_TEXT = (
        "The historical story is a genuine early-cycle-housing one, so the full "
        "evidence suite matters. The Evidence page shows the clean procyclical "
        "quartiles alongside the weaker formal causality tests that keep "
        "confidence low."
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
        "Quartile analysis sorts months into four buckets by New Home Sales "
        "YoY-growth and compares subsequent SPY performance. It is descriptive "
        "(concurrent), not the trading rule."
    ),
    question="Do stronger or weaker home-sales growth line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 (weakest home-sales growth) to Q4 (strongest). "
        "A clean rising gradient supports 'stronger housing demand is better "
        "for stocks'; here the gradient does rise cleanly."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Sharpe RISES monotonically from Q1 (weakest NHS YoY) "
        "at 0.20 to Q4 (strongest) at 1.50, and Q1 carries a -51% drawdown "
        "versus Q4's -10%."
    ),
    observation=(
        "The gradient is monotonic and procyclical: the strongest-growth "
        "quartile has the best forward Sharpe and the shallowest drawdown."
    ),
    interpretation=(
        "Stronger housing demand coincides with better, calmer equity returns. "
        "The procyclical prior holds cleanly here -- a contrast with the "
        "money-supply and industrial-production pairs, where the level story "
        "inverted."
    ),
    key_message=(
        "Procyclical and monotonic: stronger home-sales growth lines up with "
        "better, calmer equity returns."
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
    question="Does New Home Sales growth lead SPY -- and at what horizon?",
    how_to_read=(
        "Bars are F-statistics by monthly lag; bars above the dashed line are "
        "significant at the 5% level. The vermillion bars are home sales "
        "leading SPY; the pale-blue bars are SPY leading home sales."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: the forward direction (NHS to SPY) clears the line "
        "only at lag 11; the reverse direction (SPY to NHS) is significant at "
        "lags 1 and 2."
    ),
    observation=(
        "Forward Granger support is weak -- significant only at a single long "
        "lag (11 months); reverse SPY-to-NHS support is present at short lags "
        "(1, 2)."
    ),
    deep_dive_title="Why does a single long lag mean low confidence?",
    deep_dive_content=(
        "A robust leading indicator clears the significance line across a band "
        "of plausible horizons. A single isolated long lag (11 months) is more "
        "consistent with a coincidence in the search than a dependable forward "
        "channel -- especially when the reverse direction (market leading "
        "housing) is significant at short lags."
    ),
    interpretation=(
        "Forward causality is weak and long-horizon. This is the central "
        "reason confidence is low despite the strong headline Sharpe and the "
        "clean procyclical quartiles."
    ),
    key_message="Forward causality is weak (a single long lag); confidence stays low.",
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
        "offsets. Negative lags would mark home-sales growth leading SPY."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF does not establish a clean forward lead from "
        "home-sales growth to SPY, consistent with the weak Granger result."
    ),
    observation=(
        "The cross-correlation does not produce a clean forward-lead signal."
    ),
    interpretation=(
        "The CCF reinforces the Granger conclusion: the forward lead from "
        "home-sales growth to SPY is weak."
    ),
    key_message="The cross-correlation check does not support a strong forward lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after a move in home-sales growth."
    ),
    question="Does a home-sales-growth move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward NHS-to-SPY responses are weak and imprecisely "
        "estimated; the confidence bands are wide relative to the point "
        "estimates."
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
        "That pattern is consistent with a regime effect rather than a simple "
        "linear forward channel from home-sales growth to SPY."
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
        "What this shows: neither the forward (NHS to SPY) nor the reverse "
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
    method_name="HMM Regime Map (The Winning Signal)",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the home-sales growth series into "
        "latent regimes -- a calm, favourable state and a high-variance, "
        "turning-point state."
    ),
    question="When is housing demand in its favourable regime -- and does timing SPY on it help?",
    how_to_read=(
        "Higher probability marks months where home-sales growth behaves "
        "unusually (high-variance). The strategy holds SPY when the favourable "
        "(calm) regime dominates."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the high-variance regime probability spikes around "
        "housing turning points (GFC, COVID, the 2022 rate shock) -- and this "
        "regime probability IS the winning trading signal."
    ),
    observation=(
        "The HMM cleanly separates calm housing-demand regimes from "
        "high-variance turning points."
    ),
    interpretation=(
        "Unlike most pairs where the HMM is only backdrop, here the regime "
        "probability is the winning signal. It still does not rescue the "
        "statistical fragility -- the forward causality is weak and the winner "
        "is search-selected."
    ),
    key_message="The HMM regime probability IS the winner -- but fragility remains.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence: a clean procyclical direction, but weak forward causality",
    "overview": (
        "The regime quartiles are cleanly monotonic -- stronger home-sales "
        "growth lines up with better, calmer SPY returns, confirming the "
        "procyclical prior. But the formal forward-causality tests are weak: "
        "New Home Sales growth Granger-causes SPY only at a single long lag "
        "(11 months), while SPY leads home sales at short lags (1, 2). "
        "Supporting checks (local projections, transfer entropy, quantile "
        "regression) corroborate the weak-forward, regime-driven reading."
    ),
    "plain_english": (
        "This section asks whether New Home Sales really helps predict future "
        "SPY performance. The direction is right and clean in the descriptive "
        "sort, but the formal lead-lag tests are weak, so the strong headline "
        "Sharpe is treated as a low-confidence searched result driven by a "
        "regime signal."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/nhs_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/nhs_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/nhs_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/nhs_spy/rolling_correlation_nhs_spy.csv"},
        {"label": "Stationarity tests", "path": "results/nhs_spy/stationarity_tests_20260703.csv"},
    ],
    "level1": [QUARTILE_BLOCK, GRANGER_BLOCK, HMM_BLOCK, CCF_BLOCK],
    "level1_labels": ["Growth Quartiles", "Granger Causality", "HMM Regimes (Winner)", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy"],
    "tournament_intro": (
        "The tournament tested 7,700 benchmark-excluded strategy combinations, "
        "of which 5,297 passed validity filters. The winning rule is the best "
        "of that valid searched set, so its Sharpe advantage must be read with "
        "the search-position warning attached."
    ),
    "transition": (
        "**Transition:** the direction is procyclical and clean, but forward "
        "causality is weak. The strategy page shows what the rule actually is: "
        "a search-found Long/Cash housing-regime overlay whose drawdown win is "
        "concentrated in a short, episode-heavy OOS window."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Housing-Regime Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched timing overlay: better Sharpe, drawdown, and return than "
        "buy-and-hold in the OOS window -- procyclical as expected, but weak "
        "forward causality, found_in_search, and low statistical confidence."
    )

    PLAIN_ENGLISH = (
        "The rule is simple: when the New-Home-Sales favourable-regime signal "
        "(a Hidden Markov Model reading of deseasonalised year-over-year "
        "growth) is on, hold SPY; otherwise hold cash. It improved Sharpe and "
        "roughly thirded the drawdown in the search-phase OOS window, but the "
        "forward-causality tests are weak, so this is a timing overlay, not a "
        "forecast."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the New-Home-Sales high-variance-regime probability (from a 2-state Hidden Markov Model on deseasonalised year-over-year growth) is above its rolling 25th-percentile threshold (60-month window); otherwise hold cash. No signal lead (L0), because the regime probability is built from already-released data.

If-then form:
- **IF** the regime probability is **above** its rolling 25th-percentile threshold (latest value approximately 0.0123) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2018-02-28 to 2026-05-31, no holdout final exam yet): Sharpe 1.49 vs 0.89 buy-and-hold; annualized return 15.9% vs 14.8%; maximum drawdown -8.3% vs -23.9%; 10 OOS position changes; annual turnover 1.2; OOS win rate 48%.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Census/Federal Reserve monthly new-home-sales release (FRED series HSN1FNSA) and computes its year-over-year growth -- this month's sales versus the same month a year ago. Because the raw series is not seasonally adjusted, the year-over-year change is what strips out the regular spring-vs-winter selling swing. Second, it fits a 2-state Hidden Markov Model to that growth series and reads off the probability of the calm, favourable regime. Third, it compares that probability against a rolling 25th-percentile threshold and converts the comparison into a SPY-or-cash position (no lead needed, since the probability is built from released data).

This is intentionally simple. It does not forecast mortgage rates, model the Fed, or claim that housing drives stocks. It asks whether the housing-demand backdrop is in a healthy regime and times SPY on that -- and, as the Evidence page is careful to say, the formal forward-causality tests are weak.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read New Home Sales (`HSN1FNSA`) from the live FRED API at the current vintage.
2. Compute year-over-year growth (this deseasonalises the not-seasonally-adjusted series).
3. Fit / update the 2-state Hidden Markov Model on the YoY growth series and read the high-variance-regime probability.
4. Compare that probability with its rolling 25th-percentile threshold (60-month window).
5. Hold SPY when the signal is above the threshold; otherwise hold cash.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam, and forward Granger causality is significant only at a single long lag.
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
        "What this shows: the OOS Sharpe distribution across 5,297 valid "
        "searched combinations, with buy-and-hold above the median. The "
        "winner's 1.49 Sharpe is the maximum of the search, not a typical "
        "result -- and its bootstrap p-value (0.071) is above the 5% bar."
    )

    CAVEATS_MD = """
**Why confidence is low (despite the right direction):**

1. Forward causality is weak: Toda-Yamamoto Granger finds New Home Sales YoY leads SPY only at a single long lag (11 months), while SPY leads home sales at short lags (1, 2). A robust leading indicator would clear the line across a band of horizons.
2. The winner came from 5,297 valid searched combinations; its bootstrap p-value is 0.071 -- **above the 5% bar**, so it does not clear conventional significance.
3. The rule is marked `found_in_search` -- it has NOT been confirmed on an untouched final-exam window. In-sample Sharpe is 0.81 versus OOS 1.49, a large gap.
4. Durability is only `conditionally_durable`: the OOS window (2018-2026) is short and dominated by the 2022-23 rate shock; COVID is the only evaluable stress episode.
5. The winning signal is a regime probability, not the raw home-sales number; the raw NSA level and STL level are non-stationary and excluded from the signal set.

**What this means:** use the page as evidence for a genuine procyclical housing relationship AND a low-confidence, search-found timing overlay -- not as proof that New Home Sales forecasts the S&P 500.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the New-Home-Sales favourable-regime probability crosses back "
        "above its rolling threshold, moving from 0% to 100% SPY exposure, and "
        "a SELL back to cash when the regime signal falls below the threshold. "
        "Over the OOS window the rule made 10 such position changes -- a low-"
        "turnover overlay."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-05-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: NHS favourable-regime prob > rolling p25; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Census / Federal Reserve via live FRED API (current vintage) | `HSN1FNSA` New One-Family Houses Sold (thousands, NOT seasonally adjusted) | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "New Home Sales (`HSN1FNSA`) is NOT seasonally adjusted, so the raw level "
    "and raw month-to-month change are dominated by a fixed annual seasonal and "
    "are EXCLUDED as signals. Signals are deseasonalised: year-over-year growth "
    "(the primary transform; a 12-month difference cancels the fixed seasonal), "
    "its acceleration and 3-month-average variant, a statistically seasonally-"
    "adjusted (STL) level and its month-over-month and 3-month growth, and a "
    "rolling z-score of YoY growth. Both the raw level and the STL level are "
    "non-stationary (augmented Dickey-Fuller does not reject a unit root) and "
    "are excluded from the signal set. The winning signal is a 2-state Hidden "
    "Markov Model regime probability fitted on YoY growth, evaluated against a "
    "rolling 25th-percentile threshold with no lead (L0). The daily panel "
    "carries the latest released monthly value forward from the Census release "
    "date (approximately the fourth Tuesday of the following month), so the "
    "strategy does not use future information. New home sales are heavily "
    "revised; the live FRED API is treated as ground truth."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger | Do lagged home-sales values improve SPY forecasts -- or the reverse? | Formal lead-lag test, robust to integration order |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM / Markov regimes | Which months are favourable vs high-variance housing regimes? | Produces the winning regime signal |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: New-Home-Sales transforms x threshold rules x strategy families x orientations x monthly leads (L0-12) x lookbacks. The final tournament file has 7,700 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 5,297 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `hmm_stress / T2_roll_p25 / P1_long_cash (pro) / L0 / LB60`.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/nhs_spy/evidence_status.json` marks the pair `found_in_search`. Forward Granger causality is significant only at a single long lag, reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. U.S. Census Bureau & HUD, New Residential Sales (New One-Family Houses Sold, HSN1FNSA), via FRED.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." (Markov-switching / HMM)
7. Cleveland, R. B. et al. (1990). "STL: A Seasonal-Trend Decomposition Procedure Based on Loess."
8. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Out-of-sample window 2018-02-28 to 2026-05-31, 100 monthly "
        "observations; in-sample ends before the 2018 split. Total tournament "
        "count is 7,700 benchmark-excluded strategy combinations; 5,297 are "
        "valid. Evidence status: found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the New Home Sales analysis. The most "
        "important points: the indicator is not seasonally adjusted (so every "
        "signal is deseasonalised via year-over-year growth or STL), the "
        "procyclical direction is clean in the quartiles, but forward causality "
        "is weak and the winning rule still needs a frozen-rule holdout test."
    ),
)
