---
{
  "pair_id": "petrol_inv_spy",
  "narrative_version": "1.0.0",
  "generated_at": "2026-06-17T00:00:00Z",
  "pages": {
    "story": {
      "headline": "Sharpe 1.48 OOS, drawdown -6.3%: petroleum inventories look procyclical, but the evidence is low-confidence",
      "sections": [
        {"id": "headline_findings", "title": "Headline Findings", "anchor": "headline-findings"},
        {"id": "direction_reconciliation", "title": "Direction Reconciliation", "anchor": "direction-reconciliation"},
        {"id": "what_history_shows", "title": "What History Shows", "anchor": "what-history-shows"}
      ],
      "expanders": [
        {"id": "why_inventory_direction_is_tricky", "title": "Why is the inventory direction tricky?"}
      ]
    },
    "evidence": {
      "headline": "Evidence is supportive on direction, weaker on timing and statistical certainty",
      "sections": [
        {"id": "quartile_gradient", "title": "Quartile Gradient", "anchor": "quartile-gradient"},
        {"id": "lead_lag_tests", "title": "Lead-Lag Tests", "anchor": "lead-lag-tests"},
        {"id": "model_diagnostics", "title": "Model Diagnostics", "anchor": "model-diagnostics"},
        {"id": "cross_period_checks", "title": "Cross-Period Checks", "anchor": "cross-period-checks"}
      ],
      "expanders": [
        {"id": "how_to_read_granger", "title": "How should I read the Granger chart?"}
      ]
    },
    "strategy": {
      "headline": "The rule is a defensive overlay, not a return maximizer",
      "sections": [
        {"id": "rule_summary", "title": "Rule Summary", "anchor": "rule-summary"},
        {"id": "how_signal_is_generated", "title": "How the Signal is Generated", "anchor": "how-the-signal-is-generated"},
        {"id": "tradeoff", "title": "Tradeoff", "anchor": "tradeoff"},
        {"id": "how_to_read_trade_log", "title": "How to Read the Trade Log", "anchor": "how-to-read-trade-log"}
      ],
      "expanders": [
        {"id": "why_low_confidence", "title": "Why is confidence low?"}
      ]
    },
    "methodology": {
      "headline": "Methodology emphasizes searched-rule disclosure and release-lag discipline",
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
    "Drawdown",
    "Forward return",
    "Granger causality",
    "Hidden Markov Model (HMM)",
    "In-sample / Out-of-sample",
    "Local projection",
    "Quantile regression",
    "Regime",
    "Sharpe ratio",
    "Transfer entropy",
    "Tournament",
    "Walk-forward validation"
  ],
  "direction_asserted": "procyclical",
  "historical_episodes_referenced": [
    {"episode_slug": "dotcom", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_dotcom chart to compare petroleum-stock changes and SPY during the Dot-Com window.", "selection_rationale": "long_lead", "prose_ref": "Story / What History Shows"},
    {"episode_slug": "gfc", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_gfc chart to show the counter-cyclical prior in the Global Financial Crisis.", "selection_rationale": "failure_case", "prose_ref": "Story / What History Shows"},
    {"episode_slug": "covid", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_covid chart to show the abrupt demand-shock inventory build.", "selection_rationale": "coincident", "prose_ref": "Story / What History Shows"},
    {"episode_slug": "inflation_2022", "override_needed": true, "override_reason": "Story history section uses the pair-specific history_zoom_inflation_2022 chart as a confirmer for the defensive overlay in the rate-shock period.", "selection_rationale": "confirmer", "prose_ref": "Story / What History Shows"}
  ],
  "status_labels_used": ["Available", "Validated"]
}
---

## Story

### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- is the right lens here. The winning petroleum-inventory rule earns a Sharpe ratio -- return per unit of volatility -- of 1.48 versus 0.93 for buy-and-hold (buy-and-hold means staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- is -6.3% versus -23.9% for buy-and-hold. That sounds useful, but it is not a clean alpha story: annualized return is lower, 9.8% versus 15.2%.

The natural prior is counter-cyclical -- inventories building when demand is weak, which is usually bad for equities. That prior is visible in the Global Financial Crisis (GFC) and coronavirus disease 2019 (COVID-19) windows: petroleum stocks rose as fuel demand weakened. The empirical result overturns that prior for the searched rule. The quartile chart shows Q1, the lowest 3-month petroleum-stock change, at Sharpe 0.37 and 6.0% annualized return; Q4, the highest 3-month change, at Sharpe 1.25 and 17.5%. That monotonic gradient corroborates a procyclical -- moving with the equity cycle -- interpretation.

### Direction Reconciliation

The credible economic mechanism is a hypothesis, not a fact. A petroleum inventory build can mean weak demand, but it can also mean robust supply and production availability. In that second state, softer energy-price pressure can help consumers and corporate margins, creating an equity tailwind over the following year. That is the procyclical mechanism the data appear to favor in this pair.

Timing is less precise. Granger causality -- a test of whether past values of one series improve forecasts of another -- is significant at 6, 7, and 8 months for petroleum inventories leading SPY, with no reverse SPY-to-inventory signal. The tournament-selected rule uses L12, a 12-month lead. Treat the evidence as a 6-12 month lead band, not as proof that exactly 12 months is the true horizon.

<!-- expander: Why is the inventory direction tricky? -->
Inventories have two meanings. In a demand collapse, they pile up because consumers and firms are buying less fuel; that is counter-cyclical. In an expansion, they can rise because supply chains and production are strong enough to keep the economy well supplied; that can be procyclical. This pair's charts show both possibilities, which is why the narrative leads with the contradiction rather than hiding it.
<!-- /expander -->

### What History Shows

The pair-specific history zoom charts make the caveat tangible. During the GFC and COVID shock, inventories rose in ways that match the counter-cyclical prior. During the 2022 inflation shock, the Long/Cash strategy mostly stayed defensive and avoided drawdown, but that is a risk-control result rather than a proof of higher long-run return. The Dot-Com chart exists for continuity across the portal's standard episode set; it should be read as contextual background, not as the strongest validation case.

## Evidence

### Quartile Gradient

Quartile analysis -- sorting months into four buckets from low to high signal values -- is the cleanest support for direction. It is simple and descriptive: higher petroleum-stock growth lines up with better subsequent SPY performance. Q1 to Q4 Sharpe rises 0.37 -> 0.83 -> 0.69 -> 1.25, and annualized return rises 6.0% -> 10.4% -> 11.4% -> 17.5%. The Sharpe path is not perfectly linear at Q3, but the endpoint and return gradient both support the procyclical reading.

### Lead-Lag Tests

Pre-whitened cross-correlation (CCF) -- correlation after removing each series' own autocorrelation -- flags lag +6 as significant. Granger causality (GC) -- whether lagged petroleum values improve forecasts of SPY -- flags lags 6-8. These tests agree that there is a medium-horizon lead, but they do not identify the tournament's L12 as uniquely correct.

<!-- expander: How should I read the Granger chart? -->
Read the vermillion bars first. They show petroleum inventories leading SPY. Bars above the dashed critical line are statistically meaningful at the 5% level. The pattern clusters at 6-8 months. The pale-blue reverse bars, SPY leading petroleum inventories, do not clear the line.
<!-- /expander -->

### Model Diagnostics

Local projection (LP) -- an impulse-response regression over several horizons -- does not show statistically significant forward coefficients. Quantile regression -- separate regressions for weak, normal, and strong return outcomes -- is more favorable in the upper return quantiles, which fits the procyclical story better than a crash-hedge story. Transfer entropy (TE) -- a nonlinear information-flow check -- is not significant in either direction.

Hidden Markov Model (HMM) -- a model that assigns each month to latent regimes -- is useful mainly as a regime map, not as the winning signal. The HMM probability chart shows when petroleum-stock changes are in a high-variance regime. It helps explain the backdrop but does not rescue the statistical fragility of the strategy.

### Cross-Period Checks

The rolling correlation -- a moving 24-month relationship estimate -- is only moderately stable. The structural-break test -- a search for one large relationship change -- points to April 2020 but does not reject stability at conventional levels. Subperiod Sharpe confirms that protection is episode-dependent: COVID is strong, the 2022 rate-hike window is flat because the strategy is in cash, and the Global Financial Crisis lacks sufficient daily OOS rows for this strategy-return file.

## Strategy

### Rule Summary

The selected strategy is Long/Cash -- hold SPY when the lagged signal is favorable, otherwise hold cash. The signal is the 3-month percentage change in total petroleum stocks. The threshold is greater than 0.323, and the rule uses a 12-month lag. In plain terms: if petroleum stocks had grown enough one year earlier, the strategy owns SPY; otherwise it steps aside.

### How the Signal is Generated

First, the data process reads Energy Information Administration (EIA) petroleum inventory releases and carries the latest public value forward to the monthly decision date. Second, it computes the 3-month percentage change, which captures whether stocks have recently built or drawn down. Third, it compares the value from 12 months earlier with the 0.323 threshold and converts that comparison into a position.

This is intentionally simple. It does not forecast oil prices, estimate refinery demand, or model the full energy complex. It asks whether a broad physical-stock measure has historically lined up with a better or worse SPY allocation.

### Tradeoff

The result is a defensive overlay. A defensive overlay -- a rule layered on top of an equity position to reduce losses -- is valuable only if the user accepts the cost. Here the cost is clear: out-of-sample (OOS) -- tested on data not used to pick the rule -- annualized return falls to 9.8% from 15.2% for buy-and-hold. The benefit is maximum drawdown -- the largest peak-to-trough loss -- control: -6.3% versus -23.9%. That tradeoff is why the strategy objective is max_sharpe, not max_return.

Bootstrap p-value -- a resampling test for whether the result could plausibly arise by chance -- is 0.099. That is not significant at the 5% level. The rule is also marked found_in_search, meaning it was selected from a broad search rather than confirmed on a fresh final exam. Confidence is low.

<!-- expander: Why is confidence low? -->
The winner came from 5,123 valid searched combinations. A good-looking maximum can appear by chance when the search space is large. The bootstrap result helps quantify that risk: p=0.099 is suggestive but not strong enough for a 5% significance claim.
<!-- /expander -->

### How to Read the Trade Log

The trade log is simulated, not an execution record. Each row records a monthly decision based on the lagged petroleum-stock signal, the threshold, and the resulting SPY or cash exposure. Use it to audit when the rule changed exposure and why; do not treat it as broker-confirmed fills.

## Methodology

### Data Sources

The petroleum indicator is total petroleum stocks from the Energy Information Administration (EIA), identified in project metadata as WTTSTUS1. SPY is the target equity exchange-traded fund (ETF), a listed fund used here as the investable proxy for the United States equity market. Monthly transformations include year-over-year change, 3-month percentage change, 6-month percentage change, trend deviation, and z-score -- a standardized value measured in standard-deviation units.

Release-lag discipline matters. The daily panel carries the latest public petroleum value forward after release, so the strategy does not use future inventory information. The monthly strategy chart uses Evan's saved `strategy_returns_20260617.csv`, not a re-run of the rule.

### Model Suite

The evidence suite includes Pearson correlation -- a linear association measure -- pre-whitened CCF, GC, LP, HMM regimes, quantile regression, TE, rolling correlation, structural-break testing, and tournament validation. In-sample (IS) -- data used to calibrate thresholds -- ends on 2017-07-31. OOS runs from 2017-08-31 through 2025-09-30 with 98 monthly observations.

Walk-forward validation -- repeatedly testing rules after rolling through time -- is not the same as a final exam. This pair still needs a frozen-rule confirmation window to move from found_in_search to a stronger evidence status.

### Limitations

This is not a causal claim. Causal claim means asserting that inventory changes directly make equities rise or fall. The charts show prediction and association, not a structural model of energy supply, demand, inflation, and equity discount rates.

<!-- expander: Why is this not a causal claim? -->
The rule was selected because it performed best in a search. It was not identified through a natural experiment or an instrument that isolates petroleum inventories from the rest of the economy. The mechanism is plausible, but it remains an interpretation layered on top of empirical association.
<!-- /expander -->
