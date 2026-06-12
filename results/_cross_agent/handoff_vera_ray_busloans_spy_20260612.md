# Handoff: Econ Evan -> Viz Vera + Research Ray — busloans_spy (Pair #19, Mode 1)

**Date:** 2026-06-12 · **Branch:** `fix260612_busloans_spy` · **Pair:** `busloans_spy` (I20 C&I Loans → SPY)
**Producer script:** `scripts/pair_pipeline_busloans_spy.py` (deterministic; seeds fixed; rerun reproduces all numbers)
**Upstream:** Dana's dataset `data/busloans_spy_monthly_19470131_20260531.parquet` (verified vs known episodes — COVID +25.4/+30.1% YoY spike, 2009-10 −20.2% trough, z-score recomputation match). Dana's stationarity tests (`results/busloans_spy/stationarity_tests_20260612.csv`) reviewed and CONFIRMED, not re-run.

## 1. Lead-lag verdict (headline — Ray, lead with this)

**BUSLOANS LAGS SPY. It does not lead.** The lagging-indicator hypothesis is confirmed, not merely suspected:

| Evidence | BUSLOANS → SPY (forward) | SPY → BUSLOANS (reverse) |
|---|---|---|
| Toda-Yamamoto Granger (lags 1–12, d_max=1) | **n.s. at every lag** (min p = 0.257 at lag 5) | **significant at every lag** (max p = 0.0115) |
| Local projections (HAC) | n.s. at h = 1/3/6/12 (all p > 0.81) | n.s. (point estimates negative h=1–6) |
| Pre-whitened CCF (AR(12), lags −20..+20) | one stray significant lag (+17, ccf 0.119) — treat as noise | no significant lag-side cells |
| Transfer entropy (tercile, 500 perms) | p = 0.81 | p = 0.50 |
| Correlation battery | best Pearson: yoy_zscore_60m vs fwd 12m, r = 0.225 (long-horizon, level-of-cycle effect) | — |

**Reverse-only Granger flag (escalated to Lead per SOP):** this is the textbook profile of a Conference Board lagging component — equities move first, loan books respond. The publishable finding is: *this pair is confirmatory/lagging; what survives is a defensive countercyclical overlay, not a forward-causal signal.* Quantile regression shows no significant slope at any tau (0.05–0.95) — no tail-dependent forward channel either.

## 2. Tournament summary

