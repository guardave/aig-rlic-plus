"""Exact size of the indicator-combination space (COMBINATORICS.md section 2). Counting only: no returns, no backtests.

Members are the 26 INDICATORS behind the 35 live registered pairs (new home sales SA and NSA counted once). Each
indicator's member grids come from the published tournament CSVs (`results/<pair>/tournament_results_*.csv`,
latest file per pair, buy-and-hold rows removed). An indicator with several pairs has its grids merged:
  upper bound = sum over its pairs (grids treated as disjoint), lower bound = largest single pair grid.

Per indicator i:
  m_i  rules        : distinct (signal, threshold, strategy, direction, lead, lookback) rows
  s_i  binary states: distinct (signal, threshold, direction, lead, lookback) among P1/P3 rows (P1 and P3 at the
                      same key produce the same bull/bear state; P2 is continuous and has no binary state)
  t_i  readings     : distinct (signal, lead, lookback)

Operators and their applicability (k = |S|), with deduplication:
  BOOL   (R1 confirmation, R2 plain filter, R5 binary divergence, R7 diffusion): every Boolean function of the k
         states that depends on all k inputs. Because the grid holds both directions (s and not-s), functions that
         differ only by negated inputs coincide: distinct series = |F_k| * prod s_i / 2^k.
           unate (economic) set: 2 (k=2), 9 (k=3) per prod s_i;  all functions: 2.5 (k=2), 27.25 (k=3).
         R2 plain filter (act on B only in A's stress state) equals an AND of states, and R7 on unweighted
         states equals k-of-n: both are already inside BOOL and add nothing.
  SEQ    (R4): ordered chain, window w in 6 values per link: k! * 6^(k-1) * prod s_i (events are not
         negation-symmetric, no division).
  REPAR  (R2 with regime-specific rules): regime member r (partition = s_r / 2, negation gives the same
         partition); every other member's rule differs by regime. k=2: sum_r (s_r/2) * m_b (m_b - 1).
         k=3: sum_r (s_r/2) * U (U - 1), U = 2 * prod_{others} s (the unate pair rule per regime).
  COMP   (R3): composite of readings, 3 weightings * 3 thresholds * 3 position rules: 27 * prod t_i.
  DIVC   (R5 continuous gap): k = 2 only; 2 measures * 3 thresholds: 6 * t_a t_b.
  SIZE   (R6): one sizing member j (reading) * 3 maps; direction from the others' states (k=2: s_d;
         k=3: unate pair rule 2 * s_d1 s_d2): 3 * sum_j t_j * dir_j.
Totals are sums over all subsets S of size k: sum_S prod_{i in S} x_i = e_k(x) (elementary symmetric polynomial),
computed exactly. Per target asset and per alignment; multiply by 20 assets x 3 alignments for the grand total.

Run from the repo root:  python docs/indicator_combos/scripts/combinatorics_exact.py
Output: docs/indicator_combos/data/combinatorics_exact.json
"""
from __future__ import annotations

import glob
import json
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "docs" / "indicator_combos" / "data" / "combinatorics_exact.json"
MARKET = {"gold_copper_xli": "gold_copper", "vix_vix3m_spy": "vix_ratio", "phlxsox_spy": "sox_spy",
          "hy_ig_spy": "hy_ig"}
SAME = {"HSN1F": "new_home_sales", "HSN1FNSA": "new_home_sales"}
BH = ("BUY_HOLD", "P0_buy_and_hold", "BH")


def live_pairs() -> dict[str, str]:
    reg = json.loads((REPO / "docs/schemas/lead_axis_registry.json").read_text())["pairs"]
    out = {}
    for p, v in reg.items():
        if p.endswith("_archived") or p == "hy_ig_spy_v1":
            continue
        sid = v.get("release_calendar_series") or ""
        out[p] = MARKET.get(p) or SAME.get(sid) or sid
    return out


def grid(pair: str) -> dict:
    f = sorted(glob.glob(str(REPO / f"results/{pair}/tournament_results_*.csv")))[-1]
    t = pd.read_csv(f)
    t = t[~t["strategy"].astype(str).isin(BH)].copy()
    lead = next(c for c in ("lead_months", "lead_days", "lead_quarters", "lead") if c in t)
    lb = t["lookback"].astype(str) if "lookback" in t else pd.Series("", index=t.index)
    st = t["strategy"].astype(str)
    if "direction" in t:
        d = t["direction"].astype(str)
    else:
        d = np.where(st.str.endswith("_counter"), "counter", np.where(st.str.endswith("_pro"), "pro", "fixed"))
    fam = st.str[:2]
    key_rule = pd.DataFrame({"s": t["signal"], "th": t["threshold"], "st": st, "d": d, "l": t[lead], "lb": lb})
    binm = fam.isin(["P1", "P3"]).values
    key_state = key_rule.loc[binm, ["s", "th", "d", "l", "lb"]]
    return {"file": Path(f).name, "m": int(len(key_rule.drop_duplicates())),
            "s": int(len(key_state.drop_duplicates())),
            "t": int(len(key_rule[["s", "l", "lb"]].drop_duplicates()))}


