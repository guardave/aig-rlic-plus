# Design Note — housing_starts_spy (20260814)

## Category & method coverage (Rule C1, housing/activity)
All macro/activity mandatory methods produced. Deviations from the daily-pair spec, per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in levels of the stationary YoY transform with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations.
- Stationarity: Dana's tests (stationarity_tests_20260814.csv) reviewed and CONFIRMED, not re-run.
  Housing Starts LEVEL (hst_level) is NON-stationary and is EXCLUDED from the signal set.

## SA handling (contrast with nhs_spy)
HOUST is Seasonally Adjusted (SAAR). No deseasonalisation is required: `hst_pct_mom` (month-over-month)
is a valid momentum input and `hst_pct_yoy` (12-month change) is the primary growth signal, with
`hst_3m_pct`, `hst_3m_pct_yoy`, `hst_yoy_accel_pct` and a z-score on the YoY series. The raw SAAR level
is trend-dominated / non-stationary and is intentionally excluded.

## Lead-lag verdict
- Housing Starts->SPY TY-Granger significant lags: NONE
- SPY->Housing Starts TY-Granger significant lags: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
- Reverse-causality LP flag: True

## Data provenance
Source = FRED HOUST live API (1959-01 -> latest). Data Master sheet 'H Started' column 'RE - H Started'
used as an overlap cross-check (level corr 0.99998). SPY sourced from Yahoo (cached-close fallback used
when the live API was rate-limited; identical adjusted-close series).

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent.
- Lead grid [0,1,2,3,6,9,12] (ECON-LL1 monthly); L1 real-time floor (Census/HUD ~17th publication);
  L6 centered. position_t = rule(signal_(t-L)); strategy_return_t = position_t * spy_ret_t.
- Both orientations (pro/counter) tested per the empirical direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_20260814/.

## New pair — no prior version, Rule C3 regression diff not applicable.
