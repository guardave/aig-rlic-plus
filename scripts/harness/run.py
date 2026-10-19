"""Runner: legacy replay, two-track tournament, null, inference, leak tests and artifacts for one pair.

    python scripts/harness/run.py <pair_id> --tag YYYYMMDD [--K 100] [--replay-only] [--no-write]

The pair is declared in scripts/pair_spec_<pair_id>.py (SPEC, SIGNAL_DISPLAY and the data accessors
revised_levels / rebalance_index / target_return / legacy_panel). The pair's pipeline calls run_pair() and keeps
its own evidence stages and charts.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from harness import artifacts as A  # noqa: E402
from harness import charts  # noqa: E402  (installs the chart-input recorder before any data is read; Codex V51-3)
from harness import leak as LK  # noqa: E402
from harness import null as NL  # noqa: E402
from harness import prose  # noqa: E402
from harness.align import load_vintages  # noqa: E402
from harness.candidates import manifest, manifest_record  # noqa: E402
from harness.data import latest_levels, legacy_inputs, realtime_inputs, revised_inputs  # noqa: E402
from harness.engine import TrackResult, run_tournament, score_candidate  # noqa: E402

REPO = HERE.parents[1]
NBER = [("1990-07-31", "1991-03-31", "1990-91 recession"), ("2001-03-31", "2001-11-30", "2001 recession"),
        ("2007-12-31", "2009-06-30", "2008-09 recession"), ("2020-02-29", "2020-04-30", "2020 recession")]


def load_pair(pair_id: str):
    return importlib.import_module(f"pair_spec_{pair_id}")


# ---------------------------------------------------------------------------------------------------- replay
LEGACY_FILES = ("tournament_results_{tag}.csv", "legacy_oos_selection_{tag}.csv", "strategy_returns_{tag}.csv")


def not_replayable(mod) -> dict:
    """Checklist 1 for a pair whose published rule cannot be replayed through the harness (the pair declares
    LEGACY_REPLAY = None, e.g. an OOS-selected legacy tournament without a strategy_returns file). The report states
    the missing files, the published rule and how it was selected, the definitional differences, and the pair's
    verbatim legacy-code reproduction. Acceptance 4.1 passes only when that reproduction exists and its gaps are
    explained in writing (a 'gaps' text)."""
    spec = mod.SPEC
    tag = mod.LEGACY_TAG
    rdir = REPO / "results" / spec.pair_id
    missing = [f.format(tag=tag) for f in LEGACY_FILES if not (rdir / f.format(tag=tag)).exists()]
    repro_fn = getattr(mod, "legacy_reproduction", None)
    repro = repro_fn() if callable(repro_fn) else None
    pub = dict(getattr(mod, "LEGACY_PUBLISHED", {}) or {})
    if pub:
        pub.setdefault("selection", "published (OOS-selected, legacy method)")
        pub.setdefault("is_sharpe", None)
        pub.setdefault("tag", tag)
    documented = bool(repro and str(repro.get("gaps", "")).strip())
    return {"pair_id": spec.pair_id, "legacy_tag": tag, "status": "not_replayable", "pass": None,
            "reason": getattr(mod, "LEGACY_REPLAY_REASON", ""), "missing_files": missing,
            "published": pub or None, "definitional_differences": list(getattr(mod, "LEGACY_DIFFERENCES", [])),
            "legacy_reproduction": repro,
            "acceptance_4_1": {"pass": bool(documented and pub),
                               "rule": "not replayable + documented legacy-code reproduction (gaps explained)"}}


def _strategy_code(s) -> str:
    """Published strategy label -> harness code: 'P2_signal_strength' -> 'P2'; tables without a P-code
    (single-strategy legacy pipelines) are long/cash, P1."""
    head = str(s).split("_")[0]
    return head if head in ("P1", "P2", "P3") else "P1"


def legacy_unpublished(mod) -> frozenset:
    """Legacy table columns a pair declares were never published (LEGACY_UNPUBLISHED, a tuple / list of column
    names; umcsent_spy 20260912: its is_sharpe column held OOS values). A bare string or other type raises
    (QA EF2: a string was silently ignored)."""
    v = getattr(mod, "LEGACY_UNPUBLISHED", ())
    if not isinstance(v, (tuple, list, frozenset, set)) or not all(isinstance(c, str) for c in v):
        raise TypeError(f"LEGACY_UNPUBLISHED must be a tuple / list of column names, got {v!r}")
    return frozenset(v)


def published_value(rec, pub: pd.DataFrame, w, wrow, col: str, unpublished=frozenset()) -> float | None:
    """A previously published statistic: the immutable record's value, else the published table row's, else (only
    when neither has it) the harness replay's. None for a column the pair declares never published."""
    if col in unpublished:
        return None
    for src in (rec, pub.loc[w] if w in pub.index else None):
        if src is not None and col in src and pd.notna(src[col]):
            return float(src[col])
    return float(wrow[col])


