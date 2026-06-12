# Handoff: Data Dana -> Econ Evan — busloans_spy (Pair #19, Mode 1)

**Date:** 2026-06-12 · **Branch:** `fix260612_busloans_spy` · **Pair:** `busloans_spy` (I20 C&I Loans → SPY)

## Files

| Artifact | Path |
|---|---|
| Master parquet | `data/busloans_spy_monthly_19470131_20260531.parquet` |
| Stable alias | `data/busloans_spy_monthly_latest.parquet` |
| DATA-D5 sidecar (schema-valid) | `data/busloans_spy_monthly_schema.json` |
| Data dictionary | `data/data_dictionary_busloans_spy_20260612.csv` |
| Summary stats | `data/summary_stats_busloans_spy_20260612.csv` |
| Missing-value report + lag doc | `data/missing_value_report_busloans_spy_20260612.md` |
| Stationarity tests | `results/busloans_spy/stationarity_tests_20260612.csv` |
| Interpretation metadata (schema-valid) | `results/busloans_spy/interpretation_metadata.json` |
| Producer script | `scripts/pair_data_busloans_spy.py` |

## Summary

Monthly pair dataset, shape **953 × 21**, month-end DatetimeIndex 1947-01-31 → 2026-05-31. Indicator: FRED `BUSLOANS` (C&I loans, all commercial banks; monthly average of weekly H.8 Wednesday levels; billions USD; SA; full history, 952 obs through 2026-04). Target: SPY (Yahoo, auto-adjusted month-end close, from 1993-01). Controls: UNRATE, DGS10, DFF (`fed_funds`), VIX — all month-end snapshots, same conventions as `indpro_spy`.

## Column dictionary (transforms)

- `busloans_usd` — level, $bn, SA (unit `usd`; billions documented in description).
- `busloans_pct_yoy` / `busloans_pct_mom` — 12m / 1m % change (effective start 1948-01 / 1947-02).
- `busloans_3m_pct` / `busloans_6m_pct` — 3m / 6m momentum (% change).
- `busloans_ma12_usd`, `busloans_dev_trend_pct` — 12m MA and % deviation from it.
- `busloans_zscore_60m` — rolling 60m z-score of the LEVEL (min 36 obs). Trending series → persistently positive; prefer `busloans_yoy_zscore_60m` (z-score of YoY growth) for cycle signal.
- `busloans_accel_pct` — Δ of MoM growth (pp).
- `busloans_contraction` — 1.0 when YoY < 0.
- `spy_ret`, `spy_fwd_1m/3m/6m/12m` — decimal returns, same forward-target conventions as indpro_spy tournament. SPY columns NaN pre-1993; forward returns NaN at tail (no leakage).

## Lag convention (binding for tradability)

BUSLOANS comes from the weekly H.8 release (Fridays, ~8-day lag); the monthly aggregate (average of Wednesday levels) is available ~2–3 weeks after month-end, and is revised (quarterly Call Report benchmarking). **Use L1 minimum; L1–L2 is the realistic real-time floor.** Monthly indicator default per cross-pair lessons is L6 — test the lag grid as usual.

## DIRECTION-PRIOR WARNING (do not assume procyclical)

`expected_direction` is recorded as **mixed**; `indicator_nature` = **lagging** (C&I loans outstanding is a Conference Board Lagging Economic Index component); `indicator_type` = **credit**.

- Firms draw credit lines INTO downturns: Mar–Apr 2020 loans spiked **+30.1% peak YoY** (verified in the data: 2020-04 = $2,920.9bn, +25.4% YoY; 2020-05 +30.1%) while equities crashed.
- Loan growth peaks after recessions begin and contracts after they end: min YoY 2009–2010 = **−20.2%** (verified), during the equity recovery.
- Naive "rising loans = bullish" may invert at turning points. Determine direction empirically (INDPRO z-score precedent).

## Stationarity (Dana-run; confirm, don't re-run)

Level `busloans_usd`: non-stationary (ADF p≈1.0; KPSS rejects) — use transforms. All growth/momentum/deviation transforms: ADF stationary at 5%; KPSS marginally rejects for most (long-memory in growth rates — treat YoY as borderline; `busloans_yoy_zscore_60m` and `spy_ret` pass both).

## Quirks / known issues

- MoM outliers (|z|>4), flagged not removed: 1952-01 (+5.6%), 2020-03 (+9.1%), 2020-04 (+13.9%).
- No internal gaps in the indicator; no forward-fill applied to it.
- H.8 panel has definitional/coverage breaks over its 79-year span; deep history (pre-1973) predates modern H.8 methodology — consider sample-start sensitivity.
- `spy_ret` is named per the registry ("SPY Daily Return (decimal)") but in this monthly parquet it is a **monthly** return — registry name retained for cross-pair consistency (quirk documented in dictionary).
- Distinct from `ci_loan` (Data Master SLOOS tightening survey) — LEAD-DV1; mislabel fixed in `config/indicator_map.yaml` and `data/prospective_pairs.csv` this wave.
- `strategy_objective: max_sharpe` and `expected_direction: mixed` in interpretation_metadata are Dana-seeded provisional values (schema requires them at creation); Ray owns and finalizes both after the tournament.

## Questions for recipient

None blocking. Acknowledge receipt per SOP.
