# Viz Vera — Session Notes

**Project:** AIG-RLIC+
**Session window:** 48-hour continuous run, 2026-04-18 → 2026-04-20
**Agent identity:** Vera (Viz specialist)
**Current branch:** `main`

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
