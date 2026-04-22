"""AIG-RLIC+ Research Portal — Grid of Analyzed Pairs."""

import os
import sys

import streamlit as st

# Ensure components are importable
sys.path.insert(0, os.path.dirname(__file__))

from components.pair_registry import (
    load_pair_registry,
    get_nature_label,
    get_type_label,
    get_objective_label,
    get_integrity_issues,
)
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="AIG-RLIC+ Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Sidebar ---
render_sidebar()
render_glossary_sidebar()

# --- Header ---
st.title("AIG-RLIC+ Research Portal")
st.markdown("### Indicator-Target Analysis Dashboard")

st.markdown(
    "Each card below represents a completed indicator-target analysis. "
    "Click through to read the story, examine the evidence, and explore trading strategies."
)

st.markdown("---")

# --- Executive summary block ---
with st.expander("📚 What is this portal?", expanded=False):
    st.markdown(
        """
**AIG-RLIC+ Research Portal** systematically evaluates how economic indicators
predict equity market behavior. Each card below represents one completed indicator-target
analysis — a rigorous study of whether a specific signal (e.g., credit spreads,
industrial production, building permits) can be used to time equity exposure.

**How to navigate:**
- Use the filter row to narrow by indicator nature, type, strategy objective, or direction
- Click **Story** for the narrative, **Evidence** for statistics, **Strategy** for the trading rule, **Methods** for the econometrics
- Each card shows the winning strategy's Sharpe ratio and max drawdown vs buy-and-hold
        """
    )

# --- Load pairs ---
pairs = load_pair_registry()

# --- Integrity warning banner ---
issues = get_integrity_issues()
if issues:
    st.warning(
        f"⚠️ **{len(issues)} pair(s) have incomplete classification metadata.** "
        f"These pairs may not appear in filtered views. See `docs/agent-sops/team-coordination.md` for the completeness gate."
    )
    with st.expander("See which pairs"):
        for issue in issues:
            st.markdown(
                f"- `{issue['pair_id']}`: missing {', '.join(issue['missing_fields'])}"
            )

# --- Multi-dimensional filter row ---
col_search, col_nature, col_type, col_objective, col_direction = st.columns(
    [2, 1, 1, 1, 1]
)

with col_search:
    filter_text = st.text_input(
        "Search",
        placeholder="Free text search...",
        label_visibility="collapsed",
    )

with col_nature:
    nature_filter = st.selectbox(
        "Nature",
        ["All", "Leading", "Coincident", "Lagging"],
        label_visibility="collapsed",
    )

with col_type:
    type_filter = st.selectbox(
        "Type",
        ["All", "Price", "Production", "Sentiment", "Rates", "Credit", "Volatility", "Macro"],
        label_visibility="collapsed",
    )

with col_objective:
    objective_filter = st.selectbox(
        "Objective",
        ["All", "Min MDD", "Max Sharpe", "Max Return"],
        label_visibility="collapsed",
    )

with col_direction:
    direction_filter = st.selectbox(
        "Direction",
        ["All", "Pro-cyclical", "Counter-cyclical", "Ambiguous"],
        label_visibility="collapsed",
    )

# --- Apply filters (AND semantics) ---
total_pairs = len(pairs)
filtered = pairs

if filter_text:
    q = filter_text.lower()
    filtered = [
        p for p in filtered
        if (
            q in p["indicator"].lower()
            or q in p["target"].lower()
            or q in p.get("target_ticker", "").lower()
            or q in p.get("key_finding", "").lower()
            or q in p.get("pair_id", "").lower()
        )
    ]

if nature_filter != "All":
    filtered = [
        p for p in filtered
        if get_nature_label(p.get("indicator_nature")) == nature_filter
    ]

if type_filter != "All":
    filtered = [
        p for p in filtered
        if get_type_label(p.get("indicator_type")) == type_filter
    ]

if objective_filter != "All":
    filtered = [
        p for p in filtered
        if get_objective_label(p.get("strategy_objective")) == objective_filter
    ]

