#!/usr/bin/env python3
"""
Data Stage: New Home Sales (NSA) x SPY
======================================

Mode-2 Dana dispatch for pair_id nhs_spy.

Authoritative live source: FRED HSN1FNSA (New One-Family Houses Sold: United
States, Thousands of Units, monthly, NOT seasonally adjusted). Data Master.xlsx
sheet HAJKE_Month column NHS is used only as the required Phase-0/cross-check
source.

NSA handling (the defining feature of this pair):
  HSN1FNSA carries a strong, stable monthly seasonal (spring selling-season
  peak, winter trough). Raw levels and raw MoM are dominated by seasonality and
  are NOT valid signal inputs. Mitigations, in priority order:
    (a) YoY% (12-month difference) is the PRIMARY transform — cancels a fixed
        seasonal.
    (b) An STL seasonally-adjusted level (nhs_sa) and its MoM (nhs_sa_pct_mom)
        for momentum work that YoY smooths away.
    (c) Z-score computed on the YoY series, not the raw level.
  The raw NSA level (nhs_nsa) is kept for provenance only and flagged not-a-signal.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
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
RESULTS_DIR = ROOT / "results/nhs_spy"
PWS_DIR = ROOT / "_pws/lead-lesandro/nhs_spy"
PAIR_ID = "nhs_spy"
INDICATOR = "nhs"
TARGET = "spy"
DATE_TAG = "20260703"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Same interpreter that is running this script, so subprocesses inherit the environment
# the caller chose. Was pinned to .venv/bin/python — that venv is no longer tracked, and it
# was never portable anyway (built for 3.12, its shebangs hardcode an absolute host path).
PYEXE = sys.executable


def repo_rel(path: Path | str) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def validate_json(schema: str, instance: str) -> None:
    subprocess.run(
        [PYEXE, "scripts/validate_schema.py", "--schema", schema, "--instance", instance],
        cwd=ROOT,
        check=True,
    )


def fourth_tuesday_next_month(reference_month_end: pd.Timestamp) -> pd.Timestamp:
    """Approximate the Census new-home-sales release as the fourth Tuesday of the
    month following the reference month (Census releases prior-month new home
    sales around the 23rd-26th of the following month)."""
    first_next = (reference_month_end + pd.offsets.MonthBegin(1)).normalize()
    month_days = pd.date_range(first_next, first_next + pd.offsets.MonthEnd(0), freq="D")
    tuesdays = [d for d in month_days if d.weekday() == 1]
    if len(tuesdays) < 4:
        raise RuntimeError(f"Cannot find fourth Tuesday for {first_next:%Y-%m}")
    return tuesdays[3]


def verify_pre_master() -> str:
    """LEAD-DV1: confirm the Pre-master row-2 description for the NHS column is the
    NSA thousands-of-units New Home Sales series (COL 28, sheet HAJKE_Month)."""
    pm = pd.read_excel(DATA_DIR / "Data Master.xlsx", sheet_name="Pre-master", header=None, nrows=4)
    hits = []
    for j in range(pm.shape[1]):
        row1 = str(pm.iat[0, j])
        row2 = str(pm.iat[1, j])
        if row1 == "HAJKE_Month" and "New One Family Houses Sold" in row2 and "Not Seasonally Adjusted" in row2:
            hits.append(row2)
    if not hits:
        raise RuntimeError(
            "Phase-0 failed: Pre-master did not map an NSA 'New One Family Houses Sold' "
            "column to sheet HAJKE_Month (expected COL 28)."
        )
    desc = " ".join(hits[0].split())
    if "Thousands" not in desc:
        raise RuntimeError(f"Phase-0 failed: unexpected NHS units description: {desc!r}")
    return (
        "PASS: Pre-master maps sheet `HAJKE_Month` column `NHS` to "
        f"'New One Family Houses Sold, Thousands of Units, Monthly, Not Seasonally Adjusted, from FRED' "
        f"(verbatim: `{desc}`). Confirms FRED HSN1FNSA (NSA, thousands). Distinct from HSN1F "
        "(SAAR, indicator_id nh_sold_saar) and the YoY% SAAR transform."
    )


def fetch_fred_hsn1fnsa() -> pd.Series:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=HSN1FNSA"
    last_err = None
    for _ in range(3):
        try:
            df = pd.read_csv(url)
            break
        except Exception as exc:  # pragma: no cover - network retry path
            last_err = exc
    else:
        raise RuntimeError(f"FRED fetch failed for HSN1FNSA: {last_err}")
    df = df.rename(columns={"observation_date": "date", "HSN1FNSA": "nhs"})
    df["date"] = pd.to_datetime(df["date"])
    df["nhs"] = pd.to_numeric(df["nhs"], errors="coerce")
    s = df.dropna(subset=["nhs"]).set_index("date")["nhs"].astype(float).sort_index()
    s.index = s.index + pd.offsets.MonthEnd(0)
    s.name = "nhs_nsa"
    if s.index.min() != pd.Timestamp("1963-01-31"):
        raise RuntimeError(f"Unexpected HSN1FNSA start: {s.index.min()}")
    if s.index.max() < pd.Timestamp("2026-03-31"):
        raise RuntimeError(f"FRED HSN1FNSA is stale: latest {s.index.max().date()}")
    return s


def read_data_master_nhs() -> pd.Series:
    dm = pd.read_excel(
        DATA_DIR / "Data Master.xlsx",
        sheet_name="HAJKE_Month",
        usecols=["date", "NHS"],
    ).dropna(subset=["NHS"])
    dm["date"] = pd.to_datetime(dm["date"]) + pd.offsets.MonthEnd(0)
    return dm.set_index("date")["NHS"].astype(float).sort_index()


def crosscheck_data_master(nhs: pd.Series) -> str:
    dm = read_data_master_nhs()
    overlap = pd.DataFrame({"fred": nhs, "dm": dm}).dropna()
    if overlap.empty:
        raise RuntimeError("Data Master cross-check failed: no overlap with FRED HSN1FNSA")
    diff = (overlap["fred"] - overlap["dm"]).abs()
    corr = float(overlap["fred"].corr(overlap["dm"]))
    exact_rate = float((diff <= 0.5).mean())
    max_diff = float(diff.max())
    if corr < 0.995:
        raise RuntimeError(f"Data Master cross-check failed: level correlation={corr:.6f}")
    if exact_rate < 0.90:
        raise RuntimeError(
            f"Data Master cross-check failed: only {exact_rate:.2%} of months within 0.5k of FRED"
        )
    last = overlap.iloc[-1]
    return (
        "PASS (soft): Data Master NHS (HAJKE_Month) agrees with live FRED HSN1FNSA. "
        f"Level corr={corr:.6f}; {exact_rate:.1%} of {len(overlap)} overlapping months within 0.5k; "
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


def add_nhs_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """All signal transforms. YoY is primary (deseasonalises a fixed monthly
    seasonal); STL provides a seasonally-adjusted level for MoM momentum."""
    from statsmodels.tsa.seasonal import STL

    n = df["nhs_nsa"]
    # (a) YoY% — primary deseasonalised transform
    df["nhs_pct_yoy"] = (n / n.shift(12) - 1) * 100.0
    df["nhs_yoy_accel_pct"] = df["nhs_pct_yoy"].diff()
    df["nhs_3m_pct_yoy"] = (n.rolling(3).mean() / n.rolling(3).mean().shift(12) - 1) * 100.0
    # (b) STL seasonal adjustment (period=12); requires a gap-free monthly series
    n_filled = n.interpolate(limit_area="inside")
    fit = STL(n_filled.dropna(), period=12, robust=True).fit()
    sa = (fit.trend + fit.resid).reindex(df.index)
    df["nhs_sa"] = sa
    df["nhs_sa_pct_mom"] = (sa / sa.shift(1) - 1) * 100.0
    df["nhs_sa_3m_pct"] = (sa / sa.shift(3) - 1) * 100.0
    # (c) z-score on the YoY series (not the raw level)
    roll = df["nhs_pct_yoy"].rolling(120, min_periods=60)
    df["nhs_yoy_zscore_120m"] = (df["nhs_pct_yoy"] - roll.mean()) / roll.std()
    # regime feature: YoY contraction
    df["nhs_yoy_contraction_flag"] = (df["nhs_pct_yoy"] < 0).astype(float)
    return df


def build_monthly(nhs: pd.Series, spy: pd.Series) -> pd.DataFrame:
    idx = pd.date_range("1990-01-31", nhs.index.max(), freq="ME")
    df = pd.DataFrame({"nhs_nsa": nhs.reindex(idx)}, index=idx)
    df.index.name = "date"
    df = add_nhs_transforms(df)
    spy_m = spy.resample("ME").last()
    df["spy"] = spy_m.reindex(df.index)
    df["spy_ret"] = df["spy"].pct_change()
    for h in [1, 3, 6, 12]:
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    return df


def build_daily_lvcf(nhs: pd.Series, spy: pd.Series) -> pd.DataFrame:
    monthly_all = add_nhs_transforms(pd.DataFrame({"nhs_nsa": nhs.copy()}))
    release_events = monthly_all.reset_index(names="reference_month_end")
    release_events["release_date"] = release_events["reference_month_end"].map(fourth_tuesday_next_month)
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
    merged = merged.dropna(subset=["nhs_pct_yoy"]).copy()
    merged["reference_month_end"] = pd.to_datetime(merged["reference_month_end"])
    merged["release_date"] = pd.to_datetime(merged["release_date"])
    merged["days_since_release"] = (merged.index - merged["release_date"]).dt.days.astype("float64")

    ordered_cols = [
        "spy",
        "reference_month_end",
        "release_date",
        "nhs_nsa",
        "nhs_pct_yoy",
        "nhs_yoy_accel_pct",
        "nhs_3m_pct_yoy",
        "nhs_sa",
        "nhs_sa_pct_mom",
        "nhs_sa_3m_pct",
        "nhs_yoy_zscore_120m",
        "nhs_yoy_contraction_flag",
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
        "nhs_nsa": monthly["nhs_nsa"],
        "nhs_pct_yoy": monthly["nhs_pct_yoy"],
        "nhs_yoy_accel_pct": monthly["nhs_yoy_accel_pct"],
        "nhs_3m_pct_yoy": monthly["nhs_3m_pct_yoy"],
        "nhs_sa": monthly["nhs_sa"],
        "nhs_sa_pct_mom": monthly["nhs_sa_pct_mom"],
        "nhs_yoy_zscore_120m": monthly["nhs_yoy_zscore_120m"],
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
        "reference_month_end": ("datetime64[ns]", "date", "NHS Reference Month End", "neutral", "Reference-period month end for the carried New Home Sales observation.", "FRED:HSN1FNSA", 30),
        "release_date": ("datetime64[ns]", "date", "NHS Release Date", "neutral", "Assumed market availability date: fourth Tuesday of the following month for the prior-month Census new-home-sales value.", "FRED:HSN1FNSA", 30),
        "days_since_release": ("float64", "count", "Days Since Release", "neutral", "Calendar days since the most recent New Home Sales release available to the market.", "derived:release_calendar", 30),
        "nhs_nsa": ("float64", "count", "New Home Sales (000s, NSA)", "neutral", "FRED HSN1FNSA level, thousands of units, NOT seasonally adjusted. Provenance only; strong monthly seasonal makes the raw level unusable as a signal.", "FRED:HSN1FNSA", 30),
        "nhs_pct_yoy": ("float64", "pct", "New Home Sales YoY (%)", "higher_is_better", "Year-over-year percent change of FRED HSN1FNSA; PRIMARY deseasonalised signal (12-month difference cancels the fixed seasonal).", "derived:FRED:HSN1FNSA pct_change(12)*100", 30),
        "nhs_yoy_accel_pct": ("float64", "pct", "New Home Sales YoY Acceleration (pp)", "higher_is_better", "One-month change in NHS YoY growth, percentage points.", "derived:diff(nhs_pct_yoy)", 30),
        "nhs_3m_pct_yoy": ("float64", "pct", "New Home Sales 3M-Avg YoY (%)", "higher_is_better", "YoY percent change of the 3-month moving average of NHS; smooths NSA noise.", "derived:FRED:HSN1FNSA rolling(3).mean() yoy", 30),
        "nhs_sa": ("float64", "count", "New Home Sales (000s, SA/STL)", "neutral", "STL seasonally-adjusted NHS level (trend+resid, period=12, robust). Provenance/level; use its MoM for momentum.", "derived:STL(FRED:HSN1FNSA)", 30),
        "nhs_sa_pct_mom": ("float64", "pct", "New Home Sales SA MoM (%)", "higher_is_better", "Month-over-month percent change of the STL seasonally-adjusted NHS level.", "derived:STL then pct_change(1)*100", 30),
        "nhs_sa_3m_pct": ("float64", "pct", "New Home Sales SA 3M Change (%)", "higher_is_better", "Three-month percent change of the STL seasonally-adjusted NHS level.", "derived:STL then pct_change(3)*100", 30),
        "nhs_yoy_zscore_120m": ("float64", "none", "New Home Sales YoY 120M Z-Score", "higher_is_better", "Rolling 120-month z-score of NHS YoY growth, minimum 60 observations.", "derived:rolling_zscore(nhs_pct_yoy)", 30),
        "nhs_yoy_contraction_flag": ("float64", "none", "New Home Sales YoY Contraction Flag", "lower_is_better", "1.0 when NHS YoY growth is below 0%, marking a housing-demand contraction.", "derived:nhs_pct_yoy<0", 30),
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
            is_nhs = col.startswith("nhs") or col in {"reference_month_end", "release_date", "days_since_release"}
            rows.append({
                "frequency": frequency, "column_name": col,
                "display_name": m["display_name"], "description": m["description"],
                "source": "FRED" if is_nhs else "Yahoo Finance",
                "series_id": "HSN1FNSA" if is_nhs else "SPY",
                "unit": m["unit"],
                "transformation": "Monthly NSA level" if col == "nhs_nsa" else ("Monthly-to-daily LVCF from approximate Census release date" if frequency == "daily" and is_nhs else "See description"),
                "seasonal_adj": "Not seasonally adjusted (raw)" if col == "nhs_nsa" else ("STL seasonally adjusted" if col.startswith("nhs_sa") else ("Deseasonalised via YoY" if col.startswith("nhs_") and is_nhs else "N/A")),
                "direction_convention": "Higher NHS YoY growth = stronger housing demand = procyclical prior for SPY; 0% YoY marks contraction. Raw NSA level and STL level are neutral/provenance only.",
                "effective_start": str(values.min().date()) if len(values) else "",
                "known_quirks": f"NSA series with strong monthly seasonal — use YoY/STL transforms, never raw level or raw MoM. {phase0} {dm_check}",
                "display_note": "New Home Sales is a monthly Census series, not seasonally adjusted at source. We compare each month to the same month a year earlier (YoY) to strip out the regular spring-vs-winter swing. The daily panel only updates after the estimated Census release date, so daily values are a step function.",
                "refresh_freq": "monthly" if is_nhs else "daily",
                "refresh_source": "FRED HSN1FNSA" if is_nhs else "Yahoo Finance",
            })
    pd.DataFrame(rows).to_csv(path, index=False)


def update_display_registry(monthly, daily) -> None:
    reg_path = DATA_DIR / "display_name_registry.csv"
    reg = pd.read_csv(reg_path)
    existing = set(reg["column_name"])
    axis_overrides = {
        "nhs_nsa": "New Home Sales (000s)",
        "nhs_pct_yoy": "NHS YoY (%)",
        "nhs_yoy_accel_pct": "YoY Acceleration (pp)",
        "nhs_3m_pct_yoy": "3M-Avg YoY (%)",
        "nhs_sa": "New Home Sales SA (000s)",
        "nhs_sa_pct_mom": "SA MoM (%)",
        "nhs_sa_3m_pct": "SA 3M Change (%)",
        "nhs_yoy_zscore_120m": "Z-Score",
        "nhs_yoy_contraction_flag": "Contraction (0/1)",
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
        "source": "FRED:HSN1FNSA (monthly NSA new home sales, 000s units) + yahoo:SPY",
        "refresh_ttl_days": 1,
        "last_updated": last_updated,
        "pairs": [PAIR_ID],
        "mixed_freq_ttl_note": "Monthly NHS indicator plus daily SPY market data; TTL=1 per fastest-refreshing component. The indicator itself changes monthly after the Census release.",
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
        "## Seasonal Adjustment (NSA series)",
        "",
        "HSN1FNSA is NOT seasonally adjusted. The primary signal `nhs_pct_yoy` is a 12-month "
        "difference, which cancels the fixed monthly seasonal. A robust STL decomposition "
        "(period=12) provides a seasonally-adjusted level `nhs_sa` and its momentum "
        "`nhs_sa_pct_mom`. Raw `nhs_nsa` level and raw MoM are intentionally NOT provided as "
        "signals — they are seasonal-dominated.",
        "",
        "## Real-Time Lag",
        "",
        "Daily LVCF uses release dates set to the fourth Tuesday of the month following the "
        "reference month, approximating the Census new-home-sales release schedule (~23rd-26th "
        "of the following month). No-lookahead floor ~22-28 calendar days after reference month-end.",
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
            "source": "FRED HSN1FNSA live API; Data Master.xlsx sheet HAJKE_Month column NHS used as overlap cross-check",
            "series_id": "HSN1FNSA",
            "accessed_at": NOW_ISO,
        },
        "known_stress_episodes": [
            {"label": "Housing bubble peak & GFC collapse", "start": "2005-07-01", "end": "2009-06-30",
             "note": "New home sales peaked mid-2005 and collapsed ~80% into 2009 — a classic leading signal ahead of the GFC."},
            {"label": "COVID spike and reversal", "start": "2020-03-01", "end": "2022-06-30",
             "note": "Sales surged on low rates then reversed as rates rose."},
            {"label": "2022-23 rate shock", "start": "2022-07-01", "end": "2023-12-31",
             "note": "Mortgage-rate shock crushed new home sales; strong recent regime captured in the OOS window."},
        ],
        "related_pair_ids": ["permit_spy", "nh_sold_saar_xly", "indpro_spy"],
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
    for var in ["nhs_nsa", "nhs_pct_yoy", "nhs_yoy_accel_pct", "nhs_3m_pct_yoy", "nhs_sa", "nhs_sa_pct_mom", "nhs_yoy_zscore_120m"]:
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
Built the New Home Sales (NSA) -> SPY data layer from live FRED HSN1FNSA. Monthly panel is {monthly.shape[0]} rows x {monthly.shape[1]} columns, {monthly.index.min().date()} to {monthly.index.max().date()}. Daily panel is {daily.shape[0]} SPY trading days x {daily.shape[1]} columns, {daily.index.min().date()} to {daily.index.max().date()}, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
{phase0}
{dm_check}

CRITICAL — NSA handling:
HSN1FNSA is NOT seasonally adjusted. Do NOT use `nhs_nsa` (raw level) or a raw MoM as a signal — both are seasonal-dominated. Primary signal is `nhs_pct_yoy` (12-month difference cancels the fixed seasonal). `nhs_sa`/`nhs_sa_pct_mom` are STL-deseasonalised alternatives for momentum. `nhs_yoy_zscore_120m` is computed on the YoY series. Direction prior: procyclical (stronger housing demand -> risk-on). Counter-channel: at cycle peaks a far-above-trend reading can mean-revert (INDPRO precedent) — verify empirically.

Release lag floor:
Daily LVCF assumes prior-month NHS is released on the fourth Tuesday of the following month (~Census schedule). No-lookahead floor ~22-28 calendar days after reference month-end.

Stationarity:
{stationarity_verdict(stat)}

Recommendation:
Primary transform `nhs_pct_yoy`; robustness set `nhs_yoy_accel_pct`, `nhs_3m_pct_yoy`, `nhs_sa_pct_mom`, `nhs_yoy_zscore_120m`. Treat `nhs_yoy_contraction_flag` as a threshold/regime feature. Monthly lead grid L0..12 per ECON-LL1 with the release-lag floor honored. MANDATORY reverse-causality check (housing can look coincident in places).

Known issues:
- Release dates approximated by a fourth-Tuesday rule, not a historical release-timestamp file.
- Daily indicator is a deliberate monthly step function -> serial dependence in daily OLS-style specs.
- STL SA level uses interpolation across any interior gaps before decomposition.

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
    nhs = fetch_fred_hsn1fnsa()
    dm_check = crosscheck_data_master(nhs); print(dm_check)
    spy = fetch_yahoo_close("SPY", "1990-01-01", "2026-07-01", "spy")
    print(f"FRED HSN1FNSA: {len(nhs)} obs, {nhs.index.min().date()} to {nhs.index.max().date()}")
    print(f"SPY: {len(spy)} obs, {spy.index.min().date()} to {spy.index.max().date()}")

    print("\n" + "=" * 72); print("BUILD PANELS"); print("=" * 72)
    monthly = build_monthly(nhs, spy)
    daily = build_daily_lvcf(nhs, spy)
    assert monthly.index.is_monotonic_increasing and daily.index.is_monotonic_increasing
    assert not monthly.index.duplicated().any() and not daily.index.duplicated().any()
    assert daily["days_since_release"].ge(0).all()
    assert daily["nhs_pct_yoy"].loc["2009"].min() < -20.0, "GFC housing collapse missing"
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
