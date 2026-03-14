"""Finding 3 — The Evidence: TED Variants Analytical Detail."""

import os, sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(page_title="TED Evidence | AIG-RLIC+", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
render_sidebar()
render_glossary_sidebar()

st.title("The Evidence: What the Data Shows")
st.markdown("*Correlation, causality, and local projections across three funding-stress measures*")
st.markdown("---")

VARIANTS = [
    ("sofr_ted_spy", "A: SOFR - DTB3"),
    ("dff_ted_spy", "B: DFF - DTB3"),
    ("ted_spliced_spy", "C: Spliced TED"),
]

tab_corr, tab_lp = st.tabs(["Correlations", "Local Projections"])

with tab_corr:
    st.markdown("### Correlation Heatmaps")
    cols = st.columns(3)
    for i, (pid, label) in enumerate(VARIANTS):
        with cols[i]:
            st.markdown(f"**{label}**")
            load_plotly_chart(f"{pid}_correlations", pair_id=pid)

with tab_lp:
    st.markdown("### Local Projections: Impulse Response by Horizon")
    cols = st.columns(3)
    for i, (pid, label) in enumerate(VARIANTS):
        with cols[i]:
            st.markdown(f"**{label}**")
            load_plotly_chart(f"{pid}_local_projections", pair_id=pid)

st.markdown("---")
st.page_link("pages/6_ted_variants_strategy.py", label="Continue to The Strategy", icon="🎯")
st.markdown("---")
st.markdown('<div class="portal-footer">Generated with AIG-RLIC+</div>', unsafe_allow_html=True)
