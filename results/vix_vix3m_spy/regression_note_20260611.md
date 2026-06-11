# Chart Regression Note — vix_vix3m_spy — 2026-06-11

Producer: `scripts/generate_strategy_perf_charts.py` (ECON-SR1 consumer). Branch `fix260611_meta_cmp`.

## Charts Changed
- `equity_curves` (NEW — closes the META-CMP T2 gap; live page previously showed the GATE-25 "Equity curves pending" placeholder)
- `drawdown` (regenerated — replaces defective W0.5 backfill)
- `walk_forward` (regenerated — replaces defective W0.5 backfill)
- `subperiod_sharpe` (regenerated — rebuilt from Evan's ECON-SR1-reconciled `subperiod_sharpe.csv`)

## Spec Diff
| Field | Old (W0.5, 2026-05-26) | New (2026-06-11) |
|---|---|---|
| Underlying series | In-script reconstruction with two defects (threshold-code `T2_rp75` unparsed → IS-median; double countercyclical inversion). Strategy implied −96.4% full sample. | Canonical `results/vix_vix3m_spy/strategy_returns_20260611.csv` (trade-log span replay; reconciles to winner_summary EXACT) |
| Window | Full sample 2007–2025 (drawdown); OOS-2015 (walk_forward) | OOS 2020-01-01..2025-12-31 (healthy-pair convention, matches page KPI caption which quotes OOS numbers) |
| Palette | matplotlib defaults (#d62728/#888/#2ca02c) — prohibited per VIZ-V11 registry notes | okabe_ito_2026 registry roles (equity_curve/benchmark_trace/primary_data_trace) |
| NBER shading | absent (VIZ-NBER1 violation) | present + legend swatch + caption disclosure |
| walk_forward traces | strategy only | strategy + Buy & Hold benchmark (umcsent convention) |
| subperiod values | Full-OOS Sharpe −0.8814 (defective), window 2015-start | Full-OOS Sharpe +1.1295, window 2020-start (Evan round-2 CSV) |

## Rationale
W0.5 backfill series proven defective (Vera STOP report 2026-06-11; ECON-SR1 authored in response). All four charts now consume the reconciled canonical series; per-chart reconciliation results embedded in each `_meta.json` sidecar (`reconciliation` block): OOS Sharpe 1.1295/1.1295, MDD −0.2115/−0.2115, ann. return 0.1548/0.1531 — all PASS within ECON-SR1 tolerances. Drawdown chart min = −21.15% = winner_summary `oos_max_drawdown`.

## Approved By
Lead Lesandro (fix260611 dispatch, 2026-06-11): "regenerate the defective strategy-performance charts from Evan's artifacts".
