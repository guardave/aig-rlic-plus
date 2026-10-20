"""The deployed-signal panel marks the indicator's declared coverage changes (QA cement F5); the quartile palette
is sequential (QA cement F7)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "app")]


def test_coverage_change_is_marked_inside_the_plotted_span(monkeypatch):
    import streamlit as st
    from components import probability_engine_panel as PE
    figs = []
    monkeypatch.setattr(st, "plotly_chart", lambda fig, **k: figs.append(fig))
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(PE, "_load_target_price_overlay", lambda *a: None)
    idx = pd.date_range("2006-01-31", "2025-06-30", freq="ME")
    sig = pd.DataFrame({"signal": np.sin(np.arange(len(idx))), "threshold": 0.0}, index=idx)
    win = {"target_symbol": "SPY", "lead_value": 8, "lead_unit": "months", "threshold_rule": "gte",
           "track_policy": "single_revised_no_archive", "signal_code": "chg_6m", "oos_period_start": "2017-01-31"}
    PE._render_deployed_signal("toy_spy", win, sig, False, [{"date": "2024-01-31", "label": "Coverage change"},
                                                           {"date": "1990-01-31", "label": "outside"}])
    fig = figs[0]
    lines = [s for s in fig.layout.shapes if s.type == "line"]
    assert [s.x0 for s in lines] == ["2024-01-31"]
    assert [a.text for a in fig.layout.annotations if a.text in ("Coverage change", "outside")] == ["Coverage change"]
    figs.clear()
    PE._render_deployed_signal("toy_spy", win, sig, False)                 # no declaration: no marker
    assert not [s for s in figs[0].layout.shapes if s.type == "line"]


def test_quartile_palette_is_sequential():
    from _quartile_chart import QUARTILE_COLORS
    lum = [0.2126 * int(c[1:3], 16) + 0.7152 * int(c[3:5], 16) + 0.0722 * int(c[5:7], 16) for c in QUARTILE_COLORS]
    assert lum == sorted(lum, reverse=True)                     # light Q1 .. dark Q4, one hue
