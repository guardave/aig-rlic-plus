# Pair Execution History

Tracks time, token usage, and results for each priority combination analysis run.

---

*Created: 2026-03-14*
*Last updated: 2026-03-14*

---

## Summary

| # | Pair | Status | Pipeline (s) | Token Est. | Best OOS Sharpe | BH Sharpe | Valid Combos | Notes |
|---|------|--------|-------------|------------|-----------------|-----------|-------------|-------|
| 1 | INDPRO → SPY | Completed | ~14.0 | ~400K | 1.10 | 0.90 | 1,150 / 1,666 | Counter-cyclical z-score surprise |
| 2a | SOFR-DTB3 → SPY | Completed | 14.4 (3 combined) | ~200K (shared) | 1.89 | 1.41 | 580 / 991 | Short OOS (3yr), inflated Sharpe |
| 2b | DFF-DTB3 → SPY | Completed | (shared) | (shared) | 0.97 | 0.77 | 388 / 991 | Most robust; long history |
| 2c | Spliced TED → SPY | Completed | (shared) | (shared) | 1.19 | 0.77 | 598 / 991 | TEDRATE + affine-adjusted DFF-TED |

---

## Detailed Run Logs

### Run #1: INDPRO → SPY

| Field | Value |
|-------|-------|
| **Pair #** | 1 (from priority-combinations-catalog.md) |
| **Indicator** | Industrial Production (2017=100) |
| **Indicator ID** | I1 / INDPRO |
| **Target** | S&P 500 (SPY) |
| **Start time** | 2026-03-14T02:15:00Z |
| **End time** | 2026-03-14T02:30:00Z |
| **Status** | Completed |
| **Analysis Brief** | `docs/analysis_brief_indpro_spy_20260314.md` |
| **Pipeline script** | `scripts/pair_pipeline_indpro_spy.py` |

#### Pipeline Timing

| Stage | Duration (s) | Notes |
|-------|-------------|-------|
| 1. Data sourcing | 5.7 | 6 FRED + 2 Yahoo series |
| 2. Alignment + derived | 0.1 | Monthly + daily datasets, 11 derived series |
| 3. Stationarity + quality | 1.9 | ADF + KPSS on 10 variables |
| 4. Exploratory | 0.1 | 64 correlations, 25 CCF lags, 4 regime quartiles |
| 5. Core models | 1.9 | 7 model types, 45+ parameter estimates |
| 6. Tournament | 3.0 | 1,666 combinations |
| 7. Validation | 0.2 | Bootstrap, stress tests, tx cost sensitivity |
| 8. Chart generation | ~1.0 | 10 Plotly JSON charts via `scripts/generate_charts_indpro_spy.py` |
| 9. Portal pages | — | 4 Streamlit pages (Story, Evidence, Strategy, Methodology) |
| 10. Landing page | — | Redesigned as filterable card grid with pair registry |
| 11. Browser inspection | — | Playwright headless: screenshot + DOM text check per page |
| 12. Rendering fixes | — | Raw HTML in cards → native st.metric; raw MD in narratives → st.markdown |
| **Total pipeline** | **~14.0** | (stages 9-12 are token cost, not wall-clock) |

#### Token Usage Estimate

| Component | Estimated Tokens |
|-----------|-----------------|
| Analysis Brief creation | ~30K |
| Pipeline script creation | ~100K |
| Pipeline execution (Bash) | ~5K |
| RF fix + re-run | ~15K |
| Chart generation script + run | ~30K |
| Portal pages (4 pages + sidebar + landing) | ~50K |
| Browser inspection (Playwright install + inspect) | ~20K |
| Rendering fixes (cards + narratives) | ~30K |
| Documentation updates | ~20K |
| Context (SOPs, catalogs, templates) | ~80K |
| **Total for pair #1** | **~400K** |

