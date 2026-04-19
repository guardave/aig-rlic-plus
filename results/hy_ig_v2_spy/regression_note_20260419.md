# HY-IG v2 × SPY — Regression Note (2026-04-19)

**Pair ID:** `hy_ig_v2_spy`
**Author:** Econometrics Evan
**Trigger:** Wave-2 retroactive application of new econometrics rules (ECON-E1, ECON-E2, ECON-H4) to close stakeholder items S18-8 and S18-11 from the 2026-04-18 feedback batch.

## Evan's Wave 2 Changes (2026-04-19)

### New artifacts produced

1. `results/hy_ig_v2_spy/granger_by_lag.csv` — Granger causality F-statistic and p-value at lags 1–12, testing HY-IG spread → SPY returns at monthly resolution. Schema matches ECON-E1 (`lag, f_statistic, p_value, df_num, df_den`).
2. `results/hy_ig_v2_spy/regime_quartile_returns.csv` — Annualized SPY return, vol, Sharpe, and max drawdown conditional on HY-IG spread quartile (monthly). Schema matches ECON-E2 (`quartile, n_months, ann_return, ann_vol, sharpe, max_drawdown`). Methodology documented in sidecar `regime_quartile_returns_methodology.md`.
3. `results/hy_ig_v2_spy/handoff_to_vera_20260419.md` — Per-method chart handoff table covering all 8 Evidence-page methods (Correlation, Granger, CCF, Local Projections, Regime, Quantile, Transfer Entropy, Quartile Returns) with result-file path, expected chart type, and status per method. Complies with ECON-H4.

### Rule IDs addressed

- **ECON-E1** — Granger causality by-lag artifact persistence. Closes the silent-fallback bug where the Granger chart was rendering the Local Projections figure because no `granger_by_lag.csv` existed to consume.
- **ECON-E2** — Regime quartile return artifact persistence. Restores the Q1–Q4 annualized SPY return analysis that was present in HY-IG v1 and silently dropped in the v2 rerun.
- **ECON-H4** — Per-method chart artifact handoff. Explicit result-file → expected-chart table for every mandatory Evidence-page method, eliminating the ambiguity that enabled the silent drop / silent substitution failures.

### Stakeholder items closed

