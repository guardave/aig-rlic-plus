# Evan handoff: hy_ig_spy (20261017) — causal regime rebuild

- Winner (D9 lead plateau on IS, common IS window 2006-05-03..2019-09-30): **S3b_pctrank_1260d / T1_p85 / P1 / L21** (trading days; +1 execution day)
- IS Sharpe 0.8880 (SPY IS 0.5122); OOS Sharpe 0.5746 (HAC t 1.71) vs SPY B&H 0.8129
- OOS ann. return 9.3%, max DD -33.7%; OOS trades 32 (4.71/yr); full-sample trades 71 (3.29/yr)
- Grid: leads [1, 5, 21, 63, 126, 252]; 1542 combos, 1327 IS-valid (1327 distinct position series)
- Raw IS argmax (isolated-peak sensitivity, not the selection rule): S4b_roc_63d|T2_rp75|P1|countercyclical|252 IS 0.962135
- Stable lead range (D9 plateau): [5, 21, 63]
- Previously published S6_hmm_stress/T4_hmm_0.5/P2/L0 1.4083 (HAC t 3.80) relied on smoothed full-sample HMM probabilities: see hmm_lookahead_audit_20261017.json

Files: tournament_results_20261017.csv, null_tournament_20261017.csv, lead_curve_20261017.csv, track_summary.json, signals_20261017.parquet,
strategy_returns_20261017.csv, lead_*_20261017.csv, core_models_20261017/, exploratory_20261017/,
tournament_validation_20261017/, regime_quartile_forward_tests_20261017.csv, hmm_lookahead_audit_20261017.json.
Generated: 2026-10-17T15:25:42Z
