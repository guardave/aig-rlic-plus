"""Global sidebar navigation with finding selector."""

import streamlit as st


# Registry of all findings with their pages
FINDINGS = [
    {
        "id": "hy_ig_spy",
        "label": "HY-IG → SPY",
        "pages": {
            "Story": "pages/1_hy_ig_story.py",
            "Evidence": "pages/2_hy_ig_evidence.py",
            "Strategy": "pages/3_hy_ig_strategy.py",
            "Methodology": "pages/4_hy_ig_methodology.py",
        },
    },
    {
        "id": "indpro_spy",
        "label": "INDPRO → SPY",
        "pages": {
            "Story": "pages/5_indpro_spy_story.py",
            "Evidence": "pages/5_indpro_spy_evidence.py",
            "Strategy": "pages/5_indpro_spy_strategy.py",
            "Methodology": "pages/5_indpro_spy_methodology.py",
        },
    },
    {
        "id": "ted_variants",
        "label": "TED Variants → SPY",
        "pages": {
            "Story": "pages/6_ted_variants_story.py",
            "Evidence": "pages/6_ted_variants_evidence.py",
            "Strategy": "pages/6_ted_variants_strategy.py",
            "Methodology": "pages/6_ted_variants_methodology.py",
        },
    },
    {
        "id": "permit_spy",
        "label": "Building Permits → SPY",
        "pages": {
            "Story": "pages/7_permit_spy_story.py",
            "Evidence": "pages/7_permit_spy_evidence.py",
            "Strategy": "pages/7_permit_spy_strategy.py",
            "Methodology": "pages/7_permit_spy_methodology.py",
        },
    },
]


def render_sidebar():
    """Render the sidebar with dashboard link and finding selector."""
    with st.sidebar:
        st.markdown("## AIG-RLIC+")
        st.markdown("*Indicator-Target Analysis Portal*")

        st.markdown("---")

        st.page_link("app.py", label="Dashboard", icon="🏠")

        st.markdown("---")

        # Finding selector
        finding_labels = [f["label"] for f in FINDINGS]
        selected = st.selectbox(
            "Select finding",
            finding_labels,
            index=None,
            placeholder="Choose a finding...",
        )

        if selected:
            finding = next(f for f in FINDINGS if f["label"] == selected)
            for page_label, page_path in finding["pages"].items():
                icons = {"Story": "📖", "Evidence": "🔬", "Strategy": "🎯", "Methodology": "📐"}
                st.page_link(page_path, label=page_label, icon=icons.get(page_label, "📄"))

        st.markdown("---")

        st.markdown(
            '<p style="font-size: 0.8rem; color: #999;">'
            "Data through 2025-12-31<br>"
            "4 of 73 priority pairs analyzed"
            "</p>",
            unsafe_allow_html=True,
        )
