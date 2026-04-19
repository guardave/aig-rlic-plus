# Validation Audit 2026-04-19 — Data Dana

**Auditor:** Data Dana
**Scope:** Data-layer reproducibility + stakeholder-resolution spot-check against the HY-IG v2 × SPY reference pair.
**Trigger:** Lesandro, follow-up to the 2026-04-19 cross-review. "Would another Dana reproduce the same files?" and "did the Wave-2A/2B/4C fixes actually land in the artifacts, not just in the rulebook?"
**Inputs audited:** `docs/agent-sops/data-agent-sop.md`, `docs/standards.md` DATA section, `docs/stakeholder-feedback/20260418-batch.md`, `data/hy_ig_v2_spy_daily_20260410.parquet`, `results/hy_ig_v2_spy/interpretation_metadata.json`, `docs/schemas/data_subject.schema.json`, `docs/schemas/interpretation_metadata.schema.json`, `docs/cross-review-20260419-dana.md`.

Audit is read-only. No files edited. Findings feed a Wave-4D2+ rulebook revision.

Dana-owned artifact count: **7 artifact classes across 15 physical files** (see Axis 1 table).

---

## Axis 1 — Reproducibility

**Question:** Given the same source APIs and the current SOP + schemas, would another Dana produce identical files?

| # | Data artifact | SOP rule | Deterministic? | Discretion point | Captured? | Proposed fix |
|---|---|---|---|---|---|---|
| 1 | **Indicator source series selection** (`BAMLH0A0HYM2`, `BAMLC0A0CM` for HY-IG) | DATA-H1, §2 priority table | **No** | Dana could pick Bloomberg HY/IG, Markit CDX, or ICE indices; SOP §2 says "FRED first" but doesn't name a canonical registry per indicator | Partially — `docs/data-series-catalog.md` names some series, but not in a structured "canonical_source_of_record" field | **Proposed DATA-D9: Canonical Source-of-Record Registry** per indicator (FRED series ID + fallback proxy list) |
| 2 | **Sample period boundaries** (start = 2000-01-03, end = 2025-12-31 in v2 parquet) | Analysis Brief §Data | Partial — Brief usually states period | Which Dana trims to OAS start (1997) vs 2000 round date vs "since fed_funds series begins" is judgment | No — neither the parquet nor the sidecar records "why this start date" | Add `sample_period_rationale` field in DATA-D5 sidecar |
| 3 | **Data frequency alignment** (LVCF, interpolate, MIDAS?) | §5, table "alignment by downstream model class" | Partial — SOP gives guidance, but **per-column alignment method is prose-only, not a parquet/sidecar field** | When merging monthly NFCI with daily HY-OAS, SOP says "LVCF preferred" but Dana could interpolate | No — alignment method lives in data-dictionary transformation column, free-text, not validated | Add `alignment_method` enum field to DATA-D5 schema |
| 4 | **Missing-data handling** | §4 Clean and Transform | **No** | Forward-fill, interpolation, drop are all "document which and why"; no default codified | Partial — human-reviewed in data dictionary | **Proposed DATA-D10: Default Missing-Value Policy** (forward-fill ≤5 obs, drop rows with any NaN beyond that, never interpolate across regime boundaries) |
| 5 | **Outlier treatment** | §5 Validate (z>4 flag, do not auto-remove) | **Yes-ish** — rule says flag, never drop | SOP is clear, but no artifact captures which observations were flagged | Weak — "flag" is prose | Add `outlier_flags[]` section to DATA-D5 sidecar with date + column + z-score |
| 6 | **Unit conventions** (OAS in bps vs %) | DATA-D2, DATA-D5 | **No — actively violated in HY-IG v2** | Spot-check: `hy_ig_spread` is stored in **percent** (range 1.47–15.31 over 2000–2025; GFC max 15.31) but DATA-D2 mandates `_bps` suffix for spreads. Column name carries no suffix. | No sidecar exists for HY-IG v2 → unit is un-machine-verifiable | **Critical finding.** DATA-D5 sidecar must be written for HY-IG v2 and enum-constrained to catch this |
| 7 | **Column naming** (`hy_ig_spread` vs `hy_ig_oas_bps` vs `spread`) | DATA-D2 suffixes | **No — violated on HY-IG v2** | Current parquet uses `hy_ig_spread`, `hy_oas`, `ig_oas` with **zero `_bps` suffix** despite DATA-D2 requiring one | No — suffix enforcement is checklist-only, not automated | Add a producer-side linter: any spread/return/rate column without a canonical suffix fails DATA-Q1 |
| 8 | **Classification values** (`indicator_type: credit`, `indicator_nature: leading`) | DATA-D3, DATA-D6 | **Yes** — HY-IG v2 validates OK against `interpretation_metadata.schema.json` (exit 0) | Mapping a new indicator (e.g. NFCI) to `credit` vs `macro` is still judgment | Partially — DATA-D6 schema caught the structural gap, but catalog-lookup is prose | Promote `docs/data-series-catalog.md` Section 7 into a structured YAML with one row per indicator and the authoritative classification |
| 9 | **Refresh cadence** (daily vs monthly) | §6 Deliver, `data/manifest.json` | **No** — **`data/manifest.json` does not exist on disk** | Mixed-freq datasets (HY-IG v2 has daily OAS + weekly NFCI + monthly claims) have no TTL declaration | **No** — the SOP §6 example shows a format that never materialized | Block delivery until `data/manifest.json` exists and is schema-validated |
| 10 | **Derived-series computation** (`hy_ig_spread = hy_oas - ig_oas`) | §4 Clean (recipe catalog), §5 (reference-value verify) | Partial — recipe catalog exists in `data-series-catalog.md` §7.10 | Dana could compute in bps or percent (see item 6) — recipe is unit-agnostic | No — reference-value verification is opt-in prose | **Proposed DATA-D7 from cross-review** — derived-series verification JSON as a gated artifact |
| 11 | **Days-since-release column** (optional) | §5 | **No** — "optionally include" | Inconsistent across pairs | Opt-in → opt-out: make it mandatory for LVCF-aligned series |
| 12 | **Stationarity results delivery** | DATA-DD3 | Partial — format is structured, but HY-IG v2 has `results/hy_ig_v2_spy/stationarity_tests_20260410.csv`, not a handoff-message prose table | Good — file exists | Upgrade SOP: mandate the CSV, retire the "in handoff message prose" alternative |
| 13 | **Display-name registry** (`data/display_name_registry.csv`) | §6 Deliver | **N/A — file does not exist on disk** | Vera falls back to column codes as axis labels | **No** — rule is on paper only | Create `data/display_name_registry.csv`; DATA-D5 sidecar cross-validates it |
| 14 | **Dataset schema sidecar** (`data/hy_ig_v2_spy_daily_schema.json`) | DATA-D5 (new, Wave 4C-1) | **N/A — sidecar does not exist for HY-IG v2** | Schema authored in Wave 4C-1; no instance produced for the reference pair | **No** — DATA-D5 is a paper rule until the reference pair has one | Write the sidecar today; add to GATE-23 reference-pair acceptance |
| 15 | **Interpretation metadata** (`results/hy_ig_v2_spy/interpretation_metadata.json`) | DATA-D6 | **Yes** — validates OK against schema | — | Yes | — |

