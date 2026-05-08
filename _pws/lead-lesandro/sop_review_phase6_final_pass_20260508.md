# SOP Review — Phase 6 Lead Final Pass

**Author:** Lead Lesandro
**Date:** 2026-05-08
**Branch:** 260430
**Scope:** Token efficiency, inter-departmental rapport, handoff smoothness, sign-off.

---

## A. Token Efficiency Assessment

### A1. Current corpus sizes

| File | Lines | Approx. KB |
|------|------:|----:|
| `docs/agent-sops/visualization-agent-sop.md` | 1737 | 134 |
| `docs/agent-sops/team-coordination.md` | 1834 | 132 |
| `docs/agent-sops/research-agent-sop.md` | 1514 | 126 |
| `docs/agent-sops/appdev-agent-sop.md` | 1588 | — |
| `docs/agent-sops/econometrics-agent-sop.md` | 1560 | — |
| `docs/agent-sops/qa-agent-sop.md` | 980 | 82 |
| `docs/agent-sops/data-agent-sop.md` | 846 | — |
| `docs/standards.md` | 437 | 93 |
| Total agent SOPs + standards | ~10.5K | ~960 KB |

The role SOPs grew during Phase 4 (averaging +50 to +100 lines each from new rules, definitions, and cross-references). At ~960 KB total, the canonical SOP corpus is at the upper edge of what a single SOD scan can hold cheaply.

### A2. Token efficiency findings (advisory — not Phase 6 fixes)

These are flagged for a future hygiene wave (BL-SOP-COMPRESS), not for immediate Phase 6 action:

1. **Glossaries authored multiple times.** Each role SOP now defines its own "Key Definitions" sub-section (Phase 4 mandate). 6 glossaries × ~20 lines each ≈ 120 redundant lines if some terms repeat across SOPs. Candidate consolidation: a single `docs/glossary.md` (or extend `docs/portal_glossary.json`) referenced from each SOP.
2. **Pseudocode inline vs scripted.** VIZ-DP1, GATE-DP1, GATE-HZE1, GATE-SD1, GATE-NR all carry inline Python in the SOP body. Net rule clarity is high, but if these scripts ever land in `scripts/` (BL-VIZ-V11-LINT, BL-GATE-CL-AUDIT), the SOP can drop to a one-line cite + script path.
3. **Cross-reference verbosity.** Several rules end with a 4-6 cross-ref list (e.g. ECON-FE1, APP-DIR1, GATE-31). These are useful but each adds ~80 chars × 50 rules = 4 KB. Could be tabulated in `docs/standards.md` once and cross-ref'd from rule bodies via "see standards.md row" rather than restated.
4. **Anti-patterns sections.** Several SOPs (Evan, Ace) carry detailed anti-pattern enumerations that mirror entries in `docs/sop-changelog.md` waves. Consolidate or cross-ref instead of duplicating.

None of these are blockers. They become relevant if the corpus crosses ~150% of the prompt-cache window during agent dispatches.

### A3. Bloat already prevented this wave

- LA-7 dropped Ray's redundant `memories.md` requirement: ~40 lines removed across reflection sections + standards.md + future per-wave reflection writes.
- LA-1 / LA-2 collapsed two parallel episode registries into one: removes the cognitive cost of maintaining mirrored slug sets across SOPs (and prevents future drift).
- LA-3 retired `ZOOM_EPISODE_NARRATIVES`: one less attribute name to remember.

Net: the wave added rules, but the architectural arbitrations also retired duplicative structures.

---

## B. Inter-Departmental Rapport (Cross-Reference Health)

### B1. LA-* citation density per SOP

| SOP | LA-* mentions |
|-----|--------------:|
| research | 12 |
| qa | 9 |
| econometrics | 7 |
| appdev | 6 |
| visualization | 4 |
| team-coordination | 3 |
| data | 2 |

Ray's high citation count reflects the LA-1/LA-2/LA-3/LA-7 propagation work being concentrated in his SOP. Vera's lower count is misleading — she **owns** LA-1 (registry consolidation) so her implementation lives in the schema and registry data, not in citations. Rapport indicators: every agent cites at least 2 LA arbitrations, confirming the arbitrations are operationally adopted, not paper.

### B2. Phantom cross-references retired

Phase 4 closed three phantom IDs Vera flagged in Phase 1 (META-RYW, QA-CL6, GATE-NC). Phase 6 audit reveals:
- **META-RYW is actually a real rule** defined in `team-coordination.md` (Wave 10F) but was never registered in `standards.md` — that's why Vera's Phase 1 review classified it as phantom. **Phase 6 fix:** Lead registered META-RYW in `standards.md` to close the discoverability gap.
- **QA-CL6 and GATE-NC** are confirmed phantom (no occurrence anywhere in the corpus). Vera's Phase 4 cross-reference removal was correct.

Dana's SOP at line 595 still cites META-RYW correctly — this reference is now resolvable from `standards.md`.

### B3. Work-chain integrity (handoff smoothness)

Two key cross-agent chains traced end-to-end:

**Episode-narrative chain (Ray → Vera → Ace → Quincy):**
- RES-HZE1 referenced in 5 files (research, appdev, lead, qa, standards) ✓
- ACE-HZE1 referenced in 4 files (appdev, research, visualization, standards) ✓
- VIZ-HZE1 referenced in 4 files (visualization, appdev, research, standards) ✓
- VIZ-ZOOM1 referenced in 4 files (visualization, research, qa, standards) ✓
- GATE-HZE1 referenced in 3 files (qa, visualization, standards) ✓

