"""Provenance tagging of artifact values for page prose (structured-prose layer 2 v2).

Pair configs read every number they print through this module (and through components.winner_fields). In normal
use nothing changes: values behave like plain numbers and strings. When the number-provenance gate renders a page
(environment AIG_PROVENANCE_GATE=1), every artifact value that is formatted into text carries an invisible
sentinel naming its source:

    \\ue000<source expression>\\ue001<displayed text>\\ue002

and the gate (scripts/gate_number_provenance.py) fails on any number in the pair's authored text that is not
inside a sentinel (or a justified allowlist span), and re-evaluates every sentinel's source expression against
the artifacts to check the displayed text.

Source expressions (sentinel: S0 <source> U <unit> S1 <text> S2; unit 'pct' when the value was formatted with a
'%' spec, i.e. displayed x 100, else 'raw'):
    art:<results-relative path>#<key path>      a value in a JSON (a/b/0/c) or CSV (r<row>/<column>) artifact; the
                                                path must resolve inside results/<pair>/ (the gate enforces it)
    reg:<pair>/<key path>                       the pair's lead_axis_registry entry
    wf:<field>                                  a winner_fields entry (text reconciled with its value by the gate)
    mul(a,b) div(a,b) add(a,b) sub(a,b) neg(a) abs(a); const:<number> only as an operand of mul / div (unit
    constants) or add / sub (1), next to an artifact operand; never a root (Codex L2v2 F1)
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
AP = ""                                      # end of the config attribute path after A0 (added by the gate)
U = ""                                       # source / unit separator inside a value sentinel
T0, T1 = "\ue009", "\ue00a"                        # table source header marker (gate mode only, v5)
RESULTS = Path(__file__).resolve().parents[2] / "results"
REGISTRY = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "lead_axis_registry.json"
_ESC = {",": "%2C", "(": "%28", ")": "%29"}


def _esc(s: str) -> str:
    for k, v in _ESC.items():
        s = s.replace(k, v)
    return s


def _tag(text, src: str, unit: str = "raw") -> str:
    """Sentinel-wrapped text in gate mode (private: configs never mint tags; the gate re-evaluates every source
    and rejects constant roots and sources outside the pair's results)."""
    text = str.__str__(text) if isinstance(text, str) else str(text)
    return f"{S0}{src}{U}{unit}{S1}{text}{S2}" if gate_on() else text


# --------------------------------------------------------------------------------------------- tagged numbers
def _num(v, src):
    return _PInt(v, src) if isinstance(v, int) and not isinstance(v, bool) else _PNum(v, src)


def _src(x) -> str:
    return x.src if isinstance(x, (_PNum, _PInt)) else f"const:{x!r}"


class _Tagged:
    src: str

    def __format__(self, spec):
        return _tag(self._base().__format__(spec), self.src, "pct" if spec.rstrip().endswith("%") else "raw")

    def __str__(self):
        return _tag(self._base().__str__(), self.src)

    def __repr__(self):
        return self._base().__repr__()

    def __abs__(self):
        return _num(abs(self._base()), f"abs({self.src})")

    def __neg__(self):
        return _num(-self._base(), f"neg({self.src})")

    def __pos__(self):
        return self

    def __round__(self, nd=None):
        return _num(round(self._base(), nd), self.src) if nd is not None else _PInt(round(self._base()), self.src)

    def _op(self, other, fn, name, rev=False):
        if not isinstance(other, (int, float)) or isinstance(other, bool):
            return NotImplemented
        a, b = (other, self) if rev else (self, other)
        base = lambda x: x._base() if isinstance(x, _Tagged) else x  # noqa: E731  (int op int stays int)
        res = fn(base(a), base(b))
        if not isinstance(other, _Tagged):
            c = abs(float(other))
            if c not in (UNIT_MUL if name in ("mul", "div") else UNIT_ADD):
                return res              # an untagged operand that is not a unit constant: the result is untagged
        return _num(res, f"{name}({_src(a)},{_src(b)})")

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


class _PNum(_Tagged, float):
    def __new__(cls, v, src: str):
        o = float.__new__(cls, v)
        o.src = src
        return o

    def _base(self):
        return float(self)

    def __reduce__(self):                       # copy / deepcopy / pickle (plotly deep-copies figure data)
        return (_PNum, (float(self), self.src))

    __hash__ = float.__hash__


class _PInt(_Tagged, int):
    def __new__(cls, v, src: str):
        o = int.__new__(cls, v)
        o.src = src
        return o

    def _base(self):
        return int(self)

    def __reduce__(self):
        return (_PInt, (int(self), self.src))

    __hash__ = int.__hash__


# ------------------------------------------------------------------------------------------------- loaders
def _rel(path: Path) -> str:
    try:
        return _esc(str(Path(path).resolve().relative_to(RESULTS.resolve())))
    except ValueError:
        return "outside-results:" + _esc(str(path))       # the gate rejects it (Codex L2v2 F2)


class _PStr(str):
    """Artifact text that contains numbers (e.g. a diagnosis reading): tagged when formatted into prose."""

    def __new__(cls, text: str, src: str):
        o = str.__new__(cls, text)
        o.src = src
        return o

    def __format__(self, spec):
        return _tag(str.__format__(str.__str__(self), spec), self.src)

    def __reduce__(self):
        return (_PStr, (str.__str__(self), self.src))

    def __str__(self):
        return _tag(str.__str__(self), self.src)


class _PList(list):
    src: str


class _PDict(dict):
    src: str


def _wrap(o, src: str, dates: bool = True):
    if isinstance(o, str):
        # prose-like text with numbers (a diagnosis reading) and ISO dates are tagged; identifier-like strings
        # (file names, codes, keys) stay plain so that code building paths or lookups from them is unaffected
        tagged = re.search(r"\d", o) and (re.search(r"\s", o) or
                                          dates and re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", o))
        return _PStr(o, src) if tagged else o
    if isinstance(o, bool) or o is None:
        return o
    if isinstance(o, (int, float)):
        return _num(o, src) if not (isinstance(o, float) and math.isnan(o)) else o
    if isinstance(o, dict):
        d = _PDict({k: _wrap(v, f"{src}/{_esc(str(k))}", dates) for k, v in o.items()})
        d.src = src
        return d
    if isinstance(o, list):
        lst = _PList(_wrap(v, f"{src}/{i}", dates) for i, v in enumerate(o))
        lst.src = src
        return lst
    return o


def table_source(df: pd.DataFrame, *sources, derived=(), columns=None) -> pd.DataFrame:
    """Shared-template tables (v5, QA L2v4 #1): name the artifact file(s) a displayed table comes from, so the gate
    checks every number of a displayed row against ONE row of a current source file instead of value-matching it
    against every number of the pair's results. ``sources``: paths, optionally with a JSON pointer to a list of
    records ('.../signal_scope.json#/indicator_axis/derivatives'); ``derived``: {display column: rank column} for a
    rank the template computes (the gate recomputes it, Codex V52-3); ``columns``: {display column: source column}
    for a displayed column whose header is not the source column's name (the gate checks each cell against its own
    source column only, Codex V52-2). Gate mode only: the first column header carries the marker."""
    if not gate_on() or df is None or len(df.columns) == 0:
        return df
    repo = RESULTS.parent.resolve()
    srcs = []
    for x in sources:
        path, _, ptr = str(x).partition("#")
        try:
            rel = str(Path(path).resolve().relative_to(repo))
        except ValueError:
            rel = "outside-repo:" + path
        srcs.append(rel + (f"#{ptr}" if ptr else ""))
    der = derived if isinstance(derived, dict) else {c: None for c in derived}   # {display col: source col | None}
    head = f"{T0}{json.dumps({'src': srcs, 'derived': der, 'columns': dict(columns or {})})}{T1}"
    out = df.copy()
    out.columns = [f"{head}{out.columns[0]}", *out.columns[1:]]
    return out


def artifact(data, path):
    """Tag an artifact already loaded from `path` (e.g. by schema_check.validate_or_die) like json_file does."""
    return _wrap(data, f"art:{_rel(path)}#", dates=False) if gate_on() else data


def run_tag(ws: dict, pair_dir=None) -> str | None:
    """A pair's current run tag (plain text, untagged: it names files): winner_summary run_tag (Phase B harness),
    else the published winner's source tournament file. None when neither exists. No latest-dated-file guess
    (QA nomain F2: a deleted current-run file silently fell back to a superseded run). Mirrors
    scripts/chart_provenance.run_tag_of."""
    if ws.get("run_tag"):
        return str(ws["run_tag"])
    try:
        return str(ws["selection"]["raw_winner_row"]["source_tournament_file"]).split("_")[-1].removesuffix(".csv")
    except (KeyError, TypeError, AttributeError):
        return None


class CurrentRunFileError(FileNotFoundError):
    """A Phase B pair's current-run file is missing (or its run tag is unknown): pages show the error."""


def is_phase_b(pair_id: str, rdir=None) -> bool:
    """winner_summary 1.3.x with per-track records (Phase B harness pair)."""
    try:
        return "tracks" in json.loads((Path(rdir or RESULTS / pair_id) / "winner_summary.json").read_text())
    except (OSError, ValueError):
        return False


def current_file(pair_id: str, stem: str, ext: str = "csv", rdir=None) -> Path | None:
    """results/<pair>/<stem>_<tag>.<ext> of the pair's CURRENT run. Phase B pairs: the tag is winner_summary's run
    tag and a missing file raises CurrentRunFileError (never a guess). Legacy pairs (not yet ported): the latest
    dated file, None when there is none (their pre-Phase-B behaviour)."""
    rdir = Path(rdir or RESULTS / pair_id)
    if is_phase_b(pair_id, rdir):
        tag = run_tag(json.loads((rdir / "winner_summary.json").read_text()), rdir)
        if not tag:
            raise CurrentRunFileError(f"{pair_id}: winner_summary.json names no run tag, so the current run's "
                                      f"{stem} file cannot be resolved")
        f = rdir / f"{stem}_{tag}.{ext}"
        if not f.is_file():
            raise CurrentRunFileError(f"{pair_id}: the current run's file results/{pair_id}/{f.name} is missing "
                                      f"(run {tag}); rebuild with python scripts/pair_pipeline_{pair_id}.py")
        return f
    files = sorted(rdir.glob(f"{stem}_*.{ext}"))
    return files[-1] if files else None


def deployed_signal(pair_id: str, rdir=None):
    """Phase B pairs: the MAIN winner's signal and threshold exactly as the rule used them at each rebalance date
    (point in time, lagged by the lead; the harness's strategy_returns_<tag>.csv) and its position. None for
    legacy pairs or a missing file (the caller shows the error from resolve_current)."""
    import pandas as pd
    if not is_phase_b(pair_id, rdir):
        return None
    f = resolve_current(pair_id, "strategy_returns", rdir=rdir)
    if f is None:
        return None
    df = pd.read_csv(f, parse_dates=["date"]).set_index("date")
    return df[[c for c in ("signal", "threshold", "position") if c in df.columns]]


def resolve_current(pair_id: str, stem: str, ext: str = "csv", rdir=None) -> Path | None:
    """current_file for page components: a missing Phase B current-run file is shown as an error on the page and
    the component renders nothing from another run."""
    try:
        return current_file(pair_id, stem, ext, rdir)
    except CurrentRunFileError as e:
        import streamlit as st
        st.error(f"**Current-run file missing.** {e}")
        return None


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
            df[c] = pd.Series([_PStr(v, f"{src}r{i}/{_esc(str(c))}") if isinstance(v, str) and re.search(r"\d", v)
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
    out = _PList(_PInt(v, f"reg:{_esc(pair_id)}/lead_grid/{i}") for i, v in enumerate(grid))
    out.src = f"reg:{_esc(pair_id)}/lead_grid"
    return out


# ------------------------------------------------------------------------------------------- derived values
def length(obj) -> _PInt:
    """len() of a loaded JSON list / dict or a loaded CSV table, tagged."""
    src = obj.attrs["src"] if isinstance(obj, pd.DataFrame) else obj.src
    return _PInt(len(obj), f"len({src})")


_OPS = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
        "!=": lambda a, b: a != b, "==": lambda a, b: a == b}


def count(df: pd.DataFrame, col: str, op: str, other) -> _PInt:
    """Rows of a loaded CSV where `col <op> other` (a number or another column), tagged."""
    a = df[col].astype(float)
    b = df[other].astype(float) if isinstance(other, str) else float(other)
    n = int(_OPS[op](a, b).sum())
    return _PInt(n, f"count({df.attrs['src']},{_esc(col)},{op},{_esc(str(other))})")


def colmin(df: pd.DataFrame, col: str) -> _PNum:
    return _PNum(float(df[col].astype(float).min()), f"min({df.attrs['src']},{_esc(col)})")


def colmax(df: pd.DataFrame, col: str) -> _PNum:
    return _PNum(float(df[col].astype(float).max()), f"max({df.attrs['src']},{_esc(col)})")


def colmaxabs(df: pd.DataFrame, col: str) -> _PNum:
    return _PNum(float(df[col].astype(float).abs().max()), f"maxabs({df.attrs['src']},{_esc(col)})")


def prefix(text: "_PStr", n: int) -> "_PStr | str":
    """The first n characters of tagged artifact text (e.g. the year of a date), still tagged."""
    return _PStr(str.__str__(text)[:n], f"prefix({text.src},{n})") if isinstance(text, _PStr) else text[:n]


def field_text(d, key):
    """Shared templates only (not in a config's P API): the field `key` of a tagged artifact dict as tagged text,
    dates included (artifact() leaves ISO dates plain because template code parses them). Plain value outside the
    gate or for an untagged dict; None when the field is missing."""
    if isinstance(d, (list, tuple)):
        v = d[key] if isinstance(key, int) and -len(d) <= key < len(d) else None
        key = key % len(d) if v is not None else key
    else:
        v = d.get(key) if hasattr(d, "get") else None
    src = getattr(d, "src", None)
    if v is None or src is None or not gate_on() or isinstance(v, (dict, list)):
        return v
    return _PStr(str.__str__(v) if isinstance(v, str) else str(v), f"{src}/{_esc(str(key))}")


def span_years(a, b):
    """Years between two ISO dates (a window length), tagged years(<src a>,<src b>) when both dates are tagged."""
    n = (pd.Timestamp(str.__str__(a) if isinstance(a, str) else a)
         - pd.Timestamp(str.__str__(b) if isinstance(b, str) else b)).days / -365.25
    return _PNum(n, f"years({a.src},{b.src})") if isinstance(a, _PStr) and isinstance(b, _PStr) else n


def year(date_text: "_PStr") -> "_PStr | str":
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
    return [(_PStr(k, f"key({src},{_esc(str(k))})") if re.search(r"\d", str(k)) else k, v) for k, v in d.items()]


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


UNIT_MUL = {100.0, 12.0, 4.0, 52.0, 252.0, 0.01, 1.0}     # percent, periods per year
UNIT_ADD = {1.0}                                          # inclusive counts (months from a to b)


class SourceError(ValueError):
    pass


def _read_csv(f) -> pd.DataFrame:
    """A CSV artifact as the templates read it: a leading '#' comment block (broker-style logs) is skipped."""
    with open(f) as fh:
        head = fh.read(1)
    return pd.read_csv(f, comment="#") if head == "#" else pd.read_csv(f)


def _art(ref: str, pair: str | None):
    path, _, key = ref.partition("#")
    if path.startswith("outside-results:"):
        raise SourceError(f"source file outside results/: {_unesc(path[16:])}")
    f = (RESULTS / _unesc(path)).resolve()
    root = (RESULTS / pair).resolve() if pair else RESULTS.resolve()
    try:
        f.relative_to(root)
    except ValueError:
        raise SourceError(f"source {f} is not inside {root}") from None
    if f.suffix == ".csv":
        if not key:
            return _read_csv(f)
        row, col = key.split("/", 1)
        return _read_csv(f)[_unesc(col)].iloc[int(row[1:])]
    o = json.loads(f.read_text())
    for k in [x for x in key.split("/") if x != ""]:
        k = _unesc(k)
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


UNITS = Path(__file__).resolve().parents[2] / "docs" / "gates" / "provenance_units.json"
_UNIT_RULES: list | None = None
RATIO_KINDS = {"ratio", "period_return"}


def leaf_kind(leaf: str) -> str:
    """Declared kind of an artifact leaf (docs/gates/provenance_units.json; Codex L2v3 N2)."""
    global _UNIT_RULES
    if _UNIT_RULES is None:
        _UNIT_RULES = [(re.compile(r["pattern"]), r["kind"]) for r in json.loads(UNITS.read_text())["rules"]]
    for rx, kind in _UNIT_RULES:
        if rx.search(leaf):
            return kind
    return "unknown"


def _ppy(pair: str | None):
    if not pair:
        return None
    try:
        f = current_file(pair, "candidates_manifest", "json")
        if f is not None:
            return float(json.loads(f.read_text()).get("ppy"))
    except (OSError, ValueError, TypeError):
        return None
    return None


def kind_of(src: str, pair: str | None = None) -> str:
    """Kind of a source expression, enforcing unit-correct arithmetic: x100 only on a ratio or a per-period
    return (-> 'percent'); x periods-per-year only on a per-period return at the pair's own frequency
    (-> 'ratio'); /100 only on a percent; +/-1 only on a count or lead; a sum / difference only of two
    leaves of the same kind. SourceError otherwise."""
    m = re.fullmatch(r"(\w+)\((.*)\)", src, re.S)
    if src.startswith(("art:", "reg:")):
        return leaf_kind(src)
    if src.startswith("wf:"):
        return "field"
    if src.startswith("const:"):
        return "const"
    if not m:
        raise SourceError(f"bad source expression {src!r}")
    fn, args = m.group(1), _split_args(m.group(2))
    if fn in ("neg", "abs"):
        return kind_of(args[0], pair)
    if fn in ("len", "count"):
        return "count"
    if fn in ("min", "max", "maxabs"):
        return leaf_kind(f"{args[0]}/{_unesc(args[1])}")
    if fn in ("key", "prefix"):
        return "label"
    if fn == "years":
        return "duration"
    if fn in ("mul", "div", "add", "sub"):
        ka, kb = kind_of(args[0], pair), kind_of(args[1], pair)
        if "const" not in (ka, kb):
            if ka != kb:
                raise SourceError(f"{fn} of a {ka} and a {kb} in {src!r}")
            if ka == "unknown":                 # QA L2v4 #4: undeclared leaves are never combined
                raise SourceError(f"{fn} of two leaves of undeclared kind in {src!r}")
            return ka
        c = float(args[1][6:] if kb == "const" else args[0][6:])
        k = ka if kb == "const" else kb
        if fn in ("add", "sub"):
            if c == 1 and k in ("count", "lead"):
                return k
            raise SourceError(f"{fn} of {c:g} on a {k} in {src!r}")
        if c == 100 and fn == "mul" and k in RATIO_KINDS:
            return "percent"
        if c in (0.01,) and fn == "mul" and k == "percent" or c == 100 and fn == "div" and k == "percent":
            return "ratio"
        if c in (12.0, 4.0, 52.0, 252.0) and fn == "mul" and k == "period_return" and c == _ppy(pair):
            return "ratio"
        raise SourceError(f"{fn} by {c:g} is not a valid unit operation on a {k} in {src!r}")
    return "unknown"


def _has_leaf(src: str) -> bool:
    return bool(re.search(r"(?:^|[(,])(?:art|wf|reg):", src))


def evaluate(src: str, fields: dict | None = None, pair: str | None = None, _root: bool = True):
    """Value of a source expression, from the artifacts on disk (winner fields: their display text). With `pair`,
    every artifact must be inside results/<pair>/ and every registry key under that pair; a constant may not be a
    root or a stand-alone source (SourceError)."""
    m = re.fullmatch(r"(\w+)\((.*)\)", src, re.S)
    if src.startswith("art:"):
        return _art(src[4:], pair)
    if src.startswith("wf:"):
        return ((fields or {}).get(src[3:]) or {}).get("text")
    if src.startswith("reg:"):
        keys = [_unesc(k) for k in src[4:].split("/")]
        if pair and keys[0] != pair:
            raise SourceError(f"registry source for another pair: {src}")
        o = json.loads(REGISTRY.read_text())["pairs"]
        for k in keys:
            o = o[int(k)] if isinstance(o, list) else o[k]
        return o
    if src.startswith("const:"):
        if _root:
            raise SourceError(f"a constant is not a source: {src}")
        return float(src[6:])
    if not m:
        raise SourceError(f"bad source expression {src!r}")
    if _root and not _has_leaf(src):
        raise SourceError(f"no artifact in source expression {src!r}")
    fn, args = m.group(1), _split_args(m.group(2))
    ev = lambda x: evaluate(x, fields, pair, False)  # noqa: E731
    if fn in ("mul", "div", "add", "sub"):
        for x, y in ((args[0], args[1]), (args[1], args[0])):
            if x.startswith("const:"):
                c = abs(float(x[6:]))
                ok = c in (UNIT_MUL if fn in ("mul", "div") else UNIT_ADD) and _has_leaf(y)
                if not ok:
                    raise SourceError(f"constant {x} is not an allowed unit operand in {src!r}")
        if not (_has_leaf(args[0]) or _has_leaf(args[1])):
            raise SourceError(f"no artifact operand in {src!r}")
        a, b = (float(ev(x)) for x in args)
        return {"mul": a * b, "div": a / b, "add": a + b, "sub": a - b}[fn]
    if fn in ("neg", "abs"):
        a = float(ev(args[0]))
        return -a if fn == "neg" else abs(a)
    if fn == "len":
        return len(ev(args[0]))
    if fn in ("min", "max", "maxabs"):
        df = ev(args[0])
        sr = df[_unesc(args[1])].astype(float)
        return float(sr.min() if fn == "min" else sr.max() if fn == "max" else sr.abs().max())
    if fn == "key":
        d = ev(args[0])
        k = _unesc(args[1])
        if k not in d:
            raise SourceError(f"key {k!r} not in {args[0]}")
        return k
    if fn == "prefix":
        return str(ev(args[0]))[:int(args[1])]
    if fn == "years":
        return (pd.Timestamp(str(ev(args[1]))) - pd.Timestamp(str(ev(args[0])))).days / 365.25
    if fn == "count":
        df = ev(args[0])
        col, op, other = _unesc(args[1]), args[2], _unesc(args[3])
        a = df[col].astype(float)
        try:
            b = float(other)
        except ValueError:
            b = df[other].astype(float)
        return int(_OPS[op](a, b).sum())
    raise SourceError(f"unknown function {fn!r} in {src!r}")
