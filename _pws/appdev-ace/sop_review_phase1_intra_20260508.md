# Phase 1 Intra-SOP Review — AppDev Ace SOP
**Agent:** AppDev Ace  
**Date:** 2026-05-08  
**Task:** LEAD-DL1-scoped intra-SOP review only. No edits to the SOP in this phase.  
**SOP reviewed:** `docs/agent-sops/appdev-agent-sop.md`  
**Standards reference:** `docs/standards.md` (APP section)  
**Scope:** Completeness, self-consistency, definitions, coverage gaps, cross-references, severity, stale items.

---

## Findings

### F-01 — Standards Registration Gap: 8 APP rules unregistered  
**Rule(s):** APP-PT1, APP-PT2, APP-TL1, APP-PR1, APP-RL1, APP-SS1, ACE-HZE1, GATE-CL6/7/8 (and by extension GATE-CL1-5 partially — only changelog/SOP, not a standards.md table row)  
**Section:** `docs/standards.md` APP table  
**Problem:** `standards.md` is the declared canonical rule index ("source of truth for rule identity and inventory"). The APP section registers 28 rules. But 8 substantive binding rules added after Wave 5B-2 (APP-PT1, APP-PT2, APP-TL1, APP-PR1, APP-RL1, APP-SS1, ACE-HZE1) and at least 3 new GATE-CL items (CL6, CL7, CL8) are absent from `standards.md`. Anyone reading the index to understand AppDev's rule surface sees an incomplete picture. The changelog and the SOP body are the only record.  
**Severity proposal:** WARN (blocking for traceability, non-blocking for portal operation)  
**Suggested fix:** In Phase 4, add one row per missing rule to `docs/standards.md` APP table, matching the format of existing rows. ACE-HZE1 should be added under the APP prefix (it is authored by Ace, references APP-SEV1/APP-PT1, and lives in the AppDev SOP).

---

### F-02 — "Thin Wrapper" Not Defined  
**Rule(s):** APP-PT1  
**Section:** Rule APP-PT1 body (§ "Thin-wrapper contract")  
**Problem:** The SOP uses "thin wrapper" throughout as the key APP-PT1 concept but never provides a named definition block. The operative definition is embedded mid-rule: "a page file MAY contain only (a) the sys.path shim, (b) the import, and (c) a single call to the template function." This is functionally adequate but not surfaced as a term definition. The Quality Gates checklist gate ("New pair pages use page_templates.py, not hand-written pages") references the concept without a definition pointer. A new AppDev agent reading only the Quality Gates section has no term anchor.  
**Severity proposal:** WARN  
**Suggested fix:** Add a definitions subsection near the top of Rule APP-PT1 (or a standalone "Definitions" section near the top of the SOP) that explicitly defines "thin wrapper." The current prose is the definition — it just needs to be labeled as such.

---

### F-03 — "Page Template" Not Defined  
**Rule(s):** APP-PT1, Quality Gates checklist  
**Section:** §Design Portal Architecture (multi-pair section), Rule APP-PT1  
**Problem:** "Page template" and "pair config" are used interchangeably with the file paths (`page_templates.py`, `pair_configs/{pair_id}_config.py`) but no formal definition block distinguishes "template" (structural, shared) from "pair config" (content, pair-specific). The architecture section (lines ~84–112) describes a different config structure (`config/pairs/` JSON files) that is a legacy concept superseded by the Python `pair_configs/` package. The two coexist in the SOP without an explicit deprecation note.  
**Severity proposal:** WARN  
**Suggested fix:** Add a note in the architecture section explicitly marking the `config/pairs/*.json` schema (lines 114–134) as a "legacy reference schema — superseded by the Python pair_config module described in Rule APP-PT1." Add a definition for "pair config module."

---

