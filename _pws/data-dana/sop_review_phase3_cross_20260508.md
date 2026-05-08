# Data Agent SOP — Phase 3 Cross-SOP Handoff Review
**Author:** Data Dana
**Date:** 2026-05-08
**Branch:** 260430
**Scope:** Handoff concerns only — contract mismatches, missing handoffs, severity asymmetry, vocabulary drift, and cross-ref integrity between Dana's SOP and each peer SOP. No intra-SOP findings. No SOP edits (LEAD-DL1 respected).
**Inputs read:** Phase 1 findings (`sop_review_phase1_intra_20260508.md`), Lead Phase 2 arbitrations (LA-1 through LA-10 in `_pws/lead-lesandro/sop_review_phase2_global_20260508.md`), and peer SOPs: econometrics, visualization, research, appdev, qa.

---

## Section 1 — Evan (Econometrics Agent)

### P3-E1 — `interpretation_metadata.json` producer is ambiguous at Evan's consumer gate (FAIL)

**Rules involved:** DATA-D6 (data SOP) and ECON-DIR1 quality-gate checkbox in the econometrics SOP.

**Problem:** The econometrics SOP quality-gate checklist states: "`interpretation_metadata.json` received from Dana and validated at ECON-DIR1 consumer gate: (a) `observed_direction` in permitted vocabulary… (b) `observed_direction` matches `winner_summary.json.direction`. If either check fails, file returned to Dana — not patched by Evan." This language says the file comes FROM Dana and that Evan is the consumer-gatekeeper. Yet APP-DIR1 in `docs/standards.md` credits `observed_direction` to Dana, and the data SOP is completely silent on both producing and withholding this field. Lead LA-4 arbitrates that Evan owns `observed_direction` post-tournament and Dana leaves it absent. After LA-4 lands in Phase 4, the ECON-DIR1 gate text must be updated to say "Evan writes `observed_direction`" rather than "received from Dana" — otherwise the consumer gate still implies Dana is the producer, recreating the three-way conflict.

**Severity proposal:** FAIL (circular producer attribution at gate is a blocking contract defect; it will cause any future dispatch following only the ECON-DIR1 gate text to return the file to Dana for a field Dana is not supposed to write).

**Who must fix:** Evan (update ECON-DIR1 gate text to reflect LA-4 ownership assignment). Dana must add the "do not write" note per LA-4 (Phase 4 data SOP fix).

---

### P3-E2 — `interpretation_metadata.json` field `data_provenance.input_file` uses a dated path; alias contract is missing (WARN)

**Rules involved:** DATA-D13 (stable alias maintenance), ECON-H5 producer field notes.

**Problem:** The econometrics SOP documents the `interpretation_metadata.json` schema with a `data_provenance.input_file` example of `"data/{indicator_id}_{target_id}_daily_latest.parquet"`. This correctly uses the `_latest` alias convention. However, the field notes say "records the input file and hash for reconciliation traceability" without specifying whether the recorded path must be the `_latest` alias or the dated snapshot path. Dana's SOP (DATA-D13) mandates that portals and consumers always reference `_latest` alias paths, never dated filenames. If Evan records the dated snapshot path (e.g., `hy_ig_spy_daily_20260419.parquet`) in `data_provenance.input_file`, Ace's Methodology page shows a path that does not resolve after the next data refresh. There is no explicit cross-reference in either SOP confirming which path convention applies in this field.

**Severity proposal:** WARN (the example path in the ECON SOP is correct, but the lack of an explicit rule means a future dispatch could record the dated path).

**Who must fix:** Evan — add a field note: "`data_provenance.input_file` MUST record the `_latest` alias path (e.g., `data/hy_ig_spy_daily_latest.parquet`), not the dated snapshot. This matches DATA-D13's alias convention and ensures the path remains valid after data refresh."

---

### P3-E3 — Stationarity test results handoff: Evan's mandatory CSV output vs. Dana's optional delivery (WARN)

**Rules involved:** DATA-D13 (data SOP, stationarity tests are requested by Evan and are a quality-gate checkbox), Econometrics SOP §4 Exploratory Analysis ("If Dana has already provided stationarity tests, review and confirm rather than re-running from scratch").

**Problem:** The econometrics SOP says Evan must save stationarity results to `results/{pair_id}/stationarity_tests_{YYYYMMDD}.csv` (mandatory artifact, GATE-31 FAIL if missing). The SOP also says "if Dana has already provided stationarity tests, review and confirm." Dana's SOP has a quality-gate checkbox for stationarity (included in the data dictionary delivery), but no rule specifying the file format or path at which Dana delivers stationarity results to Evan. The data SOP and econometrics SOP each describe stationarity as something the other agent may have already done, without defining who is the canonical producer and in what file. A Evan dispatch that sees Dana delivered stationarity metadata in a data dictionary (not in a `stationarity_tests_*.csv`) will not know whether that satisfies GATE-31 or whether Evan must re-run and produce the CSV independently.

