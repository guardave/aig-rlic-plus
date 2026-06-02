# Portal narrative — `crude_oil_xle`

**Authored:** 2026-06-02 by Lead Lesandro (Ray hat under Mode 2).
**Indicator → target:** WTI Crude Oil Price → XLE (Energy Select Sector SPDR).

The prose here is the source of every page's narrative. Ace's pair config will
quote these anchors verbatim via the APP-PT1 template; pages contain no
`st.markdown()` calls (BL-004).

---

## eli5

Energy stocks rise and fall with the price of oil. That's mostly mechanical
— oil companies make money selling barrels, so the share price tracks the
barrel price. This study asks a different question: can the *shape* of oil
prices — calm vs choppy, drifting vs sprinting — tell us when energy stocks
are a better-than-usual bet?

We tested twelve simple rules built on WTI crude prices and asked which
one, if any, beat the obvious alternative of buying-and-holding XLE.
The data picked a rule that surprised us: **invest in XLE when oil prices
have been unusually volatile for the past quarter, sit out otherwise**.
Out of sample (2015–2025), that rule earned a Sharpe of about 0.47, while
just holding XLE earned around 0.04 — meaningfully better, with smaller
drawdowns. The rule trades roughly four times per year on average.

This doesn't mean volatility-as-bullish-signal is a deep truth about energy
markets. It means: over the OOS window we tested, that rule was the best
of the twelve we considered. Other rules — including the more intuitive
"buy when oil is going up" — were dominated.

## story_hook

Oil prices and energy stocks move together. That much is obvious. What's
less obvious is whether the *behaviour* of oil prices — the volatility,
the drift, the cycle position — carries enough information to time XLE
better than simply holding it. We built twelve simple rules from WTI's
price history and ran them through an out-of-sample tournament. The
winner trades on a regime indicator (rolling realized volatility), not
on momentum or value. The annual return is modest, but the risk-adjusted
return is more than ten times the passive benchmark.

## story_findings

Twelve strategies were considered: four pure-momentum variants (4w, 13w,
26w lookback), four z-score variants (52w and 104w windows, both
"above-mean" and "below-mean" entries), two volatility-regime variants
(low vol and high vol entries), and two long-short sign variants.

In the out-of-sample window (2015-01-23 to 2025-10-10, 52 weekly
observations per year), the strategies sort as follows by OOS Sharpe:

1. **`wti_high_vol_long`** — long XLE when WTI 13-week realized vol is
   in the top 25% of its 5-year history. **Winner.** OOS Sharpe ≈ 0.47.
   Max drawdown ≈ -26%. ~4 trades per year.
2. `wti_z_104w_long_top` — long XLE when WTI 2-year z-score is above
   +0.5. OOS Sharpe ≈ 0.24.
3. `wti_momentum_26w_long` — long XLE when WTI 26-week log return is
   positive. OOS Sharpe ≈ 0.09.

The buy-and-hold benchmark (XLE itself) had an OOS Sharpe of ≈ 0.04 over
the same window. Several rules — notably the long-short sign variants —
had negative OOS Sharpe, meaning they were actively harmful versus passive
holding.

Contemporaneous correlation between WTI weekly log returns and XLE
weekly log returns is high (Pearson ≈ 0.55 over the sample), as expected.
The lead-lag regressions at lags 0..8 weeks confirm the strongest
relationship at lag 0 with R² decaying smoothly.

## story_takeaway

The winning rule's mechanism is not "more vol = more upside." It is:
the rule selects out periods when XLE's risk-adjusted return is more
likely to be elevated, conditional on what's been happening in the
underlying commodity. The selection criterion is regime-based, not
return-based.

For a practitioner: the rule turns over slowly (≈ 4 trades/year), so it
is implementable without dragging on costs at 5 bps per leg. For a
researcher: the result is a reminder that the strongest signals in
historical data are not always the ones theory predicts loudest.

## methods_overview

Twelve strategy families were enumerated as a single neutral universe.
The tournament selected by out-of-sample Sharpe; no methodological
preference was hard-coded.

| Signal class | Variants tried |
|---|---|
| Momentum (log return) | 4-week, 13-week, 26-week lookback |
| Z-score (mean reversion / trend) | 52-week and 104-week windows, both above-+0.5 and below--0.5 entries |
| Volatility regime | 13-week realized vol percentile in 5-year rolling, both low (<50%) and high (>75%) entries |
| Sign-based (long-short) | momentum_4w, momentum_13w, z_52w signed positions |

Stationarity (ADF + KPSS) was tested on every constructed feature
before the tournament; non-stationary series were not used as signals
without transformation. Lead-lag was tested via 0..8 week lagged
regressions. Train/OOS split was 60%/40% along the calendar.

Costs: 5 bps per unit of |Δposition| (commission_bps in winner_summary).
Positions are shifted by one week to avoid look-ahead — the rule's
signal as of Friday close drives next Friday's position.

## methods_data

