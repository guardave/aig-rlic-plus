# Research Ray — AIG-RLIC+ Session Notes

**Agent Identity:** Research Ray
**PWS Path:** `_pws/research-ray/`
**Global Profile:** `~/.claude/agents/research-ray/`
**Project:** AIG-RLIC+ (quantitative economics research platform)

## Purpose

This is Ray's ephemeral session journal for the AIG-RLIC+ project. Timeless patterns belong in `~/.claude/agents/research-ray/experience.md`; this file is the chronological working notebook for in-flight work. (`memories.md` retired per LA-7 — all reflection now goes to `experience.md`.)

## Phase 4 SOP fixes — 2026-05-08

**Scope:** Research-Ray-owned edits only. Files changed: `docs/agent-sops/research-agent-sop.md`, `docs/schemas/episode_registry.json`.

### Changes applied

| Finding / LA | Change | Location in SOP |
|---|---|---|
| LA-1 | All `episode_registry.json` references retargeted to `history_zoom_events_registry.json` | RES-HZE1 slug table, slug matching procedure, verification command; RES-20 rule 2; RES-CP1 episode selection; RES-ZOOM1 pre-write checklist |
| LA-2 | Canonical slugs enforced: `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`; `dot_com` and `rates_2022` forbidden | RES-HZE1 field table, example block (`rates_2022` → `inflation_2022`), RES-ZOOM1 episode table (replaced 4-slug deprecated table with 5-slug canonical table), RES-20, RES-CP1 |
| LA-3 | `ZOOM_EPISODE_NARRATIVES` retired; RES-ZOOM1 delivery format now defers to RES-HZE1 `HISTORY_ZOOM_EPISODES` | RES-ZOOM1 Format section rewritten; explicit statement that `ZOOM_EPISODE_NARRATIVES` is retired |
| LA-7 / F-06 | Removed `memories.md` update requirement; consolidated to `experience.md` | Reflection & Memory step 5 |
| F-01 / F-02 | RES-20 rule 2 corrected: episode registry pointer changed from `output/charts/chart_type_registry.json` → `docs/schemas/history_zoom_events_registry.json` | RES-20 rule 2 |
| F-03 | 11 missing Quality Gates checklist items added for RES-11, RES-17, RES-18, RES-20, RES-22, RES-VS, RES-HZE1, RES-CP1, RES-CP2, RES-CPC1, RES-PA3 | Quality Gates section |
| F-04 | RES-CP2 trigger expanded to include `regime_story: true` in `signal_scope.json`; escalation to Evan if files absent | RES-CP2 opening paragraph |
| F-05 | Covered by LA-3 above | — |
| F-07 | Stale RES-OD1 single-line inline script replaced with reference to three-step Wave 10J script (vocabulary + equality + direction_consistent + OD1a stdout requirement + OD1c batch log) | Quality Gates RES-OD1 item |
| F-08 | "How to Read the Trade Log" section upgraded to `### Rule RES-PA3 — How to Read the Trade Log (Blocking)`; four mandatory elements specified without "or equivalent" discretion; Quality Gates item added | RES-PA3 section heading + Quality Gates |
| F-09 | SLA added to RES-ZOOM1 (BLOCKED comment if chart not delivered in current cycle); how-to-determine-VIZ-ZOOM1-trigger procedure added | RES-ZOOM1 |
| F-10 | Structured EGL1 self-check table (6 sub-rules with check and pass condition) added to Quality Gates | Quality Gates EGL1 self-check table |
| F-12 | Formal definition of "narrative instrument reference" added at start of RES-NR1 | RES-NR1 |
| F-13 | Scope statement added to RES-CP1 (applies to all pairs; Light-tier waiver details) | RES-CP1 |
| F-14 | `<!-- OOS_SPAN_TBD: ... -->` fallback added to RES-18 rule 2 | RES-18 |
| C-V2 | Skip-entry check added to RES-HZE1 pre-handoff validation step 5 (check `_meta.json` before filing Vera blocker) | RES-HZE1 |
| C-V3 | `caption` field marked mandatory in RES-HZE1 field table and validation step 4 | RES-HZE1 |
| C-E3 | Parenthetical note added to RES-18 rule 3 distinguishing Ray's "headline" sentence from Evan's "Headline Findings" KPI table | RES-18 |
| C-E4 | Canonical slugs enforced in RES-CP1 episode selection; `history_zoom_events_registry.json` cited as authority | RES-CP1 |
| C-A4 | Stub-check item added to Quality Gates (confirm no "Ray leg pending" strings before Ace handoff) | Quality Gates |

