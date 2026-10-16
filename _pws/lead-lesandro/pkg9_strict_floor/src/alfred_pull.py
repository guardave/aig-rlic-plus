"""Pull ALFRED first-vintage release dates (realtime_start of the first vintage) per reference period."""
import os, sys, time, json
import pandas as pd, requests
KEY = os.environ["FRED_API_KEY"]
OUT = sys.argv[1]
LOWFREQ = ["IR", "RSXFS", "INDPRO", "PERMIT", "HOUST", "M2SL", "FRGSHPUSM649NCIS", "BUSLOANS",
           "DRCCLACBS", "ECIALLCIV", "DRTSCIS", "UMCSENT", "UNRATE", "AMTMNO", "RETAILIRSA",
           "HSN1F", "HSN1FNSA"]
HIFREQ = ["T10Y3M", "BAMLH0A0HYM2"]
API = "https://api.stlouisfed.org/fred/series/observations"

def get(params):
    for k in range(5):
        r = requests.get(API, params=dict(params, api_key=KEY, file_type="json"), timeout=60)
        if r.status_code == 200:
            return r.json()["observations"]
        time.sleep(2 + 3 * k)
    r.raise_for_status()

rows = []
for sid in LOWFREQ:
    obs = get(dict(series_id=sid, observation_start="2017-10-01", realtime_start="1776-07-04",
                   realtime_end="9999-12-31", output_type=1))
    df = pd.DataFrame(obs)
    df = df[df.value != "."]
    first = df.groupby("date")["realtime_start"].min().reset_index()
    first["series_id"] = sid
    rows.append(first)
    print(sid, len(first), flush=True)
# high-frequency: only the reference dates the monthly pipelines sample (month-end obs / last weekly obs in month)
for sid in HIFREQ:
    cur = get(dict(series_id=sid, observation_start="2024-01-01", observation_end="2026-09-30"))
    cur = pd.DataFrame(cur); cur = cur[cur.value != "."]
    cur["d"] = pd.to_datetime(cur["date"])
    keep = cur.groupby(cur.d.dt.to_period("M"))["d"].max()   # last obs in each month (month-end sample point)
    out = []
    for d in keep.values:
        ds = pd.Timestamp(d).strftime("%Y-%m-%d")
        re_ = min(pd.Timestamp(d) + pd.Timedelta(days=30), pd.Timestamp("2026-10-15")).strftime("%Y-%m-%d")
        obs = get(dict(series_id=sid, observation_start=ds, observation_end=ds,
                       realtime_start=ds, realtime_end=re_))
        obs = [o for o in obs if o["value"] != "."]
        if obs:
            out.append({"date": ds, "realtime_start": min(o["realtime_start"] for o in obs)})
    first = pd.DataFrame(out); first["series_id"] = sid
    rows.append(first)
    print(sid, len(first), flush=True)
pd.concat(rows).rename(columns={"date": "ref_date", "realtime_start": "first_release"}).to_csv(OUT, index=False)
