# Data Series Catalog
## Multi-Indicator Analysis Framework — Reference Appendix

Below is a structured inventory of data series, indicators, and targets used across the multi-indicator analysis framework. Sections 1-6 catalog the 63 candidate series from the original credit-spread/equity research. Sections 7-10 extend coverage to the full indicator universe (31 indicators), target universe (35 targets), frequency alignment rules, and FSI version resolution.

---

## 1. Credit Market Indicators

| # | Series | Description | Predictive Rationale | Source (Code/Ticker) | Frequency |
|---|--------|-------------|---------------------|----------------------|-----------|
| 1 | **ICE BofA US HY OAS** | Option-adjusted spread on the broad US high-yield index | Baseline measure of credit risk pricing; widens before equity drawdowns | FRED: `BAMLH0A0HYM2` | Daily |
| 2 | **ICE BofA US IG OAS** | OAS on US investment-grade corporate bonds | Captures stress migrating from HY to IG; regime-change signal | FRED: `BAMLC0A0CM` | Daily |
| 3 | **ICE BofA BB HY OAS** | OAS on BB-rated high yield bonds | "Cross-over" credit — first to react at turning points | FRED: `BAMLH0A1HYBB` | Daily |
| 4 | **ICE BofA CCC & Lower OAS** | OAS on CCC-and-below-rated bonds | Extreme distress indicator; non-linear relationship with equity risk | FRED: `BAMLH0A3HYC` | Daily |
| 5 | **ICE BofA Single-B OAS** | OAS on B-rated high yield | Middle-of-the-capital-structure stress barometer | FRED: `BAMLH0A2HYB` | Daily |
| 6 | **ICE BofA AAA Corporate OAS** | OAS on AAA-rated corporates | Flight-to-quality within corporates; widening signals broad de-risking | FRED: `BAMLC0A1CAAA` | Daily |
| 7 | **ICE BofA BBB Corporate OAS** | OAS on BBB-rated (lowest IG) corporates | "Fallen angel" risk — widening here precedes downgrades and equity weakness | FRED: `BAMLC0A4CBBB` | Daily |
| 8 | **CDX.NA.IG 5Y** | CDS index on 125 North American IG names | Liquid, real-time credit risk pricing; leads cash bond spreads | Bloomberg: `CDX.NA.IG` / Markit | Daily |
| 9 | **CDX.NA.HY 5Y** | CDS index on North American HY names | Synthetic HY risk; often moves before cash spreads | Bloomberg: `CDX.NA.HY` / Markit | Daily |
| 10 | **Excess Bond Premium (EBP)** | Gilchrist-Zakrajsek decomposition: credit spread minus expected default component | Captures investor risk appetite/sentiment in bond markets; strong recession predictor ([Gilchrist & Zakrajsek, 2012](https://www.aeaweb.org/articles?id=10.1257/aer.102.4.1692)) | [Fed FEDS Notes](https://www.federalreserve.gov/econres/notes/feds-notes/updating-the-recession-risk-and-the-excess-bond-premium-20161006.html) | Monthly |
| 11 | **ICE BofA EM Corporate Plus OAS** | OAS on emerging market corporate bonds | Global risk appetite proxy; EM stress spills into US equities | FRED: `BAMLEMCBPIOAS` | Daily |
| 12 | **SLOOS: C&I Loan Tightening (Large Firms)** | Net % of banks tightening standards on commercial & industrial loans | Credit availability leading indicator; tightening precedes earnings weakness | FRED: `DRTSCILM` | Quarterly |

---

## 2. Equity Market / Volatility Indicators

| # | Series | Description | Predictive Rationale | Source (Code/Ticker) | Frequency |
|---|--------|-------------|---------------------|----------------------|-----------|
| 13 | **CBOE VIX** | 30-day implied volatility of S&P 500 options | Fear gauge; mean-reverting, extreme levels signal buying/selling opportunities | FRED: `VIXCLS` / Yahoo: `^VIX` | Daily |
| 14 | **CBOE VIX9D** | 9-day implied volatility | Short-term fear; VIX9D/VIX ratio captures term structure inversion | Yahoo: `^VIX9D` | Daily |
| 15 | **VIX Term Structure (VIX-VIX3M)** | Spread between 30-day and 3-month VIX | Inverted term structure (backwardation) signals acute stress | Yahoo: `^VIX`, `^VIX3M` | Daily |
| 16 | **CBOE SKEW Index** | Measures perceived tail risk (probability of 2+ sigma downside move) | High SKEW = market pricing crash risk even when VIX is low | Yahoo: `^SKEW` | Daily |
| 17 | **CBOE Put/Call Ratio (Total)** | Ratio of put volume to call volume across all CBOE options | Sentiment contrarian indicator; extreme readings signal reversals | [CBOE Daily Statistics](https://www.cboe.com/us/options/market_statistics/daily/) | Daily |
| 18 | **CBOE Equity Put/Call Ratio** | Put/call ratio for equity options only (excludes index options) | Purer measure of retail sentiment vs. index hedging | CBOE / ycharts | Daily |
| 19 | **S&P 500 Advance-Decline Line** | Cumulative net advances minus declines among S&P 500 constituents | Breadth divergence from price is a classic topping signal | StockCharts / TrendSpider | Daily |
| 20 | **% of S&P 500 Above 200-Day MA** | Breadth measure of trend participation | Below 50% signals deteriorating internals even if index is near highs | TrendSpider: `$MA200SP500` | Daily |
| 21 | **% of S&P 500 Above 50-Day MA** | Short-term breadth measure | Rapid drops signal momentum deterioration | TrendSpider: `$MA50SP500` | Daily |
| 22 | **KBW Bank Index / KBE ETF** | Performance of US bank equities | Banks are credit-sensitive; bank equity weakness leads broad equity weakness | Yahoo: `^BKX` / `KBE` | Daily |
| 23 | **XLF (Financial Select Sector SPDR)** | Broader financial sector performance | Financials lead the cycle; underperformance relative to SPY is a warning | Yahoo: `XLF` | Daily |
| 24 | **Russell 2000 / IWM** | Small-cap equity performance | Small caps are more credit-sensitive; RUT/SPX ratio captures risk appetite | Yahoo: `^RUT` / `IWM` | Daily |

---

## 3. Macro / Financial Conditions

| # | Series | Description | Predictive Rationale | Source (Code/Ticker) | Frequency |
|---|--------|-------------|---------------------|----------------------|-----------|
| 25 | **Chicago Fed NFCI** | Weighted average of 105 financial activity measures (money markets, debt, equity, banking) | Comprehensive financial conditions gauge; positive = tighter-than-average conditions ([Chicago Fed](https://www.chicagofed.org/research/data/nfci/current-data)) | FRED: `NFCI` | Weekly |
| 26 | **Chicago Fed Adjusted NFCI** | NFCI adjusted for current economic conditions | Isolates financial stress from the business cycle; better forward-looking signal | FRED: `ANFCI` | Weekly |
| 27 | **St. Louis Fed Financial Stress Index** | 18-variable stress index including rates, spreads, and volatility | Alternative stress composite; uses SOFR-based yield spreads post-LIBOR | FRED: `STLFSI4` | Weekly |
| 28 | **OFR Financial Stress Index** | Office of Financial Research composite stress measure | Focuses on systemic risk and financial stability ([OFR](https://www.financialresearch.gov/financial-stress-index/)) | OFR website | Daily |
| 29 | **10Y-2Y Treasury Spread** | Yield curve slope: 10-year minus 2-year Treasury yield | Classic recession predictor; inversion preceded every recession since 1970s | FRED: `T10Y2Y` | Daily |
| 30 | **10Y-3M Treasury Spread** | Yield curve slope: 10-year minus 3-month Treasury yield | NY Fed's preferred recession probability input; stronger predictor than 10Y-2Y ([NY Fed](https://www.newyorkfed.org/research/capital_markets/ycfaq)) | FRED: `T10Y3M` | Daily |
| 31 | **Fed Funds Rate** | Target federal funds rate (upper bound) | Monetary policy stance; rate hiking cycles eventually cause equity stress | FRED: `DFEDTARU` | Daily |
| 32 | **10Y Breakeven Inflation Rate** | Market-implied expected inflation over 10 years (nominal - TIPS yield) | Rising breakevens signal reflation; falling = deflation risk, bad for equities | FRED: `T10YIE` | Daily |
| 33 | **5Y Breakeven Inflation Rate** | Medium-term inflation expectations | More sensitive to near-term policy shocks than 10Y | FRED: `T5YIE` | Daily |
| 34 | **5Y5Y Forward Inflation Expectation** | Market's inflation expectation for 5 years, 5 years from now | "Anchored" inflation proxy; de-anchoring is a tail risk signal | FRED: `T5YIFR` | Daily |
| 35 | **Initial Jobless Claims** | Weekly new unemployment insurance claims | High-frequency labor market leading indicator; rising claims precede earnings weakness | FRED: `ICSA` | Weekly |
| 36 | **Conference Board LEI** | Composite Leading Economic Index (10 components) | Designed to predict business cycle turning points 7 months ahead | Conference Board / FRED: `USALOLITONOSTSAM` | Monthly |
| 37 | **ISM Manufacturing PMI** | Purchasing Managers' Index for manufacturing sector | Below 50 = contraction; leads industrial earnings and S&P 500 | FRED: `MANEMP` (employment component) / ISM direct | Monthly |

---

## 4. Risk Appetite / Sentiment / Funding Stress

| # | Series | Description | Predictive Rationale | Source (Code/Ticker) | Frequency |
|---|--------|-------------|---------------------|----------------------|-----------|
| 38 | **ICE BofAML MOVE Index** | Implied volatility of US Treasury options | Bond market fear gauge; MOVE spikes precede credit and equity stress | Yahoo: `^MOVE` | Daily |
| 39 | **TED Spread (legacy)** | 3M LIBOR minus 3M T-bill rate | Classic interbank funding stress indicator (discontinued Jan 2022, but historical data useful for backtests) | FRED: `TEDRATE` (discontinued) | Daily |
| 40 | **SOFR** | Secured Overnight Financing Rate | Post-LIBOR funding rate; SOFR spikes indicate repo market stress | FRED: `SOFR` | Daily |
| 41 | **SOFR-Fed Funds Spread** | Difference between SOFR and effective fed funds rate | Repo market stress indicator; replaces TED spread conceptually | Computed from FRED: `SOFR` - `EFFR` | Daily |
| 42 | **CNN Fear & Greed Index** | Composite of 7 market indicators (VIX, momentum, breadth, junk bond demand, etc.) | Sentiment contrarian indicator; extreme greed signals complacency | [CNN Markets](https://www.cnn.com/markets/fear-and-greed) | Daily |
| 43 | **Fed Equity Market Volatility Tracker** | Text-based measure of equity market uncertainty from newspaper coverage | Captures policy-driven uncertainty that options markets may not fully price | FRED: `EMVOVERALLEMV` | Monthly |
| 44 | **US Dollar Index (DXY / Broad)** | Trade-weighted value of USD vs. major currencies | Strong dollar tightens global financial conditions; hurts EM and US multinationals | FRED: `DTWEXBGS` (Broad) / Yahoo: `DX-Y.NYB` | Daily/Weekly |

---

## 5. Alternative Asset Class Signals

| # | Series | Description | Predictive Rationale | Source (Code/Ticker) | Frequency |
|---|--------|-------------|---------------------|----------------------|-----------|
| 45 | **Gold (GLD / GC=F)** | Spot gold price | Safe-haven demand proxy; gold/SPY ratio captures risk-off flows | Yahoo: `GC=F` / `GLD` | Daily |
| 46 | **Copper (HG=F)** | Spot copper price | "Dr. Copper" — economic growth proxy; copper weakness precedes equity weakness | Yahoo: `HG=F` / `CPER` | Daily |
| 47 | **Copper/Gold Ratio** | Ratio of copper to gold prices | Proxy for growth expectations vs. safety demand; ~0.85 correlation with 10Y yields ([CFA Institute](https://blogs.cfainstitute.org/investor/2023/03/16/is-the-copper-gold-ratio-a-leading-indicator-on-rates/)) | Computed from Yahoo: `HG=F` / `GC=F` | Daily |
| 48 | **WTI Crude Oil** | Front-month WTI crude oil futures | Energy prices affect consumer spending and corporate costs; sharp drops signal demand destruction | Yahoo: `CL=F` / FRED: `DCOILWTICO` | Daily |
| 49 | **ICE BofA EM Sovereign OAS** | Emerging market sovereign credit spread | EM stress is a leading indicator for global risk appetite and US equity risk | FRED: `BAMLEMHBHYCRPIOAS` | Daily |
| 50 | **EMBI+ Spread** | JP Morgan Emerging Market Bond Index spread | Classic EM risk gauge; widening signals global flight from risk | Bloomberg / JP Morgan | Daily |

---

## 6. Derived / Computed Series

These are not raw data but transformations that extract signal from the base series above.

| # | Derived Series | Computation | Predictive Rationale | Base Input(s) |
|---|---------------|-------------|---------------------|---------------|
| 51 | **HY-IG Spread Z-Score** | (Current spread - rolling mean) / rolling stdev, e.g., 1Y or 2Y window | Normalizes for regime; Z > 2 signals extreme stress, Z < -1 signals complacency | `BAMLH0A0HYM2` - `BAMLC0A0CM` |
| 52 | **HY Spread Rate of Change** | % change in HY OAS over 1M, 3M, 6M windows | Momentum of credit deterioration matters more than level | `BAMLH0A0HYM2` |
| 53 | **CCC-BB Spread** | CCC OAS minus BB OAS ("quality spread within HY") | Captures dispersion in HY; widening = market differentiating distress | `BAMLH0A3HYC` - `BAMLH0A1HYBB` |
| 54 | **VIX / MOVE Ratio** | VIX divided by MOVE index | Equity vs. bond fear relative pricing; divergence signals cross-asset dislocation | `^VIX` / `^MOVE` |
| 55 | **VIX Term Structure Slope** | VIX3M - VIX (or VIX - VIX9D) | Backwardation (negative slope) = acute near-term stress; contango = complacency | `^VIX3M` - `^VIX` |
| 56 | **Yield Curve Momentum** | 1M or 3M change in 10Y-2Y spread | Rate of flattening/steepening captures policy regime shifts | `T10Y2Y` |
| 57 | **Credit Spread Rolling Volatility** | 21-day or 63-day realized vol of daily spread changes | Spread volatility rises before spread level does; early warning signal | `BAMLH0A0HYM2` |
| 58 | **Credit Spread Percentile Rank** | Rolling percentile rank of HY OAS vs. trailing 2Y or 5Y | Non-parametric regime indicator; >90th pct = stress regime, <10th = complacent | `BAMLH0A0HYM2` |
| 59 | **NFCI Momentum** | 4-week change in NFCI | Captures rate of tightening; fast tightening is more bearish than gradual | `NFCI` |
| 60 | **Bank Equity Relative Strength** | KBE / SPY ratio, 20-day or 60-day rate of change | Banks underperforming = credit cycle turning; leads broad equity by weeks | `KBE` / `SPY` |
| 61 | **Small Cap Relative Strength** | IWM / SPY ratio | Small caps more leveraged and credit-sensitive; deterioration leads SPX | `IWM` / `SPY` |
| 62 | **Real Rate (10Y TIPS Yield)** | 10Y Treasury yield minus 10Y breakeven inflation | Real rate = opportunity cost of holding equities; rising real rates compress valuations | FRED: `DFII10` |
| 63 | **Spread-Volatility Regime** | Binary or categorical: e.g., HY Z-score > 1 AND VIX > 20 = "stress regime" | Combines credit and equity signals into a regime classifier | Multiple |

---

## 7. Indicator Universe (31 Indicators)

This section catalogs the 31 indicators used in the multi-indicator analysis framework. Each indicator has a canonical column name for consistent use across pipelines, models, and visualizations.

### 7.1 Macro / Activity (7 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I1 | Industrial Production Total Index (2017=100) | `indpro` | FRED: INDPRO | Monthly | Index level, SA |
| I2 | ISM Manufacturing PMI | `ism_mfg_pmi` | ISM direct | Monthly | Diffusion index, 50 = neutral |
| I3 | ISM Services PMI | `ism_svc_pmi` | ISM direct | Monthly | Diffusion index, 50 = neutral |
| I4 | Unemployment Rate | `unrate` | FRED: UNRATE | Monthly | Percent, SA |
| I6 | Job Openings (JOLTS) | `jtsjol` | FRED: JTSJOL | Monthly | Thousands, SA |
| I7 | Advanced Retail Sales | `rsafs` | FRED: RSAFS | Monthly | Millions of dollars, SA |
| I8 | Portland Cement Shipments | `cement_ship` | Portland Cement Assoc. | Monthly | Physical volume, proprietary source |

### 7.2 Housing / Construction (5 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I9 | Building/Housing Permits | `permit` | FRED: PERMIT | Monthly | Thousands, SA |
| I10a | New Home Sales (SA) | `hsn1f` | FRED: HSN1F | Monthly | Thousands, SA |
| I10b | New Home Sales (NSA) | `hsn1fnsa` | FRED: HSN1FNSA | Monthly | Thousands, NSA — distinct from I10a |
| I11 | Housing Starts | `houst` | FRED: HOUST | Monthly | Thousands, SA |
| I12 | NAHB/Wells Fargo Housing Market Index | `nahb_hmi` | FRED: NAHBHMI | Monthly | Diffusion index, 50 = neutral |
| I13 | Architecture Billings Index | `abi` | AIA (subscription/scrape) | Monthly | Diffusion index; availability risk |

### 7.3 Consumer / Sentiment (3 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I14 | Michigan Consumer Sentiment | `umcsent` | FRED: UMCSENT | Monthly | Index (1966 Q1 = 100) |
| I15 | Retail Inventories/Sales Ratio | `retailirsa` | FRED: RETAILIRSA | Monthly | Ratio, SA |
| I16 | Credit Card Default Rate | `cc_default` | FRED: DRCCLACBS | Quarterly | Percent; see frequency alignment note |

### 7.4 Financial / Monetary (4 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I17 | SOFR-US3M (TED Rate proxy) | `sofr_us3m` | Computed: FRED SOFR - TB3MS | Daily | Basis points; post-LIBOR TED proxy |
| I18 | US10Y-US3M (Yield Curve Slope) | `t10y3m` | FRED: T10Y3M | Daily | Percentage points |
| I19 | HY-IG Credit Spread | `hy_ig_oas` | Computed: FRED BAMLH0A0HYM2 - BAMLC0A0CM | Daily | Basis points |
| I20 | Commercial & Industrial Loans | `busloans` | FRED: BUSLOANS | Monthly | Billions of dollars, SA |

### 7.5 Monetary Supply (1 indicator)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I21 | M2 Money Supply YoY | `m2sl_yoy` | Derived: FRED M2SL, YoY % change | Monthly | Percent; compute as pct_change(12) |

### 7.6 Volatility / Market (2 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I22 | VIX/VIX3M (Term Structure Ratio) | `vix_vix3m` | Computed: Yahoo ^VIX / ^VIX3M | Daily | Ratio; >1 = backwardation (stress) |
| I23 | PHLX Semiconductor Index (SOX) | `sox` | Yahoo: ^SOX | Daily | Index level |

### 7.7 Trade / Transport (3 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I24 | Import Price Index | `imp_price` | FRED: IR | Monthly | Index (2000=100) |
| I25 | Cass Freight Index (Shipments) | `cass_freight` | Cass Information Systems | Monthly | Index; proprietary but published |
| I26 | Manufacturers' New Orders | `neworder` | FRED: NEWORDER | Monthly | Millions of dollars, SA |

### 7.8 Energy (3 indicators)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I27 | Petroleum Inventory | `petrol_inv` | EIA weekly data | Weekly | Thousands of barrels |
| I28 | Crude Oil Price (WTI) | `cl_f` | Yahoo: CL=F | Daily | USD/barrel; front-month futures |
| I29 | (Electricity Price - CPI) YoY | `elec_cpi_yoy` | Derived: BLS electricity CPI component | Monthly | Percent; real electricity cost proxy |

### 7.9 Cross-Asset (1 indicator)

| ID | Indicator | Canonical Name | Source | Freq | Notes |
|----|-----------|---------------|--------|------|-------|
| I30 | Gold/Copper Ratio | `gold_copper` | Computed: GC=F / HG=F | Daily | Ratio; higher = risk-off |

### 7.10 Derived Ratios (2 indicators)

| ID | Indicator | Canonical Name | Derived From | Computation |
|----|-----------|---------------|-------------|-------------|
| I31 | ISM Mfg PMI / ISM Svc PMI Ratio | `ism_mfg_svc_ratio` | I2 / I3 | `ism_mfg_pmi / ism_svc_pmi`; >1 = manufacturing stronger |
| I32 | Manufacturers' New Orders YoY | `neworder_yoy` | I26 YoY change | `neworder.pct_change(12) * 100`; percent |

---

## 8. Target Universe (35 Targets)

This section catalogs the 35 targets used in the multi-indicator analysis framework, organized by asset class. Each target is an investable security or index against which indicator-based models generate signals.

### 8.1 Broad Equity (1)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T1 | S&P 500 | SPY | Broad Equity | SPY itself | Baseline; ~15-20% annualized vol |

### 8.2 Sector ETFs — SPDR Select Sector (11)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T2 | Communication Services | XLC | Sector | SPY (relative) | Higher vol (18-35%); sector-specific risk factors |
| T3 | Energy | XLE | Sector | SPY (relative) | Higher vol (18-35%); commodity-linked |
| T4 | Industrials | XLI | Sector | SPY (relative) | Higher vol (18-35%); cyclical exposure |
| T5 | Technology | XLK | Sector | SPY (relative) | Higher vol (18-35%); growth/momentum factor |
| T6 | Consumer Staples | XLP | Sector | SPY (relative) | Lower vol; defensive sector |
| T7 | Consumer Discretionary | XLY | Sector | SPY (relative) | Higher vol (18-35%); consumer sentiment sensitive |
| T8 | Materials | XLB | Sector | SPY (relative) | Higher vol (18-35%); commodity-linked |
| T9 | Financials | XLF | Sector | SPY (relative) | Higher vol (18-35%); credit-cycle sensitive |
| T10 | Real Estate | XLRE | Sector | SPY (relative) | Higher vol (18-35%); rate-sensitive |
| T11 | Utilities | XLU | Sector | SPY (relative) | Lower vol; rate-sensitive defensive |
| T12 | Health Care | XLV | Sector | SPY (relative) | Moderate vol; defensive with policy risk |

### 8.3 Fixed Income — Treasury by Duration (3)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T13 | 1-3 Year Treasury | SHY | Treasury | SHY | Low duration; minimal interest rate risk |
| T14 | 7-10 Year Treasury | IEF | Treasury | AGG | Moderate duration risk; rate-cycle sensitive |
| T15 | 20+ Year Treasury | TLT | Treasury | AGG | High duration risk; very different vol profile from SHY |

### 8.4 Fixed Income — Inflation-Protected (2)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T16 | TIPS Bond ETF | TIP | Inflation-Protected | AGG | Real return focus; inflation breakeven exposure |
| T17 | Short-Term TIPS ETF | VTIP | Inflation-Protected | AGG | Short duration TIPS; lower rate sensitivity |

### 8.5 Fixed Income — Corporate (5)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T18 | Investment Grade Corporate Bond | LQD | Corporate IG | AGG | Credit + duration risk |
| T19 | Short-Term Corporate Bond | VCSH | Corporate IG | AGG | Lower duration; credit-focused |
| T20 | High Yield Corporate Bond | HYG | Corporate HY | HYG | Credit risk dominant; equity-like in stress |
| T21 | High Yield Bond (SPDR) | JNK | Corporate HY | HYG | Similar to HYG; slightly different index methodology |
| T22 | PIMCO Corporate & Income Opportunity | PTY | Corporate CEF | LQD | CEF premium/discount dynamics; leveraged |

### 8.6 Fixed Income — Aggregate (2)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T23 | US Aggregate Bond | AGG | Aggregate | AGG itself | Broad duration + credit; low turnover expected |
| T24 | Total Bond Market | BND | Aggregate | AGG | Near-identical to AGG; Vanguard wrapper |

### 8.7 Commodities — Individual (5)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T25 | Gold | GC=F / GLD | Commodity | Self | Roll yield; safe-haven; extended hours |
| T26 | Silver | SI=F / SLV | Commodity | Self | Roll yield; higher vol than gold; industrial demand |
| T27 | Platinum | PL=F / PPLT | Commodity | Self | Roll yield; auto-catalyst demand; thin liquidity |
| T28 | Brent Crude | BZ=F | Commodity | Self | Roll yield; contango/backwardation; geopolitical risk |
| T29 | WTI Crude | CL=F | Commodity | Self | Roll yield; contango/backwardo; US production sensitive |

### 8.8 Commodities — Aggregate (3)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T30 | Commodity Index Tracking Fund | DBC | Commodity Basket | DBC itself | Diversified basket; roll effects across sectors |
| T31 | S&P GSCI Commodity ETF | GSG | Commodity Basket | DBC | Energy-heavy weighting; different roll methodology |
| T32 | Optimum Yield Diversified Commodity | PDBC | Commodity Basket | DBC | Active roll optimization; K-1 tax treatment |

### 8.9 Crypto (2)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T33 | Bitcoin | BTC-USD | Crypto | BTC or HODL | Short history (BTC ~2014+); extreme tails (50-80% vol); 24/7 trading |
| T34 | Ethereum | ETH-USD | Crypto | BTC or HODL | Shorter history than BTC; higher vol; smart-contract ecosystem |

### 8.10 Senior Loans (1)

| ID | Target | Ticker | Class | Benchmark | Special Considerations |
|----|--------|--------|-------|-----------|----------------------|
| T35 | Senior Loan ETF | BKLN | Senior Loan | AGG | Floating rate; credit risk; low duration |

---

## 9. Frequency Alignment Rules

Multi-indicator analysis requires combining series at different native frequencies. The table below defines the canonical alignment methods used across all pipelines.

| Source Freq | Target Freq | Method | Notes |
|-------------|-------------|--------|-------|
| Daily -> Monthly | End-of-month value | Use last business day of month | Default for daily indicators paired with monthly targets |
| Weekly -> Monthly | End-of-month value | Use last weekly observation in the month | |
| Monthly -> Daily | Last-value carry-forward | Carry the monthly value until next release | Creates step function; document in data dictionary |
| Quarterly -> Monthly | Last-value carry-forward | Carry quarterly value for 3 months | I16 (Credit Card Default) uses this method |
| Weekly -> Daily | Last-value carry-forward | Carry until next weekly release | I27 (Petroleum Inventory) uses this method |

**Key implementation notes:**

- When aligning to monthly frequency, always use **end-of-month** convention (last business day) to avoid look-ahead bias.
- Carry-forward methods introduce staleness. Models should account for this by including a **days-since-release** feature or by weighting more recent observations higher.
- For quarterly series (e.g., I16 Credit Card Default Rate from FRED: DRCCLACBS), the value is carried forward for 3 months. Consider flagging the first month after release as "fresh" vs. months 2-3 as "stale."

---

## 10. FSI Version Resolution

The St. Louis Fed Financial Stress Index has undergone a significant methodology change tied to the LIBOR-to-SOFR transition.

| Version | FRED Code | Basis Rate | Status | Period |
|---------|-----------|-----------|--------|--------|
| **Canonical** | `STLFSI4` | SOFR-based | Active, current | 2022-present (backfilled) |
| **Legacy** | `STLFSI2` | LIBOR-based | Discontinued | Pre-2022 |

**Migration note:** Any existing code referencing `STLFSI2` should be updated to `STLFSI4`. The two series are not directly comparable due to the SOFR-LIBOR basis difference. For backtesting prior to 2022, use `STLFSI4` which the St. Louis Fed has backfilled using reconstructed SOFR-based inputs.

---

## Implementation Notes

**Highest-priority additions** (easiest to source, strongest academic backing):

1. **CCC-BB quality spread** (#53) — captures the non-linear risk within HY that the simple HY-IG spread misses
2. **NFCI** (#25) — the single best composite financial conditions measure, weekly frequency, on FRED
3. **10Y-3M yield curve** (#30) — stronger recession predictor than 10Y-2Y per NY Fed research
4. **VIX term structure** (#55) — backwardation is one of the most reliable short-term equity stress signals
5. **Excess Bond Premium** (#10) — Gilchrist-Zakrajsek's EBP has the strongest academic evidence for predicting both GDP and equity returns
6. **Initial Claims** (#35) — weekly, timely, and a proven leading indicator of labor market and earnings risk
7. **Bank equity relative strength** (#60) — simple, daily, and captures the credit-equity feedback loop

**Expanded indicator universe:** The 31 indicators in Section 7 are the curated set for the multi-indicator analysis framework. They span macro/activity, housing, consumer sentiment, financial/monetary, volatility, trade/transport, energy, cross-asset, and derived ratio categories. Canonical column names ensure consistent naming across all data pipelines, models, and visualizations.

**Target universe:** The 35 targets in Section 8 cover broad equity, sector ETFs, fixed income (Treasury, inflation-protected, corporate, aggregate), commodities (individual and basket), crypto, and senior loans. Each target has a designated benchmark for relative performance evaluation.

**Priority combinations:** See the Priority Combinations Catalog (`docs/priority-combinations-catalog.md`) for the 73 human-analyzed indicator-target pairs that form the core of the multi-indicator framework.

**Data access priorities:**
- FRED API covers ~35 of the 50 base series (free, reliable, programmatic via `fredapi`)
- Yahoo Finance via `yfinance` covers equity/ETF tickers, VIX, MOVE, SKEW, commodities
- Alpha Vantage MCP covers additional market data and technical indicators
- CDX/iTraxx indices require Bloomberg or Markit (institutional access) — consider using the HY/IG OAS series from FRED as proxies

**Key academic references:**
- [Gilchrist & Zakrajsek (2012)](https://www.aeaweb.org/articles?id=10.1257/aer.102.4.1692) — Credit spreads and business cycle fluctuations
- [NY Fed Yield Curve as Leading Indicator](https://www.newyorkfed.org/research/capital_markets/ycfaq) — Term spread recession probability model
- [CME Group (2025) — Are Tight Credit Spreads Underpricing Risk?](https://www.cmegroup.com/insights/economic-research/2025/are-extremely-tight-us-credit-spreads-underpricing-risk.html)
- [State Street (2025) — Credit Spreads Signal Confidence and Risk](https://www.ssga.com/us/en/institutional/insights/mind-on-the-market-24-november-2025)
- [RIA — Credit Spreads: The Market's Early Warning Indicators](https://realinvestmentadvice.com/resources/blog/credit-spreads-the-markets-early-warning-indicators/)
---
*Generated: 2026-02-28 | Last updated: 2026-03-14*
*Source: Web research across academic papers, institutional research, and quant finance literature*
*Status: Reference catalog — multi-indicator analysis framework with 63 candidate series, 31 curated indicators, and 35 investable targets*