def replay_legacy(mod, tol: float = 1e-6) -> dict:
    """Checklist 1: replay the published rule through the harness and compare with the committed artifacts.
    A pair that declares LEGACY_REPLAY = None gets the not_replayable report instead (see not_replayable)."""
    if hasattr(mod, "LEGACY_REPLAY") and mod.LEGACY_REPLAY is None:
        return not_replayable(mod)
    spec = getattr(mod, "LEGACY_SPEC", mod.SPEC)
    panel, ret = mod.legacy_panel()
    res = run_tournament(spec, legacy_inputs(spec, panel, ret.to_numpy(float)), legacy=True)
    rdir = REPO / "results" / spec.pair_id
    tag = mod.LEGACY_TAG
    pub = pd.read_csv(rdir / f"tournament_results_{tag}.csv")
    pub = pub[pub["signal"] != "BENCHMARK"].reset_index(drop=True)
    tab = res.table
    rep = {"pair_id": spec.pair_id, "legacy_tag": tag, "n_rows_harness": int(len(tab)), "n_rows_published": int(len(pub)),
           "tolerance": tol, "columns": {}}
    same_keys = (len(tab) == len(pub) and (tab["signal"].values == pub["signal"].values).all()
                 and (tab["threshold"].values == pub["threshold"].values).all()
                 and (tab["lead"].values == pub[spec.lead_col].values).all()
                 and (tab["strategy"].values == pub["strategy"].map(_strategy_code).values).all())
    rep["same_candidate_rows_in_order"] = bool(same_keys)
    # published precision: hy_ig rounds exposure to 4 dp and turnover to 3 dp; compare at the published precision
    prec = {"is_exposure": 4e-4 if spec.legacy.round_table else tol, "is_annual_turnover": 1e-3}
    for col in ["is_sharpe", "oos_sharpe", "is_n", "oos_n", "is_exposure", "n_trades", "is_n_trades", "is_annual_turnover"]:
        if col in pub and col in tab and same_keys:
            d = np.abs(tab[col].astype(float).to_numpy() - pub[col].astype(float).to_numpy())
            mx = float(np.nanmax(d)) if len(d) else 0.0
            rep["columns"][col] = {"max_abs_diff": mx, "pass": bool(mx <= prec.get(col, tol))}
    if same_keys:
        rep["valid_flags_equal"] = bool((tab["valid"].to_numpy() == pub["valid"].to_numpy()).all())
        if "common_is_start" in pub:                                   # older tables do not record it
            rep["common_is_start_equal"] = bool((tab["common_is_start"].to_numpy() == pub["common_is_start"].to_numpy()).all())
    method = spec.legacy.selection
    if method == "max_oos_valid":
        if not same_keys:
            raise ValueError("max_oos_valid replay needs the harness rows in the published order")
        # the published row was picked on OUT-OF-SAMPLE Sharpe among the legacy-valid rows (legacy `valid`:
        # OOS > 0, full-history turnover < 24); taken from the immutable published table, first in order on ties
        cand = pub[pub["valid"].astype(str).str.lower().isin(["true", "1"])]
        if "annual_turnover" in cand:
            cand = cand[cand["annual_turnover"].astype(float) < 24]
        cand = cand[cand["oos_sharpe"].astype(float) > 0]
        w = int(cand["oos_sharpe"].astype(float).idxmax())
        label = "published (selected on out-of-sample Sharpe, legacy method)"
    elif method == "is_argmax":
        w = res.selection["winner"]
        label = "raw in-sample Sharpe argmax, revised values, fixed lag"
    else:
        raise ValueError(f"unknown Legacy.selection {method!r}")
    rep["selection_method"] = method
    sel_f = rdir / f"legacy_oos_selection_{tag}.csv"                 # immutable record of the published pick
    if sel_f.exists():
        sel = pd.read_csv(sel_f)
        role = "primary_is_selected_common_start" if method == "is_argmax" else "published_oos_selected"
        p = (sel[sel["role"] == role] if "role" in sel and (sel["role"] == role).any() else sel).iloc[0]
    else:
        p = pub.loc[w]
    wrow = tab.loc[w]
    pdir = p["direction"] if "direction" in p else wrow["direction"]    # single-orientation tables omit it
    rep["winner"] = {"harness": wrow["key"], "published": f"{p['signal']}|{p['threshold']}|{pdir}|{int(p[spec.lead_col])}",
                     "match": bool(wrow["signal"] == p["signal"] and wrow["threshold"] == p["threshold"]
                                   and wrow["direction"] == pdir and int(wrow["lead"]) == int(p[spec.lead_col])
                                   and ("strategy" not in p or wrow["strategy"] == _strategy_code(p["strategy"])))}
    # previous_* report what was PUBLISHED (the immutable record, else the published table row), not the harness
    # replay: on the max_oos_valid path the IS columns are documented differences (QA B1 umcsent L1: replay IS
    # 0.3107 vs published 0.2825); the replay values are kept next to them for the record
    unpublished = legacy_unpublished(mod)

    def _published(col):
        return published_value(p, pub, w, wrow, col, unpublished)
    rep["published"] = {"key": wrow["key"], "signal": str(wrow["signal"]), "threshold": str(wrow["threshold"]),
                        "strategy": str(wrow["strategy"]), "direction": str(wrow["direction"]), "lead": int(wrow["lead"]),
                        "is_sharpe": _published("is_sharpe"), "oos_sharpe": _published("oos_sharpe"),
                        "replay_is_sharpe": float(wrow["is_sharpe"]), "replay_oos_sharpe": float(wrow["oos_sharpe"]),
                        "tag": tag, "selection": label}
    sr = pd.read_csv(rdir / f"strategy_returns_{tag}.csv")
    d = np.abs(res.deployable_returns(w) - sr["strategy_return"].to_numpy(float))
    rep["strategy_return"] = {"rows": int(len(sr)), "max_abs_diff": float(d.max()), "pass": bool(d.max() <= tol)}
    if method == "max_oos_valid":
        # The legacy `valid` flag is OOS-based (OOS > 0, turnover < 24) and the published pick used it directly;
        # the harness legacy flag is IS-based, so the two are reported, not required. The IS columns depend on
        # legacy NaN-position handling (undefined signal -> 0 / -1 kept in the IS window) that the harness does
        # not emulate: reported as documented differences. Required: same rows in order, OOS columns, the
        # published row and its returns.
        req = [c for c in ("oos_sharpe", "oos_n") if c in rep["columns"]]
        rep["documented_differences"] = {c: rep["columns"][c] for c in rep["columns"] if c not in req}
        rep["documented_differences"]["valid_flags_equal"] = rep.get("valid_flags_equal")
        rep["pass"] = bool(same_keys and rep["winner"]["match"] and rep["strategy_return"]["pass"]
                           and all(rep["columns"][c]["pass"] for c in req))
    else:
        rep["pass"] = bool(same_keys and rep["winner"]["match"] and rep["strategy_return"]["pass"]
                           and all(c["pass"] for c in rep["columns"].values()) and rep.get("valid_flags_equal", False))
    return rep


