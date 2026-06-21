#!/usr/bin/env python3
"""Data layer for pair phlxsox_spy: PHLX Semiconductor Index (^SOX) -> SPY.

NATIVE-DAILY INTERMARKET pair. ^SOX is a continuously-quoted equity index
(no release lag, no LVCF step function). Signal of interest is whether SOX
*leads* SPY beyond contemporaneous equity co-movement, so we build SOX
returns/momentum AND SOX/SPY relative-strength (ratio + ratio momentum/zscore).

Source: Yahoo Finance ^SOX (live) and SPY. Run from repo root.
"""
from __future__ import annotations
import json
import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf

np.random.seed(42)

PAIR_ID = "phlxsox_spy"
TODAY = dt.date.today().strftime("%Y%m%d")
GEN_AT = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ---- 1. Source ----------------------------------------------------------
sox = yf.download("^SOX", start="1990-01-01", auto_adjust=True, progress=False)["Close"]
spy = yf.download("SPY", start="1990-01-01", auto_adjust=True, progress=False)["Close"]
sox = sox.squeeze().rename("sox")
spy = spy.squeeze().rename("spy")

df = pd.concat([sox, spy], axis=1).dropna()  # common overlap (both trading days)
df.index.name = "date"
df = df.sort_index()
print(f"Common overlap: {df.shape}  {df.index.min().date()} -> {df.index.max().date()}")

# ---- 2. Transforms ------------------------------------------------------
# SOX returns / momentum
df["sox_ret"] = df["sox"].pct_change()
df["spy_ret"] = df["spy"].pct_change()
for w, name in [(21, "1m"), (63, "3m"), (126, "6m"), (252, "12m")]:
    df[f"sox_mom_{name}_pct"] = (df["sox"] / df["sox"].shift(w) - 1.0) * 100.0

# SOX relative strength vs SPY
df["sox_spy_ratio"] = df["sox"] / df["spy"]
df["sox_spy_logratio"] = np.log(df["sox_spy_ratio"])
for w, name in [(21, "1m"), (63, "3m"), (126, "6m"), (252, "12m")]:
    df[f"sox_spy_ratio_mom_{name}_pct"] = (
        df["sox_spy_ratio"] / df["sox_spy_ratio"].shift(w) - 1.0
    ) * 100.0
for w, name in [(126, "126d"), (252, "252d")]:
    m = df["sox_spy_ratio"].rolling(w).mean()
    s = df["sox_spy_ratio"].rolling(w).std()
    df[f"sox_spy_ratio_zscore_{name}"] = (df["sox_spy_ratio"] - m) / s

# Realized vol of SOX (regime descriptor)
df["sox_realized_vol_21d_ann_pct"] = (
    df["sox_ret"].rolling(21).std() * np.sqrt(252) * 100.0
)

# Forward SPY returns (targets)
for w in [1, 5, 21, 63, 126, 252]:
    df[f"spy_fwd_{w}d"] = df["spy"].shift(-w) / df["spy"] - 1.0

# Native-daily market index: no publication lag -> constant 0 (documented)
df["days_since_release"] = 0

daily = df.copy()
start_d = daily.index.min().strftime("%Y%m%d")
end_d = daily.index.max().strftime("%Y%m%d")

# ---- 3. Monthly (month-end resample) ------------------------------------
m = pd.DataFrame(index=daily.resample("ME").last().index)
m["sox"] = daily["sox"].resample("ME").last()
m["spy"] = daily["spy"].resample("ME").last()
m["sox_spy_ratio"] = m["sox"] / m["spy"]
m["sox_spy_logratio"] = np.log(m["sox_spy_ratio"])
m["sox_ret_1m"] = m["sox"].pct_change()
m["spy_ret_1m"] = m["spy"].pct_change()
for w, name in [(3, "3m"), (6, "6m"), (12, "12m")]:
    m[f"sox_mom_{name}_pct"] = (m["sox"] / m["sox"].shift(w) - 1.0) * 100.0
    m[f"sox_spy_ratio_mom_{name}_pct"] = (
        m["sox_spy_ratio"] / m["sox_spy_ratio"].shift(w) - 1.0
    ) * 100.0
m["sox_spy_ratio_zscore_12m"] = (
    (m["sox_spy_ratio"] - m["sox_spy_ratio"].rolling(12).mean())
    / m["sox_spy_ratio"].rolling(12).std()
)
for w in [1, 3, 6, 12]:
    m[f"spy_fwd_{w}m"] = m["spy"].shift(-w) / m["spy"] - 1.0
m.index.name = "date"
monthly = m
start_m = monthly.index.min().strftime("%Y%m%d")
end_m = monthly.index.max().strftime("%Y%m%d")

# ---- 4. Save parquets + aliases -----------------------------------------
daily_path = f"data/{PAIR_ID}_daily_{start_d}_{end_d}.parquet"
monthly_path = f"data/{PAIR_ID}_monthly_{start_m}_{end_m}.parquet"
daily.to_parquet(daily_path)
daily.to_parquet(f"data/{PAIR_ID}_daily_latest.parquet")
monthly.to_parquet(monthly_path)
monthly.to_parquet(f"data/{PAIR_ID}_monthly_latest.parquet")
print(f"Saved daily {daily.shape} -> {daily_path}")
print(f"Saved monthly {monthly.shape} -> {monthly_path}")

# ---- 5. Stationarity tests ----------------------------------------------
from arch.unitroot import ADF, KPSS

rows = []
test_cols = [
    "sox_ret", "spy_ret",
    "sox_mom_1m_pct", "sox_mom_3m_pct", "sox_mom_6m_pct", "sox_mom_12m_pct",
    "sox_spy_ratio", "sox_spy_logratio",
    "sox_spy_ratio_mom_3m_pct", "sox_spy_ratio_mom_6m_pct",
    "sox_spy_ratio_zscore_252d",
]
# Add the raw level for contrast
level = daily["sox"].dropna()
for label, series in [("sox_level", level)] + [(c, daily[c].dropna()) for c in test_cols]:
    for tname, T in [("ADF", ADF), ("KPSS", KPSS)]:
        try:
            t = T(series)
            if tname == "ADF":
                concl = "Stationary at 5%" if t.pvalue < 0.05 else "Non-stationary"
            else:
                concl = ("Fail to reject stationarity" if t.pvalue > 0.05
                         else "Reject stationarity at 5%")
            rows.append({
                "variable": label, "test": tname,
                "statistic": round(float(t.stat), 4),
                "p_value": round(float(t.pvalue), 4),
                "lags": int(getattr(t, "lags", 0)),
                "conclusion": concl,
            })
        except Exception as e:
            rows.append({"variable": label, "test": tname, "statistic": None,
                         "p_value": None, "lags": None, "conclusion": f"error: {e}"})
stat = pd.DataFrame(rows)
import os
os.makedirs(f"results/{PAIR_ID}", exist_ok=True)
stat_path = f"results/{PAIR_ID}/stationarity_tests_{TODAY}.csv"
stat.to_csv(stat_path, index=False)
print(f"\nStationarity:\n{stat.to_string(index=False)}")

# Contemporaneous correlation diagnostic (the equity-vs-equity caveat)
corr = daily[["sox_ret", "spy_ret"]].corr().iloc[0, 1]
print(f"\nContemporaneous SOX/SPY daily-return correlation: {corr:.3f}")
with open(f"results/{PAIR_ID}/.corr_diag.txt", "w") as f:
    f.write(f"contemp_daily_ret_corr={corr:.4f}\n")