### Schema / registry changes

| File | Change |
|---|---|
| `docs/schemas/episode_registry.json` | Converted to thin pointer: `{"deprecated": true, "canonical": "history_zoom_events_registry.json", "see": "LA-1", "note": ...}`. All data removed. Consumers must retarget to `history_zoom_events_registry.json`. |

### Items NOT addressed (out of scope)

- F-11 / LA-5: `docs/standards.md` registration of new rules — Lead batch update task.
- C-D1, C-D2, C-D3: Dana-owned fixes.
- C-E1, C-E2: Evan-owned fixes.
- C-V1, C-V4: Vera-owned fixes.
- C-A1, C-A2, C-A3: Ace/Lead-owned fixes.
- C-Q1, C-Q2, C-Q3, C-Q4: QA-owned fixes.
- BL-004: Architectural decision deferred; TBD note already in RES-EGL1.

## Session Timeline

### 2026-04-23 — Wave 10I.A Part 3b (TED variants narrative port)
- Filled 111/111 TODO-Ray stubs across 3 TED pair configs (`sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`), 37 stubs each.
- Source retrieval: `git show a9d493e~1:app/pages/6_ted_variants_*.py` per Ace handoff.
- KPI verification: all prose numbers cross-checked against each pair's `results/{pid}/winner_summary.json`. SOFR 1.89 / DFF 0.97 / Spliced 1.19 confirmed.
- Crisis-trade citations: SOFR → COVID recovery trade (+8.8%, largest in log), DFF → GFC Oct-2008 (+10.5%), Spliced → late-Oct-2008 (+10.1%, on pre-splice authentic TEDRATE portion).
- Narrative distribution honours "don't conflate variants" discipline: each variant frames its own purpose (SOFR = modern purist short sample, DFF = long-history proxy, Spliced = continuity with structural assumption). Cross-references in `WHERE_THIS_FITS` orient readers comparing siblings.
- All 3 smoke tests `passes=3 failures=0`.
- Handoff: `results/_cross_agent/handoff_ray_wave10i_partB_20260423.md`.
- No scope bleed (only 3 configs + handoff + PWS + status-board touched); META-AM clean.

### 2026-04-19 — Wave 1 (stakeholder feedback batch)
- Added RES-7 (plain-English signal generation on Strategy), RES-8 (episode cross-references), RES-9 (investor-impact clause), RES-10 (status vocabulary glossary).
- Narrative edits landed on `docs/portal_narrative_hy_ig_v2_spy_20260410.md`.
- Commit: `6bcb5e2` (SOP hardening Part F Wave 1).

### 2026-04-19 — Wave 1.5 (coherence patches)
- Added RES-11 (headline-first Story page structure) and RES-VS (narrative status vocabulary self-check).
- Commit: `b7ee4ba` (Wave 1.5 coherence-review patches).

### 2026-04-14/19 — Wave 2A (reference-pair polish)
- Applied 7 META-RPD polish changes, 3 new 8-element Evidence blocks, bps dual notation, 5 new glossary entries.
- Commits: `6d40af8`, `b9730cb`.

### 2026-04-19 — Wave 4C-2 (narrative_frontmatter schema)
- Authored `docs/schemas/narrative_frontmatter.schema.json` v1.0.0.
- Registered RES-17 (Narrative Frontmatter Contract) — blocking rule in SOP + standards.md.
- Committed glossary SLA (one-week close OR `status=pending_placeholder` in frontmatter).
- Commit: `e28dd3d`.

### 2026-04-19 — Wave 5B-2 (validation-audit rule additions)
- Authored validation audit `docs/validation-audit-20260419-ray.md` identifying 5 reproducibility + 5 stakeholder-resolution gaps.
- Added RES-18 (Headline Template Constraint), RES-20 (Historical-Episode Selection Criterion), RES-22 (Status-Label Assignment Decision Table) — all blocking.
- Commits: `d6e4f02`, `342f48c`.

### 2026-04-19 — Wave 5C (retro-apply sweep)
- Migrated HY-IG v2 narrative to frontmatter block.
- Fixed 8 stale `chart_status: "ready"` tokens → `"Validated"`.
- Grew glossary from 3 → 31 terms.
- Executed key rename: `status_labels` → `_status_vocabulary`.
- Schema bumped to v1.1.0 (adds `selection_rationale` enum + `prose_ref` on historical_episodes_referenced).
- Commit: `f7587a3`.

