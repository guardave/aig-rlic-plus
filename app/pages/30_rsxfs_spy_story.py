"""Pair 30 -- RSXFS x SPY STORY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.rsxfs_spy_config import STORY_CONFIG

render_story_page("rsxfs_spy", STORY_CONFIG)