Note: Pair #1 includes one-time costs (pipeline script ~100K, landing page redesign ~30K, Chromium install ~10K, rendering fixes ~30K) that won't repeat. Subsequent pairs will reuse the pipeline pattern, estimated at ~120-180K tokens each (brief + pipeline + charts + portal pages + browser verification).

#### Key Results

| Metric | Value |
|--------|-------|
| Monthly dataset | 432 rows × 23 columns (1990-01 to 2025-12) |
| Daily dataset | 9,393 rows × 16 columns |
| Econometric models run | 7 types (Granger, OLS, LP, Regime LP, Markov-Switching, Quantile Reg, Cointegration, Change-Point, RF) |
| Tournament combinations | 1,666 |
| Valid strategies (OOS Sharpe>0, turnover<24) | 1,150 (69%) |
| Best OOS Sharpe | 1.10 (INDPRO 3M momentum, fixed P75 threshold, Long/Cash, L6) |
| Buy-and-hold Sharpe | 0.90 |
| Best max drawdown | -8.1% (vs -23.9% buy-hold) |
| RF walk-forward accuracy | 61.4% (20 windows) |

#### Key Findings

1. **Direction surprise:** Expected pro-cyclical, but z-score shows *counter-cyclical* at extremes (coef=-0.020, t=-2.69, p=0.007). Interpretation: when IP is far above trend, mean-reversion → lower future returns. This is a **peak-cycle** effect.

2. **Regime effect:** Quartile analysis shows Sharpe is highest in Q4_high (1.15) and Q2 (1.09), lowest in Q1_low (0.31). Stocks perform best during moderate-to-high IP growth, worst during severe contraction.

3. **Best signal:** 3-month IP momentum with 6-month lead time — OOS Sharpe 1.10, max drawdown only -8.1% vs -23.9% buy-hold.

4. **Granger causality:** Mixed results. INDPRO→SPY not strongly significant at standard lags. Consistent with IP being a coincident (not leading) indicator — the 6-month lead in the winning strategy likely captures the publication lag effect.

5. **Change points:** 4 structural breaks detected in IP YoY growth.

6. **Cointegration:** Log(INDPRO) and log(SPY) — trace statistic (12.0) below critical value at 95% (15.5). No long-run equilibrium found at conventional levels.

#### Output Files

```
data/indpro_spy_monthly_19900101_20251231.parquet
data/indpro_spy_daily_19900101_20251231.parquet
data/summary_stats_indpro_spy_20260314.csv
data/missing_value_report_indpro_spy_20260314.md
results/indpro_spy/stationarity_tests_20260314.csv
results/indpro_spy/interpretation_metadata.json
results/indpro_spy/pipeline_timing_20260314.json
results/indpro_spy/exploratory_20260314/correlations.csv
results/indpro_spy/exploratory_20260314/ccf.csv
results/indpro_spy/exploratory_20260314/regime_descriptive_stats.csv
results/indpro_spy/core_models_20260314/granger_causality.csv
results/indpro_spy/core_models_20260314/predictive_regressions.csv
results/indpro_spy/core_models_20260314/local_projections.csv
results/indpro_spy/core_models_20260314/regime_local_projections.csv
results/indpro_spy/core_models_20260314/markov_switching_2state.csv
results/indpro_spy/core_models_20260314/markov_regime_probs_2state.csv
results/indpro_spy/core_models_20260314/quantile_regression.csv
results/indpro_spy/core_models_20260314/cointegration.csv
results/indpro_spy/core_models_20260314/change_points.csv
results/indpro_spy/core_models_20260314/rf_walk_forward.csv
results/indpro_spy/core_models_20260314/rf_feature_importance.csv
results/indpro_spy/core_models_20260314/diagnostics_summary.csv
results/indpro_spy/tournament_results_20260314.csv
results/indpro_spy/tournament_validation_20260314/bootstrap.csv
results/indpro_spy/tournament_validation_20260314/stress_tests.csv
results/indpro_spy/tournament_validation_20260314/transaction_costs.csv

# Visualization (10 Plotly JSON charts)
output/charts/indpro_spy/plotly/indpro_spy_hero.json
output/charts/indpro_spy/plotly/indpro_spy_regime_stats.json
output/charts/indpro_spy/plotly/indpro_spy_correlations.json
output/charts/indpro_spy/plotly/indpro_spy_ccf.json
output/charts/indpro_spy/plotly/indpro_spy_local_projections.json
output/charts/indpro_spy/plotly/indpro_spy_quantile_regression.json
output/charts/indpro_spy/plotly/indpro_spy_tournament_scatter.json
output/charts/indpro_spy/plotly/indpro_spy_equity_curves.json
output/charts/indpro_spy/plotly/indpro_spy_granger.json
output/charts/indpro_spy/plotly/indpro_spy_rf_importance.json

# Portal pages
app/pages/5_indpro_spy_story.py
app/pages/5_indpro_spy_evidence.py
app/pages/5_indpro_spy_strategy.py
app/pages/5_indpro_spy_methodology.py

# Supporting infrastructure (one-time, reused by future pairs)
app/components/pair_registry.py
scripts/generate_charts_indpro_spy.py
temp/inspect_portal.py
```

