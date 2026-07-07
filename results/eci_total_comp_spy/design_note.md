# Design Note — eci_total_comp_spy (20260706)

## FIRST QUARTERLY PAIR — deliberate template adaptations
All 15 prior pairs are monthly or daily. This dataset is designed on a NATIVE
QUARTERLY (quarter-end, QE-DEC) index — the monthly template was adapted, not
copied:

| Monthly convention | Quarterly adaptation here |
|---|---|
| spy_fwd_1m / _3m / _6m / _12m | `spy_fwd_1q` (~3M) / `spy_fwd_2q` (~6M) / `spy_fwd_4q` (~12M) |
| 60M rolling z-score windows | **20Q** (~5yr) windows, named `_zscore_20q` (quarter-count names, never "60m") |
| 12M trend MA | **8Q** (~2yr) MA (`_ma8q_idx`) |
| MoM / 3M / 6M momentum | QoQ (`_pct_qoq`) / 2Q (`_pct_2q`) / 4Q=YoY (`_pct_yoy`) |
| Lead grid L in months | **Lead grid L in QUARTERS; floor at L1** (pub lag, below) |

## Hypothesis (one-liner)
Does wage-inflation momentum (ECI total compensation growth) carry forward
information about SPY returns? Prior: COUNTERCYCLICAL — accelerating
compensation growth = wage-inflation pressure = tighter Fed / margin
compression = risk-off; decelerating ECI = disinflation = risk-on. ECI is a
classic LAGGING indicator (labor costs turn after the cycle). Direction and
lead-lag determined EMPIRICALLY by Evan; this note only seeds a provisional prior.

## Source & sample
- Indicator: FRED `ECIALLCIV` — Employment Cost Index: Total compensation:
  All Civilian. **Quarterly**, index Dec 2005 = 100, **SEASONALLY ADJUSTED**.
- History: **2001-Q1 to 2026-03-31** (101 quarters, ~25 years).
  Good cycle coverage (2001 recession, GFC, COVID, 2021-23 wage surge) but FEW
  observations.
- Variant note: Data Master's `ECI` sheet / Pre-master entries are the **NSA
  private-industry** ECI variants (Dec 2015 = 100) — a different variant. This
  pair uses the SA all-civilian headline series per the pair brief.
- Target: SPY quarter-end (Yahoo, auto-adjusted); controls UNRATE/DGS10/DFF
  (FRED), ^VIX (Yahoo), all quarter-end snapshots. Usable overlap = full ECI
  window: **2001-03-31 .. 2026-03-31 (101 quarters)**.

## Seasonality
Source is SA: QoQ and short-horizon transforms are seasonally CLEAN. No
NSA-contamination constraint (unlike Cass Freight). No transform-family
restriction on those grounds.

## Effective sample per transform (honesty table — few obs at quarterly freq)
- `eci_total_comp_idx`: 101 obs (starts 2001-03-31)
- `eci_total_comp_pct_qoq`: 100 obs (starts 2001-06-30)
- `eci_total_comp_pct_2q`: 99 obs (starts 2001-09-30)
- `eci_total_comp_pct_yoy`: 97 obs (starts 2002-03-31)
- `eci_total_comp_ma8q_idx`: 96 obs (starts 2002-06-30)
- `eci_total_comp_dev_trend_pct`: 96 obs (starts 2002-06-30)
- `eci_total_comp_zscore_20q`: 90 obs (starts 2003-12-31)
- `eci_total_comp_yoy_zscore_20q`: 86 obs (starts 2004-12-31)
- `eci_total_comp_accel_pct`: 99 obs (starts 2001-09-30)
- `eci_total_comp_yoy_accel_pct`: 96 obs (starts 2002-06-30)

## Stationarity (ADF/KPSS — see stationarity_tests_20260706.csv)
Level is non-stationary (trending nominal index). Growth transforms: note the
YoY series is highly persistent at quarterly frequency (slow-moving wage
inflation) — check the CSV; some growth transforms may be borderline.
Acceleration and deviation-from-trend are the cleanly stationary candidates.
Evan confirms rather than re-runs (SOP).

## No-lookahead / publication lag (CRITICAL for Evan)
BLS releases quarter Q's ECI ~1 month after quarter end (end of Jan/Apr/Jul/Oct).
At quarterly granularity the quarter-Q signal is first tradable in Q+1:
**tournament lead grid must floor at L1, with L measured in QUARTERS**
(L1 = 1 quarter ≈ 3 months; L2 ≈ 6 months; L4 ≈ 12 months). Horizon mapping
for tournament targets: `spy_fwd_1q` ≈ monthly pairs' 3M horizon, `spy_fwd_2q`
≈ 6M, `spy_fwd_4q` ≈ 12M.

## Key data-quality flags for downstream
1. **Few observations**: 101 quarters total; 20Q z-scores start ~2003-Q4/2004-Q4;
   any OOS window contains few quarters — OOS statistics high-variance. Use a
   conservative split and simple specifications; avoid dense parameter grids.
