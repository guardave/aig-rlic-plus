# Cross-Review: Research Ray

## Date: 2026-03-14

**Reviewer:** Research Ray (research-ray)
**Trigger:** Full cross-review for multi-indicator expansion (73 priority pairs across 7 targets, 27 unique indicators)

---

## 1. What I Learned About Each Teammate's Workflow and Pressures

### Data Dana

Dana is the first consumer of my data source recommendations. In the single-pair world (HY-IG x SPY), I recommended 2-3 series and Dana sourced them. In the multi-indicator expansion, each Analysis Brief's Section 6 specifies a data request covering core and secondary series, derived series, and forward target returns. Across 73 pairs involving 27 unique indicators, I will be recommending data sources for indicators spanning every category: Credit Spread (HY-IG), Volatility/Options (VIX/VIX3M), Activity/Survey (ISM PMI, Building Permits, Cass Freight), Yield Curve/Rates (US10Y-US3M), Sentiment/Flow (Michigan Consumer Sentiment, Credit Card Default), Cross-Asset (Gold/Copper, Crude Oil, SOX), and Microstructure-adjacent (Retail Inventories/Sales).

**Key pressure points for Dana from my recommendations:**

1. **Exotic/non-MCP sources.** Several indicators in the priority catalog have no clear MCP path: Portland Cement Shipments (I8, Portland Cement Association), Architecture Billings Index (I13, AIA subscription/scrape), Cass Freight Index (I25, Cass Information Systems), Electricity-CPI YoY (I29, BLS component extraction). Each of these will trigger Dana's "Availability: UNCONFIRMED" flow and require me to find proxies or alternative sources. At 73 pairs, even 5-10 impractical recommendations could create significant round-trip overhead.

2. **Derived series complexity.** 6 derived indicators (I17 SOFR-US3M, I19 HY-IG spread, I22 VIX/VIX3M, I30 Gold/Copper, I31 ISM ratio, I32 New Orders YoY) require computation recipes per the Data Series Catalog Section 7.10. My research brief must include the exact computation formula and the constituent series IDs -- if I am vague ("compute the HY-IG spread"), Dana has to reverse-engineer the components.

3. **Frequency mismatches at scale.** The 27 indicators span daily (VIX, SOFR), weekly (Petroleum Inventory), monthly (ISM PMI, Building Permits, CPI), and quarterly (Credit Card Default DRCCLACBS) frequencies. When I recommend an indicator-target pair like I16 (quarterly Credit Card Default) x SPY (daily), I need to flag the alignment challenge explicitly in my brief so Dana knows to apply LVCF or another alignment rule. At 73 pairs, frequency mismatch documentation cannot be ad-hoc.

4. **Stable path alias management.** Dana's SOP requires `_latest` alias files for portal-facing datasets. If many of the 73 pairs feed the portal, Dana's alias maintenance grows linearly. My research brief should flag which pairs are portal-priority vs. analytical-only so Dana can prioritize alias creation.

### Econ Evan

Evan depends on my spec memo and research brief to ground his model specification. In the single-pair world, I delivered one spec memo with one recommended specification. At 73 pairs, Evan needs:

1. **Category selection input.** Evan's SOP Section 2.5 specifies a two-step process: consult the Relevance Matrix, then apply Rules A-D. My research brief Section "Recommended Analysis Categories" is the primary input for Rule C (indicator type classification). I must classify every indicator into one of 7 types (Credit Spread, Volatility/Options, Activity/Survey, Yield Curve/Rates, Sentiment/Flow, Cross-Asset, Microstructure). Some indicators are borderline: Is SOX (I23, PHLX Semiconductor Index) an Activity/Survey or Cross-Asset indicator? Is Retail Inventories/Sales (I15) Activity/Survey or Microstructure? My classification directly determines which method categories Evan runs first.

2. **Direction determination support.** The Analysis Brief Section 4 requires an `expected_direction` field. For well-studied pairs (HY-IG x SPY: counter-cyclical, strong literature), this is straightforward. For exploratory pairs (Cement Shipments x XLP, Gold/Copper Ratio x XLI, Electricity-CPI x XLE), I may find no academic literature to support a direction hypothesis. My quality gate says I must "validate or flag any contradiction between theoretical expectation and available empirical evidence." At 73 pairs, I need a systematic approach to direction determination, not ad-hoc searching per pair.

