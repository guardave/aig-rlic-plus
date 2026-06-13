# QA Verification — Track A (fix260613_lead_horizon), 2026-06-13, Quincy

**Branch:** `fix260613_lead_horizon` · **Mode 1** · **Scope:** Track A only
(lead blocks newly wired on vix_vix3m_spy, hy_ig_spy, busloans_spy; permit_spy
CP-prose relocation; optional `CROSS_PERIOD_NARRATIVE_MD` slot). RE-RUN pairs
(indpro_spy, indpro_xlp, umcsent_xlv, gold_copper_xli) NOT under test (Track B).
Frozen Sample (hy_ig_v2_spy) exempt from new blocks.

## Summary
Total checks: 7 gate/assertion groups + triangulation.
PASS: all Track-A assertions. FAIL: 0 NEW defects. Pre-existing (out-of-scope) GATE-DPS1 FAILs documented, all owned by Track B / prior builds.

**Verdict: READY for Track A merge.**

---

## 1. Gate Suite (9 pairs) — ALL CLEAN

| Gate | Command | Result |
|---|---|---|
| Schemas | `validate_all_schemas.py` | PASS — pairs=9 pass=33 fail=0 skip=3 (exit 0) |
| Filenames | `lint_filename_convention.py` | PASS — 427 json checked, violations=0 |
| Chart completeness | `lint_chart_completeness.py` | PASS — refs=123 failures=0 |
| Smoke loader | `smoke_loader.py --all` | PASS — pairs=9 total_failures=0 |

The 3 wired pairs each reference both new charts (`correlations_lead_view`,
`lead_sharpe_distribution`); JSON artifacts + perceptual PNGs present on disk for all 3.

## 2. GATE-DPS1 (3 wired pairs) — NEW defects = 0

`validate_pair_completeness.py --pair {...}`:

| Pair | Overall | FAIL items | NEW? | Owner |
|---|---|---|---|---|
| busloans_spy | 1 FAIL / 153 PASS | DPS-PRE1 final-exam not run (`status=found_in_search`) | NO — known DPS-PRE1 waiver from build | Evan/Lead (waiver) |
| hy_ig_spy | 5 FAIL / 150 PASS | evidence_status.json absent; history_zoom_inflation_2022 chart+PNG+slug missing | NO — prior build / Track B | Dana/Vera/Ace (Track B) |
| vix_vix3m_spy | 9 FAIL / 98 PASS | evidence_status.json absent; history_zoom dotcom+inflation_2022 missing; Level-2 block count=1 (<2) | NO — all pre-date Track A | Dana/Vera/Ace (Track B) |

**Proof these are not Track-A regressions:** Track A commit `58de67d` touched only
the 5 pair-config files (lead-block wiring + CP slot). It did not touch
`evidence_status.json`, `history_zoom_*` charts, or method-block counts.
Verified vix Level-2 count was already FAIL on `58de67d~1` (10 FAIL before → 9 after);
Track A wiring **reduced** the failure count by adding the Level-1 lead blocks.

## 3. Rendered-DOM (LEAD-DOM1) — local Streamlit + headless Playwright

36 DOM captures (9 pairs × 4 pages). Script: `temp/qa_local_dom_verify.py`.
DOM text + HTML + screenshots: `temp/20260613_163811_qa_track_a/`.

**Global scan: zero** occurrences of `traceback`, `cannot render`,
`cannot be derived`, `chart pending`, `StreamlitAPIException`, `PageNotFound`,
`vs N/A`, `Error loading` across all 36 files.

### 3a. Lead Analysis + Lead Tournament blocks (3 wired pairs)

| Pair | Lead Analysis heading | Lead Tournament heading | LA chart | LT chart | Distinct? |
|---|---|---|---|---|---|
| vix_vix3m_spy | present (L64) | present (L66) | correlations_lead_view (heatmap) | lead_sharpe_distribution (bar) | YES |
| hy_ig_spy | present (L64) | present (L66) | correlations_lead_view (heatmap) | lead_sharpe_distribution (bar) | YES |
| busloans_spy | present (L66) | present (L68) | correlations_lead_view (heatmap) | lead_sharpe_distribution (bar) | YES |

