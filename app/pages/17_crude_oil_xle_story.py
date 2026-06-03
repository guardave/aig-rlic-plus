"""crude_oil_xle Story (thin wrapper, Rule APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.crude_oil_xle_config import STORY_CONFIG

render_story_page("crude_oil_xle", STORY_CONFIG)
