# Cross-Review 2026-04-19 — Data Dana

**Reviewer:** Data Dana
**Scope:** Boundary contracts with Evan, Vera, Ray, Ace.
**Trigger:** Lesandro — "most recent bugs came from rapport among agents."
**Inputs read (read-only):** data-agent-sop.md, econometrics-agent-sop.md, visualization-agent-sop.md, research-agent-sop.md, appdev-agent-sop.md, standards.md.

Dana is upstream of almost everyone. The boundary surface is narrow (I mostly emit, rarely consume) but it is high-fan-out: one metadata decision by me propagates into Evan's method routing, Vera's axes, Ray's dual notation, and Ace's landing page. That is exactly where the recent bugs (Wave-1.5 DATA-VS, Wave-2A unit 100x) came from, so the audit focuses on metadata clarity more than on data flow.

---

## 1. Artifacts Dana produces for other agents

| Artifact path | Consumer | Contract rule ID | Schema explicit? | Failure mode when missing/invalid | Test/gate | Known gaps |
|---|---|---|---|---|---|---|
| `data/{subject}_{freq}_{start}_{end}.parquet` (dated master) | Evan | DATA-H1, META-D1 | Partial — canonical column names (D2 suffixes), but no machine-readable schema file | Silent column drop between reruns; wrong unit propagates to every method | DATA-D1 column-diff, DATA-Q1 | No JSON schema sidecar; suffix convention not machine-enforced |
| `data/{subject}_{freq}_latest.{ext}` (stable alias) | Evan, Ace, Vera (reruns) | DATA-H1, §6 Deliver | Yes — alias protocol | Portal breakage on rename; Evan rerun loads stale columns | DATA-D1, `data/manifest.json` | Alias contract not versioned (no schema_version field) |
| `data/manifest.json` | Ace (cache TTL), Lead | §6 Deliver | Yes (4-field schema in SOP) | Mixed-freq TTL misconfig → stale portal data | None automated | No validator; hand-maintained |
| `data/display_name_registry.csv` | Vera, Ace | §6 Deliver | Yes (4 columns: column_name, display_name, unit, axis_label) | Vera falls back to column codes as axis labels | DATA-DD1 (implicit) | **No integrity check that every column shipped in a parquet has a registry entry.** Axis labels can lag silently behind new columns. |
| `data/data_dictionary_*.csv` / `.md` | Evan, Vera, Ray, Ace | DATA-DD1 | Yes (15 mandatory fields) | Direction Convention / Effective Start / Unit field missing → misinterpretation downstream | DATA-Q1 | Not machine-validated against the parquet it describes; drift possible |
| `results/{id}/interpretation_metadata.json` (Dana-owned fields only: `indicator_nature`, `indicator_type`, `known_stress_episodes`, `data_provenance`) | Evan (routing), Vera (encoding), Ace (landing filter), Ray (narrative) | DATA-D3, DATA-DD4, META-CFO, GATE-19/20 | Yes — controlled 7-value vocab for `indicator_type`, 3-value for `indicator_nature` | Invalid enum → landing page filter silently drops pair; Evan's Rule C1 can't route | GATE-19, GATE-20, META-UNK | Vocabulary is documented but not validated by a pre-handoff linter; META-UNK relies on human review |
| `results/{id}/interpretation_metadata.json` (classification-metadata schema) | Ace (landing card chips), Ray (narrative), Vera | META-CFO, APP-LP5, APP-LP6 | Partial — Dana's `indicator_nature`/`indicator_type` documented; Ray's `strategy_objective` documented; **no schema contract that lists all required fields of the merged JSON** | Card renders with "Unknown"; integrity warning triggers | GATE-19/20/21, APP-LP7 | **No single canonical schema file** — fields grew over time (indicator_nature, indicator_type, strategy_objective) without a versioned contract. Next field addition will repeat this. |
| Stationarity results table (in handoff message or sidecar) | Evan | DATA-DD3 | Yes (structured format in SOP §5) | Evan re-runs from scratch, may disagree silently | DATA-DD3 | Not written as a file — lives in handoff prose; hard to audit post-hoc |
| Status-type labels (`_status` columns, README text) | Ray, Ace | DATA-VS | Yes — canonical 7-value list | Novel term leaks into narrative / portal | DATA-VS (added Wave 1.5) | Self-check only, no automated linter |
| Derived series (`hy_ig_oas_bps`, `vix_vix3m_ratio`, etc.) | Evan, Vera | §6 Rule D2, §5 derived verification | Yes — computation recipe in data-series-catalog §7.10 | Wrong computation (unit bug!) propagates invisibly | Reference-date verification per §5 | **Verification is opt-in prose, not a gate-blocking diff vs reference value** |
| Days-since-release columns | Evan (staleness modeling) | §5 | Yes | Evan can't model staleness | None | Opt-in ("optionally include") — inconsistent across pairs |
| Benchmark series (SPY returns, AGG returns, buy-and-hold) | Ace (Strategy page), Evan (backtest) | DATA-DD2 | Partial | Ace sources own benchmark, potential divergence | DATA-Q1 | No schema for the benchmark columns themselves |

