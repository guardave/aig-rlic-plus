---
pair_id: nhs_spy
narrative_version: 1.0.0
generated_at: 2026-07-03
direction_asserted: procyclical
pages: [story, evidence, strategy, methodology]
chart_refs: [hero, regime_stats, correlation_heatmap, granger_f_by_lag, ccf_prewhitened, local_projections, quantile_coef, transfer_entropy, hmm_regime_probs, equity_curves, drawdown, tournament_scatter, tournament_sharpe_dist, rolling_correlation, structural_break, subperiod_sharpe, history_zoom_dotcom, history_zoom_gfc, history_zoom_covid, history_zoom_inflation_2022]
glossary_terms: [sharpe_ratio, drawdown, out_of_sample, granger_causality, hidden_markov_model, seasonal_adjustment, year_over_year, bootstrap_p_value, found_in_search]
---

# Portal Narrative: New Home Sales (NSA) → SPY

**Author:** Research Ray (Mode 2). **Pair:** `nhs_spy`. **Date:** 2026-07-03.

Prose source of truth for the `nhs_spy` portal. Wires into
`app/pair_configs/nhs_spy_config.py`. Evidence status is `found_in_search`, so
all headline performance is labelled "Search-phase OOS Sharpe (no holdout final
exam yet)". Headline numbers come from `results/nhs_spy/winner_summary.json`.

## Story

### Headline Findings

Out-of-sample — tested on data not used to pick the rule — the winning rule earns a Sharpe ratio (return per unit of volatility) of **1.49 versus 0.89** for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown (the largest peak-to-trough loss) improves to **−8.3% from −23.9%**, and annualised return is slightly higher, 15.9% versus 14.8%.

New Home Sales is a classic early-cycle housing indicator: buyers commit before construction begins, so sales sit one step ahead of housing starts, permits, and the employment and consumption they drive. The natural prior is **procyclical** — stronger home-sales demand should coincide with a healthier economy and better equities — and, unlike several macro pairs in this portal, the direction here comes out the way the prior expects.

### A Seasonally-Raw Series, Read Year-over-Year

The one technical wrinkle that shapes everything: the Census new-home-sales series (FRED `HSN1FNSA`) is **not seasonally adjusted**. Raw sales swing predictably every year — a spring selling-season peak, a winter trough — so the raw level and its month-to-month change are dominated by the calendar, not the cycle. Every signal on this page is therefore **deseasonalised**: the headline transform is the year-over-year change (this month versus the same month a year earlier), which cancels a fixed seasonal, backed by a statistically seasonally-adjusted (STL) alternative. We never trade or chart the raw level as a signal.

### The Regime Signal, Not the Raw Number

The winning rule does not trade the year-over-year number directly. It trades a **regime probability**: a Hidden Markov Model reads the home-sales growth series and estimates whether housing demand is in its calm, favourable state or its high-variance, turning-point state. The strategy holds SPY when the favourable-regime signal is on and steps to cash otherwise. In plain terms, it asks "is the housing-demand backdrop healthy right now?" and uses that to time equity exposure.

### The Honest Caveats

Three framings keep this from being oversold, and they shape the Evidence page:

1. **Formal forward causality is weak.** Toda-Yamamoto Granger causality — a test of whether past values of one series help forecast another — finds New Home Sales growth Granger-causes SPY only at a single long lag (11 months); the reverse (SPY → home sales) is significant at short lags (1–2 months), consistent with housing being partly rate- and market-driven. Read the edge as a search-found regime timing overlay, not a validated forward forecast.
2. **The winner is the tail of a large search.** It is the best of 5,297 valid strategy combinations. Its re-shuffle (bootstrap) p-value is **0.071 — above the 5% bar** — and its in-sample Sharpe (0.81) is far below its out-of-sample Sharpe (1.49). Confidence is **low**, and no frozen-rule final exam has been run yet.
3. **The out-of-sample window is short and episode-shaped.** Only the COVID episode falls inside the 2018-onward test window, so durability is only `conditionally_durable`.

### What History Shows

