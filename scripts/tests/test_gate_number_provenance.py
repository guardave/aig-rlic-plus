"""Tests for scripts/gate_number_provenance.py (structured-prose layer 2: rendered numbers must resolve to the
pair's artifacts). The pilot render runs the real pages in-process (AppTest), so these tests take ~20 s."""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gate_number_provenance as g  # noqa: E402

PAIR = "unrate_spy"
HAVE = (g.RESULTS / PAIR / "winner_summary.json").exists() and g._page_file(PAIR, "story") is not None


@pytest.fixture(scope="module")
def pool():
    return g.load_pool(PAIR)


# Codex B0f: every way code can build a number that layer 1 (authored text + NUMLIT) cannot see. Each snippet
# yields the prose a config would render; layer 2 must flag the stale number in it. Values are chosen so that
# they are not in the unrate pool (asserted), i.e. they test the gate, not a coincidence.
_DOC = '''def _f():
    """Out-of-sample Sharpe 7.77 versus buy-and-hold."""
TEXT = _f.__doc__'''
EVASIONS = {
    "number_parsed_from_dict_text": ('_X = {"s": "Sharpe 7.77"}\nTEXT = "The rule scored " + _X["s"].split()[1] + "."',
                                     7.77),
    "rendered_docstring": (_DOC, 7.77),
    "imported_constant": ("from math import pi\nTEXT = f'Out-of-sample Sharpe {pi:.2f}.'", 3.14),
    "subscript_context": ("TEXT = f'Out-of-sample Sharpe {[2.72, 0][0]}.'", 2.72),
    "precision_helper_arg": ("def _pct(v, nd=1):\n    return f'{v * 100:.{nd}f}%'\nTEXT = 'Annual return ' + _pct(0.613)",
                             61.3),
    "comparison_constant": ("TEXT = f'Sharpe {(0.5 > 0) * 5.13:.2f}.'", 5.13),
    "unit_conversion": ("TEXT = f'Annual return {0.0425 * 12 * 100:.1f}%.'", 51.0),
}


@pytest.mark.skipif(not HAVE, reason="unrate_spy artifacts not present")
@pytest.mark.parametrize("name", sorted(EVASIONS))
def test_codex_b0f_evasions_fail_layer2(pool, name):
    code, stale = EVASIONS[name]
    ns: dict = {}
    exec(code, ns)                                         # what the config would render
    text = ns["TEXT"]
    pct = "%" in text
    assert not g.resolves(stale, 1 if pct else 2, pct, pool), f"{stale} coincides with an artifact value"
    assert g.check_text(text, pool, g._allow_entries(), name), name


@pytest.mark.skipif(not HAVE, reason="unrate_spy artifacts not present")
def test_resolution_rules(pool):
    ws = g.json.loads((g.RESULTS / PAIR / "winner_summary.json").read_text())
    sharpe = ws["oos_sharpe"]
    assert g.check_text(f"Test-period Sharpe {sharpe:.2f}.", pool, [], "t") == []           # displayed rounding
    assert g.check_text(f"Drawdown {ws['oos_max_drawdown'] * 100:.1f}%.", pool, [], "t") == []  # percent x 100
    assert g.check_text(f"Window {ws['oos_period_start']} to {ws['oos_period_end']}.", pool, [], "t") == []
    assert g.check_text("It was right 97.3% of the time.", pool, [], "t")                     # stale percent
    assert g.check_text("The rule waits nineteen months.", pool, [], "t")                     # number word
    assert g.check_text("It ranks at the 82nd percentile.", pool, [], "t")                     # ordinal
    assert not math.isnan(g.coincidence(pool))


@pytest.mark.skipif(not HAVE, reason="unrate_spy artifacts not present")
def test_clean_pilot_render_passes_and_injected_stale_prose_fails(monkeypatch):
    findings, stats = g.check_pair(PAIR)
    assert findings == [], findings[:5]
    assert 0 < stats["coincidence"] < 0.5
    # end to end: a stale number reaching the page through the real render path fails
    cfg_path = g.APP / "pair_configs" / f"{PAIR}_config.py"
    spec = importlib.util.spec_from_file_location(f"pair_configs.{PAIR}_config", cfg_path)
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.syspath_prepend(str(g.APP))
    spec.loader.exec_module(mod)
    mod.STORY_CONFIG.PLAIN_ENGLISH = mod.STORY_CONFIG.PLAIN_ENGLISH + " Its test-period Sharpe was 7.77."
    monkeypatch.setitem(sys.modules, f"pair_configs.{PAIR}_config", mod)
    pages = g.render_pages(PAIR, sections=("story",))
    bad, _ = g.check_pair(PAIR, pages)
    assert any("7.77" in b for b in bad), bad[:3]
