# Cross-Review Round 3: Econ Evan

**Author:** Evan (Econometrics Agent, `econ-evan`)
**Date:** 2026-03-14
**Trigger:** Multi-indicator expansion design; updated SOPs with Defense 1 & 2; new Analysis Brief template
**Scope:** Full re-review of all teammate SOPs, team coordination protocol, and Analysis Brief template — focused on readiness for scaling from 1 pair (HY-IG → SPY) to 31 indicators × 35 targets

---

## 1. What I Learned About Each Teammate's Workflow and Pressures

### Data Dana

Dana operates under relentless completeness pressure. Her Quality Gates (data-agent-sop.md, "Quality Gates") demand that every delivered dataset include a data dictionary, summary statistics, stationarity test results, and documentation of missing-value treatment — all before she can mark a task done. That is a substantial checklist for every variable, and it multiplies linearly with the number of indicators.

**How my requests affect her workflow.** My Data Request Template (econometrics-agent-sop.md, Section 3) asks for preferred column names, specific transformations, stationarity tests, and frequency alignment. These are well-specified, and Dana's SOP (data-agent-sop.md, Section 1) confirms she expects exactly this level of detail. When I file mid-analysis expedited requests (econometrics-agent-sop.md, "Mid-Analysis Data Requests"), Dana's expedited protocol (data-agent-sop.md, "Expedited Protocol") gives her a lighter validation pass — stationarity tests and outlier checks are deferred. In the current single-pair workflow this is manageable; in a multi-indicator expansion where I might file 5-10 mid-analysis requests per batch, it could overwhelm Dana's pipeline and leave me with partially validated data.

**Multi-indicator expansion impact.** The Data Series Catalog lists 31+ indicators, many with derived series requiring specific computation recipes (data-agent-sop.md, Section 4, "Derived series" — references `docs/data-series-catalog.md`, Section 7.10). Dana must source raw components, compute derivatives, align frequencies (daily vs monthly vs quarterly), and deliver each with a full data dictionary. If I request 10 indicator-target pairs in a sprint, she is effectively running 10 parallel data pipelines. Her partial delivery protocol (data-agent-sop.md, "Partial Delivery Protocol") helps, but the throughput bottleneck is real.

**Frequency alignment is a latent friction point.** Dana's SOP mentions frequency alignment rules (data-agent-sop.md, Section 5, "Frequency alignment") and flagging staleness beyond 5 days. For mixed-frequency indicators like ISM PMI (monthly) paired against SPY (daily), the alignment method (LVCF, interpolation, MIDAS) directly affects my regression estimates. Dana documents the method in the data dictionary, but neither SOP currently specifies which alignment method is econometrically appropriate for which model class. LVCF is fine for regime models but creates artificial serial correlation for OLS regressions on daily data. This is a handoff subtlety that should be made explicit.

### Research Ray

Ray's two-stage delivery protocol (research-agent-sop.md, Section 6) is well-designed for my workflow. The Stage 1 Quick Spec Memo gives me enough to start baseline specification (DV, regressors, instruments, pitfalls, sample conventions) while the full brief is still in progress. This was a major friction-reduction from Round 1, and it works.

**What I need from Ray for category selection.** My Category Selection Heuristic (econometrics-agent-sop.md, Section 2.5) uses indicator type classification from Ray's brief. Ray's SOP includes a "Recommended Analysis Categories" section (research-agent-sop.md, Section 5 template) that maps indicator types to Relevance Matrix scores. This is exactly what I need — but the quality depends on Ray correctly classifying the indicator type. For novel or hybrid indicators (e.g., ISM Manufacturing/Services ratio — is it "Activity/Survey" or "Cross-Asset"?), the classification is non-trivial. A misclassification could lead me to skip a core category or waste budget on an irrelevant one.

**Method sensitivity flags remain the most valuable single line item in Ray's brief.** Ray's SOP (research-agent-sop.md, Section 3, "Method sensitivity") requires flagging when a paper's findings hold only under a specific econometric method. This directly informs my specification choices. In practice, this flag is the difference between running a futile OLS and discovering that the relationship only emerges under IV or regime-switching.

**Expected direction validation for the Analysis Brief.** The Analysis Brief (Section 4) requires `expected_direction` with a mechanism description and literature support level. Ray is the primary source for this field. For `ambiguous` or `conditional` directions, I need Ray to provide structured conditional logic — not just "direction varies by regime" but "bearish when VIX > 25, neutral when VIX < 15." This granularity feeds my Rule D (add Regime + Distributional categories) and Vera's conditional direction rendering.

### Viz Vera

