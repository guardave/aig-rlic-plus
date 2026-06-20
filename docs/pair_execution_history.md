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

---

### 2026-04-19 Wave 6D — Cloud file-sync stale on Wave 6 commit (17a73ce)

Moved 9 files from `output/_comparison/` → `output/charts/hy_ig_v2_spy/plotly/`; 
Cloud served new page code but old file tree → zoom charts rendered as 
"chart pending" placeholders. Resolved via manual Reboot App. 

**Third incident this quarter** — above META-FRD 2/quarter threshold. 
Escalation candidate for backlog: file-moves under `output/` don't reliably 
trigger Cloud's change-detection for non-`app/` paths. 

Future pair work should consider: (a) dual-step moves (land new → wait → 
confirm → delete old), or (b) per-pair-subdir-only pattern avoiding moves.

---

### 2026-05-26 — Pair (TBD) Gold/Copper Ratio → XLI — Work Mode Selection

**Per LEAD-WM1.**

- **Lead recommendation:** Mode 1 (multiple makers, single checker). Reasoning:
  - Gold/copper ratio is a new indicator category (not in existing rates / credit / production / sentiment / volatility buckets). Likely needs a new episode_registry.json slug family.
  - Medium-to-high SOP-rule risk: symbol selection (GC=F vs GLD vs LBMA; HG=F vs CPER), ratio transform (level / log / RoC / quantile rank), and "gold/copper stress" episode definitions are candidate rule sources where agent-authored reflection produces more authentic SOP additions than retro-fitting.
  - XLI target is clean; depth lives on the indicator side, where Dana's symbol judgment and Evan's specification judgment carry weight.
- **User decision:** Mode 2 (single maker, multiple checkers). Lead executes as maker; four checker subagents fan out post-flow.
- **Rationale for the override:** exercising the Mode 2 protocol on a non-trivial pair is itself a meta-goal — shaping the checker-dispatch artifact organically per the LEAD-WM1 design note.

Outcome (checker iteration count, issues per dimension, final clean wave) to be appended on completion.

### 2026-05-26 — Pair gold_copper_xli — Mode 2 COMPLETE

**Mode:** 2 (single maker, multiple checkers). Recommendation vs. choice: Lead recommended Mode 1; user overrode to exercise the protocol on a non-trivial pair.

**Maker phase (Lead wearing 5 role hats sequentially across 2 sessions):**
- Phase 1 Dana: 4.7s pipeline, 6783×39 parquet + schema + dictionary + interpretation_metadata + new `commodity_ratio` episode registry category.
- Phase 2 Ray: substantive ~220-line narrative + 4 HZE1 episode narratives (triad satisfied: gfc=long-lead, china_2015=mid-cycle, rates_2022=failure-case).
- Phase 3 Evan: 10.8s, 90-combo tournament. Winner = `gold_copper_zscore_126d <= -0.0334`, Long/Cash, no lead. **OOS Sharpe 1.27, ann return 13.4%, max DD -8.2%**. Direction countercyclical, consistent.
- Phase 4 Vera: 19.8s, essential 11-chart subset (33 files inc. perceptual PNGs + sidecars). VIZ-DP1 and GATE-VIZ-NBER2 verified by construction.
- Phase 5 Ace: pair_config + 4 page wrappers + registry edits. smoke_loader passes=4 failures=0.

**Checker swarm (4 parallel Explore agents):**
- Correctness: **PASS**, with one material catch — winner-signal mismatch (narrative+config cited 252d/Long-Short; actual winner is 126d/Long-Cash). This was a Mode-2-specific bug introduced when Ray hat (Phase 2) wrote strategy ELI5 before Evan hat (Phase 3) ran the tournament.
- Completeness: **PASS** (15/15 gate; deferred items properly documented).
- Consistency: **PASS** (missed the winner mismatch — Correctness owned it).
- ELI5: **PASS-WITH-NOTES** (z-score / Sharpe / 252d / 63d parentheticals; ONE_SENTENCE_THESIS reframe).

**Iteration 1 fixes:** corrected all winner-signal references throughout pair_config + narrative + caveats + trade-log example. Added ELI5 parentheticals on first use of z-score / Sharpe. Smoke loader re-passed (4/0).

