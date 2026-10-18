"""Codex V52-1 repro (run as a script by test_gate_v5_chart_table_provenance): a data read through an aliased
reader BEFORE chart_provenance is imported must still be recorded."""
import sys
from pathlib import Path

reader = Path.read_text
REPO = Path(__file__).resolve().parents[2]
hidden = reader(REPO / sys.argv[1])
sys.path.insert(0, str(REPO / "scripts"))
import chart_provenance  # noqa: E402

print("BOOTED" if getattr(sys, "_aig_cp_booted", False) else "NOT-BOOTED")
print("RECORDED" if sys.argv[1] in chart_provenance._READS else "MISSED")
