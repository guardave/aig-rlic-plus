#!/usr/bin/env python3
"""GATE-NUMBER-PROVENANCE (structured-prose layer 2 v2): every number a schema-1.3 pair's pages SHOW must come from
that pair's artifacts, and a number the pair config AUTHORS must carry its source.

Layer 1 (gate_structured_prose.py: authored-text scan + NUMLIT) is static and can be evaded by code that builds a
number (Codex B0f). v1 of this layer matched rendered numbers against artifact values, which a stale number
could pass by coincidence (24-32% of random plausible numbers). v2 tags provenance at render:

  1. Render each page (story / evidence / strategy / methodology) in-process with streamlit.testing.AppTest,
     with AIG_PROVENANCE_GATE=1. Then every artifact value a config formats into text carries an invisible
     sentinel naming its source (components.provenance loaders: json_file / csv_file / lead_grid / length /
     count / colmin / colmax ...; components.winner_fields text), and every prose string the pair config hands to
     the templates is marked as AUTHORED (the gate imports the config fresh and wraps its prose attributes).
     Definition text of the declared search space / methods tables (provenance.definitions /
     definition_text) is marked as DEFINITION (the layer-1 path allowlist, carried to the rendered text).
  2. AUTHORED numbers (decimals, %, pp, dates, number words, ordinals) must sit inside a sentinel or a justified
     allowlist span (docs/gates/number_provenance_allowlist.json + paths-'*' entries of the layer-1
     allowlist); anything else FAILs as UNTAGGED, whatever its value. Coincidence for authored text is zero by
     construction: equalling an artifact value is not enough.
  3. Every sentinel is re-evaluated from the artifacts on disk (provenance.evaluate) and must equal the
     displayed text at its displayed precision (MISMATCH otherwise).
  4. TEMPLATE text (shared components, not pair-authored) keeps the v1 value-matching fallback against the
     curated pool (winner_summary, track_summary, evidence_facts + its declared sources / derived facts,
     manifest, registry, trade-log first row, template-derived window lengths / KPI deltas); st.table /
     st.dataframe cells may also match the pair's current result files. The printed 'coincidence' applies to
     this template fallback only. Chart internals are not checked.

Hardening after Codex L2v2 (F1-F11): configs cannot mint tags (private constructors; layer-1 PROVENANCE-API);
a constant is never a source, only a unit operand next to an artifact; every source must resolve inside
results/<pair>/ (or the pair's registry entry); winner_fields text is reconciled with its value; every number in
a tagged span is checked in the declared unit (raw / pct); tables and charts go through the same sentinel check
(charts: see CHART_SCOPE); template matching respects explicit signs; number words compose (twenty-one) and
'one' / 'zero' count when a unit follows; non-ASCII numerals are reported; layer-1 phrase exemptions apply to
authored text only in the config attributes their `paths` name (GLOBAL_OK excepted); definition text must equal
an approved definition (a *_TEXT dict value or an approved methodology block); the marked config module is fully
discarded after a render. Shared-template values loaded through schema_check.validate_or_die are tagged too.

v4 after Codex L2v3 (N1-N5): the only allowed import is `from components import provenance as P` (any other form or
dynamic access fails PROVENANCE-API; a forged tag can in any case only show the value its source evaluates to);
every artifact leaf has a declared kind (docs/gates/provenance_units.json) and x100 / '%' display / annualisation
/ +-1 are allowed only on matching kinds and the pair's own frequency; every visible Plotly string is checked;
definition text and categorical winner-field labels may show only numbers the pair spec / pipeline / manifest /
registry declare; winner-field reconciliation is sign-sensitive. N6 (disclosed residual): shared-template text is
still value-matched (coincidence printed per pair, the value-matched blocks listed), but numbers on headline /
confidence surfaces (KPI metrics, vs buy-and-hold facts, chance check, revised-data caption) must be tagged
(HEADLINE findings otherwise).

Usage:
  python scripts/gate_number_provenance.py [pair ...]         # default: every pair with winner_summary 1.3.x
  python scripts/gate_number_provenance.py --text FILE --pair P  # v1 value check of a text file (diagnostic)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "app"
RESULTS = REPO / "results"
ALLOWLIST = REPO / "docs" / "gates" / "number_provenance_allowlist.json"
PROSE_ALLOWLIST = REPO / "docs" / "gates" / "structured_prose_allowlist.json"
REGISTRY = REPO / "docs" / "schemas" / "lead_axis_registry.json"
SECTIONS = ("story", "evidence", "strategy", "methodology")

UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen".split())}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALES = {"hundred": 100, "thousand": 1000, "million": 1e6, "dozen": 12, "half": 0.5}
NUMBER_WORDS = {**UNITS, **TENS, **SCALES}          # (kept for callers of v1)
ORDINAL_WORDS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
                 "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12}
DATE = re.compile(r"\b(\d{4})-(\d{2})(?:-(\d{2}))?\b")
NUM = re.compile(r"(?<![\w.])[-+−]?\$?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?"
                 r"|(?<![\w.])[-+−]?\$?\d+(?:\.\d+)?(?:e[-+]?\d+)?%?"
                 r"|(?<=[A-Za-z])\d+(?:\.\d+)?(?=\b)")
ORDINAL = re.compile(r"\b(\d+)(?:st|nd|rd|th)\b")
_U9 = "one|two|three|four|five|six|seven|eight|nine"
WORD = re.compile(r"\b(?:(?P<tens>" + "|".join(TENS) + r")(?:[- ](?P<unit>" + _U9 + r"))?|(?P<small>"
                  + "|".join(sorted(UNITS, key=len, reverse=True)) + r")|(?P<scale>" + "|".join(SCALES) + r"))\b",
                  re.I)
# a number word followed by a unit is a quantity even for 'one' / 'zero' (Codex L2v2 F8: 'zero percent')
UNIT_AFTER = re.compile(r"\s*-?\s*(?:%|(?:per ?cent|pp|percentage points?|basis points?|bps?|months?|quarters?|"
                        r"years?|days?|weeks?|times)\b)", re.I)
# numerals other than ASCII / Unicode decimal digits: superscripts / subscripts, vulgar fractions, Roman numerals,
# Chinese / Japanese numerals. Always reported (nothing in a pair page needs them).
NONASCII_NUM = re.compile(r"[\u00b2\u00b3\u00b9\u00bc-\u00be\u2070-\u2079\u2080-\u2089\u2150-\u218b"
                          r"\u3007\u96f6\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e"
                          r"\u5343\u4e07\u5104\u4ebf\u5169]+")


def word_value(m) -> float:
    if m.group("tens"):
        return TENS[m.group("tens").lower()] + (UNITS[m.group("unit").lower()] if m.group("unit") else 0)
    if m.group("small"):
        return UNITS[m.group("small").lower()]
    return SCALES[m.group("scale").lower()]


# ------------------------------------------------------------------------------------------------- pool
def _walk(obj, nums: list, strs: list):
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        if math.isfinite(obj):
            nums.append(float(obj))
    elif isinstance(obj, str):
        strs.append(obj)
        try:                                     # numeric strings ("0.57", "L5-L63" handled by text tokens)
            nums.append(float(obj))
        except ValueError:
            pass
        for m in NUM.finditer(obj):              # numbers inside artifact text (field `text`, readings)
            v = _value(m.group(0))
            if v is not None:
                nums.append(v[0])
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _walk(v, nums, strs)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _walk(v, nums, strs)


def pool_files(pair: str) -> list[Path]:
    rdir = RESULTS / pair
    ws = json.loads((rdir / "winner_summary.json").read_text())
    tag = ws["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")
    files = [rdir / "winner_summary.json", rdir / "track_summary.json", rdir / f"evidence_facts_{tag}.json",
             rdir / f"candidates_manifest_{tag}.json", rdir / "interpretation_metadata.json"]
    return [f for f in files if f.exists()]


def _table_numbers(f: Path, nums: list, strs: list):
    import pandas as pd
    if f.suffix == ".json":
        _walk(json.loads(f.read_text()), nums, strs)
        return
    df = pd.read_csv(f, comment="#")
    nums += [float(x) for x in df.select_dtypes("number").to_numpy().ravel() if pd.notna(x)]
    for x in df.select_dtypes(exclude="number").to_numpy().ravel():   # formatted cells ("+0.0082**")
        _walk(str(x), nums, strs)


def _template_derived(pair: str, ws: dict) -> list[float]:
    """Values the shared templates derive from the curated artifacts: KPI deltas vs buy-and-hold (Sharpe,
    annual return and drawdown, in percentage points) and the count of disclosed target-axis derivatives in
    signal_scope.json."""
    out = []
    for a, b in (("oos_sharpe", "bh_sharpe"), ("oos_ann_return", "bh_ann_return"),
                 ("oos_max_drawdown", "bh_max_drawdown")):
        if isinstance(ws.get(a), (int, float)) and isinstance(ws.get(b), (int, float)):
            out += [ws[a] - ws[b], (ws[a] - ws[b]) * 100]
    sc = RESULTS / pair / "signal_scope.json"
    if sc.exists():
        for v in json.loads(sc.read_text()).values():
            if isinstance(v, list):
                out.append(float(len(v)))
    return out


def load_pool(pair: str) -> dict:
    """Curated pool: winner / track summaries, evidence_facts (+ its declared small 'sources' tables and
    'derived' facts), the candidates manifest, the registry entry, the first row of the broker-style trade
    log (the trade-log column examples), and the template-derived values (window lengths, KPI deltas)."""
    nums, strs = [], []
    files = pool_files(pair)
    for f in files:
        _walk(json.loads(f.read_text()), nums, strs)
    rdir = RESULTS / pair
    ev = next((f for f in files if f.name.startswith("evidence_facts_")), None)
    for src in (json.loads(ev.read_text()).get("sources", []) if ev else []):
        _table_numbers(rdir / src, nums, strs)
        files.append(rdir / src)
    tl = rdir / "winner_trades_broker_style.csv"
    if tl.exists():
        import pandas as pd
        first = pd.read_csv(tl, comment="#").iloc[:1]
        nums += [float(x) for x in first.select_dtypes("number").to_numpy().ravel()]
        strs += [str(x) for x in first.select_dtypes(exclude="number").to_numpy().ravel()]
    try:
        _walk(json.loads(REGISTRY.read_text())["pairs"][pair], nums, strs)
    except (OSError, KeyError):
        pass
    nums += _durations(files) + _template_derived(pair, json.loads((rdir / "winner_summary.json").read_text()))
    dates = set()
    for s in strs:
        for m in DATE.finditer(s):
            dates.add(m.group(0))
            dates.add(m.group(0)[:7])
    years = {d[:4] for d in dates}
    return {"nums": sorted(set(nums)), "dates": dates, "years": years, "files": [str(f.relative_to(REPO)) for f in files]}


def _durations(files: list[Path]) -> list[float]:
    """Window lengths the templates derive from artifact dates ((end - start).days / 365.25, as displayed
    'N.N yrs' / '(N years)'): every [start, end] date pair and every *_start / *_end key pair in the
    winner / track summaries."""
    out = []

    def yrs(a, b):
        try:
            da, db = date.fromisoformat(str(a)[:10]), date.fromisoformat(str(b)[:10])
        except ValueError:
            return
        y = (db - da).days / 365.25
        months = (db.year - da.year) * 12 + db.month - da.month + 1      # inclusive calendar months
        out.extend([y, float(round(y)), float(months), float(db.year - da.year)])

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and k.endswith("_start") and isinstance(v, str):
                    e = o.get(k[:-6] + "_end")
                    if isinstance(e, str):
                        yrs(v, e)
                walk(v)
        elif isinstance(o, list):
            if len(o) == 2 and all(isinstance(x, str) and DATE.match(x) for x in o):
                yrs(o[0], o[1])
            for v in o:
                walk(v)
    for f in files:
        if f.name in ("winner_summary.json", "track_summary.json"):
            walk(json.loads(f.read_text()))
    return out


# ------------------------------------------------------------------------------------------- resolution
def _value(tok: str) -> tuple[float, int, bool] | None:
    """(value, decimals, is_percent) of a numeric token."""
    t = tok.replace("−", "-").replace("$", "").replace(",", "")
    pct = t.endswith("%")
    t = t.rstrip("%")
    try:
        v = float(t)
    except ValueError:
        return None
    if "e" in t.lower():                         # scientific notation: match at its significant digits
        mant, ex = t.lower().split("e")
        d = (len(mant.split(".")[1]) if "." in mant else 0) - int(ex)
        return v, max(d, 0), pct
    d = len(t.split(".")[1]) if "." in t else 0
    return v, d, pct


def resolves(v: float, d: int, pct: bool, pool: dict, is_int_word=False, signed: bool = False) -> bool:
    """Percent tokens (and ordinals, passed as pct) match a pool value or 100x a pool value at the printed
    precision; bare integers match integer-valued pool numbers exactly (so "5" is not "any value in
    [4.5, 5.5)"); decimals match at their printed precision. signed (the token carries an explicit + / -
    sign): the pool value must have that sign (Codex L2v2 F5); an unsigned token matches a magnitude."""
    def same(a, x, tol):
        return abs(a - x) <= tol if signed else abs(abs(a) - abs(x)) <= tol
    if pct:
        tol = 0.5 * 10 ** -d + 1e-9
        return any(same(a, v, tol) or same(a * 100, v, tol) for a in pool["nums"])
    if d == 0:
        return any(float(abs(a)).is_integer() and (a == v if signed else abs(a) == abs(v)) for a in pool["nums"])
    tol = 0.5 * 10 ** -d + 1e-9
    return any(same(a, v, tol) for a in pool["nums"])


# Layer-1 allowlist entries usable anywhere in AUTHORED text (they cannot carry a result: list numbering, proper
# names, identifiers / codes, fixed statistical conventions). Every other layer-1 entry applies to authored text
# only in the config attributes its `paths` name (Codex L2v2 F9: no global phrase laundering). Template text uses the
# layer-2 entries (docs/gates/number_provenance_allowlist.json: template phrases) and GLOBAL_OK only.
GLOBAL_OK = {"list_numbering", "names", "identifiers", "statistical_conventions", "inline_citation"}


def _allow_entries() -> list[dict]:
    out = json.loads(ALLOWLIST.read_text())["entries"] if ALLOWLIST.exists() else []
    if PROSE_ALLOWLIST.exists():
        out += json.loads(PROSE_ALLOWLIST.read_text())["entries"]
    return out


def _entries_for(entries: list[dict], kind: str, path: str | None) -> list[dict]:
    from fnmatch import fnmatch
    if kind != "authored":                     # template / chart / table text: the layer-2 entries (template phrases)
        return [e for e in entries if "paths" not in e or e["id"] in GLOBAL_OK]
    return [e for e in entries if e["id"] in GLOBAL_OK
            or (e.get("paths") and e["paths"] != ["*"] and path and any(fnmatch(path, g) for g in e["paths"]))]


def _allowed(span, text, entries) -> bool:
    s0, s1 = span
    for e in entries:
        for m in re.finditer(e["regex"], text, re.I | re.M):
            if m.start() <= s0 and m.end() >= s1:
                if e.get("deny_if_sentence"):
                    a = text.rfind(".", 0, m.start()) + 1
                    b = text.find(".", m.end())
                    if re.search(e["deny_if_sentence"], text[a:b if b > 0 else None], re.I):
                        continue
                return True
    return False


# Non-prose spans blanked before tokenising: CSS / HTML markup, URLs, file paths and code identifiers
# (snake_case / dotted names such as chg_12m, T_roll_p75, hy_ig_pctrank_1260d), colour codes.
NON_PROSE = [re.compile(p, re.S | re.I) for p in (
    r"<style.*?</style>", r"<[^>]+>", r"https?://\S+", r"#[0-9a-f]{3,6}\b",
    r"[\w.-]*/[\w./{}<>-]+", r"\b[\w.-]+\.(?:csv|json|py|parquet|png|md)\b",
    r"\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9.]+)+\b")]


def strip_non_prose(text: str) -> str:
    for rx in NON_PROSE:
        text = rx.sub(lambda m: " " * len(m.group(0)), text)
    return text


def check_text(text: str, pool: dict, entries: list[dict], where: str = "") -> list[str]:
    """v1 value check of plain text (no markers: every token is template-classified and value-matched)."""
    return check_tagged(text, pool, entries, {}, where)[0]


def _ctx(text: str, m) -> str:
    return text[max(0, m.start() - 60): m.end() + 40].replace("\n", " ")


def coincidence(pool: dict, n: int = 3000, seed: int = 7) -> float:
    """Share of random plausible tokens that resolve by coincidence (residual-risk measure)."""
    rng = random.Random(seed)
    hit = 0
    for i in range(n):
        k = i % 3
        if k == 0:
            v, d, p = round(rng.uniform(-3, 3), 2), 2, False
        elif k == 1:
            v, d, p = round(rng.uniform(0, 100), 1), 1, True
        else:
            v, d, p = float(rng.randint(1, 300)), 0, False
        hit += resolves(v, d, p, pool, signed=v < 0)
    return hit / n


# ----------------------------------------------------------------------------------------------- render
def _page_file(pair: str, section: str) -> Path | None:
    hits = sorted((APP / "pages").glob(f"*_{pair}_{section}.py"))
    return hits[0] if hits else None


CHART_SCOPE = ("every visible Plotly string is checked (titles, axis / colorbar titles, tick text, annotations, "
               "shape labels, legend, trace names, text / texttemplate labels, hover text / hovertemplates, "
               "category labels); raw numeric data arrays (the plotted values themselves) are NOT (disclosed gap)")
VISIBLE_KEYS = {"text", "texttemplate", "hovertext", "hovertemplate", "ticktext", "name", "label", "title",
                "prefix", "suffix"}
_PLACEHOLDER = re.compile(r"%\{[^}]*\}|<extra>.*?</extra>", re.S)
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ][\d:.]+)?$")


def _chart_texts(spec: str) -> list[str]:
    """Every visible string of a Plotly figure (Codex L2v2 F3, L2v3 N3): see CHART_SCOPE. Format placeholders
    (%{y:.2f}) are removed; category values of x / y / z arrays are included (ISO timestamps are data)."""
    try:
        fig = json.loads(spec)
    except (TypeError, ValueError):
        return []
    out: list[str] = []

    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in VISIBLE_KEYS or k in ("x", "y", "z", "labels"):
                    walk(v, k)
                elif isinstance(v, (dict, list)):
                    walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and key is not None:
            if key in ("x", "y", "z") and _ISO.match(o):
                return
            if key in VISIBLE_KEYS or key in ("x", "y", "z", "labels"):
                t = _PLACEHOLDER.sub(" ", o).strip()
                if t:
                    out.append(t)
    walk(fig)
    return out


def _texts(node, out: list):
    """(kind, text) of every rendered element: 'table' for st.table / st.dataframe rows, 'chart' for the visible
    text of a Plotly chart, else 'prose'."""
    ch = getattr(node, "children", None)
    if isinstance(ch, dict):
        for c in ch.values():
            _texts(c, out)
    typ = getattr(node, "type", None)
    if typ == "metric":
        out.append(("metric", f"{node.label}: {node.value} {getattr(node, 'delta', '') or ''}"))
        return
    if typ in ("table", "dataframe", "arrow_data_frame"):
        try:
            df = node.value
            out.append(("table", " | ".join(str(c) for c in df.columns)))
            out.extend(("table", " | ".join(str(x) for x in row)) for row in df.astype(str).itertuples(index=False))
        except Exception:
            pass
        return
    if typ == "plotly_chart":
        out.extend(("chart", t) for t in _chart_texts(getattr(getattr(node, "proto", None), "spec", "")))
        return
    if typ in ("text_input", "selectbox", "radio", "checkbox", "button"):
        return
    try:
        v = node.value
    except Exception:
        return
    if isinstance(v, str):
        out.append(("prose", v))


APPROVED_DEF_ATTRS = {"_DATA_SOURCES_MD", "_METHODS_TABLE_MD", "_GRID_TABLE_MD", "_INDICATOR_CONSTRUCTION_MD"}
_APPROVED: dict[str, set] = {}


def approved_definitions(mod) -> set[str]:
    """Raw texts a config may mark as definitions (Codex L2v2 F10): the values of its *_TEXT dicts and the
    approved methodology blocks (APPROVED_DEF_ATTRS), as they were built (with their inner sentinels)."""
    from components.provenance import DefText
    out = set()
    for name, obj in vars(mod).items():
        if name.endswith("_TEXT") and isinstance(obj, dict):
            out |= {str.__str__(v) for v in obj.values() if isinstance(v, DefText)}
        elif name in APPROVED_DEF_ATTRS and isinstance(obj, DefText):
            out.add(str.__str__(obj))
    return out


def _mark_authored(mod) -> None:
    """Wrap every prose string a pair config hands to the templates in authored-text markers carrying its
    attribute path (A0 <path> AP <text> A1), in place: attributes of the config classes / objects and module-level
    dicts / lists (block dicts), recursively. Identifier-like strings (no whitespace) are left alone."""
    import inspect

    from components.provenance import A0, A1, AP, DefText

    def wrap(v, path):
        if isinstance(v, str) and not isinstance(v, DefText) and re.search(r"\s", v) and A0 not in v:
            return f"{A0}{path}{AP}{v}{A1}"
        if isinstance(v, dict):
            for k in list(v):
                v[k] = wrap(v[k], f"{path}[{k}]")
        elif isinstance(v, list):
            v[:] = [wrap(x, path) for x in v]
        return v

    for name, obj in list(vars(mod).items()):
        if name.startswith("__") or name.endswith("_TEXT") or inspect.ismodule(obj) or inspect.isfunction(obj):
            continue
        if inspect.isclass(obj):
            if obj.__module__ == mod.__name__:
                for a, v in list(vars(obj).items()):
                    if not a.startswith("__") and not callable(v):
                        setattr(obj, a, wrap(v, f"{obj.__name__}.{a}"))
        elif isinstance(obj, (dict, list)) and not name.startswith("_"):   # public block dicts / lists only
            wrap(obj, name)
        elif hasattr(obj, "__dict__") and not inspect.isclass(obj) \
                and type(obj).__module__ in (mod.__name__, "components.page_templates"):   # config objects only
            # (never shared helper objects such as the cached WinnerFields: marking them would leak into
            # every later render in the process)
            for a, v in list(vars(obj).items()):
                setattr(obj, a, wrap(v, f"{name}.{a}"))


def _drop_config(modname: str) -> None:
    """Forget a (possibly marked) config module completely: sys.modules AND the attribute on its parent package
    (Codex L2v2 F11: `import pair_configs.x` would otherwise hand back the marked module)."""
    sys.modules.pop(modname, None)
    pkg, _, leaf = modname.rpartition(".")
    if pkg in sys.modules and hasattr(sys.modules[pkg], leaf):
        delattr(sys.modules[pkg], leaf)


def render_pages(pair: str, sections=SECTIONS, tagged: bool = True, prepare=None) -> dict[str, list[tuple[str, str]]]:
    """{section: [(kind, text)]} of the pair's pages, rendered in-process (AppTest). tagged: render with
    provenance sentinels on (AIG_PROVENANCE_GATE=1) and the pair config's prose marked as authored text."""
    import importlib

    from streamlit.testing.v1 import AppTest
    if str(APP) not in sys.path:
        sys.path.insert(0, str(APP))
    modname = f"pair_configs.{pair}_config"
    old_env = os.environ.get("AIG_PROVENANCE_GATE")
    out = {}
    cwd = os.getcwd()
    try:
        _drop_config(modname)
        if tagged:
            os.environ["AIG_PROVENANCE_GATE"] = "1"
            os.chdir(APP)
            mod = importlib.import_module(modname)
            if prepare is not None:              # tests: edit the imported config before it is marked
                prepare(mod)
            _APPROVED[pair] = approved_definitions(mod)
            _mark_authored(mod)
        else:
            os.environ.pop("AIG_PROVENANCE_GATE", None)
        for sec in sections:
            pf = _page_file(pair, sec)
            if pf is None:
                continue
            code = ("import streamlit as st, runpy\n"
                    "st.page_link = lambda *a, **k: None\n"          # multipage links need the full app router
                    f"runpy.run_path({str(pf)!r}, run_name='__main__')\n")
            os.chdir(APP)
            at = AppTest.from_string(code, default_timeout=180).run()
            if at.exception:
                out[sec] = [("prose", f"RENDER-EXCEPTION {e.message}") for e in at.exception]
                continue
            blocks: list = []
            _texts(at._tree, blocks)
            out[sec] = blocks
    finally:
        os.chdir(cwd)
        if old_env is None:
            os.environ.pop("AIG_PROVENANCE_GATE", None)
        else:
            os.environ["AIG_PROVENANCE_GATE"] = old_env
        _drop_config(modname)                     # the marked module never serves a later render
    return out


