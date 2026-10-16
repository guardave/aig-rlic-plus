"""pkg12 Phase A impact scan (read-only): point-in-time breaches and as-of Sharpe for every live pair's published winner.

Run from the repo root:  python _pws/lead-lesandro/pkg12_pit_release/src/impact_scan.py
Writes IMPACT.csv (one row per pair) and IMPACT_breaches.csv (one row per breaching winner period) next to this folder.

Method
  * Winner (lead L, position shift s) from results/<pair>/winner_summary.json + registry; release series from the
    registry; calendar from data/release_calendar/release_calendar.csv via scripts/_pit_align.py.
  * Breaches: fixed effective lag E = L + s over the rows of the committed strategy_returns CSV (the backtest sample),
    split by the calendar basis of the nominal reading (measured / sibling / rule / fallback / no release).
  * As-of positions WITHOUT rerunning the pipeline: the committed traded position at return row t is f(reading t-E)
    (signal and rolling threshold both lagged E). The as-of rule uses reading t-k_t with k_t >= E, so its traded
    position is the committed one at row t-(k_t-E). Exact for stateless rules whose inputs at a row depend only on
    data up to that row; rows whose source row precedes the CSV are cash (counted).
  * Sharpe = mean / std * sqrt(12 | 4 | 252) on the published IS / OOS windows (IS = rows before OOS start when the
    winner file has no IS window). Reproduction of the published OOS Sharpe is checked and reported.
  * Default fallback (Lead Q1): max observed lag EXCLUDING documented shutdown windows; availability uses the
    calendar's available_date (after-close releases count from the next trading day, Lead Q3).
  * Sensitivity (*_harsh): fallback rows at the shutdown-INCLUSIVE max lag; IS and OOS reported for both.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
import _pit_align as pa  # noqa: E402
import gate_lead_floor as glf  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
REG = json.loads((REPO / "docs/schemas/lead_axis_registry.json").read_text())["pairs"]
META = json.loads((REPO / "data/release_calendar/release_calendar_meta.json").read_text())["series"]
CAL = pd.read_csv(REPO / "data/release_calendar/release_calendar.csv", parse_dates=["ref_date", "period_end", "first_release"])
ANN = {"months": 12, "quarters": 4, "trading_days": 252}
RULES = {"rule:market_close": 0, "rule:next_business_day": 1}


def sharpe(x, ann):
    x = pd.Series(x).dropna()
    return float(x.mean() / x.std() * np.sqrt(ann)) if len(x) > 2 and x.std() > 0 else np.nan


def basis_of(series, stamps):
    if series in RULES:
        return pd.Series("rule", index=stamps)
    c = CAL[CAL.series_id == series]
    freq = "Q" if (c.ref_date.diff().dropna().dt.days > 80).all() else "M"
    b = pd.Series(c.basis.values, index=c.period_end.dt.to_period(freq))
    return pd.Series(b.reindex(pd.DatetimeIndex(stamps).to_period(freq)).values, index=stamps).fillna("pre-calendar")


def release_alt(series, idx):
    """Sensitivity: fallback rows at the shutdown-INCLUSIVE max lag (calendar *_harsh columns)."""
    return pa.load_release(series, idx, harsh=True)


def winner_lead(w):
    for k in ("lead_value", "lead_months", "lead_days", "lead_quarters"):
        if isinstance(w.get(k), (int, float)):
            return int(w[k])


def tournament_margin(pair, objective):
    fs = sorted(f for f in glob.glob(str(REPO / f"results/{pair}/tournament_results_*.csv")))
    if not fs:
        return np.nan, None
    t = pd.read_csv(fs[-1])
    col = "is_sharpe" if objective == "max_is_sharpe" else "oos_sharpe"
    if col not in t:
        return np.nan, Path(fs[-1]).name
    if "valid" in t:
        t = t[t["valid"].astype(str).str.lower().isin(["true", "1"])]
    v = t[col].dropna().sort_values(ascending=False).to_numpy()
    return (float(v[0] - v[1]) if len(v) > 1 else np.nan), Path(fs[-1]).name


def scan(pair):
    rec = REG[pair]
    series, axis = rec["release_calendar_series"], rec["lead_axis"]
    w = json.loads((REPO / f"results/{pair}/winner_summary.json").read_text())
    L, s_reg = winner_lead(w), int(rec.get("position_shift", 0))
    gres = glf.check_pair(REPO, pair, rec, "per-period")  # the gate's view: traded grids + detected shift
    code_grid = {x for gd in gres["grids"] for x in gd["grid"]}
    det = {gres["per_period"]["position_shift"]} if gres.get("per_period") else set()
    s = det.pop() if len(det) == 1 else s_reg  # what the committed code does; registry when ambiguous
    grid = sorted(code_grid) or rec["lead_grid"]
    row = dict(pair=pair, series=series, lead_axis=axis, winner_lead=L, position_shift=s, registry_position_shift=s_reg,
               effective_lag=L + s, searched_grid=",".join(map(str, grid)),
               registry_grid=",".join(map(str, rec["lead_grid"])), selection=(w.get("selection") or {}).get("objective"),
               signal=w.get("signal_code"), threshold=w.get("threshold_code"), strategy=w.get("strategy_family"),
               direction=w.get("direction"))
    fs = [f for f in sorted(glob.glob(str(REPO / f"results/{pair}/strategy_returns_*.csv"))) if "meta" not in f]
    d = None
    if fs:
        d = pd.read_csv(fs[-1], parse_dates=["date"]).set_index("date")
        row["returns_file"] = Path(fs[-1]).name
        row["gate_status"] = gres["status"]
        idx = d.index
    else:
        t0, t1, srcf = glf.backtest_sample(REPO, pair)
        row["gate_status"] = gres["status"]
        row["returns_file"] = f"none (sample from {srcf}; Sharpe not measurable)"
        idx = pd.date_range(t0, t1, freq={"months": "ME", "quarters": "QE"}[axis])
    E = L + s
    start = idx[0]
    out = []
    pats = {"measured": "^(?:alfred_first|usgs_file|publisher_verified)", "sibling": "^alfred_sibling",
            "rule": "^(?:publisher_calendar|rule)", "fallback": "^fallback", "no_release": "^no_release"}

    def count(lead, alt=False):
        if axis == "trading_days":
            ext = idx
        else:
            pad = pd.date_range(end=idx[0], periods=lead + pa.MAX_EXTRA + 3,
                                freq={"months": "ME", "quarters": "QE"}[axis])[:-1]
            ext = pad.append(idx)
        if series in RULES:
            r_ext = pa.rule_release(ext, RULES[series])
        else:
            r_ext = release_alt(series, ext) if alt else pa.load_release(series, ext)
        b = pa.breaches(ext, lead, r_ext, 0, start=start)
        b["basis"] = basis_of(series, pd.DatetimeIndex(b.reading)).values if len(b) else []
        return b

    per_lead, per_lead_alt, kinds_any = [], [], set()
    for lead in sorted(set(grid) | {L}):
        b = count(lead + s)
        if len(b):
            k = {k: int(b.basis.str.contains(pat).sum()) for k, pat in pats.items()}
            kinds_any |= {x for x, v in k.items() if v}
            per_lead.append(f"L{lead}:{len(b)}(" + "/".join(f"{x[0]}{v}" for x, v in k.items() if v) + ")")
            ba = count(lead + s, alt=True)
            if len(ba):
                per_lead_alt.append(f"L{lead}:{len(ba)}")
        if lead == L:
            row["winner_breaches"] = len(b)
            for kk, pat in pats.items():
                row[f"winner_breaches_{kk}"] = int(b.basis.str.contains(pat).sum()) if len(b) else 0
            row["winner_breaches_harsh_fallback"] = len(count(lead + s, alt=True))
            row["winner_breach_dates"] = ("ALL rows" if len(b) >= len(idx) - 1 else
                                          ";".join(str(x.date()) for x in b.return_row))
            row["winner_max_days_early"] = float(b.days_early.max()) if len(b) and b.days_early.notna().any() else np.nan
            if len(b) >= len(idx) - 1:  # every row breaches (contemporaneous daily lookahead): one summary row
                out = [dict(pair=pair, return_row=f"ALL {len(b)} rows {b.return_row.min().date()}..{b.return_row.max().date()}",
                            reading="same bar", basis=b.basis.iloc[0])]
            else:
              out = [dict(pair=pair, return_row=str(x.return_row.date()), reading=str(x.reading.date()),
                          release=str(x.release.date()) if pd.notna(x.release) else "", window_open=str(x.window_open.date()),
                          days_early=x.days_early, asof_lag=x.asof_lag, basis=x.basis) for x in b.itertuples()]
    row["grid_breaches"] = " ".join(per_lead)  # m=measured s=sibling r=rule f=fallback n=no release
    row["grid_breaches_harsh_fallback"] = " ".join(per_lead_alt)
    row["n_grid_leads_breaching"] = sum(1 for x in per_lead if int(x[1:x.index(":")]) in grid)
    nonfb = kinds_any - {"fallback"}
    row["needs_rerun"] = ("yes: winner breaches" if row["winner_breaches"] else
                          "yes: grid breaches on dated releases" if nonfb else
                          "conditional: grid breaches only from the fallback (pre-vintage) dates" if per_lead else "no")
    if d is None:
        return row, out
    bh = d["bh_return"] if "bh_return" in d else d["benchmark_return"]
    pos = d["position"].astype(float)
    # traded position aligned to the return row (some pipelines store the pre-shift position)
    e0 = (d.strategy_return.fillna(0) - pos.fillna(0) * bh.fillna(0)).abs().max()
    e1 = (d.strategy_return.fillna(0) - pos.shift(1).fillna(0) * bh.fillna(0)).abs().max()
    traded = pos if e0 <= e1 else pos.shift(1)
    row["csv_position_is_preshift"] = bool(e1 < e0)
    row["repro_max_abs_err"] = float(min(e0, e1))
    rel = pa.rule_release(idx, RULES[series]) if series in RULES else pa.load_release(series, idx)
    # as-of positions for the winner (fold the shift into the lead: return row t uses reading t-E)
    ann = ANN[axis]
    oos0 = pd.Timestamp(w.get("oos_period_start") or w.get("oos_start"))
    oos1 = pd.Timestamp(w.get("oos_period_end") or idx[-1])
    is0 = pd.Timestamp(w["is_period_start"]) if w.get("is_period_start") else idx[0]
    is1 = pd.Timestamp(w["is_period_end"]) if w.get("is_period_end") else oos0 - pd.Timedelta(days=1)
    isw, oosw = (idx >= is0) & (idx <= is1), (idx >= oos0) & (idx <= oos1)
    strat = traded.fillna(0) * bh
    row.update(is_sharpe_published=w.get("is_sharpe"), oos_sharpe_published=w.get("oos_sharpe"),
               is_sharpe_repro=sharpe(strat[isw], ann), oos_sharpe_repro=sharpe(strat[oosw], ann),
               bh_oos_sharpe=sharpe(bh[oosw], ann))
    for tag, rl in (("pit", None), ("pit_harsh", "alt")):
        if axis == "trading_days":
            r_full = rel
        else:
            r_full = rel if rl is None or series in RULES else release_alt(series, idx)
        k = pa.asof_lags(idx, E, r_full, 0)
        extra = (k - E)
        src = np.arange(len(idx)) - extra.fillna(10**9).to_numpy(dtype=np.int64)
        ok = (extra.notna().to_numpy()) & (src >= 0)
        tpos = traded.fillna(0).to_numpy()
        tp = tpos.copy()  # rows with no as-of lag (reading before the CSV / calendar) keep the committed position
        tp[ok] = tpos[src[ok]]
        head = np.ones(len(idx), dtype=bool)
        ppit = pd.Series(tp, index=idx)
        sp = ppit * bh
        row[f"is_sharpe_{tag}"] = sharpe(sp[isw], ann)
        row[f"oos_sharpe_{tag}"] = sharpe(sp[oosw], ann)
        row[f"rows_position_changed_{tag}"] = int((ppit != traded.fillna(0)).sum())
        row[f"rows_changed_is_{tag}"] = int(((ppit != traded.fillna(0)) & isw).sum())
        row[f"rows_changed_oos_{tag}"] = int(((ppit != traded.fillna(0)) & oosw).sum())
        row[f"rows_kept_committed_{tag}"] = int((~ok).sum())
    row["d_is_sharpe"] = row["is_sharpe_pit"] - row["is_sharpe_repro"]
    row["d_oos_sharpe"] = row["oos_sharpe_pit"] - row["oos_sharpe_repro"]
    margin, tf = tournament_margin(pair, row["selection"])
    row["tournament_file"], row["objective_margin_top2"] = tf, margin
    obj = "d_is_sharpe" if row["selection"] == "max_is_sharpe" else "d_oos_sharpe"
    row["d_objective"] = row[obj]
    return row, out


def main():
    rows, br = [], []
    for p in sorted(k for k, v in REG.items() if "release_calendar_series" in v):
        r, b = scan(p)
        rows.append(r)
        br += b
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "IMPACT.csv", index=False, float_format="%.4f")
    pd.DataFrame(br).to_csv(OUT / "IMPACT_breaches.csv", index=False)
    cols = ["pair", "effective_lag", "winner_breaches", "winner_breaches_fallback", "winner_breaches_harsh_fallback",
            "rows_changed_is_pit", "rows_changed_oos_pit", "oos_sharpe_published", "oos_sharpe_repro",
            "is_sharpe_repro", "is_sharpe_pit", "oos_sharpe_pit", "is_sharpe_pit_harsh", "oos_sharpe_pit_harsh", "d_objective",
            "objective_margin_top2", "needs_rerun"]
    pd.set_option("display.width", 300)
    print(df[[c for c in cols if c in df]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print(df[["pair", "searched_grid", "grid_breaches", "grid_breaches_harsh_fallback"]].to_string(index=False))


if __name__ == "__main__":
    main()
