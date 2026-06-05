#!/usr/bin/env python3
"""permit_spy master parquet refresh — FRED via fredapi, SPY via mqr_datalayer.

Replicates stages 1-2 of scripts/pair_pipeline_permit_spy.py with one
substitution: SPY (and VIX where possible) come from mqr_datalayer, not
yfinance. Yahoo's IP rate limit on this host is sticky; the project's
canonical data layer is the documented fallback per .claude/CLAUDE.md.

Output: data/permit_spy_monthly_<DATE>.parquet
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Resolve repo root from this file's location so the helper survives
# `git clone` to any host. Avoids the hardcoded /workspaces or
# /projects/... paths that the canonical pipeline script carries.
REPO_ROOT = str(Path(__file__).resolve().parents[1])
DATA_DIR = os.path.join(REPO_ROOT, "data")
START_DATE = "1990-01-01"
END_DATE = "2025-12-31"
PAIR_ID = "permit_spy"
DATE_TAG = "20260605"

os.makedirs(DATA_DIR, exist_ok=True)


def fetch_fred_series() -> dict[str, pd.Series]:
    from fredapi import Fred
    api_key = os.environ.get("FRED_API_KEY", "952aa4d0c4b2057609fbf3ecc6954e58")
    fred = Fred(api_key=api_key)
    out = {}
    for sid, name in [("PERMIT", "permit"), ("UNRATE", "unrate"), ("HOUST", "houst"),
                      ("DGS10", "dgs10"), ("DTB3", "dtb3"), ("DFF", "fed_funds")]:
        s = fred.get_series(sid, observation_start=START_DATE, observation_end=END_DATE)
        out[name] = s.astype(float)
        v = s.dropna()
        print(f"  [FRED]   {sid:10s} -> {name:10s}: {len(v):5d} obs, "
              f"{v.index.min().date()} to {v.index.max().date()}")
    return out


def fetch_via_mqr_datalayer(ticker: str, name: str) -> pd.Series:
    """Pull daily AdjustedPrice via mqr_datalayer for a US-listed ticker."""
    from mqr_datalayer import data_request as dr
    dates = pd.date_range(START_DATE, END_DATE, freq="B")
    df = pd.DataFrame({"date": dates, "id": f"{ticker} US"})
    res = dr.data_request(df, dr.Id.BloombergCode, dr.Pricing.AdjustedPrice,
                          data_header=name)
    s = res.set_index("date")[name].dropna().astype(float)
    s.index = pd.DatetimeIndex(s.index)
    print(f"  [MQR]    {ticker:10s} -> {name:10s}: {len(s):5d} obs, "
          f"{s.index.min().date()} to {s.index.max().date()}")
    return s


def stage_data() -> dict[str, pd.Series]:
    print("[1/2] FETCH")
    series = fetch_fred_series()
    # SPY: documented dependency for the trade log
    series["spy"] = fetch_via_mqr_datalayer("SPY", "spy")
    # VIX: try mqr_datalayer; tolerate failure (VIX is a control variable for
    # econometric tests only — not load-bearing for the trade-log fix).
    try:
        series["vix"] = fetch_via_mqr_datalayer("VIX", "vix")
    except Exception as e:
        print(f"  [MQR]    VIX skipped: {type(e).__name__}: {e}")
    return series


def stage_derived(series: dict[str, pd.Series]) -> pd.DataFrame:
    print("\n[2/2] ALIGN + DERIVE")
    monthly_idx = pd.date_range(START_DATE, END_DATE, freq="ME")
    df = pd.DataFrame(index=monthly_idx)
    df.index.name = "date"

    monthly_cols = {"permit", "unrate", "houst"}
    daily_cols = {"spy", "vix", "dgs10", "dtb3", "fed_funds"}

    for col in monthly_cols:
        if col in series:
            df[col] = series[col].resample("ME").last().reindex(monthly_idx)
    for col in daily_cols:
        if col in series:
            df[col] = series[col].resample("ME").last().reindex(monthly_idx)
    df = df.ffill(limit=2)

    p = df["permit"]
    df["permit_yoy"] = (p / p.shift(12) - 1) * 100
    df["permit_mom"] = (p / p.shift(1) - 1) * 100
    df["permit_ma12"] = p.rolling(12, min_periods=10).mean()
    df["permit_dev_trend"] = p - df["permit_ma12"]
    rm60 = p.rolling(60, min_periods=48)
    df["permit_zscore_60m"] = (p - rm60.mean()) / rm60.std()
    df["permit_mom_3m"] = p - p.shift(3)
    df["permit_mom_6m"] = p - p.shift(6)
    df["permit_accel"] = df["permit_mom"] - df["permit_mom"].shift(1)
    df["permit_contraction"] = (df["permit_yoy"] < 0).astype(int)

    if "dgs10" in df.columns and "dtb3" in df.columns:
        df["yield_spread_10y3m"] = df["dgs10"] - df["dtb3"]

    if "spy" in df.columns:
        df["spy_ret"] = df["spy"].pct_change()
        spy = df["spy"]
        df["spy_fwd_1m"] = spy.shift(-1) / spy - 1
        df["spy_fwd_3m"] = spy.shift(-3) / spy - 1
        df["spy_fwd_6m"] = spy.shift(-6) / spy - 1
        df["spy_fwd_12m"] = spy.shift(-12) / spy - 1

    df = df.dropna(subset=["permit"])
    print(f"\n  Monthly aligned: shape={df.shape}, "
          f"{df.index.min().date()} to {df.index.max().date()}")
    return df


def main() -> None:
    print(f"=== permit_spy data refresh ({DATE_TAG}) — mqr_datalayer SPY ===\n")
    series = stage_data()
    df = stage_derived(series)

    out = os.path.join(DATA_DIR, f"{PAIR_ID}_monthly_{DATE_TAG}.parquet")
    df.to_parquet(out, engine="pyarrow")
    print(f"\n  WROTE -> {out}")
    print(f"  ({len(df.columns)} cols, {len(df)} rows)")

    if "spy" in df.columns:
        spy_first = df["spy"].first_valid_index()
        nan_pre = df.loc[:spy_first, "spy"].isna().sum() - 1 if spy_first else len(df)
        print(f"\n  CHECK   spy first_valid_index : {spy_first}  "
              f"(NaN months before: {nan_pre})")
    if "spy_ret" in df.columns:
        sr = df["spy_ret"].first_valid_index()
        print(f"  CHECK   spy_ret first_valid_index : {sr}")


if __name__ == "__main__":
    main()
