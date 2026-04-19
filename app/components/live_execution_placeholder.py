"""Real-time Execution Placeholder — APP-SE4 standard component.

Addresses stakeholder item S18-10. Rule APP-SE4 (AppDev SOP §3.10):
every Strategy page MUST include a "Future: Live Execution" section so
stakeholders see the placeholder for where real-time values will render
once the execution layer is wired.

Behaviour:
    - Section title: "Future: Live Execution"
    - Three ``st.metric()`` cards:
        * Current Signal State
        * Target Position
        * Current Action
    - Reads ``results/{pair_id}/live_execution_stub.json`` if present.
      If absent, each metric displays "—" plus a short note.
    - ``st.info()`` callout explaining the historical-dashboard scope.

Contract:
    render_live_execution_placeholder(pair_id: str) -> None
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]


def render_live_execution_placeholder(pair_id: str) -> None:
    """Render the Future: Live Execution section for a pair (APP-SE4)."""
    st.markdown("## Future: Live Execution")

    stub_path = _REPO_ROOT / "results" / pair_id / "live_execution_stub.json"
    stub: dict = {}
    if stub_path.exists():
        try:
            with open(stub_path) as fh:
                stub = json.load(fh)
        except Exception as exc:  # pragma: no cover - defensive
            st.caption(f"Could not read live_execution_stub.json: {exc}")
            stub = {}

    current_signal = stub.get("current_signal_state", "—")
    target_position = stub.get("target_position", "—")
    current_action = stub.get("current_action", "—")
    as_of = stub.get("as_of")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Signal State", current_signal)
    with col2:
        st.metric("Target Position", target_position)
    with col3:
        st.metric("Current Action", current_action)

    if as_of:
        st.caption(f"Stub last updated: {as_of}")
    else:
        st.caption(
            "No `live_execution_stub.json` present yet — values render as "
            "`—` placeholders until a real-time feed is wired."
        )

    st.info(
        "This dashboard presents historical backtest results. A real-time "
        "execution layer would surface the fields above; the values shown "
        "are placeholders. Wiring to a live data feed and broker API is a "
        "deliberate out-of-scope for this research portal (see Methodology)."
    )
