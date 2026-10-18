#!/usr/bin/env python3
"""GATE-STRUCTURED-PROSE: page prose must describe the published winner (Phase B, plan section 4 item 7).

Prose = every string a pair config exposes (class attributes, nested lists / dicts / config objects), rendered
by importing the config (so f-strings that read app/components/winner_fields.py show their real text). Fields =
winner_summary.json `winner_fields` (schema 1.3.0) or, for 1.2.0 files, the same facts derived from the
top-level fields.

Checks on result statements (sentence scope):
  SHARPE     a number in a Sharpe sentence must equal a Sharpe-type field (winner / B&H / hindsight track /
             plateau / CI / cross-evaluation) at its printed precision. Sentences about evidence tables
             (sub-period, quartile, concurrent, Granger, correlation, p-values, named episodes) are not result
             statements and are skipped.
  LEAD       "N months earlier", "lagged N months", "N-month lag/lead", "waits N months", "LN" (in a winner
             sentence) must be the winner lead, a plateau lead, or a labelled hindsight / raw-argmax lead.
  OBJECTIVE  when the winner was selected on in-sample data, prose must not say it was selected on OOS Sharpe.
  COUNT      "N (valid) combinations / candidates / position series" must equal a published count.
  MISSING    a "[missing: field]" placeholder (winner_fields has no such field).
Sentences labelled as legacy / superseded / corrected may cite the legacy OOS-selected row.

HARD for pairs whose winner_summary is schema 1.3.x (rebuilt on scripts/harness), plus:
  HANDTYPED  in those configs a result number must come from a formatted field, never a literal in the source.
Other pairs are reported as debt (WARN, exit 0).

Components rule (always hard against a debt baseline): app/components must not branch on a pair id
(`pair_id == "<id>"`, `"<id>" in pair_id`, `.startswith("<id>")`) or carry a registered pair id literal.
Existing cases are listed in docs/gates/structured_prose_component_baseline.json (paid down in Phase B);
anything new FAILs.

Usage:
  python scripts/gate_structured_prose.py [pair ...]
  python scripts/gate_structured_prose.py --fixture <dir with *_config.py[.txt] and winner_summary.json> [--hard]
  python scripts/gate_structured_prose.py --write-component-baseline
"""
from __future__ import annotations

import argparse
import ast
import importlib.machinery
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "app"
BASELINE = REPO / "docs" / "gates" / "structured_prose_component_baseline.json"

WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
WORDS.update({"twenty-four": 24, "a": 1, "single": 1})
UNIT = r"(?P<u>month|quarter|trading[- ]day|day|business[- ]day)s?"
NUM = r"(?P<n>\d{1,3}|[a-z]+(?:-[a-z]+)?)"
TRANSFORM = (r"(?![- ](?:change|chg|z-?score|average|avg|momentum|growth|rolling|median|window|return|forward|"
             r"history|percentile|mean|high|low|yoy|rate|sum|difference|diff|trend)\b)")
LEAD_PATTERNS = [
    rf"\b{NUM}[- ]{UNIT}[- ](?:earlier|before|ago|prior)\b",
    rf"\blag(?:ged|s)?\s+(?:of\s+|by\s+)?{NUM}[- ]{UNIT}\b{TRANSFORM}",
    rf"\b{NUM}[- ]{UNIT}[- ](?:lag|lead|delay)\b",
    rf"\b(?:waits?|waiting|lead of|delay of)\s+{NUM}[- ]{UNIT}\b{TRANSFORM}",
]
L_PATTERN = r"(?<![\w-])L(?P<n>\d{1,3})\b"
WINNER_WORDS = re.compile(r"\b(winner|winning|selected|rule|strategy|headline|best|uses|signal from)\b", re.I)
L_EXEMPT = re.compile(r"floor|truncat|grid|tested leads|scanned|sub-floor|L0", re.I)
EVIDENCE_EXEMPT = re.compile(
    r"sub-?period|quartile|\bQ[1-4]\b|concurrent|granger|correlation|p-value|\bp\s*[=<>]|regime|episode|"
    r"dot-com|\bgfc\b|covid|rate shock|stress (?:period|episode)|stationary block bootstrap|forward return|"
    r"local projection|quantile regression", re.I)
LEGACY_LABEL = re.compile(r"legacy|previous(?:ly)?|earlier (?:version|run|rule|publication)|superseded|"
                          r"correct(?:ed|ion)|was published|old rule|pre-gh|oos-argmax|no longer", re.I)
HINDSIGHT_LABEL = re.compile(r"hindsight|as revised|revised (?:values|data|today)|comparison track", re.I)
RAW_LABEL = re.compile(r"isolated|raw|single-lead peak|argmax|not the selection rule", re.I)
OOS_OBJECTIVE = [
    r"selected (?:for|on|by) (?:the )?(?:maximum|highest|best|max)\s+(?:search[- ]period\s+)?(?:OOS|out[- ]of[- ]sample)",
    r"(?:maximum|highest|best)\s+(?:search[- ]period\s+)?(?:OOS|out[- ]of[- ]sample)\s+Sharpe\s+(?:among|of|over|across|in)",
    r"selection\s+maximi[sz]ed\s+(?:the\s+)?(?:search[- ]period\s+)?(?:OOS|out[- ]of[- ]sample)",
    r"\bOOS[- ]selected\b",
    r"selected\s+on\s+(?:the\s+)?(?:OOS|out[- ]of[- ]sample)",
    r"search[- ]phase OOS winner",
]
COUNT_PATTERN = (r"(?P<n>\d[\d,]*)\s+(?:valid\s+|distinct\s+|tested\s+|candidate\s+|searched\s+)?"
                 r"(?:combinations|combos|candidates|candidate rules|rules tested|strategies tested|position series)")
