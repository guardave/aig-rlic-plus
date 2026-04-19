# Cross-Review 2026-04-19 — Research Ray Boundary Audit

**Reviewer:** Research Ray
**Scope:** Audit Ray's producer/consumer boundaries with Evan, Vera, Ace, Dana. Identify missing contracts, propose new RES-* rules. Read-only on peer SOPs.
**Read corpus:** research-agent-sop.md, econometrics-agent-sop.md, visualization-agent-sop.md, appdev-agent-sop.md, data-agent-sop.md, team-coordination.md, standards.md.
**Bug history anchor:** RES-8 coherence gap (Wave 1.5), GFC 2-sigma override (Wave 2, no formal mechanism), chart-text drift (GATE-24), status vocabulary (S18-4 → RES-VS/DATA-VS), SL-1 headline-first (RES-11), S18-12 investor-impact bullets (RES-9).

---

### 1. Artifacts Ray produces for other agents

| Artifact path | Consumer | Contract rule ID | Schema explicit? | Failure mode when missing/invalid | Test/gate | Known gaps |
|---|---|---|---|---|---|---|
| `docs/research_brief_{topic}_{date}.md` | Evan (spec), Dana (data sources), Vera (event timeline) | RES-Q1, §5 template | Partial — template section headers enumerated, but no schema validator; field types ("Low/Medium/High") are prose | Evan specs without priors; Dana sources wrong series; Vera misses event dates | Ray self-review (§Quality Gates); no automated check | No JSON/YAML companion; no checksum for cross-ref with portal narrative |
| `docs/spec_memo_{topic}_{date}.md` | Evan (specification bootstrap) | RES-B1 | No — free-form 5-bullet | Evan begins from wrong priors; discovered only during intake step §2 | Evan sends back "Explicit confirmation" (§2 step 4) | Format drift across pairs; no field for `literature_support` level tied to `direction_confidence` |
| `docs/portal_narrative_{pair_id}_{date}.md` | Ace (renders), Vera (caption alignment), Lead (acceptance) | RES-Q1, §App Dev Handoff | Structural (Page 1-5, 8-element) but prose — Ace's content dict consumed via `narrative.py` lookup is derivative, not the authoritative artifact | Ace falls back to Vera caption; 8-element block ships incomplete; regression on rerun (see RES-5) | `acceptance.md` requires RES-11 headline check; GATE-24 chart-text coherence | **No formal "narrative content dict" schema document.** Ace's `content.get("caption")` is implicit — Ray's markdown is parsed by Ace, but the parser/contract lives in Ace code not Ray's SOP |
| `docs/portal_glossary.json` | Ace (`components/glossary.py` renderer), Lead (vocabulary), Dana (DATA-VS cross-ref) | RES-6, RES-10, RES-VS | Partial — RES-6 4-element rubric is prose; JSON key schema (`term`, `definition`, `context`) shown once in §Canonical Glossary but no JSON Schema file | Ace tooltips render degraded text; status vocabulary drifts; duplicates | RES-VS pre-handoff self-check | **No JSON Schema**; no CI lint for rubric compliance; backfill tracked outside this SOP (§RES-6 "Backfill action tracked separately") |
| `docs/storytelling_arc_{topic}_{date}.md` | Ace (page transitions), Lead (acceptance) | RES-PA1 | Template in §Storytelling Arc; no field validation | Page-to-page transitions weak (see Presentation Quality Pattern 3) | None beyond Ray self-review | No triggering rule — "if Lesandro delegates" is discretionary |
| `docs/event_timeline_{topic}_{date}.csv` + markdown table | Vera (chart annotations), Ace (timeline overlays) | RES-Q1 §"Event Timeline" | Yes — explicit columns (`date`, `event`, `relevance`, `type`, `equity/FI/commodity/crypto impact`) | Vera fabricates event dates; annotation drift | Vera ingests per VIZ-H3 | **No versioning rule when events are revised post-delivery**; no cross-check that Vera's rendered overlay dates match CSV |
| `docs/direction_annotations_batch_{date}.json` | Ace (programmatic direction callouts), Vera (Differs From) | RES-MS2 | Partial — example JSON shown but no formal schema file | Batch direction callouts inconsistent across pairs sharing indicator | None | No cross-pair consistency test automation; RES-B3 table is manual |
| `docs/portal_addendum_{indicator_id}_{target_id}_{date}.md` | Ace (per-pair Differs From notes) | RES-MS1 | No — "1-2 paragraphs" prose | Duplicate content vs indicator-level narrative; silent drift | None | Triggering threshold unclear (73+ pairs?) |
| `results/{id}/interpretation_metadata.json` — field `strategy_objective` | Ace (landing page filter), Dana (companion fields), Lead (GATE-21) | RES-B5, GATE-21, META-CFO | Yes — enum `min_mdd`/`max_sharpe`/`max_return` | GATE-21 fail → pair rejected | GATE-21 blocking | **No rule for re-setting when tournament is re-run with different winner**; no contradiction-detection with Evan's `suggested_strategy_objective` in `tournament_winner.json` |
| `results/{id}/regression_note_{date}.md` — Ray contributions | Ace, Evan, Lead (GATE-22, GATE-26) | RES-5, META-RNF | Yes — META-RNF required sections | Silent method drop (HY-IG v2 evidence) | GATE-22, GATE-26 | Ray's contribution interleaves with Evan's/Vera's in same file — **no ownership delimiter inside the note** |
| `results/{id}/prior_methods_{olddate}.csv` (regression prevention checklist) | Lead (GATE-22 reviewer), self | RES-5b | Yes — `method_name | element_1_chart_file | element_7_key_finding` | Silent method drop slips past rerun | GATE-22 | Not explicitly in any agent's consumer list; may be audit-only |
| "How to Use This Indicator Manually" narrative subsection | Ace (Strategy page render) | RES-PA3 ("How to Read Trade Log"), Rule 7 ("How the Signal is Generated") | Title-level prose requirement, no field schema | Strategy page omits user-facing manual; S18-1/S18-9 regression | Blocking via "must include" language in RES-7, RES-PA3 | **No canonical file path** — embedded in main narrative markdown; Ace extracts by heading match. Fragile. |
| Bibliography (within methodology section) | Ace (renders list), Lead (credibility review) | §Bibliography Scale (HY-IG v2 template, 10+ entries / 4 categories) | Categorical structure (foundational/empirical/method/practitioner) but no schema | Thin bibliography undetected; layperson trust impacted | `acceptance.md` reference-pair comparison | No machine-readable bibliography (BibTeX/CSL JSON); duplicates across pairs |