- **Grid:** 11 signals (9 Dana transforms + hmm_stress + markov_regime) × thresholds (T1 fixed p25/50/75, T2 roll p25/75, T3 z ±1.0/±1.5, T4 zero) × 3 strategy families × 2 orientations × leads {1,2,3,6,12} (L1 = real-time floor per Dana's H.8 lag doc) × lookbacks {LB36, LB60, LB120}.
- **6,100 strategy combos** (+1 benchmark row, `valid=False`, selector `signal=="BENCHMARK"` per ECON-T4). **4,396 valid** (validity: OOS Sharpe > 0.3, turnover < 24/yr, oos_n ≥ 24).
- **OOS window (ECON-OOS2, `v1_max36_25pct_cap120`):** 2018-02-28 → 2026-05-31 (100 months; SPY-bound sample = 400 months from 1993-02). Record: `results/busloans_spy/oos_split_record.json`. Consumers read this file; do not recompute.
- **Winner (ECON-T3 cascade, resolved at step 1, no tie — no tie note):**
  `busloans_mom` (MoM loan growth) / T2_roll_p25 / **P1_long_cash counter** / L6 / LB36 — long SPY only when 6-month-lagged MoM loan growth is in the bottom quartile of its trailing 36m range; otherwise cash.

| Metric | Winner | Buy & Hold | Δ |
|---|---|---|---|
| OOS Sharpe | **1.50** | 0.89 | +0.61 |
| OOS ann. return | 10.7% | 14.8% | −4.2pp |
| OOS max drawdown | **−1.0%** | −23.9% | +22.9pp |
| Trades / turnover | 24 / 2.88 yr⁻¹ | 0 | |

Suggested `strategy_objective` for Ray to confirm: **min_mdd** (the DD reduction dominates; the strategy gives up return).

### Robustness caveats (must appear in narrative — do not soften)
1. **Bootstrap p = 0.066** vs resampled B&H — NOT significant at 5%.
2. **IS Sharpe 0.35 vs OOS 1.50** — IS/OOS inconsistency suggests a favorable OOS draw, not a stable edge.
3. **CP1 durability: `episode_concentrated`** — COVID episode Sharpe 2.75; 2022 rates-shock episode spent entirely in cash (Sharpe 0.00 = flat, not a loss); dot-com/GFC outside OOS window (insufficient_data).
4. **Rolling 24M correlation: `sign_unstable`** (sign agreement 0.42).
5. Mean OOS exposure 0.25 — most of the DD advantage is being in cash.
6. Structural break: NOT flagged (sup-F 3.60 at 2002-10-31, bootstrap p = 0.30).
7. Returns gross of costs; at 5 bps and 2.88 turnover the Sharpe haircut is negligible (see `tournament_validation_20260612/transaction_costs.csv`).

## 3. ECON-SR1 reconciliation (strategy_returns artifact)

Canonical series: `results/busloans_spy/strategy_returns_20260612.csv` (date, position, strategy_return, bh_return; monthly; position on row t is the accrual weight for month t, signal lagged L6 — execution lag already applied). Source: pipeline-native derivation (same code path as tournament evaluation). Chart producers consume this file, never re-derive.

| Metric | Computed from series | winner_summary | Diff | Verdict |
|---|---|---|---|---|
| oos_sharpe | 1.499893 | 1.4999 | −7e-06 | PASS |
| oos_max_drawdown | −0.01019 | −0.0102 | 1e-05 | PASS |
| oos_ann_return | 0.106654 | 0.1067 | −4.6e-05 | PASS |

## 4. DPS-SCD1 numbers (Ray quotes these verbatim)

- Valid strategy combos: **4,396** (of 6,100 strategy rows; benchmark excluded per ECON-T4)
- Median OOS Sharpe across valid combos: **0.739** (below B&H 0.894 — the median strategy does NOT beat buy-and-hold)
- Winner rank: **1 of 4,396**, unique at cascade step 1 (no ties)

## 5. ECON-H4 chart handoff table (Vera)

| method | result_file | expected_chart | status |
|---|---|---|---|
| Correlation battery | results/busloans_spy/core_models_20260612/correlations.csv | signal×horizon heatmap (Pearson) | ready |
| Pre-whitened CCF | results/busloans_spy/core_models_20260612/ccf_prewhitened.csv | CCF bars ±CI, lags −20..+20 | ready |
| Granger (summary) | results/busloans_spy/core_models_20260612/granger_causality.csv | both-direction p-value comparison | ready |
| Granger by-lag | results/busloans_spy/granger_by_lag.csv | F-stat by lag bars + significance line | ready |
| Local projections | results/busloans_spy/core_models_20260612/local_projections.csv | IRF with CI band (fwd + rev panels) | ready |
| Transfer entropy | results/busloans_spy/core_models_20260612/transfer_entropy.csv | two-bar TE comparison | ready |
| Quantile regression | results/busloans_spy/core_models_20260612/quantile_regression.csv | coef-by-tau with CI band | ready |
| HMM regime | results/busloans_spy/core_models_20260612/hmm_states.parquet + hmm_summary.csv | regime probability timeline | ready |
| Regime quartiles | results/busloans_spy/regime_quartile_returns.csv | Q1–Q4 ann-return bars | ready |
| Tournament | results/busloans_spy/tournament_results_20260612.csv | 5D heatmap (signal×lead, max Sharpe) | ready |
| Equity curves | results/busloans_spy/strategy_returns_20260612.csv | winner vs B&H cumulative + drawdown | ready |
| Sub-period Sharpe | results/busloans_spy/subperiod_sharpe.csv | episode bars (note 2 insufficient_data) | ready |
| Rolling correlation | results/busloans_spy/rolling_correlation_busloans_spy.csv | 24M rolling corr timeline | ready |
| Structural break | results/busloans_spy/structural_break_busloans_spy.json | annotation only (not flagged) | ready |

**Units note:** `tournament_results_20260612.csv` metrics are RATIOS (decimal), not percent — see its `_manifest.json`. CP2 artifacts (rolling Sharpe/Granger) intentionally absent: `regime_story: false` in `signal_scope.json`.

## 6. Other artifacts

`winner_summary.json` (schema-valid, v1.1.0, validated pre-save), `tournament_winner.json` (META-TWJ deltas), `winner_trade_log.csv` (400 rows) + `winner_trades_broker_style.csv` (84 events, 5 bps), `kpis.json`, `signal_scope.json` (ECON-UD tables), `analyst_suggestions.json` (1 entry: SLOOS standards as the leading twin of this credit channel), `design_note.md` (Rule C1 monthly-pair deviations), `oos_split_record.json`, manifests, `signals_20260612.parquet` (committed via `git add -f` per ECON-DS2).

## 7. Open items / A2A

- **None blocking.** No Dana artifact found wrong; no A2A-candidate questions — handoff + sidecars answered everything.
- Escalation to Lead (informational, per SOP batch reverse-causality rule): pair is **Reverse-only** in the Granger table. Recommend the portal narrative be framed as "confirmatory indicator with a defensive overlay strategy", not as a forecasting signal.
- `interpretation_metadata.json`: Evan-owned fields written (observed_direction=countercyclical, direction_consistent=true vs Dana's provisional "mixed", confidence=**low**, key_finding). Ray owns `expected_direction`/`mechanism`/final `strategy_objective` — suggested bucket: min_mdd.

— Econ Evan
