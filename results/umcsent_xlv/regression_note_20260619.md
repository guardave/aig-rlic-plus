## Charts Changed

- `equity_curves`: rebuilt from `results/umcsent_xlv/strategy_returns_20260420.csv` and corrected `winner_summary.json`; old chart labeled the winner as `S2_yoy/L6`, new chart shows corrected `S3_mom` / rolling z-score > 1.0 / 6-month lead.
- `drawdown`: rebuilt from corrected strategy returns; title and caption now quote corrected max drawdown `-0.7%`.
- `rolling_sharpe`: rebuilt from corrected strategy returns; reference line now shows corrected OOS Sharpe `1.16`.
- `wf_sharpe`: rebuilt annual OOS Sharpe bars from corrected strategy returns.
- `subperiod_sharpe`: rebuilt chart and refreshed `results/umcsent_xlv/subperiod_sharpe.csv` from corrected strategy returns.
- `rolling_sharpe_cp`: rebuilt chart and refreshed `results/umcsent_xlv/rolling_sharpe_umcsent_xlv.csv` from corrected strategy returns.

## Spec Diff

| Chart | Prior winner encoding | New winner encoding | Source |
| --- | --- | --- | --- |
| `equity_curves` | Reconstructed tournament top strategies, including stale `S2_yoy/L6` traces | Corrected single winner: UMCSENT 3-month momentum, rolling z-score > 1.0, 6-month lead, Long/Cash | `strategy_returns_20260420.csv` |
| `drawdown` | Reconstructed stale `S2_yoy/L6` winner | Corrected `S3_mom` winner; max drawdown `-0.7007%` | `strategy_returns_20260420.csv`, `winner_summary.json` |
| `rolling_sharpe` | Reconstructed stale `S2_yoy/L6` winner | Corrected `S3_mom` winner; full OOS Sharpe reference `1.16` | `strategy_returns_20260420.csv`, `winner_summary.json` |
| `wf_sharpe` | Reconstructed stale `S2_yoy/L6` winner | Corrected `S3_mom` winner calendar-year OOS Sharpe | `strategy_returns_20260420.csv` |
| `subperiod_sharpe` | Stale subperiod CSV from pre-refresh winner | Corrected subperiod CSV; full OOS row Sharpe `1.158553`, annual return `7.9494%`, max drawdown `-0.7007%` | `strategy_returns_20260420.csv` |
| `rolling_sharpe_cp` | Stale 24-month rolling strategy Sharpe source | Corrected 24-month rolling Sharpe source | `strategy_returns_20260420.csv` |

## Rationale

Evan corrected the `umcsent_xlv` winner after discovering the published `winner_summary` and trade log were stale. The ground-truth winner is `S3_mom` / `umcsent_mom`, rolling z-score > 1.0 trigger, 6-month lead, `P1_long_cash`, with OOS Sharpe `1.1586`, annual return `7.9494%`, and max drawdown `-0.7007%`. Winner-specific charts had to be regenerated from the corrected canonical strategy-return stream instead of re-deriving positions inside the chart script.

## Approved By

- Lead Lesandro dispatch `_pws/lead-lesandro/umcsent_refresh/briefs/vera_brief.md`.
- Evan handoff `_pws/lead-lesandro/umcsent_refresh/evan_handoff.md`.

## Unchanged

Indicator-level charts are intentionally unchanged: `correlations`, `ccf`, `correlation_scatter`, `regime_stats`, `signal_dist`, `tournament_scatter`, `rolling_correlation`, `rolling_granger`, `structural_break`, and history zoom charts. They do not render the winner strategy return series or winner position path.

## Impact Assessment

Strategy-page performance visuals now align with corrected winner metrics. Ray and Ace must re-audit public display prose in `app/pair_configs/umcsent_xlv_config.py`, which still contains stale references to the old 1.02 Sharpe, +11.93% return, and -10.9% max drawdown.

## Removed

No charts, tables, subsections, or callouts were removed.
