"""Instructional Trigger Cards — APP-SE3 standard component.

Addresses stakeholder item S18-9. Rule APP-SE3 (AppDev SOP §3.6):
compact 2-4 card grid that explains "when signal crosses X → do Y".
Each card shows a mini sparkline plus action text.

Thresholds MUST match ``winner_summary.json.threshold_value`` per the
Defense-2 (consumer reconciliation) check in the Wave 1.5 extension: the
cards' decision thresholds are loaded from the same source the strategy
uses at execution time, so the user-manual view cannot drift from the
runtime rule.

**Wave 5C retro-apply (2026-04-19):** Sparklines are now drawn from the
real historical signal series (``signals_*.parquet``) rather than from
synthetic data. For each scenario card (BUY / REDUCE / HOLD), the
renderer scans the signal history for a representative crossing and
extracts a ~30-trading-day window centred on that crossing. This closes
the Wave-5 audit S18-9 spirit gap: the stakeholder intent was real-data
illustrations, not stylised curves.

Contract:
    render_instructional_trigger_cards(pair_id: str) -> None
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _latest_signals_file(pair_dir: Path) -> Path | None:
    """Return the most recent ``signals_*.parquet`` under ``pair_dir``."""
    matches = sorted(glob.glob(str(pair_dir / "signals_*.parquet")))
    return Path(matches[-1]) if matches else None


def _find_real_crossings(
    series: pd.Series,
    threshold: float,
    window: int = 30,
) -> dict[str, pd.Series | None]:
    """Locate representative real-history crossings for up / down / flat cards.

    Returns a dict with keys ``up``, ``down``, ``flat`` mapping to a
    ~``window``-day slice of the series centred on the crossing. Values
    may be None if no representative window is found (caller falls back
    to a stylised sparkline with a console note — never synthetic data
    passed off as real).
    """
    s = series.dropna().astype(float)
    if s.empty:
        return {"up": None, "down": None, "flat": None}

    above = (s > threshold).astype(int)
    transitions = above.diff().fillna(0)
    up_cross_idx = s.index[transitions == 1]
    down_cross_idx = s.index[transitions == -1]

    half = window // 2
    result: dict[str, pd.Series | None] = {"up": None, "down": None, "flat": None}

    # Up-crossing: pick the largest-magnitude post-crossing spike (most
    # educational real-history example). Fall back to first if ranking
    # fails.
    if len(up_cross_idx) > 0:
        best_idx = up_cross_idx[0]
        best_peak = -np.inf
        for crossing in up_cross_idx:
            pos = s.index.get_loc(crossing)
            lo = max(0, pos - half)
            hi = min(len(s), pos + half + 1)
            window_slice = s.iloc[lo:hi]
            peak = window_slice.max()
            if peak > best_peak:
                best_peak = peak
                best_idx = crossing
        pos = s.index.get_loc(best_idx)
        lo = max(0, pos - half)
        hi = min(len(s), pos + half + 1)
        result["up"] = s.iloc[lo:hi]

    # Down-crossing: pick the largest-magnitude pre-crossing drop.
    if len(down_cross_idx) > 0:
        best_idx = down_cross_idx[0]
        best_prior_peak = -np.inf
        for crossing in down_cross_idx:
            pos = s.index.get_loc(crossing)
            lo = max(0, pos - half)
            hi = min(len(s), pos + half + 1)
            window_slice = s.iloc[lo:hi]
            peak = window_slice.max()
            if peak > best_prior_peak:
                best_prior_peak = peak
                best_idx = crossing
        pos = s.index.get_loc(best_idx)
        lo = max(0, pos - half)
        hi = min(len(s), pos + half + 1)
        result["down"] = s.iloc[lo:hi]

    # Flat: find a window where the signal hovers around the threshold
    # band without a decisive crossing. Use rolling std to detect
    # quietest ``window``-day period whose mean is near the threshold.
    if len(s) >= window:
        roll_std = s.rolling(window).std()
        roll_mean = s.rolling(window).mean()
        # Band around threshold — widened if signal is a probability in
        # [0, 1] range; calibrated for the HY-IG v2 HMM history.
        near = roll_mean.sub(threshold).abs() <= 0.3
        quiet = roll_std <= roll_std.quantile(0.10)
        candidates = s.index[near & quiet]
        if len(candidates) > 0:
            end_idx = candidates[len(candidates) // 2]
            pos = s.index.get_loc(end_idx)
            lo = max(0, pos - window + 1)
            hi = min(len(s), pos + 1)
            result["flat"] = s.iloc[lo:hi]

    return result


def _mini_sparkline(
    crossing_direction: str,
    threshold: float,
    title: str,
    key: str,
    real_slice: pd.Series | None = None,
) -> None:
    """Render a tiny 50x100 sparkline illustrating a threshold crossing.

    When ``real_slice`` is provided (a ~30-day slice from the actual
    signal history covering the relevant crossing), the sparkline plots
    that real data. Otherwise it falls back to a stylised illustrative
    curve — this fallback is only used if no real crossing was found
    for the given direction.

    ``crossing_direction`` is one of {"up", "down", "flat"}:
      up   — signal rises above threshold (risk-on → risk-off transition)
      down — signal falls below threshold (risk-off → risk-on transition)
      flat — signal stays near threshold (no-change zone)
    """
    if real_slice is not None and len(real_slice) > 3:
        y = real_slice.values.astype(float)
        x = np.arange(len(y))
        if crossing_direction == "up":
            color = "#D55E00"
        elif crossing_direction == "down":
            color = "#009E73"
        else:
            color = "#888888"
    else:
        x = np.arange(30)
        base_low, base_high = threshold - 0.35, threshold + 0.35
        if crossing_direction == "up":
            y = np.concatenate(
                [
                    np.linspace(base_low, base_low + 0.05, 10),
                    np.linspace(base_low + 0.05, base_high, 10),
                    np.linspace(base_high, base_high + 0.1, 10),
                ]
            )
            color = "#D55E00"
        elif crossing_direction == "down":
            y = np.concatenate(
                [
                    np.linspace(base_high + 0.1, base_high, 10),
                    np.linspace(base_high, base_low + 0.05, 10),
                    np.linspace(base_low + 0.05, base_low, 10),
                ]
            )
            color = "#009E73"
        else:
            y = np.full(30, threshold) + np.random.default_rng(42).normal(0, 0.03, 30)
            color = "#888888"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x, y=y, mode="lines", line=dict(color=color, width=2))
    )
    fig.add_hline(y=threshold, line_dash="dash", line_color="#444", line_width=1)
    fig.update_layout(
        height=100,
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key,
        config={"displayModeBar": False, "staticPlot": True},
    )


def _card_specs_for_strategy(
    strategy: str,
    direction: str,
    threshold: float,
    signal_display: str,
    target_symbol: str,
) -> list[dict]:
    """Return the list of card specs for the given strategy family.

    Each card: {title, sparkline_direction, action_text, key_suffix}.
    """
    is_counter = direction in ("counter_cyclical", "countercyclical")

    if strategy == "P1":
        # Binary Long/Cash
        if is_counter:
            cards = [
                dict(
                    title="REDUCE",
                    sparkline_direction="up",
                    action_text=(
                        f"When **{signal_display}** crosses **above "
                        f"{threshold:g}** → switch to 100% cash."
                    ),
                    key_suffix="reduce",
                ),
                dict(
                    title="HOLD",
                    sparkline_direction="flat",
                    action_text=(
                        f"While **{signal_display}** hovers near "
                        f"{threshold:g} → keep current position; "
                        f"wait for a decisive crossing."
                    ),
                    key_suffix="hold",
                ),
                dict(
                    title="BUY",
                    sparkline_direction="down",
                    action_text=(
                        f"When **{signal_display}** crosses **below "
                        f"{threshold:g}** → return to 100% {target_symbol}."
                    ),
                    key_suffix="buy",
                ),
            ]
        else:
            cards = [
                dict(
                    title="BUY",
                    sparkline_direction="up",
                    action_text=(
                        f"When **{signal_display}** crosses **above "
                        f"{threshold:g}** → enter 100% {target_symbol}."
                    ),
                    key_suffix="buy",
                ),
                dict(
                    title="HOLD",
                    sparkline_direction="flat",
                    action_text=(
                        f"While **{signal_display}** hovers near "
                        f"{threshold:g} → keep current position; "
                        f"wait for a decisive crossing."
                    ),
                    key_suffix="hold",
                ),
                dict(
                    title="REDUCE",
                    sparkline_direction="down",
                    action_text=(
                        f"When **{signal_display}** crosses **below "
                        f"{threshold:g}** → switch to 100% cash."
                    ),
                    key_suffix="reduce",
                ),
            ]
        return cards

    if strategy == "P2":
        # Signal Strength — continuous scaling
        return [
            dict(
                title="REDUCE",
                sparkline_direction="up",
                action_text=(
                    f"When **{signal_display}** rises above **{threshold:g}** "
                    f"→ scale {target_symbol} exposure **down** proportionally. "
                    f"At signal = 1.0, exposure = 0%."
                ),
                key_suffix="reduce",
            ),
            dict(
                title="HOLD",
                sparkline_direction="flat",
                action_text=(
                    f"When **{signal_display}** lingers near **{threshold:g}** "
                    f"→ hold exposure at roughly {(1 - threshold) * 100:.0f}%. "
                    f"The signal-strength rule prevents whipsaw."
                ),
                key_suffix="hold",
            ),
            dict(
                title="BUY",
                sparkline_direction="down",
                action_text=(
                    f"When **{signal_display}** falls below **{threshold:g}** "
                    f"→ scale {target_symbol} exposure **back up**. "
                    f"At signal = 0, exposure = 100%."
                ),
                key_suffix="buy",
            ),
        ]

    if strategy == "P3":
        # Long/Short
        return [
            dict(
                title="SHORT",
                sparkline_direction="up",
                action_text=(
                    f"When **{signal_display}** crosses **above {threshold:g}** "
                    f"→ flip to 100% short {target_symbol}."
                ),
                key_suffix="short",
            ),
            dict(
                title="LONG",
                sparkline_direction="down",
                action_text=(
                    f"When **{signal_display}** crosses **below {threshold:g}** "
                    f"→ flip to 100% long {target_symbol}."
                ),
                key_suffix="long",
            ),
        ]

    # Fallback single card
    return [
        dict(
            title="ACT",
            sparkline_direction="up",
            action_text=(
                f"When **{signal_display}** crosses **{threshold:g}** → apply "
                f"strategy {strategy}. See Strategy Summary above for details."
            ),
            key_suffix="act",
        ),
    ]


def render_instructional_trigger_cards(pair_id: str) -> None:
    """Render the Instructional Trigger Cards for a pair (APP-SE3).

    Loads the winner's threshold from ``winner_summary.json`` so the card
    thresholds match the strategy's runtime rule (Defense-2 reconciliation).
    Sparklines are drawn from the real historical signal series whenever
    a representative crossing can be found in ``signals_*.parquet`` —
    see Wave 5C retro-apply (S18-9 spirit fix). If no real crossing is
    available, falls back to a stylised curve and labels it as such.
    """
    st.markdown("### How to Use the Signal — Trigger Scenarios")

    pair_dir = _REPO_ROOT / "results" / pair_id
    winner_path = pair_dir / "winner_summary.json"
    if not winner_path.exists():
        st.info(
            "Trigger cards unavailable — winner_summary.json missing.\n\n"
            "Plain English: the configuration file that tells us which "
            "signal and threshold to draw the trigger cards for was not "
            "found on disk, so the cards cannot render. Run the pair "
            "pipeline to regenerate it."
        )
        return

    with open(winner_path) as fh:
        winner = json.load(fh)

    strategy = winner.get("strategy_code", "P2")
    direction = winner.get("direction", "countercyclical")
    threshold = float(winner.get("threshold_value", 0.5))
    signal_display = winner.get("signal_display_name", winner.get("signal_code", "Signal"))
    target_symbol = winner.get("target_symbol", "SPY")
    signal_column = winner.get("signal_column")

    # Load real signal history for sparkline slices (Wave 5C S18-9 fix).
    real_slices: dict[str, pd.Series | None] = {"up": None, "down": None, "flat": None}
    data_source_note = "stylised (no signals parquet found)"
    signals_path = _latest_signals_file(pair_dir)
    if signals_path is not None and signal_column:
        try:
            signals_df = pd.read_parquet(signals_path)
            if signal_column in signals_df.columns:
                real_slices = _find_real_crossings(
                    signals_df[signal_column], threshold, window=30
                )
                found = sum(1 for v in real_slices.values() if v is not None)
                data_source_note = (
                    f"real history (`{signals_path.name}` column "
                    f"`{signal_column}`) — {found}/3 scenarios located"
                )
        except Exception:
            # Defensive — fall back to stylised if parquet read fails.
            data_source_note = "stylised (signals parquet read failed)"

    st.caption(
        f"What this shows: Strategy family **{strategy}** "
        f"({winner.get('strategy_display_name', '')}) · "
        f"threshold loaded from `winner_summary.json` = **{threshold:g}** · "
        f"direction: {direction.replace('_', ' ')}."
    )

    cards = _card_specs_for_strategy(
        strategy, direction, threshold, signal_display, target_symbol
    )
    columns = st.columns(len(cards))
    for col, card in zip(columns, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{card['title']}**")
                # Map card direction to real-slice key.
                slice_key_map = {
                    "up": "up",
                    "down": "down",
                    "flat": "flat",
                }
                real = real_slices.get(
                    slice_key_map.get(card["sparkline_direction"])
                )
                _mini_sparkline(
                    card["sparkline_direction"],
                    threshold,
                    card["title"],
                    key=f"trigger_{pair_id}_{card['key_suffix']}",
                    real_slice=real,
                )
                st.markdown(card["action_text"])

    st.caption(
        f"How to read it: sparklines are drawn from {data_source_note}; "
        "thresholds match the runtime rule. The dashed horizontal line "
        "is the decision threshold at which the action in each card fires."
    )
