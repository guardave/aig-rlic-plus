"""AIG-RLIC+ Research Portal — Grid of Analyzed Pairs."""

import os
import sys

import streamlit as st

# Ensure components are importable
sys.path.insert(0, os.path.dirname(__file__))

from components.pair_registry import load_pair_registry
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

# --- Load pairs ---
pairs = load_pair_registry()

# --- Filter ---
filter_text = st.text_input(
    "Filter pairs",
    placeholder="Type to filter by indicator, target, or finding...",
    label_visibility="collapsed",
)

if filter_text:
    q = filter_text.lower()
    pairs = [p for p in pairs if (
        q in p["indicator"].lower()
        or q in p["target"].lower()
        or q in p.get("target_ticker", "").lower()
        or q in p.get("key_finding", "").lower()
        or q in p.get("direction", "").lower()
        or q in p.get("pair_id", "").lower()
    )]

st.markdown(f"**{len(pairs)} pair{'s' if len(pairs) != 1 else ''} analyzed**")
st.markdown("")

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
                # Header: title + direction badge
                direction = p.get("direction", "unknown")
                if direction == "pro_cyclical":
                    badge = ":green-background[Pro-cyclical]"
                elif direction == "counter_cyclical":
                    badge = ":red-background[Counter-cyclical]"
                else:
                    badge = f":orange-background[{direction.replace('_', ' ').title()}]"

                title = f"**{p['indicator']} → {p['target']}**"
                if not p.get("direction_consistent", True):
                    title += " :warning:"
                st.markdown(title)
                st.markdown(badge)

                # Metrics as compact table (no truncation)
                sharpe_val = f"{p['best_oos_sharpe']:.2f}" if p.get("best_oos_sharpe") else "—"
                bh_val = f"{p['bh_sharpe']:.2f}" if p.get("bh_sharpe") else "—"
                dd_val = f"{p['max_drawdown']:.1f}%" if p.get("max_drawdown") is not None else "—"
                bh_dd_val = f"{p['bh_drawdown']:.1f}%" if p.get("bh_drawdown") is not None else "—"
                valid_count = p.get("valid_combos", 0)
                total_count = p.get("total_combos", 0)

                st.markdown(
                    f"| | Strategy | Buy & Hold |\n"
                    f"|:--|:--:|:--:|\n"
                    f"| **Sharpe** | **{sharpe_val}** | {bh_val} |\n"
                    f"| **Max DD** | **{dd_val}** | {bh_dd_val} |\n"
                    f"| **Valid** | **{valid_count:,}** / {total_count:,} | |"
                )

                # Key finding (truncate to ~80 chars for uniform card height)
                finding = p.get("key_finding", "")
                if finding:
                    if len(finding) > 80:
                        finding = finding[:77] + "..."
                    st.caption(finding)

                # Navigation buttons
                b1, b2, b3, b4 = st.columns(4)
                b1.page_link(p["story_page"], label="Story", icon="📖")
                b2.page_link(p["evidence_page"], label="Evidence", icon="🔬")
                b3.page_link(p["strategy_page"], label="Strategy", icon="🎯")
                b4.page_link(p["methodology_page"], label="Methods", icon="📐")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    f"Generated with AIG-RLIC+ | {len(pairs)} pairs analyzed | "
    "73 priority pairs total"
    "</div>",
    unsafe_allow_html=True,
)
