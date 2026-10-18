"""D1-27 (EXPLORATORY run on historical point-in-time data): real-time recession-probability horse race.

Registered hypotheses (registry frozen at d780845f; this run is NOT their V-C / V-S evaluation):
  H1 term + credit, H2 term + Sahm gap, H3 term + credit + Sahm gap + permits YoY, each vs the term-only probit.

Design (all choices fixed in this header before the first run):
  * Monthly decision index (month-end closes). Predictors as known at the close: T10Y3M (FRED, previous trading
    day), HY-IG OAS (local ICE BofA file, from 2000-01, previous trading day), Sahm gap (UNRATE vintages), PERMIT
    YoY (vintages). See p2data.py.
  * Label y(t) = 1 if any NBER recession month falls in (t, t+12].
  * Label availability: a row s enters training at refit date T only if s + 12 + 24 months <= T (12-month label
    window plus a conservative 24-month allowance for NBER announcement lags).
  * Expanding-window probit, refit every January month-end, predictors standardised on the training rows, L2
    penalty 0.01 on slopes for numerical stability (few positives). Predictions for the 12 months after each refit.
  * Comparator (registered): term-only probit fitted on the SAME training rows. Also reported: term-only on its
    full available history.
  * Evaluation rows: predictions whose label is fully observed (t <= 2025-09). Windows start at the first January refit
    with >= 2 labelled positives at or after 1988-01 (H2) / 2005-01 (H1, H3); in practice 1988-01 and 2006-01. Sensitivity "ex2020": excluding rows whose
    label window touches the 2020 recession (t <= 2019-02). It is POST-HOC: the frozen registry (d780845f) defines
    no such sensitivity for D1-27 (only "V-D" as descriptive), and this header was not committed before the first
    run. It is reported only as a labelled post-hoc sensitivity, never beside the primary full-window result.
  * Endpoint: Brier skill score vs term-only; one-sided p from a circular block bootstrap (block 24, 2000 draws) of
    the monthly Brier-loss difference; Holm across the 7 registered F-REC hypotheses (unrun ones count as p = 1).
  * Null tournament (N1): the added predictors are circularly shifted together (offset uniform in [36, n - 36]
    months, K = 500, seed 20261018) against term and labels; percentile of the actual BSS among null BSS.
  * Baselines: B1 base rate; B2a best single-predictor probit (highest training log-likelihood among the members);
    B3 equal-weight expanding-z composite (prior signs) through a one-slope probit; B4 SPY-below-10-month-SMA flag
    through a one-slope probit (from 1993-10).
Exploratory: no verdict words; numbers only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p2data as d  # noqa: E402

OUT = d.P2 / "d1_27"
SEED = 20261018
H = 12
LAG = 24
LAST_LABELLED = pd.Timestamp("2025-09-30")
EX2020_END = pd.Timestamp("2019-02-28")
SIGNS = {"term": -1, "credit": 1, "sahm": 1, "permit": -1}
MODELS = {"H1": ["term", "credit"], "H2": ["term", "sahm"], "H3": ["term", "credit", "sahm", "permit"]}
EVAL_START = {"H1": "2005-01-31", "H2": "1988-01-31", "H3": "2005-01-31"}
N_FAMILY = 7


def probit_fit(X: np.ndarray, y: np.ndarray, lam: float = 0.01) -> np.ndarray:
    Xc = np.column_stack([np.ones(len(X)), X])

    def nll(b):
        p = np.clip(norm.cdf(Xc @ b), 1e-10, 1 - 1e-10)
        return -(y * np.log(p) + (1 - y) * np.log(1 - p)).sum() + 0.5 * lam * np.sum(b[1:] ** 2)

    b0 = np.zeros(Xc.shape[1])
    b0[0] = norm.ppf(np.clip(y.mean(), 0.01, 0.99))
    return minimize(nll, b0, method="BFGS").x


def probit_pred(b: np.ndarray, X: np.ndarray) -> np.ndarray:
    return norm.cdf(np.column_stack([np.ones(len(X)), X]) @ b)


def labels(index: pd.DatetimeIndex) -> pd.Series:
    rec = d.nber_monthly(pd.date_range(index[0], index[-1] + pd.offsets.MonthEnd(H), freq="ME"))
    return pd.Series([int(rec.iloc[i + 1:i + 1 + H].max()) for i in range(len(index))], index=index)


def realtime_predictions(panel: pd.DataFrame, y: pd.Series, cols: list[str], start: str, kind: str = "probit"):
    """Annual-refit expanding probit; returns predictions on rows >= start (NaN where predictors missing)."""
    pred = pd.Series(np.nan, index=panel.index)
    refits = [t for t in panel.index if t.month == 1 and t >= pd.Timestamp(start)]
    for T in refits:
        known = panel.index[panel.index <= T - pd.offsets.MonthEnd(H + LAG)]
        tr = panel.loc[known, cols].dropna()
        ytr = y.loc[tr.index].to_numpy(float)
        if len(tr) < 36 or ytr.sum() < 2:
            continue
        mu, sd = tr.mean(), tr.std(ddof=1).replace(0, 1)
        Z = ((tr - mu) / sd).to_numpy()
        if kind == "composite":
            Z = (Z * np.array([SIGNS[c] for c in cols])).mean(axis=1, keepdims=True)
        b = probit_fit(Z, ytr)
        rows = panel.index[(panel.index >= T) & (panel.index < T + pd.offsets.MonthEnd(12))]
        Xp = panel.loc[rows, cols]
        ok = Xp.notna().all(axis=1)
        Zp = ((Xp[ok] - mu) / sd).to_numpy()
        if kind == "composite":
            Zp = (Zp * np.array([SIGNS[c] for c in cols])).mean(axis=1, keepdims=True)
        pred.loc[Xp.index[ok]] = probit_pred(b, Zp)
    return pred


def base_rate(panel: pd.DataFrame, y: pd.Series, start: str) -> pd.Series:
    pred = pd.Series(np.nan, index=panel.index)
    for T in [t for t in panel.index if t.month == 1 and t >= pd.Timestamp(start)]:
        known = y.index[y.index <= T - pd.offsets.MonthEnd(H + LAG)]
        rows = panel.index[(panel.index >= T) & (panel.index < T + pd.offsets.MonthEnd(12))]
        pred.loc[rows] = y.loc[known].mean()
    return pred


def best_single(panel, y, cols, start):
    """At each refit, the single-predictor probit with the highest training log-likelihood (members of the model)."""
    pred = pd.Series(np.nan, index=panel.index)
    chosen = {}
    for T in [t for t in panel.index if t.month == 1 and t >= pd.Timestamp(start)]:
        known = panel.index[panel.index <= T - pd.offsets.MonthEnd(H + LAG)]
        best, bestll = None, -np.inf
        for c in cols:
            tr = panel.loc[known, [c]].dropna()
            ytr = y.loc[tr.index].to_numpy(float)
            if len(tr) < 36 or ytr.sum() < 2:
                continue
            mu, sd = tr.mean(), tr.std(ddof=1).replace(0, 1)
            b = probit_fit(((tr - mu) / sd).to_numpy(), ytr)
            p = np.clip(probit_pred(b, ((tr - mu) / sd).to_numpy()), 1e-10, 1 - 1e-10)
            ll = (ytr * np.log(p) + (1 - ytr) * np.log(1 - p)).sum()
            if ll > bestll:
                best, bestll = (c, b, mu, sd), ll
        if best is None:
            continue
        c, b, mu, sd = best
        chosen[str(T.date())] = c
        rows = panel.index[(panel.index >= T) & (panel.index < T + pd.offsets.MonthEnd(12))]
        Xp = panel.loc[rows, [c]].dropna()
        pred.loc[Xp.index] = probit_pred(b, ((Xp - mu) / sd).to_numpy())
    return pred, chosen


def scores(p: pd.Series, y: pd.Series) -> dict:
    m = p.notna()
    pp, yy = np.clip(p[m].to_numpy(), 1e-4, 1 - 1e-4), y[m].to_numpy(float)
    brier = float(np.mean((pp - yy) ** 2))
    logs = float(np.mean(yy * np.log(pp) + (1 - yy) * np.log(1 - pp)))
    lg = np.log(pp / (1 - pp))
    slope = np.nan
    if yy.sum() > 0 and yy.sum() < len(yy):
        bb = minimize(lambda b: -np.sum(yy * (b[0] + b[1] * lg) - np.log1p(np.exp(b[0] + b[1] * lg))),
                      [0.0, 1.0], method="BFGS").x
        slope = float(bb[1])
    return {"n": int(m.sum()), "positives": int(yy.sum()), "brier": round(brier, 5), "mean_log_score": round(logs, 5),
            "calibration_slope": None if np.isnan(slope) else round(slope, 3)}


def block_boot_p(diff: np.ndarray, block: int = 24, draws: int = 2000, seed: int = SEED) -> float:
    """One-sided p for mean(diff) < 0 (model better): share of centred circular-block-bootstrap means <= observed."""
    rng = np.random.default_rng(seed)
    n = len(diff)
    obs = diff.mean()
    c = diff - obs
    nb = int(np.ceil(n / block))
    bm = np.empty(draws)
    for i in range(draws):
        idx = np.concatenate([np.arange(s, s + block) % n for s in rng.integers(0, n, nb)])[:n]
        bm[i] = c[idx].mean()
    return float(np.mean(bm <= obs))


def episode_gains(pm: pd.Series, pt: pd.Series, y: pd.Series) -> dict:
    """Per recession: summed log-score gain (model minus term-only) over the rows whose label window (t, t+12]
    overlaps the recession months (peak, trough], i.e. t in [peak - 11 months, trough)."""
    out = {}
    for pk, tr in d.recession_episodes():
        rows = y.index[(y.index >= pk - pd.offsets.MonthEnd(H - 1)) & (y.index < tr)]
        m = pm.reindex(rows).notna() & pt.reindex(rows).notna()
        if m.sum() < 6:
            continue
        r = rows[m.to_numpy()]
        a, b = np.clip(pm[r].to_numpy(), 1e-4, 1 - 1e-4), np.clip(pt[r].to_numpy(), 1e-4, 1 - 1e-4)
        yy = y[r].to_numpy(float)
        g = (yy * np.log(a) + (1 - yy) * np.log(1 - a)) - (yy * np.log(b) + (1 - yy) * np.log(1 - b))
        out[str(pk.date())[:7]] = round(float(g.sum()), 3)
    return out


def holm(pvals: dict, m: int) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    adj, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        adj[k] = round(run, 4)
    return adj


def null_bss(panel, y, cols, start, end, K=500):
    added = [c for c in cols if c != "term"]
    rng = np.random.default_rng(SEED)
    span = panel[added].dropna().index
    n = len(span)
    out = []
    for _ in range(K):
        k = int(rng.integers(36, n - 36))
        sh = panel.copy()
        vals = panel.loc[span, added].to_numpy()
        sh.loc[span, added] = np.roll(vals, k, axis=0)
        pm = realtime_predictions(sh, y, cols, start)
        pt = realtime_predictions(sh.where(sh[cols].notna().all(axis=1)), y, ["term"], start)
        w = pm.index[(pm.index >= pd.Timestamp(start)) & (pm.index <= end)]
        m = pm[w].notna() & pt[w].notna()
        bm = np.mean((pm[w][m] - y[w][m]) ** 2)
        bt = np.mean((pt[w][m] - y[w][m]) ** 2)
        out.append(1 - bm / bt)
    return np.array(out)


def main(K: int = 500):
    OUT.mkdir(parents=True, exist_ok=True)
    idx = d.month_index("1982-01-31")
    panel = pd.concat([d.t10y3m(idx), d.hy_ig(idx), d.sahm_gap(idx), d.permit_yoy(idx), d.spy_sma_flag(idx)], axis=1)
    y = labels(idx)
    panel.join(y.rename("y_rec_next12")).to_csv(OUT / "panel_pit_monthly.csv", float_format="%.5g")
    res = {"status": "Exploratory", "question": "D1-27", "registry": "frozen d780845f; not a V-C/V-S evaluation",
           "family": "F-REC", "family_registered_hypotheses": N_FAMILY, "correction": "Holm over 7 (unrun = p 1)",
           "label": "NBER recession month in (t, t+12]", "label_lag_months": LAG, "refit": "annual (January)",
           "null": {"type": "N1 circular shift of added predictors", "K": K, "seed": SEED}, "models": {}}
    preds, pv = {}, {}
    for h, cols in MODELS.items():
        start = EVAL_START[h]
        need = panel[cols].notna().all(axis=1)
        sub = panel.where(need)
        pm = realtime_predictions(sub, y, cols, start)
        pt_same = realtime_predictions(sub, y, ["term"], start)
        pt_full = realtime_predictions(panel, y, ["term"], start)
        b1 = base_rate(sub, y, start)
        b2, chosen = best_single(sub, y, cols, start)
        b3 = realtime_predictions(sub, y, cols, start, kind="composite")
        b4 = realtime_predictions(panel.where(need & panel["sma_flag"].notna()), y, ["sma_flag"], start)
        r = {"members": cols, "eval_start": start}
        for tag, end in (("full", LAST_LABELLED), ("ex2020", EX2020_END)):
            w = y.index[(y.index >= pd.Timestamp(start)) & (y.index <= end)]
            m = pm[w].notna() & pt_same[w].notna()
            ww = w[m.to_numpy()]
            rec_in = [str(pk.date())[:7] for pk, tr in d.recession_episodes()
                      if any((ww >= pk - pd.offsets.MonthEnd(H - 1)) & (ww < tr))]
            sc = {k: scores(v.reindex(ww), y.reindex(ww)) for k, v in
                  {"model": pm, "term_only_same_rows": pt_same, "term_only_full_history": pt_full, "B1_base_rate": b1,
                   "B2a_best_single": b2, "B3_naive_composite": b3}.items()}
            m4 = b4.reindex(ww).notna()
            sc["B4_sma_flag_subwindow"] = scores(b4.reindex(ww)[m4], y.reindex(ww)[m4]) if m4.sum() > 24 else None
            diff = ((pm[ww] - y[ww]) ** 2 - (pt_same[ww] - y[ww]) ** 2).to_numpy()
            bss = 1 - sc["model"]["brier"] / sc["term_only_same_rows"]["brier"]
            r[tag] = {"window": f"{ww[0].date()}..{ww[-1].date()}", "months": len(ww),
                      "recessions_covered": rec_in, "recessions_count": len(rec_in), "scores": sc,
                      "bss_vs_term_same_rows": round(float(bss), 4),
                      "bss_vs_term_full_history": round(
                          float(1 - sc["model"]["brier"] / sc["term_only_full_history"]["brier"]), 4),
                      "bss_vs_B2a": round(float(1 - sc["model"]["brier"] / sc["B2a_best_single"]["brier"]), 4),
                      "bss_vs_B3": round(float(1 - sc["model"]["brier"] / sc["B3_naive_composite"]["brier"]), 4),
                      "bss_vs_B1": round(float(1 - sc["model"]["brier"] / sc["B1_base_rate"]["brier"]), 4),
                      "p_block_bootstrap_one_sided": round(block_boot_p(diff), 4),
                      "episode_log_score_gain_vs_term": episode_gains(pm.reindex(ww), pt_same.reindex(ww), y)}
        r["B2a_choices"] = chosen
        if K:
            nb = null_bss(sub, y, cols, start, LAST_LABELLED, K)
            r["null_bss_percentile_full"] = round(float(np.mean(nb < r["full"]["bss_vs_term_same_rows"]) * 100), 1)
            r["null_bss_quantiles"] = {q: round(float(np.quantile(nb, q / 100)), 4) for q in (5, 50, 95)}
        pv[h] = r["full"]["p_block_bootstrap_one_sided"]
        res["models"][h] = r
        preds[h] = pm
        preds[f"{h}_term_same"] = pt_same
        print(h, json.dumps({k: r["full"][k] for k in ("window", "recessions_count", "bss_vs_term_same_rows",
                                                       "p_block_bootstrap_one_sided")}), flush=True)
    res["holm_adjusted_p_full"] = holm(pv, N_FAMILY)
    pd.DataFrame(preds).join(y.rename("y")).to_csv(OUT / "predictions.csv", float_format="%.5g")
    (OUT / "results.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(K=int(sys.argv[1]) if len(sys.argv) > 1 else 500)
