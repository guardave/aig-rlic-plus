# Quincy — Outstanding Work

*Last updated: 2026-04-24 (Wave 10J/10K checkpoint)*

---

## Active — awaiting Lead decision

### OW-4: GATE-ES1 evidence-status promotion gate arbitration

**Status:** Drafted by Quincy 2026-05-01; awaiting Lead/Evan arbitration.
**Evidence:** `_pws/qa-quincy/evidence-status-final-exam-qa-gate-20260501.md`.
**Impact:** No pair should be promoted from `found_in_search` to `passed_final_exam` until Lead accepts final-exam thresholds/artifact shape and QA verifies reproducibility plus DOM honesty.
**What Quincy does next:** after Evan/Lead define the confirmation-output schema/metrics, convert the draft gate into final QA SOP wording or verify the producer implementation without editing econometrics-owned files.

### OW-1: Perceptual PNGs — 9/10 pairs at GATE-HZE1 WARN

**Status:** WARN (not FAIL). No `history_zoom_*.json` on disk for 9 of 10 pairs.
**Impact:** "How the Signal Performed in Past Crises" Story section silently absent for 9 pairs.
**Blocker:** Lead must decide: dispatch Vera for bulk zoom chart generation (Wave 10K) or defer.
**What Quincy does next:** once Vera commits zoom charts for a pair, GATE-HZE1 auto-promotes to FAIL if heading absent. No Quincy action until charts are committed.

### OW-2: GATE-32 severity flip — GATE-VIZ-NBER1 WARN → FAIL

**Status:** Awaiting Lead confirmation.
**Evidence:** NBER shading confirmed present in DOM HTML across all 10 pairs in Wave 10J verify. Current scoring: absence = WARN. Proposed change: absence = FAIL (same tier as breadcrumb nav).
**What Quincy does next:** once Lead confirms, update `scripts/cloud_verify.py` to promote GATE-VIZ-NBER1 from WARN to FAIL. One-line change in the scoring block.

### OW-3: GATE-HZE1 implementation in scripts/cloud_verify.py

**Status:** SOP rule authored with full pseudocode. Ace is designated implementer (cross-agent impact log, 2026-04-24).
**Impact:** GATE-HZE1 currently enforced only as a manual HABIT-QA1 DOM-read check. Script automation pending.
**What Quincy does next:** once Ace implements the check, verify the implementation matches the SOP pseudocode and run a smoke verify to confirm no false positives/negatives. Sign off in handoff.

---

## Deferred backlog (pre-existing, unchanged)

| ID | Summary | Status |
|----|---------|--------|
| BL-002 | ECON-UD cross-pair retro (5 pairs) | Deferred by Lead |
| BL-003 | ECON-AS companion placeholders (5 pairs) | Deferred by Lead |
| BL-004 | APP-NP1 Narrative-to-Page Prose Sourcing rule | Deferred by Lead |
| BL-801 | `strategy.py:197` key drift (`max_drawdown` vs `oos_max_drawdown`) | Deferred by Lead |
| BL-802 | `turnover_basis` enum in winner_summary.schema.json | Deferred by Lead |
| BL-803 | smoke_loader.py page-prefix mismatch + hardcoded chart names | Deferred by Lead |

All six filed in `docs/backlog.md` Active Deferrals.
