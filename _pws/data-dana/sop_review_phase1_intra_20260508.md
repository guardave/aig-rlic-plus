# Data Agent SOP — Phase 1 Intra-SOP Review
**Author:** Data Dana  
**Date:** 2026-05-08  
**SOP reviewed:** `docs/agent-sops/data-agent-sop.md`  
**Branch:** 260430  
**Scope:** Internal consistency, completeness, cross-references — NO edits to SOP in this phase.

---

## Findings

### F-01 — DATA-D12: Linter-script reference is aspirational, not real (FAIL)

**Section:** §6 Rule DATA-D12 — Column-Suffix Linter  
**Problem:** The rule states "Dana runs a pre-save linter" (procedure steps 1–4) and references an exemption list and vocabulary versioned "alongside DATA-D2 and this rule's schema sidecar." However, `scripts/lint_column_suffixes.py` does not exist on disk as of 2026-05-08. The quality-gate checkbox (§Quality Gates, DATA-D12 line) says "pre-save linter pass recorded" — but there is no script to produce that pass record. This is a persistent dead-letter rule documented in my own `outstanding-work.md` (BL-D12-LINTER, P1) since Wave 5B-2 (2026-04-19) and confirmed in the Wave 10F cross-review and Wave 10J self-reflection. The rule states a FAIL severity without specifying how compliance is verified when the enforcement tool is absent.  
**Severity proposal:** FAIL  
**Suggested fix:** Either (a) add a fallback procedure ("If `scripts/lint_column_suffixes.py` does not exist, Dana performs a manual column-name audit and logs results in the handoff note; the script is a P1 backlog item BL-D12-LINTER") so the gate is not silently skipped, or (b) note explicitly that manual execution of the lint logic in-line is the current procedure. Phase 4 should coincide with the actual script delivery.

---

### F-02 — DATA-D13: Manifest stale-coverage rule has no non-reference-pair escalation path (WARN)

**Section:** §6 Rule DATA-D13 — Manifest + Display-Name Registry Bootstrap, point 5  
**Problem:** Point 5 states "The manifest is complete for the current implemented pair universe, not just the pair Dana happened to touch." This is a good rule, but there is no defined action when a non-reference pair is absent from the manifest. For reference pairs, acceptance is blocked (DATA-D11 and DATA-D13 are both stated as "reference-pair blocking"). For non-reference pairs, the rule says "if a current-pair review finds an implemented pair/signal absent from the manifest, that is a DATA-D13 failure and must be fixed before data-stage acceptance" — but DATA-D13 only applies its blocking clause to reference pairs. The gap: non-reference-pair missing manifest entries have no defined owner, no defined severity, and no defined path to resolution. My `outstanding-work.md` (BL-D13-MANIFEST) records 6 legacy pairs missing manifest entries with no dispatch date.  
**Severity proposal:** WARN  
**Suggested fix:** Explicitly state a WARN severity and an action path for non-reference-pair manifest gaps: "If a non-reference pair is absent from `data/manifest.json` at time of any data-stage delivery, Dana files a WARN in the handoff note and adds a BL entry for manifest bootstrap. The WARN upgrades to FAIL when that pair enters reference-pair acceptance or when BL entry age exceeds 30 days."

---

### F-03 — Indicator Evaluation Framework section is orphaned with dead cross-references (FAIL)

**Section:** §Indicator Evaluation Framework (lines 457–479)  
**Problem:** This section references `docs/agent-sops/evaluation_schema.md` as the validation target. While that file does exist, the section has no rule ID, no severity designation, no owner field, no integration point, and no quality-gate checkbox in the §Quality Gates block. The two artifact names (`environment_interaction_scores.json`, `strategy_survival_scores.json`) appear nowhere else in the SOP, in `docs/standards.md`, or in the quality-gate checklist. There is no cross-reference to a corresponding ECON or APP rule. The section was presumably imported as a placeholder during multi-indicator expansion but was never anchored to the rule system.  
**Severity proposal:** FAIL (missing rule ID, severity, gate item, and integration point make this a blind spot for enforcement)  
**Suggested fix:** Either (a) promote to a named rule (e.g., DATA-EV1) with severity, quality-gate checkbox, and integration point ("delivered alongside stationarity tests before Ace data-layer handoff"), and register it in `docs/standards.md`; or (b) remove the section if it is not yet in scope, documenting the removal in `sop-changelog.md`.

