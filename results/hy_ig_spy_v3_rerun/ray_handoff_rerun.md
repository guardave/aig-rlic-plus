# Ray Handoff — hy_ig_spy_v3_rerun
Generated: 2026-05-11

## Narrative Files Produced

- `results/hy_ig_spy_v3_rerun/ray_narrative_rerun.md`
  - Sections: Evidence, Strategy, Methodology
  - META-SRV: `wc -l ray_narrative_rerun.md` → 28 lines

## RES-NR1 Check

RES-NR1: instrument references confirmed against `interpretation_metadata.json`.

- `indicator_id: hy_ig_spread_pct` → prose uses "HY-IG credit spread" throughout. No bare "HY" or "IG" references without context.
- `target_symbol: SPY` → prose uses "S&P 500 (SPY)" on first use, "SPY" thereafter.
- References to "buy-and-hold" and "benchmark" are non-instrument comparators, not out-of-pair instrument references.
- "VIX" is NOT referenced in the narrative text. No out-of-pair instrument references appear.

RES-NR1 whitelist: `gate_nr_comparison_whitelist = ["S&P 500", "VIX"]` — unchanged from existing `interpretation_metadata.json`. No additions needed.

## Whitelist Additions to interpretation_metadata.json

None. Existing whitelist `["S&P 500", "VIX"]` is sufficient. No modifications made to `interpretation_metadata.json`.

## Key Claims and Evidence Citations

| Claim | Source |
|-------|--------|
| Validation Sharpe 1.20 | `winner_summary.json` → `val_oos_sharpe: 1.2` |
| Holdout Sharpe 0.85 | `final_exam_results_20260511.json` → `holdout_sharpe: 0.8459` |
| 7/10 ECON-FE1 conditions pass | `evan_handoff_rerun.md` → Final Status |
| C03 FAIL: bootstrap CI lower = −1.19, ~12 blocks | `evan_handoff_rerun.md` → Block Bootstrap note |
| C04 FAIL: DSR p-value ≪ 0.05, 150 effective trials | `final_exam_results_20260511.json` → `n_trials_effective: 150` |
| C05 FAIL: excess return −14.4 pp | `final_exam_results_20260511.json` → `excess_ann_return: -0.144481` |
| Holdout MDD −5.1%, B&H MDD −18.8% | `final_exam_results_20260511.json` → metrics |
| 16 trades in holdout | `final_exam_results_20260511.json` → `holdout_period.n_trades: 16` |
| Sharpe degradation 0.35 (C10 PASS) | `final_exam_results_20260511.json` → C10 value |

## Scope Boundary

Ray scope ends here. No portal pages, charts, or config modifications produced. Handoff to Ace for rendering.
