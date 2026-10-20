"""D1-05 (EXPLORATORY run on historical point-in-time data): do term and credit spreads carry complementary
information? Registered hypotheses (frozen d780845f; this is NOT a V-C evaluation):
  H1 SPY: d < 0 in r(t+1) = a + b*term + c*credit + d*term*credit (expanding-z levels), margin 0.25 pp/month
  H2 SPY: joint-distress dummy J = 1{T10Y3M < 0.5 pp} * 1{HY-IG 6m change > 0} beyond the two additive dummies,
     margin 0.50 pp/month. The registry sets NO sign value for H2 (pass_rule *pr_inter says "registered sign" without
     one); d < 0 is INFERRED by Ray (J = 1 is the distress state), not registered (QA D1-05 F1).
  H3 Treasury proxy: same as H1, sign d > 0 (flight to quality), margin 0.10 pp/month
  H4 Treasury proxy: same as H2, sign d > 0, margin 0.20 pp/month

Design (first draft fixed in this header before the first run on 2026-10-18; revised 2026-10-20 before any result was
reported, see "Revision" below):
  * Signals at month-end t, known at the close: T10Y3M (pinned FRED, previous trading day), HY-IG OAS (local ICE
    BofA, previous trading day; first 2000-01, last valid month-end 2026-03). Expanding z-scores need >= 36 months,
    so the first z is 2002-12.
  * Targets over month t+1: SPY dividend-adjusted return minus the 3-month T-bill (DTB3 at t, /12); Treasury
    proxy = 10-year par-bond return from DGS10 at the month-end CLOSES t and t+1 (same window as SPY; the signals
    still use the previous trading day's values; QA D1-05 F5 fixed the earlier T-1 -> T+1-1 window) (carry y(t)/12 minus modified duration x change in yield; no
    convexity term) minus the same T-bill. Local data only (gap G6 built from local DGS10; G16 not acquired, so no
    pre-2000 history and no V-B Baa - Aaa supporting run).
  * Primary window: ONE common window for all 4 hypotheses (rows where every design and both targets exist).
    Each hypothesis on its own longest window is reported as a sensitivity.
  * Endpoint: the coefficient d. HAC t (Newey-West, 6 lags) and a one-sided stationary-bootstrap p (mean block 6,
    2000 draws, centred); the registered pass rule wants both <= 0.05 and |d| >= margin with the registered sign.
  * Multiplicity: family F-TC has 4 registered hypotheses. Registered exploratory correction: Romano-Wolf stepdown
    (stationary bootstrap, mean block 6, 2000 draws, rows resampled jointly, sign-aligned studentised statistics,
    centred as (d* - d_hat) / se*) over all 4. Also reported for comparability with other families: Holm over 4
    on the registered-test p (the larger of the HAC and bootstrap p).
  * Null tournament N1: term and credit circularly shifted together against the returns; ALL admissible offsets
    in [36, n - 37] enumerated exhaustively (n = 315 -> 243 distinct offsets, deterministic; QA D1-05 F2 replaced
    500 draws with replacement); percentile of the actual sign-aligned HC0 t among null HC0 t.
  * Purge: the registered purge_months = 1 holds by construction in the real-time loop: a row t enters training at
    refit T only if t < T, so its label (the return over t+1) is realised at or before the close of T.
  * Null N2 (registered: "random second market member"): credit replaced by each of 5 other unrevised market
    series from the same local file (VIX, DXY, log gold/copper, effective fed funds, log IWM/SPY), same expanding z,
    continuous design only (H1, H3); rank of the actual t among the 6, on their common window.
  * Regime episodes (H2/H4): runs of J = 1 separated by >= 3 months.
  * Descriptive: mean next-month excess return by sign quadrant of (z_term, z_credit), to show what the sign of d
    means in this parameterisation.
  * Real-time forecast comparison (naive baselines): expanding regressions re-estimated every January on rows whose
    t+1 return is realised; out-of-sample R^2 of the interaction model and of the additive model against the
    prevailing mean.
  * Overlay translation (for the B&H / best-single / naive-composite comparison required in Phase 2): long SPY when
    the real-time predicted excess return >= 0, else T-bill; prediction from the H1 regression re-estimated every
    January on data available then. B2a: the better of term-only / credit-only regressions by in-fold R^2 at each
    refit. B3: equal-weight expanding-z composite with prior signs (+term, -credit), long when >= 0. B4: SPY
    10-month SMA. Metrics: Sharpe, CVaR(5%), max drawdown, exposure, switches. No trading costs.
  * Post-hoc, descriptive only (no p-values): d with the 2008-09 crisis rows (2008-07..2009-06) and the 2020 rows
    (2020-02..2020-06) removed, one at a time.
Revision (2026-10-20, before reporting): common primary window; Romano-Wolf centring corrected to (d* - d_hat)/se*;
  Holm, N2, quadrant table, OOS R^2, switches and the post-hoc episode drop added; 'widen' set to NaN where credit is
  missing. The first-draft numbers were not reported anywhere (not verifiable from git: the draft was never committed).
Revision 2 (2026-10-20, after QA D1-05): H2 sign labelled inferred; N1 exhaustive over 243 offsets; Treasury target
  priced from close-T yields; post-hoc drop of the 12 flat-and-wide months.
Exploratory: numbers only, no verdict words.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p2data as d  # noqa: E402

OUT = d.P2 / "d1_05"
SEED = 20261018
B = 2000
K = "exhaustive"
MIN_Z = 36
N_FAMILY = 4
SIGN_SOURCE = {"H1": "registered", "H2": "inferred by Ray (registry sets no value)", "H3": "registered",
               "H4": "registered"}
SPEC = {"H1": ("spy", "cont", -1, 0.25), "H2": ("spy", "dummy", -1, 0.50),
        "H3": ("tsy", "cont", 1, 0.10), "H4": ("tsy", "dummy", 1, 0.20)}
EPISODES_POSTHOC = {"drop_2008_09": ("2008-07-31", "2009-06-30"), "drop_2020": ("2020-02-29", "2020-06-30")}


def daily():
    return pd.read_parquet(d.REPO / "data/hy_ig_spy_daily_20000101_20260422.parquet")


def zexp(s: pd.Series) -> pd.Series:
    """Expanding z-score using data up to and including t (known at the close)."""
    return (s - s.expanding(MIN_Z).mean()) / s.expanding(MIN_Z).std()


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df["z_term"], df["z_credit"] = zexp(df["term"]), zexp(df["credit"])
    df["flat"] = (df["term"] < 0.5).astype(float).where(df["term"].notna())
    ch = df["credit"] - df["credit"].shift(6)
    df["widen"] = (ch > 0).astype(float).where(ch.notna())
    df["J"] = df["flat"] * df["widen"]
    return df


def close_value(daily: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Value at the month-end close itself (used only for the Treasury-proxy TARGET, never for a signal)."""
    s = daily.dropna().sort_index()
    closes = d.last_trading_day(index)
    v = s.reindex(s.index.union(closes)).ffill().reindex(closes)
    out = pd.Series(v.to_numpy(), index=index)
    out[closes > s.index.max()] = np.nan
    return out


