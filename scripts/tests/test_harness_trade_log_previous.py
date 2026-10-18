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


def test_undefined_tail_is_reported_with_a_hold_last_sensitivity():
    # QA pilot-visual H1: unrate's last 6 test months had no published reading; the rule held cash (pre-registered)
    import numpy as np
    from harness.artifacts import undefined_tail
    n = 24
    d = pd.date_range("2024-01-31", periods=n, freq="ME")
    pos = [1.0] * 18 + [np.nan] * 6
    br = np.full(n, 0.01)
    sr = np.where(np.isnan(pos), 0.0, br)
    ws = pd.DataFrame({"date": d, "position": pos, "strategy_return": sr, "benchmark_return": br})
    ut = undefined_tail(ws, np.ones(n, bool), 12, 1.0)
    assert ut["n_periods"] == 6 and ut["first_date"] == "2025-07-31" and ut["last_defined_position"] == 1.0
    assert round(ut["benchmark_return_over_tail"], 6) == round(1.01 ** 6 - 1, 6)
    assert undefined_tail(ws.assign(position=1.0), np.ones(n, bool), 12, 1.0) is None


def test_undefined_tail_counts_returns_from_undefined_positions_under_a_one_period_shift():
    # permit_spy B1: with position_shift = 1 the last row's position earns no return in the sample; a NaN only on
    # the last row is not a cash period
    import numpy as np
    from harness.artifacts import undefined_tail
    n = 24
    d = pd.date_range("2024-01-31", periods=n, freq="ME")
    br = np.full(n, 0.01)
    pos = np.array([0.205] * (n - 1) + [np.nan])
    sr = np.r_[0.0, pos[:-1] * br[1:]]                       # row t earns position t-1
    ws = pd.DataFrame({"date": d, "position": pos, "strategy_return": sr, "benchmark_return": br})
    assert undefined_tail(ws, np.ones(n, bool), 12, 1.0, position_shift=1) is None
    assert undefined_tail(ws, np.ones(n, bool), 12, 1.0, position_shift=0)["n_periods"] == 1
    # three undefined positions -> the last two returns came from undefined positions
    pos3 = np.array([0.5] * (n - 3) + [np.nan] * 3)
    ut = undefined_tail(ws.assign(position=pos3), np.ones(n, bool), 12, 1.0, position_shift=1)
    assert ut["n_periods"] == 2 and ut["first_date"] == "2025-11-30" and ut["last_defined_position"] == 0.5


def test_move_to_cash_on_an_undefined_signal_says_why():
    import numpy as np
    log = trade_log(pd.DataFrame({"date": pd.date_range("2026-01-31", periods=4, freq="ME"),
                                  "position": [1.0, 1.0, np.nan, np.nan], "signal": [0.2, 0.2, np.nan, np.nan],
                                  "threshold": 0.3}), "SPY", 5, "rule crossed")
    last = log.iloc[-1]
    assert last["side"] == "SELL" and "signal undefined" in last["reason"]


def test_position_chart_keeps_undefined_months_as_cash(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
    from components.position_adjustment_panel import _deployed_positions
    import numpy as np
    pd.DataFrame({"date": pd.date_range("2026-01-31", periods=5, freq="ME"),
                  "position": [np.nan, 1.0, 1.0, np.nan, np.nan]}).to_csv(tmp_path / "strategy_returns_20261017.csv",
                                                                         index=False)
    pos, _f = _deployed_positions(tmp_path, {})
    assert list(pos) == [100.0, 100.0, 0.0, 0.0]          # warm-up dropped, undefined tail shown at 0%
