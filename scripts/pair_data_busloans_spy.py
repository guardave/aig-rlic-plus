#!/usr/bin/env python3
"""
Data Stage: Commercial & Industrial Loans (BUSLOANS) x SPY
==========================================================
Priority pair #19 (I20 x SPY). Mode 1, branch fix260612_busloans_spy.

Dana-owned stage 1 of the pipeline (Dana -> Evan -> Vera+Ray -> Ace -> Quincy).

Deliverables:
  - data/busloans_spy_monthly_{start}_{end}.parquet  (+ _latest alias)
  - data/busloans_spy_monthly_schema.json            (DATA-D5 sidecar)
  - data/data_dictionary_busloans_spy_{tag}.csv
  - data/summary_stats_busloans_spy_{tag}.csv
  - data/missing_value_report_busloans_spy_{tag}.md
  - results/busloans_spy/stationarity_tests_{tag}.csv
  - results/busloans_spy/interpretation_metadata.json
  - data/display_name_registry.csv rows + data/manifest.json entry (DATA-D13)

IMPORTANT (LEAD-DV1): BUSLOANS (FRED, stock of C&I loans outstanding, $bn, SA,
monthly) is NOT the Data Master "C&I Loan" column, which is the SLOOS Net %
of Banks Tightening Standards for C&I Loans to Small Firms (quarterly survey).
The two stay distinct indicator_ids (busloans vs ci_loan).

Direction prior (for Evan): AMBIGUOUS-TO-LAGGING. C&I loans are a component
of the Conference Board LAGGING Economic Index. Firms draw credit lines INTO
downturns (March-April 2020: ~+25-30% YoY spike from credit-line drawdowns);
loan growth often peaks after recessions begin. Naive "rising loans = bullish"
may invert at turning points. Direction must be determined empirically.

Author: Data Dana (Data Agent)
Date: 2026-06-12
Pair ID: busloans_spy
"""

import json
import os
import sys
import warnings
from datetime import datetime, timezone

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

np.random.seed(42)  # no sampling occurs; seed set per SOP anyway