def build() -> pd.DataFrame:
    idx = d.month_index("2000-01-31")
    hy = daily()
    df = pd.DataFrame({"term": d.t10y3m(idx), "credit": d.hy_ig(idx),
                       "y10": close_value(hy["dgs10"], idx),
                       "tbill": d._prev_bday_month_end(hy["dtb3"], idx)})
    # Treasury proxy return over month t (from yields at t-1 and t)
    yl, y = df["y10"].shift(1) / 100, df["y10"] / 100
    md = (1 - (1 + yl / 2) ** -20) / yl          # modified duration of a 10-year par bond (semi-annual coupon)
    tsy = yl / 12 - md * (y - yl)
    spy = d.spy_monthly()["ret"].reindex(idx)
    rf = df["tbill"].shift(1) / 1200
    df["spy_x_next"] = (spy - rf).shift(-1) * 100            # pp, month t+1, known after t
    df["tsy_x_next"] = (tsy - rf).shift(-1) * 100
    # N2 pool: other unrevised market members (levels at the previous trading day's close)
    pv = lambda s: d._prev_bday_month_end(s, idx)  # noqa: E731
    df["n2_vix"] = pv(hy["vix"])
    df["n2_dxy"] = pv(hy["dxy"])
    df["n2_gold_copper"] = np.log(pv(hy["gold"]) / pv(hy["copper"]))
    df["n2_fed_funds"] = pv(hy["fed_funds_rate"])
    df["n2_iwm_spy"] = np.log(pv(hy["iwm"]) / pv(hy["spy"]))
    return add_signals(df)


