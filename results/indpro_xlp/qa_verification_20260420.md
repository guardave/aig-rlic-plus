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

---

## QA Verification — Wave 10D Signal Universe (2026-04-20, Quincy)

**QA Agent:** Quincy | **Commit verified:** 57d1bb6 | **Gate:** Signal Universe non-empty render

### Context

`14_indpro_xlp_methodology.py` had a legacy schema reader (`scope.get("in_scope", {})`) that returned an empty dict because `signal_scope.json` was migrated to `indicator_axis`/`target_axis` format. The fix (commit 57d1bb6) updated the reader to `scope.get("indicator_axis", {}).get("derivatives", [])`. This verification confirms the fix is live on the cloud app and both new-pair Methodology pages render a populated Signal Universe section.

### Checks

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Signal Universe section header present (`signal universe`) | PASS | Found at DOM position 1437: "Signal Universe (ECON-SD)" |
| 2 | In-scope subsection header present (`in-scope:`) | PASS | "In-scope: Industrial Production Index Derivatives" rendered |
| 3 | Derivative name `indpro` present in DOM | PASS | 7 INDPRO derivatives listed (indpro, indpro_yoy, indpro_mom, indpro_zscore, indpro_3m_ma, indpro_6m_ma, indpro_accel) with full descriptions |
| 4 | No `chart pending` text | PASS | 0 occurrences |
| 5 | No Python errors in DOM | PASS | No traceback, AttributeError, KeyError, or other exception text found |
| 6 | Breadcrumb/pair identifier `indpro_xlp` present | PASS | Present in footer: "Pair: indpro_xlp" |

**Overall: PASS — 6/6 checks pass**

### Signal Universe content confirmed (DOM extract)

```
Signal Universe (ECON-SD)

In-scope: Industrial Production Index Derivatives

indpro — The raw Federal Reserve Industrial Production Index...
indpro_yoy — The year-over-year percentage change in industrial production...
indpro_mom — The month-over-month percentage change in industrial production...
indpro_zscore — The 36-month rolling z-score of industrial production...
indpro_3m_ma — The 3-month moving average of industrial production...
indpro_6m_ma — The 6-month moving average of industrial production...
indpro_accel — The acceleration of industrial production...

In-scope: Consumer Staples Select Sector (XLP) Derivatives

xlp, xlp_ret_1m, xlp_ret_3m, xlp_ret_12m, xlp_vol_12m — all listed with descriptions
```

Previously these columns rendered silently blank (empty dict from legacy schema reader). Fix confirmed working.

### Playwright technical note

Streamlit Cloud renders all content inside an iframe at `/~/+/<page_slug>`. Outer `document.body.innerText` always returns empty (JavaScript SPA shell). Correct approach: extract text from the frame with `/~/+/` in URL via `page.frames`. Updated QA script (`temp/260420_wave10d_cloud/wave10d_signal_universe.py`) now uses correct frame extraction.

### Verification artefacts

- Script: `temp/260420_wave10d_cloud/wave10d_signal_universe.py`
- Screenshot: `temp/260420_wave10d_cloud/screenshots/indpro_xlp_methodology_signal_universe.png`
- DOM text: `temp/260420_wave10d_cloud/dom_text/indpro_xlp_methodology_signal_universe_dom.txt` (6,616 chars)
- JSON: `temp/260420_wave10d_cloud/wave10d_signal_universe_results.json`

### Sign-off recommendation

PASS — Signal Universe section renders correctly on `indpro_xlp_methodology` page. Schema reader fix confirmed live.

---

## RES-NR1 Verification — indpro_xlp (2026-04-20, Ray)

**Rule:** RES-NR1 — every instrument reference in portal narrative prose must match `results/indpro_xlp/interpretation_metadata.json` → `target_symbol` field.

**Confirmed identifiers:**
- `target_symbol`: XLP (Consumer Staples Select Sector SPDR)
- `indicator_id`: INDPRO (Industrial Production Index)

**Instrument references found and verified:**

| Location in `app/pair_configs/indpro_xlp_config.py` | Reference found | Status | Action |
|------------------------------------------------------|----------------|--------|--------|
| `StoryConfig.PAGE_TITLE` | "Consumer Staples sector" (implied via "Staples Stumble") | CORRECT | None |
| `StoryConfig.PAGE_SUBTITLE` | "consumer staples sector" | CORRECT | None |
| `StoryConfig.PLAIN_ENGLISH` | "consumer staples ETF (XLP)" | CORRECT | None |
| `StoryConfig.WHERE_THIS_FITS` | "consumer staples sector (XLP)" | CORRECT | None |
| `StoryConfig.ONE_SENTENCE_THESIS` | "XLP", "defensive consumer staples" | CORRECT | None |
| `StoryConfig.KPI_CAPTION` | "XLP" | CORRECT | None |
| `StoryConfig.HERO_TITLE` | "Consumer Staples (XLP)" | CORRECT | None |
| `StoryConfig.NARRATIVE_SECTION_1` (line ~121) | "broad S&P 500" used as comparative contrast, not target; XLP is clearly identified as the target | CORRECT — comparative context, not target misidentification | None |
| `StoryConfig.NARRATIVE_SECTION_2` heading (was line 139) | **"The Nuance: It Is Not a Perfect Inverse of the S&P 500"** — S&P 500 named in title where target is XLP | **VIOLATION (GATE-NR)** | **FIXED → "The Nuance: XLP Is Not a Mechanical Inverse of the IP Cycle"** |
| `StoryConfig.NARRATIVE_SECTION_2` body | "XLP" used throughout | CORRECT | None |
| `StoryConfig.SCOPE_NOTE` | "INDPRO → XLP relationship" | CORRECT | None |
| `CORRELATION_BLOCK` fields | "XLP" throughout | CORRECT | None |
| `GRANGER_BLOCK` fields | "XLP", "consumer staples equity returns" | CORRECT | None |
| `REGIME_BLOCK` fields | "XLP" throughout | CORRECT | None |
| `EVIDENCE_METHOD_BLOCKS` | "XLP", "consumer staples ETF (XLP)" | CORRECT | None |
| `StrategyConfig.PAGE_TITLE` | "XLP Timing" | CORRECT | None |
| `StrategyConfig.CAVEATS_MD` caveat 1 | "INDPRO × SPY strategy" — cross-pair reference for investor guidance, not a target misidentification | CORRECT — intentional cross-pair contrast | None |
| `_DATA_SOURCES_MD` | "XLP", "Consumer Staples ETF"; SPY listed as benchmark row — appropriate | CORRECT | None |
| `METHODOLOGY_CONFIG.plain_english` | "INDPRO × XLP pair" | CORRECT | None |

