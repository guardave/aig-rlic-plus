# Design Note — phlxsox_spy (20260619)

## THE central challenge: co-movement vs genuine lead
SOX and SPY are both equities; contemporaneous daily return corr = 0.709. That is shared
market beta (CO-MOVEMENT), not predictive edge. This pipeline establishes lead exclusively through:
- Tournament lead grid starts at **L1** (no L0). A same-day SOX reading is not a forecast.
- Toda-Yamamoto Granger BOTH directions at lags >=1.
- Pre-whitened CCF (each series AR-filtered) at lags -20..+20.
- Lean on the **relative-strength** transforms (sox_spy_ratio_mom_*) that partial out common beta.
- Compare the winner against TWO benchmarks: buy & hold SPY AND **SPY-own-momentum** (63d trend, long/cash).

## Lead-lag verdict
- Toda-Yamamoto SOX→SPY significant lags: [1, 2, 3, 5, 10, 21]
- Toda-Yamamoto SPY→SOX significant lags: [1, 2, 3, 5, 10, 21]
- Pre-whitened CCF SOX-leads (lag>0) significant: [4, 6, 8, 12, 15, 16]; SPY-leads (lag<0): [-16, -15, -9, -8, -7, -6, -1]
- Verdict: Bidirectional Granger (both directions significant) — feedback, not clean lead

## Incremental edge over SPY's own momentum (the trivial-trend test)
HAC local projection of forward SPY return on SPY-own-momentum vs +lagged relative strength:
  - fwd 21d: rel-strength coef p=0.0332, incremental R²=0.00754 (adds over SPY-own-momentum=True)
  - fwd 63d: rel-strength coef p=0.0748, incremental R²=0.01292 (adds over SPY-own-momentum=False)
- Adds at some horizon: True

## Category & method coverage (Rule C1, price/intermarket)
Full correlation battery (predictive/forward, NOT contemporaneous), pre-whitened CCF, Toda-Yamamoto
Granger (both directions), transfer entropy, local projections (fwd + reverse), quantile regression,
HMM 2-state regime detection. Stationarity: Dana's tests reviewed and CONFIRMED (levels sox & sox_spy_ratio
NON-stationary, excluded as signals).

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent.
- Lead grid: L{1,5,10,21,63} trading days. position_t = rule(signal_(t−L)); strategy_return_t = position_t × spy_ret_t.
- Both orientations (pro/counter) tested.
- TWO benchmark rows (BENCHMARK=buy&hold per ECON-T4; SPY_OWN_MOMENTUM=trivial trend) — both valid=False, excluded from combo counts.
- CP2 skipped — regime_story: false. Returns gross of costs; 5bps sensitivity in tournament_validation_20260619/.

## New pair — no prior version, Rule C3 regression diff not applicable.