### F-04 — "Evidence-Status Badge" Not Defined  
**Rule(s):** APP-LP8  
**Section:** Landing Page Design Rules §8  
**Problem:** APP-LP8 specifies an "evidence-status label" (and the Quality Gates checklist calls it a "label/badge" interchangeably in different places) and defines three canonical status values. But neither the SOP nor standards.md defines what the "badge" or "label" UI element looks like: is it an `st.badge()`, a markdown pill, an `st.caption()`, a chip? The SOP says "show an evidence-status label" without specifying component. The implementation file (`app/components/evidence_status.py`) likely has the answer, but the SOP should be self-contained. Cross-reference: APP-LP4/5 specifies badge rendering (markdown pills with CSS), but APP-LP8 adds no similar rendering spec.  
**Severity proposal:** WARN  
**Suggested fix:** Add a one-paragraph rendering spec to APP-LP8 matching the detail level of APP-LP4/5, including which Streamlit component implements the badge.

---

### F-05 — "L1/L2 Banner" Not Named as a Term  
**Rule(s):** APP-SEV1, GATE-CL1  
**Section:** Rule APP-SEV1 body, GATE-CL1 quality-gate checklist item  
**Problem:** GATE-CL1 says "no raw L1/L2 diagnostic banners on production pages" — yet APP-SEV1 defines severity levels as "L1 (Loud-Error)", "L2 (Loud-Warning)", "L3 (Caption-Note)" without calling them "banners." The term "banner" is used only in GATE-CL1 without a definition. A reader who encounters GATE-CL1 first and searches for "banner" in the SOP will find nothing. The severity levels are well-defined, but the "banner" alias is unregistered.  
**Severity proposal:** INFO (minor, but definition gap)  
**Suggested fix:** Either: (a) add "Also called: L1/L2 banners in GATE-CL1 usage" to APP-SEV1's opening paragraph, or (b) change "banners" to "L1/L2 severity callouts" in GATE-CL1 for consistency with APP-SEV1 terminology.

---

### F-06 — "_REPO_ROOT anchor" Not Formally Defined as a Term  
**Rule(s):** APP-PR1  
**Section:** Rule APP-PR1 body  
**Problem:** APP-PR1 uses "_REPO_ROOT anchor" and "_REPO_ROOT-anchored pathlib.Path object" as a term throughout but never declares it in a definitions block. The concept is clear from context (the `_REPO_ROOT = Path(__file__).resolve().parents[N]` pattern), but it appears as both a code pattern and a conceptual rule anchor without explicit labeling.  
**Severity proposal:** INFO  
**Suggested fix:** Add a one-line "Definition: `_REPO_ROOT` anchor" callout at the start of APP-PR1 before the binding paragraph.

---

### F-07 — APP-LP8 Cross-References to ECON-FE1/GATE-ES1 Are Missing  
**Rule(s):** APP-LP8  
**Section:** Landing Page Design Rules §8  
**Problem:** APP-LP8 defines three evidence-status values (`found_in_search`, `needs_final_exam`, `passed_final_exam`) and their landing-card display. ECON-FE1 (added 2026-05-01) defines the conditions under which `passed_final_exam` is assigned by Evan. GATE-ES1 (added 2026-05-01) defines Quincy's independent verification of any status promotion. APP-LP8 has no cross-reference to either. An AppDev reading APP-LP8 to understand the status values will not know where the upstream gate lives. If Evan or Quincy change the conditions, Ace has no pointer to stay in sync.  
**Severity proposal:** WARN  
**Suggested fix:** Add "Cross-references: ECON-FE1 (producer-side status assignment conditions), GATE-ES1 (QA verification of status promotions), `docs/schemas/evidence_status.schema.json`" to the APP-LP8 rule text.

---

