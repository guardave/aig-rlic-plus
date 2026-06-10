# Dashboard Page Standard

**Version:** 1.0.0  
**Effective:** 2026-05-12  
**Owner:** Lead (Lesandro)  
**Enforced by:** `app/components/page_templates.py` — `_validate_config()`  
**Cross-references:** `docs/agent-sops/appdev-agent-sop.md` (APP-PT1, APP-TT1, APP-NAV1, APP-SEV1), `docs/agent-sops/team-coordination.md` (META-CDR, META-SRV)

---

## Purpose

This document is the single authoritative specification for what every pair dashboard must contain. It defines:

1. Which sections on each page are **mandatory** (must render; missing = L1 error) vs **optional** (renders when config/artifact present; absent = silent or L3 caption)
2. The **crisis-episode zoom** minimum requirement (4 canonical episodes + optional extras)
3. The **just-in-time glossary** convention (info icons beside technical terms)

`page_templates.py` enforces this spec programmatically via `_validate_config()`. This document is the human-readable source of truth that `_validate_config()` implements. If they ever disagree, this document wins — file a bug against the code.

---

## Mandatory vs Optional — Definition

| Label | Meaning | Template behavior when missing |
|---|---|---|
| **Mandatory** | Must be present in every production pair | `st.error()` (APP-SEV1 L1) — page renders the error and stops the section |
| **Optional** | Improves quality but pair can ship without it | `st.caption()` (APP-SEV1 L3) noting the gap, then continues |

A section that is optional but present must still meet all formatting, caption, and glossary-icon standards. "Optional" means the section may be absent — not that it may be low quality.

---

## Prerequisites — Hard Gate Before Production Registration

**Rule DPS-PRE1 — Final Exam Must Have Been Run**

A pair may not be registered for production (appear on the landing page, have active page links) unless its `evidence_status.json` shows that the final exam has been run. The hard gate is the act of running the exam — not the outcome.

| `evidence_status` | Meaning | Production allowed? |
|---|---|---|
| `found_in_search` | Exam never run | **No — blocked** |
| `needs_final_exam` | Exam not yet run | **No — blocked** |
| `passed_final_exam` | Exam run and passed | Yes — normal display |
| `failed_final_exam` | Exam run and failed | Yes — with disclosure banner |

**Blocked pairs** (`found_in_search` / `needs_final_exam`) must not appear in the landing page card grid or have navigable page links. `validate_pair_completeness.py` reports this as a FAIL and the pair registry must exclude them.

**Failed pairs** (`failed_final_exam`) are production-eligible. They are shown with a prominent `st.warning` disclosure banner (APP-SEV1 L2) on the Strategy page and on the landing card, surfacing the exam outcome so stakeholders can make an informed judgment. The `failure_reasons` array from `evidence_status.json` is displayed verbatim in the banner. Hiding a failure is worse than showing it — an informed stakeholder is better than a misled one.

**Schema:** `docs/schemas/evidence_status.schema.json` v1.2.0. The `failed_final_exam` status requires: `confirmation_test`, `confirmation_window`, `technical_note`, `plain_english`, `failure_reasons` (array, ≥1 entry), `owner`, and a complete `final_exam` block with `qa_status: "qa_passed"` (QA must verify the exam was run correctly even when it fails).

---

## All Pages — Universal Requirements

These apply to every page (Story, Evidence, Strategy, Methodology) without exception.

| Requirement | Rule | Mandatory |
|---|---|---|
| `st.title(display_name)` as the first `st.*` call after `set_page_config` — human-readable display name, never raw `pair_id` slug | APP-TT1 | **Yes** |
| Sidebar (`render_sidebar`) | APP-PT1 | **Yes** |
| Glossary sidebar (`render_glossary_sidebar`) | APP-PT1 | **Yes** |
| 4-step breadcrumb: Story → Evidence → Strategy → Methodology | APP-PT1 | **Yes** |
| "Plain English" expander — non-technical summary of the page | APP-PT1 | **Yes** |
| Bottom "Continue to…" navigation via `st.page_link` (never bare markdown links) | APP-NAV1 | **Yes** |
| Footer caption (`generated with AIG-RLIC+ \| Pair: {pair_id}`) | APP-PT1 | **Yes** |
| Info icons (§ Info Icon Convention below) beside every defined technical term in headings and labels | DPS-II1 | **Yes** |

