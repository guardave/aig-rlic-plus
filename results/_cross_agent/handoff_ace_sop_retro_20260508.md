# AppDev Ace Handoff — SOP Retro Artifact Remediation

Date: 2026-05-08
Owner: appdev-ace

## Scope Checked

Pairs:
`hy_ig_v2_spy`, `hy_ig_spy`, `indpro_xlp`, `indpro_spy`, `umcsent_xlv`,
`dff_ted_spy`, `ted_spliced_spy`, `sofr_ted_spy`, `permit_spy`,
`vix_vix3m_spy`.

Surfaces:
all scoped `app/pages/*_{story,evidence,strategy,methodology}.py`,
`app/components/page_templates.py`, structural AppDev components, and
Ace-owned pair config references visible from the templates.

## SOP Rules Applied

| Rule | Applied result |
|---|---|
| META-NMF | Artifact fixes made only after SOP cross-review dispatch. |
| META-TD1 | Handoff records decisions, blockers, and command results only. |
| META-DASH1 | Fixed rendered navigation consistency across all four pages via registry routing. |
| GATE-25 | Missing chart states are not silently substituted; unresolved placeholders listed below. |
| GATE-27 | Ran loader smoke for all ten scoped pairs. |
| GATE-28 | Removed live/future placeholder panel from delivered strategy pages unless a real snapshot artifact exists. |
| GATE-29 | Clean-checkout not run in this pass; no deploy-required artifact ownership changes made by Ace. |
| APP-RL1 | Sidebar and breadcrumb now consume registry routing instead of hardcoded page lists/prefixes. |
| APP-DIR1 | Direction mismatch copy now uses reader-safe labels instead of producer/file diagnostics. |
| APP-SE4 | Live/current section now renders only from `live_execution_snapshot.json`; legacy stubs are hidden. |

## Files Changed

| File | Change |
|---|---|
| `app/components/sidebar.py` | Replaced hardcoded seven-pair sidebar with `load_pair_registry()`-driven selector and dynamic analyzed-pair count. |
| `app/components/breadcrumb.py` | Replaced hardcoded `pages/9_...` link construction with `get_page_prefix(pair_id)`. |
| `app/components/live_execution_placeholder.py` | Converted future/live placeholder renderer into snapshot-only renderer; absent snapshots render no section. |
| `app/components/direction_check.py` | Reworded rendered direction warnings/errors to reader-safe model/metadata/story labels. |
| `results/_cross_agent/handoff_ace_sop_retro_20260508.md` | This handoff. |

## Audit Findings

| Finding | Disposition |
|---|---|
| Sidebar omitted current delivered pairs (`hy_ig_spy`, `indpro_xlp`, `umcsent_xlv`) and carried hardcoded page paths. | Fixed in `sidebar.py`; registry now drives labels/pages/count. |
| Breadcrumb hardcoded `pages/9_{pair_id}_...`, producing impossible links for non-`9_` pairs. | Fixed in `breadcrumb.py`; registry prefix now drives all page links. |
| Strategy pages appended a user-facing "Future: Live Execution" placeholder with dash metrics. | Fixed by rendering only schema-shaped snapshot fields from `live_execution_snapshot.json`; absent snapshot omits the section. |
| Direction mismatch copy exposed producer/file diagnostics in user-facing warnings. | Fixed rendered copy; internal report notes still retain diagnostics for developers. |
| `hy_ig_v2_spy` reference pages remain hand-written instead of APP-PT1 thin wrappers. | Unresolved AppDev blocker; content-preserving migration needs a dedicated pass because these pages contain bespoke reference content not represented in a pair config. |
| Some Strategy performance charts are still absent under canonical/default names and can render GATE-25 placeholders. | Unresolved cross-role blocker; see table below. |

## Remaining Placeholder/Artifact Blockers

Cross-period charts checked clean for all ten scoped pairs:
`subperiod_sharpe`, `rolling_correlation`, `structural_break`,
`rolling_sharpe_cp`, and `rolling_granger` all exist.

Strategy performance chart gaps found by canonical/default presence check:

| Pair | Missing default chart(s) |
|---|---|
| `hy_ig_v2_spy` | `tournament_scatter` |
| `indpro_spy` | `drawdown`, `walk_forward` |
| `umcsent_xlv` | `walk_forward` |
| `dff_ted_spy` | `equity_curves`, `drawdown`, `walk_forward` |
| `ted_spliced_spy` | `equity_curves`, `drawdown`, `walk_forward` |
| `sofr_ted_spy` | `equity_curves`, `drawdown`, `walk_forward` |
| `permit_spy` | `equity_curves`, `drawdown`, `walk_forward` |
| `vix_vix3m_spy` | `equity_curves`, `drawdown`, `walk_forward` |

Owner routing: Vera owns missing chart artifacts/sidecars; Ace owns any
incorrect config mapping if Vera confirms an equivalent canonical artifact
already exists under another approved name.

## Verification Commands / Results

```bash
python3 -m py_compile app/components/breadcrumb.py app/components/sidebar.py app/components/live_execution_placeholder.py app/components/page_templates.py
```

Result: PASS.

```bash
python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy
python3 app/_smoke_tests/smoke_loader.py hy_ig_spy
python3 app/_smoke_tests/smoke_loader.py indpro_xlp
python3 app/_smoke_tests/smoke_loader.py indpro_spy
python3 app/_smoke_tests/smoke_loader.py umcsent_xlv
python3 app/_smoke_tests/smoke_loader.py dff_ted_spy
python3 app/_smoke_tests/smoke_loader.py ted_spliced_spy
python3 app/_smoke_tests/smoke_loader.py sofr_ted_spy
python3 app/_smoke_tests/smoke_loader.py permit_spy
python3 app/_smoke_tests/smoke_loader.py vix_vix3m_spy
```

Results:

| Pair | Smoke result |
|---|---|
| `hy_ig_v2_spy` | PASS — 15 passed, 0 failed |
| `hy_ig_spy` | PASS — 6 passed, 0 failed |
| `indpro_xlp` | PASS — 8 passed, 0 failed |
| `indpro_spy` | PASS — 4 passed, 0 failed |
| `umcsent_xlv` | PASS — 6 passed, 0 failed |
| `dff_ted_spy` | PASS — 3 passed, 0 failed |
| `ted_spliced_spy` | PASS — 3 passed, 0 failed |
| `sofr_ted_spy` | PASS — 3 passed, 0 failed |
| `permit_spy` | PASS — 3 passed, 0 failed |
| `vix_vix3m_spy` | PASS — 3 passed, 0 failed |

```bash
for pair in hy_ig_v2_spy hy_ig_spy indpro_xlp indpro_spy umcsent_xlv dff_ted_spy ted_spliced_spy sofr_ted_spy permit_spy vix_vix3m_spy; do
  for chart in subperiod_sharpe rolling_correlation structural_break rolling_sharpe_cp rolling_granger; do
    test -f "output/charts/$pair/plotly/$chart.json"
  done
done
```

Result: PASS — no missing cross-period chart files reported.

```bash
for pair in hy_ig_v2_spy hy_ig_spy indpro_xlp indpro_spy umcsent_xlv dff_ted_spy ted_spliced_spy sofr_ted_spy permit_spy vix_vix3m_spy; do
  for chart in hero regime_stats equity_curves drawdown walk_forward tournament_scatter; do
    test -f "output/charts/$pair/plotly/$chart.json" || test -f "output/charts/$pair/plotly/${pair}_${chart}.json"
  done
done
```

Result: FAIL for the Strategy performance gaps listed above.