# ------------------------------------------------------------------------------------------- tagged analysis
def parse_markers(text: str):
    """(clean text, kinds, paths, sentinels, definitions) of a rendered block.
    kinds[i] in {'template', 'authored', 'definition', 'value'}; paths[i] = config attribute path of authored text;
    sentinels = (start, end, source, unit, shown) in clean coordinates; definitions = raw text of every definition
    span. A block that opens with an authored-close marker (a template split a config string) starts authored."""
    from components.provenance import A0, A1, AP, D0, D1, S0, S1, S2, U
    marks = (A0, A1, AP, D0, D1, S0, S1, S2, U)
    first = min([i for i in (text.find(A0), text.find(A1)) if i >= 0], default=-1)
    authored = first >= 0 and text[first] == A1
    path = None
    dfn, dstart, defs = 0, None, []
    clean, kinds, paths, sents = [], [], [], []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == A0:
            authored = True
            k = text.find(AP, i)
            if k > i and A1 not in text[i:k]:
                path, i = text[i + 1:k], k + 1
                continue
        elif ch == A1:
            authored, path = False, None
        elif ch == D0:
            if dfn == 0:
                dstart = i + 1
            dfn += 1
        elif ch == D1:
            dfn = max(0, dfn - 1)
            if dfn == 0 and dstart is not None:
                defs.append(text[dstart:i])
                dstart = None
        elif ch == S0:
            j = text.find(S1, i)
            k = text.find(S2, j)
            if j < 0 or k < 0:
                i += 1
                continue
            head = text[i + 1:j]
            src, _, unit = head.partition(U)
            shown = text[j + 1:k]
            for c in marks:
                shown = shown.replace(c, "")
            start = len(clean)
            clean.extend(shown)
            kinds.extend(["value"] * len(shown))
            paths.extend([path] * len(shown))
            sents.append((start, len(clean), src, unit or "raw", shown))
            i = k + 1
            continue
        else:
            clean.append(ch)
            kinds.append("definition" if dfn else ("authored" if authored else "template"))
            paths.append(path)
        i += 1
    return "".join(clean), kinds, paths, sents, defs


