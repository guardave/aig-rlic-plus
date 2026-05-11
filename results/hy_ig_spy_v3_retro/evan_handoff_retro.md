# Evan Handoff — hy_ig_spy_v3_retro
Generated: 2026-05-11T17:15:31Z

## Split Dates (ECON-OOS4 Three-Period)

| Window      | Start          | End            | N Days |
|-------------|----------------|----------------|--------|
| In-Sample   | 2000-01-03 | 2018-10-03 | 4893 |
| Validation  | 2018-10-04 | 2025-01-13 | 1638 |
| Holdout     | 2025-01-14 | 2025-12-31 | 252 |

## Winner Rule

| Field           | Value            |
|-----------------|------------------|
| Signal code     | S6_hmm_stress |
| Threshold code  | T4_hmm_0.5 |
| Strategy code   | P2 |
| Lead days       | 0 |
| Direction       | countercyclical   |

## Validation OOS Sharpe: 1.2427

## ECON-FE1 Condition Results (Holdout)

| Condition | Pass | Value | Threshold | Description |
|-----------|------|-------|-----------|-------------|
| C01_holdout_sharpe_positive | PASS | 1.6116 | 0.0 | Holdout Sharpe > 0 |
| C02_holdout_sharpe_vs_threshold | PASS | 1.6116 | 0.3 | Holdout Sharpe >= 0.3 |
| C03_bootstrap_ci_positive | FAIL | -0.3455 | 0.0 | Block bootstrap 2.5th percentile > 0 |
| C04_deflated_sharpe_pass | FAIL | 0.0000 | 0.05 | DSR p-value >= 0.05 (not over-fitted) |
| C05_excess_return_positive | FAIL | -0.0510 | 0.0 | Excess ann. return vs B&H > 0 |
| C06_max_drawdown_acceptable | PASS | -0.0590 | -0.3 | Max drawdown > -30% |
| C07_drawdown_vs_benchmark | PASS | 0.1286 | 0.0 | Strategy max DD shallower than B&H max DD |
| C08_val_sharpe_consistency | PASS | 1.2427 | 0.3 | Validation OOS Sharpe >= validity threshold |
| C09_holdout_n_sufficient | PASS | 252.0000 | 200 | Holdout has >= 200 observations |
| C10_sharpe_degradation_moderate | PASS | -0.3689 | 0.5 | Sharpe degradation val->holdout <= 0.5 |

## Key Metrics Summary

- Holdout Sharpe: 1.6116
- Holdout Ann. Return: 14.5873%
- B&H Ann. Return: 19.6898%
- Excess Return: -5.1025%
- Holdout Max Drawdown: -5.8973%
- B&H Max Drawdown: -18.7552%
- Block Bootstrap Sharpe CI (block=21, n=10000): [-0.3455, 3.6777]
  - Block size: 21 trading days; holdout obs: 252; effective blocks: ~12
  - Wide CI is genuine low-power artefact from ~12 blocks — not a bug.
- DSR Expected Max SR: 2.6701
- DSR p-value: 1.000000e-15  (fixed: norm.sf(-z) to prevent underflow; clamped >= 1e-15)
- n_trials_effective: 150

## Final Status: **needs_final_exam** (7/10 conditions pass)

## Flags
- econ_oos4: true
- retro_apply: true (retro-apply fork; tournament not re-run — column fix only)

## Scope Boundary
Evan scope ends here. No portal pages, charts, or narrative produced.