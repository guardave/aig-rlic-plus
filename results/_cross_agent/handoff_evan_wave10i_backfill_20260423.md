# Handoff — Econ Evan — Wave 10I.A winner_summary v1.1.0 backfill

**Date:** 2026-04-23
**Scope:** Backfill 6 legacy `winner_summary.json` files to schema v1.1.0 (docs/schemas/winner_summary.schema.json).
**Trigger:** Cloud verify reported 10 schema errors each on Strategy pages for these pairs (upstream of Ace's Defense-2 coerce at position_adjustment_panel.py:177).

## Pairs fixed

1. `results/indpro_spy/winner_summary.json`
2. `results/permit_spy/winner_summary.json`
3. `results/vix_vix3m_spy/winner_summary.json`
4. `results/sofr_ted_spy/winner_summary.json`
5. `results/dff_ted_spy/winner_summary.json`
6. `results/ted_spliced_spy/winner_summary.json`

## Validation evidence

### JSON schema validate (jsonschema v1.1.0)

```
indpro_spy: PASS
permit_spy: PASS
vix_vix3m_spy: PASS
sofr_ted_spy: PASS
dff_ted_spy: PASS
ted_spliced_spy: PASS
```

### Smoke loader (`python3 app/_smoke_tests/smoke_loader.py <pair>`)

All six pairs report `# RESULT  passes=N  failures=0`. Logs written under `app/_smoke_tests/loader_<pair>_20260423.log`.

## Field-by-field decisions per pair

| pair | signal_column | threshold_rule | strategy_family | direction | oos_n_trades | oos_ann_return | oos_max_drawdown | oos_period |
|------|---------------|----------------|-----------------|-----------|--------------|----------------|------------------|------------|
| indpro_spy      | `indpro_mom3m`          | `gt` | `P1_long_cash`       | `procyclical`      | 96   | 0.0765 | -0.0807 | 2018-01-01 → 2025-12-31 |
| permit_spy      | `permit_mom1m`          | `gt` | `P3_long_short`      | `procyclical`      | 96   | 0.2266 | -0.1942 | 2018-01-01 → 2025-12-31 |
| vix_vix3m_spy   | `vix_vix3m_ratio_z126`  | `lt` | `P1_long_cash`       | `countercyclical`  | 1566 | 0.1531 | -0.2115 | 2015-01-01 → 2025-12-31 |
| sofr_ted_spy    | `spread_roc_63d`        | `lt` | `P1_long_cash`       | `countercyclical`  | 783  | 0.0815 | -0.0358 | 2015-01-01 → 2025-12-31 |
| dff_ted_spy     | `spread_roc_21d`        | `lt` | `P2_signal_strength` | `countercyclical`  | 1981 | 0.1104 | -0.1471 | 2015-01-01 → 2025-12-31 |
| ted_spliced_spy | `spread_roc_21d`        | `lt` | `P2_signal_strength` | `countercyclical`  | 2088 | 0.1342 | -0.1278 | 2015-01-01 → 2025-12-31 |

Common fields added to all six:
- `schema_version: "1.1.0"`
- `generated_at: "2026-04-23T00:00:00Z"`
- `target_symbol: "SPY"`
- `threshold_value: null` (legacy producers did not emit a numeric; Ace's Defense-2 coerce handles the downstream render fallback; backlog BL-THRESHOLD-VALUE-SCHEMA tracks producer-side backfill)
- `notes` field extended with provenance string (see Judgment calls below)

Unit conversions applied (legacy percent → schema ratio):
- `oos_ann_return`: divided by 100 (e.g. 7.65 → 0.0765; 22.66 → 0.2266)
- legacy `max_drawdown` copied to new `oos_max_drawdown` with /100 (e.g. -19.42 → -0.1942)

Preserved legacy fields (not required by schema but useful for Ace's render code): `signal_code`, `signal_display_name`, `threshold_code`, `threshold_display_name`, `strategy_code`, `strategy_display_name`, `strategy_description`, `lead_value`, `lead_unit`, `lead_description`, `win_rate`, `breakeven_cost_bps`, `max_acceptable_delay_days`, `annual_turnover`.

## Judgment calls Lead should know about

1. **`signal_column` values are synthesized snake_case names** derived from legacy `signal_display_name` + `signal_code`. No pair has a `signals_*.parquet` artifact to sanity-check exact column naming against, since the originals were never emitted. If Ace's consumer code does `pd.read_parquet(...)[signal_column]`, these will raise KeyError — but Strategy pages for these 6 legacy pairs are not currently parquet-dependent (the chart pipeline renders from CSV-based pair_configs). Recommend tracking as a follow-up: the `signal_column` field is a *schema-required contract* here but is not yet a *live consumer path* for these pairs. A future producer rerun should reconcile.

2. **`threshold_rule` inferred, not recovered.** The legacy writers never recorded a comparison operator. I inferred:
   - procyclical + pXX percentile threshold → `gt` (long when signal above threshold)
   - countercyclical + pXX percentile threshold → `lt` (long when signal below threshold)
   This holds for all 6 and is consistent with each pair's strategy intent per their interpretation_metadata.json direction fields (after typo fix). Permit_spy P3_long_short uses `gt` as the "long-side entry" convention.

3. **`direction` enum typos fixed.** Legacy files used `pro_cyclical` / `counter_cyclical` (underscored). Schema requires `procyclical` / `countercyclical`. Normalized in place. No semantic change.

4. **`oos_n_trades` := CSV `oos_n`.** Per task instruction. Worth flagging: the tournament CSV `oos_n` column is the OOS *period count* (rows evaluated), not the discrete-trade count the schema docstring describes ("count of position changes"). Using it satisfies the schema type constraint (integer ≥ 0) and matches the task directive, but Ace/QA should treat the value as a sample-size proxy, not a trade-frequency proxy. Task directive took precedence; flagged here for the record.

5. **OOS window dates reconstructed from default windows.** No `oos_split_record.json` exists for any of the 6 legacy pairs. I applied the defaults specified in the task:
   - Monthly (indpro, permit): `2018-01-01` → `2025-12-31`
   - Daily (vix, sofr_ted, dff_ted, ted_spliced): `2015-01-01` → `2025-12-31`
   Recorded as reconstructed in each file's `notes` field. A producer rerun should replace with exact split boundaries.

6. **`threshold_value` left `null`.** Tournament CSVs do not contain the numeric threshold (only the threshold *code*). Recoverable only by rerunning the threshold computation against the signal distribution, which is out of scope (task forbids tournament rerun). Schema explicitly tolerates null; Ace's Defense-2 handles the render path.

7. **`win_rate` null on 5 of 6 pairs.** Schema does not require win_rate, so left untouched. Only `indpro_spy` had a legacy value (0.1979); preserved.

## Scope compliance (META-NMF, LEAD-DL1)

- Touched: `results/{6 pairs}/winner_summary.json` + this handoff. Nothing else.
- Did NOT touch: `app/components/`, `app/pages/`, schemas, scripts, other agents' artifacts.
- Did NOT rerun tournaments.
- Did NOT fabricate recoverable fields — every uninferable value is annotated in `notes` or left null per schema tolerance.

## Next steps for Lead

- Dispatch QA (Quincy) to re-run cloud verify on Strategy pages for these 6 pairs — expect schema errors cleared.
- Consider a separate work item to emit real `oos_split_record.json` + numeric `threshold_value` for legacy pairs via a targeted producer rerun (backlog BL-THRESHOLD-VALUE-SCHEMA + a new BL-OOS-SPLIT-LEGACY).
