# Cross-Review — Viz Vera — 2026-04-20

**Reviewer:** viz-vera
**Wave:** 10F cross-review (trigger: VIZ-IC1 retro-apply surfaced three unresolved contract questions)
**Scope reviewed:** `docs/team-standards.md`, `docs/agent-sops/{team-coordination,data-agent,econometrics-agent,visualization-agent,research-agent,appdev-agent,qa-agent}-sop.md`, `docs/sop-changelog.md`, `docs/schemas/{color_palette_registry,chart_type_registry}.json`, sidecars under `output/charts/hy_ig_v2_spy/plotly/`, plus the indpro_xlp and umcsent_xlv chart directories as comparative evidence.
**Output:** findings only — no SOP or chart edits per dispatch constraints.

---

## Section 1 — Conflicts

### C1. Bare-name vs pair-prefixed filenames — three incompatible states on disk

- **VIZ-NM1 / META-ZI / VIZ-V8** (visualization SOP L42-44 experience.md; chart_type_registry.json entry for `hero`: `"canonical_filename_pattern": "hero.json"`; team-standards.md §2.1 current wording) mandate **bare-name** in the filename with `pair_id` in the directory only.
- **Ace's loader contract** (appdev SOP L522-528): `load_plotly_chart("{chart_type}", pair_id="{pair_id}")` reads `output/charts/{pair_id}/plotly/{chart_type}.json` — bare-name. Explicit anti-fallback: `"The loader MUST NOT fall back to alternative filenames (\"{pair_id}_{chart_type}.json\" or any legacy variant)"`.
- **Reality on disk:**
  - `output/charts/hy_ig_v2_spy/plotly/` contains **both** `hero.json` (+ `hero_meta.json`) and `hy_ig_v2_spy_hero.json` (no sidecar) — 13 prefixed duplicates side-by-side with the 10 bare-name canonicals.
  - `output/charts/indpro_xlp/plotly/` is 10-for-10 **prefixed** (`indpro_xlp_hero.json`) with **zero** sidecars.
  - `output/charts/umcsent_xlv/plotly/` same pattern — 10-for-10 prefixed, zero sidecars.

This is a silent conflict: the loader will 404 any request for `hero` against `indpro_xlp` / `umcsent_xlv`. The bare-name rule is declared in the SOP but not enforced at producer or QA boundary, so two pairs shipped entirely in the dialect the SOP prohibits. The HY-IG v2 duplicates were created because Wave 5C rebuilt under the new rule while nobody deleted the old files.

### C2. Sidecar naming — VIZ uses `_meta.json`, ECON uses `_manifest.json`, VIZ-IC1 reopens the question

- **Vera's convention (VIZ-V8 / VIZ-V11 / VIZ-V13 / VIZ-SD1)** — `{chart_name}_meta.json`. Visualization SOP L455 (`{chart_name}_meta.json`, field `caption`), L607 (`palette_id` lives in `_meta.json`), L670 (`annotation_strategy_id` in `_meta.json`), L735, L827 ("produce `{chart_name}_meta.json`"), L1035. Team-standards.md §3 proposal: chart sidecars = `_meta.json`. Every existing HY-IG v2 sidecar on disk is `_meta.json`.
- **Evan's convention** — `{artifact}_manifest.json` for dataset / model artifacts. Econometrics SOP L156, L450, L693 (`tournament_manifest.json`), L1149.
- **VIZ-IC1 itself (visualization SOP L962)** says: *"Vera includes a one-line `narrative_alignment_note` in the chart's `_manifest.json` sidecar"* — a **new** `_manifest.json` reference that contradicts the surrounding VIZ-SD1 / VIZ-V8 / VIZ-V11 prose of the same SOP. This is the direct trigger for Open Question #2.
- **Ace's SOP** references both — `_meta.json` at L830 ("Chart metadata sidecar"), and `chart_manifest.json` at L841/L848 as an index file listing all charts. The index file is not per-chart and does not resolve the conflict.

### C3. VIZ-IC1 §4 palette roles don't exist in the registry

Visualization SOP L960 requires: *"The pair's indicator series uses the `indicator` role color; the target series uses the `target` role color; benchmark series use the `benchmark` role color."* The registry at `docs/schemas/color_palette_registry.json` has no keys named `indicator`, `target`, or `benchmark`. Its role keys are `primary_data_trace`, `secondary_data_trace`, `tertiary_data_trace`, `equity_curve`, `buy_indicator`, `sell_indicator`, `hold_indicator`, `nber_shading`, etc. VIZ-IC1 as written cannot be executed against the current registry without either (a) aliases or (b) a rewrite.

