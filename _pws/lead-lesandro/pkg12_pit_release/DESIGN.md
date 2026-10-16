# pkg12 — Point-in-time release floor: design (Phase A)

Econ Evan, 2026-10-16; revised 2026-10-17 for the QA findings and Lead decisions Q1-Q5. Branch `feat261016_pit_release`. Design, data, and an impact scan only. No pair has been rerun and no published result has changed.

## 1. Rule

A reading for reference period M may drive a return window only if it was public when that window opened. The check is made **period by period**, against the reading's actual first-release date:

> the reading stamped M is available to the window that opens at close `c` iff `available_date(M) <= date(c)`

`c` is the close of the previous rebalance row. A month-end or quarter-end stamp is rolled back to the last trading day. On a trading-day index the stamp is used as is.

`available_date` is the first-release date, except when the release is **after the 16:00 ET close**: then it is the next trading day (Lead decision Q3). After-close releases are:
- BUSLOANS (Fed H.8, 16:15 ET);
- any USGS file stamped at or after 16:00 ET.

Documented release times for all series are in `release_calendar_meta.json`. Where the time is unknown, the date convention applies: Cass, DRCCLACBN and DRCCLACBS use FRED posting dates, which already lag the publisher.

This replaces the fixed effective lag E\* chosen at the p90 of 2018-2026. That rule left 2-10 % of periods trading before the reading was released.

## 2. Release calendar (`data/release_calendar/`)

