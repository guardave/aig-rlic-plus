# ECON-H4 Handoff to Viz Vera — Lead-Horizon charts (fix260613_lead_horizon)

**From:** Econ Evan  **To:** Viz Vera  **Date:** 2026-06-13

Two charts per pair, sourced from the lead-evidence CSVs below. Same chart shapes as
permit_spy's reference blocks (`CORRELATION_LEAD_VIEW_BLOCK` → `correlations_lead_view`;
`LEAD_TOURNAMENT_BLOCK` → `lead_sharpe_distribution` in `app/pair_configs/permit_spy_config.py`).

| method | result_file | expected_chart | status |
|--------|-------------|----------------|--------|
| Lead Analysis (ECON-LA1) | results/{pair}/lead_correlation_20260613.csv | `correlations_lead_view` — heatmap, rows = signal transforms, cols = L0..L12, cell = Pearson r vs target 1m-fwd return; stars `*`/`**`; warm = positive | ready |
| Lead Tournament (ECON-LT1) | results/{pair}/lead_tournament_20260613.csv | `lead_sharpe_distribution` — bars = `best_oos_sharpe` per lead; overlay p25/median/p75 strip (`p25_oos_sharpe`/`median_oos_sharpe`/`p75_oos_sharpe`); B&H reference line | ready |

**lead_correlation CSV columns:** `transform`, `L0`..`L12` (signed r + significance stars as text), `best_lead`, `best_r`.
**lead_tournament CSV columns:** `lead_months`, `n_valid`, `best_oos_sharpe`, `median_oos_sharpe`, `p25_oos_sharpe`, `p75_oos_sharpe`, `best_signal`, `best_threshold`, `best_strategy`, `best_max_dd`.

**Pairs (8 in-place + 1 frozen):** indpro_spy, permit_spy, vix_vix3m_spy, indpro_xlp,
hy_ig_spy, umcsent_xlv, gold_copper_xli, busloans_spy in `results/{pair}/`.
Frozen Sample hy_ig_v2_spy CSVs in `results/_cross_agent/hy_ig_v2_spy_lead_readonly/`
(do NOT write charts into the Sample's results dir; Sample-frozen mandate).

**Note:** the r values in `Lx` columns are stored as formatted strings (e.g. `+0.141**`).
Strip the trailing stars to a float for the heatmap colour scale; keep stars as cell annotations.
