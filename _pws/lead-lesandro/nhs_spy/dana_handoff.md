Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/nhs_spy_monthly_latest.parquet` (source dated file `data/nhs_spy_monthly_19900131_20260531.parquet`)
- Daily LVCF dataset: `data/nhs_spy_daily_latest.parquet` (source dated file `data/nhs_spy_daily_19930129_20260617.parquet`)
- Monthly sidecar: `data/nhs_spy_monthly_schema.json`
- Daily sidecar: `data/nhs_spy_daily_schema.json`
- Data dictionary: `data/data_dictionary_nhs_spy_20260703.csv`
- Missing-value report: `data/missing_value_report_nhs_spy_20260703.md`
- Stationarity: `results/nhs_spy/stationarity_tests_20260703.csv`
- Interpretation metadata: `results/nhs_spy/interpretation_metadata.json`

Summary:
Built the New Home Sales (NSA) -> SPY data layer from live FRED HSN1FNSA. Monthly panel is 437 rows x 15 columns, 1990-01-31 to 2026-05-31. Daily panel is 8403 SPY trading days x 20 columns, 1993-01-29 to 2026-06-17, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
PASS: Pre-master maps sheet `HAJKE_Month` column `NHS` to 'New One Family Houses Sold, Thousands of Units, Monthly, Not Seasonally Adjusted, from FRED' (verbatim: `New One Family Houses Sold, Units : Thousands of Units Monthly, Not Seasonally Adjusted, from FRED`). Confirms FRED HSN1FNSA (NSA, thousands). Distinct from HSN1F (SAAR, indicator_id nh_sold_saar) and the YoY% SAAR transform.
PASS (soft): Data Master NHS (HAJKE_Month) agrees with live FRED HSN1FNSA. Level corr=0.999763; 99.3% of 428 overlapping months within 0.5k; max abs diff 9.0k (benign vintage/revision drift). FRED live is source of truth. Last overlap 2025-08-31: FRED=57k, DataMaster=66k.

CRITICAL — NSA handling:
HSN1FNSA is NOT seasonally adjusted. Do NOT use `nhs_nsa` (raw level) or a raw MoM as a signal — both are seasonal-dominated. Primary signal is `nhs_pct_yoy` (12-month difference cancels the fixed seasonal). `nhs_sa`/`nhs_sa_pct_mom` are STL-deseasonalised alternatives for momentum. `nhs_yoy_zscore_120m` is computed on the YoY series. Direction prior: procyclical (stronger housing demand -> risk-on). Counter-channel: at cycle peaks a far-above-trend reading can mean-revert (INDPRO precedent) — verify empirically.

Release lag floor:
Daily LVCF assumes prior-month NHS is released on the fourth Tuesday of the following month (~Census schedule). No-lookahead floor ~22-28 calendar days after reference month-end.

Stationarity:
- `nhs_nsa`: ADF p=0.4444 (Non-stationary); KPSS p=0.0360 (Reject stationarity at 5%).
- `nhs_pct_yoy`: ADF p=0.0113 (Stationary at 5%); KPSS p=0.3194 (Fail to reject stationarity).
- `nhs_yoy_accel_pct`: ADF p=0.0000 (Stationary at 5%); KPSS p=0.8687 (Fail to reject stationarity).
- `nhs_3m_pct_yoy`: ADF p=0.1332 (Non-stationary); KPSS p=0.2984 (Fail to reject stationarity).
- `nhs_sa`: ADF p=0.4586 (Non-stationary); KPSS p=0.0366 (Reject stationarity at 5%).
- `nhs_sa_pct_mom`: ADF p=0.0000 (Stationary at 5%); KPSS p=0.5167 (Fail to reject stationarity).
- `nhs_yoy_zscore_120m`: ADF p=0.0700 (Non-stationary); KPSS p=0.3119 (Fail to reject stationarity).

Recommendation:
Primary transform `nhs_pct_yoy`; robustness set `nhs_yoy_accel_pct`, `nhs_3m_pct_yoy`, `nhs_sa_pct_mom`, `nhs_yoy_zscore_120m`. Treat `nhs_yoy_contraction_flag` as a threshold/regime feature. Monthly lead grid L0..12 per ECON-LL1 with the release-lag floor honored. MANDATORY reverse-causality check (housing can look coincident in places).

Known issues:
- Release dates approximated by a fourth-Tuesday rule, not a historical release-timestamp file.
- Daily indicator is a deliberate monthly step function -> serial dependence in daily OLS-style specs.
- STL SA level uses interpolation across any interior gaps before decomposition.

Questions for recipient:
- None. Set the no-lookahead lead-grid floor at one monthly publication lag.
