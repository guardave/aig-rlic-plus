"""Pair 18 -- Petroleum Inventories x SPY Strategy (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.petrol_inv_spy_config import STRATEGY_CONFIG

render_strategy_page("petrol_inv_spy", STRATEGY_CONFIG)