---

### F-04 — DATA-D6b: Missing from `docs/standards.md` registry (WARN)

**Section:** §6 Rule DATA-D6b — User-Facing Text Fields Use Human-Readable Names  
**Problem:** DATA-D6b was authored in Wave 10G.5 (2026-04-22) and is present in the SOP with full rule text, including a lint procedure and QA check. However, it is not registered in `docs/standards.md` DATA table. Every other named DATA rule (DATA-D1 through DATA-VS) has an entry in `docs/standards.md`. The omission means the rule is invisible to the canonical rule inventory and to other agents consulting `docs/standards.md` for a complete list of Dana-owned blocking rules.  
**Severity proposal:** WARN  
**Suggested fix:** Add a `docs/standards.md` DATA table row for DATA-D6b with one-line description and SOP section pointer. This is a registration gap, not a rule-text gap.

---

### F-05 — DATA-D6b cross-reference to GATE-NR is unregistered in `docs/standards.md` (WARN)

**Section:** §6 Rule DATA-D6b, QA check line  
**Problem:** DATA-D6b states "Quincy's GATE-NR DOM scan now includes this check." GATE-NR is a real rule (defined in `docs/agent-sops/qa-agent-sop.md` as `QA-CL5 / GATE-NR`) but is not registered in `docs/standards.md` GATE or QA tables. The cross-reference from DATA-D6b to GATE-NR therefore points to an unregistered rule. Any future agent checking the standards registry would find GATE-NR does not formally exist.  
**Severity proposal:** WARN  
**Suggested fix:** Add GATE-NR to `docs/standards.md` QA table (or as a sub-item under QA-CL5). This is a cross-SOP registration gap; it is a Phase 3 handoff concern (QA SOP owns GATE-NR), but flagging it here because it makes DATA-D6b's cross-reference unresolvable from `docs/standards.md` alone.

---

### F-06 — `observed_direction` ownership ambiguity in data SOP (FAIL)

**Section:** §6 Deliver — Provenance metadata ownership, and §6 Rule DATA-D6  
**Problem:** Evan's SOP (ECON-DIR1) clearly states that `observed_direction` is owned by Evan (schema `owner_writes` confirms: "Fields Econ Evan owns exclusively. Default set includes `observed_direction`, `direction_consistent`, `key_finding`, `confidence`"). APP-DIR1 in `docs/standards.md` attributes `observed_direction` to Dana ("interpretation_metadata.json.observed_direction (Dana — validated via DATA-D6)"). But the data SOP does not mention `observed_direction` anywhere — neither as a field Dana writes nor as a field Dana must leave blank for Evan. This creates a silent ownership gap: a future Dana dispatch reading only the data SOP has no guidance on whether to populate `observed_direction`, and if Evan files a mismatch report per ECON-DIR1 asking Dana to "set `observed_direction` to match `winner_summary.json.direction`", Dana has no SOP procedure to follow.  
**Severity proposal:** FAIL  
**Suggested fix:** Add a sentence in DATA-D6 procedure step 1 clarifying: "Dana does NOT write `observed_direction`, `direction_consistent`, `key_finding`, or `confidence` — these are Evan's fields per the schema's `owner_writes` map. Leave them absent (to be populated by Evan post-tournament). If Evan files a mismatch report requesting Dana to set `observed_direction`, Dana sets it to match `winner_summary.json.direction` and documents the correction in the handoff note."

---

