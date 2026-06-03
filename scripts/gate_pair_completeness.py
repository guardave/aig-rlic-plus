"""GATE-CMP1 — Producer-side completeness gate for pair pipelines.

Thin helper that pair pipelines (and any artifact-emitting script) can call
at the end of their run to assert the pair meets every requirement in
docs/dashboard-page-standard.md *before* the work is considered done.

This is the Tier-1 forcing function from BL-META-CMP / GH #7: catch
completeness drift at producer time, not at cloud render time.

Two usage patterns:

  1. Pipeline tail call (recommended; deterministic, runs on every regen)
        from scripts.gate_pair_completeness import assert_pair_complete
        assert_pair_complete("indpro_xlp")   # raises CompletenessError on FAIL

  2. CLI for manual invocation or pre-commit hooks
        python -m scripts.gate_pair_completeness indpro_xlp
        python -m scripts.gate_pair_completeness indpro_xlp --allow-partial \
          --partial-reason "winner_summary fields TBD — see BL-LEGACY-WINNER-SUMMARY-SHAPE"

The --allow-partial flag exists for the LEGITIMATE exception class only
(e.g. BL-PERMIT-CHARTS-EXCEPTION external work in flight). It downgrades
FAIL to WARN and exits 0; the reason string is required and printed so
the deviation is auditable. Do not use it to silence real drift.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


class CompletenessError(RuntimeError):
    """Raised when a pair fails GATE-CMP1 completeness validation."""


def _load_validator():
    """Load validate_pair_completeness as a module (it's a script, not a package).

    Registers the module in sys.modules BEFORE exec_module so that
    @dataclass decorators (which inspect sys.modules[cls.__module__] under
    Python 3.14+) resolve correctly.
    """
    name = "validate_pair_completeness"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name,
        _REPO_ROOT / "scripts" / "validate_pair_completeness.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def assert_pair_complete(
    pair_id: str,
    *,
    allow_partial: bool = False,
    partial_reason: str | None = None,
    verbose: bool = True,
) -> None:
    """Run the completeness validator on a pair; raise if it fails.

    Parameters
    ----------
    pair_id : str
        The pair_id (results/<pair_id>/ must exist).
    allow_partial : bool
        Downgrade FAIL to WARN. Use ONLY for documented exception carve-outs
        (e.g. BL-PERMIT-CHARTS-EXCEPTION). Requires partial_reason.
    partial_reason : str | None
        Human-readable explanation of why partial is acceptable. Printed and
        required when allow_partial=True.
    verbose : bool
        Print the text report when the pair fails (or always when verbose=True
        AND the pair has any non-PASS checks). Default: True.

    Raises
    ------
    CompletenessError
        When the pair fails AND allow_partial is False.
    ValueError
        When allow_partial=True but partial_reason is missing.
    """
    if allow_partial and not partial_reason:
        raise ValueError("allow_partial=True requires partial_reason")

    mod = _load_validator()
    report = mod.validate_pair(pair_id)

    if report.passed:
        if verbose:
            print(f"GATE-CMP1 PASS: {pair_id}")
        return

    text = mod.render_text(report, use_color=False)
    if allow_partial:
        print(
            f"GATE-CMP1 PARTIAL ({pair_id}): exception accepted — {partial_reason}",
            file=sys.stderr,
        )
        print(text, file=sys.stderr)
        return

    if verbose:
        print(text, file=sys.stderr)
    raise CompletenessError(
        f"GATE-CMP1 FAIL: {pair_id} does not meet docs/dashboard-page-standard.md. "
        f"Fix the FAIL checks above or, if a documented exception applies "
        f"(e.g. BL-PERMIT-CHARTS-EXCEPTION), invoke with --allow-partial and "
        f"--partial-reason '<BL-id and explanation>'."
    )


def _cli() -> int:
    p = argparse.ArgumentParser(
        description=(
            "GATE-CMP1 — Producer-side pair completeness gate. "
            "Wraps scripts/validate_pair_completeness.py with raise/exception "
            "semantics suitable for pipeline tail calls and pre-commit hooks."
        )
    )
    p.add_argument("pair_id", help="pair_id to validate (results/<pair_id>/ must exist)")
    p.add_argument(
        "--allow-partial",
        action="store_true",
        help="Downgrade FAIL to WARN; requires --partial-reason. Use only for documented exceptions.",
    )
    p.add_argument(
        "--partial-reason",
        metavar="STRING",
        default=None,
        help="Human-readable justification for --allow-partial (e.g. 'BL-PERMIT-CHARTS-EXCEPTION external work in flight').",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress PASS line on success; FAIL output still goes to stderr.",
    )
    args = p.parse_args()

    try:
        assert_pair_complete(
            args.pair_id,
            allow_partial=args.allow_partial,
            partial_reason=args.partial_reason,
            verbose=not args.quiet,
        )
    except ValueError as e:
        print(f"GATE-CMP1 invocation error: {e}", file=sys.stderr)
        return 2
    except CompletenessError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