Both blocks sit in Level-1 after Correlation (`level1_labels` ordering confirmed).
Chart-type verified at JSON level: `correlations_lead_view` = heatmap (1 trace);
`lead_sharpe_distribution` = bar+scatter (4 traces). No two blocks share a chart.
8-element / Level-1+Level-2 tab structure intact; breadcrumb (Story→Evidence→
Strategy→Methodology) present on all.

### 3b. permit_spy CP relocation (DPS-CPX1)

- **Evidence transition:** clean one-line bridge ("...which the next page's
  Confidence tab examines directly"). **No orphan "cross-period charts above"
  text** — grep returned none. PASS.
- **Strategy → Confidence tab:** relocated CP narrative ("**Honest read on the
  cross-period charts on this tab.**") present in Strategy HTML. Renderer
  `_render_cross_period_section` (page_templates.py L1018–1024) emits `narrative_md`
  immediately under the "Cross-Period Consistency" heading, ABOVE the first chart. PASS.
- Only `permit_spy_config.py` sets `CROSS_PERIOD_NARRATIVE_MD` (no-op for all others — regression-safe).

### 3c. Regression — RE-RUN pairs + frozen Sample render unchanged

| Pair | Lead-block hits on Evidence | Lead charts on disk | Config refs | Render |
|---|---|---|---|---|
| indpro_spy | 0 | 6 | 0 | clean |
| indpro_xlp | 0 | 6 | 0 | clean |
| umcsent_xlv | 0 | 6 | 0 | clean |
| gold_copper_xli | 0 | 6 | 0 | clean (spot-check confirmed) |
| hy_ig_v2_spy (Sample) | 0 | n/a | n/a | clean |

RE-RUN pairs have lead charts on disk but zero config references — **intentionally
unwired (Track B)**, exactly per dispatch. No new blocks, no errors, no orphan-prose change.

## 4. Numeric Spot-Triangulation (QA-CL) — hy_ig_spy

**Heatmap `correlations_lead_view` vs `lead_correlation_20260613.csv`:**
- z[0][0] = −0.05 → CSV hy_ig_spread_pct/L0 = −0.050 ✓
- z[1][1] = −0.011 → CSV hy_ig_zscore_252d/L1 = −0.011 ✓
- z[9][12] = −0.01 → CSV hmm_2state_prob_stress/L12 = −0.01 ✓

**`lead_sharpe_distribution` max bar vs `lead_tournament_20260613.csv`:**
- Max bar = 1.4389 (at L1) → CSV `best_oos_sharpe` max = 1.4389 ✓

All triangulations PASS (exact match).

## 5. HABIT-QA1 DOM read attestation
See `_pws/qa-quincy/session-notes.md`. Read DOM text for all four page types
across the 3 wired pairs + permit + regression pairs; found no error/stub strings.

---

## Defect list
**No NEW (Track-A) defects.** Pre-existing / out-of-scope items (do NOT block Track A merge):

| # | Item | Disposition | Owner |
|---|---|---|---|
| P1 | busloans_spy DPS-PRE1 final exam not run | Known waiver (carried from build) | Lead/Evan |
| P2 | vix/hy_ig evidence_status.json absent | Track B (RE-RUN/final-exam scope) | Dana/Evan |
| P3 | vix/hy_ig history_zoom dotcom/inflation_2022 charts missing | Track B | Vera |
| P4 | vix Level-2 method-block count = 1 (<2) | Pre-dates Track A (was 10 FAIL before wiring) | Evan/Ace, Track B |

## Sign-off recommendation
**Approve (READY)** for Track A merge. All Track-A assertions PASS; the two new
Evidence blocks render distinct charts on all 3 wired pairs; permit CP-prose moved
with no Evidence orphan; regression pairs + Sample unchanged; triangulation exact.

🤖 Agent: QA Quincy
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
