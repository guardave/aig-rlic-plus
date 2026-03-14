# Cross-Review: Data Dana

## Date: 2026-03-14

**Author:** Data Dana (`data-dana`)
**Reviewed documents:**
1. Team Coordination Protocol (`docs/agent-sops/team-coordination.md`)
2. Data Agent SOP (`docs/agent-sops/data-agent-sop.md`)
3. Econometrics Agent SOP (`docs/agent-sops/econometrics-agent-sop.md`)
4. Research Agent SOP (`docs/agent-sops/research-agent-sop.md`)
5. Visualization Agent SOP (`docs/agent-sops/visualization-agent-sop.md`)
6. App Dev Agent SOP (`docs/agent-sops/appdev-agent-sop.md`)
7. Analysis Brief Template (`docs/analysis_brief_template.md`)

---

## 1. What I Learned About Each Teammate's Workflow and Pressures

### Econ Evan

Evan operates under the heaviest methodological burden on the team. His SOP mandates: hypothesis-driven model specification, robust standard errors by default (HC3 for cross-section, HAC for time-series), a full diagnostics battery (Jarque-Bera, Breusch-Pagan, Breusch-Godfrey, RESET, and now mandatory reverse-causality Local Projections per the Analysis Brief Section 11.2), sensitivity analysis with at least one alternative specification, and interpretation metadata JSON for every indicator-target pair.

**How my output affects Evan:**

- He cannot begin exploratory analysis until my dataset, data dictionary, and stationarity tests arrive. Any ambiguity in column names, units, or transformations stalls his entire pipeline.
- He depends on my stationarity results to determine method category selection (his Step 2.5 Rules A-D). If I report an indicator as I(1) when it is actually I(0), he may run cointegration tests unnecessarily or skip them when they are needed. The stakes of a stationarity mis-call cascade into wrong model classes.
- His new Category Selection Heuristic (Rules A-D) explicitly references indicator frequency (Rule B: monthly indicator vs. daily target). My frequency alignment choices directly affect which analysis categories Evan applies. If I carry forward a quarterly series to daily without clearly documenting the staleness, Evan may misinterpret the effective information frequency.
- The multi-indicator expansion means Evan must apply the tournament grid (up to 3,528 combinations per pair) across potentially 73 priority pairs. Every data quality issue I let through multiplies across hundreds of model runs.

**Key pressure:** Evan's computational budget is finite (default 10,000 players per Analysis Brief). Any time he spends debugging data issues directly reduces his capacity for genuine analysis.

### Research Ray

Ray provides the intellectual scaffolding that both Dana and Evan build upon. His two-stage delivery protocol (quick spec memo first, full research brief later) is designed to unblock parallel work, and I benefit from this significantly.

**What Ray needs from me:**

- Ray does not need datasets from me directly, but he does need feedback when his data source recommendations are impractical. His SOP (Section 4: Data Feasibility Check) now requires him to verify MCP stack availability before recommending a series, which was a suggestion from my previous review. However, the multi-indicator expansion introduces 31 indicators, at least 6 of which (I8 Portland Cement, I13 ABI, I25 Cass Freight, I27 Petroleum Inventory, I29 Electricity CPI, I30 Gold/Copper) have non-trivial sourcing challenges. Ray needs to know quickly when a recommendation hits a wall so he can suggest alternatives.

**Pressures Ray faces:**

- The Analysis Brief template now requires Ray to deliver: spec memo, full research brief, portal narrative, storytelling arc, event timeline, and glossary entries — all per indicator-target pair. At 73 priority pairs, the volume of narrative work is enormous. Ray needs Dana to close the data feasibility loop fast so he does not waste time writing narratives for analyses that are data-blocked.
- Ray's new requirement to validate `expected_direction` against literature for every pair (Analysis Brief Section 4) means he must produce interpretation context for 73 pairs, each potentially having a different direction for the same indicator against different targets (e.g., VIX/VIX3M is counter-cyclical for SPY but possibly pro-cyclical for TLT). This is a cross-check burden that requires clean, consistent indicator-target labeling from my pipelines.

### Viz Vera

Vera is the team's visual quality gate. Her SOP now includes a mandatory numerical reconciliation section (Quality Gates: "every key number displayed in a chart matches the upstream source within rounding tolerance") and a data ingestion validation protocol that requires her to run manifest assertions before charting.

**How my data quality affects Vera:**

