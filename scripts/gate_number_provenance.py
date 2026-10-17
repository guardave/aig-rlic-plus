#!/usr/bin/env python3
"""GATE-NUMBER-PROVENANCE (structured-prose layer 2): every number a schema-1.3 pair's pages SHOW must resolve to
that pair's artifacts.

Layer 1 (gate_structured_prose.py: authored-text scan + NUMLIT) is static and can be evaded by code that builds a
number (Codex B0f: text parsed from a dict, a rendered docstring, an imported constant, any allowed literal
context). This layer checks the OUTPUT instead:

  1. Render: each page of the pair (story / evidence / strategy / methodology) is executed in-process with
     streamlit.testing.AppTest, the same page scripts the app serves; the text of every markdown, caption,
     title/header, alert and metric element and every st.table / st.dataframe cell is collected. Chart
     internals (Plotly titles, axes, hover) are not prose and are not checked here.
  2. Tokens: every number in that text: decimals, integers, percentages, signed values, ISO dates, number
     words ("five months") and ordinals ("45th").
  3. Resolution: a token resolves when it equals, within its displayed rounding, a value in the pair's
     ARTIFACT POOL: results/<pair>/winner_summary.json, track_summary.json, evidence_facts_<tag>.json (the
     numbers the narrative cites, written by the pipeline), candidates_manifest_<tag>.json and the pair's
     lead_axis_registry entry. Percent tokens also match pool values x 100; magnitudes match regardless of
     sign; an integer matches an integer-valued pool number; a date matches a pool date (and a bare year
     matches the year of a pool date). Tokens inside a justified allowlist span
     (docs/gates/number_provenance_allowlist.json, plus the paths-'*' entries of
     docs/gates/structured_prose_allowlist.json) are exempt.
  4. Any unresolved token FAILs (hard for schema-1.3 pairs).

RESIDUAL RISK (documented, measured): a stale number that happens to equal some artifact value at its printed
precision passes. The pool is limited to the curated files above to keep that small; the gate prints, per pair,
the share of random plausible tokens (2-dp values in [-3, 3], 1-dp percentages, integers 1-300) that would
resolve by coincidence (`coincidence` line). Chart text is out of scope.

Usage:
  python scripts/gate_number_provenance.py [pair ...]         # default: every pair with winner_summary 1.3.x
  python scripts/gate_number_provenance.py --text FILE --pair P  # check a text file against P's pool (fixtures)
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
        for m in re.finditer(e["regex"], text, re.I):
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


def render_pages(pair: str, sections=SECTIONS) -> dict[str, list[tuple[str, str]]]:
    """{section: [(kind, text)]} of the pair's pages, rendered in-process (AppTest)."""
    from streamlit.testing.v1 import AppTest
    out = {}
    for sec in sections:
        pf = _page_file(pair, sec)
        if pf is None:
            continue
        code = ("import streamlit as st, runpy\n"
                "st.page_link = lambda *a, **k: None\n"          # multipage links need the full app router
                f"runpy.run_path({str(pf)!r}, run_name='__main__')\n")
        cwd = os.getcwd()
        os.chdir(APP)
        try:
            at = AppTest.from_string(code, default_timeout=180).run()
        finally:
            os.chdir(cwd)
        if at.exception:
            out[sec] = [("prose", f"RENDER-EXCEPTION {e.message}") for e in at.exception]
            continue
        blocks: list[str] = []
        _texts(at._tree, blocks)
        out[sec] = blocks
    return out


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
    findings = []
    for sec, blocks in pages.items():
        for kind, b in blocks:
            if b.startswith("RENDER-EXCEPTION"):
                findings.append(f"{pair}/{sec}: {b}")
                continue
            if kind == "table":
                tpool = tpool or load_table_pool(pair, pool)
                findings += check_text(b, tpool, entries, f"{pair}/{sec} [table]")
            else:
                findings += check_text(b, pool, entries, f"{pair}/{sec}")
    stats = {"tokens_pool": len(pool["nums"]), "coincidence": round(coincidence(pool), 3), "files": pool["files"]}
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
              f"{', '.join(Path(x).name for x in st['files'])} + registry; coincidence {st['coincidence']:.1%}")
        for x in f:
            print("     ", x[:260])
        hard += len(f)
    print(f"\nGATE-NUMBER-PROVENANCE: {hard} unresolved number(s)")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
