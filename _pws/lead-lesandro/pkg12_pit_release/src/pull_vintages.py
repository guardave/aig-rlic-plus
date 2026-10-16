"""Pull ALFRED full vintage histories into data/release_calendar/vintages/<SID>.csv.gz (needs FRED_API_KEY / .env)."""
import os
import time
from pathlib import Path

import pandas as pd
import requests

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "data" / "release_calendar" / "vintages"
SERIES = ["BUSLOANS", "FRGSHPUSM649NCIS", "DRCCLACBS", "DRCCLACBN", "UMCSENT", "HOUST", "IR", "INDPRO", "M2SL", "AMTMNO",
          "NEWORDER", "HSN1FNSA", "HSN1F", "PERMIT", "RETAILIRSA", "RSXFS", "DRTSCIS", "DRTSCILM", "UNRATE"]

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO / ".env")
    except ImportError:
        pass
    key = os.environ["FRED_API_KEY"]
    for sid in SERIES:
        rows, off = [], 0
        while True:
            for k in range(5):
                r = requests.get("https://api.stlouisfed.org/fred/series/observations", timeout=300, params=dict(
                    series_id=sid, api_key=key, file_type="json", realtime_start="1776-07-04", realtime_end="9999-12-31",
                    observation_start="1980-01-01", limit=100000, offset=off))
                if r.status_code == 200:
                    break
                time.sleep(3 + 3 * k)
            obs = r.json()["observations"]
            rows += obs
            if len(obs) < 100000:
                break
            off += 100000
        d = pd.DataFrame(rows)
        d[d.value != "."].to_csv(OUT / f"{sid}.csv.gz", index=False)
        print(sid, len(d))
