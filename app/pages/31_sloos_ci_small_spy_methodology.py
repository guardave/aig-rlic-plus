"""Pair 31 — SLOOS C&I Tightening (Small Firms) × SPY Methodology (thin wrapper, Rule APP-PT1).

QUARTERLY credit-survey pair. Structural + presentational logic in
``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/sloos_ci_small_spy_config.py`` (honest found-in-search
framing — small 32-quarter OOS, no forecasting lead, no untouched hold-out).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.sloos_ci_small_spy_config import METHODOLOGY_CONFIG

render_methodology_page("sloos_ci_small_spy", METHODOLOGY_CONFIG)
