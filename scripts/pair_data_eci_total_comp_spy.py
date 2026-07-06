#!/usr/bin/env python3
"""
Data Stage: Employment Cost Index (Total Compensation) x SPY
============================================================
Prospective pair eci_total_comp_spy. Branch feat260705_eci_spy.

Dana-owned stage 1 of the pipeline (Dana -> Evan -> Vera+Ray -> Ace -> Quincy).
Mirrors scripts/pair_data_cass_freight_spy.py artifact shapes — but this is the
portal's FIRST QUARTERLY pair, so the template is adapted deliberately:

  * Native quarterly (quarter-end) index — NOT the monthly template.
  * SPY forward returns at quarterly-natural horizons: 1q / 2q / 4q
    (the quarterly analogues of the project's 3M / 6M / 12M monthly horizons).
  * Transform windows named in QUARTERS: z-scores use 20q (~5yr, the analogue
    of the monthly 60m windows), trend MA uses 8q (~2yr). No "60m" naming.
  * Publication lag: ECI for quarter Q is released ~1 month after quarter end
    (end of Jan/Apr/Jul/Oct). At quarterly granularity the quarter-Q signal is
    first tradable in Q+1 => tournament lead grid FLOORS AT L1 (quarters).

INDICATOR: FRED ECIALLCIV — Employment Cost Index: Total compensation: All
Civilian. Quarterly, SEASONALLY ADJUSTED, Index Dec 2005 = 100. History
2001-Q1 -> 2026-Q1 (~101 obs, 25 years: 2001 recession, GFC, COVID, the
2021-23 wage-inflation surge). SA source => QoQ/short-horizon transforms are
NOT seasonally contaminated (unlike NSA Cass Freight).

Direction prior (for Evan/Ray): COUNTERCYCLICAL wage-inflation hypothesis
(provisional). Accelerating total-compensation growth = wage-inflation
pressure = tighter Fed / margin compression = risk-off for equities;
decelerating ECI = disinflation = easier policy = risk-on. ECI is a classic
LAGGING indicator (labor costs turn after the cycle — Conference Board lists
unit-labor-cost change among the lagging composite components). Direction and
lead-lag determined EMPIRICALLY by Evan (Granger / pre-whitened CCF).

Author: Data Dana (Data Agent)
Date: 2026-07-06
Pair ID: eci_total_comp_spy
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

PAIR_ID = "eci_total_comp_spy"
ECI_SERIES = "ECIALLCIV"
START_DATE = "2001-01-01"     # full FRED ECIALLCIV history
CONTEXT_START = "1999-01-01"  # context series fetched earlier for clean q-end resample
END_DATE = "2026-06-30"
DATE_TAG = "20260706"

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
    pair_data_cass_freight_spy.py."""
    import urllib.request
    api_key = os.environ.get("FRED_API_KEY") or "952aa4d0c4b2057609fbf3ecc6954e58"
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
eci = fetch_fred(ECI_SERIES, "eci_total_comp_idx")
unrate = fetch_fred("UNRATE", "unrate", start=CONTEXT_START)
dgs10 = fetch_fred("DGS10", "dgs10", start=CONTEXT_START)
fed_funds = fetch_fred("DFF", "fed_funds", start=CONTEXT_START)
spy = fetch_yahoo("SPY", "spy")
vix = fetch_yahoo("^VIX", "vix")

# ---------------------------------------------------------------------------
# Stage 2: Alignment + derived series (QUARTER-END index — first quarterly pair)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 2: ALIGNMENT + DERIVED SERIES (quarterly)")
print("=" * 70)

# Dataset bounded by ECI history (2001-Q1 onward). Calendar quarters (QE-DEC).
# NOTE: FRED stamps quarter Q at quarter-START (2026-Q1 = 2026-01-01), so the
# range must extend to the quarter-END of the LAST observation or the final
# quarter silently drops (caught on first run: 100 vs 101 obs).
idx = pd.date_range(eci.index.min(),
                    eci.index.max() + pd.offsets.QuarterEnd(0), freq="QE-DEC")
