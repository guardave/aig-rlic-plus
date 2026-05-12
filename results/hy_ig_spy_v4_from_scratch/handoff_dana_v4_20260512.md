# Handoff: Data Dana → Econ Evan
# Dataset: hy_ig_spy_v4_from_scratch
# Date: 2026-05-12

## Files
- `results/hy_ig_spy_v4_from_scratch/data_hy_ig_spy_v4_20260512.parquet` — monthly aligned dataset
- `results/hy_ig_spy_v4_from_scratch/stationarity_tests_v4_20260512.csv` — ADF + KPSS results
- `results/hy_ig_spy_v4_from_scratch/data_manifest_v4_20260512.json` — provenance manifest

## Summary
Monthly HY-IG credit spread (%) and SPY log returns, 1996-12-31 to 2026-05-29, 354 rows.
Primary OAS source: `data/Data Master.xlsx` sheet `OASHY_IG`, cols B (BAMLH0A0HYM2) and C (BAMLC0A0CM).
Col D (pre-computed spread) explicitly NOT used — spread computed from scratch: hy_oas - ig_oas.
Xlsx ends 2025-10-01. Tail spliced: parquet (2025-10-02 to 2025-12-31) + FRED MCP (2026-01-02 to 2026-05-11).
SPY: yfinance full history 1993-01-29 to 2026-05-11, monthly log return from BME-last close.

## Seam verification
- xlsx/parquet seam 2025-10-01: hy_oas diff=0.0, ig_oas diff=0.0 (exact match)
- parquet/FRED boundary: 2025-12-31 hy_oas=2.81 → 2026-01-02 hy_oas=2.83 (next business day, consistent)

## Quality gates — all 6 PASS
1. Shape: 354 rows (≥330)
2. Date range: 1996-12-31 to 2026-05-29 (both bounds met)
3. Zero NaN: True
4. Spread always positive: True (min=1.52%, max=13.36%)
5. No |spy_log_return| > 0.50: True (max abs=0.1805)
6. Summary stats: mean spread=3.73%, mean SPY monthly log ret=0.0079

## Stationarity
| Variable | Test | Statistic | p-value | Lags | Conclusion |
|----------|------|-----------|---------|------|------------|
| hy_ig_spread_pct level | ADF | -3.3943 | 0.0112 | 15 | Stationary at 5% |
| hy_ig_spread_pct level | KPSS | 0.539 | 0.0318 | 11 | Non-stationary (reject null of stationarity) |
| hy_ig_spread_pct first diff | ADF | -8.5435 | 0.0 | 6 | Stationary at 5% |
| hy_ig_spread_pct first diff | KPSS | 0.0396 | 0.9353 | 4 | Fail to reject stationarity |
| spy_log_return | ADF | -10.1835 | 0.0 | 2 | Stationary at 5% |
| spy_log_return | KPSS | 0.213 | 0.2441 | 3 | Fail to reject stationarity |

Econometric note: HY-IG spread level is likely I(1) (ADF borderline, KPSS rejects stationarity at some samples).
Use first difference or detrended level for Granger causality / predictability tests.
SPY log returns are I(0) — no transformation needed.

## Known issues
None. Prior v4 run failed due to FRED 3-year licensing window. Resolved: xlsx provides full history
back to 1996-12-31; FRED licensing restriction bypassed entirely for the primary sample.
2026 tail (4 months) sourced from FRED MCP after confirming the 3-year window is satisfied.

## Column naming (unchanged from prior v4 — Evan's pipeline requires no changes)
- `hy_ig_spread_pct`: EOM HY-IG OAS level, percent (%). Not basis points.
- `spy_log_return`: monthly log return, dimensionless ratio.