def _numbers(text: str):
    """Numeric tokens of a span (values, decimals, percent, explicit sign) — dates excluded."""
    body = DATE.sub(lambda m: " " * len(m.group(0)), text)
    return [(_value(m.group(0)), m.group(0)) for m in NUM.finditer(body) if _value(m.group(0))]


_SPEC_POOL: dict[str, set] = {}


def spec_numbers(pair: str) -> set[float]:
    """Numbers the pair DECLARES outside its config (Codex L2v3 N4): every numeric literal and every number inside
    a string literal of scripts/pair_spec_<pair>.py and scripts/pair_pipeline_<pair>.py (windows, thresholds,
    quantiles, lags, display names such as '60-month z-score'), the candidates manifest and the registry entry.
    Definition text and categorical field labels may show only these numbers (a percentile 'p75' / '75th' also
    matches 0.75)."""
    if pair in _SPEC_POOL:
        return _SPEC_POOL[pair]
    import ast as _ast
    nums: set[float] = set()
    for f in (REPO / "scripts" / f"pair_spec_{pair}.py", REPO / "scripts" / f"pair_pipeline_{pair}.py"):
        if not f.exists():
            continue
        for n in _ast.walk(_ast.parse(f.read_text())):
            if isinstance(n, _ast.Constant):
                if isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
                    nums.add(float(n.value))
                elif isinstance(n.value, str):
                    nums |= {float(x) for x in re.findall(r"\d+(?:\.\d+)?", n.value)}
    extra: list = []
    try:
        _walk(json.loads((RESULTS / pair / f"candidates_manifest_{load_tag(pair)}.json").read_text()), extra, [])
    except (OSError, KeyError, ValueError):
        pass
    try:
        _walk(json.loads(REGISTRY.read_text())["pairs"][pair], extra, [])
    except (OSError, KeyError):
        pass
    nums |= {float(x) for x in extra}
    nums |= {round(x * 100, 6) for x in list(nums) if 0 < x < 1}          # p75 / 75th percentile <-> 0.75
    _SPEC_POOL[pair] = nums
    return nums


