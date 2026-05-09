# Evan Handoff — hy_ig_spy_v3_rerun
Generated: 2026-05-09T08:30:11Z

## Split Dates (ECON-OOS4 Three-Period)

| Window      | Start          | End            | N Days |
|-------------|----------------|----------------|--------|
| In-Sample   | 2000-01-03 | 2018-10-03 | 4893 |
| Validation  | 2018-10-04 | 2025-01-13 | 1638 |
| Holdout     | 2025-01-14 | 2025-12-31 | 252 |

## Winner Rule

| Field           | Value            |
|-----------------|------------------|
| Signal code     | S2a_zscore_252d |
| Threshold code  | T2_rp75    |
| Strategy code   | P1    |
| Lead days       | 0     |
| Direction       | countercyclical   |

## Validation OOS Sharpe: 1.2000

## ECON-FE1 Condition Results (Holdout)

| Condition | Pass | Value | Threshold | Description |
|-----------|------|-------|-----------|-------------|
| C01_holdout_sharpe_positive | PASS | 0.8459 | 0.0 | Holdout Sharpe > 0 |
| C02_holdout_sharpe_vs_threshold | PASS | 0.8459 | 0.3 | Holdout Sharpe >= 0.3 (equity validity threshold) |
| C03_bootstrap_ci_positive | FAIL | -1.1895 | 0.0 | Block bootstrap 2.5th percentile > 0 |
| C04_deflated_sharpe_pass | FAIL | 0.0000 | 0.05 | DSR p-value >= 0.05 (not over-fitted) |
| C05_excess_return_positive | FAIL | -0.1445 | 0.0 | Excess ann. return vs B&H > 0 |
| C06_max_drawdown_acceptable | PASS | -0.0508 | -0.3 | Max drawdown > -30% |
| C07_drawdown_vs_benchmark | PASS | 0.1368 | 0.0 | Strategy max DD shallower than B&H max DD |
| C08_val_sharpe_consistency | PASS | 1.2000 | 0.3 | Validation OOS Sharpe >= validity threshold (no regime collapse) |
| C09_holdout_n_sufficient | PASS | 251.0000 | 200 | Holdout has >= 200 observations |
| C10_sharpe_degradation_moderate | PASS | 0.3541 | 0.5 | Sharpe degradation val→holdout <= 0.5 |

## Key Metrics Summary

- Holdout Sharpe: 0.8459
- Holdout Ann. Return: 5.2417%
- B&H Ann. Return: 19.6898%
- Excess Return: -14.4481%
- Holdout Max Drawdown: -5.0790%
- B&H Max Drawdown: -18.7552%
- Block Bootstrap Sharpe CI (block=21, n=1000): [-1.1895, 2.1899]
- DSR Expected Max SR: 2.6701
- DSR p-value: 0.0000
- n_trials_raw: 2143, n_trials_effective: 150

## Final Status: **needs_final_exam** (7/10 conditions pass)

## Scope Boundary
Evan scope ends here. No portal pages, charts, or narrative produced.