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
| 3 | Building Permits → SPY | Completed | 7.0 | ~150K | 1.45 | 0.90 | 675 / 856 | Pro-cyclical confirmed; MoM+L6+P3 |
| 11 | VIX/VIX3M → SPY | Completed | 8.0 | ~150K | 1.13 | 0.77 | 332 / 916 | Strongest regime: Q1 6.53 vs Q4 -2.38. P/C proxy. |

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

### From Pair #3 (Building Permits → SPY) — MRA

**Measure:** 7.0s pipeline, ~150K tokens, Sharpe 1.45, 675/856 valid, pro-cyclical confirmed, 12/12 completeness gate.

**Review:**
- RoC/momentum wins for 3rd consecutive pair — now a confirmed pattern across Activity (INDPRO), Rates (TED), and Housing (Permits)
- Long/Short (P3) won for the first time — permits have strong enough signal for directional bets
- 6-month lead for monthly indicators is standard — consistent with INDPRO
- Regime differentiation modest (Q4 0.95 vs Q1 0.75) — permits are a better leading indicator than regime discriminator
- NumPy bool JSON serialization bug in pipeline template — needs `bool()` cast

**Adjust:**
- RoC-over-level is a **confirmed pattern** (3/3 pairs) — promote from observation to rule
- Long/Short (P3) is viable when signal is strong — don't exclude from tournament grid
- 6M lead is default for monthly indicators — codify in econometrics SOP

### From Pair #11 (VIX/VIX3M → SPY) — MRA

**Measure:** 8.0s pipeline, ~150K tokens, Sharpe 1.13, 332/916 valid, counter-cyclical confirmed, 11/11 completeness gate.

**Review:**
- **Strongest regime signal seen**: Q1 (contango) Sharpe 6.53 vs Q4 (backwardation) Sharpe -2.38. This 9-point Sharpe spread dwarfs all other pairs (INDPRO was 0.8, Permits was 0.2).
- VIX/VIX3M is daily and stationary — different dynamics from monthly macro indicators. L0 (no lead) won, unlike the L6 for monthly indicators. Makes sense: VIX is fast-moving, no publication lag.
- Z-score 126d won — shorter lookback than 252d. VIX term structure regimes are shorter-lived than macro cycles.
- Only 332/916 valid (36%) — lower validity rate than previous pairs (60-79%). VIX signal is noisy at daily frequency; many strategies don't survive OOS.
- Successfully used as **put/call ratio proxy** — when CBOE P/C data is unavailable, VIX term structure captures similar sentiment.

**Adjust:**
- Daily indicators: L0 is default (no publication lag). Contrast with monthly indicators (L6).
- Shorter z-score lookbacks (126d) for fast-moving indicators like VIX.
- Low validity rate (36%) is normal for daily noisy indicators — don't be alarmed.
- VIX regime quartiles are the best regime discriminator discovered — consider using as a universal control variable.

---

## Run: HY-IG v2 → SPY — 2026-04-19 (Waves 1–5, rules + portal retro-apply)

| Field | Value |
|-------|-------|
| **Pair** | HY-IG v2 → SPY (reference-pair polish sequence, not a new pair) |
| **Session date** | 2026-04-19 |
| **Waves executed** | Wave 1 (stakeholder ingestion + SOP Part F) → Wave 2A/2B (retro-apply to HY-IG v2 artifacts/charts/narrative + portal rebuild + acceptance verify) → Wave 3 (perceptual-validation bug fixes: NBER shading, Dot-Com canonical loader) → Wave 4A/4B/4C-1/4C-2/4D-1/4D-2/4E (schema contract standard + 5 schemas + consumer validation + verification) → Wave 5 (validation audits: 5 parallel agents + Lead system-level audit) → Wave 5B-1 (this) and 5B-2 (parallel) consolidate audit findings into new rules |
| **Commit sequence** | 12 commits `6bcb5e2` → `416ba94` covering Waves 1–4; Wave 5B dispatches in progress |
| **Force-redeploys** | **1** — commit `1720c0c` (Wave 4A, trivial `pair_registry` docstring bump to force Streamlit Cloud rebuild after observed stale-Cloud state). Logged in Force-Redeploy Log below. |
| **New rules added this session** | **22 total** across the session. Wave 5B-1 contribution (this dispatch): 7 new META/GATE rules — META-XVC, META-FRD, META-RPT, META-BL, META-SCV, META-ELI5, GATE-30. Earlier waves added APP-SE1..SE5, APP-ST1, APP-WS1, APP-SEV1, APP-DIR1; VIZ-V5, VIZ-V8; RES-7..11, RES-17, RES-VS; DATA-VS, DATA-D5, D6; ECON-DS2, ECON-E1, E2, H4, H5; META-ZI, META-PV, META-CF; GATE-27, 28, 29. |
| **Token estimate (this session)** | ~2M cumulative across the 5 parallel agent audits + Lead system-level audit + Wave 5B dispatches. Higher than a normal pair run because of audit depth + rule-authoring volume. |
| **Deferred items** | BL-001 (APP-SEV1-MAP — severity lookup JSON; Ace proposer; deferred to next sprint). Recorded in `docs/backlog.md` per META-BL. |
| **Reference-pair status** | `hy-ig-v2-reference-candidate` expected at end of Wave 5B consolidation; `hy-ig-v2-reference` awaits stakeholder sign-off per META-RPT. |

### Force-Redeploy Log (per META-FRD)

