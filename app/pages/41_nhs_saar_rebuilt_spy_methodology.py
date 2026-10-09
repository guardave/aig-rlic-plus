"""Pair 41 -- New Home Sales (SAAR, rebuilt, floored) x SPY METHODOLOGY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.nhs_saar_rebuilt_spy_config import METHODOLOGY_CONFIG

render_methodology_page("nhs_saar_rebuilt_spy", METHODOLOGY_CONFIG)
