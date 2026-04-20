# AIG-RLIC+ Rule Backlog

**Owner:** Lead Lesandro
**Authority:** `META-BL` (Backlog Discipline) — see `docs/agent-sops/team-coordination.md` §META-BL
**Purpose:** Registry of proposed rules that were considered, discussed, and **deliberately deferred** — preserving the proposal, its motivation, and the reactivation trigger so future Leads (or the same Lead at a later session) can pick up the thread without re-deriving it from scratch.

---

## How to use this file

- **When a rule is proposed but not adopted:** add a row here with the proposer, the proposed rule ID (if one was drafted), the motivation, the decision (deferred / rejected), the reason for deferral, the reactivation trigger, and the date.
- **At EOD:** Lead scans the `reactivation_trigger` column; any item whose trigger has fired is either re-opened (promoted to SOP) or explicitly closed (trigger fired but decision unchanged — add a dated note to the row).
- **When an item is promoted:** strike through the row, add a pointer to the SOP section where it now lives, and keep the row for historical traceability.
- **When an item is rejected outright:** move to the "Rejected Proposals" section at the bottom with a one-line rationale.

Backlog entries are NOT active rules. They have no enforcement authority until promoted to an SOP and registered in `docs/standards.md`.

---

## Active Deferrals

| ID | proposer_agent | proposed_rule_id | motivation | decision | deferred_reason | reactivation_trigger | date |
|----|----------------|------------------|------------|----------|-----------------|----------------------|------|
| BL-001 | Ace | APP-SEV1-MAP | Validation severity (L1/L2/L3) currently assigned per-call by Ace; proposal is to move to a lookup JSON so severity is consistent across components | Deferred to next sprint per Lesandro 2026-04-19 | Current ad-hoc assignments work; mechanization doesn't affect what stakeholders see; other Wave 5B rules have higher stakeholder-visible ROI | Triggered if (a) inconsistent severity causes a real bug, OR (b) after Pair #10 when severity drift becomes more likely with scale | 2026-04-19 |
| BL-002 | Quincy | (ECON-UD cross-pair retro-apply) | Wave 7 introduced `signal_scope.json` for HY-IG v2; the 5 other completed pairs (indpro_spy, sofr_ted_spy, dff_ted_spy, ted_spliced_spy, permit_spy, vix_vix3m_spy, hy_ig_spy sample) lack this file. ECON-UD's Universe Disclosure requirement is not uniformly met across the portal. | Deferred per Lesandro 2026-04-20 | Wave 7 cross-pair audit confirmed 0 active scope leaks on other pairs (they were clean by construction — only HY-IG v2 had the leak). Universe Disclosure gap exists but no stakeholder-visible symptom; retro-apply is hygiene, not urgent. | Triggered when (a) next pair is promoted to reference-pair candidacy, OR (b) stakeholder asks to see the Universe on a non-HY-IG-v2 pair, OR (c) during Pair #4 execution when fresh SOP compliance is the baseline | 2026-04-20 |
| BL-003 | Quincy | (ECON-AS cross-pair placeholder) | Companion to BL-002: the 5 non-HY-IG-v2 completed pairs lack `analyst_suggestions.json` files. ECON-AS is informational only; placeholder files (even if empty) would make the schema contract visible on every pair's Methodology page | Deferred per Lesandro 2026-04-20 | Lower priority than BL-002 — if no suggestions exist, an empty file is low-value until agents naturally file entries during future analysis work | Triggered alongside BL-002 (bundle the work) | 2026-04-20 |
| BL-004 | Ace + Quincy | (APP-NP1 Narrative-to-Page Prose Sourcing) | Wave 7C-1 QA caught that portal `.py` pages contain hardcoded `st.markdown()` prose that bypasses Ray's narrative markdown authority — Ray cleaned CCC-BB from the narrative but Ace's page files had their own prose saying the same wrong thing. This is a structural gap: narrative authority is split across `docs/portal_narrative_*.md` AND `app/pages/*.py` with no contract for sourcing. Proposed rule would require page prose to source from narrative frontmatter/anchors, limiting inline page code to chart captions + structural labels. | Deferred per Lesandro 2026-04-20 | Not urgent — Ace's Wave 7C fix-up closed the HY-IG v2 instance. But the pattern will recur: Sample HY-IG pages likely have the same gap, and every new pair starts with Ace writing some inline prose. A proper rule would change the component architecture. | Triggered when (a) another narrative-vs-page drift incident surfaces, OR (b) Pair #4 execution starts (force Ace to write pages with the new discipline from scratch rather than retrofit), OR (c) a scheduled refactor wave dedicated to the `app/components/narrative_renderer` abstraction | 2026-04-20 |

---

## Rejected Proposals

*(none yet)*

---

*Last updated: 2026-04-20 (Lead Lesandro, post-Wave-7C)*