def e(x: np.ndarray, k: int) -> float:
    """Elementary symmetric polynomial e_k(x), exact up to float64 (sum over all k-subsets of products)."""
    E = np.zeros(k + 1)
    E[0] = 1.0
    for v in x:
        E[1:] = E[1:] + v * E[:-1]
    return float(E[k])


def space(ind: pd.DataFrame) -> dict:
    m, s, t = (ind[c].to_numpy(float) for c in ("m", "s", "t"))
    n = len(ind)
    out = {}
    for k in (2, 3):
        es, et = e(s, k), e(t, k)
        seq = comb(k, k) * {2: 2, 3: 6}[k] * 6 ** (k - 1) * es
        if k == 2:
            repar = sum((s[a] / 2) * m[b] * (m[b] - 1) + (s[b] / 2) * m[a] * (m[a] - 1)
                        for a, b in combinations(range(n), 2))
            divc = 6 * et
            size = 3 * sum(t[a] * s[b] + t[b] * s[a] for a, b in combinations(range(n), 2))
        else:
            repar = 0.0
            size = 0.0
            for a, b, c in combinations(range(n), 3):
                for r, (x, y) in ((a, (b, c)), (b, (a, c)), (c, (a, b))):
                    U = 2 * s[x] * s[y]
                    repar += (s[r] / 2) * U * (U - 1)
                    size += 3 * t[r] * 2 * s[x] * s[y]
            divc = 0.0
        bool_unate = {2: 2, 3: 9}[k] * es
        bool_all = {2: 2.5, 3: 27.25}[k] * es
        comp = 27 * et
        tot_unate = bool_unate + seq + repar + comp + divc + size
        out[f"k{k}"] = {
            "subsets": comb(n, k),
            "BOOL_unate": bool_unate, "BOOL_all_extra_nonunate": bool_all - bool_unate, "SEQ": seq,
            "REPAR": repar, "COMP": comp, "DIVC": divc, "SIZE": size,
            "total_per_asset_alignment": tot_unate,
            "total_x20assets_x3alignments": tot_unate * 60,
            "total_without_REPAR_per_asset_alignment": tot_unate - repar,
        }
    return out


def main():
    pairs = live_pairs()
    rows = []
    for p, ind in pairs.items():
        g = grid(p)
        rows.append({"pair": p, "indicator": ind, **g})
    pr = pd.DataFrame(rows)
    up = pr.groupby("indicator")[["m", "s", "t"]].sum()
    lo = pr.groupby("indicator")[["m", "s", "t"]].max()
    res = {
        "n_live_pairs": int(len(pr)), "n_indicators": int(pr.indicator.nunique()),
        "pairs": rows,
        "per_pair_m": {"median": float(pr.m.median()), "mean": float(pr.m.mean()), "sum": int(pr.m.sum())},
        "upper_bound_merge_sum": space(up), "lower_bound_merge_max": space(lo),
        "approx_median_grid": {f"k{k}": comb(26, k) * pr.m.median() ** k for k in (2, 3)},
        "approx_mean_grid": {f"k{k}": comb(26, k) * pr.m.mean() ** k for k in (2, 3)},
        "frozen_members_unate_per_asset_alignment": {
            "k2": comb(26, 2) * (2 + 12 + 27 + 6 + 6), "k3": comb(26, 3) * (9 + 216 + 27 + 3 * 3 * 2)},
    }
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print(pr.to_string())
    for b in ("upper_bound_merge_sum", "lower_bound_merge_max"):
        for k in ("k2", "k3"):
            print(b, k, {kk: f"{vv:.3g}" for kk, vv in res[b][k].items()})
    print(res["per_pair_m"], {k: f"{v:.3g}" for k, v in res["approx_median_grid"].items()},
          {k: f"{v:.3g}" for k, v in res["approx_mean_grid"].items()}, res["frozen_members_unate_per_asset_alignment"])


if __name__ == "__main__":
    main()
