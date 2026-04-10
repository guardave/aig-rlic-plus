# Analysis Brief: HY-IG Credit Spread → S&P 500 (v2)

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-04-10                |
| **Author**  | Ray (Research Agent), on behalf of Lesandro (Lead Analyst) |
| **Version** | 1.0                       |
| **Status**  | Approved                  |

> **Note:** This is the v2 re-run of the HY-IG → SPY analysis (pair #20, originally completed 2026-02-28).
> The `pair_id` for this version is `hy_ig_v2_spy`. The original analysis (`hy_ig_spy`) is frozen as the
> \"Sample Analysis\" reference. This brief follows updated SOPs and the standardized analysis brief template.

---

## 1. Research Question

**Question:** Does the high-yield minus investment-grade (HY-IG) credit spread predict S&P 500 equity returns? If so, through what mechanism, at what horizons, and can the signal be profitably traded?

### Hypotheses

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H0 | The HY-IG credit spread has no predictive power for SPY returns at any horizon or in any regime | Toda-Yamamoto Granger causality (both directions), transfer entropy, local projections -- all returning insignificant results |
| H1 | HY-IG spread changes **lead** SPY returns, with stronger predictive power during stress regimes | Toda-Yamamoto Granger causality, transfer entropy, local projections -- tested in both directions and per regime (Methods Catalog: Section 2, Lead-Lag & Causality) |
| H2 | The credit-equity relationship is **nonlinear** -- it activates at stress thresholds that are regime-dependent, not fixed | Markov-switching regression, HMM, quantile regression, data-driven threshold detection via Jenks, GMM, CUSUM (Methods Catalog: Section 3, Regime Identification) |
| H3 | A credit-signal equity strategy **beats buy-and-hold SPY** out-of-sample after transaction costs | Combinatorial tournament across signals, thresholds, strategies, lookbacks, and lead times; walk-forward validation with bootstrap significance (Methods Catalog: Section 7, Signal Extraction) |

---

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | HY-IG Credit Spread |
| **ID** | `hy_ig_v2` |
| **Canonical name** | ICE BofA US High Yield OAS minus ICE BofA US Investment Grade OAS |
| **Source** | FRED: `BAMLH0A0HYM2` minus `BAMLC0A0CM` |
| **Frequency** | Daily |
| **Transformation** | Level, Z-score (252d, 504d), Percentile Rank (504d, 1260d), RoC (21d, 63d, 126d), MoM/QoQ/YoY change, Acceleration |
| **Indicator type** | **Credit Spread** |

**Indicator type classification rationale:** The HY-IG spread directly measures the yield differential between high-yield and investment-grade corporate bonds, reflecting credit risk pricing. This falls unambiguously under Step 1 of the decision tree: \"Does it measure credit risk directly (spreads, default rates, CDS)?\" -- Yes. No secondary classification needed.

---

## 3. Target Specification

| Field | Value |
|-------|-------|
| **Target** | S&P 500 |
| **ID** | `spy` |
| **Ticker** | SPY |
| **Asset class** | Equity |
| **Benchmark** | SPY (buy-and-hold) |
| **Trading calendar** | US Market Hours |
| **Transaction cost assumption** | 5 bps per round-trip trade |

---

## 4. Expected Direction

| Field | Value |
|-------|-------|
| **Expected direction** | `counter_cyclical` |
| **Mechanism** | Widening HY-IG spreads reflect deteriorating credit conditions and rising default risk. This reduces firms' access to capital, depresses corporate investment, and signals a risk-off environment in which investors rotate from equities to safe assets. Equity markets respond with a lag as earnings expectations adjust downward. The Merton (1974) structural credit model links corporate asset value to both equity and debt: when asset value declines toward the debt barrier, equity falls and credit spreads widen simultaneously. The excess bond premium (EBP) component -- capturing risk appetite and credit supply shocks -- drives most of the predictive power (Gilchrist & Zakrajsek 2012). |
| **Literature support** | **Strong** (5+ peer-reviewed studies with consistent findings) |

**Direction determination workflow:**
- Step 1: Academic evidence? **Yes.** Gilchrist & Zakrajsek (2012), Faust et al. (2013), Mueller (2009), Philippon (2009), Acharya & Johnson (2007), Norden & Weber (2009) -- 6+ studies agree on counter-cyclical direction. Mark `literature_support: Strong`.
- **Direction confidence mapping:** Strong -> `direction_confidence: high` for Evan's `interpretation_metadata.json`.

---

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample period** | 2000-01-01 to 2025-12-31 |
| **In-sample (IS)** | 2000-01-01 to 2017-12-31 |
| **Out-of-sample (OOS)** | 2018-01-01 to 2025-12-31 |
| **Minimum sample constraint** | 15 years IS |
| **Frequency** | Daily (business-day calendar) |
| **Approximate IS observations** | ~4,500 |
| **Approximate OOS observations** | ~2,000 |

**Known limitations:**

- ICE BofA OAS indices begin in 1996 but are most reliable from 2000 onward. Pre-2000 data exists but coverage quality is lower.
- The IS period covers the dot-com bust (2001-02) and the GFC (2007-09) -- two major stress episodes -- plus two long expansions (2003-07, 2010-17).
- The OOS period includes the 2018 volatility spike, the COVID crash (2020), the 2022 Fed rate shock, and the 2023-25 recovery. This provides a rich and diverse stress-test window.
- The 2022 rate shock is notable: spreads widened primarily due to monetary policy tightening rather than credit deterioration -- a different mechanism than the GFC or COVID. The signal may behave differently in rate-driven versus credit-driven stress.

---

## 6. Data Requirements

### 6.1 Core and Secondary Series

| # | Variable | Preferred Name | Source | Frequency | Transform | Stationarity Test | Priority |
|---|----------|---------------|--------|-----------|-----------|-------------------|----------|
| 1 | HY OAS | `hy_oas` | FRED: `BAMLH0A0HYM2` | Daily | Level | ADF, KPSS | Core |
| 2 | IG OAS | `ig_oas` | FRED: `BAMLC0A0CM` | Daily | Level | ADF, KPSS | Core |
| 3 | BB HY OAS | `bb_oas` | FRED: `BAMLH0A1HYBB` | Daily | Level | ADF, KPSS | Core |
| 4 | CCC HY OAS | `ccc_oas` | FRED: `BAMLH0A3HYC` | Daily | Level | ADF, KPSS | Core |
| 5 | SPY | `spy_close` | Yahoo: `SPY` | Daily | Log return | ADF, KPSS | Core |
| 6 | VIX | `vix` | Yahoo: `^VIX` | Daily | Level | ADF, KPSS | Core |
| 7 | VIX3M | `vix3m` | Yahoo: `^VIX3M` | Daily | Level | ADF, KPSS | Core |
| 8 | 10Y Treasury | `dgs10` | FRED: `DGS10` | Daily | Level | ADF, KPSS | Core |
| 9 | 3M Treasury | `dtb3` | FRED: `DTB3` | Daily | Level | ADF, KPSS | Core |
| 10 | 2Y Treasury | `dgs2` | FRED: `DGS2` | Daily | Level | ADF, KPSS | Core |
| 11 | NFCI | `nfci` | FRED: `NFCI` | Weekly (ffill to daily) | Level | ADF, KPSS | Core |
| 12 | KBE (Bank ETF) | `kbe` | Yahoo: `KBE` | Daily | Log return | ADF, KPSS | Core |
| 13 | IWM (Small-Cap ETF) | `iwm` | Yahoo: `IWM` | Daily | Log return | ADF, KPSS | Secondary |
| 14 | MOVE Index | `move` | Yahoo: `^MOVE` | Daily | Level | ADF, KPSS | Secondary |
| 15 | Initial Claims | `icsa` | FRED: `ICSA` | Weekly (ffill to daily) | Level | ADF, KPSS | Secondary |
| 16 | Fed Funds Rate | `dff` | FRED: `DFF` | Daily | Level | ADF, KPSS | Secondary |
| 17 | BBB OAS | `bbb_oas` | FRED: `BAMLC0A4CBBB` | Daily | Level | ADF, KPSS | Secondary |
| 18 | FSI (Financial Stress) | `fsi` | FRED: `STLFSI2` | Weekly (ffill to daily) | Level | ADF, KPSS | Secondary |
| 19 | Gold | `gold` | Yahoo: `GC=F` | Daily | Log return | ADF, KPSS | Secondary |
| 20 | Copper | `copper` | Yahoo: `HG=F` | Daily | Log return | ADF, KPSS | Secondary |
| 21 | DXY (Dollar Index) | `dxy` | Yahoo: `DX-Y.NYB` | Daily | Log return | ADF, KPSS | Secondary |
| 22 | SOFR | `sofr` | FRED: `SOFR` | Daily | Level | ADF, KPSS | Secondary |
| 23 | HYG (HY Bond ETF) | `hyg` | Yahoo: `HYG` | Daily | Log return | ADF, KPSS | Secondary |

**Availability:** All 23 series confirmed available through the team's MCP stack (FRED and Yahoo Finance). No sourcing risk.

### 6.2 Derived Series

| # | Derived Variable | Computation | Depends On |
|---|-----------------|-------------|------------|
| D1 | HY-IG Spread | `BAMLH0A0HYM2 - BAMLC0A0CM` | #1, #2 |
| D2 | HY-IG Z-Score (252d) | `(spread - rolling_mean_252) / rolling_std_252` | D1 |
| D3 | HY-IG Z-Score (504d) | `(spread - rolling_mean_504) / rolling_std_504` | D1 |
| D4 | HY-IG Percentile Rank (504d) | `rolling_rank_504 / 504` | D1 |
| D5 | HY-IG Percentile Rank (1260d) | `rolling_rank_1260 / 1260` | D1 |
| D6 | HY-IG RoC 21d | `(spread / spread.shift(21) - 1) * 100` | D1 |
| D7 | HY-IG RoC 63d | `(spread / spread.shift(63) - 1) * 100` | D1 |
| D8 | HY-IG RoC 126d | `(spread / spread.shift(126) - 1) * 100` | D1 |
| D9 | HY-IG MoM Change (21d) | `spread - spread.shift(21)` | D1 |
| D10 | HY-IG QoQ Change (63d) | `spread - spread.shift(63)` | D1 |
| D11 | HY-IG YoY Change (252d) | `spread - spread.shift(252)` | D1 |
| D12 | Spread Acceleration | `D6 - D6.shift(21)` (diff of 21d RoC) | D6 |
| D13 | CCC-BB Quality Spread | `BAMLH0A3HYC - BAMLH0A1HYBB` | #3, #4 |
| D14 | Spread Realized Vol (21d) | `rolling_std(daily_diff(D1), 21)` | D1 |
| D15 | VIX Term Structure | `VIX3M - VIX` | #6, #7 |
| D16 | 10Y-3M Spread | `DGS10 - DTB3` | #8, #9 |
| D17 | 10Y-2Y Spread | `DGS10 - DGS2` | #8, #10 |
| D18 | Bank/SmallCap Relative Strength | `KBE / IWM` | #12, #13 |
| D19 | NFCI Momentum (13w) | `NFCI - NFCI.shift(13)` (weekly, ffill to daily) | #11 |
| D20 | BBB-IG Spread | `BAMLC0A4CBBB - BAMLC0A0CM` | #17, #2 |

### 6.3 Forward Target Returns (Dependent Variables)

| Horizon | Computation |
|---------|-------------|
| 1d | `SPY.pct_change(1).shift(-1)` |
| 5d | `(SPY.shift(-5) / SPY - 1)` |
| 21d | `(SPY.shift(-21) / SPY - 1)` |
| 63d | `(SPY.shift(-63) / SPY - 1)` |
| 126d | `(SPY.shift(-126) / SPY - 1)` |
| 252d | `(SPY.shift(-252) / SPY - 1)` |

---

## 7. Method Classes

### 7.1 Recommended Categories

| Category | Catalog Section | Applicable? | Rationale |
|----------|----------------|-------------|-----------|
| Correlation & Dependence | Section 1 | **Yes (++)** | Baseline: establishes time-varying co-movement. 6+ studies examine credit-equity correlation across regimes (Guidolin & Timmermann 2007, Ang & Bekaert 2002). |
| Lead-Lag & Causality | Section 2 | **Yes (++)** | Core: 5+ papers document bidirectional causality (Acharya & Johnson 2007, Norden & Weber 2009, Blanco et al. 2005). |
| Regime Identification | Section 3 | **Yes (++)** | Core: Guidolin & Timmermann (2007) show 4 regimes needed; Hamilton (1989) foundation; relationship is strongly regime-dependent. |
| Time-Series Modeling | Section 4 | **Yes (+)** | VECM if cointegrated, VAR otherwise. Collin-Dufresne et al. (2001) find latent common factor. |
| Volatility & Risk | Section 5 | **Yes (+)** | GJR-GARCH with HY-IG exogenous. Campbell & Taksler (2003) show equity vol -> credit spread channel. |
| Nonlinear & ML | Section 6 | **Yes (+)** | Adrian et al. (2019) \"Vulnerable Growth\" documents nonlinear effects concentrated in left tail. |
| Signal Extraction | Section 7 | **Yes (++)** | Combinatorial tournament is primary strategy optimization tool. Essential for H3. |
| Event Study / Tail | Section 8 | **Yes (+)** | Quantile regression at extreme quantiles. Adrian et al. (2019) show left-tail concentration. |

### 7.2 Category Selection Heuristic

For **Credit Spread** indicator type: Always include Corr, Lead-Lag, Regime. Usually include TS, Vol, ML. Optional: Signal, Tail.

**Heuristic result:** All 8 categories recommended.

**Override rationale:** Flagship pair with 15+ citations justifies full coverage. Signal Extraction and Event Study/Tail elevated from optional because (a) tournament is the primary strategy tool, and (b) left-tail concentration from Adrian et al. (2019) is a core hypothesis.

---

## 8. Tournament Design

### 8.1 Dimensions

**Signals (S1-S13):**

| ID | Signal | Variants |
|----|--------|----------|
| S1 | HY-IG Spread Level | Raw |
| S2 | HY-IG Spread Z-Score | 252d, 504d lookback |
| S3 | HY-IG Spread Percentile Rank | 504d, 1260d lookback |
| S4 | HY-IG Spread Rate of Change | 21d, 63d, 126d |
| S5 | CCC-BB Quality Spread | Raw |
| S6 | HMM Regime State | 2-state, 3-state |
| S7 | Markov-Switching Regime | 2-state, 3-state |
| S8 | Composite (Z-Score + VIX Term) | Equal weight, optimized weight |
| S9 | Random Forest Probability | Walk-forward predicted prob |
| S10 | HY-IG MoM Change (21d) | Monthly momentum |
| S11 | HY-IG QoQ Change (63d) | Quarterly momentum |
| S12 | HY-IG YoY Change (252d) | Annual momentum |
| S13 | Spread Acceleration | Diff of 21d RoC |

**Signal Lead Times:** L0 (0d, default for daily), L1, L5, L10, L21, L42, L63, L126, L252

**Threshold Methods (T1-T7):** Fixed percentile, Rolling percentile (504d), Bollinger Band, Jenks Natural Breaks, GMM cluster, HMM posterior probability, CUSUM change-point

**Strategy Types:** P1 Long/Cash, P2 Signal-strength sizing, P3 Vol-targeting (10%), P4 Long/Short

**Lookback Windows:** LB126, LB252, LB504, LB1260

### 8.2 Computational Budget

| Parameter | Value |
|-----------|-------|
| Max players | 10,000 |
| Sampling strategy | Exhaustive (grid < 10,000 after pruning) |
| Estimated post-pruning size | ~800-1,200 |
| Pruning rules | HMM signal + HMM threshold redundant; MS signal + MS threshold redundant; RF prob + ML threshold redundant; L252 + daily RoC inconsistent |

### 8.3 Tournament Rules

| Rule | Specification |
|------|---------------|
| Primary ranking metric | OOS Sharpe ratio (2018-01 to 2025-12) |
| Tiebreakers | Sortino -> Calmar -> max drawdown (least negative) |
| Validity filters | OOS Sharpe > 0; turnover < 24x/year; minimum 30 OOS trades |
| Mandatory benchmark | Buy-and-hold SPY |

### 8.4 Validation on Top 5

Walk-forward (5yr train / 1yr test), bootstrap (10,000 samples), stress tests (Dot-Com, GFC, COVID, Taper Tantrum, 2022 Rate Shock), transaction cost sensitivity (1-20 bps + breakeven), signal decay (1-5 day delay).

---

## 9. Deliverables Checklist

| # | Deliverable | File / Location | Owner | Status |
|---|------------|-----------------|-------|--------|
| 1 | Analysis Brief | `docs/analysis_brief_hy_ig_v2_spy_20260410.md` | Ray/Lesandro | Done |
| 2 | Portal Narrative | `docs/portal_narrative_hy_ig_v2_spy_20260410.md` | Ray | Done |
| 3 | Event Timeline CSV | `docs/event_timeline_hy_ig_v2_spy_20260410.csv` | Ray | Done |
| 4 | Master Dataset | `data/hy_ig_v2_spy_daily_20000101_20251231.parquet` | Dana | Not Started |
| 5-12 | Remaining pipeline deliverables | Various | Dana/Evan/Vera/Ace | Not Started |

---

## 10. Portal Specifications

| Field | Value |
|-------|-------|
| **Page title** | Credit Spreads and Stocks: What the Bond Market Knows |
| **Target audience** | Portfolio managers with economics background but no coding skills; interested laypersons |

**Direction annotation:** \"When the HY-IG credit spread widens (moves up), this historically signals deteriorating credit conditions and tends to precede weaker equity returns. Charts where the indicator is rising should be read as bearish for the target. The relationship is strongest during financial stress periods.\"

**KPI Cards:** Current HY-IG Spread (bps), Current Regime (Calm/Stress), OOS Sharpe (Winner), Max Drawdown Avoided, Signal Status (Risk-On/Off), Days Since Last Signal Change

**Pages:** Story (What the Bond Market Knows), Evidence (The Statistical Evidence), Strategy (Translating the Signal), Methodology (Under the Hood)

---

## 11. Quality Standards

Minimum diagnostics: Jarque-Bera, Breusch-Pagan, Breusch-Godfrey, RESET, ADF+KPSS, VIF. Mandatory reverse causality check (G11). Reconciliation checkpoints at every handoff.

**Interpretation Metadata Template:**
```json
{
  \"indicator\": \"hy_ig_v2\",
  \"target\": \"spy\",
  \"expected_direction\": \"counter_cyclical\",
  \"confidence\": \"high\",
  \"mechanism\": \"Widening HY-IG spreads reflect deteriorating credit conditions, reduced capital access, and risk-off sentiment, leading to weaker equity returns with a lag.\",
  \"caveats\": [
    \"Rate-driven spread widening (2022) may differ from credit-driven widening\",
    \"Bidirectional causality means indicator partially reflects rather than predicts equity moves\",
    \"Post-GFC monetary policy may have altered the transmission mechanism\",
    \"HY-IG spread conflates default risk and liquidity (Longstaff et al. 2005)\"
  ]
}
```

---

## Appendix A: Key References (25 citations)

1. Gilchrist & Zakrajsek (2012), *AER* 102(4): 1692-1720 -- EBP predicts activity
2. Faust et al. (2013), *REstat* 95(5): 1501-1519 -- Credit spreads premier predictor
3. Merton (1974), *JoF* 29(2): 449-470 -- Structural credit model
4. Acharya & Johnson (2007), *JFE* 84(1): 110-141 -- Informed trading in CDS
5. Norden & Weber (2009), *EFM* 15(3): 529-562 -- Equity leads in calm, reverses in stress
6. Guidolin & Timmermann (2007), *JEDC* 31(11): 3503-3544 -- 4 regimes for stock-bond
7. Adrian et al. (2019), *AER* 109(4): 1263-1289 -- Vulnerable Growth
8. Hamilton (1989), *Econometrica* 57(2): 357-384 -- Markov-switching
9. Collin-Dufresne et al. (2001), *JoF* 56(6): 2177-2207 -- Latent common factor
10. Philippon (2009), *QJE* 124(3): 1011-1056 -- Bond market q
11. Mueller (2009), *RFS* -- Credit spread factor predicts GDP
12. Estrella & Mishkin (1998), *REstat* 80(1): 45-61 -- Yield curve predicts recessions
13. Campbell & Taksler (2003), *JoF* 58(6): 2321-2350 -- Equity vol explains spreads
14. Longstaff et al. (2005), *JoF* 60(5): 2213-2253 -- Default vs liquidity decomposition
15. Berndt et al. (2018), *RoF* 22(2): 419-454 -- Credit risk premia fluctuate 10x
16. Blanco et al. (2005), *JoF* 60(5): 2255-2281 -- CDS leads price discovery
17. Ang & Bekaert (2002), *RFS* 15(4): 1137-1187 -- Bear market regime
18. Schreiber (2000), *PRL* 85(2): 461 -- Transfer entropy
19. Diks & Panchenko (2006), *JEDC* 30(9-10): 1647-1669 -- Nonparametric Granger test
20. Toda & Yamamoto (1995), *J. Econometrics* 66(1-2): 225-250 -- Augmented VAR
21. Jorda (2005), *AER* 95(1): 161-182 -- Local projections
22. Johansen (1991), *Econometrica* 59(6): 1551-1580 -- Cointegration testing
23. Gomes & Schmid (2010), WP -- Credit risk premia and aggregate fluctuations
24. Huang et al. (2009), *JBF* 33(11): 2036-2049 -- CDS and systemic risk
25. Longstaff & Schwartz (1995), *JoF* 50(3): 789-819 -- Risky debt valuation

## Appendix B: Data Availability Risk Matrix

All core series have low sourcing risk (FRED/Yahoo). Only medium-risk item: SOFR (post-2018 only; fallback: DFF).

---
*Template source: `docs/analysis_brief_template.md` | Created: 2026-04-10*
