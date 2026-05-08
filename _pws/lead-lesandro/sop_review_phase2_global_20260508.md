# SOP Review — Phase 2 Lead Protocol/Global Review

**Author:** Lead Lesandro
**Date:** 2026-05-08
**Branch:** 260430
**Scope:** Protocol-level inconsistencies, work-chain breaks, and Lead-owned arbitrations that no single role agent can resolve from inside their own SOP.
**Inputs:** Phase 1 findings from Dana, Evan, Vera, Ray, Ace, Quincy (~90 findings total).
**LEAD-DL1 self-check:** This file is the only artifact written in this phase. No role-owned files touched.

---

## A. Cross-Cutting Protocol Findings

### A1. Standards Registry Is Substantially Incomplete (FAIL — Lead-owned)

Every role agent independently flagged unregistered rules in `docs/standards.md`. Aggregate count of rules referenced in role SOPs but missing from `docs/standards.md`:

| Owner | Unregistered rules |
|-------|-------------------|
| Dana  | DATA-D6b, GATE-NR (cross-ref target) |
| Evan  | ECON-T4, ECON-INF1, ECON-DIR2, ECON-OOS3, Rule C2a (ECON-C2a) |
| Vera  | VIZ-IC1, GATE-VIZ-NBER1, GATE-VIZ-NBER2, GATE-VIZ-ZOOM1, GATE-HZE1 (gates owned by QA but VIZ rules cite them) |
| Ray   | RES-NR1, RES-EGL1, RES-OD1/OD1a/OD1b/OD1c, RES-CPC1, RES-CP1, RES-CP2, RES-HZE1, RES-ZOOM1 |
| Ace   | APP-PT1, APP-PT2, APP-TL1, APP-PR1, APP-RL1, APP-SS1, ACE-HZE1, GATE-CL6, GATE-CL7, GATE-CL8 |
| Quincy| GATE-DP1, GATE-HZE1, GATE-ES1 (and any others authored 2026-04-22 onward) |

**Root cause:** rule promotions in waves 5B-2 → 10K added rule text to SOPs but did not consistently update `docs/standards.md`. The registry is meant to be the canonical inventory; right now it is ~40% out-of-date for new rules.

**Resolution path (Phase 4):** Lead writes a single batch update to `docs/standards.md` adding all unregistered rules in one commit. Each agent's Phase 4 fix prompt must include a Lead-supplied row template so the SOP edit and the standards.md edit stay in lock-step.

### A2. Episode Slug Fragmentation Is a Work-Chain Break (FAIL — Lead arbitration required)

Two parallel episode registries exist on disk:

| File | Used by | Slugs |
|------|---------|-------|
| `docs/schemas/episode_registry.json` | Ray (RES-HZE1, RES-ZOOM1), Evan (ECON-CP1) | `dot_com`, `rates_2022` |
| `docs/schemas/history_zoom_events_registry.json` | Vera (VIZ-V12, VIZ-ZOOM1, VIZ-HZE1), QA (GATE-VIZ-NBER2) | `dotcom`, `inflation_2022`, `taper_2018` |

On-disk artifacts (chart files, `_perceptual_check_*.png`) use the **Vera namespace** (`dotcom`, `inflation_2022`). That makes Vera's namespace the de-facto authority by virtue of being the namespace the consumer (chart loader) uses.

A Ray narrative authored against `dot_com` cannot match a Vera chart written as `history_zoom_dotcom.json`. Ace's `HISTORY_ZOOM_EPISODES` consumes whichever slug Ray authors, and the template renders the section even though no chart matches → silent rendering failure.

**Lead arbitration:**

1. **`history_zoom_events_registry.json` is canonical** going forward. Vera owns it (per VIZ-V12).
2. **`episode_registry.json` is deprecated.** Either retire entirely or convert to a thin pointer to the canonical registry.
3. **Single canonical slug set:** `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`. Variants `dot_com`, `rates_2022`, `taper_2013` are non-canonical and forbidden.
4. **Ray's RES-HZE1 / RES-ZOOM1 must read from the canonical registry.**
5. **Quincy's GATE-VIZ-NBER2 hardcoded slug set must be updated** (`dot_com` → `dotcom`).
6. **Evan's ECON-CP1 episode_registry.json reference must be retargeted.**

This arbitration is binding for Phase 4. Ray, Vera, Evan, and Quincy each need a coordinated edit.

