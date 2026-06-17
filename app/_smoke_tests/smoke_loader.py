"""Ace Defense-2 loader end-to-end smoke test (APP-ST1).

Parses each HY-IG v2 page's source via AST, extracts every
``load_plotly_chart(name, pair_id=...)`` call site, and executes the loader in
a Streamlit-mock context to verify:

    1. The loader returns a non-None plotly.graph_objs.Figure
    2. ``len(fig.data) > 0`` (at least one trace)
    3. The figure is self-titled (APP-ST1 criterion #3, amended 2026-06-11,
       fix260611_meta_cmp / commit 1b14ccc): ``fig.layout.title.text`` is a
       non-empty string, OR — multi-panel case — at least one non-empty
       subplot-title annotation is present
       (``make_subplots(subplot_titles=...)`` emits these as
       ``layout.annotations``). Intent: "no anonymous charts", not
       "exactly one title field".

For call sites where ``chart_name`` is a variable (not a literal), we
supplement the static AST list with an explicit mapping of the dynamic
chart_names used by the Evidence page's ``render_method_block`` helper.

Run from repo root::

    python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy
    python3 app/_smoke_tests/smoke_loader.py --all

Exits 0 when all call sites pass; exits 1 on any failure. Writes a per-run
log at ``app/_smoke_tests/loader_{pair_id}_{yyyymmdd}.log``.

``--all`` (META-CMP T1.2, GH #7) runs the same per-pair smoke over every
REGISTERED pair (discovered via ``components.pair_registry``, the portal's
own discovery) and exits non-zero if ANY pair reports failures > 0. The
per-pair log-file convention is unchanged — one log per pair per run.

Defense-2 extension rule: APP-ST1 (Loader End-to-End Smoke Test).
"""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import glob
import os
import sys
import traceback
from types import SimpleNamespace


# ---------------------------------------------------------------------------
# Streamlit mock — the loader calls st.plotly_chart / st.info / st.warning /
# st.markdown. We don't want a real Streamlit runtime for a smoke test, so we
# replace the ``st`` attribute on the charts module before invoking the
# loader. This preserves the cache_resource decorator (already bound at import
# time) but stubs out all rendering side-effects.
# ---------------------------------------------------------------------------


class _MockSt:
    def __init__(self):
        self.plotly_calls = 0
        self.info_calls = 0
        self.warning_calls = 0

    def plotly_chart(self, *args, **kwargs):
        self.plotly_calls += 1

    def info(self, *args, **kwargs):
        self.info_calls += 1

    def warning(self, *args, **kwargs):
        self.warning_calls += 1

    def markdown(self, *args, **kwargs):
        pass


# Per-pair dynamic chart lists for render_method_block helpers.
# Only needed when chart names aren't literal strings in the page source
# (AST can't see them). Add a new entry when a pair uses non-literal chart names.
# Pairs whose block dicts use literal strings are already covered by AST — leave
# them out of this dict (or map to an empty list).
EVIDENCE_DYNAMIC_CHARTS: dict[str, list[str]] = {
    "hy_ig_v2_spy": [
        "correlation_heatmap",
        "granger_f_by_lag",
        "local_projections",
        "hmm_regime_probs",
        "quantile_regression",
        "ccf_prewhitened",
        "transfer_entropy",
        "regime_quartile_returns",
    ],
    # umcsent_xlv block dict uses literal chart names in the page file →
    # fully covered by AST parsing.
    # indpro_xlp uses APP-PT1 page templates — charts live in
    # `app/components/page_templates.py` and `app/pair_configs/indpro_xlp_config.py`
    # which the loader now also scans. No dynamic supplement needed.
}


# APP-PT1 (2026-04-20): pair pages that are thin wrappers around
# `components.page_templates` delegate chart calls to the template module
# and the pair config module. The AST scanner now also inspects those files
# so the smoke test covers every load_plotly_chart call site for the pair.
#
# Key insight: the template has generic calls like
# ``load_plotly_chart(hero_chart, pair_id=pair_id)`` where ``hero_chart``
# is a variable — AST cannot resolve these. For those, we look up the
# literal chart names assigned in the pair config class attributes.
PAIR_TEMPLATE_CHARTS: dict[str, list[str]] = {
    "busloans_spy": [
        # Charts the template loads via variables/f-strings that AST cannot
        # resolve from the config: history zooms (f-string slug) and the
        # Cross-Period Consistency set (_cp_always tuples). Config
        # *_CHART_NAME constants cover the rest via the AST scan.
        "history_zoom_dotcom",
        "history_zoom_gfc",
        "history_zoom_covid",
        "history_zoom_inflation_2022",
        "subperiod_sharpe",
        "rolling_correlation",
        "structural_break",
        # Confidence-tab scatter sibling (config routes the slot to
        # tournament_sharpe_dist; the scatter also ships and is referenced
        # by the registry).
        "tournament_scatter",
    ],
    "petrol_inv_spy": [
        "history_zoom_dotcom",
        "history_zoom_gfc",
        "history_zoom_covid",
        "history_zoom_inflation_2022",
        "subperiod_sharpe",
        "rolling_correlation",
        "structural_break",
        "tournament_scatter",
    ],
    "indpro_xlp": [
        # Story
        "hero",
        "regime_stats",
        # Strategy — Performance tab
        "equity_curves",
        "drawdown",
        # Strategy — Confidence tab
        "walk_forward",
        "tournament_scatter",
        # Evidence method blocks
        "correlations",
        "ccf",
    ],
    "umcsent_xlv": [
        # Story
        "hero",
        "regime_stats",
        "history_zoom_dot_com",
        "history_zoom_gfc",
        "history_zoom_covid",
        "history_zoom_rates_2022",
        # Evidence method blocks
        "correlation_scatter",
        "ccf",
        "signal_dist",
        # Strategy performance and confidence tabs
        "equity_curves",
        "drawdown",
        "wf_sharpe",
        "subperiod_sharpe",
        "rolling_correlation",
        "structural_break",
        "rolling_sharpe_cp",
        "rolling_granger",
        "tournament_scatter",
    ],
}


