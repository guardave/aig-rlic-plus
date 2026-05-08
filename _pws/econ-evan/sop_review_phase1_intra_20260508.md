# Intra-SOP Review — Econ Evan Econometrics SOP
**Author:** Econ Evan  
**Date:** 2026-05-08  
**Branch:** 260430  
**Phase:** Phase 1 — intra-SOP review only (no edits to any SOP or shared file)  
**SOP reviewed:** `docs/agent-sops/econometrics-agent-sop.md`  
**Standards cross-checked:** `docs/standards.md` ECON block, recent `docs/sop-changelog.md` entries  
**Schemas cross-checked:** `evidence_status.schema.json` v1.1.0, `final_exam_results.schema.json` v1.0.0, `winner_summary.schema.json` v1.1.0  

---

## Findings

### F-01 — ECON-FE1 condition set has no schema-level enforcement for minimum confirmation sample against `final_exam_results.schema.json`
**Section:** Rule FE1, condition 3 (minimum confirmation sample)  
**Problem:** ECON-FE1 states minimum confirmation sample requirements by frequency class (daily ≥ 24 months / 252 trading days; monthly ≥ 36 observations; crypto daily ≥ 18 months / 365 days). The companion `final_exam_results.schema.json` records `confirm_n_obs` as a simple integer with `minimum: 1`. Nothing in the schema enforces the target-class floor specified in ECON-FE1. Evan (or a future agent reading only the schema) could write `confirm_n_obs: 10` and pass schema validation while violating FE1 condition 3. The schema and the prose rule are silently inconsistent — a producer-side validation gap exactly like the ones ECON-FE1 was designed to foreclose.  
**Severity proposal:** FAIL (binding rule condition has no machine-enforced gate)  
**Suggested fix:** Add a `minimum_confirmation_n_obs` field to `final_exam_results.schema.json` that records the target-class floor actually applied, with an assertion comment that `confirm_n_obs >= minimum_confirmation_n_obs`. Until the schema is updated, add a producer-side assertion step to the FE1 checklist: "Before writing `final_exam_results*.json`, assert `confirm_n_obs ≥ class_floor` and log the floor used." Wire this as item 11 in the Quality Gates checklist.

---

### F-02 — ECON-FE1 condition 6 (drawdown gate) ambiguity: "5 percentage points worse" is not ratio-unit consistent
**Section:** Rule FE1, condition 6  
**Problem:** FE1 condition 6 states "winner maximum drawdown may be no more than 5 percentage points worse than benchmark maximum drawdown." But the project-wide convention (META-UC, ECON-H5, all artifact schemas) is ratio form (−0.102 = −10.2%). "5 percentage points" in ratio-unit context is −0.05. This is internally consistent if interpreted correctly, but the prose uses "percentage points" while all artifacts use ratio form — a unit-vocabulary inconsistency that could cause a numeric error when implementing the gate check. The `final_exam_results.schema.json` field `confirm_delta_max_drawdown` has no documented threshold constraint.  
**Severity proposal:** WARN (ambiguous, not wrong, but a likely implementation error)  
**Suggested fix:** Replace "5 percentage points" with "0.05 in ratio units (i.e., the winner's `confirm_max_drawdown` may be no more than 0.05 below the benchmark's `confirm_benchmark_max_drawdown` on the negative axis)" to align with the artifact schema vocabulary.

---

