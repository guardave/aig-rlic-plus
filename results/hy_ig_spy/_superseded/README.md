# Superseded hy_ig_spy artifacts (retired 2026-10-16, branch fix261016_hmm_causal)

These files are kept unchanged for audit (ECON-T5: published tournament CSVs are immutable).
No app page, gate or pipeline reads them as current results. The current results carry
DATE_TAG 20261016 in `results/hy_ig_spy/`.

Why they were retired:

- `signals_20260422.parquet`: its `hmm_2state_prob_stress` and `ms_2state_stress_prob` columns
  came from models fit on the FULL 2000-2026 sample, using forward-backward SMOOTHED
  probabilities (`GaussianHMM.predict_proba`, `MarkovRegression.smoothed_marginal_probabilities`).
  The probability at date t used data after t, which is look-ahead. The MS model also had SPY
  returns in its likelihood. The 20261016 pipeline still reads this file, but only for
  `hmm_lookahead_audit_20261016.json`.
- `tournament_results_20260422.csv`, `tournament_results_20260715.csv`, and
  `lead_*_20260715.csv` / `strategy_returns_20260715.csv`: these selected
  S6_hmm_stress/T4_hmm_0.5/P2/L0 (OOS Sharpe 1.4083, HAC t 3.80) by OOS-argmax. That used the
  smoothed probabilities above, and the L0 grid point sits below the ~1-day OAS publication
  lag. They also had no in-sample selection (#251/#268).
- `lead_*_20260620.csv`, `lead_correlation_monthly_axis_20260620*`, `lead_sweep_manifest*`:
  monthly and weekly resampled lead sweeps for a daily pair, now replaced by the daily-axis
  lead artifacts.
- `core_models_20260422/`, `exploratory_20260422/`, `tournament_validation_20260422/`,
  `stationarity_tests_20260422.csv`, `pipeline_timing_20260422.json`: outputs of the
  20260422 pipeline. Its known defects were HC3 errors on overlapping returns, LP HAC maxlags
  below h-1, last-day monthly Granger aggregation, and validation replays on sliced windows.
- `handoff_*_20260422.md`, `qa_verification_10g_20260422.md`: handoff and QA notes for the
  superseded winner.
