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

NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split())}
NUMBER_WORDS.update({"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "hundred": 100, "dozen": 12,
                     "half": 0.5, "quarter of": 0.25, "third of": 1 / 3})
ORDINAL_WORDS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
                 "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12}
DATE = re.compile(r"\b(\d{4})-(\d{2})(?:-(\d{2}))?\b")
NUM = re.compile(r"(?<![\w.])[-+−]?\$?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?"
                 r"|(?<![\w.])[-+−]?\$?\d+(?:\.\d+)?(?:e[-+]?\d+)?%?"
                 r"|(?<=[A-Za-z])\d+(?:\.\d+)?(?=\b)")
ORDINAL = re.compile(r"\b(\d+)(?:st|nd|rd|th)\b")
WORD = re.compile(r"\b(" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + r")\b", re.I)


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
             rdir / f"candidates_manifest_{tag}.json"]
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


def resolves(v: float, d: int, pct: bool, pool: dict, is_int_word=False) -> bool:
    """Percent tokens (and ordinals, passed as pct) match a pool value or 100x a pool value at the printed
    precision; bare integers match integer-valued pool numbers exactly (so "5" is not "any value in
    [4.5, 5.5)"); decimals match at their printed precision. Signs are ignored (prose writes magnitudes)."""
    av = abs(v)
    if pct:
        tol = 0.5 * 10 ** -d + 1e-9
        return any(abs(abs(a) - av) <= tol or abs(abs(a) * 100 - av) <= tol for a in pool["nums"])
    if d == 0:
        return any(float(abs(a)).is_integer() and abs(a) == av for a in pool["nums"])
    tol = 0.5 * 10 ** -d + 1e-9
    return any(abs(abs(a) - av) <= tol for a in pool["nums"])


def _allow_entries() -> list[dict]:
    out = json.loads(ALLOWLIST.read_text())["entries"] if ALLOWLIST.exists() else []
    if PROSE_ALLOWLIST.exists():
        out += [e for e in json.loads(PROSE_ALLOWLIST.read_text())["entries"] if e["paths"] == ["*"]]
    return out


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
    """Unresolved numeric tokens of one rendered text block."""
    text = strip_non_prose(text)
    out, taken = [], []
    for m in DATE.finditer(text):
        taken.append(m.span())
        if m.group(0) not in pool["dates"] and not _allowed(m.span(), text, entries):
            out.append(f"UNRESOLVED {where}: date {m.group(0)} — \"{_ctx(text, m)}\"")
    for m in ORDINAL.finditer(text):
        taken.append(m.span())
        v = int(m.group(1))
        if not (resolves(v, 0, True, pool) or _allowed(m.span(), text, entries)):
            out.append(f"UNRESOLVED {where}: ordinal {m.group(0)} — \"{_ctx(text, m)}\"")
    for m in NUM.finditer(text):
        if any(a <= m.start() < b for a, b in taken):
            continue
        val = _value(m.group(0))
        if val is None:
            continue
        v, d, pct = val
        pct = pct or bool(re.match(r"\s?pp\b", text[m.end():m.end() + 4]))   # percentage points
        if d == 0 and not pct and 1900 <= abs(v) <= 2100 and str(int(abs(v))) in pool["years"]:
            continue
        if resolves(v, d, pct, pool) or _allowed(m.span(), text, entries):
            continue
        out.append(f"UNRESOLVED {where}: number {m.group(0)} — \"{_ctx(text, m)}\"")
    for m in WORD.finditer(text):
        w = m.group(1).lower()
        if w in ("one", "a") or _allowed(m.span(), text, entries):
            continue
        if not resolves(float(NUMBER_WORDS[w]), 0 if float(NUMBER_WORDS[w]).is_integer() else 2, False, pool):
            out.append(f"UNRESOLVED {where}: number word '{m.group(1)}' — \"{_ctx(text, m)}\"")
    return out


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
        hit += resolves(v, d, p, pool)
    return hit / n


# ----------------------------------------------------------------------------------------------- render
def _page_file(pair: str, section: str) -> Path | None:
    hits = sorted((APP / "pages").glob(f"*_{pair}_{section}.py"))
    return hits[0] if hits else None


