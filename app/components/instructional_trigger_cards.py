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

from components.rolling_threshold import resolve_threshold


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

    effective_window = window
    if len(s.index) > 2:
        spacing_days = pd.Series(s.index).diff().dt.days.median()
        if pd.notna(spacing_days) and spacing_days >= 25:
            effective_window = min(window, 7)

    above = (s > threshold).astype(int)
    transitions = above.diff().fillna(0)
    up_cross_idx = s.index[transitions == 1]
    down_cross_idx = s.index[transitions == -1]

    half = effective_window // 2
    result: dict[str, pd.Series | None] = {"up": None, "down": None, "flat": None}

    def _cross_window(crossing: pd.Timestamp) -> pd.Series:
        pos = s.index.get_loc(crossing)
        lo = max(0, pos - half)
        hi = min(len(s), pos + half + 1)
        return s.iloc[lo:hi]

    def _decisive_score(crossing: pd.Timestamp, direction: str) -> float:
        pos = s.index.get_loc(crossing)
        pre = s.iloc[max(0, pos - half):pos]
        post = s.iloc[pos:min(len(s), pos + half + 1)]
        if pre.empty or post.empty:
            return -np.inf
        if direction == "up":
            clean_bonus = (
                100.0 if pre.max() < threshold and post.min() > threshold else 0.0
            )
            return (
                clean_bonus
                + max(0.0, threshold - pre.median())
                + max(0.0, post.median() - threshold)
                + max(0.0, post.max() - pre.min())
            )
        clean_bonus = (
            100.0 if pre.min() > threshold and post.max() < threshold else 0.0
        )
        return (
            clean_bonus
            + max(0.0, pre.median() - threshold)
            + max(0.0, threshold - post.median())
            + max(0.0, pre.max() - post.min())
        )

    # Up-crossing: pick the cleanest before/after threshold break, not just
    # the highest spike. This keeps the educational sparkline decisive.
    if len(up_cross_idx) > 0:
        best_idx = max(
            up_cross_idx, key=lambda crossing: _decisive_score(crossing, "up")
        )
        result["up"] = _cross_window(best_idx)

    # Down-crossing: same logic in reverse, so REDUCE/BUY cards show a
    # distinct move through the threshold instead of a sideways segment.
    if len(down_cross_idx) > 0:
        best_idx = max(
            down_cross_idx, key=lambda crossing: _decisive_score(crossing, "down")
        )
        result["down"] = _cross_window(best_idx)

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
    threshold = float(threshold)                        # plotly cannot encode the tagged float subclass
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
    pair_id: str | None = None,
) -> list[dict]:
    """Return the list of card specs for the given strategy family.

    Each card: {title, sparkline_direction, action_text, key_suffix}.
    """
    is_counter = direction in ("counter_cyclical", "countercyclical")

    if strategy == "P1":
        # Binary Long/Cash
        if pair_id == "retail_inv_sales_spy":
            return [
                dict(
                    title=f"TARGET: 100% {target_symbol}",
                    sparkline_direction="up",
                    action_text=(
                        f"At each monthly decision date, if the **{signal_display}** "
                        "value from three months earlier is at or above its "
                        "contemporaneous "
                        "60-month rolling median → set the target allocation to "
                        f"**100% {target_symbol}**."
                    ),
                    key_suffix="target_long",
                ),
                dict(
                    title="EXIT TO CASH",
                    sparkline_direction="down",
                    action_text=(
                        f"At each monthly decision date, if the **{signal_display}** "
                        "value from three months earlier is below its contemporaneous "
                        "60-month rolling median → set the target allocation to "
                        "**100% cash**."
                    ),
                    key_suffix="exit_cash",
                ),
            ]
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
                        f"{threshold:g}, it is close to the decision line "
                        f"between {target_symbol} and cash → keep current "
                        f"position; wait for a decisive crossing."
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
                        f"{threshold:g}, it is close to the decision line "
                        f"between {target_symbol} and cash → keep current "
                        f"position; wait for a decisive crossing."
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

    if strategy == "P2" and threshold is None:
        # QA_VERIFY_B1 F2: harness P2 sizes the position on the signal's place in its own trailing range;
        # it has no threshold, and the direction decides which end of the range is fully invested.
        more, less = ("lower", "higher") if is_counter else ("higher", "lower")
        return [
            dict(title="MORE EXPOSURE", sparkline_direction="up" if not is_counter else "down",
                 action_text=(f"The {more} **{signal_display}** sits in its trailing range, the larger the "
                              f"{target_symbol} position; at the {'bottom' if is_counter else 'top'} of the "
                              f"range the position is 100% {target_symbol}."),
                 key_suffix="more"),
            dict(title="PARTIAL", sparkline_direction="flat",
                 action_text=(f"In the middle of its trailing range the position is partial, in proportion "
                              f"to where **{signal_display}** sits; there is no threshold to cross."),
                 key_suffix="partial"),
            dict(title="LESS EXPOSURE", sparkline_direction="down" if not is_counter else "up",
                 action_text=(f"The {less} **{signal_display}** sits in its trailing range, the smaller the "
                              f"position; at the {'top' if is_counter else 'bottom'} of the range it is 0% "
                              f"(cash)."),
                 key_suffix="less"),
        ]

    if strategy == "P2":
        # Signal Strength — continuous scaling (legacy pairs with a recorded level)
        if not is_counter:
            return [
                dict(title="BUY", sparkline_direction="up",
                     action_text=(f"When **{signal_display}** rises above **{threshold:g}** → scale "
                                  f"{target_symbol} exposure **up** in proportion to the signal."),
                     key_suffix="buy"),
                dict(title="HOLD", sparkline_direction="flat",
                     action_text=(f"When **{signal_display}** lingers near **{threshold:g}** → exposure stays "
                                  f"partial; the signal-strength rule prevents whipsaw."),
                     key_suffix="hold"),
                dict(title="REDUCE", sparkline_direction="down",
                     action_text=(f"When **{signal_display}** falls below **{threshold:g}** → scale "
                                  f"{target_symbol} exposure **down** in proportion to the signal."),
                     key_suffix="reduce"),
            ]
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
        # Long/Short. Direction matters: counter-cyclical pairs flip SHORT
        # when the signal crosses ABOVE threshold (high signal = bearish
        # target); pro-cyclical pairs do the opposite (high signal =
        # bullish target → LONG above, SHORT below).
        if is_counter:
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
        else:
            # Pro-cyclical: high signal → long, low signal → short.
            return [
                dict(
                    title="LONG",
                    sparkline_direction="up",
                    action_text=(
                        f"When **{signal_display}** crosses **above {threshold:g}** "
                        f"→ flip to 100% long {target_symbol}."
                    ),
                    key_suffix="long",
                ),
                dict(
                    title="SHORT",
                    sparkline_direction="down",
                    action_text=(
                        f"When **{signal_display}** crosses **below {threshold:g}** "
                        f"→ flip to 100% short {target_symbol}."
                    ),
                    key_suffix="short",
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

    from components import provenance as P
    with open(winner_path) as fh:
        winner = P.artifact(json.load(fh), winner_path)   # tagged values in gate mode (v5.1)

    # fix260526 W1 #35: legacy winner_summary files (e.g. indpro_xlp) have
    # strategy_code=None — the previous default "P2" produced P2-style
    # "scale exposure proportionally" cards for what is actually a binary
    # P3_long_short strategy. Now derive from strategy_family when
    # strategy_code is missing.
    strategy_raw = winner.get("strategy_code")
    if not strategy_raw:
        fam = (winner.get("strategy_family") or "").upper()
        if fam.startswith("P1") or "LONG_CASH" in fam:
            strategy_raw = "P1"
        elif fam.startswith("P3") or "LONG_SHORT" in fam:
            strategy_raw = "P3"
        elif fam.startswith("P2") or "SIGNAL_STRENGTH" in fam:
            strategy_raw = "P2"
        else:
            strategy_raw = "P2"  # last-resort default preserved
    strategy = strategy_raw
    direction = winner.get("direction", "countercyclical")
    # Wave 10I.A defensive coerce: legacy pairs may carry `threshold_value` as a
    # non-numeric string (e.g. an expression like "hmm_prob > 0.5"). The `.get`
    # default only fires when the key is absent, so we must catch the cast error
    # and emit an APP-SEV1 L2 fallback banner instead of crashing the page.
    _raw_threshold = winner.get("threshold_value", 0.5)
    # Rolling-threshold winner whose summary carries no numeric value (daily T2_rp, indpro_spy
    # T2_roll): use the LATEST value of its documented rolling boundary recomputed from the signals
    # parquet (window + lead shift from the pair's artifacts), never a default.
    _th = resolve_threshold(pair_id, winner)
    _spec = _th["spec"]
    if _raw_threshold is None and _th["value"] is not None:
        _raw_threshold = _th["value"]
    _thr_unknown = False
    _p2_range = strategy == "P2" and winner.get("threshold_value") is None and _th["value"] is None
    try:
        # the recorded value keeps its provenance tag (float subclass; v5.1)
        threshold = _raw_threshold if isinstance(_raw_threshold, float) and not isinstance(_raw_threshold, bool) \
            else float(_raw_threshold)
    except (TypeError, ValueError):
        # No numeric threshold is recorded. The cards illustrate the rule's direction at a nominal level;
        # the caption says so (an internal schema note is not shown to readers - QA_VERIFY_B1 F2).
        threshold = 0.5
        _thr_unknown = True
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

    # #244 re-open: when the winner uses a rolling-quantile threshold the number
    # above is the LATEST value of a moving boundary, not a permanent cutoff. The
    # cards illustrate crossings at that latest level; the live rule compares the
    # signal to its rolling quantile (window from the pair's artifacts) at each date.
    _tc_low = str(winner.get("threshold_code", "")).lower()
    _is_rolling_tc = "roll" in _tc_low or _spec is not None
    _roll_desc = _th["label"] or "rolling threshold (window not recorded)"
    _thr_note = (
        f"its **{_roll_desc}** (a moving boundary; no numeric latest value is recorded)"
        if _is_rolling_tc and _thr_unknown and _spec is not None
        else f"latest value of its **{_roll_desc}** (a moving boundary) = **{threshold:g}**"
        if _is_rolling_tc
        else f"**{threshold:g}**"
    )
    if _p2_range:
        st.caption(
            f"What this shows: Strategy family **{strategy}** ({winner.get('strategy_display_name', '')}) · "
            f"position sized in proportion to the signal's place in its trailing range (no threshold) · "
            f"direction: {direction.replace('_', ' ')}."
        )
    else:
        st.caption(
            f"What this shows: Strategy family **{strategy}** "
            f"({winner.get('strategy_display_name', '')}) · "
            + ("no numeric threshold is recorded for this rule; the cards illustrate its direction at a "
               "nominal level · " if _thr_unknown else
               f"threshold loaded from `winner_summary.json` = {_thr_note} · "
               if _th["source"] != "derived" else
               f"`winner_summary.json` records no numeric threshold; recomputed from the signals file "
               f"using the documented rolling definition = {_thr_note} · ")
            +
            f"direction: {direction.replace('_', ' ')}."
        )
    if _is_rolling_tc and pair_id == "retail_inv_sales_spy":
        st.caption(
            "At every monthly decision date, compare the ratio level from three "
            "months earlier with the rolling median calculated for that date. The rule "
            "then sets a fresh binary target of 100% SPY or 100% cash. There is "
            "no hover zone, persistence rule, hysteresis, or partial position; "
            "the prior month's allocation does not alter the comparison."
        )
    elif _is_rolling_tc and not _p2_range:
        st.caption(
            f"Note: the decision boundary is a {_roll_desc} that moves "
            "over time — the single number shown is only its most recent level. "
            "The cards below illustrate a crossing at that latest level."
            + (f" The rule reads the signal {winner.get('lead_value')} trading days back."
               if str(winner.get("lead_unit", "")).startswith("day") and winner.get("lead_value") else "")
        )
    if pair_id == "cement_spy":
        st.caption(
            "Decisive crossing definition: because this is a monthly rule, "
            "a BUY trigger requires the month-end cement-growth signal to move "
            "from below the rolling threshold to at or above it. A REDUCE "
            "trigger requires the signal to move from at or above the threshold "
            "to below it. A value that only sits close to the threshold is a "
            "hovering state, not a new trading trigger."
        )

    cards = _card_specs_for_strategy(
        strategy, direction, None if _p2_range else threshold, signal_display, target_symbol, pair_id
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
                if not _p2_range:            # a range-sized rule has no crossing to draw
                    _mini_sparkline(
                        card["sparkline_direction"],
                        threshold,
                        card["title"],
                        key=f"trigger_{pair_id}_{card['key_suffix']}",
                        real_slice=real,
                    )
                st.markdown(card["action_text"])

    if not _p2_range:
        st.caption(
            f"How to read it: sparklines are drawn from {data_source_note}; "
            "thresholds match the runtime rule. The dashed horizontal line "
            "is the decision threshold at which the action in each card fires."
        )
