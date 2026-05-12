# Vera → Ace Handoff: hy_ig_spy_v4_from_scratch (20260512)

**From:** Visualization Vera  
**To:** App Dev Ace  
**Date:** 2026-05-12  
**Pair ID:** hy_ig_spy_v4_from_scratch  
**Chart output:** `output/charts/hy_ig_spy_v4_from_scratch/plotly/`

---

## Chart Inventory

All charts are Plotly JSON with `_meta.json` sidecars and kaleido perceptual PNGs.

### Mandatory GATE-DPS1 Charts (9/9 — PASS)

| Filename | Description | Status |
|---|---|---|
| `hero.json` | Dual-panel: HY-IG spread with HMM shading (top) + SPY monthly returns (bottom). OOS/Holdout split lines annotated. | DONE |
| `regime_stats.json` | Q1–Q4 annualized SPY return bar chart with vol error bars (Q1=tightest spread). Monotonic decline confirmed. | DONE |
| `rolling_correlation.json` | Rolling Pearson r time-series, 12m/24m/36m windows. NBER recession shading. | DONE |
| `rolling_granger.json` | Rolling Granger p-value (36m window, HY-IG→SPY). p=0.05 and p=0.10 reference lines. | DONE |
| `rolling_sharpe.json` | Rolling strategy Sharpe (12m/24m/36m windows). OOS/Holdout split markers. | DONE |
| `walk_forward.json` | OOS period (2014-08-29 to 2020-06-30) equity curve: strategy vs B&H, indexed to 1.0 at OOS start. | DONE |
| `tournament_scatter.json` | OOS Sharpe vs annualized return scatter (n=1,908 valid combos). Winner (S2c/z<0/P1) highlighted as red star. | DONE |
| `drawdown.json` | Drawdown: strategy vs B&H SPY. OOS/Holdout split markers. NBER recession shading. | DONE |
| `subperiod_sharpe.json` | SPY Sharpe by sub-period: Pre-GFC / GFC Era / ZIRP Era / COVID-to-Present. | DONE |

### Crisis Episode Zoom Charts — DPS-EP1 (5/5 — PASS)

| Filename | Window | Status |
|---|---|---|
| `history_zoom_dotcom.json` | 2000-03-01 to 2002-10-31 | DONE |
| `history_zoom_gfc.json` | 2007-10-01 to 2009-06-30 | DONE |
| `history_zoom_covid.json` | 2020-02-01 to 2020-12-31 | DONE |
| `history_zoom_taper_2018.json` | 2018-01-01 to 2019-01-31 | DONE |
| `history_zoom_inflation_2022.json` | 2022-01-01 to 2022-12-31 | DONE — ANNOTATION included per Evan's instruction (rate repricing, not credit cycle default risk) |

All zoom charts: dual-axis — HY-IG spread (left, red) + SPY cumulative return indexed to episode start (right, blue). Monthly frequency. NBER recession shading applied where applicable.

### Additional ECON-H4 Charts (11)

| Filename | Description | Disposition | Status |
|---|---|---|---|
| `equity_curves.json` | Full 3-period equity curves (IS/OOS/Holdout shaded). `failed_final_exam` disclosure banner per DPS-PRE1. | consumed | DONE |
| `correlation_heatmap.json` | Pearson/Spearman/Kendall × 1m/3m/6m horizon heatmap. | suggested | DONE |
| `ccf_prewhitened.json` | Pre-whitened CCF, lags −20 to +20, 95% CI bands. Significant lags in red. | suggested | DONE |
| `granger_by_lag.json` | F-statistic by lag 1–6 bar chart (HY-IG→SPY). Lags 4–6 significant at p<0.05. | suggested | DONE |
| `local_projections.json` | Local projection IRF coefficients (HAC CI), fwd + rev directions. | suggested | DONE |
| `quantile_regression.json` | Quantile coef τ=0.05–0.95 line with OLS reference. | suggested | DONE |
| `hmm_regime_overlay.json` | HMM 2-state stress probability overlay on HY-IG spread. | suggested | DONE |
| `hmm_summary.json` | Calm vs stress regime: annualized SPY return bar chart (derived from HMM state assignments). | suggested | DONE |
| `transfer_entropy.json` | TE bar: fwd (HY-IG→SPY) vs rev (SPY→HY-IG). | suggested | DONE |
| `predictive_regressions.json` | Coefficient forest plot: all signals × 1m horizon. Winner (z-score 36m) highlighted. | suggested | DONE |
| `structural_break.json` | CUSUM-OLS result — test FAILED in Evan pipeline (numerical error). Chart shows spread history for visual inspection with documented note. | suggested | DONE |

---

## VIZ-HZE1 Gate — Crisis Zoom Verification

```
$ git ls-files output/charts/hy_ig_spy_v4_from_scratch/plotly/ | grep history_zoom

output/charts/hy_ig_spy_v4_from_scratch/plotly/_perceptual_check_history_zoom_covid.png
output/charts/hy_ig_spy_v4_from_scratch/plotly/_perceptual_check_history_zoom_dotcom.png
output/charts/hy_ig_spy_v4_from_scratch/plotly/_perceptual_check_history_zoom_gfc.png
output/charts/hy_ig_spy_v4_from_scratch/plotly/_perceptual_check_history_zoom_inflation_2022.png
output/charts/hy_ig_spy_v4_from_scratch/plotly/_perceptual_check_history_zoom_taper_2018.png
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_covid.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_covid_meta.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_dotcom.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_dotcom_meta.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_gfc.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_gfc_meta.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_inflation_2022.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_inflation_2022_meta.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_taper_2018.json
output/charts/hy_ig_spy_v4_from_scratch/plotly/history_zoom_taper_2018_meta.json
```

All 5 slugs present: dotcom ✓ gfc ✓ covid ✓ taper_2018 ✓ inflation_2022 ✓  
**VIZ-HZE1: PASS**

---

## META-SRV Evidence Block

```
$ git ls-files output/charts/hy_ig_spy_v4_from_scratch/plotly/ | grep -v perceptual | grep "\.json$" | grep -v "_meta" | wc -l
25

$ git ls-files output/charts/hy_ig_spy_v4_from_scratch/plotly/ | grep "_meta\.json$" | wc -l
25

$ git ls-files output/charts/hy_ig_spy_v4_from_scratch/plotly/ | grep "perceptual" | wc -l
25
```

Total: 25 chart JSONs, 25 sidecar `_meta.json` files, 25 perceptual PNGs.  
Commit: 3f3f01b on branch 260430, pushed to origin.

---

## Quality Notes

- All charts: axes labelled with units; titles include pair display name "HY-IG Spread → SPY (v4)"; okabe_ito_2026 palette; no raw pair_id slugs in titles.
- Hero chart: OOS split line at 2014-08-29 and Holdout split line at 2020-07-31, both labelled.
- `equity_curves.json`: includes `failed_final_exam` disclosure banner (Holdout Sharpe=0.31 < 0.50 floor). Required per DPS-PRE1.
- `inflation_2022` zoom: annotation embedded explaining rate-repricing mechanism (not credit-cycle default risk), per Evan's handoff instruction.
- `structural_break.json`: CUSUM test failed in Evan's pipeline (float/tuple numerical error). Chart shows spread history with explanatory note; disposition=`suggested`.
- Data frequency: monthly throughout. No resampling or interpolation applied.

---

## Skips

None. All 25 charts produced successfully. No `_meta.json` skip files issued.

---

Generated: 2026-05-12  
Author: Visualization Vera
