# Analysis Brief: WTI Crude Oil Price → XLE

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-06-03                |
| **Author**  | Lead Lesandro (Mode 2)    |
| **Version** | 1.0                       |
| **Status**  | Approved (post-hoc — see note in §10)  |

> **Post-hoc note (DPS-AB1).** This brief is being authored AFTER the Mode-2 build
> completed (commit `c59f0c2`, 2026-06-02) as part of resolving the Completeness
> checker's finding that DPS-AB1 was missing. Per LEAD-NPB1, the brief should
> precede dispatch; under Mode 2 single-maker, Lead's hat-switches collapsed the
> brief into the pipeline directly. This document captures, post-hoc, the
> identity, hypotheses, and method choices that the pipeline embodied — so the
> audit trail is complete even when authored out-of-order.

---

## 1. Research Question

**Question:** Does the shape (volatility, momentum, cycle position) of WTI crude
oil prices help time exposure to XLE (the Energy Select Sector ETF) — and if so,
through what kind of conditioning?

### Hypotheses

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H₀ | XLE buy-and-hold is optimal; no WTI-derived signal beats it OOS. | OOS Sharpe comparison across a 12-strategy universe vs the same-window B&H benchmark. |
| H₁ | A WTI-momentum signal (4w/13w/26w log return) provides timing edge. | OLS lead-lag regressions; OOS Sharpe of momentum-family rules. |
| H₂ | A WTI-cycle-position signal (52w/104w z-score) provides timing edge. | OOS Sharpe of z-score-family rules at both top and bottom entry levels. |
| H₃ | A WTI-volatility-regime signal (13w realized vol percentile) provides timing edge. | OOS Sharpe of vol-regime rules at both low- and high-vol entries. |

---

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | WTI Crude Oil Spot Price |
| **ID** | `crude_oil` |
| **Canonical name** | West Texas Intermediate spot price (FRED `WCOILWTICO`) |
| **Source** | `data/Data Master.xlsx` sheet `WCOILWTICO` (cached from FRED) |
| **Frequency** | Weekly (Friday close) |
| **Units** | USD per barrel, Not Seasonally Adjusted |
| **Sample** | 1986-01-03 to 2025-10-10 |
| **Pre-master row 2** | col 76, sheet `WCOILWTICO` col B (LEAD-DV1 satisfied) |

**Disambiguation.** Pre-master has TWO crude-related columns: WCOILWTICO (price)
used here, and WTTSTUS1 (inventory) which maps to a separate pair_id
`wttstus1_spy`.

---

## 3. Target Specification

| Field | Value |
|-------|-------|
| **Target** | Energy Select Sector SPDR (XLE) |
| **ID** | `xle` |
| **Source** | `data/Data Master.xlsx` sheet `etf_prices` col XLE |
| **Frequency** | Daily, resampled to weekly Friday close to align with WTI |
| **Sample** | 1998-12-22 to 2025-10-23 |

---

## 4. Sample & Alignment

- **Joint sample** (after alignment): 1998-12-25 to 2025-10-10, 1,399 weekly observations. The first observation has no usable XLE weekly return, so the estimation sample is 1,398 observations from 1999-01-01.
- **Frequency alignment policy:** XLE resampled DOWN to weekly Friday close (last-observation-of-week). WTI kept at its native weekly frequency.
- **IS/OOS split:** 60/40 calendar split of the 1,398-observation estimation sample.
  - IS: 1999-01-01 to 2015-01-16 (838 obs)
  - OOS: 2015-01-23 to 2025-10-10 (560 obs)
- **No look-ahead:** signal computed at Friday close week t; position taken at Friday close week t+1 (one-week lag built into `_build_position`).

---

## 5. Strategy Universe

12 strategy families, enumerated as a single neutral tournament:

| Family group | Variants |
|---|---|
| Momentum (long-only) | 4w, 13w, 26w log-return signs |
| Z-score (long-only) | 52w and 104w windows, both above-+0.5 and below--0.5 entries (4 variants) |
| Vol regime (long-only) | 13w realized-vol percentile in 5y rolling — both low (<50%) and high (>75%) entries |
| Sign-based (long-short) | momentum_4w, momentum_13w, z_52w signed positions (3 variants) |

All families share the same translation primitive: signal True → position +1 (or
−1 for long-short); signal False → 0. Cost model: 5 bps per unit of |Δposition|.

---

## 6. Methods & Tests

| Level | Test | Purpose |
|---|---|---|
| L1 | ADF + KPSS stationarity | Confirm derived signal features (log returns, z-scores, vol-percentiles) are usable in regression and rule-based strategies. |
| L1 | Pearson + Spearman correlation | Quantify contemporaneous WTI-XLE link. |
| L1 | Lead-lag OLS at 0..8 weeks | Test whether linear lagged relationships carry predictive content. HC3 robust SE. |
| L2 | Rolling 52w correlation | Surface time-varying co-movement. |
| L2 | CUSUM of recursive residuals | Detect structural breaks in the linear WTI→XLE relationship. |
| L3 | Strategy tournament (12 families) | OOS Sharpe ranking; select winner via `scripts.tournament.select_winner`. |

---

## 7. Acceptance Criteria

- Winner OOS Sharpe must exceed XLE buy-and-hold Sharpe by ≥ 0.10 (risk-adjusted).
- Winner OOS max drawdown must be no worse than XLE buy-and-hold max drawdown.
- Annual turnover < 10 (i.e. rule trades < 10 times per year).
- All required artifacts emitted; GATE-CMP1 PASS.

---

## 8. Result (observed, post-hoc)

| Metric | Winner (`wti_high_vol_long`) | XLE buy-and-hold | Delta |
|---|---|---|---|
| OOS Sharpe | 0.47 | 0.04 | +0.43 ✓ |
| OOS ann. return | 8.8% | 1.2% | +7.6 pp |
| OOS max drawdown | −24.5% | −68.8% | +44.3 pp ✓ |
| OOS annual turnover | 3.7 | 0 | within budget ✓ |
| OOS trades | 20 | — | within budget ✓ |

All acceptance criteria met. Winner is in the H₃ family (vol-regime) — H₁
(momentum) and H₂ (z-score) families ranked lower.

---

## 9. References

- Hamilton, J. D. (1989). *A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle*. Econometrica.
- Ang, A., & Bekaert, G. (2002). *International Asset Allocation with Regime Shifts*. Review of Financial Studies.
- Harvey, C. R., & Liu, Y. (2014). *... and the Cross-Section of Expected Returns*. Review of Financial Studies. (Multiple-testing in strategy selection.)

---

## 10. Post-hoc authoring note

This brief was authored on 2026-06-03 to close GATE-CMP1 check DPS-AB1, which
was added to `_check_backlog_hygiene` as a mechanical gate after the
Completeness checker subagent flagged the missing brief on the 2026-06-02
build. The hypotheses and methods described above were embodied in the
pipeline (`scripts/pair_pipeline_crude_oil_xle.py`) as authored; this
document is a faithful reconstruction, not a redesign.

Future builds under LEAD-NPB1 + Mode 2 should author the brief at maker-phase
start (Dana hat), not at checker-phase resolution. The current build is the
test case that surfaced the discipline gap.
