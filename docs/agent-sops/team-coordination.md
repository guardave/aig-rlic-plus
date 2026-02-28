# Team Coordination Protocol

## Overview

This document defines how agents on the AIG-RLIC+ team coordinate work, hand off outputs, and resolve issues. All agents should read this document at session start alongside their individual SOP.

## Team Structure

```
                    Alex (Lead Analyst)
                    ┌───────┼───────┐
                    │       │       │
              ┌─────┴──┐  ┌┴────┐  ┌┴──────────┐
              │ Research │  │Data │  │Econometrics│
              │  Agent   │  │Agent│  │   Agent    │
              └─────────┘  └──┬──┘  └─────┬──────┘
                              │            │
                              └─────┬──────┘
                              ┌─────┴──────┐
                              │Visualization│
                              │    Agent    │
                              └────────────┘
```

**Alex** (lead) assigns tasks, reviews outputs, and makes final decisions on methodology and interpretation.

## Standard Task Flow

A typical analysis follows this sequence:

```
1. Alex frames the question and creates tasks
2. Research agent gathers literature and context    ──┐
3. Data agent sources and cleans datasets            ──┤ (parallel)
4. Econometrics agent specifies and estimates models  ←┘ (after 2 & 3)
5. Visualization agent produces charts and tables     ← (after 4)
6. Alex reviews, interprets, and delivers final output
```

Steps 2 and 3 run in parallel. Steps 4 and 5 are sequential dependencies.

## Handoff Protocol

### From Data Agent → Econometrics Agent

**Deliverables:**
- Analysis-ready dataset (`.parquet` or `.csv`)
- Data dictionary (variable names, descriptions, sources, transformations)
- Summary statistics
- Stationarity test results (if time-series)

**Naming:** `data/{subject}_{frequency}_{start}_{end}.parquet`

### From Research Agent → Econometrics Agent

**Deliverables:**
- Research brief (markdown)
- Recommended model specifications from the literature
- Suggested instruments or identification strategies (if relevant)

**Naming:** `docs/research_brief_{topic}_{date}.md`

### From Econometrics Agent → Visualization Agent

**Deliverables:**
- Fitted model results (`.pkl` for model objects, `.csv` for coefficient tables)
- Diagnostic test results (markdown table or `.csv`)
- Specification of what charts/tables are needed
- Interpretation notes (what the chart should highlight)

**Naming:** `results/{model_name}_{date}.pkl`, `results/{model_name}_coefficients_{date}.csv`

### From Visualization Agent → Alex

**Deliverables:**
- Charts (`.png` and `.svg`)
- Formatted tables (`.md` and `.csv`)
- One-line captions for each chart

**Naming:** `output/{subject}_{chart_type}_{date}.{ext}`

## Shared Workspace Structure

```
/workspaces/aig-rlic-plus/
├── data/              # Cleaned, analysis-ready datasets
├── results/           # Model outputs, coefficient tables, diagnostics
├── output/            # Final charts, tables, reports
├── docs/              # Research briefs, documentation
│   └── agent-sops/    # This folder — agent SOPs
├── cache/             # Temporary cached data (auto-cleaned)
├── temp/              # Scratch space (auto-archived)
└── scripts/           # Reusable analysis scripts
```

## Communication Rules

1. **Use TaskList / TaskUpdate** for tracking — do not rely on messages alone
2. **Be explicit about blockers** — if you need input from another agent, say exactly what you need
3. **Deliver incrementally** — a partial dataset now is better than a perfect one late
4. **Flag surprises immediately** — unexpected data patterns, missing series, test failures
5. **Never overwrite another agent's output** — create versioned files if updating

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
| Missing data for a required variable | Data agent flags to Alex; suggests alternatives |
| Model diagnostics fail | Econometrics agent reports to Alex with proposed fix |
| Conflicting literature findings | Research agent presents both sides; Alex decides |
| Chart request is ambiguous | Visualization agent asks econometrics agent for clarification |
| Any agent is blocked for > 1 task cycle | Escalate to Alex immediately |

## Quality Standards (Team-Wide)

- Every output file has a descriptive name following the naming convention
- Every handoff includes a brief message describing what's being delivered
- No agent delivers output without running their quality gate checklist
- All code is reproducible — another agent should be able to re-run it
- Assumptions are documented, not implicit
