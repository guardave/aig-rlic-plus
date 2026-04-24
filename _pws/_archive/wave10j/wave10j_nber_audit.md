# Wave 10J — NBER Shading Audit

**Date:** 2026-04-24
**Auditor:** Viz Vera
**Rule applied:** VIZ-NBER1 (defined in Wave 10J SOP update)

---

## Audit Methodology

Checked all `.json` chart files in `output/charts/*/plotly/` (excluding `_meta.json`) for `layout.shapes` containing `fillcolor` with `rgba(...)` pattern — the canonical NBER shading signal per VIZ-V2.

Rule VIZ-NBER1 specifies the following chart types MUST carry NBER shading when the chart's x-axis spans > 5 years:
1. Hero / spread history / spread_history_annotated
2. Rolling correlation (`rolling_correlation.json`)
3. Rolling Sharpe (`rolling_sharpe.json`, `wf_sharpe.json`)
4. HMM regime probability (`hmm_regime_probs.json`)
5. Equity curves (`equity_curves.json`)
6. History zoom charts (`history_zoom_*.json`)
7. Quantile regression time-series (when x-axis is time)
8. Walk-forward Sharpe (`walk_forward.json`)
9. Rolling Granger (`rolling_granger.json`)

---

## Non-Compliant Charts (NBER Shading Missing)

### Category 1: Hero Charts — NBER MISSING

| Pair | Chart File | Span | Status |
|------|-----------|------|--------|
| `permit_spy` | `permit_spy_hero.json` | ~30 years | **NON-COMPLIANT** |
| `sofr_ted_spy` | `sofr_ted_spy_hero.json` | ~10 years | **NON-COMPLIANT** |
| `ted_spliced_spy` | `ted_spliced_spy_hero.json` | ~30 years | **NON-COMPLIANT** |
| `dff_ted_spy` | `dff_ted_spy_hero.json` | ~30 years | **NON-COMPLIANT** |
| `vix_vix3m_spy` | `vix_vix3m_spy_hero.json` | ~20 years | **NON-COMPLIANT** |

### Category 2: Equity Curves — NBER MISSING

| Pair | Chart File | Status |
|------|-----------|--------|
| `hy_ig_v2_spy` | `equity_curves.json` | **NON-COMPLIANT** |
| `indpro_spy` | `indpro_spy_equity_curves.json` | **NON-COMPLIANT** |
| `indpro_xlp` | `equity_curves.json` | **NON-COMPLIANT** |
| `umcsent_xlv` | `equity_curves.json` | **NON-COMPLIANT** |

Note: `hy_ig_spy/equity_curves.json` has NBER shading — use it as the reference implementation.

### Category 3: Rolling Sharpe — NBER MISSING

| Pair | Chart File | Status |
|------|-----------|--------|
| `indpro_xlp` | `rolling_sharpe.json` | **NON-COMPLIANT** |
| `umcsent_xlv` | `rolling_sharpe.json` | **NON-COMPLIANT** |
| `umcsent_xlv` | `wf_sharpe.json` | **NON-COMPLIANT** |
| `hy_ig_spy` | `walk_forward.json` | **NON-COMPLIANT** |
| `hy_ig_v2_spy` | `walk_forward.json` | **NON-COMPLIANT** |
| `indpro_xlp` | `walk_forward.json` | **NON-COMPLIANT** |

### Category 4: Quantile Regression — INCONSISTENT

| Pair | Chart File | NBER? |
|------|-----------|-------|
| `hy_ig_spy` | `quantile_regression.json` | YES (compliant) |
| `hy_ig_v2_spy` | `quantile_regression.json` | YES (compliant) |
| `indpro_spy` | `indpro_spy_quantile_regression.json` | **NO — NON-COMPLIANT** |

Note: Quantile regression is a cross-section chart (coefficient vs. quantile), NOT a time-series — NBER shading does not apply. The `hy_ig_spy` and `hy_ig_v2_spy` instances have shading, but this appears to be false positives in those files. **NBER shading on quantile regression is actually incorrect** — the x-axis is the quantile index, not calendar time. VIZ-NBER1 excludes this chart type.

### Category 5: Compliant Charts (reference implementations)

| Chart Type | Compliant Pairs |
|-----------|----------------|
| Hero | `hy_ig_spy`, `hy_ig_v2_spy`, `indpro_spy`, `indpro_xlp`, `umcsent_xlv` |
| Equity curves | `hy_ig_spy` |
| History zoom | `hy_ig_spy` (all 3), `hy_ig_v2_spy` (all 3) |
| HMM regime probs | `hy_ig_spy`, `hy_ig_v2_spy` |
| Spread history annotated | `hy_ig_spy`, `hy_ig_v2_spy` |

---

## Pairs with Zero NBER Shading (all charts)

The following pairs have NO chart with NBER shading at all:
- `permit_spy` — 5 charts, 0 with NBER shading
- `sofr_ted_spy` — 5 charts, 0 with NBER shading
- `ted_spliced_spy` — 5 charts, 0 with NBER shading
- `dff_ted_spy` — 5 charts, 0 with NBER shading
- `vix_vix3m_spy` — 5 charts, 0 with NBER shading

These are all "Wave 2 pipeline" pairs that used the legacy `pair_pipeline_{pair}.py` script which did not implement VIZ-V2 NBER shading. The issue is in the pipeline generators, not in Vera's manual chart work.

---

## Remediation Priority

| Priority | Action |
|----------|--------|
| P1 | Update the pair pipeline generators to include NBER shading in hero charts |
| P1 | Add NBER shading to equity_curves in all pairs |
| P2 | Add NBER shading to rolling_sharpe / walk_forward charts |
| P3 | Document any chart whose x-axis is non-temporal (quantile regression, regime bar charts) as VIZ-NBER1 exempt |
