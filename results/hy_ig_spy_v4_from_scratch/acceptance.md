# Acceptance — hy_ig_spy_v4_from_scratch

**Pair ID:** hy_ig_spy_v4_from_scratch  
**Evidence status:** `failed_final_exam` — production-eligible per DPS-PRE1; disclosure banner required on Strategy page.  
**Date:** 2026-05-12  
**Branch:** 260430

---

## QA Sign-off (Quincy) — 2026-05-12

**Verdict: CONDITIONAL-PASS**

Conditional on the `failed_final_exam` disclosure banner rendering correctly on the Strategy page (wired via `render_evidence_status_note` in `render_strategy_page` — confirmed present). No Lead override required; DPS-PRE1 explicitly authorises production eligibility with banner for `failed_final_exam` pairs.

**Blocking findings: none** — all 6 original blocking findings resolved and independently re-verified.

**Non-blocking observations (carried forward for Lead/Vera attention):**

1. **(N1)** Methodology `data_sources_table_md` lists "FRED" as source but actual primary input is `Data Master.xlsx / sheet OASHY_IG` with splice chain. `data_manifest_v4_20260512.json` documents this correctly; stakeholder-facing methodology page does not. Suggest adding a "Data Provenance" note. Owner: Ace/Ray.
2. **(N3)** QA-CL3 agent memory discipline not independently verified (QA dispatched directly by Lead; prior agent wave memory cycle not in scope of this re-verification). Lead to confirm if applicable.

**Re-verification summary (producer fixes accepted):**

| Fix | Commit | Re-verify result |
|-----|--------|-----------------|
| GATE-DP1: history_zoom xaxis corrected + NBER color fixed | 9c0b644 (Vera) | PASS |
| final_exam_results patched to schema v1.1.0 | df77391 (Evan) | PASS |
| interpretation_metadata: schema_version, owner_writes, confidence fixed | d744bf5 (Evan/Dana) | PASS |
| signal_scope: formula + appears_in_charts added to all 18 derivatives | 8c74388 (Evan) | PASS |
| winner_summary: oos_n_trades=5 (OOS-only); total_n_trades=33 added | 37071e2 (Evan) | PASS |
| smoke_schema_consumers.py | consequence of above | PASS — failures=0 |

**QA-CL1 final checklist status:**

| Item | Status |
|------|--------|
| All schema claims validated (validate_schema.py exit 0) | PASS |
| smoke_loader.py failures=0 | PASS |
| smoke_schema_consumers.py failures=0 | PASS |
| GATE-DPS1: 0 FAIL, 1 WARN (expected), 126 PASS | PASS |
| GATE-DP1: all history_zoom bottom-panel traces xaxis=x2 | PASS |
| GATE-VIZ-NBER2: canonical rgba(150,120,120,0.22) in dotcom/gfc/covid | PASS |
| GATE-SD1: no off-scope signal identifiers in chart files | PASS |
| QA-CL2 T1-T3 KPI triangulation | PASS (all 3 invariants) |
| Direction triangulation APP-DIR1 (Evan=countercyclical, Dana=countercyclical) | PASS |
| Evidence page: ≥3 L1 blocks, ≥2 L2 blocks, no [PLACEHOLDER] | PASS |
| Strategy page: render_evidence_status_note wired | PASS |
| APP-TT1: st.title as first call in all 4 templates | PASS |
| APP-NAV1: no bare markdown nav links | PASS |
| GATE-ES1: evidence_status failed_final_exam — anti-gaming verified, holdout sealed | PASS |
| GATE-HZE1: 5 crisis episodes configured, charts on disk, narratives non-placeholder | PASS |
| Signals parquet committed (GATE-29) | PASS — git ls-files confirms signals_v4_20260512.parquet |

Quincy sign-off: ✓

---

## Lead Acceptance Sign-off (Lesandro) — 2026-05-12

**Verdict: ACCEPTED**

QA CONDITIONAL-PASS accepted. Condition satisfied — disclosure banner confirmed wired via `render_evidence_status_note` in `render_strategy_page`.

**Non-blocking N1 disposition:** CLOSED — no action required. The xlsx data is FRED data downloaded before the April 2026 ICE licensing restriction. Methodology page citing "FRED" as source is accurate.

**Wave outcome:** `hy_ig_spy_v4_from_scratch` is the reference implementation — first pair built against the full Dashboard Page Standard and GATE-DPS1. Evidence status `failed_final_exam` is the honest result of a genuine regime effect in the 2020-2026 holdout. The pair ships with full disclosure.

**Data source precedent:** `data/Data Master.xlsx / OASHY_IG` is now the canonical source for ICE BofA HY and IG OAS series going back to 1996, supplemented by FRED MCP for the rolling tail. This pattern applies to all future credit pairs.

Lesandro sign-off: ✓
