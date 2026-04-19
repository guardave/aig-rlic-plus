"""Instructional Trigger Cards — APP-SE3 standard component.

Addresses stakeholder item S18-9. Rule APP-SE3 (AppDev SOP §3.6):
compact 2-4 card grid that explains "when signal crosses X → do Y".
Each card shows a mini sparkline plus action text.

Thresholds MUST match ``winner_summary.json.threshold_value`` per the
Defense-2 (consumer reconciliation) check in the Wave 1.5 extension: the
cards' decision thresholds are loaded from the same source the strategy
uses at execution time, so the user-manual view cannot drift from the
runtime rule.

Contract:
    render_instructional_trigger_cards(pair_id: str) -> None
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _mini_sparkline(
    crossing_direction: str,
    threshold: float,
    title: str,
    key: str,
) -> None:
    """Render a tiny 50x100 sparkline illustrating a threshold crossing.

    ``crossing_direction`` is one of {"up", "down", "flat"}:
      up   — signal rises above threshold (risk-on → risk-off transition)
      down — signal falls below threshold (risk-off → risk-on transition)
      flat — signal stays near threshold (no-change zone)
    """
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
    is_counter = direction == "counter_cyclical"

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
    """
    st.markdown("### How to Use the Signal — Trigger Scenarios")

    pair_dir = _REPO_ROOT / "results" / pair_id
    winner_path = pair_dir / "winner_summary.json"
    if not winner_path.exists():
        st.info("Trigger cards unavailable — winner_summary.json missing.")
        return

    with open(winner_path) as fh:
        winner = json.load(fh)

    strategy = winner.get("strategy_code", "P2")
    direction = winner.get("direction", "counter_cyclical")
    threshold = float(winner.get("threshold_value", 0.5))
    signal_display = winner.get("signal_display_name", winner.get("signal_code", "Signal"))
    target_symbol = winner.get("target_symbol", "SPY")

    st.caption(
        f"Strategy family: **{strategy}** "
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
                _mini_sparkline(
                    card["sparkline_direction"],
                    threshold,
                    card["title"],
                    key=f"trigger_{pair_id}_{card['key_suffix']}",
                )
                st.markdown(card["action_text"])

    st.caption(
        "Conceptual illustration only — thresholds match the runtime rule, "
        "but sparklines are stylised rather than historical backtest snippets."
    )
