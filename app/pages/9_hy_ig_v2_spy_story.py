"""HY-IG v2 -- The Story: Credit Spreads and Stocks.

Wave 2B restructure (2026-04-19):
  - Headline-first restructure per Ray's narrative (RES-11, closes SL-1).
  - Investor-impact bullets appended to each Headline Finding (RES-9).
  - Canonical historical-episode zoom charts (Dot-Com, GFC, COVID) rendered
    via the META-ZI loader under "What History Shows" (RES-8, SL-4, SL-5).
  - Status vocabulary: glossary-backed legend expander (§3.12, RES-10).
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(
    page_title="HY-IG v2 Story | AIG-RLIC+",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_sidebar()
render_glossary_sidebar()

PAIR_ID = "hy_ig_v2_spy"
_REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Breadcrumb navigation (N10, META-PWQ)
# ---------------------------------------------------------------------------
render_breadcrumb("Story", PAIR_ID)

# ---------------------------------------------------------------------------
# Plain English expander (N8 -- Ray's narrative addition)
# ---------------------------------------------------------------------------
with st.expander("Plain English"):
    st.markdown(
        "When companies borrow money, lenders charge safer companies lower rates "
        "and risky companies higher rates. The gap between those rates is called "
        "the credit spread. When it's small, business is going well. When it jumps "
        "up, it means investors are scared about the future. This research asks: "
        "does watching that gap help predict what the stock market will do? The "
        "answer turns out to be yes -- sometimes. You can use it to lose less money "
        "in crashes."
    )

# ---------------------------------------------------------------------------
# Headline-first block (RES-11, closes SL-1) — H2 headline + KPI bullets
# pulled to the top; Where-This-Fits and page-pack orientation follow.
# ---------------------------------------------------------------------------
st.markdown(
    "## Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month "
    "early-warning signal for equity drawdowns"
)

st.markdown(
    "**Key metrics (out-of-sample 2018-2025):**\n\n"
    "- **Sharpe ratio: 1.27** (vs 0.90 buy-and-hold) -- ~40% more return per unit of risk\n"
    "- **Annualized return: 11.3%** (vs ~10% buy-and-hold)\n"
    "- **Max drawdown: -10.2%** (vs -34% buy-and-hold) -- roughly one-third of the pain"
)

st.markdown("---")

with st.container(border=True):
    st.markdown("### Where This Fits in the Portal")
    st.markdown(
        "This is **one indicator-target analysis** -- we ask whether credit spreads "
        "can help time equity exposure. The AIG-RLIC+ portal catalogues many such "
        "pair-wise studies; this one examines whether the HY-IG credit spread "
        "carries useful information about future SPY returns."
    )
    st.markdown(
        "**How to read the rest of this page pack.** You'll read the **Story** first "
        "(why the signal works in plain English), then the **Evidence** (the "
        "statistical proofs, one method block at a time), then the **Strategy** "
        "(the actual trading rule and how you would apply it yourself), then the "
        "**Methods** (technical appendix for readers who want to reproduce or "
        "criticise the work). Each page stands alone; readers short on time can "
        "skim the Story and Strategy pages and skip the rest."
    )

# ---------------------------------------------------------------------------
# One-Sentence Thesis
# ---------------------------------------------------------------------------
st.markdown("### One-Sentence Thesis")
st.markdown(
    "*The bond market often sees trouble coming before the stock market does -- and "
    "the gap between risky and safe bond yields has been one of the most reliable "
    "early warning signals for equity declines over the past 25 years.*"
)

st.markdown("---")

# ---------------------------------------------------------------------------
# KPI Cards  (Metric Interpretation Rule)
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Lead Time (GFC)", "~5 months", delta="Credit led equity")
with col2:
    st.metric("GFC Spread Peak", "2,000+ bps", delta="6x increase")
with col3:
    st.metric("Predicted Drawdowns", "3 of 4", delta="Major episodes")
with col4:
    st.metric("Strongest During", "Stress", delta="Top quartile")
with col5:
    st.metric("OOS Test Period", "8 years", delta="2018-2025")

st.caption(
    "Why this matters: the HY-IG credit spread -- the extra yield investors demand "
    "to hold risky corporate bonds instead of safe ones -- began widening five "
    "months before the 2008 stock market peak, correctly flagged 3 of the last 4 "
    "major drawdowns, and is most predictive during the stress periods when "
    "investors need it most. The 8-year out-of-sample window includes COVID, the "
    "2022 rate shock, and the 2023-25 recovery, so these results are not the "
    "product of a single favourable episode."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Headline Findings with investor-impact bullets (RES-9, closes S18-12)
# ---------------------------------------------------------------------------
st.markdown("### Headline Findings")

st.markdown(
    "1. **Credit led equity by ~5 months before the 2008 crash** -- the HY-IG credit "
    "spread (the extra yield that investors demand to hold risky corporate bonds "
    "instead of safe ones -- essentially the price of insurance against companies "
    "going bust) began widening in June 2007, while stocks did not peak until "
    "October 2007.\n"
    "   - **What this means for investors:** an investor watching the spread "
    "crossing its stress band in mid-2007 would have had nearly half a year to "
    "trim equity exposure before the October peak and the -57% drawdown that "
    "followed.\n"
    "2. **Spreads widened from 300 to 2,000+ basis points (3% to 20%+) during the "
    "GFC** -- a basis point is 1/100th of a percentage point, so 2,000 basis points "
    "means risky companies were paying 20 full percentage points more than safe "
    "ones. That 6x increase reflected a market that believed a wave of corporate "
    "defaults was coming.\n"
    "   - **What this means for investors:** the sheer scale of the widening was a "
    "loud, unmistakable risk-off signal -- investors following the rule would have "
    "rotated the majority of equity exposure to cash well before the Lehman-week crash.\n"
    "3. **Credit signals predicted 3 of the last 4 major equity drawdowns** -- a "
    "drawdown is a peak-to-trough decline in value. The dot-com bust (2001), the "
    "Global Financial Crisis (2008), and the COVID crash (2020) were all preceded "
    "or accompanied by dramatic spread widening. The 2022 rate shock is the honest "
    "exception -- more on that below.\n"
    "   - **What this means for investors:** the signal is a reliable "
    "drawdown-avoidance tool for credit-driven sell-offs, but it should be paired "
    "with a separate interest-rate or valuation signal (e.g. the yield-curve pair "
    "in the portal) to cover the type of bear market that credit alone cannot see.\n"
    "4. **The relationship is strongest during stress** -- when spreads are in their "
    "top quartile (top 25% of historical values), the connection between credit "
    "conditions and subsequent stock returns is significantly stronger than during "
    "calm periods.\n"
    "   - **What this means for investors:** the signal earns its keep when you "
    "need it most -- during market crises -- and stays quiet the rest of the time, "
    "so following it does not impose a return drag during normal calm years.\n"
    "5. **Out-of-sample testing covers 8 years (2018-2025)** -- including the 2018 "
    "volatility spike, COVID crash, 2022 rate shock, and 2023-25 recovery. "
    "\"Out-of-sample\" means this period was hidden from the models during training, "
    "so it provides a genuine real-world test of whether the signal holds up on data "
    "it has never seen.\n"
    "   - **What this means for investors:** the 1.27 Sharpe and -10.2% max "
    "drawdown were achieved on data the model had never seen -- this is evidence of "
    "a durable edge, not curve-fitting, and supports allocating real capital to the "
    "rule rather than treating it as a historical curiosity."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Hero Chart
# ---------------------------------------------------------------------------
st.markdown("### 25 Years of Credit Spreads vs. S&P 500")
load_plotly_chart(
    "hero",
    fallback_text=(
        "Hero chart: HY-IG spread vs SPY price (2000-2025) with NBER "
        "recession bands and event annotations."
    ),
    caption=(
        "How to read it: dual-panel view — HY-IG spread on top (bps, where "
        "100 bps = 1%) and SPY price below, sharing a common time axis. "
        "Vertical shaded bands mark NBER recessions. Notice how the spread "
        "widens before or during equity declines."
    ),
    pair_id=PAIR_ID,
)

st.markdown(
    "**Scope note.** This page pack focuses on the HY-IG credit spread in isolation. "
    "Credit stress rarely travels alone -- it typically co-occurs with VIX spikes "
    "and yield-curve inversions -- but each of those indicators has its own "
    "dynamics and its own separate analysis in the portal. See the separate "
    "analyses on **VIX x SPY** and **Yield Curve x SPY** for deep dives on those "
    "related signals; here we keep the lens on credit."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Why Bond Investors Care -- with investor-impact bullets (RES-9)
# ---------------------------------------------------------------------------
SECTION_STORY = """
### Why Should Stock Investors Care About Bonds?

