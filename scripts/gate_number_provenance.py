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

v5 after QA L2v4 (Lead ruling, bounded): chart and table text is no longer value-matched against every number of
the pair's results (61-89% coincidence). Chart FILES carry a provenance record (scripts/chart_provenance.py: inputs
read by the producer with their sha256, results run tag, chart sha256) and fail as STALE-CHART when any of it no
longer matches the artifacts on disk; shared-template tables name their source file (provenance.table_source) and
every displayed row must be ONE row of that current file (UNRESOLVED-ROW / STALE-TABLE). What is still
value-matched (template prose, charts built at render time, unsourced tables) is printed with its TRUE residual:
random-token coincidence and near-miss stale-Sharpe acceptance against the curated pool. Also: markup / path /
identifier blanking no longer hides numbers; every numeric leaf has a declared, value-consistent kind (percent-
stored leaves are 'percent'); PROVENANCE-API is an allowlist (imports, P.<api>(...) calls only); whitespace-free
strings, tuples / sets, public module strings and callables are marked authored and planted markers removed;
keyed definitions and categorical labels bind to their own code's spec parameters; widget labels, tooltips,
options, tick prefixes / suffixes, customdata and table-trace strings are extracted.

v5.2 after Codex L2v5.1: no value-matching fallback remains (an untagged, non-allowlisted template number FAILS as
UNTAGGED-TEMPLATE whatever its value); sourced-table percent displays may scale x 100 only a ratio-kind column;
derived table columns are checked against a named source column; declared chart inputs must exist and every
producer installs the input recorder before reading data (static test, replaced in v5.3); the trigger-card diagnostic carries no
computed count; the bibliographic allowlist is bound to author-year context.

v5.3 after Codex L2v5.2: each sourced-table cell is checked against the ONE source column its displayed column is
bound to (explicit table_source columns= mapping, else the column whose normalised name is the header; a numeric
cell in an unbound column fails), and x 100 is allowed only when THAT column is ratio-kind (V52-2); a derived
numeric column must name a checker-owned rank rule (RANK_RULES) and equal the rank the checker recomputes from the
score column; None or any other column fails (V52-3); the input recorder is installed at the process entry point
(a repo script re-executes through scripts/_cp_boot.py; aliasing a reader before the import no longer escapes it,
V52-1); both bibliographic arms need an author and a year (V52-4).

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
if str(APP) not in sys.path:                     # components.provenance (markers, loaders) at import time
    sys.path.insert(0, str(APP))
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
                 r"|(?<=[A-Za-z_])\d+(?:\.\d+)?(?=\b)")
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
# (snake_case / dotted names such as chg_12m, T_roll_p75, hy_ig_pctrank_1260d), CSS colour codes.
# v5 (QA L2v4 #3): each pattern is tight enough not to swallow a number: only real HTML tags (not
# 'Sharpe <985.5 and the other >'), URLs end at ')' / ',' / quotes, colour codes only after 'color:' or as an
# attribute value, path segments start with a letter (not '982.22/yr', '988.8/989.9'), an identifier never ends
# in a decimal number ('stale_986.6'), and digits after '_' outside an identifier are tokens (NUM).
NON_PROSE = [re.compile(p, re.S | re.I) for p in (
    r"<style.*?</style>",
    r"</?[A-Za-z][\w-]*(?:\s+[\w:-]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?)*\s*/?>",
    r"https?://[^\s)\],\"'>]+",
    r"(?:colou?r\s*:\s*|=\s*[\"'])#[0-9a-f]{3}(?:[0-9a-f]{3})?\b",
    r"(?<![\w.])(?:[A-Za-z_.{][\w.{}<>-]*/)+[\w.{}<>-]*[A-Za-z_}][\w.{}<>-]*",
    r"\b[\w-]+(?:\.[A-Za-z_]\w*)*\.(?:csv|json|py|parquet|png|md)\b",
    r"\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+(?:\.[A-Za-z_]\w*)*\b(?!\.\d)")]


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


def _accept(pool: set[float], toks: list[float]) -> float:
    return sum(any(abs(t - v) < 1e-9 for v in pool) for t in toks) / len(toks) if toks else 0.0


def coincidence_definition(pair: str, n: int = 3000, seed: int = 7) -> dict:
    """Acceptance of random plausible tokens on the definition path (QA L2v4 #7 token mix): 2-dp decimals,
    1-dp percents, integers 1-300, years, and small integers 1-30 reported separately. 'per_code' averages over
    the spec codes a keyed definition / categorical label is bound to; 'declared' is the unbound fallback pool."""
    rng = random.Random(seed)
    mix = []
    for i in range(n):
        k = i % 4
        mix.append(abs(round(rng.uniform(-3, 3), 2)) if k == 0 else round(rng.uniform(0, 100), 1) if k == 1
                   else float(rng.randint(1, 300)) if k == 2 else float(rng.randint(1990, 2026)))
    small = [float(x) for x in range(1, 31)]
    codes = code_params(pair)
    pc = [(_accept(v, mix), _accept(v, small)) for v in codes.values()] or [(0.0, 0.0)]
    dec = spec_numbers(pair)
    return {"codes": len(codes), "per_code_mix": sum(x for x, _ in pc) / len(pc),
            "per_code_small": sum(y for _, y in pc) / len(pc), "per_code_small_max": max(y for _, y in pc),
            "declared_pool": len(dec), "declared_mix": _accept(dec, mix), "declared_small": _accept(dec, small)}


# ----------------------------------------------------------------------------------------------- render
def _page_file(pair: str, section: str) -> Path | None:
    hits = sorted((APP / "pages").glob(f"*_{pair}_{section}.py"))
    return hits[0] if hits else None


CHART_SCOPE = ("chart FILES are checked by provenance record (chart_provenance.verify: current inputs, current run, "
               "unchanged file), their text is producer output; charts built at render time have every visible "
               "string checked (titles, axis / colorbar titles, tick text and tick prefixes / suffixes, annotations, "
               "shape labels, legend, trace names, text / texttemplate labels, hover text / hovertemplates, "
               "customdata strings, go.Table header / cell strings, category labels); raw numeric data arrays are "
               "not (disclosed gap)")
