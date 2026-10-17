Handoff: Econ Evan -> Viz Vera / Research Ray / AppDev Ace

Pair: nhs_spy (New Home Sales NSA -> SPY), Mode 2.

Winner: contraction / T2_roll_p25 / P2_signal_strength (counter) / L9 / LB36
  OOS Sharpe 0.9318 vs B&H 0.8935 | DD -0.1353 vs -0.2393 | ann ret 0.1187 vs 0.1482
  Selected by IS Sharpe 1.4628 (B&H 0.7867) on 2002-11-30..2018-01-31
  Direction: countercyclical | IS-valid combos 5344/5500 | tie step 5
  Bootstrap p=0.469 | durability 'conditionally_durable' | rolling-corr 'moderately_stable' | break flagged False (2009-03-31)
  Superseded: hmm_stress/T2_roll_p25/LB60/P1_long_cash_pro/L0 OOS 1.4851 (smoothed HMM); causal same rule L0 1.3630, L2 0.8550

Lead-lag: Toda-Yamamoto Granger NHS->SPY significant at lags [11]; SPY->NHS significant at lags [1, 2]. Reverse-LP flag: True.

NSA note for Ray/Vera: this indicator is NOT seasonally adjusted; every signal is YoY or STL-deseasonalised.
Charts/narrative must NOT plot or describe the raw NSA level as a signal. The headline signal is
'nhs_contraction' (nhs_yoy_contraction_flag).

Key artifacts under results/nhs_spy/: winner_summary.json, strategy_returns_20261016.csv,
winner_trade_log.csv, tournament_results_20261016.csv, core_models_20261016/, regime_quartile_returns.csv,
subperiod_sharpe.csv, rolling_correlation_nhs_spy.csv, kpis.json, signal_scope.json, evidence_status.json.

evidence_status = found_in_search (no final exam yet). Ray to set strategy_objective (suggested: min_mdd).
