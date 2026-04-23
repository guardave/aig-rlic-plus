"""Pair 7 — PERMIT × SPY Strategy (thin wrapper, Rule APP-PT1).

This page file is a thin wrapper: all structural and presentational logic
lives in ``app/components/page_templates.py`` and the pair-specific
content lives in ``app/pair_configs/permit_spy_config.py``. See APP-PT1
in the AppDev SOP for the abstraction contract.
"""

import os
import sys

# sys.path shim so `components` / `pair_configs` resolve from a sibling dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.permit_spy_config import STRATEGY_CONFIG

render_strategy_page("permit_spy", STRATEGY_CONFIG)