---

## Story Page

The Story page is the layperson entry point. It must be readable by a non-technical stakeholder with no statistical background. Every mandatory section must be substantively populated — placeholder text is a gate failure.

| Section | Mandatory | Notes |
|---|---|---|
| Plain English expander | **Yes** | Pair-specific prose required; generic fallback text is a gate failure |
| Headline H2 (OOS Sharpe summary line) | **Yes** | Derived from `winner_summary.json` |
| Key metrics bullets (Sharpe / Return / Max DD vs B&H) | **Yes** | Derived from `winner_summary.json` |
| Where This Fits container | **Yes** | Explains the pair's role in the broader portal |
| One-sentence thesis | **Yes** | Must be authored per pair; no generic fallback |
| 5-column KPI row (OOS Sharpe / OOS Return / Max DD / Signal / OOS Period) | **Yes** | Derived from `winner_summary.json` |
| KPI caption ("What this shows") | **Yes** | Must be pair-specific; no generic fallback |
| Narrative section 1 | **Yes** | Ray-authored; minimum 2 paragraphs |
| Hero chart | **Yes** | `output/charts/{pair_id}/plotly/hero.json` — L1 error if missing |
| Regime chart | **Yes** | `output/charts/{pair_id}/plotly/regime_stats.json` — L1 error if missing. **Format standard (VIZ-QR1, 2026-06-10):** dual-panel side-by-side — Annualized Sharpe (left) + Annualized Return % (right) per quartile, same quartile x-axis and per-quartile colors in both panels, value labels outside bars. Reference implementation: `scripts/generate_charts_umcsent_xlv.py::chart_regime_stats`. Single-metric quartile charts are a gate failure for new pairs and a retro-apply item for existing ones. |
| Crisis-episode zoom charts | **Yes** | See § Crisis-Episode Zoom Requirement below |
| Narrative section 2 | **Yes** | Ray-authored; minimum 1 paragraph |
| Transition → Evidence | **Yes** | `render_transition` + `st.page_link` |
| Scope note | Optional | Renders if `SCOPE_NOTE` in config |

---

## Evidence Page

The Evidence page is the statistical proof layer. Every method block must follow the 8-element structure (RES-EP1). Incomplete blocks are a gate failure — the template renders `st.error()` and skips the block rather than show partial content.

### Page-level sections

| Section | Mandatory | Notes |
|---|---|---|
| Plain English expander | **Yes** | Pair-specific |
| Overview text | **Yes** | Motivates the multi-method approach |
| Structure explainer (8-part method description) | **Yes** | Standard text; template provides canonical version |
| Tier explainer (Level 1 / Level 2 rationale) | **Yes** | Standard text; template provides canonical version |
| Download archived CSVs expander | **Yes** | `downloads` list in `EVIDENCE_METHOD_BLOCKS` — each entry `{label, path}` pointing at the pair's statistical result CSVs (core-models tables or equivalent). Labels must state what the file contains with row counts verified against the file at authoring time. Missing files render an inline note, not an error. Introduced by vichua4b's building-permit-spy-fix (3c8b10d); extended to all pairs 2026-06-10 per stakeholder direction (fix260610_downloads_all_pairs). |
| Level 1 tab — minimum 3 method blocks | **Yes** | Fewer than 3 is a gate failure |
| Level 2 tab — minimum 2 method blocks | **Yes** | Fewer than 2 is a gate failure |
| Tournament pointer | **Yes** | Links to Strategy page leaderboard |
| Transition → Strategy | **Yes** | `st.page_link` |

