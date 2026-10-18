"""Process entry point for chart producers (Codex V52-1): installs the chart-provenance read recorder before any
of the script's code runs, then runs the script as __main__.

    python scripts/_cp_boot.py scripts/generate_charts_x.py [args]     (or: _cp_boot.py -m package.module [args])

A repo script that imports chart_provenance without having started here re-executes itself through this module
(chart_provenance._boot), so producers need not be invoked through it by hand.
"""
import runpy
import sys
from pathlib import Path

sys._aig_cp_booted = True                     # set before the import below, so chart_provenance does not re-exec
sys.path.insert(0, str(Path(__file__).resolve().parent))
import chart_provenance  # noqa: E402,F401  (installs the audit hook / read_parquet shim now)

if len(sys.argv) < 2:
    raise SystemExit(__doc__)
if sys.argv[1] == "-m":
    mod = sys.argv[2]
    sys.argv = [mod, *sys.argv[3:]]
    runpy.run_module(mod, run_name="__main__", alter_sys=True)
else:
    script = str(Path(sys.argv[1]).resolve())
    sys.argv = [script, *sys.argv[2:]]
    sys.path[0] = str(Path(script).parent)
    runpy.run_path(script, run_name="__main__")