def design(df: pd.DataFrame, kind: str, second: str = "credit") -> pd.DataFrame:
    if kind == "cont":
        zs = df["z_credit"] if second == "credit" else zexp(df[second])
        X = pd.DataFrame({"term": df["z_term"], "credit": zs, "inter": df["z_term"] * zs})
    else:
        X = pd.DataFrame({"flat": df["flat"], "widen": df["widen"], "inter": df["J"]})
    return sm.add_constant(X)


def stationary_idx(n: int, rng, mean_block: int = 6) -> np.ndarray:
    idx = np.empty(n, dtype=int)
    i = rng.integers(n)
    for t in range(n):
        idx[t] = i
        i = rng.integers(n) if rng.random() < 1 / mean_block else (i + 1) % n
    return idx


def ols_t(y: np.ndarray, X: np.ndarray) -> tuple[float, float]:
    """Coefficient and HC0 standard error of the last column."""
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    V = XtX @ (X.T * e ** 2) @ X @ XtX
    return b[-1], np.sqrt(V[-1, -1])


def test_one(m: pd.DataFrame, sign: int, seed: int) -> dict:
    r = sm.OLS(m.iloc[:, 0], m.iloc[:, 1:]).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    yv, Xv = m.iloc[:, 0].to_numpy(), m.iloc[:, 1:].to_numpy()
    dhat, se = ols_t(yv, Xv)
    rng = np.random.default_rng(seed)
    boot = np.array([ols_t(yv[ii], Xv[ii])[0] for ii in (stationary_idx(len(yv), rng) for _ in range(B))]) - dhat
    return {"window": f"{m.index[0].date()}..{m.index[-1].date()}", "months": int(len(m)),
            "d_pp_month": round(float(r.params["inter"]), 3), "hac_t": round(float(r.tvalues["inter"]), 2),
            "p_hac_one_sided": round(float(1 - norm.cdf(sign * r.tvalues["inter"])), 4),
            "p_stationary_bootstrap_one_sided": round(float(np.mean(sign * boot >= sign * dhat)), 4),
            "hc0_t": round(float(dhat / se), 2),
            "coefficients": {k: round(float(v), 3) for k, v in r.params.items()}, "r2": round(float(r.rsquared), 4)}


def episodes(flag: pd.Series, gap: int = 3) -> int:
    on = flag.fillna(0).to_numpy() > 0
    n, last_end, k = 0, -10 ** 9, 0
    while k < len(on):
        if on[k]:
            s = k
            while k < len(on) and on[k]:
                k += 1
            if s - last_end > gap:
                n += 1
            last_end = k - 1
        k += 1
    return n


def holm(pvals: dict, m: int) -> dict:
    order = sorted(pvals, key=pvals.get)
    adj, run = {}, 0.0
    for i, h in enumerate(order):
        run = max(run, min(1.0, (m - i) * pvals[h]))
        adj[h] = round(run, 4)
    return adj


def romano_wolf(data: dict, common: pd.DatetimeIndex) -> dict:
    rng = np.random.default_rng(SEED + 1)
    obs, est, tb = {}, {}, {h: [] for h in data}
    arrs = {}
    for h, (m, sign) in data.items():
        mm = m.loc[common]
        arrs[h] = (mm.iloc[:, 0].to_numpy(), mm.iloc[:, 1:].to_numpy(), sign)
        b, se = ols_t(arrs[h][0], arrs[h][1])
        est[h], obs[h] = b, sign * b / se
    n = len(common)
    for _ in range(B):
        ii = stationary_idx(n, rng)
        for h, (yv, Xv, sign) in arrs.items():
            b, se = ols_t(yv[ii], Xv[ii])
            tb[h].append(sign * (b - est[h]) / se)          # centred studentised statistic
    order = sorted(obs, key=lambda h: -obs[h])
    adj, run = {}, 0.0
    for i, h in enumerate(order):
        mx = np.max(np.column_stack([tb[k] for k in order[i:]]), axis=1)
        run = max(run, float(np.mean(mx >= obs[h])))
        adj[h] = round(run, 4)
    return {"window": f"{common[0].date()}..{common[-1].date()}", "months": n,
            "sign_aligned_hc0_t": {h: round(float(v), 2) for h, v in obs.items()}, "adjusted_p": adj}


