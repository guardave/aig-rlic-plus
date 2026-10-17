"""One tournament on one track: manifest -> positions -> scoring -> eligibility -> validity -> selection."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import metrics as M
from .candidates import Candidate, distinct_series, manifest
from .positions import position_matrix, strategy_returns
from .selection import common_is_start, plateau_select, raw_argmax
from .spec import PairSpec


@dataclass
class TrackInputs:
    """Lagged rule inputs of one track on the rebalance index. ret[u] is the target return of row u."""
    name: str                          # real_time | revised | market | legacy
    index: pd.DatetimeIndex
    ret: np.ndarray
    lagged: dict[int, pd.DataFrame]
    meta: dict = field(default_factory=dict)


@dataclass
class TrackResult:
    name: str
    spec: PairSpec
    index: pd.DatetimeIndex
    ret: np.ndarray
    cands: list[Candidate]
    positions: np.ndarray
    returns: np.ndarray
    table: pd.DataFrame
    common_is_start: pd.Timestamp | None
    is_mask: np.ndarray
    oos_mask: np.ndarray
    selection: dict | None
    raw_idx: int | None
    bh_is: dict
    bh_oos: dict
    n_distinct: int = 0
    collapse: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
    lagged: dict = field(default_factory=dict)

    @property
    def winner_idx(self):
        return None if self.selection is None else self.selection["winner"]

    def column(self, idx) -> int:
        return int(idx)

    def deployable_returns(self, idx) -> np.ndarray:
        """Full-history deployable strategy returns of a table row (NaN -> cash 0)."""
        return np.nan_to_num(self.returns[:, self.column(idx)], nan=0.0)


def _date(index, row) -> str | None:
    return None if row is None or row < 0 or row >= len(index) else index[row].date().isoformat()


def any_eligible(spec: PairSpec, ti: TrackInputs) -> bool:
    """True when at least one candidate meets the R3.3 eligibility rule (own IS returns >= min_is_n) on these
    inputs: the usable-training-window test of the real-time null's admissible offsets (harness.null)."""
    cands = manifest(spec)
    pre_oos = ~np.asarray(ti.index >= pd.Timestamp(spec.oos_start))
    by_lead: dict[int, list[int]] = {}
    for j, c in enumerate(cands):
        by_lead.setdefault(c.lead, []).append(j)
    P = np.full((len(ti.index), len(cands)), np.nan)
    for lead, cols in by_lead.items():
        P[:, cols] = position_matrix(spec, ti.lagged[lead], [cands[j] for j in cols], pre_oos, "expanding")
    R = strategy_returns(P, ti.ret, spec.position_shift)
    return bool((np.sum(~np.isnan(R) & pre_oos[:, None], axis=0) >= spec.min_is_n).any())


