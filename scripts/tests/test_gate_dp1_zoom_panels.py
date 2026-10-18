"""GATE-DP1 v2 (history zoom layout) and the shared zoom_dual_panel converter."""
import json
import sys
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cloud_verify as cv  # noqa: E402
from harness.charts import zoom_dual_panel  # noqa: E402

X = ["2008-01-31", "2008-02-29", "2008-03-31"]


def _overlay() -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=X, y=[5.0, 5.1, 5.3], name="UNRATE"), secondary_y=False)
    fig.add_trace(go.Scatter(x=X, y=[140.0, 133.0, 131.0], name="SPY"), secondary_y=True)
    fig.add_shape(type="rect", xref="x", yref="paper", x0=X[0], x1=X[2], y0=0, y1=1)
    fig.add_hline(y=135, secondary_y=True)
    fig.add_trace(go.Scatter(x=[None], y=[None], name="NBER recession period", mode="markers"))
    return fig


def _gate(tmp_path, fig_dict, pair="toy_spy"):
    d = tmp_path / "output" / "charts" / pair / "plotly"
    d.mkdir(parents=True, exist_ok=True)
    (d / "history_zoom_gfc.json").write_text(json.dumps(fig_dict, default=str))
    (d / "history_zoom_gfc_meta.json").write_text("{}")
    return cv.gate_dp1_dual_panel_preflight([pair], project_root=str(tmp_path))


def test_secondary_y_overlay_fails_viz_v1(tmp_path):
    f = _gate(tmp_path, json.loads(_overlay().to_json()))
    assert f and all(x["gate"] == "GATE-DP1" for x in f)
    assert any("overlays" in x["finding"] for x in f)


def test_original_blank_bottom_panel_bug_fails(tmp_path):
    # dual panel, but the target trace draws against the top x-axis (the Wave 10K bug)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Scatter(x=X, y=[1, 2, 3], name="ind"), row=1, col=1)
    fig.add_trace(go.Scatter(x=X, y=[3, 2, 1], name="SPY"), row=2, col=1)
    d = json.loads(fig.to_json())
    d["data"][1]["xaxis"] = "x"
    f = _gate(tmp_path, d)
    assert [x["trace_name"] for x in f] == ["SPY"] and f[0]["xaxis_expected"] == "x2"


def test_trace_on_wrong_x_for_its_overlay_base_fails(tmp_path):
    # the gold_copper_xli case v1 passed: y2 overlays the top panel's y but the trace sits on the bottom x2
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Scatter(x=X, y=[1, 2, 3], name="G/C"), row=1, col=1)
    fig.add_trace(go.Scatter(x=X, y=[0, 1, 0], name="z"), row=2, col=1)
    d = json.loads(fig.to_json())
    d["layout"]["yaxis3"] = {"overlaying": "y", "side": "right", "anchor": "x"}
    d["data"].append({"type": "scatter", "x": X, "y": [9, 8, 7], "name": "XLI", "xaxis": "x2", "yaxis": "y3"})
    f = _gate(tmp_path, d)
    assert any(x["trace_name"] == "XLI" and x["xaxis_expected"] == "x" for x in f)
    assert any("overlays" in x["finding"] for x in f)


def test_converter_produces_stacked_panels_that_pass(tmp_path):
    src = _overlay()
    out = zoom_dual_panel(src)
    assert isinstance(out, go.Figure) and zoom_dual_panel(out) is out           # idempotent
    d = json.loads(out.to_json())
    assert _gate(tmp_path, d) == []
    L = d["layout"]
    assert L["yaxis"]["domain"][0] > L["yaxis2"]["domain"][1]                    # indicator above target
    assert L["xaxis2"]["matches"] == "x" and L["xaxis"]["showticklabels"] is False
    assert [t["y"] for t in d["data"]] == [t["y"] for t in json.loads(src.to_json())["data"]]
    bands = [s for s in L["shapes"] if s["type"] == "rect"]
    assert {(s["xref"], s["y0"], s["y1"]) for s in bands} == {
        ("x", L["yaxis"]["domain"][0], L["yaxis"]["domain"][1]),
        ("x2", L["yaxis2"]["domain"][0], L["yaxis2"]["domain"][1])}            # one band per panel
    hl = [s for s in L["shapes"] if s["type"] == "line"]
    assert hl and hl[0]["yref"] == "y2" and hl[0]["xref"].startswith("x2")       # target-panel line moved


def test_converter_accepts_numpy_and_datetime_figures(tmp_path):
    # generators pass live Figures built from pandas (DatetimeIndex x, numpy y), not JSON round-trips
    import numpy as np
    import pandas as pd
    idx = pd.date_range("2008-01-31", periods=3, freq="ME")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=idx, y=np.array([5.0, 5.1, 5.3]), name="UNRATE"), secondary_y=False)
    fig.add_trace(go.Scatter(x=idx, y=np.array([140.0, 133.0, 131.0]), name="SPY"), secondary_y=True)
    out = zoom_dual_panel(fig)
    assert json.loads(out.to_json())["data"][1]["y"] == json.loads(fig.to_json())["data"][1]["y"]   # typed array kept
    assert out.data[1].xaxis == "x2"
    assert _gate(tmp_path, json.loads(out.to_json())) == []


def test_committed_fleet_zooms_pass():
    root = Path(__file__).resolve().parents[2]
    pairs = sorted(p.name for p in (root / "output" / "charts").iterdir() if p.is_dir())
    assert cv.gate_dp1_dual_panel_preflight(pairs, project_root=str(root)) == []
