[App Dev Ace] — Mode-1 dispatch — pair `phlxsox_spy` (stage 4, final)

You are App Dev Ace. Resolve persona via `./AGENTS.md`: SOP `docs/agent-sops/appdev-agent-sop.md` + `~/.claude/agents/appdev-ace/`. Lead Lesandro is manager + sole checker.

## Inputs (all VERIFIED by Lead, committed to branch `pair260619_phlxsox_spy`)
- Config templates: `app/pair_configs/petrol_inv_spy_config.py` + `ism_services_spy_config.py` + `m2sl_yoy_spy_config.py` (the 3 most recent honest low-confidence pairs — good models, since phlxsox is also fragile/low-confidence).
- Page template: `app/pages/20_m2sl_yoy_spy_{story,evidence,strategy,methodology}.py`.
- Econ: `results/phlxsox_spy/` (winner_summary.json = source of truth).
- Charts: `output/charts/phlxsox_spy/plotly/` (20 charts incl. 3-line equity_curves + both-direction granger).
- Narrative: `docs/portal_narrative_phlxsox_spy_20260619.md`.
- Vera+Ray handoff: `_pws/lead-lesandro/phlxsox/vera_ray_handoff.md` (has proposed display_names forms + history-zoom slugs).

## Winner (from winner_summary.json — do NOT hardcode divergent values)
signal `sox_spy_ratio_mom_6m_pct` (SOX/SPY relative-strength 6m momentum), threshold gt rolling-p75 (30.68), **lead L63 trading days (~3mo)**, P1 Long/Cash, procyclical. OOS Sharpe 1.57 vs B&H 0.82 (and vs SPY-own-momentum 0.83); max DD -9.7%. found_in_search, confidence LOW, bootstrap p=0.041.

## Task — assemble the portal for phlxsox_spy
1. Create `app/pair_configs/phlxsox_spy_config.py` mirroring the m2sl/ism low-confidence pattern (pair_id, display names, chart manifest from the narrative, KPIs, evidence_status routing). Pull headline numbers from winner_summary.json. found_in_search labeling (DPS-FE2).
2. Create the 4 pages with **page-numeric prefix 21**: `app/pages/21_phlxsox_spy_{story,evidence,strategy,methodology}.py` (thin wrappers; evidence wrapper passes `EVIDENCE_METHOD_BLOCKS`, not a config object).
3. Register in `app/components/pair_registry.py` PAGE_ROUTING (add `"phlxsox_spy": "pages/21_phlxsox_spy",`).
4. **Register display label** in `app/components/display_names.py` INDICATOR_NAMES: add `phlxsox` + `phlxsox_spy` with a reader-friendly label (e.g. "PHLX Semiconductor Index (SOX)" — per Ray's proposed form; "SOX" is a real ticker abbrev, so you MAY add an INDICATOR_ABBREV entry if the long form doesn't already embed it). Confirm `get_integrity_issues()` clean for this pair.
5. Combo counts: BENCHMARK-excluded (**4607 valid of 6760**) — never `len(tdf)`.

## Honesty wiring (binding — fragile, low-confidence, NOT-a-clean-lead pair)
Strategy confidence block + Evidence method blocks MUST surface: signal = RELATIVE STRENGTH (not raw SOX, because of 0.709 equity co-movement); causality is BIDIRECTIONAL feedback (not a clean semiconductor lead); edge over SPY-own-momentum is MARGINAL/horizon-dependent; IS Sharpe 0.10 vs OOS 1.57 (2021-26 semis-bull draw); median valid combo < B&H; lost every pre-OOS crisis; bootstrap p=0.041; found_in_search; confidence LOW. Route the 3-line equity curve to Strategy/Performance and the both-direction Granger to the Evidence causality block. Do NOT imply "semis lead the market."

## Gates
- META-CMP pre-commit gates must pass (T1.1/T1.2/T1.3/T2). Fix at source if any fail.
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Commit your portal files to branch `pair260619_phlxsox_spy` (author App Dev Ace).

## Output (final message to Lead — factual, not user-facing)
Files created, registry line, display_names entry + `get_integrity_issues()` result, loader-smoke result, local slug list (`phlxsox_spy_{story,evidence,strategy,methodology}`), gate results, commit hash. Or BLOCKED.