"""Structured winner fields: every number or fact that page prose may state about a result.

winner_summary.json carries `winner_fields: {name: {"value": raw, "text": display}}`. Pair configs render prose
from these (app/components/winner_fields.py) and never type a result by hand; scripts/gate_structured_prose.py
checks that every result statement in the prose matches a field.
"""
from __future__ import annotations

import math

LEAD_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
              10: "ten", 11: "eleven", 12: "twelve"}
TRACK_LABEL = {"real_time": "As known at the time", "revised": "As revised today (hindsight)",
               "market": "Market data (not revised)", "revised_single": "Revised values (no archive)"}
OBJECTIVE_TEXT = {
    "max_is_sharpe_lead_plateau_w3": "the highest in-sample Sharpe ratio on a plateau of three neighbouring leads",
    "max_is_sharpe": "the highest in-sample Sharpe ratio",
}
STRATEGY_TEXT = {"P1": "P1_long_cash", "P2": "P2_signal_strength", "P3": "P3_long_short"}


def unit_text(n: int, unit: str) -> str:
    u = {"months": "month", "quarters": "quarter", "days": "trading day"}[unit]
    return f"{n} {u}{'' if n == 1 else 's'}"


def _num(v, nd=2) -> str:
    return "n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.{nd}f}"


def _pct(v, nd=1) -> str:
    return "n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v * 100:.{nd}f}%"


def field(value, text: str) -> dict:
    return {"value": value, "text": text}


def previous_fields(pub: dict, lead_unit: str) -> dict:
    """The previously published rule (replayed through the harness, or declared by a not-replayable pair with its
    selection label), for correction banners."""
    lead = int(pub["lead"])
    sel = pub.get("selection") or "published (replayed through the harness)"
    return {"previous_rule": field(pub["key"], f"{pub['signal']} / {pub['threshold']} / L{lead}"),
            "previous_selection": field(sel, sel),
            "previous_lead": field(lead, str(lead)), "previous_lead_text": field(lead, unit_text(lead, lead_unit)),
            "previous_oos_sharpe": field(pub["oos_sharpe"], _num(pub["oos_sharpe"])),
            "previous_is_sharpe": field(pub["is_sharpe"], _num(pub["is_sharpe"])),
            "previous_tag": field(pub["tag"], f"{pub['tag'][:4]}-{pub['tag'][4:6]}-{pub['tag'][6:]}")}


def cross_fields(ce: dict) -> dict:
    """Cross-evaluation fields: each track's winner scored on the other track (like-for-like)."""
    out = {}
    for k, name in (("main_winner_on_revised", "ce_main_on_revised"), ("revised_winner_on_main", "ce_revised_on_main")):
        r = (ce or {}).get(k)
        if isinstance(r, dict):
            out[f"{name}_is_sharpe"] = field(r["is_sharpe"], _num(r["is_sharpe"]))
            out[f"{name}_oos_sharpe"] = field(r["oos_sharpe"], _num(r["oos_sharpe"]))
    return out


