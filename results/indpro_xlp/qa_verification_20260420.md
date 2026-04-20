# QA Verification — indpro_xlp — Wave 10B (2026-04-20)
QA Agent: Quincy | Gate: GATE-31

## Summary
Total checks: 22 | PASS: 14 | PASS-with-note: 2 | FAIL: 6 | Blocking: 6

## Findings table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | `results/indpro_xlp/tournament_results_20260420.csv` exists and >100 rows | PASS | 3,332 rows (including header); 3,331 combos |
| 2 | `results/indpro_xlp/winner_summary.json` exists | PASS | File present |
| 3 | winner_summary has `oos_sharpe` | PASS | 1.1147 |
| 4 | winner_summary has `oos_ann_return` | PASS | 0.1413 (ratio form) |
| 5 | winner_summary has `oos_max_drawdown` | PASS | -0.1353 (ratio form, correct field name) |
| 6 | winner_summary has `oos_ann_vol` | PASS | 0.1267 (ratio form) |
| 7 | winner_summary has `signal` / `signal_code` | FAIL | `winner_signal: S8_accel` is present, but schema field name is `signal_code`. Additionally, schema requires `signal_column` (exact parquet column name), which is absent. **Blocking** (APP-WS1 consumer cannot resolve winning signal parquet column). |
| 8 | winner_summary has `strategy_family` | FAIL | Field absent. Schema requires `strategy_family`. Present as `winner_strategy: P3_long_short_counter` — a non-standard key with a non-canonical value (`_counter` suffix not in schema enum: `P1_long_cash`, `P2_signal_strength`, `P3_long_short`). **Blocking.** |
| 9 | winner_summary has `direction` | FAIL | Field absent. `interpretation_metadata.json` has `observed_direction: countercyclical`. winner_summary must carry `direction` as an independent field per ECON-H5 contract. **Blocking.** |
| 10 | winner_summary has `generated_at`, `target_symbol`, `threshold_value`, `threshold_rule` | FAIL | All four absent. Schema (ECON-H5) requires these. Also missing `oos_n_trades`, `oos_period_start`, `oos_period_end`. **Blocking** (bundled as same root cause: winner_summary produced against an earlier schema version). |
| 11 | META-UC check: `oos_ann_return` ratio form | PASS | 0.1413; absolute value < 5.0 |
| 12 | META-UC check: `oos_max_drawdown` ratio form | PASS | -0.1353; absolute value < 5.0 |
| 13 | `results/indpro_xlp/interpretation_metadata.json` exists and has required fields | PASS | `schema_version`, `pair_id`, `indicator_nature`, `indicator_type`, `strategy_objective`, `owner_writes` all present. Rich content: mechanism, caveats array, direction fields. |
| 14 | `results/indpro_xlp/signal_scope.json` exists | PASS | File present with 13 indicator derivatives and 10 target derivatives |
| 15 | signal_scope.json schema conformance | FAIL | Missing required fields: `indicator_axis`, `target_axis`, `owner`. Uses `in_scope: {indicator_derivatives: [...], target_derivatives: [...]}` flat-array structure — same legacy shape as umcsent_xlv. `last_updated_by` and `last_updated_at` are present but the `indicator_axis` / `target_axis` axis_block structure with `canonical_column`, `display_name`, `derivatives` objects is absent. **Blocking** (ECON-UD schema gate). |
| 16 | `results/indpro_xlp/analyst_suggestions.json` exists | PASS | File present with 3 candidates |
| 17 | analyst_suggestions.json schema conformance | FAIL | Top-level key is `candidates` not `suggestions` (schema requires `suggestions`). Entry fields use `series`, `description`, `pearson_r`, `p_value`, `rationale` — diverges from schema fields `signal_name`, `proposed_by`, `observation`, `rationale`, `possible_use_case`, `caveats`, `date_filed`. Also missing top-level `schema_version`. **Blocking.** |
| 18 | `results/indpro_xlp/winner_trade_log.csv` exists and >1 row | PASS | 85 rows (84 data rows + header) |
| 19 | `data/indpro_xlp_monthly_*.parquet` exists | PASS | `data/indpro_xlp_monthly_19980101_20251231.parquet` present. Also `indpro_xlp_daily_19980101_20251231.parquet` confirmed. |
| 20 | All 10 chart JSON files exist in `output/charts/indpro_xlp/plotly/` | PASS | 10 files confirmed: ccf, correlations, drawdown, equity_curves, hero, regime_stats, rolling_sharpe, signal_dist, tournament_scatter, walk_forward. All non-empty (sizes 8.0 KB–281 KB). |
| 21 | All 4 portal pages exist (`14_indpro_xlp_*.py`) | PASS | story, evidence, strategy, methodology confirmed in `app/pages/` |
| 22 | QA-CL2: Sharpe ↔ return ↔ vol triangulation | PASS | Implied vol = 0.1413 / 1.1147 = 0.1267. Matches `oos_ann_vol` 0.1267 exactly. Perfect internal consistency. |

