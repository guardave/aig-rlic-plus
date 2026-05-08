# BL-SOP-NORMALIZE — Change Plan

**Author:** Lead Lesandro
**Date:** 2026-05-08
**Wave ID:** BL-SOP-NORMALIZE
**Goal:** Establish single source of truth (SSoT) for every concept used across two or more SOPs. Reduce drift surface area. Author META-NCD as the enforcement rule.

---

## Verification mechanism (read this first)

Every item below has a **deterministic acceptance criterion**: a shell command (or set of commands) and the expected output. The agent who owns the item must:

1. Apply the change.
2. Run the acceptance command(s) verbatim.
3. Paste the command output verbatim into their handoff entry on the status board.

Lead re-runs the same commands in NORM-008 (closing audit). Outputs must match. Items where the audit output disagrees with the agent's reported output are FAIL and re-dispatched.

**No prose self-attestation accepted as evidence.** The agent saying "I removed all five definitions" is not evidence. The grep output is.

This adapts META-SRV from "every claim must carry verification" to "every wave item carries the verification spec before the work starts."

---

## Items

### NORM-001 — Author META-NCD rule
**Owner:** Lead
**Files modified:** `docs/agent-sops/team-coordination.md`
**Action:** Add a new META section "Normalization & Concept Discipline (META-NCD)". Rule body states: any concept (term definition, field enumeration, enum set, code block, status vocabulary, severity scheme) used in 2+ rulebooks must declare exactly one canonical location; other locations cite the canonical via cross-reference. Authoring a duplicate definition is a META-NCD violation. Quincy spot-audits cross-rulebook concept overlap once per quarter.
**Acceptance:**
```bash
grep -c "^### Normalization & Concept Discipline" docs/agent-sops/team-coordination.md
# Expected: 1
grep -c "META-NCD" docs/agent-sops/team-coordination.md
# Expected: >= 5  (rule heading + cross-references)
```

---

### NORM-002 — Author glossary scaffold
**Owner:** Lead
**Files modified:** `docs/glossary.md` (new file)
**Action:** Create `docs/glossary.md` with H2 sections for every term identified during the Phase 1/3 review as appearing in 2+ SOPs. Initial 15 terms (Lead-drafted definition, agents amend in NORM-003):
1. OOS window / confirmation window / search window
2. Perceptual render (perceptual PNG, kaleido check)
3. Thin wrapper (page-template thin-wrapper contract)
4. Page template
5. Pair config module
6. Sidecar (`_meta.json` chart sidecar; `_manifest.json` dataset sidecar)
7. Disposition (chart disposition: consumed / suggested / retired)
8. Tournament winner
9. Block bootstrap (stationary / circular block)
10. Smoke test (vs. preflight, vs. cloud verify)
11. PASS-with-note
12. Trigger card (instructional trigger card)
13. `_REPO_ROOT` anchor
14. Narrative instrument reference
15. Episode triad (long-lead / coincident / failure-case)

Each H2 has: short definition (1–3 sentences), canonical authority (where the rule that owns the term lives), cross-reference list. No prose duplication of what already lives in the rule body — the glossary is the term **definition** only; the rule says how the term is used.
**Acceptance:**
```bash
ls docs/glossary.md
# Expected: file exists
grep -c "^## " docs/glossary.md
# Expected: >= 15
wc -l docs/glossary.md
# Expected: >= 60
```

---

### NORM-003 — Per-agent glossary review and amendment
**Owner:** Each role agent (Dana, Evan, Vera, Ray, Ace, Quincy)
**Files modified:** `docs/glossary.md` (only the H2 sections in the agent's domain; do not touch other agents' sections)
**Action:** Read the entire glossary scaffold. For each H2 in your domain, either confirm Lead's draft definition is correct or amend it. Add any missing terms from your domain that appear in 2+ SOPs.

