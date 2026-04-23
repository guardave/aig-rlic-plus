# Ace Session Notes -- AIG-RLIC+ (HY-IG v2 reference pair)

**Agent Identity:** Ace (role=appdev)
**PWS Path:** `_pws/appdev-ace/`
**Global Profile:** `~/.claude/agents/appdev-ace/`
**Current project:** aig-rlic-plus
**Reference pair:** hy_ig_v2_spy

## Session timeline (Wave-by-wave)

### Wave 2B -- HY-IG v2 reference-pair polish (2026-04-14)
- Authored breadcrumb component; 5 UX changes on the 4 HY-IG v2 pages.
- Rule IDs applied: N10-N13, META-PWQ, META-RPD, APP-AF3, APP-EP1, APP-PA1, APP-RP1.

### Wave 2B portal rebuild (2026-04-19)
- 4 HY-IG v2 pages rebuilt per APP-SE1..SE5 + META-ZI loader + Status Vocabulary Discipline.
- Trigger-card sparklines shipped (stylised at this point -- real-data rewrite came in Wave 5C).

### Wave 3 -- Loader bug fix (2026-04-19)
- Fixed "Dot-Com zoom chart pending" bug: `load_plotly_chart` made to return `Figure`; parse errors surfaced via `st.warning`.
- Authored APP-ST1 (Loader End-to-End Smoke Test) and co-authored GATE-27 / GATE-28.
- `app/_smoke_tests/smoke_loader.py` created.

### Wave 4D-2 -- Consumer-side schema integration (2026-04-19)
- `app/components/schema_check.py` created and wired into `probability_engine_panel.py`, `direction_check.py`, `live_execution_placeholder.py`.
- Retired `_SIGNAL_CODE_TO_COLUMN` (40+ LoC).
- Authored APP-WS1, APP-SEV1, APP-DIR1 SOP rules.
- First production APP-DIR1 run: Evan=countercyclical, Dana=countercyclical -- agreement.

### Wave 5B-2 -- Rule authoring (2026-04-19)
- Authored 4 new APP rules: APP-CC1 (caption prefixes), APP-EX1 (expander titles), APP-URL1 (slug pins), APP-CH1 (non-method chart registry).
- 3 new schemas + 1 extension to Vera chart_type_registry.json.
- 8/8 schema smoke tests pass. No code changes (retro-apply deferred to Wave 5C).

### Wave 5C -- Retro-apply to HY-IG v2 (2026-04-19)
- 45 captions migrated to APP-CC1 prefixes.
- 17 expanders retitled per APP-EX1.
- 22 loud-error sites got META-ELI5 Plain English blocks.
- Trigger-card sparklines rewritten with real data (`_find_real_crossings` helper). HY-IG up-crossing 2010-04-06, down-crossing 2016-02-11. HOLD falls back to stylised with transparent caption.
- APP-URL1 slug pins verified against Streamlit 1.54.0 (no drift from 1.39.0).

### Wave 6B -- Loader + META-ZI refinement (2026-04-19)
- Dropped `output/_comparison/` fallback chain from `charts.py`.
- `chart_type_registry.json` history_zoom_* entries updated to `expected_chart_type=dual_panel`, `override_supported=false`.
- APP-SE1 loader-contract note in SOP refined.
- Both smoke tests still pass (15/15 loader, 3/3 schema consumers).

### Wave 7B -- Methodology table renderers (2026-04-19)
- Created `signal_universe_table.py` (150 LoC) and `analyst_suggestions_table.py` (129 LoC).
- Methodology page: new "Signal Universe" + "Analyst Suggestions for Future Work" sections.
- Extended smoke_schema_consumers.py (3 -> 5 cases).

### Wave 7C fix-up -- CCC-BB prose leak (2026-04-20)
- Quincy blocked: 5 prose citations in `.py` pages contradicted Ray narrative.
- Rewrote 5 sites to point at `signal_scope.json` as authoritative.
- Story-page expander retitled to flag out-of-scope status.
- Filed BL-004 for cross-pair audit.

