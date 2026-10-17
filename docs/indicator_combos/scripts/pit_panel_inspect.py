"""Phase 1 descriptive inspection for the indicator-combination study (DRAFTING ONLY: no returns, no backtests).

Builds a month-end panel of indicator readings AS KNOWN AT THE CLOSE of the last trading day of each month, then
reports sample overlaps, release lags, correlations and an effective-dimensionality estimate.

Two tracks (same transforms):
  revised  : "revised as-of": TODAY's revised values, each entering only once its first-release date has passed
             (data/release_calendar/release_calendar.csv available_date). This is NOT point-in-time (the values
             carry later revisions); it is used for sensitivity only.
  realtime : the ALFRED vintage visible at the close of t (scripts/_pit_align.vintage_asof); the transform is
             recomputed inside that vintage. Only for the 19 series with vintage files, from their first vintage.
Market series (T10Y3M, HY/IG OAS, VIX/VIX3M, gold/copper, SOX/SPY) are unrevised; they are sampled at t, except
T10Y3M (DGS10 - DTB3) and the HY/IG OAS, which take the previous business day's value (FRED posts next day;
conservative). sox_spy is a ratio of SOX to SPY prices, so as a member it embeds SPY's own past price path. No-archive sources (ISM, NAHB, UMich expectations, USGS
cement, EIA crude stocks) exist only on the revised track (snapshot 20261016T232733Z).

Asset prices are loaded only where an indicator is built from them (SOX/SPY ratio); only the needed columns are
read, and no return or forward-return column is loaded. All random draws are seeded (SEED).

Dimensionality (pre-specified in COMBINATORICS.md section 3):
  primary estimand : participation ratio PR = (sum lam)^2 / sum lam^2 of the Pearson correlation
                     matrix of the STRICT-PIT panel (real-time ALFRED vintages + unrevised market series only),
                     with a 90% moving-block bootstrap interval (rows resampled jointly, block 24 months, 2000 draws).
  sensitivity      : parallel analysis under two serial-dependence-preserving nulls (independent per-column
                     stationary bootstrap, mean block 24; independent per-column phase randomisation), 2000 draws
                     each; entropy effective rank; Li & Ji (2005) M_eff (published formula, reported as the
                     M_eff figure); an ad hoc capped-eigenvalue sum, sum min(lam, 1) (NOT an M_eff estimator);
                     PR interval under block lengths 12 / 24 / 36 / 48 months;
                     hierarchical clusters at |rho| >= 0.5 / 0.7; the same statistics on the revised-as-of panels.

Run from the repo root:  python docs/indicator_combos/scripts/pit_panel_inspect.py
Outputs: docs/indicator_combos/data/*.csv|json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from _pit_align import TRADING_DAY, load_vintages, vintage_asof  # noqa: E402

OUT = REPO / "docs" / "indicator_combos" / "data"
CAL = pd.read_csv(REPO / "data/release_calendar/release_calendar.csv", parse_dates=["period_end", "available_date"])
SNAP = REPO / "data/release_calendar/snapshots/20261016T232733Z"
SEED = 20261017
END = pd.Timestamp("2026-09-30")

# indicator -> (source, series id, freq, transform, calendar id, economic block)
#   transform: yoy = 12m (4q) % change; d12 = 12m (4q) difference; lvl = level
SPEC = {
    "indpro":     ("alfred", "INDPRO", "M", "yoy", "INDPRO", "activity"),
    "unrate":     ("alfred", "UNRATE", "M", "d12", "UNRATE", "labour"),
    "rsxfs":      ("alfred", "RSXFS", "M", "yoy", "RSXFS", "consumer"),
    "umcsent":    ("alfred", "UMCSENT", "M", "lvl", "UMCSENT", "sentiment"),
    "houst":      ("alfred", "HOUST", "M", "yoy", "HOUST", "housing"),
    "permit":     ("alfred", "PERMIT", "M", "yoy", "PERMIT", "housing"),
    "nhs":        ("alfred", "HSN1F", "M", "yoy", "HSN1F", "housing"),
    "m2":         ("alfred", "M2SL", "M", "yoy", "M2SL", "money_credit"),
    "busloans":   ("alfred", "BUSLOANS", "M", "yoy", "BUSLOANS", "money_credit"),
    "neworder":   ("alfred", "NEWORDER", "M", "yoy", "NEWORDER", "activity"),
    "amtmno":     ("alfred", "AMTMNO", "M", "yoy", "AMTMNO", "activity"),
    "import_px":  ("alfred", "IR", "M", "yoy", "IR", "prices"),
    "cass":       ("alfred", "FRGSHPUSM649NCIS", "M", "yoy", "FRGSHPUSM649NCIS", "activity"),
    "inv_sales":  ("alfred", "RETAILIRSA", "M", "d12", "RETAILIRSA", "consumer"),
    "cc_delinq":  ("alfred", "DRCCLACBN", "Q", "d12", "DRCCLACBN", "money_credit"),
    "sloos":      ("alfred", "DRTSCILM", "Q", "lvl", "DRTSCILM", "money_credit"),
    "eci":        ("fred", "ECIALLCIV", "Q", "yoy", "ECIALLCIV", "prices"),
    "ism_mfg":    ("snap", "ISM_MFG", "M", "lvl", "ISM_MFG", "activity"),
    "ism_svc":    ("snap", "ISM_SERVICES", "M", "lvl", "ISM_SERVICES", "activity"),
    "nahb":       ("snap", "NAHB_HMI", "M", "lvl", "NAHB_HMI", "housing"),
    "umich_exp":  ("snap", "UMICH_EXP_BUS_COND", "M", "lvl", "UMCSENT", "sentiment"),
    "cement":     ("snap", "USGS_CEMENT", "M", "yoy", "USGS_CEMENT_MIS", "housing"),
    "crude_inv":  ("snap", "EIA_WTTSTUS1", "W", "yoy", "EIA_WPSR_WTTSTUS1", "energy"),
    "t10y3m":     ("mkt", "t10y3m", "D", "lvl", None, "rates"),
    "hy_oas":     ("mkt", "hy_oas", "D", "lvl", None, "credit_mkt"),
    "hy_ig":      ("mkt", "hy_ig", "D", "lvl", None, "credit_mkt"),
    "vix_ratio":  ("mkt", "vix_ratio", "D", "lvl", None, "vol"),
    "gold_copper": ("mkt", "gold_copper", "D", "yoy", None, "commodity"),
    "sox_spy":    ("mkt", "sox_spy", "M", "yoy", None, "equity_internal"),
}


def month_closes(start="1985-01-31", end=END) -> pd.DatetimeIndex:
    me = pd.date_range(start, end, freq="ME")
    return pd.DatetimeIndex([t if TRADING_DAY.is_on_offset(t) else TRADING_DAY.rollback(t) for t in me])


def transform(s: pd.Series, how: str, freq: str) -> pd.Series:
    k = {"M": 12, "Q": 4}[freq]
    if how == "yoy":
        return 100 * (s / s.shift(k) - 1)
    if how == "d12":
        return s - s.shift(k)
    return s


def avail(cal_id: str) -> pd.Series:
    c = CAL[CAL.series_id == cal_id]
    return pd.Series(c.available_date.values, index=c.period_end.values)


def latest_revised(src: str, sid: str) -> pd.Series:
    if src == "alfred":
        v = load_vintages(sid)
        cur = v[v.realtime_end >= pd.Timestamp("2262-01-01")]
        idx = cur["date"].dt.to_period("Q" if SPEC_FREQ[sid] == "Q" else "M").dt.to_timestamp(how="end").dt.normalize()
        return pd.Series(cur.value.values, index=pd.DatetimeIndex(idx)).sort_index()
    if src == "fred":
        from fredapi import Fred
        s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series(sid)
        s.index = pd.DatetimeIndex(s.index).to_period("Q").to_timestamp(how="end").normalize()
        return s.astype(float)
    s = pd.read_csv(SNAP / f"{sid}.csv", parse_dates=["ref_date"]).set_index("ref_date")["value"].astype(float)
    if sid == "EIA_WTTSTUS1":  # weekly: last reading of each month
        s = s.resample("ME").last()
    else:
        s.index = s.index.to_period("M").to_timestamp(how="end").normalize()
    return s


SPEC_FREQ = {v[1]: v[2] for v in SPEC.values()}


def revised_panel(closes: pd.DatetimeIndex) -> pd.DataFrame:
    cols = {}
    for name, (src, sid, freq, how, cal_id, _) in SPEC.items():
        if src == "mkt":
            continue
        tf = transform(latest_revised(src, sid), how, "Q" if freq == "Q" else "M")
        av = avail(cal_id)
        av.index = pd.DatetimeIndex(av.index).normalize()
        a = av.reindex(tf.index)
        known = pd.DataFrame({"v": tf.values, "a": a.values}, index=tf.index).dropna()
        vals = []
        for t in closes:
            k = known[known.a <= t]
            vals.append(k.v.iloc[-1] if len(k) and (t - k.index[-1]).days < 200 else np.nan)
        cols[name] = vals
    return pd.DataFrame(cols, index=closes)


def realtime_panel(closes: pd.DatetimeIndex) -> pd.DataFrame:
    cols = {}
    for name, (src, sid, freq, how, _, _) in SPEC.items():
        if src != "alfred":
            continue
        v = load_vintages(sid)
        first = v.realtime_start.min()
        vals = []
        for t in closes:
            if t < first:
                vals.append(np.nan)
                continue
            s = vintage_asof(v, t, freq)
            full = pd.date_range(s.index.min(), s.index.max(), freq="QE" if freq == "Q" else "ME")
            tf = transform(s.reindex(full), how, freq).dropna()
            vals.append(tf.iloc[-1] if len(tf) and (t - tf.index[-1]).days < 200 else np.nan)
        cols[name] = vals
        print(f"  realtime {name}: from {first.date()}", flush=True)
    return pd.DataFrame(cols, index=closes)


def market_panel(closes: pd.DatetimeIndex) -> pd.DataFrame:
    hy = pd.read_parquet(REPO / "data/hy_ig_spy_daily_20000101_20260422.parquet",
                         columns=["dgs10", "dtb3", "hy_oas", "ig_oas"])
    gc = pd.read_parquet(REPO / "data/gold_copper_xli_daily_20260526.parquet", columns=["gold", "copper"])
    vx = pd.read_parquet(REPO / "data/vix_vix3m_spy_daily_20260314.parquet", columns=["vix", "vix3m"])
    sx = pd.read_parquet(REPO / "data/phlxsox_spy_monthly_latest.parquet", columns=["sox_spy_ratio"])
    d = pd.DataFrame(index=closes)

    def at(s, lag_days=0):
        s = s.dropna()
        s.index = pd.DatetimeIndex(s.index)
        s = s[s.index <= s.index.max()]
        return s.shift(lag_days).reindex(closes, method="ffill", limit=5) if lag_days else s.reindex(closes, method="ffill", limit=5)

    d["t10y3m"] = at(hy["dgs10"] - hy["dtb3"], 1)
    d["hy_oas"] = at(hy["hy_oas"], 1)
    d["hy_ig"] = at(hy["hy_oas"] - hy["ig_oas"], 1)
    d["vix_ratio"] = at(vx["vix"] / vx["vix3m"])
    lr = np.log(gc["gold"] / gc["copper"]).dropna()
    d["gold_copper"] = at(100 * (lr - lr.shift(252)))
    r = sx["sox_spy_ratio"]
    d["sox_spy"] = (100 * (r / r.shift(12) - 1)).reindex(closes.to_period("M").to_timestamp(how="end").normalize()).values
    return d


N_DRAWS = 2000
BLOCK = 24  # months; YoY / 12m-difference readings overlap by construction, so blocks must exceed 12


def _eig(A: np.ndarray) -> np.ndarray:
    return np.sort(np.linalg.eigvalsh(np.corrcoef(A.T)))[::-1]


def _pr(lam: np.ndarray) -> float:
    return float(lam.sum() ** 2 / np.sum(lam ** 2))


def _stationary_bootstrap(x: np.ndarray, rng, mean_block: int) -> np.ndarray:
    """Politis-Romano stationary bootstrap of one series (circular), geometric block lengths."""
    n = len(x)
    out = np.empty(n)
    i = rng.integers(n)
    for t in range(n):
        out[t] = x[i]
        i = rng.integers(n) if rng.random() < 1 / mean_block else (i + 1) % n
    return out


def _phase_randomise(x: np.ndarray, rng) -> np.ndarray:
    """Surrogate with the same periodogram (autocorrelation) and random Fourier phases."""
    n = len(x)
    f = np.fft.rfft(x - x.mean())
    ph = rng.uniform(0, 2 * np.pi, len(f))
    ph[0] = 0
    if n % 2 == 0:
        ph[-1] = 0
    return np.fft.irfft(np.abs(f) * np.exp(1j * ph), n) + x.mean()


def _pa(lam: np.ndarray, null: np.ndarray) -> int:
    """Number of leading eigenvalues above the null's 95th percentile (stop at the first failure)."""
    q = np.percentile(null, 95, axis=0)
    below = np.where(lam <= q)[0]
    return int(below[0]) if len(below) else len(lam)


