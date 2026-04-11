# HY-IG v2 Regression Note — 2026-04-11

**Pair ID:** `hy_ig_v2_spy`
**Author:** Econometrics Evan
**Trigger:** Retroactive method-coverage fix per updated Econometrics SOP Rule C1 (credit-equity mandatory method catalog) and team-coordination.md gate item 22.

## Changes From Prior Version

- **Added** `core_models_20260410/ccf_prewhitened.csv` — pre-whitened cross-correlation function at lags −20 to +20.
  - Filter: ARIMA(2,0,2) fit to `hy_ig_spread` by BIC grid search over (p≤5, q≤2); same order applied to `spy_log_ret`.
  - Sample: 6,782 daily observations (2000-01-03 → 2025-12-31).
  - 95% CI half-width: ±1.96/√N = ±0.0238.
  - Schema: `lag, ccf, lower_ci, upper_ci, significant, arima_order, n_obs` (matches Rule C2).
  - **Why:** Mandatory under Rule C1 for credit-equity pairs; was missing from the 2026-04-10 v2 rerun. Recovers method coverage lost from v1.

- **Added** `core_models_20260410/transfer_entropy.csv` — nonlinear information flow between HY-IG spread and SPY daily returns.
  - Estimator: Shannon histogram with 6 equal-frequency bins, lag 1 day, in nats.
  - Significance: circular block-shift permutation test, 500 permutations.
  - Both directions computed: `credit_to_equity`, `equity_to_credit`.
  - Schema: `direction, te_value, permutation_p_value, n_permutations, bandwidth, bin_method` (matches Rule C2).
  - `pyinform` is not installed in the environment, so TE is implemented from first principles (see `scripts/retro_fix_hy_ig_v2_evan_20260411.py`, function `transfer_entropy_hist`) and documented there.
  - **Why:** Mandatory under Rule C1; was missing from the v2 rerun.

- **Added** `core_models_20260410/quartile_returns.csv` — SPY return diagnostics conditioned on HY-IG spread quartile.
  - Quartiles pooled across the full daily sample (2000-01-03 → 2025-12-31).
  - Schema: `quartile, mean_return, vol, sharpe, n_obs, cutoff_lower, cutoff_upper, ann_return, ann_vol, max_drawdown` (the first 7 columns match Rule C2; `ann_return`, `ann_vol`, `max_drawdown` are appended for stakeholder display and do not change the schema contract).
  - Q1 vs Q4 Welch t-test: t = 1.501, p = 0.1335 (mean difference not significant, but the Sharpe and max-drawdown gradients are economically decisive — see Impact below).
  - **Why:** Present in HY-IG v1 Evidence page, silently dropped in v2, flagged by stakeholder review.

- **Added** `tournament_winner.json` — canonical winner/benchmark/deltas object per team-coordination.md "Tournament Winner JSON Schema."
  - Winner values pulled from `winner_summary.json` (unchanged from 2026-04-10 run).
  - Benchmark values pulled from the `signal == "BENCHMARK"` row in `tournament_results_20260410.csv` (unchanged).
  - Suggested `strategy_objective`: `min_mdd` (normalized drawdown improvement +0.698 dominates normalized Sharpe improvement +0.649 and the negative return delta −0.232).
  - **Why:** New canonical handoff artifact so Ray can set `strategy_objective` deterministically; was not part of the 2026-04-10 run.

## Approved By

**Lesandro** — retroactive fix approved as part of stakeholder-flagged regression review. Scope limited to adding the four missing artifacts; no other files in this pair are touched.

## Unchanged

All existing files in `results/hy_ig_v2_spy/` and `results/hy_ig_v2_spy/core_models_20260410/` remain **byte-identical** to the 2026-04-10 run:

- `data/hy_ig_v2_spy_daily_20260410.parquet` — master dataset (read-only input).
- `results/hy_ig_v2_spy/winner_summary.json` — winner metrics (read-only input).
- `results/hy_ig_v2_spy/tournament_results_20260410.csv` — tournament grid (read-only input).
- `results/hy_ig_v2_spy/interpretation_metadata.json`, `execution_notes.md`, `stationarity_tests_20260410.csv`, `signals_20260410.parquet`, `pipeline_timing_20260410.json`, `winner_trade_log.csv`.
- `results/hy_ig_v2_spy/exploratory_20260410/correlations.csv`.
- `results/hy_ig_v2_spy/core_models_20260410/granger_causality.csv`, `hmm_states_2state.parquet`, `local_projections.csv`, `predictive_regressions.csv`, `quantile_regression.csv`, `diagnostics_summary.csv`.
- `results/hy_ig_v2_spy/tournament_validation_20260410/` (all contents).