Vera's primary pressure is interpretation clarity, and her SOP addresses it directly. Her "Inputs I Need" section (visualization-agent-sop.md) provides per-chart-type checklists, and her acknowledgment template (visualization-agent-sop.md, "Acknowledgment Template") gives me immediate feedback on gaps in my handoff. The Data Ingestion Validation workflow (visualization-agent-sop.md, "Data Ingestion Validation") — read manifest, run assertions, cross-check against known periods — is Defense 2 in action.

**How `interpretation_metadata.json` affects her.** Vera consumes my metadata for the Direction Annotation Visual Language (visualization-agent-sop.md, Section 5): solid line = pro-cyclical, dashed = counter-cyclical, dash-dot = conditional. For binary cases this is clean. For `conditional` direction, the label says "Direction varies by regime," which is too vague for a multi-pair dashboard. I need to provide more granular regime-direction mappings, and Vera's SOP should specify where to display the conditional text (inline annotation vs. callout box vs. legend entry).

**Manifest assertions are a critical error-catching gate.** The HMM state inversion bug we fixed earlier would have been caught by Vera's assertion-checking workflow had it existed then. My current SOP requires "at least one sanity-check assertion" per manifest. Reading Vera's ingestion validation process, I realize one assertion is insufficient — she runs every assertion and stops on failure. I should require a minimum of 3 assertions per artifact: (a) one per well-known historical episode in sample, (b) one distributional check, (c) one sign-convention check.

**What Vera needs beyond the chart request template.** Vera's quality gates include numerical reconciliation (visualization-agent-sop.md, "Quality Gates", "Numerical reconciliation"): she verifies that numbers in charts match my tournament results CSV. This means I must deliver tournament results in a clean, machine-readable CSV with unambiguous column names and all metrics she might reconcile against (Sharpe, max DD, annualized return, win rate) in a single canonical file. My current handoff covers this, but I should double-check completeness per pair.

### AppDev Ace

Ace is the integration endpoint and therefore the most exposed to upstream errors converging. His SOP (appdev-agent-sop.md, "Inputs I Need") documents what he needs from me: model result summaries, backtest performance tables, strategy rules in plain English, and interactive analysis specifications.

**My App Dev Handoff Template works.** In Round 2, I identified the gap and created the template (econometrics-agent-sop.md, "App Dev Handoff Template"). It covers headline findings, KPI values, backtest performance, strategy rules, interactive dimensions, and data files. However, Ace's SOP (appdev-agent-sop.md, "From Econometrics Agent") still states "Evan currently has no formal Econ-to-AppDev handoff template." This is stale documentation and should be corrected.