> **Moved 2026-06-10 (fix260610_xpair_general):** the Cross-Period Consistency
> section previously lived on the Evidence page. Per stakeholder direction it
> now lives on the **Strategy page, Confidence tab** (see below) — its content
> answers "does the strategy's edge persist across regimes?", which is a
> deployment-confidence question, not a statistical-proof question.

### Each method block — 8-element structure (RES-EP1)

| Element | Mandatory | Notes |
|---|---|---|
| Method heading + theory body | **Yes** | |
| Question (italic blockquote) | **Yes** | |
| How to read it | **Yes** | |
| Chart | **Yes** | L1 if `chart_status == "ready"` but artifact missing; L2 if `chart_status != "ready"` |
| Observation ("What this shows") | **Yes** | |
| Interpretation ("Why this matters") | **Yes** | |
| Key message (`st.info` box) | **Yes** | |
| "Why this matters" opener | Optional | Recommended for methods that need motivation |
| Regime context callout | Optional | For HMM / regime-conditional methods |
| Deep dive expander | Optional | Strongly recommended for technical methods (HMM, cointegration, IV, GARCH) |

---

## Strategy Page

The Strategy page answers "how do I use this?" It must be executable — a reader should be able to act on the winning rule after reading this page.

| Section | Mandatory | Notes |
|---|---|---|
| Plain English expander | **Yes** | Pair-specific |
| Direction triangulation (`render_direction_check`) | **Yes** | APP-DIR1 |
| Tournament Winner spotlight card | **Yes** | Signal rule in plain English |
| Evidence status badge | **Yes** | APP-LP8; reads `evidence_status.json` |
| How signal is generated | **Yes** | Pair-specific narrative; no generic fallback |
| 5-column KPI row (OOS Sharpe / OOS Return / Max DD / Turnover / Win Rate) | **Yes** | |
| Execute tab | **Yes** | See sub-items below |
| Performance tab | **Yes** | See sub-items below |
| Confidence tab | **Yes** | See sub-items below |
| Transition → Methodology | **Yes** | Live execution placeholder + `st.page_link` |

### Execute tab

| Element | Mandatory | Notes |
|---|---|---|
| Strategy Summary (signal / threshold / family / direction / lead — 2-column layout) | **Yes** | |
| Probability Engine Panel (signal time-series + threshold lines) | **Yes** | APP-SE1; L1 if `signals_{date}.parquet` missing |
| Position Adjustment Panel (exposure 0–100%) | **Yes** | APP-SE2; L1 if signal invalid |
| Instructional Trigger Cards | **Yes** | APP-SE3; minimum 2 cards (BUY-side + REDUCE-side) |
| Manual-use guidance | **Yes** | Step-by-step instructions for using the signal manually; no generic fallback |

### Performance tab

| Element | Mandatory | Notes |
|---|---|---|
| Equity curves chart | **Yes** | `equity_curves.json` — L1 if missing |
| Drawdown chart | **Yes** | `drawdown.json` — L1 if missing |
| Trade log block | **Yes** | APP-TL1; both CSVs required (L1 if both missing, L2 if one missing) |
| — Simulated-vs-real disclosure | **Yes** | |
| — Two-file model explanation | **Yes** | |
| — Column glossary | **Yes** | |
| — Pair-specific example | **Yes** | Ray-authored; generic fallback is L3 caption |
| — Column dictionary expander | **Yes** | |
| — Dual download buttons (broker-style + position log) | **Yes** | |
| — 10-row broker-style preview | **Yes** | |

### Confidence tab

| Element | Mandatory | Notes |
|---|---|---|
| Walk-forward rolling Sharpe chart | **Yes** | `walk_forward.json` — L1 if missing |
| Cross-Period Consistency section | **Yes** | Moved here from Evidence page 2026-06-10. See sub-items below. |
| Tournament scatter chart | **Yes** | `tournament_scatter.json` — L1 if missing |
| Tournament leaderboard (top 10 + benchmark row) | **Yes** | Derived from `tournament_results_{date}.csv` |
| Caveats | **Yes** | Must be pair-specific; documents known limitations and failure modes |

