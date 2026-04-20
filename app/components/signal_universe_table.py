"""Signal Universe renderer (ECON-UD / Wave 7B).

Consumer-side component that materialises the indicator-axis and target-axis
derivative registries stored in `results/{pair_id}/signal_scope.json` as two
Methodology-page tables.

Rules cited:

- **ECON-UD** (`docs/agent-sops/econometrics-agent-sop.md` Wave 7A) —
  Universe Disclosure: every derivative considered in the pair's work is
  surfaced on the Methodology page in two sibling tables (indicator axis +
  target axis) with columns `Name | Definition | Formula | Role | Appears in`.
- **ECON-SD** (sibling rule) — only mathematical derivatives of the single
  canonical indicator and target columns are permitted in the scope registry;
  off-scope suggestions live in `analyst_suggestions.json` instead.
- **META-CF** (`docs/agent-sops/team-coordination.md`) — Ace validates the
  producer artifact against `docs/schemas/signal_scope.schema.json` via
  `validate_or_die` before rendering.
- **APP-CC1 / APP-SE5** (`docs/agent-sops/appdev-agent-sop.md`) — canonical
  "What this shows:" caption above each table; 1-line takeaway caption below.
- **META-ELI5** — graceful fallback with plain-English explanation when the
  producer artifact is missing.

Contract:

- `render_signal_universe(pair_id: str) -> None`
  Reads `results/{pair_id}/signal_scope.json`, validates against the
  `signal_scope` schema, and renders two tables under h3 subheadings.
  Short-circuits on any schema error (APP-SEV1 L1 delegated to
  `validate_or_die`).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from .schema_check import SchemaValidationError, validate_or_die


_REPO_ROOT = Path(__file__).resolve().parents[2]


# Canonical column order for the rendered tables (ECON-UD).
_TABLE_COLUMNS = ["Name", "Definition", "Formula", "Role", "Appears in"]


def _derivatives_to_dataframe(derivatives: list[dict]) -> pd.DataFrame:
    """Project the schema's derivative entries onto the ECON-UD table shape."""
    rows = []
    for entry in derivatives:
        appears = entry.get("appears_in_charts") or []
        rows.append(
            {
                "Name": entry.get("name", ""),
                "Definition": entry.get("definition", ""),
                "Formula": entry.get("formula", ""),
                "Role": entry.get("role", ""),
                "Appears in": ", ".join(appears) if appears else "—",
            }
        )
    return pd.DataFrame(rows, columns=_TABLE_COLUMNS)


def render_signal_universe(pair_id: str) -> None:
    """Render the two ECON-UD Universe Disclosure tables for ``pair_id``.

    Validates the producer artifact (`signal_scope.json`) against its schema
    via `validate_or_die`. On missing artifact, surfaces a loud META-ELI5
    fallback that tells the reader what the section would have shown and
    how to regenerate it.
    """
    instance_path = _REPO_ROOT / "results" / pair_id / "signal_scope.json"

    if not instance_path.exists():
        # META-ELI5 graceful fallback (loud-but-friendly). This is distinct
        # from validate_or_die's L1 error because a missing scope file on a
        # pre-Wave-7B pair is a known-gap, not a producer contract violation.
        st.error(
            f"**Signal universe table unavailable for `{pair_id}`.**\n\n"
            "Plain English: this section normally lists every derivative "
            "(z-scores, rates of change, regime probabilities, forward "
            "returns, etc.) that was considered during the analysis, so you "
            "can see exactly what was in and out of scope. The underlying "
            "registry file (`signal_scope.json`) has not been produced for "
            "this pair yet — this is Evan's Wave 7B artifact and is only "
            "retro-fitted for HY-IG v2 at present."
        )
        return

    try:
        data = validate_or_die(instance_path, "signal_scope")
    except SchemaValidationError:
        # validate_or_die already rendered the diagnostic block via st.error.
        # Per APP-SEV1 L1 we short-circuit and do NOT render partial tables.
        return

    indicator_axis = data.get("indicator_axis", {})
    target_axis = data.get("target_axis", {})

    ind_display = indicator_axis.get("display_name", "Indicator")
    ind_canonical = indicator_axis.get("canonical_column", "")
    tgt_display = target_axis.get("display_name", "Target")
    tgt_canonical = target_axis.get("canonical_column", "")

    # -----------------------------------------------------------------
    # Indicator derivatives
    # -----------------------------------------------------------------
    st.markdown(f"#### Indicator derivatives — {ind_display}")
    st.caption(
        f"What this shows: every derivative of the `{ind_canonical}` indicator "
        "column considered in this analysis. Includes raw series, statistical "
        "transforms (z-scores, percentile ranks), momentum measures, and "
        "regime-state probabilities."
    )

    ind_df = _derivatives_to_dataframe(indicator_axis.get("derivatives", []))
    st.dataframe(ind_df, use_container_width=True, hide_index=True)

    ind_n = len(ind_df)
    st.caption(
        f"Takeaway: {ind_n} indicator-axis derivative{'s' if ind_n != 1 else ''} "
        "disclosed. Every derivative is a mathematical transform of the single "
        f"canonical column `{ind_canonical}` (ECON-SD scope discipline)."
    )

    st.markdown("")

    # -----------------------------------------------------------------
    # Target derivatives
    # -----------------------------------------------------------------
    st.markdown(f"#### Target derivatives — {tgt_display}")
    st.caption(
        f"What this shows: every derivative of the `{tgt_canonical}` target "
        "column considered in this analysis. Includes the raw price series, "
        "simple returns, forward-return horizons, and diagnostic curves "
        "(drawdown, equity curve)."
    )

    tgt_df = _derivatives_to_dataframe(target_axis.get("derivatives", []))
    st.dataframe(tgt_df, use_container_width=True, hide_index=True)

    tgt_n = len(tgt_df)
    st.caption(
        f"Takeaway: {tgt_n} target-axis derivative{'s' if tgt_n != 1 else ''} "
        "disclosed. All derived from the single canonical column "
        f"`{tgt_canonical}` (ECON-SD scope discipline)."
    )
