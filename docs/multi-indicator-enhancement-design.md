# Multi-Indicator Analysis Enhancement — Design Document

## Context

The project completed its first full pipeline run (HY-IG spread → SPY). The user wants three enhancements:

1. **More analysis categories** — expand the 8-category econometric methods catalog to 14, with a Relevance Matrix mapping indicator types to recommended categories (hybrid: static table + heuristic fallback).
2. **More indicators as first-class subjects** — each new indicator gets its own complete pipeline run with the same SOPs.
3. **Multi-target universe** — beyond SPY, target sector ETFs, fixed income, commodities, and crypto.

Additionally, the user has a list of 73 specific indicator × target combinations analyzed manually. These become the **Priority Combinations Catalog** — a benchmark for comparing human vs. agent team outputs.

The design must also generalize ~10 HY-IG-hardcoded references across SOPs so the playbook works for any indicator-target pair.

**This design document will be promoted to `docs/` as the authoritative design, overriding any prior designs.**

---

## Universes

### Target Universe (38 targets)

#### Broad Equity (1)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T1 | S&P 500 | SPY | Broad Equity |

#### Sector ETFs — All 11 SPDR Select Sector (11)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T2 | Communication Services | XLC | Sector ETF |
| T3 | Energy | XLE | Sector ETF |
| T4 | Industrials | XLI | Sector ETF |
| T5 | Technology | XLK | Sector ETF |
| T6 | Consumer Staples | XLP | Sector ETF |
| T7 | Consumer Discretionary | XLY | Sector ETF |
| T8 | Materials | XLB | Sector ETF |
| T9 | Financials | XLF | Sector ETF |
| T10 | Real Estate | XLRE | Sector ETF |
| T11 | Utilities | XLU | Sector ETF |
| T12 | Health Care | XLV | Sector ETF |

#### Fixed Income — Treasury by Duration (3)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T13 | Short Treasury (1-3Y) | SHY | FI — Short |
| T14 | Intermediate Treasury (7-10Y) | IEF | FI — Intermediate |
| T15 | Long Treasury (20+Y) | TLT | FI — Long |

#### Fixed Income — Inflation-Protected (2)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T16 | TIPS (Broad) | TIP | FI — Inflation |
| T17 | Short-Term TIPS | VTIP | FI — Inflation |

#### Fixed Income — Corporate (5)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T18 | IG Corporate Bond | LQD | FI — IG Corporate |
| T19 | Short-Term IG Corporate | VCSH | FI — IG Corporate |
| T20 | HY Corporate Bond | HYG | FI — HY Corporate |
| T21 | HY Corporate Bond (alt) | JNK | FI — HY Corporate |
| T22 | PIMCO Corporate & Income | PTY | FI — Corporate CEF |

#### Fixed Income — Aggregate (2)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T23 | Aggregate Bond (iShares) | AGG | FI — Aggregate |
| T24 | Total Bond Market (Vanguard) | BND | FI — Aggregate |

#### Commodities — Individual (5)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T25 | Gold | GC=F / GLD | Commodity |
| T26 | Silver | SI=F / SLV | Commodity |
| T27 | Platinum | PL=F / PPLT | Commodity |
| T28 | Brent Crude | BZ=F | Commodity |
| T29 | WTI Crude | CL=F | Commodity |

#### Commodities — Aggregate (3)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T30 | DB Commodity Index | DBC | Commodity Aggregate |
| T31 | S&P GSCI Commodity | GSG | Commodity Aggregate |
| T32 | Optimum Yield Diversified | PDBC | Commodity Aggregate |

#### Crypto (2)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T33 | Bitcoin | BTC-USD | Crypto |
| T34 | Ethereum | ETH-USD | Crypto |

#### Senior Loans (1)

| ID | Target | Ticker | Class |
|----|--------|--------|-------|
| T35 | Senior Loan ETF | BKLN | FI — Senior Loan |

### Indicator Universe (31 unique indicators)

#### Macro / Activity (7)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I1 | Industrial Production Total Index (2017=100) | INDPRO | FRED: INDPRO | Monthly |
| I2 | ISM Manufacturing PMI | ISM_MFG_PMI | ISM direct | Monthly |
| I3 | ISM Services PMI | ISM_SVC_PMI | ISM direct | Monthly |
| I4 | Unemployment Rate | UNRATE | FRED: UNRATE | Monthly |
| I6 | Job Openings (JOLTS) | JTSJOL | FRED: JTSJOL | Monthly |
| I7 | Advanced Retail Sales | RSAFS | FRED: RSAFS | Monthly |
| I8 | Portland Cement Shipments | CEMENT_SHIP | Portland Cement Assoc. | Monthly |