### Wave 8B-2 -- Unit-form consumer fix (2026-04-20)
- Fixed "+0.1%" KPI bug: 15 consumer sites migrated to ratio-aware handling.
- `{:.1f}%` -> `{:.1%}` on 7 format strings.
- Fallbacks: 11.33 -> 0.1133; -10.2 -> -0.102; -33.7 -> -0.337.
- Boundary-normalization in `pair_registry.py` preserves uniform percent-form contract for all pairs.
- Semantic triangulation (QA-CL2 preview): Sharpe 1.27 + ann return 11.3% + MDD -10.2% -> implied vol 8.9%, DD/vol 1.15 -- plausible.
- Both smoke tests PASS (15/15 loader, 5/5 schema consumers).

### Wave 9B -- Experience + memory catch-up (2026-04-20)
- THIS SESSION.
- Updating `experience.md`, `memories.md`, `session-notes.md`, `projects/aig-rlic-plus.md`.
- No SOP or component edits this wave.

## Component inventory (as of Wave 9B)

`app/components/` (20 files, + `__init__.py`, + `__pycache__`):
- `analyst_suggestions_table.py` -- Wave 7B
- `breadcrumb.py` -- Wave 2B
- `charts.py` -- Wave 3 / 6B (load_plotly_chart returns Figure; no _comparison/ fallback)
- `direction_check.py` -- Wave 4D-2 (APP-DIR1)
- `execution_panel.py` -- pre-existing
- `glossary.py` -- Wave 2B / pre-existing
- `instructional_trigger_cards.py` -- APP-SE3 (Wave 5C real sparklines)
- `live_execution_placeholder.py` -- APP-SE4 (Wave 4D-2)
- `metrics.py` -- pre-existing
- `narrative.py` -- fixed: no HTML wrapper
- `pair_registry.py` -- Wave 8B-2 (max_drawdown ratio->percent normalization for hy_ig_v2_spy)
- `position_adjustment_panel.py` -- APP-SE2
- `probability_engine_panel.py` -- APP-SE1 / APP-WS1 (schema-validated reads)
- `schema_check.py` -- Wave 4D-2 (validate_or_die / validate_soft / SchemaValidationError)
- `sidebar.py` -- pre-existing
- `signal_universe_table.py` -- Wave 7B
- `tournament.py` -- pre-existing
- `trade_history.py` -- pre-existing

`app/_smoke_tests/` -- Wave 3 / 7B:
- `smoke_loader.py` (AST-parses pages; exec each load_plotly_chart; asserts Figure, traces, title)
- `smoke_schema_consumers.py` (validate_or_die across 5 consumer cases)

### Wave 10D dispatch fix (2026-04-20) -- indpro_xlp BUG-1 + BUG-2

**What:** Fixed two structural bugs in all 4 `indpro_xlp` pages.

- **BUG-1 (breadcrumb missing):** Added `from components.breadcrumb import render_breadcrumb` + `render_breadcrumb("<Section>", PAIR_ID)` call to all 4 pages (story, evidence, strategy, methodology). Call placed after `render_glossary_sidebar()` per reference template pattern.
- **BUG-2 (evidence flat tab structure):** Rewrote `14_indpro_xlp_evidence.py` from a flat 4-tab layout to Level 1 / Level 2 tab hierarchy with 3 method blocks (Correlation, Granger Causality, Regime Analysis), each using `render_method_block()` with all 8 required elements. Existing analysis content preserved and restructured — no content discarded.

**Root cause:** `indpro_xlp` pages were built from scratch instead of being derived from the reference template (`9_hy_ig_v2_spy_story.py`). Template derivation would have caught both bugs structurally.

**Smoke test:** `python3 app/_smoke_tests/smoke_loader.py indpro_xlp` → `failures=0` (6 PASS, 0 FAIL).

### APP-SS1 dispatch (2026-04-20) -- Signal Universe reader mismatch retro-apply

**What:** Retro-applied rule APP-SS1 to `14_indpro_xlp_methodology.py`. The Signal Universe block used the legacy `in_scope.indicator_derivatives` / `in_scope.target_derivatives` path which does not exist in the current `signal_scope.json` schema (migrated to `indicator_axis.derivatives` / `target_axis.derivatives`). Both columns rendered silently empty.

**Files changed:**
- `app/pages/14_indpro_xlp_methodology.py` — lines 114–132: replaced legacy `scope.get("in_scope", {})` reader with APP-SS1 canonical `scope.get("indicator_axis", {}).get("derivatives", [])` reader. Updated display to show `name` + `definition` per derivative object (was just column name strings).

