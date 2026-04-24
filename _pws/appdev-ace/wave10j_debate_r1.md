# Wave 10J — Cross-Review Debate Round 1
**Agent:** App Dev Ace (appdev-ace)  
**Date:** 2026-04-24  
**Phase:** 10J Phase 3 — Cross-Review Debate Round 1

---

## Topic 1 — Contradicting Concepts, Rules, or Guidelines

### Contradiction 1: "Smoke test" means three different things across three SOPs

**Where it appears:**
- **Ace SOP (APP-ST1):** Smoke test = AST-parse of every Streamlit page + assertion that every `load_plotly_chart` call returns a non-None figure with data. Portal-layer, syntax + runtime artifact check.
- **Evan SOP (Quality Gates, § "Producer validation step"):** Smoke test = `smoke_loader.py` run against `winner_summary.json` to validate schema compliance. Schema-layer, structural integrity check.
- **Quincy SOP (QA-CL4, GATE-27/28/29):** Smoke test = `cloud_verify.py` headless browser run against Cloud-deployed portal. Deployment-layer, end-to-end render check. `scripts/cloud_verify.py` captures DOM text files; a human then reads those files.

**The contradiction:** Evan's Wave 10J self-assessment (Question 1, para 1) explicitly notes he "ran smoke_loader.py against the pair I was actively building — not against the full portfolio." Ace's Wave 10J self-assessment (Part 1, Item 1) admits her own smoke test "loads chart files, not schema content." Quincy's self-assessment (Section 1, Mistake 3) admits he treated "script PASS = QA PASS" and the script's ERR_PATS never catch APP-SEV1 banner strings. **Three agents all ran their respective "smoke tests" on Wave 10I.A and all three declared a passing state. None of the tests caught the red banner.**

This is not a naming coincidence — it is a definitional gap that allows each agent to say "I ran the smoke test" without the words being interchangeable or composing into a complete check. The system has three partial tests, each called "smoke," none of which alone constitutes production confidence.

**Position: Create a canonical term taxonomy. The three test types must have different names.**

- Evan's check = **Schema lint** (renamed from "smoke test" in Evan SOP Quality Gates). Rule: ECON-DS2 + `validate_schema.py`, run per-pair at handoff AND portfolio-wide after any schema version bump.
- Ace's check = **Portal lint** (renamed from APP-ST1 "smoke test"). Rule: AST-parse + artifact existence check, run at Ace handoff.
- Quincy's check = **Smoke test** (sole owner of this term). Rule: `cloud_verify.py` + mandatory DOM-file read before verdict. GATE-29 parquet preflight included.

**Which rule wins:** Quincy owns "smoke test" because the smoke test as understood in QA literature means end-to-end deployment verification — not lint. Evan and Ace must rename their checks in their own SOPs. This is not a demotion; it is clarification. No one loses a gate. The taxonomy becomes legible.

---

### Contradiction 2: Direction consistency — who owns the final check?

**Where it appears:**
- **Evan SOP (ECON-DIR1):** "Before finalizing `interpretation_metadata.json`, compare `observed_direction` against `winner_summary.json.direction`. They MUST match." Owner: Evan.
- **Ray SOP (RES-OD1):** "Run the mechanical assertion after ANY write to `interpretation_metadata.json`." Owner: Ray. Includes RES-OD1a (logged output), RES-OD1b (`direction_consistent` recalculation), RES-OD1c (batch-run log).
- **Quincy SOP (§ "Cross-agent seam audit", APP-DIR1):** Direction triangulation is a QA gate — Quincy checks that direction is consistent across `interpretation_metadata.json`, `winner_summary.json`, and narrative text.

**The contradiction:** Both Evan and Ray claim ownership of the direction-consistency write-time check. Evan authors `interpretation_metadata.json` from tournament results. Ray ports narrative text that references direction and may also write to `interpretation_metadata.json` during config ports. Both SOPs have a gate for the SAME check on the SAME artifact. When both run it, the result is false confidence ("two agents checked it so it must be fine"). When only one of them runs it (the typical case under time pressure), the check passes or fails silently because neither tracks what the other actually did.

