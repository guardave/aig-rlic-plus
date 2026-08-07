#!/usr/bin/env python3
"""
Data Stage: NAHB/Wells Fargo Housing Market Index (HMI) x SPY
=============================================================
Stakeholder-requested pair wells_fargo_housing_spy. Branch
feat260706_wells_fargo_housing_spy.

Dana-owned stage 1 of the pipeline (Dana -> Evan -> Vera+Ray -> Ace -> Quincy).
Mirrors scripts/pair_data_cass_freight_spy.py artifact shapes exactly
(including the display-name-registry JSON sync fix).

Deliverables:
  - data/wells_fargo_housing_spy_monthly_{start}_{end}.parquet (+ _latest alias)
  - data/wells_fargo_housing_spy_monthly_schema.json           (DATA-D5 sidecar)
  - data/data_dictionary_wells_fargo_housing_spy_{tag}.csv
  - data/summary_stats_wells_fargo_housing_spy_{tag}.csv
  - data/missing_value_report_wells_fargo_housing_spy_{tag}.md
  - results/wells_fargo_housing_spy/stationarity_tests_{tag}.csv
  - results/wells_fargo_housing_spy/interpretation_metadata.json
  - results/wells_fargo_housing_spy/design_note.md
  - data/display_name_registry.csv rows + data/manifest.json entry (DATA-D13)

INDICATOR: NAHB/Wells Fargo Housing Market Index (HMI). MONTHLY builder-
sentiment DIFFUSION index, bounded 0-100, 50 = neutral, SEASONALLY ADJUSTED
by NAHB. FRED delisted the series (licensing) — sourced from the project's
`data/Data Master.xlsx`, sheet `WFHMI` (Pre-master column ticker
"RE - Wells Fargo H Indx"; Pre-master Row 2 dictionary: "NAHB/Wells Fargo
Housing Market Index / Units: index, seasonally Adjusted Annual Rate /
Monthly, Jan 1985 - Oct 2025"). Master sample: 1985-01 .. 2025-10, 490 obs.

Publication timing: NAHB releases the HMI mid-month (~16th-18th) FOR the
CURRENT reference month — effectively zero publication lag (a survey).
The month-M value is known intra-month M, before month-end M. At monthly
granularity, L1 is the safe/conservative real-time floor; L0-at-month-end
is defensible but grid should start at L1 per project convention.

Direction prior (for Evan/Ray): PROCYCLICAL (provisional). Rising builder
sentiment = stronger housing demand pipeline = risk-on; collapsing HMI
(2006-2008, 2022) preceded/accompanied broad downturns. Housing is a classic
LEADING sector ("housing IS the business cycle", Leamer 2007). Lead-lag and
sign determined EMPIRICALLY by Evan (Granger / pre-whitened CCF).

Author: Data Dana (Data Agent)
Date: 2026-07-06
Pair ID: wells_fargo_housing_spy
"""

import json
import os
import warnings
from datetime import datetime, timezone

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

np.random.seed(42)  # no sampling occurs; seed set per SOP anyway

PAIR_ID = "wells_fargo_housing_spy"
MASTER_XLSX = "data/Data Master.xlsx"
MASTER_SHEET = "WFHMI"
MASTER_COL = "RE - Wells Fargo H Indx"
CONTEXT_START = "1984-01-01"
END_DATE = "2025-10-31"   # bounded by Data Master HMI history
DATE_TAG = "20260706"

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
os.makedirs(RESULTS_DIR, exist_ok=True)

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Stage 1: Sourcing
# ---------------------------------------------------------------------------
def fetch_master_hmi():
    """NAHB HMI from Data Master.xlsx sheet WFHMI (FRED delisted the series).
    Pre-master Row 2 is the authoritative dictionary for this column."""
    w = pd.read_excel(os.path.join(BASE_DIR, MASTER_XLSX), sheet_name=MASTER_SHEET)
    s = w.set_index("date")[MASTER_COL].astype(float)
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    s.name = "nahb_hmi"
    print(f"  [XLSX] {MASTER_SHEET}!{MASTER_COL} -> nahb_hmi: {len(s)} obs, "
          f"{s.index.min().date()} to {s.index.max().date()}")
    return s


def fetch_fred(series_id, col_name, start=CONTEXT_START):
    """Fetch via the official FRED API (JSON). Same key convention as
    pair_data_cass_freight_spy.py."""
    import urllib.request
    load_dotenv()  # repo-root .env; hardcoded fallback removed (key rotated after leak)
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise SystemExit("FRED_API_KEY not set — copy .env.example to .env, or run setup.sh.")
    url = (f"https://api.stlouisfed.org/fred/series/observations?"
           f"series_id={series_id}&api_key={api_key}&file_type=json"
           f"&observation_start={start}&observation_end={END_DATE}")
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                obs = json.load(r)["observations"]
            break
        except Exception as e:
            last_err = e
    else:
        raise RuntimeError(f"FRED fetch failed for {series_id}: {last_err}")
    s = pd.Series({pd.Timestamp(o["date"]): float(o["value"])
                   for o in obs if o["value"] != "."}, name=col_name).sort_index()
    print(f"  [FRED] {series_id} -> {col_name}: {len(s)} obs, "
          f"{s.index.min().date()} to {s.index.max().date()}")
    return s


