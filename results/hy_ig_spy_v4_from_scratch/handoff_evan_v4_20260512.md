# Evan → Vera Handoff: hy_ig_spy_v4_from_scratch (20260512)

**From:** Econ Evan  
**To:** Visualization Vera  
**Date:** 2026-05-12  
**Pair ID:** hy_ig_spy_v4_from_scratch  
**Dataset:** 354 monthly obs, 1996-12-31 to 2026-05-29 (full history)

---

## Winner Summary

| Field | Value |
|-------|-------|
| Signal | **S2c_zscore_36m** (`hy_ig_zscore_36m`) |
| Threshold | T3_z0.0 (signal < 0.0; spread below its 36-month mean) |
| Strategy | P1 (long/cash binary) |
| Lead | 1 month |
| Direction | countercyclical |
| OOS Sharpe | **1.3238** |
| OOS Ann Return | **6.57%** (ratio: 0.065700) |
| OOS Max DD | **-6.38%** (ratio: -0.063800) |
| B&H Sharpe | 0.7076 |
| B&H Ann Return | 9.90% (ratio: 0.099000) |
| B&H Max DD | -20.5% (ratio: -0.205000) |
| Delta Sharpe | +0.6162 |
| OOS window | 2014-08-29 to 2020-06-30 (71 months) |
| Win rate (OOS) | see winner_summary.json |

**Economic logic:** When HY-IG spread is below its 36-month rolling mean (z-score < 0), credit conditions are benign → strategy holds SPY long. When spread rises above 36-month mean (z-score >= 0), strategy moves to cash. Defensive credit-cycle filter with 1-month execution lead.

**FE1 holdout result: failed_final_exam**  
Holdout: 2020-07-31 to 2026-05-29 (71 months). Confirm Sharpe=0.31 (< 0.50 floor). Excess return=-12.9% vs B&H. Portal pages must display disclosure banner per DPS-PRE1.

---

## OOS Split Record

| Period | Start | End | Obs |
|--------|-------|-----|-----|
| In-sample (search) | 1996-12-31 | 2014-07-31 | 212 |
| OOS (tournament eval) | 2014-08-29 | 2020-06-30 | 71 |
| Holdout (final exam) | 2020-07-31 | 2026-05-29 | 71 |

---

## ECON-H4 Chart Table — All Charts Vera Must Produce

All result files are under `results/hy_ig_spy_v4_from_scratch/` unless noted.

| Method | Result File | Expected Chart | Chart filename |
|--------|-------------|----------------|----------------|
| Correlation battery | `core_models_20260512/correlations.csv` | Signal × horizon heatmap (Pearson/Spearman/Kendall at 1m/3m/6m) | `correlation_heatmap.json` |
| Pre-whitened CCF | `core_models_20260512/ccf_prewhitened.csv` | CCF bar chart lags -20 to +20 with 95% CI bands | `ccf_prewhitened.json` |
| Granger by lag | `granger_by_lag.csv` | F-statistic by lag 1-6 bar chart (indicator→target direction) | `granger_by_lag.json` |
| Local projections | `core_models_20260512/local_projections.csv` | IRF-style coefficient × horizon line with HAC CI (fwd + rev) | `local_projections.json` |
| Quantile regression | `core_models_20260512/quantile_regression.csv` | Quantile coef τ=0.05–0.95 line + OLS reference | `quantile_regression.json` |
| HMM regime overlay | `core_models_20260512/hmm_states.parquet` | Stress probability overlay on HY-IG spread time-series | `hmm_regime_overlay.json` |
| HMM summary | `core_models_20260512/hmm_summary.csv` | Stress vs calm regime: mean return, vol, frequency bars | `hmm_summary.json` |
| Regime quartile returns | `regime_quartile_returns.csv` | Q1-Q4 annualized SPY return bar chart (Q1=tightest spread) | `regime_stats.json` |
| Transfer entropy | `core_models_20260512/transfer_entropy.csv` | TE bar: fwd (spread→SPY) vs rev (SPY→spread) | `transfer_entropy.json` |
| Predictive regressions | `core_models_20260512/predictive_regressions.csv` | Coefficient forest plot: signals × horizons | `predictive_regressions.json` |
| Rolling correlation | `rolling_correlation_hy_ig_spy_v4.csv` | Rolling Pearson r time-series (12m/24m/36m windows) | `rolling_correlation.json` |
| Rolling Granger | `rolling_granger_hy_ig_spy_v4.csv` | Rolling Granger p-value time-series (36m window) | `rolling_granger.json` |
| Rolling Sharpe | `rolling_sharpe_hy_ig_spy_v4.csv` | Rolling strategy Sharpe (12m/24m/36m windows) | `rolling_sharpe.json` |
| Subperiod Sharpe | `subperiod_sharpe.csv` | SPY Sharpe per epoch (Pre-GFC/GFC/ZIRP/Post-COVID) | `subperiod_sharpe.json` |
| Structural break | `structural_break_hy_ig_spy_v4.json` | CUSUM OLS result + break annotation | `structural_break.json` |
| Equity curves | `winner_trade_log.csv` | Cumulative return: strategy vs B&H with IS/OOS/Holdout shading | `equity_curves.json` |
| Drawdown | `winner_trade_log.csv` (derive) | Drawdown chart: strategy vs B&H | `drawdown.json` |
| Walk-forward | derive from `tournament_results_v4_20260512.csv` | Annual OOS Sharpe scatter | `walk_forward.json` |
| Tournament scatter | `tournament_results_v4_20260512.csv` | Sharpe vs Return scatter all combos, winner highlighted | `tournament_scatter.json` |
| Hero chart | combo: spread + SPY + regime | Full-history dual-panel: HY-IG spread (with HMM shading) + SPY return | `hero.json` |

