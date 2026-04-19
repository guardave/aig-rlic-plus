# Cross-Review — Econ Evan Boundary Contracts

**Agent:** Econ Evan
**Date:** 2026-04-19
**Scope:** Audit of every artifact Evan produces for / consumes from the other four agents (Dana, Vera, Ray, Ace). Read-only; no SOP edits. Companion to the parallel audits by Dana, Vera, Ray, Ace.

**Method:** walked the Evan SOP, then each consumer SOP, then `standards.md`, then the on-disk fingerprints under `results/hy_ig_v2_spy/` and `results/hy_ig_spy/` and the live loader code in `app/components/probability_engine_panel.py` and `app/components/charts.py`. Pattern-matched against the 5 recent handoff bugs in the prompt.

---

## 1. Artifacts Evan produces for other agents

All paths relative to repo root. "Consumer" = the agent whose SOP explicitly reads the artifact; a second agent in parens = secondary consumer.

| Artifact path | Consumer | Contract rule ID | Schema explicit? | Failure mode when missing/invalid | Test/gate | Known gaps |
|---|---|---|---|---|---|---|
| `results/{pair_id}/signals_{date}.parquet` | Ace (Vera) | ECON-DS1, ECON-DS2 | Yes — DatetimeIndex + per-signal columns; column names must match tournament `signal` codes | APP-SE1 Probability Engine panel renders `st.error("signal column missing")`; exposure panel (SE2) degrades to warning | GATE-27 (load end-to-end), GATE-29 (clean checkout), APP-ST1 smoke test | **Column-name-to-signal_code mapping is implicit.** Ace has a fallback table `_SIGNAL_CODE_TO_COLUMN` (hy_ig v2: `S6_hmm_stress` → `hmm_2state_prob_stress`). Evan does not emit this mapping. Wave 1.5 bug. |
| `results/{pair_id}/winner_summary.json` | Ace (Ray) | META-TWJ-adjacent, implicit | **Partial** — SOP enumerates fields in narrative only (signal_code, threshold_code, strategy_code, oos_sharpe, max_drawdown, etc.). No single registered schema | `render_execution_panel` falls back to `"—"` for missing fields; SE1 pre-render check errors out if `signal_column` absent | Smoke test + reconciliation, no schema-level gate | **`signal_column` field absent on hy_ig_v2** (Wave 1.5). **`target_symbol` absent** — Ace reads `winner.get("target_symbol", "SPY")` as a hardcoded fallback in `instructional_trigger_cards.py` line 260. **`threshold_value` vs `threshold_code` duality** not documented. |
| `results/{pair_id}/tournament_winner.json` | Ray, (Ace) | META-TWJ (named), ECON §Tournament handoff | Yes — 10 fields enumerated (winner_label, winner_oos_sharpe, delta_sharpe, ...) + `beats_benchmark` | Ray cannot classify `strategy_objective` (RES-B5) | GATE-21 (strategy_objective populated) | No known gaps. Schema is one of the best-codified. |
| `results/{pair_id}/tournament_results.csv` (summary) | Ray, Ace, (Vera) | ECON-T1, ECON §Tournament output | Yes — canonical column schema mandated (`signal`, `threshold`, `strategy`, `lead_*`, `lookback`, `oos_sharpe`, `oos_ann_return`, `max_drawdown`, `win_rate`, `n_trades`, `annual_turnover`, `valid`, `oos_n`) | Ray cannot diff winner vs B&H; downstream `generate_winner_outputs.py` needs ad-hoc mapping (HY-IG pair #5 regression) | GATE-7 | Legacy `signal_col`/`threshold_method` aliases explicitly prohibited but no producer-side lint. |
| `results/{pair_id}/tournament_top10_equity.csv` | Vera, Ace | ECON §Tournament output | Yes — `date`, `strategy_label`, `cumulative_return`, `drawdown`, `regime` | Equity curve chart missing | GATE-8 | None. |
| `results/{pair_id}/winner_trade_log.csv` | Ace | ECON-C4 (#1 of dual log) | Implicit; narrative only | Strategy page trade table empty | GATE-17 | Row count > 0 is the only check (GATE-17). Column schema not registered. |
| `results/{pair_id}/winner_trades_broker_style.csv` | Ace | ECON-C4 (#2 of dual log) | **Yes** — 10 columns enumerated with type + meaning | Download button has no data | APP-AF5 column legend | None. Good model of a locked-down contract. |
| `results/{pair_id}/interpretation_metadata.json` | Ray, Vera, Ace | ECON (writer), DATA-D3 (Dana writes `indicator_nature`/`indicator_type`), RES-B5 (Ray writes `strategy_objective`) | Yes — fields listed in Evan SOP §9 | Vera line-style encoding wrong; Ace "How to Read This" pending placeholder | GATE-4, GATE-19, GATE-20, GATE-21 | **Multi-writer file with no locking protocol.** Evan writes `observed_direction`/`direction_confidence`, Dana writes `indicator_nature`/`indicator_type`, Ray writes `strategy_objective`. No write-order rule. Wave 4A-adjacent risk. |
| `results/{pair_id}/kpis.json` | Ace | ECON-H3 | Partial — array of `{metric, value, unit, label}`; `source_file`/`source_field` recommended in APP-AF3 but not required in ECON-H3 | Ace shows "Results pending" placeholder (APP §5) | GATE-16 (implicitly) | **Schema fork** — Evan SOP says `{metric, value, unit, delta}`, Ace SOP reads `{metric, value, unit, label, source_file, source_field}`. Silent divergence. |
| `results/{pair_id}/granger_by_lag.csv` | Vera | ECON-E1 | Yes — 5 columns (`lag`, `f_statistic`, `p_value`, `df_num`, `df_den`) | VIZ-V3 "No Silent Chart Fallback" triggers GATE-25 placeholder | GATE-25 (reference pair: GATE-28) | None. Added 2026-04-19. |
| `results/{pair_id}/regime_quartile_returns.csv` | Vera | ECON-E2 | Yes — 6 columns (`quartile`, `n_months`, `ann_return`, `ann_vol`, `sharpe`, `max_drawdown`) | CCF Evidence chart missing | VIZ-V4 + GATE-25 | Filename convention for coexisting quartile families (`ccf_quartile_returns.csv` etc.) is specified but not enforced. |
| `results/{pair_id}/core_models_{date}/*.csv` — correlations, ccf_prewhitened, granger_causality, transfer_entropy, local_projections, quantile_regression, hmm_summary | Ray, Vera | ECON-C1 + ECON-C2 (exact column schema per method) | Yes — per-method column tables | Silent method drop (HY-IG v2 Wave 2 regression) | ECON-C3 producer-side rerun diff + Ray's RES-5b filesystem diff | Filename stability rule is in §C2 but `_manifest.json` sidecar is mandated per-method by META-D1 — producer-side check for sidecar presence is missing. |
| `results/{pair_id}/core_models_{date}/hmm_states.parquet` | Ace (SE1 via `signals_*`), Vera, Ray | ECON-C2 (row in schema table) | Yes | Regime chart missing; SE1 exposure panel falls over | GATE-6 | Distinct from `signals_{date}.parquet` — the probability columns are duplicated in both. No rule says which is canonical for Ace's Probability Engine (Ace reads `signals_*`, not `hmm_states.parquet`). Cross-artifact consistency not checked. |
| `results/{pair_id}/exploratory_{date}/*` — correlations.csv, regime_descriptive_stats.csv | Vera, Ace | ECON-EX1 | Partial — section titled "Exploratory Deliverables" but no per-file column schema | Exploratory tab on Evidence page reads from `regime_descriptive_stats.csv` (Ace SOP §3.6 Tab 2); missing = pending placeholder | GATE-5 | Columns of `regime_descriptive_stats.csv` not enumerated anywhere. Ace-consumed but Evan-produced; no schema contract. |
| `results/{pair_id}/execution_notes.md` | Ray (extends), Ace (renders) | GATE-18 (co-owned by Ray/Evan) | No — free-form markdown | Execute tab falls back to "raw parameters" (Ace SOP §3.6 Tab 1) | GATE-18 | **Dual ownership with no division rule.** Evan writes signal/threshold/lead detail; Ray adds plain-English steps. No headers mandated, no "who owns which section". |
| `results/{pair_id}/handoff_to_vera_{date}.md` | Vera | ECON-H4 | Yes — 4-column table (method/file/expected_chart/status) | Vera has no method→chart map; GATE-25 placeholders proliferate | Implicit via GATE-25 | File path convention `handoff_to_vera_YYYYMMDD.md` is followed in practice but not registered as a mandatory filename in any rule. |
| `results/{pair_id}/regression_note_{date}.md` | Ray, Ace, Lesandro | META-RNF, ECON-C3 | Yes — META-RNF sections (Changes / Approved By / Unchanged / Impact, plus **Removed** per META-VNC) | GATE-22 (method coverage regression) blocks | GATE-22, GATE-26 | Producer-side (Evan) produces it; consumer-side (Ray) regression-diff (RES-5/5b) may run independently and reach a different verdict. No reconciliation protocol between the two diffs. |
| `results/{pair_id}/core_models_{date}/_manifest.json` (and per-artifact sidecars) | Vera (VIZ-DI1), Ace (APP-D2) | META-D1, Evan SOP §"Self-describing artifacts" | Yes — columns, direction/sign, units, ≥3 assertions | Vera cannot validate (VIZ-DI1 step 1); consumer reconciliation fails | META-D2 | Mandatory "per file" is stated but Evan's pipeline in practice writes one top-level manifest per core_models dir. Per-file sidecars for `hmm_states.parquet`, etc., are inconsistent. |
| `results/{pair_id}/design_note.md` (optional, on deviations) | Lesandro, Ray, Ace | META-EOI | Yes — free-form but explicit "rationale" section required | Deviations become silent drops | GATE-22, GATE-26 | File is conditional; absence means "no deviations" by convention but nothing enforces this. |
| `results/{pair_id}/acceptance.md` | Lesandro, Ace | META-PAC, GATE-23 | Yes — mandated sections (Lead sign-off, Prior-Version Inventory, method→chart mapping) | Pair not acceptable | GATE-23 + GATE-26 + GATE-28 | Primarily Lead-assembled with Evan/Ray/Ace inputs; ownership gray-area. |
| `results/{pair_id}/live_execution_stub.json` (optional) | Ace (APP-SE4) | Implicit — Ace SOP §3.10 references it as optional | No — neither Evan nor any SOP owns authorship | Ace renders "—" placeholders | None (non-blocking) | **Nobody owns this artifact.** Evan does not produce it, Ace reads it. Orphan contract. |

**Summary: 19 produced artifacts. 6 with fully explicit column/field schema. 7 with partial/narrative-only schema. 6 with implicit/no schema.**

---

## 2. Artifacts Evan consumes from other agents

| Artifact path | Producer | Contract rule ID | Schema explicit? | Failure mode when missing/invalid | Test/gate | Known gaps |
|---|---|---|---|---|---|---|
| `data/{pair_id}_{freq}_latest.parquet` (master parquet, stable alias) | Dana | DATA-D1, DATA-D2, DATA-DD1 | Yes — data dictionary + unit convention registry | Evan's Defense 2 known-fact sanity check (ECON-D2) fails; model estimation errors | DATA-Q1, ECON-D2 | `_latest` alias stability is Dana-owned; if Dana refreshes without rebuilding the alias, Evan reads stale data silently. Cross-agent invariant, not Evan-owned. |
| Data dictionary (markdown/CSV) | Dana | DATA-DD1 | Yes — 14 required fields | Evan cannot verify unit convention or direction | DATA-Q1 | None at Evan's boundary. |
| `stationarity_tests_{date}.csv` (if Dana delivers) | Dana | DATA-DD3 | Yes — variable/test/stat/p/lags/conclusion | Evan re-runs (wasted cycle, risk of different verdict) | DATA-DD3 | Ownership rule is clear; filename convention in Evan's `results/{pair_id}/` matches Dana's delivery format but could be inconsistent when Dana delivers under `data/`. |
| Analysis Brief (Ray) | Ray | META-P0, RES-B1 | Yes — Analysis Brief template | Evan starts without hypothesis; target-class-specific intake check (Evan §1) fails | META-P0, GATE-1 | None at Evan's consumption point. |
| Research brief (Ray spec memo + full brief) | Ray | RES-B1 (two-stage) | Yes — 7-section template + "Recommended Specification Details" | Evan specifies without literature grounding; RES-3 "Why we chose this method" falls back to Evan's own justification | META-ACK | Ray may deliver quick-memo only; Evan's §2 "two-stage intake" documents the protocol, but if the full brief never arrives, there is no escalation SLA. |
| Direction annotation (Ray, via Analysis Brief S11.4 + RES-B2) | Ray | RES-B2, RES-B3 | Yes — 4-value vocab (pro_cyclical, counter_cyclical, ambiguous, conditional) | Evan writes `observed_direction` but cannot compare vs `expected_direction`; interpretation_metadata.json incomplete | GATE-4 | None. |

**Summary: 6 consumed artifacts. All but one (direction annotation cadence) well-specified.**

---

## 3. Decisions Evan makes that affect other agents

| Decision | Downstream impact | Documented where? | Gap |
|---|---|---|---|
| **Naming the signal column in `signals_*.parquet`** (e.g. `hmm_2state_prob_stress` vs `stress_prob_2state`) | Ace's SE1 Probability Engine can / cannot resolve the column | ECON-DS1 says "descriptive names, match the tournament `signal` code" — but `signal_code` (e.g. `S6_hmm_stress`) ≠ column name (`hmm_2state_prob_stress`). Rule is violated in practice. | **High-risk gap.** No rule mandates that `winner_summary.json.signal_column` = exact parquet column name. Wave 1.5 bug origin. |
| Whether a mandatory method is `ready` / `blocked` / `pending` in the Vera handoff | Vera renders real chart vs GATE-25 placeholder; Ray's Evidence 8-element block degrades | ECON-H4 handoff template | Status is self-declared by Evan; Vera does not validate by re-reading the CSV. Blocked-status gaming possible. |
| **Inclusion of variants in a variant family** (e.g. `hy_ig_v2_spy` is a rerun/v2, not a new pair) | Ray narrates variant separately or combined; Ace landing-page card count | META-VF + memory:`feedback_variant_families.md` | No rule says "the variant pair ID prefix must match the base pair." `hy_ig_spy` vs `hy_ig_v2_spy` is conventional, not enforced. |
| **`beats_benchmark: false` flag in `tournament_winner.json`** | Ray's strategy_objective classification; Lesandro escalation path | ECON §Tournament handoff step 4 | Documented; no test asserts the flag is present when `winner_oos_sharpe < bh_oos_sharpe`. |
| **Renaming of files across reruns (e.g. `quartile_returns.csv` → `regime_quartile_returns.csv`, 2026-04-19)** | Ray's RES-5b filesystem diff breaks; Ace loader 404s if hardcoded | ECON-C2 "Filename stability across reruns" + META-RNF | Documented; broke in practice (2026-04-19 HY-IG v2 rename). Regression note addresses backward compat but no automated guard. |
| **Choice of OOS window length** | Short OOS (<5yr) inflates Sharpe; Ray's caveat text + Ace's KPI card framing depend on it | Analysis Brief §Sample Period + memory:`feedback_completeness_gate.md` | No single rule says "OOS window < 5 years must trigger a warning annotation on the KPI card." Memory-level lesson, not rule. |
| **`signal_column` field in `winner_summary.json`** (should be mandated) | APP-SE1 pre-render validation cannot resolve column | APP-SE1 references it; ECON SOP does not mandate writing it | **Bug origin: contract expected on consumer side but not required on producer side.** |

---

## 4. Boundaries where Evan has been bitten

1. **Wave 1.5 — `winner_summary.json` missing `signal_column`, `target_symbol`.** APP-SE1 (Ace) reads `winner_summary.json.signal_column` per Ace SOP line 247; Evan's SOP does not list this field. Ace added a `_SIGNAL_CODE_TO_COLUMN` fallback map in `probability_engine_panel.py` (commit `519d042`, Wave 3). Root cause: producer-side contract never required the field; consumer-side contract required it. Asymmetry. Still latent on every new pair unless Evan explicitly populates.

2. **Wave 4A — `signals_*.parquet` silently `.gitignore`-excluded on Cloud (HY-IG v2 Probability Engine read-failure).** Blanket `*.parquet` rule silently dropped Evan's deploy-required artifact. Root cause at Evan's boundary: ECON-DS1 said "persist to disk" without specifying "deployable." Fixed by ECON-DS2 + GATE-29 (commit `f295073`). Remaining risk: pairs created before ECON-DS2 (INDPRO, SOFR-TED, Permit, VIX-VIX3M, HY-IG v1) have never been clean-checkout tested; silent regression possible.

3. **HY-IG pair #5 — tournament CSV used `signal_col`/`threshold_method`; `hmm_2state_prob_stress` computed runtime-only, never persisted.** Two separate boundary failures (column-schema alias + missing derived-signal persistence) on the same pair. Fixed by ECON-DS1 and ECON §Tournament canonical column schema. Confirms the "producer-side contract must match consumer's read path" pattern.

4. **HY-IG v2 silent drop of pre-whitened CCF, transfer entropy, quartile-returns (Wave 2 regression before `hy_ig_v2_spy` rerun).** Root cause: Evan's rerun catalog changed; Ray had no diff. Fixed by ECON-C3 producer-side diff + META-VNC. Confirms: reruns are a hot zone for handoff boundary bugs, not just first-run.

5. **Wave 3 — Granger chart silently fell back to Local Projections chart because `granger_by_lag.csv` did not exist.** This is a Vera-side silent-fallback bug, BUT Evan's side contributed: Evan never produced the artifact, so there was nothing for Vera to consume. Fixed by ECON-E1 (added 2026-04-19). Cross-agent pattern: when Evan does not produce a method-specific artifact, Vera's substitute-a-similar-chart default inversely rewards Evan's skip.

6. **Wave 3 — `charts.py` loader was render-only, returned None.** Not on Evan's boundary per se, but the root cause is the same pattern: artifact-existence checks ≠ rendering checks. Evan's `granger_by_lag.csv` and `regime_quartile_returns.csv` could be "present and parseable" yet fail to render under the loader — GATE-27 (VIZ-V5 + APP-ST1) exists now; before 2026-04-19, Evan shipping a valid CSV did not guarantee Ace could render.

**Common thread:** producer-side (Evan) and consumer-side (Ace/Vera) contracts drift. Evan's own Quality Gates check what Evan writes; they do not check what downstream reads.

---

## 5. Proposed new rules

Focus: close concrete bugs. Five rules, highest leverage first.

> **Proposed ECON-H5 — `winner_summary.json` canonical schema**
> - Rule text: `winner_summary.json` MUST include these fields with these exact keys: `pair_id`, `signal_code`, `signal_display_name`, **`signal_column`** (the exact parquet column name in `signals_*.parquet`), **`target_symbol`** (target ticker from Analysis Brief S3), `threshold_code`, `threshold_display_name`, `threshold_value`, `strategy_code`, `strategy_display_name`, `strategy_description`, `lead_value`, `lead_unit`, `lead_description`, `direction`, `oos_sharpe`, `oos_ann_return`, `max_drawdown`, `annual_turnover`, `win_rate`, `max_acceptable_delay_days`, `breakeven_cost_bps`. Absent fields serialize as `null`, never omitted. A pre-handoff assertion (per-pair) verifies the presence of every key.
> - Closes gap: Wave 1.5 `signal_column` / `target_symbol` bug. Ace's SE1 pre-render validation (APP-SE1) expects `signal_column`; Evan's SOP never required it. Ace's trigger cards (`instructional_trigger_cards.py` line 260) hardcode `SPY` when `target_symbol` is absent.
> - Blocking?: **Yes** — blocks GATE-16 (winner summary JSON complete).
> - Cross-reference: APP-SE1 (Ace), APP-SE3 (Ace trigger cards), META-TWJ.

> **Proposed ECON-DS3 — Signal-column-to-signal-code registry (per-pair)**
> - Rule text: Every pair's handoff manifest (`results/{pair_id}/_manifest.json` or `core_models_{date}/_manifest.json`) includes a `signal_registry` block that lists, for each tournament-eligible signal, the triple `{signal_code, parquet_column, display_name}`. The parquet column name MUST match the actual column in `signals_*.parquet` verbatim. ECON-C3 rerun check asserts the triple is stable across reruns or declares a rename in the regression note.
> - Closes gap: The implicit `_SIGNAL_CODE_TO_COLUMN` map in `app/components/probability_engine_panel.py` is a consumer-side workaround for missing producer-side registry. This moves ownership upstream. Addresses the root cause of Wave 1.5.
> - Blocking?: **Yes** for pairs whose Strategy page uses APP-SE1/SE2.
> - Cross-reference: APP-SE1 pre-render validation; ECON-DS1.

> **Proposed ECON-CFO-1 — Multi-writer write-order for `interpretation_metadata.json`**
> - Rule text: `interpretation_metadata.json` is written by three agents. Mandatory write order: (1) Dana writes `indicator_nature`, `indicator_type`, `indicator_id`, `target`, `target_id` (post DATA-D3); (2) Evan writes `expected_direction`, `observed_direction`, `direction_consistent`, `direction_confidence`, `mechanism`, `callout_text`, `recommended_charts`, `supporting_evidence`, `contradictions`, `data_provenance`, `known_stress_episodes` (post tournament); (3) Ray writes `strategy_objective` (post tournament winner inspection). Each writer appends ONLY the fields enumerated above; no writer touches fields owned by another. Writer N verifies N-1's fields are present and raises escalation if absent.
> - Closes gap: multi-writer file with no locking protocol. Evan's SOP §9 enumerates the full schema but does not restrict which fields Evan writes. Risk of Evan overwriting Dana's `indicator_type` on a rerun or Ray's `strategy_objective` landing silently on top of partial Evan output.
> - Blocking?: **Yes** for GATE-4 / GATE-19 / GATE-20 / GATE-21.
> - Cross-reference: META-CFO, DATA-D3, RES-B5.

> **Proposed ECON-H6 — Producer-side consumer-read smoke test**
> - Rule text: Before Evan marks a pair handoff complete, a smoke test (`scripts/econ_consumer_smoke.py {pair_id}`) loads every artifact Evan produced using the exact access path that Ace or Vera use at render time. Specifically: (a) open `signals_*.parquet` and resolve the column name via the same lookup chain as `_resolve_signal_column` in `app/components/probability_engine_panel.py`; (b) open `winner_summary.json` and assert every ECON-H5 field is present and correctly typed; (c) open `tournament_winner.json` and assert every META-TWJ field is present; (d) open `kpis.json` and assert the schema version Ace expects; (e) open every `core_models_{date}/*.csv` and assert row count > 0 + columns match ECON-C2. A single failure blocks handoff.
> - Closes gap: Evan's Quality Gates check what Evan wrote; they do not check what downstream reads. This replicates APP-ST1 for the producer side. Would have caught Wave 1.5 before handoff.
> - Blocking?: **Yes**.
> - Cross-reference: APP-ST1 (Ace's mirror smoke test), GATE-27, GATE-29.

> **Proposed ECON-EX2 — `regime_descriptive_stats.csv` column schema**
> - Rule text: `exploratory_{date}/regime_descriptive_stats.csv` (consumed by Ace's Strategy page Performance tab and by Vera's regime chart) has a registered column schema: `regime_label`, `n_obs`, `pct_time`, `mean_return_ann`, `vol_ann`, `sharpe`, `max_drawdown`, `hit_rate`. Renames require a META-RNF regression note.
> - Closes gap: Ace SOP §3.6 Tab 2 references this file; Evan SOP §ECON-EX1 mentions exploratory deliverables but no per-file schema. Silent-drop risk on reruns.
> - Blocking?: Non-blocking (chart degrades to pending placeholder), but promotes to blocking on reference pairs (GATE-28).
> - Cross-reference: ECON-EX1, ECON-C2, APP-SE2 rendering, GATE-28.

---

## 6. Questions to other agents (for consolidation phase)

1. **@Ace:** APP-SE1 reads `winner_summary.json.signal_column` as "the expected signal column" (Ace SOP line 247). Does Ace need this to be (a) the exact parquet column name verbatim, (b) the tournament `signal_code`, or (c) a display name? My ECON-H5 proposal assumes (a). Confirm?

2. **@Ace:** On `kpis.json`, the ECON SOP specifies `{metric, value, unit, delta}` (§App Dev Handoff) but APP SOP §Data Layer + APP-AF3 reads `{metric, value, unit, label, source_file, source_field}`. Which is the canonical schema? I will update ECON-H3 to match whichever you confirm.

3. **@Vera:** For the `handoff_to_vera_{date}.md` per-method table (ECON-H4), do you validate the `status: ready` claim by opening the CSV, or do you trust Evan's declaration? If the former, we need a rule that says so; if the latter, we need a producer-side assertion that `ready` means `file_exists AND row_count > 0 AND schema_matches_C2`.

4. **@Ray:** For variant families (e.g. `hy_ig_spy` vs `hy_ig_v2_spy`), who owns the `pair_id` naming decision — you, via Analysis Brief, or Lesandro? And does the "v2" suffix trigger a new landing card or a replaced card? This affects both Evan (whether to rewrite `results/hy_ig_spy/` or create a sibling dir) and Ace (landing page).

5. **@Dana:** `interpretation_metadata.json` is currently a 3-writer file (you + me + Ray). My ECON-CFO-1 proposal orders the writes Dana → Evan → Ray. Does your rerun-diff check (DATA-R1) tolerate Evan's fields landing after yours, or do you expect a fully-populated file on Dana's write? If the latter, we need to decouple — e.g. Evan writes `interpretation_metadata_evan.json` and Ray merges at GATE-21 time.

6. **@Ace (highest-priority — BLOCKING future portal builds):** The `live_execution_stub.json` referenced in APP-SE4 has **no producer** in any SOP. Is this intentionally an orphan (always `—` placeholders for now), or should Evan own its creation? If Evan owns it, we need an ECON-SE4 companion rule.

---

**End of audit. 19 produced artifacts inventoried, 6 consumed, 13 gaps flagged, 5 blocking rules proposed. Ready for consolidation.**