**Severity proposal:** WARN (GATE-31 is Evan's gate, so Evan will re-run if the CSV is missing — but this creates redundant computation and ambiguous provenance for Ray's narrative and Quincy's verification).

**Who must fix:** Both. Data SOP should state: "Stationarity test results, when Dana runs them, are delivered in the data dictionary and in a sidecar `stationarity_notes_{pair_id}.md`. Evan owns the canonical `stationarity_tests_{YYYYMMDD}.csv` artifact at the results path." Econometrics SOP should state: "Dana's stationarity notes are informational; the canonical CSV that satisfies GATE-31 is always Evan's output."

---

### P3-E4 — `indicator_type` enum: Evan's Rule C1 uses "production" and "macro" as separate categories; Ray's indicator type classification decision tree uses the same distinction — but ECON-DIR1 and Dana's classification schema only expose 7 controlled values (WARN)

**Rules involved:** DATA-D6 / Rule D3 (data SOP, classification enum), Research SOP §4b (indicator type classification), Econometrics SOP Rule C1 (method catalog keyed on `indicator_type`).

**Problem:** The econometrics SOP Rule C1 has separate mandatory method catalogs for `indicator_type = production` and `indicator_type = macro`. Dana's Rule D3 and the schema define 7 controlled values: `price`, `production`, `sentiment`, `rates`, `credit`, `volatility`, `macro`. These are correctly aligned. However, the econometrics SOP also informally uses `activity` (e.g., "Activity/Survey" appears in §2.5 worked example 1: "ISM Manufacturing PMI (I2, Activity/Survey)") as an indicator type label alongside `production`, even though `activity` is not in the schema enum. This is the same near-synonym drift Dana's F-09 (Phase 1) flagged as a within-Evan-SOP issue. From a handoff perspective, if Ray classifies an indicator as `Activity/Survey` and Evan's Rule C1 applies the `production` method catalog but references the indicator as `activity` in communications, Dana receives ambiguous feedback when confirming classification. The handoff is informal but introduces vocabulary drift at the producer-consumer boundary.

**Severity proposal:** WARN (GATE-20 in `team-coordination.md` blocks `activity` at the schema level, so no data artifact should be affected — but the vocabulary mismatch generates avoidable confusion in cross-agent messages).

**Who must fix:** Evan — add a clarifying note in Rule C1: "Dana's schema enum uses `production` for activity/output/manufacturing indicators. Evan's informal reference to `activity` in discussion maps to `production` for classification purposes. Never write `activity` in any artifact." (Complementary to Dana's F-09 fix.)

---

### P3-E5 — CP1-B output filename includes `{pair_id}` suffix; CP2-A and CP2-B also include `{pair_id}` in filename — but the canonical bare-filename convention (VIZ-A3) requires pair_id in directory only (WARN)

**Rules involved:** DATA-D13 (stable alias and canonical path conventions), VIZ-A3 (Vera's canonical filename rule), ECON-CP1-B output path.

**Problem:** ECON-CP1-B specifies `results/{pair_id}/rolling_correlation_{pair_id}.csv` and ECON-CP2-A specifies `results/{pair_id}/rolling_sharpe_{pair_id}.csv`. These result files have `{pair_id}` embedded in the filename, not just in the directory path. This is inconsistent with VIZ-A3's canonical bare-filename convention (`output/charts/{pair_id}/plotly/{chart_type}.json`) where the pair_id lives in the directory path only. While VIZ-A3 applies directly to chart JSON files, the inconsistency creates vocabulary drift: Dana and Vera use canonical bare-name artifacts; Evan's CP series uses embedded pair_id in filenames. When Vera builds VIZ-CP1 charts from these files, her `_meta.json` `data_source_path` field will record a pair_id-embedded path, and downstream QA checks that grep for canonical bare paths may false-flag these sidecar entries.

**Severity proposal:** WARN (VIZ-A3 applies to chart files, not result CSVs, so there is no strict rule violation — but the vocabulary asymmetry will cause confusion if VIZ-A3's convention is ever extended to result artifacts).

**Who must fix:** Evan — add a comment in ECON-CP1 and CP2 output file specs: "Result CSVs use pair_id in the filename because there may be multiple pair CSVs under a shared results root; this differs from VIZ-A3's chart convention where pair_id is in the directory path only. Do not normalize to bare-name for result CSVs."

---

## Section 2 — Vera (Visualization Agent)

### P3-V1 — Data-to-Viz direct pathway: canonical names from catalog section numbers that may drift (WARN)

**Rules involved:** DATA-D13 / DATA-D12 (data SOP, canonical column naming), Visualization SOP §Handoff Pathways — Data-to-Viz: "Submit a direct request to Dana specifying: variable(s) using canonical names from `docs/data-series-catalog.md` Section 7."

**Problem:** Vera's Data-to-Viz pathway instructs Vera to reference `docs/data-series-catalog.md` Section 7 for canonical names. Dana's Phase 1 finding F-11 flagged that these cross-references use section numbers rather than anchored headings, making them fragile to catalog restructuring. This is now a cross-agent concern: Vera is actively depending on the same numbered sections. If the catalog is restructured, Vera's pathway instruction becomes stale. There is no shared convention registered in either SOP for how Vera should fall back if a section number reference fails.

**Severity proposal:** WARN (the underlying risk is low frequency but the failure mode is silent — Vera uses a renamed or moved section and retrieves wrong canonical names without noticing).

**Who must fix:** Both. Data SOP should switch references to anchored headings (F-11 fix), and Vera's Data-to-Viz pathway should be updated to match (referencing anchored headings rather than section numbers).

---

### P3-V2 — Direction check against `interpretation_metadata.json`: Vera expects Evan's field, but the file may not exist yet at chart-production time for exploratory pairs (WARN)

**Rules involved:** DATA-D6 (data SOP, `interpretation_metadata.json` producer and content), Visualization SOP §Data Ingestion Validation item 6: "Check the Direction Convention. Read Dana's data dictionary for the Direction Convention or sign convention of each indicator. Cross-reference against Evan's `interpretation_metadata.json`."

**Problem:** Vera's Data Ingestion Validation step 6 says to cross-reference Dana's data dictionary against "Evan's `interpretation_metadata.json`". After LA-4, the observed_direction field in that file is Evan's (post-tournament). For exploratory pairs or early-stage deliveries where Evan has not yet run the tournament, `interpretation_metadata.json` may not exist or may have `observed_direction` absent. Vera's step 6 does not specify a fallback when the file is missing or the field is absent. Additionally, Vera's SOP describes the file as produced by "Evan" in step 6 but other parts of the Vera SOP say it is produced by "Evan" generally — the data SOP previously attributed some fields to Dana. After LA-4 settles this, Vera's step 6 language should be explicit that the file's direction field is Evan's and what the fallback is when it is absent.

**Severity proposal:** WARN (Vera already has a "when in doubt, ask" fallback in step 7 — but it applies to column meaning, not to a missing upstream file; the gap is the absence of an explicit fallback for a missing `interpretation_metadata.json`).

**Who must fix:** Vera — add to step 6: "If `interpretation_metadata.json` does not yet exist or `observed_direction` is absent (pair not yet through tournament), use Dana's data dictionary `Direction Convention` column exclusively. Do not block chart production on a missing file; note the absence in the handoff note."

---

### P3-V3 — VIZ-HZE1 reads `docs/schemas/episode_registry.json` for required slugs, but the canonical registry post-LA-1 is `docs/schemas/history_zoom_events_registry.json` — cross-ref is wrong (FAIL)

**Rules involved:** LA-1 (Lead arbitration: `history_zoom_events_registry.json` is canonical; `episode_registry.json` is deprecated), VIZ-HZE1 Mandatory pre-handoff gate step 1: "Read `docs/schemas/episode_registry.json`, find the entry keyed on the pair's `interpretation_metadata.indicator_category`."

**Problem:** This is a direct cross-reference integrity failure triggered by LA-1. VIZ-HZE1's pre-handoff gate explicitly reads `episode_registry.json` to identify required slugs. LA-1 says `history_zoom_events_registry.json` is canonical and `episode_registry.json` is deprecated. If a Vera dispatch follows the VIZ-HZE1 gate text verbatim after LA-1 lands, she reads the wrong (deprecated) registry. This also cascades: the VIZ-ZOOM1 "Episode slug names" field says "dotcom, gfc, covid, inflation_2022" but its "Episode selection for zoom charts" section says "Read from `docs/schemas/episode_registry.json`" — same conflict. Both rules must be retargeted to the canonical registry.

**Severity proposal:** FAIL (a Vera dispatch following the VIZ-HZE1 gate after Phase 4 will read a deprecated registry; this can cause slug mismatches and missed required charts).

**Who must fix:** Vera — Phase 4 fix for VIZ-HZE1 and VIZ-ZOOM1: replace all `episode_registry.json` references with `history_zoom_events_registry.json` and the keying structure it uses. (This is a direct Phase 4 consequence of LA-1.)

---

### P3-V4 — `chart_manifest.json` vs `_meta.json` per chart: Ace's "Inputs I Need" section references a chart manifest at `output/charts/chart_manifest.json`, but Vera's SOP defines individual `_meta.json` sidecars per chart and a separate `output/chart_registry.json` — three different registry artifacts (WARN)

**Rules involved:** DATA-D13 (manifest/registry naming conventions, data SOP), VIZ-O1 / VIZ-SD1 (Vera's per-chart `_meta.json` sidecar), Visualization SOP "Chart Registry (Multi-Pair Scale)" at `output/chart_registry.json`, AppDev SOP "From Visualization Agent" section: "Chart manifest (`output/charts/chart_manifest.json`): Vera produces and maintains this."

**Problem:** There are three distinct registries referenced across the Vera and Ace SOPs:
1. `_meta.json` — per-chart sidecar (Vera's SOP, VIZ-O1/VIZ-SD1)
2. `output/chart_registry.json` — multi-pair registry (Vera's SOP, "Chart Registry" section)
3. `output/charts/chart_manifest.json` — referenced in Ace's "From Visualization Agent" inputs section

None of these three match in naming. Ace's inputs section says `chart_manifest.json` is what Vera produces to allow programmatic chart discovery. Vera's SOP says the registry is at `output/chart_registry.json`. It is unclear whether these are the same file under different names, or two distinct files. If different, Ace is waiting for a file Vera's SOP does not commit to produce. If the same, the name conflict will cause a future dispatch to produce the wrong file or skip one.

**Severity proposal:** WARN (the chart loading works via `load_plotly_chart()` and per-chart canonical paths, so the registry is secondary — but the naming conflict means a Vera dispatch maintaining "the chart manifest" could update the wrong file).

**Who must fix:** Both. Vera should standardize on a single multi-pair registry file name (either `output/chart_registry.json` per her SOP or `output/charts/chart_manifest.json` per Ace's SOP) and state it explicitly. Ace should confirm which file she reads.

---

### P3-V5 — Vera's Data-to-Viz pathway says "Dana delivers with the same quality gates as Econ handoffs" — but the quality-gate checklist for data-direct deliveries is not defined in either SOP (WARN)

**Rules involved:** DATA-D13 / DATA-VS (data SOP quality gates), Visualization SOP §Data-to-Viz: "Dana delivers with the same quality gates as Econ handoffs."

**Problem:** The Vera SOP's Data-to-Viz pathway says Dana's direct-to-Vera deliveries carry "the same quality gates as Econ handoffs." The Econ handoff gates are Evan's ECON-H4 per-method table, ECON-H5 `winner_summary.json`, manifest assertions, etc. — all of which are model-output-specific and not applicable to raw exploratory data charts. Dana's SOP defines its own quality gates (DATA-D5, DATA-D6, DATA-D12, DATA-D13) for data deliveries, which are different from Evan's handoff gates. The phrase "same quality gates as Econ handoffs" sets a false equivalency and gives Vera no actionable gate checklist for direct-from-Dana chart requests.

**Severity proposal:** WARN (in practice both agents have working gate procedures; the concern is a future dispatch reading Vera's SOP and expecting ECON-H4/H5 artifacts from Dana that Dana does not produce).

**Who must fix:** Vera — replace "with the same quality gates as Econ handoffs" with: "with a manifest sidecar per Defense 1, canonical column names per DATA-D12, and a data dictionary that includes Display Names and Direction Convention. Verify per Data Ingestion Validation steps 1–7 above."

---

## Section 3 — Ray (Research Agent)

### P3-R1 — Ray reads `indicator_nature` and `indicator_type` from Dana's `interpretation_metadata.json` for narrative — but these fields are Dana-owned per DATA-D6, and Ray's SOP does not reference DATA-D6 or acknowledge the producer contract (WARN)

**Rules involved:** DATA-D6 (data SOP, indicator_nature and indicator_type are Dana's blocking classification fields), Research SOP §6e ("Dana owns `indicator_nature` and `indicator_type`… Ray owns `strategy_objective`").

**Problem:** The research SOP §6e correctly states that Dana owns `indicator_nature` and `indicator_type`. However, the research SOP's direction determination workflow (§6b), classification decision tree (§4b), and narrative quality rules (RES-EGL1) all reference these fields as inputs Ray reads from metadata, without a formal cross-reference to DATA-D6 as the rule that governs their production. Ray's §4b has its own indicator type classification decision tree that Ray applies when writing a brief — but this classification is advisory for Evan; the canonical classification written to the artifact is Dana's per DATA-D6. There is no rule in the research SOP stating "Ray's §4b classification is a recommendation to Dana; the canonical `indicator_type` written to `interpretation_metadata.json` is always Dana's output per DATA-D6 — if they differ, Ray flags the disagreement in the handoff note rather than overwriting."

**Severity proposal:** WARN (in practice, Dana classifies first and Ray inherits the classification for narrative; but a Ray dispatch that applies §4b independently and finds a different answer has no defined procedure for resolving the conflict).

**Who must fix:** Research SOP (Ray) — add a note to §4b: "Ray's indicator type classification is a recommendation delivered in the research brief for Dana's review. The canonical `indicator_type` and `indicator_nature` values written to `interpretation_metadata.json` are Dana's responsibility per DATA-D6. If Ray's classification recommendation differs from Dana's assigned value, flag the disagreement in the Ray-to-Evan handoff note; do not rewrite or re-classify the field in the narrative."

---

### P3-R2 — RES-EGL1 says Ray checks `direction_consistent`, `observed_direction`, `expected_direction` against "Dana-produced interpretation metadata" — but post-LA-4, `observed_direction` is Evan's field (FAIL)

**Rules involved:** LA-4 (Lead arbitration: Evan owns `observed_direction`), Research SOP RES-EGL1 item 1: "Any sentence saying an indicator 'rises,' 'falls,'… must be checked against `expected_direction`, `observed_direction`, `direction_consistent`,… as Dana-produced interpretation metadata."

**Problem:** After LA-4, `observed_direction` is produced by Evan, not Dana. RES-EGL1 item 1 explicitly calls it "Dana-produced interpretation metadata," which will be wrong after Phase 4. A Ray dispatch reading RES-EGL1 post-Phase-4 will believe Dana is responsible for `observed_direction` and return mismatch notes to Dana for a field Dana is not supposed to write.

**Severity proposal:** FAIL (direct producer attribution error, same severity class as ECON-DIR1 in P3-E1 above; the two errors have a common root in the three-way conflict resolved by LA-4).

**Who must fix:** Research SOP (Ray) — Phase 4 fix: update RES-EGL1 item 1 to attribute `observed_direction` to Evan and `indicator_nature`/`indicator_type` to Dana. Suggested replacement: "…checked against `expected_direction` and `observed_direction` as Evan-produced fields (ECON-DIR1), and `indicator_nature` / `indicator_type` as Dana-produced fields (DATA-D6)."

---

### P3-R3 — RES-HZE1 reads `docs/schemas/episode_registry.json` — same post-LA-1 cross-ref failure as P3-V3 (FAIL)

**Rules involved:** LA-1 (Lead arbitration: `history_zoom_events_registry.json` is canonical; `episode_registry.json` is deprecated), Research SOP RES-HZE1 pre-handoff validation step 1: "Open `docs/schemas/episode_registry.json`."

**Problem:** Identical to P3-V3 for Vera. RES-HZE1's slug verification step reads the deprecated registry. After LA-1, any Ray dispatch following the RES-HZE1 verification step will validate slugs against the wrong file.

**Severity proposal:** FAIL (same severity as P3-V3 — a blocking pre-handoff validation step points to a deprecated file after a binding Lead arbitration).

**Who must fix:** Research SOP (Ray) — Phase 4 fix: replace `episode_registry.json` reference in RES-HZE1 step 1 with `history_zoom_events_registry.json`. (Coordinated with Vera's P3-V3 fix under LA-1 sequencing.)

---

### P3-R4 — Ray's narrative frontmatter `direction_asserted` is validated against `winner_summary.json.direction` — but `winner_summary.json` uses a `direction` field that post-LA-4 is set by Evan from `observed_direction`; the chain of provenance is not documented in the research SOP (WARN)

**Rules involved:** RES-17 (research SOP: `direction_asserted` MUST match `winner_summary.json.direction` per APP-DIR1), ECON-H5 (Evan's SOP: `winner_summary.json.direction` is the canonical APP-DIR1 enum), DATA-D6 (data SOP: silent on `observed_direction` prior to Phase 4 fix).

**Problem:** RES-17 says Ray validates `direction_asserted` against `winner_summary.json.direction`. ECON-H5 says `winner_summary.json.direction` is set by Evan from the tournament winner's direction. After LA-4, `interpretation_metadata.json.observed_direction` is also Evan's field, and `winner_summary.json.direction` should match it per ECON-DIR2. The full chain is: Evan sets `observed_direction` in `interpretation_metadata.json` → Evan copies the direction into `winner_summary.json.direction` → Ray reads `winner_summary.json.direction` to set `direction_asserted` in frontmatter. This chain is coherent but documented only piecemeal across three SOPs. Ray's SOP does not state the origin of `winner_summary.json.direction` or warn Ray that if `interpretation_metadata.json.observed_direction` and `winner_summary.json.direction` ever disagree, there is a ECON-DIR2 violation upstream that Ray must escalate rather than arbitrate.

**Severity proposal:** WARN (the chain works when all agents follow their rules, but without a documented chain Ray has no defined escalation path when the two direction fields disagree).

**Who must fix:** Research SOP (Ray) — add a note to RES-17: "Ray reads `direction_asserted` from `winner_summary.json.direction`. If `winner_summary.json.direction` disagrees with `interpretation_metadata.json.observed_direction`, this is an ECON-DIR2 violation owned by Evan. Ray escalates to Evan before committing `direction_asserted`; Ray does not arbitrate the disagreement."

---

### P3-R5 — Ray's handoff to Dana: data source table with "Unconfirmed" availability flag has no defined Dana response protocol in the data SOP (WARN)

**Rules involved:** Data SOP (no rule for intake of Ray's Unconfirmed availability flags), Research SOP §4 Data Feasibility Check: "mark explicitly as `Availability: UNCONFIRMED — Dana to verify` and suggest an alternative if possible."

**Problem:** Ray's research brief includes a Recommended Data Sources table with an `Availability` column. Rows marked `UNCONFIRMED` are flagged for Dana to verify. Dana's SOP has no corresponding intake rule: no rule stating that when Dana receives a brief with Unconfirmed rows, Dana (a) attempts to verify, (b) reports back to Ray within a defined time, or (c) escalates if the series is not accessible through the MCP stack. Without an intake rule, UNCONFIRMED rows may silently block the data pull or be quietly skipped when the series is inaccessible, without Ray or Evan knowing.

**Severity proposal:** WARN (this is a missing handoff rather than a schema mismatch; the risk is silent data omission on hard-to-source series).

**Who must fix:** Data SOP (Dana) — add to the Receive Brief or Data Pull procedure: "When Ray's brief contains rows marked `Availability: UNCONFIRMED`, Dana attempts to verify through the MCP stack (FRED, Yahoo, Alpha Vantage, Financial Datasets). If verification succeeds, Dana proceeds. If the series is inaccessible, Dana reports the failure to Ray and Evan in the handoff note within one task cycle; the series is not silently omitted from the delivery."

---

## Section 4 — Ace (App Dev Agent)

### P3-A1 — Ace reads `interpretation_metadata.json` fields `indicator_nature`, `indicator_type`, `strategy_objective`, and `direction` from Dana's output — but these have mixed producer ownership that is not stated in Ace's "From Data Agent" section (FAIL)

**Rules involved:** DATA-D6 (data SOP: Dana owns `indicator_nature` and `indicator_type`), Research SOP §6e (Ray owns `strategy_objective`), LA-4 (Evan owns `observed_direction`), AppDev SOP "Landing Page Design Rules §6 Metadata source": "These classifications come from `interpretation_metadata.json`."

**Problem:** Ace's landing page metadata section says all four classification fields (`indicator_nature`, `indicator_type`, `strategy_objective`, `direction`) come from `interpretation_metadata.json`. The ownership is split: `indicator_nature` and `indicator_type` are Dana's (DATA-D6); `strategy_objective` is Ray's (Research SOP §6e); `direction` / `observed_direction` is Evan's (LA-4). Ace's SOP treats the entire file as coming from a single upstream without naming the field-level producers. If one producer is late or a field is absent, Ace has no defined protocol for which producer to contact. The "From Data Agent" section in Ace's inputs also does not mention `interpretation_metadata.json` explicitly — it mentions the data dictionary and stable `_latest` alias paths only.

**Severity proposal:** FAIL (multi-producer file with no producer attribution in the consumer SOP creates a silent missing-field risk and an ambiguous escalation path when a field is absent).

**Who must fix:** Ace SOP — Phase 4: update "Landing Page Design Rules §6 Metadata source" and "From Data Agent" / "From Econometrics Agent" / "From Research Agent" inputs sections to attribute each field to its producer: `indicator_nature` / `indicator_type` → Dana (DATA-D6); `strategy_objective` → Ray (§6e); `direction` → Evan (ECON-H5 / LA-4). Add escalation paths: "If a field is absent, contact the owning producer. Do not infer or default to 'Unknown' without attempting to retrieve the field from the correct source first."

---

### P3-A2 — Ace's `_latest` alias requirement for data file paths is stated in the inputs section but not cross-referenced to Dana's DATA-D13 rule (WARN)

**Rules involved:** DATA-D13 (data SOP: stable alias maintenance, `_latest` alias is canonical path for consumers), AppDev SOP "From Data Agent": "Data file locations and formats (parquet/CSV in `data/`) at stable `_latest` alias paths. Portal code references `_latest` aliases, never dated filenames."

**Problem:** Ace's requirement is correctly stated — portal code must use `_latest` aliases. However, the Ace SOP does not cross-reference DATA-D13 as the producer-side rule that guarantees these aliases exist and are maintained. If Ace receives a data file at a dated path (e.g., in a mid-analysis expedited delivery), Ace's SOP gives no guidance on whether to block, request the alias from Dana, or proceed with the dated path. DATA-D13 says Dana must maintain the alias but does not address the consumer side's response to a dated-path delivery.

**Severity proposal:** WARN (in steady state, Dana produces `_latest` aliases; the gap is the missing response protocol for edge cases like expedited deliveries or legacy pairs).

**Who must fix:** Ace SOP — add a cross-reference note: "Portal code MUST reference `_latest` alias paths per DATA-D13. If a data delivery arrives at a dated path rather than a `_latest` alias, request the alias from Dana before integrating the file into portal code. Do not hardcode dated filenames in `app/` code." Data SOP (DATA-D13) — add: "For expedited deliveries, Dana still creates the `_latest` alias before or immediately after the expedited file delivery; the handoff note confirms the alias path."

---

### P3-A3 — Ace's APP-LP8 evidence-status default (`found_in_search`) for missing `evidence_status.json` is not cross-referenced to ECON-FE1 or to Dana's data SOP — Dana has no hook (WARN)

**Rules involved:** ECON-FE1 (Evan SOP: final-exam confirmation contract), GATE-ES1 (QA SOP: evidence-status promotion verification), APP-LP8 (AppDev SOP §8 Evidence-status honesty label: "Missing files… default to `found_in_search`"), Data SOP (no mention of evidence-status at all — Dana F-14 in Phase 1).

**Problem:** APP-LP8 correctly defaults missing `evidence_status.json` to `found_in_search`. ECON-FE1 says the file's `final_exam.qa_status` field must be `"qa_passed"` for `passed_final_exam` status. GATE-ES1 says Quincy verifies the promotion. Dana's data SOP (as F-14 noted) has no hook for any of this. The data SOP does not mention that for final-exam-qualifying pairs, the data delivery must document the in-sample/OOS boundary clearly (linking to `oos_split_record.json` per ECON-OOS1). Ace reads `evidence_status.json` for rendering; if Evan or Quincy cannot trace sample separation to Dana's data provenance, the final-exam promotion may fail on data-layer grounds that Dana was never informed about. This is the same cross-chain gap Lead noted in B3 of Phase 2.

**Severity proposal:** WARN (no current pair has reached `passed_final_exam` status, so no immediate blocking effect — but the chain is incomplete before the first pilot final-exam, as Lead noted in B3).

**Who must fix:** Data SOP (Dana) — per F-14 deferred item: add a brief cross-reference in §6 Deliver: "For pairs that may advance to ECON-FE1 final-exam confirmation, ensure the delivered dataset clearly documents the in-sample/OOS boundary per `results/{pair_id}/oos_split_record.json` (ECON-OOS1) so the sample separation claim in ECON-FE1 is traceable to data provenance." (This was already identified in Phase 1 F-14 as an advisory note; confirming it as a WARN after reviewing the ECON-FE1/GATE-ES1/APP-LP8 chain in Phase 3.)

---

### P3-A4 — Ace's `display_name_registry` / Display Names input expectation is not fully specified: the data SOP uses `display_name_registry.json` (DATA-D6b), but Ace's inputs section says "data dictionary Display Name column" (different format/file) (WARN)

**Rules involved:** DATA-D6b (data SOP: user-facing text field lint, references `display_name_registry.json`), DATA-D13 (data SOP: manifest + display-name registry bootstrap), AppDev SOP "From Data Agent": "Data dictionary for any series displayed in the portal — must include Display Name column."

**Problem:** Ace's inputs section expects Display Names from the "data dictionary Display Name column" (a tabular format). Dana's DATA-D6b and DATA-D13 refer to a `display_name_registry.json` file as the authoritative source for Display Names. There is also a `data/display_name_registry.json` referenced in team-coordination.md. These are not clearly the same artifact as the data dictionary Display Name column. A Vera or Ace dispatch that requests the "data dictionary Display Name column" may receive a tabular CSV entry, while Dana's SOP commitment is to maintain a JSON registry at a canonical path. If the JSON registry is the authoritative source and the dictionary column is derived from it, the relationship and the canonical path should be explicitly stated in both SOPs.

**Severity proposal:** WARN (in practice, both formats likely cover the same information — but the inconsistency in artifact name and format could cause a Vera or Ace dispatch to look for the column in the wrong place or request a format Dana does not maintain as the primary artifact).

**Who must fix:** Data SOP (Dana) — state in the §6 Deliver section: "Display Names are maintained in `data/display_name_registry.json` (DATA-D6b, DATA-D13). The data dictionary delivered to Vera and Ace includes a Display Name column populated from this registry. The registry is the authoritative source; the dictionary column is derived."

---

## Section 5 — Quincy (QA Agent)

### P3-Q1 — Quincy's direction triangulation (APP-DIR1) checks `interpretation_metadata.observed_direction` against the narrative — but post-LA-4, this field is Evan's; the QA SOP still attributes it to Dana by implication (WARN)

**Rules involved:** LA-4 (Lead: Evan owns `observed_direction`), QA SOP §Cross-Agent Seam Audit: "Direction triangulation (APP-DIR1): `winner_summary.direction` (Evan) == `interpretation_metadata.observed_direction` (Dana) == `narrative_frontmatter.direction_asserted` (Ray)."

**Problem:** The QA SOP's direction triangulation explicitly labels `interpretation_metadata.observed_direction` as "(Dana)". After LA-4, this is wrong. A Quincy dispatch reading the seam audit section will assign the finding to Dana when a mismatch is detected, when in fact the fix owner is Evan. This mislabeling will generate incorrect producer-blame assignments and wrong fix routing in QA findings.

**Severity proposal:** WARN (the triangulation check itself is correct; only the producer attribution is wrong — but mislabeled findings waste a fix cycle).

**Who must fix:** QA SOP (Quincy) — Phase 4: update the direction triangulation line to attribute `interpretation_metadata.observed_direction` to Evan, not Dana: "`winner_summary.direction` (Evan) == `interpretation_metadata.observed_direction` (Evan, per ECON-DIR1 / LA-4) == `narrative_frontmatter.direction_asserted` (Ray)."

---

### P3-Q2 — GATE-VIZ-NBER2's episode slug table uses `dot_com` and `rates_2022` — non-canonical slugs after LA-2 (FAIL)

**Rules involved:** LA-2 (Lead: canonical slug set is `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`; `dot_com`, `rates_2022`, `taper_2013` are non-canonical and forbidden), QA SOP GATE-VIZ-NBER2 episode-window overlap table: slug column uses `dot_com`, `taper_2013`, `china_2015`, `rates_2022`.

**Problem:** GATE-VIZ-NBER2's hardcoded episode-slug table uses the pre-LA-2 non-canonical slugs: `dot_com` (should be `dotcom`), `taper_2013` (non-canonical under LA-2 — Vera must author a registry PR to include or remove), `china_2015` (same), `rates_2022` (should be `inflation_2022`). After LA-2, a Quincy dispatch running GATE-VIZ-NBER2 will compare against slugs that don't exist in the canonical registry, causing every recession-overlap check to false-PASS (no chart found under deprecated slug → no shading required → PASS). The lead also specified this exact update for Quincy in LA-2 item 5.

**Severity proposal:** FAIL (the slug mismatch directly undermines the NBER shading check; a false-PASS on recession shading is the same failure class GATE-VIZ-NBER2 was designed to prevent).

**Who must fix:** QA SOP (Quincy) — Phase 4: update GATE-VIZ-NBER2 slug table to use canonical slugs per LA-2: replace `dot_com` → `dotcom`, `rates_2022` → `inflation_2022`. Retain `gfc` and `covid` (already canonical). Remove `taper_2013` and `china_2015` pending Vera's registry PR (LA-2 disposition: "need explicit registry promotion or removal").

---

### P3-Q3 — Quincy verifies DATA-D6 (interpretation metadata) and DATA-D11 (reference-pair sidecar) in cross-references but DATA-D6b (user-facing text fields) is not listed as a QA verification target despite being a blocking rule with a named gate (GATE-NR) (WARN)

**Rules involved:** DATA-D6b (data SOP: user-facing text fields lint, GATE-NR enforced by Quincy per QA-CL5/GATE-NR), QA SOP cross-references at the end of the document: "DATA-D6 / DATA-D11 — interpretation metadata schema + reference-pair sidecar (QA validates)."

**Problem:** The QA SOP's cross-references section lists DATA-D6 and DATA-D11 as rules QA validates, but omits DATA-D6b. Yet the QA SOP's QA-CL5/GATE-NR section is explicitly named as the enforcement point for DATA-D6b's user-facing text field lint ("Quincy's GATE-NR DOM scan now includes this check" per data SOP DATA-D6b). The cross-reference table is incomplete: DATA-D6b should appear alongside DATA-D6 and DATA-D11 as a QA-validated rule. As an unregistered finding from Phase 1 (F-04, F-05), this is also a standards.md registration gap — but the immediate cross-ref concern is that a Quincy dispatch checking the cross-references section to determine which DATA rules to verify would not find DATA-D6b listed.

**Severity proposal:** WARN (GATE-NR exists and is documented in QA-CL5; the gap is that DATA-D6b is not listed in the cross-reference inventory, making the linkage harder to discover).

**Who must fix:** QA SOP (Quincy) — add DATA-D6b to the cross-references section: "DATA-D6b — user-facing text fields lint (QA verifies via GATE-NR DOM scan, per QA-CL5)." Complementary to DATA-D6b's registration in `docs/standards.md` (LA-5 batch update).

---

### P3-Q4 — QA-CL1 checklist has no explicit item for verifying Dana's DATA-D13 manifest freshness or display_name_registry coverage (WARN)

**Rules involved:** DATA-D13 (data SOP: manifest + display-name registry — blocking gate for reference pairs), QA SOP QA-CL1 standard checklist (no DATA-D13 line item).

**Problem:** QA-CL1 lists direction triangulation (APP-DIR1), schema validation (META-CF), smoke tests, DOM read (HABIT-QA1), and several other cross-agent gate checks. However, there is no checklist item for verifying that `data/manifest.json` is fresh and covers the current pair universe, or that `data/display_name_registry.json` has entries for every variable rendered in the portal. DATA-D13 is a blocking gate (reference-pair blocking) that Dana self-certifies in her handoff note. Quincy has no explicit QA-CL1 item requiring independent verification of the manifest. If Dana's self-certification is wrong, the gap is only caught incidentally (e.g., when a portal label shows a raw column code instead of a Display Name).

**Severity proposal:** WARN (Quincy's seam audit would likely catch a Display Name regression through the DOM check, but there is no explicit manifest freshness gate in QA-CL1 that provides systematic coverage).

**Who must fix:** QA SOP (Quincy) — add a QA-CL1 item: "[ ] DATA-D13 manifest/display-name registry check: confirm `data/manifest.json` covers all active pairs in this wave's scope and `data/display_name_registry.json` has entries for every portal-rendered variable. Verify via `grep` against the pair's parquet column list; absence of a column's Display Name entry is a WARN."

---

## Summary of Findings

| ID | Peer Agent | Severity | Theme |
|----|-----------|----------|-------|
| P3-E1 | Evan | FAIL | ECON-DIR1 gate text implies Dana produces `observed_direction` (overridden by LA-4) |
| P3-E2 | Evan | WARN | `data_provenance.input_file` lacks explicit `_latest` alias requirement |
| P3-E3 | Evan + Dana | WARN | Stationarity test producer/path ambiguity between data SOP and ECON gate |
| P3-E4 | Evan | WARN | `activity` near-synonym still used informally in ECON SOP vs schema enum |
| P3-E5 | Evan | WARN | CP1-B/CP2-A/CP2-B result filenames embed pair_id inconsistently with VIZ-A3 |
| P3-V1 | Vera | WARN | Data-to-Viz pathway references catalog by section number, same drift risk as F-11 |
| P3-V2 | Vera | WARN | No fallback when `interpretation_metadata.json` is absent at chart-production time |
| P3-V3 | Vera | FAIL | VIZ-HZE1 reads deprecated `episode_registry.json` (LA-1 makes this wrong) |
| P3-V4 | Vera + Ace | WARN | Three different chart registry artifact names across two SOPs |
| P3-V5 | Vera | WARN | "Same quality gates as Econ handoffs" phrase is inaccurate for Dana-direct deliveries |
| P3-R1 | Ray | WARN | Ray's §4b classification decision tree lacks a stated producer-arbitration rule vs. Dana |
| P3-R2 | Ray | FAIL | RES-EGL1 attributes `observed_direction` to Dana (overridden by LA-4) |
| P3-R3 | Ray | FAIL | RES-HZE1 reads deprecated `episode_registry.json` (LA-1 makes this wrong) |
| P3-R4 | Ray | WARN | Ray's direction chain from `winner_summary.json.direction` not documented end-to-end |
| P3-R5 | Ray + Dana | WARN | No Dana intake rule for Ray's `UNCONFIRMED` data availability flags |
| P3-A1 | Ace | FAIL | `interpretation_metadata.json` treated as single-producer in Ace SOP; producer-per-field missing |
| P3-A2 | Ace + Dana | WARN | `_latest` alias requirement not cross-referenced to DATA-D13 |
| P3-A3 | Ace + Dana | WARN | Final-exam chain (ECON-FE1/GATE-ES1/APP-LP8) has no Dana data-provenance hook |
| P3-A4 | Ace + Dana | WARN | Display Name artifact name conflict: registry JSON vs. data dictionary column |
| P3-Q1 | Quincy | WARN | Direction triangulation (APP-DIR1) mislabels `observed_direction` as Dana's post-LA-4 |
| P3-Q2 | Quincy | FAIL | GATE-VIZ-NBER2 slug table uses non-canonical slugs forbidden by LA-2 |
| P3-Q3 | Quincy | WARN | DATA-D6b not listed in QA cross-references despite GATE-NR being Quincy's gate |
| P3-Q4 | Quincy | WARN | No QA-CL1 item for DATA-D13 manifest freshness / display_name_registry coverage |

**Total: 23 findings. FAIL: 5 (P3-E1, P3-V3, P3-R2, P3-R3, P3-A1, P3-Q2 — actually 6 FAIL; see table above). WARN: 17.**

**Top 3 themes:**
1. **LA-4 propagation deficit** — four SOPs (ECON-DIR1 gate, RES-EGL1, QA-APP-DIR1, and APP-LP8 attribution) still attribute `observed_direction` to Dana after Lead's binding arbitration. All four need Phase 4 updates.
2. **LA-1/LA-2 propagation deficit** — three SOPs (VIZ-HZE1, RES-HZE1, GATE-VIZ-NBER2) still reference the deprecated `episode_registry.json` or use non-canonical slug names. These must be updated coordinately in Phase 4.
3. **Missing crossover handoff rules** — several producer-consumer boundaries lack a defined protocol when an expected artifact is missing, delayed, or formatted unexpectedly (Ray's UNCONFIRMED flags → Dana, Dana's `_latest` aliases → Ace, `interpretation_metadata.json` multi-producer → Ace).

---

*Phase 3 cross-review complete. 23 handoff findings across 5 peer agents. No SOP edits made (LEAD-DL1 respected).*
