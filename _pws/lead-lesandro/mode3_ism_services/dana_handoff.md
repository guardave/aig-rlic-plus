Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/ism_services_spy_monthly_latest.parquet` (source dated file `data/ism_services_spy_monthly_19970731_20251031.parquet`)
- Daily LVCF dataset: `data/ism_services_spy_daily_latest.parquet` (source dated file `data/ism_services_spy_daily_19970805_20251105.parquet`)
- Monthly sidecar: `data/ism_services_spy_monthly_schema.json`
- Daily sidecar: `data/ism_services_spy_daily_schema.json`
- Data dictionary: `data/data_dictionary_ism_services_spy_20260618.csv`
- Stationarity: `results/ism_services_spy/stationarity_tests_20260618.csv`
- Interpretation metadata: `results/ism_services_spy/interpretation_metadata.json`

Summary:
Built the ISM Services PMI -> SPY data layer from the project workbook only. The monthly panel is 340 rows x 13 columns, 1997-07-31 to 2025-10-31. The daily panel is 7109 SPY trading days x 18 columns, 1997-08-05 to 2025-11-05, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
PASS: Pre-master maps `ISM PMI` column B to `CDis, CSta - ISM Services PMI`; dictionary row says `ISM Services PMI Monthly, Aug 1997 - Oct 2025`. Workbook data itself runs 1997-07-31 to 2025-10-31.
The workbook headline series covers 1997-07-31 to 2025-10-31. Pre-master labels its coverage as monthly Aug 1997-Oct 2025, but the actual workbook includes a 1997-07-31 first reference-month row and matches the Pre-master sum exactly. I did not include `G - ISM Services PMI, price`; that is reserved for `ism_services_price_xli`.

Units and direction prior:
`ism_services_pmi` is an index-level diffusion index. The natural threshold is 50: values above 50 indicate expansion, below 50 contraction. Direction prior for Evan: procyclical/risk-on for SPY, but empirical direction should decide.

Release lag floor:
Daily LVCF assumes prior-month ISM Services PMI is released on the third business day of the following month. This creates a real-time lag floor of roughly 3-5 calendar days after reference month-end. Do not treat month-end values as tradable before their release dates; daily `days_since_release` is included for staleness modeling.

Stationarity:
Level PMI passes ADF at p=0.0050; KPSS p=0.3293 with conclusion `Fail to reject stationarity`. This is expected for a bounded diffusion index.
See `results/ism_services_spy/stationarity_tests_20260618.csv` for ADF/KPSS on level, delta, 3-month change, z-score, and SPY returns. Recommended primary transform: test level PMI and `ism_services_gap_50` directly because the diffusion index is bounded/mean-reverting; include `ism_services_3m_change` and `ism_services_zscore_60m` as robustness signals. Do not mechanically difference unless diagnostics demand it.

Known issues:
- ISM Services PMI is an offline project-vintage workbook series, not an API-refreshable FRED series.
- Release dates are approximated by the third business day rule; exact historical release timestamps are not encoded.
- Daily indicator values are a deliberate monthly step function and will induce serial dependence in daily OLS-style specifications.

Questions for recipient:
- None. Please confirm whether Evan wants a separate exact-release-calendar enhancement later; current lag-floor handling is sufficient for no-lookahead daily modeling.