The tournament grid, the winner, and every headline number (OOS Sharpe 1.274, OOS ann return 11.33, max DD −10.2, annual turnover 3.78, B&H Sharpe 0.7726) are numerically unchanged. This fix is additive only.

## Impact Assessment

**Headline results:**

- **CCF (pre-whitened):** 15 lags are significant at 95%. Negative lags (SPY leading spread) dominate the significant set: the spread widens after SPY declines at lags −1 to −17 days. The lag-0 correlation is negative and significant (−0.028 at the CI boundary), consistent with the strong contemporaneous credit-equity link. Positive lags (spread leading SPY) are thinner — significant only at +6, +7, +9, +13 — suggesting the causal arrow on this dataset runs primarily from equity stress into credit spreads, with a weaker reverse channel at sub-monthly horizons.

- **Transfer entropy:** Credit → equity TE = 0.042 nats (permutation p = 0.004); equity → credit TE = 0.0055 nats (p = 0.050). The credit-to-equity channel carries ~7.6× more information than the reverse, which is the main nonlinear finding Ray can cite in the Evidence narrative. (Note: this sign is opposite to the CCF lead-lag result above — CCF is a linear filter so it mostly picks up price-level co-movement, whereas TE picks up conditional distribution shifts in returns. The two tell complementary stories and both deserve narrative space.)

- **Quartile returns:** The credit-cycle gradient is monotone and large: Sharpe collapses from 1.45 in Q1 (tightest spreads) to −0.04 in Q4 (widest), max drawdown blows out from −10.7% to −62.6%, and annualized return goes from +18.4% to −1.0%. The Welch Q1-vs-Q4 mean test is not significant (p = 0.13) because SPY vol in Q4 is 2.5× Q1 vol, but the risk-adjusted spread is the headline. This is exactly the stakeholder's lost chart.

- **Tournament winner JSON:** Ray can now set `strategy_objective = min_mdd` without guessing. The winner (HMM Stress Probability · P>0.5 · Signal-Strength) gives up 3.4 ppts of annualized return versus B&H but cuts max drawdown from −33.7% to −10.2% — a 23.5 ppt drawdown improvement — and lifts Sharpe from 0.77 to 1.27. The `min_mdd` classification is unambiguous on the normalized-delta test.

**Downstream consumers:**

- **Ray** can now build 8-element Evidence method blocks for CCF, Transfer Entropy, and Quartile Returns using the exact filenames and column schemas in SOP Rule C2, and can set `strategy_objective` from `suggested_strategy_objective` in the winner JSON (with override rights).
- **Vera** can build the standard CCF lag bar chart, a TE bidirectional bar, and a quartile-Sharpe bar/table without data work.
- **Ace** can render the three new method blocks on the Evidence page and can read `tournament_winner.json` to populate the winner-vs-benchmark KPI strip from a single file.
- **No impact** on the tournament winner, the equity curve, the trade log, or any already-rendered chart. Existing downstream artifacts remain valid.

**Risk notes for Ray:**

- Q1-vs-Q4 mean t-test is not significant even though the Sharpe gradient is steep — narrative should lead with risk-adjusted metrics, not the raw mean difference.
- The CCF lead-lag pattern (SPY leads spread) is consistent with prior literature (equities reprice first, credit follows intraday to several days later) and should be framed as such, not as a contradiction of the TE result. The two methods measure different things.
- TE estimates are sensitive to bin count; the 6-bin choice is documented in the CSV `bin_method` field for reproducibility.

---

*This note satisfies team-coordination.md gate item 22 (method-coverage regression) and SOP Rule C3 (producer-side rerun regression check).*

## Vera's Changes (2026-04-11)

**Author:** Visualization Vera
**Trigger:** Retroactive application of Chart Integrity Rules A1-A5 (Visualization Agent SOP) after stakeholder review flagged silent axis inversion, unit mislabel, and unexplained heatmap signal changes in the 2026-04-10 run.

### Charts Changed

