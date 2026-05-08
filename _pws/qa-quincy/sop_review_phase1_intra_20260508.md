# QA SOP Phase 1 Intra-SOP Review
*Date: 2026-05-08*
*Reviewer: QA Quincy*
*SOP file reviewed: `docs/agent-sops/qa-agent-sop.md`*
*Gate code reviewed: `scripts/cloud_verify.py`*
*Scope: completeness, self-consistency, definitions, coverage gaps, cross-references, severity, SOP↔code drift — NO edits made.*

---

## Findings

### F-01 | GATE-HZE1 declared in SOP but NOT implemented in `scripts/cloud_verify.py`
**Section:** QA-CL4 / GATE-HZE1 (line 517–572 of SOP)
**Severity: CRITICAL (Code-Drift)**

The SOP defines GATE-HZE1 in full, including a complete `gate_hze1_check()` pseudocode block and an explicit integration point: "add a call to `gate_hze1_check()` (or equivalent) ... as part of GATE-28 Story-page DOM check." `cloud_verify.py` references GATE-HZE1 only in comments (lines 587, 896) — as a statement that GATE-DP1 is *beyond* what GATE-HZE1 can catch. There is no `gate_hze1_check()` function and no HZE_HEADING assertion in `check_page()`. The SOP says the heading absence check must run for every Story DOM captured during GATE-28's browser pass; the code does not implement it.

**Consequence:** Story pages that silently omit "How the Signal Performed in Past Crises" (no zoom charts committed) currently generate WARN only from `cloud_verify.py` output — but only because the Outstanding Work item OW-3 says Ace is the designated implementer. The SOP says QA is the *author* of the gate and the code should be here. The OW-3 entry says "Ace is designated implementer" per the cross-agent impact log — but the SOP itself says the verification command pattern belongs in `cloud_verify.py`, not in Ace's code. The ownership assignment (Ace implements, Quincy wires gate code) is not reflected in the SOP text, creating an ambiguity about who is responsible for writing the heading-presence check.

**Suggested fix (Phase 4):** Either (a) implement `gate_hze1_check()` in `cloud_verify.py` per the SOP pseudocode, or (b) add a note in the SOP section clarifying that this gate currently runs as HABIT-QA1 manual DOM read only, and that OW-3 tracks script automation pending Ace's config wire-up. A gate declared in the SOP with a "verification command pattern" that is not in the script is SOP↔code drift.

---

### F-02 | Evidence page tab structure check (SOP §4 point 6) not in `cloud_verify.py`
**Section:** Verification Methods §4 Cloud Visual Smoke, item 6 (line 158)
**Severity: HIGH (Code-Drift)**

SOP states: "Asserts Evidence page tab structure matches reference — the Evidence page must render the Level 1 / Level 2 tabs consistent with `hy_ig_v2_spy_evidence`. Check by asserting at least one tab with text 'Level 1' or 'Basic Analysis' exists in the DOM." This is named as a GATE-28 structural failure if absent. `check_page()` in `cloud_verify.py` does not assert for "Level 1", "Level 2", or "Basic Analysis" text. No `tab_structure_ok` field appears in the check result dict or the verdict logic.

**Consequence:** A regression that flattens the Evidence page tab structure to a single level would pass all current code checks, producing a false-PASS on what the SOP calls a GATE-28 structural failure.

**Suggested fix (Phase 4):** Add `level_tab_missing = ("Level 1" not in html and "Basic Analysis" not in html)` to `check_page()` for Evidence pages, include it in the verdict logic, and add a result field.

---

### F-03 | GATE-NR (QA-CL5) declared in SOP with no code implementation
**Section:** QA-CL5 / GATE-NR (lines 720–752)
**Severity: HIGH (Code-Drift)**

The SOP defines GATE-NR — a DOM scan for wrong-pair instrument names — with a pseudocode block (`wrong_instruments` check) and the statement "When GATE-NR fires: every wave that adds or modifies Story or Evidence pages." There is no GATE-NR check in `cloud_verify.py` (confirmed by grep: zero hits on GATE-NR, `KNOWN_INSTRUMENTS`, `target_symbol`, or the wrong-instrument check logic). The checklist at QA-CL1 line 290 includes "QA-CL5 / GATE-NR — Narrative instrument reference check passes," implying it is a required check not a manual-only suggestion.

