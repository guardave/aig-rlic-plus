[Data Dana] — Mode-3 session dispatch — pair `m2sl_yoy_spy` (stage 1)

You are Data Dana. Resolve persona via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOP `docs/agent-sops/data-agent-sop.md`, and `~/.claude/agents/data-dana/`. Lead Lesandro (Claude) is manager + sole checker.

## Task — build the DATA LAYER for a new pair: M2 Money Supply YoY → SPY
- Canonical indicator id: `m2sl_yoy` (registered in `data/prospective_pairs.csv`, status `not_started`, tag `M2SL_YOY`).
- pair_id: `m2sl_yoy_spy`. Target: SPY (daily adjusted close, from 1993).
- Branch (already created, you are on it): `pair260619_m2sl_yoy_spy`.

## Source (Phase-0 DONE by Lead — confirmed)
- **PRIMARY: FRED `M2SL`** (M2 money stock, Billions $, Monthly, Seasonally Adjusted, 1959-01 → 2026-04, live API). Pull via the fred MCP/fredapi. The indicator is the **year-over-year % change** of M2SL (12-month % change) = `m2sl_yoy`.
- **Cross-check: Data Master.xlsx sheet `M2SL`** carries `M2SL` level + a precomputed `M2SL_YOY` column (to 2025-08). Use it to validate your YoY computation matches (the last Data Master row: 2025-08, M2SL=22195.4, M2SL_YOY=4.768%). If FRED and Data Master disagree materially on the YoY value at overlapping dates, escalate to Lead — do not guess.
- Phase-0 gate: confirm units/coverage against the Pre-master dictionary (Row 2) before finalizing.

## Critical constraints
1. **Monthly macro indicator.** Build BOTH a monthly analysis dataset AND a daily LVCF (Last-Value-Carry-Forward) dataset (see `data/busloans_spy_*.parquet` monthly shape; any daily pair for daily). Monthly cross-pair default lead is L6.
2. **`days_since_release` feature** on the daily dataset. M2 (H.6 release) publishes ~4th Tuesday of the month for the PRIOR month's data — carry the monthly value forward via LVCF from its release date; compute `days_since_release`. State the real-time release lag in your handoff so Evan sets the no-lookahead lead-grid floor.
3. **Stationarity — the key risk here.** M2SL *level* is strongly trending (secular growth, ~286 in 1959 → ~22,000 in 2025) → non-stationary, do NOT use the level as a signal. YoY % change is the headline transform but has strong regimes (the 2020-21 COVID surge to ~27% and the FIRST-EVER YoY CONTRACTION in 2022-23). Run ADF/KPSS on: YoY, MoM %, 3m/6m % change, YoY acceleration (Δ of YoY), z-score of YoY. Report which are stationary and recommend the signal transform(s). Note the 0% line (money-supply contraction) as an economically meaningful threshold.
4. **prospective_pairs.csv:** SURGICAL single-cell edit to set `m2sl_yoy_spy` status to `in_progress`. Do NOT run `build_prospective_pairs.py` (BL-PROSPECTIVE-REGEN: regen drops hand-maintained rows).

## Deliverables (match established schema — see `results/busloans_spy/`, `data/manifest.json`)
- `data/m2sl_yoy_spy_monthly_<start>_<end>.parquet` (+ `_latest` alias) — monthly analysis dataset, meaningful cols + datetime index.
- `data/m2sl_yoy_spy_daily_<start>_<end>.parquet` (+ `_latest` alias) — daily LVCF incl. `days_since_release`.
- Schema-conformant data-dictionary **sidecar JSON** (unit, dtype, direction prior, display_name, pair classification). Must pass the data sidecar schema exit 0 (DATA gate).
- `results/m2sl_yoy_spy/stationarity_tests_<date>.csv`.
- Update `data/manifest.json` (monthly TTL; additive).
- Handoff `_pws/lead-lesandro/m2sl_yoy/dana_handoff.md` (paths via `_latest` aliases, units, direction prior, release lag floor, stationarity verdict, transform recommendation).

## Working conventions
- Repo root, project Python env. Set seeds. Indicator classification: **macro** (per prospective catalog).
- Direction prior to state (hypothesis for Evan): **procyclical** — rising M2 YoY growth → liquidity tailwind → higher forward SPY; M2 contraction (2022-23) → risk-off. But let the analysis decide; note that money growth may also presage inflation→tightening (a counter-channel).
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Print `DANA DONE` at line start + artifact list, or `DANA BLOCKED: <reason>`.

Begin now.
