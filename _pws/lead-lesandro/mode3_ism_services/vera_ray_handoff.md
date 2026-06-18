# Handoff: Viz Vera + Research Ray -> Lead Lesandro / Ace

**Date:** 2026-06-18  
**Mode:** Mode 3 maker dispatch  
**Pair:** `ism_services_spy`  
**Brief:** `_pws/lead-lesandro/mode3_ism_services/briefs/vera_ray_brief.md`

## Vera Chart Artifacts

Output directory: `output/charts/ism_services_spy/plotly/`

Produced chart JSON + `_meta.json` sidecars + `_perceptual_check_*.png`:

- `hero`
- `equity_curves`
- `drawdown`
- `correlation_heatmap`
- `ccf_prewhitened`
- `granger_f_by_lag`
- `hmm_regime_probs`
- `local_projections`
- `returns_by_regime`
- `history_zoom_dotcom`
- `history_zoom_gfc`
- `history_zoom_covid`
- `history_zoom_inflation_2022`
- `quantile_coef`
- `regime_stats`
- `rolling_correlation`
- `structural_break`
- `subperiod_sharpe`
- `tournament_scatter`
- `tournament_sharpe_dist`
- `transfer_entropy`
- `walk_forward`

Skip sidecars:

- `chart_skip_rolling_sharpe_cp.json`
- `chart_skip_rolling_granger.json`

## Vera Validation

Commands run:

```bash
python3 scripts/generate_charts_ism_services_spy.py
python3 scripts/generate_strategy_perf_charts.py --no-subperiod ism_services_spy
python3 <inline VIZ-CV1 chart rendering validation>
```

VIZ-CV1 log: `output/charts/ism_services_spy/plotly/_smoke_test_20260618.log`

Result:

```text
Total: 22 charts, 22 pass, 0 fail
```

Sidecar / perceptual PNG coverage: PASS for all 22 non-sidecar chart JSON files.

VIZ-DP1 gate:

```text
VIZ-DP1 PASS [regime_stats]
VIZ-DP1 PASS [returns_by_regime]
VIZ-DP1 PASS [local_projections]
VIZ-DP1 PASS [history_zoom_dotcom]
VIZ-DP1 PASS [history_zoom_gfc]
VIZ-DP1 PASS [history_zoom_covid]
VIZ-DP1 PASS [history_zoom_inflation_2022]
```

Perceptual spot-checks performed:

- `hero`: 50 diffusion-index line visible; contrarian buy markers visible.
- `granger_f_by_lag`: both directions visible; reverse `SPY -> ISM Services PMI` dominates visually and analytically.
- `history_zoom_gfc`: both panels nonblank; event markers and NBER shading span both panels.

## Ray Narrative Artifacts

Narrative path:

- `docs/portal_narrative_ism_services_spy_20260618.md`

Updated metadata:

- `results/ism_services_spy/interpretation_metadata.json`

Ray-owned metadata fields filled/updated:

- `strategy_objective`: `min_mdd`
- `expected_direction`: remains `procyclical`
- `mechanism`: states the contrarian mean-reversion hypothesis cautiously.
- `caveats`: includes reverse causality, IS/OOS inversion, episode concentration, bootstrap p=0.073, found_in_search, structural break, and return tradeoff.
- `narrative_summary`: states drawdown overlay, not evidence that ISM leads SPY.

## Ray Validation

Commands run:

```bash
python3 scripts/validate_schema.py \
  --schema docs/schemas/narrative_frontmatter.schema.json \
  --instance /tmp/frontmatter_ism_services_spy.json

python3 scripts/validate_schema.py \
  --schema docs/schemas/interpretation_metadata.schema.json \
  --instance results/ism_services_spy/interpretation_metadata.json
```

Results:

```text
OK: /tmp/frontmatter_ism_services_spy.json conforms to docs/schemas/narrative_frontmatter.schema.json
OK: results/ism_services_spy/interpretation_metadata.json conforms to docs/schemas/interpretation_metadata.schema.json
direction/objective check PASS
```

RES-NR1 check:

- `target_symbol=SPY`
- Narrative references verified: `SPY`, `S&P 500`, `ISM Services PMI`.
- S&P 500 references are benchmark/target proxy references for SPY, not copied claims from another pair.

RES-JFU check:

- Story, Evidence, Strategy, and Methodology each expand first-use technical terms and abbreviations in-section.
- The narrative explicitly states the natural procyclical prior, then the countercyclical searched winner.
- Reverse-causality finding is foregrounded.
- In-sample / out-of-sample inversion is stated as a red flag.
- Fragility caveats are prominent and repeated.

## Ace Notes

- Use bare chart names listed above; do not use pair-prefixed filenames.
- `rolling_sharpe_cp` and `rolling_granger` have explicit skip sidecars because `signal_scope.json` has `regime_story: false` and no CP2 upstream artifacts exist.
- The honest portal bottom line should remain: interesting drawdown-management overlay, not evidence that ISM Services PMI leads the S&P 500.
