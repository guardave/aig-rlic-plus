# Validation Audit — Econ Evan

**Agent:** Econ Evan
**Date:** 2026-04-19
**Scope:** Two-axis validation of the HY-IG v2 × SPY artifact set. Axis 1: would another Evan, given the same inputs, produce an identical file? Axis 2: does HY-IG v2 actually resolve the stakeholder feedback in spirit, not just letter? Read-only; no SOP or artifact edits.

**Method:** Walked `docs/agent-sops/econometrics-agent-sop.md` (1011 lines) + `docs/standards.md` ECON block + `docs/stakeholder-feedback/20260418-batch.md` (only extant batch) + every on-disk artifact under `results/hy_ig_v2_spy/` + cross-review file `docs/cross-review-20260419-evan.md`. Re-ran line-level checks against the tournament CSV, winner_summary.json, regime_quartile_returns.csv, granger_by_lag.csv, and the schemas.

**Headline:**
- 18 artifacts audited
- 9 reproducibility gaps: 2 critical, 4 moderate, 3 stylistic
- 5 stakeholder-resolution gaps (2 still-open in spirit, 3 formally closed)
- 6 SOP proposals below

---

## Axis 1 — Reproducibility Audit

### 1.1 Tournament tie-break — **CRITICAL**

Evidence from `results/hy_ig_v2_spy/tournament_results_20260410.csv`:

```
S6_hmm_stress, T4_hmm_0.5, P2, 0, 1.274, 11.33, -10.2, 0.5048, 6004, 3.78, True, 2088
S6_hmm_stress, T4_hmm_0.7, P2, 0, 1.274, 11.33, -10.2, 0.5048, 6004, 3.78, True, 2088
```

Two rows have **identical oos_sharpe, ann_return, max_drawdown, win_rate, n_trades, turnover**; differ only in `threshold`. `winner_summary.json` records `threshold_value: 0.5`. The SOP has no tie-break rule. Another Evan, sorting pandas-stably differently (e.g. descending by `max_drawdown` before `oos_sharpe`) could pick 0.7 and produce a different `threshold_value` / `threshold_code` / broker trade log / portal caption. **The SOP §Tournament Design Parameters says "Sorted by rank (best first)" but does not define rank.**

### 1.2 Signal-code naming drift — **CRITICAL**

SOP §Tournament Design Parameters enumerates `S1_ZScore, S2_Percentile, S3_ROC, S4_HMM2, S5_HMM3, S6_MarkovSwitch`. Actual tournament CSV uses `S1_spread_level, S2a_zscore_252d, S2b_zscore_504d, S3a_pctrank_504d, S3b_pctrank_1260d, S4a_roc_21d, S4b_roc_63d, S4c_roc_126d, S5_ccc_bb_spread, S6_hmm_stress, S7_ms_stress, S10_mom_21d, S11_mom_63d, S12_mom_252d, S13_acceleration`. Neither the SOP enumeration nor the `signal_code` field in winner_summary (`S6_hmm_stress`) match the SOP's `S6_MarkovSwitch`. The "S6" in `S6_hmm_stress` is a **per-pipeline registration order**, not a canonical code. Another Evan sourcing signals in a different order (e.g. dropping `S2a`/`S2b` and promoting the others) would ship `S4_hmm_stress` for the same HMM. `winner_summary.schema.json` treats `signal_code` as an arbitrary string with no registry.

### 1.3 Threshold-rule enum inference — **MODERATE**

`winner_summary.json.threshold_rule: "gte"`. Cross-review explicitly flagged this as partial-evidence inference in Wave 4D-1: the P2 strategy family scales exposure proportional to signal strength ABOVE a value, so `gte` was Evan's best guess. SOP lists six enums (`gt`, `lt`, `gte`, `lte`, `crosses_up`, `crosses_down`) with no mapping rule from strategy_family to enum. Another Evan, reading "HMM probability > 0.5" literally, would pick `gt` — producing a different `threshold_rule` with no material effect on rendering but with audit-trail divergence.

