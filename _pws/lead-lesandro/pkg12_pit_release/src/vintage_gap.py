"""pkg12 D8 (read-only): how much do published winners depend on pairing REVISED values with first-release timing?

Run from the repo root (data panels are read from the main checkout's data/, which is gitignored):
    python _pws/lead-lesandro/pkg12_pit_release/src/vintage_gap.py [DATA_DIR]
Writes VINTAGE_GAP.csv next to this folder.

For every live pair whose winner is a FRED series with ALFRED vintages:
  C  committed      : the published traded positions (latest-vintage values, fixed lead). Re-derived here from the
                      pipeline's own data panel with a replicated rule; the quantification is reported only when
                      the replication matches the committed positions on >= 98% of rows.
  Ĉ  replicated C   : the replicated rule on the panel (Ĉ - C = replication error, reported, not attributed).
  N  timing only    : the panel's own (latest-vintage) values, each reading used only once it is present in the
                      ALFRED vintage at the window open (as-of availability). N - Ĉ = the timing effect, R - N = the pure revision effect.
  R  real-time      : at each rebalance, the vintage AS KNOWN when the return window opens (ALFRED rows with
                      realtime_start <= open <= realtime_end; for after-close series (BUSLOANS H.8; M2SL H.6 before
                      2021-02-23) the vintage of the previous trading day). The rule (transform, rolling threshold) is computed on
                      that vintage and the latest reading present in it at or before the nominal lead is used
                      (presence in a vintage = released). This is track (b): revised values floored on the date the
                      value became available.
  F  first-release  : every reading at its first print (ALFRED initial release), timed by the first-release
                      calendar (as-of). Track (a). Readings before the series' first vintage carry their
                      first-vintage values (already revised): F is only clean after the first vintage date.
Sharpe on the rows where R is defined (window opens on/after the series' first ALFRED vintage), split by the
published IS / OOS windows.
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

DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/workspaces/aig-rlic-plus/data")
VINT = REPO / "data" / "release_calendar" / "vintages"
OUT = Path(__file__).resolve().parents[1]
REG = json.loads((REPO / "docs/schemas/lead_axis_registry.json").read_text())["pairs"]

# pair -> (FRED series of the panel's raw column, panel file, raw column, raw is yoy of the FRED level)
SPEC = {
    "busloans_spy": ("BUSLOANS", "busloans_spy_monthly_latest.parquet", "busloans_usd", False),
    "cass_freight_spy": ("FRGSHPUSM649NCIS", "cass_freight_spy_monthly_latest.parquet", "cass_freight_idx", False),
    "cc_delinquency_spy": ("DRCCLACBN", "cc_delinquency_spy_quarterly_latest.parquet", "ccdelinq", False),
    "consumer_sentiment_spy": ("UMCSENT", "consumer_sentiment_spy_monthly_latest.parquet", "umcsent", False),
    "housing_starts_rebuilt_spy": ("HOUST", "housing_starts_rebuilt_spy_monthly_latest.parquet", "hst", False),
    "import_price_spy": ("IR", "import_price_spy_monthly_latest.parquet", "import_price", False),
    "indpro_spy": ("INDPRO", "indpro_spy_monthly_19900101_20251231.parquet", "indpro", False),
    "indpro_xlp": ("INDPRO", "indpro_xlp_monthly_19980101_20251231.parquet", "indpro", False),
    "m2sl_yoy_spy": ("M2SL", "m2sl_yoy_spy_monthly_latest.parquet", "m2sl_usd", False),
    "mfg_new_orders_spy": ("NEWORDER", "mfg_new_orders_spy_monthly_latest.parquet", "mfg_new_orders", False),
    "nhs_rebuilt_spy": ("HSN1FNSA", "nhs_rebuilt_spy_monthly_latest.parquet", "nhs_nsa", False),
    "nhs_saar_rebuilt_spy": ("HSN1F", "nhs_saar_rebuilt_spy_monthly_latest.parquet", "hsn1f", False),
    "permit_yoy_spy": ("PERMIT", "permit_yoy_spy_monthly_latest.parquet", "permit_yoy", True),
    "retail_inv_sales_spy": ("RETAILIRSA", "retail_inv_sales_spy_monthly_latest.parquet", "invsales", False),
    "rsxfs_spy": ("RSXFS", "rsxfs_spy_monthly_latest.parquet", "rsxfs", False),
    "sloos_ci_small_spy": ("DRTSCILM", "sloos_ci_small_spy_quarterly_latest.parquet", "sloos_ci_small", False),
    "umcsent_xlv": ("UMCSENT", "umcsent_xlv_monthly_19980101_20251231.parquet", "umcsent", False),
    "unrate_spy": ("UNRATE", "unrate_spy_monthly_latest.parquet", "unrate", False),
}


def transforms(x: pd.Series, per_year: int):
    """Candidate signal definitions on a level series (name -> function)."""
    y = per_year
    yoy = lambda s: s.pct_change(y, fill_method=None) * 100  # noqa: E731
    out = {"level": lambda s: s, "pct_mom": lambda s: s.pct_change(fill_method=None) * 100, "diff1": lambda s: s.diff(),
           "pct_6m": lambda s: s.pct_change(6, fill_method=None) * 100, "chg_6m": lambda s: s.diff(6),
           "pct_3m": lambda s: s.pct_change(3, fill_method=None) * 100, "yoy": yoy,
           "flag_yoy_neg": lambda s: (yoy(s) < 0).astype(float).where(yoy(s).notna())}
    for k in (1, 3, 6, 12):
        out[f"yoy_accel{k}"] = (lambda k: lambda s: yoy(s) - yoy(s).shift(k))(k)
    for w in (12, 24, 36, 60):
        out[f"dev_trend{w}"] = (lambda w: lambda s: (s / s.rolling(w).mean() - 1) * 100)(w)
    for mp in (60, 36, 24, 12):
        out[f"yoy_z60_mp{mp}"] = (lambda mp: lambda s: (yoy(s) - yoy(s).rolling(60, min_periods=mp).mean())
                                  / yoy(s).rolling(60, min_periods=mp).std())(mp)
    return out


def thresholds(code: str, value, lookback: str, per_year: int):
    """Candidate threshold builders (on the unshifted signal) for a winner threshold code."""
    import re
    m = re.search(r"p(\d\d)", code)
    W = 60 if per_year == 12 else 20
    lb = re.search(r"(\d+)", str(lookback or ""))
    if lb:
        W = int(lb.group(1))
    if code.startswith("T1_fixed") or code in ("T0_zero",):
        return {"fixed": lambda s: pd.Series(float(value), index=s.index)}
    cands = {}
    if code.startswith("T3_zscore") or code.startswith("T3_z"):
        k = float(re.search(r"(-?\d+\.\d+)", code).group(1))
        for mp in sorted({W, 36, 24, 12, 1}):
            cands[f"z{W}_mp{mp}"] = (lambda mp: lambda s: s.rolling(W, min_periods=mp).mean()
                                     + k * s.rolling(W, min_periods=mp).std())(mp)
        return cands
    q = int(m.group(1)) / 100
    for mp in sorted({W, 36, 24, 20, 12, 8, 1}):
        if mp <= W:
            cands[f"q{W}_mp{mp}"] = (lambda mp: lambda s: s.rolling(W, min_periods=mp).quantile(q))(mp)
    return cands


CMP = {"gt": np.greater, "gte": np.greater_equal, "ge": np.greater_equal, "lt": np.less, "lte": np.less_equal,
       "le": np.less_equal}


def rule_positions(sig: pd.Series, thr: pd.Series, rule: str, strategy: str, invert: bool = False) -> pd.Series:
    """invert=False: on = sig <rule> thr, undefined -> flat (IS-selected family). invert=True: the older family's
    countercyclical orientation, on = NOT(sig <rule> thr) with NaN comparisons False, so undefined -> on."""
    ok = sig.notna() & thr.notna()
    on = pd.Series(CMP[rule](sig.to_numpy(dtype=float), thr.to_numpy(dtype=float)), index=sig.index)
    if invert:
        on = ~on
    pos = on.astype(float) if not strategy.startswith("P3") else on.astype(float) * 2 - 1
    return pos if invert else pos.where(ok, 0.0)


def load_vint(sid):
    d = pd.read_csv(VINT / f"{sid}.csv.gz", parse_dates=["date", "realtime_start"])
    d["realtime_end"] = pd.to_datetime(d.realtime_end.replace("9999-12-31", "2262-01-01"))
    d["value"] = d.value.astype(float)
    return d


def sharpe(x, ann):
    x = pd.Series(x).dropna()
    return float(x.mean() / x.std() * np.sqrt(ann)) if len(x) > 2 and x.std() > 0 else np.nan


def run(pair):
    sid, pfile, col, raw_is_yoy = SPEC[pair]
    rec = REG[pair]
    q = rec["lead_axis"] == "quarters"
    per_year, freq = (4, "Q") if q else (12, "M")
    w = json.loads((REPO / f"results/{pair}/winner_summary.json").read_text())
    L, s = int(w["lead_value"]), int(rec.get("position_shift", 0))
    E = L + s
    sig_col, rule, strat = w["signal_column"], w["threshold_rule"], w.get("strategy_code") or w["strategy_family"]
    row = dict(pair=pair, series=sid, signal=w["signal_code"], signal_column=sig_col, threshold=w["threshold_code"],
               lead=L, position_shift=s, selection=(w.get("selection") or {}).get("objective"))
    panel = pd.read_parquet(DATA / pfile)
    fs = [f for f in sorted(glob.glob(str(REPO / f"results/{pair}/strategy_returns_*.csv"))) if "meta" not in f]
    d = pd.read_csv(fs[-1], parse_dates=["date"]).set_index("date")
    bh = d["bh_return"] if "bh_return" in d else d["benchmark_return"]
    pos = d["position"].astype(float)
    e0 = (d.strategy_return.fillna(0) - pos.fillna(0) * bh.fillna(0)).abs().max()
    e1 = (d.strategy_return.fillna(0) - pos.shift(1).fillna(0) * bh.fillna(0)).abs().max()
    traded = (pos if e0 <= e1 else pos.shift(1)).fillna(0)
    idx = d.index
    # ---- 1. replicate the committed rule on the panel (latest-vintage values the pipeline used)
    raw = panel[col].astype(float)
    level = raw
    tf = transforms(level, per_year)
    if raw_is_yoy:  # the panel already holds the yoy; the signal is that column
        tf = {"level": lambda s_: s_}
    target = panel[sig_col].astype(float) if sig_col in panel else None
    best_t, best_m = None, -1
    for name, fn in tf.items():
        if target is None:
            break
        z = fn(raw)
        j = pd.concat([z, target], axis=1).dropna()
        if len(j) < 24:
            continue
        m = np.isclose(j.iloc[:, 0], j.iloc[:, 1], rtol=1e-4, atol=1e-6).mean()
        if m > best_m:
            best_t, best_m = name, m
    row.update(transform=best_t, transform_match=round(best_m, 4))
    if best_t is None or best_m < 0.98:
        row["status"] = "transform not replicated"
        return row
    tfn = tf[best_t]
    thr_c = thresholds(w["threshold_code"], w.get("threshold_value"), w.get("lookback"), per_year)

    def positions_from(series_sig: pd.Series, thr_fn, inv) -> pd.Series:
        th = thr_fn(series_sig)
        p = rule_positions(series_sig.shift(E), th.shift(E), rule, strat, inv)
        return p.reindex(idx).fillna(0)

    sig_latest = tfn(raw)
    # the pipelines' rolling windows warm up on their own (shorter) sample; judge replication after a 60-period
    # + lead warm-up from the first return row, and report the all-rows match too
    post = np.arange(len(idx)) >= 60 + E
    best_thr, best_pm, inv, all_m = None, -1, False, None
    for name, fn in thr_c.items():
        for iv in (False, True):
            p = positions_from(sig_latest, fn, iv)
            m = float((p == traded)[post].mean())
            if m > best_pm:
                best_thr, best_pm, inv, all_m = name, m, iv, float((p == traded).mean())
    row["invert"] = inv
    row.update(threshold_variant=best_thr, replication_match=round(best_pm, 4), replication_match_all_rows=round(all_m, 4))
    if best_pm < 0.98:
        row["status"] = "positions not replicated (<98%)"
        return row
    thr_fn = thr_c[best_thr]
    # ---- 2. real-time vintages (track R) and first prints (track F)
    v = load_vint(sid)
    v["period"] = v.date.dt.to_period(freq)
    first_vintage = v.realtime_start.min()
    ac_rule = pa.after_close_rule(sid)
    row["after_close_rule"] = str(ac_rule)
    # N uses the pipeline's own panel values (its vintage), so N - Ĉ is timing only
    panel_vals = pd.Series(raw.to_numpy(), index=raw.index.to_period(freq))
    panel_vals = panel_vals[~panel_vals.index.duplicated(keep="last")]
    opens = pa.window_open(idx, 0)  # E already folded into the lead
    r_pos = pd.Series(np.nan, index=idx)
    n_pos = pd.Series(np.nan, index=idx)  # N: latest values, vintage availability only (timing effect alone)
    stamp = lambda per: per.to_timestamp(how="end").normalize()  # noqa: E731
    for t, o in opens.items():
        if pd.isna(o) or o < first_vintage:
            continue
        ov = pa.visible_on(o, ac_rule)  # after-close postings are visible from the next trading day (QA2 M-1)
        vv = v[(v.realtime_start <= ov) & (v.realtime_end >= ov)]
        lv0 = pd.Series(vv.value.values, index=vv.period.values).sort_index()
        lv0 = lv0[~lv0.index.duplicated(keep="last")]
        full = pd.period_range(lv0.index.min(), lv0.index.max(), freq=freq)
        nominal = pd.Timestamp(t).to_period(freq) - E
        for target, lv, is_panel in ((r_pos, lv0, False), (n_pos, panel_vals.reindex(lv0.index), True)):
            present = lv0.reindex(full).notna()
            if raw_is_yoy and not is_panel:
                lv = lv.reindex(full).pct_change(per_year, fill_method=None) * 100
            lv = lv.reindex(full)
            sg = tfn(lv)
            th = thr_fn(sg)
            avail = sg.index[(sg.index <= nominal) & present.to_numpy()]
            if not len(avail):
                continue
            m_ = avail.max()
            if pd.isna(sg.loc[m_]) or pd.isna(th.loc[m_]):
                continue  # rule warm-up inside this vintage
            target[t] = float(rule_positions(sg.loc[[m_]], th.loc[[m_]], rule, strat, inv).iloc[0])
    th_l = thr_fn(sig_latest)
    c_def = (sig_latest.shift(E).notna() & th_l.shift(E).notna()).reindex(idx).fillna(False)
    win = r_pos.notna() & n_pos.notna() & c_def & post  # all rules defined, after the pipeline warm-up
    # track F: first prints + first-release calendar as-of
    fp = v.sort_values("realtime_start").groupby("period").first()
    fpv = fp.value.copy()
    if raw_is_yoy:
        fpv = fpv.pct_change(per_year, fill_method=None) * 100  # yoy of first prints
    fpv.index = pd.DatetimeIndex([stamp(p_) for p_ in fpv.index])
    sgF = tfn(fpv)
    thF = thr_fn(sgF)
    relF = pd.Series(pd.DatetimeIndex([r for r in fp.realtime_start]), index=fpv.index)
    relF[relF == first_vintage] = pd.NaT  # pre-vintage readings: their first print date is unknown
    calF = pa.load_release(rec["release_calendar_series"], fpv.index) if rec["release_calendar_series"] in set(
        pd.read_csv(REPO / "data/release_calendar/release_calendar.csv", usecols=["series_id"]).series_id) else relF
    relF = relF.fillna(calF)
    # as-of over the pipeline rows: place first-print signal on the return index
    ext = fpv.index.union(idx)
    sF = sgF.reindex(ext)
    tF = thF.reindex(ext)
    rF = relF.reindex(ext)
    lagsF = pa.asof_lags(ext, E, rF, 0)
    pF = rule_positions(pa.take_lagged(sF, lagsF), pa.take_lagged(tF, lagsF), rule, strat, inv).reindex(idx).fillna(0)
    # ---- 3. compare on the R window
    ann = per_year
    oos0 = pd.Timestamp(w.get("oos_period_start") or w.get("oos_start"))
    is0 = pd.Timestamp(w["is_period_start"]) if w.get("is_period_start") else idx[0]
    isw, oosw = (idx >= is0) & (idx < oos0), idx >= oos0
    rp, npos = r_pos.fillna(0), n_pos.fillna(0)
    chat = positions_from(sig_latest, thr_fn, inv)  # replicated committed rule (isolates replication error)
    row.update(first_vintage=str(first_vintage.date()), rt_window=f"{idx[win][0].date()}..{idx[win][-1].date()}" if win.any() else "",
               rt_rows=int(win.sum()), rt_rows_is=int((win & isw).sum()), rt_rows_oos=int((win & oosw).sum()),
               pos_agree_R=round(float((rp[win] == traded[win]).mean()), 4) if win.any() else np.nan,
               pos_agree_N=round(float((npos[win] == traded[win]).mean()), 4) if win.any() else np.nan,
               pos_agree_Chat=round(float((chat[win] == traded[win]).mean()), 4) if win.any() else np.nan,
               pos_agree_N_vs_Chat=round(float((npos[win] == chat[win]).mean()), 4) if win.any() else np.nan,
               pos_agree_R_vs_N=round(float((rp[win] == npos[win]).mean()), 4) if win.any() else np.nan,
               pos_agree_F=round(float((pF[win] == traded[win]).mean()), 4) if win.any() else np.nan)
    for tag, mask in (("is", win & isw), ("oos", win & oosw)):
        row[f"{tag}_sharpe_C_win"] = sharpe((traded * bh)[mask], ann)
        row[f"{tag}_sharpe_Chat_win"] = sharpe((chat * bh)[mask], ann)
        row[f"{tag}_sharpe_N_win"] = sharpe((npos * bh)[mask], ann)
        row[f"{tag}_sharpe_R_win"] = sharpe((rp * bh)[mask], ann)
        row[f"{tag}_sharpe_F_win"] = sharpe((pF * bh)[mask], ann)
    for tag in ("is", "oos"):  # total = timing (N - C) + revisions (R - N)
        row[f"d_{tag}_total"] = row[f"{tag}_sharpe_R_win"] - row[f"{tag}_sharpe_C_win"]
        row[f"d_{tag}_replication"] = row[f"{tag}_sharpe_Chat_win"] - row[f"{tag}_sharpe_C_win"]
        row[f"d_{tag}_timing"] = row[f"{tag}_sharpe_N_win"] - row[f"{tag}_sharpe_Chat_win"]
        row[f"d_{tag}_revision"] = row[f"{tag}_sharpe_R_win"] - row[f"{tag}_sharpe_N_win"]
    row["status"] = "quantified"
    return row


def main():
    rows = []
    for p in SPEC:
        try:
            r = run(p)
        except Exception as e:  # report, never hide
            r = dict(pair=p, status=f"error: {type(e).__name__}: {e}")
        rows.append(r)
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "VINTAGE_GAP.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    main()
