"""pkg12 Q6 (read-only): sample lost if every pair's backtest is truncated at its series' first ALFRED vintage.

Track (b) real-time vintages exist only from a series' first ALFRED vintage; Q6 asks what truncating there costs.
Run from the repo root:  python _pws/lead-lesandro/pkg12_pit_release/src/q6_sample_loss.py
Writes Q6_SAMPLE_LOSS.csv next to this folder.

Per live pair:
  * current IS / OOS windows: the published winner_summary windows when present (IS-selected pairs publish the common
    IS window); otherwise IS = strategy_returns rows before the published OOS start (flagged 'derived').
  * truncated: the first return row whose window opens on/after the first ALFRED vintage (as of then a real-time
    vintage exists, and it carries the full history, so rolling windows need no extra warm-up). IS / OOS ends unchanged.
  * eligibility: IS rows on the (truncated) common IS window >= 60 monthly / 20 quarterly (the pipelines' MIN_IS_N).
  * NBER recessions (1990-07..1991-03, 2001-03..2001-11, 2007-12..2009-06, 2020-02..2020-04) inside the current IS
    that the truncated IS loses (fully or partly).
Market-data pairs and no-archive sources (Q7) are not truncated.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
import _pit_align as pa  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
REG = json.loads((REPO / "docs/schemas/lead_axis_registry.json").read_text())["pairs"]
FV = pd.read_csv(REPO / "data/release_calendar/alfred_first_vintage_dates.csv").set_index("series_id").first_alfred_vintage
RECESSIONS = {"1990-91": ("1990-07-01", "1991-03-31"), "2001": ("2001-03-01", "2001-11-30"),
              "2008-09 (GFC)": ("2007-12-01", "2009-06-30"), "2020 (COVID)": ("2020-02-01", "2020-04-30")}
NO_ARCHIVE = {"ISM_MFG", "ISM_SERVICES", "NAHB_HMI", "EIA_WPSR_WTTSTUS1", "USGS_CEMENT_MIS"}
MIN_IS = {"months": 60, "quarters": 20}


def rows(idx, a, b):
    return int(((idx >= a) & (idx <= b)).sum())


def recess(a, b):
    return [k for k, (x, y) in RECESSIONS.items() if pd.Timestamp(y) >= a and pd.Timestamp(x) <= b]


def scan(pair):
    rec = REG[pair]
    series, axis = rec["release_calendar_series"], rec["lead_axis"]
    w = json.loads((REPO / f"results/{pair}/winner_summary.json").read_text())
    row = dict(pair=pair, series=series, lead_axis=axis)
    # umcsent_spy loads UMich *expected business conditions* (Data Master; UMCSENT is only its calendar proxy)
    if series.startswith("rule:") or series == "T10Y3M_ME":
        row.update(status="unaffected: market data (not revised)")
        return row
    if series in NO_ARCHIVE or pair == "umcsent_spy":
        row.update(status="not applicable: no ALFRED archive (Q7: disclosed as revised values)")
        return row
    fv = pd.Timestamp(FV[series])
    row["first_alfred_vintage"] = str(fv.date())
    fs = [f for f in sorted(glob.glob(str(REPO / f"results/{pair}/strategy_returns_*.csv"))) if "meta" not in f]
    if fs:
        idx = pd.DatetimeIndex(pd.read_csv(fs[-1], usecols=["date"], parse_dates=["date"]).date)
    else:  # permit_spy: trade-log date range, month-end rows
        t0, t1, _ = __import__("gate_lead_floor").backtest_sample(REPO, pair)
        idx = pd.date_range(t0, t1, freq="ME")
        row["note"] = "no strategy_returns CSV: monthly rows over the trade-log range"
    oos0 = pd.Timestamp(w.get("oos_period_start") or w.get("oos_start"))
    oos1 = pd.Timestamp(w.get("oos_period_end") or idx[-1])
    if w.get("is_period_start"):
        is0, is1, basis = pd.Timestamp(w["is_period_start"]), pd.Timestamp(w["is_period_end"]), "published common IS window"
    else:
        is0, is1, basis = idx[0], idx[idx < oos0][-1], "derived: strategy_returns rows before the OOS start"
    opens = pa.window_open(idx, 0)
    ok = idx[(opens >= fv).to_numpy()]
    t_start = ok[0] if len(ok) else None
    n_is, n_oos = rows(idx, is0, is1), rows(idx, oos0, oos1)
    row.update(is_basis=basis, is_start=str(is0.date()), is_end=str(is1.date()), is_rows=n_is,
               oos_start=str(oos0.date()), oos_end=str(oos1.date()), oos_rows=n_oos)
    if fv <= idx[0] or (t_start is not None and t_start <= is0):
        row.update(status="no loss: first vintage precedes the sample", trunc_is_start=str(is0.date()),
                   trunc_is_rows=n_is, trunc_oos_start=str(oos0.date()), trunc_oos_rows=n_oos, pct_is_lost=0.0)
    else:
        ti0, to0 = max(is0, t_start), max(oos0, t_start)
        t_is = rows(idx, ti0, is1) if ti0 <= is1 else 0
        t_oos = rows(idx, to0, oos1)
        row.update(status="truncated", trunc_is_start=str(ti0.date()) if t_is else "", trunc_is_rows=t_is,
                   trunc_oos_start=str(to0.date()), trunc_oos_rows=t_oos,
                   pct_is_lost=round(100 * (1 - t_is / n_is), 1) if n_is else None,
                   recessions_lost_from_is=", ".join(
                       f"{r} ({'fully' if t_is == 0 or pd.Timestamp(RECESSIONS[r][1]) < ti0 else 'partly'})"
                       for r in recess(is0, is1) if t_is == 0 or pd.Timestamp(RECESSIONS[r][0]) < ti0) or "none")
    need = MIN_IS[axis]
    row["min_is_rows"] = need
    row["eligible_now"] = n_is >= need
    row["eligible_truncated"] = row["trunc_is_rows"] >= need
    row["recessions_in_current_is"] = ", ".join(recess(is0, is1)) or "none"
    return row


def main():
    df = pd.DataFrame([scan(p) for p in sorted(k for k, v in REG.items() if "release_calendar_series" in v)])
    df.to_csv(OUT / "Q6_SAMPLE_LOSS.csv", index=False)
    pd.set_option("display.width", 250)
    print(df[["pair", "series", "first_alfred_vintage", "is_start", "is_rows", "trunc_is_start", "trunc_is_rows",
              "pct_is_lost", "trunc_oos_rows", "oos_rows", "eligible_truncated", "recessions_lost_from_is", "status"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