The calendar is built by `scripts/build_release_calendar.py`. The default run is offline from the committed ALFRED pull; `--refresh` re-pulls. It has one row per (series, reference period) from 1985 (or the series' start) to the latest release. Every row carries a `basis`, listed here in order of preference:

| basis | meaning |
|---|---|
| `alfred_first_vintage` | ALFRED `output_type=4` (initial release only). A reference period already present in the series' first vintage is not returned, so ALFRED never fabricates a pre-vintage date |
| `alfred_sibling:<SID>` | First vintage of a series in the **same press release**. Used only before the target's own vintages begin, and only if the dates agree on ≥ 90 % of the overlap. PERMIT←HOUST 99.4 %, HSN1FNSA←HSN1F 100 %, RETAILIRSA←BUSINV 100 %, ECIALLCIV←ECIWAG 100 % |
| `publisher_verified` | Actual release date from a publisher or news archive, with its source URL (`publisher_release_dates.csv`, 381 rows: ISM mfg 25, ISM services 30, NAHB 26, EIA WPSR 270, UMich final 30). It overrides the rule or ALFRED date |
| `publisher_calendar:<rule>` | Rule outputs, not measurements, with US federal holidays applied. They were tightened against the verified sample (QA LOW-9) so that no verified date falls after its rule date: ISM bd1 of M+1 (bd2 in January), ISM services bd3 (bd4 in January), NAHB bd14 of M, EIA WPSR the Wednesday after the last Friday (Thursday after a Mon-Wed holiday, Friday in the New Year week). The only verified dates later than the rule are EIA 2012-11 (Hurricane Sandy) and 2018-12 (national day of mourning), and both are overridden by their verified dates. Per-series counts are under `publisher_check` in the meta file |
| `usgs_file_date` | S3 Last-Modified of the USGS "Cement in <month>" PDF (2021-09 → 2026-06, from the pkg9 pull) |
| `rule_next_business_day` | T10Y3M sampled at month-end: FRED posts it the next business day |
| `fallback_max_lag_excl_shutdown:<n>d` | No dated history yet (before the first vintage). The date is period end + the series' max observed lag **excluding documented shutdown windows and batch-release rows** (Lead decision Q1). The shutdown-inclusive variant is in `first_release_harsh` / `available_date_harsh` (`load_release(..., harsh=True)`) as the reported sensitivity |
| `fallback_data_hole:<n>d` | A hole in our source pull, dated like a fallback row: cement 2023-11, where the S3 PDF returns 403 (QA MED-4) |
| `no_release_recorded` | Never published: IR and UNRATE 2025-10 (shutdown; FRED shows "."). Treated as never available |

Rows flagged `batch_release` in `note` are dated rows where one ALFRED date first-releases ≥ 2 periods outside the shutdown windows; examples are Cass postings and HOUST 2013-11. They are kept, as a conservative choice, but excluded from the fallback statistic.

**Calendar semantics (QA LOW-8).**
- **Non-monotone boundary.** `first_release` is not monotone in the reference period at a fallback boundary, nor at the cement 2023-11 hole. A fallback row can be dated after the first measured release of a later period: IR 2010-02 falls after 2010-03, and cement 2023-11 falls after 2023-12. This is deliberate and conservative: the helper's as-of rule picks the latest *available* reading, so an out-of-order date only makes that reading usable later.
- **DRTSCIS / DRTSCILM negative lags.** The SLOOS survey is stamped by FRED at the start of the quarter in which it is conducted. For example, the January 2025 survey is 2025Q1, released early February. Its `period_end` is therefore the end of that quarter, and the release (about −56 d) falls inside it. The pipelines stamp the reading at the same quarter end and first trade it at the window opening there. This is consistent and not a labelling bug, so `period_end` is unchanged. The negative lag only means the survey is public before its stamp.

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
- **The grid floor stays (Lead decision Q2).** Grids keep starting at the registry floor E\* (p90-derived), truncated only and never extended. Below it, as-of would fall back in most periods and produce near-duplicates of L+1, which only enlarges the multiple-testing surface. As-of handles the residual periods; the floor keeps the search space honest.
- **Live use** follows the same rule: trade on the latest released reading.

## 4. Gate

`scripts/gate_lead_floor.py` runs `--mode per-period` by default. That mode runs every check from floor mode, registry floor included, **plus**:
- **Breach count.** For every traded grid lead and the published winner, using the detected shift, it counts the backtest periods (the pipeline's own `strategy_returns` rows) in which the fixed lag uses a reading whose `available_date` is after the window opens. Any breaching period FAILs.
- **Series identity.** The registry series must be the one the pair loads: either value-matched in `data/release_calendar/pipeline_series_identity.csv`, or named in its scripts or data dictionary. A mismatch FAILs; a mislabelled sibling name WARNs.
- **Missing sample.** A missing returns CSV is a counted WARN.

**Traded lead loops are found by what they do, not by their names (QA HIGH-2).** A loop counts if it shifts by its variable, positionally or with `periods=`, and either has a lead-ish name or multiplies by a return series. Iterables given by name are resolved through the file's assignments or at the function call sites.

**`alignment: pit_asof` passes only on a real AST `pit_shift(...)` call (QA HIGH-1).** The call's lead argument must be the traded loop variable, and its result must be read afterwards; comments, strings, dead calls and constant leads do not count.

`--mode floor` keeps the 2026-10-16 effective-lag check.

## 5. Alternatives rejected

1. **Raise the fixed E to the max lag.** The shutdown-driven maxima give HOUST/PERMIT E5, HSN1F E5 and cement E7 or more. That discards 3-4 months of information in 90-98 % of periods, moves every grid, and is still not safe against the next backlog.
2. **Go to cash, or drop breaching periods.** This creates a position artifact that clusters in shutdown windows (2013, 2019, 2025-26), changes n_IS / n_OOS, and is not what a live trader would do.
3. **Rebalance on release dates (daily returns from each release).** This is the most exact option, but it changes return construction and the rebalance calendar of 35 pipelines and breaks comparability with every published monthly result. Worth considering for new pairs, too large for this fix.
4. **Keep p90 with disclosure.** Rejected by the stakeholder decision (point-in-time).
5. **Keep latest-vintage values with first-release timing.** Rejected under D8, see §8: a revised value is not known on the first-release date.

## 6. Assumptions and limits

- ALFRED `realtime_start` is the **FRED posting date**, an upper bound on public availability.
  - For UMCSENT it matched UMich's own final-release date on 28 of 29 months checked (2006-2025). The exception is 2018-03, which ALFRED shows 27 d late; it is now `publisher_verified` at 2018-03-29.
  - So the 1-4 d post-month-end finals are genuine (for example March 2016, released 2016-04-01).
- Publisher-rule series (ISM, NAHB, EIA) are checked against 25-270 verified dates each (2004-2026), with the rules made conservative as described in §2. Unverified rule rows remain rule outputs.
- Fallback rows still dominate the pre-vintage history of IR (to 2010-02), Cass (to 2013-05), HSN1F (to 1999-06), cement (to 2021-08), UMCSENT (to 1998-07), BUSLOANS (to 1996-11), DRCCLACBN (to 2011Q1) and DRTSCILM (to 2010Q2). The default is the shutdown-excluded max (Q1), and `IMPACT.md` reports the shutdown-inclusive variant for IS and OOS.
- The cement file dates are S3 timestamps; a re-upload would overstate the lag, which is conservative.

## 7. Open questions for the Lead

- **Q1 Fallback — DECIDED (Lead, 2026-10-17):** the max observed lag excluding documented shutdown windows is the default. The shutdown-inclusive variant is reported as a sensitivity. Implemented in commit d2cefe78.
- **Q2 Grid floor — DECIDED:** grids start at the p90 floor E\* (truncate only, never extend), and as-of alignment handles the residual periods.
- **Q3 After-close releases — DECIDED:** a release after the 16:00 ET close is available on the next trading day. This applies to BUSLOANS (H.8, 16:15) and to USGS files stamped at or after 16:00 ET. Implemented as `available_date`.
- **Q4 Objective — DECIDED:** Phase B reruns use IS selection (argmax IS Sharpe on the common IS start), together with the PORT_GUIDE port, so each pair is rerun once. Phase B does not start until QA has verified Phase A.
- **Q5 Vintages (D8) — DECIDED by the user:** two tracks, see §8.
Q6-Q8 are with the user. They are not acted on.
- **Q6 Pre-vintage history under track (b).** Truncate the backtest to the first ALFRED vintage, or splice first-vintage values with a flag?
- **Q7 Non-ALFRED sources** (ISM, NAHB, UMich expected business conditions, USGS cement, EIA). Archive first prints (track a), or disclose them as revised?
- **Q8 Mislabelled sources.** sloos_ci_small trades large/middle-market firms (DRTSCILM), mfg_new_orders trades core capex orders (NEWORDER), and cc_delinquency is NSA. Rename the pairs, or switch the data?

## 8. Data vintages (D8): revised values are a different signal with a different floor

**Where the values come from today.** Every macro pipeline uses **revised, near-latest-vintage** values. None uses first prints or real-time vintages. Each FRED-backed panel's raw column was matched against every ALFRED vintage (`src/vintage_id.py` → `VINTAGE_SOURCE.csv`): all 19 match exactly one vintage dated 2025-09 → 2026-10 (100% of overlapping periods). They match first prints on 0–99% of periods; the 99% (Cass) is because Cass is barely revised.

| Pair(s) | Load path (code) | Series actually loaded | Vintage of the committed panel |
|---|---|---|---|
| unrate, rsxfs, nhs_saar_rebuilt, nhs_saar, housing_starts, nhs_spy | FRED `fredgraph.csv` at run time | UNRATE, RSXFS, HSN1F, HOUST, HSN1FNSA | latest at run (unrate 2026-10-02, rsxfs 2026-10-15, nhs_saar_rebuilt 2026-09-24) |
| indpro_spy/xlp, permit_spy, umcsent_xlv, consumer_sentiment, busloans, cass, eci, m2sl, housing_starts_rebuilt, nhs_rebuilt | fredapi / FRED API (no realtime params), some spliced with Data Master | INDPRO, PERMIT, UMCSENT, BUSLOANS, FRGSHPUSM649NCIS, ECIALLCIV, M2SL, HOUST, HSN1FNSA | latest at run (busloans 2026-06-26, m2sl 2026-06-23, others 2026-08 → 2026-10) |
| import_price, permit_yoy, retail_inv_sales, mfg_new_orders, cc_delinquency, sloos_ci_small | `Data Master.xlsx` snapshot | IR, PERMIT, RETAILIRSA, **NEWORDER** (not AMTMNO), **DRCCLACBN** (NSA, not DRCCLACBS), **DRTSCILM** (large/middle-market firms, not the small-firm DRTSCIS the pair name implies) | snapshot vintage 2025-09-03 → 2026-08-25 |
| ism_mfg, ism_services, wells_fargo_housing, umcsent_spy, cement, petrol_inv | `Data Master.xlsx` (not on FRED/ALFRED) | ISM PMIs, NAHB HMI, UMich expected business conditions, USGS cement, EIA WTTSTUS1 | snapshot of unknown date; ISM and NAHB re-estimate seasonal factors every year, cement is revised in later surveys, UMich prelim → final |
| gold_copper, vix_vix3m, phlxsox | yfinance (market closes) | — | not revised |
| t10y3m, t10y3m_rebuilt, hy_ig | Data Master / fredapi daily | T10Y3M, ICE BofA OAS | Treasury yields are not revised; ICE OAS is current-only on FRED (revisions possible, not measurable) |

**The lookahead.** The value of M that the pipeline holds is the one published at the series' latest revision, often a 2025-26 benchmark or seasonal re-estimation. Using it at M's first-release date credits the strategy with information published years later.

**Two tracks** (pick one per pair; both use the same lead grid and gate):

| | (a) First-release values | (b) Real-time vintages (recommended) |
|---|---|---|
| Value of M used | First print (ALFRED `output_type=4`, or the publisher's first release) | Value of M as published at the window open, i.e. the latest revision on or before that date |
| Floor / availability | M's first-release date (the release calendar) | Presence in the vintage at the window open: a period is in vintage `t` only after its first release, and its value changes only on revision dates |
| Transforms and thresholds | Computed on the first-print series. Note that yoy of first prints mixes vintages (M's first print vs M−12's first print) | Computed **inside one vintage** (signal and rolling threshold from the series as known at `t`), which is exactly what a live trader sees |
| Helper | `pit_shift(sig, L, load_release(...))` on a first-print panel | `realtime_apply(load_vintages(sid), index, L, fn)`; `vintage_asof(vint, t)` gives "value as known at t" |
| Data | Small: one value per period | ALFRED vintage history (`data/release_calendar/vintages/`, 19 series, 644 KB). Non-FRED sources need their own archives (ISM, NAHB, UMich components, USGS, EIA) or stay on track (a) with publisher first prints |
| Coverage | Back to the first vintage. Earlier periods only have first-vintage (already revised) values | Same: rows before the first vintage cannot be real-time (IR 2010, RETAILIRSA 2013, HSN1FNSA 2011, DRCCLACBN 2011, Cass 2013, …) |

Latest-vintage values *with their correct floor*, i.e. the most recent revision date of each value, are not a usable third track: for most of history that floor is a 2025-26 revision date, so nothing before it could be traded.

**Recommendation.** Use track (b) for every FRED/ALFRED series. For pre-vintage history, either start the backtest at the first vintage or accept track (a)'s first-vintage values with a disclosed flag (open question **Q6**). Non-FRED sources (ISM, NAHB, UMich components, USGS, EIA) go to track (a) where publisher first prints can be archived. Otherwise they are disclosed as "revised values, timing-only PIT" (**Q7**). Track (b) changes signal values and rolling thresholds, so it needs full reruns. The winner rule stays as it is and D9 is not applied.