### F-08 — ACE-HZE1 Cross-Reference to RES-HZE1 — Rule May Not Exist Under That ID  
**Rule(s):** ACE-HZE1  
**Section:** Rule ACE-HZE1 Cross-references  
**Problem:** ACE-HZE1 cites "RES-HZE1 (Ray episode narrative rule)" in its cross-references and in the blocker-filing language. However, the Research SOP and `standards.md` RES table do not contain "RES-HZE1" as a registered rule. The Research SOP has rules RES-8, RES-20 (Historical-Episode Selection Criterion), and VIZ-ZOOM1, VIZ-HZE1. The sop-changelog Wave 10J entry calls it "RES-HZE1" but this name is not confirmed in the Research SOP text or standards.md RES table. If the rule is named differently (or is actually just RES-8/RES-20), the blocker-filing template in ACE-HZE1 step 4 points to a phantom ID.  
**Severity proposal:** FAIL (broken cross-reference — blockers may be silently misfiled)  
**Suggested fix:** Verify the correct rule ID in the Research SOP (likely RES-20 or a dedicated `RES-HZE1` that needs to be registered). Update ACE-HZE1 cross-reference and blocker-filing language with the confirmed ID.

---

### F-09 — ACE-HZE1 Cross-Reference to VIZ-HZE1 — Confirm Rule ID  
**Rule(s):** ACE-HZE1  
**Section:** Rule ACE-HZE1 Cross-references  
**Problem:** ACE-HZE1 cites "VIZ-HZE1" (Historical Zoom Enumeration Gate). The Visualization SOP cross-reference footer in ACE-HZE1 says "VIZ-ZOOM1 (Vera zoom chart generation rule), RES-HZE1..." but the standards.md VIZ table confirms VIZ-HZE1 does exist. The ACE-HZE1 rule body at step 3 says "See VIZ-ZOOM1" (not VIZ-HZE1). The naming is internally inconsistent — within ACE-HZE1, VIZ-ZOOM1 and VIZ-HZE1 appear in different places to describe possibly different things (generation vs enumeration gate). Standards.md distinguishes them correctly (VIZ-ZOOM1 = production rule, VIZ-HZE1 = enumeration gate), but ACE-HZE1 blurs this distinction.  
**Severity proposal:** WARN  
**Suggested fix:** In ACE-HZE1 step 3, replace "See VIZ-ZOOM1" with "file a VIZ-HZE1 enumeration-gate blocker via VIZ-ZOOM1" or clarify that VIZ-ZOOM1 is the production rule and VIZ-HZE1 is the gate. Align cross-reference footer to name both correctly.

---

### F-10 — APP-PR1 "Cloud Verify" Integration Point Not Stated  
**Rule(s):** APP-PR1  
**Section:** Rule APP-PR1 — Detection/enforcement  
**Problem:** APP-PR1 says "_REPO_ROOT" usage is "grep-checkable CI (future)" but gives no integration point with `scripts/cloud_verify.py`. The Quality Gates checklist also does not mention APP-PR1 compliance. Cloud verify (Quincy-owned) exercises path resolution implicitly by loading pages, but there is no explicit APP-PR1 gate in the QA flow. If APP-PR1 compliance is assumed from GATE-29 (clean-checkout smoke), this should be stated. Currently the rule says the greps are for "future CI" — but there is no integration point declared for the present.  
**Severity proposal:** WARN  
**Suggested fix:** Add an integration point note to APP-PR1: "Current enforcement: Ace runs the three greps manually before each pair-config commit and at the start of any APP-PT1 migration wave. GATE-29 (Quincy) catches cloud-side path failures as a second line of defense. Future: CI lint."

---

### F-11 — APP-PT1 Migration Protocol Lists Pairs Already Migrated  
**Rule(s):** APP-PT1  
**Section:** Rule APP-PT1 — Migration protocol  
**Problem:** The migration-protocol bullet says: "pre-existing pair pages (HY-IG v2, umcsent_xlv, indpro_spy, permit_spy, vix_vix3m_spy, ted_variants, hy_ig_spy legacy) are NOT required to migrate retroactively in the same wave that introduces APP-PT1." However, per session-notes, indpro_spy, permit_spy, vix_vix3m_spy (Wave 10I.A Part 1), ted_variants (Wave 10I.A Part 2), and hy_ig_spy (Wave 10G.4E) have all been migrated. The migration list is stale — it still names pairs that are now thin wrappers as if they are pending.  
**Severity proposal:** WARN (creates false outstanding-work impression)  
**Suggested fix:** In Phase 4, update the migration protocol to strike completed migrations and note only the remaining candidates: HY-IG v2 (reference pair, last), umcsent_xlv Strategy page (BL-APP-PT1-UMCSENT).

