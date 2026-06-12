# Missing Value Report — busloans_spy (20260612)

Dataset: `data/busloans_spy_monthly_19470131_20260531.parquet` — shape (953, 21), month-end index 1947-01-31 to 2026-05-31.

## Publication lag (BUSLOANS)

BUSLOANS is derived from the Fed H.8 release (Assets and Liabilities of Commercial Banks, weekly, published each Friday with ~8-day lag). The monthly BUSLOANS observation is the average of weekly Wednesday levels and becomes available roughly 2-3 weeks after month-end. **Evan: lag the indicator by at least 1 month (L1) for real-time tradability; L1-L2 is the realistic floor.** H.8 data are also revised (benchmarked to Call Reports quarterly).

## Missing values by column

| Column | NaN count | Pattern |
|---|---|---|
| `busloans_usd` | 1 | leading (series starts 1947-01-31) |
| `unrate` | 13 | leading (series starts 1948-01-31) |
| `dgs10` | 180 | leading (series starts 1962-01-31) |
| `fed_funds` | 90 | leading (series starts 1954-07-31) |
| `vix` | 516 | leading (series starts 1990-01-31) |
| `spy` | 552 | leading (series starts 1993-01-31) |
| `busloans_pct_yoy` | 13 | leading (series starts 1948-01-31) |
| `busloans_pct_mom` | 2 | leading (series starts 1947-02-28) |
| `busloans_3m_pct` | 4 | leading (series starts 1947-04-30) |
| `busloans_6m_pct` | 7 | leading (series starts 1947-07-31) |
| `busloans_ma12_usd` | 9 | leading (series starts 1947-10-31) |
| `busloans_dev_trend_pct` | 10 | leading (series starts 1947-10-31) |
| `busloans_zscore_60m` | 36 | leading (series starts 1949-12-31) |
| `busloans_yoy_zscore_60m` | 48 | leading (series starts 1950-12-31) |
| `busloans_accel_pct` | 3 | leading (series starts 1947-03-31) |
| `busloans_contraction` | 0 | none |
| `spy_ret` | 553 | leading (series starts 1993-02-28) |
| `spy_fwd_1m` | 553 | leading (series starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_3m` | 555 | leading (series starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_6m` | 558 | leading (series starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_12m` | 564 | leading (series starts 1993-01-31); trailing NaN from forward shift |

No internal gaps in `busloans_usd` (verified). No forward-fill applied to the indicator. SPY columns are NaN before SPY inception (1993-01); forward-return columns are NaN at the tail by construction (no leakage).

## Sanity checks (Defense 2)

- COVID credit-line drawdown spike: peak YoY 30.1% (Apr-Jun 2020) — PASS (expected ~+25-30%).
- GFC contraction: min YoY 2009-2010 = -20.2% — PASS (lagging contraction confirmed).
- Units: latest level $2,874bn — consistent with billions-USD, SA.
- MoM outliers (|z|>4): 3 flagged (not removed): 1952-01-31 (+5.6%), 2020-03-31 (+9.1%), 2020-04-30 (+13.9%)
