# Econ Evan — AIG-RLIC+ Session Notes

## 2026-06-13 — ECON-LT1 Re-Run: gold_copper_xli (Track B pilot, fix260613_lead_horizon)

**Dispatch:** Lead horizon extension. Gating analysis found L10 (pctrank_504d, Sharpe 1.370) beating published L0 winner (zscore_126d, Sharpe 1.273). Gate decision: RE-RUN.

**Extended tournament design:**
- 13 signal transforms (was 5): added zscore_504d, pctrank_1260d, roc_5d, roc_21d, mom_21d, mom_63d, mom_252d, acceleration
- ~14 threshold rules (was 3): quantile-based (p25/p50/p75/p90, hi/lo), z-score fixed (±1), fixed (0.3, 0.7), reversed quantiles
- 2 strategies: P1_long_cash, P2_long_short (mapped to schema P3_long_short)
- 13 lead values: L0..L12 months (×21 trading days per ECON-LL1)
- Result: 4,732 combos + 1 benchmark, 2,996 valid

**New winner (T3 cascade step 1 — unique max Sharpe):**
- Signal: gold_copper_roc_5d (S_roc_5d), threshold: Tp75_lo (<=2.0649), strategy: P3_long_short, lead: L0
- OOS Sharpe: 1.5101 (was 1.273), ann return: 36.1% (was 13.4%), max DD: -22.7% (was -8.3%)
- Annual turnover: 89.15, 554 position changes OOS

**Old winner (superseded):**
- Signal: gold_copper_zscore_126d (S_zscore_126d), threshold: T2_p50 (<=-0.0334), strategy: P1_long_cash, lead: L0
- OOS Sharpe: 1.273, ann return: 13.4%, max DD: -8.3%

**ECON-SR1 reconciliation: PASS** (dSharpe=0.0000, dRet=0.00pp, dDD=0.00pp)

**Schema validation: PASS** (winner_summary, signal_scope, interpretation_metadata)

**Fragility concerns:**
1. roc_5d is a very short-horizon signal (1-week ROC) — noisy, high turnover (89/yr)
2. P3_long_short doubles exposure and drawdown risk vs the old P1_long_cash winner
3. Max DD -22.7% vs old -8.3% — significantly worse drawdown despite better Sharpe
4. "Conditionally durable" — only 2 episodes testable (COVID, 2022), both positive
5. The old winner (zscore_126d, P1, L0) had better drawdown profile and lower turnover
6. At L10, the best daily-data Sharpe is 1.226 (roc_21d) — does NOT reproduce the gating sweep's 1.370 because the gating sweep used monthly resampled data

**Artifacts produced:**
- tournament_results_20260613.csv (4,733 rows incl benchmark)
- winner_summary.json (new)
- signals_20260613.parquet
- strategy_returns_20260613.csv
- winner_trade_log.csv (new)
- winner_trades_broker_style.csv (new, 1080 trades)
- subperiod_sharpe.csv (updated)
- rolling_correlation_gold_copper_xli.csv (updated, signal-dependent)
- structural_break_gold_copper_xli.json (updated, break 2009-03, p=0.014, moderately_stable)
- rolling_sharpe_gold_copper_xli.csv (updated)
- rolling_granger_gold_copper_xli.csv (updated)

**Superseded artifacts (preserved with _superseded_20260613 suffix):**
- winner_summary_superseded_20260613.json
- winner_trade_log_superseded_20260613.csv
- winner_trades_broker_style_superseded_20260613.csv

**Registry update:** S_roc_5d appended to signal_code_registry.json

## 2026-04-23 — Wave 10I.A schema relaxation (fast-path)

Dispatch: relax `winner_summary.schema.json` `threshold_value` to accept `null` to unblock 6/41 cloud-verify FAILs.

Changes:
- `threshold_value.type`: `"number"` → `["number","null"]` with description note citing `BL-THRESHOLD-VALUE-SCHEMA` and Ace's Defense-2 coerce @ 5f2e50d.
- `x-version`: 1.0.0 → 1.1.0 (minor, per META-SCV; additive tolerant change).

Smoke: `smoke_loader.py` across 10 pairs → all `failures=0`.

Backlog items logged in handoff (`results/_cross_agent/handoff_evan_wave10i_schema_20260423.md`):
- BL-LEGACY-WINNER-SUMMARY-SHAPE (6 legacy pairs deviate from schema beyond just threshold_value — missing `generated_at`, `signal_column`, `target_symbol`, `threshold_rule`, `strategy_family`, `oos_max_drawdown`, OOS window fields; legacy extras: `threshold_code`, `strategy_code`, `*_display_name`, `lead_*`, `win_rate`).
- BL-WINNER-SUMMARY-ADDL-PROPS (decide whether to add `additionalProperties: false` or formally declare legacy fields).
- BL-WIN-RATE-NULL (`win_rate` null in 7 of 11 pairs).

Do-NOT boundary respected: no data files, no `app/components/*`, no producer code touched.

## 2026-04-19/20 session — HY-IG v2 reference-pair hardening (Waves 1 → 8D)
