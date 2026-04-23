# Handoff — Evan → Lead (Wave 10I.A schema relaxation)

**Date:** 2026-04-23
**Author:** Econ Evan
**Scope:** Fast-path unblocker for cloud verify 6/41 FAILs on `threshold_value: null`.

## Change summary

File: `docs/schemas/winner_summary.schema.json`

- `threshold_value.type`: `"number"` → `["number", "null"]` (JSON-Schema 2020-12 null-union).
- Description expanded to note: null is tolerated for legacy pairs pending producer-side backfill (`BL-THRESHOLD-VALUE-SCHEMA`); consumers must provide Defense-2 coerce (Ace's `instructional_trigger_cards.py` @ `5f2e50d`).
- `x-version`: `1.0.0` → `1.1.0` (minor bump per META-SCV — additive/tolerant change, backward compatible for producers already emitting numeric threshold).

Diff (conceptual, 3 lines changed):

```
- "x-version": "1.0.0",
+ "x-version": "1.1.0",
...
-   "type": "number",
-   "description": "Numeric threshold ... decision rule."
+   "type": ["number", "null"],
+   "description": "Numeric threshold ... decision rule. `null` is tolerated ... (BL-THRESHOLD-VALUE-SCHEMA) ... Ace's Defense-2 coerce (commit 5f2e50d)."
```

## Smoke evidence

`python3 app/_smoke_tests/smoke_loader.py <pair>` run for all 10 active pairs:

| Pair | passes | failures |
|---|---:|---:|
| dff_ted_spy | 3 | 0 |
| hy_ig_spy | 6 | 0 |
| hy_ig_v2_spy | 15 | 0 |
| indpro_spy | 4 | 0 |
| indpro_xlp | 8 | 0 |
| permit_spy | 3 | 0 |
| sofr_ted_spy | 3 | 0 |
| ted_spliced_spy | 3 | 0 |
| umcsent_xlv | 6 | 0 |
| vix_vix3m_spy | 3 | 0 |

All `failures=0`. Per-run logs in `app/_smoke_tests/loader_{pair}_20260423.log`.

## Additional schema mismatches noticed (FOR LEAD BACKLOG)

During null-scan of all 11 `winner_summary.json` files on disk, I found that the 6 legacy pairs (`dff_ted_spy`, `permit_spy`, `sofr_ted_spy`, `ted_spliced_spy`, `vix_vix3m_spy`, `indpro_spy`) use a **substantially different shape** from the current schema. Example keys from `dff_ted_spy/winner_summary.json`:

```
pair_id, signal_code, signal_display_name, threshold_code, threshold_display_name,
strategy_code, strategy_display_name, strategy_description, lead_value, lead_unit,
lead_description, direction, oos_sharpe, oos_ann_return, max_drawdown, annual_turnover,
win_rate, threshold_value
```

Missing vs schema `required`:
- `generated_at` (ISO 8601 timestamp) — missing from all 6 legacy pairs
- `signal_column` (APP-WS1 canonical parquet column) — missing from all 6
- `target_symbol` — missing from all 6
- `threshold_rule` (enum gt/lt/...) — missing from all 6 (legacy uses `threshold_code` instead)
- `strategy_family` (enum P1/P2/P3) — missing from all 6 (legacy uses `strategy_code`)
- `oos_max_drawdown` — legacy uses bare `max_drawdown`
- `oos_n_trades`, `oos_period_start`, `oos_period_end` — missing from all 6

Extra (unschema'd but tolerated since schema has no `additionalProperties: false`):
- `signal_display_name`, `threshold_code`, `threshold_display_name`, `strategy_code`, `strategy_display_name`, `strategy_description`, `lead_value`, `lead_unit`, `lead_description`, `win_rate` (null in 6 pairs)

**Why smoke still passes:** `smoke_loader.py` tests plotly chart loading, not `validate_or_die` on `winner_summary.json`. The Strategy-page consumer panels (`position_adjustment_panel.py`, `probability_engine_panel.py`) call `validate_or_die`, but those panels are only reached on specific pages. The cloud verify run that flagged `threshold_value: null` as "6/41 FAILs" is presumably not exercising the full schema path for legacy pairs (or those pairs' Strategy pages are gated). If a future wave turns on strict validation uniformly, the 6 legacy pairs will fail on many more fields than just threshold_value.

### Recommended backlog items

1. **BL-THRESHOLD-VALUE-SCHEMA** (already logged @ `12039c9`) — producer-side backfill of numeric `threshold_value` in 6 legacy `winner_summary.json` by reading winning-threshold code from each tournament. Dana+Evan. Unchanged.

2. **NEW: BL-LEGACY-WINNER-SUMMARY-SHAPE** — full normalization of 6 legacy `winner_summary.json` to the current v1.1 schema shape. Touches:
   - Add `generated_at` from tournament artifact mtimes or run logs
   - Resolve `signal_column` (parquet column names) — may require rerunning pair pipelines or reading `signals_*.parquet` headers
   - Map `threshold_code` → `threshold_rule` (enum), `strategy_code` → `strategy_family` (enum)
   - Rename `max_drawdown` → `oos_max_drawdown`; add OOS window metadata
   - Estimated effort: medium (Dana + Evan, ~1 wave)
   - Alternative: generate a producer-side shim that reads legacy shape and emits v1.1-compliant output without rerunning tournaments

3. **NEW: BL-WINNER-SUMMARY-ADDL-PROPS** — decision needed: should schema add `"additionalProperties": false` (strict rejection of legacy extras) or formally declare the legacy-only fields (`signal_display_name`, `lead_value/unit/description`, `win_rate`, etc.) as optional typed properties? Current behavior is permissive-by-omission, which is brittle.

4. **NEW: BL-WIN-RATE-NULL** — minor: `win_rate` is `null` in 7 of 11 pairs. Not declared in schema, so it doesn't break validation, but inconsistent. Decide: (a) add to schema as `["number","null"]`, (b) producer-side backfill, or (c) drop from the artifact.

## Files changed

- `docs/schemas/winner_summary.schema.json` (version + threshold_value type)

## Files NOT changed (per brief scope)

- No `winner_summary.json` data files modified.
- No `app/components/*` modified (Ace's domain).
- No producer/pipeline code modified (`BL-THRESHOLD-VALUE-SCHEMA` deferred).
