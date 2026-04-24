# Wave 10J — Cross-Review Debate Round 1
**Agent:** Viz Vera  
**Date:** 2026-04-24  
**Wave:** 10J Phase 3

---

## Topic 1 — Contradicting Concepts, Rules, or Guidelines

### Contradiction 1.1 — Who owns `interpretation_metadata.json`? (Evan vs. Dana vs. Ray)

**The conflict:** Three SOPs claim different ownership of `interpretation_metadata.json`.

- Evan's SOP (Section: ECON-DIR1, Anti-patterns) states: "Before finalizing `interpretation_metadata.json`, compare `observed_direction` against `winner_summary.json.direction`. They MUST match." Evan is implicitly positioned as the producer.
- Ray's SOP (Rule RES-OD1, cross-reference footnote, added 2026-04-22, Wave 10F): "Vera may begin charting using Dana's `interpretation_metadata.json` (producer per DATA-D6 — note: earlier revisions of this SOP named Evan as producer; corrected 2026-04-22 Wave 10F per cross-review finding)."
- Evan's cross-pair check (Section "interpretation_metadata.json — Producer Contract"): "observed_direction uses the same string vocabulary as expected_direction. This aligns with the Analysis Brief template Section 11.4 and feeds Vera's visual encoding directly."

So the current answer is: Dana produces `interpretation_metadata.json` for fresh pairs. But Evan's SOP still describes producer-level obligations for this file without acknowledging Dana's authorship. Evan's ECON-DIR1 gate says Evan must "compare `observed_direction` against `winner_summary.json.direction`" before finalizing — but if Dana is the producer, Evan cannot "finalize" a file he does not own.

**Verdict: Ray's footnote in RES-OD1 is the correct owner attribution (Dana), but Evan's SOP has not been updated to reflect this.** Evan's ECON-DIR1 language is obsolete: the phrase "before finalizing `interpretation_metadata.json`" should read "before accepting Dana's `interpretation_metadata.json` handoff." Every Evan instruction written in producer voice for this file is implicitly wrong. Evan's SOP must be updated to recast ECON-DIR1 as a *consumer-side validation gate*, not a producer gate. The rule is correct; the voice is wrong. Until this is fixed, any new Evan instance reading ECON-DIR1 cold will believe Evan owns the file and will produce it, creating a duplicate-producer conflict with Dana.

**Which rule wins:** Dana owns the file. Evan validates it at receipt. Ray cross-checks with RES-OD1. QA triangulates at GATE-28 (APP-DIR1). This four-agent chain is correct; the Evan SOP text must align with it.

---

### Contradiction 1.2 — "Smoke test" means different things across SOPs

**The conflict:**

- Vera's SOP (Rule VIZ-V5): "Before handoff to Ace, Vera MUST run a smoke-test script that... verifies: chart JSON loads, ≥1 data trace, non-empty layout title, palette_id in registry, annotation_strategy_id present." This is a **structural integrity check on Plotly JSON files**.
- Ace's SOP (Rule APP-ST1, referenced in QA SOP QA-CL4): "AST-parse of every page plus assertion that every `load_plotly_chart` call returns a non-None figure with data." This is a **Python import and loader resolution check**.
- QA's SOP (QA-CL4): distinguishes "GATE-27 smoke tests locally" (loader check) from "GATE-28 headless browser pass" (DOM render) from "GATE-29 clean-checkout test" (deploy artifact existence). The word "smoke test" is used for all three.

The problem: when Ace says "I ran the smoke test," she could mean APP-ST1 (loader), not VIZ-V5 (chart JSON structural integrity). When Quincy says "smoke test passes," he means `smoke_loader.py` output — which does not execute Vera's VIZ-V5 checks at all. VIZ-V5 is Vera's internal pre-handoff check; it is not wired into `smoke_loader.py`. A chart that passes Ace's smoke test can still fail VIZ-V5 (missing palette_id, missing annotation_strategy_id) because the loader only checks that the Figure is non-None with data — it does not inspect sidecar fields.

