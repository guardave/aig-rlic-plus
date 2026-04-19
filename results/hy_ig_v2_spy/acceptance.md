# Acceptance — hy_ig_v2_spy — 2026-04-14 (Wave 1) / 2026-04-19 (Wave 2)

**Gate item:** GATE-23 (Pair Acceptance Checklist)
**Pre-stakeholder draft.** Stakeholder review pending; Lead sign-off contingent on stakeholder approval.

**Latest verified commit:** `1f864e8` — SOP Part F Wave 2B: HY-IG v2 portal rebuild (2026-04-19)
**Upstream Wave 2A:** `b9730cb` — artifacts, charts, narrative
**Upstream Wave 1.5:** `b7ee4ba` — coherence-review patches
**Upstream Wave 1:**   `6bcb5e2` — 2026-04-18 stakeholder feedback
**Cloud verified:** 2026-04-19 via Playwright headless (chromium) against https://aig-rlic-plus.streamlit.app/ — see `temp/cloud_wave2_*.png` and `temp/cloud_wave2_results.json`.

---

## Portal-Wide Quality Checklist

Per `docs/agent-sops/team-coordination.md` Portal-Wide Quality Checklist section.

### Landing Page
- [x] Pair appears as card in filtered view with classification chips (Leading / Credit / Min MDD / Counter-cyclical) — verified Cloud landing page
- [x] Performance badges color-coded (Sharpe 1.27 green, Max DD -10.2% amber)
- [x] Card renders without truncation at 1280×900

### Navigation
- [x] Breadcrumb component renders on all 4 pages (Story → Evidence → Strategy → Methodology)
- [x] Sidebar finding selector includes hy_ig_v2_spy
- [x] All Story/Evidence/Strategy/Methodology page_links work

### Story Page
- [x] Hero chart: dual-panel layout, no inversion, axis labeled "Spread (bps, where 100 bps = 1%)" with values in 147-1531 bps range
- [x] KPI strip with interpretation captions (5 KPIs: Lead Time, GFC Spread Peak, Predicted Drawdowns, Strongest During, OOS Test Period)
- [x] "Where This Fits in the Portal" opener echoes landing exec summary themes (N1)
- [x] "Why this indicator?" context sections present with Merton model and CCC-BB quality spread expanders
- [x] Plain English expander at top (N8)

### Evidence Page
- [x] 8-element template applied to all 8 method blocks
- [x] Difficulty tiers: Level 1 (Correlation, Granger, CCF) and Level 2 (Local Projections, Regime, Quantile, Transfer Entropy, Quartile Returns) (N11)
- [x] "Why we chose this method" rationale present in each block's Method element
- [x] Charts use canonical short names (correlation_heatmap, hmm_regime_probs, etc.) per VIZ-A3
- [x] Unit discipline: heatmap axis labels disclose scale; CCF lag axis labeled in days
- [x] Plain English expander at top (N8)
- [x] Quartile Returns "Why this matters" opener present (N6)

### Strategy Page
- [x] Trading Rule in Plain English appears FIRST (rule-first ordering)
- [x] "How to Use This Indicator Manually" subsection present with 3-step routine + 2020 COVID example + caveats (N2, N4)
- [x] "Execution Points — Actual Trigger Dates" table with 8 historical events (N3)
- [x] KPI cards with interpretation captions
- [x] OOS Return labeled as "OOS Return (arithmetic ann.)" with tooltip (N13)
- [x] Trade log: broker-style CSV (418 rows) + column legend expander + dual download + 10-row preview
- [x] "How to Read the Trade Log" narrative subsection with COVID 2020 concrete example
- [x] Tournament leaderboard shows top 20 + "Explore Alternative Strategies" selector with per-strategy metric comparison (N12)
- [x] Plain English expander at top (N8)

### Methodology Page
- [x] Skeptical reader framing in intro
- [x] Methods table with rationale columns
- [x] Diagnostics summary present
- [x] "References" section with 17-entry bibliography organized into 4 categories (N7)
- [x] Inline [AuthorYear] citations link to bibliography
- [x] Plain English expander at top (N8)
- [x] Return Basis explanation note (CAGR vs arithmetic) present (N13 cross-page)

### Cross-Cutting
- [x] Dual notation (bps + %) on first use of unit-laden values per RES-B1
- [x] Plain English expanders on all 5 narrative pages per N8
- [x] Writing voice consistent across pages (financially-literate-non-quant baseline + plain-English layer)
- [x] Honest caveats present on Strategy page ("Honest assessment", "Important Caveats", caveats in How to Use Manually)
- [x] Regression note `regression_note_20260411.md` documents all changes with Approved By + Unchanged + Impact sections

---

## Wave 2 Verification (2026-04-19)

Wave 2 (commits `b9730cb` Wave 2A + `1f864e8` Wave 2B) closes the 2026-04-18 stakeholder feedback batch (S18-*) and the Lesandro reference-pair items (SL-*). Verified via Playwright headless cloud verification on 2026-04-19. Wave 1 (`6bcb5e2`) and Wave 1.5 (`b7ee4ba`) precede it; the Wave 1 / pre-stakeholder checklist above remains satisfied.

### New Standard Components (Strategy Page)

- [x] **APP-SE1 — Probability Engine Panel** renders on Execute tab (verified Cloud, screenshot `temp/cloud_wave2_strategy_tab_execute.png`)
- [x] **APP-SE2 — Position Adjustment Panel** renders, gated on SE1 validation (verified Cloud)
- [x] **APP-SE3 — Instructional Trigger Cards** render under Probability/Position panels (verified Cloud)
- [x] **APP-SE4 — Future: Live Execution** section renders at bottom of Strategy page with 3 metric placeholders (verified Cloud, screenshot bottom of `temp/cloud_wave2_strategy.png`)
- [x] **APP-SE5 — Confidence-tab one-line takeaway captions** render under each chart/table on Confidence tab (verified Cloud, screenshot `temp/cloud_wave2_strategy_tab_confidence.png`)

### Wave 2 Artifacts (results/hy_ig_v2_spy/)

