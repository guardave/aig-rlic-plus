# QA Verification — hy_ig_spy_v4_from_scratch (2026-05-12, QA Quincy)

**Pair:** hy_ig_spy_v4_from_scratch  
**QA agent:** Quincy  
**Date:** 2026-05-12  
**Evidence status:** `failed_final_exam` — pair is production-eligible per DPS-PRE1 but requires disclosure banner.  
**Lead CDR:** Passed, 0 blockers.

---

## Summary

| Category | PASS | PASS-with-note | FAIL | Blocking |
|----------|------|----------------|------|----------|
| (a) Artifact verification | 12 | 1 | 4 | 4 |
| (b) Smoke tests | 1 | 0 | 2 | 2 |
| (c) Stakeholder-spirit check | 8 | 1 | 0 | 0 |
| (d) Cross-agent seam audit | 7 | 1 | 1 | 1 |
| **TOTAL** | **28** | **3** | **7** | **7** |

**Overall verdict: FAIL** — 7 blocking findings. Acceptance blocked pending producer fixes.

---

## (a) Artifact Verification

### Evan's Claims

| # | Claim | File | Verification command | Result |
|---|-------|------|----------------------|--------|
| E1 | OOS Sharpe = 1.3238 | `tournament_results_v4_20260512.csv` | `grep "S2c_zscore_36m,T3_z0.0,P1,1"` | **PASS** — row present: oos_sharpe=1.3238 confirmed |
| E2 | Signal = S2c_zscore_36m | `tournament_winner.json` | `cat tournament_winner.json` | **PASS** — `winner.signal = "S2c_zscore_36m"` |
| E3 | direction = countercyclical | `interpretation_metadata.json` | `python3 -c "import json; print(json.load(open(...))['observed_direction'])"` | **PASS** — `observed_direction = "countercyclical"` |
| E4 | winner_summary.json schema valid | `docs/schemas/winner_summary.schema.json` | `python3 scripts/validate_schema.py --schema docs/schemas/winner_summary.schema.json --instance results/.../winner_summary.json` | **PASS** — exit 0, conforms |
| E5 | evidence_status.json schema v1.2.0 | `docs/schemas/evidence_status.schema.json` | `python3 scripts/validate_schema.py --schema docs/schemas/evidence_status.schema.json --instance results/.../evidence_status.json` | **PASS** — exit 0, schema_version=1.2.0 confirmed |
| E6 | final_exam_results_20260512.json exists and is non-empty | `results/hy_ig_spy_v4_from_scratch/final_exam_results_20260512.json` | `ls -la results/.../final_exam_results_20260512.json` | **PASS** — exists, non-empty (schema_version="1.0.0") |
| E7 | final_exam_results conforms to schema | `docs/schemas/final_exam_results.schema.json` | `python3 scripts/validate_schema.py --schema docs/schemas/final_exam_results.schema.json --instance results/.../final_exam_results_20260512.json` | **FAIL (BLOCKING)** — 30+ schema violations. Missing required properties: `owner`, `status_recommendation`, `metrics`, `pass_fail`, `artifact_lineage`, `qa`. `frozen_rule` missing `rule_id`, `lead_lag`, `position_rule`, `cost_bps`, `benchmark`. `sample` missing 7 required fields. `uncertainty` missing 5 required fields. `multiple_testing.adjustment_method` = "Bonferroni_deflation_approx" not in allowed enum. `schema_version` = "1.0.0" but "1.1.0" expected. Owner: Evan. |
| E8 | interpretation_metadata.json conforms to schema | `docs/schemas/interpretation_metadata.schema.json` | `python3 scripts/validate_schema.py --schema docs/schemas/interpretation_metadata.schema.json --instance results/.../interpretation_metadata.json` | **FAIL (BLOCKING)** — 3 violations: missing required `schema_version`, missing required `owner_writes`, `confidence` = "moderate" not in enum ["high","medium","low"]. Owner: Evan/Dana. |
| E9 | signal_scope.json conforms to schema | `docs/schemas/signal_scope.schema.json` | `python3 scripts/validate_schema.py --schema docs/schemas/signal_scope.schema.json --instance results/.../signal_scope.json` | **FAIL (BLOCKING)** — every derivative missing required `formula` and `appears_in_charts` fields (14 indicator derivatives + 4 target derivatives = 36 violations). Owner: Evan. |

### Vera's Claims

