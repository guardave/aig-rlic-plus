[Viz Vera] — Mode-3 session dispatch — umcsent_xlv WINNER REFRESH (stage 2)

You are Viz Vera. Resolve persona via `./AGENTS.md`: read SOP `docs/agent-sops/visualization-agent-sop.md` + `~/.claude/agents/viz-vera/`. Lead Lesandro (Claude) is manager + sole checker.

## Context
umcsent_xlv's winner was corrupted in winner_summary and is now CORRECTED by Evan (Lead-verified). The WINNER-SPECIFIC charts predate the correction and must be regenerated from the new artifacts. Indicator-level charts (granger, ccf, correlation, regime quartiles, hmm, local_projections, quantile, transfer_entropy, structural_break) are NOT winner-specific and stay as-is — do NOT regenerate those.

### Corrected winner (ground truth, from Evan handoff `_pws/lead-lesandro/umcsent_refresh/evan_handoff.md`)
- UMCSENT 3-month momentum (S3_mom / `umcsent_mom`), rolling z-score > 1.0 trigger, **6-month lead**, P1 Long/Cash, target XLV.
- OOS Sharpe 1.16, OOS ann return +7.95%, max DD -0.7%, Calmar 11.3, OOS 2019-04-30→2025-12-31.
- New inputs: `results/umcsent_xlv/strategy_returns_20260420.csv`, corrected `winner_summary.json`, `winner_trade_log.csv`.

## Task — regenerate ONLY the winner-specific charts
Use `scripts/generate_charts_umcsent_xlv.py` (the existing generator) to regenerate from the corrected strategy_returns + winner_summary:
- `equity_curves` (strategy vs buy-&-hold growth) — MUST reflect the 1.16/+7.95% corrected winner.
- `drawdown` (strategy drawdown vs B&H) — MUST reflect max DD -0.7%.
- `hero` — only if it displays winner stats/positions (regenerate so any quoted Sharpe/return matches 1.16/+7.95%).
- Any other chart that overlays the winner's positions or strategy series (e.g. walk_forward / subperiod_sharpe, history_zoom position shading) — regenerate so they reflect the corrected rule.
- Refresh each regenerated chart's `_meta.json` sidecar and run the perceptual PNG render.

## Gates
- **VIZ-DP1 (axis discipline):** any dual-axis chart assigns traces to the correct axis (no invisible-trace). Verify explicitly.
- Honest annualization labeling. Colorblind-friendly, labeled axes/titles.
- Chart titles/captions that quote performance MUST match the corrected numbers (1.16 Sharpe, +7.95%, -0.7% DD) — NOT the old 1.02.
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. Do NOT regenerate indicator-level charts.

## Conventions
- Repo root, project Python. Handoff `_pws/lead-lesandro/umcsent_refresh/vera_handoff.md` (charts regenerated + any notes for Ray/Ace).
- Print `VERA DONE` at line start + chart list, or `VERA BLOCKED: <reason>`.

Begin now.