# ---------------------------------------------------------------------------------------------------- tracks
def build_tracks(mod) -> dict:
    """{'main': TrackInputs, 'comparison': TrackInputs | None} per the pair's track policy."""
    spec = mod.SPEC
    idx = mod.rebalance_index()
    ret = mod.target_return(idx)
    if spec.track_policy == "compute_twice":
        rev = revised_inputs(spec, mod.revised_levels(), idx, ret, name="revised")
        rt = realtime_inputs(spec, load_vintages(spec.vintage_series), idx, ret)
        return {"main": rt, "comparison": rev}
    name = "market" if spec.track_policy == "single_market" else "revised"
    return {"main": revised_inputs(spec, mod.revised_levels(), idx, ret, name=name), "comparison": None}


def null_maker(mod, which: str, ti):
    """(make_inputs(k), span length) for the track's null (see harness.null)."""
    spec = mod.SPEC
    if ti.name == "real_time":            # null v3: one constant roll of the real per-row inputs (harness.null)
        return (lambda k: NL.roll_track_inputs(ti, k)), NL.defined_span_min(ti.lagged)
    lv = mod.revised_levels()
    s, e = NL.data_span(lv)
    return (lambda k: revised_inputs(spec, NL.roll_span(lv, k, s, e), ti.index, ti.ret, name=ti.name)), e - s


