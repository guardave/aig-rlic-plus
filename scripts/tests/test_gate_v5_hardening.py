"""Number-provenance gate v5 hardening (Lead brief items 2-7 = QA L2v4 #3, #4, #5, #6, addendum, #8). Every QA
repro is a must-FAIL case; each has a passing control."""
import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
import gate_number_provenance as g  # noqa: E402
import gate_structured_prose as gs  # noqa: E402

PAIR = "unrate_spy"
HAVE = (g.RESULTS / PAIR / "winner_summary.json").exists()
pytestmark = pytest.mark.skipif(not HAVE, reason="pilot artifacts not present")


def _authored(text, path="STORY_CONFIG.X"):
    from components.provenance import A0, A1, AP
    return f"{A0}{path}{AP}{text}{A1}"


def _check(text, **kw):
    return g.check_tagged(text, g.load_pool(PAIR), g._allow_entries(), {}, "t", PAIR, **kw)[0]


# ---------------------------------------------------------------- item 2: NON_PROSE blanking (QA #3)
@pytest.mark.parametrize("text,num", [("982.22/yr", "982.22"), ("988.8/989.9", "988.8"), ("code #984", "984"),
                                      ("Sharpe <985.5 and the other >", "985.5"), ("stale_986.6", "986.6"),
                                      ("(https://x.org/a),991.1,", "991.1")])
def test_code_built_numbers_next_to_markup_are_untagged(text, num):
    f = _check(_authored(f"The rule scored {text} here."))
    assert any(x.startswith("UNTAGGED") and repr(num) in x for x in f), f


def test_identifiers_paths_and_css_stay_blanked():
    for t in ("rule T_roll_p75 and hy_ig_pctrank_1260d and chg_12m", "see results/unrate_spy/x.csv and app/a.py",
              '<span style="color:#595959">ok</span>', "scripts/_regime_causal.fit_hmm_causal(x)"):
        assert not list(g.NUM.finditer(g.strip_non_prose(t))), t


def test_markup_numbers_fail_end_to_end_in_a_render():
    def inject(mod):
        x = 982.22
        mod.STORY_CONFIG.PLAIN_ENGLISH += f" Turnover was {x:.2f}/yr and code #984 and stale_986.6 here."
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    for num in ("982.22", "984", "986.6"):
        assert any(b.startswith("UNTAGGED") and repr(num) in b for b in bad), (num, bad[:6])


# ---------------------------------------------------------------- item 3: unit registry (QA #4)
def test_percent_stored_leaves_are_percent_not_ratio():
    from components import provenance as P
    assert P.leaf_kind("art:hy_ig_spy/evidence_facts_20261017.json#/hmm/pct_is") == "percent"
    assert P.leaf_kind("art:x/evidence_facts.json#/regime_quartile_ann_return_pct/Q1") == "percent"
    # QA repro: 43.48 shown as 4348.0% was accepted
    r = g.verify_sentinel("art:hy_ig_spy/evidence_facts_20261017.json#/hmm/pct_is", "pct", "4348.0%", {}, "hy_ig_spy")
    assert r and "percent" in r


def test_count_rule_is_anchored():
    from components import provenance as P
    for leaf in ("#/bh_return", "#/position", "#/mean", "#/oos_excess_mean/value", "#/ann_return_pct"):
        assert P.leaf_kind("art:x/w.json" + leaf) != "count", leaf
    for leaf in ("#/n_valid", "#/oos_n", "#/null_tournament/n_draws", "#/vs_buy_hold/draws"):
        assert P.leaf_kind("art:x/w.json" + leaf) == "count", leaf