**Severity note:** Because GATE-NR is explicitly on the QA-CL1 checklist as a mandatory wave item, its absence from `cloud_verify.py` means the only enforcement path is a manual HABIT-QA1 DOM read. That is fragile — the HABIT-QA1 scan list (line 240) does not name instrument-name scanning as a required pattern, so it is easy to miss.

**Suggested fix (Phase 4):** Either implement a GATE-NR scan in `cloud_verify.py` (instrument allow-list per pair loaded from `interpretation_metadata.json`) or add "instrument names out of pair scope" to the STUB_PATS / APP_SEV1_PATS scan list as a partial mitigation, and note the manual residual in the SOP.

---

### F-04 | GATE-ES1 has no `cloud_verify.py` hook or checklist slot
**Section:** GATE-ES1 (lines 350–410)
**Severity: MEDIUM (Completeness Gap)**

GATE-ES1 — Evidence-Status Promotion Verification — is a fully specified gate with an eight-step protocol and a finding template. However:
1. It has no slot in the QA-CL1 master checklist (lines 266–297). A reviewer running QA-CL1 top-to-bottom would not be reminded to run GATE-ES1 unless they already knew the pair had a non-`found_in_search` status.
2. The SOP says step 8 mirrors HABIT-QA1 — "script PASS gathers evidence; Quincy still makes the judgment" — but there is no triggering script step documented, even a manual command.
3. `cloud_verify.py` has no `evidence_status.json` check anywhere.

This is acceptable for the current state (all pairs are `found_in_search`; OW-4 tracks the arbitration), but it will become a live gap the moment any pair promotes. The SOP does not say "gate fires only when status > found_in_search"; a reader following QA-CL1 literally would not realize they need to run GATE-ES1 at all.

**Suggested fix (Phase 4):** Add a QA-CL1 checklist item: "[ ] GATE-ES1 — If any pair has `evidence_status > found_in_search`, run promotion verification protocol." Also add a `check_evidence_status_promotion()` helper stub in `cloud_verify.py` that reads `evidence_status.json` per pair and emits a WARN if status is above `found_in_search` without a documented QA sign-off.

---

### F-05 | GATE-31 has no standalone definition block; role is ambiguous
**Section:** Multiple references (lines 303, 330, 336, 438, 876)
**Severity: MEDIUM (Completeness Gap)**