VISIBLE_KEYS = {"text", "texttemplate", "hovertext", "hovertemplate", "ticktext", "name", "label", "title",
                "prefix", "suffix", "tickprefix", "ticksuffix", "customdata", "values"}
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
            if key in ("x", "y", "z", "customdata", "values") and _ISO.match(o):
                return
            if key in VISIBLE_KEYS or key in ("x", "y", "z", "labels"):
                t = _PLACEHOLDER.sub(" ", o).strip()
                if t:
                    out.append(t)
    walk(fig)
    return out


TABLE_SEP = " \x1f "                    # cells of a rendered table row (cannot occur in cell text)


def _chart_file(spec: str) -> str | None:
    """Repo-relative chart file a rendered figure was loaded from (components.charts._mark_chart_file)."""
    try:
        meta = (json.loads(spec).get("layout") or {}).get("meta")
    except (TypeError, ValueError, AttributeError):
        return None
    return meta.get("aig_chart_file") if isinstance(meta, dict) else None


PROTO_TEXT = ("label", "help", "placeholder", "text")


def _widget_texts(node, typ) -> list[str]:
    """v5 (QA L2v4 #8): visible strings outside an element's body: expander / tab / status labels, widget labels
    and options, help tooltips, placeholders, progress text, image captions, st.html bodies."""
    pr = getattr(node, "proto", None)
    if pr is None or typ == "plotly_chart":
        return []
    out = []
    for f in PROTO_TEXT:
        try:
            v = getattr(pr, f, None)
        except Exception:                               # noqa: BLE001 - proto without the field
            v = None
        if isinstance(v, str) and v.strip():
            out.append(v)
    if typ == "html":
        out.append(getattr(pr, "body", "") or "")
    if typ == "image":
        out.extend(im.caption for im in getattr(pr, "imgs", []) if getattr(im, "caption", ""))
    try:
        opts = getattr(node, "options", None)
    except Exception:                                   # noqa: BLE001
        opts = None
    if isinstance(opts, (list, tuple)):
        out.extend(str(o) for o in opts if isinstance(o, str))
    return [t for t in out if t]


def _texts(node, out: list):
    """(kind, text) of every rendered element: 'table' for st.table / st.dataframe rows, 'chart' for the visible
    text of a Plotly chart, else 'prose'."""
    ch = getattr(node, "children", None)
    if isinstance(ch, dict):
        for c in ch.values():
            _texts(c, out)
    typ = getattr(node, "type", None)
    out.extend(("prose", t) for t in _widget_texts(node, typ))
    if typ == "metric":
        out.append(("metric", f"{node.label}: {node.value} {getattr(node, 'delta', '') or ''}"))
        return
    if typ in ("table", "dataframe", "arrow_data_frame"):
        try:
            df = node.value
            cols = [str(c) for c in df.columns]
            kind = "table"
            from components.provenance import T0, T1
            if cols and T0 in cols[0] and T1 in cols[0]:      # components.provenance.table_source (v5)
                a, b = cols[0].index(T0), cols[0].index(T1)
                kind, cols[0] = f"table@{cols[0][a + 1:b]}", cols[0][:a] + cols[0][b + 1:]
            out.append((kind.replace("table", "tablehead", 1), TABLE_SEP.join(cols)))
            out.extend((kind, TABLE_SEP.join(str(x) for x in row)) for row in df.astype(str).itertuples(index=False))
        except Exception:
            pass
        return
    if typ == "plotly_chart":
        spec = getattr(getattr(node, "proto", None), "spec", "")
        src = _chart_file(spec)
        if src:                                   # loaded from a chart file: provenance-checked (v5)
            out.append(("chart_file", src))
            out.extend(("chart_file_text", t) for t in _chart_texts(spec))
        else:                                     # built at render time by a shared component
            out.extend(("chart", t) for t in _chart_texts(spec))
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
    codes = _DEF_CODE.setdefault(mod.__name__.rpartition(".")[2].removesuffix("_config"), {})
    for name, obj in vars(mod).items():
        if name.endswith("_TEXT") and isinstance(obj, dict):
            out |= {str.__str__(v) for v in obj.values() if isinstance(v, DefText)}
            codes.update({str.__str__(v): str(k) for k, v in obj.items() if isinstance(v, DefText)})
        elif name in APPROVED_DEF_ATTRS and isinstance(obj, DefText):
            out.add(str.__str__(obj))
    return out


_IDENT = re.compile(r"[A-Za-z_][\w./{}-]*")


def declared_identifiers(pair: str) -> set[str]:
    """Identifier strings the pair's artifacts declare (signal / threshold / strategy codes, column and file
    names): a config may carry them without authored marking, because templates use them as lookup keys."""
    out: set[str] = set()
    rdir = RESULTS / pair
    files = [rdir / "winner_summary.json", rdir / "track_summary.json", rdir / "signal_scope.json"]
    files += sorted(rdir.glob("candidates_manifest_*.json"))
    for f in files:
        try:
            strs: list = []
            _walk(json.loads(f.read_text()), [], strs)
            out |= {x for x in strs if _IDENT.fullmatch(x)}
        except (OSError, ValueError):
            pass
    try:
        strs = []
        _walk(json.loads(REGISTRY.read_text())["pairs"][pair], [], strs)
        out |= {x for x in strs if _IDENT.fullmatch(x)}
    except (OSError, KeyError, ValueError):
        pass
    return out


_IDENTS_CACHE: dict = {}


def _IDENTS_RX(pair: str):
    """Regex of the digit-bearing identifiers the pair's artifacts declare (longest first)."""
    if pair not in _IDENTS_CACHE:
        ids = sorted((x for x in declared_identifiers(pair) if re.search(r"\d", x)), key=len, reverse=True)
        _IDENTS_CACHE[pair] = re.compile("|".join(rf"(?<![\w.]){re.escape(x)}(?![\w])" for x in ids) or r"(?!x)x")
    return _IDENTS_CACHE[pair]