### F-03 — ECON-FE1 condition 7 (block-bootstrap) lacks definition of "stationary bootstrap" vs "circular block bootstrap"
**Section:** Rule FE1, condition 7  
**Problem:** Condition 7 says "stationary or circular block bootstrap" and provides block-length defaults (daily 21 trading days, monthly 6 months, crypto 30 calendar days). The `final_exam_results.schema.json` enum for `bootstrap_method` correctly limits values to `["stationary", "circular_block"]`. However, FE1's SOP prose does not define these terms, does not explain when to prefer one over the other, and does not specify how the block length should be selected when the default is inappropriate (e.g., a highly autocorrelated monthly series where 6 months is too short). A new Evan instance starting fresh would not have enough context to make a principled choice.  
**Severity proposal:** WARN (operational ambiguity; experienced Evan would know, but the rule doesn't self-document)  
**Suggested fix:** Add a one-paragraph note under condition 7: "Prefer stationary bootstrap when autocorrelation structure is uncertain; prefer circular block bootstrap when the series has a dominant seasonal frequency. Default block lengths are starting points — if the autocorrelation function shows significant structure beyond the default block length, multiply by 1.5 and document in `uncertainty.block_length`. Reference: Politis and Romano (1994) for stationary; Künsch (1989) for circular."

---

### F-04 — ECON-FE1 consumer-wording guard cross-reference is missing: GATE-ES1 cross-link absent
**Section:** Rule FE1, "Consumer wording guard" paragraph  
**Problem:** The FE1 consumer wording guard ("if Evan uses shorthand such as 'fresh holdout'... it means this full FE1 contract") correctly targets Ray and Ace as downstream consumers. However, it does not explicitly reference GATE-ES1 (the QA-side gate that independently enforces this). Without the GATE-ES1 cross-reference, a Ray or Ace reading only the FE1 section of Evan's SOP would not know that Quincy independently verifies the full contract before the status can land in the portal. The asymmetry in cross-references (FE1 → no GATE-ES1; GATE-ES1 → FE1 presumably present in QA SOP) leaves the integration point partially documented.  
**Severity proposal:** WARN (missing link, not a rule contradiction)  
**Suggested fix:** At the end of the FE1 consumer wording guard, add: "Cross-reference: GATE-ES1 (QA Quincy) independently verifies every promotion above `found_in_search`. The consumer wording guard operates alongside GATE-ES1, not as a substitute."

---

### F-05 — ECON-H5 winner_summary.schema.json cross-reference still cites v1.0.0; schema is now at v1.1.0
**Section:** ECON-H5 (Winner Summary JSON Contract), and the `standards.md` ECON block  
**Problem:** ECON-H5 in the SOP body reads: "Canonical schema: `docs/schemas/winner_summary.schema.json` (per META-CF, owned by Evan, version 1.0.0)." The actual schema file carries `"x-version": "1.1.0"`. This was bumped during Wave 10I.A (`threshold_value` `null` allowed, BL-THRESHOLD-VALUE-SCHEMA fix, commit recorded in session-notes Wave 10I). The SOP version citation is stale — any agent reading the SOP to determine the current contract version will see v1.0.0 when the live schema is v1.1.0. Similarly, `standards.md` ECON row for ECON-H5 says "v1.0.0". Both are stale.  
**Severity proposal:** FAIL (stale version reference can silently mislead producers about required fields)  
**Suggested fix:** Update the ECON-H5 SOP sentence to read "version 1.1.0" and add a parenthetical noting the change: "(v1.1.0: `threshold_value` now accepts `null` for legacy pairs per BL-THRESHOLD-VALUE-SCHEMA)." Also update `standards.md` ECON-H5 row.

---

### F-06 — ECON-CP1-B output file uses `{pair_id}` suffix but Rule C2 mandatory outputs do not — creates inconsistent naming pattern
**Section:** ECON-CP1, CP1-B output file `rolling_correlation_{pair_id}.csv`  
**Problem:** ECON-CP1-B mandates `results/{pair_id}/rolling_correlation_{pair_id}.csv` (pair_id appears in both directory and filename). ECON-CP1-C mandates `results/{pair_id}/structural_break_{pair_id}.json` (same pattern). ECON-CP2-A and CP2-B similarly use `{pair_id}` in both directory and filename. Rule C2 mandatory outputs — `correlations.csv`, `granger_causality.csv`, `local_projections.csv`, etc. — have NO pair_id suffix. The naming inconsistency creates a predictability problem: Vera and Ray cannot infer whether a given file has a pair_id suffix or not without checking the specific rule. It also means the C2 file-existence check (via canonical path) would require different logic for C1/C2 files versus CP1/CP2 files.  
**Severity proposal:** WARN (inconsistency; not a blocking failure but causes confusion at the consumer boundary)  
**Suggested fix:** Either (a) document explicitly in the Standard Evidence Block table that CP1/CP2 files include `{pair_id}` in their names to signal that they are pair-specific rather than method-generic, or (b) standardize all files to the `{method}_{pair_id}.csv` pattern. Option (a) is lower-risk and requires only a comment. Note for cross-review: Vera's chart filename convention uses pair_id in the directory only; this asymmetry should be flagged to Vera in Phase 3.

---

### F-07 — ECON-CP1 methodology_note (outstanding-work.md) is not yet in SOP — CP1 handoff annotation requirement is unenforceable
**Section:** ECON-CP1 / outstanding-work.md  
**Problem:** `_pws/econ-evan/outstanding-work.md` explicitly records that "ECON-CP1 methodology_note [Next pair — before Vera handoff]" is a rule that must be added to the SOP before Pair #4 handoff. The SOP currently does not include the CP1 annotation requirement: "Sub-period Sharpes reflect directional durability only (sign(signal) × return), NOT replication of tournament execution mechanics. Use tournament OOS Sharpe as the point-estimate reference." Without this in the SOP, the requirement is ephemeral — it lives only in a PWS note that a new Evan instance would not read on SOD. This was also identified in Wave 10J/10K self-reflection as a structural gap.  
**Severity proposal:** FAIL (documented required rule that was never promoted from PWS to SOP — exactly the dead-letter pattern ECON-CP1 is meant to prevent)  
**Suggested fix:** Add a mandatory annotation requirement to ECON-CP1 (as a sub-bullet of CP1-A or as a standalone "Handoff Annotation" rule): Evan must include the following text in every Vera and Ray handoff that contains `subperiod_sharpe.csv`: "Note: Sub-period Sharpes reflect directional durability only (sign(signal) × return), NOT replication of tournament execution mechanics. Use tournament OOS Sharpe as the point-estimate reference." This annotation prevents downstream agents from misinterpreting sub-period Sharpes as tournament replications.

---

### F-08 — ECON-CP1 "episode selection via episode_registry.json" cross-reference has no schema path or schema version reference
**Section:** ECON-CP1-A, "Episode selection" paragraph  
**Problem:** CP1-A says "Read episodes from `docs/schemas/episode_registry.json` keyed on `interpretation_metadata.indicator_category`." The registry file exists at `docs/schemas/episode_registry.json` (confirmed by directory listing). However, the SOP provides no schema reference for the registry file itself (no `$ref` to `episode_registry.schema.json`), no mention of the registry's current version, no instruction on what Evan must do if the `indicator_category` value does not exist in the registry (apart from "use `_fallback`"), and no cross-reference to where the registry was defined (RES-EPIS1 in the Cross-Agent Impact Log). A new Evan arriving without session context would have partial guidance only.  
**Severity proposal:** WARN (incomplete documentation; functional but not self-documenting)  
**Suggested fix:** Add a cross-reference footnote: "Registry schema: `docs/schemas/episode_registry.schema.json` (if it exists) or as defined in RES-EPIS1. If `indicator_category` is absent from the registry and no `_fallback` key exists, escalate to Lead before proceeding." Verify whether `episode_registry.schema.json` exists; if not, flag to Lead as a META-CF gap.

---

### F-09 — ECON-T4 (Regime Signal Leakage Guard) is in the SOP body under Tournament Design Parameters but is NOT registered in `standards.md`
**Section:** ECON-T4, Tournament Design Parameters block  
**Problem:** ECON-T4 is a well-articulated rule with clear owner (Evan), severity (BLOCKING for full-sample-fit signals), and integration point (tournament OOS evaluation). However, it does not appear in `docs/standards.md` ECON block. The canonical rule inventory (standards.md) is supposed to be the "source of truth for rule identity and inventory." An agent consulting standards.md to confirm rule coverage would not find ECON-T4, creating a silent completeness gap. `ECON-INF1` (Headline Inference Under Dependence, found in the SOP under §6 Estimation) has the same problem — it is not in standards.md either.  
**Severity proposal:** FAIL for ECON-T4 (blocking rule unregistered); WARN for ECON-INF1 (important but less critical)  
**Suggested fix:** Register ECON-T4 and ECON-INF1 in `docs/standards.md` ECON block with their one-line descriptions and SOP section pointers. This is Lead's remit per the standards.md preamble, but the gap should be flagged to Lead in the Phase 1 report.

---

### F-10 — ECON-DIR2 (alignment gate) is defined in the interpretation_metadata section but has no Quality Gates checklist item and no standards.md registration
**Section:** Interpretation metadata section, ECON-DIR2 note  
**Problem:** ECON-DIR2 is defined as: "Set `direction_consistent = true` only when the headline evidence and the winning strategy align on sign, horizon, and exploited signal/rule." It is embedded in the field notes of the interpretation_metadata template rather than as a top-level rule with an ECON-XXX heading, no standards.md entry, and no Quality Gates checklist item explicitly referencing it. ECON-DIR1 (direction receipt gate) IS in the Quality Gates checklist. ECON-DIR2 governs a closely related but distinct step — it gates the producer writing `direction_consistent: true`. Without a checklist item, it can be silently skipped.  
**Severity proposal:** WARN (the rule exists and is accessible, but its enforcement hook is weak)  
**Suggested fix:** Add ECON-DIR2 to the Quality Gates checklist as a standalone item: "Verify `direction_consistent` follows ECON-DIR2: true only when headline evidence (regression/correlation sign), winning signal type, threshold orientation (lt/gt), and tournament winner's direction all align. If a mismatch exists, set `direction_consistent: false` and add a `contradictions` note." Register ECON-DIR2 in standards.md.

---

### F-11 — BL-LEGACY-WINNER-SUMMARY-SHAPE is tracked in outstanding-work.md but no wave target or retro-apply checklist exists in the SOP
**Section:** Outstanding-work.md / ECON-H5 / Anti-Patterns  
**Problem:** BL-LEGACY-WINNER-SUMMARY-SHAPE documents 6 legacy pairs with `winner_summary.json` files missing 7+ required fields from schema v1.1.0. This was flagged as "Wave 10K first dispatch" in `_pws/econ-evan/outstanding-work.md` and session-notes but never received a wave target. The SOP does not mention this backlog item, does not mandate a schema version sweep on schema bumps, and has no rule requiring Evan to run a portfolio-wide `validate_schema.py` pass when the `winner_summary.schema.json` version bumps. The Wave 10J/10K self-reflection explicitly identified this as a lesson: "every schema bump should trigger a portfolio-wide sweep before anything else." Yet the SOP does not encode this as a rule.  
**Severity proposal:** FAIL (known failure mode, documented lesson, not gated)  
**Suggested fix:** Add a rule (proposed: ECON-BUMP1 or as a sub-rule of ECON-H5): "On any `winner_summary.schema.json` version bump (minor or major), before any other work, run `validate_schema.py` against every committed `results/*/winner_summary.json` and record failures in a version-bump regression note. No new pair handoff proceeds until the sweep completes and all failures are either fixed or documented as BL items with wave targets."

---

### F-12 — ECON-INFD1 "Headline Inference Under Dependence" (ECON-INF1) lacks a producer-side artifact requirement — the rule is advisory only
**Section:** §6 Estimation, ECON-INF1  
**Problem:** ECON-INF1 is a well-formed rule mandating robust inference (HAC/Newey-West, clustered SEs, stationary/circular block bootstrap for overlapping returns), but it only instructs Evan to "record the robust method, lag/block length, and whether the headline claim survives in the result manifest." There is no artifact name, no schema path, no verification step, and no downstream consumer cited. "Record in the result manifest" is ambiguous — which manifest? The `_manifest.json` sidecar? The `method_coverage_manifest.json` (Rule C2a)? Without a specific artifact name, ECON-INF1 is not verifiable by Quincy.  
**Severity proposal:** WARN (the rule has the right content but is not operationalized into a checkable artifact)  
**Suggested fix:** Specify that the robust inference method, lag/block length, and survival verdict must appear in `results/{pair_id}/core_models_{date}/method_coverage_manifest.json` under a new `inference_robustness` key (or in a dedicated `inference_checks.json`), and add ECON-INF1 to the Quality Gates checklist with a pointer to where the record lives.

---

### F-13 — ECON-SD audit cross-reference dead-letter: SOP says Quincy verifies scope discipline but Quincy's SOP does not name this check
**Section:** ECON-SD, "Enforcement" → "QA (Quincy)" sub-bullet  
**Problem:** ECON-SD states "QA (Quincy). Verifies every pair page's chart set and table set against `signal_scope.json`; any off-scope signal found is a GATE-31 block." The cross-agent impact log entry for ECON-SD notes this as a dead-letter (Wave 10J self-reflection, outstanding-work.md: "ECON-SD audit dead-letter — Quincy SOP does not name this check; escalate to Lead"). After the Phase 1 intra-review, this remains an unresolved gap: Evan's SOP says Quincy does something that Quincy's SOP does not mandate. This creates an integration seam with no enforcement on the QA side.  
**Severity proposal:** FAIL (integration contract with no downstream commitment)  
**Suggested fix (Evan's side):** Add a producer-side backup: "If Quincy's SOP does not include the ECON-SD audit gate, Evan must include scope compliance evidence (the `signal_scope.json` validation pass) in the handoff note, not merely in a sidecar." For Phase 3, flag this to Lead for routing to Quincy as a mandatory addition to GATE-31. 

---

### F-14 — "OOS" and "block-bootstrap" defined piecemeal; no single definitional section exists
**Section:** SOP-wide  
**Problem:** "OOS" (out-of-sample) is used extensively but never defined in a glossary or definitional section within the SOP. Different sections use related terms inconsistently: "OOS window" (ECON-OOS1/OOS2), "OOS period" (ECON-H5), "confirmation window" (ECON-FE1), "test set" (ECON-OOS2 ELI5). A new Evan instance must infer from context that the tournament OOS window (per ECON-OOS2 sizing formula) and the FE1 confirmation window are distinct concepts — the former was used during recipe selection (making it unsuitable for final exam); the latter must be genuinely post-selection. This distinction is critical to FE1 integrity and is implicit rather than explicit. Similarly, "block-bootstrap" is used in FE1 condition 7 and ECON-INF1 with slightly different framing each time.  
**Severity proposal:** WARN (experienced Evan would infer correctly; new Evan or a QA reviewer might conflate them)  
**Suggested fix:** Add a "Key Terms" sub-section at the top of ECON-FE1 (or a SOP-wide glossary appendix) defining: OOS window (tournament use; per ECON-OOS2 formula; used during selection), confirmation window (post-selection; must not overlap tournament OOS by condition 2 of FE1), block bootstrap (block-resampling method that preserves serial dependence structure), tournament winner (the rule selected from the full tournament search; discovery-grade until FE1 passes). Cross-reference ECON-OOS1 and ECON-OOS2 from this glossary entry.

---

### F-15 — Rule C2a (Method Coverage Manifest) has no entry in standards.md or Quality Gates checklist
**Section:** §2.5 Rule C2a, and Quality Gates  
**Problem:** Rule C2a ("Before handoff, write `results/<pair>/core_models_<date>/method_coverage_manifest.json`") is defined with clear fields (`status`, `artifact_path`, `skip_reason`, `producer_assertions_passed`) and cross-references META-NMF and META-DASH1. However, it is absent from `docs/standards.md` ECON block and absent from the Quality Gates checklist. Without a Quality Gates entry, C2a can be silently skipped. Without a standards.md entry, it is not part of the canonical rule inventory. This makes C2a invisible to Lead's rule inventory review.  
**Severity proposal:** WARN (the rule is well-formed but its enforcement hook is missing)  
**Suggested fix:** Add ECON-C2a to `docs/standards.md` ECON block. Add a Quality Gates checklist item: "`method_coverage_manifest.json` written to `core_models_{date}/` before Vera handoff — every C1 mandatory method listed with `produced` or `skipped` status."

---

### F-16 — ECON-OOS3 (OOS Count Semantics) is in the SOP body under Tournament Design but absent from standards.md
**Section:** Tournament Design Parameters, ECON-OOS3  
**Problem:** ECON-OOS3 defines the distinction between `oos_n_obs` and `oos_n_trades` and is labelled as a named rule. It does not appear in `docs/standards.md`. Same class of gap as F-09 (ECON-T4). ECON-OOS3 is semantically important because consumers (Ray, Ace) depend on these fields being correctly populated; a mislabeled `oos_n_obs` would silently pass schema validation (both are `integer, minimum: 0`) while violating the semantic contract.  
**Severity proposal:** WARN (important rule, incomplete registration)  
**Suggested fix:** Register ECON-OOS3 in `docs/standards.md` ECON block: "OOS Count Semantics — `oos_n_obs` counts dated return observations after alignment; `oos_n_trades` counts position-change events only. Both fields must be present in `winner_summary.json` and `tournament_summary.csv` with identical semantics. Backfilled period counts must not be stored as `oos_n_trades`."

---

### F-17 — Rule E2 / Rule C2 naming ambiguity: `quartile_returns.csv` vs `regime_quartile_returns.csv` creates confusion
**Section:** Rule E2 and Rule C2, interaction note  
**Problem:** Rule E2 renames the artifact from `quartile_returns.csv` (Rule C2 row) to `regime_quartile_returns.csv` and provides an interaction note explaining that C2's `quartile_returns.csv` schema remains valid for signal-threshold-defined quartiles while E2's `regime_quartile_returns.csv` is canonical for regime/HMM quartile analysis. This distinction exists but the vocabulary is fragile: the C2 table still lists `quartile_returns.csv` as a row label. A reader of C2 alone would see `quartile_returns.csv` as the output file, then find E2 renames it. The interaction note is there, but it requires reading both sections in sequence. Vera's consumption path (VIZ-V4) is not told which filename to expect in which context.  
**Severity proposal:** WARN (clear to a careful reader; ambiguous for a downstream agent reading only their own SOP section)  
**Suggested fix:** Add a disambiguation note directly in the C2 table row for `quartile_returns.csv`: "(see Rule E2: for regime/HMM quartile analysis, use `regime_quartile_returns.csv` instead; `quartile_returns.csv` applies only to signal-threshold-defined quartiles)." This makes the disambiguation visible without reading E2.

---

### F-18 — Intake validation (§1 Receive Analysis Brief) and Method Category Selection (§2.5) are separate steps but have no explicit integration: what happens if the intake validation finds a conflict with Ray's indicator type classification?
**Section:** §1 Receive Analysis Brief, §2.5 Method Category Selection  
**Problem:** The Intake validation (§1) requires checking that "target-class-specific parameters are consistent with the target's asset class." Step 2.5 begins "Before specifying models, determine which analysis categories to apply." There is no explicit rule for what Evan does if the intake validation (§1) flags a parameter inconsistency at the same time as Ray's indicator type classification (§2.5's "Indicator type classification check") is ambiguous. Both checks can fire simultaneously; the SOP has no triage rule for which to resolve first. If Ray's classification is wrong, the entire C1 method catalog selection is invalidated; if the intake parameter is wrong, the tournament results are invalidated. The inter-dependency ordering is unstated.  
**Severity proposal:** WARN (edge-case conflict resolution undocumented)  
**Suggested fix:** Add a one-sentence triage rule at the end of §1: "If both intake parameter errors AND indicator type ambiguity are found, resolve indicator type first (it determines the C1 method catalog); intake parameters can be corrected before tournament execution without invalidating exploratory analysis."

---

## Strengths Worth Preserving

1. **Rule C2 Mandatory Output Schema table** — exact column names, exact file paths, skip-file convention. This is the right level of specification. Vera and Ray can implement consumers without guessing.
2. **ECON-T3 Tie-Break Cascade** — fully deterministic 5-step cascade with artifact requirement (`tournament_tie_note.md`). Excellent self-documentation of the failure mode it forecloses.
3. **ECON-FE1 10-condition structure** — the 10 conditions for `passed_final_exam` are well-ordered, cover the key threats (selection, confirmation sample size, costs, uncertainty, multiple testing, QA replay), and are internally non-redundant. The consumer wording guard is a useful addition.
4. **ECON-OOS2 formula and ELI5 requirement** — the dual technical + plain-English label requirement for the OOS window is a good pattern. The formula itself (`min(max(36, round(N×0.25)), 120)`) is precisely specified and independently reproducible.
5. **ECON-DIR1 consumer-gatekeeper framing** — the step-by-step vocabulary check + consistency check + "return to Dana, do not patch yourself" discipline is the right answer to the scope-violation bug uncovered in Wave 10I.C. The "Ownership note" paragraph is especially important.
6. **Anti-Patterns section** — comprehensive, specific, and directly tied to prior failure modes. The three stationarity/signal_scope/direction sentinel lessons added in Wave 10I.C are examples of the right pattern: failure → anti-pattern → SOP.
7. **Task Completion Hooks + End-of-Task Reflection** — both hooks exist and are specific. The Reflection items map directly to the kinds of learnings that ended up in `memories.md`.
8. **Rule C2a Method Coverage Manifest** — good producer-gate concept, even if enforcement hooks are incomplete (F-15 above).
9. **ECON-INFD1 (ECON-INF1) placement** — correctly placed after the Estimation section, not as a footnote. The specific callout for overlapping forward returns (plain OLS p-values diagnostic-only) is correct.

---

## Items Deferred to Phase 3 Cross-Review

*Handoff concerns with peer agents — listed briefly only, per LEAD-DL1. No edits to peer SOPs in Phase 1.*

**Dana (Data):**
- D-CR1: `interpretation_metadata.json` ownership chain. The SOP's ECON-DIR1 gate correctly delegates `observed_direction` correction to Dana, but the SOP does not cite `DATA-D6` (Classification Schema Versioning Contract) as the upstream binding rule that makes Dana the sole writer. Adding the cross-reference would strengthen the justification.
- D-CR2: `DATA-DD3` (Stationarity Test Delivery) is listed as "Dana owns execution, Evan reviews." ECON-SOP §4 (Exploratory Analysis) says "If Dana has already provided stationarity tests, review and confirm rather than re-running from scratch." This is consistent, but the mandatory artifact rule (§4) says Evan saves the CSV. There is a potential double-write risk if Dana delivers a stationarity CSV and Evan also saves one under a different filename. Suggest clarifying ownership of the stationarity CSV file (Dana produces it? Evan produces it? Or both, with naming disambiguation?).

**Vera (Viz):**
- V-CR1: ECON-H4 (per-method chart artifact handoff table) sends a `status: ready/blocked/pending` for each method. But VIZ-V8 (chart type registry) is the authoritative source on canonical filenames. If a file passes Evan's `status: ready` check but the canonical filename in VIZ-V8 differs from what Evan's pipeline writes, the chart loader will fail. The cross-reference in ECON-H4 to VIZ-V8 should be made explicit with a producer-side instruction: "Before writing `status: ready`, verify the output filename against VIZ-V8's `canonical_filename_pattern` for the method."
- V-CR2: Rolling 24M correlation output file (`rolling_correlation_{pair_id}.csv`) and rolling Sharpe (`rolling_sharpe_{pair_id}.csv`) are produced by Evan but consumed by Vera. Vera's VIZ-CP1 cross-reference in standards.md is vague ("current/reference and cross-period comparisons must use registry-approved chart types"). The exact filenames Vera reads are in Evan's SOP, not Vera's. Risk: Vera's SOP doesn't enumerate these files, so future Vera may not know to look for them. Evan should include both files in ECON-H4 handoff table with explicit `status` field for CP1 artifacts.

**Ray (Research):**
- R-CR1: ECON-CP1 says "If `flagged: true` in `structural_break_{pair_id}.json`, Ray's narrative must include the caution flag verbatim." Whether Ray's SOP includes this requirement is not cross-checked here (Phase 1 scope). Flag to Phase 3 to verify RES-Q1 Quality Gates include structural break flag propagation.
- R-CR2: CP1-A durability verdict ("durable", "conditionally durable", "episode-concentrated") is not defined in standards.md, not cross-referenced to Ray's narrative vocabulary, and not in any schema. Ray needs to render this verdict in narrative; if the vocabulary drifts, the portal will be inconsistent. Flag for cross-review.

**Quincy (QA):**
- Q-CR1: F-13 above (ECON-SD dead-letter audit). Quincy's SOP does not mandate the scope discipline check Evan's SOP assigns to Quincy. Phase 3 should confirm whether GATE-31's catch-all language covers ECON-SD, or whether a specific gate item needs to be added.
- Q-CR2: F-01 above (FE1 minimum confirmation sample). GATE-ES1 (Quincy's evidence-status gate) checks schema validity but cannot enforce the numeric floor if `final_exam_results.schema.json` does not enforce it. Phase 3 should determine whether GATE-ES1 should include an explicit numeric check for `confirm_n_obs >= class_floor`.

**Ace (AppDev):**
- A-CR1: ECON-FE1 consumer wording guard targets Ray and Ace. APP-LP8 (Evidence-Status Honesty Label) is the consumer-side rule that lands the evidence-status badge on landing cards. The cross-reference between FE1 and APP-LP8 flows through the evidence_status schema, which is correct. But the SOP does not mention APP-LP8 as an Ace-facing integration point for the FE1 status. If Ace reads only APP-LP8 without knowing about FE1 condition 10, Ace may render `passed_final_exam` without verifying that `evidence_status.json.final_exam.qa_status == "qa_passed"`. Flag for Phase 3.

---

*Total findings: 18 (F-01 through F-18)*  
*FAIL severity: F-01, F-05, F-07, F-09 (ECON-T4), F-11, F-13 — 6 findings*  
*WARN severity: F-02, F-03, F-04, F-06, F-08, F-09 (ECON-INF1), F-10, F-12, F-14, F-15, F-16, F-17, F-18 — 13 findings*  
*(F-09 maps to one FAIL + one WARN)*  

---

*Full findings file: `/workspaces/aig-rlic-plus/_pws/econ-evan/sop_review_phase1_intra_20260508.md`*  
*This file is Evan's PWS only — no SOP or shared file edits per LEAD-DL1.*