### 1.4 OOS period boundaries — **MODERATE**

`winner_summary.json.oos_period_start: "2018-01-01"`, `oos_period_end: "2025-12-31"`. Derived from `oos_n = 2088` trading days, but this is a reverse-engineered inference. SOP has no rule defining OOS window construction. No `oos_split_date`, `oos_fraction`, or `oos_start_policy` field exists in the Analysis Brief template or the ECON SOP. Another Evan could infer the same `oos_n=2088` under a different boundary (e.g. 2017-09-01 → 2025-08-31 ≈ 2088 trading days) with equal textual justification.

### 1.5 Granger max-lag selection — **MODERATE**

`granger_by_lag.csv` has lags 1–12. The ECON SOP Rule E1 schema says `lag: 1, 2, …, max_lag` but never defines `max_lag`. For monthly indicator → monthly target, 12 is a natural choice (1 year); but another Evan might pick 24 (2 years) or use an information-criterion-selected optimal lag. The 12-month choice and the resulting p-value for the headline "best lag 5" (F=4.07, p=0.0014) hinges on this implicit choice. Not captured in the sidecar methodology file.

### 1.6 Quartile regime definition — **MODERATE**

`regime_quartile_returns_methodology.md` documents the choices (monthly resampling, spread-level, unconditional empirical quartiles, N=311). But the SOP Rule E2 does not prescribe:
- Observation frequency (monthly vs daily → different N, different Sharpe signs)
- Quartile variable (spread LEVEL vs spread RANK vs spread CHANGE — see §Axis 2 below for S18-8 implications)
- Percentile method (pandas `qcut` / `rank(pct=True)` / `numpy.percentile` with linear/nearest/lower interpolation — each can bucket a borderline month differently)

The methodology sidecar captures Evan's specific choices (unconditional empirical, month-end, log returns) but captures them only for THIS pair. Another Evan on a new pair would default to different choices and not know they deviated. Discretion is **captured in the sidecar, uncaptured in the SOP**.

### 1.7 Variant-family winner selection — **MODERATE**

`winner_summary.signal_code = S6_hmm_stress`. But S6_hmm_stress with T4_hmm_0.5 P2 AND S6_hmm_stress with T4_hmm_0.7 P2 both have Sharpe 1.274. And `S7_ms_stress` family exists in the tournament too, with its own regime probabilities. There is no SOP rule that says "when multiple signal families are within ε of each other, pick the simpler/older/default one." Another Evan sorting the tournament differently could pick S7_ms_stress.

### 1.8 `signal_column` — `signal_code` mapping — **MODERATE (partially captured)**

`winner_summary.json` has `signal_column: hmm_2state_prob_stress`, `signal_code: S6_hmm_stress`. Cross-review documented this as the canonical answer to Wave 1.5. But the relationship between the two fields is not registered anywhere: the parquet column name stays identical even if the registration order puts the HMM at position 4 instead of 6. The schema (winner_summary.schema.json) documents each field but not their cross-invariant.

### 1.9 Regime / quartile direction — **STYLISTIC**

Methodology sidecar says `Q1 = lowest-spread quartile (tightest credit)`. Another Evan might invert (Q1 = most stressed = widest-spread) — both conventions are defensible; SOP has no rule. Cross-review memory notes "stress = red" encoding convention is shared with Vera, but quartile naming convention is not.

### 1.10 Quartile artifact filename collision — **STYLISTIC**

Both `core_models_20260410/quartile_returns.csv` (daily-resolution, Rule C2 schema) AND `regime_quartile_returns.csv` (monthly-resolution, Rule E2 schema) exist. Methodology sidecar documents the relationship, but a reader of ONLY the file tree cannot tell which is canonical for the CCF Evidence chart without reading the sidecar. SOP Rule E2 says the `{method_prefix}_quartile_returns.csv` form is used only when multiple quartile families coexist — the current state has TWO quartile-returns files but does not use the prefix form. Captured in handoff_to_vera.md, not enforced.

