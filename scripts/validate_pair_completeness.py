#!/usr/bin/env python3
"""GATE-DPS1 — Pair Completeness Validator.

Validates that a pair meets every mandatory requirement in
docs/dashboard-page-standard.md before the page is rendered.

Usage:
    python scripts/validate_pair_completeness.py --pair hy_ig_spy
    python scripts/validate_pair_completeness.py --all
    python scripts/validate_pair_completeness.py --pair hy_ig_spy --json

Exit codes:
    0  All checks passed
    1  One or more FAIL checks
    2  Invocation error

Intended users:
    Ace  — run before META-SRV handoff; must show clean PASS
    Quincy — run as part of GATE-31 independent QA verification
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo root — script lives at scripts/, repo root is one level up
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[1]
_RESULTS_DIR = _REPO_ROOT / "results"
_CHARTS_DIR = _REPO_ROOT / "output" / "charts"
_PAIR_CONFIGS_DIR = _REPO_ROOT / "app" / "pair_configs"
_GLOSSARY_PATH = _REPO_ROOT / "docs" / "portal_glossary.json"

# ---------------------------------------------------------------------------
# DPS-EP1 — canonical crisis-episode slugs (mandatory for every pair)
# ---------------------------------------------------------------------------
MANDATORY_EPISODE_SLUGS = ["dotcom", "gfc", "covid", "inflation_2022"]

# ---------------------------------------------------------------------------
# Mandatory chart artifacts (relative to output/charts/{pair_id}/plotly/)
# ---------------------------------------------------------------------------
MANDATORY_CHARTS = [
    "hero",
    "regime_stats",
    "equity_curves",
    "drawdown",
    "walk_forward",
    "tournament_scatter",
    "subperiod_sharpe",
    "rolling_correlation",
    "structural_break",
    # Crisis-episode zooms checked separately via MANDATORY_EPISODE_SLUGS
]

# ---------------------------------------------------------------------------
# Mandatory result artifacts (relative to results/{pair_id}/)
# ---------------------------------------------------------------------------
MANDATORY_RESULT_ARTIFACTS = [
    "interpretation_metadata.json",
    "winner_summary.json",
    "evidence_status.json",
    "signal_scope.json",
    "winner_trade_log.csv",
    "winner_trades_broker_style.csv",
]

# Glob-pattern artifacts (need at least one match)
MANDATORY_RESULT_GLOBS = [
    ("tournament_results_*.csv", "tournament_results"),
    ("stationarity_tests_*.csv", "stationarity_tests"),
    ("signals_*.parquet", "signals"),
]

# ---------------------------------------------------------------------------
# Mandatory story config attributes
# ---------------------------------------------------------------------------
MANDATORY_STORY_ATTRS = [
    "PAGE_TITLE",
    "PLAIN_ENGLISH",
    "ONE_SENTENCE_THESIS",
    "KPI_CAPTION",
    "HERO_CHART_NAME",
    "REGIME_CHART_NAME",
    "NARRATIVE_SECTION_1",
    "NARRATIVE_SECTION_2",
    "HISTORY_ZOOM_EPISODES",
]

# ---------------------------------------------------------------------------
# Mandatory strategy config attributes
# ---------------------------------------------------------------------------
MANDATORY_STRATEGY_ATTRS = [
    "PAGE_TITLE",
    "PLAIN_ENGLISH",
    "HOW_SIGNAL_IS_GENERATED_MD",
    "MANUAL_USE_MD",
    "CAVEATS_MD",
    "TRADE_LOG_EXAMPLE_MD",
]

# ---------------------------------------------------------------------------
# Mandatory evidence method block fields (RES-EP1)
# ---------------------------------------------------------------------------
MANDATORY_METHOD_BLOCK_FIELDS = [
    "method_name",
    "method_theory",
    "question",
    "how_to_read",
    "observation",
    "interpretation",
    "key_message",
]

# Minimum method block counts (DPS standard)
MIN_LEVEL1_BLOCKS = 3
MIN_LEVEL2_BLOCKS = 2

# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------
@dataclass
class CheckResult:
    name: str
    status: str        # "PASS" | "FAIL" | "WARN"
    message: str
    path: str = ""     # file path relevant to this check, if any


@dataclass
class PageReport:
    page: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def failed(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == "FAIL"]

    @property
    def warned(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == "WARN"]


@dataclass
class PairReport:
    pair_id: str
    pages: list[PageReport] = field(default_factory=list)

    @property
    def all_checks(self) -> list[CheckResult]:
        return [c for p in self.pages for c in p.checks]

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.all_checks if c.status == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for c in self.all_checks if c.status == "WARN")

    @property
    def passed(self) -> bool:
        return self.fail_count == 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _check(name: str, condition: bool, fail_msg: str, pass_msg: str = "",
           path: str = "", warn: bool = False) -> CheckResult:
    if condition:
        return CheckResult(name, "PASS", pass_msg or name, path)
    status = "WARN" if warn else "FAIL"
    return CheckResult(name, status, fail_msg, path)


def _glob_exists(pair_id: str, pattern: str) -> Path | None:
    matches = sorted((_RESULTS_DIR / pair_id).glob(pattern))
    return matches[-1] if matches else None


def _load_config_module(pair_id: str) -> tuple[Any | None, str | None]:
    """Load pair config module. Returns (module, error_message)."""
    config_path = _PAIR_CONFIGS_DIR / f"{pair_id}_config.py"
    if not config_path.exists():
        return None, f"Config module not found: app/pair_configs/{pair_id}_config.py"
    # Pair configs import from components/ — ensure app/ is on sys.path
    app_dir = str(_REPO_ROOT / "app")
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    spec = importlib.util.spec_from_file_location(f"{pair_id}_config", config_path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        return None, f"Config module failed to import: {exc}"
    return mod, None


def _load_json(path: Path) -> tuple[dict | None, str | None]:
    if not path.exists():
        return None, f"File not found: {path.relative_to(_REPO_ROOT)}"
    try:
        with open(path) as f:
            return json.load(f), None
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in {path.relative_to(_REPO_ROOT)}: {exc}"


def _load_glossary_terms() -> set[str]:
    data, err = _load_json(_GLOSSARY_PATH)
    if err or not data:
        return set()
    return set(data.get("terms", {}).keys())


# ---------------------------------------------------------------------------
# Check groups
# ---------------------------------------------------------------------------
_EXAM_RUN_STATUSES = {"passed_final_exam", "failed_final_exam"}
_EXAM_NOT_RUN_STATUSES = {"found_in_search", "needs_final_exam"}


def _check_prerequisites(pair_id: str) -> PageReport:
    """DPS-PRE1 — Final exam must have been run. Blocks production if not."""
    report = PageReport("Prerequisites — Final Exam (DPS-PRE1)")
    es_path = _RESULTS_DIR / pair_id / "evidence_status.json"

    if not es_path.exists():
        report.checks.append(CheckResult(
            "evidence_status.json exists",
            "FAIL",
            f"MISSING evidence_status.json — pair cannot be registered for production (DPS-PRE1)",
            path=f"results/{pair_id}/evidence_status.json",
        ))
        return report

    es_data, es_err = _load_json(es_path)
    if es_err:
        report.checks.append(CheckResult(
            "evidence_status.json — valid JSON", "FAIL", es_err,
            path=str(es_path.relative_to(_REPO_ROOT)),
        ))
        return report

    for field_name in ("pair_id", "schema_version", "status", "updated_at"):
        report.checks.append(_check(
            f"evidence_status.json — field '{field_name}'",
            bool(es_data.get(field_name)),
            f"evidence_status.json missing required field: '{field_name}'",
            path=str(es_path.relative_to(_REPO_ROOT)),
        ))

    status = es_data.get("status", "")

    # Hard gate: exam must have been run
    exam_run = status in _EXAM_RUN_STATUSES
    report.checks.append(_check(
        "Final exam has been run",
        exam_run,
        f"Final exam NOT run — status is '{status}'. "
        f"Pair is blocked from production until the final exam is executed (DPS-PRE1). "
        f"Acceptable statuses: {sorted(_EXAM_RUN_STATUSES)}",
        pass_msg=f"Final exam run — status: '{status}'",
        path=str(es_path.relative_to(_REPO_ROOT)),
    ))

    # Informational: pass vs fail outcome (WARN only — outcome is user's judgment)
    if status == "failed_final_exam":
        # Must have failure_reasons
        reasons = es_data.get("failure_reasons", [])
        report.checks.append(_check(
            "failed_final_exam — failure_reasons present",
            bool(reasons),
            "failure_reasons array is missing or empty — required for failed_final_exam (schema v1.2.0)",
            path=str(es_path.relative_to(_REPO_ROOT)),
        ))
        report.checks.append(CheckResult(
            "Final exam outcome",
            "WARN",
            f"Exam FAILED — {len(reasons)} failure reason(s) documented. "
            f"Pair is production-eligible but MUST display disclosure banner (DPS-PRE1).",
            path=str(es_path.relative_to(_REPO_ROOT)),
        ))
    elif status == "passed_final_exam":
        report.checks.append(CheckResult(
            "Final exam outcome", "PASS", "Exam passed.", "",
        ))

    return report


def _check_result_artifacts(pair_id: str) -> PageReport:
    report = PageReport("Artifacts — Results")
    rdir = _RESULTS_DIR / pair_id

    for filename in MANDATORY_RESULT_ARTIFACTS:
        fpath = rdir / filename
        report.checks.append(_check(
            f"results/{pair_id}/{filename}",
            fpath.exists(),
            f"MISSING mandatory artifact: results/{pair_id}/{filename}",
            path=str(fpath.relative_to(_REPO_ROOT)),
        ))

    for pattern, label in MANDATORY_RESULT_GLOBS:
        match = _glob_exists(pair_id, pattern)
        report.checks.append(_check(
            f"results/{pair_id}/{label} (glob: {pattern})",
            match is not None,
            f"MISSING mandatory artifact matching: results/{pair_id}/{pattern}",
            path=str(match.relative_to(_REPO_ROOT)) if match else "",
        ))

    return report


def _check_chart_artifacts(pair_id: str) -> PageReport:
    report = PageReport("Artifacts — Charts")
    cdir = _CHARTS_DIR / pair_id / "plotly"

    for chart_name in MANDATORY_CHARTS:
        json_path = cdir / f"{chart_name}.json"
        png_path = cdir / f"_perceptual_check_{chart_name}.png"

        report.checks.append(_check(
            f"chart: {chart_name}.json",
            json_path.exists(),
            f"MISSING mandatory chart: output/charts/{pair_id}/plotly/{chart_name}.json",
            path=str(json_path.relative_to(_REPO_ROOT)) if json_path.exists() else "",
        ))
        report.checks.append(_check(
            f"perceptual PNG: _perceptual_check_{chart_name}.png",
            png_path.exists(),
            f"MISSING perceptual PNG (VIZ-CV1): output/charts/{pair_id}/plotly/_perceptual_check_{chart_name}.png",
            path=str(png_path.relative_to(_REPO_ROOT)) if png_path.exists() else "",
        ))

    return report


def _check_episode_zooms(pair_id: str, config_mod: Any | None) -> PageReport:
    report = PageReport("Story — Crisis Episode Zooms (DPS-EP1)")
    cdir = _CHARTS_DIR / pair_id / "plotly"

    # Check chart artifacts for all 4 mandatory slugs
    for slug in MANDATORY_EPISODE_SLUGS:
        json_path = cdir / f"history_zoom_{slug}.json"
        png_path = cdir / f"_perceptual_check_history_zoom_{slug}.png"
        report.checks.append(_check(
            f"history_zoom_{slug}.json",
            json_path.exists(),
            f"MISSING mandatory crisis-episode chart (DPS-EP1): output/charts/{pair_id}/plotly/history_zoom_{slug}.json",
        ))
        report.checks.append(_check(
            f"_perceptual_check_history_zoom_{slug}.png",
            png_path.exists(),
            f"MISSING perceptual PNG (VIZ-CV1): output/charts/{pair_id}/plotly/_perceptual_check_history_zoom_{slug}.png",
        ))

    if config_mod is None:
        return report

    # Check config declares all 4 mandatory slugs
    story_cfg = getattr(config_mod, "STORY_CONFIG", None) or config_mod
    episodes = getattr(story_cfg, "HISTORY_ZOOM_EPISODES", None)
    if not episodes:
        report.checks.append(CheckResult(
            "HISTORY_ZOOM_EPISODES in config",
            "FAIL",
            "HISTORY_ZOOM_EPISODES is missing or empty in StoryConfig",
        ))
        return report

    declared_slugs = {ep.get("slug") for ep in episodes}
    for slug in MANDATORY_EPISODE_SLUGS:
        report.checks.append(_check(
            f"HISTORY_ZOOM_EPISODES — slug '{slug}' declared",
            slug in declared_slugs,
            f"Mandatory episode slug '{slug}' not declared in HISTORY_ZOOM_EPISODES (DPS-EP1)",
        ))

    # Each declared episode must have title, narrative, caption
    for ep in episodes:
        slug = ep.get("slug", "<unnamed>")
        for attr in ("title", "narrative", "caption"):
            report.checks.append(_check(
                f"episode '{slug}' — field '{attr}'",
                bool(ep.get(attr, "").strip()),
                f"Episode '{slug}' missing required field '{attr}' in HISTORY_ZOOM_EPISODES",
            ))

    return report


def _check_story_config(pair_id: str, config_mod: Any | None) -> PageReport:
    report = PageReport("Story — Config")
    if config_mod is None:
        report.checks.append(CheckResult(
            "story config available", "FAIL",
            "Cannot check story config — config module failed to load",
        ))
        return report

    story_cfg = getattr(config_mod, "STORY_CONFIG", None) or config_mod

    for attr in MANDATORY_STORY_ATTRS:
        val = getattr(story_cfg, attr, None)
        present = bool(val)
        if present and isinstance(val, str):
            present = bool(val.strip())
        report.checks.append(_check(
            f"StoryConfig.{attr}",
            present,
            f"MISSING or empty mandatory StoryConfig attribute: {attr}",
        ))

    return report


def _check_strategy_config(pair_id: str, config_mod: Any | None) -> PageReport:
    report = PageReport("Strategy — Config")
    if config_mod is None:
        report.checks.append(CheckResult(
            "strategy config available", "FAIL",
            "Cannot check strategy config — config module failed to load",
        ))
        return report

    strat_cfg = getattr(config_mod, "STRATEGY_CONFIG", None) or config_mod

    for attr in MANDATORY_STRATEGY_ATTRS:
        val = getattr(strat_cfg, attr, None)
        present = bool(val)
        if present and isinstance(val, str):
            present = bool(val.strip())
        report.checks.append(_check(
            f"StrategyConfig.{attr}",
            present,
            f"MISSING or empty mandatory StrategyConfig attribute: {attr}",
        ))

    return report


def _check_evidence_blocks(pair_id: str, config_mod: Any | None) -> PageReport:
    report = PageReport("Evidence — Method Blocks")
    if config_mod is None:
        report.checks.append(CheckResult(
            "evidence config available", "FAIL",
            "Cannot check evidence blocks — config module failed to load",
        ))
        return report

    blocks_dict = getattr(config_mod, "EVIDENCE_METHOD_BLOCKS", None)
    if not blocks_dict:
        report.checks.append(CheckResult(
            "EVIDENCE_METHOD_BLOCKS", "FAIL",
            "EVIDENCE_METHOD_BLOCKS is missing or empty in config module",
        ))
        return report

    level1 = blocks_dict.get("level1", [])
    level2 = blocks_dict.get("level2", [])

    report.checks.append(_check(
        f"Level 1 block count ≥ {MIN_LEVEL1_BLOCKS}",
        len(level1) >= MIN_LEVEL1_BLOCKS,
        f"Level 1 has {len(level1)} method block(s) — minimum is {MIN_LEVEL1_BLOCKS} (DPS standard)",
    ))
    report.checks.append(_check(
        f"Level 2 block count ≥ {MIN_LEVEL2_BLOCKS}",
        len(level2) >= MIN_LEVEL2_BLOCKS,
        f"Level 2 has {len(level2)} method block(s) — minimum is {MIN_LEVEL2_BLOCKS} (DPS standard)",
    ))

    # Check each block for mandatory fields
    for level_name, blocks in [("Level 1", level1), ("Level 2", level2)]:
        for i, block in enumerate(blocks):
            block_name = block.get("method_name", f"block[{i}]")
            for field_name in MANDATORY_METHOD_BLOCK_FIELDS:
                val = block.get(field_name, "")
                report.checks.append(_check(
                    f"{level_name} '{block_name}' — field '{field_name}'",
                    bool(str(val).strip()),
                    f"{level_name} method block '{block_name}' missing required field '{field_name}' (RES-EP1)",
                ))

            # Chart artifact check when chart_status == "ready"
            if block.get("chart_status", "ready") == "ready" and block.get("chart_name"):
                chart_path = _CHARTS_DIR / pair_id / "plotly" / f"{block['chart_name']}.json"
                report.checks.append(_check(
                    f"{level_name} '{block_name}' — chart artifact",
                    chart_path.exists(),
                    f"Chart artifact missing for method '{block_name}': output/charts/{pair_id}/plotly/{block['chart_name']}.json",
                    path=str(chart_path.relative_to(_REPO_ROOT)) if chart_path.exists() else "",
                ))

    # plain_english and overview in blocks_dict
    for key in ("plain_english", "overview", "title"):
        report.checks.append(_check(
            f"EVIDENCE_METHOD_BLOCKS['{key}']",
            bool(str(blocks_dict.get(key, "")).strip()),
            f"EVIDENCE_METHOD_BLOCKS missing required key '{key}'",
        ))

    return report


def _check_methodology_config(pair_id: str, config_mod: Any | None) -> PageReport:
    report = PageReport("Methodology — Config")
    if config_mod is None:
        report.checks.append(CheckResult(
            "methodology config available", "FAIL",
            "Cannot check methodology config — config module failed to load",
        ))
        return report

    # Methodology uses MethodologyConfig dataclass passed directly
    meth_cfg = getattr(config_mod, "METHODOLOGY_CONFIG", None)
    if meth_cfg is None:
        report.checks.append(CheckResult(
            "METHODOLOGY_CONFIG", "FAIL",
            "METHODOLOGY_CONFIG is missing from config module",
        ))
        return report

    for attr in ("data_sources_table_md", "indicator_construction_md",
                 "methods_table_md", "tournament_design_md", "references_md"):
        val = getattr(meth_cfg, attr, "")
        report.checks.append(_check(
            f"MethodologyConfig.{attr}",
            bool(str(val).strip()),
            f"MISSING or empty mandatory MethodologyConfig attribute: {attr}",
        ))

    return report


def _check_glossary_coverage(pair_id: str, config_mod: Any | None) -> PageReport:
    """Warn (not fail) when method block headings use undefined terms (DPS-II1).

    Matching is substring + case-insensitive: search term 'sharpe' matches
    glossary key 'Sharpe ratio'. A term is covered if ANY glossary key contains
    it as a substring.
    """
    report = PageReport("Glossary Coverage (DPS-II1)")
    glossary_terms = _load_glossary_terms()
    if not glossary_terms:
        report.checks.append(CheckResult(
            "portal_glossary.json readable", "WARN",
            f"Could not load glossary from {_GLOSSARY_PATH.relative_to(_REPO_ROOT)} — skipping coverage check",
        ))
        return report

    # Build a single lowercase string of all glossary keys for substring matching
    glossary_keys_lower = [t.lower() for t in glossary_terms]

    def _covered(term: str) -> bool:
        t = term.lower()
        return any(t in key for key in glossary_keys_lower)

    if config_mod is None:
        return report

    # Well-known technical terms that should be covered by at least one glossary entry
    _TECHNICAL_TERMS = [
        "sharpe", "drawdown", "granger", "hmm", "cointegration",
        "z-score", "quantile", "local projections", "transfer entropy",
        "dsr", "deflated sharpe", "bootstrap", "walk-forward",
    ]
    missing = [t for t in _TECHNICAL_TERMS if not _covered(t)]
    if missing:
        for term in missing:
            report.checks.append(CheckResult(
                f"glossary coverage: '{term}'",
                "WARN",
                f"No glossary entry covering '{term}' — add to portal_glossary.json (DPS-II1)",
            ))
    else:
        report.checks.append(CheckResult(
            "glossary coverage: all standard terms", "PASS",
            f"All {len(_TECHNICAL_TERMS)} standard technical terms covered in portal_glossary.json",
        ))

    return report


# ---------------------------------------------------------------------------
# Per-pair runner
# ---------------------------------------------------------------------------
def validate_pair(pair_id: str) -> PairReport:
    report = PairReport(pair_id)

    # Check pair exists
    pair_dir = _RESULTS_DIR / pair_id
    if not pair_dir.is_dir():
        report.pages.append(PageReport("Setup"))
        report.pages[0].checks.append(CheckResult(
            "pair directory exists", "FAIL",
            f"results/{pair_id}/ does not exist — pair not found",
        ))
        return report

    # Load config module once
    config_mod, config_err = _load_config_module(pair_id)
    if config_err:
        p = PageReport("Config Module")
        p.checks.append(CheckResult("config module loads", "FAIL", config_err))
        report.pages.append(p)
        # Continue with artifact checks even if config fails

    # Run all check groups — prerequisites first
    report.pages.append(_check_prerequisites(pair_id))
    report.pages.append(_check_result_artifacts(pair_id))
    report.pages.append(_check_chart_artifacts(pair_id))
    report.pages.append(_check_episode_zooms(pair_id, config_mod))
    report.pages.append(_check_story_config(pair_id, config_mod))
    report.pages.append(_check_strategy_config(pair_id, config_mod))
    report.pages.append(_check_evidence_blocks(pair_id, config_mod))
    report.pages.append(_check_methodology_config(pair_id, config_mod))
    report.pages.append(_check_glossary_coverage(pair_id, config_mod))

    return report


# ---------------------------------------------------------------------------
# Registered pairs (mirrors pair_registry.py PAGE_ROUTING)
# ---------------------------------------------------------------------------
def _registered_pairs() -> list[str]:
    try:
        sys.path.insert(0, str(_REPO_ROOT / "app"))
        from components.pair_registry import PAGE_ROUTING
        return list(PAGE_ROUTING.keys())
    except Exception:
        # Fallback: scan results/ directory
        return [
            d for d in os.listdir(_RESULTS_DIR)
            if (_RESULTS_DIR / d).is_dir()
            and not d.endswith(("_v1", "_archived"))
            and d not in ("hy_ig_spy_v3_rerun", "hy_ig_spy_v3_retro")
        ]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
PASS_COLOR  = "\033[92m"
FAIL_COLOR  = "\033[91m"
WARN_COLOR  = "\033[93m"
RESET_COLOR = "\033[0m"
BOLD        = "\033[1m"


def _status_str(status: str, use_color: bool) -> str:
    if not use_color:
        return f"[{status}]"
    color = {"PASS": PASS_COLOR, "FAIL": FAIL_COLOR, "WARN": WARN_COLOR}.get(status, "")
    return f"{color}[{status}]{RESET_COLOR}"


def render_text(report: PairReport, use_color: bool = True) -> str:
    lines = []
    bold = BOLD if use_color else ""
    reset = RESET_COLOR if use_color else ""

    lines.append(f"\n{bold}{'='*60}{reset}")
    lines.append(f"{bold}GATE-DPS1 — Pair Completeness Report: {report.pair_id}{reset}")
    lines.append(f"{'='*60}")

    for page in report.pages:
        fails = page.failed
        warns = page.warned
        page_status = "FAIL" if fails else ("WARN" if warns else "PASS")
        lines.append(f"\n{bold}{page.page}{reset}  {_status_str(page_status, use_color)}")

        for c in page.checks:
            if c.status == "PASS":
                continue  # Only show non-passing in detail
            indent = "  "
            lines.append(f"{indent}{_status_str(c.status, use_color)}  {c.name}")
            lines.append(f"{indent}       {c.message}")
            if c.path:
                lines.append(f"{indent}       Path: {c.path}")

        if not fails and not warns:
            lines.append(f"  All {len(page.checks)} checks passed.")

    lines.append(f"\n{'='*60}")
    overall = "PASS" if report.passed else "FAIL"
    lines.append(
        f"{bold}Overall: {_status_str(overall, use_color)}  "
        f"{report.fail_count} FAIL  {report.warn_count} WARN  "
        f"{len(report.all_checks) - report.fail_count - report.warn_count} PASS{reset}"
    )
    lines.append(f"{'='*60}\n")
    return "\n".join(lines)


def render_json(reports: list[PairReport]) -> str:
    out = []
    for r in reports:
        out.append({
            "pair_id": r.pair_id,
            "passed": r.passed,
            "fail_count": r.fail_count,
            "warn_count": r.warn_count,
            "pages": [
                {
                    "page": p.page,
                    "checks": [
                        {"name": c.name, "status": c.status,
                         "message": c.message, "path": c.path}
                        for c in p.checks
                    ],
                }
                for p in r.pages
            ],
        })
    return json.dumps(out, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="GATE-DPS1 — Pair completeness validator (docs/dashboard-page-standard.md)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pair", metavar="PAIR_ID", help="Validate a single pair")
    group.add_argument("--all", action="store_true", help="Validate all registered pairs")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    args = parser.parse_args()

    use_color = not args.no_color and sys.stdout.isatty()

    if args.pair:
        pair_ids = [args.pair]
    else:
        pair_ids = sorted(_registered_pairs())
        if not pair_ids:
            print("No registered pairs found.", file=sys.stderr)
            return 2

    reports = [validate_pair(pid) for pid in pair_ids]

    if args.json:
        print(render_json(reports))
    else:
        for r in reports:
            print(render_text(r, use_color=use_color))

    any_failed = any(not r.passed for r in reports)
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
