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


def render_glossary_sidebar():
    """Render the glossary in the sidebar as a dynamic search field.

    Replaces the old static expander with a text_input that filters and ranks
    terms by relevance in real time. Results show plain_english definition
    plus optional why_it_matters and example fields from portal_glossary.json.
    """
    corpus = _build_glossary_corpus()

    with st.sidebar:
        st.markdown("#### Glossary")
        query = st.text_input(
            "Search terms",
            placeholder="e.g. Sharpe, drawdown, OAS…",
            label_visibility="collapsed",
            key="glossary_search",
        )

        if query.strip():
            results = _rank_results(query, corpus)
            if not results:
                st.caption("No matching terms.")
            else:
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
        else:
            st.caption("Type to search definitions.")
