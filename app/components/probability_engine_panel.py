"""Probability Engine Panel — APP-SE1 standard component.

Addresses stakeholder item S18-1. Rule APP-SE1 (AppDev SOP §3.6, §3.11.5),
with Wave 1.5 pre-render validation extension: before rendering, the
component MUST validate column presence, numeric bounds, and data integrity
(a non-degenerate series; no claim about crisis response). Invalid data surfaces as ``st.error()`` and the chart is
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

from components.rolling_threshold import latest_rolling_value, rolling_pct_spec, rolling_quantile_spec
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


def _load_winner_strategy_cumulative_return(pair_id: str) -> pd.Series | None:
    """Best-effort winner strategy cumulative return from strategy_returns CSV."""
    from components.provenance import resolve_current
    f = resolve_current(pair_id, "strategy_returns")
    if f is None:
        return None
    try:
        df = pd.read_csv(f, parse_dates=["date"]).set_index("date")
        if "strategy_equity" in df.columns:
            return (df["strategy_equity"].astype(float) - 1.0) * 100.0
        if "strategy_return" in df.columns:
            return ((1.0 + df["strategy_return"].astype(float).fillna(0.0)).cumprod() - 1.0) * 100.0
    except Exception:
        return None
    return None


def _latest_signals_file(pair_dir: Path) -> Path | None:
    """The pair's current-run ``signals_<tag>.parquet`` (provenance.resolve_current; no superseded-run guess)."""
    from components.provenance import resolve_current
    return resolve_current(Path(pair_dir).name, "signals", "parquet", rdir=pair_dir)


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

    # Constant series (e.g. an all-1 flag, a flat probability) carry no information and can
    # trivially "reach" any stress level - reject before the plausibility check.
    if series.nunique() < 2:
        return False, (
            f"Signal column `{column}` is constant (value {float(series.iloc[0]):g}); "
            "a constant series cannot be a valid signal panel."
        )

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
        # magnitude bound and rely solely on the data-integrity check.
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

    # Data integrity (Lead ruling 2026-10-18 on SE1; QA pilot-visual M2): a GENUINE degeneracy test. The series
    # must not be constant (checked above), mostly missing, truncated well before the panel ends, or - for a regime
    # probability - stuck in one regime. Nothing here asks how the signal behaved in a crisis: the earlier
    # stress-window test was passed by 64-100% of random windows (no information) and could reject a valid series.
    first = series.index.min()
    span = signals_df.loc[first:, column]
    missing = float(span.isna().mean()) if len(span) else 1.0
    if missing > 0.5:
        return False, (f"integrity: mostly missing ({missing:.0%} of the rows since the first reading "
                       f"{pd.Timestamp(first):%Y-%m} have no value)")
    rows_after = int((signals_df.index > series.index.max()).sum())
    if rows_after > max(12, int(0.10 * len(span))):
        return False, (f"integrity: truncated (the last reading is {pd.Timestamp(series.index.max()):%Y-%m}, "
                       f"{rows_after} rows before the end of the data)")
    if is_probability:
        # a probability that never leaves one regime carries no regime information (a winner threshold >= 1 can
        # never be exceeded, so the majority-regime level 0.5 is used then)
        _tv = winner.get("threshold_value")
        level = float(_tv) if _tv is not None and 0.0 <= float(_tv) < 1.0 else 0.5
        if not (float(series.min()) < level < float(series.max()) or float(series.max()) == level):
            return False, f"integrity: the probability never changes regime (always on one side of {level:g})"

    return True, "ok"


