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
        "## Sharpe 1.48 search-phase OOS, drawdown -6.3%: petroleum "
        "inventories look procyclical, but the evidence is low-confidence"
    )

    PLAIN_ENGLISH = (
        "Petroleum inventories have a tricky economic meaning. Inventories "
        "can build because demand is weak, which is usually bad for stocks, "
        "or because supply is strong enough to keep the economy well stocked, "
        "which can be supportive. In this pair, the statistical evidence "
        "leans procyclical: higher three-month inventory growth lines up "
        "with better later SPY performance. The trading rule reduces "
        "drawdown, but it gives up annual return and has not passed a final "
        "holdout exam."
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
        "holdout result. The winner was selected from 5,123 valid strategy "
        "combinations, with bootstrap p=0.099 and low confidence."
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

Out-of-sample (OOS) -- tested on data not used to pick the rule -- is the right lens here. The winning petroleum-inventory rule earns a Sharpe ratio -- return per unit of volatility -- of 1.48 versus 0.93 for buy-and-hold (buy-and-hold means staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- is -6.3% versus -23.9% for buy-and-hold. That sounds useful, but it is not a clean alpha story: annualized return is lower, 9.8% versus 15.2%.

The natural prior is counter-cyclical -- inventories building when demand is weak, which is usually bad for equities. That prior is visible in the Global Financial Crisis (GFC) and coronavirus disease 2019 (COVID-19) windows: petroleum stocks rose as fuel demand weakened. The empirical result overturns that prior for the searched rule. The quartile chart shows Q1, the lowest 3-month petroleum-stock change, at Sharpe 0.37 and 6.0% annualized return; Q4, the highest 3-month change, at Sharpe 1.25 and 17.5%. That monotonic gradient corroborates a procyclical -- moving with the equity cycle -- interpretation.

### Direction Reconciliation

The credible economic mechanism is a hypothesis, not a fact. A petroleum inventory build can mean weak demand, but it can also mean robust supply and production availability. In that second state, softer energy-price pressure can help consumers and corporate margins, creating an equity tailwind over the following year. That is the procyclical mechanism the data appear to favor in this pair.

Timing is less precise. Granger causality -- a test of whether past values of one series improve forecasts of another -- is significant at 6, 7, and 8 months for petroleum inventories leading SPY, with no reverse SPY-to-inventory signal. The tournament-selected rule uses L12, a 12-month lead. Treat the evidence as a 6-12 month lead band, not as proof that exactly 12 months is the true horizon.

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
    deep_dive_title="Why not read this as exactly a 12-month lead?",
    deep_dive_content=(
        "The tournament winner uses L12, but the formal Granger evidence "
        "clusters at lags 6-8. The honest timing claim is a 6-12 month band."
    ),
    interpretation=(
        "There is some medium-horizon lead evidence, but it is not precise "
        "enough to certify the selected 12-month rule as uniquely correct."
    ),
    key_message="Lead-lag support exists, but timing is imprecise.",
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
        "the tournament's traded 12-month lead."
    ),
    question=(
        "Which lead carries the most predictive content for the petroleum-"
        "inventory signal — and how does that compare to the traded 12-month "
        "lead?"
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
        "1-month forward return**. The traded signal `petrol_inv_3m_pct` "
        "peaks early at **L3 (r=+0.106, p<0.05)** and L4 (+0.103, p<0.05), "
        "then fades to near-zero by L12 — so the linear predictive content "
        "sits at a SHORT lead, NOT the traded 12-month lead. An honest "
        "divergence, explained in the Lead Tournament tab."
    ),
    observation=(
        "Reading the row directly: the signal's significant cells are at the "
        "**short end** — L3 (r=+0.106, p<0.05) and L4 (r=+0.103, p<0.05) — "
        "and it decays to essentially zero at the traded lag (L12 r=−0.027). "
        "So on the pure linear test, the petroleum-inventory signal's "
        "predictive content for next-month SPY is concentrated around a "
        "3–4 month lead, well short of the 12-month lead the tournament "
        "selected."
    ),
    interpretation=(
        "An honest divergence: **the lead-correlation peak (L3–L4) is far from "
        "the traded lead (L12)**. The short-lead correlation is the cleaner "
        "linear read of the inventory→equity channel (inventory swings feed "
        "through to energy-sector and broad earnings over a quarter or two). "
        "The 12-month traded lead is a tournament selection on the full "
        "strategy grid, not where the linear signal is strongest. **In plain "
        "English:** the data says petroleum inventories carry their best "
        "next-month-SPY signal about a quarter out, yet the published rule "
        "reads a full year back — a gap the reader should know about when "
        "judging the strategy's timing confidence."
    ),
    key_message=(
        "The traded signal peaks at **L3 (r=+0.106, p<0.05)** and L4, fading "
        "to zero by L12 — so the linear predictive content sits at a SHORT "
        "lead, not the traded 12-month lead. An honest divergence that flags "
        "the strategy's timing as a tournament choice, not a correlation-"
        "endorsed latency."
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block sweeps the monthly lead grid L = 0…12 and plots the best "
        "OOS Sharpe at each lead (blue bar) against all valid combos (grey "
        "strip); the dashed orange line is SPY buy-and-hold (Sharpe 0.93). "
        "Read it alongside the 'weaker on timing' caveat that runs through "
        "this pair."
    ),
    question=(
        "Where does the traded 12-month lead sit on the sweep — and is its "
        "Sharpe a robust ridge or an off-peak point, given the correlation "
        "peak sits at L3–L4?"
    ),
    how_to_read=(
        "Bars: max OOS Sharpe at each monthly lead. Strip dots: every valid "
        "combination at that lead. A tall thin spike is a single combo; a "
        "flat-but-wide cloud is a robust regime."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "Best OOS Sharpe per monthly lead (blue bars) and the full "
        "distribution (grey strip). The profile peaks at **L10 (1.53)** and "
        "L11 (1.44); the traded **L12 (1.20)** sits just past the peak on the "
        "down-slope, while the correlation-favoured short leads (L3 1.30, L5 "
        "1.33) form a separate cluster. Every lead clears buy-and-hold (0.93)."
    ),
    observation=(
        "Reading the monthly bars: the Sharpe profile rises to a **late-lead "
        "peak at L10 (1.53)** and L11 (1.44), then the traded **L12 (1.20) "
        "falls off that peak**. There is also a respectable short-lead cluster "
        "(L0 1.33, L3 1.30, L5 1.33) near where the lead-correlation content "
        "concentrates. So the grid has TWO weakly-separated regions of "
        "interest — a short-lead one (matching the correlation) and a "
        "late-lead one (around L10–L11) — and the traded L12 sits at the "
        "trailing edge of the late cluster.\n\n"
        "The published winner (`petrol_inv_3m_pct / T1_fixed_p50 / "
        "P1_long_cash`, OOS Sharpe **1.4779**) trades at L12. Its lead is "
        "neither the correlation peak (L3) nor the Sharpe peak (L10) — it is a "
        "tournament selection that lands just past the late-lead ridge. "
        "Consistent with this pair's 'weaker on timing' framing, the lead is "
        "best described as **plausible but not pinpointed**: the broad late-"
        "lead region is real, but the exact L12 is not where either diagnostic "
        "peaks."
    ),
    interpretation=(
        "The honest summary: **the traded L12 sits just past a late-lead "
        "Sharpe ridge (peak L10 1.53), while the correlation evidence favours "
        "a short L3–L4 lead** — the two diagnostics point at different parts "
        "of the grid, and the traded lead matches neither peak exactly. The "
        "late-lead region is broad enough that L12 is not fragile, but a "
        "reader should treat the precise 12-month timing as a tournament "
        "artefact rather than a sharply-identified latency — exactly the "
        "'supportive on direction, weaker on timing' verdict this page already "
        "carries."
    ),
    key_message=(
        "The Sharpe profile peaks at **L10 (1.53)** with the traded **L12 "
        "(1.20)** just past it on the down-slope, while the correlation favours "
        "a short L3–L4 lead. The two diagnostics disagree and the traded lead "
        "matches neither peak — plausible but not pinpointed. Winner OOS Sharpe "
        "1.4779; read the 12-month timing as a tournament choice."
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
        {"label": "Rolling 24-month correlation (356 rows)", "path": "results/petrol_inv_spy/rolling_correlation_petrol_inv_spy.csv"},
        {"label": "Stationarity tests (24 rows)", "path": "results/petrol_inv_spy/stationarity_tests_20260617.csv"},
    ],
    "level1": [QUARTILE_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Quartile Gradient", "Lead Analysis", "Lead Tournament", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK, HMM_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy", "HMM Regimes"],
    "tournament_intro": (
        "The tournament tested 7,392 benchmark-excluded strategy combinations, "
        "of which 5,123 passed validity filters. The winning rule is the best "
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
        "The rule is simple: if the three-month change in petroleum stocks "
        "from 12 months ago is above 0.323, hold SPY; otherwise hold cash. "
        "It reduced drawdown in the search-phase OOS window, but it did so "
        "by stepping out of the market and giving up annual return."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 12-month-lagged three-month petroleum inventory change is greater than 0.323; otherwise hold cash.

If-then form:
- **IF** `petrol_inv_3m_pct` from 12 months ago is **above 0.323** -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-08-31 to 2025-09-30, no holdout final exam yet): Sharpe 1.48 vs 0.93 buy-and-hold; annualized return 9.8% vs 15.2%; maximum drawdown -6.3% vs -23.9%; 19 OOS trades; annual turnover 2.33.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads Energy Information Administration (EIA) petroleum inventory releases and carries the latest public value forward to the monthly decision date. Second, it computes the three-month percentage change, which captures whether stocks have recently built or drawn down. Third, it compares the value from 12 months earlier with the 0.323 threshold and converts that comparison into a SPY-or-cash position.

This is intentionally simple. It does not forecast oil prices, estimate refinery demand, or model the full energy complex. It asks whether a broad physical-stock measure has historically lined up with a better or worse SPY allocation.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Pull total petroleum stocks (`WTTSTUS1`) from the EIA source used in the project data bundle.
2. Compute the three-month percentage change.
3. Apply the 12-month lag before making the monthly SPY allocation decision.
4. Compare the lagged value with the fixed threshold `0.323`.
5. Hold SPY when the lagged signal is greater than the threshold; otherwise hold cash.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam.
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
        "What this shows: the OOS Sharpe distribution across 5,123 valid "
        "searched combinations. The winner's 1.48 Sharpe is the maximum of "
        "the search, not a typical result."
    )

    CAVEATS_MD = """
**Why confidence is low:**

1. The winner came from 5,123 valid searched combinations, so a strong-looking maximum can occur by chance.
2. Bootstrap p-value is 0.099, which is suggestive but not significant at the 5% level.
3. Granger evidence clusters at 6-8 months, while the selected rule uses L12.
4. The strategy improves drawdown but gives up annualized return versus buy-and-hold.
5. The mechanism is plausible but not causal; inventories can mean demand weakness or supply availability depending on regime.

**What this means:** use the page as evidence for a candidate defensive overlay, not as proof of a durable petroleum-inventory alpha signal.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** on **1994-06-30** the "
        "broker-style log records a BUY. The rule saw "
        "`petrol_3m=3.712`, above the 0.323 threshold, and moved from 0% "
        "to 100% SPY exposure. On **1994-10-31**, the log records a SELL "
        "after `petrol_3m=0.019` fell below the threshold, moving back to cash."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1994-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash_pro: petrol_3m=3.712 threshold=0.323; position 0% to 100%",
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
    "`petrol_inv_3m_pct`, a three-month petroleum-stock momentum measure. "
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
Grid: petroleum inventory transforms x threshold rules x strategy families x orientations x leads x lookbacks. The final tournament file has 7,392 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 5,123 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `petrol_3m / T1_fixed_p50 / P1_long_cash (pro) / L12 / LB_NA`.

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
        "observations. Total tournament count is 7,392 benchmark-excluded "
        "strategy combinations; 5,123 are valid. Evidence status: "
        "found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, "
        "and tournament design behind the petroleum-inventory analysis. The "
        "most important limitation is that the winning rule was found in a "
        "large search and still needs a frozen-rule holdout test."
    ),
)
