# QA Verification — Wave 10B — Combined Summary (2026-04-20)
QA Agent: Quincy | Gate: GATE-31

## Pairs covered
- `umcsent_xlv` — UMCSENT Consumer Sentiment → XLV Healthcare ETF
- `indpro_xlp` — INDPRO Industrial Production → XLP Consumer Staples ETF

## Wave verdict: BLOCK

Neither pair passes GATE-31. Both are blocked on the same family of schema contract violations. The violations are structural (artifact format does not match schema) not data-quality (underlying econometrics are internally consistent).

---

## Aggregate results

| Pair | Checks | PASS | PASS-with-note | FAIL | Blocking | Verdict |
|------|--------|------|----------------|------|----------|---------|
| umcsent_xlv | 22 | 14 | 2 | 6 | 6 | BLOCK |
| indpro_xlp | 22 | 14 | 2 | 6 | 6 | BLOCK |
| **Wave total** | **44** | **28** | **4** | **12** | **12** | **BLOCK** |

---

## Cross-pair pattern analysis

### Pattern A — winner_summary.json: systematic schema under-population

Both pairs produce a winner_summary.json that contains the core KPIs (Sharpe, return, vol, drawdown in correct ratio form) but omits required schema contract fields:

| Missing field | umcsent_xlv | indpro_xlp | Schema source |
|---------------|------------|------------|--------------|
| `generated_at` | absent | absent | ECON-H5 / winner_summary.schema.json |
| `signal_column` | absent | absent | Required for APP-WS1 parquet resolution |
| `signal_code` | uses `signal` key | uses `winner_signal` key | Field name mismatch |
| `target_symbol` | absent | absent | Required for KPI card labelling |
| `threshold_value` | absent | absent | Required for decision-rule rendering |
| `threshold_rule` | absent | absent | Required for decision-rule rendering |
| `strategy_family` | uses `strategy` key | uses `winner_strategy` key + `_counter` suffix | Enum mismatch |
| `direction` | absent | absent | Required for APP-DIR1 check |
| `oos_max_drawdown` | uses `max_drawdown` (BL-801) | PASS (correct name) | Pre-existing BL-801 |
| `oos_n_trades` | absent | absent | Required by schema |
| `oos_period_start` | absent | absent | Required for OOS window labelling |
| `oos_period_end` | absent | absent | Required for OOS window labelling |

Root cause: Pipeline scripts for these pairs (likely `scripts/pair_pipeline_umcsent_xlv.py` and `scripts/pair_pipeline_indpro_xlp.py`) write winner_summary.json using an older/informal key structure rather than the canonical schema. The schema has been extended since earlier pairs; these new pipelines did not adopt the current schema.

**Recommended fix:** Evan must update both pipeline scripts to emit all required schema fields. `docs/schemas/winner_summary.schema.json` is the source of truth.

### Pattern B — signal_scope.json: legacy flat-array structure

Both pairs produce a signal_scope.json that lists derivatives as flat arrays (`in_scope_indicator_signals`, `in_scope_target_signals`) rather than the structured `indicator_axis` / `target_axis` axis_block objects required by `signal_scope.schema.json`. The schema requires:
- `indicator_axis.canonical_column`, `indicator_axis.display_name`, `indicator_axis.derivatives[]` (each with `name`, `definition`, `formula`, `role`, `appears_in_charts`)
- `target_axis` — same structure
- `owner: "evan"` (required const)

Root cause: Same as Pattern A — pipeline scripts use a deprecated flat-list schema.

### Pattern C — analyst_suggestions.json: mismatched vocabulary

Both pairs produce analyst_suggestions.json with entry fields that do not conform to the current schema:
- umcsent_xlv: entries use `signal`, `description`, `note`, `pearson_r` — none are schema fields.
- indpro_xlp: top-level key is `candidates` not `suggestions`; entries use `series`, `description`, `pearson_r`, `p_value`.

Required schema fields per entry: `signal_name`, `proposed_by`, `source`, `observation`, `rationale`, `possible_use_case`, `caveats`, `date_filed`.

Root cause: Same pipeline script schema lag.