### Axis 1 summary table

| # | Artifact | SOP rule | Deterministic? | Discretion point | Captured? | Proposed fix |
|---|----------|----------|:---------------:|------------------|:---------:|--------------|
| 1 | tournament_winner.json / winner_summary.json (tie-break) | §Tournament Design ("Sorted by rank") | No | `threshold_value` when oos_sharpe ties | No | **ECON-T3** (below) |
| 2 | winner_summary.json.signal_code | §Tournament S-code list | No | S-code registration order varies across pipelines | No | **ECON-DS3** (below, mirrors cross-review) |
| 3 | winner_summary.json.threshold_rule | ECON-H5 (enum listed) | No | Mapping from strategy family / threshold semantics to enum | Partial (cross-review only) | **ECON-T4** (below) |
| 4 | winner_summary.json.oos_period_start/end | ECON-H5 (format) | No | OOS boundary derivation | No | **ECON-T5** (below) |
| 5 | granger_by_lag.csv | ECON-E1 (schema) | No | max_lag choice | No | **ECON-E1.1** (below) |
| 6 | regime_quartile_returns.csv | ECON-E2 (schema) | Partial | Frequency, variable, percentile method | In sidecar only | **ECON-E2.1** (below) |
| 7 | winner_summary.json (variant winner) | Implicit "best of tournament" | No | Within-epsilon family selection | No | Part of **ECON-T3** |
| 8 | signal_column / signal_code pairing | ECON-H5 text + schema | Partial | Cross-field invariant | Partial (schema docs each) | Part of **ECON-DS3** |
| 9 | quartile_returns.csv file naming | Rule E2 prefix convention | Partial | Canonical vs legacy flag | Partial (handoff doc) | Stylistic; non-blocking |

**Count:** 2 critical (rows 1, 2); 4 moderate (rows 3, 4, 5, 6, 7 — 7 counts under variant selection); 3 stylistic (rows 8, 9, and the Q1/Q4 direction convention).

---

## Axis 2 — Stakeholder Resolution Audit

### 2.1 S18-8 — Annualized SPX return Q1–Q4 — **SPIRIT GAP**

**Stakeholder ask:** Restore the "Annualised SPX return by quartile Q1-Q4" table/chart that was present in the earlier version.

**Current state:** `regime_quartile_returns.csv` delivered with schema `quartile, n_months, ann_return, ann_vol, sharpe, max_drawdown`. Monthly observations, spread-LEVEL buckets (2.575 / 3.240 / 4.620 pp cutoffs).

**Question from the task prompt:** "CCF had spread-rank quartiles; yours is spread-level quartiles. Are they equivalent?"

**Analysis:**
- The stakeholder comment (S18-8) was filed against the CCF Evidence page, where the prior version's chart was labeled as coming from a CCF-related cross-correlation analysis. CCF analysis is a bivariate lag-based method that does not inherently produce "quartiles" — the prior chart almost certainly derived quartiles from the spread series itself, either by LEVEL or by some CCF-related statistic (lead correlation magnitude, pre-whitened residual, etc.).
- `regime_quartile_returns_methodology.md` is transparent that quartiles are by **level**. It says nothing about spread-rank or CCF-residual buckets.
- For a monotone transformation (level → rank), the quartile membership is IDENTICAL — a spread value at the 75th percentile is always in Q3 regardless of whether you bucket by level or rank. So spread-level quartiles ARE equivalent to spread-rank quartiles for the purpose of defining Q1–Q4 subsets.
- BUT: if the prior version bucketed by a different variable (e.g. CCF cross-correlation magnitude, or lag-K correlation strength), the two are NOT equivalent.

**Verdict:** Probably spirit-met, conditional on the prior version's bucketing rule having been spread-level-or-rank (which is the most natural interpretation of "annualised SPX return by quartile Q1-Q4" on a CCF page). If prior was CCF-magnitude-bucketed, the current artifact silently substitutes. **This requires Lesandro to adjudicate** — see Axis 4.

