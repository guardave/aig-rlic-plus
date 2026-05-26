#!/usr/bin/env python3
"""
Data Pipeline: Gold/Copper Ratio -> Industrials (XLI)
=====================================================

Pair: gold_copper_xli
Indicator category: commodity_ratio (new — first pair in this bucket)
Mode 2 build (LEAD-WM1): Lead-as-maker, single-session Dana phase.

Indicator hypothesis. Gold/copper ratio is a real-asset risk-on/risk-off
proxy. Copper is the bellwether industrial input ("Doctor Copper");
gold is the canonical flight asset. A rising ratio (gold up vs copper)
signals growth fears + safe-haven demand. Industrials (XLI) are the
most direct equity expression of industrial-cycle exposure, so the
hypothesized lead-lag is: rising gold/copper -> XLI underperformance.

Symbol selection rationale.
- Gold: GC=F (CME Gold futures continuous). Liquid, 24h, history to 2000.
  Cross-check column gold_etf=GLD (SPDR Gold Trust) for ETF-tracked retail proxy.
- Copper: HG=F (CME Copper futures continuous). Most-cited "Doctor Copper".
  Cross-check column copper_etf=CPER (US Copper Index Fund) — limited
  pre-2011 history.
- Target: XLI (Industrial Select Sector SPDR). Inception 1998-12-22 —
  defines sample start.

Sample. 2000-01-01 -> 2025-12-31. IS=2000-01-01..2019-12-31,
OOS=2020-01-01..2025-12-31. ~25 yr, ~6 yr OOS.

Outputs.
- data/gold_copper_xli_daily_<DATE_TAG>.parquet
- data/gold_copper_xli_daily_schema.json
- data/data_dictionary_gold_copper_xli_<DATE_TAG>.csv
- data/missing_value_report_gold_copper_xli_<DATE_TAG>.md
- data/summary_stats_gold_copper_xli_<DATE_TAG>.csv
- results/gold_copper_xli/interpretation_metadata.json
"""

