# Design Note — busloans_spy (20260612)

## Category & method coverage (Rule C1, credit-equity)
All credit-equity mandatory methods produced. Deviations from the daily-pair spec, documented per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in levels of the stationary YoY transform with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations (dcor/pyinform not in env).
- Stationarity: Dana's tests (stationarity_tests_20260612.csv) reviewed and CONFIRMED, not re-run.

## Lead-lag verdict (the lagging-indicator hypothesis)
- BUSLOANS→SPY TY-Granger significant lags: NONE
- SPY→BUSLOANS TY-Granger significant lags: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
- Reverse-causality LP flag: False
See handoff for the full verdict.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent — documented in the CSV manifest.
- Lead grid starts at L1 (real-time floor per Dana's H.8 publication-lag doc). Lead semantics:
  position_t = rule(signal_(t−L)); strategy_return_t = position_t × spy_ret_t.
- Both orientations (pro/counter) tested per the mixed direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_20260612/.

## New pair — no prior version, Rule C3 regression diff not applicable.