PAIR_ID = "busloans_spy"
START_DATE = "1947-01-01"   # full BUSLOANS history
END_DATE = "2026-05-31"
DATE_TAG = "20260612"

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
    pair_pipeline_indpro_spy.py; direct API used because fredapi rejected the
    key string in this environment and fredgraph.csv 504'd (flaky)."""
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
    df = yf.download(ticker, start=START_DATE, end=END_DATE,
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
busloans = fetch_fred("BUSLOANS", "busloans_usd")
unrate = fetch_fred("UNRATE", "unrate")
dgs10 = fetch_fred("DGS10", "dgs10")
fed_funds = fetch_fred("DFF", "fed_funds", start="1954-07-01")
spy = fetch_yahoo("SPY", "spy")
vix = fetch_yahoo("^VIX", "vix")

# ---------------------------------------------------------------------------
# Stage 2: Alignment + derived series (month-end, mirrors indpro_spy)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 2: ALIGNMENT + DERIVED SERIES")
print("=" * 70)

idx = pd.date_range(busloans.index.min(), END_DATE, freq="ME")
df = pd.DataFrame(index=idx)
df.index.name = "date"

# BUSLOANS is stamped at month-start by FRED; value is the monthly average for
# that month. Align to month-end of the SAME month (resample 'ME' last).
df["busloans_usd"] = busloans.resample("ME").last().reindex(idx)
df["unrate"] = unrate.resample("ME").last().reindex(idx)
df["dgs10"] = dgs10.resample("ME").last().reindex(idx)
df["fed_funds"] = fed_funds.resample("ME").last().reindex(idx)
df["vix"] = vix.resample("ME").last().reindex(idx)
df["spy"] = spy.resample("ME").last().reindex(idx)

b = df["busloans_usd"]
df["busloans_pct_yoy"] = (b / b.shift(12) - 1) * 100
df["busloans_pct_mom"] = (b / b.shift(1) - 1) * 100
df["busloans_3m_pct"] = (b / b.shift(3) - 1) * 100      # 3M momentum, % chg
df["busloans_6m_pct"] = (b / b.shift(6) - 1) * 100      # 6M momentum, % chg
df["busloans_ma12_usd"] = b.rolling(12, min_periods=10).mean()
df["busloans_dev_trend_pct"] = (b / df["busloans_ma12_usd"] - 1) * 100
rm60 = b.rolling(60, min_periods=36)
df["busloans_zscore_60m"] = (b - rm60.mean()) / rm60.std()
ryoy = df["busloans_pct_yoy"].rolling(60, min_periods=36)
df["busloans_yoy_zscore_60m"] = (df["busloans_pct_yoy"] - ryoy.mean()) / ryoy.std()
df["busloans_accel_pct"] = df["busloans_pct_mom"].diff()  # MoM accel, pp
df["busloans_contraction"] = (df["busloans_pct_yoy"] < 0).astype(float)

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

# COVID-spike sanity check (Defense 2): March-April 2020 C&I credit-line drawdowns
covid = df.loc["2020-03-31":"2020-05-31", ["busloans_usd", "busloans_pct_yoy", "busloans_pct_mom"]]
print("\n  COVID-era sanity check (expect YoY spiking toward ~+25-30% by Apr/May 2020):")
print(covid.round(2).to_string())
covid_peak_yoy = df.loc["2020-04-30":"2020-06-30", "busloans_pct_yoy"].max()
assert covid_peak_yoy > 15, f"COVID spike MISSING: peak YoY {covid_peak_yoy:.1f}% — wrong series?"
print(f"  PASS: COVID peak YoY = {covid_peak_yoy:.1f}%")

# GFC sanity: YoY should go negative in 2009-2010 (post-recession contraction = lagging)
gfc_min_yoy = df.loc["2009-01-31":"2010-12-31", "busloans_pct_yoy"].min()
print(f"  GFC check: min YoY 2009-2010 = {gfc_min_yoy:.1f}% (expect strongly negative)")
assert gfc_min_yoy < -10, "GFC contraction missing"

# Units sanity: level should be ~$2,000-3,000bn in mid-2020s
recent_level = df["busloans_usd"].dropna().iloc[-1]
print(f"  Latest level: ${recent_level:,.0f}bn as of {df['busloans_usd'].dropna().index[-1].date()}")
assert 1500 < recent_level < 5000, "level not in billions-USD range"

# Gap check on indicator: no internal NaN gaps
b_valid = df["busloans_usd"].dropna()
internal_gaps = df.loc[b_valid.index.min():b_valid.index.max(), "busloans_usd"].isna().sum()
print(f"  Internal gaps in busloans_usd: {internal_gaps}")
assert internal_gaps == 0, "silent gaps in BUSLOANS"

# Outlier flagging (z>4 on MoM) — flag, do not remove
mom = df["busloans_pct_mom"].dropna()
z = (mom - mom.mean()) / mom.std()
outliers = mom[abs(z) > 4]
print(f"  MoM outliers (|z|>4): {len(outliers)}")
for d, v in outliers.items():
    print(f"    {d.date()}: {v:+.2f}%")

# Stationarity tests
from arch.unitroot import ADF, KPSS
from dotenv import load_dotenv
test_cols = ["busloans_usd", "busloans_pct_yoy", "busloans_pct_mom",
             "busloans_3m_pct", "busloans_6m_pct", "busloans_zscore_60m",
             "busloans_yoy_zscore_60m", "busloans_dev_trend_pct", "spy_ret"]
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
parquet_path = os.path.join(DATA_DIR, f"busloans_spy_monthly_{start_tag}_{end_tag}.parquet")
latest_path = os.path.join(DATA_DIR, "busloans_spy_monthly_latest.parquet")
df.to_parquet(parquet_path)
df.to_parquet(latest_path)
print(f"  Parquet -> {parquet_path}")
print(f"  Alias   -> {latest_path}")

# Column metadata (single source for sidecar + dictionary + registry)
COLS = {
    "busloans_usd": dict(unit="usd", display_name="C&I Loans Outstanding ($bn)",
        direction="neutral",
        axis_label="C&I Loans ($bn)",
        desc="FRED BUSLOANS: Commercial & Industrial loans, all commercial banks. "
             "Monthly average of weekly H.8 data, billions of USD, seasonally adjusted. "
             "Level series, strongly trending."),
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
        desc="SPY adjusted close, month-end (Yahoo, auto-adjusted). Target asset. "
             "Starts 1993-01; NaN before inception."),
    "busloans_pct_yoy": dict(unit="pct", display_name="C&I Loans YoY (%)",
        direction="neutral", axis_label="C&I Loans YoY (%)",
        desc="12-month percent change in busloans_usd. Effective start = series start + 12m."),
    "busloans_pct_mom": dict(unit="pct", display_name="C&I Loans MoM (%)",
        direction="neutral", axis_label="C&I Loans MoM (%)",
        desc="1-month percent change in busloans_usd."),
    "busloans_3m_pct": dict(unit="pct", display_name="C&I Loans 3M Change (%)",
        direction="neutral", axis_label="C&I Loans 3M (%)",
        desc="3-month percent change (momentum) in busloans_usd."),
    "busloans_6m_pct": dict(unit="pct", display_name="C&I Loans 6M Change (%)",
        direction="neutral", axis_label="C&I Loans 6M (%)",
        desc="6-month percent change (momentum) in busloans_usd."),
    "busloans_ma12_usd": dict(unit="usd", display_name="C&I Loans 12M MA ($bn)",
        direction="neutral", axis_label="C&I Loans 12M MA ($bn)",
        desc="12-month rolling mean of busloans_usd (min 10 obs)."),
    "busloans_dev_trend_pct": dict(unit="pct", display_name="C&I Loans Deviation from 12M Trend (%)",
        direction="neutral", axis_label="Dev. from 12M MA (%)",
        desc="Percent deviation of busloans_usd from its 12-month moving average."),
    "busloans_zscore_60m": dict(unit="none", display_name="C&I Loans 60M Z-Score",
        direction="neutral", axis_label="Z-score (60M)",
        desc="Rolling 60-month z-score of the LEVEL (min 36 obs). Trending level means "
             "this is persistently positive; prefer YoY z-score for cycle signal."),
    "busloans_yoy_zscore_60m": dict(unit="none", display_name="C&I Loan Growth 60M Z-Score",
        direction="neutral", axis_label="YoY z-score (60M)",
        desc="Rolling 60-month z-score of busloans_pct_yoy (min 36 obs). Cycle-relevant "
             "standardization of loan growth."),
    "busloans_accel_pct": dict(unit="pct", display_name="C&I Loan Growth Acceleration (pp)",
        direction="neutral", axis_label="MoM accel. (pp)",
        desc="First difference of busloans_pct_mom (percentage points)."),
    "busloans_contraction": dict(unit="none", display_name="C&I Loan Contraction Flag",
        direction="lower_is_better", axis_label="Contraction (0/1)",
        desc="1.0 when busloans_pct_yoy < 0, else 0.0. Note: contractions occur AFTER "
             "recessions (lagging) — e.g. 2009-2010, 2021."),
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

# Cross-pair consistency (DATA-D13 / batch consistency rule): canonical column
# names already in the display-name registry keep their existing registry
# display_name/unit/axis_label verbatim. Note: registry's `spy_ret` is named
# "SPY Daily Return (decimal)"; in this monthly parquet it is a MONTHLY return —
# quirk documented in the data dictionary description (registry name retained).
reg_path = os.path.join(DATA_DIR, "display_name_registry.csv")
reg = pd.read_csv(reg_path)
_reg_idx = reg.set_index("column_name")
for c in COLS:
    if c in _reg_idx.index:
        COLS[c]["display_name"] = _reg_idx.loc[c, "display_name"]
        COLS[c]["unit"] = _reg_idx.loc[c, "unit"]
        COLS[c]["axis_label"] = _reg_idx.loc[c, "axis_label"]

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
        **{c: {"dtype": str(df[c].dtype), "unit": m["unit"],
               "display_name": m["display_name"], "direction": m["direction"],
               "description": m["desc"],
               "source_reference": ("FRED:BUSLOANS" if c.startswith("busloans") else
                                    "yahoo:SPY" if c.startswith("spy") else "see description")}
          for c, m in COLS.items()}
    },
}
sidecar_path = os.path.join(DATA_DIR, "busloans_spy_monthly_schema.json")
with open(sidecar_path, "w") as f:
    json.dump(sidecar, f, indent=2)