---

### F-12 — GATE-CL1 Is a 500+ Word Omnibus Gate — No Severity for Sub-Items  
**Rule(s):** GATE-CL1  
**Section:** Quality Gates checklist  
**Problem:** GATE-CL1 is an enormous checklist item containing at minimum 5 distinct sub-checks: (a) N/A KPI slots, (b) internal stub text visible, (c) navigation count, (d) L1/L2 banners on production pages, (e) NBER shading integration-time JSON shape check. Each sub-check has different failure consequences but no per-sub-item severity. The NBER shape check alone is a 200-word specification embedded in a quality gate bullet. GATE-CL1 should be a named rule with severity, not a quality-gate checkbox.  
**Severity proposal:** WARN (organization debt; hard to audit compliance)  
**Suggested fix:** Promote GATE-CL1 to a named rule (e.g., APP-CL1) with sub-items labeled (a)–(e), each with individual severity. Or split into separate GATE-CL1a through GATE-CL1e checklist items. The NBER shape check should be its own rule or at minimum a cross-referenced named procedure.

---

### F-13 — GATE-CL7 Has No Integration Point or Implementation Path  
**Rule(s):** GATE-CL7  
**Section:** Quality Gates checklist  
**Problem:** GATE-CL7 requires asserting that default Strategy chart slots (`equity_curves`, `equity_drawdown`, signal/position charts) "return non-empty Plotly figures and do not display 'chart pending' placeholders." The aspirational note below GATE-CL8 says `gate_cl_audit.py` (Wave 10K Phase 1) will automate GATE-CL1 through CL8. But GATE-CL7 is not covered by APP-ST1 (portal lint) either — APP-ST1 checks all charts named in `load_plotly_chart` calls, but default-slot charts may not appear as literal chart names if the slot is resolved dynamically. This gap is only partially covered.  
**Severity proposal:** WARN  
**Suggested fix:** Document that GATE-CL7's default-slot assertion is covered by APP-ST1's "Strategy pages must also lint the default chart registry" sub-rule (§Rule APP-ST1, paragraph 2). Add explicit cross-reference: "GATE-CL7 is partially enforced by APP-ST1; full enforcement pending `gate_cl_audit.py` Wave 10K Phase 1."

---

### F-14 — APP-TL1 Ownership Split Records Ambiguous Shared Ownership  
**Rule(s):** APP-TL1  
**Section:** Rule APP-TL1 — Ownership split table  
**Problem:** APP-TL1 ownership table row for "Narrative canonical defaults (steps 2, 3, 4)" says owner = Ray with the note "Constants currently in `app/components/page_templates.py`; Lead must record this narrow shared ownership or assign a Ray-owned content artifact." This is an open action item inside a rule body — the rule acknowledges its own ownership is unresolved and defers to Lead. The sop-changelog 2026-05-08 entry records that Lead acknowledged this in the LEAD-DL1 ownership map update. However, the SOP rule body still says "Lead MUST record... or assign" as future action, creating the impression the resolution is pending when it may already be done.  
**Severity proposal:** WARN  
**Suggested fix:** Update the APP-TL1 ownership note to record the actual resolution from the 2026-05-08 LEAD-DL1 update (narrow shared ownership recorded). Remove the forward-looking "Lead must..." phrasing.

---

