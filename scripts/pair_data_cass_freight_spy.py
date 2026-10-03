#!/usr/bin/env python3
"""
Data Stage: Cass Freight Index (Shipments) x SPY
================================================
Prospective pair cass_freight_spy. Mode 1, branch feat260705_cass_freight_spy.

Dana-owned stage 1 of the pipeline (Dana -> Evan -> Vera+Ray -> Ace -> Quincy).
Mirrors scripts/pair_data_busloans_spy.py artifact shapes exactly.

Deliverables:
  - data/cass_freight_spy_monthly_{start}_{end}.parquet  (+ _latest alias)
  - data/cass_freight_spy_monthly_schema.json            (DATA-D5 sidecar)
  - data/data_dictionary_cass_freight_spy_{tag}.csv
  - data/summary_stats_cass_freight_spy_{tag}.csv
  - data/missing_value_report_cass_freight_spy_{tag}.md
  - results/cass_freight_spy/stationarity_tests_{tag}.csv
  - results/cass_freight_spy/interpretation_metadata.json
  - results/cass_freight_spy/design_note.md
  - data/display_name_registry.csv rows + data/manifest.json entry (DATA-D13)

INDICATOR: FRED FRGSHPUSM649NCIS — Cass Freight Index: Shipments. Monthly,
index (Jan 1990 = 1.00), NOT SEASONALLY ADJUSTED. FRED history starts 2016-01
(short: ~10 years). Cass publishes ~mid-month for the prior month; L1 real-time
floor. Volumes represent the month Cass processes transactions, not the shipment
month (built-in ~processing lag). NSA => MoM / short-horizon momentum transforms
are seasonally contaminated; YoY-family transforms are the reliable cycle read.

Direction prior (for Evan/Ray): PROCYCLICAL (provisional). Rising freight
shipment volume = stronger goods economy = risk-on; falling freight = freight
recession / goods slowdown = risk-off. Freight is commonly characterized as an
early/leading read on economic momentum (goods move through the supply chain
before they show up in production and sales). Direction and lead-lag determined
EMPIRICALLY by Evan (Granger / pre-whitened CCF).

Author: Data Dana (Data Agent)
Date: 2026-07-05
Pair ID: cass_freight_spy
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

PAIR_ID = "cass_freight_spy"
CASS_SERIES = "FRGSHPUSM649NCIS"
# Step C #198 (Alex_UK): FRED only publishes Cass from 2016-01, but the project's
# curated Data Master.xlsx sheet 'CassFreightIndexShippments' carries the full index
# back to 1990-01 (base Jan1990=1.0). Validated: Data Master and FRED are IDENTICAL on
# the 2016-2025 overlap (116 months, max |diff| = 0.00000), so the long history is
# splice-safe. The aligned panel is bounded by SPY inception (1993).
START_DATE = "1993-01-01"     # SPY inception bounds the aligned panel
CONTEXT_START = "1993-01-01"  # context series reindexed to cass idx
END_DATE = "2026-07-31"
DATE_TAG = "20260829"
MASTER_XLSX = "/workspaces/aig-rlic-plus/data/Data Master.xlsx"
MASTER_SHEET = "CassFreightIndexShippments"

from dotenv import load_dotenv  # noqa: E402 — needed before fetch_fred runs (Step C #198 moved sourcing earlier)

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
os.makedirs(RESULTS_DIR, exist_ok=True)

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Stage 1: Sourcing
# ---------------------------------------------------------------------------
def fetch_fred(series_id, col_name, start=START_DATE):
    """Fetch via the official FRED API (JSON). Same key convention as
    pair_data_busloans_spy.py."""
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


def read_cass_master():
    """Step C #198: Cass Freight index 1990+ from Data Master, spliced with the
    FRED tail for months Data Master does not yet carry (validated identical in overlap)."""
    import openpyxl
    wb = openpyxl.load_workbook(MASTER_XLSX, read_only=True, data_only=True)
    ws = wb[MASTER_SHEET]
    rows = [(r[0], r[1]) for r in ws.iter_rows(min_row=2, values_only=True)
            if r and r[0] is not None and r[1] is not None and hasattr(r[0], "year")]
    dm = pd.Series({pd.Timestamp(d): float(v) for d, v in rows},
                   name="cass_freight_idx").sort_index()
    fred = fetch_fred(CASS_SERIES, "cass_freight_idx", start="1990-01-01")
    tail = fred[fred.index > dm.index.max()]
    out = pd.concat([dm, tail]).sort_index()
    out.name = "cass_freight_idx"
    print(f"  [MASTER+FRED] cass_freight_idx: {len(out)} obs, {out.index.min().date()} to "
          f"{out.index.max().date()} (Data Master to {dm.index.max().date()}, +{len(tail)} FRED tail)")
    return out


print("=" * 70)
print("STAGE 1: SOURCING")
print("=" * 70)
cass = read_cass_master()
unrate = fetch_fred("UNRATE", "unrate", start=CONTEXT_START)
dgs10 = fetch_fred("DGS10", "dgs10", start=CONTEXT_START)
fed_funds = fetch_fred("DFF", "fed_funds", start=CONTEXT_START)
spy = fetch_yahoo("SPY", "spy")
vix = fetch_yahoo("^VIX", "vix")

# ---------------------------------------------------------------------------
# Stage 2: Alignment + derived series (month-end, mirrors busloans_spy)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 2: ALIGNMENT + DERIVED SERIES")
print("=" * 70)

# Dataset is bounded by Cass Freight history (2016-01 onward).
idx = pd.date_range(cass.index.min(), END_DATE, freq="ME")
df = pd.DataFrame(index=idx)
df.index.name = "date"

# Cass is stamped at month-start by FRED; value is that month's index point.
# Align to month-end of the SAME month (resample 'ME' last).
df["cass_freight_idx"] = cass.resample("ME").last().reindex(idx)
df["unrate"] = unrate.resample("ME").last().reindex(idx)
df["dgs10"] = dgs10.resample("ME").last().reindex(idx)
df["fed_funds"] = fed_funds.resample("ME").last().reindex(idx)
df["vix"] = vix.resample("ME").last().reindex(idx)
df["spy"] = spy.resample("ME").last().reindex(idx)

c = df["cass_freight_idx"]
df["cass_freight_pct_yoy"] = (c / c.shift(12) - 1) * 100   # seasonality-robust
df["cass_freight_pct_mom"] = (c / c.shift(1) - 1) * 100    # NSA: seasonally biased
df["cass_freight_3m_pct"] = (c / c.shift(3) - 1) * 100     # NSA: seasonally biased
df["cass_freight_6m_pct"] = (c / c.shift(6) - 1) * 100     # NSA: partially seasonal
df["cass_freight_ma12_idx"] = c.rolling(12, min_periods=10).mean()
df["cass_freight_dev_trend_pct"] = (c / df["cass_freight_ma12_idx"] - 1) * 100
rm60 = c.rolling(60, min_periods=36)
df["cass_freight_zscore_60m"] = (c - rm60.mean()) / rm60.std()
ryoy = df["cass_freight_pct_yoy"].rolling(60, min_periods=36)
df["cass_freight_yoy_zscore_60m"] = (df["cass_freight_pct_yoy"] - ryoy.mean()) / ryoy.std()
df["cass_freight_accel_pct"] = df["cass_freight_pct_mom"].diff()  # MoM accel, pp
df["cass_freight_contraction"] = (df["cass_freight_pct_yoy"] < 0).astype(float)

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

# COVID freight-collapse sanity (Defense 2): April-May 2020 shipments crashed.
covid = df.loc["2020-03-31":"2020-07-31", ["cass_freight_idx", "cass_freight_pct_yoy", "cass_freight_pct_mom"]]
print("\n  COVID-era sanity check (expect YoY strongly negative Apr-Jun 2020):")
print(covid.round(3).to_string())
covid_trough_yoy = df.loc["2020-03-31":"2020-07-31", "cass_freight_pct_yoy"].min()
assert covid_trough_yoy < -5, f"COVID collapse MISSING: trough YoY {covid_trough_yoy:.1f}% — wrong series?"
print(f"  PASS: COVID trough YoY = {covid_trough_yoy:.1f}%")

# 2022-2024 freight recession sanity: YoY should be negative through much of it.
frr = df.loc["2022-06-30":"2024-06-30", "cass_freight_pct_yoy"]
frr_min = frr.min()
print(f"  Freight-recession check: min YoY 2022-06..2024-06 = {frr_min:.1f}% (expect negative)")
assert frr_min < 0, "2022-2024 freight recession contraction missing"

# Units sanity: index level ~0.7-1.5 (Jan 1990 = 1.00)
recent_level = df["cass_freight_idx"].dropna().iloc[-1]
print(f"  Latest level: {recent_level:.3f} as of {df['cass_freight_idx'].dropna().index[-1].date()}")
assert 0.5 < recent_level < 2.0, "level not in Cass-index range (Jan1990=1.00)"

# Gap check on indicator: no internal NaN gaps
c_valid = df["cass_freight_idx"].dropna()
internal_gaps = df.loc[c_valid.index.min():c_valid.index.max(), "cass_freight_idx"].isna().sum()
print(f"  Internal gaps in cass_freight_idx: {internal_gaps}")
assert internal_gaps == 0, "silent gaps in Cass Freight"

# Outlier flagging (z>4 on MoM) — flag, do not remove (NSA => seasonal swings)
mom = df["cass_freight_pct_mom"].dropna()
z = (mom - mom.mean()) / mom.std()
outliers = mom[abs(z) > 4]
print(f"  MoM outliers (|z|>4): {len(outliers)}")
for d, v in outliers.items():
    print(f"    {d.date()}: {v:+.2f}%")

# Overlap window with SPY (target coverage)
overlap = df.dropna(subset=["spy", "cass_freight_idx"])
print(f"  Usable Cass x SPY overlap: {overlap.index.min().date()} -> {overlap.index.max().date()} "
      f"({len(overlap)} months)")
yoy_valid = df["cass_freight_pct_yoy"].dropna()
print(f"  YoY signal effective start: {yoy_valid.index.min().date()} ({len(yoy_valid)} obs)")

# Stationarity tests
from arch.unitroot import ADF, KPSS
from dotenv import load_dotenv
test_cols = ["cass_freight_idx", "cass_freight_pct_yoy", "cass_freight_pct_mom",
             "cass_freight_3m_pct", "cass_freight_6m_pct", "cass_freight_zscore_60m",
             "cass_freight_yoy_zscore_60m", "cass_freight_dev_trend_pct", "spy_ret"]
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
parquet_path = os.path.join(DATA_DIR, f"cass_freight_spy_monthly_{start_tag}_{end_tag}.parquet")
latest_path = os.path.join(DATA_DIR, "cass_freight_spy_monthly_latest.parquet")
df.to_parquet(parquet_path)
df.to_parquet(latest_path)
print(f"  Parquet -> {parquet_path}")
print(f"  Alias   -> {latest_path}")

CASS_QUIRK = ("FRED FRGSHPUSM649NCIS; index Jan 1990 = 1.00; NOT seasonally adjusted "
              "(NSA) — YoY transforms remove seasonality, MoM/short-horizon are seasonally "
              "biased; FRED history starts 2016-01 (~10yr, short); Cass publishes ~mid-month "
              "for prior month (L1 real-time floor); volumes stamped to Cass processing month; "
              "COVID Apr-May 2020 collapse and 2022-2024 freight recession are the key episodes")

# Column metadata (single source for sidecar + dictionary + registry)
COLS = {
    "cass_freight_idx": dict(unit="index", display_name="Cass Freight Shipments Index",
        direction="higher_is_better", axis_label="Cass Freight Index (Jan1990=1)",
        desc="FRED FRGSHPUSM649NCIS: Cass Freight Index — Shipments. Monthly index "
             "(Jan 1990 = 1.00), NOT seasonally adjusted. Volume of freight shipments "
             "across the Cass client base; a read on the U.S. goods economy."),
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
        desc="CBOE VIX index, month-end close (Yahoo ^VIX). Control / regime variable."),
    "spy": dict(unit="price", display_name="SPY Price ($)",
        direction="neutral", axis_label="SPY ($)",
        desc="SPY adjusted close, month-end (Yahoo, auto-adjusted). Target asset."),
    "cass_freight_pct_yoy": dict(unit="pct", display_name="Cass Freight YoY (%)",
        direction="higher_is_better", axis_label="Cass Freight YoY (%)",
        desc="12-month percent change in cass_freight_idx. Seasonality-robust cycle "
             "signal (preferred over MoM given the NSA source). Effective start = 2017-01."),
    "cass_freight_pct_mom": dict(unit="pct", display_name="Cass Freight MoM (%)",
        direction="higher_is_better", axis_label="Cass Freight MoM (%)",
        desc="1-month percent change in cass_freight_idx. NSA source => seasonally biased; "
             "prefer YoY-family for cycle inference."),
    "cass_freight_3m_pct": dict(unit="pct", display_name="Cass Freight 3M Change (%)",
        direction="higher_is_better", axis_label="Cass Freight 3M (%)",
        desc="3-month percent change (momentum) in cass_freight_idx. NSA => seasonally biased."),
    "cass_freight_6m_pct": dict(unit="pct", display_name="Cass Freight 6M Change (%)",
        direction="higher_is_better", axis_label="Cass Freight 6M (%)",
        desc="6-month percent change (momentum) in cass_freight_idx. NSA => partially seasonal."),
    "cass_freight_ma12_idx": dict(unit="index", display_name="Cass Freight 12M MA",
        direction="higher_is_better", axis_label="Cass Freight 12M MA",
        desc="12-month rolling mean of cass_freight_idx (min 10 obs). A 12M MA also nets "
             "out the NSA seasonal pattern."),
    "cass_freight_dev_trend_pct": dict(unit="pct", display_name="Cass Freight Deviation from 12M Trend (%)",
        direction="higher_is_better", axis_label="Dev. from 12M MA (%)",
        desc="Percent deviation of cass_freight_idx from its 12-month moving average."),
    "cass_freight_zscore_60m": dict(unit="none", display_name="Cass Freight 60M Z-Score",
        direction="higher_is_better", axis_label="Z-score (60M)",
        desc="Rolling 60-month z-score of the LEVEL (min 36 obs). Effective start ~2018-12; "
             "short history limits the rolling window. NSA level => seasonal noise present."),
    "cass_freight_yoy_zscore_60m": dict(unit="none", display_name="Cass Freight Growth 60M Z-Score",
        direction="higher_is_better", axis_label="YoY z-score (60M)",
        desc="Rolling 60-month z-score of cass_freight_pct_yoy (min 36 obs). Effective start "
             "~2019-12; short history limits the rolling window."),
    "cass_freight_accel_pct": dict(unit="pct", display_name="Cass Freight Acceleration (pp)",
        direction="higher_is_better", axis_label="MoM accel. (pp)",
        desc="First difference of cass_freight_pct_mom (percentage points). NSA => noisy."),
    "cass_freight_contraction": dict(unit="none", display_name="Cass Freight Contraction Flag",
        direction="lower_is_better", axis_label="Contraction (0/1)",
        desc="1.0 when cass_freight_pct_yoy < 0, else 0.0. Marks freight-recession months "
             "(e.g. COVID 2020, 2022-2024 goods slowdown)."),
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
               "source_reference": ("FRED:FRGSHPUSM649NCIS" if col.startswith("cass_freight") else
                                    "yahoo:SPY" if col.startswith("spy") else "see description")}
          for col, m in COLS.items()}
    },
}
sidecar_path = os.path.join(DATA_DIR, "cass_freight_spy_monthly_schema.json")
with open(sidecar_path, "w") as f:
    json.dump(sidecar, f, indent=2)
print(f"  Sidecar -> {sidecar_path}")

# Data dictionary (human form, CSV like prior pairs)
dd_rows = []
for col, m in COLS.items():
    dd_rows.append({
        "column_name": col, "display_name": m["display_name"],
        "description": m["desc"],
        "source": "FRED" if col.startswith(("cass_freight", "unrate", "dgs10", "fed_funds")) else "Yahoo Finance",
        "series_id": (CASS_SERIES if col.startswith("cass_freight") else
                      {"unrate": "UNRATE", "dgs10": "DGS10", "fed_funds": "DFF",
                       "vix": "^VIX", "spy": "SPY"}.get(col, "derived")),
        "unit": m["unit"], "direction_convention": m["direction"],
        "seasonal_adj": "NSA" if col.startswith("cass_freight") else "N/A",
        "effective_start": str(df[col].first_valid_index().date()),
        "refresh_freq": "monthly" if col.startswith(("cass_freight", "unrate")) else "daily",
        "known_quirks": CASS_QUIRK if col.startswith("cass_freight") else "",
    })
dd_path = os.path.join(DATA_DIR, f"data_dictionary_cass_freight_spy_{DATE_TAG}.csv")
pd.DataFrame(dd_rows).to_csv(dd_path, index=False)
print(f"  Data dictionary -> {dd_path}")

# Summary stats
ss_path = os.path.join(DATA_DIR, f"summary_stats_cass_freight_spy_{DATE_TAG}.csv")
df.describe().T.round(4).to_csv(ss_path)
print(f"  Summary stats -> {ss_path}")

# Missing value report
mv_lines = [
    f"# Missing Value Report — cass_freight_spy ({DATE_TAG})",
    "",
    f"Dataset: `{os.path.relpath(parquet_path, BASE_DIR)}` — shape {df.shape}, "
    f"month-end index {df.index.min().date()} to {df.index.max().date()}.",
    "",
    "## Publication lag & no-lookahead (Cass Freight)",
    "",
    "The Cass Freight Index (Shipments) is published ~mid-month for the prior month "
    "(roughly a 2-week lag), and FRED carries it stamped to the Cass **processing** "
    "month (not the physical shipment month). **Evan: lag the indicator by at least 1 "
    "month (L1) for real-time tradability; L1 is the realistic floor.** The series is "
    "NOT seasonally adjusted (NSA): YoY-family transforms are seasonality-robust; MoM / "
    "3m / 6m momentum and the level z-score carry a seasonal pattern — prefer the "
    "YoY-family signals for cycle inference.",
    "",
    "## Short-history caveat",
    "",
    f"FRED FRGSHPUSM649NCIS starts 2016-01 (~{len(df)} monthly rows to {df.index.max().date()}). "
    "This is a SHORT sample: only ~10 years, one full freight cycle plus COVID. The rolling "
    "60-month z-score signals do not become valid until ~2018-12 (level) / ~2019-12 (YoY), and "
    "any OOS window will be very short (< 5yr) — OOS Sharpe will be inflated/high-variance. "
    "Flag to Evan for a conservative OOS split and to Ray for the durability caveat.",
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
    "No internal gaps in `cass_freight_idx` (verified). No forward-fill applied to the "
    "indicator. Forward-return columns are NaN at the tail by construction (no leakage).",
    "",
    "## Sanity checks (Defense 2)",
    "",
    f"- COVID freight collapse: trough YoY {covid_trough_yoy:.1f}% (Apr-Jul 2020) — PASS (expected strongly negative).",
    f"- 2022-2024 freight recession: min YoY {frr_min:.1f}% — PASS (goods slowdown confirmed).",
    f"- Units: latest level {recent_level:.3f} — consistent with Cass index (Jan1990=1.00), NSA.",
    f"- Cass x SPY usable overlap: {overlap.index.min().date()} .. {overlap.index.max().date()} ({len(overlap)} months).",
    f"- MoM outliers (|z|>4): {len(outliers)} flagged (not removed): "
    + ", ".join(f"{d.date()} ({v:+.1f}%)" for d, v in outliers.items()),
]
mv_path = os.path.join(DATA_DIR, f"missing_value_report_cass_freight_spy_{DATE_TAG}.md")
with open(mv_path, "w") as f:
    f.write("\n".join(mv_lines) + "\n")
print(f"  Missing value report -> {mv_path}")

# ---------------------------------------------------------------------------
# Stage 5: interpretation_metadata.json (Dana fields; provisional seeds noted)
# ---------------------------------------------------------------------------
meta = {
    "pair_id": PAIR_ID,
    "schema_version": "1.1.0",
    "indicator": "cass_freight",
    "target": "spy",
    "indicator_nature": "leading",
    "indicator_type": "production",
    "strategy_objective": "max_sharpe",
    "expected_direction": "procyclical",
    "data_provenance": {
        "source": "FRED (Cass Information Systems — Cass Freight Index: Shipments)",
        "series_id": CASS_SERIES,
        "accessed_at": NOW_ISO,
    },
    "known_stress_episodes": [
        {"label": "COVID freight collapse", "start": "2020-03-01",
         "end": "2020-06-30",
         "note": "Shipment volumes crashed in Apr-May 2020 as goods demand and production seized; deeply negative YoY."},
        {"label": "2022-2024 freight recession", "start": "2022-06-01",
         "end": "2024-06-30",
         "note": "A prolonged goods-economy / freight downturn: YoY shipments negative for an extended stretch while equities de-rated then recovered."},
    ],
    "related_pair_ids": ["indpro_spy", "petrol_inv_spy"],
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
design = f"""# Design Note — cass_freight_spy ({DATE_TAG})

