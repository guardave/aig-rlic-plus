#!/usr/bin/env python3
"""GATE-LEAD-FLOOR — lead-floor / lookahead enforcement (pure Python, no LLM).

Macro signals published after month-end must not be traded at lead 0 (lookahead).
Issue #255 recorded a per-pair `lead_floor` + anchored `lead_grid` in
docs/schemas/lead_axis_registry.json. gate_lead_axis.py only checks the lead AXIS
UNIT; this gate checks the lead VALUES actually scanned/published.

For every LIVE pair (has app/pages/<n>_<pair>_<section>.py):
  1. REGISTERED   pair must be in the registry (else FAIL).
  2. FLOOR/GRID   registry `lead_floor`, `lead_grid`, `position_shift` (0|1, default 0) and
                  `lead_floor_effective` = the STRICT floor on the effective lag E = lead + position_shift
                  (standard Step 2, amended 2026-10-16: the reading for period M may only drive a
                  position whose return window starts after the reading is public). When
                  `lead_floor_effective` is absent it is taken as lead_floor + position_shift; when
                  present it must equal lead_floor + position_shift (else FAIL "registry inconsistent").
  3. SCAN         statically parse every strategy script of the pair: scripts/pair_pipeline_<pair>.py,
                  scripts/econ_pipeline_<pair>.py, scripts/refresh_<pair>_lead_artifacts.py and any
                  other scripts/*<pair>*.py that DEFINES a traded grid. A grid definition is an
                  assignment to leads/LEADS/lead_times/lead_grid/lead_range/lead_list/lead_values
                  (optionally prefixed DAILY_/MONTHLY_/...), a dict entry "leads"/"lead_grid"/...,
                  or `for lead* in [literal grid]:` whose body calls `.shift(<loop var>)`
                  (diagnostic loops such as `for L in range(0,13)` are ignored). Literal lists /
                  range() / list(range()) / sorted(set) go through a restricted AST evaluator.
                  Plain name references (`"leads": leads`) carry no new grid and are ignored.
  4. SHIFT        per scanned file, detect an EXTRA position shift: `pos.shift(1) * ret` or
                  `.shift(lead).shift(1)` => 1; `pos * ret` with no shift => 0. Mixed or none
                  found => ambiguous => WARN (registry value used). Detected != registry
                  `position_shift` => FAIL ("alignment mismatch").
  5. RULES (all FAIL):  no grid found in any scanned file; unparseable grid / syntax error;
                  disagreeing duplicate grids; pipeline grid != registry lead_grid;
                  ANY scanned grid lead L with L + position_shift < lead_floor_effective (so
                  min(grid) + position_shift >= floor; the sub-floor leads are listed); any registry
                  lead_grid entry below the floor on the same basis; and ALWAYS effective lag < 1
                  (L0 with no extra shift trades the same bar whose return it earns).
  6. WINNER       results/<pair>/winner_summary.json lead_value (or lead_months/lead_days/
                  lead_quarters) + position_shift < lead_floor_effective -> FAIL.
No pair names are special-cased.

  7. MODE         --mode per-period (default; pkg12 point-in-time rule): the registry-floor comparisons in 2/5/6
                  (sub-floor grid leads, sub-floor winner) are replaced by a per-period count. For every grid lead
                  and the winner, with the detected (else registry) position shift, count the backtest periods
                  (latest results/<pair>/strategy_returns_*.csv, else winner_trade_log.csv dates) in which the
                  fixed-lag rule uses a reading of registry `release_calendar_series` whose first release
                  (data/release_calendar/release_calendar.csv; `rule:market_close` = observed at the close,
                  `rule:next_business_day` = posted the next business day) is after the close that opens the return
                  window. FAIL on any breaching period. Registry `alignment: pit_asof` + a `pit_shift(` call in a
                  canonical script => as-of alignment (scripts/_pit_align.py), 0 breaches by construction.
                  --mode floor: the 2026-10-16 fixed effective-lag floor (lead + shift >= lead_floor_effective).
                  Structural checks (grid parse/consistency, registry grid, shift alignment, effective lag >= 1)
                  run in both modes.

Usage:  python scripts/gate_lead_floor.py [--mode per-period|floor] [--json OUT.json] [--strict] [--repo DIR] [pair ...]
Exit non-zero on any FAIL. NOT wired into pre-commit (fails on known debt).
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GRID_NAME = re.compile(r"^((daily|weekly|monthly|quarterly|default|traded|tournament)_)?(leads|lead_times|lead_grid|lead_range|lead_list|lead_values)$", re.I)
LOOP_VAR = re.compile(r"^lead(_?\w*)?$", re.I)
POS_NAME = re.compile(r"^(pos|position|positions|pos_\w+|position_\w+)$", re.I)
PAGE_RE = re.compile(r"^\d+_(.+)_(story|evidence|strategy|methodology)\.py$")
WINNER_KEYS = ("lead_value", "lead_months", "lead_days", "lead_quarters", "lead_weeks")


class Unevaluable(Exception):
    pass


def _ev(node: ast.AST, env: dict):
    """Restricted evaluator: ints, list/tuple/set, range, list/sorted/tuple/set, +, known names."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [x for e in node.elts for x in [_ev(e, env)]]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_ev(node.operand, env)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        a, b = _ev(node.left, env), _ev(node.right, env)
        try:
            return a + b if isinstance(node.op, ast.Add) else a - b if isinstance(node.op, ast.Sub) else a * b
        except TypeError:
            raise Unevaluable
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        fn, args = node.func.id, [_ev(a, env) for a in node.args]
        if fn == "range" and 1 <= len(args) <= 3 and all(isinstance(a, int) for a in args):
            return list(range(*args))
        if fn in ("list", "tuple") and len(args) == 1 and isinstance(args[0], list):
            return list(args[0])
        if fn in ("sorted", "set") and len(args) == 1 and isinstance(args[0], list):
            return sorted(set(args[0]))
    raise Unevaluable


