# Analysis Brief: {INDICATOR_NAME} → {TARGET_NAME}

| Field       | Value                     |
|-------------|---------------------------|
| **Date**    | {DATE}                    |
| **Author**  | {AUTHOR}                  |
| **Version** | {VERSION} (e.g., 1.0)    |
| **Status**  | Draft \| Under Review \| Approved |

> **Purpose.** This is the mandatory kickoff document for any indicator-target analysis run.
> No agent work begins until this brief reaches **Approved** status and is distributed to
> all assigned agents. Fill every `{PLACEHOLDER}` field; delete the inline guidance once
> populated. See the worked example at
> [`docs/analysis_brief_hy_ig_spy_20260228.md`](analysis_brief_hy_ig_spy_20260228.md)
> for a completed instance.

---

## 1. Research Question

**Question:** {RESEARCH_QUESTION}

> *Guidance: State the economic question in plain English. Example: "Does the HY-IG credit
> spread predict S&P 500 equity returns? If so, through what mechanism, at what horizons,
> and can it be profitably traded?"*

### Hypotheses

| # | Statement | Identification Strategy |
|---|-----------|------------------------|
| H₀ | {NULL_HYPOTHESIS} | {H0_IDENTIFICATION} |
| H₁ | {ALT_HYPOTHESIS_1} | {H1_IDENTIFICATION} |
| H₂ | {ALT_HYPOTHESIS_2} *(optional — add rows as needed)* | {H2_IDENTIFICATION} |

> *Guidance: Each hypothesis should be testable and falsifiable. Pair it with the
> identification strategy that will produce the evidence (e.g., Granger causality,
> local projections, regime-switching regression). Refer to the
> [Econometric Methods Catalog](econometric-methods-catalog.md) for method IDs.*

---

## 2. Indicator Specification

| Field | Value |
|-------|-------|
| **Indicator** | {INDICATOR_NAME} |
| **ID** | {INDICATOR_ID} *(short code used in file names, e.g., `hy_ig`)* |
| **Canonical name** | {CANONICAL_NAME} *(exact name from data provider, e.g., "ICE BofA US HY OAS minus ICE BofA US IG OAS")* |
| **Source** | {SOURCE} *(provider and series code, e.g., FRED: `BAMLH0A0HYM2` minus `BAMLC0A0CM`)* |
| **Frequency** | {FREQUENCY} *(Daily / Weekly / Monthly / Quarterly)* |
| **Transformation** | {TRANSFORMATION} *(e.g., Level, YoY % change, Log, First difference, Z-score)* |
| **Indicator type** | {INDICATOR_TYPE} |

**Allowed indicator types** (pick one):

| Type | Examples |
|------|----------|
| Credit Spread | HY-IG OAS, CCC-BB quality spread, CDX indices |
| Volatility / Options | VIX, MOVE, VIX term structure, SKEW |
| Activity / Survey | ISM PMI, Initial Claims, LEI, SLOOS |
| Yield Curve / Rates | 10Y-2Y spread, 10Y-3M spread, breakevens |
| Sentiment / Flow | Put/Call ratio, Fear & Greed, EBP |
| Cross-Asset | Gold, copper, DXY, oil, EM spreads |
| Microstructure | Advance-decline, breadth, market-on-close imbalance |

> *Guidance: The indicator is the independent variable — the signal you believe
> carries predictive information about the target. Use canonical names from the
> [Data Series Catalog](data-series-catalog.md).*

---

## 3. Target Specification

| Field | Value |
|-------|-------|
| **Target** | {TARGET_NAME} |
| **ID** | {TARGET_ID} *(short code, e.g., `spy`)* |
| **Ticker** | {TARGET_TICKER} *(e.g., SPY, QQQ, IWM, HYG, TLT)* |
| **Asset class** | {TARGET_CLASS} *(Equity / Fixed Income / Commodity / FX / Crypto)* |
| **Benchmark** | {BENCHMARK_TICKER} *(buy-and-hold comparison, e.g., SPY for equity targets)* |
| **Trading calendar** | {CALENDAR} *(US Market Hours / Extended / 24-7)* |
| **Transaction cost assumption** | {TX_COST_BPS} bps per trade |

> *Guidance: The target is the dependent variable — the asset whose returns
> you are trying to predict or trade. The benchmark is the passive buy-and-hold
> portfolio that the tournament must beat.*

---

