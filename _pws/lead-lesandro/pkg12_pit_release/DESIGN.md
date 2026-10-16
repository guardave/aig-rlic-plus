# pkg12 — Point-in-time release floor: design (Phase A)

Econ Evan, 2026-10-16. Branch `feat261016_pit_release`. Design, data, and an impact scan only. No pair has been rerun and no published result has changed.

## 1. Rule

A reading for reference period M may drive a return window only if it was public when that window opened. The check is made **period by period**, against the reading's actual first-release date:

> the reading stamped M is available to the window that opens at close `c` iff `first_release(M) <= date(c)`

`c` is the close of the previous rebalance row. A month-end or quarter-end stamp is rolled back to the last trading day. On a trading-day index the stamp is used as is. The calendar has date resolution, so a release on the window-open date counts as available, which is the existing Step 2 convention (open question Q3).

This replaces the fixed effective lag E\* chosen at the p90 of 2018-2026. That rule left 2-10 % of periods trading before the reading was released.

## 2. Release calendar (`data/release_calendar/`)

The calendar is built by `scripts/build_release_calendar.py`. The default run is offline from the committed ALFRED pull; `--refresh` re-pulls. It has one row per (series, reference period) from 1985 (or the series' start) to the latest release. Every row carries a `basis`, listed here in order of preference:

| basis | meaning |
|---|---|
| `alfred_first_vintage` | ALFRED `output_type=4` (initial release only). A reference period already present in the series' first vintage is not returned, so ALFRED never fabricates a pre-vintage date |
| `alfred_sibling:<SID>` | First vintage of a series in the **same press release**. Used only before the target's own vintages begin, and only if the dates agree on ≥ 90 % of the overlap. PERMIT←HOUST 99.4 %, HSN1FNSA←HSN1F 100 %, RETAILIRSA←BUSINV 100 %, ECIALLCIV←ECIWAG 100 % |
| `publisher_calendar:<rule>` | ISM bd1/bd3 of M+1, NAHB about bd11 of M, EIA WPSR the Wednesday after the last Friday (Thursday after a holiday). US federal holidays are applied. These are **rule outputs, not measurements** |
| `usgs_file_date` | S3 Last-Modified of the USGS "Cement in <month>" PDF (2021-09 → 2026-06, from the pkg9 pull) |
| `rule_next_business_day` | T10Y3M sampled at month-end: FRED posts it the next business day |
| `fallback_max_observed_lag:<n>d` | No measured date exists. The row uses period end + the series' **maximum** observed lag, shutdowns included, which is conservative |
| `no_release_recorded` | A gap inside the dated history: IR and UNRATE 2025-10 (shutdown, not in ALFRED) and cement 2023-11 (PDF returns 403). Treated as never available |

Daily data are handled by rules, not table rows. Market closes (gold/copper, VIX, SOX) use `rule:market_close`. ICE OAS uses `rule:next_business_day`. The registry key is `release_calendar_series`.

## 3. Alignment: as-of (recommended default)

The helper is `scripts/_pit_align.py`, shared by all pipelines.

```python
from _pit_align import load_release, pit_shift
rel = load_release(reg["release_calendar_series"], df.index)   # or rule_release(df.index, 0|1) for daily data
lagged = pit_shift(df[["signal", "threshold"]], lead, rel)    # replaces df[[...]].shift(lead)
pos = rule(lagged.signal, lagged.threshold)                   # then pos * ret, NO extra pos.shift(1)
```

- **Lead L becomes a minimum lag.** For row u, `pit_shift` picks the smallest `k >= L` whose reading `u-k` is public when the row's window opens. In normal periods this is the fixed-lag reading. In the residual periods (shutdown backlogs, late prints, months that were never published) it is the latest reading that was released. It is **never** a newer reading than the nominal one, and NaN if nothing is available within 24 extra periods. `asof_lags()` exposes k, so pipelines can publish the share of periods that used an older reading.
- **Every input of the rule goes through one call.** Signal, rolling threshold and any sizing input then refer to the same reading. Rolling statistics are computed on the reading-stamped series *before* the shift, as now.
- **position_shift.** `pit_shift(..., position_shift=s)` covers pipelines that keep an extra `pos.shift(1)`: availability is judged at the window the shifted position actually trades. New code should drop the extra shift and use the lead directly (E = L). Registry semantics stay as they are: `lead_floor_effective` = E\*.
- **Monthly / quarterly** (month-end / quarter-end rows, close-to-close returns): the window opens at the previous row's last trading day. **Daily** (trading-day rows): the previous row is the open, and rule releases advance by index rows. That is the pipeline's own calendar, so a session the NYSE approximation calls a holiday is not mis-rolled.
- **Rows, not months.** Lags count pipeline rows. `unrate_spy` and `nhs_saar_spy` drop the 2025-10 row, which creates a two-month return row and a one-month-longer lead across the gap. Pipelines should reindex to the complete period index (NaN rows) before shifting. The gate and the impact scan follow each pipeline's actual rows.
- **The grid floor stays.** Grids keep starting at the registry floor E\* (p90-derived). Below it, as-of would fall back in most periods and produce near-duplicates of L+1, which only enlarges the multiple-testing surface. As-of handles the residual periods; the floor keeps the search space honest.
- **Live use** follows the same rule: trade on the latest released reading.

## 4. Gate

`scripts/gate_lead_floor.py` now runs `--mode per-period` by default. For every traded grid lead and the published winner, using the detected shift, it counts backtest periods (the pipeline's own `strategy_returns` rows) in which the fixed lag uses an unreleased reading. Any breaching period FAILs. A registry entry with `alignment: pit_asof` plus a `pit_shift(` call passes by construction. `--mode floor` keeps the 2026-10-16 effective-lag check, and the structural checks run in both modes.

## 5. Alternatives rejected

1. **Raise the fixed E to the max lag.** The shutdown-driven maxima give HOUST/PERMIT E5, HSN1F E5 and cement E7 or more. That discards 3-4 months of information in 90-98 % of periods, moves every grid, and is still not safe against the next backlog.
2. **Go to cash, or drop breaching periods.** This creates a position artifact that clusters in shutdown windows (2013, 2019, 2025-26), changes n_IS / n_OOS, and is not what a live trader would do.
3. **Rebalance on release dates (daily returns from each release).** This is the most exact option, but it changes return construction and the rebalance calendar of 35 pipelines and breaks comparability with every published monthly result. Worth considering for new pairs, too large for this fix.
4. **Keep p90 with disclosure.** Rejected by the stakeholder decision (point-in-time).
5. **Real-time vintages (values as first published).** Out of scope. This package fixes **timing** only. Pipelines still use current-vintage (revised) values; that is a separate, larger lookahead (open question Q5).

## 6. Assumptions and limits

- ALFRED `realtime_start` is the **FRED posting date**, an upper bound on public availability. Some UMCSENT dates fall 1-4 days after month-end before 2008, and 2018-03 is +27 d, which looks like a posting artifact. These dates are conservative, not wrong.
- Publisher-rule series (ISM, NAHB, EIA) are not verified against archived release calendars before 2018.
- Fallback rows dominate the pre-vintage history of IR (to 2010-02), Cass (to 2013-05), AMTMNO (to 2011-04), HSN1F (to 1999-06), cement (to 2021-08), UMCSENT (to 1998-07), BUSLOANS (to 1996-11), DRCCLACBS (to 2011Q1) and DRTSCIS (to 2010Q2). The max-lag fallback is deliberately harsh. `IMPACT.md` reports a sensitivity with the max lag excluding shutdown windows.
- The cement file dates are S3 timestamps; a re-upload would overstate the lag, which is conservative.

## 7. Open questions for the Lead

- **Q1 Fallback strength.** Max observed lag, shutdowns included, is what the brief suggested. It alone makes import_price (L2/L3) and cement (L5/L6) FAIL, and it drives most of the HSN1F, RSXFS, AMTMNO, RETAILIRSA and Cass grid breaches. Alternatives: max excluding documented shutdowns (shipped as the sensitivity), or the max of the earliest 60 measured periods.
- **Q2 Grid floor.** Should the grid still start at the p90 floor E\* with as-of handling the residual periods (recommended), or at the per-period max?
- **Q3 Same-day releases.** A release on the window-open date counts as available. BUSLOANS (H.8, 4:15 pm ET) is released after the close; the calendar has no time-of-day, and the per-series release times are recorded in the meta file. Adopt "release before 16:00 ET" instead?
- **Q4 Which objective.** Use the selection objective each pair publishes (14 IS / 21 OOS) for the reruns, or move all of them to IS argmax as the brief states?
- **Q5 Vintages.** Timing is now point-in-time, but the values are still current vintage (revised). Should real-time vintage values become a Phase C?