The history-zoom charts make the leading-indicator character tangible. During the **2008-09 GFC**, new home sales collapsed roughly 80% from their 2005 peak and turned down well ahead of the equity bear market — the textbook case for housing as an early-cycle signal. During **COVID**, sales spiked on record-low mortgage rates as SPY recovered. During the **2022-23 rate shock**, sales contracted sharply as mortgage rates jumped — the strong, recent regime that dominates the out-of-sample window. The Dot-Com window is a continuity confirmer for the portal's standard episode set.

## Evidence

### Lead-Lag Tests (Weak Forward)

Toda-Yamamoto Granger: New Home Sales YoY → SPY is significant only at lag 11 months; SPY → New Home Sales is significant at lags 1 and 2. The cross-correlation and local-projection checks corroborate a weak, imprecise forward relationship. This is why confidence is low despite the strong headline Sharpe — the edge rests on the regime signal, not a clean forward-causal channel.

### Regime Quartiles: Cleanly Procyclical

Sorting months by New Home Sales YoY quartile, subsequent SPY Sharpe rises **monotonically** from Q1 (weakest home-sales growth) at 0.20 to Q4 (strongest) at 1.50, and Q1's max drawdown (−51%) is far worse than Q4's (−10%). Stronger housing demand coincides with better, calmer equity returns — the procyclical prior holds cleanly, unlike the money-supply and industrial-production pairs where the level story inverted.

### Model Diagnostics and Cross-Period Checks

Supporting checks (local projections, quantile regression, transfer entropy) tell a consistent weak-forward story. The 24-month rolling correlation shifts sign over time (the concurrent relationship is not stable), and the Quandt-Andrews structural-break test is used to flag any single-date regime shift.

## Strategy

### Rule Summary

Hold SPY when the New Home Sales high-variance-regime probability (2-state HMM on YoY growth) is above its rolling 25th-percentile threshold (60-month window); otherwise hold cash. No signal lead (L0), because the regime probability is derived from already-released data.

Search-phase OOS results (2018-02-28 to 2026-05-31, no holdout final exam yet): Sharpe **1.49 vs 0.89** buy-and-hold; annualised return 15.9% vs 14.8%; maximum drawdown **−8.3% vs −23.9%**; 10 OOS position changes; annual turnover 1.2; OOS win rate 48%.

### How the Signal is Generated

The data process reads the Census/FRED monthly new-home-sales release (`HSN1FNSA`), computes its year-over-year growth to strip out the fixed seasonal, fits a 2-state Hidden Markov Model to that growth series, and takes the probability of the favourable (calm) regime. When that probability clears its rolling 25th-percentile threshold, the rule holds SPY; otherwise cash. It is intentionally simple: it does not forecast mortgage rates or model the Fed — it asks whether the housing-demand backdrop is healthy and times SPY on that.

### Tradeoff and Fragility

The rule improves Sharpe and roughly thirds the drawdown, but: forward causality is weak (single long Granger lag), the winner is the max of 5,297 combinations with bootstrap p = 0.071 (not significant at 5%), in-sample Sharpe (0.81) is far below OOS (1.49), and durability is only `conditionally_durable` with one evaluable episode. Treat it as a low-confidence, search-found candidate awaiting a frozen-rule final exam.

## Methodology

### Data Sources

Indicator: New One-Family Houses Sold, `HSN1FNSA` (thousands, **not seasonally adjusted**), Federal Reserve/Census via live FRED API. Target: SPY adjusted close (Yahoo Finance). Monthly panel 1990–2026 (SPY-bound from 1993); daily LVCF panel with release-lag discipline (Census releases prior-month sales ~4th Tuesday of the following month).

### Model Suite

Correlation battery, pre-whitened cross-correlation, Toda-Yamamoto Granger (both directions), transfer entropy, local projections (forward + reverse), quantile regression, 2-state HMM and Markov-switching regimes, regime quartiles, Quandt-Andrews structural break, and a 5-dimensional strategy tournament (signals × thresholds × strategy families × orientations × monthly leads L0–12 × lookbacks).

### Limitations

The raw series is NSA and requires deseasonalisation (YoY/STL); the raw level and STL level are non-stationary and excluded from the signal set. Forward causality is weak; the winner is search-selected with a non-significant bootstrap p-value and no final exam; the OOS window is short and episode-concentrated. New home sales are volatile and heavily revised — the live FRED vintage is treated as ground truth.