## 4. Expected Direction

This section captures the analyst's prior belief about how the indicator relates to the
target. It is required for three reasons: (a) it prevents post-hoc narrative fitting,
(b) it feeds the portal's "How to Read This" interpretation callout, and (c) it anchors
the visualization agent's color-coding conventions.

| Field | Value |
|-------|-------|
| **Expected direction** | {EXPECTED_DIRECTION} |
| **Mechanism** | {MECHANISM} |
| **Literature support** | {LITERATURE_SUPPORT} |

**Allowed values for `expected_direction`:**

| Value | Meaning | Example |
|-------|---------|---------|
| `pro_cyclical` | Higher indicator values → higher target returns | ISM PMI ↑ → SPY ↑ |
| `counter_cyclical` | Higher indicator values → lower target returns | HY-IG spread ↑ → SPY ↓ |
| `ambiguous` | Direction must be determined empirically | DXY → SPY (regime-dependent) |
| `conditional` | Direction depends on regime (specify in mechanism) | VIX → SPY (low VIX = calm, but rising VIX from low levels can be bullish) |

**Mechanism** — Plain-English explanation of the economic channel:

> *Example: "Widening HY-IG spreads reflect deteriorating credit conditions and rising
> default risk. This reduces firms' access to capital, depresses investment, and signals
> a risk-off environment. Equity markets respond with a lag as earnings expectations
> adjust downward."*

{MECHANISM}

**Literature support** — Strength of existing evidence:

| Level | Meaning |
|-------|---------|
| **Strong** | 5+ peer-reviewed studies with consistent findings |
| **Moderate** | 2-4 studies or practitioner consensus with limited academic coverage |
| **Weak** | 1 study or anecdotal / theoretical reasoning only |
| **Exploratory** | No known prior work; this analysis is novel |

> *Guidance: If `conditional`, describe the regime-dependent logic in the mechanism
> field. If `ambiguous`, explain why the direction is uncertain and what the analysis
> should determine.*

---

## 5. Sample Design

| Field | Value |
|-------|-------|
| **Full sample period** | {SAMPLE_START} to {SAMPLE_END} |
| **In-sample (IS)** | {IS_START} to {IS_END} |
| **Out-of-sample (OOS)** | {OOS_START} to {OOS_END} |
| **Minimum sample constraint** | {MIN_YEARS} years |
| **Frequency** | {SAMPLE_FREQUENCY} *(Daily / Weekly / Monthly)* |
| **Approximate IS observations** | {IS_OBS} |
| **Approximate OOS observations** | {OOS_OBS} |

**Known limitations:**

{SAMPLE_LIMITATIONS}

> *Guidance: List data gaps, survivorship issues, regime coverage gaps, or
> structural breaks within the sample. Example: "SOFR data only available from
> 2018; pre-2018 uses fed funds as proxy." The IS/OOS split should ensure the OOS
> window includes at least one stress episode for validity.*

---

## 6. Data Requirements

### 6.1 Core and Secondary Series

| # | Variable | Preferred Name | Source | Frequency | Transform | Stationarity Test | Priority |
|---|----------|---------------|--------|-----------|-----------|-------------------|----------|
| 1 | {VAR_1} | {PREF_NAME_1} | {SRC_1} | {FREQ_1} | {XFORM_1} | {STAT_TEST_1} | Core |
| 2 | {VAR_2} | {PREF_NAME_2} | {SRC_2} | {FREQ_2} | {XFORM_2} | {STAT_TEST_2} | Core |
| 3 | {VAR_3} | {PREF_NAME_3} | {SRC_3} | {FREQ_3} | {XFORM_3} | {STAT_TEST_3} | Secondary |
| ... | ... | ... | ... | ... | ... | ... | ... |

> *Guidance: List all raw series needed. Use IDs from the
> [Data Series Catalog](data-series-catalog.md). Priority = Core (required for
> pipeline) or Secondary (enrichment, can proceed without). Stationarity test =
> ADF / KPSS / PP / ZA — specify which will be run. Transform = Level / Log /
> Diff / YoY% / Z-score.*

### 6.2 Derived Series

| # | Derived Variable | Computation | Depends On |
|---|-----------------|-------------|------------|
| D1 | {DERIVED_1} | {COMPUTATION_1} | {DEPENDS_1} |
| D2 | {DERIVED_2} | {COMPUTATION_2} | {DEPENDS_2} |
| ... | ... | ... | ... |

