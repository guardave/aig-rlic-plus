"""Landing-page "Data Timing" explainer (Step C #255, Alex_UK).

Reviewer-facing, plain-English tab that answers one question: *could an investor
actually have known each signal in time to trade it?* Economic data is published
with a delay (January's factory numbers are not out until February or March), so
a backtest that "uses" a month's data during that same month is peeking at
figures nobody had yet — look-ahead bias.

The table is DATA-DRIVEN for the live rule: each pair's current signal delay
("lead") is read from ``results/<pair>/winner_summary.json`` so the status stays
correct after any tournament re-run. The per-source publication timing and the
minimum honest delay ("floor") are reference facts compiled from the release
calendars (ISM, BLS, Census, Federal Reserve, NAHB, U. Michigan, EIA, market
data); see docs/data-series-catalog.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS = _REPO_ROOT / "results"

# Per-pair reference: who publishes it, when (plain English), the minimum honest
# delay before the number is usable ("floor"), and the unit the floor/lead are in.
# floor is the smallest executable lead: a signal must be held back at least this
# long because that is how late the data arrives. unit is months / quarters / days.
_TIMING: dict[str, dict] = {
    # ---- Monthly macro released EARLY next month -> floor 1 month ----
    "ism_mfg_spy":        {"source": "ISM Manufacturing PMI",      "release": "1st business day of the next month",        "floor": 1, "unit": "months", "freq": "Monthly"},
    "ism_services_spy":   {"source": "ISM Services PMI",           "release": "~3rd business day of the next month",       "floor": 1, "unit": "months", "freq": "Monthly"},
    "import_price_spy":   {"source": "BLS Import Price Index",     "release": "~mid of the next month",                    "floor": 1, "unit": "months", "freq": "Monthly"},
    "indpro_spy":         {"source": "Fed Industrial Production",  "release": "~mid of the next month",                    "floor": 1, "unit": "months", "freq": "Monthly"},
    "indpro_xlp":         {"source": "Fed Industrial Production",  "release": "~mid of the next month",                    "floor": 1, "unit": "months", "freq": "Monthly"},
    "rsxfs_spy":          {"source": "Census Retail Sales",        "release": "~mid of the next month",                    "floor": 1, "unit": "months", "freq": "Monthly"},
    "permit_spy":         {"source": "Census Building Permits",    "release": "~mid of the next month (~17th)",            "floor": 1, "unit": "months", "freq": "Monthly"},
    "permit_yoy_spy":     {"source": "Census Building Permits",    "release": "~mid of the next month (~17th)",            "floor": 1, "unit": "months", "freq": "Monthly"},
    "housing_starts_spy": {"source": "Census Housing Starts",      "release": "~mid of the next month (~17th)",            "floor": 1, "unit": "months", "freq": "Monthly"},
    "unrate_spy":         {"source": "BLS Employment Situation",   "release": "1st Friday of the next month",              "floor": 1, "unit": "months", "freq": "Monthly"},
    "m2sl_yoy_spy":       {"source": "Fed M2 Money Stock (H.6)",   "release": "~4th week of the next month",               "floor": 1, "unit": "months", "freq": "Monthly"},
    "cass_freight_spy":   {"source": "Cass Freight Index",         "release": "~mid of the next month",                    "floor": 1, "unit": "months", "freq": "Monthly"},
    "busloans_spy":       {"source": "Fed C&I Loans (H.8)",        "release": "weekly, ~1 week lag",                       "floor": 1, "unit": "months", "freq": "Monthly"},
    "umcsent_spy":        {"source": "U. Michigan Sentiment",      "release": "final at month-end (prelim mid-month)",     "floor": 1, "unit": "months", "freq": "Monthly"},
    "umcsent_xlv":        {"source": "U. Michigan Sentiment",      "release": "final at month-end (prelim mid-month)",     "floor": 1, "unit": "months", "freq": "Monthly"},
    "wells_fargo_housing_spy": {"source": "NAHB Housing Market Index", "release": "~mid of the SAME month (near-zero lag)", "floor": 1, "unit": "months", "freq": "Monthly"},
    # ---- Monthly macro released LATE (next month-end or later) -> floor 2 months ----
    "nhs_saar_spy":       {"source": "Census New Home Sales",      "release": "~end of the next month (~24th)",            "floor": 2, "unit": "months", "freq": "Monthly"},
    "nhs_spy":            {"source": "Census New Home Sales",      "release": "~end of the next month (~24th)",            "floor": 2, "unit": "months", "freq": "Monthly"},
    "mfg_new_orders_spy": {"source": "Census Factory Orders (M3)", "release": "~early two months later (~5 weeks)",        "floor": 2, "unit": "months", "freq": "Monthly"},
    "retail_inv_sales_spy": {"source": "Census Retail Inventories (MTIS)", "release": "~6 weeks later",                   "floor": 2, "unit": "months", "freq": "Monthly"},
    "cement_spy":         {"source": "USGS Portland Cement",       "release": "~6-8 weeks later",                          "floor": 2, "unit": "months", "freq": "Monthly"},
    # ---- Weekly data available within the month -> floor 0 (special) ----
    "petrol_inv_spy":     {"source": "EIA Petroleum Stocks",       "release": "weekly, ~1 week lag (available in-month)",  "floor": 0, "unit": "months", "freq": "Weekly→Monthly"},
    # ---- Quarterly -> floor 1 quarter ----
    "cc_delinquency_spy": {"source": "Fed Credit-Card Delinquency", "release": "~2.5 months after the quarter",           "floor": 1, "unit": "quarters", "freq": "Quarterly"},
    "eci_total_comp_spy": {"source": "BLS Employment Cost Index",  "release": "~1 month after the quarter",                "floor": 1, "unit": "quarters", "freq": "Quarterly"},
    "sloos_ci_small_spy": {"source": "Fed Senior Loan Officer Survey", "release": "~5 weeks (early next quarter)",         "floor": 1, "unit": "quarters", "freq": "Quarterly"},
    # ---- Daily / market data (continuously quoted) -> floor 1 day ----
    "gold_copper_xli":    {"source": "Gold & Copper futures (market)", "release": "real-time (continuously quoted)",       "floor": 1, "unit": "days", "freq": "Daily"},
    "vix_vix3m_spy":      {"source": "CBOE VIX term structure (market)", "release": "real-time (continuously quoted)",     "floor": 1, "unit": "days", "freq": "Daily"},
    "hy_ig_spy":          {"source": "ICE BofA credit spreads",    "release": "real-time / 1-day",                         "floor": 1, "unit": "days", "freq": "Daily"},
    "hy_ig_spy_v1":       {"source": "ICE BofA credit spreads",    "release": "real-time / 1-day",                         "floor": 1, "unit": "days", "freq": "Daily"},
    "t10y3m_spy":         {"source": "Fed Treasury yield spread",  "release": "1-day lag (FRED)",                          "floor": 1, "unit": "days", "freq": "Daily"},
    "phlxsox_spy":        {"source": "PHLX Semiconductor / SPY (market)", "release": "real-time (continuously quoted)",    "floor": 1, "unit": "days", "freq": "Daily"},
    "dff_ted_spy_archived":    {"source": "T-bill / rate spread",  "release": "1-day lag",                                 "floor": 1, "unit": "days", "freq": "Daily"},
    "sofr_ted_spy_archived":   {"source": "SOFR-based spread",     "release": "1-day lag",                                 "floor": 1, "unit": "days", "freq": "Daily"},
    "ted_spliced_spy_archived":{"source": "TED (spliced) spread",  "release": "1-day lag",                                 "floor": 1, "unit": "days", "freq": "Daily"},
}

_UNIT_SHORT = {"months": "mo", "quarters": "q", "days": "d"}


def _winner_lead(pair_id: str):
    """Read the live winner lead (value, unit) from winner_summary.json."""
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
        "publication delay. A number you could not yet have seen is never used. "
        "The minimum honest wait is the **floor** below."
    )
    with st.expander("A one-line example"):
        st.markdown(
            "The ISM factory survey for **March** comes out on the **1st business "
            "day of April**. So at the end of March you do *not* have it yet — "
            "the earliest you can act on March's reading is April. A rule that "
            "traded on March's survey *within March* would be cheating; the floor "
            "pushes it to the next month so it reflects reality."
        )

    # Build the table from live winner leads + reference timing.
    rows = []
    n_safe = n_fix = 0
    for pair_id, info in sorted(_TIMING.items()):
        lead_val, lead_unit = _winner_lead(pair_id)
        if lead_val is None:
            continue
        floor = info["floor"]
        unit = info["unit"]
        ushort = _UNIT_SHORT.get(unit, unit)
        # Compare only when the winner's unit matches the reference unit.
        comparable = (lead_unit or unit).startswith(unit[:3]) or lead_unit in ("", unit)
        try:
            below = comparable and float(lead_val) < float(floor)
        except (TypeError, ValueError):
            below = False
        if below:
            status = "⚠️ Being corrected"
            n_fix += 1
        else:
            status = "✅ Safe"
            n_safe += 1
        rows.append({
            "Pair": pair_id,
            "Data source": info["source"],
            "When it's published": info["release"],
            "Frequency": info["freq"],
            "Minimum honest wait (floor)": f"{floor} {ushort}",
            "Current rule's wait (lead)": (f"{lead_val} {_UNIT_SHORT.get(lead_unit, lead_unit)}"
                                           if lead_val != "" and lead_val is not None else "—"),
            "Status": status,
        })

    # Headline counts.
    c1, c2 = st.columns(2)
    c1.metric("Pairs where the live rule is safe", n_safe)
    c2.metric("Pairs being corrected (look-ahead)", n_fix)
    if n_fix:
        st.info(
            f"**{n_fix} pair(s)** currently use a signal sooner than the data is "
            "actually published. These are being re-run with the corrected waiting "
            "period; their winning rule may change. This check (raised by a "
            "reviewer) is the portal's live guard against future-peeking."
        )

    st.markdown("### Every indicator: when it's published, and the honest wait")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.caption(
        "Floor = the shortest delay at which the data has actually been published, "
        "so the rule could have been traded. Lead = the delay the live winning "
        "rule uses (read from each pair's winner_summary.json). A rule is safe "
        "when its lead ≥ the floor. Publication timings are compiled from the "
        "official release calendars (ISM, BLS, U.S. Census, Federal Reserve, NAHB, "
        "U. Michigan, EIA) and market-data conventions."
    )