Domain assignments (Lead's initial mapping; agents may dispute via cross-review):
- **Dana:** Sidecar, Tournament winner (data side)
- **Evan:** OOS window, Block bootstrap, Tournament winner (econ side)
- **Vera:** Perceptual render, Disposition
- **Ray:** Narrative instrument reference, Episode triad
- **Ace:** Thin wrapper, Page template, Pair config module, Trigger card, `_REPO_ROOT` anchor
- **Quincy:** Smoke test, PASS-with-note

**Acceptance per agent:**
```bash
# Agent's status-board handoff includes:
# (a) list of H2 sections reviewed (by name)
# (b) list of H2 sections amended (with diff stat: git diff --stat docs/glossary.md)
# (c) list of new terms added (if any)
# Lead audit: confirm git log on docs/glossary.md shows agent's commit touching only their H2 sections
git log --author="<agent-name>" --oneline docs/glossary.md
git diff <agent-commit>~1..<agent-commit> -- docs/glossary.md  # spot-check sections touched
```

---

### NORM-004 — Per-SOP definition-to-reference refactor
**Owner:** Each role agent
**Files modified:** the agent's own SOP only (`docs/agent-sops/<role>-agent-sop.md`)
**Action:** For every term now in `docs/glossary.md`, find any inline definition in your SOP and replace with a reference: `see [docs/glossary.md § <term>](../glossary.md#<term-anchor>)`. Inline usage of the term is fine; **redefining** it locally is what gets retired.

**Two-step procedure for the agent:**
1. Pre-baseline: count inline definitions of glossary terms in your SOP today.
2. Apply changes.
3. Post-count: re-run the count. Should drop to 0 (or to 1 if your SOP IS the canonical authority for that term — in which case mark it as "canonical here, glossary points here").

**Acceptance per agent (run before and after; report both):**
```bash
# Count of inline-definition phrases in agent's own SOP
grep -cE "(Definition:|Defined as:|is defined as|We define [a-z]+ as|^- \*\*[A-Z][a-z]+\*\* —)" docs/agent-sops/<role>-agent-sop.md
# Pre-baseline count: <N>
# Post-change count: <M>
# Acceptance: M < N, AND for each term in your domain, the SOP contains a cross-reference to docs/glossary.md
grep -c "docs/glossary.md\|glossary.md#" docs/agent-sops/<role>-agent-sop.md
# Expected: >= count of glossary terms in your domain (i.e., one cross-ref per domain term)
```

---

### NORM-005 — Status vocabulary canonical SSoT
**Owner (canonical):** Ray (`docs/portal_glossary.json` `_status_vocabulary` per RES-10)
**Owner (consumers):** Dana, Evan, Vera, Ace, Quincy (drop prose enumeration; cross-reference instead)
**Action:** Any prose in non-Ray SOPs that enumerates the canonical status set (`Available / Pending / Validated / Stale / Draft / Mature / Unknown`) replaces the enumeration with a single sentence: "Status labels per `docs/portal_glossary.json._status_vocabulary` (canonical via RES-10 / DATA-VS / RES-VS)." Lists of status meanings stay in `portal_glossary.json` only.

**Acceptance:**
```bash
# Total occurrences of status enumeration patterns in non-Ray SOPs
for sop in data-agent-sop econometrics-agent-sop visualization-agent-sop appdev-agent-sop qa-agent-sop; do
  hits=$(grep -cE "Available[/, ]+Pending[/, ]+Validated|Available, Pending, Validated, Stale, Draft, Mature, Unknown" "docs/agent-sops/${sop}.md")
  echo "$sop: $hits"
done
# Expected: every line shows "0"
# Ray's SOP keeps the canonical enumeration (DATA-VS / RES-VS reference Ray's authority); audit not run on research-agent-sop.md
```

---

### NORM-006 — Severity scheme canonical SSoT
**Owner (canonical):** Ace (APP-SEV1 in `docs/agent-sops/appdev-agent-sop.md`)
**Owner (consumers):** Dana, Evan, Vera, Ray, Quincy (drop paraphrase, cross-reference instead)
**Action:** Any prose in non-Ace SOPs that paraphrases the L1/L2/L3 severity scheme (e.g., "L1 means a loud error — `st.error` — when the page can't render its primary purpose") replaces the paraphrase with a single sentence: "Severity levels (L1 / L2 / L3) per APP-SEV1 in the AppDev SOP."

**Acceptance:**
```bash
# Count of inline severity-level definitions in non-Ace SOPs
for sop in data-agent-sop econometrics-agent-sop visualization-agent-sop research-agent-sop qa-agent-sop; do
  hits=$(grep -cE "L1[ )].*Loud-Error|L2[ )].*Loud-Warning|L3[ )].*Caption-Note" "docs/agent-sops/${sop}.md")
  echo "$sop: $hits"
done
# Expected: every line shows "0"
```

---

### NORM-007 — Register META-NCD in standards.md
**Owner:** Lead
**Files modified:** `docs/standards.md`
**Action:** Add `META-NCD` row to the META table after `META-SBP`.
**Acceptance:**
```bash
grep -c "^| META-NCD " docs/standards.md
# Expected: 1
```

---

### NORM-008 — Lead closing audit
**Owner:** Lead
**Files modified:** `_pws/lead-lesandro/sop_normalize_audit_20260508.md` (new)
**Action:** Run every acceptance command above. Record actual output vs expected. Mark each NORM item PASS or FAIL. For any FAIL, dispatch the owner with a focused fix-up prompt (Phase 5–style). Wave closes when all items PASS.
**Acceptance:** the audit document exists and every NORM-001 through NORM-007 row has PASS, OR a FAIL row with a re-dispatch reference.

---

## Out of scope for this wave (deferred to backlog)

These were considered and dropped to keep wave size manageable:
- **Pseudocode externalization** — VIZ-V11 lint script, GATE-CL audit script. Real engineering work; separate wave (BL-VIZ-V11-LINT, BL-GATE-CL-AUDIT).
- **Schema field enumeration replacement** — substantial rewrite of ECON-H5 / APP-WS1 / etc. body prose. Real benefit but high blast radius. Separate wave.
- **Cross-reference list compression** — long `Cross-ref X, Y, Z, ...` lists at end of rules. Useful, low drift risk. Defer.

---

## Anti-filler instruction (per user feedback 2026-05-08)

All agents and Lead drop filler words and ceremonial openings in handoff prose and status-board entries. No "You're right", "Great", "Absolutely", "Of course", or similar. Lead the response with substance.

---

*End of plan.*
