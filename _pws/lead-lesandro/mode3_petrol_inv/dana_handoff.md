# Handoff: Data Dana -> Econ Evan — petrol_inv_spy

**Date:** 2026-06-17  
**Branch:** `pair260617_petrol_inv_spy`  
**Pair:** `petrol_inv_spy` — Petroleum Inventory (`petrol_inv`, EIA/FRED `WTTSTUS1`) -> SPY

## Files

| Artifact | Path |
|---|---|
| Monthly master alias | `data/petrol_inv_spy_monthly_latest.parquet` |
| Monthly dated master | `data/petrol_inv_spy_monthly_19900131_20250930.parquet` |
| Daily LVCF alias | `data/petrol_inv_spy_daily_latest.parquet` |
| Daily LVCF dated master | `data/petrol_inv_spy_daily_19930129_20251008.parquet` |
| Monthly DATA-D5 sidecar | `data/petrol_inv_spy_monthly_schema.json` |
| Daily DATA-D5 sidecar | `data/petrol_inv_spy_daily_schema.json` |
| Human data dictionary | `data/data_dictionary_petrol_inv_spy_20260617.csv` |
| Summary stats | `data/summary_stats_petrol_inv_spy_monthly_20260617.csv`, `data/summary_stats_petrol_inv_spy_daily_20260617.csv` |
| Missing-value / lag report | `data/missing_value_report_petrol_inv_spy_20260617.md` |
| Stationarity tests | `results/petrol_inv_spy/stationarity_tests_20260617.csv` |
| Interpretation metadata | `results/petrol_inv_spy/interpretation_metadata.json` |
| Producer script | `scripts/pair_data_petrol_inv_spy.py` |

## Summary

Built both required panels for the first weekly-native indicator in the project. Monthly panel is **429 x 18**, month-end DatetimeIndex **1990-01-31 -> 2025-09-30**, with WTTSTUS1 aggregated as the calendar-month mean of weekly ending stocks. Daily panel is **8,230 x 23**, trading-day DatetimeIndex **1993-01-29 -> 2025-10-08**, with release-lagged LVCF from the weekly series and an explicit `days_since_release` column.

Phase 0 gate passed: Data Master `Pre-master` column AN / 1-based column 40 confirms WTTSTUS1 as "Weekly U.S. Ending Stocks of Crude Oil and Petroleum Products (Thousand Barrels), From: EIA." The catalog's "col 39" appears zero-based. FRED's public API rejected `WTTSTUS1` on 2026-06-17, so I used the project-audited `data/Data Master.xlsx` WTTSTUS1 sheet; units/source agree with the brief and catalog.

## Units / Direction Prior / Classification

- Core indicator unit: `petrol_inv_kb` = **thousand barrels** (`unit=count` in sidecar; display name clarifies kb).
- Pair classification: **Cross-Asset / physical commodity stock** for research classification. Schema-level `indicator_type` is `macro` because the current controlled enum has no physical-inventory value.
- `indicator_nature`: `coincident`.
- Direction prior: **mixed / ambiguous** for SPY. Higher inventories can mean looser supply or weaker demand; estimate sign empirically.

## Lag Floor

Daily LVCF uses `release_date = report_week_end + 5 calendar days`, matching EIA Wednesday release for prior-week data. **Do not let the tournament test leads shorter than this real-time availability floor.** For daily models, use at least a **5-trading-day / one-week lag floor** before a WTTSTUS1 value can affect trades. Monthly models should also avoid same-month lookahead because the month contains multiple weekly releases.

## Stationarity

Levels are non-stationary:

- `monthly_level`: ADF p=0.0896; KPSS p=0.0001 -> non-stationary.
- `weekly_level`: ADF p=0.0960; KPSS p=0.0001 -> non-stationary.

Transforms that pass both ADF and KPSS at 5%:

- Monthly: `monthly_delta`, `monthly_pct_chg`, `monthly_yoy`, `monthly_yoy_zscore`.
- Weekly: `weekly_delta`, `weekly_pct_chg_4w`, `weekly_yoy`.

Recommended signal set: `petrol_inv_pct_yoy`, `petrol_inv_yoy_zscore_60m`, and `petrol_inv_dev_trend_pct`. Avoid raw `petrol_inv_kb` except for diagnostics; petroleum stocks have strong refinery/driving-season seasonality and a secular trend.

## Known Issues

- Daily indicator columns are intentional step functions. `days_since_release` is included so staleness can be modeled rather than hidden.
- The Data Master WTTSTUS1 sheet ends at report week **2025-10-03**; monthly panel stops at the last complete month, **2025-09-30**. Daily panel stops at the corresponding release date, **2025-10-08**, and does not carry the final value forward beyond the last known release.
- `prospective_pairs.csv` was surgically edited: only `petrol_inv_spy` status changed from `not_started` to `in_progress`; `build_prospective_pairs.py` was not run.

## Validation

All producer-side gates passed:

```bash
python3 scripts/validate_schema.py --schema docs/schemas/data_subject.schema.json --instance data/petrol_inv_spy_monthly_schema.json
python3 scripts/validate_schema.py --schema docs/schemas/data_subject.schema.json --instance data/petrol_inv_spy_daily_schema.json
python3 scripts/validate_schema.py --schema docs/schemas/interpretation_metadata.schema.json --instance results/petrol_inv_spy/interpretation_metadata.json
python3 scripts/validate_schema.py --schema docs/schemas/data_manifest.schema.json --instance data/manifest.json
```

Each exited 0. `scripts/pair_data_petrol_inv_spy.py` printed `DANA DONE` with the artifact list.

## Questions for recipient

None blocking. Please confirm the daily lag floor is reflected in the lead-grid construction.
