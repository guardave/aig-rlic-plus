# Evan handoff: hy_ig_spy (20261017) — causal regime rebuild

- Winner (D9 lead plateau on IS, common IS window 2006-05-02..2019-09-30): **S1_spread_level / T2_rp75 / P1 / L21** (trading days; +1 execution day)
- IS Sharpe 0.9207 (SPY IS 0.5150); OOS Sharpe 0.3123 (HAC t 0.87) vs SPY B&H 0.8129
- OOS ann. return 3.9%, max DD -37.0%; OOS trades 56 (8.24/yr); full-sample trades 124 (4.85/yr)
- Grid: leads [1, 5, 21, 63, 126, 252]; 1542 combos, 1354 IS-valid (1354 distinct position series)
- Raw IS argmax (isolated-peak sensitivity, not the selection rule): S4b_roc_63d|T2_rp75|P1|countercyclical|252 IS 0.961997
- Stable lead range (D9 plateau): [1, 5, 21]
- Previously published S6_hmm_stress/T4_hmm_0.5/P2/L0 1.4083 (HAC t 3.80) relied on smoothed full-sample HMM probabilities: see hmm_lookahead_audit_20261017.json

Files: tournament_results_20261017.csv, null_tournament_20261017.csv, lead_curve_20261017.csv, track_summary.json, signals_20261017.parquet,
strategy_returns_20261017.csv, lead_*_20261017.csv, core_models_20261017/, exploratory_20261017/,
tournament_validation_20261017/, regime_quartile_forward_tests_20261017.csv, hmm_lookahead_audit_20261017.json.
Generated: 2026-10-17T13:22:58Z
