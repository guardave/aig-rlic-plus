# Smoke-log verification — 2026-05-13

QA verification of three loader smoke-test logs committed by Ace
(`app/_smoke_tests/`). Cross-checked each log's declared page list against
the current state of `app/pages/`.

## Per-log results

### 1. `loader_hy_ig_spy_v3_rerun_20260511.log`
- **Footer:** `RESULT  passes=4  failures=0` — OK
- **Pages listed:**
  - `app/pages/90_hy_ig_spy_v3_rerun_evidence.py`
  - `app/pages/90_hy_ig_spy_v3_rerun_methodology.py`
  - `app/pages/90_hy_ig_spy_v3_rerun_story.py`
  - `app/pages/90_hy_ig_spy_v3_rerun_strategy.py`
- **Reality check:** NONE of these page files currently exist under
  `app/pages/`. Only `app/pair_configs/hy_ig_spy_v3_rerun_config.py` remains.
  The `90_*` page set was retired (likely in v4 from-scratch cutover).
- **Verdict:** **WARN** — log is a historical 2026-05-11 artefact; passes
  reflect the state at that timestamp. The page files were removed after
  the log was captured. Log is valuable as a historical record but does
  NOT reflect today's `app/pages/` contents. Recommend annotating log
  filename with `_historical_` prefix or moving to `_archive/`.

### 2. `loader_hy_ig_spy_v3_retro_20260511.log`
- **Footer:** `RESULT  passes=4  failures=0` — OK
- **Pages listed:**
  - `app/pages/91_hy_ig_spy_v3_retro_evidence.py`
  - `app/pages/91_hy_ig_spy_v3_retro_methodology.py`
  - `app/pages/91_hy_ig_spy_v3_retro_story.py`
  - `app/pages/91_hy_ig_spy_v3_retro_strategy.py`
- **Reality check:** NONE of these `91_*` page files currently exist under
  `app/pages/`. Only `app/pair_configs/hy_ig_spy_v3_retro_config.py` remains.
- **Verdict:** **WARN** — same situation as v3_rerun. Historical artefact;
  pages have since been retired. Same remediation suggested.

### 3. `loader_hy_ig_spy_v4_from_scratch_20260512.log`
- **Footer:** `RESULT  passes=6  failures=0` — OK
- **Pages listed:**
  - `app/pages/16_hy_ig_spy_v4_from_scratch_evidence.py` — EXISTS
  - `app/pages/16_hy_ig_spy_v4_from_scratch_methodology.py` — EXISTS
  - `app/pages/16_hy_ig_spy_v4_from_scratch_story.py` — EXISTS
  - `app/pages/16_hy_ig_spy_v4_from_scratch_strategy.py` — EXISTS
- All 6 PASS lines target `app/pair_configs/hy_ig_spy_v4_from_scratch_config.py`,
  which also exists.
- **Verdict:** **PASS** — page list matches reality; footer clean.

## Summary

| Log | Passes/Fails | Pages match reality | Verdict |
|---|---|---|---|
| v3_rerun | 4 / 0 | No (pages retired post-log) | WARN |
| v3_retro | 4 / 0 | No (pages retired post-log) | WARN |
| v4_from_scratch | 6 / 0 | Yes | PASS |

## Note for Lead

The two v3 WARN verdicts are NOT a Wave 10J/v4 regression — they are
historical 2026-05-11 logs preserved as evidence of the prior state.
The actual retirement of `90_*` and `91_*` page files happened as part
of the v4 from-scratch cutover and is correct. Suggestion: rename these
two logs with a `historical_` prefix or move them to an `_archive/`
subfolder under `app/_smoke_tests/` to make their archival nature
explicit and prevent future confusion.

— Quincy QA, 2026-05-13