3. **Reverse causality context.** The Analysis Brief Section 11.2 mandates reverse causality checks (G11 gap). My research brief should flag which pairs are at high risk for reverse causality based on the literature. For example, SOX x XLE -- does semiconductor demand drive energy prices, or do energy prices drive semiconductor costs? Both channels are plausible. Flagging these upfront saves Evan from being surprised at the diagnostic stage.

4. **Specification memo pipeline at scale.** The two-stage delivery (quick spec memo then full brief) works well for one pair at a time. At 73 pairs, Evan needs a batching strategy. Should I deliver spec memos for all 21 SPY pairs at once? Or deliver indicator-by-indicator (all ISM PMI pairs together)? The latter would allow Evan to reuse specification logic across targets, which maps better to his workflow.

### Viz Vera

Vera receives my event timeline for chart annotations. In the single-pair world, one timeline covered one target's relevant events. At 73 pairs across 7 targets:

1. **Target-class-specific timelines.** SPY events (broad market) differ from XLE events (energy-sector-specific: OPEC decisions, shale revolution, refinery disruptions). XLY events include consumer spending shifts, retail closures, seasonal patterns. I need to produce target-specific event timelines, not one generic timeline. Across 7 targets, this is 7 distinct timeline documents.

2. **Indicator-specific annotations.** When the same indicator appears across multiple targets (e.g., VIX/VIX3M appears in 5 targets), Vera needs to know whether the direction annotation changes. VIX/VIX3M rising is bearish for SPY but the relationship with XLE may be different (energy sector has its own volatility dynamics). The direction annotation visual language (solid = pro-cyclical, dashed = counter-cyclical) must be pair-specific, not indicator-specific.

3. **Annotation volume.** 73 pairs x ~5-10 events per pair = 365-730 individual annotations. Vera's Annotation Source Tracking table requires each annotation to cite its source (my research brief, Evan's notes, Alex's instructions). This creates a significant documentation overhead. I should organize event timelines in a machine-readable format (CSV) that Vera can batch-import, not just markdown tables.

4. **Domain visualization conventions.** Different indicator types have different charting conventions: yield curves have maturity on x-axis, PMI charts typically include the 50-threshold line, credit spread charts often use recession shading. I should document these conventions per indicator type, not per pair, to avoid 73 redundant notes.

### AppDev Ace

Ace receives my portal narrative and storytelling arc. At 73 pairs:

1. **Narrative template scalability.** My portal narrative template has 5 pages (Hook, Story, Evidence, Strategy, Method). Writing a bespoke narrative for each of 73 pairs is infeasible. I need a parametric narrative template where the structure is fixed but the content fills in from the Analysis Brief fields: `{INDICATOR_NAME}`, `{TARGET_NAME}`, `{MECHANISM}`, `{EXPECTED_DIRECTION}`, `{LITERATURE_SUPPORT}`.

2. **Target-class-specific narrative framing.** The "Story" page for an equity target (SPY) differs from a sector ETF (XLE). For SPY, the narrative is about broad market risk. For XLE, it is about energy sector dynamics -- supply/demand fundamentals, OPEC, transition risk. For XLP (Consumer Staples), the narrative is about defensive positioning and consumer spending resilience. One narrative template is insufficient -- I need at least 3 template variants: broad equity, sector-specific, and cross-asset.

3. **"How to Read This" callout box content.** Each pair needs a unique direction annotation for the callout box. For 73 pairs, I need a systematic way to generate these annotations. The Analysis Brief Section 10 defines `{DIRECTION_ANNOTATION}` -- I should produce a batch file of direction annotations, one per pair, that Ace can load programmatically rather than embed manually.

4. **Glossary deduplication.** Many pairs share technical terms (OAS, PMI, VIX term structure, Granger causality). Rather than producing 73 separate glossaries, I should maintain a single consolidated glossary that Ace references across all pair pages. New pairs add terms incrementally; existing terms are not duplicated.

---

## 2. Where Our Handoffs Connect and Where Friction Could Arise

### Handoff Map (all paths involving Ray)

```
              Analysis Brief (from Alex)
                      |
                      v
            +---------+---------+
            |                   |
     Spec Memo (to Evan)    Data Source Recs (to Dana)
            |                   |
     Full Brief (to Evan)   Availability feedback (from Dana)
            |                   |
     Category Recommendation    |
     Direction Validation       |
     Literature Support Level   |
            |                   |
            v                   v
     Evan's results -----> interpretation_metadata.json
            |                         |
     Ray validates direction          |
     vs literature                    |
            |                         |
            v                         v
     Event Timeline ---------> Vera (annotations)
            |                         |
            v                         v
     Portal Narrative -------> Ace (story + glossary + callout)
     Storytelling Arc -------> Ace
     Direction Annotations --> Ace ("How to Read This")
```

