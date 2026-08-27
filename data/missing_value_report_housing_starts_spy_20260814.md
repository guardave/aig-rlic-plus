# Missing Value Report - housing_starts_spy (20260814)

Monthly dataset: shape (438, 14), 1990-01-31 to 2026-06-30.
Daily dataset: shape (8403, 19), 1993-01-29 to 2026-06-17.

## Phase 0 / Cross-Check

PASS: Pre-master maps sheet `H Started` to 'New Privately-Owned Housing Units Started: Total Units, Thousands of Units, Monthly, Seasonally Adjusted Annual Rate' (verbatim: `New Privately-Owned Housing Units Started: Total Units, Thousands of Units, Monthly, Seasonally Adjusted Annual Rate from FRED`). Confirms FRED HOUST (SAAR, thousands). Distinct from Building Permits (PERMIT/BP) and New Home Sales (HSN1FNSA/nhs, HSN1F/nh_sold_saar).
PASS (soft): Data Master 'RE - H Started' (sheet H Started) agrees with live FRED HOUST. Level corr=0.999978; 93.8% of 800 overlapping months within 1k; max abs diff 25.0k (benign vintage/revision drift). FRED live is source of truth. Last overlap 2025-08-31: FRED=1291k, DataMaster=1307k.

## Seasonal Adjustment (SA series)

HOUST is Seasonally Adjusted at an annual rate (SAAR). Unlike HSN1FNSA (NSA), no deseasonalisation is required: `hst_pct_mom` (month-over-month) is a valid momentum input, and `hst_pct_yoy` (12-month change) is the primary growth signal. The raw SAAR level `hst_level` is trend-dominated / non-stationary and is intentionally NOT provided as a signal.

## Real-Time Lag

Daily LVCF uses release dates set to the ~17th of the month following the reference month, approximating the joint Census/HUD New Residential Construction release schedule (~16th-19th). No-lookahead floor ~16-19 calendar days after reference month-end.

## Missing Values

| Dataset | Column | NaN count | Note |
|---|---|---:|---|
| monthly | `hst_level` | 0 | none |
| monthly | `hst_pct_yoy` | 12 | leading transform / forward-return tail |
| monthly | `hst_pct_mom` | 1 | leading transform / forward-return tail |
| monthly | `hst_3m_pct` | 3 | leading transform / forward-return tail |
| monthly | `hst_3m_pct_yoy` | 14 | leading transform / forward-return tail |
| monthly | `hst_yoy_accel_pct` | 13 | leading transform / forward-return tail |
| monthly | `hst_yoy_zscore_120m` | 71 | leading transform / forward-return tail |
| monthly | `hst_yoy_contraction_flag` | 0 | none |
| monthly | `spy` | 36 | leading transform / forward-return tail |
| monthly | `spy_ret` | 37 | leading transform / forward-return tail |
| monthly | `spy_fwd_1m` | 37 | leading transform / forward-return tail |
| monthly | `spy_fwd_3m` | 39 | leading transform / forward-return tail |
| monthly | `spy_fwd_6m` | 42 | leading transform / forward-return tail |
| monthly | `spy_fwd_12m` | 48 | leading transform / forward-return tail |
| daily | `spy` | 0 | none |
| daily | `reference_month_end` | 0 | none |
| daily | `release_date` | 0 | none |
| daily | `hst_level` | 0 | none |
| daily | `hst_pct_yoy` | 0 | none |
| daily | `hst_pct_mom` | 0 | none |
| daily | `hst_3m_pct` | 0 | none |
| daily | `hst_3m_pct_yoy` | 0 | none |
| daily | `hst_yoy_accel_pct` | 0 | none |
| daily | `hst_yoy_zscore_120m` | 0 | none |
| daily | `hst_yoy_contraction_flag` | 0 | none |
| daily | `days_since_release` | 0 | none |
| daily | `spy_ret` | 1 | leading transform / forward-return tail |
| daily | `spy_fwd_1d` | 1 | leading transform / forward-return tail |
| daily | `spy_fwd_5d` | 5 | leading transform / forward-return tail |
| daily | `spy_fwd_21d` | 21 | leading transform / forward-return tail |
| daily | `spy_fwd_63d` | 63 | leading transform / forward-return tail |
| daily | `spy_fwd_126d` | 126 | leading transform / forward-return tail |
| daily | `spy_fwd_252d` | 252 | leading transform / forward-return tail |
