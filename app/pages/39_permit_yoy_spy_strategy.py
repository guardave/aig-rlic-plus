"""Pair 39 -- Building Permits YoY x SPY STRATEGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.permit_yoy_spy_config import STRATEGY_CONFIG

render_strategy_page("permit_yoy_spy", STRATEGY_CONFIG)
