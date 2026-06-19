---
{
  "pair_id": "m2sl_yoy_spy",
  "narrative_version": "1.0.0",
  "generated_at": "2026-06-19T00:00:00Z",
  "headline_template": "A",
  "pages": {
    "story": {
      "headline": "Sharpe 1.69 OOS, drawdown -4.0%: a money-growth acceleration overlay — but causality runs in reverse and confidence is low",
      "sections": [
        {"id": "headline_findings", "title": "Headline Findings", "anchor": "headline-findings"},
        {"id": "causality_first", "title": "The Honest Headline: Causality Runs in Reverse", "anchor": "causality-first"},
        {"id": "direction_reconciliation", "title": "Acceleration, Not Level", "anchor": "direction-reconciliation"},
        {"id": "what_history_shows", "title": "What History Shows", "anchor": "what-history-shows"}
      ],
      "expanders": [
        {"id": "why_acceleration_not_level", "title": "Why acceleration, not the level?"}
      ]
    },
    "evidence": {
      "headline": "The forward signal is empty; the edge is a search-found acceleration pattern",
      "sections": [
        {"id": "lead_lag_tests", "title": "Lead-Lag Tests (Reverse-Only)", "anchor": "lead-lag-tests"},
        {"id": "quartile_gradient", "title": "Level Quartiles: High-Money-Growth Is the Riskiest Regime", "anchor": "quartile-gradient"},
        {"id": "model_diagnostics", "title": "Model Diagnostics", "anchor": "model-diagnostics"},
        {"id": "cross_period_checks", "title": "Cross-Period Checks", "anchor": "cross-period-checks"}
      ],
      "expanders": [
        {"id": "how_to_read_granger", "title": "How should I read the Granger chart?"}
      ]
    },
    "strategy": {
      "headline": "The rule is a search-found defensive/timing overlay, not a forecasting signal",
      "sections": [
        {"id": "rule_summary", "title": "Rule Summary", "anchor": "rule-summary"},
        {"id": "how_signal_is_generated", "title": "How the Signal is Generated", "anchor": "how-the-signal-is-generated"},
        {"id": "tradeoff", "title": "Tradeoff and Fragility", "anchor": "tradeoff"},
        {"id": "how_to_read_trade_log", "title": "How to Read the Trade Log", "anchor": "how-to-read-trade-log"}
      ],
      "expanders": [
        {"id": "why_low_confidence", "title": "Why is confidence low?"}
      ]
    },
    "methodology": {
      "headline": "Methodology emphasizes searched-rule disclosure, release-lag discipline, and the reverse-causality verdict",
      "sections": [
        {"id": "data_sources", "title": "Data Sources", "anchor": "data-sources"},
        {"id": "model_suite", "title": "Model Suite", "anchor": "model-suite"},
        {"id": "limitations", "title": "Limitations", "anchor": "limitations"}
      ],
      "expanders": [
        {"id": "why_not_causal", "title": "Why is this not a causal claim?"}
      ]
    }
  },
  "chart_refs": [
    "hero",
    "equity_curves",
    "drawdown",
    "correlation_heatmap",
    "ccf_prewhitened",
    "granger_f_by_lag",
    "hmm_regime_probs",
    "local_projections",
    "quantile_coef",
    "transfer_entropy",
    "regime_stats",
    "tournament_scatter",
    "tournament_sharpe_dist",
    "rolling_correlation",
    "structural_break",
    "subperiod_sharpe",
    "history_zoom_dotcom",
    "history_zoom_gfc",
    "history_zoom_covid",
    "history_zoom_inflation_2022"
  ],
  "glossary_terms": [
    "Buy-and-hold",
    "Counter-cyclical",
    "Pro-cyclical",
    "Drawdown",
    "Forward return",
    "Granger causality",
    "Hidden Markov Model (HMM)",
    "In-sample / Out-of-sample",
    "Local projection",
    "Money supply (M2)",
    "Money-growth acceleration",
    "Quantile regression",
    "Regime",
    "Sharpe ratio",
    "Transfer entropy",
    "Tournament",
    "Walk-forward validation"
  ],
  "direction_asserted": "procyclical",
  "historical_episodes_referenced": [
    {"episode_slug": "covid", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_covid chart to show the 2020-21 money surge alongside the SPY crash-and-recovery — money and the market moved together, not money ahead.", "selection_rationale": "coincident", "prose_ref": "Story / What History Shows"},
    {"episode_slug": "gfc", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_gfc chart to show that M2 YoY growth did not lead the equity bear market — a failure case for any forward-leading claim.", "selection_rationale": "failure_case", "prose_ref": "Story / What History Shows"},
    {"episode_slug": "inflation_2022", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_inflation_2022 chart to show the first-ever M2 YoY contraction during a Fed-tightening drawdown — a second failure case for forward causality.", "selection_rationale": "failure_case", "prose_ref": "Story / What History Shows"},
    {"episode_slug": "dotcom", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_dotcom chart as a confirmer for continuity across the portal's standard episode set.", "selection_rationale": "confirmer", "prose_ref": "Story / What History Shows"}
  ],
  "selection_rationale_note": "RES-20 lagging-pair variant: the Toda-Yamamoto Granger verdict for this pair is reverse-only (M2 YoY does NOT Granger-cause SPY at any lag 1-12; SPY -> M2 YoY is significant at lags 1,2,3,4,5,8 — see results/m2sl_yoy_spy/core_models_20260619/granger_causality.csv). A long_lead episode is therefore structurally impossible and is NOT invented. The triad is COVID=coincident, GFC + 2022=failure_case, Dot-Com=confirmer.",
  "status_labels_used": ["Available", "Validated"]
}
---

> Direction asserted: **pro-cyclical** (the winning rule's orientation), but read the causality section first — this is **not** evidence that M2 leads equities.

## Story

### Headline Findings

Out-of-sample (OOS) — tested on data not used to pick the rule — is the right lens here. The winning rule earns a Sharpe ratio — return per unit of volatility — of 1.69 versus 0.90 for buy-and-hold (buy-and-hold means staying invested in SPY throughout). Its maximum drawdown — the largest peak-to-trough loss — is -4.0% (400 basis points) versus -23.9% for buy-and-hold, and annualized return is also higher, 17.6% versus 14.9%.

Those numbers look strong. Before trusting them, two honest framings matter, and they shape everything below: the signal is about whether money growth is **speeding up or slowing down**, not whether it is high or low; and the statistical tests say money does **not** lead the market — if anything, the market leads money.

### The Honest Headline: Causality Runs in Reverse

The most important finding is a negative one. Granger causality — a test of whether the past values of one series help forecast another — shows **no forward signal at all**: M2 year-over-year (YoY) growth — this month's money stock versus the same month a year ago — does not Granger-cause SPY at any lag from 1 to 12 months (every p-value is above 0.43). The reverse is what is significant: SPY Granger-causes M2 YoY growth at lags 1, 2, 3, 4, 5, and 8 months.

**What this means:** the stock market moves first, and the broad money aggregate responds afterward. M2 behaves as a coincident or lagging series with respect to equities, not a leading one. So this pair is **not** evidence that watching the money supply lets you forecast stocks. The trading edge below does not come from a forward-causal relationship; it comes from a search-found pattern in the *acceleration* of money growth, and it should be read as a timing overlay, not a forecast.

### Acceleration, Not Level

The tradable signal is **money-growth acceleration** — the month-to-month change in M2's YoY growth rate (a "second-derivative" transform), not the YoY level itself. In plain terms, the rule asks "is money growth speeding up or slowing down?" rather than "is money growth high or low?" The first question beat the second in the strategy search.

The credible economic story is a hypothesis, not a fact: when money growth is accelerating, liquidity and credit conditions are easing, which can act as a risk-on tailwind for equities over the following couple of months. That is the pro-cyclical — moving with the market cycle — mechanism the search favored. It is plausible, but the reverse-causality verdict above means we cannot claim it as a proven forecasting channel.

<!-- expander: Why acceleration, not the level? -->
The level of money growth and the change in money growth tell different stories. The level quartiles (see the Evidence page) actually show that the *highest* money-growth regime is the *riskiest* for stocks concurrently — high money growth often coincides with inflation and tightening worries. The acceleration transform sidesteps that by asking about direction of travel: an economy where money growth is re-accelerating off a low base looks different from one where fast growth is rolling over. The search found the acceleration framing tradable; it did not find the level framing tradable in the same way. We report them as two separate stories on purpose.
<!-- /expander -->

### What History Shows

The pair-specific history zoom charts make the caveats tangible, and they are chosen to teach the lagging character honestly. During the COVID-19 shock, M2 YoY growth surged toward 27% while SPY crashed and then recovered — money and the market moved together in the same window, a coincident episode rather than money leading. During the Global Financial Crisis (GFC), M2 YoY growth gave no advance warning of the equity bear market — a failure case for any forward-leading claim. During the 2022 inflation shock, M2 YoY growth fell below 0% for the first time in the modern record while the Fed tightened and equities fell — a second failure case, and the vivid first-ever contraction episode. The Dot-Com window is included as a confirmer for continuity across the portal's standard episode set, not as a validation case.

## Evidence

### Lead-Lag Tests (Reverse-Only)

Read the Granger chart first, because it is the spine of the honest story. The dark-blue bars — SPY leading M2 YoY growth — clear the dashed 5% critical line at lags 1, 2, 3, 4, 5, and 8 months. The pale-blue bars — M2 YoY growth leading SPY — clear it at **no** lag. **In plain English:** the market's past helps predict the money aggregate, but the money aggregate's past does not help predict the market.

Pre-whitened cross-correlation (CCF) — correlation after removing each series' own autocorrelation — and forward local projections (below) agree: there is no clean forward lead from money growth to equities.

<!-- expander: How should I read the Granger chart? -->
Look at which bars cross the dashed line. The dashed line is the threshold for 5% statistical significance. The dark-blue bars (SPY leading M2) cross it at the short lags; the pale-blue bars (M2 leading SPY) stay under it everywhere. A leading indicator would have the pale-blue bars crossing the line — they do not. That is why we describe M2 as coincident/lagging and the trading rule as search-found rather than forecast-based.
<!-- /expander -->

### Level Quartiles: High-Money-Growth Is the Riskiest Regime

Quartile analysis — sorting months into four buckets from low to high signal values — uses the money-growth LEVEL here, and it is descriptive (concurrent), not a trading rule. The result is the opposite of "more money is better for stocks": Sharpe FALLS from Q1 (lowest M2 YoY) at 1.06 to Q4 (highest M2 YoY) at 0.53, and Q4's max drawdown is -47%. The highest-money-growth regime is the riskiest for equities concurrently — consistent with the idea that very fast money growth coincides with inflation and tightening risk. This is a separate story from the acceleration winner, and we keep them separate on purpose.

### Model Diagnostics

Local projection (LP) — an impulse-response regression run separately at each horizon — shows no statistically significant forward coefficient at any of 1, 3, 6, or 12 months (minimum p ≈ 0.62); the confidence bands include zero throughout. Transfer entropy (TE) — a nonlinear information-flow check — tells the same reverse-only story: the forward direction is not significant (p ≈ 0.20), while only the reverse direction is (p ≈ 0.03). Quantile regression — separate regressions for weak, normal, and strong return outcomes — is most negative in the lowest return quantiles, again not the profile of a clean forward predictor.

Hidden Markov Model (HMM) — a model that assigns each month to latent regimes — is useful here as a backdrop map, not as the winning signal. Its high-variance regime probability pins near 1.0 through the 2020-21 money surge, which is what we would expect; it explains the monetary environment but does not rescue the statistical fragility of the strategy.

### Cross-Period Checks

The rolling correlation — a moving 24-month relationship estimate — is only moderately stable: its sign agrees with the full-sample value about half the time (sign stability 0.50), so the relationship is not steady enough to lean on. The structural-break test — a search for one large relationship change — points to October 2011 but does **not** reject stability at conventional levels (residual-bootstrap p = 0.28). Subperiod Sharpe confirms how narrow the evidence is: only COVID 2020 falls inside the 2018-onward OOS window and is evaluable (Sharpe ≈ 2.4); the Dot-Com, GFC, and China 2015 episodes all predate the OOS split and are marked insufficient data. A single evaluable episode is exactly why durability is rated only "conditionally durable."

## Strategy

### Rule Summary

The selected strategy is Long/Cash — hold SPY when the lagged signal is favorable, otherwise hold cash. The signal is M2 money-growth acceleration (the month-to-month change in M2's YoY growth rate). The threshold is greater than 0.0523 percentage points, and the rule uses a 2-month lag (L2). In plain terms: if money growth was accelerating above its historical-median pace two months earlier, the strategy owns SPY; otherwise it steps aside.

### How the Signal is Generated

First, the data process reads the Federal Reserve's monthly M2 money-stock release (FRED series M2SL) and computes its year-over-year growth — this month's money stock versus the same month a year ago. Second, it takes the change in that growth rate from one month to the next; this is the "acceleration" — is money growth speeding up or slowing down? Third, it compares the value from two months earlier (respecting the publication lag, so no future information is used) against the historical-median threshold and converts that comparison into a SPY-or-cash position.

This is intentionally simple. It does not forecast inflation, model the Fed's reaction function, or claim that money drives stocks. It asks whether one summary of the liquidity backdrop has historically lined up with a better or worse SPY allocation — and, as the Evidence page is careful to say, the statistical tests do not establish that money leads the market.

### Tradeoff and Fragility

The result is best understood as a defensive/timing overlay rather than a validated forecaster. The OOS numbers are favorable — Sharpe 1.69 versus 0.90, max drawdown -4.0% (400 basis points) versus -23.9%, annualized return 17.6% versus 14.9% — but several fragility flags must travel with them:

- **Bootstrap p-value** — a resampling test for whether the result could plausibly arise by chance — is 0.025. That clears the 5% bar, but the rule was selected from a large search, so this is a search-conditioned result, not a fresh confirmation.
- The rule is marked **found_in_search**, meaning it was chosen as the best of many combinations and has **not** been confirmed on an untouched final-exam window.
- **Confidence is LOW** and durability is only **conditionally durable** — the OOS window (2018-2026) is dominated by the 2020 money surge and the 2022 contraction, a single unusual monetary regime, and COVID is the only evaluable stress episode.
- The drawdown win (-4.0% versus -23.9%) is real but **episode-shaped** — it leans heavily on stepping aside during 2022.

<!-- expander: Why is confidence low? -->
Three reasons stack up. First, there is no forward-causal evidence — the Granger, local-projection, and transfer-entropy tests all say money does not lead stocks. Second, the winner is the best of thousands of searched combinations, and a good-looking maximum can appear by chance in a large search; the bootstrap (p = 0.025) helps quantify but does not eliminate that risk, and there has been no final exam on fresh data. Third, the out-of-sample window is short and dominated by one extraordinary monetary regime (2020-2022), so we cannot tell how the rule behaves in ordinary conditions. The recommended next step is to freeze the rule and test it on an untouched window.
<!-- /expander -->

### How to Read the Trade Log

The trade log is a simulated backtest record, not an execution record of real trades. Two files are available: a broker-style log (user-friendly, one row per exposure change) and a position log (for researcher debugging). The key columns in the broker-style log are the date, the action (move to SPY or move to cash), and the resulting exposure. For example, when lagged money-growth acceleration crossed back above its median threshold, the log records a switch from cash to 100% SPY on that month's decision date. Use the log to audit when and why the rule changed exposure; do not treat it as broker-confirmed fills.

## Methodology

### Data Sources

The indicator is M2 money supply from the Federal Reserve (FRED series M2SL), pulled from the live FRED application programming interface (API) at the current vintage (1959 onward, aligned to SPY from 1993). M2 is a seasonally adjusted, heavily **revised** series; the project's Data Master snapshot is a stale vintage running about 0.5% above current FRED at recent dates, so FRED is treated as ground truth. SPY is the target equity exchange-traded fund (ETF), a listed fund used as the investable proxy for the United States equity market.

The M2 **level** is non-stationary (an augmented Dickey-Fuller test gives p ≈ 0.99) and is therefore **excluded** from the signal set — only stationary growth and transform series (YoY growth, month-over-month growth, 3- and 6-month growth, the acceleration transform, and a rolling z-score) are used. Release-lag discipline matters: the monthly H.6 release publishes the prior month around the fourth Tuesday, so the rule uses at least a one-month real-time floor and the selected two-month lag never peeks at unpublished data.

### Model Suite

The evidence suite includes Pearson correlation — a linear association measure — pre-whitened CCF, Toda-Yamamoto Granger causality (both directions), local projections with HC3/HAC robust standard errors, a 2-state HMM regime map, quantile regression, transfer entropy, rolling correlation, a Quandt-Andrews structural-break test, and tournament validation across 4,720 combinations (3,369 valid). In-sample calibration of the threshold ends before the 2018 OOS split; OOS runs 2018-01 through 2026-04 (100 months).

Walk-forward validation — repeatedly testing rules after rolling through time — is not the same as a final exam. This pair still needs a frozen-rule confirmation window to move from found_in_search to a stronger evidence status.

### Limitations

This is not a causal claim. A causal claim would assert that changes in money growth directly make equities rise or fall. The charts show prediction and association at best, and in the forward direction they show no predictive content at all. The reverse-causality verdict (SPY leading M2) is the single most important limitation: it means the rule cannot be defended as a forecasting signal, only as a search-found timing overlay whose edge is concentrated in one monetary regime.

<!-- expander: Why is this not a causal claim? -->
The rule was selected because it performed best in a search, not because it was identified through a natural experiment or an instrument that isolates money growth from the rest of the economy. On top of that, the formal lead-lag tests run the wrong way for a causal forecasting story: the market Granger-causes the money aggregate, not the other way around. The mechanism we describe (accelerating money as easing liquidity) is a plausible interpretation layered on top of empirical association, and it remains a hypothesis.
<!-- /expander -->
