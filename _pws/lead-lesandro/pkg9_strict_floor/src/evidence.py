import pandas as pd, numpy as np, sys
fr = pd.read_csv("alfred_first_release.csv", parse_dates=["ref_date", "first_release"])
Q = {"DRCCLACBS", "ECIALLCIV", "DRTSCIS"}
# --- non-FRED documented calendars -> synthetic release dates 2018-01..2026-09 ---
months = pd.date_range("2018-01-01", "2026-09-01", freq="MS")
def bday(d, n):  # n-th business day of the month starting at d (ignores holidays -> lower bound)
    return pd.bdate_range(d, d + pd.offsets.MonthEnd(0))[n - 1]
syn = []
for m in months:
    nxt = m + pd.offsets.MonthBegin(1)
    syn.append(("ISM_MFG", m, bday(nxt, 1)))
    syn.append(("ISM_SERVICES", m, bday(nxt, 3)))
    # NAHB/Wells Fargo HMI: released ~mid-month of the survey month itself (calendar: ~11th business day)
    syn.append(("NAHB_HMI", m, bday(m, 11)))
    # EIA WPSR: monthly mean of weekly stocks; last week-ending Friday in M released the following Wednesday (+5 d)
    fridays = pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="W-FRI")
    syn.append(("EIA_WPSR_WTTSTUS1", m, fridays[-1] + pd.Timedelta(days=5)))
cem = [l.strip().split("|") for l in open("usgs_cement_publication_dates.txt")]
for ym, lm in cem:
    syn.append(("USGS_CEMENT_MIS", pd.Timestamp(ym + "-01"), pd.Timestamp(pd.to_datetime(lm).date())))
syn = pd.DataFrame(syn, columns=["series_id", "ref_date", "first_release"])
allr = pd.concat([fr, syn], ignore_index=True)
allr = allr[(allr.ref_date >= "2018-01-01")]
rows = []
for sid, g in allr.groupby("series_id"):
    g = g.sort_values("ref_date").copy()
    daily = sid in ("T10Y3M", "BAMLH0A0HYM2")
    if sid in Q:
        pend = g.ref_date + pd.offsets.QuarterEnd(0); step = pd.offsets.QuarterEnd(1)
    elif daily:
        pend = g.ref_date; step = None
    else:
        pend = g.ref_date + pd.offsets.MonthEnd(0); step = pd.offsets.MonthEnd(1)
    g["period_end"] = pend
    g["lag_days"] = (g.first_release - g.period_end).dt.days
    for E in (1, 2, 3, 4, 5):
        if daily:
            continue
        ws = g.period_end.map(lambda x: x + step * (E - 1))  # window opens at period-end of M+E-1
        g[f"gap_E{E}"] = (g.first_release - ws).dt.days
    rows.append(g)
ev = pd.concat(rows, ignore_index=True)
ev.to_csv("release_gaps_by_period.csv", index=False)
summ = []
for sid, g in ev.groupby("series_id"):
    rec = dict(series_id=sid, n=len(g), lag_min=g.lag_days.min(), lag_med=g.lag_days.median(),
               lag_p90=g.lag_days.quantile(.9), lag_max=g.lag_days.max())
    for E in (1, 2, 3, 4, 5):
        c = f"gap_E{E}"
        if c in g and g[c].notna().any():
            rec[f"E{E}_gap_med"] = g[c].median(); rec[f"E{E}_gap_p90"] = g[c].quantile(.9)
            rec[f"E{E}_pct_lookahead"] = round(100 * (g[c] > 0).mean(), 1)
    fl = next((E for E in (1, 2, 3, 4, 5) if f"E{E}_gap_p90" in rec and rec[f"E{E}_gap_p90"] <= 0), None)
    rec["strict_floor_E"] = fl
    last3 = g.sort_values("ref_date").tail(3)
    rec["last3"] = "; ".join(f"{r.ref_date.date()}->{r.first_release.date()}" for r in last3.itertuples())
    summ.append(rec)
S = pd.DataFrame(summ)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(S[["series_id","n","lag_min","lag_med","lag_p90","lag_max","E1_gap_med","E1_gap_p90","E1_pct_lookahead","E2_gap_p90","E2_pct_lookahead","E3_gap_p90","E3_pct_lookahead","E4_gap_p90","E4_pct_lookahead","strict_floor_E"]].to_string(index=False))
S.to_csv("series_summary.csv", index=False)
