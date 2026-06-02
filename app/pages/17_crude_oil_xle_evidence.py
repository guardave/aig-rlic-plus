"""crude_oil_xle Evidence (thin wrapper, Rule APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_evidence_page
from pair_configs.crude_oil_xle_config import EVIDENCE_METHOD_BLOCKS

render_evidence_page("crude_oil_xle", EVIDENCE_METHOD_BLOCKS)
