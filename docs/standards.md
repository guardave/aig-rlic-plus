# AIG-RLIC+ Standards — Canonical Rule Registry

**Version:** 1.0
**Effective date:** 2026-04-12
**Status:** Canonical rulebook for the AIG-RLIC+ multi-agent portal system.

This document is the single, authoritative index of every blocking rule in the AIG-RLIC+ SOP system. Each rule carries a stable ID, a one-line description, and a pointer back to the SOP section that owns the detailed specification. SOP files remain the source of truth for rule text; this document is the source of truth for rule identity and inventory.

---

## Scope

The rules registered here govern producer agents, gate reviewers, and cross-cutting meta-rules.

## Rule ID Format

Rule IDs use the pattern `<PREFIX>-<LETTER><NUMBER>` (legacy, stable) or `<PREFIX>-<NUMBER>` (gate items).

| Prefix | Domain | Owner |
|--------|--------|-------|
| DATA | Data-stage rules | Data Dana |
| ECON | Econometrics-stage rules | Econ Evan |
| VIZ | Visualization-stage rules | Viz Vera |
| RES | Research-stage / narrative rules | Research Ray |
| APP | Portal-assembly rules | AppDev Ace |
| QA | QA / independent-verification rules | QA Quincy |
| GATE | Completeness-gate items | Lead Lesandro |
| META | Cross-cutting meta-rules | Lead Lesandro |

Where a rule already has a stable short ID in its SOP (e.g., `C1`, `A3`, `D1`, `RES-4`), the registered ID preserves that short form as the suffix. New IDs assigned by this document are listed in the "Newly Assigned IDs" note at the bottom.

## Recent Changes

See [`sop-changelog.md`](sop-changelog.md) for the chronological record of rule additions and modifications. New rules are first entered into the changelog, then registered here.

---

## DATA — Data Agent Rules (Data Dana)

