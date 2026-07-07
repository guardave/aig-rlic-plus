# Design Note — cass_freight_spy (20260705)

## Category & method coverage (Rule C1, production/macro — full battery to mirror busloans_spy)
All mandatory methods produced (correlations incl. distance, pre-whitened CCF, Toda-Yamamoto Granger both
directions, transfer entropy, local projections fwd+rev, quantile regression, HMM 2-state, quartile returns)
plus ECON-LA1 Lead Analysis and ECON-LT1 Lead Tournament. Deviations from the daily-pair spec:
- MONTHLY pair: correlation horizons are 1m/3m/6m/12m fwd returns (recorded as 21/63/126/252 horizon_days).
- Pre-whitened CCF at monthly lags -18..+18 (trimmed from -20..+20 given the ~125-obs sample).
- Granger is Toda-Yamamoto (VAR in levels of YoY, d_max=1; YoY is borderline I(1) per ADF/KPSS).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations.
- Stationarity: Dana's tests (stationarity_tests_20260705.csv) reviewed and CONFIRMED, not re-run.

## Short-sample adaptations (BINDING Dana Phase-0 constraints)
- 125 monthly obs (2016-01..2026-05). OOS window is 36 months (<5yr) -> ANY winner is FOUND-IN-SEARCH,
  Sharpe inflated/high-variance; treated as a CANDIDATE, never a validated edge (stated in winner_summary).
- Signal eligibility floor 60 non-NaN obs; lookbacks ['LB24', 'LB36', 'LB60'] (LB120 impossible).
- Correlation/regression n-floor lowered to 40 (short history).

## NSA seasonality (BINDING)
Source is NSA -> MoM/3M/6M momentum and the level z-score are seasonally contaminated. YoY-family
(`_pct_yoy`, `_yoy_zscore_60m`), `_dev_trend`, `_contraction`, and regime signals are treated as
seasonally-clean; each tournament row carries a `seasonally_clean` flag and the winner's flag is surfaced
in winner_summary. A seasonally-contaminated winner is NOT allowed to ship silently — flagged hard.

## Publication lag / no-lookahead
Cass publishes ~mid-month for the prior month. Tradable lead grid FLOORS at L1 (no L0). L0 appears only in
the diagnostic lead_correlation table, explicitly flagged non-tradable.

## Lead-lag verdict (empirical — determined by Granger/CCF/LP, NOT the prior)
- Cass->SPY TY-Granger significant lags: NONE
- SPY->Cass TY-Granger significant lags: NONE
- Pre-whitened CCF significant lead(+) lags: NONE; lag(-) lags: [-2]
- LP forward significant: True; reverse-causality flag: False
- Classification: coincident_or_none. Winner direction (empirical): procyclical.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal). Lead grid L1..L12 (full tradable). Both orientations tested.
- CP2 skipped (regime_story: false). Returns gross of costs; 5bps grid in tournament_validation_20260705/.

## New pair — no prior version; Rule C3 regression diff N/A.
