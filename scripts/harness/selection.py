"""Selection: eligibility and common IS start (R3.3), raw IS argmax (legacy / side row), D9 lead plateau (R5.7).

D9 (plan section 0, decision 8): for every candidate tuple (signal, threshold, position rule, direction), each
window of 3 ADJACENT grid leads (by grid position, edge-clamped, never wrapping; the whole grid when it has
fewer than 3 executable leads) is scored by the MINIMUM IS Sharpe over its leads. Neighbours enter the minimum
whether or not they pass the validity filters (R5.7); a window must contain at least one valid candidate. The
best-scoring window over all tuples is the plateau (ties: the window holding the higher raw IS, then manifest
order). The winner is the valid lead with the highest raw IS Sharpe inside the plateau (ties: ECON-T3 keys,
then the lower lead). The raw IS argmax is kept as a labelled side row.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TIE_KEYS = ["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades"]


def common_is_start(first_row: np.ndarray, own_is_n: np.ndarray, min_is_n: int, mode: str) -> tuple[int, np.ndarray]:
    """(common IS start row, eligible mask). mode own_is_n: R3.3 eligibility before alignment;
    none: legacy, the start is the latest first-valid row over ALL candidates and everyone is eligible."""
    if mode == "none":
        eligible = np.ones(len(first_row), bool)
    elif mode == "own_is_n":
        eligible = own_is_n >= min_is_n
    else:
        raise ValueError(mode)
    if not eligible.any():
        return -1, eligible
    return int(first_row[eligible].max()), eligible


def raw_argmax(table: pd.DataFrame, tie_break: str = "cascade") -> int | None:
    """Index label of the valid row with the highest IS Sharpe. first: manifest order (pandas idxmax);
    cascade: ECON-T3 keys (IS Sharpe, IS return, IS max drawdown, IS trades), then names."""
    valid = table[table["valid"]]
    if valid.empty:
        return None
    if tie_break == "first":
        return valid["is_sharpe"].idxmax()
    keys = [k for k in TIE_KEYS if k in valid] + ["signal", "threshold", "strategy", "lead"]
    asc = [False] * len([k for k in TIE_KEYS if k in valid]) + [True] * 4
    return valid.sort_values(keys, ascending=asc, kind="mergesort").index[0]


def windows(grid_len: int) -> list[tuple[int, ...]]:
    """Windows of 3 adjacent grid positions, edge-clamped (no wrap); the whole grid if it has < 3 points."""
    if grid_len <= 0:
        return []
    if grid_len < 3:
        return [tuple(range(grid_len))]
    return [(i, i + 1, i + 2) for i in range(grid_len - 2)]


def own_window(i: int, grid_len: int) -> tuple[int, ...]:
    """R5.7 W(i): the clamped window centred on grid position i (used for the per-candidate J column)."""
    if grid_len < 3:
        return tuple(range(grid_len))
    c = min(max(i, 1), grid_len - 2)
    return (c - 1, c, c + 1)


def plateau_select(table: pd.DataFrame) -> dict | None:
    """D9 selection over a tournament table with columns signal, threshold, strategy, direction, lead, is_sharpe,
    valid, is_eligible (+ TIE_KEYS). Adds column `plateau_j` (R5.7 J on each candidate's own window) to `table`
    in place. Returns the winner index, plateau window and audit fields, or None when nothing is valid."""
    fam_cols = ["signal", "threshold", "strategy", "direction"]
    jcol: dict = {}
    wins = []     # (score, raw_in_window, -order, family_key, window_leads, valid rows)
    order = 0
    for fam, g in table[table["is_eligible"]].groupby(fam_cols, sort=False):
        g = g.sort_values("lead")
        s = g["is_sharpe"].fillna(0.0).to_numpy()
        val = g["valid"].to_numpy()
        idx = g.index.to_numpy()
        G = len(g)
        for i in range(G):
            jcol[idx[i]] = float(s[list(own_window(i, G))].min())
        for w in windows(G):
            w = list(w)
            if not val[w].any():
                continue
            wins.append((float(s[w].min()), float(s[w][val[w]].max()), -order, fam,
                         [int(x) for x in g["lead"].to_numpy()[w]], idx[w][val[w]]))
            order += 1
    table["plateau_j"] = pd.Series(jcol, dtype=float).reindex(table.index)
    if not wins:
        return None
    wins.sort(key=lambda t: (t[0], t[1], t[2]), reverse=True)

    def window_winner(rows):
        sub = table.loc[rows]
        keys = [k for k in TIE_KEYS if k in sub]
        return sub.sort_values(keys + ["lead"], ascending=[False] * len(keys) + [True], kind="mergesort").index[0]

    score, _raw, _o, fam, wleads, rows = wins[0]
    winner = window_winner(rows)
    runner = None   # second-best D9 plateau winner: the next-ranked window whose winner is a different candidate
    for t in wins[1:]:
        cand = window_winner(t[5])
        if cand != winner:
            runner = {"index": cand, "score": t[0], "window_leads": t[4]}
            break
    famrows = table[(table[fam_cols] == pd.Series(dict(zip(fam_cols, fam)))).all(axis=1) & table["is_eligible"]]
    fam_valid = famrows[famrows["valid"]]
    gmax = fam_valid["is_sharpe"].idxmax() if len(fam_valid) else winner
    return {"winner": winner, "family": dict(zip(fam_cols, fam)), "window_leads": wleads, "score": score,
            "runner_up": runner,
            "family_max_lead": int(table.loc[gmax, "lead"]),
            "family_max_inside_window": int(table.loc[gmax, "lead"]) in wleads,
            "grid_edge": int(table.loc[winner, "lead"]) in (int(famrows["lead"].min()), int(famrows["lead"].max())),
            "single_window_grid": len(famrows) < 3}
