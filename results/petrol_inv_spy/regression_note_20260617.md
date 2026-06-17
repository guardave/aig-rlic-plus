# Regression Note — petrol_inv_spy — 2026-06-17

## Changes From Prior Version

- No prior Evan econometrics version exists for `petrol_inv_spy`; this is the initial econometrics producer run.
- Added `petrol_3m` to `docs/schemas/signal_code_registry.json` because the tournament winner uses `signal_column = petrol_inv_3m_pct` and ECON-DS3 requires registry-backed winner signal codes.

## Approved By

- Lead Lesandro review pending. This note records producer-side decisions before handoff.

## Unchanged

- Dana-owned input data and stationarity conclusions were consumed as provided. Stationarity tests were reviewed/confirmed, not re-run.
- The benchmark row convention follows ECON-T4: exactly one `signal == "BENCHMARK"` row with `valid = False`.

## Impact Assessment

The new `petrol_3m` registry entry allows `winner_summary.json.signal_code` to validate without using an ad hoc or pipeline-order signal name. Downstream consumers should use `winner_summary.signal_column = petrol_inv_3m_pct` for parquet access and `signal_code = petrol_3m` for display/catalog references.

Deploy-required Evan artifacts now present in `results/petrol_inv_spy/`: `signals_20260617.parquet`, `winner_summary.json`, `signal_scope.json`, `interpretation_metadata.json`, `tournament_results_20260617.csv`, and `analyst_suggestions.json`.

## Removed

- None. Initial econometrics run.
