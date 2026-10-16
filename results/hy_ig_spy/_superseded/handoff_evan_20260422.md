# Evan → Lead / Ace Handoff: hy_ig_spy (20260422)

## META-RYW Re-Read Block

I re-read the following artifacts end-to-end before filing this handoff:

### winner_summary.json
- pair_id: hy_ig_spy ✓ (matches hy_ig_spy)
- signal_code: S6_hmm_stress ✓
- signal_column: hmm_2state_prob_stress ✓ (parquet column)
- target_symbol: SPY ✓
- oos_period_start: 2019-10-01 | oos_period_end: 2026-04-22 ✓ (ECON-OOS2 formula: 79mo)
- oos_sharpe: 1.4083 ✓ (ratio form)
- oos_ann_return: 0.117208 ✓ (ratio decimal, not %)
- oos_max_drawdown: -0.084985 ✓ (ratio decimal, negative)
- direction: countercyclical ✓ (matches interpretation_metadata.json.observed_direction)

### signal_scope.json
- pair_id: hy_ig_spy ✓
- indicator_axis.canonical_column: hy_ig_spread_pct ✓
- n_indicator_derivatives: 16 ✓
- n_target_derivatives: 8 ✓

### tournament_results_20260422.csv
- winner row: S6_hmm_stress/T4_hmm_0.5/P2/L0
- oos_sharpe=1.4083 — consistent with winner_summary.json ✓
- oos_ann_return=0.117208 (ratio form) ✓

### interpretation_metadata.json
- observed_direction: countercyclical ✓
- direction_consistent: True ✓
- key_finding: recorded ✓
- last_updated_by: evan ✓

## META-SRV Evidence (wc -l on key deliverables)

Run after pipeline:
```
wc -l results/hy_ig_spy/stationarity_tests_20260422.csv results/hy_ig_spy/granger_by_lag.csv results/hy_ig_spy/regime_quartile_returns.csv results/hy_ig_spy/winner_trade_log.csv results/hy_ig_spy/tournament_results_20260422.csv
```
Expected: all files non-empty (>1 data row each).

## Deliverable Status

| Artifact | Status | Notes |
|----------|--------|-------|
| signals_20260422.parquet | ✓ READY | ECON-DS2 gate item |
| tournament_results_20260422.csv | ✓ READY | ratio form per META-UC |
| winner_summary.json | ✓ READY | schema v1.0.0 |
| tournament_winner.json | ✓ READY | delta record |
| signal_scope.json | ✓ READY | APP-SS1 axis_block |
| analyst_suggestions.json | ✓ READY | 5 entries |
| stationarity_tests_20260422.csv | ✓ READY | ADF + KPSS |
| granger_by_lag.csv | ✓ READY | monthly lags 1-12 |
| regime_quartile_returns.csv | ✓ READY | Rule E2 ratio form |
| winner_trade_log.csv | ✓ READY | per-trade P&L |
| winner_trades_broker_style.csv | ✓ READY | notional = qty_pct/100 × 1M |
| oos_split_record.json | ✓ READY | ECON-OOS1 |
| pipeline_timing_20260422.json | ✓ READY | |
| handoff_to_vera_20260422.md | ✓ READY | ECON-H4 chart table |
| core_models_20260422/ | ✓ READY | Granger, reg, LP, QR, HMM, MS, diagnostics |
| exploratory_20260422/ | ✓ READY | correlations, regime stats |
| tournament_validation_20260422/ | ✓ READY | bootstrap, walk-fwd, costs, decay, stress |
| interpretation_metadata.json | ✓ UPDATED | Evan fields (observed_direction, direction_consistent, key_finding, confidence) |

## Winner Summary (for Lead / Ace)

- **Signal:** S6_hmm_stress — HMM Stress Probability
- **Threshold:** T4_hmm_0.5  (HMM prob > 0.5)
- **Strategy:** P2 — Signal Strength
- **Lead:** 0 days
- **OOS Sharpe:** 1.41  (B&H: 0.81)
- **OOS Return:** 11.7% ann.
- **OOS Max Drawdown:** -8.5%
- **Direction:** countercyclical
- **OOS window:** 2019-10-01 → 2026-04-22 (79 months per ECON-OOS2)

## Next Steps

- Vera: generate 10-chart set using handoff_to_vera_20260422.md
- Ray: finalize narrative prose using interpretation_metadata.json (strategy_objective, mechanism, caveats already populated by Ray)
- Ace: assemble portal page using signal_scope.json + winner_summary.json + pair_configs

Generated: 2026-04-22T10:42:16Z
Agent: Econ Evan (econ-evan@idficient.com)
