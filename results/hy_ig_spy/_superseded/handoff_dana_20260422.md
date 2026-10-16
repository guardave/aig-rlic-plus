# Dana Handoff — Wave 10G.4A: hy_ig_spy Data Layer

**Date:** 2026-04-22  
**Agent:** Data Dana  
**Wave:** 10G.4A  
**Pair ID:** `hy_ig_spy` (fresh pair; v1 archived to `hy_ig_spy_v1` in Wave 10G.1)

---

## Artifacts Produced

| Artifact | Path | Status |
|----------|------|--------|
| Data pipeline script | `scripts/pair_pipeline_hy_ig_spy.py` | DELIVERED |
| Master daily parquet | `data/hy_ig_spy_daily_20000101_20260422.parquet` | DELIVERED (gitignored per `*.parquet`) |
| Schema sidecar (DATA-D5) | `data/hy_ig_spy_daily_schema.json` | DELIVERED |
| Interpretation metadata (DATA-D6) | `results/hy_ig_spy/interpretation_metadata.json` | DELIVERED |
| Results directory | `results/hy_ig_spy/` | CREATED |
| This handoff note | `results/hy_ig_spy/handoff_dana_20260422.md` | DELIVERED |

---

## META-SRV Evidence

| Metric | Value |
|--------|-------|
| Pipeline script (wc -l) | 1070 lines |
| Parquet rows | 6,863 |
| Parquet columns | 50 |
| Parquet date range | 2000-01-03 to 2026-04-22 |
| Parquet file size | 1.7 MB |
| Schema JSON (wc -c) | 18,409 bytes |
| Schema column count | 50 columns |
| interpretation_metadata.json (wc -l) | 88 lines |
| interpretation_metadata schema validation | PASS |

---

## DATA-D6 Checklist