---

## 2. Artifacts Dana consumes from other agents

Dana's upstream surface is minimal and that is correct.

| Artifact | Producer | Contract | Failure mode | Gap |
|---|---|---|---|---|
| Analysis Brief (data request section) | Lead / Ray | RES-B1, META-P0 | Ambiguous source, frequency, or SA status → wrong series pulled | Data Request Template (SOP §1) lists 9 fields but **only 7 are enforced**. "Acceptable proxies" and "Stationarity tests needed" are skipped when Ray batches a Light brief. |
| Mid-analysis expedited data request | Evan | DATA-E1, ECON-M1 | Out-of-cycle column arrives without updating data dictionary | Expedited protocol defers quality gates "to next consolidated delivery" — that consolidation never gets scheduled. |
| Research brief's data source table (FRED IDs, frequency, SA) | Ray | RES-B1, §6 data-to-econ handoff | Ray recommends source that has no MCP path → round-trip | §Non-MCP Sourcing Protocol covers this, but the **round-trip back to Ray is not structured** — tends to be ad-hoc DM. |
| Contradiction note (direction flip) | Ray | RES-B4 | Dana does not currently act on these — they are for Evan/Vera | No gap for Dana specifically, but worth noting Dana may need to add a "known direction quirk" flag to the data dictionary when Ray files one. |

---

## 3. Decisions Dana makes that affect other agents

Decisions where a wrong or silent choice by Dana propagates widely:

1. **Unit convention (bps vs %, ratio vs pct, raw vs log)** — DATA-D2 registry. **This is the Wave-2A failure locus.** Dana owned the column; suffix convention existed, but neither the parquet nor the data dictionary emitted a machine-readable unit metadata field that Vera and Ace could validate against the axis label. Cross-ref: VIZ-A2, RES-4, APP-D2.
2. **Frequency convention (daily vs monthly, alignment method)** — drives Evan's Granger lag choice, VAR vs panel selection, Vera's hero-span resolution, Ace's cache TTL. Current alignment-by-model-class table (SOP §5) is excellent, **but the alignment method is documented in prose, not as a per-column metadata field.** Evan has to read the data dictionary to know whether `ism_mfg_pmi` was LVCF or interpolated.
3. **Sample period / date range / effective start** — affects Evan's Granger lag choice (sample-length sensitivity), Vera's hero chart span, Ray's episode citations (RES-8), Ace's NBER shading scope. Effective Start is mandatory (DATA-DD1) but derived-series effective start is often wrong by one transformation (e.g., YoY transform needs 12m lookback).
4. **Classification labels (`indicator_nature`, `indicator_type`)** — DATA-D3. Wrong label → Evan's Rule C1 routes to wrong method catalog → cascade. Landing page filter shows pair in wrong bucket. **Strongest downstream impact of any Dana decision.**
5. **Canonical column naming** — decides whether Evan's script finds the column. DATA-D2 suffixes are the enforcement mechanism, but **renames** (e.g., `hy_ig_spread` → `hy_ig_oas_bps`) are only caught by DATA-D1's diff logic, which relies on Dana remembering to run it.
6. **Derived-series computation recipe** — Dana chooses e.g. `NEWORDER YoY = log(x_t / x_{t-12})` vs `(x_t - x_{t-12})/x_{t-12}`. Either is defensible; drift between pairs is the failure mode. Catalog §7.10 exists but is not auto-enforced.
7. **Status vocabulary** — DATA-VS closes this as of Wave 1.5.

---

## 4. Boundaries where Dana has been bitten