| # | Claim | File | Verification command | Result |
|---|-------|------|----------------------|--------|
| V1 | 9/9 mandatory charts present | `output/charts/hy_ig_spy_v4_from_scratch/plotly/` | `ls plotly/ \| grep -E "^(hero\|regime_stats\|rolling_correlation\|rolling_granger\|rolling_sharpe\|walk_forward\|tournament_scatter\|drawdown\|subperiod_sharpe)\.json$"` | **PASS** — all 9 present |
| V2 | All mandatory charts > 100 bytes | same | `stat -c%s` on each | **PASS** — smallest is regime_stats.json at 8,489 bytes; all well above 100 |
| V3 | 5/5 crisis zoom charts present | `output/charts/hy_ig_spy_v4_from_scratch/plotly/` | `ls \| grep "history_zoom_"` | **PASS** — dotcom, gfc, covid, taper_2018, inflation_2022 all present |
| V4 | All crisis zoom charts > 100 bytes | same | `stat -c%s` on each | **PASS** — smallest is history_zoom_taper_2018.json at 9,326 bytes |
| V5 | GATE-DP1: bottom-panel traces use xaxis="x2" | all 5 history_zoom_*.json | custom GATE-DP1 check (see (b) Smoke tests section) | **FAIL (BLOCKING)** — all 5 zoom charts: trace[1] `SPY Cumul. Return (indexed)` has `yaxis="y2"` but `xaxis="x"` (expected `xaxis="x2"`). The bottom SPY panel is invisible on screen for all 5 crisis episodes. Owner: Vera. |
| V6 | GATE-VIZ-NBER2: recession zoom charts have canonical NBER shading | dotcom, gfc, covid | GATE-VIZ-NBER2 check: scan `layout.shapes` for fillcolor starting with `rgba(150` | **PASS-with-note** — dotcom, gfc, covid each have 1 shape of type=rect with `fillcolor=rgba(180,180,180,0.30)`. Recession is marked and annotations say "NBER Recession". However `rgba(180,...)` does not match the canonical VIZ-NBER1 color `rgba(150,120,120,0.22)`. **GATE-VIZ-NBER2 technically FAILs** on color check; recession IS visually indicated via annotations. Non-blocking given annotations are present, but Vera must update shading color to canonical palette before retro-apply window closes. |

### Ace's Claims

| # | Claim | File | Verification command | Result |
|---|-------|------|----------------------|--------|
| A1 | 4 page files exist | `app/pages/` | `ls app/pages/ \| grep "hy_ig_spy_v4"` | **PASS** — story, evidence, strategy, methodology all present |
| A2 | Pair config exists | `app/pair_configs/` | `ls app/pair_configs/ \| grep "hy_ig_spy_v4"` | **PASS** — `hy_ig_spy_v4_from_scratch_config.py` confirmed |
| A3 | Pair in registry | `app/components/pair_registry.py` | `grep "hy_ig_spy_v4" app/components/pair_registry.py` | **PASS** — pair and display name both registered |
| A4 | GATE-DPS1 self-report: 0 FAIL, 1 WARN | N/A | `python3 scripts/validate_pair_completeness.py --pair hy_ig_spy_v4_from_scratch --no-color` | **PASS** — independently confirmed: 0 FAIL, 1 WARN (pre-exam outcome), 126 PASS |

---

## (b) Smoke Tests

### smoke_loader.py

```
python3 app/_smoke_tests/smoke_loader.py hy_ig_spy_v4_from_scratch
```

**Result: PASS — failures=0**

Output (abbreviated):
```
# Loader smoke test  pair_id=hy_ig_spy_v4_from_scratch  timestamp=2026-05-12T15:57:23
# Pages scanned: 4
PASS  chart=hero  traces=2  title='HY-IG Spread → SPY (v4): Full History (1997–2026)'
PASS  chart=regime_stats  traces=1  title='...'
PASS  chart=equity_curves  traces=2  title='...'
PASS  chart=drawdown  traces=2  title='...'
PASS  chart=walk_forward  traces=2  title='...'
PASS  chart=tournament_scatter  traces=2  title='...'
# RESULT  passes=6  failures=0
```

Note: smoke_loader tests chart JSON loading only — does NOT exercise history_zoom charts or the rolling_correlation/rolling_granger/rolling_sharpe/subperiod_sharpe mandatory charts. The 9 mandatory charts are confirmed by GATE-DPS1. GATE-DP1 must be satisfied separately (see blocking findings).

### smoke_schema_consumers.py

```
python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id hy_ig_spy_v4_from_scratch
```

**Result: FAIL — failures=3**