df = pd.DataFrame(index=idx)
df.index.name = "date"

# FRED stamps ECI at quarter-START (2001-01-01 = 2001-Q1). The value is the
# quarter's index point. Align to quarter-END of the SAME quarter
# (resample 'QE-DEC' last). Market/context series take their quarter-end value.
df["eci_total_comp_idx"] = eci.resample("QE-DEC").last().reindex(idx)
df["unrate"] = unrate.resample("QE-DEC").last().reindex(idx)
df["dgs10"] = dgs10.resample("QE-DEC").last().reindex(idx)
df["fed_funds"] = fed_funds.resample("QE-DEC").last().reindex(idx)
df["vix"] = vix.resample("QE-DEC").last().reindex(idx)
df["spy"] = spy.resample("QE-DEC").last().reindex(idx)

e = df["eci_total_comp_idx"]
# Quarterly-adapted transform family (windows named in QUARTERS):
df["eci_total_comp_pct_qoq"] = (e / e.shift(1) - 1) * 100    # 1q growth (SA: clean)
df["eci_total_comp_pct_2q"] = (e / e.shift(2) - 1) * 100     # 2q rate-of-change
df["eci_total_comp_pct_yoy"] = (e / e.shift(4) - 1) * 100    # 4q = YoY growth
df["eci_total_comp_ma8q_idx"] = e.rolling(8, min_periods=6).mean()
df["eci_total_comp_dev_trend_pct"] = (e / df["eci_total_comp_ma8q_idx"] - 1) * 100
rm20 = e.rolling(20, min_periods=12)
df["eci_total_comp_zscore_20q"] = (e - rm20.mean()) / rm20.std()
ryoy = df["eci_total_comp_pct_yoy"].rolling(20, min_periods=12)
df["eci_total_comp_yoy_zscore_20q"] = (df["eci_total_comp_pct_yoy"] - ryoy.mean()) / ryoy.std()
df["eci_total_comp_accel_pct"] = df["eci_total_comp_pct_qoq"].diff()   # QoQ accel, pp
df["eci_total_comp_yoy_accel_pct"] = df["eci_total_comp_pct_yoy"].diff()  # YoY accel, pp

s = df["spy"]
df["spy_ret"] = s.pct_change()                 # 1q simple return
df["spy_fwd_1q"] = s.shift(-1) / s - 1         # ~3M forward (quarterly analogue)
df["spy_fwd_2q"] = s.shift(-2) / s - 1         # ~6M forward
df["spy_fwd_4q"] = s.shift(-4) / s - 1         # ~12M forward

print(f"  Quarterly dataset: {df.shape}, {df.index.min().date()} to {df.index.max().date()}")
print(f"  Columns: {list(df.columns)}")

# ---------------------------------------------------------------------------
# Stage 3: Validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 3: VALIDATION")
print("=" * 70)

assert df.index.is_monotonic_increasing, "index not monotonic"
assert not df.index.duplicated().any(), "duplicate timestamps"
assert df.index.max() <= pd.Timestamp(END_DATE) + pd.offsets.QuarterEnd(0), "future leakage"

# Defense 2 sanity: 2021-22 wage surge — YoY total comp should exceed 4.5%
surge = df.loc["2021-06-30":"2023-06-30", "eci_total_comp_pct_yoy"]
surge_max = surge.max()
print(f"  Wage-surge check: max YoY 2021Q2..2023Q2 = {surge_max:.2f}% (BLS peak ~5.1% mid-2022)")
assert surge_max > 4.5, "2021-23 wage surge missing — wrong series?"

# Pre-surge regime sanity: 2010s YoY should sit roughly 1.5-3%
dec = df.loc["2012-03-31":"2019-12-31", "eci_total_comp_pct_yoy"]
print(f"  2010s regime: YoY range {dec.min():.2f}%..{dec.max():.2f}% (expect ~1.5-3%)")
assert 1.0 < dec.min() and dec.max() < 3.5, "2010s ECI YoY out of expected band"