### 2.2 S18-11 — Granger chart identical to Local Projections — **LETTER MET, SPIRIT AT RISK**

**Stakeholder ask:** "點解同 level 2 Local Projections 個 chart 睇落一樣既?" — produce a standalone Granger chart distinct from Local Projections.

**Current state:** `granger_by_lag.csv` delivered with 12 lags of F-statistic + p-value (ECON-E1 schema).

**Gap:** The stakeholder's question was phrased at the chart level ("chart looks the same"). The artifact delivers the F-statistic-by-lag data that Vera can render as a bar chart. This is structurally different from the Local Projections coefficient plot (which has horizon on x-axis and coefficient+CI on y-axis). So the LETTER is met.

However, the stakeholder's deeper concern was "Granger is not interpretable from a chart that looks like impulse-response". The current artifact, rendered as "F-statistic by lag", invites a different misinterpretation: a reader may read the F-statistic as if it were a coefficient magnitude. A per-lag F-statistic without a significance threshold line is just as opaque. The SOP says "with α=0.05 F-critical horizontal line" in the handoff doc (letter), but if Vera renders without it, the stakeholder's original complaint reappears under a new visual.

**Verdict:** Letter met (distinct artifact produced). Spirit is Vera's responsibility now (VIZ-V3), but Evan's artifact does not ship the F-critical values for each lag even though `df_num` and `df_den` are present (Vera or Ace would need to compute F-critical client-side). Silent handoff-boundary risk.

### 2.3 S18-8 / S18-11 related: unit discipline (A2)

The `regime_quartile_returns.csv` columns carry no unit row. `ann_return: 0.185838` — is this a ratio (0.1858 = 18.58%) or a percent (0.186% = 0.19 bps)? The ECON-E2 schema says "decimal, e.g. 0.12 = 12%" (unambiguous in spec), but the CSV itself has no `unit` column or `_meta.json` sidecar enumerating units. Rule A2 (Vera-owned) applies to axis labels, but the raw artifact Evan hands off has the same ambiguity. Defense 2 reconciliation depends on the consumer knowing the unit.

### 2.4 Broker-style trade log (C4)

Sampled `winner_trades_broker_style.csv`: header comment is complete, all 10 columns present in correct order (`trade_date, side, instrument, quantity_pct, price, notional_usd, commission_bps, commission_usd, cum_pnl_pct, reason`). Starting capital disclaimer present. First-row initial entry present. **Letter AND spirit met.** This is the best-executed ECON-C4 delivery I have seen.

### 2.5 Tournament CSV canonical column names (§Tournament Design)

Sampled `tournament_results_20260410.csv` header: `signal, threshold, strategy, lead_days, oos_sharpe, oos_ann_return, max_drawdown, win_rate, n_trades, annual_turnover, valid, oos_n`. Matches the SOP's prohibited-aliases fix (no `signal_col`, no `threshold_method`). **Letter AND spirit met.** Note however: no `lookback` column (SOP canonical schema enumerates `lookback`) — implicit single lookback applied; the artifact silently omits this dimension. Documented in regression note? Not verified — regression note is 98kB and not fully re-read here, but this is a candidate gap.

### 2.6 S18-1 (Probability Engine Panel) — Evan's role

S18-1 is primarily an Ace deliverable (APP-SE1/SE2). Evan's role is to provide the HMM probability column that Ace consumes. `signals_20260410.parquet` exists and contains `hmm_2state_prob_stress`. `winner_summary.json.signal_column` points to it. **Letter AND spirit met on Evan's side.**

### Axis 2 summary table