- Vera needs Display Names from my data dictionary for axis labels and legends. If I deliver `ism_mfg_svc_ratio` without the Display Name "ISM Mfg/Svc PMI Ratio," she must guess or ask, which costs a round-trip.
- Her Direction Annotation Visual Language (solid = pro-cyclical, dashed = counter-cyclical, dotted = ambiguous, dash-dot = conditional) depends on `interpretation_metadata.json` from Evan, but the underlying data correctness — specifically sign conventions and unit labels — flows from my data dictionary. If I deliver a spread where "higher = tighter" but don't document the sign convention, Vera could invert the visual encoding.
- For multi-pair dashboards where the same indicator appears against multiple targets, Vera needs consistent canonical names across all my datasets. If I name the VIX/VIX3M ratio `vix_vix3m` in one dataset and `vix_term_struct` in another, Vera's join logic breaks.

**Key pressure:** Vera's SOP correctly prohibits invented annotations — every marker must have a documented source. My data dictionary is one of those sources. Incomplete metadata forces Vera to either block delivery or make assumptions, both of which are costly.

### AppDev Ace

Ace is the final integration point where errors from all upstream agents converge. His SOP explicitly calls this out: "Ace is the final integration point — errors from any upstream agent converge here."

**How my data refresh spec affects the portal:**

- Ace's caching strategy uses `@st.cache_data(ttl=...)` where TTL maps directly to my Refresh Freq metadata: daily series = TTL 86400, monthly = TTL 2592000. If I deliver a dataset without Refresh Freq populated, Ace must guess the TTL. Wrong TTL means either stale data displayed to users or unnecessary API hammering.
- The stable filename alias convention (`data/{subject}_{frequency}_latest.parquet`) is critical for Ace. If I change the dated filename on data refresh but forget to update the `_latest` alias, the portal breaks. With 31 indicators and potentially dozens of datasets, alias management becomes a genuine operations concern.
- Ace needs Display Notes (layperson-friendly Known Quirks) for tooltip text on the portal. This is distinct from the technical Known Quirks that Evan needs. I must produce both versions for every variable in portal-facing datasets.
- The Analysis Brief template (Section 10) now specifies portal page structure, direction annotations for "How to Read This" callout boxes, and KPI card definitions per pair. Ace reads the KPIs from `results/kpis.json`, but the underlying data quality that feeds those KPIs traces back to my datasets. Every wrong unit or misaligned date in my pipeline propagates through Evan's models into Ace's portal.

**Key pressure:** Ace has the least domain expertise to catch data errors. A wrong sign convention that Evan would catch immediately might sail right through Ace's integration. This makes my Defense 1 (Self-Describing Artifacts) obligation especially critical for Ace-facing deliveries.

---

## 2. Where Our Handoffs Connect and Where Friction Could Arise

### Complete Handoff Map — Dana's Perspective

**Incoming handoffs (what I receive):**

| Source | Deliverable | Template/Protocol | Multi-Indicator Friction Risk |
|--------|------------|-------------------|-------------------------------|
| Alex | Analysis Brief | `docs/analysis_brief_template.md` (Section 6) | 73 briefs = 73 data requirement tables to parse |
| Ray | Data source recommendations | Research brief "Recommended Data Sources" table | 31 indicators from 6+ MCP sources; availability risk on I8, I13, I25, I27, I29 |
| Evan | Mid-analysis data requests | Data Request Template in Evan's SOP | Up to 73 pairs x possible mid-analysis requests = volume explosion |
| Vera | Direct data requests | Data-to-Viz Handoff (my SOP) | Exploratory charts for 31 indicators = many parallel requests |
| Ace | Refresh spec requests | Data-to-AppDev Handoff (my SOP) | 31 indicators x different refresh frequencies = complex TTL mapping |

**Outgoing handoffs (what I deliver):**

| Recipient | Deliverable | Template/Protocol | Multi-Indicator Friction Risk |
|-----------|------------|-------------------|-------------------------------|
| Evan | Dataset + dictionary + stationarity + summary stats | Data-to-Econ Handoff | Column naming consistency across 73 datasets; stationarity results for 31 indicators |
| Vera | Dataset + dictionary with Display Names | Data-to-Viz Handoff | Display Name consistency for the same indicator across different pair datasets |
| Ace | Dataset at stable path + dictionary with Display Notes + refresh spec | Data-to-AppDev Handoff | 31+ stable `_latest` aliases to maintain; TTL per series |
| Alex | (indirect via quality gates) | Quality Gates checklist | Completeness across 73 pairs |

