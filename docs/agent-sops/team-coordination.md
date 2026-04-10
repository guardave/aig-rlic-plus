# Team Coordination Protocol

## Overview

This document defines how agents on the AIG-RLIC+ team coordinate work, hand off outputs, and resolve issues. All agents should read this document at session start alongside their individual SOP.

## Team Structure

```
                       Lesandro (Lead Analyst)
                    ┌────────┼────────┐
                    │        │        │
              ┌─────┴──┐  ┌─┴───┐  ┌─┴──────────┐
              │Research │  │Data │  │Econometrics │
              │  Ray    │  │Dana │  │   Evan      │
              └────┬────┘  └──┬──┘  └──────┬──────┘
                   │          │            │
                   │          └─────┬──────┘
                   │          ┌─────┴──────┐
                   │          │Visualization│
                   │          │    Vera     │
                   │          └──────┬──────┘
                   │                 │
                   └────────┬────────┘
                       ┌────┴─────┐
                       │ App Dev  │
                       │   Ace    │
                       └──────────┘
```

**Lesandro** (lead) assigns tasks, reviews outputs, and makes final decisions on methodology and interpretation.
**Ace** (app dev) is the integration point — assembles all outputs into the Streamlit portal.

## Standard Task Flow

A typical analysis follows this sequence:

```
1. Lesandro frames the question and creates tasks
2. Research agent gathers literature and context    ──┐
3. Data agent sources and cleans datasets            ──┤ (parallel)
4. Econometrics agent specifies and estimates models  ←┘ (after 2 & 3)
5. Visualization agent produces charts and tables     ← (after 4)
6. App dev assembles portal with narrative + visuals  ← (after 5, with input from 2 & 3)
7. Browser verification (headless inspect + fix)      ← (after 6)
8. Deliverables completeness gate                     ← (after 7)
9. MRA: Measure, Review, Adjust                       ← (after 8)
10. Lesandro reviews, interprets, and delivers final output
```

Steps 2 and 3 run in parallel. Steps 4, 5, and 6 are sequential dependencies.
Ace can begin scaffolding the portal structure during steps 2-4 while waiting for final outputs.

## Deliverables Completeness Gate (Step 8)

After browser verification confirms rendering quality, verify that **all deliverables exist** by reconciling against the Analysis Brief Section 9 checklist.

### Why This Is Mandatory

Pair #2 (TED Variants) shipped without a Methodology page because:
- The Analysis Brief listed 4 portal pages, but no one verified all 4 were created
- Browser verification checked rendering quality, not content completeness
- The developer consciously skipped Methodology as a "shortcut" — which a completeness gate would have caught

### Minimum Deliverables Per Pair

Every completed pair must have **all** of the following. Missing any one blocks completion.

| # | Deliverable | Verify How |
|---|------------|-----------|
| 1 | Analysis Brief | `docs/analysis_brief_{id}_{date}.md` exists |
| 2 | Master dataset | `data/{id}_*.parquet` exists, row count > 0 |
| 3 | Stationarity tests | `results/{id}/stationarity_tests_*.csv` exists |
| 4 | Interpretation metadata | `results/{id}/interpretation_metadata.json` exists |
| 5 | Exploratory results | `results/{id}/exploratory_*/correlations.csv` exists |
| 6 | Core model results | `results/{id}/core_models_*/*.csv` — at least 3 files |
| 7 | Tournament results | `results/{id}/tournament_results_*.csv` exists, rows > 0 |
| 8 | Charts | `output/charts/{id}/plotly/*.json` — at least 5 files |
| 9 | Portal: Story page | `app/pages/*_{id}_story.py` or shared page exists |
| 10 | Portal: Evidence page | `app/pages/*_{id}_evidence.py` or shared page exists |
| 11 | Portal: Strategy page | `app/pages/*_{id}_strategy.py` or shared page exists |
| 12 | Portal: Methodology page | `app/pages/*_{id}_methodology.py` or shared page exists |
| 13 | Sidebar navigation | Finding appears in sidebar dropdown |
| 14 | Landing card | Pair appears in dashboard card grid |
| 15 | Catalog status | `docs/priority-combinations-catalog.md` updated to "Completed" |
| 16 | Winner summary | `results/{id}/winner_summary.json` exists, all required fields populated (signal, threshold, strategy display names, OOS metrics) |
| 17 | Winner trade log | `results/{id}/winner_trade_log.csv` exists, rows > 0, columns: `entry_date`, `exit_date`, `direction`, `holding_days`, `trade_return_pct` |
| 18 | Execution notes | `results/{id}/execution_notes.md` exists, non-empty, includes step-by-step execution guidance |