2. **2021-22 wage surge is REAL** (YoY peak 5.11%) — do not treat as outlier.
3. **YoY persistence**: wage inflation is slow-moving; expect strong
   autocorrelation in `_pct_yoy` — pre-whitening matters for CCF/Granger.
4. **Nominal stickiness**: the level almost never declines; level-based
   contraction flags are uninformative (none included).

## New pair — no prior version; Rule D1 series-preservation / regression diff N/A.

---

# Phase 1 addendum — Econometrics & Tournament (Evan, 20260706)

## Quarterly conventions (stated explicitly — first quarterly pair)
- **Annualization: Sharpe = mean/std x sqrt(4); ann_return = mean x 4; ann_vol = std x sqrt(4).**
- Lead grid **L1..L8 in QUARTERS** (L1 = pub-lag floor, BLS releases ~1 month after quarter end;
  L8 = 2yr ceiling — wage->Fed->equity transmission has no rationale beyond ~2yr and deeper leads
  eat the 101-obs sample). Tournament CSV lead column is `lead_quarters` (NOT lead_months).
- Lookbacks LB12 (~3yr) / LB20 (~5yr) quarters. Correlation horizons spy_fwd_1q/2q/4q.

## Method coverage (Rule C1, macro) & quarterly adaptations
- Correlations incl. distance (n-floor 40 quarters); horizons recorded as 63/126/252 horizon_days.
- Pre-whitened CCF at quarterly lags -8..+8 (pre-whitening ESSENTIAL — YoY wage inflation near-I(1); AR order by AIC, max 4).
- Toda-Yamamoto Granger, lags 1..4 quarters ONLY (101 obs cannot support deeper quarterly VARs), d_max=1.
- Local projections fwd+rev at 1/2/4-quarter horizons, HAC SEs.
- Quantile regression on 1q-fwd (tail taus on ~97 obs = ~5 effective tail points; interpret loosely).
- Transfer entropy: tercile-binned, 500 permutations — LOW POWER at 97 obs; retained as a directional check with caveat.
- HMM 2-state on YoY: attempted with a degeneracy guard (min 10% regime occupancy). NOTE: on a series this
  persistent the HMM splits wage-inflation LEVEL regimes (high vs low), not volatility states — still
  economically meaningful (2021-23 surge vs pre-COVID calm) but transition probabilities weakly identified.
  HMM converged and retained: True.
- Markov-switching regression spy_ret ~ yoy (2-state, switching variance).
- Stationarity: Dana's tests (stationarity_tests_20260706.csv) reviewed and CONFIRMED, not re-run.
  Growth family borderline-persistent; 20Q z-scores regime-contaminated (KPSS reject); accel family clean.
  Each tournament row carries a `stationarity_class` flag.

## Sparse grid (BINDING Dana small-sample constraint — do not explode combos on 101 points)
- Thresholds: IS percentiles {25,50,75}, zero-cross ONLY on sign-meaningful signals (accel/yoy_accel/dev_trend
  — wage growth itself never goes negative, nominal stickiness), rolling z-score +/-1.0 at LB12/LB20
  (the +/-1.5 variants and Jenks/GMM/CUSUM thresholds dropped).
- Strategies: P1 long/cash + P3 long/short x pro/counter (P2 signal-strength sizing dropped — a continuous
  sizing rule has too many effective d.o.f. for 25 OOS quarters).
- Eligibility: signal >= 60 non-NaN quarters; IS >= 40 quarters; OOS >= 20 quarters; validity
  requires OOS Sharpe > 0.3 (equity threshold) and turnover < 6 position-changes/yr.

## OOS split (ECON-OOS2, quarterly-translated)
Policy v1_max36_25pct_cap120 in native quarterly units: span = min(max(12q, round(101 x 0.25)), 40q) =
25 quarters -> OOS 2020-03-31..2026-03-31. OOS spans COVID +
the 2021-23 wage surge + the 2022 tightening bear — exactly the episodes the countercyclical hypothesis concerns.
**Found-in-search caveat is STRONGER than any monthly pair: only 25 OOS quarters.**

## Lead-lag verdict (empirical — determined by Granger/CCF/LP, NOT the prior)
- ECI->SPY TY-Granger significant lags (quarters): NONE
- SPY->ECI TY-Granger significant lags (quarters): [1, 2, 3, 4]
- Pre-whitened CCF significant lead(+) lags: NONE; lag(-) lags: NONE
- LP forward significant: False; reverse-causality flag: False
- **Classification: lagging.** Winner direction (empirical): procyclical.
- indicator_nature in interpretation_metadata set to the EMPIRICAL verdict (Dana's provisional prior was 'lagging').

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal). Lead column `lead_quarters`. Both orientations tested.
- GH #13 artifacts emitted from the start: lead_winner_curve_20260706.csv (published winner's own Sharpe per lead;
  peak at L6q vs published L6q) and lead_clean_envelope_20260706.csv
  (SA source -> envelope == clean envelope by construction; stated in the file's manifest entry).
- CP2 skipped (regime_story: false). Returns gross of costs; cost grid in tournament_validation_20260706/.

## New pair — no prior version; Rule C3 regression diff N/A.