---

## Cost Projections (After 1 Pair)

| Metric | Value |
|--------|-------|
| Pair #1 tokens (including one-time costs) | ~400K |
| One-time infrastructure costs included | ~170K (pipeline script, landing page, Chromium, rendering fixes) |
| Estimated per-pair (recurring) | ~130-180K (brief + pipeline + charts + 4 pages + browser verify) |
| Estimated total for 73 pairs | ~10-13M tokens |
| Pipeline wall-clock per pair | ~14s |
| Estimated total pipeline wall-clock | ~17 min (73 × 14s) |
| Total wall-clock including brief + docs + viz + verify | ~5-8 min per pair → ~6-10 hours for 73 |

### Per-Pair Recurring Cost Breakdown (estimated)

| Step | Tokens | Notes |
|------|--------|-------|
| Analysis Brief | ~15K | Fill template with pair-specific parameters |
| Pipeline script adaptation | ~20K | Adapt from INDPRO template for new indicator |
| Pipeline execution | ~5K | Bash run + output review |
| Chart generation script + run | ~15K | Adapt chart script + execute |
| Portal pages (4 pages) | ~40K | Story, Evidence, Strategy, Methodology |
| Browser verification | ~10K | Playwright inspect + any rendering fixes |
| History + catalog updates | ~10K | Update tracking docs |
| Context overhead | ~15K | Reading SOPs, catalogs, existing code |
| **Total per pair** | **~130K** | Lower bound; complex pairs may be ~180K |

---

## Lessons Learned

### From Pair #1 (INDPRO → SPY)

**Econometric insights:**
1. **Direction can surprise.** Expected pro-cyclical, found counter-cyclical z-score at extremes. Always run the analysis before assuming direction — the peak-cycle mean-reversion effect was not in the prior.
2. **Monthly indicators need longer lead times.** The winning strategy used a 6-month lead — much longer than the 0-5 day leads that worked for daily HY-IG. Publication lag + economic response time matters.
3. **Granger causality is weak for coincident indicators.** IP is coincident, not leading. Don't expect strong Granger results. The predictive power comes from momentum and regime effects.
4. **Cointegration is not guaranteed.** Log(INDPRO) and log(SPY) failed the Johansen test. Don't assume all macro indicators cointegrate with equity prices.

**Portal/viz insights:**
5. **Streamlit `st.markdown(unsafe_allow_html=True)` is unreliable for nested HTML.** Use native components (st.container, st.metric, st.columns) instead.
6. **Markdown inside HTML div wrappers renders as raw text.** Fixed render_narrative() to use plain st.markdown().
7. **`st.metric` truncates in narrow columns.** Use markdown tables for compact data display.
8. **Headless browser verification is essential.** Added to SOP as mandatory step after portal assembly.