### Pattern D — smoke_loader.py: GATE-27 harness gap (new finding, file as BL-803)

`smoke_loader.py` was built for `hy_ig_v2_spy` (page prefix `9_`) and hardcodes EVIDENCE_DYNAMIC_CHARTS with HY-IG v2 chart names. For pairs with page prefix `10_` (umcsent_xlv) or `14_` (indpro_xlp), the page scan returns 0 pages, and the dynamic chart checks all fail because the chart names are HY-IG-specific. This is a test harness gap, not a pipeline failure.

**Recommended fix:** Either (a) generalize `smoke_loader.py` to accept page prefix as a parameter and dynamically derive EVIDENCE_DYNAMIC_CHARTS from the pair's chart JSON filenames, or (b) create a per-pair smoke_loader configuration. File as BL-803 with priority Normal (it degrades the GATE-27 signal for all future pairs).

---

## Items that are CLEAR (no blocking issues)

- **Econometric KPIs are internally consistent** for both pairs. Sharpe/return/vol triangulation is exact for indpro_xlp and within 0.1 pp for umcsent_xlv.
- **META-UC (ratio form)** PASS for both pairs. No percent-scale contamination in winner_summary.json.
- **Data files present**: monthly parquet confirmed for both pairs. indpro_xlp additionally has daily parquet.
- **Chart JSONs**: 10 charts each, all non-empty. File sizes (8–281 KB) consistent with substantive content.
- **Portal pages**: 4 pages each, correct prefix numbering (`10_` and `14_`).
- **Pair registry**: both pairs load correctly.
- **interpretation_metadata.json**: schema conformance PASS for both pairs (DATA-D6 gate).
- **winner_trade_log.csv**: 81 and 84 data rows respectively — not header-only.
- **Agent memory (GATE-27 portion)**: Evan's session is documented with Wave 10 content. Home-dir permission block is a known recurring issue, self-reported, not regression.

---

## Required actions before re-submission

### Must-fix (blocking) — Econ Evan

1. Rebuild `results/umcsent_xlv/winner_summary.json` with all required schema fields (see Pattern A table above).
2. Rebuild `results/indpro_xlp/winner_summary.json` with all required schema fields. Clarify `strategy_family` for `P3_long_short_counter` — either strip the suffix and use `P3_long_short` or request schema enum extension for `P3_long_short_counter`.
3. Rebuild `results/umcsent_xlv/signal_scope.json` using the current axis_block schema structure.
4. Rebuild `results/indpro_xlp/signal_scope.json` using the current axis_block schema structure.
5. Rebuild `results/umcsent_xlv/analyst_suggestions.json` using schema-compliant entry fields.
6. Rebuild `results/indpro_xlp/analyst_suggestions.json` using schema-compliant entry fields (top-level `suggestions` array, not `candidates`).

After rebuilding, re-run:
```bash
python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id umcsent_xlv
python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id indpro_xlp
```
Both must exit 0 before re-submission to GATE-31.

### Should-fix (non-blocking, file to backlog) — App Dev Ace or Econ Evan

7. BL-803: Generalize `smoke_loader.py` to support arbitrary page prefixes and pair-specific dynamic chart names.

### Advisory (no action required)

- indpro_xlp: MDD of −13.5% vs B&H −13.3%. Negligible drawdown improvement. Narrative should lead with return advantage (+4.5 pp annualized), not risk reduction. Research Ray should adjust the Story page framing.
- umcsent_xlv: MDD/vol ratio of 0.929 is slightly below the [1,6] reference. Acceptable for a defensive healthcare ETF. Note in story page caveats.

---

## Backlog updates

| ID | Wave | Status | Description |
|----|------|--------|-------------|
| BL-801 | 8C | Pre-existing, open | `max_drawdown` vs `oos_max_drawdown` key drift — confirmed also affects umcsent_xlv |
| BL-803 | 10B | **New** | `smoke_loader.py` page-prefix mismatch + hardcoded HY-IG v2 dynamic chart names |

---

*QA sign-off withheld pending pattern A/B/C remediation. Re-submit to GATE-31 after fixes verified by `smoke_schema_consumers.py`.*

*Quincy — 2026-04-20*