SHARPE_NUM = r"(?<![\w.])[-+−]?\d+\.\d{2,4}(?![\d%])"


# --------------------------------------------------------------------------------------------- fields
def fields_from_summary(ws: dict) -> dict:
    """{name: value} of the facts prose may state. 1.3.0: winner_fields; 1.2.0: derived from top-level."""
    if ws.get("winner_fields"):
        f = {k: v.get("value") for k, v in ws["winner_fields"].items()}
    else:
        sel = ws.get("selection") or {}
        grid = sel.get("grid_scanned") or {}
        f = {"oos_sharpe": ws.get("oos_sharpe"), "is_sharpe": ws.get("is_sharpe"), "bh_oos_sharpe": ws.get("bh_sharpe"),
             "bh_is_sharpe": (sel.get("is_window") or {}).get("bh_is_sharpe"), "lead": ws.get("lead_value"),
             "n_candidates": ws.get("total_combos"), "n_valid": ws.get("valid_combos") or grid.get("n_valid_combos"),
             "n_distinct": grid.get("n_distinct_position_series"), "selection_objective": sel.get("objective")}
    sel = ws.get("selection") or {}
    f["_objective"] = sel.get("objective") or f.get("selection_objective")
    f["_lead_unit"] = ws.get("lead_unit") or "months"
    grid = sel.get("grid_scanned") or {}
    f.setdefault("median_valid_is_sharpe", grid.get("median_valid_objective"))
    ru = sel.get("runner_up") or {}
    f.setdefault("runner_up_is_sharpe", ru.get("is_sharpe", ru.get("objective_value")))
    f.setdefault("runner_up_plateau_score", ru.get("objective_value") if ru.get("objective") == "plateau_score_J" else None)
    f.setdefault("runner_up_oos_sharpe", ru.get("oos_sharpe"))
    f.setdefault("runner_up_lead", ru.get("lead_value"))
    leg = sel.get("legacy_oos_selected_row") or {}
    prev = [p for p in (sel.get("previously_published") or []) if isinstance(p, dict)]
    f["_legacy_oos_sharpe"] = [x for x in [leg.get("oos_sharpe")] + [p.get("oos_sharpe") for p in prev]
                               + [p.get("is_sharpe") for p in prev] + [p.get("hac_t") for p in prev]
                               if isinstance(x, (int, float))]
    f["_legacy_lead"] = [x for x in [leg.get("lead_value")] + [p.get("lead") for p in prev] if isinstance(x, (int, float))]
    # the previous published rule is also in winner_fields.previous_* (the only place when MAIN has no winner and
    # winner_summary carries no selection block: retail_inv_sales class)
    wfp = ws.get("winner_fields") or {}
    for k, dest in (("previous_oos_sharpe", "_legacy_oos_sharpe"), ("previous_is_sharpe", "_legacy_oos_sharpe"),
                    ("previous_lead", "_legacy_lead")):
        v = (wfp.get(k) or {}).get("value") if isinstance(wfp.get(k), dict) else None
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v not in f[dest]:
            f[dest].append(v)
    ce = ws.get("cross_eval") or {}
    for k in ("main_winner_on_revised", "revised_winner_on_main"):
        if isinstance(ce.get(k), dict):
            f[f"_ce_{k}_is"] = ce[k].get("is_sharpe")
            f[f"_ce_{k}_oos"] = ce[k].get("oos_sharpe")
    # null-tournament diagnostics (timing Sharpes of scrambled contests) are artifact facts the R7.1 caveat cites
    for role, rec in (ws.get("tracks") or {}).items():
        dg = ((rec or {}).get("null_tournament") or {}).get("r71_diagnosis") or {}
        for k, v in dg.items():
            if k.startswith("timing_mean") and isinstance(v, (int, float)):
                f[f"_null_{role}_{k}_sharpe"] = v
    return f


def _sharpe_values(f: dict, legacy: bool) -> list[float]:
    keys = [k for k in f if ("sharpe" in k or k in ("plateau_score", "ci_low", "ci_high", "sharpe_gap", "p_diff_le_0")
                             or k.startswith(("comparison_ci", "comparison_plateau", "comparison_sharpe")) or
                             k.startswith("_ce_")) and not k.startswith(("_legacy", "previous_"))]
    vals = [f[k] for k in keys if isinstance(f[k], (int, float)) and not isinstance(f[k], bool)]
    if legacy:
        vals += list(f.get("_legacy_oos_sharpe") or [])
    return vals


def _lead_values(f: dict, sent: str) -> set[int]:
    out = {f.get("lead")} | set(f.get("plateau_leads") or [])
    if HINDSIGHT_LABEL.search(sent):
        out |= {f.get("comparison_lead")} | set(f.get("comparison_plateau_leads") or [])
    if RAW_LABEL.search(sent):
        out |= {f.get("raw_argmax_lead"), f.get("comparison_raw_argmax_lead")}
    if LEGACY_LABEL.search(sent):
        out |= set(f.get("_legacy_lead") or [])
    if re.search(r"runner[- ]up", sent, re.I):
        out.add(f.get("runner_up_lead"))
    return {int(x) for x in out if isinstance(x, (int, float)) and not isinstance(x, bool)}


