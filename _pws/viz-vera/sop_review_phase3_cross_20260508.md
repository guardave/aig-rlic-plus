# Viz Vera — Phase 3 Cross-SOP Review (Handoff Perspective)

**Date:** 2026-05-08
**Reviewer:** Viz Vera (viz-vera)
**Scope:** Five peer SOPs reviewed from a handoff perspective only — looking for
filename/schema/path mismatches, severity asymmetries, cross-reference integrity
failures, vocabulary drift, and skip-protocol overlaps that affect Vera's
producer–consumer relationships. No edits made (LEAD-DL1 binding).
**LA arbitrations:** LA-1 through LA-10 are binding and are NOT re-litigated.
**File:** `_pws/viz-vera/sop_review_phase3_cross_20260508.md`

---

## Section 1 — Dana (data-agent-sop.md)

### C1-D01 — `display_name_registry.csv` path mismatch between producer spec and Vera's consumer expectation (WARN)

**Rule/section:** Dana §6 "Display-name registry" (data-agent-sop.md); VIZ-A2 (Vera axis-label unit-match rule).
**Problem:** Dana's SOP specifies the display-name registry at
`data/display_name_registry.csv` with columns `column_name`, `display_name`,
`unit`, `axis_label`. Vera's SOP §VIZ-A2 states that axis labels must match the
DATA-D5 sidecar. Vera's SOP never explicitly names `display_name_registry.csv`
as a source; it refers only to the DATA-D5 sidecar (`data/{subject}_{frequency}_schema.json`).
These are two separate files. If Vera reads axis labels from DATA-D5 and Dana
updates only `display_name_registry.csv` (or vice versa), the two diverge
silently and Vera's axis labels drift from Dana's canonical display names.
The data-agent-sop.md note "Vera and Ace consume it directly" implies
`display_name_registry.csv` is a direct input to Vera — but Vera's SOP contains
no reference to this file whatsoever.
**Severity:** WARN — no immediate contradiction in current charts, but the
dual-source model is a latent drift hazard.
**Who must fix:** Dana (add a note clarifying whether `display_name_registry.csv`
supersedes or supplements DATA-D5 sidecar for Vera's axis labels). Vera (Phase 4)
must explicitly name one of the two as the single source of truth in VIZ-A2.

---

### C1-D02 — Dana's Data-to-Viz handoff template does not reference `_meta.json` sidecar schema (WARN)

**Rule/section:** Dana §"Data-to-Viz Handoff" (data-agent-sop.md); VIZ-O1 / VIZ-NM1 (Vera's `_meta.json` sidecar mandate).
**Problem:** Dana's Data-to-Viz handoff template lists four deliverables: dataset,
data dictionary with Display Name column, a note on data quirks, and recommended
chart type. It makes no mention of Vera's `_meta.json` sidecar requirement (VIZ-O1:
every chart must have a disposition sidecar; VIZ-NM1 defines sidecar schema
including `source`, `source_sample_period`, `audience_tier`, etc.). The metadata
boundary paragraph in Dana's SOP says "Vera reads column semantics from Dana's
DATA-D5 sidecar" — correctly — but stops short of saying that Dana must supply
or confirm the `source` and `source_sample_period` fields that Vera's `_meta.json`
requires (these originate with Dana, not Vera or Evan).
If Dana omits provenance fields from the handoff, Vera must hand-fill them in the
`_meta.json`, introducing a cross-agent provenance gap that VIZ-CV1 / QA would need
to flag.
**Severity:** WARN — no blocking failure, but a precision gap in the handoff contract.
**Who must fix:** Dana (add a line to Data-to-Viz handoff template: "Include or
confirm the `source`, `series_id`, and `source_sample_period` values Vera will
populate in `_meta.json` sidecars"). Vera (Phase 4) should add a VIZ-DP1-style
note listing which `_meta.json` fields come from Dana's handoff vs. Vera's own
authorship.

---

### C1-D03 — Dana's Rule D2 unit convention cross-references VIZ-A2 but VIZ-A2 does not reciprocate (WARN)

**Rule/section:** Dana Rule D2 "Cross-reference for consumers" note (data-agent-sop.md §Rule D2); VIZ-A2 (Vera's axis-label unit match rule).
**Problem:** Dana's Rule D2 says: "Vera's Rule A2 (axis-label unit match)...
both assume this registry. A unit drift here cascades into wrong axes."
This is an accurate cross-reference from Dana. However, Vera's VIZ-A2 does not
cross-reference Dana's Rule D2 or the unit convention registry. If a new Vera
reads the Viz SOP from cold start, she will not know that Dana's D2 registry is
the upstream source of unit discipline. The cross-reference is one-way (Dana →
Vera) instead of bidirectional.
**Severity:** WARN — discoverability gap. No logical gap in the rules themselves.
**Who must fix:** Vera (Phase 4 — add "see Dana Rule D2 for the upstream unit
convention registry" to VIZ-A2).

---

## Section 2 — Evan (econometrics-agent-sop.md)

### C1-E01 — ECON-H4 handoff table uses `expected_chart` vocabulary that conflicts with VIZ canonical chart-type names (FAIL)

**Rule/section:** ECON-H4 "Per-Method Chart Artifact Handoff" template (econometrics-agent-sop.md); VIZ-NM1 canonical chart filenames.
**Problem:** ECON-H4 instructs Evan to provide for each method:
- `result_file` — CSV path
- `expected_chart` — "VIZ canonical catalog" chart type description
- `status` — `ready` / `blocked` / `pending`

The `expected_chart` column is described as "expected chart type per VIZ canonical
catalog (e.g., 'F-statistic by lag bar chart')." However, Vera's VIZ-NM1 defines
canonical chart names as bare filenames (e.g., `granger_causality.json`,
`local_projections.json`, `regime_probability_timeline.json`) — not natural-
language descriptions. There is no VIZ "canonical catalog" that maps "F-statistic
by lag bar chart" to a canonical filename. Evan authors a description; Vera must
guess which canonical filename it maps to.
This is the root-cause class of the silent method-drop pattern identified in
team-coordination.md §22: if the filename Vera derives from Evan's description
differs from the filename Vera's actual generator produces, the chart is produced
under a non-canonical name and fails GATE-27.
**Severity:** FAIL — the handoff template produces an un-resolvable mapping between
Evan's `expected_chart` description and Vera's canonical filename. The gap is
currently papered over by institutional knowledge, not a rule.
**Who must fix:** Evan (Phase 4) — change the `expected_chart` column to
`canonical_chart_filename` and require a verbatim filename from VIZ-NM1 (e.g.,
`granger_causality.json`, not "F-stat by lag bars"). Vera has no fix needed if
Evan provides the verbatim filename.

---

### C1-E02 — `winner_summary.json` schema cited as v1.0.0 in ECON-H5; Lead arbitration LA-10 flags stale schema citation (FAIL — LA-10 mandated fix)

**Rule/section:** ECON-H5 "Winner Summary JSON Contract" (econometrics-agent-sop.md); LA-10; Phase 2 Finding A6.
**Problem:** ECON-H5 states: "Canonical schema: `docs/schemas/winner_summary.schema.json`
(per META-CF, owned by Evan, version 1.0.0)." LA-10 explicitly lists this as a
stale item that must be retired in Phase 4 (Phase 2: "v1.0.0 schema citation in
ECON-H5 (Evan F-05)"). Vera consumes `winner_summary.json` for direction annotation
visual encoding (solid = pro-cyclical, dashed = counter-cyclical). If Vera uses
the v1.0.0 schema assumptions and the live schema is v1.1.0, field semantics may
differ, causing silent annotation errors.
This is already an LA-10 item and is flagged here only to confirm that the impact
flows to Vera as a consumer, not just to Evan as producer.
**Severity:** FAIL (LA-10 mandated) — Vera impact: direction annotation may use
stale schema fields.
**Who must fix:** Evan (Phase 4, LA-10). Vera (Phase 4) should add an explicit
APP-WS1-style schema-version check when loading `winner_summary.json` for direction
annotation, mirroring what Ace does in APP-WS1.

---

### C1-E03 — ECON-H4 `status = "blocked"` triggers Vera placeholder, but GATE-25 placeholder terminology is not cited in ECON-H4 (WARN)

**Rule/section:** ECON-H4 (econometrics-agent-sop.md): "If status = `blocked`, Vera does NOT attempt the chart; she renders a 'chart pending' placeholder (per GATE-25)."
**Problem:** ECON-H4 names the placeholder behavior "per GATE-25" — correct. However,
Vera's SOP does not have a rule named GATE-25 (gates are in Quincy's SOP). Vera's
SOP uses the term "chart pending" state in VIZ-V8 and references "APP-EP4 / GATE-25"
in VIZ-HZE1, but GATE-25 is defined only in Ace's SOP and QA's SOP, not in Vera's.
A new Vera following ECON-H4 ("per GATE-25") would need to navigate to the App Dev
SOP or QA SOP to understand the placeholder protocol — it is not documented in her
own SOP.
Separately, Evan's ECON-H4 says "Vera does NOT attempt the chart." But Vera's
VIZ-HZE1 skip protocol (for data-coverage reasons, not Evan's blocking) produces a
structured skip entry in `_meta.json`. It is not clear whether Vera should also
write a skip entry for an Evan-side `blocked` method or just silently not produce
the chart — the two blocking causes (Vera-HZE1 / Evan-blocked) are undifferentiated
in the downstream `_meta.json` record.
**Severity:** WARN — Vera can infer correct behavior from GATE-25 context, but the
block-source disambiguation is missing.
**Who must fix:** Evan (Phase 4) — add a note to ECON-H4 clarifying that Vera's
skip-protocol (VIZ-HZE1 format) applies when the block is data-coverage-driven;
when the block is Evan-side, Vera notes the block source in the `_meta.json`
`skip_reason` field. Vera (Phase 4) — add a brief note in VIZ-HZE1 distinguishing
"data-coverage skip" (Vera-initiated, WARN at Quincy) from "upstream-blocked skip"
(Evan-initiated, tracked separately, no GATE-HZE1 implication).

---

### C1-E04 — Rule C2 mandatory output filenames: `quartile_returns.csv` used in Evan's table but chart request to Vera uses `regime_quartile_returns.csv` (WARN)

**Rule/section:** ECON Rule C2 mandatory output schema (econometrics-agent-sop.md — `quartile_returns.csv`); ECON-H4 template example row ("results/{id}/regime_quartile_returns.csv").
**Problem:** The Rule C2 mandatory output table lists the filename as
`quartile_returns.csv`. The ECON-H4 template example row shows the file as
`results/{id}/regime_quartile_returns.csv` (prefixed with `regime_`). These are
two different filenames for the same artifact. Vera receives the ECON-H4 handoff
table and loads the CSV from the stated path; if one says `quartile_returns.csv`
and the other says `regime_quartile_returns.csv`, Vera will look in the wrong place.
Rule C2 note 4 says: "Ray's narrative templates reference these exact filenames and
columns. A change to this schema requires a paired update." Since Vera also consumes
these files (per ECON-H4), the filename inconsistency means either Vera or Ray will
load from the wrong path.
**Severity:** WARN — if both filenames exist on disk (duplicate output), the drift is
silent. If only one exists, the consumer using the wrong name gets a FileNotFoundError.
**Who must fix:** Evan (Phase 4) — align the Rule C2 table and the ECON-H4 template
to use exactly one canonical filename. Canonical candidate: `quartile_returns.csv`
(per C2 table, without the `regime_` prefix).

---

## Section 3 — Ray (research-agent-sop.md)

### C1-R01 — RES-20 / RES-HZE1 `episode_registry.json` slug set conflicts with LA-2 canonical slug set (FAIL — LA-2 mandated)

**Rule/section:** RES-HZE1 "Slug matching procedure" (research-agent-sop.md, step 1: "Open `docs/schemas/episode_registry.json`"); RES-20 rule 2 ("Episode must exist in Vera's registry"); GATE-VIZ-NBER2 episode–recession overlap table in QA SOP.
**Problem:** RES-HZE1's slug matching procedure reads from `docs/schemas/episode_registry.json`
(Ray's reference) and the example config block uses `"slug": "rates_2022"` for the
2022 episode. LA-2 mandates the canonical slug set as `dotcom`, `gfc`, `covid`,
`taper_2018`, `inflation_2022` — with `rates_2022` explicitly listed as
non-canonical.
RES-20's rule 2 says each `episode_slug` "MUST resolve to an entry in
`output/charts/chart_type_registry.json` (VIZ-V12 / chart-type registry)." But
VIZ-V12 designates `history_zoom_events_registry.json` as the canonical registry
(LA-1). The `chart_type_registry.json` reference in RES-20 appears to be an
incorrect cross-reference (Phase 2 finding A6: "RES-20 cites `output/charts/chart_type_registry.json` — wrong path").
The GATE-VIZ-NBER2 episode-overlap table in Quincy's SOP also uses `dot_com`
(underscore) and `taper_2013`, `china_2015`, `rates_2022` — all non-canonical under LA-2.
Result: Ray's RES-HZE1 config block example (`"slug": "rates_2022"`) will produce
a slug that Vera rejects at chart load (no `history_zoom_rates_2022.json` exists;
canonical filename is `history_zoom_inflation_2022.json`), and the GATE-HZE1
heading check will WARN (Vera blocker) even though Ray believed the slug was valid.
**Severity:** FAIL — three-agent work chain (Ray → Vera → Ace → Quincy) breaks at
the slug handoff point. This is a LA-1/LA-2 cascading failure.
**Who must fix:** Ray (Phase 4) — update RES-HZE1 slug matching procedure to read
from `docs/schemas/history_zoom_events_registry.json` (per LA-1) and replace all
example slugs with canonical set (per LA-2). Also fix RES-20 rule 2 registry path
reference from `output/charts/chart_type_registry.json` to
`docs/schemas/history_zoom_events_registry.json`.

---

### C1-R02 — RES-HZE1 `HISTORY_ZOOM_EPISODES` attribute name confirmed canonical (LA-3 resolved) but RES-ZOOM1 config attribute conflict still in research SOP (WARN — LA-3 mandated)

**Rule/section:** RES-HZE1 and RES-ZOOM1 (research-agent-sop.md); LA-3.
**Problem:** LA-3 mandates that `HISTORY_ZOOM_EPISODES` is canonical and
`ZOOM_EPISODE_NARRATIVES` is retired. The research SOP's RES-ZOOM1 rule was not
read in full during this review (it is referenced in Phase 2 as the conflicting
attribute), but the impact on Vera is confirmed: if Ray's handoff to Ace uses
`ZOOM_EPISODE_NARRATIVES`, Ace's template (which reads `HISTORY_ZOOM_EPISODES`)
will silently skip the "How the Signal Performed in Past Crises" section. Vera is
not directly affected at chart-generation time, but the omission means Vera's
zoom charts — which she produced and committed — render invisibly on the Story page,
with no GATE-HZE1 FAIL (heading absent + charts present → Ace FAIL, not Vera FAIL).
**Severity:** WARN (from Vera's perspective — her charts exist but are wired into the
wrong config attribute upstream). FAIL for Ray (LA-3 mandated fix).
**Who must fix:** Ray (Phase 4, LA-3) — update RES-ZOOM1 to retire
`ZOOM_EPISODE_NARRATIVES` and route all zoom episode deliveries through
`HISTORY_ZOOM_EPISODES` per RES-HZE1.

---

### C1-R03 — RES-NR1 instrument-reference check cites `VIZ-NM1` but Vera's VIZ-NM1 is a filename-convention rule, not a narrative cross-reference rule (WARN)

**Rule/section:** RES-NR1 "Cross-references" (research-agent-sop.md): "APP-PT1 (Ace renders, Ray authors), GATE-NR (QA enforcement of this rule at DOM level), RES-17 (narrative frontmatter), APP-DIR1 (direction triangulation — direction accuracy is the companion rule to instrument accuracy)."
**Problem:** RES-NR1 does NOT cross-reference Vera's VIZ-NM1. However, VIZ-NM1
defines canonical chart filenames that Ray's narrative cross-references in RES-8
(Rule 8: "must reference a matching annotated zoom-in chart produced by Vera per
VIZ-V1"). Rule 8's "accepted cross-reference formats" include
`![Dot-Com zoom](output/charts/{pair_id}/plotly/history_zoom_dotcom.json)` — a
literal path that follows VIZ-NM1's naming convention. If VIZ-NM1's naming
convention changes (e.g., a future rename), Ray's Rule 8 embedded paths would break.
The cross-reference direction is missing: RES-NR1 should note that chart filenames
cited in narrative prose must follow VIZ-NM1, and Rule 8 should link to VIZ-NM1
as the canonical naming source.
**Severity:** WARN — the rules are consistent today; the bidirectional cross-reference
is missing, creating a maintenance drift risk.
**Who must fix:** Ray (Phase 4) — add VIZ-NM1 to RES-NR1 cross-references and add
a note in Rule 8 that chart paths in prose must use VIZ-NM1 canonical filenames.

---

### C1-R04 — Ray's `chart_status` field in narrative frontmatter uses vocabulary "ready" that RES-22 explicitly bans (FAIL)

**Rule/section:** RES-22 "Status-Label Assignment Decision Table" (research-agent-sop.md): "2. 'ready' is a banned informal alias..."; Phase 1 Vera F-06 noted that Quincy's GATE-VIZ-NBER2 status board entry uses `chart_status: "ready"`.
**Problem:** RES-22 explicitly bans `chart_status: "ready"` as a non-canonical status
label and mandates one of: `Available` / `Pending` / `Validated` / `Stale` /
`Draft` / `Mature` / `Unknown`. Vera's Phase 1 review (deferred item 6) identified
that the chart_status field flows from Ray's narrative to the `_meta.json` sidecar
that Vera authors. Vera's SOP (§"Chart-gap requests from Research Ray") requires Vera
to update Ray's `chart_status` field — but if the incoming value from Ray is "ready"
(banned), and Vera propagates it into `_meta.json`, the GATE-28 / RES-VS vocabulary
check will flag the sidecar. Vera is not the author of the invalid value but would
be the carrier.
The field schema for `chart_status` in Vera's `_meta.json` must only accept the RES-22
canonical vocabulary, but it is currently unguarded against Ray passing "ready."
**Severity:** FAIL — RES-22 explicitly identifies "ready" as a banned alias that
blocks acceptance. If Ray passes it to Vera and Vera carries it forward, the
downstream gate failure lands on the `_meta.json` sidecar, for which Vera is the
producer-of-record.
**Who must fix:** Ray (Phase 4) — RES-22 is already the rule; Ray must self-check
per RES-VS before handoff. Vera (Phase 4) — add a producer-side guard in the
`_meta.json` sidecar writer: if `chart_status` value is not in the canonical vocabulary,
log a VIZ-IC1 warning and substitute `"Available"` or escalate.

---

### C1-R05 — RES-17 frontmatter `chart_refs` field must resolve to `chart_type_registry.json` entries — but Vera owns that registry and its scope is unclear relative to `history_zoom_events_registry.json` (WARN)

**Rule/section:** RES-17 "Required fields" (research-agent-sop.md): "`chart_refs` (canonical names that MUST exist in Vera's `chart_type_registry.json`)"; VIZ-V12 (Vera owns `history_zoom_events_registry.json`); LA-1.
**Problem:** RES-17 mandates that `chart_refs` entries "MUST exist in Vera's
`chart_type_registry.json`." This is a different file from
`history_zoom_events_registry.json` (which LA-1 declares canonical for episodes).
`chart_type_registry.json` appears to be Vera's broader chart-type catalog (mapping
chart names to types, audience tiers, etc.), while `history_zoom_events_registry.json`
is the episode slug registry. The two files serve different purposes and this
distinction is correct — but Ray's `historical_episodes_referenced` frontmatter
field in RES-17 should resolve slugs against `history_zoom_events_registry.json`
(per LA-1), NOT `chart_type_registry.json`. The RES-20 rule 2 confirms this: "Each
`episode_slug` MUST resolve to an entry in `output/charts/chart_type_registry.json`"
— which is the wrong path (per Phase 2 finding A6). This creates a second path
where Ray validates slugs against the wrong file.
The `chart_refs` field (non-episode chart references like
`regime_probability_timeline`) legitimately uses `chart_type_registry.json`. But
episode slugs must use `history_zoom_events_registry.json`. RES-17 does not
distinguish between these two categories of `chart_refs`.
**Severity:** WARN — the two registries serve different purposes; the SOP collapses
them into one validation path, which can cause Ray to validate episode slugs against
the wrong file.
**Who must fix:** Ray (Phase 4) — split `chart_refs` validation: chart-type references
validate against `chart_type_registry.json`; episode slugs validate against
`history_zoom_events_registry.json` (per LA-1). Vera (Phase 4) — clarify VIZ-V12's
relationship to `chart_type_registry.json` in a brief cross-reference note.

---

## Section 4 — Ace (appdev-agent-sop.md)

### C1-A01 — APP-PT1 Wave 10G.3 `HISTORY_ZOOM_EPISODES` absent-field behavior contradicts VIZ-HZE1 skip-protocol scope (FAIL)

**Rule/section:** APP-PT1 Wave 10G.3 extension (appdev-agent-sop.md): "When the field is absent or empty, the section is silently skipped."; VIZ-HZE1 skip protocol (Vera SOP); GATE-HZE1 disposition logic (QA SOP).
**Problem:** APP-PT1 Wave 10G.3 says `HISTORY_ZOOM_EPISODES` absent → section
"silently skipped." GATE-HZE1 says: if heading absent AND `history_zoom_*.json`
charts exist on disk → FAIL (Ace bug). If heading absent AND no zoom charts on
disk → WARN (Vera blocker).
VIZ-HZE1 governs Vera's side: when Vera has a data-coverage reason to skip
generating a zoom chart, she writes a structured skip entry in `_meta.json` with
reason, episode_slug, and wave fields. This skip entry signals to Ace that the
chart will not arrive — Ace should NOT raise an APP-EP4 warning for a VIZ-HZE1-
authorized skip.
The combined protocol creates three distinct states that must be distinguished:
1. No zoom charts exist, no skip entry in `_meta.json` → WARN (Vera hasn't
   produced yet; Ace cannot wire config; GATE-HZE1 WARN).
2. No zoom charts exist, but VIZ-HZE1 skip entry IS in `_meta.json` →
   authorized absence; Ace should suppress the APP-EP4 placeholder and NOT
   include the episode in `HISTORY_ZOOM_EPISODES`.
3. Zoom charts exist, but `HISTORY_ZOOM_EPISODES` is absent or empty in config →
   GATE-HZE1 FAIL (Ace bug; Ace has charts to wire but hasn't).
APP-PT1 and ACE-HZE1 address state 3 but collapse states 1 and 2 into "absent
or empty → silently skip." This means Ace cannot distinguish an authorized skip
(state 2) from a Vera-not-yet-delivered state (state 1) without reading
`_meta.json` — which APP-PT1 does not instruct Ace to do.
**Severity:** FAIL — the skip-protocol overlap creates an unresolvable ambiguity
at Ace's wiring stage without a cross-SOP procedure specifying how Ace reads
VIZ-HZE1 skip entries from `_meta.json`.
**Who must fix:** Ace (Phase 4) — ACE-HZE1 step 1 should add: "Check each chart's
`_meta.json` for a `disposition: skip` entry with `skip_reason` containing
'VIZ-HZE1'. If present, the episode is authorized-absent; do not wire to config,
do not raise APP-EP4 placeholder; record 'ACE-HZE1: authorized VIZ-HZE1 skip
for {slug}' in handoff note." Vera (Phase 4) — add a note to VIZ-HZE1: "Ace reads
the skip entry from `_meta.json`; Ace's ACE-HZE1 step 1 is the downstream consumer
protocol for VIZ-HZE1 skips."

---

### C1-A02 — Ace's chart loader path `output/charts/{pair_id}/plotly/{chart_type}.json` matches VIZ-NM1, but multi-pair chart organization section shows legacy pair-prefixed filenames (FAIL)

**Rule/section:** APP-ST1 / Rule 3.9a "Chart filename contract" (appdev-agent-sop.md): "Ace loads charts from `output/charts/{pair_id}/plotly/{chart_type}.json`"; Ace §"From Visualization Agent (Vera)" multi-pair chart organization directory tree.
**Problem:** Rule 3.9a correctly specifies the canonical loader path
`output/charts/{pair_id}/plotly/{chart_type}.json` with a bare `{chart_type}`
filename (no pair prefix). This matches VIZ-NM1 (Vera Phase 1 F-12 finding: pair
prefix in filename is prohibited by VIZ-NM1). However, the earlier "From
Visualization Agent (Vera)" section shows a legacy directory structure:

```
output/charts/
├── hy_ig_spy/
│   ├── hy_ig_spy_regime_prob_narrative_v1.json      ← pair-prefixed (wrong)
│   ├── hy_ig_spy_regime_prob_narrative_v1_meta.json ← pair-prefixed (wrong)
```

These pair-prefixed legacy filenames directly contradict VIZ-NM1 and Rule 3.9a's
canonical path. A new Ace reading the directory tree example would write a loader
expecting pair-prefixed names, which would fail to find Vera's bare-name outputs.
Wave 10F session notes confirm Vera already migrated to bare names, but Ace's SOP
still shows the pre-migration tree.
**Severity:** FAIL — the stale example in Ace's SOP directly contradicts the current
canonical loader contract. A new Ace dispatch would use the wrong path pattern.
**Who must fix:** Ace (Phase 4) — update the "From Visualization Agent" directory
tree example to show bare-name canonical paths (e.g., `regime_probability_timeline.json`,
`regime_probability_timeline_meta.json`). Add a note: "Pair-prefixed filenames
are a retired convention from pre-Wave-10F; all new charts use bare names per
VIZ-NM1."

---

### C1-A03 — APP-PT2 (Methodology page Exploratory Insights renderer) cited by VIZ-O1/VIZ-E1 but not defined as a named rule in Ace's SOP (WARN)

**Rule/section:** Vera SOP VIZ-O1 and VIZ-E1 (cross-reference APP-PT2 extensively); Ace SOP (no APP-PT2 rule found in reviewed sections).
**Problem:** Vera's Phase 1 review (deferred item 2) noted that APP-PT2 is
extensively cross-referenced from VIZ-O1 and VIZ-E1 but does not appear as a
named rule in Ace's SOP. Vera's SOP cites APP-PT2 as the consumer of `suggested`
and `retired` disposition sidecars (the Methodology page Exploratory Insights
renderer). The Ace SOP reviewed (all sections) does not have an explicit APP-PT2
rule block — APP-PT1 exists, but APP-PT2 is absent as a defined rule.
The closest match found is the "Indicator Evaluation Framework" section and
APP-PT1's `_render_exploratory_insights` reference, but these are not labeled
APP-PT2. If a future Vera dispatches a chart with `disposition: "suggested"` and
cross-references APP-PT2 for the consumption contract, Ace cannot find the rule.
**Severity:** WARN — functional behavior may exist in code even without a named
SOP rule, but the cross-reference is a dangling pointer from Vera to Ace.
**Who must fix:** Ace (Phase 4) — define APP-PT2 as a named rule in the Ace SOP,
covering: how the Methodology page Exploratory Insights section renders
`suggested`-disposition charts from `analyst_suggestions.json`; when a
`retired`-disposition chart is silently excluded vs. logged. Vera (Phase 4) —
confirm APP-PT2 cross-references in VIZ-O1/VIZ-E1 point to this new named rule.

---

### C1-A04 — Ace's `_meta.json` sidecar consumer contract in Evidence-page 8-element template uses caption fallback that may expose Vera's audit caption to end users (WARN)

**Rule/section:** APP §3.9 "Caption fallback chain" (appdev-agent-sop.md): "If Ray provides a caption AND Vera's sidecar has a different caption, log a warning but prefer Ray's (display ownership principle; Viz SOP Rule A5 grants Ray display ownership and Vera audit ownership)."
**Problem:** Ace's caption fallback chain cites "Viz SOP Rule A5" as the authority
for the display/audit ownership split. Vera's SOP does not have a rule labeled
"VIZ-A5" (the SOP has VIZ-A1 through VIZ-V13, VIZ-O1, VIZ-E1, VIZ-NBER1, etc.
— no A5 found in the Phase 1 review). This is a phantom cross-reference from Ace
to Vera (similar pattern to VIZ-IC1's phantom META-RYW / QA-CL6 cited by Vera).
If Vera's `_meta.json` sidecar caption is meant for audit purposes only (Quincy
reads it, not the end user), but Ace's fallback chain exposes it as a display
caption when Ray's caption is absent (caption fallback chain step 2:
`load_chart_metadata(chart_name).get("caption")`), Vera's internal audit text
could appear verbatim in the portal — potentially revealing technical identifiers
or non-layperson language.
**Severity:** WARN — phantom rule reference + potential audit-to-display caption
leakage.
**Who must fix:** Ace (Phase 4) — fix the phantom "Viz SOP Rule A5" reference
to the actual rule that governs the display/audit ownership split (if it exists)
or flag to Lead for definition. Add a guard: Vera's sidecar caption (step 2
fallback) should only render if its `audience_tier` is not `"technical"`.
Vera (Phase 4) — confirm whether `_meta.json` captions are display-quality or
audit-quality, and add a note to the sidecar schema clarifying the intended
audience for the `caption` field.

---

## Section 5 — Quincy (qa-agent-sop.md)

### C1-Q01 — GATE-VIZ-NBER2 hardcodes `dot_com` slug; LA-2 mandates `dotcom` (FAIL — LA-2 mandated)

**Rule/section:** GATE-VIZ-NBER2 "Episode–recession overlap table" (qa-agent-sop.md):
`| dot_com | 2000-03-01 → 2002-10-31 | ...`; LA-2 canonical slug set (`dotcom`, no underscore).
**Problem:** GATE-VIZ-NBER2's hardcoded episode table uses `dot_com` (with
underscore) as the slug for the Dot-Com episode. LA-2 mandates `dotcom` (no
underscore). Vera produces `history_zoom_dotcom.json` (canonical per VIZ-V12 and
LA-2). GATE-VIZ-NBER2's verification script builds the glob pattern
`output/charts/{pair_id}/plotly/history_zoom_dot_com.json` — which will never
match Vera's output file `history_zoom_dotcom.json`. Result: all dot-com zoom
charts escape GATE-VIZ-NBER2's NBER shading check with a false PASS (file not
found → check skipped for this episode), including charts that may be missing
required shading.
**Severity:** FAIL — a gate designed to catch missing NBER shading silently does
not execute for the dot-com episode because the slug is wrong.
**Who must fix:** Quincy (Phase 4, LA-2 mandated) — update GATE-VIZ-NBER2's
hardcoded episode-overlap table to use `dotcom` (no underscore) and update all
derived glob patterns. Also replace `taper_2013`, `china_2015`, and `rates_2022`
with the canonical LA-2 slugs (`taper_2018`, and `inflation_2022`) or remove
non-canonical slugs pending registry promotion (per LA-2: these are non-canonical
until a registry PR is filed).

---

### C1-Q02 — GATE-27 PNG existence check severity is FAIL but VIZ-CV1 producer rule (VIZ-DP1 kaleido step) is WARN in Vera's SOP (severity asymmetry) (WARN)

**Rule/section:** GATE-27 "PNG existence check (D4, Wave 10K) — promoted to FAIL" (qa-agent-sop.md): "If count = 0 for any pair, log as FAIL (blocking)"; VIZ-CV1 / Rule V5 (Vera SOP): perceptual PNG is now committed to git (WARN-level finding F-03 in Phase 1 identified ghost reference to prior phrasing).
**Problem:** GATE-27 at the QA/cloud-verify stage is a hard FAIL if perceptual PNGs
are absent. VIZ-CV1 at the Vera producer stage mandates that PNGs be committed
before handoff. The Vera SOP's VIZ-DP1 (producer-side dual-panel check) is the
only rule that describes a "blocking pre-save" gate that could catch missing PNGs
before handoff. However, VIZ-V11 (which covers kaleido renders / perceptual PNGs)
is described in Vera's SOP as a "paper rule" per Phase 1 F-11 — VIZ-V11 has no
implementation script, just a prose description of a blocking check. If VIZ-V11 is
effectively unenforced at the producer stage, Vera can complete handoff without
PNGs, and the first enforcement point is Quincy's GATE-27 FAIL — at which point the
pair is already in QA review.
The asymmetry: producer-side is a prose-only rule with no script (WARN risk);
consumer-side is a hard FAIL.
**Severity:** WARN — the gate severity at QA is correctly FAIL. The concern is that
the producer-side enforcement gap (VIZ-V11 no-script status) means the FAIL
systematically arrives at QA rather than being caught at Vera's handoff.
**Who must fix:** Vera (Phase 4, also backlog item per Phase 2 D2) — reference
`scripts/viz_v11_palette_lint.py` (or confirm VIZ-IC1 check 4 is the implementation)
in VIZ-V11. Making VIZ-V11 a script-enforced gate at Vera's handoff converts GATE-27
from a discovery gate to a confirmation gate — as it should be per META-SRV.

---

### C1-Q03 — GATE-DP1 "abort browser run on failure" — QA SOP says abort; Phase 2 notes code "logs and continues" (FAIL — Phase 2 A5 item)

**Rule/section:** GATE-DP1 "Integration point" (qa-agent-sop.md): "Hard-fail (abort browser run) if any GATE-DP1 failures are returned"; Phase 2 A5: "GATE-DP1 abort behavior — SOP says 'abort browser run on failure'; code logs and continues."
**Problem:** Vera's producer-side companion to GATE-DP1 is VIZ-DP1 (dual-panel
axis check). Vera's VIZ-DP1 produces the `check_dual_panel_axis_assignment()`
function — the same structural check that GATE-DP1 runs at QA. VIZ-DP1 says
Vera should run this check before handoff and it is a producer-side blocking gate.
GATE-DP1 in Quincy's SOP says if failures are returned, "hard-fail (abort browser
run)." But Phase 2 A5 confirms the actual `scripts/cloud_verify.py` code logs
failures and continues rather than aborting. This means a Vera-side VIZ-DP1 failure
that Vera self-certifies as passing could still cause GATE-DP1 failures in QA —
but QA's script would not abort as the SOP requires.
The severity of the SOP↔code drift affects Vera because: (a) GATE-DP1 failing
at QA means Vera's VIZ-DP1 pre-handoff check was either not run or produced a
different result, and (b) if QA doesn't abort, Quincy may sign off on charts with
blank bottom panels if HABIT-QA1 DOM reading is not thorough.
**Severity:** FAIL (Phase 2 A5 item, Quincy owns fix). From Vera's perspective: WARN
— Vera's producer-side VIZ-DP1 is the preventive gate; GATE-DP1's abort behavior
is Quincy's code fix. Flagged here as a cross-reference integrity issue (SOP says
abort; code does not).
**Who must fix:** Quincy (Phase 4, A5) — fix `scripts/cloud_verify.py` to abort
browser run on GATE-DP1 failures. Vera — no fix required; VIZ-DP1 is already the
correct producer-side implementation.