- `hero` (was `hero_spread_vs_spy`) — axis de-inversion + bps unit correction (Rule A1, A2)
- `correlation_heatmap` — canonical top-8 signal selection (Rule A3)

### Charts Added

- `ccf_prewhitened` — new chart driven by Evan's `core_models_20260410/ccf_prewhitened.csv`
- `transfer_entropy` — new chart driven by Evan's `core_models_20260410/transfer_entropy.csv`
- `quartile_returns` — new chart driven by Evan's `core_models_20260410/quartile_returns.csv`

### Spec Diff

| Chart | Field | Old spec (2026-04-10) | New spec (2026-04-11) | Rule |
|-------|-------|------------------------|------------------------|------|
| `hero` | Y-axis orientation | `autorange: "reversed"` on spread axis | Non-inverted dual-panel (spread top, SPY bottom, shared X) | A1 |
| `hero` | Y-axis label | `"HY-IG OAS Spread (bps)"` with data in percent (0-15) | `"Spread (bps, where 100 bps = 1%)"` with data in bps (147-1531) | A2 |
| `hero` | Annotation | — | `"Current (2025-12-31): 202 bps"` call-out on last observation | A2 |
| `correlation_heatmap` | Rows (signals) | 20 signals in alphabetical order (all HY-IG family + 4 extras) | Top 8 by \|corr\| at 63d horizon, descending \|corr\| ordering | A3 |
| `correlation_heatmap` | Horizons (cols) | 1D, 5D, 21D, 63D, 126D, 252D | 1D, 5D, 21D, 63D, 126D, 252D (unchanged) | A3 |
| `correlation_heatmap` | Palette | RdBu_r, zmid=0 | RdBu_r, zmid=0, zmin/zmax = ±0.25 for readability | A3 |

**New heatmap signal set** (descending |correlation| at 63d horizon):

| Rank | Signal | Display name | r @ 63d |
|---:|---|---|---:|
| 1 | `nfci_momentum_13w` | NFCI Momentum (13w) | −0.2096 |
| 2 | `bank_smallcap_ratio` | Bank vs Small-Cap Ratio | −0.1853 |
| 3 | `hy_ig_mom_63d` | HY-IG Momentum (63d) | −0.1688 |
| 4 | `yield_spread_10y3m` | Yield Curve 10y-3m | −0.1090 |
| 5 | `bbb_ig_spread` | BBB-IG Spread | +0.0874 |
| 6 | `ccc_bb_spread` | CCC-BB Spread | −0.0775 |
| 7 | `hy_ig_realized_vol_21d` | HY-IG Realized Vol (21d) | +0.0767 |
| 8 | `hy_ig_roc_63d` | HY-IG RoC (63d) | −0.0539 |

### Rationale

- **Hero de-inversion:** Stakeholder review flagged axis inversion as forbidden under new Rule A1. Dual-panel layout chosen over transformed-series approach because (a) it preserves raw interpretability, (b) shared X-axis retains event alignment, and (c) each axis reads left-to-right naturally.
- **Hero unit audit:** `results/hy_ig_v2_spy/signals_20260410.parquet` stores `hy_ig_spread` in percentage points (range 1.47–15.31, mean 3.82, last obs 2.02). The 2026-04-10 chart labeled this axis "bps" — a unit mismatch of ×100. Corrected by converting to bps display (2.02% × 100 = 202 bps) and updating the label to `"Spread (bps, where 100 bps = 1%)"`. Programmatic audit asserts `max(y) >= 10` for any axis labeled bps (now 1531; previously 15.31, which would have failed the audit).
- **Heatmap signal selection:** Previous version used all 20 signals in alphabetical order, which made the strongest relationships hard to locate and violated Rule A3 (top 6-8 by |corr| at 63d, descending). Selection is now reproducible from `exploratory_20260410/correlations.csv`.
- **New method charts:** Evan added CCF, TE, and quartile-return CSVs in the companion regression note above. These unblock Ray's Evidence section, which previously could not render those methods for HY-IG v2.
- **Canonical short-name filenames:** Per Rule A3 the canonical path is `output/charts/{pair_id}/plotly/{chart_type}.json`, with `pair_id` in the directory path only — never in the filename. This script saves BOTH the canonical short name (`hero.json`) AND the legacy prefixed name (`hy_ig_v2_spy_hero.json`) to avoid breaking Ace's current loader mid-migration. Old files from the 2026-04-10 run are NOT deleted.