def extract_grids(src: str):
    """Return (defs, warns, derived): defs = [(line, name, grid)]; warns = [(line, name)] unparseable
    definitions; derived = [(line, name)] grids computed from data (`.unique()`, df[...]), which are views
    of an already-run tournament and cannot be evaluated statically."""
    tree = ast.parse(src)
    defs, warns, derived, env = [], [], [], {}

    def handle(name, value, line, in_dict=False):
        if isinstance(value, ast.Name):  # pure reference, carries no new grid
            return
        try:
            g = _ev(value, env)
        except (Unevaluable, TypeError):
            if not in_dict and any((isinstance(x, ast.Attribute) and x.attr in ("unique", "tolist", "values", "index", "columns"))
                                   or isinstance(x, ast.Subscript) for x in ast.walk(value)):
                derived.append((line, name))
            elif not in_dict:  # data-derived dict metadata (e.g. sorted(df[..].unique())) is not a grid definition
                warns.append((line, name))
            return
        if not isinstance(g, list) or not g or not all(isinstance(x, int) for x in g):
            return  # scalar / non-grid
        defs.append((line, name, [int(x) for x in g]))

    nodes = sorted((n for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.AnnAssign, ast.Dict, ast.For))),
                   key=lambda n: (n.lineno, getattr(n, "col_offset", 0)))
    for n in nodes:
        if isinstance(n, ast.For):
            if isinstance(n.target, ast.Name) and LOOP_VAR.match(n.target.id) and not isinstance(n.iter, ast.Name):
                uses = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "shift"
                           and c.args and isinstance(c.args[0], ast.Name) and c.args[0].id == n.target.id
                           for b in n.body for c in ast.walk(b))
                if uses:
                    handle(f"for {n.target.id}", n.iter, n.lineno)
            continue
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and GRID_NAME.match(k.value):
                    handle(k.value, v, k.lineno, in_dict=True)
            continue
        targets = n.targets if isinstance(n, ast.Assign) else [n.target]
        if n.value is None:
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                if GRID_NAME.match(t.id):
                    handle(t.id, n.value, n.lineno)
                try:  # track evaluable ints/lists so later references resolve
                    env[t.id] = _ev(n.value, env)
                except (Unevaluable, TypeError):
                    env.pop(t.id, None)
    return defs, warns, derived


RET_NAME = re.compile(r"^(ret|rets|returns?|\w*_ret|\w*_rets|\w*_returns?)$", re.I)


