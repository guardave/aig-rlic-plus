[Data Dana] — Mode-3 maker dispatch — pair `ism_services_spy`

You are Data Dana, the data agent. Resolve your full persona/SOP per the repo AGENTS.md role-resolver: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, your SOP `docs/agent-sops/data-agent-sop.md`, and `~/.claude/agents/data-dana/`. Lead Lesandro (Claude) is your manager and checker in this Mode-3 wave.

## Task
Build the DATA LAYER for a new pair: **ISM Services PMI → SPY**.

- Canonical indicator id: `ism_services` (already registered in `data/prospective_pairs.csv`, status `not_started`).
- pair_id: `ism_services_spy`
- Target: SPY (daily adjusted close, from 1993).
- Branch (already created, you are on it): `feat_ism_services_spy`.

## CRITICAL — data source (Phase-0 already done by Lead; DO NOT re-pull from FRED)
**ISM forced its PMI series OFF FRED (~2023 licensing). FRED has ZERO ISM series — Lead confirmed.** The authoritative source is the offline dictionary:
- File: `data/Data Master.xlsx`, sheet **`ISM PMI`**.
- Column **`CDis, CSta - ISM Services PMI`** = the headline ISM Services PMI (THIS pair's indicator).
- Coverage: **monthly, 1997-07 → 2025-10** (~340 obs), values oscillate around 50 (diffusion index).
- The same sheet also has `G - ISM Services PMI, price` — that is the SEPARATE `ism_services_price_xli` pair (different target). **Do NOT include it. Headline only.**
- Phase-0 gate: cross-check the column header/units against the Pre-master dictionary sheet (Row 2 = description/units/source/frequency, per memory reference_pre_master_row2). If the Pre-master and the `ISM PMI` sheet disagree on units/coverage, escalate to Lead — do not guess.

## Critical constraints
1. **Monthly-native indicator, diffusion index.** Build BOTH a monthly analysis dataset AND a daily LVCF (Last-Value-Carry-Forward) dataset, matching the established schema (see `data/busloans_spy_*.parquet` monthly shape; any daily pair for daily shape). Monthly cross-pair default is lead L6.
2. **`days_since_release` feature** on the daily dataset (weekly→/monthly→daily step-function lineage). ISM Services PMI releases on/around the **3rd business day of each month** for the PRIOR month's reference period. Carry the monthly value forward via LVCF from its release date, and compute `days_since_release`. Document in the dictionary sidecar.
3. **Real-time lag floor.** State the release lag explicitly in your handoff (prior-month data published ~3rd business day of current month → ~3-5 day lag from reference month-end) so Evan sets the tournament lead-grid floor with NO lookahead.
4. **Stationarity — diffusion-index nuance.** A PMI oscillates around 50 and is bounded/mean-reverting, so **levels may already be stationary** (unlike the trending series in prior pairs — do NOT assume you must difference). Run ADF/KPSS on level, Δ, 3-month change, and z-score. Report honestly which transform(s) achieve stationarity and recommend accordingly. Note the 50 boundary as the natural expansion/contraction threshold.
5. **prospective_pairs.csv:** SURGICAL single-cell edit to set `ism_services_spy` status to `in_progress`. DO NOT run `build_prospective_pairs.py` (BL-PROSPECTIVE-REGEN: regen drops hand-maintained rows).

## Deliverables (match established schema — see `results/busloans_spy/`, `data/manifest.json`)
- `data/ism_services_spy_monthly_<start>_<end>.parquet` (+ `_latest` alias) — monthly analysis dataset, meaningful cols + datetime index.
- `data/ism_services_spy_daily_<start>_<end>.parquet` (+ `_latest` alias) — daily LVCF dataset incl. `days_since_release`.
- Schema-conformant data-dictionary **sidecar JSON** (unit, dtype, direction prior, display_name, pair classification). Must pass the data sidecar schema with exit code 0 (DATA gate).
- `results/ism_services_spy/stationarity_tests_<date>.csv`.
- Update `data/manifest.json` (monthly TTL; additive edit).
- Handoff `_pws/lead-lesandro/mode3_ism_services/dana_handoff.md` using the Data→Econometrics template (paths via `_latest` aliases, units, direction prior, lag floor, stationarity verdict, transform recommendation).

## Working conventions
- Run from repo root `/workspaces/aig-rlic-plus`. Project Python env. Set seeds.
- Indicator classification: **sentiment** (survey diffusion index), per prospective_pairs catalog + research-agent-sop.
- Direction prior to state (as hypothesis, for Evan): ISM Services > 50 = expansion → risk-on → procyclical with SPY is the natural prior. Note it; let the analysis decide.
- Do NOT touch any other pair's files. Frozen sample `hy_ig_v2_spy` is untouchable.
- When done, print a line-start `DANA DONE` line + artifact list. If blocked, print `DANA BLOCKED: <reason>` and stop.

Begin now.