if direction_filter != "All":
    direction_map = {
        "Pro-cyclical": "pro_cyclical",
        "Counter-cyclical": "counter_cyclical",
        "Ambiguous": "ambiguous",
    }
    filtered = [
        p for p in filtered
        if p.get("direction") == direction_map[direction_filter]
    ]

pairs = filtered

st.markdown(
    f"**Showing {len(pairs)} of {total_pairs} pair{'s' if total_pairs != 1 else ''}**"
)
st.markdown("")


# --- Helper: performance coloring ---
def _sharpe_color(val):
    if val is None:
        return "#6c757d"
    if val > 1.0:
        return "#0f5132"
    if val >= 0.5:
        return "#664d03"
    return "#842029"


def _mdd_color(val):
    if val is None:
        return "#6c757d"
    if val > -10:
        return "#0f5132"
    if val >= -20:
        return "#664d03"
    return "#842029"


# --- Render cards in 3-column grid ---
cols_per_row = 3
for i in range(0, len(pairs), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(pairs):
            break
        p = pairs[idx]

        with col:
            with st.container(border=True):
                # Header: title + direction badge with hover hints
                direction = p.get("direction", "unknown")
                if direction == "pro_cyclical":
                    dir_html = '<span style="background:#d4edda;color:#155724;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:600;cursor:help" title="When this indicator rises, stocks tend to rise too. Think of it as &quot;good news for the economy = good news for stocks.&quot;">Pro-cyclical</span>'
                elif direction == "counter_cyclical":
                    dir_html = '<span style="background:#f8d7da;color:#721c24;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:600;cursor:help" title="When this indicator rises, stocks tend to fall. Think of it as a stress signal — higher values mean more risk ahead.">Counter-cyclical</span>'
                elif direction == "ambiguous":
                    dir_html = '<span style="background:#fff3cd;color:#856404;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:600;cursor:help" title="The direction depends on context. Sometimes rising values are bullish, sometimes bearish — it changes with market conditions.">Ambiguous</span>'
                else:
                    dir_label = direction.replace("_", " ").title()
                    dir_html = f'<span style="background:#e2e3e5;color:#383d41;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:600">{dir_label}</span>'

                warn_html = ""
                if not p.get("direction_consistent", True):
                    warn_html = ' <span style="cursor:help" title="Surprise: the data showed the opposite direction from what economic theory predicted. This is an important finding — see the Story page for the explanation.">&#9888;&#65039;</span>'

                # Sample (benchmark / reference implementation) badge
                # Wave 10G.2 (2026-04-22): hy_ig_v2_spy is the canonical
                # quality benchmark — flagged via is_sample in pair_registry.
                if p.get("is_sample"):
                    st.markdown(
                        '<span style="background:#0d6efd;color:#fff;padding:3px 10px;'
                        'border-radius:4px;font-size:0.75rem;font-weight:700;letter-spacing:0.4px;'
                        'cursor:help" title="Canonical reference pair. All future pairs are '
                        'quality-compared against this dashboard.">★ SAMPLE — REFERENCE IMPLEMENTATION</span>',
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"**{p['indicator']} → {p['target']}**{warn_html}",
                    unsafe_allow_html=True,
                )
                st.markdown(dir_html, unsafe_allow_html=True)

                # Classification chips
                nature_chip = get_nature_label(p.get("indicator_nature"))
                type_chip = get_type_label(p.get("indicator_type"))
                objective_chip = get_objective_label(p.get("strategy_objective"))

                nature_colors = {
                    "Leading": "#cfe2ff",
                    "Coincident": "#fff3cd",
                    "Lagging": "#f8d7da",
                    "Unknown": "#e2e3e5",
                }
                type_colors = {
                    "Credit": "#d1e7dd",
                    "Production": "#cfe2ff",
                    "Volatility": "#fff3cd",
                    "Rates": "#f8d7da",
                    "Sentiment": "#e7d6f5",
                    "Price": "#d1ecf1",
                    "Macro": "#fce5cd",
                    "Unknown": "#e2e3e5",
                }
                objective_colors = {
                    "Min MDD": "#d1e7dd",
                    "Max Sharpe": "#cfe2ff",
                    "Max Return": "#fff3cd",
                    "Unknown": "#e2e3e5",
                }

                chips_html = (
                    f'<div style="margin-top:6px;margin-bottom:6px">'
                    f'<span style="background:{nature_colors.get(nature_chip, "#e2e3e5")};color:#333;padding:2px 8px;border-radius:4px;font-size:0.75rem;margin-right:4px">{nature_chip}</span>'
                    f'<span style="background:{type_colors.get(type_chip, "#e2e3e5")};color:#333;padding:2px 8px;border-radius:4px;font-size:0.75rem;margin-right:4px">{type_chip}</span>'
                    f'<span style="background:{objective_colors.get(objective_chip, "#e2e3e5")};color:#333;padding:2px 8px;border-radius:4px;font-size:0.75rem">{objective_chip}</span>'
                    f'</div>'
                )
                st.markdown(chips_html, unsafe_allow_html=True)

                # Metrics as compact table (with performance coloring)
                sharpe_raw = p.get("best_oos_sharpe")
                dd_raw = p.get("max_drawdown")
                sharpe_val = f"{sharpe_raw:.2f}" if sharpe_raw is not None else "—"
                bh_val = f"{p['bh_sharpe']:.2f}" if p.get("bh_sharpe") is not None else "—"
                # META-UC (Wave 8B-2): `dd_raw` / `bh_drawdown` are normalized
                # to percent-form for all pairs at pair_registry.py (ratio
                # pairs like hy_ig_v2_spy are scaled ×100 upstream). Keep
                # literal-"%" suffix here; `_mdd_color` thresholds (-10, -20)
                # also operate on percent-form values.
                dd_val = f"{dd_raw:.1f}%" if dd_raw is not None else "—"
                bh_dd_val = f"{p['bh_drawdown']:.1f}%" if p.get("bh_drawdown") is not None else "—"
                valid_count = p.get("valid_combos", 0)
                total_count = p.get("total_combos", 0)

                sharpe_color = _sharpe_color(sharpe_raw)
                dd_color = _mdd_color(dd_raw)

                sharpe_cell = f'<span style="color:{sharpe_color};font-weight:700">{sharpe_val}</span>'
                dd_cell = f'<span style="color:{dd_color};font-weight:700">{dd_val}</span>'

                st.markdown(
                    f"| | Strategy | Buy & Hold |\n"
                    f"|:--|:--:|:--:|\n"
                    f"| **Sharpe** | {sharpe_cell} | {bh_val} |\n"
                    f"| **Max DD** | {dd_cell} | {bh_dd_val} |\n"
                    f"| **Valid** | **{valid_count:,}** / {total_count:,} | |",
                    unsafe_allow_html=True,
                )

                # Key finding (full text — card height aligned via CSS)
                finding = p.get("key_finding", "")
                if finding:
                    st.caption(finding)

                # Navigation buttons (2x2 to avoid label clipping)
                nav_links = [
                    ("Story", "📖", p["story_page"]),
                    ("Evidence", "🔬", p["evidence_page"]),
                    ("Strategy", "🎯", p["strategy_page"]),
                    ("Methods", "📐", p["methodology_page"]),
                ]
                r1a, r1b = st.columns(2)
                r2a, r2b = st.columns(2)
                for slot, (label, icon, page_path) in zip(
                    [r1a, r1b, r2a, r2b], nav_links
                ):
                    try:
                        slot.page_link(page_path, label=label, icon=icon)
                    except Exception:
                        # Fallback: derive URL from page filename
                        url_name = os.path.splitext(os.path.basename(page_path))[0]
                        url_name = "_".join(url_name.split("_")[1:])  # strip numeric prefix
                        slot.markdown(f"{icon} [{label}](/{url_name})")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    f"Generated with AIG-RLIC+ | {len(pairs)} pairs shown | "
    "73 priority pairs total"
    "</div>",
    unsafe_allow_html=True,
)