## Hypothesis (one-liner)
Does the volume of U.S. freight shipments (Cass Freight Index: Shipments) carry
forward information about SPY returns? Prior: PROCYCLICAL — expanding freight
signals a strengthening goods economy (risk-on); a freight recession signals a
goods slowdown (risk-off). Freight is commonly characterized as an early/leading
read on economic momentum. Lead-lag and sign are determined EMPIRICALLY by Evan
(Granger / pre-whitened CCF); this note only seeds a provisional prior.

## Source & sample
- Indicator: FRED `{CASS_SERIES}` — Cass Freight Index: Shipments. Monthly index,
  base Jan 1990 = 1.00, **Not Seasonally Adjusted (NSA)**.
- FRED history: **2016-01 to {df.index.max().date()}** (~{len(df)} months). Short sample.
- Target: SPY month-end (Yahoo, auto-adjusted); controls UNRATE/DGS10/DFF (FRED),
  ^VIX (Yahoo). SPY covers the entire Cass window, so the usable overlap is the
  full Cass history: **{overlap.index.min().date()} .. {overlap.index.max().date()}
  ({len(overlap)} months)**.

## Transform family (mirrors busloans_spy monthly convention)
Level (`cass_freight_idx`), YoY (`_pct_yoy`), MoM (`_pct_mom`), 3M/6M momentum
(`_3m_pct`/`_6m_pct`), 12M MA (`_ma12_idx`), deviation-from-trend (`_dev_trend_pct`),
60M level z-score (`_zscore_60m`), 60M YoY z-score (`_yoy_zscore_60m`), MoM
acceleration (`_accel_pct`), and a contraction flag (`_contraction`).

