# Viz Vera Handoff - UMCSENT x XLV Winner Refresh

VERA DONE

## Chart Request Acknowledgment

**Request from:** Lead Lesandro  
**Request received:** 2026-06-19 09:00 UTC

**What I received:**
- [x] Data file: `results/umcsent_xlv/strategy_returns_20260420.csv` - received
- [x] Chart type specified: winner-specific strategy charts
- [x] Key message / insight: corrected winner is UMCSENT 3-month momentum, rolling z-score > 1.0, 6-month lead, Long/Cash
- [x] Variable list: strategy return, buy-and-hold return, position, threshold path
- [x] Annotation context: NBER shading for long-horizon calendar charts

**What is missing (blockers):**
- None for chart production.

**What is missing (nice-to-have, will proceed without):**
- Ray/Ace display-prose refresh for stale public narrative numbers remains downstream.

## Regenerated Charts

- `output/charts/umcsent_xlv/plotly/equity_curves.json`
- `output/charts/umcsent_xlv/plotly/drawdown.json`
- `output/charts/umcsent_xlv/plotly/rolling_sharpe.json`
- `output/charts/umcsent_xlv/plotly/wf_sharpe.json`
- `output/charts/umcsent_xlv/plotly/subperiod_sharpe.json`
- `output/charts/umcsent_xlv/plotly/rolling_sharpe_cp.json`

Each regenerated chart has a refreshed `_meta.json` sidecar and `_perceptual_check_*.png`.

## Derived Source Refresh

- `results/umcsent_xlv/subperiod_sharpe.csv` refreshed from corrected `strategy_returns_20260420.csv`.
- `results/umcsent_xlv/rolling_sharpe_umcsent_xlv.csv` refreshed from corrected `strategy_returns_20260420.csv`.

Full OOS row now reconciles to Evan's corrected ground truth:

- OOS Sharpe: `1.158553`
- OOS annual return: `0.079494`
- OOS max drawdown: `-0.007007`

## Explicit Non-Changes

Indicator-level charts were not regenerated: `correlations`, `ccf`, `correlation_scatter`, `regime_stats`, `signal_dist`, `tournament_scatter`, `rolling_correlation`, `rolling_granger`, `structural_break`, and history zoom charts.

`hero` was not regenerated because it does not display winner statistics or positions.

## Verification

`python -m py_compile scripts/generate_charts_umcsent_xlv.py` - PASS.

`python scripts/generate_charts_umcsent_xlv.py --winner-refresh` - PASS.

VIZ-CV1 chart rendering validation:

```text
PASS equity_curves: traces=3; title=yes; meta=True; perceptual_png=True size=62809
PASS drawdown: traces=3; title=yes; meta=True; perceptual_png=True size=81931
PASS rolling_sharpe: traces=3; title=yes; meta=True; perceptual_png=True size=76075
PASS wf_sharpe: traces=2; title=yes; meta=True; perceptual_png=True size=56634
PASS subperiod_sharpe: traces=1; title=yes; meta=True; perceptual_png=True size=45793
PASS rolling_sharpe_cp: traces=2; title=yes; meta=True; perceptual_png=True size=81363
Total: 6 charts, 6 pass, 0 fail
```

VIZ-DP1:

```text
VIZ-DP1 SKIP equity_curves: not dual-panel
VIZ-DP1 SKIP drawdown: not dual-panel
VIZ-DP1 SKIP rolling_sharpe: not dual-panel
VIZ-DP1 SKIP wf_sharpe: not dual-panel
VIZ-DP1 SKIP subperiod_sharpe: not dual-panel
VIZ-DP1 SKIP rolling_sharpe_cp: not dual-panel
VIZ-DP1 PASS - regenerated chart set has no dual-panel axis-assignment violations.
```

VIZ-NBER1:

```text
VIZ-NBER1 equity_curves: 3 NBER shape(s)
VIZ-NBER1 drawdown: 3 NBER shape(s)
VIZ-NBER1 rolling_sharpe: 3 NBER shape(s)
VIZ-NBER1 rolling_sharpe_cp: 3 NBER shape(s)
```

Metric reconciliation from `strategy_returns_20260420.csv` over `2019-04-30` to `2025-12-31`:

```text
oos_sharpe: computed=1.158553 reported=1.158600 diff=-0.000047
oos_ann_return: computed=0.079494 reported=0.079494 diff=-0.000000
oos_max_drawdown: computed=-0.007007 reported=-0.007007 diff=-0.000000
```

Stale chart-label grep:

```text
rg "S2_yoy|Winner: S2|1\.02 Sharpe|Sharpe 1\.02|\+6\." regenerated chart JSON/meta files
```

Result: no matches.

## Ray / Ace Follow-Up Notice

Chart-text coherence audit found stale display prose in `app/pair_configs/umcsent_xlv_config.py` still quoting the old 1.02 Sharpe, +11.93% annual return, and -10.9% max drawdown. Ray should refresh display narrative and captions; Ace should re-render/check the Strategy and Story pages after Ray's update. Vera-owned chart titles, captions, and sidecars now quote the corrected 1.16 Sharpe, +7.95% annual return, and -0.7% max drawdown.