### Cross-Period Consistency sub-sections (Confidence tab)

| Chart | Mandatory | Notes |
|---|---|---|
| Sub-period Sharpe | **Yes** | L1 error if artifact missing |
| Rolling Correlation | **Yes** | L1 error if artifact missing |
| Structural Break | **Yes** | L1 error if artifact missing |
| Rolling Sharpe (CP) | Optional | Renders if artifact exists |
| Rolling Granger | Optional | Renders if artifact exists |

Placement within the tab: after Walk-Forward Rolling Sharpe, before Tournament
Scatter. Rationale: walk-forward and cross-period both answer "does the edge
persist over time?"; scatter and leaderboard answer "how was the winner
selected?". Grouping by question keeps the tab narrative coherent.

---

## Methodology Page

The Methodology page is the technical appendix for replication and critique. Every section must be substantively populated; stub tables or placeholder narratives are gate failures.

| Section | Mandatory | Notes |
|---|---|---|
| Plain English expander | **Yes** | Pair-specific |
| Sample period metrics (OOS window + total combos) | **Yes** | Derived from `winner_summary.json` |
| Data Sources table | **Yes** | Ray-authored; canonical column set: Category / Source / Series / Frequency |
| Indicator Construction narrative | **Yes** | Ray-authored; explains how raw data becomes signals |
| Signal Universe table (`render_signal_universe`) | **Yes** | APP-SS1; reads `signal_scope.json` |
| Stationarity Tests table | **Yes** | L2 warning if CSV missing |
| Econometric Methods table | **Yes** | Ray-authored; canonical columns: Method / Question It Answers / Why We Chose It |
| Tournament Design table | **Yes** | Ray-authored; grid dimensions (signals × thresholds × strategies × leads) |
| Analyst Suggestions section | **Yes** | Empty state renders gracefully; section heading still appears |
| Exploratory Insights section | Optional | Silent no-op if no entries in `analyst_suggestions.json` |
| References | **Yes** | Minimum 3 citations; grouped by topic |

---

## Crisis-Episode Zoom Requirement

**Rule DPS-EP1** — Every Story page must include at least the following 4 canonical crisis episodes. Pair configs may add additional episodes (`HISTORY_ZOOM_EPISODES` list) but may not ship fewer than these 4.

| Slug | Episode | Window |
|---|---|---|
| `dotcom` | Dot-com bust | 2000-03 to 2002-10 |
| `gfc` | Global Financial Crisis | 2008-09 to 2009-06 |
| `covid` | COVID crash | 2020-02 to 2020-06 |
| `inflation_2022` | Inflation / rate-shock drawdown | 2022-01 to 2022-12 |

Each episode entry requires:
- `slug` — matches the chart filename `history_zoom_{slug}.json`
- `title` — human-readable episode name
- `narrative` — 1–3 sentences explaining what the signal did during this episode (Ray-authored)
- `caption` — one-line "how to read it" for the chart

Chart artifacts live at `output/charts/{pair_id}/plotly/history_zoom_{slug}.json`. Missing artifact = L1 error (not pending — these are mandatory).

Perceptual PNG sidecars (`_perceptual_check_history_zoom_{slug}.png`) are required per VIZ-CV1.

**Chart layout standard (mandatory):** All `history_zoom_{slug}.json` charts — and any other multi-panel chart whose horizontal dimension is time (e.g. hero dual-panel, equity-curves with stacked indicator panel) — MUST follow Rule **VIZ-TS1** (Shared Time Axis for Multi-Panel Time-Series Charts) in `docs/agent-sops/visualization-agent-sop.md`. Exactly one set of date tick labels is rendered below the bottom panel; the two panels share a synchronised time range via `xaxis.matches = "x2"`. Violations are a BLOCKING handoff gate.

---

