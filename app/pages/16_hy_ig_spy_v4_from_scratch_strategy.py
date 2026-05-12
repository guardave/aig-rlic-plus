"""Pair 16 — HY-IG × SPY v4 (from scratch) Strategy (thin wrapper, Rule APP-PT1).

This page file is a thin wrapper: all structural and presentational logic
lives in ``app/components/page_templates.py`` and the pair-specific
content lives in ``app/pair_configs/hy_ig_spy_v4_from_scratch_config.py``.
See APP-PT1 in the AppDev SOP for the abstraction contract.

Evidence status: failed_final_exam (holdout Sharpe 0.31 < 0.50 floor).
APP-SEV1 L2 disclosure banner rendered automatically via render_evidence_status_note()
called inside render_strategy_page(). Do NOT suppress or omit.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_strategy_page
from pair_configs.hy_ig_spy_v4_from_scratch_config import STRATEGY_CONFIG

render_strategy_page("hy_ig_spy_v4_from_scratch", STRATEGY_CONFIG)