def test_undeclared_leaves_cannot_be_combined_and_numeric_leaves_need_a_kind(tmp_path, monkeypatch):
    from components import provenance as P
    with pytest.raises(P.SourceError):
        P.kind_of("sub(art:x/w.json#/foo_metric,art:x/w.json#/bar_metric)")
    assert not g._kind_value_ok("ratio", 43.48) and g._kind_value_ok("ratio", 0.43)
    assert not g._kind_value_ok("count", 2.5) and not g._kind_value_ok("pvalue", 1.2)
    monkeypatch.setattr(P, "evaluate", lambda src, fields=None, pair=None, _root=True: 7.5)
    assert "no declared kind" in g.leaf_kind_check("art:x/w.json#/foo_metric", "x")


# ---------------------------------------------------------------- item 4: P trust boundary (QA #5)
_HEAD = "from components import provenance as P\nfrom components.page_templates import MethodologyConfig\n"


@pytest.mark.parametrize("body", [
    "Q = P\nx = Q.json_file('a')\n",                                      # alias
    "import components\nx = components.provenance\n",                       # package import + attribute
    "import components.provenance as Z\n",
    "x = P.json_file('a')\ny = type(x)('1.00', 'art:unrate_spy/winner_summary.json#/bh_sharpe')\n",
    "from components.zz_qa_reexport import _tag\n",                         # re-exporting module
    "import operator\nf = operator.attrgetter('_tag')(P)\n",
    "import inspect\nm = inspect.getmembers(P)\n",
    "from components.winner_fields import FieldText\n",
    "from components import winner_fields\n",
    "flag = P.gate_on()\n", "o = P.os\n", "f = P._tag\n", "d = P.DefText\n",
    "x = P.json_file('a')\nx.src = 'art:unrate_spy/winner_summary.json#/bh_sharpe'\n",
    "x = P.json_file('a')\ny = x.__class__('1.00')\n",
    "from .helpers import anything\n", "import sys\n",
    "def f(mod=P):\n    return mod\n",                                    # P passed / stored
])
def test_provenance_api_rejects_forge_routes(tmp_path, body):
    cfg = tmp_path / "zz_spy_config.py"
    cfg.write_text(_HEAD + body)
    assert gs.provenance_api(cfg), body


def test_provenance_api_accepts_the_pilot_configs():
    for pair in ("unrate_spy", "cc_delinquency_spy", "hy_ig_spy"):
        assert gs.provenance_api(g.APP / "pair_configs" / f"{pair}_config.py") == [], pair


# ---------------------------------------------------------------- item 5: authored-text escapes (QA #6)
def _fake_module():
    m = types.ModuleType("pair_configs.zz_spy_config")

    class StoryConfig:
        TITLE = "S=0.43,BH=1.00"
        PCT = "+4.9%"
        BARE = "0.43"
        CODE = "zscore_60m"
        PAIRS = ("Sharpe 0.43", ("nested 0.44",))
        TAGS = {"Sharpe 0.45"}

        def caption(self):
            return "method returns 0.46"

        @property
        def note(self):
            return "property returns 0.47"
    StoryConfig.__module__ = m.__name__
    m.StoryConfig = StoryConfig
    m.SCOPE_NOTE = "module string 0.48"

    def public_text():
        return "function returns 0.49"
    public_text.__module__ = m.__name__
    m.public_text = public_text
    m.PLANTED = "Fits  here with a hand-typed Sharpe 0.43 value"
    return m


def test_mark_authored_reaches_every_shape(monkeypatch):
    from components.provenance import A0, A1
    monkeypatch.setattr(g, "declared_identifiers", lambda pair: {"zscore_60m"})
    m = _fake_module()
    g._mark_authored(m, PAIR)
    sc = m.StoryConfig
    for v in (sc.TITLE, sc.PCT, sc.BARE, sc.PAIRS[0], sc.PAIRS[1][0], next(iter(sc.TAGS)), sc().caption(),
              sc().note, m.SCOPE_NOTE, m.public_text()):
        assert v.startswith(A0), v
    assert sc.CODE == "zscore_60m"                                   # a declared identifier stays a lookup key
    # QA repro: a planted U+E006 (authored-close) ended the authored span early; it is removed
    assert m.PLANTED.count(A1) == 1 and m.PLANTED.endswith(A1)
    f = _check(m.PLANTED)
    assert any(x.startswith("UNTAGGED") and "'0.43'" in x for x in f), f


