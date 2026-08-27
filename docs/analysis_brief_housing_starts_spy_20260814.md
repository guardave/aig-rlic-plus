# Analysis Brief: Housing Starts (SAAR) → S&P 500

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-08-14                |
| **Author**  | Lesandro (Lead Analyst)   |
| **Version** | 1.0                       |
| **Status**  | Approved                  |

> Phase-0 kickoff document for the `housing_starts_spy` pair. Registered in
> `data/prospective_pairs.csv` this wave
> (`housing_starts, Housing Starts, real_estate, SPY, housing_starts_spy, in_progress`) — the
> matrix previously carried only `housing_starts_xle`, so the SPY row was added (mirrors the
> `RE - H Started` Data Master column, source row 106).

## 1. Research Question

**Question:** Does new residential construction activity predict S&P 500 returns? As a
classic early-cycle, interest-rate-sensitive activity indicator, does the pace of housing
starts forecast equity performance?

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H0 | Housing starts have no predictive power for SPY | Toda-Yamamoto Granger, predictive OLS |
| H1 | Rising starts predict positive SPY returns (pro-cyclical, leading) | Local projections, regime analysis |
| H2 | Signal is strongest at 3-6 month horizons and, like INDPRO, direction may surprise at cycle extremes (peak-cycle mean-reversion) | Multi-horizon LP + quartile regime analysis |

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | Housing Starts: Total New Privately-Owned Housing Units Started |
| **ID** | housing_starts |
| **Canonical name** | New Privately-Owned Housing Units Started: Total Units, Thousands of Units, SAAR (FRED) |
| **Source** | FRED: `HOUST` |
| **Frequency** | Monthly (**Seasonally Adjusted Annual Rate**) |
| **Transformation** | YoY% (primary), MoM% (valid — series is SA), 3-month YoY, YoY acceleration, rolling 120M z-score of YoY, contraction flag (YoY<0). Raw level kept for provenance (non-stationary). |
| **Indicator type** | Activity (Housing / Construction) |

> **LEAD-DV1 verification (2026-08-14).** `indicator_map.yaml` maps `RE - H Started` →
> `indicator_id: housing_starts`, `display_name: Housing Starts`, category `real_estate`, and
> the map's housing-family note (verified against Data Master Pre-master row 2, 2026-06-02)
> records **"BP / RE - H Started are level (thousands, SAAR)."** Housing starts is therefore the
> Census/HUD **HOUST** series — Total, Thousands of units, **Seasonally Adjusted Annual Rate** —
> distinct from Building Permits (`permit`/`BP`) and New Home Sales (`nhs` = HSN1FNSA, NSA;
> `nh_sold_saar` = HSN1F, SAAR). The distinct series stay distinct per LEAD-DV1.

> **SA HANDLING (contrast with nhs_spy).** HOUST is already Seasonally Adjusted (annual rate),
> so — unlike `nhs_spy` (HSN1FNSA, NSA) — **no STL/YoY deseasonalisation is required to make a
> signal valid.** MoM% is a legitimate momentum input here. This pair follows the SA
> monthly-indicator template (permit_spy / INDPRO), not the NSA deseasonalisation template. The
> raw SAAR level is trend-dominated / non-stationary and is excluded from the signal set; all
> signals are stationary growth/transform series.

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
| **Mechanism** | Housing starts are a canonical leading indicator: construction commits capital and labour ahead of the broader activity cycle, and residential investment is among the most interest-rate-sensitive GDP components — it turns down early into tightening cycles and recovers early into easing. Rising starts signal expansion; collapsing starts (2006-08) preceded the GFC bear. Per the INDPRO precedent, a far-above-trend reading can flip counter-cyclical at cycle peaks (mean-reversion), so direction is verified empirically before narrative. Because starts and equities are jointly driven by rates and the cycle, reverse causality (SPY→starts, via financial conditions/wealth) is plausible and tested. |
| **Literature support** | Strong (housing starts are a long-established component of the Conference Board Leading Economic Index). |

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample** | 1990-01-01 to latest (HOUST available from 1959; window aligned to SPY history and peer pairs) |
| **IS / OOS** | Tournament OOS policy `v1_max36_25pct_cap120` on the SPY-availability-bound sample (1993 onward) |
| **Frequency** | Monthly (indicator); Daily (target, release-lagged LVCF) |

**Limitations:** Housing bubble 2003-2006 and its GFC collapse may dominate regime models. COVID
caused a sharp starts dip then surge (2020-2021). The 2022-2024 rate-shock cut starts materially
— a strong recent regime the OOS window captures. Starts are volatile and revised; the daily LVCF
uses an approximate Census/HUD release calendar (~mid-month for the prior month).

## 6-12. Per template — standard parameters apply.

**Tournament:** INDPRO / Building Permits monthly-indicator template (monthly indicator, lead grid
L0-L12 per ECON-LL1, 3 strategies, fixed/rolling/z-score thresholds), both pro/counter
orientations. RoC/momentum-over-level is the confirmed cross-pair pattern; include but do not
presuppose. Mandatory reverse-causality check per §11.2 (verify lead vs coincident/lagging).

**Closest analog:** `permit_spy` (completed, Sharpe 1.45, pro-cyclical leading, monthly, L6) —
same real_estate/SA construction family; reuse pipeline/chart/portal template directly. Unlike
`nhs_spy`, **no NSA→YoY deseasonalisation step is needed** (HOUST is SA at source).

**Distribution:** All agents (Dana, Evan, Vera, Ray, Ace, Quincy).
