[Econ Evan] — Mode-3 session dispatch — pair `m2sl_yoy_spy` (stage 2)

You are Econ Evan. Resolve persona via `./AGENTS.md`: read SOP `docs/agent-sops/econometrics-agent-sop.md` + `~/.claude/agents/econ-evan/`. Lead Lesandro is manager + sole checker.

## Inputs (Dana's data layer — VERIFIED by Lead; confirm only, don't re-run stationarity)
- Monthly: `data/m2sl_yoy_spy_monthly_latest.parquet` (400×14, 1993-01 → 2026-04).
- Daily LVCF: `data/m2sl_yoy_spy_daily_latest.parquet` (8403×19, incl. `days_since_release`).
- Schema sidecars: `data/m2sl_yoy_spy_{monthly,daily}_schema.json`.
- Stationarity: `results/m2sl_yoy_spy/stationarity_tests_20260619.csv`. **M2SL level is NON-stationary — do NOT use the level.** Stationary, usable signals: `m2sl_pct_yoy` (headline), `m2sl_pct_mom`, `m2sl_3m_pct`, `m2sl_6m_pct`, `m2sl_yoy_accel_pct`, `m2sl_yoy_zscore_120m`, plus the binary `m2sl_contraction_flag` (M2 YoY < 0).
- `results/m2sl_yoy_spy/interpretation_metadata.json`: Dana set indicator_nature/type. You OWN {observed_direction, direction_consistent, key_finding, confidence}.

## Data provenance (carry into design_note)
Source = **FRED `M2SL`** (live API, current vintage, 1959-01→2026-04). The Data Master M2SL snapshot is a stale vintage (~0.5% above current FRED at recent dates due to M2 SA revisions) — FRED is ground truth. State source + that M2 is a revised series.

## Economic framing (state hypotheses up front)
M2 money-supply YoY growth vs SPY.
- H1 (procyclical / liquidity): rising M2 YoY → liquidity tailwind → HIGHER forward SPY; M2 **contraction** (the first-ever YoY decline, 2022-23) → risk-off (coincided with the 2022 bear). Tradable signal likely long when YoY growth strong / contraction_flag off.
- H1b (inflation counter-channel): excessive M2 growth → inflation → Fed tightening → equity HEADWIND at a lag. So the level-vs-acceleration distinction may matter (accelerating money vs already-high money).
- H0: M2 YoY does not predict forward SPY.
Direction is **empirical** — let analysis decide. **Run Granger BOTH directions** — monetary aggregates and equities are jointly driven by Fed policy / the cycle; reverse causality (markets→money) is plausible. Watch the `m2sl_contraction_flag` as a potentially strong regime discriminator.

## Method scope (macro category → full battery)
Full correlation battery (incl. distance correlation), pre-whitened CCF, Toda-Yamamoto Granger (both directions), regime/quartile returns (quartile the YoY level AND test the contraction_flag regime), structural break (expect one around 2020 + 2022), HMM 2-state, local projections. Tournament per **ECON-SR1 / ECON-T3 / ECON-T4** (BENCHMARK row valid=False, EXCLUDED from combo counts; report valid-of-total). Honest OOS per DPS-FE2 / evidence_status (set oos_split_record.json + evidence_status.json).

## Lag grid / floor (no lookahead)
- Monthly: M2 (H.6) publishes ~4th Tuesday for prior month → state the real-time floor (from Dana's handoff); monthly default grid centers L6, sweep the standard grid.
- Daily: release lag baked into LVCF + `days_since_release`; daily L0 on the carried value feasible. Confirm + document.

## Deliverables (match `results/busloans_spy/` schema exactly)
tournament_results + manifest, tournament_winner.json, winner_summary.json, winner_trade_log.csv, winner_trades_broker_style.csv, strategy_returns + meta, oos_split_record.json, evidence_status.json, granger_by_lag.csv, rolling_correlation_*.csv, regime_quartile_returns + manifest, structural_break_*.json, subperiod_sharpe.csv, signals_<date>.parquet + manifest, signal_scope.json, core_models_<date>/, design_note.md, kpis.json, analyst_suggestions.json. Update interpretation_metadata owned fields.
**CRITICAL (cloud-sweep SEV1 + the umcsent precedent THIS WEEK):** the winner's named signal column MUST exist in the signals parquet; `winner_summary.signal_column` must match a real column; and `winner_summary`'s threshold/lead encoding MUST faithfully reflect the selected tournament row (threshold_code + rule + value + lead_value/unit) — do NOT mis-serialize them. After writing winner_summary, RECOMPUTE the OOS Sharpe from your strategy_returns using the encoded rule and confirm it matches the headline (±0.03). If it doesn't, the encoding is wrong — fix before DONE.

## Conventions
- Repo root, project Python, `np.random.seed(42)`. HC3 robust SE. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Handoff `_pws/lead-lesandro/m2sl_yoy/evan_handoff.md` (winner spec, observed direction, key charts needed, evidence_status, any direction/lag reconciliation Ray must narrate).
- Print `EVAN DONE` at line start + artifact list, or `EVAN BLOCKED: <reason>`.

Begin now.
