# Data Handoff — pair `phlxsox_spy` (Dana → Evan / Lead)

**Date:** 2026-06-19 · **Branch:** `pair260619_phlxsox_spy` · **Stage:** 1 (data layer)
**Pair:** PHLX Semiconductor Index (`^SOX`) → SPY. **Class:** native-daily **INTERMARKET** (equity index → broad market).

## Files (consume via `_latest` aliases)
| Artifact | Path |
|---|---|
| Daily master | `data/phlxsox_spy_daily_latest.parquet` (dated: `..._19940504_20260617.parquet`) |
| Monthly master | `data/phlxsox_spy_monthly_latest.parquet` (dated: `..._19940531_20260630.parquet`) |
| Daily sidecar (DATA-D5) | `data/phlxsox_spy_daily_schema.json` |
| Monthly sidecar | `data/phlxsox_spy_monthly_schema.json` |
| Interpretation metadata | `results/phlxsox_spy/interpretation_metadata.json` (Dana fields only; Evan/Ray pending) |
| Stationarity | `results/phlxsox_spy/stationarity_tests_20260619.csv` |
| Data dictionary (human) | `data/data_dictionary_phlxsox_spy_20260619.csv` |
| Manifest | `data/manifest.json` (4 additive entries) |
| Registry | `data/display_name_registry.csv` (SOX columns appended; SPY columns reuse existing rows verbatim) |

## Dataset shape & range
- **Daily:** 8,085 rows × 24 cols, **1994-05-04 → 2026-06-17** (common SOX∩SPY trading-day overlap; SPY starts 1993 but SOX from 1994-05). 0 missing in `sox`/`spy`. Forward-return cols NaN-tail by construction (last w rows).
- **Monthly:** 386 rows × 17 cols, **1994-05-31 → 2026-06-30** (month-end resampled `.last()`).

## Units & direction prior
- `sox` = `index`, `spy` = `price` (auto-adjusted). Returns `decimal_return`; momentum `_pct` = `percent`; ratios `ratio`; zscores `ratio`; vol `vol_ann_pct`. All DATA-D2/D12 compliant.
- **Direction prior (hypothesis for Evan):** **procyclical / leading.** Semis are early-cycle, high-beta; SOX strength and SOX/SPY relative strength may lead broad-market SPY. `interpretation_metadata` has `indicator_nature=leading`, `indicator_type=price`.

## Signal transforms provided (the lead-lag toolkit)
- **SOX absolute:** `sox_ret`, `sox_mom_{1m,3m,6m,12m}_pct`, `sox_realized_vol_21d_ann_pct`.
- **SOX/SPY relative strength (the economically interesting candidates):** `sox_spy_ratio`, `sox_spy_logratio`, `sox_spy_ratio_mom_{1m,3m,6m,12m}_pct`, `sox_spy_ratio_zscore_{126d,252d}` (monthly: `_zscore_12m`).
- **Targets:** `spy_fwd_{1,5,21,63,126,252}d` (daily), `spy_fwd_{1,3,6,12}m` (monthly).

## Stationarity verdict
- **Do NOT use levels.** `sox_level` non-stationary (ADF p=1.00; KPSS reject). `sox_spy_ratio` and `sox_spy_logratio` **non-stationary** (ADF p≈0.98/0.82; KPSS reject) — trending; use their momentum/zscore, not the level.
- **Stationary, ADF+KPSS both clean (recommended):** `sox_ret`, `spy_ret`, `sox_mom_{1m,3m,6m}_pct`, `sox_spy_ratio_mom_{3m,6m}_pct`. `sox_mom_12m_pct` ADF-stationary but KPSS borderline (p≈0.05). `sox_spy_ratio_zscore_252d` ADF-stationary, KPSS rejects (slow-moving standardized series — treat with care).
- **Recommended signal set for Evan:** SOX momentum (1m/3m/6m) and SOX/SPY relative-strength momentum (3m/6m), plus the 252d rel-strength z-score as a regime feature.

## Caveats for Evan
1. **No release lag — `days_since_release` is constant 0.** `^SOX` is a continuously-quoted market index, same-day close like SPY. There is **no LVCF step-function and no monthly-release staleness** (contrast the macro pairs). Daily cross-pair default lead is **L0**. The column is retained at 0 only for schema parity; it carries no information.
2. **Equity-vs-equity high contemporaneous correlation — this is NOT the signal.** Daily SOX/SPY return correlation = **0.709**. Both are equities and co-move heavily. A naive contemporaneous regression will look "significant" purely from co-movement. The real question is whether SOX **leads** SPY beyond co-movement — use lead-lag methods (Toda-Yamamoto Granger at L1+, lagged momentum predicting `spy_fwd`, pre-whitened CCF) and lean on the **relative-strength** transforms (which partial out the common equity beta) rather than raw SOX returns.

## Gate results
- **DATA gate (schema validation):** daily sidecar, monthly sidecar, interpretation_metadata, manifest — **all exit 0 (PASS).**
- Display-name verbatim cross-check (sidecar ↔ registry): **no mismatches.**
- `prospective_pairs.csv`: surgical single-cell edit `phlxsox_spy` → `in_progress` (no regen).

## Verification (Defense 2)
- SOX dot-com bust: ratio/level peaked 2000 then collapsed through 2002 — consistent with semis leading lower (recorded in `known_stress_episodes`).
- Contemporaneous corr 0.709 within expected equity-index band.