## QA-CL2 Extended

- MDD/vol ratio: |−0.1353| / 0.1267 = 1.07. Within [1, 6] range. PASS.
- `oos_annual_turnover`: 10.14 (high for monthly indicator — note: `P3_long_short_counter` strategy flips to short rather than cash, so turnover reflects counter-trend rebalancing frequency). Not implausible for an acceleration signal that changes sign frequently.
- `bh_max_drawdown`: −0.1329. Strategy max drawdown of −0.1353 is only marginally worse than B&H. Worth flagging for narrative — the primary gain is return, not drawdown protection. PASS-with-note.

## QA-CL3 — Agent memory discipline

Same as umcsent_xlv (same Evan session). See umcsent_xlv QA report for full detail.
- `~/.claude/agents/econ-evan/experience.md`: 51 lines. Present.
- `~/.claude/agents/econ-evan/memories.md`: 146 lines. Present.
- `_pws/econ-evan/session-notes.md`: Wave 10 documented with indpro_xlp-specific insights (FRED API fallback pattern, acceleration signal dynamics, counter-strategy dominance for defensive targets).
- **Result: PASS-with-note** — home-dir permission block known and self-reported.

## QA-CL4 — Smoke tests (GATE-27)

| Test | Result | Evidence |
|------|--------|---------|
| `smoke_loader.py indpro_xlp` | FAIL | 0 passes, 8 failures. Same root cause as umcsent_xlv: page glob uses `9_{pair_id}_*` prefix but indpro_xlp uses `14_`. EVIDENCE_DYNAMIC_CHARTS hardcoded to HY-IG v2 names. Test harness gap — not a pipeline failure. Same BL-803 filing needed. |
| `smoke_schema_consumers.py --pair-id indpro_xlp` | FAIL | 1 pass, 4 failures. Failures are genuine schema contract violations: winner_summary missing 11 required fields; signal_scope missing `indicator_axis`/`target_axis`/`owner`; analyst_suggestions has no `suggestions` key. **Blocking.** |
| `pair_registry.py` loads indpro_xlp | PASS | `indpro_xlp: True` confirmed |

## Verdict

**BLOCK**

Blocking items:
1. **winner_summary.json** — missing required schema fields: `generated_at`, `signal_column`, `signal_code` (uses `winner_signal`), `target_symbol`, `threshold_value`, `threshold_rule`, `strategy_family` (uses `winner_strategy` with non-canonical `_counter` suffix), `direction`, `oos_n_trades`, `oos_period_start`, `oos_period_end`. APP-WS1 consumer cannot render Strategy page.
2. **signal_scope.json** — legacy flat-array structure. Missing `indicator_axis`, `target_axis` (axis_block objects required), `owner`. ECON-UD gate fails.
3. **analyst_suggestions.json** — top-level key `candidates` instead of `suggestions`; entry fields use non-schema vocabulary. APP-WS1 consumer gate fails.
4. **smoke_loader GATE-27 gap** — same harness bug as umcsent_xlv. File as BL-803.

