# Research Ray — Phase 3 Cross-SOP Review (Handoff Perspective)

**Reviewer:** Research Ray
**Date:** 2026-05-08
**Branch:** 260430
**Scope:** Handoff concerns only — contract mismatches, severity asymmetry, cross-ref integrity, vocabulary drift, trigger-condition mismatches. No SOP edits (LEAD-DL1). LA-1 through LA-10 treated as binding; not re-litigated.
**Inputs reviewed:** data-agent-sop.md, econometrics-agent-sop.md, visualization-agent-sop.md, appdev-agent-sop.md, qa-agent-sop.md

---

## Section 1 — Dana (Data Agent)

### C-D1 — indicator_nature / indicator_type Enum Vocabulary Diverges from Ray's Research Taxonomy
**Rule(s):** DATA-D6 / Rule D3 (Step 2 classification decision) vs. Ray's narrative buckets
**Problem:** Dana's SOP explicitly documents the mismatch in Rule D3 Step 2: "Ray's research taxonomy uses reader-facing buckets such as Credit Spread, Rates, Activity/Survey, Volatility, Sentiment/Flow, and Cross-Asset; Dana still writes only the schema enum above." However, the mapping rules are one-directional and incomplete:
- "Activity/Survey" maps to `production`, `sentiment`, or `macro` — three distinct destinations with no tiebreaker. A new Dana dispatch must choose without a deterministic rule.
- "Cross-Asset" "usually maps to `price`" — the word "usually" introduces discretion in a blocking-gate field that is read by Evan's Rule C1 method router. If Dana classifies a Cross-Asset series as `volatility` (e.g., VIX/VIX3M ratio, which is also "Cross-Asset" in Ray's taxonomy), Evan's method category selection (Rule C1) changes, producing a different mandatory method set. Ray then cites methods that were not run or misses methods that were run.
- Dana's Rule D3 does not say "coordinate with Ray before classifying ambiguous types." Evan's SOP (§2.5 step 1) says "If Ray's indicator type classification is ambiguous or borderline, request clarification before running the category selection heuristic." But Ray's research SOP (RES-IT1, not reviewed in Phase 3) and Dana's D3 do not describe the same clarification path. The path originates with Evan, not Dana, so a Dana dispatch may write a classification that Evan then disputes without a clear escalation owner.
**Severity:** WARN (non-blocking gap). Classification is a blocking gate field, but the practical risk is escalated ambiguity rather than a silent wrong value.
**Who must fix:** Dana SOP Phase 4 — sharpen "Activity/Survey → production vs. sentiment vs. macro" tiebreaker rule; add explicit "if borderline, coordinate with Ray (per RES-IT1) and Evan (per ECON §2.5) before writing." Also cross-reference so all three SOPs name the same clarification path.

---

### C-D2 — DATA-D6b "Narrative Instrument Reference Accuracy" Cites META-RYW as a Cross-Reference — META-RYW Does Not Exist in Any SOP
**Rule(s):** DATA-D6b (raw column identifier in user-facing fields), cross-reference list
**Problem:** DATA-D6b cross-references include "META-RYW (Read Your Own Work — Dana must re-read `key_finding` before handoff and catch this class)." META-RYW does not appear in team-coordination.md or any other SOP (not in standards.md, not in data-agent-sop.md body). The rule cites a phantom rule ID. Ray's companion rule RES-NR1 is correctly cited in the DATA-D6b cross-references, and GATE-NR (QA consumer) is also cited correctly. The phantom META-RYW is the only broken link but it is named as a self-check protocol, so a Dana author following the cross-reference trail finds nothing.
**Severity:** WARN (non-blocking, phantom cross-reference only). The functional requirement (re-read `key_finding` before handoff) is clear from prose; the rule ID is unfindable.
**Who must fix:** Dana SOP Phase 4 — either register META-RYW as a real protocol in team-coordination.md and standards.md, or replace the cross-reference with a standalone "(self-check: grep key_finding string for raw column patterns before handoff)" directive that does not rely on a phantom rule ID.

---

### C-D3 — Quality Gates Checklist Missing DATA-D6b Rule Item Despite Blocking Status
**Rule(s):** DATA-D6b, Data Agent Quality Gates checklist (lines 482–513)
**Problem:** DATA-D6b was added 2026-04-22 (Wave 10G.5) as a blocking rule. The Quality Gates checklist (which is the operational pre-handoff gate a Dana author executes) does not include a `[ ] Rule DATA-D6b` entry. The checklist covers DATA-D5, DATA-D6, DATA-D11, DATA-D12, DATA-D13 by name, plus DATA-VS and DATA-R1. DATA-D6b is absent. A Dana dispatch completing the checklist will not run the DATA-D6b producer-side lint (grep `key_finding` for raw column identifiers). Ray, as the narrative author, depends on Dana's `key_finding` field being human-readable before authoring the corresponding narrative section. If the field leaks raw column IDs (e.g., `hy_ig_spread_pct`, `spy_fwd_63d`) into the pair config, Ray may faithfully reproduce those identifiers in narrative text, producing an RES-NR1 / GATE-NR failure downstream.
**Severity:** FAIL (blocking). The producer-side lint that prevents a downstream narrative error is not a gate item; therefore the lint is not run operationally.
**Who must fix:** Dana SOP Phase 4 — add `[ ] Rule DATA-D6b — Human-readable name lint: grep key_finding string for raw column pattern tokens; no matches before handoff. Record grep result in handoff note.`

