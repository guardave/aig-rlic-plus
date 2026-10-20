"""Track records and artifact writers (plan section 2; app design section 12).

File names: MAIN keeps today's stems (tournament_results_<tag>.csv, strategy_returns_<tag>.csv, ...). The
COMPARISON (hindsight) track uses a `hindsight_` PREFIX instead of the plan's `_hindsight` suffix: the app
resolves the latest file with sorted(glob("tournament_results_*.csv"))[-1], and a suffixed name would sort
after the MAIN file and be picked as the headline.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import metrics as M
from . import prose
from .engine import TrackResult
from .inference import hac_t_mean, paired_block_bootstrap_sharpe_diff
from .spec import ISQuantile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

SCHEMA_VERSION = "1.3.0"
STRATEGY_FAMILY = {"P1": "P1_long_cash", "P2": "P2_signal_strength", "P3": "P3_long_short"}
TRACK_PREFIX = {"main": "", "comparison": "hindsight_"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso(ts) -> str | None:
    return None if ts is None or pd.isna(ts) else pd.Timestamp(ts).date().isoformat()


def _r(v, nd=6):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), nd)


def threshold_rule(direction: str, strict: bool) -> str:
    if direction == "countercyclical":
        return "lt" if strict else "lte"
    return "gt" if strict else "gte"


def winner_series(res: TrackResult, idx) -> pd.DataFrame:
    """Per-row signal, threshold, position, deployable strategy and benchmark returns of a table row."""
    spec, c = res.spec, res.cands[int(idx)]
    from .candidates import p2_col, thr_col, x_col
    lag = res.lagged.get(c.lead)
    j = int(idx)
    pos = res.positions[:, j]
    sig = thr = np.full(len(res.index), np.nan)
    if lag is not None:
        if c.strategy == "P2":
            sig = lag[p2_col(c.signal)].to_numpy(float)
        else:
            rule = spec.rules(c.signal)[c.threshold]
            sig = lag[x_col(c.signal, rule.x_name)].to_numpy(float)
            if isinstance(rule.thr, ISQuantile):
                from .positions import is_quantile_threshold
                thr = is_quantile_threshold(sig, ~res.oos_mask, rule.thr)
            elif callable(rule.thr):
                thr = lag[thr_col(c.signal, c.threshold)].to_numpy(float)
            else:
                thr = np.full(len(sig), float(rule.thr))
    sr = res.deployable_returns(j)
    br = np.nan_to_num(res.ret, nan=0.0)
    sample = np.where(res.oos_mask, "OOS", np.where(res.is_mask, "IS", "pre_IS"))
    out = pd.DataFrame({"date": res.index, "signal": sig, "threshold": thr, "position": pos,
                        "strategy_return": sr, "benchmark_return": br, "sample": sample})
    out["strategy_equity"] = (1 + out["strategy_return"]).cumprod()
    out["benchmark_equity"] = (1 + out["benchmark_return"]).cumprod()
    return out


def track_record(res: TrackResult, signal_display: dict, null_summary: dict | None = None,
                 bootstrap: bool = True) -> dict:
    """Everything one track publishes about its winner (winner_summary.tracks.<track>)."""
    spec = res.spec
    tab = res.table
    lead_unit = spec.lead_unit
    base = {"track": res.name, "lead_unit": lead_unit, "lead_column": spec.lead_col,
            "n_candidates": int(len(tab)), "n_eligible": int(tab["is_eligible"].sum()),
            "n_valid": int(tab["valid"].sum()), "n_distinct": int(res.n_distinct),
            "sample": dict(res.meta)}
    if res.selection is None:
        firsts = [r for r in tab["own_is_start"].dropna()] if "own_is_start" in tab else []
        base.update({"eligible": False, "winner": None,
                     "insufficient_reason": {
                         "rt_start": min(firsts) if firsts else None,
                         "n_is_rows": int(tab["own_is_n"].max()) if "own_is_n" in tab and len(tab) else 0,
                         "min_required": spec.min_is_n}})
        return base
    w = res.selection["winner"]
    row = tab.loc[w]
    ws = winner_series(res, w)
    oos = ws.loc[res.oos_mask]
    pw = M.perf(oos["strategy_return"].to_numpy(), spec.ppy)
    pb = M.perf(oos["benchmark_return"].to_numpy(), spec.ppy)
    thr_last = ws["threshold"].dropna()
    tr, to = M.trades(res.positions[:, int(w)], res.oos_mask, spec.trade_count, spec.ppy)
    raw = tab.loc[res.raw_idx] if res.raw_idx is not None else row
    rec = dict(base)
    rec.update({
        "eligible": True,
        "winner": {"key": row["key"], "signal": row["signal"], "signal_column": row["signal_column"],
                   "signal_display": signal_display.get(row["signal"], row["signal"]),
                   "threshold": row["threshold"],
                   "threshold_value": _r(thr_last.iloc[-1]) if len(thr_last) else None,
                   "threshold_rule": threshold_rule(row["direction"], spec.strict_counter),
                   "direction": row["direction"], "strategy": row["strategy"],
                   "strategy_family": STRATEGY_FAMILY[row["strategy"]], "lead": int(row["lead"]),
                   "is_sharpe": _r(row["is_sharpe"]), "oos_sharpe": _r(pw["sharpe"]),
                   "oos_sortino": _r(pw["sortino"]), "oos_calmar": _r(pw["calmar"]),
                   "oos_ann_return": _r(pw["ann_return"]), "oos_ann_vol": _r(pw["ann_vol"]),
                   "oos_max_drawdown": _r(pw["max_drawdown"]), "oos_win_rate": _r(pw["win_rate"]),
                   "oos_n_trades": tr, "annual_turnover": _r(to),
                   "oos_exposure": _r(M.exposure(res.positions[:, int(w)], res.oos_mask, row["strategy"])),
                   "source_row_index": int(w)},
        "bh_is": {k: _r(v) for k, v in res.bh_is.items()},
        "bh_oos": {k: _r(v) for k, v in pb.items()},
        "is_window": [_iso(res.common_is_start), _iso(res.index[res.is_mask][-1])],
        "oos_window": [_iso(res.index[res.oos_mask][0]), _iso(res.index[-1])],
        "is_n": int(res.is_mask.sum()), "oos_n": int(res.oos_mask.sum()),
        "objective": res.selection["rule"],
        "plateau": {"leads": res.selection.get("window_leads", [int(row["lead"])]),
                    "score": _r(res.selection.get("score", row["is_sharpe"])),
                    "winner_lead": int(row["lead"]),
                    "global_max_lead": res.selection.get("family_max_lead"),
                    "global_max_inside_plateau": res.selection.get("family_max_inside_window"),
                    "grid_edge": res.selection.get("grid_edge"),
                    "single_window_grid": res.selection.get("single_window_grid"),
                    "tie": res.selection.get("tie"),
                    "family": res.selection.get("family")},
        "raw_argmax": {"key": raw["key"], "signal": raw["signal"], "threshold": raw["threshold"],
                       "strategy": raw["strategy"], "direction": raw["direction"], "lead": int(raw["lead"]),
                       "is_sharpe": _r(raw["is_sharpe"]), "oos_sharpe": _r(raw["oos_sharpe"]),
                       "note": "highest single in-sample Sharpe in the grid; reference only, not the selection rule"},
        "runner_up": _runner_up(tab, res.selection.get("runner_up")),
        "spearman_is_oos": _r(tab.loc[tab["valid"], ["is_sharpe", "oos_sharpe"]].corr("spearman").iloc[0, 1], 4)
        if tab["valid"].sum() > 2 else None,
    })
    held = pd.Series(res.positions[:, int(w)]).shift(spec.position_shift).fillna(0.0).to_numpy()
    cost = np.abs(np.diff(held, prepend=0.0)) * 5e-4          # 5 bp per unit of position change, charged when it takes effect
    net = M.perf((ws["strategy_return"].to_numpy() - cost)[res.oos_mask], spec.ppy)
    rec["winner"]["oos_sharpe_net_5bp"] = _r(net["sharpe"])
    if bootstrap:
        bs = paired_block_bootstrap_sharpe_diff(oos["strategy_return"].to_numpy(), oos["benchmark_return"].to_numpy(),
                                                spec.bootstrap_block, spec.ppy)
        rec["vs_buy_hold"] = dict(bs, sharpe_diff=bs["observed"],
                                  ann_return={"strat": _r(pw["ann_return"]), "bh": _r(pb["ann_return"])},
                                  ann_vol={"strat": _r(pw["ann_vol"]), "bh": _r(pb["ann_vol"])},
                                  max_dd={"strat": _r(pw["max_drawdown"]), "bh": _r(pb["max_drawdown"])})
        rec["hac"] = {"oos_strategy_mean": hac_t_mean(oos["strategy_return"].to_numpy()),
                      "oos_excess_mean": hac_t_mean((oos["strategy_return"] - oos["benchmark_return"]).to_numpy())}
    rec["undefined_tail"] = undefined_tail(ws, res.oos_mask, spec.ppy, pw["sharpe"], spec.position_shift)
    if null_summary is not None:
        rec["null_tournament"] = null_summary
    return rec


def undefined_tail(ws: pd.DataFrame, oos_mask: np.ndarray, ppy: int, oos_sharpe: float,
                   position_shift: int = 0) -> dict | None:
    """Trailing test periods whose RETURN comes from an undefined position (no published reading: the fleet rule
    holds cash), and the test-period Sharpe had the last defined position been held instead (a SENSITIVITY, not the
    rule; QA pilot-visual H1 / Lead ruling: undefined means cash stays). With position_shift = 1 the position of row
    t earns row t+1's return, so an undefined position on the last row earns nothing in the sample and is not a cash
    period (permit_spy B1). None when every test-period return comes from a defined position."""
    held_all = ws["position"].shift(position_shift)
    o = ws.loc[oos_mask].reset_index(drop=True)
    pos = held_all.loc[oos_mask].reset_index(drop=True)
    k = 0
    for v in pos.iloc[::-1]:
        if pd.isna(v):
            k += 1
        else:
            break
    if k == 0 or k == len(o):
        return None
    last = float(pos.iloc[len(o) - k - 1])
    held = o["strategy_return"].to_numpy(float).copy()
    br = o["benchmark_return"].to_numpy(float)
    held[len(o) - k:] = last * br[len(o) - k:]        # the same holding, no trade: no extra cost
    return {"n_periods": int(k), "first_date": _iso(o["date"].iloc[len(o) - k]),
            "last_date": _iso(o["date"].iloc[-1]), "last_defined_position": _r(last),
            "benchmark_return_over_tail": _r(float(np.prod(1 + br[len(o) - k:]) - 1)),
            "oos_sharpe_as_published": _r(oos_sharpe),
            "oos_sharpe_hold_last_position": _r(M.perf(held, ppy)["sharpe"]),
            "rule": "undefined signal = cash (pre-registered fleet rule); the hold-last figure is a sensitivity"}


def _runner_up(tab: pd.DataFrame, ru: dict | None) -> dict | None:
    """Second-best D9 plateau winner (winner of the next-ranked window whose winner differs); objective_value is
    that window's plateau score J, like the winner's selection.J."""
    if not ru:
        return None
    r = tab.loc[ru["index"]]
    return {"signal": r["signal"], "threshold": r["threshold"], "strategy": r["strategy"], "lead_value": int(r["lead"]),
            "objective": "plateau_score_J", "objective_value": _r(ru["score"]), "window_leads": ru["window_leads"],
            "is_sharpe": _r(r["is_sharpe"]), "oos_sharpe": _r(r["oos_sharpe"])}


def tournament_frame(res: TrackResult) -> pd.DataFrame:
    """Published tournament CSV: candidate rows (+ track, plateau_j, ranks) and one BENCHMARK row."""
    spec = res.spec
    t = res.table.copy()
    t.insert(0, "track", res.name)
    nb = t["valid"]
    t["is_rank"] = t["is_sharpe"].where(nb).rank(ascending=False, method="min")
    t["oos_rank"] = t["oos_sharpe"].where(nb).rank(ascending=False, method="min")
    t["selected"] = False
    if res.selection is not None:
        t.loc[res.selection["winner"], "selected"] = True
    t["raw_is_argmax"] = False
    if res.raw_idx is not None:
        t.loc[res.raw_idx, "raw_is_argmax"] = True
    bm = {"track": res.name, "signal": "BENCHMARK", "signal_column": "target", "threshold": "BUY_HOLD",
          "strategy": "BUY_HOLD", "lead": 0, "direction": "benchmark", "is_sharpe": res.bh_is["sharpe"],
          "is_ann_return": res.bh_is["ann_return"], "is_max_drawdown": res.bh_is["max_drawdown"],
          "oos_sharpe": res.bh_oos["sharpe"], "oos_ann_return": res.bh_oos["ann_return"],
          "max_drawdown": res.bh_oos["max_drawdown"], "is_n": res.bh_is["n"], "oos_n": res.bh_oos["n"],
          "is_exposure": 1.0, "is_eligible": False, "valid": False, "is_valid": False,
          "common_is_start": _iso(res.common_is_start), "key": "BENCHMARK"}
    t = pd.concat([t, pd.DataFrame([bm])], ignore_index=True)
    return t.rename(columns={"lead": spec.lead_col})


def lead_curve(res: TrackResult) -> pd.DataFrame:
    """IS and OOS Sharpe of the winner's tuple at every executable lead, plateau flag and J (R6.9)."""
    if res.selection is None:
        return pd.DataFrame(columns=["lead", "is_sharpe", "oos_sharpe", "valid", "plateau_j", "in_plateau",
                                     "winner", "raw_is_argmax"])
    fam = res.selection["family"]
    t = res.table
    m = np.ones(len(t), bool)
    for k, v in fam.items():
        m &= (t[k] == v).to_numpy()
    sub = t[m & t["is_eligible"].to_numpy()].sort_values("lead")
    out = pd.DataFrame({"lead": sub["lead"].astype(int), "is_sharpe": sub["is_sharpe"],
                        "oos_sharpe": sub["oos_sharpe"], "valid": sub["valid"], "plateau_j": sub["plateau_j"]})
    out["in_plateau"] = out["lead"].isin(res.selection["window_leads"])
    out["winner"] = sub.index == res.selection["winner"]
    out["raw_is_argmax"] = sub.index == res.raw_idx
    best = t[t["valid"]].groupby("lead")["is_sharpe"].max()
    out["best_valid_is_sharpe_at_lead"] = out["lead"].map(best)
    out.insert(0, "track", res.name)
    return out.rename(columns={"lead": res.spec.lead_col})


