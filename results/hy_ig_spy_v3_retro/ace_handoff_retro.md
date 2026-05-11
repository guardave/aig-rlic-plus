# Ace Handoff — hy_ig_spy_v3_retro
Generated: 2026-05-11

## Files Created

### pair_config
```
-rw-r--r-- 1 vscode vscode 7636 May 11 17:22 app/pair_configs/hy_ig_spy_v3_retro_config.py
```

### portal pages
```
-rw-r--r-- 1 vscode vscode 2573 May 11 17:23 app/pages/91_hy_ig_spy_v3_retro_evidence.py
-rw-r--r-- 1 vscode vscode 4978 May 11 17:23 app/pages/91_hy_ig_spy_v3_retro_strategy.py
-rw-r--r-- 1 vscode vscode 5670 May 11 17:24 app/pages/91_hy_ig_spy_v3_retro_methodology.py
```

META-SRV: files confirmed via `ls -la` at build time (2026-05-11 17:22–17:24).

## Link Verification Log

Story page: `app/pages/91_hy_ig_spy_v3_retro_story.py`

Links found in story page:
1. `[← Clean Rerun fork (page 90)](90_hy_ig_spy_v3_rerun_story)` — target: `app/pages/90_hy_ig_spy_v3_rerun_story.py` — EXISTS: YES
   META-SRV: `ls app/pages/90_hy_ig_spy_v3_rerun_story.py` → file present (committed 90dc902).

Links added by Ace pages (within pages 91_*):
2. Evidence page nav → `91_hy_ig_spy_v3_retro_story` — EXISTS: YES (story page, not modified)
3. Strategy page nav → `91_hy_ig_spy_v3_retro_evidence` — EXISTS: YES (created this session)
4. Strategy page nav → `91_hy_ig_spy_v3_retro_methodology` — EXISTS: YES (created this session)
5. Methodology page nav → `91_hy_ig_spy_v3_retro_strategy` — EXISTS: YES (created this session)

All links resolve. No broken links.

## Chart Load Issues

All 4 Vera charts confirmed present on disk (META-SRV: `ls -la output/charts/hy_ig_spy_v3_retro/plotly/`):
- `equity_curves_holdout.json` (25,485 bytes) — loaded in strategy page
- `equity_curves_validation.json` (124,420 bytes) — loaded in strategy page
- `signal_distribution.json` (80,453 bytes) — loaded in evidence page
- `drawdown_comparison.json` (24,549 bytes) — loaded in strategy page

No chart load issues found. GATE-25 placeholder pattern coded defensively in all chart calls.

## Design Decisions

- Did NOT use `render_evidence_page()` from page_templates — same reason as rerun fork: template requires 8 statistical method blocks not available for experiment forks.
- Evidence page renders: Ray evidence narrative + signal_distribution chart.
- Strategy page renders: Ray strategy narrative + ECON-OOS4 retro-apply caveat (st.info) + all 3 performance charts.
- Methodology page renders: Ray methodology narrative + ECON-OOS4 retro-apply caveat (st.info) + ECON-FE1 table + three-period split + data sources.
- Retro-apply caveat rendered on both Strategy and Methodology pages as required.
- Experiment fork banner on every page: `st.warning("⚗️ EXPERIMENT FORK — not a production pair. Results are for comparison purposes only.")`

## Scope Boundary
Ace scope ends here. No results/ files modified except this handoff note.
