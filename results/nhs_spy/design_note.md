# Design Note — nhs_spy (20260703)

## Category & method coverage (Rule C1, housing/activity)
All macro/activity mandatory methods produced. Deviations from the daily-pair spec, per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in levels of the stationary YoY transform with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations.
- Stationarity: Dana's tests (stationarity_tests_20260703.csv) reviewed and CONFIRMED, not re-run.
  NHS LEVEL (nhs_nsa) and STL LEVEL (nhs_sa) are NON-stationary and are EXCLUDED from the signal set.

## NSA / seasonality handling (defining feature)
HSN1FNSA is NOT seasonally adjusted. All signals are deseasonalised: `nhs_pct_yoy` (primary; 12-month
difference cancels the fixed seasonal), STL-based `nhs_sa_pct_mom`/`nhs_sa_3m_pct`, and a z-score on the
YoY series. Raw level and raw MoM are intentionally excluded as seasonal-dominated.

## Lead-lag verdict
- NHS->SPY TY-Granger significant lags: [11]
- SPY->NHS TY-Granger significant lags: [1, 2]
- Reverse-causality LP flag: True

## Data provenance
Source = FRED HSN1FNSA live API (1963-01 -> 2026-05). Data Master HAJKE_Month column NHS used as an
overlap cross-check (level corr 0.9998). SPY sourced from Yahoo (cached-close fallback used when the
live API was rate-limited; identical adjusted-close series).

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent.
- Lead grid [0,1,2,3,6,9,12] (ECON-LL1 monthly); L1 real-time floor (Census ~4th-Tuesday publication);
  L6 centered. position_t = rule(signal_(t-L)); strategy_return_t = position_t * spy_ret_t.
- Both orientations (pro/counter) tested per the empirical direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_20260703/.

## New pair — no prior version, Rule C3 regression diff not applicable.