**Verdict: The term "smoke test" should be formally partitioned across SOPs.** Proposed taxonomy:
- **VIZ smoke test** → Vera's VIZ-V5 pre-save structural check (JSON integrity + sidecar)
- **Loader smoke test** → Ace's APP-ST1 / `smoke_loader.py` (Python loader chain)
- **Cloud smoke test** → Quincy's GATE-28/29 headless browser + clean-checkout

Using "smoke test" generically obscures which check is being claimed. Any handoff note that says "smoke test passed" without specifying which type is unverifiable by the receiver. **The Vera SOP should be the precedent model:** it names VIZ-V5 explicitly as a distinct check. Every other SOP should adopt the same named-check pattern.

---

### Contradiction 1.3 — Direction vocabulary mismatch: `counter_cyclical` vs. `countercyclical`

**The conflict:**

- Evan's SOP (Section: "winner_summary.json schema"): "direction (required) vocabulary is `procyclical` | `countercyclical` | `mixed` (note: single-word spelling — legacy `counter_cyclical` is deprecated)."
- Ray's SOP (Rule RES-OD1 assertion script, actual code shown): the assertion compares `ws.get('direction') == im.get('observed_direction')`. Ray's SOP does not independently specify the vocabulary — it delegates to the assertion script.
- Ray's SOP (Quality Gates checklist, RES-OD1b): produces code that prints `direction_consistent={consistent}` but never validates that `observed_direction` uses the single-word form.
- Vera's SOP (Rule VIZ-SD1 sidecar schema, direction encoding section): "Use Evan's `interpretation_metadata.json` for direction and mechanism text." Direction encoding is keyed on the string values. If `interpretation_metadata.json` was produced by Dana using the legacy hyphenated form and not caught by RES-OD1, Vera's direction-annotation logic will silently fail to match the expected encoding.

**Verdict: Evan's deprecation of `counter_cyclical` is correct, but it is Evan's SOP that records it — not Ray's, not Dana's, not Vera's.** The schema is authoritative (winner_summary.schema.json), but the vocabulary restriction must be explicitly stated in every SOP that reads or writes `observed_direction` or `direction`. Ray's RES-OD1 assertion script checks equality but does not validate vocabulary — a pair where both `direction` and `observed_direction` are `counter_cyclical` (hyphenated) would pass RES-OD1 while both violating the schema. Quincy's schema validation via `validate_schema.py` is the only gate that would catch this — but only on `winner_summary.json`, not on `interpretation_metadata.json`. This is a seam gap.

---

### Contradiction 1.4 — "Handoff" means different things: Ray→Evan vs. Evan→Vera vs. Vera→Ace

**The conflict:**

- Evan's SOP (Section "Research Brief Intake"): "Read the brief and confirm receipt to Ray." The handoff is a markdown research brief. Evan's SOP defines specific intake steps.
- Vera's SOP (Section "Inputs I Need"): defines minimum viable input per chart type. The handoff is a chart request table (ECON-H4).
- Ray's SOP (Quality Gates checklist): "Handoff message template — 'Request acknowledgment from all receivers.'" This is prose acknowledgment, not a structured format.
- QA's SOP (handoff template at end of SOP): defines a structured `Handoff Evidence Table` with rows for every agent.

There is no single definition of "handoff" shared across SOPs. The Ray→Evan handoff is a markdown brief. The Evan→Vera handoff is a table (ECON-H4). The Vera→Ace handoff is a structured template. The producer→QA handoff is the Evidence Table. The team coordination SOP exists (`docs/agent-sops/team-coordination.md`) but these SOPs each define their own formats independently.

**Verdict: The coordination SOP should own the canonical handoff definition and format. Individual agent SOPs should reference it, not define their own variants.** The current state — where each SOP defines its own handoff language — means a new agent reads their SOP and learns their particular handoff convention without seeing the full pipeline sequence. Ray's SOP, for instance, does not teach Ray that Evan is waiting on a structured Research Brief with specific fields — it describes Ray's output requirements vaguely as "brief." I am arguing for a shared handoff schema governed by team-coordination.md, with per-agent sections that are references, not redefinitions.

---