---

### C1-Q04 — GATE-HZE1 FAIL/WARN disposition maps exactly to VIZ-HZE1 skip protocol, but QA SOP does not explicitly cite VIZ-HZE1 as the authoritative skip format (WARN)

**Rule/section:** GATE-HZE1 "WARN disposition: Vera blocker" (qa-agent-sop.md): "no `history_zoom_*.json` file exists for the pair — Charts not yet produced → Ray has authored the narratives but Vera has not generated the zoom charts yet"; VIZ-HZE1 structured skip protocol (Vera SOP).
**Problem:** GATE-HZE1's WARN disposition correctly identifies "Vera blocker — zoom
charts not yet committed" as the trigger when the "Past Crises" heading is absent
and no zoom JSON files exist on disk. However, the QA SOP does not cite VIZ-HZE1
as the mechanism by which Vera signals authorized skips. VIZ-HZE1 mandates a
structured skip entry in `_meta.json` when a zoom chart is not produced due to data
coverage; this entry is the auditable record of Vera's intent. GATE-HZE1's WARN
path does not check for a VIZ-HZE1 skip entry in `_meta.json` — it only checks
file existence on disk.
Result: GATE-HZE1 WARN applies equally to:
- Vera legitimately skipped with a VIZ-HZE1 entry (authorized absence)
- Vera simply hasn't produced the chart yet (pending, Vera blocker)
These are different situations requiring different actions (no action needed vs.
escalate to Vera), but GATE-HZE1 cannot distinguish them.
**Severity:** WARN — the gate fires correctly (WARN either way), but Quincy cannot
determine whether to file a Vera blocker or note the authorized skip without reading
`_meta.json` manually.
**Who must fix:** Quincy (Phase 4) — add a check to GATE-HZE1 WARN path: if a
VIZ-HZE1 skip entry exists in `_meta.json` for the pair+episode, record as
"GATE-HZE1 AUTHORIZED SKIP — VIZ-HZE1 entry confirmed" instead of "Vera blocker."
Vera (Phase 4) — add a note to VIZ-HZE1: "QA's GATE-HZE1 reads the `_meta.json`
skip entry to distinguish authorized absence from pending production; ensure skip
entry format is machine-parsable."

