# Ace — Outstanding Work

_Last updated: 2026-04-24 (Wave 10J/10K checkpoint)_

## P0 — Non-negotiable before Wave 10K closes

### gate_cl_audit.py Phase 1
**What:** Implement GATE-HZE1 check in `scripts/cloud_verify.py` per Quincy's pseudocode in the GATE-HZE1 SOP section.
- Wire into `check_page()` Story-page branch.
- For each pair: assert heading `"How the Signal Performed in Past Crises"` is present in Story DOM when `history_zoom_*.json` files are committed for that pair.
- Failure disposition: FAIL if charts committed + heading absent (config/Ace bug); WARN if no charts yet (Vera blocker — auto-promotes to FAIL once Vera ships charts).
- Script-only change; no portal code required.
**Owner:** Ace
**Blocks:** Quincy next smoke run; GATE-HZE1 is currently paper-only (SOP written, not implemented).

---

## P1 — High priority backlog

### APP-PT1 retro-apply — remaining pairs
Migrate to thin wrappers (lift narrative to config, template untouched). Net LoC per pair: -400 to -700 page lines, +300 config lines.
- hy_ig_v2_spy (reference pair — last)
- umcsent_xlv Strategy (BL-APP-PT1-UMCSENT)
- All TED variants already migrated (Wave 10I.A Part 2) ✓

### ACE-HZE1 acceptance gate in config review workflow
When the next new pair config is authored, enforce:
1. `ls output/charts/{pair_id}/plotly/history_zoom_*.json` — count must match `HISTORY_ZOOM_EPISODES` length.
2. Each slug in the list must appear in `docs/schemas/episode_registry.json` for the pair's `indicator_category`.
3. If mismatch → blocker filed before config commit.

---

## P2 — Open backlog items (not immediately blocking)

| ID | Description | Depends on |
|----|-------------|-----------|
| BL-002 | Cross-pair unit-form inherit for sample pairs (1-4_*, 5-8_*) | — |
| BL-004 | Cross-pair prose leak audit (other pages may cite out-of-scope signals) | — |
| BL-APP-PT1-LEGACY | Full APP-PT1 migration sweep (all remaining hand-written pairs) | Lead scheduling |
| BL-CHART-GAPS-LEGACY | equity_curves/drawdown/walk_forward missing for TED/permit/vix pairs | Evan/Vera |
| BL-VIZ-O1-LEGACY | VIZ-O1 chart disposition audit for pre-Wave-10H pairs | Vera |
| APP-EX1 v1.1.0 | Propose sixth canonical expander entry "status_labels_glossary" | Lead approval |
| RES-17 upgrade | When Ray narrative_frontmatter migration lands, upgrade APP-DIR1 to 3-way check | Ray |
| APP-PT1 v1.1 | Variant template for pairs needing different Story structure | Lead approval |

---

## Completed this session (Wave 10J/10K — 2026-04-24)

- [x] ACE-HZE1 rule authored (self-reflection)
- [x] ACE-HZE1 coherence gaps fixed (3 issues, commit d2b52ae)
- [x] HISTORY_ZOOM_EPISODES wired into 8 pair configs (commit 816444f)
- [x] vix_vix3m_spy dot_com omission note filed (commit d99e7da)
- [x] META-CPD cross-reference added to AppDev SOP (commit 66b58d3)
- [x] Wave 10J Phase 5: 60/60 PASS
