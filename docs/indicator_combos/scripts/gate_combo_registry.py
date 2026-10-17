"""GATE-COMBO-REGISTRY (revision 3): compliance gate for the indicator-combination ledger (pure Python, no LLM).

Validates docs/indicator_combos/registry/{hypotheses,families}.yaml against registry/schema.json and a set of
semantic rules, and keeps COMPLIANCE.md / registry/compliance.csv in sync.

  S0  JSON-schema validation (missing / mistyped fields give messages, never a crash)
  R2  every question and hypothesis family exists in families.yaml
  R3  baselines B1, B2a, B3, B4 are "yes: ..." or "n/a: <reason>" (schema pattern)
  R4  pass rules: numeric margin, a test from the enumerated set, alpha in (0, 0.10] or an interval level (schema)
  R5  purge_months == label_horizon_months == the horizon implied by the endpoint's label definition
  R6  question status agrees with its hypotheses' statuses; descriptive <=> an estimand and no hypotheses;
      hypothesis ids carry the question id and are unique; hypothesis members exist in the question
  R7  confirmatory hypotheses: every rule parameter is "citation" or "natural"; members only vintage / market /
      snapshot_forward / label / derived tracks; no fleet winners; influenced_by == [none]; primary validation
      only V-C / V-S; a null is named; provenance label "discovery-informed prospective confirmation"
  R8  V-D (viewed OOS) never in a primary validation
  R9  an influenced question has no confirmatory hypothesis
  R10 recession classification (U4) questions with hypotheses name a LORO evaluation
  R11 state-dependence questions (D1-04, D1-05, D1-06, D1-17): interaction endpoints and min_events >= 5
  R12 Sahm: a confirmatory sahm_threshold_pp must be the number 0.50; a question with any other Sahm threshold
      must also carry 0.50 (as a hypothesis or as comparator_sahm_threshold_pp)
  R13 U3 (relative-return) questions do not use V-B (pre-1999 sector indices are price-only)
  R14 exactly 10 ranked questions, ranks 1..10
  R15 families: hypothesis counts match; a correction method other than "none" wherever the family has
      hypotheses of that kind
  R16 QUESTION_BANK.md has a heading per question id; COMPLIANCE.md and compliance.csv are current
  R17 member tracks agree with real data availability: vintage => an ALFRED vintage file exists, or pending_gap
      names the data gap to close before any evaluation; market => gate whitelist and not a macro release series;
      snapshot_forward => a no-archive snapshot source; revised => a release-calendar or snapshot series;
      label => NBER; derived => DERIVED; fleet => FLEET

Modes: default reads the working tree; --staged reads the INDEX (`git show :path`), which is what the pre-commit
hook uses; --write regenerates COMPLIANCE.md and compliance.csv in the working tree.
Limits: the hook runs only if `git config core.hooksPath scripts/hooks` is set, and `git commit --no-verify`
bypasses it. Labels such as source_type and influenced_by are declared by the author; the gate checks their
consistency, not their truth.
"""
from __future__ import annotations

import csv
import io
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[3]
SUB = "docs/indicator_combos"
MARKET = {"T10Y3M", "GS10_TB3MS", "HY_IG_OAS", "HY_OAS", "BAA_AAA", "VIX", "VIX3M", "GOLD_COPPER", "GOLD", "SOX_SPY",
          "SPY", "SPX_SECTOR_INDICES", "FEDFUNDS", "DGS10"}
CONF_TRACKS = {"vintage", "market", "snapshot_forward", "label", "derived"}
STATE_IDS = {"D1-04", "D1-05", "D1-06", "D1-17"}
HORIZON_PARAM = {"cvar_overlay": "return_horizon_months", "interaction": "return_horizon_months",
                 "information_ratio": "return_horizon_months", "forward_return_diff": "return_horizon_months",
                 "log_score": "return_horizon_months", "plateau_k": "return_horizon_months",
                 "capture_share": "return_horizon_months", "false_exit_rate": "return_horizon_months",
                 "lexicographic_recession": "recall_window_pre_peak_months", "brier_skill": "forecast_horizon_months",
                 "missed_rally": "measure_window_months", "pr_difference": "window_overlap_months"}
