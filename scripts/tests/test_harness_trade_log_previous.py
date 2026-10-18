"""Harness artifacts after QA B1 umcsent_xlv: trade-log columns (M2) and previous_* = published values (L1)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.artifacts import trade_log  # noqa: E402
from harness.run import published_value  # noqa: E402


def _ws(pos):
    d = pd.date_range("1998-12-31", periods=len(pos), freq="ME")
    return pd.DataFrame({"date": d, "position": pos, "signal": range(len(pos)), "threshold": 0.0})


def test_quantity_is_weight_after_and_trade_size_is_separate():
    # QA repro (umcsent P2): 1999-01-31 SELL 12.655 with position_after 0.0; 1999-03-31 SELL 13.159, after 0.124
    log = trade_log(_ws([0.12655, 0.0, 0.25559, 0.124]), "XLV", 5, "r")
    sells = log[log["side"] == "SELL"]
    assert list(sells["quantity_pct"].round(3)) == [0.0, 12.4]                 # the weight after the trade
    assert list(sells["trade_size_pct"].round(3)) == [12.655, 13.159]         # the size of the trade
    assert (log["quantity_pct"] == log["position_after"] * 100).all()


def test_position_held_from_the_first_row_is_an_entry():
    # QA: the initial entry at 1998-12-31 (position 0.1266) was not logged (pos.diff().fillna(0))
    log = trade_log(_ws([0.1266, 0.1266, 0.0]), "XLV", 5, "r")
    first = log.iloc[0]
    assert first["trade_date"] == "1998-12-31" and first["side"] == "BUY"
    assert round(first["trade_size_pct"], 2) == 12.66 and first["position_before"] == 0.0


def test_previous_values_are_the_published_record_not_the_replay():
    # QA L1: replay IS 0.3107 (harness, common start) vs published 0.2825 (immutable record)
    rec = pd.Series({"is_sharpe": 0.2825, "oos_sharpe": 0.5})
    pub = pd.DataFrame({"is_sharpe": [0.29], "oos_sharpe": [0.5]})
    wrow = pd.Series({"is_sharpe": 0.3107, "oos_sharpe": 0.5})
    assert published_value(rec, pub, 0, wrow, "is_sharpe") == 0.2825
    assert published_value(pd.Series({"oos_sharpe": 0.5}), pub, 0, wrow, "is_sharpe") == 0.29   # table row next
    assert published_value(None, pub.drop(columns="is_sharpe"), 0, wrow, "is_sharpe") == 0.3107
