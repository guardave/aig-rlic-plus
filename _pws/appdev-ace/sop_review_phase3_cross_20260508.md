# Phase 3 Cross-SOP Review — AppDev Ace (Handoff Perspective)

**Agent:** AppDev Ace  
**Date:** 2026-05-08  
**Task:** LEAD-DL1-scoped cross-review of the five peer SOPs from a handoff perspective. NO edits to any SOP or standards file in this phase.  
**Peer SOPs reviewed:**
- `docs/agent-sops/data-agent-sop.md` (Data Dana)
- `docs/agent-sops/econometrics-agent-sop.md` (Econ Evan)
- `docs/agent-sops/visualization-agent-sop.md` (Viz Vera)
- `docs/agent-sops/research-agent-sop.md` (Research Ray)
- `docs/agent-sops/qa-agent-sop.md` (QA Quincy)

**Binding precedents (LA-1..LA-10, not re-litigated):** LA-3 `HISTORY_ZOOM_EPISODES` canonical; LA-4 Evan owns `observed_direction` post-tournament; LA-5 standards.md batch update Lead-owned; LA-6 GATE-CL family registered under GATE prefix.

**Focus areas:** schema contract mismatches, severity asymmetry, cross-ref integrity, vocabulary drift, bypass-page handoff.

---

## Section 1 — Data Dana

