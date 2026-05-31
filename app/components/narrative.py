"""Markdown rendering with glossary tooltips and expander parsing."""

import json
import re
from functools import lru_cache
from pathlib import Path

import streamlit as st

from .glossary import GLOSSARY

_REPO_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def _load_portal_glossary() -> dict:
    """Load portal_glossary.json terms block. Falls back to empty dict."""
    path = _REPO_ROOT / "docs" / "portal_glossary.json"
    try:
        raw = json.loads(path.read_text())
        return raw.get("terms", {})
    except Exception:
        return {}


def _build_glossary_corpus() -> list[tuple[str, str, dict]]:
    """Merge portal_glossary.json and GLOSSARY into a unified list.

    Returns list of (term, plain_english, extra_fields) tuples.
    portal_glossary.json entries take precedence when both sources have the term.
    """
    portal = _load_portal_glossary()
    corpus: dict[str, tuple[str, dict]] = {}

    # Base layer: simple GLOSSARY
    for term, defn in GLOSSARY.items():
        corpus[term.lower()] = (term, defn, {})

    # Override/extend with portal_glossary.json (richer entries)
    for term, data in portal.items():
        plain = data.get("plain_english", "")
        corpus[term.lower()] = (term, plain, data)

    return [(term, plain, extra) for term, plain, extra in corpus.values()]


def _rank_results(query: str, corpus: list[tuple[str, str, dict]]) -> list[tuple[str, str, dict]]:
    """Return corpus entries ranked by relevance to query (case-insensitive)."""
    q = query.strip().lower()
    if not q:
        return []

    scored: list[tuple[int, str, str, dict]] = []
    for term, plain, extra in corpus:
        tl = term.lower()
        pl = plain.lower()
        # Score: lower = higher priority
        if tl == q:
            score = 0
        elif tl.startswith(q):
            score = 1
        elif q in tl:
            score = 2
        elif q in pl:
            score = 3
        else:
            # Check why_it_matters + example fields too
            combined = " ".join(str(v) for v in extra.values()).lower()
            if q in combined:
                score = 4
            else:
                continue
        scored.append((score, term, plain, extra))

    scored.sort(key=lambda x: (x[0], x[1]))
    return [(term, plain, extra) for _, term, plain, extra in scored]


def render_narrative(text: str):
    """Render narrative markdown, converting expander blocks to st.expander components.

    Parses <!-- expander: Title --> ... <!-- /expander --> blocks.
    Renders regular markdown content using st.markdown (no HTML wrapping)
    so that headings, bold, lists, etc. render correctly.
    """
    pattern = r"<!--\s*expander:\s*(.+?)\s*-->(.*?)<!--\s*/expander\s*-->"
    parts = re.split(pattern, text, flags=re.DOTALL)

    i = 0
    while i < len(parts):
        if i + 2 < len(parts) and (i % 3 == 1):
            title = parts[i].strip()
            content = parts[i + 1].strip()
            with st.expander(title):
                st.markdown(content)
            i += 2
        else:
            content = parts[i].strip()
            if content:
                st.markdown(content)
            i += 1


def _md_to_html_simple(md_text: str) -> str:
    """Minimal pass-through: let Streamlit handle full markdown rendering."""
    return md_text


def render_transition(text: str):
    """Render a transition text block between sections."""
    st.markdown(f'<div class="transition-text">{text}</div>', unsafe_allow_html=True)


def _glossary_clear() -> None:
    """Reset the glossary search field. Used as the on_click callback for
    the clear button so the input re-renders empty on the next pass."""
    st.session_state["glossary_search"] = ""


# CSS that turns Streamlit's default pill button into a small borderless
# icon button — visually attached to the search input on its right, like a
# native search-box clear-X.
#
# Scoped to our button via Streamlit's `st-key-<key>` class on the element
# container (Streamlit adds this whenever a widget has a `key=`). This is
# stable across Streamlit minor versions and doesn't depend on aria-label,
# title, or internal css class names.
_GLOSSARY_CLEAR_CSS = """
<style>
/* Tighten the column gap so the clear icon hugs the text input */
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:has(.st-key-glossary_clear) {
    gap: 0.2rem;
}
/* The clear button itself: kill pill chrome and focus ring */
.st-key-glossary_clear button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #888 !important;
    padding: 0 !important;
    min-height: 38px;   /* matches Streamlit's stTextInput default height */
    height: 38px;
    width: 38px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 120ms ease, color 120ms ease;
}
.st-key-glossary_clear button:hover:not(:disabled) {
    background: rgba(0, 0, 0, 0.06) !important;
    color: #333 !important;
}
.st-key-glossary_clear button:disabled {
    color: #ccc !important;
    background: transparent !important;
    cursor: default !important;
}
/* Material icon size */
.st-key-glossary_clear button span[data-testid="stIconMaterial"] {
    font-size: 20px !important;
    line-height: 1 !important;
}
</style>
"""


def render_glossary_sidebar():
    """Render the glossary in the sidebar as a dynamic search field.

    Uses ``st.text_input`` so the user can search across term names AND
    definition text (the previous selectbox-only experiment lost this
    deep-text match — e.g. typing "annualized" no longer surfaced "OOS
    Sharpe" via its definition). Adds a small Material Symbols "close"
    icon button to the right of the input so the user can wipe the field
    with one click. CSS strips Streamlit's default pill chrome so the
    button looks like a native search-box clear-X.

    Results are ranked by relevance via ``_rank_results`` — exact match
    first, then prefix, then term substring, then plain_english substring,
    then auxiliary fields (why_it_matters / example).
    """
    corpus = _build_glossary_corpus()

    with st.sidebar:
        st.markdown("#### Glossary")
        # Inject the icon-button CSS once per render. (Streamlit dedupes
        # repeated markdown blocks via diffing, so re-injecting is cheap.)
        st.markdown(_GLOSSARY_CLEAR_CSS, unsafe_allow_html=True)

        # Two-column layout: wide input + narrow icon button.
        col_input, col_clear = st.columns([6, 1], gap="small")
        with col_input:
            query = st.text_input(
                "Search terms",
                placeholder="Type to search definitions…",
                label_visibility="collapsed",
                key="glossary_search",
            )
        with col_clear:
            # Material Symbols "close" icon (Streamlit ≥1.36). Disabled
            # state mutes the icon when the field is empty.
            st.button(
                "",
                icon=":material/close:",
                key="glossary_clear",
                on_click=_glossary_clear,
                disabled=not (query or "").strip(),
                help="Clear search",
                use_container_width=True,
            )

        if not (query or "").strip():
            st.caption("Type to search definitions.")
            return

        results = _rank_results(query, corpus)
        if not results:
            st.caption("No matching terms.")
            return

        for term, plain, extra in results[:8]:
            with st.expander(term):
                if plain:
                    st.markdown(plain)
                why = extra.get("why_it_matters", "")
                if why:
                    st.caption(f"**Why it matters:** {why}")
                example = extra.get("example", "")
                if example:
                    st.caption(f"*Example: {example}*")