**`10_umcsent_xlv_methodology.py` status:** Already uses `render_signal_universe(PAIR_ID)` component — no change needed. Component reads new schema correctly.

**Validation result:**
```
indpro_xlp: indicator=7 derivatives, target=5 derivatives
umcsent_xlv: indicator=5 derivatives, target=5 derivatives
APP-SS1 validation PASS
```

**Root cause:** `14_indpro_xlp_methodology.py` had an inline hand-rolled JSON reader instead of using the `render_signal_universe` component. The component was already correct; only the inline reader was stale.

### APP-PT1 dispatch (2026-04-20) -- page template abstraction + indpro_xlp migration

**What:** Authored APP-PT1 rule and built the page-template abstraction for the portal. Replaced the 4 `14_indpro_xlp_*.py` pages with thin wrappers; introduced `app/pair_configs/` package with `indpro_xlp_config.py`; extended smoke loader to scan template + config modules.

**Files created:**
- `app/components/page_templates.py` (~850 LoC) — four template functions: `render_story_page`, `render_evidence_page`, `render_strategy_page`, `render_methodology_page`. Public `MethodologyConfig` dataclass. Shared helpers: `_apply_page_config`, `_load_winner_summary` (APP-SEV1 L1), `_load_interpretation_metadata` (soft load), `_latest_dated_file` (glob `*_YYYYMMDD.*`), `_indicator_target_display` (mirrors `pair_registry` display maps), `_format_ratio_pct`, `_page_prefix` (mirrors `pair_registry` routing). 8-element `_render_method_block` lives inside the template.
- `app/pair_configs/__init__.py` — package marker.
- `app/pair_configs/indpro_xlp_config.py` (~450 LoC) — `STORY_CONFIG`, `EVIDENCE_METHOD_BLOCKS` (CORRELATION + GRANGER + REGIME blocks, 8-element), `STRATEGY_CONFIG`, `METHODOLOGY_CONFIG` (MethodologyConfig dataclass). Content migrated verbatim from the prior hand-written pages.

**Files modified:**
- `app/pages/14_indpro_xlp_story.py` — thin wrapper (11 lines, zero `st.*` calls).
- `app/pages/14_indpro_xlp_evidence.py` — thin wrapper (11 lines, zero `st.*` calls).
- `app/pages/14_indpro_xlp_strategy.py` — thin wrapper (11 lines, zero `st.*` calls).
- `app/pages/14_indpro_xlp_methodology.py` — thin wrapper (11 lines, zero `st.*` calls).
- `app/_smoke_tests/smoke_loader.py` — added `PAIR_TEMPLATE_CHARTS` registry + AST scanner for `page_templates.py` and `pair_configs/{pair_id}_config.py`. Scans `load_plotly_chart(...)` args and `_CHART_NAME` assignments.
- `docs/agent-sops/appdev-agent-sop.md` — added APP-PT1 rule body after APP-SS1 and added a new Quality Gates checklist item for thin-wrapper compliance.

**Validation:**
- `python3 -c "from components.page_templates import *; from pair_configs.indpro_xlp_config import *"` → Import OK.
- `python3 app/_smoke_tests/smoke_loader.py indpro_xlp` → 8 PASS / 0 FAIL (2 Story charts, 2 Performance charts, 2 Confidence charts, 2 Evidence method-block charts).
- `python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy` → 15 PASS / 0 FAIL (non-regression).
- `python3 app/_smoke_tests/smoke_loader.py umcsent_xlv` → 7 PASS / 0 FAIL (non-regression).
- `python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id indpro_xlp` → 5 PASS / 0 FAIL (APP-WS1 / DATA-D6 / ECON-UD / ECON-AS / APP-DIR1).
- AST verification: all 4 `14_indpro_xlp_*.py` page files contain zero `st.*` calls (thin-wrapper compliance verified).

**Root-cause framing:** Wave 10D was the catalyst (breadcrumb missing, Evidence flat tabs, Signal Universe empty). Those bugs were symptoms of a single class — copy-paste page files drift from the reference. APP-PT1 fixes the class: page files are now pure routing with no room for structural divergence. META-NMF compliant — the fix is at the abstraction layer, not inline patches.

