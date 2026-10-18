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
                                          + P._tag("1.91", "wf:oos_sharpe") + ".")
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    assert any(b.startswith("MISMATCH") and "1.91" in b for b in bad), bad[:5]


def test_parse_markers_and_source_evaluation():
    from components import provenance as P
    import os
    os.environ["AIG_PROVENANCE_GATE"] = "1"
    try:
        ws = P.json_file(g.RESULTS / PAIR / "winner_summary.json")
        text = (f"{P.A0}StoryConfig.X{P.AP}Sharpe {ws['oos_sharpe']:.2f} vs {ws['bh_ann_return'] * 100:.0f} and "
                f"{ws['oos_max_drawdown']:.1%} and 0.77.{P.A1}")
    finally:
        os.environ.pop("AIG_PROVENANCE_GATE")
    clean, kinds, paths, sents, defs = g.parse_markers(text)
    assert clean.startswith("Sharpe ") and len(sents) == 3 and paths[0] == "StoryConfig.X"
    assert [u for *_, u, _ in sents] == ["raw", "raw", "pct"]
    for a, b, src, unit, shown in sents:
        assert g.verify_sentinel(src, unit, shown, _ws()["winner_fields"], PAIR) is None
    f, c = g.check_tagged(text, g.load_pool(PAIR), [], {}, "t", PAIR)
    assert c["tagged_values"] == 3 and any("0.77" in x for x in f)


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


# ------------------------------------------------------------------------- Codex L2v2 review: every repro FAILs
def _gate_env():
    import os
    os.environ["AIG_PROVENANCE_GATE"] = "1"


def _gate_off():
    import os
    os.environ.pop("AIG_PROVENANCE_GATE", None)


def _authored(body, path="StoryConfig.PLAIN_ENGLISH"):
    from components import provenance as P
    return f"{P.A0}{path}{P.AP}{body}{P.A1}"


def _check(text, approved=None):
    return g.check_tagged(text, g.load_pool(PAIR), g._allow_entries(), _ws()["winner_fields"], "t", PAIR,
                          approved)[0]


def test_l2v2_f1_constant_cannot_mint_a_tag():
    from components import provenance as P
    _gate_env()
    try:
        a = _authored("Stale " + P._tag("987.65", "const:987.65"))
        b = _authored(f"Stale {P._PNum(987.65, 'const:987.65'):.2f}")
        c = _authored(f"Stale {P._PNum(987.65, 'mul(const:987.65,const:1.0)'):.2f}")
    finally:
        _gate_off()
    for t in (a, b, c):
        assert any(x.startswith("MISMATCH") for x in _check(t)), t
    with pytest.raises(P.SourceError):
        P.evaluate("const:987.65", {}, PAIR)
    with pytest.raises(P.SourceError):                       # a constant that is not a unit operand
        P.evaluate(f"mul(art:{PAIR}/winner_summary.json#/oos_sharpe,const:7.0)", {}, PAIR)


def test_l2v2_f2_sources_must_live_in_the_pairs_results(tmp_path):
    from components import provenance as P
    f = tmp_path / "not_results.json"
    f.write_text('{"value": 12.34}')
    other = next(p for p in g.RESULTS.iterdir() if p.is_dir() and p.name != PAIR and (p / "winner_summary.json").exists())
    _gate_env()
    try:
        outside = P.json_file(f)
        a = _authored(f"Stale {outside['value']:.2f}")
        b = _authored(f"Stale {P.json_file(other / 'winner_summary.json')['oos_sharpe']:.2f}")
    finally:
        _gate_off()
    assert any("MISMATCH" in x and "outside" in x for x in _check(a))
    assert any("MISMATCH" in x and "not inside" in x for x in _check(b))     # another pair's results


