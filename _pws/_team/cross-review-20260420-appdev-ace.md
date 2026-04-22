# Cross-Review 2026-04-20 — AppDev Ace

**Reviewer:** AppDev Ace (integrator / portal developer)
**Scope:** All agent SOPs + `docs/team-standards.md` + `app/components/page_templates.py` + `app/pair_configs/indpro_xlp_config.py`
**Perspective:** Downstream consumer of every producer's artifacts; author of APP-* rules and the page template abstraction.

---

## Section 1 — Conflicts

1. **Chart filename convention — bare-name vs pair-prefixed (live conflict).** `VIZ-NM1` (`sop-changelog.md` 2026-04-09 / `visualization-agent-sop.md`) declares: *pair_id appears ONLY in directory path, NEVER in filename.* The loader in `app/components/charts.py` lines 106–113 STILL tries bare name first then falls back to `{pair_id}_{chart_name}.json`. Evidence on disk that the conflict is active: `output/charts/hy_ig_v2_spy/plotly/` contains BOTH `hero.json` and `hy_ig_v2_spy_hero.json`, `correlation_heatmap.json` and `hy_ig_v2_spy_correlation_heatmap.json`, etc. The indpro_xlp and umcsent_xlv pairs have bare-name only (VIZ-NM1-compliant). APP-EP4 (2026-04-09) was supposed to remove the fallback — *"loader uses canonical filename only; no fallback to alternate filenames"* — but `load_plotly_chart` still appends the pair-prefixed candidate. `team-standards.md §2.1` correctly flags this as `[TO BE POPULATED BY CROSS-REVIEW]`.

2. **Sidecar naming — `_meta.json` vs `_manifest.json` (soft conflict).** Vera's SOP §Viz-to-App section 6 and VIZ-V8 (implicit in IC1 changelog wording) say `{chart_name}_meta.json`. Evan's artifact manifests (data sidecars in the Econ-to-Viz handoff: "Artifact manifest (`_manifest.json` sidecar)") use `_manifest.json`. `team-standards.md §3` proposes splitting them by artifact type (charts → `_meta`, datasets → `_manifest`), which is sensible but not yet ratified. I consume both and the split proposal matches my mental model; formalize it.

3. **Color palette — two registries.** `app/components/page_templates.py` lines 74–90 hard-codes a `PALETTE` dict with keys `winner / benchmark / stress / calm / neutral / indicator / target / delta_*`. `team-standards.md §4` names a separate canonical file `docs/schemas/color_palette_registry.json` (`okabe_ito_2026`) with role keys `primary_data_trace / secondary_data_trace / equity_curve / drawdown_fill / quartile_gradient / nber_shading`. These two registries have disjoint role vocabularies. VIZ-IC1's "palette registry conformance" check presumably points at the JSON registry, not the Python dict — so the page template is currently outside the enforcement radius of VIZ-IC1. See Section 6 for recommended reconciliation.

4. **`signal_column` provenance — two sources.** APP-SE1 (Rule A1 validation, SOP §3.6) says the signal column name is declared *"in the pair's `winner_summary.json` under the `signal_column` field."* In the template code at line 408, I read `winner.get("signal_code") or winner.get("signal_column")`. Evan's SOP elsewhere uses `signal` and `signal_code` interchangeably (see `tournament_winner.json` schema in `team-coordination.md` lines 130–154: only `signal` is declared, no `signal_column`). Three different field names for the same concept across Evan's producer artifacts and Ace's consumer. This is a META-CF violation waiting to blow up.

5. **Page file naming vs routing map.** `team-standards.md §2.3` states pages follow `app/pages/{N}_{pair_id}_{section}.py`. The `_page_prefix` table in `page_templates.py` lines 570–581 hard-codes N per pair. A new pair added without updating BOTH the map AND the pair_registry will silently route to a non-existent page. This is a dispatch-surface conflict — two places store the same information.

6. **Breadcrumb ownership ambiguity.** APP-URL1 (per QA-CL4 description in qa-agent-sop.md line 91) mandates the 4-step breadcrumb. GATE-28 enforces it. The breadcrumb is rendered by `render_breadcrumb(section, pair_id)` in the template — so APP-PT1 compliance implies APP-URL1 compliance. But APP-URL1 is referenced from qa-agent-sop.md without a definition in appdev-agent-sop.md that I could locate; only the implicit template behavior. Either APP-URL1 needs a named section in appdev SOP or it should be folded into APP-PT1 as "structural element #1."

---

