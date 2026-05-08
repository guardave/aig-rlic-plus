# META-DM Consequential Review — hy_ig_v2_spy
**Date:** 2026-05-08  
**Reviewer:** Research Ray  
**Trigger:** oos_split_record.json and evidence_status.json changed (two-period → three-period split, evidence status → passed_final_exam)

---

## Summary

- **Findings identified:** 9 distinct claim locations requiring update
- **Changes applied:** 9 edits to `docs/portal_narrative_hy_ig_v2_spy_20260410.md`
- **Acceptance checks:** Both passed — 0 matches for stale figures and stale evidence language

---

## Findings and Changes Applied

| # | Line (pre-edit) | Issue | Action |
|---|-----------------|-------|--------|
| 1 | 6 (YAML rationale) | Cited oos_sharpe 1.274, 2018-2025, 8-year OOS as source values | Updated rationale to reflect three-period split, validation Sharpe 1.87, holdout Sharpe 2.35, passed_final_exam status |
| 2 | 81 (YAML headline) | `Sharpe 1.27 over 8-year OOS` | Updated to `Sharpe 1.87 over 6-year validation OOS` |
| 3 | 234 (section heading) | `Sharpe 1.27 over 8-year OOS` | Updated to `Sharpe 1.87 over 6-year validation OOS` |
| 4 | 236 | `Key metrics (out-of-sample 2018-2025)` | Updated to `out-of-sample validation 2018-2024` |
| 5 | 238 | `Sharpe ratio: 1.27` | Updated to `1.87`; added holdout bullet (Sharpe 2.35, MDD −4.1%) |
| 6 | 265 | `8 years (2018-2025) … 1.27 Sharpe … not proof` | Updated to 6-year validation, 1.87 Sharpe, added confirmation test language |
| 7 | 474 (HMM methodology) | `let the HMM classify 2018-2025 cold` | Updated to `2018 onward cold` — methodology prose, range still correct but no longer anchors to stale end date |
| 8 | 588 (tournament prose) | `over 2018-2025` (tournament ranking window) | Updated to `2018-2024` |
| 9 | 639 (strategy table) | `OOS Sharpe Ratio (2018-2025) \| 1.27` | Updated to validation 2018-2024 \| 1.87; added holdout row (2025 \| 2.35) |
| 10 | 579 (quartile comparison) | `OOS Sharpe 1.27` (comparison to quartile 1.45) | Removed the stale absolute figure; reworded to avoid citing the superseded number |
| 11 | 645 (strategy interpretation) | `Sharpe ratio of 1.27` | Updated to validation Sharpe 1.87; added sealed confirmation test sentence |

---

## Items Flagged for Lead Judgment

**None requiring blocking Lead decision.**

One judgment call made without escalation: line 474 (HMM methodology deep-dive) described the out-of-sample classification window as "2018-2025." The HMM is fitted on 2000-2017 IS data only and classifies forward — the classification window now spans 2018 through end of holdout (2025-12-31), so the statement was factually accurate but anchored to a stale end date that matched the old OOS boundary. Changed to "2018 onward" which is correct regardless of where the period ends and avoids implying a specific boundary.

The ARIMA sample reference on line 523 (`2000-01-03 to 2025-12-31, N = 6,782`) was not changed — this refers to the full estimation sample for the pre-whitening filter, not the OOS window, and is a methodology description rather than a performance claim. Lead should confirm whether the ARIMA was in fact fitted on the full sample including 2025 data or only through end-2024; if the latter, line 523 needs a separate update.

---

## Acceptance Check Output (verbatim)

```
$ grep -n "1\.27\|1\.274\|2018-2025\|8-year OOS\|8 year" docs/portal_narrative_hy_ig_v2_spy_20260410.md | head -20
[no output]
$ grep -n "not yet confirmed\|search.grade\|discovery.grade\|best rule found" docs/portal_narrative_hy_ig_v2_spy_20260410.md | head -10
[no output]
```

Both return 0 matches. Review complete.
