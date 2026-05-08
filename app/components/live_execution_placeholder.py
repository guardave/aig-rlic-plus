"""Live execution snapshot renderer.

Strategy pages are historical backtest pages unless a real snapshot artifact
exists. Missing snapshots render nothing: delivered pages must not show
future/live placeholder panels.

Contract:
    render_live_execution_placeholder(pair_id: str) -> bool
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]


def render_live_execution_placeholder(pair_id: str) -> bool:
    """Render a live/current snapshot only when the artifact is present.

    Returns True when a snapshot section was rendered, False when the section
    was intentionally omitted. Legacy ``live_execution_stub.json`` files are
    development-only and are never surfaced to stakeholders.
    """
    snapshot_path = _REPO_ROOT / "results" / pair_id / "live_execution_snapshot.json"
    if not snapshot_path.exists():
        return False

    try:
        with open(snapshot_path) as fh:
            snapshot = json.load(fh)
    except Exception as exc:  # pragma: no cover - defensive
        st.warning(
            "Current snapshot is unavailable because the snapshot artifact "
            f"could not be read: {exc.__class__.__name__}."
        )
        return False

    required = ["as_of_date", "current_signal", "target_position", "action"]
    missing = [field for field in required if snapshot.get(field) in (None, "")]
    if missing:
        st.warning(
            "Current snapshot is unavailable because required fields are "
            f"missing: {', '.join(missing)}."
        )
        return False

    st.markdown("## Current Snapshot")

    current_signal = snapshot["current_signal"]
    target_position = snapshot["target_position"]
    current_action = snapshot["action"]
    as_of = snapshot["as_of_date"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Signal State", current_signal)
    with col2:
        st.metric("Target Position", target_position)
    with col3:
        st.metric("Current Action", current_action)

    feed_type = snapshot.get("feed_type", "snapshot")
    st.caption(
        f"What this shows: {feed_type} values as of {as_of}; this section "
        "appears only when a real snapshot artifact is present."
    )

    return True