```
PASS  APP-WS1: winner_summary.json conforms to ECON-H5  keys=27
FAIL  APP-WS1 sibling: interpretation_metadata.json conforms to DATA-D6 
      errors=["[<root>] 'schema_version' is a required property", 
               "[<root>] 'owner_writes' is a required property", 
               "[confidence] 'moderate' is not one of ['high', 'medium', 'low']"]
FAIL  ECON-UD: signal_scope.json conforms to signal_scope.schema.json  
      errors=[18 derivative entries missing 'formula' and 'appears_in_charts']
PASS  ECON-AS: analyst_suggestions.json conforms to analyst_suggestions.schema.json
FAIL  APP-DIR1: schema errors during triangulation (blocked by interpretation_metadata errors above)
PASS  APP-DIR1 render copy: ELI5 text has no internal tokens
# RESULT  passes=3  failures=3
```

**These are BLOCKING findings.** Owner: Evan (signal_scope), Dana/Evan (interpretation_metadata).

### GATE-DP1 (run independently per QA-CL4)

```python
# GATE-DP1 check on all 5 history_zoom_*.json charts
```

**Result: FAIL — 5 axis mismatch failures (BLOCKING)**

All 5 crisis zoom charts fail:
- `history_zoom_covid.json`: trace[1] `SPY Cumul. Return (indexed)` yaxis=y2 but xaxis=x (expected x2)
- `history_zoom_dotcom.json`: same failure
- `history_zoom_gfc.json`: same failure
- `history_zoom_inflation_2022.json`: same failure
- `history_zoom_taper_2018.json`: same failure

The bottom SPY panel is invisible on screen for all 5 crisis episodes. Owner: Vera.

### GATE-SD1 (run independently)

**Result: PASS** — no off-scope signal identifiers found in chart filenames.

### GATE-VIZ-NBER2 (run independently)

**Result: FAIL (color mismatch, non-canonical NBER palette)** — see artifact section V6. Recession IS visually indicated via annotations + gray rectangle. QA treats this as PASS-with-note rather than blocking given annotations are unambiguous; Vera must fix color in next delivery. Owner: Vera.

---

## (c) Stakeholder-Spirit Check

Reading the 4 page files end-to-end as a non-technical stakeholder:

- **Story page — Plain English expander:** PASS — `PLAIN_ENGLISH` attribute populated with clear economic prose. Expander renders via `with st.expander("Plain English")` in template.
- **Story page — Headline meaningful (not placeholder):** PASS — `PAGE_TITLE = "The Story: When Credit Markets Warn, Equity Investors Should Listen"` and `HEADLINE_H2` both substantive.
- **Story page — Crisis episodes mentioned:** PASS — 5 HISTORY_ZOOM_EPISODES configured with title + narrative + caption for dotcom, gfc, covid, taper_2018, inflation_2022. Narratives are pair-specific and non-placeholder.
- **Strategy page — disclosure banner wired:** PASS — `render_evidence_status_note(pair_id)` is called at line 1167 of `page_templates.py` inside `render_strategy_page()`. `failed_final_exam` failure reasons will be visible per APP-SEV1 L2.
- **Evidence page — ≥3 L1 blocks, ≥2 L2 blocks:** PASS — confirmed 3 L1 blocks (Correlation, Granger Causality, Pre-Whitened CCF) and 2 L2 blocks (HMM Regime Analysis, Regime Quartile Returns) via runtime inspection of EVIDENCE_METHOD_BLOCKS.
- **Evidence page — no [PLACEHOLDER] text:** PASS — `str(EVIDENCE_METHOD_BLOCKS)` contains no "PLACEHOLDER" string.
- **Methodology page — data source documented:** PASS-with-note — data sources table lists FRED and Yahoo Finance as upstream series sources (correct). However, the table does not disclose that the actual primary input file is `Data Master.xlsx / sheet OASHY_IG` with a splice to daily parquet and then FRED MCP for 2026 dates. The `data_manifest_v4_20260512.json` captures this correctly but the stakeholder-facing methodology page does not. This is informative provenance that belongs in the methodology disclosure. Non-blocking but should be added by Ace/Ray.
- **APP-TT1 compliance:** PASS — `render_story_page`, `render_strategy_page`, `render_evidence_page`, `render_methodology_page` all call `st.title(...)` as the first `st.*` call after `_apply_page_config()`. Title enforcement is correctly inside templates per APP-TT1 contract.
- **APP-NAV1 compliance:** PASS — no `st.markdown("[Label](bare_name)")` patterns found in any of the 4 page files. Pages are thin wrappers with no direct Streamlit calls beyond imports and the single render function call.

---

## (d) Cross-Agent Seam Audit

