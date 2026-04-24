# Research Ray — Outstanding Work

**Agent Identity:** Research Ray
**PWS Path:** `_pws/research-ray/`
**Last updated:** 2026-04-24 — Wave 10J/10K checkpoint

---

## Blocked / Awaiting Lead Dispatch

| Item | Description | Blocked on |
|------|-------------|-----------|
| Pair #4 (US10Y-US3M → SPY) | Research/narrative layer for next priority pair | Lead dispatch |
| RES-OD1 three-step fix | Upgrade equality check to correctness check (read `winner_summary.json.direction` as authoritative) | Lead disposition — propose code patch |
| Pair-class-specific episode sets for Taper 2013 + China 2015 | Proposed in self-reflection; rates-class pairs should include these episodes | Lead decision before Pair #4 |
| BL-APP-PT1-UMCSENT disposition | umcsent_xlv strategy page bypasses APP-PT1 template flow | Lead decision |

## Open Monitoring Items (Not Mine to Fix)

| Item | Owner | Status |
|------|-------|--------|
| BL-004 — narrative surface (.py vs .md) | Ace | Open — monitor |
| FAIL-06 — "Ray leg pending" stub replaced with 3-way direction check | Ace | Resolved in Wave 10I.C; verifying stays clean |
| Legacy broker-style CSV for indpro_spy, permit_spy, vix_vix3m_spy | Evan / Dana | Open |
| Chart-filename drift (`indpro_spy_hero.json` vs bare `hero.json`) | Vera | Open |

## Backlog (Low Priority)

| Item | Description |
|------|-------------|
| Glossary SLA clock | No open `status=open` entries should age past 7 days; review at each SOD |
| `memories.md` deprecation | My SOP inconsistency (uses both memories.md + experience.md vs other agents' experience.md only) — align on next available wave |
| Episode registry maintenance | Add new episodes as they arise; propose pair-class expansion for equity/sector pairs |

## Completed This Wave (2026-04-24)

- [x] Self-reflection: authored RES-HZE1 rule
- [x] Episode registry: designed + authored `docs/schemas/episode_registry.json`
- [x] Pair reclassification: dff_ted_spy/sofr_ted_spy → rates; ted_spliced_spy → credit
- [x] HZE1 retro-apply: HISTORY_ZOOM_EPISODES narratives for all 8 pairs
- [x] RES-20 triad verified across all 8 pairs
- [x] META-CPD cross-reference added (commit `00f27d9`)
- [x] Handoff: `results/_cross_agent/handoff_ray_hze1_retro_20260424.md`