> *Guidance: Include all computed features — spreads, z-scores, rolling ranks,
> rates of change, momentum, relative strength ratios, term structures. Specify
> the exact formula and which raw series it depends on.*

### 6.3 Forward Target Returns (Dependent Variables)

| Horizon | Computation |
|---------|-------------|
| {HORIZON_1} | {RETURN_FORMULA_1} |
| {HORIZON_2} | {RETURN_FORMULA_2} |
| ... | ... |

> *Guidance: Forward returns are the dependent variables for predictive models
> and tournament strategies. Use `shift(-h)` convention for h-day ahead returns.
> Include at least 1d, 5d, 21d, 63d horizons.*

---

## 7. Method Classes

### 7.1 Recommended Categories

The [Econometric Methods Catalog](econometric-methods-catalog.md) organizes 52 methods
into 8 categories. Select which categories apply to this analysis:

| Category | Catalog Section | Applicable? | Rationale |
|----------|----------------|-------------|-----------|
| Correlation & Dependence | Section 1 | {Y/N} | {RATIONALE_CORR} |
| Lead-Lag & Causality | Section 2 | {Y/N} | {RATIONALE_LEADLAG} |
| Regime Identification | Section 3 | {Y/N} | {RATIONALE_REGIME} |
| Time-Series Modeling | Section 4 | {Y/N} | {RATIONALE_TS} |
| Volatility & Risk | Section 5 | {Y/N} | {RATIONALE_VOL} |
| Nonlinear & ML | Section 6 | {Y/N} | {RATIONALE_ML} |
| Signal Extraction | Section 7 | {Y/N} | {RATIONALE_SIGNAL} |
| Event Study / Tail | Section 8 | {Y/N} | {RATIONALE_TAIL} |

**Recommended categories:** {RECOMMENDED_CATEGORIES}

### 7.2 Category Selection Heuristic

The heuristic below determines category selection based on indicator type and target
class. Record the heuristic output and any overrides.

| Indicator Type → | Credit Spread | Volatility | Activity | Yield Curve | Sentiment | Cross-Asset | Micro |
|:-----------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Always include** | Corr, Lead-Lag, Regime | Corr, Vol, Regime | Corr, Lead-Lag, TS | Corr, Lead-Lag, TS | Corr, Tail | Corr, Lead-Lag | Corr, Tail |
| **Usually include** | TS, Vol, ML | Lead-Lag, ML | Regime, ML | Regime, Vol | Regime, ML | Regime, Signal | Signal, ML |
| **Optional** | Signal, Tail | Signal, Tail | Vol, Signal, Tail | Signal, Tail, ML | TS, Signal, Vol | TS, Vol, Tail, ML | Lead-Lag, TS, Vol, Regime |

**Heuristic result:** {HEURISTIC_RESULT}

**Override rationale** (if departing from heuristic): {OVERRIDE_REASON}

> *Guidance: The heuristic is a suggestion, not a mandate. Override when domain
> knowledge warrants it — but document why.*

---

## 8. Tournament Design

### 8.1 Dimensions

**Signals:**

| ID | Signal | Variants |
|----|--------|----------|
| {S_ID_1} | {SIGNAL_1} | {SIGNAL_VARIANTS_1} |
| {S_ID_2} | {SIGNAL_2} | {SIGNAL_VARIANTS_2} |
| ... | ... | ... |

> *Full signal list: {SIGNAL_LIST}*

**Threshold Methods:**

| ID | Method | Variants |
|----|--------|----------|
| {T_ID_1} | {THRESHOLD_1} | {THRESHOLD_VARIANTS_1} |
| {T_ID_2} | {THRESHOLD_2} | {THRESHOLD_VARIANTS_2} |
| ... | ... | ... |

> *Full threshold list: {THRESHOLD_LIST}.
> See [Threshold & Regime Methods Catalog](threshold-regime-methods-catalog.md)
> for method details and implementation references.*

**Strategy Types:**

| ID | Strategy | Description |
|----|----------|-------------|
| {P_ID_1} | {STRATEGY_1} | {STRATEGY_DESC_1} |
| {P_ID_2} | {STRATEGY_2} | {STRATEGY_DESC_2} |
| ... | ... | ... |

> *Full strategy list: {STRATEGY_LIST}*

**Signal Lead Times:**

