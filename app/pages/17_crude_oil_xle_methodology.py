"""crude_oil_xle Methodology (thin wrapper, Rule APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_methodology_page
from pair_configs.crude_oil_xle_config import METHODOLOGY_CONFIG

render_methodology_page("crude_oil_xle", METHODOLOGY_CONFIG)