| # | Bug | Root cause in Dana's boundary | Rule that closed it (or gap) |
|---|---|---|---|
| B1 | **Wave 2A hero chart unit 100x off** | Data was in decimal (0.04) under a column named `..._bps`. Vera labeled axis "bps", Ace rendered. Neither consumer could validate against the parquet because unit lived only in the data dictionary prose, not as a column-level metadata field. | Partially closed by VIZ-A2 code-audit check; **Dana side still has no machine-readable unit tag** — gap remains. |
| B2 | **Wave 1.5 status-term leak** | Dana used a novel `_status` value; leaked through Ray narrative to portal. | Closed by DATA-VS + RES-VS. |
| B3 | **pair_registry classification schema expansion** | Dana added `indicator_nature`, `indicator_type`; Ray added `strategy_objective`; Ace's loader had to defensive-code for missing fields. Each addition was ad-hoc; no versioned schema. | Not closed — next field addition will repeat the pattern. |
| B4 | **Silent column drop between reruns** (HY-IG v2 pre-whitened CCF) | At the econometrics stage, but Dana's SOP §6 Rule D1 was written to prevent the data-stage analogue. Open question: has Dana ever tested her own D1 diff check? | DATA-D1 exists but only Dana runs it — no GATE enforces it at Lead level. |
| B5 | **Mid-analysis expedited data arrives without dictionary entry** | DATA-E1 explicitly defers quality gates; the consolidated-delivery follow-up often does not happen. | Open. |
| B6 | **Derived-series verification is opt-in prose** | SOP §5 says "verify against one published value." Catch rate is low because the check is not a gate-blocking artifact. | Open. |
| B7 | **Display-name registry drift** | A new column ships in the parquet before `display_name_registry.csv` is updated; Vera picks a raw column name as an axis label. | Partially covered by DATA-DD1 quality-gate checkbox; **no cross-check that every column has a registry entry.** |

Pattern across these: **Dana's rules are strong at the human-discipline level and weak at the machine-enforcement level.** The bugs that bit us were exactly at that gap.

---

## 5. Proposed new rules

> **Proposed DATA-D4 — Column-Level Unit Metadata (Parquet-Embedded)**
> - **Rule text:** Every non-date column in a master parquet delivered to `data/` must carry a `unit` entry in the parquet's pandas metadata (via `df.attrs[{col}_unit]` serialized into the parquet schema, or a sibling `{subject}_{freq}_schema.json` sidecar). Permitted values: the canonical set from DATA-D2 (`bps`, `pct`, `decimal_return`, `vol_ann_pct`, `index`, `usd`, `ratio`, `count`, `date`). Consumers (Vera, Ace) must read this field and cross-check against the intended axis label before rendering; if absent, treat as an ingestion error.
> - **Closes gap:** Wave-2A 100x bps-vs-decimal bug. VIZ-A2 caught it at Vera's end; with DATA-D4, the unit is discoverable from the artifact itself, not inferable from the column name or data-dictionary prose.
> - **Blocking?** Yes — applies to any parquet that crosses the data → econ/viz/app boundary.
> - **Cross-reference:** VIZ-A2 (Unit Discipline), RES-4 (Dual Notation), APP-D2 (Ace reconciliation). Makes all three enforceable without re-reading the data dictionary.

> **Proposed DATA-D5 — Machine-Readable Dataset Schema Sidecar**
> - **Rule text:** Every `data/{subject}_{freq}_latest.{ext}` must ship with a sibling `data/{subject}_{freq}_schema.json` containing: `columns[].{name, unit, dtype, frequency, alignment_method, effective_start, direction_convention, display_name, transformation, source_series_id}`. Schema sidecar is regenerated on every rerun. Adding a column to the parquet without adding it to the schema is a gate failure (DATA-Q1 addition).
> - **Closes gap:** (a) data-dictionary drift — CSV dictionary and parquet can diverge; (b) display-name-registry staleness — registry can lag new columns; (c) alignment method is currently prose-only. Also gives Ace a single machine-readable source instead of parsing the markdown dictionary.
> - **Blocking?** Yes for portal-facing `_latest` aliases; optional for dated files used only internally by Evan for sensitivity.
> - **Cross-reference:** DATA-DD1 (existing dictionary rule, now machine-mirrored), META-D1 (self-describing artifacts), APP-DL1 (Ace cache TTL).

> **Proposed DATA-D6 — Classification Schema Versioning Contract**
> - **Rule text:** The shape of `interpretation_metadata.json` (which fields are required, which are Dana-owned, which are Ray-owned, which controlled vocabularies apply) is governed by a canonical schema at `docs/interpretation_metadata_schema.json` with a `schema_version` field. Adding, removing, or renaming any field requires: (a) bumping `schema_version`, (b) a SOP changelog entry, (c) Ace's `pair_registry.py` loader updated in the same commit, (d) Lesandro sign-off. No ad-hoc field additions.
> - **Closes gap:** The pair_registry classification expansion (indicator_nature, indicator_type, strategy_objective) happened in three ad-hoc waves. The next addition (e.g., `risk_bucket`, `time_horizon`) will repeat the same pattern and re-break Ace's landing page loader.
> - **Blocking?** Yes — structural. Not per-pair, but per schema revision.
> - **Cross-reference:** META-CFO (classification field ownership), GATE-19/20/21, APP-LP6 (landing page metadata source), RES-IT1.