**Iteration count:** 1 (single round of fixes; no second dispatch needed since non-Correctness checkers were already PASS).

**Mode 2 observations:**
- *Hope confirmed:* one-head execution preserved cross-stage context (Dana's provisional correlation → Ray's mechanism narrative → Evan's quartile result → Vera's NBER2-aware shading → Ace's caveats) without handoff overhead.
- *Risk validated:* writing strategy ELI5 in Phase 2 before running Phase 3 produced a placeholder-vs-reality mismatch that propagated through Phase 5. The checker swarm caught it — the protocol's safety net worked as designed.
- *Cost vs. Mode 1:* roughly comparable in tokens. Single-session impossible for a non-trivial pair (took 2 sessions); per-phase staging is the right cadence.
- *Best Mode 2 fit:* recurring pairs in familiar categories where the playbook is established and the checker swarm catches the few "wrote ahead of evidence" slips. Worst fit: novel categories where domain depth from agent reflection matters (Lead correctly recommended Mode 1 here; user chose Mode 2 as a protocol-exercise meta-goal).

**Final artifacts:** all under `results/gold_copper_xli/`, `output/charts/gold_copper_xli/`, `app/pair_configs/gold_copper_xli_config.py`, `app/pages/16_gold_copper_xli_*.py`, `docs/portal_narrative_gold_copper_xli_20260526.md`, `scripts/{pair_pipeline,econ_pipeline,generate_charts}_gold_copper_xli.py`.

**Honest re-classification of "deferred" items** (added 2026-05-26 after user challenged the framing):

The initial close lumped four very different categories under one "deferred" bucket. Re-classifying:

1. **Trivially completable from existing artifacts (was budget cut, not principled scope).** Charts: `granger_f_by_lag` (data already in granger_by_lag.csv), `walk_forward`, `drawdown_comparison`, `tournament_sharpe_dist`, `ccf_prewhitened`, `returns_by_regime`, `spread_history_annotated`. Estimated cost: one Vera-hat dispatch (~20 min wall-clock for 6-7 plotly figures + sidecars + perceptual PNGs). **Honest cause:** Phase 4 token-budget caution, not analytic principle. Calling these "scoped out" was a polite framing.

2. **Genuinely new econometric work (real scope cut from Phase 3).** HMM 2-state regime probabilities (`hmm_regime_probs` + REGIME-HMM evidence block); local projections / Jordà impulse responses (`local_projections` + LP evidence block); quantile regression at lower tail (`quantile_regression` + QR evidence block); transfer entropy non-linear lead-lag (`transfer_entropy` + TE evidence block). **Honest cause:** Phase 3 Evan hat shipped only correlation/Granger/quartile — the other 4 methods were not run. These are genuine analytical gaps, not chart-rendering gaps. HMM in particular would let the Evidence page validate the rates_2022 failure case as a distinct inferred regime, which is interpretively powerful.

3. **ELI5 polish (nice-to-have).** Visual callouts around 2022 failure case; split one long sentence in EVIDENCE_METHOD_BLOCKS overview; 63-day window parenthetical (252-day was added in iteration 1).

4. **Evan's analyst_suggestions.json** — genuinely future ideas, not gaps: log-ratio signals, DXY-conditional gating, supply-decoupling detector. Forward-looking suggestions, not deferred deliverables.

**Decision (2026-05-26, user):** complete categories 1 + 2 + 3 in this session (Phases 3.5, 4.5, 5.5 + ELI5 polish). Category 4 (Evan suggestions) discussed later.

### 2026-06-12 — Pair busloans_spy (Commercial & Industrial Loans → SPY) — Work Mode Selection

**Pair:** `busloans_spy` — priority combination #19 (I20 = FRED BUSLOANS, monthly, $bn, SA) × SPY. Branch `fix260612_busloans_spy`.

**LEAD-DV1 finding at SOD:** the Data Master's "C&I Loan" sheet is NOT loan volumes — Pre-master row 2 identifies it as the SLOOS Net % of Banks Tightening Standards (C&I, small firms; percent, quarterly, NSA). The `indicator_map.yaml` "C&I Loan" → `ci_loan` entry mislabels that survey as "Commercial & Industrial Loans"; `prospective_pairs.csv` ci_loan rows inherit the mislabel. Resolution: this pair uses NEW indicator_id `busloans` (FRED fetch by Dana); the `ci_loan` mislabel is corrected in the same wave (Dana's lane). Two distinct series stay distinct ids per LEAD-DV1.

