"""Provenance tagging of artifact values for page prose (structured-prose layer 2 v2).

Pair configs read every number they print through this module (and through components.winner_fields). In normal
use nothing changes: values behave like plain numbers and strings. When the number-provenance gate renders a page
(environment AIG_PROVENANCE_GATE=1), every artifact value that is formatted into text carries an invisible
sentinel naming its source:

    \\ue000<source expression>\\ue001<displayed text>\\ue002

and the gate (scripts/gate_number_provenance.py) fails on any number in the pair's authored text that is not
inside a sentinel (or a justified allowlist span), and re-evaluates every sentinel's source expression against
the artifacts to check the displayed text.

Source expressions:
    art:<results-relative path>#<key path>      a value in a JSON (a/b/0/c) or CSV (r<row>/<column>) artifact
    wf:<field>                                  a winner_fields entry (its display text)
    mul(a,b) div(a,b) add(a,b) sub(a,b) neg(a) abs(a) const:<number>
    len(<container source>)  count(<csv source>,<column>,<op>,<number or column>)
    min(<csv source>,<column>)  max(<csv source>,<column>)
Arithmetic on tagged numbers (x * 100, a - b) keeps a tag (it can be re-evaluated); a number computed any other
way loses it, so it must come from the pipeline as an artifact (evidence_facts 'derived') instead.
Definitions (threshold / signal descriptions of the declared search space) are wrapped with definitions():
their text is marked as definition text, which the gate exempts like layer 1 does by path.
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

import pandas as pd



def gate_on() -> bool:
    """Read at format time, so the gate can switch tagging on for one in-process render."""
    return os.environ.get("AIG_PROVENANCE_GATE") == "1"


S0, S1, S2 = "", "", ""          # value sentinel: open, source / text separator, close
D0, D1 = "", ""                        # definition text
A0, A1 = "", ""                        # authored config text (added by the gate)
RESULTS = Path(__file__).resolve().parents[2] / "results"
REGISTRY = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "lead_axis_registry.json"
_ESC = {",": "%2C", "(": "%28", ")": "%29"}


def _esc(s: str) -> str:
    for k, v in _ESC.items():
        s = s.replace(k, v)
    return s


def tag(text, src: str) -> str:
    text = str(text)
    return f"{S0}{src}{S1}{text}{S2}" if gate_on() else text


# --------------------------------------------------------------------------------------------- tagged numbers
def _num(v, src):
    return PInt(v, src) if isinstance(v, int) and not isinstance(v, bool) else PNum(v, src)


def _src(x) -> str:
    return x.src if isinstance(x, (PNum, PInt)) else f"const:{x!r}"


class _Tagged:
    src: str

    def __format__(self, spec):
        return tag(self._base().__format__(spec), self.src)

    def __str__(self):
        return tag(self._base().__str__(), self.src)

    def __repr__(self):
        return self._base().__repr__()

    def __abs__(self):
        return _num(abs(self._base()), f"abs({self.src})")

    def __neg__(self):
        return _num(-self._base(), f"neg({self.src})")

    def __pos__(self):
        return self

    def __round__(self, nd=None):
        return _num(round(self._base(), nd), self.src) if nd is not None else PInt(round(self._base()), self.src)

    def _op(self, other, fn, name, rev=False):
        if not isinstance(other, (int, float)) or isinstance(other, bool):
            return NotImplemented
        a, b = (other, self) if rev else (self, other)
        return _num(fn(float(a), float(b)), f"{name}({_src(a)},{_src(b)})")

    def __mul__(self, o):
        return self._op(o, lambda a, b: a * b, "mul")

    def __rmul__(self, o):
        return self._op(o, lambda a, b: a * b, "mul", True)

    def __truediv__(self, o):
        return self._op(o, lambda a, b: a / b, "div")

    def __rtruediv__(self, o):
        return self._op(o, lambda a, b: a / b, "div", True)

    def __add__(self, o):
        return self._op(o, lambda a, b: a + b, "add")

    def __radd__(self, o):
        return self._op(o, lambda a, b: a + b, "add", True)

    def __sub__(self, o):
        return self._op(o, lambda a, b: a - b, "sub")

    def __rsub__(self, o):
        return self._op(o, lambda a, b: a - b, "sub", True)


class PNum(_Tagged, float):
    def __new__(cls, v, src: str):
        o = float.__new__(cls, v)
        o.src = src
        return o

    def _base(self):
        return float(self)

    __hash__ = float.__hash__


class PInt(_Tagged, int):
    def __new__(cls, v, src: str):
        o = int.__new__(cls, v)
        o.src = src
        return o

    def _base(self):
        return int(self)

    __hash__ = int.__hash__


# ------------------------------------------------------------------------------------------------- loaders
def _rel(path: Path) -> str:
    try:
        return _esc(str(Path(path).resolve().relative_to(RESULTS)))
    except ValueError:
        return _esc(str(path))


class PStr(str):
    """Artifact text that contains numbers (e.g. a diagnosis reading): tagged when formatted into prose."""

    def __new__(cls, text: str, src: str):
        o = str.__new__(cls, text)
        o.src = src
        return o

    def __format__(self, spec):
        return tag(str.__format__(str.__str__(self), spec), self.src)

    def __str__(self):
        return tag(str.__str__(self), self.src)


class PList(list):
    src: str


class PDict(dict):
    src: str


def _wrap(o, src: str):
    if isinstance(o, str):
        return PStr(o, src) if re.search(r"\d", o) else o
    if isinstance(o, bool) or o is None:
        return o
    if isinstance(o, (int, float)):
        return _num(o, src) if not (isinstance(o, float) and math.isnan(o)) else o
    if isinstance(o, dict):
        d = PDict({k: _wrap(v, f"{src}/{_esc(str(k))}") for k, v in o.items()})
        d.src = src
        return d
    if isinstance(o, list):
        lst = PList(_wrap(v, f"{src}/{i}") for i, v in enumerate(o))
        lst.src = src
        return lst
    return o


def json_file(path) -> dict:
    """A JSON artifact with every number tagged art:<path>#<key path>."""
    return _wrap(json.loads(Path(path).read_text()), f"art:{_rel(path)}#")


