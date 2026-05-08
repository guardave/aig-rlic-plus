# Handoff: Viz Vera SOP Retro Artifact Remediation

Date: 2026-05-08
Agent: viz-vera
Scope pairs: hy_ig_v2_spy, hy_ig_spy, indpro_xlp, indpro_spy, umcsent_xlv, dff_ted_spy, ted_spliced_spy, sofr_ted_spy, permit_spy, vix_vix3m_spy

## Inputs Read

- `docs/agent-sops/visualization-agent-sop.md`
- `docs/agent-sops/team-coordination.md` (`META-NMF`, `META-TD1`, `META-DASH1`, `GATE-25`, `GATE-27`, `GATE-28`)
- `docs/schemas/chart_type_registry.json`
- `docs/stakeholder-feedback/20260418-batch.md`
- `output/charts/{pair}/plotly/` for all scoped pairs

## SOP Rules Applied

- `VIZ-A3` / `VIZ-V8`: registry-backed canonical bare filenames; pair-prefixed files retained only as retired legacy audit artifacts.
- `VIZ-O1`: every chart JSON gets same-name `_meta.json` with valid disposition and required source/sample fields.
- `VIZ-E1`: non-registry analytical leftovers are `suggested`, not `consumed`.
- `VIZ-CV1` / `GATE-27`: every chart JSON has `_perceptual_check_{chart_name}.png` using the active naming convention.
- `VIZ-CP1`: CP-series sidecars now include `econ_rule_id`, `result_file`, disposition, source, and sample metadata.
- `META-AL` / `GATE-25`: no active chart JSON/sidecar depends on `output/_comparison` fallback.

## Remediation Performed

- Created canonical copies where the mapping was deterministic from the registry or active SOP:
  - `{pair}_correlations` / `correlations` -> `correlation_heatmap`
  - `ccf` -> `ccf_prewhitened`
  - `quantile_regression` -> `quantile_coef`
  - `{pair}_hero` -> `hero`
  - `{pair}_local_projections` -> `local_projections`
  - `{pair}_tournament_scatter` -> `tournament_scatter`
  - `{pair}_equity_curves` -> `equity_curves`
  - `{pair}_granger` -> `granger_f_by_lag`
  - `{pair}_rf_importance` -> `rf_importance`
  - `history_zoom_dot_com` -> `history_zoom_dotcom`
  - `history_zoom_rates_2022` -> `history_zoom_inflation_2022`
- Completed sidecars for all chart JSONs with required fields: `title`, `caption`, `source`, `source_sample_period`, `data_source_path`, `rules_applied`, `disposition`, plus `palette_id` where missing.
- Marked superseded pair-prefixed and stale legacy filenames as `retired` with `canonical_consumption: false`.
- Marked non-registry exploratory/leftover artifacts as `suggested` with `canonical_consumption: false`.
- Copied existing perceptual/static PNGs into the current `_perceptual_check_{chart_name}.png` naming convention where deterministic.

## Verification Commands And Results

### Structured Chart Audit

Command: Python audit over the 10 scoped `output/charts/{pair}/plotly` directories.

Result:

```text
total_chart_json 225
parse_fail 0
missing_meta 0
missing_required_fields 0
bad_disposition 0
consumed_noncanonical 0
nonregistry_active_retained 5
missing_perceptual_png 0
orphan_sidecars 5
```

Remaining `nonregistry_active_retained` rows are `suggested`, not `consumed`:

```text
output/charts/indpro_xlp/plotly/history_zoom_china_2015.json:suggested
output/charts/indpro_spy/plotly/history_zoom_china_2015.json:suggested
output/charts/indpro_spy/plotly/rf_importance.json:suggested
output/charts/dff_ted_spy/plotly/history_zoom_taper_2013.json:suggested
output/charts/permit_spy/plotly/history_zoom_china_2015.json:suggested
```

Remaining orphan sidecars:

