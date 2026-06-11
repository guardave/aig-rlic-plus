#!/usr/bin/env python3
"""META-CMP T2 — Chart-set completeness lint across all registered pairs (GH #7).

For every REGISTERED pair (discovered via app/components/pair_registry.py),
assert that every chart the pair config references exists on disk at
output/charts/<pair_id>/plotly/<chart_name>.json.

References covered (via validate_pair_completeness.collect_config_chart_refs —
GATE-DPS1's config-introspection internals, reused per DRY):
    - *_CHART_NAME attributes (HERO_CHART_NAME, REGIME_CHART_NAME,
      EQUITY_CHART_NAME, DRAWDOWN_CHART_NAME, WALK_FORWARD_CHART_NAME, ...)
    - HISTORY_ZOOM_EPISODES[*].slug → history_zoom_{slug}.json (DPS-EP1)
    - EVIDENCE_METHOD_BLOCKS level1/level2 chart_name where
      chart_status == "ready" (default)

Additionally, for template (APP-PT1) pairs the page template itself
references charts via getattr defaults — e.g.
``getattr(config, "EQUITY_CHART_NAME", "equity_curves")`` in
app/components/page_templates.py loads ``equity_curves.json`` even when the
config never declares the attribute. Those effective references are
collected by AST-scanning page_templates.py for
``getattr(_, "*_CHART_NAME", "<literal>")`` sites, and the default is
checked whenever the config does not override the attribute. (This is what
catches the live "Equity curves pending" class on a config that simply
omits the attr.)

Catches: producer-vs-template drift — a config declaring `drawdown` while
Vera shipped `<pair>_drawdown.json` (or nothing) renders a silent
"Drawdown chart pending" on the cloud page.

Semantics:
    - Config references a chart, file absent      → FAIL
    - Pair has no pair_config module at all       → SKIP with a note
      (e.g. the frozen Sample hy_ig_v2_spy uses bespoke pages, not the
      APP-PT1 template; its chart wiring is covered by smoke_loader's AST
      scan, T1.2)
    - Config module exists but fails to import    → FAIL (a broken config
      breaks the live page too)

Usage:
    python3 scripts/lint_chart_completeness.py

Exit codes:
    0 - every referenced chart exists for every registered pair
    1 - one or more FAILs
    2 - infrastructure error (registry unavailable)

A FAIL means fix the PRODUCER (chart generator or config), never hand-create
the artifact (META-NMF).
"""
from __future__ import annotations

import ast
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from _pair_discovery import registered_pair_ids  # noqa: E402
from validate_pair_completeness import (  # noqa: E402  (GATE-DPS1 internals, DRY)
    _CHARTS_DIR,
    _PAIR_CONFIGS_DIR,
    _load_config_module,
    collect_config_chart_refs,
)

_PAGE_TEMPLATES_PATH = os.path.join(_REPO_ROOT, "app", "components", "page_templates.py")


def template_default_chart_names() -> dict[str, str]:
    """AST-scan page_templates.py for getattr(_, "*_CHART_NAME", "<default>").

    Returns {attr_name: default_chart_name}. These are charts the APP-PT1
    template loads even when the pair config omits the attribute.
    """
    defaults: dict[str, str] = {}
    with open(_PAGE_TEMPLATES_PATH, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) == 3
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
                and node.args[1].value.endswith("_CHART_NAME")
                and isinstance(node.args[2], ast.Constant)
                and isinstance(node.args[2].value, str)
                and node.args[2].value.strip()):
            defaults[node.args[1].value] = node.args[2].value.strip()
    return defaults


def _config_defines_attr(config_mod, attr: str) -> bool:
    """True when STORY_CONFIG / STRATEGY_CONFIG / module defines attr as a str."""
    for owner in (getattr(config_mod, "STORY_CONFIG", None),
                  getattr(config_mod, "STRATEGY_CONFIG", None),
                  config_mod):
        if owner is not None and isinstance(getattr(owner, attr, None), str):
            return True
    return False


def main() -> int:
    try:
        pair_ids = registered_pair_ids()
    except Exception as exc:
        print(f"ERROR: pair registry discovery failed: {exc!r}", file=sys.stderr)
        return 2
    if not pair_ids:
        print("ERROR: pair registry returned no registered pairs.", file=sys.stderr)
        return 2

    n_refs = n_fail = 0
    fail_lines: list[str] = []
    tmpl_defaults = template_default_chart_names()

    for pair_id in pair_ids:
        config_path = _PAIR_CONFIGS_DIR / f"{pair_id}_config.py"
        if not config_path.exists():
            print(f"SKIP  {pair_id} — no pair_config module "
                  f"(bespoke pages; chart wiring covered by smoke_loader T1.2)")
            continue

        config_mod, config_err = _load_config_module(pair_id)
        if config_err:
            n_fail += 1
            msg = f"FAIL  pair={pair_id}  {config_err}"
            fail_lines.append(msg)
            print(msg)
            continue

        refs = collect_config_chart_refs(pair_id, config_mod)
        # Template (APP-PT1) getattr defaults: effective references even when
        # the config omits the attribute. Config overrides are already in refs.
        seen_names = {name for name, _ in refs}
        for attr, default_name in sorted(tmpl_defaults.items()):
            if not _config_defines_attr(config_mod, attr) and default_name not in seen_names:
                seen_names.add(default_name)
                refs.append((default_name,
                             f"page_templates.py getattr default for {attr} "
                             f"(config does not override)"))
        missing = 0
        for chart_name, source in refs:
            n_refs += 1
            chart_path = _CHARTS_DIR / pair_id / "plotly" / f"{chart_name}.json"
            if not chart_path.exists():
                n_fail += 1
                missing += 1
                msg = (f"FAIL  pair={pair_id}  "
                       f"chart=output/charts/{pair_id}/plotly/{chart_name}.json  "
                       f"referenced by {source} but absent on disk")
                fail_lines.append(msg)
                print(msg)
        print(f"PASS  {pair_id} — {len(refs) - missing}/{len(refs)} "
              f"config-referenced charts present" if missing == 0 else
              f"# {pair_id}: {missing}/{len(refs)} referenced charts missing")

    print(f"\n# T2 lint_chart_completeness  pairs={len(pair_ids)}  "
          f"refs_checked={n_refs}  failures={n_fail}")
    if n_fail:
        print("# FAIL — fix the chart generator or config, never hand-create "
              "the artifact (META-NMF).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
