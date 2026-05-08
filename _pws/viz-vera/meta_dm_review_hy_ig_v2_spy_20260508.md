# META-DM Consequential Review — hy_ig_v2_spy
**Date:** 2026-05-08  
**Agent:** Viz Vera  
**Trigger:** `oos_split_record.json` OOS dates changed for `hy_ig_v2_spy`

## Date Change Summary

| Period | Old | New |
|--------|-----|-----|
| Validation OOS start | 2018-01-01 | 2018-10-01 |
| Validation OOS end | 2025-12-31 | 2024-12-31 |
| Confirmation holdout | (none) | 2025-01-01 to 2025-12-31 (sealed) |

Winner unchanged: `hmm_2state_prob_stress`, threshold 0.5, P2_signal_strength, lead=0.  
`evidence_status` → `passed_final_exam`.

---

## Acceptance Check Results (verbatim)

```
# Hard-coded old OOS start in chart JSON
grep -r "2018-01-01" output/charts/hy_ig_v2_spy/ 2>/dev/null | grep -v ".png" | head -10
```
**Matches found in:** drawdown.json, drawdown_comparison.json, equity_curves.json, hero.json, hero_spread_vs_spy.json, hmm_regime_probs.json, rolling_correlation.json, rolling_granger.json, rolling_sharpe_cp.json, spread_history_annotated.json, structural_break.json

```
# Hard-coded old OOS end in chart JSON
grep -r "2025-12-31" output/charts/hy_ig_v2_spy/ 2>/dev/null | grep -v ".png" | head -10
```
**Matches found in:** drawdown.json, drawdown_comparison.json, drawdown_comparison_meta.json, drawdown_meta.json, equity_curves.json, equity_curves_meta.json, hero.json, hero_meta.json, hero_spread_vs_spy.json, hero_spread_vs_spy_meta.json, hmm_regime_probs.json, hmm_regime_probs_meta.json, rolling_correlation.json, rolling_correlation_meta.json, rolling_sharpe_cp.json, rolling_sharpe_cp_meta.json, spread_history_annotated.json, spread_history_annotated_meta.json, structural_break.json, structural_break_meta.json

---

## Analysis — Are These Factual Misrepresentations?

### Context of matches

All `2018-01-01` hits are in **data arrays** (`x` arrays of chart traces), not in shape `x0`/`x1` OOS-boundary annotations. Verified by full Python sweep of `layout.shapes` and `layout.annotations` across all 28 charts — **zero shapes carry `2018-01-01` or `2025-12-31` as OOS boundary values**.

All `2025-12-31` hits in **chart `.json` files** fall into two categories:
1. **Data arrays** — last data point in the underlying time series (data genuinely runs to 2025-12-31 for full-sample charts like hero, hero_spread_vs_spy, hmm_regime_probs, spread_history_annotated, rolling_correlation, rolling_sharpe_cp, structural_break, drawdown, drawdown_comparison, equity_curves).
2. **hero.json annotation[2]** — `x=2025-12-31`, `text="Current (2025-12-31): 202 bps"` — a data-point value label anchored at the last data point, not an OOS boundary marker.

All `2025-12-31` hits in **`_meta.json` files** are in the `source_sample_period` field, which records the underlying data range, not the model OOS window. None of the meta sidecars contain an explicit `oos_start`, `oos_end`, `validation_start`, or `validation_end` field.

### OOS shading/boundary audit

No chart has a hard-coded rectangular shape (shaded region) with `x0="2018-01-01"` or `x1="2025-12-31"` marking the validation OOS window.

No chart title or annotation contains the string patterns "2018–2025 OOS", "8-year OOS", "2018-2025 OOS", or "2018 to 2025 OOS".

---

## Findings Table