#### Housing / Construction (5)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I9 | Building/Housing Permits | PERMIT | FRED: PERMIT | Monthly |
| I10a | New Home Sales (SA) | HSN1F | FRED: HSN1F | Monthly |
| I10b | New Home Sales (NSA) | HSN1FNSA | FRED: HSN1FNSA | Monthly |
| I11 | Housing Starts | HOUST | FRED: HOUST | Monthly |
| I12 | NAHB/Wells Fargo Housing Market Index | NAHB_HMI | FRED: NAHBHMI | Monthly |
| I13 | Architecture Billings Index | ABI | AIA (subscription/scrape) | Monthly |

#### Consumer / Sentiment (3)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I14 | Michigan Consumer Sentiment | UMCSENT | FRED: UMCSENT | Monthly |
| I15 | Retail Inventories/Sales Ratio | RETAILIRSA | FRED: RETAILIRSA | Monthly |
| I16 | Credit Card Default Rate | CC_DEFAULT | FRED: DRCCLACBS | Quarterly |

#### Financial / Monetary (4)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I17 | SOFR-US3M (TED Rate proxy) | SOFR_US3M | Computed: FRED SOFR - TB3MS | Daily |
| I18 | US10Y-US3M (Yield Curve Slope) | T10Y3M | FRED: T10Y3M | Daily |
| I19 | HY-IG Credit Spread | HY_IG_OAS | Computed: FRED BAMLH0A0HYM2 - BAMLC0A0CM | Daily |
| I20 | Commercial & Industrial Loans | BUSLOANS | FRED: BUSLOANS | Monthly |

#### Monetary Supply (1)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I21 | M2 Money Supply YoY | M2SL_YOY | Derived: FRED M2SL, YoY % change | Monthly |

#### Volatility / Market (2)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I22 | VIX/VIX3M (Term Structure Ratio) | VIX_VIX3M | Computed: Yahoo ^VIX / ^VIX3M | Daily |
| I23 | PHLX Semiconductor Index (SOX) | SOX | Yahoo: ^SOX | Daily |

#### Trade / Transport (3)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I24 | Import Price Index | IMP_PRICE | FRED: IR | Monthly |
| I25 | Cass Freight Index (Shipments) | CASS_FREIGHT | Cass Information Systems | Monthly |
| I26 | Manufacturers' New Orders | NEWORDER | FRED: NEWORDER | Monthly |

#### Energy (3)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I27 | Petroleum Inventory | PETROL_INV | EIA weekly data | Weekly |
| I28 | Crude Oil Price (WTI) | CL_F | Yahoo: CL=F | Daily |
| I29 | (Electricity Price - CPI) YoY | ELEC_CPI_YOY | Derived: BLS electricity CPI component | Monthly |

#### Cross-Asset (1)

| ID | Indicator | Canonical Name | Source | Freq |
|----|-----------|---------------|--------|------|
| I30 | Gold/Copper Ratio | GOLD_COPPER | Computed: GC=F / HG=F | Daily |

#### Derived Ratios (2)

| ID | Indicator | Canonical Name | Derived From |
|----|-----------|---------------|-------------|
| I31 | ISM Mfg PMI / ISM Svc PMI Ratio | ISM_MFG_SVC_RATIO | I2 / I3 |
| I32 | Manufacturers' New Orders YoY | NEWORDER_YOY | I26 YoY change |

---

## Priority Combinations Catalog (73 pairs — human benchmark)

These specific pairs were analyzed manually by the user and found to have meaningful results. Agent team outputs will be compared against these human findings.

