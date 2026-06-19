Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/m2sl_yoy_spy_monthly_latest.parquet` (source dated file `data/m2sl_yoy_spy_monthly_19930131_20260430.parquet`)
- Daily LVCF dataset: `data/m2sl_yoy_spy_daily_latest.parquet` (source dated file `data/m2sl_yoy_spy_daily_19930129_20260617.parquet`)
- Monthly sidecar: `data/m2sl_yoy_spy_monthly_schema.json`
- Daily sidecar: `data/m2sl_yoy_spy_daily_schema.json`
- Data dictionary: `data/data_dictionary_m2sl_yoy_spy_20260619.csv`
- Missing-value report: `data/missing_value_report_m2sl_yoy_spy_20260619.md`
- Stationarity: `results/m2sl_yoy_spy/stationarity_tests_20260619.csv`
- Interpretation metadata: `results/m2sl_yoy_spy/interpretation_metadata.json`

Summary:
Built the M2 Money Supply YoY -> SPY data layer from live FRED M2SL. The monthly panel is 400 rows x 14 columns, 1993-01-31 to 2026-04-30. The daily panel is 8403 SPY trading days x 19 columns, 1993-01-29 to 2026-06-17, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
PASS: Pre-master maps `M2SL` sheet column B to M2SL level and column C to `M2SL_YOY`; descriptions are `M2 Money Supply, monthly, from Federal Reserve` and `M2 Money Supply, monthly, from Federal Reserve YoY%`.
PASS (soft): Data Master M2SL overlap agrees in shape/sign with live FRED. Level corr=0.999998; YoY corr=0.999918; YoY sign agreement=1.000; monthly-change sign agreement=0.996. Revision drift observed: max level diff 108.5000 $bn (0.491%), max YoY diff 0.5195 pp. This is treated as benign seasonal-adjustment/vintage drift per Lead adjudication; FRED live M2SL is the source of truth. Last Data Master row is 2025-08-31: M2SL=22195.4, M2SL_YOY=4.76793%.
FRED live M2SL currently runs 1993-01-31 to 2026-04-30 in this delivered panel; full source history starts 1959-01.

Units and direction prior:
`m2sl_pct_yoy` is percent YoY, computed as `(M2SL / M2SL.shift(12) - 1) * 100`. Direction prior for Evan: procyclical/liquidity tailwind for SPY. Important counter-channel: rapid money growth can also presage inflation and policy tightening. The 0% line is economically meaningful: below zero is outright M2 contraction. `m2sl_usd` is included for provenance only and should not be used as a signal.

Release lag floor:
Daily LVCF assumes prior-month M2SL is released on the fourth Tuesday of the following month. This creates a real-time no-lookahead floor of roughly 22-28 calendar days after reference month-end. Do not use month-end M2 values as if known at month-end; use the daily panel's release-date carry-forward and `days_since_release`.

Stationarity:
- `m2sl_usd`: ADF p=0.9947 (Non-stationary); KPSS p=0.0001 (Reject stationarity at 5%).
- `m2sl_pct_yoy`: ADF p=0.0164 (Stationary at 5%); KPSS p=0.5567 (Fail to reject stationarity).
- `m2sl_pct_mom`: ADF p=0.0008 (Stationary at 5%); KPSS p=0.5016 (Fail to reject stationarity).
- `m2sl_3m_pct`: ADF p=0.0006 (Stationary at 5%); KPSS p=0.5438 (Fail to reject stationarity).
- `m2sl_6m_pct`: ADF p=0.0011 (Stationary at 5%); KPSS p=0.5697 (Fail to reject stationarity).
- `m2sl_yoy_accel_pct`: ADF p=0.0000 (Stationary at 5%); KPSS p=0.9450 (Fail to reject stationarity).
- `m2sl_yoy_zscore_120m`: ADF p=0.0192 (Stationary at 5%); KPSS p=0.4942 (Fail to reject stationarity).

Recommendation:
Do not use the M2SL level as a signal. Prefer `m2sl_yoy_accel_pct` as the cleanest primary transform where stationarity matters; use `m2sl_pct_yoy`, `m2sl_pct_mom`, `m2sl_3m_pct`, `m2sl_6m_pct`, and `m2sl_yoy_zscore_120m` as robustness candidates, with explicit regime controls for the COVID surge and 2022-23 contraction period. Treat `m2sl_contraction_flag` as a threshold/regime feature.

Known issues:
- Release dates are approximated by a fourth-Tuesday rule, not a historical release timestamp file.
- Daily indicator values are a deliberate monthly step function and will induce serial dependence in daily OLS-style specifications.
- The SPY feed returned a missing adjusted close for 2026-06-18 during this run; that row was dropped, so the daily panel ends at the last non-missing adjusted close.

Questions for recipient:
- None. Evan should set the no-lookahead lead-grid floor at one monthly publication lag (minimum L1 monthly, or daily horizons after release-date carry-forward).