### 2. Artifacts Ray consumes from other agents

| Source | Artifact | Purpose | Rule relied on | Known gaps |
|---|---|---|---|---|
| Vera | `output/charts/{pair_id}/plotly/{chart_type}.json` + `_meta.json` sidecar | RES-8 cross-reference in narrative prose; Observation (Element 5) author from visual | VIZ-A3, VIZ-A5, VIZ-SD1 | **No notification contract when Vera updates a chart** — GATE-24 partially addresses but is reactive. Ray must proactively diff per 2026-04-19 clarification. |
| Vera | `output/_comparison/history_zoom_{episode_slug}.json` (canonical) | RES-8 historical-episode cross-ref | VIZ-V1, META-ZI | Override trigger (`output/charts/{pair_id}/history_zoom_...`) is Ray-driven per META-ZI — **no formal override request schema**, just prose "flag in handoff" |
| Vera | `_smoke_test_{date}.log` | Confirm charts loadable before I ship narrative referencing them | VIZ-V5, GATE-27 | Ray doesn't currently check this log before finalizing narrative — gap |
| Evan | `results/{id}/core_models_{date}/*.csv` (correlations, CCF, Granger, LP, quantile, HMM, transfer_entropy, quartile_returns) | Fuel Evidence Page 8-element Observation + Interpretation; power RES-5 manifest | ECON-C1, ECON-C2, ECON-C3 | Filename stability promised (ECON-C2 §Filename stability) — good. **But Ray's manifest CSV (`prior_methods_*.csv`) doesn't yet have a reciprocal file from Evan to diff against.** |
| Evan | `results/{id}/winner_summary.json` + `tournament_winner.json` | RES-11 headline KPIs (Sharpe, MDD, CAGR); RES-B5 strategy_objective derivation | META-TWJ, GATE-16 | **No canonical headline metric pick rule** — which 2-3 of (Sharpe/MDD/CAGR/turnover/ann_return) show up depends on Ray. Risk of variation across pairs. |
| Evan | `results/{id}/interpretation_metadata.json` — `observed_direction`, `mechanism`, `direction_confidence` | RES-B4 contradiction detection; RES-EP1 Element 7 Interpretation | ECON-C1, Defense 2 | Contradiction resolution is one-way (Ray flags, Vera revises via Defense 2 §2 sequencing) — no deadline on Ray's validation timing |
| Evan | `regression_note_{date}.md` (ECON-C3 producer-side) | Input to Ray's RES-5 rerun check | ECON-C3 | Ray's RES-5 still requires Ray to do its own diff — ECON-C3 is defense-in-depth, good |
| Dana | Data dictionary (Display Name, Direction Convention, Known Quirks, Display Note) | Rule 1 inline definitions; RES-4 unit narrative; glossary entries | DATA-DD1, DATA-D2, DATA-VS | **No rule that Ray must reference Dana's `Display Note` verbatim** for layperson quirk annotations in portal; risk of divergent phrasing |
| Dana | `interpretation_metadata.json` — `indicator_nature`, `indicator_type` | RES-B2 direction rationale; RES-EP1 Element 1 Method anchor | DATA-D3, GATE-19, GATE-20 | Good — canonical vocab enforced. Ray consumes classification read-only. |
| Dana | `data/display_name_registry.csv` | Glossary entries + axis labels in narrative | DATA-DD1 | Ray rarely touches directly — Ace/Vera are primary consumers; Ray should cross-check for new indicators |
| Ace | (nothing produced by Ace consumed by Ray) | — | — | One-way relationship; Ace is sink not source for Ray |
| Lead (Lesandro) | Analysis Brief; stakeholder feedback (SL-*, S18-*) | Triggers RES-* rule additions | META-P0 | Ray converts stakeholder feedback into rules, but **no rule requiring Ray to cite the SL/S18 ID in every new RES-* addition** — currently done ad-hoc (done well in RES-9, RES-11). |