def trade_log(ws: pd.DataFrame, instrument: str, cost_bps: int, reason: str) -> pd.DataFrame:
    """One row per position change. quantity_pct = target weight AFTER the trade in percent (the fleet broker-style
    convention, scripts/_trade_log_broker.py, and the Strategy page's column dictionary); trade_size_pct = size of
    the trade in percent of capital (QA B1 umcsent M2). A position held from the first row is logged as an entry
    from flat."""
    pos = ws.set_index("date")["position"].fillna(0.0)
    sig = ws.set_index("date")["signal"]
    thr = ws.set_index("date")["threshold"]
    before = pos.shift(1).fillna(0.0)
    ch = pos - before
    rows = []
    for dt, d in ch[ch != 0].items():
        undefined = pd.isna(sig.loc[dt]) and pd.isna(ws.set_index("date")["position"].loc[dt])
        rows.append({"trade_date": dt.date().isoformat(), "side": "BUY" if d > 0 else "SELL",
                     "instrument": instrument, "quantity_pct": float(pos.loc[dt]) * 100,
                     "trade_size_pct": abs(float(d)) * 100, "commission_bps": cost_bps,
                     "signal_value": _r(sig.loc[dt]), "threshold_value": _r(thr.loc[dt]),
                     "position_before": float(before.loc[dt]), "position_after": float(pos.loc[dt]),
                     "reason": ("signal undefined (no published reading for this month): cash under the "
                                "undefined-means-cash rule") if undefined else reason})
    return pd.DataFrame(rows)


def validate(instance: dict, schema_name: str) -> list[str]:
    """Validate against docs/schemas/<schema_name>.schema.json (empty list = valid)."""
    from validate_schema import validate_json
    schema = json.loads((REPO / "docs" / "schemas" / f"{schema_name}.schema.json").read_text())
    return validate_json(instance, schema)


def write_json(path: Path, obj: dict, schema_name: str | None = None) -> None:
    if schema_name:
        errs = validate(obj, schema_name)
        if errs:
            raise ValueError(f"{path.name} fails {schema_name}.schema.json: {errs[:5]}")
    path.write_text(json.dumps(obj, indent=2, default=_json_default) + "\n")


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (pd.Timestamp,)):
        return o.isoformat()
    raise TypeError(type(o))


def jsonable(obj):
    """Round-trip through JSON so numpy scalars / NaN become plain JSON values."""
    return json.loads(json.dumps(obj, default=_json_default).replace("NaN", "null"))
