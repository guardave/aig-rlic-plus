---
{
  "pair_id": "ism_services_spy",
  "narrative_version": "1.0.0",
  "generated_at": "2026-06-18T00:00:00Z",
  "pages": {
    "story": {
      "headline": "OOS Sharpe 1.54 with low confidence -- ISM Services PMI is a contrarian drawdown overlay, not a leading SPY signal",
      "plain_english": "Services sentiment usually moves with the economy and stocks, but the searched rule buys after unusually weak readings. That can protect drawdowns, but the evidence says stocks lead the survey more than the survey leads stocks.",
      "sections": [
        {"id": "headline_findings", "title": "Headline Findings", "anchor": "headline-findings"},
        {"id": "natural_prior_vs_winner", "title": "Natural Prior vs Tournament Winner", "anchor": "natural-prior-vs-tournament-winner"},
        {"id": "why_not_a_leading_signal", "title": "Why This Is Not a Leading Signal", "anchor": "why-this-is-not-a-leading-signal"},
        {"id": "historical_episodes", "title": "Historical Episodes", "anchor": "historical-episodes"}
      ],
      "expanders": [
        {"id": "what_is_pmi", "title": "What is a diffusion index?"},
        {"id": "why_reverse_causality_matters", "title": "Why does reverse causality matter?"}
      ]
    },
    "evidence": {
      "headline": "Reverse causality dominates: SPY predicts the survey at lags 1-12; the survey predicts SPY at no tested lag.",
      "plain_english": "The statistical tests do not show ISM Services PMI getting ahead of stocks. They mostly show stocks getting ahead of the survey.",
      "sections": [
        {"id": "causality_first", "title": "Lead With Causality", "anchor": "lead-with-causality"},
        {"id": "method_results", "title": "Method Results", "anchor": "method-results"},
        {"id": "robustness_flags", "title": "Robustness Flags", "anchor": "robustness-flags"}
      ],
      "expanders": []
    },
    "strategy": {
      "headline": "The rule is defensive: annual return falls to 9.8% from 15.1%, while max drawdown improves to -3.8% from -23.9%.",
      "plain_english": "This is a cash-raising overlay. It spends much of the time out of the market and earns its keep by avoiding large drawdowns, not by proving that the survey forecasts stocks.",
      "sections": [
        {"id": "how_signal_generated", "title": "How the Signal is Generated", "anchor": "how-the-signal-is-generated"},
        {"id": "how_signal_translates", "title": "How the Signal Translates to Action", "anchor": "how-the-signal-translates-to-action"},
        {"id": "where_it_adds_value", "title": "Where It Adds Value and Where It Does Not", "anchor": "where-it-adds-value-and-where-it-does-not"},
        {"id": "important_caveats", "title": "Important Caveats", "anchor": "important-caveats"}
      ],
      "expanders": [
        {"id": "what_is_zscore", "title": "What is a rolling z-score?"}
      ]
    },
    "methodology": {
      "headline": "Monthly ISM Services PMI, monthly SPY returns, 1997-07 to 2025-10, with OOS from 2018-10 to 2025-10.",
      "plain_english": "The analysis tests many versions of the signal, many lags, and several statistical methods. The best rule is the result of that search, so it needs a fresh final exam before anyone treats it as validated.",
      "sections": [
        {"id": "data_sources", "title": "Data Sources", "anchor": "data-sources"},
        {"id": "sample_period", "title": "Sample Period", "anchor": "sample-period"},
        {"id": "econometric_methods", "title": "Econometric Methods", "anchor": "econometric-methods"},
        {"id": "validation_status", "title": "Validation Status", "anchor": "validation-status"}
      ],
      "expanders": []
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
    "returns_by_regime",
    "history_zoom_dotcom",
    "history_zoom_gfc",
    "history_zoom_covid",
    "history_zoom_inflation_2022",
    "quantile_coef",
    "rolling_correlation",
    "structural_break",
    "subperiod_sharpe",
    "tournament_scatter",
    "tournament_sharpe_dist",
    "transfer_entropy",
    "walk_forward"
  ],
  "glossary_terms": [
    "Diffusion index",
    "Out-of-sample",
    "Granger causality",
    "Sharpe ratio",
    "Maximum drawdown",
    "Bootstrap p-value",
    "Structural break",
    "Z-score"
  ],
  "direction_asserted": "countercyclical",
  "historical_episodes_referenced": [
    {
      "episode_slug": "dotcom",
      "override_needed": true,
      "override_reason": "Story historical-episodes paragraph uses dot-com as an early-sample context chart, not as evidence for the OOS winner.",
      "selection_rationale": "failure_case",
      "prose_ref": "Story - Historical Episodes"
    },
    {
      "episode_slug": "gfc",
      "override_needed": true,
      "override_reason": "Story historical-episodes paragraph uses the GFC to show PMI stress was coincident with the market crash, not a long lead.",
      "selection_rationale": "confirmer",
      "prose_ref": "Story - Historical Episodes"
    },
    {
      "episode_slug": "covid",
      "override_needed": true,
      "override_reason": "Story historical-episodes paragraph identifies COVID as the concentrated episode behind much of the OOS result.",
      "selection_rationale": "coincident",
      "prose_ref": "Story - Historical Episodes"
    },
    {
      "episode_slug": "inflation_2022",
      "override_needed": true,
      "override_reason": "Story historical-episodes paragraph uses 2022 as a defensive cash-overlay example, not a leading-services signal.",
      "selection_rationale": "failure_case",
      "prose_ref": "Story - Historical Episodes"
    }
  ],
  "status_labels_used": ["Validated"]
}
---

# Portal Narrative: ISM Services PMI x SPY

## Story

### Headline Findings

Institute for Supply Management Services Purchasing Managers' Index (ISM Services PMI) -- a monthly survey score where 50 separates services expansion from contraction -- has a natural procyclical prior for equities: above 50 usually means the services economy is expanding, which should be risk-on for the SPDR S&P 500 ETF Trust (SPY) -- the exchange-traded fund used here as the S&P 500 proxy.

The tournament winner goes the other way. It is countercyclical -- it goes long SPY when services sentiment is unusually weak, specifically when the ISM Services PMI gap to 50 falls below a rolling z-score threshold of -1.0 after a 3-month lag. The plain-English version is "buy after services fear," not "buy because services strength leads stocks."

The result is useful to inspect but easy to oversell. Out-of-sample (OOS) -- tested on data not used as the initial in-sample fit -- Sharpe ratio is 1.54 versus 0.88 for buy-and-hold, and maximum drawdown -- the worst peak-to-trough loss -- improves to -3.8% from -23.9%. But the strategy gives up return: 9.8% annualized versus 15.1% for buy-and-hold.

### Natural Prior vs Tournament Winner

The prior is simple: ISM Services PMI above 50 means expansion, and expansion should usually support SPY. The descriptive quartile charts agree with that prior. The lowest PMI quartile has weak SPY performance, while stronger PMI and stronger 3-month PMI momentum line up with better returns.

That makes the winner more suspicious, not less. Its mechanism is only a hypothesis: depressed services sentiment may mark cyclical troughs or "maximum pessimism" moments near which forward equity returns improve. That is plausible mean reversion, but the evidence here does not establish it as a stable law.

### Why This Is Not a Leading Signal

Granger causality -- a test of whether one series' past values help predict another series beyond its own past -- points in the wrong direction for a forecasting story. SPY predicts the ISM Services survey at lags 1 through 12, while ISM Services PMI predicts SPY at no tested lag.

The honest reading is that ISM Services PMI behaves as a coincident or lagging reflection of conditions equities already price. Any tradable edge is therefore suspect, likely regime-driven, and not evidence that the survey leads the stock market.

### Historical Episodes

The Global Financial Crisis (GFC) -- the 2007-2009 credit and equity collapse -- shows the survey falling with the market, not providing a clean long lead. Coronavirus disease 2019 (COVID-19) -- the 2020 pandemic shock -- is the episode that helps explain the OOS result: services sentiment collapsed and then recovered quickly, and the defensive rule avoided much of the drawdown.

The dot-com episode mostly sits before the OOS test window, and the 2022 inflation shock is better read as a cash-overlay example than as proof of services leadership. These episodes support the low-confidence story: the rule can manage drawdown in certain shocks, but it is not a general leading indicator.

<!-- expander: What is a diffusion index? -->
Diffusion index means the survey records breadth, not dollars of output. A value above 50 means more respondents report expansion than contraction; a value below 50 means contraction is more common.
<!-- /expander -->

<!-- expander: Why does reverse causality matter? -->
Reverse causality matters because it changes the interpretation. If SPY moves first and the survey follows, the survey may summarize investor-visible conditions after the market has already reacted.
<!-- /expander -->

## Evidence

### Lead With Causality

Institute for Supply Management Services Purchasing Managers' Index (ISM Services PMI) -- a monthly services-sector survey diffusion index -- does not pass the main lead-lag test against SPDR S&P 500 ETF Trust (SPY) -- the S&P 500 proxy used in this project.

Toda-Yamamoto Granger causality -- a Granger causality variant designed to be more robust when time series may be integrated -- is the headline result. Forward direction, ISM Services PMI to SPY, is not significant at lags 1-12. Reverse direction, SPY to ISM Services PMI, is significant at every lag from 1 through 12.

### Method Results

Local projections -- regressions that estimate the response of one variable over future horizons -- tell the same story. Forward ISM-to-SPY responses are not statistically distinguishable from zero; reverse SPY-to-ISM responses are significant at 1, 3, 6, and 12 months.

Transfer entropy -- a nonlinear information-flow measure -- is also reverse-heavy. ISM-to-SPY is marginal with permutation p-value 0.064, while SPY-to-ISM is stronger with p-value 0.002.

Quantile regression -- a method that estimates relationships at different parts of the return distribution -- is mixed rather than clean. Some lower-tail coefficients are positive and some median or upper-tail coefficients are negative. That sign instability does not support a simple economic channel.

### Robustness Flags

Bootstrap p-value -- a resampling estimate of how often a result could appear by chance -- is 0.073, so the winner is not significant at the 5% level. Structural break -- a detected change in the statistical relationship over time -- is flagged at 2009-03.

The largest warning is the in-sample/out-of-sample inversion. In-sample (IS) -- the period used before the final OOS split -- Sharpe is -0.11, while OOS Sharpe is 1.54. A negative IS Sharpe with a strong OOS Sharpe is a red flag for fragility, not a strength.

## Strategy

### How the Signal is Generated

Institute for Supply Management Services Purchasing Managers' Index (ISM Services PMI) -- a survey diffusion index where 50 is neutral -- is transformed into a gap-to-50 signal: PMI minus 50. The rule then compares that gap with a rolling z-score -- the number of standard deviations a value is from its recent average -- over a 120-month lookback window.

The selected trigger is "less than -1.0 z-score," applied with a 3-month lead convention. In plain English: if services sentiment is unusually weak relative to its own history, the searched rule prepares to own SPDR S&P 500 ETF Trust (SPY) after the lag; otherwise it sits in cash.

### How the Signal Translates to Action

The strategy is Long/Cash -- long SPY when the condition is active, cash when it is not. It is not a short strategy, and it is not a continuous allocation rule. It is a sparse overlay: OOS position changes total 17, and average exposure is low.

The expected economic direction was procyclical -- stronger services activity should support equities. The observed winner is countercyclical -- weaker services sentiment triggers equity exposure. That contradiction must remain visible anywhere the strategy is described.

### Where It Adds Value and Where It Does Not

The strategy objective is minimum maximum drawdown (min MDD) -- reducing the worst peak-to-trough loss. It succeeds on that metric in OOS: -3.8% max drawdown versus -23.9% for buy-and-hold.

It does not maximize total return. Annualized OOS return is 9.8% versus 15.1% for buy-and-hold. The strategy gives up upside to reduce drawdown, and the performance appears episode-concentrated.

### Important Caveats

Out-of-sample (OOS) -- the test period from 2018-10-31 to 2025-10-31 -- is still part of the tournament search result, not a fresh final exam. Evidence status is found_in_search. Confidence is low.

The bottom line: this is an interesting drawdown-management overlay, but not evidence that ISM Services PMI leads the S&P 500.

<!-- expander: What is a rolling z-score? -->
A rolling z-score compares today's value with its own recent history. A value below -1.0 means the signal is more than one recent standard deviation below normal.
<!-- /expander -->

## Methodology

### Data Sources

Institute for Supply Management Services Purchasing Managers' Index (ISM Services PMI) -- a monthly services survey diffusion index -- comes from the project Data Master workbook because the relevant ISM series is not pulled from FRED in this project. SPDR S&P 500 ETF Trust (SPY) -- the target equity ETF -- comes from Yahoo Finance adjusted prices.

The monthly panel runs from 1997-07-31 to 2025-10-31. The daily panel carries the most recent monthly survey value forward from an assumed release date, but the tournament described here is monthly.

### Sample Period

Out-of-sample (OOS) -- the evaluation window not used for initial fitting -- runs from 2018-10-31 to 2025-10-31 with 85 monthly observations. In-sample (IS) -- the earlier model-selection period -- ends on 2018-09-30.

The selected signal is ISM Services PMI gap to 50, the threshold rule is less than a rolling z-score of -1.0, the strategy is P1 Long/Cash, and the lead is 3 months.

### Econometric Methods

The evidence bundle includes correlation analysis -- linear association across forward return horizons; cross-correlation function (CCF) -- lead/lag correlation after pre-whitening; Granger causality -- predictive timing tests; local projections -- horizon-by-horizon response regressions; transfer entropy -- nonlinear information-flow testing; hidden Markov model (HMM) -- latent regime classification; quantile regression -- return-distribution sensitivity; and structural-break testing -- parameter instability detection.

The central methodological finding is not subtle: lead-lag methods point backward from SPY to the survey, not forward from the survey to SPY.

### Validation Status

Bootstrap p-value -- the resampled chance threshold for the searched winner -- is 0.073, above the 5% cutoff. Structural break is flagged at 2009-03, and cross-period durability is episode_concentrated.

A final-exam test would freeze the rule exactly as selected here and evaluate it on new post-2025 data or on a confirmation window not used in the tournament. Until then, this pair should remain low confidence.