- [x] `granger_by_lag.csv` — F-statistic by lag table (closes S18-11) — present
- [x] `regime_quartile_returns.csv` — quartile returns by HMM regime — present
- [x] `regime_quartile_returns_methodology.md` — methodology note — present
- [x] `winner_trades_broker_style.csv` — broker-style trade log — present
- [x] `regression_note_20260419.md` — Wave 2 regression note — present

### Wave 2 Charts (output/charts/hy_ig_v2_spy/plotly/)

- [x] **Canonical META-ZI zoom charts** for Story "What History Shows": Dot-Com (1997-2003), GFC (2007-2010), COVID (2020) zooms render with event markers (verified Cloud, story page screenshot)
- [x] **Standalone Granger F-statistic by lag bar chart** (`granger_f_by_lag.json`) — replaces previous Local Projections fallback (verified Cloud, `temp/cloud_wave2_evidence_tab_granger_causality.png`) — closes S18-11
- [x] **Regime quartile bars** (`regime_quartile_returns.json`) — Q1-Q4 forward returns, monthly resolution (verified Cloud, `temp/cloud_wave2_evidence_L2_quartile_returns.png`)
- [x] **Hero chart annualized return overlay + NBER caption** (verified Cloud, story page hero — text contains "NBER", "annualized", "recession")
- [x] All other Wave 1 charts continue to render (correlation_heatmap, hmm_regime_probs, ccf_prewhitened, transfer_entropy, local_projections, quantile_regression, equity_curves, drawdown, walk_forward, tournament_sharpe_dist)

### Narrative — Story Page

- [x] **Headline-first structure**: `## Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns` renders at TOP, BEFORE "Where This Fits in the Portal" (verified Cloud)
- [x] **Investor-impact clauses** ("What this means for investors:") on each Early Warning Signal bullet (verified Cloud — text contains 5 occurrences)
- [x] **What History Shows** section with 3 zoom charts (Dot-Com, GFC, COVID) and event markers (verified Cloud)
- [x] Plain English expander at top (verified Cloud)
- [x] Hero chart caption shows NBER recession bands + annualized return overlay (verified Cloud)
- [x] Breadcrumb renders (verified Cloud)

### Narrative — Strategy Page

- [x] **"How the Signal is Generated"** plain-English section renders BEFORE KPI cards (verified Cloud — closes S18-1 narrative side)
- [x] Execute / Performance / Confidence three-tab structure renders (verified Cloud)
- [x] Performance tab: equity curves, drawdown, trade log all present (verified Cloud, `temp/cloud_wave2_strategy_tab_performance.png`)
- [x] Confidence tab: walk-forward, stress tests, signal decay all present with 1-line takeaways (verified Cloud)
- [x] Plain English expander + breadcrumb (verified Cloud)

### Narrative — Evidence Page

- [x] Two-tier difficulty: Level 1 (Correlation, Granger Causality, CCF) + Level 2 (Local Projections, Regime Analysis, Quantile Regression, Transfer Entropy, Quartile Returns) — 8 method blocks total (verified Cloud — 10 tab buttons enumerated: 2 outer + 8 inner)
- [x] Granger tab shows F-statistic by lag bar chart, NOT a Local Projections fallback (verified Cloud — closes S18-11)
- [x] Quartile Returns tab shows Q1-Q4 bars with monthly-resolution commentary (verified Cloud)
- [x] Plain English expander + breadcrumb (verified Cloud)

### Narrative — Methodology Page

- [x] References section renders with 16-17 bracket-cited entries across 4 categories (Credit Spread & Equity Research / Time Series Econometrics / Regime Detection & Risk / HY-IG Specific) (verified Cloud)
- [x] Status vocabulary legend present (verified Cloud — text contains "status")
- [x] Plain English expander + breadcrumb (verified Cloud)

### Defense-2 Validations

- [x] Pre-render validation guards on APP-SE1 (Probability Engine) — gates SE2 rendering on schema match
- [x] Render-time linter on Evidence page (8-element template per method block)
- [x] Pair registry integrity check passes — `_check_integrity(pair)` for hy_ig_v2_spy entry

### Stakeholder Items Closed (2026-04-18 batch)

- [x] **S18-1**  — How the Signal is Generated plain-English section before KPIs
- [x] **S18-3**  — Investor-impact clauses on Early Warning Signal bullets
- [x] **S18-8**  — META-ZI canonical zoom charts (Dot-Com, GFC, COVID) on Story page
- [x] **S18-9**  — Hero chart annualized return overlay + NBER recession bands
- [x] **S18-10** — Future Live Execution section (placeholder-only, by-design — see open items below)
- [x] **S18-11** — Standalone Granger F-statistic by lag bar chart (no longer falls back to Local Projections)
- [x] **S18-12** — Regime quartile returns chart with monthly-resolution commentary

### Lesandro Reference-Pair Items Closed

- [x] **SL-1** — Headline-first Story structure
- [x] **SL-2** — Reference list standardized to bracket-cite [AuthorYear] format
- [x] **SL-3** — Coupled to SL-2; in-text citations resolve to references section
- [x] **SL-4** — META-ZI loader integrated for "What History Shows" zoom charts
- [x] **SL-5** — META-ZI event markers (NBER, COVID, GFC anchors) render on zoom charts

### Cloud Verification Matrix (2026-04-19)

