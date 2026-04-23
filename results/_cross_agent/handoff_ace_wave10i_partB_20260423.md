# Handoff — Ace → Ray (Wave 10I.A Part 2: TED composite explode)

**Author:** Dev Ace (appdev-ace)
**Date:** 2026-04-23
**Wave:** 10I.A Part 2
**Governing rules:** APP-PT1 (template abstraction), APP-RL1 (page-routing single-source), APP-PR1 (path resolution)
**Scope:** Explode the 3-in-1 TED composite (`6_ted_variants_*.py`) into 3 separate one-pair-per-page surfaces for `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`. Lead decision: explode (not preserve).

---

## Summary

- **3 pair configs created** (880 lines total, 111 TODO-Ray stubs).
- **12 thin wrappers created** (22 lines each, 264 lines total).
- **4 composite pages deleted** (`6_ted_variants_{story,evidence,strategy,methodology}.py`, 458 lines).
- **Routing updates:** `pair_registry.PAGE_ROUTING` absorbs all 3 TED pair_ids and drops the `_TED_VARIANTS` composite branch. `sidebar.FINDINGS` replaces the single composite entry with 3 separate entries.
- **Smoke:** all 3 pairs pass `smoke_loader.py` with `failures=0`.
- **Landing-page verification:** `load_pair_registry()` now surfaces all 3 TED variants as separate pair cards routed to the new pages.

## Pair_id → page_file mappings (final)

| pair_id | prefix | Story | Evidence | Strategy | Methodology |
|---|---|---|---|---|---|
| `sofr_ted_spy` | `6` | `app/pages/6_sofr_ted_spy_story.py` | `6_sofr_ted_spy_evidence.py` | `6_sofr_ted_spy_strategy.py` | `6_sofr_ted_spy_methodology.py` |
| `dff_ted_spy` | `11` | `app/pages/11_dff_ted_spy_story.py` | `11_dff_ted_spy_evidence.py` | `11_dff_ted_spy_strategy.py` | `11_dff_ted_spy_methodology.py` |
| `ted_spliced_spy` | `12` | `app/pages/12_ted_spliced_spy_story.py` | `12_ted_spliced_spy_evidence.py` | `12_ted_spliced_spy_strategy.py` | `12_ted_spliced_spy_methodology.py` |

Numeric prefixes picked to preserve the Part-1 registry convention (sofr keeps `6` — the legacy composite slot; `dff` and `spliced` take unused prefixes `11` and `12`; `13` skipped to avoid superstition-triggered reshuffles later; `14` / `15` already in use for `indpro_xlp` / `hy_ig_spy`).

## Per-config line count + TODO-Ray stubs

| File | Lines | TODO-Ray stubs |
|---|---:|---:|
| `app/pair_configs/sofr_ted_spy_config.py` | 291 | 37 |
| `app/pair_configs/dff_ted_spy_config.py` | 293 | 37 |
| `app/pair_configs/ted_spliced_spy_config.py` | 296 | 37 |
| **Total** | **880** | **111** |

All 3 configs follow the 2-evidence-block pattern (Correlation + Local Projections) matching the legacy composite's on-disk chart set (5 charts per pair: hero, regime_stats, correlations, local_projections, tournament_scatter).

## Extracted-from-composite content map (per pair)

Each pair config stubs source-line hints pointing back to the deleted composite. Because the composite is deleted, Ray should retrieve the prose via:

```bash
git show HEAD~1:app/pages/6_ted_variants_story.py
git show HEAD~1:app/pages/6_ted_variants_evidence.py
git show HEAD~1:app/pages/6_ted_variants_strategy.py
git show HEAD~1:app/pages/6_ted_variants_methodology.py
```

Where HEAD~1 = commit prior to the Part-2 explode commit.

**Composite → per-pair narrative mapping** (Ray should distribute prose pair-specifically, not replicate verbatim):