**Gaps for multi-target portal.** My handoff template is designed for a single indicator-target pair. For a multi-target portal (same indicator → SPY, TLT, HYG, GLD), Ace needs:
1. Per-pair `interpretation_metadata.json` (I produce this)
2. A cross-pair comparison summary: which target shows the strongest signal? Do directions differ?
3. Consistent KPI schemas across pairs so his components can iterate programmatically
4. A `kpis.json` file (Ace's SOP mandates JSON loading in Section 5), not just a markdown KPI table

My template does not currently include items 2 or 4. These are gaps I must close.

**Benchmark display is target-class-aware.** Ace's SOP (appdev-agent-sop.md, Section 3, Page 4) notes that "benchmark selection is target-class-aware." This means my handoff must explicitly state the benchmark for each pair, sourced from the Analysis Brief Section 4. If I deliver results without specifying the benchmark, Ace defaults to SPY, which is wrong for TLT or crypto targets.

---

## 2. Where Our Handoffs Connect and Where Friction Could Arise

### Handoff Map (Evan's Connections)

```
Ray ──[Spec Memo + Research Brief]──→ Evan
Dana ──[Dataset + Dict + Stationarity]──→ Evan
Evan ──[Mid-Analysis Request]──→ Dana
Evan ──[Chart Request + Manifests + interpretation_metadata.json]──→ Vera
Evan ──[App Dev Handoff + kpis.json + interpretation_metadata.json]──→ Ace
Evan ──[Acknowledgment]──→ Ray, Dana
Ray ──[Direction validation]──→ interpretation_metadata.json
Vera ──[Direction visual encoding]──→ from interpretation_metadata.json
Ace ──["How to Read This" callout]──→ from interpretation_metadata.json
```

### NEW Friction Points from Multi-Indicator Expansion

**F1. The 5D Tournament Grid (3,528 combinations per pair).**
With 31 indicators × up to 35 targets, the full expansion could produce 31 × 35 × 3,528 = ~3.8 million strategy combinations. Even with the computational budget cap (Analysis Brief Section 8.2, default `{MAX_PLAYERS}` = 10,000), the aggregate across all pairs is ~10.8 million evaluations. My SOP's stratified sampling section (econometrics-agent-sop.md, "Computational budget") handles within-pair budgeting, but there is no cross-pair budgeting protocol. Who decides which pairs get a full grid vs. a reduced grid? This should be specified in either the Analysis Brief or team coordination protocol.

**F2. Category Selection Heuristic at scale.**
My heuristic (econometrics-agent-sop.md, Section 2.5, Rules A-D) requires me to check stationarity (Rule A), frequency mismatch (Rule B), indicator type (Rule C), and direction uncertainty (Rule D) for every pair. For 31 indicators, some rules can be pre-computed: stationarity is a property of the series, not the pair. But Rule D depends on the pair-specific `expected_direction` from each Analysis Brief. If 20 Briefs arrive in a sprint, I face 20 category-selection decisions before starting any models. Partial automation — a lookup table mapping indicator types to default category sets — would help.

**F3. Interpretation metadata consistency across hundreds of pairs.**
Each pair produces an `interpretation_metadata.json`. If VIX/VIX3M is analyzed against 5 different targets, I produce 5 metadata files. These must be internally consistent (same `expected_direction` for the same indicator when the mechanism is the same) but may legitimately differ in `observed_direction` (VIX rising is bearish for SPY but potentially bullish for TLT). The team coordination protocol (team-coordination.md, "Interpretation Annotation Handoffs") handles this conceptually, but at 100+ pairs, manual consistency checking is infeasible. We need an automated cross-pair consistency check.

**F4. Target-class-aware backtest parameters.**
My SOP (econometrics-agent-sop.md, "Target-Class-Aware Backtest Parameters") specifies different parameters per asset class: transaction costs (5 bps equity vs. 10-30 bps crypto), calendars (US market hours vs. 24/7), Sharpe validity thresholds (0.3 equity vs. 0.2 crypto), and benchmarks. The Analysis Brief (Section 8.3) is where these are specified per pair. If Alex produces Briefs in batches, an error in the backtest parameters table (e.g., equity Sharpe threshold applied to a crypto target) would silently invalidate tournament results. This is a Defense 2 reconciliation point I must check on brief intake.

**F5. Reverse causality diagnostic at scale.**
My SOP mandates a Local Projection reverse causality check (econometrics-agent-sop.md, Section 7, "Reverse causality check") for every indicator-target analysis. For each pair, I run Jorda LP regressions at horizons 1-12 in both directions. With 31 × 35 = 1,085 pairs, that is 1,085 × 24 = 26,040 LP regressions just for this diagnostic. Feasible but time-consuming. A batch reporting template would help.

**F6. Computational budget management across the expansion.**
The Analysis Brief (Section 8.2) specifies `{MAX_PLAYERS}` per pair with a default of 10,000. But there is no team-level computational budget. If each pair gets 10,000 combinations and we run 100 pairs, that is 1 million tournament evaluations. Who tracks this aggregate? The team coordination protocol should define a per-sprint computational budget ceiling.

**F7. Analysis Brief acknowledgment overhead at batch scale.**
The Phase 0 Brief Acknowledgment Protocol (team-coordination.md, "Brief Acknowledgment Protocol") requires each agent to send a structured acknowledgment per brief. A batch of 10 Briefs generates 10 × 5 = 50 acknowledgment messages before any work starts. A batch acknowledgment mechanism ("I have read and accept Briefs 3-12; concerns on Brief 7 re: data availability") would be more practical.

---

## 3. Suggestions for Each Teammate's SOP

### For Dana's SOP

1. **Add frequency alignment method guidance by model class.** Dana's SOP (Section 5, "Frequency alignment") documents alignment methods but does not distinguish which method is appropriate for which downstream model. Suggestion: add a lookup table — "If downstream model is OLS/VAR → LVCF is safe but flag serial correlation risk. If MIDAS → provide both high-freq and low-freq series. If regime-switching → LVCF is preferred." This prevents me from receiving a dataset with an alignment method that biases my estimates.

2. **Derived series computation verification.** Dana's SOP (Section 4, "Derived series") references computation recipes from the Data Series Catalog. Add a quality gate: "For every derived series, verify computation against at least one known published value (e.g., HY-IG spread on 2008-10-10 should match FRED source data within ±5 bps)." This is Defense 2 applied at the computation step.

3. **Batch delivery option.** For multi-indicator sprints, Dana should consider delivering a "master dataset" containing all core indicators for a given target, rather than separate files per indicator. This reduces my data ingestion overhead from N separate handoffs to 1 per target. The data dictionary would need to scale accordingly.

4. **Stable `_latest` alias for model-consumed data.** Dana's SOP has a stable filename alias for portal-bound datasets (data-agent-sop.md, Section 6, "Stable filename alias") but only for Ace. I would benefit from the same convention for model inputs — especially for re-runs, sensitivity analysis, and tournament re-executions where I need to re-read the "current" dataset without tracking date-stamped filenames.

### For Ray's SOP

5. **Category recommendation rationale depth.** Ray's "Recommended Analysis Categories" section (research-agent-sop.md, Section 5 template) provides a table with relevance scores. The rationale column should specify *why* each score is assigned: "Lead-Lag: ++ because 3 papers find Granger causality at monthly frequency" is actionable; "Lead-Lag: ++" is not. At scale, I cannot independently verify each score against the literature.

6. **Indicator type classification for hybrids.** Ray's SOP should address how to classify hybrid indicators that span multiple types (e.g., ISM Mfg/Svc ratio — is it "Activity/Survey" or "Cross-Asset"?). My heuristic (Rule C) uses a single indicator type. A tie-breaking rule or "primary type + secondary type" convention would prevent computational budget inflation from defaulting to the broader set.

7. **Expected direction conditional logic.** For `ambiguous` or `conditional` expected directions, Ray should provide structured conditional logic, not just "direction varies by regime." Example: "VIX rising from below 15 = bullish (volatility mean-reversion); VIX rising from above 25 = bearish (stress escalation)." This feeds both my Rule D and Vera's conditional direction rendering.

8. **Literature support → interpretation confidence mapping.** Ray rates evidence as "established / emerging / exploratory" (research-agent-sop.md, Section 7). This should map explicitly to my `direction_confidence` field in `interpretation_metadata.json`: established → high, emerging → medium, exploratory → low. This prevents me from expressing high confidence in a direction with weak literature support.

### For Vera's SOP

9. **Conditional direction visual language needs more specificity.** Vera's Direction Annotation Visual Language (visualization-agent-sop.md, Section 5) uses dash-dot lines for "conditional" direction with the label "Direction varies by regime." For multi-pair dashboards, this label should include the regime condition. I should provide the conditional text in my interpretation metadata, and Vera's SOP should specify where to display it (inline annotation, legend entry, or separate callout box — these have different space constraints).

10. **Tournament results visualization template.** Vera's "Inputs I Need" covers standard chart types but does not include templates for tournament-specific visualizations: heatmaps of Sharpe ratios across the 5D grid, parallel coordinates for top-N winners, signal-threshold interaction plots. I will need to request these, and standard templates would reduce friction.

11. **Cross-pair numerical reconciliation.** Vera's quality gates require reconciling chart numbers against source CSVs. For multi-pair dashboards, the reconciliation must verify that each pair's numbers come from the correct pair's CSV, not a neighboring pair's file. A naming convention check (chart ID contains indicator_id + target_id; source CSV contains same) would prevent cross-pair contamination.

### For Ace's SOP

12. **Update "From Econometrics Agent" section.** Ace's SOP (appdev-agent-sop.md, "From Econometrics Agent") states "Evan currently has no formal Econ-to-AppDev handoff template." This is outdated. My SOP (econometrics-agent-sop.md, "App Dev Handoff Template") has a comprehensive template. Ace should reference it.

13. **Multi-pair portal architecture guidance.** Ace's standard portal structure (appdev-agent-sop.md, Section 2) is a 5-page layout. For multi-target portals (same indicator → multiple targets), Ace needs guidance on architecture:
    - (a) One 5-page portal per pair (simple but fragmentary)
    - (b) Master portal with pair-selection sidebar (integrated but complex)
    - (c) Hybrid: shared Pages 1-2, pair-specific Pages 3-4
    This decision affects what I deliver (per-pair vs. cross-pair summaries) and should be resolved before the expansion begins.

14. **`kpis.json` schema standardization.** Ace mandates loading KPIs from `results/kpis.json` (appdev-agent-sop.md, Section 5). The schema should be documented so I know exactly what fields to populate. Suggested schema: `[{metric: string, value: number, unit: string, label: string, source_file: string, source_field: string}]`. I will produce this file alongside my handoff.

15. **Tournament display across asset classes.** Ace needs guidance on displaying tournament results when the Sharpe validity threshold differs by asset class. The portal should communicate: "This strategy's Sharpe of 0.35 exceeds the equity threshold of 0.3" vs. "This Sharpe of 0.35 would not meet the fixed income threshold of 0.5." I should include the applicable threshold in my handoff, and Ace should display it alongside the metric.

### For Team Coordination Protocol

16. **Batch acknowledgment mechanism.** The current acknowledgment protocol (team-coordination.md, "Brief Acknowledgment Protocol") requires per-brief, per-agent acknowledgments. For batches of 10+ Analysis Briefs, allow a single batch acknowledgment: "Acknowledged Briefs #3-#12. Concerns on #7: ISM ratio data source unconfirmed." This reduces message volume from O(agents × briefs) to O(agents).

17. **Cross-pair consistency check protocol.** The Interpretation Annotation Handoffs section (team-coordination.md) defines per-pair annotation. Add a cross-pair consistency step: before portal assembly, run an automated check verifying (a) same indicator has consistent `expected_direction` across targets when the mechanism is the same, (b) `observed_direction` differences are documented, (c) Vera's visual encoding matches metadata for all pairs.

18. **Aggregate computational budget.** Add a per-sprint computational budget ceiling to the team coordination protocol. This prevents the scenario where 100 simultaneous pairs each request 10,000 tournament combinations without anyone tracking the aggregate.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

Reading my teammates' SOPs — particularly the updated versions with Defense 1 & 2 and the new Analysis Brief template — surfaced these gaps in my own workflow:

### A. `kpis.json` delivery is not explicit

My App Dev Handoff Template specifies KPIs as a markdown table but does not require a `kpis.json` file. Ace's SOP mandates JSON loading. I should add to my handoff deliverables: "Deliver `results/kpis.json` alongside the handoff message." And define the schema: `[{metric, value, unit, label, source_file, source_field}]`.

### B. Cross-pair comparison summary is missing

My handoff template is single-pair. For multi-target analyses, I should add a "Cross-Pair Summary" section comparing:
- Signal strength across targets (which target shows the strongest predictive relationship?)
- Direction consistency (does the same indicator have the same direction for all targets?)
- Sharpe ratio comparability (adjusted for asset-class-specific thresholds)
- A flag when an indicator shows opposite direction for different targets (e.g., counter-cyclical for SPY, pro-cyclical for TLT)

### C. Category selection heuristic needs batch mode

My heuristic (Section 2.5) is sequential and per-pair. For batch operation, I should pre-compute indicator-level properties (stationarity, type classification) once and apply them across all targets for that indicator. This eliminates redundant ADF/KPSS tests and speeds up the specification phase.

### D. Tournament design section lacks lookback window worked examples

My tournament grid includes lookback windows (LB60, LB120, LB252). The worked examples in Section 2.5 do not illustrate how lookback interacts with signal generation. A Z-score signal with LB60 lookback has very different characteristics (more responsive, higher turnover) than LB252 (smoother, fewer trades). I should add a worked example showing this interaction and its implications for strategy selection.

### E. Target-class backtest parameters need crypto-specific detail

My target-class table lists crypto parameters but lacks detail on: weekend effects (24/7 trading means no Monday open gaps), the very short history problem (BTC from 2014 = ~2,500 daily observations; ETH from 2017 = ~2,000), and minimum degrees-of-freedom requirements per model class. Statistical power with 120 monthly observations is fundamentally different from 300+. I should add:
- Minimum sample requirements by model class for short-history assets
- Guidance on method restriction for crypto targets (e.g., "cointegration requires 200+ monthly observations — skip for ETH targets")
- Bootstrap inference as default for short samples

### F. Reverse causality reporting needs a batch template

My SOP mandates reverse causality checks but provides no batch reporting format. A summary table across pairs would be valuable:

| Indicator | Target | Forward p-value | Reverse p-value | Interpretation |
|-----------|--------|----------------|----------------|----------------|
| HY-IG | SPY | 0.003 | 0.42 | Clean predictive signal |
| VIX | SPY | 0.001 | 0.018 | Bidirectional; feedback loop |

### G. Manifest assertions coverage is underspecified

My SOP requires "at least one sanity-check assertion" per manifest. Reading Vera's validation workflow, one assertion is insufficient. I should require minimum 3 assertions:
1. One assertion per well-known historical episode in the sample (GFC, COVID)
2. One distributional check (mean, median, or range)
3. One sign-convention check (higher values mean what the column name says)

### H. Analysis Brief intake validation

The Analysis Brief template (Section 8.3, "Target-Class-Specific Parameters") specifies backtest parameters that directly affect my tournament. I should add an explicit intake validation step: when receiving a new Brief, verify that the target-class parameters (Sharpe threshold, transaction costs, benchmark, calendar) are consistent with the target's asset class. If SPY is listed with a 24/7 calendar, that is an error I should catch immediately, not discover during backtest execution.

---

## 5. Key Concerns for the Multi-Indicator Expansion

### 5.1 Computational Feasibility

**Scale of the problem.** The Econometric Methods Catalog contains ~95 methods across 8+ categories. With 31 indicators × 35 targets = 1,085 pairs, the full expansion at face value is enormous. However, the Category Selection Heuristic (Rules A-D) typically selects 3-5 categories per pair, yielding ~15-25 methods per pair. That gives ~20,000-27,000 model estimations across all pairs.

The tournament adds up to 3,528 combinations per pair (6 signals × 7 thresholds × 4 strategies × 7 lead times × 3 lookbacks). With stratified sampling at the 10,000 cap, the total across 1,085 pairs is ~10.8 million tournament evaluations. Pruning redundant combinations (HMM signal + HMM threshold) and prioritizing high-relevance pairs reduces this, but the aggregate is still significant.

**Mitigation.** The team needs an aggregate resource allocation plan with three tiers:
1. **Tier 1 (full analysis):** Priority pairs from `docs/priority-combinations-catalog.md` — full method set + full tournament grid
2. **Tier 2 (focused analysis):** Secondary pairs — core categories only + reduced tournament grid (stratified sample)
3. **Tier 3 (screening):** Exploratory pairs — correlation + lead-lag screening only, tournament on demand if results are promising

### 5.2 Statistical Power with Short Crypto Histories

BTC-USD daily data from ~2014 provides ~2,500 daily observations (~120 monthly). ETH-USD from ~2017 provides ~2,000 daily (~100 monthly). For monthly-frequency methods (cointegration, structural VAR), this is marginal. A VAR(4) with 3 variables consumes 12 degrees of freedom per equation before exogenous variables. The IS/OOS split further reduces usable sample.

**Recommendation for crypto targets:**
- Restrict method set to methods that work with short samples: rolling correlations, 2-state regime-switching, simple threshold strategies
- Use bootstrap inference rather than asymptotic distributions
- Document reduced statistical power in every results narrative
- Set wider confidence intervals in interpretation metadata (`direction_confidence` capped at "medium" for < 150 monthly observations)
- Add explicit minimum-observations requirements per model class to my SOP

### 5.3 Comparability of Sharpe Ratios Across Asset Classes

The target-class backtest parameters set different Sharpe validity thresholds (0.3 for equities, 0.5 for fixed income, 0.2 for crypto). Raw Sharpe ratios are not comparable across asset classes with different volatility profiles. A Sharpe of 0.5 on a 15% vol equity target represents different economic value than 0.5 on a 5% vol Treasury target.

**Unresolved issue for portal display.** When the portal shows cross-asset-class comparisons ("Which pair has the best risk-adjusted performance?"), raw Sharpe is misleading. Options:
- (a) Report asset-class-adjusted Sharpe (Sharpe relative to class-specific threshold)
- (b) Use Omega ratio or Sortino ratio (less affected by vol level)
- (c) Report dollar-risk-adjusted metrics (return per unit of max drawdown)
The team should decide on a cross-class comparison metric before the expansion begins.

### 5.4 Interpretation Metadata Consistency at Scale

With 1,085 potential pairs producing `interpretation_metadata.json` files, automated consistency checks are essential:

1. **Direction consistency by indicator:** For a given indicator, if the mechanism is the same across targets, `expected_direction` should be consistent. Exceptions (e.g., VIX → SPY is counter-cyclical but VIX → TLT may be pro-cyclical) must be documented with a distinct mechanism.
2. **Confidence calibration:** If Ray rates literature support as "Exploratory," my `direction_confidence` should not be "high." Cross-check between Ray's evidence rating and my confidence field should be automated.
3. **Mechanism text deduplication:** For the same indicator across targets, mechanism text should be templated with target-specific substitution, not written fresh each time (risking inconsistency).

### 5.5 Pipeline Throughput and Sequencing

The standard task flow (team-coordination.md) is sequential: Research → Data → Econometrics → Visualization → App Dev. For multi-indicator expansion, we need partial parallelism: multiple pairs at different pipeline phases simultaneously.

Key throughput concerns:
1. **Phase tracking per pair.** The Analysis Brief's deliverables checklist (Section 9) handles this, but the team needs a dashboard showing all pairs' pipeline status.
2. **Inter-pair data sharing.** Some indicators share raw data (VIX and VIX/VIX3M both need VIX series). Dana should source shared series once.
3. **My throughput bottleneck.** I am the narrowest point in the pipeline: Research and Data run in parallel for multiple pairs, but I process each pair through specification → estimation → diagnostics → tournament sequentially. If I receive 10 pairs' data simultaneously, I need a prioritization framework. The Analysis Brief should include a priority tier.

### 5.6 Analysis Brief Template Assessment

The new Analysis Brief template (docs/analysis_brief_template.md) is comprehensive and well-structured. From my perspective:

**Strengths:**
- Section 4 (Expected Direction) with mechanism, literature support, and conditional logic — exactly what I need for interpretation metadata
- Section 7 (Method Classes) with the Category Selection Heuristic matrix — aligns with my SOP Section 2.5
- Section 8 (Tournament Design) with target-class-specific parameters — aligns with my SOP's backtest parameters table
- Section 11 (Quality Standards) with mandatory reverse causality check (G11 resolution) and interpretation metadata schema
- Section 9 (Deliverables Checklist) for per-pair progress tracking

**Gaps I would flag:**
- No cross-pair comparison deliverable in Section 9. When the same indicator is analyzed against multiple targets, there should be a "Cross-Pair Summary" deliverable owned by Evan.
- Section 8.2 (Computational Budget) specifies per-pair budget but not per-sprint aggregate. For batch Analysis Briefs, the total across all briefs should be tracked.
- The placeholder `{AGENT_LIST}` at the bottom should default to "All agents" unless the pair requires a reduced team.

### 5.7 Automation Opportunities

Several parts of my workflow could be templatized for the expansion:

| Task | Current State | Automation Opportunity |
|------|--------------|----------------------|
| Category selection | Manual heuristic per pair | Lookup table: indicator_type × rules → default category set |
| Stationarity check | Per-series ADF/KPSS | Pre-compute once per indicator; reuse across targets |
| Reverse causality | Per-pair LP regression | Batch script running all pairs; output summary table |
| `interpretation_metadata.json` | Manual per pair | Template with indicator-level defaults; pair-specific overrides |
| `kpis.json` | Not currently produced | Auto-extract from tournament results CSV |
| Manifest assertions | Manual per artifact | Template assertions per indicator type (spread → check GFC levels) |

These automations reduce per-pair marginal cost while maintaining the same quality gates.

---

## Summary of Top Recommendations

| # | Recommendation | Affects | Priority |
|---|---------------|---------|----------|
| 1 | Add cross-pair consistency check protocol to team coordination | All agents | High |
| 2 | Define aggregate computational budget per sprint/batch | Alex, Evan | High |
| 3 | Add `kpis.json` to Evan's mandatory handoff deliverables | Evan, Ace | High |
| 4 | Add frequency-alignment-by-model-class guidance to Dana's SOP | Dana, Evan | High |
| 5 | Update Ace's SOP to reference Evan's existing App Dev Handoff Template | Ace | Medium |
| 6 | Add batch acknowledgment mechanism to the Analysis Brief protocol | All agents | Medium |
| 7 | Expand conditional direction visual language (Vera) and conditional metadata (Evan) | Vera, Evan | Medium |
| 8 | Increase minimum manifest assertions from 1 to 3 per artifact | Evan, Vera, Ace | Medium |
| 9 | Define cross-asset-class comparison metric for portal displays | Evan, Ace, Alex | Medium |
| 10 | Add multi-pair portal architecture guidance to Ace's SOP | Ace, Alex | Medium |
| 11 | Add crypto-specific minimum sample requirements to Evan's SOP | Evan | Medium |
| 12 | Add cross-pair summary deliverable to Analysis Brief Section 9 | Evan, Alex | Low |
| 13 | Add indicator type tie-breaking rule for hybrids to Ray's SOP | Ray, Evan | Low |
| 14 | Add reverse causality batch reporting template to Evan's SOP | Evan | Low |

---

---

## Addendum: Accept/Reject Rationale for SOP Self-Updates (Step 2)

**Date:** 2026-03-14
**Context:** After writing the R3 cross-review above, I read all 4 teammates' cross-reviews for feedback directed at my SOP. Below is the consolidated inventory with my accept/reject decision and rationale for each item.

### From Data Dana's Review

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| D1 | Add batch data request template for multi-indicator sprints | **Accepted** | Added full Batch Data Request template to Section 3. Dana's point about reducing round-trips is directly supported by the multi-indicator expansion math. |
| D2 | Clarify frequency alignment responsibility — who decides the method? | **Accepted** | Added explicit guidance to Section 3: "Specify the desired alignment frequency and method in the request." Evan owns the econometric suitability; Dana owns the implementation. |
| D3 | Fix `observed_direction` format inconsistency (+1/-1 vs. string) | **Accepted** | Rewrote `interpretation_metadata.json` schema. Now uses string vocabulary (`pro_cyclical`, `counter_cyclical`, `ambiguous`, `conditional`) matching Analysis Brief Section 11.4. |
| D4 | Add data provenance to tournament output | **Accepted** | Added `data_provenance` field to `interpretation_metadata.json` with `input_file`, `input_hash`, and `sample_period`. |

### From Research Ray's Review

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| R1 | Add batch category selection workflow for multi-indicator sprints | **Accepted** | Added batch mode instructions after Section 2.5 worked examples. Pre-compute indicator-level properties (Rules A-C) once, apply pair-specific Rule D individually. |
| R2 | Create reusable spec templates by indicator type | **Accepted** | Added "Multi-target specification reuse" paragraph to Section 2.5. Templates capture stationarity, frequency, type, and base categories per indicator. |
| R3 | Add direction consistency checks across targets | **Accepted** | Added "Cross-pair direction consistency check" paragraph to the interpretation metadata section. Flags when same-class targets show different observed directions for the same indicator. |
| R4 | Improve Rule C input quality — request clarification on ambiguous classifications | **Accepted** | Added "Indicator type classification check" paragraph to Section 2. Requires clarification from Ray before running the heuristic on borderline cases. |

### From Viz Vera's Review (R3)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| V1 | Move `interpretation_metadata.json` to Quality Gates as mandatory checklist item | **Accepted** | Added three new quality gate items: `interpretation_metadata.json`, `kpis.json`, and `_manifest.json` (with 3-assertion minimum). |
| V2 | Add `recommended_charts` field to interpretation metadata | **Accepted** | Added to the rewritten `interpretation_metadata.json` schema. Lists chart types appropriate for the pair's results. |
| V3 | Add target-class Y-axis scaling hint to chart request template | **Accepted** | Added `Target class` field to the chart request template. Vera uses this to determine Y-axis scaling and vol annotation range. |
| V4 | Add tournament visualization recommendation guidance to chart requests | **Accepted** | Added "Tournament visualization guidance" paragraph to chart request guidance section. Specifies heatmap, equity curve comparison, and drawdown timeline as common tournament chart types. |
| V5 | Add manifest for tournament results with grid dimensions and sampling metadata | **Accepted** | Added `tournament_manifest.json` requirement to the tournament output format section. Documents grid dimensions, total combinations, sampling applied, and assertions. |

### From AppDev Ace's Reviews (R2 + R3)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| A1 | Add `kpis.json` as mandatory deliverable — Ace loads KPIs from JSON, not markdown | **Accepted** | Added "KPI File (mandatory)" section to App Dev Handoff Template with file path convention `results/{indicator_id}_{target_id}/kpis.json`. |
| A2 | Use naming convention `results/{indicator_id}_{target_id}/` for interpretation metadata | **Accepted** | Added file path convention to the interpretation metadata section. All per-pair artifacts now use this pattern. |
| A3 | Add `callout_text` field for portal "How to Read This" boxes | **Accepted** | Added to `interpretation_metadata.json` schema. Written by Evan as domain expert; Ace renders directly. |
| A4 | Split tournament results into summary CSV + detail CSV | **Accepted** | Added "Tournament output format" section with summary CSV (all 3,528 rows) and detail CSV (top 10 equity curves). |
| A5 | Add cross-pair comparison summary for multi-target handoffs | **Accepted** | Added "Cross-Pair Comparison Summary" table to App Dev Handoff Template with columns for indicator, target, top strategy, Sharpe, max DD, and direction consistency. |

### From Self-Identified Blind Spots

| # | Blind Spot | Decision | Rationale |
|---|-----------|----------|-----------|
| S-A | `kpis.json` delivery not explicit | **Accepted** | Same as A1. |
| S-B | Cross-pair comparison summary missing | **Accepted** | Same as A5. |
| S-C | Category selection heuristic needs batch mode | **Accepted** | Same as R1. |
| S-D | Tournament design lacks lookback window worked examples | **Accepted** | Added worked example #4 to Section 2.5 explaining LB60 vs. LB252 interaction with signal characteristics. |
| S-E | Crypto-specific minimum sample requirements missing | **Accepted** | Added crypto minimum requirements (1,500 daily observations) and exchange data quality note to target-class backtest parameters section. |
| S-F | Reverse causality reporting needs batch template | **Accepted** | Added batch reverse causality summary table template to Section 7 diagnostics. |
| S-G | Manifest assertions minimum too low (1 → 3) | **Accepted** | Changed from "at least one" to "at least three" with specified categories: stress period, calm period, magnitude/range plausibility. |
| S-H | Analysis Brief intake validation missing | **Accepted** | Added "Intake validation (mandatory)" paragraph to Section 1. Checks target-class parameter consistency on brief receipt. |

### Summary

**Total items reviewed:** 24 (4 from Dana, 4 from Ray, 5 from Vera, 5 from Ace, 8 self-identified — with 2 overlaps)
**Accepted:** 24 (100%)
**Rejected:** 0

All suggestions were well-grounded and directly supported by the multi-indicator expansion requirements. The high acceptance rate reflects the quality of the cross-review process — teammates identified genuine gaps, not stylistic preferences.

---

*Addendum completed: 2026-03-14*
*Agent: Econ Evan (`econ-evan`)*
*Round: 3 (Multi-indicator expansion + Analysis Brief template)*