def _mark_authored(mod, pair: str | None = None) -> None:
    """Wrap every prose string a pair config hands to the templates in authored-text markers carrying its
    attribute path (A0 <path> AP <text> A1), in place: attributes of the config classes / objects and public
    module-level values (strings, dicts, lists, tuples, sets; recursively), and the text returned by public
    functions / methods / properties of the config. v5 (QA L2v4 #6): a whitespace-free string is wrapped when it
    has a digit unless it is an identifier the pair's artifacts declare ('S=0.43,BH=1.00', '+4.9%', '0.43' are
    authored; 'zscore_60m' is a lookup key); the gate-only marker characters (A0 / A1 / AP / T0 / T1) are removed
    from config text so a planted marker cannot end the authored span."""
    import functools
    import inspect

    from components.provenance import A0, A1, AP, T0, T1, DefText
    idents = declared_identifiers(pair) if pair else set()
    planted = str.maketrans("", "", A0 + A1 + AP + T0 + T1)

    def prose(v: str) -> bool:
        if re.search(r"\s", v):
            return True
        return bool(re.search(r"\d", v)) and v not in idents

    def wrap(v, path):
        if isinstance(v, str) and not isinstance(v, DefText):
            if A0 in v or not prose(v):
                return v
            return f"{A0}{path}{AP}{str.__str__(v).translate(planted)}{A1}"
        if isinstance(v, dict):
            for k in list(v):
                v[k] = wrap(v[k], f"{path}[{k}]")
        elif isinstance(v, list):
            v[:] = [wrap(x, path) for x in v]
        elif isinstance(v, tuple) and not hasattr(v, "_fields"):
            return tuple(wrap(x, path) for x in v)
        elif isinstance(v, (set, frozenset)):
            return type(v)(wrap(x, path) for x in v)
        elif hasattr(v, "__dict__") and type(v).__module__ == mod.__name__ and not inspect.isclass(v):
            for a, x in list(vars(v).items()):
                setattr(v, a, wrap(x, f"{path}.{a}"))
        return v

    def returns_marked(fn, path):
        @functools.wraps(fn)
        def inner(*a, **k):
            return wrap(fn(*a, **k), f"{path}()")
        return inner

    for name, obj in list(vars(mod).items()):
        if name.startswith("__") or name.endswith("_TEXT") or inspect.ismodule(obj):
            continue
        if inspect.isfunction(obj):
            if not name.startswith("_") and obj.__module__ == mod.__name__:
                setattr(mod, name, returns_marked(obj, name))
            continue
        if inspect.isclass(obj):
            if obj.__module__ == mod.__name__:
                for a, v in list(vars(obj).items()):
                    if a.startswith("__"):
                        continue
                    if isinstance(v, property):
                        setattr(obj, a, property(returns_marked(v.fget, f"{obj.__name__}.{a}")))
                    elif inspect.isfunction(v):
                        setattr(obj, a, returns_marked(v, f"{obj.__name__}.{a}"))
                    elif isinstance(v, (staticmethod, classmethod)):
                        setattr(obj, a, type(v)(returns_marked(v.__func__, f"{obj.__name__}.{a}")))
                    elif not callable(v):
                        setattr(obj, a, wrap(v, f"{obj.__name__}.{a}"))
        elif name.startswith("_"):
            continue                                  # private names are only read by the config itself
        elif isinstance(obj, (str, dict, list, tuple, set, frozenset)):
            setattr(mod, name, wrap(obj, name))
        elif hasattr(obj, "__dict__") and type(obj).__module__ in (mod.__name__, "components.page_templates"):
            # config objects only (never shared helper objects such as the cached WinnerFields: marking them
            # would leak into every later render in the process)
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
            _mark_authored(mod, pair)
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
def parse_markers(text: str, def_index: list | None = None):
    """(clean text, kinds, paths, sentinels, definitions) of a rendered block.
    kinds[i] in {'template', 'authored', 'definition', 'value'}; paths[i] = config attribute path of authored text;
    sentinels = (start, end, source, unit, shown) in clean coordinates; definitions = raw text of every definition
    span. A block that opens with an authored-close marker (a template split a config string) starts authored."""
    from components.provenance import A0, A1, AP, D0, D1, S0, S1, S2, U
    marks = (A0, A1, AP, D0, D1, S0, S1, S2, U)
    first = min([i for i in (text.find(A0), text.find(A1)) if i >= 0], default=-1)
    authored = first >= 0 and text[first] == A1
    path = None
    dfn, dstart, defs, dcur = 0, None, [], -1
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
                dcur = len(defs)
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
            if def_index is not None:
                def_index.extend([-1] * len(shown))
            sents.append((start, len(clean), src, unit or "raw", shown))
            i = k + 1
            continue
        else:
            clean.append(ch)
            kinds.append("definition" if dfn else ("authored" if authored else "template"))
            paths.append(path)
            if def_index is not None:
                def_index.append(dcur if dfn else -1)
        i += 1
    return "".join(clean), kinds, paths, sents, defs


def _numbers(text: str):
    """Numeric tokens of a span (values, decimals, percent, explicit sign) — dates excluded."""
    body = DATE.sub(lambda m: " " * len(m.group(0)), text)
    return [(_value(m.group(0)), m.group(0)) for m in NUM.finditer(body) if _value(m.group(0))]


_SPEC_POOL: dict[str, set] = {}


def spec_numbers(pair: str) -> set[float]:
    """Numbers the pair DECLARES outside its config (Codex L2v3 N4, Lead-tightened): every numeric literal and
    every number inside a string literal of the harness spec scripts/pair_spec_<pair>.py (windows, thresholds,
    quantiles, lags, display names such as '60-month z-score'); in scripts/pair_pipeline_<pair>.py only the
    NAMED MODULE-LEVEL parameter constants (``NAME = <literal>``) -- incidental literals inside pipeline code
    (seeds, clip bounds, 0.5 ...) are not declarations; the candidates manifest and the registry entry.
    Definition text and categorical field labels may show only these numbers (a percentile 'p75' / '75th' also
    matches 0.75)."""
    if pair in _SPEC_POOL:
        return _SPEC_POOL[pair]
    import ast as _ast
    nums: set[float] = set()

    def consts(node) -> None:
        for n in _ast.walk(node):
            if isinstance(n, _ast.Constant):
                if isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
                    nums.add(float(n.value))
                elif isinstance(n.value, str):
                    nums.update(float(x) for x in re.findall(r"\d+(?:\.\d+)?", n.value))

    spec = REPO / "scripts" / f"pair_spec_{pair}.py"
    if spec.exists():
        consts(_ast.parse(spec.read_text()))
    pipe = REPO / "scripts" / f"pair_pipeline_{pair}.py"
    if pipe.exists():
        for st in _ast.parse(pipe.read_text()).body:
            tgt = st.targets if isinstance(st, _ast.Assign) else [st.target] if isinstance(st, _ast.AnnAssign) else []
            if not tgt or st.value is None or not all(isinstance(t, _ast.Name) for t in tgt):
                continue
            try:
                _ast.literal_eval(st.value)                     # a literal parameter, not computed code
            except (ValueError, TypeError, SyntaxError, RecursionError):
                continue
            consts(st.value)
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