| Stakeholder item | Claimed SOP rule | HY-IG v2 evidence | Spirit met? | Gap |
|------------------|-------------------|-------------------|:-----------:|-----|
| S18-8 | ECON-E2 | `regime_quartile_returns.csv` exists, spread-level monthly | **CONDITIONAL** | Spread-level ≡ spread-rank for quartile membership, BUT prior version's bucketing rule not documented — if CCF-magnitude-bucketed, silent substitution |
| S18-11 | ECON-E1 | `granger_by_lag.csv` exists, 12 lags F-stat + p-value | **LETTER MET** | F-critical not pre-computed in artifact; per-lag critical values must be derived by Vera |
| A2 (unit discipline) | Rule A2 (Vera) + ECON-E2 (spec says decimal) | CSV has no unit column, no `_meta.json` sidecar | **LETTER** | Unit is in SOP spec, not in the artifact — consumer must trust Evan's adherence |
| C4 (broker trade log) | ECON-C4 | Broker CSV: all 10 cols, header disclaimer, first-row entry | **YES** | None |
| Tournament canonical schema | §Tournament Design Parameters | CSV uses canonical names, no legacy aliases | **MOSTLY** | `lookback` column absent — either skipped dimension (ok if documented) or silent omission |
| S18-1 (Prob Engine panel) | ECON-DS1, ECON-H5 | signals parquet + winner_summary.json complete | **YES** | None on Evan's side |

**Count:** 2 still-open-in-spirit (S18-8 conditional, S18-11 F-critical); 3 formally closed (C4, canonical schema, S18-1); 1 pending verification (lookback column).

---

## Axis 3 — Proposed SOP fixes

High-leverage; mechanize existing discretion; ≤7 proposals. Ordered by severity.

> **Proposed ECON-T3 — Tournament Tie-Break and Rank Definition**
> - Rule text: The tournament sort order is: (1) DESC `oos_sharpe`; (2) DESC `oos_ann_return`; (3) ASC `max_drawdown` (most negative first → less negative wins); (4) ASC `n_trades` (fewer trades wins — simpler strategy); (5) ASC tuple of `(signal, threshold, strategy, lead_days, lookback)` lexicographic as a final deterministic disambiguator. This sort produces `rank` per the canonical tournament schema. The winning row is `rank == 1`. When the within-epsilon tie-break is used (rows 1–2 differ by <0.01 in oos_sharpe), a `tournament_tie_note.md` must be written documenting the near-tie set and the chosen row.
> - Closes gap: Row 1 (tournament tie — HY-IG v2 ships threshold_value=0.5 where 0.7 has identical Sharpe/return/DD).
> - Blocking?: **Yes** — blocks GATE-16 (winner_summary complete) because `threshold_value` is non-deterministic without this rule.

> **Proposed ECON-DS3 — Signal Code Registry (per-pair, author: Evan)**
> - Rule text: Every pair produces `results/{pair_id}/_signal_registry.json` mapping each tournament-eligible signal to a tuple `{signal_code, parquet_column, display_name, family, canonical_order}`. `signal_code` MUST be stable across reruns (if the pipeline adds or removes a signal, the remaining codes do NOT renumber — append-only). `canonical_order` is a non-negative integer for sort stability. Schema-registered at `docs/schemas/signal_registry.schema.json` per META-CF. Producer validates before save; `winner_summary.signal_code` MUST match one of the registered codes.
> - Closes gap: Row 2 (S-code registration-order drift — `S6_hmm_stress` would rename to `S4_hmm_stress` if S2a/S2b were dropped on a rerun, silently breaking the cross-pair registry). Also closes cross-review Proposed ECON-DS3 (same rule, different framing).
> - Blocking?: **Yes** for any pair that uses `winner_summary.signal_code` (effectively all pairs post-ECON-H5).

> **Proposed ECON-T4 — Threshold-Rule Enum Mapping**
> - Rule text: Add to the ECON SOP (§Tournament Design) a mapping table: strategy family + threshold semantic → `threshold_rule` enum. Specifically: P1_long_cash + "signal > threshold (stress)" → `gt`; P1 + "signal < threshold (calm)" → `lt`; P2_signal_strength + "scale up when above" → `gte` (inclusive because the position is continuous at the boundary); P2 + "scale up when below" → `lte`; crosses → `crosses_up` / `crosses_down`. Producer asserts the chosen enum against the mapping before `winner_summary.json` save.
> - Closes gap: Row 3 (threshold_rule=gte inference captured as partial-evidence in Wave 4D-1).
> - Blocking?: Non-blocking — existing `gte` value is not rendering-critical — but promotes to blocking at reference-pair acceptance.