def _is_shift(node, arg=None) -> bool:
    """`<x>.shift(n)`, `.shift(periods=n)` or `.shift(n, ...)`; arg=None accepts any n, else n must equal arg."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "shift"):
        return False
    first = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "periods"), None)
    if first is None:
        return False
    return arg is None or (isinstance(first, ast.Constant) and first.value == arg)


def _posish(node) -> bool:
    return isinstance(node, ast.Name) and bool(POS_NAME.match(node.id))


def _retish(node) -> bool:
    """return-like operand: ret / *_ret / returns, also df["spy_ret"] and obj.spy_ret."""
    if isinstance(node, ast.Name):
        return bool(RET_NAME.match(node.id))
    if isinstance(node, ast.Attribute):
        return bool(RET_NAME.match(node.attr))
    if isinstance(node, ast.Subscript):
        sl = node.slice
        return isinstance(sl, ast.Constant) and isinstance(sl.value, str) and bool(RET_NAME.match(sl.value))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("fillna", "dropna", "reindex"):
        return _retish(node.func.value)
    return False


CHAIN_ATTRS = ("fillna", "astype", "reindex", "dropna", "clip")


def _core(node):
    """Strip trailing .fillna/.astype/.reindex/.dropna/.clip calls: `pos.shift(1).fillna(0)` -> `pos.shift(1)`."""
    while (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in CHAIN_ATTRS):
        node = node.func.value
    return node


def detect_position_shift(src: str):
    """Return (shift, line, note). shift in {0, 1, None}; None => ambiguous / undetectable.
    1: `<name>.shift(1|periods=1) * <ret>` in either order (<ret> return-like: ret, *_ret, returns, df["x_ret"]),
       a pos-named shifted operand times anything, or `<x>.shift(lead).shift(1)`.
    0: `<pos-named or lead-shifted name> * <ret>` with no shift(1) pattern anywhere."""
    tree = ast.parse(src)
    lead_built = set()  # names assigned from an expression containing .shift(<non-constant>)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(_is_shift(c) and not isinstance(
                (c.args[0] if c.args else c.keywords[0].value), ast.Constant) for c in ast.walk(n.value)):
            lead_built.update(t.id for t in n.targets if isinstance(t, ast.Name))
    shifted, bare = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult):
            for side, other in ((_core(n.left), n.right), (_core(n.right), n.left)):
                if _is_shift(side, 1) and (_posish(side.func.value) or _retish(other)):
                    shifted.append(n.lineno)
                elif isinstance(side, ast.Name) and (_posish(side) or side.id in lead_built) and _retish(other):
                    bare.append(n.lineno)
                elif _posish(side) and not isinstance(other, ast.Constant):
                    bare.append(n.lineno)
        if _is_shift(n, 1) and _is_shift(n.func.value) and not isinstance(
                (n.func.value.args[0] if n.func.value.args else n.func.value.keywords[0].value), ast.Constant):
            shifted.append(n.lineno)  # .shift(lead).shift(1)
    if shifted and not bare:
        return 1, shifted[0], ""
    if bare and not shifted:
        return 0, bare[0], ""
    if shifted and bare:
        return None, min(shifted + bare), f"mixed shifted (L{shifted[0]}) and unshifted (L{bare[0]}) position*return"
    return None, 0, "no position*return pattern found"


def scan_files(repo: Path, pair: str) -> list[Path]:
    sd = repo / "scripts"
    canon = [sd / f"pair_pipeline_{pair}.py", sd / f"econ_pipeline_{pair}.py", sd / f"refresh_{pair}_lead_artifacts.py"]
    out = [p for p in canon if p.exists()]
    pat = re.compile(rf"(?<![a-z0-9]){re.escape(pair)}(?![a-z0-9])")
    for p in sorted(sd.glob("*.py")):
        if p not in out and pat.search(p.name) and not p.name.startswith(("gate_", "test_")):
            out.append(p)
    return out


def live_pairs(repo: Path) -> list[str]:
    out = set()
    for p in (repo / "app" / "pages").glob("*.py"):
        m = PAGE_RE.match(p.name)
        if m:
            out.add(m.group(1))
    return sorted(out)


def winner_lead(repo: Path, pair: str):
    p = repo / "results" / pair / "winner_summary.json"
    if not p.exists():
        return None, None, "no winner_summary.json"
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        return None, None, f"unreadable: {type(e).__name__}"
    for k in WINNER_KEYS:
        if isinstance(d.get(k), (int, float)):
            return int(d[k]), k, str(p.relative_to(repo))
    return None, None, "no lead field"


def check_pair(repo: Path, pair: str, rec: dict | None, mode: str = "per-period") -> dict:
    res = {"pair": pair, "status": "PASS", "reasons": [], "floor": None, "grids": [], "winner_lead": None}
    fails, warns = [], []
    if rec is None:
        res.update(status="FAIL", reasons=["live pair not in lead_axis_registry.json (register it)"],
                   where="docs/schemas/lead_axis_registry.json")
        return res
    floor = rec.get("lead_floor")
    reg_grid = rec.get("lead_grid")
    res["floor"] = floor
    if not isinstance(floor, int):
        fails.append(f"registry has no integer lead_floor ({floor!r})")
    reg_shift = rec.get("position_shift", 0)
    if reg_shift not in (0, 1):
        fails.append(f"registry position_shift must be 0|1 ({reg_shift!r})")
        reg_shift = 0
    floor_eff = rec.get("lead_floor_effective")
    if floor_eff is None and isinstance(floor, int):
        floor_eff = floor + reg_shift  # strict floor on the effective lag
    elif isinstance(floor_eff, int) and isinstance(floor, int) and floor + reg_shift != floor_eff:
        fails.append(f"registry inconsistent: lead_floor {floor} + position_shift {reg_shift} != lead_floor_effective {floor_eff}")
    res["floor_effective"] = floor_eff
    if mode == "floor" and isinstance(floor_eff, int) and reg_grid:
        below = [g for g in reg_grid if g + reg_shift < floor_eff]
        if below:
            fails.append(f"registry lead_grid has sub-floor leads {below} (lead + shift {reg_shift} < floor E{floor_eff})")
    files = scan_files(repo, pair)
    canon = {repo / "scripts" / f"{k}_{pair}{suf}.py" for k, suf in (("pair_pipeline", ""), ("econ_pipeline", ""))}
    canon.add(repo / "scripts" / f"refresh_{pair}_lead_artifacts.py")
    where = f"scripts/*{pair}*.py"
    defs, file_grids = [], []  # defs: (line, name, grid, relpath)
    for f in files:
        rel = str(f.relative_to(repo))
        try:
            src = f.read_text()
            fd, uw, dv = extract_grids(src)
        except SyntaxError as e:
            fails.append(f"unparseable script, syntax error ({rel}:{e.lineno})")
            continue
        det, dline, dnote = detect_position_shift(src)
        if f not in canon and (not fd or det is None):
            continue  # extra scripts count only if they define a traded grid (grid + position*return)
        for line, name in uw:
            fails.append(f"unparseable grid '{name}' ({rel}:{line})")
        for line, name in dv:
            warns.append(f"data-derived grid '{name}' not statically verifiable ({rel}:{line})")
        if not fd:
            continue
        defs += [(l, n, g, rel) for l, n, g in fd]
        file_grids.append((rel, det, dline, dnote, min(min(g) for _, _, g in fd)))
        if det is None and reg_shift == 1:
            need = max(floor_eff if isinstance(floor_eff, int) else 0, 1)
            gm = min(min(g) for _, _, g in fd)
            if gm < need:
                fails.append(f"registry position_shift=1 is needed (min grid L{gm} < required lag {need}) but the code shift "
                             f"is not confirmed: {dnote} ({rel}:{dline or fd[0][0]})")
        if det is None:
            warns.append(f"position shift ambiguous: {dnote} ({rel}:{dline or fd[0][0]}); using registry position_shift={reg_shift}")
        elif det != reg_shift:
            fails.append(f"alignment mismatch: code position shift={det} ({rel}:{dline}) != registry position_shift={reg_shift}")
            where = f"{rel}:{dline}"
    if not defs and not any("unparseable" in x for x in fails):
        fails.append("no lead-grid definition found in any scanned script ("
                     + (", ".join(str(f.relative_to(repo)) for f in files) or f"no scripts/*{pair}*.py exist") + ")")
    res["grids"] = [{"file": r, "line": l, "name": n, "grid": g} for l, n, g, r in defs]
    uniq = {tuple(g) for _, _, g, _ in defs}
    if len(uniq) > 1:
        fails.append("inconsistent grids at " + ", ".join(f"{r}:{l} {n}={g[0]}..{g[-1]}({len(g)})" for l, n, g, r in defs))
    for rel, det, dline, dnote, gmin in file_grids:
        shift = det if det is not None else reg_shift
        eff = gmin + shift
        if mode == "floor" and isinstance(floor_eff, int):
            for l, n, g, r in defs:
                sub = [x for x in g if r == rel and x + shift < floor_eff]
                if sub:
                    fails.append(f"sub-floor leads {sub} in {n} ({rel}:{l}): effective lag L+shift {shift} = "
                                 f"{min(sub) + shift} < strict floor E{floor_eff} (min grid + shift must be >= floor)")
                    where = f"{rel}:{l}"
        if eff < 1:
            ln = next(l for l, n, g, r in defs if r == rel and min(g) == gmin)
            fails.append(f"effective lag {eff} < 1: L{gmin} with no extra position shift trades the same bar it earns (contemporaneous lookahead) ({rel}:{ln})")
            where = f"{rel}:{ln}"
    if reg_grid:
        rg = list(reg_grid)
        for l, n, g, r in defs:
            if g != rg:
                fails.append(f"grid {n}={g} != registry lead_grid {rg} ({r}:{l})")
    wl, wk, wdetail = winner_lead(repo, pair)
    res["winner_lead"] = wl
    if wl is None:
        warns.append(f"winner lead unavailable: {wdetail}")
    elif mode == "floor" and isinstance(floor_eff, int) and wl + reg_shift < floor_eff:
        fails.append(f"published winner {wk}={wl} + shift {reg_shift} = effective lag {wl + reg_shift} < strict floor E{floor_eff} ({wdetail})")
    pp_txt = ""
    if mode == "per-period":
        shifts = {det for _, det, _, _, _ in file_grids if det is not None}
        shift = shifts.pop() if len(shifts) == 1 else reg_shift
        leads = sorted({x for _, _, g, _ in defs for x in g} | ({wl} if wl is not None else set()))
        pf, pw, res["per_period"] = per_period_check(repo, pair, rec, leads, shift, wl, files, canon)
        fails += pf
        warns += pw
        pp_txt = "; " + res["per_period"].get("summary", "") if res.get("per_period") else ""
    res["reasons"] = fails + warns
    res["status"] = "FAIL" if fails else ("WARN" if warns else "PASS")
    if res["status"] == "PASS":
        g0 = sorted(uniq)[0] if uniq else None
        gtxt = f"L{g0[0]}..L{g0[-1]} (n={len(g0)})" if g0 else "n/a"
        res["reasons"] = [f"floor E{floor_eff} (L{floor}+shift {reg_shift}); grid {gtxt}; winner L{wl}; files {len(file_grids)}{pp_txt}"]
    res["where"] = where
    return res


PIT_CALL = re.compile(r"\bpit_shift\s*\(")
RULES = {"rule:market_close": 0, "rule:next_business_day": 1}
FREQ = {"months": "ME", "quarters": "QE", "trading_days": "B"}


def backtest_sample(repo: Path, pair: str):
    """(start, end, source) of the pair's backtest return rows: latest results/<pair>/strategy_returns_*.csv,
    else winner_trade_log.csv entry/exit dates. (None, None, why) when neither exists."""
    import pandas as pd
    d = repo / "results" / pair
    for f in sorted(d.glob("strategy_returns_*.csv"), reverse=True):
        if "_meta" in f.name:
            continue
        try:
            x = pd.read_csv(f, usecols=[0], parse_dates=[0]).iloc[:, 0].dropna()
        except Exception:
            continue
        if len(x):
            return x.min(), x.max(), str(f.relative_to(repo))
    f = d / "winner_trade_log.csv"
    if f.exists():
        x = pd.read_csv(f)
        cols = [c for c in ("entry_date", "exit_date") if c in x]
        if cols:
            v = pd.to_datetime(pd.concat([x[c] for c in cols]), errors="coerce").dropna()
            if len(v):
                return v.min(), v.max(), str(f.relative_to(repo))
    return None, None, "no strategy_returns_*.csv or winner_trade_log.csv"


def per_period_check(repo: Path, pair: str, rec: dict, leads: list, shift: int, wl, files, canon):
    """Point-in-time check (standard Step 2, pkg12): count the backtest periods in which a FIXED lag L uses a
    reading whose first release (data/release_calendar/release_calendar.csv) is after the return window opens.
    Zero breaching periods are required for every grid lead and the winner, unless the registry declares
    alignment 'pit_asof' AND the pair's canonical scripts call _pit_align.pit_shift (as-of alignment never uses an
    unreleased reading, by construction)."""
    import pandas as pd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _pit_align as pa
    fails, warns = [], []
    info = {"series": rec.get("release_calendar_series"), "alignment": rec.get("alignment", "fixed_lag"),
            "position_shift": shift, "by_lead": {}}
    series = info["series"]
    if not series:
        return ["per-period: registry has no release_calendar_series (calendar series id or rule:...)"], [], info
    if info["alignment"] == "pit_asof":
        callers = [str(f.relative_to(repo)) for f in files if f in canon and PIT_CALL.search(f.read_text())]
        if callers:
            info["summary"] = f"per-period: as-of aligned ({', '.join(callers)}), 0 breaches by construction"
            return [], [], info
        return ["per-period: registry alignment 'pit_asof' but no pit_shift( call in the canonical scripts"], [], info
    start, end, src = backtest_sample(repo, pair)
    info["sample_source"] = src
    if start is None:
        return [], [f"per-period: backtest sample unknown ({src}); breaches not counted"], info
    freq = FREQ.get(rec.get("lead_axis"), "ME")
    pad = (max(leads) if leads else 0) + pa.MAX_EXTRA + 2
    if freq == "B":
        idx = pd.date_range(start - pd.Timedelta(days=int(pad * 1.6) + 10), end, freq=pa.TRADING_DAY)
    else:
        off = pd.offsets.MonthEnd(pad) if freq == "ME" else pd.offsets.QuarterEnd(pad)
        idx = pd.date_range(start - off, end, freq=freq)
    if series in RULES:
        rel = pa.rule_release(idx, RULES[series])
    else:
        try:
            rel = pa.load_release(series, idx, repo / "data" / "release_calendar" / "release_calendar.csv")
        except (KeyError, FileNotFoundError) as e:
            return [f"per-period: release calendar unavailable for {series!r} ({type(e).__name__})"], [], info
    info.update(sample=f"{start.date()}..{end.date()}")
    bad = []
    for L in leads:
        b = pa.breaches(idx, L, rel, shift, start=start, end=end)
        info["by_lead"][L] = {"n": int(len(b)), "return_rows": [str(x.date()) for x in b.return_row]}
        if len(b):
            bad.append(L)
            first = ", ".join(str(x.date()) for x in b.return_row[:4]) + (", ..." if len(b) > 4 else "")
            who = "winner " if L == wl else ""
            nr = int(b.release.isna().sum())
            early = f"max {int(b.days_early.max())} d early" if b.days_early.notna().any() else ""
            fails.append(f"per-period: {who}L{L} + shift {shift} uses an unreleased {series} reading in {len(b)} "
                         f"backtest period(s) ({first}); " + "; ".join(x for x in (early, f"{nr} never released" if nr else "") if x))
    info["summary"] = (f"per-period: 0 breaching periods for leads {leads} ({series}, {info['sample']})" if not bad
                       else f"per-period: breaches at leads {bad}")
    return fails, warns, info


def run(repo: Path, requested: list[str], mode: str = "per-period") -> list[dict]:
    if mode not in ("per-period", "floor"):
        raise ValueError(f"mode must be 'per-period' or 'floor' ({mode!r})")
    reg = json.loads((repo / "docs" / "schemas" / "lead_axis_registry.json").read_text()).get("pairs", {})
    pairs = requested or live_pairs(repo)
    return [check_pair(repo, p, reg.get(p), mode) for p in pairs]


def main(argv: list[str]) -> int:
    repo, out_json, req, strict, mode = REPO, None, [], False, "per-period"
    it = iter(argv)
    for a in it:
        if a == "--json":
            out_json = next(it)
        elif a == "--mode":
            mode = next(it)
        elif a == "--strict":
            strict = True
        elif a == "--repo":
            repo = Path(next(it)).resolve()
        elif not a.startswith("-"):
            req.append(a)
    results = run(repo, req, mode)
    for r in results:
        print(f"{r['status']} {r['pair']}: " + " | ".join(r["reasons"]))
    c = {s: sum(r["status"] == s for r in results) for s in ("PASS", "FAIL", "WARN")}
    print(f"\nGATE-LEAD-FLOOR [{mode}]: {c['PASS']} PASS, {c['FAIL']} FAIL, {c['WARN']} WARN across {len(results)} live pair(s)"
          + (f"  [{c['WARN']} WARN = unverified, exit 0 unless --strict]" if c["WARN"] else ""))
    if out_json:
        Path(out_json).write_text(json.dumps({"summary": c, "pairs": results}, indent=2))
    return 1 if c["FAIL"] or (strict and c["WARN"]) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
