#!/usr/bin/env python3
"""GATE-CONSISTENCY — cross-artifact winner consistency (pure Python, no LLM).

The winner is described in many places: winner_summary.json (the anchor), the
native tournament (the selection source), kpis.json, the lead-coherence artifacts,
and the pair's narrative config. A re-selection (or any edit) that fails to
propagate leaves the report internally contradictory. This scanner anchors on
winner_summary and verifies every other surface agrees.

HARD checks (fail the gate):
  A. winner_summary's combo exists in tournament_results at its lead, Sharpe within tol.
  B. winner_summary is the MAX valid selection-objective value on the grid (OOS Sharpe
     by default; IS Sharpe when selection.objective == "max_is_sharpe", GH #251) — i.e. no valid
     combo beats it (selection is internally consistent; a beating combo means a
     pending re-selection that has not propagated).
  C. kpis.json "OOS Sharpe (winner)" == winner_summary.oos_sharpe (2dp).
  D. lead_winner_curve (if present): the is_published_winner row's lead + Sharpe
     match winner_summary.

SOFT checks (report, don't fail — prose parsing is fuzzy):
  E. the narrative config states the CURRENT winner: Sharpe (4dp/2dp), lead (any unit),
     threshold code, and -- where the `sig / thr / dir / Ln` notation is used --
     that notation must include the winner combo. Also, scoped to winner-describing sentences
     ('winner', 'best strategy', 'headline', the winner Sharpe): direction, lead binding and
     signal identity. `INFO:` lines mean a field could not be verified (not a warning, not a pass). Soft because prose is human-authored
     (runner-ups / legacy comparisons are legal) and parsing is fuzzy; the artifact checks
     A-D stay hard. Any E warning means the prose needs a human re-read before publishing.

Exit non-zero if any HARD check fails for any pair.

Usage:  python scripts/gate_consistency.py [pair ...]
"""
from __future__ import annotations

import csv
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHARPE_TOL = 0.01


def _read_csv(path: Path):
    with open(path) as f:
        return list(csv.DictReader(f))


def _latest(pair: str, stem: str):
    c = sorted((REPO / "results" / pair).glob(f"{stem}_*.csv"))
    c = [p for p in c if re.match(rf"^{re.escape(stem)}_\d{{8}}\.csv$", p.name)]
    return c[-1] if c else None


def _native_sig(pair: str, signal_code: str) -> str:
    # best-effort code->native strip; both the stem and the leading token are tried
    stem = pair.rsplit("_", 1)[0]
    for pref in (f"{stem}_", f"{stem.split('_')[0]}_"):
        if signal_code.startswith(pref):
            return signal_code[len(pref):]
    return signal_code


def _contaminated_signals(rdir: Path) -> set:
    """Seasonally-contaminated signal codes excluded from selection (from the
    lead_sweep_manifest); empty for pairs with none."""
    mans = [p for p in sorted(rdir.glob("lead_sweep_manifest_*.json")) if "weekly" not in p.name]
    if not mans:
        return set()
    try:
        return set(json.loads(mans[-1].read_text()).get("seasonally_contaminated_signals") or [])
    except Exception:
        return set()


# Winner-combo notation used in the pair prose: `signal / threshold / [strategy] direction / L<n>`
_TRIPLE_RE = re.compile(
    r"`?([A-Za-z][\w.]*) ?/ ?(T[\w.]*) ?/ ?(?:P\d\w* ?)?((?:\w*_)?[A-Za-z]*cyclical) ?/ ?L(\d+)")


def _norm_dir(s: str) -> str:
    """Normalise direction spellings: pro/procyclical/pro_cyclical -> 'procyclical';
    cc/countercyclical/counter_cyclical/counter-cyclical -> 'countercyclical'; else ''."""
    t = re.sub(r"[-_ ]", "", (s or "").lower())
    if t == "cc" or "counter" in t:
        return "countercyclical"
    if t in ("pro", "procyclical") or t.endswith("procyclical") or t.endswith("cyclical"):
        return "procyclical"
    return ""


_DIR_RE = re.compile(r"\b(counter[-_ ]?cyclical|pro[-_ ]?cyclical)\b", re.I)
# a clause that contrasts the winner with something else may legally name other values
_CONTRAST_RE = re.compile(
    r"opposite|contradict|\bprior\b|expected|hypothes|runner|instead|unlike|rather than|whereas|"
    r"legacy|previous|former|stale|\bother\b|alternative|earlier|version|concurrent|quartile|natural|original|compar|side by side|contemporaneous|descriptive|would", re.I)