def run_tournament(spec: PairSpec, ti: TrackInputs, legacy: bool = False, full_table: bool = True) -> TrackResult:
    """legacy=True replays the pre-harness pipeline (spec.legacy scoring, eligibility and tie rule, raw IS argmax);
    otherwise Phase B rules: R3.3 eligibility, deployable scoring, D9 plateau selection with a raw-argmax side row."""
    L = spec.legacy
    cands = manifest(spec, legacy=legacy)
    idx = ti.index
    n = len(idx)
    oos_mask = np.asarray(idx >= pd.Timestamp(spec.oos_start))
    pre_oos = ~oos_mask
    P = np.full((n, len(cands)), np.nan)
    by_lead: dict[int, list[int]] = {}
    for j, c in enumerate(cands):
        by_lead.setdefault(c.lead, []).append(j)
    for lead, cols in by_lead.items():
        P[:, cols] = position_matrix(spec, ti.lagged[lead], [cands[j] for j in cols], pre_oos,
                                     L.is_quantile if legacy else "expanding")
    R = strategy_returns(P, ti.ret, spec.position_shift)

    first = M.first_valid(R)
    own_is_n = np.sum(~np.isnan(R) & pre_oos[:, None], axis=0)
    elig_mode = L.eligibility if legacy else "own_is_n"
    cs_row, eligible = common_is_start(first, own_is_n, spec.min_is_n, elig_mode)
    rows = np.arange(n)
    is_mask = (rows >= cs_row) & pre_oos if cs_row >= 0 else np.zeros(n, bool)
    if legacy and L.is_window == "own_dropna":      # legacy: every candidate on its own pre-OOS rows (dropna)
        is_mask = pre_oos.copy()
    is_sc = L.is_scoring if legacy else "deployable"
    oos_sc = L.oos_scoring if legacy else "deployable"
    ann = L.ann_return if legacy else "geometric"

    Xi = M.window(R, is_mask, is_sc)
    is_n, is_sd, is_sh = M.col_sharpe(Xi, spec.ppy)
    Xo = M.window(R, oos_mask, oos_sc)
    oos_n, _osd, oos_sh = M.col_sharpe(Xo, spec.ppy)

    lo, hi = spec.exposure_bounds
    recs = []
    for j, c in enumerate(cands):
        pos = P[:, j]
        expo = M.exposure(pos, is_mask, c.strategy)
        tr, to = M.trades(pos, is_mask, spec.trade_count, spec.ppy)
        ok = bool(eligible[j] and is_n[j] >= spec.min_is_n and lo <= expo <= hi and is_sd[j] > 0)
        if spec.max_is_turnover is not None:
            ok = ok and to < spec.max_is_turnover
        if spec.min_is_trades is not None:
            ok = ok and tr >= spec.min_is_trades
        rec = {"signal": c.signal, "signal_column": spec.signals[c.signal], "threshold": c.threshold,
               "strategy": c.strategy, "lead": c.lead, "direction": c.direction,
               "is_sharpe": float(is_sh[j]), "is_exposure": expo, "is_n_trades": tr, "is_annual_turnover": to,
               "is_n": int(is_n[j]), "oos_sharpe": float(oos_sh[j]), "oos_n": int(oos_n[j]),
               "is_eligible": bool(eligible[j]), "valid": ok, "key": c.key}
        # ECON-T3 tie-break fields are computed in every run, null draws included (Codex B0 LOW)
        ri = Xi[:, j]
        pi = M.perf(ri, spec.ppy, ann)
        rec.update({"is_ann_return": pi["ann_return"], "is_max_drawdown": pi["max_drawdown"]})
        if full_table:
            ro = Xo[:, j]
            po = M.perf(ro, spec.ppy, ann)
            isr = np.flatnonzero(is_mask)[~np.isnan(ri)] if is_sc == "dropna" else np.flatnonzero(is_mask)
            own = (rows >= first[j]) & pre_oos
            Xw = M.window(R[:, [j]], own, is_sc)[:, 0]
            pw = M.perf(Xw, spec.ppy, ann)
            otr, oto = M.trades(pos, oos_mask, spec.trade_count, spec.ppy)
            own_ok = bool(pw["n"] >= spec.min_is_n and lo <= M.exposure(pos, own, c.strategy) <= hi
                          and np.nanstd(Xw) > 0)
            rec.update({
                "is_start": _date(idx, isr[0] if len(isr) else None), "is_end": _date(idx, isr[-1] if len(isr) else None),
                "common_is_start": _date(idx, cs_row), "own_is_start": _date(idx, int(first[j])),
                "own_is_sharpe": pw["sharpe"], "own_is_n": pw["n"], "own_is_valid": own_ok,
                "oos_sortino": po["sortino"], "oos_calmar": po["calmar"], "oos_ann_return": po["ann_return"],
                "oos_ann_vol": po["ann_vol"], "max_drawdown": po["max_drawdown"], "win_rate": po["win_rate"],
                "oos_exposure": M.exposure(pos, oos_mask, c.strategy), "n_trades": otr, "annual_turnover": oto,
                "is_ineligible_reason": "" if eligible[j] else
                f"insufficient IS history: n_own={int(own_is_n[j])} < MIN_IS_N={spec.min_is_n}",
                "is_valid": ok})
        recs.append(rec)
    table = pd.DataFrame(recs)
    if legacy and L.round_table is not None:
        for k in ("is_sharpe", "oos_sharpe", "is_ann_return", "is_max_drawdown"):
            if k in table:
                table[k] = table[k].round(L.round_table)

    if legacy:
        sel_idx = raw_argmax(table, L.tie_break)
        selection = None if sel_idx is None else {"winner": sel_idx, "rule": "raw_is_argmax"}
        raw_idx = sel_idx
    else:
        selection = plateau_select(table)
        if selection is not None:
            selection["rule"] = "max_is_sharpe_lead_plateau_w3"
        raw_idx = raw_argmax(table, "cascade")

    bh_is = M.perf(ti.ret[is_mask], spec.ppy, ann)
    bh_oos = M.perf(ti.ret[oos_mask], spec.ppy, ann)
    n_distinct, collapse = (distinct_series(P, table["valid"].to_numpy()) if full_table else (0, {}))
    return TrackResult(ti.name, spec, idx, ti.ret, cands, P, R, table,
                       idx[cs_row] if cs_row >= 0 else None, is_mask, oos_mask, selection, raw_idx,
                       bh_is, bh_oos, n_distinct, collapse, dict(ti.meta), ti.lagged if full_table else {})


def score_candidate(res: TrackResult, key: str) -> dict | None:
    """Cross-evaluation: a candidate's IS / OOS Sharpe on this track's own windows (None if not in the manifest)."""
    hit = res.table.index[res.table["key"] == key]
    if not len(hit):
        return None
    r = res.table.loc[hit[0]]
    return {"is_sharpe": float(r["is_sharpe"]), "oos_sharpe": float(r["oos_sharpe"]), "valid": bool(r["valid"]),
            "is_eligible": bool(r["is_eligible"]),
            "window": {"is_start": None if res.common_is_start is None else res.common_is_start.date().isoformat(),
                       "oos_start": res.spec.oos_start, "oos_end": res.index[-1].date().isoformat()}}