### C4. `grandfather_until` legacy palette escape hatch conflicts with VIZ-V5 smoke test

Visualization SOP L609 allows `palette_id: "matplotlib_legacy"` with `grandfather_until`; L613 says a chart whose `palette_id` is *"not in the registry"* fails VIZ-V5. `matplotlib_legacy` is not in the registry file. Either add a legacy palette entry to the registry or clarify that VIZ-V5 treats `matplotlib_legacy` as a sanctioned exception. Today the two rules contradict within the same SOP.

### C5. `override_supported` field in chart registry is self-deprecated

`chart_type_registry.json` `history_zoom_*` entries carry `"override_supported": false` with an explicit `"SCHEMA-REQUEST"` note that the field refers to a legacy META-ZI model. The field is still present, still consumed by Ace's loader per appdev SOP L1180, but Vera's own notes say the semantics need revisiting. This is latent inconsistency — not urgent but it will bite the next rule-writer.

---

## Section 2 — Redundancies

### R1. Palette rule stated in four places

Visualization SOP Rule V11 (L588-615), standards.md, team-standards.md §4, and experience.md all describe the palette role system. If the four ever diverge (alias added in one, missed in another) the canonical source is ambiguous. Recommend: team-standards.md §4 is the index and points at the registry JSON as source of truth; SOP prose cites the rule ID and JSON path only.

### R2. Sidecar schema defined in three places

VIZ-SD1 prose in visualization SOP, informal enumeration in appdev SOP L830, and team-standards.md §3. There is no JSON schema in `docs/schemas/` for chart metadata sidecars (compare: `winner_summary.schema.json`, `signal_scope.schema.json` do exist). Every other cross-agent contract artifact has a JSON schema; chart sidecars don't. This is the underlying reason §3 of team-standards is a stub.

### R3. Narrative-chart coherence rule echoed by three owners

