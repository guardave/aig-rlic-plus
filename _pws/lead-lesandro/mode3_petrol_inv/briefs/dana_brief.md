[Data Dana] — Mode-3 maker dispatch — pair `petrol_inv_spy`

You are Data Dana, the data agent. Resolve your full persona/SOP per the repo AGENTS.md role-resolver: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, your SOP `docs/agent-sops/data-agent-sop.md`, and `~/.claude/agents/data-dana/`. Lead Lesandro (Claude) is your manager and checker in this Mode-3 wave.

## Task
Build the DATA LAYER for a new pair: **Petroleum Inventory → SPY**.

- Canonical indicator id: `petrol_inv` (already registered in `data/prospective_pairs.csv`, status `not_started`).
- pair_id: `petrol_inv_spy`
- Source series: **FRED `WTTSTUS1`** — Weekly U.S. Ending Stocks of Total Petroleum Products (thousand barrels). EIA weekly release calendar.
- Target: SPY (daily adjusted close, from 1993).
- Branch (already created, you are on it): `pair260617_petrol_inv_spy`.

## Critical constraints
1. **WTTSTUS1 is WEEKLY** — the first weekly-native indicator in this project. Frequency alignment is the key risk. Per `docs/data-series-catalog.md`: weekly→monthly aggregation for the monthly analysis dataset; weekly→daily uses Last-Value-Carry-Forward (LVCF) carried until next weekly release. Produce BOTH a monthly analysis dataset AND a daily LVCF dataset, exactly as prior pairs deliver (see `data/busloans_spy_*.parquet` for the monthly shape and any daily pair for the daily shape).
2. **Add a `days_since_release` feature** to the daily dataset (your own prior review flagged this gap for weekly→daily step-functions). Document it in the data dictionary sidecar.
3. **Real-time lag floor:** WTTSTUS1 weekly figure publishes ~5-6 days after the report week (EIA Wednesday release for prior-week data). State the real-time availability lag explicitly in your handoff so Evan sets the tournament lead-grid floor correctly (no lookahead).
4. **Stationarity:** run ADF/KPSS on levels and transforms (Δ, %Δ, YoY, z-score). Petroleum stocks have strong seasonality (refinery turnarounds, driving season) AND a secular trend — flag both. Recommend the transform(s) that achieve stationarity.
5. **prospective_pairs.csv:** make a SURGICAL edit to set `petrol_inv_spy` status to `in_progress`. DO NOT run `build_prospective_pairs.py` to regenerate (BL-PROSPECTIVE-REGEN: regen drops hand-maintained rows). Edit the single cell.
6. **Phase 0 gate:** confirm WTTSTUS1 against the Data Master pre-master dictionary (Pre-master col 39 per data-series-catalog) before pulling. If FRED and Data Master disagree on units/coverage, escalate to Lead — do not guess.

## Deliverables (match the established schema — see `results/busloans_spy/` and `data/manifest.json`)
- `data/petrol_inv_spy_monthly_<start>_<end>.parquet` (+ `_latest` alias) — monthly analysis dataset with meaningful columns + datetime index.
- `data/petrol_inv_spy_daily_<start>_<end>.parquet` (+ `_latest` alias) — daily LVCF dataset incl. `days_since_release`.
- Schema-conformant data-dictionary **sidecar JSON** (unit, dtype, direction, display_name, pair classification) — this is what Evan/Vera/Ray/Ace consume. Validate it passes the data sidecar schema with exit code 0 (DATA gate).
- `results/petrol_inv_spy/stationarity_tests_<date>.csv`.
- Update `data/manifest.json` (mixed-freq TTL = fastest series = weekly; note it).
- A handoff note `_pws/lead-lesandro/mode3_petrol_inv/dana_handoff.md` using the Data→Econometrics handoff template (file paths via `_latest` aliases, units, direction prior, lag floor, stationarity verdict, transform recommendation).

## Working conventions
- Run from repo root `/workspaces/aig-rlic-plus`. Use the project Python env. Set seeds.
- Indicator classification: Cross-Asset (physical commodity stock), per research-agent-sop.
- Do NOT touch any other pair's files. Frozen sample `hy_ig_v2_spy` is untouchable.
- When done, print a clear `DANA DONE` line and the list of artifacts written. If blocked, print `DANA BLOCKED: <reason>` and stop.

Begin now.
