"""Pair 8 — VIX/VIX3M × SPY Methodology (thin wrapper, Rule APP-PT1).

This page file is a thin wrapper: all structural and presentational logic
lives in ``app/components/page_templates.py`` and the pair-specific
content lives in ``app/pair_configs/vix_vix3m_spy_config.py``. See APP-PT1
in the AppDev SOP for the abstraction contract.
"""

import os
import sys

# sys.path shim so `components` / `pair_configs` resolve from a sibling dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.vix_vix3m_spy_config import METHODOLOGY_CONFIG

render_methodology_page("vix_vix3m_spy", METHODOLOGY_CONFIG)
