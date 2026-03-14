# Cross-Review: AppDev Ace

## Date: 2026-03-14

**Agent:** appdev-ace
**Context:** New agent onboarding cross-review per team-coordination.md, Section "New Agent Onboarding Protocol." This review builds on the R2 review (2026-02-28) and specifically addresses the multi-indicator expansion framework (31 indicators x 35 targets = up to 1,085 pairs, with ~73 priority combinations).

---

## 1. What I Learned About Each Teammate's Workflow and Pressures

### Data Dana

**Stable path alias (`_latest`) at scale.** Dana's convention of maintaining a `_latest` alias alongside the dated filename (e.g., `data/hy_ig_spy_daily_latest.parquet` -> `data/hy_ig_spy_daily_20000101_20251231.parquet`) is elegant for one or two analyses but raises questions at scale:

- With 73 priority pairs, the `data/` directory would contain 73 dated files plus 73 `_latest` aliases -- 146 entries before accounting for multiple frequencies or partial deliveries.
- The alias is currently a file copy, not a symlink. If Dana refreshes data, she overwrites the `_latest` copy. There is no manifest that maps alias -> dated file, so if the dated file changes name on refresh (new end date), I cannot programmatically discover which dated file backs the alias without re-reading Dana's handoff message.
- **Cache TTL across refresh frequencies:** The data dictionary includes `Refresh Freq.` and `Refresh Source` per variable, and Dana's SOP maps these to recommended TTL values (daily = 86400, monthly = 2592000). But a single dataset for a pair may contain variables with mixed refresh frequencies (e.g., daily market data + monthly ISM). The TTL question becomes: do I cache the whole parquet with the fastest TTL (daily), or split the data load into fast-refresh and slow-refresh subsets? Neither Dana's SOP nor mine addresses this.

**What I need from Dana at scale:**
1. A machine-readable **data manifest** (`data/manifest.json`) listing every `_latest` alias, its backing dated file, refresh cadence, and last-updated timestamp. This replaces hunting through individual handoff messages.
2. Guidance on **mixed-frequency TTL** -- does she deliver one file per pair with a single recommended TTL, or split fast/slow refresh series?
3. A clear answer on whether `_latest` aliases are file copies or symlinks.

### Econ Evan

**Expanded output surface.** The R2 review noted Evan had no formal Econ-to-AppDev handoff template. Since then, his SOP now includes the App Dev Handoff Template (Section "App Dev Handoff Template"), which is a significant improvement. Key new outputs I consume:

1. **5D Tournament Design:** The tournament now has 5 dimensions (Signal x Threshold x Strategy x Lead Time x Lookback = up to 3,528 combinations per pair). This means tournament results CSVs will be much larger, and the portal needs performant filtering. I cannot load all 3,528 rows into st.dataframe without pagination or pre-aggregation for 73 pairs.

2. **`interpretation_metadata.json`:** New mandatory output per pair containing `direction`, `mechanism`, `confidence`, `observed_direction`, `supporting_evidence`, `contradictions`. This is the primary data source for the "How to Read This" callout box and "Differs From" notes. The schema is well-defined, which is good. My concern: the file is per-pair, so I need 73 of these, and I must cross-reference them to detect when the same indicator has opposite observed directions for different targets.

3. **Target-class-aware backtest parameters:** Different benchmarks, transaction costs, calendars, and Sharpe validity thresholds per target class. This means the Strategy page cannot hardcode "SPY buy-and-hold" as the benchmark -- it must read the benchmark from the Analysis Brief or Evan's handoff. The App Dev Handoff Template includes a `Benchmark` field, which covers this.

4. **KPI loading from `results/kpis.json`:** My SOP mandates loading KPIs from JSON, never hardcoded. Evan's App Dev Handoff Template includes a KPI Values table. The question is: does Evan write `kpis.json` directly, or do I construct it from his handoff? Currently the answer seems to be that Evan delivers the table and I construct the JSON for portal consumption. This should be clarified -- if Evan writes the JSON directly, it is one less transformation step and one less error surface.

**What I need from Evan at scale:**
1. Clarity on whether `kpis.json` is Evan's deliverable or mine to construct from his handoff table.
2. Tournament results in a format that supports efficient filtering (pre-aggregated summaries + detail CSVs, not one massive file).
3. A convention for `interpretation_metadata.json` file naming per pair (e.g., `results/interpretation_metadata_{indicator_id}_{target_id}.json`).

