"""crude_oil_xle Strategy (thin wrapper, Rule APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.crude_oil_xle_config import STRATEGY_CONFIG

render_strategy_page("crude_oil_xle", STRATEGY_CONFIG)
