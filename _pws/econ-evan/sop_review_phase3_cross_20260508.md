# SOP Cross-Review — Phase 3 (Econ Evan, Handoff Perspective)

**Author:** Econ Evan
**Date:** 2026-05-08
**Branch:** 260430
**Phase:** Phase 3 — cross-review of five peer SOPs from a handoff perspective only. NO EDITS to any SOP or shared file (LEAD-DL1).
**SOPs reviewed:** data-agent-sop.md (Dana), visualization-agent-sop.md (Vera), research-agent-sop.md (Ray), appdev-agent-sop.md (Ace), qa-agent-sop.md (Quincy)
**Binding arbitrations applied:** LA-1 through LA-10 (Lead Phase 2). Not re-litigated here.
**Skipped per instruction:** episode_registry retargeting (LA-1/LA-2), `observed_direction` ownership (LA-4), standards.md batch registration (LA-5), schema-bump rule promotion to META-SBP (LA-8).

---

## Summary Table

| Peer | Findings | FAIL | WARN |
|------|----------|------|------|
| Dana (Data) | 5 | 2 | 3 |
| Vera (Visualization) | 6 | 3 | 3 |
| Ray (Research) | 5 | 2 | 3 |
| Ace (AppDev) | 5 | 3 | 2 |
| Quincy (QA) | 4 | 2 | 2 |
| **Total** | **25** | **12** | **13** |

---

## Section 1 — Dana (Data Agent SOP)

**Evan's handoff dependency on Dana:** stationarity test results, `interpretation_metadata.json` classification fields (`indicator_type`, `indicator_nature`), DATA-D5 sidecar (unit, display_name, direction), `data/manifest.json` (refresh TTL), canonical signal column name.

---

### D-P3-01 — Stationarity CSV double-write risk: Dana delivers, Evan saves — no file-path disambiguation
**Contract type:** Missing handoff (mutually-referenced, not jointly specified)
**Problem:** Dana SOP §5 ("Stationarity testing ownership") states: "Dana runs ADF, KPSS, and/or Phillips-Perron tests and delivers results in a structured table. The econometrics agent reviews and confirms these results rather than re-running from scratch." Evan's SOP §4 (Exploratory Analysis) says "If Dana has already provided stationarity tests, review and confirm rather than re-running." But neither SOP specifies who owns the CSV artifact path. Evan's Rule C1/C2a mandatory output table lists `stationarity_tests_{date}.csv` under `results/{pair_id}/core_models_{date}/` as Evan's output. Dana has no matching delivery rule specifying a path under `results/`. If both save the file to different paths, Ace's `page_templates.py` (which uses `sorted(glob("stationarity_tests_*.csv"))[-1]`) will pick whichever is newer — silently using the wrong version if Dana's delivery and Evan's re-save are on different dates.
**Severity:** FAIL
**Who must fix:** Evan (SOP edit in Phase 4): add an explicit "if Dana provided `stationarity_tests_{date}.csv`, copy it to `results/{pair_id}/core_models_{date}/stationarity_tests_{date}.csv` without re-running tests; do not create a second file under a different path." Dana SOP (Phase 4 SOP edit): add a note that the authoritative consumer path for stationarity tests is `results/{pair_id}/core_models_{date}/stationarity_tests_{date}.csv`, not a path under `data/`.

---

### D-P3-02 — `indicator_type` vocabulary: Dana's classification vocabulary includes `activity` as a near-synonym; Evan's Rule C1 catalog uses `production/macro` — silent routing ambiguity
**Contract type:** Vocabulary drift
**Problem:** Dana SOP Rule D3 Step 2 states: "Evan's SOP also references `activity` as a near-synonym for `production/macro`. If in doubt between `production` and `macro`, prefer `production` for real-economy output series." Evan's SOP §2 Rule C1 defines the `indicator_type` enum as `{price, production, sentiment, rates, credit, volatility, macro}` — `activity` is explicitly NOT in the enum. Dana's note about `activity` as a near-synonym is informal guidance, not a controlled-vocabulary mapping, and it does not appear in `interpretation_metadata.schema.json`. If a future Dana uses the word `activity` as a literal value in `interpretation_metadata.json`, Evan's Rule C1 router will fail to find a method catalog entry for that type (because the router keys on exact enum values), and a new pair would ship with no mandatory methods run.
**Severity:** WARN
**Who must fix:** Dana (Phase 4): Remove the `activity` synonym reference from Rule D3 Step 2 and replace with an explicit decision rule: "If choosing between `production` and `macro`, prefer `production` for real-economy output series (INDPRO, permits, industrial capacity); prefer `macro` for composite indices (NFCI, Chicago Fed). Never use `activity` as a field value." Cross-reference: Evan's Rule C1 enum.

---

