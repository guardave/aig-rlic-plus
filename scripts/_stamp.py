"""Canonical UTC timestamp helper (DUP-15 consolidation).

Before fix260531 the same `datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")`
pattern was duplicated 22+ times across pipelines, generators, and chart
scripts. `datetime.utcnow()` is deprecated in Python 3.12 and emits a
DeprecationWarning. Some code had already migrated to the timezone-aware
`datetime.now(timezone.utc)` — but inconsistently.

This module centralises the convention. Every place that emits a "generated
at" / "last_updated_at" stamp should import ``iso_utc_now()`` instead of
calling ``datetime`` directly.

Usage:

    from scripts._stamp import iso_utc_now
    meta["generated_at"] = iso_utc_now()           # "2026-05-31T14:30:45Z"
    meta["generated_date"] = iso_utc_now(date_only=True)   # "2026-05-31"
"""

from __future__ import annotations

from datetime import datetime, timezone

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT = "%Y-%m-%d"


def iso_utc_now(*, date_only: bool = False) -> str:
    """Return the current UTC time as an ISO 8601 string.

    The standard form is ``YYYY-MM-DDTHH:MM:SSZ`` (seconds, ``Z`` for UTC).
    Pass ``date_only=True`` for the date-only form ``YYYY-MM-DD``.
    """
    now = datetime.now(timezone.utc)
    return now.strftime(DATE_FORMAT if date_only else ISO_FORMAT)


__all__ = ("iso_utc_now", "ISO_FORMAT", "DATE_FORMAT")
