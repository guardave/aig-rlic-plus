# Cross-Review — AppDev Ace (2026-04-19)

**Reviewer:** AppDev Ace
**Scope:** Audit Ace's boundary contracts with every other agent. Ace is the downstream integration point — every upstream artifact converges here, so leaky contracts surface as portal bugs visible to stakeholders. This review is read-only on all SOPs.

**Context triggers (recent bugs I'm matching against):**
- Wave 3: `charts.py::load_plotly_chart` was render-only with no return channel → GATE-25 placeholder rendered on Cloud while the JSON was fine. Root cause: loader contract with Vera was ambiguous about end-to-end test ownership.
- Wave 3: Hero NBER shading at alpha 0.12 imperceptible. Vera produced per numeric spec; Ace rendered without visual QA. Gap: no "does this tell a story on Cloud" verification on Ace side.
- Wave 4A: `signals_*.parquet` silently excluded by `.gitignore` on Cloud. APP-SE1 pre-render validation caught it at render time (good), but nothing caught it at deploy time. ECON-DS2 + GATE-29 closed the producer / gate sides; Ace side is the APP-ST1 harness.
- Wave 1.5: `winner_summary.json` lacked `signal_column` and `target_symbol` fields. APP-SE1 works around with a literal-name map; contract is still implicit.
- Chart naming drift: Vera's prefix vs. Ace's unprefixed loader — historical "try both" fallback. APP-EP4 (Rule 3.9a) nominally closed this but legacy drift still exists.
- Narrative rendering: Ray delivers markdown; Ace renders via `st.markdown` or `render_narrative()` — table/HTML edge cases surface on Cloud only.

---

### 1. Artifacts Ace produces for other agents

| Artifact | Path / Location | Consumer(s) | Contract rule | Failure mode if missing/malformed |
|----------|-----------------|-------------|---------------|-----------------------------------|
| Streamlit page files | `app/pages/{N}_{pair_id}_{page_type}.py` | Lead (acceptance review); stakeholders (portal); other agents (debugging) | APP-PA1, GATE-9..12 | Page missing → acceptance blocker (GATE-9..12). Page crashes on Cloud → stakeholder sees broken portal. |
| Shared component code | `app/components/*.py` (charts, narrative, execution_panel, probability_engine_panel, glossary, pair_registry, trade_history, etc.) | All pair pages (implicit via import) | Implicit (component API not versioned) | Component signature change → silent breakage across pages until smoke test. |
| Landing page registry | `app/app.py` + `app/components/pair_registry.py` | Lead + stakeholders (navigation entry point) | APP-LP1..LP7, GATE-14 | New pair not registered → not discoverable; Unknown classification → APP-LP7 warning banner. |
| Smoke test harness | `app/_smoke_tests/smoke_loader.py` | Vera (mirrors VIZ-V5 on portal side), Lead (reads log at gate review) | APP-ST1, GATE-27, GATE-29 | Harness absent → GATE-27/29 uncheckable → blocks reference-pair acceptance. |
| Smoke test logs | `app/_smoke_tests/loader_{pair_id}_{YYYYMMDD}.log`, `app/_smoke_tests/clean_checkout_{pair_id}_{date}.log` | Lead (acceptance review), Vera (cross-check vs `_smoke_test_*.log`) | APP-ST1, GATE-27, GATE-29 | Missing log = undocumented gate-pass claim; Lead must re-run. |
| Input Quality Log | `docs/agent-sops/appdev-input-quality-log.md` | All upstream agents (retro input) | APP-IQ1 | Missing entry = lost feedback signal; systemic handoff issues recur. |
| Acceptance-visible narrative rendering (the "final-mile" render of Ray's prose) | Rendered on every portal page | Lead (acceptance), Ray (narrative integrity), stakeholders | APP-RP1, APP-EP1..EP5 (implicit render contract with Ray) | Ray's markdown rendered wrong (tables flattened, HTML leaked) → narrative integrity violation that Ray cannot catch without opening the page. |
| Landing-page card metadata rendering | `app/components/pair_registry.py` → UI | Lead, stakeholders, Ray (cross-pair direction consistency) | APP-LP4..LP6 | Metadata-missing fallbacks (`Unknown`, `—`) can silently ship if producer gaps aren't surfaced as warnings. |

---

### 2. Artifacts Ace consumes from other agents

This is the widest boundary surface in the team and the historical locus of bugs.

#### 2a. From Evan (Econometrics)

| Artifact | Canonical path | Contract rule | Failure mode | Dependent pages |
|----------|---------------|---------------|--------------|-----------------|
| `signals_{date}.parquet` | `results/{pair_id}/signals_{date}.parquet` | ECON-DS1, ECON-DS2 | Missing signal column → APP-SE1 renders `st.error(...)`; file absent on Cloud but present locally → GATE-29 failure; Wave-4A canonical bug. | Strategy page (SE1 Probability Engine, SE2 Position Adjustment) |
| `winner_summary.json` | `results/{pair_id}/winner_summary.json` | GATE-16, META-TWJ (schema), APP-SE1 requires `signal_column` field | **Implicit contract fields** — `signal_column`, `target_symbol`, `threshold_value`. Wave-1.5 flagged missing `signal_column` and `target_symbol`; APP-SE1 and `instructional_trigger_cards.py` now include literal-name fallbacks. Malformed schema → `st.info("Trigger cards unavailable")` or silent `"SPY"` default. | Strategy page (all 3 Execution Panel tabs) |
| `tournament_results.csv` / `tournament_summary.csv` | `results/{pair_id}/tournament_*.csv` | ECON-C2, ECON-H2, GATE-7 | Missing → landing card can't display Sharpe badge (APP-LP4); cross-pair summary breaks. | Landing page, Strategy page. |
| `tournament_top10_equity.csv` | `results/{pair_id}/tournament_top10_equity.csv` | ECON-C2 | Missing → equity-curve chart has no data to augment. | Strategy page (Equity Curve). |
| `execution_notes.md` | `results/{pair_id}/execution_notes.md` | GATE-18 | Missing → Strategy SOP section falls back to raw parameters (declared fallback). | Strategy page > Execute tab. |
| `kpis.json` | `results/{pair_id}/kpis.json` | ECON-H3 | Missing → "Results pending" placeholder (documented) — but no hardcoded fallback. | Hook, Landing, Strategy KPI cards. |
| `interpretation_metadata.json` | `results/{pair_id}/interpretation_metadata.json` | GATE-4, META-CFO, META-IA | Missing direction fields → `"Direction pending"` placeholder; **missing `priority_rank`/`indicator_nature`/`indicator_type`/`strategy_objective` → card classifies as `Unknown`** and is excluded from filtered views (APP-LP7). | Every pair page + landing page. |
| `winner_trade_log.csv` / `winner_trades_broker_style.csv` | `results/{pair_id}/` | ECON-C4, GATE-17 | Empty log → `st.dataframe` renders empty; used to show headers only (HY-IG pair-#5 bug, now upstream fixed). | Strategy > Performance tab. |
| `regime_descriptive_stats.csv`, `granger_by_lag.csv`, `regime_quartile_returns.csv`, `hmm_states.parquet` | `results/{pair_id}/exploratory_*/` or `core_models_*/` | ECON-C2, ECON-E1, ECON-E2 | Missing → evidence sources table shows `Pending`; chart triggers GATE-25 placeholder chain. | Evidence page, Confidence tab. |
| `live_execution_stub.json` | `results/{pair_id}/live_execution_stub.json` | APP-SE4 acceptance (schema: `current_signal_value`, `target_position_pct`, `current_action`, `as_of_date`) | Missing → `—` in `st.metric` (documented); malformed schema → violation logged to `design_note.md`. | Strategy > "Future: Live Execution". |

#### 2b. From Vera (Visualization)

| Artifact | Canonical path | Contract rule | Failure mode | Dependent pages |
|----------|---------------|---------------|--------------|-----------------|
| Per-pair Plotly JSON charts | `output/charts/{pair_id}/plotly/{chart_type}.json` | VIZ-P1, VIZ-NM1, VIZ-A3, APP-EP4 (Rule 3.9a) | **Canonical-filename mismatch** (prefixed vs unprefixed) caused Wave-3 "try both" fallback. APP-EP4 deprecated fallbacks; legacy drift may still exist per pair. Missing chart → APP-EP5 cascade (family substitute → `design_note.md` log → `st.warning`). | Evidence, Strategy, Story (hero). |
| Chart metadata sidecars | `output/charts/{pair_id}/plotly/{chart_type}_meta.json` | VIZ-SD1, VIZ-A5 | Missing caption → fallback chain (Ray's narrative caption → Vera sidecar → `None`); caption mismatch → log warning, prefer Ray. | Evidence page (caption beneath every chart). |
| Canonical historical-episode charts | `output/_comparison/history_zoom_{episode_slug}.json` | VIZ-V1, META-ZI, APP-SE1 loader note | **Wave-3 Bug #2 canonical path** — loader returned None because it had no return channel. Fixed via APP-ST1. Override at `output/charts/{pair_id}/history_zoom_{slug}.json` preferred if present. | Story page cross-references, Evidence page. |
| Chart manifest | `output/charts/chart_manifest.json` | VIZ-CR1 | Missing → Ace must scan directories directly (degrades to slow startup, acceptable); stale manifest → orphan chart references. | Startup discovery (non-blocking). |
| Smoke-test log (producer side) | `output/charts/{pair_id}/plotly/_smoke_test_{YYYYMMDD}.log` | VIZ-V5 | Present and PASS ⇒ Ace's APP-ST1 is the second line. If Vera's log missing, Ace can still run APP-ST1 but loses the Vera-side attestation. | GATE-27 acceptance. |
| Perceptual-check PNG (NBER shading etc.) | `_perceptual_check_{chart}.png` | VIZ-V2 (rev 2026-04-19), META-PV | Missing → Wave-3 NBER-shading-invisible class of bug. Ace does not re-validate; relies on Vera's META-PV PNG. **Gap:** Ace has no rendered-on-Cloud visual check; see Proposed APP-VQ1 below. | Any chart with alpha-shading / low-contrast encoding. |

#### 2c. From Ray (Research)

| Artifact | Canonical path | Contract rule | Failure mode | Dependent pages |
|----------|---------------|---------------|--------------|-----------------|
| Portal narrative | `docs/portal_narrative_{topic}_{date}.md` (or `_{pair_id}_{date}.md`) | RES-EP1..EP4, RES-1..RES-9, RES-PA1..PA3 | Markdown tables / HTML tags / `<!-- expander -->` markers mis-parsed by `render_narrative()` → **formatting regressions surface only on Cloud**. No AST-level validation today. | Every portal page. |
| Portal glossary | `docs/portal_glossary.json` | RES-6, RES-10, RES-VS, ownership split (Ray writes, Ace reads) | Missing term referenced in narrative → tooltip/definition broken; new status vocab not registered → APP-SE5 captions show undefined terms. | Glossary tooltips, Strategy/Confidence captions. |
| Direction annotation batch file | `docs/direction_annotations_batch.json` | META-IA, implicit schema | Missing entry for a pair → "How to Read This" callout falls back to `"Direction pending"` (APP-DA1). | Per-pair Story page callout. |
| Event timeline CSV | `event_timeline_{topic}_{date}.csv` | VIZ-H3 (Ray→Vera primary); Ace reads for chart annotations | Missing → Vera charts lack event markers; downstream silent. | Evidence, Story pages. |
| Storytelling arc doc | `docs/storytelling_arc_{topic}_{date}.md` | RES-PA1 | Missing → Ace must infer page ordering (documented risk); Lead gate may reject. | Portal architecture. |
| Acceptance text / headline | Narrative "headline-first" structure per RES-11 | RES-11 | Narrative-first ordering → GATE-23 / acceptance.md rejection. Ace renders what Ray delivers; Ace cannot repair upstream order violation. | Story page top. |

#### 2d. From Dana (Data)

| Artifact | Canonical path | Contract rule | Failure mode | Dependent pages |
|----------|---------------|---------------|--------------|-----------------|
| Master pair parquet (`_latest` alias) | `data/{pair_id}_daily_latest.parquet` (or `_monthly_`) | DATA-H1, DATA-DD1, Dana _latest convention | Dated filename referenced by portal (instead of `_latest`) → breaks on refresh; wrong unit (bps vs decimal) → silent axis / KPI corruption (DATA-D2 + RES-4). | Hero chart, Evidence data-driven panels. |
| Data dictionary | `data/{dataset}_data_dictionary.csv` | DATA-DD1 | Missing Display Name → axis/KPI labels fall back to canonical column names (ugly). Missing Display Note → tooltip shows nothing. | Axis labels, tooltips. |
| Display-name registry | `data/display_name_registry.csv` | DATA-DD1 extension | Missing → per-pair data-dictionary fallback; inconsistent labels across pairs. | All charts. |
| Data manifest | `data/manifest.json` | DATA-DD1 | Missing → no automated staleness check; `@st.cache_data(ttl=...)` hardcoded by Ace. | Cache config. |

---

### 3. Decisions Ace makes that affect other agents

| Decision | Contract surface | Cross-impact |
|----------|------------------|---------------|
| **Chart-name → filename mapping** (implicit in every `load_plotly_chart("foo", pair_id=...)` call) | Tight coupling with Vera (VIZ-NM1, VIZ-A3, APP-EP4). | Vera renames a chart → every Ace call site breaks silently until APP-ST1 runs. Conversely, Ace refactoring call-site names without coordinating → chart manifest/registry drifts. |
| **Narrative anchor / expander detection** (`<!-- expander: Title -->` marker parsing in `render_narrative()`) | Tight coupling with Ray (RES narrative format). | If Ray switches marker syntax or uses HTML comments inconsistently, Ace's parser skips the expander (silent content loss). Not currently validated end-to-end. |
| **Validation severity** — warning vs error vs silent skip | User-visible behavior; contract implicit to all 4 upstream agents. | APP-SE1 renders `st.error` for missing signal column (loud); landing page shows `Unknown` chip + warning (loud); missing event timeline → silent (quiet). Inconsistent policy means stakeholders can't tell whether a page is "good" or "partial." |
| **Page URL structure** (`app/pages/{N}_{pair_id}_{page_type}.py`) | Affects external linking (breadcrumbs via `breadcrumb.py`, inter-page `st.page_link`), stakeholder bookmarks, and GATE-13 sidebar entry. | Changing numbering or page-type slug breaks Ray's prose cross-references (`See Strategy page`) and Lead's acceptance URLs. Template-page migration (multi-pair scale) changes all URLs at once. |
| **Caption fallback chain order** (Ray narrative → Vera sidecar → None) | APP-EP2. Silent precedence. | If Ray and Vera disagree on a caption, reader sees Ray's; audit trail (Vera's) is silently overridden without surfacing discrepancy. |
| **Which pair is the "reference pair"** (META-RPD — today HY-IG v2) | Sets the gate-28 bar for all other pairs. | Ace's reference-pair renders must be perfect (zero `chart_pending`); stricter gate propagates quality pressure upstream to Evan/Vera/Ray. |
| **Cache TTL for each series** | Affects staleness on Cloud. | Ace hardcoding TTL silently drifts from Dana's Refresh Freq. |
| **Render choice `st.markdown` vs `render_narrative()`** | Determines whether tables / `<!-- expander -->` markers / glossary tooltips render correctly. | Inconsistent usage → Cloud-only formatting bugs that don't show in dev. |

---

### 4. Boundaries where Ace has been bitten

Bug history matched to contract.

1. **Loader had no return channel (Wave 3 Bug #2 — Dot-Com zoom).** `load_plotly_chart` rendered as a side-effect. Resolver + existence checks all PASSed; any parse-stage silent failure produced `None` inside the function, then degraded to GATE-25 placeholder. **Contract gap:** no testable return value, no end-to-end "can this Figure be parsed" check. **Closed by APP-ST1 + GATE-27**, but the underlying meta-lesson ("artifact-existence is not render-success") now needs an ongoing policy, not a one-off rule.

2. **NBER shading imperceptible on Cloud (Wave 3 Hero chart).** Vera produced per numeric spec (alpha=0.12). Ace rendered without rendered-on-Cloud visual QA. **Contract gap:** META-PV and VIZ-V2 address the producer side; Ace has no mandatory rendered-Cloud visual pass. **Partially closed** (perceptual PNG at Vera side); Ace still lacks an on-Cloud audit step.

3. **Signals parquet not on Cloud (Wave 4A).** APP-SE1 pre-render validation rendered `st.error(...)` correctly on Cloud (the validation worked!), but the deployment gap (`.gitignore` blanket `*.parquet`) only surfaced AFTER deploy. **Closed** by ECON-DS2 (producer) + GATE-29 (gate) + APP-ST1 clean-checkout mode.

4. **`winner_summary.json` field schema implicit (Wave 1.5).** APP-SE1 and trigger cards carry literal-name fallbacks for missing `signal_column` and `target_symbol`. Contract is technically satisfied (the file exists) but the field inventory is undocumented. **Open gap** — see Proposed APP-WS1 below.

5. **Chart-name prefix drift.** Vera's output prefix convention vs. Ace's loader call-site convention diverged historically; the loader had a "try both" fallback that APP-EP4 deprecated. **Likely still present** in legacy pages not yet migrated. **Open gap** on cleanup — no forcing function today.

6. **Narrative markdown edge cases (tables, HTML tags, expander markers) surface only on Cloud.** No local rendered-Cloud test step; `render_narrative()` regressions only caught by Lead at acceptance. **Open gap** — see Proposed APP-NR1 below.

7. **Landing-page Unknown silence before APP-LP7.** Prior to APP-LP7, `Unknown` classification silently displayed on cards. Closed by APP-LP7 but shows the pattern: **Ace's "graceful degradation" can mask upstream gaps unless explicitly surfaced.**

Meta-pattern across these bugs: **every Ace bug of the last 3 waves was at a contract edge, not inside Ace's own code.** The files Ace wrote were correct against the contract Ace had. The contracts themselves were ambiguous or implicit.

---

### 5. Proposed new rules

> **Proposed APP-WS1 — `winner_summary.json` Required-Fields Contract (elevate from implicit to explicit)**
> - Rule text: `results/{pair_id}/winner_summary.json` must contain the following required fields for Ace to render the Strategy page without literal-name fallbacks: `signal_column` (string, matches a column in `signals_{date}.parquet`), `target_symbol` (string, matches the pair's target ticker), `threshold_value` (float), `strategy_family` (one of `P1_long_cash` | `P2_long_short` | `P3_dynamic_size` | `P4_vol_target`), `direction` (one of `pro_cyclical` | `counter_cyclical` | `conditional`). On load, Ace validates; a missing required field blocks Strategy-page render (`st.error`) and is a GATE-11 / GATE-16 regression for that pair. Existing literal-name map fallback is deprecated and removed once every pair has a conforming file.
> - Closes gap: Wave-1.5 (missing `signal_column` / `target_symbol`) — today the fallback works but is invisible to the producer.
> - Blocking?: **Yes**. Ace refuses to render Strategy page without the fields.
> - Cross-reference: ECON-H2 (App Dev Handoff Template), META-TWJ (Tournament Winner JSON Schema — merge this rule into META-TWJ as an extension).

> **Proposed APP-NR1 — Narrative Rendering Smoke Test (end-to-end parse+render of Ray's markdown)**
> - Rule text: Before Ace finishes a page that consumes `docs/portal_narrative_{topic}_{date}.md`, run `app/_smoke_tests/smoke_narrative.py {pair_id}` which (a) parses the narrative markdown with the same tokenizer `render_narrative()` uses, (b) asserts every `<!-- expander: -->` marker has a matching close, (c) asserts every referenced chart filename exists, (d) asserts every glossary term referenced in the narrative is present in `docs/portal_glossary.json`, (e) asserts no raw HTML tags leak through (unless wrapped in an approved safe-HTML helper). Failure = blocker.
> - Closes gap: Cloud-only narrative formatting regressions (tables, HTML, expander markers, glossary drift). Wave-3 flagged the pattern but no automation today.
> - Blocking?: **Yes** for reference pairs; warning for non-reference pairs.
> - Cross-reference: RES-EP1..EP4, RES-6, APP-EP1..EP5; companion to VIZ-V5 and APP-ST1 (same "end-to-end or you can't know" lineage).

> **Proposed APP-VQ1 — Rendered-on-Cloud Visual QA Step (per reference pair)**
> - Rule text: For every reference-pair page, after deploy, Ace runs a headless-Playwright capture against the Cloud URL (not localhost) for all 4 page types, saves PNGs under `app/_smoke_tests/visual_{pair_id}_{page_type}_{YYYYMMDD}.png`, and asserts each capture meets two checks: (a) **viewport-level perceptibility** — any chart marked with `perceptual_dependent=true` in its Vera sidecar must have a pixel-level contrast of ≥ threshold against the background across a sample of viewport locations; (b) **zero `chart_pending` DOM occurrences** (GATE-28 mechanized). Failure = acceptance blocker for reference pairs.
> - Closes gap: Wave-3 NBER-shading-invisible class. META-PV currently lives on Vera's side (PNG at producer) but Cloud rendering (font rendering, browser zoom, cache) can still degrade. Also mechanizes GATE-28.
> - Blocking?: **Yes** for reference pairs (per META-RPD).
> - Cross-reference: META-PV, VIZ-V2 (rev 2026-04-19), GATE-28.

> **Proposed APP-SEV1 — Validation-Severity Policy (loud vs quiet vs silent)**
> - Rule text: Every `if not file.exists()` / `if not column.present()` / `except` branch in portal code MUST map to one of three severity levels and render accordingly: (L1 **Loud-Error** / `st.error`) when a required artifact is missing and the page's primary purpose cannot be served (e.g. APP-SE1 signal column missing); (L2 **Loud-Warning** / `st.warning`) when the primary purpose can be degraded gracefully but the gap is meaningful (e.g. missing perceptual PNG, missing override chart with canonical fallback); (L3 **Caption-Note** / `st.caption`) for minor gaps (e.g. missing caption text, falling back to Vera sidecar). **Silent skip is prohibited.** A canonical mapping table lives in `app/_smoke_tests/severity_map.json`; every new code path is registered before merge.
> - Closes gap: inconsistent Ace decision-making about when to render a placeholder vs warning vs error — the root cause of "graceful degradation masks upstream gaps."
> - Blocking?: **Yes** — CI grep-check rejects new `except: pass`, silent `return`, or bare `continue` in `app/`.
> - Cross-reference: META-UNK (Unknown Is Not A Display State — same philosophy extended to all gap states), GATE-25, GATE-28.

> **Proposed APP-CN1 — Canonical Chart-Name Conformance Sweep (retire legacy fallbacks)**
> - Rule text: Ace runs `app/_smoke_tests/chart_name_sweep.py` over all `load_plotly_chart(...)` call sites per pair; any call site whose resolved filename does not match the canonical `output/charts/{pair_id}/plotly/{chart_type}.json` (or the META-ZI canonical/override pair for history zooms) is reported as a legacy fallback. Zero legacy fallbacks = ship-ready. This sweep is re-run on every pair rerun and on every Vera canonical-catalog revision.
> - Closes gap: chart-name prefix drift; historical "try both" fallback the team has been trying to retire since APP-EP4 was written.
> - Blocking?: **Yes** for reference pairs; informational for non-reference pairs until legacy pair migration is complete.
> - Cross-reference: APP-EP4 (Rule 3.9a), VIZ-NM1, VIZ-A3.

> **Proposed APP-TC1 — Cache TTL Derived From Dana Manifest (no hardcoded TTLs)**
> - Rule text: Every `@st.cache_data(ttl=...)` TTL value in portal code must be derived at import time from `data/manifest.json` (Dana's Refresh Freq) via a helper `resolve_ttl(alias_path)`. Hardcoded numeric TTLs in portal modules are prohibited (CI grep-check). If `manifest.json` is missing the alias, `resolve_ttl` raises — the missing manifest entry is the bug, not the missing TTL.
> - Closes gap: silent Ace-Dana TTL drift; missing staleness banner when Dana updates Refresh Freq.
> - Blocking?: **No** (warning during pair assembly), **Yes** at reference-pair acceptance.
> - Cross-reference: DATA-H2 (Data-to-AppDev Handoff), DATA-DD1, APP-DL1.

> **Proposed APP-DIR1 — Direction Annotation Integrity Check (cross-pair, mechanized)**
> - Rule text: At landing-page load, `pair_registry` validates that every loaded pair's `interpretation_metadata.json` `direction` field matches (a) the direction encoded in Vera's chart line-style (via sidecar `direction` field), (b) the direction asserted in Ray's narrative (via a new required `direction_asserted` frontmatter field in `docs/portal_narrative_*.md`). Mismatches log to `app/_smoke_tests/direction_integrity_{date}.log` and render as a warning chip on the affected card. Three-way consistency (Evan / Vera / Ray) is a reference-pair blocker.
> - Closes gap: META-IA (Interpretation Annotation Handoffs) is a 4-agent protocol with no mechanized verification at render time. Today a direction change by Evan can ship without Vera's chart or Ray's prose catching up.
> - Blocking?: **Yes** for reference pairs.
> - Cross-reference: META-IA, META-CFO, VIZ-A3 (line style), RES-B2..B4, APP-DA1.

---

### 6. Questions to other agents (for consolidation phase)

**Evan (Econometrics):** Can you commit to elevating `winner_summary.json` to a canonical schema document (extending META-TWJ) with `signal_column`, `target_symbol`, `threshold_value`, `strategy_family`, and `direction` as required fields — so that my APP-WS1 replaces the current literal-name fallbacks, and I can remove that workaround code? And: when you add a new derived-signal family (e.g. a new HMM variant), can you update `signal_column` naming conventions in the same PR as the signal-production code, so that my Strategy-page render doesn't silently fall back?

**Vera (Visualization):** Your VIZ-V5 smoke test and my APP-ST1 cover the same Figure-integrity question from two sides (producer vs consumer). Can we align their assertions exactly (Figure not None, ≥1 trace, non-empty title) and cross-reference each other's log files in `acceptance.md`? And more pointed: for charts with alpha-shading / low-contrast perceptual dependencies, can your `_perceptual_check_*.png` carry a `perceptual_dependent=true` tag in the sidecar so my proposed APP-VQ1 knows which charts to re-validate on Cloud (vs. skipping charts that don't need visual QA)?

**Ray (Research):** Your narrative markdown currently uses `<!-- expander: Title -->` HTML-comment markers that my `render_narrative()` parses — but the parser has no validation that opens and closes match, or that referenced charts/glossary terms exist. Would you agree to: (a) a machine-readable frontmatter block at the top of every `docs/portal_narrative_*.md` listing expander titles, chart references, and glossary terms used, so my proposed APP-NR1 smoke test can validate the manifest against the prose? (b) Adding a `direction_asserted` frontmatter field that my proposed APP-DIR1 can cross-check against Evan's metadata and Vera's chart line style?

**Dana (Data):** The `data/manifest.json` is documented in your SOP, but my portal code currently hardcodes `@st.cache_data(ttl=86400)` values rather than reading from the manifest. Can you confirm the manifest schema is stable (fields: `alias`, `refresh_freq`, `refresh_source`, `last_updated`, `mixed_freq_ttl_note`) so I can write `resolve_ttl()` per APP-TC1 with confidence, and commit to updating the manifest whenever you change a Refresh Freq? And: can the manifest carry an explicit `_latest`-alias existence assertion so my pre-deploy smoke test catches "alias not updated on this rerun" silently (Cloud-only bug class)?

---

**End of audit. Lead consolidates across all 5 reviews.**