## Failed-Final-Exam KPI Routing

**Rule DPS-FE2** — When `evidence_status.status == "failed_final_exam"`, the Story page and Strategy page top-of-page KPI row MUST display the **holdout** Sharpe / annualised return / max drawdown from `final_exam_results.json` as the **primary** headline metric. The tournament-OOS numbers from `winner_summary.json` may appear as a secondary "Search Phase" sub-row with an explicit qualifier caption.

### Why this rule exists

The v4 reference case shipped with this defect: `evidence_status.status` was `failed_final_exam` but the Story KPI row headlined "OOS Sharpe 1.32" — the tournament-OOS number from `winner_summary.json`. A reader landing on the Story page saw a strong-looking Sharpe as the headline, then had to read the Strategy page disclosure banner to discover the holdout actually returned -13%. The two pages cited different windows for the same "OOS" label, and the reader had no way to know which one was the verdict.

The rule eliminates the failure mode by binding KPI routing to `evidence_status.status` at the template level, not at the producer's discretion.

### KPI routing matrix (template-level, owned by Ace per APP-PLB1)

| `evidence_status.status` | Headline KPI source | Optional secondary row | Headline KPI label |
|---|---|---|---|
| `passed_final_exam` | `final_exam_results.holdout_*` | `winner_summary.oos_*` as "Search Phase" sub-row (optional) | "Holdout Sharpe" |
| `failed_final_exam` | `final_exam_results.holdout_*` | `winner_summary.oos_*` as "Search Phase (did not generalise)" sub-row (recommended for context) | "Holdout Sharpe (failed)" |
| `found_in_search` | `winner_summary.oos_*` | None | "Search-phase OOS Sharpe (no holdout test yet)" |
| `pending_final_exam` | `winner_summary.oos_*` | None | "Search-phase OOS Sharpe (holdout pending)" |
| `inconclusive` | `winner_summary.oos_*` | `final_exam_results.holdout_*` if computed | "Search-phase OOS Sharpe (holdout inconclusive — see disclosure)" |

### Window labelling rule

Any KPI cited on a page MUST be labelled with its window in the KPI row, not just in body prose. A reader scanning the KPI row must be able to tell which window each number is over without reading further.

- ✅ `OOS Sharpe 1.32 (search 2014-08–2020-06)` + `Holdout Sharpe 0.31 (test 2020-07–2026-05)`
- ❌ `OOS Sharpe 1.32` alone with the window explained in a caption two sections below

### Cross-reference