print(f"  Sidecar -> {sidecar_path}")

# Data dictionary (human form, CSV like prior pairs)
dd_rows = []
for c, m in COLS.items():
    dd_rows.append({
        "column_name": c, "display_name": m["display_name"],
        "description": m["desc"],
        "source": "FRED" if c.startswith(("busloans", "unrate", "dgs10", "fed_funds")) else "Yahoo Finance",
        "series_id": ("BUSLOANS" if c.startswith("busloans") else
                      {"unrate": "UNRATE", "dgs10": "DGS10", "fed_funds": "DFF",
                       "vix": "^VIX", "spy": "SPY"}.get(c, "derived")),
        "unit": m["unit"], "direction_convention": m["direction"],
        "seasonal_adj": "SA" if c.startswith("busloans") and not c.endswith(("zscore_60m", "contraction")) else "N/A",
        "effective_start": str(df[c].first_valid_index().date()),
        "refresh_freq": "monthly" if c.startswith(("busloans", "unrate")) else "daily",
        "known_quirks": ("H.8-derived; monthly value = average of weekly Wednesday levels; "
                         "published ~2-3 weeks after month-end; March-Apr 2020 credit-line "
                         "drawdown spike (+25-30% YoY); definitional breaks in H.8 panel over decades"
                         if c.startswith("busloans") else ""),
    })