GATE-24 / SL-3 (Vera's chart-text coherence), META-RYW (all agents re-read work), RES-NR1 (Ray's narrative instrument accuracy), and VIZ-IC1 §6 (Vera's narrative_alignment_note) all describe the same control — "chart prose and chart data must agree." Four rule IDs, overlapping obligations. Recommend collapsing to: META-RYW is the team-level rule; RES-NR1 is Ray's chart-text side; VIZ-IC1 is Vera's chart-save side; drop the verbal redundancy between VIZ-IC1 §6 and GATE-24.

### R4. Chart filename contract stated in VIZ-NM1, VIZ-A3, VIZ-V8, APP-EP4, appdev SOP L522-528, team-standards.md §2.1

Six places. If §2.1 becomes authoritative, every other restatement should shrink to "per team-standards.md §2.1."

---

## Section 3 — Rules That Belong in team-standards.md

The skeleton is right; proposed additions for Lead to ratify:

1. **§2.1** — promote bare-name as mandatory + migration clause for prefixed duplicates (see §6 Q1 below).
2. **§3** — canonicalise `_meta.json` for chart sidecars, `_manifest.json` for dataset / model sidecars; add a JSON schema file `docs/schemas/chart_sidecar.schema.json` owned by Vera (see §6 Q2 below).
3. **§4** — add semantic aliases (`indicator`, `target`, `benchmark`) onto existing role keys, rather than rewriting VIZ-IC1 (see §6 Q3 below).
4. **§5 new row** — chart perceptual-check PNG (`_perceptual_check_{name}.png`) producer=Vera, consumer=human reviewer, rule=META-PV. Currently only in experience.md and visualization SOP; should be in the cross-agent artifact registry.
5. **§5 new row** — `design_note.md` append path when any agent makes a substitution or deletion (cited in econometrics SOP L197 and appdev SOP L540 but not as a named contract).
6. **§2.4 new** — perceptual-check PNG filename convention: `_perceptual_check_{chart_name}.png` alongside the JSON in the same directory.
7. **§9 new** — schema ownership table: which agent owns which `docs/schemas/*.json` file, with version-bump rules (currently spread across rule IDs META-CF, META-XVC, VIZ-V8 owner line, etc.).

---

## Section 4 — Silent Weakening

### SW1. VIZ-IC1 is unenforceable as written — silent no-op risk

Three of the six sub-assertions cannot be executed against the current schema: §4 (palette roles don't exist), §6 (`_manifest.json` does not exist for charts), and §3 requires a date-range check that is not in any helper. If a pair ships with VIZ-IC1 "passed" in the handoff log but the checker skipped the three assertions silently, the rule is worse than absent because it creates false confidence. Recommend: VIZ-IC1 should be blocked from ratification until team-standards.md §2.1, §3, §4 are populated, and a reference implementation `scripts/viz_ic1_check.py` is committed.

### SW2. Prefixed-filename charts never blocked at producer

VIZ-NM1 is declared but no producer-side enforcement exists. Vera (me) produced `indpro_xlp_hero.json` directly at the prefixed path for two pairs without any smoke test catching it, because VIZ-V5 iterates whatever files exist — it does not assert the filename *matches* the registry. Ace's consumer-side smoke test (appdev SOP L1051-1054) would catch it by trying `load_plotly_chart("hero", ...)` and getting `None`, but that only runs on pages Ace has authored. indpro_xlp and umcsent_xlv have no pair pages yet, so nobody has been trying to load these charts. Silent weakening via deferred consumption.

### SW3. META-RYW does not require running VIZ-IC1

META-RYW is a prose re-read rule. VIZ-IC1 is a machine assertion rule. A producer who re-reads thoughtfully but does not execute the VIZ-IC1 asserter may still ship. Recommend cross-referencing: "Vera's META-RYW handoff note MUST include the VIZ-IC1 assertion log."

### SW4. Sidecars not required on newer pairs

indpro_xlp and umcsent_xlv have zero `_meta.json` files. VIZ-V11 says every chart records `palette_id` in its sidecar; these charts have no sidecar. Either these charts pre-date VIZ-V11 (check: they're newer than 2026-04-19) or VIZ-V11 was not retro-applied. Without a gate item ("every pair's chart directory has a sidecar for every chart"), the sidecar rule is advisory.

### SW5. Chart manifest index `output/charts/chart_manifest.json` (appdev SOP L848/L851) does not exist on disk

A consumer-side affordance documented as Vera's output that nobody produces.

---

## Section 5 — Vera-Specific Observations

### V1. Palette registry has 11 role keys but only 4 are referenced by current charts

Audit the registry: `buy_indicator` / `sell_indicator` / `hold_indicator` are declared for APP-SE3 position panels and not yet consumed by any Plotly JSON. `tertiary_data_trace` and `categorical_extended` are used in heatmaps and tournament scatter. All four are load-bearing for future pairs. Keep them — but recognise the registry is under-exercised and semantic drift is likely when a new chart type arrives.

### V2. `color_palette_registry.schema.json` exists but I have not opened it in this review

If it does not permit `aliases` at the palette level, Open Question #3's answer needs a schema bump too. (Action for Wave 10G: open and validate.)

### V3. Chart sidecar schema: no `.schema.json` yet

Every other contract artifact has one. The absence is why `palette_id` / `annotation_strategy_id` / `caption` / `wave_5c_retro` / `narrative_alignment_note` / `events_registry_version` accumulate ad hoc. Proposed fields for the schema are scattered across visualization SOP L827 (formal list) and L670 / L607 / L613 / L641 / L962 (incremental additions). A schema file would force the inventory.

### V4. `wave_5c_retro: true` in `hero_meta.json` is a one-off field

Not part of any published schema. Harmless but illustrative of ad-hoc sidecar drift. A schema would flag `additionalProperties: false`.

### V5. VIZ-IC1 §6's `narrative_alignment_note` is **semantically correct** but **in the wrong file**

The note is chart-level audit metadata — it belongs in `_meta.json`, not `_manifest.json`. The word "manifest" in line 962 is almost certainly a drafting slip by the rule's author (me) at the moment VIZ-IC1 was being written during Wave 10F.

### V6. VIZ-IC1 §3 date-range assertion needs a helper

"Annotations ↔ data" requires extracting x-range from `fig.data` traces and comparing against `layout.annotations[*].x`. That is 20-40 lines of Python that should live in `scripts/viz_ic1_check.py` once, not be re-implemented per chart script. Without a reference implementation, each chart script will skip the check silently.

### V7. Sidecar / JSON twin-file pattern is fragile

`hero.json` and `hero_meta.json` are two files that must be kept in lockstep. When someone `rm hero.json` they often forget `hero_meta.json`. A directory-level manifest (one `_sidecars.json` per chart directory with a dict keyed by chart_name) would halve the filesystem surface and make orphan detection trivial. Worth considering for the schema design.

---

## Section 6 — Vera's Three Open Questions — Authoritative Recommendations

These are the primary input to team-standards.md §2.1, §3, §4. I give recommendation + full reasoning + migration steps.

---

### Q1. Chart filename convention — bare-name vs pair-prefixed + HY-IG v2 duplicates

**Recommendation: BARE-NAME IS CANONICAL. Prefixed duplicates are deleted. The rule is ratified in team-standards.md §2.1 as mandatory with a producer-side and QA-side gate.**

**Reasoning:**

1. **The consumer contract is already bare-name and already anti-fallback.** Appdev SOP L522-528 explicitly forbids the loader from trying prefixed filenames. Changing the loader to accept both is structurally wrong because:
   - it permits two sources of truth per chart (which is fresher?),
   - it lets prefixed-filename drift re-enter the codebase silently, undoing the rule entirely.
2. **`pair_id` in the directory already disambiguates.** The path `output/charts/indpro_xlp/plotly/hero.json` is fully qualified. Repeating `indpro_xlp` in the filename is redundant and forces every downstream tool (loader, smoke test, chart registry) to string-munge the prefix off to recover the chart type.
3. **The chart_type_registry.json `canonical_filename_pattern` values are bare-name.** Changing to prefixed would require mutating every entry in the registry and bumping its `x-version`. The registry is the contract; fighting the contract is wrong.
4. **Sidecars follow the chart name.** A prefixed chart would demand a prefixed sidecar — `indpro_xlp_hero_meta.json` — compounding the string mess.
5. **Only HY-IG v2 has both forms; indpro_xlp and umcsent_xlv are wholly prefixed.** The "dual state" is real but small (10 charts × 2 pairs = 20 files to migrate, plus 13 duplicates to delete in HY-IG v2 = 33 total file ops, zero ambiguity in outcome).

**Migration steps (dispatch to Vera, post-ratification):**

1. **Delete the prefixed duplicates under HY-IG v2.** `git rm output/charts/hy_ig_v2_spy/plotly/hy_ig_v2_spy_*.json` (13 files). These are exact duplicates of the canonical bare-name versions (confirmed: both `hy_ig_v2_spy_hero.json` and `hero.json` exist — the latter is what Ace's loader actually consumes). If the prefixed version has drifted content, reconcile into the bare-name version first, then delete.
2. **Rename indpro_xlp charts in place:** `for f in indpro_xlp/plotly/indpro_xlp_*.json; do git mv "$f" "$(echo $f | sed 's/indpro_xlp_//')"; done`. Produces `hero.json`, `ccf.json`, etc. Note: `ccf.json` is the bare name; check chart_type_registry — it's `ccf_prewhitened.json`. **So also rename `indpro_xlp_ccf.json` → `ccf_prewhitened.json` if the content matches CCF semantics**, otherwise flag as a method-chart-mismatch finding.
3. **Same for umcsent_xlv.** Cross-check `wf_sharpe.json` against registry — not in current registry; either add an entry or rename to a registered chart type.
4. **Generate missing `_meta.json` sidecars for the 20 renamed charts.** Required fields per VIZ-V11 / VIZ-V13: `palette_id`, `annotation_strategy_id`, `caption`, `chart_type`, `pair_id`, `owner`, `produced_on`.
5. **Add producer-side enforcement:** `scripts/hooks/check_chart_filename.sh` — for every file under `output/charts/*/plotly/*.json`, assert basename matches a `canonical_filename_pattern` in `chart_type_registry.json` (resolve `{episode_slug}` wildcards). Wire as pre-commit and as a GATE item in QA SOP.
6. **Add QA-side enforcement:** extend Quincy's GATE-27 / GATE-28 cloud verify to `git ls-files output/charts/*/plotly/` and reject any filename containing the pair_id as a prefix.
7. **Document in team-standards.md §2.1:** `output/charts/{pair_id}/plotly/{chart_type}.json` — pair_id in directory ONLY. Prefixed filenames are prohibited. Migration completed <date>; gate enforced from Wave 10G.

---

### Q2. Sidecar naming — `_meta.json` vs `_manifest.json`

**Recommendation: `_meta.json` for chart sidecars; `_manifest.json` for dataset / model sidecars. They stay distinct. Fix VIZ-IC1 §6 to say `_meta.json`.**

**Reasoning:**

1. **They describe different object types.** A chart sidecar carries: caption, palette_id, annotation_strategy_id, events_registry_version, narrative_alignment_note, audience_tier, portal_page. A dataset sidecar carries: column semantics, units, sign conventions, sanity-check assertions, producer script. These are different schemas with minimal field overlap; unifying the name would force one schema to carry both field sets or force consumers to branch on artifact type anyway.
2. **Usage in the codebase is already asymmetric and stable.**
   - Chart sidecars: 10 files in HY-IG v2, all `_meta.json`. Every visualization SOP reference (8 occurrences) says `_meta.json`. Every appdev SOP consumer reference (L495, L830) says `_meta.json`.
   - Dataset sidecars: econometrics SOP has 4 occurrences, all `_manifest.json`. `tournament_manifest.json` is a live file name. Data SOP conventions align.
3. **The semantic distinction has precedent.** In package ecosystems, `META-INF/MANIFEST.MF` is a packaging descriptor (what files are here, how to load them) while `meta.yaml` / `_meta.json` is descriptive metadata (what the content means). Vera's chart sidecar is descriptive; Evan's dataset sidecar is a loading contract with assertions. Keeping the names distinct preserves a useful semantic cue.
4. **VIZ-IC1 §6's `_manifest.json` reference is a drafting slip.** The narrative_alignment_note is chart-descriptive content. Every other field VIZ-IC1 touches lives in `_meta.json`. Correcting the word is cleaner than migrating 10 sidecars + all consumers.
5. **A chart `_manifest.json` (index file, appdev SOP L848/L851) at the directory level is a **third** object type** — a directory listing, not a per-chart sidecar. If we want that, call it `chart_index.json` to avoid collision with the dataset convention. Today it does not exist on disk, so no migration.

**Migration steps (dispatch post-ratification):**

1. **Edit visualization SOP L962** — change `_manifest.json` → `_meta.json` in VIZ-IC1 §6.
2. **Add chart sidecar JSON schema** — create `docs/schemas/chart_sidecar.schema.json` (owner: Vera) enumerating: `chart_type` (required), `pair_id` (required), `caption` (required), `palette_id` (required, must resolve in palette registry), `annotation_strategy_id` (required when ≥2 annotations), `events_registry_version` (required for zoom charts), `narrative_alignment_note` (required when chart is in a narrative), `audience_tier`, `portal_page`, `owner`, `produced_on`, `source_script`, `rules_applied[]`. `additionalProperties: false`.
3. **Validate existing HY-IG v2 sidecars against the new schema** — expected to fail minor fields (the `wave_5c_retro` ad-hoc flag). Either add to schema as optional or remove from sidecars.
4. **Document in team-standards.md §3**: chart sidecars = `{chart_name}_meta.json`, schema at `docs/schemas/chart_sidecar.schema.json`; dataset sidecars = `{artifact}_manifest.json`, schema per ECON-DS2. The two names are intentionally distinct; do not unify.
5. **Optional §3 addendum:** directory-level chart index at `output/charts/{pair_id}/plotly/_index.json` (if team wants it) — not required, not `_manifest.json` to avoid overload.

---

### Q3. Palette role aliases — add aliases or rewrite VIZ-IC1?

**Recommendation: ADD SEMANTIC ALIASES to the palette registry. Do not rewrite VIZ-IC1. This is the smaller, more durable fix.**

**Reasoning:**

1. **The two classes of role key serve different consumers.**
   - Existing keys (`primary_data_trace`, `secondary_data_trace`, `equity_curve`, `buy_indicator`, etc.) are **visual-encoding** roles — they describe *how* a color is used on a chart.
   - Proposed aliases (`indicator`, `target`, `benchmark`) are **semantic** roles — they describe *what the plotted thing is in the pair's domain*.
   Both are load-bearing: a chart script needs visual-encoding roles to pick colors; VIZ-IC1 needs semantic roles to audit that the indicator line is the vermillion color and not accidentally the blue one.
2. **Aliases are additive, not disruptive.** An alias dict `{"indicator": "primary_data_trace", "target": "secondary_data_trace", "benchmark": "equity_curve"}` added to the palette JSON makes VIZ-IC1 executable today without renaming a single existing key and without invalidating any chart script that currently references `primary_data_trace`.
3. **Rewriting VIZ-IC1 to use visual-encoding keys loses meaning.** "The indicator series uses `primary_data_trace`" is circular — it says "the primary trace is the primary trace." The audit value of VIZ-IC1 §4 is the assertion that the **pair's indicator** (as declared in `interpretation_metadata.json.indicator_symbol`) is **rendered** in the primary color. That requires the two naming levels.
4. **Benchmark** is a genuine third semantic role that does not have a clean visual-encoding analog. `equity_curve` is the closest but is strategy-page-specific. Proposed: use `equity_curve` for benchmark on strategy pages, introduce a new `benchmark_trace` visual-encoding key for non-strategy pages (equal to `tertiary_data_trace` value) so the alias resolves cleanly.
5. **This is the pattern other portal registries follow.** `expander_title_registry.json`, `caption_prefix_vocab.json`, and `signal_code_registry.json` all have a semantic→canonical indirection. The palette registry is the outlier in hard-coding visual-encoding as the only key level.

**Migration steps (dispatch post-ratification):**

1. **Extend `color_palette_registry.json`** — add to the `okabe_ito_2026` palette object:
   ```
   "aliases": {
     "indicator": "primary_data_trace",
     "target": "secondary_data_trace",
     "benchmark": "equity_curve"
   }
   ```
   Bump `x-version` to `1.1.0`.
2. **Extend `color_palette_registry.schema.json`** — add optional `aliases` property (object, values must be keys in the same palette, validated by `$data` or a custom check).
3. **Publish resolver helper** — `scripts/viz/palette_resolver.py::resolve(role, palette_id)` that accepts alias or canonical key and returns the hex. Every chart script and VIZ-IC1 checker uses this single function so alias consistency is centralized.
4. **Update VIZ-IC1 §4 prose only lightly** — change "the pair's indicator series uses the `indicator` role color (which aliases to `primary_data_trace` in the registry)" to make the indirection explicit. No logic change.
5. **Document in team-standards.md §4** — list the three aliases with their canonical targets; note that aliases are the semantic-audit interface and canonical keys are the visual-encoding interface.
6. **(Optional) Add per-pair overrides** — future pairs where benchmark ≠ SPY may want a pair-level alias override. Defer until a pair forces the question.

---

## Section 7 — Priority Ranking (Top 5 Fixes)

Ordered by (impact on next pair shipping) × (unambiguity of the fix):

1. **P1 — Ratify bare-name filename rule and migrate indpro_xlp + umcsent_xlv + delete HY-IG v2 prefixed duplicates.** (§6 Q1.) Without this, the next pair (pair #4) has no clear rule to follow and Ace's loader will continue to miss charts silently. 33 file operations, under an hour, unblocks the largest class of current drift.
2. **P2 — Add palette aliases (`indicator`, `target`, `benchmark`) to `color_palette_registry.json`.** (§6 Q3.) One schema edit + one version bump. Makes VIZ-IC1 §4 executable. Without this, VIZ-IC1 ships as a silent no-op (SW1).
3. **P3 — Fix VIZ-IC1 §6 `_manifest.json` → `_meta.json` drafting slip and create `docs/schemas/chart_sidecar.schema.json`.** (§6 Q2 + V3.) One-line SOP edit plus one new schema file. Eliminates the naming contradiction and gives every future chart sidecar a validated shape.
4. **P4 — Reference implementation `scripts/viz_ic1_check.py` + wiring into pre-commit + Vera's META-RYW handoff template.** (§V6 + SW3.) Without it the six VIZ-IC1 assertions are "by hand" per chart script, which will decay. Ship the checker once, reuse it across all pairs.
5. **P5 — Retro-apply sidecars to indpro_xlp and umcsent_xlv charts once they are renamed.** (§SW4.) 20 new `_meta.json` files, each with palette_id + caption + annotation_strategy_id. Clears the VIZ-V11 gap silently accrued on two pairs. Depends on P1 (rename first) and P3 (schema ready).

Honorable mentions (not top-5 but worth scheduling): purge `override_supported` from chart_type_registry schema (C5); retire or implement `output/charts/chart_manifest.json` (SW5); add `_perceptual_check_*.png` as a contract artifact in team-standards.md §5 (§3 item 4); resolve the `matplotlib_legacy` grandfathering vs VIZ-V5 smoke rule conflict (C4) by adding a `matplotlib_legacy` palette entry with `colorblind_safe: false` and an `audit_flag: true` marker.

---

**Word count:** ~2,650 (Section 6 deliberately expanded per dispatch guidance).
**File-path citations:** all paths are absolute under `/workspaces/aig-rlic-plus/` unless otherwise noted.
**No SOP or chart JSON edits made in this review** — findings only, per constraints.