> **Proposed ECON-T5 — OOS Window Construction Rule**
> - Rule text: Every pair's Analysis Brief (and `results/{pair_id}/oos_split_record.json`) records: `is_start`, `is_end`, `oos_start`, `oos_end`, `split_policy` (one of `fixed_date`, `fraction_70_30`, `fraction_80_20`, `walk_forward_k_folds`), and `oos_trading_day_count`. `winner_summary.oos_period_start/end` MUST be copied from this record, not reverse-inferred from `oos_n`. Pipeline script asserts the copy-through before save.
> - Closes gap: Row 4 (OOS boundary inferred from oos_n=2088 with no audit trail).
> - Blocking?: **Yes** for GATE-7 (tournament results) and GATE-16 (winner summary complete).

> **Proposed ECON-E1.1 — Granger Max-Lag Default and F-Critical Emission**
> - Rule text: Amend ECON-E1 schema with two additions: (a) mandatory default `max_lag = 12` for monthly indicators, `max_lag = 21` for daily indicators (single trading month), overridable via Analysis Brief with a design_note rationale; (b) add `f_critical_95` (float) column computed from `scipy.stats.f.ppf(0.95, df_num, df_den)` per-lag, so consumers can render the significance line without recomputation.
> - Closes gap: Row 5 (max_lag implicit) and Axis 2.2 (F-critical not shipped).
> - Blocking?: **Yes** — existing pair's CSV is missing `f_critical_95` column; enforcing the schema bump on the next rerun cycle.

> **Proposed ECON-E2.1 — Quartile Methodology Sidecar Mandatory**
> - Rule text: Every `regime_quartile_returns.csv` (and variant-prefixed quartile files) MUST ship with `{filename}_methodology.md` sidecar enumerating: (a) observation frequency (daily/monthly/weekly); (b) bucketing variable (`{variable_name}_level` / `{variable_name}_rank` / `{variable_name}_zscore` / custom); (c) percentile method (`pandas.qcut` / `numpy.percentile` interpolation mode); (d) cutoff values; (e) return convention (arithmetic / log / geometric-annualized); (f) risk-free-rate treatment in Sharpe. Template lives at `docs/templates/quartile_methodology_template.md`. Schema-registered as META-CF companion.
> - Closes gap: Row 6 (quartile discretion captured only for THIS pair, not SOP-level). Also underwrites S18-8 spirit check (§Axis 2.1) — enables prior-version bucketing comparison.
> - Blocking?: Non-blocking for existing file (HY-IG v2 already ships this sidecar, probably by accident of Wave 2A diligence); blocking for new pairs.

> **Proposed ECON-C2.1 — Unit Column or Sidecar for Numeric Artifacts**
> - Rule text: Every ECON artifact row with numeric columns ships either (a) a `unit` row/column in the CSV, OR (b) a JSON sidecar `{filename}.unit.json` mapping column name → unit string (e.g. `{ "ann_return": "ratio", "max_drawdown": "ratio", "ann_vol": "ratio" }`). Units vocabulary: `ratio`, `bps`, `pct`, `index`, `usd`, `count`, `date`. Producer asserts unit correctness against a known-fact value before save (Defense 1 requires this anyway; this rule operationalizes it at the column level).
> - Closes gap: Axis 2.3 (unit ambiguity in `regime_quartile_returns.csv`).
> - Blocking?: Non-blocking on existing artifacts; blocking on new pairs or reference-pair acceptance.

**7 proposals. Prioritize ECON-T3, ECON-DS3, ECON-T5 as the highest-severity (each closes a gap where another Evan could produce a materially different artifact).**