dd_path = os.path.join(DATA_DIR, f"data_dictionary_busloans_spy_{DATE_TAG}.csv")
pd.DataFrame(dd_rows).to_csv(dd_path, index=False)
print(f"  Data dictionary -> {dd_path}")

# Summary stats
ss_path = os.path.join(DATA_DIR, f"summary_stats_busloans_spy_{DATE_TAG}.csv")
df.describe().T.round(4).to_csv(ss_path)
print(f"  Summary stats -> {ss_path}")

# Missing value report
mv_lines = [
    f"# Missing Value Report — busloans_spy ({DATE_TAG})",
    "",
    f"Dataset: `{os.path.relpath(parquet_path, BASE_DIR)}` — shape {df.shape}, "
    f"month-end index {df.index.min().date()} to {df.index.max().date()}.",
    "",
    "## Publication lag (BUSLOANS)",
    "",
    "BUSLOANS is derived from the Fed H.8 release (Assets and Liabilities of "
    "Commercial Banks, weekly, published each Friday with ~8-day lag). The monthly "
    "BUSLOANS observation is the average of weekly Wednesday levels and becomes "
    "available roughly 2-3 weeks after month-end. **Evan: lag the indicator by at "
    "least 1 month (L1) for real-time tradability; L1-L2 is the realistic floor.** "
    "H.8 data are also revised (benchmarked to Call Reports quarterly).",
    "",
    "## Missing values by column",
    "",
    "| Column | NaN count | Pattern |",
    "|---|---|---|",
]
for c in df.columns:
    n = int(df[c].isna().sum())
    fv = df[c].first_valid_index()
    pattern = (f"leading (series starts {fv.date()})" if n and fv is not None else "none")
    if c.startswith("spy_fwd") or c == "spy_ret":
        pattern += "; trailing NaN from forward shift" if c.startswith("spy_fwd") else ""
    mv_lines.append(f"| `{c}` | {n} | {pattern} |")