### NEW Friction Points from Multi-Indicator Expansion

**F1: Frequency alignment across 31 indicators with mixed native frequencies.**

The indicator universe spans 4 frequencies: daily (I17, I18, I19, I22, I23, I28, I30), weekly (I27), monthly (I1-I4, I6-I16, I20, I21, I24-I26, I29, I31, I32), and quarterly (I16). The Data Series Catalog Section 9 defines alignment rules (LVCF for downsampling, end-of-month for upsampling), but in practice:

- Quarterly I16 (Credit Card Default) carried forward across 3 months introduces significant staleness. Evan's models on daily targets will see the same I16 value for ~63 trading days. This must be flagged in every data dictionary that includes I16.
- Weekly I27 (Petroleum Inventory) carried forward to daily creates a step function. The "days since release" feature suggested in Section 9 is a good idea but is not currently in my pipeline output.
- Mixing daily I17 (SOFR-US3M) with monthly I1 (Industrial Production) in the same dataset requires either downsampling I17 to monthly or carrying I1 forward to daily. The choice depends on Evan's model — but Evan may not know what he wants until after he sees the data. This creates a chicken-and-egg problem.

**Mitigation:** Deliver multiple frequency views per indicator (daily-aligned, monthly-aligned) and let Evan choose. Document the alignment method in every data dictionary entry.

**F2: Derived series computation consistency.**

Six indicators are computed from component series: I17 (SOFR - TB3MS), I19 (BAMLH0A0HYM2 - BAMLC0A0CM), I22 (VIX / VIX3M), I30 (GC=F / HG=F), I31 (I2 / I3), I32 (NEWORDER YoY). The recipes are documented in Data Series Catalog Section 7.10, but:

- If component series have different trading calendars (e.g., GC=F trades extended hours while HG=F does not), the ratio computation may produce NaN on misaligned dates.
- ISM PMI data (I2, I3) is released on specific dates, not end-of-month. The ISM Mfg/Svc ratio (I31) must use the same observation date for both numerator and denominator. If I source I2 and I3 from different releases or with different lag conventions, the ratio is nonsensical.
- I32 (NEWORDER YoY) requires 12 months of history before the first valid observation. My data dictionary must document the effective start date (12 months after the raw NEWORDER start), not the raw start date.

**Mitigation:** Add a "Derived Series Computation Log" to every delivery, showing the formula, component sources, alignment method, and first valid observation date.

**F3: Canonical naming collisions at scale.**

With 31 indicators and 35 targets, the canonical naming system (`{indicator_id}_{target_id}_daily_{start}_{end}.parquet`) must be unique and collision-free. Current potential issues:

- I10a (HSN1F, SA) vs. I10b (HSN1FNSA, NSA) have different canonical names but the same indicator family. File names like `hsn1f_spy_daily_*.parquet` vs. `hsn1fnsa_spy_daily_*.parquet` are distinguishable but easy to confuse in file listings.
- The priority combinations catalog lists 73 pairs using 27 unique indicators — some indicators appear in 17 pairs (e.g., XLE has 17 pairs). If I name datasets per-pair, I produce up to 73 files. If I name per-indicator with all targets merged, I risk massive wide datasets. The naming convention must be clear about whether datasets are per-pair or per-indicator.

**Mitigation:** Adopt a strict per-pair naming convention: `{indicator_canonical}_{target_ticker}_daily_{start}_{end}.parquet` and document this in the team coordination protocol.

**F4: API rate limits at scale.**

Sourcing 31 indicators from 6 MCP servers simultaneously risks hitting rate limits, especially on:

- Yahoo Finance: VIX, VIX3M, SOX, CL=F, GC=F, HG=F all require separate API calls. A batch of 73 pairs requesting Yahoo data could trigger throttling.
- FRED: Most indicators are on FRED, but rapid-fire requests for 20+ series may exceed rate limits if not paced.
- ISM, Portland Cement Association, AIA, Cass, EIA: These are non-MCP sources requiring web scraping or manual download. They represent 5 of 31 indicators and are the most likely sourcing bottleneck.

**Mitigation:** Build a sourcing priority matrix: MCP-accessible series first (FRED, Yahoo, Alpha Vantage), non-MCP series second with explicit sourcing plan per indicator. Cache aggressively. Deliver partial datasets for available series so Evan can start while I source the harder ones.

**F5: Interpretation annotation dependency chain.**

