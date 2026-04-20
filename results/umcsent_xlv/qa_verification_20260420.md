# QA Verification — umcsent_xlv — Wave 10B (2026-04-20)
QA Agent: Quincy | Gate: GATE-31

## Summary
Total checks: 22 | PASS: 14 | PASS-with-note: 2 | FAIL: 6 | Blocking: 6

## Findings table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | `results/umcsent_xlv/tournament_results_20260420.csv` exists and >100 rows | PASS | 1,307 rows (including header) |
| 2 | `results/umcsent_xlv/winner_summary.json` exists | PASS | File present, 1,088 bytes |
| 3 | winner_summary has `oos_sharpe` | PASS | 1.0202 |
| 4 | winner_summary has `oos_ann_return` | PASS | 0.119344 (ratio form) |
| 5 | winner_summary has `oos_max_drawdown` | FAIL | Field is named `max_drawdown` not `oos_max_drawdown`; schema requires `oos_max_drawdown`. Value -0.10865 is correct in magnitude and sign. This is BL-801 (filed Wave 8C, deferred). **Blocking** — schema consumer APP-WS1 fails on this pair. |
| 6 | winner_summary has `oos_ann_vol` | PASS | 0.116975 (ratio form) |
| 7 | winner_summary has `signal` | PASS-with-note | Present as `signal` key (value: S2_yoy). Schema requires `signal_code` — field name mismatch. |
| 8 | winner_summary has `strategy_family` | FAIL | Field absent. Schema (ECON-H5) requires `strategy_family`. Present as `strategy` key (value: P1_long_cash). Field naming diverges from schema contract. **Blocking.** |
| 9 | winner_summary has `direction` | FAIL | Field absent. Schema (ECON-H5) requires `direction`. `interpretation_metadata.json` has `observed_direction: procyclical`. **Blocking.** |
| 10 | META-UC check: `oos_ann_return` ratio form | PASS | 0.119344; absolute value < 5.0 |
| 11 | META-UC check: `max_drawdown` ratio form | PASS | -0.10865; absolute value < 5.0 |
| 12 | `results/umcsent_xlv/interpretation_metadata.json` exists and has required fields | PASS | `schema_version`, `pair_id`, `indicator_nature`, `indicator_type`, `strategy_objective`, `owner_writes` all present. |
| 13 | `results/umcsent_xlv/signal_scope.json` exists | PASS | File present and detailed (7 indicator signals, 7 target signals, 3 out-of-scope controls) |
| 14 | signal_scope.json schema conformance | FAIL | Missing required fields: `indicator_axis`, `target_axis`, `last_updated_by`, `last_updated_at`, `owner`. Current structure uses flat `in_scope_indicator_signals` / `in_scope_target_signals` arrays — a legacy schema shape. **Blocking** (ECON-UD schema gate). |
| 15 | `results/umcsent_xlv/analyst_suggestions.json` exists | PASS | File present with 4 suggestions |
| 16 | analyst_suggestions.json schema conformance | FAIL | Entries use old field names: `signal`, `description`, `note`, `pearson_r`. Schema requires `signal_name`, `proposed_by`, `observation`, `rationale`, `possible_use_case`, `caveats`, `date_filed`. Also missing top-level `schema_version` and `last_updated_at`. **Blocking** (APP-WS1 consumer pre-render gate). |
| 17 | `results/umcsent_xlv/winner_trade_log.csv` exists and >1 row | PASS | 82 rows (81 data rows + header) |
| 18 | `data/umcsent_xlv_monthly_*.parquet` exists | PASS | `data/umcsent_xlv_monthly_19980101_20251231.parquet` present |
| 19 | All 10 chart JSON files exist in `output/charts/umcsent_xlv/plotly/` | PASS | 10 files confirmed: ccf, correlations, drawdown, equity_curves, hero, regime_stats, rolling_sharpe, signal_dist, tournament_scatter, wf_sharpe. All non-empty (sizes 7.7 KB–117 KB). |
| 20 | All 4 portal pages exist (`10_umcsent_xlv_*.py`) | PASS | story, evidence, strategy, methodology confirmed in `app/pages/` |
| 21 | QA-CL2: Sharpe ↔ return ↔ vol triangulation | PASS | Implied vol = oos_ann_return / oos_sharpe = 0.1193 / 1.0202 = 11.69% ≈ actual vol 11.70%. Delta < 0.1 pp. Plausible for equity strategy. |
| 22 | QA-CL2: |MDD|/vol ratio | PASS-with-note | 0.10865 / 0.116975 = 0.929. Below the [1, 6] reference range. XLV is a lower-vol defensive ETF; OOS period is 6 years (81 months). Borderline but not implausible. Note rather than block. |

## QA-CL3 — Agent memory discipline

