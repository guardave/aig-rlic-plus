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
- **GATE-1..GATE-23** — gate items registered with short IDs for citation.
- **META-\*** — meta-rules registered with short IDs. Previously referenced by section name only.

Promoting any of these short IDs into the owning SOP text is Lead Lesandro call at next SOP revision.

---

## Usage

- **Authoring an Analysis Brief:** cite the ECON-C1 / RES-IT1 / DATA-D3 triad to declare the indicator_type and its required method list.
- **Gate reviews:** walk the GATE-1..GATE-23 checklist; then cross-check META-PWQ; then apply META-RPD reference pair comparison.
- **Writing a regression note:** follow META-RNF format; document each rule deviation by ID.
- **Onboarding a new agent:** read META-NO, then read the full rule set for your role prefix.
- **Adding a new rule:** (a) add text to the owning SOP, (b) add a changelog entry in sop-changelog.md, (c) register the ID here.

Lead Lesandro reviews this document monthly and at every major SOP revision.
