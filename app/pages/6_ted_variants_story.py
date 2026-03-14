"""Finding 3 — The Story: TED Spread Variants as Equity Signals."""

import os, sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(page_title="TED Story | AIG-RLIC+", page_icon="📖", layout="wide", initial_sidebar_state="expanded")
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
render_sidebar()
render_glossary_sidebar()

st.title("The Story: Funding Stress and the Stock Market")
st.markdown("*Three ways to measure how much banks pay for money — and what each tells us about equities*")
st.markdown("---")

# --- Why 3 Variants ---
st.info(
    "**Why three variants?** The original indicator (SOFR minus 3M T-Bill) only exists since "
    "April 2018 — too short for robust econometrics. We investigated whether splicing with "
    "its predecessor (the classic LIBOR-based TED spread) could extend the history. The "
    "analysis revealed that SOFR and LIBOR measure fundamentally different risks (secured "
    "vs unsecured funding), making a direct splice invalid (overlap correlation: -0.04). "
    "Instead, the Fed Funds rate minus T-Bill (DFF-DTB3) proved a reliable proxy for the "
    "TED spread (overlap correlation: +0.63). We run all three variants to let the data decide."
)

NARRATIVE = """
### What Is the TED Spread?

The TED spread measures the gap between what banks pay to borrow from each other and the risk-free government rate. When banks trust each other, this gap is small (10-30 basis points). When fear rises — because of credit concerns, liquidity squeezes, or systemic risk — the gap widens dramatically.

The classic TED spread used LIBOR (the London Interbank Offered Rate) as the bank borrowing rate. After the LIBOR manipulation scandal, regulators replaced it with SOFR (the Secured Overnight Financing Rate) in 2018. But SOFR and LIBOR are not the same thing:

- **LIBOR** measured *unsecured* interbank lending — it included credit risk
- **SOFR** measures *secured* overnight repo — it's collateralized, so it reflects liquidity/collateral risk, not credit risk

This matters because a widening LIBOR-based TED spread signaled *credit distress*, while a widening SOFR-based spread signals *repo market stress* — related but distinct phenomena.

### The Three Variants We Test

**Variant A: SOFR - DTB3** (2018-2025, ~2,000 observations)
The "pure" modern version. Short history but captures the post-LIBOR regime including COVID, rate hikes, and recent markets.

**Variant B: DFF - DTB3** (1993-2025, ~8,600 observations)
The Fed Funds rate minus T-Bill. Available for the full period and correlates well with the classic TED spread (r=0.63). Captures the funding premium without the LIBOR discontinuity.

**Variant C: TEDRATE + adjusted DFF-TED splice** (1993-2025, ~8,600 observations)
Uses the official FRED TED spread (1993-2022) and extends it post-2022 using an affine-adjusted Fed Funds spread calibrated on the overlap period.
"""
render_narrative(NARRATIVE)

st.markdown("---")

# --- Side-by-side hero charts ---
st.markdown("### The Three Signals Over Time")

tabs = st.tabs(["A: SOFR-DTB3", "B: DFF-DTB3 (Fed Funds)", "C: Spliced TED"])

with tabs[0]:
    load_plotly_chart("sofr_ted_spy_hero", pair_id="sofr_ted_spy",
        caption="SOFR minus 3M T-Bill (2018-2025). Note the extreme spike in March 2020 (COVID repo stress).")

with tabs[1]:
    load_plotly_chart("dff_ted_spy_hero", pair_id="dff_ted_spy",
        caption="Fed Funds minus 3M T-Bill (1993-2025). Captures dot-com, GFC, and COVID funding stress episodes.")

with tabs[2]:
    load_plotly_chart("ted_spliced_spy_hero", pair_id="ted_spliced_spy",
        caption="Spliced TED spread: official TEDRATE (1993-2022) + adjusted DFF-TED (2022-2025).")

st.markdown("---")

# --- Regime Analysis ---
st.markdown("### Returns by Funding Stress Regime")

cols = st.columns(3)
for i, (pid, label) in enumerate([
    ("sofr_ted_spy", "A: SOFR-DTB3"),
    ("dff_ted_spy", "B: DFF-DTB3"),
    ("ted_spliced_spy", "C: Spliced"),
]):
    with cols[i]:
        st.markdown(f"**{label}**")
        load_plotly_chart(f"{pid}_regime_stats", pair_id=pid,
            caption="Sharpe by spread quartile. Q4 = highest stress.")

st.markdown("---")

# --- Transition to Evidence ---
render_transition(
    "All three variants show that high funding stress (Q4) is associated with lower equity "
    "Sharpe ratios — but the patterns differ. The evidence page digs into the econometric detail."
)
st.page_link("pages/6_ted_variants_evidence.py", label="Continue to The Evidence", icon="🔬")

st.markdown("---")
st.markdown('<div class="portal-footer">Generated with AIG-RLIC+ | 3 TED variants analyzed</div>', unsafe_allow_html=True)
