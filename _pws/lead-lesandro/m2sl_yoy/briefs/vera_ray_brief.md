[Viz Vera + Research Ray] — Mode-1 dispatch — pair `m2sl_yoy_spy` (stage 3)

You run TWO roles: **Viz Vera** (charts) and **Research Ray** (narrative). Resolve both personas via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOPs `docs/agent-sops/visualization-agent-sop.md` AND `docs/agent-sops/research-agent-sop.md`, and the matching `~/.claude/agents/` profiles. Lead Lesandro is manager + sole checker.

## Inputs (Dana + Evan, VERIFIED by Lead)
- Data: `data/m2sl_yoy_spy_{monthly,daily}_latest.parquet`.
- Econ results: `results/m2sl_yoy_spy/` — winner_summary.json, tournament_results_*, granger_by_lag.csv, regime_quartile_returns*, rolling_correlation_*, structural_break_*, subperiod_sharpe.csv, strategy_returns_*, signals_*.parquet, evidence_status.json, oos_split_record.json, core_models_20260619/.
- Evan handoff: `_pws/lead-lesandro/m2sl_yoy/evan_handoff.md`.
- **Winner:** signal `m2sl_yoy_accel_pct` = **M2 money-growth ACCELERATION** (month-over-month change in M2 YoY growth), threshold gt 0.0523 (p50), **lead L2 (months)**, P1 Long/Cash, direction **PROCYCLICAL**. OOS Sharpe 1.69 vs 0.90 B&H; ann return 17.6% vs 14.9%; max DD -4.0% vs -23.9%; OOS 2018-01→2026-04 (100mo). bootstrap p=0.025, confidence LOW, evidence_status=found_in_search, durability conditionally_durable.

## ============ VERA (charts) ============
Use `scripts/generate_charts_busloans_spy.py` / `_petrol_inv_spy.py` as structural templates; create `scripts/generate_charts_m2sl_yoy_spy.py`. Produce the standard set as Plotly JSON + `_meta.json` sidecars + `_perceptual_check_*.png` into `output/charts/m2sl_yoy_spy/plotly/`:
hero, equity_curves, drawdown, correlation_heatmap, ccf_prewhitened, granger_f_by_lag, hmm_regime_probs, local_projections, quartile/regime returns, history_zoom_{gfc,covid,dotcom,inflation_2022}. Emit `chart_skip_*.json` for any genuinely-N/A chart with a reason.
- **VIZ-DP1 (axis discipline, binding):** dual-axis charts assign traces to the correct axis, pass GATE-DP1 (no invisible-trace). Verify explicitly.
- **Granger chart MUST show BOTH directions** — forward (M2→SPY, n.s. at all lags) and reverse (SPY→M2, significant lags 1-5,8). Do NOT hide the reverse dominance; it's the headline honesty point.
- M2 YoY history is vivid: plot the 2020-21 surge (~27%) and the **first-ever YoY contraction 2022-23** (negative) prominently; mark the 0% line. Colorblind-friendly, labeled axes/titles, honest annualization.
- Run perceptual PNG render for each chart.

## ============ RAY (narrative) ============
Write `docs/portal_narrative_m2sl_yoy_spy_20260619.md` (4 sections: Story, Evidence, Strategy, Methodology) + fill owned interpretation_metadata fields {strategy_objective, expected_direction, mechanism, caveats, narrative_summary}.

**RES-JFU (binding):** first user-facing use of any term/abbrev → long form + (abbrev) + plain gloss (e.g. "year-over-year (YoY) — this month vs the same month a year ago"; "out-of-sample (OOS) — tested on data not used to pick the rule"; "Granger causality — whether one series' past helps predict another's future").

**REQUIRED — honest reconciliation (Lead mandate). Do NOT oversell:**
  1. The tradable signal is **money-growth ACCELERATION** (the MoM change in M2's YoY rate), NOT the YoY level itself — explain plainly why "is money growth speeding up or slowing down" beat "is money growth high/low".
  2. **Lead with the causality finding:** Toda-Yamamoto Granger shows NO forward signal (M2→SPY n.s. at all lags); the REVERSE (SPY→M2) is significant. M2 behaves as coincident/lagging — the market moves first. So this is NOT evidence that M2 leads equities; the edge is a found-in-search acceleration pattern. State this prominently.
  3. Mechanism as HYPOTHESIS (not fact): accelerating money growth ≈ easing liquidity/credit impulse → risk-on tailwind over the next ~2 months. Reference the 2020-21 surge and 2022-23 contraction as the vivid (but regime-concentrated) episodes.
  4. Carry fragility caveats prominently: bootstrap p=0.025 (significant at 5% but search-selected), found_in_search (no final exam), confidence LOW, conditionally_durable, OOS dominated by the 2020/2022 monetary regime. The defensive overlay's drawdown win (-4.0% vs -23.9%) is real but episode-shaped.

## Conventions
- Repo root, project Python. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. Stay in lanes; don't edit Evan's design_note.
- Commit charts + narrative to branch `pair260619_m2sl_yoy_spy` (META-CMP gates run; fix at source). Authors: Viz Vera / Research Ray as appropriate.
- Handoff `_pws/lead-lesandro/m2sl_yoy/vera_ray_handoff.md` (charts list + narrative path + Ace notes).
- Your final message to Lead is a factual report (charts produced, narrative path, commit hash, any blocks) — not user-facing.