| Composite content | Distribution |
|---|---|
| `story.py` lines 36-46 (What Is the TED Spread, LIBOR↔SOFR distinction) | all 3 pairs share background in `NARRATIVE_SECTION_1` |
| `story.py` lines 49-51 (Variant A SOFR-DTB3 description) | `sofr_ted_spy` only — lives in `PLAIN_ENGLISH` |
| `story.py` lines 52-53 (Variant B DFF-DTB3 description) | `dff_ted_spy` only |
| `story.py` lines 55-56 (Variant C Spliced TED description) | `ted_spliced_spy` only |
| `story.py` lines 67-77 (hero tab captions) | per-pair `HERO_CAPTION` (one caption per pair) |
| `story.py` lines 83-93 (regime quartile framing) | per-pair `REGIME_CAPTION` |
| `story.py` lines 99-101 (transition text) | identical template; per-pair `TRANSITION_TEXT` |
| `evidence.py` lines 31-37 (correlation tab) | per-pair `CORRELATION_BLOCK.chart_caption` |
| `evidence.py` lines 39-45 (local projections tab) | per-pair `LOCAL_PROJECTIONS_BLOCK.chart_caption` |
| `strategy.py` (per-pair tournament loop, winner spotlight) | each pair now has its own `STRATEGY_CONFIG.SIGNAL_RULE_MD`; canonical winner lives in `results/{pair_id}/winner_summary.json` — Ray should read that file for the actual numeric winner params |
| `strategy.py` lines 146-152 (cross-variant caveats) | split into per-pair `CAVEATS_MD` (Variant A: 3yr OOS; Variant B: conservative; Variant C: splice assumption) |
| `methodology.py` (splice problem, variant definitions, stationarity, methods, tournament design, references) | each pair config carries its own in-place `_DATA_SOURCES_MD`, `_METHODS_TABLE_MD`, `_TOURNAMENT_DESIGN_MD`, `_REFERENCES_MD` (Ace authored); `_INDICATOR_CONSTRUCTION_MD` stubbed for Ray |

## Routing / navigation updates (Ace-owned, not Ray)

1. **`app/components/pair_registry.py`** — `_TED_VARIANTS` set and the special-case branch in `get_page_prefix` removed; all 3 TED pair_ids added to `PAGE_ROUTING` dict. Landing-page cards now route pair-specifically (previously all 3 routed to the composite slot `pages/6_ted_variants`).
2. **`app/components/sidebar.py`** — Single `ted_variants` FINDING entry replaced with 3 separate entries (SOFR-TED, DFF-TED, Spliced TED) so the finding-selector dropdown matches the exploded surfaces.

These two updates are navigation plumbing (APP-RL1 single-source-of-truth), not narrative content. Ray does **not** touch them.

## Composite pages deleted

```
app/pages/6_ted_variants_story.py         (105 lines)
app/pages/6_ted_variants_evidence.py      ( 50 lines)
app/pages/6_ted_variants_strategy.py      (155 lines)
app/pages/6_ted_variants_methodology.py   (148 lines)
---------------------------------------------------
TOTAL                                      (458 lines deleted)
```

Grep confirms no remaining code references to the deleted filenames (only TODO-Ray stub comments cite the old paths as "port from" source markers — intentional, they tell Ray where to retrieve prose via `git show HEAD~1:…`).

## Smoke test results

All runs `failures=0`:

| Pair | passes | failures | Log file |
|---|---:|---:|---|
| `sofr_ted_spy`   | 3 | 0 | `app/_smoke_tests/loader_sofr_ted_spy_20260423.log` |
| `dff_ted_spy`    | 3 | 0 | `app/_smoke_tests/loader_dff_ted_spy_20260423.log` |
| `ted_spliced_spy`| 3 | 0 | `app/_smoke_tests/loader_ted_spliced_spy_20260423.log` |

AST smoke covers `HERO_CHART_NAME`, `REGIME_CHART_NAME`, and `TOURNAMENT_SCATTER_CHART_NAME`. Evidence method-block chart names (`{pid}_correlations`, `{pid}_local_projections`) are dict literals — not AST-covered (pre-existing smoke-test limitation, consistent with Part-1 pairs).

## Landing-page registry check

Confirmed via `load_pair_registry()`:

```
sofr_ted_spy    -> pages/6_sofr_ted_spy_story.py
dff_ted_spy     -> pages/11_dff_ted_spy_story.py
ted_spliced_spy -> pages/12_ted_spliced_spy_story.py
```

All 3 pairs have `results/{pair_id}/interpretation_metadata.json` → each will render its own card on the dashboard grid. No ghost card remains for the former composite (registry now dynamic-discovers the 3 pair dirs that were already present on disk). **No Dana gap flagged.**

## Fields filled by Ace vs. stubbed for Ray (per pair)

Each config has the same field split:

- **Filled by Ace (structural / factual):** `PAGE_TITLE`, `PAGE_SUBTITLE`, `HEADLINE_H2`, `HERO_TITLE`, `HERO_CHART_NAME`, `REGIME_TITLE`, `REGIME_CHART_NAME`, evidence method-block `method_name` + `chart_name`, `TOURNAMENT_SCATTER_CHART_NAME`, `_DATA_SOURCES_MD`, `_METHODS_TABLE_MD`, `_TOURNAMENT_DESIGN_MD`, `_REFERENCES_MD`.
- **Stubbed for Ray (narrative prose):** StoryConfig — `PLAIN_ENGLISH`, `WHERE_THIS_FITS`, `ONE_SENTENCE_THESIS`, `KPI_CAPTION`, `HERO_CAPTION`, `REGIME_CAPTION`, `NARRATIVE_SECTION_1`, `NARRATIVE_SECTION_2`, `SCOPE_NOTE`, `TRANSITION_TEXT`. Evidence method blocks — `method_theory`, `question`, `how_to_read`, `chart_caption`, `observation`, `interpretation`, `key_message` (× 2 blocks × 3 pairs). Evidence shell — `overview`, `plain_english`, `tournament_intro`, `transition`. StrategyConfig — `PLAIN_ENGLISH`, `SIGNAL_RULE_MD`, `HOW_SIGNAL_IS_GENERATED_MD`, `MANUAL_USE_MD`, `CAVEATS_MD`, `TRADE_LOG_EXAMPLE_MD`. Methodology — `_INDICATOR_CONSTRUCTION_MD`, `sample_period_note`, `plain_english`.

**Total stubs: 111 (37 × 3).**

## Stub-grep command for Ray

```bash
grep -n "TODO Ray (Wave 10I.A Part 2)" \
  app/pair_configs/sofr_ted_spy_config.py \
  app/pair_configs/dff_ted_spy_config.py \
  app/pair_configs/ted_spliced_spy_config.py
```

## Flags for downstream agents

### Dana
- **No gaps.** All 3 TED pair dirs already have `interpretation_metadata.json`, `tournament_results_20260314.csv`, `winner_summary.json`, and `winner_trade_log.csv` on disk (pre-existing from the original TED-variants pipeline run). Landing-page grid surfaces each pair automatically.

### Evan
- **Pre-existing data gap (not a regression).** None of the 3 TED pairs has `equity_curves`, `drawdown`, or `walk_forward` chart artifacts on disk (only 5 charts per pair: hero, regime_stats, correlations, local_projections, tournament_scatter). Strategy-page Performance tab will show "chart pending" placeholders for those 3 surfaces — identical behavior to the legacy composite. The composite didn't render them either, so the explode does **not** introduce a regression. Evan may queue a Vera-task to generate the missing charts under a later wave if Lead decides.

### Ray
- **111 TODO-Ray stubs across 3 files.** Prose can be ported via `git show HEAD~1:app/pages/6_ted_variants_*.py` once the explode commit is the current HEAD. Each stub cites the composite filename + line range.
- **Signal-rule caveat.** Composite's per-tab winner spotlight was computed by reading `results/{pid}/tournament_results_20260314.csv` at page-render time (dynamic). For a static narrative, Ray should read `results/{pid}/winner_summary.json` and transcribe the winner params into each `STRATEGY_CONFIG.SIGNAL_RULE_MD`. Don't claim tournament numbers Ray hasn't verified against `winner_summary.json`.
- **The per-variant caveat section** (composite `strategy.py` lines 146-152) covered all 3 variants in one block. Split pair-specifically — each `CAVEATS_MD` stub has a hint for which caveat belongs where.

### Quincy
- Smoke green for all 3 pairs. Cloud verify should hit:
  - `pages/6_sofr_ted_spy_{story,evidence,strategy,methodology}.py`
  - `pages/11_dff_ted_spy_{story,evidence,strategy,methodology}.py`
  - `pages/12_ted_spliced_spy_{story,evidence,strategy,methodology}.py`
  - Landing page: 3 distinct TED cards, all linking to the new per-pair surfaces.
  - Sidebar finding selector: 3 TED entries (not 1 composite).

## Scope-discipline confirmations

- Did **not** touch Sample (`hy_ig_v2_spy`) — Wave 10I.B.
- Did **not** touch the 4 non-TED configs from Part 1 — Ray's queue.
- Did **not** modify `page_templates.py`, chart artifacts, scripts, or SOPs.
- Did **not** write narrative prose anywhere — every narrative field is a TODO-Ray stub (LEAD-DL1 discipline).
- Did **not** touch `results/*` (interpretation metadata already present, no new files needed).

## Next-step dispatch for Ray

Ray's content port can proceed pair-by-pair. Each stub identifies the deleted composite file + approximate line range to retrieve via `git show HEAD~1:…`. After Ray's commit, Quincy's cloud verify covers all 3 exploded TED surfaces alongside the Part-1 pairs.