**Total violations found:** 1  
**Total violations fixed:** 1  
**Fix applied:** `StoryConfig.NARRATIVE_SECTION_2` heading changed from "The Nuance: It Is Not a Perfect Inverse of the S&P 500" to "The Nuance: XLP Is Not a Mechanical Inverse of the IP Cycle"

**RES-NR1 Status: PASS (after fix)**

---

## QA Verification — GATE-NR Narrative Instrument Check (2026-04-20, Quincy)

**Gate:** GATE-NR (QA-CL5) | **Pair:** indpro_xlp | **target_symbol:** XLP  
**Pages audited:** `indpro_xlp_story`, `indpro_xlp_evidence`  
**Script:** `temp/260420_wave10d_cloud/wave10d_gate_nr.py`  
**Cloud app commit at time of scan:** `bfb1b70` (Wave 10E)

### Rule summary

For Story and Evidence pages, scan DOM text for equity instrument names from `KNOWN_INSTRUMENTS` list. Any non-target instrument found outside a clearly comparative context is a FAIL. Comparative/contrastive references are classified PASS-with-note.

### Results

| # | Page | Gate-NR status | Instrument hits | Detail |
|---|------|---------------|-----------------|--------|
| 1 | `indpro_xlp_story` | **PASS-with-note** | S&P 500 (×2) | Both in comparative context — see below |
| 2 | `indpro_xlp_evidence` | **PASS** | None (no non-target instruments) | Clean |

**Overall GATE-NR verdict: PASS**  
Total: 1 PASS, 1 PASS-with-note, 0 FAIL, 0 ERROR

### PASS-with-note detail — `indpro_xlp_story`

Two occurrences of "S&P 500" found on the Story page. Both are genuine contrastive references, not target misidentifications:

**Occurrence 1** (contrastive inline sentence):
```
This is the opposite of what we expect for the broad S&P 500, where rising IP is bullish. XLP is the defensive case.
```
Classification: PASS-with-note — XLP is correctly identified as the subject; S&P 500 is used as a contrast benchmark.

**Occurrence 2** (section heading):
```
The Nuance: It Is Not a Perfect Inverse of the S&P 500
```
Classification: PASS-with-note — The heading explicitly states XLP is *not* a mirror of S&P 500, which is a contrastive framing, not a target misidentification.

**Note on Ray's fix:** Research Ray identified this heading as a GATE-NR violation (RES-NR1) and changed it locally in `app/pair_configs/indpro_xlp_config.py` to "The Nuance: XLP Is Not a Mechanical Inverse of the IP Cycle". That local fix has **not yet been deployed to Cloud** as of commit `bfb1b70`. The Cloud app still shows the old heading.

Assessment: The old heading ("It Is Not a Perfect Inverse of the S&P 500") is contrastive and does not mislead users about the target instrument. GATE-NR classifies it as PASS-with-note rather than FAIL. However, Ray's improved heading is cleaner and should be included in the next deployment.

### Instrument scan coverage

All 20 instruments from `KNOWN_INSTRUMENTS` were scanned:
- `XLP` (target): found extensively on both pages — all OK
- `S&P 500`: found ×2 on Story page — PASS-with-note (comparative)
- All others (SPY, XLV, XLK, XLE, XLF, XLI, XLB, XLU, XLRE, S&P500, S&P 500 Index, VIX, QQQ, IWM, DIA, Nasdaq, Dow Jones, Russell 2000): **not found** on either page

### Verification artefacts

- Script: `temp/260420_wave10d_cloud/wave10d_gate_nr.py`
- Screenshots: `temp/260420_wave10d_cloud/screenshots/gate_nr_indpro_xlp_story.png`, `gate_nr_indpro_xlp_evidence.png`
- DOM text: `temp/260420_wave10d_cloud/dom_text/gate_nr_indpro_xlp_story_dom.txt` (7,772 chars), `gate_nr_indpro_xlp_evidence_dom.txt` (4,695 chars)
- JSON: `temp/260420_wave10d_cloud/wave10d_gate_nr_results.json`

### Sign-off

**GATE-NR: PASS** — No instrument violations found on either `indpro_xlp_story` or `indpro_xlp_evidence`. Two comparative S&P 500 references on the Story page are correctly classified as PASS-with-note. Ray's heading fix (pending deployment) will eliminate both notes when deployed.