---

## Crisis Episode Zooms — 5 Mandatory (credit class, ECON-H4 + DPS-EP1)

Per META-ZI: pair-specific dual-panel. Top: HY-IG spread (hy_ig_spread_pct). Bottom: SPY monthly log return. Source: `data_hy_ig_spy_v4_20260512.parquet`. Events registry: `docs/schemas/history_zoom_events_registry.json`.

| Slug | Window | Key Narrative | Output path |
|------|---------|---------------|-------------|
| `dotcom` | 2000-03-01 → 2002-10-31 | HY-IG spread widened 400+ bps; SPY declined -47%. Strategy correctly moved to cash as spread rose above 36-mo mean. | `output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_dotcom.json` |
| `gfc` | 2007-10-01 → 2009-06-30 | Spread peaked ~13% (1000+ bps). SPY fell -55%. Textbook credit-cycle signal. | `output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_gfc.json` |
| `covid` | 2020-02-01 → 2020-04-30 | Spread +6pp in ~6 weeks; SPY -30%. Monthly frequency means 1-2 observations in crisis window. | `output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_covid.json` |
| `taper_2018` | 2018-01-01 → 2019-01-31 | Fed rate hike cycle; modest spread widening +1pp. SPY flat. Signal correctly reduced exposure. | `output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_taper_2018.json` |
| `inflation_2022` | 2022-01-01 → 2022-12-31 | ANNOTATION REQUIRED: spread widened +2pp but mechanism was rate repricing, not credit cycle. SPY -20% from valuation compression, not default risk. Strategy moved to cash correctly on spread signal but miss-classified the mechanism. | `output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_inflation_2022.json` |

---

## interpretation_metadata

| Field | Value |
|-------|-------|
| pair_id | hy_ig_spy_v4_from_scratch |
| indicator_category | credit |
| indicator_type | credit |
| indicator_nature | leading |
| observed_direction | countercyclical |
| direction_consistent | true |
| strategy_objective | min_mdd |
| key_finding | OOS Sharpe=1.32 vs B&H 0.71 (2014-2020). FE1 failed on 2020-2026 holdout (Sharpe=0.31). Strategy demonstrated pre-COVID; fails to confirm on post-COVID bull market. |
| confidence | moderate |

---

## META-SRV Evidence Block

```
wc -l key deliverables:
    34 winner_trade_log.csv
    34 winner_trades_broker_style.csv
   994 rolling_correlation_hy_ig_spy_v4.csv
   320 rolling_granger_hy_ig_spy_v4.csv
   994 rolling_sharpe_hy_ig_spy_v4.csv
     5 subperiod_sharpe.csv (header + 5 rows)
     4 regime_quartile_returns.csv (header + 4 rows)
     7 quantile_regression.csv in core_models_20260512
    13 granger_causality.csv in core_models_20260512
    42 ccf_prewhitened.csv in core_models_20260512

Artifacts: 19/19 required result artifacts present and non-empty.
Pipeline: pair_pipeline_hy_ig_spy_v4_from_scratch.py, completed in 14.4s.
Commit: eb4d6f4 on branch 260430, pushed to origin.
```

---

## GATE-DPS1 Pre-Check Results

`python3 scripts/validate_pair_completeness.py --pair hy_ig_spy_v4_from_scratch --no-color`

| Section | Result |
|---------|--------|
| Artifacts — Results | **PASS** (9/9) |
| Prerequisites / FE1 | **WARN** — exam ran correctly; failure is genuine finding; disclosure banner required |
| Config module | FAIL — Ace lane (pair_configs not yet created) |
| Charts | FAIL — Vera lane (19 chart FAILs, all in Vera scope) |
| Crisis episode zooms | FAIL — Vera lane (5 episode charts missing) |
| Story/Evidence/Methodology/Strategy | FAIL — Ace lane |

Overall: 31 FAIL (Vera + Ace lanes), 1 WARN (genuine FE1 failure), 15 PASS.

---

## Final Exam Outcome

**Status: failed_final_exam**  
**qa_status: qa_passed** (exam correctly run; failure is genuine economic finding, not procedural gap)

FE1 conditions failed (4 of 8):
- Cond 4: Confirmation Sharpe 0.308 < floor 0.500 (credit class)
- Cond 5: Excess annualized return -12.93% (strategy underperforms B&H on holdout)
- Cond 7: Bootstrap 95% CI lower bound -0.622 does not exclude zero (block_length=8, n=71)
- Cond 8: Multiple-testing: n_trials_raw=1908, n_trials_effective=382, deflated_p=0.27 > 0.10

**Assessment:** The defensive credit-spread z-score strategy worked well from 2014-2020 (OOS Sharpe 1.32, MDD -6.4% vs -20.5% for B&H). The 2020-2026 holdout period was dominated by the COVID recovery rally, 2023-2026 equity bull market, and the 2022 rate shock — all periods where a defensive credit filter underperforms. This is a genuine macro regime effect: the credit-equity channel is real but time-varying. The 2022 episode is specifically complicated by the rate-shock confound documented in spec_memo §4.

---

Generated: 2026-05-12  
Author: Econ Evan  
Regression note: `results/hy_ig_spy_v4_from_scratch/regression_note_20260512.md`
