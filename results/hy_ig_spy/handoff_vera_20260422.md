# Vera → [Next Agent] Handoff: hy_ig_spy Charts (20260422)

## META-RYW Block — Chart Review

Each chart was reviewed for: title states insight (not just variable name), axes labeled with units, legend entries match traces, palette role applied correctly.

| Chart | Title (insight-driven?) | Axes with units? | Legend OK? | Palette role | narrative_alignment_note |
|-------|------------------------|------------------|------------|--------------|--------------------------|
| hero | ✓ "Credit Stress Predicts Equity Drawdowns" | bps spread (%), SPY ($) | ✓ | indicator=C_INDICATOR, target=C_TARGET | Full 25-year context establishes counter-cyclical link |
| regime_stats | ✓ "HMM Regime Discrimination: Calm = Strong..." | HMM Regime / Ann Return (%) | no legend (intentional, showlegend=False) | C_TERTIARY calm, C_INDICATOR stress | Validates winner signal regime separation |
| history_zoom_dotcom | ✓ "Dot-Com Bust: Spread widened months before..." | HY-IG Spread (%), SPY ($) | ✓ | indicator / target | Episode zoom confirms lead-lag |
| history_zoom_gfc | ✓ "GFC: Credit Spreads Peaked at 2,000 bps..." | HY-IG Spread (%), SPY ($) | ✓ | indicator / target | Strongest case for spread as early warning |
| history_zoom_covid | ✓ "COVID Crash: HMM Correctly Signaled Stress..." | HY-IG Spread (%), SPY ($) | ✓ | indicator / target | Strategy performance context |
| correlations | ✓ "Negatively Correlated Persistently Since 2008" | Date / Rolling 252d Correlation | no legend (single trace + fill) | C_INDICATOR primary | Negative rolling r validates predictive direction |
| ccf | ✓ "Negative Contemporaneous Cross-Correlation..." | Lag (days) / Cross-Correlation | no legend (single bar series) | C_INDICATOR neg / C_TARGET pos | CCF at lag 0 strongly negative |
| granger_f_by_lag | ✓ "Granger Causality HY-IG Predicts SPY Monthly" | Lag (months) / Granger F-Stat | no legend (single bar) | C_INDICATOR sig / C_NEUTRAL insig | F-stats by lag show horizons with predictive content |
| hmm_regime_probs | ✓ "HMM Stress Probability > 0.5 Flags Every..." | P(Stress State) / SPY ($) | ✓ indicator + target | C_ALERT fill, C_TARGET SPY | Stress prob visually aligns with crisis episodes |
| regime_quartile_returns | ✓ "Spread Quartile Anatomy: Q1 +18.7%, Q4 -10.2%" | Quartile / Ann Return (%) | no legend (single bar) | C_Q gradient | Monotone degradation Q1→Q4 confirmed |
| transfer_entropy | ✓ "Information Flow Predominantly HY-IG → SPY" | Date / TE Proxy (rolling 504d) | ✓ HY→SPY / SPY→HY | C_INDICATOR / C_TARGET | Directional flow validates credit-leads-equity |
| local_projections | ✓ "Credit Spread Impact Builds Over Weeks..." | Horizon (days) / Coefficient (HAC SE) | ✓ CI / coef / sig | C_TARGET coef, C_INDICATOR stars | LP IRF confirms effect intensifies at 63d |
| quantile_regression | ✓ "Credit Spreads Hit Worst Outcomes Hardest" | Return quantile / QR Coeff | ✓ CI / QR / tails | C_TARGET coef, C_INDICATOR diamonds | V-shape asymmetry confirmed |
| equity_curves | ✓ "HMM Signal Beats Buy-and-Hold: Sharpe 1.41 vs 0.81" | Date / Growth of $1 | ✓ Winner / B&H | C_TERTIARY winner, C_BENCHMARK (#6C7A89) B&H | benchmark_trace role applied for B&H line |
| drawdown | ✓ "Winner Strategy Max Drawdown: -8.5%" | Date / Drawdown from Peak (%) | ✓ | C_INDICATOR fill (drawdown_fill role) | Shallow MDD demonstrates risk control |
| drawdown_comparison | ✓ "HMM Strategy Limits Drawdowns: -9% vs -34% B&H" | Date / Drawdown (%) | ✓ B&H / Winner | C_BENCHMARK B&H, C_TERTIARY winner | benchmark_trace for B&H, tertiary for strategy |
| walk_forward | ✓ "Walk-Forward OOS Sharpe: Positive 14/17 Years" | Test Year / OOS Sharpe | no legend (single bar) | C_TERTIARY > bh / C_INDICATOR < bh | Consistent OOS performance across years |
| tournament_scatter | ✓ "Tournament: N Valid Combos, Winner Sharpe 1.41" | Ann Return (%) / OOS Sharpe | ✓ by strategy + winner star | C_CAT by strategy, C_TERTIARY star | Winner at Sharpe frontier |
| tournament_sharpe_dist | ✓ "Winner Is Top N of N Valid Strategies" | OOS Sharpe / Count | ✓ valid histogram | C_TARGET hist, C_TERTIARY winner, C_BENCHMARK B&H | Sharpe distribution with benchmark_trace B&H |
| spread_history_annotated | ✓ "25-Year HY-IG History: Every Crisis Visible" | HY-IG Spread (%) / SPY ($) | ✓ | C_INDICATOR spread, C_TARGET SPY | Full annotated history with Ray's event registry |
| quartile_returns | ✓ "Monotone Return Decline, Rising Vol Q1→Q4" | Quartile / Ann Return (%) + Ann Vol (%) | ✓ Return / Vol | C_Q bars, C_INDICATOR vol scatter | Raw quartile signal validated without HMM conditioning |
| returns_by_regime | ✓ "Return Distribution by HMM Regime: Fat Left Tail" | HMM Regime / Daily SPY Return (%) | ✓ Calm / Stress violin | C_TERTIARY calm, C_INDICATOR stress | Violin confirms asymmetric distribution in stress regime |
| correlation_heatmap | ✓ "Signal × Horizon Heatmap: Red = Spread Predicts Lower Returns" | Horizon / Signal | colorbar = Pearson r | RdBu_r diverging scale | Heatmap shows which signals/horizons most predictive |

## VIZ-IC1 Summary

- 23 charts generated (22 required + `regime_quartile_returns` which is a distinct view from `quartile_returns`)
- All 23 VIZ-IC1 pre-save assertions PASS: non-empty `data`, non-empty `layout.title.text`
- All 23 `_meta.json` sidecars written with `palette_id=okabe_ito_2026`, `rules_applied=[VIZ-V8, VIZ-V11, VIZ-NM1, VIZ-IC1]`
- All filenames bare-name per VIZ-NM1 (no `hy_ig_spy_` prefix)
- NBER shading `rgba(150,120,120,0.22)` applied on all time-series charts (VIZ-V2)
- Palette role aliases: `indicator=#D55E00`, `target=#0072B2`, `benchmark=#6C7A89`

## VIZ-V5 Smoke Results

```
23/23 PASS — all charts parsed OK, ≥1 trace, non-empty title
0 FAIL
```

## Existing-Pair Smoke Loader

| Pair | Result |
|------|--------|
| hy_ig_v2_spy | 15 PASS, 0 FAIL |
| indpro_xlp | 8 PASS, 0 FAIL |
| umcsent_xlv | 7 PASS, 0 FAIL |

No regression introduced.

## Output Location

`output/charts/hy_ig_spy/plotly/` — 23 chart JSONs + 23 `_meta.json` sidecars + `_smoke_test_20260422.log`

## Notes for Ace (App Dev)

- `pair_id = "hy_ig_spy"` (bare, not v2)
- 22 required chart names per task spec all present; `regime_quartile_returns` is an additional chart (23 total)
- Winner: `S6_hmm_stress / T4_hmm_0.5 / P2 / L0`, OOS Sharpe 1.41, MDD -8.5%
- `equity_curves` and `drawdown_comparison` use `benchmark_trace` (#6C7A89) for B&H lines per v1.1.0 palette spec

Generated: 2026-04-22T10:51:00Z
Author: Viz Vera