# ECI level is monotone-ish (nominal comp index rarely falls) — count declines
declines = (df["eci_total_comp_pct_qoq"].dropna() < 0).sum()
print(f"  QoQ declines in ECI level: {declines} (expect 0 or near-0; nominal comp is sticky)")

# Gap check: quarterly index must have no internal NaN
e_valid = df["eci_total_comp_idx"].dropna()
internal_gaps = df.loc[e_valid.index.min():e_valid.index.max(), "eci_total_comp_idx"].isna().sum()
print(f"  Internal gaps in eci_total_comp_idx: {internal_gaps}")
assert internal_gaps == 0, "silent gaps in ECI"

# Outlier flagging (z>4 on QoQ) — flag, do not remove (2021-22 surge is REAL)
qoq = df["eci_total_comp_pct_qoq"].dropna()
z = (qoq - qoq.mean()) / qoq.std()
outliers = qoq[abs(z) > 4]
print(f"  QoQ outliers (|z|>4): {len(outliers)}")
for d, v in outliers.items():
    print(f"    {d.date()}: {v:+.2f}%")

# Overlap window with SPY
overlap = df.dropna(subset=["spy", "eci_total_comp_idx"])
print(f"  Usable ECI x SPY overlap: {overlap.index.min().date()} -> {overlap.index.max().date()} "
      f"({len(overlap)} quarters)")
# Effective sample per transform (few-obs honesty check)
print("\n  Effective sample per transform:")
for col in df.columns:
    v = df[col].dropna()
    if col.startswith("eci_total_comp") and len(v):
        print(f"    {col}: {len(v)} obs, starts {v.index.min().date()}")

# Stationarity tests
from arch.unitroot import ADF, KPSS
test_cols = ["eci_total_comp_idx", "eci_total_comp_pct_qoq", "eci_total_comp_pct_2q",
             "eci_total_comp_pct_yoy", "eci_total_comp_dev_trend_pct",
             "eci_total_comp_zscore_20q", "eci_total_comp_yoy_zscore_20q",
             "eci_total_comp_accel_pct", "eci_total_comp_yoy_accel_pct", "spy_ret"]
rows = []
for col in test_cols:
    x = df[col].dropna()
    try:
        adf = ADF(x, max_lags=8)
        rows.append({"variable": col, "test": "ADF", "statistic": round(adf.stat, 4),
                     "p_value": round(adf.pvalue, 4), "lags": adf.lags,
                     "conclusion": "Stationary at 5%" if adf.pvalue < 0.05 else "Non-stationary"})
    except Exception as e2:
        rows.append({"variable": col, "test": "ADF", "statistic": np.nan,
                     "p_value": np.nan, "lags": np.nan, "conclusion": f"failed: {e2}"})
    try:
        kp = KPSS(x)
        rows.append({"variable": col, "test": "KPSS", "statistic": round(kp.stat, 4),
                     "p_value": round(kp.pvalue, 4), "lags": kp.lags,
                     "conclusion": "Fail to reject stationarity" if kp.pvalue > 0.05
                     else "Reject stationarity at 5%"})
    except Exception as e2:
        rows.append({"variable": col, "test": "KPSS", "statistic": np.nan,
                     "p_value": np.nan, "lags": np.nan, "conclusion": f"failed: {e2}"})
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
parquet_path = os.path.join(DATA_DIR, f"eci_total_comp_spy_quarterly_{start_tag}_{end_tag}.parquet")
latest_path = os.path.join(DATA_DIR, "eci_total_comp_spy_quarterly_latest.parquet")
df.to_parquet(parquet_path)
df.to_parquet(latest_path)
print(f"  Parquet -> {parquet_path}")
print(f"  Alias   -> {latest_path}")

