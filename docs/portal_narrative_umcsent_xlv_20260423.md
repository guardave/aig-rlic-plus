---
pair_id: umcsent_xlv
narrative_version: 1.1.0
generated_at: "2026-06-19T09:30:00Z"
direction_asserted: procyclical
headline_template: A
chart_refs:
  - hero
  - correlations
  - ccf
  - regime_stats
  - equity_curves
  - drawdown
  - walk_forward
  - tournament_scatter
  - rolling_sharpe
  - signal_dist
glossary_terms:
  - University of Michigan Consumer Sentiment
  - Out-of-sample
  - Sharpe ratio
  - Z-score
  - Max drawdown
  - Calmar ratio
pages:
  story:
    headline: "Sharpe 1.16 over 2019-2025 OOS -- consumer-sentiment momentum as a 6-month XLV timing signal"
    sections:
      - id: story_headline
        anchor: story-headline
        title: "Sharpe 1.16 over 2019-2025 OOS -- consumer-sentiment momentum as a 6-month XLV timing signal"
      - id: story_mechanism
        anchor: story-mechanism
        title: "Why Sentiment Momentum Might Lead Health Care"
      - id: story_caveats
        anchor: story-caveats
        title: "What Not to Over-Claim"
    expanders: []
  evidence:
    headline: "The evidence supports a positive but fragile sentiment-to-XLV timing relationship"
    sections:
      - id: evidence_summary
        anchor: evidence-summary
        title: "Evidence Summary"
      - id: evidence_fragility
        anchor: evidence-fragility
        title: "Fragility and Method Sensitivity"
    expanders: []
  strategy:
    headline: "The corrected winner is UMCSENT 3-month momentum, rolling z-score > +1.0, 6-month lead"
    sections:
      - id: strategy_rule
        anchor: strategy-rule
        title: "Corrected Winning Rule"
      - id: strategy_metrics
        anchor: strategy-metrics
        title: "Corrected Performance"
      - id: strategy_caveats
        anchor: strategy-caveats
        title: "Execution Caveats"
    expanders: []
  methodology:
    headline: "The indicator-level evidence is unchanged; only the winner description was refreshed"
    sections:
      - id: methodology_scope
        anchor: methodology-scope
        title: "Scope of This Refresh"
      - id: methodology_sources
        anchor: methodology-sources
        title: "Authoritative Sources"
    expanders: []
---

# Portal Narrative: umcsent_xlv

## Story

### Sharpe 1.16 over 2019-2025 OOS -- consumer-sentiment momentum as a 6-month XLV timing signal

The corrected UMCSENT x XLV finding is not about the level of consumer confidence or its year-over-year change. It is about **University of Michigan Consumer Sentiment (UMCSENT) -- a monthly survey of household confidence -- 3-month momentum**, meaning the change in the sentiment index over the prior three months.

The working hypothesis is procyclical: when household confidence is improving quickly, Health Care Select Sector SPDR Fund (XLV) tends to do better over the next several months. The corrected winner acts on that hypothesis with a 6-month lead, so the rule uses sentiment momentum observed six months earlier rather than the current month's reading.

This should be read as a timing hypothesis, not a law. Health care is partly defensive, and the existing indicator-level evidence is positive but noisy. The refreshed winner says that improving sentiment momentum was useful for XLV exposure in this sample; it does not prove that consumers mechanically drive health-care stocks.

### Why Sentiment Momentum Might Lead Health Care

The economic channel is plausible but indirect. Rising consumer-sentiment momentum may mark a broader improvement in household risk appetite, labor-market confidence, and willingness to absorb equity exposure. XLV can participate in that risk-on environment even though it is less cyclical than many equity sectors.

The 6-month lead is the key interpretation point. The strategy is not reacting to today's survey print. It tests whether a sustained improvement in sentiment momentum has information about XLV several months ahead.

### What Not to Over-Claim