---

## Section 2 — Evan (Econometrics Agent)

### C-E1 — ECON-H5 winner_summary.json Schema Version Cited as v1.0.0 — Live Schema Is v1.1.0
**Rule(s):** ECON-H5 (winner_summary.json producer contract), Phase 2 finding A6
**Problem:** ECON-H5 states: "Canonical schema: `docs/schemas/winner_summary.schema.json` (per META-CF, owned by Evan, version 1.0.0)." Lead's Phase 2 (finding A6) confirmed: "ECON-H5 (Evan) cites 'winner_summary.schema.json v1.0.0'. Stale; live schema is v1.1.0." This is an LA-10 item. From Ray's handoff perspective, this matters because RES-18 reads OOS headline metrics from `winner_summary.json` fields that were added or modified in v1.1.0 (specifically `oos_period_start`, `oos_period_end` — which ECON-OOS1 states "MUST be copied verbatim from `oos_split_record`"). If Evan produces a v1.0.0-conformant file while the running schema is v1.1.0, fields Ray reads may have different names or semantics than Ray's rule expects.
**Severity:** WARN (non-blocking under current pairs; would become blocking if a v1.1.0-specific field Ray reads is absent or differently named in a v1.0.0 file). The practical impact is Evan's producer-side validator may be checking the wrong schema version, letting a non-conformant instance through.
**Who must fix:** Evan SOP Phase 4 — update ECON-H5 version citation to v1.1.0 per LA-10. This is an Evan-owned fix, not Ray's. Cross-reference: Ray's RES-18 must not hand-type the field names; it reads whatever `oos_split_record.json` contains, which decouples Ray from schema drift as long as ECON-OOS1's verbatim-copy rule holds.

---

### C-E2 — ECON-CP1/CP2 Delivery Does Not Trigger an Explicit Handoff Message to Ray
**Rule(s):** ECON-CP1 / ECON-CP2 (Econometrics SOP §cross-period commentary), RES-CP1 / RES-CP2 (Research SOP)
**Problem:** Ray's Phase 1 finding F-04 (already in Phase 1, not repeated here per instructions) concerned the trigger-condition mismatch between RES-CP2 and ECON-CP2. The complementary gap — not in Phase 1 — is that ECON-CP1 is described in the Econometrics SOP but there is no explicit delivery artifact or handoff message step for Evan to notify Ray that ECON-CP1 output is ready. Lead Phase 2 (finding B3) notes "ECON-FE1 → no GATE-ES1 cross-link (Evan F-04)" as a similar sequencing gap. For ECON-CP1, the same pattern: Evan runs the sub-period analysis, writes output files to `results/{pair_id}/`, but the Econometrics SOP has no "handoff message to Ray" step for ECON-CP1 delivery (unlike the tournament winner handoff to Ray in ECON-H5 and the tournament handoff for `strategy_objective` classification). Ray's RES-CP1 says "mandatory alongside ECON-CP1" — but if Evan does not send a trigger message, a Ray dispatch may start narrative authoring before the ECON-CP1 output files have landed, and Ray silently skips RES-CP1 because the files are not yet present.
**Severity:** WARN (non-blocking gap, same pipeline-timing risk as F-04 in Phase 1). Causes silent narrative omission.
**Who must fix:** Evan SOP Phase 4 — add to the ECON-CP1 procedure: "Upon completing ECON-CP1 output, send a structured handoff message to Ray: paths to sub-period output files, the sub-period labels, and a flag indicating whether regime_story=true (ECON-CP2 may follow)." Cross-reference RES-CP1 in that message.

---

### C-E3 — Evan's "headline metrics" Vocabulary in ECON-H5/OOS1 Differs From Ray's "headline" in RES-18
**Rule(s):** ECON-H5, ECON-OOS1 (headline metric fields in winner_summary.json), RES-18 (headline template constraint for narrative)
**Problem:** ECON-H5 uses "Headline Findings" and "KPI Values" as section names in the App Dev Handoff Template. ECON-OOS1 uses "headline numbers" informally in the regression note context. RES-18 uses "headline" to mean the specific narrative sentence in the portal's Story page that reads: "[indicator] generated an OOS Sharpe of X over Y months (YYYY-MM to YYYY-MM), compared to buy-and-hold Z." Ray's RES-18 rule specifies that the OOS span must be read from `oos_split_record.json` (not hand-typed) and the Sharpe from `winner_summary.json`. The term "headline" is used with different referents: Evan uses it for the App Dev display summary table; Ray uses it for a specific narrative sentence with strict sourcing rules. A new cross-agent author reading both SOPs may confuse Evan's "Headline Findings" (a broad data summary for Ace) with Ray's "headline" (a strictly sourced narrative sentence). This creates risk that a Ray author writes the headline from Evan's informal narrative summary rather than from the specified JSON fields.
**Severity:** WARN (non-blocking vocabulary drift). The two uses are technically distinct and context-disambiguates them, but a novice cross-agent reading would not recognize the distinction.
**Who must fix:** Both SOPs in Phase 4 — Evan should rename "Headline Findings" in the App Dev Handoff Template to "Executive KPI Summary" or "Key Metrics Block" to remove the "headline" overlap. Ray's RES-18 could add a parenthetical "(see RES-18 for the specific narrative sentence format; this is distinct from Evan's KPI summary table)" to prevent readers from conflating the two uses.