_CODE_PARAMS: dict[str, dict] = {}
_CODE_COLS: dict[str, dict] = {}
_DEF_CODE: dict[str, dict] = {}


def _fn_numbers(fn, seen=None) -> set[float]:
    """Numeric constants of a callable: its code constants (nested code objects included) and closure cells."""
    seen = seen or set()
    out: set[float] = set()
    code = getattr(fn, "__code__", None)
    if code is None or id(code) in seen:
        return out
    seen.add(id(code))
    stack = [code]
    while stack:
        c = stack.pop()
        for k in c.co_consts:
            if isinstance(k, (int, float)) and not isinstance(k, bool):
                out.add(float(k))
            elif hasattr(k, "co_consts"):
                stack.append(k)
    for cell in getattr(fn, "__closure__", None) or ():
        try:
            out |= _obj_numbers(cell.cell_contents, seen)
        except ValueError:
            pass
    return out


def _obj_numbers(o, seen=None) -> set[float]:
    if isinstance(o, bool) or o is None:
        return set()
    if isinstance(o, (int, float)):
        return {float(o)}
    if callable(o) and hasattr(o, "__code__"):
        return _fn_numbers(o, seen)
    if hasattr(o, "__dataclass_fields__"):
        out: set[float] = set()
        for f in o.__dataclass_fields__:
            out |= _obj_numbers(getattr(o, f), seen)
        return out
    return set()


def code_params(pair: str) -> dict[str, set[float]]:
    """{signal or threshold code: the numbers that parameterise it in the pair spec} (QA L2v4 addendum: a
    definition number is bound to ITS code's parameters, not to any number the pair declares).
      signal code    -> SIGNALS column -> constants of the spec statement(s) computing that column, of the local
                        variables and spec helper functions that statement uses
      threshold code -> the Rule objects rules(signal) returns for every signal: threshold value, ISQuantile q /
                        min_periods, constants and closure values of the rule's callables
    A fraction 0 < x < 1 also stands for 100x (0.75 <-> '75th percentile'). Empty for a pair without a spec."""
    if pair in _CODE_PARAMS:
        return _CODE_PARAMS[pair]
    import ast as _ast
    import importlib.util
    out: dict[str, set[float]] = {}
    f = REPO / "scripts" / f"pair_spec_{pair}.py"
    if f.exists():
        tree = _ast.parse(f.read_text())
        funcs = {n.name: n for n in tree.body if isinstance(n, _ast.FunctionDef)}
        modconst = {t.id: n.value for n in tree.body if isinstance(n, _ast.Assign) for t in n.targets
                    if isinstance(t, _ast.Name) and isinstance(n.value, (_ast.Constant, _ast.Tuple, _ast.List))}

        def consts(node) -> set[float]:
            return {float(n.value) for n in _ast.walk(node) if isinstance(n, _ast.Constant)
                    and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)}

        col_nums: dict[str, set[float]] = {}
        for fn in funcs.values():
            local: dict[str, _ast.AST] = dict(modconst)
            frames = {t.value.id for st in _ast.walk(fn) if isinstance(st, _ast.Assign) for t in st.targets
                      if isinstance(t, _ast.Subscript) and isinstance(t.value, _ast.Name)}
            loops = {}                                   # statement -> (loop var, literal values)
            for lp in _ast.walk(fn):
                if isinstance(lp, _ast.For) and isinstance(lp.target, _ast.Name) \
                        and isinstance(lp.iter, (_ast.Tuple, _ast.List)) \
                        and all(isinstance(e, _ast.Constant) for e in lp.iter.elts):
                    for st in lp.body:
                        loops[st] = (lp.target.id, [e.value for e in lp.iter.elts])
            for st in _ast.walk(fn):
                if not (isinstance(st, _ast.Assign) and len(st.targets) == 1):
                    continue
                t = st.targets[0]
                if isinstance(t, _ast.Name):
                    local[t.id] = st.value
                    continue
                if not isinstance(t, _ast.Subscript):
                    continue
                nums = _expr_numbers(st.value, local, funcs, consts, frames=frames)
                if isinstance(t.slice, _ast.Constant) and isinstance(t.slice.value, str):
                    col_nums.setdefault(t.slice.value, set()).update(nums)
                elif isinstance(t.slice, _ast.JoinedStr) and st in loops:
                    var, vals = loops[st]
                    for v in vals:
                        key = "".join(str(p.value) if isinstance(p, _ast.Constant) else
                                      str(v) if isinstance(p, _ast.FormattedValue) and isinstance(p.value, _ast.Name)
                                      and p.value.id == var else "\0" for p in t.slice.values)
                        if "\0" not in key and isinstance(v, (int, float)):
                            col_nums.setdefault(key, set()).update(nums | {float(v)})
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            spec_ = importlib.util.spec_from_file_location(f"_gate_spec_{pair}", f)
            mod = importlib.util.module_from_spec(spec_)
            spec_.loader.exec_module(mod)
            signals = dict(getattr(mod, "SIGNALS", {}) or {})
            for code, col in signals.items():
                out[code] = set(col_nums.get(col, set())) | {float(x) for x in re.findall(r"\d+(?:\.\d+)?", col)}
            _CODE_COLS[pair] = {col: code for code, col in signals.items()}
            for code in signals:
                try:
                    for tcode, rule in (mod.rules(code) or {}).items():
                        out.setdefault(tcode, set()).update(_obj_numbers(rule))
                except Exception:                        # noqa: BLE001 - a spec without rules() binds signals only
                    pass
        except Exception:                                # noqa: BLE001 - an unloadable spec binds nothing
            out = {}
        finally:
            sys.path.remove(str(REPO / "scripts"))
    ppy = None
    try:
        ppy = float(json.loads(sorted((RESULTS / pair).glob("candidates_manifest_*.json"))[-1].read_text())["ppy"])
    except (IndexError, OSError, KeyError, ValueError, TypeError):
        pass
    for k, v in out.items():
        v |= {round(x * 100, 6) for x in list(v) if 0 < x < 1}
        if ppy and ppy > 1:                      # a window in years: 20 quarters = 5-year, 1260 days = 5-year
            v |= {x / ppy for x in list(v) if x >= ppy and (2 * x / ppy).is_integer()}
    _CODE_PARAMS[pair] = out
    return out