COLS = ["hid", "question", "family", "status", "use_case", "asset", "endpoint_type", "endpoint_statistic",
        "comparator", "margin", "margin_unit", "test", "alpha_or_interval", "guardrail", "min_events",
        "label_horizon_months", "purge_months", "B1", "B2a", "B3", "B4", "null_design", "validation_primary",
        "validation_supporting", "parameter_sources", "priority", "rank"]


class Source:
    """Reads repository files from the working tree or from the git index (staged blobs)."""

    def __init__(self, repo: Path, staged: bool):
        self.repo, self.staged = repo, staged

    def read(self, rel: str) -> str | None:
        if self.staged:
            r = subprocess.run(["git", "-C", str(self.repo), "show", f":{rel}"], capture_output=True, text=True)
            return r.stdout if r.returncode == 0 else None
        p = self.repo / rel
        return p.read_text() if p.exists() else None

    def exists(self, rel: str) -> bool:
        if self.staged:
            return subprocess.run(["git", "-C", str(self.repo), "cat-file", "-e", f":{rel}"],
                                  capture_output=True).returncode == 0
        return (self.repo / rel).exists()


def macro_series(src: Source) -> tuple[set[str], set[str]]:
    cal = src.read("data/release_calendar/release_calendar.csv") or ""
    calendar = {line.split(",", 1)[0] for line in cal.splitlines()[1:] if line}
    man = src.read("data/release_calendar/snapshots/20261016T232733Z/manifest.json") or "{}"
    snaps = set(yaml.safe_load(man).get("sources", {}))
    return calendar, snaps


def tokens(text: str) -> set[str]:
    return set(re.findall(r"\bV-[A-DS]\b", text or ""))


def flat(x) -> str:
    return " ".join(str(x).split())


def rows(qs: list[dict]) -> list[dict]:
    out = []
    for q in qs:
        b, v = q.get("baselines", {}), q.get("validation", {})
        common = {"question": q.get("id"), "use_case": q.get("use_case"), "B1": b.get("B1"), "B2a": b.get("B2a"),
                  "B3": b.get("B3"), "B4": b.get("B4"), "null_design": q.get("null_design"),
                  "validation_primary": v.get("primary"), "validation_supporting": v.get("supporting"),
                  "priority": q.get("priority"), "rank": "" if q.get("rank") is None else q.get("rank")}
        if not q.get("hypotheses"):
            e = q.get("estimand", {})
            out.append({**common, "hid": f"{q.get('id')}.E", "family": q.get("family"), "status": "descriptive",
                        "asset": "", "endpoint_type": "estimand", "endpoint_statistic": flat(e.get("statistic")),
                        "comparator": "", "margin": "", "margin_unit": flat(e.get("decision_rule")), "test": "",
                        "alpha_or_interval": flat(e.get("interval")), "guardrail": "", "min_events": "",
                        "label_horizon_months": e.get("label_horizon_months"), "purge_months": e.get("purge_months"),
                        "parameter_sources": ""})
        for h in q.get("hypotheses") or []:
            ep, pr = h.get("endpoint", {}), h.get("pass_rule", {})
            out.append({**common, "hid": h.get("hid"), "family": h.get("family"), "status": h.get("status"),
                        "asset": h.get("asset"), "endpoint_type": ep.get("type"),
                        "endpoint_statistic": flat(ep.get("statistic")), "comparator": flat(ep.get("comparator")),
                        "margin": pr.get("margin"), "margin_unit": flat(pr.get("margin_unit")), "test": pr.get("test"),
                        "alpha_or_interval": f"alpha {pr['alpha']}" if "alpha" in pr else
                        f"{pr.get('interval_level')} interval",
                        "guardrail": flat(pr.get("guardrail", "")), "min_events": h.get("min_events"),
                        "label_horizon_months": h.get("label_horizon_months"), "purge_months": h.get("purge_months"),
                        "parameter_sources": "; ".join(f"{p.get('name')}={p.get('value')} ({p.get('source_type')})"
                                                        for p in h.get("parameters", []))})
    return sorted(out, key=lambda r: (str(r["family"]), str(r["hid"])))