### New Friction Points from the Multi-Indicator Expansion

1. **Category recommendation (6th bullet in my SOP).** My research brief must include a "Recommended Analysis Categories" table with indicator type classification and Relevance Matrix scores. If I classify an indicator incorrectly (e.g., Gold/Copper as "Cross-Asset" when Evan treats it as "Activity/Survey" proxy), Evan may run the wrong category set. Resolution: my SOP says "Indicator type classification: {INDICATOR_TYPE}" -- I should cross-reference with the Data Series Catalog's own classification (Section 7) and flag any disagreements.

2. **Direction-vs-theory contradiction flag.** My quality gate requires: "If Analysis Brief specifies `expected_direction`, the brief validates or flags any contradiction between theoretical expectation and available empirical evidence." At 73 pairs, some will have contradictions (e.g., Cement Shipments theoretically pro-cyclical for XLP, but empirical evidence may show no significant relationship). I need a systematic contradiction-flagging format, not ad-hoc prose. Suggested format:

   ```
   | Pair | Expected Direction | Literature Direction | Contradiction? | Resolution |
   |------|--------------------|---------------------|---------------|------------|
   | I8 x XLP | pro_cyclical | no literature found | FLAG: exploratory | Determine empirically |
   ```

3. **Literature validation for 73 priority pairs.** My quality gate says: "For priority pairs, note whether the indicator-target relationship has established academic support or is exploratory." This is the highest-volume single task I face. Of the 73 pairs, I estimate:
   - ~15-20 have strong academic support (HY-IG x SPY, VIX/VIX3M x SPY, ISM PMI x SPY, Unemployment x SPY, Yield Curve x SPY)
   - ~25-30 have moderate support (sector-specific versions of well-studied indicators)
   - ~20-25 are exploratory (Cement x XLP, ABI x XLE, Cass Freight x XLY, Electricity-CPI x XLE, Gold/Copper x XLI)

   Delivering individual literature reviews for each exploratory pair is infeasible. I need a tiered approach: deep review for strong/moderate pairs, indicator-level review (not pair-level) for exploratory pairs, with a note that target-specific evidence is limited.

4. **Indicator type classification for Relevance Matrix.** Some indicators straddle categories:
   - SOX (I23): Cross-Asset (it is a semiconductor index) or Activity/Survey (it proxies tech manufacturing activity)?
   - Credit Card Default (I16): Sentiment/Flow (credit stress signal) or Activity/Survey (consumer activity)?
   - Retail Inventories/Sales (I15): Activity/Survey or Microstructure?
   - Petroleum Inventory (I27): Cross-Asset or Activity/Survey?

   These classification ambiguities propagate to Evan's category selection heuristic. I should document my classification rationale for borderline indicators and invite Evan to override with justification.

5. **Target-class-specific research contexts.** The same indicator (e.g., Michigan Consumer Sentiment, I14) has different economic channels depending on the target:
   - I14 x SPY: broad consumer confidence -> spending -> corporate earnings -> equity returns
   - I14 x XLE: consumer confidence -> energy demand expectations -> energy prices -> energy sector
   - I14 x XLK: consumer confidence -> tech spending (consumer electronics, cloud services)
   - I14 x XLP: consumer confidence -> staples spending (actually less sensitive -- staples are defensive)
   - I14 x XLY: consumer confidence -> discretionary spending -> direct linkage

   Each of these channels needs a distinct mechanism description in the Analysis Brief Section 4. This is 5 different mechanism write-ups for one indicator, multiplied across the 6 indicators that appear in 4+ targets. This is a significant research burden.

---

## 3. Suggestions for Each Teammate's SOP

### For Dana's SOP

1. **Batch data availability pre-check.** Dana's current pre-check is per-pair. For the multi-indicator expansion, I suggest a batch pre-check step: "When the Analysis Brief covers multiple pairs sharing the same indicator (e.g., I14 Michigan Consumer Sentiment appears in 5 targets), source the indicator data once and validate once. Create a shared indicator dataset that feeds all target analyses." This reduces redundant sourcing from 73 pulls to ~27 unique indicator pulls + 7 target pulls.

2. **Exotic indicator sourcing playbook.** Several priority indicators have no MCP path: I8 (Cement), I13 (ABI), I25 (Cass Freight), I29 (Electricity-CPI component). Dana's SOP lists web scraping as Priority 5 but provides no guidance on how to handle subscription-gated sources (AIA requires paid access for ABI). I suggest adding a decision tree: "If source is subscription-gated -> escalate to Alex for access decision -> if denied, recommend proxy (from Ray's brief) -> document the proxy substitution."

