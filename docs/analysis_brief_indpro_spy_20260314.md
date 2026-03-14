# Analysis Brief: Industrial Production → S&P 500

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | 2026-03-14                |
| **Author**  | Alex (Lead Analyst)       |
| **Version** | 1.0                       |
| **Status**  | Approved                  |

---

## 1. Research Question

**Question:** Does US Industrial Production predict S&P 500 equity returns? If so, through what mechanism, at what horizons, and can it be profitably traded?

### Hypotheses

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H₀ | Industrial Production has no predictive power for SPY returns at any horizon | Granger causality (Toda-Yamamoto), transfer entropy |
| H₁ | Rising IP predicts positive SPY returns with a lag of 1-3 months (pro-cyclical channel) | Local projections (Jorda), predictive regressions |
| H₂ | IP regime changes (expansion → contraction) predict equity drawdowns | Markov-switching regression, HMM, change-point detection |
| H₃ | The IP-SPY relationship is nonlinear — stronger during recessions than expansions | Quantile regression, regime-dependent local projections |

---

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | Industrial Production Index (2017=100) |
| **ID** | indpro |
| **Canonical name** | Industrial Production: Total Index (INDPRO) |
| **Source** | FRED: `INDPRO` |
| **Frequency** | Monthly |
| **Transformation** | Level, YoY % change, MoM % change, 12-month moving average |
| **Indicator type** | Activity / Survey |

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
| **Expected direction** | pro_cyclical |
| **Mechanism** | Rising industrial production reflects expanding manufacturing activity, higher capacity utilization, and growing corporate earnings. This supports equity valuations through both the earnings channel (higher revenues for industrials, materials, and consumer sectors) and the macro confidence channel (rising IP reduces recession probability, encouraging risk-taking). The effect operates with a lag because IP data is released with a ~6-week delay and markets may not fully price the signal immediately. |
| **Literature support** | Strong |

**Literature references:**
- Stock & Watson (1989, 2003): IP is a core component of the Coincident Economic Index and leading indicators
- Fama & French (1989): Business conditions (including IP) predict stock returns
- Chen, Roll & Ross (1986): IP growth is a priced factor in the APT framework
- Schwert (1990): Stock volatility related to macroeconomic volatility including IP

---

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample period** | 1990-01-01 to 2025-12-31 |
| **In-sample (IS)** | 1990-01-01 to 2017-12-31 |
| **Out-of-sample (OOS)** | 2018-01-01 to 2025-12-31 |
| **Minimum sample constraint** | 15 years |
| **Frequency** | Monthly (indicator native); Daily (target native); analysis at both frequencies |
| **Approximate IS observations** | 336 months / ~7,056 trading days |
| **Approximate OOS observations** | 96 months / ~2,016 trading days |

**Known limitations:**
- INDPRO is released monthly with ~6-week lag (e.g., January data available mid-March). The pipeline must account for publication lag to avoid look-ahead bias.
- COVID-19 caused an unprecedented 12.7% MoM drop in April 2020, followed by a sharp recovery. This structural break must be handled (winsorize or dummy).
- INDPRO includes revisions; real-time vs. revised data may differ. We use revised (latest vintage) data.
- Pre-2000 INDPRO methodology differs slightly (base year changes).

---

## 6. Data Requirements

### 6.1 Core and Secondary Series

| # | Variable | Preferred Name | Source | Frequency | Transform | Stationarity Test | Priority |
|---|----------|---------------|--------|-----------|-----------|-------------------|----------|
| 1 | Industrial Production Index | indpro | FRED: INDPRO | Monthly | Level | ADF + KPSS | Core |
| 2 | SPY (S&P 500 ETF) | spy | Yahoo: SPY | Daily | Level (adj close) | ADF + KPSS | Core |
| 3 | VIX | vix | Yahoo: ^VIX | Daily | Level | ADF + KPSS | Secondary |
| 4 | 10Y Treasury Yield | dgs10 | FRED: DGS10 | Daily | Level | ADF + KPSS | Secondary |
| 5 | 3M Treasury Yield | dtb3 | FRED: DTB3 | Daily | Level | ADF + KPSS | Secondary |
| 6 | Fed Funds Rate | fed_funds | FRED: DFF | Daily | Level | ADF + KPSS | Secondary |
| 7 | Unemployment Rate | unrate | FRED: UNRATE | Monthly | Level | ADF + KPSS | Secondary |
| 8 | Capacity Utilization | caput | FRED: TCU | Monthly | Level | ADF + KPSS | Secondary |

