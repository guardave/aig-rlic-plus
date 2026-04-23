"""Pair 10 — UMCSENT × XLV Strategy (thin wrapper, Rule APP-PT1).

This page file is a thin wrapper: all structural and presentational logic
lives in ``app/components/page_templates.py`` and the pair-specific
content lives in ``app/pair_configs/umcsent_xlv_config.py``. See APP-PT1
in the AppDev SOP for the abstraction contract.
"""

import os
import sys

# sys.path shim so `components` / `pair_configs` resolve from a sibling dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.umcsent_xlv_config import STRATEGY_CONFIG

render_strategy_page("umcsent_xlv", STRATEGY_CONFIG)