def _count_values(f: dict) -> set[int]:
    keys = ("n_candidates", "n_valid", "n_distinct", "comparison_n_candidates", "comparison_n_valid",
            "comparison_n_distinct", "null_draws", "comparison_null_draws")
    return {int(f[k]) for k in keys if isinstance(f.get(k), (int, float)) and not isinstance(f.get(k), bool)}


def _to_int(tok: str) -> int | None:
    tok = tok.lower()
    if tok.isdigit():
        return int(tok)
    return WORDS.get(tok)


def _in_lead_unit(n: int, unit: str, lead_unit: str) -> int:
    """Convert a stated lag to the winner's lead unit (a quarter = 3 months)."""
    u = unit.lower()
    if lead_unit == "months" and u.startswith("quarter"):
        return 3 * n
    if lead_unit == "quarters" and u.startswith("month"):
        return n // 3 if n % 3 == 0 else -1
    return n


def _matches(num: str, vals: list[float]) -> bool:
    x = float(num.replace("−", "-").replace("+", ""))
    d = len(num.split(".")[1])
    tol = 0.5 * 10 ** -d + 1e-9
    return any(abs(x - v) <= tol for v in vals)


# --------------------------------------------------------------------------------------------- prose
def sentences(text: str, clauses: bool = True) -> list[str]:
    """Checked units: clauses (split at ';' too, so a number in one clause is not read against the 'Sharpe' of
    another) or whole sentences (clauses=False: the scope of a legacy / raw label)."""
    text = re.sub(r"[*_`#>]", "", text)
    sep = r"(?<=[.!?;])\s+" if clauses else r"(?<=[.!?])\s+"
    parts = re.split(sep + r"|\n\s*[-•]\s+|\n{2,}", text)
    return [p.strip() for p in parts if p and p.strip()]


def _units(text: str) -> list[tuple[str, bool]]:
    """(clause, legacy): a legacy / raw label anywhere in a sentence covers all of that sentence's clauses (QA B1
    consumer_sentiment: a label in one clause did not cover the next clause -> false LEAD / SHARPE findings)."""
    out = []
    for sent in sentences(text, clauses=False):
        lg = bool(LEGACY_LABEL.search(sent))
        out += [(c, lg) for c in sentences(sent)]
    return out


def check_text(text: str, f: dict, where: str) -> list[str]:
    """Findings for one rendered prose string."""
    out = []
    in_is = str(f.get("_objective") or "").startswith("max_is_sharpe")
    for s, legacy in _units(text):
        if "[missing:" in s:
            out.append(f"MISSING {where}: {s[:160]}")
        if re.search(r"sharpe", s, re.I) and not EVIDENCE_EXEMPT.search(s):
            vals = _sharpe_values(f, legacy)
            for num in re.findall(SHARPE_NUM, s):
                if not _matches(num, vals):
                    out.append(f"SHARPE {where}: {num} is not a published Sharpe field — \"{s[:160]}\"")
        if not EVIDENCE_EXEMPT.search(s):
            allowed = _lead_values(f, s)
            for pat in LEAD_PATTERNS:
                for m in re.finditer(pat, s, re.I):
                    n = _to_int(m.group("n"))
                    if n is not None:
                        n = _in_lead_unit(n, m.group("u"), f.get("_lead_unit", "months"))
                    if n is not None and n not in allowed:
                        out.append(f"LEAD {where}: \"{m.group(0)}\" != winner lead {f.get('lead')} — \"{s[:160]}\"")
            if WINNER_WORDS.search(s) and not L_EXEMPT.search(s):
                for m in re.finditer(L_PATTERN, s):
                    if int(m.group("n")) not in allowed:
                        out.append(f"LEAD {where}: \"{m.group(0)}\" != winner lead {f.get('lead')} — \"{s[:160]}\"")
        if in_is and not legacy:
            for pat in OOS_OBJECTIVE:
                m = re.search(pat, s, re.I)
                if m:
                    out.append(f"OBJECTIVE {where}: says OOS-selected (\"{m.group(0)}\") but the winner was selected "
                               f"on in-sample data ({f.get('_objective')}) — \"{s[:160]}\"")
                    break
        counts = _count_values(f)
        for m in re.finditer(COUNT_PATTERN, s, re.I):
            n = int(m.group("n").replace(",", ""))
            if counts and n not in counts:
                out.append(f"COUNT {where}: \"{m.group(0)}\" not in published counts {sorted(counts)} — \"{s[:160]}\"")
    return out


def _collect(obj, path: str, out: list, depth: int = 0, seen=None):
    seen = set() if seen is None else seen
    if depth > 6 or id(obj) in seen:
        return
    if isinstance(obj, str):
        out.append((path, obj))
        return
    seen.add(id(obj))
    if isinstance(obj, dict):
        for k, v in obj.items():
            _collect(v, f"{path}[{k!r}]", out, depth + 1, seen)
    elif isinstance(obj, (list, tuple, set)):
        for i, v in enumerate(obj):
            _collect(v, f"{path}[{i}]", out, depth + 1, seen)
    elif hasattr(obj, "__dict__") and not isinstance(obj, type) and type(obj).__module__ not in ("builtins",):
        for k, v in vars(obj).items():
            if not k.startswith("_"):
                _collect(v, f"{path}.{k}", out, depth + 1, seen)


