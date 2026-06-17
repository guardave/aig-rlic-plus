"""Probability Engine Panel — APP-SE1 standard component.

Addresses stakeholder item S18-1. Rule APP-SE1 (AppDev SOP §3.6, §3.11.5),
with Wave 1.5 pre-render validation extension: before rendering, the
component MUST validate column presence, numeric bounds, and historical
plausibility. Invalid data surfaces as ``st.error()`` and the chart is
skipped — we never render a time-series from invalid signal values.

**Wave 4D-2 (2026-04-19) refactor per APP-WS1 + APP-SEV1 + META-CF:**
The Wave-1.5 ``_SIGNAL_CODE_TO_COLUMN`` literal-name fallback map has been
removed. ``winner_summary.json`` is now schema-validated at load via
``app.components.schema_check.validate_or_die`` — the ``signal_column``
field is guaranteed present by the schema, so the fallback map is
structurally unnecessary. Schema failures surface as ``st.error(...)``
(APP-SEV1 L1, never silent skip).

Contract:
    render_probability_engine_panel(pair_id: str) -> None

Data sources (read-only):
    - results/{pair_id}/signals_*.parquet       (most recent file auto-selected)
    - results/{pair_id}/winner_summary.json     (schema-validated — ECON-H5)
    - results/{pair_id}/interpretation_metadata.json (known_stress_episodes — DATA-D6)
"""

from __future__ import annotations

import glob
import base64
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.schema_check import SchemaValidationError, validate_or_die, validate_soft


_REPO_ROOT = Path(__file__).resolve().parents[2]


# Default column-type bounds per Rule APP-SE1 "Numeric + bounds" check.
_PROBABILITY_PREFIXES = ("hmm_", "ms_", "prob_", "stress_prob")


def _decode_plotly_array(value):
    """Decode Plotly typed-array payloads when a chart JSON uses them."""
    if isinstance(value, dict) and "bdata" in value:
        dtype = np.dtype(value.get("dtype", "f8"))
        return np.frombuffer(base64.b64decode(value["bdata"]), dtype=dtype)
    return value


def _load_target_price_overlay(pair_id: str, target_symbol: str) -> pd.Series | None:
    """Best-effort target price overlay from the pair's hero chart artifact."""
    hero_path = _REPO_ROOT / "output" / "charts" / pair_id / "plotly" / "hero.json"
    if not hero_path.exists():
        return None
    try:
        with open(hero_path) as f:
            hero = json.load(f)
        target_upper = target_symbol.upper()
        for trace in hero.get("data", []):
            name = str(trace.get("name", "")).upper()
            if target_upper not in name or "PRICE" not in name:
                continue
            x = pd.to_datetime(trace.get("x", []))
            y = _decode_plotly_array(trace.get("y", []))
            if len(x) == len(y) and len(x) > 0:
                return pd.Series(y, index=x).dropna()
    except Exception:
        return None
    return None


