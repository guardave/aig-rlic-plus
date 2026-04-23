# Handoff — Quincy, Wave 10H.2 (APP-TL1 cloud verify + DOM marker extensions)

**From:** QA Quincy
**Date:** 2026-04-23
**Scope:** Cloud verification of Streamlit deployment after APP-TL1 retro-apply to `hy_ig_spy` and `indpro_xlp` Strategy pages. HEAD under verification: `2574d83`.

## 1. Summary

**Result: Wave 10H.2 ready to close.** 17/17 PASS on the GATE-28 grid. APP-TL1 markers fully present on both retro-applied pairs. Sample and `umcsent_xlv` (bypassed this wave) are unchanged.

## 2. Cloud verify script extensions

Surgical additions to `scripts/cloud_verify.py`:

1. **New constants block** (APP-TL1 markers): heading `"How to Read the Trade Log"`, broker-button label `"Download trade log (broker-style)"`, position-log-button label `"Download position log (researcher)"`, preview caption fragment `"executions, one row per trade"`. Scope set: `APP_TL1_PAIRS = {"hy_ig_spy", "indpro_xlp"}` — the two pairs retro-applied this wave. Sample and `umcsent_xlv` explicitly out of scope.
2. **`check_page` accepts `html`** and uses the full rendered HTML (`frame.content()`) for APP-TL1 marker matching. Required because the Trading History block lives inside the "Performance" tab panel of `st.tabs(["Execute", "Performance", "Confidence"])`. Streamlit renders inactive tabs into DOM but hides them via CSS; `inner_text("body")` only traverses visible elements. First verify pass returned false-FAIL on both retro-applied pairs (9 charts rendered — confirming the tab IS in DOM — but markers absent from visible text). Switched to `target.content()` HTML source for APP-TL1 assertions only; `inner_text` retained for existing checks.
3. **New `app_tl1_check` field** in result JSON: `{scope: "applied"|"n/a", heading, broker_button, position_button, preview, ok}`. Contributes to verdict only when `scope="applied"`.
4. **`get_dom` signature widened** to return a 4-tuple `(text, src, plotly_count, html)` with html captured via `frame.content()` after text stabilizes.

## 3. Verdict grid

| Slug | Verdict | Charts | APP-PT2 | APP-TL1 |
|---|---|---|---|---|
| landing | PASS | — | — | — |
| hy_ig_v2_spy × {story,evidence,strategy,methodology} | PASS×4 | 5/8/7/3 | Sample Methodology: section=True, ELI5=3/3 | n/a |
| hy_ig_spy × {story,evidence,strategy,methodology} | PASS×4 | 5/8/9/0 | non-Sample Methodology: section=False | **strategy: heading✓ broker✓ position✓ preview✓** |
| indpro_xlp × {story,evidence,strategy,methodology} | PASS×4 | 2/3/9/0 | non-Sample Methodology: section=False | **strategy: heading✓ broker✓ position✓ preview✓** |
| umcsent_xlv × {story,evidence,strategy,methodology} | PASS×4 | 2/4/5/0 | non-Sample Methodology: section=False | n/a |

**17 PASS / 0 FAIL / 17 TOTAL.**

## 4. APP-TL1 marker presence (retro-applied pairs)

| Pair | Heading | Broker button | Position button | Preview caption |
|---|---|---|---|---|
| `hy_ig_spy` | ✓ | ✓ | ✓ | ✓ |
| `indpro_xlp` | ✓ | ✓ | ✓ | ✓ |

Detected via `target.content()` (full iframe HTML). Chart-count jump 7→9 on both strategy pages corroborates the Trading History block rendered (new preview dataframe = 1 additional chart-adjacent DOM element observed alongside the standard Performance-tab charts).

## 5. Regression gate (bypassed pairs)

| Pair | Strategy page verdict | Change vs Wave 10H.1 |
|---|---|---|
| `hy_ig_v2_spy` (Sample) | PASS, 7 charts | Unchanged (hand-rolled legacy — APP-TL1 does not reach it) |
| `umcsent_xlv` | PASS, 5 charts | Unchanged (tracked as BL-APP-PT1-UMCSENT follow-on) |

No regressions. APP-PT2 regression gate (non-Sample Methodology pages MUST NOT render Exploratory Insights section) holds for all 3 non-Sample pairs.

## 6. Smoke tests

`python3 app/_smoke_tests/smoke_loader.py <pair>` for all 4 pairs: **failures=0** on each.

- `hy_ig_v2_spy` — passes=15
- `hy_ig_spy` — passes=6
- `indpro_xlp` — passes=8
- `umcsent_xlv` — passes=7

## 7. QA-CL2 status

Pattern 22 fix (canonical `query_selector_all(".js-plotly-plot")`) holds. Iframe-selector pattern (`wait_for_selector('iframe[title="streamlitApp"]').content_frame()`) holds. Added a new documented pattern:

- **Pattern 23 — Tab-panel lazy-hide.** Streamlit's `st.tabs` renders all panels into DOM but hides inactive ones via CSS. Playwright `inner_text` does NOT traverse hidden panels. For marker-presence checks on content inside tabs other than the default-active first tab, use `frame.content()` HTML source instead of `inner_text`. Canonical implementation now in `scripts/cloud_verify.py` `check_page(html=...)`. Lesson to codify in qa-agent-sop.md under QA-CL2 at next SOP revision.

## 8. Artifacts

- Cloud verify run (final, passing): `temp/20260423T075033Z_cloud_verify_wave10h2/results.json` + `summary.txt` + `dom_text/` + `screenshots/`.
- First (pre-fix) run showing the false-FAIL diagnostic: `temp/20260423T074506Z_cloud_verify/results.json` (15 PASS / 2 FAIL — kept for lesson documentation).
- Updated script: `scripts/cloud_verify.py`.

## 9. Recommendation

**Wave 10H.2 ready to close.** APP-TL1 framework ships green end-to-end on its defined scope. No blocking issues.

**Follow-ons (already logged, no new backlog):**

- `BL-APP-PT1-UMCSENT` — `umcsent_xlv` Strategy page migration onto the APP-PT1 template (then APP-TL1 auto-applies).
- Sample decommission (hy_ig_v2_spy legacy Strategy page retirement) — tracked in SOP changelog as Wave 10H.2 follow-on.
- Codify Pattern 23 (tab-panel lazy-hide / `content()` over `inner_text`) in qa-agent-sop.md at next SOP revision.

## 10. Compliance

- Did NOT modify Ace's `_render_trade_log_block` helper.
- Did NOT modify Ray's narrative constants or any pair config.
- Did NOT touch Evan's CSVs or the shared helper.
- Did NOT rerun Vera's backfill or touch chart sidecars.
- Script changes are surgical and isolated to Quincy-owned `scripts/cloud_verify.py`.