## Topic 2 — Redundancies and Whether They Are Necessary

### Redundancy 2.1 — Direction triangulation checked by Evan (ECON-DIR1), Ray (RES-OD1), and Quincy (APP-DIR1 at GATE-28)

**The redundancy:** All three agents check that `winner_summary.json.direction` == `interpretation_metadata.json.observed_direction` == `narrative_frontmatter.direction_asserted`.

- Evan checks ECON-DIR1 before handoff to Vera.
- Ray checks RES-OD1 (+ RES-OD1a/b/c) before narrative handoff.
- Quincy checks APP-DIR1 (direction triangulation) as part of the cross-agent seam audit.

**Verdict: Keep all three, but assign distinct ownership.**

This is a deliberate triple-check and I argue it is correct, with one important clarification on what each agent is checking:

- **ECON-DIR1 (Evan):** verifies that `interpretation_metadata.observed_direction` matches `winner_summary.direction` *at the time Evan finalizes econometric results*. Evan is comparing two files he controls (winner_summary) and receives (interpretation_metadata from Dana). This is the production-side gate.
- **RES-OD1 (Ray):** verifies the same invariant *at the time Ray writes narrative*, because Ray may be performing a batch backfill where both files are stale and the invariant may have drifted between Evan's check and Ray's writing. This is the editorial-side gate.
- **APP-DIR1 (Quincy):** verifies the invariant *at cloud render time*, checking the live portal DOM for the L1 error banner that fires when the fields disagree. This is the acceptance gate.

These three checks are checking the same invariant at three different time points in the pipeline. Each is necessary because drift can occur in the intervals between them (e.g., a schema migration backfill that Evan ran but Ray has not yet re-validated). The triple-check is not redundant waste — it is the architecture appropriate for a distributed async pipeline.

**What IS redundant:** both Ray's SOP (RES-OD1) and Evan's SOP (ECON-DIR1) describe the python assertion script independently. They should share a single canonical script path (`scripts/check_direction_invariant.py`) and both SOPs should reference it. Two separately described scripts that check the same invariant will diverge over time.

---

### Redundancy 2.2 — NBER shading checked by Vera (VIZ-V2 / VIZ-NBER1) and Quincy (GATE-VIZ-NBER1)

**The redundancy:**

- Vera's SOP (VIZ-NBER1): "The QA agent verifies this at smoke-test time by checking that `layout.shapes` contains at least one shape with `fillcolor` matching the NBER shading rgba pattern."
- Quincy's SOP does not explicitly list GATE-VIZ-NBER1 — it is referenced in Vera's SOP but does not appear as a named gate in Quincy's SOP QA checklist.

**Verdict: Remove the redundancy — Quincy's SOP is the gate owner; Vera's SOP is the production rule.** Vera's SOP correctly states the production requirement (NBER shading mandatory on charts in list). Vera should not also define what Quincy must check — that is Quincy's domain. Vera's SOP should say "NBER shading compliance is verified by Quincy per GATE-VIZ-NBER1." Quincy's SOP should actually list GATE-VIZ-NBER1 in the QA checklist. Currently, Vera is writing Quincy's verification procedure in her own SOP — that is a role boundary violation, and if the two descriptions ever diverge, it creates a contradiction.

---

### Redundancy 2.3 — Stationarity test requirement stated in both Evan's SOP and Dana's (implied) workflow

**The redundancy:**

- Evan's SOP (Section 4, Exploratory Analysis): "Mandatory artifact: Save stationarity results to `results/{pair_id}/stationarity_tests_{YYYYMMDD}.csv`." Evan explicitly runs ADF/KPSS. He also says: "If Dana has already provided stationarity tests, review and confirm rather than re-running from scratch."
- The research SOP does not mention stationarity. The Data agent SOP (not fully read here, but referenced by Evan) presumably covers this.

