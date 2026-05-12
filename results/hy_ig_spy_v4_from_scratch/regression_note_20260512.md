# Regression Note — hy_ig_spy_v4_from_scratch
**Date:** 2026-05-12  
**Author:** Econ Evan  
**Purpose:** Prior-version observation + changes from prior v4 run

---

### Prior-version observation

Prior v4 run (same date tag 20260512, same pipeline script) was executed on 35 monthly observations (2023-06-30 to 2026-04-30) due to FRED ICE BofA OAS 3-year licensing restriction.

| Field | Prior (35-obs run) | This run (354-obs) |
|-------|-------------------|-------------------|
| Total obs | 35 months | 354 months |
| OOS split design | two_period_data_constrained | three_period |
| IS end | 2025-03-31 | 2014-07-31 |
| OOS window | 2025-06-30 – 2025-12-31 (7 mo) | 2014-08-29 – 2020-06-30 (71 mo) |
| Holdout window | 2026-01-31 – 2026-04-30 (4 mo) | 2020-07-31 – 2026-05-29 (71 mo) |
| Tournament combos | ~816 | 1908 |
| Tournament winner | S4a_roc_1m/T1_p60/P2/L1 | S2c_zscore_36m/T3_z0.0/P1/L1 |
| OOS Sharpe | 5.18 (on 7 months — meaningless) | 1.32 (on 71 months — reliable) |
| FE1 status | failed_final_exam (structural data constraint) | failed_final_exam (genuine finding) |
| Failure reason | Data constraint (35 obs) | Holdout Sharpe=0.31 < 0.50 floor; negative excess return in 2020-2026 |

---

### Changes from prior version

1. **Dataset:** 35 obs → 354 obs. Root cause of prior failure resolved (Dana delivered full xlsx history + FRED tail splice). Column naming unchanged.
2. **OOS split design:** two_period_data_constrained → three_period (60/20/20). IS=212mo, OOS=71mo, Holdout=71mo.
3. **Feature engineering:** Added zscore_36m, pctrank_36m signals (longer lookbacks meaningful on full sample). Rolling windows expanded from min_periods=n//6 to standard 12/24/36 monthly.
4. **Tournament:** Added T3_z (z-score threshold) levels {0.0, 0.5, 1.0, 1.5, 2.0}; expanded percentile thresholds {40, 50, 60, 70, 75, 80, 85}; included T4_hmm {0.3, 0.5, 0.7}. Lookback for position sizing changed from LB12 to LB24 (appropriate for full sample).
5. **Transaction costs:** Applied 5 bps per side inline in tournament (pos_diff * 0.0005). Prior run also applied 5 bps — method unchanged, but now explicit in return series.
6. **Transfer entropy:** Fixed numpy/pandas dtype error (`pd.cut` on ndarray → wrap in `pd.Series`). TE now produces valid results.
7. **Structural break note:** Updated from "n=35, unreliable" to full-sample CUSUM analysis.
8. **FE1 failure character changed:** Prior failure was structural (data unavailable). This failure is a genuine economic finding: the credit-spread defensive signal underperformed buy-and-hold on the 2020-2026 holdout (COVID recovery rally + 2023-26 bull market), where a defensive positioning from high spreads was the wrong call.

---

### Unchanged

All mandatory Rule C1 methods preserved: correlations, CCF, Granger, transfer entropy, local projections, quantile regression, HMM. File naming within `core_models_20260512/` is identical to prior version. evidence_status schema v1.2.0 unchanged.

---

### Impact assessment

- **Prior winner (roc_1m on 7-month OOS):** Economically meaningless — 7 observations produce a Sharpe of 5+ from noise.
- **New winner (zscore_36m on 71-month OOS):** Sharpe=1.32 vs B&H 0.71 in OOS. Delta Sharpe=+0.62, MDD improvement from -20.5% to -6.4%. Economically coherent: when 36-month z-score is below zero (spread below its 3-year mean), signal goes long — countercyclical defensive strategy that outperformed during 2014-2020 when credit stress preceded equity weakness.
- **FE1 holdout failure is genuine:** 2020-07 to 2026-05 was dominated by post-COVID recovery + 2023-26 equity bull market. A defensive credit strategy systematically underperformed during this period. This is a valid finding: the strategy works in pre-2020 regimes but has not confirmed on post-COVID data.

---

### Removed

No content removed from prior version. All methods produced in prior run are also present in this run, with expanded outputs. The `structural_constraint` field in final_exam_results no longer applies (constraint resolved) and has been omitted from this version's output.

---

**Approved by:** Lesandro (Evan's lane — producer self-verification, META-SRV)