def render_csv(rs: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rs)
    return buf.getvalue()


def render_md(rs: list[dict], fams: dict) -> str:
    esc = lambda x: str(x).replace("|", "/")
    L = ["# Compliance table (generated; do not edit)", "",
         "Generated by `scripts/gate_combo_registry.py --write` from `registry/hypotheses.yaml` and "
         "`registry/families.yaml`; one row per hypothesis (descriptive questions: one estimand row). The gate "
         "fails when this file is stale. Field meanings: QUESTION_BANK.md section 0.", "",
         "## Families", "",
         "| Family | Name | Hypotheses | Confirmatory | Correction (confirmatory) | Correction (exploratory) |",
         "|---|---|--:|--:|---|---|"]
    for k, f in fams.items():
        cc, ce = f.get("correction_confirmatory", {}), f.get("correction_exploratory", {})
        L.append(f"| {k} | {esc(f.get('name'))} | {f.get('n_total')} | {f.get('n_confirmatory')} | "
                 f"{cc.get('method')}: {esc(flat(cc.get('detail')))} | {ce.get('method')}: {esc(flat(ce.get('detail')))} |")
    nt = sum(f.get("n_total", 0) for f in fams.values())
    nc = sum(f.get("n_confirmatory", 0) for f in fams.values())
    ncf = sum(1 for f in fams.values() if f.get("n_confirmatory", 0) > 0)
    L += ["", f"Total: {nt} registered hypotheses; {nc} confirmatory (discovery-informed prospective "
          f"confirmations) in {ncf} families.", "", "## Hypotheses", ""]
    for r in rs:
        L += [f"### {r['hid']} · {r['family']} · {r['status']} · {r['use_case']}"
              + (f" · rank {r['rank']}" if r["rank"] != "" else ""), "", "| Field | Value |", "|---|---|"]
        for c in COLS[5:-1]:
            L.append(f"| {c} | {esc(r[c])} |")
        L.append("")
    return "\n".join(L) + "\n"


