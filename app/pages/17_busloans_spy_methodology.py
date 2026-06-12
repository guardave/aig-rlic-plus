"""Pair 17 — C&I Loans (BUSLOANS) × SPY Methodology (thin wrapper, Rule APP-PT1).

Pair #19, Mode 1 (fix260612_busloans_spy). Structural + presentational
logic in ``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/busloans_spy_config.py`` (prose by Research Ray).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.busloans_spy_config import METHODOLOGY_CONFIG

render_methodology_page("busloans_spy", METHODOLOGY_CONFIG)
