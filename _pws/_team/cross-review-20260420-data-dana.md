# Cross-Review Findings — Data Dana (2026-04-20)

**Reviewer:** `data-dana`
**Scope:** team-coordination.md, 5 producer SOPs, qa-agent-sop.md, team-standards.md (stub)
**Method:** Full read of team-coordination.md + data-agent-sop.md; targeted grep + spot-reads across the other five SOPs for naming, sidecar, palette, handoff, and META-rule references.

---

## Section 1: Conflicts

### C1. Sidecar naming: `_meta.json` vs `_manifest.json` (hard conflict)

- `visualization-agent-sop.md:107` calls the viz sidecar `_manifest.json` in one breath ("Artifact manifest (`_manifest.json` sidecar) — column semantics…") and, everywhere else in the same file (L143, L455, L457, L613, L735, L827, L1035), calls the chart sidecar `_meta.json`. Internal inconsistency inside Vera's own SOP.
- `econometrics-agent-sop.md:156, 450, 693, 1149, 1162` uses `_manifest.json` for model/tournament/signals artifacts.
- `appdev-agent-sop.md:830, 841, 848` consumes `_meta.json` for chart sidecars AND `chart_manifest.json` as a registry.
- `team-coordination.md:1202` reinforces `_manifest.json` for model artifacts; `team-coordination.md:82` (handoff table) writes `chart_{name}_meta.json`.
- `visualization-agent-sop.md:962` says Vera writes `narrative_alignment_note` into `_manifest.json` — but the sidecar schema defined a few pages up says `_meta.json`. Vera writes to a file that does not exist per her own rule A3.

