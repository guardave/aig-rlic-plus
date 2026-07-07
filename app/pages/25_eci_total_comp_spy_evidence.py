"""Pair 25 — Employment Cost Index (Total Compensation) × SPY Evidence (thin wrapper, Rule APP-PT1).

New pair, first QUARTERLY pair (feat260705_eci_spy). Structural +
presentational logic in ``app/components/page_templates.py``; pair-specific
content in ``app/pair_configs/eci_total_comp_spy_config.py`` (honest
placeholder prose pending Research Ray's finished pass — lagging /
reverse-causality framing is the headline).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.eci_total_comp_spy_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("eci_total_comp_spy", EVIDENCE_METHOD_BLOCKS)
