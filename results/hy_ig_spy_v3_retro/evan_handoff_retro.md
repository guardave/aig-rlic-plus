# Evan Handoff — hy_ig_spy_v3_retro

Generated: 2026-05-09T08:27:36Z

## Split Dates (Three-Period, ECON-OOS4)

| Period | Start | End | Days |
|--------|-------|-----|------|
| In-Sample (IS) | 2000-01-03 | 2018-10-03 | 4893 |
| Validation | 2018-10-04 | 2025-01-13 | ~1638 |
| Holdout | 2025-01-14 | 2025-12-31 | 252 |

ECON-OOS2 formula: val_months = min(max(36, round(311×0.25)), 120) = 78

## Original hy_ig_spy Winner Rule

- Signal: S6_hmm_stress
- Threshold: T4_hmm_0.5
- Strategy: P2
- Lead days: 0
- Original OOS Sharpe (2019-10-01 to 2026-04-22): 1.4083

## Re-Tournament Result (IS + Validation Only)

- New winner: S6_hmm_stress / T4_hmm_0.5 / P2 / L0
- Validation Sharpe (new window): 1.2427
- Validation Ann Return: 10.88%
- Validation MDD: -8.5%

**Winner changed vs original hy_ig_spy: NO**

| | Original OOS Sharpe | New Validation Sharpe |
|--|---------------------|----------------------|
| S6_hmm_stress/T4_hmm_0.5/P2 | 1.3530 | 1.2427 |

## Final Exam — Holdout (2025-01-14 to 2025-12-31)

| Metric | Strategy | B&H |
|--------|----------|-----|
| Sharpe | 1.6116 | 1.0232 |
| Ann Return | 14.59% | 19.69% |
| MDD | -5.9% | -18.8% |
| DSR | 0.9419 | — |
| Boot CI 95% | [-0.345, 3.678] | — |
| Boot % positive | 94.4% | — |

## ECON-FE1 Condition Results (7/10 passed)

| Condition | Result |
|-----------|--------|
| C1_sharpe_positive | PASS |
| C2_sharpe_gt_0.5 | PASS |
| C3_beats_bh_sharpe | PASS |
| C4_mdd_lt_20pct | PASS |
| C5_mdd_better_than_bh | PASS |
| C6_boot_ci_lo_positive | FAIL |
| C7_boot_pct_pos_gt90 | PASS |
| C8_dsr_gt_0.95 | FAIL |
| C9_ann_return_positive | PASS |
| C10_alpha_positive | FAIL |

## Evidence Status

**CONDITIONAL_PASS** — 7/10 conditions met but key robustness gates (DSR/CI) may be borderline.

## Output Files

- `results/hy_ig_spy_v3_retro/oos_split_record.json`
- `results/hy_ig_spy_v3_retro/tournament_results_retro_20260509.csv`
- `results/hy_ig_spy_v3_retro/winner_summary.json`
- `results/hy_ig_spy_v3_retro/final_exam_results_20260509.json`
- `results/hy_ig_spy_v3_retro/evidence_status.json`
- `results/hy_ig_spy_v3_retro/evan_handoff_retro.md`
