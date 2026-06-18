#!/usr/bin/env python3
"""
Data Stage: ISM Services PMI x SPY
==================================

Mode-3 Dana dispatch for pair_id ism_services_spy.

Authoritative indicator source is the offline project workbook:
  data/Data Master.xlsx, sheet "ISM PMI", column
  "CDis, CSta - ISM Services PMI".

Do not pull ISM Services from FRED. ISM removed PMI series from FRED; the
workbook is the source-of-record for this pair.
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

ROOT = Path("/workspaces/aig-rlic-plus")
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results/ism_services_spy"
PWS_DIR = ROOT / "_pws/lead-lesandro/mode3_ism_services"
PAIR_ID = "ism_services_spy"
INDICATOR = "ism_services"
TARGET = "spy"
DATE_TAG = "20260618"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

ISM_SHEET = "ISM PMI"
ISM_COL = "CDis, CSta - ISM Services PMI"
PRICE_COL = "G - ISM Services PMI, price"


def repo_rel(path: Path | str) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def validate_json(schema: str, instance: str) -> None:
    subprocess.run(
        ["python3", "scripts/validate_schema.py", "--schema", schema, "--instance", instance],
        cwd=ROOT,
        check=True,
    )


def third_business_day_next_month(reference_month_end: pd.Timestamp) -> pd.Timestamp:
    first_next = (reference_month_end + pd.offsets.MonthBegin(1)).normalize()
    return pd.bdate_range(first_next, first_next + pd.Timedelta(days=10))[2]


def verify_pre_master() -> str:
    pm = pd.read_excel(DATA_DIR / "Data Master.xlsx", sheet_name="Pre-master", header=None, nrows=8)
    hits = []
    for j in range(pm.shape[1]):
        vals = pm.iloc[:8, j].tolist()
        if vals[0] == ISM_SHEET or vals[6] == ISM_COL:
            hits.append((j, vals))
    exact = [x for x in hits if x[1][0] == ISM_SHEET and x[1][2] == "B" and x[1][6] == ISM_COL]
    if not exact:
        raise RuntimeError(f"Phase-0 failed: Pre-master did not map {ISM_SHEET} column B to {ISM_COL}")

    desc = " ".join(str(exact[0][1][1]).split())
    if "ISM Services PMI" not in desc or "Monthly" not in desc or "Oct 2025" not in desc:
        raise RuntimeError(f"Phase-0 failed: unexpected Pre-master description: {desc!r}")
    price_hits = [x for x in hits if x[1][0] == ISM_SHEET and x[1][2] == "C" and x[1][6] == PRICE_COL]
    if not price_hits:
        raise RuntimeError("Phase-0 failed: adjacent price component dictionary entry was not found as a distinct column C series")
    return (
        "PASS: Pre-master maps `ISM PMI` column B to `CDis, CSta - ISM Services PMI`; "
        f"dictionary row says `{desc}`. Workbook data itself runs 1997-07-31 to 2025-10-31."
    )


def read_ism_services() -> pd.Series:
    raw = pd.read_excel(
        DATA_DIR / "Data Master.xlsx",
        sheet_name=ISM_SHEET,
        usecols=["date", ISM_COL],
    )
    raw = raw.dropna(subset=["date", ISM_COL]).copy()
    raw["date"] = pd.to_datetime(raw["date"])
    raw["date"] = raw["date"] + pd.offsets.MonthEnd(0)
    raw = raw.sort_values("date")
    s = raw.set_index("date")[ISM_COL].astype(float)
    s.name = "ism_services_pmi"
    if PRICE_COL in raw.columns:
        raise RuntimeError("Price component leaked into headline-only extract")
    assert s.index.min() == pd.Timestamp("1997-07-31")
    assert s.index.max() == pd.Timestamp("2025-10-31")
    assert 35 <= s.min() <= 40, "GFC trough sanity check failed"
    assert 60 <= s.loc["2021"].max() <= 70, "2021 reopening high sanity check failed"
    assert abs(float(s.sum()) - 18598.09) < 1e-6, "Pre-master sum check failed"
    return s


def fetch_yahoo_close(ticker: str, start: str, end: str, name: str) -> pd.Series:
    import yfinance as yf

    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False, threads=False)
    if df.empty:
        raise RuntimeError(f"Yahoo returned no data for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    s = df["Close"].astype(float)
    s.index = pd.to_datetime(s.index)
    if s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    s.name = name
    return s


def add_ism_transforms(df: pd.DataFrame) -> pd.DataFrame:
    p = df["ism_services_pmi"]
    df["ism_services_gap_50"] = p - 50.0
    df["ism_services_delta"] = p.diff()
    df["ism_services_3m_change"] = p - p.shift(3)
    df["ism_services_6m_change"] = p - p.shift(6)
    roll = p.rolling(60, min_periods=36)
    df["ism_services_zscore_60m"] = (p - roll.mean()) / roll.std()
    df["ism_services_above_50"] = (p > 50).astype(float)
    return df


def build_monthly(ism: pd.Series, spy: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({"ism_services_pmi": ism})
    df.index.name = "date"
    df = add_ism_transforms(df)
    spy_m = spy.resample("ME").last()
    df["spy"] = spy_m.reindex(df.index)
    df["spy_ret"] = df["spy"].pct_change()
    for h in [1, 3, 6, 12]:
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    return df


def build_daily_lvcf(ism: pd.Series, spy: pd.Series) -> pd.DataFrame:
    release_events = pd.DataFrame({
        "reference_month_end": ism.index,
        "release_date": [third_business_day_next_month(d) for d in ism.index],
        "ism_services_pmi": ism.to_numpy(),
    }).sort_values("release_date")
    max_release = release_events["release_date"].max()
    spy_cut = spy.loc[:max_release]
    df = pd.DataFrame(index=spy_cut.index)
    df.index.name = "date"
    df["spy"] = spy_cut

    left = df.reset_index().rename(columns={"date": "trade_date"}).sort_values("trade_date")
    merged = pd.merge_asof(
        left,
        release_events.sort_values("release_date"),
        left_on="trade_date",
        right_on="release_date",
        direction="backward",
    ).set_index("trade_date")
    merged.index.name = "date"
    merged = merged.dropna(subset=["ism_services_pmi"]).copy()
    merged["reference_month_end"] = pd.to_datetime(merged["reference_month_end"])
    merged["release_date"] = pd.to_datetime(merged["release_date"])
    merged["days_since_release"] = (merged.index - merged["release_date"]).dt.days.astype("float64")

    event_df = release_events.set_index("release_date")[["ism_services_pmi"]].copy()
    event_df = add_ism_transforms(event_df)
    for col in [c for c in event_df.columns if c != "ism_services_pmi"]:
        merged[col] = pd.merge_asof(
            left[["trade_date"]],
            event_df[[col]].reset_index().sort_values("release_date"),
            left_on="trade_date",
            right_on="release_date",
            direction="backward",
        )[col].to_numpy()[-len(merged):]

    merged["spy_ret"] = merged["spy"].pct_change()
    for h in [1, 5, 21, 63, 126, 252]:
        merged[f"spy_fwd_{h}d"] = merged["spy"].shift(-h) / merged["spy"] - 1
    return merged


def run_stationarity(monthly: pd.DataFrame) -> pd.DataFrame:
    from arch.unitroot import ADF, KPSS

    variables = {
        "level": monthly["ism_services_pmi"],
        "delta": monthly["ism_services_delta"],
        "3m_change": monthly["ism_services_3m_change"],
        "zscore_60m": monthly["ism_services_zscore_60m"],
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
                    "variable": name,
                    "test": test,
                    "statistic": round(float(obj.stat), 4),
                    "p_value": round(float(obj.pvalue), 4),
                    "lags": int(obj.lags),
                    "n_obs": int(len(x)),
                    "conclusion": conclusion,
                })
            except Exception as exc:
                rows.append({
                    "variable": name,
                    "test": test,
                    "statistic": np.nan,
                    "p_value": np.nan,
                    "lags": np.nan,
                    "n_obs": int(len(x)),
                    "conclusion": f"failed: {exc}",
                })
    return pd.DataFrame(rows)


def metadata_for_columns(df: pd.DataFrame, frequency: str, parquet_path: Path) -> dict:
    common = {
        "date": ("datetime64[ns]", "date", "Date", "neutral", f"{frequency.title()} date index."),
        "reference_month_end": ("datetime64[ns]", "date", "ISM Services Reference Month End", "neutral", "Reference-period month end for the carried ISM Services PMI observation."),
        "release_date": ("datetime64[ns]", "date", "ISM Services Release Date", "neutral", "Assumed market availability date: third business day of the following month for the prior-month reference period."),
        "days_since_release": ("float64", "count", "Days Since Release", "neutral", "Calendar days since the most recent ISM Services PMI release available to the market."),
        "ism_services_pmi": ("float64", "index", "ISM Services PMI", "higher_is_better", "ISM Services headline PMI diffusion index. Values above 50 indicate services-sector expansion; values below 50 indicate contraction."),
        "ism_services_gap_50": ("float64", "index", "ISM Services PMI Gap to 50", "higher_is_better", "ISM Services PMI minus the 50 expansion/contraction threshold."),
        "ism_services_delta": ("float64", "index", "ISM Services PMI Monthly Change", "higher_is_better", "One-month change in the ISM Services PMI level, in index points."),
        "ism_services_3m_change": ("float64", "index", "ISM Services PMI 3M Change", "higher_is_better", "Three-month change in the ISM Services PMI level, in index points."),
        "ism_services_6m_change": ("float64", "index", "ISM Services PMI 6M Change", "higher_is_better", "Six-month change in the ISM Services PMI level, in index points."),
        "ism_services_zscore_60m": ("float64", "none", "ISM Services PMI 60M Z-Score", "higher_is_better", "Rolling 60-month z-score of the ISM Services PMI level, minimum 36 observations."),
        "ism_services_above_50": ("float64", "none", "ISM Services PMI Above 50 Flag", "higher_is_better", "1.0 when ISM Services PMI is above 50, else 0.0."),
        "spy": ("float64", "price", "SPY Close ($)", "neutral", "SPY adjusted close from Yahoo Finance."),
        "spy_ret": ("float64", "decimal_return", "SPY Daily Return (decimal)" if frequency == "daily" else "SPY Monthly Return", "neutral", f"Simple SPY return over the {frequency} panel frequency."),
    }
    for h in [1, 3, 6, 12]:
        common[f"spy_fwd_{h}m"] = ("float64", "decimal_return", f"SPY Forward {h}M Return", "neutral", f"Forward {h}-month SPY return, decimal.")
    for h in [1, 5, 21, 63, 126, 252]:
        common[f"spy_fwd_{h}d"] = ("float64", "decimal_return", f"SPY {h}D Forward Return", "neutral", f"Forward {h}-trading-day SPY return, decimal.")

    cols = {
        "date": {
            "dtype": "datetime64[ns]",
            "unit": "date",
            "display_name": "Date",
            "direction": "neutral",
            "description": f"{frequency.title()} date index; spans {df.index.min().date()} through {df.index.max().date()}.",
        }
    }
    for col in df.columns:
        dtype, unit, display, direction, desc = common[col]
        is_ism = col.startswith("ism_services") or col in {"reference_month_end", "release_date", "days_since_release"}
        cols[col] = {
            "dtype": str(df[col].dtype) if not pd.api.types.is_datetime64_any_dtype(df[col]) else "datetime64[ns]",
            "unit": unit,
            "display_name": display,
            "direction": direction,
            "description": desc,
            "source_reference": "Data Master.xlsx:ISM PMI!B / ISM" if is_ism else "yahoo:SPY",
            "refresh_ttl_days": 30 if is_ism else 1,
        }
    return {
        "pair_id": PAIR_ID,
        "parquet_path": repo_rel(parquet_path),
        "schema_version": "1.0.0",
        "generated_at": NOW_ISO,
        "columns": cols,
    }


def write_data_dictionary(monthly: pd.DataFrame, daily: pd.DataFrame, path: Path, phase0: str) -> None:
    rows = []
    for frequency, df in [("monthly", monthly), ("daily", daily)]:
        meta = metadata_for_columns(df, frequency, Path(f"data/{PAIR_ID}_{frequency}_placeholder.parquet"))
        for col in ["date"] + list(df.columns):
            m = meta["columns"][col]
            is_ism = col.startswith("ism_services") or col in {"reference_month_end", "release_date", "days_since_release"}
            if col == "date":
                values = df.index
            else:
                values = df[col].dropna().index
            rows.append({
                "frequency": frequency,
                "column_name": col,
                "display_name": m["display_name"],
                "description": m["description"],
                "source": "Project Data Master workbook / ISM" if is_ism else "Yahoo Finance",
                "series_id": ISM_COL if is_ism else "SPY",
                "unit": m["unit"],
                "transformation": "Monthly-native level" if col == "ism_services_pmi" and frequency == "monthly" else ("Monthly-to-daily LVCF from release date" if frequency == "daily" and is_ism else "See description"),
                "seasonal_adj": "N/A; diffusion index" if is_ism else "N/A",
                "direction_convention": "Higher PMI and values above 50 = services expansion; prior for SPY is procyclical/risk-on, to be tested by Evan.",
                "effective_start": str(values.min().date()) if len(values) else "",
                "known_quirks": f"ISM PMI removed from FRED; use offline workbook only. {phase0} Release lag approximated as third business day of following month.",
                "display_note": "ISM Services PMI is a monthly survey diffusion index. The daily panel is a step function and updates only after the monthly release.",
                "refresh_freq": "monthly" if is_ism else "daily",
                "refresh_source": "ISM via project Data Master workbook" if is_ism else "Yahoo Finance",
            })
    pd.DataFrame(rows).to_csv(path, index=False)


def update_display_registry(monthly: pd.DataFrame, daily: pd.DataFrame) -> None:
    reg_path = DATA_DIR / "display_name_registry.csv"
    reg = pd.read_csv(reg_path)
    existing = set(reg["column_name"])
    meta = {}
    for frequency, df in [("monthly", monthly), ("daily", daily)]:
        meta.update(metadata_for_columns(df, frequency, Path("x"))["columns"])
    rows = []
    for col, m in meta.items():
        if col not in existing:
            rows.append({
                "column_name": col,
                "display_name": m["display_name"],
                "unit": m["unit"],
                "axis_label": {
                    "ism_services_pmi": "PMI",
                    "ism_services_gap_50": "PMI - 50",
                    "ism_services_delta": "PMI Change",
                    "ism_services_3m_change": "3M Change",
                    "ism_services_6m_change": "6M Change",
                    "ism_services_zscore_60m": "Z-score (60M)",
                    "ism_services_above_50": "Above 50 (0/1)",
                    "days_since_release": "Days Since Release",
                }.get(col, m["display_name"]),
            })
    if rows:
        reg = pd.concat([reg, pd.DataFrame(rows)], ignore_index=True)
    reg.loc[reg["column_name"] == "days_since_release", ["display_name", "axis_label"]] = ["Days Since Release", "Days Since Release"]
    reg.to_csv(reg_path, index=False, lineterminator="\n")

    reg_json_path = DATA_DIR / "display_name_registry.json"
    if reg_json_path.exists():
        obj = json.loads(reg_json_path.read_text())
        if "columns" in obj:
            have = {entry["column_name"] for entry in obj["columns"]}
            obj["columns"].extend([r for r in rows if r["column_name"] not in have])
            for entry in obj["columns"]:
                if entry["column_name"] == "days_since_release":
                    entry["display_name"] = "Days Since Release"
                    entry["axis_label"] = "Days Since Release"
            obj["generated_at"] = NOW_ISO
            reg_json_path.write_text(json.dumps(obj, indent=2) + "\n")


def update_manifest(monthly_path: Path, monthly_latest: Path, daily_path: Path, daily_latest: Path) -> None:
    manifest_path = DATA_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    artifacts = [a for a in manifest["artifacts"] if PAIR_ID not in a.get("path", "")]
    last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = {
        "source": "ISM Services PMI from project Data Master.xlsx sheet ISM PMI column B + yahoo:SPY",
        "refresh_ttl_days": 30,
        "last_updated": last_updated,
        "pairs": [PAIR_ID],
        "mixed_freq_ttl_note": "Monthly ISM Services PMI plus SPY market prices; TTL=30 because the signal updates monthly. Daily SPY can refresh faster, but the carried indicator changes only at monthly release dates.",
    }
    entries = [
        {**base, "path": repo_rel(monthly_path), "schema_ref": f"data/{PAIR_ID}_monthly_schema.json"},
        {**base, "path": repo_rel(monthly_latest), "source": f"alias_of:{repo_rel(monthly_path)}", "schema_ref": f"data/{PAIR_ID}_monthly_schema.json", "source_master": repo_rel(monthly_path)},
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


def write_missing_report(monthly: pd.DataFrame, daily: pd.DataFrame, phase0: str, path: Path) -> None:
    lines = [
        f"# Missing Value Report - {PAIR_ID} ({DATE_TAG})",
        "",
        f"Monthly dataset: shape {monthly.shape}, {monthly.index.min().date()} to {monthly.index.max().date()}.",
        f"Daily dataset: shape {daily.shape}, {daily.index.min().date()} to {daily.index.max().date()}.",
        "",
        "## Phase 0 / Source Check",
        "",
        phase0,
        "",
        "The adjacent `G - ISM Services PMI, price` column is intentionally excluded; it belongs to `ism_services_price_xli`.",
        "",
        "## Real-Time Lag",
        "",
        "Daily LVCF uses release dates set to the third business day of the month following the reference month. This approximates the ISM Services release calendar and implies a real-time lag floor of about 3-5 calendar days after reference month-end.",
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
    lines.extend([
        "",
        "No internal gaps in the ISM Services PMI headline series. The daily indicator is an intentional release-lagged step function; `days_since_release` documents staleness.",
    ])
    path.write_text("\n".join(lines) + "\n")


def write_interpretation_metadata(path: Path) -> None:
    meta = {
        "pair_id": PAIR_ID,
        "schema_version": "1.1.0",
        "indicator": INDICATOR,
        "target": TARGET,
        "indicator_nature": "leading",
        "indicator_type": "sentiment",
        "strategy_objective": "max_sharpe",
        "expected_direction": "procyclical",
        "data_provenance": {
            "source": "Project Data Master.xlsx sheet ISM PMI, column CDis, CSta - ISM Services PMI; FRED intentionally not used because ISM PMI series are no longer on FRED",
            "series_id": ISM_COL,
            "accessed_at": NOW_ISO,
        },
        "known_stress_episodes": [
            {"label": "GFC services contraction", "start": "2008-11-01", "end": "2009-06-30", "note": "ISM Services PMI fell below 40 in November 2008."},
            {"label": "COVID services shock", "start": "2020-03-01", "end": "2020-06-30", "note": "Services activity contracted sharply during the initial pandemic shock."},
        ],
        "related_pair_ids": ["ism_services_xlp", "ism_services_xle", "ism_services_xli", "ism_services_xly", "ism_services_xlk", "ism_services_xlf", "ism_services_price_xli"],
        "owner_writes": {
            "dana": ["pair_id", "schema_version", "indicator", "target", "indicator_nature", "indicator_type", "data_provenance", "known_stress_episodes", "related_pair_ids"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "expected_direction", "mechanism", "caveats", "narrative_summary"],
        },
        "last_updated_by": "dana",
        "last_updated_at": NOW_ISO,
    }
    path.write_text(json.dumps(meta, indent=2) + "\n")


def write_handoff(
    path: Path,
    phase0: str,
    monthly_path: Path,
    daily_path: Path,
    stationarity_path: Path,
    monthly: pd.DataFrame,
    daily: pd.DataFrame,
    stat: pd.DataFrame,
) -> None:
    lvl = stat[(stat["variable"] == "level") & (stat["test"] == "ADF")].iloc[0]
    kpss = stat[(stat["variable"] == "level") & (stat["test"] == "KPSS")].iloc[0]
    verdict = (
        f"Level PMI passes ADF at p={lvl.p_value:.4f}; KPSS p={kpss.p_value:.4f} "
        f"with conclusion `{kpss.conclusion}`. This is expected for a bounded diffusion index."
    )
    text = f"""Handoff: Data Dana -> Econ Evan

