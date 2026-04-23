# Ace Discovery — Wave 10I Legacy-Page Migration

**Author:** Dev Ace (appdev-ace)
**Date:** 2026-04-23
**Wave:** 10I (opener) — scoping only, no implementation
**Template reference:** `results/_cross_agent/ace_discovery_trade_log_20260423.md` (Wave 10H.2)
**Governing rules:** APP-PT1 (template abstraction), APP-TL1 (trade-log contract), APP-PR1 (path-resolution discipline, Wave 10I)

---

## 0. Executive Summary

- **24 page files** under `app/pages/` in scope across 7 pair surfaces (plus a 3-in-1 TED variants composite).
- **2 thin wrappers complete** (`indpro_xlp`, `hy_ig_spy` — 8 files × ~17 lines).
- **15 hand-written pages + 1 hybrid page** still bypass the template (Sample pair + 5 legacy pair surfaces + TED composite).
- **2 pair configs absent**: `umcsent_xlv_config.py`, `hy_ig_v2_spy_config.py`. The 5 legacy pair_ids under the TED composite (`sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`) have no per-pair pages at all — a separate decision is needed: either create 3 × 4 thin wrappers or retain the composite page as an intentional exception.
- **Template gaps for Sample:** zero. Every component Sample uses (probability engine, position adjustment, trigger cards, live execution, signal universe, analyst suggestions, APP-TL1 trade log) is already wired into `page_templates.py`. The abstraction contract is ready for Sample content to move into a config.
- **Template gaps for umcsent_xlv:** one data-dependent gap (broker-style CSV, tracked under Wave 10H.2 `BL-APP-PT1-UMCSENT`), plus a narrative anchor (`TRADE_LOG_EXAMPLE_MD`) to be authored. No template code change required.
- **APP-PR1 compliance in legacy pages:** no prohibited **bare-relative** reads (`open("results/...")`) found. All 16 non-thin pages use either the older `os.path.join(os.path.dirname(__file__), "..", ...)` idiom (functional but non-canonical) or the canonical `_REPO_ROOT = Path(__file__).resolve().parents[2]` idiom (umcsent_xlv + Sample already). Migration makes the point moot by deleting all direct I/O from page files.
- **Recommended phasing: two waves.** Wave 10I.A = non-Sample legacy (5 pair surfaces, config-heavy, no template changes). Wave 10I.B = Sample migration (content-port + APP-TL1 example content; parallel to the Sample legacy-page decommission decision). A three-wave split is not warranted — no template extensions are required for the 4 page types.
- **Ballpark budget:** ~10 agent-waves across Ace, Ray, Dana, Evan, Quincy. Wave 10I.A ≈ 7 waves; Wave 10I.B ≈ 3 waves.

---

## 1. Inventory Matrix

Classification definitions
- **THIN** — imports `render_*_page`; ≤ ~30 lines; zero non-delegated `st.*` calls.
- **HYBRID** — thin wrapper but with additional direct `st.*` calls in the page file (e.g. the Wave 10H.1 defensive `_render_exploratory_insights` patch on Sample Methodology).
- **HAND** — fully hand-written: direct `st.*` calls, inline data loading, inline prose.

Line counts are from `wc -l`. `st.*` call counts are grep `^\s*st\.`.

| Pair / Surface         | Story        | Evidence     | Strategy     | Methodology  | Notes |
|------------------------|--------------|--------------|--------------|--------------|-------|
| `indpro_xlp`           | THIN (18)    | THIN (17)    | THIN (17)    | THIN (17)    | ✅ fully migrated; reference green path |
| `hy_ig_spy`            | THIN (18)    | THIN (17)    | THIN (17)    | THIN (17)    | ✅ fully migrated (Wave 10H.2); APP-TL1 retro-applied |
| `hy_ig_v2_spy` (Sample)| HAND (502, 48) | HAND (1037, 30) | HAND (964, 115) | HYBRID (442, 69, 1 render call) | Reference implementation; APP-TL1 **not** applicable (legacy); Methodology carries Wave 10H.1 patch |
| `indpro_spy`           | HAND (146, 18) | HAND (183, 23) | HAND (213, 27) | HAND (150, 32) | Pair #1 legacy |
| `permit_spy`           | HAND (152, 18) | HAND (120, 16) | HAND (218, 26) | HAND (177, 32) | Pair #3 legacy |
| `vix_vix3m_spy`        | HAND (165, 18) | HAND (126, 16) | HAND (223, 26) | HAND (186, 33) | Pair #11 legacy |
| `umcsent_xlv`          | HAND (304, 32) | HAND (447, 30) | HAND (473, 70) | HAND (339, 54) | Richest hand-written; rich trade log already present → APP-TL1 anchor lives on the page itself |
| TED variants composite | HAND (105, 15) | HAND (50, 13) | HAND (155, 18) | HAND (148, 31) | **One file serves 3 pair_ids** (`sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`) via `st.tabs`/loop; architectural exception — see §3.4 |

