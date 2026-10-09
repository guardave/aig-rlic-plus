"""Pair 43 -- 10Y-3M Treasury Spread (rebuilt, floored) x SPY STRATEGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.t10y3m_rebuilt_spy_config import STRATEGY_CONFIG

render_strategy_page("t10y3m_rebuilt_spy", STRATEGY_CONFIG)
