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

## Reference Pair Comparison

**Compared against:** N/A — HY-IG v2 IS the reference pair (first to be tagged).

**Note:** This is the inaugural reference pair. Future pairs will compare against this one. Per META-RPD, when stakeholder approves, this state is tagged as `hy-ig-v2-reference`.

**design_note.md:** Not required — this is the reference establishment, not a deviation from prior reference.

---

## Regression Note

**Files:** `results/hy_ig_v2_spy/regression_note_20260411.md`

**Sections present:**
- Evan's Changes (2026-04-11) — added CCF, Transfer Entropy, Quartile Returns + tournament_winner.json
- Vera's Changes (2026-04-11) — fixed hero chart axis/units, canonicalized heatmap, 3 new method charts
- Ray's Changes (2026-04-11) — 3 new 8-element blocks + bps dual notation + 5 glossary entries expanded
- Ace's Changes (2026-04-11) — Evidence 5 → 8 tabs + render-time linter
- Ray's Follow-up Changes (2026-04-11) — "How to Read the Trade Log" subsection
- Ace's Follow-up Changes (2026-04-11) — Strategy page legend + dual download
- Ray's Reference-Pair Polish (2026-04-14) — 7 narrative changes for reference quality
- Ace's Reference-Pair Polish (2026-04-14) — 5 portal UX changes for reference quality

**Summary of changes from prior version:** Comprehensive — see individual sections in the regression note. All changes traceable to stakeholder feedback items (N1-N13, F1-F15) and SOP rules (META-PWQ, META-RPD, etc.).

---

## Stakeholder Review

**Reviewed by:** Pending
**Review date:** TBD
**Outstanding issues:** TBD after review

---

## Lead Sign-off

**Approved by:** Lead Lesandro
**Approval date:** Pending stakeholder sign-off
**Tag/commit:** Pending — will tag as `hy-ig-v2-reference` upon stakeholder approval
**Current commit:** `1f864e8` (Wave 2B: HY-IG v2 portal rebuild). Includes upstream `b9730cb` (Wave 2A: artifacts/charts/narrative), `b7ee4ba` (Wave 1.5: coherence patches), `6bcb5e2` (Wave 1: 2026-04-18 stakeholder feedback). Earlier reference-pair polish landed in `6d40af8`.

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
