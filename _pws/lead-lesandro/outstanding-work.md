# Outstanding Work — Lead Lesandro

## Evidence-Status Follow-On

- **Final-exam contract defined, implementation pending** — Evan and Quincy completed SOD/EOD-gated drafts on 2026-05-01. Lead promoted `ECON-FE1`, `GATE-ES1`, `evidence_status` v1.1, and `final_exam_results.schema.json`. Current pairs still default to `found_in_search`; no pair may upgrade until Evan produces a valid `final_exam_results_{YYYYMMDD}.json` artifact and Quincy verifies it.
- Candidate next dispatch: Evan builds the final-exam computation/replay helper for one pilot pair; Quincy adds a focused verification path once the producer artifact exists.

## Wave 10H.2/10I Hygiene Wave (bundleable)

Four backlog items, all closely related, best shipped together:
- **BL-VIZ-O1-LEGACY** — create minimal `_meta.json` sidecars for 35 legacy-pair chart JSONs (6 legacy pairs)
- **BL-VIZ-SIDECAR-HELPER** — consolidate 4 bypass generators into `scripts/_chart_sidecar.py` shared helper
- **BL-APP-PR1** — new rule for path-resolution discipline (`_REPO_ROOT` anchors mandatory, bare relatives prohibited)
- **BL-APP-PT1-LEGACY** — migrate 5 hand-written Methodology pages to template wrappers (Sample, indpro_spy, permit_spy, vix_vix3m_spy, ted variants, umcsent_xlv)

Scope estimate: ~1 full agent-wave (Ace-heavy, Vera light support, Quincy verify). Blocks: none — framework is live on active pairs; legacy gap is hygiene.

## Next Priority Pair
- **Pair #4: US10Y-US3M → SPY** (yield curve slope, daily, Yield Curve/Rates type)
- This is a well-studied indicator with strong literature (Estrella & Hardouvelis 1991)
- Expected: counter-cyclical (inverted curve → recession → equity weakness)

## Remaining Pairs (68 of 73)
- 5 completed: #1 INDPRO, #2 SOFR/TED (3 variants), #3 Permits, #11 VIX/VIX3M, #20 HY-IG (sample + v2)
- Next SPY pairs: #4 T10Y3M, #5 UMCSENT, #6 HSN1F, #7 ISM_MFG_PMI, ...
- Full list in `docs/priority-combinations-catalog.md`

## Pipeline Template Fixes Needed
- [ ] Add `bool()` cast for numpy bool in JSON serialization (pair_pipeline_permit_spy.py has the fix)
- [ ] Standardize L6 as default lead for monthly indicators in tournament grid
- [ ] Consider creating a truly generic `pair_pipeline_generic.py` that reads config from Analysis Brief

## SOP Improvements To Consider
- [x] Add audience-friendliness rules to Research + AppDev SOPs (done 2026-04-10)
- [x] Add 8-element Evidence template to SOPs (done 2026-04-11, Part D)
- [x] Add classification metadata schema + gate items 19-21 (done 2026-04-11, Part D)
- [x] SOP hardening from stakeholder bug review (done 2026-04-11, Part E — 34 new rules)
- [x] Add chart naming convention (done 2026-04-11, Viz Rule A3 canonical path)
- [x] Add trade log UX rules: Econometrics C4, AppDev §3.8 #5, Research "How to Read" (done 2026-04-11)
- [ ] Codify "variant family" pattern formally in team-coordination SOP
- [ ] Add short-OOS auto-flag (< 5 years) to econometrics SOP
- [ ] Update Relevance Matrix with RoC signal preference note

## Architecture Items Surfaced But Not Yet Done
- [ ] Glossary architecture migration: Ray owns `docs/portal_glossary.json`, Ace migrates `glossary.py` to read from it. Currently Ray is editing glossary.py directly as a workaround.
- [ ] Chart filename dedup: both canonical short names (`hero.json`) and legacy prefixed names (`hy_ig_v2_spy_hero.json`) coexist during migration. Cleanup when loader fallback is removed.
- [ ] tournament_winner.json schema defined in team-coordination but not yet produced by all prior pairs — Evan needs to backfill.

## Trade Log UX — Cross-Pair Rollout Needed
The three-layer fix (Evan broker-style CSV + Ace column legend + Ray narrative) is live on HY-IG v2. The 5 other completed pairs still use the old bare-CSV download pattern:
- [ ] hy_ig_spy (sample)
- [ ] indpro_spy
- [ ] sofr_ted_spy / dff_ted_spy / ted_spliced_spy (shared pages)
- [ ] permit_spy
- [ ] vix_vix3m_spy
Reusable script `scripts/synthesize_broker_trade_log.py` is ready; just needs per-pair dispatch of Evan → Ray → Ace.

## Portal Improvements To Consider
- [ ] Auto-generate sidebar FINDINGS list from pair_registry instead of hardcoding
- [ ] Add cross-pair comparison page when 10+ pairs completed
- [ ] Consider template-based pages instead of per-pair files (per appdev SOP guidance for 10+ pairs)