### 6.2 Derived Series

| # | Derived Variable | Computation | Depends On |
|---|-----------------|-------------|------------|
| D1 | INDPRO YoY % change | `(indpro / indpro.shift(12) - 1) * 100` | indpro |
| D2 | INDPRO MoM % change | `(indpro / indpro.shift(1) - 1) * 100` | indpro |
| D3 | INDPRO 12M moving average | `indpro.rolling(12).mean()` | indpro |
| D4 | INDPRO deviation from trend | `indpro - indpro_12m_ma` | indpro, D3 |
| D5 | INDPRO Z-score (60M) | `(indpro - rolling_mean_60) / rolling_std_60` | indpro |
| D6 | INDPRO momentum (3M) | `indpro - indpro.shift(3)` | indpro |
| D7 | INDPRO momentum (6M) | `indpro - indpro.shift(6)` | indpro |
| D8 | INDPRO acceleration | `D2 - D2.shift(1)` (change in MoM growth) | D2 |
| D9 | INDPRO contraction dummy | `1 if D1 < 0 else 0` | D1 |
| D10 | Yield spread 10Y-3M | `dgs10 - dtb3` | dgs10, dtb3 |
| D11 | SPY monthly return | `spy_monthly.pct_change()` | spy |

### 6.3 Forward Target Returns (Dependent Variables)

| Horizon | Computation |
|---------|-------------|
| 1 month | `spy_monthly.shift(-1) / spy_monthly - 1` |
| 3 months | `spy_monthly.shift(-3) / spy_monthly - 1` |
| 6 months | `spy_monthly.shift(-6) / spy_monthly - 1` |
| 12 months | `spy_monthly.shift(-12) / spy_monthly - 1` |

Note: Since INDPRO is monthly, forward returns are computed at monthly frequency. For daily-frequency tournament strategies, daily SPY returns will be used with monthly INDPRO signals forward-filled to daily.

---

## 7. Method Classes

### 7.1 Recommended Categories

| Category | Catalog Section | Applicable? | Rationale |
|----------|----------------|-------------|-----------|
| Correlation & Dependence | Section 1 | Y | Baseline: establish correlation structure at multiple lags |
| Lead-Lag & Causality | Section 2 | Y | Core: test whether IP leads equity returns (H₁) |
| Regime Identification | Section 3 | Y | Core: IP expansion/contraction regimes (H₂) |
| Time-Series Modeling | Section 4 | Y | IP is monthly, auto-correlated — VAR/VECM appropriate |
| Volatility & Risk | Section 5 | N | IP is not a volatility indicator |
| Nonlinear & ML | Section 6 | Y | Test nonlinear relationship (H₃) |
| Signal Extraction | Section 7 | Y | Monthly-to-daily frequency mismatch requires signal extraction |
| Event Study / Tail | Section 8 | N | IP is continuous, not event-driven |
| Cointegration & Equilibrium | Section 9 | Y | IP level and log(SPY) may share a long-run equilibrium |
| Network & Spillover | Section 10 | N | Single-indicator analysis |
| Factor Decomposition | Section 11 | N | Not a factor model setup |
| Distributional & Higher-Moment | Section 12 | Y | Test if IP affects SPY return distribution shape (H₃) |
| Forecast Evaluation | Section 13 | Y | Compare IP-based forecasts vs naive/random walk |
| Liquidity & Microstructure | Section 14 | N | IP is macro, not microstructure |

**Recommended categories:** 1, 2, 3, 4, 6, 7, 9, 12, 13

### 7.2 Category Selection Heuristic

**Heuristic result:**
- Rule A (Stationarity): INDPRO is I(1), log(SPY) is I(1) → prioritize cointegration (Cat 9)
- Rule B (Frequency): Monthly indicator, daily target → add signal extraction (Cat 7)
- Rule C (Indicator type): Activity/Survey → always include Corr(1), Lead-Lag(2), TS(4); usually include Regime(3), ML(6)
- Rule D (Direction): pro_cyclical (clear) → no additional regime/distributional needed, but include for H₃