3. **Frequency alignment documentation at scale.** Dana's SOP requires documenting alignment methods in the data dictionary. For 73 pairs with mixed frequencies, I suggest a standardized alignment summary table in the data delivery: "All quarterly indicators (I16) aligned to daily targets using LVCF. All monthly indicators aligned using last-business-day convention. Staleness exceeding 5 days flagged for: [list]."

### For Evan's SOP

1. **Category selection batch workflow.** Evan's current heuristic (Rules A-D) is designed for one pair at a time. For 73 pairs, I suggest adding a batch pre-computation step: "Group pairs by indicator type. Apply Rules A-D at the indicator-type level first, then adjust for target-specific considerations. This avoids re-running the heuristic 73 times for 27 indicators."

2. **Reusable specification templates by indicator.** When the same indicator appears across multiple targets (I14 appears in 5 targets), the core specification (regressors, controls, lag structure) is similar -- only the dependent variable changes. Evan's SOP should acknowledge this: "For multi-target indicators, establish a base specification from the first target analysis, then adapt for subsequent targets. Document what changed and why."

3. **Direction consistency checks across targets.** Evan's `interpretation_metadata.json` is per-pair. When I14 Michigan Consumer Sentiment is analyzed against both SPY (pro-cyclical) and XLP (potentially less cyclical or even counter-cyclical for defensive staples), Evan should flag cross-target direction inconsistencies proactively rather than waiting for me to catch them during validation.

4. **Rule C input quality.** Evan's Rule C depends on the indicator type from my brief. I suggest Evan's SOP add: "If Ray's indicator type classification is ambiguous or borderline, request clarification before running the heuristic. Do not default to one classification without documenting the choice." This prevents silent errors in category selection.

### For Vera's SOP

1. **Batch event timeline ingestion.** Vera's current workflow reads event timelines from markdown tables in my research briefs. For 73 pairs across 7 targets, I suggest Vera's SOP add support for machine-readable event timeline ingestion: "Accept event timelines as CSV files with columns: `date`, `event`, `relevance`, `type`, `target`, `indicator`. Batch-load for chart annotation rather than manual extraction from markdown."

2. **Direction annotation per pair, not per indicator.** Vera's SOP defines visual language for direction (solid = pro-cyclical, dashed = counter-cyclical). The SOP should clarify that direction encoding is per indicator-target pair, not per indicator. VIX/VIX3M may be counter-cyclical for SPY but could have a different relationship with XLE. "Always reference the pair-specific `interpretation_metadata.json`, never assume direction from the indicator alone."

3. **Indicator-type charting convention library.** Rather than receiving ad-hoc domain visualization conventions from me per brief, Vera's SOP could maintain a reusable library:
   - Activity/Survey indicators: include the 50-threshold line for PMI charts
   - Yield Curve/Rates: maturity on x-axis
   - Credit Spread: recession shading, crisis markers
   - Volatility/Options: log scale for VIX extremes

   I would contribute the initial library content; Vera would maintain and extend it.

4. **Multi-pair dashboard annotations.** Vera's SOP mentions "Differs From" annotations when the same indicator has opposite interpretations across targets. At 73 pairs, the number of same-indicator cross-target comparisons is significant (6 indicators appear in 4+ targets). Vera may need a template for cross-target comparison dashboards that I help populate with mechanism text.

### For Ace's SOP

1. **Parametric portal narrative templates.** Ace's SOP assumes bespoke page content per analysis. For 73 pairs, I suggest Ace develop parametric page templates that load content from structured data:
   - Page title, KPI labels, mechanism text, direction annotation -> all from a `pair_config.json` per analysis
   - Narrative body -> parametric template with fill-in variables, not freeform prose for every pair
   - Glossary -> consolidated, incremental, shared across all pair pages

2. **Target-class-specific portal templates.** The "How to Read This" callout box content differs by target class. For equity targets, the benchmark context is SPY. For energy sector (XLE), the benchmark context is XLE itself plus sector-specific dynamics. Ace's SOP should define at least 3 callout templates:
   - Broad equity (SPY): "This indicator predicts broad market returns..."
   - Sector equity (XLE, XLI, XLK, XLC, XLP, XLY): "This indicator predicts {sector_name} sector returns. Unlike the broad market..."
   - (Future: fixed income, commodity, crypto -- not yet in the priority catalog)

