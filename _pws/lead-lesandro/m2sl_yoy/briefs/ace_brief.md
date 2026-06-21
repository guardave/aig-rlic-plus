[App Dev Ace] — Mode-1 dispatch — pair `m2sl_yoy_spy` (stage 4, final)

You are App Dev Ace. Resolve persona via `./AGENTS.md`: read SOP `docs/agent-sops/appdev-agent-sop.md` + `~/.claude/agents/appdev-ace/`. Lead Lesandro is manager + sole checker.

## Inputs (all VERIFIED by Lead, committed to branch `pair260619_m2sl_yoy_spy`)
- Config template: `app/pair_configs/petrol_inv_spy_config.py` (most recent full pattern); `ism_services_spy_config.py` (most recent honest low-confidence pair — good model since m2sl is also reverse-causal/low-confidence).
- Page template: `app/pages/19_ism_services_spy_{story,evidence,strategy,methodology}.py`.
- Econ results: `results/m2sl_yoy_spy/` (winner_summary.json = source of truth for headline numbers).
- Charts: `output/charts/m2sl_yoy_spy/plotly/` (20 charts + meta + perceptual PNGs).
- Narrative: `docs/portal_narrative_m2sl_yoy_spy_20260619.md` (use its prose + section structure, incl. the reverse-causality lead).
- Vera+Ray handoff: `_pws/lead-lesandro/m2sl_yoy/vera_ray_handoff.md` (has proposed display_names forms).

## Winner (from winner_summary.json — do NOT hardcode divergent values)
signal `m2sl_yoy_accel_pct` (M2 money-growth ACCELERATION), threshold gt 0.0523 (p50), **lead L2 months**, P1 Long/Cash, **procyclical**. OOS Sharpe 1.69 vs 0.90 B&H; ann 17.6% vs 14.9%; max DD -4.0% vs -23.9%; OOS 2018-01→2026-04. found_in_search, confidence LOW, bootstrap p=0.025.

## Task — assemble the portal for m2sl_yoy_spy
1. Create `app/pair_configs/m2sl_yoy_spy_config.py` mirroring the petrol/ism config structure (pair_id, display names, chart manifest, section content wiring from the narrative, KPIs, evidence_status routing). Pull headline numbers from winner_summary.json. Honor found_in_search labeling (DPS-FE2: "Search-phase OOS Sharpe (no holdout final exam yet)").
2. Create the 4 pages with **page-numeric prefix 20**: `app/pages/20_m2sl_yoy_spy_{story,evidence,strategy,methodology}.py` (thin wrappers; note the evidence page passes `EVIDENCE_METHOD_BLOCKS`, not a config object — see the ism evidence wrapper).
3. Register the pair in `app/components/pair_registry.py` (add `"m2sl_yoy_spy": "pages/20_m2sl_yoy_spy",` adjacent to the ism entry).
4. **Register display label (completeness gate — Ray flagged this gap):** add `m2sl_yoy` + `m2sl_yoy_spy` to `INDICATOR_NAMES` in `app/components/display_names.py` with a reader-friendly label (e.g. "M2 Money Supply (YoY)" or per Ray's proposed form). Confirm `get_integrity_issues()` returns clean for this pair (no display_indicator_unregistered). Skip INDICATOR_ABBREV if the label already embeds the abbrev.
5. Leaderboard / combination counts: use the BENCHMARK-excluded count (**3369 valid of 4720**) — NEVER `len(tdf)`.

## Honesty wiring (binding — low-confidence, reverse-causal winner)
- Strategy confidence block + Evidence method blocks MUST surface: the signal is ACCELERATION (not level); reverse causality (M2 lags SPY — not a leading signal); found_in_search; confidence LOW; bootstrap p=0.025; drawdown win is episode-shaped (2020/2022 regime). Do NOT imply M2 leads SPY. Route the both-direction Granger chart to the Evidence causality block (LEAD-DOM1 spirit).

## Gates
- META-CMP pre-commit gates must pass (T1.1 schema, T1.2 loader smoke — runs since app/ staged, T1.3 filename, T2 chart completeness). Fix at source if any fail.
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Commit your portal files to branch `pair260619_m2sl_yoy_spy` (author App Dev Ace).

## Output (final message to Lead — factual, not user-facing)
- Files created, registry line, display_names entry + `get_integrity_issues()` result, local slug list for cloud verify (`m2sl_yoy_spy_{story,evidence,strategy,methodology}`), gate results, commit hash. Or BLOCKED + reason.