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

## Open threads / backlog

- BL-002 -- cross-pair unit-form inherit for sample pairs (1-4_*, 5-8_*) still in percent form.
- BL-004 -- cross-pair prose leak audit (other pages may cite signals that Ray narrative has scoped out).
- APP-EX1 v1.1.0 -- propose sixth canonical entry `"status_labels_glossary"` with title `"Status labels"` (pending Lead approval).
- RES-17 upgrade -- when Ray narrative_frontmatter migration lands, upgrade APP-DIR1 from 2-way to 3-way check.
