"""Probability Engine Panel — APP-SE1 standard component.

Addresses stakeholder item S18-1. Rule APP-SE1 (AppDev SOP §3.6, §3.11.5),
with Wave 1.5 pre-render validation extension: before rendering, the
component MUST validate column presence, numeric bounds, and historical
plausibility. Invalid data surfaces as ``st.error()`` and the chart is
skipped — we never render a time-series from invalid signal values.

Contract:
    render_probability_engine_panel(pair_id: str) -> None

Data sources (read-only):
    - results/{pair_id}/signals_*.parquet       (most recent file auto-selected)
    - results/{pair_id}/winner_summary.json     (signal_column + threshold)
    - results/{pair_id}/interpretation_metadata.json (known_stress_episodes)
"""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]


# Map from signal_code (in winner_summary.json) to the canonical column name in
# the signals parquet. If the code is not in this map, we fall back to the
# literal signal_code and the validator will surface a clear error if missing.
_SIGNAL_CODE_TO_COLUMN = {
    "S6_hmm_stress": "hmm_2state_prob_stress",
    "S7_ms_stress": "ms_2state_stress_prob",
}

# Default column-type bounds per Rule APP-SE1 "Numeric + bounds" check.
_PROBABILITY_PREFIXES = ("hmm_", "ms_", "prob_", "stress_prob")


def _latest_signals_file(pair_dir: Path) -> Path | None:
    """Return the most recent ``signals_*.parquet`` under ``pair_dir``."""
    matches = sorted(glob.glob(str(pair_dir / "signals_*.parquet")))
    return Path(matches[-1]) if matches else None


def _resolve_signal_column(signals_df: pd.DataFrame, winner: dict) -> tuple[str | None, str]:
    """Resolve the canonical signal column name.

    Returns (column_name, display_name). ``column_name`` is None if unresolved.
    """
    signal_code = winner.get("signal_code", "")
    display_name = winner.get("signal_display_name", signal_code or "Signal")

    # 1) Explicit signal_column field (if producer populates it per SOP)
    if winner.get("signal_column") and winner["signal_column"] in signals_df.columns:
        return winner["signal_column"], display_name

    # 2) Map-based lookup
    mapped = _SIGNAL_CODE_TO_COLUMN.get(signal_code)
    if mapped and mapped in signals_df.columns:
        return mapped, display_name

    # 3) Literal signal_code as column name
    if signal_code and signal_code in signals_df.columns:
        return signal_code, display_name

    return None, display_name


def _validate_signal(
    signals_df: pd.DataFrame,
    column: str,
    winner: dict,
    metadata: dict,
) -> tuple[bool, str]:
    """Pre-render validation (APP-SE1, Wave 1.5 extension).

    Returns (ok, diagnostic). When ok is False the caller MUST skip the chart
    and render ``st.error(diagnostic)`` instead — we never render invalid data.
    """
    if column not in signals_df.columns:
        return False, (
            f"Signal column `{column}` missing from signals parquet. "
            f"Available columns: {list(signals_df.columns)[:8]}..."
        )

    series = signals_df[column].dropna()
    if series.empty:
        return False, f"Signal column `{column}` contains no non-null values."

    # Numeric check
    if not pd.api.types.is_numeric_dtype(series):
        return False, f"Signal column `{column}` is not numeric (dtype={series.dtype})."

    # Bounds check — probability-type signals must lie in [0, 1]
    is_probability = column.startswith(_PROBABILITY_PREFIXES) or "_prob_" in column
    if is_probability:
        lo, hi = float(series.min()), float(series.max())
        if lo < -1e-6 or hi > 1.0 + 1e-6:
            return False, (
                f"Probability signal `{column}` out of [0, 1] bounds: "
                f"min={lo:.4f}, max={hi:.4f}."
            )
    else:
        lo, hi = float(series.min()), float(series.max())
        if abs(lo) > 20 or abs(hi) > 20:
            return False, (
                f"Signal `{column}` magnitude unusually large: "
                f"min={lo:.4f}, max={hi:.4f} — expected z-score / level in ~±5 range."
            )

    # Historical plausibility — during at least one known stress window the
    # signal should reach the expected extreme. Default windows cover GFC and
    # COVID; a pair may override via interpretation_metadata.known_stress_episodes.
    stress_windows = metadata.get("known_stress_episodes") or [
        ("2008-09-01", "2009-06-30"),
        ("2020-02-15", "2020-04-30"),
    ]
    threshold = float(winner.get("threshold_value", 0.5))

    stress_hit = False
    for win_start, win_end in stress_windows:
        try:
            sliced = series.loc[win_start:win_end]
        except Exception:
            continue
        if sliced.empty:
            continue
        if is_probability:
            if sliced.max() > threshold:
                stress_hit = True
                break
        else:
            # For z-scores / levels: expect the magnitude to clearly exceed
            # a reasonable stress extreme (e.g. |value| > 1).
            if sliced.abs().max() > 1.0:
                stress_hit = True
                break

    if not stress_hit:
        return False, (
            f"Historical plausibility check failed: signal `{column}` did not "
            f"reach its stress threshold ({threshold:g}) during any known "
            f"stress window {stress_windows}. Signal may be inverted or miscoded."
        )

    return True, "ok"


