"""Global sidebar navigation with finding selector.

The finding list is built dynamically from `pair_registry.load_pair_registry()`
so every auto-discovered pair appears in the dropdown — there is no
hand-maintained list. The previous hand-list lagged behind the landing page
(7 pairs in sidebar vs 11 auto-discovered as of 2026-05-31).

Display labels follow the convention:
    "<INDICATOR-SHORT> → <TARGET-TICKER>"
e.g. "INDPRO → SPY", "VIX/VIX3M → SPY", "HY-IG Spread → SPY".

The short-name is derived from `pair_id` by stripping the trailing
`_<target_ticker>` suffix and consulting a small overrides table for pairs
whose short form is not a clean transliteration (HY-IG, Gold/Copper, …).
Any new pair without an override falls back to the uppercased `pair_id`
prefix — graceful, not pretty.
"""

from __future__ import annotations

import os

import streamlit as st

from components.pair_registry import load_pair_registry
from components.display_names import resolve_short_indicator
from components.prospective_pairs import (
    n_universe as prospective_n_universe,
    n_completed as prospective_n_completed,
)


# Pairs whose Sample/legacy distinction matters in the dropdown.
_LABEL_SUFFIX = {
    "hy_ig_v2_spy": " (Sample)",
}


def _build_findings() -> list[dict]:
    """Dynamically build the finding list from the auto-discovery registry."""
    pairs = load_pair_registry()
    findings = []
    for p in pairs:
        pair_id = p.get("pair_id")
        if not pair_id:
            continue
        target_ticker = p.get("target_ticker") or ""
        label = (
            f"{resolve_short_indicator(pair_id, target_ticker)} → {target_ticker or '?'}"
            + _LABEL_SUFFIX.get(pair_id, "")
        )
        findings.append({
            "id": pair_id,
            "label": label,
            "pages": {
                "Story": p.get("story_page"),
                "Evidence": p.get("evidence_page"),
                "Strategy": p.get("strategy_page"),
                "Methodology": p.get("methodology_page"),
            },
        })
    # Stable display order: Sample first, then alphabetical by label.
    findings.sort(key=lambda f: (0 if "(Sample)" in f["label"] else 1, f["label"]))
    return findings


def render_sidebar():
    """Render the sidebar with dashboard link and finding selector."""
    findings = _build_findings()

    with st.sidebar:
        st.markdown("## AIG-RLIC+")
        st.markdown("*Indicator-Target Analysis Portal*")

        st.markdown("---")

        st.page_link("app.py", label="Dashboard", icon="🏠")

        st.markdown("---")

        # Finding selector (dynamic from pair_registry)
        finding_labels = [f["label"] for f in findings]
        selected = st.selectbox(
            "Select finding",
            finding_labels,
            index=None,
            placeholder="Choose a finding...",
        )

        if selected:
            finding = next(f for f in findings if f["label"] == selected)
            icons = {"Story": "📖", "Evidence": "🔬", "Strategy": "🎯", "Methodology": "📐"}
            for page_label, page_path in finding["pages"].items():
                if not page_path:
                    continue
                try:
                    st.page_link(page_path, label=page_label, icon=icons.get(page_label, "📄"))
                except Exception:
                    url_name = os.path.splitext(os.path.basename(page_path))[0]
                    url_name = "_".join(url_name.split("_")[1:])
                    icon = icons.get(page_label, "📄")
                    st.markdown(f"{icon} [{page_label}](/{url_name})")

        st.markdown("---")

        completed_ids = {f["id"] for f in findings}
        n_total = prospective_n_universe()
        n_done = prospective_n_completed(completed_ids)
        st.markdown(
            f'<p style="font-size: 0.8rem; color: #999;">'
            f"Data through 2025-12-31<br>"
            f"{n_done} of {n_total} priority pairs analyzed"
            f"</p>",
            unsafe_allow_html=True,
        )