Most people think of stocks and bonds as separate worlds. Stocks are for growth; bonds are for safety. But behind the scenes, the bond market is constantly making judgments about risk that stock investors often ignore -- until it is too late.

When companies borrow money by issuing bonds, investors demand higher interest rates from riskier companies. The difference between what a risky company pays and what a safe company pays is called a **credit spread** -- the extra yield investors require to compensate for the possibility that the risky company might not pay them back. Think of it as the price of insurance against a company going bust: when more companies look shaky, the insurance gets more expensive.

<!-- expander: What exactly is a credit spread, and how is it measured? -->
A credit spread is measured in **basis points** (hundredths of a percentage point). If a risky company's bond yields 8% and a safe company's bond yields 4%, the credit spread is 400 basis points (4 percentage points). When investors become worried about the economy, they demand even higher yields from risky companies, causing spreads to **widen**. When confidence returns, spreads **tighten** (narrow).

The specific spread we study is the **HY-IG spread**: the difference between the yield on high-yield bonds (also called "junk bonds" -- bonds from companies with lower credit ratings, like BB or CCC) and investment-grade bonds (bonds from companies with higher credit ratings, like AA or A). Both yields are measured as **option-adjusted spreads (OAS)** -- a technique that strips out the effect of special bond features like early repayment clauses, leaving a cleaner measure of pure credit risk.
<!-- /expander -->

