# Vera + Ray Handoff — petrol_inv_spy — 2026-06-17

VERARAY DONE

## Scope

Mode-3 maker dispatch executed for both roles:
- Viz Vera: standard Plotly chart bundle for `petrol_inv_spy`.
- Research Ray: four-section portal narrative and Ray-owned interpretation metadata fields.

## Vera Artifacts

Generator:
- `scripts/generate_charts_petrol_inv_spy.py`

Chart output directory:
- `output/charts/petrol_inv_spy/plotly/`

Produced chart JSONs, each with `{chart}_meta.json` and `_perceptual_check_{chart}.png`:
- `hero`
- `equity_curves`
- `drawdown`
- `correlation_heatmap`
- `ccf_prewhitened`
- `granger_f_by_lag`
- `hmm_regime_probs`
- `local_projections`
- `quantile_coef`
- `transfer_entropy`
- `regime_stats`
- `tournament_scatter`
- `tournament_sharpe_dist`
- `rolling_correlation`
- `structural_break`
- `subperiod_sharpe`
- `history_zoom_dotcom`
- `history_zoom_gfc`
- `history_zoom_covid`
- `history_zoom_inflation_2022`

Skip sidecars:
- `chart_skip_rolling_sharpe_cp.json`
- `chart_skip_rolling_granger.json`

Reason: ECON-CP2 rolling Sharpe / rolling Granger artifacts are not present in Evan's petrol output bundle. The pair has CP1 artifacts (`rolling_correlation`, `structural_break`, `subperiod_sharpe`) and those were charted.

## Vera Verification

Generation command:

```bash
python scripts/generate_charts_petrol_inv_spy.py
```

Chart rendering validation:

```text
PASS: ccf_prewhitened traces=1 title=True png=True
PASS: correlation_heatmap traces=1 title=True png=True
PASS: drawdown traces=3 title=True png=True
PASS: equity_curves traces=3 title=True png=True
PASS: granger_f_by_lag traces=3 title=True png=True
PASS: hero traces=3 title=True png=True
PASS: history_zoom_covid traces=3 title=True png=True
PASS: history_zoom_dotcom traces=3 title=True png=True
PASS: history_zoom_gfc traces=3 title=True png=True
PASS: history_zoom_inflation_2022 traces=2 title=True png=True
PASS: hmm_regime_probs traces=2 title=True png=True
PASS: local_projections traces=4 title=True png=True
PASS: quantile_coef traces=2 title=True png=True
PASS: regime_stats traces=2 title=True png=True
PASS: rolling_correlation traces=2 title=True png=True
PASS: structural_break traces=2 title=True png=True
PASS: subperiod_sharpe traces=1 title=True png=True
PASS: tournament_scatter traces=4 title=True png=True
PASS: tournament_sharpe_dist traces=1 title=True png=True
PASS: transfer_entropy traces=2 title=True png=True
Total: 20 charts, 20 pass, 0 fail
```

NBER shading inspection:

```text
PASS: hero NBER_shapes=3
PASS: hmm_regime_probs NBER_shapes=3
PASS: equity_curves NBER_shapes=3
PASS: drawdown NBER_shapes=3
PASS: rolling_correlation NBER_shapes=3
PASS: structural_break NBER_shapes=3
PASS: history_zoom_dotcom NBER_shapes=2
PASS: history_zoom_gfc NBER_shapes=2
PASS: history_zoom_covid NBER_shapes=2
SKIP-OK: history_zoom_inflation_2022 NBER_shapes=0 (episode window has no NBER recession)
```

VIZ-DP1:
- `regime_stats`: PASS
- `local_projections`: PASS
- `history_zoom_dotcom`: PASS
- `history_zoom_gfc`: PASS
- `history_zoom_covid`: PASS
- `history_zoom_inflation_2022`: PASS

Sidecar/perceptual audit:

```text
sidecar/perceptual audit PASS
```

## Ray Artifacts

Narrative:
- `docs/portal_narrative_petrol_inv_spy_20260617.md`

Metadata updated:
- `results/petrol_inv_spy/interpretation_metadata.json`

Ray-owned fields filled/updated:
- `strategy_objective`: `max_sharpe`
- `expected_direction`: `procyclical`
- `mechanism`
- `caveats`
- `narrative_summary`

## Ray Verification

Narrative schema:

```text
OK: /tmp/petrol_frontmatter.json conforms to docs/schemas/narrative_frontmatter.schema.json
```

Glossary references:

```text
missing glossary terms: []
```

RES-OD1:

```text
RES-OD1 check: OK: petrol_inv_spy direction=procyclical
direction_consistent recalculated: True
```

RES-NR1:
- target_symbol from `winner_summary.json`: `SPY`
- narrative references verified: `SPY`, `buy-and-hold`, `United States equity market`
- no non-SPY target instrument references introduced.

RES-JFU:
- First user-facing uses of OOS, Sharpe ratio, maximum drawdown, procyclical/counter-cyclical, Granger causality, pre-whitened CCF, local projection, HMM, quantile regression, transfer entropy, Long/Cash, EIA, ETF, z-score, in-sample/out-of-sample, and walk-forward validation are expanded with plain-English glosses in their respective sections.

## Direction and Lag Reconciliation

Narrative explicitly states:
- Counter-cyclical prior: inventories may build when demand is weak, as in GFC/COVID.
- Evidence overturning that prior: quartile gradient Q1 Sharpe 0.37 / 6.0% annualized return to Q4 Sharpe 1.25 / 17.5% annualized return.
- Mechanism as hypothesis, not fact: inventory builds can reflect robust supply/production availability and softer energy-price pressure that supports consumers and margins.
- Lag imprecision: Granger support clusters at 6-8 months; selected rule is L12; use 6-12 month band.
- Fragility: bootstrap p=0.099, found_in_search, confidence low, lower return but better drawdown.

## Ace Notes

- Canonical chart names are bare names under `output/charts/petrol_inv_spy/plotly/`; no pair-prefixed chart filenames.
- `history_zoom_inflation_2022` has no NBER shading by construction because the registered episode window has no NBER recession.
- `regime_stats` is the quartile/returns-by-regime chart requested in the dispatch.
- Narrative chart refs include all 20 produced charts. Ace can choose the standard page subset and route exploratory extras (`quantile_coef`, `transfer_entropy`, `tournament_*`, CP1 charts) to Evidence/Methodology as appropriate.
