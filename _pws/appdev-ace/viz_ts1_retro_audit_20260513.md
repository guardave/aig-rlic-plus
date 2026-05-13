# VIZ-TS1 Retroactive Audit — 2026-05-13

**Auditor:** Ace AppDev
**Rule:** VIZ-TS1 (Shared Time Axis for Multi-Panel Time-Series Charts) — see `docs/agent-sops/visualization-agent-sop.md` §VIZ-TS1
**Scope:** Every `history_zoom_*.json` under `output/charts/*/plotly/` across all pairs
**Method:** Verbatim `check_shared_time_axis()` function from VIZ-TS1 rule body, applied via `temp/viz_ts1_audit.py`

## Headline

- Total charts audited: **104**
- PASS: **104**
- FAIL: **0**

All multi-panel `history_zoom_*.json` charts on the branch conform to VIZ-TS1 (single bottom-panel date tick set; `xaxis.matches="x2"`; `xaxis.showticklabels=false`; correct `yaxis`/`yaxis2` anchors; bottom-panel traces declare `xaxis="x2"`).

## Per-pair tally

| Pair | Pass | Fail |
|------|-----:|-----:|
| dff_ted_spy | 12 | 0 |
| hy_ig_spy | 6 | 0 |
| hy_ig_spy_v4_from_scratch | 10 | 0 |
| hy_ig_v2_spy | 6 | 0 |
| indpro_spy | 10 | 0 |
| indpro_xlp | 10 | 0 |
| permit_spy | 10 | 0 |
| sofr_ted_spy | 7 | 0 |
| ted_spliced_spy | 12 | 0 |
| umcsent_xlv | 12 | 0 |
| vix_vix3m_spy | 9 | 0 |
| **Total** | **104** | **0** |

Note: `hy_ig_spy_v3_rerun` and `hy_ig_spy_v3_retro` pair directories contain no `history_zoom_*.json` files (no multi-panel zoom charts produced for those waves), so are not included in the tally.

## Failures

None.

## Disposition

Report-only. No chart JSON files were touched (Vera's lane). The VIZ-TS1 rule, freshly authored today by Lead, is already universally satisfied on the branch — the recent reader-walk fixes (commits `7f2470d`, `76321b0`) appear to have brought every pair into compliance ahead of codification.
