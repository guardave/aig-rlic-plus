[Data Dana] — Mode-1 dispatch — pair `phlxsox_spy` (stage 1)

You are Data Dana. Resolve persona via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOP `docs/agent-sops/data-agent-sop.md`, `~/.claude/agents/data-dana/`. Lead Lesandro is manager + sole checker.

## Task — build the DATA LAYER for a new pair: PHLX Semiconductor Index → SPY
- Canonical indicator id: `phlxsox` (registered in `data/prospective_pairs.csv`, status `not_started`, tag `PHLXSOX`, category technology).
- pair_id: `phlxsox_spy`. Target: SPY (daily adjusted close, from 1993).
- Branch (already created, you are on it): `pair260619_phlxsox_spy`.

## Source (Phase-0 DONE by Lead — confirmed)
- **PRIMARY: Yahoo Finance `^SOX`** (PHLX Semiconductor Index, live, daily). Confirmed quoted ~14,342 on 2026-06-18; usable history from ~1994-05. NOT in Data Master, NOT on FRED — Yahoo is the source. Pull via the yahoo-finance MCP or yfinance.
- The indicator is a **native-DAILY equity index** — this is an INTERMARKET pair (an equity index predicting the broad market), NOT a macro indicator. Treat accordingly.

## Critical constraints — this pair differs from the macro pairs
1. **Native-daily indicator → no release lag, no LVCF step-function.** ^SOX is a continuously-quoted market index, same-day close like SPY. So `days_since_release` is 0/N/A (a market index has no publication lag) — either omit it or set it constant 0 and document why (contrast the macro pairs where it tracked monthly releases). Daily cross-pair default lead is **L0**.
2. **Both series are equities → high contemporaneous correlation is expected and is NOT the signal.** The analytical question (for Evan) is whether SOX *leads* SPY beyond co-movement. Your job: provide clean transforms that enable a lead-lag analysis — SOX returns, SOX momentum (multi-horizon), and **SOX relative strength vs SPY** (e.g. SOX/SPY ratio and its momentum/z-score) are the economically interesting signal candidates. Build daily + month-end-resampled monthly datasets as usual.
3. **Stationarity:** the ^SOX level is non-stationary (trending equity index) — do NOT use the level. Run ADF/KPSS on returns, momentum (e.g. 1m/3m/6m/12m % change), the SOX/SPY ratio, ratio momentum, and z-scores. Recommend stationary signal transforms.
4. **Alignment:** align ^SOX and SPY on common trading days (both daily). Handle any history-start mismatch (SPY from 1993, ^SOX from ~1994) — use the common overlap.
5. **prospective_pairs.csv:** SURGICAL single-cell edit to set `phlxsox_spy` status to `in_progress`. Do NOT run `build_prospective_pairs.py` (BL-PROSPECTIVE-REGEN).

## Deliverables (match established schema — see `results/busloans_spy/`, `data/manifest.json`)
- `data/phlxsox_spy_daily_<start>_<end>.parquet` (+ `_latest` alias) — daily analysis dataset (native frequency), meaningful cols + datetime index, incl. SOX returns/momentum + SOX/SPY ratio transforms.
- `data/phlxsox_spy_monthly_<start>_<end>.parquet` (+ `_latest` alias) — month-end resampled, for the monthly analysis lens.
- Schema-conformant data-dictionary **sidecar JSON** (unit, dtype, direction prior, display_name, pair classification). Must pass the data sidecar schema exit 0 (DATA gate).
- `results/phlxsox_spy/stationarity_tests_<date>.csv`.
- Update `data/manifest.json` (daily TTL; additive).
- Handoff `_pws/lead-lesandro/phlxsox/dana_handoff.md` (paths via `_latest`, units, direction prior, the no-release-lag note, stationarity verdict, transform recommendation, and an explicit note on the equity-vs-equity high-correlation caveat for Evan).

## Working conventions
- Repo root, project Python env. Set seeds. Indicator classification: **technology / intermarket** (per catalog category=technology).
- Direction prior to state (hypothesis for Evan): **procyclical / leading** — semiconductors are early-cycle, high-beta; SOX strength/relative-strength may lead broad-market SPY. But equities co-move heavily — let the lead-lag analysis (not contemporaneous correlation) decide whether there's a genuine lead.
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Commit your data layer to branch `pair260619_phlxsox_spy` (META-CMP gates run; author Data Dana).
- Your final message to Lead is a factual report (artifacts, ranges, stationarity verdict, the no-release-lag + correlation caveats, commit hash), not user-facing. Or BLOCKED + reason.