### P3-DANA-01 — `display_name_registry.csv` Path Contract Mismatch  
**Rule(s):** DATA-D13 (Dana SOP), APP-RL1 / APP-DL1 (Ace SOP)  
**Problem:** Dana SOP §6 Rule DATA-D13 declares `data/display_name_registry.csv` as "single source of truth for all chart labels across all deliveries. Vera and Ace consume it directly." Ace SOP Rule APP-RL1 says Ace maintains a "single-source label map" for display names. The two rules name different sources without distinguishing between them — one declares Dana's CSV as the master, the other implies Ace owns the rendering-time label resolution. If Ace's `APP-RL1` map deviates from Dana's registry row for a column (e.g., stale copy, local override for a pair_config), the contract is broken with no gate to detect the drift. The DATA-D13 bootstrap requirement mandates "sidecar `display_name` must match the registry verbatim (case-sensitive)" but the consumer-side rule (APP-RL1) sets no equivalent cross-validation step.  
**Severity:** WARN  
**Who must fix:** Dana (add cross-reference to APP-RL1 in DATA-D13, noting Ace's consumption mode) + Ace (add cross-validation step in APP-RL1 noting it must read from `data/display_name_registry.csv` as the primary source; local overrides require a regression_note).

### P3-DANA-02 — `observed_direction` "Do Not Write" Clause Missing (LA-4 Compliance)  
**Rule(s):** DATA-D6 (Dana SOP), DATA-D6 `owner_writes` field  
**Problem:** Lead arbitration LA-4 is binding: "Dana leaves it absent at data-stage handoff." The Data SOP DATA-D6 Procedure Step 1 says "Before writing the JSON, confirm the field you intend to set is listed under your agent in `owner_writes`." The `owner_writes` schema map currently has `observed_direction` unresolved in Dana's SOP (Dana's Phase-1 finding F-06 flagged this as a gap). The SOP does NOT contain an explicit "Dana MUST NOT write `observed_direction`" rule. A new Dana dispatch who reads only the SOP (not the changelog or LA-4) has no clear instruction to leave the field absent. The schema's `owner_writes` is the deterministic gate — but until the schema lists `observed_direction` under Evan's ownership (and explicitly not Dana's), the SOP does not encode LA-4.  
**Severity:** FAIL — active production risk (a new Dana could silently write a stale direction that conflicts with Evan's post-tournament value)  
**Who must fix:** Dana (add explicit "do NOT write `observed_direction`" note in DATA-D6 procedure step 1, per LA-4) + Evan (ensure `owner_writes` in `interpretation_metadata.schema.json` attributes `observed_direction` to Evan, not Dana).

### P3-DANA-03 — `interpretation_metadata.json` Merge Order Not Enforced at Ace's Consumer End  
**Rule(s):** DATA-D6 (Dana SOP), APP-WS1 (Ace SOP — analog for `winner_summary.json`)  
**Problem:** DATA-D6 says the merge order is "dana → evan → ray" and notes that Ray writes last. Ace's SOP (APP-WS1) mandates schema validation of `winner_summary.json` on load, but does NOT mention `interpretation_metadata.json` validation or ordering. Ace's landing-card loader (`pair_registry.py`) reads `interpretation_metadata.json` at render time. If Evan or Ray has written a schema-invalid field after Dana's initial write (race condition, schema version mismatch), Ace's loader encounters the corruption with no APP-SEV1 banner contract — it is not governed by APP-WS1. This is a consumer gap: Ace reads `interpretation_metadata.json` but has no schema validation gate for it analogous to APP-WS1.  
**Severity:** WARN  
**Who must fix:** Ace (add a consumer-side schema validation call for `interpretation_metadata.json` in the landing-card loader, analogous to APP-WS1 for `winner_summary.json`; emit APP-SEV1 L1 banner on validation failure; cross-reference DATA-D6).

### P3-DANA-04 — DATA-D6b "Human-Readable Names" Rule Scope vs. APP-RL1 "No Raw Column Names" Rule  
**Rule(s):** DATA-D6b (Dana SOP), APP-RL1 (Ace SOP)  
**Problem:** DATA-D6b (added 2026-04-22) says "Every `interpretation_metadata.json` field that renders in the portal's landing card, Story page, or Strategy page MUST use human-readable names." APP-RL1 prohibits raw column identifiers in user-facing text. The two rules overlap for the `key_finding` and `mechanism` fields. DATA-D6b mandates a producer-side lint grep (Dana, before handoff). APP-RL1 mandates Ace enforces at render time. The SOPs do not cross-reference each other, leaving an implicit assumption that one will catch what the other misses. If DATA-D6b lint passes but Ace's render inserts a raw column name from a non-`key_finding` field (e.g., from `callout_text` authored by Evan, which is NOT in DATA-D6b's scope), no gate catches it. The two rules have different scope — DATA-D6b covers Dana-owned fields; `callout_text` is Evan-owned.  
**Severity:** WARN  
**Who must fix:** Ace (add cross-reference from APP-RL1 to DATA-D6b; clarify that APP-RL1 lint must cover Evan-authored `callout_text` field in addition to Dana-authored `key_finding`). Evan (add DATA-D6b equivalent for `callout_text` — verify no raw column identifiers before handoff).

### P3-DANA-05 — Indicator Evaluation Framework "Supply AppDev Agent" Statement Has No Ace-Side Rule  
**Rule(s):** Dana SOP §Indicator Evaluation Framework  
**Problem:** Dana SOP §Indicator Evaluation Framework says "Supply AppDev Agent with fully validated datasets" for `environment_interaction_scores.json` and `strategy_survival_scores.json`. The Ace SOP has no corresponding consumption rule for these files — no APP-xxx rule names them, no GATE-CL item checks for them, and no quality gate verifies their presence. If Dana delivers these files and Ace does not consume them, the delivery is silent waste. Conversely, if Ace depends on them for a feature (radar chart, environment bar) and Dana does not deliver, the feature silently shows N/A with no blocker.  
**Severity:** WARN  
**Who must fix:** Ace (add a rule or GATE-CL item documenting what Ace does with these files; if they feed a portal component, the component must have an APP-SEV1 L2 banner fallback when absent). Dana (add cross-reference pointer to whatever Ace rule governs their consumption, once Ace defines it).

---

## Section 2 — Econ Evan

### P3-EVAN-01 — `winner_summary.json` Schema Version Stale (ECON-H5 vs. Live Schema)  
**Rule(s):** ECON-H5 (Evan SOP), APP-WS1 (Ace SOP)  
**Problem:** ECON-H5 in the Evan SOP declares the schema as "version 1.0.0". Lead Phase 2 finding A1 (citing Evan F-05) notes "live schema is v1.1.0." APP-WS1 in Ace's SOP cites the schema but does not pin a version. If Evan's SOP still says v1.0.0 and the live schema is v1.1.0, a new Evan dispatch will produce against the older spec and the `validate_or_die` call (APP-WS1 gate) will catch the mismatch at render time — but Evan will not know about the schema bump from reading his SOP. The SOP reference is stale regardless of LA-10's instruction to fix the text in Phase 4. The consumer (Ace) is at risk of `validate_or_die` FAILs whenever Evan produces without knowing about the version bump.  
**Severity:** FAIL — Evan SOP points to a superseded schema version; any Evan dispatch producing to v1.0.0 spec will fail APP-WS1 gate on Ace's side  
**Who must fix:** Evan (update ECON-H5 schema version reference from v1.0.0 to v1.1.0 in Phase 4; add a note about the schema-bump propagation protocol per LA-8 / META-SBP).

### P3-EVAN-02 — `interpretation_metadata.json` `direction` Field Name Conflict: ECON-DIR1 vs. APP-DIR1  
**Rule(s):** ECON-DIR1 (Evan SOP), APP-DIR1 (Ace SOP)  
**Problem:** Evan's SOP `interpretation_metadata.json` schema example shows field `"observed_direction"`. APP-DIR1 says Ace verifies by reading `interpretation_metadata.observed_direction`. LA-4 confirms Evan owns this field post-tournament. However, Evan's SOP also mentions `direction_consistent` and `direction_confidence` as sibling fields. The Ace SOP (APP-DIR1 direction triangulation) cross-references `winner_summary.json.direction` and `interpretation_metadata.json.observed_direction` and `narrative_frontmatter.direction_asserted`. The Evan SOP has no explicit statement that `winner_summary.json.direction` and `interpretation_metadata.json.observed_direction` MUST be the same value. If Evan produces a `winner_summary.json` with `direction: "countercyclical"` but `interpretation_metadata.json` with `observed_direction: "mixed"` (because the tournament result was ambiguous), APP-DIR1 triangulation (Quincy GATE) fires a mismatch FAIL. Neither Evan's SOP nor Ace's SOP clarifies what happens when `direction_consistent = false` — is a triangulation mismatch expected and documented, or a bug?  
**Severity:** WARN  
**Who must fix:** Evan (add a clarifying note to ECON-DIR2 alignment gate: when `direction_consistent = false`, `winner_summary.json.direction` is still written and equals the observed dominant direction; `interpretation_metadata.observed_direction` matches it; the `direction_consistent = false` flag documents the gap between prior and observed, not a mismatch in the two artifacts). Ace (APP-DIR1 should state: direction triangulation FAIL is only a hard block when `winner_summary.direction` ≠ `interpretation_metadata.observed_direction` after accounting for `direction_consistent = false` documentation).

### P3-EVAN-03 — `callout_text` Field: Evan-Authored but No DATA-D6b Equivalent  
**Rule(s):** ECON-H5 `interpretation_metadata` fields (Evan SOP), APP-LP8 (Ace SOP)  
**Problem:** Evan's SOP says `callout_text` "is written by Evan as the domain expert... Ace renders it directly without interpretation." This is a user-facing field (renders in the portal's 'How to Read This' callout box). DATA-D6b (Dana SOP) mandates a lint on user-facing text fields for raw column identifiers. DATA-D6b's scope is Dana-owned fields. `callout_text` is Evan-owned. The Evan SOP has no DATA-D6b-equivalent rule requiring Evan to scan `callout_text` for raw column identifiers (e.g., `hmm_2state_prob_stress`, `spy_fwd_63d`) before handoff. Since APP-RL1 (Ace's label-consistency rule) operates at render time, and Ace "renders directly without interpretation," the lint chain for `callout_text` is broken: Dana doesn't lint it (not her field), Evan doesn't lint it (no rule), Ace doesn't modify it (renders directly), and GATE-NR only checks Story/Evidence DOM for wrong-pair instrument names, not for raw column identifier leakage.  
**Severity:** WARN  
**Who must fix:** Evan (add a pre-handoff lint step for `callout_text`: grep for `[a-z_]+_(pct|bps|yoy|fwd_\d+d|prob_[a-z]+|zscore)\b` pattern, rewrite to plain-English equivalents; cross-reference DATA-D6b as the model).

