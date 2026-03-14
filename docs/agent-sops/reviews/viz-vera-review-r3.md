# Cross-Review Round 3: Viz Vera

*Reviewer:* Viz Vera (Visualization Agent)
*Date:* 2026-03-14
*Trigger:* Multi-indicator expansion framework -- scaling from 1 indicator-target pair (HY-IG -> SPY) to 73+ priority combinations across 31 indicators and 35 targets

---

## 1. What I Learned About Each Teammate's Workflow and Pressures

### Data Dana

Dana's data dictionary now carries a **Display Name** column explicitly for chart-ready labels (e.g., `us_cpi_yoy` -> "US CPI (% YoY)"). This is a direct response to my R1 review, and it is exactly what I need. However, the expansion to 31 indicators introduces a scaling concern: does Dana's SOP ensure that **every one of the 31 indicators and 35 targets** has a consistent, chart-ready display name? The Data Series Catalog (`docs/data-series-catalog.md`) provides canonical names, but canonical names are not the same as display names -- "ICE BofA US HY OAS minus ICE BofA US IG OAS" is canonical but unusable as an axis label.

Dana's SOP also now includes **derived series computation recipes** (Section 7.10 of the Data Series Catalog): I17 SOFR-US3M, I19 HY-IG spread, I22 VIX/VIX3M, I30 Gold/Copper, I31 ISM ratio, I32 New Orders YoY. These derived indicators need display names too, and the display name must capture the computation (e.g., "VIX/VIX3M Ratio" not just "I22"). If I receive data with column name `vix_vix3m` and no display name mapping, I have to guess, which risks a chart label that misleads the reader.

Dana also now provides **frequency alignment documentation** (Section 9 of the Data Series Catalog). With 31 indicators spanning daily (VIX), weekly (NFCI), monthly (ISM), and quarterly (GDP) frequencies, alignment will be a constant issue for charts that overlay multiple indicators or compare indicator-target pairs. I need to know the alignment method used so I can annotate charts appropriately -- "ISM PMI (last-value carried forward to daily)" versus "ISM PMI (interpolated to daily)" have different visual implications.

**Key pressure for Dana at scale:** Maintaining display names, units, sign conventions, and quirks documentation for 63+ series. Any gap cascades directly to chart quality. A missing display name for one indicator means a chart with a cryptic axis label.

### Econ Evan

Evan's SOP now includes two major additions that directly affect my workflow:

1. **`interpretation_metadata.json`** -- This file is produced for every indicator-target pair and contains: `direction` (+1/-1), `mechanism` (plain English), `confidence`, `expected_direction`, `observed_direction`, `contradictions`. This is the single most important new input for my direction annotation visual language (solid/dashed/dotted/dash-dot lines). Without this file, I cannot encode direction in charts.

2. **Expanded tournament design** -- 5 dimensions (Signal x Threshold x Strategy x Lead Time x Lookback) producing up to 3,528 combinations per pair. For 73 priority pairs, that is up to 257,544 tournament entries across the project. The tournament results CSV will be massive, and charts summarizing tournament outcomes (heatmaps, sensitivity plots, winner comparison dashboards) will need to be templated and parameterized rather than hand-crafted per pair.

Evan's **Category Selection Heuristic** (Rules A-D) determines which of 8 method categories to apply per indicator type. Different indicator types trigger different method mixes, which means different chart types will be appropriate for different pairs. A volatility/options indicator (VIX -> SPY) may need regime probability charts and tail-risk distributions, while an activity/survey indicator (ISM -> SPY) may need lead-lag impulse response plots and forecast evaluation charts. I need to anticipate this diversity in my chart template library.

Evan's **target-class-aware backtest parameters** table is critical: equity targets (15-35% vol) need different Y-axis scales than fixed income (2-18% vol) or crypto (50-80% vol). A drawdown chart scaled for SPY (-55% worst case) would look ridiculous for SHY (-5% worst case). My chart templates must be scale-adaptive.