- **S18-8 (Half-closed → Closed, pending Vera's chart)** — "Annualised SPX return by quartile Q1-Q4" restored via `regime_quartile_returns.csv`. Monotonic gradient: Q1 Sharpe = 1.79 (spread < 2.58 pp), Q2 = 1.48, Q3 = 0.53, Q4 = −0.53 (spread > 4.62 pp). Q1–Q4 Sharpe spread = **2.33 Sharpe units**.
- **S18-11 (Open → Closed, pending Vera's chart)** — Granger chart now has its own underlying artifact (`granger_by_lag.csv`). No longer falls back to Local Projections. Best lag-5 result: F = 4.07, p = 0.0014.

### Diagnostic notes

- **Sample size (monthly):** 311 months, 2000-02-29 to 2025-12-31.
- **Granger lag of best significance:** lag 5 (F = 4.0694, p = 0.001377). Lags 4 through 12 all significant at α=0.05. Lags 1–3 not significant, consistent with the view that credit-spread information about SPY accumulates over multi-month horizons rather than arriving in a single-month impulse.
- **Quartile return spread (Q1 vs Q4):** Q1 ann_return = +18.6%, Q4 ann_return = −11.3% — absolute spread of **29.9 percentage points**. Sharpe spread = 2.33 units. Max drawdown deteriorates from −13.6% in Q1 to −67.6% in Q4. The monotonicity across all three risk/return metrics is the core empirical punchline for the CCF Evidence narrative.
- **Method consistency check:** The monotonic Q1→Q4 gradient is directionally consistent with the pre-whitened CCF result (credit spread widening precedes weaker equity returns) and with the transfer-entropy finding (credit → equity TE ≈ 7.6× reverse TE). Narrative space on Evidence page can now cite three independent methods pointing the same direction, up from two.
- **Reverse causality reminder:** the daily-resolution Granger file `core_models_20260410/granger_causality.csv` shows the SPY → HY-IG direction is very strong (F > 50 at every lag), which is the well-known contemporaneous / immediate credit-equity co-movement. The monthly HY-IG → SPY direction documented here is the forecasting-relevant finding and is the one surfaced in the Evidence page.

### Files unchanged

All pre-existing results under `results/hy_ig_v2_spy/` and its subdirectories remain byte-identical to the prior 2026-04-10 and 2026-04-11 states. This Wave-2 fix is additive only — no rerun, no silent rewrite of upstream artifacts.

### Handoff chain

- → **Vera:** consumes `granger_by_lag.csv` and `regime_quartile_returns.csv` per `handoff_to_vera_20260419.md`. Produces standalone Granger and quartile-return charts.
- → **Ray:** may cite the new Sharpe spread (2.33 units) and best-lag p-value (0.0014) in the Evidence narrative. No specification changes; narrative-level updates only.
- → **Ace:** Evidence page chart slots for Granger and Quartile-Returns remain the same canonical filenames; once Vera publishes, Ace just swaps the chart JSON.

## Approved by

**Lesandro** — Wave-2 scope explicitly bounded to closing S18-8 and S18-11 via ECON-E1/E2/H4 application. No other pairs touched, no tournament rerun, no headline-number changes to winner metrics.

## Vera's Wave 2 Changes (2026-04-19)

### Chart files produced

**Canonical historical-episode zoom charts** (under `output/_comparison/`, per META-ZI default path):

1. `output/_comparison/history_zoom_dotcom.json` (+ `_meta.json`) — HY-IG OAS spread, 1998-01 → 2003-12, 4 event markers (Dot-Com peak, 400 bps crossing, NBER recession start, WorldCom), NBER shading + caption disclosure.
2. `output/_comparison/history_zoom_gfc.json` (+ `_meta.json`) — HY-IG OAS spread, 2005-01 → 2010-12, 5 event markers (BNP Paribas, spread widening, Bear Stearns, Lehman, NBER recession end), NBER shading + caption disclosure.
3. `output/_comparison/history_zoom_covid.json` (+ `_meta.json`) — HY-IG OAS spread, 2019-01 → 2022-12, 3 event markers (pandemic declared, spread peak ~1100 bps, Fed credit facilities), NBER shading + caption disclosure.

**HY-IG v2 standalone method charts** (under `output/charts/hy_ig_v2_spy/plotly/`):

4. `granger_f_by_lag.json` (+ `_meta.json`) — F-statistic bar chart by lag 1–12, red bars at p < 0.05, dashed F-critical (5%) reference line. Consumes `results/hy_ig_v2_spy/granger_by_lag.csv` (Evan). Replaces the silent Local Projections fallback previously served under the Granger heading.
5. `regime_quartile_returns.json` (+ `_meta.json`) — Annualized SPY return bar chart by HY-IG spread quartile Q1–Q4, green-to-red gradient (Q1 tightest = green, Q4 widest = red), zero-line reference. Consumes `results/hy_ig_v2_spy/regime_quartile_returns.csv` (Evan).

### Chart files modified

6. `output/charts/hy_ig_v2_spy/plotly/hero.json` (+ `hero_meta.json`) — Added NBER recession shading (3 grey rectangles for 2001, 2007-09, 2020 windows). Added caption disclosure annotation "Vertical shaded bands mark NBER recessions." Added annualized-return overlay callout in top-right corner: "SPY Annualized return: 7.8% (2000–2025 sample)". Bottom margin bumped to 110 px so the NBER caption is visible.

### Rule IDs addressed

- **VIZ-V1** (Canonical + Override zoom-in loader contract) — All three episode zooms produced at canonical `output/_comparison/` path per META-ZI default; no HY-IG-specific override produced in this iteration.
- **VIZ-V2** (NBER shading + caption disclosure) — Applied to all three zoom charts and restored on the hero.
- **VIZ-V3** (No silent fallbacks) — `granger_f_by_lag.json` now ships as the dedicated Granger artifact; the per-method ownership chain (Evan artifact → Vera chart → Ace portal slot) is intact.
- **VIZ-V4** (No silent drops of diagnostic charts) — `regime_quartile_returns.json` restores the Q1–Q4 annualized SPY return chart that was silently dropped in the HY-IG v2 polish.
- **META-ZI** (Canonical + override artifact model) — Canonical zoom-in charts live once at `output/_comparison/`; reused across pairs. No pair-specific overrides produced this iteration (Ray will flag if an HY-IG indicator overlay is needed; see cross-agent contract below).

### Stakeholder items closed (chart side)

- **S18-8 (Half-closed → Closed)** — Annualized SPY return Q1–Q4 bar chart restored via `regime_quartile_returns.json`. Visually communicates the Q1-tightest → Q4-widest monotonic gradient (Q1 = +18.6% ann. return; Q4 = −11.3%).
- **S18-11 (Open → Closed)** — Granger chart now has its own figure (`granger_f_by_lag.json`) instead of silently re-serving the Local Projections artifact.
- **SL-2 (Open → Closed)** — Hero chart NBER caption disclosure AND annualized-return callout both restored. Chart now self-documents the recession shading and carries the "SPY Annualized return: 7.8%" overlay that was dropped in the prior hero polish.
- **SL-4 (Open → Closed for HY-IG v2)** — Dot-Com episode zoom-in `history_zoom_dotcom.json` produced per SL-4 worked example; event markers match the sketched dates (Mar 2000, Aug 2000, Mar 2001, Jul 2002).
- **SL-5 (Open → Closed for HY-IG v2)** — GFC episode zoom-in `history_zoom_gfc.json` produced per SL-5 parallel; event markers cover the Aug 2007 → Jun 2009 window with the stakeholder-requested Oct 2007 and Bear/Lehman dates.
- **SL-3** — Not directly addressed in this dispatch (that item concerns heatmap/text drift, which requires a coupled Ray narrative update). This wave only adds chart artifacts; Ray's narrative should be refreshed in a separate coupled entry per the Chart-Text Coherence contract.

### Cross-agent contract notes

- **Canonical-only this iteration:** No pair-specific `output/charts/hy_ig_v2_spy/history_zoom_*.json` override produced. If Ray's narrative coherence check on the Story page determines that the HY-IG v2 prose ties any episode to HY-IG-specific indicator behavior (e.g., "HY-IG spread widened 450 bps as Lehman fell"), Ray flags "override needed" per VIZ-V1 cross-agent contract and a pair-specific override chart will be added starting from the canonical baseline.
- **Ace loader fallback chain:** Per META-ZI / GATE-25, Ace's portal loader should try `output/charts/{pair_id}/history_zoom_{slug}.json` first, then `output/_comparison/history_zoom_{slug}.json`, else render a "chart pending" placeholder. Today only the canonical tier is populated for these three episodes.
- **Chart-text coherence:** Because the hero now carries an annualized-return overlay and an NBER caption, Ray should review the Story hero caption and any prose referencing these figures to confirm consistency. No chart semantics changed (no inversion, no signal swap), so the coherence review is lightweight.

### Files NOT touched

- No other pairs' charts modified.
- No narrative content (`content/*_narrative.py` or similar) modified — that is Ray's scope.
- No portal code (`app/`) modified — that is Ace's scope.
- The legacy `hy_ig_v2_spy_*.json` files (pair-id-prefixed filenames) left in place; they are audit-trail artifacts from a prior rerun and do not block the canonical `{chart_type}.json` loader path.

### Approved by

**Vera self-approves** the visualization-layer changes; all four rules (VIZ-V1 through V4) applied as written and the hero-chart update is a faithful restoration of the prior-version overlay set (SL-2 explicit ask). Lesandro review requested at next checkpoint if any rendered output looks off.

## Ray's Wave 2 Changes (2026-04-19)

### Narrative sections modified

All edits applied to `docs/portal_narrative_hy_ig_v2_spy_20260410.md` (in place; filename retained per established pair convention).

1. **Page 1 headline restructure (RES-11, closes SL-1).** Replaced the Page 1 ordering so the `## Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns` headline and 3-KPI subhead (Sharpe, annualized return, max drawdown) sit at the top. "Where This Fits in the Portal," "How to read the rest of this page pack," and the One-Sentence Thesis follow the headline. The old "**The headline.**" inline paragraph was removed -- its content is now the H2 headline plus the bulleted KPI metrics.
2. **Headline Findings for KPI Cards — investor-impact rewrite (RES-9, closes S18-12 partial).** Appended a "What this means for investors" clause to each of the five bullets, converting each from observation-only to observation + concrete action implication.
3. **The Early Warning Signal — investor-impact rewrite (RES-9, closes S18-12 partial).** Appended a "What this means for investors" clause to each of the three mechanism bullets (bond investors wired for caution; banks trade on private information; the bond market is harder to fool), each naming a concrete action (head-start, trim toward bond view, treat divergence as equity complacency).
4. **What History Shows — historical-episode cross-references (RES-8, closes SL-4 and SL-5 narrative side).** Added explicit parenthetical cross-references to the canonical Vera zoom-in chart paths for all three episodes: Dot-Com (`output/_comparison/history_zoom_dotcom.json`), GFC (`output/_comparison/history_zoom_gfc.json`), and COVID (`output/_comparison/history_zoom_covid.json`). Each cross-reference lists the labelled event markers so the reader can locate them on the chart.
5. **Page 4 — How the Signal is Generated (RES-7, closes S18-1 narrative side).** Inserted a new subsection at the top of Page 4 (before "How the Signal Translates to Action"). Three short paragraphs, zero formulas, three-step mechanism (world event → what the HMM detects → action taken). Explicitly points readers to the Methodology page for the formal specification.

### Rule IDs addressed

- **RES-7** — "How the Signal is Generated" subsection on Strategy page, plain-English, no formulas, 2-3 paragraphs.
- **RES-8** — Every historical episode named in prose (Dot-Com, GFC, COVID) now carries an explicit cross-reference to the canonical Vera zoom-in artifact path. Coherence inspection completed — see override note below.
- **RES-9** — Every bullet in the Page 1 Headline Findings and Page 2 Early Warning Signal lists now carries a "What this means for investors" action-implication clause.
- **RES-10** — Canonical status vocabulary (Available / Pending / Validated / Stale / Draft / Mature / Unknown) added to `docs/portal_glossary.json` with one-sentence definitions for each.
- **RES-11** — Page 1 opens with the metric-headline structure (`## [headline]` followed by KPI bullets); narrative and Where-This-Fits context come after.
- **RES-VS** — Narrative Vocabulary Self-Check passed. `Grep` over the narrative found no novel status labels in prose; the only `chart_status:` tokens present (`"ready"`) are artifact-lifecycle codes defined in the SOP chart_status subsection, not reader-facing status vocabulary. No rewrites needed in prose; canonical glossary entries added proactively to support portal caption consistency.

### Stakeholder items closed

- **S18-1 (partial — narrative side only)** — "How the Signal is Generated" subsection added. Full closure requires Ace's Probability Engine + Position Adjustment panels (S18-1 chart side) to be implemented; those are out of this dispatch's scope.
- **S18-4 follow-up** — Status vocabulary glossary entries created in `docs/portal_glossary.json`.
- **S18-12** — Every Early Warning Signal bullet and every Page 1 Headline Findings bullet now carries an investor-impact clause.
- **SL-1** — Page 1 restructured to headline-first per RES-11.
- **SL-4** — Dot-Com episode cross-referenced to `output/_comparison/history_zoom_dotcom.json` in the "What History Shows" paragraph.
- **SL-5** — GFC episode cross-referenced to `output/_comparison/history_zoom_gfc.json` in the "What History Shows" paragraph.

### Coherence inspection and override candidates for Vera

Per RES-8, Ray inspected each prose reference against the canonical zoom chart and asked: "Does this chart make the point the narrative is trying to make?"

- **Dot-Com:** Prose is episode-only (WorldCom, telecom implosion, lead-time caveat). **Canonical sufficient. No override needed.**
- **GFC:** Prose refers to "roughly five months of warning," "HY-IG spread had already reached roughly 800 basis points," and "an investor who moved to cash when spreads crossed 2 standard deviations above their rolling mean." The first two are event-only narrative supported by the canonical HY-IG OAS line. The third names a specific statistical trigger (2-sigma rolling band) which the canonical chart does not display. **Canonical sufficient for the primary prose; flag for Vera:** if the stakeholder gate tightens, consider an HY-IG override variant with a 2-sigma rolling band overlay (label: `history_zoom_gfc_hyig_2sigma.json`). Not a blocker for Wave 2 closure.
- **COVID:** Prose spans "surged from about 350 to 1,100 basis points (3.5% to 11%) in just five weeks" -- event-only, well supported by the canonical chart. **Canonical sufficient. No override needed.**

**Override candidates for Vera (non-blocking):**

1. *(GFC only, low priority)* Optional HY-IG v2 override variant of `history_zoom_gfc.json` with a 2-sigma rolling-mean band overlay, to illustrate the "2 standard deviations above their rolling mean" trigger cited in the What History Shows paragraph. Only produce if the stakeholder review flags the trigger reference as under-illustrated; otherwise the canonical chart carries the episode narrative.

### Glossary entries added or updated

`docs/portal_glossary.json` was created in this dispatch (file did not previously exist as a JSON canonical source of truth). Entries added:

- `status_labels.Available`, `status_labels.Pending`, `status_labels.Validated`, `status_labels.Stale`, `status_labels.Draft`, `status_labels.Mature`, `status_labels.Unknown` — one-sentence definitions per RES-10.
- `terms.Basis point (bp)`, `terms.Credit spread`, `terms.HMM stress probability` — 3 starter entries in the 4-element rubric reduced form (plain_english / why_it_matters / example) to give Ace a canonical JSON schema to consume. Backfill of the full HY-IG v2 glossary from `app/components/glossary.py` into `docs/portal_glossary.json` is tracked separately per SOP §Backfill.

### Files unchanged

- Evan's artifacts (`results/hy_ig_v2_spy/*`) — untouched (scope: Evan).
- Vera's chart JSONs — untouched (scope: Vera).
- Ace's portal pages (`app/pages/*`, `app/components/glossary.py`) — untouched (scope: Ace). Glossary content edits flow through the new `docs/portal_glossary.json`; `app/components/glossary.py` is Ace's rendering helper and is edited by Ace, not Ray.
- The ~17-entry References bibliography at the bottom of the narrative — preserved verbatim.
- All Evidence method blocks (Correlation → Quartile Returns) — preserved; only the Page 1 header stack and the Page 2 / Page 4 narrative subsections were modified.

### Approved by

**Ray self-approves** the narrative-layer changes; all six new rules (RES-7, RES-8, RES-9, RES-10, RES-11, RES-VS) applied as written. Lesandro review requested at next checkpoint, with attention to: (a) the headline wording "multi-month early-warning signal" (kept indicator-agnostic rather than pinning to a single lead-time figure), and (b) the GFC override-candidate flag (currently logged as low-priority; upgrade if stakeholder wants the 2-sigma band visualized).

## Ace's Wave 2B Changes (2026-04-19)

### Components created

Four new standard components under `app/components/`, each self-contained and parameterised by `pair_id`:

1. `app/components/probability_engine_panel.py` (~260 lines) — `render_probability_engine_panel(pair_id)`. Loads latest `signals_*.parquet`, resolves signal column via `winner_summary.signal_code` map, runs **pre-render validation** (column presence, numeric bounds, GFC/COVID historical-plausibility check) before rendering. On failure, `st.error()` with diagnostic and the chart is skipped. On success, Plotly time-series with threshold line, epsilon band for continuous signals, and NBER shading when the span exceeds 5 years. Writes its validation outcome to `st.session_state` for APP-SE2 to consume.
2. `app/components/position_adjustment_panel.py` (~160 lines) — `render_position_adjustment_panel(pair_id)`. Gated on SE1 validation state — if SE1 failed, renders `st.warning("Position exposure cannot be derived without valid signal values.")` and skips the chart (per the Wave 1.5 "derived from SE1" contract). Computes exposure per strategy family (P1 binary, P2 continuous, P3 long/short) with direction-aware sign flip. Plotly area chart.
3. `app/components/instructional_trigger_cards.py` (~210 lines) — `render_instructional_trigger_cards(pair_id)`. 2-3 cards via `st.columns()` + `st.container(border=True)`. Thresholds **loaded from `winner_summary.json.threshold_value`** (Defense-2 reconciliation with the strategy's runtime rule). Strategy-family-aware card specs (P1 BUY/HOLD/REDUCE, P2 continuous scaling, P3 LONG/SHORT). Stylised sparklines (50×100) illustrating each crossing.
4. `app/components/live_execution_placeholder.py` (~60 lines) — `render_live_execution_placeholder(pair_id)`. Section titled "Future: Live Execution" with three `st.metric()` cards (Current Signal State / Target Position / Current Action). Reads `results/{pair_id}/live_execution_stub.json` if present, else renders `"—"` placeholders. Mandatory `st.info()` callout explaining historical-dashboard scope.

### Chart loader META-ZI implementation

Updated `app/components/charts.py`:

- New `_resolve_history_zoom_paths(chart_name, pair_id)` helper implements the Canonical + Override fallback chain per META-ZI: tries `output/charts/{pair_id}/history_zoom_{episode}.json` first, falls back to `output/_comparison/history_zoom_{episode}.json`. Called automatically by `load_plotly_chart()` when `chart_name` starts with `history_zoom_`.
- Code comments cite META-ZI, VIZ-V1, and GATE-25. Missing chart → GATE-25 "chart pending" placeholder (the existing `st.info()` fallback); no silent substitution.

Confirmed resolution against the three episodes published by Vera in Wave 2A (all three resolve to the canonical `output/_comparison/` path since no HY-IG-specific overrides were produced this iteration).

### Pages modified

1. `app/pages/9_hy_ig_v2_spy_story.py` — **headline-first restructure (SL-1)**: pulled the new `## Sharpe 1.27 …` H2 headline + KPI bullets to the top; Where-This-Fits + page-pack orientation follow. Investor-impact bullets rendered in the new "Headline Findings" list (RES-9 / S18-12). New "What History Shows" subsections (Dot-Com / GFC / COVID / 2022) each render the canonical zoom chart via the META-ZI loader (RES-8, SL-4, SL-5). Status-vocabulary legend expander appended at page bottom.
2. `app/pages/9_hy_ig_v2_spy_evidence.py` — **Granger block** now consumes `granger_f_by_lag.json` (closes S18-11; no more silent Local Projections fallback). `how_to_read`, `observation`, and `chart_caption` rewritten to reflect monthly-resolution F-by-lag semantics (best lag 5, F = 4.07, p = 0.0014). **Quartile Returns block** now consumes `regime_quartile_returns.json` and cites Evan's monthly-resolution numbers (Q1 Sharpe 1.79, Q4 −0.53, 29.9 pp return spread, 2.33 Sharpe-units spread); deep-dive content updated to reflect monthly sample; closes S18-8. All other method blocks unchanged.
3. `app/pages/9_hy_ig_v2_spy_strategy.py` — full restructure to Execute / Performance / Confidence tabs. Ray's new "How the Signal is Generated" plain-English section rendered BEFORE KPI cards (RES-7, closes S18-1 narrative side). Execute tab: Strategy Summary + APP-SE1 + APP-SE2 + APP-SE3 + Execution Points table + How to Use Manually + COVID example. Performance tab: equity curves + drawdown + trade log narrative + dual-download CSVs + preview (each with a 1-line APP-SE5 takeaway caption). Confidence tab: stress tests, signal decay, walk-forward (each with its own takeaway caption); Tournament Leaderboard; Explore Alternative Strategies; Where the Strategy Adds Value; Important Caveats. "Future: Live Execution" section (APP-SE4) rendered at the bottom.
4. `app/pages/9_hy_ig_v2_spy_methodology.py` — light-touch: status-vocabulary legend expander loaded from `docs/portal_glossary.json` added near the top. All other content unchanged.

### Rule IDs addressed

- **APP-SE1** (Probability Engine Panel + Wave 1.5 pre-render validation) — component created, wired into Strategy > Execute tab; validation verified against `signals_20260410.parquet`.
- **APP-SE2** (Position Adjustment Panel + Wave 1.5 SE1-derived gate) — component created, wired below SE1; gated on `st.session_state[f"se1_validation_{pair_id}"].ok`.
- **APP-SE3** (Instructional Trigger Cards + Wave 1.5 Defense-2 threshold reconciliation) — component created, rendered below SE2. Thresholds loaded from `winner_summary.json` so user-manual view cannot drift from runtime rule.
- **APP-SE4** (Real-time Execution Placeholder) — component created, rendered at bottom of Strategy page; reads optional `live_execution_stub.json`.
- **APP-SE5** (Universal Takeaway Caption) — every table/chart in the Confidence tab carries a dedicated `st.caption()` takeaway; Performance tab equity-curve, drawdown, and trade-log preview also carry takeaways; SE1 and SE2 panels each carry takeaway captions.
- **META-ZI** (Loader contract) — `charts.py::_resolve_history_zoom_paths()` implements per-pair override → canonical fallback for `history_zoom_*` charts. Wired into Story page's "What History Shows" section.
- **§3.12 Status Vocabulary Discipline + RES-10** — Story, Strategy (Confidence tab), and Methodology pages each expose a status-labels legend expander loaded from `docs/portal_glossary.json`.

### Stakeholder items closed

- **S18-1 (Closed, chart + narrative sides together)** — Probability Engine Panel (APP-SE1) + Position Adjustment Panel (APP-SE2) + Ray's "How the Signal is Generated" plain-English section all now render on the Strategy page.
- **S18-3** — Confidence-section tables and charts carry `st.caption()` takeaways (APP-SE5).
- **S18-8** — Evidence-page Quartile Returns block consumes Evan's new `regime_quartile_returns.csv` → Vera's `regime_quartile_returns.json`.
- **S18-9** — Instructional Trigger Cards (APP-SE3) rendered in Strategy > Execute tab.
- **S18-10** — Future: Live Execution section (APP-SE4) rendered at bottom of Strategy page.
- **S18-11** — Evidence-page Granger block consumes `granger_f_by_lag.json`, no more silent Local-Projections fallback.
- **SL-1** — Story page restructured headline-first.

### Defense-2 validation outcomes (HY-IG v2)

Pre-flight checks run against `results/hy_ig_v2_spy/`:

- **Signal column present**: `hmm_2state_prob_stress` exists in `signals_20260410.parquet` ✅
- **Numeric bounds**: probability signal in `[0, 1]` (min 0.0000, max 1.0000) ✅
- **GFC plausibility**: max stress probability in 2008-09 → 2009-06 window = 1.0000 > threshold 0.5 ✅
- **COVID plausibility**: max stress probability in 2020-02 → 2020-04 window = 1.0000 > threshold 0.5 ✅
- **Threshold reconciliation (APP-SE3 cards ↔ winner)**: both read from `winner_summary.json.threshold_value = 0.5` ✅
- **META-ZI resolution**: Dot-Com, GFC, COVID zooms all resolve to `output/_comparison/` canonical tier ✅

No validation failures or warnings flagged for HY-IG v2. The APP-SE1 pre-render path is exercised end-to-end and returns `ok=True`; APP-SE2 receives the gate-passed state; APP-SE3 thresholds match the strategy's runtime rule.

### Files NOT touched

- No artifacts under `results/hy_ig_v2_spy/*` modified (Evan's scope).
- No chart JSONs under `output/charts/hy_ig_v2_spy/plotly/` or `output/_comparison/` modified (Vera's scope).
- No narrative document `docs/portal_narrative_hy_ig_v2_spy_20260410.md` modified (Ray's scope).
- No glossary JSON `docs/portal_glossary.json` modified (Ray's scope); Ace's pages consume it read-only.
- Other pairs' pages (`1_*`, `2_*`, `5_*`, etc.) untouched.

### Approved by

**Ace self-approves** the portal-layer assembly; all five APP-SE rules (SE1–SE5) + META-ZI loader + Status Vocabulary Discipline applied as written. All four pages load cleanly (`python3 -m py_compile` passes on each). Defense-2 validations pass against the HY-IG v2 artifact set. Lesandro review requested at next checkpoint.

---

### Ace's Bug-fix patch (2026-04-19)

**Trigger.** Post-Wave-2 stakeholder review flagged Bug #2: the Dot-Com zoom chart on the Story page rendered as the GATE-25 "chart pending" placeholder, even though `output/_comparison/history_zoom_dotcom.json` existed (59 KB, valid Plotly JSON with one trace and a title) and `_resolve_history_zoom_paths('history_zoom_dotcom', 'hy_ig_v2_spy')` returned that path with `exists=True`.

**Root cause of loader None-return.** `app/components/charts.py::load_plotly_chart` was a render-only function — it invoked `st.plotly_chart(...)` as a side-effect and returned `None` unconditionally. That design had two consequences that combined into Bug #2:

1. **No observable end-to-end signal.** Because the function had no return value, nothing at the call site could distinguish "chart rendered" from "GATE-25 placeholder rendered" from "silent parse failure." Defense-2 as extended in Wave 1.5 could confirm the artifact existed on disk, but could not confirm the Figure actually loaded and had traces + title. The Wave-2 review caught a visibly-broken chart that the Wave-1.5 gate had approved.
2. **Silent exception swallowing risk.** The cached `_load_plotly_json` was wrapped in `@st.cache_resource`. Any parse-time exception from `pio.from_json` (e.g., encoding quirk, plotly version upgrade, stale cache entry) had no outer `except` handler — it would propagate, terminate the block, and the user would see whatever Streamlit paints in that state (in this case, an empty region visually indistinguishable from the GATE-25 info box). No warning, no log, no path to triage.

**charts.py lines changed.**

- Added `import logging` and a module-level `_LOGGER`.
- `_load_plotly_json` docstring updated to state that exceptions are intentionally propagated (consumer handles them).
- `load_plotly_chart`: introduced `fig = None` init; wrapped the `_load_plotly_json` call in `try/except` with a `_LOGGER.warning(...)` + `st.warning(...)` on failure so parse errors surface visibly instead of degrading silently. The GATE-25 `st.info(fallback_text)` placeholder now fires only when `not json_path` (no artifact on disk) — a parse failure emits a distinct, user-visible warning instead.
- `load_plotly_chart` now **returns the Figure** (or `None` on miss / parse failure) so smoke tests and any future caller can assert load success. Rendering side-effect is unchanged.

**SOP fix: Defense-2 extended with loader smoke test.** `docs/agent-sops/appdev-agent-sop.md` Defense-2 section extended with a new "Loader end-to-end smoke test" block (rule ID **APP-ST1**). Requirements: AST-parse each page (plus a literal registry for dynamic `chart_name` variables in helper functions), execute `load_plotly_chart` under a Streamlit mock for each call site, assert non-None Figure + `len(fig.data) > 0` + non-empty `fig.layout.title.text`, log per-call results to `app/_smoke_tests/loader_{pair_id}_{yyyymmdd}.log`. Any FAIL is a blocker. Root-cause narrative for Bug #2 captured inline in the SOP so future Ace instances see the same lesson in their onboarding read.

**standards.md row added.** New row **APP-ST1** (Loader End-to-End Smoke Test) appended to the APP-* block, referencing the Defense-2 (Loader E2E) subsection. The existing APP-D2 row (Numerical Reconciliation) is unchanged; APP-ST1 is a distinct rule focused on render-path integrity rather than value reconciliation.

**Retro-application.** Smoke-test harness built at `app/_smoke_tests/smoke_loader.py` and run against HY-IG v2 (`python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy`). Result:

- **passes = 15**, **failures = 0**, skips = 1 (the dynamic-chart AST site at `9_hy_ig_v2_spy_evidence.py:139`, which is resolved via the supplemental `EVIDENCE_DYNAMIC_CHARTS` literal list; all 8 Evidence charts pass).
- Bug #2 specifically: `history_zoom_dotcom` now returns a Figure with 1 trace and title "Credit Spreads During the Dot-Com Bust, 1998–2003". The two sibling zoom charts (`history_zoom_gfc`, `history_zoom_covid`) also pass.
- Log written to `app/_smoke_tests/loader_hy_ig_v2_spy_20260419.log`.

**Gate-failure learning.** *"Artifact-existence checks are not rendering checks. Load end-to-end or you can't know."* The Wave 1.5 Defense-2 extension correctly verified that the canonical Plotly JSON existed on disk and that the resolver returned the right path. That was necessary but not sufficient — it could not surface a render-path failure because the loader had no return channel. Any future Defense-2-style check built around "the file exists and the path resolver works" must be paired with an end-to-end load-and-assert on the object that the file decodes into.

### Lead's Wave 3 Gate Patches (2026-04-19)

**Trigger.** Post-Wave-2 stakeholder review exposed two bugs that slipped past every existing gate:

1. **Hero NBER shading imperceptible.** VIZ-V2 was followed to the letter (grey rectangles, alpha in the 0.10–0.15 prescribed range) and the rendered shading was still invisible against the dark line trace on the chart's light background. Compliance with the numeric prescription did not produce the intended visual.
2. **Dot-Com canonical zoom loader returned None.** The canonical artifact file existed at `output/_comparison/history_zoom_dotcom.json`, the META-ZI loader path resolved correctly, the file parsed as JSON, and yet `load_plotly_chart()` returned None in the portal — so the Story page rendered the GATE-25 "chart pending" placeholder on the reference pair.

Both are gate-layer failures, not producer failures. Existing Playwright verification checks DOM text/element presence, not visual correctness. Existing Defense-2 checks artifact existence and structural parse, not end-to-end loader success. Existing GATE-25 rightly allows "chart pending" as graceful degradation — but on a reference pair, graceful degradation is a regression, not acceptable behavior.

**Fix the gates, not the symptoms.**

#### Gate fixes registered

- **GATE-27 — End-to-End Chart Render Test (blocking).** Every chart referenced by any portal page of a pair under acceptance must load via `load_plotly_chart(name, pair_id)` as a non-None Figure, carry ≥1 data trace, and have a non-empty title. Vera runs VIZ-V5 smoke tests on all canonical artifacts; Ace runs a loader smoke-test extension of Defense-2 that exercises `load_plotly_chart()` for every chart referenced by every portal page. Both agents attach their smoke-test logs to acceptance.md. Directly addresses the Dot-Com canonical-zoom loader bug.
- **GATE-28 — Reference-Pair Placeholder Prohibition (blocking).** On reference-pair pages, any "chart pending" placeholder (the GATE-25 fallback) is an acceptance blocker. Headless-browser DOM audit must return zero `chart_pending` occurrences across Story / Evidence / Strategy / Methodology pages of the reference pair. Directly addresses the gate-layer gap that allowed the Dot-Com placeholder to pass Wave 2B verification.
- **META-PV — Perceptual Validation of Visual Encoding (meta-rule).** Any chart element that depends on color, alpha, shading, or low-contrast visual encoding for information transfer requires a perceptual-validation step in the producing agent's SOP: render to PNG via `plotly.io.write_image` and visually confirm the encoding is perceivable against realistic backgrounds and data traces. Rules that prescribe numeric values (alpha ranges, stroke widths, font sizes) must be validated against perceptual output, not assumed. Directly addresses the Hero NBER shading bug. Companion to META-VNC and META-RNF; operationalized by GATE-27.

All three rules are registered in `docs/standards.md` under the GATE and META sections, and the Pair Acceptance Checklist template in `docs/agent-sops/team-coordination.md` has been extended with GATE-27 (smoke-test logs attached, zero null loads) and GATE-28 (reference-pair DOM audit, zero `chart_pending` occurrences) as blocking items.

#### Gate-failure learning

> **Existence checks are not rendering checks.**
> **Rule prescriptions that were never validated perceptually are untested assumptions.**
> **Fix the rules.**

The common thread across both Wave-3 bugs is misplaced trust in intermediate artifacts — file-on-disk trust (Dot-Com) and numeric-prescription trust (NBER alpha). A gate that proves the file exists but does not prove the rendered page shows the intended content is not a complete gate; a rule that prescribes a numeric value but does not require perceptual confirmation is not a complete rule. The Wave-3 patches shift the final verification from "intermediate artifact" to "rendered page DOM" (GATE-28) and "rendered PNG" (META-PV), and from "file-exists" to "loader-returns-a-valid-Figure" (GATE-27).

#### Scope and approval

- **SOP scope:** Vera and Ace are each updating their producer SOPs in parallel to add VIZ-V5 (smoke-test procedure + perceptual-validation step for shading/alpha encodings) and the Defense-2 loader-smoke-test extension respectively. Lead Lesandro owns the gate registration (standards.md, team-coordination.md, this regression note).
- **Pair scope:** no artifacts under `results/hy_ig_v2_spy/*`, `output/charts/hy_ig_v2_spy/*`, `output/_comparison/*`, or `app/pages/9_hy_ig_v2_spy_*.py` are modified by this Wave-3 gate patch. Remediation of the two underlying bugs (re-render hero with perceptible NBER shading; fix Dot-Com loader path) is tracked under Vera's and Ace's parallel Wave-3 dispatches and will be captured in a follow-up entry when the reference pair clears GATE-27 and GATE-28.
- **Approved by:** Lead Lesandro. Gate additions do not require producer sign-off; producer SOP updates require the owning agent's self-approval per the standard SOP-change protocol.


---

### Vera's Bug-fix patch (2026-04-19)

**Root cause.** The post-Wave-2 stakeholder review caught two NBER-shading bugs on HY-IG v2 that the existing SOPs failed to prevent. Both bugs cleared prior Quality Gates because the **VIZ-V2 rule as written was wrong**, not because it was unfollowed.

1. **Imperceptible alpha.** Rule V2 prescribed "alpha 0.1–0.15, grey". Against the Streamlit off-white background, grey at alpha 0.12 is not visually distinguishable from the plot canvas. The hero caption truthfully disclosed "Vertical shaded bands mark NBER recessions," but there was nothing to see.
2. **Single-xref on a dual-panel hero.** Rule V2 said nothing about subplots. The hero chart is a two-panel layout (`xaxis` = HY-IG spread, `xaxis2` = SPY price). The three existing shapes all had `xref='x'`, so only the top panel carried shading; the bottom SPY panel had no shading at all, and the caption's claim was half-true.

**SOP fix.**

- **VIZ-V2 revised (docs/agent-sops/visualization-agent-sop.md):**
  - Alpha prescription bumped to **0.20–0.28**, default fill `rgba(150,120,120,0.22)` (faded red-brown); plain grey at alpha < 0.18 prohibited.
  - Added mandatory **subplot handling clause**: one shading shape per panel per recession; inspect `layout` for `xaxis/xaxis2/xaxis3…`; total shape count = `n_recessions × n_panels`.
  - Added mandatory **perceptual-validation step**: after saving JSON, render a PNG via `plotly.io.from_json` + `fig.write_image` (kaleido), save to `_perceptual_check_{chart}.png`, and confirm shading is perceptible at standard zoom. Failure fails **GATE-27 (End-to-End Chart Render Test)**.
- **VIZ-V5 added:** End-to-End Chart Load Smoke Test. Before handoff, Vera runs a smoke-test script per chart: (1) `plotly.io.read_json` loads cleanly, (2) `len(fig.data) > 0`, (3) `fig.layout.title.text` non-empty. Pass/fail logged to `output/charts/{pair_id}/plotly/_smoke_test_{YYYYMMDD}.log`; any fail blocks handoff.
- **docs/standards.md updated:** VIZ-V2 row carries `rev 2026-04-19` note citing the new alpha/subplot/perceptual-check clauses; VIZ-V5 row added.
- **docs/sop-changelog.md updated:** 2026-04-19 entry added describing the revision and the retro-application.

**Retro-application.** Four charts updated using the new rule:

| Chart | Path | Change |
|-------|------|--------|
| Hero (dual-panel) | `output/charts/hy_ig_v2_spy/plotly/hero.json` | 3 old shapes (grey 127/127/127 alpha 0.12, `xref=x` only) replaced with **6 new shapes** — 3 recessions × 2 panels (`xref=x` + `xref=x2`), `fillcolor='rgba(150,120,120,0.22)'`, `layer='below'`, `yref='paper'` |
| Zoom — Dot-Com | `output/_comparison/history_zoom_dotcom.json` | 1 NBER shape (of 5 total; 4 others are event vlines) recolored to `rgba(150,120,120,0.22)` |
| Zoom — GFC | `output/_comparison/history_zoom_gfc.json` | 1 NBER shape (of 6 total) recolored to `rgba(150,120,120,0.22)` |
| Zoom — COVID | `output/_comparison/history_zoom_covid.json` | 1 NBER shape (of 4 total) recolored to `rgba(150,120,120,0.22)` |

Recession episode coordinates (2001-03 to 2001-11, 2007-12 to 2009-06, 2020-02 to 2020-04) unchanged. Existing NBER disclosure caption annotations preserved. Hero's annualized-return corner callout preserved.

**Perceptual-check PNGs (new per updated VIZ-V2; visually confirmed by Vera):**

- `output/charts/hy_ig_v2_spy/plotly/_perceptual_check_hero.png` — confirmed: NBER bands visible in BOTH the top HY-IG panel and the bottom SPY panel at 2001, 2008–09, and 2020.
- `output/_comparison/_perceptual_check_history_zoom_dotcom.png` — confirmed: 2001 NBER band clearly visible against the spread chart.
- `output/_comparison/_perceptual_check_history_zoom_gfc.png` — confirmed: 2007–09 NBER band clearly visible.
- `output/_comparison/_perceptual_check_history_zoom_covid.png` — confirmed: 2020 NBER band clearly visible against the tight zoom.

**Smoke-test log (VIZ-V5):** `output/charts/hy_ig_v2_spy/plotly/_smoke_test_20260419.log` — 10 charts tested, **10 pass, 0 fail**. Covered: `hero`, `correlation_heatmap`, `ccf_prewhitened`, `granger_f_by_lag`, `quartile_returns`, `regime_quartile_returns`, `transfer_entropy`, plus the 3 canonical episode zooms.

**Gate-failure learning.** *"Rule was followed; rule was wrong. Fix the rule."* Both bugs were preventable had VIZ-V2 carried (a) a perceptible alpha prescription, (b) a subplot-coverage clause, and (c) a perceptual-validation step — all three are now in the revised rule. VIZ-V5's smoke test catches the orthogonal structural-integrity failure mode (empty/corrupt/untitled JSON). This closes the gap that allowed a chart with an invisible/half-applied regime layer to ship through a passing completeness gate.

**Approved by.** Vera self-approves the SOP revisions and retro-application; escalates to Lead Lesandro for GATE-27 registration and Wave-3 commit.

---

### Evan's Deploy-Artifact Allowlist (2026-04-19)

**Trigger.** Stakeholder-reported bug: Probability Engine Panel on Streamlit Cloud returned `No signals_*.parquet under /mount/src/aig-rlic-plus/results/hy_ig_v2_spy`. Local investigation showed `signals_20260410.parquet` (720 KB) existed in the developer's working tree but was never committed to git — the repo-root `.gitignore` had a blanket `*.parquet` rule that silently suppressed `git add`, so Cloud never saw the file.

**Root cause.** `ECON-DS1` stopped at "persist signals to `signals_{date}.parquet`" — it closed the in-process pipeline integrity loop but was silent about the deploy loop. The artifact existed on disk, the tournament read it, but it never made it to the Cloud runtime. The broader SOP system had no rule that named the deploy-required-artifact category. Same hazard applies to the HMM state parquets and Markov regime probability parquets consumed by `app/components/probability_engine_panel.py`, `app/components/position_adjustment_panel.py`, `app/components/execution_panel.py`, and the chart-generation scripts.

**SOP fix.** Added **ECON-DS2 — Deploy-Required Artifact Allowlist (Mandatory)** to `docs/agent-sops/econometrics-agent-sop.md` immediately after ECON-DS1, and registered the rule in `docs/standards.md` under the ECON section. ECON-DS2 codifies two acceptable deployment paths: (a) explicit `.gitignore` carve-out with `!`-pattern allowlist entries plus `git add -f`, suitable for small infrequently-changed artifacts; (b) build-time regeneration script at Cloud boot, suitable for large or fast-to-regenerate artifacts. The producing agent owns the choice and is responsible for wiring in either the allowlist or the regeneration script; the pair's regression note must list every deploy-required artifact with its deployment mechanism. Cross-references GATE-29 (Clean-Checkout Deployment Test) for the gate-side validation. Cross-agent companion to APP-SE1/SE2: read failures on Cloud are symptoms of DS2 violations, not rendering-layer bugs.

**Retro-application — `.gitignore` carve-outs.** The blanket `*.parquet` ignore is retained (large model intermediates should stay out of git by default). Three scoped allowlist entries added immediately after the blanket rule:

```
# Deploy-required parquet artifacts (per ECON-DS2)
!results/**/signals_*.parquet
!results/**/hmm_states_*.parquet
!results/**/markov_regime_probs_*.parquet
```

**Retro-application — files now tracked.** Staged via `git add`:

| File | Size | Consumer |
|------|-----:|----------|
| `results/hy_ig_v2_spy/signals_20260410.parquet` | 720 KB | `app/components/probability_engine_panel.py`, `app/components/position_adjustment_panel.py` |
| `results/hy_ig_v2_spy/core_models_20260410/hmm_states_2state.parquet` | 189 KB | Chart-generation scripts + manifest reference |
| `results/core_models_20260228/hmm_states_2state.parquet` | 185 KB | `scripts/generate_charts.py`, `scripts/tournament_backtest.py` |
| `results/core_models_20260228/hmm_states_3state.parquet` | 256 KB | `scripts/tournament_backtest.py` |
| `results/core_models_20260228/markov_regime_probs_2state.parquet` | 61 KB | `scripts/tournament_backtest.py` |
| `results/core_models_20260228/markov_regime_probs_3state.parquet` | 62 KB | `scripts/tournament_backtest.py` |

`git ls-files 'results/**/*.parquet'` confirms all six are now tracked.

**Coverage verification.** Grep of `pd.read_parquet(` and `glob.glob(...parquet)` in `app/components/` and `app/pages/` returns exactly three call sites: `probability_engine_panel.py:47,275` (signals), `position_adjustment_panel.py:161` (signals, re-use), and `trade_history.py:36` (reads from `data/` not `results/`, outside DS2 scope). The three allowlist patterns (`signals_*`, `hmm_states_*`, `markov_regime_probs_*`) fully cover all Evan-produced parquets read by `app/` code and by the shared chart/backtest scripts that feed app-rendered output.

**Gate-failure learning.** *"'Works on my laptop' is not deployment. Every artifact read by `app/` must survive a clean checkout."* ECON-DS1 closed the in-process persistence loop but left the deploy loop open — a silent failure mode because the producing agent's local tests all passed. The fix is to treat the deploy boundary as a first-class handoff, with an explicit allowlist (or regeneration script) declared per artifact and audited at the gate. Cross-cutting implication: any future Evan-produced artifact consumed by `app/` code must carry its deployment mechanism in the handoff, not as an afterthought discovered only when Cloud's logs return a read error.

**Approved by.** Evan self-approves the SOP addition and retro-application. Lead Lesandro commits after Wave 4A agents finish (DS2 + GATE-29 + smoke-test paired commit).

---

### Lead's Wave 4A Gate Patch (2026-04-19)

**Trigger (stakeholder bug).** Streamlit Cloud returned `Probability engine panel cannot render: No signals_*.parquet under /mount/src/aig-rlic-plus/results/hy_ig_v2_spy` on the HY-IG v2 Strategy page. Local working tree had the file; Cloud's clean checkout did not. Root cause: the repo-root `.gitignore` carried a blanket `*.parquet` rule that silently excluded a deploy-required artifact — `git add` was a no-op against the pattern, so the file was never committed, and the Cloud runtime had no way to resolve it.

**Gate gap.** Existing smoke tests (GATE-27 End-to-End Chart Render, APP-ST1 Loader End-to-End) all run in the developer's working tree where the file exists and the loader returns a non-None Figure. No gate tested a clean-checkout / deployment-clean environment. The bug passed every existing structural and rendering gate because every gate was dev-env scoped. This is the same class of failure as the Wave-3 Dot-Com bug (artifact existed on disk, but something between "on disk" and "rendered in browser" silently broke) — just with the break point shifted from the loader to the deploy boundary.

**Gate fix.** Added **GATE-29 — Clean-Checkout Deployment Test** (blocking) to `docs/agent-sops/team-coordination.md` (Deliverables Completeness Gate row 29, Pair Acceptance Checklist Blocking Items section), and registered the rule in `docs/standards.md` GATE block. Implementation: `git clone --depth 1 "$(git rev-parse --show-toplevel)" /tmp/clean_checkout_{pair_id}` followed by `python3 app/_smoke_tests/smoke_loader.py --pair-id {pair_id}` executed inside the clone. Output log at `app/_smoke_tests/clean_checkout_{pair_id}_{date}.log`; zero FileNotFound / zero None-return / zero placeholder must be asserted. Blocks acceptance for reference pairs. Rationale split from GATE-27: GATE-27 validates rendering in the dev env; GATE-29 validates deployability.

**META-VNC scope extension.** The META-VNC meta-rule (Version-to-Version Content Continuity) had previously been scoped to iterations (v1 → v2 → v3) only. Scope extended in both `docs/agent-sops/team-coordination.md` (Version-to-Version Content Continuity section) and `docs/standards.md` (META-VNC row) to cover cross-environment continuity as well: "Content continuity applies across iterations AND across environments (dev → Cloud). An artifact that works locally but doesn't survive a clean checkout is the same class of bug as an artifact silently dropped across iterations — both are violations of META-VNC." GATE-29 operationalizes the cross-environment axis; GATE-24/25/26 continue to operationalize the cross-iteration axis. Producer-side operationalization of the cross-environment axis is ECON-DS2.

**Cross-reference (Evan, Wave 4A parallel).** ECON-DS2 (Deploy-Required Artifact Allowlist) is the producer-side companion rule. Where GATE-29 is the gate-side verification that the clean-checkout survives end-to-end smoke testing, ECON-DS2 is the producer-side contract that every artifact read by `app/` code is declared deploy-required and wired into the deploy path via one of two mechanisms: (a) explicit `.gitignore` `!`-pattern allowlist entries + `git add -f`, or (b) build-time regeneration script at Cloud boot. Read failures on Cloud are symptoms of DS2 violations on the producer side and are caught at the gate by GATE-29.

**Gate-failure learning.** *"Dev-env gates are necessary but not sufficient. Every gate that runs in the developer's working tree must have a clean-checkout counterpart, or the deploy boundary is untested."* The Wave-4A bug is structurally identical to the Wave-3 Dot-Com loader bug: an intermediate artifact passed structural validation but the end-to-end user-visible path was broken. Wave-3 closed the loader gap (GATE-27); Wave-4A closes the deploy gap (GATE-29). The general principle: final verification belongs on the rendered user-visible surface in the deployment-equivalent environment, not on any intermediate artifact in the dev environment.

**Scope and approval.**

- **SOP scope:** this Wave-4A patch edits `docs/agent-sops/team-coordination.md` (GATE-29 row + Pair Acceptance Checklist extension + META-VNC scope extension), `docs/standards.md` (GATE-29 row + META-VNC row update), and this regression note. Evan in parallel edits `docs/agent-sops/econometrics-agent-sop.md` (ECON-DS2 addition), `docs/standards.md` ECON block (ECON-DS2 row), `.gitignore` (allowlist carve-outs), and the tracked parquet files themselves. No other SOPs are touched.
- **Pair scope:** no artifacts under `results/hy_ig_v2_spy/*` other than this regression note are modified by this gate patch. Remediation of the underlying bug (actually tracking the signals parquet) is Evan's ECON-DS2 retro-application in the parallel Wave-4A branch.
- **Approved by:** Lead Lesandro. Gate additions do not require producer sign-off; producer-side ECON-DS2 updates require Evan's self-approval per the standard SOP-change protocol. Central commit held until both Wave-4A agents finish.

---

### Lead's Wave 4C-1 Contract File Standard (2026-04-19)

**Why.** The Wave 4B cross-review produced five independent agent audits that converged on a single pattern: the same cross-agent artifact was being described by prose dictionaries in one SOP, a partial JSON fragment in another, and a freehand example in a third. Contracts forked silently every time an SOP was touched. Before authoring the four high-priority contract JSONs surfaced by 4B (winner_summary, chart_type_registry, narrative_frontmatter, data_subject), the system needs a meta-rule that prevents the same divergence from recurring at the JSON-schema layer. Otherwise we trade prose divergence for schema divergence.

**What.**

- **META-CF — Contract File Standard (meta-rule, blocking).** Added to `docs/agent-sops/team-coordination.md` (Contract File Standard section, immediately before Classification Field Ownership) and registered in `docs/standards.md` under the META block. Rule text mandates: single authoritative schema per cross-agent artifact at `docs/schemas/{contract_name}.schema.json` (JSON Schema draft 2020-12); header fields `x-owner` (single agent) and `x-version` (semver); companion example instance at `docs/schemas/examples/{contract_name}.example.json` that must validate; producer validates before save, consumer validates before use, both via `scripts/validate_schema.py`; SOPs cross-link, never inline; schema changes require regression_note (per META-VNC) and sop-changelog entries; one authoritative schema per artifact, no forks.
- **`docs/schemas/` directory created** with a ≤80-line `README.md` explaining purpose, what does and does not live in the directory, naming convention, add/evolve workflow, and the validation tool. An `examples/` subdirectory is reserved for reference instances.
- **`scripts/validate_schema.py` created** (≤100 lines). Uses `jsonschema` with `Draft202012Validator`, CLI flags `--schema`, `--instance`, `--strict`, exit codes 0/1/2, human-readable error path/message output, and a library entrypoint `validate_json(instance, schema, strict=False)` returning a list of error strings (empty = valid). Header docstring cites META-CF.
- **`requirements.txt` updated** to add `jsonschema` under a new "Schema validation (per META-CF)" section. Package was already installed (4.26.0) but not declared; declaration closes the gap for clean-checkout deploys per GATE-29 / ECON-DS2.

**Smoke-test result.** Validator exercised end-to-end with a throwaway schema + valid + invalid instance pair under `/tmp/` — `EXIT=0` on the valid instance (`OK: … conforms to …`), `EXIT=1` on the invalid instance with two path-annotated error lines (`[<root>] 'sharpe' is a required property` and `[pair_id] 42 is not of type 'string'`). Throwaway files deleted. Validator ready for producer/consumer wiring in Wave 4C-2.

**Next (Wave 4C-2).** Four concrete contract schemas to be authored, each following META-CF:
- `winner_summary.schema.json` (owner: Evan) — supersedes the inline prose dictionary currently scattered across Evan's and Ace's SOPs.
- `chart_type_registry.schema.json` (owner: Vera) — supersedes the VIZ-A3 standard-chart-catalog prose table as the machine-readable source of truth.
- `narrative_frontmatter.schema.json` (owner: Ray) — formalizes the Story/Evidence/Strategy/Methodology frontmatter currently described in RES-EP1.
- `data_subject.schema.json` (owner: Dana) — formalizes the data-dictionary row shape currently described in DATA-DD1.

Each schema ships with a validating example instance and a SOP cross-link update in the owner's SOP plus every consumer's SOP.

**Learning.** *"Standards-on-standards prevent divergence at the schema layer, not just the prose layer."* The Wave 4B audits converged because prose SOPs leak: every edit to a prose dictionary risks drifting one agent's copy relative to another's. Promoting the contract to a versioned JSON schema moves the source of truth out of SOP prose into a single validated artifact, with a machine-checkable pre-commit hook on both producer and consumer sides. The meta-rule itself is the scaffold; without META-CF, the four contract JSONs planned for 4C-2 would have reintroduced exactly the same fork hazard one layer deeper.

**Scope and approval.**

- **SOP scope:** edits limited to `docs/schemas/README.md` (new), `scripts/validate_schema.py` (new), `docs/agent-sops/team-coordination.md` (META-CF section), `docs/standards.md` (META-CF row), `requirements.txt` (jsonschema declaration), and this regression note. No concrete contract schemas authored — that is Wave 4C-2.
- **Pair scope:** no artifacts under `results/hy_ig_v2_spy/*` other than this regression note are modified.
- **Approved by:** Lead Lesandro. Central commit held until Wave 4C-1 is reviewed alongside any producer agents' companion work.

---

### Evan's Wave 4C-2 winner_summary schema (2026-04-19)

**Trigger.** Wave 4C-1 (Lead) landed META-CF and the `scripts/validate_schema.py` validator. The 4B cross-review (Evan + Ace) converged on `winner_summary.json` being the single highest-leverage schema fork: Evan's SOP enumerated the fields in prose only; Ace's APP-SE1 pre-render validation and `instructional_trigger_cards.py` both relied on `signal_column` and `target_symbol` fields that Evan's SOP never required, with a literal-name fallback map (`_SIGNAL_CODE_TO_COLUMN` at `app/components/probability_engine_panel.py` commit `519d042`) wallpapering the gap. This dispatch authors the first META-CF-compliant schema, resolving ECON-H5 (producer mandate) and APP-WS1 (consumer pre-render contract) in one artifact.

**Schema path + version.**

- Schema: `docs/schemas/winner_summary.schema.json` — JSON Schema draft 2020-12, `x-owner: "evan"`, `x-version: "1.0.0"`.
- Field count: **15 required**, **5 recommended/optional** (20 total). Required: `pair_id`, `generated_at`, `signal_column`, `signal_code`, `target_symbol`, `threshold_value`, `threshold_rule` (enum: gt/lt/gte/lte/crosses_up/crosses_down), `strategy_family` (enum: P1_long_cash/P2_signal_strength/P3_long_short), `direction` (enum: procyclical/countercyclical/mixed), `oos_sharpe`, `oos_ann_return` (ratio; 0.113 = 11.3%), `oos_max_drawdown` (≤ 0, ratio), `oos_n_trades`, `oos_period_start`, `oos_period_end` (ISO dates). Optional: `bh_sharpe`, `bh_ann_return`, `annual_turnover`, `cost_assumption_bps`, `notes`.
- Example instance: `docs/schemas/examples/winner_summary.example.json` — populated with HY-IG v2 real values (Sharpe 1.274, ann. return 0.1133, max DD −0.102, OOS 2017-01-01 → 2025-12-31, B&H Sharpe 0.7726).

**Answer to Ace's pointed question (APP-WS1).**

Ace asked: *"does `winner_summary.json.signal_column` need to be the exact parquet column name, the tournament `signal_code`, or a display name?"*

**Committed answer: the EXACT parquet column name.** The schema mandates `signal_column` as the verbatim column in `results/{pair_id}/signals_{date}.parquet` that Ace's consumer code (`pd.read_parquet(...)[signal_column]` in `probability_engine_panel.py` and `position_adjustment_panel.py`) reads at render time. For HY-IG v2 this is `hmm_2state_prob_stress`. The tournament identifier (`S6_hmm_stress` for HY-IG v2) lives in the sibling field `signal_code`; the two fields are both required so a consumer that wants either never has to guess or maintain a mapping table. This commitment replaces the `_SIGNAL_CODE_TO_COLUMN` fallback map and makes the Wave 1.5 bug class structurally impossible on pairs that conform to v1.0.0.

**Smoke-test results.**

1. `python3 scripts/validate_schema.py --schema docs/schemas/winner_summary.schema.json --instance docs/schemas/examples/winner_summary.example.json` → **PASS** (`OK: … conforms to …`, exit 0).
2. `python3 scripts/validate_schema.py --schema docs/schemas/winner_summary.schema.json --instance results/hy_ig_v2_spy/winner_summary.json` → **INVALID** (exit 1). Gaps (pre-migration, as expected):
   - 9 required fields missing: `generated_at`, `signal_column`, `target_symbol`, `threshold_rule`, `strategy_family`, `oos_max_drawdown`, `oos_n_trades`, `oos_period_start`, `oos_period_end`.
   - 1 enum mismatch: `direction: "counter_cyclical"` (legacy two-word spelling) is not one of `["procyclical", "countercyclical", "mixed"]`.
   - Unit mismatches (silent, detected on inspection, not by the schema's `type: number`): `oos_ann_return = 11.33` and `max_drawdown = -10.2` are percent-units; the schema expects ratio units (0.1133, -0.102). Migration (Wave 4D) must normalize these.

   Per instruction, `results/hy_ig_v2_spy/winner_summary.json` is NOT patched in this dispatch — Wave 4D owns the migration of existing artifacts across all pairs (INDPRO, SOFR-TED variants, Permit, VIX-VIX3M, HY-IG v1, HY-IG v2).

**Rule IDs registered.**

- **ECON-H5** — "Winner Summary JSON Contract (per META-CF)" — added to `docs/agent-sops/econometrics-agent-sop.md` immediately after the KPI File section, and registered in `docs/standards.md` ECON block. SOP entry links to the canonical schema path (per META-CF: no inline schemas in SOPs) and mandates the producer-side `scripts/validate_schema.py` pre-save validation.
- **Cross-ref APP-WS1** — Ace's consumer-side companion rule. This schema is the shared artifact; APP-WS1 (Ace will ratify in parallel) will cite `docs/schemas/winner_summary.schema.json` as the authoritative contract and retire the `_SIGNAL_CODE_TO_COLUMN` fallback map once every pair's `winner_summary.json` conforms to v1.0.0.

**Files touched.**

- `docs/schemas/winner_summary.schema.json` (new).
- `docs/schemas/examples/winner_summary.example.json` (new).
- `docs/agent-sops/econometrics-agent-sop.md` (ECON-H5 section appended after "KPI File (mandatory)").
- `docs/standards.md` (ECON-H5 row appended in ECON block).
- This regression note (appended).

**Files NOT touched.**

- `results/hy_ig_v2_spy/winner_summary.json` (and every other pair's `winner_summary.json`) — migration deferred to Wave 4D.
- No other agents' SOPs.
- No other schemas (chart_type_registry, narrative_frontmatter, data_subject are owned by Vera/Ray/Dana respectively and ship in parallel dispatches).
- No portal code (Ace retires APP-WS1's fallback map on a separate dispatch after migration completes).

**Approved by.** Evan self-approves the schema authorship; Lead Lesandro reviews at Wave 4C-2 consolidation alongside the three companion schemas from Dana, Vera, and Ray.

---

### Vera's Wave 4C-2 chart_type_registry (2026-04-19)

**Why.** Wave 4B cross-review (my own `docs/cross-review-20260419-vera.md`, Evan's `docs/cross-review-20260419-evan.md`, Ace's `docs/cross-review-20260419-ace.md`) converged on one finding: the method → chart-type mapping lived as three partial prose copies — in Evan's ECON-H4 handoff table (`results/{pair_id}/handoff_to_vera_{date}.md`), in Vera's Rule A3 inline table in `docs/agent-sops/visualization-agent-sop.md`, and in Ace's `render_method_block` helper in `app/components/charts.py`. The copies drifted silently and were the direct root cause of the Wave 1.5 Granger → Local Projections silent fallback (S18-11) and the broader S18-8 class of silent drops.

**What.**

- **`docs/schemas/chart_type_registry.schema.json` created** (JSON Schema draft 2020-12, `x-owner: vera`, `x-version: 1.0.0`). Shape: `{x-version, x-owner, x-generated, notes, methods}` where `methods` is a map `method_name → {expected_chart_type, canonical_filename_pattern, required_result_file, viz_rule_id, econ_rule_id, override_supported?, consumer_page?, notes?}`. `expected_chart_type` is an enum covering the 13 chart forms the team ships (bar, line, heatmap, dual_panel, sparkline, bar_by_lag, scatter, area_probability, line_with_ci, quantile_coef, equity_line, drawdown_area, regime_bars). `override_supported=true` is the META-ZI flag for entries that carry an `{episode_slug}` placeholder.
- **`docs/schemas/chart_type_registry.json` created** — the canonical registry instance seeded from the HY-IG v2 reference pair (per META-RPD). **Method count: 17** — correlation, granger, ccf, local_projections, regime, quantile, transfer_entropy, quartile_returns, five history_zoom episode entries (dotcom, gfc, covid, taper_2018, inflation_2022), hero, equity_curves, equity_drawdown, tournament_scatter.
- **`docs/schemas/examples/chart_type_registry.example.json` created** — minimal 2-method reference instance (correlation + granger) per META-CF example-instance separation.
- **VIZ-V8 registered** as a new Vera-owned rule in `docs/agent-sops/visualization-agent-sop.md` (Rule V8, immediately after V5) and in `docs/standards.md` VIZ block. The rule text mandates: Vera validates chart basenames against `canonical_filename_pattern` before save; Evan's ECON-H4 is the INPUT that must align with the registry per-row; Ace's `render_method_block` resolves `method_name` via the registry and falls back only to a GATE-25 placeholder (never a lookalike).
- **VIZ-A3 inline chart-catalog table removed** in favor of a link to the registry. Axis / ordering / palette *preferences* remain in VIZ-A3 text; the structural binding of method → canonical filename lives in the registry. New methods require updating the registry, bumping `x-version`, and a `sop-changelog.md` entry per META-VNC.

**Smoke-test result.** Validator run against both instances:
- `python3 scripts/validate_schema.py --schema docs/schemas/chart_type_registry.schema.json --instance docs/schemas/chart_type_registry.json` → `OK` (EXIT=0).
- `python3 scripts/validate_schema.py --schema docs/schemas/chart_type_registry.schema.json --instance docs/schemas/examples/chart_type_registry.example.json` → `OK` (EXIT=0).

Initial authoring surfaced one schema bug: the `canonical_filename_pattern` regex was too strict to allow the `{episode_slug}` META-ZI placeholder — loosened to `^[a-z0-9_{}]+\.json$` on the first smoke-test cycle, and both instances then passed. The loosened pattern still rejects pair-id-prefixed filenames (VIZ-NM1 compliance) and still requires the `.json` extension.

**Resolution of Vera's Q to Evan (Q3 in `docs/cross-review-20260419-vera.md`).** Vera asked: "Will you accept a machine-readable `viz_handoff_manifest.json` mirroring ECON-H4?" Resolution: **No separate manifest.** The `chart_type_registry.json` Vera owns IS the mutual contract. Evan's per-pair ECON-H4 handoff table points into this registry by `method_name` — one authoritative registry, no per-pair manifest, no second source-of-truth to drift against. Simpler than a manifest-per-pair; consistent with META-CF "one authoritative schema per artifact, no forks." This decision is captured in VIZ-V8 rule text ("Evan does NOT produce a separate `viz_handoff_manifest.json` — the registry is the mutual contract") and mirrored in VIZ-V8's standards.md row.

**Gap closed.** The three-agent silent-fallback failure mode that produced the Wave 1.5 Granger → Local Projections substitution (S18-11) and the HY-IG v2 silent drops of pre-whitened CCF / transfer entropy / quartile returns (S18-8) is now structurally prevented: Vera's production validates against the registry; Evan's ECON-H4 rows reconcile against the registry; Ace's loader resolves via the registry and surfaces GATE-25 placeholders instead of rendering lookalikes. Cross-reference: ECON-H4 (INPUT), VIZ-V8 (OUTPUT), APP-CN1 (legacy-chart-name-fallback sweep, consumer-side enforcement).

**Scope and approval.**
- **SOP scope:** edits limited to `docs/agent-sops/visualization-agent-sop.md` (Rule A3 table replaced with registry link + new Rule V8), `docs/standards.md` (VIZ-V8 row), `docs/schemas/chart_type_registry.schema.json` (new), `docs/schemas/chart_type_registry.json` (new), `docs/schemas/examples/chart_type_registry.example.json` (new), and this regression-note append. No other SOPs are touched (no rename of existing chart files yet — migration is a separate dispatch).
- **Pair scope:** no existing artifacts under `results/hy_ig_v2_spy/*` are modified other than this regression note. No chart files under `output/charts/hy_ig_v2_spy/plotly/*` are renamed; the registry commits the canonical names for future production and for Ace's legacy-sweep per APP-CN1.
- **Approved by:** Vera self-approves the schema authorship; Lead Lesandro reviews at Wave 4C-2 consolidation alongside the winner_summary, narrative_frontmatter, and data_subject schemas from Evan, Ray, and Dana.


---

### Ray's Wave 4C-2 narrative_frontmatter (2026-04-19)

**Why.** The Wave 4B cross-review surfaced a fragile consumer contract at the Ray → Ace boundary: Ace extracted narrative subsections (`How the Signal is Generated`, `How to Use This Indicator Manually`, `How to Read the Trade Log`) from the portal narrative markdown by heading-text match. Renaming a heading silently broke extraction. My own review (`docs/cross-review-20260419-ray.md`, Proposed RES-16) and Ace's review (`docs/cross-review-20260419-ace.md`, Proposed APP-NR1 + APP-DIR1) converged on the same gap: no machine-readable inventory of sections, expanders, chart references, glossary terms, or direction assertion. Ace asked explicitly for a frontmatter block at the top of every `docs/portal_narrative_*.md`; a frontmatter contract is a less invasive alternative to splitting standalone subsection files (RES-16's original proposal), with the same anchor-stability effect. Lead decides later whether to ALSO require standalone files in a future wave — frontmatter is sufficient now.

**What.**

- **`docs/schemas/narrative_frontmatter.schema.json` created** (JSON Schema draft 2020-12, `x-owner: ray`, `x-version: 1.0.0`). Describes the YAML-or-JSON frontmatter block between standard markdown `---` delimiters at the top of every portal narrative. Required fields: `pair_id`, `narrative_version` (semver for Ray's revisions, independent of schema version), `generated_at`, `pages` (Story / Evidence / Strategy / Methodology each with `headline`, optional `plain_english`, `sections[{id,title,anchor}]`, `expanders[{id,title,content_ref?}]`), `chart_refs` (canonical names that MUST exist in `chart_type_registry.json`), `glossary_terms` (MUST exist in `docs/portal_glossary.json`), `direction_asserted` (enum `procyclical|countercyclical|mixed`, aligned exactly with `winner_summary.schema.json.direction` and consumed by APP-DIR1). Optional fields: `historical_episodes_referenced` (for META-ZI coherence inspection), `status_labels_used` (subset of RES-VS vocabulary), `glossary_requests` (Ace-to-Ray request-back ledger).
- **`docs/schemas/examples/narrative_frontmatter.example.json` created** — frontmatter-only reference instance seeded from HY-IG v2 real values: `narrative_version: 2.0.0`, RES-11 headline "Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns", four pages with complete section/expander inventories (Story: 8 sections + 4 expanders; Evidence: 8 method sections; Strategy: 8 sections + 2 expanders; Methodology: 8 sections), 13 `chart_refs` (hero, the six Evidence method charts, quartile returns, tournament, equity curve, three history_zoom episodes), three glossary terms (Basis point, Credit spread, HMM stress probability), `direction_asserted: countercyclical`, and a worked GFC override example in `historical_episodes_referenced`.
- **`scripts/validate_schema.py` run** against the example instance. **Smoke-test result:** `OK: docs/schemas/examples/narrative_frontmatter.example.json conforms to docs/schemas/narrative_frontmatter.schema.json` (EXIT=0) on the first attempt.
- **RES-17 registered** as a new Ray-owned blocking rule in `docs/agent-sops/research-agent-sop.md` (new §"Rule RES-17 — Narrative Frontmatter Contract", placed between RES-VS and Bibliography Scale) and in `docs/standards.md` RES block (row inserted after RES-VS). Rule text: every portal narrative opens with a frontmatter block conforming to the schema; producer validation blocks handoff; anchor fields are stable across title renames; glossary request-back SLA (below).
- **App Dev Handoff section updated** in `docs/agent-sops/research-agent-sop.md` with the mandatory-frontmatter paragraph + producer-validation command snippet, linking to the schema and example.

**Glossary SLA policy (answers my Q to Ace).** My cross-review §6 asked Ace: "how many task-cycles can you wait before the portal ships with a fallback?" Answered within the schema's `glossary_requests` optional array and in RES-17 rule text. Policy:

> When Ace files a missing-term request against a narrative, Ray commits to ONE of two outcomes: (1) close the term in the NEXT narrative revision within ONE WEEK of Ace's request — status `closed` with a resolution pointer to the glossary entry — OR (2) ship the current narrative with a `[term pending definition]` placeholder in the prose AND a matching `glossary_requests` entry with `status='pending_placeholder'` — the term is then queued for the next revision. Silence is not acceptance; an unaddressed Ace request past the one-week SLA is a RES-17 / RES-6 violation and a gate flag at the next acceptance.

The ledger is kept inside the frontmatter rather than in a sidecar file so it travels with the narrative and cannot silently drift from the prose state.

**APP-DIR1 cross-agent direction-assertion.** Confirmed the schema includes a required `direction_asserted` field (enum `procyclical|countercyclical|mixed`). Values align EXACTLY with `winner_summary.schema.json.direction` — no hyphenated variants (`counter-cyclical`, `pro-cyclical`) permitted, closing a historical source of drift. Ace's APP-DIR1 renders a landing-card warning chip on two-way mismatch (any of Ray / Evan / Vera) and blocks reference-pair acceptance on three-way mismatch.

**Gap closed.** The heading-match fragility (RES-16 / B8) and the three-way direction-annotation silent-drift risk (APP-DIR1 / META-IA) are both structurally closed. Ace now extracts by stable `anchor` rather than by prose title; renames are non-breaking. Ray's empirical direction assertion is machine-readable and reconciled against Evan's `winner_summary.json` and Vera's chart line-style sidecar. RES-17 is the single authoritative contract; no inline schema copies in SOPs (META-CF compliance).

**Scope and approval.**
- **SOP scope:** edits limited to `docs/agent-sops/research-agent-sop.md` (App Dev Handoff frontmatter paragraph + new Rule RES-17 section), `docs/standards.md` (RES-17 row in the RES block), `docs/schemas/narrative_frontmatter.schema.json` (new), `docs/schemas/examples/narrative_frontmatter.example.json` (new), and this regression-note append. No other SOPs are touched. No existing narratives are modified yet; migration of `docs/portal_narrative_hy_ig_v2_spy_20260410.md` to carry the frontmatter block is a separate Wave 4D dispatch.
- **Pair scope:** no existing artifacts under `results/hy_ig_v2_spy/*` are modified other than this regression note.
- **Approved by:** Ray self-approves the schema authorship; Lead Lesandro reviews at Wave 4C-2 consolidation alongside the winner_summary, chart_type_registry, and data_subject schemas from Evan, Vera, and Dana.


### Dana's Wave 4C-2 schemas (2026-04-19)

**Scope:** Authorship of two META-CF-governed schemas owned by Data Dana, plus their reference instances, plus producer-side validator integration. No touch to any pair artifact; no edit to existing `interpretation_metadata.json` instances (migration is a separate dispatch).

**Artifacts produced:**

- **`docs/schemas/data_subject.schema.json`** (new, `x-owner: dana`, `x-version: 1.0.0`) — column-level metadata sidecar contract governing `data/{subject}_{frequency}_schema.json`. Required per-column fields: `dtype`, `unit` (controlled enum from DATA-D2), `display_name`, `direction` (`higher_is_better` / `lower_is_better` / `neutral`), `description`. Optional: `source_reference`, `refresh_ttl_days`. Closes the Wave-2A 100x unit bug class at the artifact layer by turning `unit` into a machine-verifiable contract field consumers MUST read instead of inferring from column names.
- **`docs/schemas/interpretation_metadata.schema.json`** (new, `x-owner: dana`, `x-version: 1.0.0`) — versioned pair-classification contract governing `results/{pair_id}/interpretation_metadata.json`. Required: `pair_id`, `schema_version`, `indicator_nature`, `indicator_type`, `strategy_objective`, `owner_writes` (explicit field-ownership map with `dana`, `evan`, `ray` arrays), `last_updated_by`, `last_updated_at`. Closes the ECON-CFO-1 multi-writer race by codifying a deterministic `dana → evan → ray` merge order; closes the ad-hoc field-addition pattern by requiring schema bumps rather than silent JSON-shape expansion.
- **`docs/schemas/examples/data_subject.example.json`** (new) — 5-column reference instance modeled on real columns from `data/hy_ig_v2_spy_daily_20260410.parquet`: `date`, `hy_ig_spread` (bps, lower_is_better), `hy_ig_mom_63d` (bps, lower_is_better), `spy` (price, neutral), `spy_fwd_63d` (decimal_return, higher_is_better).
- **`docs/schemas/examples/interpretation_metadata.example.json`** (new) — HY-IG v2 reference instance with real classification values (`leading` / `credit` / `countercyclical_protection`), full `owner_writes` map, and `schema_version: "1.0.0"`.

**Smoke-test results** (all three calls run from repo root):

```
python3 scripts/validate_schema.py --schema docs/schemas/data_subject.schema.json            --instance docs/schemas/examples/data_subject.example.json
   → OK (EXIT=0)
python3 scripts/validate_schema.py --schema docs/schemas/interpretation_metadata.schema.json --instance docs/schemas/examples/interpretation_metadata.example.json
   → OK (EXIT=0)
python3 scripts/validate_schema.py --schema docs/schemas/interpretation_metadata.schema.json --instance results/hy_ig_v2_spy/interpretation_metadata.json
   → INVALID (EXIT=1) — gaps on the real HY-IG v2 instance, as expected:
       - missing required property: `pair_id`
       - missing required property: `schema_version`
       - missing required property: `owner_writes`
       - missing required property: `last_updated_by`
       - missing required property: `last_updated_at`
       - [expected_direction] `counter_cyclical` is not in the controlled enum (valid: `procyclical` / `countercyclical` / `mixed`)
       - [observed_direction] same as above
```

Gap list is recorded; the real HY-IG v2 instance is NOT edited in this wave. Migration of existing `interpretation_metadata.json` instances to the new schema (add the five required fields, collapse `counter_cyclical` → `countercyclical`) is a separate Wave 4D dispatch.

**SOP + standards registration:**

- **DATA-D5** registered in `docs/agent-sops/data-agent-sop.md` (§6 Rule DATA-D5) and `docs/standards.md` DATA block.
- **DATA-D6** registered in `docs/agent-sops/data-agent-sop.md` (§6 Rule DATA-D6) and `docs/standards.md` DATA block.
- New §6 Deliver sub-section "Canonical schemas (single source of truth — META-CF)" links both schemas and writes the producer-side validator call verbatim.
- Quality-gate checklist gains two blocking lines (one per rule).

**Resolution of Dana's keystone question to Ace** (cross-review-20260419-dana.md §6): *"Will you commit to consuming a `data/{subject}_schema.json` sidecar as the single source of truth for column unit, display name, direction, and refresh TTL?"* Dana commits UNILATERALLY in the schema definition — the schema IS the contract. Dana's SOP treats the sidecar as authoritative; Ace's consumer adoption (calling `resolve_ttl()` against the sidecar in place of hardcoded `@st.cache_data(ttl=...)` values) is a Wave 4D / 4E task tracked under APP-TC1. If Ace cannot adopt, Ace files an APP-side exception explaining why; the default position is full consumption.

**Gaps closed:**

- Wave-2A 100x hero chart unit bug class (bps-vs-decimal silent axis mislabel) — closed at the artifact layer by DATA-D5 `unit` enum; no longer reliant on VIZ-A2 catch at Vera's end.
- ECON-CFO-1 multi-writer race latent bug (Dana / Evan / Ray writing to the same classification JSON with no ordering protocol) — closed by DATA-D6 `owner_writes` field-ownership map + enforced `dana → evan → ray` merge order.
- Ad-hoc field-addition pattern on `interpretation_metadata.json` (three waves of ad-hoc expansion — `indicator_nature`, `indicator_type`, `strategy_objective` — each without a versioned contract) — closed by DATA-D6 requirement that any new field needs a schema `x-version` bump, loader update, and Lead sign-off in the same commit.

**Cross-reference for consumer adoption (future Wave 4D / 4E scope, not this wave):**

- Ace's consumer-side adoption of `resolve_ttl()` against `refresh_ttl_days` — APP-TC1 track.
- Vera's axis-builder refactor to read `unit` and `display_name` from the sidecar — VIZ-A2 track.
- Ray's dual-notation narrative generator refactor to read `unit` — RES-4 track.
- Migration of existing per-pair `interpretation_metadata.json` instances to DATA-D6 shape — Wave 4D data-agent sub-dispatch.

**Scope and approval.**
- **Schema scope:** `docs/schemas/data_subject.schema.json`, `docs/schemas/interpretation_metadata.schema.json`, `docs/schemas/examples/data_subject.example.json`, `docs/schemas/examples/interpretation_metadata.example.json`. No other schemas touched.
- **SOP scope:** edits limited to `docs/agent-sops/data-agent-sop.md` (§6 Deliver canonical-schemas link, two new Quality-Gate lines, two new Rule DATA-D5 / DATA-D6 sections) and `docs/standards.md` (two new DATA rows). No other agent SOPs touched.
- **Pair scope:** no existing pair artifacts modified; this regression-note append is the only change under `results/hy_ig_v2_spy/`.
- **Approved by:** Dana self-approves the schema authorship and the unilateral consumer-contract commitment to Ace; Lead Lesandro ratifies at Wave 4C-2 consolidation alongside the winner_summary, narrative_frontmatter, and chart_type_registry schemas from Evan, Ray, and Vera.
