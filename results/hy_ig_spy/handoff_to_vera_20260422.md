# Evan → Vera Handoff: hy_ig_spy (20260422)

## ECON-H4 Per-Method Chart Artifact Table

| Method | Result File | Expected Chart | Status |
|--------|-------------|----------------|--------|
| Correlation heatmap | `results/hy_ig_spy/exploratory_20260422/correlations.csv` | Signal × horizon Pearson r heatmap | ready |
| Granger by lag | `results/hy_ig_spy/granger_by_lag.csv` | F-statistic by lag 1-12 bar chart | ready |
| Predictive regressions | `results/hy_ig_spy/core_models_20260422/predictive_regressions.csv` | Coefficient forest plot across signals × horizons | ready |
| Local projections | `results/hy_ig_spy/core_models_20260422/local_projections.csv` | IRF-style coefficient × horizon line chart with CI | ready |
| Quantile regression | `results/hy_ig_spy/core_models_20260422/quantile_regression.csv` | Quantile coefficients vs OLS line chart | ready |
| HMM regime overlay | `results/hy_ig_spy/core_models_20260422/hmm_states_2state.parquet` | Regime probability overlay on spread time-series | ready |
| Quartile returns | `results/hy_ig_spy/regime_quartile_returns.csv` | Q1-Q4 annualized SPY return bar chart | ready |
| Walk-forward | `results/hy_ig_spy/tournament_validation_20260422/walk_forward.csv` | Annual OOS Sharpe scatter | ready |
| Bootstrap CI | `results/hy_ig_spy/tournament_validation_20260422/bootstrap_ci.csv` | Sharpe CI95 bar chart for top-5 | ready |
| Transaction costs | `results/hy_ig_spy/tournament_validation_20260422/transaction_costs.csv` | Net Sharpe vs cost bps line chart | ready |
| Signal decay | `results/hy_ig_spy/tournament_validation_20260422/signal_decay.csv` | Sharpe vs execution delay bar chart | ready |
| Stress tests | `results/hy_ig_spy/tournament_validation_20260422/stress_tests.csv` | Strategy vs benchmark Sharpe per stress period | ready |
| Cumulative return | `results/hy_ig_spy/winner_trade_log.csv` | Cumulative return curve: strategy vs B&H | ready |
| Stationarity | `results/hy_ig_spy/stationarity_tests_20260422.csv` | Table of ADF/KPSS results | ready |

## Winner Summary

- Signal: **S6_hmm_stress** (`hmm_2state_prob_stress`)
- Threshold: T4_hmm_0.5  |  Strategy: P2  |  Lead: 0d
- OOS Sharpe: 1.41  |  Return: 11.7%  |  MDD: -8.5%
- B&H Sharpe: 0.81
- OOS window: 2019-10-01 → 2026-04-22
- Direction: countercyclical

## Notes for Vera

- All ratio-form values (returns, MDD) are decimals — multiply ×100 for display pct.
- granger_by_lag.csv uses monthly series (lags 1-12 months); x-axis label = "Lag (months)".
- regime_quartile_returns.csv: Q1=tightest spread (bullish), Q4=widest spread (bearish).
- HMM: stress_state is the high spread_change regime; probability near 1.0 → cash.
- Chart sidecar _meta.json required per VIZ-IC1 for each chart JSON saved.

Generated: 2026-04-22T10:42:16Z
Author: Econ Evan
