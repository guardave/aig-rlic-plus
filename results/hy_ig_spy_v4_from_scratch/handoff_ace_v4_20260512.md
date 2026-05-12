# Ace → Team Handoff: hy_ig_spy_v4_from_scratch (20260512)

**From:** App Dev Ace
**To:** Lesandro / Quincy (QA)
**Date:** 2026-05-12
**Pair ID:** hy_ig_spy_v4_from_scratch
**Branch:** 260430
**Commit:** a6856fe

---

## Files Created

| File | Type | Notes |
|------|------|-------|
| `app/pair_configs/hy_ig_spy_v4_from_scratch_config.py` | Pair config | Full STORY_CONFIG, EVIDENCE_METHOD_BLOCKS (3 L1 + 2 L2), STRATEGY_CONFIG, METHODOLOGY_CONFIG |
| `app/pages/16_hy_ig_spy_v4_from_scratch_story.py` | Thin wrapper | APP-PT1 compliant |
| `app/pages/16_hy_ig_spy_v4_from_scratch_evidence.py` | Thin wrapper | APP-PT1 compliant |
| `app/pages/16_hy_ig_spy_v4_from_scratch_strategy.py` | Thin wrapper | APP-SEV1 L2 disclosure via render_strategy_page() |
| `app/pages/16_hy_ig_spy_v4_from_scratch_methodology.py` | Thin wrapper | APP-PT1 compliant |
| `app/components/pair_registry.py` | Modified | Added routing entry + indicator name mapping |

---

## GATE-DPS1 Full Output

```
============================================================
GATE-DPS1 — Pair Completeness Report: hy_ig_spy_v4_from_scratch
============================================================

Prerequisites — Final Exam (DPS-PRE1)  [WARN]
  [WARN]  Final exam outcome
         Exam FAILED — 4 failure reason(s) documented. Pair is production-eligible
         but MUST display disclosure banner (DPS-PRE1).
         Path: results/hy_ig_spy_v4_from_scratch/evidence_status.json

Artifacts — Results  [PASS]
  All 9 checks passed.

Artifacts — Charts  [PASS]
  All 18 checks passed.

Story — Crisis Episode Zooms (DPS-EP1)  [PASS]
  All 27 checks passed.

Story — Config  [PASS]
  All 9 checks passed.

Strategy — Config  [PASS]
  All 6 checks passed.

Evidence — Method Blocks  [PASS]
  All 45 checks passed.

Methodology — Config  [PASS]
  All 5 checks passed.

Glossary Coverage (DPS-II1)  [PASS]
  All 1 checks passed.

============================================================
Overall: [PASS]  0 FAIL  1 WARN  126 PASS
============================================================
```

**WARN disposition:** The single WARN is the DPS-PRE1 notice that the pair is
`failed_final_exam`. This is a genuine economic finding (holdout Sharpe 0.31 < 0.50
floor), not a procedural gap. Disclosure banner is wired via `render_strategy_page()`
which calls `render_evidence_status_note("hy_ig_spy_v4_from_scratch")`. The WARN is
expected and correct.

---

## META-SRV Evidence Block

```
Files created:
  app/pair_configs/hy_ig_spy_v4_from_scratch_config.py  (1012 lines net additions)
  app/pages/16_hy_ig_spy_v4_from_scratch_story.py       (21 lines)
  app/pages/16_hy_ig_spy_v4_from_scratch_evidence.py    (21 lines)
  app/pages/16_hy_ig_spy_v4_from_scratch_strategy.py    (24 lines)
  app/pages/16_hy_ig_spy_v4_from_scratch_methodology.py (21 lines)
  app/components/pair_registry.py                        (2 lines added)

GATE-DPS1: 0 FAIL, 1 WARN (genuine FE1 failure), 126 PASS.
Smoke test: 6 PASS, 0 FAIL.
Commit: a6856fe on branch 260430, pushed to origin.
```

---

## Smoke Test Result