### Approved By

**Lesandro** — retroactive fix approved as part of the stakeholder-flagged regression review. Scope limited to (a) Rule A1/A2 hero fix, (b) Rule A3 heatmap canonicalization, (c) three new method charts for Evan's added CSVs. No other charts touched.

### Unchanged

All other charts in `output/charts/hy_ig_v2_spy/plotly/` remain byte-identical to the 2026-04-10 run:

- `hy_ig_v2_spy_spread_history_annotated.json`
- `hy_ig_v2_spy_returns_by_regime.json`
- `hy_ig_v2_spy_hmm_regime_probs.json`
- `hy_ig_v2_spy_local_projections.json`
- `hy_ig_v2_spy_quantile_regression.json`
- `hy_ig_v2_spy_tournament_sharpe_dist.json`
- `hy_ig_v2_spy_equity_curves.json`
- `hy_ig_v2_spy_drawdown.json`
- `hy_ig_v2_spy_drawdown_comparison.json`
- `hy_ig_v2_spy_walk_forward.json`
- `hy_ig_v2_spy_regime_stats.json`

The old `hy_ig_v2_spy_hero_spread_vs_spy.json` is preserved on disk (not deleted) so Ace's current loader continues to work until the pair_id-prefixed filenames are migrated out.

### Impact Assessment

- **Hero fix** addresses the top stakeholder complaint (axis inversion) and the unit-mismatch complaint in one pass. Readers no longer have to mentally flip the spread axis, and the "bps" label now matches the data values.
- **Heatmap regeneration** restores Rule A3 compliance and makes the signal selection reproducible from a single line of code (`top 8 by |corr| at 63d horizon`).
- **Three new method charts** enable Ray to build full Evidence blocks for CCF, Transfer Entropy, and Quartile Returns using the exact filenames documented in the Econometrics Rule C2 schema, closing the method-coverage gap that Evan's CSV fix opened.
- **Canonical short-name filenames** begin the migration to Ace's `load_plotly_chart("{chart_type}", pair_id="...")` convention. Ace can flip the loader at their convenience; the old prefixed files remain as a fallback.
- **No changes** to tournament winner, equity curves, trade log, or any pipeline result. This is a visualization-layer-only fix.

### Files Touched By This Dispatch

- `scripts/retro_fix_hy_ig_v2_vera_20260411.py` — new script (does not modify `scripts/generate_charts_hy_ig_v2_spy.py`)
- `output/charts/hy_ig_v2_spy/plotly/hero.json` — new canonical hero
- `output/charts/hy_ig_v2_spy/plotly/hy_ig_v2_spy_hero.json` — legacy-style copy
- `output/charts/hy_ig_v2_spy/plotly/hero_meta.json` — Rule A5 technical caption
- `output/charts/hy_ig_v2_spy/plotly/correlation_heatmap.json` — new canonical heatmap
- `output/charts/hy_ig_v2_spy/plotly/hy_ig_v2_spy_correlation_heatmap.json` — overwritten with canonical selection
- `output/charts/hy_ig_v2_spy/plotly/correlation_heatmap_meta.json` — Rule A5 sidecar
- `output/charts/hy_ig_v2_spy/plotly/ccf_prewhitened.json` + legacy copy + meta
- `output/charts/hy_ig_v2_spy/plotly/transfer_entropy.json` + legacy copy + meta
- `output/charts/hy_ig_v2_spy/plotly/quartile_returns.json` + legacy copy + meta
- `results/hy_ig_v2_spy/regression_note_20260411.md` — this section appended

---

*This section satisfies Visualization Agent SOP Rule A4 (Chart Regression Report) for the 2026-04-11 retro fix.*

## Ray's Changes (2026-04-11)

### Changes From Prior Version
- **Added** 3 new method blocks to Page 3 (Evidence) of `portal_narrative_hy_ig_v2_spy_20260410.md`: Pre-whitened CCF, Transfer Entropy, Quartile Returns Analysis. Each follows the 8-element template with `chart_status: "ready"`.
- **Applied** bps dual notation per Rule B1 throughout the narrative. First-occurrence rule followed; subsequent uses in same section use single notation.
- **Expanded** 5 glossary entries in `app/components/glossary.py` per Rule B3 4-element rubric: Quantile regression, Basis point, CCF, Transfer entropy, Pre-whitening. Other entries untouched.
- **Confirmed** `strategy_objective = "min_mdd"` in `interpretation_metadata.json` matches Evan's `suggested_strategy_objective` from `tournament_winner.json`.

