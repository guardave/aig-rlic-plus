# Team Standards — aig-rlic-plus

**Single source of truth for cross-agent conventions.** Individual agent SOPs reference this file rather than duplicating its content. When a convention changes, it changes here; SOP cross-references stay valid.

**Status:** Wave 10F skeleton. Sections marked `[TO BE POPULATED BY CROSS-REVIEW]` will be filled by the parallel agent audit dispatched on 2026-04-20. Expected outcome: resolution of naming, sidecar, palette, and handoff conflicts surfaced during Vera's VIZ-IC1 retro-apply attempt.

Read order for every agent at SOD (see `.claude/commands/sod.md`): this file → your own SOP → `sop-changelog.md` entries since `last_seen`.

---

## 1. Directory Layout

| Path | Owner | Purpose |
|------|-------|---------|
| `results/{pair_id}/` | Evan | Econometrics outputs per pair (signals parquet, winner summary, tournament CSV, interpretation metadata) |
| `data/` | Dana | Raw & cleaned datasets |
| `output/charts/{pair_id}/plotly/` | Vera | Plotly chart JSONs per pair |
| `app/pages/` | Ace | Streamlit portal pages (thin wrappers per APP-PT1) |
| `app/components/page_templates.py` | Ace | Page template functions |
| `app/pair_configs/{pair_id}_config.py` | Ace (structure) + Ray (narrative prose) | Pair-specific config |
| `docs/agent-sops/*.md` | Lead + authors | Per-agent SOPs |
| `docs/schemas/*.json` | varies | Contract-file schemas |
| `docs/team-standards.md` | Lead | This file — cross-agent conventions |
| `docs/sop-changelog.md` | Lead | Append-only change log |
| `_pws/<role>-<name>/` | each agent | Project workspace per agent |
| `~/.claude/agents/<role>-<name>/` | each agent | Global profile (cross-project) |
| `scripts/hooks/` | Lead | Harness hooks (SOD / EOD audit) |

---

## 2. Filename Conventions

### 2.1 Chart JSONs

`[TO BE POPULATED BY CROSS-REVIEW]` — resolve bare-name vs pair-prefixed convention. Current state: HY-IG v2 has both; indpro_xlp & umcsent_xlv have bare-name only. VIZ-NM1 declares bare-name canonical; this file needs to mandate deprecation of prefixed duplicates.

### 2.2 Parquet and CSV artifacts

Pattern: `results/{pair_id}/signals_{yyyymmdd}.parquet`, `results/{pair_id}/tournament_results_{yyyymmdd}.csv`, `results/{pair_id}/stationarity_tests_{yyyymmdd}.csv`. Dates resolved at load time via glob (`sorted(...glob(...))[-1]`) to avoid hardcoding.

### 2.3 Pair pages

`app/pages/{N}_{pair_id}_{section}.py` where `{section}` ∈ `story | evidence | strategy | methodology`. N is a display-order integer (see pair registry).

---

## 3. Sidecar Schema

`[TO BE POPULATED BY CROSS-REVIEW]` — canonicalise `_meta.json` vs `_manifest.json`. Current state: Vera uses `_meta.json` for HY-IG v2 bare-name charts only; indpro_xlp and umcsent_xlv have no sidecars. Evan uses `_manifest.json` for dataset sidecars. Need one name per artifact type, documented here.

Proposed (to confirm via cross-review):
- **Chart sidecars:** `{chart_name}_meta.json` — Vera-owned, per VIZ-V8
- **Dataset sidecars:** `{artifact}_manifest.json` — Evan-owned, per ECON-DS2

---

## 4. Color Palette & Role Aliases

Canonical palette file: `docs/schemas/color_palette_registry.json` (`okabe_ito_2026`).

Current role keys: `primary_data_trace`, `secondary_data_trace`, `equity_curve`, `drawdown_fill`, `quartile_gradient`, `nber_shading`.

`[TO BE POPULATED BY CROSS-REVIEW]` — add semantic role aliases so VIZ-IC1's palette conformance check (which expects `indicator` / `target` / `benchmark`) is verifiable. Proposed mapping:
- `indicator` → `primary_data_trace`
- `target` → `secondary_data_trace`
- `benchmark` → `equity_curve` (or new key if visually distinct)

Confirm or revise via cross-review.

---

## 5. Cross-Agent Handoff Contracts

### 5.1 Producer → consumer artifact registry

| Artifact | Producer | Consumer(s) | Schema | Rule |
|----------|----------|-------------|--------|------|
| `winner_summary.json` | Evan | Ace (Strategy page), Quincy | `docs/schemas/winner_summary.schema.json` | ECON-H5 / APP-WS1 |
| `signal_scope.json` | Evan | Ace (Methodology), Vera, Quincy | `docs/schemas/signal_scope.schema.json` | ECON-SD / APP-SS1 |
| `interpretation_metadata.json` | Dana | Evan, Ray, Ace, Quincy | `docs/schemas/interpretation_metadata.schema.json` | DATA-D6 |
| `signals_{date}.parquet` | Evan | Ace (APP-SE1) | column names match tournament CSV `signal_code` | Derived Signal Persistence + ECON-DS2 |
| `chart_{name}.json` + `chart_{name}_meta.json` | Vera | Ace | `docs/schemas/chart_type_registry.json` | VIZ-V8 / VIZ-IC1 |
| `analyst_suggestions.json` | Evan (+ Ray edits) | Ace (Methodology), Quincy | `docs/schemas/analyst_suggestions.schema.json` | ECON-AS |
| narrative prose (in `pair_configs/`) | Ray | Ace (renders), Quincy (verifies) | no schema; RES-NR1 accuracy rule | RES-NR1 / META-RYW |

### 5.2 Deploy-required artifacts (git-committed, Cloud-readable)

Per ECON-DS2. Every new pair must have these in `git ls-files results/{pair_id}/`:
- `signals_*.parquet` (at least one dated)
- `winner_summary.json`
- `signal_scope.json`
- `interpretation_metadata.json`
- `tournament_results_*.csv`
- `analyst_suggestions.json` (may be empty array)

GATE-29 (QA) verifies this list exists in clean checkout.

---

## 6. Global Agent Profile Files

Per agent at `~/.claude/agents/<role>-<name>/`:

| File | Purpose | Updated when |
|------|---------|--------------|
| `profile.md` | Identity & capabilities | Onboarding / role change |
| `experience.md` | Cross-project patterns | Every wave (EOD) |
| `memories.md` | Dated incident log | Every wave (EOD) |
| `last_seen` | UTC timestamp of most recent SOD | Every SOD |
| `projects/<project>.md` | Per-project summary | Every wave |

Enforcement: META-AM (mandated updates) + PostToolUse hook (audit) + QA-CL3 (verify).

---

## 7. Dispatch Template (Lead → subagent)

Minimum valid dispatch prompt:

```
AGENT_ID: <role>-<name>

<task description>

## SOD Block
<per section 7 of .claude/commands/sod.md>

## MANDATORY EOD
<per team-coordination.md §Mandatory EOD block>
```

PreToolUse hook checks SOD block; PostToolUse hook checks EOD compliance.

---

## 8. Cross-References

- `.claude/commands/sod.md` — project-local SOD procedure
- `docs/agent-sops/team-coordination.md` — full cross-agent protocol
- `docs/sop-changelog.md` — rule additions/changes log
- `scripts/hooks/check-agent-sod.sh`, `scripts/hooks/check-agent-eod.sh` — harness enforcement