### 3. Decisions Ray makes that affect other agents

| Ray decision | Affects | Mechanism | Current safeguard | Gap |
|---|---|---|---|---|
| Writing voice / plain-English register | Ace's caption rendering, layperson usability | Narrative markdown + glossary JSON | Rule 1-4 (audience, translation bridge, method justification, unit discipline) | No register audit — Ace just renders what's delivered |
| Inline definition vs glossary link | `docs/portal_glossary.json` scope creep | Rule 6 (4-element rubric) + Rule 10 (status vocab) | Ray is sole owner; Ace cannot append | Ace request-back protocol exists in Rule 6 but **no SLA — how long before Ray responds?** |
| Bullet structure + "What this means for investors" clause | Ace layout, Story page gate | RES-9 | Blocking gate (per RES-9 "gate failure") | Enforcement is Lead review; no automated detection of bare-observation bullets |
| Which historical episodes to reference | Vera's zoom chart production (VIZ-V1, META-ZI); Ace's loader fallback | RES-8 cross-ref rule; override trigger | RES-8 + META-ZI + coherence inspection step (Wave 1.5) | **No deadline for override request relative to Vera's first chart commit** (bug history item explicitly flags this) |
| `strategy_objective` setting | Ace landing page filter (APP-LP2); Lead GATE-21 | RES-B5 | GATE-21 blocking; must not be "unknown" (META-UNK) | **No contradiction handshake with Evan's `suggested_strategy_objective`** in tournament_winner.json; Ray can silently override |
| Status vocabulary choices in prose | Dana's DATA-VS (mirror at data layer); Ace's glossary renderer | RES-VS, RES-10 | Both RES-VS and DATA-VS self-check canonical list | Canonical list lives in two SOPs — **no single source of truth file** |
| "Coherence inspection" verdict — ship canonical vs request override | Vera's per-pair chart budget; Ace's loader | META-ZI §Canonical + Override | Decision logged in Ray→Ace handoff note | **No written verdict file path** — logged in prose handoff, not a machine-readable artifact |
| Bibliography depth (10+ / 4 categories) | Ace renders list; Lead credibility check | §Bibliography Scale | Reference-template via HY-IG v2 acceptance.md | No hard minimum enforcement; "thin literature" escape hatch |
| Regression note **Removed** entries authored by Ray | Evan, Ace, Lead GATE-26 | META-RNF §Removed | Canonical mechanism, gates 22/26 | Ownership delimiter inside shared note is informal (see gap above) |

