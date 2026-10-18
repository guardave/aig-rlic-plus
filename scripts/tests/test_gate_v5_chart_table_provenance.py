"""Number-provenance gate v5, QA L2v4 #1: chart files are checked by provenance record, sourced tables row by row
against their source file. Every QA repro is a must-FAIL case."""
import json
import os
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
    # V51-2: a Sharpe is not a ratio-kind column, so it may not be shown x 100 as a percent
    assert not g.row_bound(g._template_cells(f"GFC{g.TABLE_SEP}74.0%"), head, rows, der)


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
    assert bad == [] and der["derived"] == {"Rank": None}
    head = ["Name", "Window"]
    assert g.row_bound(g._template_cells(f"z_60m{g.TABLE_SEP}60"), head, rows, der)
    assert not g.row_bound(g._template_cells(f"z_60m{g.TABLE_SEP}36"), head, rows, der)
    # Codex V52-3: a derived numeric cell with no checker-owned rule ('None = skipped') now fails
    assert not g.row_bound(g._template_cells(f"7{g.TABLE_SEP}z_60m{g.TABLE_SEP}60"), ["Rank", *head], rows, der)


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


def test_absent_input_is_reported_with_a_rebuild_path_not_as_stale(repo):
    # QA pilot-visual M6: a gitignored input missing from a fresh clone read as 16 STALE-CHART
    f = _chart(repo)
    cp.record(PAIR, f, ["results/toy_spy/subperiod_sharpe.csv"], "test")
    (repo / "results" / PAIR / "subperiod_sharpe.csv").unlink()
    r = cp.verify(PAIR, f.relative_to(repo).as_posix())
    assert "not present in this checkout" in r and "pair_pipeline_toy_spy.py" in r and "stale" not in r


def test_pilot_chart_inputs_are_all_tracked():
    import subprocess
    root = Path(__file__).resolve().parents[2]
    for pair in ("unrate_spy", "cc_delinquency_spy", "hy_ig_spy"):
        ins = {i for e in json.loads(cp.manifest_path(pair).read_text()).values() for i in e["inputs"]}
        untracked = [i for i in ins if subprocess.run(["git", "ls-files", "--error-unmatch", i], cwd=root,
                                                       capture_output=True).returncode]
        assert not untracked, (pair, untracked)              # a fresh clone can verify every record


def test_reads_of_other_pairs_results_are_not_inputs(repo):
    (repo / "results" / "other_spy").mkdir()
    (repo / "results" / "other_spy" / "x.csv").write_text("a\n1\n")
    with open(repo / "results" / "other_spy" / "x.csv") as fh:     # a producer looping over pairs read this
        fh.read()
    e = cp.record(PAIR, _chart(repo), ["results/toy_spy/subperiod_sharpe.csv"], "test")
    assert not [i for i in e["inputs"] if i.startswith("results/other_spy/")]


def _probe(*pre):
    import subprocess
    root = Path(__file__).resolve().parents[2]
    data = next(p for p in subprocess.run(["git", "ls-files", "data"], cwd=root, capture_output=True, text=True,
                                          env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
                                          ).stdout.split() if p.endswith(".csv"))
    out = subprocess.run([sys.executable, *pre, str(root / "scripts" / "tests" / "_cp_alias_probe.py"), data],
                         capture_output=True, text=True, cwd=root, timeout=120)
    assert out.returncode == 0, out.stderr
    return out.stdout.split()


def test_a_read_before_the_recorder_import_is_still_recorded():
    # Codex V52-1: an aliased reader (reader = Path.read_text) called before `import chart_provenance` escaped the
    # static import-order test; the script now re-executes through the boot module, which installs the hook first
    assert _probe() == ["BOOTED", "RECORDED"]


def test_non_script_processes_are_not_re_executed():
    import subprocess
    root = Path(__file__).resolve().parents[2]
    out = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, 'scripts'); import chart_provenance;"
                          " print(getattr(sys, '_aig_cp_booted', False))"], capture_output=True, text=True, cwd=root)
    assert out.stdout.strip() == "False", out.stderr