### F-07 — Quality-gate checkbox for DATA-D6b missing (WARN)

**Section:** §Quality Gates  
**Problem:** Every blocking rule that has a quality-gate procedure (DATA-D5, DATA-D11, DATA-D12, DATA-D13, DATA-VS, DATA-D6, Rule D1) has a corresponding checkbox in the §Quality Gates block. DATA-D6b (blocking by its own text) has no corresponding checkbox. A Dana dispatch running through the checklist before handoff would not be reminded to run the producer-side lint for user-facing text fields.  
**Severity proposal:** WARN  
**Suggested fix:** Add a checkbox: "[ ] Rule DATA-D6b — User-Facing Text Fields Lint: grep `key_finding` for tokens matching `[a-z_]+_(pct|bps|yoy|mom|fwd_\d+d|prob_stress|zscore)\b`; if match found, rewrite with human-readable equivalent. Log lint in handoff note."

---

### F-08 — Expedited Protocol: no owner, no severity, no gate-enforcement path (WARN)

**Section:** §Expedited Protocol for Mid-Analysis Requests  
**Problem:** The Expedited Protocol has a clear process (steps 1–6) but no stated severity for violations (what if Dana skips the lightweight validation?), no quality-gate checkbox, and no statement of who verifies that deferred quality gates eventually get closed. Step 5 says "Full quality gates … are deferred to the next consolidated delivery — note this in the handoff message." There is no mechanism to track whether the deferral is ever resolved. In practice, expedited additions could accumulate without full gate closure.  
**Severity proposal:** WARN  
**Suggested fix:** Add: "Deferred quality gates from an expedited delivery must be recorded as BL entries with an explicit ETA. If the consolidated delivery does not close them within 2 sprints, escalate to Lesandro." Also add a gate-enforcement note: "DATA-E1 compliance: expedited request must include urgency flag and intended use; absence of either is a WARN logged in the handoff."

---

### F-09 — `activity` near-synonym note could contradict `production` enum silently (WARN)

**Section:** §6 Rule D3 — Classification Decision Procedure, Step 2, `indicator_type`  
**Problem:** The note says "Evan's SOP also references `activity` as a near-synonym for `production/macro`." This correctly flags a cross-SOP vocabulary drift. However, the SOP then says "If in doubt between `production` and `macro`, prefer `production` for real-economy output series." This heuristic works for most cases, but there is a subtle softening: the note normalizes `activity` as an acceptable near-synonym in communication with Evan, even though the schema enum explicitly does not include `activity`. A future Dana dispatch could interpret the note as permission to use `activity` informally. The earlier part of the same section explicitly states "EXACTLY this controlled vocabulary" and cross-references that near-synonyms like `activity` are REJECTED at GATE-20 in `team-coordination.md`. The near-synonym language (§D3 Step 2) does not repeat the GATE-20 hard-rejection, creating an ambiguous reading.  
**Severity proposal:** WARN  
**Suggested fix:** Add a clarifying sentence after the near-synonym note: "The term `activity` is Evan's informal language in discussion only; Dana MUST NOT write `activity` in `indicator_type` — the schema enum will reject it and GATE-20 blocks delivery."

---

### F-10 — Stable alias maintenance step 5 requires manifest freshness, but manifest staleness has no FAIL escalation for non-reference pairs (info)

**Section:** §6 Deliver — Stable alias maintenance process, step 5  
**Problem:** Step 5 says "Update `data/manifest.json`" as part of every alias maintenance process. This is correct. However, the manifest staleness scenario (F-02 above) reveals that when a non-reference pair's manifest entry is stale or missing after a `_latest` alias update, the SOP provides no specific failure path. The step is stated as mandatory ("MUST update") but the enforcement weight is inconsistent with the non-reference-pair gap in DATA-D13.  
**Severity proposal:** info (covered by F-02; noting separately because the alias-maintenance procedure and DATA-D13 are separate sections that could each benefit from explicit cross-referencing)  
**Suggested fix:** In the stable alias maintenance steps, add a cross-reference: "See DATA-D13 for manifest freshness gate severity by pair type (reference-pair: FAIL; non-reference: WARN with BL entry)."