def _texts(node, out: list):
    """(kind, text) of every rendered element: kind 'table' for st.table / st.dataframe rows, else 'prose'."""
    ch = getattr(node, "children", None)
    if isinstance(ch, dict):
        for c in ch.values():
            _texts(c, out)
    typ = getattr(node, "type", None)
    if typ == "metric":
        out.append(("prose", f"{node.label}: {node.value} {getattr(node, 'delta', '') or ''}"))
        return
    if typ in ("table", "dataframe", "arrow_data_frame"):
        try:
            df = node.value
            out.append(("table", " | ".join(str(c) for c in df.columns)))
            out.extend(("table", " | ".join(str(x) for x in row)) for row in df.astype(str).itertuples(index=False))
        except Exception:
            pass
        return
    if typ in ("text_input", "selectbox", "radio", "checkbox", "button"):
        return
    try:
        v = node.value
    except Exception:
        return
    if isinstance(v, str):
        out.append(("prose", v))


def _mark_authored(mod) -> None:
    """Wrap every prose string a pair config hands to the templates in authored-text markers (A0 .. A1), in place:
    attributes of the config classes / objects and module-level dicts / lists (block dicts), recursively.
    Identifier-like strings (no whitespace: chart names, paths, codes) are left alone."""
    import inspect

    from components.provenance import A0, A1, DefText

    def wrap(v):
        if isinstance(v, str) and not isinstance(v, DefText) and re.search(r"\s", v) and A0 not in v:
            return f"{A0}{v}{A1}"
        if isinstance(v, dict):
            for k in list(v):
                v[k] = wrap(v[k])
        elif isinstance(v, list):
            v[:] = [wrap(x) for x in v]
        return v

    for name, obj in list(vars(mod).items()):
        if name.startswith("__") or name.endswith("_TEXT") or inspect.ismodule(obj) or inspect.isfunction(obj):
            continue
        if inspect.isclass(obj):
            if obj.__module__ == mod.__name__:
                for a, v in list(vars(obj).items()):
                    if not a.startswith("__") and not callable(v):
                        setattr(obj, a, wrap(v))
        elif isinstance(obj, (dict, list)):
            wrap(obj)
        elif hasattr(obj, "__dict__") and not inspect.isclass(obj):      # config objects (own or template classes)
            for a, v in list(vars(obj).items()):
                setattr(obj, a, wrap(v))


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
        if tagged:
            os.environ["AIG_PROVENANCE_GATE"] = "1"
            sys.modules.pop(modname, None)
            os.chdir(APP)
            mod = importlib.import_module(modname)
            if prepare is not None:              # tests: edit the imported config before it is marked
                prepare(mod)
            _mark_authored(mod)
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
        if tagged:
            sys.modules.pop(modname, None)      # the marked module never serves a normal render
    return out


# ------------------------------------------------------------------------------------------- tagged analysis
def parse_markers(text: str):
    """(clean text, per-char kind list, value sentinels) of a rendered block. kind: 'template' | 'authored' |
    'definition' | 'value'; sentinels: (start, end, source expression, displayed text) in clean coordinates.
    A block that opens with an authored-close marker (a template split a config string) starts authored."""
    from components.provenance import A0, A1, D0, D1, S0, S1, S2
    first = min([i for i in (text.find(A0), text.find(A1)) if i >= 0], default=-1)
    authored = first >= 0 and text[first] == A1
    dfn = 0
    clean, kinds, sents = [], [], []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == A0:
            authored = True
        elif ch == A1:
            authored = False
        elif ch == D0:
            dfn += 1
        elif ch == D1:
            dfn = max(0, dfn - 1)
        elif ch == S0:
            j = text.find(S1, i)
            k = text.find(S2, j)
            if j < 0 or k < 0:
                i += 1
                continue
            src, shown = text[i + 1:j], text[j + 1:k]
            for c in (A0, A1, D0, D1, S0, S1, S2):
                shown = shown.replace(c, "")
            start = len(clean)
            clean.extend(shown)
            kinds.extend(["value"] * len(shown))
            sents.append((start, len(clean), src, shown))
            i = k + 1
            continue
        else:
            clean.append(ch)
            kinds.append("definition" if dfn else ("authored" if authored else "template"))
        i += 1
    return "".join(clean), kinds, sents


