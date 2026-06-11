# Chart Regression Note — indpro_xlp — 2026-06-11

Producer: `scripts/generate_strategy_perf_charts.py` (ECON-SR1 consumer). Branch `fix260611_meta_cmp`.

## Charts Changed
- `equity_curves` (regenerated — CONTENT CHANGE, see Spec Diff)
- `drawdown` (regenerated — replaces defective W0.5-class backfill)
- `walk_forward` (regenerated — replaces defective W0.5-class backfill)
- `subperiod_sharpe` (regenerated — Full-OOS Sharpe was 0.1379 defective → 1.1147; old end date 2026-01-31 off-by-one → 2025-12-31)

## Spec Diff
| Field | Old | New (2026-06-11) |
|---|---|---|
| equity_curves traces | 4: "Buy & Hold XLP" + top-3 ("#1: S8_accel/T2_roll_p75", "#2: S3_mom/T1_fixed_p50", "#3: S8_accel/T2_roll_p25"), 2026-04-22 generator | 2: winner ("Strategy: Acceleration Long/Short") + "Buy & Hold XLP", from canonical `strategy_returns_20260611.csv` (repaired signal re-derivation — NB the on-disk trade log is NOT the winner combo, per Evan's 2026-06-11 finding) |
| equity_curves fidelity | #1 trace did NOT reconcile: endpoint 2.187 vs canonical 2.531 (13.6% off); implied Sharpe 0.97 vs reported 1.1147 | reconciles EXACT (implied DD −13.53% = winner_summary) |
| drawdown/walk_forward series | defective reconstruction (recon OOS Sharpe 0.14 / MDD −36.4% vs reported 1.11 / −13.5%) | canonical series; window OOS 2019-01-31..2025-12-31 |
| Palette / NBER / naming | matplotlib defaults; no NBER; raw tokens | okabe_ito_2026; NBER shading + disclosure; humanised names |

## Rationale
Same defect class and same remediation as indpro_spy (see that note). The #2/#3 traces dropped for the same reason; template caption promises winner-vs-B&H.

## Approved By
Lead Lesandro dispatch (regeneration of defective charts); equity content change self-approved per Rule A4 and FLAGGED FOR LEAD REVIEW in the handoff.