**Lead recommendation: Mode 1.** Reasons: (a) new sub-category — bank-credit QUANTITY aggregate vs the existing credit-SPREAD pair (hy_ig); (b) genuine method-selection depth needed — C&I loans are famously lagging/coincident (credit lines drawn into downturns; loan growth peaks after recessions start), so direction may surprise (INDPRO z-score precedent) and trend-dominated levels demand careful transform choice; (c) first NEW pair under the full current standards stack (META-CMP gates, ECON-SR1, ECON-T4, DPS-SCD1/VIZ-SCD1, VIZ-QR1, DPS-LF1, downloads, CP-on-Confidence) — SOP-friction findings likely, and Mode-1 agent reflection is how rules get written authentically; (d) precedent — crude_oil_xle (Mode 2, new category) produced the W0.5 defect class; the 2026-06-11 Mode-1 wave produced 5-bugs-beyond-dispatch verification depth.

**User decision: Mode 1** ("Go", 2026-06-12).

**Pipeline plan:** Dana (BUSLOANS fetch + validation + ci_loan mislabel fix) → Evan (econometrics + tournament per ECON-SR1/T3/T4) → Vera + Ray (charts + narrative) → Ace (portal assembly) → Quincy (GATE-DPS1 + cloud verify). All under the active pre-commit hook.

### 2026-06-12 — Pair busloans_spy — Mode 1 COMPLETE (pending merge)

**Pipeline:** Dana (`0994310`) → Evan (`168a0d0`, `cf9e314` evidence_status) → Vera (`949a113`) ∥ Ray (`fc315b2`+) → Ace (`0008aa3`, QA-1 fix `d8d656b`) → Quincy (`beea4c1`, re-verify `1d43768` READY). Lead: rules (META-A2A first live wave; RES-20 lagging-pair variant), dispositions, waiver below.

**Verdict shipped:** BUSLOANS LAGS SPY (reverse-only Granger, all methods corroborate). Winner = defensive counter overlay (long SPY only in bottom-quartile lagged MoM loan growth, L6): search-phase OOS Sharpe 1.50 vs 0.89 B&H, DD −1.0%, rank 1/4,396, no ties — with non-negotiable fragility disclosure (bootstrap p=0.066 n.s.; IS 0.35; episode-concentrated; median 0.74 < B&H 0.89). **First live instance of DPS-FE2 routing** (`evidence_status.json` = `found_in_search`; "Search-phase OOS Sharpe (no holdout test yet)" labels; plain_english disclosure box).

**DPS-PRE1 waiver (Lead, this wave):** sole GATE-DPS1 FAIL is the final-exam prerequisite — waived because no holdout has been run BY DESIGN (found_in_search status + prominent disclosure is the compensating control). ECON-FE1 final-exam path documented in `evidence_status.next_step` as the pair's next milestone.

**Process notes:** LEAD-DV1 caught the Data-Master "C&I Loan" mislabel (SLOOS survey, not loan volumes) before any data was fetched — `ci_loan` corrected, `busloans` registered distinct. META-A2A's first wave: zero relay round-trips needed (producer artifacts self-documented); 2 A2A-candidate escalations (episode-slug vocabulary → BL-EPISODE-SLUGS; both handled by Lead). One blocking QA defect (QA-1 manifest-sidecar glob collision — first pair carrying META-CMP manifest sidecars) found by Quincy's DOM sweep, fixed by Ace with byte-identical legacy regression proof, re-verified READY. Checker iteration count: 1.

**Mode-1 recommendation vs outcome:** recommended Mode 1 for novelty + lagging-direction depth + first-pair-under-new-stack; outcome validates — Evan's reverse-only verdict reshaped the entire narrative frame (a Mode-2 single head with a bullish prior might have buried it), and the honest-framing chain (evidence_status → RES-CAP1 → DPS-FE2 routing) exercised three dormant standards for the first time.