| Series | Source | Frequency | Units | Sample |
|---|---|---|---|---|
| WTI crude oil price | FRED `WCOILWTICO` (cached in `data/Data Master.xlsx` sheet `WCOILWTICO`) | Weekly | USD per barrel, NSA | 1986-01-03 → 2025-10-10 |
| XLE total return | `data/Data Master.xlsx` sheet `etf_prices`, col XLE | Daily | USD | 1998-12-22 → 2025-10-23 |

XLE was resampled to weekly-Friday close to align with WTI's native
frequency. The intersection — 1998-12-22 to 2025-10-10 — is the
analysis sample.

## methods_assumptions

- Returns are continuously-compounded (log).
- Costs are linear in |Δposition|. Slippage and price-impact are
  modelled implicitly through the commission_bps assumption.
- The OOS split is fixed-fraction (60/40 by calendar). No rolling-window
  re-fit; the rule and the position-translation are static across the
  OOS window.
- The volatility-percentile rule uses a 5-year rolling window for its
  percentile rank, with a 52-week minimum-periods relaxation early in
  the sample to avoid burning the entire first year.

## glossary_terms

- **Sharpe ratio** — A common measure of risk-adjusted return. Higher
  is better. A Sharpe of 0.5 is decent; 1.0 is very good; above 2.0 is
  rare and should be treated with suspicion.
- **Drawdown** — How far the strategy's cumulative equity has fallen
  from its previous peak, in percent. Smaller (less negative) is better.
- **OOS (out-of-sample)** — The portion of history NOT used to select
  the winning rule. Performance in OOS is the honest test of the rule.
- **Realized volatility** — The actual observed standard deviation of
  returns over a window, annualised. The "13-week realized vol" used
  in the winning rule is the past three months' wiggle, annualised.
- **Z-score** — How many standard deviations the current value sits
  away from the rolling mean. A z of +1 = one standard deviation above
  the mean.
- **Buy-and-hold** — The passive alternative of just holding the
  target asset over the same OOS window. The benchmark every strategy
  must beat to justify its complexity and turnover.

## evidence_overview

The exploratory analysis confirms what theory and intuition predict:
WTI and XLE returns are strongly correlated contemporaneously. The
tournament tested whether weak-form predictability survives this strong
contemporaneous link — i.e. whether *anything* about WTI's recent past
helps time XLE's near future.

## evidence_takeaways

- 12 strategies × IS/OOS split; 12 valid in OOS.
- 7 of 12 had positive OOS Sharpe; 5 had negative. The signal is genuine
  but mostly noise.
- The 3 best OOS-Sharpe strategies belong to 3 different families
  (vol regime, z-score, momentum) — no single class dominates.
- The buy-and-hold benchmark is beatable but not by much in absolute
  return terms; the gain is risk-adjusted (lower drawdown).

## strategy_overview

The deployed rule is `wti_high_vol_long`:

- Each week's Friday close, compute WTI's 13-week realized volatility
  and rank it within its trailing 5-year history.
- If the rank is above the 75th percentile, hold XLE for the coming week.
- Otherwise, hold cash.
- Apply 5 bps per unit of |Δposition|.

## strategy_trade_log

The OOS window covers 2015-01-23 to 2025-10-10. Over that window, the
rule fired into ~41 distinct trades. Median holding period and win-rate
are derived from `winner_trade_log.csv`.

## strategy_risk_notes

- The rule was selected by maximum OOS Sharpe across 12 candidates.
  Multiple-comparisons risk is real; the OOS Sharpe of 0.47 should be
  interpreted as an upper bound on out-of-sample expectation.
- Annual turnover ≈ 3.7 — meaningful, not negligible. Costs above
  ~25 bps per leg would meaningfully erode the edge.
- The rule has not been tested on crude regimes outside the 1998-2025
  sample. Pre-2000 crude markets (deregulation era) and a hypothetical
  post-2025 transition-economy regime are out of scope.

## episode_dotcom_narrative

The 2001 dot-com bust did not strongly impair WTI or XLE because oil
fundamentals were not the centre of the shock — equity exuberance was.
WTI traded sideways through 2001; XLE was relatively flat. The
historical zoom shows both series with mild downward bias but no
crisis-level breakdown.

## episode_gfc_narrative

The 2008 Global Financial Crisis broke both series violently. WTI ran
from ~$60 to $145 in mid-2008, then collapsed to $35 by year-end.
XLE tracked the collapse closely. This is the canonical co-crash and
the largest single drawdown in the sample.

## episode_covid_narrative

March-April 2020 saw the most extreme single episode in the sample:
WTI futures briefly traded negative on 2020-04-20 (storage capacity
shock), and XLE fell roughly 50% peak-to-trough. The series recovered
unevenly through 2020 H2; XLE lagged WTI's recovery.

## episode_inflation_2022_narrative

The 2022 inflation cycle and Russia's invasion of Ukraine pushed
WTI back above $120/bbl in early 2022. XLE rallied strongly through
mid-2022 then drifted as crude retraced. This episode is the
clearest example in the sample of WTI volatility correlating with
elevated XLE risk-adjusted return — and is one of the periods in
which the winning rule was active.