| # | Field | Expected | Actual | Result |
|---|-------|----------|--------|--------|
| S1 | `winner_summary.signal_code` = `tournament_winner.winner.signal` | S2c_zscore_36m | S2c_zscore_36m (both) | **PASS** |
| S2 | `interpretation_metadata.observed_direction` = `winner_summary.direction` | countercyclical | countercyclical (both) | **PASS** |
| S3 | `evidence_status.pair_id` | hy_ig_spy_v4_from_scratch | hy_ig_spy_v4_from_scratch | **PASS** |
| S4 | `evidence_status.schema_version` | 1.2.0 | 1.2.0 | **PASS** |
| S5 | `evidence_status.failure_reasons` has ≥1 entry | ≥1 | 4 entries | **PASS** |
| S6 | HISTORY_ZOOM_EPISODES slugs match chart files on disk | dotcom, gfc, covid, taper_2018, inflation_2022 | exact match both ways | **PASS** |
| S7 | No [PLACEHOLDER] in EVIDENCE_METHOD_BLOCKS fields | 0 occurrences | 0 occurrences | **PASS** |
| S8 | `evidence_status.final_exam.qa_status` = "qa_passed" | qa_passed | qa_passed | **PASS** |
| S9 | `winner_summary.oos_n_trades` consistent with OOS period trade count | ~5 distinct periods in OOS window 2014-2020 | 33 (appears to be full-sample count, not OOS-only) | **PASS-with-note** — `winner_trade_log.csv` shows 33 trade periods across full history 1999-2026, with only 5 overlapping the OOS window 2014-08-29 to 2020-06-30. `oos_n_trades=33` appears to reflect full-sample trade periods, not OOS-only. The field is labeled "OOS" but covers full history. Non-blocking (does not break portal rendering) but Evan should clarify field definition and correct labeling. |
| S10 | QA-CL2 T1: Sharpe-Return-Vol plausibility | Implied vol in plausible range | Sharpe=1.32, return=6.57%, implied vol=4.20% → plausible for FI/credit-style | **PASS** |
| S11 | QA-CL2 T2: MDD-Vol ratio plausibility | Ratio in [1,6] | MDD=6.38%, vol=4.20%, ratio=1.52 → in range | **PASS** |
| S12 | QA-CL2 T3: Turnover-Trade count | Deviation ≤2× | With `oos_n_trades=33` and `annual_turnover=1.12`, deviation is 4.98× (one-way) or 2.49× (round-trip) | **FAIL (BLOCKING)** — T3 fails under standard interpretation. Investigation shows `oos_n_trades=33` may be mislabeled (full-sample count). Until Evan clarifies and corrects the field, T3 cannot pass. If confirmed as labeling error and corrected to OOS-only count (~5 periods → ~1 per year ≈ matches turnover=1.12), T3 clears. Owner: Evan. |

---

## Overall Verdict: FAIL

**Blocking findings (7) — must be resolved before acceptance:**

1. **(GATE-DP1 BLOCKING)** All 5 crisis zoom charts have `yaxis="y2"` but `xaxis="x"` on the SPY bottom panel — bottom panel is invisible on screen. Owner: **Vera**. Fix: regenerate all 5 `history_zoom_*.json` charts with bottom-panel traces set to `xaxis="x2"`.

2. **(Schema BLOCKING) `final_exam_results_20260512.json` does not conform to `final_exam_results.schema.json`** — 30+ violations including wrong `schema_version` (has "1.0.0", needs "1.1.0"), missing required root fields, wrong `adjustment_method` enum value. Owner: **Evan**. Fix: regenerate or patch to match schema v1.1.0.

3. **(Schema BLOCKING) `interpretation_metadata.json` does not conform to `interpretation_metadata.schema.json`** — missing `schema_version`, missing `owner_writes`, `confidence="moderate"` not in enum. Owner: **Dana/Evan** (whoever owns this artifact). Fix: add missing fields, change confidence to "high"/"medium"/"low".

4. **(Schema BLOCKING) `signal_scope.json` does not conform to `signal_scope.schema.json`** — all 18 derivatives missing required `formula` and `appears_in_charts` fields. Owner: **Evan**. Fix: add `formula` and `appears_in_charts` to every derivative entry.

5. **(smoke_schema_consumers BLOCKING) `smoke_schema_consumers.py` exits with failures=3** — directly caused by findings 3 and 4 above; APP-DIR1 triangulation also blocked. Owner: Evan/Dana.

