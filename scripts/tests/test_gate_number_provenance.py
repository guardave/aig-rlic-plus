"""Tests for scripts/gate_number_provenance.py (structured-prose layer 2 v2: provenance sentinels).

In gate mode every artifact value a pair config formats into prose carries a sentinel naming its source
(components.provenance, components.winner_fields); the gate fails on any number in the config's authored text
outside a verified sentinel or an allowlist span. A stale number therefore fails even when it EQUALS some
artifact value (the coincidence path of the value-matching v1). The pilot renders run the real pages
in-process (AppTest), ~5 s per page."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gate_number_provenance as g  # noqa: E402

PAIR = "unrate_spy"
HAVE = (g.RESULTS / PAIR / "winner_summary.json").exists() and g._page_file(PAIR, "story") is not None
pytestmark = pytest.mark.skipif(not HAVE, reason="unrate_spy artifacts not present")


def _ws():
    return g.json.loads((g.RESULTS / PAIR / "winner_summary.json").read_text())


# Codex B0f: ways code can build a number that layer 1 cannot see. Each yields authored prose; every value is
# chosen to EQUAL a real unrate artifact value, so value-matching alone would pass it.
def _stale_values():
    ws = _ws()
    f = ws["winner_fields"]
    return {"oos_sharpe": f["oos_sharpe"]["text"], "bh_oos_sharpe": f["bh_oos_sharpe"]["text"],
            "is_sharpe": f["is_sharpe"]["text"], "n_valid": f["n_valid"]["text"]}


def _evasions(v):
    from math import pi  # noqa: F401  (an imported constant)
    d = {"s": v["oos_sharpe"]}

    def doc():
        pass
    doc.__doc__ = f"Its training Sharpe was {v['is_sharpe']}."
    return {
        "number_parsed_from_dict_text": f"The rule scored {d['s']} out of sample.",
        "rendered_docstring": doc.__doc__,
        "formatted_literal_equal_to_artifact": f"Buy-and-hold scored {float(v['bh_oos_sharpe']):.2f}.",
        "count_equal_to_artifact": f"It was the best of {int(v['n_valid'])} valid rules.",
    }


@pytest.fixture(scope="module")
def clean():
    return g.check_pair(PAIR)


def test_clean_pilot_render_passes(clean):
    findings, stats = clean
    assert findings == [], findings[:5]
    assert stats["tagged_values"] > 50                       # the pages really carry sentinels


def test_authored_stale_numbers_equal_to_artifact_values_fail():
    v = _stale_values()
    ev = _evasions(v)
    pool = g.load_pool(PAIR)
    for text in ev.values():                                 # v1 value matching would accept every one of them
        assert g.check_text(text, pool, [], "v1") == []

    def inject(mod):
        mod.STORY_CONFIG.PLAIN_ENGLISH = mod.STORY_CONFIG.PLAIN_ENGLISH + " " + " ".join(ev.values())
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    for name, text in ev.items():
        num = g.NUM.search(text).group(0)
        assert any(b.startswith("UNTAGGED") and repr(num) in b for b in bad), (name, bad[:5])


def test_wrong_sentinel_value_fails():
    from components import provenance as P

    def inject(mod):
        mod.STORY_CONFIG.PLAIN_ENGLISH = (mod.STORY_CONFIG.PLAIN_ENGLISH + " Out-of-sample Sharpe "
                                          + P.tag("1.91", "wf:oos_sharpe") + ".")
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    assert any(b.startswith("MISMATCH") and "1.91" in b for b in bad), bad[:5]


def test_parse_markers_and_source_evaluation():
    from components import provenance as P
    import os
    os.environ["AIG_PROVENANCE_GATE"] = "1"
    try:
        ws = P.json_file(g.RESULTS / PAIR / "winner_summary.json")
        text = f"{P.A0}Sharpe {ws['oos_sharpe']:.2f} vs {ws['bh_sharpe'] * 100:.0f} and 0.77.{P.A1}"
    finally:
        os.environ.pop("AIG_PROVENANCE_GATE")
    clean, kinds, sents = g.parse_markers(text)
    assert clean.startswith("Sharpe ") and len(sents) == 2
    for a, b, src, shown in sents:
        assert g.verify_sentinel(src, shown, _ws()["winner_fields"]) is None
    f, c = g.check_tagged(text, g.load_pool(PAIR), [], {}, "t")
    assert c["tagged_values"] == 2 and any("0.77" in x for x in f)


# ----------------------------------------------------------------------------------------- regression record
# Codex B0f evasions (ported from v1): each snippet builds a number in code; layer 1 cannot see it. Under v2 every
# one must FAIL as an UNTAGGED authored number when it reaches a page (one render, all injected).
_DOC = '''def _f():
    """Out-of-sample Sharpe 7.77 versus buy-and-hold."""
TEXT = _f.__doc__'''
B0F_EVASIONS = {
    "number_parsed_from_dict_text": ('_X = {"s": "Sharpe 7.77"}\nTEXT = "The rule scored " + _X["s"].split()[1] + "."',
                                     "7.77"),
    "rendered_docstring": (_DOC, "7.77"),
    "imported_constant": ("from math import pi\nTEXT = f'Out-of-sample Sharpe {pi:.2f}.'", "3.14"),
    "subscript_context": ("TEXT = f'Out-of-sample Sharpe {[2.72, 0][0]}.'", "2.72"),
    "precision_helper_arg": ("def _pct(v, nd=1):\n    return f'{v * 100:.{nd}f}%'\nTEXT = 'Annual return ' + _pct(0.613)",
                             "61.3%"),
    "comparison_constant": ("TEXT = f'Sharpe {(0.5 > 0) * 5.13:.2f}.'", "5.13"),
    "unit_conversion": ("TEXT = f'Annual return {0.0425 * 12 * 100:.1f}%.'", "51.0%"),
}


def _b0f_texts():
    out = {}
    for name, (code, num) in B0F_EVASIONS.items():
        ns: dict = {}
        exec(code, ns)
        out[name] = (ns["TEXT"], num)
    return out


@pytest.mark.parametrize("name", sorted(B0F_EVASIONS))
def test_codex_b0f_evasions_fail_layer2_v2(name):
    text, num = _b0f_texts()[name]

    def inject(mod):
        mod.STORY_CONFIG.PLAIN_ENGLISH = mod.STORY_CONFIG.PLAIN_ENGLISH + " " + text
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    assert any(b.startswith("UNTAGGED") and repr(num) in b for b in bad), (name, bad[:6])


def test_resolution_rules_template_fallback():
    """v1 value matching, still used for shared-template text."""
    pool = g.load_pool(PAIR)
    ws = _ws()
    assert g.check_text(f"Test-period Sharpe {ws['oos_sharpe']:.2f}.", pool, [], "t") == []
    assert g.check_text(f"Drawdown {ws['oos_max_drawdown'] * 100:.1f}%.", pool, [], "t") == []
    assert g.check_text(f"Window {ws['oos_period_start']} to {ws['oos_period_end']}.", pool, [], "t") == []
    assert g.check_text("It was right 97.3% of the time.", pool, [], "t")
    assert g.check_text("The rule waits nineteen months.", pool, [], "t")
    assert g.check_text("It ranks at the 82nd percentile.", pool, [], "t")


def test_injected_stale_prose_fails_end_to_end_v2():
    """The v1 end-to-end case (stale Sharpe 7.77 appended to the live config) under v2."""
    def inject(mod):
        mod.STORY_CONFIG.PLAIN_ENGLISH = mod.STORY_CONFIG.PLAIN_ENGLISH + " Its test-period Sharpe was 7.77."
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    assert any(b.startswith("UNTAGGED") and "'7.77'" in b for b in bad), bad[:3]