def _declared(tok: str, pair: str | None) -> bool:
    val = _value(tok)
    if val is None or pair is None:
        return False
    x = abs(val[0])
    return any(abs(x - v) < 1e-9 for v in spec_numbers(pair))


def reconcile_field(name: str, fields: dict, pair: str | None = None) -> str | None:
    """winner_fields text vs value (Codex L2v2 F6): every number the text shows must be the value (x 100 for a
    percent, any element of a list value, a digit run of a string value); a number word must equal the value."""
    f = fields.get(name)
    if not f:
        return f"winner field {name!r} does not exist"
    val, text = f.get("value"), str(f.get("text", ""))
    if isinstance(val, bool) or val is None:
        return None
    toks = _numbers(text)
    if isinstance(val, (int, float)):
        vals = [float(val)]
    elif isinstance(val, list) and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in val):
        vals = [float(x) for x in val]
    elif isinstance(val, str):
        # a categorical field (code / display label): each number in the text must be in the value itself or be
        # a number the pair spec / pipeline declares (the '60' of a '60-month z-score' label; Codex L2v3 note)
        digits = re.findall(r"\d+", val)
        bad = [t for (_, t) in toks if re.sub(r"\D", "", t.split(".")[0]) not in digits
               and not any(re.sub(r"\D", "", t) in d for d in digits) and not _declared(t, pair)]
        return f"field {name}: text {text!r} shows {bad} not in its value {val!r}" if bad and not DATE.fullmatch(val) \
            else None
    else:
        return None
    if not toks:
        w = WORD.search(text)
        if w and float(word_value(w)) not in vals:
            return f"field {name}: text {text!r} (= {word_value(w)}) != value {val!r}"
        return None
    for (x, d, pct), t in toks:                 # sign-sensitive (Codex L2v3 N5)
        tol = 0.5 * 10 ** -d + 1e-9
        if not any(abs(((v * 100) if pct else v) - x) <= tol for v in vals):
            return f"field {name}: text {text!r} shows {t} but its value is {val!r}"
    return None