**Verdict: Merge — one agent owns, one reviews.** The current "Evan reviews Dana's results OR runs his own" phrasing is ambiguous. If Dana is the data specialist, stationarity tests belong to Dana's pipeline output — they are data quality artifacts, not econometric artifacts. Evan should validate, not reproduce. The current Evan language allows him to skip checking Dana's work if she has provided it, or to run his own if she has not — but which is authoritative? If both run stationarity tests, which result does the portal Methodology page display? The artifact name is `stationarity_tests_{YYYYMMDD}.csv` — one file path, two potential producers. This is a silent collision risk.

---

### Redundancy 2.4 — Perceptual validation defined in Vera's SOP and referenced in Quincy's GATE-27

**The redundancy:**

- Vera's SOP (VIZ-V2): "After saving the chart JSON, render it to a PNG via `plotly.io.from_json` + `fig.write_image(...)` (kaleido) OR via browser snapshot, and visually confirm the shading bands are perceptible at standard zoom. Save the test snapshot as `output/charts/{pair_id}/plotly/_perceptual_check_{chart_name}.png`."
- Quincy's SOP (GATE-27): "Vera's VIZ-V5 smoke test log: every canonical chart artifact loads via Plotly, has ≥1 data trace, and non-empty title." GATE-27 does not explicitly check the perceptual PNG. It checks the smoke-test log, which covers structural integrity (VIZ-V5) but not the perceptual rendering step (VIZ-V2 item 4).

**Verdict: The perceptual check is currently NOT verified by QA — it is only self-attested by Vera.** Vera's VIZ-V2 perceptual check should be a QA gate, not just a producer step. Quincy's GATE-27 should be extended to verify that `_perceptual_check_{chart_name}.png` exists for every mandatory-NBER chart type. The PNG existence is machine-verifiable (file exists check). The perceptual quality of the PNG is a human judgment — and that judgment should be QA's, not Vera's, because Vera has an obvious conflict of interest (she produced the chart). I am arguing to move this verification from producer self-attestation to QA independent verification.

---

### Redundancy 2.5 — The `regression_note.md` requirement appears in both Vera's SOP and Evan's SOP

**The redundancy:**

- Vera's SOP (Section "Regression Note Requirement"): "On rerun of an existing pair... run a diff against the prior charts directory... Vera must write a regression note."
- Evan's SOP (Rule C3): "When rerunning a pair, list prior-version method files and tournament winners BEFORE writing the new run." Evan's regression note covers method outputs.

**Verdict: Keep both — they are checking different artifacts.** Vera's regression note covers chart-level changes (filename set, signal selection, palette, color). Evan's covers method-level changes (tournament winner, model outputs). These are not duplicates — they are complementary regression-check artifacts at different levels of the pipeline. The naming collision ("regression note" for both) is confusing but the content is distinct. Proposal: rename Evan's to "method-rerun log" and Vera's to "chart-rerun log" to prevent cross-agent confusion when QA audits both.

---

## Topic 3 — Strengthening Lesson-Application Individually and Collectively

### 3.1 — Individual: The Pre-Handoff Gate Must Be a Checklist You Read, Not Remember

**Current state:** Every SOP has a Quality Gates section at the end. Vera's Wave 10J self-assessment confirms that Rule V2 (NBER shading) and VIZ-O1 (disposition mandate) were violated because I did not check my own gates before handoff. Evan's self-assessment confirms the same: ECON-UD and stationarity CSV were missed because his quality gate was written as a "per-handoff check" but was not mechanically re-read at handoff time. Quincy's self-assessment explicitly names the failure: "GATE-29 omission was not caused by an unclear SOP — GATE-29 was documented. It was caused by not re-reading QA-CL4 before starting."

**Proposal: Mandatory SOD Checklist Print.** At every session start, before any production work begins, each agent must `cat` or display their own SOP's Quality Gates section and explicitly mark which items apply to the current wave. This is not "consult your experience.md" — that is narrative learning. This is a mechanical gate: you cannot begin handoff work until you have physically read the checklist that wave.

**Why this is better than experience.md:** experience.md is a growing narrative document. A new agent inheriting the role reads the experience.md for lessons but must then mentally reconstruct which lessons apply to the current task. The Quality Gates checklist is the applied form — it lists specific checks in execution order. The failure mode we have seen repeatedly (Evan, Quincy, Vera) is that agents learn the rule, update experience.md, and then violate the rule on the next task because the checklist was never re-read. experience.md records the lesson; the pre-task checklist-read is the enforcement mechanism. Without the enforcement mechanism, experience.md is a historical record, not a process control.