## Section 2 — Redundancies

1. **"Thin wrapper" rule stated three times.** APP-PT1 in `appdev-agent-sop.md`, APP-PT1 in `sop-changelog.md` 2026-04-20 Wave 10E, and (proposed) `team-standards.md §1` directory-layout row for `app/pages/`. The phrasing differs across three places; when it mutates, one of them will diverge.

2. **Read-order instructions repeated.** `team-standards.md §Read order`, `sop-changelog.md §SOD read protocol`, and each agent SOP's SOD section all re-specify the same 3-step read sequence (team-standards → own SOP → changelog since last_seen). This belongs in team-standards.md only; SOPs should cite it.

3. **Deliverables gate items 9–12 (portal pages) duplicate APP-PT1.** `team-coordination.md` gate items 9/10/11/12 list 4 page files as separate checklist items. APP-PT1 already mandates all four via the template. Items 9-12 should collapse to a single item: "all 4 thin-wrapper pages exist per APP-PT1."

4. **Chart filename contract stated in three places.** APP-EP4 (AppDev SOP + standards.md), VIZ-NM1 (Viz SOP), and `team-standards.md §2.1` placeholder. Three rules for one convention is the recipe for drift that already exists (see Conflict 1).

5. **KPI caption pattern.** APP-AF3 (metric interpretation), APP-RP1 (rendering patterns), and the `kpi_caption` hook in the Story template all say "every KPI row needs a caption bridging numbers to meaning." Pick one canonical locus.

6. **Fallback-severity policy appears ad hoc.** APP-SEV1 is referenced in `page_templates.py` docstrings (L1 loud-error, L2 loud-warning, L3 caption) but I cannot find a single authoritative section that defines it. It is de facto encoded in the template and inherited wherever the template is used. Should be promoted to a named rule in appdev-agent-sop.md.

---

## Section 3 — Rules That Belong in team-standards.md (integrator view)

As the agent who glues everyone's outputs together, I see duplication in these topics most often. Each one should become a canonical section in team-standards.md with agent SOPs citing by link.

1. **Artifact naming registry** (supersedes §2.1, §2.2, §2.3 placeholders). One table: artifact type → filename pattern → owner → consumer → sidecar. Rows: chart JSON, chart sidecar, signals parquet, winner_summary.json, signal_scope.json, interpretation_metadata.json, tournament_results CSV, stationarity_tests CSV, trade log CSV, analyst_suggestions JSON, pair page file, pair config module. This single table would retire APP-EP4 / VIZ-NM1 / ECON-DS2's scattered rules about paths.

2. **Severity policy (APP-SEV1 promotion).** Three tiers — loud-error short-circuit (L1) / loud-warning continue (L2) / caption soft-note (L3) — with exemplars. Currently lives only inside my template docstrings. Other agents render `st.info/warning/error` with no shared rubric.

3. **Color palette canonical mapping.** Resolve conflict #3 above. One JSON registry + explicit role-alias table. Move `page_templates.PALETTE` out of Python into JSON and load at runtime.

4. **Consumer contracts for all shared JSONs.** `team-standards.md §5.1` has a start. Add: minimum required fields per schema (with link to the JSON Schema file), forbidden legacy fields, migration aliases. APP-SS1 / APP-WS1 are the first two instances of this genus; others follow.

5. **"Unknown is not a display state" principle.** Currently buried in team-coordination.md section. Belongs in team-standards as the META rule it is. Every agent needs to see it at SOD.

6. **Agent dispatch template fields.** `team-standards.md §7` has the skeleton; add the EOD block and the "inspect briefly" convention explicitly. Right now dispatch prompts vary in completeness wave-to-wave.

7. **Pair routing registry** (the N in `{N}_{pair_id}_*.py` and the display_order). Currently duplicated in `pair_registry.py` and `_page_prefix` in page_templates.py. Move to JSON `docs/schemas/pair_registry.json` owned by Ace, consumed by both.

---

## Section 4 — Silent Weakening

Places where rules are nominally intact but practice has eroded:

1. **APP-EP4 ("no loader fallback").** Stated 2026-04-09. Loader code at `charts.py` L106–113 STILL has the fallback, and HY-IG v2 still ships both filename variants. The rule exists on paper; the code undermines it. Classic silent weakening: nobody removed the fallback branch when the rule was added.

