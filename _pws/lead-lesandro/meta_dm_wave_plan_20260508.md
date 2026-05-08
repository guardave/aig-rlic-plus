# Wave Plan: META-DM — Dispatch Matrix & EOD Dispatch Gate
**Date:** 2026-05-08
**Lead:** Lesandro
**Status:** OPEN

## Motivation

After promoting `hy_ig_v2_spy` to `passed_final_exam`, the qualitative narrative (Ray) was not reviewed for reconciliation with the updated three-period split metrics. No SOP rule required Ray to be notified. Adding per-agent rules would be combinatorially expensive and drift-prone (META-NCD violation). A static dispatch matrix in `team-coordination.md` plus a two-item EOD extension is the minimal correct fix: one canonical table, one pointer in each role SOP, and a Lead wave-closure obligation.

## Design decisions

1. **Matrix lives in `team-coordination.md` only** — team-level contract, not role knowledge.
2. **Role SOPs get one cross-reference line** — no table, no enumeration.
3. **EOD-Lightweight gains one universal step** — "consult META-DM" — in `team-coordination.md` only; existing role-specific phase checklists are not duplicated.
4. **Lead SOP gains a wave-closure step** — read open dispatch obligations, route, confirm.

---

## Change Items

### META-DM-01 — Add META-DM rule + matrix to `team-coordination.md`
**Owner:** Lead (implements directly — Lead-owned file)
**File:** `docs/agent-sops/team-coordination.md`

Insert a new section **Dispatch Matrix (Meta-Rule META-DM)** after the META-AVD block (after line 830). Content:

**Rule body:** When any agent completes work that changes an artifact listed in the matrix below, Lead consults the matrix at wave closure and dispatches the listed downstream agents for consequential review before the wave is closed. Downstream review is not optional — it is a wave-closure gate. If Lead determines a listed downstream agent is not materially affected (e.g., Ray's narrative contains no OOS date references and the split dates changed), Lead records the rationale for skipping in the wave closure note. Silent skips without rationale are a META-DM violation.

**The matrix:**

| Producer | Changed artifact / event | Must review |
|----------|--------------------------|-------------|
| Evan | `oos_split_record.json` dates change | Ray, Vera, Ace |
| Evan | `winner_summary.json` winner changes | Ray, Vera, Ace, Quincy |
| Evan | `evidence_status.json` status promotion | Ray, Ace, Quincy |
| Evan | Any owned schema version bump | Quincy, Ace |
| Dana | `signal_scope.json` change | Evan, Quincy |
| Dana | Dataset columns added / removed | Evan |
| Vera | Chart artifact renamed / removed | Ace, Quincy |
| Ray | Narrative KPI values change | Ace |
| Ace | Portal template structure change | Quincy |
| Quincy | `cloud_verify.py` gate added / removed | All |
| Lead | Schema version bump (META-SBP) | All affected owners |

**Cross-references:** META-NCD (single canonical location), META-AVD (two-sided acceptance at wave closure), META-SRV (dispatch evidence recorded).

**Acceptance (positive):**
`grep -c "META-DM" docs/agent-sops/team-coordination.md` → ≥ 3
`grep -c "Must review\|must review" docs/agent-sops/team-coordination.md` → ≥ 1

**Acceptance (negative):**
`grep -c "Dispatch Matrix" docs/agent-sops/econometrics-agent-sop.md docs/agent-sops/data-agent-sop.md docs/agent-sops/research-agent-sop.md docs/agent-sops/visualization-agent-sop.md docs/agent-sops/appdev-agent-sop.md docs/agent-sops/qa-agent-sop.md` → 0
(Matrix must not be duplicated in role SOPs.)

---

### META-DM-02 — Extend EOD-Lightweight in `team-coordination.md`
**Owner:** Lead (implements directly)
**File:** `docs/agent-sops/team-coordination.md`

The EOD-Lightweight block is the canonical source (role SOPs copy it). Add a fourth step after the existing three:

> **4. Dispatch gate** — For every artifact you changed this session, check the META-DM matrix in `docs/agent-sops/team-coordination.md`. If any downstream agent appears in the "Must review" column, note it in your handoff note so Lead can route at wave closure. Do not dispatch directly — Lead owns routing decisions.

**Acceptance (positive):**
`grep -c "Dispatch gate\|META-DM" docs/agent-sops/team-coordination.md` → ≥ 2

**Acceptance (negative):**
`grep -c "Dispatch gate" docs/agent-sops/data-agent-sop.md docs/agent-sops/econometrics-agent-sop.md docs/agent-sops/research-agent-sop.md docs/agent-sops/visualization-agent-sop.md docs/agent-sops/appdev-agent-sop.md docs/agent-sops/qa-agent-sop.md` → 0
(Step 4 must not be duplicated in role SOPs — cross-reference only.)

---

### META-DM-03 — Add cross-reference line to each role SOP (×6)
**Owner:** Each role agent implements their own SOP (LEAD-DL1)
**Files:** All six role SOPs

In each role SOP's EOD-Lightweight section, replace the existing three-step block footer (or add after step 3) with:

> **Cross-reference:** Step 4 (Dispatch gate) is defined in `docs/agent-sops/team-coordination.md § EOD-Lightweight`. Consult META-DM there for the full dispatch matrix.

**Single dispatch covers all six:** one agent call, six files.

**Acceptance (positive):**
```
grep -c "META-DM" docs/agent-sops/data-agent-sop.md
grep -c "META-DM" docs/agent-sops/econometrics-agent-sop.md
grep -c "META-DM" docs/agent-sops/research-agent-sop.md
grep -c "META-DM" docs/agent-sops/visualization-agent-sop.md
grep -c "META-DM" docs/agent-sops/appdev-agent-sop.md
grep -c "META-DM" docs/agent-sops/qa-agent-sop.md
```
All → ≥ 1

**Acceptance (negative):**
```
grep -c "Must review\|Dispatch Matrix" docs/agent-sops/data-agent-sop.md docs/agent-sops/econometrics-agent-sop.md docs/agent-sops/research-agent-sop.md docs/agent-sops/visualization-agent-sop.md docs/agent-sops/appdev-agent-sop.md docs/agent-sops/qa-agent-sop.md
```
→ 0

---

### META-DM-04 — Add wave-closure dispatch step to Lead SOP
**Owner:** Lead (implements directly — Lead-owned file)
**File:** `docs/agent-sops/lead-agent-sop.md`

In the wave closure / acceptance section, add a mandatory step before sign-off:

> **META-DM gate:** For every artifact changed in this wave, consult the META-DM matrix. For each downstream agent listed: (a) dispatch for consequential review, or (b) record explicit rationale for skip in the wave closure note. Wave may not be marked CLOSED until all META-DM obligations are dispatched or explicitly skipped with rationale.

**Acceptance (positive):**
`grep -c "META-DM" docs/agent-sops/lead-agent-sop.md` → ≥ 1

**Acceptance (negative):**
`grep -c "Dispatch Matrix" docs/agent-sops/lead-agent-sop.md` → 0
(Lead SOP cross-references META-DM; does not duplicate the matrix.)

---

### META-DM-05 — Register META-DM in `docs/standards.md`
**Owner:** Lead (implements directly)
**File:** `docs/standards.md`

Add META-DM row to the META section.

**Acceptance (positive):**
`grep -c "META-DM" docs/standards.md` → 1

---

### META-DM-06 — Log in `docs/sop-changelog.md`
**Owner:** Lead (implements directly)

---

## Execution order
1. Lead: META-DM-01, 02, 04, 05, 06 (all Lead-owned files — done in this wave directly)
2. Single agent dispatch: META-DM-03 (six role SOPs, one agent call)
3. Lead audit: re-run all acceptance commands

## Post-wave obligation (META-DM applied retroactively)
The `hy_ig_v2_spy` three-period re-run changed `oos_split_record.json` dates and promoted `evidence_status.json`. Per the new matrix: Ray, Vera, Ace, Quincy are downstream. These reviews are the first consequential dispatches under META-DM — to be run as a separate wave (ECON-3PERIOD-DOWNSTREAM) immediately after this wave closes.