ECI_QUIRK = ("FRED ECIALLCIV; Employment Cost Index: Total compensation: All Civilian; "
             "QUARTERLY (first quarterly pair in the portal); index Dec 2005 = 100; "
             "SEASONALLY ADJUSTED (QoQ transforms are clean, unlike NSA sources); "
             "history 2001-Q1 onward (~101 obs, 25yr but FEW observations); BLS releases "
             "quarter Q ~1 month after quarter end (end of Jan/Apr/Jul/Oct) => at quarterly "
             "granularity the signal is tradable from Q+1: tournament lead grid FLOORS AT "
             "L1 (quarters); NOTE: Data Master 'ECI' sheet carries the NSA private-industry "
             "variants (Dec 2015=100) — a DIFFERENT variant from this SA all-civilian series; "
             "key episodes: 2001 recession, GFC deceleration, COVID, 2021-23 wage surge "
             "(YoY peak ~5.1% mid-2022, real)")

COLS = {
    "eci_total_comp_idx": dict(unit="index", display_name="Employment Cost Index (Total Compensation)",
        direction="lower_is_better", axis_label="ECI Total Comp (Dec2005=100)",
        desc="FRED ECIALLCIV: Employment Cost Index — Total compensation, All Civilian. "
             "Quarterly, SA, index Dec 2005 = 100. Measures employer labor costs (wages + "
             "benefits); the Fed's preferred wage-inflation gauge. Countercyclical prior: "
             "faster comp growth = wage-inflation pressure = risk-off."),
    "unrate": dict(unit="pct", display_name="Unemployment Rate (%)",
        direction="lower_is_better", axis_label="Unemployment (%)",
        desc="FRED UNRATE: civilian unemployment rate, quarter-end month value. Control series."),
    "dgs10": dict(unit="pct", display_name="10Y Treasury Yield (%)",
        direction="neutral", axis_label="10Y Yield (%)",
        desc="FRED DGS10: 10-year constant-maturity Treasury yield, quarter-end value. Control."),
    "fed_funds": dict(unit="pct", display_name="Fed Funds Rate (%)",
        direction="neutral", axis_label="Fed Funds (%)",
        desc="FRED DFF: effective federal funds rate, quarter-end value. Control."),
    "vix": dict(unit="index", display_name="VIX",
        direction="lower_is_better", axis_label="VIX",
        desc="CBOE VIX index, quarter-end close (Yahoo ^VIX). Control / regime variable."),
    "spy": dict(unit="price", display_name="SPY Price ($)",
        direction="neutral", axis_label="SPY ($)",
        desc="SPY adjusted close, quarter-end (Yahoo, auto-adjusted). Target asset."),
    "eci_total_comp_pct_qoq": dict(unit="pct", display_name="ECI Total Comp QoQ (%)",
        direction="lower_is_better", axis_label="ECI QoQ (%)",
        desc="1-quarter percent change in eci_total_comp_idx. SA source => seasonally clean. "
             "Effective start 2001-Q2."),
    "eci_total_comp_pct_2q": dict(unit="pct", display_name="ECI Total Comp 2Q Change (%)",
        direction="lower_is_better", axis_label="ECI 2Q (%)",
        desc="2-quarter (~6M) percent change in eci_total_comp_idx. Effective start 2001-Q3."),
    "eci_total_comp_pct_yoy": dict(unit="pct", display_name="ECI Total Comp YoY (%)",
        direction="lower_is_better", axis_label="ECI YoY (%)",
        desc="4-quarter (year-over-year) percent change in eci_total_comp_idx — the headline "
             "wage-inflation read (BLS/Fed convention). Effective start 2002-Q1."),
    "eci_total_comp_ma8q_idx": dict(unit="index", display_name="ECI Total Comp 8Q MA",
        direction="lower_is_better", axis_label="ECI 8Q MA",
        desc="8-quarter (~2yr) rolling mean of eci_total_comp_idx (min 6 obs). Trend line "
             "for deviation-from-trend."),
    "eci_total_comp_dev_trend_pct": dict(unit="pct", display_name="ECI Deviation from 8Q Trend (%)",
        direction="lower_is_better", axis_label="Dev. from 8Q MA (%)",
        desc="Percent deviation of eci_total_comp_idx from its 8-quarter moving average."),
    "eci_total_comp_zscore_20q": dict(unit="none", display_name="ECI Total Comp 20Q Z-Score",
        direction="lower_is_better", axis_label="Z-score (20Q)",
        desc="Rolling 20-quarter (~5yr) z-score of the LEVEL (min 12 obs). Quarterly analogue "
             "of the monthly pairs' 60M z-score. Effective start ~2003-Q4; consumes ~12 of "
             "101 obs before first value."),
    "eci_total_comp_yoy_zscore_20q": dict(unit="none", display_name="ECI Growth 20Q Z-Score",
        direction="lower_is_better", axis_label="YoY z-score (20Q)",
        desc="Rolling 20-quarter z-score of eci_total_comp_pct_yoy (min 12 obs). Effective "
             "start ~2004-Q4 (YoY needs 4q + window needs 12q)."),
    "eci_total_comp_accel_pct": dict(unit="pct", display_name="ECI QoQ Acceleration (pp)",
        direction="lower_is_better", axis_label="QoQ accel. (pp)",
        desc="First difference of eci_total_comp_pct_qoq (percentage points). Wage-growth "
             "acceleration — the inflation-momentum signal. Effective start 2001-Q3."),
    "eci_total_comp_yoy_accel_pct": dict(unit="pct", display_name="ECI YoY Acceleration (pp)",
        direction="lower_is_better", axis_label="YoY accel. (pp)",
        desc="First difference of eci_total_comp_pct_yoy (percentage points). Smoother "
             "acceleration read. Effective start 2002-Q2."),
    "spy_ret": dict(unit="decimal_return", display_name="SPY Quarterly Return",
        direction="neutral", axis_label="SPY return",
        desc="SPY 1-quarter simple return (decimal)."),
    "spy_fwd_1q": dict(unit="decimal_return", display_name="SPY Forward 1Q Return",
        direction="neutral", axis_label="SPY fwd 1Q",
        desc="Forward 1-quarter (~3M) SPY return (decimal). Regression/tournament target — "
             "quarterly analogue of the monthly pairs' spy_fwd_3m."),
    "spy_fwd_2q": dict(unit="decimal_return", display_name="SPY Forward 2Q Return",
        direction="neutral", axis_label="SPY fwd 2Q",
        desc="Forward 2-quarter (~6M) SPY return (decimal). Regression/tournament target."),
    "spy_fwd_4q": dict(unit="decimal_return", display_name="SPY Forward 4Q Return",
        direction="neutral", axis_label="SPY fwd 4Q",
        desc="Forward 4-quarter (~12M) SPY return (decimal). Regression/tournament target."),
}
assert set(COLS) == set(df.columns), (
    f"COLS/parquet drift: {set(COLS) ^ set(df.columns)}")

