"""Pair 18 -- Petroleum Inventories x SPY Methodology (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.petrol_inv_spy_config import METHODOLOGY_CONFIG

render_methodology_page("petrol_inv_spy", METHODOLOGY_CONFIG)