### The Early Warning Signal

Our research examines whether this spread can serve as an early warning system for stock investors. The core finding, supported by over two decades of academic research, is that **the bond market tends to detect trouble before the stock market reacts.** There are several reasons for this:

- **Bond investors are wired for caution.** Unlike stock investors who can profit from unlimited upside, bond investors can only get their money back plus interest. This asymmetry makes them structurally more sensitive to the first signs of deterioration. When something smells off, bond investors raise the price of lending before stock investors lower the price they will pay for shares. *What this means for investors:* credit spreads widen earlier than equity prices drop -- investors who watch spreads get a head start of days to months over investors who watch only equity prices.
- **Banks trade on private information.** Banks that lend to companies have inside knowledge about their financial health. Research by Acharya & Johnson (2007) found evidence that this information leaks into credit markets -- through hedging activity in credit default swaps -- before it appears in stock prices. *What this means for investors:* a spread-widening signal is effectively picking up informed-trader conviction that equity investors have not yet seen -- acting on it before the news becomes public is what turns the signal into a risk-management edge.
- **The bond market is harder to fool.** Philippon (2009) showed that bond prices provide a cleaner signal of a company's fundamental value than stock prices. Stocks can be inflated by speculation and momentum; bond investors care only about getting their money back. *What this means for investors:* when spreads widen while stocks are still making highs, the likely explanation is equity complacency -- the disciplined move is to trim equity exposure toward the bond market's view, not to dismiss the divergence.

The relationship is **counter-cyclical** -- meaning the spread moves opposite to stocks. When spreads widen (risky bonds get more expensive to issue), stocks tend to fall. When spreads tighten (risk appetite returns), stocks tend to rise.