Wave 10I.A confirmed this: Evan's ECON-DIR1 was not retro-applied to legacy pairs; Ray's RES-OD1 was not applied during the narrative port batch; Quincy's APP-DIR1 caught it on the third pass. Three agents, one check, one actual enforcement: Quincy.

**Position: Assign single ownership at write time. Quincy remains the independent verifier — not the primary enforcer.**

Evan owns ECON-DIR1 (write-time, in pipeline, non-negotiable). Ray's RES-OD1 is a **read-time confirmation**, not a duplicate gate — Ray reads what Evan wrote and confirms it matches the narrative. If it does not match, Ray blocks and escalates; Ray does not fix the data. Quincy's APP-DIR1 remains unchanged as the independent out-of-band check. The sequence is: Evan writes and checks → Ray reads and confirms → Quincy audits. No overlap; clear escalation path.

**Which rule wins:** ECON-DIR1 is the primary gate (it is at write time, blocking, script-enforced). RES-OD1 is retained but reclassified as read-time confirmation. APP-DIR1 remains unchanged.

---

### Contradiction 3: "Handoff" — is it a file or a message?

**Where it appears:**
- **Evan SOP (§ "Handoff message template"):** Handoff = structured message in Markdown format, written to `regression_note_<date>.md`, containing model summary, schema compliance status, questions for downstream agents.
- **Vera SOP (§ "Inputs I Need"):** Handoff = a set of files (DataFrames, Plotly JSON, sidecar `_meta.json`) delivered to the chart output path. No message format specified.
- **Ray SOP (§ "Handoff to Evan"):** Handoff = a structured Research Brief (Markdown document), separate from any file artifacts.
- **Ace SOP (§ "Receive Portal Brief"):** Handoff = a "portal brief" confirmed with Lesandro; inputs from Ray (narrative sections), Vera (chart specs + Plotly objects), Evan (model results), Dana (data pipelines). No prescribed format for how those inputs arrive — Ace is expected to know where to look.

**The contradiction:** Evan writes a message. Vera delivers files. Ray writes a document. Ace waits for all three without a protocol for knowing when any of them are ready. The team-coordination SOP (`docs/agent-sops/team-coordination.md`) was referenced in the project CLAUDE.md but none of the individual SOPs bind to it consistently. Ace's self-assessment (Part 1, Item 2: "Template changes require a bypass audit") and Ray's self-assessment (Part 2, Item 3: "handed off to Ace without requesting explicit acknowledgment from Dana") both show that informal handoffs produce silent gaps.

**Position: The team-coordination SOP must define a canonical "handoff artifact" struct. All four agent SOPs must bind to it.**

A handoff from any producer agent to any consumer agent must contain: (1) pair_id, (2) artifact paths, (3) schema compliance verdict (with evidence), (4) known gaps or open questions. This is already implied by Evan's handoff template but must be made the team-wide standard, not just Evan's personal practice. Ace should never need to look for artifacts — they should arrive via the canonical handoff note.

**Which rule wins:** Evan's handoff message template is the closest to complete and should become the team standard. Other agents' SOPs should reference it rather than maintaining their own implicit formats.

---

### Contradiction 4: Portfolio-wide validation — who triggers it after schema evolution?

**Where it appears:**
- **Evan SOP (ECON-DS2):** "Run `validate_schema.py` before saving." Per-pair, per-handoff only.
- **Quincy SOP (§ QA-CL1, schema validation pillar):** "Every claim in a producer's `regression_note_<date>.md` section must trace to evidence." Quincy validates schema compliance as part of the verification pass.

**The contradiction (implicit):** Evan's ECON-DS2 is a per-pair forward-looking gate. Quincy's schema pillar is reactive — it checks what's already committed. Neither SOP explicitly assigns responsibility for re-running schema validation across ALL committed pairs when the schema version bumps. Evan's self-assessment (Question 1, para 3) admits this directly: "I ran them only against the pair I was actively building — not against the full portfolio of committed pairs." Quincy caught the portfolio drift in Wave 10I.A.

**Position: Schema version bumps must trigger a mandatory portfolio-wide re-validation, explicitly assigned to Evan as a blocking prerequisite before any new pair work.**