| ID | Lag | Meaning |
|----|-----|---------|
| L5 | 5d | 1-week lag |
| L10 | 10d | 2-week lag |
| L21 | 21d | 1-month lag |
| L42 | 42d | 2-month lag |
| L63 | 63d | 1-quarter lag |
| L126 | 126d | 6-month lag |
| L252 | 252d | 1-year lag |

> *Adjust lead times for the indicator's expected information horizon.
> Full lead time list: {LEAD_TIMES}*

**Lookback Windows:**

{LOOKBACK_WINDOWS} *(e.g., LB60, LB120, LB252, LB504)*

### 8.2 Computational Budget

| Parameter | Value |
|-----------|-------|
| **Max players (combinations)** | {MAX_PLAYERS} *(default: 10,000)* |
| **Sampling strategy** | {SAMPLING_STRATEGY} *(Exhaustive if grid ≤ 10,000; Stratified random sampling if grid > 10,000; Latin hypercube if dimensionality > 6)* |
| **Estimated raw grid size** | {RAW_GRID_SIZE} |
| **Estimated post-pruning size** | {PRUNED_GRID_SIZE} |
| **Pruning rules** | {PRUNING_RULES} *(e.g., "HMM signal + HMM threshold is redundant; remove")* |

### 8.3 Target-Class-Specific Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Benchmark | {BENCHMARK} | {BENCHMARK_RATIONALE} |
| Risk-free rate | {RF_RATE} | {RF_RATIONALE} *(e.g., SOFR / 3-month T-bill)* |
| Transaction costs | {TX_COST} bps | {TX_RATIONALE} |
| Calendar | {CALENDAR} | {CALENDAR_RATIONALE} |
| Sample period constraint | {SAMPLE_CONSTRAINT} | {CONSTRAINT_RATIONALE} |
| Sharpe validity threshold | {SHARPE_THRESHOLD} | {SHARPE_RATIONALE} *(asset-class adjusted; typically 0.3 for equities, 0.5 for FI)* |

### 8.4 Tournament Rules

| Rule | Specification |
|------|---------------|
| **Primary ranking metric** | OOS Sharpe ratio ({OOS_START}–{OOS_END}) |
| **Tiebreakers** | Sortino → Calmar → max drawdown (least negative) |
| **Validity filters** | OOS Sharpe > 0; turnover < {MAX_TURNOVER}x/year; minimum {MIN_OOS_TRADES} OOS trades |
| **Mandatory benchmark** | Buy-and-hold {BENCHMARK_TICKER} |

### 8.5 Validation on Top Combinations

Apply to the top {TOP_N} tournament winners:

| Validation Method | Details |
|-------------------|---------|
| Walk-forward | {WF_TRAIN}yr train / {WF_TEST}yr test, roll {WF_STEP} |
| Bootstrap significance | {BOOTSTRAP_N} samples, p-value for Sharpe > 0 |
| Stress tests | {STRESS_TEST_PERIODS} |
| Transaction cost sensitivity | {TX_RANGE} bps range + breakeven analysis |
| Signal decay | {DECAY_LAGS} execution delay test |

---

## 9. Deliverables Checklist

