# Execution Notes: hy_ig_spy

## Winner: HMM 2-State Stress Probability / 70% Threshold / Long/Cash

## Step-by-Step Execution

1. **Monitor** the HY-IG credit spread (OAS) daily.
2. **Apply HMM regime model**: The 2-state Hidden Markov Model classifies each day as "calm" or "stress" based on spread dynamics and VIX levels.
3. **Threshold**: When the model assigns >70% probability to the stress regime, move to cash.
4. **Re-enter**: When stress probability drops below 70%, return to full equity (SPY) exposure.
5. **Strategy type**: Long/Cash — fully invested or fully in cash. No short positions.
6. **Expected turnover**: ~5 trades per year.
7. **Transaction cost budget**: Strategy Sharpe remains positive up to 10.0 bps round-trip.

## Key Characteristics

- This is a **drawdown avoidance** strategy, not an alpha generator.
- OOS return (+11.0%) is lower than buy-and-hold (+13.8%), but max drawdown improves from -33.7% to -11.6%.
- Bootstrap p-value: 0.0002 (significant at 5%).

## Caveats

- HMM states are estimated in-sample and may not persist out-of-sample
- Credit spread data begins 2000 — limited to ~25 years of history
- Strategy reduces drawdowns but does not generate excess return over buy-and-hold

---
*Structured from existing strategy page and validation outputs for hy_ig_spy*