### 2026-04-19/20 — Wave 7B (Methodology read-only tables)
- Added Methodology page sections rendering `signal_scope.json` (ECON-UD) and `analyst_suggestions.json` (ECON-AS).
- Off-scope references in analytical prose 3 → 0.

### 2026-04-20 — Wave 7C BLOCKER (bystander)
- Quincy caught CCC-BB prose surviving in `.py` page modules, bypassing my cleaned narrative markdown.
- Not my fix to ship. BL-004 filed; Ace owns the architectural rule that all user-facing prose on `.py` pages must flow through `components/narrative.py`.
- Coordination action only.

### 2026-04-20 — Wave 9B (this session — experience + memory catch-up)
- Updated `~/.claude/agents/research-ray/experience.md` with Wave 1-7B timeless patterns.
- Updated `~/.claude/agents/research-ray/memories.md` with wave-by-wave incidents.
- Updated `~/.claude/agents/research-ray/projects/aig-rlic-plus.md` with current rule set + HY-IG v2 narrative state.
- Created this `session-notes.md`.
- No SOP / narrative / glossary edits in this wave (memory-only per constraint).

### 2026-04-20 — Wave 10E (RES-NR1 audit — indpro_xlp)

**Dispatch:** Audit and fix all instrument name references in `app/pair_configs/indpro_xlp_config.py` per Rule RES-NR1 (new, 2026-04-20).

**Confirmed identifiers (from `results/indpro_xlp/interpretation_metadata.json` and `winner_summary.json`):**
- `target_symbol`: XLP (Consumer Staples Select Sector SPDR)
- `indicator`: INDPRO (Industrial Production Index)

**Audit findings:**
- Scanned all narrative prose fields in the config (StoryConfig, CORRELATION_BLOCK, GRANGER_BLOCK, REGIME_BLOCK, EVIDENCE_METHOD_BLOCKS, StrategyConfig, methodology strings)
- **1 GATE-NR violation found:** `StoryConfig.NARRATIVE_SECTION_2` heading: "The Nuance: It Is Not a Perfect Inverse of the S&P 500" — S&P 500 incorrectly named where target is XLP
- 2 comparative references verified as intentional/correct: (a) "broad S&P 500" in NARRATIVE_SECTION_1 body used as explanatory contrast for countercyclical mechanism; (b) "INDPRO × SPY strategy" in CAVEATS_MD used as explicit cross-pair comparison for investor guidance

**Fix applied:**
- `StoryConfig.NARRATIVE_SECTION_2` heading changed to: "The Nuance: XLP Is Not a Mechanical Inverse of the IP Cycle"

**Artifacts updated:**
- `app/pair_configs/indpro_xlp_config.py` — line 139 fixed
- `results/indpro_xlp/qa_verification_20260420.md` — RES-NR1 section appended

**New rule registered:** RES-NR1 — Instrument Name Accuracy (added to memories.md + experience.md)