**Evidence:** HY-IG (pair #5) shipped with a header-only trade log (0 data rows) because items 16–18 were not in the completeness gate. The downstream execution panel showed "Trade log pending" with no data. Nobody caught it until manual inspection.

### Variant Families

When one priority pair spawns multiple variants (e.g., TED → 3 variants), the deliverables above apply to the **shared pages** — but all 4 page types (Story, Evidence, Strategy, Methodology) must still exist. Sharing pages across variants is acceptable; omitting a page type is not.

## Pipeline Self-Containment Contract (Mandatory)

### Why This Exists

HY-IG (pair #5) required 3 separate scripts run in a specific sequence: `data_pipeline_hy_ig_spy.py` → `stage2_core_models.py` → `tournament_backtest.py`. The HMM probability signal (`hmm_2state_prob_stress`) was computed at runtime inside `tournament_backtest.py` but never persisted. When `generate_winner_outputs.py` ran later as a separate process, it could not find the signal — producing an empty trade log. Fragmented pipelines with runtime-only derived signals create invisible dependencies that break downstream consumers.

### The Contract

Every indicator-target pair must have a **single self-contained pipeline script** (`scripts/pair_pipeline_{id}.py`) that produces ALL artifacts needed by downstream consumers. Specifically, the pipeline must:

1. **Source raw data** from external APIs (FRED, Yahoo Finance, etc.)
2. **Compute and persist ALL derived signals** — including HMM probabilities, Markov states, z-scores, composite scores, and any other signal that could become a tournament winner. These must be saved to `results/{id}/signals_{date}.parquet` per the Econometrics SOP Derived Signal Persistence Rule.
3. **Run the tournament** using signals from the persisted file (not in-memory computation)
4. **Run validation** (walk-forward, bootstrap, stress tests, signal decay, transaction costs)
5. **Generate winner outputs**: `winner_summary.json`, `winner_trade_log.csv`, `execution_notes.md`

### What's Allowed Outside the Pipeline

- **Chart generation** (`generate_charts_{id}.py`) may be a separate script — charts are a rendering concern, not a data pipeline concern
- **Portal page creation** — Streamlit page files are developed separately by Ace

### Verification

After the pipeline runs, the following must be true without running any other script:
- Completeness gate items 1–7 and 16–18 are satisfied from `results/{id}/`
- The signals parquet contains all columns referenced in the tournament results CSV
- A fresh clone can regenerate all data by running only the pipeline script (plus API keys)

**Cross-reference:** See Econometrics SOP, "Derived Signal Persistence Rule" for signal-level requirements.

## Iterative Review: Browser Verification (Mandatory After Portal Assembly)

After every portal page is created or modified, a **headless browser inspection** must be performed before the work is considered complete. This catches rendering issues that are invisible in Python code but visible in the browser.

### Why This Is Mandatory

Pair #1 (INDPRO → SPY) revealed two classes of rendering bugs:
1. **Raw HTML in Streamlit:** `st.markdown(unsafe_allow_html=True)` silently fails on nested HTML (e.g., `<div>` with child `<span>` elements). The HTML appears as literal text instead of rendered markup.
2. **Raw Markdown inside HTML blocks:** Markdown headings (`###`) and bold (`**text**`) inside HTML `<div>` wrappers are not rendered by Streamlit — they display as raw syntax.

These bugs are **invisible during development** (the Python code looks correct) and only appear in the browser.

### Verification Protocol

**Tool:** Playwright headless browser (`temp/inspect_portal.py`)

**Steps:**
1. Launch Streamlit app
2. For each page, navigate and wait for render (4-5s for Streamlit hydration)
3. Take full-page screenshot
4. Extract `body` inner text and scan for:
   - Raw HTML tags: `<div`, `<span`, `<b>`, `<br>`, `</h4>`
   - Raw Markdown syntax: lines starting with `###`, `##`, or containing `**text**`
5. If issues found → fix and re-verify
6. Save screenshots for the record

**When to run:**
- After creating new portal pages
- After modifying `components/narrative.py`, `components/charts.py`, or any component that renders HTML
- After updating the landing page layout
- Before committing any portal changes

### Known Streamlit Rendering Rules

| Pattern | Works? | Fix |
|---------|--------|-----|
| `st.markdown("### Heading")` | Yes | Use directly |
| `st.markdown("<div>### Heading</div>", unsafe_allow_html=True)` | **No** — heading shows as raw `###` | Remove HTML wrapper; use `st.markdown("### Heading")` |
| `st.markdown("<div><span>text</span></div>", unsafe_allow_html=True)` | **Unreliable** — may show as raw tags | Use `st.container()` + native Streamlit components |
| `st.metric("Label", value)` in narrow column | Truncates with `...` | Use fewer columns or markdown tables |
| `st.container(border=True)` | Yes | Preferred for card-like layouts |

## MRA: Measure, Review, Adjust (Mandatory After Browser Verification)

After every pair pipeline + portal + browser verification, conduct **MRA** before the work is considered complete. This is Step 8 in the Standard Task Flow.

### Measure

Record quantitative outcomes in `docs/pair_execution_history.md`:

| What to Measure | Where to Record |
|----------------|-----------------|
| Pipeline wall-clock time per stage | Pipeline Timing table |
| Token usage by component | Token Usage Estimate table |
| Econometric results: best Sharpe, direction, significance | Key Results table |
| Tournament stats: combos tested, valid count, benchmark comparison | Key Results table |
| Portal: rendering issues found and fixed | Key Findings section |
| Deviation from previous pair's cost/timing | Cost Projections section |

### Review

Reflect on what worked and what didn't:

- **Econometric:** Direction surprises, model convergence issues, unexpected insignificance
- **Data:** Sourcing failures, frequency mismatches, sample limitations
- **Portal:** Rendering bugs caught by browser, layout issues, chart quality
- **Process:** Pipeline friction, script adaptation difficulty, documentation gaps

### Adjust

Update artifacts based on the review:

| If This Happened | Then Adjust This |
|-----------------|-----------------|
| New rendering rule discovered | Update viz-agent SOP + appdev SOP |
| Pipeline step failed or was slow | Fix template script + document in lessons |
| Econometric method was unhelpful for this indicator type | Note in econometric-methods-catalog Relevance Matrix |
| Token usage significantly off projection | Revise per-pair estimates in execution history |
| New data source challenge | Update data-agent SOP |
| Direction was surprising | Document in interpretation_metadata.json + lessons |

### Documentation

After MRA, update:
1. `docs/pair_execution_history.md` — full MRA section for this pair
2. File-based memory (`~/.claude/projects/.../memory/`) — new lessons file if significant
3. AutoMem knowledge graph — new entities/observations for major findings
4. SOPs — if any rules changed

**No pair is considered complete until MRA is documented.**

## Phase 0: Analysis Brief (Mandatory Gate)

No agent starts work on a new indicator-target analysis without an approved Analysis Brief. The brief is the single source of truth for:
- Research question and hypotheses
- Indicator and target specification (including expected direction)
- Sample design and data requirements
- Method categories (from Relevance Matrix)
- Tournament design parameters (target-class-specific)
- Computational budget
- Portal specifications

**Gate rule:** Lesandro creates or approves the Analysis Brief. Each agent acknowledges receipt and flags domain-specific concerns before proceeding. The brief template is at `docs/analysis_brief_template.md`.

### Brief Acknowledgment Protocol

When the Analysis Brief is issued:

1. **Each agent reads the brief** within one task cycle
2. **Each agent sends a structured acknowledgment:**
   - "I have read the Analysis Brief for {INDICATOR} → {TARGET}"
   - Domain-specific concerns (e.g., Dana: "I16 is quarterly — will use LVCF alignment"; Evan: "Expected direction is ambiguous — will determine empirically")
   - Blockers (e.g., "Cannot source I13 (ABI) — need alternative")
3. **Lesandro reviews all acknowledgments** and resolves any concerns before giving the go-ahead
4. **No agent proceeds past their intake step** until the go-ahead is issued

## Handoff Protocol

Every handoff follows three rules:
1. **Use the structured template** defined in the sender's SOP
2. **Receiver must acknowledge** within one task cycle (silence ≠ acceptance)
3. **Partial delivery is OK** — mark it clearly and include a manifest of what's missing

### Primary Pipeline Handoffs

#### Research Agent → Econometrics Agent (Two-Stage)

**Stage 1 — Quick Spec Memo (deliver ASAP):**
- 5-bullet specification memo: DV, regressors, instruments, pitfalls, sample conventions
- Naming: `docs/spec_memo_{topic}_{date}.md`

**Stage 2 — Full Research Brief:**
- Complete brief with literature synthesis, specification details table, data sources with series IDs, event timeline, references
- Naming: `docs/research_brief_{topic}_{date}.md`

#### Research Agent → Data Agent

- Data source recommendations table (variable, series ID, MCP server, frequency, availability status)
- Included in the research brief; Dana extracts on receipt

#### Data Agent → Econometrics Agent

- Analysis-ready dataset (`.parquet` or `.csv`)
- Data dictionary with Display Name column (variable name, display name, description, source, series ID, unit, transformation, SA status, known quirks)
- Summary statistics
- Stationarity test results (structured table: variable, test, statistic, p-value, lags, conclusion)
- Handoff message using Data-to-Econ template (see Dana's SOP)
- Naming: `data/{subject}_{frequency}_{start}_{end}.parquet`

#### Econometrics Agent → Visualization Agent

- Fitted model results (`.pkl`)
- Coefficient tables (`.csv`) using standardized schema: `variable`, `coef`, `se`, `t_stat`, `p_value`, `ci_lower`, `ci_upper`
- Diagnostic test results (standardized table: test, statistic, p-value, interpretation)
- **Chart Request Template** (chart type, data source path, key variables, main insight sentence, audience, comparison notes, special annotations)
- Naming: `results/{model_name}_{date}.pkl`, `results/{model_name}_coefficients_{date}.csv`

#### Visualization Agent → Lesandro

- Charts (`.png` and `.svg`) with versioning: `_v{N}`
- Formatted tables (`.md` and `.csv`)
- One-line captions for each chart
- Annotation source tracking table
- Naming: `output/{subject}_{chart_type}_{date}_v{N}.{ext}`

### Direct (Non-Pipeline) Handoffs

#### Data Agent → Visualization Agent

- For exploratory charts, data quality plots, descriptive visualizations
- Dataset with Display Name metadata in data dictionary
- Data quirks relevant to visual interpretation
- See Dana's SOP: Data-to-Viz Handoff section

#### Research Agent → Visualization Agent

- Event timeline (date, event, relevance, type) for chart annotations
- Domain visualization conventions from literature
- See Ray's SOP: Event Timeline section

#### Econometrics Agent → Data Agent (Mid-Analysis)

- Expedited single-variable requests during diagnostics
- Must include: variable name, source preference, urgency flag, econometric rationale
- See Evan's SOP: Mid-Analysis Data Requests section

### Portal Assembly Handoffs

#### Visualization Agent → App Dev

- Plotly figure objects (`.json` or Python code) for interactive charts
- Static chart files (`.png`, `.svg`) for fallback
- Chart specifications (data source, key message, caption)
- See Vera's SOP: Output Standards

#### Research Agent → App Dev

- Narrative text sections (markdown) for each portal page
- Section ordering and storytelling arc
- Plain-English interpretation of findings for layperson audience

#### Data Agent → App Dev

- Data refresh pipeline code or specifications
- Cached dataset locations and update frequency
- Data dictionary for any series displayed in the portal

#### Econometrics Agent → App Dev

- Model result summaries for display (key coefficients, diagnostics, strategy performance)
- Backtest results in tabular format
- Regime/signal status for any live indicators

#### App Dev → Lesandro

- Running portal URL (Streamlit Community Cloud)
- Portal architecture documentation
- User guide for content updates

### Interpretation Annotation Handoffs

When the same indicator is analyzed against multiple targets, interpretation may differ (e.g., VIX/VIX3M rising is bearish for SPY but bullish for TLT). The team must coordinate annotations:

1. **Evan** outputs `interpretation_metadata.json` alongside results: `direction` (+1/-1), `mechanism` (plain English), `confidence` (from analysis)
2. **Ray** validates direction against literature; flags contradictions between empirical and theoretical expectations
3. **Vera** renders direction indicators: solid line = pro-cyclical, dashed = counter-cyclical; inline annotations on multi-pair dashboards
4. **Ace** implements "How to Read This" callout box on each pair's page; "Differs From" notes when same indicator has opposite interpretations across targets on the same dashboard

The `expected_direction` field in the Analysis Brief sets the prior; the `interpretation_metadata.json` from Evan records the empirical finding.

## Shared Workspace Structure

```
/workspaces/aig-rlic-plus/
├── app/               # Streamlit portal source code (Ace owns)
│   ├── app.py         # Main Streamlit entry point
│   ├── pages/         # Multi-page app sections
│   ├── components/    # Reusable UI components
│   └── assets/        # Static assets (images, CSS)
├── data/              # Cleaned, analysis-ready datasets
├── results/           # Model outputs, coefficient tables, diagnostics
├── output/            # Final charts, tables, reports
├── docs/              # Research briefs, documentation
│   └── agent-sops/    # This folder — agent SOPs
├── cache/             # Temporary cached data (auto-cleaned)
├── temp/              # Scratch space (auto-archived)
└── scripts/           # Reusable analysis scripts
```

## Acknowledgment Protocol

Every handoff requires a structured acknowledgment from the receiver:

1. **Sender** delivers output using the handoff template from their SOP
2. **Receiver** acknowledges within one task cycle with:
   - What was received (file list)
   - Whether it meets their needs (accepted / accepted with caveats / blocked — specify what's missing)
   - Any questions or follow-ups
3. **If no acknowledgment** within one task cycle, sender follows up explicitly
4. **Silence is never acceptance** — an unacknowledged handoff is an open loop

## Communication Rules

1. **Use TaskList / TaskUpdate** for tracking — do not rely on messages alone
2. **Be explicit about blockers** — if you need input from another agent, say exactly what you need
3. **Deliver incrementally** — a partial dataset now is better than a perfect one late
4. **Flag surprises immediately** — unexpected data patterns, missing series, test failures
5. **Never overwrite another agent's output** — create versioned files with `_v{N}` suffix
6. **Acknowledge every handoff** — confirm receipt and adequacy (see Acknowledgment Protocol above)
7. **Cite upstream contributions** — reference teammates' deliverables by file path in your output

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|---------|
| Dataset | `data/{subject}_{freq}_{start}_{end}.parquet` | `data/macro_panel_monthly_200001_202312.parquet` |
| Research brief | `docs/research_brief_{topic}_{date}.md` | `docs/research_brief_phillips_curve_20260228.md` |
| Model results | `results/{model}_{date}.pkl` | `results/phillips_ols_20260228.pkl` |
| Coefficients | `results/{model}_coefficients_{date}.csv` | `results/phillips_ols_coefficients_20260228.csv` |
| Chart | `output/{subject}_{type}_{date}.png` | `output/us_inflation_line_20260228.png` |
| Table | `output/{subject}_table_{date}.md` | `output/regression_results_table_20260228.md` |

### Branches (if applicable)

- `analysis/{topic}` for analysis work
- `data/{source}` for data pipeline changes
- `docs/{topic}` for documentation updates

## Escalation Rules

| Situation | Action |
|-----------|--------|
| Missing data for a required variable | Data agent flags to Lesandro; suggests alternatives |
| Model diagnostics fail | Econometrics agent reports to Lesandro with proposed fix |
| Conflicting literature findings | Research agent presents both sides; Lesandro decides |
| Chart request is ambiguous | Visualization agent asks econometrics agent for clarification |
| Any agent is blocked for > 1 task cycle | Escalate to Lesandro immediately |

## Quality Standards (Team-Wide)

- Every output file has a descriptive name following the naming convention
- Every handoff includes a structured message using the sender's SOP template
- Every handoff is acknowledged by the receiver within one task cycle
- No agent delivers output without running their quality gate checklist
- All code is reproducible — another agent should be able to re-run it
- Assumptions are documented, not implicit
- Upstream contributions are cited by file path

### Defense 1: Self-Describing Artifacts (Producer Rule)

**Any artifact that crosses an agent boundary must carry enough context that the consumer cannot misinterpret it.** Implicit assumptions — state labels, sign conventions, units, date ranges, return types, merge keys — are the #1 source of silent errors in multi-agent pipelines.

**Concrete requirements for producers:**

1. **Column names encode meaning, not indices.** Never deliver columns named `state_0`, `regime_1`, `cluster_2`. Use `stress_prob`, `calm_prob`, `high_vol_regime`. If a model assigns numeric labels, rename them before saving the output file.

2. **Units are explicit.** Include units in column names (`spread_bps`, `return_pct`, `vol_annualized`) or in a sidecar metadata file. Never assume the consumer knows your unit convention.

3. **Sign conventions are stated.** Document whether positive means "widening" or "tightening", whether a higher value means "more stressed" or "less stressed". If the convention is non-obvious, add a comment in the data dictionary row.

4. **Date/sample boundaries are in the file.** If an artifact is OOS-only, the filename or metadata must say so. Never rely on the consumer knowing your train/test split.

5. **Sidecar manifest for model artifacts.** Every `.pkl` or `.parquet` model output must be accompanied by a `_manifest.json` that documents: what each column/variable means, what higher/lower values signify, and at least one sanity-check assertion (see Defense 2).

**Why this matters:** When Vera receives `prob_state_0` and `prob_state_1`, she must guess which is stress. If Evan delivers `prob_stress` and `prob_calm`, guessing is impossible. This principle applies to every handoff, not just HMM states — it covers sign conventions, return types (arithmetic vs geometric), threshold directions, and any other implicit assumption.

### Defense 2: Reconciliation at Every Boundary (Consumer + Reviewer Rule)

**Every agent that consumes an upstream artifact must verify that their interpretation produces results consistent with the upstream agent's reported numbers.** Gate reviewers must run automated numerical reconciliation, not just structural checks.

**Concrete requirements:**

**For consumers (Vera, Ace, or any downstream agent):**

1. **Sanity-check on ingestion.** Before using any upstream data, verify at least one known fact. Examples:
   - "During GFC (2008-09), stress probability should be > 0.8" (Example — adjust assertion to match the specific indicator-target pair)
   - "Tournament winner Sharpe should match the value reported in the Analysis Brief's tournament results"
   - "B&H max drawdown should be consistent with the target's historical volatility profile (see Analysis Brief, Section 4)"
   These checks are derived from the upstream agent's summary or handoff message. If the check fails, STOP and ask — do not proceed with a guess.

2. **Cross-check derived outputs against source.** If you compute a drawdown curve from raw data, the max drawdown of that curve must match the number reported in the upstream results CSV (within rounding). If it doesn't, your interpretation of the data is wrong.

3. **When in doubt, verify with a known period.** Pick a well-understood historical episode (GFC, COVID) and confirm your derived series behaves as expected during that period. This catches sign inversions, unit errors, and state label swaps generically.

**For gate reviewers (Lesandro):**

4. **Automated reconciliation script.** Before signing off on any gate, run a script that compares every number displayed in the portal/charts against the source CSV/parquet. This is not optional spot-checking — it is a systematic check that every displayed number traces back to the ground truth.

5. **Reconciliation covers derived quantities.** Don't just check that "Sharpe = 1.17" appears correctly. Recompute the Sharpe from the equity curve data in the chart and verify it matches. This catches errors in the derivation, not just the label.

**Template for a reconciliation script:**

```python
# gate_reconciliation.py — mandatory before Gate 3/4 sign-off
import json, pandas as pd

def reconcile_chart(chart_name, check_fn, tolerance=0.02):
    """Load a chart JSON and run a numerical check against ground truth."""
    with open(f'output/charts/plotly/{chart_name}.json') as f:
        fig = json.load(f)
    result = check_fn(fig)
    assert result, f"RECONCILIATION FAILED: {chart_name}"
    print(f"  OK  {chart_name}")

# Example checks:
# 1. Drawdown chart W1 MDD must match tournament CSV
# 2. Equity curve final value must be consistent with reported annualized return
# 3. HMM stress probability must be high during GFC, low during 2013-2014
# 4. KPI card numbers must match tournament CSV
# ... add one check per chart
```

**Why this matters:** Structural reviews (files exist, parse OK, titles are good) catch ~20% of errors. Numerical reconciliation catches the remaining ~80% — the silent errors where the chart looks plausible but shows the wrong data. The cost of writing these checks is low; the cost of shipping wrong charts is high.

## Task Completion Hooks (Team-Wide Standard)

Every agent must run these two hooks when completing any task. Individual SOPs contain role-specific details; these are the universal minimums.

### Hook 1: Validation & Verification (before marking task done)

1. **Re-read the original request** — does the deliverable actually answer what was asked?
2. **Run your Quality Gates checklist** — every box must be checked
3. **Self-review** — read your output as if you were the receiving agent. Would you accept this?
4. **Verify file naming and location** — follows conventions, saved to correct workspace directory
5. **Send structured handoff message** — use the template from your SOP
6. **Request acknowledgment** — explicitly ask the receiver to confirm

### Hook 2: Reflection & Memory (after every completed task)

1. **What went well? What was harder than expected?**
2. **Did any handoff friction occur?** Note it for SOP improvement
3. **Did you learn something reusable?** (data gotcha, method insight, tool trick, collaboration pattern)
4. **Distill 1-2 key lessons** and update your memories file at `~/.claude/agents/{your-id}/memories.md`
5. **Cross-project lessons** go to `~/.claude/agents/{your-id}/experience.md`
6. **If a lesson affects another agent's workflow**, message them directly — don't assume they'll discover it

These hooks are not optional. They are the mechanism by which the team improves over time. Skipping them to save time is a false economy — the cost shows up as repeated mistakes and handoff friction in future tasks.

## New Agent Onboarding Protocol

When a new agent joins the team (or when the team is first formed), run this cross-review exercise before starting real work:

### Step 1: Cross-Review SOPs
Every agent reads ALL teammates' SOPs plus the team coordination protocol. Each writes a structured review covering:
1. What I learned about each teammate's workflow and pressures
2. Where our handoffs connect and where friction could arise
3. Suggestions for each teammate's SOP (empathy, rapport, handoff clarity)
4. Suggestions for my own SOP (blind spots revealed by reading others')
5. Suggestions for the team coordination protocol

Reviews are saved to `docs/agent-sops/reviews/{agent-id}-review.md`.

### Step 2: Self-Update SOPs
Each agent incorporates the best feedback into their own SOP. Ownership matters — you update your own SOP, not someone else's.

### Step 3: Distill and Remember
Each agent distills key lessons into:
- `~/.claude/agents/{agent-id}/memories.md` (gotchas, insights, commitments)
- `~/.claude/agents/{agent-id}/experience.md` (cross-project patterns)

### Why This Matters
Reading teammates' SOPs reveals handoff gaps, duplicated work, and blind spots that no amount of solo work surfaces. This is not optional — it is the single highest-leverage activity for team cohesion. Do it for every new team or whenever the team composition changes.

---

## Indicator Evaluation Framework

### Purpose

Integrate the Indicator Evaluation Layer into the multi-agent workflow. This layer provides a structured framework for evaluating how indicators interact with market environments and strategy performance.

### Artifacts

- `environment_interaction_scores.json`
- `strategy_survival_scores.json`

### Coordination Responsibilities

- Ensure evaluation-layer tasks are properly assigned across agents (Data validates schema, Econ supplies evidence, Research provides grounding, Viz renders radars, AppDev integrates into portal)
- Monitor completion and integration of evaluation components
- Maintain clear communication between all agents on evaluation-layer deliverables
- Evaluation-layer work follows the same Phase 0 → MRA pipeline as pair analysis

---

## Retrospective

After completing a major analysis (not after every task), the team lead (Lesandro) convenes a brief retrospective:

1. Each agent reviews their Input Quality Log / memories for recurring friction
2. Top 3 improvement suggestions are collected
3. SOPs are updated by their respective owners
4. Team coordination protocol is updated if cross-cutting changes are needed
5. Learnings are promoted to global experience files if cross-project applicable

### Run Registry

The team maintains a "Registered Analysis Runs" table in the Reference Catalogs Index (`docs/reference-catalogs-index.md`). Every completed indicator-target analysis is registered there with: pair ID, date completed, lead agent, and link to results. This is the single source of truth for what has been analyzed.