**Override rationale:** Including Distributional (Cat 12) and Forecast Evaluation (Cat 13) beyond heuristic recommendation because H₃ specifically asks about nonlinear/asymmetric effects and we want formal forecast comparison.

---

## 8. Tournament Design

### 8.1 Dimensions

**Signals:**

| ID | Signal | Variants |
|----|--------|----------|
| S1 | INDPRO level | Raw monthly value, forward-filled to daily |
| S2 | INDPRO YoY % change | D1 |
| S3 | INDPRO MoM % change | D2 |
| S4 | INDPRO deviation from trend | D4 |
| S5 | INDPRO Z-score (60M) | D5 |
| S6 | INDPRO momentum 3M | D6 |
| S7 | INDPRO momentum 6M | D7 |
| S8 | INDPRO acceleration | D8 |
| S9 | INDPRO contraction dummy | D9 |
| S10 | Composite (PCA of S2-S8) | Computed |

**Threshold Methods:**

| ID | Method | Variants |
|----|--------|----------|
| T1 | Fixed percentile (IS) | 25th, 50th, 75th |
| T2 | Rolling percentile (60M window) | 25th, 50th, 75th |
| T3 | Rolling mean ± k std (60M) | Mean ± 1.0σ, 1.5σ, 2.0σ |
| T4 | Zero-crossing (for YoY/MoM) | 0 (expansion/contraction) |
| T5 | HMM regime probability | 0.5, 0.7 |
| T6 | Markov-Switching probability | 0.5, 0.7 |

**Strategy Types:**

| ID | Strategy | Description |
|----|----------|-------------|
| P1 | Long/Cash | Long SPY when signal is pro-cyclical (above threshold), else cash |
| P2 | Signal-Strength | Position sized by normalized signal strength |
| P3 | Long/Short | Long SPY when bullish, short when bearish |

**Signal Lead Times:** L0, L21, L42, L63, L126 (monthly indicator → longer lead times appropriate)

**Lookback Windows:** LB36, LB60, LB120 (3Y, 5Y, 10Y — monthly data)

### 8.2 Computational Budget

| Parameter | Value |
|-----------|-------|
| **Max players (combinations)** | 10,000 |
| **Sampling strategy** | Exhaustive (estimated grid ~5,400) |
| **Estimated raw grid size** | 10 signals × 18 thresholds × 3 strategies × 5 leads × 3 lookbacks ≈ 8,100 |
| **Estimated post-pruning size** | ~5,400 (remove redundant combos) |
| **Pruning rules** | Contraction dummy (S9) only with T4 zero-crossing; HMM signal only with HMM threshold |

### 8.3 Target-Class-Specific Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Benchmark | SPY buy-and-hold | Standard equity benchmark |
| Risk-free rate | 3M T-bill (DTB3) | Standard short-term rate |
| Transaction costs | 5 bps | Liquid large-cap equity ETF |
| Calendar | US Market Hours | NYSE/NASDAQ trading days |
| Sample period constraint | 1990-2025 (INDPRO reliable from 1990) | Pre-1990 methodology changes |
| Sharpe validity threshold | 0.3 | Standard for equity strategies |

### 8.4 Tournament Rules

| Rule | Specification |
|------|---------------|
| **Primary ranking metric** | OOS Sharpe ratio (2018-01–2025-12) |
| **Tiebreakers** | Sortino → Calmar → max drawdown (least negative) |
| **Validity filters** | OOS Sharpe > 0; turnover < 24x/year; minimum 20 OOS trades |
| **Mandatory benchmark** | Buy-and-hold SPY |

### 8.5 Validation on Top Combinations

Apply to the top 5 tournament winners:

| Validation Method | Details |
|-------------------|---------|
| Walk-forward | 10yr train / 3yr test, roll 1yr |
| Bootstrap significance | 10,000 samples, p-value for Sharpe > 0 |
| Stress tests | GFC (2008-09), Taper Tantrum (2013), COVID (2020), Rate Hike Cycle (2022-23) |
| Transaction cost sensitivity | 0-50 bps range + breakeven analysis |
| Signal decay | 0, 5, 10, 21 day execution delay |

