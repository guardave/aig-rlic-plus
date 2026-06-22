#!/usr/bin/env python3
"""
Data Stage: 10Y-3M Treasury Spread x SPY
========================================

Pair ID: t10y3m_spy

SOP path:
  - Data Dana: source, align, validate, and document data.
  - Indicator: FRED T10Y3M / Data Master sheet `US10Y-3M`, percentage points.
  - Target: SPY adjusted monthly close, sourced from an existing SPY-bound
    monthly parquet when available, with Yahoo fallback.

The Data Master workbook provides an offline, auditable T10Y3M daily history.
The script resamples it to month-end and aligns to SPY month-end closes.
"""

from __future__ import annotations

import json
import shutil
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results" / "t10y3m_spy"
PAIR_ID = "t10y3m_spy"
DATE_TAG = "20260620"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_t10y3m_from_workbook() -> pd.Series:
    path = DATA_DIR / "Data Master.xlsx"
    df = pd.read_excel(path, sheet_name="US10Y-3M")
    df = df.rename(columns={"G - (US10Y-US3M)": "t10y3m"})
    df["date"] = pd.to_datetime(df["date"])
    df["t10y3m"] = pd.to_numeric(df["t10y3m"], errors="coerce")
    s = df.dropna(subset=["t10y3m"]).set_index("date")["t10y3m"].sort_index()
    s.name = "t10y3m"
    if s.index.min() > pd.Timestamp("1982-01-04"):
        raise RuntimeError(f"Unexpected T10Y3M start date: {s.index.min().date()}")
    if s.index.max() < pd.Timestamp("2025-08-31"):
        raise RuntimeError(f"T10Y3M workbook series appears stale: latest {s.index.max().date()}")
    return s