def verify_sentinel(src: str, unit: str, shown: str, fields: dict, pair: str | None) -> str | None:
    """None when the displayed text equals its source at displayed precision, else the reason. Every number in
    the span is checked against the one source value, in the declared unit (Codex L2v2 F7)."""
    from components import provenance as P
    try:
        val = P.evaluate(src, fields, pair)
    except Exception as e:                              # noqa: BLE001 - an unresolvable source is a finding
        return f"source {src!r} does not resolve ({type(e).__name__}: {e})"
    if src.startswith("wf:"):
        r = reconcile_field(src[3:], fields, pair)
        if r:
            return r
        return None if val == shown else f"text {shown!r} != {src} {val!r}"
    if isinstance(val, str):
        return None if val == shown else f"text {shown!r} != {src} {val!r}"
    try:
        kind = P.kind_of(src, pair)
    except Exception as e:                              # noqa: BLE001 - invalid unit arithmetic is a finding
        return f"source {src!r} is not unit-correct ({e})"
    if unit == "pct" and kind not in P.RATIO_KINDS:
        return f"shows {shown!r} as a percent but {src} is a {kind} (only ratios may be shown x 100)"
    toks = _numbers(shown.replace("−", "-"))
    if not toks:
        return None if not re.search(r"\d", shown) else f"shows {shown!r} for numeric {src}"
    try:
        e = float(val)
    except (TypeError, ValueError):
        return f"source {src!r} is not numeric"
    if len(toks) > 1:
        return f"shows {shown!r}: {len(toks)} numbers in one tagged value ({src})"
    (x, d, _pct), t = toks[0]
    target = e * 100 if unit == "pct" else e
    tol = 0.5 * 10 ** -d + 1e-9
    return None if abs(target - x) <= tol else f"shows {shown!r} but {src} = {target:.6g} ({unit})"