### F-15 — winner_summary Schema Drift Failure Mode Not Gated  
**Rule(s):** APP-WS1, GATE-CL gates generally  
**Section:** Rule APP-WS1 body; Quality Gates  
**Problem:** APP-WS1 requires schema validation of `winner_summary.json` via `validate_or_die`. The session-notes (Wave 10I.A Fix session) document exactly how schema drift caused 10 errors in 6 legacy pairs — fields `direction` (enum typo `pro_cyclical` vs `procyclical`), `strategy_family` (legacy `strategy_code` vs schema field name), 8 missing required fields. APP-WS1 gates the consumer side (Ace) but the SOP has no rule about what Ace should do when a legacy pair's `winner_summary.json` fails schema validation: the component short-circuits (correct per APP-SEV1 L1), but there is no rule mandating that Ace file an Evan backlog item or blocker. The drift propagates silently until a backlog-aware human notices.  
**Severity proposal:** WARN  
**Suggested fix:** Add to APP-WS1 a "Schema violation escalation" clause: when `validate_or_die` fails on a delivered (non-WIP) pair's `winner_summary.json`, Ace MUST file a blocker in `_pws/_team/status-board.md` identifying the pair and the specific validation errors, and MUST NOT mark the pair's Strategy page as delivered-green. This closes the "observe-but-don't-escalate" gap.

---

### F-16 — Hand-Written Legacy Bypass Is Not Explicitly Gated Beyond Migration Protocol  
**Rule(s):** APP-PT1, APP-PT2  
**Section:** Rule APP-PT1 migration protocol; Rule APP-PT2  
**Problem:** APP-PT1 explicitly says legacy pages "are NOT required to migrate retroactively in the same wave." APP-PT2 notes that "5 legacy Methodology pages that bypass the template... must have the helper called directly from the page file until migration." But neither rule establishes a positive gate that checks whether hand-written legacy pages are compliant with ALL accumulated template rules (APP-TL1, APP-PT2, GATE-CL gates). Session-notes Wave 10H.1 follow-up shows this gap concretely: Wave 10H.1 wired `_render_exploratory_insights` into the template, but `9_hy_ig_v2_spy_methodology.py` bypassed the template and did not get the feature — caught only because Quincy cloud-verified and found the gap.  
**Severity proposal:** FAIL (active gap class — recurs every time a new template feature ships)  
**Suggested fix:** Add a rule (or expand APP-PT1 migration protocol) requiring: whenever a new feature is added to `page_templates.py`, Ace MUST run `grep -L "render_methodology_page\|render_story_page\|render_evidence_page\|render_strategy_page" app/pages/` to enumerate bypass pages and either (a) add a defensive direct call to each bypass page in the same commit, or (b) file a blocker before closing the wave. The lesson is in session-notes; it needs to be in the SOP.

---

### F-17 — Hibernation / Cache-Clear Reboot Not Gated  
**Rule(s):** None (coverage gap)  
**Section:** Quality Gates; Standard Workflow §6 Deploy  
**Problem:** Streamlit Cloud can serve a stale deploy (cached container) after a commit-push, particularly after it has hibernated. Session-notes Wave 10I.A Fix documents exactly this: `ccb0d5f` was committed, 35/41 FAIL remained on reverify, root cause was stale Cloud cache. Resolved only by Lead-forced manual reboot. The SOP has no rule about what Ace should do when cloud-verify shows unexpected failures that don't match HEAD code (vs. Pattern 24 which instructs Quincy, not Ace). Ace has no guidance on when to suspect cloud-cache vs. a real code bug.  
**Severity proposal:** WARN  
**Suggested fix:** Add a rule or anti-pattern note in §6 Deploy: "After a commit-push, allow 2-3 minutes before cloud-verifying. If cloud-verify results are inconsistent with code at HEAD (e.g., traceback line number points to a comment or deleted code), request a Streamlit Cloud manual reboot before filing a bug. See Pattern 24 (Quincy SOP) for the QA companion rule."

---