```text
output/charts/sofr_ted_spy/plotly/history_zoom_dot_com_meta.json
output/charts/sofr_ted_spy/plotly/history_zoom_gfc_meta.json
output/charts/sofr_ted_spy/plotly/history_zoom_taper_2013_meta.json
output/charts/vix_vix3m_spy/plotly/_meta.json
output/charts/vix_vix3m_spy/plotly/history_zoom_dot_com_meta.json
```

### `_comparison` Fallback Scan

Command: `rg -n "output/_comparison|_comparison|canonical rendered|fallback" output/charts/<scoped pairs>/plotly`

Result: active chart JSON/sidecars did not reference `output/_comparison`. Matches were limited to historical smoke-test logs:

```text
output/charts/hy_ig_v2_spy/plotly/_smoke_test_20260419.log: PASS _comparison/history_zoom_*.json
output/charts/hy_ig_v2_spy/plotly/_smoke_test_wave5c_20260419.log: PASS _comparison/history_zoom_*.json
```

## Unresolved Blockers / Cross-Role Risks

- `history_zoom_china_2015`, `history_zoom_taper_2013`, and `rf_importance` lack active registry coverage. They are now `suggested`; consuming them requires registry entries or an explicit retire decision.
- Orphan skip/global sidecars remain for `sofr_ted_spy` and `vix_vix3m_spy`. They document skipped episodes/global inventory rather than a chart JSON; QA/Ace should decide whether skip records move outside `plotly/` or get a formal skip-manifest schema.
- Some retrofilled `source` fields read `legacy chart artifact; upstream source not declared in prior sidecar`. This satisfies VIZ-O1 field presence while preserving provenance uncertainty; true vendor/upstream attribution needs chart regeneration or upstream manifest recovery.
- Historical smoke-test logs still mention `_comparison` fallback. I did not rewrite historical logs; a fresh VIZ-CV1 run should supersede them if QA requires current log evidence.
- No chart JSON was regenerated; remediation used existing chart JSON/PNG artifacts only.

## Files Changed

