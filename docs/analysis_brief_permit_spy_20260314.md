# Analysis Brief: Building Permits → S&P 500

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-03-14                |
| **Author**  | Lesandro (Lead Analyst)   |
| **Version** | 1.0                       |
| **Status**  | Approved                  |

## 1. Research Question

**Question:** Do Building Permits predict S&P 500 returns? As a classic leading indicator of the housing cycle — and by extension the business cycle — does permitting activity forecast equity performance?

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H0 | Building Permits have no predictive power for SPY | Granger causality, predictive OLS |
| H1 | Rising permits predict positive SPY returns (pro-cyclical, leading) | Local projections, regime analysis |
| H2 | The signal is strongest at 3-6 month horizons (construction lead time) | Multi-horizon LP comparison |

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | New Private Housing Units Authorized by Building Permits |
| **ID** | permit_spy |
| **Canonical name** | PERMIT |
| **Source** | FRED: `PERMIT` |
| **Frequency** | Monthly (SA) |
| **Transformation** | Level, YoY%, MoM%, 12M MA, deviation from trend, z-score |
| **Indicator type** | Activity / Survey (Housing) |

## 3. Target Specification

| Field | Value |
|-------|-------|
| **Target** | S&P 500 |
| **ID** | spy |
| **Ticker** | SPY |
| **Asset class** | Equity |
| **Benchmark** | SPY buy-and-hold |
| **Transaction cost** | 5 bps |

## 4. Expected Direction

| Field | Value |
|-------|-------|
| **Expected direction** | pro_cyclical |
| **Mechanism** | Building permits are a leading indicator of housing construction, which drives employment, consumer spending (wealth effect), and material demand. Rising permits signal economic expansion 6-12 months ahead. Housing is ~15-18% of GDP when including related spending. |
| **Literature support** | Strong (Conference Board LEI component since 1959) |

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample** | 1990-01-01 to 2025-12-31 |
| **IS** | 1990-01-01 to 2017-12-31 |
| **OOS** | 2018-01-01 to 2025-12-31 |
| **Frequency** | Monthly (indicator); Daily (target) |
| **IS obs** | ~336 months |
| **OOS obs** | ~96 months |

**Limitations:** Housing bubble 2003-2007 may dominate regime models. COVID lockdown caused temporary permit collapse (April 2020). Post-COVID lumber/supply-chain issues distorted permits-to-starts relationship.

## 6-12. Per template — standard parameters apply.

**Tournament:** Same design as INDPRO pair (monthly indicator, leads L0-L6 months, 3 strategies, fixed/rolling thresholds).

**Distribution:** All agents.
