"""Narrative provenance record: results/<pair>/evidence_facts_<tag>.json.

The pages may show a number only when it resolves to the pair's artifacts (scripts/gate_number_provenance.py).
Besides winner_summary / track_summary / the candidates manifest, those artifacts are:
  - "sources": the small evidence tables the narrative cites (Granger by lag, quartile returns, local
    projections, ...), listed by path relative to results/<pair>/. Each must exist and have at most MAX_ROWS
    rows, so the provenance pool stays small (large tables such as tournament results are never sources;
    a fact taken from them is written as a derived fact instead);
  - "derived": facts the pipeline computes for the narrative (a regime Sharpe, a share of windows, ...),
    written by the pipeline, read by the config.
write_evidence_facts merges into the file, keeping keys other stages wrote (hy_ig's market-history facts).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
MAX_ROWS = 200


def evidence_path(pair: str, tag: str) -> Path:
    return REPO / "results" / pair / f"evidence_facts_{tag}.json"


def write_evidence_facts(pair: str, tag: str, sources: list[str] | None = None, derived: dict | None = None) -> Path:
    rdir = REPO / "results" / pair
    for s in sources or []:
        f = rdir / s
        if not f.exists():
            raise FileNotFoundError(f"evidence source {f} does not exist")
        if f.suffix == ".csv" and len(pd.read_csv(f)) > MAX_ROWS:
            raise ValueError(f"evidence source {s} has more than {MAX_ROWS} rows; cite a derived fact instead")
    p = evidence_path(pair, tag)
    out = json.loads(p.read_text()) if p.exists() else {"pair_id": pair, "date_tag": tag}
    if sources is not None:
        out["sources"] = sorted(set(sources))
    if derived is not None:
        out["derived"] = {**out.get("derived", {}), **derived}
    p.write_text(json.dumps(out, indent=2, default=float) + "\n")
    return p