def build(rec: dict, prefix: str = "") -> dict:
    """Fields of one track record (artifacts.track_record). `prefix` namespaces the comparison track."""
    p = prefix
    if not rec.get("eligible"):
        return {f"{p}eligible": field(False, "not eligible"),
                f"{p}track_label": field(rec["track"], TRACK_LABEL[rec["track"]]),
                f"{p}insufficient_reason": field(rec.get("insufficient_reason"), str(rec.get("insufficient_reason")))}
    w = rec["winner"]
    lead, unit = int(w["lead"]), rec["lead_unit"]
    f = {
        "eligible": field(True, "eligible"),
        "track_label": field(rec["track"], TRACK_LABEL[rec["track"]]),
        "signal_code": field(w["signal"], w["signal"]),
        "signal_display": field(w["signal"], w["signal_display"]),
        "threshold_code": field(w["threshold"], w["threshold"]),
        "threshold_value": field(w["threshold_value"], _num(w["threshold_value"], 2)),
        "direction": field(w["direction"], w["direction"]),
        "strategy_family": field(STRATEGY_TEXT[w["strategy"]], STRATEGY_TEXT[w["strategy"]]),
        "lead": field(lead, str(lead)),
        "lead_text": field(lead, unit_text(lead, unit)),
        "lead_word": field(lead, LEAD_WORDS.get(lead, str(lead))),
        "is_sharpe": field(w["is_sharpe"], _num(w["is_sharpe"])),
        "oos_sharpe": field(w["oos_sharpe"], _num(w["oos_sharpe"])),
        "oos_ann_return": field(w["oos_ann_return"], _pct(w["oos_ann_return"])),
        "oos_sharpe_net_5bp": field(w.get("oos_sharpe_net_5bp"), _num(w.get("oos_sharpe_net_5bp"))),
        "oos_max_drawdown": field(w["oos_max_drawdown"], _pct(w["oos_max_drawdown"])),
        "oos_n_trades": field(w["oos_n_trades"], str(w["oos_n_trades"])),
        "bh_is_sharpe": field(rec["bh_is"]["sharpe"], _num(rec["bh_is"]["sharpe"])),
        "bh_oos_sharpe": field(rec["bh_oos"]["sharpe"], _num(rec["bh_oos"]["sharpe"])),
        "bh_oos_ann_return": field(rec["bh_oos"]["ann_return"], _pct(rec["bh_oos"]["ann_return"])),
        "bh_oos_max_drawdown": field(rec["bh_oos"]["max_drawdown"], _pct(rec["bh_oos"]["max_drawdown"])),
        "sharpe_gap": field(w["oos_sharpe"] - rec["bh_oos"]["sharpe"], _num(w["oos_sharpe"] - rec["bh_oos"]["sharpe"])),
        "is_start": field(rec["is_window"][0], rec["is_window"][0]),
        "is_end": field(rec["is_window"][1], rec["is_window"][1]),
        "oos_start": field(rec["oos_window"][0], rec["oos_window"][0]),
        "oos_end": field(rec["oos_window"][1], rec["oos_window"][1]),
        "is_n": field(rec["is_n"], str(rec["is_n"])),
        "oos_n": field(rec["oos_n"], str(rec["oos_n"])),
        "n_candidates": field(rec["n_candidates"], str(rec["n_candidates"])),
        "n_valid": field(rec["n_valid"], str(rec["n_valid"])),
        "n_distinct": field(rec["n_distinct"], str(rec["n_distinct"])),
        "selection_objective": field(rec["objective"], OBJECTIVE_TEXT[rec["objective"]]),
        "plateau_leads": field(rec["plateau"]["leads"], ", ".join(str(x) for x in rec["plateau"]["leads"])),
        "plateau_score": field(rec["plateau"]["score"], _num(rec["plateau"]["score"])),
        "plateau_range": field(rec["plateau"]["leads"], f"L{min(rec['plateau']['leads'])}-L{max(rec['plateau']['leads'])}"),
        "annual_turnover": field(w["annual_turnover"], _num(w["annual_turnover"])),
        "oos_exposure": field(w["oos_exposure"], _pct(w["oos_exposure"], 0)),
        "raw_argmax_lead": field(rec["raw_argmax"]["lead"], str(rec["raw_argmax"]["lead"])),
        "raw_argmax_is_sharpe": field(rec["raw_argmax"]["is_sharpe"], _num(rec["raw_argmax"]["is_sharpe"])),
        "raw_argmax_rule": field(rec["raw_argmax"]["key"], " / ".join(
            str(rec["raw_argmax"][k]) for k in ("signal", "threshold", "strategy"))),
        "raw_argmax_position": field(
            rec["raw_argmax"]["lead"] in rec["plateau"]["leads"],
            "inside the stable lead range" if rec["raw_argmax"]["lead"] in rec["plateau"]["leads"]
            else "outside the stable lead range"),
        "raw_argmax_is_winner": field(
            rec["raw_argmax"]["key"] == w.get("key"),
            "the same rule as the winner" if rec["raw_argmax"]["key"] == w.get("key")
            else "a different rule from the winner"),
    }
    vb = rec.get("vs_buy_hold")
    if vb:
        f["ci_low"] = field(vb["ci_95"][0], _num(vb["ci_95"][0]))
        f["ci_high"] = field(vb["ci_95"][1], _num(vb["ci_95"][1]))
        f["p_diff_le_0"] = field(vb["p_diff_le_0"], _num(vb["p_diff_le_0"]))
    ut = rec.get("undefined_tail")
    if ut:
        f["tail_n_periods"] = field(ut["n_periods"], str(ut["n_periods"]))
        f["tail_first_date"] = field(ut["first_date"], ut["first_date"])
        f["tail_last_date"] = field(ut["last_date"], ut["last_date"])
        f["tail_bh_return"] = field(ut["benchmark_return_over_tail"], _pct(ut["benchmark_return_over_tail"]))
        f["tail_hold_last_sharpe"] = field(ut["oos_sharpe_hold_last_position"],
                                           _num(ut["oos_sharpe_hold_last_position"]))
    nt = rec.get("null_tournament")
    if nt:
        f["null_percentile"] = field(nt.get("selection_stat_percentile"), _pct(nt.get("selection_stat_percentile"), 0))
        f["null_p_is"] = field(nt.get("p_is"), _num(nt.get("p_is")))
        f["null_draws"] = field(nt.get("n_draws"), str(nt.get("n_draws")))
    return {f"{p}{k}": v for k, v in f.items()}