3. **Direction annotation batch loading.** Instead of manually embedding `{DIRECTION_ANNOTATION}` per page, Ace should implement a direction annotation service that reads from a batch file I produce: `docs/direction_annotations_batch.json` with one entry per pair. This scales to 73+ pairs without code changes.

4. **Consolidated glossary management.** Ace's SOP should specify how the glossary grows across pairs: "When a new pair adds terms not already in the glossary, append them. When an existing term is used in a new context, add a context-specific note but do not duplicate the definition." I will deliver glossary entries as structured data (term, definition, context) rather than inline prose.

### For Team Coordination Protocol

1. **Phase 0 Analysis Brief batching.** The current protocol assumes one Analysis Brief per analysis run. For 73 pairs, Alex needs a batching strategy: by target (all 21 SPY pairs in one sprint), by indicator (all ISM PMI pairs together), or by indicator type (all Activity/Survey indicators). The protocol should document the recommended batching approach and how it affects the acknowledgment protocol -- does each agent acknowledge 21 briefs individually, or one batch?

2. **Acknowledgment protocol scalability.** The current protocol requires "Each agent reads the brief within one task cycle" and sends a structured acknowledgment. At 73 pairs, this means 73 x 5 agents = 365 acknowledgment messages. The protocol should allow batch acknowledgments: "I have read the Analysis Briefs for pairs #1-#21 (SPY). Domain-specific concerns: [aggregated list]."

3. **Shared indicator data deduplication.** The protocol should address data reuse: "When multiple pairs share the same indicator (e.g., I14 appears in 5 targets), Dana sources the indicator once. The indicator dataset is shared across all target analyses. Only the target-specific data is sourced per pair."

4. **Interpretation annotation coordination at scale.** The Interpretation Annotation Handoffs section (team coordination, lines 179-188) describes a 4-agent workflow per pair. At 73 pairs, this workflow needs a batch coordinator. I suggest adding: "For indicators appearing in multiple targets, Ray validates direction across all targets simultaneously and delivers a consolidated direction validation table, rather than validating each pair individually."

5. **Run Registry integration.** The Run Registry (in `docs/reference-catalogs-index.md`) must track 73+ analysis runs. The protocol should specify how the registry links to the Priority Combinations Catalog -- when a pair moves from "Pending" to "Completed" in the catalog, a corresponding entry should appear in the Run Registry.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

Reading all teammates' SOPs in the context of 73 pairs revealed several gaps in my own workflow:

1. **I need an indicator type classification guide.** My SOP says to classify each indicator into one of 7 types, but I have no documented rationale for borderline cases. I should add a classification decision tree:
   - Does it measure credit risk directly? -> Credit Spread
   - Does it derive from options markets? -> Volatility/Options
   - Does it survey economic activity or sentiment? -> Activity/Survey (if output-based) or Sentiment/Flow (if opinion-based)
   - Does it measure yield differentials? -> Yield Curve/Rates
   - Does it measure fund flows, positioning, or crowd behavior? -> Sentiment/Flow
   - Does it measure a non-equity asset that proxies macro conditions? -> Cross-Asset
   - Does it measure market internal structure? -> Microstructure

   For SOX (I23): it is a semiconductor index (equity-based), used as a proxy for tech/manufacturing activity -> Cross-Asset. For Credit Card Default (I16): it measures consumer credit stress -> Sentiment/Flow. For Petroleum Inventory (I27): it is a physical commodity stock measure -> Cross-Asset.

2. **I need a template for category recommendations.** My current brief includes a "Recommended Analysis Categories" section, but the format is not standardized. I should use the exact format from the Analysis Brief template Section 7.1, mirroring the Relevance Matrix layout, so Evan can directly copy my recommendation without reformatting.

3. **I need target-class-specific research brief templates.** A research brief for ISM PMI x SPY (broad equity) should emphasize different literature than ISM PMI x XLE (energy sector). The mechanism, control variables, and relevant papers differ. I should develop template variants:
   - **Broad equity template:** emphasize macro channels (aggregate demand, monetary policy, business cycle)
   - **Sector template:** emphasize sector-specific channels (supply/demand fundamentals, regulatory exposure, competitive dynamics) in addition to macro channels
   - **Cross-asset template** (future): emphasize price transmission, commodity cycles, global demand