_WINNER_KEY_RE = re.compile(r"\bwinner|\bwinning\b|best strateg|\bheadline\b|selected rule|\bchampion", re.I)
# lead mentions explicitly tagged as a lead: L9 / L6q / lead-0 / lead of 3 / 3-quarter lead / same-day
_LEAD_TAG_RES = (
    re.compile(r"(?<![\w])L(\d+)(?!\d)"),
    re.compile(r"\blead[- ](?:of )?(\d+)(?!\d)", re.I),
    re.compile(r"\b(\d+)[- ](?:trading[- ])?(?:day|quarter|month|week)s?(?:[- ]ahead)?\s+lead\b", re.I),
)
_SAME_DAY_RE = re.compile(r"\bsame[- ]day\b|\bzero[- ]lead\b", re.I)


def _lead_mentioned(txt: str, n: int, unit: str) -> bool:
    """True if the prose states lead n: `L<n>` (L4, L4q, L4Q), `<n>-quarter`/`<n> months`,
    daily phrasings (`21-day`, `21 trading days`, `21d`), or 'same-day' for lead 0."""
    word = unit.rstrip("s")
    if re.search(rf"\bL{n}(?!\d)", txt) or re.search(rf"\b{n}[- ](?:trading[- ])?{word}", txt, re.I):
        return True
    if word == "day" and re.search(rf"(?<![\w.]){n}d\b", txt):
        return True
    return n == 0 and bool(_SAME_DAY_RE.search(txt))


def _clean_prose(txt: str) -> str:
    """Undo python source layout: join implicit string concatenation and soft-wrapped lines."""
    txt = re.sub(r'["\']\s*\n\s*[frbFRB]*["\']', " ", txt)
    txt = re.sub(r"(?<!\n)\n(?!\s*(?:[-*#|>]|\d+[.)]|\n))[ \t]*", " ", txt)
    return txt


