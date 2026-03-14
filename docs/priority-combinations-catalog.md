# Catalog E: Priority Combinations

## Human-Analyzed Indicator x Target Pairs — Benchmark Reference

These 73 pairs were analyzed manually and found to have meaningful indicator-target relationships. Agent team outputs will be compared against these human findings to validate automated analysis quality and identify gaps.

---

*Created: 2026-03-14*
*Last updated: 2026-03-14*

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total pairs | 73 |
| Targets covered | 7 (SPY, XLC, XLE, XLI, XLK, XLP, XLY) |
| Unique indicators used | 27 |
| Rows in catalog | 74 (includes SA/NSA variants counted separately) |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| Pending | Not yet analyzed by agent team |
| In Progress | Agent team currently running |
| Completed | Agent analysis complete |
| Compared | Human vs. agent comparison done |

---

## SPY (21 pairs)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 1 | S&P 500 | SPY | Industrial Production (2017=100) | I1 | INDPRO | FRED: INDPRO | Completed | OOS Sharpe 1.10 (3M mom, L6). Z-score counter-cyclical surprise. |
| 2 | S&P 500 | SPY | SOFR-US3M (TED Rate) | I17 | SOFR_US3M | Computed: FRED SOFR - TB3MS | Pending | |
| 3 | S&P 500 | SPY | Building Permits | I9 | PERMIT | FRED: PERMIT | Pending | |
| 4 | S&P 500 | SPY | US10Y-US3M | I18 | T10Y3M | FRED: T10Y3M | Pending | |
| 5 | S&P 500 | SPY | Michigan Consumer Sentiment | I14 | UMCSENT | FRED: UMCSENT | Pending | |
| 6 | S&P 500 | SPY | New Home Sales (SA) | I10a | HSN1F | FRED: HSN1F | Pending | |
| 7 | S&P 500 | SPY | ISM Manufacturing PMI | I2 | ISM_MFG_PMI | ISM direct | Pending | |
| 8 | S&P 500 | SPY | ISM Services PMI | I3 | ISM_SVC_PMI | ISM direct | Pending | |
| 9 | S&P 500 | SPY | PHLX SOX Index | I23 | SOX | Yahoo: ^SOX | Pending | |
| 10 | S&P 500 | SPY | Portland Cement Shipments | I8 | CEMENT_SHIP | Portland Cement Assoc. | Pending | |
| 11 | S&P 500 | SPY | VIX/VIX3M | I22 | VIX_VIX3M | Computed: Yahoo ^VIX / ^VIX3M | Pending | |
| 12 | S&P 500 | SPY | M2SL YoY | I21 | M2SL_YOY | Derived: FRED M2SL | Pending | |
| 13 | S&P 500 | SPY | Unemployment Rate | I4 | UNRATE | FRED: UNRATE | Pending | |
| 14 | S&P 500 | SPY | Import Price Index | I24 | IMP_PRICE | FRED: IR | Pending | |
| 15 | S&P 500 | SPY | Retail Inventories/Sales | I15 | RETAILIRSA | FRED: RETAILIRSA | Pending | |
| 16 | S&P 500 | SPY | Manufacturers' New Orders | I26 | NEWORDER | FRED: NEWORDER | Pending | |
| 17 | S&P 500 | SPY | Credit Card Default | I16 | CC_DEFAULT | FRED: DRCCLACBS | Pending | |
| 18 | S&P 500 | SPY | Cass Freight Index | I25 | CASS_FREIGHT | Cass Information Systems | Pending | |
| 19 | S&P 500 | SPY | C&I Loans | I20 | BUSLOANS | FRED: BUSLOANS | Pending | |
| 20 | S&P 500 | SPY | HY-IG Spread | I19 | HY_IG_OAS | Computed: FRED BAMLH0A0HYM2 - BAMLC0A0CM | Pending | |
| 21 | S&P 500 | SPY | Petroleum Inventory | I27 | PETROL_INV | EIA weekly data | Pending | |

---

## XLC (1 pair)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 22 | Communication Services | XLC | ISM Mfg/Svc PMI Ratio | I31 | ISM_MFG_SVC_RATIO | Derived: I2 / I3 | Pending | |

---

