"""Pair 27 -- UNRATE x SPY STRATEGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.unrate_spy_config import STRATEGY_CONFIG

render_strategy_page("unrate_spy", STRATEGY_CONFIG)