**Severity triage:**
- **Critical (blocks reproducibility):** #6 unit convention, #7 column naming, #14 schema sidecar missing, #13 display-name registry missing, #9 manifest.json missing.
- **High (silent drift risk):** #1 source registry, #3 alignment method per-column, #10 derived-series verification.
- **Medium:** #2 sample period rationale, #4 missing-value default, #5 outlier flags, #11 days-since-release.
- **Low / resolved:** #8 classification (DATA-D6 landed), #12 stationarity CSV (artifact exists), #15 interpretation metadata (validates).

---

## Axis 2 — Stakeholder Resolution

| # | Stakeholder item | Claimed SOP rule | HY-IG v2 data evidence | Spirit met? | Gap |
|---|---|---|---|---|---|
| A | **S18-5 Hero chart 100x unit bug (Wave 2A)** — column unit metadata | DATA-D5 (schema sidecar) | **No sidecar exists on disk** for HY-IG v2. Parquet `hy_ig_spread` is in **percent** (max 15.31 over GFC), data dictionary claims `Unit=bps` — the same class of discrepancy that caused Wave-2A. | **No — paper rule only.** The fix works in theory (schema + validator exist); the instance for the reference pair was never produced. Vera/Ace cannot consume a file that doesn't exist. | **Produce `data/hy_ig_v2_spy_daily_schema.json` this cycle.** Unit must be explicitly `percent` (or normalize the parquet to `bps` and rename column `hy_ig_spread_bps`). This is the most visible open gap. |
| B | **S18-4 status vocabulary** | DATA-VS (7-value canonical) | I grep'd `_status` in the parquet columns (none present), the `interpretation_metadata.json` (none), and `handoff_to_vera_20260419.md` (uses `ready` — not canonical but also not a `_status`). No leak detected in HY-IG v2 artifacts. | **Yes, spirit met** in-pair. | `ready` in handoff messages is a near-synonym for `Available` — consider adding to canonical list or rewriting. |
| C | **DATA-D6 classification schema** (Wave 4C-2) — `owner_writes` mapping | DATA-D6 | `interpretation_metadata.json` validates OK against schema (exit 0). `owner_writes` lists dana/evan/ray explicitly. `last_updated_by=dana`, `last_updated_at=2026-04-19T17:37:40Z`. Dana's fields (`indicator_nature=leading`, `indicator_type=credit`) populated; Evan's (`observed_direction=countercyclical`, `confidence=high`, `key_finding`) populated; Ray's (`strategy_objective=min_mdd`, `expected_direction`, `mechanism`, `caveats`) populated. | **Yes — actually achieved.** 3-way ownership is real, not aspirational. This is the cleanest landing of any Wave-4 rule. | `strategy_objective=min_mdd` is a legacy label. Schema accepts it but the new canonical vocabulary includes `countercyclical_protection` — Ray should migrate on next touch. Non-blocking. |
| D | **Earlier Part D/E classification filter correctness** — no `Unknown` on landing page | GATE-19/20/21, APP-LP7 | HY-IG v2 values: `indicator_nature=leading`, `indicator_type=credit`, `strategy_objective=min_mdd`. All three are valid controlled-vocab values. **No `Unknown` present.** | **Yes, spirit met.** | Registry cross-check: `app/components/pair_registry.py` still defaults to `"unknown"` string fallback when a field is missing (lines 64-66, 168-170). Acceptable as defense-in-depth but means a future schema-invalid JSON would still render. Coordinate with Ace on APP-SEV1 L1 upgrade. |