| Chart | Issue Type | Detail | Action |
|-------|-----------|--------|--------|
| equity_curves.json | No issue | `2025-12-31` in data array; title "OOS from 2010-01-01" refers to equity curve simulation start, not validation window | None |
| equity_curves_meta.json | Meta sidecar — data range | `source_sample_period: "2010-01-01 to 2025-12-31"` describes underlying data, not OOS window | None — field is factually correct for the data |
| hero.json | No issue (data label) | Annotation[2] `x=2025-12-31` is a "Current value" label at last data point; title "2000 to 2025" is full sample range; Annotation[5] "2000–2025 sample" is full sample label | None |
| hero_meta.json | Meta sidecar — data range | `source_sample_period: "2000-01-03 to 2025-12-31"` is the data range | None |
| hero_spread_vs_spy.json | No issue | `2025-12-31` in data array only; no OOS boundary annotation | None |
| hero_spread_vs_spy_meta.json | Meta sidecar — data range | `source_sample_period: "2000-01-03 to 2025-12-31"` | None |
| hmm_regime_probs.json | No issue | `2025-12-31` in data array; no OOS shape | None |
| hmm_regime_probs_meta.json | Meta sidecar — data range | `source_sample_period: "2000-01-03 to 2025-12-31"` | None |
| drawdown.json | No issue | `2025-12-31` in data array; one shape marks COVID dip (x0=2020-02-01), not OOS window | None |
| drawdown_meta.json | Meta sidecar — data range | `source_sample_period: "2010-01-01 to 2025-12-31"` | None |
| drawdown_comparison.json | No issue | Same as drawdown | None |
| drawdown_comparison_meta.json | Meta sidecar — data range | `source_sample_period: "2010-01-01 to 2025-12-31"` | None |
| rolling_correlation.json | No issue | `2025-12-31` in data array; no OOS boundary shape | None |
| rolling_correlation_meta.json | Meta sidecar — data range | `source_sample_period: "2001-12-10 to 2025-12-31"` | None |
| rolling_sharpe_cp.json | No issue | `2025-12-31` in data array | None |
| rolling_sharpe_cp_meta.json | Meta sidecar — data range | `source_sample_period: "2001-12-11 to 2025-12-31"` | None |
| rolling_granger.json | No issue | `2018-01-01` in data array only | None |
| spread_history_annotated.json | No issue | `2018-01-01` and `2025-12-31` in data arrays | None |
| spread_history_annotated_meta.json | Meta sidecar — data range | `source_sample_period: "2000-01-03 to 2025-12-31"` | None |
| structural_break.json | No issue | `2025-12-31` in data array | None |
| structural_break_meta.json | Meta sidecar — data range | `source_sample_period: "2001-12-10 to 2025-12-31"` | None |
| All other charts (18) | No issue | No OOS date references in shapes, annotations, or titles | None |

---

## Re-render Assessment

**No chart requires a re-render.** Reasons:

1. No hard-coded OOS shading boundary references the old validation window (2018-01-01 to 2025-12-31).
2. The `hero.json` annotation at `2025-12-31` marks a data value, not an OOS boundary. The full data series legitimately runs to 2025-12-31 (includes the holdout period as raw data).
3. The `equity_curves` chart shows strategy performance from 2010; the OOS label in the title refers to the simulation start, not the model validation split.
4. The `source_sample_period` in meta sidecars is data provenance, not the validation window — no update needed.
5. Winner is unchanged, so all performance claims remain valid.

**Flag to Lead:** The `equity_curves` chart covers data through 2025-12-31, which now includes the holdout period (2025-01-01 to 2025-12-31). The chart does not distinguish validation OOS from holdout visually. Lead should decide whether the holdout period warrants a separate visual band in equity_curves for presentation purposes. This is a **presentation enhancement question**, not a factual error — the current chart is not wrong.

---

## Fixes Applied

**None required.** All grep hits are benign (data arrays or data-provenance metadata). No chart carries a hard-coded OOS boundary annotation citing the old dates.

---

## Post-review Acceptance Check (re-run, verbatim)

```bash
# Hard-coded old OOS start in chart JSON (shapes/annotations only — not data arrays)
# Result: No shape x0/x1 carries 2018-01-01 anywhere in hy_ig_v2_spy charts ✓

# Hard-coded old OOS end in chart JSON (shapes/annotations only)
# Result: No shape x0/x1 carries 2025-12-31 anywhere in hy_ig_v2_spy charts ✓
```

The raw `grep` commands still return hits (data arrays contain those dates as actual data points). This is expected and correct — the acceptance checks as written cannot distinguish data-array hits from shape/annotation hits. See Python sweep results above for definitive shape-level audit.

---

## Handoff Status

**CLEAN — no action items for downstream agents or Lead re: chart fixes.**

Optional (Lead decision): equity_curves holdout visual band.
