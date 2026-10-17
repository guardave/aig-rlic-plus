"""Phase B schema changes are backward-compatible (winner_summary 1.3.0, track_summary 1.0.0, registry 1.4.0)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_schema import validate_json  # noqa: E402

WS = json.loads((ROOT / "docs/schemas/winner_summary.schema.json").read_text())
TS = json.loads((ROOT / "docs/schemas/track_summary.schema.json").read_text())
INELIGIBLE_MAIN = {"track": "real_time", "eligible": False, "lead_unit": "months", "n_candidates": 10, "n_valid": 0,
                   "insufficient_reason": {"rt_start": "2019-01-31", "n_is_rows": 47, "min_required": 60}}


@pytest.mark.parametrize("pair", sorted(p.parent.name for p in (ROOT / "results").glob("*/winner_summary.json")
                                        if not p.parent.name.endswith(("_archived", "_v1"))))
def test_existing_winner_summaries_still_validate(pair):
    ws = json.loads((ROOT / "results" / pair / "winner_summary.json").read_text())
    if ws.get("schema_version", "").startswith("1.3"):
        pytest.skip("Phase B file (covered by the producer)")
    assert validate_json(ws, WS) == []


def test_ineligible_main_omits_winner_fields_but_needs_status():
    stub = {"pair_id": "x", "generated_at": "2026-10-17T00:00:00+00:00", "main_eligible": False,
            "track_policy": "compute_twice", "status": {"text": "not enough real-time history"},
            "tracks": {"main": INELIGIBLE_MAIN, "comparison": None}}
    assert validate_json(stub, WS) == []
    bad = {k: v for k, v in stub.items() if k != "status"}
    assert any("status" in e for e in validate_json(bad, WS))


def test_eligible_main_still_requires_full_winner_record():
    ws = json.loads((ROOT / "results/unrate_spy/winner_summary.json").read_text())
    ws = dict(ws, main_eligible=True)
    ws.pop("signal_column")
    assert any("signal_column" in e for e in validate_json(ws, WS))


def test_plateau_objective_admitted_and_unknown_rejected():
    ws = json.loads((ROOT / "results/unrate_spy/winner_summary.json").read_text())
    ws["selection"] = dict(ws["selection"], objective="max_is_sharpe_lead_plateau_w3")
    assert validate_json(ws, WS) == []
    ws["selection"]["objective"] = "max_lucky_sharpe"
    assert validate_json(ws, WS)


def test_track_summary_rt_insufficient_shape():
    ts = {"pair_id": "x", "schema_version": "1.0.0", "track_state": "rt_insufficient", "track_policy": "compute_twice",
          "main": {"track": "real_time", "eligible": False},
          "comparison": {"track": "revised", "eligible": True, "window": ["1993-02-28", "2026-09-30"], "n_obs": 400,
                         "winner": {"signal": "s", "threshold": "t", "lead": 3}, "is_sharpe": 0.5, "oos_sharpe": 0.4},
          "cross_eval": {"main_winner_on_revised": None, "revised_winner_on_main": None},
          "insufficient_reason": {"rt_start": "2019-01-31", "n_is_rows": 47, "min_required": 60},
          "plateau": None, "null_tournament": None, "vs_buy_hold": None, "status_badge_source": "main",
          "pair_version": None}
    assert validate_json(ts, TS) == []
    assert validate_json(dict(ts, status_badge_source="comparison"), TS)
    assert validate_json(dict(ts, track_state="ranked"), TS)