def null_n1(df: pd.DataFrame, rows: pd.DatetimeIndex, actual: dict) -> dict:
    span = df.index[df[["term", "credit"]].notna().all(axis=1)]
    nulls = {h: [] for h in SPEC}
    offsets = range(36, len(span) - 36)
    for k in offsets:
        sh = df.copy()
        sh.loc[span, ["term", "credit"]] = np.roll(df.loc[span, ["term", "credit"]].to_numpy(), k, axis=0)
        sh = add_signals(sh)
        for h, (asset, kind, sign, _) in SPEC.items():
            m = pd.concat([sh[f"{asset}_x_next"], design(sh, kind)], axis=1).reindex(rows).dropna()
            b, se = ols_t(m.iloc[:, 0].to_numpy(), m.iloc[:, 1:].to_numpy())
            nulls[h].append(sign * b / se)
    out = {}
    for h, (_, _, sign, _) in SPEC.items():
        v = np.array(nulls[h])
        out[h] = {"statistic": "sign-aligned HC0 t", "distinct_offsets": len(offsets),
                  "percentile_sign_aligned_t": round(float(np.mean(v < sign * actual[h])) * 100, 1),
                  "null_quantiles": {q: round(float(np.quantile(v, q / 100)), 2) for q in (5, 50, 95)}}
    return out


def null_n2(df: pd.DataFrame) -> dict:
    members = ["credit"] + [c for c in df.columns if c.startswith("n2_")]
    zs = {c: (df["z_credit"] if c == "credit" else zexp(df[c])) for c in members}
    out = {}
    for h, (asset, kind, sign, _) in SPEC.items():
        if kind != "cont":
            continue
        y = df[f"{asset}_x_next"]
        ok = y.notna() & df["z_term"].notna() & pd.concat(zs, axis=1).notna().all(axis=1)
        rows = df.index[ok]
        ts = {}
        for c in members:
            X = sm.add_constant(pd.DataFrame({"term": df["z_term"], "second": zs[c], "inter": df["z_term"] * zs[c]}))
            b, se = ols_t(y[rows].to_numpy(), X.loc[rows].to_numpy())
            ts[c] = round(float(sign * b / se), 2)
        rank = 1 + sum(v > ts["credit"] for k, v in ts.items() if k != "credit")
        out[h] = {"window": f"{rows[0].date()}..{rows[-1].date()}", "months": int(len(rows)),
                  "sign_aligned_hc0_t": ts, "credit_rank_of_6": int(rank)}
    return out


def quadrants(df: pd.DataFrame, rows: pd.DatetimeIndex) -> dict:
    q = df.loc[rows]
    lab = np.where(q["z_term"] >= 0, "steep", "flat") + "_" + np.where(q["z_credit"] >= 0, "wide", "tight")
    out = {}
    for a in ("spy", "tsy"):
        g = q.groupby(lab)[f"{a}_x_next"]
        out[a] = {k: {"months": int(g.size()[k]), "mean_pp": round(float(g.mean()[k]), 2),
                      "sign_of_zterm_x_zcredit": "+" if k in ("steep_wide", "flat_tight") else "-"}
                  for k in sorted(g.size().index)}
    out["flat_wide_months"] = [str(t.date()) for t in q.index[lab == "flat_wide"]]
    return out