Chain is closed. Each producer cites the consumer's gate; each gate cites the producer rule. Slug namespace is unified (LA-2). Config-attribute name is unified (LA-3). Registry path is unified (LA-1).

**Direction chain (Evan → Ray → Ace → Quincy):**
- ECON-DIR1: 4 references ✓
- ECON-DIR2: registered in standards.md (Phase 4b new) ✓
- RES-OD1: 4 references ✓ (incl. tightened OD1a/OD1b/OD1c sub-rules)
- APP-DIR1: 6 references (heavily cross-cited; healthy) ✓
- GATE-NR: 4 references ✓ + `_gate_nr_check()` implementation in `cloud_verify.py` (Quincy Phase 4)

Chain is closed. `observed_direction` ownership now consistently attributed to Evan post-tournament (LA-4) across DATA-D6, ECON-DIR1/DIR2, RES-OD1, APP-DIR1.

**Final-exam evidence-status chain (Evan → Quincy → Ace):**
- ECON-FE1 references GATE-ES1 (added Phase 4) ✓
- GATE-ES1 references ECON-FE1 + APP-LP8 + schemas (added Phase 4) ✓
- APP-LP8 references ECON-FE1 + GATE-ES1 (added Phase 4) ✓
- `final_exam_results.schema.json` 1.0.1 with `minimum_confirmation_n_obs` enforces the numeric floor producer-side ✓
- Example instance validates against schema (Phase 5 fix-up) ✓

Chain is closed and operationally enforceable.

### B4. Schema-bump propagation chain (newly authored META-SBP)

- META-SBP defined in `team-coordination.md` ✓
- META-SBP registered in `standards.md` ✓
- ECON-BUMP1 (Evan-side instantiation) defined in econometrics SOP ✓
- ECON-BUMP1 registered in `standards.md` ✓
- Cross-ref to META-CF, META-SCV, META-VNC, META-UC ✓

**Validation:** Phase 5 caught a META-SBP violation in real time — Evan bumped `final_exam_results.schema.json` to 1.0.1 without updating the example instance. The violation was detected by Lead's audit grep, not by Quincy's gate. This is the failure mode META-SBP was meant to prevent. Fix-up wave closed it. Quincy's QA-CL1 should soon include a META-SBP audit step (deferred to next wave's QA SOP refinement).

---

## C. Outstanding Items (carry to backlog)

These were identified during the 6-phase review but are out of scope for this wave's SOP-first remediation:

1. **BL-SOP-COMPRESS** — token-efficiency hygiene wave per §A2 (glossary consolidation, scripted pseudocode externalization, cross-ref tabulation).
2. **BL-D12-LINTER** — `scripts/lint_column_suffixes.py` (Dana's DATA-D12 dead-letter; P1, unchanged).
3. **BL-VIZ-V11-LINT** — `scripts/viz_v11_palette_lint.py` (Vera's VIZ-V11 paper-rule; documented in Phase 4 with manual lint as current procedure).
4. **BL-GATE-CL-AUDIT** — `scripts/gate_cl_audit.py` (Wave 10K Phase 1 plan; GATE-CL7/CL8 enforcement automation).
5. **BL-LEGACY-WINNER-SUMMARY-SHAPE** — 6 legacy `winner_summary.json` instances need re-running to v1.1.0 schema. SOP rule (ECON-BUMP1 + META-SBP) added in this wave; the artifact remediation is its own dispatch.
6. **BL-D13-MANIFEST** — 6 legacy pairs missing manifest entries.
7. **BL-004** — architectural decision: `app/pair_configs/*.py` vs `docs/portal_narrative_*.md` as authoritative (referenced in RES-EGL1; still open).
8. **META-SBP audit step in QA-CL1** — Quincy adds a wave-checklist item: "if any schema's `x-version` bumped this wave, regression note exists with portfolio-wide instance sweep table." Defer to next wave's QA SOP refinement.

---

## D. Sign-Off

The six-phase SOP review is complete. End-state:

- **~90 Phase-1 findings + ~133 Phase-3 findings** triaged; **~117 SOP edits + 5 schema updates** applied.
- **10 Lead arbitrations** (LA-1 to LA-10) ratified and propagated across role SOPs, schemas, and code.
- **44 new rule rows + 1 META-RYW backfill** registered in `docs/standards.md`.
- **META-SBP** authored in `team-coordination.md` as a new cross-agent META rule.
- **Three key work-chains** (episode-narrative, direction, final-exam evidence-status) verified end-to-end.
- **5 Phase-5 residue findings** fixed in a focused mini-wave (Evan, Ace, Vera, Lead).

**LEAD-DL1 final self-audit.** Lead writes confined to:
- `docs/standards.md` (Phase 4b batch + Phase 6 META-RYW row)
- `docs/agent-sops/team-coordination.md` (META-SBP authoring)
- `docs/sop-changelog.md` (closure entry)
- `_pws/lead-lesandro/*` (Phase 2/5/6 audit documents)
- `_pws/_team/status-board.md` (status entries)

Zero edits to role-owned SOPs, schemas, configs, charts, results, scripts, or pair pages. Discipline held throughout the six phases.

**Sign-off.** SOP corpus is internally consistent, cross-referentially closed, and work-chain-integrity verified. The team can resume product work (next priority pair #4 US10Y-US3M → SPY, or final-exam pilot) on the updated SOP foundation.

*Phase 6 closure — six-phase SOP review wave complete.*
