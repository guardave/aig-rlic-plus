#!/usr/bin/env python3
"""Build the point-in-time release calendar: one row per (series, reference period) with the date the
reading was first public. Consumed by scripts/_pit_align.py and scripts/gate_lead_floor.py --mode per-period.

Sources, in order of preference (the `basis` column says which one each row uses):
  alfred_first_vintage        ALFRED `output_type=4` (initial release only) realtime_start of the reference period.
  alfred_sibling:<SID>        ALFRED first vintage of a series published in the SAME press release, used only for
                              periods before the target's own vintage history starts, and only when the two series'
                              dates agree on >= 90% of the overlap (agreement is stored in release_calendar_meta.json).
  publisher_calendar:<rule>   publisher schedule rule (ISM, NAHB, EIA WPSR) with US federal holidays; not measured.
  usgs_file_date              Last-Modified of the USGS "Cement in <month>" Mineral Industry Survey PDF.
  rule_next_business_day      daily market series sampled at month-end (T10Y3M): FRED posts the value the next
                              business day.
  publisher_verified          actual release date from a publisher / news archive (publisher_release_dates.csv, with
                              source URL); overrides the rule or ALFRED date and validates the rules (meta).
  fallback_max_lag_excl_shutdown:<n>d  period before any dated history: period_end + the series' max observed lag
                              EXCLUDING documented shutdown windows and batch releases (Lead decision Q1). The
                              shutdown-inclusive variant is in first_release_harsh / available_date_harsh (sensitivity).
  fallback_data_hole:<n>d     a hole in our source pull (cement 2023-11: S3 403), dated like a fallback row.
  no_release_recorded         reference period inside the dated history that was never published (IR / UNRATE 2025-10:
                              shutdown; FRED shows "."); first_release blank, treated as never available.
available_date = first_release, or the next trading day for releases after the 16:00 ET close (AFTER_CLOSE; USGS files
stamped >= 16:00 ET). This is the column the helper and the gate use.

Usage:  python scripts/build_release_calendar.py [--refresh]
  --refresh  re-pull ALFRED into data/release_calendar/alfred_initial_release.csv (needs FRED_API_KEY / .env);
             otherwise the committed pull is used, so the build is offline and deterministic.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
OUT_DIR = REPO / "data" / "release_calendar"
RAW = OUT_DIR / "alfred_initial_release.csv"
CEMENT_DATES = OUT_DIR / "usgs_cement_publication_dates.txt"
# actual release dates gathered from publisher / news archives (one row per reference period, with source URL);
# they override rule outputs and ALFRED posting dates, and validate the publisher rules
PUBLISHER_DATES = OUT_DIR / "publisher_release_dates.csv"
PUBLISHER_MAP = {"ISM_MFG": "ISM_MFG", "ISM_SERVICES": "ISM_SERVICES", "NAHB_HMI": "NAHB_HMI",
                 "EIA_WPSR": "EIA_WPSR_WTTSTUS1", "UMICH_FINAL": "UMCSENT"}
# series released after the 16:00 ET close: usable from the NEXT trading day's close (Lead decision Q3)
AFTER_CLOSE = {"BUSLOANS": "Fed H.8, 16:15 ET"}
CAL_START = pd.Timestamp("1985-01-01")
BUILD_DATE = pd.Timestamp("2026-10-16")  # releases after this date are not in the calendar

QUARTERLY = {"DRCCLACBS", "ECIALLCIV", "DRTSCIS", "ECIWAG", "DRCCLACBN", "DRTSCILM"}
FRED = ["IR", "RSXFS", "INDPRO", "PERMIT", "HOUST", "M2SL", "FRGSHPUSM649NCIS", "BUSLOANS", "DRCCLACBS",
        "ECIALLCIV", "DRTSCIS", "UMCSENT", "UNRATE", "AMTMNO", "RETAILIRSA", "HSN1F", "HSN1FNSA",
        # the series the pipelines actually load (pkg12 vintage check): Data Master 'mfg new orders' = NEWORDER
        # (advance durable-goods report), cc delinquency = DRCCLACBN (NSA), SLOOS 'C&I small' column = DRTSCILM
        "NEWORDER", "DRCCLACBN", "DRTSCILM"]
# target -> sibling released in the same press release (New Residential Construction / Sales, MTIS, ECI)
SIBLINGS = {"PERMIT": "HOUST", "HSN1FNSA": "HSN1F", "RETAILIRSA": "BUSINV", "ECIALLCIV": "ECIWAG"}
SIBLING_MIN_AGREEMENT = 0.90
# first observation of each series in FRED (current vintage); the calendar never starts before it
SERIES_START = {"IR": "1982-09", "RSXFS": "1992-01", "INDPRO": "1919-01", "PERMIT": "1960-01", "HOUST": "1959-01",
                "M2SL": "1959-01", "FRGSHPUSM649NCIS": "1990-01", "BUSLOANS": "1947-01", "DRCCLACBS": "1991-01",
                "ECIALLCIV": "2001-01", "DRTSCIS": "1990-04", "UMCSENT": "1952-11", "UNRATE": "1948-01",
                "AMTMNO": "1992-02", "RETAILIRSA": "1992-01", "NEWORDER": "1992-02", "DRCCLACBN": "1985-01",
                "DRTSCILM": "1990-04", "HSN1F": "1963-01", "HSN1FNSA": "1963-01",
                "ISM_MFG": "1948-01", "ISM_SERVICES": "1997-07", "NAHB_HMI": "1985-01",
                "EIA_WPSR_WTTSTUS1": "1985-01", "USGS_CEMENT_MIS": "1998-01", "T10Y3M_ME": "1982-01"}
# documented release time (ET); informational: the calendar is date-resolution and a reading released on the
# window-open date counts as available (standard Step 2 convention)
RELEASE_TIME_ET = {"IR": "08:30", "RSXFS": "08:30", "INDPRO": "09:15", "PERMIT": "08:00/08:30", "HOUST": "08:00/08:30",
                   "M2SL": "13:00", "FRGSHPUSM649NCIS": "unknown (FRED posting date used)", "BUSLOANS": "16:15 (H.8, after the close)",
                   "DRCCLACBS": "unknown (FRED posting date used)", "ECIALLCIV": "08:30", "DRTSCIS": "14:00",
                   "UMCSENT": "10:00", "UNRATE": "08:30", "AMTMNO": "10:00", "RETAILIRSA": "10:00", "NEWORDER": "08:30",
                   "DRCCLACBN": "unknown (FRED posting date used)", "DRTSCILM": "14:00", "HSN1F": "10:00",
                   "HSN1FNSA": "10:00", "ISM_MFG": "10:00", "ISM_SERVICES": "10:00", "NAHB_HMI": "10:00",
                   "EIA_WPSR_WTTSTUS1": "10:30", "USGS_CEMENT_MIS": "file timestamp (UTC date used)",
                   "T10Y3M_ME": "FRED next business day"}
# documented federal-shutdown / backlog windows (reference periods whose releases were delayed); used only for the
# max_lag_excl_shutdown statistic in the meta file, never to change a date
SHUTDOWN_REF = [("1995-10-01", "1996-01-31"), ("2013-08-01", "2013-10-31"), ("2018-11-01", "2019-02-28"),
                ("2025-07-01", "2026-03-31")]

BDAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())


def pull_alfred(sids) -> pd.DataFrame:
    import requests
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO / ".env")
    except ImportError:
        pass
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise SystemExit("FRED_API_KEY not set — copy .env.example to .env, or run setup.sh.")
    rows = []
    for sid in sids:
        for k in range(5):
            r = requests.get("https://api.stlouisfed.org/fred/series/observations", timeout=120, params=dict(
                series_id=sid, api_key=key, file_type="json", realtime_start="1776-07-04",
                realtime_end="9999-12-31", output_type=4))
            if r.status_code == 200:
                break
            time.sleep(2 + 3 * k)
        r.raise_for_status()
        d = pd.DataFrame(r.json()["observations"])
        d = d[d.value != "."]
        rows.append(pd.DataFrame({"series_id": sid, "ref_date": d["date"], "first_release": d["realtime_start"]}))
        print(f"  {sid}: {len(d)} initial releases from {d['date'].min()}", flush=True)
    return pd.concat(rows, ignore_index=True)


def period_end(ref: pd.Timestamp, q: bool) -> pd.Timestamp:
    return ref + (pd.offsets.QuarterEnd(0) if q else pd.offsets.MonthEnd(0))


def periods(sid: str, last: pd.Timestamp) -> pd.DatetimeIndex:
    start = max(CAL_START, pd.Timestamp(SERIES_START[sid] + "-01"))
    if sid in QUARTERLY:
        start = start.to_period("Q").start_time
        return pd.date_range(start, last, freq="QS")
    return pd.date_range(start, last, freq="MS")


def nth_bday(month_start: pd.Timestamp, n: int) -> pd.Timestamp:
    return pd.date_range(month_start, month_start + pd.offsets.MonthEnd(0), freq=BDAY)[n - 1]


def calendar_rules() -> pd.DataFrame:
    """Publisher-schedule series (not on FRED). Holiday-aware; dates are rule outputs, not measurements."""
    rows = []
    for sid, basis in (("ISM_MFG", "publisher_calendar:ISM business day 1 of M+1 (January: day 2)"),
                       ("ISM_SERVICES", "publisher_calendar:ISM business day 3 of M+1 (January: day 4)"),
                       ("NAHB_HMI", "publisher_calendar:NAHB/Wells Fargo HMI business day 14 of M (conservative bound)"),
                       ("EIA_WPSR_WTTSTUS1", "publisher_calendar:EIA WPSR, last week-ending Friday of M released the following Wednesday (Thursday after a Mon-Wed holiday; Friday in the New Year week)"),
                       ("T10Y3M_ME", "rule_next_business_day")):
        for m in periods(sid, pd.Timestamp("2026-09-01")):
            nxt = m + pd.offsets.MonthBegin(1)
            # rules tightened against the publisher_release_dates sample (pkg12 QA LOW-9) so that no verified
            # release date is later than the rule date (meta: rule_validation)
            if sid == "ISM_MFG":
                rel = nth_bday(nxt, 2 if nxt.month == 1 else 1)
            elif sid == "ISM_SERVICES":
                rel = nth_bday(nxt, 4 if nxt.month == 1 else 3)
            elif sid == "NAHB_HMI":
                rel = nth_bday(m, 14)
            elif sid == "EIA_WPSR_WTTSTUS1":
                last_fri = pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="W-FRI")[-1]
                wed = last_fri + pd.Timedelta(days=5)
                hol = USFederalHolidayCalendar().holidays(last_fri + pd.Timedelta(days=3), wed + pd.Timedelta(days=2))
                if any(h.month == 1 and h.day == 1 for h in hol):
                    rel = wed + pd.Timedelta(days=2)
                elif any(h <= wed for h in hol):
                    rel = wed + pd.Timedelta(days=1)
                else:
                    rel = wed
            else:  # month-end sample of a daily FRED series: last business day of M, posted next business day
                last_bd = pd.date_range(m, m + pd.offsets.MonthEnd(0), freq=BDAY)[-1]
                rel = last_bd + BDAY
            if rel <= BUILD_DATE:
                rows.append((sid, m, rel, basis))
    return pd.DataFrame(rows, columns=["series_id", "ref_date", "first_release", "basis"])


def cement_rows() -> pd.DataFrame:
    rows = []
    for line in CEMENT_DATES.read_text().splitlines():
        if line.strip():
            ym, lm = line.strip().split("|")
            et = pd.to_datetime(lm, utc=True).tz_convert("America/New_York")
            rows.append(("USGS_CEMENT_MIS", pd.Timestamp(ym + "-01"), pd.Timestamp(et.date()), "usgs_file_date",
                         et.hour >= 16))
    return pd.DataFrame(rows, columns=["series_id", "ref_date", "first_release", "basis", "after_close"])


def publisher_rows() -> pd.DataFrame:
    p = pd.read_csv(PUBLISHER_DATES)
    p = p[~p.note.fillna("").str.contains("AMBIGUOUS|UNVERIFIED|SCHEDULED", case=False)]
    p = p.assign(series_id=p.series.map(PUBLISHER_MAP), ref_date=pd.to_datetime(p.ref_period + "-01"),
                 first_release=pd.to_datetime(p.release_date))
    p = p[p.first_release <= BUILD_DATE].drop_duplicates(["series_id", "ref_date"], keep="first")
    return p[["series_id", "ref_date", "first_release", "source_url"]]


def in_shutdown(ref: pd.Timestamp) -> bool:
    return any(pd.Timestamp(a) <= ref <= pd.Timestamp(b) for a, b in SHUTDOWN_REF)


def build(raw: pd.DataFrame):
    from _pit_align import TRADING_DAY  # NYSE approximation (federal holidays - Columbus/Veterans + Good Friday)

    def next_trading_day(d):
        return d + TRADING_DAY

    raw = raw.assign(ref_date=pd.to_datetime(raw.ref_date), first_release=pd.to_datetime(raw.first_release))
    measured = {sid: g.set_index("ref_date")["first_release"] for sid, g in raw.groupby("series_id")}
    out, meta = [], {}
    rules_cement = pd.concat([calendar_rules(), cement_rows()], ignore_index=True)
    pub = publisher_rows()
    for sid in FRED + sorted(rules_cement.series_id.unique()):
        q = sid in QUARTERLY
        if sid in measured:
            src = pd.DataFrame({"first_release": measured[sid], "basis": "alfred_first_vintage"})
            src["after_close"] = False
        else:
            g = rules_cement[rules_cement.series_id == sid].set_index("ref_date")
            src = g[["first_release", "basis", "after_close"]].copy()
            src["after_close"] = src["after_close"].fillna(False).astype(bool)
        info = {"freq": "Q" if q else "M", "release_time_et": RELEASE_TIME_ET.get(sid),
                "after_close": AFTER_CLOSE.get(sid)}
        sib = SIBLINGS.get(sid)
        if sib and sib in measured:
            ov = src.index.intersection(measured[sib].index)
            agree = float((src.loc[ov, "first_release"] == measured[sib].loc[ov]).mean()) if len(ov) else 0.0
            info["sibling"] = {"series": sib, "overlap_periods": int(len(ov)), "same_date_share": round(agree, 4),
                               "used": agree >= SIBLING_MIN_AGREEMENT}
            if agree >= SIBLING_MIN_AGREEMENT:
                pre = measured[sib][measured[sib].index < src.index.min()]
                src = pd.concat([pd.DataFrame({"first_release": pre, "basis": f"alfred_sibling:{sib}",
                                               "after_close": False}), src])
        # publisher-verified dates: validate the rule / ALFRED date, then override it
        pv = pub[pub.series_id == sid].set_index("ref_date")
        if len(pv):
            ov = pv.index.intersection(src.index)
            diff = (src.loc[ov, "first_release"] - pv.loc[ov, "first_release"]).dt.days
            info["publisher_check"] = {"n_dates": int(len(pv)), "n_compared": int(len(ov)),
                                       "n_same": int((diff == 0).sum()),
                                       "n_calendar_earlier_than_actual": int((diff < 0).sum()),
                                       "n_calendar_later_than_actual": int((diff > 0).sum()),
                                       "max_calendar_early_d": int(-diff.min()) if len(diff) and diff.min() < 0 else 0,
                                       "max_calendar_late_d": int(diff.max()) if len(diff) and diff.max() > 0 else 0,
                                       "corrected": [str(k.date()) for k in diff.index[diff != 0]],
                                       "source_file": str(PUBLISHER_DATES.relative_to(REPO))}
            add = pd.DataFrame({"first_release": pv.first_release, "basis": "publisher_verified",
                                "after_close": False})
            src = pd.concat([src.drop(index=ov), add]).sort_index()
        last = src.index.max()
        idx = periods(sid, last)
        cal = pd.DataFrame(index=idx)
        cal.index.name = "ref_date"
        cal["period_end"] = [period_end(r, q) for r in idx]
        cal = cal.join(src)
        cal["note"] = ""
        dated = cal.basis.notna()
        first_dated = cal.index[dated].min()
        b = cal.basis.fillna("")
        lag = (cal.first_release - cal.period_end).dt.days
        # batch releases outside the documented shutdown windows (one ALFRED date first-releasing >= 2 periods:
        # FRED posting artefacts, e.g. UMCSENT 2018-03 posted with 2018-04 though UMich released it 2018-03-29, or
        # catch-up releases): kept as dated rows (conservative), flagged, excluded from the fallback statistic
        am = b == "alfred_first_vintage"
        batch = cal[am].groupby("first_release").first_release.transform("size") >= 2
        anomalies = [r for r in batch.index[batch] if not in_shutdown(r)]
        cal.loc[anomalies, "note"] = "batch_release (>=2 periods first dated on one day outside shutdown windows; excluded from the fallback lag)"
        stat_rows = [r for r in cal.index[dated] if not in_shutdown(r) and r not in anomalies]
        stat_lag = lag.loc[stat_rows]
        own = b.isin(["alfred_first_vintage", "usgs_file_date"])
        rule = b.str.startswith("publisher_calendar") | (b == "rule_next_business_day")
        lag_all = lag[dated]
        fb = int(stat_lag.max()) if len(stat_lag) else int(lag_all.max())
        fb_harsh = int(lag_all.max())
        info.update(first_dated_ref=str(first_dated.date()),
                    first_own_measured_ref=str(cal.index[own].min().date()) if own.any() else None,
                    last_ref=str(last.date()), n_measured=int(own.sum()),
                    n_sibling=int(b.str.startswith("alfred_sibling").sum()), n_rule=int(rule.sum()),
                    n_publisher_verified=int((b == "publisher_verified").sum()),
                    lag_median_d=float(lag_all.median()), lag_p90_d=float(lag_all.quantile(.9)), lag_max_d=fb_harsh,
                    fallback_lag_d=fb, fallback_lag_harsh_d=fb_harsh,
                    lag_max_first60_d=int(lag_all.iloc[:60].max()),
                    batch_release_rows=[str(r.date()) for r in anomalies])
        pre = ~dated & (cal.index < first_dated)
        gap = ~dated & (cal.index > first_dated)
        hole = gap & (sid == "USGS_CEMENT_MIS")  # S3 403: a data hole in our pull, not a non-publication
        never = gap & ~hole  # FRED "." (IR / UNRATE 2025-10: not published)
        cal["first_release_harsh"] = cal["first_release"]
        for m_, tag in ((pre, "fallback_max_lag_excl_shutdown"), (hole, "fallback_data_hole")):
            cal.loc[m_, "first_release"] = cal.loc[m_, "period_end"] + pd.Timedelta(days=fb)
            cal.loc[m_, "first_release_harsh"] = cal.loc[m_, "period_end"] + pd.Timedelta(days=fb_harsh)
            cal.loc[m_, "basis"] = f"{tag}:{fb}d"
            cal.loc[m_, "after_close"] = False
        cal.loc[never, "basis"] = "no_release_recorded"
        info["n_fallback"] = int(pre.sum())
        info["data_holes"] = [str(x.date()) for x in cal.index[hole]]
        info["no_release_recorded"] = [str(x.date()) for x in cal.index[never]]
        ac = cal["after_close"].fillna(False).astype(bool) | (sid in AFTER_CLOSE)
        info["n_after_close_rows"] = int((ac & cal.first_release.notna()).sum())
        for col, src_col in (("available_date", "first_release"), ("available_date_harsh", "first_release_harsh")):
            cal[col] = cal[src_col]
            sel = ac & cal[src_col].notna()
            cal.loc[sel, col] = [next_trading_day(d) for d in cal.loc[sel, src_col]]
        cal["lag_days"] = (cal.first_release - cal.period_end).dt.days
        cal["series_id"] = sid
        out.append(cal.reset_index())
        meta[sid] = info
    cal = pd.concat(out, ignore_index=True)
    cal = cal[["series_id", "ref_date", "period_end", "first_release", "available_date", "lag_days", "basis",
               "first_release_harsh", "available_date_harsh", "note"]]
    for c in ("ref_date", "period_end", "first_release", "available_date", "first_release_harsh", "available_date_harsh"):
        cal[c] = pd.to_datetime(cal[c]).dt.strftime("%Y-%m-%d")
    cal["lag_days"] = cal["lag_days"].astype("Int64")
    return cal, meta


def main(argv):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if "--refresh" in argv or not RAW.exists():
        sids = FRED + sorted({s for s in SIBLINGS.values() if s not in FRED})
        pull_alfred(sids).to_csv(RAW, index=False)
    cal, meta = build(pd.read_csv(RAW))
    cal.to_csv(OUT_DIR / "release_calendar.csv", index=False)
    (OUT_DIR / "release_calendar_meta.json").write_text(json.dumps(
        {"built_through": str(BUILD_DATE.date()), "calendar_start": str(CAL_START.date()),
         "convention": "first_release = date the reading is first public; available_date = first_release, or the next "
                       "trading day when the release is after the 16:00 ET close (AFTER_CLOSE series, USGS files stamped "
                       ">= 16:00 ET). A reading is usable for a window opening at the close of day d iff available_date <= d. "
                       "Fallback rows use the max observed lag excluding documented shutdown windows and batch-posting "
                       "artefacts (default); *_harsh columns use the shutdown-inclusive max (sensitivity).",
         "after_close": AFTER_CLOSE, "shutdown_reference_windows": SHUTDOWN_REF,
         "daily_rules": {"BAMLH0A0HYM2": "value dated t posted by FRED on the next business day",
                         "T10Y3M": "value dated t posted by FRED on the next business day",
                         "market_close": "gold/copper, VIX/VIX3M, SOX/SPY observed at the close of t: usable from t's close for the t -> t+1 return"},
         "series": meta}, indent=2))
    for sid, m in meta.items():
        print(f"{sid:18s} {m['freq']} measured {m['n_measured']:4d} (from {m['first_own_measured_ref']}) sibling {m['n_sibling']:3d} "
              f"rule {m['n_rule']:3d} verified {m['n_publisher_verified']:3d} fallback {m['n_fallback']:3d} at {m['fallback_lag_d']}d "
              f"(harsh {m['fallback_lag_harsh_d']}d)  holes {m['data_holes']} no_release {m['no_release_recorded']} "
              f"batch {m['batch_release_rows']}" + (f" check {m['publisher_check']['n_compared']}/{m['publisher_check']['n_calendar_earlier_than_actual']} early" if 'publisher_check' in m else "")
              + (f"  sibling {m['sibling']['series']} agree {m['sibling']['same_date_share']}" if 'sibling' in m else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
