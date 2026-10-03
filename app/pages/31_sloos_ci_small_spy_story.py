"""Pair 31 — SLOOS C&I Tightening (Small Firms) × SPY Story (thin wrapper, Rule APP-PT1).

QUARTERLY credit-survey pair. Structural + presentational logic in
``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/sloos_ci_small_spy_config.py`` (honest found-in-search
framing — the winner's procyclical direction contradicts the countercyclical
credit prior; SLOOS has no forecasting lead).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.sloos_ci_small_spy_config import STORY_CONFIG

render_story_page("sloos_ci_small_spy", STORY_CONFIG)