---

### F-11 — `docs/data-series-catalog.md` Section 7 / 7.10 / 9 cross-references — file exists but section numbers not validated (info)

**Section:** §4 Clean and Transform and §5 Validate  
**Problem:** Three cross-references point to specific sections of `docs/data-series-catalog.md` (Section 7, Section 7.10, Section 9). The file exists, but the SOP does not verify that these section numbers are stable or that the referenced content (canonical name registry, derived series recipes, alignment rules) actually lives at those sections. If the catalog is restructured, the SOP cross-references go stale silently.  
**Severity proposal:** info  
**Suggested fix:** Change to anchored section headings rather than numbered sections, e.g., "see `docs/data-series-catalog.md` §Canonical Name Registry" so that renames are detectable by grep. Not urgent but reduces drift risk.

---

### F-12 — Provenance metadata ownership section lists many fields without specifying which schema fields they map to (WARN)

**Section:** §6 Deliver — Provenance metadata ownership  
**Problem:** The provenance section says Dana "populates or verifies" fields including "effective start, source frequency, unit, missingness treatment/summary, stationarity-test reference, manifest reference, data dictionary reference, schema/sidecar reference, and canonical signal column." However, it does not state which fields in `interpretation_metadata.schema.json` correspond to each item. A Dana dispatch following this section would not know which JSON keys to write, and the instruction "record the value in the data dictionary/sidecar and include a compact `provenance_refs` pointer" is vague — `provenance_refs` is not defined in the schema (as of Wave 4C-2 v1.0.0). If `provenance_refs` is a proposed field, it needs a schema bump under META-CF before Dana can write it.  
**Severity proposal:** WARN  
**Suggested fix:** Either (a) map each listed provenance item to its schema field name (or note "not yet in schema — record in data dictionary only"), or (b) note that `provenance_refs` is a planned field requiring a META-CF schema bump. Prevents orphaned writes or schema validation failures.

---

### F-13 — `META-DASH1` four-page consistency check has no Dana hook (info)

**Section:** Cross-cutting — no mention in data SOP  
**Problem:** `META-DASH1` (added 2026-05-07, registered in `docs/standards.md`) defines a cross-page consistency checklist for Story, Evidence, Strategy, and Methodology. The protocol section says "Ray owns author-side narrative consistency; Ace owns rendered label/status/navigation consistency; Quincy independently verifies four-page DOM/read-through consistency." Dana's data artifacts (units, direction, classification in `interpretation_metadata.json`) feed the numeric KPIs and metric labels checked by META-DASH1. There is no mention of META-DASH1 in the data SOP, meaning Dana has no reminder to ensure data-layer consistency feeds the four-page audit at handoff.  
**Severity proposal:** info  
**Suggested fix:** Add a brief note in the quality-gate checklist or in the §6 Deliver section: "Dana-owned fields in `interpretation_metadata.json` (`indicator_nature`, `indicator_type`, `observed_direction` if backfilled) feed META-DASH1 four-page consistency checks. Confirm these are consistent before final handoff."

---

### F-14 — ECON-FE1 / GATE-ES1 / APP-LP8 / evidence_status: no Dana hook or cross-reference (info)

