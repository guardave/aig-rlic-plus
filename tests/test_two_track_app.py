"""Tests for the two-track display component (Phase B; design temp/_issues/twotrack_app_design.md)."""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "app"))
sys.path.insert(0, str(REPO / "scripts"))

from components import two_track as tt  # noqa: E402
from validate_schema import validate_json  # noqa: E402

BANNED = ("beats", "fails", "strong", "weak", "promising")
PILOTS = sorted(p.parent.name for p in (REPO / "results").glob("*/track_summary.json"))


def _vb(lo, hi, d, strat=(0.05, 0.10, -0.2), bh=(0.15, 0.15, -0.24)):
    return {"ci_95": [lo, hi], "sharpe_diff": d, "draws": 5000, "block_length": 6,
            "ann_return": {"strat": strat[0], "bh": bh[0]}, "ann_vol": {"strat": strat[1], "bh": bh[1]},
            "max_dd": {"strat": strat[2], "bh": bh[2]}}


def test_fact_templates_are_neutral_and_follow_the_interval():
    inside = tt._facts(_vb(-0.4, 0.3, -0.05), {"oos_sharpe": 0.9})
    outside = tt._facts(_vb(-0.9, -0.2, -0.5), {"oos_sharpe": 0.5})
    assert "cannot statistically distinguish" in inside[0]
    assert "excludes zero" in outside[0]
    assert any("below buy-and-hold" in s for s in outside)
    assert any("lower volatility" in s and "smaller worst drawdown" in s for s in outside)
    for s in inside + outside:
        assert not any(w in s.lower() for w in BANNED), s


def test_every_track_state_has_strip_copy():
    for state in ("both", "rt_insufficient", "single_market", "single_no_archive"):
        assert tt.STRIP[state][0].startswith("Data basis:")


def test_ordinal():
    assert [tt._ordinal(n) for n in (1, 2, 3, 11, 12, 13, 21, 94, 100)] == \
        ["1st", "2nd", "3rd", "11th", "12th", "13th", "21st", "94th", "100th"]


def test_component_has_no_pair_literals():
    src = (REPO / "app" / "components" / "two_track.py").read_text()
    for pid in [p.parent.name for p in (REPO / "results").glob("*/winner_summary.json")]:
        assert f'"{pid}"' not in src and f"'{pid}'" not in src


@pytest.mark.parametrize("pair", PILOTS)
def test_published_track_summary_validates_and_matches_winner_summary(pair):
    ts = json.loads((REPO / "results" / pair / "track_summary.json").read_text())
    ws = json.loads((REPO / "results" / pair / "winner_summary.json").read_text())
    schema = json.loads((REPO / "docs" / "schemas" / "track_summary.schema.json").read_text())
    assert validate_json(ts, schema) == []
    assert ts["status_badge_source"] == "main" and ts["track_policy"] == ws["track_policy"]
    main = ws["tracks"]["main"]
    if main["eligible"]:
        assert ts["main"]["oos_sharpe"] == main["winner"]["oos_sharpe"] == ws["oos_sharpe"]
        assert ts["plateau"]["winner_lead"] == ws["lead_value"]
