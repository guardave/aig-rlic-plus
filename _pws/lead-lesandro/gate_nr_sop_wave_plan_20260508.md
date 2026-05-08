# Wave Plan: GATE-NR-SOP — Fix Two SOP Gaps Causing Systematic GATE-NR Failures
**Date:** 2026-05-08
**Lead:** Lesandro
**Status:** OPEN

## Motivation

Cloud verify (2026-05-08T20:58Z) returned 14 FAILs across all 10 pairs. Root cause:
`gate_nr_result = FAIL` on every story page and 4 evidence pages. Two distinct SOP gaps:

**Gap 1 — `target_symbol` blank in `interpretation_metadata.json` (3 pairs)**
`hy_ig_v2_spy`, `indpro_xlp`, `umcsent_xlv` have `target_symbol = ""`. GATE-NR allows only
`{target_symbol, indicator_id}` — with blank target_symbol, it allows only the indicator_id,
so any mention of SPY/XLP/XLV in the narrative is rejected as a wrong-pair reference. Root
cause: DATA-D6 names `target_symbol` as Dana's field but the checklist and rule body do NOT
require it to be non-blank. The schema apparently permits empty string.

**Gap 2 — `gate_nr_comparison_whitelist` never populated (all pairs)**
Legitimate comparisons trigger GATE-NR on pairs where `target_symbol` IS correctly set:
- S&P 500 on SPY-target pairs (8 pairs)
- VIX on vix_vix3m_spy story/evidence
- VIX on non-VIX pairs (indpro_spy, permit_spy, sofr_ted_spy) where narrative mentions VIX
  in an economic comparison

QA-CL5/GATE-NR documents the whitelist mechanism (line 819 of qa-agent-sop.md). RES-NR1
documents that Ray verifies instrument references. But NEITHER rule requires the whitelist
to be populated as a delivery gate. It is only invoked reactively. The gap: no SOP rule
says "when your narrative legitimately references an out-of-pair instrument for comparison,
add it to `gate_nr_comparison_whitelist` before handoff."

## Design decisions

1. **SOP-first per LEAD-SOP1.** No artifact fixes until both SOP patches are authored and
   ratified.
2. **Gap 1 is Dana's domain** — DATA-D6 rule body + delivery checklist. Dana patches her own
   SOP (LEAD-DL1). Lead does NOT edit data-agent-sop.md.
3. **Gap 2 spans Ray (producer) and Quincy (gate owner).** Ray's RES-NR1 gains a whitelist
   step; Quincy's QA-CL5/GATE-NR gains a delivery gate requirement. Each agent patches their
   own SOP. Single dispatch covers both (one agent call, two files).
4. **Lead SOP:** no change needed — GATE-NR already listed in META-DM matrix under Quincy
   (cloud_verify.py gate added/removed → All). No new matrix rows required.
5. **Artifact fixes (interpretation_metadata.json backfill)** are a separate follow-on wave
   dispatched after both SOP patches pass acceptance.

---

## Change Items

