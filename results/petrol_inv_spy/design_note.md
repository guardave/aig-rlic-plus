# Design Note — petrol_inv_spy (20261016)

## Economic hypotheses
H1 counter-cyclical demand signal: rising/high petroleum inventories can indicate weak fuel demand and lower forward SPY. H1b supply-glut benign: inventory builds may reflect supply rather than demand. H0: petroleum stocks do not predict SPY.

## Data provenance and vintage
WTTSTUS1 is an EIA petroleum-stocks series sourced from project `data/Data Master.xlsx` sheet `WTTSTUS1`; FRED public API rejected WTTSTUS1 on 2026-06-17. Dana's vintage ends October 2025. Monthly analysis data: `/workspaces/aig-rlic-plus/data/petrol_inv_spy_monthly_latest.parquet`. Daily LVCF data: `/workspaces/aig-rlic-plus/data/petrol_inv_spy_daily_latest.parquet`, with `days_since_release` 0-6.

## Stationarity and method category
Dana's stationarity artifact `results/petrol_inv_spy/stationarity_tests_20260617.csv` was reviewed and confirmed, not re-run. Levels are nonstationary; the tournament and models use stationary transforms only. Indicator type is macro / cross-asset, so this run includes correlation battery with distance correlation, pre-whitened CCF, Toda-Yamamoto Granger both directions, local projections, quantile regression, HMM regime detection, quartile returns, structural break, and validation sensitivity.

## Lag convention
Daily LVCF may use L0 because carried values are already public after release. The monthly signal is the calendar-month mean of weekly stocks; the last weekly print of month M is released 0-5 days into M+1, so the monthly tournament starts at the strict floor L2 (grid L2..L12; standard Step 2 amended 2026-10-16).

## Lead-lag verdict
Indicator -> SPY Granger significant lags: [6, 7, 8]. SPY -> indicator Granger significant lags: none. Reverse direction is therefore reported directly for Ray rather than suppressed.

## Tournament and evidence status
Benchmark row has `signal == "BENCHMARK"` and `valid == False` per ECON-T4. Winner signal column `petrol_inv_zscore_60m` exists in `signals_20261016.parquet`. Evidence status is `found_in_search`; no independent final exam has been run.
