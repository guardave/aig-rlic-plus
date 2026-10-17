# Evan handoff: hy_ig_spy (20261016) — causal regime rebuild

- Winner (IS argmax, common IS window 2006-05-02..2019-09-30): **S4b_roc_63d / T2_rp75 / P1 / L252** (trading days; +1 execution day)
- IS Sharpe 0.9620 (SPY IS 0.5150); OOS Sharpe 0.3442 (HAC t 1.01) vs SPY B&H 0.8129
- OOS ann. return 6.2%, max DD -33.7%; OOS trades 110 (16.19/yr); full-sample trades 288 (11.8/yr)
- Grid: leads [1, 5, 21, 63, 126, 252]; 2178 combos, 1990 IS-valid (1354 distinct position series)
- Legacy OOS-argmax (comparison only): {'signal': 'S12_mom_252d', 'threshold': 'T1_p75', 'strategy': 'P2', 'direction': 'countercyclical', 'lead_value': 1, 'oos_sharpe': 1.180364, 'note': 'OOS-argmax on this grid (pre-GH#251 rule), comparison only; see legacy_oos_selection_20261016.csv'}
- Previously published S6_hmm_stress/T4_hmm_0.5/P2/L0 1.4083 (HAC t 3.80) relied on smoothed full-sample HMM probabilities: see hmm_lookahead_audit_20261016.json

Files: tournament_results_20261016.csv, legacy_oos_selection_20261016.csv, signals_20261016.parquet,
strategy_returns_20261016.csv, lead_*_20261016.csv, core_models_20261016/, exploratory_20261016/,
tournament_validation_20261016/, regime_quartile_forward_tests_20261016.csv, hmm_lookahead_audit_20261016.json.
Generated: 2026-10-16T16:47:00Z
