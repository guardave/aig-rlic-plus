[Viz Vera + Research Ray] — Mode-1 dispatch — pair `phlxsox_spy` (stage 3)

Two roles: Viz Vera (charts) + Research Ray (narrative). Resolve both via `./AGENTS.md`: SOPs `docs/agent-sops/visualization-agent-sop.md` AND `docs/agent-sops/research-agent-sop.md` + matching `~/.claude/agents/` profiles. Lead Lesandro is manager + sole checker.

## Inputs (Dana + Evan, VERIFIED by Lead)
- Data: `data/phlxsox_spy_{daily,monthly}_latest.parquet`.
- Econ: `results/phlxsox_spy/` — winner_summary.json, tournament_results_*, granger_by_lag.csv, regime_quartile_returns*, rolling_correlation_*, structural_break_*, subperiod_sharpe.csv, strategy_returns_*, signals_*.parquet, evidence_status.json, oos_split_record.json, core_models_20260619/ (incl. `incremental_edge_vs_spy_momentum.csv`).
- Evan handoff: `_pws/lead-lesandro/phlxsox/evan_handoff.md`.
- **Winner:** signal `sox_spy_ratio_mom_6m_pct` = **SOX/SPY relative-strength 6-month momentum**, threshold gt rolling-p75 (30.68), **lead L63 trading days (~3mo)**, P1 Long/Cash, procyclical. OOS (2021-06→2026-06) Sharpe **1.57 vs B&H 0.82 AND vs SPY-own-momentum 0.83**; max DD −9.7% vs −24.5%. found_in_search, confidence LOW, bootstrap p=0.041.

## ============ VERA (charts) ============
Create `scripts/generate_charts_phlxsox_spy.py` (use busloans/petrol generators as templates). Standard set → `output/charts/phlxsox_spy/plotly/` as Plotly JSON + `_meta.json` + `_perceptual_check_*.png`:
hero, equity_curves, drawdown, correlation_heatmap, ccf_prewhitened, granger_f_by_lag, hmm_regime_probs, local_projections, quartile/regime returns, history_zoom_{gfc,covid,dotcom,inflation_2022}. chart_skip_*.json for N/A charts.
- **equity_curves MUST be a 3-LINE chart: winner vs Buy&Hold vs SPY-own-momentum benchmark** (per Evan handoff) — the SPY-own-momentum line is the honesty anchor (the winner only marginally beats it).
- **Granger chart shows BOTH directions** — the honest finding is BIDIRECTIONAL feedback (SOX↔SPY both significant at all lags), NOT a one-way semiconductor lead. Title/caption must convey "feedback, not clean lead."
- **VIZ-DP1 axis discipline** (verify explicitly). Colorblind palettes, labeled axes/titles, honest annualization. Perceptual PNG each.

## ============ RAY (narrative) ============
Write `docs/portal_narrative_phlxsox_spy_20260619.md` (Story/Evidence/Strategy/Methodology) + owned interpretation_metadata fields {strategy_objective, expected_direction, mechanism, caveats, narrative_summary}.

**RES-JFU (binding):** first use of any term/abbrev → long form + (abbrev) + plain gloss (e.g. "relative strength — one index's price divided by another's, here SOX ÷ SPY"; "out-of-sample (OOS) — tested on data not used to pick the rule").

**REQUIRED honest reconciliation (Lead mandate — do NOT oversell; this winner is fragile):**
  1. The signal is **SOX/SPY RELATIVE STRENGTH momentum**, NOT raw SOX — explain that because both are equities (0.709 daily return correlation), raw SOX vs SPY is mostly shared market beta (co-movement), so the analysis deliberately uses the *ratio* to isolate any genuine semiconductor-leadership signal.
  2. **Causality is BIDIRECTIONAL feedback, not a clean lead:** Toda-Yamamoto Granger is significant SOX→SPY AND SPY→SOX at all lags. So this is NOT "semis lead the market" in a clean causal sense; the tradable content is a weak relative-strength momentum effect.
  3. **The edge over SPY-own-momentum is MARGINAL and horizon-dependent:** relative strength adds over SPY's own momentum at the 21-day horizon (p=0.033) but NOT at 63 days (p=0.075); incremental R² ~1%. State this plainly — the winner beats a SPY-momentum benchmark in the backtest but the statistical incremental edge is thin.
  4. **Fragility caveats prominent:** in-sample Sharpe 0.10 vs OOS 1.57 (the OOS is a favorable 2021-26 semiconductor-bull draw); the median valid tournament combo (0.67) UNDERPERFORMS buy&hold (0.82) — the search mostly found losers; win-rate 0.20; the rule LOST in every pre-OOS crisis (Dot-Com, GFC, COVID); bootstrap p=0.041 (marginal); found_in_search, no final exam; confidence LOW. The drawdown improvement is real but regime-shaped.

## Conventions
- Repo root, project Python. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. Stay in lanes.
- Commit charts + narrative to branch `pair260619_phlxsox_spy` (META-CMP gates run). Authors Vera/Ray.
- Handoff `_pws/lead-lesandro/phlxsox/vera_ray_handoff.md` (charts list + narrative path + Ace notes incl. the display_names gap).
- Final message to Lead = factual report (charts incl. 3-line equity + both-direction Granger, narrative path, honesty points covered, commit hash). Or BLOCKED.