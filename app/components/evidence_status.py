"""Evidence-status honesty layer for pair results.

`results/{pair_id}/evidence_status.json` is optional. Missing files default
to `found_in_search` so legacy pairs are labelled honestly without requiring
artifact backfills or pipeline reruns.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import streamlit as st

from components.schema_check import validate_soft


_REPO_ROOT = Path(__file__).resolve().parents[2]


_STATUS_COPY: dict[str, dict[str, str]] = {
    "found_in_search": {
        "label": "Best rule found in the search",
        "short": "Promising result from testing many recipes.",
        "plain": (
            "This is the best rule found while testing many combinations. "
            "Treat it as a promising research lead, not a confirmed prediction."
        ),
        "background": "#fff3cd",
        "color": "#664d03",
    },
    "needs_final_exam": {
        "label": "Needs final exam",
        "short": "Promising, but still needs a fresh holdout test.",
        "plain": (
            "This rule looked good in the search and now needs a fresh test "
            "that was not used to choose it."
        ),
        "background": "#cff4fc",
        "color": "#055160",
    },
    "passed_final_exam": {
        "label": "Passed final exam",
        "short": "Confirmed on a fresh holdout after selection.",
        "plain": (
            "This rule passed an additional holdout test after it was chosen, "
            "so the evidence is stronger than a search result alone."
        ),
        "background": "#d1e7dd",
        "color": "#0f5132",
    },
    "failed_final_exam": {
        "label": "Failed final exam",
        "short": "Holdout test was run but did not pass — see disclosure below.",
        "plain": (
            "This rule was subjected to a final holdout test after selection, "
            "but did not pass all required conditions. The exam results are "
            "documented below. This information is provided for transparency — "
            "you can judge the findings in context."
        ),
        "background": "#f8d7da",
        "color": "#842029",
    },
}


def _default_status(pair_id: str) -> dict[str, Any]:
    copy = _STATUS_COPY["found_in_search"]
    return {
        "pair_id": pair_id,
        "schema_version": "1.0.0",
        "status": "found_in_search",
        "label": copy["label"],
        "short_explanation": copy["short"],
        "plain_english": copy["plain"],
        "source": "default_missing_file",
    }


def load_evidence_status(pair_id: str) -> tuple[dict[str, Any], list[str]]:
    """Load optional evidence status, defaulting missing files to search-grade.

    Returns `(status, errors)`. Missing file is not an error; malformed or
    schema-invalid files return the default status plus validation errors so
    the UI can surface a recoverable APP-SEV1 L2 note.
    """
    path = _REPO_ROOT / "results" / pair_id / "evidence_status.json"
    if not path.exists():
        return _default_status(pair_id), []

    data, errors = validate_soft(path, "evidence_status")
    if errors or data is None:
        return _default_status(pair_id), errors

    status = data.get("status", "found_in_search")
    copy = _STATUS_COPY.get(status, _STATUS_COPY["found_in_search"])
    merged = {
        **data,
        "label": data.get("label") or copy["label"],
        "short_explanation": data.get("short_explanation") or copy["short"],
        "plain_english": data.get("plain_english") or copy["plain"],
        "source": "evidence_status_json",
    }
    return merged, []


def evidence_status_badge_html(pair_id: str) -> str:
    """Return compact badge HTML for landing cards."""
    status, _ = load_evidence_status(pair_id)
    status_key = status.get("status", "found_in_search")
    copy = _STATUS_COPY.get(status_key, _STATUS_COPY["found_in_search"])
    label = html.escape(status.get("label") or copy["label"], quote=True)
    title = html.escape(status.get("plain_english") or copy["plain"], quote=True)
    return (
        f'<span style="background:{copy["background"]};color:{copy["color"]};'
        'padding:2px 8px;border-radius:4px;font-size:0.75rem;'
        f'font-weight:600;cursor:help" title="{title}">{label}</span>'
    )


def render_evidence_status_note(pair_id: str) -> None:
    """Render the evidence-status note near strategy/tournament claims.

    For `failed_final_exam` pairs, renders an APP-SEV1 L2 disclosure banner
    surfacing the failure reasons from evidence_status.json verbatim (DPS-PRE1).
    """
    status, errors = load_evidence_status(pair_id)
    if errors:
        st.warning(
            f"Evidence status for `{pair_id}` could not be validated; "
            "showing the conservative default of search-grade evidence."
        )

    status_key = status.get("status", "found_in_search")
    st.info(f"**Evidence status: {status['label']}**  \n{status['plain_english']}")

    # DPS-PRE1 — disclosure banner for failed_final_exam
    if status_key == "failed_final_exam":
        failure_reasons = status.get("failure_reasons") or []
        technical_note = status.get("technical_note", "")

        reasons_md = "\n".join(f"- {r}" for r in failure_reasons) if failure_reasons else ""
        banner_body = (
            "**Final Exam Result: Did Not Pass**\n\n"
            "This strategy was subjected to a rigorous final holdout test after the winning "
            "rule was selected. The test did not pass all required conditions. "
            "This does not necessarily mean the strategy is worthless — some failures "
            "reflect structural constraints (short holdout window, multiple-testing "
            "penalty, unusual market conditions) rather than model failure. "
            "The full findings are documented below so you can judge them in context.\n\n"
        )
        if reasons_md:
            banner_body += f"**Conditions that did not pass:**\n{reasons_md}\n\n"
        if technical_note:
            with st.expander("Technical detail"):
                st.markdown(technical_note)

        st.warning(banner_body)
