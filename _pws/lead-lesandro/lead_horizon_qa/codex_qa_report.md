# Codex-QA Independent Audit Report

Audit target: Lead-Horizon Wave Reconciliation  
Auditor: Codex-QA, independent external QA  
Date: 2026-06-20

## Method

- Source of truth for production: `git show HEAD:results/<pair>/<file>`.
- Working-tree copies were inspected only for tamper detection and for the explicit `indpro_xlp` Phase-1 proposal files named in the brief.
- Tournament legitimacy test: max `oos_sharpe` among rows where `valid == True`.
- Sharpe recomputation for `indpro_xlp` proposal: monthly OOS returns, `mean(return) / sample_std(return) * sqrt(12)`.
- No files under `results/`, `app/`, `output/`, or `scripts/` were modified.

## A. Winner Legitimacy Over Committed Production Grids

Some winner JSON files use display/registry aliases while tournament rows use compact codes. I therefore report both the JSON winner and the raw tournament max row. `SHARPE_ONLY` means the published Sharpe equals the committed valid-grid maximum exactly, but row identity is alias-coded in the JSON/tournament schema and cannot be compared literally without the registry mapping.

| pair | committed tournament | committed lead grid | published winner from committed `winner_summary.json` | max valid committed row | result |
|---|---:|---|---|---|---|
| `busloans_spy` | 6,101 rows; 4,396 valid | `[0,1,2,3,6,12]` months | `busloans_mom/T2_roll_p25/P1_long_cash/L6 = 1.4999` | `mom/T2_roll_p25/P1_long_cash_counter/L6 = 1.4999` | SHARPE_ONLY |
| `gold_copper_xli` | 91 rows; 60 valid | `[0,1,5]` days; no `lead_months` column | `S_zscore_126d/T2_p50/P1_long_cash/L0 = 1.2730` | `gold_copper_zscore_126d/T2_p50/P1_long_cash/L0 = 1.2730` | SHARPE_ONLY |
| `hy_ig_spy` | 2,167 rows; 2,036 valid | `[0,1,5,10,21,63]` days; no `lead_months` column | `S6_hmm_stress/T4_hmm_0.5/P2_signal_strength/L0 = 1.4083` | `S6_hmm_stress/T4_hmm_0.5/P2/L0 = 1.4083` | CONFIRM |
| `indpro_spy` | 1,666 rows; 1,149 valid | `[0,1,2,3,6]` months | `S6_mom3m/T1_fixed_p75/P1_long_cash/L6 = 1.1036` | `S6_mom3m/T1_fixed_p75/P1_long_cash/L6 = 1.1036` | CONFIRM |
| `indpro_xlp` | 3,331 rows; 2,691 valid | `[0,1,2,3,6]` months | `S8_accel/P3_long_short/L3 = 1.1147` | `S8_accel/T2_roll_p75/P3_long_short_counter/L3 = 1.1147` | CONFIRM |
| `ism_services_spy` | 4,881 rows; 3,385 valid | `[0,1,2,3,6,12]` months | `ism_services_gap_50/T3_zscore_neg_1.0/P1_long_cash/L3 = 1.5377` | `level/T3_zscore_neg_1.0/P1_long_cash_pro/L3 = 1.5377` | SHARPE_ONLY |
| `m2sl_yoy_spy` | 4,721 rows; 3,369 valid | `[0,1,2,3,6,12]` months | `m2sl_accel/T1_fixed_p50/P1_long_cash/L2 = 1.6882` | `accel/T1_fixed_p50/P1_long_cash_pro/L2 = 1.6882` | SHARPE_ONLY |
| `permit_spy` | 856 rows; 674 valid | `[0,1,2,3,6]` months | `S3_mom/T1_p25/P3_long_short/L6 = 1.4454` | `S3_mom/T1_p25/P3/L6 = 1.4454` | CONFIRM |
| `petrol_inv_spy` | 7,393 rows; 5,123 valid | `[0,1,2,3,6,12]` months | `petrol_3m/T1_fixed_p50/P1_long_cash/L12 = 1.4779` | `petrol_3m/T1_fixed_p50/P1_long_cash_pro/L12 = 1.4779` | CONFIRM |
| `phlxsox_spy` | 6,762 rows; 4,607 valid | `[0,1,5,10,21,63]` days; no `lead_months` column | `phlxsox_rs_mom6m/T2_roll_p75/P1_long_cash/L63 = 1.5700` | `rs_mom6m/T2_roll_p75/P1_long_cash_pro/L63 = 1.5700` | SHARPE_ONLY |
| `umcsent_xlv` | 1,828 rows; 1,339 valid | `[0,1,2,3,4,5,6]` months | `S3_mom/T3_zscore_1.0/P1_long_cash/L6 = 1.1586` | `S3_mom/T3_zscore_1.0/P1_long_cash/L6 = 1.1586` | CONFIRM |
| `vix_vix3m_spy` | 916 rows; 331 valid | `[0,1,5,10,21]` days; no `lead_months` column | `S3_z126/T2_rp75/P1_long_cash/L0 = 1.1295` | `S3_z126/T2_rp75/P1/L0 = 1.1295` | CONFIRM |

