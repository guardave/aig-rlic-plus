# Chart Regression Note — indpro_spy — 2026-06-11

Producer: `scripts/generate_strategy_perf_charts.py` (ECON-SR1 consumer). Branch `fix260611_meta_cmp`.

## Charts Changed
- `equity_curves` (regenerated — CONTENT CHANGE, see Spec Diff)
- `drawdown` (regenerated — replaces defective W0.5 backfill)
- `walk_forward` (regenerated — replaces defective W0.5 backfill)
- `subperiod_sharpe` (regenerated — rebuilt from Evan's ECON-SR1-reconciled CSV; Full-OOS Sharpe was 0.2543 defective → 1.1036)

## Spec Diff
| Field | Old | New (2026-06-11) |
|---|---|---|
| equity_curves traces | 4: "Buy & Hold SPY" + top-3 tournament strategies ("#1: S6_mom3m/T1_fixed_p75", "#2: S3_mom/T1_fixed_p25", "#3: S4_dev_trend/T3_zscore_1.0") — original 2026-03 tournament-era chart | 2: winner ("Strategy: 3-Month Momentum Long/Cash") + "Buy & Hold SPY", from canonical `strategy_returns_20260611.csv` |
| equity_curves fidelity | #1 winner trace did NOT reconcile: endpoint 1.519 vs canonical 1.711 (11.2% off); implied Sharpe 0.90 vs reported 1.1036 | reconciles EXACT (implied DD −8.07% = winner_summary; endpoint re-read at gen time) |
| drawdown/walk_forward series | defective W0.5 reconstruction (recon OOS Sharpe 0.25 vs reported 1.10) | canonical series; window OOS 2018-01-01..2025-12-31 |
| Palette / NBER | matplotlib defaults; no NBER | okabe_ito_2026; NBER shading + disclosure |
| Trace naming | raw pipeline tokens ("#1: S6_mom3m/T1_fixed_p75") — VIZ-NS1 violation | humanised display names |

## Rationale
The old equity chart predated W0.5 but its winner trace derived from a non-reconciling reconstruction in the original generator (B&H trace was exact; winner trace 11.2% off at endpoint and Sharpe-understated vs the page KPI). ECON-SR1 + the SOP numerical-reconciliation gate require chart data to match winner_summary. The #2/#3 comparison traces cannot be produced from the canonical winner-series artifact and were dropped; the live template caption already promises "the tournament winner compared to buy-and-hold", so the new content aligns chart with caption. If the top-3 comparison view is wanted back, it needs reconciled series for those combos from Evan first — flagged to Lead.

## Approved By
Lead Lesandro dispatch (regeneration of defective charts); equity content change (top-3 → winner-only) self-approved per Rule A4 and FLAGGED FOR LEAD REVIEW in the handoff.
