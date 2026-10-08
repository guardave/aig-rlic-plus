"""Landing-page "Data Timing" explainer (Step C #255, Alex_UK).

Reviewer-facing, plain-English tab that answers one question: *could an investor
actually have known each signal in time to trade it?* Economic data is published
with a delay (January's factory numbers are not out until February or March), so
a backtest that "uses" a month's data during that same month is peeking at
figures nobody had yet — look-ahead bias.

Single source of truth: every row is read from the **Lead-Axis Registry**
(`docs/schemas/lead_axis_registry.json`), the per-pair record mandated by the
Lead-Grid Frequency Standard (`docs/lead-grid-frequency-standard.md`). The
registry holds each pair's data source, publication lag, derived real-time floor
(Step 2, amended 2026-10-06), the floor-shifted lead grid, and whether its live
winner has been re-selected under that floored grid (``conformed``). The live
winner lead is read from ``results/<pair>/winner_summary.json`` so the status
stays correct after any re-run. Nothing about timing is hard-coded here.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS = _REPO_ROOT / "results"
_REGISTRY = _REPO_ROOT / "docs" / "schemas" / "lead_axis_registry.json"

_UNIT_SHORT = {"months": "mo", "quarters": "q", "trading_days": "d", "days": "d", "weeks": "w"}


def _load_registry() -> dict:
    try:
        return json.loads(_REGISTRY.read_text()).get("pairs", {})
    except Exception:
        return {}


def _winner_lead(pair_id: str):
    wp = _RESULTS / pair_id / "winner_summary.json"
    if not wp.exists():
        return None, None
    try:
        w = json.loads(wp.read_text())
        return w.get("lead_value", w.get("lead_months")), (w.get("lead_unit") or "").lower()
    except Exception:
        return None, None


def render_data_timing(key_prefix: str = "timing") -> None:
    """Render the plain-English data-timing / look-ahead explainer + table."""
    st.markdown("## Could an investor have known this in time?")
    st.markdown(
        "Economic data is **published with a delay**. January's factory numbers "
        "aren't released until February or March. So if a backtest *uses* a "
        "month's figure **during that same month**, it is peeking at a number "
        "nobody actually had yet — a mistake called **look-ahead bias**. The "
        "strategy would look better on paper than anything you could have truly "
        "traded."
    )
    st.markdown(
        "**How we prevent it.** Every signal is held back by a waiting period "
        "(we call it the **lead**) that is *at least* as long as the real "
        "publication delay — the **floor**. The floor is derived per source from "
        "its actual release calendar, and it **shifts the whole search window** "
        "rather than cutting the short end, so every pair still tests the same "
        "set of economic horizons (see the Lead-Grid Frequency Standard)."
    )
    with st.expander("A one-line example"):
        st.markdown(
            "The ISM factory survey for **March** comes out on the **1st business "
            "day of April**. So at the end of March you do *not* have it yet — "
            "the earliest you can act on March's reading is April. A rule that "
            "traded on March's survey *within March* would be cheating; the floor "
            "pushes the whole window out by one month so it reflects reality."
        )

    reg = _load_registry()
    buckets: dict[str, list[dict]] = {"fix": [], "pending": [], "safe": []}
    for pair_id, info in sorted(reg.items()):
        lead_val, lead_unit = _winner_lead(pair_id)
        floor = info.get("lead_floor")
        axis = info.get("lead_axis", "")
        ushort = _UNIT_SHORT.get(axis, axis)
        conformed = bool(info.get("conformed", False))
        try:
            below = lead_val is not None and float(lead_val) < float(floor)
        except (TypeError, ValueError):
            below = False
        if below:
            bucket = "fix"
        elif conformed:
            bucket = "safe"
        else:
            bucket = "pending"
        buckets[bucket].append({
            "Pair": pair_id,
            "Data source": info.get("signal_description", "—"),
            "When it's published": info.get("publication_lag", "—"),
            "Frequency": (info.get("signal_frequency", "") or "").capitalize(),
            "Min honest wait (floor)": f"L{floor} {ushort}" if floor is not None else "—",
            "Current rule's wait (lead)": (f"{lead_val} {_UNIT_SHORT.get(lead_unit, lead_unit)}"
                                           if lead_val is not None and lead_val != "" else "—"),
        })
    n_fix, n_pending, n_safe = len(buckets["fix"]), len(buckets["pending"]), len(buckets["safe"])

    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Safe (confirmed under the floor)", n_safe)
    c2.metric("🟡 To be re-confirmed", n_pending)
    c3.metric("⚠️ Look-ahead — being corrected", n_fix)

    st.warning(
        f"**Only {n_safe} pair(s) are confirmed.** Another **{n_pending}** "
        "currently *look* fine (their rule already waits past the floor), but "
        "their search has **not yet been re-run with the floor enforced and the "
        "window shifted** — so the winning rule could still change once it is. A "
        f"further **{n_fix}** use a signal **sooner than the data is published** "
        "(look-ahead) and are being corrected now. A rule is only truly safe once "
        "the search itself was never allowed to peek — re-confirming the 🟡 group "
        "is the #255 re-validation now under way on a review branch."
    )

    st.markdown("### Every indicator: when it's published, and the honest wait")
    st.caption(
        "Floor = the shortest lead at which the data has actually been published, "
        "derived per source from its release calendar and recorded in the "
        "Lead-Axis Registry. Lead = the delay the live winning rule uses (from "
        "winner_summary.json). Status reflects whether the winner has been "
        "re-selected under the floor-shifted grid."
    )

    if buckets["fix"]:
        st.markdown(
            f"#### ⚠️ Look-ahead — being corrected ({n_fix})  \n"
            "*The live rule trades sooner than the data is published. Being re-run now.*"
        )
        st.table(buckets["fix"])
    if buckets["pending"]:
        st.markdown(
            f"#### 🟡 To be re-confirmed ({n_pending})  \n"
            "*Current rule clears the floor, but the search must be re-run with the "
            "floor enforced and the window shifted to confirm the winner holds.*"
        )
        st.table(buckets["pending"])
    if buckets["safe"]:
        st.markdown(
            f"#### ✅ Safe — confirmed under the floor ({n_safe})  \n"
            "*The winner was selected with the floor in force, so it is genuinely executable.*"
        )
        st.table(buckets["safe"])
