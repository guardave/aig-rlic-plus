# AIG-RLIC+ SOP Changelog

Chronological record of every rule addition and modification across the AIG-RLIC+ agent SOP system. New rules are entered here first, then registered in [`docs/standards.md`](standards.md).

Entries are listed newest-first. Each entry cites the commit hash, date, and summarizes what changed.

---

## 2026-04-12 — Regression-Proofing Infrastructure (this session)

**Scope:** team-coordination.md + new docs/standards.md + new docs/sop-changelog.md. No changes to agent-specific SOPs.

**Added to team-coordination.md:**

- **META-PWQ / Portal-Wide Quality Checklist** — cross-cutting acceptance checklist applied to every pair. Covers Landing Page, Navigation, Story, Evidence, Strategy, Methodology pages, and cross-cutting items (dual notation, plain-English expanders, honest caveats, no silent regressions).
- **META-RPD / Reference Pair Doctrine** — HY-IG v2 (tag: hy-ig-v2-reference once approved) established as canonical reference pair. Every new pair dispatch begins with comparison; deviations require design_note.md.
- **META-PAC / Pair Acceptance Checklist** — new template for results/<pair_id>/acceptance.md with Portal-Wide Quality Checklist, Reference Pair Comparison, Regression Note, Stakeholder Review, Lead Sign-off sections.
- **GATE-23** — new gate row for Pair Acceptance.md (blocking); owner Lead Lesandro.

**Created:**

- **docs/standards.md** — canonical rule registry with stable IDs for every blocking rule across DATA, ECON, VIZ, RES, APP, GATE, and META prefixes.
- **docs/sop-changelog.md** — this file.

**Rationale:** Regression-proofs the SOP system. Future agent dispatches can cite rules by stable ID (GATE-23, META-RPD, APP-AF2, etc.) rather than quoting SOP prose. The Reference Pair Doctrine and Pair Acceptance Checklist together turn tribal knowledge about pair-quality decisions into mechanical artifacts that reviewers and future agents cannot miss.

---

## 2026-04-11 — EOD Checkpoint (commit 93ed4b2)

**Scope:** EOD checkpoint capturing SOP hardening Parts D+E + trade log UX in a single marker. No new rules, but consolidates the day session work.

**Referenced:**

- SOP hardening Part D (c5bf1a9)
- SOP hardening Part E (62c60e9)
- Trade log UX fix (8ef55c5)
- HY-IG v2 retroactive fixes (b6dd6a9)

---

## 2026-04-11 — Trade Log UX (commit 8ef55c5)

**Scope:** Econometrics + Research + AppDev SOPs.

**Added:**

- **ECON-C4 / Rule C4** — Dual Trade Log Output (Internal + Broker-Style). Winner trade log produced in both internal schema and broker-style CSV for downstream consumers.
- **RES-PA3** — How to Read the Trade Log subsection mandatory on Strategy page narrative.
- **APP-AF5** — Column Legend Requirement for Downloadable Artifacts. Every CSV download must have an adjacent column-legend expander.

