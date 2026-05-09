---
pair_id: hy_ig_spy_v3_rerun
winner_rule: "S2a_zscore_252d / T2_rp75 / P1 / L0"
signal_code: S2a_zscore_252d
threshold_code: T2_rp75
strategy_code: P1
lead_days: 0
direction: countercyclical
target_symbol: SPY
indicator: hy_ig_spread_pct
validation_sharpe: 1.20
holdout_sharpe: 0.85
status: needs_final_exam
split_design: three_period
is_start: "2000-01-03"
is_end: "2018-10-03"
is_n_days: 4893
val_start: "2018-10-04"
val_end: "2025-01-13"
val_n_days: 1638
holdout_start: "2025-01-14"
holdout_end: "2025-12-31"
holdout_n_days: 252
experiment_fork: rerun
generated_at: "2026-05-09T00:00:00Z"
narrative_version: "1.0.0"
---

> **EXPERIMENT FORK — rerun branch.** This portal covers `hy_ig_spy_v3_rerun`, the clean-rerun half of a controlled experiment comparing clean rerun vs retro-apply methodology. It is a minimal comparison build, not a production pair.

# hy_ig_spy_v3_rerun — Narrative Summary

## Signal Mechanism

The HY-IG spread measures the yield premium that high-yield (junk) bond issuers must pay above investment-grade issuers. When credit markets grow fearful — as they do before and during equity drawdowns — this spread widens, signalling elevated default risk and deteriorating risk appetite. The winner rule exploits this relationship in a strictly rules-based, countercyclical way: each day the 252-trading-day z-score of the HY-IG spread is computed and compared against its own rolling 75th percentile (T2_rp75). When the z-score exceeds that threshold — indicating the spread is elevated relative to its recent history — the strategy moves to cash (flat, zero equity exposure). When the z-score is at or below the threshold, the strategy holds SPY in full. There is no look-ahead: the signal fires at the close of the same day the z-score is observed (L0, zero-day lag), with a one-way cost assumption of 5 bps per trade.

## Key Findings

Over the 18-year in-sample period (2000-01-03 to 2018-10-03, 4,893 trading days), the rule was selected from a tournament of 2,143 raw candidates (150 effective after correlation pruning). In the validation out-of-sample window (2018-10-04 to 2025-01-13, 1,638 trading days), the strategy produced a Sharpe ratio of 1.20 — a clean demonstration that the credit-to-equity lead-indicator relationship persisted through trade wars, a global pandemic, and the 2022 rate shock. The holdout period (2025-01-14 to 2025-12-31, 252 trading days) delivered a Sharpe of 0.85 — positive and above the 0.30 validity floor, but with an annualised excess return of −14.4% versus buy-and-hold SPY (5.2% vs 19.7%). The final exam status is **needs_final_exam**: 7 of 10 ECON-FE1 conditions pass, but three fail — C03 (block bootstrap 2.5th percentile dips to −1.19, below zero), C04 (deflated Sharpe ratio p-value is effectively 0.00, flagging over-fit risk given the large raw trial count), and C05 (excess annual return is negative). The economic interpretation is straightforward: 2025 was a strong bull year for U.S. equities; a defensive strategy that reduces equity exposure when credit stress is elevated will mechanically lag a rising market. The strategy avoided the Q1 2025 drawdown (max drawdown −5.1% vs −18.8% for SPY) but gave back that cushion in foregone upside. Whether this is a permanent regime shift or a transient bull-year penalty is the open question the final exam is designed to resolve.

## Three-Period Split Design

| Window | Start | End | N Days |
|---|---|---|---|
| In-Sample (IS) | 2000-01-03 | 2018-10-03 | 4,893 |
| Validation OOS | 2018-10-04 | 2025-01-13 | 1,638 |
| Holdout | 2025-01-14 | 2025-12-31 | 252 |

The split follows the ECON-OOS4 three-period protocol. The in-sample window covers the full history available at tournament time (including dot-com, GFC, and COVID). The validation OOS window — the primary selection criterion — spans 78 months of post-IS data. The holdout is a sealed window of 252 trading days (approximately one calendar year) unsealed only for the final exam; it was not accessible during tournament selection or threshold tuning.

## Conditions Summary (ECON-FE1)

| ID | Description | Result | Value |
|---|---|---|---|
| C01 | Holdout Sharpe > 0 | PASS | 0.85 |
| C02 | Holdout Sharpe ≥ 0.30 | PASS | 0.85 |
| C03 | Boot CI lower bound > 0 | FAIL | −1.19 |
| C04 | DSR p-value ≥ 0.05 | FAIL | 0.00 |
| C05 | Excess return vs B&H > 0 | FAIL | −14.4% |
| C06 | Max drawdown > −30% | PASS | −5.1% |
| C07 | Strategy DD shallower than B&H | PASS | +13.7 pp |
| C08 | Validation Sharpe ≥ 0.30 | PASS | 1.20 |
| C09 | Holdout N ≥ 200 obs | PASS | 251 |
| C10 | Sharpe degradation val→holdout ≤ 0.50 | PASS | 0.35 |
