# Design Note — nhs_spy (20261016)

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
Source = FRED HSN1FNSA (1963-01 -> 2026-05) via Dana's data stage. The original input parquet is
gitignored and was rebuilt for the 20261016 run with the indicator transforms exactly as published in
signals_20260703.parquet and SPY re-pulled from Yahoo (monthly returns within 1.6e-6 of the 20260703
file); see _pws/lead-lesandro/pkg13_hmm_port/nhs_frozen_input.py. A fresh live pull differs: FRED
revised 2026-04/05, and the STL seasonal adjustment behind nhs_sa_* is a full-sample (two-sided)
decomposition, so its values change when months are added.

## Regime models (20261016)
HMM (2 states, NHS YoY, stress = higher-variance state) and Markov-switching (2 regimes, switching
variance, on NHS YoY itself; the old model put spy_ret in the likelihood) are fit on IS months only and
read with a forward filter (scripts/_regime_causal.py). The 20260703 winner used full-sample
forward-backward smoothed HMM probabilities; replay and causal comparison in
hmm_lookahead_audit_20261016.json.

## Selection (20261016)
argmax IS Sharpe on the common IS window 2002-11-30..2018-01-31 (173 months;
start set by yoy_zscore_120m/T2_roll_p25/LB120/L12, yoy_zscore_120m/T2_roll_p75/LB120/L12, yoy_zscore_120m/T3_zscore_1.0/LB120/L12); eligibility before alignment, MIN_IS_N=60; validity uses
IS rows only. Winner contraction/T2_roll_p25/LB36/P2_signal_strength_counter/L9:
IS Sharpe 1.4628 (B&H 0.7867); OOS Sharpe 0.9318
(B&H 0.8935), HAC t 3.26. 5500 combos, 5344 IS-valid,
Spearman(IS, OOS) 0.691.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent.
- Lead grid [2, 3, 6, 9, 12]: the legacy ECON-LL1 grid [0,1,2,3,6,9,12] truncated at the registry floor L2
  (Census publishes month M near the end of M+1). position_t = rule(signal_(t-L));
  strategy_return_t = position_t * spy_ret_t.
- Both orientations (pro/counter) tested per the empirical direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_20261016/.

## Previous version: 20260703 (OOS-selected, L0 smoothed-HMM winner); superseded.