### SPY (21 unique pairs)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 1 | SPY | Industrial Production (2017=100) | I1 |
| 2 | SPY | SOFR-US3M (TED Rate) | I17 |
| 3 | SPY | Building Permits | I9 |
| 4 | SPY | US10Y-US3M | I18 |
| 5 | SPY | Michigan Consumer Sentiment | I14 |
| 6 | SPY | New Home Sales (SA) | I10a |
| 7 | SPY | ISM Manufacturing PMI | I2 |
| 8 | SPY | ISM Services PMI | I3 |
| 9 | SPY | PHLX SOX Index | I23 |
| 10 | SPY | Portland Cement Shipments | I8 |
| 11 | SPY | VIX/VIX3M | I22 |
| 12 | SPY | M2SL YoY | I21 |
| 13 | SPY | Unemployment Rate | I4 |
| 14 | SPY | Import Price Index | I24 |
| 15 | SPY | Retail Inventories/Sales | I15 |
| 16 | SPY | Manufacturers' New Orders | I26 |
| 17 | SPY | Credit Card Default | I16 |
| 18 | SPY | Cass Freight Index | I25 |
| 19 | SPY | C&I Loans | I20 |
| 20 | SPY | HY-IG Spread | I19 |
| 21 | SPY | Petroleum Inventory | I27 |

### XLC (1 pair)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 22 | XLC | ISM Mfg/Svc PMI Ratio | I31 |

### XLE (17 pairs)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 23 | XLE | PHLX SOX Index | I23 |
| 24 | XLE | ISM Manufacturing PMI | I2 |
| 25 | XLE | ISM Services PMI | I3 |
| 26 | XLE | Michigan Consumer Sentiment | I14 |
| 27 | XLE | VIX/VIX3M | I22 |
| 28 | XLE | US10Y-US3M (displayed inverted) | I18 |
| 29 | XLE | Import Price Index | I24 |
| 30 | XLE | Job Openings | I6 |
| 31 | XLE | Manufacturers' New Orders | I26 |
| 32 | XLE | Building Permits | I9 |
| 33 | XLE | Housing Starts | I11 |
| 34 | XLE | Petroleum Inventory | I27 |
| 35 | XLE | Crude Oil Price | I28 |
| 36 | XLE | (Electricity-CPI) YoY | I29 |
| 37 | XLE | Wells Fargo Housing Index | I12 |
| 38 | XLE | Architecture Billings Index | I13 |
| 39 | XLE | Cass Freight Index | I25 |

### XLI (10 pairs)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 40 | XLI | ISM Mfg/Svc PMI Ratio | I31 |
| 41 | XLI | Industrial Production (2017=100) | I1 |
| 42 | XLI | Gold/Copper Ratio | I30 |
| 43 | XLI | US10Y-US3M | I18 |
| 44 | XLI | VIX/VIX3M | I22 |
| 45 | XLI | Advanced Retail Sales | I7 |
| 46 | XLI | Import Price Index | I24 |
| 47 | XLI | Job Openings | I6 |
| 48 | XLI | Manufacturers' New Orders | I26 |
| 49 | XLI | Manufacturers' New Orders YoY | I32 |

### XLK (1 pair)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 50 | XLK | Michigan Consumer Sentiment | I14 |

### XLP (12 pairs)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 51 | XLP | Portland Cement Shipments | I8 |
| 52 | XLP | ISM Services PMI | I3 |
| 53 | XLP | Industrial Production (2017=100) | I1 |
| 54 | XLP | ISM Manufacturing PMI | I2 |
| 55 | XLP | SOFR-US3M (TED Rate) | I17 |
| 56 | XLP | Michigan Consumer Sentiment | I14 |
| 57 | XLP | Building Permits | I9 |
| 58 | XLP | VIX/VIX3M | I22 |
| 59 | XLP | US10Y-US3M | I18 |
| 60 | XLP | HY-IG Spread | I19 |
| 61 | XLP | C&I Loans | I20 |
| 62 | XLP | Cass Freight Index | I25 |

### XLY (12 pairs, including SA/NSA distinction)

| # | Target | Indicator | Indicator ID |
|---|--------|-----------|-------------|
| 63 | XLY | Michigan Consumer Sentiment | I14 |
| 64 | XLY | ISM Mfg/Svc PMI Ratio | I31 |
| 65 | XLY | PHLX SOX Index | I23 |
| 66 | XLY | Industrial Production (2017=100) | I1 |
| 67 | XLY | VIX/VIX3M | I22 |
| 68 | XLY | US10Y-US3M | I18 |
| 69 | XLY | Wells Fargo Housing Index | I12 |
| 70 | XLY | New Home Sales (SA) | I10a |
| 71 | XLY | Cass Freight Index | I25 |
| 72 | XLY | New Home Sales (NSA) | I10b |
| 73 | XLY | Manufacturers' New Orders | I26 |
| 74 | XLY | Job Openings | I6 |