**Summary:** 2 of 4 stakeholder resolutions are **genuinely landed** (DATA-D6 schema + owner_writes; classification filter values). 1 is **paper-only** (DATA-D5 — critical, the keystone rule for the Wave-2A class of bug doesn't have a concrete instance on disk for the reference pair). 1 is **mostly-met** (DATA-VS — no leaks in HY-IG v2 artifacts).

---

## Axis 3 — Proposed DATA-* fixes

Ranked by value × feasibility. All are addressable this cycle without a data refresh.

### DATA-D9 (new) — Canonical Source-of-Record Registry per Indicator
**Problem:** SOP §2 names the API priority ladder but does not bind each indicator to a specific series ID. Another Dana could reproduce "HY-IG spread" from Bloomberg, Markit, or FRED with different numeric values.
**Proposal:** Promote `docs/data-series-catalog.md` Section 7 into a structured `docs/data-series-registry.yaml` with `indicator_id`, `canonical_source`, `canonical_series_id`, `fallback_proxies[]`, `computation_recipe`, `canonical_classification.{indicator_nature, indicator_type}`. Producer reads YAML; validator confirms every column the producer emits is registered.
**Closes:** Item #1, #8 mapping judgment, cross-pair drift on shared indicators.
**Blocking:** Yes at data-pipeline intake, not at gate.

### DATA-D11 (new) — Reference-Pair Sidecar Instance Gate
**Problem:** DATA-D5 schema exists; HY-IG v2 sidecar instance does not. A schema with no reference instance is a rule the reference pair actively violates.
**Proposal:** Add to GATE-23 (Pair Acceptance) a hard check that every reference pair (per META-RPD) has `data/{subject}_{frequency}_schema.json` on disk, validating OK. For HY-IG v2 specifically, **produce the sidecar immediately** and include it in the next commit along with a reconciliation step for the bps-vs-percent mismatch in item #6.
**Closes:** Axis-2 gap A (S18-5 residual), Axis-1 gap #14.
**Blocking:** Yes — reference-pair acceptance blocker. Non-reference pairs get a gate-24 warning.

### DATA-D12 (new) — Column Suffix Linter (DATA-D2 Enforcement)
**Problem:** DATA-D2 mandates `_bps` / `_pct` / `_ret` etc. suffixes. HY-IG v2 parquet has `hy_ig_spread`, `hy_oas`, `ig_oas`, `yield_spread_10y3m` — **zero suffix compliance on spread/yield columns.** Checklist-only enforcement fails.
**Proposal:** Small `scripts/validate_column_suffix.py` that scans any parquet and flags columns matching a spread/yield/return pattern without a canonical suffix. Wire into DATA-Q1. Grandfather existing `hy_ig_spread` → accept until next rerun, then require rename + regression_note with mapping table for consumers.
**Closes:** Item #7, partially #6.
**Blocking:** Yes on new deliveries; grandfathered on existing reference pairs.

### DATA-D13 (new) — Manifest + Display-Name Registry Bootstrap
**Problem:** SOP §6 mandates `data/manifest.json` and `data/display_name_registry.csv`. Neither file exists on disk. Two cornerstone artifacts that downstream consumers (Ace cache TTL, Vera axis labels) rely on are entirely paper.
**Proposal:** Generate both files from the union of existing parquets + data dictionaries in one script (`scripts/bootstrap_data_manifest.py`). Thereafter the DATA-D5 sidecar is the source of truth for display names (per META-CF) and the manifest is the source of truth for TTL and cross-pair alias mapping. Block GATE-23 on missing manifest entry for any reference pair.
**Closes:** Items #9, #13.
**Blocking:** Yes.

### DATA-D14 (new) — Derived-Series Reference-Value Verification Artifact (lift of proposed DATA-D7 from cross-review)
**Problem:** Derived series (`hy_ig_spread`, `ccc_bb_spread`, `yield_spread_10y3m`, `hy_ig_realized_vol_21d`) rely on §5's "verify against one published value" — prose-only. HY-IG v2 has no on-disk verification artifact.
**Proposal:** `data/{subject}_{frequency}_verification.json` with ≥3 reference-date assertions per derived column; ≥1 must be a known stress episode from `known_stress_episodes` in `interpretation_metadata.json`. Fail on any mismatch outside tolerance.
**Closes:** Item #10, secondary defense against item #6 (a known-peak cross-check would have flagged percent-vs-bps immediately).
**Blocking:** Yes on any pair using a derived series.

**Ranking for this cycle:** D11 > D12 > D13 > D9 > D14. D11 closes the most visible open gap for the reference pair; D12 institutionalizes what checklist review keeps missing; D13 unblocks Ace's TTL and Vera's labels.

---

## Axis 4 — Questions to Lesandro

1. **Bps-vs-percent reconciliation on HY-IG v2.** `hy_ig_spread` is stored in percent but the unit-suffix convention (DATA-D2) mandates `_bps`. Two options: (a) rename column to `hy_ig_spread_pct`, keep values, document in regression_note; (b) rescale values ×100 to bps, rename to `hy_ig_spread_bps`, break every downstream consumer. **Recommend (a)** plus immediate DATA-D5 sidecar authoring — lowest blast radius, makes the existing convention match reality. Cross-reference with Evan for method-coverage impact. Is (a) acceptable, or do you want me to force (b) for alignment with the DATA-D2 "bps by default" principle?

2. **Reference-pair sidecar deadline.** DATA-D11 proposes GATE-23 blocking on reference-pair sidecars. Do I author `data/hy_ig_v2_spy_daily_schema.json` this cycle (before next acceptance), or wait for Wave 5 consolidation?

3. **Manifest + display-name registry bootstrap authority.** Creating `data/manifest.json` and `data/display_name_registry.csv` from scratch is a ~1-day script but touches every pair's metadata. Do I scope it to HY-IG v2 + INDPRO + VIX-VIX3M (the three pairs cited in the portal landing cards today), or batch-scan every pair in `results/` now? Former is safer, latter prevents a second migration pass.

4. **Source-of-record registry migration path.** DATA-D9 promotes the markdown catalog into structured YAML. This is a one-time migration with no data impact. Can I do this unilaterally and file a regression_note, or does it need Lead review before I touch the catalog?

5. **Strategy-objective vocabulary migration.** HY-IG v2 still uses `min_mdd` (legacy label in the schema enum). The preferred new label is `countercyclical_protection`. Ray owns the field — should I file a request-back for Ray to update on next touch, or leave as-is?

**Top priority:** #1 (bps-vs-percent reconciliation). This is the residual Wave-2A exposure. Until resolved, HY-IG v2's data dictionary continues to assert `Unit=bps` on a percent-valued column — exactly the failure mode DATA-D5 was designed to prevent.

---

## Deliverable summary (≤200 words)

1. **Data artifacts audited:** 7 artifact classes across 15 physical files (parquet, data dictionary, interpretation metadata, schema sidecar, manifest, display-name registry, derived-series verification). Focus on HY-IG v2 reference-pair conformance.

2. **Reproducibility gaps by severity:**
   - **Critical:** unit convention violated on `hy_ig_spread` (stored percent, dictionary claims bps); column-suffix convention violated (10+ columns missing `_bps`/`_pct`); DATA-D5 sidecar not produced for reference pair; `data/manifest.json` and `data/display_name_registry.csv` do not exist on disk.
   - **High:** no canonical source-of-record registry; alignment method is prose-only; derived-series verification opt-in.
   - **Low/resolved:** interpretation_metadata validates OK; classification values clean; no status-vocabulary leaks.

3. **Stakeholder-resolution gaps:** S18-5 (Wave-2A 100x) **paper-only** — schema exists, instance doesn't. DATA-D6 and classification values are genuinely landed. S18-4 status vocab is clean in HY-IG v2 artifacts.

4. **Top 3 rule proposals:** DATA-D11 (reference-pair sidecar gate), DATA-D12 (column-suffix linter), DATA-D13 (manifest + display-name registry bootstrap).

5. **Top question to Lesandro:** How to reconcile the bps-vs-percent mismatch on `hy_ig_spread` — rename to `_pct` (safe) or rescale to bps (principled but breaks consumers)?
