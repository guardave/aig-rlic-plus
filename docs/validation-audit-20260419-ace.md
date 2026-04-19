# Validation Audit — AppDev Ace (2026-04-19)

**Auditor:** AppDev Ace
**Scope:** HY-IG v2 × SPY reference-pair portal (`app/pages/9_hy_ig_v2_spy_*.py`) plus shared components (`app/components/*`). Read-only audit; no source edits.
**Inputs reviewed:** appdev-agent-sop.md; standards.md APP section; 20260418-batch.md (S18-1..S18-12, SL-1..SL-5); all 4 HY-IG v2 page files; 6 components (probability_engine_panel, position_adjustment_panel, instructional_trigger_cards, live_execution_placeholder, direction_check, schema_check) + charts.py; smoke logs (loader + schema_consumers); cross-review-20260419-ace.md.

---

## Axis 1 — Reproducibility

**Question:** given the same upstream artifacts + SOP, would a second Ace produce byte-identical page code? For each element, map the rule (if any), mark deterministic or discretionary, and propose the closing fix.

| Page element | SOP rule | Deterministic? | Discretion point | Captured? | Proposed fix |
|---|---|---|---|---|---|
| **Story headline block** (H2 + "Key metrics" bullets at top) | RES-11 | Partial | RES-11 mandates `## [Metric summary] — [One-liner]` + KPI bullets, but exact KPI count (2-3), bullet format (dash vs numbered), and metric verbatim wording are Ray's discretion — Ace just renders. | Partial — structure codified, content wording is Ray's | Codify the Story headline schema in APP-SF1 (H2 prefix, KPI count, "Where This Fits" container position). |
| **"Where This Fits" container-border block** | none | No | Ace chose `st.container(border=True)` on Story p1; could have been plain markdown. No rule says orientation-block goes inside a bordered container. | No | **APP-OR1** — Orientation Block rule: every reference-pair Story page opens with a bordered container titled "Where This Fits" immediately after the headline. |
| **Page title casing** ("The Strategy: Translating Signals to Action" vs "Strategy") | none | No | I chose sentence-case with subtitle. Second Ace could write "Strategy (HY-IG → SPY)". | No | Codify page-title template per page type in APP-PA1. |
| **Plain English expander title** ("🧒 Plain English version") | RES-2, APP-AF4 | No | Emoji (🧒), literal title wording, collapsed-by-default are all my calls. Canonical title could be "In Plain English" (matching RES-2 bridge phrasing) or "ELI5". | No | **APP-EX1** — Expander canonical-titles registry (`app/components/expander_titles.py`): one string per concept, imported everywhere. |
| **Internal ordering: bullets then zoom charts** (Story "What History Shows") | RES-8 + SL-4/5 | Partial | RES-8 requires episode prose + matching chart; ordering (prose-then-chart vs chart-then-prose) not mandated. | No | Codify prose-before-chart convention in APP-SF1 or defer to RES-8 to pin the order. |
| **KPI column count** (5 columns on Story, 5 cards on Strategy, 3 columns on Methodology Sample Period) | none | No | `st.columns(5)` is my pick — 4, 5, or 6 all plausible. | No | APP-AF3 extension: cap KPI row at max 5 columns; specify default by page type. |
| **Column width ratios** (`st.columns(2)` vs `st.columns([2,1,1])`) | none | No | Strategy "Signal/Threshold/Family + Lead/Direction/Description" uses `st.columns(2)`; could be `[3,2]`. | No | Low priority — document in APP-RP1 only if stakeholders complain. |
| **`st.container(border=True)` placement** | APP-RP1 (lists native-component preference) | Partial | APP-RP1 says use bordered containers for cards; it does NOT say which blocks must be bordered. I chose: Trading Rule, Where This Fits, COVID example, Concrete Example on Story. Second Ace could border differently. | Partial | Add a bordered-block registry to APP-RP1 ("rule-first strategy box, concrete worked examples, orientation callouts"). |
| **Severity mapping** (L1/L2/L3) for each validation branch | APP-SEV1 | Partial | APP-SEV1 defines the 3 levels. File-level choices (`winner_summary` → L1, `interpretation_metadata` → L2, missing caption → L3) are Ace's per-component judgement. | Partial | Extend APP-SEV1 with a severity-map JSON at `app/_smoke_tests/severity_map.json` (mentioned in cross-review §5, not yet built) — deterministic lookup per `(artifact, field)` pair. |
| **Expander `expanded=` default** | APP-AF1 (defer, don't expand) | Partial | APP-AF1 says collapsed by default; I used `expanded=True` on the Methodology status-legend and `expanded=False` on the column-legend. | No | Add explicit default-state rule: `expanded=False` except for first-visit orientation (per-visit session flag). |
| **Takeaway caption wording** | APP-SE5 | No | APP-SE5 mandates 1-line takeaway; exact wording ("Takeaway: ...", "What this means: ...", "The strategy...") is Ace discretion. Three different prefixes appear on the Strategy Confidence tab alone. | No | **APP-CC1** — Caption-prefix canonical: "Takeaway:" for APP-SE5 items; "What this means:" reserved for RES translation bridges. |
| **Trigger-card count** (`_card_specs_for_strategy`: 3 for P1/P2, 2 for P3) | APP-SE3 | Partial | SOP says 2–4 cards. Ace codified the mapping in code: P1=3, P2=3, P3=2. But it is buried in a component function, not the rulebook. | Partial | Promote the strategy→card-count mapping from `instructional_trigger_cards.py` into APP-SE3 as a required table. |
| **Trigger-card action text wording** ("When probability crosses X → do Y") | APP-SE3 | Partial | APP-SE3 mandates the pattern; exact verbs ("scale exposure down" vs "cut equity exposure" vs "reduce SPY") discretionary. | No | Canonical verb table per strategy family in APP-SE3 or APP-EX1. |
| **Chart-name → file path mapping** | VIZ-V8 (chart_type_registry.json) + APP-EP4 | Partial | VIZ-V8 codifies method charts; `hero`, `equity_curves`, `drawdown_comparison`, `history_zoom_*` use different conventions (pair_id subdir, `_comparison/`, inferred basenames). Smoke log confirms `hero.json` lives in `{pair_id}/plotly/` while `history_zoom_*` lives in `_comparison/` or `{pair_id}/`. | Partial | Extend VIZ-V8 registry to cover non-method charts (hero, equity_curves, drawdown_comparison); Ace's loader already forks on `history_zoom_` prefix — canonicalize in the registry instead. |
| **Fallback text wording** on `load_plotly_chart` miss | GATE-25 (no silent fallback) | No | Each `fallback_text=` call site invents its own string ("Hero chart: …", "Dot-Com zoom chart pending …", "Will appear when visualization is complete."). | No | Chart-key → fallback-string registry; load via `fallback_for(chart_name)` helper. |
| **Page URL slug** (`9_hy_ig_v2_spy_story.py` → Streamlit drops `9_` and converts `_` → space) | none | No | Streamlit's own slugify rule. If it changes, all `st.page_link` calls break silently. | No | **APP-URL1** — pin slug transformation in a helper `slugify_page(path)` tested once per Streamlit upgrade. |
| **Trade-log preview row count** ("first 10 rows of the broker-style log") | none | No | `_broker_df.head(10)` hardcoded in `9_hy_ig_v2_spy_strategy.py` line 581. No rule says 10. | No | APP-AF5 extension: canonical preview = 10 rows; constant `BROKER_PREVIEW_ROWS` in `components/trade_history.py`. |
| **Tab label strings** ("Execute" / "Performance" / "Confidence"; "Level 1 -- Basic Analysis" / "Level 2 -- Advanced Analysis") | none | No | Labels are my writing; second Ace may use "Signal" / "Backtest" / "Validation". | No | Tab-label registry in APP-PA1. |
| **Status-vocabulary legend location** | §3.12 + RES-10 | Partial | Rule says "pull from `docs/portal_glossary.json`". Location on page is discretion — I put the legend in an expander at the bottom of Story and inside the Confidence tab on Strategy; Methodology has it at the top. | Partial | §3.12 should pin one canonical placement per page type. |
| **Direction-check caption on agreement** | APP-DIR1 | Yes | `render_direction_check` renders a single caption string from code; deterministic. | Yes | — |
| **Schema-check error formatting** | APP-SEV1 L1 + APP-WS1 | Yes | `validate_or_die` renders a templated `st.error` with full error list. Fully deterministic. | Yes | — |
| **Live-Execution placeholder copy** ("This dashboard presents historical backtest results…") | APP-SE4 | Yes | Exact string is in `live_execution_placeholder.py` — identical across pairs. | Yes | — |
| **Hero chart caption text** | VIZ-A5 (Ray owns display caption) | No | Ray's narrative is the source, but I transcribed to the `caption=` kwarg by hand. If Ray rewrites, I have to re-transcribe. | No | Adopt RES-17 frontmatter + auto-load caption by chart_name from narrative frontmatter. |
| **Tournament top-N selection** (top 20) | none | No | `.nlargest(20, "oos_sharpe")` — could be top 10 or top 25. | No | Constant `TOURNAMENT_LEADERBOARD_ROWS=20` in APP-SP1. |
| **Color palette in components** (`#D55E00`, `#0072B2`, `#009E73`) | VIZ-CP1 | Yes | Components match VIZ-CP1 palette exactly. | Yes | — |
| **Metric `delta_color="inverse"` usage** (Max Drawdown card) | none | No | I chose `inverse` for max-DD on Strategy but not on Story. | No | Metric-delta-color canonical table per metric-type. |

**Reproducibility summary:** ~25 elements audited. **3 fully deterministic** (direction-check caption, schema-check error, live-execution copy), **9 partially codified** (rule exists but wording/layout discretion), **13 fully discretionary** (no rule → second Ace would diverge). The discretion surface is biggest in **caption wording, expander titles, container borders, and column-width ratios** — all surface-level but all visible to the stakeholder.

---

## Axis 2 — Stakeholder Resolution

| Stakeholder item | Claimed SOP rule | HY-IG v2 portal evidence | Spirit met? | Gap |
|---|---|---|---|---|
| **S18-1** (replace trigger viz with dual time-series + signal-gen explainer) | APP-SE1, APP-SE2, APP-SE3, RES-7 | Strategy page: `render_probability_engine_panel` + `render_position_adjustment_panel` + `render_instructional_trigger_cards` all present in Execute tab; Ray's "How the Signal is Generated" section rendered BEFORE KPIs (lines 105-135). Loader smoke PASS, schema-consumer smoke PASS. | **Yes** — the three components render on Cloud and the explainer precedes the KPI cards. A non-technical stakeholder reading in order sees: "HMM fits two states → probability between 0 and 1 → crosses 50% → reduces equity → restores when fades." Clear causal chain. | Minor: "How the Signal is Generated" is pure prose with no inline diagram. A stakeholder who skims prose and reads only charts might miss the explainer. Gap closed by APP-SE3 trigger cards which restate the rule visually. |
| **S18-3** (Confidence section: 1-line takeaway per table/chart) | APP-SE5 | Confidence tab has 4 items: stress_tests, signal_decay, walk_forward tables + tournament leaderboard + alt-strategy explorer. Spot-check 3 captions: (a) stress_tests "Takeaway: the strategy excels in credit-driven crises (GFC, COVID) but offers limited protection during pure rate-shock selloffs (2022)." → **genuinely informative** (names the regime it fails in). (b) signal_decay "Takeaway: Sharpe declines monotonically as execution delay rises; delays beyond ~5 days materially erode the edge." → **informative + actionable** (gives the "5 days" threshold). (c) walk_forward "Takeaway: Sharpe stays positive across the majority of walk-forward windows — the edge is not concentrated in any single year." → **informative but a touch generic** — doesn't quantify "majority". | **Mostly yes.** 2/3 spot-checks are strong; 1/3 could quantify. | Walk-forward caption should cite the actual fraction (e.g. "Sharpe > 0 in X of Y windows"). |
| **S18-9** (Instructional Trigger Cards, "board-game-like") | APP-SE3 | `instructional_trigger_cards.py` renders 3 bordered cards with stylised 30-point sparkline + title (BUY/HOLD/REDUCE) + action text. Sparklines illustrate up-cross, flat, and down-cross against the threshold dashed line. | **Partially.** The board-game intuition (one scenario per card, minimal visuals, clear action) is accomplished — stakeholder sees three cards side-by-side with one-line "When X → do Y" instructions. However, the sparklines are **synthetic (random + linspace)** rather than zoom-ins of actual historical crossings. A board-game card would usually show the concrete historical moment. | Add an optional "historical zoom" mode where the sparkline is a real 30-day slice around a canonical event (2008-06-02, 2020-02-24). Keep synthetic as fallback when no event can be matched. |
| **S18-10** (Live Execution placeholder) | APP-SE4 | `live_execution_placeholder.py` renders three `st.metric` cards ("—" when stub absent) + `st.info` callout: "This dashboard presents historical backtest results. A real-time execution layer would surface the fields above; the values shown are placeholders." | **Yes.** The callout text explicitly names it as a future feature ("a real-time execution layer would surface…"). A non-technical stakeholder reads "historical backtest" + "placeholders" and understands. | Minor: the section title is `## Future: Live Execution` — an explicit "(Not yet wired)" or "(Placeholder)" subtitle would be even clearer. |
| **SL-1** (Story layout: data summary as headline) | RES-11, §APP-PA1/SF1 | Story p1 line 66: `## Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns` followed by 3-bullet KPI block, then `---`, then Where-This-Fits container. The H2 is the first visible block after the Plain English expander. | **Yes** — headline prominence is high (H2 + bold metrics). It is NOT buried under a generic H1; the page has no H1 at all before the headline. | The Plain English expander renders before the headline (line 51). Some readers may expand it and scroll past the headline. Consider moving the expander below the headline or keeping it collapsed-by-default (currently collapsed — fine). |
| **§3.9 Evidence 8-Element template** (earlier Part D/E) | APP-EP1..EP5, RES-EP1..EP4 | `render_method_block` in `9_hy_ig_v2_spy_evidence.py` lines 98-167 implements ALL 8 elements with a render-time completeness linter (REQUIRED_ELEMENTS list lines 87-95). 8 method blocks render: Correlation, Granger, CCF, Local Projections, Regime, Quantile, Transfer Entropy, Quartile Returns. Smoke log confirms all 8 charts PASS. | **Yes** — strict compliance, better than any other pair. | Helper duplicates the field-name contract from RES-EP1; should import a shared dataclass to prevent drift (partial copy across RES/APP SOPs). |
| **§3.12 status vocabulary** (earlier Part E) | RES-10, DATA-VS, RES-VS | Story p1 lines 455-465, Methodology lines 71-89, Strategy Confidence tab lines 594-607 all load `docs/portal_glossary.json` and render the same legend expander. Smoke log indirectly confirms via schema-consumer PASS. | **Yes** — canonical glossary source, identical rendering across 3 pages. | Duplicated glue code at 3 sites. Extract to `components/glossary.py::render_status_legend()`. (Module exists but is not used for the status legend.) |
| **§3.6 / §3.8 Rule-First Strategy Cards** (earlier Part D APP-AF2) | APP-AF2 | Strategy page line 142-152: `st.container(border=True)` with `### The Trading Rule in Plain English` at position #1 (immediately after the `How the Signal is Generated` explainer and before KPIs). | **Yes** — rule-first is honoured. The explainer precedes it (by design per S18-1 RES-7), but the bordered Rule box is still the first element the reader parses as "the actual trading rule." | None. |
| **§3.11 Universal Takeaway Caption** (earlier Part E APP-SE5) | APP-SE5 | Every table in Confidence tab + every chart on Performance tab + status-legend expander all carry `st.caption()`. Tournament leaderboard and alt-strategy explorer both carry captions. | **Yes** — comprehensive. | See S18-3: one caption (walk_forward) is generic. |
| **SL-2** (Hero NBER caption + annualized return overlay) | VIZ-V2, RES-8 | Story p1 hero chart caption (line 198-204) includes "Vertical shaded bands mark NBER recessions." + describes the dual-panel structure. | **Yes** — caption text matches SL-2 ask. | Annualized-return overlay is delivered by Vera (chart-producer side), not verifiable from Ace code alone. Smoke log PASS confirms the chart renders. |
| **SL-3** (heatmap chart-text drift) | GATE-24 | Correlation-heatmap block (`9_hy_ig_v2_spy_evidence.py` CORRELATION_BLOCK lines 174-248) has a freshly written observation + interpretation pointing at the actual chart data (row/column/value specifics). | **Yes** — the "observation" text matches the chart. | Pre-publish diff check (GATE-24 mechanization) is manual today. |
| **SL-4, SL-5** (Dot-Com and GFC annotated zoom-ins) | VIZ-V1, RES-8, META-ZI | Story "What History Shows" renders `history_zoom_dotcom`, `history_zoom_gfc`, `history_zoom_covid`, each with prose + chart + event-marker caption. Smoke log: all 3 PASS with titles ("Credit Spreads During the Dot-Com Bust, 1998–2003" etc.). | **Yes**. | None. |
| **S18-12** (Early Warning bullets need investor impact) | RES-9 | Story p1 lines 139-184: every Headline Finding has a sub-bullet "What this means for investors:". 5/5 bullets have the action-clause. | **Yes**. | None. |

**Stakeholder-resolution summary:** 13 items audited. **10 fully met** (S18-1, S18-9 core intent, S18-10, SL-1, SL-2, SL-3, SL-4, SL-5, S18-12, 8-element template, status vocab). **3 partial** (S18-3 walk-forward caption slightly generic; S18-9 sparklines synthetic vs historical; Live Execution subtitle could explicitly say "Placeholder"). **0 unmet.**

---

## Axis 3 — Proposed SOP fixes (APP-*)

Five mechanizations below, ranked by stakeholder-visible impact.

> **Proposed APP-CC1 — Caption Prefix Canonical Vocabulary**
> Caption prefixes on portal pages are drawn from a closed vocabulary: `Takeaway:` (APP-SE5 user-facing one-liner); `What this means:` (reserved for RES translation bridges per RES-2); `How to read this chart:` (Evidence 8-element element 3); `Note:` (disclaimer). No other prefixes allowed. Lives in `app/components/narrative.py::CAPTION_PREFIXES`; CI grep-check rejects unknown prefixes in `st.markdown(f"**{prefix}:**...")` patterns.
> **Closes:** S18-3 spot-check finding + reproducibility gap on caption wording.
> **Blocking?:** No — informational sweep initially.

> **Proposed APP-EX1 — Expander Titles Canonical Registry**
> Every recurring expander title (Plain English, status-legend, trade-log column-legend, strategy-Why-not-all-in, deep-dive-by-method) is looked up from `app/components/expander_titles.py::TITLES`. Emoji policy: one emoji per recurring concept, registered. Ad-hoc titles prohibited for recurring concepts; new concepts added via registry PR.
> **Closes:** "Plain English" vs "ELI5" vs "In plain English" divergence across pairs.
> **Blocking?:** No — migration over next pair.

> **Proposed APP-OR1 — Story-Page Orientation Block Template**
> Every Story page opens with (1) optional Plain English expander (collapsed), (2) H2 headline per RES-11, (3) `st.container(border=True)` titled "Where This Fits in the Portal" explaining the pair's place in the broader catalog, (4) One-Sentence Thesis italicised, (5) KPI row, (6) takeaway caption. Fixed order. Prevents per-pair ordering drift (recurring cost since pair #5).
> **Closes:** Reproducibility gap on Story layout above bullets.
> **Blocking?:** Yes for reference pair (per META-RPD); warning elsewhere.

> **Proposed APP-URL1 — Page URL Slug Pin**
> Add `app/_smoke_tests/slug_test.py` run at deploy time: iterates every `app/pages/*.py`, computes the Streamlit-derived slug (strip leading `N_`, replace `_` with space, title-case), and asserts every `st.page_link("pages/...")` call resolves to a page that exists. Breakage on Streamlit upgrade surfaces before the stakeholder sees a 404.
> **Closes:** Cross-review Bug #5 class (navigation drift); mechanizes `st.page_link` try/except from APP-DP1.
> **Blocking?:** Yes at deploy.

> **Proposed APP-CH1 — Chart-Name Registry Extension (non-method charts)**
> Extend `docs/schemas/chart_type_registry.json` (VIZ-V8) to cover hero, equity_curves, drawdown_comparison, regime visualizations, and history_zoom_* — not just method-block charts. `load_plotly_chart` consults the registry and resolves path via the registry's `canonical_path_pattern`. Removes Ace's per-call-site path discretion.
> **Closes:** Reproducibility gap on chart-name → path mapping; makes APP-EP4 enforceable for all charts, not just method charts.
> **Blocking?:** Yes for reference pair.

> **Proposed APP-SEV1-MAP — Severity Map Lookup Table**
> Build `app/_smoke_tests/severity_map.json`: one row per `(artifact, field)` pair → L1/L2/L3 severity. Every new validation branch Ace writes must register an entry; CI grep-check rejects `st.error` / `st.warning` / silent skip in app/ that isn't covered by the map. Promotes APP-SEV1 from policy to mechanization.
> **Closes:** Reproducibility gap on severity assignment judgement.
> **Blocking?:** Yes — CI rejects unregistered branches.

> **Proposed APP-PV1 — Preview-Row-Count Canonical**
> Data-frame previews on portal pages use a single constant `PREVIEW_ROWS = 10` imported from `app/components/trade_history.py`. Hardcoded `.head(N)` calls flagged by CI grep.
> **Closes:** "first 10 rows" magic-number drift; enables uniform preview across pairs.
> **Blocking?:** No.

> **Proposed APP-TB1 — Tab-Label Canonical Registry**
> Strategy page tabs always read `["Execute", "Performance", "Confidence"]`; Evidence Level-1/Level-2 tabs always read `["Level 1 — Basic Analysis", "Level 2 — Advanced Analysis"]`. Registered in `app/components/tab_labels.py`. Renames require standards-changelog entry.
> **Closes:** Tab-label drift (cross-review Decision table row).
> **Blocking?:** Yes for reference pair.

---

## Axis 4 — Questions to Lesandro

1. **APP-SEV1 severity-map mechanization scope.** Cross-review §5 proposed the map; this audit confirms the need. Do you want `severity_map.json` to ship with HY-IG v2 (reference-pair blocker) or wait until next sprint? Ship-now would take ~1 hour of classification work for the ~25 existing branches, but opens a CI-reject pattern that will catch every future Ace branch.

2. **Who owns expander / tab / caption canonical vocabularies?** These are surface-level English-string choices sitting squarely on the APP/RES boundary. My preference: Ace owns expander titles + tab labels + caption prefixes (they are UI vocabulary); Ray owns narrative glossary (already owned per RES-6). Please confirm or reassign.

3. **APP-CH1 (non-method chart registry extension) scope with Vera.** VIZ-V8 currently registers method charts. Extending to hero / equity_curves / history_zoom_* crosses into Vera's VIZ-NM1 naming territory. Should Ace file the extension proposal or Vera?

4. **"Board-game-like" trigger cards — synthetic vs historical sparklines.** S18-9 is met in spirit but the sparklines are stylised. A historical-zoom variant is a ~2-hour component change. Worth doing for reference pair, or accept the stylised version as permanent?

5. **Story "Plain English" expander position.** Currently above the headline (line 51). Moving it below the headline gives the headline unambiguous first-position prominence per SL-1 / RES-11. Pro: strict headline-first. Con: readers who click the expander first lose the implicit "read more" affordance. My recommendation: move below headline; alternate: keep above but explicitly collapsed and tiny.

> **Top question:** Is APP-SEV1 severity-map mechanization a reference-pair blocker for HY-IG v2 acceptance, or a next-sprint deliverable?

---

## Deliverable ≤300 words

**1. Page/component elements audited:** 25 page/layout elements (Axis 1 table) + 13 stakeholder items (Axis 2 table) across 4 pages (Story, Evidence, Strategy, Methodology) and 7 components (probability_engine_panel, position_adjustment_panel, instructional_trigger_cards, live_execution_placeholder, direction_check, schema_check, charts).

**2. Reproducibility gaps by severity:**
- **High (reference-pair-blocking if strict):** severity-map not yet materialized (APP-SEV1-MAP); non-method chart paths uncodified (APP-CH1); tab + expander + caption vocabularies ad-hoc (APP-CC1, APP-EX1, APP-TB1); Story orientation block order discretionary (APP-OR1).
- **Medium:** trigger-card count/wording mapping lives in code not rulebook; container-border placement; URL slug transformation uncaptured.
- **Low:** preview-row count; column-width ratios; tournament top-N.

**3. Stakeholder-resolution gaps:** 10/13 fully met, 3 partial. Walk-forward caption needs fraction quantification (S18-3); trigger-card sparklines are stylised rather than historical (S18-9); Live-Execution subtitle could say "Placeholder" explicitly (S18-10). Zero unmet. Reference-pair passes stakeholder spirit.

**4. Top 4 rule proposals (priority):**
1. **APP-SEV1-MAP** — severity lookup JSON + CI grep; mechanizes existing APP-SEV1 policy.
2. **APP-CH1** — extend VIZ-V8 registry to cover hero/equity/history_zoom; closes chart-path discretion.
3. **APP-OR1** — Story orientation-block template (headline → Where-This-Fits → thesis → KPIs); ends per-pair layout drift.
4. **APP-CC1 / APP-EX1 / APP-TB1** — closed vocabularies for caption prefixes, expander titles, tab labels; CI grep-check enforced.

**5. Top question for Lesandro:** Is APP-SEV1 severity-map mechanization a reference-pair blocker for HY-IG v2 acceptance, or deferred to next sprint? Ship-now costs ~1 hour on existing branches and activates CI protection for every subsequent branch.

---

**End of audit. Lead consolidates across all 5 validation audits.**