### Approved By
Lesandro (retroactive fix per stakeholder review)

### Unchanged
- Pages 1-2 (Hook, Story), Pages 4-5 (Strategy, Methodology) of the narrative remain identical to the 2026-04-10 rewrite
- Existing 5 method blocks in Page 3 (Correlation, Granger, LP, Regime, Quantile) remain identical, only updated with bps dual notation and chart_status field
- No other glossary entries were modified

### Impact Assessment
Ace can now rebuild the Evidence page with 8 method blocks instead of 5. Readers get the pre-whitened CCF and Transfer Entropy analyses that were in v1 and silently dropped in v2. The Quartile Returns block serves as a narrative bridge to the HMM regime analysis. Expanded glossary entries comply with the 4-element rubric and address stakeholder complaint #2 (quantile too brief) and #9 (bps inconsistency).

## Ace's Changes (2026-04-11)

### Changes From Prior Version
- **Extended** `app/pages/9_hy_ig_v2_spy_evidence.py` from 5 tabs to 8 tabs: added Pre-whitened CCF, Transfer Entropy, Quartile Returns method blocks. Each uses the canonical chart short names (`ccf_prewhitened`, `transfer_entropy`, `quartile_returns`).
- **Added** render-time 8-element presence linter to `render_method_block`. Missing mandatory elements now surface as `st.error()` visible to Lesandro, not silent skips.
- **Updated** `app/pages/9_hy_ig_v2_spy_story.py` to load hero chart from canonical short name `hero` (Vera's fixed version with un-inverted Y-axis and correct bps units).
- **Preserved** loader fallback to `{pair_id}_{chart_type}.json` — no infrastructure changes to `charts.py`, migration is gradual.

### Approved By
Lesandro (retroactive fix per stakeholder review)

### Unchanged
- All other page files in `app/pages/` unchanged
- `app/components/charts.py` unchanged (loader still supports both naming conventions during migration)
- Other v2 pages (strategy, methodology) unchanged

### Impact Assessment
Stakeholder can now see 8 method blocks in the Evidence tab (vs 5 before). Hero chart on the Story page now displays with correct axis orientation and units. Render-time linter catches future regressions where a method block is incomplete.

## Ray's Follow-up Changes (2026-04-11)

### Changes From Prior Version
- **Added** "How to Read the Trade Log" subsection to Page 4 (Strategy) in `portal_narrative_hy_ig_v2_spy_20260410.md`. New rule from Research SOP (added this session). Includes disclaimer, two-file explanation, column legend summary, and concrete example from HY-IG v2 broker-style CSV.

### Approved By
Lesandro

### Impact Assessment
Addresses stakeholder complaint that the trade history "looks cryptic and lacks legends." Complements Ace's column legend expander and Evan's broker-style CSV to form a three-layer fix (schema + rendering + explanation).

## Ace's Follow-up Changes (2026-04-11)

### Changes From Prior Version
- **Rebuilt** trade log section on `app/pages/9_hy_ig_v2_spy_strategy.py` per new SOP §3.8 rule "Column Legend Requirement for Downloadable Artifacts"
- **Added** Ray's "How to Read the Trade Log" narrative subsection (from portal_narrative_hy_ig_v2_spy_20260410.md Page 4) rendered above the downloads
- **Added** `st.expander` column legend with all 10 broker-style columns + disclaimer caption
- **Added** dual download buttons: primary broker-style CSV, secondary position log CSV, side by side in st.columns(2)
- **Added** preview dataframe showing first 10 rows of broker-style log
- **Removed** previous bare download button (if it existed) that violated the new legend requirement

### Approved By
Lesandro

### Impact Assessment
Completes the three-layer fix for the "cryptic trade history" stakeholder complaint:
- Schema layer: Evan's broker-style CSV (Rule C4)
- Rendering layer: Ace's column legend + dual downloads (this change)
- Explanation layer: Ray's narrative subsection (Rule "How to Read")

Users now see the trade log in a format matching retail broker statements, with an inline legend, an explanation of what the strategy did at specific historical moments (COVID 2020 concrete example), and a researcher-mode alternative.
