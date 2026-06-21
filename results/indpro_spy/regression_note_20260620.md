# Chart Regression Note — indpro_spy — 2026-06-20

**Author:** Vera (Visualization agent)
**Branch:** `fix260620_lead_horizon`
**Trigger:** ECON-LT1 lead-horizon re-run (under ECON-T5) changed the tournament winner.

## Winner change (upstream, Evan)

| Field | Prior (published) | New (20260620) |
|-------|-------------------|----------------|
| Signal | S6_mom3m (3-Month Momentum) | **S3_mom (INDPRO 1-month momentum)** |
| Threshold | T1_fixed_p75 | **T2_roll_p75 (rolling 60m)** |
| Strategy | P1_long_cash | P1_long_cash (pro-cyclical) |
| Lead | L6 | **L4** |
| OOS Sharpe | 1.1036 | **1.2301** |
| OOS max drawdown | -8.1% | **-2.7%** |

Source of truth: `results/indpro_spy/strategy_returns_20260620.csv` (+ `_meta.json`,
ECON-SR1 reconciled, schema repaired 2026-06-20) and `winner_summary.json`.

## Charts Changed

Regenerated via `scripts/generate_strategy_perf_charts.py indpro_spy` (ECON-SR1
canonical consumer — globs the latest `strategy_returns_*.csv`, never re-derives
positions from signals):

- `equity_curves`
- `drawdown`
- `walk_forward`
- `subperiod_sharpe`

## Spec Diff

| Chart | Field | Old → New |
|-------|-------|-----------|
| equity_curves | strategy trace label | "Strategy: 3-Month Momentum Long/Cash" → "Strategy: INDPRO 1-month momentum Long/Cash" |
| equity_curves | winner final cumret (OOS) | 1.81 → **2.22** (BH unchanged 2.92) |
| drawdown | winner max drawdown | -8.1% → **-2.7%** |
| walk_forward | reported-OOS-Sharpe reference line | 1.10 → **1.23** |
| subperiod_sharpe | Full-OOS Sharpe + per-episode bars | recomputed from regenerated `subperiod_sharpe.csv` (Full-OOS 1.1036 → 1.2301) |

All four reconcile to `winner_summary.json` within ECON-SR1 tolerance
(Sharpe 1.2301, max DD -2.74%, ann ret 10.3%). Palette `okabe_ito_2026`, NBER
shading, VIZ-IC1 pre-save assertions all PASS.

## Winner-INDEPENDENT charts (correctly left untouched)

`hero`, `correlations`, `ccf`, `regime_stats`, `local_projections`,
`quantile_regression`, `granger`, `rf_importance`, `rolling_correlation`,
`rolling_granger`, `structural_break`, `history_zoom_*`.

## Outstanding (not in this pass — authorized systemic 3-chart fix)

`rolling_sharpe_cp` and `tournament_scatter` are winner-dependent, portal-consumed,
and still encode the displaced winner. They will be regenerated from Evan's
forthcoming canonical ECON-SR1-extension sidecars (no re-simulation);
`tournament_scatter` sources the IMMUTABLE coarse published CSV
(`tournament_results_20260314.csv`), not the extended sweep. Tracked separately.

## Two upstream blockers cleared before this pass (Evan, 2026-06-20)

1. `strategy_returns_20260620_meta.json` was missing `oos_start`/`oos_end`/`frequency`
   — re-emitted with full ECON-SR1 schema.
2. `subperiod_sharpe.csv` was stale (Full-OOS 1.1036) — regenerated, all reconciled.

## Rationale

The legacy per-pair generator `scripts/generate_charts_indpro_spy.py` is SUPERSEDED
and must NOT be run (hardcoded `DATE_TAG="20260314"`, reads superseded tournament
CSV, re-simulates the winner from signal/threshold heuristics — the bug class
ECON-SR1 eliminates). The ECON-SR1 consumer `generate_strategy_perf_charts.py` is
the correct producer.

## Approved By

Vera self-approved (winner change is upstream/Evan-driven, ECON-LT1). Flagged for
Lesandro review.

---

## Appendix — Systemic 3-chart pass (2026-06-21, ECON-SR3 sidecars)

Regenerated from Evan's gap sidecars (`gap_sidecars_indpro_spy_meta.json`) via the
ECON-SR3 consumer-side twin (VIZ-SR3T), no re-simulation:

| Chart | Source sidecar | Old → New |
|-------|----------------|-----------|
| `rolling_sharpe_cp` | `rolling_sharpe_indpro_spy.csv` | re-rendered off canonical strategy_return (reconciles OOS 1.2301) |
| `signal_dist` | `signal_dist_indpro_spy.csv` | **new chart** for this pair; histograms indpro_mom IS vs OOS; title "INDPRO 1-Month Momentum Signal Distribution" |
| `tournament_scatter` | `tournament_scatter_indpro_spy.csv` | population = immutable coarse grid (1,666 / 1,149 valid); added labeled overlay "Winner (L4, extended grid)" at (turnover 4.5, Sharpe 1.2301) |

**Disposition:** `signal_dist` is referenced by no page/config (orphan) →
`suggested` + `exploratory: true` (VIZ-O1/E1). Routing into the Methodology
Exploratory section flagged to Lead/Ace.
