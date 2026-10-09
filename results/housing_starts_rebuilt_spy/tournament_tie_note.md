# Tournament Tie Note — housing_starts_rebuilt_spy (20261008)

Winner resolved at cascade step 5 (ECON-T3).

## Candidates tied at step 1 (oos_sharpe)

| signal      | threshold         | strategy               |   lead_months | lookback   |   oos_sharpe |   oos_ann_return |   max_drawdown |   n_trades |
|:------------|:------------------|:-----------------------|--------------:|:-----------|-------------:|-----------------:|---------------:|-----------:|
| yoy         | T4_zero           | P1_long_cash_counter   |             8 | LB_NA      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T1_fixed_p25      | P1_long_cash_pro       |             8 | LB_NA      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T1_fixed_p50      | P1_long_cash_pro       |             8 | LB_NA      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p25       | P1_long_cash_pro       |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p25       | P2_signal_strength_pro |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p75       | P2_signal_strength_pro |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.0     | P2_signal_strength_pro |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_neg_1.0 | P2_signal_strength_pro |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.5     | P2_signal_strength_pro |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_neg_1.5 | P2_signal_strength_pro |             8 | LB36       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p25       | P1_long_cash_pro       |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p25       | P2_signal_strength_pro |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p75       | P2_signal_strength_pro |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.0     | P2_signal_strength_pro |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_neg_1.0 | P2_signal_strength_pro |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.5     | P2_signal_strength_pro |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_neg_1.5 | P2_signal_strength_pro |             8 | LB60       |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p25       | P1_long_cash_pro       |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p25       | P2_signal_strength_pro |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T2_roll_p75       | P2_signal_strength_pro |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.0     | P1_long_cash_pro       |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.0     | P2_signal_strength_pro |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_neg_1.0 | P2_signal_strength_pro |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_1.5     | P2_signal_strength_pro |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |
| contraction | T3_zscore_neg_1.5 | P2_signal_strength_pro |             8 | LB120      |       1.4485 |           0.1323 |        -0.0833 |         30 |

Interpretation: candidates are near-equivalent on the primary objective; the selected winner is preferred on the documented tie-break dimension.