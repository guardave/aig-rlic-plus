"""Pair 16 — Gold/Copper × XLI Story (thin wrapper, Rule APP-PT1).

Mode 2 Phase 5 (LEAD-WM1 — Ace hat). Structural + presentational logic
in ``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/gold_copper_xli_config.py``.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.gold_copper_xli_config import STORY_CONFIG

render_story_page("gold_copper_xli", STORY_CONFIG)
