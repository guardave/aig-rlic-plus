# Phase 2 data dictionary (exploratory)

All Phase 2 inputs are point-in-time. They are read through `scripts/p2data.py`.

## Pinned external pulls

| File | Source / series id | Pulled (UTC) | Rows / span | sha256 | Gap | Notes |
|------|--------------------|--------------|-------------|--------|-----|-------|
| `pinned/fred_T10Y3M_20261017.csv` | FRED `T10Y3M` (10-year Treasury constant maturity minus 3-month Treasury constant maturity, daily, percent), via `fredapi` `get_series` | 2026-10-17 17:46 | 11,685 observations, 1982-01-04 .. 2026-10-16 (columns `date,value`; FRED gaps on non-trading days are omitted) | `7bf269c5bd78a19d26172e9d5cb1af6efeacebff632e833bc0457fc8dadd36dc` | G8 (pre-2000 market history; accepted by the Lead 2026-10-17) | Unrevised market data. Used at each month-end close as the value dated the previous trading day (FRED posts it the next business day). |

## Repository inputs (read-only)

| Variable | Source | Point-in-time handling | First month |
|----------|--------|------------------------|-------------|
| `term` | the pinned T10Y3M above | previous trading day's value at the month-end close | 1982-01 |
| `credit` | `data/hy_ig_spy_daily_20000101_20260422.parquet`, columns `hy_oas − ig_oas` (ICE BofA OAS) | previous trading day's value at the month-end close | 2000-01 (last valid month-end 2026-03: the file ends 2026-04-22, before the 2026-04 close). No pre-2000 credit spread is held (gap G16), so every credit model starts its training in 2000-01 |
| `sahm` | ALFRED UNRATE vintages (`data/release_calendar/vintages/UNRATE.csv.gz`) | `_pit_align.realtime_apply` (vintage visible at the close); 3-month average minus the minimum of the prior 12 months' 3-month averages | 1981-04 |
| `permit` | ALFRED PERMIT vintages | `realtime_apply`; YoY % inside the vintage | 1999-08 |
| `sma_flag` | SPY dividend-adjusted month-end closes, `feat261017_phaseB_harness:data/phaseB_inputs/spy_month_end_20261017.csv` (read with `git show`, GIT_* variables unset) | close below its 10-month SMA at the close | 1993-10 |
| NBER recession months | `scripts/_nber.RECESSIONS` (1990+) plus 1980-01..1980-07 and 1981-07..1982-11 (NBER peak/trough dates) | ex-post label only. Training uses a row's label only 12 + 24 months after the row (label window plus a conservative allowance for NBER announcement lags) | 1980 |
| SPY monthly return | the same SPY file, `pct_change` of the adjusted close | return of month t | 1993-02 |