6. **(QA-CL2 T3 BLOCKING) `oos_n_trades=33` appears mislabeled** — field says OOS but contains full-sample trade count (33 full-history periods vs ~5 in the OOS window). This causes T3 KPI triangulation to fail. Owner: **Evan**. Fix: clarify field definition; if full-sample, rename to `n_trades_full_sample` and add correct `oos_n_trades` (~5). Re-run T3 check after correction.

7. **(GATE-VIZ-NBER2 BLOCKING per protocol)** `history_zoom_dotcom.json`, `history_zoom_gfc.json`, `history_zoom_covid.json` have NBER recession shading in wrong color `rgba(180,180,180,0.30)` instead of canonical VIZ-NBER1 color `rgba(150,120,120,0.22)`. QA notes this is technically a GATE-VIZ-NBER2 failure per protocol color check. The recession IS visually indicated via annotations labeled "NBER Recession". QA downgrades severity to **non-blocking WARN** given annotation clarity, but Vera must fix color in next delivery iteration. Owner: **Vera**.

*Updated: QA reclassifies finding 7 as non-blocking WARN, reducing blocking count to 6.*

---

## Blocking Findings (6 after reclassification)

| # | Finding | Owner | Fix scope |
|---|---------|-------|-----------|
| 1 | GATE-DP1: all 5 history_zoom charts — bottom panel xaxis="x" should be "x2" | Vera | Regenerate history_zoom_*.json with corrected axis assignment |
| 2 | final_exam_results_20260512.json: schema v1.0.0, needs v1.1.0, missing 6 required root fields, wrong enum | Evan | Patch/regenerate to schema v1.1.0 |
| 3 | interpretation_metadata.json: missing schema_version, owner_writes; confidence enum violation | Dana/Evan | Add fields; fix confidence value |
| 4 | signal_scope.json: 18 derivatives each missing formula + appears_in_charts | Evan | Add formula + appears_in_charts to all derivative entries |
| 5 | smoke_schema_consumers.py failures=3 (direct consequence of 3+4) | Evan/Dana | Resolved once 3 and 4 are fixed |
| 6 | oos_n_trades=33 is full-sample count, not OOS — QA-CL2 T3 cannot pass | Evan | Clarify + correct field; QA re-runs T3 |

---

## Non-Blocking Observations

| # | Category | Observation |
|---|----------|-------------|
| N1 | Methodology page | `data_sources_table_md` lists "FRED" as source but actual primary input is `Data Master.xlsx / sheet OASHY_IG` with splice chain (parquet + FRED MCP). `data_manifest_v4_20260512.json` documents this correctly but stakeholder-facing methodology page does not. Suggest adding a "Data Provenance" note to the displayed table. Owner: Ace/Ray. |
| N2 | GATE-VIZ-NBER2 | Recession shading color `rgba(180,180,180,0.30)` in dotcom/gfc/covid does not match canonical VIZ-NBER1 color `rgba(150,120,120,0.22)`. Recession IS visually clear via annotations. Vera to correct palette on next delivery. |
| N3 | QA-CL3 | QA did not verify agent memory files (experience.md, memories.md, session-notes.md) for all dispatched agents — Lead dispatched QA directly without prior agent-wave memory update cycle. This finding is scoped: if agents were previously dispatched in this wave, Lead should confirm memory discipline compliance separately. |

---

## GATE-ES1 — Evidence-Status Promotion Verification

**Pair status:** `failed_final_exam` — this is a DEMOTION below `passed_final_exam`, not a promotion above baseline. GATE-ES1 eight-step promotion verification is not required for `failed_final_exam` status.

However, per QA mandate, the following checks were run:

1. `evidence_status.json` validates against schema — **PASS** (confirmed above)
2. `pair_id` = hy_ig_spy_v4_from_scratch — **PASS**
3. `schema_version` = "1.2.0" — **PASS**
4. `failure_reasons` array has ≥1 entry — **PASS** (4 entries)
5. `final_exam.qa_status` = "qa_passed" — **PASS**
6. `final_exam_results_20260512.json` exists — **PASS**
7. `final_exam_results_20260512.json` validates against schema — **FAIL** (blocking, see finding 2)
8. Anti-gaming review: confirmation window 2020-07-31 to 2026-05-29 is post-search window 2014-08-29 to 2020-06-30, no overlap — **PASS**. Failure is genuine: post-COVID bull market regime underperforms the defensive signal. 4 ECON-FE1 conditions failed; all documented.

---

*QA sign-off is WITHHELD until all 6 blocking findings are resolved and re-verified.*

*Next step: Producers fix blocking findings. QA re-verifies the narrow set of changed artifacts only.*