### F-18 — Smoke vs Cloud Gap: APP-ST1 "Portal Lint" Scope Not Fully Stated  
**Rule(s):** APP-ST1  
**Section:** Rule APP-ST1 body; terminology note  
**Problem:** APP-ST1 explicitly renames itself "portal lint" (not "smoke test") and says smoke test is Quincy's domain. This is correct. However, APP-ST1's "before Ace finishes a page" requirement and Quincy's cloud verify are presented as independent complementary checks, but the specific gaps are not enumerated. Session-notes Wave 10I.A Fix (root-cause: `validate_or_die` runs at render-time in Streamlit, not at AST import time) shows APP-ST1 portal lint cannot catch render-path schema failures — the lint exercises imports and `load_plotly_chart`, not the full Streamlit render chain. APP-ST1's scope limitation is not stated.  
**Severity proposal:** WARN  
**Suggested fix:** Add a "Scope limitation" note to APP-ST1: "Portal lint (APP-ST1) verifies chart artifact loading and import correctness. It does NOT exercise the Streamlit render chain — schema validation (`validate_or_die`) and component-level data reads run at render time, not at AST import time. Cloud verify (Quincy, GATE-31) is the only gate that catches render-path failures. Portal lint PASS does not imply cloud-verify PASS."

---

### F-19 — APP-DIR1 "Ray Leg" Integration Point Is Conditional but the Condition Is Ambiguous  
**Rule(s):** APP-DIR1  
**Section:** Rule APP-DIR1 body  
**Problem:** APP-DIR1 says "Ray narrative frontmatter `direction_asserted` when present in the pair's registered narrative artifact." The condition "when present" is ambiguous — it is unclear whether "present" means (a) the narrative frontmatter file exists for the pair, (b) the specific field `direction_asserted` exists in the file, or (c) the pair is registered in the narrative frontmatter schema. The GATE-CL1 update (2026-05-01) adds important clarification — "if Ray frontmatter exists, the log and UI must report the Ray leg as included" — but this is in GATE-CL1, not APP-DIR1 where the rule lives. APP-DIR1 has no pointer back to GATE-CL1's clarification.  
**Severity proposal:** WARN  
**Suggested fix:** In APP-DIR1 "Ray leg handling" paragraph, add a cross-reference to GATE-CL1 and explicitly define "Ray leg present" as: "the narrative frontmatter file for the pair exists on disk AND the `direction_asserted` field is populated."

---

### F-20 — "Trigger Card" Not Defined; APP-SE3 and APP-SEV1 Severity Mismatch for Cards  
**Rule(s):** APP-SE3 (Instructional Trigger Cards)  
**Section:** §3.6 Rule A3  
**Problem:** (a) "Trigger card" / "instructional trigger card" is a visual concept used throughout but never defined with a term definition. The SOP describes them ("compact card grid, 2-4 cards, each = one trigger scenario") but does not define the term itself. (b) APP-SE3 does not specify APP-SEV1 severity for the case where `winner_summary.json` is missing or where `threshold_value` is null (the Wave 10I.A defect). APP-WS1 gates the load, but the trigger-cards-specific failure path is not documented. The `threshold_value` null defect was patched defensively (Wave 10I.A Fix) but the SOP does not acknowledge this case.  
**Severity proposal:** WARN  
**Suggested fix:** (a) Add "trigger card" to the definitions section as "a compact scenario card (implemented with `st.container(border=True)`) that illustrates one signal-to-action scenario (BUY, REDUCE, or HOLD) using a mini-chart snippet and plain-English rule." (b) In APP-SE3, add: "If `threshold_value` is null or unparseable after APP-WS1 load, fall back to the default threshold (0.5) and emit APP-SEV1 L3 caption. Do not raise TypeError silently." This documents the Wave 10I.A Fix as a SOP-level contract.

---

## Strengths Worth Preserving

1. **APP-SEV1 three-level severity policy is well-designed.** L1/L2/L3 coverage is consistent across all downstream rule bodies. The "diagnostic hygiene" clause (no schema names, paths, SOP IDs, agent names in user-visible copy) is specific and actionable.