**Scope discipline:** Did NOT migrate hy_ig_v2_spy, umcsent_xlv, or any other pair pages. Retroactive migration is scheduled pair-by-pair in a subsequent wave (see APP-PT1 §migration-protocol in the SOP).

## Open threads / backlog

- BL-002 -- cross-pair unit-form inherit for sample pairs (1-4_*, 5-8_*) still in percent form.
- BL-004 -- cross-pair prose leak audit (other pages may cite signals that Ray narrative has scoped out).
- APP-EX1 v1.1.0 -- propose sixth canonical entry `"status_labels_glossary"` with title `"Status labels"` (pending Lead approval).
- RES-17 upgrade -- when Ray narrative_frontmatter migration lands, upgrade APP-DIR1 from 2-way to 3-way check.
- APP-PT1 retro-apply -- migrate HY-IG v2, umcsent_xlv, indpro_spy, permit_spy, vix_vix3m_spy, ted_variants, hy_ig_spy legacy pages to thin wrappers in subsequent waves. Each migration is pure restructure: lift narrative text to config, leave template untouched. Net LoC per pair: -400 to -700 page lines, +300 config lines.
- APP-PT1 v1.1 -- if a pair needs a genuinely different Story structure (different section order, alternate hero layout), promote it as `render_story_page_variant_a` in `page_templates.py` — do NOT allow per-page overrides.

## 2026-04-20 Wave 10F Cross-Review (Ace)

**Task:** Read all SOPs + team-standards.md + inspect page_templates.py + indpro_xlp_config.py. Produce findings at `_pws/_team/cross-review-20260420-appdev-ace.md` with sections 1–7 (Conflicts / Redundancies / Rules for team-standards / Silent Weakening / Ace-specific / Vera Q&A / Priority Top-5).

**META-SRV evidence:**
- Deliverable file exists: `/workspaces/aig-rlic-plus/_pws/_team/cross-review-20260420-appdev-ace.md` — ~215 lines, all 7 sections present, ~2100 words.
- Files read: `docs/team-standards.md` (142L), `docs/sop-changelog.md` (400L), `docs/agent-sops/appdev-agent-sop.md` (L1-400), `docs/agent-sops/team-coordination.md` (L1-300), `docs/agent-sops/visualization-agent-sop.md` (L1-300), `docs/agent-sops/qa-agent-sop.md` (L1-250), `app/components/page_templates.py` (1319L full), `app/pair_configs/indpro_xlp_config.py` (611L full), `app/components/charts.py` (L1-120).
- Directory evidence: `output/charts/hy_ig_v2_spy/plotly/` lists BOTH `hero.json` and `hy_ig_v2_spy_hero.json` — confirms VIZ-NM1 silent-weakening finding. `output/charts/indpro_xlp/plotly/` is bare-name only (compliant).

**Key findings (top 5 priority):**
1. P0 — Remove loader pair-prefix fallback in `charts.py`; delete HY-IG v2 duplicate JSONs; ratify VIZ-NM1 in `team-standards.md §2.1`.
2. P0 — Unify `signal` / `signal_code` / `signal_column` field names across `winner_summary.schema.json` + `tournament_winner.schema.json`; retire defensive `or` fallbacks in template.
3. P1 — Promote APP-SEV1 to a named SOP section; define APP-CC1, APP-EX1, APP-URL1, APP-ST1 canonically (currently referenced but undefined in my SOP).
4. P1 — Ratify `team-standards.md` placeholders §2.1 / §3 / §4 in one wave, consuming this review + Vera's + others'.
5. P2 — APP-PT1 migration of existing pairs (TED variants → monthly pairs → HY-IG v2 reference last) with before/after screenshots + regression_note per pair.

**Vera's three open questions (my answers as chart consumer):**
- Q1 filename: loader supports both; enforce bare-name per VIZ-NM1, remove fallback, delete HY-IG v2 duplicates. I will own the migration.
- Q2 sidecar: chart `_meta.json` (Vera), dataset `_manifest.json` (Dana/Evan). Ratify `team-standards.md §3` proposal as-is.
- Q3 palette: keep `color_palette_registry.json` as SSoT; add semantic role aliases (`indicator`, `target`, `benchmark`); retire Python `PALETTE` dict in `page_templates.py`; load from JSON at runtime.

