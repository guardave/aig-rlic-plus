# Vera Handoff — hy_ig_spy_v3_rerun
Generated: 2026-05-11

## Charts Produced

| Chart | Full Path | Disposition |
|-------|-----------|-------------|
| equity_curves_holdout | output/charts/hy_ig_spy_v3_rerun/plotly/equity_curves_holdout.json | consumed |
| equity_curves_validation | output/charts/hy_ig_spy_v3_rerun/plotly/equity_curves_validation.json | consumed |
| signal_distribution | output/charts/hy_ig_spy_v3_rerun/plotly/signal_distribution.json | consumed |
| drawdown_comparison | output/charts/hy_ig_spy_v3_rerun/plotly/drawdown_comparison.json | consumed |

Each chart has a paired `_meta.json` sidecar (VIZ-V8 compliant).

## Data Cross-Checks

- Winner signal `S2a_zscore_252d` maps to column `hy_ig_zscore_252d` in `results/hy_ig_spy/signals_20260422.parquet`.
  - NOTE: `hy_ig_zscore_252d` in `data/hy_ig_spy_daily_latest.parquet` contains only 499 non-NaN values starting 2024-02-02 — insufficient for in-sample threshold computation. Signal sourced from signals parquet (6664 non-NaN from 2000-10-06) instead.
- Threshold (T2_rp75): 75th percentile of `hy_ig_zscore_252d` over in-sample (2000-01-03 to 2018-10-03) = **0.7278**.
- Evan holdout Sharpe confirmed: 0.8459 (from `winner_summary.json` and `evan_handoff_rerun.md`).
- Validation Sharpe confirmed: 1.2000 (from `evan_handoff_rerun.md`).
- B&H holdout max DD from Evan: -18.7552% — strategy holdout max DD: -5.0790%.

## META-SRV Evidence

```
ls -la output/charts/hy_ig_spy_v3_rerun/plotly/

total 276
-rw-r--r-- 1 vscode vscode  24634 May 11 17:18 drawdown_comparison.json
-rw-r--r-- 1 vscode vscode    433 May 11 17:18 drawdown_comparison_meta.json
-rw-r--r-- 1 vscode vscode  25390 May 11 17:18 equity_curves_holdout.json
-rw-r--r-- 1 vscode vscode    436 May 11 17:18 equity_curves_holdout_meta.json
-rw-r--r-- 1 vscode vscode 124375 May 11 17:18 equity_curves_validation.json
-rw-r--r-- 1 vscode vscode    445 May 11 17:18 equity_curves_validation_meta.json
-rw-r--r-- 1 vscode vscode  70555 May 11 17:18 signal_distribution.json
-rw-r--r-- 1 vscode vscode    491 May 11 17:18 signal_distribution_meta.json
```

## Scope Boundary
Vera scope ends here. No portal pages or narrative produced.
