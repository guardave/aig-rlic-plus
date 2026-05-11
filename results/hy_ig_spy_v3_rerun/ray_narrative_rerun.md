<!-- ray_narrative_rerun.md — hy_ig_spy_v3_rerun experiment fork -->
<!-- RES-NR1: instrument references confirmed against interpretation_metadata.json -->
<!-- indicator_id: hy_ig_spread_pct → "HY-IG credit spread" in prose -->
<!-- target_symbol: SPY → "S&P 500 (SPY)" in prose -->

## Evidence

This fork tests a clean rerun of the hy_ig_spy v3 pipeline with the winner rule S2a_zscore_252d / T2_rp75 / P1. The primary question is whether a pipeline-clean re-execution, holding all design choices fixed, reproduces the original findings under the ECON-OOS4 three-period split.

The HY-IG credit spread — the yield gap between high-yield (junk) bonds and investment-grade corporate bonds — is a leading credit stress indicator. When this spread widens sharply relative to its recent history, it signals that markets are pricing elevated default risk, typically ahead of equity drawdowns. The winner signal (S2a_zscore_252d) standardises the raw HY-IG credit spread against its own trailing 252-day distribution (z-score), producing a dimensionless stress index that filters out secular level drift. The observed direction is confirmed countercyclical: elevated z-score precedes negative S&P 500 (SPY) returns in the backtest data.

The 10-condition ECON-FE1 framework scores 7/10 passes. Validation OOS Sharpe is 1.20 (2018–2025-01). Holdout Sharpe is 0.85 (Jan–Dec 2025, 251 observations). Three conditions fail with honest interpretations: C03 (block bootstrap 2.5th percentile = −1.19) fails because 252 holdout days yield only ~12 non-overlapping 21-day blocks — a genuine low-power artefact, not a sampling bug. C04 (deflated Sharpe ratio, DSR p-value ≪ 0.05) correctly fails given 150 effective trials across the candidate space; the DSR penalises multiple comparisons and this fork does not clear that bar. C05 (excess annual return vs. buy-and-hold = −14.4 pp) fails because SPY delivered ~19.7% annualised in 2025 — a strong bull-market year where a risk-off rule, by design, underperforms a fully-invested benchmark.

This fork tests the clean rerun design: re-running the identical pipeline from source data with a column-alignment fix. The three failing conditions are structurally expected for a single-year holdout in a bull market with a large candidate pool; they do not invalidate the validation-period evidence but do correctly constrain the confidence grade to "low."

## Strategy

The winner rule enters cash (zero SPY exposure) when the 252-day z-score of the HY-IG credit spread crosses above the rolling 75th percentile (T2_rp75) — that is, when current spread stress is elevated relative to the past year's own distribution. It exits back to full SPY when the z-score falls below that threshold. Position sizing follows P1 (binary): the rule is either fully invested in S&P 500 (SPY) or fully in cash. There are no partial allocations. Lead days = 0 (signal and trade execute on the same bar).

In the holdout period (Jan–Dec 2025, 251 trading days), the strategy executed 16 trades. Holdout Sharpe was 0.85 vs. 1.20 in validation — a degradation of 0.35 Sharpe units, within the C10 threshold of 0.5 (PASS). Holdout MDD was −5.1% vs. −18.8% for buy-and-hold. The strategy preserved capital during intra-year drawdowns but sacrificed return in a year when SPY appreciated ~19.7%; excess annual return was −14.4 pp. This trade-off is expected from a countercyclical protection rule in a low-volatility bull market year.

## Methodology

The experiment uses the ECON-OOS4 three-period split: in-sample 2000-01-03 to 2018-10-03 (4,893 days), validation OOS 2018-10-04 to 2025-01-13 (1,638 days), and holdout 2025-01-14 to 2025-12-31 (252 days). The winner is selected on validation Sharpe; the holdout is used once, blind, for final evaluation. No re-fitting occurs after the IS period.

ECON-FE1 is a 10-condition pass/fail framework that evaluates holdout robustness across six dimensions: absolute Sharpe adequacy (C01, C02), statistical significance under resampling (C03 block bootstrap; C04 deflated Sharpe ratio), economic value over buy-and-hold (C05 excess return), drawdown control (C06, C07), validation consistency (C08), sample size adequacy (C09), and performance stability (C10 Sharpe degradation). Conditions are scored against pre-specified thresholds; no post-hoc adjustment is permitted.

This fork specifically tests whether a clean pipeline re-execution — fixing a column-alignment bug identified after the original run — changes the winner selection or ECON-FE1 outcome. The winner (S2a_zscore_252d / T2_rp75 / P1) is unchanged, and 7/10 conditions pass in both runs. The result implies ECON-OOS4 compliance is robust to the column fix: the fork is consistent with the original pipeline but does not achieve full 10/10 ECON-FE1 pass, confirming the three structurally-expected failures are properties of the holdout environment (small T, large candidate pool, bull-market year), not of the bug fix.
