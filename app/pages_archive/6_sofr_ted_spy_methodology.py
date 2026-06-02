"""Pair 6 — SOFR-TED × SPY Methodology (thin wrapper, Rule APP-PT1).

This page file is a thin wrapper: all structural and presentational logic
lives in ``app/components/page_templates.py`` and the pair-specific
content lives in ``app/pair_configs/sofr_ted_spy_config.py``. See APP-PT1
in the AppDev SOP for the abstraction contract.

Wave 10I.A Part 2: created as part of the TED composite explode
(sofr_ted_spy / dff_ted_spy / ted_spliced_spy split from the old
3-in-1 `6_ted_variants_*.py` composite).
"""

import os
import sys

# sys.path shim so `components` / `pair_configs` resolve from a sibling dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.sofr_ted_spy_config import METHODOLOGY_CONFIG

render_methodology_page("sofr_ted_spy", METHODOLOGY_CONFIG)
