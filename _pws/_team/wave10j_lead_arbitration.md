# Wave 10J — Lead Arbitration: Debate Round 1 + Round 2
*Authored by: Lesandro (Lead)*
*Date: 2026-04-24*
*Source: All five R1 submissions + all five R2 submissions*

---

## Rulings on Six Contested Points

---

### D1 — NBER Shading Redundancy: What stays in GATE-CL1?

**Positions after R2:**
- Vera: V2 becomes blocking at handoff; GATE-CL1 should contain render-success only; Quincy holds independent GATE-VIZ-NBER1 at portal level
- Ace: Drops DOM check; keeps Plotly JSON shape check (vrect/rect) in GATE-CL1 as integration-time verification — different trust level from Vera's creation-time V2
- Quincy R1: Remove NBER entirely from GATE-CL1; Vera owns via V2

**Ruling: Ace's architecture, with V2 made blocking.**

Ace's trust-level argument is correct and consistent with how the team already handles other redundancies (Evan schema-validates before handoff, Quincy schema-validates independently — both kept). Vera's V2 is creation-time; Ace's JSON shape check is integration-time. These catch different failure modes:
- V2 catches missing shading before the chart is committed
- Ace's check catches shading that was present at Vera's commit but corrupted or stripped during Ace's config wiring or chart reload

Quincy's "same underlying state" objection (R1) falls because the two checks run at different moments, on different file instances. The DOM check (same state as JSON) is correctly dropped.

**Implementation required:**
1. Vera: V2 becomes a **blocking** pre-handoff gate (no handoff without VIZ-V5 log AND vrect/rect assertion passing)
2. Ace: GATE-CL1 retains JSON shape check, removes DOM shading check
3. Quincy: Add GATE-VIZ-NBER1 to cloud_verify.py — portal-level shading check (HTML content scan for "NBER" or shading-related class)

---

### D2 — interpretation_metadata.json producer voice in ECON-DIR1

**Ruling: Settled. Vera correct. Already implemented.**

Evan fully conceded and committed the fix (e8c659b). ECON-DIR1 is now a consumer-side validation gate with `[SCRIPT]` enforcement tags. Evan returns the file to Dana on mismatch — does not fix in place.

No further action required.

---

### D3 — Lesson system: Registry vs. SOP-rule-first vs. Ratification

**Positions after R2:**
- Ace: Every lesson must produce a SOP rule immediately; experience.md entry links to rule; no rule = not ready to record
- Ray: Drops full registry; keeps minimal cross-agent impact log in status-board.md (5 fields: rule_id, authored_by, affected_agents, action_required, wave)
- Quincy: Synthesis — all three compatible as a pipeline: Ace's model governs creation, Ray's log governs cross-agent visibility, Quincy's ratification governs distribution; carve-out for "pending-rule" status with wave-limit

**Ruling: Quincy's synthesis, with Ace's model as the primary gate.**

The three models are not alternatives — they are layers:

1. **Entry gate (Ace):** A lesson must produce a SOP rule change before it enters any record. "Pending-rule" is allowed with a one-wave deadline (Quincy's carve-out). After one wave without a rule, the lesson is escalated to Lead.
2. **Visibility mechanism (Ray):** Every new SOP rule that affects another agent's behavior gets a 5-field entry in `_pws/_team/status-board.md` under a "Cross-Agent Impact" section. No separate registry file — the status board is already read at SOD.
3. **Distribution (Quincy):** Post-wave ratification round — each agent reads the Cross-Agent Impact entries since last wave and explicitly adopts or dismisses. Logged in `_pws/_team/wave_NNx_lessons_ratified.md`.

**Implementation required:**
1. team-coordination.md: Add Cross-Agent Impact section format to status-board protocol
2. All five agent SOPs: Add entry gate rule ("lesson → SOP rule before experience.md entry")
3. Quincy SOP: Add post-wave ratification round as a standard step

---

### D4 — Perceptual PNG verification: Producer self-attestation vs. QA gate

**Ruling: Vera correct. Quincy accepts. Implement.**

Vera's conflict-of-interest argument is structurally sound. Quincy conceded. The gate:
- `git ls-files output/charts/{pair_id}/plotly/_perceptual_check_{chart_name}.png` for every mandatory-NBER chart
- FAIL = any mandatory chart has no committed PNG (Vera skipped the kaleido step)
- QA does NOT gate on visual quality — that is an unverifiable judgment; only existence is checked

**Implementation required:**
1. Quincy SOP + cloud_verify.py: Add PNG existence check to GATE-27

---

### D5 — gate_cl_audit.py: Ace solo vs. team deliverable

**Ruling: Ace's two-phase model.**

Ace's key insight is correct: the script reads committed artifact files already in the repo — no cross-agent fixtures are required to *run* it. Fixtures are only needed for the pytest test suite. The distinction is valid.

- **Phase 1 (Wave 10K):** Ace writes and runs `scripts/gate_cl_audit.py` solo against the live portfolio. No blockers.
- **Phase 2 (Wave 10K+1):** Evan (schema fixtures), Vera (chart rendering fixtures), Ray (narrative stub fixtures), Quincy (integration into cloud_verify.py) contribute to the test suite jointly.

GATE-CL1-5 remain labeled "ASPIRATIONAL" in Ace's SOP until Phase 1 is complete. Wave 10K cannot close without Phase 1 delivered.

**Implementation required:**
1. Ace SOP: Label GATE-CL1-5 "ASPIRATIONAL — gate_cl_audit.py due Wave 10K Phase 1" explicitly in SOP text

---

### D6 — Direction vocabulary validation

**Ruling: Settled. Vera correct. Already conceded by both Evan and Ray.**

- Evan: ECON-DIR1 recast with vocabulary check as `[SCRIPT]` gate (e8c659b). Deprecated vocabulary template corrected in SOP.
- Ray: RES-OD1 vocabulary assertion added (described in R2 — commit required).

**Implementation required:**
1. Ray: Commit the RES-OD1 vocabulary assertion change described in R2

---

## Smoke Test Taxonomy (Convergence — unanimous)

All five agents agreed. Final taxonomy — implement in all relevant SOPs and team-coordination.md:

| Name | Owner | Scope |
|------|-------|-------|
| **Schema lint** | Evan | `validate_schema.py` against winner_summary.json per pair |
| **Portal lint** | Ace | AST-parse + `load_plotly_chart` non-None assertion |
| **Chart rendering validation (VIZ-CV1)** | Vera | VIZ-V5 JSON integrity + kaleido render |
| **Smoke test** | Quincy | `cloud_verify.py` + mandatory DOM-file read |

The term "smoke test" is reserved exclusively for Quincy's end-to-end cloud verification. No other agent uses this term.

---

## Handoff Template (Convergence — unanimous)

team-coordination.md owns the canonical handoff definition. All agent SOPs reference it, not define their own variants. Evan's template is the closest to complete and becomes the team standard with one addition: bidirectional receipt section ("Items received from upstream: [list]").

---

## Summary: What Gets Implemented

| # | Action | Owner | Wave |
|---|--------|-------|------|
| D1a | V2 becomes blocking pre-handoff gate | Vera | 10J |
| D1b | GATE-CL1 keeps JSON shape check, removes DOM check | Ace | 10J |
| D1c | Add GATE-VIZ-NBER1 to cloud_verify.py | Quincy | 10J |
| D2 | Done (e8c659b) | Evan | ✓ |
| D3a | Cross-Agent Impact section added to status-board protocol | Lead → team-coordination.md | 10J |
| D3b | Entry gate rule added to all five agent SOPs | Each agent | 10J |
| D3c | Post-wave ratification round added to Quincy SOP | Quincy | 10J |
| D4 | PNG existence check added to GATE-27 + cloud_verify.py | Quincy | 10J |
| D5 | GATE-CL1-5 labeled ASPIRATIONAL; gate_cl_audit.py Phase 1 due | Ace | Wave 10K |
| D6 | RES-OD1 vocabulary assertion committed | Ray | 10J |
| T1 | Smoke test taxonomy in all SOPs + team-coordination.md | Each agent | 10J |
| T2 | Unified handoff template in team-coordination.md | Lead | 10J |

---

*Lead arbitration complete. Dispatch implementation commits.*
