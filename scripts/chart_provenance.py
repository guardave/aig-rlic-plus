"""Chart provenance (number-provenance gate v5, Lead ruling on QA L2v4 #1).

A chart file shows numbers its producer computed. Rather than value-match those numbers (QA measured 61-89%
coincidence for chart text), every chart file a schema-1.3 pair page loads must carry a provenance record, and
the gate checks that record against the artifacts on disk:

    output/charts/<pair>/chart_provenance.json
    {"<chart_name>": {"chart_sha256": ..., "results_tag": "20261017", "producer": "scripts/...",
                      "recorded_at": ..., "inputs": {"results/<pair>/x.csv": "<sha256>", "data/y.parquet": ...}}}

``record()`` is called by a producer's save function right after it writes the chart JSON. Its inputs are the
sources the producer declares PLUS every file under data/ or results/ the producer process has read so far
(captured by an audit hook on open() and a pandas.read_parquet shim). Reads a script made BEFORE the hook was
installed cannot be recovered, so the hook is installed at the process entry point (Codex V52-1: a static check of
import order was bypassable by aliasing a reader): when a repo script (scripts/...) imports this module in a
process that was not started through scripts/_cp_boot.py, the process re-executes itself through it, and the
boot module installs the hook before any of the script's code runs. Whatever the first process read is discarded
with it; the script then runs again from its first line under the hook.

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

BOOT = Path(__file__).resolve().with_name("_cp_boot.py")
BOOT_TOKEN = "entry-point:scripts/_cp_boot.py"   # a record made with the hook installed before the script ran


def _boot() -> None:
    """Re-execute a repo script through the boot module unless this process already started there. Skipped for
    non-script processes (pytest, streamlit, python -c, multiprocessing children, whose main is '__mp_main__')."""
    if getattr(sys, "_aig_cp_booted", False):
        return
    main = sys.modules.get("__main__")
    f = getattr(main, "__file__", None)
    if not f or getattr(main, "__name__", "") != "__main__":
        return
    try:
        p = Path(f).resolve()
        p.relative_to(REPO / "scripts")
    except (ValueError, OSError):
        return
    spec = getattr(main, "__spec__", None)
    target = ["-m", spec.name] if spec is not None and spec.name else [str(p)]
    sys.stdout.flush(); sys.stderr.flush()
    os.execv(sys.executable, [sys.executable, str(BOOT), *target, *sys.argv[1:]])


_boot()


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
    declared = set()
    for src in sources:                     # a declared input must exist (Codex V51-3: missing ones were dropped)
        f = REPO / src if not Path(src).is_absolute() else Path(src)
        if not f.is_file():
            raise ValueError(f"chart_provenance: declared input {src} of {chart_json.name} does not exist")
        r = _rel(f)
        if r:
            declared.add(r)
    # reads of OTHER pairs' results (a producer looping over several pairs in one process) are not this chart's
    # inputs; declared sources are always kept
    own = {r for r in _READS if r.startswith(("data/", f"results/{pair}/"))}
    inputs = sorted((declared | own) - {_rel(chart_json)})
    inputs = [p for p in inputs if (REPO / p).is_file()]
    if not inputs:
        raise ValueError(f"chart_provenance: {chart_json.name} has no inputs under data/ or results/")
    entry = {"chart_sha256": sha256(chart_json), "results_tag": results_tag(pair),
             "producer": producer or Path(sys.argv[0]).as_posix(),
             "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "recorder": BOOT_TOKEN if getattr(sys, "_aig_cp_booted", False) else "not-booted",
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


def _ignored(rel: str) -> bool:
    import subprocess
    try:
        return subprocess.run(["git", "check-ignore", "-q", rel], cwd=REPO).returncode == 0
    except OSError:
        return False


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
    if e.get("recorder") != BOOT_TOKEN:        # Codex V52-1: inputs are complete only under the entry-point hook
        return (f"chart {chart.stem} was not recorded under the producer bootstrap (scripts/_cp_boot.py); "
                "regenerate it by running its producer script")
    if not chart.is_file() or sha256(chart) != e.get("chart_sha256"):
        return f"chart {chart.stem} changed after its provenance was recorded"
    tag = results_tag(pair)
    if tag and e.get("results_tag") != tag:
        return f"chart {chart.stem} was built for run {e.get('results_tag')}, current run is {tag}"
    if not e.get("inputs"):
        return f"chart {chart.stem} records no inputs"
    absent = [p for p in e["inputs"] if not (REPO / p).is_file()]
    if absent:                     # QA pilot-visual M6: say what is missing and how to get it, not "stale"
        return (f"chart {chart.stem}: input(s) not present in this checkout: {', '.join(absent[:4])} - "
                f"{'gitignored data: ' if any(_ignored(p) for p in absent) else ''}rebuild with "
                f"python scripts/pair_pipeline_{pair}.py (or track the file)")
    stale = [p for p, h in e["inputs"].items() if sha256(REPO / p) != h]
    if stale:
        return f"chart {chart.stem} is stale: input(s) changed since it was built: {', '.join(stale[:4])}"
    return None
