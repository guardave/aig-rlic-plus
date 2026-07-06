# Design Note — wells_fargo_housing_spy (20260706)

## Hypothesis (one-liner)
Does homebuilder sentiment (NAHB/Wells Fargo Housing Market Index) carry forward
information about SPY returns? Prior: PROCYCLICAL and LEADING — housing is the
most interest-rate-sensitive real sector and classically leads the business
cycle ("housing IS the business cycle", Leamer 2007); the HMI turned down ~2
years before the GFC equity peak. Lead-lag and sign are determined EMPIRICALLY
by Evan (Granger / pre-whitened CCF); this note only seeds a provisional prior.

## Source & sample
- Indicator: **data/Data Master.xlsx**, sheet `WFHMI`, column
  `RE - Wells Fargo H Indx` (queue primary_csv_ticker). FRED delisted NAHBHMI
  (licensing) — the Master is the authoritative project source. Pre-master
  Row 2 dictionary: "NAHB/Wells Fargo Housing Market Index / Units: index,
  seasonally Adjusted / Monthly, Jan 1985 - Oct 2025".
- Master sample: **1985-01 .. 2025-10 (490 monthly obs, no gaps)**. (NAHB HMI
  begins Jan-1985 at the source, so the Master holds full history.)
- Target: SPY month-end (Yahoo, auto-adjusted; inception 1993-01) — usable pair
  overlap **1993-01-31 .. 2025-10-31
  (394 months, ~33 years: multiple full cycles — a LONG sample by
  fleet standards)**. Controls: UNRATE/DGS10/DFF (FRED), ^VIX (Yahoo, from 1990).

## Bounded-index transform design (differs from unbounded-quantity pairs)
The HMI is a bounded 0-100 SENTIMENT diffusion index, 50 = neutral:
- **Level is meaningful in itself** (distance from 50 = net builder optimism)
  and mean-reverting — unlike unbounded quantity indices where only changes
  matter. Level and 60M level z-score are first-class signals here.
- **Point changes** (`_diff_3m`, `_diff_12m`) are the natural momentum metric;
  **percent changes of a bounded index are level-dependent** (8 -> 16 = "+100%")
  and included only for standard-family consistency, with a caveat.
- **Regime flag = above/below 50** (`nahb_hmi_above50`), the native
  expansion/contraction line for a diffusion index — NOT a YoY<0 contraction
  flag, which would be degenerate/misleading for a mean-reverting bounded series.

## Seasonality
The HMI is **seasonally adjusted by NAHB** (confirmed by Pre-master Row 2).
MoM / short-horizon transforms are NOT seasonally contaminated (contrast with
the NSA Cass Freight pair).

## Stationarity (ADF/KPSS — see stationarity_tests_20260706.csv)
Level is highly persistent (borderline; bounded so it cannot be a true random
walk); change/z-score transforms stationary; `spy_ret` stationary. Full table
in the CSV; Evan confirms rather than re-runs (SOP).

## No-lookahead / publication lag (recommendation for Evan)
NAHB releases mid-month (~16th-18th) FOR the CURRENT month — effectively zero
publication lag. The month-M value is public ~2 weeks BEFORE month-end M, so
even L0 at month-end granularity involves no lookahead. **Recommendation: start
the lead grid at L1 (safe/conservative, consistent with fleet convention); an
L0 variant is defensible if Evan wants to test the freshest read.**

## Key data-quality flags for downstream
1. **Static source**: the Master is hand-maintained; latest obs 2025-10. No
   live API refresh — manifest TTL set to 30 days but refresh requires a
   Master update (flagged in manifest note). Data Access Risk: Medium.
2. **Bounded index**: prefer level / point-change / z-score signals; treat
   pct-change transforms with caution (documented per-column).
3. 2008-09 single-digit trough and 2020 whipsaw are REAL — do not winsorize.
4. Integer-granularity series (whole index points) — ties are common; flag for
   any rank/percentile-based signal.

## New pair — no prior version; Rule D1 series-preservation / regression diff N/A.

---

# Phase 1 addendum — Econometrics & Tournament (Evan, 20260706)

## Bounded-diffusion-index conventions (design deviations, per Dana's Phase-0)
- LEVEL and level z-score are FIRST-CLASS signals (bounded 0-100, 50 = neutral, mean-reverting).
- Point changes (diff_3m/diff_12m) are the natural momentum metric; %-change transforms are
  level-dependent (8 -> 16 = "+100%") — included for family consistency, flagged per-row
  (`bounded_pct_risk` column); a pct-transform winner is artifact-flagged in winner_summary.notes.