Additional note:
- Strategy `winner_strategy: P3_long_short_counter` — the `_counter` suffix is not in the schema `strategy_family` enum (`P1_long_cash`, `P2_signal_strength`, `P3_long_short`). Producer either needs to strip the suffix and use the base enum value, or the schema enum must be extended. Recommend enum extension to `P3_long_short_counter` as the strategy semantics differ (inverted directional position) and the distinction matters for Ace's position-adjustment logic.
- MDD of −13.5% vs B&H −13.3%: strategy offers negligible drawdown improvement over B&H; value-add is in return (14.1% vs 9.7%). This is not a QA blocker but should be flagged in narrative.

---

## QA Verification — Wave 10D GATE-28 Cloud Structural (2026-04-20, Quincy)

### Context
Cloud app rebooted at commit `eb023f9` which fixed two structural bugs caught by prior visual review:
- **BUG-1** (all 8 pages): Missing breadcrumb nav component (`render_breadcrumb()`)
- **BUG-2** (`indpro_xlp` Evidence only): Flat tab structure instead of required Level 1/Level 2 tabs

This wave verifies that both fixes are live on the cloud app for indpro_xlp (4 pages).

### Summary
Total checks: 18 (4 pages × 4 structural checks + 1 evidence-tab check for evidence page)
PASS: 18 | FAIL: 0 | NAV_ERROR: 0

### Detailed findings
| # | Page | Check | Result | Evidence |
|---|------|-------|--------|----------|
| 1 | indpro_xlp_story | chart_pending | PASS | No "chart pending" found |
| 2 | indpro_xlp_story | python_errors | PASS | No Python errors detected |
| 3 | indpro_xlp_story | page_not_blank | PASS | dom=7862 chars |
| 4 | indpro_xlp_story | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 5 | indpro_xlp_evidence | chart_pending | PASS | No "chart pending" found |
| 6 | indpro_xlp_evidence | python_errors | PASS | No Python errors detected |
| 7 | indpro_xlp_evidence | page_not_blank | PASS | dom=4724 chars |
| 8 | indpro_xlp_evidence | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 9 | indpro_xlp_evidence | evidence_tab_structure | PASS | Found "Level 1" — Level 1/Level 2 tab structure confirmed |
| 10 | indpro_xlp_strategy | chart_pending | PASS | No "chart pending" found |
| 11 | indpro_xlp_strategy | python_errors | PASS | No Python errors detected |
| 12 | indpro_xlp_strategy | page_not_blank | PASS | dom=4627 chars |
| 13 | indpro_xlp_strategy | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 14 | indpro_xlp_methodology | chart_pending | PASS | No "chart pending" found |
| 15 | indpro_xlp_methodology | python_errors | PASS | No Python errors detected |
| 16 | indpro_xlp_methodology | page_not_blank | PASS | dom=4772 chars |
| 17 | indpro_xlp_methodology | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 18 | All 4 pages | nav_error | PASS | All pages loaded successfully (networkidle, 90s timeout) |

### Evidence of BUG-1 fix (breadcrumb)
DOM text sample from `indpro_xlp_story`:
```
📖 Story  🔬 Evidence  🎯 Strategy  📐 Methodology
```
All 4 navigation labels confirmed in live DOM.

### Evidence of BUG-2 fix (Level 1/Level 2 tab structure — indpro_xlp_evidence)
DOM text sample:
```
Evidence is organized in two tiers. Level 1 covers basic correlations and cross-correlations (Granger causality). Level 2 adds regime analysis.
Level 1 — Basic Analysis
```
Confirms the Level 1/Level 2 tab structure is present. Previously this page had flat single-level tabs.

### Sign-off recommendation
GATE-28 PASS — All 18 structural checks pass across 4 indpro_xlp pages. BUG-1 (missing breadcrumb) confirmed resolved. BUG-2 (flat Evidence tab structure) confirmed resolved — Level 1/Level 2 two-tier layout now live.

Verification artefacts:
- Script: `temp/260420_wave10d_cloud/wave10d_gate28_structural.py`
- Screenshots: `temp/260420_wave10d_cloud/screenshots/indpro_xlp_*.png`
- DOM text: `temp/260420_wave10d_cloud/dom_text/indpro_xlp_*_dom.txt`
- JSON: `temp/260420_wave10d_cloud/wave10d_gate28_structural_results.json`