def r71_diagnosis(spec, make, n_span: int, summ: dict, log=print, K: int = 30, max_offset=None) -> dict:
    """When the R7.1 check fails, describe where the bias lives: (a) the timing Sharpe averaged over ALL valid
    candidates of each draw (no selection) and (b) the selected winner's timing Sharpe when the target returns
    are also randomly permuted (no return path). These checks locate the bias but do not identify its cause: a
    lookahead in the null construction that only the selection step exploits looks the same (Codex B0r: the
    real-time null's cross-vintage fill did exactly that). The flag stays open with the cause unproven."""
    log(f"  R7.1 diagnosis: {K} draws with permuted returns")
    sh = NL.run_null(spec, make, n_span, K, shuffle_returns_seed=NL.SEED_BASE, max_offset=max_offset)
    st = sh["timing_sharpe"].dropna()
    se, _ = NL.dependent_se(st.to_numpy(), sh.loc[st.index, "offset"].to_numpy(), spec.ppy)
    a, b = summ["timing_sharpe_mean_all_valid_candidates"], round(float(st.mean()), 4)
    return {"timing_mean_selected_winner": summ["timing_sharpe_mean"], "timing_mean_all_valid_candidates": a,
            "timing_mean_selected_winner_returns_permuted": b, "returns_permuted_se": round(se, 4),
            "returns_permuted_draws": int(len(st)),
            "bias_only_in_selected_winners_on_real_returns": bool(abs(a) <= 0.05 and abs(b) <= max(0.10, 2 * se)),
            "cause": "unproven",
            "reading": (f"Selected winners average a timing Sharpe of {summ['timing_sharpe_mean']} in the null; all valid "
                        f"candidates average {a}; with the returns permuted the selected winners average {b} "
                        f"(SE {se:.3f}). "
                        + ("The bias appears only in the selected winners on the real return path, not in unselected "
                           "candidates or without the return path. "
                           if abs(a) <= 0.05 and abs(b) <= max(0.10, 2 * se) else
                           "The bias also appears without selection or without the return path. ")
                        + "Cause unproven; open flag. The leak tests are reported separately.")}


def leak_makers(mod, ti):
    spec = mod.SPEC
    if ti.name == "real_time":
        vint = load_vintages(spec.vintage_series)

        def trunc(c):
            idx = ti.index[ti.index <= c]
            return realtime_inputs(spec, LK.truncate_vintages(vint, c), idx, ti.ret[: len(idx)])

        def pert(c):
            return realtime_inputs(spec, LK.perturb_vintages(vint, c), ti.index, ti.ret)
        return trunc, pert
    lv = mod.revised_levels()

    def trunc(c):
        idx = ti.index[ti.index <= c]
        return revised_inputs(spec, lv.loc[:c], idx, ti.ret[: len(idx)], name=ti.name)

    def pert(c):
        return revised_inputs(spec, LK.perturb_levels(lv, c), ti.index, ti.ret, name=ti.name)
    return trunc, pert


# ---------------------------------------------------------------------------------------------------- run
def run_pair(pair_id: str, tag: str, K: int = 100, write: bool = True, leak: bool = True, extra: dict | None = None,
             log=print) -> dict:
    mod = load_pair(pair_id)
    spec = mod.SPEC
    extra = extra or {}
    out = {"pair_id": pair_id, "tag": tag}
    log(f"[{pair_id}] legacy replay")
    out["replay"] = replay_legacy(mod)
    if out["replay"].get("status") == "not_replayable":
        log(f"  replay: not replayable ({', '.join(out['replay']['missing_files']) or 'declared'}); "
            f"acceptance 4.1 via legacy reproduction pass={out['replay']['acceptance_4_1']['pass']}")
    else:
        log(f"  replay pass={out['replay']['pass']}  strategy_return max diff "
            f"{out['replay']['strategy_return']['max_abs_diff']:.2e}")
    tracks = build_tracks(mod)
    results: dict[str, TrackResult | None] = {}
    nulls: dict[str, pd.DataFrame | None] = {}
    records: dict[str, dict | None] = {}
    leaks: dict[str, dict | None] = {}
    for role, ti in tracks.items():
        if ti is None:
            results[role] = nulls[role] = records[role] = leaks[role] = None
            continue
        log(f"[{pair_id}] {role} track ({ti.name}): tournament")
        res = run_tournament(spec, ti)
        results[role] = res
        summ = None
        if res.selection is not None and K:
            log(f"  null tournament K={K}")
            make, n_span = null_maker(mod, role, ti)
            max_off = NL.max_usable_offset(spec, make, n_span) if ti.name == "real_time" else None
            if ti.name == "real_time":
                log(f"  usable admissible offsets up to {max_off}")
            nd = NL.run_null(spec, make, n_span, K, max_offset=max_off)
            nulls[role] = nd
            valid = res.table[res.table["valid"]]
            actual = {"is_max": float(valid["is_sharpe"].max()), "selection_stat": res.selection["score"],
                      "winner_oos": float(res.table.loc[res.selection["winner"], "oos_sharpe"])}
            summ = NL.summarize(nd, actual, len(spec.leads), spec.ppy)
            if not summ["r71_pass"]:
                summ["r71_diagnosis"] = r71_diagnosis(spec, make, n_span, summ, log, max_offset=max_off)
        else:
            nulls[role] = None
        records[role] = A.track_record(res, mod.SIGNAL_DISPLAY, summ)
        if res.selection is not None and leak:
            log("  leak tests")
            trunc, pert = leak_makers(mod, ti)
            leaks[role] = LK.run_leak_tests(spec, res.cands[int(res.selection["winner"])], ti, trunc, pert)
        else:
            leaks[role] = None
        if records[role].get("eligible"):
            w = records[role]["winner"]
            log(f"  winner {w['key']} IS {w['is_sharpe']:.3f} OOS {w['oos_sharpe']:.3f} "
                f"(B&H OOS {records[role]['bh_oos']['sharpe']:.3f}); plateau {records[role]['plateau']['leads']}")
        else:
            log("  MAIN not eligible")
    out.update(results=results, records=records, nulls=nulls, leaks=leaks)
    out["cross_eval"] = cross_eval(results, records)
    if write:
        write_outputs(mod, tag, out, extra)
    return out