# Headline / confidence surfaces whose numbers must be TAGGED even in shared-template text (Lead ruling on L2v3
# N6): KPI metrics for Sharpe / return / drawdown / win rate, the vs-buy-and-hold facts, the chance check, the
# revised-data caption and the executive summary lines.
HEADLINE = re.compile(r"^(?:[^\n:]*(?:Sharpe|Return|Drawdown|Win Rate)[^\n:]*:)|The test-period Sharpe difference|"
                      r"Test-period Sharpe was below|Winner on revised data|scrambled-signal contests|"
                      r"Contests: \d|\*\*Chance check\.\*\*|Annual return was")


def check_tagged(text: str, pool: dict, entries: list[dict], fields: dict, where: str,
                 pair: str | None = None, approved: set | None = None,
                 headline: bool = False) -> tuple[list[str], dict]:
    """Layer 2 v2 on one rendered block. Authored numbers must sit in a verified sentinel, an approved definition
    span or a path-bound allowlist span; template text keeps the value-matching fallback (sign-sensitive for
    explicitly signed tokens). Returns (findings, counters)."""
    clean, kinds, paths, sents, defs = parse_markers(text)
    out, cnt = [], {"authored_tokens": 0, "template_tokens": 0, "tagged_values": len(sents)}
    for a, b, src, unit, shown in sents:
        r = verify_sentinel(src, unit, shown, fields, pair)
        if r:
            out.append(f"MISMATCH {where}: {r}")
    for d in defs:
        if approved is not None and d not in approved:
            out.append(f"DEFINITION {where}: definition text not from an approved definition field — "
                       f"\"{d[:100]}\"")
    body = strip_non_prose(clean)
    for m in NONASCII_NUM.finditer(clean):
        out.append(f"NUMERAL {where}: non-ASCII numeral {m.group(0)!r} — \"{_ctx(clean, m)}\"")
    spans = []
    for rx in (DATE, ORDINAL, NUM, WORD):
        for m in rx.finditer(body):
            if any(s <= m.start() < e for s, e in spans):
                continue
            spans.append(m.span())
            span_ix = range(m.start(), m.end())
            has_digit = any(body[i].isdigit() for i in span_ix)
            digits = [kinds[i] for i in span_ix if (body[i].isdigit() if has_digit else body[i].isalnum())] \
                or kinds[m.start():m.end()]
            k = set(digits)
            if k <= {"value"}:
                continue
            if "definition" in k and k <= {"definition", "value"}:
                # definition text may show only numbers the pair declares outside its config (Codex L2v3 N4)
                if rx is DATE or _declared(m.group(1) if rx is ORDINAL else m.group(0), pair) or \
                        (rx is WORD and pair is not None and float(word_value(m)) in spec_numbers(pair)):
                    continue
                out.append(f"DEFINITION {where}: definition number {m.group(0)!r} is not a parameter the pair "
                           f"spec / pipeline declares — \"{_ctx(body, m)}\"")
                continue
            if rx is WORD and m.group("small") and m.group("small").lower() in ("one", "zero") \
                    and not UNIT_AFTER.match(body, m.end()):
                continue                               # 'one of', 'near zero': not a quantity
            kind = "authored" if "authored" in k else "template"
            path = next((paths[i] for i in range(m.start(), m.end()) if paths[i]), None)
            ents = _entries_for(entries, kind, path)
            if _allowed(m.span(), clean, ents):
                cnt[f"{kind}_tokens"] += 1
                continue
            cnt[f"{kind}_tokens"] += 1
            if kind == "authored":
                out.append(f"UNTAGGED {where}{f' [{path}]' if path else ''}: authored number {m.group(0)!r} is not "
                           f"from a field or artifact — \"{_ctx(body, m)}\"")
            elif headline and rx in (NUM, ORDINAL) and not (re.fullmatch(r"(?:19|20)\d\d", m.group(0))):
                out.append(f"HEADLINE {where}: untagged template number {m.group(0)!r} on a headline surface — "
                           f"\"{_ctx(body, m)}\"")
            elif not _resolve_token(m, rx, pool, body):
                out.append(f"UNRESOLVED {where}: template number {m.group(0)!r} — \"{_ctx(body, m)}\"")
            else:
                cnt.setdefault("template_blocks", set()).add(body.strip()[:70].replace("\n", " "))
    return out, cnt


