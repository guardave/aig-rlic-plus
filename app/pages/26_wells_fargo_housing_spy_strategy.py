"""Pair 26 — NAHB/Wells Fargo Housing Market Index (HMI) × SPY Strategy (thin wrapper, Rule APP-PT1).

New pair, MONTHLY (feat260706_wells_fargo_housing_spy). Structural +
presentational logic in ``app/components/page_templates.py``; pair-specific
content in ``app/pair_configs/wells_fargo_housing_spy_config.py`` (honest
placeholder prose pending Research Ray's finished pass — lagging /
reverse-dominant framing is the headline; the drawdown is the virtue).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.wells_fargo_housing_spy_config import STRATEGY_CONFIG

render_strategy_page("wells_fargo_housing_spy", STRATEGY_CONFIG)
