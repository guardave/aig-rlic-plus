[Econ Evan] — Mode-1 dispatch — pair `phlxsox_spy` (stage 2)

You are Econ Evan. Resolve persona via `./AGENTS.md`: SOP `docs/agent-sops/econometrics-agent-sop.md` + `~/.claude/agents/econ-evan/`. Lead Lesandro is manager + sole checker.

## Inputs (Dana's data layer — VERIFIED by Lead; confirm only)
- Daily: `data/phlxsox_spy_daily_latest.parquet` (8085×24, 1994-05 → 2026-06).
- Monthly: `data/phlxsox_spy_monthly_latest.parquet` (386×17, month-end).
- Stationarity: `results/phlxsox_spy/stationarity_tests_*.csv`. **Levels NON-stationary (sox, sox_spy_ratio) — do NOT use.** Stationary signals: `sox_ret`, `sox_mom_{1,3,6,12}m_pct`, `sox_spy_ratio_mom_{1,3,6}m_pct` (relative strength), rel-strength z-score (regime feature).
- `days_since_release` is constant 0 (continuously-quoted index; no lag). Daily default L0, but the LEAD question is at L1+ (see below).
- interpretation_metadata: Dana set indicator_nature=leading / type=price / direction=procyclical. You OWN {observed_direction, direction_consistent, key_finding, confidence}.

## THE central challenge for THIS pair (binding — this is where it's easy to ship a false positive)
SOX and SPY are BOTH equities; daily return correlation = **0.709**. A contemporaneous regression / level correlation will look hugely significant from shared market beta alone — that is **co-movement, not predictive edge**. Your job is to establish whether SOX genuinely **LEADS** SPY:
1. **Lead-lag only:** Toda-Yamamoto Granger BOTH directions at lags ≥1; pre-whitened CCF (pre-whitening removes each series' own autocorrelation — essential here). Report whether lagged SOX predicts forward SPY beyond SPY's OWN past.
2. **Beat the trivial benchmark:** a "SOX momentum → long SPY" rule on a high-beta proxy can just be leveraged market trend-following. Compare the winner against a SPY-own-momentum benchmark (and buy&hold). If the SOX signal does NOT beat SPY's own momentum, SAY SO — the honest finding may be "SOX adds no lead beyond SPY's own trend." Lean on the **relative-strength** transforms (sox_spy_ratio_mom), which partial out common beta, as the signals most likely to carry genuine intermarket information.
3. Direction prior is leading/procyclical — but let the lead-lag evidence decide, and be skeptical.

## Method scope (technology/intermarket → full battery)
Full correlation battery, pre-whitened CCF, Toda-Yamamoto Granger (both directions), regime/quartile returns, structural break, HMM, local projections. Tournament per **ECON-SR1 / ECON-T3 / ECON-T4** (BENCHMARK row valid=False, excluded from combo counts). Honest OOS per DPS-FE2 / evidence_status. Include the SPY-own-momentum comparison in your design_note / kpis.

## winner_summary integrity (umcsent precedent THIS WEEK — do NOT repeat)
The winner's named signal column MUST exist in the signals parquet; threshold/lead encoding MUST faithfully reflect the selected tournament row (threshold_code + rule + value + lead_value/unit). **After writing winner_summary, RECOMPUTE OOS Sharpe from strategy_returns using the encoded rule and confirm it matches the headline within ±0.03** — if not, fix the encoding before declaring done. np.random.seed(42).

## Deliverables (match `results/busloans_spy/` schema exactly)
Full set: tournament_results + manifest, tournament_winner.json, winner_summary.json, winner_trade_log.csv, winner_trades_broker_style.csv, strategy_returns + meta, oos_split_record.json, evidence_status.json, granger_by_lag.csv, rolling_correlation_*.csv, regime_quartile_returns + manifest, structural_break_*.json, subperiod_sharpe.csv, signals_<date>.parquet + manifest, signal_scope.json, core_models_<date>/, design_note.md, kpis.json, analyst_suggestions.json. Update interpretation_metadata owned fields.

## Conventions
- Repo root, project Python. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Commit results to branch `pair260619_phlxsox_spy` (META-CMP gates run; author Econ Evan).
- Handoff `_pws/lead-lesandro/phlxsox/evan_handoff.md` (winner spec, observed direction, the SOX-leads-or-not verdict + does-it-beat-SPY-momentum result, evidence_status, charts Vera needs, reconciliation Ray must narrate).
- Final message to Lead = factual report (winner spec, recompute-guardrail result, the lead-vs-comovement verdict, artifacts, commit hash). Or BLOCKED.