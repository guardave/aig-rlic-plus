# Missing Value Report — wells_fargo_housing_spy (20260706)

Dataset: `data/wells_fargo_housing_spy_monthly_19850131_20251031.parquet` — shape (490, 23), month-end index 1985-01-31 to 2025-10-31.

## Publication lag & no-lookahead (NAHB HMI)

NAHB releases the HMI mid-month (~16th-18th) FOR the CURRENT reference month — a survey with effectively ZERO publication lag. The month-M value is known intra-month M, before month-end M. **Evan: L1 is the safe/conservative real-time floor at monthly granularity; even L0-at-month-end is defensible (value is public ~2 weeks before month-end), but start the lead grid at L1 per project convention.** The series is seasonally adjusted by NAHB — no seasonal contamination of MoM/short-horizon transforms.

## Bounded-index caveat

The HMI is a bounded 0-100 diffusion index (50 = neutral). Percent-change transforms are level-dependent (a move from 8 to 16 is '+100%'); the LEVEL itself and point-change transforms (`nahb_hmi_diff_3m`, `nahb_hmi_diff_12m`) are the natural signal family. Percent-change columns are included for family consistency but flagged.

## Missing values by column

| Column | NaN count | Pattern |
|---|---|---|
| `nahb_hmi` | 0 | none |
| `unrate` | 1 | leading (series/transform starts 1985-01-31) |
| `dgs10` | 0 | none |
| `fed_funds` | 0 | none |
| `vix` | 60 | leading (series/transform starts 1990-01-31) |
| `spy` | 96 | leading (series/transform starts 1993-01-31) |
| `nahb_hmi_pct_yoy` | 12 | leading (series/transform starts 1986-01-31) |
| `nahb_hmi_pct_mom` | 1 | leading (series/transform starts 1985-02-28) |
| `nahb_hmi_3m_pct` | 3 | leading (series/transform starts 1985-04-30) |
| `nahb_hmi_6m_pct` | 6 | leading (series/transform starts 1985-07-31) |
| `nahb_hmi_diff_12m` | 12 | leading (series/transform starts 1986-01-31) |
| `nahb_hmi_diff_3m` | 3 | leading (series/transform starts 1985-04-30) |
| `nahb_hmi_ma12_idx` | 9 | leading (series/transform starts 1985-10-31) |
| `nahb_hmi_dev_trend_pct` | 9 | leading (series/transform starts 1985-10-31) |
| `nahb_hmi_zscore_60m` | 35 | leading (series/transform starts 1987-12-31) |
| `nahb_hmi_diff12_zscore_60m` | 47 | leading (series/transform starts 1988-12-31) |
| `nahb_hmi_accel_pct` | 2 | leading (series/transform starts 1985-03-31) |
| `nahb_hmi_above50` | 0 | none |
| `spy_ret` | 97 | leading (series/transform starts 1993-02-28) |
| `spy_fwd_1m` | 97 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_3m` | 99 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_6m` | 102 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |
| `spy_fwd_12m` | 108 | leading (series/transform starts 1993-01-31); trailing NaN from forward shift |

No internal gaps in `nahb_hmi` (verified: 490 consecutive months). No forward-fill applied to the indicator. SPY/VIX have leading NaNs (SPY inception 1993-01; VIX 1990) — the usable pair overlap window starts at SPY inception. Forward-return columns are NaN at the tail by construction (no leakage).

## Sanity checks (Defense 2)

- GFC trough: Jan-2009 HMI = 8 — PASS (published record low).
- COVID whipsaw: Apr-2020 = 30, Nov-2020 = 90 (record high) — PASS.
- 2022 rate-shock collapse: 83 (Jan) -> 31 (Dec) — PASS.
- Bounds: min 8 / max 90 within 0-100 — PASS.
- HMI x SPY usable overlap: 1993-01-31 .. 2025-10-31 (394 months).
- 1M point-change outliers (|z|>4): 2 flagged (not removed): 2020-04-30 (-42 pts), 2020-06-30 (+21 pts)
