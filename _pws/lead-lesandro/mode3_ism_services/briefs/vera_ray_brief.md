[Viz Vera + Research Ray] — Mode-3 maker dispatch — pair `ism_services_spy`

You are running TWO roles in this pane: **Viz Vera** (charts) and **Research Ray** (narrative). Resolve both personas via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOPs `docs/agent-sops/visualization-agent-sop.md` AND `docs/agent-sops/research-agent-sop.md`, and the matching `~/.claude/agents/` profiles. Lead Lesandro (Claude) is manager + sole checker.

## Inputs (Dana + Evan, VERIFIED by Lead)
- Data: `data/ism_services_spy_{monthly,daily}_latest.parquet`.
- Econ results: `results/ism_services_spy/` — winner_summary.json, tournament_results_*, granger_by_lag.csv, regime_quartile_returns*, rolling_correlation_*, structural_break_*, subperiod_sharpe.csv, strategy_returns_*, signals_20260618.parquet, evidence_status.json, oos_split_record.json, core_models_20260618/ (correlations, ccf_prewhitened, granger_causality, local_projections, quantile_regression, transfer_entropy, hmm_states/summary).
- Evan handoff: `_pws/lead-lesandro/mode3_ism_services/evan_handoff.md`.
- **Winner:** signal `ism_services_gap_50` (ISM Services PMI minus 50), threshold **lt** a rolling z-score of −1.0, **P1 Long/Cash, direction COUNTERCYCLICAL, lead L3 (months)**. OOS Sharpe 1.54 vs 0.88 B&H; max DD −3.8% vs −23.9%; OOS 2018-10→2025-10 (n=85). bootstrap p=0.073 (NOT significant). IS Sharpe −0.112. confidence LOW. evidence_status=found_in_search.

## ============ VERA (charts) ============
Use `scripts/generate_charts_petrol_inv_spy.py` (or busloans) as the structural template; create `scripts/generate_charts_ism_services_spy.py`. Produce the standard set as Plotly JSON + `_meta.json` sidecars + `_perceptual_check_*.png` into `output/charts/ism_services_spy/plotly/`:
hero, equity_curves, drawdown, correlation_heatmap, ccf_prewhitened, granger_f_by_lag, hmm_regime_probs, local_projections, history_zoom_{gfc,covid,dotcom,inflation_2022}, plus quartile/returns-by-regime chart. Emit `chart_skip_*.json` for any genuinely-not-applicable chart with a reason.
- **VIZ-DP1 (axis discipline, binding):** any dual-axis chart must assign traces to the correct axis and pass GATE-DP1 — no invisible-trace risk (the exact defect that bit gold_copper history_zoom). Verify axis assignment explicitly.
- The PMI is a diffusion index — plot it with the **50 reference line** prominent (expansion/contraction threshold). The signal fires when the gap z-score drops below −1.0, so the hero/signal chart should make the "buy when services are weak" (contrarian) logic visually legible.
- **Granger chart MUST show BOTH directions** — forward (PMI→SPY, significant at NO lags) and reverse (SPY→PMI, significant at lags 1–12). Do NOT hide the reverse dominance; it is the headline honesty point.
- Colorblind-friendly palettes, labeled axes, titles. Annualization labeling honest (state window if a return is scaled).
- Run perceptual PNG render for each chart.

## ============ RAY (narrative) ============
Write `docs/portal_narrative_ism_services_spy_20260618.md` (4 sections: Story, Evidence, Strategy, Methodology) and fill your owned interpretation_metadata fields {strategy_objective, expected_direction, mechanism, caveats, narrative_summary}.

**RES-JFU (binding):** on first user-facing use of ANY technical term/notation/abbreviation in each section, write the full long form + short form in parentheses + a plain-English gloss. (e.g. "diffusion index — a survey score where 50 separates expansion from contraction"; "out-of-sample (OOS) — tested on data not used to pick the rule"; "Granger causality — whether one series' past helps predict another's future".)

**REQUIRED — Direction, causality & robustness reconciliation (Lead checker mandate). This is the weakest winner in the pair series; do NOT oversell. Your narrative MUST explicitly:**
  1. **State the natural prior (procyclical):** ISM Services > 50 = expansion → risk-on → higher SPY. Then show the tournament winner is the OPPOSITE — **countercyclical / contrarian**: it goes LONG SPY when services sentiment is depressed (gap z-score < −1.0). Frame this as buying fear/weakness, and offer a credible MECHANISM as a HYPOTHESIS (e.g. depressed services sentiment marks cyclical troughs near which forward equity returns are high — a mean-reversion/"maximum pessimism" effect), NOT as established fact.
  2. **Lead with the reverse-causality finding (do not bury it):** Toda-Yamamoto Granger shows SPY predicts the ISM Services survey at lags 1–12, while the survey predicts SPY at NO lags. The honest reading: ISM Services PMI behaves as a **coincident/lagging** reflection of conditions equities already price — it is NOT a leading indicator of SPY. Any tradable edge is therefore suspect and likely regime-driven.
  3. **Flag the in-sample/out-of-sample inversion:** in-sample Sharpe is NEGATIVE (−0.11) while OOS Sharpe is 1.54, and the OOS performance is `episode_concentrated` (CP1-A) — strongly suggesting the result rides specific episodes (e.g. the 2020 COVID services collapse and recovery) rather than a stable effect. A negative IS Sharpe with a strong OOS Sharpe is a RED FLAG for fragility, not a strength — say so plainly.
  4. **Carry the fragility caveats prominently:** bootstrap p=0.073 (not significant at 5%), found_in_search (no final exam), confidence LOW, structural break flagged 2009-03, and the defensive overlay gives up return (9.8% vs 15.1% B&H) for drawdown protection. The honest bottom line: an interesting drawdown-management overlay, but NOT evidence that ISM Services PMI leads the S&P 500.

## Conventions
- Run from repo root, project Python. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. LEAD-DL1: stay in your lanes; do not edit Evan's design_note.
- Write handoff `_pws/lead-lesandro/mode3_ism_services/vera_ray_handoff.md` (charts list + narrative path + any Ace notes).
- Print `VERARAY DONE` at line start when finished (+ artifact list), or `VERARAY BLOCKED: <reason>`.

Begin now.
