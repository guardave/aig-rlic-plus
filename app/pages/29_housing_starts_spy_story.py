"""Pair 29 -- Housing Starts (SAAR) x SPY STORY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.housing_starts_spy_config import STORY_CONFIG

render_story_page("housing_starts_spy", STORY_CONFIG)
