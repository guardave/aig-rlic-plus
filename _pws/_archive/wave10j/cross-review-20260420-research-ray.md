# Cross-Review Findings — Research Ray — 2026-04-20 (Wave 10F)

Reviewer: `research-ray`
Scope: `team-coordination.md`, all six agent SOPs, `docs/team-standards.md` (stub), `docs/sop-changelog.md`.
Vantage: narrative author / META-CF frontmatter producer / RES-NR1 owner.

All citations below use `<file>:<line>` form where practical.

---

## Section 1 — Conflicts

**1.1 Sidecar filename: `_meta.json` vs `_manifest.json` (real, bidirectional conflict).**
Vera's SOP uses both names for the same artifact class. `visualization-agent-sop.md:143,455,483,613,670,735,827,1035` all say `{chart_name}_meta.json`, and VIZ-V8 explicitly names it the "metadata sidecar schema." But the VIZ-IC1 specification at `visualization-agent-sop.md:962` says Vera writes the narrative-alignment note into `{chart}_manifest.json`. `team-standards.md:49-54` correctly identifies the conflict and proposes `_meta.json` for charts, `_manifest.json` for datasets — but that proposal is not yet in force and `VIZ-IC1` still points at `_manifest.json`. This is an active ship-blocking ambiguity: a producer following VIZ-V8 and a consumer following VIZ-IC1 will never meet.

**1.2 Chart filename convention: bare-name vs pair-prefixed.**
`VIZ-NM1` (per `sop-changelog.md:217-225`) says pair_id appears only in directory path, never in filename. HY-IG v2 ships both forms (bare and prefixed). `team-standards.md:35` acknowledges the conflict and holds it open. Meanwhile `team-coordination.md:115-117` (GATE-27/28) asserts that `load_plotly_chart(name, pair_id)` must resolve — which implicitly assumes bare-name, because pair_id is passed separately. The bare-name convention is already structurally required by the loader signature; the conflict is with the on-disk duplicates, not with the rule itself.

**1.3 History-zoom chart path: superseded text still present.**
`research-agent-sop.md:672` directs me to inspect `output/_comparison/history_zoom_{episode_slug}.json` at narrative handoff. That path was explicitly superseded by `META-ZI` Wave 6B (`team-coordination.md:223-238` — "there is no canonical rendered chart to 'start from' and no `_comparison/` fallback"). My SOP still carries the old inspection instruction. A literal reading of Ray's SOP will send me to a path the system has been told to stop emitting.

**1.4 `interpretation_metadata.json` ownership and population point.**
`team-standards.md:80` names Dana as producer of `interpretation_metadata.json`. `team-coordination.md:107-109` (items 19-21) says Dana owns `indicator_nature` and `indicator_type`, but Ray owns `strategy_objective` — **after tournament results are known**. `research-agent-sop.md:287-293` repeats this split. The artifact is therefore **co-owned across two phases** (Dana at data stage, Ray at post-tournament stage), but `team-standards.md` presents it as single-producer. Consumers (Ace, Vera) cannot tell from the standards table which fields are populated at which handoff — this creates a real race condition when Vera reads the file before Ray has written `strategy_objective`.

**1.5 Narrative markdown vs `pair_configs/` — two authoring surfaces, one author.**
`RES-NR1` (`research-agent-sop.md:425-436`) says narrative lives in `app/pair_configs/{pair_id}_config.py`. `RES-17` (`:467-487`) says narrative lives in `docs/portal_narrative_{pair_id}_{date}.md` with a blocking frontmatter contract. Both claim to be the authoritative narrative location. In practice the Wave 10E post-mortem (memories.md) shows prose actually rendered from the `.py` config — the markdown file was advisory. This is a real conflict: RES-17's frontmatter validation has no teeth if prose ships from `.py`, and RES-NR1's instrument audit must run on the `.py`, not the `.md`. BL-004 (noted in my memories) is the architectural fix pending.

---

## Section 2 — Redundancies

**2.1 RES-17 vs team-standards.md §5 vs research-agent-sop.md "App Dev Handoff" — triple frontmatter restatement.**
The frontmatter contract exists in three places: the schema file, RES-17 prose (`research-agent-sop.md:467-487`), and the App Dev Handoff section (`research-agent-sop.md:329-341`). The App Dev Handoff section largely duplicates RES-17's required-field list. Per META-CF ("schema file is the single source of truth"), the prose should collapse to a pointer.

