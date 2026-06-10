"""Shared dual-panel quartile regime chart builder (Rule VIZ-QR1).

Added 2026-06-10 (fix260610_xpair_general, stakeholder direction). Every
pair's quartile regime chart must show Annualized Sharpe (left panel) and
Annualized Return % (right panel) side-by-side, with identical quartile
x-axis and per-quartile colors. Reference look: the umcsent_xlv chart the
stakeholder supplied as the canonical example
(`scripts/generate_charts_umcsent_xlv.py::chart_regime_stats`).

Single implementation per BL-DUP-9 lessons — generators import this helper
rather than re-authoring the subplot layout. Usage::

    from scripts._quartile_chart import make_dual_panel_regime_chart

    fig = make_dual_panel_regime_chart(
        quartile_labels=["Q1_low", "Q2", "Q3", "Q4_high"],
        sharpe=[0.31, 1.09, 0.93, 0.56],
        ann_return_pct=[5.5, 14.5, 12.1, 7.7],
        signal_label="UMCSENT YoY",
        x_axis_title="Sentiment YoY Quartile (Q1=Low, Q4=High)",
    )

The caller saves via its own ``save_chart`` so sidecar conventions stay
with the per-pair generator.
"""

from __future__ import annotations

from typing import Sequence

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Per-quartile colors matching the umcsent_xlv reference (Q1 red, Q2 orange,
# Q3 blue, Q4 green).
QUARTILE_COLORS = ["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"]


def make_dual_panel_regime_chart(
    quartile_labels: Sequence[str],
    sharpe: Sequence[float],
    ann_return_pct: Sequence[float],
    signal_label: str,
    x_axis_title: str,
    height: int = 470,
    takeaway: str | None = "auto",
    axis_noun: str = "Quartile",
) -> go.Figure:
    """Build the VIZ-QR1 dual-panel quartile chart.

    Parameters
    ----------
    quartile_labels : labels for the x axis, Q1 → Q4 order. Use intuitive
        forms ("Q1 (Weakest IP growth)") per fix260526 #27 — raw machine
        codes ("Q1_low") on a user surface violate VIZ-NS1.
    sharpe : annualized Sharpe ratio per quartile (same order).
    ann_return_pct : annualized return per quartile in PERCENT form
        (e.g. 14.5 for 14.5%). Callers with ratio-form data multiply by
        100 before calling.
    signal_label : short signal name used in the subplot titles
        (e.g. "UMCSENT YoY", "INDPRO YoY", "Gold/Copper Z-Score").
    x_axis_title : full x-axis title shared by both panels.
    takeaway : "auto" derives a one-line "Key: best vs worst by Sharpe"
        annotation above the chart (fix260526 #27 device); a string uses it
        verbatim; None omits the annotation.
    """
    if not (len(quartile_labels) == len(sharpe) == len(ann_return_pct)):
        raise ValueError("quartile_labels, sharpe, ann_return_pct must be equal length")

    colors = QUARTILE_COLORS[: len(quartile_labels)]
    labels = [str(l) for l in quartile_labels]

    suffix = f" {axis_noun}" if axis_noun else ""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Annualized Sharpe by {signal_label}{suffix}",
            f"Annualized Return by {signal_label}{suffix}",
        ],
    )

    fig.add_trace(go.Bar(
        x=labels, y=list(sharpe),
        name="Sharpe",
        marker_color=colors,
        text=[f"{v:.2f}" for v in sharpe],
        textposition="outside",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=labels, y=list(ann_return_pct),
        name="Ann Return %",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in ann_return_pct],
        textposition="outside",
    ), row=1, col=2)

    annotations = list(fig.layout.annotations)  # keep subplot titles
    if takeaway == "auto":
        def _flat(label: str) -> str:
            return label.replace("<br>", " ").replace(chr(10), " ").strip()
        best_i = max(range(len(sharpe)), key=lambda i: sharpe[i])
        worst_i = min(range(len(sharpe)), key=lambda i: sharpe[i])
        takeaway = (
            f"Best regime by Sharpe: {_flat(labels[best_i])} "
            f"({sharpe[best_i]:.2f}); worst: {_flat(labels[worst_i])} "
            f"({sharpe[worst_i]:.2f})."
        )
    if takeaway:
        annotations.append(dict(
            text=f"<b>Key:</b> {takeaway}",
            xref="paper", yref="paper", x=0, y=1.18, showarrow=False,
            font=dict(size=12), align="left",
        ))

    fig.update_layout(
        template="plotly_white",
        height=height,
        showlegend=False,
        margin=dict(t=110),
        annotations=annotations,
    )
    fig.update_xaxes(title_text=x_axis_title)
    fig.update_yaxes(title_text="Annualized Sharpe", row=1, col=1)
    fig.update_yaxes(title_text="Annualized Return (%)", row=1, col=2)
    return fig