### Research Ray

**Portal narrative scaling.** Ray's SOP now includes a dedicated Portal Narrative deliverable (Section "Portal Narrative Deliverable") structured by portal page (Hook, Story, Evidence, Strategy, Method, Glossary). This is a major improvement over the R2 review. However, at scale:

- **73 narratives are not feasible.** Writing a full 5-page portal narrative for each of 73 priority pairs would consume enormous research bandwidth. Ray would need months of narrative work, and the resulting portal would have 73 x 5 = 365 pages of prose.
- **Thematic grouping is necessary.** Many pairs share the same indicator (e.g., VIX/VIX3M analyzed against SPY, QQQ, TLT, HYG). The narrative for "what VIX/VIX3M measures and why it matters" is the same across all targets -- only the direction and mechanism differ. Ray should write one narrative per indicator (31 narratives), with per-target addenda that cover direction-specific interpretation and mechanism differences.
- **Glossary deduplication.** If each narrative has its own glossary, the same terms ("OAS," "Sharpe ratio," "regime") will be defined 73 times. The portal should have a single global glossary, with Ray maintaining one canonical definition per term.

**What I need from Ray at scale:**
1. **One narrative per indicator** (not per pair) covering what the indicator measures, economic significance, and historical context.
2. **Per-target addenda** covering direction, mechanism, and how interpretation differs from other targets of the same indicator.
3. **A single canonical glossary** (`docs/portal_glossary.md`) maintained across all analyses.
4. **Storytelling arc at the portfolio level**, not just per pair. If a user lands on the portal, what is the overarching narrative that ties 73 analyses together?

### Viz Vera

**Plotly JSON + metadata sidecar at scale.** Vera's SOP now includes a complete Viz-to-App handoff template (Section "App Dev Handoff (Viz -> Ace)") with a chart metadata sidecar schema and Plotly export standard. This is excellent. At scale:

- **Chart volume.** If each pair produces ~6-8 charts (exploratory, regime, equity curve, drawdown, signal, diagnostics, coefficient, sensitivity), 73 pairs means ~440-580 charts in `output/charts/`. The current flat directory structure (`output/charts/plotly/`, `output/charts/png/`) will become unmanageable. I need either per-pair subdirectories or a chart registry.
- **Metadata sidecar per chart.** Each chart gets a `_meta.json` with `chart_id`, `caption`, `source`, `audience_tier`, `portal_page`, `interactive_controls`, `data_source_path`, `static_fallback_identical`. With ~500 sidecars, I need a programmatic way to discover and load them -- not manual file hunting. A chart registry (JSON manifest of all chart IDs with their metadata paths) would solve this.
- **Direction annotation rendering.** Vera's SOP defines a Direction Annotation Visual Language (solid = pro-cyclical, dashed = counter-cyclical, dotted = ambiguous, dash-dot = conditional) with specific label patterns ("Higher {indicator} -> Higher {target}"). This is well-specified. My concern is consistency: if Vera renders direction in the chart itself, and I render it in a "How to Read This" callout box, do they always agree? Both pull from `interpretation_metadata.json`, so as long as both reference the same file, they should stay synchronized. But if Vera renders at chart-creation time and I render at page-load time, temporal drift is possible if the metadata is updated between chart production and portal assembly.
- **Multi-pair comparison dashboards.** Vera's SOP includes guidance for multi-pair dashboards ("Differs From" annotations, inline direction arrows). But her current chart-level handoff is per-chart, not per-dashboard. If I need a comparison dashboard showing the same indicator across 5 targets, I need either (a) a single composite Plotly figure from Vera, or (b) the raw data to construct the comparison myself. Neither pathway is currently specified.

**What I need from Vera at scale:**
1. **Per-pair subdirectories** under `output/charts/` or a **chart registry** (`output/charts/chart_registry.json`) mapping chart IDs to file paths and metadata.
2. **Composite chart specs for comparison dashboards** -- when the same indicator appears across multiple targets, specify whether Vera delivers a single combined chart or I assemble side-by-side panels.
3. **Temporal consistency guarantee** -- confirm that chart annotations and my callout boxes reference the same version of `interpretation_metadata.json`.

---

## 2. Where Our Handoffs Connect and Where Friction Could Arise

### Handoff Map (All Inbound to Ace)