def cross_eval(results: dict, records: dict) -> dict:
    m, c = results.get("main"), results.get("comparison")
    if c is None:
        return {"not_scorable_reason": "single track"}
    if records["main"] is None or not records["main"].get("eligible"):
        out = {"main_winner_on_revised": None}
    else:
        out = {"main_winner_on_revised": score_candidate(c, records["main"]["winner"]["key"])}
    out["revised_winner_on_main"] = (score_candidate(m, records["comparison"]["winner"]["key"])
                                     if records["comparison"] and records["comparison"].get("eligible") else None)
    return out


def _recessions(start: str | None, end: str | None) -> list[str]:
    if not start:
        return []
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return [lbl for a, b, lbl in NBER if pd.Timestamp(b) >= s and pd.Timestamp(a) <= e]


def track_state(spec, main_rec) -> str:
    if spec.track_policy == "single_market":
        return "single_market"
    if spec.track_policy == "single_revised_no_archive":
        return "single_no_archive"
    return "both" if main_rec and main_rec.get("eligible") else "rt_insufficient"


def winner_summary(mod, tag: str, out: dict, extra: dict) -> dict:
    """winner_summary.json 1.3.0: top-level fields describe MAIN (unchanged names), plus tracks / cross_eval."""
    spec = mod.SPEC
    recs = out["records"]
    main = recs["main"]
    comp = recs["comparison"]
    res = out["results"]["main"]
    ws = {"pair_id": spec.pair_id, "generated_at": A.now_iso(), "schema_version": A.SCHEMA_VERSION,
          "run_tag": tag,                 # the run's results tag, present whether or not MAIN has a winner
          "target_symbol": extra.get("target_symbol", "SPY"), "track_policy": spec.track_policy,
          "main_eligible": bool(main and main.get("eligible")),
          "cost_assumption_bps": extra.get("cost_bps", 5)}
    if ws["main_eligible"]:
        w = main["winner"]
        tab = res.table
        ws.update({
            "signal_column": w["signal_column"], "signal_code": w["signal"], "signal_display_name": w["signal_display"],
            "threshold_code": w["threshold"], "threshold_value": w["threshold_value"],
            "threshold_rule": w["threshold_rule"],
            "threshold_note": f"{w['threshold']} threshold; threshold_value is the value in force at the last row",
            **({"lookback": extra["lookback"]} if extra.get("lookback") else {}),
            "strategy_family": w["strategy_family"], "strategy_code": w["strategy"],
            "strategy_display_name": {"P1": "P1 long cash", "P2": "P2 signal strength", "P3": "P3 long short"}[w["strategy"]],
            "strategy_description": extra.get("strategy_description", ""),
            "lead_value": w["lead"], "lead_unit": spec.lead_unit,
            "lead_description": f"Signal is lagged {prose.unit_text(w['lead'], spec.lead_unit)} before allocation.",
            "direction": w["direction"],
            "oos_sharpe": w["oos_sharpe"], "oos_sortino": w["oos_sortino"], "oos_calmar": w["oos_calmar"],
            "oos_ann_return": w["oos_ann_return"], "oos_ann_vol": w["oos_ann_vol"],
            "oos_max_drawdown": w["oos_max_drawdown"], "oos_win_rate": w["oos_win_rate"],
            "oos_n_trades": w["oos_n_trades"], "annual_turnover": w["annual_turnover"], "oos_n": main["oos_n"],
            "oos_period_start": main["oos_window"][0], "oos_period_end": main["oos_window"][1],
            "bh_sharpe": main["bh_oos"]["sharpe"], "bh_ann_return": main["bh_oos"]["ann_return"],
            "bh_max_drawdown": main["bh_oos"]["max_drawdown"],
            "is_sharpe": w["is_sharpe"], "is_n": main["is_n"],
            "is_period_start": main["is_window"][0], "is_period_end": main["is_window"][1],
            "total_combos": main["n_candidates"], "valid_combos": main["n_valid"],
            "notes": extra.get("notes", ""),
            "selection": {
                "objective": main["objective"],
                "objective_formula": ("D9: min IS Sharpe over 3 adjacent grid leads (edge-clamped); best window = "
                                      "plateau; winner = highest raw IS Sharpe inside it. IS = deployable returns on "
                                      "[common_is_start, oos_start); OOS never consulted"),
                "is_window": {"start": main["is_window"][0], "end": main["is_window"][1], "n": main["is_n"],
                              "common_is_start": main["is_window"][0], "oos_start": spec.oos_start,
                              "min_is_n": spec.min_is_n, "n_candidates": main["n_candidates"],
                              "n_eligible": main["n_eligible"],
                              "rule": "R3.3 eligibility before alignment; common_is_start = latest first-valid return "
                                      "among eligible candidates", "bh_is_sharpe": main["bh_is"]["sharpe"]},
                "grid_scanned": {"leads": list(spec.leads), "n_signals": len(spec.signals),
                                 "n_thresholds": int(tab["threshold"].nunique()),
                                 "n_strategies": len(spec.strategies), "n_combos": main["n_candidates"],
                                 "n_valid_combos": max(main["n_valid"], 1),
                                 "n_distinct_position_series": main["n_distinct"],
                                 "median_valid_objective": float(tab.loc[tab["valid"], "is_sharpe"].median())},
                "tie_break_step": None,
                "raw_winner_row": {"signal": w["signal"], "threshold": w["threshold"], "strategy": w["strategy"],
                                   "lead_column": spec.lead_col, "lead_value": w["lead"],
                                   "source_tournament_file": f"tournament_results_{tag}.csv",
                                   "source_row_index": w["source_row_index"]},
                "runner_up": main["runner_up"],
                "window_leads": main["plateau"]["leads"], "J": main["plateau"]["score"],
                "raw_is_argmax": main["raw_argmax"],
                "rationale": "Winner selected on IS data only by the D9 lead-plateau rule; OOS reported for it only.",
                "inference": {"oos_sharpe_diff_vs_bh_bootstrap": main.get("vs_buy_hold"), "hac": main.get("hac")},
                "previously_published": [out["replay"]["published"]] if out["replay"].get("published") else [],
            },
        })
    else:
        # winner fields are omitted (schema 1.3.0 allOf): the headline must say "not eligible", never fall back
        ws["status"] = {"main_not_eligible": main["insufficient_reason"] if main else None,
                        "text": "Not enough real-time history for the training window."}
    ws["tracks"] = {"main": main, "comparison": comp}
    ws["cross_eval"] = out["cross_eval"]
    wf = prose.build(main) if main else {}
    if comp is not None:
        wf.update(prose.build(comp, prefix="comparison_"))
        wf.update(prose.cross_fields(out["cross_eval"]))
    wf["track_state"] = prose.field(track_state(spec, main), track_state(spec, main))
    if out["replay"].get("published"):
        wf.update(prose.previous_fields(out["replay"]["published"], spec.lead_unit))
    ws["winner_fields"] = wf
    return A.jsonable(ws)