- Native thresholds added: T4_gap50 (level > 50) and T4_above50 (the binary regime flag's only threshold).
- Integer-granularity values: percentile/rank ties are expected; strict `>` comparisons are
  deterministic and quartile bucketing uses rank(method='first'); winner ties resolve via ECON-T3.

## Method coverage (Rule C1, sentiment + leading-candidate battery)
- Correlations incl. distance (n-floor 60 months), horizons 1/3/6/12M fwd.
- Pre-whitened CCF at monthly lags -24..+24 (housing classically leads up to ~2yr; AR order by AIC, max 12).
- Toda-Yamamoto Granger both directions, lags 1..12 months, d_max=1 (level ADF non-stat/KPSS borderline).
- Local projections fwd+rev at 1/3/6/12M horizons, HAC SEs. Transfer entropy tercile-binned, 500 perms.
- Quantile regression on 1m-fwd. HMM 2-state on the LEVEL (optimism/pessimism split — deliberate for a
  bounded sentiment index; stress = LOW-sentiment regime). Markov-switching spy_ret ~ level.
- Era sub-period battery (era_correlations.csv): pre-GFC 1993-2006 / GFC-bust 2007-2012 /
  QE-era 2013-2019 / post-COVID 2020-2025, level + diff_12m vs 1M-fwd SPY:

| signal   | era                  | start   | end     |   n_months |   pearson_r |   p_value |
|:---------|:---------------------|:--------|:--------|-----------:|------------:|----------:|
| level    | pre_gfc_1993_2006    | 1993-01 | 2006-12 |        168 |     -0.0578 |    0.4565 |
| level    | gfc_bust_2007_2012   | 2007-01 | 2012-12 |         72 |      0.0738 |    0.5379 |
| level    | qe_era_2013_2019     | 2013-01 | 2019-12 |         84 |     -0.0378 |    0.7328 |
| level    | post_covid_2020_2025 | 2020-01 | 2025-10 |         69 |     -0.1065 |    0.3836 |
| diff_12m | pre_gfc_1993_2006    | 1993-01 | 2006-12 |        168 |     -0.031  |    0.6896 |
| diff_12m | gfc_bust_2007_2012   | 2007-01 | 2012-12 |         72 |      0.1212 |    0.3106 |
| diff_12m | qe_era_2013_2019     | 2013-01 | 2019-12 |         84 |     -0.016  |    0.8849 |
| diff_12m | post_covid_2020_2025 | 2020-01 | 2025-10 |         69 |     -0.0116 |    0.9244 |

- Stationarity: Dana's tests (stationarity_tests_20260706.csv) reviewed and CONFIRMED, not re-run.
  Level ADF p=0.16 / KPSS fail-to-reject (bounded — cannot be a true random walk); all change/z-score
  transforms and spy_ret stationary.

## Tournament grid (monthly template, 394-month sample affords the full battery)
- Signals: 12 native + hmm_stress + markov_regime. Thresholds: T1 IS-percentiles {25,50,75},
  T2 rolling percentiles {25,75}, T3 rolling z ±1.0/±1.5 x {LB36,LB60,LB120}, T4_zero
  (sign-meaningful), T4_gap50, T4_above50. Strategies: P1 long/cash, P2 signal-strength, P3 long/short,
  each pro/counter. Leads L1..L12 exhaustive (GH #13 artifacts native).
- Eligibility: signal >= 120 non-NaN months; IS >= 120 months; OOS >= 36 months;
  validity = OOS Sharpe > 0.3 (equity threshold) and turnover < 24 position-changes/yr.

## OOS split (ECON-OOS2)
Policy v1_max36_25pct_cap120: span = min(max(36, round(393 x 0.25)), 120) =
98 months -> OOS 2017-09-30..2025-10-31
(~8.2 years — ABOVE the 5yr reliability floor; the first
pair in a while where a proper OOS verdict is possible). IS covers the 1990s expansion, dot-com, the
classic 2005-09 housing-leads-the-cycle episode and the QE era; OOS spans 2018 vol, COVID, the 2021
housing boom, the 2022 rate shock (HMI 83->31) and the 2023-25 high-rate regime.

## Lead-lag verdict (empirical — determined by Granger/CCF/LP, NOT the prior)
- HMI->SPY TY-Granger significant lags (months): [5]
- SPY->HMI TY-Granger significant lags (months): [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
- Pre-whitened CCF significant lead(+) lags: [1, 5, 12, 13]; lag(-) lags: [-10, -1]
- LP forward significant: False; reverse-causality flag: False
- **Classification: bidirectional.** Winner direction (empirical): procyclical.
- Dana's provisional prior was 'leading' (Leamer 2007); interpretation_metadata carries the EMPIRICAL verdict.
- Winner's own lead-curve peaks at L7 (published L7); adjacent-lead
  durability (ECON-LT2 spirit): False.

## Sub-period stability & structural breaks
- Quandt-Andrews sup-F on spy_ret ~ winner-signal: break at 2009-03-31, bootstrap p=0.35,
  flagged=False. Rolling 60M correlation sign-stability: sign_stable. CP1 episode durability: conditionally_durable.
- See era_correlations.csv above for the era-by-era relationship (the 1990s/2000s housing-equity link vs
  post-GFC vs post-COVID).

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal). Lead column `lead_months`. Both orientations tested.
- GH #13 artifacts emitted natively: lead_winner_curve_20260706.csv and lead_clean_envelope_20260706.csv
  (SA source -> envelope == clean envelope by construction).
- Static source ends 2025-10 (~9 months stale at run date) — flagged in evidence_status.json.
- CP2 skipped (regime_story: false). Returns gross of costs; cost grid in tournament_validation_20260706/.

## New pair — no prior version; Rule C3 regression diff N/A.