```
Dana ──[data/_latest aliases, data dict, refresh specs]──> Ace
Evan ──[kpis.json/table, tournament CSV, interpretation_metadata.json,
        App Dev Handoff Template, strategy rules, backtest results]──> Ace
Ray  ──[portal narrative, storytelling arc, event timeline, glossary]──> Ace
Vera ──[Plotly JSON + _meta.json sidecars, static fallbacks,
        handoff message]──> Ace
```

### NEW Friction Points (Multi-Indicator Expansion)

#### F1: Data-Driven Page Configuration from Analysis Brief

The Analysis Brief template (Section 10, "Portal Specifications") contains fields that directly drive portal page configuration: `page_title`, `audience`, `direction_annotation`, KPI definitions, and page structure. Currently I hardcode these in page source files (e.g., `1_hy_ig_story.py` has HY-IG-specific titles and text). At scale with 73 pairs, I cannot maintain 73 x 4 = 292 page source files.

**Required change:** A `config/` directory with one JSON config per pair (or a single registry), each containing the Analysis Brief's Section 10 fields. Portal pages become templates that read from config, not hardcoded scripts.

**Friction risk:** Who writes the config JSON -- Alex (from the Analysis Brief), Evan (from model results), or me (by extracting from the Brief)? Currently undefined.

#### F2: "How to Read This" Callout Boxes

The team coordination protocol (Section "Interpretation Annotation Handoffs") assigns me responsibility for implementing "How to Read This" callout boxes on each pair's page. The data source is Evan's `interpretation_metadata.json`. The Analysis Brief's `direction_annotation` field provides the prior text.

**Friction risk:** The callout must synthesize two sources -- the Brief's expected direction (the prior) and Evan's observed direction (the empirical finding). If they disagree, the callout must note this. Currently no template exists for "expected said X, we found Y" language. This needs a Streamlit component template and agreement on who writes the discrepancy text (Evan in his metadata? Ray in narrative? Me?).

#### F3: "Differs From" Notes Across Targets

When the same indicator has opposite interpretations for different targets on the same dashboard (e.g., VIX/VIX3M rising is bearish for SPY but potentially bullish for TLT), I must show "Differs From" notes. This requires cross-pair comparison at runtime, not just per-pair metadata.

**Friction risk:** Each pair's `interpretation_metadata.json` is self-contained. To generate "Differs From" notes, I must load metadata for ALL pairs sharing the same indicator, compare `observed_direction` values, and generate the comparison text. No one currently owns the cross-pair comparison logic. This is naturally my responsibility, but I need a naming convention that makes it trivial to find all metadata files for a given indicator.

**Suggested convention:** `results/{indicator_id}/interpretation_metadata_{indicator_id}_{target_id}.json` -- grouped by indicator directory rather than flat in `results/`.

#### F4: KPI Loading from kpis.json

My SOP mandates KPIs from `results/kpis.json`. Evan's App Dev Handoff Template includes a KPI Values table. At scale, with 73 pairs, either:

- (a) There is one `kpis.json` per pair: `results/{indicator_id}_{target_id}/kpis.json` -- 73 files, each loaded when the user navigates to that pair's page.
- (b) There is one consolidated `kpis.json` with a nested structure keyed by pair ID.

Option (b) is more efficient for portal-level dashboards (e.g., "show all pairs' OOS Sharpe ratios on one page"). Neither Evan's SOP nor mine specifies the convention.

#### F5: Target-Class-Aware Benchmark Display

The Strategy page must display the correct benchmark per target class (SPY for equities, AGG for fixed income, self for commodities, HODL for crypto). The Analysis Brief specifies the benchmark in Section 8.3. Evan's App Dev Handoff Template includes it. At scale, this means each pair's strategy page dynamically selects the benchmark series. The data for the benchmark must be in the pair's dataset or loadable separately.

**Friction risk:** Dana may not include benchmark data in every pair's dataset. If the benchmark is SPY, it might be in one pair's data but not another's (e.g., a TLT analysis might not include SPY returns). I need either: (a) a universal benchmark dataset separately, or (b) confirmation that every pair's dataset includes the benchmark series for that target class.

#### F6: Multi-Pair Comparison Dashboards

The portal needs a way to compare results across pairs. Example views:

- "All indicators predicting SPY" -- filter by target, show all indicator-target pairs
- "HY-IG OAS across all targets" -- filter by indicator, show direction differences
- "Top 10 tournament winners across all pairs" -- leaderboard

None of these views are covered by the current per-pair page structure. They require either:
- New portal pages that aggregate across pairs
- A master results registry with all pairs' KPIs, tournament winners, and direction metadata