def _expr_numbers(expr, local: dict, funcs: dict, consts, depth: int = 0, frames: set = frozenset()) -> set[float]:
    """Constants of a column expression plus those of the local variables (never the feature frame itself) and
    spec helper functions it uses."""
    import ast as _ast
    nums = set(consts(expr))
    if depth > 4:
        return nums
    for n in _ast.walk(expr):
        if isinstance(n, _ast.Name) and n.id in local and n.id not in frames and local[n.id] is not expr:
            nums |= _expr_numbers(local[n.id], local, funcs, consts, depth + 1, frames)
        elif isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name) and n.func.id in funcs:
            nums |= consts(funcs[n.func.id])
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
        params = code_params(pair).get(val) if pair else None
        if params is not None:                  # a spec code: its text may show only that code's parameters
            bad = [t for (x, d, _p), t in toks if not any(abs(abs(x) - v) < 1e-9 for v in params)]
        else:
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


_LEAF = re.compile(r"(?:art|reg):[^,()]+")


def _kind_value_ok(kind: str, v: float) -> bool:
    """docs/gates/provenance_units.json value_checks."""
    return {"ratio": abs(v) <= 1.5, "count": float(v).is_integer() and v >= 0, "lead": float(v).is_integer(),
            "pvalue": 0 <= v <= 1, "turnover": v >= 0, "sharpe": abs(v) < 10}.get(kind, True)


def leaf_kind_check(src: str, pair: str | None) -> str | None:
    """QA L2v4 #4: every numeric leaf a page shows has a declared kind, and its value is consistent with it (a
    percent-stored 43.48 declared as a ratio fails)."""
    from components import provenance as P
    for m in _LEAF.finditer(src):
        leaf = m.group(0)
        try:
            v = P.evaluate(leaf, {}, pair)
        except Exception:                               # noqa: BLE001 - resolution is reported by the caller
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        kind = P.leaf_kind(leaf)
        if kind == "unknown":
            return f"numeric leaf {leaf} has no declared kind (docs/gates/provenance_units.json)"
        if not _kind_value_ok(kind, float(v)):
            return f"leaf {leaf} = {v!r} is inconsistent with its declared kind {kind!r}"
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
    r = leaf_kind_check(src, pair)
    if r:
        return r
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


def definition_allowed(pair: str | None, raw_def: str, body: str, m) -> tuple[set[float], str | None]:
    """(numbers a definition token may show, the code(s) it is bound to or None)."""
    if pair is None:
        return set(), None
    params = code_params(pair)
    code = _DEF_CODE.get(pair, {}).get(raw_def)
    if code in params:
        return params[code], code
    # unkeyed methodology text describes codes in words ("its rolling 60-month 75th percentile"): it cannot be
    # bound to one code, so it keeps the pair's declared numbers (reported as unbound, with its acceptance)
    return spec_numbers(pair), None


def check_tagged(text: str, pool: dict, entries: list[dict], fields: dict, where: str,
                 pair: str | None = None, approved: set | None = None,
                 headline: bool = False, value_match: bool = True) -> tuple[list[str], dict]:
    """Layer 2 on one rendered block. Authored numbers must sit in a verified sentinel, an approved definition
    span or a path-bound allowlist span; template text keeps the value-matching fallback (sign-sensitive for
    explicitly signed tokens) unless value_match is False (text of a provenance-checked chart file, or of a
    sourced table whose rows are checked against their source file). Returns (findings, counters)."""
    dix: list = []
    clean, kinds, paths, sents, defs = parse_markers(text, dix)
    out, cnt = [], {"authored_tokens": 0, "template_tokens": 0, "tagged_values": len(sents), "provenance_tokens": 0,
                    "definition_bound": 0, "definition_unbound": 0}
    for a, b, src, unit, shown in sents:
        r = verify_sentinel(src, unit, shown, fields, pair)
        if r:
            out.append(f"MISMATCH {where}: {r}")
    for d in defs:
        if approved is not None and d not in approved:
            out.append(f"DEFINITION {where}: definition text not from an approved definition field — "
                       f"\"{d[:100]}\"")
    body = strip_non_prose(clean)
    if pair is not None:                       # codes the pair's artifacts declare ('T_z_1.0', 'T3_z1.5') are keys
        body = _IDENTS_RX(pair).sub(lambda m_: " " * len(m_.group(0)), body)
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
                # definition text may show only the parameters of the code it defines (QA L2v4 addendum): the
                # *_TEXT key, else the signal / threshold codes (or signal columns) named on the same line; a line
                # naming no code falls back to every number the pair declares (counted as unbound)
                if rx is DATE:
                    continue
                d = next((dix[i] for i in range(m.start(), m.end()) if dix[i] >= 0), -1)
                allowed, bound = definition_allowed(pair, defs[d] if d >= 0 else "", body, m)
                cnt["definition_bound" if bound else "definition_unbound"] += 1
                val = float(word_value(m)) if rx is WORD else _value(m.group(1) if rx is ORDINAL else m.group(0))
                x = abs(val if isinstance(val, float) else (val[0] if val else float("nan")))
                if any(abs(x - v) < 1e-9 for v in allowed):
                    continue
                out.append(f"DEFINITION {where}: definition number {m.group(0)!r} is not a parameter of "
                           f"{bound or 'any code the pair declares'} — \"{_ctx(body, m)}\"")
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
            elif not value_match:
                cnt["template_tokens"] -= 1
                cnt["provenance_tokens"] += 1
            else:
                # v5.2 (Codex V51-5): no value-matching fallback. A template number that is neither tagged nor an
                # allowlisted descriptive phrase FAILS, whatever its value (equalling an artifact value is no proof)
                kindtxt = "on a headline surface " if headline else ""
                out.append(f"UNTAGGED-TEMPLATE {where}: template number {m.group(0)!r} {kindtxt}is neither tagged "
                           f"nor an allowlisted descriptive phrase — \"{_ctx(body, m)}\"")
                cnt.setdefault("template_blocks", set()).add(body.strip()[:70].replace("\n", " "))
                cnt.setdefault("template_list", []).append((m.group(0), _ctx(body, m)))
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


