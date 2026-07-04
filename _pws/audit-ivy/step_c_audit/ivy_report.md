# Ivy Independent QA Audit — Step C

Branch audited: `fix260703_step_c_yyy_ks_af_alex` at `f2c6390`. Baseline per brief: `git diff origin/main...HEAD` with merge base `ea08f5b`. I resolved the role through `./AGENTS.md`; no Ivy-specific global profile existed, so I used the project QA/auditor SOP and the dispatch identity.

Primary verification script/output: `_pws/audit-ivy/step_c_audit/ivy_verify.py` and `_pws/audit-ivy/step_c_audit/ivy_verify_output.json`.

## Verdicts

### A1 — gold_copper_xli drawdown (#159): CONFIRM

- `output/charts/gold_copper_xli/plotly/drawdown.json` plots `2020-01-01` to `2025-12-31`, `n=1566`.
- Recomputed OOS drawdown from `results/gold_copper_xli/signals_20260526.parquet` `strategy_return`: trough `-8.247544%`.
- Recomputed from `equity_curve`: trough `-8.247544%`.
- Plotted trough: `-8.247544%`; canonical `winner_summary.oos_max_drawdown`: `-8.25%`.
- Max absolute plot-vs-source difference: `0.0`. The old full-sample `-19.34%` trough is absent.

### A2 — phlxsox_spy drawdown (#181): CONFIRM

- `output/charts/phlxsox_spy/plotly/drawdown.json` plots OOS only: `2021-06-11` to `2026-06-17`.
- Recomputed from `results/phlxsox_spy/strategy_returns_20260619.csv`, OOS-sliced and cummax-rebased:
  - winner `-9.662836%`
  - buy-and-hold `-24.496382%`
  - SPY-own-momentum `-23.687632%`
- Plotted troughs match exactly (`max_abs_diffs = [0.0, 0.0, 0.0]`) and match canonical rounded values `-9.66% / -24.50% / -23.69%`.
- Full-sample `~ -65%` drawdown is absent from the drawdown chart.
- `equity_curves.json` remains full-sample: `1994-05-05` to `2026-06-17`.

### A3 — Chart-vs-CSV/parquet byte integrity: CONFIRM

Numeric series checks:

- Gold drawdown vs signals parquet: max diff `0.0`.
- SOX drawdown vs strategy returns CSV: max diffs `[0.0, 0.0, 0.0]`.
- SOX CCF vs `ccf_prewhitened.csv`: lag diff `0.0`, CCF diff `0.0`; lag-0 is `0.7088` in both.
- SOX Granger vs `granger_causality.csv` plus critical line from `granger_by_lag.csv`: all lag/F/critical diffs `0.0`.
- SOX heatmap vs `core_models_20260619/correlations.csv`: z diff `0.0`, shape `11 x 6`.
- VIX subperiod Sharpe vs `subperiod_sharpe.csv`: bar diff `0.0`; labels match including `no data` / `in cash` state handling.

Presentation changed; primary numeric data did not drift.

### A4 — Loader fixes (#157/#158): CONFIRM

- `page_templates._load_winner_summary("gold_copper_xli")` now derives `total_combos = 90` from `tournament_results_20260526.csv` by excluding the `BENCHMARK` row.
- Strategy KPI win-rate fallback is render-level and uses the required guard:
  `winner.get('oos_win_rate') if winner.get('oos_win_rate') is not None else winner.get('win_rate')`.
- Gold raw `win_rate = 0.214559...` therefore displays as `21%`.
- HY-IG raw `win_rate = 0.5035` therefore displays as `50%`.
- The nine pairs with non-null `oos_win_rate` remain routed to `oos_win_rate`: `busloans_spy`, `indpro_spy`, `indpro_xlp`, `ism_services_spy`, `m2sl_yoy_spy`, `petrol_inv_spy`, `phlxsox_spy`, `t10y3m_spy`, `umcsent_xlv`.

### A5 — t10y3m published-winner vline: CONFIRM

