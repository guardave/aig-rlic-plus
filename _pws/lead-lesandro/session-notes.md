# Session Notes — Lead Lesandro
**Date:** 2026-05-11
**Branch:** 260430

## Session Accomplishments

### 1. Landing card fixes (three root causes)
- `app.py:240` — card title used raw `indicator → target` instead of `display_name`
- `pair_registry.py` — `val_sharpe` vs `oos_sharpe` column detection added (retro CSV used different name)
- `evidence_status.json` for both v3 forks — rewritten to conform to schema v1.0.0 (was using wrong field names)

### 2. META-CDR: Cross-Domain Review rule (new meta-rule)
- Codified observation from Wave 10I: no single producer's gate covers cross-agent seams
- Standard Task Flow updated: Step 10 = Lead CDR, Quincy now step 11
- Pipeline summary updated from "Producer → QA → Lead" to "Producer → Lead CDR → QA → Lead acceptance"
- Files: `team-coordination.md`, `lead-agent-sop.md`, `sop-changelog.md`

### 3. V3 experiment fork full rebuild (V3-EXP-RERUN wave)
Full agent pipeline dispatched:
- **Evan**: fixed DSR underflow (norm.cdf → norm.sf, clamped to 1e-15), normalised `val_sharpe` → `oos_sharpe` in retro CSV, regenerated all artifacts
- **Vera**: 4 charts × 2 forks + perceptual PNGs (VIZ-CV1 compliance)
- **Ray**: concise experiment narratives for Evidence/Strategy/Methodology × 2 forks; RES-NR1 clean
- **Ace**: 6 portal pages + 2 pair_configs; link verification performed
- **Lead CDR**: caught `winner_summary.json` field name inconsistency (retro had `val_sharpe`, missing `holdout_sharpe`) — fixed before QA
- **Quincy**: 2 blocking FAILs found (VIZ-CV1 PNGs missing, semantic inversion bug "unchanged: False"); both fixed and re-verified; GATE-31 PASS

### 4. Breadcrumb link fix (all 8 v3 pages)
All `st.markdown("...[Evidence](bare_name)...")` replaced with `st.page_link("pages/file.py")`. Streamlit does not route bare markdown links — they 404. Committed after verifying all 8 pages syntax-clean.

### 5. evidence_status: needs_final_exam → passed_final_exam
Both forks had holdout exam fully run (252-day holdout, 7/10 ECON-FE1 conditions). Status was wrong. Evan updated both to `passed_final_exam` with full `final_exam` lineage block, schema v1.1.0, `qa_status: qa_passed`.

### 6. APP-TT1: Pair title at page top (new rule)
- `st.title(display_name)` must be first content after `st.set_page_config()` on every page
- Applied to all 8 v3 fork pages immediately
- Codified in `appdev-agent-sop.md`, logged in `sop-changelog.md`

## Lead CDR lesson (first real-world use)
CDR caught the `winner_summary.json` field name inconsistency between rerun and retro before Quincy. The schema gap (retro used `val_sharpe`/missing `holdout_sharpe`) would have caused silent blank metrics on the retro landing card. CDR worked as designed.

## Key Failure Pattern Confirmed
Ace used `st.markdown` with bare page name links `[Evidence](90_hy_ig_spy_v3_rerun_evidence)` — these are not Streamlit routes and 404. Correct pattern is `st.page_link("pages/prefix_pair_pagetype.py")`. This should be added to Ace's SOP anti-patterns.

## Commits this session
- cf6505c: Landing card title, Sharpe/MDD, evidence_status schema fix
- 8c17611: META-CDR SOP addition
- (multiple): V3 experiment rebuild (Evan/Vera/Ray/Ace/Quincy)
- 85d6438: Lead CDR fix — retro winner_summary schema
- 1610c23: Breadcrumb fix (st.page_link)
- 0e8e62a: passed_final_exam story page text
- 51d0cd4: APP-TT1 rule + page fixes
- 86a5c82: wave plan + cloud_verify URL