def pr_block_ci(Z: np.ndarray, block: int, n_draws: int, rng) -> list[float]:
    """90% moving-block bootstrap interval of PR (rows resampled jointly)."""
    n = len(Z)
    nb = int(np.ceil(n / block))
    prs = []
    for _ in range(n_draws):
        starts = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        prs.append(_pr(_eig(Z[idx])))
    return [round(float(np.percentile(prs, 5)), 2), round(float(np.percentile(prs, 95)), 2)]


def eff_dim(X: pd.DataFrame, n_draws: int = N_DRAWS, full: bool = True) -> dict:
    Z = ((X - X.mean()) / X.std(ddof=1)).values
    n, M = Z.shape
    lam = _eig(Z)
    p = lam / lam.sum()
    share = np.cumsum(lam) / lam.sum()
    out = {
        "n_obs": int(n), "n_vars": int(M), "start": str(X.index.min().date()), "end": str(X.index.max().date()),
        "eigenvalues": [round(float(x), 3) for x in lam],
        "cum_share": [round(float(x), 3) for x in share],
        "participation_ratio": round(_pr(lam), 2),
        "entropy_eff_rank": round(float(np.exp(-np.sum(p * np.log(p)))), 2),
        "meff_li_ji_2005": round(float(np.sum((lam >= 1) + (lam - np.floor(lam)))), 2),
        "capped_eigenvalue_sum_adhoc": round(float(np.minimum(lam, 1).sum()), 2),
        "kaiser_gt1": int(np.sum(lam > 1)),
        "pcs_80pct": int(np.searchsorted(share, 0.80) + 1),
    }
    if not full:
        return out
    rng = np.random.default_rng(SEED)
    # 90% moving-block bootstrap interval for PR (rows resampled jointly, keeps cross-correlation)
    out["pr_block_boot_90ci"] = pr_block_ci(Z, BLOCK, n_draws, rng)
    # parallel analysis under serial-dependence-preserving nulls (columns made independent)
    sb = np.array([_eig(np.column_stack([_stationary_bootstrap(Z[:, j], rng, BLOCK) for j in range(M)]))
                   for _ in range(n_draws)])
    pr_ = np.array([_eig(np.column_stack([_phase_randomise(Z[:, j], rng) for j in range(M)]))
                    for _ in range(n_draws)])
    out["pa_stationary_block"] = _pa(lam, sb)
    out["pa_phase_randomised"] = _pa(lam, pr_)
    out["null_pr_95pct_stationary_block"] = round(float(np.percentile([_pr(x) for x in sb], 5)), 2)
    out["n_draws"] = n_draws
    return out