**2.2 Narrative-alignment notes duplicated between sidecar and handoff message.**
VIZ-IC1 asks Vera to write a narrative-alignment note into the chart sidecar. META-RYW (Wave 10F, `sop-changelog.md:17`) asks every producer to log a re-read in the handoff note, covering chart-narrative coherence. Both are evidence of the same check. If Vera is the only one who can verify chart↔title↔axes, fine — but META-RYW across Vera+Ray+Ace will produce three independent logs of roughly the same claim without a named authoritative entry.

**2.3 Instrument-accuracy rules: RES-NR1, APP-DIR1 triangulation, GATE-NR all overlap.**
RES-NR1 (producer) + APP-DIR1 (direction triangulation, consumer) + GATE-NR (QA DOM scan) all enforce a variant of "narrative references match canonical metadata." The overlap is arguably defense-in-depth, but the three rules use slightly different field names (`target_symbol` vs `indicator` vs `indicator_id`) and the authoritative mapping is not in one place.

**2.4 Status vocabulary lives in three files.**
RES-10, RES-VS, RES-22 (`research-agent-sop.md:537-562`), plus `docs/portal_glossary.json._status_vocabulary`, plus Dana's DATA-VS. A single canonical vocabulary file with one-line definitions would eliminate the need for three parallel rule bodies.

**2.5 Regression-note templates.**
`team-coordination.md:175-216` (Regression Note Format + META-VNC + META-XVC "Methodological divergence" block) and Ray's Rule 5 regression-prevention recipe (`research-agent-sop.md:631-643`) overlap heavily. Ray's recipe should cite the team-coordination template and add only the Ray-specific steps (prior_methods CSV build).

---

## Section 3 — Rules That Belong in `team-standards.md`

Items currently scattered across agent SOPs that are truly cross-agent conventions:

1. **Canonical status vocabulary** (Available / Pending / Validated / Stale / Draft / Mature / Unknown). Currently in RES-10 + RES-22 decision table + DATA-VS. Move the list + the condition→label decision table here; let RES/DATA SOPs cite it.
2. **Sidecar filename contract** (`_meta.json` for charts, `_manifest.json` for datasets, with the exact required keys `palette_id`, `events_registry_version`, `annotation_strategy_id`, `narrative_alignment_note`, etc.). Currently in VIZ-V8 + VIZ-IC1 + VIZ-SD1 only.
3. **Palette role → registry key mapping** (`indicator`, `target`, `benchmark` → palette keys). Vera's SOP defines roles; team-standards.md §4 is where the alias map should live so Ray and Ace can cite the same names.
4. **`interpretation_metadata.json` two-phase field ownership table** (which fields are written at which handoff, by whom).
5. **Historical-episode registry** (slug list — `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`). Ray's RES-20 requires the triad; Vera's VIZ-V12 holds the registry. The slug list itself is cross-agent.
6. **META-ELI5 pairing rule** (every user-visible technical label must have a plain-English sibling from the glossary). Currently buried in RES-22 rule 3; applies to Ace's rendering and Quincy's gate.
7. **META-XVC six-field divergence block schema**. Currently only in team-coordination.md prose; should be a named schema file.
8. **Dispatch template** — already in team-standards.md §7, but the required fields `AGENT_ID`, `SOD Block`, `MANDATORY EOD` should be a validator-checked schema, not a prose block.

---

## Section 4 — Silent Weakening

**4.1 RES-17 glossary-request-back SLA has no enforcement.**
`research-agent-sop.md:479-483` says "Silence is not acceptance. An unaddressed Ace request past the one-week SLA is a RES-17/RES-6 violation." But no mechanical gate checks for overdue entries. `glossary_requests` is an optional frontmatter field; if I never add it, nobody notices. The SLA is honor-system. This is silent-weakening territory: the rule looks hard but is soft in practice.

**4.2 RES-20 historical-episode triad is verified by schema only if `selection_rationale` is populated.**
If a narrative frontmatter omits the `selection_rationale` enum, `validate_schema.py` may still pass (depending on whether the schema marks it required). A narrative could ship with three episodes all implicitly flagged `long_lead` and the triad requirement is silently skipped. Need: schema marks the field `required` AND the validator asserts at least one of each enum value is present.

**4.3 RES-22 decision-table condition evaluation is not mechanically checked.**
The table says "last modified within 60 days → Validated" but nothing at QA time inspects mtime against the label. Ray's honor-system assignment can silently drift from reality — the labels will decay from `Validated` to `Stale` over calendar time without any prose change.