# Cross-pair consistency (DATA-D13): canonical names already registered keep
# their existing registry display_name/unit/axis_label.
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
                 "description": "Quarter-end date index (parquet index column; first "
                                "QUARTERLY pair); "
                                f"spans {df.index.min().date()} through {df.index.max().date()}."},
        **{col: {"dtype": str(df[col].dtype), "unit": m["unit"],
               "display_name": m["display_name"], "direction": m["direction"],
               "description": m["desc"],
               "source_reference": ("FRED:ECIALLCIV" if col.startswith("eci_total_comp") else
                                    "yahoo:SPY" if col.startswith("spy") else "see description")}
          for col, m in COLS.items()}
    },
}
sidecar_path = os.path.join(DATA_DIR, "eci_total_comp_spy_quarterly_schema.json")
with open(sidecar_path, "w") as f:
    json.dump(sidecar, f, indent=2)
print(f"  Sidecar -> {sidecar_path}")

# Data dictionary (human form, CSV like prior pairs)
dd_rows = []
for col, m in COLS.items():
    dd_rows.append({
        "column_name": col, "display_name": m["display_name"],
        "description": m["desc"],
        "source": "FRED" if col.startswith(("eci_total_comp", "unrate", "dgs10", "fed_funds")) else "Yahoo Finance",
        "series_id": (ECI_SERIES if col.startswith("eci_total_comp") else
                      {"unrate": "UNRATE", "dgs10": "DGS10", "fed_funds": "DFF",
                       "vix": "^VIX", "spy": "SPY"}.get(col, "derived")),
        "unit": m["unit"], "direction_convention": m["direction"],
        "seasonal_adj": "SA" if col.startswith("eci_total_comp") else "N/A",
        "effective_start": str(df[col].first_valid_index().date()),
        "refresh_freq": "quarterly" if col.startswith("eci_total_comp") else
                        ("monthly" if col == "unrate" else "daily"),
        "known_quirks": ECI_QUIRK if col.startswith("eci_total_comp") else "",
    })
