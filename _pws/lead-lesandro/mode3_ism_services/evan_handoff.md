# Handoff: Econ Evan -> Viz Vera + Research Ray — ism_services_spy

**Date:** 2026-06-18  
**Mode:** Mode 3 maker dispatch  
**Pair:** `ism_services_spy` (ISM Services PMI -> SPY)  
**Producer script:** `scripts/pair_pipeline_ism_services_spy.py` (deterministic, `np.random.seed(42)`)  
**Upstream:** Dana's monthly dataset `data/ism_services_spy_monthly_latest.parquet` and daily LVCF dataset `data/ism_services_spy_daily_latest.parquet`. Dana's stationarity file `results/ism_services_spy/stationarity_tests_20260618.csv` reviewed and confirmed; I did not re-run stationarity.

## Source and Lag Convention

ISM Services PMI is not a public FRED series in this project. Source is `data/Data Master.xlsx`, sheet `ISM PMI`, column `CDis, CSta - ISM Services PMI`; vintage ends October 2025.

Monthly tournament convention: prior-month PMI is released early the following month, so month-end PMI is not tradable at that month-end. The monthly tournament starts at L1 and sweeps L1/L2/L3/L6/L12. Daily LVCF data has release lag already baked in via `release_date` and `days_since_release`; daily L0 on the carried value is feasible, but the tournament here is monthly.

## Winner Spec

| field | value |
|---|---|
| winner | `gap_50 / T3_zscore_neg_1.0 / P1_long_cash (pro) / L3 / LB120` |
| `winner_summary.signal_code` | `ism_services_gap_50` |
| `winner_summary.signal_column` | `ism_services_gap_50` |
| threshold | rolling z-score lower band; latest threshold value `1.9503`; rule `lt` |
| rule | long SPY when lagged PMI gap-to-50 is below its rolling threshold; otherwise cash |
| empirical direction | `countercyclical` |
| OOS window | 2018-10-31 to 2025-10-31 (`oos_split_record.json`, 85 months) |
| OOS Sharpe | 1.5377 vs B&H 0.8796 |
| OOS annual return | 9.84% vs B&H 15.12% |
| OOS max drawdown | -3.76% vs B&H -23.93% |
| trades / turnover | 17 OOS position changes; annual turnover 2.40 |
| objective suggestion | `min_mdd` |

Critical SEV1 check: `results/ism_services_spy/signals_20260618.parquet` contains `ism_services_gap_50`; `winner_summary.signal_column` matches exactly.

## Lead-Lag Verdict

The natural prior was procyclical: PMI above 50 or rising should be risk-on. The empirical monthly lead-lag evidence does not support that as a forward SPY predictor.

- Toda-Yamamoto Granger, `ISM Services -> SPY`: no significant lags 1-12.
- Toda-Yamamoto Granger, `SPY -> ISM Services`: significant at every lag 1-12.
- Local projections: reverse direction significant at horizons 1, 3, 6, and 12 months.
- Transfer entropy: indicator -> target TE p=0.064; target -> indicator TE p=0.002.

Ray should narrate this as a sentiment/coincident survey that appears already priced by equities. The tournament winner is a searched drawdown-control rule, not validated standalone alpha.

## Evidence Status

`results/ism_services_spy/evidence_status.json`: `found_in_search`.

Why not validated: the winner was selected and evaluated on the tournament OOS window, with no fresh final-exam holdout. Bootstrap p-value for the top rule is 0.073, not below 5%. Structural break test flags 2009-03-31. CP1 durability is `episode_concentrated`; rolling-correlation verdict is `moderately_stable`.

## Method Artifact Table

| method | result_file | expected_chart | status |
|---|---|---|---|
| Correlation battery | `results/ism_services_spy/core_models_20260618/correlations.csv` | signal x horizon heatmap, include distance corr note | ready |
| Pre-whitened CCF | `results/ism_services_spy/core_models_20260618/ccf_prewhitened.csv` | CCF bars with +/- CI, lags -20..+20 | ready |
| Granger summary | `results/ism_services_spy/core_models_20260618/granger_causality.csv` | both-direction p-value / F-stat comparison | ready |
| Granger by lag | `results/ism_services_spy/granger_by_lag.csv` | F-stat by lag bars for indicator -> target | ready |
| Local projections | `results/ism_services_spy/core_models_20260618/local_projections.csv` | IRF with CI band, forward + reverse panels | ready |
| Transfer entropy | `results/ism_services_spy/core_models_20260618/transfer_entropy.csv` | two-bar information-flow comparison | ready |
| Quantile regression | `results/ism_services_spy/core_models_20260618/quantile_regression.csv` | coefficient by tau with CI band | ready |
| HMM regime | `results/ism_services_spy/core_models_20260618/hmm_states.parquet` + `hmm_summary.csv` | low-PMI stress probability timeline | ready |
| PMI level quartiles | `results/ism_services_spy/regime_quartile_returns.csv` | Q1-Q4 annualized return bars | ready |
| PMI 3m-change quartiles | `results/ism_services_spy/regime_quartile_returns_3m_change.csv` | Q1-Q4 annualized return bars | ready |
| Tournament | `results/ism_services_spy/tournament_results_20260618.csv` | 5D search heatmap; valid strategy count excludes BENCHMARK | ready |
| Equity / drawdown | `results/ism_services_spy/strategy_returns_20260618.csv` | winner vs B&H cumulative return and drawdown | ready |
| Sub-period Sharpe | `results/ism_services_spy/subperiod_sharpe.csv` | episode Sharpe bars, insufficient-data labels where needed | ready |
| Rolling correlation | `results/ism_services_spy/rolling_correlation_ism_services_spy.csv` | rolling 24M correlation timeline | ready |
| Structural break | `results/ism_services_spy/structural_break_ism_services_spy.json` | annotation/callout; flagged break | ready |

## Quartile Findings

PMI level quartiles: Q1 (lowest PMI) has Sharpe 0.209 and max drawdown -60.25%; Q3/Q4 are stronger (Sharpe 1.001 / 0.861). This supports the common-sense view that low activity regimes coincide with poor equity conditions.

PMI 3-month-change quartiles: Q1 weakest momentum Sharpe 0.008; Q3/Q4 Sharpe 1.428 / 1.300. Momentum carries the procyclical relationship more cleanly than level.

## Files for Ace/Ray

- `results/ism_services_spy/winner_summary.json` (schema-valid)
- `results/ism_services_spy/tournament_winner.json`
- `results/ism_services_spy/tournament_results_20260618.csv` + manifest
- `results/ism_services_spy/winner_trade_log.csv`
- `results/ism_services_spy/winner_trades_broker_style.csv`
- `results/ism_services_spy/strategy_returns_20260618.csv` + meta
- `results/ism_services_spy/oos_split_record.json`
- `results/ism_services_spy/evidence_status.json`
- `results/ism_services_spy/signal_scope.json`
- `results/ism_services_spy/kpis.json`
- `results/ism_services_spy/analyst_suggestions.json`
- `results/ism_services_spy/design_note.md`
- `results/ism_services_spy/tournament_tie_note.md`

## Validation Run

- `python3 scripts/pair_pipeline_ism_services_spy.py` completed.
- `winner_summary.json` schema validation PASS.
- `signal_scope.json` schema validation PASS.
- `analyst_suggestions.json` schema validation PASS.
- `docs/schemas/signal_code_registry.json` JSON parse PASS.
- Benchmark row check PASS: exactly one `signal == "BENCHMARK"` row and `valid=False`.
- Winner signal-column check PASS: `ism_services_gap_50` exists in `signals_20260618.parquet`.

