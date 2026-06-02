# Execution Notes — crude_oil_xle

Generated: 2026-06-02T22:17:34Z

## Strategy
- **Signal:** `wti_vol_q_13w`
- **Family:** `wti_high_vol_long`
- **Rule:** gt 0.75
- **Direction:** long_when_high_vol_regime

## Implementation
- Compute the signal on each Friday's close.
- Translate signal → position per the rule + direction.
- Execute at next week's Friday open (one-week lag).
- Apply 5.0 bps per unit of |Δposition|.

## OOS Performance
- Sharpe: 0.47 (vs 0.04 buy-and-hold)
- Annual return: 8.77%
- Max drawdown: -26.26%
- Trades: 41
- Annual turnover: 3.7

## Sample period
- IS: 1999-01-01 to 2015-01-16
- OOS: 2015-01-23 to 2025-10-10
