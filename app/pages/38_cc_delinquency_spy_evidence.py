"""Pair 38 — Credit-Card Delinquency Rate × SPY Evidence (thin wrapper, Rule APP-PT1).

QUARTERLY credit pair. Structural + presentational logic in
``app/components/page_templates.py``; pair-specific content in
``app/pair_configs/cc_delinquency_spy_config.py`` (honest found-in-search
framing — the winner's procyclical direction contradicts the countercyclical
credit prior; credit-card delinquency has no forecasting lead).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.cc_delinquency_spy_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("cc_delinquency_spy", EVIDENCE_METHOD_BLOCKS)