**Totals.**

- Thin wrappers: **8** (2 pairs × 4 pages). Covered.
- Hybrid: **1** (Sample Methodology).
- Hand-written legacy: **15 per-pair pages** + **4 TED composite pages** = **19 files, 5,829 lines** still to migrate.
- Migration surface by pair:
  - Sample: 2,945 lines across 4 files
  - umcsent_xlv: 1,563 lines across 4 files
  - vix_vix3m_spy: 700 lines
  - indpro_spy: 692 lines
  - permit_spy: 667 lines
  - TED composite: 458 lines (but spans 3 pair_ids — see §3.4)

---

## 2. Per-Page Migration-Effort Estimates

Severity heuristics used below
- **A (trivial)** — narrative-only port: prose → config string constant; zero custom widgets.
- **B (standard)** — narrative + 1–2 pair-specific chart references; pair config creation is the dominant work.
- **C (rich)** — multiple pair-specific charts and/or inline data loading; needs careful config surface to preserve current content.
- **D (reference-defining)** — Sample-scale; content defines the canon, and migrating it validates the template abstraction.

### 2.1 indpro_spy (legacy Pair #1)

| Page | Severity | Lines | Narrative blocks | Unique content | Pair-config attrs needed |
|------|----------|-------|------------------|----------------|--------------------------|
| Story | B | 146 | plain-English, thesis, 2 narrative sections, hero+regime chart refs | mild: counter-cyclical z-score framing | all StoryConfig defaults fit |
| Evidence | B | 183 | method blocks for Correlation, Granger, CCF, HMM, Regime-Quartile, Transfer-Entropy, LocalProj, Quantile | rich (all 8 method blocks) | EVIDENCE_METHOD_BLOCKS mirror of hy_ig_spy_config.py |
| Strategy | B | 213 | how-signal, KPI cards, tournament spotlight | no Sample-grade tabs (no probability engine / live execution) | StrategyConfig defaults; `TRADE_LOG_EXAMPLE_MD` |
| Methodology | B | 150 | data sources, indicator construction, methods table, references | mild | MethodologyConfig mirror |

Pair-config file to create: `app/pair_configs/indpro_spy_config.py` (~500 lines, ~80% copy-morph from `hy_ig_spy_config.py`).

### 2.2 permit_spy (legacy Pair #3)

Same shape as indpro_spy. Severity B across all 4 pages. Pair config to create: `app/pair_configs/permit_spy_config.py`. Estimated 500 lines.

### 2.3 vix_vix3m_spy (legacy Pair #11)

Same shape. Severity B across all 4 pages. The pair has the strongest regime discrimination (VIX quartile Q1 vs Q4 Sharpe spread = 9 points) — narrative is punchier but the structural port is the same. Pair config to create: `app/pair_configs/vix_vix3m_spy_config.py`. Estimated 500 lines.

### 2.4 TED variants composite (sofr_ted_spy / dff_ted_spy / ted_spliced_spy)

**Architectural decision required.** The 4 TED pages each multiplex 3 pair_ids via `st.tabs` or a for-loop. Example from `6_ted_variants_story.py`:

```python
tabs = st.tabs(["A: SOFR-DTB3", "B: DFF-DTB3 (Fed Funds)", "C: Spliced TED"])
# ...
for i, (pid, label) in enumerate([
    ("sofr_ted_spy", "SOFR-TED"),
    ("dff_ted_spy", "DFF-TED"),
    ("ted_spliced_spy", "TED-Spliced"),
]):
```

This breaks the one-pair-per-page assumption in `render_*_page(pair_id, ...)`. Two options:

