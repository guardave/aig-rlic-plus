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
  fallback_max_observed_lag   period before any measured history: period_end + the series' MAX observed lag
                              (conservative; includes shutdown backlogs). Never a measured date.
  no_release_recorded         reference period inside the dated history with no release in the source (IR / UNRATE
                              2025-10: shutdown, not in ALFRED; cement 2023-11: no USGS file date in the pkg9 pull);
                              first_release is blank and the period is treated as never available.

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
OUT_DIR = REPO / "data" / "release_calendar"
RAW = OUT_DIR / "alfred_initial_release.csv"
CEMENT_DATES = OUT_DIR / "usgs_cement_publication_dates.txt"
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
    for sid, basis in (("ISM_MFG", "publisher_calendar:ISM business day 1 of M+1"),
                       ("ISM_SERVICES", "publisher_calendar:ISM business day 3 of M+1"),
                       ("NAHB_HMI", "publisher_calendar:NAHB/Wells Fargo HMI ~business day 11 of M"),
                       ("EIA_WPSR_WTTSTUS1", "publisher_calendar:EIA WPSR, last week-ending Friday of M released the following Wednesday (Thursday after a Mon-Wed holiday)"),
                       ("T10Y3M_ME", "rule_next_business_day")):
        for m in periods(sid, pd.Timestamp("2026-09-01")):
            nxt = m + pd.offsets.MonthBegin(1)
            if sid == "ISM_MFG":
                rel = nth_bday(nxt, 1)
            elif sid == "ISM_SERVICES":
                rel = nth_bday(nxt, 3)
            elif sid == "NAHB_HMI":
                rel = nth_bday(m, 11)
            elif sid == "EIA_WPSR_WTTSTUS1":
                last_fri = pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="W-FRI")[-1]
                wed = last_fri + pd.Timedelta(days=5)
                hol = USFederalHolidayCalendar().holidays(last_fri + pd.Timedelta(days=3), wed)
                rel = wed + pd.Timedelta(days=1) if len(hol) else wed
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
            rows.append(("USGS_CEMENT_MIS", pd.Timestamp(ym + "-01"),
                         pd.Timestamp(pd.to_datetime(lm, utc=True).date()), "usgs_file_date"))
    return pd.DataFrame(rows, columns=["series_id", "ref_date", "first_release", "basis"])


def in_shutdown(ref: pd.Timestamp) -> bool:
    return any(pd.Timestamp(a) <= ref <= pd.Timestamp(b) for a, b in SHUTDOWN_REF)


def build(raw: pd.DataFrame):
    raw = raw.assign(ref_date=pd.to_datetime(raw.ref_date), first_release=pd.to_datetime(raw.first_release))
    measured = {sid: g.set_index("ref_date")["first_release"] for sid, g in raw.groupby("series_id")}
    out, meta = [], {}
    other = pd.concat([calendar_rules(), cement_rows()], ignore_index=True)
    for sid in FRED + sorted(other.series_id.unique()):
        q = sid in QUARTERLY
        if sid in measured:
            own = measured[sid]
            src = pd.DataFrame({"first_release": own, "basis": "alfred_first_vintage"})
        else:
            g = other[other.series_id == sid].set_index("ref_date")
            src = g[["first_release", "basis"]]
        info = {"freq": "Q" if q else "M", "release_time_et": RELEASE_TIME_ET.get(sid)}
        sib = SIBLINGS.get(sid)
        if sib and sib in measured:
            ov = src.index.intersection(measured[sib].index)
            agree = float((src.loc[ov, "first_release"] == measured[sib].loc[ov]).mean()) if len(ov) else 0.0
            info["sibling"] = {"series": sib, "overlap_periods": int(len(ov)), "same_date_share": round(agree, 4),
                               "used": agree >= SIBLING_MIN_AGREEMENT}
            if agree >= SIBLING_MIN_AGREEMENT:
                pre = measured[sib][measured[sib].index < src.index.min()]
                src = pd.concat([pd.DataFrame({"first_release": pre, "basis": f"alfred_sibling:{sib}"}), src])
        last = src.index.max()
        idx = periods(sid, last)
        cal = pd.DataFrame(index=idx)
        cal.index.name = "ref_date"
        cal["period_end"] = [period_end(r, q) for r in idx]
        cal = cal.join(src)
        lag = (cal.first_release - cal.period_end).dt.days
        meas = cal.basis.notna()
        first_meas = cal.index[meas].min()
        b = cal.basis.fillna("")
        own = b.isin(["alfred_first_vintage", "usgs_file_date"])
        rule = b.str.startswith("publisher_calendar") | (b == "rule_next_business_day")
        own_lag = lag[meas]  # own + sibling measured lags: the fallback max is taken over both
        excl = own_lag[[not in_shutdown(r) for r in own_lag.index]]
        max_lag = int(own_lag.max())
        info.update(first_dated_ref=str(first_meas.date()),
                    first_own_measured_ref=str(cal.index[own].min().date()) if own.any() else None,
                    last_ref=str(last.date()), n_measured=int(own.sum()), n_sibling=int(b.str.startswith("alfred_sibling").sum()),
                    n_rule=int(rule.sum()),
                    lag_median_d=float(own_lag.median()), lag_p90_d=float(own_lag.quantile(.9)), lag_max_d=max_lag,
                    lag_max_excl_shutdown_d=int(excl.max()) if len(excl) else None,
                    lag_max_first60_d=int(own_lag.iloc[:60].max()))
        pre = ~meas & (cal.index < first_meas)
        gap = ~meas & (cal.index > first_meas)
        cal.loc[pre, "first_release"] = cal.loc[pre, "period_end"] + pd.Timedelta(days=max_lag)
        cal.loc[pre, "basis"] = f"fallback_max_observed_lag:{max_lag}d"
        cal.loc[gap, "basis"] = "no_release_recorded"
        info["n_fallback"] = int(pre.sum())
        info["no_release_recorded"] = [str(x.date()) for x in cal.index[gap]]
        cal["lag_days"] = (cal.first_release - cal.period_end).dt.days
        cal["series_id"] = sid
        out.append(cal.reset_index())
        meta[sid] = info
    cal = pd.concat(out, ignore_index=True)
    cal = cal[["series_id", "ref_date", "period_end", "first_release", "lag_days", "basis"]]
    for c in ("ref_date", "period_end", "first_release"):
        cal[c] = cal[c].dt.strftime("%Y-%m-%d")
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
         "convention": "first_release is the date the reading is first public; a reading released on the window-open "
                       "date counts as available (date resolution, standard Step 2)",
         "daily_rules": {"BAMLH0A0HYM2": "value dated t posted by FRED on the next business day",
                         "T10Y3M": "value dated t posted by FRED on the next business day",
                         "market_close": "gold/copper, VIX/VIX3M, SOX/SPY observed at the close of t: usable from t's close for the t -> t+1 return"},
         "series": meta}, indent=2))
    for sid, m in meta.items():
        print(f"{sid:18s} {m['freq']} measured {m['n_measured']:4d} (from {m['first_own_measured_ref']}) sibling {m['n_sibling']:3d} "
              f"rule {m['n_rule']:3d} fallback {m['n_fallback']:3d}  lag med/p90/max {m['lag_median_d']:.0f}/{m['lag_p90_d']:.0f}/{m['lag_max_d']}"
              f"  no_release {m['no_release_recorded']}"
              + (f"  sibling {m['sibling']['series']} agree {m['sibling']['same_date_share']}" if 'sibling' in m else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