The new Interpretation Annotation Handoff protocol (team coordination Section "Interpretation Annotation Handoffs") creates a four-agent dependency chain: Evan produces `interpretation_metadata.json` -> Ray validates direction -> Vera renders visual encoding -> Ace implements "How to Read This" callout. Dana is upstream of all of this: if my sign conventions are wrong (e.g., I deliver HY-IG spread where higher = tighter when it should be higher = wider), the entire interpretation chain is corrupted.

**Mitigation:** My data dictionary must include an explicit "Direction Convention" column stating what higher/lower values mean in economic terms. This is a Defense 1 obligation that becomes critical at scale.

---

## 3. Suggestions for Each Teammate's SOP

### For Evan's SOP

1. **Add a batch data request mechanism for multi-indicator work.** Evan's current Data Request Template is designed for a single analysis. When running 73 priority pairs, Evan needs a way to request data in batches: "Give me all indicators for target SPY" or "Give me indicator I22 for all 7 target tickers." Add a "Batch Data Request" variant that specifies a cross of indicators and targets rather than listing each pair individually. This saves both of us dozens of round-trips.

2. **Clarify how Evan handles mixed-frequency inputs.** Evan's Method Category Selection (Step 2.5, Rule B) triggers on frequency mismatch between indicator and target, but does not specify who is responsible for the frequency alignment — does Evan expect Dana to deliver data already aligned, or does he want to receive multiple frequencies and align himself? The current ambiguity causes rework. Recommendation: add a line in Step 3 (Data Request to Dana) specifying the desired alignment: "Deliver at [desired frequency]. If the indicator's native frequency differs, apply alignment rules from Data Series Catalog Section 9 and document in the data dictionary."

3. **Specify the format for `interpretation_metadata.json` more precisely.** The template in Evan's SOP (Chart Request Template section) shows `observed_direction` as `+1 | -1` but the Analysis Brief template (Section 11.4) shows it as `"pro_cyclical | counter_cyclical | ambiguous | conditional"`. These are inconsistent. Standardize to the string format from the Analysis Brief, since it carries more information and feeds directly into Vera's visual encoding and Ace's callout boxes.

4. **Document how tournament results reference source data.** Evan's tournament produces results CSVs, but there is no specification for how those CSVs reference back to the input dataset (e.g., which data version, which frequency alignment, which sample split). Add a `data_provenance` field to tournament output that records the input file hash and path. This supports Vera's and Ace's reconciliation checks.

### For Ray's SOP

1. **Add a "Data Availability Risk Matrix" section to the research brief template.** For the multi-indicator expansion, many indicators have non-trivial sourcing challenges (I8 Portland Cement = proprietary, I13 ABI = subscription/scrape, I25 Cass Freight = published but proprietary, I27 Petroleum Inventory = EIA weekly with special calendar, I29 Electricity CPI = derived from BLS sub-component). Ray's brief should flag these explicitly in a risk matrix so I can triage sourcing effort before starting. Format: `| Indicator | Sourcing Risk (Low/Medium/High) | Reason | Fallback |`.

2. **Coordinate indicator-target direction annotations across briefs.** When Ray validates `expected_direction` for the same indicator against different targets (e.g., I22 VIX/VIX3M → SPY vs. I22 VIX/VIX3M → XLE), the direction may differ. Ray's SOP does not currently require cross-referencing these across briefs. Add a "Cross-Pair Direction Consistency Check" to the Quality Gates: "For indicators appearing in multiple pairs, verify that direction annotations are internally consistent and document any target-specific direction differences."

3. **Provide data source recommendations in machine-readable format.** Ray's current recommendation format is a markdown table. For batch operations across 73 pairs, a machine-readable format (CSV or JSON) would allow me to automate the intake step. Add an option to deliver the "Recommended Data Sources" table as `data_sources_{topic}_{date}.csv` alongside the markdown version.

### For Vera's SOP

1. **Use canonical column names from the Data Series Catalog for data requests.** When Vera requests data from me, she should reference the canonical name from Section 7 of the Data Series Catalog (e.g., `ism_mfg_pmi`, not "ISM PMI" or "manufacturing PMI"). This eliminates ambiguity and lets me deliver exactly what she expects. Add to the Data-to-Viz handoff protocol: "All variable requests must use canonical names from `docs/data-series-catalog.md`, Section 7."

2. **Add a Display Name verification step to Data Ingestion Validation.** Vera's mandatory data validation on intake (per Defense 2) currently checks for manifest assertions and known-period behavior. Add: "Verify that Display Names are present in the data dictionary for all variables that will appear as axis labels or legend entries. If Display Names are missing, request them from Dana before proceeding — do not infer display names from column codes."