def config_prose(cfg_path: Path) -> list[tuple[str, str]]:
    """(attribute path, rendered string) for every string the config module exposes."""
    if str(APP) not in sys.path:
        sys.path.insert(0, str(APP))
    name = f"_sp_cfg_{abs(hash(str(cfg_path)))}"
    loader = importlib.machinery.SourceFileLoader(name, str(cfg_path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    out: list = []
    for k, v in vars(mod).items():
        if k.startswith("_"):
            continue
        if isinstance(v, type) and v.__module__ == name:
            for a, val in vars(v).items():
                if not a.startswith("_"):
                    _collect(val, f"{k}.{a}", out)
        elif isinstance(v, str) and k.isupper():
            out.append((k, v))
        elif not isinstance(v, type) and type(v).__module__ not in ("builtins",) and not callable(v) \
                and not hasattr(v, "__file__"):
            _collect(v, k, out)
    return out


ALLOWLIST = REPO / "docs" / "gates" / "structured_prose_allowlist.json"
NUM_TOKEN = re.compile(r"(?<![A-Za-z0-9])(?:(?<![\w%-])[-+\u2212])?\d+(?:[.,]\d+)*%?")
NUM_WORD = re.compile(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
                      r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
                      r"hundred|thousand|dozen|half|quarter of|third of)\b", re.I)
EXTRA_LEAD = [
    r"\b(?:prior|previous|preceding|last|earlier)\s+(?:calendar\s+)?(?:month|quarter|day|year|week)(?:'s)?\b",
    r"\bdelayed by\b", r"\b(?:a|one)\s+(?:calendar\s+)?(?:month|quarter|year|week|day)\s+(?:earlier|before|ago|back|later|lag)\b",
    r"\bone[- ](?:month|quarter|year|week|day|trading[- ]day)\b", r"(?<![\w-])L\d+\b",
]
EXTRA_OBJECTIVE = [r"\b(?:chosen|selected|picked)\s+(?:for|on|by)\s+(?:its\s+|their\s+|the\s+)?(?:best\s+|highest\s+)?"
                   r"(?:out[- ]of[- ]sample|OOS|test[- ]period)"]
EXTRA_COUNT = r"\b(?:rules|combinations|combos|candidates|strategies|position series|signals tested)\b"
BANNED = [r"\bvalidated edge\b", r"\bverdict\b", r"\bfails?\b(?! to)", r"\bat most\b", r"\bconfirms?\b",
          r"\bbeats?\b", r"\bpromising\b"]


def _authored_segments(tree) -> list[tuple[str, int, str]]:
    """(dotted attribute path, line, authored text) for every string literal of a config module. Formatted
    values of f-strings are masked as \u27e8F\u27e9 (they are rendered from fields / artifacts); docstrings, dict
    keys, format specs and identifier-like strings (no whitespace: chart names, paths, codes) are skipped."""
    out = []

    def text_of(node):
        if isinstance(node, ast.JoinedStr):
            return "".join(v.value if isinstance(v, ast.Constant) else "\u27e8F\u27e9" for v in node.values)
        return node.value

    def visit(node, path):
        if isinstance(node, (ast.JoinedStr,)) or (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            t = text_of(node)
            if re.search(r"\s", t):
                out.append((path, node.lineno, t))
            return
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                kk = k.value if isinstance(k, ast.Constant) else "?"
                visit(v, f"{path}[{kk}]")
            return
        if isinstance(node, ast.Call):
            for a in node.args:
                visit(a, path)
            for kw in node.keywords:
                visit(kw.value, f"{path}.{kw.arg}" if path else str(kw.arg))
            return
        if isinstance(node, ast.FormattedValue):
            return
        for child in ast.iter_child_nodes(node):
            visit(child, path)

    def body(stmts, prefix):
        for i, st in enumerate(stmts):
            if isinstance(st, ast.Expr) and isinstance(getattr(st, "value", None), ast.Constant) and i == 0:
                continue   # docstring
            if isinstance(st, ast.ClassDef):
                body(st.body, f"{prefix}{st.name}.")
            elif isinstance(st, ast.FunctionDef):
                body(st.body, f"{prefix}{st.name}.")
            elif isinstance(st, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tgt = st.targets[0] if isinstance(st, ast.Assign) else st.target
                name = getattr(tgt, "id", getattr(tgt, "attr", "?"))
                visit(st.value, f"{prefix}{name}")
            else:
                visit(st, prefix.rstrip("."))
    body(tree.body, "")
    return out


def _allowed(token_span, sentence, path, entries) -> bool:
    from fnmatch import fnmatch
    s0, s1 = token_span
    for e in entries:
        if not any(fnmatch(path, g) for g in e["paths"]):
            continue
        if e.get("deny_if_sentence") and re.search(e["deny_if_sentence"], sentence, re.I):
            continue
        for m in re.finditer(e["regex"], sentence, re.I):
            if m.start() <= s0 and m.end() >= s1:
                return True
    return False


def structural(cfg_path: Path) -> list[str]:
    """STRUCTURAL (hard, schema-1.3 pairs): authored config text contains no numeric token, number word, lead /
    objective / count phrase or banned verdict word outside docs/gates/structured_prose_allowlist.json."""
    entries = json.loads(ALLOWLIST.read_text())["entries"]
    out = []
    for path, line, text in _authored_segments(ast.parse(cfg_path.read_text())):
        for sent in sentences(text):
            hits = [("number", m) for m in NUM_TOKEN.finditer(sent)] + [("number word", m) for m in NUM_WORD.finditer(sent)]
            for kind, m in hits:
                if not _allowed(m.span(), sent, path, entries):
                    out.append(f"STRUCTURAL {path} (line {line}): {kind} \"{m.group(0)}\" typed in authored text — "
                               f"\"{sent[:140]}\"")
            for pat in LEAD_PATTERNS + EXTRA_LEAD:
                for m in re.finditer(pat, sent, re.I if "L\\d" not in pat else 0):
                    if "\u27e8F\u27e9" in m.group(0):
                        continue
                    if not _allowed(m.span(), sent, path, [e for e in entries if e["id"] in
                                                            ("spec_descriptions", "references", "release_and_execution_rule")]):
                        out.append(f"STRUCTURAL {path} (line {line}): lead phrase \"{m.group(0)}\" — \"{sent[:140]}\"")
            for pat in OOS_OBJECTIVE + EXTRA_OBJECTIVE:
                m = re.search(pat, sent, re.I)
                if m and not LEGACY_LABEL.search(sent):
                    out.append(f"STRUCTURAL {path} (line {line}): objective phrase \"{m.group(0)}\" — \"{sent[:140]}\"")
            for m in re.finditer(r"(?:\d[\d,]*|\b(?:" + NUM_WORD.pattern[3:-3] + r"))[\w -]{0,20}?" + EXTRA_COUNT, sent, re.I):
                out.append(f"STRUCTURAL {path} (line {line}): count phrase \"{m.group(0)}\" — \"{sent[:140]}\"")
            for pat in BANNED:
                m = re.search(pat, sent, re.I)
                if m:
                    out.append(f"STRUCTURAL {path} (line {line}): verdict word \"{m.group(0)}\" — \"{sent[:140]}\"")
    return sorted(set(out))


def _bh_scope(k: str) -> tuple[str, str, str]:
    """(track, period, kind) of a strategy or buy-and-hold field name: track comparison for comparison_* and the
    main rule scored on revised data (ce_main_on_revised_*); period is / oos / tail; kind sharpe / drawdown /
    return."""
    k = k.lstrip("_")
    track = "comparison" if k.startswith("comparison_") or k.startswith("ce_main_on_revised") else "main"
    period = "tail" if "tail" in k else ("is" if re.search(r"(?:^|_)is_", k) else "oos")
    kind = "sharpe" if "sharpe" in k else ("drawdown" if "drawdown" in k else "return")
    return track, period, kind


def swapped(text: str, f: dict, where: str) -> list[str]:
    """SWAPPED: in 'X versus Y for buy-and-hold', Y must be the buy-and-hold field of X's own track, period and
    kind (QA B1 consumer_sentiment: comparison_bh_is_sharpe 0.71 equalled the winner's OOS 0.71 and passed a
    correct sentence as swapped; any bh_* field used to count), and X must not be one (unless the values are equal).
    When X matches no strategy field, every buy-and-hold field is allowed (the SHARPE check reports X)."""
    bh_items = [(k, v) for k, v in f.items() if k.lstrip("_").replace("comparison_", "").startswith("bh_")
                or k.lstrip("_").startswith("tail_bh") or k.lstrip("_").startswith("comparison_tail_bh")]
    bh_items = [(k, v) for k, v in bh_items if isinstance(v, (int, float)) and not isinstance(v, bool)]
    strat = [(k, v) for k, v in f.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
             and (k, v) not in bh_items and any(w in k for w in ("sharpe", "return", "drawdown"))]
    out = []
    pat = (r"(" + SHARPE_NUM + r"|[-+\u2212]?\d+\.\d%)\s+(?:versus|vs\.?|against)\s+(" + SHARPE_NUM +
           r"|[-+\u2212]?\d+\.\d%)\s+(?:for\s+)?(?:SPY\s+)?(?:buy-and-hold|B&H)")

    def val(t):
        return float(t.replace("\u2212", "-").rstrip("%")) / (100 if t.endswith("%") else 1)

    def hits(t, items):
        v, d = val(t), (len(t.rstrip("%").split(".")[1]) + (2 if t.endswith("%") else 0))
        return [k for k, b in items if abs(v - b) <= 0.5 * 10 ** -d + 1e-9]
    # also 'X (buy-and-hold SPY: Y)' (QA B1 consumer_sentiment F3: the reworded form passed both regexes)
    pat2 = (r"(" + SHARPE_NUM + r"|[-+\u2212]?\d+\.\d%)\s*\((?:for\s+)?(?:buy-and-hold|B&H)(?:\s+\w+){0,3}\s*[:=]\s*(" +
            SHARPE_NUM + r"|[-+\u2212]?\d+\.\d%)\)")
    for s in sentences(text):
        for m in list(re.finditer(pat, s, re.I)) + list(re.finditer(pat2, s, re.I)):
            x, y = m.group(1), m.group(2)
            xs = hits(x, strat)
            scopes = {_bh_scope(k) for k in xs}
            allowed = [(k, v) for k, v in bh_items if not scopes or _bh_scope(k) in scopes]
            y_ok = bool(hits(y, allowed))
            x_is_bh = bool(hits(x, bh_items)) and not xs
            if not y_ok or (x_is_bh and abs(val(x) - val(y)) > 1e-9):
                out.append(f"SWAPPED {where}: \"{m.group(0)}\" — strategy and buy-and-hold values do not match their "
                           "fields (same track, period and kind)")
    return out


_PAIR_PH = re.compile(r"\{W\.(\w+)\}\s*(?:\w+\s+){0,3}?(?:versus|vs\.?|against)\s+(?:\w+\s+){0,3}?\{W\.(\w+)\}", re.I)


def _is_bh_field(name: str) -> bool:
    return name.replace("comparison_", "").startswith("bh_")


def swapped_placeholders(cfg_path: Path) -> list[str]:
    """SWAPPED (structural): in authored 'X versus Y' with both sides winner-field placeholders, a buy-and-hold
    field may not stand before a strategy field. Catches swaps the rendered-text check cannot see when the
    sentence does not name buy-and-hold."""
    out = []
    for node in ast.walk(ast.parse(cfg_path.read_text())):
        if not isinstance(node, ast.JoinedStr):
            continue
        txt = "".join(v.value if isinstance(v, ast.Constant) else "{" + ast.unparse(v.value) + "}"
                      for v in node.values)
        for m in _PAIR_PH.finditer(txt):
            a, b = m.group(1), m.group(2)
            if _is_bh_field(a) and not _is_bh_field(b):
                out.append(f"SWAPPED (line {node.lineno}): \"{m.group(0)}\" — a buy-and-hold field stands before "
                           "the strategy field it is compared with")
    return out


# Numeric literals in schema-1.3 config modules (Codex B0r): a number typed in Python code can reach prose through
# an f-string, str()/repr()/format()/%/+ or a named constant, all invisible to the authored-text scan. So a
# numeric literal is allowed ONLY in these contexts, each of which selects or converts artifact data and cannot
# itself be rendered:
#   - subscript / slice positions (row, column or key selection, e.g. parents[2], iloc[0], _AUD[("x", 1)]);
#   - a precision argument: the `nd` / `ndigits` default of a formatting helper, or argument 2 of round() /
#     the helpers in PRECISION_HELPERS (an int <= 6);
#   - a comparison operand from COMPARE_CONSTANTS (sign tests, conventional p-value cut-offs, a two-state
#     probability midpoint), compared with a non-literal expression;
#   - an arithmetic operand from UNIT_CONSTANTS (percent, periods per year, square root, +/- one period),
#     combined with a non-literal expression (a constant-only expression such as 1 * 12 fails).
PRECISION_HELPERS = {"round", "_pct", "_f", "_num", "_fmt"}
COMPARE_CONSTANTS = {0, 1, 0.05, 0.01, 0.1, 0.5}
UNIT_CONSTANTS = {1, 4, 12, 100, 252, 0.5}


def _is_num(n) -> bool:
    return isinstance(n, ast.Constant) and type(n.value) in (int, float)


def numeric_literals(cfg_path: Path) -> list[str]:
    """NUMLIT (hard, schema-1.3 pairs): numeric literals outside the enumerated contexts above."""
    tree = ast.parse(cfg_path.read_text())
    parent = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    out = []

    def in_subscript(n) -> bool:
        while n in parent:
            p = parent[n]
            if isinstance(p, ast.Subscript) and n is p.slice or isinstance(p, ast.Slice):
                return True
            if not isinstance(p, (ast.Tuple, ast.UnaryOp)):
                return False
            n = p
        return False

    for n in ast.walk(tree):
        if not _is_num(n):
            continue
        v, node = n.value, n
        if isinstance(parent.get(node), ast.UnaryOp):
            node = parent[node]
        p = parent.get(node)
        ok = in_subscript(n)
        if not ok and isinstance(p, ast.arguments):
            names = [a.arg for a in p.args[len(p.args) - len(p.defaults):]] if node in p.defaults else []
            ok = isinstance(v, int) and v <= 6 and \
                names[p.defaults.index(node)] in ("nd", "ndigits", "digits", "decimals")
        if not ok and isinstance(p, ast.Call) and isinstance(v, int) and v <= 6:
            fn = p.func.id if isinstance(p.func, ast.Name) else getattr(p.func, "attr", "")
            ok = fn in PRECISION_HELPERS and len(p.args) >= 2 and node is p.args[1]
        if not ok and isinstance(p, ast.Compare):
            others = [p.left] + list(p.comparators)
            ok = v in COMPARE_CONSTANTS and any(not isinstance(o, ast.Constant) and o is not node for o in others)
        if not ok and isinstance(p, ast.BinOp) and not isinstance(p.op, ast.Mod):
            other = p.right if node is p.left else p.left
            ok = v in UNIT_CONSTANTS and not isinstance(other, ast.Constant) and \
                not (isinstance(other, ast.UnaryOp) and isinstance(other.operand, ast.Constant))
        if not ok:
            out.append(f"NUMLIT (line {n.lineno}): numeric literal {v!r} in config code — "
                       f"\"{ast.unparse(p)[:100] if p is not None else v}\"; read it from an artifact")
    return out


APPROVED_DEF_ATTRS = {"_DATA_SOURCES_MD", "_METHODS_TABLE_MD", "_GRID_TABLE_MD", "_INDICATOR_CONSTRUCTION_MD"}


FORBIDDEN_CALLS = {"getattr", "setattr", "__import__", "eval", "exec", "compile", "vars", "globals", "locals",
                   "import_module", "reload"}


# v5 (QA L2v4 #5): what a schema-1.3 config may import and how it may use P, as allowlists. The forge damage is
# bounded (a forged tag is re-evaluated from its source, so it can only show some leaf's true value), but the rule
# is stated, not inferred from underscore names.
CONFIG_MODULES = {"__future__", "json", "pathlib", "pandas", "numpy", "math", "re", "datetime", "textwrap",
                  "typing", "dataclasses"}
CONFIG_COMPONENT_IMPORTS = {"components.page_templates": None,             # None: any *Config class
                            "components.winner_fields": {"load", "lead_grid"}}
P_API = {"json_file", "csv_file", "col_dict", "colmin", "colmax", "colmaxabs", "length", "count", "lead_grid",
         "year", "items", "prefix", "definitions", "definition_text"}


def provenance_api(cfg_path: Path) -> list[str]:
    """PROVENANCE-API (hard, schema-1.3 pairs; Codex L2v2 F1 / F10, L2v3 N1, QA L2v4 #5). A config may not mint
    tags or definitions itself:
      * imports: only CONFIG_MODULES, `from components import provenance as P`, and the CONFIG_COMPONENT_IMPORTS
        names; anything else that touches the components package (or pair_configs, or a relative import) fails;
      * P appears only as `P.<name>(...)` with <name> in P_API (no alias Q = P, no P passed or stored, no
        P.gate_on / P.os / P._x / P.DefText);
      * no dynamic access (getattr / eval / ... / sys.modules), no dunder attribute (x.__class__), no `.src`,
        no `type(...)(...)`, no DefText;
      * definition_text() only as the value of an approved methodology block, definitions() only for a *_TEXT
        dict."""
    tree = ast.parse(cfg_path.read_text())
    out = []
    parent = {c: x for x in ast.walk(tree) for c in ast.iter_child_nodes(x)}

    def bad(n, msg):
        out.append(f"PROVENANCE-API (line {n.lineno}): {msg}")

    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            if n.level:
                bad(n, "relative imports are not allowed in a config")
            elif mod == "components":
                for a in n.names:
                    if not (a.name == "provenance" and a.asname == "P"):
                        bad(n, "from components import only `provenance as P`")
            elif mod in CONFIG_COMPONENT_IMPORTS:
                allowed = CONFIG_COMPONENT_IMPORTS[mod]
                for a in n.names:
                    ok = a.name.endswith("Config") if allowed is None else a.name in allowed
                    if not ok or a.asname:
                        bad(n, f"`from {mod} import {a.name}` is not allowed in a config")
            elif mod.split(".")[0] not in CONFIG_MODULES:
                bad(n, f"`from {mod} import ...` is not allowed in a config (allowed: {sorted(CONFIG_MODULES)})")
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] not in CONFIG_MODULES:
                    bad(n, f"`import {a.name}` is not allowed in a config")
        elif isinstance(n, ast.Call):
            fn = n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "")
            if fn in FORBIDDEN_CALLS:
                bad(n, f"dynamic access `{fn}(...)` is not allowed in a config")
            if isinstance(n.func, ast.Call) and isinstance(n.func.func, ast.Name) and n.func.func.id == "type":
                bad(n, "`type(...)(...)` is not allowed in a config")
        elif isinstance(n, ast.Attribute):
            if n.attr.startswith("__") or n.attr in ("modules", "src"):
                bad(n, f"`.{n.attr}` is not allowed in a config")
        elif isinstance(n, ast.Name):
            if n.id == "DefText":
                bad(n, "DefText is not allowed in a config")
            elif n.id == "P":
                at = parent.get(n)
                call = parent.get(at)
                if not (isinstance(at, ast.Attribute) and at.value is n and isinstance(call, ast.Call)
                        and call.func is at and at.attr in P_API):
                    what = f"P.{at.attr}" if isinstance(at, ast.Attribute) and at.value is n else "P"
                    bad(n, f"{what}: P may only be used as `P.<name>(...)` with <name> in {sorted(P_API)}")
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) \
                and n.func.value.id == "P" and n.func.attr in ("definition_text", "definitions"):
            p = parent.get(n)
            targets = [t.id for t in getattr(p, "targets", []) if isinstance(t, ast.Name)] \
                if isinstance(p, ast.Assign) else []
            ok = (targets and all(t in APPROVED_DEF_ATTRS for t in targets)) if n.func.attr == "definition_text" \
                else (targets and all(t.endswith("_TEXT") for t in targets))
            if not ok:
                bad(n, f"{n.func.attr}() must be assigned to "
                    + ("an approved methodology block " + str(sorted(APPROVED_DEF_ATTRS))
                       if n.func.attr == "definition_text" else "a *_TEXT dict"))
    return out


def check_pair_files(cfg: Path, ws_path: Path, hard: bool) -> list[str]:
    ws = json.loads(ws_path.read_text())
    f = fields_from_summary(ws)
    findings = []
    for where, text in config_prose(cfg):
        findings += check_text(text, f, where)
        if hard:
            findings += swapped(text, f, where)
            findings += [x for x in (f"VERDICT {where}: \"{m.group(0)}\"" for pat in BANNED
                                     for m in [re.search(pat, text, re.I)] if m)]
    if hard:
        findings += structural(cfg) + swapped_placeholders(cfg) + numeric_literals(cfg) + provenance_api(cfg)
    return findings


# --------------------------------------------------------------------------------------------- components
def registered_pairs() -> set[str]:
    ids = {p.name[: -len("_config.py")] for p in (APP / "pair_configs").glob("*_config.py")}
    ids |= {p.name[: -len("_config.py")] for p in (APP / "pair_configs_archive").glob("*_config.py")}
    ids |= {p.name for p in (REPO / "results").iterdir() if p.is_dir()}
    return {i for i in ids if "_" in i}


def _mentions_pair(node) -> bool:
    return any(isinstance(n, ast.Name) and "pair" in n.id.lower() or
               isinstance(n, ast.Attribute) and "pair" in n.attr.lower() for n in ast.walk(node))


def component_violations() -> list[dict]:
    pairs = registered_pairs()
    out = []
    for py in sorted((APP / "components").glob("*.py")):
        tree = ast.parse(py.read_text())
        rel = str(py.relative_to(REPO))
        # allowed: id -> path / display-name maps (pair ids as dict keys)
        map_keys = {id(k) for d in ast.walk(tree) if isinstance(d, ast.Dict) for k in d.keys if k is not None}
        for node in ast.walk(tree):
            if id(node) in map_keys:
                continue
            snip = None
            if isinstance(node, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq, ast.In, ast.NotIn)) for o in node.ops):
                sides = [node.left] + list(node.comparators)
                consts = [s for s in sides if isinstance(s, ast.Constant) and isinstance(s.value, str) and s.value
                          and any(s.value in p for p in pairs)]
                others = [s for s in sides if not (isinstance(s, ast.Constant))]
                if consts and any(_mentions_pair(o) for o in others):
                    snip = ast.unparse(node)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in ("startswith", "endswith") and _mentions_pair(node.func.value) \
                    and node.args and isinstance(node.args[0], ast.Constant):
                snip = ast.unparse(node)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in pairs:
                snip = repr(node.value)
            if snip:
                out.append({"file": rel, "line": node.lineno, "snippet": snip})
    seen, uniq = set(), []
    for v in out:
        k = (v["file"], v["snippet"])
        if k not in seen:
            seen.add(k)
            uniq.append(v)
    return uniq