| # | Deliverable | File / Location | Owner | Status |
|---|------------|-----------------|-------|--------|
| 1 | **Analysis Brief** (this document) | `docs/analysis_brief_{INDICATOR_ID}_{TARGET_ID}_{DATE}.md` | Lesandro | {STATUS_BRIEF} |
| 2 | **Spec Memo** | `docs/spec_memo_{INDICATOR_ID}_{TARGET_ID}_{DATE}.md` | Ray | {STATUS_SPEC} |
| 3 | **Research Brief** | `docs/research_brief_{INDICATOR_ID}_{TARGET_ID}_{DATE}.md` | Ray | {STATUS_RESEARCH} |
| 4 | **Portal Narrative** | `docs/portal_narrative_{INDICATOR_ID}_{TARGET_ID}_{DATE}.md` | Ray | {STATUS_NARRATIVE} |
| 5 | **Storytelling Arc** | `docs/storytelling_arc_{INDICATOR_ID}_{TARGET_ID}_{DATE}.md` | Ray | {STATUS_STORY} |
| 6 | **Master Dataset** | `data/{INDICATOR_ID}_{TARGET_ID}_daily_{SAMPLE_START_SHORT}_{SAMPLE_END_SHORT}.parquet` | Dana | {STATUS_DATA} |
| 7 | **Data Dictionary** | `data/data_dictionary_{INDICATOR_ID}_{TARGET_ID}_{DATE}.csv` | Dana | {STATUS_DICT} |
| 8 | **Stationarity Tests** | `results/stationarity_tests_{DATE}.csv` | Dana | {STATUS_STATIONARITY} |
| 9 | **Missing Value Report** | `data/missing_value_report_{INDICATOR_ID}_{TARGET_ID}_{DATE}.md` | Dana | {STATUS_MISSING} |
| 10 | **Exploratory Results** | `results/exploratory_{DATE}/` | Evan | {STATUS_EXPLORATORY} |
| 11 | **Core Model Results** | `results/core_models_{DATE}/` | Evan | {STATUS_CORE} |
| 12 | **Tournament Results** | `results/tournament_results_{DATE}.csv` | Evan | {STATUS_TOURNAMENT} |
| 13 | **Top-N Validation** | `results/tournament_validation_{DATE}/` | Evan | {STATUS_VALIDATION} |
| 14 | **Chart Requests** | `results/chart_requests_{DATE}/` | Evan | {STATUS_CHART_REQ} |
| 15 | **Plotly JSON Charts** | `output/charts/plotly/` | Vera | {STATUS_PLOTLY} |
| 16 | **PNG Fallback Charts** | `output/charts/png/` | Vera | {STATUS_PNG} |
| 17 | **Chart Metadata** | `output/charts/metadata/` | Vera | {STATUS_CHART_META} |
| 18 | **Streamlit Portal Pages** | `app/pages/` | Ace | {STATUS_PORTAL} |

> *Guidance: Set each Status to one of: Not Started / In Progress / Review / Done / Blocked.
> Update this table as the analysis proceeds.*

---

## 10. Portal Specifications

| Field | Value |
|-------|-------|
| **Page title** | {PAGE_TITLE} |
| **Target audience** | {AUDIENCE} *(e.g., Portfolio managers with economics background but no coding skills)* |
| **Direction annotation** | {DIRECTION_ANNOTATION} |

**Direction annotation** provides the text for the portal's "How to Read This" callout box:

> *Example for counter-cyclical HY-IG → SPY: "When the HY-IG credit spread widens
> (moves up), this historically signals deteriorating credit conditions and tends to
> precede weaker equity returns. Charts where the indicator is rising should be read
> as bearish for the target."*

{DIRECTION_ANNOTATION}

**Key KPI Cards:**

| # | KPI | Source | Format |
|---|-----|--------|--------|
| 1 | {KPI_1} | {KPI_SOURCE_1} | {KPI_FORMAT_1} |
| 2 | {KPI_2} | {KPI_SOURCE_2} | {KPI_FORMAT_2} |
| 3 | {KPI_3} | {KPI_SOURCE_3} | {KPI_FORMAT_3} |
| ... | ... | ... | ... |

> *Full KPI list: {KPI_LIST}. Typical KPIs include: current indicator value, current
> regime, OOS Sharpe of winner, max drawdown avoided, signal status (risk-on / risk-off),
> days since last signal change.*

**Portal page structure:**

| Page | Title | Content |
|------|-------|---------|
| Story | {STORY_PAGE_TITLE} | Layperson narrative with embedded visuals |
| Evidence | {EVIDENCE_PAGE_TITLE} | Interactive charts — Plotly with hover, zoom, regime filter |
| Strategy | {STRATEGY_PAGE_TITLE} | Tournament winner, alternatives, live signal dashboard |
| Methodology | {METHODOLOGY_PAGE_TITLE} | Technical appendix — model specs, diagnostics, sensitivity |

---

## 11. Quality Standards

### 11.1 Minimum Diagnostics

Every estimated model must report:

| Diagnostic | Test | Package |
|-----------|------|---------|
| Normality of residuals | Jarque-Bera | `scipy.stats.jarque_bera` |
| Heteroskedasticity | Breusch-Pagan | `statsmodels.stats.diagnostic.het_breuschpagan` |
| Serial correlation | Breusch-Godfrey | `statsmodels.stats.diagnostic.acorr_breusch_godfrey` |
| Functional form | RESET | `statsmodels.stats.diagnostic.linear_reset` |
| Stationarity | ADF + KPSS (confirmatory) | `statsmodels.tsa.stattools.adfuller`, `statsmodels.tsa.stattools.kpss` |
| Multicollinearity | VIF (if > 2 regressors) | `statsmodels.stats.outliers_influence.variance_inflation_factor` |

