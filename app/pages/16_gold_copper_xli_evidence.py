"""Pair 16 — Gold/Copper × XLI Evidence (thin wrapper, Rule APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.gold_copper_xli_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("gold_copper_xli", EVIDENCE_METHOD_BLOCKS)
