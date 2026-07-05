"""Pair 24 — Cass Freight Index (Shipments) × SPY Evidence (thin wrapper, Rule APP-PT1).

New pair, Mode 1 (feat260705_cass_freight_spy). Structural + presentational
logic in ``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/cass_freight_spy_config.py`` (honest placeholder prose
pending Research Ray's finished pass).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.cass_freight_spy_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("cass_freight_spy", EVIDENCE_METHOD_BLOCKS)