2. **GATE-29 parquet explicit check (added Wave 10E).** The status files show INDPRO_XLP and UMCSENT_XLV smoke test logs now exist — but looking at the git status (`_smoke_tests/*.log` are modified, uncommitted), someone is running them manually rather than in CI. The gate is a rule without automation; one missed wave and drift returns.

3. **META-PT1 "no `st.*` call in page file other than template call."** The SOP says any `st.*` call is a gate failure. There is no automated check (grep over `app/pages/*.py` for `^import streamlit` or `st\.` outside the wrapper). Enforcement depends on reviewer diligence — drift is inevitable.

4. **VIZ-NM1 compliance for old pairs.** HY-IG v2 has 14 pair-prefixed duplicate JSONs still on disk (see ls output). VIZ-NM1 2026-04-09 should have driven their deletion. Instead the pair limped along with BOTH forms because the loader accepts either. Deprecation never happened.

5. **APP-SS1 "Empty Signal Universe = L1 error."** The rule exists (Wave 10E). Whether every new pair's Methodology page renders a non-empty Signal Universe section is currently checked by eyeballing screenshots. No automated test grep's the rendered DOM for "No signals in scope."

6. **META-CF (schema-instance alignment).** The field-name drift in Conflict 4 above (`signal` / `signal_code` / `signal_column`) is exactly the failure mode META-CF was supposed to block. It hasn't. Schema file for `tournament_winner.json` and `winner_summary.json` need reconciliation; right now consumers use `getattr(obj, "field_a") or getattr(obj, "field_b")` defensive patterns (my own template does this at L408, L892, L917, L920) — which IS silent weakening of the contract.

7. **"Narrative prose MUST be authored by Ray" (APP-PT1 supplement).** indpro_xlp_config.py lines 94–148 contain ~500 words of narrative prose. The header comment says "migrated from the prior hand-written pages under `app/pages/14_indpro_xlp_*.py`, 2026-04-20 wave, AppDev Ace". If Ace migrated it, Ace authored it — the supplement rule was retro-applied after narrative authorship happened. GATE-NR/RES-NR1 would catch instrument-name errors, but Ray has not re-audited this prose per the supplement. Silent weakening at birth.

---

## Section 5 — Ace-Specific Observations

### 5.1 Template architecture (`page_templates.py`)

**Strengths:** centralized structure, frozen section order, APP-PT1 observable via "is this a thin wrapper?" grep. The `getattr(config, "FIELD", default)` pattern is resilient to missing config fields — a pair can ship with minimal config and still render.

**Concerns:**
- 1319-line single module. Evidence pages, Strategy pages, Methodology pages all in one file. When one section needs changes it risks touching the others. Consider splitting per-page file (`story.py`, `evidence.py`, `strategy.py`, `methodology.py`) inside `components/page_templates/`.
- `_indicator_target_display` embeds a hard-coded display-name map (lines 234–249). Adding a pair requires editing this map in at least two places (this map + `_page_prefix` map + pair_registry.py). Should be JSON-driven.
- `_render_tournament_leaderboard` contains the percent-vs-ratio heuristic (`if abs(x) > 1.5: assume percent`). This is a band-aid for META-UC drift. Every consumer carrying a heuristic is a META-CF violation in disguise (QA-CL2 documents this exact class of bug).
- `PALETTE` is a module-level Python dict; not loaded from JSON. Duplicates the color registry.

### 5.2 `pair_configs/indpro_xlp_config.py`

- Good separation: display config, narrative, method blocks, methodology markdown.
- Uses `class StoryConfig: ...` then instantiates — slight overhead versus a dataclass, but works.
- `_DATA_SOURCES_MD`, `_METHODS_TABLE_MD` are module-private constants. Consistent.
- **Authorship concern (see Section 4).** Narrative prose in a Python module violates APP-PT1 supplement's spirit that narrative should be Ray-owned. A cleaner path: narrative in `.md` files under `docs/pair_narratives/{pair_id}/` and the config module just references paths.

### 5.3 APP-* cross-references

Rules referenced in the template but not all defined with a canonical section in appdev-agent-sop.md:

| Rule ID | Status | Location |
|---------|--------|----------|
| APP-PT1 | Defined | SOP §Template Abstraction (Wave 10E) |
| APP-PT1 supplement | Defined | SOP (Wave 10E) |
| APP-SEV1 | **Not clearly defined** | Only in template docstrings |
| APP-SS1 | Defined | SOP (Wave 10E) |
| APP-WS1 | Referenced in team-coordination.md §5.1 | Need explicit appdev SOP section |
| APP-DIR1 | Referenced | appdev SOP (direction triangulation) |
| APP-CC1 | Referenced in template | **Not defined anywhere I could find** |
| APP-EX1 | Referenced in template | **Not defined anywhere I could find** |
| APP-ST1 | Referenced in team-coordination.md §29 | Need explicit appdev SOP section |
| APP-URL1 | Referenced in qa SOP QA-CL4 | **Not defined in appdev SOP** |
| APP-EP4 | Defined 2026-04-09 | Loader still in violation (see Section 4) |
| APP-SE1/SE2/SE3 | Defined | Strategy Execution Panel rules |

Five rule IDs show up in template code or cross-agent SOP references without a named section in my own SOP. That is a documentation debt I should own.

### 5.4 APP-PT1 migration path for existing pairs

Current state:
- **Migrated to template:** `indpro_xlp` (this review target), `umcsent_xlv` (presumed — smoke logs modified in git status).
- **NOT migrated:** `hy_ig_v2_spy` (reference pair), `indpro_spy`, `permit_spy`, `vix_vix3m_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`. The reference pair still uses hand-authored page files (pages `9_hy_ig_v2_spy_*.py`).

This is an APP-PT1 gap: the template was built to match the reference pair's structure, but the reference pair itself was never migrated. If the template changes structurally, the reference pair's hand-authored pages won't pick up the change. Proposed migration order: TED variants (shared page) → permit_spy → vix_vix3m_spy → indpro_spy → hy_ig_v2_spy (last, to avoid destabilizing the reference while other pairs migrate). Each migration is a commit of (a) new `pair_configs/{id}_config.py` + (b) thin-wrapper replacement of the 4 `pages/*.py` files + (c) before/after screenshot diff + (d) regression_note entry.

### 5.5 Severity policy consistency

APP-SEV1's three tiers need documentation consistency. Current use in template:
- L1 (loud-error + short-circuit): used for winner_summary.json missing.
- L2 (loud-warning + continue): used for chart pending, trade log missing.
- L3 (caption soft-note): used widely as `st.caption("What this shows: …")` which is not really the same thing as a severity level — it's a narrative caption, not a degraded-data signal.

Conflating "narrative caption" with "L3 severity caption" is confusing. Separate them: severity is for producer-side data degradation; captions are for reader guidance.

### 5.6 Consumer contracts

I consume at least 8 distinct producer JSON/CSV types per pair. Only 3 have enforceable schemas today (`winner_summary.json` via APP-WS1, `signal_scope.json` via APP-SS1, `interpretation_metadata.json` via DATA-D6). The other five (`tournament_results_*.csv`, `stationarity_tests_*.csv`, `winner_trade_log.csv`, `analyst_suggestions.json`, chart `_meta.json`) have implicit contracts defended by defensive `getattr / iloc / try`. Every defensive pattern is a silent-weakening risk.

---

## Section 6 — Vera's Three Open Questions (my opinion as chart consumer)

### Q1 — Chart filename convention: what does the loader support, what breaks if changed?

**Current behavior (charts.py L106–113):** loader tries `{chart_dir}/{chart_name}.json` first, then `{chart_dir}/{pair_id}_{chart_name}.json` as fallback. Both supported.

**What breaks if the fallback is removed (and only bare-name supported, per VIZ-NM1):**
- HY-IG v2 pages that hard-code pair-prefixed names (e.g., references to `hy_ig_v2_spy_hero` in older config) — would need to be cleaned up to bare `hero`.
- Any agent handoff that was told "use pair-prefixed" in Wave-N dispatch and complied.
- Reality check: the bare-name versions exist on disk for HY-IG v2 already. Removing the fallback would require (a) auditing every `load_plotly_chart(…)` call for pair-prefixed chart_name arguments and (b) deleting the 14 duplicate pair-prefixed JSONs in `output/charts/hy_ig_v2_spy/plotly/`.

**Recommendation:** Enforce bare-name per VIZ-NM1. Remove loader fallback. Delete duplicates. This is a 1-commit change; benefit is APP-EP4 finally gets real teeth. I will own this migration if dispatched.

### Q2 — Sidecar naming: `_meta.json` vs `_manifest.json`

**My preference as consumer:** split by artifact type, exactly as team-standards.md §3 proposes:
- **Chart sidecars → `{chart_name}_meta.json`** (Vera-owned). Short and consistent with how "metadata" reads for a chart.
- **Dataset sidecars → `{artifact}_manifest.json`** (Dana/Evan-owned). "Manifest" fits the data-provenance connotation.