**4.4 META-RYW re-read logging has no format spec.**
Wave 10F added META-RYW ("re-read end-to-end, log the re-read in the handoff note") but didn't specify a structured log format. Agents will produce heterogeneous prose logs; downstream audit becomes string-matching. Cf. RES-NR1's explicit log format (`RES-NR1 check: target_symbol=X; narrative references verified: [...]`) — that pattern should be the META-RYW default.

**4.5 RES-18 template ID: `headline_template: "A"` or `"B"` in frontmatter — but the validator doesn't check prose conformance.**
I can write `headline_template: "A"` in frontmatter and then author a headline that matches neither template A nor B. Schema validates the field exists; it does not validate prose-template fit. The rule assumes me honest; the gate is soft.

**4.6 `Unknown` is blocking — but the runtime fallback in `pair_registry.py` accepts it.**
`team-coordination.md:161-165` says Unknown is a gate error. But `pair_registry.get_integrity_issues()` treats it as a warning at runtime. Unless Quincy's GATE-31 hard-rejects any integrity warning, a pair can ship with `Unknown` and nobody notices until a stakeholder opens the portal.

---

## Section 5 — Ray-Specific Observations

**5.1 RES-NR1 enforcement post-APP-PT1.**
APP-PT1 (template abstraction, `sop-changelog.md:34-37`) moved narrative into `app/pair_configs/{pair_id}_config.py`. That's good for Ace's render consistency but fractures my authoring surface: I now write markdown narrative (`docs/portal_narrative_*.md` per RES-17) that nobody renders, plus Python config that actually ships. Until BL-004 closes (prose flows from the markdown via `components/narrative.py`), my RES-NR1 audit must run on the `.py` — and the md is essentially a specification artifact. This is workable but should be made explicit in the SOP: **"Ray's authoritative authoring surface is `pair_configs/*.py` prose fields; the `.md` narrative is the spec + frontmatter carrier. RES-NR1 grep target is the `.py`."** Currently RES-NR1 implies the `.md`; the Wave 10E incident was in the `.py`.

**5.2 RES-17 frontmatter ↔ APP-PT1 handoff contract is unclear.**
If prose lives in `.py` config dicts, where does the frontmatter JSON live? Options: (a) frontmatter stays in `.md` and Ace loads it separately; (b) frontmatter becomes a dict literal at the top of `pair_configs/{pair_id}_config.py`. Neither is stated. I recommend (a) — frontmatter in `.md` as Ray's spec surface; Ace's narrative-rendering component bridges — but the SOPs don't say so.

**5.3 `interpretation_metadata` consumption — Ray as both consumer and producer.**
I consume Dana's `indicator_nature`/`indicator_type` to shape narrative framing AND produce `strategy_objective` after tournament. The SOP should state the exact read-only vs read-write fields on the same artifact, preferably as a field-ownership table in team-standards.md (see §3.4 above). Today I have to derive this from two separate SOPs.

**5.4 META-ELI5 — Ray authors, Ace renders, Quincy gates. Ownership of the "plain-English sibling" is muddy.**
RES-22 rule 3 says Ray supplies the technical label and Ace's `glossary.py` renders the ELI5 body from `portal_glossary.json._status_vocabulary`. So editorially the glossary entry is mine, but at render time Ace has to pair them. If Ace renders without pairing, is that a RES violation or APP violation? I argue: **Ray authors the entry (RES-22) → Ace renders the pairing (APP-AF*) → Quincy gates the DOM (QA-CL#)**. The three-agent chain should be named explicitly.

**5.5 RES-NR1 × APP-PT1 supplement interaction.**
APP-PT1 supplement (Wave 10E, `sop-changelog.md:35-37`) added: "Narrative prose in `pair_configs/` MUST be authored by Ray, not Ace. Ace renders structure only." RES-NR1 is the consequence rule for the content of that prose. The two rules together form: **APP-PT1 supp = who writes; RES-NR1 = what must be true about what is written**. That chain is correct but the split responsibilities mean a new-pair dispatch must send the prose task to Ray FIRST (before Ace can render), not in parallel. `team-coordination.md` task flow (steps 2-6) should reflect the ordering.