def tournament_winner(ws: dict, tag: str) -> dict:
    """Canonical winner-vs-benchmark record (team-coordination.md 'Tournament Winner JSON Schema', META-TWJ) for
    the MAIN winner on its OOS dates; deltas = winner - buy-and-hold. The suggested objective follows the fleet
    rule: min_mdd when the relative drawdown improvement exceeds the relative Sharpe improvement, else
    max_sharpe."""
    d_sh = ws["oos_sharpe"] - ws["bh_sharpe"]
    d_ret = ws["oos_ann_return"] - ws["bh_ann_return"]
    d_dd = ws["oos_max_drawdown"] - ws["bh_max_drawdown"]
    rel_sharpe = d_sh / max(abs(ws["bh_sharpe"]), 0.1)
    rel_dd = d_dd / max(abs(ws["bh_max_drawdown"]), 0.01)
    return A.jsonable({
        "pair_id": ws["pair_id"], "generated_at": ws["generated_at"], "track": "main",
        "source_tournament_file": f"tournament_results_{tag}.csv",
        "winner": {"signal": ws["signal_code"], "threshold": ws["threshold_code"], "strategy": ws["strategy_family"],
                   "direction": ws["direction"], "lead_value": ws["lead_value"], "lead_unit": ws["lead_unit"],
                   "oos_sharpe": ws["oos_sharpe"], "oos_ann_return": ws["oos_ann_return"],
                   "max_drawdown": ws["oos_max_drawdown"], "annual_turnover": ws["annual_turnover"]},
        "benchmark": {"name": "Buy & Hold", "oos_sharpe": ws["bh_sharpe"], "oos_ann_return": ws["bh_ann_return"],
                      "max_drawdown": ws["bh_max_drawdown"]},
        "deltas": {"delta_sharpe": round(d_sh, 6), "delta_return": round(d_ret, 6), "delta_max_drawdown": round(d_dd, 6)},
        "beats_benchmark": bool(d_sh > 0),
        "suggested_strategy_objective": "min_mdd" if rel_dd > rel_sharpe else "max_sharpe",
    })