import os, sys, json, warnings, time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------
PAIR_ID = "gold_copper_xli"
INDICATOR_NAME = "Gold/Copper Ratio"
TARGET_NAME = "Industrials (XLI)"
START_DATE = "2000-01-01"
END_DATE = "2025-12-31"
IS_END = "2019-12-31"
OOS_START = "2020-01-01"
DATE_TAG = "20260526"
SCHEMA_VERSION = "1.0.0"
INDICATOR_CATEGORY = "commodity_ratio"

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
for d in [DATA_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

PARQUET_PATH = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_{DATE_TAG}.parquet")
SCHEMA_PATH = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_schema.json")
DICT_PATH = os.path.join(DATA_DIR, f"data_dictionary_{PAIR_ID}_{DATE_TAG}.csv")
MISSING_PATH = os.path.join(DATA_DIR, f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md")
SUMMARY_PATH = os.path.join(DATA_DIR, f"summary_stats_{PAIR_ID}_{DATE_TAG}.csv")
INTERP_PATH = os.path.join(RESULTS_DIR, "interpretation_metadata.json")


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------------
# Stage 1: ingest
# ------------------------------------------------------------------
def stage_ingest():
    import yfinance as yf
    log("Stage 1: ingest")
    tickers = {
        "GC=F": "gold",
        "HG=F": "copper",
        "GLD": "gold_etf",
        "CPER": "copper_etf",
        "XLI": "xli",
        "SPY": "spy",
        "^VIX": "vix",
        "DX-Y.NYB": "dxy",
    }
    out = {}
    for ticker, name in tickers.items():
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE,
                             progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            s = df["Close"].astype(float)
            s.index = s.index.tz_localize(None) if s.index.tz else s.index
            out[name] = s
            log(f"  {ticker:12s} -> {name:12s}  n={len(s):5d}  "
                f"first={s.index[0].date()}  last={s.index[-1].date()}")
        except Exception as e:
            log(f"  {ticker} FAILED: {e}")
            out[name] = pd.Series(dtype=float)
    return out


# ------------------------------------------------------------------
# Stage 2: align to business-day index + derive signals
# ------------------------------------------------------------------
def stage_align_and_derive(raw):
    log("Stage 2: align + derive")
    bdays = pd.bdate_range(START_DATE, END_DATE)
    df = pd.DataFrame(index=bdays)
    df.index.name = "date"

    for col, s in raw.items():
        df[col] = s.reindex(bdays).ffill(limit=5)

    # Primary indicator: gold/copper ratio
    df["gold_copper_ratio"] = df["gold"] / df["copper"]
    df["gold_copper_ratio_etf"] = df["gold_etf"] / df["copper_etf"]  # cross-check

    # Log-ratio (better-distributed)
    df["gold_copper_logratio"] = np.log(df["gold_copper_ratio"])

    # Z-score windows
    r = df["gold_copper_ratio"]
    for window in [126, 252, 504]:
        mn = r.rolling(window, min_periods=int(window * 0.8)).mean()
        sd = r.rolling(window, min_periods=int(window * 0.8)).std()
        df[f"gold_copper_zscore_{window}d"] = (r - mn) / sd

    # Percentile rank
    for window in [504, 1260]:
        df[f"gold_copper_pctrank_{window}d"] = r.rolling(
            window, min_periods=int(window * 0.8)
        ).apply(lambda x: (x.rank().iloc[-1] - 1) / (len(x) - 1), raw=False)

    # Rate of change
    for n in [5, 21, 63, 126]:
        df[f"gold_copper_roc_{n}d"] = (r / r.shift(n) - 1.0) * 100.0

    # Momentum (level diff)
    for n in [21, 63, 252]:
        df[f"gold_copper_mom_{n}d"] = r - r.shift(n)

    # Acceleration
    df["gold_copper_acceleration"] = (
        df["gold_copper_roc_21d"] - df["gold_copper_roc_21d"].shift(21)
    )

    # Realized vol of ratio changes
    df["gold_copper_realized_vol_21d"] = (
        df["gold_copper_ratio"].pct_change().rolling(21, min_periods=15).std()
        * np.sqrt(252)
    )

    # Target returns (XLI primary; SPY for cross-check)
    for label, col in [("xli", "xli"), ("spy", "spy")]:
        df[f"{label}_ret"] = df[col].pct_change()
        for n in [1, 5, 21, 63, 126, 252]:
            df[f"{label}_fwd_{n}d"] = df[col].shift(-n) / df[col] - 1.0

    log(f"  rows={len(df)}  cols={len(df.columns)}")
    return df


# ------------------------------------------------------------------
# Stage 3: persist parquet
# ------------------------------------------------------------------
def stage_persist(df):
    log("Stage 3: persist parquet")
    df.to_parquet(PARQUET_PATH, engine="pyarrow", compression="snappy")
    log(f"  wrote {PARQUET_PATH}  ({os.path.getsize(PARQUET_PATH)/1024:.1f} KB)")


# ------------------------------------------------------------------
# Stage 4: schema + dictionary + reports
# ------------------------------------------------------------------
COLUMN_META = {
    "date": ("datetime64[ns]", "date", "Date", "neutral",
             "Daily trading-date index (parquet index column). NYSE business "
             "calendar; spans 2000-01-03 through 2025-12-31."),
    "gold": ("float64", "price", "Gold Futures ($/oz)", "neutral",
             "CME Gold continuous front-month futures close, USD per troy ounce.",
             "yahoo:GC=F"),
    "copper": ("float64", "price", "Copper Futures ($/lb)", "higher_is_better",
               "CME Copper continuous front-month futures close, USD per pound. "
               "Higher = stronger industrial demand.",
               "yahoo:HG=F"),
    "gold_etf": ("float64", "price", "GLD Close ($)", "neutral",
                 "SPDR Gold Trust adjusted close — ETF cross-check for gold price.",
                 "yahoo:GLD"),
    "copper_etf": ("float64", "price", "CPER Close ($)", "higher_is_better",
                   "US Copper Index Fund adjusted close — ETF cross-check for copper. "
                   "Limited pre-2011 history.",
                   "yahoo:CPER"),
    "xli": ("float64", "price", "XLI Close ($)", "higher_is_better",
            "Industrial Select Sector SPDR ETF adjusted close. Target asset.",
            "yahoo:XLI"),
    "spy": ("float64", "price", "SPY Close ($)", "higher_is_better",
            "SPDR S&P 500 ETF adjusted close, cross-check target.",
            "yahoo:SPY"),
    "vix": ("float64", "index", "VIX Index Level", "lower_is_better",
            "CBOE Volatility Index, regime overlay.",
            "yahoo:^VIX"),
    "dxy": ("float64", "index", "DXY Dollar Index", "neutral",
            "ICE US Dollar Index — USD vs basket of 6 currencies. Strong "
            "USD typically pressures both gold and copper prices.",
            "yahoo:DX-Y.NYB"),
    "gold_copper_ratio": ("float64", "ratio", "Gold/Copper Ratio", "lower_is_better",
                          "Primary indicator. gold ($/oz) / copper ($/lb). Higher = "
                          "risk-off (gold up vs copper down). Dimensionless after "
                          "the unit cancellation by ratio convention.",
                          "derived: gold / copper"),
    "gold_copper_ratio_etf": ("float64", "ratio", "Gold/Copper Ratio (ETF)",
                              "lower_is_better",
                              "ETF cross-check: GLD/CPER. Useful for post-2011 "
                              "consistency check against futures-based ratio.",
                              "derived: gold_etf / copper_etf"),
    "gold_copper_logratio": ("float64", "ratio", "Gold/Copper Log-Ratio",
                             "lower_is_better",
                             "Natural log of gold_copper_ratio. Better-distributed "
                             "for stationarity and modeling.",
                             "derived: log(gold_copper_ratio)"),
}

# Derived columns produced programmatically — generate metadata too.
for w in [126, 252, 504]:
    COLUMN_META[f"gold_copper_zscore_{w}d"] = (
        "float64", "ratio", f"G/C Z-Score ({w}d)", "lower_is_better",
        f"Standardized gold_copper_ratio vs trailing {w}-day rolling mean/std. "
        "Higher z = ratio elevated vs recent history = risk-off.",
        f"derived: (ratio - rollmean_{w}) / rollstd_{w}",
    )
for w in [504, 1260]:
    COLUMN_META[f"gold_copper_pctrank_{w}d"] = (
        "float64", "ratio", f"G/C %-Rank ({w}d)", "lower_is_better",
        f"Percentile rank (0-1) of ratio within trailing {w}-day window.",
        f"derived: percentile_rank(ratio, window={w})",
    )
for n in [5, 21, 63, 126]:
    COLUMN_META[f"gold_copper_roc_{n}d"] = (
        "float64", "percent", f"G/C {n}d Rate-of-Change (%)", "lower_is_better",
        f"{n}-trading-day percent-change of gold_copper_ratio. Positive = "
        "ratio rising = increasing risk-off.",
        f"derived: (ratio[t] / ratio[t-{n}] - 1) * 100",
    )
for n in [21, 63, 252]:
    COLUMN_META[f"gold_copper_mom_{n}d"] = (
        "float64", "ratio", f"G/C {n}d Momentum (level diff)", "lower_is_better",
        f"{n}-trading-day level difference of gold_copper_ratio.",
        f"derived: ratio[t] - ratio[t-{n}]",
    )
COLUMN_META["gold_copper_acceleration"] = (
    "float64", "percent", "G/C Acceleration", "lower_is_better",
    "Change in 21d rate-of-change (second-difference proxy). Captures "
    "inflection in the ratio trajectory.",
    "derived: roc_21d[t] - roc_21d[t-21]",
)
COLUMN_META["gold_copper_realized_vol_21d"] = (
    "float64", "ratio", "G/C Realized Vol (21d, ann.)", "lower_is_better",
    "21-day annualized realized vol of daily ratio percent-changes. "
    "Decimal (0.30 = 30% annualized).",
    "derived: std(pct_change(ratio), 21) * sqrt(252)",
)

# Returns metadata
for label, asset in [("xli", "XLI"), ("spy", "SPY")]:
    COLUMN_META[f"{label}_ret"] = (
        "float64", "decimal_return", f"{asset} Daily Return", "higher_is_better",
        f"1-day percent return of {asset} as decimal.",
        f"derived: {label}[t] / {label}[t-1] - 1",
    )
    for n in [1, 5, 21, 63, 126, 252]:
        COLUMN_META[f"{label}_fwd_{n}d"] = (
            "float64", "decimal_return", f"{asset} {n}d Forward Return",
            "higher_is_better",
            f"Forward {n}-trading-day total return of {asset} (decimal).",
            f"derived: {label}[t+{n}] / {label}[t] - 1",
        )


def stage_metadata(df):
    log("Stage 4: schema + dictionary + reports")

    # Schema JSON
    columns = {}
    for col in ["date"] + [c for c in df.columns if c != "date"]:
        meta = COLUMN_META.get(col)
        if meta is None:
            log(f"  WARN: no metadata registered for column {col}")
            continue
        if len(meta) == 5:
            dtype, unit, disp, direction, desc = meta
            src = None
        else:
            dtype, unit, disp, direction, desc, src = meta
        entry = {
            "dtype": dtype,
            "unit": unit,
            "display_name": disp,
            "direction": direction,
            "description": desc,
        }
        if src:
            entry["source_reference"] = src
            entry["refresh_ttl_days"] = 1
        columns[col] = entry

    schema = {
        "pair_id": PAIR_ID,
        "parquet_path": f"data/{os.path.basename(PARQUET_PATH)}",
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "columns": columns,
    }
    with open(SCHEMA_PATH, "w") as f:
        json.dump(schema, f, indent=2)
    log(f"  wrote {SCHEMA_PATH}")

    # Data dictionary CSV
    rows = []
    for col, entry in columns.items():
        rows.append({
            "column": col,
            "dtype": entry["dtype"],
            "unit": entry["unit"],
            "display_name": entry["display_name"],
            "direction": entry["direction"],
            "source": entry.get("source_reference", "derived"),
            "description": entry["description"],
        })
    pd.DataFrame(rows).to_csv(DICT_PATH, index=False)
    log(f"  wrote {DICT_PATH}")

    # Missing value report
    miss = df.isna().sum()
    pct = (miss / len(df) * 100).round(2)
    with open(MISSING_PATH, "w") as f:
        f.write(f"# Missing Value Report — {PAIR_ID}\n\n")
        f.write(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write(f"Rows: {len(df)}  Cols: {len(df.columns)}\n\n")
        f.write("| Column | n_missing | pct_missing |\n|---|---:|---:|\n")
        for c in df.columns:
            f.write(f"| {c} | {int(miss[c])} | {pct[c]:.2f}% |\n")
        f.write("\n## Notes\n\n")
        f.write("- `copper_etf` (CPER) inception 2011-11; expect ~30% missing across full sample. Used only as ETF cross-check after 2011.\n")
        f.write("- All other primary columns are forward-filled up to 5 business days for cross-asset alignment.\n")
        f.write("- Rolling window columns (zscore_*, pctrank_*, roc_*, mom_*, realized_vol_*) have leading missings equal to their lookback window.\n")
        f.write("- Forward-return columns (*_fwd_*) have trailing missings equal to their horizon.\n")
    log(f"  wrote {MISSING_PATH}")

    # Summary stats CSV
    df.describe().T.to_csv(SUMMARY_PATH)
    log(f"  wrote {SUMMARY_PATH}")

    return schema


# ------------------------------------------------------------------
# Stage 5: interpretation_metadata.json
# ------------------------------------------------------------------
def stage_interpretation(df):
    log("Stage 5: interpretation_metadata.json")

    # Quick directional check (provisional — Evan will finalize)
    sub = df.dropna(subset=["gold_copper_zscore_252d", "xli_fwd_63d"])
    corr_provisional = sub["gold_copper_zscore_252d"].corr(sub["xli_fwd_63d"])
    log(f"  provisional corr(z_252d, xli_fwd_63d) = {corr_provisional:+.3f}  (Evan finalizes)")

    interp = {
        "pair_id": PAIR_ID,
        "schema_version": SCHEMA_VERSION,
        "indicator": "gold_copper_ratio",
        "indicator_display": INDICATOR_NAME,
        "target": "xli",
        "target_symbol": "XLI",
        "target_display": TARGET_NAME,
        "indicator_nature": "coincident",
        "indicator_type": INDICATOR_CATEGORY,
        "indicator_category": INDICATOR_CATEGORY,
        "strategy_objective": "max_sharpe",
        "expected_direction": "countercyclical",
        "observed_direction_provisional": (
            "countercyclical" if corr_provisional < 0 else "procyclical"
        ),
        "observed_direction": None,
        "direction_consistent": None,
        "mechanism": (
            "Gold/copper ratio is a real-asset risk-on/risk-off gauge. Copper "
            "tracks industrial demand (\"Doctor Copper\"); gold is the canonical "
            "flight asset. A rising ratio signals growth fears plus safe-haven "
            "demand. Industrials (XLI) are the most direct equity expression of "
            "industrial-cycle exposure, so the hypothesized link is: rising "
            "gold/copper -> XLI underperformance on a several-month horizon."
        ),
        "confidence": "provisional",
        "key_finding": "[Evan: tournament not yet run]",
        "caveats": [
            "Both gold and copper are USD-priced; DXY co-movement can confound the ratio.",
            "Copper futures (HG=F) reflect global industrial activity; XLI is US-focused — basis risk on geography.",
            "Ratio is bounded below by zero but has no upper bound; log-ratio (gold_copper_logratio) is the better-distributed transform.",
            "CPER ETF inception 2011 limits ETF-based cross-check to post-2011.",
            "Commodity ratios can decouple from equity risk-off when one leg is driven by supply (e.g. 2022 copper held on supply tightness).",
        ],
        "owner_writes": {
            "dana": [
                "pair_id", "schema_version",
                "indicator", "indicator_display",
                "target", "target_symbol", "target_display",
                "indicator_nature", "indicator_type", "indicator_category",
                "strategy_objective", "expected_direction",
                "observed_direction_provisional",
                "mechanism", "caveats",
            ],
            "evan": [
                "observed_direction", "direction_consistent",
                "key_finding", "confidence",
            ],
        },
        "sample": {
            "start": START_DATE,
            "end": END_DATE,
            "is_end": IS_END,
            "oos_start": OOS_START,
            "rows": int(len(df)),
            "cols": int(len(df.columns)),
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "Lead Lesandro (Mode 2 maker — Dana hat)",
    }
    with open(INTERP_PATH, "w") as f:
        json.dump(interp, f, indent=2)
    log(f"  wrote {INTERP_PATH}")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    t0 = time.time()
    raw = stage_ingest()
    df = stage_align_and_derive(raw)
    stage_persist(df)
    stage_metadata(df)
    stage_interpretation(df)
    log(f"\nDONE in {time.time()-t0:.1f}s")
    log(f"  parquet: {PARQUET_PATH}")
    log(f"  schema:  {SCHEMA_PATH}")
    log(f"  dict:    {DICT_PATH}")
    log(f"  missing: {MISSING_PATH}")
    log(f"  summary: {SUMMARY_PATH}")
    log(f"  interp:  {INTERP_PATH}")


if __name__ == "__main__":
    main()
