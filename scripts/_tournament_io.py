#!/usr/bin/env python3
"""Tournament CSV immutability guard (ECON-T5 §4).

A published `tournament_results_*.csv` is the FROZEN, publish-time record of the
grid a winner was selected over. It must never be appended to, overwritten, or
otherwise mutated in place. Any grid expansion (more leads / signals / thresholds)
is a NEW tournament and MUST be written to a NEW date-stamped file.

This module centralises the two safe operations so every producer/consumer uses
the same enforced contract:

  * ``read_tournament(path)``  — open a published CSV READ-ONLY. Returns a
    DataFrame. Never writes. (Thin wrapper over ``pd.read_csv`` that documents
    intent and is the single import point auditors can grep for.)

  * ``write_tournament(df, path, *, allow_overwrite=False)`` — write a NEW
    tournament CSV. Raises ``TournamentImmutabilityError`` if ``path`` already
    exists, unless ``allow_overwrite=True`` is passed EXPLICITLY (reserved for
    the rare intentional in-place regeneration of a same-grid file, e.g. a
    benchmark-validity flag flip, and even then the caller must justify it).
    Grid expansion must instead pass a fresh date-stamped ``path``.

Root cause this guards against (2026-06-20 indpro_spy provenance investigation):
a downstream regen reused the committed publish-time date tag and overwrote/
appended L0..12 rows into `tournament_results_20260314.csv` in place, making the
original L6 winner appear to lose to an unselected L4 row. Auditability — not a
wrong number — was the defect. See ECON-T5 in docs/agent-sops/econometrics-agent-sop.md.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd

_TOURNAMENT_RE = re.compile(r"tournament_results_.*\.csv$")


class TournamentImmutabilityError(RuntimeError):
    """Raised when a publish-time tournament CSV would be mutated in place."""


def is_tournament_path(path) -> bool:
    return bool(_TOURNAMENT_RE.search(str(path)))


def read_tournament(path) -> pd.DataFrame:
    """Open a published tournament CSV READ-ONLY (ECON-T5 §4).

    This function performs NO writes. It exists so producers/consumers have one
    auditable, grep-able read entry point and never reach for a read-then-rewrite
    pattern on the same handle.
    """
    return pd.read_csv(path)


def file_sha256(path) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_tournament(df: pd.DataFrame, path, *, allow_overwrite: bool = False,
                     index: bool = False) -> None:
    """Write a NEW tournament CSV. Refuses to overwrite an existing one.

    Grid expansion is a re-run, not a backfill: write to a NEW date-stamped path.
    `allow_overwrite=True` is an explicit, narrowly-scoped escape hatch for an
    intentional same-grid regeneration of a non-published or to-be-replaced file;
    it MUST be justified by the caller and never used to expand a grid.
    """
    p = Path(path)
    if p.exists() and not allow_overwrite:
        raise TournamentImmutabilityError(
            f"Refusing to overwrite existing tournament CSV in place: {p}\n"
            f"Published tournament_results_*.csv files are FROZEN at publish time "
            f"(ECON-T5 §4). A grid expansion is a NEW tournament — write to a NEW "
            f"date-stamped file (e.g. tournament_results_<today>.csv). If you truly "
            f"intend a same-grid in-place rewrite, pass allow_overwrite=True and "
            f"document why."
        )
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=index)