**Key pressure for Evan at scale:** Producing interpretation_metadata.json for every pair, ensuring manifest files accompany every output, and maintaining consistency in direction/sign conventions across 73+ analyses. Any inconsistency in a manifest means I might invert a direction annotation.

### Research Ray

Ray's SOP now includes an **Event Timeline** section as a standard attachment to every research brief: date, event, relevance, and type (structural break / policy change / regime shift / crisis). This is my primary source for chart annotations.

The scaling concern: with 35 targets spanning equities, fixed income, commodities, and crypto, event timelines may need to be **target-class-specific**. The GFC event timeline is relevant for SPY, HYG, and TLT, but Bitcoin did not exist in 2008. A COVID timeline matters for all targets but its impact direction differs: COVID was bearish for SPY but bullish for TLT and gold. Ray's SOP requires each event entry to include "expected direction of impact on the variables" -- this is essential for multi-target annotations, but Ray will need to produce direction-aware event entries for each target class, not a single generic timeline.

Ray also validates Evan's `interpretation_metadata.json` against literature, flagging contradictions between empirical and theoretical expectations. This **direction-vs-theory contradiction flag** is important for my charts: if Evan's observed direction contradicts Ray's literature-based expectation, I may need a special visual marker (e.g., a warning icon or footnote) rather than a simple solid/dashed line.

Ray's **Portal Narrative** and **Storytelling Arc** deliverables are organized by Ace's 5-page structure. With 73+ pairs, will Ray produce one narrative per pair, or one overarching narrative for the entire multi-indicator framework? This affects how many separate chart sets I need to produce and whether dashboards comparing indicators need their own narrative context.

**Key pressure for Ray at scale:** Producing event timelines that are both comprehensive and target-class-aware, validating direction consistency across dozens of pairs, and providing narrative context that scales beyond one-at-a-time stories.

### AppDev Ace

Ace receives my Plotly JSON charts plus metadata sidecars and assembles them into the Streamlit portal. The handoff protocol established in R2 (JSON format, `_meta.json` sidecar, audience tier tagging) was designed for one indicator-target pair producing 8-12 charts. Scaling to 73+ pairs means:

1. **Chart volume explosion.** If each pair generates ~10 charts, that is 730+ chart files, 730+ metadata sidecars, and 730+ static fallbacks. File naming, directory organization, and manifest management become non-trivial engineering problems.

2. **Multi-pair comparison dashboards.** The Analysis Brief template (Section 10, Portal Specifications) now implies dashboards where the same indicator is compared across multiple targets. This is a new chart type I have not produced before -- it requires overlaying 7+ time-series (one per target) with different Y-axis scales, direction annotations per series, and "Differs From" callouts where the same indicator has opposite interpretations for different targets.

3. **Portal navigation at scale.** With 73+ pairs, the portal cannot have 5 pages per pair (that would be 365+ pages). Ace will need to design a hub-and-spoke architecture with index pages, drill-downs, and cross-pair comparison views. My chart metadata needs to support this -- specifically, the `portal_page` field in `_meta.json` needs to become a hierarchical path (e.g., `"portal_page": "credit_spreads/hy_ig/spy/evidence"`) rather than a flat page number.

4. **Interactive controls for multi-pair views.** On a dashboard comparing ISM PMI across SPY, QQQ, IWM, HYG, TLT, and BTC, what controls does the user need? Indicator selector? Target selector? Date range? Regime filter? These controls affect how I structure the Plotly figures (one figure with many traces vs. separate figures per target assembled by Ace into a grid).

**Key pressure for Ace at scale:** Portal architecture that handles 730+ charts across 73+ pairs without becoming a disorganized data dump. Navigation, search, comparison, and filtering all need to work coherently. My chart deliverables need to be structured to support this.

---

## 2. Where Our Handoffs Connect and Where Friction Could Arise

### Handoff Map (All Vera Connections)