## XLE (17 pairs)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 23 | Energy | XLE | PHLX SOX Index | I23 | SOX | Yahoo: ^SOX | Pending | |
| 24 | Energy | XLE | ISM Manufacturing PMI | I2 | ISM_MFG_PMI | ISM direct | Pending | |
| 25 | Energy | XLE | ISM Services PMI | I3 | ISM_SVC_PMI | ISM direct | Pending | |
| 26 | Energy | XLE | Michigan Consumer Sentiment | I14 | UMCSENT | FRED: UMCSENT | Pending | |
| 27 | Energy | XLE | VIX/VIX3M | I22 | VIX_VIX3M | Computed: Yahoo ^VIX / ^VIX3M | Pending | |
| 28 | Energy | XLE | US10Y-US3M (displayed inverted) | I18 | T10Y3M | FRED: T10Y3M | Pending | |
| 29 | Energy | XLE | Import Price Index | I24 | IMP_PRICE | FRED: IR | Pending | |
| 30 | Energy | XLE | Job Openings | I6 | JTSJOL | FRED: JTSJOL | Pending | |
| 31 | Energy | XLE | Manufacturers' New Orders | I26 | NEWORDER | FRED: NEWORDER | Pending | |
| 32 | Energy | XLE | Building Permits | I9 | PERMIT | FRED: PERMIT | Pending | |
| 33 | Energy | XLE | Housing Starts | I11 | HOUST | FRED: HOUST | Pending | |
| 34 | Energy | XLE | Petroleum Inventory | I27 | PETROL_INV | EIA weekly data | Pending | |
| 35 | Energy | XLE | Crude Oil Price | I28 | CL_F | Yahoo: CL=F | Pending | |
| 36 | Energy | XLE | (Electricity-CPI) YoY | I29 | ELEC_CPI_YOY | Derived: BLS electricity CPI component | Pending | |
| 37 | Energy | XLE | Wells Fargo Housing Index | I12 | NAHB_HMI | FRED: NAHBHMI | Pending | |
| 38 | Energy | XLE | Architecture Billings Index | I13 | ABI | AIA (subscription/scrape) | Pending | |
| 39 | Energy | XLE | Cass Freight Index | I25 | CASS_FREIGHT | Cass Information Systems | Pending | |

---

## XLI (10 pairs)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 40 | Industrials | XLI | ISM Mfg/Svc PMI Ratio | I31 | ISM_MFG_SVC_RATIO | Derived: I2 / I3 | Pending | |
| 41 | Industrials | XLI | Industrial Production (2017=100) | I1 | INDPRO | FRED: INDPRO | Pending | |
| 42 | Industrials | XLI | Gold/Copper Ratio | I30 | GOLD_COPPER | Computed: GC=F / HG=F | Pending | |
| 43 | Industrials | XLI | US10Y-US3M | I18 | T10Y3M | FRED: T10Y3M | Pending | |
| 44 | Industrials | XLI | VIX/VIX3M | I22 | VIX_VIX3M | Computed: Yahoo ^VIX / ^VIX3M | Pending | |
| 45 | Industrials | XLI | Advanced Retail Sales | I7 | RSAFS | FRED: RSAFS | Pending | |
| 46 | Industrials | XLI | Import Price Index | I24 | IMP_PRICE | FRED: IR | Pending | |
| 47 | Industrials | XLI | Job Openings | I6 | JTSJOL | FRED: JTSJOL | Pending | |
| 48 | Industrials | XLI | Manufacturers' New Orders | I26 | NEWORDER | FRED: NEWORDER | Pending | |
| 49 | Industrials | XLI | Manufacturers' New Orders YoY | I32 | NEWORDER_YOY | Derived: I26 YoY change | Pending | |

---

## XLK (1 pair)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 50 | Technology | XLK | Michigan Consumer Sentiment | I14 | UMCSENT | FRED: UMCSENT | Pending | |

---

