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

import functools
import json
import os
from pathlib import Path

import streamlit as st

from components.pair_registry import load_pair_registry

_REPO_ROOT = Path(__file__).resolve().parents[2]
from components.display_names import resolve_short_indicator
from components.prospective_pairs import (
    n_universe as prospective_n_universe,
    n_completed as prospective_n_completed,
)


# Pairs whose Sample/legacy distinction matters in the dropdown.
# fix260620_archive_sample: the only entry (hy_ig_v2_spy "(Sample)") was
# removed when the Sample pair was retired/archived. Kept as an extension
# point for any future per-pair label suffixes.
_LABEL_SUFFIX: dict[str, str] = {}


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


@functools.lru_cache(maxsize=None)
def _oos_end(pair_id: str) -> str | None:
    p = _REPO_ROOT / "results" / pair_id / "winner_summary.json"
    try:
        end = json.loads(p.read_text()).get("oos_period_end")
    except Exception:
        return None
    return str(end)[:10] if end else None


@functools.lru_cache(maxsize=1)
def _oos_end_range_all() -> tuple[str, str] | None:
    """(earliest, latest) ``oos_period_end`` over the live (non-archived) pairs' winner_summary."""
    ends = [e for d in (_REPO_ROOT / "results").glob("*/winner_summary.json")
            if not d.parent.name.endswith("_archived") and (e := _oos_end(d.parent.name))]
    return (min(ends), max(ends)) if ends else None


def _data_through(pair_id: str | None) -> str:
    """Pair pages: that pair's own data end. Non-pair pages (home, methods): the range of data ends
    across the live pairs (the old hard-coded single date was stale and wrong for most pairs)."""
    if pair_id:
        end = _oos_end(pair_id)
        if end:
            from components import provenance as P
            if P.gate_on():                  # tagged at display time only: the cached value stays plain
                p = _REPO_ROOT / "results" / pair_id / "winner_summary.json"
                end = P.prefix(P.field_text(P.artifact(json.loads(p.read_text()), p), "oos_period_end"), 10)
            return f"Data through {end}"
    rng = _oos_end_range_all()
    if rng:
        return f"Data end dates vary by pair ({rng[0]} to {rng[1]})"
    return "Data end dates vary by pair"


def render_sidebar(pair_id: str | None = None):
    """Render the sidebar with dashboard link and finding selector.
    ``pair_id`` (optional) sets the "Data through" line from that pair's winner_summary."""
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
            f"{_data_through(pair_id)}<br>"
            f"{n_done} of {n_total} priority pairs analyzed"
            f"</p>",
            unsafe_allow_html=True,
        )