def _latest_signals_file(pair_dir: Path) -> Path | None:
    """Return the most recent ``signals_*.parquet`` under ``pair_dir``."""
    matches = sorted(glob.glob(str(pair_dir / "signals_*.parquet")))
    return Path(matches[-1]) if matches else None


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
        # Magnitude check is only meaningful for z-score / standardised signals.
        # Raw momentum, YoY, RoC, or basis-point signals can have arbitrarily
        # large natural-unit values — applying a ±20 threshold to them is
        # incorrect and produces false FC-APP-SEV1 failures.
        # Heuristic: treat column as a z-score if its name ends with an
        # underscore-z + optional digits suffix (e.g. "_z", "_z63", "_z126")
        # or contains "_zscore".  All other non-probability columns skip the
        # magnitude bound and rely solely on the historical-plausibility gate.
        _is_zscore_col = bool(
            re.search(r"_z\d*$", column) or "_zscore" in column
        )
        if _is_zscore_col:
            lo, hi = float(series.min()), float(series.max())
            if abs(lo) > 20 or abs(hi) > 20:
                return False, (
                    f"Signal `{column}` magnitude unusually large: "
                    f"min={lo:.4f}, max={hi:.4f} — expected z-score in ~±5 range."
                )

    # Historical plausibility — during at least one known stress window the
    # signal should reach the expected extreme. Default windows cover GFC and
    # COVID; a pair may override via interpretation_metadata.known_stress_episodes.
    stress_windows = metadata.get("known_stress_episodes") or [
        ("2008-09-01", "2009-06-30"),
        ("2020-02-15", "2020-04-30"),
    ]
    # winner["threshold_value"] may be JSON null (None) — coerce safely.
    _tv = winner.get("threshold_value")
    threshold = float(_tv) if _tv is not None else 0.5

    # Normalise stress_windows: each element may be a (start, end) tuple/list
    # OR a dict with "start"/"end" keys (as produced by Evan's
    # interpretation_metadata.json). Both forms are supported.
    def _to_window(w):
        if isinstance(w, dict):
            return w["start"], w["end"]
        return w[0], w[1]

    stress_hit = False
    for _w in stress_windows:
        win_start, win_end = _to_window(_w)
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
    target_symbol: str,
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
    fig.add_trace(
        go.Scatter(
            x=[series.index.min(), series.index.max()],
            y=[threshold, threshold],
            mode="lines",
            name=f"Decision threshold ({threshold:g}): long above, cash at/below",
            line=dict(color="#444444", width=1.2, dash="dash"),
            hoverinfo="skip",
        )
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
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=12, color="rgba(187,187,187,0.35)", symbol="square"),
                name="Grey zone: near threshold",
                hoverinfo="skip",
            )
        )

    target_price = _load_target_price_overlay(pair_id, target_symbol)
    if target_price is not None:
        aligned = target_price.loc[
            (target_price.index >= series.index.min())
            & (target_price.index <= series.index.max())
        ]
        if len(aligned) > 1:
            indexed = aligned / aligned.iloc[0] * 100.0
            fig.add_trace(
                go.Scatter(
                    x=indexed.index,
                    y=indexed.values,
                    mode="lines",
                    name=f"{target_symbol} price performance (indexed)",
                    line=dict(color="#1f77b4", width=1.2, dash="dot"),
                    yaxis="y2",
                    hovertemplate="%{x|%Y-%m-%d}: %{y:.1f}<extra></extra>",
                )
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
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=12, color="rgba(153,153,153,0.35)", symbol="square"),
                name="NBER recession period",
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        height=340,
        margin=dict(l=50, r=30, t=30, b=60),
        xaxis_title="Date",
        yaxis_title=display_name,
        yaxis2=dict(
            title=f"{target_symbol} indexed price",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
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
    pair_dir = _REPO_ROOT / "results" / pair_id

    # ---- Load + schema-validate winner_summary (APP-WS1 / ECON-H5 / META-CF) ----
    # Per APP-SEV1 L1: schema failure = st.error + short-circuit (no silent skip).
    winner_path = pair_dir / "winner_summary.json"
    try:
        winner = validate_or_die(winner_path, "winner_summary")
    except SchemaValidationError as exc:
        # validate_or_die already rendered st.error with the full error list.
        # Header still needs to render before the error so the page reads coherently.
        st.markdown("### Probability Engine Panel")
        st.session_state[f"se1_validation_{pair_id}"] = {
            "ok": False,
            "reason": f"winner_summary schema violation: {exc.errors}",
        }
        return

    # Schema guarantees signal_column is present and non-empty.
    column: str = winner["signal_column"]
    display_name: str = winner.get("signal_display_name", column)

    # ---- Panel header (per-pair adaptive title — fix260526 #34) ----
    # "Probability Engine Panel" is accurate only when the underlying signal
    # is a true probability in [0, 1] (HMM stress probability, Markov-switch
    # probability, etc.). For pairs whose winning signal is a level / z-score
    # / rate-of-change (e.g. indpro_accel, gold_copper_zscore_126d), call it
    # "Signal Monitoring Panel" instead — what the chart actually shows is
    # the signal value vs threshold, not a probability.
    is_probability_signal = column.startswith(_PROBABILITY_PREFIXES)
    panel_title = (
        "Probability Engine Panel"
        if is_probability_signal
        else "Signal Monitoring Panel"
    )
    panel_caption = (
        "What this shows: how the winning signal probability evolves over "
        "time and where the decision threshold sits."
        if is_probability_signal
        else "What this shows: how the winning signal value evolves over "
             "time and where each decision threshold sits. The grey zone "
             "means the signal hovers near 0, so small month-to-month moves "
             "can flip the rule between long "
             f"{winner.get('target_symbol', 'SPY')} and cash."
    )
    st.markdown(f"### {panel_title}")
    st.caption(panel_caption)

    # ---- Load signals parquet ----
    signals_path = _latest_signals_file(pair_dir)
    if signals_path is None:
        msg = f"No signals_*.parquet under {pair_dir}"
        st.error(
            f"Probability engine panel cannot render: {msg}\n\n"
            "Plain English: the model needs a history of indicator values "
            "to draw the time-series chart, but we can't find that file "
            "on disk. This prevents the probability panel from rendering."
        )
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    try:
        signals_df = pd.read_parquet(signals_path)
    except Exception as exc:  # pragma: no cover - defensive
        msg = f"Failed to read {signals_path.name}: {exc}"
        st.error(
            f"Probability engine panel cannot render: {msg}\n\n"
            "Plain English: the file containing the historical indicator "
            "series exists but could not be parsed — typically because "
            "it was produced by a different pandas / pyarrow version "
            "than this portal uses. Regenerate via the data pipeline."
        )
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    # ---- Load interpretation_metadata (schema-validated, soft — DATA-D6) ----
    # Metadata is optional for rendering, but if present it must conform to the
    # schema (APP-SEV1 L2 — loud-warning, not hard block).
    meta_path = pair_dir / "interpretation_metadata.json"
    metadata, meta_errors = validate_soft(meta_path, "interpretation_metadata")
    if meta_errors and meta_path.exists():
        st.warning(
            f"`interpretation_metadata.json` schema violation "
            f"(APP-SEV1 L2 — panel still renders with default stress windows): "
            + "; ".join(meta_errors[:3])
            + "\n\nPlain English: the side file that describes how to "
            "interpret the signal (stress episodes, expected direction) "
            "does not fully conform to its schema. We fell back to "
            "default stress windows (GFC + COVID) so the chart could "
            "still render, but the notes file should be regenerated."
        )
    if metadata is None:
        metadata = {}

    # ---- Pre-render validation ----
    ok, diagnostic = _validate_signal(signals_df, column, winner, metadata)
    if not ok:
        st.error(
            f"Probability engine panel cannot render: {diagnostic}\n\n"
            "Plain English: the signal data failed one of our sanity "
            "checks — it might be the wrong column, outside the expected "
            "numeric range, or it never reached its stress threshold "
            "during known historical crises. Rendering would mislead "
            "you, so the chart is held back until the data is fixed."
        )
        st.session_state[f"se1_validation_{pair_id}"] = {
            "ok": False,
            "reason": diagnostic,
            "column": column,
        }
        return

    # ---- Validation passed — record + render ----
    # winner["threshold_value"] may be JSON null (None) — coerce safely.
    _tv = winner.get("threshold_value")
    threshold = float(_tv) if _tv is not None else 0.5
    is_probability = column.startswith(_PROBABILITY_PREFIXES) or "_prob_" in column
    st.session_state[f"se1_validation_{pair_id}"] = {
        "ok": True,
        "column": column,
        "display_name": display_name,
        "threshold": threshold,
        "is_probability": is_probability,
        "signals_path": str(signals_path),
    }

    target_symbol = winner.get("target_symbol", "SPY")
    _render_chart(
        signals_df,
        column,
        display_name,
        threshold,
        is_probability,
        pair_id,
        target_symbol,
    )

    # APP-SE5 universal takeaway caption
    strategy = winner.get("strategy_code") or winner.get("strategy_family", "")
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
    if str(strategy).startswith("P1"):
        takeaway += " P1 Long/Cash: any crossing flips exposure between 100% and 0%."
    elif str(strategy).startswith("P2"):
        takeaway += " P2 Signal Strength: exposure scales continuously with the signal."
    elif str(strategy).startswith("P3"):
        takeaway += " P3 Long/Short: signal polarity determines long vs short tilt."
    st.caption(f"Why this matters: {takeaway}")