<!-- expander: Why are stocks and bonds mathematically connected? (The Merton Model) -->
In 1974, economist Robert Merton proved something elegant: a company's stock and its debt are not separate instruments -- they are two different bets on the same underlying reality.

Imagine a company as a house with a mortgage. The homeowner (stockholder) profits if the house value rises above the mortgage. The bank (bondholder) gets paid as long as the house value stays above the mortgage. Now imagine the house value drops toward the mortgage amount. Two things happen at once: the homeowner's equity shrinks, and the bank starts worrying about getting paid back.

Merton showed that this analogy is mathematically precise. A company's stock is essentially a call option on its total asset value, with the strike price set at the value of its debts. When asset value drops toward the debt level, equity declines and credit spreads widen simultaneously. This is why credit spreads and stock prices tend to move in opposite directions during stress -- they are both responding to the same underlying reality, just viewed from different angles.

The practical implication: when you see credit spreads widening, it means the market is pricing in a higher probability that corporate asset values are falling toward their debt levels -- which is also bad news for equity holders.
<!-- /expander -->
"""

render_narrative(SECTION_STORY)

st.markdown("---")

# ---------------------------------------------------------------------------
# What History Shows — with META-ZI zoom charts (RES-8, SL-4, SL-5)
# ---------------------------------------------------------------------------
st.markdown(
    "### What History Shows\n\n"
    "We analyzed 25 years of daily data (January 2000 through December 2025), "
    "covering four major market disruptions. Each episode reveals a different "
    "facet of how credit spreads interact with stock prices."
)

st.markdown("#### The Dot-Com Bust (2001-2002)")
st.markdown(
    "Credit spreads began widening well before the recession officially started "
    "in March 2001. High-yield spreads climbed from roughly 500 to over 1,000 "
    "basis points (5% to 10%+) as the telecom and technology sectors imploded, "
    "highlighted by the WorldCom bankruptcy in July 2002. The signal was "
    "genuine, though the lead time was shorter than in later episodes -- the "
    "dot-com bust was driven more by equity overvaluation than by credit "
    "deterioration, so the credit market was a contemporaneous confirmer rather "
    "than a leading indicator."
)
load_plotly_chart(
    "history_zoom_dotcom",
    fallback_text=(
        "Dot-Com zoom chart pending (canonical path: "
        "output/_comparison/history_zoom_dotcom.json)."
    ),
    caption=(
        "What this shows: HY-IG OAS spread, 1998-2003. Event markers: "
        "Dot-Com peak (Mar 2000), 400 bps crossing (Aug 2000), NBER "
        "recession start (Mar 2001), WorldCom (Jul 2002). Vertical shaded "
        "bands mark NBER recessions."
    ),
    pair_id=PAIR_ID,
)

st.markdown("#### The Global Financial Crisis (2007-2009)")
st.markdown(
    "This is the textbook example of credit leading equity. Credit spreads "
    "started widening in mid-2007, following the collapse of two Bear Stearns "
    "hedge funds that were exposed to subprime mortgages. The stock market did "
    "not peak until October 2007 -- giving attentive investors roughly five "
    "months of warning. By the time Lehman Brothers collapsed in September "
    "2008, the HY-IG spread had already reached roughly 800 basis points. It "
    "eventually peaked above 2,000 basis points in December 2008. An investor "
    "who moved to cash when spreads crossed 2 standard deviations above their "
    "rolling mean would have avoided the majority of the drawdown -- though "
    "the timing of re-entry was equally critical."
)
load_plotly_chart(
    "history_zoom_gfc",
    fallback_text=(
        "GFC zoom chart pending (canonical path: "
        "output/_comparison/history_zoom_gfc.json)."
    ),
    caption=(
        "What this shows: HY-IG OAS spread, 2005-2010. Event markers: "
        "BNP Paribas freeze (Aug 2007), Bear Stearns (Mar 2008), Lehman "
        "(Sep 2008), NBER recession end (Jun 2009). Vertical shaded bands "
        "mark NBER recessions."
    ),
    pair_id=PAIR_ID,
)

st.markdown("#### The COVID Crash (2020)")
st.markdown(
    "Credit spreads surged from about 350 to 1,100 basis points (3.5% to 11%) "
    "in just five weeks (late February to late March 2020). This time, credit "
    "and equity moved almost simultaneously -- the speed of the pandemic shock "
    "compressed the usual lead time to near zero. However, the signal still "
    "provided value: the sheer magnitude of spread widening confirmed that the "
    "sell-off was not a garden-variety correction but a genuine liquidity "
    "crisis. The Federal Reserve's unprecedented intervention -- including "
    "direct corporate bond purchases announced on March 23, 2020 -- truncated "
    "the stress episode faster than any previous crisis."
)
load_plotly_chart(
    "history_zoom_covid",
    fallback_text=(
        "COVID zoom chart pending (canonical path: "
        "output/_comparison/history_zoom_covid.json)."
    ),
    caption=(
        "What this shows: HY-IG OAS spread, 2019-2022. Event markers: "
        "pandemic declared (Mar 2020), spread peak ~1,100 bps (Mar 2020), "
        "Fed credit facilities (Mar 23 2020). Vertical shaded bands mark "
        "NBER recessions."
    ),
    pair_id=PAIR_ID,
)

st.markdown("#### The 2022 Rate Shock -- Where the Signal Struggled")
st.markdown(
    "As the Federal Reserve raised interest rates at the fastest pace in four "
    "decades, credit spreads widened from about 300 to 500 basis points "
    "(3% to 5%). The S&P 500 fell roughly 25%. But here is the honest caveat: "
    "the spread widening was modest compared to the equity decline. The "
    "mechanism was different -- this was not a credit crisis driven by "
    "deteriorating corporate balance sheets but a valuation repricing driven "
    "by higher discount rates. The HY-IG spread was reacting to the same "
    "force (rising rates) rather than providing an independent early warning. "
    "This episode illustrates a genuine limitation of the credit signal: it "
    "works best when stress originates in the credit cycle, and less well "
    "when the driver is pure monetary policy shock."
)

with st.expander("Deeper dive"):
    st.markdown(
        "*Is there a deeper signal within the credit market itself? "
        "(The CCC-BB quality spread.)*\n\n"
        "Not all high-yield bonds are equally risky. Within the high-yield "
        "universe, there is a meaningful hierarchy: BB-rated bonds are the "
        "least risky high-yield issues (just one notch below investment "
        "grade), while CCC-rated bonds are at the edge of default.\n\n"
        "The spread between CCC and BB yields -- what we call the **quality "
        "spread** -- provides an even more granular stress signal. When this "
        "quality spread widens, it means investors are specifically fleeing "
        "the weakest, most default-prone companies. This often happens before "
        "the broader HY-IG spread fully reflects the stress, because the "
        "weakest links break first.\n\n"
        "During the GFC, the CCC-BB quality spread began widening months "
        "before the overall HY-IG spread reached crisis levels. During COVID, "
        "the quality spread spike was even more dramatic -- CCC-rated bonds "
        "briefly yielded over 20%, while BB bonds remained relatively "
        "contained. The quality spread is a \"canary in the coal mine\" "
        "within the credit market itself.\n\n"
        "We include the CCC-BB quality spread as one of our tournament "
        "signals (S5) precisely because it captures a different dimension of "
        "credit stress than the broad HY-IG measure."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Regime Chart
# ---------------------------------------------------------------------------
st.markdown("### Returns by Credit Regime")
load_plotly_chart(
    "returns_by_regime",
    fallback_text="SPY performance by credit spread regime (quartile analysis).",
    caption=(
        "Why this matters: equity performance differs across credit spread "
        "regimes. When spreads are in their top quartile (highest stress), "
        "the credit-equity relationship strengthens significantly."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Regime Dependence
# ---------------------------------------------------------------------------
SECTION_REGIMES = """
### It Is Not a Simple Relationship

