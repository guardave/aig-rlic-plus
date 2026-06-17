[Viz Vera + Research Ray] — Mode-3 maker dispatch — pair `petrol_inv_spy`

You are running TWO roles in this pane: **Viz Vera** (charts) and **Research Ray** (narrative). Resolve both personas via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOPs `docs/agent-sops/visualization-agent-sop.md` AND `docs/agent-sops/research-agent-sop.md`, and the matching `~/.claude/agents/` profiles. Lead Lesandro (Claude) is manager + sole checker.

## Inputs (Dana + Evan, VERIFIED by Lead)
- Data: `data/petrol_inv_spy_{monthly,daily}_latest.parquet`.
- Econ results: `results/petrol_inv_spy/` — winner_summary.json, tournament_results_20260617.csv, granger_by_lag.csv, regime_quartile_returns.csv, rolling_correlation_petrol_inv_spy.csv, structural_break_*.json, subperiod_sharpe.csv, strategy_returns_20260617.csv, signals_20260617.parquet, core_models_20260617/ (correlations, ccf_prewhitened, granger_causality, local_projections, quantile_regression, transfer_entropy, hmm_states/summary).
- Evan handoff: `_pws/lead-lesandro/mode3_petrol_inv/evan_handoff.md`.
- Winner: signal `petrol_inv_3m_pct` (3-month % change in total petroleum stocks), threshold gt 0.323, **P1 Long/Cash, direction PROCYCLICAL, lead L12 (months)**. OOS Sharpe 1.48 vs 0.93 B&H; max DD −6.3% vs −23.9%; OOS 2017-08→2025-09 (n=98). bootstrap p=0.099 (NOT significant). confidence=low. evidence_status=found_in_search.

## ============ VERA (charts) ============
Use `scripts/generate_charts_busloans_spy.py` as the structural template; create `scripts/generate_charts_petrol_inv_spy.py`. Produce the standard set as Plotly JSON + `_meta.json` sidecars + `_perceptual_check_*.png` into `output/charts/petrol_inv_spy/plotly/`:
hero, equity_curves, drawdown, correlation_heatmap, ccf_prewhitened, granger_f_by_lag, hmm_regime_probs, local_projections, history_zoom_{gfc,covid,dotcom,inflation_2022}, plus quartile/returns-by-regime chart. Emit `chart_skip_*.json` for any genuinely-not-applicable chart with a reason.
- **VIZ-DP1 (axis discipline, binding):** any dual-axis chart must assign traces to the correct axis and pass the GATE-DP1 check — no invisible-trace risk. This is the exact defect class that bit gold_copper history_zoom. Verify axis assignment explicitly.
- Colorblind-friendly palettes, labeled axes, titles. Annualization labeling honest (state window if a return is scaled).
- Run perceptual PNG render for each chart.

## ============ RAY (narrative) ============
Write `docs/portal_narrative_petrol_inv_spy_20260617.md` (4 sections: Story, Evidence, Strategy, Methodology) and fill your owned interpretation_metadata fields {strategy_objective, expected_direction, mechanism, caveats, narrative_summary}.

**RES-JFU (binding):** on first user-facing use of ANY technical term/notation/abbreviation in each section, write the full long form + short form in parentheses + a plain-English gloss. (e.g. "autoregressive order-one (AR(1)) — a series compared to its own previous value"; "out-of-sample (OOS) — tested on data not used to pick the rule".)

**REQUIRED — Direction & lag reconciliation (Lead checker mandate).** The winner is *procyclical* at a *12-month* lead, which (a) contradicts the natural counter-cyclical prior (inventories build when demand is weak — they rose into the GFC and COVID) and (b) does not match where Granger causality peaks (significant at lags 6, 7, 8 months; reverse none). Your narrative MUST explicitly:
  1. State the counter-cyclical prior, then show it is overturned by evidence — cite the quartile gradient (Q1 lowest 3m petrol change → Sharpe 0.37 / 6.0% ann; Q4 highest → Sharpe 1.25 / 17.5% ann; monotonic), which corroborates procyclical.
  2. Offer a credible economic MECHANISM for procyclical (e.g. inventory builds reflecting robust supply/production expansion and softer energy prices → consumer & corporate tailwind → equities over the following year), stated as a hypothesis, not a fact.
  3. Honestly flag the lag imprecision: Granger leads cluster at 6–8 months but the tournament winner sits at 12 — the exact horizon is NOT pinpointed; treat the 6–12m band as the corroborated lead range and the L12 point as a found-in-search selection.
  4. Carry the fragility caveats prominently: bootstrap p=0.099 (not significant at 5%), found_in_search (no final exam), confidence low, defensive overlay that gives up return (9.8% vs 15.2% B&H) for drawdown protection. Do NOT oversell.

## Conventions
- Run from repo root, project Python. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. LEAD-DL1: stay in your lanes; do not edit Evan's design_note.
- Write handoff `_pws/lead-lesandro/mode3_petrol_inv/vera_ray_handoff.md` (charts list + narrative path + any Ace notes).
- Print `VERARAY DONE` at line start when finished (+ artifact list), or `VERARAY BLOCKED: <reason>`.

Begin now.
