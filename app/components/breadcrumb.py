"""Breadcrumb / 4-step progress component for pair page navigation (N10, META-PWQ).

Renders Story -> Evidence -> Strategy -> Methodology with the current step
highlighted and the others rendered as st.page_link navigation targets.

Usage:
    from components.breadcrumb import render_breadcrumb
    render_breadcrumb("Story", "hy_ig_v2_spy")

The breadcrumb should appear directly below render_sidebar() and above the
page title. It uses only native Streamlit primitives; the single small
unsafe_allow_html usage is the centred arrow separator (a non-layout decorative
element), consistent with APP-RP1 (no nested HTML for layout).
"""

import streamlit as st

STEPS = ["Story", "Evidence", "Strategy", "Methodology"]
ICONS = {
    "Story": "📖",
    "Evidence": "🔬",
    "Strategy": "🎯",
    "Methodology": "📐",
}


def render_breadcrumb(current_page: str, pair_id: str) -> None:
    """Render a 4-step progress breadcrumb at the top of a pair page.

    Parameters
    ----------
    current_page : str
        One of "Story", "Evidence", "Strategy", "Methodology". The step
        label matching this argument is rendered as a bold, non-clickable
        "you are here" marker.
    pair_id : str
        Pair identifier used to build page_link targets. The canonical
        filename pattern is ``pages/9_{pair_id}_{step_lower}.py`` for the
        HY-IG v2 pair family; other pair pages may need to override.
    """
    if current_page not in STEPS:
        st.warning(
            f"[breadcrumb] Unknown current_page '{current_page}'; "
            f"expected one of {STEPS}.\n\n"
            "Plain English: the breadcrumb at the top of each pair page "
            "expects the current page to be one of Story, Evidence, "
            "Strategy, or Methodology. A call arrived with a different "
            "label, so the breadcrumb was skipped to avoid misleading "
            "the reader."
        )
        return

    # 7 columns: 4 step columns interleaved with 3 arrow separators.
    cols = st.columns([1, 0.1, 1, 0.1, 1, 0.1, 1])

    for i, step in enumerate(STEPS):
        col_idx = i * 2  # 0, 2, 4, 6
        with cols[col_idx]:
            page_path = f"pages/9_{pair_id}_{step.lower()}.py"
            is_current = (step == current_page)
            if is_current:
                st.markdown(f"**{ICONS[step]} {step}**")
                st.caption("What this shows: ← you are here.")
            else:
                try:
                    st.page_link(page_path, label=step, icon=ICONS[step])
                except Exception:
                    url_name = f"{pair_id}_{step.lower()}"
                    st.markdown(f"{ICONS[step]} [{step}](/{url_name})")

        if i < len(STEPS) - 1:
            with cols[col_idx + 1]:
                st.markdown(
                    "<div style='text-align:center; padding-top:10px'>→</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
