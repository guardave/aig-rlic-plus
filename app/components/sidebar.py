"""Global sidebar navigation and filters."""

import streamlit as st


def render_sidebar():
    """Render the global sidebar with navigation and info."""
    with st.sidebar:
        st.markdown("## AIG-RLIC+")
        st.markdown("*Indicator-Target Analysis Portal*")

        st.markdown("---")

        st.page_link("app.py", label="Dashboard", icon="🏠")

        st.markdown("---")

        st.markdown("### Finding 1: HY-IG → SPY")
        st.page_link("pages/1_hy_ig_story.py", label="Story", icon="📖")
        st.page_link("pages/2_hy_ig_evidence.py", label="Evidence", icon="🔬")
        st.page_link("pages/3_hy_ig_strategy.py", label="Strategy", icon="🎯")
        st.page_link("pages/4_hy_ig_methodology.py", label="Methodology", icon="📐")

        st.markdown("### Finding 2: INDPRO → SPY")
        st.page_link("pages/5_indpro_spy_story.py", label="Story", icon="📖")
        st.page_link("pages/5_indpro_spy_evidence.py", label="Evidence", icon="🔬")
        st.page_link("pages/5_indpro_spy_strategy.py", label="Strategy", icon="🎯")
        st.page_link("pages/5_indpro_spy_methodology.py", label="Methodology", icon="📐")

        st.markdown("### Finding 3: TED Variants → SPY")
        st.page_link("pages/6_ted_variants_story.py", label="Story", icon="📖")
        st.page_link("pages/6_ted_variants_evidence.py", label="Evidence", icon="🔬")
        st.page_link("pages/6_ted_variants_strategy.py", label="Strategy", icon="🎯")

        st.markdown("---")

        st.markdown(
            '<p style="font-size: 0.8rem; color: #999;">'
            "Data through 2025-12-31<br>"
            "3 of 73 priority pairs analyzed"
            "</p>",
            unsafe_allow_html=True,
        )