def _render_chart(
    signals_df: pd.DataFrame,
    column: str,
    display_name: str,
    threshold: float,
    is_probability: bool,
    pair_id: str,
):
    """Render the probability-engine time-series (APP-SE1 acceptance)."""
    series = signals_df[column].dropna()
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines",
            name=display_name,
            line=dict(color="#D55E00", width=1.2),
            hovertemplate="%{x|%Y-%m-%d}: %{y:.3f}<extra></extra>",
        )
    )

    # Threshold decoration: horizontal line at discrete threshold (or epsilon
    # band for continuous signals where thresholds are soft).
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="#444444",
        annotation_text=f"threshold = {threshold:g}",
        annotation_position="top left",
    )
    if not is_probability:
        # Epsilon band for continuous/z-score signals: ±0.25 around threshold.
        fig.add_hrect(
            y0=threshold - 0.25,
            y1=threshold + 0.25,
            fillcolor="#BBBBBB",
            opacity=0.15,
            line_width=0,
        )

    # NBER recession shading when span > 5 years (APP-SE1 acceptance)
    span_years = (series.index.max() - series.index.min()).days / 365.25
    if span_years > 5:
        nber_bands = [
            ("2001-03-01", "2001-11-30"),
            ("2007-12-01", "2009-06-30"),
            ("2020-02-01", "2020-04-30"),
        ]
        for band_start, band_end in nber_bands:
            fig.add_vrect(
                x0=band_start,
                x1=band_end,
                fillcolor="#999999",
                opacity=0.18,
                line_width=0,
            )

    fig.update_layout(
        height=340,
        margin=dict(l=50, r=30, t=30, b=60),
        xaxis_title="Date",
        yaxis_title=display_name,
        showlegend=False,
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EEEEEE")
    fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"prob_engine_{pair_id}",
    )


def render_probability_engine_panel(pair_id: str) -> None:
    """Render the Probability Engine Panel for a pair (APP-SE1).

    Flow:
        1. Load signals parquet (most recent) + winner_summary.json.
        2. Resolve the canonical signal column name.
        3. Pre-render validation (column presence, bounds, plausibility).
        4. On failure → st.error(diagnostic); skip chart.
        5. On success → Plotly time-series + threshold line + NBER shading.
        6. 1-line st.caption() takeaway (APP-SE5).

    Also records the validation outcome in ``st.session_state`` under
    ``se1_validation_{pair_id}`` so downstream components (APP-SE2 Position
    Adjustment Panel) can gate their own rendering per the Wave 1.5
    "derived from APP-SE1" contract.
    """
    st.markdown("### Probability Engine Panel")
    st.caption(
        "How the winning signal evolves over time and where the decision "
        "threshold sits."
    )

    pair_dir = _REPO_ROOT / "results" / pair_id

    # ---- Load winner_summary ----
    winner_path = pair_dir / "winner_summary.json"
    if not winner_path.exists():
        msg = f"winner_summary.json missing at {winner_path}"
        st.error(f"Probability engine panel cannot render: {msg}")
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return
    with open(winner_path) as fh:
        winner = json.load(fh)

    # ---- Load signals parquet ----
    signals_path = _latest_signals_file(pair_dir)
    if signals_path is None:
        msg = f"No signals_*.parquet under {pair_dir}"
        st.error(f"Probability engine panel cannot render: {msg}")
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    try:
        signals_df = pd.read_parquet(signals_path)
    except Exception as exc:  # pragma: no cover - defensive
        msg = f"Failed to read {signals_path.name}: {exc}"
        st.error(f"Probability engine panel cannot render: {msg}")
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    # ---- Load interpretation_metadata (optional) ----
    metadata: dict = {}
    meta_path = pair_dir / "interpretation_metadata.json"
    if meta_path.exists():
        with open(meta_path) as fh:
            metadata = json.load(fh)

    # ---- Resolve signal column ----
    column, display_name = _resolve_signal_column(signals_df, winner)
    if column is None:
        msg = (
            f"Signal column for code `{winner.get('signal_code')}` "
            f"(display: {display_name}) not resolvable from signals parquet."
        )
        st.error(f"Probability engine panel cannot render: {msg}")
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    # ---- Pre-render validation ----
    ok, diagnostic = _validate_signal(signals_df, column, winner, metadata)
    if not ok:
        st.error(f"Probability engine panel cannot render: {diagnostic}")
        st.session_state[f"se1_validation_{pair_id}"] = {
            "ok": False,
            "reason": diagnostic,
            "column": column,
        }
        return

    # ---- Validation passed — record + render ----
    threshold = float(winner.get("threshold_value", 0.5))
    is_probability = column.startswith(_PROBABILITY_PREFIXES) or "_prob_" in column
    st.session_state[f"se1_validation_{pair_id}"] = {
        "ok": True,
        "column": column,
        "display_name": display_name,
        "threshold": threshold,
        "is_probability": is_probability,
        "signals_path": str(signals_path),
    }

    _render_chart(signals_df, column, display_name, threshold, is_probability, pair_id)

    # APP-SE5 universal takeaway caption
    strategy = winner.get("strategy_code", "")
    if is_probability:
        takeaway = (
            f"The {display_name.lower()} is the live stress meter; the strategy "
            f"scales equity exposure down whenever this probability rises above "
            f"{threshold:g}."
        )
    else:
        takeaway = (
            f"The signal ({display_name}) drives the strategy; position changes "
            f"are triggered when the value crosses {threshold:g}."
        )
    if strategy == "P1":
        takeaway += " P1 Long/Cash: any crossing flips exposure between 100% and 0%."
    elif strategy == "P2":
        takeaway += " P2 Signal Strength: exposure scales continuously with the signal."
    elif strategy == "P3":
        takeaway += " P3 Long/Short: signal polarity determines long vs short tilt."
    st.caption(takeaway)
