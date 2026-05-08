"""Global sidebar navigation with registry-driven finding selector."""

import os

import streamlit as st

from components.pair_registry import load_pair_registry


PAGE_ICONS = {
    "Story": "📖",
    "Evidence": "🔬",
    "Strategy": "🎯",
    "Methodology": "📐",
}


def _finding_label(pair: dict) -> str:
    """Return a compact selector label from registry metadata."""
    if pair.get("is_sample"):
        return "Sample: HY-IG × SPY"
    indicator = pair.get("indicator") or pair.get("indicator_id") or pair["pair_id"]
    target = pair.get("target_ticker") or pair.get("target") or ""
    return f"{indicator} → {target}".strip()


def _page_map(pair: dict) -> dict[str, str]:
    return {
        "Story": pair["story_page"],
        "Evidence": pair["evidence_page"],
        "Strategy": pair["strategy_page"],
        "Methodology": pair["methodology_page"],
    }


def render_sidebar():
    """Render the sidebar with dashboard link and finding selector."""
    pairs = load_pair_registry()
    findings = [
        {
            "id": pair["pair_id"],
            "label": _finding_label(pair),
            "pages": _page_map(pair),
        }
        for pair in pairs
    ]

    with st.sidebar:
        st.markdown("## AIG-RLIC+")
        st.markdown("*Indicator-Target Analysis Portal*")

        st.markdown("---")

        st.page_link("app.py", label="Dashboard", icon="🏠")

        st.markdown("---")

        # Finding selector
        finding_labels = [f["label"] for f in findings]
        selected = st.selectbox(
            "Select finding",
            finding_labels,
            index=None,
            placeholder="Choose a finding...",
        )

        if selected:
            finding = next(f for f in findings if f["label"] == selected)
            for page_label, page_path in finding["pages"].items():
                try:
                    st.page_link(
                        page_path,
                        label=page_label,
                        icon=PAGE_ICONS.get(page_label, "📄"),
                    )
                except Exception:
                    url_name = os.path.splitext(os.path.basename(page_path))[0]
                    url_name = "_".join(url_name.split("_")[1:])
                    icon = PAGE_ICONS.get(page_label, "📄")
                    st.markdown(f"{icon} [{page_label}](/{url_name})")

        st.markdown("---")

        st.markdown(
            '<p style="font-size: 0.8rem; color: #999;">'
            "Data through 2025-12-31<br>"
            f"{len(findings)} of 73 priority pairs analyzed"
            "</p>",
            unsafe_allow_html=True,
        )
