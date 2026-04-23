# Handoff — Ace → Ray (Wave 10I.A Part 1: 4 legacy-pair migrations)

**Author:** Dev Ace (appdev-ace)
**Date:** 2026-04-23
**Wave:** 10I.A Part 1
**Governing rules:** APP-PT1 (template abstraction), APP-TL1 (trade log contract), APP-PR1 (path resolution)
**Scope:** Migrate 4 single-pair legacy surfaces to APP-PT1 thin-wrapper pattern. TED composite and Sample are out of scope for this dispatch.

---

## Summary

4 pair configs created, 16 page files reduced to thin wrappers. All smoke
loaders pass (0 failures across 4 pairs). Structural content (chart names,
data-source tables, methods tables, tournament design skeletons, references)
filled in-place by Ace. All narrative prose left as TODO-Ray stubs with
explicit source line hints — Ray's next dispatch replaces them.

## Per-pair line count before → after

| Pair | Page | Legacy lines | Thin-wrapper lines | Delta |
|---|---|---:|---:|---:|
| indpro_spy | story        | 146 | 18 | -128 |
| indpro_spy | evidence     | 183 | 18 | -165 |
| indpro_spy | strategy     | 213 | 18 | -195 |
| indpro_spy | methodology  | 150 | 18 | -132 |
| **indpro_spy total** |  | **692** | **72** | **-620** |
| permit_spy | story        | 152 | 18 | -134 |
| permit_spy | evidence     | 120 | 18 | -102 |
| permit_spy | strategy     | 218 | 18 | -200 |
| permit_spy | methodology  | 177 | 18 | -159 |
| **permit_spy total** |  | **667** | **72** | **-595** |
| vix_vix3m_spy | story        | 165 | 18 | -147 |
| vix_vix3m_spy | evidence     | 126 | 18 | -108 |
| vix_vix3m_spy | strategy     | 223 | 18 | -205 |
| vix_vix3m_spy | methodology  | 186 | 18 | -168 |
| **vix_vix3m_spy total** |  | **700** | **72** | **-628** |
| umcsent_xlv | story        | 304 | 18 | -286 |
| umcsent_xlv | evidence     | 447 | 18 | -429 |
| umcsent_xlv | strategy     | 473 | 18 | -455 |
| umcsent_xlv | methodology  | 339 | 18 | -321 |
| **umcsent_xlv total** |  | **1,563** | **72** | **-1,491** |
| **GRAND TOTAL (pages)** |  | **3,622** | **288** | **-3,334** |

## New pair configs (lines)

| File | Lines | TODO-Ray stubs |
|---|---:|---:|
| `app/pair_configs/indpro_spy_config.py`     | 440 | 65 |
| `app/pair_configs/permit_spy_config.py`     | 272 | 37 |
| `app/pair_configs/vix_vix3m_spy_config.py`  | 279 | 37 |
| `app/pair_configs/umcsent_xlv_config.py`    | 343 | 51 |
| **Total** | **1,334** | **190** |

## Smoke test results

All runs `failures=0`:

| Pair | passes | failures | Log file |
|---|---:|---:|---|
| indpro_spy     | 4 | 0 | `app/_smoke_tests/loader_indpro_spy_20260423.log` |
| permit_spy     | 3 | 0 | `app/_smoke_tests/loader_permit_spy_20260423.log` |
| vix_vix3m_spy  | 3 | 0 | `app/_smoke_tests/loader_vix_vix3m_spy_20260423.log` |
| umcsent_xlv    | 6 | 0 | `app/_smoke_tests/loader_umcsent_xlv_20260423.log` |

Pass counts differ because smoke only checks charts referenced as literal
`*_CHART_NAME` assignments or literal `load_plotly_chart(...)` first args.
Evidence method-block dict `chart_name="..."` entries are not AST-covered
(pre-existing limitation, same as hy_ig_spy).

## Fields filled by Ace vs. stubbed for Ray

Per `app/pair_configs/<pair_id>_config.py`, structural-filled vs. stubbed:

### indpro_spy (65 stubs)
- **Filled by Ace:** `PAGE_TITLE`, `PAGE_SUBTITLE`, `HEADLINE_H2`, `HERO_TITLE`,
  `HERO_CHART_NAME`, `REGIME_TITLE`, `REGIME_CHART_NAME`, all chart-name
  attrs on StrategyConfig (`EQUITY_CHART_NAME`, `TOURNAMENT_SCATTER_CHART_NAME`),
  evidence method-block names + labels + `chart_name` values (6 blocks:
  Correlation, CCF, Granger, Local Projections, Quantile, Random Forest),
  `_DATA_SOURCES_MD`, `_METHODS_TABLE_MD`, `_TOURNAMENT_DESIGN_MD`,
  `_REFERENCES_MD`.
