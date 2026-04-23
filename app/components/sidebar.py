"""Global sidebar navigation with finding selector."""

import streamlit as st


# Registry of all findings with their pages.
# Wave 10G.1 (2026-04-22): v1 hy_ig_spy entry removed — pair archived to
# results/hy_ig_spy_v1/ and pages moved to app/pages_archive/. The Sample
# (canonical reference) is now hy_ig_v2_spy, surfaced via pair_registry.py
# auto-discovery and rendered with the is_sample badge on the landing page.
FINDINGS = [
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
        "id": "sofr_ted_spy",
        "label": "SOFR-TED → SPY",
        "pages": {
            "Story": "pages/6_sofr_ted_spy_story.py",
            "Evidence": "pages/6_sofr_ted_spy_evidence.py",
            "Strategy": "pages/6_sofr_ted_spy_strategy.py",
            "Methodology": "pages/6_sofr_ted_spy_methodology.py",
        },
    },
    {
        "id": "dff_ted_spy",
        "label": "DFF-TED → SPY",
        "pages": {
            "Story": "pages/11_dff_ted_spy_story.py",
            "Evidence": "pages/11_dff_ted_spy_evidence.py",
            "Strategy": "pages/11_dff_ted_spy_strategy.py",
            "Methodology": "pages/11_dff_ted_spy_methodology.py",
        },
    },
    {
        "id": "ted_spliced_spy",
        "label": "Spliced TED → SPY",
        "pages": {
            "Story": "pages/12_ted_spliced_spy_story.py",
            "Evidence": "pages/12_ted_spliced_spy_evidence.py",
            "Strategy": "pages/12_ted_spliced_spy_strategy.py",
            "Methodology": "pages/12_ted_spliced_spy_methodology.py",
        },
    },
    {
        "id": "vix_vix3m_spy",
        "label": "VIX/VIX3M → SPY",
        "pages": {
            "Story": "pages/8_vix_vix3m_spy_story.py",
            "Evidence": "pages/8_vix_vix3m_spy_evidence.py",
            "Strategy": "pages/8_vix_vix3m_spy_strategy.py",
            "Methodology": "pages/8_vix_vix3m_spy_methodology.py",
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
    {
        "id": "hy_ig_v2_spy",
        "label": "HY-IG Spread × SPY",
        "pages": {
            "Story": "pages/9_hy_ig_v2_spy_story.py",
            "Evidence": "pages/9_hy_ig_v2_spy_evidence.py",
            "Strategy": "pages/9_hy_ig_v2_spy_strategy.py",
            "Methodology": "pages/9_hy_ig_v2_spy_methodology.py",
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
            icons = {"Story": "📖", "Evidence": "🔬", "Strategy": "🎯", "Methodology": "📐"}
            for page_label, page_path in finding["pages"].items():
                try:
                    st.page_link(page_path, label=page_label, icon=icons.get(page_label, "📄"))
                except Exception:
                    import os
                    url_name = os.path.splitext(os.path.basename(page_path))[0]
                    url_name = "_".join(url_name.split("_")[1:])
                    icon = icons.get(page_label, "📄")
                    st.markdown(f"{icon} [{page_label}](/{url_name})")

        st.markdown("---")

        st.markdown(
            '<p style="font-size: 0.8rem; color: #999;">'
            "Data through 2025-12-31<br>"
            "6 of 73 priority pairs analyzed"
            "</p>",
            unsafe_allow_html=True,
        )
