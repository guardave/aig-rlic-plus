"""Portal-wide Statistical Methods reference page.

A STATIC reference page: it documents every statistical / econometric method
the portal uses and how to read each one. Unlike the pair pages it has no
pair/registry/``validate_or_die`` coupling — it renders the canonical content
module ``app/components/statistical_methods.py`` (authored by Evan) and nothing
pair-specific. Streamlit auto-discovers ``app/pages/*.py``; the ``1`` prefix
places it at the top of the sidebar, directly under the Dashboard landing page.

This page is a THIN WRAPPER: it owns the page chrome (page config + shared CSS,
the global sidebar, and the glossary sidebar) but delegates ALL content to the
shared ``render_statistical_methods()`` function so the landing-page tab and
this standalone page render from one source of truth. Chrome is deliberately
WITHOUT the pair breadcrumb, which requires a ``pair_id`` this page does not
have.
"""

import os
import sys

# sys.path shim so `components` resolves from the sibling dir (matches the
# pattern used by every pair page, e.g. 5_indpro_spy_evidence.py).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar
from components.statistical_methods_render import render_statistical_methods


def _apply_page_config() -> None:
    """Page config + shared CSS, mirroring page_templates._apply_page_config
    but with no pair coupling."""
    st.set_page_config(
        page_title="Statistical Methods — Reference | AIG-RLIC+",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_page() -> None:
    _apply_page_config()
    render_sidebar()
    render_glossary_sidebar()
    render_statistical_methods()


render_page()
