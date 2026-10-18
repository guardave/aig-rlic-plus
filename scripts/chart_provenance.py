"""Chart provenance (number-provenance gate v5, Lead ruling on QA L2v4 #1).

A chart file shows numbers its producer computed. Rather than value-match those numbers (QA measured 61-89%
coincidence for chart text), every chart file a schema-1.3 pair page loads must carry a provenance record, and
the gate checks that record against the artifacts on disk:

    output/charts/<pair>/chart_provenance.json
    {"<chart_name>": {"chart_sha256": ..., "results_tag": "20261017", "producer": "scripts/...",
                      "recorded_at": ..., "inputs": {"results/<pair>/x.csv": "<sha256>", "data/y.parquet": ...}}}

``record()`` is called by a producer's save function right after it writes the chart JSON. Its inputs are the
sources the producer declares PLUS every file under data/ or results/ the producer process has read so far
(captured by an audit hook on open() and a pandas.read_parquet shim, both installed when this module is
imported). Importing this module before reading any data is therefore what makes the record complete: producers
import it at the top.

``verify()`` (used by scripts/gate_number_provenance.py) fails a chart when it has no record, when the chart file
changed after it was recorded, when the pair's results run tag moved on, or when any recorded input is missing or
has different content. That is the class of the five stale hy_ig_spy cross-period charts (built from the previous
winner's CSVs and never regenerated).

Disclosed limits: a record proves which inputs a producer read, not that its code used them correctly (producer
code is reviewed code, like the shared templates); reads done by native code other than pandas.read_parquet are
captured only when declared as sources.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_ROOTS = ("data/", "results/")
_READS: set[str] = set()


def _rel(path) -> str | None:
    try:
        p = Path(os.fsdecode(path))
        if not p.is_absolute():
            p = Path.cwd() / p
        r = p.resolve().relative_to(REPO).as_posix()
    except (TypeError, ValueError, OSError):
        return None
    return r if r.startswith(_ROOTS) else None


def _audit(event: str, args) -> None:
    if event != "open" or not args:
        return
    path, mode = args[0], args[1] if len(args) > 1 else "r"
    if not isinstance(path, (str, bytes, os.PathLike)) or (isinstance(mode, str) and any(c in mode for c in "wax+")):
        return
    r = _rel(path)
    if r:
        _READS.add(r)


def _install() -> None:
    if getattr(sys, "_aig_chart_provenance_hook", False):
        return
    sys.addaudithook(_audit)
    sys._aig_chart_provenance_hook = True
    try:                                            # pyarrow opens parquet files natively (no audit event)
        import pandas as pd
        if not getattr(pd.read_parquet, "_aig_wrapped", False):
            _orig = pd.read_parquet

            def read_parquet(path, *a, **k):
                r = _rel(path) if isinstance(path, (str, os.PathLike)) else None
                if r:
                    _READS.add(r)
                return _orig(path, *a, **k)
            read_parquet._aig_wrapped = True
            pd.read_parquet = read_parquet
    except ImportError:                             # pragma: no cover
        pass


_install()


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def results_tag(pair: str) -> str | None:
    """The pair's current run tag (the tournament file the published winner came from), None without one."""
    try:
        ws = json.loads((REPO / "results" / pair / "winner_summary.json").read_text())
        return ws["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
    except (OSError, KeyError, ValueError, AttributeError):
        return None


def manifest_path(pair: str) -> Path:
    return REPO / "output" / "charts" / pair / "chart_provenance.json"


def record(pair: str, chart_json, sources=(), producer: str | None = None) -> dict:
    """Record the provenance of a chart JSON just written for ``pair``. ``sources``: paths the producer declares
    (repo-relative or absolute); files read so far by this process under data/ or results/ are added."""
    chart_json = Path(chart_json)
    declared = {r for r in (_rel(REPO / s if not Path(s).is_absolute() else s) for s in sources) if r}
    inputs = sorted((declared | _READS) - {_rel(chart_json)})
    inputs = [p for p in inputs if (REPO / p).is_file()]
    if not inputs:
        raise ValueError(f"chart_provenance: {chart_json.name} has no inputs under data/ or results/")
    entry = {"chart_sha256": sha256(chart_json), "results_tag": results_tag(pair),
             "producer": producer or Path(sys.argv[0]).as_posix(),
             "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "inputs": {p: sha256(REPO / p) for p in inputs}}
    mp = manifest_path(pair)
    try:
        man = json.loads(mp.read_text())
    except (OSError, ValueError):
        man = {}
    man[chart_json.stem] = entry
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(dict(sorted(man.items())), indent=1) + "\n")
    return entry


def verify(pair: str, chart_rel: str) -> str | None:
    """None when the chart file at repo-relative ``chart_rel`` matches its provenance record, else the reason."""
    chart = REPO / chart_rel
    try:
        man = json.loads(manifest_path(pair).read_text())
    except (OSError, ValueError):
        return f"chart {chart.stem} has no provenance record (no output/charts/{pair}/chart_provenance.json)"
    e = man.get(chart.stem)
    if not e:
        return f"chart {chart.stem} has no provenance record (regenerate it with a recording producer)"
    if not chart.is_file() or sha256(chart) != e.get("chart_sha256"):
        return f"chart {chart.stem} changed after its provenance was recorded"
    tag = results_tag(pair)
    if tag and e.get("results_tag") != tag:
        return f"chart {chart.stem} was built for run {e.get('results_tag')}, current run is {tag}"
    stale = [p for p, h in (e.get("inputs") or {}).items() if not (REPO / p).is_file() or sha256(REPO / p) != h]
    if not e.get("inputs"):
        return f"chart {chart.stem} records no inputs"
    if stale:
        return f"chart {chart.stem} is stale: input(s) changed since it was built: {', '.join(stale[:4])}"
    return None