**Implementation:** Add to each SOP's SOD ritual (already present as a section): "Print and read the Quality Gates section before beginning any handoff. Annotate which items are in scope for this wave. Unannotated Quality Gates sections are a compliance gap."

---

### 3.2 — Individual (Vera-specific): The Input Quality Log Must Be Filled Before Chart Production Starts

**Current state:** Vera's SOP requires maintaining `docs/agent-sops/viz-input-quality-log.md` after each task. My self-assessment confirms it has not been consistently updated. The consequence: I start charting from Evan's handoff without auditing whether the input meets the minimum viable input spec per chart type. This is what produces missing-title charts, wrong direction annotations, and ad-hoc decisions on CP chart types.

**Proposal: Input Quality Log as a blocking pre-condition, not an end-of-task reflection.** The log must be partially filled *before* chart production begins (at minimum: which chart types are requested, which minimum viable input fields are present, which are missing). Missing inputs are flagged to Evan before I begin, not discovered mid-production. This eliminates the class of bug where Vera is mid-chart and discovers that ECON-H4 did not include the expected-direction field, forcing either an assumption or a mid-task interruption.

**Why better than current:** The current log is a post-hoc reflection document. A pre-production partial fill turns it into an intake validation step. Quincy already does this for QA: he reads the handoff note before verifying, not after. Vera should do the same.

---

### 3.3 — Collective: New Rules Require a Paired Retro-Apply Task — Always

**Current state:** Evan's self-assessment names this as his systematic weakness: "Rule authoring without portfolio-wide retro-apply is a latent time bomb." When Evan writes ECON-DIR1, it applies to the current pair and future pairs, but not to the 9 existing pairs unless an explicit retro-apply task is dispatched. The same pattern appears for Vera (VIZ-NBER1 and VIZ-ZOOM1 added in Wave 10J — 5 active pairs have no NBER shading, no zoom charts, no CP charts), Ray (RES-OD1 added reactively, not applied to all pairs at time of addition), and Ace (GATE-CL1-5 added in 10I.C, not applied to any pair in the same wave).

**Proposal: Mandatory Retro-Apply Dispatch Protocol.** When any agent adds a new rule that applies to existing artifacts (not just future pairs), the Lead immediately creates a retro-apply task and assigns it to the relevant agent before the current wave closes. The retro-apply task has a specific scope: list every existing pair that the rule applies to, and the artifact path that must be verified or updated for each. The task is tracked in the status board. The wave cannot close until the retro-apply task is either completed or explicitly waived by Lead with a documented reason.

**Why better than experience.md:** experience.md records the observation that retro-apply was missed. The proposed protocol makes retro-apply structurally mandatory — it cannot be missed because the task is created at the same time the rule is written. The current flow is: (1) rule added to SOP, (2) team notices during next wave that old pairs are non-compliant, (3) backfill task created reactively. The proposed flow is: (1) rule added to SOP, (2) retro-apply task immediately dispatched, (3) backfill complete before any new pair work resumes. This eliminates the observation-to-fix lag.

---

### 3.4 — Collective: Shared Gate Registry Owned by QA, Updated by All