- **(a) Explode to 12 pages.** 3 pair_ids × 4 pages = 12 thin wrappers, 3 pair configs. Portal nav grows (sidebar pair selector already supports this via `pair_registry.py`). Retires the composite.
- **(b) Preserve composite as documented exception.** Keep the 4 composite pages, but migrate their inner per-pair rendering to call `render_*_page(pid, config)` inside each tab. This requires `render_*_page` to be **idempotent and tab-safe** (skip the `st.set_page_config` call if already set). Currently the template's step-1 would raise `StreamlitAPIException` on the second tab.

Recommend **option (a)**: cleaner, matches the 1 pair = 1 card = 4 pages model used by the landing-page registry, and avoids adding a "tab-safe" mode to the template. Cost: 3 new pair configs, 12 new thin-wrapper files, deletion of the 4 composite files. Total lines removed: 458. Total lines added: ~180 (wrappers) + ~1,500 (configs). **Severity B × 12**, but configs can be produced in parallel.

### 2.5 umcsent_xlv (legacy Pair)

Severity **C** on all 4 pages — this is the richest hand-written pair. Already has a rich trade-log section on the Strategy page (which is why `BL-APP-PT1-UMCSENT` has been open): the current legacy page already satisfies the APP-TL1 narrative contract, but the template-migrated version loses content unless we carry it into the config.

| Page | Severity | Lines | Key challenges |
|------|----------|-------|----------------|
| Story | C | 304 | Longest Story narrative in the portal; needs careful section-boundary mapping to StoryConfig |
| Evidence | C | 447 | All 8 method blocks — mirror of Sample evidence shape |
| Strategy | C | 473 | `TRADE_LOG_EXAMPLE_MD` authoring required (APP-TL1 anchor); broker-style CSV backfill required (Evan; data prerequisite from Wave 10H.2) |
| Methodology | C | 339 | Rich XLV target construction prose; interpretation_metadata references |

Pair config to create: `app/pair_configs/umcsent_xlv_config.py` (estimated ~800 lines — the largest pair config to date).

APP-PR1 note: file already uses `_REPO_ROOT = Path(__file__).resolve().parents[2]` — already canonical.

### 2.6 hy_ig_v2_spy (Sample)

Severity **D** — reference-defining migration. This is the quality benchmark and the `sample-v1.0` git tag is pinned here. Migrating Sample means promoting the *reference content* into `hy_ig_v2_spy_config.py` and making every current template-based pair one `st` call away from Sample quality.

