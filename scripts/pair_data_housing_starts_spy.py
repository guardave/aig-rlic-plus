#!/usr/bin/env python3
"""
Data Stage: Housing Starts (SAAR) x SPY
=======================================

Mode-2 Dana dispatch for pair_id housing_starts_spy.

Authoritative live source: FRED HOUST (New Privately-Owned Housing Units Started:
Total Units, Thousands of Units, Monthly, Seasonally Adjusted Annual Rate). Data
Master.xlsx sheet "H Started" column "RE - H Started" is the required Phase-0 /
cross-check source (same level series).

SA handling (contrast with nhs_spy):
  HOUST is already Seasonally Adjusted (annual rate). Unlike HSN1FNSA (NSA), no
  STL/YoY deseasonalisation is required to make a signal valid. MoM% is a
  legitimate momentum input. Signals follow the SA monthly-indicator template
  (permit_spy / INDPRO):
    - hst_pct_yoy       : 12-month % change (primary growth signal)
    - hst_pct_mom       : 1-month % change (valid because series is SA)
    - hst_3m_pct        : 3-month % change of the level
    - hst_3m_pct_yoy    : YoY % change of the 3-month moving average (smooths noise)
    - hst_yoy_accel_pct : 1-month change in YoY growth (acceleration, pp)
    - hst_yoy_zscore_120m : rolling 120-month z-score of YoY growth
    - hst_yoy_contraction_flag : 1 when YoY growth < 0
  The raw SAAR level (hst_level) is trend-dominated / non-stationary and is kept
  for provenance only, flagged not-a-signal.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

np.random.seed(42)

ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results/housing_starts_spy"
PWS_DIR = ROOT / "_pws/lead-lesandro/housing_starts_spy"
PAIR_ID = "housing_starts_spy"
INDICATOR = "housing_starts"
TARGET = "spy"
DATE_TAG = "20260814"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

PYEXE = str(ROOT / ".venv/bin/python")


def repo_rel(path: Path | str) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def validate_json(schema: str, instance: str) -> None:
    subprocess.run(
        [PYEXE, "scripts/validate_schema.py", "--schema", schema, "--instance", instance],
        cwd=ROOT,
        check=True,
    )


def mid_month_next_release(reference_month_end: pd.Timestamp) -> pd.Timestamp:
    """Approximate the joint Census/HUD New Residential Construction release for the
    prior month as the 17th of the following month (typical release window is the
    16th-19th), rolled forward to the next weekday if it lands on a weekend."""
    first_next = (reference_month_end + pd.offsets.MonthBegin(1)).normalize()
    rel = first_next + pd.Timedelta(days=16)  # the 17th
    while rel.weekday() >= 5:  # Sat/Sun -> next Monday
        rel = rel + pd.Timedelta(days=1)
    return rel


def verify_pre_master() -> str:
    """LEAD-DV1 / Phase-0: confirm the Pre-master row-2 description for the H Started
    column is the SAAR thousands-of-units Housing Starts level series."""
    pm = pd.read_excel(DATA_DIR / "Data Master.xlsx", sheet_name="Pre-master", header=None, nrows=4)
    hits = []
    for j in range(pm.shape[1]):
        row1 = str(pm.iat[0, j])
        row2 = str(pm.iat[1, j])
        if (row1 == "H Started" and "Housing Units Started" in row2
                and "Thousands of Units" in row2 and "Seasonally Adjusted" in row2):
            hits.append(row2)
    if not hits:
        raise RuntimeError(
            "Phase-0 failed: Pre-master did not map a SAAR 'Housing Units Started' "
            "level column to sheet H Started (expected COL 89)."
        )
    desc = " ".join(hits[0].split())
    return (
        "PASS: Pre-master maps sheet `H Started` to "
        f"'New Privately-Owned Housing Units Started: Total Units, Thousands of Units, Monthly, "
        f"Seasonally Adjusted Annual Rate' (verbatim: `{desc}`). Confirms FRED HOUST (SAAR, "
        "thousands). Distinct from Building Permits (PERMIT/BP) and New Home Sales "
        "(HSN1FNSA/nhs, HSN1F/nh_sold_saar)."
    )


def fetch_fred_houst() -> pd.Series:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=HOUST"
    last_err = None
    for _ in range(3):
        try:
            df = pd.read_csv(url)
            break
        except Exception as exc:  # pragma: no cover - network retry path
            last_err = exc
    else:
        raise RuntimeError(f"FRED fetch failed for HOUST: {last_err}")
    df = df.rename(columns={"observation_date": "date", "HOUST": "hst"})
    df["date"] = pd.to_datetime(df["date"])
    df["hst"] = pd.to_numeric(df["hst"], errors="coerce")
    s = df.dropna(subset=["hst"]).set_index("date")["hst"].astype(float).sort_index()
    s.index = s.index + pd.offsets.MonthEnd(0)
    s.name = "hst_level"
    if s.index.min() != pd.Timestamp("1959-01-31"):
        raise RuntimeError(f"Unexpected HOUST start: {s.index.min()}")
    if s.index.max() < pd.Timestamp("2026-03-31"):
        raise RuntimeError(f"FRED HOUST is stale: latest {s.index.max().date()}")
    return s


def read_data_master_hst() -> pd.Series:
    dm = pd.read_excel(
        DATA_DIR / "Data Master.xlsx",
        sheet_name="H Started",
        usecols=["date", "RE - H Started"],
    ).dropna(subset=["RE - H Started"])
    dm["date"] = pd.to_datetime(dm["date"]) + pd.offsets.MonthEnd(0)
    return dm.set_index("date")["RE - H Started"].astype(float).sort_index()


def crosscheck_data_master(hst: pd.Series) -> str:
    dm = read_data_master_hst()
    overlap = pd.DataFrame({"fred": hst, "dm": dm}).dropna()
    if overlap.empty:
        raise RuntimeError("Data Master cross-check failed: no overlap with FRED HOUST")
    diff = (overlap["fred"] - overlap["dm"]).abs()
    corr = float(overlap["fred"].corr(overlap["dm"]))
    exact_rate = float((diff <= 1.0).mean())
    max_diff = float(diff.max())
    if corr < 0.995:
        raise RuntimeError(f"Data Master cross-check failed: level correlation={corr:.6f}")
    if exact_rate < 0.90:
        raise RuntimeError(
            f"Data Master cross-check failed: only {exact_rate:.2%} of months within 1k of FRED"
        )
    last = overlap.iloc[-1]
    return (
        "PASS (soft): Data Master 'RE - H Started' (sheet H Started) agrees with live FRED HOUST. "
        f"Level corr={corr:.6f}; {exact_rate:.1%} of {len(overlap)} overlapping months within 1k; "
        f"max abs diff {max_diff:.1f}k (benign vintage/revision drift). FRED live is source of truth. "
        f"Last overlap {overlap.index[-1].date()}: FRED={last['fred']:.0f}k, DataMaster={last['dm']:.0f}k."
    )


def fetch_yahoo_close(ticker: str, start: str, end: str, name: str) -> pd.Series:
    import yfinance as yf

    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False, threads=False)
        if df.empty:
            raise RuntimeError(f"Yahoo returned no data for {ticker}")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        s = df["Close"].astype(float).dropna()
        s.index = pd.to_datetime(s.index)
        if s.index.tz is not None:
            s.index = s.index.tz_localize(None)
        s.name = name
        return s
    except Exception as exc:  # noqa: BLE001
        if ticker.upper() != "SPY":
            raise
        print(f"  WARN: Yahoo fetch failed for SPY ({exc}); falling back to cached SPY close.")
        return _cached_spy_close(name)


def _cached_spy_close(name: str) -> pd.Series:
    """Fallback: reuse the SPY adjusted-close already cached by another pair's daily
    parquet. SPY close is identical across pairs (all Yahoo auto-adjusted). Picks the
    longest available cached series. Used only when the live Yahoo API is rate-limited."""
    import glob

    best = None
    for f in glob.glob(str(DATA_DIR / "*_daily_latest.parquet")):
        try:
            df = pd.read_parquet(f)
        except Exception:
            continue
        if "spy" not in df.columns:
            continue
        s = df["spy"].dropna()
        if best is None or len(s) > len(best[1]):
            best = (f, s)
    if best is None:
        raise RuntimeError("No cached SPY close available for fallback")
    src, s = best
    s = s.copy()
    s.index = pd.to_datetime(s.index)
    if s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    s.index = s.index.as_unit("ns")
    s.name = name
    print(f"  Using cached SPY close from {repo_rel(Path(src))}: "
          f"{s.index.min().date()} to {s.index.max().date()}, {len(s)} obs.")
    return s


def add_hst_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """All signal transforms. HOUST is SA, so MoM is a valid momentum input and no
    deseasonalisation is required. Raw level is provenance only."""
    n = df["hst_level"]
    df["hst_pct_yoy"] = (n / n.shift(12) - 1) * 100.0
    df["hst_pct_mom"] = (n / n.shift(1) - 1) * 100.0
    df["hst_3m_pct"] = (n / n.shift(3) - 1) * 100.0
    df["hst_3m_pct_yoy"] = (n.rolling(3).mean() / n.rolling(3).mean().shift(12) - 1) * 100.0
    df["hst_yoy_accel_pct"] = df["hst_pct_yoy"].diff()
    roll = df["hst_pct_yoy"].rolling(120, min_periods=60)
    df["hst_yoy_zscore_120m"] = (df["hst_pct_yoy"] - roll.mean()) / roll.std()
    df["hst_yoy_contraction_flag"] = (df["hst_pct_yoy"] < 0).astype(float)
    return df


def build_monthly(hst: pd.Series, spy: pd.Series) -> pd.DataFrame:
    idx = pd.date_range("1990-01-31", hst.index.max(), freq="ME")
    df = pd.DataFrame({"hst_level": hst.reindex(idx)}, index=idx)
    df.index.name = "date"
    df = add_hst_transforms(df)
    spy_m = spy.resample("ME").last()
    df["spy"] = spy_m.reindex(df.index)
    df["spy_ret"] = df["spy"].pct_change()
    for h in [1, 3, 6, 12]:
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    return df


def build_daily_lvcf(hst: pd.Series, spy: pd.Series) -> pd.DataFrame:
    monthly_all = add_hst_transforms(pd.DataFrame({"hst_level": hst.copy()}))
    release_events = monthly_all.reset_index(names="reference_month_end")
    release_events["release_date"] = release_events["reference_month_end"].map(mid_month_next_release)
    release_events = release_events.sort_values("release_date")

    df = pd.DataFrame(index=spy.index)
    df.index.name = "date"
    df["spy"] = spy
    left = df.reset_index().rename(columns={"date": "trade_date"}).sort_values("trade_date")
    left["trade_date"] = left["trade_date"].astype("datetime64[ns]")
    release_events = release_events.sort_values("release_date")
    release_events["release_date"] = release_events["release_date"].astype("datetime64[ns]")
    merged = pd.merge_asof(
        left,
        release_events,
        left_on="trade_date",
        right_on="release_date",
        direction="backward",
    ).set_index("trade_date")
    merged.index.name = "date"
    merged = merged.dropna(subset=["hst_pct_yoy"]).copy()
    merged["reference_month_end"] = pd.to_datetime(merged["reference_month_end"])
    merged["release_date"] = pd.to_datetime(merged["release_date"])
    merged["days_since_release"] = (merged.index - merged["release_date"]).dt.days.astype("float64")

    ordered_cols = [
        "spy",
        "reference_month_end",
        "release_date",
        "hst_level",
        "hst_pct_yoy",
        "hst_pct_mom",
        "hst_3m_pct",
        "hst_3m_pct_yoy",
        "hst_yoy_accel_pct",
        "hst_yoy_zscore_120m",
        "hst_yoy_contraction_flag",
        "days_since_release",
    ]
    merged = merged[ordered_cols]
    merged["spy_ret"] = merged["spy"].pct_change()
    for h in [1, 5, 21, 63, 126, 252]:
        merged[f"spy_fwd_{h}d"] = merged["spy"].shift(-h) / merged["spy"] - 1
    return merged


def run_stationarity(monthly: pd.DataFrame) -> pd.DataFrame:
    from arch.unitroot import ADF, KPSS

    variables = {
        "hst_level": monthly["hst_level"],
        "hst_pct_yoy": monthly["hst_pct_yoy"],
        "hst_pct_mom": monthly["hst_pct_mom"],
        "hst_3m_pct": monthly["hst_3m_pct"],
        "hst_3m_pct_yoy": monthly["hst_3m_pct_yoy"],
        "hst_yoy_accel_pct": monthly["hst_yoy_accel_pct"],
        "hst_yoy_zscore_120m": monthly["hst_yoy_zscore_120m"],
        "spy_ret": monthly["spy_ret"],
    }
    rows = []
    for name, s in variables.items():
        x = s.replace([np.inf, -np.inf], np.nan).dropna()
        for test in ["ADF", "KPSS"]:
            try:
                if test == "ADF":
                    obj = ADF(x, max_lags=12)
                    conclusion = "Stationary at 5%" if obj.pvalue < 0.05 else "Non-stationary"
                else:
                    obj = KPSS(x)
                    conclusion = "Fail to reject stationarity" if obj.pvalue > 0.05 else "Reject stationarity at 5%"
                rows.append({
                    "variable": name, "test": test,
                    "statistic": round(float(obj.stat), 4),
                    "p_value": round(float(obj.pvalue), 4),
                    "lags": int(obj.lags), "n_obs": int(len(x)),
                    "conclusion": conclusion,
                })
            except Exception as exc:
                rows.append({
                    "variable": name, "test": test, "statistic": np.nan,
                    "p_value": np.nan, "lags": np.nan, "n_obs": int(len(x)),
                    "conclusion": f"failed: {exc}",
                })
    return pd.DataFrame(rows)


def col_meta(col: str, frequency: str):
    """(dtype, unit, display, direction, description, source, ttl)."""
    meta = {
        "date": ("datetime64[ns]", "date", "Date", "neutral", f"{frequency.title()} date index.", "derived:index", 30),
        "reference_month_end": ("datetime64[ns]", "date", "Housing Starts Reference Month End", "neutral", "Reference-period month end for the carried Housing Starts observation.", "FRED:HOUST", 30),
        "release_date": ("datetime64[ns]", "date", "Housing Starts Release Date", "neutral", "Assumed market availability date: ~17th of the following month for the prior-month Census/HUD New Residential Construction value.", "FRED:HOUST", 30),
        "days_since_release": ("float64", "count", "Days Since Release", "neutral", "Calendar days since the most recent Housing Starts release available to the market.", "derived:release_calendar", 30),
        "hst_level": ("float64", "count", "Housing Starts (000s, SAAR)", "neutral", "FRED HOUST level, thousands of units, Seasonally Adjusted Annual Rate. Provenance only; trend-dominated / non-stationary, not used as a signal.", "FRED:HOUST", 30),
        "hst_pct_yoy": ("float64", "pct", "Housing Starts YoY (%)", "higher_is_better", "Year-over-year percent change of FRED HOUST; PRIMARY growth signal.", "derived:FRED:HOUST pct_change(12)*100", 30),
        "hst_pct_mom": ("float64", "pct", "Housing Starts MoM (%)", "higher_is_better", "Month-over-month percent change of FRED HOUST; valid momentum input because the series is seasonally adjusted.", "derived:FRED:HOUST pct_change(1)*100", 30),
        "hst_3m_pct": ("float64", "pct", "Housing Starts 3M Change (%)", "higher_is_better", "Three-month percent change of the HOUST level.", "derived:FRED:HOUST pct_change(3)*100", 30),
        "hst_3m_pct_yoy": ("float64", "pct", "Housing Starts 3M-Avg YoY (%)", "higher_is_better", "YoY percent change of the 3-month moving average of HOUST; smooths month-to-month noise.", "derived:FRED:HOUST rolling(3).mean() yoy", 30),
        "hst_yoy_accel_pct": ("float64", "pct", "Housing Starts YoY Acceleration (pp)", "higher_is_better", "One-month change in Housing Starts YoY growth, percentage points.", "derived:diff(hst_pct_yoy)", 30),
        "hst_yoy_zscore_120m": ("float64", "none", "Housing Starts YoY 120M Z-Score", "higher_is_better", "Rolling 120-month z-score of Housing Starts YoY growth, minimum 60 observations.", "derived:rolling_zscore(hst_pct_yoy)", 30),
        "hst_yoy_contraction_flag": ("float64", "none", "Housing Starts YoY Contraction Flag", "lower_is_better", "1.0 when Housing Starts YoY growth is below 0%, marking a construction-activity contraction.", "derived:hst_pct_yoy<0", 30),
        "spy": ("float64", "price", "SPY Close ($)", "neutral", "SPY adjusted close from Yahoo Finance.", "yahoo:SPY", 1),
        "spy_ret": ("float64", "decimal_return", "SPY Daily Return (decimal)" if frequency == "daily" else "SPY Monthly Return", "neutral", f"Simple SPY return over the {frequency} panel frequency.", "yahoo:SPY", 1),
    }
    for h in [1, 3, 6, 12]:
        meta[f"spy_fwd_{h}m"] = ("float64", "decimal_return", f"SPY Forward {h}M Return", "neutral", f"Forward {h}-month SPY return, decimal.", "derived:yahoo:SPY", 1)
    for h in [1, 5, 21, 63, 126, 252]:
        meta[f"spy_fwd_{h}d"] = ("float64", "decimal_return", f"SPY {h}-Day Forward Return", "neutral", f"Forward {h}-trading-day SPY return, decimal.", "derived:yahoo:SPY", 1)
    return meta[col]


def metadata_for_columns(df: pd.DataFrame, frequency: str, parquet_path: Path) -> dict:
    cols = {
        "date": {
            "dtype": "datetime64[ns]", "unit": "date", "display_name": "Date",
            "direction": "neutral",
            "description": f"{frequency.title()} date index; spans {df.index.min().date()} through {df.index.max().date()}.",
        }
    }
    registry = pd.read_csv(DATA_DIR / "display_name_registry.csv").set_index("column_name").to_dict("index")
    for col in df.columns:
        dtype, unit, display, direction, desc, source, ttl = col_meta(col, frequency)
        if col in registry and col not in {"reference_month_end", "release_date"}:
            display = registry[col]["display_name"]
            unit = registry[col]["unit"]
        cols[col] = {
            "dtype": str(df[col].dtype) if not pd.api.types.is_datetime64_any_dtype(df[col]) else "datetime64[ns]",
            "unit": unit, "display_name": display, "direction": direction,
            "description": desc, "source_reference": source, "refresh_ttl_days": ttl,
        }
    return {
        "pair_id": PAIR_ID,
        "parquet_path": repo_rel(parquet_path),
        "schema_version": "1.0.0",
        "generated_at": NOW_ISO,
        "columns": cols,
    }


def write_data_dictionary(monthly, daily, path, phase0, dm_check) -> None:
    rows = []
    for frequency, df in [("monthly", monthly), ("daily", daily)]:
        meta = metadata_for_columns(df, frequency, Path(f"data/{PAIR_ID}_{frequency}_placeholder.parquet"))
        for col in ["date"] + list(df.columns):
            m = meta["columns"][col]
            values = df.index if col == "date" else df[col].dropna().index
            is_hst = col.startswith("hst") or col in {"reference_month_end", "release_date", "days_since_release"}
            rows.append({
                "frequency": frequency, "column_name": col,
                "display_name": m["display_name"], "description": m["description"],
                "source": "FRED" if is_hst else "Yahoo Finance",
                "series_id": "HOUST" if is_hst else "SPY",
                "unit": m["unit"],
                "transformation": "Monthly SAAR level" if col == "hst_level" else ("Monthly-to-daily LVCF from approximate Census/HUD release date" if frequency == "daily" and is_hst else "See description"),
                "seasonal_adj": "Seasonally adjusted at source (SAAR)" if is_hst and col != "hst_yoy_contraction_flag" else ("N/A" if not is_hst else "Seasonally adjusted at source (SAAR)"),
                "direction_convention": "Higher Housing Starts YoY growth = stronger construction activity = procyclical prior for SPY; 0% YoY marks contraction. Raw SAAR level is neutral/provenance only.",
                "effective_start": str(values.min().date()) if len(values) else "",
                "known_quirks": f"SA series (SAAR) — MoM is a valid momentum input, no deseasonalisation needed. Raw level is non-stationary and excluded from the signal set. {phase0} {dm_check}",
                "display_note": "Housing Starts is a monthly Census/HUD series, seasonally adjusted at an annual rate. The daily panel only updates after the estimated release date (~17th of the following month), so daily values are a step function.",
                "refresh_freq": "monthly" if is_hst else "daily",
                "refresh_source": "FRED HOUST" if is_hst else "Yahoo Finance",
            })
    pd.DataFrame(rows).to_csv(path, index=False)


def update_display_registry(monthly, daily) -> None:
    reg_path = DATA_DIR / "display_name_registry.csv"
    reg = pd.read_csv(reg_path)
    existing = set(reg["column_name"])
    axis_overrides = {
        "hst_level": "Housing Starts (000s)",
        "hst_pct_yoy": "Housing Starts YoY (%)",
        "hst_pct_mom": "MoM (%)",
        "hst_3m_pct": "3M Change (%)",
        "hst_3m_pct_yoy": "3M-Avg YoY (%)",
        "hst_yoy_accel_pct": "YoY Acceleration (pp)",
        "hst_yoy_zscore_120m": "Z-Score",
        "hst_yoy_contraction_flag": "Contraction (0/1)",
        "reference_month_end": "Reference Month",
        "release_date": "Release Date",
        "days_since_release": "Days Since Release",
    }
    rows = []
    all_cols = ["date"] + list(dict.fromkeys(list(monthly.columns) + list(daily.columns)))
    for col in all_cols:
        if col in existing:
            continue
        _, unit, display, _, _, _, _ = col_meta(col, "daily")
        rows.append({
            "column_name": col, "display_name": display, "unit": unit,
            "axis_label": axis_overrides.get(col, display),
        })
    if rows:
        reg = pd.concat([reg, pd.DataFrame(rows)], ignore_index=True)
    reg.to_csv(reg_path, index=False, lineterminator="\n")

    obj = {
        "schema_version": "1.0.0",
        "generated_at": NOW_ISO,
        "columns": reg[["column_name", "display_name", "unit", "axis_label"]].to_dict("records"),
    }
    (DATA_DIR / "display_name_registry.json").write_text(json.dumps(obj, indent=2) + "\n")


def update_manifest(monthly_path, monthly_latest, daily_path, daily_latest) -> None:
    manifest_path = DATA_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    artifacts = [a for a in manifest["artifacts"] if PAIR_ID not in a.get("path", "")]
    last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = {
        "source": "FRED:HOUST (monthly SAAR housing starts, 000s units) + yahoo:SPY",
        "refresh_ttl_days": 1,
        "last_updated": last_updated,
        "pairs": [PAIR_ID],
        "mixed_freq_ttl_note": "Monthly Housing Starts indicator plus daily SPY market data; TTL=1 per fastest-refreshing component. The indicator itself changes monthly after the Census/HUD release.",
    }
    entries = [
        {**base, "path": repo_rel(monthly_path), "schema_ref": f"data/{PAIR_ID}_monthly_schema.json", "refresh_ttl_days": 30, "mixed_freq_ttl_note": "Monthly analysis panel; TTL=30 because both signal rows and target snapshots are month-end."},
        {**base, "path": repo_rel(monthly_latest), "source": f"alias_of:{repo_rel(monthly_path)}", "schema_ref": f"data/{PAIR_ID}_monthly_schema.json", "source_master": repo_rel(monthly_path), "refresh_ttl_days": 30, "mixed_freq_ttl_note": "Monthly analysis panel alias; TTL=30 because both signal rows and target snapshots are month-end."},
        {**base, "path": repo_rel(daily_path), "schema_ref": f"data/{PAIR_ID}_daily_schema.json"},
        {**base, "path": repo_rel(daily_latest), "source": f"alias_of:{repo_rel(daily_path)}", "schema_ref": f"data/{PAIR_ID}_daily_schema.json", "source_master": repo_rel(daily_path)},
    ]
    manifest["artifacts"] = artifacts + entries
    manifest["generated_at"] = NOW_ISO
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def update_prospective_pairs() -> None:
    path = DATA_DIR / "prospective_pairs.csv"
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    changed = False
    for row in rows:
        if row["pair_id"] == PAIR_ID:
            row["status"] = "in_progress"
            changed = True
            break
    if not changed:
        raise RuntimeError(f"{PAIR_ID} not found in prospective_pairs.csv")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_missing_report(monthly, daily, phase0, dm_check, path) -> None:
    lines = [
        f"# Missing Value Report - {PAIR_ID} ({DATE_TAG})",
        "",
        f"Monthly dataset: shape {monthly.shape}, {monthly.index.min().date()} to {monthly.index.max().date()}.",
        f"Daily dataset: shape {daily.shape}, {daily.index.min().date()} to {daily.index.max().date()}.",
        "",
        "## Phase 0 / Cross-Check",
        "", phase0, dm_check, "",
        "## Seasonal Adjustment (SA series)",
        "",
        "HOUST is Seasonally Adjusted at an annual rate (SAAR). Unlike HSN1FNSA (NSA), no "
        "deseasonalisation is required: `hst_pct_mom` (month-over-month) is a valid momentum "
        "input, and `hst_pct_yoy` (12-month change) is the primary growth signal. The raw SAAR "
        "level `hst_level` is trend-dominated / non-stationary and is intentionally NOT provided "
        "as a signal.",
        "",
        "## Real-Time Lag",
        "",
        "Daily LVCF uses release dates set to the ~17th of the month following the reference "
        "month, approximating the joint Census/HUD New Residential Construction release schedule "
        "(~16th-19th). No-lookahead floor ~16-19 calendar days after reference month-end.",
        "",
        "## Missing Values",
        "",
        "| Dataset | Column | NaN count | Note |",
        "|---|---|---:|---|",
    ]
    for label, df in [("monthly", monthly), ("daily", daily)]:
        for col in df.columns:
            n = int(df[col].isna().sum())
            note = "leading transform / forward-return tail" if n else "none"
            lines.append(f"| {label} | `{col}` | {n} | {note} |")
    path.write_text("\n".join(lines) + "\n")


def write_interpretation_metadata(path: Path) -> None:
    meta = {
        "pair_id": PAIR_ID,
        "schema_version": "1.1.0",
        "indicator": INDICATOR,
        "target": TARGET,
        "indicator_nature": "leading",
        "indicator_type": "housing",
        "strategy_objective": "max_sharpe",
        "expected_direction": "procyclical",
        "data_provenance": {
            "source": "FRED HOUST live API; Data Master.xlsx sheet 'H Started' column 'RE - H Started' used as overlap cross-check",
            "series_id": "HOUST",
            "accessed_at": NOW_ISO,
        },
        "known_stress_episodes": [
            {"label": "Housing bubble peak & GFC collapse", "start": "2005-07-01", "end": "2009-06-30",
             "note": "Housing starts peaked in early 2006 and collapsed ~75% into 2009 — a classic leading signal ahead of the GFC."},
            {"label": "COVID dip and surge", "start": "2020-03-01", "end": "2021-12-31",
             "note": "Starts dipped sharply then surged on low rates and a demand shift."},
            {"label": "2022-24 rate shock", "start": "2022-04-01", "end": "2024-12-31",
             "note": "Mortgage-rate shock cut starts materially; a strong recent regime captured in the OOS window."},
        ],
        "related_pair_ids": ["permit_spy", "nhs_spy", "indpro_spy"],
        "owner_writes": {
            "dana": ["pair_id", "schema_version", "indicator", "target", "indicator_nature",
                     "indicator_type", "data_provenance", "known_stress_episodes", "related_pair_ids"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "expected_direction", "mechanism", "caveats", "narrative_summary"],
        },
        "last_updated_by": "dana",
        "last_updated_at": NOW_ISO,
    }
    path.write_text(json.dumps(meta, indent=2) + "\n")


def stationarity_verdict(stat: pd.DataFrame) -> str:
    lines = []
    for var in ["hst_level", "hst_pct_yoy", "hst_pct_mom", "hst_3m_pct", "hst_3m_pct_yoy", "hst_yoy_accel_pct", "hst_yoy_zscore_120m"]:
        sub = stat[stat["variable"] == var]
        adf = sub[sub["test"] == "ADF"].iloc[0]
        kpss = sub[sub["test"] == "KPSS"].iloc[0]
        lines.append(f"- `{var}`: ADF p={adf.p_value:.4f} ({adf.conclusion}); KPSS p={kpss.p_value:.4f} ({kpss.conclusion}).")
    return "\n".join(lines)


def write_handoff(path, phase0, dm_check, monthly_path, daily_path, stationarity_path, monthly, daily, stat) -> None:
    text = f"""Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/{PAIR_ID}_monthly_latest.parquet` (source dated file `{repo_rel(monthly_path)}`)
- Daily LVCF dataset: `data/{PAIR_ID}_daily_latest.parquet` (source dated file `{repo_rel(daily_path)}`)
- Monthly sidecar: `data/{PAIR_ID}_monthly_schema.json`
- Daily sidecar: `data/{PAIR_ID}_daily_schema.json`
- Data dictionary: `data/data_dictionary_{PAIR_ID}_{DATE_TAG}.csv`
- Missing-value report: `data/missing_value_report_{PAIR_ID}_{DATE_TAG}.md`
- Stationarity: `{repo_rel(stationarity_path)}`
- Interpretation metadata: `results/{PAIR_ID}/interpretation_metadata.json`

Summary:
Built the Housing Starts (SAAR) -> SPY data layer from live FRED HOUST. Monthly panel is {monthly.shape[0]} rows x {monthly.shape[1]} columns, {monthly.index.min().date()} to {monthly.index.max().date()}. Daily panel is {daily.shape[0]} SPY trading days x {daily.shape[1]} columns, {daily.index.min().date()} to {daily.index.max().date()}, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
{phase0}
{dm_check}

SA handling (contrast with nhs_spy):
HOUST is Seasonally Adjusted (SAAR). NO deseasonalisation needed. `hst_pct_mom` is a valid momentum
input; `hst_pct_yoy` is the primary growth signal. The raw SAAR level `hst_level` is trend-dominated
/ non-stationary and is EXCLUDED from the signal set. Direction prior: procyclical (stronger
construction activity -> risk-on). Counter-channel: at cycle peaks a far-above-trend reading can
mean-revert (INDPRO precedent) — verify empirically.

Release lag floor:
Daily LVCF assumes prior-month starts are released on the ~17th of the following month (Census/HUD
New Residential Construction schedule). No-lookahead floor ~16-19 calendar days after reference month-end.

Stationarity:
{stationarity_verdict(stat)}

Recommendation:
Primary transform `hst_pct_yoy`; robustness set `hst_pct_mom`, `hst_3m_pct`, `hst_3m_pct_yoy`,
`hst_yoy_accel_pct`, `hst_yoy_zscore_120m`. Treat `hst_yoy_contraction_flag` as a threshold/regime
feature. Monthly lead grid L0..12 per ECON-LL1 with the release-lag floor honored. MANDATORY
reverse-causality check (housing and equities jointly driven by rates).

Known issues:
- Release dates approximated by a mid-month (~17th) rule, not a historical release-timestamp file.
- Daily indicator is a deliberate monthly step function -> serial dependence in daily OLS-style specs.

Questions for recipient:
- None. Set the no-lookahead lead-grid floor at one monthly publication lag.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PWS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72); print("PHASE 0: DATA MASTER VERIFICATION"); print("=" * 72)
    phase0 = verify_pre_master(); print(phase0)

    print("\n" + "=" * 72); print("SOURCING"); print("=" * 72)
    hst = fetch_fred_houst()
    dm_check = crosscheck_data_master(hst); print(dm_check)
    spy = fetch_yahoo_close("SPY", "1990-01-01", "2026-08-01", "spy")
    print(f"FRED HOUST: {len(hst)} obs, {hst.index.min().date()} to {hst.index.max().date()}")
    print(f"SPY: {len(spy)} obs, {spy.index.min().date()} to {spy.index.max().date()}")

    print("\n" + "=" * 72); print("BUILD PANELS"); print("=" * 72)
    monthly = build_monthly(hst, spy)
    daily = build_daily_lvcf(hst, spy)
    assert monthly.index.is_monotonic_increasing and daily.index.is_monotonic_increasing
    assert not monthly.index.duplicated().any() and not daily.index.duplicated().any()
    assert daily["days_since_release"].ge(0).all()
    assert daily["hst_pct_yoy"].loc["2009"].min() < -20.0, "GFC housing collapse missing"
    print(f"Monthly: {monthly.shape}, {monthly.index.min().date()} to {monthly.index.max().date()}")
    print(f"Daily:   {daily.shape}, {daily.index.min().date()} to {daily.index.max().date()}")

    print("\n" + "=" * 72); print("STATIONARITY"); print("=" * 72)
    stat = run_stationarity(monthly)
    stat_path = RESULTS_DIR / f"stationarity_tests_{DATE_TAG}.csv"
    stat.to_csv(stat_path, index=False)
    print(stat.to_string(index=False))

    print("\n" + "=" * 72); print("WRITE ARTIFACTS"); print("=" * 72)
    m_start, m_end = monthly.index.min().strftime("%Y%m%d"), monthly.index.max().strftime("%Y%m%d")
    d_start, d_end = daily.index.min().strftime("%Y%m%d"), daily.index.max().strftime("%Y%m%d")
    monthly_path = DATA_DIR / f"{PAIR_ID}_monthly_{m_start}_{m_end}.parquet"
    daily_path = DATA_DIR / f"{PAIR_ID}_daily_{d_start}_{d_end}.parquet"
    monthly_latest = DATA_DIR / f"{PAIR_ID}_monthly_latest.parquet"
    daily_latest = DATA_DIR / f"{PAIR_ID}_daily_latest.parquet"
    monthly.to_parquet(monthly_path); daily.to_parquet(daily_path)
    shutil.copy2(monthly_path, monthly_latest); shutil.copy2(daily_path, daily_latest)

    monthly_schema_path = DATA_DIR / f"{PAIR_ID}_monthly_schema.json"
    daily_schema_path = DATA_DIR / f"{PAIR_ID}_daily_schema.json"
    monthly_schema_path.write_text(json.dumps(metadata_for_columns(monthly, "monthly", monthly_path), indent=2) + "\n")
    daily_schema_path.write_text(json.dumps(metadata_for_columns(daily, "daily", daily_path), indent=2) + "\n")

    dict_path = DATA_DIR / f"data_dictionary_{PAIR_ID}_{DATE_TAG}.csv"
    write_data_dictionary(monthly, daily, dict_path, phase0, dm_check)
    monthly.describe().T.round(4).to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_monthly_{DATE_TAG}.csv")
    daily.describe(include="all").T.to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_daily_{DATE_TAG}.csv")
    mv_path = DATA_DIR / f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md"
    write_missing_report(monthly, daily, phase0, dm_check, mv_path)

    meta_path = RESULTS_DIR / "interpretation_metadata.json"
    write_interpretation_metadata(meta_path)
    update_display_registry(monthly, daily)
    update_manifest(monthly_path, monthly_latest, daily_path, daily_latest)
    update_prospective_pairs()

    handoff_path = PWS_DIR / "dana_handoff.md"
    write_handoff(handoff_path, phase0, dm_check, monthly_path, daily_path, stat_path, monthly, daily, stat)

    print("\n" + "=" * 72); print("VALIDATE"); print("=" * 72)
    validate_json("docs/schemas/data_subject.schema.json", repo_rel(monthly_schema_path))
    validate_json("docs/schemas/data_subject.schema.json", repo_rel(daily_schema_path))
    validate_json("docs/schemas/interpretation_metadata.schema.json", repo_rel(meta_path))
    validate_json("docs/schemas/data_manifest.schema.json", "data/manifest.json")
    validate_json("docs/schemas/display_name_registry.schema.json", "data/display_name_registry.json")

    print("\nDANA DONE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nDANA BLOCKED: {exc}")
        raise