4. **I need a batch literature review strategy.** Reviewing literature for 73 individual pairs is infeasible. My strategy should be:
   - **Tier 1: Indicator-level review** (27 reviews). For each indicator, review the academic literature on its predictive power for equity returns generally. This covers the mechanism and establishes the indicator type.
   - **Tier 2: Target-class adjustment** (7 adjustments). For each target class (SPY, XLE, XLI, etc.), document sector-specific factors that modify the indicator's channel.
   - **Tier 3: Pair-specific notes** (only for pairs where the indicator-target relationship has specific academic study). Most sector-specific pairs will not have dedicated academic studies -- the Tier 1 review plus Tier 2 adjustment is sufficient.

   This reduces 73 full literature reviews to 27 indicator reviews + 7 target-class contexts + a handful of pair-specific deep dives.

5. **My spec memo pipeline needs a batching protocol.** The two-stage delivery (spec memo then full brief) works per-pair. At scale, I should batch spec memos by indicator: "Here are the spec memos for all ISM PMI pairs (I2 x SPY, I2 x XLE, I2 x XLP). The base specification is identical; target-specific adjustments noted per pair." This lets Evan start work on a batch without waiting for 73 individual memos.

6. **I need a direction determination workflow for ambiguous/conditional pairs.** My SOP says I must determine expected direction, but it does not describe how to handle the ~20-25 exploratory pairs where no literature exists. I should add a decision tree:
   - Is there academic evidence for this indicator's predictive power? -> If yes, use the literature's direction
   - If no academic evidence: is there a clear theoretical channel? -> If yes, state the theoretical direction and mark as "Weak" literature support
   - If no clear theoretical channel: is the indicator in the same factor family as a well-studied indicator? -> If yes, use analogical reasoning (e.g., Cass Freight is Activity/Survey like ISM PMI, so expect pro-cyclical)
   - If none of the above: mark as "ambiguous" and let Evan determine empirically

7. **I need to scale event timeline production.** Producing 7 target-specific event timelines is a one-time investment. I should create a master event database organized by category:
   - Macro events (recessions, rate changes, QE) -> apply to all targets
   - Sector events (OPEC for XLE, semiconductor shortages for XLK, consumer spending shifts for XLY) -> apply to specific targets
   - Indicator events (methodology changes for CPI, ISM survey redesigns) -> apply to pairs using that indicator

   The master database produces pair-specific timelines by filtering: `target_events = macro_events + sector_events[target] + indicator_events[indicator]`.

---

## 5. Key Concerns for the Multi-Indicator Expansion

### 5.1 Literature Coverage for Non-Standard Indicators

Several priority indicators have thin or nonexistent academic coverage:

| Indicator | Literature Status | Concern | Mitigation |
|-----------|------------------|---------|------------|
| I8 Portland Cement Shipments | Very thin -- practitioner lore, no peer-reviewed studies | Cannot cite academic support; direction determination relies on theoretical reasoning (construction activity proxy) | Frame as "exploratory" with Activity/Survey classification by analogy to housing starts |
| I13 Architecture Billings Index | Moderate -- AIA publishes reports, some practitioner research | Subscription-gated source creates data access risk; academic coverage limited to housing/construction sector | Recommend NAHB HMI (I12) as accessible proxy; flag ABI as "UNCONFIRMED" source |
| I25 Cass Freight Index | Thin -- logistics industry reports, limited academic | No FRED series; proprietary data from Cass Information Systems | Research alternative freight indicators (BTS freight index, trucking tonnage); flag access risk |
| I29 Electricity-CPI YoY | Very thin -- no dedicated academic study found | Derived BLS component; extraction methodology may be fragile | Provide detailed BLS series hierarchy for Dana; flag as "UNCONFIRMED" |
| I30 Gold/Copper Ratio | Moderate -- practitioner "Dr. Copper" narrative, some academic | Well-known as economic health proxy but specific academic study of Gold/Copper -> sector ETFs is limited | Leverage broader Gold and Copper individual literature; combine |
| I32 Manufacturers' New Orders YoY | Good for levels (I26), thin for YoY transform specifically | YoY transformation is an analyst choice, not an academically studied variant | Reference I26 literature and document the transformation rationale |

### 5.2 Cross-Asset Pair Research Challenges

The priority catalog includes several cross-indicator-target pairs where the economic channel is non-obvious:

- **SOX (I23) x XLE:** How does semiconductor demand relate to energy sector returns? Possible channels: tech manufacturing = energy demand, but the linkage is indirect. Academic support is exploratory.
- **Import Price Index (I24) x XLI:** Import prices affect input costs for industrials, but the direction is ambiguous -- higher import prices could mean stronger global demand (pro-cyclical) or supply shock (stagflationary).
- **Cement Shipments (I8) x XLP:** Why would construction activity predict consumer staples returns? The channel is very indirect -- possibly through housing wealth effects on consumer spending. This pair may have low academic justification.