| Page | Markers Tested | PASS | FAIL | Notes |
|------|---------------:|-----:|-----:|-------|
| Landing | 2 | 2 | 0 | HY-IG v2 card present with Sharpe + classification chips |
| Story | 9 | 9 | 0 | All headline/structure/zoom markers present |
| Evidence | 9 (req'd tabs clicked) | 9 | 0 | Level-2 tabs require outer "Level 2 — Advanced Analysis" click first; both Granger F-by-lag AND Quartile Returns charts render |
| Strategy | 8 + 9 sub | 17 | 0 | Execute/Performance/Confidence sub-tabs all populated |
| Methodology | 2 | 2 | 0 | References section + status vocab legend |

Full results JSON: `temp/cloud_wave2_results.json`. Screenshots: `temp/cloud_wave2_{landing,story,evidence,strategy,methodology}.png` plus 9 tab-level supplementary captures.

---

## Wave 4 Cloud Verification (2026-04-19)

Final Cloud verification for Wave 4 after commit `cc3f551` (SOP Part F Waves 4A → 4D). Verified via Playwright headless (chromium) against https://aig-rlic-plus.streamlit.app/ — see `temp/cloud_wave4e_{story,evidence,strategy,methodology}.png` and `temp/cloud_wave4e_results.json`.

### Session Bugs Fixed (all verified Cloud)

- [x] **Bug 1 — "No signals_*.parquet" error on Probability Engine Panel** (Wave 4A fix via ECON-DS2 / GATE-29): Strategy page Execute tab now renders the HMM stress probability time-series chart. No red `st.error` callout. Verified DOM contains no occurrence of "No signals_*.parquet" or "Probability engine panel cannot render" across any of the 4 pages.
- [x] **Bug 2 — Hero chart NBER shading imperceptible** (Wave 3 fix): Story page hero dual-panel chart renders with 3 visible NBER rose/mauve vertical bands (2001, 2008-09, 2020) on BOTH HY-IG top panel AND SPY bottom panel.
- [x] **Bug 3 — Dot-Com / GFC / COVID zoom charts as "chart pending" placeholders** (Wave 3 loader fix): Story "What History Shows" renders 3 zoom line charts with event markers ("Mar 2000: Dot-Com peak", "NBER recession start (Mar 2001)", "WorldCom (Jul 2002)", "COVID Shock 2019-2022" etc.) and visible NBER bands. No `st.info` "chart pending" placeholders anywhere.
- [x] **Bug 4 — GATE-28 compliance audit**: Grep of full DOM text across all 4 pages returned **0** occurrences of "chart pending" (case-insensitive). Raw DOM bodies saved to `temp/cloud_wave4e_{page}_body.txt`.
- [x] **Bug 5 — APP-DIR1 direction-check red error**: Strategy page renders cleanly at the top. No "Direction disagreement" red banner. 2-way triangulation (Evan=countercyclical, Dana=countercyclical) passes per Wave 4D-1 artifact migration.

### META-CF Schemas Committed (Wave 4C)

8 META-CF contract schemas committed upstream in `e28dd3d` (Wave 4B+4C) and activated on the consumer side in `cc3f551` (Wave 4D). Consumer-side integration verified via `app/_smoke_tests/smoke_schema_consumers.py` (3/3 pass, including first production use of APP-DIR1).

### Cloud Smoke-Test Matrix (Wave 4E, 2026-04-19)

| Item | Result | Notes |
|------|--------|-------|
| Cloud live (rebuild complete) | PASS | All 4 pages loaded on first attempt; no splash/please-wait screens |
| Probability Engine Panel renders (not parquet error) | PASS | Time-series plotly chart visible on Strategy Execute tab |
| Hero NBER bands visible on both panels | PASS | Dual-panel hero with 2001/2008-09/2020 bands on HY-IG + SPY |
| Dot-Com zoom renders (not placeholder) | PASS | "Mar 2000: Dot-Com peak" + NBER band + 400 bps crossing marker |
| GFC zoom renders (not placeholder) | PASS | "Oct 2007" / 2008-09 NBER band rendered |
| COVID zoom renders (not placeholder) | PASS | "COVID Shock 2019-2022" with Feb/Mar 2020 markers |
| GATE-28: total `chart pending` across 4 pages | **0** PASS | Grep of 4 body.txt DOM dumps returned zero matches |
| APP-DIR1 direction check passes | PASS | No red banner; 2-way agreement (Evan=Dana=countercyclical) |
| Story headline-first + investor-impact bullets | PASS | "Sharpe 1.27 over 8-year OOS..." at top; "What this means for investors" clauses present |
| Evidence 2-tier tabs + standalone Granger + quartile returns | PASS | Level 1/2 structure visible; Granger tab text confirmed. Level 2 inner tabs collapsed behind outer selector (expected, per Wave 2 verification notes) |
| Strategy: plain-English signal-gen + trigger cards + live-exec placeholder | PASS | "How the Signal is Generated" before KPIs; "How to Use the Signal — Trigger Scenarios" cards visible; "Future Live Execution" section at bottom |
| Methodology references + plain-english expander | PASS | References section with ~16 bracket-cited entries across 4 categories; plain-english expander present |
| Zero Streamlit error banners on any page | PASS | `st.error` / stAlert[kind=error] scan returned no error-text matches on any page |

### Verification Artifacts

- Results JSON: `temp/cloud_wave4e_results.json`
- Screenshots: `temp/cloud_wave4e_{story,evidence,strategy,methodology}.png`
- DOM dumps: `temp/cloud_wave4e_{story,evidence,strategy,methodology}_body.txt`
- Script: `temp/cloud_wave4e.py`

### Recommended Next Action

Cloud state is clean. Ready for stakeholder review — the Wave 4 deploy-artifact gap is closed (GATE-29), schema consumer-side validation is active (APP-WS1 / APP-SEV1 / APP-DIR1), and all 5 session-surfaced bugs are verified fixed on Cloud. The `hy-ig-v2-reference` tag remains reserved for post-stakeholder-approval sign-off per META-RPD.

---

## Wave 5D Cloud Verification (2026-04-19)

Cloud verification after Wave 5C retro-apply landed on `f7587a3`. Initial Wave 5D Playwright sweep exposed one stale-Cloud failure (zoom-chart `line.color` resolved to `#d62728` matplotlib-default red, not the Okabe-Ito vermilion `#D55E00` that the committed `history_zoom_*.json` artifacts declare). Lesandro invoked a manual **Reboot App** via the Streamlit Cloud dashboard per META-FRD (dashboard reboot is authoritative, no force-redeploy layering). Post-reboot re-verify executed 2026-04-19 via `temp/cloud_wave5d_rerun_story.py`; all 3 zoom charts now render the canonical Okabe-Ito vermilion.

### Wave 5D Cloud Smoke-Test Matrix (9 items)

| Item | Result | Notes |
|------|--------|-------|
| 1. Cloud live across all 4 v2 pages (Story / Evidence / Strategy / Methodology) | PASS | Pages hydrate; no splash/please-wait; no `st.error` banners (continuation of Wave 4E state on `f7587a3`) |
| 2. Okabe-Ito palette on hero chart (`#D55E00` vermilion + second panel accent) | PASS | DOM probe `gd.data[0].line.color = "#D55E00"` on hero (idx 0) |
| 3. Okabe-Ito palette on 3 Story zoom charts (Dot-Com / GFC / COVID) | PASS (after reboot) | Initial run returned `#d62728` across all 3 (stale Cloud cache). After Lesandro's manual Reboot App, re-verify returned `#D55E00` for all 3. See "Reboot Event" note below. |
| 4. Okabe-Ito palette on regime-quartile bars (Q1-Q4 marker colors) | PASS | DOM probe returned `["#009E73","#0072B2","#D55E00","#CC79A7"]` (Okabe-Ito Q1-Q4 sequence) |
| 5. VIZ-V11 pre-save lint absence of `#d62728` / `#1f77b4` / `#2ca02c` across charts | PASS | 0 matplotlib-default color codes detected in any rendered Plotly div (post-reboot DOM dump) |
| 6. GATE-28 `chart pending` residual count across 4 pages | PASS — **0** occurrences | DOM-body grep on `temp/cloud_wave5d_{page}_body.txt` |
| 7. APP-DIR1 direction-check renders without red banner | PASS | Continues Wave 4E state; 2-way agreement (Evan=Dana=countercyclical) |
| 8. Story `What History Shows` renders 3 zoom charts with event markers | PASS | All 3 zoom-chart titles present: "Credit Spreads During the Dot-Com Bust, 1998-2003" / "... Global Financial Crisis, 2005-2010" / "... COVID Shock, 2019-2022" |
| 9. META-ZI event-marker registry integrity (`docs/schemas/history_zoom_events_registry.json`) | PASS | Registry file present; loader populates zoom charts from canonical events |

All 9 PASS.

### Reboot Event (per META-FRD)

**Item 3** required one manual Reboot App via the Streamlit Cloud dashboard. Cloud had served a stale chart JSON bundle: committed `output/charts/hy_ig_v2_spy/plotly/history_zoom_*.json` files on `f7587a3` declared the correct Okabe-Ito `#D55E00` values, but the live Cloud served pre-Wave-5C palette (`#d62728`). This is the second META-FRD invocation in 2026-Q2 (first was `1720c0c` trivial-bump redeploy in Wave 4A). No force-redeploy commit was layered — Lesandro's dashboard Reboot is the authoritative action. Logged in the Force-Redeploy / Reboot register in `docs/pair_execution_history.md` per META-FRD.

### Verification Artifacts

- Screenshot (full page, post-reboot): `temp/cloud_wave5d_rerun_story.png`
- DOM dump (all Plotly divs with `line.color` / `marker.color`): `temp/cloud_wave5d_rerun_dom.json`
- Re-verify script: `temp/cloud_wave5d_rerun_story.py`
- Prior Wave-5D supplementary captures: `temp/cloud_wave5d_{landing,story,evidence,strategy,methodology}.png` + `temp/cloud_wave5d_*_body.txt`

### Zoom-Chart Color Matrix (post-reboot)

| Zoom chart | Plotly div title | `data[0].line.color` | Verdict |
|------------|------------------|----------------------|---------|
| Dot-Com | "Credit Spreads During the Dot-Com Bust, 1998-2003" | `#D55E00` | PASS |
| GFC | "Credit Spreads During the Global Financial Crisis, 2005-2010" | `#D55E00` | PASS |
| COVID | "Credit Spreads During the COVID Shock, 2019-2022" | `#D55E00` | PASS |

Cloud state is clean on `f7587a3`. Ready for stakeholder review; `hy-ig-v2-reference` tag continues to be reserved until stakeholder approval per META-RPT (no self-tagging by Lead).

---

## Reference Pair Comparison

**Compared against:** N/A — HY-IG v2 IS the reference pair (first to be tagged).

**Note:** This is the inaugural reference pair. Future pairs will compare against this one. Per META-RPD, when stakeholder approves, this state is tagged as `hy-ig-v2-reference`.

**design_note.md:** Not required — this is the reference establishment, not a deviation from prior reference.

---

### Cross-Version Consistency Check (vs Sample HY-IG)

Per META-XVC (team-coordination.md §Cross-Version Discipline). Baseline observed against: Sample HY-IG pair (`results/hy_ig_spy/`, portal pages `app/pages/{1..4}_hy_ig_*.py`, Sample narrative `docs/portal_narrative_hy_ig_spy_20260228.md`). v2 is NOT a successor of Sample in the tag-reference sense (Sample was never tagged and v2 is the first `<pair_id>-reference` candidate per META-RPT), but the audit treats Sample as the de-facto v0 for method continuity.

#### Retained methods (v2 matches Sample — silent match per META-XVC)

Evidence per inspection of Sample's `winner_summary.json`, `interpretation_metadata.json`, Sample chart filenames (`output/charts/plotly/hy_ig_spy_*.json`), Sample portal pages 1-4, and v2 counterparts:

- **HMM family and state count** — both use a 2-state Hidden Markov Model over credit-spread dynamics with the stress-state probability as the tradable signal. Signal column `hmm_2state_prob_stress` is unchanged (Sample `winner_summary.signal_code = hmm_2state_prob_stress` / v2 `winner_summary.signal_column = hmm_2state_prob_stress`). Evidence: both winner_summary.json files; Sample Strategy page §"HMM Long/Cash (W1)" and v2 regime-analysis method block.
- **Tournament ranking by OOS Sharpe** — v2 preserves Sample's "tournament tests {signal × threshold × strategy} combinations and ranks by OOS Sharpe" model. Evidence: Sample `winner_trade_log.csv` exists alongside `winner_summary.json`; v2 `tournament_results_20260410.csv` + `winner_summary.json` carry the same shape.
- **Direction assertion = countercyclical** — Sample `expected_direction = counter_cyclical`; v2 `direction = countercyclical`. Semantically identical; spelling normalized to single-token form (enum requirement of `winner_summary.schema.json v1.0.0`, not a method change).
- **Indicator-nature + indicator-type taxonomy** — `leading` / `credit` in both Sample and v2 `interpretation_metadata.json`.
- **Strategy objective = min_mdd** — both pairs assert drawdown avoidance as the primary objective (Sample `interpretation_metadata.strategy_objective = min_mdd`; v2 matches).
- **OOS window concept** — Sample OOS implied by `winner_trade_log.csv` date range; v2 uses the same 2018-01-01 → 2025-12-31 out-of-sample period. v2 promotes the window to an explicit sidecar (`oos_split_record.json`), but the window itself matches Sample (8 years, 2018-2025).
- **Cost model** — Sample `breakeven_cost_bps = 50`; v2 `breakeven_cost_bps = 50` with `cost_assumption_bps = 5` (round-trip assumption carried forward from Sample's implicit 5 bps).
- **Evidence method inventory (Level 1 + Level 2 shared subset)** — Correlation, Granger, Local Projections, Regime (HMM), Quantile Regression are present in BOTH Sample (pages 2_hy_ig_evidence) and v2 (page 9_hy_ig_v2_spy_evidence). Method family unchanged.
- **Hero-chart concept** — dual-panel HY-IG spread over SPY, NBER shading backdrop. Concept retained; unit discipline and palette are declared divergences (see below).
- **Narrative voice** — "financially-literate-non-quant baseline + plain-English layer" maintained across all four pages (Ray retained the Sample voice; the Wave 1+ enhancements are additive, not replacements).

#### Intentionally diverged (v2 improved on Sample — declared per META-XVC)

Consolidated from the Wave 5C retro-apply sections in `regression_note_20260419.md`. Each row below is a full META-XVC `### Methodological divergence` block condensed to the 6 required fields. All have an upstream regression-note entry for the full text.

| Area | Prior (Sample) | New (v2) | Strong reason | Expected impact | Validation | Cross-ref |
|------|----------------|----------|---------------|-----------------|------------|-----------|
| **Strategy family** | P1 Long/Cash, threshold 0.7 (`winner_summary.threshold_code = T4_0.7`) | P2 Signal Strength, threshold 0.5 (`winner_summary.threshold_code = T4_hmm_0.5`) | Tournament re-run with broadened cost model ranked P2 above P1 on OOS Sharpe (1.27 vs 1.17); P2 reduces whipsaw turnover | Sharpe +0.10; turnover falls from 4.83 to 3.78; Max DD changes marginally (-10.2% v2 vs -12% Sample) | Tournament re-run documented in `tournament_results_20260410.csv`; winner validated via walk-forward CV | Ray/Evan Wave 2A; `regression_note_20260411.md` |
| **HMM emission threshold** | 0.7 | 0.5 | P2 Signal Strength scales position continuously with stress probability; a lower threshold captures earlier stress onset for proportional scaling (not binary switching) | Stress-phase position begins scaling earlier; Sharpe gain concentrated in GFC + COVID regions | Perceptible on walk-forward chart; OOS Sharpe gain validated against schema-validated winner_summary | Evan Wave 2A |
| **Hero-chart unit** | Decimal spread (silent axis) | bps (explicit unit, dual-panel) | Wave-2A stakeholder report of 100× unit-scale bug (S18-5); Sample rendered the spread axis with the wrong implicit scale | Hero axis labeled "Spread (bps, where 100 bps = 1%)" with values 147-1531 bps range | DATA-D12 column rename `hy_ig_spread` → `hy_ig_spread_pct` + DATA-D5 sidecar declare unit at artifact layer; Vera's VIZ-V5 smoke test passes | Wave 5C Dana Task 1+2; S18-5 |
| **Color palette** | Matplotlib/Plotly defaults (`#d62728`, `#1f77b4`, `#2ca02c`) | Okabe-Ito 2026 colorblind-safe palette (`#D55E00`, etc.) | Colorblind accessibility + palette drift audit — hero + zoom charts used mismatched palettes in Sample | Perceptual consistency across hero, zoom, regime, quartile charts; no new semantics | VIZ-V11 pre-save lint blocks raw matplotlib defaults; `_meta.json.palette_id` mandatory | Vera Wave 5B-2 (rule) + Wave 5C (retro-apply) |
| **Historical-episode selection + event-marker registry** | Ad-hoc Dot-Com / GFC references in prose, no chart | Canonical triad (Dot-Com, GFC, COVID) with event-marker registry at `docs/schemas/history_zoom_events_registry.json`; three zoom charts at `output/_comparison/history_zoom_*.json` with rationale + source_citation per event | Sample had historical-episode prose without matching zoom charts (SL-4, SL-5); registry prevents silent episode drift across future pairs | Three new zoom charts render on Story "What History Shows"; no behavior change in Sample | VIZ-V12 registry; META-ZI canonical + override loader; Wave 4E Cloud verification PASS | Ray Wave 2A; Vera Wave 2A + Wave 5B-2 + Wave 5C |
| **Signal-code canonicalization** | `hmm_2state_prob_stress` (Sample) + `S6_hmm_stress` (v2 pre-Wave-5C tournament CSV) drifted across artifacts | `signal_code = hmm_stress` canonicalized via ECON-DS3 registry in `winner_summary.json` | Wave-5B-2 audit: signal_code drift between `tournament_results_*.csv` and `winner_summary.json` created silent column-lookup failures | No behavior change — registry resolves both the parquet column name AND the display name per APP-WS1 | `winner_summary.schema.json v1.0.0` validates; smoke_schema_consumers PASS | Evan Wave 5C Task 3; ECON-DS3 |
| **OOS-window provenance** | Sample: window implicit in `winner_trade_log.csv` (no sidecar); reverse-inferable from `oos_n` | v2: explicit `oos_split_record.json` sidecar with 7 fields | ECON-OOS1: downstream agents must NOT recompute OOS bounds from the trade log | No window change (2018-2025 preserved); provenance is now machine-readable | `oos_split_record.json` validated; consumers updated per ECON-OOS1 | Evan Wave 5C Task 1; ECON-OOS1 |
| **Tournament-tie documentation** | Sample: no tie note | v2: `tournament_tie_note.md` with ECON-T3 rationale | ECON-T3: cascade / tie-break rule change = methodological divergence; must be auditable | No ranking change; top-of-leaderboard rationale documented | File present + cross-referenced from regression note | Evan Wave 5C Task 2; ECON-T3 |
| **Contract-file governance** | Sample: no META-CF schemas | v2: 8 schemas under `docs/schemas/` (winner_summary, interpretation_metadata, data_subject, chart_type_registry, narrative_frontmatter, url_slug_pins, caption_prefix_vocab, history_zoom_events_registry); producer + consumer validators | Wave-5 audit: inline prose dictionaries drifted between Evan's SOP and Ace's consumer code | No behavior change in happy path; validation-first reads on every portal entry point | Ace's consumer-side APP-WS1 / APP-SEV1 / APP-DIR1 gates run at load time; Wave 4D-2 verified | Wave 4B+4C authoring + Wave 4D producer+consumer migration |
| **Data-layer sidecar + manifest + display-name registry** | Sample: none | v2: `data/hy_ig_v2_spy_daily_schema.json` sidecar + `data/manifest.json` + `data/display_name_registry.csv` | DATA-D5 / D11 / D12 / D13: unit, ownership, manifest, and display-name must all be machine-readable | No value change in v2 data; structural governance added | 3/3 schema validations exit 0; 4/4 Python consumers compile; 0 bare `hy_ig_spread` references remain | Dana Wave 5C Tasks 1-4 |
| **Narrative frontmatter contract** | Sample narrative: Markdown body only, no frontmatter | v2: frontmatter block per `narrative_frontmatter.schema.json`; stable `anchor` fields; `direction_asserted`, `status_vocabulary`, `glossary_requests` arrays | RES-17: heading-match fragility (RES-16 / B8) and three-way direction silent-drift risk (APP-DIR1) were structurally open in Sample | No narrative-body change beyond reference-pair polish already shipped in Wave 1; frontmatter is additive metadata | Ray Wave 5C retro-apply validates extracted anchors against the schema; APP-DIR1 2-way agreement PASS | Ray Wave 4C-2 authoring + Wave 5C retro-apply |
| **Caption-prefix + expander-title + slug canonical vocab** | Sample: ad-hoc prefixes ("What this shows" / "In plain English" / "Read this chart as" co-occur) | v2: APP-CC1 canonical 4-prefix vocabulary + APP-EX1 expander titles + APP-URL1 slug pins | Wave-5 Ace audit: three different caption prefixes on one Strategy tab of Sample | No information loss; unified vocabulary; slug redirects prevent dead external links | Ace Wave 5C Tasks 1-2-5; `_smoke_tests/smoke_url_slugs.py` (scheduled) + manual prefix grep PASS | Ace Wave 5B-2 + Wave 5C |
| **META-ELI5 on loud errors** | Sample: `st.error` / `st.warning` carry technical label only | v2: every loud error carries technical label + 1-2 sentence ELI5 body; `_status_vocabulary` in `portal_glossary.json` has `{eli5, technical}` object shape for all 7 status labels | META-ELI5: stakeholder should be able to read every on-screen flag without agent translation | New wording appears in Evidence `chart_status != "ready"` warning and Strategy direction-mismatch banner | Grep confirms `_status_vocabulary` has `{eli5, technical}` for Available/Pending/Validated/Stale/Draft/Mature/Unknown | Ace Wave 5C Task 3; Ray Wave 5C glossary body |

**Total:** 13 declared divergences, all with regression-note provenance and validation evidence.

#### Possibly diverged but undeclared (audit)

Findings: **none at the blocker level.** The Wave 5C sweep (Dana, Evan, Vera, Ray, Ace retro-apply sections in `regression_note_20260419.md`) explicitly enumerated drifts against Sample and declared them. Suspicion candidates checked:

- **Strategy P-family semantic drift** — checked: P2 Signal Strength vs Sample's P1 Long/Cash is the single most consequential method change. Declared above (row 1); no residual undeclared drift.
- **Threshold value 0.7 → 0.5** — declared above (row 2).
- **Cost basis / turnover accounting** — Sample `annual_turnover = 4.83` vs v2 `3.78`; this is a consequence of the P1→P2 change, not an independent cost-model change. No divergence entry needed (follows from the declared strategy-family change).
- **OOS period length** — Sample implicit OOS window vs v2 explicit 2018-2025; the window concept matches (retained) and the sidecar promotion is declared (row 7). No residual.
- **Evidence tab structure (5 tabs in Sample → 8 in v2)** — Added Pre-whitened CCF, Transfer Entropy, Quartile Returns. Documented in `regression_note_20260411.md` Evan's 2026-04-11 changes + Ace's 5→8 tabs; additive, not a drift.
- **Narrative voice and structure** — Retained, not diverged; Wave 1+ additions (headline-first, plain-English expanders, investor-impact bullets, zoom charts) are additive and all stakeholder-authorized per SL-1..5 + S18-* items.
- **Hero dual-panel vs single-panel** — Declared (row 3, unit-scale fix bundle).

**Conclusion:** no undeclared drift found; cross-version diff is clean. No BLOCKERS raised by this audit step.

---

### Deflection Audit (GATE-30)

Per GATE-30 (team-coordination.md §Pair Acceptance Checklist, Blocking Items). Two stakeholder items in the 2026-04-18 batch (`docs/stakeholder-feedback/20260418-batch.md`) were closed by deflection (resolution = "see other page/section") rather than in-place fix. Both are audited here for: (a) target anchor actually renders, and (b) target content actually addresses the ask.

| Stakeholder item | Origin page / section | Deflection target page | Deflection target anchor/section | DOM-renders? | Content-matches? | Lead sign-off |
|------------------|-----------------------|------------------------|----------------------------------|--------------|------------------|----------------|
| **S18-2** (Market Regime summary) | Strategy tab | Story | Market regime explainer section + "How do we define market regimes without arbitrary cutoffs?" expander | **Y** (verified Wave 4E DOM dumps `temp/cloud_wave4e_story_body.txt`) | **Y** (`docs/portal_narrative_hy_ig_v2_spy_20260410.md` line 340-358 contains "The connection changes depending on the market **regime**", defines regime, explains stress-vs-calm, expander answers "How do we define market regimes without arbitrary cutoffs?" citing Hamilton 1989 and Guidolin-Timmermann 2007) | **Y** — Lead Lesandro |
| **S18-4** (Evidence Sources Table) | Story/Strategy | Evidence | Statistical-method walk-through (8-element template applied to each of 8 method blocks) + `_status_vocabulary` legend in `portal_glossary.json` | **Y** (Wave 4E cloud verification; `app/pages/9_hy_ig_v2_spy_evidence.py` loads 8 method blocks via `render_method_block`) | **Y** (each of 8 method blocks renders `method_name`, `method_theory`, `question`, `how_to_read`, chart, `observation` rendered as `"What this shows:"` per APP-CC1, optional `deep_dive`, `interpretation` rendered as `"Why this matters:"`, and `key_message` — this is the "plain English" layer S18-4 asked for. Available/Pending clarity provided by `_status_vocabulary` entries `{eli5, technical}` in `docs/portal_glossary.json` — both `Available` and `Pending` carry stakeholder-readable ELI5 bodies. `plain_english` / `why_it_matters` structure additionally present in glossary terms per Ray Wave 2A addition.) | **Y** — Lead Lesandro |

**S18-2 — PASS.** The Story page regime explainer exists, is specific (defines regime, explains stress-vs-calm statistical properties, walks through HMM and MS regressions, cites literature), and directly addresses the stakeholder ask ("short and simple summary — how to identify each regime, what it means for strategy performance"). The explainer includes the "what it means for strategy performance" paragraph (lines 340-345 of the narrative: "A simple 'sell stocks when spreads widen' rule will not work…An effective strategy needs to distinguish between calm and stressed markets…"). Deflection is strong.

**S18-4 — PASS.** The Evidence page statistical-method walk-through exists, is comprehensive (8 methods × 8 elements = 64 populated fields), and carries plain-English prose in every `observation`, `interpretation`, and `key_message` slot — rendered with canonical APP-CC1 prefixes ("What this shows:" / "Why this matters:" / "How to read it:"). Available-vs-Pending status clarity is provided by the glossary's `_status_vocabulary` block which now has `{eli5, technical}` bodies for `Available` ("produced and live on the portal — you can read it now"), `Pending` ("on the to-do list but has not been made yet…"), `Validated`, `Stale`, `Draft`, `Mature`, and `Unknown`. Deflection is strong.

**BLOCKERS:** none raised by GATE-30 audit.

---

## Regression Note

**Files:** `results/hy_ig_v2_spy/regression_note_20260411.md` + `results/hy_ig_v2_spy/regression_note_20260419.md`

**Sections present (20260411):**
- Evan's Changes (2026-04-11) — added CCF, Transfer Entropy, Quartile Returns + tournament_winner.json
- Vera's Changes (2026-04-11) — fixed hero chart axis/units, canonicalized heatmap, 3 new method charts
- Ray's Changes (2026-04-11) — 3 new 8-element blocks + bps dual notation + 5 glossary entries expanded
- Ace's Changes (2026-04-11) — Evidence 5 → 8 tabs + render-time linter
- Ray's Follow-up Changes (2026-04-11) — "How to Read the Trade Log" subsection
- Ace's Follow-up Changes (2026-04-11) — Strategy page legend + dual download
- Ray's Reference-Pair Polish (2026-04-14) — 7 narrative changes for reference quality
- Ace's Reference-Pair Polish (2026-04-14) — 5 portal UX changes for reference quality

**Sections present (20260419):**
- Wave 2A / 2B — Evan / Vera / Ray / Ace (2026-04-19) — S18-* stakeholder batch closure
- Wave 3 — Lead gate patches + Vera bug-fix (hero NBER perceptibility) + Ace bug-fix
- Wave 4A — Evan Deploy-Artifact Allowlist (ECON-DS2) + Lead GATE-29
- Wave 4B+4C — Lead META-CF contract standard + schema authoring (Evan / Vera / Ray / Dana)
- Wave 4D-1 — Dana / Evan artifact migration to v1.0.0 schemas
- Wave 4D-2 — Ace consumer-side schema integration (APP-WS1 / APP-SEV1 / APP-DIR1)
- Wave 5B-1 — Lead META-* authoring (META-XVC, META-SCV, META-ELI5, META-RPT, META-BL)
- Wave 5B-2 — Ray / Dana / Vera / Evan / Ace agent-scoped rule authoring
- **Wave 5C retro-apply (2026-04-19)** — Evan (ECON-OOS1/OOS2/T3/DS3 artifact migration + signal_code canonicalization) / Dana (column rename + sidecar + manifest + display-name registry) / Vera (Okabe-Ito palette + VIZ-V12 events-registry + VIZ-V13 annotation strategy + VIZ-V5 smoke re-run) / Ray (headline + frontmatter + status_labels → _status_vocabulary + glossary ELI5 bodies) / Ace (APP-CC1 caption prefixes + APP-EX1 expander titles + META-ELI5 audit on loud errors + trigger-card sparkline real-history fix + APP-URL1 slug pins)
- **Lead's Wave 5C consolidation (2026-04-19)** — this acceptance.md update: cross-version diff vs Sample + GATE-30 deflection audit

**New files created by Wave 5C (provenance for reference-pair manifest):**

- `results/hy_ig_v2_spy/oos_split_record.json` (Evan, ECON-OOS1)
- `results/hy_ig_v2_spy/tournament_tie_note.md` (Evan, ECON-T3)
- `data/hy_ig_v2_spy_daily_schema.json` (Dana, DATA-D5)
- `data/manifest.json` (Dana, DATA-D13)
- `data/display_name_registry.csv` + `data/display_name_registry.json` (Dana, DATA-D13)
- `output/charts/hy_ig_v2_spy/plotly/_perceptual_check_granger_f_by_lag.png` (Vera, VIZ-V2 refreshed)
- `output/charts/hy_ig_v2_spy/plotly/_perceptual_check_regime_quartile_returns.png` (Vera, VIZ-V2 refreshed)
- `output/charts/hy_ig_v2_spy/plotly/_smoke_test_wave5c_20260419.log` (Vera, VIZ-V5)

Plus modifications to `winner_summary.json` (signal_code canonicalized), `docs/portal_glossary.json` (_status_vocabulary shape + ELI5 bodies), `docs/portal_narrative_hy_ig_v2_spy_20260410.md` (frontmatter + status labels), 4× `app/pages/9_hy_ig_v2_spy_*.py` (APP-CC1/EX1/URL1 + META-ELI5 + sparklines), 5× `app/components/*.py` (breadcrumb, charts, direction_check, instructional_trigger_cards, live_execution_placeholder, position_adjustment_panel, probability_engine_panel), `docs/schemas/narrative_frontmatter.schema.json`, `docs/schemas/url_slug_pins.json`, 3× `output/_comparison/history_zoom_*.json` (Vera palette + event-marker registry), `output/charts/hy_ig_v2_spy/plotly/hero.json` + `granger_f_by_lag.json` + `regime_quartile_returns.json` (palette), 2× `scripts/retro_fix_hy_ig_v2_*.py` + `scripts/pair_pipeline_hy_ig_v2_spy.py` + `scripts/generate_charts_hy_ig_v2_spy.py` (registry consumers).

**Wave 5C agent sign-off status (regression_note_20260419.md confirms all 5 present):**

- Evan — self-approved (§Evan's Wave 5C retro-apply)
- Vera — self-approved (§Vera's Wave 5C retro-apply)
- Dana — self-approved (§Dana's Wave 5C retro-apply)
- Ray — self-approved (§Ray's Wave 5C retro-apply)
- Ace — self-approved (§Ace's Wave 5C retro-apply)

**Summary of changes from prior version:** Comprehensive — see individual sections in the regression note. All changes traceable to stakeholder feedback items (N1-N13, F1-F15, S18-*, SL-*) and SOP rules (META-PWQ, META-RPD, META-XVC, META-RPT, META-ELI5, GATE-23/24/25/26/27/28/29/30, APP-*, ECON-*, DATA-*, VIZ-*, RES-*).

---

## Stakeholder Review

**Reviewed by:** Pending
**Review date:** TBD
**Outstanding issues:** TBD after review

---

## Lead Sign-off

**Approved by:** Lead Lesandro
**Approval date:** Pending stakeholder sign-off
**Tag/commit:** Pending — will tag as `hy-ig-v2-reference-candidate` at Lead commit per META-RPT, promoted to `hy-ig-v2-reference` upon stakeholder approval. Per META-RPT, the `hy-ig-v2-reference` tag is **NOT** applied here — it remains reserved until stakeholder sign-off.
**Current commit:** `f7587a3` (Wave 5C retro-apply of 24 new Wave-5B rules; Cloud-verified 2026-04-19 post-reboot).
**Upstream chain:** `416ba94` (Wave 4E Cloud verification) ← `cc3f551` (Wave 4D: migrate artifacts + consumer-side schema integration) ← `e28dd3d` (Wave 4B+4C: cross-review + META-CF) ← `f295073` (Wave 4A: deploy-artifact gap + GATE-29) ← `519d042` (Wave 3: gate fixes + retro-apply) ← `342f48c` (Wave 5B: 24 new rules + 10 schemas/registries) ← `f7587a3` (Wave 5C: retro-apply). Further upstream: `d6e4f02` (Wave 5 validation audits), `1720c0c` (force Cloud redeploy), `beca5aa` (Wave 2 verification), `1f864e8` (Wave 2B: portal rebuild), `b9730cb` (Wave 2A: artifacts/charts/narrative), `b7ee4ba` (Wave 1.5: coherence patches), `6bcb5e2` (Wave 1: 2026-04-18 stakeholder feedback), `27c6182` (pre-stakeholder draft). Earlier reference-pair polish landed in `6d40af8`.

---

## Notes for Stakeholder Review

### Closed in Wave 2 (2026-04-19)

- ~~**Granger Causality chart** still falls back to local_projections chart~~ — **CLOSED**: standalone `granger_f_by_lag.json` now renders on the Granger tab (commit `b9730cb`).
- ~~**Investor-impact clauses missing on Early Warning Signal bullets**~~ — **CLOSED**: 5 "What this means for investors" clauses now present.
- ~~**Headline buried in Story page**~~ — **CLOSED**: Sharpe 1.27 headline-first, before "Where This Fits".
- ~~**No "What History Shows" zoom charts**~~ — **CLOSED**: META-ZI loader integrated; Dot-Com / GFC / COVID render with event markers.

### Open — Pending stakeholder judgement

1. **S18-10 "Live Execution"** is intentionally a **placeholder section only** at the bottom of Strategy (3 metric cards: Last Signal, Last Update, Status). This is **by-design** for the reference-pair release — no live-data wiring yet. Stakeholder to confirm: keep as-is, or defer until live-data plumbing is in scope?

2. **GFC zoom-chart band override** — META-ZI applied a default ±2σ band on the GFC zoom. Lesandro to confirm this is the desired band, or if a different anchor (e.g. Lehman date) is preferred.

3. **Plain English expanders** still rendered as `st.expander` rather than HTML `<details>` tags (carried over from prior Notes). Functionally equivalent. Decision deferred to stakeholder; CSS sidecar would be needed for exact HTML rendering.

4. **CAGR vs arithmetic gap** is stated as "less than ~50 bps" in Methodology Return Basis note (carried over). If stakeholder wants the exact computed difference, Evan can derive from the equity curve.

5. **"Explore Alternative Strategies"** still shows metric comparison only — no per-strategy equity-curve overlay (carried over). Vera could add if requested.

6. **Landing-page card metrics** still read from `winner_summary.json`; no Wave 2 changes here. Sharpe 1.27 / Max DD -10.2% currently displayed are correct.
