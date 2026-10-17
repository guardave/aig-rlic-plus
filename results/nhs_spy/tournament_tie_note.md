# Tournament Tie Note - nhs_spy (20261016)

Winner resolved at IS cascade step 5 (is_sharpe, is_ann_return, is_max_drawdown, is_n_trades, then names).

| signal      | threshold         | strategy                   |   lead_months | lookback   |   is_sharpe |   is_ann_return |   is_max_drawdown |   is_n_trades |   oos_sharpe |
|:------------|:------------------|:---------------------------|--------------:|:-----------|------------:|----------------:|------------------:|--------------:|-------------:|
| contraction | T2_roll_p25       | P2_signal_strength_counter |             9 | LB36       |     1.46285 |        0.113996 |          -0.06698 |            23 |     0.931838 |
| contraction | T2_roll_p75       | P2_signal_strength_counter |             9 | LB36       |     1.46285 |        0.113996 |          -0.06698 |            23 |     0.931838 |
| contraction | T3_zscore_1.0     | P2_signal_strength_counter |             9 | LB36       |     1.46285 |        0.113996 |          -0.06698 |            23 |     0.931838 |
| contraction | T3_zscore_neg_1.0 | P2_signal_strength_counter |             9 | LB36       |     1.46285 |        0.113996 |          -0.06698 |            23 |     0.931838 |
| contraction | T3_zscore_1.5     | P2_signal_strength_counter |             9 | LB36       |     1.46285 |        0.113996 |          -0.06698 |            23 |     0.931838 |
| contraction | T3_zscore_neg_1.5 | P2_signal_strength_counter |             9 | LB36       |     1.46285 |        0.113996 |          -0.06698 |            23 |     0.931838 |