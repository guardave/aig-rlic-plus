"""Analyst Suggestions renderer (ECON-AS / Wave 7B).

Consumer-side component that materialises the informational suggestions
stored in `results/{pair_id}/analyst_suggestions.json` as a read-only table
on the Methodology page.

Rules cited:

- **ECON-AS** (`docs/agent-sops/econometrics-agent-sop.md` Wave 7A) —
  Analyst Suggestions are informational-only. There are NO lifecycle
  fields (status / priority / assigned_to). The renderer MUST carry an
  explicit disclaimer telling the reader there is no automated follow-up
  action and that explicit team requests are required to action any entry.
- **META-CF** — Ace validates the producer artifact against
  `docs/schemas/analyst_suggestions.schema.json` via `validate_or_die`
  before rendering.
- **APP-CC1** — canonical "What this shows:" caption above the table.
- **META-ELI5** — graceful, plain-English fallback when the producer
  artifact is missing or has zero suggestions.

Contract:

- `render_analyst_suggestions(pair_id: str) -> None`
  Reads `results/{pair_id}/analyst_suggestions.json`, validates, and
  renders a single table with the ECON-AS columns plus the disclaimer.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from .schema_check import SchemaValidationError, validate_or_die


_REPO_ROOT = Path(__file__).resolve().parents[2]


_TABLE_COLUMNS = [
    "Signal",
    "Proposed by",
    "Observation",
    "Rationale",
    "Possible use case",
    "Caveats",
]


def _suggestions_to_dataframe(suggestions: list[dict]) -> pd.DataFrame:
    rows = []
    for entry in suggestions:
        rows.append(
            {
                "Signal": entry.get("signal_name", ""),
                "Proposed by": entry.get("proposed_by", ""),
                "Observation": entry.get("observation", ""),
                "Rationale": entry.get("rationale", ""),
                "Possible use case": entry.get("possible_use_case", ""),
                "Caveats": entry.get("caveats", ""),
            }
        )
    return pd.DataFrame(rows, columns=_TABLE_COLUMNS)


def render_analyst_suggestions(pair_id: str) -> None:
    """Render the ECON-AS suggestions table for ``pair_id``.

    Graceful fallbacks:

    - File missing: loud `st.info(...)` explaining what the section would
      contain — consistent with META-ELI5.
    - Empty suggestions array: loud `st.info(...)` noting no suggestions
      were filed during this pair's work (a valid, non-error state).
    - Schema violation: `validate_or_die` renders the full error block and
      raises; the caller short-circuits.
    """
    instance_path = _REPO_ROOT / "results" / pair_id / "analyst_suggestions.json"

    if not instance_path.exists():
        st.info(
            f"**No analyst suggestions filed for `{pair_id}`.**\n\n"
            "Plain English: during a pair's work, any team member (Dana, "
            "Evan, Vera, Ray, Ace, Quincy) can log an observation about a "
            "signal that's outside the pair's formal scope but might be "
            "worth pursuing later. No entries have been recorded for this "
            "pair — that is a valid state, not an error."
        )
        return

    try:
        data = validate_or_die(instance_path, "analyst_suggestions")
    except SchemaValidationError:
        return

    suggestions = data.get("suggestions", [])

    st.caption(
        "What this shows: signals the team noticed during this pair's work "
        "that are outside the HY-IG × SPY formal scope. Logged here so the "
        "observations are not lost; none of them fed into this pair's "
        "winning strategy."
    )

    if not suggestions:
        st.info(
            "No suggestions filed for this pair. Plain English: the team "
            "reviewed the scope and did not flag any off-scope signals as "
            "candidates for future work during this pair's analysis."
        )
        return

    df = _suggestions_to_dataframe(suggestions)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ECON-AS explicit disclaimer — the canonical wording.
    st.info(
        "These are informational. If any warrant follow-up work, please "
        "request explicitly to the team — there is no automated action from "
        "this table."
    )

    n = len(suggestions)
    st.caption(
        f"Takeaway: {n} off-scope observation{'s' if n != 1 else ''} on "
        "file for this pair. Each includes the observed metric, the "
        "rationale, a possible use case, and honest caveats."
    )