def extract_static_calls(page_path: str) -> list[tuple[int, str | None]]:
    """AST-parse a page and return (lineno, literal_chart_name_or_None) tuples
    for every ``load_plotly_chart(...)`` invocation.

    Literal chart_name is None when the first positional arg is not a
    ``str`` constant (e.g., inside a helper function that receives
    ``chart_name`` as a parameter).
    """
    with open(page_path) as f:
        tree = ast.parse(f.read())
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
        if name != "load_plotly_chart":
            continue
        chart_name: str | None = None
        if node.args:
            a0 = node.args[0]
            if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                chart_name = a0.value
        else:
            for kw in node.keywords:
                if kw.arg == "chart_name" and isinstance(kw.value, ast.Constant):
                    chart_name = kw.value.value
                    break
        out.append((node.lineno, chart_name))
    return out


def run_smoke_test(pair_id: str) -> tuple[int, int, list[str]]:
    """Return (passes, failures, log_lines)."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(repo_root, "app"))

    # Import the module under test and install the mock st
    import components.charts as charts_mod

    mock_st = _MockSt()
    charts_mod.st = mock_st

    # Dynamically discover page prefix — pages follow N_{pair_id}_*.py naming
    # where N varies per pair (e.g. 9 for hy_ig_v2_spy, 10 for umcsent_xlv).
    page_glob = os.path.join(
        repo_root, "app", "pages", f"*_{pair_id}_*.py"
    )
    pages = sorted(glob.glob(page_glob))

    log: list[str] = []
    passes = 0
    failures = 0

    def _check(chart_name: str, source_ref: str) -> None:
        nonlocal passes, failures
        try:
            fig = charts_mod.load_plotly_chart(chart_name, pair_id=pair_id)
        except Exception as exc:
            failures += 1
            log.append(
                f"FAIL  {source_ref}  chart={chart_name}  exception={exc!r}"
            )
            log.append(traceback.format_exc())
            return
        if fig is None:
            failures += 1
            log.append(f"FAIL  {source_ref}  chart={chart_name}  loader returned None")
            return
        if len(fig.data) == 0:
            failures += 1
            log.append(
                f"FAIL  {source_ref}  chart={chart_name}  fig.data empty (0 traces)"
            )
            return
        # Criterion #3 — self-titled (APP-ST1, amended 2026-06-11 / 1b14ccc):
        # overall layout.title.text non-empty, OR at least one non-empty
        # subplot-title annotation (multi-panel figures built via
        # make_subplots(subplot_titles=...) carry titles as annotations).
        title = getattr(getattr(fig.layout, "title", None), "text", None)
        has_title = bool(title and str(title).strip())
        subplot_titles = []
        if not has_title:
            subplot_titles = [
                str(a.text).strip()
                for a in (fig.layout.annotations or ())
                if getattr(a, "text", None) and str(a.text).strip()
            ]
        if not has_title and not subplot_titles:
            failures += 1
            log.append(
                f"FAIL  {source_ref}  chart={chart_name}  not self-titled: "
                f"fig.layout.title.text empty AND no non-empty subplot-title "
                f"annotation (APP-ST1 #3, amended 1b14ccc)"
            )
            return
        passes += 1
        title_note = (
            f"title={title!r}" if has_title
            else f"subplot_titles={subplot_titles!r}"
        )
        log.append(
            f"PASS  {source_ref}  chart={chart_name}  traces={len(fig.data)}  "
            f"{title_note}"
        )

    log.append(f"# Loader smoke test  pair_id={pair_id}  "
               f"timestamp={_dt.datetime.now().isoformat(timespec='seconds')}")
    log.append(f"# Pages scanned: {len(pages)}")
    for p in pages:
        log.append(f"#   {os.path.relpath(p, repo_root)}")
    log.append("")

    for page in pages:
        rel = os.path.relpath(page, repo_root)
        calls = extract_static_calls(page)
        for lineno, chart_name in calls:
            if chart_name is None:
                log.append(
                    f"SKIP  {rel}:{lineno}  chart_name is a variable; "
                    "resolved via EVIDENCE_DYNAMIC_CHARTS list"
                )
                continue
            _check(chart_name, f"{rel}:{lineno}")

    # Dynamic-chart set (Evidence render_method_block helper)
    log.append("")
    log.append("# Dynamic charts (Evidence render_method_block helper)")
    for chart_name in EVIDENCE_DYNAMIC_CHARTS.get(pair_id, []):
        _check(chart_name, f"{pair_id}/evidence<render_method_block>")

    # APP-PT1 (2026-04-20): thin-wrapper pair pages delegate to the
    # template module + pair config. Scan those files' source for the
    # same pair's chart calls, so we don't miss them just because they're
    # no longer in a page file.
    template_path = os.path.join(repo_root, "app", "components", "page_templates.py")
    config_path = os.path.join(repo_root, "app", "pair_configs", f"{pair_id}_config.py")
    log.append("")
    log.append("# APP-PT1 template + pair_config chart scans")
    seen_charts = set()
    for aux_path in (template_path, config_path):
        if not os.path.exists(aux_path):
            continue
        rel = os.path.relpath(aux_path, repo_root)
        # Pull literal chart names from load_plotly_chart(...) call sites
        # in the template, plus any *_CHART_NAME class attribute literals
        # in the config (which the template reads via getattr).
        try:
            with open(aux_path) as f:
                aux_tree = ast.parse(f.read())
        except SyntaxError as exc:
            log.append(f"SKIP  {rel}  AST parse failed: {exc}")
            continue
        for node in ast.walk(aux_tree):
            # load_plotly_chart(name=..., ...)
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
                if name == "load_plotly_chart" and node.args:
                    a0 = node.args[0]
                    if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                        if a0.value not in seen_charts:
                            seen_charts.add(a0.value)
                            _check(a0.value, f"{rel}:{node.lineno}")
            # {KEY}_CHART_NAME = "..." assignments in the pair config.
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id.endswith("_CHART_NAME"):
                        v = node.value
                        if isinstance(v, ast.Constant) and isinstance(v.value, str):
                            if v.value not in seen_charts:
                                seen_charts.add(v.value)
                                _check(v.value, f"{rel}:{node.lineno}")

    # Any template/config pair charts the registry knows about but the AST
    # didn't pick up (e.g. via getattr default strings) — belt-and-braces.
    for chart_name in PAIR_TEMPLATE_CHARTS.get(pair_id, []):
        if chart_name in seen_charts:
            continue
        seen_charts.add(chart_name)
        _check(chart_name, f"{pair_id}/template-registry")

    log.append("")
    log.append(f"# RESULT  passes={passes}  failures={failures}")

    return passes, failures, log


def _registered_pair_ids() -> list[str]:
    """Registered pairs via the portal's own discovery (META-CMP scope rule)."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app_dir = os.path.join(repo_root, "app")
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    from components.pair_registry import load_pair_registry

    return sorted(p["pair_id"] for p in load_pair_registry())


