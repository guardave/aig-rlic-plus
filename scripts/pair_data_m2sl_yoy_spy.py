#!/usr/bin/env python3
"""
Data Stage: M2 Money Supply YoY x SPY
====================================

Mode-3 Dana dispatch for pair_id m2sl_yoy_spy.

Authoritative live source: FRED M2SL (M2 Money Stock, monthly, seasonally
adjusted, billions of dollars). The signal is the year-over-year percent
change of M2SL. Data Master.xlsx sheet M2SL is used only as the required
Phase-0/cross-check source.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import urllib.request
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

np.random.seed(42)

ROOT = Path("/workspaces/aig-rlic-plus")
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results/m2sl_yoy_spy"
PWS_DIR = ROOT / "_pws/lead-lesandro/m2sl_yoy"
PAIR_ID = "m2sl_yoy_spy"
INDICATOR = "m2sl_yoy"
TARGET = "spy"
DATE_TAG = "20260619"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def repo_rel(path: Path | str) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def validate_json(schema: str, instance: str) -> None:
    subprocess.run(
        ["python3", "scripts/validate_schema.py", "--schema", schema, "--instance", instance],
        cwd=ROOT,
        check=True,
    )


def fourth_tuesday_next_month(reference_month_end: pd.Timestamp) -> pd.Timestamp:
    """Approximate H.6 monthly release as fourth Tuesday of following month."""
    first_next = (reference_month_end + pd.offsets.MonthBegin(1)).normalize()
    month_days = pd.date_range(first_next, first_next + pd.offsets.MonthEnd(0), freq="D")
    tuesdays = [d for d in month_days if d.weekday() == 1]
    if len(tuesdays) < 4:
        raise RuntimeError(f"Cannot find fourth Tuesday for {first_next:%Y-%m}")
    return tuesdays[3]


def verify_pre_master() -> str:
    pm = pd.read_excel(DATA_DIR / "Data Master.xlsx", sheet_name="Pre-master", header=None, nrows=20)
    level_hits = []
    yoy_hits = []
    for j in range(pm.shape[1]):
        vals = pm.iloc[:10, j].tolist()
        if vals[0] == "M2SL" and vals[2] == "B" and vals[6] == "M2SL":
            level_hits.append(vals)
        if vals[0] == "M2SL" and vals[2] == "C" and vals[6] == "M2SL_YOY":
            yoy_hits.append(vals)
    if not level_hits:
        raise RuntimeError("Phase-0 failed: Pre-master did not map M2SL level to sheet M2SL column B")
    if not yoy_hits:
        raise RuntimeError("Phase-0 failed: Pre-master did not map M2SL_YOY to sheet M2SL column C")
    level_desc = " ".join(str(level_hits[0][1]).split())
    yoy_desc = " ".join(str(yoy_hits[0][1]).split())
    if "M2 Money Supply" not in level_desc or "Federal Reserve" not in level_desc:
        raise RuntimeError(f"Phase-0 failed: unexpected M2SL description: {level_desc!r}")
    if "YoY" not in yoy_desc:
        raise RuntimeError(f"Phase-0 failed: unexpected M2SL_YOY description: {yoy_desc!r}")
    return (
        "PASS: Pre-master maps `M2SL` sheet column B to M2SL level and column C "
        f"to `M2SL_YOY`; descriptions are `{level_desc}` and `{yoy_desc}`."
    )


def fetch_fred_m2sl() -> pd.Series:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2SL"
    last_err = None
    for _ in range(3):
        try:
            df = pd.read_csv(url)
            break
        except Exception as exc:  # pragma: no cover - network retry path
            last_err = exc
    else:
        raise RuntimeError(f"FRED fetch failed for M2SL: {last_err}")
    df = df.rename(columns={"observation_date": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["M2SL"] = pd.to_numeric(df["M2SL"], errors="coerce")
    s = df.dropna(subset=["M2SL"]).set_index("date")["M2SL"].astype(float).sort_index()
    s.index = s.index + pd.offsets.MonthEnd(0)
    s.name = "m2sl_usd"
    if s.index.min() != pd.Timestamp("1959-01-31"):
        raise RuntimeError(f"Unexpected M2SL start: {s.index.min()}")
    if s.index.max() < pd.Timestamp("2026-04-30"):
        raise RuntimeError(f"FRED M2SL is stale: latest {s.index.max().date()}")
    return s


def read_data_master_m2sl() -> pd.DataFrame:
    dm = pd.read_excel(
        DATA_DIR / "Data Master.xlsx",
        sheet_name="M2SL",
        usecols=["date", "M2SL", "M2SL_YOY"],
    ).dropna(subset=["date"])
    dm["date"] = pd.to_datetime(dm["date"]) + pd.offsets.MonthEnd(0)
    return dm.set_index("date").sort_index()


def crosscheck_data_master(m2sl: pd.Series) -> str:
    dm = read_data_master_m2sl()
    yoy = (m2sl / m2sl.shift(12) - 1) * 100.0
    overlap = pd.DataFrame(
        {
            "fred_level": m2sl,
            "fred_yoy": yoy,
            "dm_level": dm["M2SL"],
            "dm_yoy": dm["M2SL_YOY"],
        }
    ).dropna()
    if overlap.empty:
        raise RuntimeError("Data Master cross-check failed: no overlap with FRED M2SL")
    level_diff = (overlap["fred_level"] - overlap["dm_level"]).abs()
    level_pct_diff = level_diff / overlap["fred_level"].abs() * 100.0
    yoy_diff = (overlap["fred_yoy"] - overlap["dm_yoy"]).abs()
    max_level_diff = float(level_diff.max())
    max_level_pct_diff = float(level_pct_diff.max())
    max_yoy_diff = float(yoy_diff.max())
    level_corr = float(overlap["fred_level"].corr(overlap["dm_level"]))
    yoy_corr = float(overlap["fred_yoy"].corr(overlap["dm_yoy"]))
    fred_yoy_delta = overlap["fred_yoy"].diff().dropna()
    dm_yoy_delta = overlap["dm_yoy"].diff().dropna()
    same_shape_rate = float((np.sign(fred_yoy_delta) == np.sign(dm_yoy_delta)).mean())
    same_yoy_sign_rate = float((np.sign(overlap["fred_yoy"]) == np.sign(overlap["dm_yoy"])).mean())
    last = overlap.iloc[-1]
    if level_corr < 0.999:
        raise RuntimeError(f"Data Master cross-check failed shape test: level correlation={level_corr:.6f}")
    if yoy_corr < 0.995 or same_yoy_sign_rate < 0.99 or same_shape_rate < 0.75:
        raise RuntimeError(
            "Data Master cross-check failed YoY shape/sign test: "
            f"YoY correlation={yoy_corr:.6f}, YoY sign agreement={same_yoy_sign_rate:.3f}, "
            f"YoY monthly-change sign agreement={same_shape_rate:.3f}"
        )
    if overlap.index[-1] != pd.Timestamp("2025-08-31"):
        raise RuntimeError(f"Unexpected Data Master last overlap date: {overlap.index[-1].date()}")
    if abs(float(last["dm_level"]) - 22195.4) > 1e-6 or abs(float(last["dm_yoy"]) - 4.76793) > 1e-5:
        raise RuntimeError("Data Master last-row check failed for 2025-08")
    return (
        "PASS (soft): Data Master M2SL overlap agrees in shape/sign with live FRED. "
        f"Level corr={level_corr:.6f}; YoY corr={yoy_corr:.6f}; "
        f"YoY sign agreement={same_yoy_sign_rate:.3f}; monthly-change sign agreement={same_shape_rate:.3f}. "
        f"Revision drift observed: max level diff {max_level_diff:.4f} $bn "
        f"({max_level_pct_diff:.3f}%), max YoY diff {max_yoy_diff:.4f} pp. "
        "This is treated as benign seasonal-adjustment/vintage drift per Lead adjudication; "
        "FRED live M2SL is the source of truth. Last Data Master row is 2025-08-31: "
        "M2SL=22195.4, M2SL_YOY=4.76793%."
    )


def fetch_yahoo_close(ticker: str, start: str, end: str, name: str) -> pd.Series:
    import yfinance as yf

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


def add_m2_transforms(df: pd.DataFrame) -> pd.DataFrame:
    m = df["m2sl_usd"]
    df["m2sl_pct_yoy"] = (m / m.shift(12) - 1) * 100.0
    df["m2sl_pct_mom"] = (m / m.shift(1) - 1) * 100.0
    df["m2sl_3m_pct"] = (m / m.shift(3) - 1) * 100.0
    df["m2sl_6m_pct"] = (m / m.shift(6) - 1) * 100.0
    df["m2sl_yoy_accel_pct"] = df["m2sl_pct_yoy"].diff()
    roll = df["m2sl_pct_yoy"].rolling(120, min_periods=60)
    df["m2sl_yoy_zscore_120m"] = (df["m2sl_pct_yoy"] - roll.mean()) / roll.std()
    df["m2sl_contraction_flag"] = (df["m2sl_pct_yoy"] < 0).astype(float)
    return df


def build_monthly(m2sl: pd.Series, spy: pd.Series) -> pd.DataFrame:
    idx = pd.date_range("1993-01-31", m2sl.index.max(), freq="ME")
    df = pd.DataFrame({"m2sl_usd": m2sl.reindex(idx)}, index=idx)
    df.index.name = "date"
    df = add_m2_transforms(df)
    spy_m = spy.resample("ME").last()
    df["spy"] = spy_m.reindex(df.index)
    df["spy_ret"] = df["spy"].pct_change()
    for h in [1, 3, 6, 12]:
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    return df


def build_daily_lvcf(m2sl: pd.Series, spy: pd.Series) -> pd.DataFrame:
    monthly_all = add_m2_transforms(pd.DataFrame({"m2sl_usd": m2sl.copy()}))
    release_events = monthly_all.reset_index(names="reference_month_end")
    release_events["release_date"] = release_events["reference_month_end"].map(fourth_tuesday_next_month)
    release_events = release_events.sort_values("release_date")

    df = pd.DataFrame(index=spy.index)
    df.index.name = "date"
    df["spy"] = spy
    left = df.reset_index().rename(columns={"date": "trade_date"}).sort_values("trade_date")
    merged = pd.merge_asof(
        left,
        release_events.sort_values("release_date"),
        left_on="trade_date",
        right_on="release_date",
        direction="backward",
    ).set_index("trade_date")
    merged.index.name = "date"
    merged = merged.dropna(subset=["m2sl_pct_yoy"]).copy()
    merged["reference_month_end"] = pd.to_datetime(merged["reference_month_end"])
    merged["release_date"] = pd.to_datetime(merged["release_date"])
    merged["days_since_release"] = (merged.index - merged["release_date"]).dt.days.astype("float64")

    ordered_cols = [
        "spy",
        "reference_month_end",
        "release_date",
        "m2sl_usd",
        "m2sl_pct_yoy",
        "m2sl_pct_mom",
        "m2sl_3m_pct",
        "m2sl_6m_pct",
        "m2sl_yoy_accel_pct",
        "m2sl_yoy_zscore_120m",
        "m2sl_contraction_flag",
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
        "m2sl_usd": monthly["m2sl_usd"],
        "m2sl_pct_yoy": monthly["m2sl_pct_yoy"],
        "m2sl_pct_mom": monthly["m2sl_pct_mom"],
        "m2sl_3m_pct": monthly["m2sl_3m_pct"],
        "m2sl_6m_pct": monthly["m2sl_6m_pct"],
        "m2sl_yoy_accel_pct": monthly["m2sl_yoy_accel_pct"],
        "m2sl_yoy_zscore_120m": monthly["m2sl_yoy_zscore_120m"],
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
                rows.append(
                    {
                        "variable": name,
                        "test": test,
                        "statistic": round(float(obj.stat), 4),
                        "p_value": round(float(obj.pvalue), 4),
                        "lags": int(obj.lags),
                        "n_obs": int(len(x)),
                        "conclusion": conclusion,
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "variable": name,
                        "test": test,
                        "statistic": np.nan,
                        "p_value": np.nan,
                        "lags": np.nan,
                        "n_obs": int(len(x)),
                        "conclusion": f"failed: {exc}",
                    }
                )
    return pd.DataFrame(rows)


def col_meta(col: str, frequency: str) -> tuple[str, str, str, str, str, str, int]:
    meta = {
        "date": ("datetime64[ns]", "date", "Date", "neutral", f"{frequency.title()} date index.", "derived:index", 30),
        "reference_month_end": ("datetime64[ns]", "date", "M2SL Reference Month End", "neutral", "Reference-period month end for the carried M2SL observation.", "FRED:M2SL", 30),
        "release_date": ("datetime64[ns]", "date", "M2SL Release Date", "neutral", "Assumed market availability date: fourth Tuesday of the following month for the prior-month M2SL value.", "FRED:M2SL", 30),
        "days_since_release": ("float64", "count", "Days Since Release", "neutral", "Calendar days since the most recent M2SL release available to the market.", "derived:release_calendar", 30),
        "m2sl_usd": ("float64", "usd", "M2 Money Stock ($bn)", "neutral", "FRED M2SL level, billions of dollars, seasonally adjusted. Included for provenance only; strongly trending and not recommended as a signal.", "FRED:M2SL", 30),
        "m2sl_pct_yoy": ("float64", "pct", "M2 Money Supply YoY (%)", "higher_is_better", "Year-over-year percent change of FRED M2SL; primary canonical indicator signal.", "derived:FRED:M2SL pct_change(12)*100", 30),
        "m2sl_pct_mom": ("float64", "pct", "M2 Money Supply MoM (%)", "higher_is_better", "Month-over-month percent change of FRED M2SL.", "derived:FRED:M2SL pct_change(1)*100", 30),
        "m2sl_3m_pct": ("float64", "pct", "M2 Money Supply 3M Change (%)", "higher_is_better", "Three-month percent change of FRED M2SL.", "derived:FRED:M2SL pct_change(3)*100", 30),
        "m2sl_6m_pct": ("float64", "pct", "M2 Money Supply 6M Change (%)", "higher_is_better", "Six-month percent change of FRED M2SL.", "derived:FRED:M2SL pct_change(6)*100", 30),
        "m2sl_yoy_accel_pct": ("float64", "pct", "M2 YoY Acceleration (pp)", "higher_is_better", "One-month change in M2 YoY growth, in percentage points.", "derived:diff(m2sl_pct_yoy)", 30),
        "m2sl_yoy_zscore_120m": ("float64", "none", "M2 YoY 120M Z-Score", "higher_is_better", "Rolling 120-month z-score of M2 YoY growth, minimum 60 observations.", "derived:rolling_zscore(m2sl_pct_yoy)", 30),
        "m2sl_contraction_flag": ("float64", "none", "M2 YoY Contraction Flag", "lower_is_better", "1.0 when M2 YoY growth is below 0%, marking money-supply contraction.", "derived:m2sl_pct_yoy<0", 30),
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
            "dtype": "datetime64[ns]",
            "unit": "date",
            "display_name": "Date",
            "direction": "neutral",
            "description": f"{frequency.title()} date index; spans {df.index.min().date()} through {df.index.max().date()}.",
        }
    }
    registry = pd.read_csv(DATA_DIR / "display_name_registry.csv")
    registry = registry.set_index("column_name").to_dict("index")
    for col in df.columns:
        dtype, unit, display, direction, desc, source, ttl = col_meta(col, frequency)
        if col in registry and col not in {"reference_month_end", "release_date"}:
            display = registry[col]["display_name"]
            unit = registry[col]["unit"]
        cols[col] = {
            "dtype": str(df[col].dtype) if not pd.api.types.is_datetime64_any_dtype(df[col]) else "datetime64[ns]",
            "unit": unit,
            "display_name": display,
            "direction": direction,
            "description": desc,
            "source_reference": source,
            "refresh_ttl_days": ttl,
        }
    return {
        "pair_id": PAIR_ID,
        "parquet_path": repo_rel(parquet_path),
        "schema_version": "1.0.0",
        "generated_at": NOW_ISO,
        "columns": cols,
    }


def write_data_dictionary(monthly: pd.DataFrame, daily: pd.DataFrame, path: Path, phase0: str, dm_check: str) -> None:
    rows = []
    for frequency, df in [("monthly", monthly), ("daily", daily)]:
        meta = metadata_for_columns(df, frequency, Path(f"data/{PAIR_ID}_{frequency}_placeholder.parquet"))
        for col in ["date"] + list(df.columns):
            m = meta["columns"][col]
            values = df.index if col == "date" else df[col].dropna().index
            is_m2 = col.startswith("m2sl") or col in {"reference_month_end", "release_date", "days_since_release"}
            rows.append(
                {
                    "frequency": frequency,
                    "column_name": col,
                    "display_name": m["display_name"],
                    "description": m["description"],
                    "source": "FRED" if is_m2 else "Yahoo Finance",
                    "series_id": "M2SL" if is_m2 else "SPY",
                    "unit": m["unit"],
                    "transformation": "Monthly level" if col == "m2sl_usd" else ("Monthly-to-daily LVCF from approximate H.6 release date" if frequency == "daily" and is_m2 else "See description"),
                    "seasonal_adj": "Seasonally adjusted" if is_m2 else "N/A",
                    "direction_convention": "Higher M2 growth = liquidity tailwind/procyclical prior for SPY; 0% YoY marks contraction. Level is neutral/provenance only.",
                    "effective_start": str(values.min().date()) if len(values) else "",
                    "known_quirks": f"M2SL level is strongly trending and should not be used as a signal. {phase0} {dm_check}",
                    "display_note": "M2 is a monthly money-stock series. The daily panel only updates after the estimated H.6 release date, so daily values are a step function.",
                    "refresh_freq": "monthly" if is_m2 else "daily",
                    "refresh_source": "FRED M2SL" if is_m2 else "Yahoo Finance",
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False)


def update_display_registry(monthly: pd.DataFrame, daily: pd.DataFrame) -> None:
    reg_path = DATA_DIR / "display_name_registry.csv"
    reg = pd.read_csv(reg_path)
    existing = set(reg["column_name"])
    rows = []
    all_cols = ["date"] + list(dict.fromkeys(list(monthly.columns) + list(daily.columns)))
    axis_overrides = {
        "m2sl_usd": "M2 ($bn)",
        "m2sl_pct_yoy": "M2 YoY (%)",
        "m2sl_pct_mom": "M2 MoM (%)",
        "m2sl_3m_pct": "3M Change (%)",
        "m2sl_6m_pct": "6M Change (%)",
        "m2sl_yoy_accel_pct": "YoY Acceleration (pp)",
        "m2sl_yoy_zscore_120m": "Z-Score",
        "m2sl_contraction_flag": "Contraction (0/1)",
        "reference_month_end": "Reference Month",
        "release_date": "Release Date",
        "days_since_release": "Days Since Release",
    }
    for col in all_cols:
        if col in existing:
            continue
        _, unit, display, _, _, _, _ = col_meta(col, "daily")
        rows.append(
            {
                "column_name": col,
                "display_name": display,
                "unit": unit,
                "axis_label": axis_overrides.get(col, display),
            }
        )
    if rows:
        reg = pd.concat([reg, pd.DataFrame(rows)], ignore_index=True)
    reg.loc[reg["column_name"] == "days_since_release", ["display_name", "axis_label"]] = ["Days Since Release", "Days Since Release"]
    reg.loc[reg["column_name"] == "reference_month_end", ["display_name", "axis_label"]] = ["Reference Month End", "Reference Month End"]
    reg.loc[reg["column_name"] == "release_date", ["display_name", "axis_label"]] = ["Release Date", "Release Date"]
    reg.to_csv(reg_path, index=False, lineterminator="\n")

    obj = {
        "schema_version": "1.0.0",
        "generated_at": NOW_ISO,
        "columns": reg[["column_name", "display_name", "unit", "axis_label"]].to_dict("records"),
    }
    (DATA_DIR / "display_name_registry.json").write_text(json.dumps(obj, indent=2) + "\n")


def update_manifest(monthly_path: Path, monthly_latest: Path, daily_path: Path, daily_latest: Path) -> None:
    manifest_path = DATA_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    artifacts = [a for a in manifest["artifacts"] if PAIR_ID not in a.get("path", "")]
    last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = {
        "source": "FRED:M2SL (monthly SA money stock, $bn) + yahoo:SPY",
        "refresh_ttl_days": 1,
        "last_updated": last_updated,
        "pairs": [PAIR_ID],
        "mixed_freq_ttl_note": "Monthly M2SL indicator plus daily SPY market data; TTL=1 per fastest-refreshing component. The indicator itself changes monthly after the H.6 release.",
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


def write_missing_report(monthly: pd.DataFrame, daily: pd.DataFrame, phase0: str, dm_check: str, path: Path) -> None:
    lines = [
        f"# Missing Value Report - {PAIR_ID} ({DATE_TAG})",
        "",
        f"Monthly dataset: shape {monthly.shape}, {monthly.index.min().date()} to {monthly.index.max().date()}.",
        f"Daily dataset: shape {daily.shape}, {daily.index.min().date()} to {daily.index.max().date()}.",
        "",
        "## Phase 0 / Cross-Check",
        "",
        phase0,
        dm_check,
        "",
        "## Real-Time Lag",
        "",
        "Daily LVCF uses release dates set to the fourth Tuesday of the month following the reference month, approximating the FRED/H.6 M2 release schedule for prior-month data. This implies a no-lookahead floor of roughly 22-28 calendar days after reference month-end.",
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
    lines.extend(
        [
            "",
            "The daily indicator is an intentional release-lagged step function; `days_since_release` documents staleness. The SPY feed returned a missing adjusted close for 2026-06-18 during this run, so the daily panel ends on the last non-missing adjusted close.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def write_interpretation_metadata(path: Path) -> None:
    meta = {
        "pair_id": PAIR_ID,
        "schema_version": "1.1.0",
        "indicator": INDICATOR,
        "target": TARGET,
        "indicator_nature": "leading",
        "indicator_type": "macro",
        "strategy_objective": "max_sharpe",
        "expected_direction": "procyclical",
        "data_provenance": {
            "source": "FRED M2SL live API; Data Master.xlsx sheet M2SL used as overlap cross-check through 2025-08",
            "series_id": "M2SL",
            "accessed_at": NOW_ISO,
        },
        "known_stress_episodes": [
            {
                "label": "COVID money surge",
                "start": "2020-03-01",
                "end": "2021-03-31",
                "note": "M2 YoY growth surged to roughly 27% during pandemic liquidity support.",
            },
            {
                "label": "First modern M2 YoY contraction",
                "start": "2022-12-01",
                "end": "2023-12-31",
                "note": "M2 YoY growth fell below 0%, an economically meaningful contraction threshold.",
            },
        ],
        "related_pair_ids": ["busloans_spy", "hy_ig_spy", "dff_ted_spy"],
        "owner_writes": {
            "dana": [
                "pair_id",
                "schema_version",
                "indicator",
                "target",
                "indicator_nature",
                "indicator_type",
                "data_provenance",
                "known_stress_episodes",
                "related_pair_ids",
            ],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "expected_direction", "mechanism", "caveats", "narrative_summary"],
        },
        "last_updated_by": "dana",
        "last_updated_at": NOW_ISO,
    }
    path.write_text(json.dumps(meta, indent=2) + "\n")


def stationarity_verdict(stat: pd.DataFrame) -> str:
    lines = []
    for var in ["m2sl_usd", "m2sl_pct_yoy", "m2sl_pct_mom", "m2sl_3m_pct", "m2sl_6m_pct", "m2sl_yoy_accel_pct", "m2sl_yoy_zscore_120m"]:
        sub = stat[stat["variable"] == var]
        adf = sub[sub["test"] == "ADF"].iloc[0]
        kpss = sub[sub["test"] == "KPSS"].iloc[0]
        lines.append(
            f"- `{var}`: ADF p={adf.p_value:.4f} ({adf.conclusion}); KPSS p={kpss.p_value:.4f} ({kpss.conclusion})."
        )
    return "\n".join(lines)


def write_handoff(
    path: Path,
    phase0: str,
    dm_check: str,
    monthly_path: Path,
    daily_path: Path,
    stationarity_path: Path,
    monthly: pd.DataFrame,
    daily: pd.DataFrame,
    stat: pd.DataFrame,
) -> None:
    text = f"""Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/m2sl_yoy_spy_monthly_latest.parquet` (source dated file `{repo_rel(monthly_path)}`)
- Daily LVCF dataset: `data/m2sl_yoy_spy_daily_latest.parquet` (source dated file `{repo_rel(daily_path)}`)
- Monthly sidecar: `data/m2sl_yoy_spy_monthly_schema.json`
- Daily sidecar: `data/m2sl_yoy_spy_daily_schema.json`
- Data dictionary: `data/data_dictionary_m2sl_yoy_spy_{DATE_TAG}.csv`
- Missing-value report: `data/missing_value_report_m2sl_yoy_spy_{DATE_TAG}.md`
- Stationarity: `{repo_rel(stationarity_path)}`
- Interpretation metadata: `results/m2sl_yoy_spy/interpretation_metadata.json`

Summary:
Built the M2 Money Supply YoY -> SPY data layer from live FRED M2SL. The monthly panel is {monthly.shape[0]} rows x {monthly.shape[1]} columns, {monthly.index.min().date()} to {monthly.index.max().date()}. The daily panel is {daily.shape[0]} SPY trading days x {daily.shape[1]} columns, {daily.index.min().date()} to {daily.index.max().date()}, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
{phase0}
{dm_check}
FRED live M2SL currently runs {monthly['m2sl_usd'].dropna().index.min().date()} to {monthly['m2sl_usd'].dropna().index.max().date()} in this delivered panel; full source history starts 1959-01.

Units and direction prior:
`m2sl_pct_yoy` is percent YoY, computed as `(M2SL / M2SL.shift(12) - 1) * 100`. Direction prior for Evan: procyclical/liquidity tailwind for SPY. Important counter-channel: rapid money growth can also presage inflation and policy tightening. The 0% line is economically meaningful: below zero is outright M2 contraction. `m2sl_usd` is included for provenance only and should not be used as a signal.

Release lag floor:
Daily LVCF assumes prior-month M2SL is released on the fourth Tuesday of the following month. This creates a real-time no-lookahead floor of roughly 22-28 calendar days after reference month-end. Do not use month-end M2 values as if known at month-end; use the daily panel's release-date carry-forward and `days_since_release`.

Stationarity:
{stationarity_verdict(stat)}

Recommendation:
Do not use the M2SL level as a signal. Prefer `m2sl_yoy_accel_pct` as the cleanest primary transform where stationarity matters; use `m2sl_pct_yoy`, `m2sl_pct_mom`, `m2sl_3m_pct`, `m2sl_6m_pct`, and `m2sl_yoy_zscore_120m` as robustness candidates, with explicit regime controls for the COVID surge and 2022-23 contraction period. Treat `m2sl_contraction_flag` as a threshold/regime feature.

Known issues:
- Release dates are approximated by a fourth-Tuesday rule, not a historical release timestamp file.
- Daily indicator values are a deliberate monthly step function and will induce serial dependence in daily OLS-style specifications.
- The SPY feed returned a missing adjusted close for 2026-06-18 during this run; that row was dropped, so the daily panel ends at the last non-missing adjusted close.

Questions for recipient:
- None. Evan should set the no-lookahead lead-grid floor at one monthly publication lag (minimum L1 monthly, or daily horizons after release-date carry-forward).
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PWS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("PHASE 0: DATA MASTER VERIFICATION")
    print("=" * 72)
    phase0 = verify_pre_master()
    print(phase0)

    print("\n" + "=" * 72)
    print("SOURCING")
    print("=" * 72)
    m2sl = fetch_fred_m2sl()
    dm_check = crosscheck_data_master(m2sl)
    print(dm_check)
    spy = fetch_yahoo_close("SPY", "1993-01-01", "2026-06-20", "spy")
    print(f"FRED M2SL: {len(m2sl)} obs, {m2sl.index.min().date()} to {m2sl.index.max().date()}")
    print(f"SPY: {len(spy)} obs, {spy.index.min().date()} to {spy.index.max().date()}")

    print("\n" + "=" * 72)
    print("BUILD PANELS")
    print("=" * 72)
    monthly = build_monthly(m2sl, spy)
    daily = build_daily_lvcf(m2sl, spy)
    assert monthly.index.is_monotonic_increasing and daily.index.is_monotonic_increasing
    assert not monthly.index.duplicated().any() and not daily.index.duplicated().any()
    assert daily["days_since_release"].ge(0).all()
    assert daily["m2sl_pct_yoy"].loc["2020"].max() > 20.0, "COVID M2 surge missing"
    assert daily["m2sl_pct_yoy"].loc["2023"].min() < 0.0, "2022-23 M2 contraction missing"
    print(f"Monthly: {monthly.shape}, {monthly.index.min().date()} to {monthly.index.max().date()}")
    print(f"Daily:   {daily.shape}, {daily.index.min().date()} to {daily.index.max().date()}")

    print("\n" + "=" * 72)
    print("STATIONARITY")
    print("=" * 72)
    stat = run_stationarity(monthly)
    stat_path = RESULTS_DIR / f"stationarity_tests_{DATE_TAG}.csv"
    stat.to_csv(stat_path, index=False)
    print(stat.to_string(index=False))

    print("\n" + "=" * 72)
    print("WRITE ARTIFACTS")
    print("=" * 72)
    m_start, m_end = monthly.index.min().strftime("%Y%m%d"), monthly.index.max().strftime("%Y%m%d")
    d_start, d_end = daily.index.min().strftime("%Y%m%d"), daily.index.max().strftime("%Y%m%d")
    monthly_path = DATA_DIR / f"{PAIR_ID}_monthly_{m_start}_{m_end}.parquet"
    daily_path = DATA_DIR / f"{PAIR_ID}_daily_{d_start}_{d_end}.parquet"
    monthly_latest = DATA_DIR / f"{PAIR_ID}_monthly_latest.parquet"
    daily_latest = DATA_DIR / f"{PAIR_ID}_daily_latest.parquet"
    monthly.to_parquet(monthly_path)
    daily.to_parquet(daily_path)
    shutil.copy2(monthly_path, monthly_latest)
    shutil.copy2(daily_path, daily_latest)

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

    print("\n" + "=" * 72)
    print("VALIDATE")
    print("=" * 72)
    validate_json("docs/schemas/data_subject.schema.json", repo_rel(monthly_schema_path))
    validate_json("docs/schemas/data_subject.schema.json", repo_rel(daily_schema_path))
    validate_json("docs/schemas/interpretation_metadata.schema.json", repo_rel(meta_path))
    validate_json("docs/schemas/data_manifest.schema.json", "data/manifest.json")
    validate_json("docs/schemas/display_name_registry.schema.json", "data/display_name_registry.json")

    print("\nDANA DONE")
    for artifact in [
        monthly_path,
        monthly_latest,
        daily_path,
        daily_latest,
        monthly_schema_path,
        daily_schema_path,
        dict_path,
        DATA_DIR / f"summary_stats_{PAIR_ID}_monthly_{DATE_TAG}.csv",
        DATA_DIR / f"summary_stats_{PAIR_ID}_daily_{DATE_TAG}.csv",
        mv_path,
        stat_path,
        meta_path,
        handoff_path,
        DATA_DIR / "manifest.json",
        DATA_DIR / "display_name_registry.csv",
        DATA_DIR / "display_name_registry.json",
        DATA_DIR / "prospective_pairs.csv",
    ]:
        print(f"- {repo_rel(artifact)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nDANA BLOCKED: {exc}")
        raise
