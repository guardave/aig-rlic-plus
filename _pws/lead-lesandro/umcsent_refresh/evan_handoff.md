# Econ Evan Handoff - UMCSENT x XLV Winner Refresh

EVAN DONE

## Corrected Winner Facts

- Ground truth: `results/umcsent_xlv/tournament_results_20260420.csv` row 777.
- Signal: `S3_mom` / `umcsent_mom` = UMCSENT 3-month momentum.
- Threshold: `T3_zscore_1.0`, rolling 60-month mean plus 1 standard deviation, rule `gt`.
- Materialized latest threshold value: `6.953160` in signal units.
- Lead: `6 months`.
- Strategy: `P1_long_cash` / Long-Cash.
- Target: `XLV`.
- OOS window: `2019-04-30` to `2025-12-31`.
- Metrics: Sharpe `1.1586`, Sortino `1.6121`, Calmar `11.3449`, annual return `7.9494%`, annual volatility `6.8615%`, max drawdown `-0.7007%`, win rate `16.05%`, annual turnover `3.29`.

## Recomputed Verification

Recomputed from `results/umcsent_xlv/strategy_returns_20260420.csv` over `2019-04-30` to `2025-12-31`:

- `oos_n=81`
- `oos_sharpe=1.158553`
- `oos_ann_return=0.079494`
- `oos_ann_vol=0.068615`
- `oos_max_drawdown=-0.007007`

This passes the brief tolerance of `1.16 +/- 0.03`.

## Producer Change

Fixed `scripts/pair_pipeline_umcsent_xlv.py` so winner-specific outputs are derived from the selected tournament row, not default/static encodings:

- Added `derive_winner_series()` as the shared path for position, threshold path, and strategy returns.
- `winner_summary.json` now writes `threshold_code`, rolling `threshold_note`, `lead_value`, `lead_unit`, and `lead_description`.
- The producer now writes `strategy_returns_20260420.csv`.
- `winner_trade_log.csv` now uses the corrected rolling z-score threshold and 6-month lead.

Also updated `scripts/_trade_log_broker.py` so broker-style reason strings prefer `signal_value` from the regenerated position log, preserving the actual lagged signal used by the strategy.

## Artifacts Changed

- `results/umcsent_xlv/winner_summary.json`
- `results/umcsent_xlv/strategy_returns_20260420.csv`
- `results/umcsent_xlv/winner_trade_log.csv`
- `results/umcsent_xlv/winner_trades_broker_style.csv`
- `results/umcsent_xlv/interpretation_metadata.json`
- `scripts/pair_pipeline_umcsent_xlv.py`
- `scripts/_trade_log_broker.py`
- `scripts/refresh_umcsent_winner_artifacts.py`

## Validation Commands

- `python scripts/refresh_umcsent_winner_artifacts.py` - exit 0.
- `python scripts/_trade_log_broker.py umcsent_xlv --position-col position --strat-ret-col strat_ret --price-col xlv --signal-col umcsent_mom --signal-display '6-month-lagged UMCSENT 3-month momentum' --commission-bps 5` - exit 0.
- `python -m py_compile scripts/pair_pipeline_umcsent_xlv.py scripts/_trade_log_broker.py scripts/refresh_umcsent_winner_artifacts.py` - exit 0.
- `python scripts/validate_schema.py --schema docs/schemas/winner_summary.schema.json --instance results/umcsent_xlv/winner_summary.json` - exit 0.
- `python scripts/validate_schema.py --schema docs/schemas/interpretation_metadata.schema.json --instance results/umcsent_xlv/interpretation_metadata.json` - exit 0.
- Strategy-return recompute script - exit 0, `oos_sharpe=1.158553`.
