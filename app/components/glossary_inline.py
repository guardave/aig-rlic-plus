"""DPS-II1 — just-in-time info icon for technical terms.

Renders a ``st.popover("ⓘ")`` beside a heading or label, sourced from
``docs/portal_glossary.json``. Silent no-op if the term is not found so
it never breaks a page render.

Usage::

    from components.glossary_inline import info_icon

    col1, col2 = st.columns([15, 1])
    with col1:
        st.markdown("#### Sharpe Ratio")
    with col2:
        info_icon("Sharpe ratio")
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def _load_glossary() -> dict:
    """Load the ``terms`` block from ``docs/portal_glossary.json``.

    Cached for the process lifetime — the file does not change during a
    Streamlit session. Returns empty dict on any read/parse error (silent
    degradation per DPS-II1).
    """
    path = _REPO_ROOT / "docs" / "portal_glossary.json"
    try:
        raw = json.loads(path.read_text())
        return raw.get("terms", {})
    except Exception:
        return {}


def info_icon(term_key: str) -> None:
    """Render a ⓘ popover beside a technical term.

    ``term_key`` is matched case-insensitively as a substring against
    glossary keys. Renders the first match. Silent no-op if:
      - the glossary file is missing or unreadable
      - no key contains ``term_key`` as a substring

    The popover shows:
      - **Term** (the full glossary key)
      - Plain-English definition
      - Example (if present)

    Never raises — designed to be a safe drop-in beside any heading.
    """
    try:
        glossary = _load_glossary()
        needle = term_key.lower()
        match_key: str | None = None
        match_val: dict | None = None
        for k, v in glossary.items():
            if needle in k.lower():
                match_key = k
                match_val = v
                break
        if match_key is None or match_val is None:
            return
        with st.popover("ⓘ", use_container_width=False):
            st.markdown(f"**{match_key}**")
            plain = match_val.get("plain_english", "")
            if plain:
                st.caption(plain)
            example = match_val.get("example", "")
            if example:
                st.caption(f"*Example: {example}*")
    except Exception:
        # DPS-II1: never let the icon break the page
        return