def clusters(X: pd.DataFrame, cut_rho: float) -> list[list[str]]:
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform
    R = X.corr(method="spearman").abs().values
    D = 1 - R
    np.fill_diagonal(D, 0)
    Lk = linkage(squareform(D, checks=False), method="average")
    lab = fcluster(Lk, t=1 - cut_rho, criterion="distance")
    groups = {}
    for c, l in zip(X.columns, lab):
        groups.setdefault(int(l), []).append(c)
    return sorted(groups.values(), key=len, reverse=True)


# Frozen before the 2026-10-17 revision; see COMBINATORICS.md section 3.1.
STRICT_PIT = ["indpro", "unrate", "rsxfs", "umcsent", "houst", "permit", "nhs", "m2", "busloans", "neworder",
              "t10y3m", "hy_ig", "gold_copper", "sox_spy"]
CORE23_DROP = ("eci", "vix_ratio", "cass", "inv_sales", "cement", "ism_svc")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    closes = month_closes()
    print("revised panel ...", flush=True)
    rev = revised_panel(closes).join(market_panel(closes))
    print("realtime panel ...", flush=True)
    rt = realtime_panel(closes)
    rev.to_csv(OUT / "panel_revised_asof_monthly.csv", float_format="%.5g")
    rt.to_csv(OUT / "panel_realtime_alfred_monthly.csv", float_format="%.5g")

    cov = pd.DataFrame({
        "block": {k: v[5] for k, v in SPEC.items()},
        "freq": {k: v[2] for k, v in SPEC.items()},
        "transform": {k: v[3] for k, v in SPEC.items()},
        "track_available": {k: {"alfred": "realtime+revised", "fred": "revised", "snap": "revised (no archive)",
                                "mkt": "market (unrevised)"}[v[0]] for k, v in SPEC.items()},
        "first_revised_asof": {c: (str(rev[c].first_valid_index().date()) if rev[c].notna().any() else "") for c in rev},
        "first_realtime": {c: str(rt[c].first_valid_index().date()) for c in rt},
    })
    # measured lags (calendar meta: ALFRED / publisher dates, fallback rows excluded); market series: 0-1 day
    meta = json.loads((REPO / "data/release_calendar/release_calendar_meta.json").read_text())["series"]
    for col, key in (("release_lag_median_d", "lag_median_d"), ("release_lag_p90_d", "lag_p90_d"),
                     ("release_dates_measured_from", "first_own_measured_ref"), ("n_fallback_rows", "n_fallback")):
        cov[col] = [meta.get(SPEC[k][4], {}).get(key) if SPEC[k][4] else None for k in cov.index]
    cov.to_csv(OUT / "coverage_and_lags.csv")

    summary = {"generated": "2026-10-17 (rev3)", "seed": SEED, "end": str(END.date()), "block_months": BLOCK,
               "primary_estimand": "participation_ratio on strict_pit14 with 90% moving-block bootstrap interval"}
    # PRIMARY: strict point-in-time panel (real-time vintages + unrevised market series)
    strict = rt[STRICT_PIT[:10]].join(rev[STRICT_PIT[10:]])
    strict.to_csv(OUT / "panel_strict_pit14_monthly.csv", float_format="%.5g")
    Xs = strict.dropna()
    summary["strict_pit14"] = eff_dim(Xs)
    summary["strict_pit14"]["vars"] = STRICT_PIT
    summary["strict_pit14"]["clusters_rho0.5"] = clusters(Xs, 0.5)
    summary["strict_pit14"]["clusters_rho0.7"] = clusters(Xs, 0.7)
    Zs = ((Xs - Xs.mean()) / Xs.std(ddof=1)).values
    rng_b = np.random.default_rng(SEED + 1)
    summary["strict_pit14"]["pr_ci_by_block_length"] = {str(b): pr_block_ci(Zs, b, N_DRAWS, rng_b)
                                                         for b in (12, 24, 36, 48)}
    Xs.corr(method="spearman").round(2).to_csv(OUT / "spearman_strict_pit14.csv")
    # SENSITIVITY: real-time ALFRED only; revised-as-of panels (not point-in-time); 3-month changes
    summary["realtime_long10"] = eff_dim(rt[STRICT_PIT[:10]].dropna())
    summary["realtime_all16"] = eff_dim(rt.dropna())
    core = [c for c in rev if c not in CORE23_DROP]
    for label, cols in {"revised_all29": list(rev.columns), "revised_core23": core}.items():
        X = rev[cols].dropna()
        summary[label] = eff_dim(X)
        summary[label]["clusters_rho0.7"] = clusters(X, 0.7)
        summary[label]["clusters_rho0.5"] = clusters(X, 0.5)
        X.corr(method="spearman").round(2).to_csv(OUT / f"spearman_{label}.csv")
    summary["strict_pit14_chg3m"] = eff_dim(strict.diff(3).dropna())
    summary["revised_core23_chg3m"] = eff_dim(rev[core].diff(3).dropna())
    # revision gap: realtime vs revised-as-of, per series, common months
    gap = {}
    for c in rt:
        j = pd.concat([rt[c], rev[c]], axis=1).dropna()
        if len(j) > 24:
            gap[c] = {"n": int(len(j)), "corr_rt_vs_revised": round(float(j.corr().iloc[0, 1]), 3),
                      "mean_abs_diff": round(float((j.iloc[:, 0] - j.iloc[:, 1]).abs().mean()), 3)}
    summary["realtime_vs_revised"] = gap
    R = rev.corr(method="spearman", min_periods=60)
    pairs = [(a, b, R.loc[a, b]) for i, a in enumerate(R) for b in R.columns[i + 1:] if pd.notna(R.loc[a, b])]
    pairs.sort(key=lambda x: -abs(x[2]))
    summary["top_abs_pairs_revised"] = [[a, b, round(float(r), 2)] for a, b, r in pairs[:25]]
    R.round(2).to_csv(OUT / "spearman_revised_pairwise.csv")
    (OUT / "effective_dimensionality.json").write_text(json.dumps(summary, indent=1))
    for k, v in summary.items():
        if isinstance(v, dict) and "n_obs" in v:
            print(k, {kk: vv for kk, vv in v.items() if kk not in ("eigenvalues", "cum_share", "vars")})


if __name__ == "__main__":
    main()