mv_lines += [
    "",
    "No internal gaps in `busloans_usd` (verified). No forward-fill applied to the "
    "indicator. SPY columns are NaN before SPY inception (1993-01); forward-return "
    "columns are NaN at the tail by construction (no leakage).",
    "",
    "## Sanity checks (Defense 2)",
    "",
    f"- COVID credit-line drawdown spike: peak YoY {covid_peak_yoy:.1f}% (Apr-Jun 2020) — PASS (expected ~+25-30%).",
    f"- GFC contraction: min YoY 2009-2010 = {gfc_min_yoy:.1f}% — PASS (lagging contraction confirmed).",
    f"- Units: latest level ${recent_level:,.0f}bn — consistent with billions-USD, SA.",
    f"- MoM outliers (|z|>4): {len(outliers)} flagged (not removed): "
    + ", ".join(f"{d.date()} ({v:+.1f}%)" for d, v in outliers.items()),
]
mv_path = os.path.join(DATA_DIR, f"missing_value_report_busloans_spy_{DATE_TAG}.md")
with open(mv_path, "w") as f:
    f.write("\n".join(mv_lines) + "\n")
print(f"  Missing value report -> {mv_path}")

# ---------------------------------------------------------------------------
# Stage 5: interpretation_metadata.json (Dana fields; provisional seeds noted)
# ---------------------------------------------------------------------------
meta = {
    "pair_id": PAIR_ID,
    "schema_version": "1.1.0",
    "indicator": "busloans",
    "target": "spy",
    "indicator_nature": "lagging",
    "indicator_type": "credit",
    "strategy_objective": "max_sharpe",
    "expected_direction": "mixed",
    "data_provenance": {
        "source": "FRED (H.8 Assets and Liabilities of Commercial Banks)",
        "series_id": "BUSLOANS",
        "accessed_at": NOW_ISO,
    },
    "known_stress_episodes": [
        {"label": "GFC post-recession C&I contraction", "start": "2009-01-01",
         "end": "2010-12-31",
         "note": "YoY loan growth bottomed deeply negative AFTER the recession ended — textbook lagging behavior."},
        {"label": "COVID credit-line drawdown spike", "start": "2020-03-01",
         "end": "2020-06-30",
         "note": "C&I loans spiked ~+25-30% YoY as firms drew revolvers INTO the downturn; rising loans coincided with crashing equities."},
    ],
    "related_pair_ids": ["hy_ig_spy", "indpro_spy"],
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
# Stage 6: DATA-D13 — display-name registry + manifest
# ---------------------------------------------------------------------------
reg = pd.read_csv(reg_path)
new_rows = []
for c, m in COLS.items():
    if c in set(reg["column_name"]):
        continue  # cross-pair consistency: existing canonical names keep existing entries
    new_rows.append({"column_name": c, "display_name": m["display_name"],
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
    if isinstance(reg_json, dict) and "entries" in reg_json:
        existing = {e["column_name"] for e in reg_json["entries"]}
        reg_json["entries"] += [r for r in new_rows if r["column_name"] not in existing]
        reg_json["generated_at"] = NOW_ISO
        with open(reg_json_path, "w") as f:
            json.dump(reg_json, f, indent=2)
        print(f"  Registry JSON view updated -> {reg_json_path}")

# Sidecar display_name must match registry verbatim — cross-validate
reg_map = dict(zip(reg["column_name"], reg["display_name"]))
for c in COLS:
    assert sidecar["columns"][c]["display_name"] == reg_map[c] or c not in reg_map, \
        f"display-name drift for {c}"

manifest_path = os.path.join(DATA_DIR, "manifest.json")
with open(manifest_path) as f:
    manifest = json.load(f)
key = "artifacts" if "artifacts" in manifest else "aliases"
entries = [e for e in manifest[key] if PAIR_ID not in e.get("path", "")]
entries += [
    {"path": os.path.relpath(parquet_path, BASE_DIR),
     "source": "FRED:BUSLOANS (H.8 monthly avg, SA, $bn) + FRED:UNRATE/DGS10/DFF + yahoo:SPY/^VIX",
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

print("\nDONE — data stage complete for busloans_spy.")