**Recommended resolution (matches team-standards.md §3 proposal):**
- Chart sidecar: `{chart_name}_meta.json` (Vera). Canonical.
- Dataset/model/tournament sidecar: `{artifact}_manifest.json` (Dana, Evan).
- Fix viz-sop L107 and L962 (and reviews/*) to use `_meta.json` consistently.
- Dana's `data/manifest.json` (section §6, DATA-D13) is the **portfolio-level registry**, distinct from per-artifact `_manifest.json`. Keep as-is, but call it out in team-standards §3 so no one conflates the two.

### C2. Chart filename convention — bare-name vs pair-prefixed (declared resolved but unevenly applied)

- `visualization-agent-sop.md:1076` (VIZ-NM1): "Canonical path: `output/charts/{pair_id}/plotly/{chart_type}.json` — pair_id appears ONLY in the directory path, NEVER in the filename." Bare-name is canonical.
- `visualization-agent-sop.md:1083` explicitly lists `hy_ig_v2_spy/plotly/hy_ig_v2_spy_correlation_heatmap.json` as the **wrong** pattern.
- But on disk HY-IG v2 still carries both bare and pair-prefixed duplicates; GATE-28 and APP-CN1 reference `load_plotly_chart(name, pair_id)` which assumes bare-name. No SOP rule explicitly mandates deletion of the duplicate set.
- `team-standards.md §2.1` correctly flags this as unresolved.

**Recommended resolution:** team-standards.md §2.1 mandates bare-name, and adds a one-line retro-apply task: "Delete pair-prefixed duplicates in HY-IG v2; any reference to a prefixed filename in `app/pages/` or `app/components/` is a VIZ-NM1 violation caught by APP-CN1."

### C3. Chart color role keys — registry vocabulary vs VIZ-IC1 verifier

- `docs/schemas/color_palette_registry.json` canonical role keys: `primary_data_trace`, `secondary_data_trace`, `equity_curve`, `drawdown_fill`, `quartile_gradient`, `nber_shading` (per viz-sop L590 and team-standards §4).
- `visualization-agent-sop.md:960` (VIZ-IC1): "The pair's indicator series uses the `indicator` role color; the target series uses the `target` role color; benchmark series use the `benchmark` role color."
- The keys `indicator`, `target`, `benchmark` are **not in the registry**. VIZ-IC1 as written cannot pass a palette-conformance check against the actual registry.

**Recommended resolution:** add semantic aliases to the registry per team-standards §4 proposal (`indicator`→`primary_data_trace`, `target`→`secondary_data_trace`, `benchmark`→ a new dedicated key if visually distinct from equity_curve).

### C4. Classification vocabulary drift

- `team-coordination.md §20` locks `indicator_type` to 7 values (`price, production, sentiment, rates, credit, volatility, macro`) and explicitly REJECTS near-synonyms (`activity, output, vol, fx`).
- `data-agent-sop.md:226` (Rule D3 Step 2) says "Evan's SOP also references `activity` as a near-synonym for `production/macro`." — this is the near-synonym §20 explicitly rejects.
- Either Evan's SOP still carries `activity` (needs removal) or Dana's SOP is quoting stale Evan text.

**Recommended resolution:** Grep Evan's SOP for `activity` and delete any occurrence as a category label; tighten Dana Rule D3 Step 2 to say "any near-synonym is a D3 violation per team-coordination §20."

### C5. Interpretation metadata write-ownership timing

- `team-coordination.md` Classification Field Ownership table (line ~752) says Ray writes `strategy_objective` "After tournament results known."
- `data-agent-sop.md:519` (DATA-D6 procedure) says merge order is `dana → evan → ray`.
- Neither SOP states explicitly what happens if Ray's write overlaps an Evan rerun — file-level lock? Append-only? Evan's tournament rerun silently overwrites Ray's `strategy_objective`?

**Recommended resolution:** team-standards.md §5 (or a new §9) adds a one-paragraph merge protocol: each writer only touches their `owner_writes` fields; `last_updated_by` / `last_updated_at` updated atomically; QA-CL3 / GATE-31 verifies no agent writes outside their ownership.

### C6. "Defense 1/2" naming collision

`data-agent-sop.md:668` has Defense 1 (Self-Describing Artifacts) / Defense 2 (Reconciliation at Boundary). Ace's SOP (inferred from grep context) uses "Defense 1/2" as portal render/loader defenses. Same label, different meaning.

**Recommended resolution:** prefix with agent scope (DATA-DEF1, APP-DEF1). Low priority but creates confusion when searching.

---

## Section 2: Redundancies

### R1. EOD reflection block duplicated verbatim across all 5 SOPs

`data-agent-sop.md:766`, `visualization-agent-sop.md:1169`, `appdev-agent-sop.md:1273`, `econometrics-agent-sop.md:1253`, `research-agent-sop.md:1097` all carry the same three-step "flag cross-role insights" paragraph. Already codified in team-coordination.md §META-AM and the Mandatory Dispatch Template. **Canonical home:** team-standards.md §6 with a one-line `See team-standards §6` stub in each SOP.

### R2. Handoff templates duplicated between each SOP and team-coordination.md

Dana's SOP lines 270-334 replicate the Data→Econ / Data→Viz / Data→AppDev templates already present in team-coordination.md Primary Pipeline Handoffs section. Same for Evan, Vera, Ray, Ace. **Canonical home:** team-coordination.md. SOPs should link.

### R3. Deliverables completeness gate items 19-22 repeated in Dana and Ray SOPs

`data-agent-sop.md:482` restates items 19, 20 (Dana-owned); Ray's SOP presumably restates 21, 22. Fine for local cross-reference but the substance is in team-coordination.md §Deliverables Completeness Gate. Keep one-line pointers, drop the restated full text.

### R4. META-SRV evidence block format

Appears in team-coordination.md §META-SRV plus scattered in every SOP's "quality gates" section. Canonical: team-coordination.md. Everywhere else: "per META-SRV evidence discipline."

### R5. Unit registry (Dana Rule D2) is the source, but Vera VIZ-A2 and Ray RES-4 silently re-describe it

Dana's D2 registry table at `data-agent-sop.md:236-248` is the single source. VIZ-A2 and RES-4 cite D2 in prose but should never restate the table. Keep a cross-ref only.

### R6. Directory layout

Dana SOP §Output Standards, team-coordination.md §Shared Workspace Structure, team-standards.md §1 all describe the same tree. Canonical = team-standards.md §1.

---

## Section 3: Rules That Belong in team-standards.md

The following are authored in a single agent's SOP but bind every agent — they are team-level conventions masquerading as local rules.

### S1. Classification vocabulary enum (indicator_nature / indicator_type / strategy_objective)
Currently scattered: Dana SOP D3, team-coordination gate items 19-21. The controlled enum list is team-wide contract consumed by Dana (writer), Ray (writer), Evan (C1 routing), Ace (landing chip), Quincy (GATE-31 audit). Move the enum table to team-standards §5 or new §9; all SOPs cross-ref.

### S2. Unit suffix registry (Dana D2 / D12)
Dana authors it, but Vera (axis labels), Ray (narrative notation), Ace (KPI formatting), Evan (signal threshold formatting), Quincy (KPI triangulation QA-CL2) all consume it. team-standards.md §4.5 (new) would house the suffix table.

### S3. Color palette role keys + semantic aliases
Currently in viz-sop. Every render consumer reads via `_meta.json.palette_id`. Add to team-standards §4 with the alias mapping (resolves C3 above).

### S4. Chart filename convention (VIZ-NM1)
Currently viz-sop L1076. Also binds Ace loader, Quincy GATE-28 audit. team-standards.md §2.1.

### S5. Sidecar schema naming (_meta vs _manifest)
Currently implicit and conflicting. team-standards.md §3 — single table: "artifact type → sidecar filename → producer → schema."

### S6. Schema versioning contract (META-CF, META-SCV, META-UC)
Currently only in team-coordination.md but deeply touches every consumer's validation call. Keep authorship in team-coordination (the meta rules are sprawling) but team-standards.md §3 or §5 should carry a one-line "every artifact validates_or_die against its contract before save and before use."

### S7. `data/manifest.json` and `data/display_name_registry.csv`
Portfolio-level registries produced by Dana, consumed by every other agent. DATA-D13 authors this in Dana's SOP but it is a team asset. Move the "what this file is / who consumes it" description to team-standards §1 (or a new §2.4 Registries). Dana keeps the producer-side procedure.

### S8. `interpretation_metadata.json` ownership map
The `owner_writes` object and merge order (dana→evan→ray) lives in Dana's Rule D6. It is a cross-agent contract. team-standards.md §5 artifact registry should carry "writer agents + field ownership + merge order" per artifact.

### S9. Directory layout (already in team-standards §1 ✓)
Keep here; remove duplicates from SOPs.

---

## Section 4: Silent Weakening

Rules that exist as prose but have no automatic enforcement, with my honest assessment of actual compliance:

| Rule | Stated where | Enforcement | Honest status |
|---|---|---|---|
| **DATA-D13** (`data/manifest.json` and `data/display_name_registry.csv` must exist and validate) | Dana SOP L586 | None on disk yet — rule itself notes "Not created yet at this rule's authoring moment" | **Dead letter.** Authored April, none of the three existing completed pairs (INDPRO, VIX, HY-IG v2) have a valid manifest. I should own the bootstrap this wave. |
| **DATA-D11** (reference-pair sidecar gate) | Dana SOP L528 | `validate_schema.py` exists; no CI hook | **Partially followed.** I run it manually on my waves; unclear whether it was run for HY-IG v2. |
| **DATA-D12** (column-suffix linter) | Dana SOP L548 | "pre-save linter" described but no actual script in `scripts/` | **Dead letter.** The linter script does not exist. The rule is a checklist item without a checker. The exact failure mode (`hy_ig_spread` without suffix) is still on disk. |
| **D1 Series Preservation on Reruns (column diff)** | Dana SOP L620 | Manual | **Probably followed** on Dana's own reruns but no automated diff script. Would fail silently if a future Dana instance skipped it. |
| **VIZ-IC1 palette conformance** | viz-sop L960 | Role keys reference nonexistent registry aliases (C3) | **Unverifiable** until C3 resolved. |
| **GATE-24 Chart-Text Coherence** | team-coord L112 | "grep -r `<chart_name>` app/pages/" — manual grep per chart edit | **Practiced inconsistently.** No pre-commit hook. Relies on Vera's memory to notify Ray. |
| **GATE-30 Deflection Link Audit** | team-coord L118 | Playwright DOM assertion described; no harness script | **Partially followed** — Quincy re-audits at acceptance; no scheduled regression check if target pages later move. |
| **META-SRV evidence blocks** | team-coord L532 | QA-CL3 post-hoc check | **Followed** when dispatched with mandatory EOD template. Prior-wave regression notes (before April) often lack evidence blocks. |
| **META-AM (experience.md / memories.md)** | team-coord L630 | PostToolUse hook at `~/.claude/hooks/check-agent-eod.sh` | **New and now enforced.** Wave 9B audit found 5 of 6 agents had zero cumulative entries. Hook is fresh; compliance trajectory unproven. |
| **META-FRD (force-redeploy ≤ 2x/quarter)** | team-coord L295 | None — log in pair_execution_history | **Unverified.** No counter. A future Lead could exceed without detection. |
| **META-UC consumer inventory at schema migration** | team-coord L580 | QA-CL2 display-layer check catches drift; no pre-commit check | **Followed** when migration is remembered; the Wave 4D-1 incident that motivated the rule is exactly the pattern that could recur. |

---

## Section 5: Dana-Specific Observations

From my role's lens — sourcing, cleaning, producing `interpretation_metadata.json`, sidecars, and classification fields:

1. **I am the write-point for classification fields that four other agents consume at runtime.** `indicator_nature` and `indicator_type` flow into Evan's C1 method router, Ray's narrative, Vera's palette role inference, and Ace's landing-card chip. A silent drift in my output breaks four downstream pipelines. Yet the controlled vocabulary (§20) lives in team-coordination and the routing logic (C1) lives in Evan's SOP — I have to tri-link to write a correct value. **Fix:** team-standards §5 should carry a single "classification field registry" table: field name → enum values → writer → readers → consumer behavior if missing.

2. **The `_latest` alias convention is my load-bearing contract with Ace but is described only in Dana SOP §6.** Ace's cache TTL resolver, the portal page loader, and Streamlit Cloud's builder all depend on stable paths. **Fix:** promote `_latest` alias rules to team-standards §2.2.

3. **DATA-D11 / D12 / D13 are interlocking schema-sidecar gates but the schemas are not all on disk.** `docs/schemas/data_subject.schema.json`, `interpretation_metadata.schema.json` exist; `data_manifest.schema.json` and `display_name_registry.schema.json` — I need to verify whether these exist. If not, the rules that validate against them are unrunnable. **Action for me:** Wave 10F/11 bootstrap — create missing schemas, generate sidecar instances for all three completed pairs, delete grandfather clauses.

4. **Unit form × enum rename × direction sign — META-UC's three trigger modes all touch me at source.** I am the producer at the inflection point. Wish team-standards carried a "Dana pre-save checklist if any of (unit/enum/direction) changed" that forces the consumer-inventory grep before save, not at migration-commit as META-UC states (too late — by then my parquet is already on disk).

5. **I wish documented:**
   - Whether mixed-freq parquets should be split (one file per frequency) or kept wide with a `_days_since_release` column. Both patterns exist; no rule.
   - Whether `data/manifest.json` or a per-pair manifest is canonical when the same indicator serves multiple pairs (INDPRO serves INDPRO×SPY, INDPRO×XLP, INDPRO×XLI).
   - A source-attribution field in the sidecar for derived columns (I currently put this in `description`; no schema requirement).

---

## Section 6: Opinions on Vera's VIZ-IC1 Retro-Apply Open Questions

### Q1. Chart filename: bare-name vs pair-prefixed

**Bare-name is correct.** VIZ-NM1 is already written correctly (L1076); Ace's loader `load_plotly_chart(name, pair_id)` is already written for bare-name. Pair-prefixed is a historical artifact of the HY-IG v2 period.

**Reasoning:** (a) `pair_id` is already in the directory path — duplicating it in the filename is redundant and creates the exact class of drift we are seeing. (b) Bare-name makes cross-pair chart-type registries (VIZ-V8) trivially consistent — the registry keys on `chart_type`, not `{pair_id}_{chart_type}`. (c) A rerun of a pair does not rewrite the directory path but would rewrite a prefixed filename inconsistently.

**Action:** team-standards §2.1 declares bare-name canonical; HY-IG v2 duplicate prefixed files are deleted in a single commit with regression note citing VIZ-NM1.

### Q2. Sidecar naming: `_meta.json` vs `_manifest.json`

**Two canonical names, each with a clear role:**
- `{chart_name}_meta.json` — Vera's chart sidecar (small, per-chart, stable schema).
- `{artifact}_manifest.json` — Evan/Dana's dataset or model sidecar (larger, per-data-artifact, carries sanity assertions).

**Reasoning:** they carry different content (chart metadata vs dataset semantics+assertions), are produced by different agents, and have different lifecycles. Forcing one name creates ambiguity in grep. The conflict today is not between the two names but that `visualization-agent-sop.md:107` and `962` accidentally use `_manifest` where the rest of Vera's SOP uses `_meta`. Fix those two lines; canonicalize both in team-standards §3.

### Q3. Palette role aliases

**Yes — add `indicator` / `target` / `benchmark` as aliases.**

Proposed mapping:
- `indicator` → `primary_data_trace`
- `target` → `secondary_data_trace`
- `benchmark` → new dedicated key (not `equity_curve` — equity curve is already used for strategy output; benchmark is the passive B&H line, semantically distinct).

**Reasoning:** the registry's current keys (`primary_data_trace`, `equity_curve`) mix two ontologies — one visual-role-based, one chart-type-based. VIZ-IC1 was authored in the *semantic* ontology (indicator/target/benchmark) because that is how Vera actually thinks about the page. Forcing her to translate every check makes VIZ-IC1 read-unfriendly. Aliases give the registry one canonical key per role plus a human-readable front door.

**Caveat:** if `benchmark` gets its own key, need a design note clarifying that `equity_curve` is strictly the realized-strategy line and `benchmark` is the B&H reference. Else Ace's Strategy page might use the wrong one.

---

## Section 7: Top 5 Fixes I'd Prioritize as Lead

1. **Bootstrap `data/manifest.json` + `data/display_name_registry.csv` + the two missing schemas for the three completed pairs.** Impact: closes DATA-D11/12/13 simultaneously and makes VIZ-A2, APP-TC1, RES-4 verifiable. Ease: one Dana wave, 2-3 hours. I can own this.

2. **Fix `visualization-agent-sop.md` lines 107 and 962 to say `_meta.json`** — and add the sidecar-naming canon table to team-standards §3. Impact: closes C1, eliminates the biggest source of downstream confusion. Ease: 10-minute edit.

3. **Add semantic aliases (`indicator`/`target`/`benchmark`) to `docs/schemas/color_palette_registry.json`.** Impact: makes VIZ-IC1 runnable as written; unblocks Vera's palette-conformance lint. Ease: one JSON edit + one regression note.

4. **Write the DATA-D12 column-suffix linter script** (`scripts/lint_column_suffixes.py`) and wire it into the pair-pipeline pre-save path. Impact: promotes a dead-letter rule to enforced; prevents the next `hy_ig_spread`-class bug. Ease: half-day of Python.

5. **Extract the classification-field registry to team-standards §5** (field → enum → writer → readers → merge order), and collapse the three partial restatements in Dana/Ray/team-coord into cross-refs. Impact: single source of truth for the rule that most often silently drifts. Ease: copy-paste + cross-ref edits.

---

## Evidence block (per META-SRV)

- File: `/workspaces/aig-rlic-plus/_pws/_team/cross-review-20260420-data-dana.md`
- Verification: `wc -l /workspaces/aig-rlic-plus/_pws/_team/cross-review-20260420-data-dana.md`
- Expected: >200 lines
- Files read this wave: CLAUDE.md, team-coordination.md (full L1-1050 + spot-reads), data-agent-sop.md (full), visualization-agent-sop.md (grep + spot-reads L107-1085), econometrics-agent-sop.md (grep + spot), appdev-agent-sop.md (grep + spot), research-agent-sop.md (grep only), qa-agent-sop.md (grep + L34-293), team-standards.md (full L1-141).