Conclusion for A: zero published winners have a committed-grid Sharpe below the max valid row. The daily pairs were handled by their `lead_days` grids where no `lead_months` column exists.

## B. Tamper Check: Working Tournament CSVs vs HEAD

All 12 working-tree publish-time tournament CSVs byte-hash match their committed `HEAD` versions. Row counts and grids also match.

| pair | tournament | HEAD rows | working rows | HEAD grid | working grid | hash match |
|---|---|---:|---:|---|---|---|
| `busloans_spy` | `tournament_results_20260612.csv` | 6,101 | 6,101 | `[0,1,2,3,6,12]` months | same | YES |
| `gold_copper_xli` | `tournament_results_20260526.csv` | 91 | 91 | `[0,1,5]` days | same | YES |
| `hy_ig_spy` | `tournament_results_20260422.csv` | 2,167 | 2,167 | `[0,1,5,10,21,63]` days | same | YES |
| `indpro_spy` | `tournament_results_20260314.csv` | 1,666 | 1,666 | `[0,1,2,3,6]` months | same | YES |
| `indpro_xlp` | `tournament_results_20260420.csv` | 3,331 | 3,331 | `[0,1,2,3,6]` months | same | YES |
| `ism_services_spy` | `tournament_results_20260618.csv` | 4,881 | 4,881 | `[0,1,2,3,6,12]` months | same | YES |
| `m2sl_yoy_spy` | `tournament_results_20260619.csv` | 4,721 | 4,721 | `[0,1,2,3,6,12]` months | same | YES |
| `permit_spy` | `tournament_results_20260314.csv` | 856 | 856 | `[0,1,2,3,6]` months | same | YES |
| `petrol_inv_spy` | `tournament_results_20260617.csv` | 7,393 | 7,393 | `[0,1,2,3,6,12]` months | same | YES |
| `phlxsox_spy` | `tournament_results_20260619.csv` | 6,762 | 6,762 | `[0,1,5,10,21,63]` days | same | YES |
| `umcsent_xlv` | `tournament_results_20260420.csv` | 1,828 | 1,828 | `[0,1,2,3,4,5,6]` months | same | YES |
| `vix_vix3m_spy` | `tournament_results_20260314.csv` | 916 | 916 | `[0,1,5,10,21]` days | same | YES |

Specific checks requested:

- `indpro_spy/tournament_results_20260314.csv`: working copy matches `HEAD`; grid is committed coarse `[0,1,2,3,6]`.
- `umcsent_xlv/tournament_results_20260420.csv`: working copy matches `HEAD`; grid is committed `[0,1,2,3,4,5,6]`.

Additional working-tree observation: `results/indpro_xlp/tournament_results_20260620.csv` is an extra untracked proposal file. It is not a mutation of the committed production tournament.

## C. Independent Verification of C4: `indpro_xlp` L11 Proposal

Working files checked:

- `results/indpro_xlp/winner_summary.json`
- `results/indpro_xlp/strategy_returns_20260620.csv`

Working proposal winner:

- `S3_mom/T1_fixed_p50/P1_long_cash/L11`
- Reported OOS Sharpe: `1.3282`
- Reported buy-and-hold OOS Sharpe: `0.7437`
- Committed original `indpro_xlp` grid: `[0,1,2,3,6]`; `L11` was not in the committed production grid.

Arithmetic from `strategy_returns_20260620.csv`, OOS window `2019-01-31` to `2025-12-31`:

- Strategy OOS observations: `84`
- Strategy monthly mean: `0.0092582887`
- Strategy monthly sample std: `0.0241467291`
- Strategy Sharpe: `0.0092582887 / 0.0241467291 * sqrt(12) = 1.3281986467`
- Buy-and-hold monthly mean: `0.0080700271`
- Buy-and-hold monthly sample std: `0.0375873536`
- Buy-and-hold Sharpe: `0.7437446691`

Verdict on C4: CONFIRM. The proposal Sharpe recomputes to `1.3282` within tolerance and beats buy-and-hold.

## D. Independent Verification of C5: `indpro_spy` Extended Native Best

File checked: `temp/260620211849_leadrerun/indpro_spy_tournament_full.csv`

