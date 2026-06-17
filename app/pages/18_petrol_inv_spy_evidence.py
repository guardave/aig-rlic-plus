"""Pair 18 -- Petroleum Inventories x SPY Evidence (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.petrol_inv_spy_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("petrol_inv_spy", EVIDENCE_METHOD_BLOCKS)