3. **Document how Vera handles multi-frequency overlays.** When Vera plots a daily target (SPY price) alongside a monthly indicator (ISM PMI), the visual representation of the carried-forward monthly data matters. Does she show it as a step function, a smooth interpolation, or point observations? This choice affects the reader's perception. Add a "Frequency Representation" section to the style defaults specifying the visual treatment for carried-forward data (recommendation: step function with visual indicator that it is a monthly observation, not daily).

4. **Request Direction Convention from data dictionary.** Vera's Direction Annotation Visual Language depends on knowing whether higher indicator values are bullish or bearish. This information should come from my data dictionary (not just Evan's `interpretation_metadata.json`), because Evan's output is posterior (after analysis) while my dictionary is prior (inherent to the data definition). Add to Vera's "Context Gathering" step (Section 2): "Check Dana's data dictionary for the Direction Convention column to understand the raw sign convention before applying Evan's interpretation overlay."

### For Ace's SOP

1. **Add a "Data Source Manifest" page or component to the portal.** For transparency and reproducibility, the portal should display the data provenance: which MCP server sourced each series, when the data was last refreshed, and the alignment method used. This can be a lightweight "Data Sources" section on the Methodology page. My data dictionary already contains Refresh Source and Refresh Freq columns; Ace should render them.

2. **Define a fallback strategy for when `_latest` aliases are stale.** With 31 indicators refreshing at different frequencies, some `_latest` files will inevitably become stale (e.g., a monthly indicator not yet updated this month). Ace's SOP should specify: display the last-refreshed timestamp on the portal, and if data is older than 2x its expected refresh frequency, show a warning banner. This requires my Refresh Freq metadata to be complete.

3. **Batch KPI loading for multi-pair dashboards.** The current `load_kpis()` function reads from `results/kpis.json`, which is a single file. For 73 priority pairs, KPIs will either be in one massive JSON (hard to parse) or in per-pair files (`results/kpis_{indicator}_{target}.json`). Ace's SOP should specify the expected format. Recommendation: one JSON file per pair, with a master index at `results/kpi_index.json` listing all available pair KPIs.

4. **Add a "How to Read This" component template that consumes `interpretation_metadata.json`.** The team coordination protocol specifies that Ace implements the "How to Read This" callout box, but Ace's SOP does not describe the component's contract — what JSON fields it expects, how it handles `ambiguous` vs. `conditional` directions, and what fallback text appears if the metadata is missing. This component will be reused across all 73 pair pages, so its contract must be explicit.

### For Team Coordination Protocol

1. **Add a "Batch Operations" section for multi-indicator work.** The current protocol assumes a single-pair workflow (one Analysis Brief -> one data request -> one model -> one chart set -> one portal page). The multi-indicator expansion requires batch equivalents: batch briefs, batch data requests, batch model runs, batch chart generation. The protocol should define how these batch operations are coordinated: sequential (one pair at a time) or parallel (multiple pairs simultaneously, grouped by indicator or by target).

2. **Define a canonical data versioning strategy.** The naming convention `{subject}_{freq}_{start}_{end}.parquet` includes the date range but not the extraction date. If I re-pull the same series two weeks later and FRED has revised the data (vintage issue), the file name is identical but the contents differ. Add an extraction date or version hash to the naming convention for datasets that may be subject to revision. Recommendation: `{subject}_{freq}_{start}_{end}_v{YYYYMMDD}.parquet`.

3. **Add an "Indicator Availability Status Board."** For the multi-indicator expansion, the team needs a shared view of which indicators are sourceable, which are blocked, and which have known data quality issues. Add a section to the team coordination protocol (or a separate `docs/indicator_status_board.md`) that Dana maintains with: `| Indicator ID | Canonical Name | Status (Available / Blocked / Degraded) | Source | Notes |`. This prevents other agents from planning work around indicators that Dana cannot source.

4. **Define the Analysis Brief acknowledgment protocol for batch briefs.** The current protocol requires each agent to acknowledge each brief individually. For 73 briefs, this is 73 x 5 = 365 acknowledgment messages. Define a batch acknowledgment format: "I have reviewed Analysis Briefs for pairs #1-#21 (all SPY pairs). Domain-specific concerns: [list]. Blockers: [list]."

