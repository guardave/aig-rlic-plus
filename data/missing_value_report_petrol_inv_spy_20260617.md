# Missing Value Report - petrol_inv_spy (20260617)

Monthly dataset: `data/petrol_inv_spy_monthly_19900131_20250930.parquet` shape (429, 18), 1990-01-31 to 2025-09-30.
Daily dataset: `data/petrol_inv_spy_daily_19930129_20251008.parquet` shape (8230, 23), 1993-01-29 to 2025-10-08.

## Phase 0 / Source Check

Pre-master column 40 (AN1) confirms: Weekly U.S. Ending Stocks of Crude Oil and Petroleum Products (Thousand Barrels)

From: EIA

FRED public API rejected `WTTSTUS1` on 2026-06-17; the project-audited `data/Data Master.xlsx` sheet `WTTSTUS1` was used. Pre-master units/source agree with the dispatch brief and catalog.

## Real-Time Lag

Daily LVCF uses `release_date = report_week_end + 5 calendar days`, matching the EIA Wednesday release for prior-week data. Evan should not test leads shorter than this availability floor; use at least a 5-trading-day / one-week floor for daily models.

## Missing Values

| Dataset | Column | NaN count | Note |
|---|---|---:|---|
| monthly | `petrol_inv_kb` | 0 | none |
| monthly | `petrol_inv_pct_yoy` | 12 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_pct_chg` | 1 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_3m_pct` | 3 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_6m_pct` | 6 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_ma12_kb` | 9 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_dev_trend_pct` | 9 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_zscore_60m` | 35 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_yoy_zscore_60m` | 47 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `petrol_inv_accel_pct` | 2 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `spy` | 36 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `vix` | 36 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `dgs10` | 0 | none |
| monthly | `spy_ret` | 37 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `spy_fwd_1m` | 37 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `spy_fwd_3m` | 39 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `spy_fwd_6m` | 42 | leading transform / SPY pre-inception / forward-return tail |
| monthly | `spy_fwd_12m` | 48 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy` | 0 | none |
| daily | `vix` | 0 | none |
| daily | `dgs10` | 0 | none |
| daily | `report_week_end` | 0 | none |
| daily | `release_date` | 0 | none |
| daily | `petrol_inv_kb` | 0 | none |
| daily | `days_since_release` | 0 | none |
| daily | `petrol_inv_pct_yoy` | 0 | none |
| daily | `petrol_inv_pct_chg` | 0 | none |
| daily | `petrol_inv_3m_pct` | 0 | none |
| daily | `petrol_inv_6m_pct` | 0 | none |
| daily | `petrol_inv_ma12_kb` | 0 | none |
| daily | `petrol_inv_dev_trend_pct` | 0 | none |
| daily | `petrol_inv_zscore_60m` | 0 | none |
| daily | `petrol_inv_yoy_zscore_60m` | 231 | leading transform / SPY pre-inception / forward-return tail |
| daily | `petrol_inv_accel_pct` | 0 | none |
| daily | `spy_ret` | 1 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy_fwd_1d` | 1 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy_fwd_5d` | 5 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy_fwd_21d` | 21 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy_fwd_63d` | 63 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy_fwd_126d` | 126 | leading transform / SPY pre-inception / forward-return tail |
| daily | `spy_fwd_252d` | 252 | leading transform / SPY pre-inception / forward-return tail |

No internal gaps in WTTSTUS1. The daily indicator is an intentional step function; `days_since_release` documents staleness.

## Stationarity Verdict

Petroleum inventory levels are non-stationary and visibly seasonal/trending. Recommended signals for Evan: `petrol_inv_pct_yoy`, `petrol_inv_yoy_zscore_60m`, and `petrol_inv_dev_trend_pct`; avoid raw levels except as diagnostics.