> **Proposed DATA-D7 — Derived-Series Reference-Value Verification Artifact**
> - **Rule text:** For every derived series (HY-IG spread, VIX/VIX3M, Gold/Copper, ISM ratio, NEWORDER YoY, SOFR-US3M spliced, and any future derived series registered in data-series-catalog §7.10), Dana ships `data/{series_name}_verification.json` with at least 3 reference-date assertions: `[{date, expected_value, actual_value, tolerance, pass}]`. At least one reference date must be from a known stress episode. Fail on any pass=false. Regenerated on every rerun.
> - **Closes gap:** §5 "Derived series computation verification" is prose-only today. The Wave-2A unit bug was on a derived column; a reference-value assertion against a known-published number would have caught it.
> - **Blocking?** Yes for any pair that uses a derived series.
> - **Cross-reference:** META-D2 (reconciliation), ECON-D2 (Evan sanity-check), data-series-catalog §7.10.

> **Proposed DATA-D8 — Mid-Analysis Expedited Follow-Up Gate**
> - **Rule text:** Every expedited single-variable delivery under DATA-E1 carries a "debt" tag in the handoff message and an entry in `data/expedited_debt.md`. The debt is discharged when: (a) the column appears in the next consolidated data dictionary, (b) Dana re-runs quality gates on it, (c) the debt log entry is marked closed. A pair cannot reach GATE-23 acceptance if any debt tied to its dataset is still open.
> - **Closes gap:** DATA-E1 explicitly defers quality gates "to the next consolidated delivery" — in practice that consolidation often never happens, and the expedited column ships to production without stationarity tests or dictionary entry.
> - **Blocking?** Yes at pair-acceptance time (GATE-23 dependency).
> - **Cross-reference:** DATA-E1, ECON-M1, META-PAC, GATE-23.

**Top-3 ranking:** D4 (unit metadata in parquet), D5 (schema sidecar), D6 (classification schema versioning). These three together close the three distinct bug classes we have actually seen.

---

## 6. Questions to other agents (for consolidation phase)

- **@Evan** — Do you need the raw FRED series code (e.g., `BAMLH0A0HYM2`) *and* the semantic canonical name (`hy_oas_bps`) in my parquet, or only the canonical? Today I deliver only the canonical and put the raw code in the data dictionary. If your Rule C1 routing ever needs the raw code programmatically, I need to know.
- **@Evan** — When you submit a mid-analysis expedited request (ECON-M1), are you willing to receive the variable **without** a stationarity test result, on the understanding that a follow-up consolidated delivery will supply it? Proposed DATA-D8 makes this debt explicit — please confirm the tradeoff is acceptable.
- **@Vera** — If I add DATA-D4 (column-level unit metadata in the parquet), will you consume it via `df.attrs` in your chart-build pipeline, or would a schema sidecar (DATA-D5 route) be easier? Preference drives implementation.
- **@Ace** — Your `pair_registry.py` loader currently falls back to `"Unknown"` when classification fields are missing. If I add DATA-D6 (versioned classification schema), would you prefer (a) a hard error on schema_version mismatch, or (b) defensive fallback with a warning chip? Landing page integrity depends on this.
- **@Ace** — `data/manifest.json` `mixed_freq_ttl_note` is advisory today. Are you using it? If not, the rule is dead weight; if yes, it should be in the schema (DATA-D5) so it is machine-readable.
- **@Ray** — When you file a RES-B4 direction-contradiction note, do you want me to add a `known_direction_quirk` flag to the data dictionary so Evan and Vera see it at ingestion, or is the contradiction note itself sufficient?
- **@Ray** — For derived series, your RES-4 dual-notation rule relies on my units being right. If DATA-D4 / DATA-D7 close this, can we retire the dual-notation fallback for columns that ship with verified unit metadata, or is the dual notation still a reader-facing requirement regardless?

**Top-priority question:** **@Ace — would you commit to consuming a `data/{subject}_schema.json` sidecar (DATA-D5) as the single source of truth for column unit, display name, direction, and refresh TTL, replacing your current path of parsing the markdown data dictionary?** This is the keystone of the whole proposal — if Ace will consume it, DATA-D4/D5/D6 collectively retire three failure modes at once. If Ace won't, DATA-D4 alone is still worth doing but the compound win is much smaller.
