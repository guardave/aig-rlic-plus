Handoff: Econ Evan -> Viz Vera / Research Ray / AppDev Ace

Pair: nhs_spy (New Home Sales NSA -> SPY), Mode 2.

Winner: hmm_stress / T2_roll_p25 / P1_long_cash (pro) / L0 / LB60
  OOS Sharpe 1.4851 vs B&H 0.8935 | DD -0.0833 vs -0.2393 | ann ret 0.159 vs 0.1482
  Direction: procyclical | valid combos 5297/7700 | cascade step 1 | ties@1 1
  Bootstrap p=0.071 | durability 'conditionally_durable' | rolling-corr 'sign_unstable' | break flagged False (2009-03-31)

Lead-lag: Toda-Yamamoto Granger NHS->SPY significant at lags [11]; SPY->NHS significant at lags [1, 2]. Reverse-LP flag: True.

NSA note for Ray/Vera: this indicator is NOT seasonally adjusted; every signal is YoY or STL-deseasonalised.
Charts/narrative must NOT plot or describe the raw NSA level as a signal. The headline signal is
'hmm_stress' (hmm_2state_prob_stress).

Key artifacts under results/nhs_spy/: winner_summary.json, strategy_returns_20260703.csv,
winner_trade_log.csv, tournament_results_20260703.csv, core_models_20260703/, regime_quartile_returns.csv,
subperiod_sharpe.csv, rolling_correlation_nhs_spy.csv, kpis.json, signal_scope.json, evidence_status.json.

evidence_status = found_in_search (no final exam yet). Ray to set strategy_objective (suggested: max_sharpe).
