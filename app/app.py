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

# Inject card CSS
st.markdown("""
<style>
.pair-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 16px;
    background-color: #fafafa;
    transition: box-shadow 0.2s;
}
.pair-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.pair-card h4 {
    margin: 0 0 6px 0;
    font-size: 1.1rem;
}
.pair-card .direction-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 6px;
}
.tag-pro { background-color: #d4edda; color: #155724; }
.tag-counter { background-color: #f8d7da; color: #721c24; }
.tag-ambiguous { background-color: #fff3cd; color: #856404; }
.pair-card .metrics-row {
    display: flex;
    gap: 16px;
    margin: 8px 0;
    flex-wrap: wrap;
}
.pair-card .metric {
    font-size: 0.85rem;
}
.pair-card .metric .value {
    font-weight: 700;
    font-size: 1.1rem;
}
.pair-card .finding {
    font-size: 0.85rem;
    color: #555;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

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

# --- Render cards in 2-column grid ---
cols_per_row = 2
for i in range(0, len(pairs), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(pairs):
            break
        p = pairs[idx]

        with col:
            # Direction tag
            direction = p.get("direction", "unknown")
            if direction == "pro_cyclical":
                tag_class = "tag-pro"
                tag_label = "Pro-cyclical"
            elif direction == "counter_cyclical":
                tag_class = "tag-counter"
                tag_label = "Counter-cyclical"
            else:
                tag_class = "tag-ambiguous"
                tag_label = direction.replace("_", " ").title()

            # Direction consistency warning
            dir_warn = ""
            if not p.get("direction_consistent", True):
                dir_warn = ' <span style="color:#dc3545;font-size:0.75rem;">⚠ Direction surprise</span>'

            sharpe_str = f"{p['best_oos_sharpe']:.2f}" if p.get("best_oos_sharpe") else "—"
            bh_str = f"{p['bh_sharpe']:.2f}" if p.get("bh_sharpe") else "—"
            dd_str = f"{p['max_drawdown']:.1f}%" if p.get("max_drawdown") is not None else "—"
            bh_dd_str = f"{p['bh_drawdown']:.1f}%" if p.get("bh_drawdown") is not None else "—"
            valid_str = f"{p.get('valid_combos', 0):,}/{p.get('total_combos', 0):,}" if p.get("total_combos") else "—"

            st.markdown(f"""
<div class="pair-card">
    <h4>{p['indicator']} → {p['target']}
        <span class="direction-tag {tag_class}">{tag_label}</span>
        {dir_warn}
    </h4>
    <div class="metrics-row">
        <div class="metric">Best Sharpe<br><span class="value">{sharpe_str}</span></div>
        <div class="metric">B&H Sharpe<br><span class="value">{bh_str}</span></div>
        <div class="metric">Max DD<br><span class="value">{dd_str}</span></div>
        <div class="metric">B&H DD<br><span class="value">{bh_dd_str}</span></div>
        <div class="metric">Valid<br><span class="value">{valid_str}</span></div>
    </div>
    <div class="finding">{p.get('key_finding', '')}</div>
</div>
""", unsafe_allow_html=True)

            # Navigation buttons
            btn_cols = st.columns(4)
            with btn_cols[0]:
                st.page_link(p["story_page"], label="Story", icon="📖")
            with btn_cols[1]:
                st.page_link(p["evidence_page"], label="Evidence", icon="🔬")
            with btn_cols[2]:
                st.page_link(p["strategy_page"], label="Strategy", icon="🎯")
            with btn_cols[3]:
                st.page_link(p["methodology_page"], label="Methods", icon="📐")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    f"Generated with AIG-RLIC+ | {len(pairs)} pairs analyzed | "
    "73 priority pairs total"
    "</div>",
    unsafe_allow_html=True,
)