### 11.2 Mandatory Reverse Causality Check (G11 Gap Resolution)

Every lead-lag or predictive claim must include a reverse-causality test:

- Run the same predictive model in both directions: Indicator → Target AND Target → Indicator
- Report both sets of results side by side
- If reverse causality is significant, flag it and discuss whether the finding survives
- Use local projections (Jorda) for impulse response comparison in both directions

> *This resolves gap G11 from the multi-indicator design review. It is not optional.*

### 11.3 Reconciliation Checkpoints

At each pipeline handoff, the receiving agent must verify:

| Checkpoint | Verification |
|------------|-------------|
| Row counts match | `len(df)` matches between sender and receiver |
| Date range matches | `df.index.min()` and `df.index.max()` consistent |
| No silent NaN injection | `df.isna().sum()` reported and explained |
| Column names match data dictionary | All columns present and correctly named |
| Reproducibility | Re-running sender's script produces identical output (hash check) |

### 11.4 Interpretation Metadata

Every model output must include a structured interpretation block:

```json
{
  "indicator": "{INDICATOR_ID}",
  "target": "{TARGET_ID}",
  "expected_direction": "{EXPECTED_DIRECTION}",
  "observed_direction": "<pro_cyclical | counter_cyclical | ambiguous | conditional>",
  "direction_consistent": "<true | false>",
  "mechanism": "{MECHANISM}",
  "confidence": "<high | medium | low>",
  "key_finding": "<one-sentence summary>",
  "caveats": ["<list of limitations>"]
}
```

> *This metadata feeds the portal narrative and ensures every quantitative result
> has a "so what" interpretation attached.*

### 11.5 Quantitative Claim Standards

- Every quantitative claim has a p-value or confidence interval
- Every qualitative claim cites Author (Year) — 3+ studies = consensus, 1 study = flagged
- Every result has a plain-English "so what" interpretation
- OOS performance is the primary evaluation criterion, not in-sample
- Transaction costs included in all strategy metrics
- Report HC3 robust standard errors by default

---

## 12. Timeline Dependencies

```
Phase 0 (Lesandro: Brief) ──────────────────────────┐
                                                  │
Phase 1A (Ray: Research) ──────────────────┐     │
Phase 1B (Dana: Data)     ─────────────────┤     │ parallel
                                            │     │
Gate 1 (Lesandro Review) ──────────────────────┤     │
                                            │     │
Phase 2 (Evan: Econometrics) ──────────────┤     │
                                            │     │
Gate 2 (Lesandro Review) ──────────────────────┤     │
                                            │     │
Phase 3 (Vera: Visualization) ─────────────┤     │
                                            │     │
Gate 3 (Lesandro Review) ──────────────────────┤     │
                                            │     │
Phase 4 (Ace: Portal Assembly) ────────────┤     │
                                            │     │
Gate 4 (Lesandro Final Review) ────────────────┘     │
                                                  │
Phase 5 (Lessons Learned — All) ─────────────────┘
```

> *Guidance: Gates are mandatory review checkpoints. Work does not advance past a gate
> until Lesandro approves. Phases 1A and 1B run in parallel. Ace can scaffold portal structure
> during Phases 1-2 while waiting for final content.*

---

## Appendix

### A. Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Worked example (HY-IG → SPY) | [`docs/analysis_brief_hy_ig_spy_20260228.md`](analysis_brief_hy_ig_spy_20260228.md) | Completed instance of this template |
| Econometric Methods Catalog | [`docs/econometric-methods-catalog.md`](econometric-methods-catalog.md) | 52 candidate methods with relevance matrix |
| Data Series Catalog | [`docs/data-series-catalog.md`](data-series-catalog.md) | 63 candidate time series across 7 categories |
| Threshold & Regime Methods Catalog | [`docs/threshold-regime-methods-catalog.md`](threshold-regime-methods-catalog.md) | 40 threshold/regime identification techniques |
| Backtesting Approaches Catalog | [`docs/backtesting-approaches-catalog.md`](backtesting-approaches-catalog.md) | 62 backtesting approaches across 6 dimensions |
| Reference Catalogs Index | [`docs/reference-catalogs-index.md`](reference-catalogs-index.md) | Master index linking all four catalogs |
| Team Coordination Protocol | [`docs/agent-sops/team-coordination.md`](agent-sops/team-coordination.md) | Handoff formats, naming conventions, escalation |

