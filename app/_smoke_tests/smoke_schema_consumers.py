"""Schema-consumer smoke test (APP-WS1 + APP-DIR1 coverage).

Exercises every `validate_or_die` call that the HY-IG v2 Strategy page
consumer components (`probability_engine_panel`, `position_adjustment_panel`,
`direction_check`) make against real artifacts under
`results/hy_ig_v2_spy/`. A regression on any of these = producer contract
violation and acceptance blocker per APP-SEV1 L1.

Runs with Streamlit stubbed out (no real runtime required).

Exit codes:
    0 — all consumer validations pass.
    1 — at least one consumer raised SchemaValidationError.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
import traceback
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[2]


class _MockSt:
    """Minimal Streamlit stub — swallows rendering calls."""

    def error(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def caption(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        pass


def run_smoke(pair_id: str) -> tuple[int, int, list[str]]:
    """Return (passes, failures, log_lines)."""
    sys.path.insert(0, str(_REPO_ROOT / "app"))

    # Install Streamlit mock BEFORE importing the target modules so their
    # top-level `import streamlit as st` receives the stub. We inject at the
    # `sys.modules` level for maximum compatibility.
    import types

    fake_st = _MockSt()
    fake_module = types.ModuleType("streamlit")
    for name in ("error", "warning", "caption", "info", "markdown"):
        setattr(fake_module, name, getattr(fake_st, name))
    sys.modules["streamlit"] = fake_module

    from components import schema_check  # noqa: E402
    from components.schema_check import SchemaValidationError  # noqa: E402
    from components import direction_check  # noqa: E402

    # Ensure the schema_check module uses our stubbed streamlit
    schema_check.st = fake_module
    direction_check.st = fake_module

    pair_dir = _REPO_ROOT / "results" / pair_id
    log: list[str] = []
    passes = 0
    failures = 0

    cases = [
        # (instance_path, schema_name, label)
        (pair_dir / "winner_summary.json", "winner_summary",
         "APP-WS1: winner_summary.json conforms to ECON-H5"),
        (pair_dir / "interpretation_metadata.json", "interpretation_metadata",
         "APP-WS1 sibling: interpretation_metadata.json conforms to DATA-D6"),
    ]

    for inst_path, schema_name, label in cases:
        try:
            data = schema_check.validate_or_die(inst_path, schema_name)
            if not isinstance(data, dict):
                failures += 1
                log.append(f"FAIL  {label}  returned non-dict: {type(data)}")
                continue
            passes += 1
            log.append(f"PASS  {label}  keys={len(data)}")
        except SchemaValidationError as exc:
            failures += 1
            log.append(f"FAIL  {label}  errors={exc.errors}")
        except Exception as exc:  # pragma: no cover
            failures += 1
            log.append(f"FAIL  {label}  unexpected: {exc!r}")
            log.append(traceback.format_exc())

    # APP-DIR1: direction triangulation
    try:
        report = direction_check.check_direction_agreement(pair_id)
        if report.get("schema_errors"):
            failures += 1
            log.append(
                f"FAIL  APP-DIR1: schema errors during triangulation: "
                f"{report['schema_errors']}"
            )
        elif report.get("agreement") is True:
            passes += 1
            log.append(
                f"PASS  APP-DIR1: 2-way agreement (Evan={report['evan']}, "
                f"Dana={report['dana']}, Ray=pending RES-17)"
            )
        else:
            failures += 1
            log.append(
                f"FAIL  APP-DIR1: no agreement (Evan={report['evan']}, "
                f"Dana={report['dana']}). notes={report.get('notes')}"
            )
    except Exception as exc:  # pragma: no cover
        failures += 1
        log.append(f"FAIL  APP-DIR1 triangulation raised: {exc!r}")
        log.append(traceback.format_exc())

    return passes, failures, log


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair-id", default="hy_ig_v2_spy")
    parser.add_argument(
        "--log-dir", default=os.path.dirname(os.path.abspath(__file__))
    )
    args = parser.parse_args()

    log: list[str] = []
    log.append(
        f"# Schema-consumer smoke test  pair_id={args.pair_id}  "
        f"timestamp={_dt.datetime.now().isoformat(timespec='seconds')}"
    )
    passes, failures, call_log = run_smoke(args.pair_id)
    log.extend(call_log)
    log.append("")
    log.append(f"# RESULT  passes={passes}  failures={failures}")

    date_tag = _dt.datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(
        args.log_dir, f"schema_consumers_{args.pair_id}_{date_tag}.log"
    )
    with open(log_path, "w") as f:
        f.write("\n".join(log) + "\n")

    print("\n".join(log))
    print(f"\nLog written: {log_path}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