2. **APP-PT1 with narrative authorship supplement is a complete rule.** The thin-wrapper contract, pair-config contract, template-locking clause, dated-file globbing, migration protocol, and narrative authorship supplement cover all major failure classes from prior waves. The rule is longer than ideal but the detail is earned.

3. **ACE-HZE1 4-step pre-ship checklist is a model gate.** It requires a positive audit (read Ray handoff, run `ls` on disk, cross-check against episode registry, file blockers if absent) rather than a passive absence-check. Other rules should adopt this pattern.

4. **APP-WS1 explicit retirement of fallback code** (`_SIGNAL_CODE_TO_COLUMN`) is a best-practice pattern. Rules that retire specific anti-patterns with named code evidence are much stronger than rules that merely prohibit a class of behavior.

5. **GATE-CL1 content-level audit requirement** (Structural PASS + Content FAIL = FAIL) was a genuine insight from Wave 10I.C. The explicit stub-text pattern list ("Ray leg:", "RES-17", "SOP", "ticket") is actionable.

6. **APP-PR1 grep-checkable enforcement patterns** (three specific `grep` commands) make the rule self-auditing. This is a useful pattern for future rules.

7. **APP-TL1 ownership table** is clear about which owner is responsible for each layer (Ace: structure; Ray: narrative; Evan: CSV production; Dana: schema; Quincy: QA).

---

## Items Deferred to Phase 3 Cross-Review

1. **APP-LP8 ↔ Strategy page Tournament Winner section.** APP-LP8 requires the status label on landing cards AND "Strategy pages MUST repeat the status near the Tournament Winner section." The Strategy-page mandate belongs to APP-TL1 or a dedicated APP-SE rule — cross-pollinating it inside a Landing Page rule creates cross-page split ownership. Phase 3 should check whether Ray, Evan, or Quincy SOPs reference this requirement from their own perspective.

2. **APP-DIR1 ↔ RES-OD1 / ECON-DIR1 handoff coherence.** The sop-changelog 2026-04-23 Wave 10I.C adds ECON-DIR1 (Evan reconciles direction before handoff) and RES-OD1 (Ray asserts direction). APP-DIR1 is the consumer-side check. Phase 3 should verify the three rules form a closed loop: Evan confirms, Ray asserts, Ace verifies.

3. **APP-PT1 / APP-PT2 bypass rule (F-16 above) — cross-agent scope.** The "grep pages/ for bypass" enforcement proposed in F-16 requires Ace to run a cross-pair audit at every template-feature addition wave. This should be registered in the team-coordination.md as a LEAD-assigned responsibility, not purely Ace's discovery task.

4. **APP-TL1 Ray narrative constants in `page_templates.py` — shared file ownership.** Per F-14, the 2026-05-08 changelog records Lead's acknowledgment in the LEAD-DL1 map. Phase 3 should verify the lead-agent-sop.md ownership map explicitly lists this sharing arrangement.

5. **GATE-CL (1–8) not in standards.md.** The entire GATE-CL family is registered only in the AppDev SOP and changelog, not in standards.md GATE table. Phase 3 (cross-review with Quincy) should determine whether GATE-CL items belong in the GATE section (Lead-owned) or the APP section (Ace-owned) of standards.md.

6. **APP-ST1 "portal lint" vs cloud-verify gap (F-18) — Quincy's GATE-31 complement.** Phase 3 should verify Quincy's SOP explicitly states that cloud verify catches render-path failures that portal lint misses, and that the two gates are described as complementary (not redundant) in both SOPs.

---

*Findings count: 20 findings (1 FAIL, 10 WARN, 3 INFO, 6 deferred to Phase 3)*  
*Findings file: `/workspaces/aig-rlic-plus/_pws/appdev-ace/sop_review_phase1_intra_20260508.md`*