---

## Lead-Horizon Wave (fix260613_lead_horizon) — ECON-LL1/LA1/LT1 gate, all 9 active pairs

**Dispatch:** Lead Analysis + Lead Tournament on the universal monthly lead grid L=0..12 (ECON-LL1) for every active pair; per-pair conditional-re-run gate decision (ECON-LT1). Analysis + decision only — NO re-runs / winner changes this dispatch. Producer: `scripts/lead_horizon_sweep.py` (seed=42; daily pairs resampled to month-end). Artifacts per pair: `results/{pair}/lead_correlation_20260613.csv`, `lead_tournament_20260613.csv`, `lead_sweep_manifest_20260613.json` (frozen Sample routed to `results/_cross_agent/hy_ig_v2_spy_lead_readonly/` — its own dir untouched).

| pair | published winner lead | L* (best-Sharpe lead, L0..12) | best Sharpe @ L* | published Sharpe | decision | rationale |
|------|:--:|:--:|:--:|:--:|:--|:--|
| indpro_spy | 6 | 12 | 1.374 | 1.104 | **RE-RUN** | L*∈{7..12} and 1.374 > 1.104 — extended grid finds a better long-lead winner the legacy {0,1,2,3,6} grid missed |
| permit_spy | 6 | 6 | 1.445 | 1.445 | CHARTS-ONLY | max Sharpe stays L=6 (reproduces vichua); L8-10 is a lower-Sharpe, lower-DD ridge, not a higher-Sharpe winner |
| vix_vix3m_spy | 0 | 3 | 1.869 | 1.130 | CHARTS-ONLY | L*=3 ∈ {0..6}; published winner's lead region still wins, no re-run |
| indpro_xlp | 3 | 8 | 1.423 | 1.115 | **RE-RUN** | L*∈{7..12} and 1.423 > 1.115 |
| hy_ig_spy | 0 | 1 | 1.439 | 1.408 | CHARTS-ONLY | L*=1 ∈ {0..6}; near-tie with published, winner region unaffected |
| umcsent_xlv | 6 | 11 | 1.188 | 1.020 | **RE-RUN** | L*∈{7..12} and 1.188 > 1.020 |
| gold_copper_xli | 0 | 10 | 1.370 | 1.273 | **RE-RUN** | L*∈{7..12} and 1.370 > 1.273 |
| busloans_spy | 6 | 5 | 1.500 | 1.500 | CHARTS-ONLY | L*=5 ∈ {0..6}; best @ L5 ties published L6 winner family, winner region unaffected |
| hy_ig_v2_spy (FROZEN Sample) | 0 | 2 | 1.546 | 1.274 | CHARTS-ONLY | L*=2 ∈ {0..6}; analysis read-only, decision recorded, NO write to its dir, NO re-run regardless |

**Summary:** 4 RE-RUN candidates (indpro_spy, indpro_xlp, umcsent_xlv, gold_copper_xli — all L*∈{7..12} beating the published winner), 5 CHARTS-ONLY. Re-runs are a SEPARATE Lead-checkpointed dispatch; none performed here. permit_spy confirms vichua's published finding (max Sharpe L=6 → CHARTS-ONLY). Frozen Sample handled read-only.

**Caveat (Lead to weigh before authorising re-runs):** the lead grid uses a *generic standardised* (threshold × strategy) backtest harness — fixed/rolling percentile + rolling-z thresholds, P1 long/cash + P2 long/short, both signal polarities, 1-month execution shift — re-run identically at every lead. It is the correct *apples-to-apples* lead comparator (only the lead axis varies), and it reproduces permit_spy's published winner (L6, 1.4454) and busloans (L6, 1.4999) from raw data. But the absolute best-Sharpe at L* for a RE-RUN pair must be re-confirmed against that pair's *native* tournament machinery (which may carry pair-specific signals/thresholds/lookbacks not in the generic grid) before any winner is cascaded. The gate decision (which lead region wins) is robust; the headline Sharpe at L* is harness-comparator, to be reconciled at re-run time per ECON-SR1.
