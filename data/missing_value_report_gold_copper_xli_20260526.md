# Missing Value Report — gold_copper_xli

Generated: 2026-05-26 16:34 UTC

Rows: 6783  Cols: 39

| Column | n_missing | pct_missing |
|---|---:|---:|
| gold | 172 | 2.54% |
| copper | 172 | 2.54% |
| gold_etf | 1273 | 18.77% |
| copper_etf | 3096 | 45.64% |
| xli | 0 | 0.00% |
| spy | 0 | 0.00% |
| vix | 0 | 0.00% |
| dxy | 0 | 0.00% |
| gold_copper_ratio | 172 | 2.54% |
| gold_copper_ratio_etf | 3096 | 45.64% |
| gold_copper_logratio | 172 | 2.54% |
| gold_copper_zscore_126d | 271 | 4.00% |
| gold_copper_zscore_252d | 372 | 5.48% |
| gold_copper_zscore_504d | 574 | 8.46% |
| gold_copper_pctrank_504d | 574 | 8.46% |
| gold_copper_pctrank_1260d | 1179 | 17.38% |
| gold_copper_roc_5d | 177 | 2.61% |
| gold_copper_roc_21d | 193 | 2.85% |
| gold_copper_roc_63d | 235 | 3.46% |
| gold_copper_roc_126d | 298 | 4.39% |
| gold_copper_mom_21d | 193 | 2.85% |
| gold_copper_mom_63d | 235 | 3.46% |
| gold_copper_mom_252d | 424 | 6.25% |
| gold_copper_acceleration | 214 | 3.15% |
| gold_copper_realized_vol_21d | 187 | 2.76% |
| xli_ret | 1 | 0.01% |
| xli_fwd_1d | 1 | 0.01% |
| xli_fwd_5d | 5 | 0.07% |
| xli_fwd_21d | 21 | 0.31% |
| xli_fwd_63d | 63 | 0.93% |
| xli_fwd_126d | 126 | 1.86% |
| xli_fwd_252d | 252 | 3.72% |
| spy_ret | 1 | 0.01% |
| spy_fwd_1d | 1 | 0.01% |
| spy_fwd_5d | 5 | 0.07% |
| spy_fwd_21d | 21 | 0.31% |
| spy_fwd_63d | 63 | 0.93% |
| spy_fwd_126d | 126 | 1.86% |
| spy_fwd_252d | 252 | 3.72% |

## Notes

- `copper_etf` (CPER) inception 2011-11; expect ~30% missing across full sample. Used only as ETF cross-check after 2011.
- All other primary columns are forward-filled up to 5 business days for cross-asset alignment.
- Rolling window columns (zscore_*, pctrank_*, roc_*, mom_*, realized_vol_*) have leading missings equal to their lookback window.
- Forward-return columns (*_fwd_*) have trailing missings equal to their horizon.