**Note:** XLY has 12 unique pairs (74 - 62 = 12). Total across all targets: 74 rows but 73 unique combinations (XLY #70 and #72 are distinct SA vs NSA variants; grand total confirmed at 73 after earlier dedup of SPY Building Permits/Housing Permits and SPY UNRATE/Employment Index).

---

## Backtest Design Implications of Multi-Target Universe

The expanded target universe requires backtest infrastructure changes:

| Target Class | Tickers | Trading Hours | Benchmark | B&H Vol | Special Considerations |
|-------------|---------|---------------|-----------|---------|----------------------|
| Broad equity | SPY | US market | SPY itself | ~15-20% | Baseline |
| Sector ETFs | XLB-XLY (11) | US market | SPY (relative) | 18-35% | Higher vol; sector-specific risk factors |
| Treasury short | SHY | US market | SHY itself | ~2-4% | Very low vol; Sharpe > 1.0 is meaningful |
| Treasury long | TLT, IEF | US market | AGG | 10-18% | Duration risk dominates; rate sensitivity |
| TIPS / Inflation | TIP, VTIP | US market | AGG | 5-8% | Real return focus; inflation breakeven matters |
| IG Corporate | LQD, VCSH | US market | AGG | 5-10% | Credit + duration; spread component |
| HY Corporate | HYG, JNK | US market | HYG itself | 8-15% | Credit risk dominates; equity-like in stress |
| Corporate CEF | PTY | US market | LQD | 10-20% | CEF premium/discount; leverage; illiquidity |
| Aggregate bond | AGG, BND | US market | AGG itself | 4-7% | Broad duration + credit; low turnover expected |
| Senior loan | BKLN | US market | AGG | 3-6% | Floating rate; credit risk; low duration |
| Commodities (individual) | GC, SI, PL, BZ, CL | Extended/24hr | Commodity itself | 15-30% | Roll yield; contango/backwardation |
| Commodities (aggregate) | DBC, GSG, PDBC | US market | DBC itself | 12-20% | Diversified commodity basket; roll effects |
| Crypto | BTC-USD, ETH-USD | 24/7 | BTC or HODL | 50-80% | Short history (BTC ~2014+); extreme tails |

**Key backtest adjustments needed:**
1. **Benchmark selection** — each target class needs its own buy-and-hold benchmark (not SPY for everything)
2. **Risk-free rate** — same SOFR/T-bill for all, but Sharpe interpretation varies (a 0.5 Sharpe on crypto ≠ 0.5 on bonds)
3. **Sample period** — crypto targets have shorter history; commodity futures may have different start dates
4. **Transaction costs** — differ by asset class (equities ~5bps, futures ~2bps, crypto ~10-30bps)
5. **Calendar** — crypto trades 24/7; commodities have extended hours; this affects daily return computation
6. **Tournament metrics** — may need asset-class-adjusted Sharpe thresholds for validity filters

---

## New Analysis Categories (6 additions to Catalog B)

Appended as categories 9-14 (methods #53-95), preserving existing numbering.

| # | Category | ~Methods | Key Packages |
|---|----------|---------|-------------|
| 9 | Cointegration & Equilibrium | 7 | `statsmodels` (coint, VECM, ARDL) |
| 10 | Network & Spillover | 7 | `statsmodels`, `networkx`, `sklearn` |
| 11 | Factor Decomposition | 7 | `sklearn`, `statsmodels`, `factor_analyzer` |
| 12 | Distributional & Higher-Moment | 8 | `statsmodels`, `properscoring` |
| 13 | Forecast Evaluation | 7 | `statsmodels`, `sklearn` |
| 14 | Liquidity & Microstructure | 7 | `numpy`, `pandas` |

**Total:** 52 existing + 43 new = **95 methods across 14 categories**

---

## Relevance Matrix (Appendix to Catalog B)

7 indicator types × 14 categories. Scores: `++` core, `+` useful, `-` low priority, `--` N/A.

| Indicator Type | Corr | Lead-Lag | Regime | TimeSeries | Vol | ML | Signal | Event/Tail | Coint | Network | Factor | Distrib | FcstEval | Liquidity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Credit Spread | ++ | ++ | ++ | ++ | + | + | + | ++ | ++ | + | + | ++ | ++ | - |
| Volatility/Options | ++ | + | ++ | + | ++ | + | + | ++ | - | + | + | ++ | + | + |
| Activity/Survey | + | ++ | + | ++ | - | ++ | + | + | + | + | ++ | + | ++ | - |
| Yield Curve/Rates | + | ++ | + | ++ | - | + | ++ | + | ++ | - | + | + | ++ | - |
| Sentiment/Flow | ++ | + | + | - | + | + | + | + | - | + | ++ | + | + | ++ |
| Cross-Asset | + | + | + | + | + | ++ | + | + | + | ++ | ++ | + | + | + |
| Microstructure | + | - | - | - | ++ | - | + | - | - | + | - | + | - | ++ |

Fallback: Category Selection Heuristic in Evan's SOP (Rules A-D based on stationarity, frequency, type, and uncertainty).

---

## Interpretation Annotations for Portal Storytelling

Different indicator-target pairs may require opposite interpretations of the same signal. The portal must annotate these differences so layman users understand what the indicator means for each specific target.

### The Problem

Consider VIX/VIX3M ratio:
- For **SPY**: Higher ratio → stress → bearish (lower expected returns)
- For **TLT**: Higher ratio → stress → bullish (flight to safety, higher bond prices)
- For **GLD**: Higher ratio → stress → bullish (safe-haven demand)

Without annotation, a layman seeing "VIX/VIX3M is elevated" might assume the same implication for all targets.

### Design Requirements

1. **Interpretation Metadata per Pair** — Each indicator-target analysis run produces interpretation metadata:
   - `direction`: Whether higher indicator values are associated with higher (+1) or lower (-1) target returns
   - `mechanism`: Plain-English explanation of the economic channel (e.g., "Rising credit spreads signal corporate stress, reducing equity returns")
   - `confidence`: Statistical confidence level from the analysis (correlation sign, regime-switching interpretation, lead-lag direction)

2. **Portal Annotation Layer** — The Streamlit portal must:
   - Display a **"How to Read This"** callout box on each pair's page, stating the direction and mechanism
   - When showing cross-pair comparisons, use color-coded direction arrows (green ↑ = "higher indicator is bullish for target", red ↓ = "higher indicator is bearish for target")
   - Include a **"Differs From"** note when the same indicator has opposite interpretations across targets shown on the same dashboard

3. **Analysis Brief Field** — The Analysis Brief template includes an `expected_direction` field with one of:
   - `pro_cyclical` — indicator and target move together
   - `counter_cyclical` — indicator and target move inversely
   - `ambiguous` — direction must be determined empirically (output of the analysis)
   - `conditional` — direction depends on regime (e.g., bullish in expansion, bearish in contraction)

4. **Agent Responsibilities**
   - **Econometrics agent**: Outputs `interpretation_metadata.json` alongside results, with direction, mechanism, and confidence fields
   - **Research agent**: Validates direction against academic literature; flags any contradiction between empirical finding and theoretical expectation
   - **Visualization agent**: Renders direction indicators and mechanism text in chart annotations
   - **App Dev agent**: Implements the annotation layer in portal pages, including cross-pair comparison views

### Implementation in SOPs

- **Step 7 (SOP generalization)** adds interpretation annotation requirements to each agent's SOP
- **Step 1 (Analysis Brief)** adds `expected_direction` field to template
- **Step 3 (Evan's SOP)** adds `interpretation_metadata.json` to output manifest

---

## Cross-Check: HY-IG Gap Coverage

A cross-check of the completed HY-IG × SPY pipeline against the analysis brief found 12 gaps between specified design and actual implementation. The generalized framework must address each.

| Gap ID | Description | Status in HY-IG | Resolution in Generalized Framework |
|--------|------------|-----------------|--------------------------------------|
| G1 | Threshold method T4 (Jenks natural breaks) not implemented | Missing from tournament | **Add to Catalog B** as method in Signal Engineering category; add to tournament grid as T4 |
| G2 | Threshold method T5 (Gaussian Mixture) not implemented | Missing from tournament | **Add to Catalog B**; already covered by new Category 11 (Factor Decomposition) |
| G3 | Threshold method T6 (HMM posterior prob > 0.9) not implemented | Only T4_0.7 used | **Add to tournament grid** as T6_0.9; document in Evan's SOP as alternative threshold |
| G4 | Threshold method T7 (CUSUM) not implemented | Missing | **Add to Catalog B** as method in Category 13 (Forecast Evaluation); add to tournament grid |
| G5 | Strategy P4 (volatility-targeting) not implemented | Only P1-P3 | **Add to tournament strategies**; document vol-targeting formula in Evan's SOP (target vol / realized vol) |
| G6 | Lead times L42, L126, L252 not in tournament | Only L5, L10, L21, L42, L63 used | **Add L126, L252 to tournament grid**; note: L42 was actually used (verify naming) |
| G7 | 3-state HMM not used as tournament signal | Only 2-state | **Add S_HMM3 to signal catalog**; 3 states = expansion/transition/contraction |
| G8 | 3-state Markov switching not used as signal | Missing | **Already covered** by S7 in existing catalog; ensure implementation includes 3-state variant |
| G9 | Lookback window not a separate tournament dimension | Hardcoded per signal | **Add lookback as 5th tournament dimension**: [60, 120, 252] trading days for rolling computations |
| G10 | FSI version mismatch (brief says STLFSI4, code uses STLFSI2) | Inconsistent | **Resolve in Data Series Catalog**: specify STLFSI4 as canonical; add migration note |
| G11 | Reverse causality (LP regression target→indicator) not run | Missing diagnostic | **Add to Evan's SOP** as mandatory diagnostic in Step 4 (post-estimation); flag if significant |
| G12 | KPI data not loaded from JSON (hardcoded in app.py) | Hardcoded | **Add to App Dev SOP**: KPIs must be loaded from `results/kpis.json`; no hardcoded values |

### Coverage in Implementation Steps

- **G1, G2, G4**: Addressed in Step 2 (Extend Econometric Methods Catalog — new methods added)
- **G3, G5, G6, G7, G8, G9**: Addressed in Step 3/8 (Evan's SOP — tournament design expansion)
- **G10**: Addressed in Step 4 (Data Series Catalog — canonical series specification)
- **G11**: Addressed in Step 3 (Evan's SOP — post-estimation diagnostics)
- **G12**: Addressed in Step 7 (App Dev SOP — no hardcoded KPIs)

All 12 gaps are covered. No HY-IG feature is dropped without rationale.

---

## Agent Review Notes

Each implementation step was reviewed from the perspective of the agent whose SOP it affects. Key comments:

### Data Agent (Dana) — Steps 4, 7
- **Naming convention**: New indicators must follow `{canonical_name}` pattern already established (e.g., `hy_oas_bps` → `ism_mfg_pmi`, `vix_vix3m_ratio`). Step 4 must specify canonical column names for all 31 indicators.
- **Frequency alignment**: Mixed-frequency indicators (daily vs monthly vs quarterly) need explicit resampling rules in the Data Series Catalog. Credit Card Default (I16) is quarterly — document how to align with daily targets.
- **Derived series**: ISM ratio (I31) and New Orders YoY (I32) need computation recipes in the catalog, not just "derived from I2/I3."

### Econometrics Agent (Evan) — Steps 2, 3, 8
- **Category Selection Heuristic**: Rules A-D must be unambiguous so two analysts applying them to the same indicator reach the same categories. Include worked examples for each rule.
- **Tournament dimension explosion**: Adding lookback as 5th dimension (G9) and new thresholds (G1-G4) significantly expands the grid. Must add a **computational budget** parameter to the Analysis Brief so runs don't exceed available compute. Suggest: cap at 10,000 players per run with stratified sampling for larger grids.
- **Interpretation metadata**: The `interpretation_metadata.json` output is a new deliverable — add to the manifest schema.

### Visualization Agent (Vince) — Step 7
- **Direction indicators**: Need a consistent visual language for pro-cyclical vs counter-cyclical across all chart types. Suggest: solid line = pro-cyclical, dashed = counter-cyclical, with legend.
- **Multi-pair dashboards**: When comparing the same indicator across multiple targets, charts must show direction annotations inline (not just in separate callout boxes).

### Research Agent (Rita) — Step 7
- **Category recommendation**: Adding a 6th bullet to the spec memo (indicator type + recommended categories from Relevance Matrix) is straightforward. But Rita should also flag when empirical direction contradicts theoretical expectation — add as explicit quality gate.
- **Literature validation**: For the 73 priority pairs, Rita should note whether the indicator-target relationship has established academic support or is exploratory.

### App Dev Agent (Ace) — Step 7
- **Portal parameterization**: `page_title` via config is fine, but the entire page structure should be data-driven from the Analysis Brief — not just the title. Config should include: indicator name, target name, direction annotation, benchmark name.
- **KPI loading (G12)**: Portal must read `results/kpis.json` and fail gracefully if missing, rather than hardcoding fallback values.

### Team Coordinator — Steps 1, 6, 7
- **Phase 0 (Analysis Brief)**: The brief must be a mandatory artifact before any agent starts work. Team coordination SOP should enforce this with a gate check.
- **Acknowledgment protocol**: When the brief is issued, each agent must acknowledge receipt and flag any concerns within their domain before proceeding.
- **Run registry**: Step 6 adds a "Registered Analysis Runs" table to the index — this becomes the single source of truth for which pairs have been analyzed.

---

## Implementation Steps

### Step 1: Create Analysis Brief Template
**File:** `docs/analysis_brief_template.md` (new)
- Parameterized kickoff with {PLACEHOLDER} fields
- Sections: Research Question, Hypotheses, Sample, Data Requirements, Method Classes, Tournament Design, Deliverables, Portal, Quality Standards
- Appendix: link to `docs/analysis_brief_hy_ig_spy_20260228.md` as worked example
- **New:** Tournament Design section includes target-class-specific parameters (benchmark, transaction costs, calendar, sample period constraints)
- **New:** `expected_direction` field (pro_cyclical / counter_cyclical / ambiguous / conditional) for interpretation annotations
- **New:** `computational_budget` field (max tournament players per run, default 10,000)

### Step 2: Extend Econometric Methods Catalog
**File:** `docs/econometric-methods-catalog.md`
- Generalize header to "Multi-Indicator Analysis"
- Add 6 new categories (9-14) with ~43 methods in 7-column format
- Update Summary Statistics table (52→95)
- Update Recommended Prioritization (add Phase 4)
- Add Relevance Matrix appendix

### Step 3: Update Evan's SOP
**File:** `docs/agent-sops/econometrics-agent-sop.md`
- Insert "Step 2.5 — Method Category Selection" (consult Relevance Matrix + heuristic)
- Add Category Selection Heuristic (Rules A-D) with worked examples per rule
- Add second manifest example (PMI-based regime alongside HMM)
- Generalize sanity-check examples (add ISM/VIX/P-C alongside HY OAS)
- **New:** Add target-class-aware backtest parameters section
- **New:** Add `interpretation_metadata.json` to output manifest schema (direction, mechanism, confidence)
- **New:** Add reverse causality LP as mandatory post-estimation diagnostic (G11)
- **New:** Add lookback as 5th tournament dimension [60, 120, 252] (G9)
- **New:** Add 3-state HMM/Markov as signal variants (G7, G8)
- **New:** Add Jenks, GMM, HMM p>0.9, CUSUM to threshold grid (G1-G4)
- **New:** Add vol-targeting strategy P4 (G5)
- **New:** Add computational budget cap with stratified sampling for large grids

### Step 4: Expand Data Series Catalog
**File:** `docs/data-series-catalog.md`
- Generalize header
- Add new sections for the 31 indicators (organized by category)
- Add Tier 2 category-level stubs (6 entries)
- Add derived series with computation recipes (ISM ratio = I2/I3, New Orders YoY = 12-month pct change of I26)
- **New:** Add Target Universe section (35 targets with tickers, class, benchmark, special considerations)
- **New:** Specify canonical column names for all 31 indicators (following existing `{canonical_name}` pattern)
- **New:** Document frequency alignment rules (quarterly I16 → monthly via last-value-carry-forward; daily → monthly via end-of-month)
- **New:** Resolve FSI version: STLFSI4 is canonical; add migration note for STLFSI2 (G10)

### Step 5: Create Priority Combinations Catalog
**File:** `docs/priority-combinations-catalog.md` (new)
- 73 specific indicator × target pairs from user's manual analysis
- Organized by target (SPY, XLC, XLE, XLI, XLK, XLP, XLY)
- Each entry references indicator ID and target ID
- Status column for tracking: Pending | In Progress | Completed | Compared
- Comparison notes column for human vs. agent output assessment

### Step 6: Update Reference Catalogs Index
**File:** `docs/reference-catalogs-index.md`
- Generalize title to "Multi-Indicator Analysis"
- Update counts (methods 52→95, data series expanded, new priority catalog)
- Add Catalog E: Priority Combinations (73 pairs)
- Add "Registered Analysis Runs" table
- Update cross-reference table

### Step 7: Generalize HY-IG References (all SOPs)
**Files:** All 6 SOP files in `docs/agent-sops/`

| File | Changes |
|------|---------|
| team-coordination.md | Parameterize Sharpe/MDD values, W1/HMM refs in reconciliation; add Phase 0 (Analysis Brief) as mandatory gate — no agent starts without brief; add acknowledgment protocol (each agent confirms receipt + domain-specific concerns); add interpretation annotation handoff rules |
| data-agent-sop.md | Add PMI/P-C examples to column naming, sanity checks, derived series |
| econometrics-agent-sop.md | (covered in Step 3) |
| appdev-agent-sop.md | Parameterize page_title via config; add target-class-aware B&H benchmark note; KPIs from JSON not hardcoded (G12); data-driven page structure from Analysis Brief |
| research-agent-sop.md | Add category recommendation to spec memo (6th bullet); add indicator type + categories to quality gates; add direction-vs-theory contradiction flag; note academic support level for priority pairs |
| visualization-agent-sop.md | Generalize "[winner] max drawdown" example; add direction annotation visual language (solid=pro-cyclical, dashed=counter-cyclical); inline annotations on multi-pair dashboards |

### Step 8: Update Backtest Infrastructure SOPs
**File:** `docs/agent-sops/econometrics-agent-sop.md` (combined with Step 3)
- Add target-class parameter table to Tournament Design section
- Document benchmark selection logic per target class
- Document transaction cost assumptions per asset class
- Document calendar/trading hours handling
- Document sample period constraints (crypto shorter than equities)

---

## Execution Batches

| Batch | Steps | Parallel? | Files |
|-------|-------|-----------|-------|
| 1 | Steps 1, 4, 5, 7 (SOP generalizations except Evan) | Yes | analysis_brief_template.md, data-series-catalog.md, priority-combinations-catalog.md, 5 SOP files |
| 2 | Step 2 (econometric catalog — largest) | After batch 1 | econometric-methods-catalog.md |
| 3 | Steps 3 + 8 combined (Evan's SOP — one pass) | After step 2 | econometrics-agent-sop.md |
| 4 | Step 6 (index — needs final counts) | After steps 2 + 4 | reference-catalogs-index.md |

---

## Files Summary

| File | Action | Steps |
|------|--------|-------|
| `docs/analysis_brief_template.md` | **New** | 1 |
| `docs/priority-combinations-catalog.md` | **New** | 5 |
| `docs/econometric-methods-catalog.md` | Major edit (+43 methods, matrix) | 2 |
| `docs/data-series-catalog.md` | Major edit (+targets, +indicators) | 4 |
| `docs/reference-catalogs-index.md` | Edit (counts, new catalog E, runs table) | 6 |
| `docs/agent-sops/econometrics-agent-sop.md` | Edit (category selection, backtest params) | 3, 8 |
| `docs/agent-sops/team-coordination.md` | Edit (Phase 0, parameterize) | 7 |
| `docs/agent-sops/data-agent-sop.md` | Edit (generalize examples) | 7 |
| `docs/agent-sops/appdev-agent-sop.md` | Edit (parameterize, target-class) | 7 |
| `docs/agent-sops/research-agent-sop.md` | Edit (category guidance) | 7 |
| `docs/agent-sops/visualization-agent-sop.md` | Edit (generalize example) | 7 |

**Total: 9 files modified, 2 files created.**

---

## Verification

1. `grep -r "Credit Spread / Equity Prediction" docs/` → 0 hits in catalog headers
2. `grep -c "Relevance Matrix" docs/econometric-methods-catalog.md` → appendix exists
3. `grep -c "Analysis Brief" docs/agent-sops/team-coordination.md` → Phase 0 exists
4. Count methods in econometric catalog → ~95
5. Count entries in data series catalog → expanded with all 31 indicators + 35 targets
6. Count entries in priority combinations catalog → 73
7. All SOPs: no un-parameterized HY-IG-specific values (all say "Example" or reference Analysis Brief)
8. `grep -c "interpretation_metadata" docs/agent-sops/econometrics-agent-sop.md` → manifest entry exists
9. `grep -c "expected_direction" docs/analysis_brief_template.md` → field exists
10. All 12 HY-IG gaps (G1-G12) traceable to specific implementation steps
11. `grep -c "acknowledgment" docs/agent-sops/team-coordination.md` → protocol exists
12. Commit and push