---

### C1-Q05 — GATE-27 "chart rendering validation" renamed from "smoke test" in Wave 10J but QA-CL4 text uses both terms inconsistently (WARN — vocabulary drift)

**Rule/section:** GATE-27 preamble in QA-CL4 (qa-agent-sop.md): "Vera's chart rendering validation (VIZ-CV1 / VIZ-V5): every canonical chart artifact loads via Plotly... (Vera's check is called 'chart rendering validation', not 'smoke test' — see Wave 10J taxonomy)"; earlier QA-CL4 text: "GATE-27 — End-to-End Chart Render Test."
**Problem:** Wave 10J renamed Ace's check to "portal lint" and Vera's check to
"chart rendering validation" to distinguish them from Quincy's "cloud smoke test."
The QA-CL4 section header is "GATE-27 — End-to-End Chart Render Test" — neither
"smoke test" nor "chart rendering validation" — and the body parenthetically notes
the Wave-10J taxonomy renaming. Vera's SOP uses "VIZ-V5" as the rule for chart
rendering validation (smoke test in earlier waves). Research SOP's RES-CPC1 says
"The term 'smoke test' is retired from Ray's SOP for this check class" — applying
the same taxonomy shift.
The QA SOP's gate header still says "End-to-End Chart Render Test" where it should
say something that does not conflict with the Wave-10J taxonomy. Vera's and Ray's
SOPs have adopted the new vocabulary; QA-CL4's GATE-27 header has not.
**Severity:** WARN — terminology inconsistency between SOPs, creating coordination
confusion when agents reference gates by name.
**Who must fix:** Quincy (Phase 4) — update GATE-27 header in QA-CL4 to align with
Wave-10J taxonomy. The exact label should be confirmed with Lead.