### 4. Boundaries where Ray has been bitten

Every item below cross-references a commit or stakeholder feedback item. Extracted from bug history in prompt + my own reading of SOP revision comments.

**B1 — RES-8 historical-episode cross-ref had no zoom-chart coherence step (Wave 1.5 gap).**
First shipped as "cite the matching VIZ-V1 zoom chart in same paragraph." Gap surfaced because Ray would cite an episode (e.g., GFC) in narrative tying it to HY-IG widening behavior, but the canonical `output/_comparison/history_zoom_gfc.json` had no HY-IG overlay. Reader saw prose claim not supported by visual. Wave 1.5 added the coherence-inspection step + META-ZI canonical+override protocol.
*Root cause:* no explicit rule distinguishing "event-only reference" (canonical OK) vs "indicator-tied reference" (override needed). Fixed by extending RES-8 + adding META-ZI.
*Residual gap:* override request timing vs Vera's chart commit — see Proposed RES-12 below.

**B2 — GFC 2-sigma band override candidate (Wave 2, informal).**
Ray flagged to Vera in prose handoff: "GFC zoom needs a 2-sigma band overlay for HY-IG." No structured override-request artifact. Vera had to re-derive context from prose. Similar risk to B1 but at the annotation layer, not the overlay layer.
*Root cause:* META-ZI §3 says "Ray flags 'override needed' in her handoff to Vera" — the how (format, fields, deadline) is unspecified. Currently prose-only.

**B3 — Chart-text drift: Vera updated heatmap signal selection; Ray's narrative went stale (SL-3).**
Evidence heatmap had signal ordering change. Ray's "What the chart shows" prose unchanged. GATE-24 was added as partial fix — but initially written as "Vera notifies Ray." 2026-04-19 clarified Vera notifies AND Ray proactively diffs on every rerun. VIZ "chart-text coherence" subsection codifies Vera side.
*Residual gap:* Ray's proactive diff has no formal recipe analogous to RES-5b. Ray can declare "no changes" without actually doing the diff. See Proposed RES-13.

**B4 — Status vocabulary ambiguity (S18-4 → RES-10 / RES-VS).**
Ray used "Available", "Pending" without definitions. Stakeholder asked "what does Pending mean?" Fixed by RES-10 (glossary entries) + RES-VS (pre-handoff self-check) + DATA-VS (companion at data layer).
*Residual gap:* canonical list duplicated across RES-VS and DATA-VS SOPs. Single source of truth file missing. See Proposed RES-14.

**B5 — SL-1 headline-first: Story page narrative-first ordering (fixed by RES-11).**
Stakeholder: "Suggest swapping — data summary is better suited as a headline." Previously Ray's guidance was non-blocking. RES-11 made it blocking with mandatory order Headline → Hook → Narrative → Bullets.
*Residual gap:* "2-3 KPI metrics" is prose — no schema validator. Which 2-3 is discretionary. See §3 row "headline metric pick rule."

**B6 — S18-12 investor-impact bullets (fixed by RES-9).**
Ray wrote observation-only bullets ("Credit spreads widened 6 months before Dot-Com recession"). Stakeholder (AF): "每點可解釋得詳細些, 例如加上對投資者的影響." RES-9 made investor-impact clause mandatory per bullet.
*Residual gap:* No automated detection. Lead review only. A regex for "would have [action]" would catch most missing clauses but isn't codified.

