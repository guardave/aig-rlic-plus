"""KPI card renderer components."""

import streamlit as st


def kpi_card(label: str, value: str, delta: str = None, delta_color: str = "normal", delta_arrow: str | None = None):
    """Render a single KPI metric card. A neutral delta that reports no difference ('(same)') shows no arrow;
    ``delta_arrow='off'`` for a delta that is a reference value, not a change (e.g. buy-and-hold)."""
    arrow = delta_arrow or ("off" if delta_color == "off" and delta is not None and str(delta).endswith("(same)")
                            else "auto")
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color, delta_arrow=arrow)


def kpi_row(metrics: list[dict]):
    """Render a row of KPI cards.

    Args:
        metrics: List of dicts with keys matching kpi_card params
                 (label, value, delta, delta_color).
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kpi_card(**m)