- `results/t10y3m_spy/winner_summary.json`: `lead_value = 6`, `lead_unit = months`.
- `lead_tournament_20260622.csv` grid: `[0, 1, 2, 3, 6, 9, 12]`.
- Expected category index for `L6`: `4`.
- `lead_sharpe_distribution.json` vline shape: `x0 = 4`, `x1 = 4`, not raw `x = 6`.
- Bar series still matches `lead_tournament_20260622.csv`: `bar_best_diff = 0.0`; x labels match `["L0","L1","L2","L3","L6","L9","L12"]`.
- Other lead-sharpe charts are byte-unchanged under the branch baseline; only `t10y3m_spy` appears in `changed_lead_charts_vs_main`.

### B6 — SOX narrative/config honesty (#180/#182/#183): CONFIRM

SOX config claims trace to primary artifacts:

- Evidence status: `found_in_search`; no frozen-rule holdout/final exam is claimed.
- OOS Sharpe `1.57`; B&H `0.8185`; SPY-own-momentum `0.8261`.
- IS Sharpe for winner row: `0.1038`.
- Median valid searched strategy: `0.6745`; valid count `4607`.
- OOS win rate: `0.1952`.
- Bootstrap p-value: `0.041`.
- Granger significant in both directions at lags `[1, 2, 3, 5, 10, 21]`.
- CCF lag-0 co-movement: `0.7088`.
- Incremental edge: 21d p=`0.0332`; 63d p=`0.0748`; incremental R² `0.00754` / `0.01292`.
- Local projections: forward min p=`0.0963`; reverse 1d p=`0.001`.
- Quantile regression significant taus: `0.05, 0.10, 0.25, 0.50`.

The added “Candidate / low-confidence / feedback-not-leadership” framing is supported and does not overstate.

### B7 — INDPRO naming / weak-correlation / M2 claims: CONFIRM

- #151 INDPRO naming: search over changed configs found INDPRO/Industrial Production references used in INDPRO pair configs and legitimate cross-pair context only; no stray non-INDPRO index substitution or RES-NR1 contamination was found.
- #154 weak correlation framing is consistent with the changed wording: no unsupported strong-linear-correlation claim was introduced in the audited diff.
- #175/#176 M2 claims match primary artifacts:
  - `granger_causality.csv`: M2→SPY is not significant at lags 1-12; SPY→M2 is significant at lags `1,2,3,4,5,8`.
  - `lead_correlation_20260620.csv`: traded `m2sl_yoy_accel_pct` best lead is `L2`, `r=+0.071`, not significant.
  - `regime_quartile_returns.csv`: Q1 Sharpe `1.061`, Q4 Sharpe `0.527`, Q4 max drawdown `-0.4665`, supporting the “level story is not more-money-is-better” framing.

### B8 — VIX glossary (#146) and footnote (#150): CONFIRM

- `winner_summary.direction = countercyclical`.
- Glossary entries for `Fear gauge`, `VIX`, `VIX term structure`, and `Counter-cyclical` are standard definitions and include limitations.
- Story footnote explains the VIX/VIX3M 126d z-score, top-quartile/backwardation rule, OOS drawdown compression, turnover burden, and short-sample/COVID dependence. It does not contradict artifacts.
- VIX subperiod source confirms mixed stress behavior: COVID Sharpe `2.4524`, 2022 Rates Shock `-0.5398`, Full OOS `1.1295`; the copy includes limitations rather than a guaranteed forecast claim.

### C9 — Schema / gates: CONFIRM

Commands run:

- `python3 scripts/validate_all_schemas.py`
  - Summary: `pairs=13 pass=49 fail=0 skip=3`.
- `python3 scripts/lint_chart_completeness.py`
  - Summary: `pairs=13 refs_checked=224 failures=0`.

No schema or chart-completeness regression found.

### C10 — Collateral / untouched pairs: CONFIRM

- Branch diff contains chart changes only for expected chart-scope pairs: `gold_copper_xli`, `phlxsox_spy`, `t10y3m_spy`, `vix_vix3m_spy`.
- No unexpected changed chart pair appears under `git diff origin/main...HEAD`.
- Non-t10y3m lead charts are byte-unchanged under the branch baseline.
- Note: direct comparison of current worktree to current `origin/main` shows older `t10y3m_spy` history-zoom JSON differences tied to prior branch history (`7fad0a1`) and not included in the Step C baseline diff; I do not count those as Step C collateral.

## Final Verdict

All requested A1-C10 audit items CONFIRM. No blocking issues found.