This matches existing practice (HY-IG v2 uses `_meta.json` for charts), requires no renames for Vera, and cleanly separates the two producer domains. Ratify team-standards.md §3 proposal as-is.

### Q3 — Palette role aliases

Current state has two vocabularies (Conflict 3). Proposed reconciliation:
- Keep `docs/schemas/color_palette_registry.json` as the SSoT, but ADD the semantic role keys Vera needs (`indicator`, `target`, `benchmark`) alongside the primitive `primary_data_trace`, `secondary_data_trace`, `equity_curve`.
- Map like this:
  - `indicator` = `primary_data_trace` (but semantic; Vera references `indicator` in code)
  - `target` = `secondary_data_trace`
  - `benchmark` = a new key, visually distinct from target (e.g., a grey shade, not the equity_curve green/red which is for strategy).
  - `strategy` / `winner` = `equity_curve`
  - Stress / calm stay separate.
- Retire the Python `PALETTE` dict in `page_templates.py` and load from JSON.

VIZ-IC1 palette-conformance check then has something concrete to test: "every chart uses only colors that appear in the registry, mapped via a documented role."

---

## Section 7 — Priority Ranking (top 5 fixes)

1. **[P0] Resolve chart filename convention.** Remove loader fallback; delete HY-IG v2 duplicates; ratify VIZ-NM1 in team-standards.md §2.1. Addresses Conflict 1, Silent Weakening 1 & 4, Vera Q1. Blast radius: HY-IG v2 pages and pair_configs. Owner: Ace + Vera.

2. **[P0] Unify `signal` / `signal_code` / `signal_column` field names across producer JSONs.** Write the `winner_summary.schema.json` + `tournament_winner.schema.json` with a single canonical field. Retire defensive `or` fallbacks in template. Addresses Conflict 4, Silent Weakening 6. Owner: Evan (schema author) + Ace (consumer migration).

3. **[P1] Promote APP-SEV1 to a named SOP section + document APP-CC1 / APP-EX1 / APP-URL1 / APP-ST1 / APP-WS1.** Today these are "rules by reference" with no canonical definition. Addresses Ace-Specific 5.3, Section 2 redundancy 6. Owner: Ace (documentation debt).

4. **[P1] Ratify `team-standards.md` placeholders** (§2.1 filename, §3 sidecar, §4 palette) in one wave. Close the three `[TO BE POPULATED BY CROSS-REVIEW]` markers, citing this review + Vera's + others'. Addresses Conflict 2 & 3, Vera Q2 & Q3. Owner: Lead (ratification) + Ace/Vera (input).

5. **[P2] APP-PT1 migration of existing pairs, starting with reference pair.** Migrate the TED variants → other monthly pairs → HY-IG v2. Each migration commit carries before/after screenshots + regression_note entry. Ends the drift window where template changes don't propagate to non-migrated pages. Owner: Ace (with Lead acceptance gating each pair).

Honorable mentions (not in top 5 but on the radar):
- Move `PALETTE` / `_indicator_target_display` / `_page_prefix` maps out of Python into JSON (Section 5.1).
- Automate APP-PT1 enforcement (grep check that `app/pages/*.py` contains only template calls).
- Relocate narrative prose out of pair config modules (Ace-Specific 5.2; ties to APP-PT1 supplement authorship rule).

---

## Cross-references consulted

- `docs/team-standards.md` (Wave 10F skeleton)
- `docs/sop-changelog.md` full log
- `docs/agent-sops/appdev-agent-sop.md` §Template Abstraction, §3.6 Strategy Execution Panel, §3.7 Rendering Patterns, §3.8 Audience-Friendly
- `docs/agent-sops/team-coordination.md` §Deliverables Completeness Gate (items 1-31), §META-ZI, §META-VNC, §META-XVC, §META-FRD
- `docs/agent-sops/visualization-agent-sop.md` §Viz-to-App, VIZ-V1/V2/V5/V8/V11/V12, VIZ-NM1
- `docs/agent-sops/qa-agent-sop.md` §QA-CL2/CL3/CL4/CL5 + GATE-NR + QA 5 Pillars
- `app/components/page_templates.py` (1319 lines reviewed in full)
- `app/components/charts.py` loader behavior
- `app/pair_configs/indpro_xlp_config.py` migrated config
- `output/charts/hy_ig_v2_spy/plotly/` + `output/charts/indpro_xlp/plotly/` directory listings

Prepared by: AppDev Ace, 2026-04-20.