---

## 9. Deliverables Checklist

| # | Deliverable | File / Location | Owner | Status |
|---|------------|-----------------|-------|--------|
| 1 | **Analysis Brief** | `docs/analysis_brief_indpro_spy_20260314.md` | Alex | Done |
| 2 | **Master Dataset** | `data/indpro_spy_monthly_19900101_20251231.parquet` | Dana | Not Started |
| 3 | **Data Dictionary** | `data/data_dictionary_indpro_spy_20260314.csv` | Dana | Not Started |
| 4 | **Stationarity Tests** | `results/indpro_spy/stationarity_tests_20260314.csv` | Dana | Not Started |
| 5 | **Missing Value Report** | `data/missing_value_report_indpro_spy_20260314.md` | Dana | Not Started |
| 6 | **Exploratory Results** | `results/indpro_spy/exploratory_20260314/` | Evan | Not Started |
| 7 | **Core Model Results** | `results/indpro_spy/core_models_20260314/` | Evan | Not Started |
| 8 | **Interpretation Metadata** | `results/indpro_spy/interpretation_metadata.json` | Evan | Not Started |
| 9 | **Tournament Results** | `results/indpro_spy/tournament_results_20260314.csv` | Evan | Not Started |
| 10 | **Top-5 Validation** | `results/indpro_spy/tournament_validation_20260314/` | Evan | Not Started |
| 11 | **Plotly JSON Charts** | `output/charts/indpro_spy/plotly/` | Vera | Not Started |
| 12 | **PNG Fallback Charts** | `output/charts/indpro_spy/png/` | Vera | Not Started |
| 13 | **Streamlit Portal Pages** | `app/pages/indpro_spy/` | Ace | Not Started |

---

## 10. Portal Specifications

| Field | Value |
|-------|-------|
| **Page title** | Industrial Production → S&P 500 Analysis |
| **Target audience** | Portfolio managers with economics background but no coding skills |
| **Direction annotation** | pro_cyclical |

**Direction annotation — "How to Read This" callout:**

> When Industrial Production is rising (positive YoY growth), this historically signals expanding manufacturing activity and tends to precede stronger equity returns. Charts where IP growth is positive should be read as bullish for the S&P 500. When IP contracts (negative YoY growth), expect weaker equity performance with a lag of 1-3 months.

**Key KPI Cards:**

| # | KPI | Source | Format |
|---|-----|--------|--------|
| 1 | Current INDPRO YoY growth | Latest INDPRO value | +X.X% |
| 2 | Current regime | HMM state | Expansion / Contraction |
| 3 | OOS Sharpe (winner) | Tournament results | X.XX |
| 4 | Max drawdown avoided | Tournament validation | -X.X% vs -X.X% |
| 5 | Signal status | Latest signal from winning strategy | Risk-On / Risk-Off |

**Portal page structure:**

| Page | Title | Content |
|------|-------|---------|
| Story | The IP-Equity Connection | Layperson narrative: why factory output matters for your portfolio |
| Evidence | Statistical Evidence | Granger causality, local projections, regime analysis |
| Strategy | Trading Strategy | Tournament results, equity curves, signal dashboard |
| Methodology | Technical Details | Model specs, diagnostics, sensitivity analysis |

---

## 11. Quality Standards

Per template — all standard diagnostics, reverse causality check (G11), reconciliation checkpoints, and interpretation metadata apply.

Special attention for this pair:
- **Publication lag:** INDPRO released ~6 weeks after reference month. Tournament must use lagged signals (minimum L42 for realistic trading).
- **Frequency mismatch:** Monthly INDPRO → daily SPY requires forward-fill with explicit documentation of autocorrelation implications.
- **COVID outlier:** April 2020 INDPRO drop (-12.7% MoM) is a genuine observation but may dominate regime models. Run with and without COVID window.

---

## 12. Timeline Dependencies

Standard 5-phase workflow per template. Estimated 4-6 hours wall-clock.

---

**Distribution:** Dana, Evan, Vera, Ace. All agents should read this brief plus their SOP before beginning work.

---
*Template source: `docs/analysis_brief_template.md`*