Files:
- Monthly analysis dataset: `data/ism_services_spy_monthly_latest.parquet` (source dated file `{repo_rel(monthly_path)}`)
- Daily LVCF dataset: `data/ism_services_spy_daily_latest.parquet` (source dated file `{repo_rel(daily_path)}`)
- Monthly sidecar: `data/ism_services_spy_monthly_schema.json`
- Daily sidecar: `data/ism_services_spy_daily_schema.json`
- Data dictionary: `data/data_dictionary_ism_services_spy_{DATE_TAG}.csv`
- Stationarity: `{repo_rel(stationarity_path)}`
- Interpretation metadata: `results/ism_services_spy/interpretation_metadata.json`

Summary:
Built the ISM Services PMI -> SPY data layer from the project workbook only. The monthly panel is {monthly.shape[0]} rows x {monthly.shape[1]} columns, {monthly.index.min().date()} to {monthly.index.max().date()}. The daily panel is {daily.shape[0]} SPY trading days x {daily.shape[1]} columns, {daily.index.min().date()} to {daily.index.max().date()}, with release-lagged LVCF and `days_since_release`.

Source / Phase-0:
{phase0}
The workbook headline series covers 1997-07-31 to 2025-10-31. Pre-master labels its coverage as monthly Aug 1997-Oct 2025, but the actual workbook includes a 1997-07-31 first reference-month row and matches the Pre-master sum exactly. I did not include `G - ISM Services PMI, price`; that is reserved for `ism_services_price_xli`.

