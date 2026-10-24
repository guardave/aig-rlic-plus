"""No pipeline, chart producer or harness module reads a name the module never binds (hy_ig 74028730: removing the
old trade-log block deleted sig_l but left two uses; stage 9 raised NameError after the null stage had run)."""
import builtins
import symtable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FILES = sorted([*ROOT.glob("scripts/pair_pipeline_*.py"), *ROOT.glob("scripts/generate_charts_*.py"),
                *ROOT.glob("scripts/harness/*.py"), ROOT / "scripts/r71_calibrate.py", ROOT / "scripts/null_is_windows.py"])


def undefined_globals(src: str, name: str = "<src>") -> list[tuple[str, str]]:
    """(scope, name) for each name a function reads as an implicit global that the module never binds."""
    top = symtable.symtable(src, name, "exec")
    bound = {s.get_name() for s in top.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()}
    bound |= set(dir(builtins)) | {"__file__", "__name__", "__doc__"}
    out = []

    def walk(t, where):
        for s in t.get_symbols():
            if s.is_referenced() and s.is_global() and not s.is_declared_global() and s.get_name() not in bound:
                out.append((where, s.get_name()))
        for c in t.get_children():
            walk(c, f"{where}.{c.get_name()}")

    for c in top.get_children():
        walk(c, c.get_name())
    return out


def test_checker_catches_a_dangling_name():
    src = "import pandas as pd\n\ndef stage(work):\n    lagged = work.shift(1)\n    return sig_l.shift(1)\n"
    assert undefined_globals(src) == [("stage", "sig_l")]


def test_checker_accepts_module_bindings():
    src = "from x import y\nZ = 1\n\ndef f():\n    return y, Z, len, f\n"
    assert undefined_globals(src) == []


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_no_undefined_globals(path):
    assert undefined_globals(path.read_text(), str(path)) == []
