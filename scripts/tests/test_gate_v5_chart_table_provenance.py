"""Number-provenance gate v5, QA L2v4 #1: chart files are checked by provenance record, sourced tables row by row
against their source file. Every QA repro is a must-FAIL case."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
import chart_provenance as cp  # noqa: E402
import gate_number_provenance as g  # noqa: E402

PAIR = "toy_spy"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "results" / PAIR).mkdir(parents=True)
    (tmp_path / "output" / "charts" / PAIR / "plotly").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    ws = {"selection": {"raw_winner_row": {"source_tournament_file": "tournament_results_20261017.csv"}},
          "oos_sharpe": 0.43}
    (tmp_path / "results" / PAIR / "winner_summary.json").write_text(json.dumps(ws))
    (tmp_path / "results" / PAIR / "subperiod_sharpe.csv").write_text("episode,sharpe\nGFC,0.74\nCOVID,0.07\n")
    monkeypatch.setattr(cp, "REPO", tmp_path)
    monkeypatch.setattr(g, "REPO", tmp_path)
    monkeypatch.setattr(g, "RESULTS", tmp_path / "results")
    g._SRC_ROWS.clear()
    return tmp_path


def _chart(repo, name="subperiod_sharpe"):
    f = repo / "output" / "charts" / PAIR / "plotly" / f"{name}.json"
    f.write_text(json.dumps({"data": [{"type": "bar", "x": [0.74, 0.07]}], "layout": {"title": {"text": "x"}}}))
    return f


def test_recorded_chart_verifies(repo):
    f = _chart(repo)
    cp.record(PAIR, f, ["results/toy_spy/subperiod_sharpe.csv"], "test")
    assert cp.verify(PAIR, f.relative_to(repo).as_posix()) is None


def test_stale_input_fails_the_hy_ig_cross_period_class(repo):
    # QA L2v4 #1 / the five stale hy_ig_spy charts: built from CSVs that later changed, never regenerated
    f = _chart(repo)
    cp.record(PAIR, f, ["results/toy_spy/subperiod_sharpe.csv"], "test")
    (repo / "results" / PAIR / "subperiod_sharpe.csv").write_text("episode,sharpe\nGFC,0.61\nCOVID,0.07\n")
    r = cp.verify(PAIR, f.relative_to(repo).as_posix())
    assert r and "stale" in r and "subperiod_sharpe.csv" in r


def test_unrecorded_edited_and_wrong_run_charts_fail(repo):
    f = _chart(repo)
    rel = f.relative_to(repo).as_posix()
    assert "no provenance record" in cp.verify(PAIR, rel)
    cp.record(PAIR, f, ["results/toy_spy/subperiod_sharpe.csv"], "test")
    f.write_text(f.read_text().replace("0.74", "0.75"))                     # hand-edited after recording
    assert "changed after" in cp.verify(PAIR, rel)
    cp.record(PAIR, f, ["results/toy_spy/subperiod_sharpe.csv"], "test")
    ws = repo / "results" / PAIR / "winner_summary.json"
    ws.write_text(ws.read_text().replace("20261017", "20261018"))           # the pair was re-run since
    assert "built for run 20261017" in cp.verify(PAIR, rel)


def test_record_captures_files_the_producer_read(repo):
    import pandas as pd
    p = repo / "data" / "toy.parquet"
    pd.DataFrame({"a": [1.0, 2.0]}).to_parquet(p)
    pd.read_parquet(p)                                                        # native read, via the shim
    with open(repo / "results" / PAIR / "subperiod_sharpe.csv") as fh:       # python open, via the audit hook
        fh.read()
    e = cp.record(PAIR, _chart(repo), (), "test")
    assert {"data/toy.parquet", "results/toy_spy/subperiod_sharpe.csv"} <= set(e["inputs"])
    with pytest.raises(ValueError):
        cp._READS.clear()
        cp.record(PAIR, _chart(repo, "orphan"), (), "test")                   # no inputs at all


def test_gate_reports_stale_chart_files_on_a_page(repo, monkeypatch):
    f = _chart(repo)
    cp.record(PAIR, f, ["results/toy_spy/subperiod_sharpe.csv"], "test")
    (repo / "results" / PAIR / "subperiod_sharpe.csv").write_text("episode,sharpe\nGFC,0.5\n")
    monkeypatch.setattr(g, "load_pool", lambda pair: {"nums": [], "dates": set(), "years": set(), "files": []})
    monkeypatch.setattr(g, "_headline_centres", lambda pair: [])
    monkeypatch.setattr(g, "spec_numbers", lambda pair: set())
    pages = {"strategy": [("chart_file", f.relative_to(repo).as_posix()), ("chart_file_text", "Sharpe 0.74")]}
    findings, stats = g.check_pair(PAIR, pages)
    assert any(x.startswith("STALE-CHART") for x in findings) and stats["charts_checked"] == 1


def _src(path, derived=()):
    return json.dumps({"src": [path], "derived": list(derived)})


def test_sourced_table_row_must_be_one_source_row(repo):
    rows, bad, der = g.table_source_rows(_src("results/toy_spy/subperiod_sharpe.csv"), PAIR)
    assert bad == [] and len(rows) == 2
    head = ["Episode", "Sharpe"]
    assert g.row_bound(g._template_cells(f"GFC{g.TABLE_SEP}0.74"), head, rows, der)
    # QA repro: a stale Sharpe near the truth ('Winner (Sharpe 0.45)') was accepted by the table pool 20/20
    assert not g.row_bound(g._template_cells(f"GFC{g.TABLE_SEP}0.71"), head, rows, der)
    # each number must come from the SAME row: GFC with COVID's value fails
    assert not g.row_bound(g._template_cells(f"GFC{g.TABLE_SEP}0.07"), head, rows, der)
    assert g.row_bound(g._template_cells(f"GFC{g.TABLE_SEP}74.0%"), head, rows, der)   # percent display


def test_stale_or_foreign_table_source_fails(repo):
    (repo / "results" / PAIR / "tournament_results_20261008.csv").write_text("a\n1\n")
    _r, bad, _d = g.table_source_rows(_src("results/toy_spy/tournament_results_20261008.csv"), PAIR)
    assert bad and "from run 20261008" in bad[0]
    (repo / "results" / "other_spy").mkdir()
    (repo / "results" / "other_spy" / "x.csv").write_text("a\n1\n")
    _r, bad, _d = g.table_source_rows(_src("results/other_spy/x.csv"), PAIR)
    assert bad and "not a file of results/toy_spy/" in bad[0]


def test_derived_columns_and_json_pointer_sources(repo):
    (repo / "results" / PAIR / "scope.json").write_text(json.dumps(
        {"axis": {"derivatives": [{"name": "z_60m", "definition": "60-month z-score", "window": 60}]}}))
    rows, bad, der = g.table_source_rows(_src("results/toy_spy/scope.json#/axis/derivatives", ("Rank",)), PAIR)
    assert bad == [] and der == {"Rank"}
    head = ["Rank", "Name", "Window"]
    assert g.row_bound(g._template_cells(f"7{g.TABLE_SEP}z_60m{g.TABLE_SEP}60"), head, rows, der)
    assert not g.row_bound(g._template_cells(f"7{g.TABLE_SEP}z_60m{g.TABLE_SEP}36"), head, rows, der)


def test_cell_containing_the_old_separator_is_one_cell(repo):
    # a definition 'P(stress_t | data up to t)' split into two cells under the old ' | ' separator
    (repo / "results" / PAIR / "d.json").write_text(json.dumps([{"d": "P(s | data to 2019-09-30)", "n": "x"}]))
    rows, _b, der = g.table_source_rows(_src("results/toy_spy/d.json"), PAIR)
    assert g.row_bound(g._template_cells(f"P(s | data to 2019-09-30){g.TABLE_SEP}x"), ["D", "N"], rows, der)


def test_table_source_marker_only_in_gate_mode(monkeypatch):
    import pandas as pd
    from components import provenance as P
    df = pd.DataFrame({"a": [1], "b": [2]})
    monkeypatch.delenv("AIG_PROVENANCE_GATE", raising=False)
    assert P.table_source(df, "results/x.csv") is df
    monkeypatch.setenv("AIG_PROVENANCE_GATE", "1")
    col = P.table_source(df, g.RESULTS / "x.csv").columns[0]
    assert col.startswith(P.T0) and col.endswith("a") and '"src"' in col


def test_pilots_record_every_chart_they_show():
    for pair in ("unrate_spy", "cc_delinquency_spy", "hy_ig_spy"):
        man = json.loads(cp.manifest_path(pair).read_text())
        assert man and all(e["inputs"] and e["results_tag"] for e in man.values()), pair
