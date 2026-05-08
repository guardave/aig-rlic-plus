# Viz Vera — Session Notes

**Project:** AIG-RLIC+
**Session window:** 48-hour continuous run, 2026-04-18 → 2026-04-20
**Agent identity:** Vera (Viz specialist)
**Current branch:** `main`

## 2026-05-08 — Phase 4 SOP Fixes

**Task:** Apply Phase 1/3/Lead Phase 2 findings to own SOP and owned schemas. Critical LA-1/LA-2 registry consolidation work.

### Files Changed

| File | Change |
|------|--------|
| `docs/agent-sops/visualization-agent-sop.md` | 15 finding fixes (F-01 through F-15 minus F-08) + 8 cross-SOP fixes |
| `docs/schemas/history_zoom_events_registry.json` | v1.0.0 → v1.1.0: added `indicator_category_map` (LA-1), added `china_2015` episode (LA-2) |
| `docs/schemas/history_zoom_events_registry.schema.json` | Added `indicator_category_map`, `x-revised`, `x-revision-notes` properties |
| `docs/schemas/color_palette_registry.json` | v1.1.0 → v1.2.0: added `matplotlib_legacy` named exception palette (F-14) |

### Finding Resolution Log

| ID | Status | Action |
|----|--------|--------|
| F-01 | FIXED | Replaced stale matplotlib palette table with pointer to `okabe_ito_2026` in registry |
| F-02 | FIXED | Added `_comparison/` scoping carve-out in VIZ-V11 lint preamble + §8 Deliver |
| F-03 | FIXED | Deleted "Unlike earlier phrasing in VIZ-DP1..." ghost sentence from Rule V5 |
| F-04 | FIXED | Added check 7 to VIZ-IC1: source/visible-provenance in chart text |
| F-05 | FIXED | Covered by LA-1/LA-2 work (episode_registry → history_zoom_events_registry; taper_2018 added to ZOOM1/HZE1; china_2015 promoted) |
| F-06 | FIXED | Replaced META-RYW with META-QS; QA-CL6/GATE-NC with QA-CL1 in VIZ-IC1 cross-refs |
| F-07 | FIXED | Removed stale self-flagging note; added note that Lead handles standards.md registration (LA-5) |
| F-08 | OUT OF SCOPE | standards.md gate registration — Lead Phase 4b |
| F-09 | FIXED | Added `equity_curves.json` to VIZ-DP1 `dual_panel_patterns` |
| F-10 | FIXED | Clarified .json/.log skip-condition prose in Rule V5 |
| F-11 | FIXED | Added `scripts/viz_v11_palette_lint.py` reference + confirmed VIZ-IC1 check 4 as current implementation vehicle |
| F-12 | FIXED | Corrected Indicator Evaluation Framework filenames to `env_radar.json`, `strategy_radar.json` |
| F-13 | FIXED | Added Key Definitions section after Identity block |
| F-14 | FIXED | Added `matplotlib_legacy` to color_palette_registry.json; updated SOP text to confirm registry registration |
| F-15 | FIXED | Covered by LA-1 (registry consolidation); episode_registry.json references in VIZ-ZOOM1/VIZ-HZE1 replaced |

### Cross-SOP Fixes (Vera's lane)

| ID | Action |
|----|--------|
| C1-D03 | Added reciprocal Dana Rule D2 cross-reference to VIZ-A2 header |
| C1-E03 | Added data-coverage vs upstream-blocked skip distinction in VIZ-HZE1 |
| C1-R04 | Added chart_status canonical vocabulary guard in chart-gap requests section |
| C1-R05 | Added registry scope note in VIZ-V12 distinguishing from chart_type_registry |
| C1-A01 | Added downstream consumer protocol note in VIZ-HZE1 for Ace ACE-HZE1 |
| C1-A03 | Confirmed APP-PT2 cross-reference note in VIZ-E1 |
| C1-A04 | Added caption audience_tier note in VIZ-E1 (VIZ-A5 clarification) |
| C1-Q02 | Added GATE-27 severity note in Rule V5 gate section |