## Open Follow-Ups
- Monitor BL-004 resolution (Ace's work, not mine) — re-inspect narrative coherence on `.py` pages once architectural fix lands.
- Next pair migration (when Lead dispatches): apply RES-17 frontmatter from the start (not retro), RES-20 triad from the start, RES-18 template choice declared in frontmatter, **and run RES-NR1 instrument audit before handoff**.
- Keep glossary SLA clock running — no open `status=open` entries should age past 7 days without `pending_placeholder` or `closed`.

---
*Last updated: 2026-04-20 — Wave 10E (RES-NR1)*

---

## 2026-04-22 — Wave 10F Cross-Review

**Dispatch:** Cross-review all 6 SOPs + coordination + team-standards stub + changelog. File findings at `_pws/_team/cross-review-20260420-research-ray.md`.

**Deliverable:** `_pws/_team/cross-review-20260420-research-ray.md` — 7 sections (Conflicts, Redundancies, Rules-for-team-standards, Silent-Weakening, Ray-Specific, Vera's 3 Qs, Priority Top-5). ~2000 words, with file:line citations.

**Evidence logged per META-AM / META-SRV:**
- Read: research-agent-sop.md (800+ lines via offset reads), team-coordination.md (first 400 lines), team-standards.md (full), sop-changelog.md (full), plus grep across all SOPs for RES-NR1/RES-17/META-ELI5/META-CF/APP-PT1/narrative-related anchors.
- Write: findings file (this wave's cross-review deliverable).
- Appended: global experience.md (two-authoring-surfaces pattern + silent-weakening audit pattern); global memories.md (Wave 10F cross-review entry).

**Blocked from:** updating `last_seen` file (permission denied in this sandbox); noting here for Lead awareness. The SOD block was completed via read-only inspection; EOD updates to experience/memories/session-notes were permitted.

**PROMOTED 2026-04-22T07:49:45Z** — Experience (86→102 lines) and memories (163→193 lines) updated in `~/.claude/agents/research-ray/` by Wave 10F-EOD promotion pass.

**Top-3 asks of Lead (from my findings section 7):**
1. Decide `.py` vs `.md` narrative authoritative surface (blocks RES-17 teeth).
2. Amend VIZ-IC1 to write narrative-alignment note into `_meta.json` (not `_manifest.json`).
3. Extend `validate_schema.py` to cross-check frontmatter against chart/glossary/episode registries.

---
*Last updated: 2026-04-22 — Wave 10F cross-review*

---
## Session: Wave 10G.4B — 2026-04-22

**Task:** Build fresh research/narrative layer for new `hy_ig_spy` pair.

**Status: COMPLETE**

**Deliverables committed (1561370):**
- `docs/portal_narrative_hy_ig_spy_20260422.md` — 423 lines, all 4 pages, 3 crisis episodes, regime_context callouts
- `docs/research/hy_ig_spy_narrative_prose_20260422.md` — 364 lines, Python-string-ready prose for Ace's pair_config
- `docs/event_timeline_hy_ig_spy_20260422.csv` — 37 rows, 2000-2025
- `results/hy_ig_spy/handoff_ray_20260422.md` — RES-NR1 PASS, META-RYW complete

**RES-NR1:** PASS — target_symbol = SPY throughout; no wrong-pair tickers.

**META-RYW:** Complete — re-read all deliverables end-to-end before commit.

**Dana contract assumption:** interpretation_metadata.json for hy_ig_spy not yet written (parallel pipeline). Contract values assumed from hy_ig_v2_spy: target_symbol="SPY", indicator="hy_ig_spread", direction=countercyclical. Handoff note flags this explicitly.

**Pushed to remote:** yes (main branch, commit 1561370)

**Outstanding:** None from Ray's scope. Ace (4E), Vera (4C), Evan (4D) complete the pipeline.

---
## Session: Wave 10H.2 — 2026-04-23 — APP-TL1 narrative fill

**Task:** Replace Ace's 4 `# TODO Ray` stubs in `page_templates.py` with canonical APP-TL1 prose; add `TRADE_LOG_EXAMPLE_MD` to 3 pair configs.

**Status: COMPLETE (2 of 3 pair configs — 3rd flagged to Lead).**

**Deliverables:**
- 4 narrative constants authored (disclosure, two-file model, column glossary, 10-row column dict).
- 2 pair configs enriched with `TRADE_LOG_EXAMPLE_MD` (hy_ig_spy, indpro_xlp) — both anchored on COVID 2020 transitions with verifiable broker-CSV rows.
- 1 pair config (umcsent_xlv) flagged NOT to create — page hand-rolled, bypasses render_strategy_page; would be orphan code.
- Smoke: 4/4 pairs PASS failures=0.
- Handoff: `results/_cross_agent/handoff_ray_wave10h2_20260423.md`.

**Flags to Lead:**
1. umcsent_xlv's strategy page is outside APP-PT1 template flow; open `BL-APP-PT1-UMCSENT` before extending APP-TL1 coverage there.
2. `results/hy_ig_spy/winner_trades_broker_style.csv` still on legacy 12-col schema; dispatch Evan/Dana to regenerate per APP-TL1 canonical 10-col schema (does not block Ray's prose but breaks UX consistency of Ace's column-dictionary expander).

**Cross-agent coordination:** Purely downstream of Ace's 10H.2 structural commit `a32eaff`. No interaction with Vera/Evan/Dana this wave.

**LEAD-DL1:** Honoured — only touched Ray-owned files (narrative constants, pair config narrative fields, handoff, PWS, team status).

---
## Session: Wave 10I.A Part 3a — 2026-04-23 — narrative port for 4 non-TED pairs

**Task:** Replace all TODO-Ray stubs in the 4 non-TED pair configs Ace migrated in Wave 10I.A Part 1.

**Status: COMPLETE.**

**Deliverables:**
- 190 TODO-Ray stubs filled (indpro_spy 65, permit_spy 37, vix_vix3m_spy 37, umcsent_xlv 51). Zero remaining.
- Smoke tests: 16 passes / 0 failures across the 4 pairs.
- Source: legacy `app/pages/{N}_{pair}_*.py` via `git show 24e2f16~1:...`; ported, lightly edited, META-ELI5 compliant.
- TRADE_LOG_EXAMPLE_MD per pair:
  - indpro_spy — 2020 COVID cash anchor (672 days cash 2019-03 → 2021-01).
  - permit_spy — 2008 GFC short (+26.65% over 123 days) with honest whipsaw commentary.
  - vix_vix3m_spy — 2020 COVID cash 2020-01-24 → 2020-04-03 then long +36.09% over 186 days.
  - umcsent_xlv — 2020-02-29 broker-CSV entry (BUY XLV at $83.70, UMCSENT YoY +7.676%, cum P&L +14.25%).
- Handoff: `results/_cross_agent/handoff_ray_wave10i_partA_20260423.md`.

**KPI cross-check (Ace's flag resolved):** All 4 pairs' `_TOURNAMENT_DESIGN_MD` numbers from `docs/pair_execution_history.md` matched the authoritative `winner_summary.json`. No corrections required. Enriched each design table with additional JSON fields (Sortino, Calmar, win rate, turnover, breakeven-cost where present).

**Flags to Lead:**
1. Only `umcsent_xlv` has the canonical broker-style CSV (APP-TL1). The other three pairs use legacy 5-column `winner_trade_log.csv`. Candidate for Vera/Dana dispatch.
2. `permit_spy` and `vix_vix3m_spy` lack `equity_curves`/`drawdown`/`walk_forward` charts on disk (pre-existing; Ace flagged this in Part-1).
3. Chart-filename drift remains (`indpro_spy_hero.json` vs bare `hero.json`). Candidate for Vera cleanup.

**LEAD-DL1:** Honoured — only touched Ray-owned narrative fields in pair configs, handoff doc, PWS, and team status.

---
## Session: Wave 10I.C — 2026-04-23 — Adversarial audit self-review and FAIL-05 fix

**Task:** Read Quincy's full-coverage adversarial DOM audit, own the failures in Ray's domain, fix what is fixable, update SOP and experience.

**Status: COMPLETE (Ray-owned fixes done; out-of-scope failures documented below).**

### What I owned

**FAIL-05 (BLOCKING) — APP-DIR1 L1 error banners on 4 Strategy pages.**

Root cause: During Wave 10I.A backfill of `interpretation_metadata.json` for 6 legacy pairs, I preserved the pre-existing `observed_direction` values verbatim without cross-checking them against `winner_summary.json.direction`. Four values were wrong:

| Pair | winner_summary.direction | old observed_direction | fixed |
|------|-------------------------|----------------------|-------|
| indpro_spy | procyclical | countercyclical | to procyclical, direction_consistent true |
| vix_vix3m_spy | countercyclical | procyclical | to countercyclical, direction_consistent true |
| sofr_ted_spy | countercyclical | procyclical | to countercyclical, direction_consistent true |
| dff_ted_spy | countercyclical | procyclical | to countercyclical, direction_consistent true |

**Fixes applied:** All 4 `interpretation_metadata.json` files corrected. Smoke tests: 4/4 pairs 0 failures after fix.

**SOP updated:** Added Rule RES-OD1 (observed_direction cross-check, blocking) to Quality Gates checklist and Defense 2 section of `docs/agent-sops/research-agent-sop.md`.

### Experience lesson (for manual promotion to experience.md)

**2026-04-23 — Wave 10I.C: backfill passes must cross-check observed_direction against winner_summary.direction (RES-OD1)**

During the Wave 10I.A backfill, I preserved `observed_direction` verbatim from legacy files. Four of those values disagreed with `winner_summary.json.direction` (the tournament ground truth), triggering APP-DIR1 L1 error banners on 4 Strategy pages. These were stakeholder-visible but missed by structural smoke tests (which only catch Python tracebacks, not content banners).

Root cause: "preserve verbatim" is not safe for `observed_direction` during schema migration. Rule RES-OD1 now mandates: read `winner_summary.json.direction` first, set `observed_direction` to match, recompute `direction_consistent`, run the 1-line Python assert before commit.

### What is NOT mine to fix (flagged to Lead/Ace)

**FAIL-06** ("Ray leg pending RES-17 frontmatter migration" caption on 8 Strategy pages) — internal dev note hard-coded in `app/components/direction_check.py:197-200` leaking to stakeholders. Ace should replace with "Direction check: Evan and Dana agree on `{direction}`."

**All other FAILs** (FAIL-01 through FAIL-04, FAIL-07 through FAIL-10) — owned by Ace and/or Evan per Quincy's audit table.

---

## Session: Wave 10J / 10K — 2026-04-24 — Self-Reflection + HZE1 Retro-Apply

### Self-Reflection Round (Wave 10J Phase 1)

Participated in team-wide self-reflection. My two real failures this wave were design failures:
1. **RES-OD1 equality-check-only design** — assumed if two files agreed, both were correct. Vera's vocabulary challenge exposed that both inputs can be wrong while agreeing. Conceded in full and specified the three-step fix.
2. **SOP operational inconsistency** — my SOP required both `memories.md` and `experience.md` while every other agent uses only `experience.md`. Executed my own SOP correctly for multiple waves without noticing the inconsistency — surfaced only by external debate.

**Top lesson:** after authoring any SOP rule, apply the meta-question — "can this rule pass while the underlying reality is wrong?" — and audit your own SOP's operational conventions against the other agents' SOPs at every self-reflection, not only during formal cross-review waves.

### Wave 10J Phase 2-4: Rule Set Finalization

New rules confirmed and committed: VIZ-HZE1, RES-HZE1, ACE-HZE1, GATE-HZE1, LEAD-QF1, META-CPD.

### Wave 10J Phase 5: Episode Registry Design & Implementation

Designed and authored `docs/schemas/episode_registry.json` — canonical source of truth for all historical crisis episodes across all pairs. Episodes covered: GFC 2008, COVID 2020, Taper 2013, China Shock 2015, Euro Crisis 2011, Volcker 1980s, COVID Recovery 2021, Russia-Ukraine 2022.

**Pair reclassification confirmed:** `dff_ted_spy` + `sofr_ted_spy` → rates class; `ted_spliced_spy` → credit class (LIBOR-era ancestry). Wave 10J Phase 5 final verify: 60/60 PASS. Wave APPROVED.

### HZE1 Retro-Apply (Wave 10K)

Authored HISTORY_ZOOM_EPISODES narratives for all 8 deployed pairs across all pair classes. RES-20 triad verified for all 8 (3 episodes each, correct pair-class selection, prose cross-references to Methodology page). META-CPD cross-reference added (commit `00f27d9`).

Handoff: `results/_cross_agent/handoff_ray_hze1_retro_20260424.md`

---
*Last updated: 2026-04-24 — Wave 10J/10K checkpoint*

---

## Session: 2026-05-08 — Phase 1 Intra-SOP Review

**Task:** Read and review own SOP for completeness, internal consistency, definition gaps, coverage gaps, cross-reference validity, severity consistency, and stale items. No edits to SOP permitted this phase (LEAD-DL1).

**Status: COMPLETE.**

**Deliverable:** `_pws/research-ray/sop_review_phase1_intra_20260508.md`

**Findings summary:**
- 14 findings total: 5 FAIL (blocking), 9 WARN (non-blocking)
- FAIL items: F-01 (slug namespace mismatch dot_com vs dotcom / rates_2022 vs inflation_2022), F-02 (RES-20 wrong registry file pointer), F-03 (Quality Gates missing 9+ rule items), F-05 (RES-ZOOM1 vs RES-HZE1 config attribute conflict), F-07 (OD1 checklist item stale vs Wave-10J tightening)
- WARN items: F-04 (RES-CP2 trigger mismatch vs ECON-CP2), F-06 (memories.md still required), F-08 (RES-PA3 not in quality gates), F-09 (RES-ZOOM1/RES-8 missing SLA + trigger verification), F-10 (RES-EGL1 gate entry too thin), F-11 (9 rules not in standards.md), F-12 (narrative instrument undefined), F-13 (RES-CP1 scope unstated), F-14 (RES-18 missing file-absent escalation)

**Top-3 themes:**
1. Quality Gates checklist is significantly under-populated — 9+ blocking rules added since Wave 5B-2 have no corresponding gate items.
2. Episode slug namespace fragmentation — two independent slug naming conventions (with/without underscore; rates_2022 vs inflation_2022) create pipeline compatibility failures across Ray→Vera→Ace.
3. Rule supersession ambiguity — RES-ZOOM1 and RES-HZE1 appear to govern the same config delivery with different attribute names; one may be stale.

**LEAD-DL1:** Honoured — only touched `_pws/research-ray/sop_review_phase1_intra_20260508.md`, `_pws/research-ray/session-notes.md`, and `_pws/_team/status-board.md`.

---
*Last updated: 2026-05-08 — Phase 1 intra-SOP review*
