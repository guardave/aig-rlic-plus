"""Position Adjustment Panel — APP-SE2 standard component.

Addresses stakeholder item S18-1. Rule APP-SE2 (AppDev SOP §3.6, §3.11.5):
derived from APP-SE1. If APP-SE1 pre-render validation failed, this panel
MUST NOT compute exposure from invalid signal data — instead it renders
``st.warning("Position exposure cannot be derived without valid signal
values.")`` and skips the chart.

**Wave 4D-2 (2026-04-19) refactor per APP-WS1 + APP-SEV1 + META-CF:**
``winner_summary.json`` is loaded via ``schema_check.validate_or_die`` —
``strategy_family``, ``direction``, ``threshold_value``, and ``target_symbol``
are guaranteed present by the schema (ECON-H5). All "infer strategy from
signal_code" fallbacks dropped.

Strategy family → exposure mapping (canonical schema enums):
    P1_long_cash        → binary 0% / 100%
    P2_signal_strength  → continuous 0..100%
    P3_long_short       → −100% .. +100%

Contract:
    render_position_adjustment_panel(pair_id: str) -> None
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.schema_check import SchemaValidationError, validate_or_die


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

    # Canonical schema direction is `countercyclical` (no underscore) per
    # winner_summary.schema.json. Treat `counter_cyclical` as a legacy alias
    # but the schema-validated input guarantees canonical spelling.
    is_counter = direction in ("countercyclical", "counter_cyclical")

    if strategy == "P2_signal_strength":
        # Signal Strength: exposure scales with signal.
        if is_probability:
            if is_counter:
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
            if not is_counter:
                sigmoid = 1.0 - sigmoid
            exposure = pd.Series(sigmoid, index=sig.index).clip(0.0, 1.0) * 100.0
        return exposure

    if strategy == "P1_long_cash":
        # Long/Cash: binary 100% or 0% based on threshold crossing.
        if is_counter:
            exposure = (sig <= threshold).astype(float) * 100.0
        else:
            exposure = (sig >= threshold).astype(float) * 100.0
        return exposure

    if strategy == "P3_long_short":
        # Long/Short: full long (+100) or full short (−100).
        if is_counter:
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
    if strategy == "P3_long_short":
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

    # ---- Load + schema-validate winner_summary (APP-WS1 / ECON-H5) ----
    # Per APP-SEV1 L1: schema failure = st.error + short-circuit. No silent
    # infer-from-signal-code fallback.
    pair_dir = _REPO_ROOT / "results" / pair_id
    try:
        winner = validate_or_die(pair_dir / "winner_summary.json", "winner_summary")
    except SchemaValidationError:
        # validate_or_die already rendered st.error with the full error list.
        return

    signals_df = pd.read_parquet(se1["signals_path"])
    column = se1["column"]
    threshold = se1["threshold"]
    is_probability = se1["is_probability"]

    # Schema guarantees these four fields are present + canonical-enum valued.
    strategy = winner["strategy_family"]
    direction = winner["direction"]
    target_symbol = winner["target_symbol"]

    exposure = _compute_exposure(
        signals_df[column], strategy, threshold, direction, is_probability
    )

    _render_chart(exposure, target_symbol, pair_id, strategy)

    # APP-SE5 universal takeaway caption
    if strategy == "P2_signal_strength":
        takeaway = (
            f"Exposure scales continuously: {target_symbol} allocation falls "
            f"toward zero as the stress signal approaches 1, and returns to "
            f"100% as the signal fades."
        )
    elif strategy == "P1_long_cash":
        takeaway = (
            f"{target_symbol} exposure flips between 100% and 0% at the "
            f"threshold crossing — no partial positions."
        )
    elif strategy == "P3_long_short":
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