def track_summary(mod, out: dict, ws: dict) -> dict:
    spec = mod.SPEC
    main, comp = out["records"]["main"], out["records"]["comparison"]
    ce = out["cross_eval"]

    def block(rec, label):
        if rec is None:
            return None
        b = {"track": label, "eligible": bool(rec.get("eligible"))}
        if rec.get("eligible"):
            w = rec["winner"]
            b.update({"window": [rec["is_window"][0], rec["oos_window"][1]], "n_obs": rec["is_n"] + rec["oos_n"],
                      "winner": {"signal": w["signal"], "threshold": w["threshold"], "strategy": w["strategy"],
                                 "direction": w["direction"], "lead": w["lead"]},
                      "is_sharpe": w["is_sharpe"], "oos_sharpe": w["oos_sharpe"],
                      "recessions_covered": _recessions(rec["is_window"][0], rec["oos_window"][1])})
        return b

    mb = block(main, {"real_time": "real_time", "revised": "revised", "market": "market"}[main["track"]])
    cb = block(comp, "revised")
    if cb is not None and main.get("eligible") and comp.get("eligible"):
        cb["same_winner"] = main["winner"]["key"] == comp["winner"]["key"]
        cb["sharpe_gap"] = round(comp["winner"]["oos_sharpe"] - main["winner"]["oos_sharpe"], 6)
    plat = None
    if main.get("eligible"):
        res = out["results"]["main"]
        lc = A.lead_curve(res)
        cres = out["results"].get("comparison")
        rev_lc = A.lead_curve(cres) if cres is not None and cres.selection is not None else None
        scores = []
        for _, r in lc.iterrows():
            s = {"lead": int(r[spec.lead_col]), "score_rt" if comp is not None else "score": round(float(r["is_sharpe"]), 6)}
            scores.append(s)
        plat = {"leads": main["plateau"]["leads"], "winner_lead": main["plateau"]["winner_lead"],
                "global_max_lead": main["plateau"]["global_max_lead"],
                "global_max_inside_plateau": main["plateau"]["global_max_inside_plateau"], "scores": scores,
                "score": main["plateau"]["score"]}
        if rev_lc is not None:
            plat["revised_curve"] = [{"lead": int(r[spec.lead_col]), "score_rev": round(float(r["is_sharpe"]), 6)}
                                     for _, r in rev_lc.iterrows()]
    nt = None
    if main.get("null_tournament"):
        n = main["null_tournament"]
        nt = {"n_draws": n["n_draws"], "winner_percentile": n["selection_stat_percentile"],
              "p_selection_stat": n["p_selection_stat"], "is_max_percentile": n["is_max_percentile"],
              "winner_oos_percentile": n["winner_oos_percentile"], "null_scores_hist": n["null_scores_hist"],
              "method": n["method"], "r71_pass": n["r71_pass"], "edge_flag": n["edge_flag"],
              "n_admissible_offsets": n.get("n_admissible_offsets"),
              "n_draws_without_winner": n.get("n_draws_without_winner", 0)}
        if n.get("r71_diagnosis"):
            nt["r71_diagnosis"] = n["r71_diagnosis"]
        if comp and comp.get("null_tournament"):
            nt["revised_winner_percentile"] = comp["null_tournament"]["selection_stat_percentile"]
            nt["revised_r71_pass"] = comp["null_tournament"]["r71_pass"]
            if comp["null_tournament"].get("r71_diagnosis"):
                nt["revised_r71_diagnosis"] = comp["null_tournament"]["r71_diagnosis"]
    vb = None
    if main.get("vs_buy_hold"):
        v = main["vs_buy_hold"]
        vb = {k: v[k] for k in ("sharpe_diff", "ci_95", "p_diff_le_0", "block_length", "draws", "ann_return",
                                "ann_vol", "max_dd")}
    ts = {"pair_id": spec.pair_id, "schema_version": "1.0.0", "generated_at": ws["generated_at"],
          "track_state": track_state(spec, main), "track_policy": spec.track_policy, "main": mb, "comparison": cb,
          "cross_eval": ce, "insufficient_reason": None if main.get("eligible") else main.get("insufficient_reason"),
          "plateau": plat, "null_tournament": nt, "vs_buy_hold": vb, "status_badge_source": "main",
          "pair_version": None}
    return A.jsonable(ts)