def test_l2v2_f3_chart_text_is_extracted_and_checked():
    import json
    spec = json.dumps({"data": [{"name": "Winner (Sharpe 987.65)", "text": ["987.65"]}],
                       "layout": {"title": {"text": "Chart title 987.65"}, "yaxis": {"title": {"text": "Axis 987.65"}},
                                  "annotations": [{"text": "note 987.65"}]}})
    texts = g._chart_texts(spec)
    assert len(texts) == 5 and all("987.65" in t for t in texts)
    for t in texts:
        assert any(x.startswith("UNRESOLVED") for x in _check(t)), t

    from streamlit.testing.v1 import AppTest
    at = AppTest.from_string("import streamlit as st, plotly.graph_objects as go\n"
                             "st.plotly_chart(go.Figure(layout={'title': {'text': 'Chart title 987.65'}}))\n").run()
    blocks = []
    g._texts(at._tree, blocks)
    assert ("chart", "Chart title 987.65") in blocks


def test_l2v2_f4_table_cells_are_sentinel_verified_and_sign_aware():
    from components import provenance as P
    _gate_env()
    try:
        wrong = "Sharpe | " + P._tag("987.65", "wf:oos_sharpe")
    finally:
        _gate_off()
    tpool = g.load_pool(PAIR)
    f, _ = g.check_tagged(wrong, tpool, [], _ws()["winner_fields"], "t [table]", PAIR)
    assert any(x.startswith("MISMATCH") for x in f)
    f, _ = g.check_tagged(_authored("Stale estimate -57"), tpool, [], {}, "t [table]", PAIR)
    assert f


def test_l2v2_f5_template_matching_is_sign_sensitive():
    x = _ws()["oos_sharpe"]
    assert x > 0
    assert any(t.startswith("UNRESOLVED") for t in _check(f"Out-of-sample Sharpe {-x:.2f}."))
    assert _check(f"Out-of-sample Sharpe {x:.2f}.") == []


def test_l2v2_f6_winner_field_text_is_reconciled_with_value():
    fields = {"metric": {"value": 1.23, "text": "9.99"}, "pct": {"value": 0.239, "text": "23.9%"},
              "lead": {"value": 5, "text": "five"}, "bad_word": {"value": 5, "text": "seven"},
              "rng": {"value": [4, 5, 6], "text": "L4-L6"}}
    assert g.verify_sentinel("wf:metric", "raw", "9.99", fields, PAIR)
    assert g.verify_sentinel("wf:pct", "raw", "23.9%", fields, PAIR) is None
    assert g.verify_sentinel("wf:lead", "raw", "five", fields, PAIR) is None
    assert g.verify_sentinel("wf:bad_word", "raw", "seven", fields, PAIR)
    assert g.verify_sentinel("wf:rng", "raw", "L4-L6", fields, PAIR) is None


def test_l2v2_f7_every_number_and_the_declared_unit_are_checked():
    src = f"art:{PAIR}/winner_summary.json#/oos_ann_return"          # a ratio: may be shown as a percent
    x = _ws()["oos_ann_return"]
    assert g.verify_sentinel(src, "raw", f"{x:.4f} and 987.65", {}, PAIR)          # extra number in the span
    assert g.verify_sentinel(src, "raw", f"{x * 100:.0f}%", {}, PAIR)               # raw value shown as x100
    assert g.verify_sentinel(src, "pct", f"{x * 100:.0f}%", {}, PAIR) is None       # declared percent
    assert g.verify_sentinel(src, "pct", f"{x:.4f}", {}, PAIR)                      # declared percent, raw shown


@pytest.mark.parametrize("body", ["It returned seventy percent.", "It returned zero percent.",
                                  "It returned one percent.", "It held twenty-one months.",
                                  "It returned 二十 percent.", "It ranked Ⅻ.", "Sharpe 1.⁹."])
def test_l2v2_f8_number_words_and_non_ascii_numerals_fail(body):
    assert _check(_authored(body)), body


@pytest.mark.parametrize("body", ["The stale estimate used a 12-month return.", "The stale Sharpe was reported in 2025.",
                                  "The stale allocation holds 100% SPY."])
def test_l2v2_f9_phrase_allowlists_are_bound_to_config_paths(body):
    assert any(x.startswith("UNTAGGED") for x in _check(_authored(body))), body


