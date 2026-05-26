"""Pair 16 — Gold/Copper × XLI Methodology (thin wrapper, Rule APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.gold_copper_xli_config import METHODOLOGY_CONFIG

render_methodology_page("gold_copper_xli", METHODOLOGY_CONFIG)
