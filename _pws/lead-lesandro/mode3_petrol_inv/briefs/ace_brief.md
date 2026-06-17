[App Dev Ace] — Mode-3 maker dispatch — pair `petrol_inv_spy`

You are App Dev Ace. Resolve persona via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOP `docs/agent-sops/appdev-agent-sop.md`, and `~/.claude/agents/appdev-ace/`. Lead Lesandro (Claude) is manager + sole checker.

## Inputs (all VERIFIED by Lead, committed)
- Config template: `app/pair_configs/busloans_spy_config.py`.
- Page template: `app/pages/17_busloans_spy_{story,evidence,strategy,methodology}.py`.
- Econ results: `results/petrol_inv_spy/` (winner_summary.json is the source of truth for headline numbers).
- Charts: `output/charts/petrol_inv_spy/plotly/` (20 charts pass, meta sidecars present).
- Narrative: `docs/portal_narrative_petrol_inv_spy_20260617.md` (Story/Evidence/Strategy/Methodology — use its prose & section structure).
- interpretation_metadata.json (fully populated by Dana/Evan/Ray).
- Vera+Ray handoff: `_pws/lead-lesandro/mode3_petrol_inv/vera_ray_handoff.md`.

## Task — assemble the portal for petrol_inv_spy
1. Create `app/pair_configs/petrol_inv_spy_config.py` mirroring the busloans config structure (pair_id, display names, chart manifest, section content wiring, KPIs, evidence_status routing). Pull headline numbers from winner_summary.json — do NOT hardcode divergent values. Honor found_in_search labeling (DPS-FE2): "Search-phase OOS Sharpe (no holdout final exam yet)".
2. Create the 4 pages with **page-numeric prefix 18**:
   `app/pages/18_petrol_inv_spy_{story,evidence,strategy,methodology}.py`.
3. Register the pair in `app/components/pair_registry.py` (add `"petrol_inv_spy": "pages/18_petrol_inv_spy",` near line 104) and any display-name map. Confirm it appears on the landing card grid.
4. Leaderboard / combination counts: use the BENCHMARK-excluded count (5123 valid of 7392) — NEVER `len(tdf)`. (APP count-bug precedent.)

## Binding gates
- **META-CMP pre-commit gates must pass** (T1.1 schema, T1.2 loader smoke — will run since app/ files are staged, T1.3 filename, T2 chart completeness). Fix at source if any fail.
- Chart→method-block wiring: right chart attached to right section (LEAD-DOM1 spirit — the Strategy tab's confidence block and Evidence method blocks must reference the correct charts).
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.

## Conventions
- Run from repo root, project Python. Commit your portal files (META-CMP gates run on commit).
- Write handoff `_pws/lead-lesandro/mode3_petrol_inv/ace_handoff.md` (files created, registry line, local slug list for cloud verify: `petrol_inv_spy_{story,evidence,strategy,methodology}`).
- Print `ACE DONE` at line start when finished (+ files list), or `ACE BLOCKED: <reason>`.

Begin now.
