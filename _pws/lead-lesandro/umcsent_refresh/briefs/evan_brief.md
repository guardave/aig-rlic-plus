[Econ Evan] — Mode-3 session dispatch — umcsent_xlv WINNER REFRESH (stage 1)

You are Econ Evan. Resolve persona via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOP `docs/agent-sops/econometrics-agent-sop.md`, and `~/.claude/agents/econ-evan/`. Lead Lesandro (Claude) is manager + sole checker.

## Context — a partial-regeneration inconsistency (NOT a fresh pair)
`results/umcsent_xlv/` is internally inconsistent. The WINNER is settled and is GROUND TRUTH — **do NOT re-run the tournament or re-select a winner.** Some winner-specific downstream artifacts are stale or missing and must be regenerated to match the settled winner.

### Settled winner (ground truth — pin to this, do NOT change it)
- signal_column `umcsent_mom` (signal_code `S3_mom`), threshold_rule `gt`, threshold_value `6.95316`, strategy_family `P1_long_cash`, **lead_value None (no lead)**, target XLV.
- Headline (from `results/umcsent_xlv/winner_summary.json`): oos_sharpe 1.1586, oos_ann_return 0.079494, oos_max_drawdown -0.007007, OOS 2019-04-30 → 2025-12-31.
- `signals_20260420.parquet` already carries the `umcsent_mom` column. `winner_summary.json`, `winner_trade_log.csv`, `tournament_results_20260420.csv` are CURRENT (Jun 16) — do not touch them.

## Task — regenerate ONLY the winner-specific artifacts that are stale/missing, consistent with the settled winner
1. **`strategy_returns_<date>.csv` — MISSING.** Produce the per-period strategy return series for the settled winner rule (umcsent_mom gt 6.95316, P1_long_cash, no lead) applied to XLV, over the full sample + OOS window. Use the existing producer `scripts/pair_pipeline_umcsent_xlv.py` strategy-construction logic, or reconstruct directly from `signals_20260420.parquet` + the winner rule — whichever guarantees the series matches the settled winner. Add the meta sidecar if the schema expects one.
2. **`winner_trades_broker_style.csv` — STALE (Apr 23, old winner).** Regenerate the canonical APP-TL1 broker-style CSV for the settled winner's trades (from `winner_trade_log.csv` / the shared `scripts/_trade_log_broker.py` helper).
3. **`interpretation_metadata.json` `key_finding` — STALE.** It currently reads "UMCSENT umcsent_zscore predicts xlv_fwd_6m (...)" — that's the OLD 6-month-lead basis. Rewrite `key_finding` (your owned field) to describe the SETTLED winner: umcsent_mom (3-month momentum), no lead, P1 Long/Cash, OOS Sharpe ~1.16, min-MDD objective. Preserve your other owned fields (observed_direction=procyclical, direction_consistent, confidence) and do NOT touch fields owned by Dana/Ray.

## Verify before you hand off (Lead will re-check)
- Recompute OOS Sharpe from your regenerated `strategy_returns` over 2019-04-30→2025-12-31 — it MUST be ≈ 1.16 (±0.03). If it isn't, STOP and print `EVAN BLOCKED: <recomputed sharpe> != winner_summary 1.16` — that means the winner rule and the series disagree and Lead must investigate before proceeding.
- `winner_summary.signal_column` (`umcsent_mom`) must exist in the signals parquet (it does — confirm).
- Schema-validate any JSON you touch (winner_summary, interpretation_metadata, signal_scope) — exit 0.

## Conventions
- Run from repo root, project Python, `np.random.seed(42)`. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. Do NOT re-run the tournament or change the winner.
- Write handoff `_pws/lead-lesandro/umcsent_refresh/evan_handoff.md` (what you regenerated, the recomputed OOS Sharpe, exactly which winner-specific facts Vera/Ray must use: signal=umcsent_mom 3m momentum, no lead, Sharpe 1.16, return 7.95%, max DD -0.7%).
- Print `EVAN DONE` at line start + artifact list when finished, or `EVAN BLOCKED: <reason>`.

Begin now.
