# Vera Handoff — hy_ig_spy_v3_retro
Generated: 2026-05-11

## Charts Produced

| Chart | Full Path | Disposition |
|-------|-----------|-------------|
| equity_curves_holdout | output/charts/hy_ig_spy_v3_retro/plotly/equity_curves_holdout.json | consumed |
| equity_curves_validation | output/charts/hy_ig_spy_v3_retro/plotly/equity_curves_validation.json | consumed |
| signal_distribution | output/charts/hy_ig_spy_v3_retro/plotly/signal_distribution.json | consumed |
| drawdown_comparison | output/charts/hy_ig_spy_v3_retro/plotly/drawdown_comparison.json | consumed |

Each chart has a paired `_meta.json` sidecar (VIZ-V8 compliant).

## Data Cross-Checks

- Winner signal `S6_hmm_stress` maps to column `hmm_2state_prob_stress` in `results/hy_ig_spy/signals_20260422.parquet` (6863 obs, full history available).
- Threshold (T4_hmm_0.5): fixed at **0.5** (per Evan handoff spec; not a data-derived percentile).
- Evan holdout Sharpe confirmed: 1.6116 (from `evan_handoff_retro.md`).
- Validation Sharpe confirmed: 1.2427 (from `evan_handoff_retro.md` and `winner_summary.json`).
- B&H holdout max DD from Evan: -18.7552% — strategy holdout max DD: -5.8973%.
- retro_apply flag: true (tournament not re-run — column fix only, per Evan).

## META-SRV Evidence

```
ls -la output/charts/hy_ig_spy_v3_retro/plotly/

total 280
-rw-r--r-- 1 vscode vscode  24549 May 11 17:18 drawdown_comparison.json
-rw-r--r-- 1 vscode vscode    433 May 11 17:18 drawdown_comparison_meta.json
-rw-r--r-- 1 vscode vscode  25485 May 11 17:18 equity_curves_holdout.json
-rw-r--r-- 1 vscode vscode    444 May 11 17:18 equity_curves_holdout_meta.json
-rw-r--r-- 1 vscode vscode 124420 May 11 17:18 equity_curves_validation.json
-rw-r--r-- 1 vscode vscode    453 May 11 17:18 equity_curves_validation_meta.json
-rw-r--r-- 1 vscode vscode  80453 May 11 17:18 signal_distribution.json
-rw-r--r-- 1 vscode vscode    496 May 11 17:18 signal_distribution_meta.json
```

## Scope Boundary
Vera scope ends here. No portal pages or narrative produced.
