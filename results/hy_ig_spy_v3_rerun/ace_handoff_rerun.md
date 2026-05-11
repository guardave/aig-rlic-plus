# Ace Handoff — hy_ig_spy_v3_rerun
Generated: 2026-05-11

## Files Created

### pair_config
```
-rw-r--r-- 1 vscode vscode 7199 May 11 17:21 app/pair_configs/hy_ig_spy_v3_rerun_config.py
```

### portal pages
```
-rw-r--r-- 1 vscode vscode 2587 May 11 17:22 app/pages/90_hy_ig_spy_v3_rerun_evidence.py
-rw-r--r-- 1 vscode vscode 4307 May 11 17:22 app/pages/90_hy_ig_spy_v3_rerun_strategy.py
-rw-r--r-- 1 vscode vscode 4970 May 11 17:23 app/pages/90_hy_ig_spy_v3_rerun_methodology.py
```

META-SRV: files confirmed via `ls -la` at build time (2026-05-11 17:22–17:23).

## Link Verification Log

Story page: `app/pages/90_hy_ig_spy_v3_rerun_story.py`

Links found in story page:
1. `[→ Retro-Apply fork (page 91)](91_hy_ig_spy_v3_retro_story)` — target: `app/pages/91_hy_ig_spy_v3_retro_story.py` — EXISTS: YES
   META-SRV: `ls app/pages/91_hy_ig_spy_v3_retro_story.py` → file present (committed 90dc902).

Links added by Ace pages (within pages 90_*):
2. Evidence page nav → `90_hy_ig_spy_v3_rerun_story` — EXISTS: YES (story page, not modified)
3. Strategy page nav → `90_hy_ig_spy_v3_rerun_evidence` — EXISTS: YES (created this session)
4. Strategy page nav → `90_hy_ig_spy_v3_rerun_methodology` — EXISTS: YES (created this session)
5. Methodology page nav → `90_hy_ig_spy_v3_rerun_strategy` — EXISTS: YES (created this session)

All links resolve. No broken links.

## Chart Load Issues

All 4 Vera charts confirmed present on disk (META-SRV: `ls -la output/charts/hy_ig_spy_v3_rerun/plotly/`):
- `equity_curves_holdout.json` (25,390 bytes) — loaded in strategy page
- `equity_curves_validation.json` (124,375 bytes) — loaded in strategy page
- `signal_distribution.json` (70,555 bytes) — loaded in evidence page
- `drawdown_comparison.json` (24,634 bytes) — loaded in strategy page

No chart load issues found. GATE-25 placeholder pattern coded defensively in all chart calls.

## Design Decisions

- Did NOT use `render_evidence_page()` from page_templates — the template requires 8 statistical method blocks that this experiment fork does not have (only 4 Vera charts + Ray narrative). Self-contained pages built instead.
- Evidence page renders: Ray evidence narrative + signal_distribution chart.
- Strategy page renders: Ray strategy narrative + all 3 performance charts (holdout equity, validation equity, drawdown).
- Methodology page renders: Ray methodology narrative + ECON-FE1 table + three-period split + data sources.
- Experiment fork banner on every page: `st.warning("⚗️ EXPERIMENT FORK — not a production pair. Results are for comparison purposes only.")`

## Scope Boundary
Ace scope ends here. No results/ files modified except this handoff note.