**Process insights:**
9. **One-time infrastructure costs are high for pair #1 (~170K tokens).** Subsequent pairs reuse scripts, landing page, components — ~130K/pair.
10. **The pipeline script template is the key reusable artifact.** Future pairs adapt `pair_pipeline_indpro_spy.py` with different data sources and derived series.
11. **Chart generation should be a separate script per pair** (not inline in the pipeline). This allows re-running viz without re-running models.
12. **Always update tracking docs at every stage**, not just at the end. Missed viz tracking on first pass.

### SOP Updates Applied

| SOP | What Changed | Why |
|-----|-------------|-----|
| team-coordination.md | Added Step 7 (browser verification) to task flow; added Iterative Review section with Playwright protocol | Rendering bugs invisible in Python code |
| visualization-agent-sop.md | Added Viz Preferences section: 10 standard charts, color palette, naming convention, Streamlit rendering rules | Standardize chart set across pairs; prevent rendering bugs |
| appdev-agent-sop.md | Added Streamlit Rendering Rules to architecture rules | Prevent HTML/markdown rendering failures |
| All SOPs | Renamed Alex → Lesandro | Lead analyst name change |

### From Pair #2 (TED Variants → SPY) — MRA

**Measure:**
- 3 variants, 14.4s combined pipeline, ~200K tokens (shared data sourcing)
- SOFR-DTB3: Sharpe 1.89 (OOS 3yr only — high variance), DFF-DTB3: 0.97 (robust), Spliced: 1.19
- Rate-of-change signals won across all 3 variants
- No portal rendering issues (prior fixes held)

**Review:**
- SOFR and LIBOR-based TED measure fundamentally different risks (r=-0.04). The splice investigation was essential.
- DFF-DTB3 is the canonical TED proxy (r=+0.63 with TEDRATE). Should be default going forward.
- Short-OOS inflates Sharpe — Variant A's 1.89 is not trustworthy with only 3 years.
- "Variant family" pattern (one indicator question → multiple measurement approaches) is powerful and should be formalized.
- Analysis brief was written before splice analysis — should update brief post-analysis for completeness.

**Adjust:**
- Rate-of-change > level signals: consistent finding across INDPRO and TED variants. *Change in conditions* matters more than *level of conditions*.
- Short-OOS flag needed: when OOS < 5 years, auto-flag the Sharpe as "high variance, interpret with caution".
- Variant family pattern: when an indicator has measurement alternatives (predecessor/proxy/derived), run all variants in one pipeline. Document the choice rationale in the Story page.
- 3 TED variants count as 1 priority pair (#2), not 3. Sidebar and tracking reflect this.

### From Pair #2 Post-MRA: Missing Methodology Page

**What happened:** TED variants shipped with 3 portal pages (Story, Evidence, Strategy) but no Methodology page. The developer consciously skipped it as a "shortcut" and routed Methodology links to the Strategy page.

**Root cause:** No deliverables completeness check in the SOPs. Browser verification caught rendering bugs but not missing pages. The Analysis Brief checklist was passive (no one verified it at the end).

**Fix:** Added **Step 8: Deliverables Completeness Gate** to team-coordination SOP with a 15-item checklist. Added "All 4 page types exist" as first item in AppDev Quality Gates.

### SOP Updates Applied (Pair #2)

| SOP | What Changed | Why |
|-----|-------------|-----|
| team-coordination.md | Added MRA (Step 9, renumbered); added Deliverables Completeness Gate (Step 8) with 15-item checklist | Missing Methodology page; no completeness verification existed |
| appdev-agent-sop.md | Added "All 4 page types exist" as first quality gate item | Prevent page omission shortcuts |
| memory | Added MRA feedback memory | Persist across sessions |

---

*This document is maintained by Lesandro (lead analyst) and updated after each pair completes.*
