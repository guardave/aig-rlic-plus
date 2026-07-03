# Analysis Brief: New Home Sales (NHS, NSA) → S&P 500

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-07-03                |
| **Author**  | Lesandro (Lead Analyst)   |
| **Version** | 1.0                       |
| **Status**  | Approved                  |

> Phase-0 kickoff document for the `nhs_spy` pair. No agent work begins until this brief reaches
> **Approved**. Already registered in `data/prospective_pairs.csv`
> (`nhs, New Home Sales (NHS), real_estate, SPY, nhs_spy, not_started`) — matrix row 126 (`NHS`)
> has the SPY column marked Done-Y, so no generator change was needed.

## 1. Research Question

**Question:** Does New Home Sales activity predict S&P 500 returns? As an early-cycle housing
demand indicator — one step ahead of construction in the housing pipeline — does the pace of new
single-family home sales forecast equity performance?

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H0 | New Home Sales have no predictive power for SPY | Granger causality, predictive OLS |
| H1 | Rising home sales predict positive SPY returns (pro-cyclical, leading) | Local projections, regime analysis |
| H2 | Signal is strongest at 3-6 month horizons and, like INDPRO, direction may surprise at cycle extremes (peak-cycle mean-reversion) | Multi-horizon LP + quartile regime analysis |

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | New One-Family Houses Sold: United States |
| **ID** | nhs |
| **Canonical name** | New One-Family Houses Sold, Thousands of Units, NSA (FRED) |
| **Source** | FRED: `HSN1FNSA` |
| **Frequency** | Monthly (**Not** Seasonally Adjusted) |
| **Transformation** | YoY% (primary — cancels the fixed seasonal), plus level, 12M MA, deviation from trend, z-score. MoM% NOT used raw (seasonal noise); use YoY or seasonally-adjusted MoM. |
| **Indicator type** | Activity / Survey (Housing) |

> **LEAD-DV1 verification (2026-07-03).** Confirmed against `data/Data Master.xlsx` → Pre-master
> row 2 (COL 28): "New One Family Houses Sold, Units: Thousands of Units, Monthly, Not Seasonally
> Adjusted, from FRED". Three distinct New Home Sales series exist and MUST stay distinct:
> `HSN1FNSA` = Thousands, **NSA** (this pair, `indicator_id: nhs`); `HSN1F` = Thousands, SAAR
> (`indicator_id: nh_sold_saar`, COL 94, catalogued I10a→SPY); YoY% SAAR transform (COL 18).
> **This pair follows the `nhs` id (NSA) per the user's naming decision (2026-07-03).**

> **NSA HANDLING (critical, Dana + Evan).** HSN1FNSA carries a strong, stable monthly seasonal
> (spring selling season peak, winter trough). Raw levels/MoM will be dominated by seasonality
> and are NOT valid signal inputs. Mitigations, in priority order: (a) **YoY% is the primary
> transform** — a 12-month difference cancels a fixed seasonal; (b) a seasonally-adjusted MoM
> via `statsmodels` STL/X-13 if MoM momentum is wanted; (c) z-score computed on the YoY series,
> not the level. This is the principal methodological difference from the SA peers (INDPRO,
> Building Permits) and must be documented in the interpretation_metadata caveats.

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
| **Mechanism** | New home sales are an early housing-demand signal: buyers commit before construction, so sales lead starts, permits, and the broader construction/employment/consumption chain. Housing is ~15-18% of GDP including related spending. Rising sales signal expansion; collapsing sales (2006-07) are a classic recession precursor. Per the INDPRO precedent, a far-above-trend reading can flip counter-cyclical at cycle peaks (mean-reversion), so direction is verified empirically before narrative. |
| **Literature support** | Strong (housing demand is a long-studied leading indicator; new home sales lead starts/permits) |

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample** | 1990-01-01 to 2025-12-31 (HSN1FNSA available from 1963; window aligned to SPY history and peer pairs) |
| **IS** | 1990-01-01 to 2017-12-31 |
| **OOS** | 2018-01-01 to 2025-12-31 |
| **Frequency** | Monthly (indicator); Daily (target) |
| **IS obs** | ~336 months |
| **OOS obs** | ~96 months |

**Limitations:** NSA series requires seasonal handling (see §2). Housing bubble 2003-2007 may
dominate regime models. COVID caused a sharp sales spike then collapse (2020-2022). The 2022-2023
rate-shock crushed sales — a strong recent regime the OOS window captures. New home sales are
volatile and heavily revised — vintage matters (Dana to document data-vintage note).

## 6-12. Per template — standard parameters apply.

**Tournament:** INDPRO / Building Permits monthly-indicator template (monthly indicator, lead grid
L0-L12 per ECON-LL1, 3 strategies, fixed/rolling/z-score thresholds), with **signals computed on
the YoY-transformed / deseasonalised series, not raw NSA levels**. RoC/momentum-over-level is the
confirmed cross-pair pattern; include but do not presuppose. Mandatory reverse-causality check per
§11.2 (verify lead vs coincident/lagging, as with busloans).

**Closest analog:** `permit_spy` (completed, Sharpe 1.45, pro-cyclical leading, monthly, L6) —
reuse pipeline/chart/portal template, but add the NSA→YoY deseasonalisation step that Permits
(SA) did not need.

**Distribution:** All agents (Dana, Evan, Vera, Ray, Ace, Quincy).