def csv_file(path, **kw) -> pd.DataFrame:
    """A CSV artifact whose numeric cells are tagged art:<path>#r<row>/<column> (object columns)."""
    df = pd.read_csv(path, **kw)
    src = f"art:{_rel(path)}#"
    for c in df.columns:
        if pd.api.types.is_bool_dtype(df[c]):
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = pd.Series([v if pd.isna(v) else _num(v.item() if hasattr(v, "item") else v,
                                                         f"{src}r{i}/{_esc(str(c))}")
                               for i, v in enumerate(df[c])], index=df.index, dtype=object)
        else:                                       # formatted text cells ("+0.0082**") stay tagged as text
            df[c] = pd.Series([PStr(v, f"{src}r{i}/{_esc(str(c))}") if isinstance(v, str) and re.search(r"\d", v)
                               else v for i, v in enumerate(df[c])], index=df.index, dtype=object)
    df.attrs["src"] = src
    return df


def col_dict(df: pd.DataFrame, key: str, col: str) -> dict:
    """{key value: tagged cell} of a loaded CSV (DataFrame.to_dict would unbox the tags to plain floats)."""
    return {(str.__str__(k) if isinstance(k, str) else k): v for k, v in zip(df[key].tolist(), df[col].tolist())}


def lead_grid(pair_id: str) -> list:
    """The pair's declared lead grid (docs/schemas/lead_axis_registry.json), each lead tagged reg:<pair>/..."""
    try:
        grid = json.loads(REGISTRY.read_text())["pairs"][pair_id]["lead_grid"]
    except (OSError, KeyError, json.JSONDecodeError):
        return []
    out = PList(PInt(v, f"reg:{_esc(pair_id)}/lead_grid/{i}") for i, v in enumerate(grid))
    out.src = f"reg:{_esc(pair_id)}/lead_grid"
    return out


# ------------------------------------------------------------------------------------------- derived values
def length(obj) -> PInt:
    """len() of a loaded JSON list / dict or a loaded CSV table, tagged."""
    src = obj.attrs["src"] if isinstance(obj, pd.DataFrame) else obj.src
    return PInt(len(obj), f"len({src})")


_OPS = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
        "!=": lambda a, b: a != b, "==": lambda a, b: a == b}


def count(df: pd.DataFrame, col: str, op: str, other) -> PInt:
    """Rows of a loaded CSV where `col <op> other` (a number or another column), tagged."""
    a = df[col].astype(float)
    b = df[other].astype(float) if isinstance(other, str) else float(other)
    n = int(_OPS[op](a, b).sum())
    return PInt(n, f"count({df.attrs['src']},{_esc(col)},{op},{_esc(str(other))})")


def colmin(df: pd.DataFrame, col: str) -> PNum:
    return PNum(float(df[col].astype(float).min()), f"min({df.attrs['src']},{_esc(col)})")


def colmax(df: pd.DataFrame, col: str) -> PNum:
    return PNum(float(df[col].astype(float).max()), f"max({df.attrs['src']},{_esc(col)})")