- **APP-PLB1** (Ace owns the template wiring that routes by status; this is plumbing, not content)
- **ECON-CAP1** (Evan owns `final_exam_results.json` and the `evidence_status.plain_english` framing the template displays)
- **LEAD-FR1 Checkpoint 2** (Lead reviews framing at Step 3 — confirms `evidence_status.status` and the framing language match)
- **RES-CAP1** (Ray's narrative cannot headline tournament-OOS numbers on a `failed_final_exam` pair)
- **GATE-RW1** (Reader walk catches any escaped KPI-routing defect at Step 5)

---

## Term Naming Convention

**Rule DPS-LF1 (added 2026-06-10, fix260610_xpair_general)** — Every technical term, ticker, or abbreviation appearing on a dashboard surface must be written in **long form first with the abbreviation in brackets** on its first mention per page. Subsequent mentions on the same page may use the short form.

Examples:
- "Industrial Production (INDPRO)" — then "INDPRO" thereafter
- "Energy Select Sector SPDR (XLE)" — then "XLE" thereafter
- "Michigan Consumer Sentiment (UMCSENT)" — then "UMCSENT" thereafter
- "Hidden Markov Model (HMM) stress probability" — then "HMM" thereafter

Scope: page titles, KPI captions, chart titles + axis labels on first chart of a page, narrative prose, landing-page cards, sidebar finding labels. Raw pipeline tokens (e.g. `gold_copper_zscore_126d`) must NEVER appear on a user surface — humanise via `display_names.py` helpers.

The canonical long-form/short-form pairs live in `app/components/display_names.py` (`INDICATOR_NAMES` = long form, `SHORT_INDICATOR_LABELS` = abbreviation). A helper `long_form_with_abbrev(pair_id)` returns the combined "Long Form (ABBREV)" string for first-mention use. Cross-references BL-VIZ-NS1 (now promoted to live rule VIZ-NS1 in the Visualization SOP).

---

## Info Icon Convention

**Rule DPS-II1** — Every defined technical term appearing in a page heading, label, KPI card, or method block heading must be accompanied by an inline info icon that surfaces its plain-English definition on click.

### What counts as a defined term

A term is "defined" if it has an entry in `docs/portal_glossary.json` under the `"terms"` key. The canonical list as of this version includes: Basis point, Credit spread, HMM stress probability, Sharpe ratio, Max drawdown, Out-of-sample, In-sample, Validation window, Holdout, Z-score, DSR (Deflated Sharpe Ratio), Granger causality, Cointegration, NBER recession, Regime, and all signal/threshold/strategy codes (S1–S6, T1–T4, P1–P3).

When a new term is introduced for a pair, the term must be added to `portal_glossary.json` in the same wave before the pair ships.

### Implementation

Info icons are rendered using `st.popover("ⓘ")` (Streamlit ≥ 1.31). The component is exposed as `info_icon(term_key)` from `app/components/glossary_inline.py`.

```python
# Usage pattern — term beside a heading
col1, col2 = st.columns([10, 1])
with col1:
    st.markdown("### HMM Stress Probability")
with col2:
    info_icon("HMM stress probability")
```

The popover content renders the `plain_english` field from `portal_glossary.json` for the given term, followed by an `example` line if present. The `technical` field is not shown in the popover — it belongs in the Deep Dive expander.

**Fallback:** If the term key is not found in the glossary, the icon renders with "Definition pending — add this term to `docs/portal_glossary.json`." This is an L3 caption, not an error. It makes glossary gaps visible without breaking the page.

### Where info icons are required

| Location | Required on |
|---|---|
| Story — KPI row labels | All 5 labels |
| Story — "Where This Fits" heading | No (section title is self-explanatory) |
| Evidence — method block headings | Every method name that is a defined term |
| Evidence — "How to read it" labels | Any metric name (Sharpe, p-value, CI, etc.) |
| Strategy — Strategy Summary fields | Signal code, threshold, strategy family, direction |
| Strategy — KPI row labels | All 5 labels |
| Strategy — Confidence tab headings | Walk-forward, DSR, bootstrap CI |
| Methodology — Methods table entries | Every method name in the Method column |
| All pages — any `st.metric` label | If the label contains a defined term |

### What info icons are NOT required on

- Plain prose paragraphs (Ray writes these to be self-explanatory)
- Chart axis labels (handled by chart caption)
- Download button labels
- Navigation elements (breadcrumb, page links)

---

## Artifact Checklist

For reference: complete list of artifacts that must exist before a pair can pass acceptance.

### Mandatory artifacts (`results/{pair_id}/`)

| Artifact | Owner |
|---|---|
| `interpretation_metadata.json` | Evan / Dana |
| `winner_summary.json` | Evan |
| `evidence_status.json` (schema v1.1.0, status `passed_final_exam`) | Evan |
| `tournament_results_{date}.csv` | Evan |
| `stationarity_tests_{date}.csv` | Evan |
| `signals_{date}.parquet` | Evan |
| `signal_scope.json` | Evan |
| `winner_trade_log.csv` | Evan |
| `winner_trades_broker_style.csv` | Evan |

### Mandatory artifacts (`output/charts/{pair_id}/plotly/`)

| Artifact | Owner |
|---|---|
| `hero.json` + `_perceptual_check_hero.png` | Vera |
| `regime_stats.json` + perceptual PNG | Vera |
| `equity_curves.json` + perceptual PNG | Vera |
| `drawdown.json` + perceptual PNG | Vera |
| `walk_forward.json` + perceptual PNG | Vera |
| `tournament_scatter.json` + perceptual PNG | Vera |
| `subperiod_sharpe.json` + perceptual PNG | Vera |
| `rolling_correlation.json` + perceptual PNG | Vera |
| `structural_break.json` + perceptual PNG | Vera |
| `history_zoom_dotcom.json` + perceptual PNG | Vera |
| `history_zoom_gfc.json` + perceptual PNG | Vera |
| `history_zoom_covid.json` + perceptual PNG | Vera |
| `history_zoom_inflation_2022.json` + perceptual PNG | Vera |

### Optional artifacts

| Artifact | Effect if missing |
|---|---|
| `analyst_suggestions.json` | Exploratory Insights section silently omitted |
| `environment_interaction_scores.json` | Dana radar panel shows L2 info callout |
| `strategy_survival_scores.json` | Dana radar panel shows L2 info callout |
| `rolling_sharpe_cp.json` | Cross-period section omits this chart |
| `rolling_granger.json` | Cross-period section omits this chart |
| `history_zoom_{custom_slug}.json` | Only if beyond the 4 mandatory episodes |

---

## GATE-DPS1 — Pair Completeness Validation Script

**Script:** `scripts/validate_pair_completeness.py`

This script is the primary gate for dashboard completeness. It must pass before any pair is accepted.

```bash
# Validate a single pair
python scripts/validate_pair_completeness.py --pair hy_ig_spy

# Validate all registered pairs
python scripts/validate_pair_completeness.py --all

# Machine-readable output (for CI or Quincy logging)
python scripts/validate_pair_completeness.py --pair hy_ig_spy --json
```

**Exit codes:** `0` = all PASS, `1` = any FAIL, `2` = invocation error.

**What it checks:**

| Group | Checks |
|---|---|
| Artifacts — Results | All mandatory `results/{pair_id}/` files exist; `evidence_status.json` schema-valid and `passed_final_exam` |
| Artifacts — Charts | All 9 mandatory chart JSONs + perceptual PNGs exist |
| Story — Crisis Episode Zooms | All 4 canonical episode chart artifacts + perceptual PNGs; all 4 slugs declared in config with title/narrative/caption |
| Story — Config | All 9 mandatory `StoryConfig` attributes present and non-empty |
| Strategy — Config | All 6 mandatory `StrategyConfig` attributes present and non-empty |
| Evidence — Method Blocks | Level 1 ≥ 3 blocks, Level 2 ≥ 2 blocks; all 7 mandatory fields per block; chart artifacts present |
| Methodology — Config | All 5 mandatory `MethodologyConfig` fields present and non-empty |
| Glossary Coverage | WARN (not FAIL) for technical terms missing from `portal_glossary.json` |

**Gate protocol:**

1. **Ace** runs `--pair {pair_id}` before META-SRV handoff. Must show `Overall: [PASS]` (zero FAILs). WARNs must be acknowledged in the handoff note with a resolution plan or accepted justification.
2. **Quincy** runs `--pair {pair_id}` independently as part of GATE-31. Any FAIL found by Quincy that was not in Ace's report is a META-SRV violation — Ace's self-verification is incomplete.
3. **Lead** may run `--all` during META-CDR to get a cross-pair view.

**Updating the script:** when `dashboard-page-standard.md` adds or changes a mandatory requirement, `validate_pair_completeness.py` must be updated in the same commit. The two are co-owned — a standard change without a script update is incomplete.

---

## Versioning

Changes to this document require:
1. Version bump in the header
2. Entry in `docs/sop-changelog.md`
3. Update to `_validate_config()` in `page_templates.py` to enforce new requirements
4. Cross-reference update in `docs/agent-sops/appdev-agent-sop.md`

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-05-12 | Initial version — all sections mandatory, DPS-EP1 (4 canonical episodes), DPS-II1 (info icons) |
