# Portal Narrative: 10Y-3M Treasury Spread x SPY

Pair ID: `t10y3m_spy`

## Thesis

The 10Y-3M Treasury spread is a rates-cycle and recession-risk indicator for
SPY. A steeper curve usually points to easier future conditions and lower
near-term recession risk, while inversion warns that restrictive policy may
pressure future equity returns.

The winning rule is not the raw spread level. It is the 3-month change in the
spread, applied with a 6-month lead and a rolling 60-month 75th percentile
threshold. In plain English: hold SPY when the curve had been steepening
strongly six months earlier; otherwise hold cash.

## Headline Result

- Winner: `t10y3m_3m_chg / T2_roll_p75 / P1_long_cash / L6 / LB60`
- OOS window: 2017-10-31 to 2025-11-30
- OOS Sharpe: 1.32
- Buy-and-hold Sharpe: 0.93
- OOS annualized return: 10.7%
- OOS maximum drawdown: -4.7%
- Buy-and-hold maximum drawdown: -23.9%
- Valid tournament combinations: 775

## Interpretation

The result supports a medium-confidence risk overlay, not a causal forecast.
The economic mechanism is plausible: curve steepening can indicate improving
growth expectations or easier future policy conditions. The caveat is timing:
yield-curve signals can be early by many months, and inversion can persist
while equities rally.

## Dashboard Framing

The Story page should emphasize the rates-cycle mechanism and the timing
caveat. The Evidence page should show that correlation and Granger tests are
not decisive enough for a high-confidence causal claim. The Strategy page
should focus on the actual implementable rule: a lagged 3-month curve-change
signal, rolling p75 threshold, and long/cash SPY allocation.