def _resolve_token(m, rx, pool, body: str = "") -> bool:
    """Value-matching fallback for template text (the v1 rule; explicit signs must agree)."""
    tok = m.group(0)
    if rx is DATE:
        return tok in pool["dates"]
    if rx is ORDINAL:
        return resolves(int(m.group(1)), 0, True, pool)
    if rx is WORD:
        v = float(word_value(m))
        return resolves(v, 0 if v.is_integer() else 2, False, pool)
    val = _value(tok)
    if val is None:
        return True
    v, d, pct = val
    pct = pct or bool(re.match(r"\s?pp\b", body[m.end():m.end() + 4]))
    if d == 0 and not pct and 1900 <= abs(v) <= 2100 and str(int(abs(v))) in pool["years"]:
        return True
    return resolves(v, d, pct, pool, signed=tok.lstrip("$")[:1] in "+-−")


# ------------------------------------------------------------------------------------------------- main
def pairs_13() -> list[str]:
    out = []
    for ws in sorted(RESULTS.glob("*/winner_summary.json")):
        try:
            if str(json.loads(ws.read_text()).get("schema_version", "")).startswith("1.3"):
                out.append(ws.parent.name)
        except (OSError, json.JSONDecodeError):
            pass
    return out


def load_table_pool(pair: str, pool: dict) -> dict:
    """Data tables (st.table / st.dataframe) display artifact rows directly; their cells resolve against the
    curated pool plus every number in the pair's CURRENT result files (latest date tag or untagged, CSV / JSON)."""
    import pandas as pd
    rdir = RESULTS / pair
    tag = load_tag(pair)
    nums, strs = list(pool["nums"]), []
    for f in sorted(rdir.rglob("*")):
        if f.suffix not in (".csv", ".json") or not f.is_file():
            continue
        tags = re.findall(r"(?<!\d)(20\d{6})(?!\d)", str(f.relative_to(rdir)))
        if tags and any(t != tag for t in tags):
            continue
        try:
            if f.suffix == ".json":
                _walk(json.loads(f.read_text()), nums, strs)
            else:
                df = pd.read_csv(f)
                nums += [float(x) for x in df.select_dtypes("number").to_numpy().ravel() if pd.notna(x)]
                strs += [str(x) for x in df.select_dtypes(exclude="number").to_numpy().ravel()][:20000]
        except Exception:
            continue
    dates = set(pool["dates"])
    for s_ in strs:
        for m in DATE.finditer(s_):
            dates.update({m.group(0), m.group(0)[:7]})
    return {"nums": sorted(set(nums)), "dates": dates, "years": {d[:4] for d in dates}, "files": []}


