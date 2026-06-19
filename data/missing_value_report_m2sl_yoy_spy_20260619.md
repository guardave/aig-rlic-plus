# Missing Value Report - m2sl_yoy_spy (20260619)

Monthly dataset: shape (400, 14), 1993-01-31 to 2026-04-30.
Daily dataset: shape (8403, 19), 1993-01-29 to 2026-06-17.

## Phase 0 / Cross-Check

PASS: Pre-master maps `M2SL` sheet column B to M2SL level and column C to `M2SL_YOY`; descriptions are `M2 Money Supply, monthly, from Federal Reserve` and `M2 Money Supply, monthly, from Federal Reserve YoY%`.
PASS (soft): Data Master M2SL overlap agrees in shape/sign with live FRED. Level corr=0.999998; YoY corr=0.999918; YoY sign agreement=1.000; monthly-change sign agreement=0.996. Revision drift observed: max level diff 108.5000 $bn (0.491%), max YoY diff 0.5195 pp. This is treated as benign seasonal-adjustment/vintage drift per Lead adjudication; FRED live M2SL is the source of truth. Last Data Master row is 2025-08-31: M2SL=22195.4, M2SL_YOY=4.76793%.

## Real-Time Lag

Daily LVCF uses release dates set to the fourth Tuesday of the month following the reference month, approximating the FRED/H.6 M2 release schedule for prior-month data. This implies a no-lookahead floor of roughly 22-28 calendar days after reference month-end.

## Missing Values

| Dataset | Column | NaN count | Note |
|---|---|---:|---|
| monthly | `m2sl_usd` | 0 | none |
| monthly | `m2sl_pct_yoy` | 12 | leading transform / forward-return tail |
| monthly | `m2sl_pct_mom` | 1 | leading transform / forward-return tail |
| monthly | `m2sl_3m_pct` | 3 | leading transform / forward-return tail |
| monthly | `m2sl_6m_pct` | 6 | leading transform / forward-return tail |
| monthly | `m2sl_yoy_accel_pct` | 13 | leading transform / forward-return tail |
| monthly | `m2sl_yoy_zscore_120m` | 71 | leading transform / forward-return tail |
| monthly | `m2sl_contraction_flag` | 0 | none |
| monthly | `spy` | 0 | none |
| monthly | `spy_ret` | 1 | leading transform / forward-return tail |
| monthly | `spy_fwd_1m` | 1 | leading transform / forward-return tail |
| monthly | `spy_fwd_3m` | 3 | leading transform / forward-return tail |
| monthly | `spy_fwd_6m` | 6 | leading transform / forward-return tail |
| monthly | `spy_fwd_12m` | 12 | leading transform / forward-return tail |
| daily | `spy` | 0 | none |
| daily | `reference_month_end` | 0 | none |
| daily | `release_date` | 0 | none |
| daily | `m2sl_usd` | 0 | none |
| daily | `m2sl_pct_yoy` | 0 | none |
| daily | `m2sl_pct_mom` | 0 | none |
| daily | `m2sl_3m_pct` | 0 | none |
| daily | `m2sl_6m_pct` | 0 | none |
| daily | `m2sl_yoy_accel_pct` | 0 | none |
| daily | `m2sl_yoy_zscore_120m` | 0 | none |
| daily | `m2sl_contraction_flag` | 0 | none |
| daily | `days_since_release` | 0 | none |
| daily | `spy_ret` | 1 | leading transform / forward-return tail |
| daily | `spy_fwd_1d` | 1 | leading transform / forward-return tail |
| daily | `spy_fwd_5d` | 5 | leading transform / forward-return tail |
| daily | `spy_fwd_21d` | 21 | leading transform / forward-return tail |
| daily | `spy_fwd_63d` | 63 | leading transform / forward-return tail |
| daily | `spy_fwd_126d` | 126 | leading transform / forward-return tail |
| daily | `spy_fwd_252d` | 252 | leading transform / forward-return tail |

The daily indicator is an intentional release-lagged step function; `days_since_release` documents staleness. The SPY feed returned a missing adjusted close for 2026-06-18 during this run, so the daily panel ends on the last non-missing adjusted close.