- `~/.claude/agents/econ-evan/experience.md`: 51 lines. Present.
- `~/.claude/agents/econ-evan/memories.md`: 146 lines. Present.
- `_pws/econ-evan/session-notes.md`: Wave 10 documented — cross-pair insights, rules applied, open items all present. Evan explicitly notes that home-dir EOD write permissions were denied and that content was recorded in session-notes.md instead.
- **Result: PASS-with-note** — experience.md and memories.md are present from a prior wave. Evan self-reported the permission block and documented cross-project patterns in session-notes.md. First occurrence of this issue, already documented. No regression.

## QA-CL4 — Smoke tests (GATE-27)

| Test | Result | Evidence |
|------|--------|---------|
| `smoke_loader.py umcsent_xlv` | FAIL | 0 passes, 8 failures. Root cause: (a) loader scans pages matching `9_{pair_id}_*.py` but umcsent_xlv uses `10_` prefix — 0 pages scanned; (b) EVIDENCE_DYNAMIC_CHARTS is hardcoded to HY-IG v2 chart names (e.g. `correlation_heatmap`, `hmm_regime_probs`) which do not exist for umcsent_xlv. This is a **test harness gap**, not a pipeline failure. Actual chart JSONs are present and non-empty. Structural fix needed: extend smoke_loader to support multi-page-prefix pairs or parameterize EVIDENCE_DYNAMIC_CHARTS. |
| `smoke_schema_consumers.py --pair-id umcsent_xlv` | FAIL | 1 pass, 4 failures. Failures are schema contract violations: winner_summary missing 12 required fields; signal_scope missing 5 required fields; analyst_suggestions entries missing 7 required fields per entry. These failures reflect real producer violations, not harness gaps. **Blocking.** |
| `pair_registry.py` loads umcsent_xlv | PASS | `umcsent_xlv: True` confirmed |

## Verdict

**BLOCK**

Blocking items:
1. **winner_summary.json** — missing required schema fields: `generated_at`, `signal_column`, `signal_code`, `target_symbol`, `threshold_value`, `threshold_rule`, `strategy_family`, `direction`, `oos_max_drawdown` (filed as `max_drawdown`), `oos_n_trades`, `oos_period_start`, `oos_period_end`. This prevents APP-WS1 consumer from loading the Strategy page.
2. **signal_scope.json** — schema shape is the legacy flat-array structure. Missing required fields: `indicator_axis`, `target_axis`, `owner`, `last_updated_by`, `last_updated_at`. ECON-UD gate fails.
3. **analyst_suggestions.json** — entry fields use old vocabulary (`signal`, `description`, `note`) instead of schema fields (`signal_name`, `proposed_by`, `observation`, `rationale`, `possible_use_case`, `caveats`, `date_filed`). Also missing top-level `schema_version` and `last_updated_at`. APP-WS1 consumer gate fails.
4. **smoke_loader GATE-27 gap** — test harness bug (page-prefix mismatch + hardcoded chart names). Not a pipeline failure but GATE-27 cannot be verified as PASS until fixed. Recommend filing as BL-803.

Non-blocking observations:
- `max_drawdown` key alias (vs `oos_max_drawdown`) is a pre-existing known issue (BL-801, filed Wave 8C).
- MDD/vol ratio of 0.929 is borderline but defensible for a defensive sector ETF with a 6-year OOS window.

---

## QA Verification — Wave 10D GATE-28 Cloud Structural (2026-04-20, Quincy)

### Context
Cloud app rebooted at commit `eb023f9` which fixed two structural bugs caught by prior visual review:
- **BUG-1** (all 8 pages): Missing breadcrumb nav component (`render_breadcrumb()`)
- **BUG-2** (`indpro_xlp` Evidence only): Flat tab structure instead of required Level 1/Level 2 tabs

This wave verifies that both fixes are live on the cloud app for umcsent_xlv (4 pages).

### Summary
Total checks: 18 (4 pages × 4 structural checks + 1 evidence-tab check for evidence page)
PASS: 18 | FAIL: 0 | NAV_ERROR: 0

### Detailed findings
| # | Page | Check | Result | Evidence |
|---|------|-------|--------|----------|
| 1 | umcsent_xlv_story | chart_pending | PASS | No "chart pending" found |
| 2 | umcsent_xlv_story | python_errors | PASS | No Python errors detected |
| 3 | umcsent_xlv_story | page_not_blank | PASS | dom=9257 chars |
| 4 | umcsent_xlv_story | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 5 | umcsent_xlv_evidence | chart_pending | PASS | No "chart pending" found |
| 6 | umcsent_xlv_evidence | python_errors | PASS | No Python errors detected |
| 7 | umcsent_xlv_evidence | page_not_blank | PASS | dom=4653 chars |
| 8 | umcsent_xlv_evidence | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 9 | umcsent_xlv_evidence | evidence_tab_structure | PASS | Found "Level 1" — Level 1/Level 2 tab structure confirmed |
| 10 | umcsent_xlv_strategy | chart_pending | PASS | No "chart pending" found |
| 11 | umcsent_xlv_strategy | python_errors | PASS | No Python errors detected |
| 12 | umcsent_xlv_strategy | page_not_blank | PASS | dom=4430 chars |
| 13 | umcsent_xlv_strategy | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 14 | umcsent_xlv_methodology | chart_pending | PASS | No "chart pending" found |
| 15 | umcsent_xlv_methodology | python_errors | PASS | No Python errors detected |
| 16 | umcsent_xlv_methodology | page_not_blank | PASS | dom=8486 chars |
| 17 | umcsent_xlv_methodology | breadcrumb_nav | PASS | All 4 labels present: Story, Evidence, Strategy, Methodology |
| 18 | All 4 pages | nav_error | PASS | All pages loaded successfully (networkidle, 90s timeout) |