### P3-EVAN-04 — ECON-FE1 Evidence-Status Semantics vs. APP-LP8 Status Display  
**Rule(s):** ECON-FE1 (Evan SOP), APP-LP8 (Ace SOP)  
**Problem:** ECON-FE1 defines three status values: `found_in_search`, `needs_final_exam`, `passed_final_exam`. APP-LP8 defines three matching display labels and "evidence-status badge" rendering. The severity of a "badge mismatch" (e.g., Ace displays `found_in_search` when `evidence_status.json` says `needs_final_exam`) is never specified in either SOP. APP-SEV1 governs Ace's banner/severity system (L1/L2/L3), but APP-LP8 does not cross-reference APP-SEV1 for the case where the evidence_status.json value is inconsistent with the winning strategy's artifact state. Quincy's GATE-ES1 checks schema validity and DOM render, but GATE-ES1 does not specify whether a DOM mismatch is a GATE-ES1 FAIL or an APP-SEV1 L1 banner. The severity path is undefined.  
**Severity:** WARN  
**Who must fix:** Ace (clarify in APP-LP8: if `evidence_status.json` value does not match the displayed badge, it is an APP-SEV1 L1 render failure, block with banner; cross-reference GATE-ES1 as the QA gate). Evan (clarify in ECON-FE1: a schema-valid `evidence_status.json` that contradicts `winner_summary.json` artifact state should be flagged to Lead before handoff, not left for Quincy to catch).