---

## Cross-Cutting Themes

Three dominant themes emerge across all five peer relationships:

### Theme 1 — Episode slug namespace fragmentation (LA-1 / LA-2)
Ray (RES-HZE1 example uses `rates_2022`), Quincy (GATE-VIZ-NBER2 uses `dot_com`,
`taper_2013`, `china_2015`, `rates_2022`) all reference non-canonical slugs.
Findings: C1-R01, C1-Q01. These are LA-2 mandated fixes that cascade across all
four agents (Ray, Ace, Quincy, Evan per Phase 2).

### Theme 2 — Skip-protocol overlap and state ambiguity
The three-state protocol (authorized VIZ-HZE1 skip / Vera-not-yet-delivered /
Ace config missing) is not jointly documented in any single SOP. Vera's VIZ-HZE1,
Ace's ACE-HZE1, and Quincy's GATE-HZE1 each describe one facet of this protocol
without cross-referencing the others' facets. Findings: C1-E03, C1-A01, C1-Q04.

### Theme 3 — Phantom cross-references to non-existent or renamed rules
Ace cites "Viz SOP Rule A5" (does not exist); ECON-H4 cites "VIZ canonical catalog"
(not a named artifact); RES-20 cites `output/charts/chart_type_registry.json`
(wrong path). Findings: C1-E01, C1-A04, C1-R05. These are the same class as
VIZ-IC1's phantom META-RYW / QA-CL6 (Phase 1 F-06) — phantom references across
multiple SOPs are a systemic documentation hygiene issue.