**5.6 `chart_refs` ↔ `chart_type_registry.json` — my consumer side.**
RES-17 requires `chart_refs[*]` to exist in Vera's chart-type registry. VIZ-NM1 says the registry keys are bare names. If I accidentally pair-prefix a chart_ref, the schema validator catches it only if it does a registry cross-lookup — currently the schema just validates string type. Need: `validate_schema.py` extension that reads both the narrative frontmatter and Vera's registry and cross-checks membership. This is the "META-SCV for frontmatter" I should propose.

---

## Section 6 — Vera's Three Open Questions (my opinion)

**6.1 Chart filename convention — bare-name should be canonical; prefixed duplicates deprecated.**
Reasoning: (a) `load_plotly_chart(name, pair_id)` already takes pair_id as a separate argument (team-coordination.md:115), so filename prefix would be redundant; (b) pair_id already appears in the directory (`output/charts/{pair_id}/plotly/`), so prefix is doubly redundant; (c) bare-name is the pattern in the newest pairs (indpro_xlp, umcsent_xlv). The only legitimate reason for prefix is file-system search convenience outside the loader — that's an auxiliary concern solved by `find` and `grep`. **Vote: mandate bare-name, delete prefixed duplicates, update team-standards.md §2.1.** From Ray's side: my `chart_refs[]` values in RES-17 frontmatter are already bare-name; matching the on-disk canonical convention is free.

**6.2 Sidecar naming — `_meta.json` for charts (Vera), `_manifest.json` for datasets (Evan).**
Reasoning: the two artifacts are categorically different. A chart's sidecar is about *rendering metadata* (palette, annotations, caption) — the word "meta" fits. A dataset's sidecar is about *columns, units, and sign conventions* — the word "manifest" fits its inventory semantics. The convention is already followed in practice; team-standards.md §3 proposes it; the only loose end is VIZ-IC1 which mentions `_manifest.json` for the narrative-alignment note — that should move into `_meta.json` to align. **Vote: adopt team-standards.md §3 proposal as-is; amend VIZ-IC1 to write into `_meta.json`.**

**6.3 Palette role aliases.**
The proposal at team-standards.md:63-68 (`indicator` → `primary_data_trace`, `target` → `secondary_data_trace`, `benchmark` → `equity_curve`) is semantically right for my needs — my narrative prose refers to "the indicator," "the target," and "the benchmark," and an alias map lets me write chart captions that cite colors by semantic role. One caveat: `benchmark` collapsing to `equity_curve` is a category error on non-equity targets (e.g., XLE futures) — a bond benchmark shouldn't inherit the "equity_curve" color. **Vote: adopt `indicator` and `target` as proposed; split `benchmark` into `benchmark_equity` / `benchmark_fixed_income` / `benchmark_commodity` to avoid the equity-curve color being forced onto non-equity pairs.** The reference pair doctrine makes this cheap to add: expand now, not later.

---

## Section 7 — Priority Ranking (top 5 fixes)

1. **Resolve the narrative-surface ambiguity (`.py` config vs `.md` narrative).** Either promote `.md` to authoritative (BL-004 architectural route, `components/narrative.py` loader) or explicitly document `.py` as authoritative and demote `.md` to spec. Until this is clear, RES-17 frontmatter validation is theater. **Highest impact because it blocks RES-NR1, RES-17, and META-RYW from being mechanically enforceable.**

2. **Unify sidecar naming (`_meta.json` charts, `_manifest.json` datasets) and amend VIZ-IC1 accordingly.** Single-sprint fix; unblocks QA's cross-seam audit (QA's GATE-24 and META-CF checks both depend on knowing which file to read).

3. **Extend `validate_schema.py` to cross-check narrative frontmatter against Vera's registries.** `chart_refs[*]` → `chart_type_registry.json` membership; `glossary_terms[*]` → `portal_glossary.json` membership; `historical_episodes_referenced[*].episode_slug` → episode registry. Closes the silent-weakening of RES-17 and RES-20.

4. **Promote canonical status vocabulary + condition-to-label decision table into `team-standards.md`** and add a mechanical mtime-based linter (`scripts/check_status_labels.py`). Eliminates RES-22's silent drift and unifies DATA-VS / RES-VS / RES-10.

5. **Add structured log format to META-RYW** (mirror RES-NR1's `{rule_id} check: {fields}=...; verified: [...]` pattern). Without a format, the re-read log devolves into prose and Quincy's audit becomes string-matching. Small change, large audit-cost saving.

---

*End of findings.*
