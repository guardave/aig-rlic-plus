# META-DM Consequential Review — hy_ig_v2_spy
**Date:** 2026-05-08  
**Agent:** App Dev Ace  
**Trigger:** evidence_status promoted to `passed_final_exam`; oos_split_record dates updated to three-period split

---

## Changes Reviewed

| Field | Old | New |
|-------|-----|-----|
| evidence_status.status | found_in_search | passed_final_exam |
| Validation OOS | 2018-01-01 to 2025-12-31 (8 yr) | 2018-10-01 to 2024-12-31 (6 yr / 75 mo) |
| Holdout | none | 2025-01-01 to 2025-12-31 (261 days) |
| oos_year_count | MISSING | 6 |

---

## Findings

### `oos_split_record.json`
- `oos_year_count` field was absent. **Added: 6** (authoritative field per ECON-OOS1 for Ray's narrative).

### `evidence_status.json`
- Already correct (`passed_final_exam`). No portal-side changes needed for the badge; it reads dynamically from the JSON.

### `app/pair_configs/hy_ig_spy_config.py`
- No hard-coded OOS dates or year counts for hy_ig_v2_spy found. The `tournament_intro` references the old validation window label ("2019-10-01 → 2026-04-22") — this is the tournament ranking window, not the split dates, and is accurate to the tournament run. **No change made.**

### `app/pages/9_hy_ig_v2_spy_story.py` — FIXED
Hard-coded stale values replaced:
- H2 headline: "8-year OOS" → "6-year OOS"; Sharpe 1.27 → 1.41
- Key metrics block: "2018-2025" → "2018-10 to 2024-12"; updated Sharpe, MDD, added final exam note
- KPI card: `st.metric("OOS Test Period", "8 years", delta="2018-2025")` → `"6 years"` / `"2018-10 to 2024-12"`
- Caption under KPI cards: "8-year out-of-sample window" → "6-year validation window"; added sealed 2025 exam pass note
- Headline Finding #5: rewritten from "8 years (2018-2025)" to "6 years (2018-10 to 2024-12)" with holdout exam detail

### `app/pages/9_hy_ig_v2_spy_methodology.py` — FIXED
- Sample period metrics: replaced two-column (IS / OOS) with four-column layout (Full / IS / Validation OOS / Holdout)
- OOS metric was `"2018-01 to 2025-12"` (wrong) → now shows correct three-period split
- Caption: "8-year out-of-sample" → "75-month validation window (6 years)" with holdout exam pass note

---

## Acceptance Check Results (verbatim)

```
$ python3 -c "import json; d=json.load(open('results/hy_ig_v2_spy/evidence_status.json')); print(d['status'])"
passed_final_exam

$ python3 -c "import json; d=json.load(open('results/hy_ig_v2_spy/oos_split_record.json')); print('oos_year_count:', d.get('oos_year_count', 'MISSING'))"
oos_year_count: 6

$ grep -r "8.year\|2018-01-01\|2025-12-31" app/pair_configs/ 2>/dev/null | grep "hy_ig_v2" | head -5
(no output — clean)
```

## Playwright Browser Checks (headless, port 8501)
```
LANDING: passed_final_exam label FOUND
LANDING: no stale 8-year/2018-2025 text (OK)
STORY: no stale 8-year text (OK)
STORY: no stale 2018-2025 text (OK)
STORY: no search-grade language (OK)
```

---

## Files Modified

| File | Change |
|------|--------|
| `results/hy_ig_v2_spy/oos_split_record.json` | Added `oos_year_count: 6` |
| `app/pages/9_hy_ig_v2_spy_story.py` | Fixed 5 hard-coded stale OOS year/date references |
| `app/pages/9_hy_ig_v2_spy_methodology.py` | Replaced stale two-period sample metrics with correct three-period layout |

## Files Confirmed Accurate (no change needed)

| File | Verdict |
|------|---------|
| `results/hy_ig_v2_spy/evidence_status.json` | Already `passed_final_exam` |
| `app/components/evidence_status.py` | Reads JSON dynamically — no hard-code |
| `app/app.py` | Reads evidence_status dynamically — no hard-code |
| `app/pair_configs/hy_ig_spy_config.py` | No hy_ig_v2_spy OOS date hard-codes found |

---

**Status: COMPLETE — all META-DM obligations fulfilled.**
