# Missing Value Report - ism_services_spy (20260618)

Monthly dataset: shape (340, 13), 1997-07-31 to 2025-10-31.
Daily dataset: shape (7109, 18), 1997-08-05 to 2025-11-05.

## Phase 0 / Source Check

PASS: Pre-master maps `ISM PMI` column B to `CDis, CSta - ISM Services PMI`; dictionary row says `ISM Services PMI Monthly, Aug 1997 - Oct 2025`. Workbook data itself runs 1997-07-31 to 2025-10-31.

The adjacent `G - ISM Services PMI, price` column is intentionally excluded; it belongs to `ism_services_price_xli`.

## Real-Time Lag

Daily LVCF uses release dates set to the third business day of the month following the reference month. This approximates the ISM Services release calendar and implies a real-time lag floor of about 3-5 calendar days after reference month-end.

## Missing Values

| Dataset | Column | NaN count | Note |
|---|---|---:|---|
| monthly | `ism_services_pmi` | 0 | none |
| monthly | `ism_services_gap_50` | 0 | none |
| monthly | `ism_services_delta` | 1 | leading transform / forward-return tail |
| monthly | `ism_services_3m_change` | 3 | leading transform / forward-return tail |
| monthly | `ism_services_6m_change` | 6 | leading transform / forward-return tail |
| monthly | `ism_services_zscore_60m` | 35 | leading transform / forward-return tail |
| monthly | `ism_services_above_50` | 0 | none |
| monthly | `spy` | 0 | none |
| monthly | `spy_ret` | 1 | leading transform / forward-return tail |
| monthly | `spy_fwd_1m` | 1 | leading transform / forward-return tail |
| monthly | `spy_fwd_3m` | 3 | leading transform / forward-return tail |
| monthly | `spy_fwd_6m` | 6 | leading transform / forward-return tail |
| monthly | `spy_fwd_12m` | 12 | leading transform / forward-return tail |
| daily | `spy` | 0 | none |
| daily | `reference_month_end` | 0 | none |
| daily | `release_date` | 0 | none |
| daily | `ism_services_pmi` | 0 | none |
| daily | `days_since_release` | 0 | none |
| daily | `ism_services_gap_50` | 0 | none |
| daily | `ism_services_delta` | 20 | leading transform / forward-return tail |
| daily | `ism_services_3m_change` | 65 | leading transform / forward-return tail |
| daily | `ism_services_6m_change` | 126 | leading transform / forward-return tail |
| daily | `ism_services_zscore_60m` | 735 | leading transform / forward-return tail |
| daily | `ism_services_above_50` | 0 | none |
| daily | `spy_ret` | 1 | leading transform / forward-return tail |
| daily | `spy_fwd_1d` | 1 | leading transform / forward-return tail |
| daily | `spy_fwd_5d` | 5 | leading transform / forward-return tail |
| daily | `spy_fwd_21d` | 21 | leading transform / forward-return tail |
| daily | `spy_fwd_63d` | 63 | leading transform / forward-return tail |
| daily | `spy_fwd_126d` | 126 | leading transform / forward-return tail |
| daily | `spy_fwd_252d` | 252 | leading transform / forward-return tail |

No internal gaps in the ISM Services PMI headline series. The daily indicator is an intentional release-lagged step function; `days_since_release` documents staleness.