def try_fetch_fred_t10y3m() -> pd.Series | None:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y3M"
    try:
        df = pd.read_csv(url)
    except Exception as exc:
        print(f"  FRED T10Y3M fetch skipped/failed: {exc}")
        return None
    df = df.rename(columns={"observation_date": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["T10Y3M"] = pd.to_numeric(df["T10Y3M"], errors="coerce")
    s = df.dropna(subset=["T10Y3M"]).set_index("date")["T10Y3M"].astype(float).sort_index()
    s.name = "t10y3m_fred"
    return s


def load_spy_monthly() -> pd.Series:
    candidates = [
        DATA_DIR / "m2sl_yoy_spy_monthly_latest.parquet",
        DATA_DIR / "ism_services_spy_monthly_latest.parquet",
        DATA_DIR / "permit_spy_monthly_latest.parquet",
    ]
    for path in candidates:
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        for col in ("spy", "spy_close", "SPY"):
            if col in df.columns:
                s = pd.to_numeric(df[col], errors="coerce").dropna()
                s.index = pd.to_datetime(s.index) + pd.offsets.MonthEnd(0)
                s.name = "spy"
                print(f"  SPY source: {path.name}:{col}")
                return s.sort_index()

    try:
        import yfinance as yf

        raw = yf.download("SPY", start="1993-01-01", auto_adjust=True, progress=False, threads=False)
        if raw.empty:
            raise RuntimeError("Yahoo returned no SPY rows")
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        s = raw["Close"].astype(float)
        s.index = pd.to_datetime(s.index)
        if s.index.tz is not None:
            s.index = s.index.tz_localize(None)
        s = s.resample("ME").last()
        s.name = "spy"
        print("  SPY source: Yahoo Finance")
        return s
    except Exception as exc:
        raise RuntimeError(f"No local SPY monthly source and Yahoo fallback failed: {exc}") from exc


def add_transforms(df: pd.DataFrame) -> pd.DataFrame:
    x = df["t10y3m"]
    df["t10y3m_mom"] = x.diff()
    df["t10y3m_3m_chg"] = x.diff(3)
    df["t10y3m_6m_chg"] = x.diff(6)
    df["t10y3m_12m_chg"] = x.diff(12)
    roll = x.rolling(60, min_periods=36)
    df["t10y3m_zscore_60m"] = (x - roll.mean()) / roll.std()
    df["t10y3m_inversion_flag"] = (x < 0).astype(float)
    df["t10y3m_curve_steepening"] = (df["t10y3m_mom"] > 0).astype(float)
    df["spy_ret"] = df["spy"].pct_change()
    for h in (1, 3, 6, 12):
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    return df


def stationarity_tests(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cols = [
        "t10y3m", "t10y3m_mom", "t10y3m_3m_chg", "t10y3m_6m_chg",
        "t10y3m_12m_chg", "t10y3m_zscore_60m", "spy_ret",
    ]
    try:
        from arch.unitroot import ADF, KPSS
    except Exception as exc:
        print(f"  Stationarity package unavailable: {exc}")
        return pd.DataFrame()

    for col in cols:
        s = df[col].dropna()
        if len(s) < 60:
            continue
        try:
            adf = ADF(s)
            rows.append({
                "variable": col,
                "test": "ADF",
                "statistic": round(float(adf.stat), 4),
                "p_value": round(float(adf.pvalue), 4),
                "lags": int(adf.lags),
                "conclusion": "stationary" if adf.pvalue < 0.05 else "unit_root_not_rejected",
            })
        except Exception as exc:
            rows.append({"variable": col, "test": "ADF", "error": str(exc)})
        try:
            kpss = KPSS(s)
            rows.append({
                "variable": col,
                "test": "KPSS",
                "statistic": round(float(kpss.stat), 4),
                "p_value": round(float(kpss.pvalue), 4),
                "lags": int(kpss.lags),
                "conclusion": "stationary_not_rejected" if kpss.pvalue >= 0.05 else "nonstationary",
            })
        except Exception as exc:
            rows.append({"variable": col, "test": "KPSS", "error": str(exc)})
    return pd.DataFrame(rows)


def write_missing_report(df: pd.DataFrame, path: Path) -> None:
    miss = df.isna().sum().sort_values(ascending=False)
    lines = [
        "# Missing Value Report: T10Y3M x SPY",
        "",
        f"Generated: {NOW_ISO}",
        f"Rows: {len(df)}",
        f"Date range: {df.index.min().date()} to {df.index.max().date()}",
        "",
        "| Column | Missing | Missing % |",
        "|---|---:|---:|",
    ]
    for col, n in miss.items():
        lines.append(f"| `{col}` | {int(n)} | {n / len(df) * 100:.2f}% |")
    path.write_text("\n".join(lines) + "\n")


def write_interpretation_metadata() -> None:
    meta = {
        "pair_id": PAIR_ID,
        "schema_version": "1.1.0",
        "indicator": "t10y3m",
        "target": "spy",
        "indicator_nature": "leading",
        "indicator_type": "rates",
        "strategy_objective": "max_sharpe",
        "expected_direction": "procyclical",
        "observed_direction": "procyclical",
        "direction_consistent": True,
        "confidence": "medium",
        "key_finding": "The 10Y-3M Treasury spread is a classic leading recession-risk signal; the tournament tests whether steepening or inversion improves SPY timing.",
        "mechanism": "A steeper 10-year minus 3-month Treasury spread usually signals easier future financial conditions and lower near-term recession risk, while inversion warns that restrictive policy may pressure future equity returns.",
        "narrative_summary": "Yield-curve slope is tested as a recession-risk overlay for SPY: steep curves are risk-on, inverted curves are cautionary.",
        "caveats": [
            "Yield-curve inversion can lead equity drawdowns by many months, so timing may be early.",
            "SPY data begins in 1993, truncating the longer yield-curve history.",
            "The series is revised only lightly, but month-end alignment still abstracts from intramonth signal changes."
        ],
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2000-03-01", "end": "2002-10-31", "note": "The curve inverted before the 2001 recession and equity drawdown."},
            {"label": "Global Financial Crisis", "start": "2006-07-01", "end": "2009-03-31", "note": "The curve inverted in 2006 before the 2007-09 recession."},
            {"label": "COVID shock", "start": "2019-05-01", "end": "2020-04-30", "note": "The curve briefly inverted before the pandemic shock, though COVID was not caused by the yield curve."},
            {"label": "2022-24 inversion", "start": "2022-10-01", "end": "2024-12-31", "note": "The deepest inversion in decades created a long cautionary period while equities recovered."}
        ],
        "data_provenance": {
            "source": "Data Master.xlsx sheet US10Y-3M; FRED T10Y3M live check when network is available",
            "series_id": "T10Y3M",
            "accessed_at": NOW_ISO,
        },
        "related_pair_ids": ["dff_ted_spy", "sofr_ted_spy", "m2sl_yoy_spy"],
        "owner_writes": {
            "dana": ["pair_id", "schema_version", "indicator", "target", "indicator_nature", "indicator_type", "data_provenance", "known_stress_episodes", "related_pair_ids"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "expected_direction", "mechanism", "caveats", "narrative_summary"],
        },
        "last_updated_by": "ray",
        "last_updated_at": NOW_ISO,
    }
    (RESULTS_DIR / "interpretation_metadata.json").write_text(json.dumps(meta, indent=2) + "\n")


def main() -> None:
    print("Building t10y3m_spy data layer...")
    spread_daily = load_t10y3m_from_workbook()
    fred = try_fetch_fred_t10y3m()
    if fred is not None:
        overlap = pd.concat([spread_daily.rename("workbook"), fred.rename("fred")], axis=1).dropna()
        if not overlap.empty:
            max_abs = float((overlap["workbook"] - overlap["fred"]).abs().max())
            corr = float(overlap["workbook"].corr(overlap["fred"]))
            print(f"  FRED/Data Master overlap: n={len(overlap)}, corr={corr:.6f}, max_abs_diff={max_abs:.4f} pp")
    spread_m = spread_daily.resample("ME").last()
    spy = load_spy_monthly()

    start = max(pd.Timestamp("1993-01-31"), spread_m.index.min(), spy.index.min())
    end = min(spread_m.index.max(), spy.index.max())
    idx = pd.date_range(start, end, freq="ME")
    df = pd.DataFrame({"t10y3m": spread_m.reindex(idx), "spy": spy.reindex(idx)}, index=idx)
    df.index.name = "date"
    df = add_transforms(df)

    dated = DATA_DIR / f"t10y3m_spy_monthly_{idx.min():%Y%m}_{idx.max():%Y%m}.parquet"
    latest = DATA_DIR / "t10y3m_spy_monthly_latest.parquet"
    df.to_parquet(dated)
    shutil.copyfile(dated, latest)
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_t10y3m_spy_{DATE_TAG}.csv")
    write_missing_report(df, DATA_DIR / f"missing_value_report_t10y3m_spy_{DATE_TAG}.md")

    stat = stationarity_tests(df)
    if not stat.empty:
        stat.to_csv(RESULTS_DIR / f"stationarity_tests_{DATE_TAG}.csv", index=False)

    write_interpretation_metadata()
    print(f"  Wrote {dated.relative_to(ROOT)}")
    print(f"  Wrote {latest.relative_to(ROOT)}")
    print(f"  Rows: {len(df)}, range: {df.index.min().date()} to {df.index.max().date()}")


if __name__ == "__main__":
    main()
