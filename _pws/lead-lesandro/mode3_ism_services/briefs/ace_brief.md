[App Dev Ace] — Mode-3 maker dispatch — pair `ism_services_spy`

You are App Dev Ace. Resolve persona via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOP `docs/agent-sops/appdev-agent-sop.md`, and `~/.claude/agents/appdev-ace/`. Lead Lesandro (Claude) is manager + sole checker.

## Inputs (all VERIFIED by Lead, committed)
- Config template: `app/pair_configs/petrol_inv_spy_config.py` (most recent pattern).
- Page template: `app/pages/18_petrol_inv_spy_{story,evidence,strategy,methodology}.py`.
- Econ results: `results/ism_services_spy/` (winner_summary.json is source of truth for headline numbers).
- Charts: `output/charts/ism_services_spy/plotly/` (22 charts pass, meta sidecars present; 2 justified chart_skip files).
- Narrative: `docs/portal_narrative_ism_services_spy_20260618.md` (Story/Evidence/Strategy/Methodology — use its prose & section structure, including the "Why This Is Not a Leading Signal" and "Lead With Causality" sections).
- interpretation_metadata.json (fully populated by Dana/Evan/Ray).
- Vera+Ray handoff: `_pws/lead-lesandro/mode3_ism_services/vera_ray_handoff.md`.

## Task — assemble the portal for ism_services_spy
1. Create `app/pair_configs/ism_services_spy_config.py` mirroring the petrol config structure (pair_id, display names, chart manifest, section content wiring, KPIs, evidence_status routing). Pull headline numbers from winner_summary.json — do NOT hardcode divergent values. Honor found_in_search labeling (DPS-FE2): e.g. "Search-phase OOS Sharpe (no holdout final exam yet)".
2. Create the 4 pages with **page-numeric prefix 19**:
   `app/pages/19_ism_services_spy_{story,evidence,strategy,methodology}.py`.
3. Register the pair in `app/components/pair_registry.py` (add `"ism_services_spy": "pages/19_ism_services_spy",` adjacent to the petrol_inv_spy entry) and any display-name map. Confirm it appears on the landing card grid.
4. Leaderboard / combination counts: use the BENCHMARK-excluded count (**3385 valid of 4880**) — NEVER `len(tdf)`. (APP count-bug precedent.)

## Honesty wiring (binding — this is a LOW-confidence, fragile winner)
- The Strategy confidence block and Evidence method blocks MUST surface the narrative's honest framing: countercyclical (not procyclical), reverse-causality dominance, negative in-sample Sharpe red flag, bootstrap p=0.073 (not significant), confidence LOW, gives up return (9.8% vs 15.1% B&H). Do NOT let the config headline imply ISM Services leads SPY. The pair's own headline string is: "contrarian drawdown overlay, not a leading SPY signal".
- Route the correct charts to the correct sections (LEAD-DOM1 spirit): the both-direction Granger chart belongs in the Evidence causality block.

## Binding gates
- **META-CMP pre-commit gates must pass** (T1.1 schema, T1.2 loader smoke — runs since app/ files staged, T1.3 filename, T2 chart completeness). Fix at source if any fail.
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.

## Conventions
- Run from repo root, project Python. Commit your portal files (META-CMP gates run on commit).
- Write handoff `_pws/lead-lesandro/mode3_ism_services/ace_handoff.md` (files created, registry line, local slug list for cloud verify: `ism_services_spy_{story,evidence,strategy,methodology}`).
- Print `ACE DONE` at line start when finished (+ files list), or `ACE BLOCKED: <reason>`.

Begin now.