For each of these, I must either find a defensible economic channel or recommend the pair be flagged as "exploratory" in the Analysis Brief with `literature_support: Exploratory`.

### 5.3 Scaling Research Briefs for 73 Pairs

The current research brief template is designed for deep single-pair analysis (~3,000-5,000 words). At 73 pairs, this would produce 220,000-365,000 words of research briefs. This is infeasible.

**Proposed tiered approach:**

| Tier | Pairs | Brief Type | Depth | Est. Volume |
|------|-------|-----------|-------|-------------|
| Deep | ~10 (flagship pairs with strong literature) | Full research brief per pair | Complete template | ~40,000 words |
| Standard | ~30 (well-studied indicators, sector adaptation) | Indicator-level brief + target-specific addendum | Core sections + adaptation notes | ~60,000 words |
| Light | ~33 (exploratory or thin-literature pairs) | Indicator-level brief + direction determination note | Key findings + classification + direction only | ~30,000 words |

Total: ~130,000 words, manageable across a phased rollout.

### 5.4 Direction Determination for Ambiguous/Conditional Pairs

Of the 73 pairs, I estimate:
- ~35 have clear direction (established literature consensus)
- ~20 have theoretically motivated direction (moderate confidence)
- ~10 have conditional direction (regime-dependent -- need to specify conditions)
- ~8 have ambiguous direction (must be determined empirically)

The conditional and ambiguous pairs are the most challenging for my SOP. Examples:

- **VIX/VIX3M (I22) x XLE:** VIX/VIX3M is counter-cyclical for broad equities, but energy sector has its own volatility dynamics (geopolitical risk, OPEC). Direction may be conditional on whether the VIX spike is market-wide or energy-specific.
- **US10Y-US3M (I18) x XLE (displayed inverted):** The catalog notes "displayed inverted" -- meaning the human analyst found that inverting the yield curve relationship improved the signal for energy. This is an empirical finding I need to validate or challenge from the literature.
- **Gold/Copper Ratio (I30) x XLI:** Higher ratio = risk-off (gold up, copper down). For industrials, this should be counter-cyclical. But the magnitude and lag structure are uncertain.

### 5.5 Managing the Spec Memo Pipeline at Scale

If Alex issues Analysis Briefs in batches (e.g., all 21 SPY pairs), I need to deliver 21 spec memos before Evan can start. Serial delivery would create a bottleneck. My recommendation:

1. **Batch by indicator.** Deliver one spec memo per indicator (27 total), each covering all targets for that indicator. This reduces 73 spec memos to 27.
2. **Reuse base specifications.** For each indicator, the dependent variable definition, lag structure, and core regressors are target-independent. Only the target variable and sector-specific controls change.
3. **Deliver in priority order.** Start with the 6 most-connected indicators (I14, I18, I22, I1, I25, I26 -- appearing in 4-5 targets each), which cover 26 pairs. This gives Evan the highest-leverage batch first.
4. **Flag exploratory pairs for deferred deep research.** For the ~33 light-tier pairs, the spec memo says: "No established specification in the literature. Recommend standard lead-lag + correlation analysis. Direction to be determined empirically."

---

*This review reflects my assessment as Research Ray facing a 25x scale-up (from 1 pair to 73). The team's SOPs are strong for single-pair workflows. The primary risk is that per-pair processes (literature reviews, spec memos, event timelines, direction determinations, portal narratives) do not scale linearly. Every suggestion above is aimed at introducing batch processing, template reuse, and tiered depth to make the expansion feasible without sacrificing rigor.*

---

## Addendum: Step 2 — SOP Self-Update Disposition (2026-03-14)

### Suggestions Received from Teammates and Disposition

#### From Data Dana's Review

| # | Suggestion | Disposition | Rationale |
|---|-----------|:-----------:|-----------|
| 1 | Add "Data Availability Risk Matrix" to research brief template | **Accepted** | Added to Section 5 brief template. Essential for flagging non-MCP sourcing risks before Dana invests effort. |
| 2 | Cross-pair direction consistency check across briefs | **Accepted** | Added as Section 6c "Cross-Pair Direction Consistency Check." Produces a consistency table for multi-target indicators. |
| 3 | Deliver data source recommendations in machine-readable format (CSV/JSON) | **Accepted** | Added CSV delivery note to the Recommended Data Sources section. Enables Dana to automate intake. |

