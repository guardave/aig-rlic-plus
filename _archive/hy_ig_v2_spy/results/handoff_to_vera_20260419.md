# Handoff to Vera — HY-IG v2 × SPY Evidence Page Chart Production

**From:** Econ Evan
**To:** Viz Vera
**Date:** 2026-04-19
**Pair:** `hy_ig_v2_spy`
**Rule cited:** ECON-H4 (per-method chart artifact handoff)
**Stakeholder items addressed (indirectly via explicit chart production):** S18-8 (quartile-return bar chart on CCF Evidence), S18-11 (standalone Granger chart, no silent fallback to Local Projections).

## Per-method chart table

All paths are absolute-from-repo-root unless prefixed with `results/hy_ig_v2_spy/`.

| method              | result_file                                                                      | expected_chart                                                            | status  |
|---------------------|----------------------------------------------------------------------------------|---------------------------------------------------------------------------|---------|
| Correlation         | `results/hy_ig_v2_spy/exploratory_20260410/correlations.csv`                     | Correlation matrix heatmap (Pearson/Spearman/Kendall/distance by horizon) | ready   |
| Granger             | `results/hy_ig_v2_spy/granger_by_lag.csv`                                        | F-statistic by lag bar chart with α=0.05 F-critical horizontal line       | ready   |
| CCF                 | `results/hy_ig_v2_spy/core_models_20260410/ccf_prewhitened.csv`                  | Pre-whitened CCF lag bars (lags −20 to +20) with 95% CI bands             | ready   |
| Local Projections   | `results/hy_ig_v2_spy/core_models_20260410/local_projections.csv`                | Jordà IRF coefficient plot (horizon on x, coef + CI on y)                 | ready   |
| Regime (HMM)        | `results/hy_ig_v2_spy/core_models_20260410/hmm_states_2state.parquet`            | HMM stress-probability timeline with regime shading                       | ready   |
| Quantile regression | `results/hy_ig_v2_spy/core_models_20260410/quantile_regression.csv`              | Quantile coefficient plot across τ ∈ {0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95} | ready   |
| Transfer entropy    | `results/hy_ig_v2_spy/core_models_20260410/transfer_entropy.csv`                 | Directional TE bar chart (credit→equity vs equity→credit) with permutation p annotations | ready   |
| Quartile returns    | `results/hy_ig_v2_spy/regime_quartile_returns.csv`                               | Q1–Q4 annualized SPY return bars, colored by sign; methodology in sidecar `regime_quartile_returns_methodology.md` | ready   |

## Sign conventions (for chart encoding)

- HY-IG spread: higher = more credit stress. Use the project's standard "stress = red" / "calm = green" palette where applicable.
- Granger F-stat: larger is stronger evidence against the null. Significance line at F-critical(α=0.05, df_num, df_den) — note df varies by lag, so place the threshold line per-bar or annotate the lag-specific critical values in the hover text.
- Quartile returns: Q1 → Q4 is low-spread → high-spread; the expected pattern is declining annualized SPY returns (Q1 positive, Q4 negative). Use a diverging palette so the sign flip between Q2 and Q4 is visible.

## Non-negotiables (GATE-25 compliance)

- **No silent fallback.** The Granger chart MUST consume `granger_by_lag.csv` and render the F-statistic-by-lag view. Rendering the Local Projections chart in its place (the v2 bug, stakeholder S18-11) is a completeness-gate failure.
- **No silent drop.** The quartile-return bar chart MUST be rendered on the CCF Evidence page. It is the S18-8 artifact.
- Any `status = blocked` in future reruns triggers a "chart pending" placeholder per GATE-25, not a fallback to a different method's chart.

## Files you may optionally regenerate from

The following are legacy/alternate versions — prefer the files above. Listed so you know what to ignore:

- `results/hy_ig_v2_spy/core_models_20260410/granger_causality.csv` — direction × lag summary table (Rule C2). Still authoritative for the direction table, NOT for the F-by-lag chart. Use `granger_by_lag.csv` for the chart.
- `results/hy_ig_v2_spy/core_models_20260410/quartile_returns.csv` — daily-observation quartile returns (Rule C2 schema). Superseded for the CCF Evidence chart by `regime_quartile_returns.csv`; retained for backward compatibility with any daily-resolution consumers.

## Contact

Questions or missing columns → ping Evan via status board. Do NOT silently substitute a different artifact path.