Neither the team coordination protocol nor any SOP specifies who produces this aggregated data. This is a portal-level concern, so it is naturally my responsibility, but I need standardized per-pair outputs to aggregate from.

#### F7: Portal Architecture for 73+ Pairs

The current portal has 4 page files hardcoded for HY-IG x SPY. With 73 pairs, the architecture choices are:

| Architecture | Pages | Pros | Cons |
|-------------|-------|------|------|
| Per-pair pages (4 per pair) | 292 | Each pair is self-contained | Streamlit sidebar becomes unmanageable; file count explodes |
| Template pages with pair selector | 4 + config | Clean, scalable | User must select pair from dropdown; less direct URL linking |
| Hybrid: comparison home + per-pair deep dive | 5 + dynamic | Best UX; overview-then-drill | Most complex to build; needs routing logic |

Option 3 (hybrid) is the most appropriate for a portal serving 73 analyses. It requires:
- A home/landing page with the cross-pair leaderboard and filter controls
- Template-based per-pair pages generated from config
- Comparison dashboard pages for multi-target or multi-indicator views

This is an architecture decision that should be in the team coordination protocol or Analysis Brief.

---

## 3. Suggestions for Each Teammate's SOP

### For Dana's SOP

1. **Data manifest at scale.** Add a requirement that Dana maintains `data/manifest.json` listing all `_latest` aliases, their backing dated files, refresh cadence, last-updated timestamp, and the pairs they serve. This replaces per-handoff discovery.

2. **Mixed-frequency TTL guidance.** When a pair's dataset contains variables with different refresh frequencies (daily market data + monthly macro), document the recommended TTL strategy: single TTL at the fastest frequency, or split into separate data files.

3. **Benchmark data inclusion.** Clarify whether each pair's dataset includes the target-class benchmark series (SPY for equities, AGG for fixed income), or if benchmark data is delivered as a separate universal dataset. The portal needs benchmark series for every Strategy page.

4. **Symlink vs. copy for `_latest`.** At scale, 73 file copies of `_latest` wastes storage and complicates updates. Consider using OS symlinks or a manifest-based lookup instead.

### For Evan's SOP

1. **`kpis.json` ownership.** Clarify whether Evan writes `kpis.json` directly (preferred) or delivers a KPI table that Ace must transform. Having Evan produce the JSON eliminates one transformation step and one error surface.

2. **Naming convention for `interpretation_metadata.json`.** Specify the file path convention for multi-pair runs: `results/{indicator_id}_{target_id}/interpretation_metadata.json` or `results/interpretation_metadata_{indicator_id}_{target_id}.json`. Grouping by indicator directory would make cross-pair comparison trivial for "Differs From" notes.

3. **"How to Read This" callout content.** The `interpretation_metadata.json` schema includes `mechanism` (plain English) and `observed_direction`. It does not include the ready-to-render callout text that compares expected vs. observed direction. Consider adding a `callout_text` field that Evan writes as part of his handoff -- he is the domain expert best positioned to explain discrepancies between expected and observed direction.

4. **Tournament results format at scale.** With 3,528 combinations per pair, the tournament CSV must be efficient for portal filtering. Evan should deliver: (a) a summary CSV with top-N winners per pair, and (b) a detail CSV with all combinations for users who want to explore. This prevents me from loading massive files on every page render.

5. **Cross-pair aggregation.** When Evan runs multiple pairs, consider producing a `results/cross_pair_summary.csv` with one row per pair showing: pair_id, winner_signal, winner_threshold, winner_strategy, oos_sharpe, oos_max_dd, observed_direction. This feeds comparison dashboards directly.

### For Ray's SOP

1. **Narrative scaling strategy.** At 73 pairs, Ray cannot write 73 full portal narratives. Adopt a tiered approach:
   - **Indicator narrative** (one per indicator, ~31 docs): what the indicator measures, economic significance, historical context. Reused across all targets.
   - **Per-pair addendum** (one per priority pair, ~73 docs): direction-specific interpretation, mechanism differences, "Differs From" notes relative to other targets of the same indicator. These are lightweight (1-2 paragraphs).
   - **Thematic group narrative** (optional, ~5-10 docs): for groups of related pairs (e.g., "All credit spread indicators vs. equity targets").

2. **Single canonical glossary.** Maintain one `docs/portal_glossary.json` (or .md with machine-readable structure) covering all technical terms across all analyses. Portal loads this once. Do not embed per-pair glossaries.