5. **Add a "Cross-Pair Consistency Gate" between Gate 2 and Gate 3.** Before Vera starts charting results from multiple pairs, there should be a consistency check: are all datasets using the same sample period? Are canonical names consistent across pairs? Are sign conventions consistent for the same indicator across different targets? This gate is new — it does not exist in the single-pair workflow — and it is critical for preventing subtle inconsistencies from propagating into the portal.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

Reading the other SOPs and the Analysis Brief template revealed several gaps in my own SOP:

1. **Missing: Direction Convention in the data dictionary.** My current data dictionary schema includes Column Name, Display Name, Description, Source, Series ID, Unit, Transformation, Seasonal Adj., Known Quirks, Display Note, Refresh Freq., and Refresh Source. But it does not include a "Direction Convention" field documenting what higher/lower values mean economically (e.g., "Higher = wider spreads = more stressed"). This is a Defense 1 gap. Evan's interpretation and Vera's visual encoding depend on this. **Action:** Add a `Direction Convention` column to the data dictionary template.

2. **Missing: Effective Start Date for derived series.** My SOP documents that derived series should have their computation recipes in the data dictionary. But it does not require me to document the effective start date (the first date where the derived value is valid). For I32 (NEWORDER YoY), the raw NEWORDER series might start in 1992, but the YoY transform is only valid from 1993. If I report the sample period as starting in 1992, Evan's models will use NaN values for the first 12 months. **Action:** Add an `Effective Start` column to the data dictionary for all transformed/derived series.

3. **Missing: Batch delivery protocol.** My SOP describes delivery per-dataset. For the multi-indicator expansion, I may need to deliver 20+ datasets in a single handoff. There is no "batch delivery manifest" format in my SOP. **Action:** Add a "Batch Delivery" handoff variant that includes a master manifest listing all delivered files, their status (complete / partial), and per-file notes.

4. **Missing: Cross-dataset consistency checks.** My Quality Gates check individual datasets (monotonic index, no duplicates, stationarity). They do not check cross-dataset consistency (same indicator uses same canonical name across different pair datasets, same sample period boundaries, same unit conventions). **Action:** Add a "Cross-Dataset Consistency" quality gate for batch deliveries: verify canonical names, date ranges, and units are consistent across all datasets in the batch.

5. **Missing: Days-since-release feature.** The Data Series Catalog (Section 9) suggests including a "days-since-release" feature for carried-forward series to capture staleness. My SOP does not mention this. For quarterly I16 carried forward to monthly (3 months of staleness) or weekly I27 carried forward to daily, this feature could be valuable for Evan's models. **Action:** Add an optional `days_since_release` column for all carry-forward aligned series, and document it in the data dictionary.

6. **Insufficient: Handling of non-MCP sources.** My SOP lists MCP sources in priority order (FRED -> Yahoo -> Alpha Vantage -> Financial Datasets -> Web scraping -> Manual). But 5 of 31 indicators (I8, I13, I25, I27 partially, I29) require non-MCP sourcing (web scraping, proprietary databases, BLS sub-components). My SOP does not document the scraping/manual process for these. **Action:** Add a "Non-MCP Sourcing Protocol" subsection that defines: how to document the source URL, how to validate scraped data, how to flag proprietary/subscription sources to Alex, and when to propose a proxy variable instead.

7. **Missing: Stable alias management process.** My SOP mentions the `_latest` alias convention but does not describe the process for maintaining 31+ aliases when datasets are refreshed. **Action:** Add a "Stable Alias Maintenance" checklist: when refreshing a dataset, (1) save the new dated file, (2) update the `_latest` symlink/copy, (3) verify the alias points to the new file, (4) notify Ace if the alias was updated. Consider a script that automates steps 2-3.

---

## 5. Key Concerns for the Multi-Indicator Expansion

### 5.1 Scale: From 1 Pair to 73 Priority Pairs

The HY-IG x SPY pipeline was a single indicator-target pair. The multi-indicator expansion scales to 73 priority pairs (27 unique indicators x 7 targets, with varying coverage). From a data perspective, the scaling challenges are:

| Dimension | Single Pair | Multi-Indicator | Scale Factor |
|-----------|------------|-----------------|--------------|
| Indicators | 1 (HY-IG) | 31 (27 unique in priority set) | 31x |
| Targets | 1 (SPY) | 35 (7 in priority set) | 35x |
| Priority pairs | 1 | 73 | 73x |
| Datasets to deliver | 1-2 | 73+ (per-pair) or 31+ (per-indicator) | 30-70x |
| Data dictionary entries | ~5-10 | 200+ | 20-40x |
| Stationarity tests | 2-3 | 60+ (31 indicators x 2 tests each) | 20x |
| Stable `_latest` aliases | 1 | 31+ | 31x |
| MCP API calls | ~5 | 100+ | 20x |
| Frequency alignment decisions | 1 | 31 (one per indicator) | 31x |

