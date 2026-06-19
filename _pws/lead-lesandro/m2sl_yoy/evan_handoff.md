# Evan Handoff — m2sl_yoy_spy (M2 Money Supply YoY → SPY)

**Stage:** Econometrics + tournament (Mode 3). Branch `pair260619_m2sl_yoy_spy`.
**Date:** 2026-06-19. Producer: `scripts/pair_pipeline_m2sl_yoy_spy.py`. `np.random.seed(42)`.

## Winner spec
- **Signal:** `accel` = `m2sl_yoy_accel_pct` (MoM change in M2 YoY growth, i.e. money-growth acceleration, pp).
- **Threshold:** `T1_fixed_p50` (static IS-calibrated median), value **0.0523**, rule **gt** (long when acceleration above its in-sample median).
- **Lead:** L2 months (≥ L1 real-time floor; M2 H.6 publishes ~4th Tuesday for prior month). No lookahead.
- **Strategy:** `P1_long_cash`, **procyclical** orientation. Lookback `LB_NA` (static threshold).
- **Plain English:** Long SPY when lagged M2 YoY *acceleration* is above its historical median; otherwise cash. Procyclical — accelerating money growth = risk-on (liquidity channel).
- **OOS (2018-01-31 → 2026-04-30, 100 months):** Sharpe **1.69** vs B&H **0.90**; ann return **17.6%** vs 14.9%; max DD **-4.0%** vs **-23.9%**.
- Tournament: **4720** strategy combos (+1 BENCHMARK, valid=False per ECON-T4), **3369** valid. Median valid OOS Sharpe 0.71 (< B&H). Cascade resolved at step 1 (1 tied).

## Recomputed-OOS-Sharpe verification (umcsent guardrail)
Independently re-derived OOS Sharpe FROM the `winner_summary` encoded rule (signal_column + lead_value + threshold_code/value/rule + strategy_family + direction + lookback): **1.6882 vs headline 1.6882, diff -0.0000** → PASS (well within ±0.03). `signal_column = m2sl_yoy_accel_pct` confirmed present in `signals_20260619.parquet`. ECON-SR1 tournament reconciliation also PASS on all three headline metrics.

## Observed direction & lead-lag (Ray must narrate this reconciliation)
- **observed_direction = procyclical** (winner is pro-orientation, gt rule). Consistent with Ray/Dana's `expected_direction = procyclical` (liquidity channel H1). `direction_consistent = true`.
- **BUT the formal causality test is reverse-only:** Toda-Yamamoto Granger M2SL→SPY is **NOT significant at any lag 1-12** (forward NONE); SPY→M2SL **significant at lags 1,2,3,4,5,8**. So M2 YoY is effectively a coincident/lagging series w.r.t. equities — markets move first, the money aggregate responds. The tradable edge comes from the *acceleration* transform (2nd-derivative style), not from a forward-causal level relationship. **Ray: narrate the procyclical winner as a search-found defensive/timing overlay, NOT a validated forecasting signal — the reverse-only Granger verdict must be carried verbatim, same pattern as busloans/ism_services.**
- Quartile returns (concurrent, descriptive): low/mid M2-YoY quartiles Q1/Q2 Sharpe ~1.06; high-growth Q4 Sharpe 0.53 with -46.6% DD — the high-money-growth regime is the riskiest concurrently (consistent with the H1b inflation/tightening counter-channel). Report level-quartiles and the acceleration winner as **separate** stories.

## Robustness / evidence_status
- `evidence_status = found_in_search` (status field), confidence **low**. Bootstrap p = **0.025** (significant vs resampled B&H) — but no forward Granger causality, CP1-A durability `conditionally_durable` (only 1 OOS episode evaluable: COVID), rolling-corr `moderately_stable` (sign stability 0.50, full-sample r=0.07). Structural break: sup-F at 2011-10, bootstrap p=0.28, not flagged. No final exam (ECON-FE1) run — selection and evaluation share the OOS window. Next step: freeze and run ECON-FE1 on an untouched window.

## Key charts Vera needs
1. **Equity curve** winner vs B&H (OOS shaded 2018-01 →) — headline DD reduction story (-4% vs -24%).
2. **Granger by-lag bars** (`granger_by_lag.csv`) — forward M2→SPY (all n.s.) — visualizes the reverse-only verdict. Pair with reverse direction from `core_models_20260619/granger_causality.csv`.
3. **Regime quartile returns** (`regime_quartile_returns.csv`) — Q1-Q4 ann-return + Sharpe bars; main insight: high-money-growth Q4 is the riskiest regime concurrently.
4. **Tournament heatmap** (signal × threshold, colored by OOS Sharpe) from `tournament_results_20260619.csv`.
5. **Rolling 24M correlation** (`rolling_correlation_m2sl_yoy_spy.csv`) — sign instability caveat.
Main-insight sentences are in each manifest. Signal main insight: acceleration (2nd derivative) of money growth, not the level, carries the OOS edge.

## Data provenance (carry into narrative)
FRED `M2SL` live API, current vintage (1959-01 → 2026-04, SPY-bound from 1993). M2 is a **revised, SA** series; Data Master M2SL snapshot is a stale vintage (~0.5% above current FRED at recent dates). FRED = ground truth. M2SL **level is non-stationary (ADF p=0.99)** and is EXCLUDED from the signal set — only stationary growth/transform series used.

## Artifacts written (results/m2sl_yoy_spy/)
winner_summary.json, tournament_winner.json, tournament_results_20260619.csv (+manifest), winner_trade_log.csv, winner_trades_broker_style.csv (133 events), strategy_returns_20260619.csv (+meta), oos_split_record.json, evidence_status.json, granger_by_lag.csv, rolling_correlation_m2sl_yoy_spy.csv, regime_quartile_returns.csv (+manifest), structural_break_m2sl_yoy_spy.json, subperiod_sharpe.csv, signals_20260619.parquet (+manifest, 9 cols), signal_scope.json, kpis.json, analyst_suggestions.json, design_note.md, pipeline_timing_20260619.json, core_models_20260619/ (correlations, ccf_prewhitened, granger_causality, transfer_entropy, local_projections, quantile_regression, predictive_regressions, diagnostics_summary, hmm_states.parquet/+summary, markov_*), tournament_validation_20260619/ (bootstrap, stress_tests, transaction_costs). Updated interpretation_metadata.json (evan-owned fields only). Appended `m2sl_accel` to docs/schemas/signal_code_registry.json (ECON-DS3 append-only, source_method=roc).

## BLOCKED / flag to Lead
- **Pre-existing (NOT my regression):** `docs/schemas/signal_code_registry.json` fails its own schema at HEAD — the ism_services entries (signals 5-11) use `source_method` values (`level`, `threshold_gap`, `difference`, `threshold_flag`) not in the schema enum. My appended `m2sl_accel` entry uses a valid enum (`roc`). Recommend a separate cleanup wave to bring the legacy ism entries into enum compliance.
