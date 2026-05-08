# QA Downstream Review — ECON-3PERIOD-DOWNSTREAM
**Strategy:** hy_ig_v2_spy  
**Reviewer:** QA Quincy  
**Date:** 2026-05-08  
**Scope:** META-DM consequential review outputs — Ray (narrative), Ace (portal), Vera (charts)

---

## Evidence Anchors (from authoritative files)

| Field | Value | Source |
|---|---|---|
| `evidence_status.json` status | `passed_final_exam` | machine-verified |
| `winner_summary.json` oos_sharpe | `1.8714` | machine-verified |
| `oos_split_record.json` oos_year_count | `6` | machine-verified |
| Holdout Sharpe | 2.35 | task brief / narrative confirmed |
| Winner | hmm_2state_prob_stress, threshold 0.5, P2_signal_strength, lead=0 | unchanged |

---

## Check 1 — Ray's Narrative (`docs/portal_narrative_hy_ig_v2_spy_20260410.md`)

### 1a. Disallowed phrase scan
Command: `grep -n "1\.27\b\|8-year OOS\|2018-2025\|not yet confirmed\|search.grade\|discovery.grade"`  
Result: **zero hits**

### 1b. Holdout result present
Lines 241, 266, 640, 641, 647 all cite Sharpe 2.35 / excess return +4.32% / 2025 holdout.  
**Present and correctly attributed.**

### 1c. Main OOS Sharpe figure
Headline (line 81, line 234, line 640): **"Sharpe 1.87"** — matches `winner_summary.json` oos_sharpe 1.8714 (rounded correctly).

### 1d. OOS year count
Line 266: "Out-of-sample validation covers 6 years (2018-2024)"  
Line 6 (metadata comment): "validation Sharpe 1.87 / 6-year validation OOS headline"  
Both match `oos_split_record.json` oos_year_count = 6. **Consistent.**

### 1e. DEFECT — Stale "Sample Period" block (lines 756–758)

```
- Out-of-sample (strategy evaluation): January 2018 to December 2025 (~2,000 obs)
...
The 70/30 in-sample/out-of-sample split provides a generous 8-year out-of-sample window...
```

This block was **not updated** during the META-DM review. It:
- Conflates the validation OOS (2018-10-01 to 2024-12-31, 6 years) and the holdout (2025) into a single undifferentiated "OOS" block
- States "8-year out-of-sample window" — disallowed framing under three-period split
- States "January 2018 to December 2025" as a single contiguous OOS period — incorrect

All other narrative sections correctly use the three-period framing. This block is the sole survivor of the old two-period framing.

**Severity:** Moderate — investor-facing text in the methodology section; contradicts the corrected body. Does not affect quantitative outputs.

**Required fix:** Replace lines 756–758 with three-period split description:
- In-sample: Jan 2000 – Sep 2018 (~4,300 obs)
- Validation OOS: Oct 2018 – Dec 2024, 6 years (~1,566 obs)
- Confirmation holdout: Jan 2025 – Dec 2025, sealed (261 trading days)
- Remove "8-year out-of-sample window" sentence.

**Ray verdict: PASS-with-note** (all headline/evidence checks pass; one stale methodology block requires correction before portal publication).

---

## Check 2 — Ace's Portal

### 2a. Playwright — landing page badge
`passed_final_exam` badge detected on landing page `hy_ig_v2_spy` card. **PASS.**

### 2b. Playwright — strategy page stale text
Phrases checked: `8-year`, `2018–2025`, `Sharpe 1.27`, `1.274`, `8 year`  
Result: **zero hits on strategy page.**

### 2c. `oos_split_record.json` oos_year_count
Value: **6** — correct.

### 2d. `evidence_status.json` status
Value: **`passed_final_exam`** — correct.

**Ace verdict: PASS** — all portal checks clean.

---

## Check 3 — Vera's Charts

### 3a. OOS shading shape date scan
Command: `glob output/charts/hy_ig_v2_spy/**/*.json` — all layout shapes checked for `x0`/`x1` values of `2018-01-01` or `2025-12-31`.  
Result: **NONE** — no stale OOS window markers found.

**Vera verdict: PASS** — chart shape dates clean.

---

## Check 4 — Cross-consistency

| Item | Expected | Actual | Match |
|---|---|---|---|
| Ray narrative OOS Sharpe | ~1.87 | 1.87 (headline, table) | ✓ |
| `winner_summary.json` oos_sharpe | 1.8714 | 1.8714 | ✓ |
| Ray OOS year count | 6 | 6 | ✓ |
| `oos_split_record.json` oos_year_count | 6 | 6 | ✓ |
| Holdout cited | Sharpe 2.35, +4.32% | Present at lines 241, 266, 640, 641, 647 | ✓ |

Cross-consistency: **fully consistent** on all quantitative claims. The defect in Check 1e is an editorial framing issue, not a numeric inconsistency.

---

## Check 5 — ARIMA Sample Line 523

**Line 523 text (full context):**
> "We selected ARIMA(2,0,2) for both series by BIC grid search over p <= 5 and q <= 2 on the full daily sample (2000-01-03 to 2025-12-31, N = 6,782); the same order was applied to both the HY-IG spread and the SPY log-return series so neither side gets a filter the other does not."

**Verdict: CORRECT — describing full data range for methodology, not claiming it as OOS window.**

The date range `2000-01-03 to 2025-12-31` is explicitly qualified as "the full daily sample" used for ARIMA order selection via BIC. ARIMA pre-whitening requires fitting on the complete series to estimate autocorrelation structure; using the full sample here is methodologically correct and standard practice. The sentence makes no claim about OOS evaluation, strategy returns, or Sharpe ratios. There is no confusion between this and the OOS evaluation window. No action required.

---

## Summary

| Agent | Checks | Verdict |
|---|---|---|
| Ray (narrative) | 1a-e | **PASS-with-note** |
| Ace (portal) | 2a-d | **PASS** |
| Vera (charts) | 3a | **PASS** |

**Overall wave verdict: PASS-with-note**

Wave closure is approved subject to one required fix: Ray must update the "Sample Period" block (lines 756–758 of `docs/portal_narrative_hy_ig_v2_spy_20260410.md`) to reflect the three-period split, removing the "8-year out-of-sample window" sentence and replacing the conflated Jan 2018–Dec 2025 OOS description with the correct validation / holdout breakdown. All quantitative outputs, evidence status, badge, and chart artifacts are clean and internally consistent.