def perf(r: pd.Series) -> dict:
    r = r.dropna() / 100
    ann = r.mean() * 12
    sd = r.std(ddof=1) * np.sqrt(12)
    lvl = (1 + r).cumprod()
    q = np.quantile(r, 0.05)
    return {"months": int(len(r)), "ann_excess_return_pct": round(100 * ann, 2), "sharpe": round(ann / sd, 3),
            "cvar5_monthly_pct": round(-100 * r[r <= q].mean(), 2),
            "max_drawdown_pct": round(100 * (lvl / lvl.cummax() - 1).min(), 1)}


def realtime(df: pd.DataFrame) -> dict:
    """Real-time forecasts and overlays on SPY excess returns; positions decided at t, earn month t+1."""
    rows = df.index[df[["z_term", "z_credit", "spy_x_next"]].notna().all(axis=1)]
    keys = ("H1_model", "additive", "prevailing_mean", "B2a_best_single")
    fc = {k: pd.Series(np.nan, index=df.index) for k in keys}
    chosen = {}
    for T in [t for t in rows if t.month == 1 and t >= rows[0] + pd.offsets.MonthEnd(36)]:
        tr = rows[rows < T]                      # rows whose t+1 return is realised by the close of T
        cur = rows[(rows >= T) & (rows < T + pd.offsets.MonthEnd(12))]
        y = df.loc[tr, "spy_x_next"]
        X = design(df.loc[tr], "cont")
        fc["H1_model"].loc[cur] = design(df.loc[cur], "cont") @ sm.OLS(y, X).fit().params
        ba = sm.OLS(y, X[["const", "term", "credit"]]).fit().params
        fc["additive"].loc[cur] = design(df.loc[cur], "cont")[["const", "term", "credit"]] @ ba
        fc["prevailing_mean"].loc[cur] = y.mean()
        best, r2 = None, -np.inf
        for c in ("z_term", "z_credit"):
            rr = sm.OLS(y, sm.add_constant(df.loc[tr, [c]])).fit()
            if rr.rsquared > r2:
                best, r2, bb = c, rr.rsquared, rr.params
        chosen[str(T.date())] = best
        fc["B2a_best_single"].loc[cur] = bb["const"] + bb[best] * df.loc[cur, best]
    first = fc["H1_model"].first_valid_index()
    w = df.index[(df.index >= first) & df["spy_x_next"].notna()]
    yw = df.loc[w, "spy_x_next"]
    sse = {k: float(((yw - fc[k].reindex(w)) ** 2).sum()) for k in keys}
    oos = {"window": f"{w[0].date()}..{w[-1].date()}", "months": int(len(w)),
           "oos_r2_vs_prevailing_mean": {k: round(1 - sse[k] / sse["prevailing_mean"], 4)
                                         for k in ("H1_model", "additive", "B2a_best_single")},
           "oos_r2_interaction_vs_additive": round(1 - sse["H1_model"] / sse["additive"], 4)}
    pos = {"H1_model": (fc["H1_model"] >= 0).astype(float).where(fc["H1_model"].notna()),
           "B2a_best_single": (fc["B2a_best_single"] >= 0).astype(float).where(fc["B2a_best_single"].notna())}
    comp = (df["z_term"] - df["z_credit"]) / 2
    pos["B3_naive_composite"] = (comp >= 0).astype(float).where(comp.notna())
    p = d.spy_monthly()["spy_close"]
    pos["B4_sma"] = (p >= p.rolling(10).mean()).astype(float).where(p.rolling(10).mean().notna()).reindex(df.index)
    ov = {"window_signals": oos["window"], "costs": "none", "B1_buy_and_hold": perf(yw)}
    for k, v in pos.items():
        pw = v.reindex(w).fillna(0)
        ov[k] = {**perf(pw * yw), "exposure": round(float(pw.mean()), 3), "switches": int((pw.diff().abs() > 0).sum())}
    ov["B2a_choices"] = sorted(set(chosen.values()))
    return {"forecast": oos, "overlay_spy": ov}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT / "panel_monthly.csv", float_format="%.5g")
    res = {"status": "Exploratory", "question": "D1-05", "registry": "frozen d780845f; not a V-C evaluation",
           "family": "F-TC", "family_registered_hypotheses": N_FAMILY,
           "correction": "Romano-Wolf stepdown over 4 (registered); Holm over 4 also shown",
           "null": {"N1": {"type": "joint circular shift of term and credit", "offsets": "all 243 admissible, exhaustive"},
                    "N2": "credit replaced by each of 5 other market members (continuous design)"},
           "hypotheses": {}}
    full = {h: pd.concat([df[f"{a}_x_next"], design(df, k)], axis=1).dropna() for h, (a, k, _, _) in SPEC.items()}
    common = full["H1"].index
    for m in full.values():
        common = common.intersection(m.index)
    data, p_reg, actual = {}, {}, {}
    for i, (h, (asset, kind, sign, margin)) in enumerate(SPEC.items()):
        prim = test_one(full[h].loc[common], sign, SEED + 10 + i)
        own = test_one(full[h], sign, SEED + 20 + i)
        data[h] = (full[h], sign)
        p_reg[h] = max(prim["p_hac_one_sided"], prim["p_stationary_bootstrap_one_sided"])
        actual[h] = prim["hc0_t"]
        r = {"asset": "SPY" if asset == "spy" else "10y Treasury proxy (DGS10, G6)", "kind": kind,
             "test_sign": "d < 0" if sign < 0 else "d > 0", "sign_source": SIGN_SOURCE[h],
             "margin_pp_month": margin,
             "primary_common_window": prim, "sensitivity_own_window": own,
             "sign_matches_test_sign": bool(np.sign(prim["d_pp_month"]) == sign),
             "abs_d_vs_margin": round(abs(prim["d_pp_month"]) / margin, 2),
             "numeric_thresholds_of_registered_rule_met": bool(
                 p_reg[h] <= 0.05 and np.sign(prim["d_pp_month"]) == sign and abs(prim["d_pp_month"]) >= margin)}
        if kind == "dummy":
            r["J_months"] = int(df.loc[common, "J"].sum())
            r["J_episodes"] = episodes(df.loc[common, "J"])
        post = {}
        for tag, (a, b) in EPISODES_POSTHOC.items():
            keep = common[(common < pd.Timestamp(a)) | (common > pd.Timestamp(b))]
            rr = sm.OLS(full[h].loc[keep].iloc[:, 0], full[h].loc[keep].iloc[:, 1:]).fit(
                cov_type="HAC", cov_kwds={"maxlags": 6})
            post[tag] = {"months": int(len(keep)), "d_pp_month": round(float(rr.params["inter"]), 3),
                         "hac_t": round(float(rr.tvalues["inter"]), 2)}
        if kind == "cont":                                  # QA D1-05 F3: selection on X quadrants, not on y
            fw = common[((df.loc[common, "z_term"] < 0) & (df.loc[common, "z_credit"] >= 0)).to_numpy()]
            keep = common.difference(fw)
            rr = sm.OLS(full[h].loc[keep].iloc[:, 0], full[h].loc[keep].iloc[:, 1:]).fit(
                cov_type="HAC", cov_kwds={"maxlags": 6})
            post["drop_12_flat_wide_months"] = {"months": int(len(keep)), "d_pp_month": round(float(rr.params["inter"]), 3),
                                                "hac_t": round(float(rr.tvalues["inter"]), 2)}
        r["posthoc_episode_drop_descriptive"] = post
        res["hypotheses"][h] = r
        print(h, json.dumps({k: prim[k] for k in ("window", "d_pp_month", "hac_t", "p_stationary_bootstrap_one_sided")}),
              flush=True)
    res["primary_window"] = {"window": f"{common[0].date()}..{common[-1].date()}", "months": int(len(common))}
    res["romano_wolf"] = romano_wolf(data, common)
    res["holm_over_4_on_registered_test_p"] = {"p_used": p_reg, "adjusted_p": holm(p_reg, N_FAMILY)}
    n1 = null_n1(df, common, actual)
    for h in SPEC:
        res["hypotheses"][h]["null_N1"] = n1[h]
    res["null_N2"] = null_n2(df)
    res["quadrant_means_primary_window"] = quadrants(df, common)
    res.update(realtime(df))
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=str))
    for k in ("romano_wolf", "holm_over_4_on_registered_test_p", "null_N2", "forecast", "overlay_spy"):
        print(k, json.dumps(res[k]))


if __name__ == "__main__":
    main()