---

### C-E4 — VIZ-ZOOM1 Episode Selection Step Reads from `episode_registry.json` (deprecated per LA-1) — Evan's ECON-CP1 Has the Same Dependency
**Rule(s):** VIZ-ZOOM1 §"Episode selection for zoom charts", ECON-CP1 sub-period analysis, LA-1 (episode_registry.json deprecated), LA-2 (canonical slug set)
**Problem:** VIZ-ZOOM1 (Vera's SOP) states: "Read from `docs/schemas/episode_registry.json` keyed on `interpretation_metadata.indicator_category`." Per LA-1, `episode_registry.json` is deprecated and `history_zoom_events_registry.json` is canonical. This is a Vera-side issue (Phase 3 for Vera). The handoff concern for Ray is: ECON-CP1 in the Econometrics SOP references episode-based sub-period analysis, and if Evan's sub-period labeling uses episode slugs from the deprecated `episode_registry.json` (e.g., `dot_com`, `rates_2022`), Ray's RES-CP1 sub-period commentary will use those same non-canonical slugs in narrative text. Ray's narrative for the "2022 rates shock" episode will label it "rates_2022" while Vera's zoom chart is named `history_zoom_inflation_2022.json` (canonical per LA-2). The episode labels in Ray's cross-period prose and Vera's zoom chart filename will not match, creating a reader-visible inconsistency even after LA-1/LA-2 are applied to the registry files.
**Severity:** FAIL (blocking, coordinated fix required). The slug retargeting required by LA-1/LA-2 must propagate through Evan's ECON-CP1 sub-period labels AND Ray's RES-CP1 prose in the same Phase 4 batch. A partial fix (registry only) leaves the slug mismatch in narrative text.
**Who must fix:** Evan SOP Phase 4 — update any episode slug references in ECON-CP1 to use canonical slugs (`inflation_2022`, not `rates_2022`; `dotcom`, not `dot_com`). Ray SOP Phase 4 — update RES-CP1 worked examples to use canonical slugs. Both must explicitly cite `history_zoom_events_registry.json` as the slug authority post-LA-1.

---

## Section 3 — Vera (Visualization Agent)

### C-V1 — VIZ-ZOOM1 Episode Selection Still Reads from Deprecated `episode_registry.json` (LA-1 Non-Compliance)
**Rule(s):** VIZ-ZOOM1 §"Episode selection for zoom charts", LA-1, LA-2
**Problem:** VIZ-ZOOM1 (Wave 10J) states: "Read from `docs/schemas/episode_registry.json` keyed on `interpretation_metadata.indicator_category`." Per LA-1, `history_zoom_events_registry.json` is canonical and `episode_registry.json` is deprecated. This is the most directly Ray-impacting Vera-side finding: Ray's RES-HZE1 slug validation also reads `episode_registry.json` (the pre-LA-1 state). Both rules must be simultaneously retargeted to `history_zoom_events_registry.json` in Phase 4 — otherwise a Phase-4 Vera dispatch that reads the canonical registry will generate charts under canonical slugs (`dotcom`, `inflation_2022`) while a Phase-4 Ray dispatch that reads the still-deprecated registry will validate slugs against `episode_registry.json` (`dot_com`, `rates_2022`). Ray's RES-HZE1 slug validation will then fail on Vera's canonical-slug charts. This is a compound of LA-1 and Phase-1 finding F-01 — noted here as the Vera-side leg that must be fixed in the same commit as Ray's leg.
**Severity:** FAIL (blocking). Coordinated simultaneous fix required across Vera (VIZ-ZOOM1, VIZ-HZE1) and Ray (RES-HZE1, RES-ZOOM1) in Phase 4.
**Who must fix:** Vera SOP Phase 4 (VIZ-ZOOM1 registry pointer), Ray SOP Phase 4 (RES-HZE1 registry pointer). Lead has already arbitrated (LA-1); this is an implementation gap remaining in both SOPs.

---

### C-V2 — VIZ-HZE1 Skip Protocol "history_zoom_{slug}_skip" Entry Location Conflicts with Ray's Handoff Expectations
**Rule(s):** VIZ-HZE1 §Skip Protocol, RES-HZE1 (Ray's pre-handoff slug-validation command), RES-9 (Phase-1 implicit) 
**Problem:** VIZ-HZE1's skip protocol says Vera adds a `history_zoom_{slug}_skip` entry to the pair's `_meta.json` at `output/charts/{pair_id}/plotly/_meta.json`. Ray's RES-HZE1 verification command checks for chart files at `output/charts/{pair_id}/plotly/history_zoom_{slug}.json` via `git ls-files`. When Vera legitimately skips a chart (data coverage fails), Ray's `git ls-files` check returns empty — which is correct behavior. However, RES-HZE1 does not describe how Ray should know whether an empty `git ls-files` result means "Vera has not yet generated the chart" vs. "Vera legitimately skipped it." Ray has no SOP step to read `_meta.json` for skip entries. A Ray author will see an empty `git ls-files` result and cannot distinguish between a Vera production failure and a Vera-documented skip, because Ray's SOP points only at the chart file, not the skip record.
**Severity:** WARN (non-blocking gap). The practical consequence is Ray filing an incorrect blocker against Vera for a legitimately skipped chart. The skip is documented on Vera's side; Ray has no instruction to read that documentation.
**Who must fix:** Ray SOP Phase 4 — add to RES-HZE1: "If `git ls-files` returns empty for a slug, check `output/charts/{pair_id}/plotly/_meta.json` for a `history_zoom_{slug}_skip` entry (per VIZ-HZE1). If the skip entry exists with a coverage reason, the chart is legitimately absent; do not file a Vera blocker. If no skip entry exists, file a Vera blocker." Cross-reference VIZ-HZE1's skip protocol in RES-HZE1.

---

### C-V3 — Rule A5 Caption Ownership Split Uses Different Vocabulary Than RES-HZE1 Episode Caption Field
**Rule(s):** VIZ Rule A5 (display caption = Ray, technical caption = Vera), ACE-HZE1 HISTORY_ZOOM_EPISODES schema (`caption` field), RES-HZE1 (Ray authors narrative and caption per episode)
**Problem:** Rule A5 defines: "Display caption (what the portal reader sees) — owned by Ray, in narrative content dict." "Technical caption (audit/metadata) — owned by Vera, in `{chart_name}_meta.json`." ACE-HZE1's `HISTORY_ZOOM_EPISODES` schema has a `caption` field described as "Ray-authored per RES-HZE1." Ace's rendering: "Each episode renders: title → narrative markdown → chart (`history_zoom_{slug}` via `load_plotly_chart`) → caption." The Ace SOP's caption fallback chain for the 8-element Evidence template (§3.9) specifies: "1. `content.get('caption')` (Ray's narrative-side); 2. `load_chart_metadata(chart_name).get('caption')` (Vera's sidecar)." This fallback works for Evidence-page method blocks but the HISTORY_ZOOM_EPISODES caption (Story page episode section) does NOT go through `load_chart_metadata` — it is read directly from the config object. The fallback chain is therefore absent for episode captions. If Ray delivers a `HISTORY_ZOOM_EPISODES` entry without a caption, the Story page renders no caption, with no fallback to Vera's `_meta.json` — silent omission. The caption ownership split in VIZ-A5 does not address this rendering path.
**Severity:** WARN (non-blocking, silent omission risk). An episode section with no caption is not an error — just a quality gap. But it is structurally different from the Evidence page which has a documented fallback.
**Who must fix:** Ace SOP Phase 4 — extend the caption fallback chain to apply to HISTORY_ZOOM_EPISODES episode rendering: "If `episode['caption']` is empty or absent, fall back to `load_chart_metadata(f'history_zoom_{episode["slug"]}').get('caption')`." Vera SOP Phase 4 — confirm that `history_zoom_{slug}_meta.json` sidecar always populates `caption` (per VIZ-O1 sidecar spec, this is already required). Ray SOP Phase 4 — RES-HZE1 should clarify that `caption` in the HISTORY_ZOOM_EPISODES dict is mandatory (not optional) to avoid triggering the fallback path on every pair.

---

### C-V4 — Vera's chart_status Field and RES-8 Gap Notice Protocol Reference Incompatible Vocabularies
**Rule(s):** VIZ SOP §"Chart-gap requests from Research Ray" (Vera updates `chart_status` field to `ready`, `pending`, `unavailable`), RES-8 (Ray flags gap and blocks Evidence page handoff to Ace), VIZ-O1 (disposition = `consumed` / `suggested` / `retired`)
**Problem:** Vera's "Chart-gap requests from Research Ray" section states: "Update Ray's narrative content dict `chart_status` field accordingly (`ready`, `pending`, or `unavailable` — see Research SOP 'chart_status field')." VIZ-O1 defines chart disposition as `consumed`, `suggested`, or `retired`. These are two parallel status vocabularies for the same charts. `chart_status: pending` (Vera→Ray communication) has no direct mapping to the VIZ-O1 disposition system — a chart with `chart_status: pending` would presumably be `disposition: consumed` once delivered, but during the waiting period it has no `_meta.json` disposition (which VIZ-O1 says is mandatory for every chart in the output directory). If Vera creates a stub `<chart_type>_meta.json` with `status: "requested_by_ray"` (as the gap-request protocol describes), what is the VIZ-O1 disposition for that stub? The stub is not `consumed`, `suggested`, or `retired`. Vera's stub `_meta.json` format violates VIZ-O1's three-value constraint.
**Severity:** WARN (non-blocking inconsistency). The practical impact is a Quincy VIZ-O1 check failing on stub sidecars during a wave where charts are pending.
**Who must fix:** Vera SOP Phase 4 — extend VIZ-O1's permitted disposition values to include `pending` (with an explicit "pending = chart requested and in-progress; will become consumed or retired on completion" semantics), or redefine the chart-gap stub sidecar to use `disposition: "suggested"` with a note that it converts to `consumed` on delivery. Cross-reference VIZ-O1 in the gap-request protocol. QA SOP Phase 4 — update the VIZ-O1 completeness check to accept `pending` during an active wave (if Vera SOP adds it) or reject stub sidecars as VIZ-O1 violations (if Vera SOP does not add it).

---

## Section 4 — Ace (App Dev Agent)

### C-A1 — ACE-HZE1 Cross-References `docs/schemas/episode_registry.json` (deprecated per LA-1)
**Rule(s):** ACE-HZE1 §"Audit Vera's chart directory and cross-check against episode registry" (step 2), LA-1
**Problem:** ACE-HZE1 step 2 states: "For each on-disk slug, Ace MUST cross-check the slug against `docs/schemas/episode_registry.json` keyed on `indicator_category` for the pair." Per LA-1, `episode_registry.json` is deprecated in favor of `history_zoom_events_registry.json`. Ace is therefore directed to validate slugs against the deprecated registry. A slug that is canonical per LA-2 (e.g., `dotcom`, `inflation_2022`) may or may not be present in `episode_registry.json` after it is converted to a thin pointer (the LA-1 conversion format is unspecified). If `episode_registry.json` becomes a stub that returns empty or redirects, Ace's cross-check will fail on all slugs or silently pass all slugs — either outcome is wrong.
**Severity:** FAIL (blocking). ACE-HZE1's slug validation will break after LA-1 is applied to `episode_registry.json` unless the pointer is updated simultaneously.
**Who must fix:** Ace SOP Phase 4 — update ACE-HZE1 step 2 to read `docs/schemas/history_zoom_events_registry.json` (canonical per LA-1) for slug validation. This must be a coordinated change with the Vera VIZ-ZOOM1 / VIZ-HZE1 retargeting (C-V1 above) and Ray's RES-HZE1 retargeting.

---

### C-A2 — APP-PT1 Narrative Authorship Contract Ownership Split for Trade Log Narrative Constants Is Unresolved
**Rule(s):** APP-TL1 §Narrative defaults / APP-PT1 Supplement — Narrative Authorship Contract, LEAD-DL1
**Problem:** APP-TL1 states: "Narrative defaults for steps 2, 3, 4 (disclosure, two-file model, column glossary) live as canonical constants in `page_templates.py`, authored by Ray, referenced by Ace's helper. Ace does NOT write the narrative prose; Ace wires the structure. Because this places Ray-authored constants in an Ace-owned implementation file, Lead must either record that narrow shared ownership in the ownership map or direct Ray to move the constants to a Ray-owned content artifact consumed by the template." The SOP explicitly acknowledges the unresolved ownership split and defers to Lead. From Ray's handoff perspective: Ray has no SOP rule (in research-agent-sop.md) requiring Ray to deliver trade log narrative constants. APP-PT1 Narrative Authorship Contract says "Ray's handoff to Ace includes the completed narrative fields" — but trade log narrative constants are not listed in RES-HZE1, RES-PA3, or any Ray-side delivery rule. Ray will not know to deliver these constants unless a Ray-side rule explicitly lists them.
**Severity:** WARN (non-blocking gap). Trade log disclosure text has a canonical default in the template; missing Ray-specific delivery creates an ownership gap but not a functional failure.
**Who must fix:** Lead must resolve the ownership map question (as noted in APP-TL1). If Ray owns the trade log narrative constants, Ray SOP Phase 4 must add a delivery requirement (akin to RES-PA3 for the "How to Read the Trade Log" subsection) specifying that Ray delivers canonical trade log disclosure text as a named artifact. If Ace owns the defaults, APP-PT1 must drop the "authored by Ray" attribution.

---

### C-A3 — APP-LP8 Status Label Table Uses Different Field Name Than ECON-FE1 Schema
**Rule(s):** APP-LP8 (Ace landing page evidence-status label), ECON-FE1 (Evan's evidence-status contract), GATE-ES1 (Quincy promotion verification)
**Problem:** APP-LP8's status table (§"Evidence-status honesty label") shows three labels for three `status` values: `found_in_search`, `needs_final_exam`, `passed_final_exam`. Ace reads these from `results/{pair_id}/evidence_status.json` keyed on `status`. ECON-FE1 defines the same three values with the same keys and calls them "evidence status semantics." GATE-ES1 (Quincy) checks `evidence_status.json` against `docs/schemas/evidence_status.schema.json`. The contract appears aligned — except that APP-LP8 also says "Schema-invalid status files degrade to the conservative `found_in_search` default and surface an APP-SEV1 L2 warning." ECON-FE1 does not describe what Evan should do if a schema validation failure occurs — Evan's SOP says "run `scripts/validate_schema.py`... block on failure." These two failure modes (producer blocks vs. consumer degrades) are not coordinated: if Evan blocks on validation failure and does not hand off, Ace never receives the file and correctly defaults to `found_in_search`. But if Evan accidentally ships an invalid file (skips the validation step), Ace silently degrades and the stakeholder sees the conservative label without knowing the file is invalid. Quincy's GATE-ES1 would catch this, but only for promotions above `found_in_search`. A `found_in_search` pair with an invalid `evidence_status.json` passes GATE-ES1 silently (GATE-ES1: "Missing files remain allowed and default to `found_in_search`; they do not trigger this gate").
**Severity:** WARN (non-blocking gap). The practical scenario (Evan ships an invalid file that slips through) requires Evan's validator to fail and the producer to bypass the block — low probability. But the gap is structurally unmonitored.
**Who must fix:** QA SOP Phase 4 — extend GATE-ES1 or add a new preflight check: "For all active pairs, if `evidence_status.json` is present, validate it against the schema regardless of `status` value. A present-but-invalid file at any status is a GATE-ES1 WARN (not FAIL for `found_in_search` pairs, since the correct display behavior is the same conservative default)." Evan SOP Phase 4 — add: "If schema validation fails and producer blocks shipment, notify Ace and Quincy that `evidence_status.json` will be absent; Ace should expect the conservative default."

---

### C-A4 — GATE-CL1 Cites "Ray leg pending" as Prohibited DOM Text — but This Phrasing Originates in Ace's Own Templates (Not a Ray-Authored String)
**Rule(s):** GATE-CL1 (GATE-CL1 content audit, APP SOP §Quality Gates), APP-PT1 Narrative Authorship Contract, RES-17 (Ray narrative frontmatter contract)
**Problem:** GATE-CL1 lists "Ray leg pending", "RES-17", "stub expected", "no narrative file found" as internal development stub text that must not appear in the DOM. These strings appear to originate from Ace's template code when Ray's narrative has not yet been delivered (the template generates a diagnostic string citing Ray's pending delivery). From Ray's perspective, this creates a handoff dependency: Ray must deliver narrative content before Ace deploys to Cloud, or the template renders diagnostic strings that become GATE-CL1 failures. However, Ray's SOP has no explicit "delivery sequencing" rule that says "narrative must be delivered before Ace's cloud deploy." The Phase 1 finding F-03 in Ray's SOP noted missing Quality Gate checklist items; one of those missing items should be "confirm Ace has no 'Ray leg pending' stubs before accepting the Ace handoff as complete." Ray currently has no SOP instruction to check for this class of Ace-side stub before sign-off.
**Severity:** WARN (non-blocking gap). The sequencing dependency exists implicitly but is not stated in either Ray's or Ace's SOP as a delivery prerequisite.
**Who must fix:** Ray SOP Phase 4 — add to RES-HZE1 (or the broader Quality Gates): "Before completing narrative handoff to Ace, confirm with Ace that no 'Ray leg pending' or 'stub expected' diagnostic strings appear in the current template for this pair. If such strings exist, they indicate a missing narrative field that Ray must deliver before Ace deploys." Ace SOP Phase 4 — add to APP-PT1 delivery prerequisites: "Do not deploy to Cloud while any 'Ray leg pending' string remains in any active pair's template output; resolve by either receiving Ray's prose or filing an explicit Ray blocker on the status board."

---

## Section 5 — Quincy (QA Agent)

### C-Q1 — GATE-NR Instrument Whitelist Scope Does Not Account for Ray's Episode Prose (Historical Zoom Section Contains Cross-Pair Instrument References by Design)
**Rule(s):** GATE-NR / QA-CL5 (narrative instrument reference check), RES-HZE1 (Ray episode narratives), RES-ZOOM1 (episode prose content requirements)
**Problem:** GATE-NR checks "any instrument name found in the narrative that does not match the pair's `target_symbol` or `indicator_id` is a GATE-NR FAIL." Ray's episode narratives (per RES-ZOOM1 and RES-HZE1) are required to describe historical episodes in economic context. Episode prose for the GFC or COVID episode will legitimately contain references to other instruments by design — e.g., "During the GFC, the S&P 500 fell 50% while credit spreads widened..." on a pair whose target is XLP, not SPY. GATE-NR's instrument extraction and comparison logic uses a `comparison_whitelist` ("clearly comparative context"), but the GATE-NR rule only explicitly addresses "appears in a clearly comparative context (e.g., 'unlike SPY, XLP...')" as a PASS-with-note. Episode prose is not "comparative" in the same sense — it is historical context, often citing index names (S&P 500, Nasdaq) as market backdrop, not as target-pair instruments. Ray's episode narratives for any non-SPY pair will likely contain "S&P 500" in historical context, which GATE-NR may flag as a FAIL rather than a PASS-with-note, blocking valid episode prose.
**Severity:** FAIL (blocking). Unless GATE-NR's whitelist logic is extended to recognize that historical episode prose (Story page HISTORY_ZOOM_EPISODES section) may legitimately contain cross-pair index references, every pair whose target is not SPY will trigger false-positive GATE-NR FAILs when Ray's episode narratives are deployed.
**Who must fix:** QA SOP Phase 4 — extend GATE-NR logic to exempt instrument references found inside the "How the Signal Performed in Past Crises" section (identified by the `HISTORY_ZOOM_EPISODES` section heading or surrounding DOM markers). Alternatively, define an explicit episode-context whitelist rule: "instrument names appearing in prose under the `### How the Signal Performed in Past Crises` heading are exempt from the wrong-pair instrument check, provided they appear as historical backdrop references (not as the pair's claimed target)." Cross-reference RES-HZE1 and RES-ZOOM1 as the producer rules that generate this legitimate cross-instrument prose.

---

### C-Q2 — GATE-HZE1 Assigns Producer Responsibility Based on Chart File Existence — But RES-HZE1 Mandates Ray Deliver Episode Narratives First, Making Ace's Config Block Pre-Conditional on Ray
**Rule(s):** GATE-HZE1 (QA structural check), ACE-HZE1 (Ace config population rule), RES-HZE1 (Ray narrative delivery rule)
**Problem:** GATE-HZE1's two failure dispositions are: "FAIL (Ace bug) — charts exist but heading absent" and "WARN (Vera blocker) — heading absent and no charts." Neither disposition names a Ray blocker scenario. However, ACE-HZE1 step 4 explicitly says: "If Vera's chart directory has zoom charts but Ray's handoff lacks episode narratives: Ace MUST NOT ship the config... Block config ship until Ray delivers per RES-HZE1." In this scenario — charts exist (Vera delivered) but Ray has not yet delivered episode narratives — GATE-HZE1 would fire a FAIL blaming Ace ("charts exist → heading must render → heading absent = Ace bug"). But the actual root cause is Ray's missing narrative delivery, which blocked Ace from populating the config. GATE-HZE1's failure analysis assigns the wrong owner.
**Severity:** WARN (non-blocking mismatch). GATE-HZE1's two-case logic correctly handles two of three production scenarios but misclassifies the third (Ray blocker preventing Ace config population).
**Who must fix:** QA SOP Phase 4 — extend GATE-HZE1 failure disposition to a three-case analysis: "FAIL (Ace bug): charts exist, heading absent, AND Ray's narratives were delivered (Ray blocker resolved). FAIL (Ray blocker, Ace compliant): charts exist, heading absent, AND status-board shows 'ACE-HZE1 BLOCKER [Ray]' for this pair — owner is Ray, not Ace. WARN (Vera blocker): no charts and no heading." Add: "Before assigning GATE-HZE1 FAIL to Ace, Quincy must check `_pws/_team/status-board.md` for an active Ray blocker entry for the pair."

---

### C-Q3 — QA-CL3 Requires verification of `memories.md` Update — LA-7 Retires `memories.md` for Ray; QA-CL3 Checklist Is Not Updated to Reflect LA-7
**Rule(s):** QA-CL3 (agent memory discipline verification), LA-7 (Ray's `memories.md` requirement removed)
**Problem:** QA-CL3 mandates: "For every agent dispatched in the wave, verify... `wc -l ~/.claude/agents/<role>-<name>/memories.md` — same [line count must have increased]." LA-7 states: "Ray's `memories.md` requirement is removed from research-agent-sop.md. Reflection consolidates to `experience.md` to match team norm." After LA-7 is applied, Ray will only update `experience.md`, not `memories.md`. QA-CL3 will then flag Ray as a QA-CL3 FAIL (first occurrence PASS-with-note, subsequent FAIL) for not updating a file that Ray is no longer required to update. This is a direct conflict between a Lead arbitration (LA-7) and the QA compliance check (QA-CL3).
**Severity:** FAIL (blocking after first occurrence). After LA-7 is implemented, every Ray dispatch will accumulate QA-CL3 warnings that will escalate to blocking failures on subsequent waves, unless QA-CL3 is updated to exempt Ray from the `memories.md` line-count check.
**Who must fix:** QA SOP Phase 4 — add an agent-specific exemption note in QA-CL3: "For research-ray: `memories.md` check is N/A per LA-7 (2026-05-08). Verify only `experience.md` and `session-notes.md`. Other agents: standard check applies." This exemption note must be added in the same Phase 4 wave that Ray SOP removes the `memories.md` requirement.

---

### C-Q4 — GATE-VIZ-NBER2 Episode-Recession Overlap Table Uses Deprecated Slug Set (dot_com, rates_2022) — Conflicts with LA-2
**Rule(s):** GATE-VIZ-NBER2 (QA SOP), LA-2 (canonical slug set: `dotcom`, `inflation_2022`)
**Problem:** GATE-VIZ-NBER2's "Episode–recession overlap table" hardcodes the following slugs: `dot_com`, `gfc`, `covid`, `taper_2013`, `china_2015`, `rates_2022`. Per LA-2, `dot_com` → `dotcom` and `rates_2022` → `inflation_2022` are non-canonical. The GATE-VIZ-NBER2 check derives the slug from the filename `history_zoom_{slug}.json`. If Phase 4 retargeting produces chart files named `history_zoom_dotcom.json` (canonical) and `history_zoom_inflation_2022.json` (canonical), GATE-VIZ-NBER2's hardcoded overlap table will not recognize `dotcom` (it expects `dot_com`) and will not find an NBER overlap classification for `inflation_2022` (it has `rates_2022`). The gate will either silently skip these charts (no FAIL, no WARN) or classify them as non-recession slugs and apply the WARN path incorrectly.
**Severity:** FAIL (blocking post-Phase-4). After LA-2 slug retargeting, GATE-VIZ-NBER2 will produce incorrect verdicts for the two renamed slugs.
**Who must fix:** QA SOP Phase 4 — update the GATE-VIZ-NBER2 overlap table to use LA-2 canonical slugs: `dot_com` → `dotcom`, `rates_2022` → `inflation_2022`. Also remove `taper_2013` and `china_2015` from the table if they are not canonical per LA-2 (LA-2 lists only `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`; `taper_2013` and `china_2015` are not in the canonical set). Note: `taper_2018` is canonical per LA-2 but absent from GATE-VIZ-NBER2's table — add it.

---

## Summary Table

| Finding | Peer | Severity | Owner |
|---------|------|----------|-------|
| C-D1 | Dana | WARN | Dana SOP Phase 4 |
| C-D2 | Dana | WARN | Dana SOP Phase 4 |
| C-D3 | Dana | FAIL | Dana SOP Phase 4 |
| C-E1 | Evan | WARN | Evan SOP Phase 4 |
| C-E2 | Evan | WARN | Evan SOP Phase 4 |
| C-E3 | Evan | WARN | Evan/Ray SOP Phase 4 |
| C-E4 | Evan | FAIL | Evan+Ray SOP Phase 4 (coordinated) |
| C-V1 | Vera | FAIL | Vera+Ray SOP Phase 4 (coordinated) |
| C-V2 | Vera | WARN | Ray SOP Phase 4 |
| C-V3 | Vera | WARN | Ace+Vera+Ray SOP Phase 4 |
| C-V4 | Vera | WARN | Vera+QA SOP Phase 4 |
| C-A1 | Ace  | FAIL | Ace SOP Phase 4 |
| C-A2 | Ace  | WARN | Lead + Ray/Ace SOP Phase 4 |
| C-A3 | Ace  | WARN | QA+Evan SOP Phase 4 |
| C-A4 | Ace  | WARN | Ray+Ace SOP Phase 4 |
| C-Q1 | Quincy | FAIL | QA SOP Phase 4 |
| C-Q2 | Quincy | WARN | QA SOP Phase 4 |
| C-Q3 | Quincy | FAIL | QA SOP Phase 4 |
| C-Q4 | Quincy | FAIL | QA SOP Phase 4 |

**Count by peer:**
- Dana: 3 findings (1 FAIL, 2 WARN)
- Evan: 4 findings (1 FAIL, 3 WARN)
- Vera: 4 findings (2 FAIL, 2 WARN)
- Ace: 4 findings (1 FAIL, 3 WARN)
- Quincy: 4 findings (3 FAIL, 1 WARN)

**Total:** 19 findings, 8 FAIL, 11 WARN

**Top-3 cross-cutting themes:**
1. **LA-1/LA-2 slug retargeting not yet propagated through consuming SOPs** — VIZ-ZOOM1, VIZ-HZE1, ACE-HZE1, RES-HZE1, GATE-VIZ-NBER2 all still reference the deprecated `episode_registry.json` or the non-canonical slug strings (C-V1, C-A1, C-Q4, C-E4). Phase 4 must retarget all five in the same commit batch.
2. **GATE-NR and GATE-HZE1 failure classification gaps** — GATE-NR will false-positive on legitimate episode prose cross-instrument references (C-Q1, FAIL); GATE-HZE1 misclassifies a Ray-blocker-as-Ace-bug scenario (C-Q2, WARN). Both QA gates need extended case logic before Phase 4 episode content ships.
3. **Memory/checklist rule items not updated to reflect LA-7 and new blocking rules** — Dana's Quality Gates missing DATA-D6b (C-D3, FAIL), QA-CL3 will FAIL Ray for not updating `memories.md` after LA-7 removes the requirement (C-Q3, FAIL). Both are operational traps that will surface in the first post-Phase-4 wave.

---

*Phase 3 constraint observed: no edits to any file outside `_pws/research-ray/`. LEAD-DL1 respected.*
*Phase 4 has authority to make SOP edits.*