## XLP (12 pairs)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 51 | Consumer Staples | XLP | Portland Cement Shipments | I8 | CEMENT_SHIP | Portland Cement Assoc. | Pending | |
| 52 | Consumer Staples | XLP | ISM Services PMI | I3 | ISM_SVC_PMI | ISM direct | Pending | |
| 53 | Consumer Staples | XLP | Industrial Production (2017=100) | I1 | INDPRO | FRED: INDPRO | Pending | |
| 54 | Consumer Staples | XLP | ISM Manufacturing PMI | I2 | ISM_MFG_PMI | ISM direct | Pending | |
| 55 | Consumer Staples | XLP | SOFR-US3M (TED Rate) | I17 | SOFR_US3M | Computed: FRED SOFR - TB3MS | Pending | |
| 56 | Consumer Staples | XLP | Michigan Consumer Sentiment | I14 | UMCSENT | FRED: UMCSENT | Pending | |
| 57 | Consumer Staples | XLP | Building Permits | I9 | PERMIT | FRED: PERMIT | Pending | |
| 58 | Consumer Staples | XLP | VIX/VIX3M | I22 | VIX_VIX3M | Computed: Yahoo ^VIX / ^VIX3M | Pending | |
| 59 | Consumer Staples | XLP | US10Y-US3M | I18 | T10Y3M | FRED: T10Y3M | Pending | |
| 60 | Consumer Staples | XLP | HY-IG Spread | I19 | HY_IG_OAS | Computed: FRED BAMLH0A0HYM2 - BAMLC0A0CM | Pending | |
| 61 | Consumer Staples | XLP | C&I Loans | I20 | BUSLOANS | FRED: BUSLOANS | Pending | |
| 62 | Consumer Staples | XLP | Cass Freight Index | I25 | CASS_FREIGHT | Cass Information Systems | Pending | |

---

## XLY (12 pairs)

| # | Target | Ticker | Indicator | Indicator ID | Canonical Name | Source | Status | Comparison Notes |
|---|--------|--------|-----------|--------------|----------------|--------|--------|------------------|
| 63 | Consumer Discretionary | XLY | Michigan Consumer Sentiment | I14 | UMCSENT | FRED: UMCSENT | Pending | |
| 64 | Consumer Discretionary | XLY | ISM Mfg/Svc PMI Ratio | I31 | ISM_MFG_SVC_RATIO | Derived: I2 / I3 | Pending | |
| 65 | Consumer Discretionary | XLY | PHLX SOX Index | I23 | SOX | Yahoo: ^SOX | Pending | |
| 66 | Consumer Discretionary | XLY | Industrial Production (2017=100) | I1 | INDPRO | FRED: INDPRO | Pending | |
| 67 | Consumer Discretionary | XLY | VIX/VIX3M | I22 | VIX_VIX3M | Computed: Yahoo ^VIX / ^VIX3M | Pending | |
| 68 | Consumer Discretionary | XLY | US10Y-US3M | I18 | T10Y3M | FRED: T10Y3M | Pending | |
| 69 | Consumer Discretionary | XLY | Wells Fargo Housing Index | I12 | NAHB_HMI | FRED: NAHBHMI | Pending | |
| 70 | Consumer Discretionary | XLY | New Home Sales (SA) | I10a | HSN1F | FRED: HSN1F | Pending | |
| 71 | Consumer Discretionary | XLY | Cass Freight Index | I25 | CASS_FREIGHT | Cass Information Systems | Pending | |
| 72 | Consumer Discretionary | XLY | New Home Sales (NSA) | I10b | HSN1FNSA | FRED: HSN1FNSA | Pending | |
| 73 | Consumer Discretionary | XLY | Manufacturers' New Orders | I26 | NEWORDER | FRED: NEWORDER | Pending | |
| 74 | Consumer Discretionary | XLY | Job Openings | I6 | JTSJOL | FRED: JTSJOL | Pending | |

---

## Cross-Reference: Indicator Coverage

How often each indicator appears across the 7 target ETFs.