---

## Summary Table

| ID | Peer | Severity | Problem (one line) | Fix owner |
|----|------|----------|--------------------|-----------|
| C1-D01 | Dana | WARN | `display_name_registry.csv` vs DATA-D5 sidecar: dual axis-label sources, Vera unclear on which to read | Dana + Vera |
| C1-D02 | Dana | WARN | Data-to-Viz handoff omits `_meta.json` provenance fields; Vera must hand-fill | Dana + Vera |
| C1-D03 | Dana | WARN | D2 unit convention registry cross-ref to VIZ-A2 is one-way; VIZ-A2 has no reciprocal ref | Vera |
| C1-E01 | Evan | FAIL | ECON-H4 `expected_chart` is a description, not a VIZ-NM1 canonical filename; Vera cannot resolve | Evan |
| C1-E02 | Evan | FAIL | ECON-H5 cites `winner_summary.schema.json` v1.0.0; live is v1.1.0; Vera reads direction from stale schema | Evan (LA-10) |
| C1-E03 | Evan | WARN | ECON-H4 `blocked` status cites GATE-25 but doesn't clarify which `_meta.json` skip format Vera should use | Evan + Vera |
| C1-E04 | Evan | WARN | C2 table says `quartile_returns.csv`; ECON-H4 example says `regime_quartile_returns.csv` — two filenames | Evan |
| C1-R01 | Ray | FAIL | RES-HZE1 uses `rates_2022` slug and `episode_registry.json` path — both non-canonical per LA-1/LA-2 | Ray (LA-1, LA-2) |
| C1-R02 | Ray | WARN | RES-ZOOM1 `ZOOM_EPISODE_NARRATIVES` attribute still in research SOP; LA-3 mandates retirement | Ray (LA-3) |
| C1-R03 | Ray | WARN | RES-NR1 / Rule 8 chart-path references VIZ-NM1 implicitly but no cross-reference exists | Ray |
| C1-R04 | Ray | FAIL | Ray may pass `chart_status: "ready"` (banned by RES-22) to `_meta.json` that Vera authors | Ray + Vera |
| C1-R05 | Ray | WARN | RES-17/RES-20 conflate `chart_type_registry.json` and `history_zoom_events_registry.json` for slug validation | Ray + Vera |
| C1-A01 | Ace | FAIL | APP-PT1 "silently skip" on absent `HISTORY_ZOOM_EPISODES` collapses authorized VIZ-HZE1 skip and pending into one undifferentiated state | Ace + Vera |
| C1-A02 | Ace | FAIL | Ace SOP "From Vera" directory tree shows legacy pair-prefixed filenames that contradict VIZ-NM1 and Rule 3.9a | Ace |
| C1-A03 | Ace | WARN | APP-PT2 cited extensively by VIZ-O1/VIZ-E1 but not defined as a named rule in Ace's SOP | Ace + Vera |
| C1-A04 | Ace | WARN | Caption fallback chain cites phantom "Viz SOP Rule A5"; audit caption may leak to portal display | Ace + Vera |
| C1-Q01 | Quincy | FAIL | GATE-VIZ-NBER2 uses `dot_com` slug → glob never matches Vera's `history_zoom_dotcom.json` → NBER check silently skipped for dot-com | Quincy (LA-2) |
| C1-Q02 | Quincy | WARN | GATE-27 PNG check is hard FAIL; VIZ-V11 kaleido producer check is script-less (paper rule) — severity asymmetry | Vera (Phase 4) |
| C1-Q03 | Quincy | FAIL | GATE-DP1 abort-on-failure in SOP contradicts code behavior (logs and continues) — Phase 2 A5 item | Quincy |
| C1-Q04 | Quincy | WARN | GATE-HZE1 WARN path cannot distinguish VIZ-HZE1 authorized skip from Vera-not-yet-delivered | Quincy + Vera |
| C1-Q05 | Quincy | WARN | GATE-27 header uses "End-to-End Chart Render Test" — out of sync with Wave-10J vocabulary taxonomy | Quincy |

**Total findings: 21**
**By severity:** FAIL = 8, WARN = 13
**By peer:** Dana = 3, Evan = 4, Ray = 5, Ace = 4, Quincy = 5

---

*Written: 2026-05-08 — Phase 3 cross-SOP review (no peer SOP edits made, LEAD-DL1 respected)*