def check_components() -> tuple[list[str], list[str]]:
    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {"violations": []}
    known = {(v["file"], v["snippet"]) for v in base["violations"]}
    now = component_violations()
    cur = {(v["file"], v["snippet"]) for v in now}
    new = [f"COMPONENT {v['file']}:{v['line']}: pair-specific branch/literal {v['snippet'][:120]}"
           for v in now if (v["file"], v["snippet"]) not in known]
    paid = [f"debt paid: {f}: {s[:100]}" for f, s in sorted(known - cur)]
    return new, paid


# --------------------------------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="*")
    ap.add_argument("--fixture")
    ap.add_argument("--hard", action="store_true", help="fixture: apply the hard rules (HANDTYPED included)")
    ap.add_argument("--write-component-baseline", action="store_true")
    a = ap.parse_args(argv)
    if a.write_component_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps({"description": "Pair-specific branches / pair-id literals in app/components "
                                        "existing when the structured-prose gate was added (Phase B, plan 2a). Debt to "
                                        "pay down; the gate fails only on entries not listed here. Matching is by file "
                                        "+ code snippet, not line number.",
                                        "violations": component_violations()}, indent=2) + "\n")
        print(f"wrote {BASELINE.relative_to(REPO)}")
        return 0
    if a.fixture:
        d = Path(a.fixture)
        cfg = next(iter(sorted(d.glob("*_config.py*"))))
        res = check_pair_files(cfg, d / "winner_summary.json", hard=a.hard)
        for r in res:
            print(f"  ✗ {r}")
        print(f"\nGATE-STRUCTURED-PROSE (fixture {d.name}): {len(res)} finding(s)")
        return 1 if res else 0
    pairs = a.pairs or sorted(p.name[: -len("_config.py")] for p in (APP / "pair_configs").glob("*_config.py"))
    n_hard = n_debt = 0
    for p in pairs:
        cfg = APP / "pair_configs" / f"{p}_config.py"
        ws_path = REPO / "results" / p / "winner_summary.json"
        if not cfg.exists() or not ws_path.exists():
            print(f"[skip] {p}: config or winner_summary missing")
            continue
        ws = json.loads(ws_path.read_text())
        hard = str(ws.get("schema_version", "")).startswith("1.3")
        try:
            res = check_pair_files(cfg, ws_path, hard)
        except Exception as e:  # a config that cannot be imported cannot be verified
            res = [f"IMPORT {type(e).__name__}: {e}"]
        mark = ("FAIL" if hard else "debt") if res else "OK  "
        print(f"[{mark}] {p}{' (hard: schema 1.3)' if hard else ''}: {len(res)} finding(s)")
        for r in res[: (50 if hard else 5)]:
            print(f"         ✗ {r}")
        if hard:
            n_hard += len(res)
        else:
            n_debt += len(res)
    new, paid = check_components()
    print(f"[{'FAIL' if new else 'OK  '}] app/components pair-literal rule: {len(new)} new violation(s)")
    for r in new:
        print(f"         ✗ {r}")
    for r in paid:
        print(f"         · {r}")
    print(f"\nGATE-STRUCTURED-PROSE: {n_hard + len(new)} hard finding(s); {n_debt} debt finding(s) on legacy pairs")
    return 1 if (n_hard or new) else 0


if __name__ == "__main__":
    raise SystemExit(main())