def test_whitespace_free_title_fails_end_to_end():
    def inject(mod):
        mod.STORY_CONFIG.REGIME_TITLE = "S=0.43,BH=1.00"
    bad, _ = g.check_pair(PAIR, g.render_pages(PAIR, sections=("story",), prepare=inject))
    assert any(b.startswith("UNTAGGED") and "'0.43'" in b for b in bad), bad[:6]


# ---------------------------------------------------------------- item 6: definition binding (QA addendum)
def _def(text, code):
    from components.provenance import D0, D1
    g._DEF_CODE.setdefault(PAIR, {})[text] = code
    return _authored(f"Threshold {D0}{text}{D1}"), {text}


@pytest.mark.parametrize("text,code", [("its rolling 12-month 75th percentile", "T_roll_p75"),
                                       ("its rolling 36-month 90th percentile", "T_roll_p90"),
                                       ("a z-score of 1.2", "T_z_1.0")])
def test_definition_numbers_bind_to_their_own_code(text, code):
    t, ok = _def(text, code)
    assert any(x.startswith("DEFINITION") for x in _check(t, approved=ok)), text


def test_definition_controls_pass():
    for text, code in (("its rolling 60-month 75th percentile", "T_roll_p75"), ("a z-score of 1.0", "T_z_1.0"),
                       ("its rolling 5-year 90th percentile", "T_roll_p90")):
        t, ok = _def(text, code)
        assert not [x for x in _check(t, approved=ok) if x.startswith("DEFINITION")], text


def test_categorical_label_binds_to_its_code():
    f = {"signal_display": {"value": "zscore_60m", "text": "12-month unemployment z-score"}}
    assert g.reconcile_field("signal_display", f, PAIR)                     # QA repro: was accepted
    f["signal_display"]["text"] = "60-month unemployment z-score"
    assert g.reconcile_field("signal_display", f, PAIR) is None


def test_code_params_follow_the_spec():
    cp = g.code_params(PAIR)
    assert {60.0, 75.0, 0.75} <= cp["T_roll_p75"] and 12.0 not in cp["T_roll_p75"]
    assert 60.0 in cp["zscore_60m"] and 12.0 not in cp["zscore_60m"]
    hy = g.code_params("hy_ig_spy")
    assert 63.0 in hy["S4b_roc_63d"] and 252.0 not in hy["S4b_roc_63d"]       # loop-built columns
    assert 504.0 not in hy["S6_hmm_stress"]                                   # the feature frame is not followed


def test_definition_acceptance_is_reported():
    d = g.coincidence_definition(PAIR)
    assert d["codes"] >= 10 and d["per_code_small"] < 0.10 and 0 < d["declared_small"] <= 1


# ---------------------------------------------------------------- item 7: missed surfaces (QA #8)
def test_plotly_prefixes_customdata_and_table_cells_are_extracted():
    spec = json.dumps({"data": [{"type": "scatter", "customdata": ["cd 981.5"], "hovertemplate": "%{customdata}"},
                                {"type": "table", "header": {"values": ["hdr 982.5"]},
                                 "cells": {"values": [["cell 983.5"]]}}],
                       "layout": {"yaxis": {"tickprefix": "pre 984.5", "ticksuffix": "suf 985.5"},
                                  "coloraxis": {"colorbar": {"ticksuffix": "cb 986.5"}}}})
    texts = " ".join(g._chart_texts(spec))
    for n in ("981.5", "982.5", "983.5", "984.5", "985.5", "986.5"):
        assert n in texts, n


