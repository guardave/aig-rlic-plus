"""Pair 15 — HY-IG × SPY Evidence (thin wrapper, Rule APP-PT1).

This page file is a thin wrapper: all structural and presentational logic
lives in ``app/components/page_templates.py`` and the pair-specific
content lives in ``app/pair_configs/hy_ig_spy_config.py``. See APP-PT1
in the AppDev SOP for the abstraction contract.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.hy_ig_spy_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("hy_ig_spy", EVIDENCE_METHOD_BLOCKS)