def _run_and_log(pair_id: str, log_dir: str) -> int:
    """Run the smoke for one pair, write its log, print output. Returns failures."""
    passes, failures, log = run_smoke_test(pair_id)
    date_tag = _dt.datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(log_dir, f"loader_{pair_id}_{date_tag}.log")
    with open(log_path, "w") as f:
        f.write("\n".join(log) + "\n")

    print("\n".join(log))
    print(f"\nLog written: {log_path}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pair_id", nargs="?", default=None, help="e.g. hy_ig_v2_spy")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run the smoke over every registered pair (META-CMP T1.2); "
        "exit non-zero if any pair reports failures > 0",
    )
    parser.add_argument(
        "--log-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Where to write loader_{pair_id}_{date}.log",
    )
    args = parser.parse_args()

    if args.all == bool(args.pair_id):
        parser.error("provide exactly one of: pair_id, --all")

    if not args.all:
        failures = _run_and_log(args.pair_id, args.log_dir)
        return 0 if failures == 0 else 1

    # --all mode: iterate every registered pair, aggregate exit status.
    pair_ids = _registered_pair_ids()
    summary: list[tuple[str, int]] = []
    for pair_id in pair_ids:
        print(f"\n{'=' * 60}\n=== {pair_id}\n{'=' * 60}")
        failures = _run_and_log(pair_id, args.log_dir)
        summary.append((pair_id, failures))

    total_failures = sum(f for _, f in summary)
    print(f"\n{'=' * 60}")
    print(f"# ALL-PAIRS SUMMARY  pairs={len(summary)}  total_failures={total_failures}")
    for pair_id, failures in summary:
        print(f"#   {'PASS' if failures == 0 else 'FAIL'}  {pair_id}  failures={failures}")
    return 0 if total_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