dd_path = os.path.join(DATA_DIR, f"data_dictionary_eci_total_comp_spy_{DATE_TAG}.csv")
pd.DataFrame(dd_rows).to_csv(dd_path, index=False)
print(f"  Data dictionary -> {dd_path}")

# Summary stats
ss_path = os.path.join(DATA_DIR, f"summary_stats_eci_total_comp_spy_{DATE_TAG}.csv")
df.describe().T.round(4).to_csv(ss_path)
print(f"  Summary stats -> {ss_path}")

# Missing value report
eff = {col: (int(df[col].isna().sum()), df[col].first_valid_index(), int(df[col].notna().sum()))
       for col in df.columns}
mv_lines = [
    f"# Missing Value Report — eci_total_comp_spy ({DATE_TAG})",
    "",
    f"Dataset: `{os.path.relpath(parquet_path, BASE_DIR)}` — shape {df.shape}, "
    f"QUARTER-END index {df.index.min().date()} to {df.index.max().date()} "
    "(first quarterly pair in the portal).",
    "",
    "## Publication lag & no-lookahead (ECI)",
    "",
    "BLS releases the ECI for quarter Q at the END OF THE MONTH FOLLOWING quarter end "
    "(end of Jan/Apr/Jul/Oct — ~1 month lag). At quarterly granularity that means the "
    "quarter-Q value is only tradable from quarter Q+1. **Evan: the tournament lead grid "
    "must FLOOR AT L1, where L is measured in QUARTERS (L1 = 1 quarter ≈ 3 months).** "
    "The series is SEASONALLY ADJUSTED, so QoQ and short-horizon transforms are clean — "
    "no NSA seasonal-contamination constraint (unlike Cass Freight).",
    "",
    "## Few-observations caveat (quarterly frequency)",
    "",
    f"ECIALLCIV spans 25 years but only {eff['eci_total_comp_idx'][2]} quarterly observations. "
    "Cycle coverage is good (2001 recession, GFC, COVID, 2021-23 wage surge) but the "
    "tournament sample is SMALL. Rolling 20Q z-scores consume ~12 quarters before first "
    "value; YoY consumes 4. Any OOS split leaves few OOS quarters — OOS statistics will "
    "be high-variance. Flag to Evan for a conservative split and simple specifications; "
    "flag to Ray for the durability caveat.",
    "",
    "## Missing values by column",
    "",
    "| Column | NaN count | Effective obs | Pattern |",
    "|---|---|---|---|",
]
for col in df.columns:
    n, fv, nn = eff[col]
    pattern = (f"leading (series/transform starts {fv.date()})" if n and fv is not None else "none")
    if col.startswith("spy_fwd"):
        pattern += "; trailing NaN from forward shift"
    mv_lines.append(f"| `{col}` | {n} | {nn} | {pattern} |")