GATE-31 is described as "Independent QA Verification (the gate this role exists to satisfy)" in the Cross-References section and is invoked by name throughout the SOP as the ultimate blocking gate. However, it has no own section. There is no definition of:
- What exact checks GATE-31 subsumes (is it QA-CL2 + QA-CL3 + QA-CL4 + QA-CL5, or the union of all gates?)
- What the formal trigger is (every wave? every pair? every acceptance.md?)
- What documentation is required when GATE-31 passes (beyond the findings block format)
- Whether GATE-31 can partially pass (some pairs pass, others don't)

A new reader of the SOP would understand that QA-CL2 FAILs are GATE-31 FAILs, but not what GATE-31 *is* as a defined gate — owner, scope, severity, completion criteria. The `acceptance.md` sign-off requirement is described in team-coordination.md (step 10) but not summarized here.

**Suggested fix (Phase 4):** Add a "GATE-31 — Independent QA Verification" subsection that defines: scope (all active pairs in the wave), completion criteria (all GATE-27/28/29 + QA-CL2/3/4/5 checks pass or have documented exceptions), output (QA sign-off block in acceptance.md), and severity (blocking — acceptance.md may not be signed without it).

---

### F-06 | GATE-VIZ-NBER1 severity transition still WARN; no explicit "flip trigger" documented
**Section:** QA-CL4 / GATE-VIZ-NBER1 (line 452)
**Severity: MEDIUM (Stale / GATE-32 Violation Risk)**

The SOP states: "Severity transition: WARN during Wave 10J retro; FAIL after VIZ-NBER1 retro-apply is confirmed complete across all active pairs." The code (`check_page()` lines 400–417, `CROSS_PERIOD_STUB_IS_FAIL = False`) still treats NBER absence as WARN. There is no boolean flag in `cloud_verify.py` for the NBER1 WARN→FAIL transition (unlike GATE-32's `CROSS_PERIOD_STUB_IS_FAIL` flag). The SOP references OW-2 (outstanding work item), but GATE-32's own rule states: "do not carry forward WARN→FAIL transitions." Wave 10J is past. There is no documented trigger for when "VIZ-NBER1 retro-apply is confirmed complete" — no checklist step, no Vera handoff criterion, no Quincy verification action.

**Suggested fix (Phase 4):** Add a `NBER1_WARN_IS_FAIL = False` flag in `cloud_verify.py` (parallel to `CROSS_PERIOD_STUB_IS_FAIL`) and add a QA-CL1 checklist item: "[ ] GATE-VIZ-NBER1 severity — confirm whether VIZ-NBER1 retro-apply is complete (Vera to confirm); if yes, flip `NBER1_WARN_IS_FAIL = True` and re-run." Also add OW-2's resolution criteria explicitly to the SOP rather than leaving it as "Quincy checks OW-2."

---

### F-07 | GATE-DP1 "abort browser run" rule is in SOP but not enforced in code
**Section:** GATE-DP1 integration point (line 655)
**Severity: MEDIUM (Code-Drift)**

The SOP states: "Hard-fail (abort browser run) if any GATE-DP1 failures are returned." The code (lines 909–916) does NOT abort: it prints a warning and continues to the `with sync_playwright() as pw:` block unconditionally. A GATE-DP1 failure records a FAIL entry in results but does not prevent the browser pass from running.

**Consequence:** The FAIL count inflates (GATE-DP1 FAIL + potential GATE-28 FAILs for the same pair's blank panels), but more critically, the SOP's explicit instruction ("Do not proceed to browser verification while GATE-DP1 failures persist") is violated silently on every run with failures. The browser session wastes time verifying a page whose chart will be visually blank regardless.

**Suggested fix (Phase 4):** Add `if dp1_failures: sys.exit(1)` (or a structured early-return with a clear diagnostic) between the GATE-DP1 block and the `with sync_playwright()` block, matching the SOP's "abort" language.

---

### F-08 | GATE-32 / `CROSS_PERIOD_STUB_IS_FAIL` still `False` — stale across multiple waves
**Section:** GATE-32 (lines 697–714 SOP; line 139 of code)
**Severity: MEDIUM (Stale / Active GATE-32 Violation)**

`CROSS_PERIOD_STUB_IS_FAIL = False` in `cloud_verify.py`. The SOP's own GATE-32 rule says: "The WARN→FAIL flip is a required deliverable for wave closure — it is NOT optional and MUST NOT be deferred indefinitely." Wave 10J was the wave that added ECON-CP1/CP2 / VIZ-CP1. Wave 10I.C confirmed all pairs were running cloud verify. It is now Wave 10K+ (as of 2026-05-08). The SOP anti-patterns section (line 264) repeats: "Never carry a WARN→FAIL stub transition across multiple waves." The flag has not been flipped. The QA-CL1 checklist item (line 292) includes GATE-32 as a mandatory wave-closure action, implying it was not yet satisfied.

**Suggested fix (Phase 4):** Confirm with Lead/Vera/Ace whether all active pairs have been retro-applied for ECON-CP1/CP2. If yes, flip the flag in the code in Phase 4. If not, document the open retro blockers explicitly in OW and add a timeline. Either way, the SOP text should note the current state rather than leaving it as an anonymous "flip to True after Wave 10J retro-apply."

---

### F-09 | QA-CL1 checklist does not list GATE-HZE1, GATE-DP1, or GATE-VIZ-NBER2 as explicit items
**Section:** Standard QA Checklist per Wave (lines 266–297)
**Severity: LOW (Completeness Gap)**

QA-CL4 is a checklist item that contains GATE-27/28/29 and sub-rules. GATE-HZE1, GATE-DP1, and GATE-VIZ-NBER2 are all sub-rules of QA-CL4 / GATE-27 (per their SOP sections), but the QA-CL1 checklist does not name them explicitly. A reader following QA-CL1 mechanically would check "QA-CL4 passes" without necessarily knowing they must also run the three preflight functions for HZE1, DP1, and NBER2.

**Suggested fix (Phase 4):** Either expand the QA-CL4 checklist line to enumerate the sub-gates: "Cloud / deploy verification passes — includes GATE-27 (portal lint + GATE-DP1 preflight + GATE-VIZ-NBER2 preflight + PNG preflight + GATE-HZE1 Story DOM), GATE-28 (all-page DOM error/placeholder/breadcrumb/tab-structure), GATE-29 (parquet clean-checkout)" or add explicit checklist items for each preflight.

---

### F-10 | No glossary for key terms: "smoke", "preflight", "cloud verify", "hibernation", "PASS-with-note"
**Section:** No dedicated definitions section
**Severity: LOW (Completeness Gap)**

The SOP uses "smoke test" (lines 131–146), "preflight" (used for GATE-DP1, GATE-VIZ-NBER2, GATE-29 parquet check), "cloud verify" (HABIT-QA1, QA-CL4), "hibernation" (memories.md and cloud_verify comments only, not in SOP), and "PASS-with-note" (multiple uses) without defining them. The Wave 10J taxonomy note (lines 449–450) partially addresses the smoke vs. portal-lint distinction, but not in a findable glossary location.

**Consequence:** A new Quincy instance (or a cross-reader) must infer these terms. "Preflight" is used inconsistently — GATE-29's parquet check is called a "preflight" but runs within `main()` alongside the browser session. GATE-DP1 and GATE-VIZ-NBER2 are also called "preflights" but run before the browser. The distinction matters for execution ordering and failure disposition.

**Suggested fix (Phase 4):** Add a "Terminology" section near the top of the SOP with 6–8 definitions (smoke, preflight, cloud verify, hibernation, PASS-with-note, perceptual PNG mandate, browser pass).

---

### F-11 | GATE-VIZ-NBER2 "preceding GATE-DP1" integration inconsistency
**Section:** GATE-VIZ-NBER2 integration point (line 693) vs. SOP description ("runs alongside GATE-DP1")
**Severity: LOW (Self-Consistency)**

SOP says GATE-VIZ-NBER2 "runs alongside GATE-DP1." The code runs GATE-DP1 first (lines 898–917), then GATE-VIZ-NBER2 (lines 923–956), then GATE-27-PNG (lines 961–980), then the browser. The ordering is not wrong per se, but the SOP phrase "alongside" implies simultaneous or interchangeable ordering. The actual ordering matters for abort behavior: if GATE-DP1 were to abort on failure (per F-07), GATE-VIZ-NBER2 would never run. The SOP does not address this dependency.

**Suggested fix (Phase 4):** Change "runs alongside GATE-DP1" to "runs after GATE-DP1 preflight and before the browser pass" in the GATE-VIZ-NBER2 section, and add a note that a GATE-DP1 abort (if F-07 is fixed) would prevent GATE-VIZ-NBER2 from running.

---

### F-12 | Cross-reference to ECON-FE1 missing from GATE-ES1 section
**Section:** GATE-ES1 cross-references (lines 350–410)
**Severity: LOW (Cross-Reference Gap)**

GATE-ES1 was promoted from Quincy's draft note after Lead arbitration that produced `ECON-FE1` (the econometrics-side final-exam criteria). The GATE-ES1 section has no "Cross-references" block at all — it defines the eight-step protocol and a finding format, but does not cite:
- `ECON-FE1` (the econometrics-side rule QA is verifying)
- `docs/schemas/evidence_status.schema.json` (schema Quincy validates)
- `docs/schemas/final_exam_results.schema.json` (schema Quincy validates)
- `APP-LP8` (the landing-card status label QA checks in step 7)

Each of these is mentioned inline in the protocol steps but not consolidated in a cross-reference block. The pattern established by QA-CL2 (cross-references block after each rule) is broken here.

**Suggested fix (Phase 4):** Add a Cross-references block to GATE-ES1: ECON-FE1, evidence_status.schema.json, final_exam_results.schema.json, APP-LP8, HABIT-QA1.

---

### F-13 | "perceptual PNG mandate" not defined; VIZ-CV1 cross-reference is in code comment but not in gate body
**Section:** GATE-27 PNG existence check (line 453)
**Severity: LOW (Definitions Gap)**

The GATE-27 PNG check (line 453) names "perceptual PNG mandate" as a concept approved on 2026-04-24, and says "producer-side gate: VIZ-CV1." But VIZ-CV1 is not in the QA SOP Cross-References section (lines 866–881). A reader following the QA SOP cannot verify what VIZ-CV1 requires without opening Vera's SOP. The term "perceptual PNG" is not defined (it refers to a kaleido static-render of each Plotly chart to a PNG file, used to verify visual correctness independently of the browser). The SOP never states this explicitly.

**Suggested fix (Phase 4):** Add VIZ-CV1 to the Cross-References section and add a one-line definition of "perceptual PNG" to the Terminology section (F-10 fix covers this).

---

### F-14 | Post-Wave Lesson Ratification output artifact path is not in QA-CL1 checklist
**Section:** Post-Wave Lesson Ratification (lines 755–788)
**Severity: LOW (Completeness Gap)**

The Lesson Ratification protocol defines `_pws/_team/wave_NNx_lessons_ratified.md` as a wave-closure artifact, explicitly stating "wave cannot close until every `action_required: true` entry... has an Adopted or Dismissed row." However, the QA-CL1 checklist does not include a step for this. A QA agent running QA-CL1 before wave closure would not be prompted to check whether the ratification file exists and is complete.

**Suggested fix (Phase 4):** Add a QA-CL1 checklist item: "[ ] Post-wave lesson ratification — `_pws/_team/wave_NNx_lessons_ratified.md` exists and every `action_required: true` impact-log entry since last ratification has an Adopted or Dismissed row."

---

### F-15 | GATE-27-PNG: variable name `gate27_png_warnings` despite FAIL severity — misleading
**Section:** QA-CL4 / GATE-27-PNG and `cloud_verify.py` lines 962–980
**Severity: LOW (Self-Consistency / Terminology Drift)**

The SOP promotes GATE-27-PNG from WARN to FAIL on 2026-04-24. The code (`main()`) uses the variable name `gate27_png_warnings` and stores results under `"gate27_png_warnings"` in `summary` (line 1101). The variable name (`_warnings`) contradicts the SOP's declared FAIL severity and the FAIL verdict assigned in the results list. This is misleading: a reader scanning the code who sees `gate27_png_warnings` would infer WARN severity, not FAIL. The `summary.txt` output also does not flag PNG failures in the FAIL count (they appear in the separate `gate27_png_warnings` key, not in `summary["fail"]`), creating a potential discrepancy where the FAIL count underreports true failures.

**Suggested fix (Phase 4):** Rename `gate27_png_warnings` to `gate27_png_failures` in `cloud_verify.py` throughout. Verify that PNG failures are included in the `summary["fail"]` count (they ARE added to `results` with `"verdict": "FAIL"`, so the count is correct — but the summary JSON key name is still misleading). Fix the `summary` key name too.

---

## Strengths Worth Preserving

1. **GATE-DP1 and GATE-VIZ-NBER2 are complete, well-specified, and correctly wired into `cloud_verify.py`.** Both have root-cause context, pseudocode (matching actual implementation), severity rationale, and cross-references. The NBER fillcolor heuristic is explicitly documented in both the SOP and the code.

2. **QA-CL2 (KPI triangulation) is an exemplary gate specification.** Three mandatory triangulations with worked examples, a clearly documented strategy-family exception (P2 continuous rebalancing with detection instructions), and cross-references to every related rule. The Wave 4D-1 root-cause story is compelling and makes the "why" unambiguous.

3. **HABIT-QA1 is enforceable and concrete.** The per-page-per-pair requirement is unambiguous: four DOM files, one sentence per file in session-notes, full four-page coverage (no cross-pair sampling). The "what HABIT-QA1 is not" clause prevents misuse. The enforcement mechanism (Lead spot-check of session-notes) is named.

4. **STUB_PATS and APP_SEV1_PATS are well-maintained and separated.** The Wave 10I.C upgrade that split Python-exception patterns (ERR_PATS) from soft-error banners (APP_SEV1_PATS) from stub placeholders (STUB_PATS) is documented in the code header and reflects the evolution history accurately. The "no narrative file found" addition (Wave 10I.A lesson) is present and correctly categorized.

5. **GATE-ES1 protocol is rigorous.** Eight steps, anti-gaming review, blocking conditions (including `qa_status != "qa_passed"` as an explicit FAIL trigger), and a finding template. The conservative fallback is clearly stated.

6. **QA-CL3 (agent memory discipline)** closes a genuine gap and is as auditable as QA-CL2. The first-vs-subsequent-occurrence differentiation (PASS-with-note vs. FAIL) is proportionate.

7. **Post-Wave Lesson Ratification protocol is complete.** Five-step protocol, output format, scope discipline (current wave only), Quincy's bounded role (ensure completion, not adjudicate), and cross-references to team-coordination.md. This is a mature process design.

8. **GATE-29 parquet pre-flight** is correctly integrated with `--skip-gate29` as an escape hatch (explicitly labelled "use only when explicitly approved"), and the root-cause story (smoke_loader.py only checks chart JSON, not signals parquet) is documented both in the SOP and in the code comment.

---

## Items Deferred to Phase 3 Cross-Review

These items touch other agents' SOPs or require Lead arbitration and are listed here for handoff only — Quincy does not own them:

1. **VIZ-DP1 cross-reference** — The SOP dispatch states GATE-DP1's fix owner is Vera. Vera's SOP should carry a VIZ-DP1 rule mandating `xaxis="x2"` on all bottom-panel traces of dual-panel zoom charts. Whether VIZ-DP1 exists and matches GATE-DP1's assertion is a Phase 3 concern (Vera's SOP review).

2. **RES-OD1 cross-reference** — GATE-NR (F-03) cites `RES-NR1` as the producer-side companion. Phase 3 should verify RES-NR1 exists in Ray's SOP and matches GATE-NR's instrument-scope definition.

3. **ACE-HZE1 vs. GATE-HZE1 ownership ambiguity** — The status board (2026-04-24 Ace entry) created `ACE-HZE1` in Ace's SOP: Ace must wire `HISTORY_ZOOM_EPISODES` into every pair config. GATE-HZE1 in Quincy's SOP says Ace is the fix owner when heading is absent and charts are committed. The two rules should be cross-referenced in both SOPs — Phase 3 cross-review should confirm Ace's SOP carries the ACE-HZE1 rule and that it explicitly links GATE-HZE1 as the QA verification counterpart.

4. **ECON-FE1 consistency** — GATE-ES1 step 5 ("compare expected versus observed headline metrics: confirmation Sharpe, excess return, delta Sharpe, drawdown, bootstrap uncertainty, and multiple-testing adjustment") should match exactly what ECON-FE1 defines as confirmation criteria. Phase 3 cross-review should compare the two.

5. **APP-LP8 cross-reference consistency** — GATE-ES1 step 7 cites APP-LP8 (landing-card status label). APP-LP8 is in Ace's SOP. Phase 3 should confirm the label strings and logic in APP-LP8 match what GATE-ES1 step 7 verifies.

---

*End of Phase 1 findings. No edits made to SOP, `cloud_verify.py`, or any other agent's files. Fixes deferred to Phase 4.*