def test_missing_declared_input_is_rejected(repo):
    with pytest.raises(ValueError, match="does not exist"):
        cp.record(PAIR, _chart(repo), ["results/toy_spy/subperiod_sharpe.csv", "data/missing.csv"], "test")


def test_every_chart_a_pilot_shows_verifies():
    # Codex V51-1: the old test only checked that manifests were non-empty; this runs verify() on every record
    root = Path(__file__).resolve().parents[2]
    for pair in ("unrate_spy", "cc_delinquency_spy", "hy_ig_spy"):
        man = json.loads(cp.manifest_path(pair).read_text())
        bad = {name: cp.verify(pair, f"output/charts/{pair}/plotly/{name}.json") for name in man}
        assert not {k: v for k, v in bad.items() if v}, (pair, {k: v for k, v in bad.items() if v})


def test_percent_display_needs_a_ratio_kind_column():
    # Codex V51-2 repro: '4348.0%' was accepted against a stored 43.48 (any decimal could be shown x 100)
    assert not g._cell_ok("4348.0%", [(43.48, False)], set())
    assert g._cell_ok("43.5%", [(43.48, False)], set())                   # a stored percent shown as stored
    assert g._cell_ok("6.6%", [(0.066, True)], set())                      # a ratio-kind column shown x 100
    assert not g._cell_ok("6.6", [(0.066, True)], set())                   # x 100 only with a percent sign


def test_derived_rank_is_checked_against_the_source_rank_column(repo):
    # Codex V51-6 repro: row_bound(['987'], ['Rank'], ..., {'Rank'}) passed a wrong hand-computed rank
    (repo / "results" / PAIR / "t.csv").write_text(
        "key,is_sharpe,is_rank,oos_sharpe,decoy\na,0.9,1,0.62,987\nb,0.8,2,0.67,987\n")
    rows, _b, _d = g.table_source_rows(_src("results/toy_spy/t.csv"), PAIR)
    head = ["Rank", "Key", "OOS Sharpe"]
    der = {"Rank": "is_rank"}
    assert g.row_bound(g._template_cells(f"2{g.TABLE_SEP}b{g.TABLE_SEP}0.67"), head, rows, der)
    assert not g.row_bound(g._template_cells(f"987{g.TABLE_SEP}b{g.TABLE_SEP}0.67"), head, rows, der)
    assert not g.row_bound(g._template_cells(f"1{g.TABLE_SEP}b{g.TABLE_SEP}0.67"), head, rows, der)
    # Codex V52-3: a decoy column or None no longer authorises a derived rank
    cells = g._template_cells(f"987{g.TABLE_SEP}b{g.TABLE_SEP}0.67")
    assert not g.row_bound(cells, head, rows, {"Rank": "decoy"})
    assert not g.row_bound(cells, head, rows, {"Rank": None})
    # the checker recomputes the rank from is_sharpe: a file whose rank column disagrees fails
    (repo / "results" / PAIR / "t2.csv").write_text("key,is_sharpe,is_rank,oos_sharpe\na,0.9,2,0.62\nb,0.8,1,0.67\n")
    rows2, _b, _d = g.table_source_rows(_src("results/toy_spy/t2.csv"), PAIR)
    assert not g.row_bound(g._template_cells(f"1{g.TABLE_SEP}b{g.TABLE_SEP}0.67"), head, rows2, der)


def test_percent_permission_is_bound_to_the_displayed_column():
    # Codex V52-2 repro: '50.0%' under 'Sharpe' was authorised by the coincident ratio-kind oos_ann_return
    rows = [[("episode", "GFC"), ("sharpe", 0.5), ("oos_ann_return", 0.5)]]
    assert not g.row_bound(["GFC", "50.0%"], ["Episode", "Sharpe"], rows, {})
    assert g.row_bound(["GFC", "50.0%"], ["Episode", "OOS Return"], rows, {"columns": {"OOS Return": "oos_ann_return"}})
    assert g.row_bound(["GFC", "0.50"], ["Episode", "Sharpe"], rows, {})
    # a numeric cell in a column bound to no source column fails
    assert not g.row_bound(["GFC", "0.50"], ["Episode", "Score"], rows, {})