- `output/charts/dff_ted_spy/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/dff_ted_spy/plotly/_perceptual_check_hero.png`
- `output/charts/dff_ted_spy/plotly/_perceptual_check_history_zoom_dotcom.png`
- `output/charts/dff_ted_spy/plotly/_perceptual_check_history_zoom_inflation_2022.png`
- `output/charts/dff_ted_spy/plotly/_perceptual_check_local_projections.png`
- `output/charts/dff_ted_spy/plotly/_perceptual_check_tournament_scatter.png`
- `output/charts/dff_ted_spy/plotly/correlation_heatmap.json`
- `output/charts/dff_ted_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/dff_ted_spy/plotly/dff_ted_spy_correlations_meta.json`
- `output/charts/dff_ted_spy/plotly/dff_ted_spy_hero_meta.json`
- `output/charts/dff_ted_spy/plotly/dff_ted_spy_local_projections_meta.json`
- `output/charts/dff_ted_spy/plotly/dff_ted_spy_regime_stats_meta.json`
- `output/charts/dff_ted_spy/plotly/dff_ted_spy_tournament_scatter_meta.json`
- `output/charts/dff_ted_spy/plotly/hero.json`
- `output/charts/dff_ted_spy/plotly/hero_meta.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_dot_com_meta.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_dotcom.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_dotcom_meta.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_inflation_2022.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_inflation_2022_meta.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_rates_2022_meta.json`
- `output/charts/dff_ted_spy/plotly/history_zoom_taper_2013_meta.json`
- `output/charts/dff_ted_spy/plotly/local_projections.json`
- `output/charts/dff_ted_spy/plotly/local_projections_meta.json`
- `output/charts/dff_ted_spy/plotly/rolling_correlation_meta.json`
- `output/charts/dff_ted_spy/plotly/rolling_granger_meta.json`
- `output/charts/dff_ted_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/dff_ted_spy/plotly/structural_break_meta.json`
- `output/charts/dff_ted_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/dff_ted_spy/plotly/tournament_scatter.json`
- `output/charts/dff_ted_spy/plotly/tournament_scatter_meta.json`
- `output/charts/hy_ig_spy/plotly/_perceptual_check_ccf_prewhitened.png`
- `output/charts/hy_ig_spy/plotly/_perceptual_check_quantile_coef.png`
- `output/charts/hy_ig_spy/plotly/ccf_meta.json`
- `output/charts/hy_ig_spy/plotly/ccf_prewhitened.json`
- `output/charts/hy_ig_spy/plotly/ccf_prewhitened_meta.json`
- `output/charts/hy_ig_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/hy_ig_spy/plotly/correlations_meta.json`
- `output/charts/hy_ig_spy/plotly/drawdown_comparison_meta.json`
- `output/charts/hy_ig_spy/plotly/drawdown_meta.json`
- `output/charts/hy_ig_spy/plotly/equity_curves_meta.json`
- `output/charts/hy_ig_spy/plotly/granger_f_by_lag_meta.json`
- `output/charts/hy_ig_spy/plotly/hero_meta.json`
- `output/charts/hy_ig_spy/plotly/history_zoom_covid_meta.json`
- `output/charts/hy_ig_spy/plotly/history_zoom_dotcom_meta.json`
- `output/charts/hy_ig_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/hy_ig_spy/plotly/hmm_regime_probs_meta.json`
- `output/charts/hy_ig_spy/plotly/local_projections_meta.json`
- `output/charts/hy_ig_spy/plotly/quantile_coef.json`
- `output/charts/hy_ig_spy/plotly/quantile_coef_meta.json`
- `output/charts/hy_ig_spy/plotly/quantile_regression_meta.json`
- `output/charts/hy_ig_spy/plotly/quartile_returns_meta.json`
- `output/charts/hy_ig_spy/plotly/regime_quartile_returns_meta.json`
- `output/charts/hy_ig_spy/plotly/regime_stats_meta.json`
- `output/charts/hy_ig_spy/plotly/returns_by_regime_meta.json`
- `output/charts/hy_ig_spy/plotly/rolling_correlation_meta.json`
- `output/charts/hy_ig_spy/plotly/rolling_granger_meta.json`
- `output/charts/hy_ig_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/hy_ig_spy/plotly/spread_history_annotated_meta.json`
- `output/charts/hy_ig_spy/plotly/structural_break_meta.json`
- `output/charts/hy_ig_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/hy_ig_spy/plotly/tournament_scatter_meta.json`
- `output/charts/hy_ig_spy/plotly/tournament_sharpe_dist_meta.json`
- `output/charts/hy_ig_spy/plotly/transfer_entropy_meta.json`
- `output/charts/hy_ig_spy/plotly/walk_forward_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/_perceptual_check_quantile_coef.png`
- `output/charts/hy_ig_v2_spy/plotly/ccf_prewhitened_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/drawdown_comparison_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/drawdown_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/equity_curves_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/granger_f_by_lag_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/hero_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/hero_spread_vs_spy_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/history_zoom_covid_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/history_zoom_dotcom_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/hmm_regime_probs_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/local_projections_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/quantile_coef.json`
- `output/charts/hy_ig_v2_spy/plotly/quantile_coef_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/quantile_regression_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/quartile_returns_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/regime_quartile_returns_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/regime_stats_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/returns_by_regime_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/rolling_correlation_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/rolling_granger_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/spread_history_annotated_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/structural_break_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/tournament_sharpe_dist_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/transfer_entropy_meta.json`
- `output/charts/hy_ig_v2_spy/plotly/walk_forward_meta.json`
- `output/charts/indpro_spy/plotly/_perceptual_check_ccf_prewhitened.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_equity_curves.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_granger_f_by_lag.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_hero.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_history_zoom_dotcom.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_local_projections.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_quantile_coef.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_rf_importance.png`
- `output/charts/indpro_spy/plotly/_perceptual_check_tournament_scatter.png`
- `output/charts/indpro_spy/plotly/ccf_prewhitened.json`
- `output/charts/indpro_spy/plotly/ccf_prewhitened_meta.json`
- `output/charts/indpro_spy/plotly/correlation_heatmap.json`
- `output/charts/indpro_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/indpro_spy/plotly/equity_curves.json`
- `output/charts/indpro_spy/plotly/equity_curves_meta.json`
- `output/charts/indpro_spy/plotly/granger_f_by_lag.json`
- `output/charts/indpro_spy/plotly/granger_f_by_lag_meta.json`
- `output/charts/indpro_spy/plotly/hero.json`
- `output/charts/indpro_spy/plotly/hero_meta.json`
- `output/charts/indpro_spy/plotly/history_zoom_china_2015_meta.json`
- `output/charts/indpro_spy/plotly/history_zoom_covid_meta.json`
- `output/charts/indpro_spy/plotly/history_zoom_dot_com_meta.json`
- `output/charts/indpro_spy/plotly/history_zoom_dotcom.json`
- `output/charts/indpro_spy/plotly/history_zoom_dotcom_meta.json`
- `output/charts/indpro_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_ccf_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_correlations_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_equity_curves_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_granger_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_hero_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_local_projections_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_quantile_regression_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_regime_stats_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_rf_importance_meta.json`
- `output/charts/indpro_spy/plotly/indpro_spy_tournament_scatter_meta.json`
- `output/charts/indpro_spy/plotly/local_projections.json`
- `output/charts/indpro_spy/plotly/local_projections_meta.json`
- `output/charts/indpro_spy/plotly/quantile_coef.json`
- `output/charts/indpro_spy/plotly/quantile_coef_meta.json`
- `output/charts/indpro_spy/plotly/rf_importance.json`
- `output/charts/indpro_spy/plotly/rf_importance_meta.json`
- `output/charts/indpro_spy/plotly/rolling_correlation_meta.json`
- `output/charts/indpro_spy/plotly/rolling_granger_meta.json`
- `output/charts/indpro_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/indpro_spy/plotly/structural_break_meta.json`
- `output/charts/indpro_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/indpro_spy/plotly/tournament_scatter.json`
- `output/charts/indpro_spy/plotly/tournament_scatter_meta.json`
- `output/charts/indpro_xlp/plotly/_perceptual_check_ccf_prewhitened.png`
- `output/charts/indpro_xlp/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/indpro_xlp/plotly/_perceptual_check_history_zoom_dotcom.png`
- `output/charts/indpro_xlp/plotly/ccf_meta.json`
- `output/charts/indpro_xlp/plotly/ccf_prewhitened.json`
- `output/charts/indpro_xlp/plotly/ccf_prewhitened_meta.json`
- `output/charts/indpro_xlp/plotly/correlation_heatmap.json`
- `output/charts/indpro_xlp/plotly/correlation_heatmap_meta.json`
- `output/charts/indpro_xlp/plotly/correlations_meta.json`
- `output/charts/indpro_xlp/plotly/drawdown_meta.json`
- `output/charts/indpro_xlp/plotly/equity_curves_meta.json`
- `output/charts/indpro_xlp/plotly/hero_meta.json`
- `output/charts/indpro_xlp/plotly/history_zoom_china_2015_meta.json`
- `output/charts/indpro_xlp/plotly/history_zoom_covid_meta.json`
- `output/charts/indpro_xlp/plotly/history_zoom_dot_com_meta.json`
- `output/charts/indpro_xlp/plotly/history_zoom_dotcom.json`
- `output/charts/indpro_xlp/plotly/history_zoom_dotcom_meta.json`
- `output/charts/indpro_xlp/plotly/history_zoom_gfc_meta.json`
- `output/charts/indpro_xlp/plotly/regime_stats_meta.json`
- `output/charts/indpro_xlp/plotly/rolling_correlation_meta.json`
- `output/charts/indpro_xlp/plotly/rolling_granger_meta.json`
- `output/charts/indpro_xlp/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/indpro_xlp/plotly/rolling_sharpe_meta.json`
- `output/charts/indpro_xlp/plotly/signal_dist_meta.json`
- `output/charts/indpro_xlp/plotly/structural_break_meta.json`
- `output/charts/indpro_xlp/plotly/subperiod_sharpe_meta.json`
- `output/charts/indpro_xlp/plotly/tournament_scatter_meta.json`
- `output/charts/indpro_xlp/plotly/walk_forward_meta.json`
- `output/charts/permit_spy/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/permit_spy/plotly/_perceptual_check_hero.png`
- `output/charts/permit_spy/plotly/_perceptual_check_history_zoom_dotcom.png`
- `output/charts/permit_spy/plotly/_perceptual_check_local_projections.png`
- `output/charts/permit_spy/plotly/_perceptual_check_tournament_scatter.png`
- `output/charts/permit_spy/plotly/correlation_heatmap.json`
- `output/charts/permit_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/permit_spy/plotly/hero.json`
- `output/charts/permit_spy/plotly/hero_meta.json`
- `output/charts/permit_spy/plotly/history_zoom_china_2015_meta.json`
- `output/charts/permit_spy/plotly/history_zoom_covid_meta.json`
- `output/charts/permit_spy/plotly/history_zoom_dot_com_meta.json`
- `output/charts/permit_spy/plotly/history_zoom_dotcom.json`
- `output/charts/permit_spy/plotly/history_zoom_dotcom_meta.json`
- `output/charts/permit_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/permit_spy/plotly/local_projections.json`
- `output/charts/permit_spy/plotly/local_projections_meta.json`
- `output/charts/permit_spy/plotly/permit_spy_correlations_meta.json`
- `output/charts/permit_spy/plotly/permit_spy_hero_meta.json`
- `output/charts/permit_spy/plotly/permit_spy_local_projections_meta.json`
- `output/charts/permit_spy/plotly/permit_spy_regime_stats_meta.json`
- `output/charts/permit_spy/plotly/permit_spy_tournament_scatter_meta.json`
- `output/charts/permit_spy/plotly/rolling_correlation_meta.json`
- `output/charts/permit_spy/plotly/rolling_granger_meta.json`
- `output/charts/permit_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/permit_spy/plotly/structural_break_meta.json`
- `output/charts/permit_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/permit_spy/plotly/tournament_scatter.json`
- `output/charts/permit_spy/plotly/tournament_scatter_meta.json`
- `output/charts/sofr_ted_spy/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/sofr_ted_spy/plotly/_perceptual_check_hero.png`
- `output/charts/sofr_ted_spy/plotly/_perceptual_check_history_zoom_inflation_2022.png`
- `output/charts/sofr_ted_spy/plotly/_perceptual_check_local_projections.png`
- `output/charts/sofr_ted_spy/plotly/_perceptual_check_tournament_scatter.png`
- `output/charts/sofr_ted_spy/plotly/correlation_heatmap.json`
- `output/charts/sofr_ted_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/sofr_ted_spy/plotly/hero.json`
- `output/charts/sofr_ted_spy/plotly/hero_meta.json`
- `output/charts/sofr_ted_spy/plotly/history_zoom_inflation_2022.json`
- `output/charts/sofr_ted_spy/plotly/history_zoom_inflation_2022_meta.json`
- `output/charts/sofr_ted_spy/plotly/history_zoom_rates_2022_meta.json`
- `output/charts/sofr_ted_spy/plotly/local_projections.json`
- `output/charts/sofr_ted_spy/plotly/local_projections_meta.json`
- `output/charts/sofr_ted_spy/plotly/rolling_correlation_meta.json`
- `output/charts/sofr_ted_spy/plotly/rolling_granger_meta.json`
- `output/charts/sofr_ted_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/sofr_ted_spy/plotly/sofr_ted_spy_correlations_meta.json`
- `output/charts/sofr_ted_spy/plotly/sofr_ted_spy_hero_meta.json`
- `output/charts/sofr_ted_spy/plotly/sofr_ted_spy_local_projections_meta.json`
- `output/charts/sofr_ted_spy/plotly/sofr_ted_spy_regime_stats_meta.json`
- `output/charts/sofr_ted_spy/plotly/sofr_ted_spy_tournament_scatter_meta.json`
- `output/charts/sofr_ted_spy/plotly/structural_break_meta.json`
- `output/charts/sofr_ted_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/sofr_ted_spy/plotly/tournament_scatter.json`
- `output/charts/sofr_ted_spy/plotly/tournament_scatter_meta.json`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_hero.png`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_history_zoom_dotcom.png`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_history_zoom_inflation_2022.png`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_history_zoom_rates_2022.png`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_local_projections.png`
- `output/charts/ted_spliced_spy/plotly/_perceptual_check_tournament_scatter.png`
- `output/charts/ted_spliced_spy/plotly/correlation_heatmap.json`
- `output/charts/ted_spliced_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/ted_spliced_spy/plotly/hero.json`
- `output/charts/ted_spliced_spy/plotly/hero_meta.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_covid_meta.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_dot_com_meta.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_dotcom.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_dotcom_meta.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_inflation_2022.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_inflation_2022_meta.json`
- `output/charts/ted_spliced_spy/plotly/history_zoom_rates_2022_meta.json`
- `output/charts/ted_spliced_spy/plotly/local_projections.json`
- `output/charts/ted_spliced_spy/plotly/local_projections_meta.json`
- `output/charts/ted_spliced_spy/plotly/rolling_correlation_meta.json`
- `output/charts/ted_spliced_spy/plotly/rolling_granger_meta.json`
- `output/charts/ted_spliced_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/ted_spliced_spy/plotly/structural_break_meta.json`
- `output/charts/ted_spliced_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/ted_spliced_spy/plotly/ted_spliced_spy_correlations_meta.json`
- `output/charts/ted_spliced_spy/plotly/ted_spliced_spy_hero_meta.json`
- `output/charts/ted_spliced_spy/plotly/ted_spliced_spy_local_projections_meta.json`
- `output/charts/ted_spliced_spy/plotly/ted_spliced_spy_regime_stats_meta.json`
- `output/charts/ted_spliced_spy/plotly/ted_spliced_spy_tournament_scatter_meta.json`
- `output/charts/ted_spliced_spy/plotly/tournament_scatter.json`
- `output/charts/ted_spliced_spy/plotly/tournament_scatter_meta.json`
- `output/charts/umcsent_xlv/plotly/_perceptual_check_ccf_prewhitened.png`
- `output/charts/umcsent_xlv/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/umcsent_xlv/plotly/_perceptual_check_history_zoom_dotcom.png`
- `output/charts/umcsent_xlv/plotly/_perceptual_check_history_zoom_inflation_2022.png`
- `output/charts/umcsent_xlv/plotly/ccf_meta.json`
- `output/charts/umcsent_xlv/plotly/ccf_prewhitened.json`
- `output/charts/umcsent_xlv/plotly/ccf_prewhitened_meta.json`
- `output/charts/umcsent_xlv/plotly/correlation_heatmap.json`
- `output/charts/umcsent_xlv/plotly/correlation_heatmap_meta.json`
- `output/charts/umcsent_xlv/plotly/correlations_meta.json`
- `output/charts/umcsent_xlv/plotly/drawdown_meta.json`
- `output/charts/umcsent_xlv/plotly/equity_curves_meta.json`
- `output/charts/umcsent_xlv/plotly/hero_meta.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_covid_meta.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_dot_com_meta.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_dotcom.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_dotcom_meta.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_gfc_meta.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_inflation_2022.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_inflation_2022_meta.json`
- `output/charts/umcsent_xlv/plotly/history_zoom_rates_2022_meta.json`
- `output/charts/umcsent_xlv/plotly/regime_stats_meta.json`
- `output/charts/umcsent_xlv/plotly/rolling_correlation_meta.json`
- `output/charts/umcsent_xlv/plotly/rolling_granger_meta.json`
- `output/charts/umcsent_xlv/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/umcsent_xlv/plotly/rolling_sharpe_meta.json`
- `output/charts/umcsent_xlv/plotly/signal_dist_meta.json`
- `output/charts/umcsent_xlv/plotly/structural_break_meta.json`
- `output/charts/umcsent_xlv/plotly/subperiod_sharpe_meta.json`
- `output/charts/umcsent_xlv/plotly/tournament_scatter_meta.json`
- `output/charts/umcsent_xlv/plotly/wf_sharpe_meta.json`
- `output/charts/vix_vix3m_spy/plotly/_perceptual_check_correlation_heatmap.png`
- `output/charts/vix_vix3m_spy/plotly/_perceptual_check_hero.png`
- `output/charts/vix_vix3m_spy/plotly/_perceptual_check_history_zoom_inflation_2022.png`
- `output/charts/vix_vix3m_spy/plotly/_perceptual_check_local_projections.png`
- `output/charts/vix_vix3m_spy/plotly/_perceptual_check_tournament_scatter.png`
- `output/charts/vix_vix3m_spy/plotly/correlation_heatmap.json`
- `output/charts/vix_vix3m_spy/plotly/correlation_heatmap_meta.json`
- `output/charts/vix_vix3m_spy/plotly/hero.json`
- `output/charts/vix_vix3m_spy/plotly/hero_meta.json`
- `output/charts/vix_vix3m_spy/plotly/history_zoom_covid_meta.json`
- `output/charts/vix_vix3m_spy/plotly/history_zoom_gfc_meta.json`
- `output/charts/vix_vix3m_spy/plotly/history_zoom_inflation_2022.json`
- `output/charts/vix_vix3m_spy/plotly/history_zoom_inflation_2022_meta.json`
- `output/charts/vix_vix3m_spy/plotly/history_zoom_rates_2022_meta.json`
- `output/charts/vix_vix3m_spy/plotly/local_projections.json`
- `output/charts/vix_vix3m_spy/plotly/local_projections_meta.json`
- `output/charts/vix_vix3m_spy/plotly/rolling_correlation_meta.json`
- `output/charts/vix_vix3m_spy/plotly/rolling_granger_meta.json`
- `output/charts/vix_vix3m_spy/plotly/rolling_sharpe_cp_meta.json`
- `output/charts/vix_vix3m_spy/plotly/structural_break_meta.json`
- `output/charts/vix_vix3m_spy/plotly/subperiod_sharpe_meta.json`
- `output/charts/vix_vix3m_spy/plotly/tournament_scatter.json`
- `output/charts/vix_vix3m_spy/plotly/tournament_scatter_meta.json`
- `output/charts/vix_vix3m_spy/plotly/vix_vix3m_spy_correlations_meta.json`
- `output/charts/vix_vix3m_spy/plotly/vix_vix3m_spy_hero_meta.json`
- `output/charts/vix_vix3m_spy/plotly/vix_vix3m_spy_local_projections_meta.json`
- `output/charts/vix_vix3m_spy/plotly/vix_vix3m_spy_regime_stats_meta.json`
- `output/charts/vix_vix3m_spy/plotly/vix_vix3m_spy_tournament_scatter_meta.json`
- `results/_cross_agent/handoff_vera_sop_retro_20260508.md`