def check(repo: Path = REPO, staged: bool = False, write: bool = False) -> list[str]:
    src = Source(repo, staged)
    err: list[str] = []
    raw = {}
    for name in ("hypotheses", "families"):
        txt = src.read(f"{SUB}/registry/{name}.yaml")
        try:
            raw[name] = yaml.safe_load(txt) if txt is not None else None
        except yaml.YAMLError as e:
            return [f"S0 {name}.yaml does not parse: {e}"]
        if raw[name] is None:
            return [f"S0 {name}.yaml missing"]
    schema = yaml.safe_load(src.read(f"{SUB}/registry/schema.json") or "{}")
    for e in sorted(Draft202012Validator(schema).iter_errors(raw), key=lambda e: list(e.absolute_path)):
        err.append(f"S0 {'/'.join(map(str, e.absolute_path))}: {e.message[:160]}")
    qs = [q for q in (raw["hypotheses"] or {}).get("questions", []) if isinstance(q, dict)]
    fams = (raw["families"] or {}).get("families", {}) or {}
    calendar, snaps = macro_series(src)
    seen_q, seen_h = set(), set()
    for q in qs:
        i = q.get("id", "?")
        if i in seen_q or str(q.get("direction")) != str(i)[1:2]:
            err.append(f"R6 {i}: duplicate id or direction does not match the id")
        seen_q.add(i)
        hs = [h for h in (q.get("hypotheses") or []) if isinstance(h, dict)]
        members = q.get("members") or {}
        val = q.get("validation") or {}
        prim, supp = str(val.get("primary", "")), str(val.get("supporting", ""))
        infl = q.get("influenced_by") or []
        st = q.get("status")
        if q.get("family") not in fams:
            err.append(f"R2 {i}: family {q.get('family')} not in families.yaml")
        # R6 status consistency
        hst = {h.get("status") for h in hs}
        want = "descriptive" if not hs else ("confirmatory" if "confirmatory" in hst else "exploratory")
        if st != want:
            err.append(f"R6 {i}: question status {st} but hypotheses imply {want}")
        if (not hs) != ("estimand" in q):
            err.append(f"R6 {i}: descriptive questions need an estimand and no hypotheses (and vice versa)")
        if "estimand" in q:
            e = q["estimand"] or {}
            if e.get("purge_months") != e.get("label_horizon_months"):
                err.append(f"R5 {i}: estimand purge != label horizon")
        # R17 tracks vs availability
        for k, m in members.items():
            if not isinstance(m, dict):
                continue
            s, t = str(m.get("series")), m.get("track")
            ok = {"vintage": src.exists(f"data/release_calendar/vintages/{s}.csv.gz") or bool(m.get("pending_gap")),
                  "market": s in MARKET and s not in calendar and s not in snaps,
                  "snapshot_forward": s in snaps,
                  "revised": s in calendar or s in snaps,
                  "label": s == "NBER", "derived": s == "DERIVED", "fleet": s == "FLEET"}.get(t, False)
            if not ok:
                err.append(f"R17 {i}: member {k} series {s} cannot be on track '{t}'")
        if "V-D" in tokens(prim):
            err.append(f"R8 {i}: V-D used as primary validation")
        if q.get("use_case") == "U4" and hs and "LORO" not in prim + " " + supp:
            err.append(f"R10 {i}: U4 question without a LORO evaluation")
        if q.get("use_case") == "U3" and "V-B" in tokens(prim) | tokens(supp):
            err.append(f"R13 {i}: U3 question uses V-B (pre-1999 sector indices are price-only)")
        sahm_vals, has_050 = [], False
        for h in hs:
            hid = h.get("hid", "?")
            if not str(hid).startswith(f"{i}.H") or hid in seen_h:
                err.append(f"R6 {hid}: id must be '{i}.Hn' and unique")
            seen_h.add(hid)
            if h.get("family") not in fams:
                err.append(f"R2 {hid}: family {h.get('family')} not in families.yaml")
            for mk in h.get("members") or []:
                if mk not in members:
                    err.append(f"R6 {hid}: member '{mk}' not defined in the question")
            ep = h.get("endpoint") or {}
            prm = ep.get("params") or {}
            need = prm.get(HORIZON_PARAM.get(ep.get("type"), ""), None)
            if isinstance(need, int) and isinstance(prm.get("model_label_horizon_months"), int):
                need = max(need, prm["model_label_horizon_months"])  # a fitted model's own label also needs purging
            if need is None or h.get("label_horizon_months") != need or h.get("purge_months") != need:
                err.append(f"R5 {hid}: purge {h.get('purge_months')} / horizon {h.get('label_horizon_months')} must "
                           f"equal the endpoint's label definition ({HORIZON_PARAM.get(ep.get('type'))} = {need})")
            if i in STATE_IDS and (ep.get("type") != "interaction" or (h.get("min_events") or 0) < 5):
                err.append(f"R11 {hid}: state-dependence hypotheses need an interaction endpoint and min_events >= 5")
            for p in h.get("parameters") or []:
                if isinstance(p, dict) and p.get("name") == "sahm_threshold_pp":
                    sahm_vals.append((hid, h.get("status"), p.get("value")))
                    if isinstance(p.get("value"), (int, float)) and float(p["value"]) == 0.5:
                        has_050 = True
            c = (ep.get("params") or {}).get("comparator_sahm_threshold_pp")
            if isinstance(c, (int, float)) and float(c) == 0.5:
                has_050 = True
            if h.get("status") == "confirmatory":
                bad_p = [p.get("name") for p in h.get("parameters") or []
                         if not isinstance(p, dict) or p.get("source_type") not in ("citation", "natural")]
                bad_t = [mk for mk in h.get("members") or []
                         if isinstance(members.get(mk), dict) and members[mk].get("track") not in CONF_TRACKS]
                prov = (q.get("provenance") or {}).get("label")
                vt = tokens(prim)
                if (bad_p or bad_t or q.get("uses_fleet_winners") or infl != ["none"]
                        or not vt or not vt <= {"V-C", "V-S"} or str(q.get("null_design", "")).startswith("none")
                        or prov != "discovery-informed prospective confirmation"):
                    err.append(f"R7 {hid}: confirmatory requirements violated (non-cited parameters {bad_p}, "
                               f"tracks {bad_t}, validation {sorted(vt)}, provenance '{prov}')")
                if set(infl) - {"none"}:
                    err.append(f"R9 {hid}: influenced question cannot hold a confirmatory hypothesis")
        for hid, hst_, v in sahm_vals:
            if not isinstance(v, (int, float)):
                err.append(f"R12 {hid}: sahm_threshold_pp must be a number")
            elif hst_ == "confirmatory" and float(v) != 0.5:
                err.append(f"R12 {hid}: confirmatory Sahm threshold must be exactly 0.50 (got {v})")
        if sahm_vals and not has_050:
            err.append(f"R12 {i}: a Sahm variant without the standard 0.50 pp rule in the question")
    ranks = sorted(q.get("rank") for q in qs if isinstance(q.get("rank"), int))
    if ranks != list(range(1, 11)):
        err.append(f"R14 ranks must be exactly 1..10, got {ranks}")
    for k, f in fams.items():
        if not isinstance(f, dict):
            continue
        hs = [h for q in qs for h in (q.get("hypotheses") or []) if isinstance(h, dict) and h.get("family") == k]
        nc = sum(h.get("status") == "confirmatory" for h in hs)
        if len(hs) != f.get("n_total") or nc != f.get("n_confirmatory"):
            err.append(f"R15 {k}: hypotheses {len(hs)}/{nc} vs families.yaml {f.get('n_total')}/{f.get('n_confirmatory')}")
        for kind, n in (("correction_confirmatory", nc), ("correction_exploratory", len(hs) - nc)):
            m = (f.get(kind) or {}).get("method")
            if n > 0 and m in (None, "", "none"):
                err.append(f"R15 {k}: {kind} must name a method (family has {n} such hypotheses)")
    bank = src.read(f"{SUB}/QUESTION_BANK.md") or ""
    for q in qs:
        if not re.search(rf"^#+ {re.escape(str(q.get('id')))}\b", bank, re.M):
            err.append(f"R16 {q.get('id')}: no heading in QUESTION_BANK.md")
    if any(e.startswith("S0") for e in err):
        return err  # do not render tables from an invalid ledger
    rs = rows(qs)
    want = {f"{SUB}/COMPLIANCE.md": render_md(rs, fams), f"{SUB}/registry/compliance.csv": render_csv(rs)}
    for rel, txt in want.items():
        if write:
            (repo / rel).write_text(txt)
        elif src.read(rel) != txt:
            err.append(f"R16 {rel} is stale: run with --write")
    return err


def main() -> int:
    err = check(REPO, staged="--staged" in sys.argv, write="--write" in sys.argv)
    if err:
        print("GATE-COMBO-REGISTRY FAIL")
        print("\n".join(f"  {e}" for e in err))
        return 1
    print("GATE-COMBO-REGISTRY PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
