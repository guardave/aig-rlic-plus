# Design Note — ism_services_spy (20260618)

## Category & method coverage (Rule C1, sentiment-equity + brief add-ons)
All sentiment-equity mandatory methods produced, plus CCF/local projections/structural break per brief. Deviations from the daily-pair spec, documented per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in stationary PMI level with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations (dcor/pyinform not in env).
- Stationarity: Dana's tests (stationarity_tests_20260618.csv) reviewed and CONFIRMED, not re-run.

## Lead-lag verdict (sentiment already priced / reverse causality)
- ISM Services→SPY TY-Granger significant lags: NONE
- SPY→ISM Services TY-Granger significant lags: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
- Reverse-causality LP flag: True
See handoff for the full verdict.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent — documented in the CSV manifest.
- Monthly lead grid starts at L1 (real-time floor: prior-month PMI publishes early in the following month). Lead semantics:
  position_t = rule(signal_(t−L)); strategy_return_t = position_t × spy_ret_t.
- Daily LVCF data has release lag baked in; daily L0 on the carried value is feasible, but this monthly tournament uses L1+.
- Both orientations (pro/counter) tested per the mixed direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_20260618/.

## New pair — no prior version, Rule C3 regression diff not applicable.
