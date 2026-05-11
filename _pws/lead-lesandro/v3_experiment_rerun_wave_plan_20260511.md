# Wave Plan: V3-EXP-RERUN — Full Rebuild of hy_ig_spy v3 Experiment Forks
**Date:** 2026-05-11
**Lead:** Lesandro
**Status:** OPEN

## Motivation

The first v3 experiment build (2026-05-09) had two structural problems:

1. **Incomplete portal build.** Only Story pages were built for both forks. Evidence, Strategy, and Methodology pages were never created — all four page links 404. No one verified the links before handoff (pre-META-CDR gap).
2. **SOP state was stale.** The build predated META-CDR (cross-domain review), the corrected ECON-OOS4 retro-apply constraint SOP language, and the evidence_status.json schema fixes. The pipeline and portal artifacts should reflect the current SOP baseline.

**Goal:** Experiment comparison — 4 correct, linkable pages per fork, concise narrative, full chart set. Not production-quality polish; the point is a valid, honest rerun-vs-retro comparison.

## What exists and is KEPT

- `results/hy_ig_spy_v3_rerun/tournament_results_rerun_20260509.csv` — 2143 rows, valid
- `results/hy_ig_spy_v3_retro/tournament_results_retro_20260509.csv` — valid
- `results/hy_ig_spy_v3_rerun/oos_split_record.json` — valid three-period split
- `results/hy_ig_spy_v3_retro/oos_split_record.json` — valid three-period split
- `results/hy_ig_spy_v3_rerun/interpretation_metadata.json` — valid (schema-conforming)
- `results/hy_ig_spy_v3_retro/interpretation_metadata.json` — valid (schema-conforming)
- `results/hy_ig_spy_v3_rerun/evidence_status.json` — fixed 2026-05-11 (schema-conforming)
- `results/hy_ig_spy_v3_retro/evidence_status.json` — fixed 2026-05-11 (schema-conforming)
- `scripts/pair_pipeline_hy_ig_spy_v3_rerun.py` — kept for reference; Evan may re-run to fix DSR/bootstrap anomalies

## Known issues to resolve in this wave

| # | Issue | Owner |
|---|-------|-------|
| 1 | Evidence, Strategy, Methodology pages missing for both forks (404) | Ace |
| 2 | pair_configs missing for both forks (`app/pair_configs/`) | Ace |
| 3 | DSR p-value = 0.0000 exactly in rerun (likely numerical underflow) | Evan |
| 4 | Bootstrap CI lower = -1.19 with observed Sharpe 0.85 (suspicious width) | Evan |
| 5 | `val_sharpe` column name in retro CSV vs `oos_sharpe` in rerun CSV (inconsistency) | Evan (retro re-run) |
| 6 | No charts beyond equity_curves_holdout for either fork | Vera |
| 7 | No Ray narrative on any Evidence, Strategy, or Methodology page | Ray |

## Scope: what each agent must deliver

### Evan (re-run pipelines)
- Re-run `pair_pipeline_hy_ig_spy_v3_rerun.py` to fix issues #3 and #4. Investigate DSR underflow — if n_trials_effective=150 and expected_max_sr=2.67, a p-value of exactly 0.0 indicates a computation error (likely `norm.cdf` underflow — use `norm.logsf` or clamp). Fix bootstrap width issue if found.
- Re-run retro pipeline (or produce a corrected CSV) so that the column name is `oos_sharpe` consistent with the rerun CSV schema.
- Re-generate: `tournament_results_*.csv`, `winner_summary.json`, `oos_split_record.json`, `final_exam_results_*.json`, `evan_handoff_*.md` for both forks.
- Handoff note must include: winner rule, split dates, ECON-FE1 condition table, and explicit `econ_oos4: true` flag.

### Vera (charts)
For each fork, produce the **experiment-comparison minimum chart set**:
- `equity_curves_holdout` — already exists; re-generate if Evan re-runs
- `equity_curves_validation` — winner rule equity curve on validation window vs B&H
- `signal_distribution` — histogram/density of the indicator signal used
- `drawdown_comparison` — strategy vs B&H drawdown on holdout window

