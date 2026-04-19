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

---

## Rejected Proposals

*(none yet)*

---

*Last updated: 2026-04-19 (Lead Lesandro, Wave 5B-1)*