3. **Portfolio-level storytelling arc.** The current storytelling arc is per-pair. The portal needs a top-level arc that explains: "Why 31 indicators? What do they tell us collectively about market conditions? How should a portfolio manager use this dashboard?" This is a single document, not 73 documents.

### For Vera's SOP

1. **Chart directory structure at scale.** With ~500 charts, flat directories under `output/charts/plotly/` are unmanageable. Adopt per-pair subdirectories: `output/charts/plotly/{indicator_id}_{target_id}/`. Alternatively, maintain a `chart_registry.json` in `output/charts/` that maps chart IDs to file paths and metadata.

2. **Comparison dashboard chart specs.** Add guidance for when Vera should produce composite comparison charts (same indicator across multiple targets) vs. individual per-pair charts that Ace assembles into side-by-side panels. Define the handoff for composite charts.

3. **Direction annotation versioning.** Confirm that direction annotations baked into charts reference a specific version of `interpretation_metadata.json`. If the metadata is updated after chart production (e.g., after a model re-run), charts must be regenerated. The metadata sidecar should include a hash or version of the interpretation metadata it was built from.

4. **Audience tag enforcement.** The audience tag (`exec`, `narrative`, `analytical`, `technical`) in the file naming convention becomes critical at scale. I need to filter charts by page automatically. Enforce this tag in every chart delivery.

### For Team Coordination Protocol

1. **Portal navigation architecture.** Add a section specifying the portal architecture for multi-indicator analyses. The protocol should state whether pairs are accessed via: (a) per-pair pages in the sidebar, (b) a pair selector dropdown on template pages, or (c) a hybrid with comparison home + deep-dive pages. This is a cross-cutting decision that affects all agents' deliverables.

2. **Cross-pair data products.** Add a standard deliverable: `results/cross_pair_summary.csv` with one row per pair. Define the schema. This feeds the portal's comparison dashboards and is jointly owned by Evan (produces) and Ace (consumes).

3. **Naming conventions for multi-pair files.** Extend the existing naming conventions to include pair ID in paths: `results/{indicator_id}_{target_id}/...`, `output/charts/{indicator_id}_{target_id}/...`. Currently, the conventions assume a single pair per analysis run.

4. **Interpretation annotation pipeline.** The team coordination protocol (Section "Interpretation Annotation Handoffs") describes the pipeline well (Evan -> Ray validates -> Vera renders -> Ace implements callout). Add: (a) the file naming convention for `interpretation_metadata.json` per pair, (b) who produces the "Differs From" comparison text when the same indicator has opposite directions for different targets, (c) how to handle updates to metadata after charts and portal pages are already built.

5. **Analysis Brief Section 10 as machine-readable config.** The Analysis Brief's Portal Specifications section (Section 10) contains exactly the fields I need for config-driven page generation. If this section were also delivered as JSON (`docs/portal_config_{indicator_id}_{target_id}.json`), I could auto-generate page scaffolding. Add this to the Brief template's Deliverables Checklist.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

### 4.1 Portal Architecture Template for Multi-Pair Apps

My SOP defines a standard 5-page structure (Hook, Story, Evidence, Strategy, Method) designed for a single analysis pair. At 73+ pairs, this structure breaks. I need to add a **Multi-Pair Portal Architecture** section:

```
app/
  app.py                           # Landing: cross-pair dashboard, leaderboard, filters
  pages/
    1_overview.py                   # Cross-pair comparison: heatmaps, direction grid
    2_pair_story.py                 # Template: per-pair layperson narrative
    3_pair_evidence.py              # Template: per-pair analytical detail
    4_pair_strategy.py              # Template: per-pair backtest results
    5_methodology.py                # Shared: data sources, methods catalog, glossary
  components/
    charts.py                       # Reusable chart rendering
    metrics.py                      # KPI card components
    narrative.py                    # Markdown rendering
    direction.py                    # NEW: "How to Read This" + "Differs From" components
    pair_selector.py                # NEW: pair navigation component
    comparison.py                   # NEW: cross-pair comparison dashboards
  config/
    pairs/                          # Per-pair config JSONs (from Analysis Brief S10)
    portal_config.json              # Global portal config (theme, navigation, defaults)
    glossary.json                   # Canonical glossary (from Ray)
```

### 4.2 Config Schema for Data-Driven Pages

