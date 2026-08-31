"""Pair 37 -- Retail Inventories-to-Sales Ratio x SPY STORY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.retail_inv_sales_spy_config import STORY_CONFIG

render_story_page("retail_inv_sales_spy", STORY_CONFIG)
