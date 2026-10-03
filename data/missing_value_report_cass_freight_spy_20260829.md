# Missing Value Report — cass_freight_spy (20260829)

Dataset: `data/cass_freight_spy_monthly_19900131_20260731.parquet` — shape (439, 21), month-end index 1990-01-31 to 2026-07-31.

## Publication lag & no-lookahead (Cass Freight)

The Cass Freight Index (Shipments) is published ~mid-month for the prior month (roughly a 2-week lag), and FRED carries it stamped to the Cass **processing** month (not the physical shipment month). **Evan: lag the indicator by at least 1 month (L1) for real-time tradability; L1 is the realistic floor.** The series is NOT seasonally adjusted (NSA): YoY-family transforms are seasonality-robust; MoM / 3m / 6m momentum and the level z-score carry a seasonal pattern — prefer the YoY-family signals for cycle inference.

## Short-history caveat

FRED FRGSHPUSM649NCIS starts 2016-01 (~439 monthly rows to 2026-07-31). This is a SHORT sample: only ~10 years, one full freight cycle plus COVID. The rolling 60-month z-score signals do not become valid until ~2018-12 (level) / ~2019-12 (YoY), and any OOS window will be very short (< 5yr) — OOS Sharpe will be inflated/high-variance. Flag to Evan for a conservative OOS split and to Ray for the durability caveat.

## Missing values by column

| Column | NaN count | Pattern |
|---|---|---|
| `cass_freight_idx` | 0 | none |
| `unrate` | 37 | leading (series/transform starts 1993-01-31) |
| `dgs10` | 36 | leading (series/transform starts 1993-01-31) |
| `fed_funds` | 36 | leading (series/transform starts 1993-01-31) |
| `vix` | 36 | leading (series/transform starts 1993-01-31) |
| `spy` | 36 | leading (series/transform starts 1993-01-31) |
| `cass_freight_pct_yoy` | 12 | leading (series/transform starts 1991-01-31) |
| `cass_freight_pct_mom` | 1 | leading (series/transform starts 1990-02-28) |
| `cass_freight_3m_pct` | 3 | leading (series/transform starts 1990-04-30) |
| `cass_freight_6m_pct` | 6 | leading (series/transform starts 1990-07-31) |
| `cass_freight_ma12_idx` | 9 | leading (series/transform starts 1990-10-31) |
| `cass_freight_dev_trend_pct` | 9 | leading (series/transform starts 1990-10-31) |
| `cass_freight_zscore_60m` | 35 | leading (series/transform starts 1992-12-31) |
| `cass_freight_yoy_zscore_60m` | 47 | leading (series/transform starts 1993-12-31) |
| `cass_freight_accel_pct` | 2 | leading (series/transform starts 1990-03-31) |
| `cass_freight_contraction` | 0 | none |
| `spy_ret` | 37 | leading (series/transform starts 1993-02-28) |
| `spy_fwd_1m` | 37 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_3m` | 39 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_6m` | 42 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_12m` | 48 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |

No internal gaps in `cass_freight_idx` (verified). No forward-fill applied to the indicator. Forward-return columns are NaN at the tail by construction (no leakage).

## Sanity checks (Defense 2)

- COVID freight collapse: trough YoY -23.6% (Apr-Jul 2020) — PASS (expected strongly negative).
- 2022-2024 freight recession: min YoY -10.6% — PASS (goods slowdown confirmed).
- Units: latest level 0.983 — consistent with Cass index (Jan1990=1.00), NSA.
- Cass x SPY usable overlap: 1993-01-31 .. 2026-07-31 (403 months).
- MoM outliers (|z|>4): 0 flagged (not removed): 
