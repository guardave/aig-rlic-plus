# Design Note — m2sl_yoy_spy (20260619)

## Category & method coverage (Rule C1, macro/production)
All macro mandatory methods produced. Deviations from the daily-pair spec, documented per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in levels of the stationary YoY transform with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations (dcor/pyinform not in env).
- Stationarity: Dana's tests (stationarity_tests_20260619.csv) reviewed and CONFIRMED, not re-run.
  M2SL LEVEL is NON-stationary (ADF p=0.99, KPSS reject) and is EXCLUDED from the signal set.

## Lead-lag verdict
- M2SL->SPY TY-Granger significant lags: NONE
- SPY->M2SL TY-Granger significant lags: [1, 2, 3, 4, 5, 8]
- Reverse-causality LP flag: False
See handoff for the full verdict.

## Data provenance
Source = FRED M2SL live API (current vintage, 1959-01 -> 2026-04). M2 is a REVISED, seasonally-adjusted
series; the Data Master M2SL snapshot is a stale vintage (~0.5% above current FRED at recent dates due to
SA revisions). FRED is treated as ground truth.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent — documented in the CSV manifest.
- Lead grid [1, 2, 3, 6, 12] starts at L1 (real-time floor: M2 H.6 publishes ~4th Tuesday for the
  prior month) and centers L6. Lead semantics: position_t = rule(signal_(t-L)); strategy_return_t =
  position_t * spy_ret_t.
- Both orientations (pro/counter) tested per the empirical direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_20260619/.

## New pair — no prior version, Rule C3 regression diff not applicable.
