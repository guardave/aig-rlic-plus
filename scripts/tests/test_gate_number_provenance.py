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