def colmaxabs(df: pd.DataFrame, col: str) -> PNum:
    return PNum(float(df[col].astype(float).abs().max()), f"maxabs({df.attrs['src']},{_esc(col)})")


def prefix(text: "PStr", n: int) -> "PStr | str":
    """The first n characters of tagged artifact text (e.g. the year of a date), still tagged."""
    return PStr(str.__str__(text)[:n], f"prefix({text.src},{n})") if isinstance(text, PStr) else text[:n]


def year(date_text: "PStr") -> "PStr | str":
    """The year of a tagged ISO date."""
    return prefix(date_text, 4)


# ------------------------------------------------------------------------------------------------ definitions
class DefText(str):
    """Definition text of the declared search space (threshold / signal descriptions)."""

    def __format__(self, spec):
        return f"{D0}{str.__format__(str.__str__(self), spec)}{D1}" if gate_on() else str.__format__(str.__str__(self), spec)

    def __str__(self):
        return f"{D0}{str.__str__(self)}{D1}" if gate_on() else str.__str__(self)


def definitions(d: dict) -> dict:
    return {k: DefText(v) for k, v in d.items()}


def definition_text(text: str) -> DefText:
    """A whole block that declares the search space or the methods (methods / data-source / manifest tables):
    the layer-1 path allowlist of those blocks, carried to the rendered text. Tagged values inside stay
    checked."""
    return DefText(text)


def items(d: dict):
    """(key, value) pairs of a loaded JSON dict with the keys tagged (keys that are numbers, e.g. horizons)."""
    src = getattr(d, "src", "")
    return [(PStr(k, f"key({src},{_esc(str(k))})") if re.search(r"\d", str(k)) else k, v) for k, v in d.items()]


# --------------------------------------------------------------------------------- evaluation (used by the gate)
def _split_args(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
            continue
        depth += ch == "("
        depth -= ch == ")"
        cur += ch
    out.append(cur)
    return out


def _unesc(s: str) -> str:
    for k, v in _ESC.items():
        s = s.replace(v, k)
    return s


def _art(ref: str):
    path, _, key = ref.partition("#")
    f = RESULTS / _unesc(path)
    if f.suffix == ".csv":
        if not key:
            return pd.read_csv(f)
        row, col = key.split("/", 1)
        return pd.read_csv(f)[_unesc(col)].iloc[int(row[1:])]
    o = json.loads(f.read_text())
    for k in [x for x in key.split("/") if x != ""]:
        k = _unesc(k)
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


def evaluate(src: str, fields: dict | None = None):
    """Value of a source expression, from the artifacts on disk (winner fields: their display text)."""
    m = re.fullmatch(r"(\w+)\((.*)\)", src, re.S)
    if src.startswith("art:"):
        return _art(src[4:])
    if src.startswith("wf:"):
        return ((fields or {}).get(src[3:]) or {}).get("text")
    if src.startswith("reg:"):
        o = json.loads(REGISTRY.read_text())["pairs"]
        for k in src[4:].split("/"):
            k = _unesc(k)
            o = o[int(k)] if isinstance(o, list) else o[k]
        return o
    if src.startswith("const:"):
        return float(src[6:])
    if not m:
        raise ValueError(f"bad source expression {src!r}")
    fn, args = m.group(1), _split_args(m.group(2))
    if fn in ("mul", "div", "add", "sub"):
        a, b = (float(evaluate(x, fields)) for x in args)
        return {"mul": a * b, "div": a / b, "add": a + b, "sub": a - b}[fn]
    if fn in ("neg", "abs"):
        a = float(evaluate(args[0], fields))
        return -a if fn == "neg" else abs(a)
    if fn == "len":
        return len(evaluate(args[0], fields))
    if fn in ("min", "max", "maxabs"):
        df = evaluate(args[0], fields)
        s = df[_unesc(args[1])].astype(float)
        return float(s.min() if fn == "min" else s.max() if fn == "max" else s.abs().max())
    if fn == "key":
        d = evaluate(args[0], fields)
        k = _unesc(args[1])
        if k not in d:
            raise KeyError(k)
        return k
    if fn == "prefix":
        return str(evaluate(args[0], fields))[:int(args[1])]
    if fn == "count":
        df = evaluate(args[0], fields)
        col, op, other = _unesc(args[1]), args[2], _unesc(args[3])
        a = df[col].astype(float)
        try:
            b = float(other)
        except ValueError:
            b = df[other].astype(float)
        return int(_OPS[op](a, b).sum())
    raise ValueError(f"unknown function {fn!r} in {src!r}")