**EOD status:**
- Session notes (this file) — appended.
- Global profile `experience.md` + `memories.md` + `last_seen` — BLOCKED by sandbox; global-profile paths (`~/.claude/agents/...`) are denied by Bash/Edit/Write in this environment. Key Wave 10F entries captured in this session notes file for manual promotion by Lead or next SOD.

**PROMOTED 2026-04-22T07:49Z**

**Proposed entries for `~/.claude/agents/appdev-ace/experience.md`** (for manual promotion):
- "Rule on paper, code in violation" silent-weakening class: rule changes must include code deletion in the same commit.
- Defensive `getattr ... or getattr` in consumer code = META-CF smell; every such fallback silently weakens the contract.
- Hard-coded maps duplicated across files = dispatch-surface hazard. Drive from single JSON registry.
- Template abstraction is incomplete until the reference pair is migrated to it.
- Narrative-authorship (Ray-only) can only be retro-applied at migration time.

**Proposed entries for `~/.claude/agents/appdev-ace/memories.md`:**
- 2026-04-20: VIZ-NM1/APP-EP4 silent weakening — `charts.py` L106-113 still has fallback; HY-IG v2 has 14 duplicate pair-prefixed JSONs on disk.
- 2026-04-20: Field drift `signal` / `signal_code` / `signal_column` — template uses `or` fallback at L408, L892-920.
- 2026-04-20: Undefined rule IDs referenced in my template or other SOPs — APP-CC1, APP-EX1, APP-URL1, APP-SEV1 (partially), APP-ST1.
- 2026-04-20: Pairs NOT migrated to APP-PT1 include the reference pair HY-IG v2; gap is structural.
- 2026-04-20: indpro_xlp_config.py narrative migrated by Ace, not re-authored by Ray (APP-PT1 supplement gap).

---

## Session 2026-04-22T08:35Z — Wave 10F item 6: VIZ-NM1/APP-EP4 fallback removal

**Dispatch:** Remove pair-prefix fallback from `app/components/charts.py` (L106-113).

**Before:** 181 lines. Fallback block (5 lines) tried `{chart_name}.json` first, then `{pair_id}_{chart_name}.json` as second candidate.

**After:** 180 lines (net -1). Single candidate: bare-name `{chart_name}.json` only. Comment added citing VIZ-NM1, APP-EP4, Wave 10F item 6, and Vera's migration commits.

**Diff summary:** `charts.py` — 1 file changed, 4 insertions(+), 5 deletions(-)

**Smoke loader results (all pass):**
- `hy_ig_v2_spy`: passes=15, failures=0
- `indpro_xlp`: passes=8, failures=0
- `umcsent_xlv`: passes=7, failures=0

**Commit:** `cc99fc4` — pushed to remote main.

**Violation lifetime:** ~13 days (VIZ-NM1 ratified 2026-04-09; fallback removed 2026-04-22). Detected by Wave 10F cross-review (commit `85ee737`). Root cause: rule ratification did not include a code-deletion gate or follow-up grep scan. Process fix documented in global experience.md.

---

## 2026-04-22 Wave 10F item 6b dispatch — VIZ-NM1 page_templates.py

**Dispatch:** a55c9dc3 cloud verify failure on indpro_xlp story+evidence ("chart pending" with pair-prefixed paths)

**Root cause:** 6 getattr defaults in `app/components/page_templates.py` using `f"{pair_id}_Y"` form

**Line-by-line diff (6 changes, 0 net delta):**
- L457: `f"{pair_id}_hero"` → `"hero"`
- L476: `f"{pair_id}_regime_stats"` → `"regime_stats"`
- L973: `f"{pair_id}_equity_curves"` → `"equity_curves"`
- L988: `f"{pair_id}_drawdown"` → `"drawdown"`
- L1025: `f"{pair_id}_walk_forward"` → `"walk_forward"`
- L1042: `f"{pair_id}_tournament_scatter"` → `"tournament_scatter"`

**wc -l evidence:** 1318 before, 1318 after (no structural change)

**smoke_loader results:**
- hy_ig_v2_spy: passes=15, failures=0
- indpro_xlp: passes=8, failures=0
- umcsent_xlv: passes=7, failures=0

**Commit:** `a74364f` — pushed to remote main

**Post-mortem:** item 6 deletion gate (cc99fc4) only covered charts.py; page_templates.py contained 6 more violations undetected. Project-wide grep scope is mandatory after any VIZ-NM1 change.