def test_l2v2_f10_definition_text_must_come_from_an_approved_field(tmp_path):
    from components import provenance as P
    t = _authored(f"Stale result {P.D0}987.65 percent{P.D1}")
    assert any(x.startswith("DEFINITION") for x in _check(t, approved=set()))
    import gate_structured_prose as L1
    cfg = tmp_path / "x_config.py"
    cfg.write_text("from components import provenance as P\nX = P.definition_text('987.65 percent')\n"
                   "Y = P._tag('987.65', 'const:987.65')\nZ = P.definitions({'a': '1'})\n"
                   "from components.provenance import _PNum\n")
    found = L1.provenance_api(cfg)
    assert len(found) == 4, found                              # X, Y (P._tag), Z (not *_TEXT), the import


def test_l2v2_f11_markers_never_leak_into_a_later_normal_render():
    from components import provenance as P
    g.render_pages(PAIR, sections=("story",), tagged=True)
    plain = g.render_pages(PAIR, sections=("story",), tagged=False)
    text = "".join(b for blocks in plain.values() for _, b in blocks)
    assert not any(c in text for c in (P.A0, P.A1, P.AP, P.S0, P.S1, P.S2, P.D0, P.D1, P.U))
    import sys as _s
    assert f"pair_configs.{PAIR}_config" not in _s.modules
    assert not hasattr(_s.modules.get("pair_configs"), f"{PAIR}_config")


# --------------------------------------------------------------------- Codex L2v3 review: every repro FAILs (v4)
def test_l2v3_n1_any_other_import_or_dynamic_access_of_provenance_fails(tmp_path):
    import gate_structured_prose as L1
    cases = {
        "import_module_alias": "import components.provenance as sneaky\nX = sneaky._tag('0.43', 'wf:oos_sharpe')\n",
        "from_import": "from components.provenance import json_file\n",
        "getattr": "from components import provenance as P\nX = getattr(P, '_tag')('0.43', 'wf:oos_sharpe')\n",
        "importlib": "import importlib\nM = importlib.import_module('components.provenance')\n",
        "dunder_import": "M = __import__('components.provenance')\n",
        "other_alias": "from components import provenance as Q\n",
        "sys_modules": "import sys\nM = sys.modules['components.provenance']\n",
    }
    for name, code in cases.items():
        cfg = tmp_path / f"{name}_config.py"
        cfg.write_text(code)
        assert L1.provenance_api(cfg), name


def test_l2v3_n2_unit_operations_need_a_matching_declared_kind():
    from components import provenance as P
    ws = f"art:{PAIR}/winner_summary.json#"
    with pytest.raises(P.SourceError):                              # a lead shown x100 ("500")
        P.kind_of(f"mul({ws}/lead_value,const:100)", PAIR)
    assert g.verify_sentinel(f"mul({ws}/lead_value,const:100)", "raw", "500", {}, PAIR)
    with pytest.raises(P.SourceError):                              # a Sharpe annualised
        P.kind_of(f"mul({ws}/oos_sharpe,const:12)", PAIR)
    with pytest.raises(P.SourceError):                              # a Sharpe shown x100
        P.kind_of(f"mul({ws}/oos_sharpe,const:100)", PAIR)
    assert g.verify_sentinel(f"{ws}/oos_sharpe", "pct", "43%", {}, PAIR)   # percent display of a non-ratio
    assert P.kind_of(f"mul({ws}/oos_ann_return,const:100)", PAIR) == "percent"
    with pytest.raises(P.SourceError):                              # wrong-frequency annualisation (unrate: 12)
        P.kind_of(f"mul(art:{PAIR}/regime_quartile_returns.csv#r0/mean_return,const:252)", PAIR)
    assert P.kind_of(f"mul(art:{PAIR}/regime_quartile_returns.csv#r0/mean_return,const:12)", PAIR) == "ratio"