| Page | Severity | Lines | Unique content | Risk |
|------|----------|-------|----------------|------|
| Story | D | 502 | 4 hand-annotated episode narratives (Dot-Com, GFC, COVID, 2022); "where the signal struggled" caveat; deepest prose | Content density — narrative fidelity must survive the port |
| Evidence | D | 1037 | Inline `render_method_block(content: dict)` helper (already mirrors the template's internal `_render_method_block`) — check for divergence; 8 method blocks at max granularity | Any drift between Sample's local `render_method_block` and the template's must be reconciled before migration |
| Strategy | D | 964 | Uses **all** 4 optional rich components (probability engine, position adjustment, trigger cards, live execution) + APP-TL1 preview | Template already supports all of these (verified §4); risk is config-surface completeness, not template code |
| Methodology | D | 442 (HYBRID — 1 render call) | Direct `_render_exploratory_insights` import (Wave 10H.1 defensive patch) | After migration, the defensive patch is redundant and should be removed |

Sample's `hy_ig_v2_spy_config.py` is the **reference pair config** — it should be the cleanest, most complete config in the repo. Once written, every future pair can be produced by copy-morph.

### 2.7 APP-PR1 Compliance Audit (all 16 files)

| File | Path idiom | Status |
|------|-----------|--------|
| 5_indpro_spy_* (4 files) | `os.path.join(os.path.dirname(__file__), "..", ...)` | non-canonical; functional |
| 6_ted_variants_* (4 files) | `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` + `os.path.join(BASE, "results", ...)` | non-canonical; functional |
| 7_permit_spy_* (4 files) | same as indpro_spy | non-canonical; functional |
| 8_vix_vix3m_spy_* (4 files) | same as indpro_spy | non-canonical; functional |
| 9_hy_ig_v2_spy_* (4 files) | `_REPO_ROOT = Path(__file__).resolve().parents[2]` | **canonical** (APP-PR1 compliant) |
| 10_umcsent_xlv_* (4 files) | `_REPO_ROOT = Path(__file__).resolve().parents[2]` | **canonical** (APP-PR1 compliant) |

**Zero** bare-relative reads (`open("results/...")`, `pd.read_csv("results/...")`, `Path("results/...")`) found anywhere in `app/pages/`. The prophylactic intent of APP-PR1 holds: **no SEV1 silent-skip regressions to fix**. Migration removes direct I/O from page files entirely, so the idiom-drift in 16 files becomes moot by deletion.

**Flag for Lead:** if APP-PR1 enforcement adds a grep CI check, consider expanding the forbidden pattern list to also flag `os.path.join(os.path.dirname(__file__), "..", ...)` for **resolved artifacts** (results/output paths), since it has the same parent-depth-guess fragility that motivated APP-PR1. CSS / assets are a different class (app-internal, sibling directory) and can stay. This is an observation only — rule proposals are Lead's step.

---

## 3. Dependency Graph

### 3.1 Pair configs to create (prerequisites)

| Config file | For | Size estimate | Depends on |
|-------------|-----|---------------|------------|
| `indpro_spy_config.py` | indpro_spy 4 pages | 500 lines | copy-morph from hy_ig_spy_config.py |
| `permit_spy_config.py` | permit_spy 4 pages | 500 lines | copy-morph from hy_ig_spy_config.py |
| `vix_vix3m_spy_config.py` | vix_vix3m_spy 4 pages | 500 lines | copy-morph from hy_ig_spy_config.py |
| `sofr_ted_spy_config.py` | sofr_ted_spy 4 pages | 400 lines | narrative fork of TED composite; coordinate with Ray |
| `dff_ted_spy_config.py` | dff_ted_spy 4 pages | 400 lines | narrative fork of TED composite; coordinate with Ray |
| `ted_spliced_spy_config.py` | ted_spliced_spy 4 pages | 400 lines | narrative fork of TED composite; coordinate with Ray |
| `umcsent_xlv_config.py` | umcsent_xlv 4 pages | 800 lines | Ray authors `TRADE_LOG_EXAMPLE_MD`; Evan produces broker-style CSV (open from Wave 10H.2 `BL-APP-PT1-UMCSENT`) |
| `hy_ig_v2_spy_config.py` | Sample 4 pages | 1,000 lines | Ray authors (or extracts from current hand-written prose); Ace structurally ports |

Total new configs: **8 files, ~4,500 lines**. Plus 8 new thin wrappers per config = **32 wrappers × ~17 lines = 544 lines**.

### 3.2 Template extensions

**Zero required.** Full audit of `page_templates.py` confirms all Sample-exclusive components are already imported and invoked inside `render_strategy_page` and `render_methodology_page`:

- `render_probability_engine_panel` — template line 1130
- `render_position_adjustment_panel` — template line 1133
- `render_instructional_trigger_cards` — template line 1136
- `render_live_execution_placeholder` — template line 1232
- `render_signal_universe` — template line 1601
- `render_analyst_suggestions` — template line 1642
- APP-TL1 `_render_trade_log_block` — shipped Wave 10H.2

The template abstraction contract is **ready**. This is the single biggest finding of the discovery: the migration is config-and-content work, not template work.

### 3.3 Data prerequisites

| Pair | Prerequisite | Owner | Status |
|------|--------------|-------|--------|
| umcsent_xlv | broker-style `winner_trades_broker_style.csv` | Evan | open from Wave 10H.2 `BL-APP-PT1-UMCSENT` |
| umcsent_xlv | `TRADE_LOG_EXAMPLE_MD` narrative | Ray | not yet authored |
| indpro_spy, permit_spy, vix_vix3m_spy | `TRADE_LOG_EXAMPLE_MD` narratives | Ray | not yet authored (3 needed) |
| TED variants (3 pair_ids) | pair-specific narratives (if exploding composite) | Ray | not yet authored (3 needed) |
| hy_ig_v2_spy (Sample) | `TRADE_LOG_EXAMPLE_MD` narrative (note: Sample legacy page retains its rich example; porting it is content-extraction, not authoring) | Ray | extract from current page |

### 3.4 TED composite architectural decision

**Gate before Wave 10I.A scoping is finalized.** Lead needs to pick option (a) explode or (b) preserve composite. My recommendation is (a). If (b) is chosen, template extension is required (tab-safe mode in `_apply_page_config`) — that would force the three-wave split.

---

## 4. Sample-Gap Analysis

Scope: what does `hy_ig_v2_spy` currently render that the template does not yet support?

| Feature | Sample uses? | Template supports? | Gap |
|---------|--------------|--------------------|-----|
| Plain English expander | Yes | Yes (StoryConfig, StrategyConfig, MethodologyConfig) | none |
| One-sentence thesis | Yes | Yes (StoryConfig.ONE_SENTENCE_THESIS) | none |
| 5-column KPI cards (winner_summary.json) | Yes | Yes (step 6) | none |
| Where-this-fits (interpretation_metadata.mechanism) | Yes | Yes (step 7) | none |
| Hero chart + regime chart | Yes | Yes (HERO_CHART_NAME, REGIME_CHART_NAME) | none |
| 8 evidence method blocks (Correlation, Granger, CCF, HMM, Regime-Quartile, Transfer-Entropy, LocalProj, Quantile) | Yes | Yes (Level 1 / Level 2 tabs in render_evidence_page) | none |
| Strategy tab: Execute/Performance/Confidence | Yes | Yes (render_strategy_page tabs) | none |
| Probability engine panel | Yes | Yes (line 1130) | none |
| Position adjustment panel | Yes | Yes (line 1133) | none |
| Instructional trigger cards | Yes | Yes (line 1136) | none |
| Live execution placeholder | Yes | Yes (line 1232) | none |
| APP-TL1 trade log block (dual download, glossary, preview) | Yes (hand-rolled original — predates APP-TL1) | Yes (post Wave 10H.2) | none — but content to port |
| Signal Universe table | Yes | Yes (line 1601) | none |
| Analyst Suggestions table | Yes | Yes (line 1642) | none |
| Exploratory insights (APP-PT2) | Yes (Wave 10H.1 defensive patch) | Yes (template proper) | patch becomes redundant — removed on migration |
| 4 episode narratives (Dot-Com / GFC / COVID / 2022) in Story | Yes | Not as a distinct StoryConfig field; current StoryConfig has `NARRATIVE_SECTION_1`, `NARRATIVE_SECTION_2` | **Minor gap — resolvable by content concatenation**. Either put all 4 episodes into `NARRATIVE_SECTION_2` as a markdown block, or extend StoryConfig with an optional `EPISODES_MD` field. The latter is cleaner and backward-compatible (all other pairs can leave it unset). **Not a blocker**; content-concatenation works today. |
| Evidence Tournament section ("The Combinatorial Tournament") | Yes | Template renders this as part of Methodology/Strategy, not Evidence footer | **Check before porting** — Sample's Evidence ends with a tournament section; template ships tournament framing on Methodology. Could be content-concat into final Evidence block, or treat as a standard template section. **Minor.** |

**Verdict:** no template code change is required to migrate Sample. One optional StoryConfig field (`EPISODES_MD`) would be nice-to-have but is not blocking. The abstraction contract is complete.

---

## 5. Recommended Phasing

### Option A — **Two waves** (recommended)

**Wave 10I.A — non-Sample legacy migration**

- Scope: 5 pair surfaces (indpro_spy, permit_spy, vix_vix3m_spy, umcsent_xlv, TED-exploded × 3) = 8 pair configs + 32 thin wrappers + 4 composite deletions.
- No template code changes.
- Parallelization (see §6): 5 pair configs can run in parallel (one per pair); serialize on Ray narrative authorship where content is thin.
- Ends with a QA gate: 17/17 PASS (current gate) + 12 new pair/page smoke rows.

**Wave 10I.B — Sample migration**

- Scope: `hy_ig_v2_spy` — author `hy_ig_v2_spy_config.py`, flip all 4 pages to thin wrappers, remove Wave 10H.1 defensive patch.
- Optional template extension: `StoryConfig.EPISODES_MD` if the content-concat approach is rejected.
- Sibling: Sample legacy-page decommission decision (BL-APP-PT1-LEGACY parent item).
- Ends with a QA gate: Sample still passes `sample-v1.0` visual smoke parity; all prose preserved.

**Why not three waves?**

- The only thing that would justify a third template-extension wave is the `StoryConfig.EPISODES_MD` field or the TED composite "tab-safe" mode. Both have content-concatenation fallbacks. The template is ready as-is.
- Keeping Wave 10I.A and Wave 10I.B distinct is important for risk isolation: Sample is reference-defining and deserves its own dispatch cycle with sample-v1.0 regression comparison.

### Option B — **One wave** (not recommended)

All 8 pair configs + 32 thin wrappers + Sample port in one wave. Risk: Sample-scale content port + 5 parallel legacy ports concurrent. If Sample content fidelity issues surface mid-wave, they block the whole wave's QA gate. Two-wave sequencing de-risks this.

### Option C — **Three waves**

Add a Wave 10I.0 "template extensions" gate before 10I.A. Only needed if Lead chooses TED option (b) (preserve composite — requires tab-safe mode) OR mandates `EPISODES_MD` before Sample. Otherwise redundant.

---

## 6. Parallelization Plan

### Wave 10I.A parallel lanes

- **Lane 1 (Ace, 2 waves):** `indpro_spy_config.py` — copy-morph from `hy_ig_spy_config.py`; swap pair_id, indicator names, narrative defaults.
- **Lane 2 (Ace, 2 waves):** `permit_spy_config.py` — same pattern.
- **Lane 3 (Ace, 2 waves):** `vix_vix3m_spy_config.py` — same pattern.
- **Lane 4 (Ace + Ray + Evan, 3 waves):** `umcsent_xlv_config.py` — must serialize behind Ray's `TRADE_LOG_EXAMPLE_MD` and Evan's broker-style CSV backfill (BL-APP-PT1-UMCSENT).
- **Lane 5 (Ace + Ray, 2 waves):** TED-exploded — 3 pair configs + 12 thin wrappers + delete composite. Requires Ray to author (or fork) 3 narratives. Can run concurrent with Lanes 1–3.

Thin-wrapper creation (once each pair config exists) is mechanical; Ace can batch all wrappers in one commit per lane.

QA (Quincy, 1 wave): one `cloud_verify.py` run covering the expanded pair set. Current 17/17 gate extends to ~29/29 (17 existing + 12 new).

**Wave 10I.A estimated total:** 2 + 2 + 2 + 3 + 2 + 1 = **12 agent-waves, 7 in the critical path** (Lane 4 umcsent_xlv is the long pole).

### Wave 10I.B parallel lanes

- **Lane 6 (Ace, 2 waves):** `hy_ig_v2_spy_config.py` — structural port + content extraction.
- **Lane 7 (Ray, 1 wave):** review ported narrative for fidelity vs. sample-v1.0 tag; flag any content regressions.
- **Lane 8 (Quincy, 1 wave):** regression parity against sample-v1.0; Sample is the gold-standard visual smoke.

**Wave 10I.B estimated total:** 2 + 1 + 1 = **4 agent-waves, 3 in the critical path**.

---

## 7. Total Cost Estimate

| Agent | Wave 10I.A waves | Wave 10I.B waves | Total |
|-------|------------------|------------------|-------|
| Ace (Dev) | 6 (config + wrapper lanes) | 2 (Sample port) | 8 |
| Ray (Research) | 2 (umcsent TRADE_LOG example + TED narratives + misc `TRADE_LOG_EXAMPLE_MD` for indpro/permit/vix) | 1 (Sample fidelity review) | 3 |
| Evan (Econometrics) | 1 (umcsent broker CSV — from `BL-APP-PT1-UMCSENT`) | 0 | 1 |
| Dana (Data) | 0 | 0 | 0 |
| Quincy (QA) | 1 (cloud verify expanded) | 1 (Sample regression parity) | 2 |
| **Total** | **10** | **4** | **14 agent-waves** |

Lead commit touches (per LEAD-DL1): zero code; only `docs/sop-changelog.md`, `docs/standards.md`, and wave dispatches. One potential exception: if Option (b) is chosen for TED composite, template extension lands in Wave 10I.0 under Ace.

**Token-budget prior (from `docs/pair_execution_history.md`):** ~150K per recurring pair. Migration is lighter than a new-pair pipeline (no econometrics, no visualization generation, no data pull) — estimate **40K–60K per pair config + wrapper set**. Total wave budget: **~350K–500K tokens for Wave 10I.A, ~150K–200K for Wave 10I.B**.

---

## 8. Findings & Flags for Lead

### Green lights

1. **Template is ready.** Zero code changes required to `page_templates.py` for Sample migration. Every Sample-exclusive component is wired.
2. **APP-PR1 regression risk is zero.** No bare-relative `results/` reads anywhere in `app/pages/`. Migration removes the idiom entirely; the 16 non-canonical `os.path.join(dirname, "..", ...)` paths all go away.
3. **Copy-morph is viable** for indpro_spy, permit_spy, vix_vix3m_spy. Lanes 1–3 should run smoothly in parallel.

### Amber flags

4. **TED composite architectural decision is a prerequisite to Wave 10I.A scoping.** Lead must pick explode vs. preserve before Ray and Ace start Lane 5.
5. **umcsent_xlv is the long pole** (Lane 4, 3 waves serial on Ray + Evan + Ace). Start it first.
6. **Sample migration risk** is content fidelity, not template capability. Sample-v1.0 visual smoke comparison must be the Wave 10I.B gate.

### Red flags

None. No template-blocking gap, no data-blocking gap other than the one already tracked under `BL-APP-PT1-UMCSENT`.

### Observation for Lead consideration (not a rule proposal)

If APP-PR1 enforcement is operationalized as a CI grep, expanding it to flag `os.path.join(os.path.dirname(__file__), "..", ...)` for `results/` and `output/` paths (not assets/CSS) would catch the same failure class as APP-PR1 in the 16 non-canonical legacy files before they're migrated. This is informational only — rule proposals remain Lead's step per LEAD-DL1.

---

## Appendix A. File-level inventory snapshot

```
app/pages/
  5_indpro_spy_story.py          146L  HAND
  5_indpro_spy_evidence.py       183L  HAND
  5_indpro_spy_strategy.py       213L  HAND
  5_indpro_spy_methodology.py    150L  HAND
  6_ted_variants_story.py        105L  HAND (composite × 3 pair_ids)
  6_ted_variants_evidence.py      50L  HAND (composite × 3 pair_ids)
  6_ted_variants_strategy.py     155L  HAND (composite × 3 pair_ids)
  6_ted_variants_methodology.py  148L  HAND (composite × 3 pair_ids)
  7_permit_spy_story.py          152L  HAND
  7_permit_spy_evidence.py       120L  HAND
  7_permit_spy_strategy.py       218L  HAND
  7_permit_spy_methodology.py    177L  HAND
  8_vix_vix3m_spy_story.py       165L  HAND
  8_vix_vix3m_spy_evidence.py    126L  HAND
  8_vix_vix3m_spy_strategy.py    223L  HAND
  8_vix_vix3m_spy_methodology.py 186L  HAND
  9_hy_ig_v2_spy_story.py        502L  HAND  (Sample)
  9_hy_ig_v2_spy_evidence.py    1037L  HAND  (Sample)
  9_hy_ig_v2_spy_strategy.py     964L  HAND  (Sample)
  9_hy_ig_v2_spy_methodology.py  442L  HYBRID (Sample — 1 direct render call)
  10_umcsent_xlv_story.py        304L  HAND
  10_umcsent_xlv_evidence.py     447L  HAND
  10_umcsent_xlv_strategy.py     473L  HAND
  10_umcsent_xlv_methodology.py  339L  HAND
  14_indpro_xlp_story.py          18L  THIN  ✓
  14_indpro_xlp_evidence.py       17L  THIN  ✓
  14_indpro_xlp_strategy.py       17L  THIN  ✓
  14_indpro_xlp_methodology.py    17L  THIN  ✓
  15_hy_ig_spy_story.py           18L  THIN  ✓
  15_hy_ig_spy_evidence.py        17L  THIN  ✓
  15_hy_ig_spy_strategy.py        17L  THIN  ✓
  15_hy_ig_spy_methodology.py     17L  THIN  ✓

app/pair_configs/
  hy_ig_spy_config.py            940L
  indpro_xlp_config.py           631L

TO CREATE (Wave 10I.A):
  indpro_spy_config.py           ~500L
  permit_spy_config.py           ~500L
  vix_vix3m_spy_config.py        ~500L
  sofr_ted_spy_config.py         ~400L   (if TED exploded)
  dff_ted_spy_config.py          ~400L   (if TED exploded)
  ted_spliced_spy_config.py      ~400L   (if TED exploded)
  umcsent_xlv_config.py          ~800L

TO CREATE (Wave 10I.B):
  hy_ig_v2_spy_config.py        ~1000L
```

---

**End of discovery report.**