### 5.2 Data Availability Triage

Not all 31 indicators are equally sourceable. My initial assessment:

| Risk Tier | Indicators | Count | Issue |
|-----------|-----------|-------|-------|
| **Low** (FRED/Yahoo, confirmed) | I1, I2 (proxy via FRED), I3 (proxy), I4, I6, I7, I9, I10a, I10b, I11, I12, I14, I15, I16, I17, I18, I19, I20, I21, I22, I23, I24, I26, I28, I30 | 25 | Standard MCP sourcing |
| **Medium** (non-standard but feasible) | I27, I29, I32 | 3 | EIA weekly format, BLS sub-component derivation, simple YoY computation |
| **High** (proprietary/scraping required) | I8, I13, I25 | 3 | Portland Cement Assoc. (proprietary), AIA Architecture Billings (subscription), Cass Freight (published but proprietary) |

The 3 high-risk indicators (I8, I13, I25) appear in 3, 1, and 2 priority pairs respectively (6 pairs total). If these cannot be sourced, 6 of 73 priority pairs are blocked. I should flag this to Alex immediately and propose proxy variables.

### 5.3 Frequency Heterogeneity

The 31 indicators span 4 native frequencies:

| Native Frequency | Indicators | Count |
|-----------------|-----------|-------|
| Daily | I17, I18, I19, I22, I23, I28, I30 | 7 |
| Weekly | I27 | 1 |
| Monthly | I1, I2, I3, I4, I6, I7, I8, I9, I10a, I10b, I11, I12, I13, I14, I15, I20, I21, I24, I25, I26, I29, I31, I32 | 23 |
| Quarterly | I16 | 1 |

All targets are daily (equities, ETFs). This means 24 of 31 indicators require frequency alignment (carry-forward or interpolation) to merge with daily target returns. The alignment method directly affects model results: LVCF creates step functions that may distort correlation estimates; interpolation introduces false smoothness. The choice must be documented and Evan must be aware of it.

### 5.4 Derived Series Consistency

Six indicators are computed from components. The consistency risk is that if I source the components on different dates, with different revision vintages, or from different providers, the derived series may not match published reference values. For each derived indicator:

| Derived Indicator | Components | Consistency Risk |
|-------------------|-----------|-----------------|
| I17 SOFR-US3M | SOFR, TB3MS | Different publication calendars; TB3MS may lag SOFR by 1 day |
| I19 HY-IG OAS | BAMLH0A0HYM2, BAMLC0A0CM | Both from FRED/ICE BofA; aligned by construction |
| I22 VIX/VIX3M | ^VIX, ^VIX3M | Both from Yahoo/CBOE; same trading calendar; low risk |
| I30 Gold/Copper | GC=F, HG=F | Different trading sessions; GC=F trades nearly 23 hours, HG=F has narrower window. Date alignment needed |
| I31 ISM Mfg/Svc Ratio | I2, I3 | Same release schedule (ISM); must use same reporting month |
| I32 NEWORDER YoY | I26 (NEWORDER) | Single source; YoY computation introduces 12-month lead time |

### 5.5 Cross-Check Infrastructure

The Analysis Brief template (Section 11.3) mandates reconciliation checkpoints at every handoff: row counts, date ranges, NaN counts, column names, reproducibility. At 73 pairs, manual reconciliation is infeasible. I should build a reusable reconciliation script that:

1. Validates each delivered dataset against its data dictionary (all columns present, types correct, no unexpected NaNs).
2. Compares derived series against known reference values for at least one date per indicator (e.g., HY-IG OAS during GFC should exceed 800 bps).
3. Checks cross-dataset consistency (same indicator has same canonical name, unit, and direction convention across all pair datasets).
4. Produces a machine-readable reconciliation report that Evan and Vera can run on receipt.

This script should be part of my standard delivery, not an afterthought.

### 5.6 Portal Data Refresh at Scale

When the portal displays live signals for 73 pairs, the refresh complexity is significant:

- 7 daily-frequency indicators need daily refreshes.
- 23 monthly indicators need monthly refreshes (but on different release schedules — ISM releases on the 1st business day, FRED data on various dates).
- 1 quarterly indicator (I16) refreshes quarterly.
- 1 weekly indicator (I27) refreshes weekly.