### A3. Config-Attribute Naming Conflict for Zoom Episodes (FAIL — Lead arbitration required)

Independently of the slug issue, two config-attribute names exist:

- **Ray's RES-ZOOM1:** `ZOOM_EPISODE_NARRATIVES` (dict, slug→narrative)
- **Ray's RES-HZE1 + Ace's ACE-HZE1:** `HISTORY_ZOOM_EPISODES` (list[dict], slug/title/narrative/caption)

Ace's template only consumes `HISTORY_ZOOM_EPISODES`. A Ray author following RES-ZOOM1 alone produces a silently-ignored structure.

**Lead arbitration:** `HISTORY_ZOOM_EPISODES` is canonical (already consumed by template; richer schema). RES-ZOOM1 must be updated to specify the same name and structure as RES-HZE1 (or RES-ZOOM1's delivery-format section becomes "see RES-HZE1," with content focus only).

### A4. `observed_direction` Three-Way Ownership Ambiguity (FAIL — Lead arbitration required)

| Source | Says |
|--------|------|
| Evan SOP (ECON-DIR1, schema `owner_writes`) | Evan owns `observed_direction` |
| Dana SOP | silent — not mentioned |
| `docs/standards.md` APP-DIR1 row | "Dana — validated via DATA-D6" |

Three different positions on one field. Evan's SOP says he writes it; standards.md says Dana writes it; Dana's SOP says nothing.

**Lead arbitration (binding):** Evan owns `observed_direction` post-tournament (he has the winning direction by then; Dana does not). Dana leaves it absent at data-stage handoff. The APP-DIR1 row in `docs/standards.md` is wrong and must be corrected to attribute `observed_direction` to Evan. Dana's SOP gets an explicit "do not write" note in DATA-D6 procedure step 1.

### A5. SOP↔Code Drift on `scripts/cloud_verify.py` (FAIL — Quincy + Lead)

Quincy reported four gates declared in SOP without corresponding code:
1. **GATE-HZE1** — pseudocode in SOP, not in script.
2. **Evidence Level 1/Level 2 tab structure check** — listed in SOP §4 item 6, not in script.
3. **GATE-NR** — listed in QA-CL1 mandatory checklist, not in script.
4. **GATE-DP1 abort behavior** — SOP says "abort browser run on failure"; code logs and continues.

Plus stale flags `CROSS_PERIOD_STUB_IS_FAIL = False` (GATE-32 anti-pattern: "do not carry WARN→FAIL transitions across waves") and the misleading variable name `gate27_png_warnings` despite FAIL severity.

**Resolution:** Quincy's Phase 4 owns code edits. Lead does not touch `cloud_verify.py`. Each item gets a single line in Quincy's fix-list with an explicit owner-action statement.

### A6. Cross-Reference Cascade Failures (FAIL — multi-agent)

Several rules cite phantom or wrong-target rule IDs:

| Source rule | Cites | Issue |
|-------------|-------|-------|
| ACE-HZE1 (Ace) | RES-HZE1 | Ace claimed phantom; Ray confirms it exists at his SOP §RES-HZE1. Real cause: Ace couldn't locate it in `docs/standards.md` (A1 issue). Once A1 closes, this auto-resolves. |
| VIZ-IC1 (Vera) | META-RYW, QA-CL6, GATE-NC | All three are phantom — never defined anywhere. |
| RES-20 (Ray) | `output/charts/chart_type_registry.json` | Wrong path; should be `docs/schemas/episode_registry.json` (or canonical registry per A2). |
| ECON-H5 (Evan) | "winner_summary.schema.json v1.0.0" | Stale; live schema is v1.1.0. |
| Vera Color Palette table | matplotlib-default hex | Direct contradiction with VIZ-V11 lint. |

**Resolution:** each agent fixes their own cross-references in Phase 4. Lead arbitrates which alias survives where the cited rule has been renamed (most cases: drop the phantom alias entirely).

---

## B. Work-Chain / Handoff Integrity

### B1. Episode-narrative work-chain (Ray → Vera → Ace → Quincy) is broken at three points

1. **Slug namespace** (A2): Ray's slug ≠ chart filename slug.
2. **Config attribute** (A3): Ray writes one name; Ace reads another.
3. **Skip protocol overlap**: VIZ-HZE1 has a structured skip protocol; Ace's APP-EP4/GATE-25 has a placeholder protocol; the two cover different causes (data-coverage gap vs chart-not-built) but the SOPs do not jointly clarify which fires when. (Vera P3 #3, Ray P3 #6.)

After A2 and A3 resolve, the Phase 4 dispatches must include explicit handoff verification: Ray writes → Vera generates with matching slug → Ace consumes the right attribute → Quincy GATE-HZE1 confirms presence.

### B2. Direction work-chain (Evan → Ray → Ace → Quincy)

The four-rule chain — ECON-DIR1 (Evan reconciles), RES-OD1 (Ray asserts), APP-DIR1 (Ace verifies), GATE-NR (Quincy DOM scan) — is internally consistent except for:

1. The `observed_direction` ownership conflict (A4) at the head of the chain.
2. RES-OD1 Quality-Gate checklist entry uses the pre-Wave-10J script (Ray F-07: silent-weakening of a tightened blocking rule).
3. Quincy's GATE-NR has no code implementation (A5 #3).

Phase 4 must close all three for the chain to be operational.

### B3. Final-exam evidence-status work-chain (Evan → Quincy → Ace)

ECON-FE1 + GATE-ES1 + APP-LP8 form a clean three-step gate but cross-references between them are sparse:

- ECON-FE1 → no GATE-ES1 cross-link (Evan F-04).
- ECON-FE1 schema lacks `minimum_confirmation_n_obs` enforcement (Evan F-01) — schema can pass while rule fails.
- APP-LP8 → no ECON-FE1/GATE-ES1 cross-link (Ace F-07).
- Dana not mentioned anywhere despite being upstream of sample-separation evidence (Dana F-14).

This is a chain with no clinical break (no current pair has promoted past `found_in_search`), but the cross-links must land in Phase 4 before the first pilot final-exam runs. Otherwise the contract becomes operational with documentation drift baked in.

### B4. Schema-bump propagation contract (Evan-side missing rule)

Evan F-11: BL-LEGACY-WINNER-SUMMARY-SHAPE documents 6 legacy pairs failing v1.1.0 schema after `threshold_value` bump. Lesson: every schema bump should trigger a portfolio-wide validate sweep before any other work. Not gated. Add as ECON-BUMP1 (or sub-rule of ECON-H5) in Phase 4.

This is a Lead-level concern because schema files are META-CF artifacts and the propagation rule belongs in `team-coordination.md` (or as a META rule), not buried in the econometrics SOP.

### B5. Hand-written legacy bypass class (Ace F-16) is an unsolved recurrence pattern

Whenever a new feature ships into `page_templates.py`, the 5 hand-written legacy Methodology pages silently miss it. Wave 10H.1 caught one instance (`_render_exploratory_insights` not on `9_hy_ig_v2_spy_methodology.py`); the next will do the same.

**Resolution:** Ace F-16 fix in Phase 4 — add a positive grep gate to APP-PT1. No Lead arbitration needed; route into Ace's fix list with priority FAIL.

---

## C. Lead Arbitrations (Binding for Phase 4)

These decisions must be communicated to all relevant agents in their Phase 3 cross-review prompts and again in their Phase 4 fix prompts.

| ID | Decision |
|----|----------|
| LA-1 | `history_zoom_events_registry.json` is the canonical episode registry. `episode_registry.json` is deprecated; convert to thin pointer or retire. |
| LA-2 | Canonical slug set: `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`. All other slugs (`dot_com`, `rates_2022`, `taper_2013`, `china_2015`, `ukraine`) are non-canonical. `china_2015` and `ukraine` need explicit registry promotion or removal — Vera authors a registry PR in Phase 4. |
| LA-3 | `HISTORY_ZOOM_EPISODES` is the canonical pair-config attribute for zoom narratives. `ZOOM_EPISODE_NARRATIVES` is retired. RES-ZOOM1 narrows to content guidance and points to RES-HZE1 for delivery format. |
| LA-4 | Evan owns `observed_direction` post-tournament. Dana leaves it absent at data-stage handoff. APP-DIR1 row in `docs/standards.md` is corrected. |
| LA-5 | Lead writes one batch update to `docs/standards.md` registering all unregistered rules from §A1. Each agent's Phase 4 fix produces the rule text; Lead consolidates rows. |
| LA-6 | GATE-CL family (CL1–CL8) is registered under the GATE prefix in `docs/standards.md` (gates are GATE-owned regardless of authoring agent). Cross-references in the Ace SOP remain. |
| LA-7 | Ray's `memories.md` requirement is removed from research-agent-sop.md. Reflection consolidates to `experience.md` to match team norm. |
| LA-8 | Schema-bump propagation contract is promoted to a META rule (META-SBP) in `docs/agent-sops/team-coordination.md`, not buried in the econometrics SOP. |
| LA-9 | `ECON-SD` audit gate must appear in Quincy's QA SOP (QA-CL2 family or new gate slot). Resolves Evan F-13 dead-letter. |
| LA-10 | Stale items get explicit retirement: matplotlib palette table in Vera SOP (Vera F-01); v1.0.0 schema citation in ECON-H5 (Evan F-05); migration list in APP-PT1 (Ace F-11); "Unlike earlier phrasing" sentence in VIZ-CV1 (Vera F-03). |

---

## D. Items That Cannot Be Resolved in Phase 4 (carry to backlog)

These exceed SOP-review scope and need separate dispatches:

1. **`scripts/lint_column_suffixes.py`** (DATA-D12 dead-letter, BL-D12-LINTER, P1) — needs a Dana script-build dispatch, not an SOP edit. Phase 4 can add a fallback procedure but cannot conjure the script.
2. **`scripts/viz_v11_palette_lint.py`** — VIZ-V11 paper-rule status. Same shape as DATA-D12. Phase 4 SOP edit can cross-reference the planned script and treat manual lint as the current procedure.
3. **`scripts/gate_cl_audit.py`** (GATE-CL7/CL8 enforcement, Wave 10K Phase 1 plan) — backlog item; not in SOP-review scope.
4. **BL-LEGACY-WINNER-SUMMARY-SHAPE** (Evan, 6 legacy pairs failing schema v1.1.0) — needs an Evan pipeline rerun, not an SOP edit. Phase 4 adds the propagation rule that would have caught this; the artifact remediation is separate.
5. **BL-D13-MANIFEST** (6 legacy pairs missing manifest entries) — Dana script-execution dispatch, not SOP.
6. **BL-004** (architectural decision: `app/pair_configs/*.py` vs `docs/portal_narrative_*.md` as authoritative) — referenced in RES-EGL1; still open. Defer; Phase 4 adds a TBD note.

---

## E. Phase 3 Cross-Review Agenda

For Phase 3, each agent reviews the other five SOPs from a handoff perspective. Briefs must include the LA arbitrations above so cross-reviewers don't re-relitigate them. Specific cross-pair concerns to seed:

| Reviewer | Targets / focus |
|----------|-----------------|
| Dana | Evan's interpretation_metadata field ownership; Vera's data-direct-from-Dana paths; Ray's narrative reads of data fields |
| Evan | Vera's chart-type registry vs ECON-H4 handoff table; Ray's headline-from-OOS-record contract; Quincy's GATE-ES1 vs ECON-FE1 numeric floors |
| Vera | Ray's narrative chart-status field; Ace's APP-PT1/PT2 template chart consumption; Quincy's GATE-DP1/HZE1/NBER2 vs producer-side rules |
| Ray | Evan's CP1/CP2 trigger semantics; Vera's slug namespace + skip protocol; Ace's HISTORY_ZOOM_EPISODES contract; Quincy's GATE-HZE1 content-vs-structure boundary |
| Ace | Dana's interpretation_metadata write paths; Evan's winner_summary schema version; Ray's narrative attribute names; Quincy's GATE-CL family ownership |
| Quincy | All five producer-side gates (DATA-D6/D6b/D12, ECON-FE1/T4/INF1/SD, VIZ-CV1/DP1/HZE1/NBER1, RES-OD1/HZE1, APP-PR1/WS1/LP8) — confirm code coverage matches SOP language |

---

## F. Phase 4 Sequencing

Phase 4 cannot start until:
- LA-1 through LA-10 are communicated to all agents.
- Phase 3 cross-reviews complete (any new findings folded in).

Phase 4 dispatch order is not strictly serial, but with two coordination dependencies:
- Vera authors registry consolidation (LA-1, LA-2) **first**; her result unblocks Ray, Evan, Quincy retargeting.
- Lead's `docs/standards.md` batch update (LA-5) lands **last** — after all agents have confirmed their final rule names and severity.

All other Phase 4 fixes can run in parallel.

---

*Phase 2 complete. ~90 Phase-1 findings synthesized into 10 binding Lead arbitrations and 6 backlog items. No role-owned files touched (LEAD-DL1 self-check clean).*
