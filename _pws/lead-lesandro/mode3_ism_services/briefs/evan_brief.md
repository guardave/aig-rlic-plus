[Econ Evan] — Mode-3 maker dispatch — pair `ism_services_spy`

You are Econ Evan, the econometrics agent. Resolve your full persona/SOP per the repo `./AGENTS.md` role-resolver: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, your SOP `docs/agent-sops/econometrics-agent-sop.md`, and `~/.claude/agents/econ-evan/`. Lead Lesandro (Claude) is your manager and sole checker.

## Inputs (Dana's data layer — VERIFIED by Lead, do NOT re-run stationarity, confirm only)
- Monthly analysis dataset: `data/ism_services_spy_monthly_latest.parquet` (340×13, 1997-07 → 2025-10).
- Daily LVCF dataset: `data/ism_services_spy_daily_latest.parquet` (7108×18, 1997-08 → 2025-11), incl. `days_since_release` (0–32 cal days).
- Schema sidecars: `data/ism_services_spy_{monthly,daily}_schema.json`.
- Stationarity: `results/ism_services_spy/stationarity_tests_20260618.csv`. **LEVELS ARE STATIONARY** — this is a bounded diffusion index (ADF p=0.005, KPSS fail-to-reject). DO NOT mechanically difference. The level (`ism_services_pmi`) and `ism_services_gap_50` (PMI−50) are first-class signals; `ism_services_3m_change`, `ism_services_delta`, `ism_services_6m_change`, `ism_services_zscore_60m`, `ism_services_above_50` are also stationary and available. Use them all in the signal grid.
- `results/ism_services_spy/interpretation_metadata.json`: Dana set indicator_nature/indicator_type. You OWN {observed_direction, direction_consistent, key_finding, confidence} — write them.

## Data provenance note (carry into your design note honesty)
ISM Services PMI is **NOT on FRED** — ISM forced its PMI series off the public FRED API (~2023 licensing; Lead reconfirmed zero hits 2026-06-18). Source is the project `data/Data Master.xlsx` (sheet `ISM PMI`, column `CDis, CSta - ISM Services PMI`), vintage ends Oct 2025. State the source + vintage in your design note. Documented, acceptable.

## Economic framing (state hypotheses up front)
ISM Services PMI = monthly survey diffusion index; **50 is the expansion/contraction threshold**.
- H1 (procyclical, the natural prior): PMI > 50 / rising → services-sector expansion → risk-on → HIGHER forward SPY. Tradable signal likely LONG when above threshold / rising.
- H1b (sentiment already priced): survey is coincident/contemporaneous with equity sentiment → no exploitable lead.
- H0: ISM Services PMI does NOT predict forward SPY.
Direction prior is procyclical but **let the empirical analysis decide**. **Run Granger in BOTH directions** — a sentiment survey may be predicted BY equities (reverse-causality precedent from busloans). Watch for the level-vs-change distinction: the *level* (above/below 50) and the *momentum* (3m change) can carry different signals.

## Method scope (sentiment category → full battery)
Full correlation battery (incl. distance correlation), pre-whitened CCF, Toda-Yamamoto Granger (both directions), regime/quartile returns (quartile the PMI level AND the 3m change — report both), structural break. Add HMM 2-state regime + local projections (depth). Tournament per **ECON-SR1 / ECON-T3 / ECON-T4**: BENCHMARK row carries `valid=False` and is EXCLUDED from combination counts (report valid-of-total). Honest OOS handling per DPS-FE2 / evidence_status (found_in_search vs validated — set `oos_split_record.json` + `evidence_status.json` correctly).

## Lag grid / floor (no lookahead)
- Monthly: prior-month PMI publishes ~3rd business day of the following month. The month-end row is therefore NOT tradable until release. State your convention explicitly; monthly cross-pair default lead grid centers on L6 but sweep the standard grid.
- Daily: release lag already baked into LVCF + `days_since_release`; daily L0 on the carried value is feasible (value only changes the day after release). Confirm and document.

## Deliverables (match `results/busloans_spy/` schema exactly)
tournament_results + manifest, tournament_winner.json, winner_summary.json, winner_trade_log.csv, winner_trades_broker_style.csv, strategy_returns + meta, oos_split_record.json, evidence_status.json, granger_by_lag.csv, rolling_correlation_*.csv, regime_quartile_returns + manifest, structural_break_*.json, subperiod_sharpe.csv, signals_<date>.parquet + manifest, signal_scope.json, core_models_<date>/, design_note.md, kpis.json, analyst_suggestions.json. Update interpretation_metadata with your owned fields.
**CRITICAL (cloud-sweep SEV1 precedent):** the winner's named signal column MUST exist in the signals parquet; `winner_summary.signal_column` must match a real column.

## Conventions
- Run from repo root, project Python, `np.random.seed(42)`. HC3 robust SE. statsmodels formula API where applicable.
- Write handoff `_pws/lead-lesandro/mode3_ism_services/evan_handoff.md` (Econ→Viz/Ray template: winner spec, observed direction, key charts needed, evidence_status, any direction/lag reconciliation Ray must narrate).
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Print `EVAN DONE` at line start when finished (+ artifact list) or `EVAN BLOCKED: <reason>`.

Begin now.