Each refresh must: (1) pull new data, (2) recompute derived series, (3) update the dated file, (4) update the `_latest` alias, (5) rerun the reconciliation script. For 31 indicators, this is an operational burden that needs automation. I should propose a `scripts/data_refresh.py` pipeline that handles all refresh logic and is triggered on a schedule.

---

*This review reflects a thorough reading of all teammate SOPs, the team coordination protocol, and the Analysis Brief template. Every suggestion is grounded in specific SOP sections and oriented toward the practical challenges of scaling from the single HY-IG x SPY analysis to the full multi-indicator framework. The SOPs are well-structured — these are refinements for scale, not fundamental redesigns.*

---

## Addendum: SOP Self-Update Disposition (Step 2)

**Date:** 2026-03-14

After reading all 4 teammates' cross-reviews, I incorporated the following suggestions into `docs/agent-sops/data-agent-sop.md`:

### Accepted and Incorporated

| Source | Suggestion | What I Changed |
|--------|-----------|----------------|
| **Evan #1** | Add frequency alignment guidance by model class | Added lookup table (OLS/VAR/MIDAS/Regime/Rolling) to Validate section |
| **Evan #2** | Derived series computation verification against known values | Added verification requirement to Validate section |
| **Evan #3** | Batch delivery option (master dataset per target) | Added full "Batch Operations for Multi-Indicator Work" section with batch manifest, shared indicator deduplication |
| **Evan #4** | Stable `_latest` alias for model-consumed data too | Extended alias convention to include econometrics agent, not just App Dev |
| **Vera #1** | Guarantee display name coverage for all indicators/targets | Made Display Name mandatory in quality gates with explicit escalation if undetermined |
| **Vera #2** | Display-name registry (`data/display_name_registry.csv`) | Added registry requirement and quality gate to keep it updated |
| **Vera #3** | Document frequency alignment method per derived series in Transformation column | Added explicit guidance: "Level, LVCF from monthly" not just "Level" |
| **Vera #4** | Sign convention explicitly for every derived indicator | Incorporated as new mandatory "Direction Convention" column in data dictionary |
| **Ray #1** | Batch data availability pre-check | Added "Batch Data Availability Pre-Check" subsection with Indicator Availability Status Board |
| **Ray #2** | Exotic indicator sourcing playbook (subscription-gated decision tree) | Added full "Non-MCP Sourcing Protocol" section with decision tree |
| **Ray #3** | Frequency alignment documentation at scale | Covered by the new alignment guidance table and batch documentation requirements |
| **Ace #1** | Data manifest at scale (`data/manifest.json`) | Added manifest specification with JSON schema example |
| **Ace #2** | Mixed-frequency TTL guidance | Added to Data-to-AppDev Handoff "Special considerations" |
| **Ace #3** | Benchmark data inclusion in pair datasets | Added requirement that every pair dataset includes benchmark returns |
| **Ace #4** | Symlink vs. copy for `_latest` | Noted in alias management process; chose to keep copy-based approach for portability (symlinks break on some platforms) but documented the tradeoff |
| **Self #1** | Direction Convention column in data dictionary | Added as mandatory field |
| **Self #2** | Effective Start Date for derived series | Added as mandatory field |
| **Self #3** | Batch delivery protocol | Added full batch delivery section with manifest template |
| **Self #4** | Cross-dataset consistency checks | Added as mandatory quality gate for batch deliveries |
| **Self #5** | Days-since-release feature for carry-forward series | Added as optional column with documentation requirement |
| **Self #6** | Non-MCP sourcing protocol | Added full section with decision tree |
| **Self #7** | Stable alias management process | Added 5-step maintenance checklist |

### Deferred (Not Rejected, But Not Yet Incorporated)

| Source | Suggestion | Reason for Deferral |
|--------|-----------|-------------------|
| **Ace #4** | Switch to OS symlinks instead of file copies | Symlinks break on Windows and some CI/CD platforms. Will revisit if storage becomes a constraint at 73+ aliases. |
| **Self (Section 5.6)** | Automated `scripts/data_refresh.py` pipeline | This is an implementation task, not an SOP change. Will build when portal enters production refresh mode. |

### Not Applicable (Suggestions Directed Elsewhere)

Suggestions from my review directed at Evan, Ray, Vera, Ace, and the Team Coordination Protocol are for those agents/documents to evaluate — not for me to implement in my own SOP.