**Section:** Cross-cutting  
**Problem:** Three rules introduced in 2026-05-01 (ECON-FE1, GATE-ES1, APP-LP8) define an evidence-status framework that directly reads from data-layer artifacts. APP-LP8 defaults any pair without `results/{pair_id}/evidence_status.json` to `found_in_search`. ECON-FE1 requires a confirmation final exam whose criteria include data-layer provenance (sample separation, artifact validation). None of these are mentioned in the data SOP. Dana has no rule saying "before delivering a final-exam-qualifying dataset, ensure the sample separation is documented and the data artifacts are in a state that can support ECON-FE1 validation."  
**Severity proposal:** info (ECON-FE1 is Evan-owned; the data SOP hook would be advisory, not blocking — but the gap is worth noting for Phase 3)  
**Suggested fix:** Add a brief cross-reference in §6 Deliver: "For pairs that may advance to ECON-FE1 final-exam confirmation, ensure the delivered dataset clearly documents the in-sample/OOS boundary per `results/{pair_id}/oos_split_record.json` (ECON-OOS1) so the sample separation claim in ECON-FE1 is traceable to data provenance."

---

## Strengths Worth Preserving

1. **DATA-D5 / DATA-D6 / DATA-D13 triad is architecturally sound.** The three-tier provenance stack (parquet sidecar, manifest, registry) with machine-readable schemas and producer-side validator calls is the right model. Lead must not collapse this into a single "data quality" rule — the granularity is what enables agent-specific enforcement.

2. **DATA-D12 rule text is excellent even without the enforcement script.** The exemption-list design (identifiers, well-known index levels exempt; unit-valued quantities require suffix) is the right granularity. The grandfathering clause prevents retroactive breakage. Preserve both when the script is finally built.

3. **DATA-D6b lint pattern is precisely specified.** The grep regex `[a-z_]+_(pct|bps|yoy|mom|fwd_\d+d|prob_stress|zscore)\b` is grep-runnable and catches the class of bug that triggered the rule. This is a model for other lint rules in the team.

4. **Rule D3 classification decision procedure (4-step mandatory workflow) is thorough.** The "Step 3 — confirm Evan's Rule C1 has a method list for that indicator_type before delivery" is a cross-agent integration gate that prevents silent routing failures. Keep it.

5. **Stable alias maintenance process (5-step) is the right level of detail.** The ordered steps (save dated → update `_latest` → verify alias → notify Ace → update manifest) close the portal-breakage failure class. Preserve the ordering.

6. **Quality-gate checklist is comprehensive.** The 20+ checkbox items covering data dictionary, stationarity, display names, manifest, unit suffixes, direction, classification, and git push are a genuine value-add over typical data agent SOPs.

7. **Anti-patterns section is correct.** All 8 anti-patterns are real failure classes this team has encountered. Do not condense or remove.

8. **META-CPD cross-reference is present and correct.** The §Git and Handoff Protocol section correctly states the commit-must-push-immediately rule with verification instructions. This was the correct closure of the Wave 10J finding.

---

## Items Deferred to Phase 3 Cross-Review

1. **`observed_direction` ownership disagreement between data SOP and Evan's SOP / APP-DIR1** — data SOP is silent; Evan's SOP says Evan owns it; APP-DIR1 in `docs/standards.md` attributes it to Dana. Needs cross-SOP reconciliation with Evan and Lead. (Related to F-06.)

2. **GATE-NR unregistered in `docs/standards.md`** — requires QA SOP review to confirm GATE-NR's canonical ID, registration, and whether it should appear in the GATE table or QA table. (Related to F-05.)

3. **DATA-D13 non-reference-pair escalation path needs team coordination** — the 6 legacy pairs without manifest entries require a Lead-authorized dispatch to close. The ownership question (does Evan or Ace block on missing manifest for legacy pairs?) is cross-agent. (Related to F-02.)

4. **META-DASH1 role hook for data agent** — whether Dana should have an explicit META-DASH1 checkstep requires alignment with Ray (narrative) and Ace (rendering). Belongs in Phase 3. (Related to F-13.)

5. **`indicator_type: "production"` on `indpro_spy`** — possible enum violation outside controlled vocabulary on a live artifact. Requires Evan confirmation that Rule C1 can route "production". If not, schema bump needed. Cross-agent coordination item.

---

*Phase 1 review complete. No SOP edits made. Findings ready for Lead review.*