Source: [`docs/agent-sops/data-agent-sop.md`](agent-sops/data-agent-sop.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| DATA-D1 | Series Preservation on Reruns — every column in the prior master parquet is preserved on rerun, or the drop is documented in a regression note. | §6 Rule D1 |
| DATA-D2 | Default Unit Convention Registry — canonical column names carry canonical units; column suffix and data-dictionary Unit field must agree. | §6 Rule D2 |
| DATA-D3 | Classification Decision Procedure — Dana follows the mandatory workflow for indicator_nature/indicator_type and confirms a matching Rule C1 category exists before writing interpretation_metadata.json. | §6 Rule D3 |
| DATA-D5 | Machine-Readable Dataset Schema Sidecar — every master parquet ships with `data/{subject}_{frequency}_schema.json` conforming to `docs/schemas/data_subject.schema.json` (column-level dtype, unit, display_name, direction, description). Closes the Wave-2A 100x unit bug at the artifact layer. Producer runs `scripts/validate_schema.py` before handoff. | §6 Rule DATA-D5 |
| DATA-D6 | Classification Schema Versioning Contract — `results/{id}/interpretation_metadata.json` validates against `docs/schemas/interpretation_metadata.schema.json` with `schema_version` and `owner_writes` fields. Closes ECON-CFO-1 multi-writer race (deterministic dana→evan→ray merge order) and the ad-hoc field-addition pattern. | §6 Rule DATA-D6 |
| DATA-DD1 | Data Dictionary — every delivered dataset carries a dictionary with Display Name, Direction Convention, Effective Start, Unit, SA status, known quirks. | §6 Deliver |
| DATA-DD2 | Benchmark Inclusion — every pair dataset includes the target-class benchmark series (SPY for equities, AGG for fixed income, etc.). | §6 Deliver |
| DATA-DD3 | Stationarity Test Delivery — ADF/KPSS/PP results delivered as a structured table; Dana owns execution, Evan reviews. | §5 Validate |
| DATA-DD4 | Classification Metadata Ownership — Dana sets indicator_nature and indicator_type; Ray owns strategy_objective. | §6 Deliver |
| DATA-H1 | Data-to-Econometrics Handoff — structured handoff includes parquet path, data dictionary, summary stats, stationarity table. | Handoff Specifications |
| DATA-H2 | Data-to-Viz Handoff — direct-to-Vera channel for exploratory/quality charts must include Display Name metadata. | Handoff Specifications |
| DATA-H3 | Partial Delivery Protocol — partial deliveries are marked with a manifest of what is missing. | Partial Delivery Protocol |
| DATA-E1 | Expedited Mid-Analysis Requests — Dana accepts expedited single-variable requests from Evan during diagnostics, with urgency flag. | Expedited Protocol |
| DATA-N1 | Non-MCP Sourcing Protocol — document source, scrape cadence, and Data Access Risk (Low/Medium/High). | Non-MCP Sourcing Protocol |
| DATA-B1 | Batch Data Availability Pre-Check — for multi-indicator sprints, pre-check availability before sourcing. | Batch Operations |
| DATA-B2 | Shared Indicator Deduplication — deduplicate shared indicator series across pair deliveries. | Batch Operations |
| DATA-Q1 | Quality Gate Checklist — every deliverable passes Dana Quality Gates (including DATA-D1 column diff). | Quality Gates |
| DATA-R1 | Classification Rerun Diff — on every rerun, diff new interpretation_metadata.json against prior; flag in regression note. | Quality Gates |
| DATA-VS | Status Vocabulary Self-Check — all status labels in `_status` columns, `interpretation_metadata.json`, and data-dictionary files drawn from canonical list (Available/Pending/Validated/Stale/Draft/Mature/Unknown); novel terms escalated to Lead. Companion to RES-VS. Addresses S18-4. | §Quality Gates Rule DATA-VS |
| DATA-D11 | Reference-Pair Sidecar Gate (Blocking) — for any pair undergoing reference-pair acceptance (per META-RPD), `data/{pair_id}_schema.json` MUST exist on disk and validate OK against `docs/schemas/data_subject.schema.json`. A schema with no reference instance is a paper rule. Blocking: acceptance.md cannot be signed without the sidecar. Non-reference pairs receive a GATE-24-class warning. Added 2026-04-19 (Wave 5B-2). Cross-ref DATA-D5, GATE-28, META-RPD, META-ELI5. | §6 Rule DATA-D11 |
| DATA-D12 | Column-Suffix Linter (Blocking) — mechanical pre-save linter enforcing DATA-D2 suffix convention (`_bps`, `_pct`, `_ratio`, `_usd`, `_pct_mom`, `_pct_yoy`, `_ret`, `_vol_ann_pct`, `_idx`). Fails the save on any numeric unit-valued column without a matching suffix. Cross-agent contract: Vera's VIZ-A2 axis builder, Ray's RES-4 dual-notation narrative, Ace's KPI renderer all read the suffix. Grandfathering allowed until next rerun, with regression_note mapping. Added 2026-04-19 (Wave 5B-2). Cross-ref DATA-D2, DATA-D5, VIZ-A2, RES-4, META-ELI5. | §6 Rule DATA-D12 |
| DATA-D13 | Manifest + Display-Name Registry Bootstrap — canonical `data/manifest.json` (schema `docs/schemas/data_manifest.schema.json`) tracks every data artifact with `{path, source, refresh_ttl_days, schema_ref, last_updated, pairs}`; canonical `data/display_name_registry.csv` (schema `docs/schemas/display_name_registry.schema.json`) maps parquet column names to chart-ready labels. Dana produces, Evan/Vera/Ray/Ace consume. Bootstrap requirement: both files exist and cover the reference pair's columns. Added 2026-04-19 (Wave 5B-2). Cross-ref META-CF, META-XVC, DATA-D5, DATA-D12. | §6 Rule DATA-D13 |

---

## ECON — Econometrics Agent Rules (Econ Evan)

Source: [`docs/agent-sops/econometrics-agent-sop.md`](agent-sops/econometrics-agent-sop.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| ECON-C1 | Category-Specific Mandatory Method Catalog — every pair runs the mandatory methods for its indicator_type before tournament. | §2.5 Rule C1 |
| ECON-C2 | Mandatory Output Schema Per Method — each mandatory method writes to a named file with exact column schema in results/<pair>/core_models_<date>/. | §2.5 Rule C2 |
| ECON-C3 | Producer-Side Rerun Regression Check — Evan runs method-coverage and numeric-diff checks against prior version before handoff. | §2.5 Rule C3 |
| ECON-C4 | Dual Trade Log Output — winner trade log produced in both internal schema and broker-style CSV. | §2.5 Rule C4 |
| ECON-DS1 | Derived Signal Persistence Rule — every derived signal (HMM prob, Markov state, z-score, composite) is persisted to results/{id}/signals_{date}.parquet. | Derived Signal Persistence |
| ECON-DS2 | Deploy-Required Artifact Allowlist — every Evan-produced artifact read by `app/` at page-render time must be deployable via `.gitignore` carve-out (allowlist `!` + `git add -f`) or build-time regeneration script; "works on my laptop" silent non-deployment is a violation. Cross-ref GATE-29. Added 2026-04-19 after HY-IG v2 Probability Engine Cloud read-failure. | §ECON-DS2 |
| ECON-SS1 | Model Specification Step — document functional form, variable selection, identification strategy before estimation. | §5 Model Specification |
| ECON-EX1 | Exploratory Analysis Deliverables — correlations, lead-lag, rolling relationships saved to results/{id}/exploratory_*/. | §4 Exploratory |
| ECON-ES1 | Estimation Standards — report HC3 robust SEs by default; clustered SEs for panel; bootstrapped for non-standard inference. | §6 Estimation |
| ECON-DG1 | Diagnostics Mandatory — every model runs residual, specification, and stability diagnostics; failures escalate to Lesandro. | §7 Diagnostics |
| ECON-SA1 | Sensitivity Analysis — every headline result has at least one sensitivity check (sample, spec, transformation). | §8 Sensitivity |
| ECON-H1 | Chart Request Template — Evan submits structured chart requests to Vera (type, source, variables, insight, audience, annotations). | Chart Request Template |
| ECON-H2 | App Dev Handoff Template — Evan delivers headline findings, KPI values, backtest performance, strategy rules to Ace. | App Dev Handoff Template |
| ECON-H3 | KPI File Mandatory — every pair produces a KPI file Ace consumes without re-computation. | App Dev Handoff |
| ECON-T1 | Tournament Design Parameters — target-class-aware tournament parameters (holding periods, thresholds, costs). | Tournament Design |
| ECON-T2 | Target-Class-Aware Backtest Parameters — backtest parameters (frequency, trading costs, slippage) match target class. | Backtest Parameters |
| ECON-M1 | Mid-Analysis Data Requests — structured expedited request channel to Dana during diagnostics. | Mid-Analysis Data Requests |
| ECON-Q1 | Quality Gates — Evan checklist passed before handoff. | Quality Gates |
| ECON-D2 | Defense 2 Reconciliation — Evan validates upstream data with known-fact sanity checks before using. | Defense 2 |
| ECON-E1 | Granger By-Lag Artifact — every Granger causality test persists `results/{id}/granger_by_lag.csv` with columns `lag`, `f_statistic`, `p_value`, `df_num`, `df_den`; Vera renders F-statistic-by-lag bar chart per VIZ-V3. Addresses S18-11. | §Derived Signal Persistence Rule E1 |
| ECON-E2 | Quartile Returns Artifact — every regime/quartile analysis (CCF, HMM, VIX, z-score quartiles) persists `results/{id}/regime_quartile_returns.csv` (renamed from `quartile_returns.csv` to disambiguate from Rule C2's `quantile_regression.csv`; use `{method_prefix}_quartile_returns.csv` when multiple quartile families coexist) with columns `quartile`, `n_months`, `ann_return`, `ann_vol`, `sharpe`, `max_drawdown`; Vera renders quartile-return bar chart per VIZ-V4. Addresses S18-8. | §Derived Signal Persistence Rule E2 |
| ECON-H4 | Per-Method Chart Artifact Handoff — Evan delivers an explicit table to Vera listing method name, result CSV path, expected chart type per VIZ canonical catalog, and status (ready/blocked/pending) for every mandatory method in Rule C1; blocked entries trigger a "chart pending" placeholder (GATE-25) rather than a silent substitute. Addresses S18-11, S18-8 (handoff clarity). | §App Dev Handoff Template ECON-H4 |
| ECON-H5 | Winner Summary JSON Contract (per META-CF) — `results/{pair_id}/winner_summary.json` conforms to the canonical JSON Schema at `docs/schemas/winner_summary.schema.json` (v1.0.0, owner: Evan). Required fields include `pair_id`, `generated_at`, `signal_column` (exact parquet column name), `signal_code` (tournament identifier), `target_symbol`, `threshold_value`, `threshold_rule`, `strategy_family`, `direction`, and OOS metrics (`oos_sharpe`, `oos_ann_return`, `oos_max_drawdown`, `oos_n_trades`, `oos_period_start`, `oos_period_end`). Producer runs `scripts/validate_schema.py` before save and blocks on failure. Resolves APP-WS1 (consumer-side pre-render contract) in the same artifact. Added 2026-04-19 (Wave 4C-2). | §App Dev Handoff Template ECON-H5 |
| ECON-T3 | Tournament Tie-Break Cascade (Blocking) — winner selection applies a 5-step deterministic cascade: (1) higher `oos_sharpe`; (2) higher `oos_ann_return`; (3) lower absolute `oos_max_drawdown`; (4) higher `oos_n_trades`; (5) lexicographic `signal_code`. Any resolution beyond step 1 writes `results/{pair_id}/tournament_tie_note.md` documenting the near-equivalent candidate set. Closes silent non-determinism where pandas-stable-sort resolved identical-Sharpe ties. Cross-ref META-XVC (cascade changes = methodological divergence). Added 2026-04-19 (Wave 5B-2). | §ECON-T3 |
| ECON-OOS1 | OOS Window Ownership — OOS window is owned by Evan exclusively and persisted in `results/{pair_id}/oos_split_record.json` (`owner`, `split_policy_id`, `in_sample_end`, `oos_start`, `oos_end`, `sample_size_months`, `justification`). Downstream agents (Ray narrative, Ace display) read this file; independent recomputation is a contract violation. `winner_summary.json.oos_period_start/end` copied verbatim from this record — no reverse-inference from `oos_n`. Cross-ref META-XVC (OOS changes = divergence). Added 2026-04-19 (Wave 5B-2). | §ECON-OOS1 |
| ECON-OOS2 | OOS Window Sizing Criterion (Blocking) — generalizable formula for all 73 pairs: `span_months = min(max(36, round(total_sample_months × 0.25)), 120)`. When `total_sample_months < 48` → `oos_status = "insufficient_sample"` BLOCKING unless Lead waiver in acceptance.md. `split_policy_id: "v1_max36_25pct_cap120"` (versioned, bumps traceable). Every user-facing render of OOS window carries a dual technical + ELI5 label per META-ELI5. Cross-ref ECON-OOS1, META-ELI5. Added 2026-04-19 (Wave 5B-2). | §ECON-OOS2 |
| ECON-DS3 | Signal Code Registry (per META-CF) — canonical append-only registry at `docs/schemas/signal_code_registry.json` (schema `docs/schemas/signal_code_registry.schema.json`, owner: Evan). Per-entry: `{signal_code, display_name, parquet_column_pattern, description, source_method}`. `signal_code` is stable across reruns; existing entries never renumber. Starter entries include `hmm_stress`, `hmm_3state`, `markov_regime`. `winner_summary.json.signal_code` MUST be from the registry; producer validates before save. Adding a new signal requires PR + regression_note + sop-changelog entry. Cross-ref META-CF, ECON-H5. Added 2026-04-19 (Wave 5B-2). | §ECON-DS3 |

---

## VIZ — Visualization Agent Rules (Viz Vera)

Source: [`docs/agent-sops/visualization-agent-sop.md`](agent-sops/visualization-agent-sop.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| VIZ-A1 | No Inverted Axes on Financial Dashboards — equity/return axes run up=good; spreads run up=wider (stress). | Rule A1 |
| VIZ-A2 | Unit Discipline — axis labels must match data values units (bps vs %; decimal vs percent). | Rule A2 |
| VIZ-A3 | Standard Chart Catalog with Canonical Signal Selection — filename, signal, ordering, styling canonical and stable across reruns. | Rule A3 |
| VIZ-A4 | Chart Regression Report — on every rerun, Vera writes a regression_note.md with Spec Diff section. | Rule A4 |
| VIZ-A5 | Caption Ownership — Ray owns display caption, Vera owns audit sidecar caption. | Rule A5 |
| VIZ-DI1 | Data Ingestion Validation — Vera runs known-fact sanity check on upstream data before charting. | Data Ingestion Validation |
| VIZ-P1 | Plotly Export Standard — portal-destined charts saved as Plotly JSON at output/charts/{pair_id}/plotly/{chart_type}.json. | Plotly Export Standard |
| VIZ-UR1 | Universal Requirements (All Chart Types) — axis labels, title, legend, colorblind-friendly palette. | Universal Requirements |
| VIZ-CT1 | Per Chart Type Inputs — required inputs for each chart type (coefficient, time-series, scatter, etc.). | Per Chart Type |
| VIZ-H1 | Econ-to-Viz Pathway — primary handoff protocol from Evan with chart requests. | Handoff Pathways |
| VIZ-H2 | Data-to-Viz Pathway — direct pathway for exploratory charts. | Handoff Pathways |
| VIZ-H3 | Research-to-Viz Annotation Pathway — Ray provides event timelines and domain conventions. | Handoff Pathways |
| VIZ-H4 | Viz-to-AppDev Handoff — Plotly JSON + static fallback + sidecar metadata for Ace. | App Dev Handoff |
| VIZ-SD1 | Chart Metadata Sidecar Schema — every chart ships with sidecar JSON documenting data source, signal, period, caption. | Sidecar Schema |
| VIZ-CP1 | Color Palette Mandatory — use mandated palette (colorblind-friendly, consistent across pairs). | Color Palette |
| VIZ-NM1 | Chart Naming Convention — canonical filenames per Rule A3; pair_id appears only in directory path. | Chart Naming |
| VIZ-SR1 | Streamlit Rendering Rules — no nested HTML, no markdown inside HTML wrappers. | Streamlit Rendering |
| VIZ-PP1 | Plotly Performance Guidelines — charts stay within performance budget (file size, traces, hover). | Plotly Performance |
| VIZ-CS1 | Standard Chart Set Per Pair — every pair delivers the canonical 10-chart standard set. | Standard Chart Set |
| VIZ-CR1 | Chart Registry — multi-pair chart registry maintained for audit. | Chart Registry |
| VIZ-CD1 | Comparison Dashboard Charts — cross-pair dashboards use direction indicators (solid vs dashed). | Comparison Dashboards |
| VIZ-Q1 | Quality Gates — Vera checklist passed before handoff. | Quality Gates |
| VIZ-V1 | Annotated Historical-Episode Zoom-In — narrative references to Dot-Com/GFC/COVID/etc. require matching ±2-year zoom chart with 3–5 dashed event markers and explicit episode title; filename `history_zoom_{episode_slug}.json`. Canonical+override protocol per META-ZI. Addresses SL-4, SL-5; enables S18-12. | Rule V1 |
| VIZ-V2 | NBER Shading Caption — long-horizon (>5yr) time-series carries NBER recession shading AND explicit disclosure text "Vertical shaded bands mark NBER recessions." rev 2026-04-19: alpha prescription bumped to 0.20–0.28 with `rgba(150,120,120,0.22)` default (plain grey at alpha <0.18 prohibited); mandatory subplot handling (one shape per xaxis/xaxis2/… per recession); mandatory perceptual-validation PNG saved at `_perceptual_check_{chart}.png`. Addresses SL-2 + April 2026 follow-up. | Rule V2 |
| VIZ-V3 | No Silent Chart Fallback — every method gets its own canonical artifact; Granger standard = F-statistic by lag with significance line; if blocked, explicit "chart pending" placeholder, never a silent substitute. Addresses S18-11. | Rule V3 |
| VIZ-V4 | No Silent Drop of Diagnostic Charts — mandatory diagnostics per method (CCF→pre-whitened + Q1–Q4 return bars; Regime→prob + regime-quartile returns; Quantile→coefficient chart; Granger→F-by-lag; TE→TE-by-lag); removal requires regression_note entry. Addresses S18-8. | Rule V4 |
| VIZ-V5 | End-to-End Chart Load Smoke Test — before handoff to Ace, Vera runs a smoke test per chart (JSON loads cleanly, `len(fig.data) > 0`, `fig.layout.title.text` non-empty); pass/fail logged to `output/charts/{pair_id}/plotly/_smoke_test_{YYYYMMDD}.log`; any fail is a blocker. Added 2026-04-19 in response to HY-IG v2 stakeholder review. | Rule V5 |
| VIZ-V8 | Chart Type Registry (canonical, machine-readable) — method-to-chart mapping is authoritative at `docs/schemas/chart_type_registry.json` (schema: `docs/schemas/chart_type_registry.schema.json`, owner: Vera, per META-CF). Supersedes the inline Rule A3 table and the three partial copies that previously lived across Evan's ECON-H4 handoff, Vera's VIZ-A3 table, and Ace's `render_method_block` helper — root cause of S18-11 (Wave 1.5 Granger → Local Projections silent fallback) and S18-8 class of silent drops. Evan's ECON-H4 is the INPUT; VIZ-V8 is the authoritative OUTPUT. Evan does NOT produce a separate `viz_handoff_manifest.json` — the registry is the mutual contract. Producer (Vera) validates chart basenames against `canonical_filename_pattern` before save; consumer (Ace) resolves `method_name` via the registry and falls back to GATE-25 placeholder when canonical file is missing. Added 2026-04-19 (Wave 4C-2). | Rule V8 |
| VIZ-V11 | Color Palette Registry (canonical, machine-readable) — the palette used across AIG-RLIC+ portal charts is authoritative at `docs/schemas/color_palette_registry.json` (schema: `docs/schemas/color_palette_registry.schema.json`, owner: Vera, per META-CF). Palette entries expose named roles (`primary_data_trace`, `secondary_data_trace`, `nber_shading`, `event_marker_line`, `event_marker_label_bg`, `buy_indicator`, `sell_indicator`, `hold_indicator`, `equity_curve`, `drawdown_fill`, optional `tertiary_data_trace` / `quartile_gradient` / `categorical_extended`). Every chart's `_meta.json` carries `palette_id` referencing a versioned palette (`okabe_ito_2026` bootstrap). Producer-side pre-save lint blocks saves when raw matplotlib / plotly defaults (`#d62728`, `#1f77b4`, `#2ca02c`, etc.) appear in trace / shape / annotation color fields outside the declared palette. Palette changes between versions are methodological divergence per META-XVC. Closes Wave 5 audit findings on hero (Okabe-Ito) vs zoom (matplotlib default) palette inconsistency within HY-IG v2. Added 2026-04-19 (Wave 5B-2). | Rule V11 |
| VIZ-V12 | Historical-Episode Events Registry (canonical, machine-readable) — the event markers for `history_zoom_{episode_slug}` charts (VIZ-V1) are authoritative at `docs/schemas/history_zoom_events_registry.json` (schema: `docs/schemas/history_zoom_events_registry.schema.json`, owner: Vera — Ray may propose entries via PR, per META-CF). Each episode carries `{episode_slug, episode_name, start_date, end_date, key_events: [{date, label, rationale, source_citation, event_category?}]}`; `rationale` and `source_citation` are mandatory (NBER for recession starts, paper / FOMC / news citation for market events — no bare agent discretion). Vera reads this registry for event markers when rendering zoom charts — ad-hoc picks are prohibited. New episodes require registry PR first. Amending an existing episode is methodological divergence per META-XVC on every pair that previously rendered it. Bootstrapped with 5 episodes (dotcom, gfc, covid, taper_2018, inflation_2022). Cross-ref RES-20 (Ray's episode-selection criterion, pending Wave 5B-2 Ray dispatch). Added 2026-04-19 (Wave 5B-2). | Rule V12 |
| VIZ-V13 | Annotation Positioning Strategies (named, logged) — annotation-positioning on zoom charts and any chart with ≥2 annotations MUST declare one of three named strategies in `_meta.json.annotation_strategy_id`: `descending_stair` (y shifts down by plot_height × 0.10 per annotation in event order), `top_right_uniform` (all anchored top-right, offset by plot_height × 0.06 per annotation), or `alternating_top_bottom` (odd markers above data, even below — reduces overlap for dense zoom charts). Hand-tuned layouts require `annotation_strategy_id: "manual_override"` + regression_note entry listing each moved annotation with y-offset and one-sentence justification + sidecar `annotation_overrides` array; on reference pairs, `manual_override` is a Lead-signoff acceptance item. Strategy changes across versions are methodological divergence per META-XVC. Closes Wave 5 audit finding that Dot-Com annotations at y=(867, 807, 748, 867) were hand-picked with no recorded algorithm. Added 2026-04-19 (Wave 5B-2). | Rule V13 |

---

## RES — Research Agent Rules (Research Ray)

Source: [`docs/agent-sops/research-agent-sop.md`](agent-sops/research-agent-sop.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| RES-B1 | Two-Stage Delivery Protocol — 5-bullet spec memo immediately, then full research brief. | §6 |
| RES-B2 | Direction Determination Workflow — Ray sets expected_direction in Analysis Brief after literature + mechanism review. | §6b |
| RES-B3 | Cross-Pair Direction Consistency Check — direction consistency across pairs sharing an indicator. | §6c |
| RES-B4 | Direction Contradiction Deliverable — when empirical direction contradicts theory, Ray delivers structured contradiction note. | §6d |
| RES-B5 | Strategy Objective Classification — Ray sets strategy_objective (min_mdd/max_sharpe/max_return) after tournament. | §6e |
| RES-IT1 | Indicator Type Classification — Ray classifies indicator type in research brief (shared vocab with Dana). | §4b |
| RES-1 | Audience Assumption — write for a layperson who knows markets but is not a quant. | Rule 1 |
| RES-2 | Translation Bridge — every quant term gets a plain-English translation on first use. | Rule 2 |
| RES-3 | Method Justification — every method has a Why we chose this method sentence in narrative. | Rule 3 |
| RES-4 | Unit Discipline — Inline Dual Notation — first use of any unit-laden value shows dual notation (bps / %). | Rule 4 |
| RES-5 | Regression Prevention on Reruns — Ray compares new narrative to prior version; missing methods trigger escalation. | Rule 5 |
| RES-5b | Regression Prevention Recipe — filesystem-diff recipe for comparing method coverage across reruns. | Rule 5 |
| RES-6 | Glossary Quality Rubric — 4-element standard for every glossary entry. | Rule 6 |
| RES-7 | Signal Generation in Plain English — Strategy page includes a no-formula subsection explaining world event → signal detection → action. Addresses S18-1. | Rule 7 |
| RES-8 | Historical-Episode Cross-Reference — prose references to Dot-Com/GFC/COVID/etc. must cite the matching VIZ-V1 zoom-in chart in the same paragraph; missing chart blocks prose shipment. Addresses SL-4, SL-5. | Rule 8 |
| RES-9 | Investor-Impact Bullet Discipline — every Story-page historical-observation bullet carries a concrete "what this means for investors" action clause. Addresses S18-12. | Rule 9 |
| RES-10 | Status Vocabulary Glossary — every status label (Available/Pending/Validated/Draft/Mature/Exploratory) used in narrative has a one-sentence glossary entry in docs/portal_glossary.json. Addresses S18-4 follow-up. | Rule 10 |
| RES-11 | Story Page Headline Structure — every Story page leads with `## [Metric summary] — [One-liner]` headline (2-3 KPI metrics) before hook paragraph, narrative arc, and bullets; acceptance.md confirms headline-first structure. Addresses SL-1. | Rule RES-11 |
| RES-VS | Narrative Status Vocabulary Self-Check — pre-handoff, Ray verifies every status label in narrative prose matches the canonical set (Available/Pending/Validated/Stale/Draft/Mature/Unknown) or adds the novel term to docs/portal_glossary.json in the same handoff. Companion to DATA-VS. Addresses S18-4 follow-up, S18-3. | Rule RES-VS |
| RES-17 | Narrative Frontmatter Contract — every `docs/portal_narrative_{pair_id}_{date}.md` opens with a frontmatter block conforming to `docs/schemas/narrative_frontmatter.schema.json` (META-CF, owner: Ray). Inventories pages/sections/expanders by stable anchor, `chart_refs`, `glossary_terms`, `direction_asserted` (matches APP-DIR1). Producer validation via `scripts/validate_schema.py` blocks handoff on failure. Glossary request-back SLA: Ace-filed requests close in the next revision within one week OR ship with `[term pending definition]` placeholder. Cross-ref APP-NR1 (Ace consumer), APP-DIR1. Closes RES-16 / B8. | Rule RES-17 |
| RES-18 | Headline Template Constraint — Story page headline (RES-11) must instantiate one of two sanctioned templates: **A (metric-first)** `## [Metric] over [OOS span] — [indicator] as [role] for [target outcome]` or **B (insight-first)** `## [One-line insight]. [Metric] over [OOS span].`. Exact wording within a template is author's choice. OOS span is read from `results/{pair_id}/oos_split_record.json` (no hand-typed numbers); metric value read from `winner_summary.json`. Template ID (`"A"` or `"B"`) recorded in narrative frontmatter (`headline_template`). Other forms require design_note. Cross-ref RES-11, RES-17, ECON-H5, META-XVC. Closes Wave-5 audit headline-reproducibility gap and the 8-year/15-year OOS drift bug. Added 2026-04-19 (Wave 5B-2). | Rule RES-18 |
| RES-20 | Historical-Episode Selection Criterion — every narrative (per RES-8) references at least 3 historical episodes following the triad: **long-lead** (indicator led equity by 6+ months, e.g. GFC for credit), **coincident** (indicator moved with equity, e.g. COVID), **failure-case** (indicator did NOT signal a drawdown it should have caught, e.g. 2022 for credit). Optional 4th confirmer allowed. Per-episode `selection_rationale` (enum: `long_lead` / `coincident` / `failure_case` / `confirmer`) recorded in frontmatter `historical_episodes_referenced[i]`. Each `episode_slug` must exist in VIZ-V12 chart-type registry; unregistered episodes require a PR to the registry before prose references them. Cross-version consistency via META-XVC. Cross-ref RES-8, META-ZI, VIZ-V1, VIZ-V12, META-XVC, RES-17. Closes Wave-5 audit episode-selection discretion gap and codifies the failure-case honesty norm. Added 2026-04-19 (Wave 5B-2). | Rule RES-20 |
| RES-22 | Status-Label Assignment Decision Table — mapping from artifact empirical condition → canonical status label (Available/Pending/Validated/Stale/Draft/Mature/Unknown) is deterministic, not discretionary. First-match-wins lookup: (schema-validated + <60 days → **Validated**), (schema-validated + >60 days → **Stale**), (on-disk + no schema → **Available**), (scheduled, not produced → **Pending**), (explicit WIP → **Draft**), (3+ cycles stable → **Mature**), (indeterminate → **Unknown**, BLOCKING per META-UNK). Informal aliases (e.g. `"ready"`) banned; Wave 5C migrates existing occurrences. Every user-visible status label paired with its plain-English definition from `portal_glossary.json._status_vocabulary` per META-ELI5. Cross-ref RES-10, RES-VS, DATA-VS, META-UNK, META-ELI5, META-CF. Closes Wave-5 audit `chart_status: "ready"` vocabulary violation. Added 2026-04-19 (Wave 5B-2). | Rule RES-22 |
| RES-EP1 | Evidence Page 8-Element Template — every method block has 8 required elements (Why, How, Method, Graph, Observation, Interpretation, Caveats, Link-back). | Evidence Page Structure |
| RES-EP2 | chart_status field mandatory — every method block declares chart availability status. | chart_status field |
| RES-EP3 | Missing-Element Fallback Protocol — structured fallback (escalate before dropping). | Missing-Element Fallback |
| RES-EP4 | Drop Only With Regression Note — a method may be dropped only after (a) gap cannot be resolved and (b) regression note is written. | Missing-Element Fallback |
| RES-PA1 | Storytelling Arc — Hook / Story / Evidence / Strategy / Method arc across pages. | Storytelling Arc |
| RES-PA2 | Presentation Quality Patterns — skeptical reader framing, progressive disclosure, honest caveats. | Presentation Quality Patterns |
| RES-PA3 | How to Read the Trade Log — Strategy page includes this narrative subsection with concrete example. | How to Read the Trade Log |
| RES-MS1 | Multi-Indicator Scaling — tiered literature review, batch spec memos, canonical glossary, master event database. | Multi-Indicator Scaling |
| RES-MS2 | Batch Direction Annotation Delivery — direction annotations batched across pairs sharing an indicator. | Batch Direction Annotation |
| RES-DS1 | Data Source Feedback Loop — Ray routes data-source failures back into next cycle brief. | Data Source Feedback Loop |
| RES-Q1 | Quality Gates — Ray checklist passed before handoff. | Quality Gates |

---

## APP — AppDev Agent Rules (AppDev Ace)

Source: [`docs/agent-sops/appdev-agent-sop.md`](agent-sops/appdev-agent-sop.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| APP-PA1 | Portal Architecture — 4 canonical page types per pair (Story, Evidence, Strategy, Methodology). | §2 |
| APP-SF1 | Storytelling Flow — narrative arc implemented top-to-bottom on each page. | §3 |
| APP-DA1 | Direction Annotation Components — How to Read This callout; Differs From notes on multi-pair dashboards. | §3.5 |
| APP-SP1 | Strategy Execution Panel — standard component with KPI cards, trade log, leaderboard, execution notes. | §3.6 |
| APP-RP1 | Rendering Patterns for Presentation Quality — use st.container(border=True); no nested HTML; no markdown inside HTML. | §3.7 |
| APP-AF1 | Expander Philosophy: Defer, Do not Expand — progressive disclosure via expanders for depth content. | §3.8 #1 |
| APP-AF2 | Rule-First Strategy Cards — Trading Rule in Plain English appears FIRST on Strategy page. | §3.8 #2 |
| APP-AF3 | Metric Interpretation Rule — every KPI card has interpretation caption (benchmark + one-sentence meaning). | §3.8 #3 |
| APP-AF4 | Translation Bridge Rendering — plain-English translations rendered inline with quant term on first use. | §3.8 #4 |
| APP-AF5 | Column Legend Requirement for Downloadable Artifacts — every CSV download has adjacent column-legend expander. | §3.8 #5 |
| APP-EP1 | Evidence Page 8-Element Template — rendering rules for 8-element template (see RES-EP1 for authoring). | §3.9 |
| APP-EP2 | Caption Fallback Chain — when Ray caption missing, fall back to Vera sidecar; log warning. | §3.9 Caption fallback |
| APP-EP3 | Render-time Completeness Check — rendered block verifies all mandatory elements present. | §3.9 Completeness check |
| APP-EP4 | Chart Filename Contract (Rule 3.9a) — loader uses canonical filename only; no fallback. | §3.9 Chart filename contract |
| APP-EP5 | Missing Element 4 Fallback (Rule 3.9b) — when chart missing, render explicit visible error. | §3.9 Missing Element 4 fallback |
| APP-CI1 | Charts and Interactivity — charts loaded via canonical path; chart_key set to avoid duplicate-element errors. | §4 |
| APP-DL1 | Data Layer — cached dataset integration; refresh pipeline documented. | §5 |
| APP-DP1 | Deploy to Streamlit Community Cloud — try/except fallback for st.page_link to avoid StreamlitPageNotFoundError. | §6 |
| APP-LP1 | Landing Page Executive Summary Block — top-of-page summary with portal scope and headline finding. | Landing Page 1 |
| APP-LP2 | Multi-dimensional Filters — filter by nature, type, objective, direction. | Landing Page 2 |
| APP-LP3 | Card Numbering — consistent numbering across filter states. | Landing Page 3 |
| APP-LP4 | Performance Badges — Sharpe and Max DD badges use correct color thresholds. | Landing Page 4 |
| APP-LP5 | Classification Chips — nature/type/objective/direction chips on each card. | Landing Page 5 |
| APP-LP6 | Metadata Source — cards read from interpretation_metadata.json + winner_summary.json + tournament_winner.json. | Landing Page 6 |
| APP-LP7 | Filter Behavior for Unknown — unknown values surfaced as integrity warnings, not silent. | Landing Page 7 |
| APP-IQ1 | Input Quality Log — Ace logs input quality issues per portal page. | Input Quality Log |
| APP-D2 | Defense 2 — Numerical Reconciliation — Ace runs reconciliation script against chart numbers before shipping. | Defense 2 |
| APP-Q1 | Quality Gates — Ace checklist passed before shipping. | Quality Gates |
| APP-SE1 | Probability Engine Panel — mandatory Strategy page component: time-series of primary signal with decision-threshold lines, NBER shading if span > 5yr, 1-line takeaway caption. Addresses S18-1. Extended 2026-04-19 with pre-render validation (Gap 2) and META-ZI loader cross-ref (Gap 5). | §3.6 Rule A1 |
| APP-SE2 | Position Adjustment Panel — mandatory Strategy page component: time-series of resulting equity exposure 0–100% derived from signal × strategy family rules, 1-line takeaway caption. Addresses S18-1. Extended 2026-04-19 with pre-render validation fallback and Defense-2 checks (Gap 2, Gap 4). | §3.6 Rule A2 |
| APP-SE3 | Instructional Trigger Cards — mandatory Strategy page component: 2-4 card grid (st.columns + st.container(border=True)) showing BUY/REDUCE/HOLD scenarios with mini-chart + "when probability crosses X → do Y" text. Addresses S18-9. | §3.6 Rule A3 |
| APP-SE4 | Real-time Execution Placeholder — mandatory "Future: Live Execution" section on every Strategy page with st.metric() placeholders for Current Signal State / Target Position / Current Action; reads from results/{id}/live_execution_stub.json if present, else "—". Addresses S18-10. | §3.10 Rule A4 |
| APP-SE5 | Universal Takeaway Caption — every table, chart, diagnostic in Confidence section of Strategy page MUST carry a 1-line st.caption() user-facing takeaway; also required on Evidence Sources status table and any status legend (Available/Pending/Validated definitions). Addresses S18-3, S18-4. | §3.11 Rule A5 |
| APP-ST1 | Loader End-to-End Smoke Test — before Ace finishes a pair's portal pages, run `python3 app/_smoke_tests/smoke_loader.py {pair_id}` which AST-parses each page (plus a literal list for dynamic chart_names in the Evidence `render_method_block` helper), invokes `load_plotly_chart` under a Streamlit mock, and asserts (a) non-None `Figure` returned, (b) `len(fig.data) > 0`, (c) `fig.layout.title.text` non-empty. Per-call PASS / FAIL / SKIP logged to `app/_smoke_tests/loader_{pair_id}_{yyyymmdd}.log`. Any FAIL is a blocker — Ace cannot mark the page done. Added 2026-04-19 after Wave-2 stakeholder review exposed Bug #2 (Dot-Com zoom rendered as GATE-25 placeholder while the canonical JSON was present and parseable). Core learning: artifact-existence checks are not rendering checks; load end-to-end or you can't know. | Defense 2 (Loader E2E) |
| APP-WS1 | `winner_summary.json` Consumer Contract — Ace's Strategy-page components load `results/{pair_id}/winner_summary.json` via `app.components.schema_check.validate_or_die(path, "winner_summary")`, which validates against `docs/schemas/winner_summary.schema.json` (v1.0.0). Required fields (`signal_column`, `signal_code`, `target_symbol`, `threshold_value`, `threshold_rule`, `strategy_family`, `direction`, OOS metrics) are guaranteed by the schema; no fallback inference permitted. Validation failure → `st.error(...)` + `SchemaValidationError` (APP-SEV1 L1). Retires the Wave-1.5 `_SIGNAL_CODE_TO_COLUMN` literal-name fallback map in `probability_engine_panel.py`. Added 2026-04-19 (Wave 4D-2). Cross-ref ECON-H5, META-CF, APP-SEV1, APP-DIR1. | §Rule APP-WS1 |
| APP-SEV1 | Validation Severity Policy — every consumer-side validation branch maps to one of three user-visible levels: L1 (Loud-Error / `st.error`) when the page's primary purpose cannot be served (e.g. APP-WS1 schema violation); L2 (Loud-Warning / `st.warning`) when the gap is meaningful but the render can degrade gracefully (e.g. optional artifact schema violation); L3 (Caption-Note / `st.caption`) for minor gaps. Silent skip is prohibited. Helper contract lives at `app/components/schema_check.py` (`validate_or_die` for L1, `validate_soft` for caller-owned severity). Added 2026-04-19 (Wave 4D-2). Cross-ref META-UNK, APP-WS1, APP-DIR1, GATE-25, GATE-28. | §Rule APP-SEV1 |
| APP-DIR1 | 3-Way Direction Triangulation — at every reference-pair page load, `app/components/direction_check.py::check_direction_agreement(pair_id)` reads `winner_summary.json.direction` (Evan / ECON-H5), `interpretation_metadata.json.observed_direction` (Dana / DATA-D6), and — once RES-17 narrative-frontmatter migration lands — `narrative_frontmatter.direction_asserted` (Ray). Canonical enum: `procyclical` / `countercyclical` / `mixed`. Mismatch between any two available legs → `st.error("Direction disagreement: Evan says X, Dana says Y")` per APP-SEV1 L1. Currently 2-way (Evan ↔ Dana); upgrades to 3-way post-RES-17. Reference-pair acceptance blocker. Added 2026-04-19 (Wave 4D-2). Cross-ref META-IA, META-CFO, ECON-H5, DATA-D6, RES-17. | §Rule APP-DIR1 |
| APP-CC1 | Caption Prefix Canonical Vocabulary — every `st.caption` / bolded caption-style markdown on every portal page leads with one of four canonical prefixes pinned at `docs/schemas/caption_prefix_vocab.json` (META-CF, owner Ace, Ray reviews tone): `"What this shows:"` (data description), `"Why this matters:"` (investor-impact takeaway), `"How to read it:"` (reading guide), `"Caveat:"` (honest caution). Prefix is fixed; body is author's discretion. Novel prefixes require a regression_note entry and a minor bump per META-SCV. Added 2026-04-19 (Wave 5B-2). Cross-ref APP-SE5, APP-AF3, APP-EX1, RES-2, RES-EP1, META-CF, META-ELI5. | §Rule APP-CC1 |
| APP-EX1 | Expander Title Canonical Registry — five canonical titles pinned at `docs/schemas/expander_title_registry.json` (META-CF, owner Ace): `"Plain English"` (not "ELI5" / "In plain English" / "What this means"), `"Deeper dive"`, `"Why we chose this method"`, `"How to read this chart"`, `"Honest assessment"`. Deprecated aliases registered for grep-based migration audit. All default to `expanded=False` per APP-AF1. Deviations require a regression_note justification. Added 2026-04-19 (Wave 5B-2). Cross-ref APP-AF1, APP-AF4, APP-CC1, RES-EP1, RES-2, META-CF, META-ELI5. | §Rule APP-EX1 |
| APP-URL1 | Page URL-Slug Pin — expected Streamlit slug per `app/pages/*.py` pinned at `docs/schemas/url_slug_pins.json` (META-CF, owner Ace) with observed `streamlit_version_observed`. Smoke test at acceptance asserts actual Cloud slug matches pin; breadcrumb component reads `canonical_breadcrumb` from the pin rather than inferring from filename. Mismatch blocks reference-pair acceptance. GATE-29 clean-checkout test extended to cover slug verification. Added 2026-04-19 (Wave 5B-2). Cross-ref APP-DP1, GATE-29, GATE-30, META-CF, META-VNC. | §Rule APP-URL1 |
| APP-CH1 | Chart Name Registry Extension for Non-Method Charts — non-method charts (`hero`, `equity_curves`, `equity_drawdown`, `tournament_scatter`, `history_zoom_*`, `trade_log_preview`, `signal_timeseries`, `position_timeseries`, `regime_shading_backdrop`) registered in VIZ-V8's `docs/schemas/chart_type_registry.json` as an extension — NOT a new registry. Vera owns schema and method-chart rows; Ace PRs non-method rows via shared edits. Ace's `load_plotly_chart` loader consults the registry for ALL chart names, method and non-method. Enforces GATE-25 / APP-EP4 across the full chart catalog. Added 2026-04-19 (Wave 5B-2). Cross-ref VIZ-V8, VIZ-NM1, GATE-25, GATE-27, APP-EP4, META-CF, META-ZI. | §Rule APP-CH1 |

---

## QA — QA Agent Rules (QA Quincy)

Source: [`docs/agent-sops/qa-agent-sop.md`](agent-sops/qa-agent-sop.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| QA-SOP | QA Agent SOP — Quincy's core mandate (5 pillars): artifact verification, end-to-end Cloud smoke, stakeholder-eye review, cross-agent seam audit, block authority. Runs AFTER all producers and BEFORE Lead acceptance sign-off. Cannot modify producer artifacts — files findings only. Second line of defense behind META-SRV. Makes GATE-31 enforceable. Added 2026-04-19 (Wave 6A). Cross-ref META-SRV, META-AL, GATE-31, META-RPD, META-FRD. | Whole SOP |
| QA-CL1 | Standard QA Checklist per Wave — 12-item mandatory list: every claim has verification command + result, all schemas validate, both smoke tests pass, Cloud pages render, zero `chart_pending` on reference pair, direction triangulation passes, stakeholder-spirit checks, META-XVC drift = 0, META-ELI5 compliance, GATE-30 deflection audit, every discrepancy evidenced. | Standard QA Checklist per Wave |
| QA-FF1 | Findings Format — results logged as `PASS / PASS-with-note / FAIL` with claim, category, evidence, and action columns; per-wave summary of totals; block authority on FAIL. Lead can override per META-FRD-style log. | Findings Format |
| QA-EP1 | Escalation Path — All PASS → QA sign-off in acceptance.md; FAIL → producer fix + QA re-verify; Lead override logged to `docs/pair_execution_history.md` "QA Override Log" (mirrors META-FRD). Override >1/quarter triggers retro on QA scope. | Escalation Path |
| QA-H1 | Producer → QA Handoff — producer delivers claims + META-SRV evidence block; silence is not acceptance; missing evidence returned as META-SRV violation before QA runs full verification. | Handoff: Producer → QA |
| QA-H2 | QA → Lead Handoff — QA writes outcome + blocking items + sign-off recommendation + findings link to Lead; Lead signs acceptance or routes blockers back. | Handoff: QA → Lead |

---

## GATE — Completeness Gate Items (Lead Lesandro)

Source: [`docs/agent-sops/team-coordination.md`](agent-sops/team-coordination.md) Deliverables Completeness Gate

Every pair must satisfy every gate item below before being marked completed.

| ID | Short name | Owner |
|----|-----------|-------|
| GATE-1 | Analysis Brief present | Lesandro/Ray |
| GATE-2 | Master dataset present | Dana |
| GATE-3 | Stationarity tests present | Dana |
| GATE-4 | Interpretation metadata present | Dana + Ray |
| GATE-5 | Exploratory results present | Evan |
| GATE-6 | Core model results present (3+ files) | Evan |
| GATE-7 | Tournament results present | Evan |
| GATE-8 | Charts present (5+ JSON files) | Vera |
| GATE-9 | Portal: Story page | Ace |
| GATE-10 | Portal: Evidence page | Ace |
| GATE-11 | Portal: Strategy page | Ace |
| GATE-12 | Portal: Methodology page | Ace |
| GATE-13 | Sidebar navigation entry | Ace |
| GATE-14 | Landing card entry | Ace |
| GATE-15 | Catalog status updated to Completed | Ray |
| GATE-16 | Winner summary JSON complete | Evan |
| GATE-17 | Winner trade log CSV (rows > 0) | Evan |
| GATE-18 | Execution notes markdown | Ray/Evan |
| GATE-19 | indicator_nature populated (canonical vocab) | Dana |
| GATE-20 | indicator_type populated (canonical 7-value vocab) | Dana |
| GATE-21 | strategy_objective populated | Ray |
| GATE-22 | Method coverage — no regression | Evan + Ray + Ace |
| GATE-23 | Pair acceptance.md present with Lead sign-off | Lesandro |
| GATE-24 | Chart-Text Coherence Audit — every chart modification grep-checked against `app/pages/`; caption/narrative updated in same commit; regression_note pairs chart change with narrative change. 2026-04-19: ownership clarified — Vera notifies, Ray proactively diffs. Addresses SL-3. | Vera + Ray (Ace verifies) |
| GATE-25 | No Silent Chart Fallbacks — every method renders its own canonical chart (VIZ-V3); missing artifacts render a labeled "chart pending" placeholder, never a lookalike from a different method. acceptance.md lists method → chart mapping. Addresses S18-11. | Vera + Ace |
| GATE-26 | No Silent Content Drops — any element present in a prior version but absent now is declared in regression_note's **Removed** section with rationale; otherwise restored. acceptance.md includes Prior-Version Inventory diff (retained/added/removed). Addresses S18-8, SL-2, silent-drop meta-pattern. | Evan + Ray + Ace (Lesandro gates) |
| GATE-27 | End-to-End Chart Render Test — every chart referenced by any portal page of the pair must load via `load_plotly_chart(name, pair_id)` as a non-None Figure, carry ≥1 data trace, and have a non-empty title. Vera (VIZ-V5 smoke test) + Ace (loader smoke-test extension of Defense-2) attach logs to acceptance.md. Blocks acceptance on any failure. Addresses the Wave-3 Dot-Com canonical-zoom loader bug (file existed, path resolved, loader returned None — undetectable by file-existence checks alone). | Vera + Ace (Lesandro gates) |
| GATE-28 | Reference-Pair Placeholder Prohibition — on reference-pair pages (per META-RPD), any "chart pending" placeholder (the GATE-25 graceful fallback) is an acceptance blocker. Headless-browser DOM audit must return zero `chart_pending` occurrences across all portal pages of the reference pair. Graceful degradation is for non-reference pairs only; reference pairs must render 100% of referenced charts. Addresses the Wave-3 gate-layer gap that allowed "chart pending" to pass verification on a reference pair. | Ace + Lesandro |
| GATE-29 | Clean-Checkout Deployment Test — before acceptance, the pair's portal must pass `app/_smoke_tests/smoke_loader.py --pair-id {pair_id}` run inside a clean `git clone --depth 1` checkout that respects `.gitignore` (Streamlit Cloud simulation). Any file referenced by `app/` code that exists in the working tree but NOT in the clean checkout = gate failure (silent gitignore exclusion or missing `git add -f`). Log saved to `app/_smoke_tests/clean_checkout_{pair_id}_{date}.log` with zero FileNotFound / zero None-return / zero placeholder asserted. Blocks acceptance for reference pairs. `GATE-27` validates rendering in the dev env; `GATE-29` validates deployability. Producer-side companion: **ECON-DS2** (Deploy-Required Artifact Allowlist). Reusable harness: APP-ST1. Addresses the Wave-4A stakeholder bug "Probability engine panel cannot render: No signals_*.parquet" on Cloud where `.gitignore`'s blanket `*.parquet` rule silently excluded a deploy-required artifact. | Ace + Lesandro |
| GATE-30 | Deflection Link Audit — any stakeholder-feedback item (Sxx-y / SL-n) closed in `acceptance.md` via deflection ("see other page/section" rather than in-place fix) requires: (a) explicit target page + anchor named in the resolution; (b) blocking DOM-assertion that the target anchor renders; (c) blocking content-presence assertion that the target section contains the content claimed to address the stakeholder's concern; (d) **Lead sign-off on every deflection resolution** — agents cannot close a deflection item unilaterally; (e) meta-rule: if the deflection target page is later renamed/restructured, every deflection reference that pointed at it is automatically re-opened for re-audit. Deflection audit table appears in the Pair Acceptance Checklist template. Addresses Wave-5 audit findings S18-2 (regime summary deflected to Story page) and S18-4 (Evidence Sources Table deflected via cross-link) where no mechanical assertion verified the deflection target rendered or contained the referenced content. Added 2026-04-19 (Wave 5B-1). | Ace + Lead Lesandro |
| GATE-31 | Independent QA Verification (Blocking) — every `acceptance.md` sign-off must carry a QA Verification section authored by Quincy (`docs/agent-sops/qa-agent-sop.md`) with ≥1 finding per mandated category: (a) artifact verification (claim-evidence cross-check on every regression-note bullet); (b) smoke tests (`smoke_loader.py` + `smoke_schema_consumers.py` exit-0 logs); (c) stakeholder-spirit check (every S-item re-read as the stakeholder); (d) cross-agent seam audit (GATE-24 / 25 / 26 / 28 / 30 + APP-DIR1 + META-XVC cross-version diff). Any FAIL blocks acceptance until producer fix + QA re-verify; Lead override permitted but logged to `docs/pair_execution_history.md` "QA Override Log" (mirrors META-FRD). Makes QA involvement mandatory, not optional. Closes the Wave-5 reflection gap that producer self-reports were signed off without an independent second line of defense. Added 2026-04-19 (Wave 6A). Cross-ref META-SRV, META-AL, META-RPD, GATE-23..30. | Quincy + Lead Lesandro |

---

## META — Cross-Cutting Meta-Rules

Source: [`docs/agent-sops/team-coordination.md`](agent-sops/team-coordination.md)

| ID | One-line description | SOP section |
|----|----------------------|-------------|
| META-EOI | Explicit Over Implicit — every deviation from canonical chart catalog (VIZ-A3), mandatory method list (ECON-C1), prior pair version, or unit conventions (VIZ-A2 / RES-4) documented in design_note.md or regression_note.md. | Explicit Over Implicit |
| META-UNK | Unknown Is Not a Display State — unknown classification is an error signal, fixed at source, not shipped as a label. | Unknown Is Not a Display State |
| META-PSC | Pipeline Self-Containment Contract — every pair has single self-contained pipeline script producing ALL downstream artifacts. | Pipeline Self-Containment |
| META-BV | Browser Verification Mandatory — headless Playwright inspection after every portal page creation or modification. | Browser Verification |
| META-MRA | MRA Mandatory — Measure / Review / Adjust documented in pair_execution_history.md before pair complete. | MRA |
| META-P0 | Phase 0: Analysis Brief Gate — no agent starts work without approved Analysis Brief and structured acknowledgment. | Phase 0 |
| META-HO | Handoff Protocol — structured template, acknowledge within one cycle, partial is OK if manifested. | Handoff Protocol |
| META-ACK | Acknowledgment Protocol — silence is never acceptance. | Acknowledgment Protocol |
| META-CR | Communication Rules — 7-point standing rules. | Communication Rules |
| META-ER | Escalation Rules — structured triggers and escalation targets. | Escalation Rules |
| META-QS | Quality Standards (Team-Wide) — 7-point cross-cutting quality checklist. | Quality Standards |
| META-D1 | Defense 1 — Self-Describing Artifacts (producer): meaningful column names, units, sign conventions, boundaries, sidecar manifest. | Defense 1 |
| META-D2 | Defense 2 — Reconciliation at Every Boundary (consumer + reviewer): known-fact sanity checks, derived-quantity cross-check, automated reconciliation script. | Defense 2 |
| META-TCH1 | Task Completion Hook 1 — Validation and Verification before marking any task done. | Task Completion Hooks |
| META-TCH2 | Task Completion Hook 2 — Reflection and Memory after every completed task. | Task Completion Hooks |
| META-NO | New Agent Onboarding Protocol — cross-review SOPs, self-update, distill lessons. | New Agent Onboarding |
| META-REG | Run Registry — every completed indicator-target analysis registered in Reference Catalogs Index. | Run Registry |
| META-CFO | Classification Field Ownership — Dana owns indicator_nature/indicator_type; Ray owns strategy_objective. | Classification Field Ownership |
| META-VF | Variant Families — when one priority pair spawns multiple variants, shared pages OK but all 4 page types required. | Variant Families |
| META-IA | Interpretation Annotation Handoffs — four-agent protocol for same-indicator / different-target direction differences. | Interpretation Annotation Handoffs |
| META-TWJ | Tournament Winner JSON Schema — canonical schema for results/<pair_id>/tournament_winner.json. | Tournament Winner JSON Schema |
| META-RNF | Regression Note Format — required sections: Changes From Prior Version / Approved By / Unchanged / Impact Assessment. | Regression Note Format |
| META-PWQ | Portal-Wide Quality Checklist — cross-cutting acceptance checklist applied to every pair. | Portal-Wide Quality Checklist |
| META-RPD | Reference Pair Doctrine — HY-IG v2 is canonical reference; every new pair compares against it; deviations require design_note.md. | Reference Pair Doctrine |
| META-PAC | Pair Acceptance Checklist — results/<pair_id>/acceptance.md with Lead sign-off is blocking (GATE-23). | Pair Acceptance Checklist |
| META-VNC | Version-to-Version Content Continuity — iterations must be additive or explicitly substitutive, never silently subtractive; the **Removed** section in regression_note is the canonical mechanism for declaring intentional removals. **Scope extended 2026-04-19 (Wave 4A): content continuity applies across iterations AND across environments (dev → Cloud). An artifact that works locally but doesn't survive a clean checkout is the same class of bug as an artifact silently dropped across iterations — both are violations of META-VNC.** Companion to META-RNF and META-SC. Operationalized by GATE-24/25/26 (cross-iteration) and GATE-29 + ECON-DS2 (cross-environment). Applies to all 5 agents. Addresses S18-8, SL-2, SL-3, S18-11, silent-content-drop meta-pattern, and the Wave-4A Cloud-deploy `.gitignore`-exclusion bug. | Version-to-Version Content Continuity |
| META-ZI | Historical Episode Chart Strategy — canonical by default, specialize on justified need. Shared canonical chart at `output/_comparison/history_zoom_{episode_slug}.json` (Vera produces per VIZ-V1); pair-specific overrides at `output/charts/{pair_id}/history_zoom_{episode_slug}.json` only when prose ties the episode to the pair's indicator behavior (trigger: Ray coherence check per RES-8). Ace loader tries override → canonical → GATE-25 placeholder. Addresses Gap 5 (design decision); supports VIZ-V1, RES-8, APP-SE1. | Historical Episode Chart Strategy |
| META-PV | Perceptual Validation of Visual Encoding — any chart element that depends on color, alpha, shading, or low-contrast visual encoding for information transfer must have a perceptual-validation step in the producing agent's SOP. Validation requires rendering the chart to PNG (via `plotly.io.write_image`) and visually confirming the encoding is perceivable against realistic backgrounds and data traces; numeric prescriptions (alpha, stroke width, font size) are unvalidated until checked perceptually. Meta-principle: "A rule that was followed but produced the wrong visual is a broken rule. Fix the rule." Applies to NBER shading (VIZ-V2), regime shading, sparkline thickness, annotation dot size, event-marker opacity. Companion to META-VNC and META-RNF; operationalized by GATE-27. Addresses Wave-3 Hero NBER imperceptible-shading bug. | Perceptual Validation of Visual Encoding |
| META-CF | Contract File Standard — single authoritative schema per cross-agent JSON artifact at `docs/schemas/{contract_name}.schema.json` (JSON Schema draft 2020-12). Header `x-owner` and `x-version` (semver) mandatory; companion example instance at `docs/schemas/examples/{contract_name}.example.json`. Producer validates before save, consumer validates before use, both via `scripts/validate_schema.py`. SOPs link to the schema; inline schemas and partial copies are prohibited. Schema changes require a regression_note entry (META-VNC) and a sop-changelog entry. Added 2026-04-19 (Wave 4C-1) after cross-review exposed rampant partial-copy + prose-schema divergence. | Contract File Standard |
| META-XVC | Cross-Version Discipline — when producing v2+ of a pair, each agent observes the prior version and defaults to methodological consistency. Mandatory `### Prior-version observation` subsection in `regression_note_{date}.md` before v2+ authoring. Divergence permitted if documented in a `### Methodological divergence` block (6 fields: Prior method / New method / Strong reason / Expected impact / Validation / Cross-reference). Divergence entries traced in BOTH regression_note AND acceptance.md. Chain preserved across versions (v3 cites v2, v2 cites v1/reference). Extends META-VNC beyond content-drops to method-drifts. Applies to all 5 agents. Added 2026-04-19 (Wave 5B-1). Cross-ref META-VNC, META-RNF, META-RPD, META-RPT. | Cross-Version Discipline |
| META-FRD | Force-Redeploy Discipline — a commit whose sole purpose is to trigger Streamlit Cloud rebuild (after observed stale-Cloud state) must be (a) trivial (docstring/comment only, no functional code change), (b) alone in the commit (never batched), (c) commit-message-tagged with the stale-Cloud observation timestamp and method. Every force-redeploy logged in `docs/pair_execution_history.md` "Force-Redeploy Log" section with `{commit_sha, trigger_reason, time_to_rebuild, observed_stale_element, lead_initials}`. Threshold: >2 invocations/quarter escalates to root-cause investigation (deeper CI/CD or META-VNC cross-environment gap). Codifies the pattern set by precedent commit 1720c0c. Added 2026-04-19 (Wave 5B-1). Cross-ref META-VNC, GATE-29, ECON-DS2. | Force-Redeploy Discipline |
| META-RPT | Reference-Pair Tagging Protocol — codifies the `<pair_id>-reference-candidate` (pre-approval) → `<pair_id>-reference` (post-approval, frozen) tag lifecycle. Approval requires named stakeholder + date in `acceptance.md` Stakeholder Review block; Lead endorses and creates annotated tag `git tag -a <pair_id>-reference <commit> -m "Stakeholder approved: <reviewer> on <date>"` then pushes same operation. Tag is immutable once created. Evolution creates new versioned candidate (`<pair_id>-v3-reference-candidate`); original tag preserved for historical traceability. Makes META-RPD Git-native. Added 2026-04-19 (Wave 5B-1). Cross-ref META-RPD, META-XVC. | Reference-Pair Tagging Protocol |
| META-BL | Backlog Discipline — proposed-but-deferred rules registered in `docs/backlog.md` with columns `{ID, proposer_agent, proposed_rule_id, motivation, decision, deferred_reason, reactivation_trigger, date}`. ID format `BL-NNN` (monotonic 3-digit, immutable). Lead reviews at EOD for fired triggers → promote to SOP or explicitly re-defer with dated note. Only Lead promotes; agents propose. Promoted items follow normal rule-addition workflow (SOP text + changelog + standards.md registration). Bootstrap entry: BL-001 (APP-SEV1-MAP, Ace, deferred to next sprint). Added 2026-04-19 (Wave 5B-1). | Backlog Discipline |
| META-SCV | Schema Consumer Version Contract — extends META-CF to the consumer side. `validate_or_die(path, schema_name, minimum_x_version=...)` and `validate_soft(...)` gain a `minimum_x_version` parameter. Rule: consumer's `minimum_x_version` major must equal producer's `x-version` major; consumer's minor must be ≤ producer's minor. Major mismatch → `SchemaVersionMismatch`. Additive (minor) bumps pass. Call sites must pass an explicit `minimum_x_version` — defaulting to "1.0.0" silently defeats the rule. Closes the Wave-5 audit gap where an Evan bump to winner_summary 1.1.0 (additive) would silently pass a consumer written against 1.0.0, setting up a downstream `KeyError` when another consumer relied on a 1.1.0-only field against a 1.0.0 instance. Added 2026-04-19 (Wave 5B-1). Cross-ref META-CF, APP-SEV1, APP-WS1. | Schema Consumer Version Contract |
| META-ELI5 | User-Facing Technical Flags → Plain English Explanation — every user-visible `st.error` / `st.warning` / `st.info` callout (all APP-SEV1 levels), every status label (Available/Pending/Validated/Insufficient/Stale/Draft/Mature/Unknown), every validation failure message from `schema_check`, and every "chart pending / unavailable" placeholder must carry BOTH (a) a technical label (agent-facing short string, canonical vocabulary) AND (b) an ELI5 body (1–2 sentences, no formulas, no jargon, layperson-friendly). Ownership: producing agent authors both parts; Ray is editorial owner of user-facing prose and reviews tone at handoff. Retroactive audit scheduled for Wave 5C (every `st.error` / `st.warning` / `st.info` in HY-IG v2 portal code gets an ELI5 sibling). Extends RES-1/RES-3 writing voice and APP-SE5 takeaway captions to in-line flags — a layer none of those catch. Added 2026-04-19 (Wave 5B-1). Cross-ref RES-1, RES-3, APP-SE5, APP-SEV1. | User-Facing Technical Flags → Plain English |
| META-AL | Abstraction Layer Discipline — before abstracting anything as "canonical," ask: does the output vary across consumers? If yes, the canonical layer is the *inputs/rules*, not the output. Canonical (shareable): metadata, rules, registries, parameters, templates, schemas. Pair-specific (per-pair): rendered outputs, derived artifacts, anything computed from pair-specific inputs. Test question: "Does the artifact contain any pair-specific data?" If yes → it cannot be canonical. Worked example: canonical rendered zoom chart at `output/_comparison/history_zoom_{episode}.json` was wrong (contains one pair's data, cannot serve another); right answer is canonical events registry at `docs/schemas/history_zoom_events_registry.json` (metadata only) + each pair renders its own dual-panel chart. Invalidates the META-ZI canonical-rendered-chart fallback — scheduled for Wave 6B refinement (loader drops `_comparison/` fallback; canonical layer shrinks to events registry). Applies to any future shared-artifact proposals. Added 2026-04-19 (Wave 6A). Cross-ref META-ZI (to be refined), VIZ-V12. | Abstraction Layer Discipline (META-AL) |
| META-SRV | Self-Report Verification Discipline — every agent self-report must name (a) the file path(s) touched and (b) a machine-checkable verification method. Self-reports without verification evidence are not acceptable for Lead to sign off. Format for regression-note entries: `Claims:` (one-sentence claim) + `Evidence:` (File / Verification command / Result). Verification methods catalog: schema conformance (`scripts/validate_schema.py --schema X --instance Y → exit 0`), grep absence (`grep -r ... | wc -l → 0`), smoke test (`smoke_loader.py <pair_id> → failures=0`), file existence (`ls <path> → exists`), diff count (`git diff HEAD~1 --stat <file> → non-empty`), Cloud assertion (Playwright query + expected DOM text/attribute). First line of defense: producer self-verifies. Second line: Quincy re-verifies independently per `docs/agent-sops/qa-agent-sop.md`. Both layers apply; QA catches self-reports that didn't catch their own blind spots. Added 2026-04-19 (Wave 6A). Cross-ref QA-SOP, GATE-31, META-RNF, META-CF, META-XVC. | Self-Report Verification Discipline (META-SRV) |

---

## Newly Assigned IDs (for this document)

The following rules existed in the source SOPs but lacked explicit short IDs in their source text. IDs assigned here for registry purposes (Lesandro to review and promote into SOPs on the next revision):

- **DATA-DD1..DD4** — data dictionary/handoff/classification deliverables not previously ID-tagged.
- **DATA-H1..H3, DATA-E1, DATA-N1, DATA-B1..B2, DATA-Q1, DATA-R1** — Dana handoff, expedited, non-MCP, batch, and quality rules.
- **ECON-DS1** — Derived Signal Persistence Rule (existed by name, now tagged).
- **ECON-SS1, ECON-EX1, ECON-ES1, ECON-DG1, ECON-SA1, ECON-H1..H3, ECON-T1..T2, ECON-M1, ECON-Q1, ECON-D2** — Evan workflow and handoff rules.
- **VIZ-DI1, VIZ-P1, VIZ-UR1, VIZ-CT1, VIZ-H1..H4, VIZ-SD1, VIZ-CP1, VIZ-NM1, VIZ-SR1, VIZ-PP1, VIZ-CS1, VIZ-CR1, VIZ-CD1, VIZ-Q1** — Vera ingestion, export, chart-type, handoff, metadata, preferences.
- **RES-B1..B5, RES-IT1, RES-5b, RES-EP1..EP4, RES-PA1..PA3, RES-MS1..MS2, RES-DS1, RES-Q1** — Ray protocol, evidence-page, and multi-indicator rules (Rule 1-6 retained as-is).
- **APP-PA1, APP-SF1, APP-DA1, APP-SP1, APP-RP1, APP-AF1..AF5, APP-EP1..EP5, APP-CI1, APP-DL1, APP-DP1, APP-LP1..LP7, APP-IQ1, APP-D2, APP-Q1** — Ace architecture, storytelling, rendering, audience-friendly, evidence, landing page, and quality rules.
- **APP-SE1..SE5** — Ace Strategy Execution standard-component rules added in response to 2026-04-18 stakeholder feedback batch (S18-1, S18-3, S18-4, S18-9, S18-10).
- **GATE-1..GATE-23** — gate items registered with short IDs for citation.
- **META-\*** — meta-rules registered with short IDs. Previously referenced by section name only.
- **QA-SOP, QA-CL1, QA-FF1, QA-EP1, QA-H1, QA-H2** — QA agent rules (new prefix) added 2026-04-19 (Wave 6A) to register Quincy's QA SOP. QA is the new 6th agent role; SOP at `docs/agent-sops/qa-agent-sop.md`.
- **META-AL, META-SRV** — cross-cutting meta-rules added 2026-04-19 (Wave 6A). META-AL codifies abstraction-layer discipline (the canonical-vs-pair-specific test); META-SRV codifies self-report verification (the producer-side first line of defense that QA/GATE-31 enforces as second line).
- **GATE-31** — Independent QA Verification, added 2026-04-19 (Wave 6A) as the blocking gate that makes QA involvement mandatory on every acceptance.md sign-off.

Promoting any of these short IDs into the owning SOP text is Lead Lesandro call at next SOP revision.

---

## Usage

- **Authoring an Analysis Brief:** cite the ECON-C1 / RES-IT1 / DATA-D3 triad to declare the indicator_type and its required method list.
- **Gate reviews:** walk the GATE-1..GATE-23 checklist; then cross-check META-PWQ; then apply META-RPD reference pair comparison.
- **Writing a regression note:** follow META-RNF format; document each rule deviation by ID.
- **Onboarding a new agent:** read META-NO, then read the full rule set for your role prefix.
- **Adding a new rule:** (a) add text to the owning SOP, (b) add a changelog entry in sop-changelog.md, (c) register the ID here.

Lead Lesandro reviews this document monthly and at every major SOP revision.