**B7 — Strategy objective contradiction with Evan's suggested_strategy_objective.**
Not yet a shipped bug but structurally possible. META-TWJ defines `suggested_strategy_objective` in `tournament_winner.json`; RES-B5 says Ray "may override with rationale." No handshake file documenting the override reason.
See Proposed RES-15.

**B8 — "How to Use This Indicator Manually" / "How the Signal is Generated" extraction fragility.**
Ace extracts these subsections from narrative markdown by heading match. Cross-reference: Wave 2 handoff notes to Ace. If Ray renames the heading (e.g., "How the Signal Works" instead of "How the Signal is Generated") the extraction silently fails.
*Root cause:* no canonical heading registry; no file-per-subsection delivery option. See Proposed RES-16.

### 5. Proposed new rules

> **Proposed RES-12 — Historical-Episode Override Request Schema + Deadline**
> - **Rule text:** When Ray's narrative coherence inspection (RES-8 / META-ZI) determines an episode zoom override is required, Ray MUST deliver a structured override request file at `results/{pair_id}/override_requests_{date}.md` with fields: `episode_slug`, `prose_reference` (Story§ + line number), `overlay_required` (indicator name + expected transformation), `baseline_elements_preserved` (list, must include canonical event markers + NBER shading), `requested_by_date`. The file must be delivered **before Vera's first chart commit for the pair** (i.e., before Vera writes any `output/charts/{pair_id}/history_zoom_*.json`). Late requests trigger a v2 chart cycle and a regression note entry.
> - **Closes gap:** B1 (Wave 1.5 coherence) + B2 (Wave 2 GFC 2-sigma informal handoff). Ensures the override lifecycle is machine-auditable and scheduled, not prose-and-goodwill.
> - **Blocking?:** Yes for reference pairs; advisory for exploratory pairs.
> - **Cross-reference:** VIZ-V1 (Vera's production side), META-ZI §3 (cross-agent contract), GATE-25 / GATE-27.

> **Proposed RES-13 — Narrative-Chart Coherence Diff Recipe (Ray's proactive GATE-24 side)**
> - **Rule text:** On every rerun of a pair that already has a portal narrative, Ray MUST produce `results/{pair_id}/narrative_chart_diff_{date}.md` listing: (1) every chart referenced in the new narrative, (2) prior-version chart for same method, (3) field-level diff (signal, ordering, axes, colors) read from Vera's `_meta.json` sidecars, (4) verdict "coherence preserved" / "narrative edit required". Recipe: `for each chart_type in new narrative: load output/charts/{pair_id}/plotly/{chart_type}_meta.json new+prior, diff on {signal, ordering, axis_label, unit}; if diff nonzero, narrative prose for that chart must be re-audited or moved to **Removed** section`.
> - **Closes gap:** B3 (chart-text drift). GATE-24 says "Ray proactively diffs" — this rule gives Ray the recipe analogous to RES-5b.
> - **Blocking?:** Yes — tied to GATE-24 sign-off.
> - **Cross-reference:** GATE-24 (team-coordination.md), VIZ-A5 (caption ownership), RES-5 / RES-5b (method manifest recipe).

> **Proposed RES-14 — Canonical Status Vocabulary — Single Source of Truth**
> - **Rule text:** The canonical list **Available / Pending / Validated / Stale / Draft / Mature / Unknown** is maintained in ONE file: `docs/portal_glossary.json` under key `_status_vocabulary` (array of objects, each with `label`, `definition`, `applies_to`). RES-VS and DATA-VS both cite this file as the single source; the list is no longer re-declared in either SOP. Adding a term requires a glossary PR first, then a changelog entry, then SOP cross-reference update.
> - **Closes gap:** B4 residual (list duplicated across RES-VS / DATA-VS). Prevents vocabulary drift.
> - **Blocking?:** No (structural rule, not per-pair).
> - **Cross-reference:** RES-10, RES-VS, DATA-VS, META-UNK.

> **Proposed RES-15 — Strategy Objective Contradiction Handshake**
> - **Rule text:** When Ray's `strategy_objective` in `interpretation_metadata.json` differs from Evan's `suggested_strategy_objective` in `tournament_winner.json`, Ray MUST write `results/{pair_id}/strategy_objective_override_{date}.md` with: `evan_suggested`, `ray_chosen`, `rationale` (cite tournament deltas per META-TWJ), `approved_by` (Lesandro). Absence of this file when the two fields disagree is a GATE-21 failure.
> - **Closes gap:** B7 (no handshake for override).
> - **Blocking?:** Yes — extends GATE-21.
> - **Cross-reference:** META-TWJ, GATE-21, META-CFO.

> **Proposed RES-16 — Narrative Subsection File-Path Contract**
> - **Rule text:** Strategy-page narrative subsections that Ace renders as standalone UI blocks — "How the Signal is Generated" (RES-7), "How to Read the Trade Log" (RES-PA3), "How to Use This Indicator Manually" — MUST be delivered BOTH inline in the main narrative markdown AND as standalone files: `docs/portal_subsections/{pair_id}/signal_generation.md`, `.../how_to_read_trade_log.md`, `.../how_to_use_indicator.md`. Ace loads the standalone file with heading-match fallback. Renaming a heading in the main narrative is non-breaking as long as the standalone file is correct.
> - **Closes gap:** B8 (Ace extracts by heading match — fragile).
> - **Blocking?:** Yes — failure = standalone file missing OR standalone file's first-line header does not match canonical names.
> - **Cross-reference:** RES-7, RES-PA3, APP-SE3 (instructional trigger cards), APP-AF2 (rule-first strategy cards).

### 6. Questions to other agents (for consolidation phase)

- **@Vera — override-request deadline.** Proposed RES-12 says Ray's override request lands *before* Vera's first chart commit for the pair. Is that achievable given Vera's pipeline (canonical zooms produced once, reused across pairs)? Or should the deadline be "before the pair's chart batch starts" with canonical already assumed done? Tag: RES-12 / META-ZI.
- **@Vera — `_meta.json` schema stability.** Proposed RES-13 recipe reads field-level diffs from your sidecar. Are `signal`, `ordering`, `axis_label`, `unit` stable fields across all chart types? If some sidecars use `signals` (plural) or `series_selection`, I need to normalize. Tag: RES-13 / VIZ-SD1.
- **@Evan — method manifest reciprocal file.** My RES-5b produces `prior_methods_{olddate}.csv` as a checklist. Your ECON-C3 says "List the set of method files present in the prior `core_models_*` directory." Should we converge on one shared manifest file (e.g., `results/{id}/method_manifest_{date}.csv`) owned jointly, or keep two parallel files? Tag: RES-5b / ECON-C3.
- **@Evan — strategy_objective override rationale.** Proposed RES-15: if you and I disagree on `strategy_objective`, is your `suggested_strategy_objective` derivation documented anywhere Ray can cite? META-TWJ shows the schema but not the heuristic. Tag: RES-B5 / META-TWJ.
- **@Ace — heading-match fragility.** Proposed RES-16 adds standalone files. Would you prefer (a) both inline + standalone, or (b) canonical standalone only and your page code imports from the standalone path? Option (b) removes duplication but loses narrative flow for Lead review. Tag: RES-16 / APP-SE3.
- **@Dana — Display Note verbatim rule.** Should Ray's layperson quirk annotations copy your `Display Note` field verbatim, or is paraphrase allowed as long as semantic intent is preserved? Currently no rule — divergence risk. Tag: DATA-DD1 / RES-6.
- **@Ace (top priority) — glossary request-back SLA.** RES-6 says Ace files a request back to Ray when a missing term is spotted during portal assembly. How many task-cycles can you wait before the portal ships with a fallback? I'd propose: 1 cycle (same dispatch if possible); define "fallback" as `term: "{term}"; definition: "pending Ray addition"; status: "Pending"`. Tag: RES-6 / APP-Q1.

---

**File budget check:** ~520 lines including tables (under 600-line cap).