### B. File Naming Convention

All deliverables follow this pattern:

```
{type}_{indicator_id}_{target_id}_{date_YYYYMMDD}.{ext}
```

Examples:
- `analysis_brief_hy_ig_spy_20260228.md`
- `research_brief_vix_ts_qqq_20260315.md`
- `tournament_results_20260315.csv`
- `hy_ig_spy_daily_20000101_20251231.parquet`

### C. Placeholder Quick Reference

| Placeholder | Section | Description |
|-------------|---------|-------------|
| `{INDICATOR_NAME}` | Header, S2 | Human-readable indicator name |
| `{INDICATOR_ID}` | S2, S9, S11 | Short code for file names (e.g., `hy_ig`, `vix_ts`) |
| `{CANONICAL_NAME}` | S2 | Exact provider name |
| `{SOURCE}` | S2 | Data provider and series code |
| `{FREQUENCY}` | S2 | Daily / Weekly / Monthly / Quarterly |
| `{TRANSFORMATION}` | S2 | Level / Log / Diff / YoY% / Z-score |
| `{INDICATOR_TYPE}` | S2 | One of 7 allowed types |
| `{TARGET_NAME}` | Header, S3 | Human-readable target name |
| `{TARGET_ID}` | S3, S9, S11 | Short code for file names (e.g., `spy`, `qqq`) |
| `{TARGET_TICKER}` | S3 | Trading ticker |
| `{TARGET_CLASS}` | S3 | Equity / Fixed Income / Commodity / FX / Crypto |
| `{BENCHMARK_TICKER}` | S3, S8 | Buy-and-hold benchmark ticker |
| `{CALENDAR}` | S3, S8 | Trading calendar type |
| `{TX_COST_BPS}` | S3, S8 | Transaction cost in basis points |
| `{EXPECTED_DIRECTION}` | S4, S11 | pro_cyclical / counter_cyclical / ambiguous / conditional |
| `{MECHANISM}` | S4, S11 | Plain-English economic channel description |
| `{LITERATURE_SUPPORT}` | S4 | Strong / Moderate / Weak / Exploratory |
| `{SAMPLE_START}` / `{SAMPLE_END}` | S5 | Full sample date range |
| `{IS_START}` / `{IS_END}` | S5 | In-sample date range |
| `{OOS_START}` / `{OOS_END}` | S5, S8 | Out-of-sample date range |
| `{MIN_YEARS}` | S5 | Minimum required sample length |
| `{SAMPLE_LIMITATIONS}` | S5 | Known data gaps and caveats |
| `{RECOMMENDED_CATEGORIES}` | S7 | Selected method categories from catalog |
| `{HEURISTIC_RESULT}` | S7 | Output of category selection heuristic |
| `{OVERRIDE_REASON}` | S7 | Justification for departing from heuristic |
| `{SIGNAL_LIST}` | S8 | Tournament signal dimension members |
| `{THRESHOLD_LIST}` | S8 | Tournament threshold dimension members |
| `{STRATEGY_LIST}` | S8 | Tournament strategy dimension members |
| `{LEAD_TIMES}` | S8 | Signal lead time values |
| `{LOOKBACK_WINDOWS}` | S8 | Rolling window lengths |
| `{MAX_PLAYERS}` | S8 | Computational budget cap |
| `{PAGE_TITLE}` | S10 | Streamlit portal page title |
| `{AUDIENCE}` | S10 | Target audience description |
| `{DIRECTION_ANNOTATION}` | S10 | "How to Read This" callout text |
| `{KPI_LIST}` | S10 | Key performance indicator cards |
| `{DATE}` | Header, S9 | Brief creation date (YYYYMMDD) |
| `{AUTHOR}` | Header | Brief author name and role |
| `{VERSION}` | Header | Document version number |

---

**Distribution:** This brief must be distributed to all assigned agents ({AGENT_LIST}).
All agents should read this document plus their individual SOP
([`docs/agent-sops/`](agent-sops/)) plus the
[Team Coordination Protocol](agent-sops/team-coordination.md) before beginning work.

---
*Template version: 1.0*
*Created: {DATE}*
*Template source: `docs/analysis_brief_template.md`*
