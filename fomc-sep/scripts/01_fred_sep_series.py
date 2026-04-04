#!/usr/bin/env python3
"""
Phase 1: Extract all FOMC SEP series from FRED API.
=========================================================
Pulls all 63 SEP-related series from FRED release #326.
Outputs structured Parquet files for each variable group.
"""

import os
import pandas as pd
from fredapi import Fred

API_KEY = os.environ.get("FRED_API_KEY", "952aa4d0c4b2057609fbf3ecc6954e58")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fred")
os.makedirs(OUT_DIR, exist_ok=True)

# All known SEP FRED series organized by variable and statistic
SEP_SERIES = {
    "gdp_growth": {
        "median": "GDPC1MD",
        "ct_mid": "GDPC1CTM", "ct_low": "GDPC1CTL", "ct_high": "GDPC1CTH",
        "range_low": "GDPC1RL", "range_mid": "GDPC1RM", "range_high": "GDPC1RH",
        # Longer run
        "median_lr": "GDPC1MDLR",
        "ct_mid_lr": "GDPC1CTMLR", "ct_high_lr": "GDPC1CTHLR",
        "range_low_lr": "GDPC1RLLR", "range_mid_lr": "GDPC1RMLR",
    },
    "unemployment": {
        "median": "UNRATEMD",
        "ct_mid": "UNRATECTM", "ct_low": "UNRATECTL", "ct_high": "UNRATECTH",
        "range_low": "UNRATERL", "range_mid": "UNRATERM", "range_high": "UNRATERH",
        # Longer run
        "median_lr": "UNRATEMDLR",
        "ct_mid_lr": "UNRATECTMLR", "ct_low_lr": "UNRATECTLLR",
    },
    "pce_inflation": {
        "median": "PCECTPIMD",
        "ct_mid": "PCECTPICTM", "ct_low": "PCECTPICTL", "ct_high": "PCECTPICTH",
        "range_low": "PCECTPIRL", "range_mid": "PCECTPIRM", "range_high": "PCECTPIRH",
    },
    "core_pce": {
        "median": "JCXFEMD",
        "ct_mid": "JCXFECTM", "ct_high": "JCXFECTH",
        "range_mid": "JCXFERM", "range_high": "JCXFERH",
    },
    "fed_funds": {
        "median": "FEDTARMD",
        "ct_mid": "FEDTARCTM", "ct_low": "FEDTARCTL", "ct_high": "FEDTARCTH",
        "range_low": "FEDTARRL", "range_mid": "FEDTARRM", "range_high": "FEDTARRH",
        # Longer run
        "median_lr": "FEDTARMDLR",
        "ct_mid_lr": "FEDTARCTMLR", "ct_low_lr": "FEDTARCTLLR", "ct_high_lr": "FEDTARCTHLR",
        "range_low_lr": "FEDTARRLLR", "range_mid_lr": "FEDTARRMLR", "range_high_lr": "FEDTARRHLR",
    },
}


def main():
    fred = Fred(api_key=API_KEY)

    total_series = 0
    total_obs = 0

    for var_name, series_dict in SEP_SERIES.items():
        print(f"\n=== {var_name} ({len(series_dict)} series) ===")
        frames = {}

        for stat_name, fred_id in series_dict.items():
            try:
                s = fred.get_series(fred_id, observation_start="2007-01-01")
                s = s.dropna()
                if len(s) > 0:
                    frames[stat_name] = s
                    total_series += 1
                    total_obs += len(s)
                    print(f"  {fred_id:20s} ({stat_name:12s}): {len(s):3d} obs, "
                          f"{s.index.min().date()} to {s.index.max().date()}")
                else:
                    print(f"  {fred_id:20s} ({stat_name:12s}): empty")
            except Exception as e:
                print(f"  {fred_id:20s} ({stat_name:12s}): FAILED ({str(e)[:50]})")

        if frames:
            df = pd.DataFrame(frames)
            df.index.name = "date"
            path = os.path.join(OUT_DIR, f"sep_{var_name}.parquet")
            df.to_parquet(path, engine="pyarrow")
            print(f"  -> Saved {path} ({df.shape})")

    # Also save a combined long-format dataset
    all_rows = []
    for var_name, series_dict in SEP_SERIES.items():
        for stat_name, fred_id in series_dict.items():
            try:
                s = fred.get_series(fred_id, observation_start="2007-01-01").dropna()
                for date, value in s.items():
                    all_rows.append({
                        "date": date,
                        "variable": var_name,
                        "statistic": stat_name,
                        "fred_id": fred_id,
                        "value": float(value),
                    })
            except Exception:
                pass

    if all_rows:
        combined = pd.DataFrame(all_rows)
        combined_path = os.path.join(OUT_DIR, "sep_all_fred.parquet")
        combined.to_parquet(combined_path, engine="pyarrow", index=False)
        print(f"\n=== Combined: {len(combined)} rows -> {combined_path} ===")

    print(f"\nTotal: {total_series} series, {total_obs} observations")


if __name__ == "__main__":
    main()
