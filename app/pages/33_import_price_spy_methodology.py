"""Pair 33 -- Import Price Index x SPY METHODOLOGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.import_price_spy_config import METHODOLOGY_CONFIG

render_methodology_page("import_price_spy", METHODOLOGY_CONFIG)
