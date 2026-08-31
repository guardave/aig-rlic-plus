"""Pair 35 -- ISM Manufacturing PMI x SPY EVIDENCE (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.ism_mfg_spy_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("ism_mfg_spy", EVIDENCE_METHOD_BLOCKS)