If the story ended at "wider spreads = lower stocks," building a profitable trading strategy would be straightforward. But the relationship between credit spreads and stock returns is more nuanced, and understanding these nuances is essential for using the signal effectively.

The connection changes depending on the market **regime** -- a regime is a distinct state of financial conditions, like "calm weather" versus "storm," where each state has its own patterns of returns, volatility, and correlations between assets:

- **During calm periods** (when spreads are in their normal range of roughly 250-400 basis points), the predictive power of credit spreads for stock returns is modest. In fact, during these periods, stock prices tend to lead credit spreads -- equity markets set the pace, and credit markets follow. This makes intuitive sense: when things are going well, there is not much default risk to price, so the credit market mostly mirrors what equities are already saying.
- **During stress periods** (when spreads are in the top quartile of their historical range, roughly above 500 basis points), the relationship strengthens and may reverse direction -- credit markets appear to lead equity markets. This is consistent with the informed-trading and risk-appetite channels described above. It is also when the signal is most valuable: precisely when investors most need a warning.
"""

render_narrative(SECTION_REGIMES)

st.markdown(
    "**What this means:** A simple \"sell stocks when spreads widen\" rule will not work "
    "because the signal is noisy during calm periods. An effective strategy needs to "
    "distinguish between calm and stressed markets and only act on the credit signal "
    "when it is in a state where it actually carries predictive power."
)

st.markdown("")

with st.expander("Why we chose this method"):
    st.markdown(
        "*How do we define market regimes without arbitrary cutoffs?*\n\n"
        'In financial economics, a "regime" refers to a distinct state of the market '
        "characterized by its own set of statistical properties -- its own average return, "
        "level of volatility, and pattern of correlations between assets. Think of weather: "
        "sunny days and stormy days are governed by different atmospheric dynamics, and a "
        "forecast that works in summer may be useless in winter.\n\n"
        "The key insight from research by Hamilton (1989) and Guidolin & Timmermann (2007) "
        "is that financial markets do not behave the same way all the time. They switch "
        "between regimes -- sometimes abruptly. A model that assumes markets always behave "
        "the same way will miss the most important signals, because the relationship between "
        "credit and equity fundamentally changes when the market shifts from calm to crisis.\n\n"
        "Our analysis uses **Hidden Markov Models** (statistical models that infer which of "
        "several unobservable \"hidden\" states the market is in at any given time, based on "
        "patterns in the data) and **Markov-switching regressions** (regressions where the "
        "coefficients change depending on which regime is active). These let the data tell us "
        "when the market has shifted rather than imposing arbitrary thresholds like "
        "\"spreads above 500 bps = stress.\""
    )

# ---------------------------------------------------------------------------
# Status vocabulary legend expander (§3.12) — pulled from portal_glossary.json
# ---------------------------------------------------------------------------
_glossary_path = _REPO_ROOT / "docs" / "portal_glossary.json"
if _glossary_path.exists():
    with open(_glossary_path) as _gf:
        _glossary = json.load(_gf)
    _status = _glossary.get("status_labels", {})
    with st.expander("What do status labels like *Available*, *Pending*, *Validated* mean?"):
        for label, definition in _status.items():
            if label.startswith("_"):
                continue
            st.markdown(f"- **{label}** — {definition}")
        st.caption(
            "What this shows: the canonical source for these labels is "
            "`docs/portal_glossary.json` (Rule RES-10)."
        )

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
st.markdown("---")
render_transition(
    "History suggests a real connection between credit spreads and stocks -- but anecdotes "
    "are not evidence. We subjected 25 years of daily data to a battery of statistical "
    "tests to separate genuine predictive power from coincidence and survivorship bias."
)

st.page_link(
    "pages/9_hy_ig_v2_spy_evidence.py",
    label="Continue to The Evidence",
    icon="🔬",
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | Data: 2000-01 to 2025-12 | "
    "~6,500 daily observations."
)
