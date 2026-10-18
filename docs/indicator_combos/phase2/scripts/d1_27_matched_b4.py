"""D1-27 add-on (EXPLORATORY): every model and baseline scored on the SAME rows where the SPY trend flag (B4) exists.

The main run scores B4 on its own sub-window (SPY starts 1993), so its Brier score is not directly comparable with the
H2 models scored from 1988. This add-on recomputes the identical real-time predictions (same functions, same
settings, no null draws) and scores all of them on the rows where B4 exists, for the full window only (the primary
result; no post-hoc sensitivity here). Output: phase2/d1_27/matched_b4.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d1_27_recession_probit as m  # noqa: E402
import p2data as d  # noqa: E402


def main():
    idx = d.month_index("1982-01-31")
    panel = pd.concat([d.t10y3m(idx), d.hy_ig(idx), d.sahm_gap(idx), d.permit_yoy(idx), d.spy_sma_flag(idx)], axis=1)
    y = m.labels(idx)
    out = {"status": "Exploratory", "question": "D1-27", "note": "all predictions scored on rows where B4 exists"}
    for h, cols in m.MODELS.items():
        start = m.EVAL_START[h]
        need = panel[cols].notna().all(axis=1)
        sub = panel.where(need)
        preds = {"model": m.realtime_predictions(sub, y, cols, start),
                 "term_only_same_rows": m.realtime_predictions(sub, y, ["term"], start),
                 "term_only_full_history": m.realtime_predictions(panel, y, ["term"], start),
                 "B1_base_rate": m.base_rate(sub, y, start),
                 "B2a_best_single": m.best_single(sub, y, cols, start)[0],
                 "B3_naive_composite": m.realtime_predictions(sub, y, cols, start, kind="composite"),
                 "B4_sma_flag": m.realtime_predictions(panel.where(need & panel["sma_flag"].notna()), y,
                                                       ["sma_flag"], start)}
        df = pd.DataFrame(preds)
        w = df.index[(df.index >= pd.Timestamp(start)) & (df.index <= m.LAST_LABELLED)]
        rows = w[df.loc[w].notna().all(axis=1).to_numpy()]
        sc = {k: m.scores(df.loc[rows, k], y.loc[rows]) for k in df}
        best = min(sc, key=lambda k: sc[k]["brier"])
        out[h] = {"rows": f"{rows[0].date()}..{rows[-1].date()}", "months": len(rows),
                  "recessions_covered": [str(pk.date())[:7] for pk, tr in d.recession_episodes()
                                         if any((rows >= pk - pd.offsets.MonthEnd(m.H - 1)) & (rows < tr))],
                  "brier": {k: v["brier"] for k, v in sc.items()},
                  "lowest_brier": best,
                  "B4_rank_of_7": sorted(sc, key=lambda k: sc[k]["brier"]).index("B4_sma_flag") + 1}
        print(h, json.dumps(out[h]), flush=True)
    (d.P2 / "d1_27" / "matched_b4.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