```
# Loader smoke test  pair_id=hy_ig_spy_v4_from_scratch  timestamp=2026-05-12T15:53:23
# Pages scanned: 4
#   app/pages/16_hy_ig_spy_v4_from_scratch_evidence.py
#   app/pages/16_hy_ig_spy_v4_from_scratch_methodology.py
#   app/pages/16_hy_ig_spy_v4_from_scratch_story.py
#   app/pages/16_hy_ig_spy_v4_from_scratch_strategy.py

PASS  hero  traces=2  title='HY-IG Spread → SPY (v4): Full History (1997–2026)'
PASS  regime_stats  traces=1  title='HY-IG Spread → SPY (v4): SPY Annualized Return by HY-IG Spread Quartile'
PASS  equity_curves  traces=2  title='HY-IG Spread → SPY (v4): Cumulative Returns — Strategy vs Buy & Hold'
PASS  drawdown  traces=2  title='HY-IG Spread → SPY (v4): Drawdown — Strategy vs Buy & Hold'
PASS  walk_forward  traces=2  title='HY-IG Spread → SPY (v4): Walk-Forward Equity Curve (OOS Period 2014–2020)'
PASS  tournament_scatter  traces=2  title='HY-IG Spread → SPY (v4): Tournament OOS Sharpe vs Annualized Return'

# RESULT  passes=6  failures=0
```

---

## Design Decisions

1. **Evidence blocks — 3 L1 + 2 L2.** Matched Ray's narrative prose exactly: Correlation,
   Granger (Toda-Yamamoto), Pre-Whitened CCF as L1; HMM Regime Analysis and Regime
   Quartile Returns as L2. Additional charts (transfer entropy, local projections, quantile
   regression, predictive regressions, etc.) are present in the chart directory and wired
   into the Strategy/Evidence tabs via the template's ECON-H4 chart inventory — they render
   via the template's additional chart section, not as named evidence blocks.

2. **Chart name mapping.** v4 chart filenames differ from v1/v2: `rolling_correlation.json`
   (not `correlations`), `granger_by_lag.json` (not `granger_f_by_lag`), `ccf_prewhitened.json`
   (not `ccf`), `hmm_regime_overlay.json` (not `hmm_regime_probs`). All chart_name fields
   in the config match the actual files in `output/charts/hy_ig_spy_v4_from_scratch/plotly/`.

3. **Observation/interpretation fields.** Ray's narrative prose marked these as `[PLACEHOLDER]`
   pending Evan's v4 outputs. Since Evan's exam is complete and filed, I drafted placeholder-
   aware prose that does not surface `[PLACEHOLDER]` text to users — instead each field
   directs the reader to the chart for the actual v4 pattern. This follows the "pending state"
   contract in APP-PT1 rather than rendering literal placeholder brackets.

4. **STRATEGY_CONFIG.** Ray's prose described the strategy as signal-scaling (P2) but the v4
   tournament winner is P1 (long/cash binary). The config is wired to the v4 winner
   (S2c_zscore_36m / T3_z0.0 / P1 / L1) as required. All runtime metrics (Sharpe, MDD,
   return) are loaded from `winner_summary.json` at runtime — no hardcoded values.

5. **pair_registry.py.** Added routing entry `"hy_ig_spy_v4_from_scratch": "pages/16_hy_ig_spy_v4_from_scratch"`
   and indicator name mapping `"hy_ig_spy_v4_from_scratch": "HY-IG Credit Spread"`. The registry
   auto-discovers `interpretation_metadata.json` and `evidence_status.json` at runtime;
   the `failed_final_exam` status badge renders automatically via the landing page card logic.

---

## Known Gaps for Quincy

1. **Observation/interpretation/key_message text is hedge-forward.** Ray's source prose had
   `[PLACEHOLDER]` for these fields in all 5 evidence blocks. I wrote reader-safe prose that
   defers to the chart for specific numbers rather than fabricating findings. Quincy should
   review whether the language meets the evidence-grade language standard (RES-EGL1) or
   whether Ray needs a follow-on pass to add specific v4 findings from Evan's artifacts.

2. **STRATEGY_CONFIG.MANUAL_USE_MD** uses the z-score signal description (correct for v4),
   not the HMM probability description from Ray's v4 narrative prose. Ray's prose was written
   before the tournament ran and described the signal-scaling family (P2 + HMM). Ace adjusted
   to match the actual v4 winner (P1 + z-score). Quincy should verify the plain-English
   strategy description is accurate per the winner_summary.json.

3. **No live execution panel.** `live_execution_snapshot.json` does not exist for this pair;
   per Rule 3.10 the live section is omitted entirely. Correct.

---

*App Dev Ace — 2026-05-12*