---

## Axis 4 — Questions to Lesandro

1. **S18-8 equivalence ruling (blocking for acceptance):** Do we accept spread-LEVEL quartiles as spirit-equivalent to whatever bucketing the prior CCF page used? The prior-version bucketing rule is not in the regression_note and no prior-version artifact is on disk for direct comparison. Three possible rulings: (a) yes, equivalent for acceptance; (b) must reconstruct prior version and diff; (c) inadequate but acceptable with a documented caveat in `acceptance.md`.

2. **Tournament tie-break policy (blocking, per ECON-T3):** Two rows with identical oos_sharpe 1.274 exist in HY-IG v2 tournament. I picked the lower threshold (0.5) via implicit pandas-stable-sort; the other option (0.7) has identical headline metrics. Do you (a) endorse the stable-sort lexicographic final tie-break, (b) prefer to cascade through `max_drawdown` / `n_trades` / `annual_turnover` as a richer rank, or (c) force the pipeline to escalate ties > 0.001 Sharpe apart to Lesandro manually?

3. **Signal-code stability policy (blocking, per ECON-DS3):** If a future HY-IG v3 drops S2a_zscore_252d from the signal catalog, do the remaining codes renumber (S2b → S2a, S3a → S2b, …, S6 → S5) or stay append-only (S2b, S3a, …, S6 unchanged)? Append-only is my default recommendation; user-facing "S6" becomes an identity key, not an ordinal. Need ruling to register in schema.

4. **OOS window policy (blocking, per ECON-T5):** Project-wide default — `fixed_date` (2018-01-01) or `fraction_80_20`? The former is easier to audit but depends on sample coverage; the latter is structure-preserving but date boundaries differ across pairs. Need one-line ruling to seed every pair's `oos_split_record.json`.

5. **Granger max-lag default (per ECON-E1.1):** 12 monthly / 21 daily are my recommendation. A stakeholder could argue for 24 monthly (2 years) for slow-moving regime indicators. One-line ruling so I can default every new pipeline with confidence.

6. **Lookback-column status (Axis 2.5):** Tournament CSV has no `lookback` column — either the pipeline applies a single implicit lookback (which is fine but must be documented in design_note.md) or lookback is not a tournament dimension for HY-IG v2 (which would warrant a ECON-T1 exception note). Which is it? Regression note is 98kB — I need a direct pointer.

---

## Appendix — Artifacts audited (18)

Under `results/hy_ig_v2_spy/`:

1. `winner_summary.json` — validates against `docs/schemas/winner_summary.schema.json` v1.0.0 (ECON-H5)
2. `tournament_winner.json` — META-TWJ canonical schema
3. `tournament_results_20260410.csv` — §Tournament Design canonical column schema (minus `lookback`)
4. `winner_trade_log.csv` — internal schema (ECON-C4 #1)
5. `winner_trades_broker_style.csv` — broker schema (ECON-C4 #2)
6. `signals_20260410.parquet` — ECON-DS1
7. `granger_by_lag.csv` — ECON-E1
8. `regime_quartile_returns.csv` — ECON-E2
9. `regime_quartile_returns_methodology.md` — E2 sidecar (ad-hoc, to be promoted to ECON-E2.1)
10. `handoff_to_vera_20260419.md` — ECON-H4
11. `stationarity_tests_20260410.csv` — DATA-DD3 (produced by Dana, audited for Evan consumption)
12. `interpretation_metadata.json` — DATA-D6 / META-CFO multi-writer
13. `execution_notes.md` — GATE-18
14. `regression_note_20260419.md` — META-RNF (98kB, sampled only)
15. `core_models_20260410/ccf_prewhitened.csv` — C2
16. `core_models_20260410/granger_causality.csv` — C2 (summary, distinct from #7)
17. `core_models_20260410/quartile_returns.csv` — C2 (daily-resolution, distinct from #8)
18. `core_models_20260410/hmm_states_2state.parquet` — C2

**End of audit.**