**Current state:** Gates exist as named items within individual agent SOPs (GATE-VIZ-NBER1 defined in Vera's SOP, GATE-27/28/29/30/31/32 defined in Quincy's SOP, GATE-CL1-5 defined in Ace's SOP, GATE-NR defined in Quincy's SOP but triggered by Ace's behavior). There is no single document that lists all active gates, their owners, their scope, and their pass/fail criteria. Quincy must read five SOPs to construct the complete gate list for a given wave.

**Proposal: A shared gate registry at `docs/schemas/gate_registry.json` owned by QA, updated by all agents when they introduce new gates.** Schema: `{gate_id, owner_sop, checking_agent, scope (artifact type + pair scope), pass_criterion, first_active_wave, blocking_or_warn}`. Every new gate introduced in any SOP is simultaneously registered in this file (PR required, QA approves). This makes QA's verification job executable without reading five SOPs: load the registry, filter by wave scope, run each gate in order.

**Why better than current:** Gates scattered across five SOPs are a coordination failure waiting to happen. GATE-VIZ-NBER1 is described in Vera's SOP but executed by Quincy — Quincy must know to look in Vera's SOP for the verification procedure. A new QA agent would not find it without reading every producer SOP. The registry centralizes gate discovery without removing the detailed specification from the individual agent's SOP (individual SOPs retain the how-to; the registry provides the what and who).

---

### 3.5 — Collective: Team Retrospective After Every Five Pairs, Not Just Experience.md Updates

**Current state:** Lessons are accumulated in individual `experience.md` files per agent. Cross-agent lessons (e.g., "Evan's retro-apply gap has a structural fix that affects every agent") require the lead to read multiple experience files and synthesize. There is no team-level retrospective ritual.

**Proposal: After every five pairs or every major wave, a structured cross-agent retrospective is dispatched by Lead.** Format: each agent reads every other agent's experience.md additions from the last five pairs and produces one cross-agent insight — "what Evan's lesson implies for how Vera should behave" or "what Quincy's GATE-29 failure implies for how Ray should hand off." The output is a `_pws/_team/retro_{wave}.md` that Lead reviews and uses to update cross-cutting SOP sections (team-coordination.md, or new rules in multiple SOPs simultaneously).

**Why better than experience.md:** experience.md is agent-local. A lesson learned by Evan about retro-apply does not automatically reach Vera — unless Vera reads Evan's experience.md, which is not required by any SOP. The team retrospective creates a forced cross-pollination of lessons at regular intervals. The cross-review debates (like this one, Wave 10J Phase 3) are a high-quality version of this, but they occur irregularly and produce debate submissions rather than actionable SOP changes. A lightweight regular retrospective (30 minutes of structured reading + one cross-agent insight per agent) would catch lesson-propagation gaps earlier and at lower coordination cost.

---

## Summary of Positions

| # | Issue | Position |
|---|-------|----------|
| 1.1 | `interpretation_metadata.json` ownership | Dana produces; Evan's SOP must recast ECON-DIR1 as consumer validation, not producer gate |
| 1.2 | "Smoke test" term ambiguity | Formalize three distinct named checks: VIZ smoke, Loader smoke, Cloud smoke |
| 1.3 | Direction vocabulary mismatch | Vocabulary restriction must appear in every SOP that writes `observed_direction`, not just Evan's |
| 1.4 | "Handoff" format inconsistency | team-coordination.md owns the definition; individual SOPs reference, don't redefine |
| 2.1 | Direction triple-check (Evan + Ray + Quincy) | Keep all three; merge the assertion script into one shared script path |
| 2.2 | NBER shading (Vera defines + Quincy verifies) | Quincy's SOP must explicitly list GATE-VIZ-NBER1; Vera's SOP references but does not define the QA check |
| 2.3 | Stationarity test ownership (Dana vs. Evan) | Merge: Dana produces, Evan validates; one artifact file, one producer |
| 2.4 | Perceptual PNG self-attested by Vera | Move to QA: Quincy verifies PNG existence as GATE-27 extension |
| 2.5 | Regression note (Vera + Evan) | Keep both; rename to distinguish: "chart-rerun log" (Vera) vs. "method-rerun log" (Evan) |
| 3.1 | Pre-handoff gate enforcement | Mandatory SOD checklist-read, annotated per wave, not memory-dependent |
| 3.2 | Input Quality Log (Vera) | Pre-production partial fill as blocking intake gate, not post-hoc reflection |
| 3.3 | New rules without retro-apply | Mandatory paired retro-apply task dispatched at the same time any new rule is written |
| 3.4 | Shared gate registry | `docs/schemas/gate_registry.json` owned by QA, updated at rule-introduction time |
| 3.5 | Experience.md silos | Team retrospective after every 5 pairs; forced cross-agent lesson reading |
