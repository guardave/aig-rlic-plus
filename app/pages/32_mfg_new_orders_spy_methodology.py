"""Pair 32 -- Manufacturers' New Orders x SPY METHODOLOGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.mfg_new_orders_spy_config import METHODOLOGY_CONFIG

render_methodology_page("mfg_new_orders_spy", METHODOLOGY_CONFIG)