I need a formal config schema that replaces hardcoded values in page source files:

```json
{
  "pair_id": "hy_ig_spy",
  "indicator_id": "hy_ig",
  "target_id": "spy",
  "page_title": "HY-IG Credit Spread -> S&P 500",
  "audience": "Portfolio managers with economics background",
  "expected_direction": "counter_cyclical",
  "observed_direction": "counter_cyclical",
  "direction_consistent": true,
  "direction_annotation": "When the HY-IG spread widens...",
  "mechanism": "Widening HY-IG spreads reflect...",
  "benchmark_ticker": "SPY",
  "target_class": "Equity",
  "kpis": [...],
  "data_path": "data/hy_ig_spy_daily_latest.parquet",
  "results_dir": "results/hy_ig_spy/",
  "charts_dir": "output/charts/plotly/hy_ig_spy/"
}
```

This schema should be documented in my SOP and agreed with Alex.

### 4.3 Templates for "How to Read This" and "Differs From" Components

**"How to Read This" callout box template:**

```python
def render_how_to_read(metadata: dict):
    """Renders the direction interpretation callout for a pair."""
    direction = metadata["observed_direction"]
    mechanism = metadata["mechanism"]
    confidence = metadata["confidence"]
    # ... render st.info() or st.callout() with direction-specific icon and text
```

**"Differs From" note template:**

```python
def render_differs_from(indicator_id: str, current_target: str, all_metadata: dict):
    """Shows notes when the same indicator has different directions for different targets."""
    current_dir = all_metadata[current_target]["observed_direction"]
    for target, meta in all_metadata.items():
        if target != current_target and meta["observed_direction"] != current_dir:
            # Render st.warning() with comparison text
```

Both should be in `app/components/direction.py`.

### 4.4 Guidance on Per-Pair Pages vs. Comparison Views

My SOP should include a decision tree:

| User Question | View Type | Implementation |
|--------------|-----------|----------------|
| "Tell me about VIX/VIX3M -> SPY" | Per-pair deep dive | Template page with pair selector |
| "Which indicators best predict SPY?" | Target-filtered comparison | Comparison dashboard, filter by target |
| "Does HY-IG OAS behave differently for equity vs. bond targets?" | Indicator-filtered comparison | Comparison dashboard, filter by indicator |
| "What is the current regime across all indicators?" | Live signal dashboard | Aggregate page, all pairs' latest signals |
| "Top 10 best-performing strategies" | Leaderboard | Cross-pair summary table with sort/filter |

### 4.5 Performance Optimization for 73+ Pairs

At scale, Streamlit performance concerns include:

- **Data loading:** Loading 73 parquet files on app startup is not feasible. Use lazy loading: only load the selected pair's data. Pre-compute aggregated summaries for comparison pages.
- **Chart rendering:** 500+ Plotly JSONs cannot be loaded into memory simultaneously. Load on demand when the user navigates to a pair.
- **Session state:** Streamlit re-runs the entire script on every interaction. Minimize global state; use `st.cache_data` and `st.cache_resource` aggressively.
- **Sidebar navigation:** With 73 pairs, a flat sidebar list is unusable. Use a hierarchical structure: group by indicator type (Credit Spread, Volatility, Activity, etc.) or by target. Or use a search-based pair selector component instead of sidebar navigation.
- **Streamlit Community Cloud limits:** Free tier limits to 1 GB RAM, 1 CPU core, and 1 GB storage. With 73 pairs' data + charts, storage may exceed limits. Consider: (a) lazy data loading from GitHub raw URLs, (b) parquet compression, (c) paid tier, or (d) alternative hosting (Streamlit on a VM).

### 4.6 Reconciliation Scope at Scale

My SOP's Defense 2 (Reconciliation at Every Boundary) requires me to verify every upstream artifact. At 73 pairs, manual reconciliation is impossible. I need:

- An **automated reconciliation script** (`scripts/portal_reconciliation.py`) that iterates over all pairs, loads each pair's `interpretation_metadata.json`, `kpis.json`, and chart metadata, and verifies consistency.
- **Spot-check sampling:** For full manual review, sample 5-10 pairs per batch, rotating through pairs over time.
- **CI integration:** Run the reconciliation script as a pre-deployment check.

---

## 5. Key Concerns for the Multi-Indicator Expansion

### 5.1 Streamlit Performance with 73+ Pairs

Streamlit was designed for single-purpose data apps, not 73-pair analytical portals. Key risks:

- **Memory pressure.** Each Plotly JSON chart averages 100-500 KB. With 500 charts, that is 50-250 MB of chart data alone, plus 73 parquet datasets. Community Cloud's 1 GB RAM limit will be hit.
- **Startup time.** If the app attempts to load all data/charts at startup, it will exceed the 1-minute Streamlit boot timeout.
- **Re-run penalty.** Every widget interaction re-runs the script top to bottom. Heavy data loading in global scope will make the app feel sluggish.

**Mitigation:** Aggressive lazy loading, granular caching (`@st.cache_data` per pair, not globally), server-side filtering, and potentially a data API layer if performance remains insufficient.

### 5.2 Navigation Architecture

With 73 pairs, navigation is the make-or-break UX decision. Options:

- **Sidebar grouping:** Group pairs by indicator type (7 groups of ~10 pairs each). Pro: discoverable. Con: still long lists.
- **Search + filter:** A text search box with dropdown filters for indicator type and target class. Pro: scales indefinitely. Con: requires user to know what they want.
- **Heatmap landing page:** A heatmap of indicators (rows) x targets (columns), colored by a key metric (OOS Sharpe or observed direction). Clicking a cell navigates to that pair's deep dive. Pro: visual, intuitive, shows the whole landscape. Con: requires cross-pair summary data.

I recommend the heatmap landing page with search/filter as the primary navigation.

### 5.3 Config-Driven Page Generation

The current hardcoded page approach (one `.py` file per pair per page) does not scale. The solution is template pages that read from config:

```python
# pages/2_pair_story.py (template, works for any pair)
pair_id = st.session_state.get("selected_pair")
config = load_pair_config(pair_id)
narrative = load_narrative(config["indicator_id"], config["target_id"])
charts = load_charts(config["charts_dir"], audience_tier="narrative")
render_story_page(config, narrative, charts)
```

This requires a pair selection mechanism (either URL params or session state) and standardized config files for every pair.

### 5.4 Direction Annotation Rendering Consistency

Three layers render direction information:
1. **Vera's charts:** Inline line style (solid/dashed) and label text
2. **Ace's callout box:** "How to Read This" with direction + mechanism
3. **Ace's "Differs From" notes:** Cross-pair comparison when same indicator has opposite directions

All three must agree. The single source of truth is `interpretation_metadata.json`. The risk is temporal: if Vera renders charts on Tuesday and I build pages on Wednesday using an updated metadata file, the chart and callout may disagree. Mitigation: the metadata sidecar for each chart should include a hash of the interpretation metadata that was current when the chart was built. If I detect a mismatch, I flag it for Vera to regenerate.

### 5.5 "Differs From" Logic Across Pairs

The "Differs From" logic requires loading interpretation metadata for all pairs sharing an indicator, then comparing `observed_direction` values. Example:

- VIX/VIX3M -> SPY: `observed_direction = counter_cyclical` (VIX up -> SPY down)
- VIX/VIX3M -> TLT: `observed_direction = conditional` (depends on why VIX is rising)
- VIX/VIX3M -> GLD: `observed_direction = pro_cyclical` (VIX up -> GLD up, flight to safety)

The "Differs From" note for VIX/VIX3M -> SPY would read: "Note: This indicator behaves differently for other targets. For TLT, the direction is regime-dependent. For GLD, the indicator is pro-cyclical (rising VIX -> rising gold). See individual pair pages for details."

This text cannot come from Evan's per-pair metadata alone. It requires cross-pair aggregation. Either:
- (a) Evan produces a cross-pair direction comparison file, or
- (b) I generate the comparison text at runtime from individual metadata files.

Option (b) is more natural for the portal engineer, but I need a template for the comparison language. I should draft this template and have Ray review it for accuracy.

### 5.6 Deployment Constraints

- **Streamlit Community Cloud storage:** 1 GB. With 73 parquet datasets (~100-500 MB) + 500 charts (~50-250 MB), we may approach or exceed this limit.
- **Build time:** Community Cloud installs dependencies from `requirements.txt` on every deploy. With a large dependency set, this can take 5+ minutes.
- **Secret management:** If pairs use different data APIs with different keys, secrets management scales linearly.
- **Fallback plan:** If Community Cloud proves insufficient, consider Streamlit on a dedicated VM (Docker) with external storage for data/charts. The docker-compose approach from CLAUDE.md would apply here.

### 5.7 Mobile Responsiveness