| Indicator ID | Indicator | SPY | XLC | XLE | XLI | XLK | XLP | XLY | Total |
|--------------|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:-----:|
| I1 | Industrial Production (2017=100) | x | | | x | | x | x | 4 |
| I2 | ISM Manufacturing PMI | x | | x | | | x | | 3 |
| I3 | ISM Services PMI | x | | x | | | x | | 3 |
| I4 | Unemployment Rate | x | | | | | | | 1 |
| I6 | Job Openings | | | x | x | | | x | 3 |
| I7 | Advanced Retail Sales | | | | x | | | | 1 |
| I8 | Portland Cement Shipments | x | | | | | x | | 2 |
| I9 | Building Permits | x | | x | | | x | | 3 |
| I10a | New Home Sales (SA) | x | | | | | | x | 2 |
| I10b | New Home Sales (NSA) | | | | | | | x | 1 |
| I11 | Housing Starts | | | x | | | | | 1 |
| I12 | Wells Fargo Housing Index | | | x | | | | x | 2 |
| I13 | Architecture Billings Index | | | x | | | | | 1 |
| I14 | Michigan Consumer Sentiment | x | | x | | x | x | x | 5 |
| I15 | Retail Inventories/Sales | x | | | | | | | 1 |
| I16 | Credit Card Default | x | | | | | | | 1 |
| I17 | SOFR-US3M (TED Rate) | x | | | | | x | | 2 |
| I18 | US10Y-US3M | x | | x | x | | x | x | 5 |
| I19 | HY-IG Spread | x | | | | | x | | 2 |
| I20 | C&I Loans | x | | | | | x | | 2 |
| I21 | M2SL YoY | x | | | | | | | 1 |
| I22 | VIX/VIX3M | x | | x | x | | x | x | 5 |
| I23 | PHLX SOX Index | x | | x | | | | x | 3 |
| I24 | Import Price Index | x | | x | x | | | | 3 |
| I25 | Cass Freight Index | x | | x | | | x | x | 4 |
| I26 | Manufacturers' New Orders | x | | x | x | | | x | 4 |
| I27 | Petroleum Inventory | x | | x | | | | | 2 |
| I28 | Crude Oil Price | | | x | | | | | 1 |
| I29 | (Electricity-CPI) YoY | | | x | | | | | 1 |
| I30 | Gold/Copper Ratio | | | | x | | | | 1 |
| I31 | ISM Mfg/Svc PMI Ratio | | x | | x | | | x | 3 |
| I32 | Manufacturers' New Orders YoY | | | | x | | | | 1 |
| | **Column Total** | **21** | **1** | **17** | **10** | **1** | **12** | **12** | **74** |

### Most-Connected Indicators (appearing in 4+ targets)

| Rank | Indicator ID | Indicator | Targets | Count |
|------|--------------|-----------|---------|:-----:|
| 1 | I14 | Michigan Consumer Sentiment | SPY, XLE, XLK, XLP, XLY | 5 |
| 2 | I18 | US10Y-US3M | SPY, XLE, XLI, XLP, XLY | 5 |
| 3 | I22 | VIX/VIX3M | SPY, XLE, XLI, XLP, XLY | 5 |
| 4 | I1 | Industrial Production (2017=100) | SPY, XLI, XLP, XLY | 4 |
| 5 | I25 | Cass Freight Index | SPY, XLE, XLP, XLY | 4 |
| 6 | I26 | Manufacturers' New Orders | SPY, XLE, XLI, XLY | 4 |

### Target-Exclusive Indicators (appearing in only 1 target)

| Indicator ID | Indicator | Exclusive To |
|--------------|-----------|--------------|
| I4 | Unemployment Rate | SPY |
| I7 | Advanced Retail Sales | XLI |
| I10b | New Home Sales (NSA) | XLY |
| I11 | Housing Starts | XLE |
| I13 | Architecture Billings Index | XLE |
| I15 | Retail Inventories/Sales | SPY |
| I16 | Credit Card Default | SPY |
| I21 | M2SL YoY | SPY |
| I28 | Crude Oil Price | XLE |
| I29 | (Electricity-CPI) YoY | XLE |
| I30 | Gold/Copper Ratio | XLI |
| I32 | Manufacturers' New Orders YoY | XLI |

---

## Notes

- XLY has 12 unique pairs (rows 63--74).
- Total: 74 rows, 73 unique combinations (SPY Building Permits / Housing Permits deduped).
- SA vs. NSA variants (I10a vs. I10b) are counted as distinct pairs.
- This catalog is the benchmark for human vs. agent comparison.

---

## Maintenance

- **Status transitions:** Pending --> In Progress --> Completed --> Compared
- **Comparison Notes column:** Document differences between human and agent findings (e.g., agent missed the relationship, agent found it with different lag, agent found stronger/weaker effect).
- **Update status** as agent teams complete analysis runs.
- **Owner:** Alex (lead analyst) maintains this catalog.

---

*Catalog E is part of the [Reference Catalogs Index](reference-catalogs-index.md).*