| Source/Dest | Handoff | New Friction Risk at Scale |
|-------------|---------|---------------------------|
| Dana -> Vera | Data + data dictionary with display names | 31 indicators x 35 targets = display name coverage gaps; frequency alignment documentation gaps |
| Evan -> Vera | Model results + chart request + interpretation_metadata.json + manifests | 73+ interpretation_metadata.json files; direction consistency across pairs; chart request template adequacy for 5-dimension tournaments |
| Ray -> Vera | Event timeline + domain viz conventions | Target-class-specific timelines needed; direction-vs-theory contradiction visual encoding |
| Vera -> Alex | Charts + captions + annotation source tracking | Volume: 730+ charts need systematic review, not one-by-one inspection |
| Vera -> Ace | Plotly JSON + _meta.json + static fallbacks + handoff message | File naming with 73+ pairs; portal_page field needs hierarchy; multi-pair dashboards are a new chart type |

### Direction Annotation Visual Language -- Friction Points

My SOP defines four direction line styles:

| Direction | Line Style | Color Modifier |
|-----------|-----------|----------------|
| Pro-cyclical (indicator up -> target up) | Solid | Standard palette |
| Counter-cyclical (indicator up -> target down) | Dashed | Standard palette |
| Ambiguous | Dotted | Grey (#999999) |
| Conditional (regime-dependent) | Dash-dot | Standard palette |

**Friction 1: Same indicator, opposite directions on different targets.** HY-IG spread widening is counter-cyclical for SPY (bearish) but potentially pro-cyclical for TLT (flight to quality = bullish for treasuries). If I produce a multi-pair dashboard overlaying HY-IG -> SPY and HY-IG -> TLT, the SPY line is dashed and the TLT line is solid. Is this clear enough, or will users be confused by the mixed line styles on a single chart?

**Friction 2: Conditional direction within a single pair.** VIX -> SPY has a conditional relationship: low and stable VIX is bullish, but rapidly rising VIX is bearish. Evan's interpretation_metadata.json encodes this as `"expected_direction": "conditional"`, but the dash-dot line style does not communicate the regime-specific logic. I may need a more nuanced visual encoding for conditional directions -- perhaps color-coded segments (blue during calm regime, red during stress regime) rather than a uniform dash-dot pattern.

**Friction 3: Scale differences across target classes.** Charting equity (15-35% annualized vol), fixed income (2-18% vol), commodities (12-30% vol), and crypto (50-80% vol) on the same comparison dashboard requires either dual/multi Y-axes (violating my anti-pattern rule about dual axes) or normalized scales (z-scores, percentile ranks). The Analysis Brief must specify which normalization is preferred; otherwise, I will make a choice that may not match Evan's or Alex's expectations.

**Friction 4: Direction annotation handoff rules in team-coordination.md.** The current protocol (Section "Interpretation Annotation Handoffs") says:
- Evan outputs interpretation_metadata.json
- Ray validates against literature
- Vera renders direction indicators
- Ace implements "How to Read This" callout box

But it does not specify: (a) what happens when Ray flags a contradiction (does Evan update the metadata, or does Vera annotate the contradiction visually?), (b) whether Vera should wait for Ray's validation before charting (this would add a dependency that slows the pipeline), or (c) how Ace should handle the "Differs From" notes (does Vera produce these as chart annotations, or does Ace add them as Streamlit callout boxes?).

### Multi-Pair Comparison Dashboard -- New Handoff Type

Neither my SOP nor the team coordination protocol currently addresses **cross-pair comparison charts**. These are a new artifact type that does not fit the existing one-pair-at-a-time workflow. Examples:

- "Same indicator, multiple targets" dashboard: HY-IG spread vs. SPY, QQQ, IWM, HYG, TLT, GLD, BTC
- "Same target, multiple indicators" dashboard: SPY predicted by HY-IG, VIX/VIX3M, ISM PMI, 10Y-2Y spread, Initial Claims
- "Tournament winner comparison" table: Top strategy for each of the 73 pairs, sorted by OOS Sharpe

These dashboards require inputs from **multiple Analysis Briefs simultaneously**. I would need a meta-handoff that collects interpretation_metadata.json files across pairs, event timelines across target classes, and tournament results across all completed analyses. No current handoff template covers this aggregation.

---

## 3. Suggestions for Each Teammate's SOP

### For Dana's SOP

1. **Guarantee display name coverage for all 31 indicators and 35 targets.** Dana's data dictionary format includes a Display Name column, but there is no enforcement that it is populated for every variable. Add a quality gate: "Display Name field is mandatory for every variable in the data dictionary. If a display name cannot be determined, flag to Alex before delivery." Without this, I will inevitably receive a column named `i17_sofr_us3m` with no human-readable label.

2. **Add a display-name registry.** Centralize the mapping from canonical column names to display names in a single reference file (e.g., `data/display_name_registry.csv` with columns: `column_name`, `display_name`, `unit`, `axis_label`). This file becomes the single source of truth for all chart labels and prevents inconsistencies across multiple data deliveries. Dana maintains it; Vera and Ace consume it.

3. **Document frequency alignment method per derived series.** When delivering data that has been frequency-aligned (e.g., monthly ISM carried forward to daily), include the alignment method in the data dictionary's "Transformation" column. Example: "Level, LVCF from monthly" instead of just "Level." This affects how I label the axis and whether I add staleness annotations to the chart.

4. **Include sign convention explicitly for every derived indicator.** For HY-IG spread: "positive = HY wider than IG = more credit stress." For VIX/VIX3M: "ratio > 1 = term structure inversion = near-term fear elevated." These sign conventions should be in the data dictionary's Known Quirks or a new "Sign Convention" column. Without them, I risk flipping the visual encoding of stress vs. calm.

### For Evan's SOP

1. **Ensure interpretation_metadata.json is produced for every pair.** This file is my primary input for direction annotations. Evan's SOP describes it, but it is listed under the Chart Request Template section rather than as a mandatory quality gate deliverable. Move it to the Quality Gates checklist: "interpretation_metadata.json delivered alongside results (mandatory per pair)."

2. **Add chart type guidance to interpretation_metadata.json.** Currently the file has `direction`, `mechanism`, `confidence`, `supporting_evidence`, and `contradictions`. Add a `"recommended_charts"` field listing the chart types most appropriate for this pair's results. Example: `["regime_probability_timeline", "impulse_response", "tournament_heatmap", "equity_curve_comparison"]`. This is especially important at scale because different indicator types (Credit Spread vs. Volatility vs. Activity) warrant different chart portfolios, and I cannot infer this without econometric judgment.

3. **Specify target-class-specific Y-axis scaling guidance.** When Evan delivers equity curve or drawdown data for a fixed income target (TLT, LQD), the typical scale is very different from equities. The chart request template should include a "scale hint" field: `"y_range": [-20%, +30%]` or `"scale_type": "auto_by_target_class"`. Without this, I will produce equity-scaled charts for bond targets that waste visual real estate or compress the data into an unreadable band.

4. **Address the 5-dimension tournament visualization challenge.** With Signal x Threshold x Strategy x Lead Time x Lookback, the tournament results cannot be displayed in a simple 2D table. Evan should recommend the visualization approach: nested heatmaps? Parallel coordinates? Treemaps? Faceted bar charts by dimension? This is an analytical decision (which dimensions matter most for interpretation?) rather than a purely aesthetic one, so it should come from Evan.

5. **Manifest files for tournament results.** The tournament results CSV will be the largest and most complex artifact I consume. The `_manifest.json` must document: column semantics for all metric columns (is "sharpe" IS or OOS?), which rows are the tournament winners vs. full grid, and the sort order. If I chart the "top 10 strategies" from a CSV without knowing whether it is sorted by OOS Sharpe or IS Sharpe, the chart will be wrong.

### For Ray's SOP

1. **Produce target-class-specific event timelines.** A single "macro events" timeline is insufficient when targets span equities, bonds, commodities, and crypto. The impact direction of events differs by target class: Fed rate hike is bearish for TLT but potentially bullish for DXY. Ray should either produce separate timelines per target class or add a `"target_class_impact"` column to the event timeline: `{"equities": "bearish", "fixed_income": "bullish", "commodities": "neutral"}`. Without this, I cannot correctly annotate multi-target comparison dashboards.

2. **Add a "direction contradiction" deliverable format.** When Ray validates Evan's interpretation_metadata.json and finds a contradiction between empirical and theoretical expectations, the output should be a structured record (not just a flag in prose): `{"indicator": "vix_vix3m", "target": "spy", "empirical_direction": "counter_cyclical", "theoretical_direction": "conditional", "explanation": "Literature suggests regime-dependent effect that simple correlation misses"}`. I need this structure to render contradiction annotations consistently.

3. **Scale the event timeline to cover asset-class-specific events.** Credit market events (HY default waves, fallen angel episodes) matter for HYG and LQD but not for GLD. Crypto halving events matter for BTC but not for SPY. If Ray's standard template only covers macro/equity events, I will lack annotation material for non-equity targets. The SOP should ensure event coverage scales with the target universe.

4. **Clarify whether Ray validates direction before or after I chart.** The current workflow (team-coordination.md, Section "Interpretation Annotation Handoffs") implies Ray validates Evan's direction after Evan delivers. But if I start charting before Ray validates, I might render a direction that Ray subsequently overturns. The SOP should specify: "Vera may begin charting using Evan's interpretation_metadata.json. If Ray flags a contradiction, Vera produces a revised chart version." This at least makes the sequencing explicit.

### For Ace's SOP

1. **Redesign the portal_page field for multi-pair scale.** The current `_meta.json` schema uses `"portal_page": 2` (a flat integer). With 73+ pairs, the portal needs hierarchical navigation. Propose: `"portal_section": "credit_spreads"`, `"portal_pair": "hy_ig_spy"`, `"portal_page_type": "evidence"`. Ace and I need to agree on this schema before I start producing metadata at scale.

2. **Define multi-pair dashboard specifications.** Ace's SOP currently describes a 5-page structure per analysis. With the multi-indicator expansion, the portal needs cross-pair comparison pages (e.g., "All indicators for SPY," "HY-IG across all targets," "Tournament winners leaderboard"). Ace should specify: what chart types these pages need, what interactive controls they require (indicator dropdown, target dropdown, date range), and whether I produce these aggregation charts or Ace assembles them from individual pair charts.

3. **Clarify chart volume management.** With 730+ potential charts, Ace needs a chart manifest or index file that catalogs all available charts with their metadata. I can produce this as part of my deliverables: `output/chart_manifest.json` listing every chart file with its metadata summary. Ace uses this manifest to build navigation and search in the portal.

4. **Address Plotly performance with large datasets.** Some comparison dashboards may have 10+ time-series spanning 20+ years of daily data. Plotly figures with >100K data points can be slow to render in Streamlit. Ace's SOP should address: downsampling strategy (LTTB algorithm?), server-side rendering for heavy charts, or lazy loading. I need to know whether to pre-downsample for portal delivery or deliver full-resolution data.

### For Team Coordination Protocol

1. **Add direction annotation handoff rules with explicit sequencing.** The current "Interpretation Annotation Handoffs" section lists who does what but not when. Propose:
   - Step 1: Evan delivers interpretation_metadata.json alongside results
   - Step 2: Vera begins charting using Evan's metadata (no wait for Ray)
   - Step 3: Ray validates direction against literature and delivers validation result
   - Step 4: If Ray flags contradiction, Vera produces a chart revision (v2) with contradiction annotation
   - Step 5: Ace implements "Differs From" notes based on validated interpretation_metadata.json

2. **Add a cross-pair aggregation handoff type.** The current handoff templates are all per-pair. Add a new handoff type for multi-pair artifacts: chart manifests, tournament leaderboards, cross-pair comparison dashboards, and aggregated event timelines. Specify who produces these aggregations and who consumes them.

3. **Add chart versioning rules for 73+ pairs.** With potentially 730+ charts across multiple versioning rounds, the `_v{N}` suffix alone is insufficient. Add: pair-level versioning (`output/{indicator}_{target}/` directory per pair), a global chart manifest maintained by Vera, and a change log noting what changed in each version.

4. **Specify who produces "same indicator, multiple targets" comparison charts.** This is a cross-pair artifact. Does Vera produce it from aggregated data (requiring coordination with Dana for multi-target datasets), or does Ace assemble it from individual pair charts? The protocol needs to designate ownership.

5. **Add a "contradiction flow" protocol.** When Ray contradicts Evan's direction finding, the current protocol is silent on resolution. Propose: Ray notifies Evan and Vera simultaneously. Evan either updates interpretation_metadata.json or provides a written justification for the empirical finding. Vera annotates the chart with both the empirical and theoretical directions (e.g., a footnote: "Empirical: counter-cyclical (dashed). Theoretical expectation: conditional. See note.").

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

### Chart Templates for Different Target Classes

My SOP has one set of style defaults (figure size, DPI, font, palette) that was designed for equity analysis. With 5 target classes (Equity, Fixed Income, Commodity, FX, Crypto), I need:

1. **Target-class-specific Y-axis scaling presets.** Equity drawdown charts: Y-axis [-60%, 0%]. Fixed income drawdown: [-20%, 0%]. Crypto drawdown: [-90%, 0%]. These prevent charts with inappropriately scaled axes.

2. **Target-class-specific benchmark labeling.** The benchmark name changes per target class (SPY for equities, AGG for fixed income, asset-specific for commodities/crypto). My chart templates should parameterize the benchmark label, pulling it from the Analysis Brief.

3. **Target-class-specific annotation sets.** Recession shading is appropriate for equity and credit targets. Halving events are appropriate for crypto. OPEC decisions are appropriate for oil. My annotation library needs to be segmented by target class.

### Scaling the Direction Annotation Visual Language

The solid/dashed/dotted/dash-dot system works for individual pair charts. For multi-pair comparison dashboards with 7+ targets, the four line styles become hard to distinguish. Potential solutions to prototype:

- **Color + style encoding:** Use both line style (direction) and color (target identity) simultaneously. Risk: visual overload with >5 series.
- **Small multiples instead of overlay:** One mini-chart per target, each with its own direction annotation. Cleaner but uses more space.
- **Direction arrows in legend:** Instead of encoding direction in line style, use standard solid lines with direction arrows (up/down) in the legend entry. More accessible but less visually informative at a glance.
- **Tabular direction summary alongside chart:** A small table showing {target, direction, mechanism} next to the time-series plot. Separates the direction information from the visual encoding.

My SOP should document the decision: when overlay, when small multiples, based on series count and direction diversity.

### Handling Charts with 10+ Series

My anti-pattern list says "never use more than 6-7 colors in a single chart (use facets instead)." But multi-pair comparison dashboards might need 7+ targets on one chart. I need to formalize the escalation:

- 1-3 series: single panel, standard palette
- 4-6 series: single panel, extended colorblind-safe palette
- 7-10 series: faceted small multiples (one per series) with shared X-axis
- 10+ series: grouped facets (by target class) or interactive selector (Plotly dropdown)

### Chart Template Library

At scale, I cannot hand-craft each chart. I need a parameterized chart template library:

| Template | Input | Output | Parameterized By |
|----------|-------|--------|-----------------|
| Regime probability timeline | `prob_stress` column + event timeline | Time-series with regime shading | Target class (Y-axis scale), events (target-class-specific) |
| Tournament heatmap | Tournament results CSV | 2D heatmap (Signal x Threshold or similar) | Which 2 dimensions to display; metric (Sharpe/Sortino/MDD) |
| Equity curve comparison | Strategy equity curve + benchmark | Dual-line chart with drawdown panel | Benchmark name, Y-axis scale (target-class-dependent) |
| Impulse response | LP coefficients + CIs | Dot-and-band plot across horizons | Direction annotation, confidence level |
| Direction summary | Multiple interpretation_metadata.json files | Tabular/visual summary of directions | Indicator name, target list |
| KPI card data | Tournament winner metrics | Formatted numbers for Ace | Unit formatting (bps, %, ratio) |

My SOP should reference this library and specify which templates are mandatory per pair vs. produced only on request.

### File Naming with 73+ Pairs

My current naming convention: `{subject}_{chart_type}_{audience}_{date}_v{N}.{ext}`. With 73+ pairs, `subject` becomes ambiguous (is it the indicator, the target, or the pair?). Propose a structured convention:

```
output/{indicator_id}_{target_id}/{indicator_id}_{target_id}_{chart_type}_{audience}_{date}_v{N}.{ext}
```

Example:
```
output/hy_ig_spy/hy_ig_spy_regime_prob_narrative_20260315_v1.json
output/hy_ig_spy/hy_ig_spy_regime_prob_narrative_20260315_v1_meta.json
output/hy_ig_spy/hy_ig_spy_regime_prob_narrative_20260315_v1.png
```

Cross-pair charts go in a `_comparison/` directory:
```
output/_comparison/hy_ig_all_targets_equity_curve_exec_20260315_v1.json
```

### Plotly Performance at Scale

My SOP should add guidance on Plotly figure optimization for portal rendering:

- For daily data spanning 20+ years (5,000+ points per series): use `go.Scattergl` instead of `go.Scatter` for WebGL rendering
- For multi-series charts with >50K total data points: pre-downsample using the Largest Triangle Three Buckets (LTTB) algorithm
- For metadata-heavy figures: strip internal Plotly metadata not needed for rendering before JSON export
- Document maximum recommended data points per figure: ~100K for smooth Streamlit rendering

---

## 5. Key Concerns for the Multi-Indicator Expansion

### Chart Template Scaling

With ~10 charts per pair and 73 priority pairs, I need to produce ~730 charts. Hand-crafting is impossible. I need:
- A chart generation script that reads interpretation_metadata.json, tournament results, and the Analysis Brief, then calls parameterized chart templates
- A chart manifest (`output/chart_manifest.json`) that indexes all produced charts with their metadata
- A validation script that checks every chart's data against the upstream source (Defense 2 at scale)

### Direction Annotation Consistency Across Hundreds of Pairs

The direction annotation visual language (solid/dashed/dotted/dash-dot) must be consistent across all 730+ charts. This means:
- The line style is derived from interpretation_metadata.json, not hand-selected
- If Evan updates a direction (from ambiguous to counter-cyclical), every chart for that pair must be regenerated
- Cross-pair comparison charts must handle mixed directions (solid for some targets, dashed for others) without visual confusion

### Visual Language for Conditional and Ambiguous Directions

The `conditional` direction (dash-dot) is the least informative visual encoding. For pairs like VIX -> SPY where the relationship is regime-dependent, a single line style cannot capture "bullish when VIX is low, bearish when VIX spikes." I propose:
- For conditional pairs: use regime-colored line segments (blue in calm, red in stress) instead of dash-dot
- For ambiguous pairs: use grey dotted with a footnote "Direction determined empirically -- see interpretation notes"
- Add a `direction_visual_override` field to interpretation_metadata.json for cases where the default visual encoding is insufficient

### Dashboard Design for Comparing Same Indicator Across 7+ Targets

This is a new chart type with no precedent in the current pipeline. Design considerations:
- Y-axis normalization: z-score or percentile rank to make cross-target comparison meaningful
- Direction indicators per series: inline arrows or legend-embedded direction symbols
- "Differs From" callouts: when HY-IG is counter-cyclical for SPY but pro-cyclical for TLT, highlight this in a callout box within the chart
- Interactive target selector: let the user toggle targets on/off rather than showing all 7+ simultaneously

### File Naming and Organization with 73+ Pairs

The flat `output/` directory becomes unmanageable with 730+ files. Propose:
- Per-pair subdirectories: `output/{indicator_id}_{target_id}/`
- Cross-pair directory: `output/_comparison/`
- Chart manifest: `output/chart_manifest.json`
- This requires updates to my SOP, Ace's SOP, and the team coordination naming conventions

### Plotly Performance with Large Datasets

Daily data across 20+ years for 7+ targets on a single chart = 35,000+ data points. At this scale:
- Use WebGL rendering (`Scattergl`)
- Pre-downsample for portal delivery (keep full resolution for static PNG)
- Test Streamlit rendering performance before committing to all-Plotly delivery
- Consider server-side rendering for the heaviest charts

### Reconciliation at Scale

Defense 2 (numerical reconciliation) requires checking every displayed number against upstream sources. With 730+ charts, manual reconciliation is impossible. I need:
- An automated reconciliation script that loops through chart_manifest.json, loads each chart's JSON, extracts key displayed values, and compares against the tournament results CSV and interpretation_metadata.json
- Tolerance-based checks (within 0.02 for Sharpe ratios, within 1% for returns)
- A reconciliation report output that Alex can review at Gate 3

---

*This review reflects the visualization challenges of scaling from 1 pair to 73+. The core infrastructure (direction annotation protocol, Plotly handoff, metadata sidecar) is sound but was designed for single-pair workflow. Scaling requires: parameterized chart templates, hierarchical file organization, target-class-aware styling, cross-pair comparison chart types, and automated reconciliation. These are not cosmetic changes -- they are structural requirements for producing 730+ charts without quality degradation.*

-- Viz Vera, 2026-03-14

---

## Addendum: Disposition of Teammate Suggestions (Step 2)

### From Dana's Review (data-dana-review.md)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Use canonical column names from Data Series Catalog for data requests | **Accepted** | Added to Data-to-Viz handoff protocol |
| 2 | Add Display Name verification step to Data Ingestion Validation | **Accepted** | Added as step 5 in Data Ingestion Validation |
| 3 | Document how Vera handles multi-frequency overlays | **Accepted** | Added "Frequency Representation" section |
| 4 | Request Direction Convention from data dictionary | **Accepted** | Added as step 6 in Data Ingestion Validation |

### From Evan's Review (econ-evan-review-r3.md)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 9 | Conditional direction visual language needs more specificity | **Accepted** | Added "Conditional direction -- enhanced encoding" sub-section |
| 10 | Tournament results visualization template | **Accepted** | Added "Tournament Visualization Templates" table |
| 11 | Cross-pair numerical reconciliation | **Accepted** | Added to Quality Gates |

### From Ray's Review (research-ray-review.md)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Batch event timeline ingestion (CSV format) | **Accepted** | Updated Research-to-Viz pathway |
| 2 | Direction annotation per pair, not per indicator | **Accepted** | Added explicit note to Direction Annotation Visual Language |
| 3 | Indicator-type charting convention library | **Accepted** | Added "Indicator-Type Charting Conventions" table |
| 4 | Multi-pair dashboard annotations template | **Accepted** | Added "Comparison Dashboard Charts" section |

### From Ace's Review (appdev-ace-review.md)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Chart directory structure at scale | **Accepted** | Per-pair subdirectories under `output/` |
| 2 | Comparison dashboard chart specs | **Accepted** | Added ownership rule in "Comparison Dashboard Charts" |
| 3 | Direction annotation versioning (hash in metadata sidecar) | **Accepted** | Added `interpretation_metadata_version` field |
| 4 | Audience tag enforcement | **Accepted** | Reinforced in file naming convention |

### From My Own Review (Section 4)

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Target-class-specific chart templates | **Accepted** | Added "Target-Class-Specific Chart Defaults" table |
| 2 | Multi-series escalation rules | **Accepted** | Added escalation table |
| 3 | File naming hierarchy | **Accepted** | Updated file naming and directory conventions |
| 4 | Tournament visualization templates | **Accepted** | Added 5 standard templates |
| 5 | Plotly performance guidance | **Accepted** | Added "Plotly Performance Guidelines" |
| 6 | Chart registry for multi-pair | **Accepted** | Added `chart_registry.json` spec |
| 7 | Automated reconciliation script | **Accepted** | Added to Quality Gates |

All 18 suggestions from teammates were accepted. Each addressed a genuine gap for the multi-indicator expansion.