**Rationale:** HY-IG (pair #5) shipped a header-only trade log; downstream users had no way to interpret columns. Fix makes the trade log self-describing at three layers: file (broker CSV), portal (expander), narrative (worked example).

---

## 2026-04-11 — HY-IG v2 Retroactive Fixes (commit b6dd6a9)

**Scope:** No new SOP rules. Applied the hardened SOPs retroactively to HY-IG v2 to close stakeholder-reported gaps. Retroactive fixes served as the integration test for the new rule set.

**Validated rules:** GATE-22 (method coverage no regression), RES-EP1 (8-element template), VIZ-A3 (canonical chart catalog), META-RNF (regression note format), APP-EP4 (chart filename contract).

---

## 2026-04-11 — SOP Hardening Part E (commit 62c60e9)

**Scope:** Stakeholder-driven + self-review + cross-review fixes across all SOPs.

**10 stakeholder-driven rules added:**

- **RES-EP1** — Evidence Page 8-Element Template (Why / How / Method / Graph / Observation / Interpretation / Caveats / Link-back).
- **RES-EP2** — chart_status field mandatory in each method block.
- **RES-EP3** — Missing-Element Fallback Protocol (escalate before dropping).
- **RES-EP4** — Drop Only With Regression Note.
- **APP-EP1..EP5** — Render-side rules for 8-element template, caption fallback chain, render-time completeness check, chart filename contract (3.9a), missing-element fallback (3.9b).
- **GATE-22** — Method coverage no-regression gate item.

**15 self-review rules added:**

- **DATA-D3** — Classification Decision Procedure (mandatory workflow).
- **RES-B5** — Strategy Objective Classification.
- **ECON-C3** — Producer-Side Rerun Regression Check (method and numeric diff).
- **VIZ-A4** — Chart Regression Report with Spec Diff section.
- **RES-5b** — Regression Prevention Recipe (filesystem diff).
- plus audience-friendly refinements across AppDev SOP §3.8.

**10 cross-review fixes:**

- META-EOI expanded to cover prior-pair-version deviations and unit/scale conventions.
- META-UNK formalized: unknown classification is an error signal, not a fallback label.
- META-CFO formalized classification field ownership (Dana owns nature/type; Ray owns objective).
- VIZ-A2 + RES-4 cross-referenced for dual-notation consistency.
- GATE-19/20/21 ownership explicitly named on gate rows.

---

## 2026-04-10 — SOP Hardening Part D (commit c5bf1a9)

**Scope:** classification schema, 8-element template intro, landing page filters.

**Added:**

- **DATA-D3 / Classification Decision Procedure (first version)** — mandatory workflow for indicator_nature and indicator_type.
- **DATA-D2 / Default Unit Convention Registry** — canonical units per column suffix; rules for one unit per canonical name.
- **RES-IT1** — Indicator Type Classification in research brief with controlled vocabulary.
- **APP-LP1..LP7** — Landing Page Design Rules (executive summary, multi-dimensional filters, card numbering, performance badges, classification chips, metadata source, filter behavior for Unknown).
- **META-TWJ** — Tournament Winner JSON Schema formalized.

**Rationale:** Portal landing page needed filterable classification. Classification became the linchpin coordinating Dana, Ray, Evan, Vera, Ace.

---

## 2026-04-10 — HY-IG v2 Narrative Rewrite (commit d9aeaff)

**Scope:** No new rules. First full exercise of the audience-friendly rules on an existing pair.

**Validated:** RES-1, RES-2, RES-3, RES-4, APP-AF1..AF5.

---

## 2026-04-09 — Audience-Friendliness Rules (commit 61efe7d)

**Scope:** Research + AppDev SOPs.

**Added:**

- **RES-1** — Audience Assumption (write for layperson who knows markets).
- **RES-2** — Translation Bridge (plain-English on first use).
- **RES-3** — Method Justification (Why we chose this method sentence).
- **RES-4** — Unit Discipline — Inline Dual Notation (bps and percent on first use).
- **RES-6** — Glossary Quality Rubric (4-element standard).
- **APP-AF1** — Expander Philosophy: Defer Do not Expand.
- **APP-AF2** — Rule-First Strategy Cards.
- **APP-AF3** — Metric Interpretation Rule (interpretation caption on every KPI).
- **APP-AF4** — Translation Bridge Rendering.

**Rationale:** Stakeholder feedback that portal was too quant-dense for intended audience. Ray now assumes layperson; Ace renders with progressive disclosure.

---

## 2026-04-09 — Chart Rendering Fix (commit 8767a8a)

**Scope:** AppDev + Visualization contract.

**Added:**

- **APP-EP4 / Chart Filename Contract (Rule 3.9a)** — loader uses canonical filename only; no fallback to alternate filenames.
- **VIZ-NM1** — pair_id appears ONLY in directory path, NEVER in filename.

**Rationale:** Filename mismatch between Vera outputs and Ace loader was the single most common portal bug. Rule removes silent fallback behavior.

---

## 2026-04-08 — HY-IG v2 Full Pipeline Test (commit b009674)

**Scope:** No new rules. Full multi-agent pipeline test of hardened SOPs.

**Validated:** META-PSC (pipeline self-containment), ECON-DS1 (derived signal persistence), RES-EP1 (8-element template), VIZ-A3 (standard chart catalog).

---

## 2026-04-07 — SOP Hardening Core (commit 6cb5b4c)

**Scope:** Team coordination + Econometrics + AppDev + Research SOPs.

**Added:**

- **META-PSC / Pipeline Self-Containment Contract** — every pair has single self-contained pipeline script producing ALL downstream artifacts.
- **ECON-DS1 / Derived Signal Persistence Rule** — HMM probs, Markov states, z-scores, composites persisted to results/{id}/signals_{date}.parquet.
- **APP-RP1** — Rendering Patterns for Presentation Quality (st.container(border=True), no nested HTML, no markdown inside HTML wrappers).
- **RES-PA2** — Presentation Quality Patterns (skeptical reader framing, progressive disclosure, honest caveats).

**Rationale:** HY-IG (pair #5) required 3 separate scripts in specific sequence. HMM probability signal computed inside tournament but never persisted. Fragmented pipelines created invisible dependencies.

---

## 2026-03-20 — Deliverables Completeness Gate (commit a8ca9f6)

**Scope:** team-coordination.md.

**Added:**

- **GATE-1..GATE-18** — Deliverables Completeness Gate Step 8 with 18 gate items across analysis brief, dataset, stationarity, interpretation metadata, exploratory results, core models, tournament, charts, portal pages, navigation, catalog status, winner summary/trade log/execution notes.
- **META-MRA / MRA Mandatory** — Measure, Review, Adjust step after browser verification.
- **META-BV / Browser Verification Mandatory** — Playwright headless inspection after every portal change.
- **META-VF / Variant Families** — sharing pages across variants acceptable; omitting page type not.

**Rationale:** Pair #2 (TED Variants) shipped without Methodology page because no one verified all 4 pages existed. Browser verification checked rendering, not completeness.

---

## 2026-03-14 — Multi-Indicator Enhancement Framework (commit c367347)

**Scope:** All 6 SOPs.

**Added:**

- **ECON-C1 / Category-Specific Mandatory Method Catalog** — every indicator_type routes to a mandatory method list.
- **ECON-C2 / Mandatory Output Schema Per Method** — exact column schema for each mandatory method.
- **META-P0 / Phase 0: Analysis Brief Gate** — no agent starts work without approved brief.
- **ECON-T1 / Tournament Design Parameters** — target-class-aware tournament parameters.
- **ECON-T2 / Target-Class-Aware Backtest Parameters** — backtest parameters match target class.
- **RES-MS1 / Multi-Indicator Scaling** — tiered literature review, batch spec memos, canonical glossary, master event database.
- **RES-MS2 / Batch Direction Annotation Delivery** — direction annotations batched across pairs.
- **DATA-B1 / DATA-B2** — batch data availability pre-check and shared indicator deduplication.

**Rationale:** Scaling the team from single-pair analysis to 73-pair portfolio required framework generalization. Econometric catalog expanded 52 to 95 methods with 6 new categories and Relevance Matrix; data series catalog added 31 indicators and 35 targets.

---

## 2026-03-14 — Cross-Review Update (commit 9364b2c)

**Scope:** All 5 agent SOPs.

**Added (via self-update after cross-review):**

- **META-NO / New Agent Onboarding Protocol** — cross-review SOPs, self-update, distill lessons.
- **META-TCH1 / META-TCH2** — Task Completion Hooks (Validation/Verification and Reflection/Memory).
- **META-HO / META-ACK** — Handoff Protocol and Acknowledgment Protocol (silence is never acceptance).

**Rationale:** Cross-review surfaced handoff gaps that solo work missed.

---

## 2026-03-01 — HY-IG Initial Analysis (commit e2a4c65)

**Scope:** No SOP changes. First end-to-end pair.

**Surfaced issues later fixed:** HMM state inversion (commit 2c9368d), pipeline fragmentation (later META-PSC), header-only trade log (later ECON-C4).

---

## 2026-02-28 — Defensive Rules (commits 22ac0bf, efccb3b)

**Scope:** All agent SOPs.

**Added:**

- **META-D1 / Defense 1: Self-Describing Artifacts** — producer rule: meaningful column names, units, sign conventions, boundaries, sidecar manifest.
- **META-D2 / Defense 2: Reconciliation at Every Boundary** — consumer + reviewer rule: known-fact sanity checks, derived-quantity cross-check, automated reconciliation script.

**Rationale:** Prevent implicit-assumption errors at every agent boundary. HMM state inversion was the archetypal failure mode.

---

## 2026-02-15 — Visualization Integrity Rules (commit series)

**Scope:** Visualization SOP.

**Added:**

- **VIZ-A1** — No Inverted Axes on Financial Dashboards.
- **VIZ-A2** — Unit Discipline: Axis Labels Must Match Data Values.
- **VIZ-A3** — Standard Chart Catalog with Canonical Signal Selection.
- **VIZ-A5** — Caption Ownership (Ray displays, Vera audits).
- **VIZ-CP1** — Color Palette Mandatory (colorblind-friendly, consistent).
- **VIZ-CS1** — Standard Chart Set Per Pair (canonical 10-chart set).

**Rationale:** Consistent chart specifications across pairs. Canonical chart catalog prevents ad-hoc rerun drift.

---

## 2026-02-01 — App Dev Integration (commit 04c8f67, e9c6467)

**Scope:** New AppDev SOP + cross-review round 2.

**Added:**

- **APP-PA1 / APP-SF1 / APP-DA1 / APP-SP1** — Portal Architecture, Storytelling Flow, Direction Annotation, Strategy Execution Panel standards.
- **META-IA / Interpretation Annotation Handoffs** — four-agent protocol for same-indicator / different-target direction differences.

**Rationale:** Streamlit portal became canonical delivery surface.

---

## 2026-01-20 — Research Catalogs (commits 155204b, ef5b83b)

**Scope:** docs/ reference catalogs.

**Created:**

- data-series-catalog.md
- econometric-methods-catalog.md
- backtesting-approaches-catalog.md
- threshold-regime-methods-catalog.md
- reference-catalogs-index.md (with Run Registry — META-REG)

**Rationale:** Standing references that all agents consult.

---

## 2026-01-10 — Initial SOP Foundation (commits 10f4b0a, 652d1b5, 1156869)

**Scope:** First agent SOP set.

**Created:**

- data-agent-sop.md (Data Dana)
- econometrics-agent-sop.md (Econ Evan)
- visualization-agent-sop.md (Viz Vera) — early Rules A1/A2 form
- research-agent-sop.md (Research Ray)
- team-coordination.md — early handoff specifications, escalation rules

**Foundational rules established:**

- **DATA-DD1** — Data Dictionary (Display Name, Direction Convention, Effective Start, Unit, SA status, known quirks).
- **DATA-DD3** — Stationarity Test Delivery (ADF/KPSS/PP).
- **DATA-H1..H3** — handoff specifications.
- **ECON-SS1 / ECON-ES1 / ECON-DG1 / ECON-SA1** — Model Specification, Estimation Standards (HC3 default), Diagnostics Mandatory, Sensitivity Analysis.
- **RES-B1** — Two-Stage Delivery Protocol (spec memo + full brief).
- **META-CR** — Communication Rules (7-point).
- **META-ER** — Escalation Rules.
- **META-QS** — Quality Standards (team-wide).

---

## Appendix: Rule-to-Commit Cross-Reference

For rules whose source commit predates this changelog or is distributed across multiple commits, see git log and the originating SOP section. This changelog captures rule IDs going forward; earlier rules are registered in standards.md with their current SOP section as source.

## Appendix: How to Add an Entry

1. Identify the SOP(s) being changed.
2. Name each new or modified rule by ID (if new, pick an ID that fits the prefix scheme in standards.md).
3. Write a one-paragraph summary per rule: what changed, why, and what upstream evidence (commit, bug, stakeholder feedback) drove it.
4. Commit the SOP change, standards.md update, and this changelog entry together.
5. Entries are newest-first.
