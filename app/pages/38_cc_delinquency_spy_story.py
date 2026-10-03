"""Pair 38 — Credit-Card Delinquency Rate × SPY Story (thin wrapper, Rule APP-PT1).

QUARTERLY credit pair. Structural + presentational logic in
``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/cc_delinquency_spy_config.py`` (honest found-in-search
framing — the winner's procyclical direction contradicts the countercyclical
credit prior; credit-card delinquency has no forecasting lead).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.cc_delinquency_spy_config import STORY_CONFIG

render_story_page("cc_delinquency_spy", STORY_CONFIG)
