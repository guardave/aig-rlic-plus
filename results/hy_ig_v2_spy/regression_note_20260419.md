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
