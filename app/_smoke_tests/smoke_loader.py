"""Ace Defense-2 loader end-to-end smoke test (APP-ST1).

Parses each HY-IG v2 page's source via AST, extracts every
``load_plotly_chart(name, pair_id=...)`` call site, and executes the loader in
a Streamlit-mock context to verify:

    1. The loader returns a non-None plotly.graph_objs.Figure
    2. ``len(fig.data) > 0`` (at least one trace)
    3. ``fig.layout.title.text`` is a non-empty string

For call sites where ``chart_name`` is a variable (not a literal), we
supplement the static AST list with an explicit mapping of the dynamic
chart_names used by the Evidence page's ``render_method_block`` helper.

Run from repo root::

    python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy

Exits 0 when all call sites pass; exits 1 on any failure. Writes a per-run
log at ``app/_smoke_tests/loader_{pair_id}_{yyyymmdd}.log``.

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


# HY-IG v2 Evidence page uses dynamic chart_name (via render_method_block).
# Enumerate the literal values here to keep the smoke test comprehensive.
EVIDENCE_DYNAMIC_CHARTS = [
    "correlation_heatmap",
    "granger_f_by_lag",
    "local_projections",
    "hmm_regime_probs",
    "quantile_regression",
    "ccf_prewhitened",
    "transfer_entropy",
    "regime_quartile_returns",
]


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

    # Short-form pair token for glob (HY-IG v2 uses pair_id='hy_ig_v2_spy' and
    # page filenames start with '9_hy_ig_v2_spy_*')
    page_glob = os.path.join(
        repo_root, "app", "pages", f"9_{pair_id}_*.py"
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
        title = getattr(getattr(fig.layout, "title", None), "text", None)
        if not title or not str(title).strip():
            failures += 1
            log.append(
                f"FAIL  {source_ref}  chart={chart_name}  fig.layout.title.text empty"
            )
            return
        passes += 1
        log.append(
            f"PASS  {source_ref}  chart={chart_name}  traces={len(fig.data)}  "
            f"title={title!r}"
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
    for chart_name in EVIDENCE_DYNAMIC_CHARTS:
        _check(chart_name, f"{pair_id}/evidence<render_method_block>")

    log.append("")
    log.append(f"# RESULT  passes={passes}  failures={failures}")

    return passes, failures, log


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pair_id", help="e.g. hy_ig_v2_spy")
    parser.add_argument(
        "--log-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Where to write loader_{pair_id}_{date}.log",
    )
    args = parser.parse_args()

    passes, failures, log = run_smoke_test(args.pair_id)
    date_tag = _dt.datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(args.log_dir, f"loader_{args.pair_id}_{date_tag}.log")
    with open(log_path, "w") as f:
        f.write("\n".join(log) + "\n")

    print("\n".join(log))
    print(f"\nLog written: {log_path}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