def verify_sentinel(src: str, shown: str, fields: dict) -> str | None:
    """None when the displayed text equals its source at displayed precision, else the reason."""
    from components import provenance as P
    try:
        val = P.evaluate(src, fields)
    except Exception as e:                              # noqa: BLE001 - an unresolvable source is a finding
        return f"source {src!r} does not resolve ({type(e).__name__}: {e})"
    if src.startswith("wf:") or isinstance(val, str):
        return None if str(val) == shown else f"text {shown!r} != {src} {str(val)!r}"
    m = NUM.search(shown.replace("\u2212", "-"))
    if not m:
        return None                                     # a non-numeric rendering (n/a)
    v = _value(m.group(0))
    if v is None:
        return None
    x, d, pct = v
    try:
        e = float(val)
    except (TypeError, ValueError):
        return f"source {src!r} is not numeric"
    tol = 0.5 * 10 ** -d + 1e-9
    ok = abs(e - x) <= tol or (pct and abs(e * 100 - x) <= tol)
    return None if ok else f"shows {shown!r} but {src} = {e:.6g}"


def check_tagged(text: str, pool: dict, entries: list[dict], fields: dict, where: str) -> tuple[list[str], dict]:
    """Layer 2 v2 on one rendered block. Authored numbers must sit in a verified sentinel or an allowlist span;
    template text keeps the value-matching fallback. Returns (findings, counters)."""
    clean, kinds, sents = parse_markers(text)
    out, cnt = [], {"authored_tokens": 0, "template_tokens": 0, "tagged_values": len(sents)}
    for a, b, src, shown in sents:
        r = verify_sentinel(src, shown, fields)
        if r:
            out.append(f"MISMATCH {where}: {r}")
    body = strip_non_prose(clean)
    spans = []
    for rx in (DATE, ORDINAL, NUM, WORD):
        for m in rx.finditer(body):
            if any(s <= m.start() < e for s, e in spans):
                continue
            spans.append(m.span())
            # classify by the token's DIGITS (a unit sign such as % or pp written after a tagged value is fine)
            digits = [kinds[i] for i in range(m.start(), m.end()) if body[i].isalnum()] or kinds[m.start():m.end()]
            k = set(digits)
            if k <= {"value"} or "definition" in k and k <= {"definition", "value"}:
                continue
            if rx is WORD and m.group(1).lower() in ("one", "a", "zero"):
                continue
            if "authored" in k:
                cnt["authored_tokens"] += 1
                if not _allowed(m.span(), clean, entries):
                    out.append(f"UNTAGGED {where}: authored number {m.group(0)!r} is not from a field or "
                               f"artifact — \"{_ctx(body, m)}\"")
            else:
                cnt["template_tokens"] += 1
                if not _allowed(m.span(), clean, entries) and not _resolve_token(m, rx, pool):
                    out.append(f"UNRESOLVED {where}: template number {m.group(0)!r} — \"{_ctx(body, m)}\"")
    return out, cnt


def _resolve_token(m, rx, pool) -> bool:
    """Value-matching fallback for template text (the v1 rule)."""
    tok = m.group(0)
    if rx is DATE:
        return tok in pool["dates"]
    if rx is ORDINAL:
        return resolves(int(m.group(1)), 0, True, pool)
    if rx is WORD:
        v = float(NUMBER_WORDS[m.group(1).lower()])
        return resolves(v, 0 if v.is_integer() else 2, False, pool)
    val = _value(tok)
    if val is None:
        return True
    v, d, pct = val
    if d == 0 and not pct and 1900 <= abs(v) <= 2100 and str(int(abs(v))) in pool["years"]:
        return True
    return resolves(v, d, pct, pool)


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
    findings, tot = [], {"authored_tokens": 0, "template_tokens": 0, "tagged_values": 0}
    for sec, blocks in pages.items():
        for kind, b in blocks:
            if b.startswith("RENDER-EXCEPTION"):
                findings.append(f"{pair}/{sec}: {b}")
                continue
            if kind == "table":
                tpool = tpool or load_table_pool(pair, pool)
                findings += check_text(parse_markers(b)[0], tpool, entries, f"{pair}/{sec} [table]")
            else:
                f, c = check_tagged(b, pool, entries, fields, f"{pair}/{sec}")
                findings += f
                for k in tot:
                    tot[k] += c[k]
    stats = {"tokens_pool": len(pool["nums"]), "coincidence_template": round(coincidence(pool), 3),
             "files": pool["files"], **tot}
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
        hard += len(f)
    print(f"\nGATE-NUMBER-PROVENANCE: {hard} unresolved number(s)")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
