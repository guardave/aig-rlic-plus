# Reference Catalogs Index

## Multi-Indicator Analysis Framework — Engine Parts Library

This index links to five reference catalogs that serve as a library of interchangeable "engine parts" for multi-indicator analysis design. Each catalog covers one dimension of the analysis pipeline — data, methods, backtesting, regime detection, and priority combinations. Not all parts will be used in every analysis — they are here for selection, substitution, and future enrichment.

---

## Catalogs

| # | Catalog | File | Contents | Count |
|---|---------|------|----------|-------|
| A | **Data Series** | [`data-series-catalog.md`](data-series-catalog.md) | Candidate time series across credit, equity, macro, sentiment, alternative assets, and computed derivatives — includes 31 indicators, 35 targets, and original 63 base series | 129 |
| B | **Econometric Methods** | [`econometric-methods-catalog.md`](econometric-methods-catalog.md) | Statistical and econometric techniques for correlation, causality, regime detection, volatility, ML, signal extraction, tail analysis, cointegration, network, factor, distributional, forecast evaluation, and liquidity methods | 95 |
| C | **Backtesting Approaches** | [`backtesting-approaches-catalog.md`](backtesting-approaches-catalog.md) | Strategy evaluation frameworks spanning return metrics, risk metrics, long/short variants, validation methods, and practical considerations | 62 |
| D | **Threshold & Regime Methods** | [`threshold-regime-methods-catalog.md`](threshold-regime-methods-catalog.md) | Techniques for identifying market regimes and signal thresholds — statistical, adaptive, ML-based, and multi-dimensional | 40 |
| E | **Priority Combinations** | [`priority-combinations-catalog.md`](priority-combinations-catalog.md) | Human-analyzed indicator x target pairs — benchmark reference for agent comparison | 73 |

**Total: 399 candidates across 5 dimensions**

---

## How to Use These Catalogs

### For Analysis Design

0. **Start with the Analysis Brief** — Fill out the Analysis Brief template (`docs/analysis_brief_template.md`) before selecting from any catalog
1. **Start with the question** — What economic hypothesis are we testing?
2. **Select data** from Catalog A — Choose base series and derivatives relevant to the hypothesis
3. **Select methods** from Catalog B — Match the method to the data structure (cross-section, time-series, panel) and the question type (correlation, causation, prediction, regime)
4. **Select threshold approach** from Catalog D — Choose how to identify regimes or signal boundaries
5. **Select backtest framework** from Catalog C — Choose metrics, strategy variants, and validation approach

### For Iterative Improvement

- **Add a data series:** Source it, add to Catalog A, re-run the pipeline
- **Swap a method:** Replace one technique with another from the same category in Catalog B
- **Change the backtest lens:** Switch from return-oriented to risk-oriented using Catalog C alternatives
- **Refine thresholds:** Move from fixed to adaptive using Catalog D options

### Priority Tags

Each catalog includes implementation priority recommendations:
- **Phase 1 (Quick wins)** — Low complexity, high value, can be done in hours
- **Phase 2 (Core enhancements)** — Moderate complexity, fills major analytical gaps
- **Phase 3 (Advanced)** — High complexity, provides differentiated insights
- **Phase 4 (New categories)** — Multi-indicator expansion; cointegration, network, factor, distributional, forecast evaluation, liquidity methods

---

## Cross-Reference: Sample Analysis vs. Catalog Options

What the HY-IG baseline used and what the multi-indicator framework upgrades to:

| Dimension | HY-IG Baseline | Multi-Indicator Framework |
|-----------|---------------|--------------------------|
| **Data** | HY-IG spread, SPY (2 series) | 31 indicators x 35 targets (see Catalogs A & E) |
| **Correlation** | Pearson, Spearman, rolling window (from HY-IG baseline) | DCC-GARCH, copulas, distance correlation, mutual information, time-varying |
| **Lead-lag** | Granger causality, cross-correlation (from HY-IG baseline) | Toda-Yamamoto, transfer entropy, wavelet coherence, frequency-domain Granger |
| **Regimes** | HMM, fixed thresholds (from HY-IG baseline) | Markov-switching, TAR, change-point detection, adaptive percentiles, ML clustering |
| **Time-series model** | VAR, VECM (from HY-IG baseline) | SVAR, TVP-VAR, BVAR, local projections, GARCH-MIDAS |
| **Backtest: metrics** | Sharpe, max drawdown, total return (from HY-IG baseline) | Sortino, Calmar, Omega, VaR, CVaR, Ulcer index, stress tests |
| **Backtest: strategy** | Long/cash, regime-based (from HY-IG baseline) | Long/short, volatility targeting, drawdown control, put hedging, pairs trading |
| **Backtest: validation** | Walk-forward, expanding window (from HY-IG baseline) | Bootstrap, White's Reality Check, CPCV, combinatorial purged |

---

## Registered Analysis Runs

This table tracks completed indicator-target analysis runs. It is the single source of truth for what has been analyzed by the agent team.

| Run # | Indicator (ID) | Target (ID) | Date Completed | Lead Agent | Brief | Results | Portal Page | Priority? |
|-------|---------------|-------------|----------------|------------|-------|---------|-------------|-----------|
| 1 | HY-IG Spread (I19) | SPY (T1) | 2026-02-28 | Evan | `docs/analysis_brief_hy_ig_spy_20260228.md` | `results/` | Pages 1-4 | Yes (#20) |

*Add rows as analyses are completed. Priority column references the Priority Combinations Catalog (#).*

---

## Maintenance

- **Owner:** Alex (lead analyst) maintains the index; individual catalogs are updated by the relevant agent
- **Update frequency:** After each major analysis, review catalogs and add new discoveries
- **Deprecation:** Mark entries as `[DEPRECATED]` rather than deleting — future analyses may revisit
- **Version control:** All catalogs are tracked in git; use commit messages to document additions/removals

---
*Created: 2026-02-28*
*Last updated: 2026-03-14*