### LA-1/LA-2 Registry Consolidation (canonical — unblocks Ray, Evan, Quincy retargeting)

- `history_zoom_events_registry.json` is now the single canonical episode registry (LA-1 confirmed).
- Added `indicator_category_map`: per-category slug lists for VIZ-HZE1/RES-HZE1 (satisfies LA-1 keying requirement).
- Canonical slug set: `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`, `china_2015` (category-scoped).
- `china_2015` promoted to canonical: 3 production pairs have `suggested` charts on disk.
- `ukraine`: zero production charts; non-canonical status documented in registry notes and SOP.
- All `episode_registry.json` references in VIZ-ZOOM1, VIZ-HZE1, VIZ-V1 replaced with `history_zoom_events_registry.json`.
- Non-canonical slug variants (`dot_com`, `rates_2022`, `taper_2013`, `taper`) explicitly prohibited in SOP.

---

## 2026-05-08 — Phase 3 Cross-SOP Review

**Task:** Review five peer SOPs (Dana, Evan, Ray, Ace, Quincy) from a handoff perspective. No peer SOP edits (LEAD-DL1). Output: `_pws/viz-vera/sop_review_phase3_cross_20260508.md`.

**Status-board EOD line:** Phase 3 cross-review: 21 findings (8 FAIL, 13 WARN), file: `_pws/viz-vera/sop_review_phase3_cross_20260508.md`.

---

## 2026-05-08 — Phase 1 Intra-SOP Review

**Task:** Review own SOP for completeness, self-consistency, definition gaps, coverage gaps, cross-reference validity, and severity consistency. No edits to SOP (LEAD-DL1 binding).

**Findings file:** `_pws/viz-vera/sop_review_phase1_intra_20260508.md`

**Summary:**
- 15 findings total: 3 FAIL, 12 WARN.
- FAIL-01: Stale matplotlib palette table directly contradicts VIZ-V11 (blocking lint violation).
- FAIL-02: `output/_comparison/` still referenced for live chart saves despite META-AL prohibition for zoom charts — ambiguous scope for comparison charts.
- FAIL-05: Episode slug names inconsistent across VIZ-V1, VIZ-ZOOM1, VIZ-HZE1 (dotcom vs dot_com; taper_2018 absent from ZOOM1; ukraine produced but not registered).
- Key WARN themes: unregistered VIZ-IC1, dangling META-RYW/QA-CL6/GATE-NC cross-references, VIZ-V11 grandfather clause potentially contradicting VIZ-CV1, episode_registry.json vs history_zoom_events_registry.json naming ambiguity, equity_curves.json missing from VIZ-DP1 batch check.
- Strengths preserved: VIZ-DP1 inline code, VIZ-HZE1 skip protocol, three-pathway handoff model, VIZ-O1 disposition mandate, VIZ-V13 annotation strategies.
- 6 items deferred to Phase 3 cross-review (slug naming with Quincy, APP-PT2 definition gap with Ace, ukraine episode registry question for Lead).

**No SOP edits made (LEAD-DL1 respected).**

---

## Wave 10H.1 Session — 2026-04-22

**Task:** VIZ-O1 (disposition mandate) + VIZ-E1 (exploratory sidecar spec) first implementation.

**Delivered:**
1. `scripts/backfill_chart_dispositions.py` — idempotent migration. First run: `{"consumed":62,"suggested":3,"unchanged":0,"errors":0}`. Rerun: all 65 unchanged.
2. `results/hy_ig_v2_spy/analyst_suggestions.json` — added top-level `exploratory_charts` key (3 entries) alongside Evan's existing `suggestions` array (LEAD-DL1 shared-file split honoured).
3. Generator updates: `generate_charts_hy_ig_spy.py`, `retro_fix_hy_ig_v2_vera_20260411.py`, `generate_charts.py` — now emit `"disposition": "consumed"` on future runs. Four other per-pair generators have no sidecar-writer function to patch — flagged as follow-up refactor candidate.

