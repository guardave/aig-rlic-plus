"""Position Adjustment Panel — APP-SE2 standard component.

Addresses stakeholder item S18-1. Rule APP-SE2 (AppDev SOP §3.6, §3.11.5):
derived from APP-SE1. If APP-SE1 pre-render validation failed, this panel
MUST NOT compute exposure from invalid signal data — instead it renders
``st.warning("Position exposure cannot be derived without valid signal
values.")`` and skips the chart.

Strategy family → exposure mapping:
    P1 (Long/Cash)         → binary 0% / 100%
    P2 (Signal Strength)   → continuous 0..100% (inverse of stress prob)
    P3 (Long/Short)        → −100% .. +100%

Contract:
    render_position_adjustment_panel(pair_id: str) -> None
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _compute_exposure(
    signal: pd.Series,
    strategy: str,
    threshold: float,
    direction: str,
    is_probability: bool,
) -> pd.Series:
    """Compute equity exposure time-series from signal values.

    For probability-type counter-cyclical signals (stress probability),
    exposure = 1 - signal when scaled, and 0 or 1 based on threshold crossing
    otherwise.
    """
    sig = signal.dropna().astype(float)

    if strategy == "P2":
        # Signal Strength: exposure scales with signal.
        if is_probability:
            if direction == "counter_cyclical":
                # stress prob high → exposure low
                exposure = (1.0 - sig).clip(0.0, 1.0) * 100.0
            else:
                exposure = sig.clip(0.0, 1.0) * 100.0
        else:
            # For z-scores/levels: map signal → [0, 1] via a smooth sigmoid.
            # Counter-cyclical: higher signal → lower exposure.
            z = (sig - threshold)
            import numpy as np
            sigmoid = 1.0 / (1.0 + np.exp(z.values))
            if direction != "counter_cyclical":
                sigmoid = 1.0 - sigmoid
            exposure = pd.Series(sigmoid, index=sig.index).clip(0.0, 1.0) * 100.0
        return exposure

    if strategy == "P1":
        # Long/Cash: binary 100% or 0% based on threshold crossing.
        if direction == "counter_cyclical":
            exposure = (sig <= threshold).astype(float) * 100.0
        else:
            exposure = (sig >= threshold).astype(float) * 100.0
        return exposure

    if strategy == "P3":
        # Long/Short: full long (+100) or full short (−100).
        if direction == "counter_cyclical":
            exposure = pd.Series(100.0, index=sig.index)
            exposure[sig > threshold] = -100.0
        else:
            exposure = pd.Series(-100.0, index=sig.index)
            exposure[sig > threshold] = 100.0
        return exposure

    # Unknown strategy — return a flat 100% exposure line and let the caller
    # surface a caption note about the fallback.
    return pd.Series(100.0, index=sig.index)


def _render_chart(
    exposure: pd.Series,
    target_symbol: str,
    pair_id: str,
    strategy: str,
):
    """Render the exposure area chart."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=exposure.index,
            y=exposure.values,
            mode="lines",
            name="Exposure",
            line=dict(color="#0072B2", width=1.2),
            fill="tozeroy",
            fillcolor="rgba(0, 114, 178, 0.20)",
            hovertemplate="%{x|%Y-%m-%d}: %{y:.1f}%<extra></extra>",
        )
    )

    # Zero line (visible especially for P3 long/short).
    fig.add_hline(y=0, line_color="#444", line_width=1)
    if strategy == "P3":
        fig.update_yaxes(range=[-110, 110])
    else:
        fig.update_yaxes(range=[-5, 105])

    fig.update_layout(
        height=300,
        margin=dict(l=50, r=30, t=20, b=60),
        xaxis_title="Date",
        yaxis_title=f"{target_symbol} Exposure (%)",
        showlegend=False,
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EEEEEE")
    fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"pos_adj_{pair_id}",
    )


def render_position_adjustment_panel(pair_id: str) -> None:
    """Render the Position Adjustment Panel for a pair (APP-SE2).

    Reads the SE1 validation state from ``st.session_state`` to gate the
    panel — if SE1 failed we render a warning and skip the chart rather than
    silently computing exposure from invalid signal values.
    """
    st.markdown("### Position Adjustment Panel")
    st.caption(
        "How the signal translates into equity exposure — the trading decision "
        "in one visual."
    )

    # ---- Gate on SE1 validation (Wave 1.5 extension contract) ----
    se1 = st.session_state.get(f"se1_validation_{pair_id}")
    if not se1 or not se1.get("ok"):
        st.warning(
            "Position exposure cannot be derived without valid signal values. "
            "See diagnostic above."
        )
        return

    # ---- Load winner + signals ----
    pair_dir = _REPO_ROOT / "results" / pair_id
    with open(pair_dir / "winner_summary.json") as fh:
        winner = json.load(fh)

    signals_df = pd.read_parquet(se1["signals_path"])
    column = se1["column"]
    threshold = se1["threshold"]
    is_probability = se1["is_probability"]

    strategy = winner.get("strategy_code", "P2")
    direction = winner.get("direction", "counter_cyclical")
    target_symbol = winner.get("target_symbol", "SPY")

    exposure = _compute_exposure(
        signals_df[column], strategy, threshold, direction, is_probability
    )

    _render_chart(exposure, target_symbol, pair_id, strategy)

    # APP-SE5 universal takeaway caption
    if strategy == "P2":
        takeaway = (
            f"Exposure scales continuously: {target_symbol} allocation falls "
            f"toward zero as the stress signal approaches 1, and returns to "
            f"100% as the signal fades."
        )
    elif strategy == "P1":
        takeaway = (
            f"{target_symbol} exposure flips between 100% and 0% at the "
            f"threshold crossing — no partial positions."
        )
    elif strategy == "P3":
        takeaway = (
            f"{target_symbol} exposure swings between +100% (long) and −100% "
            f"(short) based on signal polarity."
        )
    else:
        takeaway = (
            f"{target_symbol} exposure derived from signal {column}; see the "
            f"Strategy Summary for the exact rule."
        )
    st.caption(takeaway)