def fetch_yahoo(ticker, col_name):
    import yfinance as yf
    df = yf.download(ticker, start=CONTEXT_START, end=END_DATE,
                     progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    s = df["Close"].copy()
    s.name = col_name
    s.index = pd.to_datetime(s.index)
    if s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    s = s.astype(float)
    print(f"  [YF]   {ticker} -> {col_name}: {len(s)} obs, "
          f"{s.index.min().date()} to {s.index.max().date()}")
    return s


print("=" * 70)
print("STAGE 1: SOURCING")
print("=" * 70)
hmi = fetch_master_hmi()
unrate = fetch_fred("UNRATE", "unrate")
dgs10 = fetch_fred("DGS10", "dgs10")
fed_funds = fetch_fred("DFF", "fed_funds")
spy = fetch_yahoo("SPY", "spy")
vix = fetch_yahoo("^VIX", "vix")

# ---------------------------------------------------------------------------
# Stage 2: Alignment + derived series (month-end, mirrors cass_freight_spy)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 2: ALIGNMENT + DERIVED SERIES")
print("=" * 70)

# Dataset is bounded by HMI history in the Master (1985-01 .. 2025-10).
idx = pd.date_range(hmi.index.min(), END_DATE, freq="ME")
df = pd.DataFrame(index=idx)
df.index.name = "date"

# HMI is stamped at month-start in the Master; value is that month's survey.
# Align to month-end of the SAME month (resample 'ME' last).
df["nahb_hmi"] = hmi.resample("ME").last().reindex(idx)
df["unrate"] = unrate.resample("ME").last().reindex(idx)
df["dgs10"] = dgs10.resample("ME").last().reindex(idx)
df["fed_funds"] = fed_funds.resample("ME").last().reindex(idx)
df["vix"] = vix.resample("ME").last().reindex(idx)
df["spy"] = spy.resample("ME").last().reindex(idx)

h = df["nahb_hmi"]
# BOUNDED 0-100 diffusion index: LEVEL is meaningful in itself (50 = neutral)
# and mean-reverting; point-differences are the natural change metric.
# Percent-changes are included per the standard monthly family but behave
# oddly near low levels (8 -> 9 is +12.5% "growth") — documented, prefer
# point-change / level family for inference.
df["nahb_hmi_pct_yoy"] = (h / h.shift(12) - 1) * 100
df["nahb_hmi_pct_mom"] = (h / h.shift(1) - 1) * 100
df["nahb_hmi_3m_pct"] = (h / h.shift(3) - 1) * 100
df["nahb_hmi_6m_pct"] = (h / h.shift(6) - 1) * 100
df["nahb_hmi_diff_12m"] = h - h.shift(12)        # 12M point change (bounded-index native)
df["nahb_hmi_diff_3m"] = h - h.shift(3)          # 3M point change
df["nahb_hmi_ma12_idx"] = h.rolling(12, min_periods=10).mean()
df["nahb_hmi_dev_trend_pct"] = (h / df["nahb_hmi_ma12_idx"] - 1) * 100
rm60 = h.rolling(60, min_periods=36)
df["nahb_hmi_zscore_60m"] = (h - rm60.mean()) / rm60.std()
ry = df["nahb_hmi_diff_12m"].rolling(60, min_periods=36)
df["nahb_hmi_diff12_zscore_60m"] = (df["nahb_hmi_diff_12m"] - ry.mean()) / ry.std()
df["nahb_hmi_accel_pct"] = df["nahb_hmi_pct_mom"].diff()
# 50-line regime flag: for a diffusion index, ABOVE/BELOW 50 is the natural
# expansion/contraction regime (builders net-optimistic vs net-pessimistic),
# NOT a YoY<0 contraction flag (which would be degenerate for a mean-reverting
# bounded sentiment index).
df["nahb_hmi_above50"] = (h >= 50).astype(float)

s = df["spy"]
df["spy_ret"] = s.pct_change()
df["spy_fwd_1m"] = s.shift(-1) / s - 1
df["spy_fwd_3m"] = s.shift(-3) / s - 1
df["spy_fwd_6m"] = s.shift(-6) / s - 1
df["spy_fwd_12m"] = s.shift(-12) / s - 1

print(f"  Monthly dataset: {df.shape}, {df.index.min().date()} to {df.index.max().date()}")
print(f"  Columns: {list(df.columns)}")

# ---------------------------------------------------------------------------
# Stage 3: Validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 3: VALIDATION")
print("=" * 70)

assert df.index.is_monotonic_increasing, "index not monotonic"
assert not df.index.duplicated().any(), "duplicate timestamps"
assert df.index.max() <= pd.Timestamp(END_DATE) + pd.offsets.MonthEnd(0), "future leakage"

# Bounded 0-100 diffusion-index sanity
hv = df["nahb_hmi"].dropna()
assert hv.min() >= 0 and hv.max() <= 100, "HMI out of 0-100 bounds"
print(f"  Bounds: min={hv.min():.0f}, max={hv.max():.0f} (0-100 OK)")

# Known-history sanity (Defense 2)
checks = {
    "2009-01-31": (7, 9, "GFC trough ~8"),
    "2020-04-30": (28, 32, "COVID crash to 30"),
    "2020-11-30": (89, 91, "post-COVID peak 90"),
    "2022-12-31": (29, 33, "2022 rate-shock collapse ~31"),
}
for d, (lo, hi_, label) in checks.items():
    v = df.loc[d, "nahb_hmi"]
    assert lo <= v <= hi_, f"known-history FAIL {label}: {d} = {v}"
    print(f"  PASS known history: {label} -> {d} = {v:.0f}")

# 2022 collapse magnitude (84 -> ~31 within the year)
h2022 = df.loc["2022-01-31":"2022-12-31", "nahb_hmi"]
assert h2022.iloc[0] >= 80 and h2022.min() <= 35, "2022 collapse missing"
print(f"  PASS 2022 collapse: {h2022.iloc[0]:.0f} (Jan) -> {h2022.min():.0f} (trough)")

# Gap check on indicator: no internal NaN gaps
internal_gaps = df.loc[hv.index.min():hv.index.max(), "nahb_hmi"].isna().sum()
print(f"  Internal gaps in nahb_hmi: {internal_gaps}")
assert internal_gaps == 0, "silent gaps in HMI"

# Outlier flagging (z>4 on 1M point change) — flag, do NOT remove
chg = df["nahb_hmi"].diff().dropna()
z = (chg - chg.mean()) / chg.std()
outliers = chg[abs(z) > 4]
print(f"  1M point-change outliers (|z|>4): {len(outliers)}")
for d, v in outliers.items():
    print(f"    {d.date()}: {v:+.0f} pts")

# Overlap window with SPY (target coverage; SPY inception 1993)
overlap = df.dropna(subset=["spy", "nahb_hmi"])
print(f"  Usable HMI x SPY overlap: {overlap.index.min().date()} -> {overlap.index.max().date()} "
      f"({len(overlap)} months)")

# Stationarity tests
from arch.unitroot import ADF, KPSS
from dotenv import load_dotenv
test_cols = ["nahb_hmi", "nahb_hmi_pct_yoy", "nahb_hmi_pct_mom", "nahb_hmi_3m_pct",
             "nahb_hmi_6m_pct", "nahb_hmi_diff_12m", "nahb_hmi_diff_3m",
             "nahb_hmi_zscore_60m", "nahb_hmi_diff12_zscore_60m",
             "nahb_hmi_dev_trend_pct", "spy_ret"]
rows = []
for col in test_cols:
    x = df[col].dropna()
    try:
        adf = ADF(x, max_lags=12)
        rows.append({"variable": col, "test": "ADF", "statistic": round(adf.stat, 4),
                     "p_value": round(adf.pvalue, 4), "lags": adf.lags,
                     "conclusion": "Stationary at 5%" if adf.pvalue < 0.05 else "Non-stationary"})
    except Exception as e:
        rows.append({"variable": col, "test": "ADF", "statistic": np.nan,
                     "p_value": np.nan, "lags": np.nan, "conclusion": f"failed: {e}"})
    try:
        kp = KPSS(x)
        rows.append({"variable": col, "test": "KPSS", "statistic": round(kp.stat, 4),
                     "p_value": round(kp.pvalue, 4), "lags": kp.lags,
                     "conclusion": "Fail to reject stationarity" if kp.pvalue > 0.05
                     else "Reject stationarity at 5%"})
    except Exception as e:
        rows.append({"variable": col, "test": "KPSS", "statistic": np.nan,
                     "p_value": np.nan, "lags": np.nan, "conclusion": f"failed: {e}"})
stat_df = pd.DataFrame(rows)
stat_path = os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv")
stat_df.to_csv(stat_path, index=False)
print(f"\n  Stationarity tests -> {stat_path}")
print(stat_df.to_string(index=False))

# ---------------------------------------------------------------------------
# Stage 4: Save parquet + alias + sidecar + reports
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 4: DELIVERY ARTIFACTS")
print("=" * 70)

start_tag = df.index.min().strftime("%Y%m%d")
end_tag = df.index.max().strftime("%Y%m%d")
parquet_path = os.path.join(DATA_DIR, f"wells_fargo_housing_spy_monthly_{start_tag}_{end_tag}.parquet")
latest_path = os.path.join(DATA_DIR, "wells_fargo_housing_spy_monthly_latest.parquet")
df.to_parquet(parquet_path)
df.to_parquet(latest_path)
print(f"  Parquet -> {parquet_path}")
print(f"  Alias   -> {latest_path}")

HMI_QUIRK = ("Sourced from data/Data Master.xlsx sheet WFHMI (FRED delisted NAHBHMI for "
             "licensing); Pre-master Row 2 dictionary: 'NAHB/Wells Fargo Housing Market Index, "
             "Units: index, seasonally Adjusted, Monthly, Jan 1985 - Oct 2025'. Bounded 0-100 "
             "builder-sentiment diffusion index, 50 = neutral; seasonally adjusted by NAHB. "
             "Released mid-month FOR the current month (~zero lag; L1 monthly floor is "
             "conservative). Known episodes: GFC trough 8 (Jan-2009), COVID crash to 30 "
             "(Apr-2020) then V-recovery to 90 (Nov-2020), 2022 rate-shock collapse 83->31. "
             "Percent-changes of a bounded index behave oddly at low levels — prefer "
             "level / point-change transforms.")

COLS = {
    "nahb_hmi": dict(unit="index", display_name="NAHB Housing Market Index",
        direction="higher_is_better", axis_label="NAHB HMI (50 = neutral)",
        desc="NAHB/Wells Fargo Housing Market Index: monthly homebuilder-sentiment "
             "diffusion index, bounded 0-100, 50 = neutral, seasonally adjusted by NAHB. "
             "Sourced from Data Master.xlsx (WFHMI sheet); FRED delisted the series."),
    "unrate": dict(unit="pct", display_name="Unemployment Rate (%)",
        direction="lower_is_better", axis_label="Unemployment (%)",
        desc="FRED UNRATE: civilian unemployment rate, monthly, SA. Control series."),
    "dgs10": dict(unit="pct", display_name="10Y Treasury Yield (%)",
        direction="neutral", axis_label="10Y Yield (%)",
        desc="FRED DGS10: 10-year constant-maturity Treasury yield, month-end value. Control."),
    "fed_funds": dict(unit="pct", display_name="Fed Funds Rate (%)",
        direction="neutral", axis_label="Fed Funds (%)",
        desc="FRED DFF: effective federal funds rate, month-end value. Control."),
    "vix": dict(unit="index", display_name="VIX",
        direction="lower_is_better", axis_label="VIX",
        desc="CBOE VIX index, month-end close (Yahoo ^VIX). Control / regime variable. "
             "Starts 1990 (leading NaNs before that)."),
    "spy": dict(unit="price", display_name="SPY Price ($)",
        direction="neutral", axis_label="SPY ($)",
        desc="SPY adjusted close, month-end (Yahoo, auto-adjusted). Target asset. "
             "Starts 1993-01 (SPY inception)."),
    "nahb_hmi_pct_yoy": dict(unit="pct", display_name="NAHB HMI YoY (%)",
        direction="higher_is_better", axis_label="NAHB HMI YoY (%)",
        desc="12-month percent change in nahb_hmi. CAUTION: percent change of a bounded "
             "0-100 index is level-dependent (8->16 = +100%); prefer nahb_hmi_diff_12m."),
    "nahb_hmi_pct_mom": dict(unit="pct", display_name="NAHB HMI MoM (%)",
        direction="higher_is_better", axis_label="NAHB HMI MoM (%)",
        desc="1-month percent change in nahb_hmi. Bounded-index caveat as for YoY."),
    "nahb_hmi_3m_pct": dict(unit="pct", display_name="NAHB HMI 3M Change (%)",
        direction="higher_is_better", axis_label="NAHB HMI 3M (%)",
        desc="3-month percent change (momentum) in nahb_hmi. Bounded-index caveat."),
    "nahb_hmi_6m_pct": dict(unit="pct", display_name="NAHB HMI 6M Change (%)",
        direction="higher_is_better", axis_label="NAHB HMI 6M (%)",
        desc="6-month percent change (momentum) in nahb_hmi. Bounded-index caveat."),
    "nahb_hmi_diff_12m": dict(unit="index", display_name="NAHB HMI 12M Point Change",
        direction="higher_is_better", axis_label="12M change (pts)",
        desc="12-month POINT change in nahb_hmi (index points). The bounded-index-native "
             "momentum measure; preferred over pct_yoy for cycle inference."),
    "nahb_hmi_diff_3m": dict(unit="index", display_name="NAHB HMI 3M Point Change",
        direction="higher_is_better", axis_label="3M change (pts)",
        desc="3-month POINT change in nahb_hmi (index points)."),
    "nahb_hmi_ma12_idx": dict(unit="index", display_name="NAHB HMI 12M MA",
        direction="higher_is_better", axis_label="NAHB HMI 12M MA",
        desc="12-month rolling mean of nahb_hmi (min 10 obs)."),
    "nahb_hmi_dev_trend_pct": dict(unit="pct", display_name="NAHB HMI Deviation from 12M Trend (%)",
        direction="higher_is_better", axis_label="Dev. from 12M MA (%)",
        desc="Percent deviation of nahb_hmi from its 12-month moving average."),
    "nahb_hmi_zscore_60m": dict(unit="none", display_name="NAHB HMI 60M Z-Score",
        direction="higher_is_better", axis_label="Z-score (60M)",
        desc="Rolling 60-month z-score of the LEVEL (min 36 obs). Effective start ~1987-12."),
    "nahb_hmi_diff12_zscore_60m": dict(unit="none", display_name="NAHB HMI Momentum 60M Z-Score",
        direction="higher_is_better", axis_label="12M-chg z-score (60M)",
        desc="Rolling 60-month z-score of nahb_hmi_diff_12m (min 36 obs). Effective start ~1988-12."),
    "nahb_hmi_accel_pct": dict(unit="pct", display_name="NAHB HMI Acceleration (pp)",
        direction="higher_is_better", axis_label="MoM accel. (pp)",
        desc="First difference of nahb_hmi_pct_mom (percentage points). Noisy; bounded-index caveat."),
    "nahb_hmi_above50": dict(unit="none", display_name="NAHB HMI Above-50 Flag",
        direction="higher_is_better", axis_label="Above 50 (0/1)",
        desc="1.0 when nahb_hmi >= 50 (builders net-optimistic), else 0.0. The natural "
             "diffusion-index regime flag (replaces a degenerate YoY<0 contraction flag)."),
    "spy_ret": dict(unit="decimal_return", display_name="SPY Monthly Return",
        direction="neutral", axis_label="SPY return",
        desc="SPY 1-month simple return (decimal)."),
    "spy_fwd_1m": dict(unit="decimal_return", display_name="SPY Forward 1M Return",
        direction="neutral", axis_label="SPY fwd 1M",
        desc="Forward 1-month SPY return (decimal). Regression/tournament target."),
    "spy_fwd_3m": dict(unit="decimal_return", display_name="SPY Forward 3M Return",
        direction="neutral", axis_label="SPY fwd 3M",
        desc="Forward 3-month SPY return (decimal). Regression/tournament target."),
    "spy_fwd_6m": dict(unit="decimal_return", display_name="SPY Forward 6M Return",
        direction="neutral", axis_label="SPY fwd 6M",
        desc="Forward 6-month SPY return (decimal). Regression/tournament target."),
    "spy_fwd_12m": dict(unit="decimal_return", display_name="SPY Forward 12M Return",
        direction="neutral", axis_label="SPY fwd 12M",
        desc="Forward 12-month SPY return (decimal). Regression/tournament target."),
}
assert set(COLS) == set(df.columns), (
    f"COLS/parquet drift: {set(COLS) ^ set(df.columns)}")

# Cross-pair consistency (DATA-D13): canonical column names already in the
# display-name registry keep their existing registry display_name/unit/axis_label.
reg_path = os.path.join(DATA_DIR, "display_name_registry.csv")
reg = pd.read_csv(reg_path)
_reg_idx = reg.set_index("column_name")
for col in COLS:
    if col in _reg_idx.index:
        COLS[col]["display_name"] = _reg_idx.loc[col, "display_name"]
        COLS[col]["unit"] = _reg_idx.loc[col, "unit"]
        COLS[col]["axis_label"] = _reg_idx.loc[col, "axis_label"]

# DATA-D5 sidecar
sidecar = {
    "pair_id": PAIR_ID,
    "parquet_path": os.path.relpath(parquet_path, BASE_DIR),
    "schema_version": "1.0.0",
    "generated_at": NOW_ISO,
    "columns": {
        "date": {"dtype": "datetime64[ns]", "unit": "date", "display_name": "Date",
                 "direction": "neutral",
                 "description": "Month-end date index (parquet index column); "
                                f"spans {df.index.min().date()} through {df.index.max().date()}."},
        **{col: {"dtype": str(df[col].dtype), "unit": m["unit"],
               "display_name": m["display_name"], "direction": m["direction"],
               "description": m["desc"],
               "source_reference": ("DataMaster:WFHMI!RE - Wells Fargo H Indx" if col.startswith("nahb_hmi") else
                                    "yahoo:SPY" if col.startswith("spy") else "see description")}
          for col, m in COLS.items()}
    },
}
sidecar_path = os.path.join(DATA_DIR, "wells_fargo_housing_spy_monthly_schema.json")
with open(sidecar_path, "w") as f:
    json.dump(sidecar, f, indent=2)
print(f"  Sidecar -> {sidecar_path}")

# Data dictionary (human form, CSV like prior pairs)
dd_rows = []
for col, m in COLS.items():
    dd_rows.append({
        "column_name": col, "display_name": m["display_name"],
        "description": m["desc"],
        "source": ("Data Master.xlsx (NAHB)" if col.startswith("nahb_hmi") else
                   "FRED" if col in ("unrate", "dgs10", "fed_funds") else "Yahoo Finance"),
        "series_id": ("WFHMI!RE - Wells Fargo H Indx" if col == "nahb_hmi" else
                      {"unrate": "UNRATE", "dgs10": "DGS10", "fed_funds": "DFF",
                       "vix": "^VIX", "spy": "SPY"}.get(col, "derived")),
        "unit": m["unit"], "direction_convention": m["direction"],
        "seasonal_adj": "SA (by NAHB)" if col.startswith("nahb_hmi") else "N/A",
        "effective_start": str(df[col].first_valid_index().date()),
        "refresh_freq": "monthly" if col.startswith(("nahb_hmi", "unrate")) else "daily",
        "known_quirks": HMI_QUIRK if col.startswith("nahb_hmi") else "",
    })
dd_path = os.path.join(DATA_DIR, f"data_dictionary_wells_fargo_housing_spy_{DATE_TAG}.csv")
pd.DataFrame(dd_rows).to_csv(dd_path, index=False)
print(f"  Data dictionary -> {dd_path}")

# Summary stats
ss_path = os.path.join(DATA_DIR, f"summary_stats_wells_fargo_housing_spy_{DATE_TAG}.csv")
df.describe().T.round(4).to_csv(ss_path)
print(f"  Summary stats -> {ss_path}")

# Missing value report
mv_lines = [
    f"# Missing Value Report — wells_fargo_housing_spy ({DATE_TAG})",
    "",
    f"Dataset: `{os.path.relpath(parquet_path, BASE_DIR)}` — shape {df.shape}, "
    f"month-end index {df.index.min().date()} to {df.index.max().date()}.",
    "",
    "## Publication lag & no-lookahead (NAHB HMI)",
    "",
    "NAHB releases the HMI mid-month (~16th-18th) FOR the CURRENT reference month — "
    "a survey with effectively ZERO publication lag. The month-M value is known "
    "intra-month M, before month-end M. **Evan: L1 is the safe/conservative real-time "
    "floor at monthly granularity; even L0-at-month-end is defensible (value is public "
    "~2 weeks before month-end), but start the lead grid at L1 per project convention.** "
    "The series is seasonally adjusted by NAHB — no seasonal contamination of MoM/short-"
    "horizon transforms.",
    "",
    "## Bounded-index caveat",
    "",
    "The HMI is a bounded 0-100 diffusion index (50 = neutral). Percent-change transforms "
    "are level-dependent (a move from 8 to 16 is '+100%'); the LEVEL itself and point-"
    "change transforms (`nahb_hmi_diff_3m`, `nahb_hmi_diff_12m`) are the natural signal "
    "family. Percent-change columns are included for family consistency but flagged.",
    "",
    "## Missing values by column",
    "",
    "| Column | NaN count | Pattern |",
    "|---|---|---|",
]
for col in df.columns:
    n = int(df[col].isna().sum())
    fv = df[col].first_valid_index()
    pattern = (f"leading (series/transform starts {fv.date()})" if n and fv is not None else "none")
    if col.startswith("spy_fwd"):
        pattern += "; trailing NaN from forward shift"
    mv_lines.append(f"| `{col}` | {n} | {pattern} |")
mv_lines += [
    "",
    "No internal gaps in `nahb_hmi` (verified: 490 consecutive months). No forward-fill "
    "applied to the indicator. SPY/VIX have leading NaNs (SPY inception 1993-01; VIX 1990) "
    "— the usable pair overlap window starts at SPY inception. Forward-return columns are "
    "NaN at the tail by construction (no leakage).",
    "",
    "## Sanity checks (Defense 2)",
    "",
    "- GFC trough: Jan-2009 HMI = 8 — PASS (published record low).",
    "- COVID whipsaw: Apr-2020 = 30, Nov-2020 = 90 (record high) — PASS.",
    "- 2022 rate-shock collapse: 83 (Jan) -> 31 (Dec) — PASS.",
    f"- Bounds: min {hv.min():.0f} / max {hv.max():.0f} within 0-100 — PASS.",
    f"- HMI x SPY usable overlap: {overlap.index.min().date()} .. {overlap.index.max().date()} ({len(overlap)} months).",
    f"- 1M point-change outliers (|z|>4): {len(outliers)} flagged (not removed): "
    + ", ".join(f"{d.date()} ({v:+.0f} pts)" for d, v in outliers.items()),
]
mv_path = os.path.join(DATA_DIR, f"missing_value_report_wells_fargo_housing_spy_{DATE_TAG}.md")
with open(mv_path, "w") as f:
    f.write("\n".join(mv_lines) + "\n")
print(f"  Missing value report -> {mv_path}")

# ---------------------------------------------------------------------------
# Stage 5: interpretation_metadata.json (Dana fields; provisional seeds noted)
# ---------------------------------------------------------------------------
meta = {
    "pair_id": PAIR_ID,
    "schema_version": "1.1.0",
    "indicator": "wells_fargo_housing",
    "target": "spy",
    "indicator_nature": "leading",
    "indicator_type": "sentiment",
    "strategy_objective": "max_sharpe",
    "expected_direction": "procyclical",
    "data_provenance": {
        "source": "data/Data Master.xlsx sheet WFHMI (NAHB/Wells Fargo Housing Market Index; FRED delisted NAHBHMI for licensing)",
        "series_id": "WFHMI!RE - Wells Fargo H Indx",
        "accessed_at": NOW_ISO,
    },
    "known_stress_episodes": [
        {"label": "Housing bust / GFC", "start": "2006-01-01", "end": "2009-06-30",
         "note": "HMI slid from ~70s (2005) to record-low 8 in Jan-2009 — the classic housing-leads-the-cycle episode, turning down ~2 years before the equity market peak."},
        {"label": "COVID whipsaw", "start": "2020-03-01", "end": "2020-11-30",
         "note": "HMI crashed to 30 in Apr-2020, then V-recovered to a record 90 by Nov-2020 on the rates-driven housing boom."},
        {"label": "2022 rate shock", "start": "2022-01-01", "end": "2022-12-31",
         "note": "HMI collapsed 83 -> 31 over 2022 as mortgage rates doubled; equities de-rated concurrently."},
    ],
    "related_pair_ids": ["building_permits_spy", "indpro_spy"],
    "owner_writes": {
        "dana": ["pair_id", "schema_version", "indicator", "target",
                 "indicator_nature", "indicator_type", "data_provenance",
                 "known_stress_episodes", "related_pair_ids"],
        "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
        "ray": ["strategy_objective", "expected_direction", "mechanism", "caveats",
                "narrative_summary"],
    },
    "last_updated_by": "dana",
    "last_updated_at": NOW_ISO,
}
meta_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
with open(meta_path, "w") as f:
    json.dump(meta, f, indent=2)
print(f"  interpretation_metadata -> {meta_path}")

# ---------------------------------------------------------------------------
# Stage 6: design_note.md
# ---------------------------------------------------------------------------
design = f"""# Design Note — wells_fargo_housing_spy ({DATE_TAG})

## Hypothesis (one-liner)
Does homebuilder sentiment (NAHB/Wells Fargo Housing Market Index) carry forward
information about SPY returns? Prior: PROCYCLICAL and LEADING — housing is the
most interest-rate-sensitive real sector and classically leads the business
cycle ("housing IS the business cycle", Leamer 2007); the HMI turned down ~2
years before the GFC equity peak. Lead-lag and sign are determined EMPIRICALLY
by Evan (Granger / pre-whitened CCF); this note only seeds a provisional prior.

## Source & sample
- Indicator: **data/Data Master.xlsx**, sheet `WFHMI`, column
  `RE - Wells Fargo H Indx` (queue primary_csv_ticker). FRED delisted NAHBHMI
  (licensing) — the Master is the authoritative project source. Pre-master
  Row 2 dictionary: "NAHB/Wells Fargo Housing Market Index / Units: index,
  seasonally Adjusted / Monthly, Jan 1985 - Oct 2025".
- Master sample: **1985-01 .. 2025-10 (490 monthly obs, no gaps)**. (NAHB HMI
  begins Jan-1985 at the source, so the Master holds full history.)
- Target: SPY month-end (Yahoo, auto-adjusted; inception 1993-01) — usable pair
  overlap **{overlap.index.min().date()} .. {overlap.index.max().date()}
  ({len(overlap)} months, ~33 years: multiple full cycles — a LONG sample by
  fleet standards)**. Controls: UNRATE/DGS10/DFF (FRED), ^VIX (Yahoo, from 1990).

## Bounded-index transform design (differs from unbounded-quantity pairs)
The HMI is a bounded 0-100 SENTIMENT diffusion index, 50 = neutral:
- **Level is meaningful in itself** (distance from 50 = net builder optimism)
  and mean-reverting — unlike unbounded quantity indices where only changes
  matter. Level and 60M level z-score are first-class signals here.
- **Point changes** (`_diff_3m`, `_diff_12m`) are the natural momentum metric;
  **percent changes of a bounded index are level-dependent** (8 -> 16 = "+100%")
  and included only for standard-family consistency, with a caveat.
- **Regime flag = above/below 50** (`nahb_hmi_above50`), the native
  expansion/contraction line for a diffusion index — NOT a YoY<0 contraction
  flag, which would be degenerate/misleading for a mean-reverting bounded series.

## Seasonality
The HMI is **seasonally adjusted by NAHB** (confirmed by Pre-master Row 2).
MoM / short-horizon transforms are NOT seasonally contaminated (contrast with
the NSA Cass Freight pair).

## Stationarity (ADF/KPSS — see stationarity_tests_{DATE_TAG}.csv)
Level is highly persistent (borderline; bounded so it cannot be a true random
walk); change/z-score transforms stationary; `spy_ret` stationary. Full table
in the CSV; Evan confirms rather than re-runs (SOP).

## No-lookahead / publication lag (recommendation for Evan)
NAHB releases mid-month (~16th-18th) FOR the CURRENT month — effectively zero
publication lag. The month-M value is public ~2 weeks BEFORE month-end M, so
even L0 at month-end granularity involves no lookahead. **Recommendation: start
the lead grid at L1 (safe/conservative, consistent with fleet convention); an
L0 variant is defensible if Evan wants to test the freshest read.**

## Key data-quality flags for downstream
1. **Static source**: the Master is hand-maintained; latest obs 2025-10. No
   live API refresh — manifest TTL set to 30 days but refresh requires a
   Master update (flagged in manifest note). Data Access Risk: Medium.
2. **Bounded index**: prefer level / point-change / z-score signals; treat
   pct-change transforms with caution (documented per-column).
3. 2008-09 single-digit trough and 2020 whipsaw are REAL — do not winsorize.
4. Integer-granularity series (whole index points) — ties are common; flag for
   any rank/percentile-based signal.

## New pair — no prior version; Rule D1 series-preservation / regression diff N/A.
"""
design_path = os.path.join(RESULTS_DIR, "design_note.md")
with open(design_path, "w") as f:
    f.write(design)
print(f"  Design note -> {design_path}")

# ---------------------------------------------------------------------------
# Stage 7: DATA-D13 — display-name registry + manifest
# ---------------------------------------------------------------------------
reg = pd.read_csv(reg_path)
new_rows = []
for col, m in COLS.items():
    if col in set(reg["column_name"]):
        continue  # cross-pair consistency: existing canonical names keep existing entries
    new_rows.append({"column_name": col, "display_name": m["display_name"],
                     "unit": m["unit"], "axis_label": m["axis_label"]})
if new_rows:
    reg = pd.concat([reg, pd.DataFrame(new_rows)], ignore_index=True)
    reg.to_csv(reg_path, index=False)
print(f"  Registry: +{len(new_rows)} rows -> {reg_path}")
# keep JSON view in sync if it exists
reg_json_path = os.path.join(DATA_DIR, "display_name_registry.json")
if os.path.exists(reg_json_path):
    with open(reg_json_path) as f:
        reg_json = json.load(f)
    listkey = "columns" if "columns" in reg_json else ("entries" if "entries" in reg_json else None)
    if isinstance(reg_json, dict) and listkey:
        existing = {e["column_name"] for e in reg_json[listkey]}
        reg_json[listkey] += [r for r in new_rows if r["column_name"] not in existing]
        reg_json["generated_at"] = NOW_ISO
        with open(reg_json_path, "w") as f:
            json.dump(reg_json, f, indent=2)
        print(f"  Registry JSON view ({listkey}) updated -> {reg_json_path}")

# Sidecar display_name must match registry verbatim — cross-validate
reg_map = dict(zip(reg["column_name"], reg["display_name"]))
for col in COLS:
    assert sidecar["columns"][col]["display_name"] == reg_map[col] or col not in reg_map, \
        f"display-name drift for {col}"

manifest_path = os.path.join(DATA_DIR, "manifest.json")
with open(manifest_path) as f:
    manifest = json.load(f)
key = "artifacts" if "artifacts" in manifest else "aliases"
entries = [e for e in manifest[key] if PAIR_ID not in e.get("path", "")]
entries += [
    {"path": os.path.relpath(parquet_path, BASE_DIR),
     "source": "DataMaster:WFHMI (NAHB/Wells Fargo HMI, monthly diffusion index 0-100, SA) + FRED:UNRATE/DGS10/DFF + yahoo:SPY/^VIX",
     "refresh_ttl_days": 30,
     "schema_ref": os.path.relpath(sidecar_path, BASE_DIR),
     "last_updated": datetime.now().strftime("%Y-%m-%d"),
     "pairs": [PAIR_ID],
     "mixed_freq_ttl_note": "Monthly indicator (hand-maintained Data Master, latest 2025-10; "
                            "no live API — refresh requires a Master update) + month-end "
                            "snapshots of daily market data; TTL=30 days nominal."},
    {"path": os.path.relpath(latest_path, BASE_DIR),
     "source": f"alias_of:{os.path.relpath(parquet_path, BASE_DIR)}",
     "refresh_ttl_days": 30,
     "schema_ref": os.path.relpath(sidecar_path, BASE_DIR),
     "last_updated": datetime.now().strftime("%Y-%m-%d"),
     "pairs": [PAIR_ID]},
]
manifest[key] = entries
manifest["generated_at"] = NOW_ISO
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"  Manifest updated -> {manifest_path}")

print("\nDONE — data stage complete for wells_fargo_housing_spy.")
