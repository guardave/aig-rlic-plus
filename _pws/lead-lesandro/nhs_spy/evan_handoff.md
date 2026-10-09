Handoff: Econ Evan -> Viz Vera / Research Ray / AppDev Ace

Pair: nhs_rebuilt_spy (New Home Sales NSA -> SPY), Mode 2.

Winner: yoy_accel / T3_zscore_1.0 / P3_long_short (counter) / L13 / LB36
  OOS Sharpe 1.5439 vs B&H 0.9538 | DD -0.1295 vs -0.2393 | ann ret 0.2396 vs 0.1563
  Direction: countercyclical | valid combos 9971/14300 | cascade step 1 | ties@1 1
  Bootstrap p=0.069 | durability 'conditionally_durable' | rolling-corr 'moderately_stable' | break flagged False (1999-07-31)

Lead-lag: Toda-Yamamoto Granger NHS->SPY significant at lags [11]; SPY->NHS significant at lags [1, 2, 3]. Reverse-LP flag: True.

NSA note for Ray/Vera: this indicator is NOT seasonally adjusted; every signal is YoY or STL-deseasonalised.
Charts/narrative must NOT plot or describe the raw NSA level as a signal. The headline signal is
'nhs_yoy_accel' (nhs_yoy_accel_pct).

Key artifacts under results/nhs_rebuilt_spy/: winner_summary.json, strategy_returns_20261008.csv,
winner_trade_log.csv, tournament_results_20261008.csv, core_models_20261008/, regime_quartile_returns.csv,
subperiod_sharpe.csv, rolling_correlation_nhs_rebuilt_spy.csv, kpis.json, signal_scope.json, evidence_status.json.

evidence_status = found_in_search (no final exam yet). Ray to set strategy_objective (suggested: max_sharpe).