---
## Wave 10G.3 Dispatch — 2026-04-22

**Task:** Close two APP-PT1 template gaps for Sample feature parity.

**Gap 1 — HISTORY_ZOOM_EPISODES:**
- Added optional section in `render_story_page()` after regime chart (line ~491)
- `getattr(config, "HISTORY_ZOOM_EPISODES", None)` guard — absent → silent skip
- Each episode: title → narrative markdown → `load_plotly_chart(history_zoom_{slug})` → caption
- Missing chart → APP-SEV1 L2 `st.warning`

**Gap 2 — regime_context:**
- Added `regime_context = content.get("regime_context")` inside `_render_method_block()`
- When present: `st.info(regime_context)` between method_theory and question
- When absent: block unchanged

**Validation:**
- imports OK
- indpro_xlp: 8/0
- umcsent_xlv: 7/0
- hy_ig_v2_spy: 15/0

**SOP/Docs:**
- APP-PT1 supplement added to appdev-agent-sop.md
- sop-changelog.md Wave 10G.3 updated to DONE

**Commit:** cfe66fb — pushed to remote main

**wc -l page_templates.py:** 1318 → 1355 (+37 lines)

---
## 2026-04-22 — Wave 10G.4E Session

**Task:** Build hy_ig_spy portal (pair_config + 4 thin wrappers).

**Completed:**
- `app/pair_configs/hy_ig_spy_config.py` (922 lines)
  - STORY_CONFIG with HISTORY_ZOOM_EPISODES (3 episodes: dotcom, gfc, covid)
  - EVIDENCE_METHOD_BLOCKS: 3 level-1 (Correlation, Granger, CCF) + 5 level-2 (HMM, Regime Quartile, Transfer Entropy, Local Projections, Quantile Regression)
  - regime_context on HMM, Regime Quartile, Transfer Entropy blocks
  - STRATEGY_CONFIG + METHODOLOGY_CONFIG
- `app/pages/15_hy_ig_spy_{story,evidence,strategy,methodology}.py` — 4 thin wrappers, 0 st.* calls each
- `results/hy_ig_spy/handoff_ace_20260422.md`

**Validation (all PASS):**
- Import: HISTORY_ZOOM_EPISODES=3, level1=3, level2=5
- smoke_loader hy_ig_spy: 6/0
- smoke_loader hy_ig_v2_spy: 15/0 (no regression)
- smoke_loader indpro_xlp: 8/0 (no regression)
- smoke_loader umcsent_xlv: 7/0 (no regression)
- smoke_schema_consumers hy_ig_spy: 5/5
- APP-PT1 gate: 0 st.* calls in all 4 page files
- Commit: 4e45eb0, pushed to remote

**Next:** Quincy (GATE-NR narrative scan + cloud verify).

---
## 2026-04-22 — Wave 10G.4E-fix Session

**Task:** Fix two cloud-only bugs on hy_ig_spy pair (Bug 1: page_link routing; Bug 2: _validate_signal ValueError).

**Bug 1 root cause:** `page_routing` dict in `pair_registry.py` missing `hy_ig_spy` entry. Fell through to default `pages/5_hy_ig_spy` but actual pages live at `pages/15_hy_ig_spy_*.py`. Fix: added `"hy_ig_spy": "pages/15_hy_ig_spy"` to dict.

**Bug 2 root cause:** `_validate_signal` in `probability_engine_panel.py` unpacked `known_stress_episodes` elements as 2-tuples `(win_start, win_end)`, but Evan's `interpretation_metadata.json` uses dicts `{label, start, end, note}`. Fix: added `_to_window()` normaliser inside `_validate_signal` that handles both formats.

**Backlog note (META-NMF):** The `_validate_signal` function has no documented contract for its acceptable `stress_windows` element shape (tuple vs dict). Should add to probability_engine_panel.py docstring and the data agent SOP: `known_stress_episodes` must be a list of `{start, end, ...}` dicts; the validator accepts both dict and tuple for backward compat.

**Validation (all PASS):**
- `_validate_signal` local repro: ok=True, diag='ok'
- `load_pair_registry` hy_ig_spy story_page = `pages/15_hy_ig_spy_story.py` ✓
- smoke_loader hy_ig_spy: 6/0
- smoke_loader hy_ig_v2_spy: 15/0
- smoke_loader indpro_xlp: 8/0
- smoke_loader umcsent_xlv: 7/0
- Commit: 75d6574, pushed to remote