**ELI5 authorship:** 3 orphan charts each got a 3-4 sentence plain-English caption (no jargon, no model names) + a one-line analyst rationale. Lead earlier flagged the audit on these three; now surfaced through the Methodology-page Exploratory Insights section rather than deleted.

**Handoff:** `results/_cross_agent/handoff_vera_wave10h1_20260422.md`. Parallel: Ace implementing APP-PT2 consumer — both commits are backward-compatible either order.

**Learning:** the dispatch said "65 sidecars" but the glob `output/charts/*/plotly/*_meta.json` currently matches exactly 65 across 5 pair dirs (the 19 files under `metadata/` are outside that glob — they're an older convention and will be handled in a future wave if needed).

## Wave 10F Session — 2026-04-22

**Task:** Complete HY-IG v2 bare-name migration (deferred from commit 3c6bb50).
**Outcome:** 12 charts + 12 _meta.json sidecars renamed via `git mv`. No conflicts found. Zero consumer code hits on prefixed chart names. Smoke tests: hy_ig_v2_spy 15/0, indpro_xlp 8/0, umcsent_xlv 7/0. Committed 27fb01f and pushed.
**Flagged for audit:** `hero_spread_vs_spy`, `spread_history_annotated`, `tournament_sharpe_dist` — zero references in consumer code, possibly stale.
**Unblocked:** Ace can now remove the loader fallback (Wave 10F item 6).

wc -l evidence (pre-session): experience.md 87L, memories.md 88L, session-notes.md 109L.

## Session Summary

This session covered Waves 3 through 7B of the HY-IG v2 reference-pair hardening, plus the Wave 9B memory-catch-up that produced this file. The common thread: **converting prose-specified visual conventions into machine-readable contracts with perceptual validation gates**, and **retro-applying those contracts to the reference pair** so future pairs inherit a clean template.

## Commits with Vera-Touched Files (recent)

| Commit | Description | Vera touch |
|--------|-------------|-----------|
| `a2f6570` | Wave 7: ECON scope discipline — filter correlation heatmap to pair derivatives | Regenerated `correlation_heatmap.json`, renamed title to "HY-IG Derivatives vs SPY Forward Returns", added `signal_scope_ref` to sidecar. |
| `fbb834a` | Wave 6D: dual-panel zooms verified on Cloud + META-FRD escalation | Perceptual verification of the Wave 6B dual-panel rebuilds on Streamlit Cloud. |
| `17a73ce` | Wave 6: QA role + META-AL/SRV + dual-panel zoom retro-fix | Rebuilt 3 zoom charts as dual-panel per META-AL; deleted 3 old single-panel canonical files from `output/_comparison/`. |
| `049fa3f` | Wave 5D: Cloud verification PASS after manual Reboot + late artifacts | Cloud verification of Wave 5C retro-apply. |
| `f7587a3` | Wave 5C: retro-apply 24 new Wave-5B rules to HY-IG v2 | Migrated 6 HY-IG v2 chart JSONs to `okabe_ito_2026` palette + registered events + named annotation strategies; palette lint passes; smoke 10/10. |
| `342f48c` | Wave 5B: 24 new rules + 10 new schemas/registries from validation audits | Authored VIZ-V11, V12, V13 + `color_palette_registry.json` + `history_zoom_events_registry.json` + schemas + examples. |
| `d6e4f02` | Wave 5 validation audits | Reviewed `docs/validation-audit-20260419-vera.md` — 3 HIGH-severity reproducibility gaps flagged that became V11 / V12 / V13. |
| `519d042` | SOP Part F Wave 3: gate fixes + retro-apply (stakeholder bugs) | Revised VIZ-V2 (NBER alpha 0.20–0.28, subplot rule, META-PV perceptual check); authored V3 (no silent fallbacks), V4 (no silent drops), V5 (smoke test). |

## Wave-by-Wave Summary

**Wave 3** — Stakeholder review surfaced SL-2 (NBER shading imperceptible on HY-IG v2 hero) and S18-8 / S18-11 (silent chart drops + silent fallbacks). Revised VIZ-V2 alpha prescription; added VIZ-V3, V4, V5. First chart-level rebuild of the hero (perceptible shading + caption disclosure + annualized-return callout + subplot coverage on both panels).

**Wave 5B-2** — Authored the three registry-backed rules (V11 palette, V12 events, V13 annotation strategies). Bootstrapped both registries with the `okabe_ito_2026` palette and the 5-episode event set. All schemas validated exit-0.

**Wave 5C** — Retro-applied the three new rules to 6 existing HY-IG v2 chart JSONs via in-place JSON mutation. Declared methodological divergence from v1 (which shipped matplotlib defaults) in the regression note. Palette lint passes; smoke 10/10; perceptual PNGs regenerated.

**Wave 6B** — META-AL (abstraction-layer discipline) killed the canonical-rendered-chart fallback. Rebuilt 3 zoom charts as dual-panel (indicator on top, target on bottom, shared x-axis, markers + shading on both panels). Deleted 9 files from the now-defunct `output/_comparison/` tier. Perceptual PNGs confirm dual-panel structure.

**Wave 7B** — Evan's scope-discipline rule (ECON-SD) required me to drop 5 off-scope traces (NFCI, Bank/Small-Cap, Yield Curve 10y-3m, BBB-IG, CCC-BB) from the correlation heatmap and honestly rename the title. Sidecar now records `signal_scope_ref` + `off_scope_signals_removed` list for audit.

**Wave 9B (this dispatch)** — Memory catch-up. Updated global `experience.md` (timeless patterns), global `memories.md` (specific incidents), project file `aig-rlic-plus.md` (current VIZ rule set + HY-IG v2 chart inventory), and authored this session-notes file.

## Key Cross-Agent Coordination

- **Evan (Wave 7A)** authored ECON-SD + signal_scope.json — I consumed it in Wave 7B to filter the heatmap.
- **Ray** flags historical episodes in narrative; I render the dual-panel zoom per episode. Ray may propose registry additions via PR; I own the merge + `x-version` bump.
- **Ace** consumes my chart JSONs via `load_plotly_chart("{chart_type}", pair_id="{pair_id}")`. Filename canon is rigid: `output/charts/{pair_id}/plotly/{chart_type}.json` — pair_id is in the path only.
- **Quincy (QA)** runs GATE-24, GATE-25, GATE-27, GATE-29, GATE-31 against my deliveries. VIZ-V5 smoke log + perceptual PNG sidecars are required before handoff.

## Open Items for Next Session

- **Legacy pair-id-prefixed filenames** (e.g., `hy_ig_v2_spy_correlation_heatmap.json`) still exist alongside the canonical `correlation_heatmap.json`. They are audit-trail residues from earlier runs and do not block the loader; housekeeping question for central commit decision.
- **`output/_comparison/` directory** is empty post-Wave-6B but still exists. Directory removal left for Quincy/central commit.
- **Ray's GFC 2-sigma band overlay candidate** (flagged low-priority in Wave 2 coherence review) — produce only if stakeholder upgrades priority.
- **RES-20** (Ray's episode-selection criterion) remains pending; new episodes proposed via PR against `history_zoom_events_registry.json`.
- **kaleido deprecation warnings** during perceptual-check PNG rendering — upstream upgrade is a separate track.

---
*Written: 2026-04-20 (Wave 9B memory catch-up)*

---

## 2026-04-24 — Wave 10J/10K Checkpoint

**Identity:** Viz Vera (viz-vera)
**Wave context:** 10J self-reflection + 10K retro-apply

### Contributions

1. **VIZ-HZE1 rule authored** — new pre-handoff gate in `docs/agent-sops/visualization-agent-sop.md`. Mandates `git ls-files` verification per required zoom slug before dispatch; structured skip protocol for data-coverage gaps (`_meta.json` with `"skip": true`). Fills the structural blind spot where SOP had no production enumeration gate.

2. **29 history_zoom charts generated** across 8 pairs (commit `20669d9`):
   - `dff_ted_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `hy_ig_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `indpro_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `indpro_xlp` — 3 charts (gfc, covid, taper — ukraine omitted: no SPY divergence)
   - `permit_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `sofr_ted_spy` — 3 charts (covid, taper, ukraine — gfc skip: SOFR data starts 2018)
   - `ted_spliced_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `umcsent_xlv` — 3 charts (gfc, covid, taper)
   (31 `_meta.json` sidecars also generated)

3. **vix_vix3m_spy dot_com skip** (commit `2f15547`) — `history_zoom_dot_com_meta.json` structured skip entry; VIX3M data starts 2007, predates dot-com episode 1999-2002. Documented skip.

4. **META-CPD cross-reference** (commit `da8f534`) — added cross-reference to META-CPD in Viz Vera SOP deployment rules section.

5. **Experience entry promoted** to `~/.claude/agents/viz-vera/experience.md` — failure mode class: "SOP rule without production enumeration gate."

### Documented skips
| Pair | Episode | Reason |
|------|---------|--------|
| sofr_ted_spy | gfc | SOFR data starts 2018 (post-GFC) |
| vix_vix3m_spy | dot_com | VIX3M data starts 2007; episode 1999-2002 |

### Wave 10J Phase 5 Quincy verify result
60/60 PASS — wave APPROVED (all 10 pairs × 6 gates per pair).

### Outstanding item flagged
- **Perceptual PNGs (kaleido renders):** only `hy_ig_v2_spy` has them. 9 other pairs at WARN. Lead decision pending on whether to assign a wave target for backfill.

*Written: 2026-04-24 (Wave 10J/10K checkpoint)*

---

## 2026-04-22 — Wave 10F Cross-Review Dispatch

**Task:** Cross-review all team SOPs from viz perspective; deliver authoritative answers to the three open questions that triggered this wave (filename convention, sidecar naming, palette aliases).

**Deliverable:** `_pws/_team/cross-review-20260420-viz-vera.md` (240 lines, ~2650 words, 7 sections).

**Key recommendations:**
1. Bare-name filenames are canonical; migrate indpro_xlp + umcsent_xlv (20 renames) and delete HY-IG v2 prefixed duplicates (13 deletes). Add producer-side pre-commit enforcement.
2. `_meta.json` for charts, `_manifest.json` for datasets — distinct classes, stay distinct. Fix VIZ-IC1 §6 `_manifest.json` → `_meta.json` (drafting slip). Create `docs/schemas/chart_sidecar.schema.json`.
3. Add `aliases` block (`indicator`/`target`/`benchmark` → canonical keys) to `color_palette_registry.json`. Do not rewrite VIZ-IC1; the two-level semantic/visual split is the point.

**Additional findings flagged:** VIZ-IC1 ships as silent no-op today (schema gaps); `matplotlib_legacy` grandfather clause vs VIZ-V5 smoke rule contradiction; `chart_manifest.json` index documented but not on disk; indpro_xlp + umcsent_xlv have zero `_meta.json` sidecars.

**Top-5 priority fixes:** (P1) filename migration, (P2) palette aliases, (P3) VIZ-IC1 §6 fix + sidecar schema, (P4) `scripts/viz_ic1_check.py` reference impl, (P5) sidecar retro-apply for the two prefixed pairs.

**Evidence:** `wc -l _pws/_team/cross-review-20260420-viz-vera.md` → 240. META-AM updates: global experience.md appended (3 new patterns), memories.md appended (Wave 10F-CR incident), this file appended. Global `last_seen` updated to 2026-04-22T00:00:00Z.

**PROMOTED 2026-04-22T00:00:00Z** — experience.md: 65→79 lines (+3 patterns). memories.md: 51→70 lines (+1 incident block).

---

## 2026-04-22 — Wave 10F Filename Migration Session

**Identity:** Viz Vera (viz-vera)
**SOD performed:** Yes — read sod.md, team-standards.md §2.1/§3/§4, sop-changelog.md, experience.md, memories.md.

### Phase-by-phase counts

| Phase | Action | Count |
|-------|--------|-------|
| 1 | HY-IG v2 pair-prefixed duplicates deleted (git rm) | 5 |
| 2a | indpro_xlp charts renamed to bare-name (git mv) | 10 |
| 2b | umcsent_xlv charts renamed to bare-name (git mv) | 10 |
| 3 | _meta.json sidecars created | 32 |
| 3 | _meta.json sidecars pre-existing (skipped) | 10 |
| + | Consumer files updated (pages + config + smoke_loader) | 5 |
| 4 | Smoke tests: hy_ig_v2_spy passes | 15/0 |
| 4 | Smoke tests: indpro_xlp passes | 8/0 |
| 4 | Smoke tests: umcsent_xlv passes | 7/0 |

### Commit
- SHA: 3c6bb50
- 65 files changed, +516/-34
- Pushed to remote main

### Key finding
Consumer-side references (portal pages, pair config class attributes, smoke_loader registry) are not updated by `git mv`. All 5 consumer files required explicit sed updates to pass smoke tests. This is now documented in experience.md as a mandatory migration step.

### wc -l evidence (META-AM)
- experience.md: 79 → 93 lines
- memories.md: 70 → 103 lines

---

## Session: 2026-04-22 Wave 10G.4D — Fresh hy_ig_spy 22-Chart Suite

### Identity
Agent: Viz Vera | Pair: hy_ig_spy | Wave: 10G.4D

### Task
Produce Sample-parity 22-chart suite for fresh `hy_ig_spy` pair (bare pair_id, Wave 10G.4C Evan outputs at fb49123).

### Completed

| Step | Item | Count |
|------|------|-------|
| 1 | Chart generation script written | 1 script (~500 lines) |
| 2 | Charts produced | 23 (22 required + 1 bonus) |
| 3 | _meta.json sidecars | 23 |
| 4 | VIZ-V5 smoke: hy_ig_spy | 23/23 PASS |
| 5 | smoke_loader: hy_ig_v2_spy | 15/0 PASS |
| 5 | smoke_loader: indpro_xlp | 8/0 PASS |
| 5 | smoke_loader: umcsent_xlv | 7/0 PASS |
| 6 | Handoff vera_20260422.md | written |
| 7 | Commit + push | c525470 |

### Data Sources Used
- Master: `data/hy_ig_spy_daily_20000101_20260422.parquet` (6,863 × 50 cols)
- Signals: `results/hy_ig_spy/signals_20260422.parquet` (17 cols)
- Models: `core_models_20260422/`, `exploratory_20260422/`, `tournament_validation_20260422/`
- Events: `docs/event_timeline_hy_ig_spy_20260422.csv` (Ray)
- Winner: S6_hmm_stress / T4_hmm_0.5 / P2 / L0 → OOS Sharpe 1.41

### Key decisions
- `regime_quartile_returns` produced from `results/hy_ig_spy/regime_quartile_returns.csv` (separate from `quartile_returns` which adds vol overlay)
- `transfer_entropy` computed inline (no pre-built artifact) via rolling conditional correlation proxy
- `walk_forward` filtered rank==1 only to get winner series

### wc -l evidence
- memories.md: ~119 lines (before 94 → after ~119)
