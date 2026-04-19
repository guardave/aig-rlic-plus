"""Direction triangulation — APP-DIR1.

Cross-checks that every upstream agent agrees on the empirical direction
between a pair's indicator and target. Without this, a direction change by
Evan can ship to production while Dana's metadata and Ray's narrative
silently disagree — exactly the class of bug META-IA (Interpretation
Annotation Handoffs) was written to prevent but had no mechanized gate for.

**Scope (Wave 4D-2):** 2-way triangulation (Evan ↔ Dana). The 3rd leg —
Ray's ``narrative_frontmatter.direction_asserted`` — is flagged as TODO and
will be added once RES-17 narrative-frontmatter migration lands.

Rules cited:

- **APP-DIR1** (`docs/agent-sops/appdev-agent-sop.md`) — direction
  triangulation at page load; mismatch = APP-SEV1 L1 hard error.
- **APP-SEV1** — loud-error on mismatch (no silent reconciliation).
- **META-IA** (`docs/agent-sops/team-coordination.md`) — 4-agent
  interpretation-annotation protocol.
- **ECON-H5** — `winner_summary.direction` canonical enum.
- **DATA-D6** — `interpretation_metadata.observed_direction` canonical enum.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.schema_check import SchemaValidationError, validate_or_die


_REPO_ROOT = Path(__file__).resolve().parents[2]


# Schema enum for direction (winner_summary v1.0.0, interpretation_metadata
# v1.0.0). `counter_cyclical` is a legacy spelling seen in some pre-4D-1 code;
# the schema now mandates `countercyclical` (no underscore).
_CANONICAL_DIRECTIONS = {"procyclical", "countercyclical", "mixed"}


def _canonicalize(direction: str | None) -> str | None:
    """Fold legacy `counter_cyclical` → `countercyclical` for comparison."""
    if direction is None:
        return None
    if direction == "counter_cyclical":
        return "countercyclical"
    if direction == "pro_cyclical":
        return "procyclical"
    return direction


def check_direction_agreement(pair_id: str) -> dict:
    """Validate 3-way direction agreement (Evan ↔ Dana ↔ Ray) for a pair.

    Reads ``winner_summary.direction`` (Evan) and
    ``interpretation_metadata.observed_direction`` (Dana) via schema-validated
    loads; compares. On mismatch, renders ``st.error(...)`` per APP-SEV1 L1
    and sets ``agreement=False`` in the returned report.

    **Ray leg (narrative_frontmatter.direction_asserted):** not yet migrated
    (RES-17 pending). Ray's leg is skipped with a TODO marker; once the
    frontmatter lands, add the third read + assertion here.

    Args:
        pair_id: Pair identifier (e.g. ``hy_ig_v2_spy``).

    Returns:
        A dict with keys:
          - ``agreement`` (bool) — True iff Evan's and Dana's directions agree.
          - ``evan`` (str | None) — winner_summary.direction (canonical).
          - ``dana`` (str | None) — interpretation_metadata.observed_direction.
          - ``ray`` — always None until RES-17 migration lands.
          - ``notes`` (list[str]) — diagnostic notes (e.g. "ray leg pending").
          - ``schema_errors`` (list[str]) — non-empty if a schema read failed.

    Side effects:
        Renders ``st.error(...)`` if the two available legs disagree
        (APP-SEV1 L1). Does NOT raise — the caller decides whether to
        short-circuit the page (currently Lead policy: mismatch is a loud
        error on the page but does not block other page sections from
        rendering — it's a visibility-first signal until 3-way is active).
    """
    pair_dir = _REPO_ROOT / "results" / pair_id
    report: dict = {
        "agreement": False,
        "evan": None,
        "dana": None,
        "ray": None,
        "notes": [],
        "schema_errors": [],
    }

    # ---- Evan leg: winner_summary.direction ----
    try:
        winner = validate_or_die(pair_dir / "winner_summary.json", "winner_summary")
        report["evan"] = _canonicalize(winner.get("direction"))
    except SchemaValidationError as exc:
        report["schema_errors"].append(f"winner_summary: {exc.errors}")
        # Without Evan's leg, triangulation is impossible. validate_or_die
        # already rendered st.error; just return the report.
        return report

    # ---- Dana leg: interpretation_metadata.observed_direction ----
    try:
        meta = validate_or_die(
            pair_dir / "interpretation_metadata.json", "interpretation_metadata"
        )
        # observed_direction is optional in the schema but must be the
        # canonical enum if present. For this pair family (post-Wave-4D-1)
        # Dana populates it; absence is itself a contract gap.
        observed = meta.get("observed_direction")
        if observed is None:
            report["notes"].append(
                "interpretation_metadata.observed_direction missing — Dana leg unknown"
            )
        report["dana"] = _canonicalize(observed)
    except SchemaValidationError as exc:
        report["schema_errors"].append(f"interpretation_metadata: {exc.errors}")
        return report

    # ---- Ray leg: narrative_frontmatter.direction_asserted (TODO) ----
    # TODO(Ace, post-RES-17): once the narrative markdown files carry a
    # schema-validated frontmatter (`docs/schemas/narrative_frontmatter.schema.json`),
    # read `direction_asserted` here and include in the 3-way assertion.
    # Until then, Ray's leg is None and APP-DIR1 is a 2-way check.
    report["notes"].append(
        "Ray leg (narrative_frontmatter.direction_asserted) skipped — "
        "RES-17 narrative-frontmatter migration pending."
    )

    # ---- Assert agreement between available legs ----
    evan = report["evan"]
    dana = report["dana"]
    if evan is None or dana is None:
        # One leg missing — cannot triangulate. Raise a loud warning, not
        # an error (agreement check is moot until both legs exist).
        st.warning(
            "**Direction triangulation incomplete** (APP-DIR1). "
            f"Evan (winner_summary.direction) = `{evan}`; "
            f"Dana (observed_direction) = `{dana}`. "
            "At least one leg missing — cannot assert agreement.\n\n"
            "Plain English: before showing you a trading rule, we "
            "cross-check that our econometrician and our data analyst "
            "agree on whether the indicator moves with the market "
            "(pro-cyclical) or against it (counter-cyclical). One of "
            "those two opinions is missing, so we cannot yet confirm "
            "agreement — results may still be right, but they are "
            "unchecked."
        )
        return report

    if evan != dana:
        st.error(
            f"**Direction disagreement detected** (APP-DIR1, APP-SEV1 L1). "
            f"Evan says `{evan}` in `winner_summary.json.direction`; "
            f"Dana says `{dana}` in "
            f"`interpretation_metadata.json.observed_direction`. "
            f"These must match. Escalate to Lead for reconciliation per META-IA."
            "\n\nPlain English: our econometrician and our data analyst "
            "disagree on whether this indicator moves with the market or "
            "against it. That is a serious inconsistency — trading-rule "
            "direction is not a matter of opinion. The page is allowed "
            "to render, but do not act on the results until the "
            "disagreement is resolved."
        )
        return report

    # Valid 2-way agreement (Ray leg pending until RES-17).
    if evan in _CANONICAL_DIRECTIONS:
        report["agreement"] = True
    else:
        st.warning(
            f"Direction value `{evan}` is not in the canonical schema enum "
            f"{sorted(_CANONICAL_DIRECTIONS)}. Agreement reported, but value "
            f"violates schema vocabulary — escalate to Lead.\n\n"
            "Plain English: the direction label does not match the "
            "controlled vocabulary we have pinned in the schema. The "
            "two sources agree with each other, but they are using a "
            "variant spelling we do not recognise — a Lead review is "
            "needed before acting."
        )

    return report


def render_direction_check(pair_id: str) -> dict:
    """Thin wrapper — renders a success caption on clean agreement.

    Use at the top of each pair page (Story / Evidence / Strategy / Methodology)
    as the mechanical APP-DIR1 hook. Returns the same report as
    `check_direction_agreement` so callers can gate downstream rendering.
    """
    report = check_direction_agreement(pair_id)
    if report["agreement"]:
        st.caption(
            f"What this shows: direction triangulation (APP-DIR1, 2-way) "
            f"— Evan and Dana agree on `{report['evan']}`. Ray leg "
            f"pending RES-17 frontmatter migration."
        )
    return report