The evidence should not be described as a clean causal chain from sentiment to XLV. The existing lead-lag and regime evidence was not regenerated in this winner refresh and remains the proper basis for the broader indicator discussion. The refreshed task only corrects the tournament winner and the performance story tied to that winner.

## Evidence

### Evidence Summary

The existing evidence supports a positive relationship between sentiment improvement and future XLV performance, but the signal is noisy. Cross-correlation and regime-style diagnostics remain relevant as indicator-level support. They should be presented as context for why the tournament searched sentiment-based rules, not as fresh confirmation of the corrected winner.

Out-of-sample (OOS) -- tested on data not used to pick the rule -- performance for the corrected winner runs from 2019-04-30 through 2025-12-31. Over that period, the winning rule delivered Sharpe 1.16. Sharpe ratio -- return earned per unit of volatility -- is the primary risk-adjusted performance measure used here.

### Fragility and Method Sensitivity

The strongest result is the strategy result, not a broad claim that every UMCSENT transformation predicts XLV. The winner uses one specific transformed signal: UMCSENT 3-month momentum (`S3_mom` / `umcsent_mom`). Other signal definitions can tell a weaker or different story.

The indicator-level tests should remain visible because they discipline the interpretation. If the portal presents the winner without the noisy evidence context, readers may infer more certainty than the evidence supports.

## Strategy

### Corrected Winning Rule

The corrected tournament winner is:

| Field | Corrected value |
|---|---|
| Signal | UMCSENT 3-month momentum (`S3_mom` / `umcsent_mom`) |
| Threshold | rolling z-score > +1.0 |
| Lead | 6 months |
| Strategy | P1 Long/Cash |
| Target | XLV |

Z-score -- how many standard deviations a value is above or below its recent average -- is the threshold language here. The rule goes long XLV when the 6-month-lagged UMCSENT 3-month momentum is more than one standard deviation above its rolling average; otherwise it sits in cash.

### Corrected Performance

The corrected OOS performance metrics are:

| Metric | Corrected value |
|---|---:|
| OOS Sharpe | 1.16 |
| OOS annual return | +7.95% |
| Max drawdown | -0.7% |
| Calmar | 11.3 |
| Sortino | 1.61 |
| Annual volatility | 6.9% |
| Win rate | 16% |
| Annual turnover | 3.29 |

Max drawdown -- the worst peak-to-trough loss over the test window -- is the standout metric: the corrected winner reduced OOS max drawdown to -0.7%, versus XLV buy-and-hold max drawdown of -15.6% in the same OOS window. Calmar ratio -- annual return divided by max drawdown risk -- is therefore high at 11.3.

The result is a drawdown-control story more than a return-maximization story. The strategy's +7.95% OOS annual return trails the XLV buy-and-hold annual return in `winner_summary.json`, but it achieves that return with much lower drawdown.

### Execution Caveats

This is a monthly, medium-frequency signal. The 6-month lead makes it slow by design, so it should not be framed as a tactical response to fast shocks. The low 16% win rate also means most months are not "signal months"; the value comes from a few periods when the rule materially changes exposure.

Turnover of 3.29 per year is not extreme, but implementation costs still matter. The reported figures use the project cost assumptions in the corrected winner artifacts.

## Methodology

### Scope of This Refresh

This refresh corrects the winner-specific narrative only. It states the corrected UMCSENT 3-month momentum / rolling z-score > +1.0 winner and the corrected performance numbers: Sharpe 1.16, OOS annual return +7.95%, max drawdown -0.7%, and Calmar 11.3.

The broader indicator-level evidence was not rerun for this handoff. It remains valid as previously produced and should be referenced as context, not rewritten as if it were newly estimated.

### Authoritative Sources

The authoritative winner facts are Evan's handoff at `_pws/lead-lesandro/umcsent_refresh/evan_handoff.md` and `results/umcsent_xlv/winner_summary.json`. Those artifacts identify the ground-truth tournament row as row 777 in `results/umcsent_xlv/tournament_results_20260420.csv`.