Native extended valid-row bests:

- `L4`: `S3_mom/T2_roll_p75/P1_long_cash`, OOS Sharpe `1.2301`
- `L6`: `S6_mom3m/T1_fixed_p75/P1_long_cash`, OOS Sharpe `1.1036`

Committed `indpro_spy` grid from `HEAD:results/indpro_spy/tournament_results_20260314.csv` is `[0,1,2,3,6]`; `L4` is not in that committed grid.

Verdict on C5: CONFIRM. The extended native best is a real untested `L4` row and beats the committed `L6` winner.

## E. Independent Verification of C6: Gating Sweep Polarity-Mirror Phantom

Sweep file checked: `results/indpro_spy/lead_tournament_20260620.csv`

- Sweep `L12` row reports best OOS Sharpe `1.3744`, `indpro_mom_6m/Tp75_lo/P2`.

Native extended file checked: `temp/260620211849_leadrerun/indpro_spy_tournament_full.csv`

- Native valid `L12` best is only `1.0412`, from `S9_contraction` rows.
- The sweep value `1.3744` matches the absolute value of an invalid native negative-Sharpe row: `S7_mom6m/T1_fixed_p75/P3_long_short/L12 = -1.3744`, `valid=False`.
- Other large absolute native `L12` rows are also invalid negative-Sharpe long/short rows, e.g. `S4_dev_trend/T1_fixed_p75/P3_long_short/L12 = -1.4786`, `valid=False`.

Verdict on C6: CONFIRM. The cheap sweep is not a safe gate for native tournament promotion; it can surface polarity-mirror artifacts that are not native valid winners.

## F. Claim Reconciliation

| claim | verdict | evidence |
|---|---|---|
| C1 | CONFIRM | All 12 committed production winners equal the max valid committed-grid OOS Sharpe; zero mystery winners. Some exact identity fields require alias mapping, but Sharpe maxima reconcile exactly. |
| C2 | CONFIRM | `HEAD:results/indpro_spy/tournament_results_20260314.csv` has 1,666 rows and committed grid `[0,1,2,3,6]`; working copy hash-matches `HEAD`. |
| C3 | CONFIRM | `umcsent_xlv` committed grid is `[0,1,2,3,4,5,6]`; max valid row is `S3_mom/T3_zscore_1.0/P1_long_cash/L6 = 1.1586`; working copy hash-matches `HEAD`. |
| C4 | CONFIRM | Recomputed `indpro_xlp` proposal Sharpe is `1.3281986467`; buy-and-hold Sharpe is `0.7437446691`; committed grid `[0,1,2,3,6]` excludes `L11`. |
| C5 | CONFIRM | Extended native `indpro_spy` file has `L4 = 1.2301` from `S3_mom/T2_roll_p75/P1_long_cash`, above committed `L6 = 1.1036`; `L4` was absent from committed grid. |
| C6 | CONFIRM | Sweep reports `L12 = 1.3744`, while native valid `L12` best is `1.0412`; `1.3744` equals `abs(-1.3744)` from an invalid native negative-Sharpe row. |

## Trust Verdict

The 12 committed production winners are trustworthy as published-baseline winners over their committed tournament grids. I found no current in-place append corruption in the publish-time tournament CSVs; `indpro_spy` and `umcsent_xlv` specifically match `HEAD`.

The Phase-1 proposals are real, not artifacts:

- `indpro_xlp` `S3_mom/T1_fixed_p50/P1_long_cash/L11 = 1.3282` is supported by the working-tree proposal returns and was outside the committed coarse grid.
- `indpro_spy` `S3_mom/T2_roll_p75/P1_long_cash/L4 = 1.2301` is supported by the extended native temp tournament and was outside the committed coarse grid.

The cheap lead sweep is unsafe as a promotion gate. It is useful as exploratory evidence only; promotion decisions must come from the native tournament rerun.

## New Issues Found

1. The working tree currently has modified production-side `indpro_xlp` files (`winner_summary.json`, trade logs, `subperiod_sharpe.csv`) plus untracked proposal artifacts. That is expected for the C4 working-tree proposal, but it means the working tree no longer represents the committed production baseline for `indpro_xlp` winner artifacts. Any stakeholder-facing baseline audit must keep using `git show HEAD:` until the proposal is intentionally reviewed and committed.
2. Several winner summaries use aliases or display-level names that do not literally match tournament row codes (`busloans_spy`, `ism_services_spy`, `m2sl_yoy_spy`, `phlxsox_spy`). This did not change the Sharpe reconciliation, but exact identity reconciliation would be cleaner if each summary carried the raw tournament row keys alongside display aliases.