def write_outputs(mod, tag: str, out: dict, extra: dict) -> None:
    from _tournament_io import write_tournament
    spec = mod.SPEC
    rdir = REPO / "results" / spec.pair_id
    rdir.mkdir(parents=True, exist_ok=True)
    for role in ("main", "comparison"):
        res = out["results"].get(role)
        if res is None:
            continue
        pre = A.TRACK_PREFIX[role]
        write_tournament(A.tournament_frame(res), rdir / f"{pre}tournament_results_{tag}.csv", allow_overwrite=True)
        A.lead_curve(res).to_csv(rdir / f"{pre}lead_curve_{tag}.csv", index=False)
        if out["nulls"].get(role) is not None:
            out["nulls"][role].to_csv(rdir / f"{pre}null_tournament_{tag}.csv", index=False)
        if res.selection is not None:
            ws_ = A.winner_series(res, res.selection["winner"])
            ws_.to_csv(rdir / f"{pre}strategy_returns_{tag}.csv", index=False)
            meta = {"pair_id": spec.pair_id, "track": res.name, "role": role,
                    "winner_key": res.table.loc[res.selection["winner"], "key"], "generated_at": A.now_iso(),
                    "vintage_policy": res.meta, "calendar_sha256": _sha(REPO / "data" / "release_calendar" / "release_calendar.csv"),
                    "vintage_file_sha256": _sha(REPO / "data" / "release_calendar" / "vintages" / f"{spec.vintage_series}.csv.gz")
                    if spec.vintage_series else None}
            (rdir / f"{pre}strategy_returns_{tag}_meta.json").write_text(json.dumps(A.jsonable(meta), indent=2) + "\n")
    A.write_json(rdir / f"candidates_manifest_{tag}.json", manifest_record(spec, manifest(spec)))
    ws = winner_summary(mod, tag, out, extra)
    A.write_json(rdir / "winner_summary.json", ws, "winner_summary")
    if ws.get("main_eligible"):
        A.write_json(rdir / "tournament_winner.json", tournament_winner(ws, tag), "tournament_winner")
    ts = track_summary(mod, out, ws)
    A.write_json(rdir / "track_summary.json", ts, "track_summary")
    if out["records"]["main"] and out["records"]["main"].get("eligible"):
        charts.lead_plateau(spec.pair_id, tag, spec.lead_unit)
        charts.chance_check(spec.pair_id, tag)
    A.write_json(rdir / f"leak_tests_{tag}.json", A.jsonable({"pair_id": spec.pair_id, "tag": tag,
                                                              "replay": out["replay"], "tracks": out["leaks"],
                                                              "null": {r: (out["records"][r] or {}).get("null_tournament")
                                                                       for r in ("main", "comparison")}}))


def _sha(p: Path) -> str | None:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pair_id")
    ap.add_argument("--tag", required=False)
    ap.add_argument("--K", type=int, default=100)
    ap.add_argument("--replay-only", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    if a.replay_only:
        rep = replay_legacy(load_pair(a.pair_id))
        print(json.dumps(rep, indent=2, default=str))
        if rep.get("status") == "not_replayable":
            return 0 if rep["acceptance_4_1"]["pass"] else 1
        return 0 if rep["pass"] else 1
    run_pair(a.pair_id, a.tag, a.K, write=not a.no_write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
