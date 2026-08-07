"""Petroleum Inventories x SPY pair configuration (Rule APP-PT1).

Pair `petrol_inv_spy`, Mode 3. Prose is sourced from Research Ray's
`docs/portal_narrative_petrol_inv_spy_20260617.md`; this file wires that
prose to the shared Streamlit templates and Vera's bare-name chart artifacts.

Evidence status is `found_in_search`, so headline performance is labelled as
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/petrol_inv_spy/winner_summary.json`.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Petroleum Inventories as a Low-Confidence Equity Signal"
    PAGE_SUBTITLE = (
        "Total U.S. petroleum stocks (EIA WTTSTUS1) x S&P 500 (SPY), "
        "monthly decision rules with release-lag discipline."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.53 search-phase OOS, drawdown -7.6%: petroleum "
        "inventories look procyclical, but the evidence is low-confidence"
    )

    PLAIN_ENGLISH = (
        "Petroleum inventories have a tricky economic meaning. Inventories "
        "can build because demand is weak, which is usually bad for stocks, "
        "or because supply is strong enough to keep the economy well stocked, "
        "which can be supportive. In this pair, the descriptive evidence "
        "leans procyclical: subsequent SPY performance is best when petroleum "
        "stocks have grown fastest. The searched winner trades a related but "
        "distinct signal -- how high the stock LEVEL sits versus its own "
        "five-year norm -- and holds SPY unless that level is unusually low. "
        "It reduces drawdown and roughly keeps pace on return, but it was "
        "found in a large search, sits in a flat cluster of near-tied rules, "
        "and has not passed a final holdout exam."
    )

    WHERE_THIS_FITS = (
        "This is a commodity-inventory macro signal tested against broad "
        "U.S. equities. It is not a causal oil-market model. The useful "
        "reading is narrower: petroleum stock builds sometimes align with "
        "equity-friendly supply and inflation conditions, but the rule is "
        "still a searched defensive overlay with low confidence."
    )

    ONE_SENTENCE_THESIS = (
        "The winning petroleum-inventory rule improves risk-adjusted return "
        "mainly by reducing drawdown, not by raising annual return, and it "
        "should be treated as a searched candidate awaiting a final exam."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final "
        "holdout result. The winner was selected from 10,991 valid strategy "
        "combinations, with bootstrap p=0.081 and low confidence."
    )

    HERO_TITLE = "Petroleum Inventory Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: petroleum inventory changes and SPY are shown on "
        "the same time axis. Recession shading and stress windows help show "
        "why inventory builds can look counter-cyclical in some crises but "
        "procyclical in the full searched rule."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Petroleum-Stock Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by petroleum "
        "inventory-growth quartile. Q1 Sharpe is 0.37 with 6.0% annualized "
        "return; Q4 Sharpe is 1.25 with 17.5%, supporting the procyclical "
        "interpretation."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- is the right lens here. The winning petroleum-inventory rule earns a Sharpe ratio -- return per unit of volatility -- of 1.53 versus 0.93 for buy-and-hold (buy-and-hold means staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- is -7.6% versus -23.9% for buy-and-hold. Unlike a pure defensive overlay it roughly keeps pace on return: 14.0% annualized versus 15.2% for buy-and-hold. Read that as a risk-control result with modest give-up, not a proven alpha story.

The natural prior is counter-cyclical -- inventories building when demand is weak, which is usually bad for equities. That prior is visible in the Global Financial Crisis (GFC) and coronavirus disease 2019 (COVID-19) windows: petroleum stocks rose as fuel demand weakened. The descriptive evidence overturns that prior on average. The quartile chart shows Q1, the lowest inventory-growth bucket, at Sharpe 0.37 and 6.0% annualized return; Q4, the highest, at Sharpe 1.25 and 17.5%. That endpoint gradient (Q1 to Q4) corroborates a procyclical -- moving with the equity cycle -- interpretation.

### What the Winner Actually Trades

One honest wrinkle: the descriptive quartile evidence sorts on inventory *growth*, but the searched winner trades a different transform -- the **60-month z-score of the stock LEVEL** (how high petroleum stocks sit versus their own five-year norm), lagged 11 months, held long unless that level is in the bottom quartile of its recent range. Direction is still procyclical, but the specific winning signal, its 11-month lead, and its threshold are a tournament selection from a flat cluster of near-tied rules -- not a uniquely identified relationship. The runner-up (a different transform at the same L11) is only 0.003 Sharpe behind.

### Direction Reconciliation

The credible economic mechanism is a hypothesis, not a fact. A petroleum inventory build can mean weak demand, but it can also mean robust supply and production availability. In that second state, softer energy-price pressure can help consumers and corporate margins, creating an equity tailwind. That is the procyclical mechanism the data appear to favor in this pair.

Timing is the weak point. Granger causality -- a test of whether past values of one series improve forecasts of another -- is significant at 6, 7, and 8 months for petroleum inventories leading SPY, with no reverse SPY-to-inventory signal. So there IS a weak forward signal -- but the tournament-selected rule trades at **L11, not 6-8 months**, and (as the Lead Tournament tab shows) the winning rule's own Sharpe is actually *weakest* around those causal lags. Treat the 11-month lead as a searched choice, not the causally-motivated horizon.

<!-- expander: Why is the inventory direction tricky? -->
Inventories have two meanings. In a demand collapse, they pile up because consumers and firms are buying less fuel; that is counter-cyclical. In an expansion, they can rise because supply chains and production are strong enough to keep the economy well supplied; that can be procyclical. This pair's charts show both possibilities, which is why the narrative leads with the contradiction rather than hiding it.
<!-- /expander -->
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The Dot-Com chart is included for continuity across the "
                "portal's standard episode set. Read it as contextual "
                "background, not the strongest validation case."
            ),
            "caption": "Contextual background for the long-lead petroleum inventory signal.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "During the Global Financial Crisis, inventories rose in a "
                "way that matches the counter-cyclical prior: demand weakened "
                "and stocks built."
            ),
            "caption": "GFC shows the counter-cyclical failure-case prior.",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "During COVID, petroleum stocks rose as mobility and fuel "
                "demand collapsed. This is the clearest reminder that an "
                "inventory build is not automatically bullish."
            ),
            "caption": "COVID shows abrupt inventory build during a demand collapse.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022 inflation shock, the Long/Cash strategy "
                "mostly stayed defensive and avoided drawdown. That is a "
                "risk-control result, not proof of higher long-run return."
            ),
            "caption": "2022 is a confirmer for drawdown control, not a causal proof.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history zoom charts make the caveat tangible. During the GFC and COVID shock, inventories rose in ways that match the counter-cyclical prior. During the 2022 inflation shock, the Long/Cash strategy mostly stayed defensive and avoided drawdown, but that is a risk-control result rather than a proof of higher long-run return. The Dot-Com chart exists for continuity across the portal's standard episode set; it should be read as contextual background, not as the strongest validation case.
"""

    TRANSITION_TEXT = (
        "The historical story is mixed enough that we need the full evidence "
        "suite. The Evidence page separates the procyclical quartile result "
        "from weaker timing and statistical-certainty checks."
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
    method_name="Quartile Gradient",
    method_theory=(
        "Quartile analysis sorts months into four buckets from low to high "
        "petroleum-stock growth and compares subsequent SPY performance."
    ),
    question="Do higher petroleum-stock builds line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 to Q4. If returns and Sharpe improve as the "
        "quartile rises, the evidence supports a procyclical interpretation."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Q1 Sharpe is 0.37 and Q4 Sharpe is 1.25; annualized "
        "return rises from 6.0% to 17.5%."
    ),
    observation=(
        "The endpoint gradient is clear: lowest inventory growth has weak "
        "forward SPY performance, while highest inventory growth has the "
        "best forward performance."
    ),
    interpretation=(
        "This is the cleanest support for direction. It does not prove "
        "causality, but it overturns the simple weak-demand prior for this "
        "searched rule."
    ),
    key_message=(
        "The descriptive evidence leans procyclical: stronger petroleum-stock "
        "growth lines up with stronger later SPY performance."
    ),
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past petroleum-inventory values "
        "improve forecasts of SPY beyond SPY's own history."
    ),
    question="Does the inventory signal lead SPY, and at which monthly lags?",
    how_to_read=(
        "Vermillion bars are petroleum inventories leading SPY. Bars above "
        "the dashed line are statistically meaningful at the 5% level."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: petroleum inventories clear the line at lags 6, 7, "
        "and 8; the reverse SPY-to-inventory direction does not."
    ),
    observation=(
        "Forward Granger support clusters at 6-8 months, while reverse "
        "SPY-to-inventory support is absent."
    ),
    deep_dive_title="Why doesn't the winner trade the 6-8 month causal lag?",
    deep_dive_content=(
        "The formal Granger evidence clusters at lags 6-8, but the tournament "
        "winner trades at L11 -- and its own Sharpe-by-lead curve is actually "
        "weakest around 6-8 months. The tradable edge and the causal lag point "
        "at different horizons, so the 11-month lead is a searched choice, not "
        "a causally-endorsed one."
    ),
    interpretation=(
        "There is a weak medium-horizon forward signal, but it neither "
        "certifies the winner's 11-month lead nor aligns with it -- the causal "
        "lags (6-8) are where the winning rule performs worst."
    ),
    key_message="A weak forward lead exists at 6-8 months, but the winner trades L11 -- timing is not causally identified.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation removes each series' own persistence "
        "before checking whether one echoes the other at monthly offsets."
    ),
    question="Is there a clean lead-lag echo after removing autocorrelation?",
    how_to_read=(
        "Bars outside the confidence band indicate statistically meaningful "
        "offsets. Positive lags mark petroleum leading SPY in this chart."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF flags lag +6 as significant, consistent "
        "with the Granger medium-horizon band."
    ),
    observation=(
        "The meaningful CCF signal appears around +6 months, not uniformly "
        "across all lags."
    ),
    interpretation=(
        "The CCF supports a medium-horizon relationship but reinforces the "
        "same caveat: timing is approximate."
    ),
    key_message="The cross-correlation check supports a 6-month lead signal.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after an inventory move."
    ),
    question="Does a petroleum-stock move produce statistically clear forward responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward coefficients are not statistically strong "
        "across horizons."
    ),
    observation=(
        "The local-projection panel does not produce significant forward "
        "coefficients."
    ),
    interpretation=(
        "The result is not a broad linear impulse-response story. The "
        "strategy relies more on state sorting than on a clean average effect."
    ),
    key_message="Local projections weaken the statistical-confidence case.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression asks whether the relationship differs in weak, "
        "normal, and strong SPY-return environments."
    ),
    question="Is the signal most useful in the tails or in stronger markets?",
    how_to_read=(
        "Read coefficient estimates across return quantiles. A stronger "
        "right-tail pattern fits a procyclical interpretation better than a "
        "crash-hedge interpretation."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: coefficient support is more favorable in upper "
        "return quantiles."
    ),
    observation=(
        "The quantile view is more favorable in stronger return states than "
        "in left-tail crash states."
    ),
    interpretation=(
        "That pattern fits the supply/tailwind interpretation better than a "
        "pure downside hedge story."
    ),
    key_message="Quantile evidence fits a procyclical tailwind story.",
)

TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy is a nonlinear information-flow check that can "
        "catch relationships missed by linear tests."
    ),
    question="Is there nonlinear directed information flow from inventories to SPY?",
    how_to_read=(
        "Small permutation p-values indicate genuine directed information "
        "flow. Large p-values indicate no reliable nonlinear channel."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: transfer entropy is not significant in either direction."
    ),
    observation="Neither direction shows significant nonlinear information flow.",
    interpretation=(
        "The nonlinear check does not rescue the strategy's low-confidence "
        "status."
    ),
    key_message="No nonlinear information-flow result strengthens the case.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the inventory series into latent "
        "high-variance regimes."
    ),
    question="When did petroleum inventories sit in unusual regimes?",
    how_to_read=(
        "Higher regime probability marks months where inventory behavior "
        "looks unusual relative to the long sample."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the HMM is useful as a backdrop, not as the "
        "winning trading signal."
    ),
    observation=(
        "The HMM highlights stress and high-variance inventory environments, "
        "including major crisis windows."
    ),
    interpretation=(
        "The regime map helps explain context, but the winning rule is the "
        "three-month inventory change threshold, not HMM probability."
    ),
    key_message="The HMM explains backdrop; it does not validate the winner by itself.",
)

CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "For a monthly-rebalanced strategy the decision is: how stale should "
        "the signal be allowed to get before we trade on it? This block "
        "computes Pearson correlations between the petroleum-inventory signal "
        "lagged L = 0…12 months and the SPY 1-month forward return, then reads "
        "off which lead maximises predictive content — and compares that to "
        "the tournament's traded 11-month lead."
    ),
    question=(
        "Which lead carries the most predictive content for the winning "
        "level-z-score signal — and how does that compare to the traded "
        "11-month lead?"
    ),
    how_to_read=(
        "Rows are inventory signal variants; columns are signal lead in MONTHS "
        "(L0 = contemporaneous, L12 = 12 months ago). Forward horizon fixed at "
        "1 month. Cell shading is Pearson r (linear co-movement, -1 to +1) "
        "against `spy_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson correlations between **signal lagged L months** and **SPY "
        "1-month forward return**. The traded signal `petrol_inv_zscore_60m` "
        "is weak at every lead — its largest cell is **L3 (r=+0.041, NOT "
        "significant)** — and it actually turns slightly NEGATIVE by the "
        "traded **L11 (r=−0.036)**. No lead clears the p<0.05 band. The linear "
        "read gives no endorsement to the traded 11-month lead."
    ),
    observation=(
        "Reading the row directly: every cell is small and none is "
        "significant. The largest is L3 (r=+0.041), and the correlation drifts "
        "to slightly negative at the traded lag (L11 r=−0.036, L12 r=−0.039). "
        "So on the pure linear test the winning level-z-score signal carries "
        "**no meaningful next-month-SPY content at any lead**, least of all at "
        "the 11-month lead the tournament selected."
    ),
    interpretation=(
        "An honest null: **the lead-correlation view does not support the "
        "traded L11** — its best cell (L3, +0.041) is statistically "
        "indistinguishable from zero and the traded lead is faintly negative. "
        "Unlike the quartile sort (which leans procyclical on inventory "
        "growth), this direct linear test of the *level z-score* finds nothing "
        "at any lead. **In plain English:** the specific signal and lead the "
        "search crowned are not corroborated by a simple correlation check — "
        "the edge, such as it is, lives in the full strategy backtest, not in "
        "a clean predictive latency."
    ),
    key_message=(
        "The traded signal `petrol_inv_zscore_60m` is insignificant at every "
        "lead (best |r|=0.041 at L3, n.s.) and slightly negative at the traded "
        "**L11** — the correlation view gives the traded lead no endorsement. "
        "The timing is a tournament choice, not a correlation-endorsed latency."
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This chart is a projection of the pair's ONE native tournament (GH #13 "
        "single-source): the orange line is the **published winner's own** OOS "
        "Sharpe at each lead; the grey bars are the best-of-any-signal envelope "
        "on the SAME grid; the dashed line is SPY buy-and-hold (Sharpe 0.93). "
        "Every lead L1–L12 was scored directly by the native tournament on the "
        "**deployable** series, so all markers are solid — nothing patched. "
        "Read it alongside the 'weaker on timing' caveat that runs through this "
        "pair."
    ),
    question=(
        "On the tournament's own grid, is the winner's L11 a robust ridge or a "
        "single-lead spike — and does its edge line up with the 6–8 month "
        "causal lag or the short-lead correlation?"
    ),
    how_to_read=(
        "Orange line + green star: the deployed winner's Sharpe by lead, peaking "
        "at its traded L11. A broad plateau around the traded lead is robust; a "
        "tall isolated point that collapses one lead either side is fragile. "
        "Grey bars: the best any signal achieves at each lead (envelope ≥ the "
        "winner curve by construction)."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "The winner's own curve is a **sharp spike at its traded L11 (OOS "
        "Sharpe 1.5273)** that collapses to ~1.2 at L10 and ~0.95 at L12, and "
        "sags to its WORST (0.77–0.90) at L6–8 — exactly the Granger-causal "
        "lags. L11 is also the top of the cross-signal envelope, but the "
        "envelope is **nearly flat** (leads span ~1.29–1.53, top-two margin "
        "only 0.05), so no lead is decisively best. A flat envelope plus a "
        "single-lead winner spike is a weakly-identified, searched result."
    ),
    observation=(
        "On the native tournament grid the published winner "
        "(`petrol_inv_zscore_60m / T2_roll_p25 / P1_long_cash`, OOS Sharpe "
        "**1.5273**) sits at the top of the lead profile at its traded L11 — "
        "its own curve and the cross-signal envelope both peak there. But two "
        "honesty flags sit right on the chart. First, the winner's own curve is "
        "a **single-lead spike**: 1.53 at L11, but ~1.25 at L10 and ~0.95 at "
        "L12, and it is **weakest (0.77–0.90) at L6–8** — the very lags where "
        "Granger finds the forward signal. The tradable edge and the causal lag "
        "are in different places. Second, the cross-signal envelope is **nearly "
        "flat** (best-per-lead ranges ~1.29–1.53; the next-best lead, L12 at "
        "1.4779, is only 0.05 behind), and within L11 a runner-up combo is just "
        "0.003 behind — so the winning lead AND combo are weakly separated.\n\n"
        "(An earlier version of this chart drew its bars from a separate "
        "exploratory sweep on a different grid; that was a grid artefact. On the "
        "tournament's own grid — the one that selected the winner, scored on the "
        "deployable series across the full L1–L12 — L11 is the top, but of a "
        "flat, near-tied profile.) Combined with the null lead-correlation "
        "result, the honest read is a searched in-window result, not a robust "
        "predictive ridge."
    ),
    interpretation=(
        "The honest summary: **the winner's L11 is the envelope peak but a "
        "sharp single-lead spike on an otherwise flat profile, and it sits away "
        "from — indeed at a trough of — the 6–8 month causal lag.** The lead is "
        "weakly identified, the combo is one of a near-tied L11 cluster, and the "
        "lead-correlation diagnostic finds nothing significant at any lead. A "
        "reader should treat the strong OOS Sharpe as a searched result that "
        "scores well in one window and weight it as low-confidence, exactly as "
        "the rest of this page advises."
    ),
    key_message=(
        "On the native grid the winner's lead L11 (OOS Sharpe 1.5273) is the "
        "top of a **nearly flat** envelope (top-two margin 0.05) and a sharp "
        "single-lead spike whose curve is weakest at the 6–8 month causal lags. "
        "With a null lead-correlation and a near-tied L11 cluster (runner-up "
        "0.003 behind), that Sharpe is a searched, low-confidence result, not a "
        "discovered predictive lead."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence is supportive on direction, weaker on timing and statistical certainty",
    "overview": (
        "Quartile sorting gives the clearest procyclical direction evidence. "
        "Lead-lag tests support a medium-horizon relationship, while local "
        "projections and transfer entropy keep confidence low."
    ),
    "plain_english": (
        "This section asks whether petroleum inventories really help explain "
        "future SPY performance. The simple sorting evidence is favorable, "
        "but the more technical tests are mixed enough that this remains a "
        "low-confidence searched result."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/petrol_inv_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/petrol_inv_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/petrol_inv_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 24-month correlation (357 rows)", "path": "results/petrol_inv_spy/rolling_correlation_petrol_inv_spy.csv"},
        {"label": "Stationarity tests (24 rows)", "path": "results/petrol_inv_spy/stationarity_tests_20260617.csv"},
    ],
    "level1": [QUARTILE_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Quartile Gradient", "Lead Analysis", "Lead Tournament", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK, HMM_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy", "HMM Regimes"],
    "tournament_intro": (
        "The tournament tested 16,016 benchmark-excluded strategy combinations, "
        "of which 10,991 passed validity filters. The winning rule is the best "
        "of that valid searched set, so its Sharpe advantage must be read with "
        "the search-position warning attached."
    ),
    "transition": (
        "**Transition:** the evidence supports a plausible procyclical signal, "
        "but the strategy page is where the tradeoff becomes clear: lower "
        "drawdown, lower annual return, and low confidence."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Petroleum-Inventory Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched defensive overlay: better Sharpe and drawdown than "
        "buy-and-hold, but lower annual return and low statistical confidence."
    )

    PLAIN_ENGLISH = (
        "The rule is a level-regime overlay: it looks at how high petroleum "
        "stocks sit versus their own five-year norm (a 60-month z-score), "
        "reads that value from 11 months earlier, and holds SPY unless the "
        "level is unusually low (in the bottom quartile of its recent range); "
        "otherwise it holds cash. It reduced drawdown in the search-phase OOS "
        "window and roughly kept pace with the market on return, but it is a "
        "searched rule sitting in a flat cluster of near-tied alternatives."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 11-month-lagged 60-month z-score of petroleum stocks is above its rolling 25th-percentile threshold (i.e. unless the level is in the bottom quartile of its recent range); otherwise hold cash.

If-then form:
- **IF** `petrol_inv_zscore_60m` from 11 months ago is **above its rolling 25th-percentile threshold** (latest value -2.2581) -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-08-31 to 2025-09-30, no holdout final exam yet): Sharpe 1.53 vs 0.93 buy-and-hold; annualized return 14.0% vs 15.2%; maximum drawdown -7.6% vs -23.9%; 10 OOS trades; annual turnover 1.22. The threshold is a rolling 25th percentile (36-month window), so it moves over time — see `winner_trade_log.csv` for the full path.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads Energy Information Administration (EIA) petroleum inventory releases and carries the latest public value forward to the monthly decision date. Second, it standardizes the stock LEVEL as a rolling 60-month z-score -- how far current inventories sit above or below their own five-year norm. Third, it compares the value from 11 months earlier with a rolling 25th-percentile threshold and converts that comparison into a SPY-or-cash position: long unless the standardized level is in the bottom quartile of its recent range.

This is intentionally simple. It does not forecast oil prices, estimate refinery demand, or model the full energy complex. It asks whether a broad physical-stock level measure has historically lined up with a better or worse SPY allocation.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Pull total petroleum stocks (`WTTSTUS1`) from the EIA source used in the project data bundle.
2. Standardize the stock level as a rolling 60-month z-score (`petrol_inv_zscore_60m`).
3. Apply the 11-month lag before making the monthly SPY allocation decision.
4. Compare the lagged z-score with its rolling 25th-percentile threshold (36-month window; latest value -2.2581).
5. Hold SPY when the lagged z-score is above the threshold; otherwise hold cash.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam, and the winning combo sits in a flat cluster of near-tied rules.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Protection is "
        "episode-dependent, with COVID strong and several windows limited "
        "by insufficient OOS rows."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 10,991 valid "
        "searched combinations. The winner's 1.53 Sharpe is the maximum of "
        "the search, not a typical result -- and it sits only ~0.003 above the "
        "runner-up."
    )

    CAVEATS_MD = """
**Why confidence is low:**

1. The winner came from 10,991 valid searched combinations, so a strong-looking maximum can occur by chance -- and it sits in a **flat cluster of near-tied rules**: the runner-up (a different transform at the same 11-month lead) is only ~0.003 Sharpe behind, and the best-per-lead envelope is nearly flat across the whole grid.
2. Bootstrap p-value is 0.081, which is suggestive but not significant at the 5% level; durability is only `conditionally_durable`.
3. Granger evidence clusters at 6-8 months, but the selected rule trades at **L11** -- and the winning rule's own Sharpe is *weakest* around those causal lags. The traded lead is not the causal horizon, and the direct lead-correlation check is insignificant at every lead.
4. The strategy improves drawdown and roughly matches buy-and-hold on return, but the edge is a searched, in-window result.
5. The mechanism is plausible but not causal; inventories can mean demand weakness or supply availability depending on regime, and the winner trades the stock *level* z-score, a different transform from the growth measure the quartile evidence sorts on.

**What this means:** use the page as evidence for a candidate defensive overlay, not as proof of a durable petroleum-inventory alpha signal.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** on **1995-12-31** the "
        "broker-style log records a BUY. The rule saw the 11-month-lagged "
        "level z-score `petrol_level_z60=0.065`, above its rolling threshold "
        "(-0.654), and moved from 0% to 100% SPY exposure. On **1996-02-29**, "
        "the log records a SELL after the lagged z-score (-0.741) fell below "
        "the rolling threshold (-0.712), moving back to cash."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1995-12-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash_pro: petrol_level_z60=0.065 threshold=-0.654; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | EIA weekly petroleum stocks via project Data Master.xlsx | `WTTSTUS1` total petroleum stocks | Weekly source, monthly aligned |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw petroleum-stock level is transformed into year-over-year change, "
    "short-horizon percentage change, 3-month percentage change, 6-month "
    "percentage change, trend deviation, and z-scores. The winning signal is "
    "`petrol_inv_zscore_60m`, a rolling 60-month z-score of the petroleum-stock "
    "LEVEL (how far current inventories sit from their five-year norm). "
    "The daily panel carries the latest public petroleum value forward, so "
    "the strategy does not use future inventory information."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Granger causality | Do lagged inventories improve SPY forecasts? | Formal lead-lag test across monthly lags |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow? | Model-free nonlinear robustness check |
| HMM regimes | Which months are unusual inventory regimes? | Backdrop and regime context, not the winning signal |
| Cross-period checks | Does the strategy persist across periods? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: petroleum inventory transforms x threshold rules x strategy families x orientations x leads x lookbacks. The final tournament file has 16,016 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 10,991 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `petrol_level_z60 / T2_roll_p25 / P1_long_cash (pro) / L11 / LB36`, scored on the deployable cash-filled series across the full L0-12 grid (GH#13). It is the unique OOS-Sharpe maximum but sits in a flat, near-tied L11 cluster.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/petrol_inv_spy/evidence_status.json` marks the pair `found_in_search`.
"""

_REFERENCES_MD = """
1. U.S. Energy Information Administration, weekly petroleum stocks series WTTSTUS1.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
5. Simonsohn, U., Simmons, J. P. & Nelson, L. D. (2020). "Specification curve analysis."
6. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Out-of-sample window 2017-08-31 to 2025-09-30, 98 monthly "
        "observations. Total tournament count is 16,016 benchmark-excluded "
        "strategy combinations; 10,991 are valid. Evidence status: "
        "found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, "
        "and tournament design behind the petroleum-inventory analysis. The "
        "most important limitation is that the winning rule was found in a "
        "large search and still needs a frozen-rule holdout test."
    ),
)
