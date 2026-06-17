# Evan Handoff — petrol_inv_spy (20260617)

## Winner spec
- Winner: `petrol_3m / T1_fixed_p50 / P1_long_cash (pro) / L12 / LB_NA`
- Signal column: `petrol_inv_3m_pct` (present in `results/petrol_inv_spy/signals_20260617.parquet`)
- OOS: 2017-08-31 -> 2025-09-30
- Winner OOS Sharpe 1.48 vs B&H 0.93; ann return 9.8% vs 15.2%; max DD -6.3% vs -23.9%.
- Suggested strategy objective: `max_sharpe`.

## Observed direction and caveat
Observed direction: `procyclical`. Expected direction was mixed, so this is direction-consistent. Confidence: `low`. Evidence status is `found_in_search`: selected from the tournament, not validated by a final exam.

## Method artifacts for Vera/Ray
| method | result_file | expected_chart | status |
|---|---|---|---|
| Correlations | `results/petrol_inv_spy/core_models_20260617/correlations.csv` | correlation matrix / bar | ready |
| Pre-whitened CCF | `results/petrol_inv_spy/core_models_20260617/ccf_prewhitened.csv` | CCF lag bars | ready |
| Granger | `results/petrol_inv_spy/granger_by_lag.csv` + `core_models_20260617/granger_causality.csv` | F-stat by lag | ready |
| Local projections | `results/petrol_inv_spy/core_models_20260617/local_projections.csv` | impulse response | ready |
| Quantile regression | `results/petrol_inv_spy/core_models_20260617/quantile_regression.csv` | coefficient by quantile | ready |
| HMM regime | `results/petrol_inv_spy/core_models_20260617/hmm_states.parquet`, `hmm_summary.csv` | regime timeline / stats | ready |
| Quartile returns | `results/petrol_inv_spy/regime_quartile_returns.csv` | Q1-Q4 bars | ready |
| Strategy returns | `results/petrol_inv_spy/strategy_returns_20260617.csv` | equity/drawdown charts | ready |

## Lead-lag notes
- Indicator -> SPY TY-Granger significant lags: [6, 7, 8]
- SPY -> indicator TY-Granger significant lags: none
- Local projections reverse significant horizons: none

## Key charts needed
Hero inventory vs SPY, correlation battery, Granger by lag both-direction callout, HMM stress timeline, quartile returns, tournament Sharpe distribution, strategy equity/drawdown, rolling correlation, structural break marker.