mv_lines += [
    "",
    "No internal gaps in `eci_total_comp_idx` (verified). No forward-fill applied. "
    "Forward-return columns are NaN at the tail by construction (no leakage).",
    "",
    "## Sanity checks (Defense 2)",
    "",
    f"- 2021-23 wage surge: max YoY {surge_max:.2f}% — PASS (BLS peak ~5.1% mid-2022; real, not an error).",
    f"- 2010s regime: YoY {dec.min():.2f}%..{dec.max():.2f}% — PASS (expected ~1.5-3%).",
    f"- QoQ declines in nominal comp index: {declines} (sticky-wage sanity).",
    f"- ECI x SPY usable overlap: {overlap.index.min().date()} .. {overlap.index.max().date()} ({len(overlap)} quarters).",
    f"- QoQ outliers (|z|>4): {len(outliers)} flagged (not removed): "
    + (", ".join(f"{d.date()} ({v:+.2f}%)" for d, v in outliers.items()) or "none"),
]
mv_path = os.path.join(DATA_DIR, f"missing_value_report_eci_total_comp_spy_{DATE_TAG}.md")
with open(mv_path, "w") as f:
    f.write("\n".join(mv_lines) + "\n")
print(f"  Missing value report -> {mv_path}")

# ---------------------------------------------------------------------------
# Stage 5: interpretation_metadata.json (Dana fields; provisional seeds noted)
# ---------------------------------------------------------------------------
meta = {
    "pair_id": PAIR_ID,
    "schema_version": "1.1.0",
    "indicator": "eci_total_comp",
    "target": "spy",
    "indicator_nature": "lagging",
    "indicator_type": "macro",
    "strategy_objective": "max_sharpe",
    "expected_direction": "countercyclical",
    "data_provenance": {
        "source": "FRED (BLS — Employment Cost Index: Total compensation: All Civilian, SA)",
        "series_id": ECI_SERIES,
        "accessed_at": NOW_ISO,
    },
    "known_stress_episodes": [
        {"label": "GFC wage deceleration", "start": "2008-09-30",
         "end": "2010-12-31",
         "note": "Total-compensation growth decelerated sharply after the GFC as labor markets slackened; YoY fell toward ~1.4%."},
        {"label": "2021-23 wage-inflation surge", "start": "2021-06-30",
         "end": "2023-12-31",
         "note": "Post-COVID labor shortage drove ECI YoY to ~5.1% (mid-2022) — the key wage-price-spiral scare feeding Fed tightening; real, not a data error."},
    ],
    "related_pair_ids": ["m2sl_yoy_spy", "indpro_spy"],
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
design = f"""# Design Note — eci_total_comp_spy ({DATE_TAG})

## FIRST QUARTERLY PAIR — deliberate template adaptations
All 15 prior pairs are monthly or daily. This dataset is designed on a NATIVE
QUARTERLY (quarter-end, QE-DEC) index — the monthly template was adapted, not
copied:

| Monthly convention | Quarterly adaptation here |
|---|---|
| spy_fwd_1m / _3m / _6m / _12m | `spy_fwd_1q` (~3M) / `spy_fwd_2q` (~6M) / `spy_fwd_4q` (~12M) |
| 60M rolling z-score windows | **20Q** (~5yr) windows, named `_zscore_20q` (quarter-count names, never "60m") |
| 12M trend MA | **8Q** (~2yr) MA (`_ma8q_idx`) |
| MoM / 3M / 6M momentum | QoQ (`_pct_qoq`) / 2Q (`_pct_2q`) / 4Q=YoY (`_pct_yoy`) |
| Lead grid L in months | **Lead grid L in QUARTERS; floor at L1** (pub lag, below) |

## Hypothesis (one-liner)
Does wage-inflation momentum (ECI total compensation growth) carry forward
information about SPY returns? Prior: COUNTERCYCLICAL — accelerating
compensation growth = wage-inflation pressure = tighter Fed / margin
compression = risk-off; decelerating ECI = disinflation = risk-on. ECI is a
classic LAGGING indicator (labor costs turn after the cycle). Direction and
lead-lag determined EMPIRICALLY by Evan; this note only seeds a provisional prior.

## Source & sample
- Indicator: FRED `{ECI_SERIES}` — Employment Cost Index: Total compensation:
  All Civilian. **Quarterly**, index Dec 2005 = 100, **SEASONALLY ADJUSTED**.
- History: **2001-Q1 to {df.index.max().date()}** ({len(df)} quarters, ~25 years).
  Good cycle coverage (2001 recession, GFC, COVID, 2021-23 wage surge) but FEW
  observations.
- Variant note: Data Master's `ECI` sheet / Pre-master entries are the **NSA
  private-industry** ECI variants (Dec 2015 = 100) — a different variant. This
  pair uses the SA all-civilian headline series per the pair brief.
- Target: SPY quarter-end (Yahoo, auto-adjusted); controls UNRATE/DGS10/DFF
  (FRED), ^VIX (Yahoo), all quarter-end snapshots. Usable overlap = full ECI
  window: **{overlap.index.min().date()} .. {overlap.index.max().date()} ({len(overlap)} quarters)**.

## Seasonality
Source is SA: QoQ and short-horizon transforms are seasonally CLEAN. No
NSA-contamination constraint (unlike Cass Freight). No transform-family
restriction on those grounds.

## Effective sample per transform (honesty table — few obs at quarterly freq)
""" + "\n".join(
    f"- `{col}`: {eff[col][2]} obs (starts {eff[col][1].date()})"
    for col in df.columns if col.startswith("eci_total_comp")
) + f"""

## Stationarity (ADF/KPSS — see stationarity_tests_{DATE_TAG}.csv)
Level is non-stationary (trending nominal index). Growth transforms: note the
YoY series is highly persistent at quarterly frequency (slow-moving wage
inflation) — check the CSV; some growth transforms may be borderline.
Acceleration and deviation-from-trend are the cleanly stationary candidates.
Evan confirms rather than re-runs (SOP).

## No-lookahead / publication lag (CRITICAL for Evan)
BLS releases quarter Q's ECI ~1 month after quarter end (end of Jan/Apr/Jul/Oct).
At quarterly granularity the quarter-Q signal is first tradable in Q+1:
**tournament lead grid must floor at L1, with L measured in QUARTERS**
(L1 = 1 quarter ≈ 3 months; L2 ≈ 6 months; L4 ≈ 12 months). Horizon mapping
for tournament targets: `spy_fwd_1q` ≈ monthly pairs' 3M horizon, `spy_fwd_2q`
≈ 6M, `spy_fwd_4q` ≈ 12M.

## Key data-quality flags for downstream
1. **Few observations**: {len(df)} quarters total; 20Q z-scores start ~2003-Q4/2004-Q4;
   any OOS window contains few quarters — OOS statistics high-variance. Use a
   conservative split and simple specifications; avoid dense parameter grids.
2. **2021-22 wage surge is REAL** (YoY peak {surge_max:.2f}%) — do not treat as outlier.
3. **YoY persistence**: wage inflation is slow-moving; expect strong
   autocorrelation in `_pct_yoy` — pre-whitening matters for CCF/Granger.
4. **Nominal stickiness**: the level almost never declines; level-based
   contraction flags are uninformative (none included).

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
     "source": "FRED:ECIALLCIV (Employment Cost Index Total Compensation, quarterly, SA) + FRED:UNRATE/DGS10/DFF + yahoo:SPY/^VIX",
     "refresh_ttl_days": 92,
     "schema_ref": os.path.relpath(sidecar_path, BASE_DIR),
     "last_updated": datetime.now().strftime("%Y-%m-%d"),
     "pairs": [PAIR_ID],
     "mixed_freq_ttl_note": "Quarterly indicator + quarter-end snapshots of daily market "
                            "data; TTL=92 days (quarterly cadence governs; ECI released "
                            "~1 month after quarter end)."},
    {"path": os.path.relpath(latest_path, BASE_DIR),
     "source": f"alias_of:{os.path.relpath(parquet_path, BASE_DIR)}",
     "refresh_ttl_days": 92,
     "schema_ref": os.path.relpath(sidecar_path, BASE_DIR),
     "last_updated": datetime.now().strftime("%Y-%m-%d"),
     "pairs": [PAIR_ID]},
]
manifest[key] = entries
manifest["generated_at"] = NOW_ISO
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"  Manifest updated -> {manifest_path}")

print("\nDONE — data stage complete for eci_total_comp_spy (first quarterly pair).")