# ------------------------------------------------------------------------------ sourced tables (v5, QA L2v4 #1)
_SRC_ROWS: dict[str, list] = {}


def _flat(o, out: list, key: str = "") -> list:
    """(column / key, value) pairs of a JSON record, nested keys flattened to their last name."""
    if isinstance(o, dict):
        for k, v in o.items():
            _flat(v, out, str(k))
    elif isinstance(o, (list, tuple)):
        for v in o:
            _flat(v, out, key)
    else:
        out.append((key, o))
    return out


def table_source_rows(payload: str, pair: str) -> tuple[list[list], list[str], dict]:
    """(source rows as flat value lists, freshness findings, column binding {"derived": {display: source col},
    "columns": {display: source col}}) of a table_source marker.
    A source must exist inside results/<pair>/ or data/, and a dated source (YYYYMMDD in its path) must carry the
    pair's current run tag."""
    import pandas as pd
    try:
        spec = json.loads(payload)
    except ValueError:
        return [], [f"table source marker unreadable: {payload[:80]!r}"], {"derived": {}, "columns": {}}
    rows, bad, tag = [], [], load_tag(pair)
    for src in spec.get("src", []):
        path, _, ptr = src.partition("#")
        f = (REPO / path).resolve()
        try:
            rel = f.relative_to(REPO.resolve()).as_posix()
        except ValueError:
            rel = None
        if not rel or not (rel.startswith(f"results/{pair}/") or rel.startswith("data/")) or not f.is_file():
            bad.append(f"table source {src!r} is not a file of results/{pair}/ or data/")
            continue
        dated = re.findall(r"(?<!\d)(20\d{6})(?!\d)", rel)
        if dated and any(t != tag for t in dated):
            bad.append(f"table source {rel} is from run {dated[-1]}, the current run is {tag}")
            continue
        if src not in _SRC_ROWS:
            if f.suffix == ".json":
                o = json.loads(f.read_text())
                for k in [x for x in ptr.split("/") if x]:
                    o = o[int(k)] if isinstance(o, list) else o[k]
                recs = o if isinstance(o, list) else [o]
                _SRC_ROWS[src] = [_flat(r, []) for r in recs]
            elif f.suffix == ".parquet":
                d_ = pd.read_parquet(f).reset_index()
                _SRC_ROWS[src] = [list(zip(d_.columns.astype(str), r)) for r in d_.values.tolist()]
            else:
                d_ = pd.read_csv(f, comment="#")
                _SRC_ROWS[src] = [list(zip(d_.columns.astype(str), r)) for r in d_.values.tolist()]
        rows += _SRC_ROWS[src]
    d = spec.get("derived", {})
    return rows, bad, {"derived": d if isinstance(d, dict) else {c: None for c in d},
                       "columns": spec.get("columns") or {}}


def _row_values(row: list) -> tuple[list[tuple[float, bool]], set[str]]:
    """(numbers with 'may be shown x 100' = the source column's declared kind is a ratio, text cells)."""
    from components import provenance as P
    nums, strs = [], set()
    for col, v in row:
        if isinstance(v, bool) or v is None:
            continue
        ratio = P.leaf_kind(f"art:t#/{col}") in P.RATIO_KINDS
        if isinstance(v, (int, float)):
            if not (isinstance(v, float) and math.isnan(v)):
                nums.append((float(v), ratio))
            continue
        t = str(v)
        strs.add(t)
        try:
            nums.append((float(t), ratio))
        except ValueError:
            pass
    return nums, strs


def _cell_ok(cell, nums: list, strs: set[str]) -> bool:
    """A displayed cell equals a source cell (text), or every number / date in it is a value of the row at the
    displayed precision (signed). A percent display may show x 100 ONLY of a column whose declared kind is a ratio
    (Codex V51-2: '4348.0%' no longer matches a stored 43.48); otherwise the value is shown as stored.
    ``cell``: text, or (exact text, text with allowlisted name spans blanked)."""
    exact, cell = cell if isinstance(cell, tuple) else (cell, cell)
    if exact in strs or not re.search(r"\d", cell):
        return True
    for m in DATE.finditer(cell):
        if not any(x.startswith(m.group(0)) for x in strs):
            return False
    for (x, d, pct), _t in _numbers(cell.replace("−", "-")):
        tol = 0.5 * 10 ** -d + 1e-9
        ok = any((abs(v - x) <= tol if d else (float(v).is_integer() and v == x)) or
                 (pct and ratio and abs(v * 100 - x) <= tol) for v, ratio in nums)
        if not ok:
            return False
    return True


_ALL_STRS: dict[int, set] = {}
_RANKS: dict[tuple, dict] = {}

# Checker-owned derivation rules for derived table columns (Codex V52-3): a derived display column may only name
# a rank column listed here, and the checker recomputes that rank from its score column over the source rows
# (descending, ties share the lowest rank, rows without a rank are not ranked) instead of trusting the file or the
# producer's mapping.
RANK_RULES = {"is_rank": "is_sharpe", "oos_rank": "oos_sharpe"}