### Wave 10G.5-fix -- APP-RL1 single-source routing (2026-04-22)

- Bug A closed: deleted `_page_prefix()` from `page_templates.py` (19-line func + dict). Added import of `get_page_prefix` from pair_registry. Replaced 3 call sites.
- Bug B closed: added `"hy_ig_spy": "HY-IG Credit Spread"` to `indicator_names` in `load_pair_registry()`.
- New helper `get_page_prefix(pair_id)` in pair_registry.py backed by module-level `PAGE_ROUTING = {...}`. `load_pair_registry()` refactored to use it.
- APP-RL1 grep: `grep -rn -E "PAGE_ROUTING\s*=\s*\{" app/` returns exactly 1 match.
- load_pair_registry assertion: PASS.
- smoke_loader: hy_ig_spy 6/0, hy_ig_v2_spy 15/0, indpro_xlp 8/0, umcsent_xlv 7/0.
- Commit: 35bb008, pushed to remote.

---
## 2026-04-22 — Wave 10H.1 — APP-PT2 Exploratory Insights

**Task:** Implement Rule APP-PT2 (Methodology page Exploratory Insights section) in the centralised template.

**Edit:** single file — `app/components/page_templates.py`.
- Added helper `_render_exploratory_insights(pair_id)` (~63 LoC) near `_load_interpretation_metadata`.
- Wired into `render_methodology_page` as section 13b (between Analyst Suggestions and References). Helper owns its trailing `---` separator so that legacy pairs (no `exploratory_charts` key) render identically.
- Reads `results/{pair_id}/analyst_suggestions.json`; soft-fail on missing file / JSON error / key absent / empty list. Missing `chart_name` in an entry → `continue`. Missing chart artifact → `st.warning` (APP-SEV1 L2) → `continue`.
- Caption prefix `"What this shows:"` per APP-CC1; italic rationale per APP-PT2 §3c; feedback prompt per APP-PT2 §3d.

**Smoke evidence:**
- `smoke_loader hy_ig_v2_spy` → 15/0 PASS
- `smoke_loader hy_ig_spy` → 6/0 PASS
- Dry-run harness at `temp/260422_app_pt2/dry_run_helper.py` → 4/4 scenarios PASS (missing file, key absent, two entries, missing chart recover).

**Handoff:** `results/_cross_agent/handoff_ace_wave10h1_20260422.md`.

**Scope discipline (LEAD-DL1):** no writes to `analyst_suggestions.json`, chart sidecars, pair_config narrative, QA scripts, or hand-written legacy `.py` pages.

## 2026-04-23 — Wave 10H.1 follow-up (2 FAILs from Quincy cloud verify)

Two real FAILs, byte-identical across 2 cloud reboots → not deploy-lag.

**Bug 1 landing raw-col leak:** root cause = `key_finding` string in `interpretation_metadata.json` contains raw `spy_fwd_*d` tokens, rendered verbatim at `app/app.py:312`. Fixed by adding `humanize_column_tokens()` + `_FWD_RETURN_LABELS` map in `pair_registry.py` (APP-RL1 SSoT) and wrapping the key_finding display.

**Bug 2 APP-PT2 silent no-op:** root cause = `app/pages/9_hy_ig_v2_spy_methodology.py` is hand-written legacy page; does NOT use `render_methodology_page` template where I wired `_render_exploratory_insights` in Wave 10H.1 (e6767e0). Classic template-scope miss. Fix: direct call in the page file before References section. Also tightened observability in the helper's JSON read error branch (st.warning instead of silent return) per APP-SEV1 L2.

**Lesson logged for global experience:** when adding a feature via a centralized template, always grep pages/ for bypass (`grep -L "render_methodology_page"`). 5 pages currently bypass (not just hy_ig_v2_spy).

Proposed APP-PR1 to Lead: mandate `_REPO_ROOT` anchors for all project-relative file reads; require `st.warning`/`st.error` on path-exists-but-unreadable failures of shipped-pair files.

Smoke: both pairs failures=0. CWD-independence regression test added at `temp/260423_ace_wave10h1_followup/`.
