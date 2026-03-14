# Analysis Brief: SOFR-US3M (TED Rate) → S&P 500

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-03-14                |
| **Author**  | Lesandro (Lead Analyst)   |
| **Version** | 1.0                       |
| **Status**  | Approved                  |

---

## 1. Research Question

**Question:** Does the SOFR-US3M spread (a modern TED-rate proxy) predict S&P 500 equity returns? If so, at what horizons and can it be traded?

### Hypotheses

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H0 | SOFR-US3M has no predictive power for SPY returns | Granger causality, predictive regressions |
| H1 | Widening SOFR-US3M spread (funding stress) predicts negative SPY returns | Local projections, regime analysis |
| H2 | The relationship is regime-dependent — stronger during stress | Markov-switching, quantile regression |

---

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | SOFR minus US 3-Month Treasury Bill Rate |
| **ID** | sofr_us3m |
| **Canonical name** | SOFR - TB3MS (TED Rate proxy) |
| **Source** | Computed: FRED `SOFR` minus FRED `TB3MS` |
| **Frequency** | Daily |
| **Transformation** | Level, rolling z-score, rate of change |
| **Indicator type** | Yield Curve / Rates |

---

## 3. Target Specification

| Field | Value |
|-------|-------|
| **Target** | S&P 500 |
| **ID** | spy |
| **Ticker** | SPY |
| **Asset class** | Equity |
| **Benchmark** | SPY (buy-and-hold) |
| **Trading calendar** | US Market Hours |
| **Transaction cost assumption** | 5 bps per trade |

---

## 4. Expected Direction

| Field | Value |
|-------|-------|
| **Expected direction** | counter_cyclical |
| **Mechanism** | A widening SOFR-US3M spread indicates funding stress — banks paying more for overnight funding relative to risk-free T-bills. This reflects tightening financial conditions, reduced interbank trust, and potential liquidity constraints. Historically (via the LIBOR-based TED spread), such widening preceded equity weakness through the credit/liquidity channel. |
| **Literature support** | Moderate |

---

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample period** | 2018-04-01 to 2025-12-31 |
| **In-sample (IS)** | 2018-04-01 to 2022-12-31 |
| **Out-of-sample (OOS)** | 2023-01-01 to 2025-12-31 |
| **Minimum sample constraint** | 3 years OOS |
| **Frequency** | Daily |
| **Approximate IS observations** | ~1,200 trading days |
| **Approximate OOS observations** | ~750 trading days |

**Known limitations:**
- SOFR only available from April 2018. Very short sample compared to most macro indicators.
- IS period includes COVID crash (March 2020) and rate hike cycle (2022) — two extreme regimes in a short window.
- OOS period is only 3 years — limited statistical power for long-horizon tests.
- SOFR had quarter-end spikes (repo market stress) that may create noise.

---

## 6. Data Requirements

### 6.1 Core and Secondary Series

| # | Variable | Preferred Name | Source | Frequency | Transform | Priority |
|---|----------|---------------|--------|-----------|-----------|----------|
| 1 | SOFR | sofr | FRED: SOFR | Daily | Level | Core |
| 2 | 3M Treasury Bill | tb3ms | FRED: TB3MS | Daily | Level | Core |
| 3 | SPY | spy | Yahoo: SPY | Daily | Level (adj) | Core |
| 4 | VIX | vix | Yahoo: ^VIX | Daily | Level | Secondary |
| 5 | 10Y Treasury | dgs10 | FRED: DGS10 | Daily | Level | Secondary |
| 6 | Fed Funds Rate | fed_funds | FRED: DFF | Daily | Level | Secondary |

### 6.2 Derived Series

| # | Derived Variable | Computation | Depends On |
|---|-----------------|-------------|------------|
| D1 | SOFR-US3M spread | `sofr - tb3ms` | sofr, tb3ms |
| D2 | Spread z-score (252d) | Rolling z-score | D1 |
| D3 | Spread z-score (126d) | Rolling z-score | D1 |
| D4 | Spread RoC 21d | `(D1 / D1.shift(21) - 1) * 100` | D1 |
| D5 | Spread RoC 63d | Rate of change 63d | D1 |
| D6 | Spread momentum 21d | `D1 - D1.shift(21)` | D1 |
| D7 | Spread percentile rank 252d | Rolling rank | D1 |
| D8 | Spread realized vol 21d | Rolling std of daily changes | D1 |
| D9 | Yield spread 10Y-3M | `dgs10 - tb3ms` (if avail) | dgs10, tb3ms |

### 6.3 Forward Target Returns

| Horizon | Computation |
|---------|-------------|
| 1 day | `spy.pct_change(1).shift(-1)` |
| 5 days | `spy.shift(-5) / spy - 1` |
| 21 days | `spy.shift(-21) / spy - 1` |
| 63 days | `spy.shift(-63) / spy - 1` |

---

## 7. Method Classes

**Recommended categories:** 1 (Corr), 2 (Lead-Lag), 3 (Regime), 4 (Time-Series), 5 (Volatility), 6 (ML)

**Heuristic result:**
- Rule A: Both likely I(1) in levels → test cointegration
- Rule B: Both daily → no frequency mismatch
- Rule C: Yield Curve / Rates type → always Corr, Lead-Lag, TS; usually Regime, Vol
- Rule D: Counter-cyclical (clear) → standard set

---

## 8. Tournament Design

**Signals:** Spread level, z-scores (126d, 252d), RoC (21d, 63d), momentum, percentile rank, realized vol

**Thresholds:** Fixed percentile (IS), rolling percentile, rolling z-score, zero-crossing

**Strategies:** P1 Long/Cash, P2 Signal-Strength, P3 Long/Short

**Lead times:** L0, L1, L5, L10, L21 (daily indicator — shorter leads appropriate)

**Sharpe validity threshold:** 0.3 (equity)

**Transaction costs:** 5 bps

---

**Distribution:** Dana, Evan, Vera, Ace.