def _norm(h: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", str(h).lower()).strip("_")


def _binding(bind) -> tuple[dict, dict]:
    if isinstance(bind, dict) and set(bind) <= {"derived", "columns"} and bind:
        return dict(bind.get("derived") or {}), dict(bind.get("columns") or {})
    return (bind if isinstance(bind, dict) else {c: None for c in bind or ()}), {}


def _bound_col(h: str, columns: dict, row_cols: set) -> str | None:
    """Source column a displayed column shows: the producer's explicit mapping, else the source column whose
    normalised name equals the header ('OOS Sharpe' -> oos_sharpe). None: unbound."""
    if h in columns:
        return columns[h] if columns[h] in row_cols else None
    n = _norm(h)
    return next((c for c in row_cols if _norm(c) == n), None)


def _recomputed_rank(rows: list[list], rank_col: str) -> dict[int, float]:
    """{row index: rank} recomputed from RANK_RULES[rank_col] over the rows that carry a rank."""
    key = (id(rows), rank_col)
    if key not in _RANKS:
        score = RANK_RULES[rank_col]
        vals = {}
        for i, r in enumerate(rows):
            d = dict(r)
            rk, sc = d.get(rank_col), d.get(score)
            if _isnum(rk) and _isnum(sc):
                vals[i] = float(sc)
        _RANKS[key] = {i: 1.0 + sum(1 for w in vals.values() if w > v) for i, v in vals.items()}
    return _RANKS[key]


def _isnum(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and not (isinstance(v, float) and math.isnan(v))


def row_bound(cells: list, header: list[str], rows: list[list], bind) -> bool:
    """Every checked cell of a displayed row is matched by ONE source row. A cell with numbers or dates is checked
    against the ONE source column its displayed column is bound to (_bound_col; Codex V52-2: a percent display
    was authorised by a coincident ratio value in another column): its value at the displayed precision, x 100
    only when that column's declared kind is a ratio. A numeric cell in an unbound column fails (UNBOUND). Text
    cells that occur in the source (row keys such as an episode name) must occur in that same row; text the
    template composes binds nothing. ``bind``: {"derived": {display: rank column}, "columns": {display: source
    column}} (a bare dict is the derived map). A derived numeric cell must name a RANK_RULES column (None or any
    other column fails, Codex V52-3) and equal both that column's value and the rank the checker recomputes."""
    derived, columns = _binding(bind)
    if id(rows) not in _ALL_STRS:
        _ALL_STRS.clear()
        _RANKS.clear()
        _ALL_STRS[id(rows)] = {t for r in rows for t in _row_values(r)[1]}
    known = _ALL_STRS[id(rows)]
    row_cols = {c for r in rows for c, _v in r}
    keys, want, checks = [], [], []
    for c, h in zip(cells, header):
        exact, blanked = c if isinstance(c, tuple) else (c, c)
        if h in derived:
            if re.search(r"\d", exact):
                if derived[h] not in RANK_RULES:
                    return False
                checks.append((exact, derived[h]))
            continue
        if re.search(r"\d", blanked):
            col = _bound_col(h, columns, row_cols)
            if col is None:
                return False
            want.append((c, col))
        elif exact and exact in known:
            keys.append(exact)
    if not want and not keys and not checks:
        return True

    def derived_ok(i, r) -> bool:
        vals = dict(r)
        for txt, col in checks:
            v = vals.get(col)
            n = [x for (x, _d, _p), _t in _numbers(txt)]
            rk = _recomputed_rank(rows, col).get(i)
            if not _isnum(v) or not n or rk is None or abs(float(v) - n[0]) > 1e-9 or abs(rk - n[0]) > 1e-9:
                return False
        return True
    for i, r in enumerate(rows):
        _nums, strs = _row_values(r)
        if not all(k in strs for k in keys) or not derived_ok(i, r):
            continue
        vals = dict(r)
        if all(_cell_ok(c, *_row_values([(col, vals.get(col))])) for c, col in want):
            return True
    return False


def _template_cells(row_text: str, entries: list[dict] | None = None) -> list[str]:
    """The cells of a rendered table row with sentinel-tagged / authored characters removed (those are checked by
    check_tagged) and allowlisted template spans (names such as 'S&P 500') blanked; what is left is copied from
    the table's source file."""
    ents = _entries_for(entries or [], "template", None)
    out = []
    for cell in row_text.split(TABLE_SEP):
        clean, kinds, _p, _s, _d = parse_markers(cell)
        chars = [ch if k == "template" else " " for ch, k in zip(clean, kinds)]
        for m in NUM.finditer(clean):
            if _allowed(m.span(), clean, ents):
                chars[m.start():m.end()] = " " * (m.end() - m.start())
        out.append(("".join(ch if k == "template" else " " for ch, k in zip(clean, kinds)).strip(),
                    "".join(chars).strip()))
    return out


def load_tag(pair: str) -> str:
    ws = json.loads((RESULTS / pair / "winner_summary.json").read_text())
    return ws["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv")


def near_miss(pool: dict, centres: list[float], signed: bool = True) -> float:
    """Share of near-miss stale values accepted by value-matching: each centre (a headline Sharpe) +-0.01..0.10
    at 2 dp, the QA L2v4 #1 measure ('a stale Sharpe within 0.10 of the truth')."""
    toks = [round(c + k * 0.01, 2) for c in centres for k in list(range(-10, 0)) + list(range(1, 11))]
    if not toks:
        return 0.0
    return sum(resolves(v, 2, False, pool, signed=signed and v < 0) for v in toks) / len(toks)


def _headline_centres(pair: str) -> list[float]:
    ws = json.loads((RESULTS / pair / "winner_summary.json").read_text())
    return [float(ws[k]) for k in ("oos_sharpe", "is_sharpe", "bh_sharpe") if isinstance(ws.get(k), (int, float))]


def _row_near_miss(cells: list[str], header: list[str], rows: list, derived: set) -> tuple[int, int]:
    """(accepted, tried): perturb each decimal number of a displayed row by +-0.01..0.10 at its precision and
    re-run the row-bound check."""
    acc = tried = 0
    der, _cols = _binding(derived)
    for i, (c, h) in enumerate(zip(cells, header)):
        if h in der:
            continue
        c = c[1] if isinstance(c, tuple) else c
        for (x, d, pct), t in _numbers(c)[:1]:
            if d == 0:
                continue
            step = 10 ** -d
            for k in (-10, -5, -2, -1, 1, 2, 5, 10):
                v = x + k * max(step, 0.01)
                fake = c.replace(t, f"{v:.{d}f}{'%' if pct else ''}", 1)
                tried += 1
                acc += row_bound(cells[:i] + [fake] + cells[i + 1:], header, rows, derived)
    return acc, tried


SURFACES = ("prose", "runtime_chart", "unsourced_table", "chart_file", "sourced_table")


def check_pair(pair: str, pages: dict | None = None) -> tuple[list[str], dict]:
    """Every rendered block, by surface:
      prose / runtime_chart / unsourced_table  authored + tagged checks; template numbers value-matched against the
                                               curated pool (the disclosed residual, measured below)
      chart_file      the chart file's provenance record must be current (chart_provenance.verify); its text is
                      producer output and is not value-matched
      sourced_table   every row must be matched by ONE row of its current source file (row_bound)."""
    import chart_provenance
    pool = load_pool(pair)
    entries = _allow_entries()
    pages = render_pages(pair) if pages is None else pages
    fields = json.loads((RESULTS / pair / "winner_summary.json").read_text()).get("winner_fields") or {}
    approved = _APPROVED.get(pair)
    findings, tot = [], {"authored_tokens": 0, "template_tokens": 0, "tagged_values": 0, "provenance_tokens": 0,
                         "definition_bound": 0, "definition_unbound": 0}
    surf = {k: 0 for k in SURFACES}
    blocks_seen: set[str] = set()
    charts, rows_checked, nm = set(), 0, [0, 0]
    head, srows, derived = [], [], set()
    tlist: list = []
    for sec, blocks in pages.items():
        for kind, b in blocks:
            where = f"{pair}/{sec}"
            if b.startswith("RENDER-EXCEPTION"):
                findings.append(f"{where}: {b}")
                continue
            if kind == "chart_file":
                if b not in charts:
                    charts.add(b)
                    r = chart_provenance.verify(pair, b)
                    if r:
                        findings.append(f"{'INPUT-ABSENT' if 'not present in this checkout' in r else 'STALE-CHART'}"
                                        f" {where}: {r}")
                continue
            if kind == "chart_file_text":
                f, c = check_tagged(b, pool, entries, fields, f"{where} [chart]", pair, approved, value_match=False)
                surface = "chart_file"
            elif kind.startswith("tablehead@"):
                srows, bad, derived = table_source_rows(kind[len("tablehead@"):], pair)
                findings += [f"STALE-TABLE {where}: {x}" for x in bad]
                head = parse_markers(b)[0].split(TABLE_SEP)
                f, c = check_tagged(b, pool, entries, fields, f"{where} [table]", pair, approved, value_match=False)
                surface = "sourced_table"
            elif kind.startswith("table@"):
                f, c = check_tagged(b, pool, entries, fields, f"{where} [table]", pair, approved, value_match=False)
                cells = _template_cells(b, entries)
                rows_checked += 1
                if srows and not row_bound(cells, head, srows, derived):
                    f = f + [f"UNRESOLVED-ROW {where} [table]: row is not a row of its source file — "
                             f"\"{parse_markers(b)[0][:160]}\""]
                elif srows and sum(nm) < 400:
                    a_, t_ = _row_near_miss(cells, head, srows, derived)
                    nm[0] += a_
                    nm[1] += t_
                surface = "sourced_table"
            elif kind in ("table", "tablehead"):
                f, c = check_tagged(b, pool, entries, fields, f"{where} [table]", pair, approved)
                surface = "unsourced_table"
            elif kind == "chart":
                f, c = check_tagged(b, pool, entries, fields, f"{where} [chart]", pair, approved)
                surface = "runtime_chart"
            else:
                hl = bool(HEADLINE.search(parse_markers(b)[0]))
                f, c = check_tagged(b, pool, entries, fields, where, pair, approved, hl)
                surface = "prose"
            findings += f
            for k in tot:
                tot[k] += c[k]
            surf[surface] += c["template_tokens"] + c["provenance_tokens"]
            blocks_seen.update(f"{sec}: {x}" for x in c.get("template_blocks", ()))
            tlist.extend((sec, surface, t, ctx) for t, ctx in c.get("template_list", ()))
    stats = {"tokens_pool": len(pool["nums"]), "coincidence_template": round(coincidence(pool), 3),
             "near_miss_template": round(near_miss(pool, _headline_centres(pair)), 3),
             "row_near_miss": round(nm[0] / nm[1], 3) if nm[1] else None, "rows_checked": rows_checked,
             "charts_checked": len(charts), "surfaces": surf,
             "definition": coincidence_definition(pair),
             "files": pool["files"], "template_blocks": sorted(blocks_seen), "template_list": tlist, **tot}
    return findings, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pairs", nargs="*")
    ap.add_argument("--text", help="check this text file against --pair's pool (fixtures)")
    ap.add_argument("--pair")
    ap.add_argument("--list-template", action="store_true", help="print every value-matched template token")
    a = ap.parse_args(argv)
    if a.text:
        f = check_text(Path(a.text).read_text(), load_pool(a.pair), _allow_entries(), a.pair)
        print("\n".join(f) or "OK")
        return 1 if f else 0
    hard = 0
    for p in a.pairs or pairs_13():
        f, st = check_pair(p)
        sf = st["surfaces"]
        vm = sf["prose"] + sf["runtime_chart"] + sf["unsourced_table"]
        print(f"[{'FAIL' if f else 'OK  '}] {p}: {len(f)} finding(s); {st['tagged_values']} tagged values, "
              f"{st['authored_tokens']} untagged authored tokens (allowlisted or failing)")
        print(f"      chart files: {st['charts_checked']} provenance-checked ({sf['chart_file']} text tokens not "
              f"value-matched); sourced tables: {st['rows_checked']} rows row-bound to their source "
              f"(near-miss acceptance {st['row_near_miss'] if st['row_near_miss'] is not None else 'n/a'})")
        print(f"      template numbers: no value matching (v5.2) - every number is tagged, an allowlisted "
              f"descriptive phrase ({vm} such tokens), or a finding ({len(st['template_list'])} UNTAGGED-TEMPLATE)")
        dfn = st["definition"]
        print(f"      definitions: {st['definition_bound']} tokens bound to their own code (keyed definitions, "
              f"categorical labels; {dfn['codes']} spec codes, random-token acceptance {dfn['per_code_mix']:.1%}, "
              f"integers 1-30 {dfn['per_code_small']:.1%} mean / {dfn['per_code_small_max']:.1%} max per code); "
              f"{st['definition_unbound']} unbound methodology tokens against {dfn['declared_pool']} declared "
              f"numbers (random-token acceptance {dfn['declared_mix']:.1%}, integers 1-30 {dfn['declared_small']:.1%})")
        for x in f:
            print("     ", x[:260])
        if a.list_template:
            for sec, surf, t, ctx in st["template_list"]:
                print(f"      TOKEN {sec}/{surf}: {t!r} — {ctx}")
        if st.get("template_blocks"):
            print(f"      value-matched template blocks: {len(st['template_blocks'])}")
            for b in st["template_blocks"]:
                print("        -", b[:110])
        hard += len(f)
    print(f"\nGATE-NUMBER-PROVENANCE: {hard} unresolved number(s). Charts: {CHART_SCOPE}.")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