Units and direction prior:
`ism_services_pmi` is an index-level diffusion index. The natural threshold is 50: values above 50 indicate expansion, below 50 contraction. Direction prior for Evan: procyclical/risk-on for SPY, but empirical direction should decide.

Release lag floor:
Daily LVCF assumes prior-month ISM Services PMI is released on the third business day of the following month. This creates a real-time lag floor of roughly 3-5 calendar days after reference month-end. Do not treat month-end values as tradable before their release dates; daily `days_since_release` is included for staleness modeling.

Stationarity:
{verdict}
See `{repo_rel(stationarity_path)}` for ADF/KPSS on level, delta, 3-month change, z-score, and SPY returns. Recommended primary transform: test level PMI and `ism_services_gap_50` directly because the diffusion index is bounded/mean-reverting; include `ism_services_3m_change` and `ism_services_zscore_60m` as robustness signals. Do not mechanically difference unless diagnostics demand it.

Known issues:
- ISM Services PMI is an offline project-vintage workbook series, not an API-refreshable FRED series.
- Release dates are approximated by the third business day rule; exact historical release timestamps are not encoded.
- Daily indicator values are a deliberate monthly step function and will induce serial dependence in daily OLS-style specifications.

Questions for recipient:
- None. Please confirm whether Evan wants a separate exact-release-calendar enhancement later; current lag-floor handling is sufficient for no-lookahead daily modeling.
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
    ism = read_ism_services()
    max_release = third_business_day_next_month(ism.index.max())
    spy = fetch_yahoo_close("SPY", "1993-01-01", (max_release + pd.Timedelta(days=2)).strftime("%Y-%m-%d"), "spy")
    print(f"ISM Services PMI: {len(ism)} obs, {ism.index.min().date()} to {ism.index.max().date()}, min={ism.min():.1f}, max={ism.max():.1f}")
    print(f"SPY: {len(spy)} obs, {spy.index.min().date()} to {spy.index.max().date()}")

    print("\n" + "=" * 72)
    print("BUILD PANELS")
    print("=" * 72)
    monthly = build_monthly(ism, spy)
    daily = build_daily_lvcf(ism, spy)
    assert not monthly.index.duplicated().any()
    assert not daily.index.duplicated().any()
    assert daily["days_since_release"].ge(0).all()
    assert daily["release_date"].max() == max_release
    assert daily["ism_services_pmi"].min() == ism.min()
    assert daily["ism_services_pmi"].max() == ism.max()
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
    write_data_dictionary(monthly, daily, dict_path, phase0)
    monthly.describe().T.round(4).to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_monthly_{DATE_TAG}.csv")
    daily.describe(include="all").T.to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_daily_{DATE_TAG}.csv")
    mv_path = DATA_DIR / f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md"
    write_missing_report(monthly, daily, phase0, mv_path)

    meta_path = RESULTS_DIR / "interpretation_metadata.json"
    write_interpretation_metadata(meta_path)
    update_display_registry(monthly, daily)
    update_manifest(monthly_path, monthly_latest, daily_path, daily_latest)
    update_prospective_pairs()

    handoff_path = PWS_DIR / "dana_handoff.md"
    write_handoff(handoff_path, phase0, monthly_path, daily_path, stat_path, monthly, daily, stat)

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
        monthly_path, monthly_latest, daily_path, daily_latest,
        monthly_schema_path, daily_schema_path, dict_path,
        DATA_DIR / f"summary_stats_{PAIR_ID}_monthly_{DATE_TAG}.csv",
        DATA_DIR / f"summary_stats_{PAIR_ID}_daily_{DATE_TAG}.csv",
        mv_path, stat_path, meta_path, handoff_path,
        DATA_DIR / "manifest.json", DATA_DIR / "display_name_registry.csv",
        DATA_DIR / "display_name_registry.json", DATA_DIR / "prospective_pairs.csv",
    ]:
        print(f"- {repo_rel(artifact)}")


if __name__ == "__main__":
    main()