- [x] `pair_id` = `hy_ig_spy`
- [x] `schema_version` = `1.0.0` (matches `interpretation_metadata.schema.json` x-version)
- [x] `indicator` = `hy_ig_spread_pct`
- [x] `target` = `spy`, `target_symbol` = `SPY`
- [x] `indicator_nature` = `leading` — HY-IG spread leads equity drawdowns (leading per Conference Board / NBER credit-stress literature; consistent with v1/v2 classification)
- [x] `indicator_type` = `credit` — controlled vocabulary, matches Evan's Rule C1 category routing
- [x] `strategy_objective` = `countercyclical_protection` — ex-ante objective (Ray may confirm after tournament in 4C)
- [x] `expected_direction` = `countercyclical` — wider spread → lower SPY returns (canonical)
- [x] `owner_writes` mapping present with all three agents
- [x] `last_updated_by` = `dana`, `last_updated_at` = `2026-04-22T00:00:00Z`
- [x] `related_pair_ids` = `[hy_ig_v2_spy, hy_ig_spy_v1]`
- [x] `known_stress_episodes` populated (5 episodes: dot-com, GFC, ESDC, COVID, 2022)
- [x] `data_provenance` populated with splice note
- [x] Schema validation: PASS (`jsonschema.validate` exit 0)
- [x] `observed_direction` and `confidence` omitted (Evan's fields; not pre-filled by Dana per DATA-D6 field ownership)

---

## DATA-D12 Linter

Pre-save linter run before parquet write. Result: **PASS — all 50 columns conform.**

Notable DATA-D12 decisions in this fresh pair vs. v1/v2:
- `ccc_bb_spread` → renamed `ccc_bb_spread_pct` (unit: percent)
- `yield_spread_10y3m` → renamed `yield_spread_10y3m_pct`
- `yield_spread_10y2y` → renamed `yield_spread_10y2y_pct`
- `bbb_ig_spread` → renamed `bbb_ig_spread_pct`
- Raw FRED rates (`dgs10`, `dtb3`, `dgs2`, `nfci`, `fed_funds_rate`, `fsi`, `initial_claims`, `sofr`) and raw OAS levels (`hy_oas`, `ig_oas`, `bb_hy_oas`, `ccc_hy_oas`, `bbb_oas`) declared SUFFIX_EXEMPT — their units are declared in the DATA-D5 sidecar.

**Evan: downstream signal/tournament code must use the new `_pct`-suffixed column names above. The bare names (`ccc_bb_spread`, `yield_spread_10y3m`, etc.) do NOT exist in this parquet.**

---

## OAS Series Splice (Data Quality Note)

FRED series BAMLH0A0HYM2 (`hy_oas`) and related OAS series (BAMLC0A0CM, BAMLH0A1HYBB, BAMLH0A3HYC, BAMLC0A4CBBB) have `observation_start: 2023-04-24` as of 2026-04-22 fetch. The series appears truncated at source on FRED.

**Resolution:** pre-2023 OAS history back-filled from `data/hy_ig_spy_v1_daily_20000101_20251231.parquet` (the archived Wave 10G.1 v1 data). Splice method: `pd.Series.combine_first()` (live FRED overrides v1 on overlap). Post-splice coverage: 6,872 non-null observations, 2000-01-03 to 2026-04-20. Coverage verified via spot-check against v2 parquet values.

This is the same pattern as the SOFR splice in v2 (SOFR starts 2018-04-03; earlier dates backfilled with Fed Funds proxy). Documented in `data_provenance.splice_note` in interpretation_metadata.json.

---

## META-RYW Re-Read Block

Dana re-read each artifact before handoff:

1. **`scripts/pair_pipeline_hy_ig_spy.py`** — Re-read top-to-bottom. Confirmed:
   - PAIR_ID = `hy_ig_spy` (bare, not v1/v2)
   - `START_DATE = "2000-01-01"`, `END_DATE = today` (2026-04-22)
   - OAS splice logic present with v1 fallback documented
   - DATA-D12 linter called before `to_parquet()` — halts on violation
   - `write_schema()` called after parquet save
   - Column names in derived stage match schema dict entries
   - No references to `hy_ig_v2_spy` or `hy_ig_spy_v1` in output paths

2. **`data/hy_ig_spy_daily_schema.json`** — Re-read. Confirmed:
   - `pair_id` = `hy_ig_spy`, `parquet_path` uses correct `20000101_20260422` date tag
   - All 50 columns have `dtype`, `unit`, `display_name`, `direction`, `description`
   - Unit-suffixed columns (`_pct`, `_ratio`, `_ret`) correctly labeled
   - Exempt raw columns carry `unit: "percent"` or `unit: "index"` as appropriate
   - No column references `hy_ig_v2_spy` or `hy_ig_spy_v1`

3. **`results/hy_ig_spy/interpretation_metadata.json`** — Re-read. Confirmed:
   - Schema validation PASS
   - `indicator_nature: "leading"` — correct for credit spread (leads equity drawdowns)
   - `indicator_type: "credit"` — correct controlled vocabulary
   - `expected_direction: "countercyclical"` — canonical; wider spread = bearish equities
   - `observed_direction` absent (Evan's field)
   - `caveats` array includes the DATA-D12 column-rename notice for Evan
   - `data_provenance.splice_note` accurately describes the FRED truncation
   - `last_updated_by: "dana"` is correct

4. **Parquet spot-check** — Loaded and verified:
   - `hy_ig_spread_pct` range: 0.66 to 15.57 (percent) — plausible; GFC peak ~15%
   - `spy_fwd_63d` non-null count: ~6600 (trailing 63 rows NaN as expected)
   - No `ccc_bb_spread` or `yield_spread_10y3m` bare-name columns present (DATA-D12 rename confirmed)
   - `ccc_bb_spread_pct` and `yield_spread_10y3m_pct` present

---

## Notes for Evan (Wave 10G.4C)

1. Column renames from v1/v2 → fresh pair (DATA-D12 compliance):
   - `ccc_bb_spread` → `ccc_bb_spread_pct`
   - `yield_spread_10y3m` → `yield_spread_10y3m_pct`
   - `yield_spread_10y2y` → `yield_spread_10y2y_pct`
   - `bbb_ig_spread` → `bbb_ig_spread_pct`

2. OAS splice caveat: post-2023 data is live FRED; pre-2023 is from v1 archive. The data is continuous and no gap exists, but the splice boundary is 2023-04-24. If running a structural-break test, consider this date as a potential candidate.

3. `IS_END` / `OOS_START` are not set in the data script — Evan sets these in the econometrics stage per pair-specific decision.

4. `results/hy_ig_spy/` directory is ready for tournament artifacts.

---

*Dana — Wave 10G.4A, 2026-04-22*