All charts: JSON + `_meta.json` sidecar with `disposition: consumed`. No perceptual PNG required for experiment forks (not production pairs).

Handoff note to Ray must name each chart file produced.

### Ray (narratives)
For each fork, write concise experiment-framed narrative for:
- **Evidence page** — what the data shows, 3-4 key observations, one chart callout per method
- **Strategy page** — winner rule in plain English, entry/exit logic, experiment caveat ("winner inherited via retro-apply" for retro fork per ECON-OOS4)
- **Methodology page** — three-period split design, ECON-FE1 conditions table, experiment status

Narrative must be concise (experiment comparison, not production pair). All instrument references must match `interpretation_metadata.json` (`indicator_id: hy_ig_spread_pct`, `target_symbol: SPY`). RES-NR1 whitelist check required before handoff.

Handoff note to Ace must name each narrative section.

### Ace (portal pages)
For each fork (`90_hy_ig_spy_v3_rerun`, `91_hy_ig_spy_v3_retro`), build:
- `*_evidence.py`
- `*_strategy.py`
- `*_methodology.py`

These pages already have a Story page — do NOT modify the story pages.

Also create `app/pair_configs/hy_ig_spy_v3_rerun_config.py` and `hy_ig_spy_v3_retro_config.py` using the production `hy_ig_spy_config.py` as structural reference.

After building, **click every link** on every page of both forks and confirm no 404s. Log link check in handoff note.

### Lead CDR (Step 10 — before Quincy)
- Confirm all 8 pages exist (4 per fork) and links resolve
- Confirm tournament CSV column names are consistent across forks
- Spot-check: winner Sharpe in story page matches `winner_summary.json`
- Spot-check: evidence_status.json `status` field matches story page badge
- CDR PASS required before Quincy is invoked

### Quincy (QA)
- cloud_verify.py on both forks
- GATE-NR check on both forks
- Link audit: all 8 pages load without error
- Confirm no `val_sharpe` / `oos_sharpe` inconsistency in displayed metrics

## Dispatch order

```
Step 1: Evan (re-run pipelines, fix DSR/bootstrap) — blocking for Vera
Step 2: Vera (charts) — parallel with Ray once Evan delivers
Step 2: Ray (narratives, concurrent with Vera)
Step 3: Ace (portal pages + pair_configs) — after Vera + Ray
Step 4: Lead CDR — after Ace
Step 5: Quincy QA — after Lead CDR PASS
```

## Acceptance commands

**Positive:**
```bash
# All 8 pages exist
ls app/pages/{90,91}_hy_ig_spy_v3_{rerun,retro}_{evidence,strategy,methodology}.py | wc -l
# → 6 (evidence + strategy + methodology × 2 forks)

# pair_configs exist
ls app/pair_configs/hy_ig_spy_v3_{rerun,retro}_config.py | wc -l
# → 2

# No exact-zero DSR p-value in rerun final_exam
python3 -c "import json; d=json.load(open('results/hy_ig_spy_v3_rerun/final_exam_results_$(ls results/hy_ig_spy_v3_rerun/final_exam_results_*.json | grep -o '[0-9]*').json')); print(d.get('dsr_pvalue', 'missing'))"
# → non-zero float

# Column name consistent
python3 -c "import pandas as pd; [print(p, 'oos_sharpe' in pd.read_csv(p).columns) for p in ['results/hy_ig_spy_v3_rerun/tournament_results_rerun_$(ls results/hy_ig_spy_v3_rerun/tournament_results*.csv | grep -o [0-9]*).csv', 'results/hy_ig_spy_v3_retro/tournament_results_retro_$(ls results/hy_ig_spy_v3_retro/tournament_results*.csv | grep -o [0-9]*).csv']]"
# → both True
```

**Negative:**
```bash
# Story pages not modified
git diff HEAD~1 -- app/pages/90_hy_ig_spy_v3_rerun_story.py app/pages/91_hy_ig_spy_v3_retro_story.py | wc -l
# → 0 (no changes)
```