### D-P3-03 — DATA-D6b producer-side lint targets `key_finding` field; Evan is the downstream owner of that field — cross-ref absent
**Contract type:** Missing handoff (cross-reference)
**Problem:** Dana SOP Rule DATA-D6b mandates that Dana run a grep lint on `interpretation_metadata.json.key_finding` before handoff, checking for raw column identifiers. However, per `interpretation_metadata.schema.json` `owner_writes`, `key_finding` is listed as an Evan-owned field (Evan writes it post-tournament when he knows the winning signal and direction). If Dana writes `key_finding` at data-stage, it would overwrite Evan's later entry (the merge order per DATA-D6 is `dana → evan → ray`). The DATA-D6b rule is either (a) misattributed — Dana should not be writing `key_finding`; the lint belongs in Evan's or Ray's SOP; or (b) Dana is writing a placeholder `key_finding` at data-stage that Evan is expected to overwrite. Neither interpretation is stated. Evan has no rule requiring him to re-run the DATA-D6b lint on the `key_finding` value he writes.
**Severity:** FAIL
**Who must fix:** Dana SOP (Phase 4): clarify whether Dana writes `key_finding` at all. If yes, add it to Dana's `owner_writes` section and note it is a placeholder overwritten by Evan. If no, remove the DATA-D6b lint instruction for `key_finding` from Dana's SOP and move it to Evan's Quality Gates checklist, or to Ray's SOP (since Ray's key_finding is the final user-facing version). Cross-reference with `interpretation_metadata.schema.json` `owner_writes`.

---

### D-P3-04 — `display_name_registry.csv` consumed by Evan's signal-column reader but Evan's SOP has no check for registry presence before tournament
**Contract type:** Missing handoff (Evan expects but doesn't gate)
**Problem:** DATA-D13 names Evan as a consumer of `data/display_name_registry.csv` ("Evan / Vera / Ray / Ace read directly; none may duplicate the mapping locally"). Evan's SOP Rule C1 and ECON-H5 refer to `display_name` as available from the sidecar. However, Evan's SOP has no intake check confirming the registry exists before starting tournament execution. If Dana delivered the pair without a complete registry (e.g., a partial delivery per the Partial Delivery Protocol), Evan would proceed with tournament execution and then fail silently when the signal-column reader cannot find a display_name for the winning signal. There is no explicit "before tournament, verify `data/display_name_registry.csv` has a row for the pair's canonical signal column" step in Evan's SOP.
**Severity:** WARN
**Who must fix:** Evan (Phase 4): add to §1 Intake Validation: "Before tournament execution, confirm `data/display_name_registry.csv` contains a row for the pair's `canonical_column` (from `signal_scope.json`) or request one from Dana."

---

### D-P3-05 — DATA-VS vocabulary `"Mature"` label used in Dana SOP status checks; Evan does not produce or consume `"Mature"` — creates asymmetric vocabulary exposure
**Contract type:** Vocabulary drift (minor, directional only)
**Problem:** Dana's DATA-VS lists "Available / Pending / Validated / Stale / Draft / Mature / Unknown" as the canonical status vocabulary. Evan's SOP uses `evidence_status` levels (`found_in_search`, `needs_final_exam`, `passed_final_exam`) for the pair's overall evidence grade. These are different vocabularies for different constructs — but the `"Mature"` label in the DATA-VS set is defined as "artifact has persisted across 3+ acceptance cycles with no schema, validation, or content changes." Evan's handoff notes do not use `"Mature"` for any artifact. This is not a contract mismatch but a vocabulary siloing that could create confusion if Ace or Ray try to map Dana's `"Mature"` chip to an evidence-status badge.
**Severity:** WARN
**Who must fix:** Informational only — no immediate Phase 4 fix required. The vocabulary boundary should be documented clearly in team-coordination.md as: "DATA-VS vocabulary governs data-layer artifact status only; `evidence_status.json` vocabulary governs pair evidence-grade status only. Do not cross-map."

---

## Section 2 — Vera (Visualization Agent SOP)

**Evan's handoff dependency on Vera:** Vera is Evan's downstream consumer of chart artifact inputs from ECON-H4 handoff table; VIZ-V8 / chart_type_registry.json is the canonical filename standard Evan must match.

---

### V-P3-01 — ECON-H4 handoff `status: ready` verification against chart_type_registry: no explicit cross-check step in Evan's SOP
**Contract type:** Missing handoff (producer-side verification absent)
**Problem:** Evan's SOP ECON-H4 mandates writing a per-method handoff table with `method / result_file / expected_chart / status`. Rule A3 in Vera's SOP states: "The machine-readable catalog in `docs/schemas/chart_type_registry.json` is the single source of truth for method-to-chart bindings and canonical filename patterns (VIZ-V8). If they diverge from the registry, the registry wins." VIZ-V8 further states: "Evan's `results/{pair_id}/handoff_to_vera_{date}.md` per-method table ... MUST align with a registry entry: the handoff's `expected_chart` description names the same `expected_chart_type` the registry carries, and `result_file` matches the registry's `required_result_file`." However, Evan's ECON-H4 SOP text contains no instruction to cross-check his `expected_chart` label against the registry before writing the handoff. Evan could write `expected_chart: "CCF bar chart"` when the registry entry for `method_name: "ccf"` uses `expected_chart_type: "ccf_bar"` — a field-name discrepancy that leaves Vera's validation step (VIZ-V8 "Divergence between Evan's handoff row and the registry is a blocking reconciliation failure") with no automated fix path.
**Severity:** FAIL
**Who must fix:** Evan (Phase 4): add an ECON-H4 pre-handoff check step: "Before writing `handoff_to_vera_{date}.md`, load `docs/schemas/chart_type_registry.json` and verify that each row's `expected_chart` description matches the registry's `expected_chart_type` for the corresponding `method_name`. Paste the registry's canonical `expected_chart_type` string verbatim, not a prose synonym."

---

### V-P3-02 — CP1/CP2 output files use `{pair_id}` in filename; VIZ-CP1 canonical filenames use bare names — filing asymmetry causes Vera to receive `rolling_correlation_{pair_id}.csv` but VIZ-CP1 `_meta.json` expects `rolling_correlation.json`
**Contract type:** Contract mismatch (filename)
**Problem:** Evan's SOP ECON-CP1-B mandates: `results/{pair_id}/rolling_correlation_{pair_id}.csv`. VIZ-CP1.2 in Vera's SOP mandates the output chart be named `rolling_correlation.json` (bare name, pair_id in directory per VIZ-A3). The VIZ-CP1.2 `_meta.json` required field is `chart_name: "rolling_correlation"`. Vera's SOP VIZ-CP1 also states `result_file` in the CP sidecar must point to the upstream result CSV. If the upstream CSV is `rolling_correlation_{pair_id}.csv` but the chart's `result_file` in the sidecar uses the bare name `rolling_correlation.csv` (which Vera might assume by analogy with chart bare-naming convention), the sidecar's `result_file` will be a dead path. Flagged in Phase 1 finding F-06 as Evan's intra-SOP inconsistency; here the cross-agent impact is: Vera's VIZ-CP1 `_meta.json` template needs to be told the exact upstream CSV filename pattern.
**Severity:** FAIL
**Who must fix:** Vera (Phase 4): VIZ-CP1 `_meta.json` template for `result_file` should specify: "`result_file` must use the upstream CSV path verbatim from Evan's ECON-H4 handoff table, which follows the `{method}_{pair_id}.csv` pattern for CP1/CP2 artifacts, not the bare-name convention. Example: `results/hy_ig_spy/rolling_correlation_hy_ig_spy.csv`." Additionally, Evan (Phase 4): add a note to ECON-CP1-B: "CP1/CP2 CSV filenames include `{pair_id}` by convention to distinguish them from aggregate C2 outputs; Vera's chart JSON uses bare names (pair_id in directory only). Make this explicit in the ECON-H4 handoff row."

---

### V-P3-03 — Durability verdict vocabulary (`"durable"`, `"conditionally durable"`, `"episode-concentrated"`) in Evan's CP1-A is not referenced in VIZ-CP1 or Vera's chart spec — Vera cannot encode it visually without a vocabulary bridge
**Contract type:** Missing handoff (vocabulary not transmitted)
**Problem:** Evan's ECON-CP1-A says the sub-period analysis produces a durability verdict using three labels: `"durable"`, `"conditionally durable"`, `"episode-concentrated"`. These labels are stored in `subperiod_sharpe.csv`. VIZ-CP1.1 specifies the `subperiod_sharpe.json` chart content (grouped bar chart with Sharpe, win-rate, max-drawdown) but does not mention the durability verdict field, does not specify how to visually encode it (e.g., as a chart subtitle, annotation, or label color), and does not cite which CSV column carries it. The result: the verdict is computed by Evan, stored in CSV, but has no specified visual surface in Vera's chart spec. If Vera omits it, the durability verdict never reaches the portal user.
**Severity:** FAIL
**Who must fix:** Evan (Phase 4): add a row to the ECON-H4 handoff table for the `subperiod_sharpe.csv` output, explicitly listing the `durability_verdict` column and its expected values. Vera (Phase 4): add a VIZ-CP1.1 annotation requirement — "include the durability verdict as a chart subtitle or prominent annotation below the x-axis. Format: 'Overall verdict: {durability_verdict}'. Source column: `subperiod_sharpe.csv.durability_verdict`."

---

### V-P3-04 — ECON-H5 handoff annotation requirement (Evan's ECON-CP1 methodology_note) has no Vera-facing equivalent — Vera does not know sub-period Sharpes must carry a specific disclaimer
**Contract type:** Missing handoff (Evan-to-Vera disclaimer not transmitted)
**Problem:** Phase 1 finding F-07 identified that Evan must include a handoff annotation when delivering `subperiod_sharpe.csv` to Ray: "Sub-period Sharpes reflect directional durability only (sign(signal) × return), NOT replication of tournament execution mechanics. Use tournament OOS Sharpe as the point-estimate reference." Evan's SOP targets Ray and Ace with this disclaimer, but not Vera. Vera produces the `subperiod_sharpe.json` chart with bar heights that are sub-period Sharpe values. If a stakeholder reads the chart without the disclaimer, they could mistake the sub-period bar heights for tournament-execution Sharpes. Vera has no instruction to include this disclaimer in the chart caption or footnote.
**Severity:** WARN
**Who must fix:** Vera (Phase 4): VIZ-CP1.1 should add a mandatory chart caption/footnote template: "Note: Sub-period Sharpe values reflect directional consistency (sign(signal) × return) only and are not replication of tournament execution. Refer to the tournament OOS Sharpe for the point-estimate." This text should be stored in `_meta.json.caption` for the `subperiod_sharpe.json` chart.

---

### V-P3-05 — VIZ-ZOOM1 reads episode slugs from `docs/schemas/episode_registry.json`; LA-1 (Lead) deprecates `episode_registry.json` and makes `history_zoom_events_registry.json` canonical — Vera SOP references the deprecated file
**Contract type:** Cross-ref integrity (LA-1 binding arbitration not reflected in Vera SOP)
**Problem:** LA-1 states: "`history_zoom_events_registry.json` is the canonical episode registry. `episode_registry.json` is deprecated." Vera's Rule VIZ-ZOOM1 §"Episode selection for zoom charts" reads: "Read from `docs/schemas/episode_registry.json` keyed on `interpretation_metadata.indicator_category`." Similarly, VIZ-HZE1 §1 says: "Read `docs/schemas/episode_registry.json`". These references are to the deprecated file. Note: this finding is included because it is a direct handoff contract point with Evan — Evan's ECON-CP1 also reads from `episode_registry.json` and both will need coordinated retargeting to the canonical registry per LA-1/LA-2. The coordination dependency is the handoff concern.
**Severity:** WARN
**Who must fix:** Per LA-1: Vera authors the registry consolidation in Phase 4 (first), then Evan, Ray, and Quincy retarget in their Phase 4 edits. This finding flags the coordination dependency: Vera's Phase 4 registry PR must be merged before Evan updates ECON-CP1 to avoid a window where both reference different files.

---

### V-P3-06 — VIZ-CP1 `_meta.json` for CP charts requires `econ_rule_id` field; Evan's ECON-H4 handoff row does not explicitly name the ECON rule ID — Vera must infer
**Contract type:** Missing handoff (field not transmitted)
**Problem:** Vera's VIZ-CP1 sidecar spec requires `"econ_rule_id": "ECON-CP1"` or `"ECON-CP2"` in each CP chart's `_meta.json`. Evan's ECON-H4 per-method handoff table columns are: `method / result_file / expected_chart / status`. There is no `econ_rule_id` column. Vera must infer whether a given method maps to ECON-CP1 or ECON-CP2 by matching the method name against an internal understanding, not from a machine-readable field in the handoff. If Evan adds new CP methods in future, Vera has no handoff contract guaranteeing the correct rule ID.
**Severity:** WARN
**Who must fix:** Evan (Phase 4): add an optional `econ_rule_id` column to the ECON-H4 handoff table template. For CP methods, populate it explicitly ("ECON-CP1" or "ECON-CP2"). Vera reads it directly into the `_meta.json.econ_rule_id` field.

---

## Section 3 — Ray (Research Agent SOP)

**Evan's handoff dependency on Ray:** Ray reads `oos_split_record.json` for the OOS span (RES-18), `winner_summary.json` for the headline Sharpe (RES-18), `subperiod_sharpe.csv` (durability narrative), and `structural_break_{pair_id}.json` (flagged structural breaks).

---

### R-P3-01 — RES-18 reads `oos_split_record.json` for OOS span; Evan's ECON-H5 adjacent contract commits to `winner_summary.json` but is silent on `oos_split_record.json` field format — Ray could read a stale or missing file
**Contract type:** Contract mismatch (field specification)
**Problem:** Ray's RES-18 Rule states: "The `[OOS span]` value is resolved from `results/{pair_id}/oos_split_record.json` (Evan-owned, per ECON-H5 adjacent contract). Ray does NOT hand-type an OOS year-count." Evan's SOP defines `oos_split_record.json` in ECON-OOS1 as the ownership artifact for OOS window metadata. However, Evan's SOP does not specify the field name Ray should read to get the OOS span in years. Is it `oos_n_years`? `oos_start_date` + `oos_end_date` (from which Ray computes years)? `oos_period_label` (a pre-formatted string)? If Ray reads the wrong field or computes years from dates using a different calendar convention (365 vs 252 trading days), the headline "8-year OOS" or "15-year OOS" will be inconsistent with Evan's `oos_split_record.json` without triggering a validation error.
**Severity:** FAIL
**Who must fix:** Evan (Phase 4): add to ECON-OOS1 a specification of the `oos_split_record.json` field that Ray reads for narrative templates: "The `oos_year_count` field (integer, calendar years rounded to nearest whole year) is the authoritative OOS span for Ray's RES-18 headline templates. Ray reads `oos_split_record.json.oos_year_count` directly; do not read `oos_start_date`/`oos_end_date` and compute." Add `oos_year_count` to the `oos_split_record.json` schema if not already present.

---

### R-P3-02 — ECON-CP1 structural break flag propagation: Evan says "if `flagged: true` in `structural_break_{pair_id}.json`, Ray's narrative must include the caution flag"; Ray SOP has no corresponding rule
**Contract type:** Missing handoff (Evan assigns obligation to Ray; Ray SOP does not commit)
**Problem:** Evan's SOP ECON-CP1-C states: "If `flagged: true` in `structural_break_{pair_id}.json`, Ray's narrative must include the caution flag verbatim." Ray's SOP does not contain a corresponding rule mandating that Ray reads `structural_break_{pair_id}.json` before authoring the narrative or that Ray must include the caution text verbatim when the flag is true. Ray's RES-HZE1 and RES-20 address episode narrative selection, but neither rule checks for a structural break flag. The caution flag propagation is thus a one-sided mandate in Evan's SOP with no corresponding commitment in Ray's SOP.
**Severity:** FAIL
**Who must fix:** Ray (Phase 4): add a rule (proposed: RES-CP1a or as a sub-step of RES-20) — "Before finalizing the durability narrative for any CP1 pair, read `results/{pair_id}/structural_break_{pair_id}.json`. If `flagged: true`, include the following caution in the Evidence page narrative verbatim: [Evan's caution text template]. This flag is mandatory and non-negotiable when present."

---

### R-P3-03 — Durability verdict vocabulary (`"durable"` / `"conditionally durable"` / `"episode-concentrated"`) from ECON-CP1-A is not registered in Ray's narrative vocabulary, Ray's quality gates, or `docs/portal_glossary.json`
**Contract type:** Vocabulary drift
**Problem:** Evan's ECON-CP1-A produces a durability verdict with three labels. Ray's narrative will render these labels for users. But Ray's SOP contains no reference to these three labels, no instruction on how to translate them into user-facing prose (the labels are semi-technical), and no quality-gate check confirming the narrative's rendering matches the verdict stored in `subperiod_sharpe.csv`. Ray's Rule RES-22 (status-label decision table) covers artifact status labels, not analytical verdict labels; the durability verdict vocabulary lives outside both. If Ray invents synonyms ("robust across cycles" for `"durable"`), the labels become inconsistent across portal pages.
**Severity:** WARN
**Who must fix:** Ray (Phase 4): add a subsection under Evidence Page authoring defining the three durability verdict labels with their user-facing prose mappings. Example: `"durable"` → "The strategy performed consistently across all tested historical episodes." `"conditionally durable"` → "The strategy performed well in most historical periods but showed meaningful variation across episodes — review the episode breakdown." `"episode-concentrated"` → "Most of the strategy's performance was concentrated in one or two specific historical episodes; generalizability is uncertain."

---

### R-P3-04 — Ray's RES-20 requires episode slugs to exist in `output/charts/chart_type_registry.json`; the canonical episode slug registry per LA-1 is `docs/schemas/history_zoom_events_registry.json` — wrong path cited
**Contract type:** Cross-ref integrity (phantom path, post-LA-1)
**Problem:** Ray's Rule RES-20 §Rule 2 states: "Episode must exist in Vera's registry. Each `episode_slug` MUST resolve to an entry in `output/charts/chart_type_registry.json` (VIZ-V12 / chart-type registry)." The parenthetical `VIZ-V12 / chart-type registry` is self-contradictory: VIZ-V12 refers to the events registry (`docs/schemas/history_zoom_events_registry.json`), while `output/charts/chart_type_registry.json` is the chart-type binding registry (a different file). Evan's Phase 1 finding F-08 also noted this phantom path discrepancy in `episode_registry.json` vs the canonical registry. The path cited by Ray maps to a non-existent location — episode slugs are not in the chart-type registry.
**Severity:** WARN
**Who must fix:** Ray (Phase 4): Rule RES-20 §2 should read: "Each `episode_slug` MUST resolve to an entry in `docs/schemas/history_zoom_events_registry.json` (VIZ-V12 canonical events registry, per LA-1)." Remove the reference to `output/charts/chart_type_registry.json`.

---

### R-P3-05 — ECON-CP2 produces `rolling_sharpe` and `rolling_granger` artifacts; Ray's narrative template for Evidence page cross-period section lacks explicit field names for reading these artifacts
**Contract type:** Missing handoff (no Ray-side field-name contract)
**Problem:** Evan's ECON-CP2 outputs `rolling_sharpe_{pair_id}.csv` and a Granger rolling CSV. Vera's VIZ-CP1.4 and VIZ-CP1.5 consume them to produce charts. Ray's narrative for the cross-period Evidence section must interpret these charts (elements 1-8 per the 8-element template). But Ray's SOP contains no specification of which CSV fields to read when writing the Observation (element 5) or Key Message (element 8) for rolling Sharpe or rolling Granger. Without field-name contracts, Ray will write observations from visual inspection of Vera's chart rather than from the authoritative CSV, creating the possibility of prose drifting from the underlying numbers.
**Severity:** WARN
**Who must fix:** Evan (Phase 4): add to ECON-CP2 a "Ray Narrative Fields" subsection listing the specific CSV columns Ray should cite in the narrative: for `rolling_sharpe`, the columns are `window_mean_sharpe`, `window_min_sharpe`, `pct_windows_positive`; for `rolling_granger`, the columns are `n_windows_significant`, `pct_windows_significant`, `critical_f_value`. Ray (Phase 4): add a cross-period Evidence subsection specifying these field names as the authoritative source for narrative observations.

---

## Section 4 — Ace (AppDev Agent SOP)

**Evan's handoff dependency on Ace:** Ace consumes `winner_summary.json` (APP-WS1), `interpretation_metadata.json` direction fields (APP-DIR1), `evidence_status.json` (APP-LP8), and `signal_scope.json` (APP-SS1). These are Evan's primary deliverables to the portal.

---

### A-P3-01 — APP-WS1 loads `winner_summary.json` against schema v1.0.0; live schema is at v1.1.0 — Ace's validator will accept v1.1.0 instances only if it uses the live schema file (not a cached v1.0.0 reference)
**Contract type:** Contract mismatch (version reference)
**Problem:** APP-WS1 states: "validates the instance against `docs/schemas/winner_summary.schema.json` (v1.0.0, owner: Evan, producer rule ECON-H5)." The live schema is at v1.1.0 (per Evan Phase 1 finding F-05 and LA-10). If Ace's validator call in `app.components.schema_check.validate_or_die` was written with a hardcoded schema path when the schema was at v1.0.0, it may work correctly IF the path resolves to the live schema file. But the prose citation of "v1.0.0" in APP-WS1 means a future Ace reading only the SOP would believe the current schema version is v1.0.0, potentially missing that v1.1.0 adds `null` acceptance for `threshold_value`. An Ace loading a v1.1.0 instance against a v1.0.0 schema definition (if cached or copied) would get a validation error on pairs with `threshold_value: null`, blocking the Strategy page.
**Severity:** FAIL
**Who must fix:** Ace (Phase 4): update APP-WS1 version citation to v1.1.0 (per LA-10 stale citation retirement). Add a rule: "Schema version in APP-WS1 must be updated whenever Evan bumps `winner_summary.schema.json` — the version is cited explicitly in the SOP prose for auditability and must not be allowed to drift." Cross-reference: ECON-H5 (Evan), LA-10 (Lead arbitration).

---

### A-P3-02 — APP-LP8 (evidence-status label on landing card) consumes `evidence_status.json` but does not verify `final_exam.qa_status == "qa_passed"` before rendering `passed_final_exam` label — GATE-ES1 gap
**Contract type:** Missing handoff (ECON-FE1 condition 10 not wired to APP-LP8)
**Problem:** Evan's FE1 condition 10 states: "QA replay gate: GATE-ES1 (Quincy's Evidence-Status Promotion) passes before `passed_final_exam` is written to `evidence_status.json`." GATE-ES1 (Quincy SOP) includes: "If `status = 'passed_final_exam'` but `final_exam.qa_status` is not `'qa_passed'`, the promotion is a FAIL." Ace's APP-LP8 states: "Every landing-page card MUST show an evidence-status label loaded from `results/{pair_id}/evidence_status.json`." But APP-LP8 does not instruct Ace to read `final_exam.qa_status` from within the `evidence_status.json` or `final_exam_results.json` and verify it equals `"qa_passed"` before rendering the `passed_final_exam` label. Ace's landing-card renderer trusts the `status` field value directly. If a corrupt or pre-QA instance of `evidence_status.json` were present with `status: "passed_final_exam"` and `final_exam.qa_status: "pending"`, Ace would display the `Passed final exam` label without Quincy's gate having fired. This is exactly the anti-gaming scenario ECON-FE1 condition 10 is designed to prevent.
**Severity:** FAIL
**Who must fix:** Ace (Phase 4): update APP-LP8 to add a defensive check before rendering the `passed_final_exam` label: "Before rendering the `passed_final_exam` label, also read `evidence_status.json.final_exam.qa_status`. If this field is absent or not `'qa_passed'`, degrade to the `found_in_search` label and surface an APP-SEV1 L2 warning: `'Final exam label suppressed: qa_status not confirmed as qa_passed. Contact Quincy.'` This is the Ace-side enforcement of ECON-FE1 condition 10 at the render layer." Cross-reference GATE-ES1.

---

### A-P3-03 — `winner_summary.json` `direction` field drives APP-DIR1 direction triangulation; Ace's SOP does not specify the canonical enum value set — `"mixed"` vs `"ambiguous"` vs `"conditional"` drift risk
**Contract type:** Vocabulary drift
**Problem:** Ace's SOP §3.5 "Direction Annotation Components" states: `render_how_to_read` "Handles canonical direction values: procyclical, countercyclical, mixed." APP-WS1 cites the schema enum for `direction` as `procyclical | countercyclical | mixed`. Evan's ECON-FE1 and interpretation_metadata use `mixed` as the canonical ambiguous/conditional value. However, Ace's SOP §3.5 also says: "If the relationship is ambiguous, conditional, regime-specific, or otherwise not reducible to one APP-DIR1 enum value, keep `observed_direction` in the canonical enum (`mixed` unless the canonical registry says otherwise)." The parenthetical "unless the canonical registry says otherwise" is undefined — there is no "canonical registry" of direction enum values cited here. If a future Evan writes `direction: "conditional"` in `winner_summary.json` (an informal label that could plausibly be used for regime-dependent strategies), Ace's `render_how_to_read` would not handle it (the function only handles `procyclical`, `countercyclical`, `mixed`), and the "How to Read This" callout would silently fall through to a default branch.
**Severity:** WARN
**Who must fix:** Ace (Phase 4): the `render_how_to_read` function must have an explicit `else` branch that catches any non-canonical value and renders an APP-SEV1 L2 warning ("Unexpected direction value: {value}. Expected one of: procyclical, countercyclical, mixed. Contact Evan to fix winner_summary.json."). Cross-reference: winner_summary.schema.json `direction` enum.

---

### A-P3-04 — Ace's GATE-CL3 requires "vs X buy-and-hold" on all Story pages from `winner_summary.json`; Evan's SOP does not name a specific `benchmark_bah_*` field in `winner_summary.json` schema — Ace may read from the wrong source
**Contract type:** Missing handoff (field-name specification absent)
**Problem:** Ace's GATE-CL3 states: "Every Story page key metrics block must show 'vs X buy-and-hold' — never 'vs N/A'. Source: tournament CSV BENCHMARK row. If `winner_summary.json` is missing these fields, the template must backfill from tournament CSV." Evan's SOP ECON-H5 lists `winner_summary.json` required fields but does not specify a `benchmark_bah_sharpe`, `benchmark_bah_return`, or equivalent field. The schema (`winner_summary.schema.json`) currently contains `oos_bah_sharpe` and `oos_bah_ann_return` (OOS buy-and-hold metrics). GATE-CL3's fallback to "tournament CSV BENCHMARK row" is also underspecified — which CSV file, which column name? If Evan's ECON-H5 contract adds `oos_bah_sharpe` but Ace reads `benchmark_bah_sharpe` (by analogy), a silent KeyError or None-render occurs.
**Severity:** WARN
**Who must fix:** Evan (Phase 4): add to ECON-H5 a "Benchmark fields" subsection: "The buy-and-hold comparison metrics for Story page KPI cards are `oos_bah_sharpe` and `oos_bah_ann_return`. Ace reads these directly from `winner_summary.json`. These fields are REQUIRED when the pair has a portal Story page." Ace (Phase 4): update GATE-CL3 to cite the exact field names: "`winner_summary.json.oos_bah_sharpe` and `oos_bah_ann_return`" and specify the fallback column names in the tournament CSV.

---

### A-P3-05 — ACE-HZE1 validates episode slugs against `docs/schemas/episode_registry.json`; LA-1 deprecates this file — ACE-HZE1 references the deprecated registry path
**Contract type:** Cross-ref integrity (LA-1 binding arbitration not reflected in Ace SOP)
**Problem:** Ace's ACE-HZE1 §2 states: "For each on-disk slug, Ace MUST cross-check the slug against `docs/schemas/episode_registry.json` keyed on `indicator_category` for the pair." Per LA-1 (Lead binding arbitration), `episode_registry.json` is deprecated; `history_zoom_events_registry.json` is canonical. This is the same retargeting need as V-P3-05 and R-P3-04 — three agents reference the deprecated file. The coordination dependency for Ace is that Vera must complete the registry consolidation (Phase 4 first step per LA-1) before Ace's ACE-HZE1 can be updated with the correct path.
**Severity:** FAIL
**Who must fix:** Ace (Phase 4, after Vera's registry PR): update ACE-HZE1 §2 to read `docs/schemas/history_zoom_events_registry.json` instead of `docs/schemas/episode_registry.json`. Cross-reference: LA-1.

---

## Section 5 — Quincy (QA Agent SOP)

**Evan's handoff dependency on Quincy:** Quincy's GATE-ES1 independently verifies every `evidence_status.json` promotion above `found_in_search`. GATE-31 covers ECON-SD scope discipline (per ECON-SD "Enforcement → QA" sub-bullet). Quincy's GATE-VIZ-NBER2 references `episode_registry.json` slug table.

---

### Q-P3-01 — GATE-ES1 checks 8 conditions including numeric metrics; it does NOT check `confirm_n_obs ≥ class_floor` — ECON-FE1 condition 3 minimum sample requirement has no QA numeric gate
**Contract type:** Severity asymmetry / missing gate
**Problem:** ECON-FE1 condition 3 requires minimum confirmation samples by frequency class (daily ≥ 252 trading days; monthly ≥ 36 observations; crypto ≥ 365 days). Evan's Phase 1 finding F-01 identified that `final_exam_results.schema.json` only enforces `confirm_n_obs minimum: 1`, not the class-specific floor. GATE-ES1 (Quincy) checks 8 conditions including "Compare expected versus observed headline metrics: confirmation Sharpe, excess return, delta Sharpe, drawdown, bootstrap uncertainty, and multiple-testing adjustment" — but the class-floor check for `confirm_n_obs` is NOT listed among the 8 conditions. A pair with `confirm_n_obs: 10` on a daily equity series (which requires ≥ 252) would pass GATE-ES1 schema validation and pass the 8-condition check, falsely promoted.
**Severity:** FAIL
**Who must fix:** Quincy (Phase 4): add a 9th GATE-ES1 condition: "Verify `final_exam_results.confirm_n_obs ≥ class_floor` where class_floor is determined by the pair's target_class and frequency (daily equity ≥ 252; monthly ≥ 36; crypto daily ≥ 365; other: ≥ 24). If `minimum_confirmation_n_obs` is present in the `final_exam_results_*.json`, use that field's value as the floor; otherwise compute from target_class and frequency per ECON-FE1 condition 3." Evan (Phase 4): add `minimum_confirmation_n_obs` to `final_exam_results.schema.json` (see Phase 1 F-01).

---

### Q-P3-02 — ECON-SD audit: Evan's SOP assigns GATE-31 to Quincy for scope discipline; GATE-31 in Quincy's SOP covers KPI triangulation (QA-CL2) — the ECON-SD audit is not explicitly in GATE-31's scope
**Contract type:** Missing handoff (integration contract dead-letter — cross-confirms F-13 from Phase 1)
**Problem:** Evan's ECON-SD states: "QA (Quincy). Verifies every pair page's chart set and table set against `signal_scope.json`; any off-scope signal found is a GATE-31 block." Quincy's GATE-31 is defined implicitly as the blocking gate triggered by QA-CL2 (semantic KPI triangulation) findings. GATE-31 is described in QA-CL2 as: "Treat as BLOCKING per GATE-31 — acceptance cannot proceed." There is no GATE-31 section in Quincy's SOP that explicitly covers `signal_scope.json` audit. The cross-reference in Evan's SOP is to a gate that Quincy's SOP associates with KPI triangulation failures, not scope-discipline audit. LA-9 confirms this: "ECON-SD audit gate must appear in Quincy's QA SOP (QA-CL2 family or new gate slot)."
**Severity:** FAIL
**Who must fix:** Quincy (Phase 4, per LA-9): add an explicit GATE-31 extension or new gate slot in the QA SOP mandating the signal_scope audit: "For every pair in scope, load `results/{pair_id}/signal_scope.json` and verify that every chart in `output/charts/{pair_id}/plotly/` uses only signals listed in `scope.indicator_axis.derivatives` or `scope.target_axis.derivatives`. Any chart using an off-scope signal is a GATE-31 (or new GATE-SCOPE1) blocking finding. Owner of fix: Evan."

---

### Q-P3-03 — GATE-VIZ-NBER2 slug table hardcodes `dot_com` and `rates_2022` — these are non-canonical per LA-2; the gate will WARN/FAIL on canonical `dotcom` and `inflation_2022` charts
**Contract type:** Contract mismatch (slug vocabulary, LA-2 binding arbitration)
**Problem:** Quincy's GATE-VIZ-NBER2 contains a hardcoded "Episode–recession overlap table" with slugs: `dot_com`, `gfc`, `covid`, `taper_2013`, `china_2015`, `rates_2022`. Per LA-2 (Lead binding arbitration): canonical slugs are `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`. The GATE-VIZ-NBER2 slug table uses `dot_com` (non-canonical, underscore), `taper_2013` (non-canonical date), `china_2015` (not in LA-2 canonical set), `rates_2022` (non-canonical, should be `inflation_2022`). Vera will produce charts named `history_zoom_dotcom.json` and `history_zoom_inflation_2022.json` (canonical). GATE-VIZ-NBER2's filename matching logic `history_zoom_{slug}.json` would classify these with wrong episode data (e.g., `dotcom` chart matched against a `dot_com` entry with `dot_com = REQUIRED shading`) — but with the wrong key the match fails and the chart is treated as an unrecognized slug, potentially missing a FAIL on a recession-overlapping episode.
**Severity:** WARN
**Who must fix:** Quincy (Phase 4, after Vera's registry PR per LA-2): update GATE-VIZ-NBER2 hardcoded slug table to: `dotcom` (2000-03 → 2002-10, NBER 2001 overlap, REQUIRED), `gfc` (2007-12 → 2009-06, NBER 2008 overlap, REQUIRED), `covid` (2020-02 → 2020-12, NBER 2020 overlap, REQUIRED), `taper_2018` (2018, no NBER overlap, WARN if shaded), `inflation_2022` (2022, no NBER overlap, WARN if shaded). Remove `dot_com`, `taper_2013`, `china_2015`, `rates_2022`. Cross-reference: LA-2.

---

### Q-P3-04 — GATE-ES1 does not cite ECON-FE1 as its parent rule; QA-CL1 does not include GATE-ES1 as a checklist item — the gate exists but has no systematic dispatch trigger
**Contract type:** Cross-ref integrity / severity asymmetry
**Problem:** GATE-ES1 is a well-defined gate in Quincy's SOP (8 conditions, blocking severity). However: (a) GATE-ES1 is not listed as a checklist item in QA-CL1 (the standard per-wave checklist); (b) GATE-ES1 does not cross-reference ECON-FE1 as the upstream rule that defines the contract; (c) Evan's ECON-FE1 cross-link to GATE-ES1 is absent (per Phase 1 F-04). Without a QA-CL1 entry, a Quincy working from the checklist alone would not be reminded to run GATE-ES1 unless a pair explicitly promotes above `found_in_search`. This is an implicit dispatch trigger ("when promotion happens") rather than an explicit checklist item. If the promotion occurs in the same wave as a heavy workload, the absence of the checklist item is a realistic miss path.
**Severity:** WARN
**Who must fix:** Quincy (Phase 4): add GATE-ES1 to QA-CL1 as: "[ ] GATE-ES1 — if any active pair's `evidence_status.json` carries `status` above `found_in_search`, run the full 8+1 condition GATE-ES1 check and record findings." Evan (Phase 4): add GATE-ES1 cross-reference at end of ECON-FE1 consumer wording guard (per Phase 1 F-04 fix).

---

## Cross-Cutting Themes (Top 3)

1. **Episode-registry path fragmentation across all five peers (V-P3-05, R-P3-04, A-P3-05, Q-P3-03).** Four agents reference either the deprecated `episode_registry.json` or use non-canonical slugs. This is already arbitrated by LA-1/LA-2 but is flagged here as a coordination sequencing risk: Vera's registry consolidation PR must precede all other Phase 4 retargeting edits. Any agent that updates their SOP before Vera's PR merges will reference a non-existent or incomplete canonical registry.

2. **Evan writes conditions that peer agents are obligated to enforce, but those conditions are absent from the peers' SOPs (R-P3-02, Q-P3-01, Q-P3-02).** Three separate cases where Evan's SOP assigns an obligation to a downstream agent and the peer SOP contains no corresponding rule: Ray must include structural-break caution text (R-P3-02), Quincy must check confirm_n_obs ≥ class_floor (Q-P3-01), Quincy must audit signal_scope.json (Q-P3-02 / LA-9). These are one-sided contracts — the integration seams exist on paper but are dead-letters downstream.

3. **Version reference drift and field-name underspecification at the Evan→Ace boundary (A-P3-01, A-P3-04, V-P3-01).** Ace's APP-WS1 cites a stale schema version; GATE-CL3 cites unspecified field names; Evan's ECON-H4 handoff table is not required to cross-check chart-type registry entries. At scale (73 pairs), any of these will produce silent mismatches that pass smoke tests and fail in the DOM.

---

## Items Confirmed Clear (Not Flagged)

- LA-4 (`observed_direction` ownership): Dana SOP does not write the field at data stage; Evan writes post-tournament. Chain is clean. Not re-litigated.
- ECON-DIR1 → DATA-D6 relationship: Dana's DATA-D6 correctly maps `owner_writes` with the `dana → evan → ray` merge order. Evan's ECON-DIR1 correctly delegates correction to Dana. No mismatch beyond what LA-4 already resolved.
- APP-DIR1 triangulation contract: `winner_summary.json.direction` (Evan) = `interpretation_metadata.observed_direction` (Dana/Evan) = `narrative_frontmatter.direction_asserted` (Ray). All three SOPs name the same fields and cite each other. The ownership arbitration from LA-4 flows cleanly into all three.

---

*Total findings: 25 (D: 5, V: 6, R: 5, A: 5, Q: 4)*
*FAIL: 12 | WARN: 13*
*LEAD-DL1 self-check: only `_pws/econ-evan/sop_review_phase3_cross_20260508.md` written. No SOP or shared file edits.*