def test_l2v3_n3_every_visible_plotly_string_is_checked():
    import json
    spec = json.dumps({"data": [{"name": "clean", "y": [987.65], "text": ["987.65"],
                                 "texttemplate": "Stale %{y:.2f}; fixed 876.54", "hovertext": ["Hover 765.43"],
                                 "hovertemplate": "Hover fixed 654.32<extra></extra>",
                                 "marker": {"colorbar": {"title": {"text": "Bar 432.10"}}}}],
                       "layout": {"xaxis": {"tickvals": [1], "ticktext": ["Tick 543.21"]},
                                  "shapes": [{"label": {"text": "Shape 321.09"}}]}})
    texts = g._chart_texts(spec)
    for n in ("987.65", "876.54", "765.43", "654.32", "543.21", "432.10", "321.09"):
        assert any(n in t for t in texts), (n, texts)
        assert any(x.startswith("UNRESOLVED") for t in texts if n in t for x in _check(t)), n


def test_l2v3_n4_definitions_must_use_numbers_the_spec_or_pipeline_declares():
    from components import provenance as P
    bad = _authored(f"Threshold {P.D0}Stale result 987.65 percent{P.D1}")
    assert any(x.startswith("DEFINITION") and "987.65" in x for x in _check(bad, approved={"Stale result 987.65 percent"}))
    ok = _authored(f"Threshold {P.D0}its rolling 60-month 75th percentile{P.D1}")
    assert not [x for x in _check(ok, approved={"its rolling 60-month 75th percentile"}) if "60" in x or "75" in x]


def test_l2v3_n5_winner_field_reconcile_is_sign_sensitive():
    fields = {"metric": {"value": 1.23, "text": "-1.23"}, "dd": {"value": -0.239, "text": "23.9%"}}
    assert g.reconcile_field("metric", fields, PAIR)
    assert g.verify_sentinel("wf:metric", "raw", "-1.23", fields, PAIR)
    assert g.reconcile_field("dd", fields, PAIR)
    assert g.reconcile_field("dd", {"dd": {"value": -0.239, "text": "-23.9%"}}, PAIR) is None


def test_signal_display_digits_reconcile_against_the_spec_not_blindly():
    fields = {"signal_display": {"value": "zscore_60m", "text": "60-month unemployment z-score"},
              "stale_display": {"value": "zscore_60m", "text": "987-month unemployment z-score"}}
    assert g.reconcile_field("signal_display", fields, PAIR) is None          # 60 is declared by the unrate spec
    assert g.reconcile_field("stale_display", fields, PAIR)                   # 987 is not


def test_headline_numbers_must_be_tagged_even_in_template_text():
    x = _ws()["oos_sharpe"]
    f, _ = g.check_tagged(f"The test-period Sharpe difference is {x:+.2f} (95% interval -0.95 to -0.28).",
                          g.load_pool(PAIR), g._allow_entries(), {}, "t", PAIR, None, headline=True)
    assert any(t.startswith("HEADLINE") for t in f)
    findings, stats = g.check_pair(PAIR, g.render_pages(PAIR, sections=("strategy",)))
    assert findings == [] and stats["template_blocks"]                          # residual blocks are listed


def test_n4_definition_pool_takes_only_named_pipeline_parameters(tmp_path, monkeypatch):
    # Lead tightening of N4: incidental literals inside pipeline code (seeds, clip bounds, ranges) are not
    # declarations; only named module-level literal constants of the pipeline (plus the spec, manifest, registry)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "pair_pipeline_toy_spy.py").write_text(
        "WINDOW = 36\nLAGS = (1, 3)\nDERIVED = WINDOW * 2\n"
        "def run():\n    seed = 987\n    return list(range(-20, 21))\n")
    monkeypatch.setattr(g, "REPO", tmp_path)
    monkeypatch.setattr(g, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(g, "REGISTRY", tmp_path / "registry.json")
    g._SPEC_POOL.pop("toy_spy", None)
    pool = g.spec_numbers("toy_spy")
    assert {36.0, 1.0, 3.0} <= pool
    assert not {987.0, 20.0, 21.0, 72.0} & pool, pool                 # code literals and computed values excluded
    assert 0 <= g.coincidence_definition("toy_spy")["declared_mix"] < 0.05
    g._SPEC_POOL.pop("toy_spy", None)