This is not currently a rule in any SOP. It needs to be. Quincy should not be the backstop for Evan's portfolio hygiene. Adding this as ECON-DS3 in Evan's SOP: "When `winner_summary.schema.json` version is incremented, before starting any new pair, re-run `smoke_loader.py` against all committed pairs and fix all FAILs. Produce a batch log `results/schema_regression_YYYYMMDD.txt` as evidence."

**Which rule wins:** Evan is responsible for schema production; Evan must own portfolio re-validation on version bumps. Quincy's role is independent spot-check, not portfolio maintenance.

---

## Topic 2 — Redundancies and Whether They Are Necessary

### Redundancy 1: NBER shading rules — Vera and Ace both check it

**Where it appears:**
- **Vera SOP (Rule V2):** "Long-horizon time-series charts (>5 years) MUST include NBER shading. Apply `add_nber_shading(fig, pair_id)` as a standard step."
- **Ace SOP (GATE-CL1):** DOM audit includes checking that NBER shading appears on rendered pages. Also enforced through Plotly JSON artifacts loaded by `load_plotly_chart()`.

**Assessment: Keep — deliberate double-check, but clarify ownership.**

Vera produces the chart with shading baked in. Ace verifies the chart renders correctly in the portal. These are different checks at different layers. Vera's V2 is a production rule (does the Plotly JSON contain shading?). Ace's GATE-CL1 is a render rule (does the DOM show the chart without a fallback error?). Both are needed. However: Vera's self-assessment (Question 1, para 1) admits 5 hero charts lack NBER shading, and those charts presumably passed Ace's GATE-CL1 because the chart *rendered* — it just rendered without shading. This means Ace's GATE-CL1 does not actually catch Vera's V2 violation. They are not duplicates; they are different gaps, neither catching the other's failure mode.

**Recommendation:** Keep both. Explicitly note in each SOP that the other agent's check does not substitute for yours. Ace's GATE-CL1 should be extended to verify shading presence in the Plotly JSON data (check for `vrect` or `rect` shapes in the figure JSON), not just render-success.

---

### Redundancy 2: Direction triangulation — Evan, Ray, and Quincy all check direction

Covered in Contradiction 2 above. The redundancy here is **necessary but currently unstructured**, producing false confidence. The fix is to make the chain explicit (Evan writes → Ray confirms → Quincy audits) with clear escalation, not to remove any of the three checks. All three are kept; ownership is clarified.

---

### Redundancy 3: Experience.md as both a learning record and an SOP update trigger

**Where it appears:**
- All five SOPs have a "Task Completion Hooks" or "Reflection & Memory" section requiring updates to `experience.md` at EOD.
- Evan's SOP (§ "Quality Gates" and various ECON rules): Rules are amended reactively when failures surface, and the SOP becomes the authoritative rule; experience.md records the lesson that generated the rule.
- Ray's SOP (§ "Task Completion Hooks"): Both `memories.md` and `experience.md` are updated at EOD.
- Quincy's SOP (§ "Reflection & Memory"): experience.md updated with new patterns (Pattern 25, 26, 27, 28).

**Assessment: This is a structural redundancy that creates two separate truth sources for the same knowledge.**