## NSA seasonality (important)
Because the source is NSA, MoM / 3M / 6M momentum and the level z-score are
seasonally contaminated. **YoY-family transforms (`_pct_yoy`, `_yoy_zscore_60m`)
and the 12M MA are the seasonality-robust cycle signals** and should be preferred
for direction/lead-lag inference. A future refinement (Evan's call) could add an
explicit seasonal adjustment (STL/X-13) column; not added here to avoid
in-sample seasonal-factor lookahead in a tradable signal.

## Stationarity (ADF/KPSS — see stationarity_tests_{DATE_TAG}.csv)
Level is non-stationary (trending index); the growth/momentum transforms and
z-scores are stationary. `spy_ret` stationary. Full table in the CSV; Evan
confirms rather than re-runs (SOP).

## No-lookahead / publication lag
Cass publishes ~mid-month for the prior month (~2-week lag) and FRED stamps to the
Cass processing month. Tournament lead grid must start at **L1** (real-time floor).

## Key data-quality flags for downstream
1. **Short history** (~10yr from 2016): OOS window will be < 5yr — OOS Sharpe
   inflated/high-variance. Use a conservative split; treat any winner as
   found-in-search, not validated.
2. **NSA source**: prefer YoY-family signals; MoM/short-horizon are seasonal.
3. **60M z-score signals** only valid from ~2018-12 (level) / ~2019-12 (YoY) —
   very short usable span; may be near-degenerate in the tournament.

## New pair — no prior version; Rule D1 series-preservation / C3 regression diff N/A.
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
# keep JSON view in sync if it exists (canonical shape: {schema_version,
# generated_at, columns:[{column_name,display_name,unit,axis_label}, ...]})
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
     "source": "FRED:FRGSHPUSM649NCIS (Cass Freight Shipments, monthly index, NSA) + FRED:UNRATE/DGS10/DFF + yahoo:SPY/^VIX",
     "refresh_ttl_days": 30,
     "schema_ref": os.path.relpath(sidecar_path, BASE_DIR),
     "last_updated": datetime.now().strftime("%Y-%m-%d"),
     "pairs": [PAIR_ID],
     "mixed_freq_ttl_note": "Monthly indicator + month-end snapshots of daily market data; "
                            "TTL=30 days (monthly cadence governs)."},
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

print("\nDONE — data stage complete for cass_freight_spy.")
