[Econ Evan] — Mode-3 maker dispatch — pair `petrol_inv_spy`

You are Econ Evan, the econometrics agent. Resolve your full persona/SOP per the repo `./AGENTS.md` role-resolver: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, your SOP `docs/agent-sops/econometrics-agent-sop.md`, and `~/.claude/agents/econ-evan/`. Lead Lesandro (Claude) is your manager and sole checker.

## Inputs (Dana's data layer — VERIFIED by Lead, do NOT re-run stationarity, confirm only)
- Monthly analysis dataset: `data/petrol_inv_spy_monthly_latest.parquet` (429×18, 1990-01 → 2025-09).
- Daily LVCF dataset: `data/petrol_inv_spy_daily_latest.parquet` (8230×23, 1993-01 → 2025-10), incl. `days_since_release` (0–6).
- Schema sidecars: `data/petrol_inv_spy_{monthly,daily}_schema.json`.
- Stationarity: `results/petrol_inv_spy/stationarity_tests_20260617.csv`. **Levels are NON-stationary (ADF & KPSS agree). Use transforms only** — Δ, %chg, YoY, 3m/6m %, z-score (60m), YoY z-score, accel. All transforms are stationary (weekly_zscore_5y KPSS marginal — prefer yoy_zscore/delta).
- `results/petrol_inv_spy/interpretation_metadata.json`: indicator_nature=`coincident`, indicator_type=`macro`, expected_direction=`mixed`, strategy_objective=`max_sharpe`. You OWN the fields {observed_direction, direction_consistent, key_finding, confidence} — write them.

## Data provenance note (carry into your narrative honesty)
WTTSTUS1 is an EIA series NOT available on the public FRED API (FRED rejected it 2026-06-17). Source is the project Data Master.xlsx (sheet WTTSTUS1), vintage ends Oct 2025. State the source + vintage in your design note. This is acceptable, documented.

## Economic framing (state hypotheses up front)
Petroleum **inventory** (total stocks). Inventories BUILD when demand weakens — they rose sharply into the GFC (2008-09) and COVID (2020) demand collapses (see known_stress_episodes). So:
- H1 (counter-cyclical demand signal): rising/high petroleum stocks → weak fuel demand → economic slowdown → LOWER forward SPY. Tradable signal likely INVERTED level/RoC.
- H1b (supply glut, benign): stocks rise on supply, not demand — no equity signal.
- H0: petroleum stocks do NOT predict SPY.
Direction is `mixed` / empirical. **Run Granger in BOTH directions** (a coincident/possibly-lagging physical stock may be predicted BY equities — the busloans reverse-Granger precedent).

## Method scope (Cross-Asset category → full battery)
Full correlation battery (incl. distance correlation), pre-whitened CCF, Toda-Yamamoto Granger (both directions), regime/quartile returns, structural break. Add HMM 2-state regime + local projections if time permits (Cross-Asset depth). Tournament per **ECON-SR1 / ECON-T3 / ECON-T4**: BENCHMARK row carries `valid=False` and is EXCLUDED from combination counts. Honest OOS handling per DPS-FE2 / evidence_status (found_in_search vs validated — set `oos_split_record.json` + `evidence_status.json` correctly).

## Lag floor (no lookahead)
Daily: release lag is already in the LVCF + `days_since_release` (max 6 days), so a daily strategy may use L0 on the carried-forward value (it only changes the day after release). Monthly: the month-end value reflects data published within ~6 days of week-end, so L0 monthly is feasible but state your convention explicitly. Confirm and document in the design note.

## Deliverables (match `results/busloans_spy/` schema exactly)
tournament_results + manifest, tournament_winner.json, winner_summary.json, winner_trade_log.csv, winner_trades_broker_style.csv, strategy_returns + meta, oos_split_record.json, evidence_status.json, granger_by_lag.csv, rolling_correlation_*.csv, regime_quartile_returns + manifest, structural_break_*.json, subperiod_sharpe.csv, signals_<date>.parquet + manifest, signal_scope.json, core_models_<date>/, design_note.md, kpis.json, analyst_suggestions.json. Update interpretation_metadata with your owned fields.
**CRITICAL (cloud-sweep SEV1 precedent):** the winner's named signal column MUST exist in signals parquet; `winner_summary.signal_column` must match a real column.

## Conventions
- Run from repo root, project Python, `np.random.seed(42)`. HC3 robust SE. statsmodels formula API where applicable.
- Write a handoff note to `_pws/lead-lesandro/mode3_petrol_inv/evan_handoff.md` (Econ→Viz/Ray template: winner spec, observed direction, key charts needed, evidence_status).
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Print `EVAN DONE` at line start when finished (+ artifact list) or `EVAN BLOCKED: <reason>`.

Begin now.