#### From Econ Evan's Review (R3)

| # | Suggestion | Disposition | Rationale |
|---|-----------|:-----------:|-----------|
| 5 | Category recommendation rationale depth (cite evidence, not just scores) | **Accepted** | Updated the Recommended Analysis Categories table to require cited evidence in rationale column. |
| 6 | Indicator type classification for hybrids (tie-breaking rule) | **Accepted** | Added Section 4b "Indicator Type Classification" with decision tree and primary/secondary type convention. |
| 7 | Expected direction conditional logic (structured, not vague) | **Accepted** | Added to Section 6b "Direction Determination Workflow" with specific conditional logic format and examples. |
| 8 | Literature support → interpretation confidence mapping | **Accepted** | Added mapping table in Section 6b: Strong→high, Moderate→medium, Weak→low, Exploratory→low. |

#### From Viz Vera's Review (R3)

| # | Suggestion | Disposition | Rationale |
|---|-----------|:-----------:|-----------|
| 1 | Target-class-specific event timelines (add impact columns) | **Accepted** | Event timeline table now includes Equity/FI/Commodity/Crypto impact columns. |
| 2 | "Direction contradiction" deliverable format (structured JSON) | **Accepted** | Added Section 6d "Direction Contradiction Deliverable" with JSON schema. |
| 3 | Scale event timelines for asset-class-specific events | **Accepted** | Addressed via the Master Event Database in the Multi-Indicator Scaling Protocol (macro + sector + indicator layers). |
| 4 | Clarify whether Ray validates direction before or after Vera charts | **Accepted** | Added clarification in Defense 2 Section 3: Vera charts from Evan's metadata (v1), Ray validates subsequently, Vera revises if contradiction (v2). No serial dependency. |

#### From AppDev Ace's Review

| # | Suggestion | Disposition | Rationale |
|---|-----------|:-----------:|-----------|
| 1 | Narrative scaling strategy (one per indicator + per-pair addenda) | **Accepted** | Added "Narrative Scaling Strategy" in Multi-Indicator Scaling Protocol with three tiers. |
| 2 | Single canonical glossary | **Accepted** | Added "Canonical Glossary" section with JSON format for portal loading. |
| 3 | Portfolio-level storytelling arc | **Accepted** | Added to Narrative Scaling Strategy as Tier 3 deliverable. |

#### From My Own Review (Section 4 — Blind Spots)

| # | Suggestion | Disposition | Rationale |
|---|-----------|:-----------:|-----------|
| 1 | Indicator type classification guide | **Accepted** | Added as Section 4b with decision tree and borderline rulings table. |
| 2 | Template for category recommendations | **Accepted** | Enhanced the rationale column format in the brief template. |
| 3 | Target-class-specific research brief templates | **Partially accepted** | Addressed via the tiered brief strategy rather than separate templates — the tier determines depth, not separate template variants. Full template variants would add complexity without proportional benefit. |
| 4 | Batch literature review strategy | **Accepted** | Added "Tiered Literature Review Strategy" table in Multi-Indicator Scaling Protocol. |
| 5 | Spec memo batching protocol | **Accepted** | Added "Batch Spec Memo Protocol" section — deliver by indicator, not by pair. |
| 6 | Direction determination workflow | **Accepted** | Added as Section 6b with 4-step decision tree and conditional logic format. |
| 7 | Scalable event timeline production | **Accepted** | Added "Master Event Database" with layered architecture (macro + sector + indicator). |

### Summary of SOP Changes

Total suggestions received: 17 (3 from Dana, 4 from Evan, 4 from Vera, 3 from Ace, 7 from self)
Accepted in full: 16
Partially accepted: 1 (target-class-specific templates — addressed via tiered approach instead)
Rejected: 0

New SOP sections added:
- Section 4b: Indicator Type Classification
- Section 6b: Direction Determination Workflow
- Section 6c: Cross-Pair Direction Consistency Check
- Section 6d: Direction Contradiction Deliverable
- Multi-Indicator Scaling Protocol (Tiered Review, Batch Spec Memos, Narrative Scaling, Canonical Glossary, Master Event Database, Batch Direction Annotations)

Enhanced existing sections:
- Recommended Analysis Categories (rationale depth)
- Event Timeline (target-class impact columns, CSV delivery)
- Recommended Data Sources (CSV delivery)
- Data Availability Risk Matrix (new subsection in brief template)
- Quality Gates (11 new checklist items)
- Anti-Patterns (6 new items)
- Defense 2 (direction validation sequencing clarification)