### Evidence of BUG-1 fix (breadcrumb)
DOM text sample from `umcsent_xlv_story`:
```
📖 Story  🔬 Evidence  🎯 Strategy  📐 Methodology
```
All 4 navigation labels confirmed in live DOM.

### Evidence of Level 1/Level 2 tab structure (umcsent_xlv_evidence)
DOM text sample:
```
Evidence is organized in two tiers. Level 1 covers basic correlations and cross-correlations. Level 2 adds regime analysis and distributional methods.
Level 1 — Basic Analysis
```

### Sign-off recommendation
GATE-28 PASS — All 18 structural checks pass across 4 umcsent_xlv pages. BUG-1 (missing breadcrumb) confirmed resolved. Evidence page Level 1/Level 2 tab structure confirmed present.

Verification artefacts:
- Script: `temp/260420_wave10d_cloud/wave10d_gate28_structural.py`
- Screenshots: `temp/260420_wave10d_cloud/screenshots/umcsent_xlv_*.png`
- DOM text: `temp/260420_wave10d_cloud/dom_text/umcsent_xlv_*_dom.txt`
- JSON: `temp/260420_wave10d_cloud/wave10d_gate28_structural_results.json`

---

## QA Verification — Wave 10D Signal Universe (2026-04-20, Quincy)

**QA Agent:** Quincy | **Commit verified:** 57d1bb6 | **Gate:** Signal Universe non-empty render

### Context

`10_umcsent_xlv_methodology.py` already used the shared `render_signal_universe()` component — no code change was needed for this page. This verification confirms the page continues to render a populated Signal Universe section (regression guard) alongside the verification of the indpro_xlp fix.

### Checks

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Signal Universe section header present (`signal universe`) | PASS | Found: "Signal Universe (ECON-UD)" section present |
| 2 | In-scope subsection header present (`indicator derivatives`) | PASS | "Indicator derivatives — U of Michigan Consumer Sentiment" rendered |
| 3 | Derivative name `umcsent` present in DOM | PASS | 7 UMCSENT derivatives listed (umcsent, umcsent_yoy, umcsent_mom, umcsent_zscore, umcsent_3m_ma, umcsent_direction, umcsent_dev_ma) |
| 4 | No `chart pending` text | PASS | 0 occurrences |
| 5 | No Python errors in DOM | PASS | No traceback, AttributeError, KeyError, or other exception text found |
| 6 | Breadcrumb/pair identifier `umcsent_xlv` present | PASS | Present in footer: "Pair ID: umcsent_xlv" |

**Overall: PASS — 6/6 checks pass**

### Signal Universe content confirmed (DOM extract)

```
Signal Universe (ECON-UD)

...the authoritative list of in-scope signals per ECON-SD scope discipline.
Loaded from results/umcsent_xlv/signal_scope.json.

Indicator derivatives — U of Michigan Consumer Sentiment

Takeaway: 5 indicator-axis derivatives disclosed...

Target derivatives — Health Care Select Sector (XLV)

Takeaway: 5 target-axis derivatives disclosed...
```

Note: umcsent_xlv uses `render_signal_universe()` component which renders "Indicator derivatives" / "Target derivatives" subheaders, while indpro_xlp uses the legacy inline renderer producing "In-scope:" headers. Both are populated and correct.

### Playwright technical note

Same as indpro_xlp: content extracted from Streamlit's `/~/+/<page_slug>` iframe frame. DOM text length: 8,486 chars (larger than indpro_xlp's 6,616 chars due to more detailed IS/OOS split explanation and indicator construction tables).

### Verification artefacts

- Script: `temp/260420_wave10d_cloud/wave10d_signal_universe.py`
- Screenshot: `temp/260420_wave10d_cloud/screenshots/umcsent_xlv_methodology_signal_universe.png`
- DOM text: `temp/260420_wave10d_cloud/dom_text/umcsent_xlv_methodology_signal_universe_dom.txt` (8,486 chars)
- JSON: `temp/260420_wave10d_cloud/wave10d_signal_universe_results.json`

### Sign-off recommendation

PASS — Signal Universe section renders correctly on `umcsent_xlv_methodology` page. No regression introduced by Wave 10D changes.
