Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/housing_starts_spy_monthly_latest.parquet` (source dated file `data/housing_starts_spy_monthly_19900131_20260630.parquet`)
- Daily LVCF dataset: `data/housing_starts_spy_daily_latest.parquet` (source dated file `data/housing_starts_spy_daily_19930129_20260617.parquet`)
- Monthly sidecar: `data/housing_starts_spy_monthly_schema.json`
- Daily sidecar: `data/housing_starts_spy_daily_schema.json`
- Data dictionary: `data/data_dictionary_housing_starts_spy_20260814.csv`
- Missing-value report: `data/missing_value_report_housing_starts_spy_20260814.md`
- Stationarity: `results/housing_starts_spy/stationarity_tests_20260814.csv`
- Interpretation metadata: `results/housing_starts_spy/interpretation_metadata.json`

Summary:
Built the Housing Starts (SAAR) -> SPY data layer from live FRED HOUST. Monthly panel is 438 rows x 14 columns, 1990-01-31 to 2026-06-30. Daily panel is 8403 SPY trading days x 19 columns, 1993-01-29 to 2026-06-17, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
PASS: Pre-master maps sheet `H Started` to 'New Privately-Owned Housing Units Started: Total Units, Thousands of Units, Monthly, Seasonally Adjusted Annual Rate' (verbatim: `New Privately-Owned Housing Units Started: Total Units, Thousands of Units, Monthly, Seasonally Adjusted Annual Rate from FRED`). Confirms FRED HOUST (SAAR, thousands). Distinct from Building Permits (PERMIT/BP) and New Home Sales (HSN1FNSA/nhs, HSN1F/nh_sold_saar).
PASS (soft): Data Master 'RE - H Started' (sheet H Started) agrees with live FRED HOUST. Level corr=0.999978; 93.8% of 800 overlapping months within 1k; max abs diff 25.0k (benign vintage/revision drift). FRED live is source of truth. Last overlap 2025-08-31: FRED=1291k, DataMaster=1307k.

SA handling (contrast with nhs_spy):
HOUST is Seasonally Adjusted (SAAR). NO deseasonalisation needed. `hst_pct_mom` is a valid momentum
input; `hst_pct_yoy` is the primary growth signal. The raw SAAR level `hst_level` is trend-dominated
/ non-stationary and is EXCLUDED from the signal set. Direction prior: procyclical (stronger
construction activity -> risk-on). Counter-channel: at cycle peaks a far-above-trend reading can
mean-revert (INDPRO precedent) — verify empirically.

Release lag floor:
Daily LVCF assumes prior-month starts are released on the ~17th of the following month (Census/HUD
New Residential Construction schedule). No-lookahead floor ~16-19 calendar days after reference month-end.

Stationarity:
- `hst_level`: ADF p=0.5375 (Non-stationary); KPSS p=0.0645 (Fail to reject stationarity).
- `hst_pct_yoy`: ADF p=0.0090 (Stationary at 5%); KPSS p=0.4578 (Fail to reject stationarity).
- `hst_pct_mom`: ADF p=0.0000 (Stationary at 5%); KPSS p=0.4212 (Fail to reject stationarity).
- `hst_3m_pct`: ADF p=0.0002 (Stationary at 5%); KPSS p=0.3735 (Fail to reject stationarity).
- `hst_3m_pct_yoy`: ADF p=0.1574 (Non-stationary); KPSS p=0.4374 (Fail to reject stationarity).
- `hst_yoy_accel_pct`: ADF p=0.0000 (Stationary at 5%); KPSS p=0.6030 (Fail to reject stationarity).
- `hst_yoy_zscore_120m`: ADF p=0.0493 (Stationary at 5%); KPSS p=0.3810 (Fail to reject stationarity).

Recommendation:
Primary transform `hst_pct_yoy`; robustness set `hst_pct_mom`, `hst_3m_pct`, `hst_3m_pct_yoy`,
`hst_yoy_accel_pct`, `hst_yoy_zscore_120m`. Treat `hst_yoy_contraction_flag` as a threshold/regime
feature. Monthly lead grid L0..12 per ECON-LL1 with the release-lag floor honored. MANDATORY
reverse-causality check (housing and equities jointly driven by rates).

Known issues:
- Release dates approximated by a mid-month (~17th) rule, not a historical release-timestamp file.
- Daily indicator is a deliberate monthly step function -> serial dependence in daily OLS-style specs.

Questions for recipient:
- None. Set the no-lookahead lead-grid floor at one monthly publication lag.
