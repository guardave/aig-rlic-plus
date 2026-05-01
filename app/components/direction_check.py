"""Direction triangulation — APP-DIR1.

Cross-checks that every upstream agent agrees on the empirical direction
between a pair's indicator and target. Without this, a direction change by
Evan can ship to production while Dana's metadata and Ray's narrative
silently disagree — exactly the class of bug META-IA (Interpretation
Annotation Handoffs) was written to prevent but had no mechanized gate for.

**Scope (Wave 10I.C):** 3-way triangulation (Evan ↔ Dana ↔ Ray). Ray's leg
reads ``direction_asserted`` from the narrative frontmatter block in
``docs/portal_narrative_{pair_id}_*.md`` (RES-17 migration complete).

Rules cited:

- **APP-DIR1** (`docs/agent-sops/appdev-agent-sop.md`) — direction
  triangulation at page load; mismatch = APP-SEV1 L1 hard error.
- **APP-SEV1** — loud-error on mismatch (no silent reconciliation).
- **META-IA** (`docs/agent-sops/team-coordination.md`) — 4-agent
  interpretation-annotation protocol.
- **ECON-H5** — `winner_summary.direction` canonical enum.
- **DATA-D6** — `interpretation_metadata.observed_direction` canonical enum.
- **RES-17** — narrative frontmatter contract; Ray owns ``direction_asserted``.
"""

from __future__ import annotations

import glob
from pathlib import Path

import streamlit as st

from components.schema_check import SchemaValidationError, validate_or_die


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_ray_direction(pair_id: str) -> tuple[str | None, str | None]:
    """Read Ray's ``direction_asserted`` from the narrative frontmatter.

    Finds the most-recent ``docs/portal_narrative_{pair_id}_*.md`` file
    (by filename sort, which is date-ordered) and extracts the YAML
    frontmatter block between the opening and closing ``---`` delimiters.

    Returns:
        (direction, note) where direction is the canonical string or None,
        and note is a diagnostic message explaining any gap.
    """
    docs_dir = _REPO_ROOT / "docs"
    pattern = str(docs_dir / f"portal_narrative_{pair_id}_*.md")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return None, (
            f"Ray leg missing — no docs/portal_narrative_{pair_id}_*.md found. "
            "Ray must create a narrative frontmatter file (RES-17)."
        )

    latest = matches[-1]
    try:
        content = Path(latest).read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"Ray leg read error ({exc})"

    if not content.startswith("---"):
        return None, (
            f"Ray leg malformed — {Path(latest).name} has no YAML frontmatter "
            "opening delimiter. RES-17 requires frontmatter starting with '---'."
        )

    try:
        end_idx = content.index("---", 3)
    except ValueError:
        return None, (
            f"Ray leg malformed — {Path(latest).name} YAML frontmatter "
            "has no closing '---' delimiter."
        )

    try:
        import yaml  # type: ignore[import]
        fm = yaml.safe_load(content[3:end_idx])
    except Exception as exc:  # noqa: BLE001
        return None, f"Ray leg YAML parse error in {Path(latest).name}: {exc}"

    direction = fm.get("direction_asserted") if isinstance(fm, dict) else None
    if direction is None:
        return None, (
            f"Ray leg incomplete — {Path(latest).name} frontmatter lacks "
            "'direction_asserted'. RES-17 requires this field."
        )

    return direction, None


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


def _plain_direction_label(direction: str | None) -> str:
    """Return a reader-friendly label for the canonical direction enum."""
    labels = {
        "countercyclical": "counter-cyclical",
        "procyclical": "pro-cyclical",
        "mixed": "mixed",
    }
    return labels.get(direction or "", "unknown")


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

    # ---- Ray leg: narrative_frontmatter.direction_asserted (RES-17) ----
    ray_direction, ray_note = _load_ray_direction(pair_id)
    report["ray"] = _canonicalize(ray_direction)
    if ray_note:
        report["notes"].append(ray_note)

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

    # ---- Check Ray leg disagreement (non-blocking warning per RES-17 launch) ----
    ray = report["ray"]
    if ray is not None and ray != evan:
        st.warning(
            f"**Direction partial mismatch** (APP-DIR1, 3-way). "
            f"Evan/Dana agree on `{evan}` but Ray's narrative frontmatter "
            f"asserts `{ray}` (from `docs/portal_narrative_{pair_id}_*.md`). "
            "Ray must update `direction_asserted` to match. Escalate to Lead.\n\n"
            "Plain English: the narrative's stated direction does not match "
            "what the model found empirically — the portal story may mislead "
            "readers. The page renders but Ray must reconcile before acceptance."
        )

    # Valid agreement (2-way Evan ↔ Dana, with Ray cross-check above).
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
        ray = report.get("ray")
        direction_label = _plain_direction_label(report.get("evan"))
        if ray is not None:
            st.caption(
                "What this shows: direction check — the model record, "
                "metadata record, and story record all agree this signal is "
                f"{direction_label}."
            )
        else:
            st.caption(
                "What this shows: direction check — two independent project "
                f"records agree this signal is {direction_label}. The optional "
                "story cross-check has not been added yet."
            )
    return report