### GATE-NR-SOP-01 — Add `target_symbol` non-blank requirement to DATA-D6
**Owner:** Dana (data-agent-sop.md — Dana's file per LEAD-DL1)

In `docs/agent-sops/data-agent-sop.md`, within **Rule DATA-D6**:

**Rule body addition** — after the existing Procedure step 1, add:

> **Required non-blank fields (blocking):** `target_symbol` MUST be set to the ETF or index
> ticker that is the pair's return target (e.g., `"SPY"`, `"XLP"`, `"XLV"`). An empty string
> is not acceptable — it causes GATE-NR to reject all instrument references in the pair's
> narrative. If the target is unclear, escalate to Lead before delivery; do not ship with
> `target_symbol: ""`.

**Checklist addition** — in Dana's EOD/delivery checklist, add a bullet under the DATA-D6
checklist item:

> - [ ] `target_symbol` is non-blank and matches the pair's return target ticker.

**Acceptance (positive):**
```
grep -c "target_symbol.*non-blank\|non-blank.*target_symbol" docs/agent-sops/data-agent-sop.md
```
→ ≥ 1

**Acceptance (negative):**
```
grep -c "target_symbol.*non-blank" docs/agent-sops/team-coordination.md docs/agent-sops/lead-agent-sop.md
```
→ 0 (rule lives in data SOP only, not duplicated)

---

### GATE-NR-SOP-02 — Add whitelist population step to RES-NR1
**Owner:** Ray (research-agent-sop.md — Ray's file per LEAD-DL1)

In `docs/agent-sops/research-agent-sop.md`, within **Rule RES-NR1**:

**Rule body addition** — after the existing Verification step, add:

> **Whitelist obligation:** When narrative prose legitimately references an out-of-pair
> instrument for comparison (e.g., "Unlike SPY, XLP tends to..." on an XLP pair; or "the
> VIX spiked" as economic context on a non-VIX pair), Ray MUST add those instrument names
> to `gate_nr_comparison_whitelist` in `results/{pair_id}/interpretation_metadata.json`
> before handoff. An empty whitelist on a pair whose narrative contains any comparative
> instrument reference is a RES-NR1 violation. Log the whitelist entries in the handoff
> note alongside the RES-NR1 check line:
> ```
> RES-NR1 whitelist: gate_nr_comparison_whitelist = ["S&P 500", "VIX"]
> ```

**Checklist addition** — in Ray's delivery checklist, add under the RES-NR1 item:

> - [ ] `gate_nr_comparison_whitelist` reviewed; any legitimate out-of-pair instrument
>   references added before handoff.

**Acceptance (positive):**
```
grep -c "gate_nr_comparison_whitelist" docs/agent-sops/research-agent-sop.md
```
→ ≥ 2 (rule body + checklist)

**Acceptance (negative):**
```
grep -c "gate_nr_comparison_whitelist" docs/agent-sops/data-agent-sop.md docs/agent-sops/qa-agent-sop.md
```
→ 0 for data-agent-sop.md (Dana doesn't own this step)
(qa-agent-sop.md already has the term — that existing reference is acceptable, not duplicating the producer obligation)

---

### GATE-NR-SOP-03 — Add whitelist delivery gate to QA-CL5/GATE-NR
**Owner:** Quincy (qa-agent-sop.md — Quincy's file per LEAD-DL1)

In `docs/agent-sops/qa-agent-sop.md`, within **QA-CL5 / GATE-NR**:

**Rule body addition** — after the existing scope limitation paragraph (line ~819), add:

> **Delivery gate (blocking):** Before accepting a pair's Story/Evidence pages as GATE-NR
> clean, Quincy checks that `results/{pair_id}/interpretation_metadata.json` contains:
> (a) a non-blank `target_symbol`, AND (b) a `gate_nr_comparison_whitelist` entry for every
> instrument name in the narrative that is not the pair's own target or indicator. If either
> is missing, the pair fails QA-CL5 and is returned to Ray (whitelist) or Dana
> (target_symbol) before cloud verify is run.

**Acceptance (positive):**
```
grep -c "Delivery gate\|delivery gate" docs/agent-sops/qa-agent-sop.md
```
→ ≥ 1 (new gate text)

**Acceptance (negative):**
```
grep -c "Delivery gate.*target_symbol" docs/agent-sops/research-agent-sop.md docs/agent-sops/data-agent-sop.md
```
→ 0 (gate enforcement lives in QA SOP, not duplicated in producer SOPs)

---

### GATE-NR-SOP-04 — Log in `docs/sop-changelog.md`
**Owner:** Lead (Lead-owned file)

Add changelog entry: GATE-NR-SOP wave — two producer-side gaps (DATA-D6 `target_symbol`
non-blank, RES-NR1 whitelist obligation) + QA-CL5 delivery gate.

---

## Dispatch plan

| Step | Who | Files | How |
|------|-----|-------|-----|
| 1 | Lead | `docs/sop-changelog.md` | Direct write (Lead-owned) |
| 2 | Single agent dispatch | `data-agent-sop.md`, `research-agent-sop.md`, `qa-agent-sop.md` | One agent call; three files |
| 3 | Lead audit | All four files | Re-run all acceptance commands |

## Post-wave artifact follow-on (separate wave)

After SOP patches pass acceptance, dispatch Dana + Ray to backfill the 10 affected pairs:
- Dana: populate `target_symbol` in `interpretation_metadata.json` for 3 pairs
  (hy_ig_v2_spy, indpro_xlp, umcsent_xlv)
- Ray: review all 10 pairs' narratives and populate `gate_nr_comparison_whitelist`
  where legitimate comparisons exist
- Quincy: re-run cloud_verify.py; target 0 GATE-NR FAILs
