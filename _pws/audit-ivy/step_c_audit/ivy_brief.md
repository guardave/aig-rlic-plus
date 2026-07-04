Ivy — Independent QA Audit (Codex-backed, INDEPENDENT of the Claude team)

Resolve persona via ./AGENTS.md (read ~/.claude/CLAUDE.md, ./CLAUDE.md, your auditor role, and docs/agent-sops/ as relevant). You are Ivy: a skeptical, independent auditor. Re-derive findings from PRIMARY artifacts (winner_summary.json, tournament CSVs, signals parquet, chart JSON, configs) — do NOT take the team's claims on trust. Baseline for "what changed" = `git diff origin/main...HEAD` (branch `fix260703_step_c_yyy_ks_af_alex` @ f2c6390; main @ ea08f5b).

## What this branch claims to do
27 fixes on branch fix260703_step_c_yyy_ks_af_alex: 26 Step C reviewer comments (YYY/KS/AF/Alex_UK) + the t10y3m published-winner vline-position fix. Commits: 13b3bcc (vline), 7c7da6d (26 items), 705a492 (merge), f2c6390 (SOX drawdown legend).

## Your audit scope — verify each, INDEPENDENTLY from primary data

### A. Data-integrity (HIGHEST priority — trust-critical)
1. **gold_copper_xli drawdown (#159):** chart `output/charts/gold_copper_xli/plotly/drawdown.json` must plot the OOS window (2020-01→2025-12) with trough = canonical `oos_max_drawdown` in `results/gold_copper_xli/winner_summary.json` (claimed −8.25%). Recompute the OOS drawdown from `results/gold_copper_xli/signals_*.parquet` `strategy_return` and confirm the plotted trough matches. Confirm the OLD full-sample −19.34% is GONE.
2. **phlxsox_spy drawdown (#181):** `output/charts/phlxsox_spy/plotly/drawdown.json` — recompute winner/B&H/SPY-mom OOS drawdowns from `strategy_returns_20260619.csv` sliced to OOS (2021-06-11→2026-06-17), cummax re-based to OOS start. Claimed troughs −9.66% / −24.50% / −23.69%. Confirm plotted values match and full-sample (−65%) is gone. Confirm `equity_curves` was NOT changed to OOS (it should stay full-sample).
3. **Chart-vs-CSV byte integrity:** for every regenerated chart (gold drawdown; phlxsox drawdown, granger_f_by_lag, ccf_prewhitened, correlation_heatmap; vix subperiod_sharpe), confirm the numeric series still byte-match their source CSV/parquet — i.e. only PRESENTATION changed, no data drift. Granger F-values, CCF values (incl. lag-0 0.7088), heatmap z, subperiod bars.
4. **Loader fixes (#157/#158):** in `app/components/page_templates.py`, confirm total_combos for gold = 90 (from `tournament_results_20260526.csv`, rows−benchmark) and Win Rate fallback oos_win_rate→win_rate gives gold 21% (win_rate 0.2146) / hy_ig 50%, WITHOUT changing the 9 pairs that have oos_win_rate. Check the guard is `is not None` (0.0 win rate must not be treated as missing).
5. **vline (#... t10y3m):** `output/charts/t10y3m_spy/plotly/lead_sharpe_distribution.json` — the published-winner vline must sit at category index for L6 (winner lead_value=6 on grid [0,1,2,3,6,9,12] → index 4), NOT at raw x=6 (=L12). Confirm bars still byte-match `lead_tournament_20260622.csv`. Confirm the other 12 pairs' lead charts are byte-unchanged vs main.

### B. Honesty / consistency of narrative edits
6. Spot-check the narrative/config edits do NOT introduce FALSE or unsupported quantitative claims. In particular: SOX new panels (#182 Executive Confidence, #180 Advanced Evidence, #183 framing) in `phlxsox_spy_config.py` — every number cited must exist in `results/phlxsox_spy/winner_summary.json` or existing evidence blocks; the "Candidate / low-confidence / feedback-not-leadership" framing must be consistent with the actual evidence (search-found, no frozen-rule holdout). Flag any overstatement.
7. #151 INDPRO naming: confirm no stray non-INDPRO index refs remain AND no cross-pair contamination introduced (RES-NR1). #154 (r=0.225 weak) and #175/#176 (M2) claims must match artifacts.
8. VIX glossary (#146) + footnote (#150) copy: no fabricated definitions that contradict the data; direction consistent with `results/vix_vix3m_spy/winner_summary.json` (countercyclical).

### C. Schema / gates
9. Confirm all schema-required contracts still hold: run `python3 scripts/validate_all_schemas.py` and `python3 scripts/lint_chart_completeness.py` — report pass/fail counts. Confirm no pair regressed to non-conforming.
10. Confirm pairs NOT touched by this branch render byte-identically (no collateral changes to other pairs' configs/charts).

## Output
Write your full findings to `_pws/audit-ivy/step_c_audit/ivy_report.md` (verdict per item A1–C10: CONFIRM / ISSUE + evidence). Then print, at line start:
- `IVY DONE` if every item CONFIRMS (no issues), or
- `IVY ISSUES: <n>` followed by a one-line summary of each issue.
Be rigorous and adversarial. If a claimed value is off by any margin, or a chart's data drifted, or a narrative overstates — flag it with the primary-data evidence. Do not fix anything; report only (Lead handles fixes).
