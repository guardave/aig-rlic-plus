# Missing Value Report — eci_total_comp_spy (20260706)

Dataset: `data/eci_total_comp_spy_quarterly_20010331_20260331.parquet` — shape (101, 19), QUARTER-END index 2001-03-31 to 2026-03-31 (first quarterly pair in the portal).

## Publication lag & no-lookahead (ECI)

BLS releases the ECI for quarter Q at the END OF THE MONTH FOLLOWING quarter end (end of Jan/Apr/Jul/Oct — ~1 month lag). At quarterly granularity that means the quarter-Q value is only tradable from quarter Q+1. **Evan: the tournament lead grid must FLOOR AT L1, where L is measured in QUARTERS (L1 = 1 quarter ≈ 3 months).** The series is SEASONALLY ADJUSTED, so QoQ and short-horizon transforms are clean — no NSA seasonal-contamination constraint (unlike Cass Freight).

## Few-observations caveat (quarterly frequency)

ECIALLCIV spans 25 years but only 101 quarterly observations. Cycle coverage is good (2001 recession, GFC, COVID, 2021-23 wage surge) but the tournament sample is SMALL. Rolling 20Q z-scores consume ~12 quarters before first value; YoY consumes 4. Any OOS split leaves few OOS quarters — OOS statistics will be high-variance. Flag to Evan for a conservative split and simple specifications; flag to Ray for the durability caveat.

## Missing values by column

| Column | NaN count | Effective obs | Pattern |
|---|---|---|---|
| `eci_total_comp_idx` | 0 | 101 | none |
| `unrate` | 0 | 101 | none |
| `dgs10` | 0 | 101 | none |
| `fed_funds` | 0 | 101 | none |
| `vix` | 0 | 101 | none |
| `spy` | 0 | 101 | none |
| `eci_total_comp_pct_qoq` | 1 | 100 | leading (series/transform starts 2001-06-30) |
| `eci_total_comp_pct_2q` | 2 | 99 | leading (series/transform starts 2001-09-30) |
| `eci_total_comp_pct_yoy` | 4 | 97 | leading (series/transform starts 2002-03-31) |
| `eci_total_comp_ma8q_idx` | 5 | 96 | leading (series/transform starts 2002-06-30) |
| `eci_total_comp_dev_trend_pct` | 5 | 96 | leading (series/transform starts 2002-06-30) |
| `eci_total_comp_zscore_20q` | 11 | 90 | leading (series/transform starts 2003-12-31) |
| `eci_total_comp_yoy_zscore_20q` | 15 | 86 | leading (series/transform starts 2004-12-31) |
| `eci_total_comp_accel_pct` | 2 | 99 | leading (series/transform starts 2001-09-30) |
| `eci_total_comp_yoy_accel_pct` | 5 | 96 | leading (series/transform starts 2002-06-30) |
| `spy_ret` | 1 | 100 | leading (series/transform starts 2001-06-30) |
| `spy_fwd_1q` | 1 | 100 | leading (series/transform starts 2001-03-31); trailing NaN from forward shift |
| `spy_fwd_2q` | 2 | 99 | leading (series/transform starts 2001-03-31); trailing NaN from forward shift |
| `spy_fwd_4q` | 4 | 97 | leading (series/transform starts 2001-03-31); trailing NaN from forward shift |

No internal gaps in `eci_total_comp_idx` (verified). No forward-fill applied. Forward-return columns are NaN at the tail by construction (no leakage).

## Sanity checks (Defense 2)

- 2021-23 wage surge: max YoY 5.11% — PASS (BLS peak ~5.1% mid-2022; real, not an error).
- 2010s regime: YoY 1.77%..2.97% — PASS (expected ~1.5-3%).
- QoQ declines in nominal comp index: 0 (sticky-wage sanity).
- ECI x SPY usable overlap: 2001-03-31 .. 2026-03-31 (101 quarters).
- QoQ outliers (|z|>4): 0 flagged (not removed): none
