"""Pair 20 -- M2 Money Supply (YoY) x SPY STORY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.m2sl_yoy_spy_config import STORY_CONFIG

render_story_page("m2sl_yoy_spy", STORY_CONFIG)