def _render_chart(
    signals_df: pd.DataFrame,
    column: str,
    display_name: str,
    threshold: float,
    is_probability: bool,
    pair_id: str,
    target_symbol: str,
    show_near_threshold_zone: bool = True,
    long_below: bool = False,
    is_rolling: bool = False,
    rolling_quantile: float | None = None,
    rolling_window: int = 60,
    rolling_min_periods: int = 36,
    rolling_label: str | None = None,
    threshold_known: bool = True,
):
    """Render the probability-engine time-series (APP-SE1 acceptance).

    ``long_below`` (Step C #244): when True the winner is countercyclical /
    threshold_rule lte-lt (hold long AT/BELOW the threshold), so the legend must
    read "long at/below, cash above" — not the hard-coded "long above".
    ``is_rolling`` (Step C #245 re-open): when True the threshold is a rolling
    quantile (e.g. T_roll_p50). The decision boundary is a TIME-VARYING series,
    not a fixed cutoff — so when ``rolling_quantile`` is supplied we recompute
    ``signal.rolling(rolling_window, min_periods=rolling_min_periods).quantile(q)``
    (exactly the pipeline's ``build_threshold``) and plot that curve, with the
    grey zone tracking it. Labelling it "rolling, latest X" while drawing a flat
    line (the prior fix) was the specific defect re-opened by the reviewer.
    """
    thr_lbl, threshold = threshold, float(threshold)   # tagged value for text, plain float for plotly (v5.1)
    # near-threshold band in the signal's own scale (QA pilot-visual L5: a fixed +-0.25 was a third of a 0-1 rank
    # and wider than a Sahm threshold of 0.3): a tenth of the signal's 5th-95th percentile range
    _s = signals_df[column].dropna()
    band = 0.10 * float(_s.quantile(0.95) - _s.quantile(0.05)) if len(_s) else 0.0
    series = signals_df[column].dropna()
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines",
            name=str(display_name),   # str(): plotly would serialise a tagged label by its raw value
            line=dict(color="#D55E00", width=1.2),
            hovertemplate="%{x|%Y-%m-%d}: %{y:.3f}<extra></extra>",
        )
    )

    # Threshold decoration. #245 re-open: a rolling threshold is a TIME-VARYING
    # series, so when we can recompute it we draw the actual curve (and track the
    # grey zone to it) instead of a flat line at the latest value.
    roll_series = None
    if is_rolling and rolling_quantile is not None and column in signals_df.columns:
        roll_series = (
            signals_df[column]
            .rolling(rolling_window, min_periods=rolling_min_periods)
            .quantile(rolling_quantile)
            .reindex(series.index)
        )
        if not roll_series.notna().any():
            roll_series = None

    if roll_series is not None:
        fig.add_trace(
            go.Scatter(
                x=roll_series.index,
                y=roll_series.values,
                mode="lines",
                name=(
                    f"Decision threshold ({rolling_label or f'rolling {rolling_window}m median'}, "
                    f"latest {thr_lbl:g}): "
                    + ("long at/below, cash above" if long_below else "long above, cash at/below")
                ),
                line=dict(color="#444444", width=1.4, dash="dash"),
                hovertemplate="%{x|%Y-%m-%d}: %{y:.3f}<extra>rolling threshold</extra>",
            )
        )
        if not is_probability and show_near_threshold_zone:
            # Grey zone (+-band) that TRACKS the rolling boundary (two edge traces
            # with a fill between them), not a flat horizontal band.
            fig.add_trace(
                go.Scatter(
                    x=roll_series.index, y=(roll_series + band).values,
                    mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=roll_series.index, y=(roll_series - band).values,
                    mode="lines", line=dict(width=0), fill="tonexty",
                    fillcolor="rgba(187,187,187,0.22)",
                    name="Grey zone: near the threshold", hoverinfo="skip",
                )
            )
    elif threshold_known:
        # Fixed-threshold path: horizontal line at the discrete threshold, with
        # an epsilon band for continuous/z-score signals where thresholds are soft.
        fig.add_trace(
            go.Scatter(
                x=[series.index.min(), series.index.max()],
                y=[threshold, threshold],
                mode="lines",
                name=(
                    f"Decision threshold ("
                    + (f"rolling, latest {thr_lbl:g}" if is_rolling else f"{thr_lbl:g}")
                    + "): "
                    + ("long at/below, cash above" if long_below else "long above, cash at/below")
                ),
                line=dict(color="#444444", width=1.2, dash="dash"),
                hoverinfo="skip",
            )
        )
        if not is_probability and show_near_threshold_zone:
            fig.add_hrect(
                y0=threshold - band,
                y1=threshold + band,
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

    if pair_id == "cement_spy":
        strategy_cum_return = _load_winner_strategy_cumulative_return(pair_id)
        if strategy_cum_return is not None:
            aligned_strategy = strategy_cum_return.loc[
                (strategy_cum_return.index >= series.index.min())
                & (strategy_cum_return.index <= series.index.max())
            ].dropna()
            if len(aligned_strategy) > 1:
                fig.add_trace(
                    go.Scatter(
                        x=aligned_strategy.index,
                        y=aligned_strategy.values,
                        mode="lines",
                        name="Winner strategy cumulative return",
                        line=dict(color="#D62728", width=1.5),
                        yaxis="y2",
                        hovertemplate="%{x|%Y-%m-%d}: %{y:.1f}%<extra></extra>",
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

    # a spike that would squash the series and hide the threshold (unrate's COVID reading, 9.4 against a 98th
    # percentile of 3.7): clip the axis at the 2nd-98th percentile range (threshold always inside) and say so;
    # nothing is dropped from the data
    if len(_s) > 20:
        lo, hi = float(_s.quantile(0.02)), float(_s.quantile(0.98))
        if hi > lo and (float(_s.max()) - lo > 1.5 * (hi - lo) or hi - float(_s.min()) > 1.5 * (hi - lo)):
            lo, hi = min(lo, threshold), max(hi, threshold)
            pad = 0.08 * (hi - lo)
            fig.update_yaxes(range=[lo - pad, hi + pad])
            fig.add_annotation(text="Axis clipped so the threshold stays readable; the most extreme readings run "
                                    "off the chart.", xref="paper", yref="paper", x=1, y=1.01, xanchor="right",
                               yanchor="bottom", showarrow=False, font=dict(size=10, color="#666666"))
    fig.update_layout(
        height=420,
        margin=dict(l=50, r=30, t=30, b=60),
        xaxis_title="Date",
        yaxis_title=str(display_name),
        yaxis2=dict(
            title=(
                "Indexed price / cumulative return"
                if pair_id == "cement_spy"
                else f"{target_symbol} indexed price"
            ),
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
        3. Pre-render validation (column presence, bounds, data integrity).
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
    show_near_threshold_zone = pair_id != "cement_spy"
    # QA_VERIFY_B1 F2: a range-sized P2 rule (harness) has no decision threshold
    _p2_range_hdr = (str(winner.get("strategy_code") or winner.get("strategy_family", "")).startswith("P2")
                     and winner.get("threshold_value") is None and not is_probability_signal)
    panel_title = (
        "Probability Engine Panel"
        if is_probability_signal
        else "Signal Monitoring Panel"
    )
    panel_caption = (
        "What this shows: how the winning signal value evolves over time; the rule sizes its position on "
        "where the value sits in its own trailing range, so there is no decision threshold to draw."
        if _p2_range_hdr else
        "What this shows: how the winning signal probability evolves over "
        "time and where the decision threshold sits."
        if is_probability_signal
        else (
            "What this shows: how the winning signal value evolves over "
            "time and where the decision threshold sits."
            if not show_near_threshold_zone
            else "What this shows: how the winning signal value evolves over "
                 "time and where the decision threshold sits. The grey zone "
                 "marks values close to the decision threshold (within a tenth of the signal's usual range), "
                 "where small period-to-period moves can flip the rule between "
                 f"long {winner.get('target_symbol', 'SPY')} and cash."
        )
    )
    st.markdown(f"### {panel_title}")
    st.caption(panel_caption)

    # ---- Load signals parquet ----
    signals_path = _latest_signals_file(pair_dir)
    if signals_path is None:
        msg = f"No signals_*.parquet under {pair_dir}"
        st.error(
            "The signal panel cannot render: the history of the signal's values is not available for this "
            "pair, so the chart cannot be drawn. The strategy results on this page do not depend on it."
        )
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    try:
        signals_df = pd.read_parquet(signals_path)
    except Exception as exc:  # pragma: no cover - defensive
        msg = f"Failed to read {signals_path.name}: {exc}"
        st.error(
            "The signal panel cannot render: the stored history of the signal's values could not be read, so "
            "the chart cannot be drawn. The strategy results on this page do not depend on it."
        )
        st.session_state[f"se1_validation_{pair_id}"] = {"ok": False, "reason": msg}
        return

    # ---- Load interpretation_metadata (schema-validated, soft — DATA-D6) ----
    # Metadata is optional for rendering, but if present it must conform to the
    # schema (APP-SEV1 L2 — loud-warning, not hard block).
    meta_path = pair_dir / "interpretation_metadata.json"
    metadata, meta_errors = validate_soft(meta_path, "interpretation_metadata")
    if meta_errors and meta_path.exists():
        # the schema errors stay out of the page (plain text for readers); they are kept for debugging
        st.session_state[f"se1_metadata_errors_{pair_id}"] = meta_errors
        st.warning(
            "The notes describing this signal's stress episodes are incomplete, so the chart uses the default "
            "episodes (the global financial crisis and the COVID shock). The strategy results on this "
            "page are unaffected."
        )
    if metadata is None:
        metadata = {}

    # ---- Pre-render validation ----
    ok, diagnostic = _validate_signal(signals_df, column, winner, metadata)
    if not ok:
        # QA / Lead (B1): a plain, factual message; the diagnostic (column names, thresholds, window lists)
        # stays in session state for debugging and is never shown to readers.
        if diagnostic.startswith("integrity:"):
            st.warning(
                "The signal panel cannot render: the stored signal history failed the data-integrity check: "
                f"{diagnostic.removeprefix('integrity: ')}. This is a data check, not a statement about how the "
                "signal behaved in crises. The strategy results on this page are computed separately and are "
                "unaffected."
            )
        else:
            st.error(
                "The signal panel cannot render: the signal's stored values did not pass the consistency checks "
                "(present, numeric, within their natural range), so the chart is held back. The strategy "
                "results on this page are computed separately and are unaffected."
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
    # the recorded value keeps its provenance tag (a float subclass) so every text that prints it is tagged (v5.1)
    threshold = (_tv if isinstance(_tv, float) else float(_tv)) if _tv is not None else 0.5
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
    # Step C #244/#245: legend direction must follow the winner's actual
    # threshold rule (lte/lt => long at/below), and a rolling threshold must be
    # labelled as its latest value, not a fixed cutoff.
    _rule = str(winner.get("threshold_rule", "")).lower()
    _long_below = _rule in ("lte", "lt")
    _tc = str(winner.get("threshold_code", "")).lower()
    _is_rolling = "roll" in _tc
    # #245 re-open: a period rolling quantile (T_roll_p25/p50/p75, T2_roll_p*) is redrawn as the actual
    # time-varying boundary, using the window recorded in the pair's artifacts (rolling_threshold.py)
    # - never an assumed 60-month median. Unknown window -> flat latest-value line, neutral label.
    _roll_q = None
    _roll_kw = {}
    _threshold_known = _tv is not None
    _qspec = rolling_quantile_spec(winner)
    if _qspec:
        _is_rolling = True
        _roll_kw = dict(rolling_label=_qspec["label"])
        if _qspec["window"] and (_tc.startswith("t_roll_p") or _tv is None):
            _roll_q = _qspec["quantile"]
            _roll_kw.update(rolling_window=_qspec["window"], rolling_min_periods=_qspec["min_periods"])
    # Trailing-percentile thresholds (daily T2_rp<NN>, e.g. hy_ig_spy 504d, vix_vix3m_spy 252d; or a
    # T2_roll winner whose summary records no number, e.g. indpro_spy): the rule compares the
    # LEAD-SHIFTED signal with its own trailing percentile. The window comes from the pair's winner
    # artifacts, never from an assumption; if the artifacts do not record it we use neutral wording
    # and draw no boundary rather than a wrong one.
    _spec = rolling_pct_spec(winner) or (_qspec if _tv is None else None)
    _lead_n = winner.get("lead_value")
    _lead_n = _lead_n if isinstance(_lead_n, int) and not isinstance(_lead_n, bool) else None
    _lead_unit_txt = {"days": "trading days", "months": "months", "quarters": "quarters"}.get(
        str(winner.get("lead_unit", "")).lower(), "periods")
    if _spec:
        _is_rolling = True
        _roll_kw = dict(rolling_label=_spec["label"])
        _raw_col = signals_df[column] if column in signals_df.columns else None
        if _spec["window"]:
            _roll_q = _spec["quantile"]
            _roll_kw.update(rolling_window=_spec["window"], rolling_min_periods=_spec["min_periods"])
            if not _threshold_known and _raw_col is not None:
                _lv = latest_rolling_value(_raw_col, _spec, _lead_n)
                if _lv is not None:
                    threshold, _threshold_known = _lv, True
        if isinstance(_lead_n, int) and _lead_n > 0 and _raw_col is not None:
            signals_df = signals_df.copy()
            signals_df[column] = signals_df[column].shift(_lead_n)
            display_name = f"{display_name} (lagged {_lead_n} {_lead_unit_txt})"
    # QA_VERIFY_B1 F2: a range-sized P2 rule (harness) has no threshold: draw no line, no near-threshold zone.
    _strat = str(winner.get("strategy_code") or winner.get("strategy_family", ""))
    _p2_range = _strat.startswith("P2") and _tv is None and not is_probability and not _spec
    if _p2_range:
        _threshold_known = False
        show_near_threshold_zone = False
    _render_chart(
        signals_df,
        column,
        display_name,
        threshold,
        is_probability,
        pair_id,
        target_symbol,
        show_near_threshold_zone=show_near_threshold_zone,
        long_below=_long_below,
        is_rolling=_is_rolling,
        rolling_quantile=_roll_q,
        threshold_known=_threshold_known,
        **_roll_kw,
    )

    # APP-SE5 universal takeaway caption
    strategy = winner.get("strategy_code") or winner.get("strategy_family", "")
    _counter = str(winner.get("direction", "")).replace("_", "") == "countercyclical"
    if _p2_range:
        takeaway = (
            f"The signal ({display_name}) sets the position size directly: exposure is proportional to "
            f"where the reading sits in its own trailing range, {'less' if _counter else 'more'} "
            f"{target_symbol} when it is higher. There is no threshold to cross."
        )
    elif is_probability:
        takeaway = (
            f"The {display_name.lower()} is the live stress meter; the strategy "
            f"scales equity exposure down whenever this probability rises above "
            f"{threshold:g}."
        )
    elif _is_rolling:
        takeaway = (
            f"The signal ({display_name}) drives the strategy; position changes "
            f"are triggered when the value crosses its "
            f"{_roll_kw.get('rolling_label', 'rolling threshold (window not recorded)')} "
            + (f"(a moving boundary, latest value {threshold:g}) — not a fixed cutoff."
               if _threshold_known else "(a moving boundary) — not a fixed cutoff.")
        )
    else:
        takeaway = (
            f"The signal ({display_name}) drives the strategy; position changes "
            f"are triggered when the value crosses {threshold:g}."
        )
    if _p2_range:
        pass
    elif str(strategy).startswith("P1"):
        takeaway += " P1 Long/Cash: any crossing flips exposure between 100% and 0%."
    elif str(strategy).startswith("P2"):
        takeaway += " P2 Signal Strength: exposure scales continuously with the signal."
    elif str(strategy).startswith("P3"):
        takeaway += " P3 Long/Short: signal polarity determines long vs short tilt."
    st.caption(f"Why this matters: {takeaway}")