| commit_sha | trigger_reason | time_to_rebuild | observed_stale_element | lead_initials |
|------------|----------------|------------------|-------------------------|---------------|
| `1720c0c` | Streamlit Cloud served a `pair_registry`-cached landing-page state that did not reflect HEAD on main after the Wave 4A push; 7+ minutes elapsed since last push; Playwright inspection confirmed the delta. | Rebuild completed within ~5 minutes of the trivial-bump push. | Landing-page card grid missing the HY-IG v2 schema-validated chips (post-Wave 4A). | LL |
| `f7587a3` (dashboard reboot; no force-redeploy commit layered) | **Manual Reboot App via Cloud dashboard.** Triggered by: Lesandro. Reason: Cloud cache held pre-Wave-5C zoom chart JSON (Story "What History Shows" rendered 3 zoom charts with matplotlib-default red `#d62728` in `gd.data[0].line.color`); the committed `output/charts/hy_ig_v2_spy/plotly/history_zoom_*.json` files on `f7587a3` correctly declared Okabe-Ito `#D55E00`, confirming Cloud-side staleness rather than artifact error. | Rebuild completed within ~2 minutes of dashboard Reboot click. | Story page zoom charts (Dot-Com / GFC / COVID) served pre-Wave-5C palette. | LL |

**Quarterly count (2026-Q2):** 2 invocations — `1720c0c` (force-redeploy commit, Wave 4A) + `f7587a3` (dashboard Reboot App, Wave 5D). At the META-FRD threshold of 2/quarter; next invocation in 2026-Q2 triggers a root-cause investigation of Cloud caching behavior (chart-JSON bundle hashing vs. `pair_registry` docstring dependency).

#### Wave 5D Reboot Event — detailed entry (per META-FRD)

- **Event:** Manual Reboot App via Cloud dashboard
- **Triggered by:** Lesandro
- **Date/time:** 2026-04-19
- **Commit at Cloud HEAD:** `f7587a3` (Wave 5C)
- **Reason:** Cloud cache held pre-Wave-5C zoom chart JSON; committed files were correct but Cloud was stale.
- **Detection method:** Playwright DOM probe (`temp/cloud_wave5d_color_probe.py`) extracted `gd.data[0].line.color` from each `.js-plotly-plot` div on the Story page and found `#d62728` on the 3 zoom charts (Dot-Com / GFC / COVID) — the pre-Wave-5C matplotlib default, not the Okabe-Ito `#D55E00` declared in the on-disk artifacts.
- **Action taken:** Lesandro clicked "Reboot App" in the Streamlit Cloud dashboard for this app. No force-redeploy commit was layered on top, per META-FRD authority-of-dashboard-reboot.
- **Outcome:** Post-reboot re-verify (`temp/cloud_wave5d_rerun_story.py`) returned `#D55E00` on all 3 zoom charts. **PASS.** Full Wave 5D 9-item matrix cleared.
- **Screenshot:** `temp/cloud_wave5d_rerun_story.png`
- **DOM dump:** `temp/cloud_wave5d_rerun_dom.json`
- **Consequence:** Wave 5D Cloud Verification section appended to `results/hy_ig_v2_spy/acceptance.md` with all 9 items PASS and reboot disclosure.

### Wave 5B-1 MRA — Meta-Rule Authoring Session

**Measure:**

- 7 new rules authored in one dispatch (~500 lines of SOP text across team-coordination.md + standards.md).
- 1 new file created (`docs/backlog.md`).
- 1 existing file updated with session entry (this file).
- 1 regression note append (`results/hy_ig_v2_spy/regression_note_20260419.md`).
- Token usage for Wave 5B-1 dispatch only: ~60K input + ~10K output ≈ ~70K total.

**Review:**

- Rule-batching paid off. All 7 rules share the "make tribal knowledge artifact" pattern — force-redeploy discipline, reference-pair tagging, cross-version observation, backlog discipline, schema consumer version contract, ELI5 flag layer, deflection link audit. One Lead dispatch = one review pass = coherent cross-references.
- The 3 META rules that extend existing meta-principles (META-XVC extends VNC; META-SCV extends CF; META-ELI5 extends RES-1 / APP-SE5) slotted in cleanly. The 3 operational META rules (META-FRD, META-RPT, META-BL) are net-new mechanisms — these required more care on wording because they have no pre-existing frame.
- GATE-30 is interesting: it's a META-rule disguised as a GATE. The meta-clause ("if the deflection target page is later restructured, every deflection reference is automatically re-opened") is a cross-cutting property that the GATE machinery enforces per-pair. Future pairs will test whether the auto-reopen actually fires — the mechanism needs a trigger implementation (likely a `scripts/audit_deflections.py` helper that Lead runs on SOP/page restructures).

**Adjust:**

- **Next session** (Wave 5B-2 dispatches): confirm no cross-agent rule ID conflicts. Wave 5B-1 added `META-XVC`, `META-FRD`, `META-RPT`, `META-BL`, `META-SCV`, `META-ELI5`, `GATE-30`. Wave 5B-2 agent dispatches will add agent-specific rules (prefixed DATA / ECON / VIZ / RES / APP). No collisions expected since agent dispatches don't touch META / GATE blocks. Central commit at the end of Wave 5B consolidates both.
- **Wave 5C** (per META-ELI5 retroactive check): audit every `st.error` / `st.warning` / `st.info` in HY-IG v2 portal code and remediate gaps.
- **META-SCV implementation:** extend `app/components/schema_check.py` `validate_or_die` / `validate_soft` signatures with a `minimum_x_version` parameter. Non-trivial; schedule as its own Wave (likely 5D or a separate Ace dispatch).
- **META-RPT activation:** once the stakeholder signs off on HY-IG v2 acceptance, Lead creates the `hy-ig-v2-reference` annotated tag and pushes it. This will be the first live test of the META-RPT procedure.

---

*This document is maintained by Lesandro (lead analyst) and updated after each pair completes.*
