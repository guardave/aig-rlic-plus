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

### 2.1 Chart JSONs — bare-name canonical (Wave 10F ratification)

**Canonical form:** `output/charts/{pair_id}/plotly/{chart_type}.json` — bare-name only. `{chart_type}` is the short key from the Standard Chart Set (e.g. `hero`, `correlations`, `ccf`, `regime_stats`, `equity_curves`, `drawdown`, `walk_forward`, `tournament_scatter`, `rolling_sharpe`, `signal_dist`). The pair_id lives in the directory path, NEVER prefixed into the filename. This is VIZ-NM1 promoted to team standard.

**Deprecated:** pair-prefixed duplicates like `hy_ig_v2_spy_hero.json` alongside `hero.json`. HY-IG v2 currently carries 13-14 such duplicates on disk — scheduled for deletion. `indpro_xlp` and `umcsent_xlv` bare-name files were produced under a different path (some prefixed, some not); pending Vera migration sweep (next wave).

**Loader contract:** `app/components/charts.py::load_plotly_chart(chart_name, pair_id)` resolves bare-name only. The pair-prefix fallback at `charts.py:106-113` is a live violation of VIZ-NM1 — scheduled for removal in the next Ace dispatch.

**Enforcement:** producer-side pre-commit hook (to be implemented — currently a planned follow-up) asserts every file under `output/charts/{pair_id}/plotly/` matches the registry pattern in `docs/schemas/chart_type_registry.json`. A pair-prefixed filename is a commit failure.

**Unanimous cross-review consensus** (Dana, Evan, Vera, Ray, Ace, Quincy — 2026-04-20).

### 2.2 Parquet and CSV artifacts

Pattern: `results/{pair_id}/signals_{yyyymmdd}.parquet`, `results/{pair_id}/tournament_results_{yyyymmdd}.csv`, `results/{pair_id}/stationarity_tests_{yyyymmdd}.csv`. Dates resolved at load time via glob (`sorted(...glob(...))[-1]`) to avoid hardcoding.

### 2.3 Pair pages

`app/pages/{N}_{pair_id}_{section}.py` where `{section}` ∈ `story | evidence | strategy | methodology`. N is a display-order integer (see pair registry).

---

## 3. Sidecar Schema — two names, two owners, two artifact classes (Wave 10F ratification)

The split is deliberate and authoritative. Different artifacts, different owners, different content shapes — they do NOT share a filename.

| Artifact class | Sidecar filename pattern | Owner | Primary content |
|---------------|-------------------------|-------|----------------|
| Chart JSON | `output/charts/{pair_id}/plotly/{chart_name}_meta.json` | Vera (VIZ-V8) | `palette_id`, `rules_applied`, `narrative_alignment_note`, `method_name`, `expected_chart_type`, VIZ-IC1 lint results |
| Dataset / model output | `data/{artifact}_manifest.json` or `results/{pair_id}/{artifact}_manifest.json` | Dana (data), Evan (econometrics model outputs) | column semantics, sign conventions, units, sanity-check assertions (Defense 1) |

**Why two names:** a chart sidecar and a dataset sidecar are consumed at different times, by different agents, with different schemas. Forcing one filename would require a discriminator inside the JSON, which is a worse contract than a filename that already encodes the artifact class.

**The Wave 10F drafting slip that triggered this ratification:** `visualization-agent-sop.md:962` (VIZ-IC1 §6) originally wrote `_manifest.json` for a chart sidecar — contradicting VIZ-V8 which declares `_meta.json`. Fixed 2026-04-22; see sop-changelog.md entry.

**Enforcement:** chart sidecar schema at `docs/schemas/chart_sidecar.schema.json` (to be created — planned follow-up). Dataset manifest schema already exists per ECON-DS2 / DATA-D-series rules.

**Unanimous cross-review consensus** (Dana, Evan, Vera, Ray, Ace, Quincy — 2026-04-20).

---

## 4. Color Palette & Role Aliases — Wave 10F ratification (v1.1.0)

**Canonical palette file:** `docs/schemas/color_palette_registry.json` (palette `okabe_ito_2026`). Bumped to `x-version: 1.1.0` on 2026-04-22.

**Semantic role aliases → visual keys** (added Wave 10F via `aliases` block inside `okabe_ito_2026`):

| Semantic alias | Resolves to | Hex | Used for |
|----------------|------------|-----|----------|
| `indicator` | `primary_data_trace` | `#D55E00` (Okabe-Ito vermillion) | The pair's indicator series (left-axis indicator — e.g. HY-IG spread, INDPRO YoY) |
| `target` | `secondary_data_trace` | `#0072B2` (Okabe-Ito blue) | The pair's target series (right-axis target — e.g. XLP, XLV, SPY when it IS the target) |
| `benchmark` | `benchmark_trace` | `#6C7A89` (muted slate) | Reference / buy-and-hold comparison when distinct from the strategy's own equity curve |

**Why `benchmark_trace` is a new visual key (not reuse of `equity_curve`):** on a chart that displays the strategy's own equity curve AND a buy-and-hold benchmark (common on Strategy pages), reusing `equity_curve` for both collapses them to one color. The Wave 10F cross-review consensus (3 of 6 — Dana, Evan, Quincy) was to give `benchmark` its own visually-distinct registry key. Muted slate (`#6C7A89`) reads as "reference, not star" against the Okabe-Ito foreground palette and preserves colorblind safety.

**Deferred:** per-asset-class benchmark variants (`benchmark_equity`, `benchmark_fixed_income`, `benchmark_commodity`) per Ray's Wave 10F nuance — held until the portal hosts non-equity pairs, since today the distinction would be speculative.

**Consumption pattern (VIZ-IC1 §4):** Vera's chart-save pipeline resolves `indicator` / `target` / `benchmark` aliases to hex by reading the registry at save time. Ad-hoc hex codes are prohibited. Legacy keys (`primary_data_trace`, `equity_curve`, etc.) remain usable directly — aliases are additive, not replacing.

**Cross-references:** VIZ-V11 (registry source rule), VIZ-IC1 (consumption + pre-save lint), ECON-UD (`signal_scope.json` semantics that drive which role each column gets).

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
