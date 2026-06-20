"""Pair 21 -- 10Y-3M Treasury Spread x SPY METHODOLOGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.t10y3m_spy_config import METHODOLOGY_CONFIG

render_methodology_page("t10y3m_spy", METHODOLOGY_CONFIG)
