"""Structured winner fields for pair-config prose (Phase B, winner_summary.json schema 1.3.0).

Pair configs never type a result by hand. They read the producer's `winner_fields` block:

    from components.winner_fields import load
    W = load("<pair_id>")
    HEADLINE_H2 = f"## Out-of-sample Sharpe {W.oos_sharpe} versus {W.bh_oos_sharpe} for buy-and-hold"

`W.<name>` is the display text of a field; `W.value("<name>")` is its raw value. A missing field renders as
"[missing: <name>]" so the page stays up and scripts/gate_structured_prose.py fails on it.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_RESULTS = Path(__file__).resolve().parents[2] / "results"


class FieldText(str):
    """A field's display text. Behaves as the plain string (lookups, comparisons); when formatted into prose
    under the number-provenance gate it carries a source sentinel (components.provenance)."""

    def __new__(cls, text: str, name: str):
        o = str.__new__(cls, text)
        o.field = name
        return o

    def __format__(self, spec):
        from components.provenance import _tag as tag
        return tag(str.__format__(str.__str__(self), spec), f"wf:{self.field}")

    def __str__(self):
        from components.provenance import _tag as tag
        return tag(str.__str__(self), f"wf:{self.field}")


class WinnerFields:
    def __init__(self, pair_id: str, fields: dict):
        self._pair_id = pair_id
        self._fields = fields

    def __getattr__(self, name: str) -> str:
        if name.startswith("_"):
            raise AttributeError(name)
        f = self._fields.get(name)
        return FieldText(f["text"], name) if f else f"[missing: {name}]"

    def value(self, name: str):
        f = self._fields.get(name)
        return None if f is None else f["value"]

    def has(self, name: str) -> bool:
        return name in self._fields

    def names(self) -> list[str]:
        return sorted(self._fields)


@lru_cache(maxsize=None)
def load(pair_id: str) -> WinnerFields:
    path = _RESULTS / pair_id / "winner_summary.json"
    try:
        ws = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        ws = {}
    return WinnerFields(pair_id, ws.get("winner_fields") or {})


@lru_cache(maxsize=None)
def lead_grid(pair_id: str) -> list[int]:
    """The pair's declared lead grid (docs/schemas/lead_axis_registry.json), for prose that names the grid."""
    reg = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "lead_axis_registry.json"
    try:
        return list(json.loads(reg.read_text())["pairs"][pair_id]["lead_grid"])
    except (OSError, KeyError, json.JSONDecodeError):
        return []