def load_tag(pair: str) -> str:
    ws = json.loads((RESULTS / pair / "winner_summary.json").read_text())
    return ws["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")


def check_pair(pair: str, pages: dict | None = None) -> tuple[list[str], dict]:
    pool = load_pool(pair)
    tpool = None
    entries = _allow_entries()
    pages = render_pages(pair) if pages is None else pages
    fields = json.loads((RESULTS / pair / "winner_summary.json").read_text()).get("winner_fields") or {}
    approved = _APPROVED.get(pair)
    findings, tot = [], {"authored_tokens": 0, "template_tokens": 0, "tagged_values": 0}
    blocks_seen: set[str] = set()
    for sec, blocks in pages.items():
        for kind, b in blocks:
            if b.startswith("RENDER-EXCEPTION"):
                findings.append(f"{pair}/{sec}: {b}")
                continue
            if kind in ("table", "chart"):      # sentinel-verified like prose; value fallback on current results
                tpool = tpool or load_table_pool(pair, pool)
                f, c = check_tagged(b, tpool, entries, fields, f"{pair}/{sec} [{kind}]", pair, approved)
            else:
                head = bool(HEADLINE.search(parse_markers(b)[0]))
                f, c = check_tagged(b, pool, entries, fields, f"{pair}/{sec}", pair, approved, head)
            findings += f
            for k in tot:
                tot[k] += c[k]
            blocks_seen.update(f"{sec}: {x}" for x in c.get("template_blocks", ()))
    stats = {"tokens_pool": len(pool["nums"]), "coincidence_template": round(coincidence(pool), 3),
             "files": pool["files"], "template_blocks": sorted(blocks_seen), **tot}
    return findings, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pairs", nargs="*")
    ap.add_argument("--text", help="check this text file against --pair's pool (fixtures)")
    ap.add_argument("--pair")
    a = ap.parse_args(argv)
    if a.text:
        f = check_text(Path(a.text).read_text(), load_pool(a.pair), _allow_entries(), a.pair)
        print("\n".join(f) or "OK")
        return 1 if f else 0
    hard = 0
    for p in a.pairs or pairs_13():
        f, st = check_pair(p)
        print(f"[{'FAIL' if f else 'OK  '}] {p}: {len(f)} unresolved; pool {st['tokens_pool']} values from "
              f"{', '.join(Path(x).name for x in st['files'])} + registry; {st['tagged_values']} tagged values, "
              f"{st['authored_tokens']} untagged authored tokens (allowlisted or failing), {st['template_tokens']} "
              f"template tokens (value-matched; coincidence {st['coincidence_template']:.1%})")
        for x in f:
            print("     ", x[:260])
        if st.get("template_blocks"):
            print(f"      template text value-matched (disclosed residual, coincidence "
                  f"{st['coincidence_template']:.1%}): {len(st['template_blocks'])} block(s)")
            for b in st["template_blocks"]:
                print("        -", b[:110])
        hard += len(f)
    print(f"\nGATE-NUMBER-PROVENANCE: {hard} unresolved number(s). Charts: {CHART_SCOPE}.")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
