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
    f.setdefault("runner_up_is_sharpe", ru.get("objective_value"))
    f.setdefault("runner_up_oos_sharpe", ru.get("oos_sharpe"))
    f.setdefault("runner_up_lead", ru.get("lead_value"))
    leg = sel.get("legacy_oos_selected_row") or {}
    prev = [p for p in (sel.get("previously_published") or []) if isinstance(p, dict)]
    f["_legacy_oos_sharpe"] = [x for x in [leg.get("oos_sharpe")] + [p.get("oos_sharpe") for p in prev]
                               + [p.get("is_sharpe") for p in prev] + [p.get("hac_t") for p in prev]
                               if isinstance(x, (int, float))]
    f["_legacy_lead"] = [x for x in [leg.get("lead_value")] + [p.get("lead") for p in prev] if isinstance(x, (int, float))]
    ce = ws.get("cross_eval") or {}
    for k in ("main_winner_on_revised", "revised_winner_on_main"):
        if isinstance(ce.get(k), dict):
            f[f"_ce_{k}_is"] = ce[k].get("is_sharpe")
            f[f"_ce_{k}_oos"] = ce[k].get("oos_sharpe")
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
def sentences(text: str) -> list[str]:
    text = re.sub(r"[*_`#>]", "", text)
    parts = re.split(r"(?<=[.!?;])\s+|\n\s*[-•]\s+|\n{2,}", text)
    return [p.strip() for p in parts if p and p.strip()]


def check_text(text: str, f: dict, where: str) -> list[str]:
    """Findings for one rendered prose string."""
    out = []
    in_is = str(f.get("_objective") or "").startswith("max_is_sharpe")
    for s in sentences(text):
        legacy = bool(LEGACY_LABEL.search(s))
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


def handtyped(cfg_path: Path, f: dict) -> list[str]:
    """HANDTYPED: result numbers typed as literals in a migrated config's source (formatted fields are masked)."""
    tree = ast.parse(cfg_path.read_text())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            text = "".join(v.value if isinstance(v, ast.Constant) else "⟨F⟩" for v in node.values)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        else:
            continue
        for s in sentences(text):
            if re.search(r"sharpe", s, re.I) and not EVIDENCE_EXEMPT.search(s) and re.search(SHARPE_NUM, s):
                out.append(f"HANDTYPED line {node.lineno}: Sharpe number typed in the source — \"{s[:140]}\"")
            if not EVIDENCE_EXEMPT.search(s):
                for pat in LEAD_PATTERNS:
                    for m in re.finditer(pat, s, re.I):
                        if _to_int(m.group("n")) is not None:
                            out.append(f"HANDTYPED line {node.lineno}: lead typed in the source \"{m.group(0)}\"")
            for m in re.finditer(COUNT_PATTERN, s, re.I):
                out.append(f"HANDTYPED line {node.lineno}: candidate count typed in the source \"{m.group(0)}\"")
    return sorted(set(out))


def check_pair_files(cfg: Path, ws_path: Path, hard: bool) -> list[str]:
    ws = json.loads(ws_path.read_text())
    f = fields_from_summary(ws)
    findings = []
    for where, text in config_prose(cfg):
        findings += check_text(text, f, where)
    if hard:
        findings += handtyped(cfg, f)
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