### P3-EVAN-05 — APP-WS1 Schema Failure Escalation vs. ECON-H5 Delivery Responsibility  
**Rule(s):** APP-WS1 (Ace SOP), ECON-H5 (Evan SOP)  
**Problem:** APP-WS1 says Ace MUST file a blocker in `_pws/_team/status-board.md` when `validate_or_die` fails on a delivered (non-WIP) pair's `winner_summary.json`. ECON-H5 says Evan's producer-side validation is a "blocking gate" before handoff. If both gates are respected, a schema-invalid `winner_summary.json` should never reach Ace. But the Evan SOP has no explicit statement of what happens if Evan's producer-side validation gate is skipped or missed (e.g., in an expedited pipeline). Ace's APP-WS1 escalation clause (from Ace's Phase-1 F-15 proposal) is the correct fallback — but the Evan SOP should mirror it with a reciprocal statement: "If Ace files a winner_summary schema blocker, Evan owns the fix within the same wave; silence is not an acceptable response."  
**Severity:** WARN  
**Who must fix:** Evan (add a rule in ECON-H5: "if APP-WS1 fires a schema blocker on a pair Evan delivered as completed, Evan treats it as a FAIL on ECON-H5's producer-side gate — rerun the producer-side validate_or_die, fix the schema violation at source, and deliver a corrected file in the same wave").

---

## Section 3 — Viz Vera

### P3-VERA-01 — `_meta.json` Sidecar Contract: Ace's Loader vs. Vera's Mandatory Fields  
**Rule(s):** VIZ-O1, VIZ-E1 (Vera SOP); APP-PT1, ACE-HZE1 (Ace SOP)  
**Problem:** VIZ-O1 mandates a `{chart_name}_meta.json` sidecar for every chart with `disposition`, `title`, `caption`, `source`, `source_sample_period`, `data_source_path`, and `rules_applied`. VIZ-E1 adds `narrative_alignment_note`, `vera_rationale`, `canonical_consumption`, and `portal_page_hint` for exploratory charts. Ace's SOP (APP-PT1) reads chart files via `load_plotly_chart(name, pair_id)`. There is no Ace-side rule specifying which `_meta.json` fields Ace consumes, which it ignores, and what Ace does when a mandatory field is absent. If Vera ships a `consumed` chart with a missing `caption` in `_meta.json` (e.g., as a fallback because Ray's narrative dict is absent), Rule A5 says Ace uses Vera's `_meta.json` caption as fallback — but APP-PT1/Rule A5 is described in the Vera SOP, not in Ace's SOP. Ace has no mirrored rule that says "if Ray's narrative caption is absent, use Vera's `_meta.json` caption." This means Ace may silently render a chart without any caption, with no APP-SEV1 banner.  
**Severity:** WARN  
**Who must fix:** Ace (add a caption-fallback rule in the portal chart-rendering logic: if Ray's narrative dict `caption` for a given chart_type is absent or empty, use Vera's `_meta.json` `caption` as fallback; if both are absent, emit APP-SEV1 L3 caption noting "chart caption pending." Cross-reference Vera's Rule A5). 

### P3-VERA-02 — Episode Slug Used in ACE-HZE1 vs. VIZ-ZOOM1 vs. RES-HZE1: Three Slug Sources  
**Rule(s):** ACE-HZE1 (Ace SOP), VIZ-ZOOM1 (Vera SOP), RES-HZE1 (Ray SOP)  
**Problem:** LA-3 (binding) declares `HISTORY_ZOOM_EPISODES` canonical. LA-1/LA-2 declare `history_zoom_events_registry.json` the canonical episode registry with slug set `dotcom, gfc, covid, taper_2018, inflation_2022`. ACE-HZE1 says Ace pre-ship checks episodes from the pair config `HISTORY_ZOOM_EPISODES`. VIZ-ZOOM1 says Vera reads slugs from `docs/schemas/episode_registry.json` keyed on `indicator_category`. RES-HZE1 says Ray validates slugs against `docs/schemas/episode_registry.json`. GATE-VIZ-NBER2 in Quincy's SOP has a hardcoded slug table that includes `dot_com` (not `dotcom`) and `rates_2022` (not `inflation_2022`). After LA-1/LA-2, VIZ-ZOOM1 still uses the old slug set in its per-pair status table (`dotcom` ✓ and `inflation_2022` in the required episodes list), which is correct. But GATE-VIZ-NBER2's hardcoded table includes `dot_com` and `rates_2022` — old non-canonical slugs. This means GATE-VIZ-NBER2 will attempt to classify a `history_zoom_dotcom.json` file with slug `dotcom` against an episode table that keys on `dot_com` and may silently misclassify it. **This directly affects Ace** because ACE-HZE1's pre-ship check would pass (canonical slug `dotcom`) while Quincy's GATE-VIZ-NBER2 operates on different slug names. The two gates can disagree on the same artifact.  
**Severity:** FAIL — slug namespace discrepancy between ACE-HZE1 pre-ship gate and GATE-VIZ-NBER2 will cause silent false-PASSes or false-FAILs in the handoff chain  
**Who must fix:** Quincy (fix GATE-VIZ-NBER2 episode table to use canonical slugs per LA-2: `dotcom` not `dot_com`, `inflation_2022` not `rates_2022`). Vera (confirm VIZ-ZOOM1 per-pair status table uses canonical slugs; the table in the SOP already uses `inflation_2022` which is correct, but the `dotcom` in VIZ-ZOOM1 is also correct — confirm VIZ-ZOOM1 is already aligned with LA-2). Ace (no fix needed — ACE-HZE1 reads from `HISTORY_ZOOM_EPISODES` config which Ray writes; Ray uses episode_registry.json post-LA-1; the chain is correct IF Quincy aligns GATE-VIZ-NBER2).

### P3-VERA-03 — VIZ-HZE1 Skip Protocol: Ace's GATE-25 Placeholder vs. Vera's Skip Entry  
**Rule(s):** VIZ-HZE1 (Vera SOP), APP-EP4 / GATE-25 (Ace SOP)  
**Problem:** VIZ-HZE1 defines a skip protocol when pair data does not cover an episode: Vera adds `history_zoom_{slug}_skip` entry to `output/charts/{pair_id}/plotly/_meta.json`. This skip entry is Vera-side. Ace's GATE-25 / APP-EP4 defines a placeholder behavior for missing charts. The two protocols cover overlapping failure modes (chart not built due to data coverage gap) but have different trigger sources: Vera's skip is a pre-handoff annotation; Ace's placeholder fires at render time when `load_plotly_chart` returns None. There is no rule that explicitly connects the two: if Vera has written a skip entry but ACE-HZE1 fires a pre-ship check and finds a missing slug chart, should Ace consult `_meta.json` for the skip entry before filing a GATE-HZE1 blocker? ACE-HZE1 Step 3 says "list disk artifacts" — it does NOT say "check `_meta.json` for skip entries." Without this connection, Ace may file a false blocker against Vera for a legitimately skipped episode.  
**Severity:** WARN  
**Who must fix:** Ace (add to ACE-HZE1 Step 3: "Before filing a VIZ-HZE1 blocker for a missing slug, check `output/charts/{pair_id}/plotly/_meta.json` for a `history_zoom_{slug}_skip` entry per VIZ-HZE1's skip protocol. If a skip entry is present with a documented reason, do NOT file a blocker — record the skip in the pre-ship log and proceed.").

### P3-VERA-04 — VIZ-DP1 Scope Claim vs. Ace's `load_plotly_chart` Consumer  
**Rule(s):** VIZ-DP1 (Vera SOP), APP-PT1 / load_plotly_chart (Ace SOP)  
**Problem:** VIZ-DP1 is "BLOCKING — no Vera handoff proceeds until axis-assignment check returns PASS." The producer-side gate is thorough. However, Ace's `load_plotly_chart` function loads chart JSON and passes the Plotly figure to Streamlit for rendering. If a chart passes VIZ-DP1 at Vera's handoff time but is later modified (e.g., a hot-fix commit where Vera regenerates the chart) without re-running VIZ-DP1, Ace renders the broken bottom panel with no detection. Ace's SOP has no consumer-side axis-assignment check. The assumption is VIZ-DP1 is enforced once and is thereafter stable. This is fragile — GATE-DP1 (Quincy) runs as a JSON preflight before each cloud verify, providing a second line of defense. But between Vera's commit and Quincy's verify, Ace may have triggered a deploy.  
**Severity:** INFO  
**Who must fix:** Ace (no SOP change needed, but add a session-note to watch for GATE-DP1 failures in Quincy's findings before signing off on any story page. If GATE-DP1 finds a failure in a pair Ace just wired, Ace owns the deployment coordination). The two-gate chain (VIZ-DP1 at handoff + GATE-DP1 at verify) is architecturally correct; the concern is documentation only.

### P3-VERA-05 — Vera SOP Rule VIZ-IC1: Referenced by VIZ-CP1 but Not Defined in SOP  
**Rule(s):** VIZ-IC1 (Vera SOP), VIZ-CP1 (Vera SOP)  
**Problem:** VIZ-CP1 ends with "VIZ-IC1 lint applies: All CP charts undergo the standard intra-chart consistency check before save." VIZ-IC1 is referenced as if it is a defined rule in the Vera SOP. The Vera SOP Phase-1 report (status board) identified "VIZ-IC1 unregistered in standards.md, dangling cross-references (META-RYW, QA-CL6, GATE-NC)." The rule text for VIZ-IC1 does not appear in the Vera SOP. From Ace's perspective: CP charts consume VIZ-IC1 lint output, but the rule that governs what VIZ-IC1 actually checks is undefined. If VIZ-IC1 is a pre-save axis/unit consistency check, Ace cannot know what constitutes VIZ-IC1 compliance without reading the rule text. This is directly relevant because Ace may need to verify at portal-lint time (APP-ST1) that a CP chart is VIZ-IC1 compliant.  
**Severity:** WARN  
**Who must fix:** Vera (define VIZ-IC1 rule text in the Vera SOP in Phase 4; register in standards.md per LA-5). Ace (once VIZ-IC1 is defined, evaluate whether APP-ST1 portal lint needs to mirror any of its checks at the consumer side).

---

## Section 4 — Research Ray

### P3-RAY-01 — RES-HZE1 Slug Source: `episode_registry.json` vs. `history_zoom_events_registry.json` (LA-1 Compliance)  
**Rule(s):** RES-HZE1 (Ray SOP), LA-1 (binding)  
**Problem:** LA-1 declares `docs/schemas/history_zoom_events_registry.json` canonical. LA-2 says `episode_registry.json` is deprecated. RES-HZE1 Step 1 says: "Open `docs/schemas/episode_registry.json`. Look up the pair's `indicator_category`." Step 1 still points to the deprecated registry. The "slug matching procedure" in RES-HZE1 explicitly references `episode_registry.json` five times. After LA-1, Ray is supposed to produce `HISTORY_ZOOM_EPISODES` with slugs sourced from `history_zoom_events_registry.json`, not `episode_registry.json`. If Ray follows the SOP literally, he uses the deprecated registry and may produce non-canonical slugs (e.g., `dot_com` instead of `dotcom`). Ace's ACE-HZE1 pre-ship step then fires a mismatch against the chart files which Vera generates using the canonical registry. The entire handoff chain breaks.  
**Severity:** FAIL — this is the most critical handoff gap in Phase 3. Ray's SOP (RES-HZE1) still points to the deprecated `episode_registry.json` which LA-1 retires. Any Ray dispatch following the SOP will produce non-canonical slugs and break ACE-HZE1 and VIZ-HZE1.  
**Who must fix:** Ray (update RES-HZE1 slug matching procedure to reference `history_zoom_events_registry.json` per LA-1; update all five occurrences of `episode_registry.json` in RES-HZE1). This is Phase 4 priority FAIL.

### P3-RAY-02 — `direction_asserted` Frontmatter Field vs. APP-DIR1 Enum Vocabulary  
**Rule(s):** RES-17 (Ray SOP), APP-DIR1 (Ace SOP)  
**Problem:** RES-17 declares `direction_asserted` in the narrative frontmatter as "one of `procyclical` / `countercyclical` / `mixed`, MUST match Evan's `winner_summary.json.direction`." APP-DIR1 (Ace's rule) cross-references the same field. The `winner_summary.json` `direction` field vocabulary is `procyclical | countercyclical | mixed` (per ECON-H5 in Evan's SOP). These are aligned. However, Ray's broader SOP includes direction states `ambiguous` and `conditional` in the 6d Direction Determination workflow and in the research brief `expected_direction` field. The frontmatter `direction_asserted` specifically prohibits `ambiguous` and `conditional` (only the three canonical values are allowed). But the Ray SOP does not explicitly state that `direction_asserted` cannot be `ambiguous` or `conditional` — it only says "one of `procyclical` / `countercyclical` / `mixed`." A new Ray reading the 6d workflow might try to write `direction_asserted: "conditional"` and fail the frontmatter schema validation without a clear SOP cross-reference explaining why `conditional` is not permitted in frontmatter even though it is used elsewhere.  
**Severity:** WARN  
**Who must fix:** Ray (add a note in RES-17 cross-referencing the 6d workflow: "The three frontmatter values `procyclical/countercyclical/mixed` are the rendered enum. `ambiguous` and `conditional` from the 6b/6d workflows are research-stage labels that Evan collapses to the canonical enum before writing `winner_summary.json`; `direction_asserted` reflects the post-collapse value only.").

### P3-RAY-03 — APP-PT1 Narrative Authorship Supplement vs. RES-NR1 Rule: Ownership Overlap  
**Rule(s):** APP-PT1 (Ace SOP — narrative authorship supplement), RES-NR1 (Ray SOP)  
**Problem:** Ace's APP-PT1 contains a "narrative authorship supplement" that states "Ray owns all user-facing narrative prose on Story, Evidence, Strategy, and Methodology pages. Ace renders and structures; Ace does NOT author narrative." RES-NR1 (Ray SOP) independently states the same ownership rule. Two separate rules in two separate SOPs declare the same constraint. This is not a contradiction — it is vocabulary duplication. The risk: if one SOP updates the rule (e.g., adds a new exception where Ace may write placeholder narrative for a new template section), the other SOP does not automatically update. Phase-1 F-16 (Ace) raises the "legacy bypass page" gap where hand-written Methodology pages (not using the template) contain Ace-authored structure without Ray-authored narrative. APP-PT1's narrative authorship supplement does not address this legacy exception. RES-NR1 says "Any narrative text in `app/pair_configs/{pair_id}_config.py` must have been written or reviewed by Ray for that specific pair" — but the legacy pages are not pair_configs, they are direct `app/pages/` files.  
**Severity:** WARN  
**Who must fix:** Ace (add a note in APP-PT1 narrative authorship supplement: "Legacy hand-written pages (bypass pages per F-16) may contain Ace-authored structure in the absence of a pair_config; such pages are queued for APP-PT1 migration. Until migration, any narrative text in the bypass page must still be Ray-reviewed." Cross-reference RES-NR1). Ray (add a note in RES-NR1: "Narrative review applies to pair_config files AND to any hand-written page file that exposes user-facing text on a delivered portal page.").

### P3-RAY-04 — RES-HZE1 Pre-Handoff Validation Checks vs. ACE-HZE1 Acceptance Criteria: Gap in `narrative` Field Verification  
**Rule(s):** RES-HZE1 (Ray SOP), ACE-HZE1 (Ace SOP)  
**Problem:** RES-HZE1 pre-handoff validation step 3 says: "Each `narrative` field is 1–2 sentences and contains no hand-typed metric values — cite the behavior pattern, not a precise Sharpe or date that might drift. Verifiable data points (e.g., spread level, SPY drawdown %) are acceptable only if they are auditable in a result CSV." ACE-HZE1 pre-ship step 1 says "read Ray's handoff note for each episode; confirm `slug`, `title`, `narrative`, `caption` fields are present." Ace's pre-ship check verifies presence of the `narrative` field but does NOT verify that the narrative is semantically valid per RES-HZE1's constraints (no hand-typed metrics, etc.). If Ray delivers a `narrative` containing a hand-typed Sharpe ratio that later drifts with a rerun, Ace's ACE-HZE1 step 1 passes, and the drift goes undetected until the next Ray rerun. The RES-HZE1 producer-side constraint and ACE-HZE1 consumer-side check are not aligned in depth.  
**Severity:** INFO (the mismatch is a quality concern, not a structural failure — the portal will render the stale metric, not crash)  
**Who must fix:** Ace (ACE-HZE1 Step 1 can add a lightweight check: flag any `narrative` that contains a numeric pattern `\d+\.\d+` or `\d+%` that is NOT a pair/episode slug or date — this is the class of hand-typed metrics RES-HZE1 prohibits. Emit APP-SEV1 L3 caption if found, do not block render). This is optional hardening.

### P3-RAY-05 — "Thin Wrapper" Vocabulary Used in Ray's RES-NR1 Context vs. Ace's APP-PT1 Definition  
**Rule(s):** RES-NR1 (Ray SOP), APP-PT1 (Ace SOP)  
**Problem:** APP-PT1 uses "thin wrapper" as a key concept (Ace's Phase-1 F-02 noted this is undefined formally in Ace's SOP). The Ray SOP (RES-NR1) says narrative text in `app/pair_configs/{pair_id}_config.py` must be Ray-reviewed — but does not use the term "thin wrapper" anywhere. "Thin wrapper" is Ace's vocabulary for the `pages/*.py` files; the Ray SOP refers to pair_config files instead. When Ray authors narrative for a thin-wrapper pair page (where `pair_configs/{pair_id}_config.py` is the content source and the `pages/` file is the thin wrapper that calls the template), the narrative lives in the `pair_configs/` file. RES-NR1's scope says "pair_config" — this is correct. But the Ace SOP APP-PT1 migration protocol says "pair pages" — referring to the `pages/*.py` wrapper. A new Ray unfamiliar with the architecture may not know the two-file structure and may mistakenly write narrative directly in the `pages/*.py` file (the thin wrapper) rather than in `pair_configs/`.  
**Severity:** INFO  
**Who must fix:** Ray (add a note in RES-NR1: "narrative prose lives in `app/pair_configs/{pair_id}_config.py`; the matching `app/pages/*.py` file is a thin-wrapper that renders the config — do not author narrative in the pages file."). Ace (add a cross-reference from APP-PT1 to RES-NR1 clarifying the same).

---

## Section 5 — QA Quincy

### P3-QUINCY-01 — GATE-HZE1 Implementation Owner: Ambiguity Between Ace Fix and Vera WARN  
**Rule(s):** GATE-HZE1 (Quincy SOP), ACE-HZE1 (Ace SOP)  
**Problem:** GATE-HZE1 defines two failure dispositions: FAIL (heading absent + zoom charts committed → "Ace bug") and WARN (heading absent + no zoom charts → "Vera blocker"). However, the WARN→FAIL transition rule says "The WARN converts to FAIL automatically once `history_zoom_*.json` charts are committed." The automation is declarative — no script enforces the WARN→FAIL flip. If Vera commits zoom charts but the WARN in `results.json` from a prior cloud_verify run is not re-run, the WARN persists indefinitely in old result artifacts. More critically: GATE-HZE1's FAIL disposition says owner is Ace ("wire `HISTORY_ZOOM_EPISODES` into pair config"). But the root cause of the gap could also be Ray not providing `HISTORY_ZOOM_EPISODES` in the config handoff (violating RES-HZE1). If Quincy files the FAIL against Ace, Ace may discover that Ray's handoff note omitted the `HISTORY_ZOOM_EPISODES` block — then Ace has to redirect the blocker to Ray, adding a round-trip. GATE-HZE1 does not instruct Quincy to check whether Ray's handoff note included `HISTORY_ZOOM_EPISODES` before assigning ownership to Ace.  
**Severity:** WARN  
**Who must fix:** Quincy (add a diagnostic step to GATE-HZE1 FAIL disposition: "Before assigning ownership to Ace, verify that Ray's config handoff note included `HISTORY_ZOOM_EPISODES`. If absent, the blocker owner is Ray (RES-HZE1 violation), not Ace."). This eliminates the misdirected-blocker round-trip.

### P3-QUINCY-02 — GATE-31 Acceptance Contract: Defined in Quincy's SOP but Referenced as a Gate by Ace and Evan  
**Rule(s):** GATE-31 (Quincy SOP, QA-CL2 section), APP-ST1 / APP-WS1 (Ace SOP)  
**Problem:** Ace's Phase-1 F-18 (APP-ST1 scope limitation) says "Cloud verify (Quincy, GATE-31) is the only gate that catches render-path failures." GATE-31 is referenced in the Ace SOP as the QA gate that complements portal lint. However, the Quincy SOP does not have an explicit "GATE-31" section — GATE-31 appears as a cross-reference in QA-CL2 ("A QA-CL2 FAIL is a GATE-31 FAIL") and in other QA rules, but never as a standalone definition. From Ace's perspective, GATE-31 is a known entity that Quincy owns. From the Quincy SOP, GATE-31 is referenced but never formally defined with its own rule body (name, condition, pass/fail criteria, owner). This is a standards-registration gap: GATE-31 appears in standards.md per the QA section (to be confirmed in Phase 4 batch update), but the Quincy SOP itself does not have a Rule GATE-31 block, only QA-CL2/4 sections that reference it obliquely. Any reader trying to find the GATE-31 acceptance contract definition in the Quincy SOP cannot — it is spread across QA-CL2 and cross-references.  
**Severity:** WARN  
**Who must fix:** Quincy (add a formal "GATE-31 — Acceptance Contract (cloud verify PASS required)" rule block in Phase 4 that aggregates all GATE-31 triggering conditions from QA-CL2/4; cross-reference as the complement of APP-ST1 per Ace's F-18).

### P3-QUINCY-03 — GATE-CL Family Ownership vs. GATE Prefix (LA-6 Compliance)  
**Rule(s):** GATE-CL1–8 (listed in Ace SOP, binding), LA-6 (binding)  
**Problem:** LA-6 declares: "GATE-CL family (CL1–CL8) is registered under the GATE prefix in `docs/standards.md` (gates are GATE-owned regardless of authoring agent)." The Quincy SOP's QA checklist (QA-CL1) contains checks like "GATE-27, GATE-28, GATE-29" as QA-owned gates. The GATE-CL family is authored by Ace but now registered under the GATE prefix. The Quincy SOP has no mention of GATE-CL1–CL8 in its QA-CL1 checklist or in QA-CL4. This means Quincy does not formally own verification of the GATE-CL family, even though they are now GATE-prefix rules. The question of verification ownership is undefined: Ace self-checks (the GATE-CL items are in the AppDev SOP Quality Gates checklist), but Quincy does not independently verify them as GATE-owned rules. If GATE-CL rules are in the GATE namespace, Quincy should at minimum verify them in the wave QA cycle.  
**Severity:** WARN  
**Who must fix:** Quincy (add GATE-CL1–8 to QA-CL1 checklist as items Quincy verifies: "GATE-CL1–8 — content audit items authored by Ace, verified by Quincy as GATE-prefix rules; check that Ace's GATE-CL pre-ship log covers all 8 items for the current pair."). Ace (clarify in the GATE-CL family: Ace runs the gate at pre-ship time; Quincy independently verifies at QA time. The GATE-CL audit script `gate_cl_audit.py` (Wave 10K plan) should emit results Quincy can consume).

### P3-QUINCY-04 — GATE-NR DOM Scan: "Raw Column Identifiers" Scope Excludes `callout_text` Field  
**Rule(s):** GATE-NR / QA-CL5 (Quincy SOP), DATA-D6b (Dana SOP)  
**Problem:** GATE-NR / QA-CL5 checks "all instrument references in Story and Evidence DOM text" for wrong-pair instrument names. DATA-D6b extends GATE-NR to check for raw column identifiers in landing-card text (added 2026-04-22). However, Evan's `callout_text` field renders in the portal's 'How to Read This' callout box on the Story page — this is on the Story page DOM but is Evan-authored, not Dana-authored. DATA-D6b's producer-side lint scope covers Dana-owned fields. GATE-NR/QA-CL5's DOM scan looks for "wrong-pair instrument names" — it is not stated as also checking for raw column identifier tokens. The two scopes (wrong instruments vs. raw column names) address different problems and are checked by different rules. If Evan's `callout_text` contains `hmm_2state_prob_stress` as a rendered token, neither GATE-NR (wrong instrument scope) nor DATA-D6b (Dana-field scope) catches it in the DOM. The gap is a Story-page raw-column-identifier check for Evan-authored fields.  
**Severity:** WARN  
**Who must fix:** Quincy (extend QA-CL5 / GATE-NR DOM scan to include a raw-column-identifier pattern check: grep rendered Story DOM text for `[a-z_]+_(pct|bps|yoy|fwd_\d+d|prob_[a-z]+|zscore)\b` in addition to the wrong-instrument check. Flag hits as PASS-with-note unless the pattern appears in a technically-oriented section like Methodology). Cross-reference DATA-D6b and the Evan SOP's `callout_text` field.

### P3-QUINCY-05 — Severity Mapping Asymmetry: Ace L1/L2/L3 vs. Quincy PASS/PASS-with-note/FAIL  
**Rule(s):** APP-SEV1 (Ace SOP), GATE-CL1 (Ace SOP Quality Gates), Quincy Findings Format (Quincy SOP)  
**Problem:** Ace raises three severity levels: L1 (Loud-Error, blocks page render), L2 (Loud-Warning, non-blocking banner), L3 (Caption-Note, informational). Quincy reports: PASS, PASS-with-note, FAIL. These are two independent systems with no declared mapping. When Quincy reviews a page where Ace's APP-SEV1 L2 banner is visible, should Quincy record it as FAIL (user-facing warning present) or PASS-with-note (correct behavior, Ace rendering L2 as designed)? The Quincy SOP says "Zero occurrences of internal development diagnostics in user-facing DOM text" (GATE-28) — but L2 banners are intentional user-facing warnings, not internal diagnostics. A new Quincy might flag all L2 banners as GATE-28 violations. There is no cross-reference in either SOP explaining the mapping.  
**Severity:** WARN  
**Who must fix:** Quincy (add a mapping note in GATE-28: "APP-SEV1 L1 user-facing error banners: FAIL if they indicate a schema or data load failure on a delivered page; L2 warning banners: PASS-with-note if they are rendered by APP-SEV1 design (missing optional data); FAIL only if they expose internal SOP/ticket/agent-name text (GATE-CL1 prohibition). L3 captions: PASS." Cross-reference APP-SEV1). Ace (add cross-reference in APP-SEV1: "Quincy's GATE-28 treats L1 schema-failure banners on delivered pages as FAIL; L2 optional-data banners as PASS-with-note; L3 as PASS.").

---

## Summary Table

| # | Peer | Rule(s) | Problem class | Severity | Fix owner |
|---|------|---------|--------------|----------|-----------|
| P3-DANA-01 | Dana | DATA-D13, APP-RL1 | Schema contract mismatch — display name registry source | WARN | Dana + Ace |
| P3-DANA-02 | Dana | DATA-D6 | LA-4 not encoded in SOP — `observed_direction` no explicit "do not write" | FAIL | Dana + Evan |
| P3-DANA-03 | Dana | DATA-D6, APP-WS1 | Consumer gap — no `interpretation_metadata.json` schema validation at Ace's loader | WARN | Ace |
| P3-DANA-04 | Dana | DATA-D6b, APP-RL1 | Scope gap — `callout_text` (Evan-owned) not covered by Dana-D6b lint or APP-RL1 explicitly | WARN | Ace + Evan |
| P3-DANA-05 | Dana | §Indicator Evaluation Framework | No Ace-side rule for `environment_interaction_scores.json` / `strategy_survival_scores.json` | WARN | Ace + Dana |
| P3-EVAN-01 | Evan | ECON-H5, APP-WS1 | Schema version stale (v1.0.0 in SOP vs. v1.1.0 live) | FAIL | Evan |
| P3-EVAN-02 | Evan | ECON-DIR1/DIR2, APP-DIR1 | Direction mismatch semantics when `direction_consistent = false` undefined at triangulation | WARN | Evan + Ace |
| P3-EVAN-03 | Evan | ECON-H5, APP-RL1, DATA-D6b | `callout_text` has no human-readable name lint (Evan-authored user-facing field) | WARN | Evan |
| P3-EVAN-04 | Evan | ECON-FE1, APP-LP8, APP-SEV1 | Evidence-status badge mismatch severity path undefined | WARN | Ace + Evan |
| P3-EVAN-05 | Evan | ECON-H5, APP-WS1 | No reciprocal escalation clause in Evan SOP when Ace files APP-WS1 schema blocker | WARN | Evan |
| P3-VERA-01 | Vera | VIZ-O1, APP-PT1, Rule A5 | Caption fallback not mirrored in Ace SOP (Ace has no rule for using `_meta.json` caption as fallback) | WARN | Ace |
| P3-VERA-02 | Vera | ACE-HZE1, VIZ-ZOOM1, GATE-VIZ-NBER2 | Slug namespace — GATE-VIZ-NBER2 uses `dot_com`/`rates_2022` (non-canonical post LA-2) | FAIL | Quincy |
| P3-VERA-03 | Vera | VIZ-HZE1 skip, ACE-HZE1 | Skip protocol not connected — Ace may file false VIZ-HZE1 blocker for a legitimately skipped episode | WARN | Ace |
| P3-VERA-04 | Vera | VIZ-DP1, APP-PT1 | INFO: no consumer-side axis check; GATE-DP1 provides second-line defense adequately | INFO | No action |
| P3-VERA-05 | Vera | VIZ-IC1, VIZ-CP1 | VIZ-IC1 rule text undefined; CP charts reference it; Ace cannot know compliance criteria | WARN | Vera |
| P3-RAY-01 | Ray | RES-HZE1, LA-1 | CRITICAL: RES-HZE1 still points to deprecated `episode_registry.json` (LA-1 retires it) | FAIL | Ray |
| P3-RAY-02 | Ray | RES-17, APP-DIR1 | `direction_asserted` frontmatter vs. `ambiguous`/`conditional` in 6d workflow — no cross-reference | WARN | Ray |
| P3-RAY-03 | Ray | APP-PT1, RES-NR1 | Ownership duplication: same rule declared in two SOPs; legacy bypass pages not addressed by RES-NR1 | WARN | Ace + Ray |
| P3-RAY-04 | Ray | RES-HZE1, ACE-HZE1 | Narrative field depth verification gap: Ace checks presence, not semantic validity per RES-HZE1 | INFO | Ace (optional) |
| P3-RAY-05 | Ray | RES-NR1, APP-PT1 | "Thin wrapper" vocabulary absent from Ray SOP — Ray may author narrative in wrong file | INFO | Ray + Ace |
| P3-QUINCY-01 | Quincy | GATE-HZE1 | FAIL disposition assigns owner to Ace without first checking whether Ray omitted `HISTORY_ZOOM_EPISODES` | WARN | Quincy |
| P3-QUINCY-02 | Quincy | GATE-31, APP-ST1 | GATE-31 has no formal rule body in Quincy SOP; only referenced obliquely | WARN | Quincy |
| P3-QUINCY-03 | Quincy | GATE-CL1–8, LA-6, QA-CL1 | GATE-CL family now GATE-prefix per LA-6 but absent from Quincy's QA-CL1 checklist | WARN | Quincy + Ace |
| P3-QUINCY-04 | Quincy | GATE-NR/QA-CL5, DATA-D6b | DOM scan does not cover raw column identifier tokens (only wrong instruments) | WARN | Quincy |
| P3-QUINCY-05 | Quincy | APP-SEV1, GATE-28 | Severity mapping undefined: Ace L1/L2/L3 vs. Quincy PASS/PASS-with-note/FAIL | WARN | Quincy + Ace |

---

## Findings Count by Peer

| Peer | FAIL | WARN | INFO | Total |
|------|------|------|------|-------|
| Dana | 1 | 4 | 0 | 5 |
| Evan | 1 | 4 | 0 | 5 |
| Vera | 1 | 3 | 1 | 5 |
| Ray | 1 | 2 | 2 | 5 |
| Quincy | 0 | 4 | 1 | 5 |
| **Total** | **4** | **17** | **4** | **25** |

---

## Top-3 Themes Across Peers

1. **LA-1/LA-2 slug namespace not yet propagated** — RES-HZE1 still references `episode_registry.json` (FAIL, P3-RAY-01) and GATE-VIZ-NBER2 uses non-canonical slugs `dot_com`/`rates_2022` (FAIL, P3-VERA-02). These two FAILs will break the Ray→Vera→Ace→Quincy history-zoom chain immediately in Phase 4 if not fixed first. Ray must update before any pair dispatch uses RES-HZE1.

2. **User-facing field lint chain is incomplete** — `callout_text` (Evan-authored) has no DATA-D6b-style pre-handoff lint (P3-EVAN-03, P3-DANA-04) and GATE-NR/QA-CL5 DOM scan covers wrong-instrument names but not raw column identifier tokens (P3-QUINCY-04). Three agents own fragments of this problem; no single rule closes the gap end-to-end.

3. **Cross-reference fragmentation on severity and ownership** — APP-SEV1 (Ace L1/L2/L3) and Quincy's PASS/FAIL system have no declared mapping (P3-QUINCY-05), GATE-31 has no formal definition in the Quincy SOP (P3-QUINCY-02), and GATE-HZE1's FAIL owner assignment skips checking whether Ray omitted the `HISTORY_ZOOM_EPISODES` handoff block (P3-QUINCY-01). These are coordination failures that produce misdirected blockers and ambiguous QA verdicts.

---

## Items Deferred / Out of Scope

- GATE-CL5/6/7/8 individual rule text (governed by Ace's Phase-4 standards.md registration, LA-6 — Quincy verification is the cross-agent action, addressed in P3-QUINCY-03 above).
- BL-004 architecture decision (`pair_configs/*.py` vs. `portal_narrative_*.md` as authoritative) — noted in RES-EGL1 source-of-truth clause; open design decision for Lead.
- META-SBP / ECON-BUMP1 schema-bump propagation rule (LA-8) — team-coordination.md change, not a per-peer SOP finding.

---

*Phase 3 findings count: 25 total (4 FAIL, 17 WARN, 4 INFO)*  
*Findings file: `/workspaces/aig-rlic-plus/_pws/appdev-ace/sop_review_phase3_cross_20260508.md`*