- **Stubbed for Ray:** `PLAIN_ENGLISH`, `WHERE_THIS_FITS`,
  `ONE_SENTENCE_THESIS`, `KPI_CAPTION`, `HERO_CAPTION`, `REGIME_CAPTION`,
  `NARRATIVE_SECTION_1`, `NARRATIVE_SECTION_2`, `SCOPE_NOTE`,
  `TRANSITION_TEXT`, all method-block prose fields (`method_theory`,
  `question`, `how_to_read`, `chart_caption`, `observation`,
  `interpretation`, `key_message`), EVIDENCE overview/plain_english/
  tournament_intro/transition, StrategyConfig prose (`PLAIN_ENGLISH`,
  `SIGNAL_RULE_MD`, `HOW_SIGNAL_IS_GENERATED_MD`, `MANUAL_USE_MD`,
  `CAVEATS_MD`, `TRADE_LOG_EXAMPLE_MD`), Methodology
  `_INDICATOR_CONSTRUCTION_MD`, `sample_period_note`, `plain_english`.

### permit_spy (37 stubs), vix_vix3m_spy (37 stubs)
Same pattern as indpro_spy but with only 2 evidence blocks (Correlation,
Local Projections) — hence fewer stubs.

### umcsent_xlv (51 stubs)
Same pattern with 4 evidence blocks (Correlation, Granger, Regime,
Signal Distribution). `TRADE_LOG_EXAMPLE_MD` stub notes the broker-style
CSV at `results/umcsent_xlv/winner_trades_broker_style.csv` is available
(shipped Wave 10H.2) — Ray should author the narrative example block from
that file rather than restart from scratch.

## Stub-grep command for Ray

```bash
grep -n "TODO Ray (Wave 10I.A)" app/pair_configs/indpro_spy_config.py \
  app/pair_configs/permit_spy_config.py \
  app/pair_configs/vix_vix3m_spy_config.py \
  app/pair_configs/umcsent_xlv_config.py
```

Total: 190 stubs (65 + 37 + 37 + 51). Each stub cites the legacy page and
line range that holds the source prose.

## Unexpected content / things Ray should know

1. **Chart filename drift.** `indpro_spy`, `permit_spy`, `vix_vix3m_spy`
   still keep the legacy pair-id-prefixed chart filenames on disk
   (e.g. `indpro_spy_hero.json`, not the canonical bare `hero.json`).
   `umcsent_xlv` is already canonical. The configs set `HERO_CHART_NAME`,
   `REGIME_CHART_NAME`, etc. to the on-disk prefixed names to keep smoke
   green. A later wave (Vera) can rename these files to the canonical
   bare names and drop the chart-name attrs from the configs.

2. **Missing performance-tab charts for permit_spy and vix_vix3m_spy.**
   Neither pair has `equity_curves`, `drawdown`, or `walk_forward` chart
   files on disk. Those configs omit `EQUITY_CHART_NAME` /
   `DRAWDOWN_CHART_NAME` / `WALK_FORWARD_CHART_NAME` → template falls
   back to bare defaults → runtime shows "chart pending" placeholders.
   This is a **pre-existing data gap**, not a migration regression. The
   legacy pages also didn't render these charts (smoke evidence:
   legacy pages only referenced tournament_scatter + hero + regime +
   correlations + local_projections). Flag for Lead: this may be Evan's
   queue.

3. **umcsent_xlv walk-forward chart is named `wf_sharpe`, not canonical
   `walk_forward`.** Config sets `WALK_FORWARD_CHART_NAME = "wf_sharpe"`
   so smoke and runtime both resolve.

4. **indpro_spy has a Random Forest method block** (rf_importance chart)
   — unusual in the portal. Preserved as a distinct 6th evidence block.
   Ray: check whether the legacy narrative (pages 139-162 of
   `5_indpro_spy_evidence.py`) should be preserved verbatim or reframed.

5. **Tournament winner parameters in each config's `_TOURNAMENT_DESIGN_MD`
   come from `docs/pair_execution_history.md`** (Ace did not re-run the
   tournament to verify). Ray should cross-check the winner KPIs against
   the pair's own `winner_summary.json` during narrative port.

6. **Pre-migration page count is 16; zero page files were renamed or
   renumbered.** Landing page registry (`components/pair_registry.py`)
   keys off numeric prefix — keeping N unchanged preserves card
   registration.

## Scope discipline confirmations

- Did **not** touch Sample (`hy_ig_v2_spy`) — Wave 10I.B.
- Did **not** touch the TED composite (`6_ted_variants_*.py`) — separate
  Ace-B dispatch.
- Did **not** modify `page_templates.py`. Discovery confirmed 0 template
  changes needed; that held.
- Did **not** write narrative prose anywhere — every narrative field is
  a TODO-Ray stub (LEAD-DL1 discipline).
- Did **not** touch chart artifacts, results/\*, scripts/, or SOPs.

## Next-step dispatch for Ray

Ray's content port can proceed pair-by-pair or in one batch. Each stub
identifies the source legacy file + approximate line range to port from.
After Ray's commit, Quincy's cloud verify should cover all 4 pairs — each
surface now uses the same template and should render without template
regressions.