Streamlit provides basic mobile responsiveness, but:
- Comparison dashboards with multiple charts side-by-side will not render well on small screens.
- The heatmap landing page requires horizontal scrolling with 35 target columns.
- KPI cards should stack vertically on mobile.

My SOP should include mobile testing as a quality gate item, with specific attention to the comparison dashboards.

---

## Summary

The multi-indicator expansion transforms the portal from a single-pair analytical app into a multi-dimensional research platform. The SOPs are well-structured for the analytical pipeline, but the portal integration pathway has four critical gaps at scale:

1. **No cross-pair data products are defined** -- I need aggregated summaries, direction comparison files, and a cross-pair leaderboard. Evan and I must agree on these.
2. **No portal architecture standard for multi-pair** -- the team coordination protocol should specify the navigation pattern and config-driven page generation approach.
3. **Narrative does not scale** -- Ray needs a tiered narrative strategy (per-indicator + per-pair addenda) rather than 73 full narratives.
4. **File management at 500+ charts** -- Vera needs per-pair chart directories and a chart registry.

These gaps are addressable with targeted SOP additions. None require fundamental changes to the analytical pipeline -- they are all portal integration concerns that fall primarily in my domain, with supporting conventions needed from each upstream agent.

---

## Addendum: Cross-Review Feedback Disposition (Step 2)

### Suggestions Received and Disposition

**From Dana's review (Section 3, "For Ace's SOP"):**

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Add "Data Source Manifest" page/component | ACCEPTED | Added to Section 3.5 as Data Source Manifest on Methodology page |
| 2 | Define fallback for stale `_latest` aliases | ACCEPTED | Added staleness warning to Quality Gates and Dana intake section |
| 3 | Batch KPI loading for multi-pair dashboards | ACCEPTED | Added multi-pair KPI loading pattern to Section 5 |
| 4 | "How to Read This" component template | ACCEPTED | Added full specification in new Section 3.5 |

**From Evan's review (Section 3, "For Ace's SOP"):**

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 12 | Update stale "no handoff template" note | ACCEPTED | Removed stale note; now references Evan's App Dev Handoff Template |
| 13 | Multi-pair portal architecture guidance | ACCEPTED | Added full multi-pair architecture section with config schema and view decision tree |
| 14 | `kpis.json` schema standardization | ACCEPTED | Documented schema in Evan intake section |
| 15 | Tournament display with Sharpe threshold | ACCEPTED | Added threshold display guidance; new anti-pattern "never display Sharpe without threshold" |

**From Vera's review (Section 3, "For Ace's SOP"):**

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Redesign portal_page field for hierarchy | ACCEPTED | Noted in chart organization section; will coordinate schema with Vera |
| 2 | Multi-pair dashboard specifications | ACCEPTED | Added comparison dashboard section to Viz intake |
| 3 | Chart manifest for volume management | ACCEPTED | Added chart_manifest.json spec to Viz intake section |
| 4 | Plotly performance with large datasets | ACCEPTED | Added Scattergl, downsampling guidance to performance section |

**From Ray's review (Section 3, "For Ace's SOP"):**

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 1 | Parametric portal narrative templates | ACCEPTED | Added multi-pair narrative scaling section to Ray intake |
| 2 | Target-class-specific portal templates | ACCEPTED | Covered by pair config schema (target_class field drives template selection) |
| 3 | Direction annotation batch loading | ACCEPTED | Added direction_annotations_batch.json to Ray intake section |
| 4 | Consolidated glossary management | ACCEPTED | Added portal_glossary.json spec to Ray intake section |

**From my own review (Section 4):**

| # | Suggestion | Decision | Rationale |
|---|-----------|----------|-----------|
| 4.1 | Multi-pair architecture template | ACCEPTED | Full architecture section added |
| 4.2 | Config schema for data-driven pages | ACCEPTED | JSON schema documented with all fields |
| 4.3 | "How to Read This" + "Differs From" templates | ACCEPTED | New Section 3.5 with component contracts |
| 4.4 | View type decision tree | ACCEPTED | Table added to architecture section |
| 4.5 | Performance optimization | ACCEPTED | Lazy loading, caching, Plotly WebGL guidance added |
| 4.6 | Automated reconciliation at scale | ACCEPTED | Added to Defense 2 as items 5 and 6 |

All 18 suggestions were accepted. None were rejected -- all addressed genuine scaling gaps revealed by the multi-indicator expansion.