def winner_context(txt: str, ws: dict):
    """(sentences, clauses) of the prose that DESCRIBE THE WINNER: contain 'winner' / 'best strategy'
    / 'headline', or the winner's Sharpe, or the combo triple. Contrast clauses are dropped by callers."""
    sharpe = float(ws["oos_sharpe"])
    nums = [f"{sharpe:.4f}", f"{sharpe:.2f}"]
    sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z`\"*(])|\n|[\"'] ?[)\]}]+ ?,? ?|[\"'] ?, ", _clean_prose(txt)) if x.strip()]

    def is_w(x):
        return bool(_WINNER_KEY_RE.search(x) or any(re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", x) for n in nums))
    wins, nxt = [], set()
    for i, x in enumerate(sents):
        if is_w(x):
            wins.append(x)
            if i + 1 < len(sents):
                nxt.add(sents[i + 1])
    clauses = [c.strip() for x in wins for c in x.split(";") if _WINNER_KEY_RE.search(c)
               or any(n in c for n in nums)]
    return wins, sorted(nxt - set(wins)), clauses


def _signal_aliases(code: str, column: str, display: str) -> set:
    """Normalised (lowercase alnum) aliases of a signal from its code, data column and display label."""
    out = set()
    for v in {code, column, display, code.split("_", 1)[-1] if "_" in code else code}:
        n = re.sub(r"[^a-z0-9]", "", (v or "").lower())
        if len(n) >= 4:
            out.add(n)
    return out


_KIND_WORDS = {"zscore": r"z[- ]?score", "pctrank": r"percentile|pct[- ]?rank|rank", "roc": r"roc|rate of change|change",
               "mom": r"mom|momentum|change", "chg": r"change|chg", "diff": r"change|diff", "yoy": r"yoy|year[- ]over[- ]year"}


def _signal_in_text(code: str, aliases: set, txt: str) -> bool:
    flat = re.sub(r"[^a-z0-9]", "", txt.lower())
    if any(a in flat for a in aliases):
        return True
    # human form: kind word within 25 chars of the window number, e.g. '126-day z-score', 'z-score of 126'
    m = re.search(r"([a-z]+)_?(\d+)", code.lower())
    if m:
        kind = next((k for k in _KIND_WORDS if k in code.lower()), None)
        if kind:
            w, kw = m.group(2), _KIND_WORDS[kind]
            return bool(re.search(rf"(?<!\d){w}(?!\d).{{0,25}}(?:{kw})|(?:{kw}).{{0,25}}(?<!\d){w}(?!\d)", txt, re.I))
    return False


def check_prose(txt: str, ws: dict, other_signals: dict | None = None) -> list[str]:
    """Check E (soft). Structured comparison of the prose against winner_summary:
    Sharpe, lead, threshold code, and any `sig / thr / dir / Ln` combo notation; plus -- scoped to
    winner-describing sentences ('winner', 'best strategy', 'headline', or the winner Sharpe) --
    direction, lead binding and signal identity. Mentions of OTHER combos (runner-up, comparisons)
    are legal, so a mismatch is only reported when the winner context never states the current value.
    `other_signals` maps the OTHER tournament signal codes -> data columns (for signal mismatch).
    Lines starting 'INFO:' are not warnings: they mark a field that could not be verified."""
    out: list[str] = []
    lead = int(ws.get("lead_value", ws.get("lead_months")))
    sharpe = float(ws["oos_sharpe"])
    unit = ws.get("lead_unit") or "months"
    s4, s2 = f"{sharpe:.4f}", f"{sharpe:.2f}"
    if s4 not in txt and s2 not in txt:
        out.append(f"E: config cites neither {s4} nor {s2} — prose may show a stale winner Sharpe")
    if not _lead_mentioned(txt, lead, unit):
        out.append(f"E: config does not mention winner lead L{lead} ({unit})")
    thr = ws.get("threshold_code", "")
    if thr and not re.search(rf"(?<![\w.]){re.escape(thr)}(?![\w.])", txt):
        out.append(f"E: config never names winner threshold '{thr}' — prose may describe a stale rule")
    sig = ws.get("signal_code", "")
    wdir = _norm_dir(ws.get("direction") or "")
    triples = [(m.group(1), m.group(2), _norm_dir(m.group(3)), int(m.group(4))) for m in _TRIPLE_RE.finditer(txt)]
    if triples:
        def _is_winner(t):
            return (t[1] == thr and t[3] == lead and t[2] == wdir
                    and t[0].split("_")[-1] == sig.split("_")[-1])  # tolerate pair-prefix naming
        if not any(_is_winner(t) for t in triples):
            seen = sorted({f"{a}/{b}/{c}/L{d}" for a, b, c, d in triples})
            out.append(f"E: prose states combo(s) {seen[:3]} but none equals the winner "
                       f"{sig}/{thr}/{ws.get('direction')}/L{lead}")

    # ---- winner-scoped checks (direction, lead binding, signal identity) ----
    wins, nexts, clauses = winner_context(txt, ws)
    # a following sentence counts only when it is plainly about the winner's orientation
    follow = [x for x in nexts if re.match(r"\W*(?:the|this)\s+(?:pro|counter)[-_ ]?cyclical\s+"
                                          r"(?:orientation|direction|rule|reading|signal|strategy)", x, re.I)]
    # a clause speaks for the winner only if it names the winner / its Sharpe, or says orientation/rule/family
    _own = re.compile(r"\bwinn|best strateg|\bheadline\b|orientation|direction\W{0,3}:|\bfamily\b", re.I)
    all_cl = [c for x in wins + follow for c in re.split(r";|\u2014|\bbut\b|\byet\b|\bwhile\b|\bwhereas\b", x)
              if _own.search(c) or any(re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", c) for n in (s4, s2))]
    # Every plain winner clause that states a direction must state the winner's (a clause naming both
    # is a contrast and passes). Clauses contrasting with a prior / runner-up may legally name the other
    # direction, so they are only used when no plain clause states one (then: aggregate).
    plain = [{_norm_dir(m) for m in _DIR_RE.findall(c)} for c in all_cl if not _CONTRAST_RE.search(c)]
    plain = [d for d in plain if d]
    if plain:
        bad = sorted({x for d in plain if wdir not in d for x in d})
        dirs = {wdir} if not bad else set(bad)
    else:
        dirs = {_norm_dir(m) for c in all_cl for m in _DIR_RE.findall(c)}
    if wdir and dirs and wdir not in dirs:
        out.append(f"E: winner-describing prose states direction {sorted(dirs)} but the winner is {wdir}")
    elif wdir and not dirs:
        out.append(f"INFO: direction '{wdir}' is unverifiable (winner-describing text never states a direction) — NOT verified")
    leads = set()
    for c in clauses:
        if _CONTRAST_RE.search(c):
            continue
        for r in _LEAD_TAG_RES:
            leads |= {int(v) for v in r.findall(c)}
        if _SAME_DAY_RE.search(c):
            leads.add(0)
    if leads and lead not in leads:
        out.append(f"E: winner-describing prose states lead(s) {sorted(leads)} but the winner is L{lead} ({unit})")
    elif not leads:
        out.append(f"INFO: lead L{lead} is unverifiable in winner-describing text (no tagged lead there) — NOT bound")
    wtxt = " ".join(wins)
    aliases = _signal_aliases(sig, ws.get("signal_column", ""), ws.get("signal_display_name", ""))
    if wins and sig:
        if _signal_in_text(sig, aliases, wtxt) or any(a in re.sub(r"[^a-z0-9]", "", wtxt.lower()) for a in aliases):
            pass
        else:
            hit = next((c for c, col in (other_signals or {}).items()
                        if c != sig and _signal_in_text(c, _signal_aliases(c, col, ""), wtxt)), None)
            if hit:
                out.append(f"E: winner-describing prose names signal '{hit}', not the winner signal '{sig}'")
            else:
                out.append(f"INFO: signal '{sig}' is unverifiable in prose (no alias of it appears in "
                           f"winner-describing text) — NOT verified")
    elif sig:
        out.append(f"INFO: no winner-describing text found — signal/direction/lead binding not verified")
    return out


def check_pair(pair: str) -> tuple[list[str], list[str]]:
    """(hard_failures, soft_warnings)."""
    rdir = REPO / "results" / pair
    ws_path = rdir / "winner_summary.json"
    if not ws_path.exists():
        return [], ["no winner_summary.json — skipped"]
    ws = json.loads(ws_path.read_text())
    hard: list[str] = []
    soft: list[str] = []

    win_lead = int(ws.get("lead_value", ws.get("lead_months")))
    win_sharpe = float(ws["oos_sharpe"])
    sig_code = ws.get("signal_code", "")
    contaminated = _contaminated_signals(rdir)
    other_sigs: dict = {}

    # ── A + B: against the native tournament (selection source) ──
    tr_files = sorted(rdir.glob("tournament_results_*.csv"))
    if tr_files:
        rows = [r for r in _read_csv(tr_files[-1]) if r["signal"] != "BENCHMARK"]
        lk = next((k for k in rows[0] if k.startswith("lead_")), None) if rows else None

        def _f(r, k):
            try:
                return float(r[k])
            except (KeyError, ValueError):
                return float("nan")

        if lk is None:
            soft.append("tournament_results has no lead column")
        else:
            valids = [r for r in rows if str(r.get("valid", "True")).lower() == "true"]
            # A (naming-independent): the winner Sharpe must be reproduced by SOME
            # valid combo at the winner's own lead. Signal-code<->native-name maps
            # vary per pair, so anchor on (lead, Sharpe), not the combo string.
            at_lead = [r for r in valids if int(float(r[lk])) == win_lead]
            if not any(abs(_f(r, "oos_sharpe") - win_sharpe) <= SHARPE_TOL for r in at_lead):
                hard.append(f"A: winner OOS Sharpe {win_sharpe} is not reproduced by any "
                            f"valid combo at L{win_lead} in tournament_results "
                            f"(winner_summary vs selection source drift)")
            # B: winner must be the max valid CLEAN combo (excluding seasonally-
            # contaminated signals, which are validly excluded from selection).
            clean = [r for r in valids if r["signal"] not in contaminated]
            # GH #251/#268: when selection.objective == max_is_sharpe the selection
            # metric is the IN-SAMPLE Sharpe; OOS Sharpe is evaluation-only and a
            # higher-OOS combo is expected, not a propagation failure.
            objective = (ws.get("selection") or {}).get("objective", "max_oos_sharpe")
            if clean and objective == "max_is_sharpe":
                if "is_sharpe" not in ws:
                    hard.append("B: objective max_is_sharpe but winner_summary has no is_sharpe")
                else:
                    win_is = float(ws["is_sharpe"])
                    top = max(clean, key=lambda r: _f(r, "is_sharpe"))
                    if _f(top, "is_sharpe") > win_is + SHARPE_TOL:
                        hard.append(f"B: a valid, non-excluded combo beats the published winner on IS Sharpe "
                                    f"— {top['signal']}/{top['threshold']}/{top['strategy']}/"
                                    f"L{int(float(top[lk]))} = {top['is_sharpe']} > winner IS {win_is}")
            elif clean:
                top = max(clean, key=lambda r: _f(r, "oos_sharpe"))
                if _f(top, "oos_sharpe") > win_sharpe + SHARPE_TOL:
                    hard.append(f"B: a valid, non-excluded combo beats the published winner "
                                f"— {top['signal']}/{top['threshold']}/{top['strategy']}/"
                                f"L{int(float(top[lk]))} = {top['oos_sharpe']} > winner "
                                f"{win_sharpe} (pending re-selection not propagated)")
            # soft: does the winner's signal code map onto a tournament signal?
            sigs = {r["signal"] for r in rows}
            other_sigs.update({r["signal"]: r.get("signal_column", "") for r in rows})
            if sig_code and sig_code not in sigs and _native_sig(pair, sig_code) not in sigs:
                soft.append(f"signal_code '{sig_code}' does not obviously map to a "
                            f"tournament signal {sorted(sigs)[:6]}… (naming, likely benign)")
    else:
        soft.append("no tournament_results — cannot verify selection")

    # ── C: kpis.json winner Sharpe ──
    kpi_path = rdir / "kpis.json"
    if kpi_path.exists():
        try:
            kpis = json.loads(kpi_path.read_text())
            wk = next((k for k in kpis if isinstance(k, dict)
                       and "sharpe" in str(k.get("metric", "")).lower()
                       and "winner" in str(k.get("metric", "")).lower()), None)
            if wk and abs(float(str(wk["value"])) - round(win_sharpe, 2)) > 0.011:
                hard.append(f"C: kpis.json winner Sharpe {wk['value']} != "
                            f"winner_summary {win_sharpe:.2f}")
        except Exception as e:
            soft.append(f"kpis.json unreadable: {type(e).__name__}")

    # ── D: lead_winner_curve marker ──
    wc_path = _latest(pair, "lead_winner_curve")
    if wc_path:
        wc = _read_csv(wc_path)
        lk = next(k for k in wc[0] if k.startswith("lead_"))
        flagged = [r for r in wc if str(r["is_published_winner"]).lower() == "true"]
        if len(flagged) != 1:
            hard.append(f"D: lead_winner_curve has {len(flagged)} winner flags (expected 1)")
        elif int(flagged[0][lk]) != win_lead:
            hard.append(f"D: lead_winner_curve winner flag at L{flagged[0][lk]} != "
                        f"winner_summary L{win_lead}")
        elif abs(float(flagged[0]["oos_sharpe"]) - win_sharpe) > SHARPE_TOL:
            hard.append(f"D: lead_winner_curve winner Sharpe {flagged[0]['oos_sharpe']} "
                        f"!= winner_summary {win_sharpe}")

    # ── E (soft): narrative config cites the CURRENT winner ──
    cfg = REPO / "app" / "pair_configs" / f"{pair}_config.py"
    if cfg.exists():
        soft.extend(check_prose(cfg.read_text(), ws, other_sigs))

    return hard, soft


def main() -> int:
    pairs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not pairs:
        pairs = sorted(p.name for p in (REPO / "results").iterdir()
                       if p.is_dir() and (p / "winner_summary.json").exists()
                       and not p.name.endswith("_archived"))
    total_hard = 0
    for p in pairs:
        try:
            hard, soft = check_pair(p)
        except Exception as e:
            hard, soft = [f"scan error: {type(e).__name__}: {e}"], []
        warns = [x for x in soft if not x.startswith("INFO:")]
        mark = "FAIL" if hard else ("warn" if warns else "OK  ")
        print(f"[{mark}] {p}")
        for h in hard:
            print(f"         ✗ {h}")
        for s in soft:
            print(f"         · {s}")
        total_hard += len(hard)
    print(f"\nGATE-CONSISTENCY: {total_hard} hard failure(s) across {len(pairs)} pairs")
    return 1 if total_hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