def test_streamlit_labels_tooltips_and_options_are_extracted():
    from streamlit.testing.v1 import AppTest
    code = ("import streamlit as st\n"
            "with st.expander('Expander 981.1'):\n    st.write('x')\n"
            "st.tabs(['Tab 982.2'])\n"
            "st.selectbox('Select 983.3', ['opt 984.4'], help='help 985.5')\n"
            "st.metric('M', '1', help='mhelp 988.8')\n"
            "st.markdown('md', help='mdhelp 989.9')\n"
            "st.progress(0.3, text='prog 991.2')\n"
            "st.html('<p>html 993.4</p>')\n"
            "st.text_area('ta 996.7', placeholder='ph 997.8')\n")
    at = AppTest.from_string(code).run()
    blocks = []
    g._texts(at._tree, blocks)
    texts = " ".join(t for _, t in blocks)
    for n in ("981.1", "982.2", "983.3", "984.4", "985.5", "988.8", "989.9", "991.2", "993.4", "996.7", "997.8"):
        assert n in texts, n


def test_bibliographic_allowlist_needs_an_author_year_citation():
    # Codex V51-7: the bare '(dddd)' arm matched '(1260d)' in a signal label
    import re
    e = next(x for x in g._allow_entries() if x["id"] == "bibliographic_citation")
    assert re.search(e["regex"], "as shown by Hamilton (1989), regimes")
    assert re.search(e["regex"], "Politis and Romano (1994)")
    assert not re.search(e["regex"], "HY-IG Percentile Rank (1260d)")
    assert not re.search(e["regex"], "the window (2019) only")
    # Codex V52-4: the journal-volume arm needed neither author nor year
    assert not re.search(e["regex"], "*Journal*, 999(888), 777-666")
    assert not re.search(e["regex"], "Sharpe 0.85. *J*, 1(1), 1-2")
    ref = ("Gilchrist, S., & Zakrajsek, E. (2012). Credit spreads and business cycle fluctuations. "
           "*American Economic Review*, 102(4), 1692-1720")
    assert re.search(e["regex"], "- " + ref).group(0) == ref


def test_trigger_card_diagnostic_has_no_computed_count():
    # Codex V51-4: '{found}/3 scenarios located' was an untagged, data-derived number hidden by an allowlist entry
    src = (g.APP / "components" / "instructional_trigger_cards.py").read_text()
    assert "/3 scenarios located" not in src
    assert not [x for x in g._allow_entries() if x["id"] == "trigger_scenarios"]


def test_rolling_sharpe_allowlist_matches_every_producer_window():
    # Lead (d319c206): the 'rolling_window_convention' entry hard-codes '24-month'; every producer of the
    # rolling-Sharpe series (column rolling_sharpe_24m) must use 24 monthly periods or 504 trading days, so a
    # producer change fails here instead of the allowlist quietly blessing stale text
    import re
    root = Path(__file__).resolve().parents[1]
    assert any(x["id"] == "rolling_window_convention" and "24-month" in x["regex"] for x in g._allow_entries())
    writers = {}
    for f in sorted(root.glob("*.py")) + sorted((root / "harness").glob("*.py")):
        lines = f.read_text().splitlines()
        for i, ln in enumerate(lines):
            if re.search(r'"rolling_sharpe_24m"\s*:|columns\s*=\s*\[[^\]]*"rolling_sharpe_24m"', ln):
                ctx = "\n".join(lines[max(0, i - 25):i + 1])
                wins = {int(w) for w in re.findall(r"\.rolling\((\d+)", ctx)}
                wins |= {int(w) for m in re.findall(r"\bwindow\s*=\s*([^\n#]+)", ctx) for w in re.findall(r"\d+", m)
                         if int(w) > 4}
                writers[f"{f.name}:{i + 1}"] = (wins, ctx)
    assert len(writers) >= 3, writers.keys()
    for where, (wins, ctx) in writers.items():
        assert wins and wins <= {24, 504}, (where, wins)
        if 504 in wins:
            assert re.search(r"daily|252|ANN", ctx), (where, "504 must be the daily window")