When Evan learns a lesson, it appears in: (1) experience.md as a narrative entry, AND (2) the SOP as a rule. When they drift (experience.md has the lesson but the SOP doesn't yet have the rule, or vice versa), neither is authoritative. Ace's self-assessment (Part 3) is the explicit case: "GATE-CL gates are aspirational unless backed by a script or a manual verification run" was NOT in experience.md before this wave. Gates existed in the SOP; the meta-lesson about enforcement existed nowhere.

**Recommendation:** Collapse the two into a single canonical path. Every lesson learned must produce a SOP rule before it produces an experience.md entry. The SOP is the code; experience.md is the commit message. You don't merge a commit message without a code change. If an experience entry cannot be tied to a specific SOP rule change, it is an opinion, not a lesson.

This is an argument for removing pure-narrative experience.md entries and replacing them with forward-pointers: "Lesson: [n words]. → Rule added: [RULE-ID] in [agent]-agent-sop.md, §[section]." If the rule cannot be written, the lesson is not ready to be recorded.

---

### Redundancy 4: Handoff templates duplicated across agent SOPs

**Where it appears:**
- Evan SOP (§ "Handoff message template"): Full template with structured fields.
- Ray SOP (§ "Handoff to Evan"): Research Brief template with its own structured fields.
- Team-coordination SOP (referenced in CLAUDE.md but not consistently cross-referenced from individual SOPs).

**Assessment: Merge into team-coordination SOP. Agent SOPs reference it by name.**

Having two nearly-equivalent handoff formats maintained independently in two SOPs guarantees drift. Ray's self-assessment (Part 2, Item 3) confirms: Ray used the "none" placeholder in the "Questions for Ace" field when there was a live assumption pending Dana confirmation. The template was available; the agent complied with its letter ("I filled the field") while violating its spirit. A shared canonical template, maintained in team-coordination.md and referenced by all agent SOPs, makes the format authoritative and auditable by Quincy. Individual agents stop maintaining their own variations.

---

## Topic 3 — Strengthening Lesson Application Individually and Collectively

### Individual Proposal: Replace experience.md with a Runbook Pattern

**Current state:** Five agents each maintain an `experience.md` with narrative entries. Quincy's self-assessment (Section 3) identified a gap: "the meta-lesson about SOP compliance — re-reading my own SOP at SOD — is not recorded in experience.md." Ace's self-assessment (Part 2) identified the same gap: "GATE-CL gates were written but not systematically applied." In both cases the lesson is soft (narrative) and the failure is hard (specific missing action in a specific wave).

**Why experience.md fails as a lesson mechanism:** A narrative entry does not produce a behavior change. It documents that a failure happened, but it does not create a forcing function in the next wave. Quincy knew GATE-29 existed (it was in the SOP). Ace knew GATE-CL gates existed (she wrote them). Experience.md was accurate; behavior did not change. The problem is that reading experience.md is not mandatory, not time-boxed, and not tied to a specific action.

**Proposed change — Individual SOP Runbook at SOD (mandatory, time-boxed):**

Each agent SOP gains a **"SOD Execution Checklist"** section — a flat numbered list of mandatory steps, ordered, with a 3-minute time budget. Not a reading prompt. An execution checklist. Example for Ace:

```
SOD Checklist (run before first commit):
1. [ ] Read GATE-CL1 through GATE-CL6 aloud. If any gate has no verification script, flag it.
2. [ ] Run `scripts/gate_cl_audit.py` if it exists; if not, file a 1-line TODO to write it.
3. [ ] Run `grep -L "render_methodology_page" app/pages/*.py` — confirm bypass count.
4. [ ] Read today's pair's `winner_summary.json` — confirm `threshold_value` is not null.
```

The checklist is wave-specific. At the start of each wave, the Lead adds the pair-specific items (pair_id, artifacts expected from upstream). Completing the checklist is a prerequisite to the first handoff note. Quincy verifies the checklist was run by checking for it in the handoff note, not by trusting the agent's word.

**Why this works better than experience.md:** A checklist creates a forcing function. "Did you run item 3?" has a yes/no answer. "Did you internalize the lesson from Wave 10I.A?" does not. GATE-29 would not have been skipped if the Quincy SOD checklist required running `git ls-files results/{pair_id}/signals_*.parquet` as item 2.

---

### Collective Proposal: Rule Propagation Protocol (RPP) — enforce retro-apply as a team norm

**Current state (the common failure pattern across all five self-assessments):** Every agent authored new rules in response to failures but did not retro-apply them to existing artifacts. Evan (ECON-DIR1, stationarity CSV): "I write the rule when a failure surfaces, but I don't always backfill older artifacts." Ray (RES-OD1): "I applied the rule to the current pair and future pairs, but I don't retroactively audit prior pairs." Ace (GATE-CL1-5): "Gates that exist only in text are not gates — they are aspirations." Quincy (GATE-29): "The Wave 10E parquet-preflight addition is documented; I simply did not do it."

This is the team's most consistent failure mode. The pattern is: **rule written → current pair compliant → prior pairs never audited → Quincy catches it N waves later.**

**Proposed change — Rule Propagation Protocol (RPP), owned by Lead:**

When any agent adds a new rule to their SOP, they must simultaneously produce a **Rule Propagation Task (RPT)** filed to `_pws/_team/status-board.md`. The RPT has a fixed format:

```
RPT-[rule-id]: [Rule name]
Scope: [which pair artifacts does this apply to?]
Backfill action: [exact command or manual step to verify compliance for existing pairs]
Assigned to: [agent who wrote the rule]
Deadline: [before next handoff of any kind]
QA gate: Quincy verifies backfill log before sign-off
```

Lesandro's role in this protocol: at SOD, review the open RPT list. No new pair work begins until all open RPTs with past-due deadlines are cleared. Quincy adds RPT verification to the standard QA checklist (QA-CL5 or new QA-CL-RPT gate).

**Why this works better than the current experience.md approach:** The team-coordination SOP currently defines handoffs, naming conventions, and escalation. It does not define what happens when a new rule is added. RPP makes rule addition a team-visible event, not a private SOP edit. The Lead can see at a glance which rules are pending backfill. Quincy can track compliance without re-reading all five SOPs before every verify pass.

**Concrete example:** When Evan added ECON-DIR1, an RPT would have been filed: "Backfill action: run `validate_direction.py` against all committed pairs' `interpretation_metadata.json`. Produce `results/dir_backfill_YYYYMMDD.txt`." That task, visible to Lesandro and Quincy, would have been the forcing function that Evan's private experience.md entry was not.

---

### Collective Proposal 2: Aspirational Gate Prohibition

Any gate added to a SOP checklist without a corresponding verification mechanism (script, manual step with expected output, or Quincy-auditable log) is prohibited from being committed to the SOP. The proposed language for all five SOPs:

> **Gate authoring rule (mandatory):** A quality gate may not be added to any SOP checklist unless one of the following is true: (a) a script exists that runs the check and exits non-zero on failure, OR (b) a manual checklist step is defined with a specific expected output that Quincy can verify from the handoff note. A gate description without a verification mechanism is a comment, not a gate. Add it to the "Known Gaps" section of experience.md, not the SOP checklist.

Ace's own GATE-CL1-5 are the clearest violation of this principle. All five were listed in the SOP checklist. None had a script. None had a manual step with verifiable output. The self-assessment correctly classifies them as "aspirational." The gate authoring rule would have prevented this: GATE-CL1-5 would have gone to the Known Gaps section, and writing `scripts/gate_cl_audit.py` would have been the explicit prerequisite to promoting them to the checklist.

This is a hard stance but defensible: an unchecked box that cannot be checked is worse than no box, because it creates an illusion of rigor. The Wave 10I.A false-PASS incident is the direct consequence of that illusion — multiple agents believed their respective "gates" were sufficient, but none of the gates had enforcement mechanisms strong enough to catch the failure.

---

## Summary of Positions

| # | Topic | Position |
|---|-------|----------|
| C1 | "Smoke test" naming collision | Quincy owns "smoke test." Evan = "schema lint." Ace = "portal lint." Rename in respective SOPs. |
| C2 | Direction ownership (ECON-DIR1 vs RES-OD1) | Evan writes and checks (primary). Ray confirms (secondary). Quincy audits (independent). No overlap; clear sequence. |
| C3 | Handoff format diversity | Evan's handoff template becomes team standard. All SOPs reference team-coordination.md. |
| C4 | Portfolio re-validation on schema bump | Add ECON-DS3: Evan runs portfolio schema regression before any new pair when schema version bumps. |
| R1 | NBER shading — Vera + Ace check | Keep both; extend Ace's GATE-CL1 to check Plotly JSON for shading data, not just render-success. |
| R2 | Direction — Evan + Ray + Quincy | Necessary redundancy; restructure as write-time → read-time → audit chain. |
| R3 | experience.md duplicating SOP rules | Collapse: every experience entry must link to a specific SOP rule change. No free-floating narrative. |
| R4 | Handoff templates in multiple SOPs | Merge into team-coordination.md. Agent SOPs reference it. |
| I1 | Individual lesson application | Replace narrative experience.md re-reads with mandatory SOD Execution Checklists, wave-specific, Quincy-verified. |
| T1 | Collective lesson application | Rule Propagation Protocol (RPP): every new SOP rule triggers a team-visible backfill task. Lead owns; Quincy verifies. |
| T2 | Aspirational gates | Prohibition: no gate enters SOP checklist without a verification mechanism. Gates without scripts go to Known Gaps. |
