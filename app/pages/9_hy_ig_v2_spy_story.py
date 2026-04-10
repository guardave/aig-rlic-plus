"""HY-IG v2 — The Story: Credit Spreads and Stocks."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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

# --- Page Header ---
st.title("Credit Spreads and Stocks: What the Bond Market Knows")
st.markdown(
    "*The bond market often sees trouble coming before the stock market does -- and the "
    "gap between risky and safe bond yields has been one of the most reliable early "
    "warning signals for equity declines over the past 25 years.*"
)
st.markdown("---")

# --- KPI Cards ---
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

st.markdown("---")

# --- Hero Chart ---
st.markdown("### 25 Years of Credit Spreads vs. S&P 500")
load_plotly_chart(
    "spread_history_annotated",
    fallback_text=(
        "Hero chart: HY-IG spread (inverted) vs SPY price (2000-2025) with "
        "NBER recession bands and event annotations."
    ),
    caption=(
        "Dual-axis view: HY-IG spread (left, inverted so widening = down) and "
        "SPY price (right). Vertical shaded bands mark NBER recessions. "
        "Notice how the spread widens (dips) before or during equity declines."
    ),
    pair_id="hy_ig_v2_spy",
)

st.markdown("---")

# --- Why Bond Investors Care ---
SECTION_STORY = """
### Why Should Stock Investors Care About Bonds?

Most people think of stocks and bonds as separate worlds. Stocks are for growth; bonds are for safety. But behind the scenes, the bond market is constantly making judgments about risk that stock investors often ignore -- until it is too late.

When companies borrow money by issuing bonds, investors demand higher interest rates from riskier companies. The difference between what a risky company pays and what a safe company pays is called a **credit spread** (the extra yield investors require to compensate for the possibility that the risky company might not pay them back). Think of it as the price of insurance against a company going bust -- when more companies look shaky, the insurance gets more expensive.

<!-- expander: What exactly is a credit spread? -->
A credit spread is measured in **basis points** (hundredths of a percentage point). If a risky company's bond yields 8% and a safe company's bond yields 4%, the credit spread is 400 basis points (4 percentage points). When investors become worried about the economy, they demand even higher yields from risky companies, causing spreads to **widen**. When confidence returns, spreads **tighten** (narrow).

The specific spread we study is the **HY-IG spread**: the difference between the yield on high-yield bonds (also called "junk bonds" -- bonds from companies with lower credit ratings, like BB or CCC) and investment-grade bonds (bonds from companies with higher credit ratings, like AA or A). Both yields are measured as option-adjusted spreads (OAS), meaning they account for embedded options like call provisions, providing a cleaner measure of pure credit risk.
<!-- /expander -->

### The Early Warning Signal

Our research examines whether this spread can serve as an early warning system for stock investors. The core finding, supported by over two decades of academic research, is that **the bond market tends to detect trouble before the stock market reacts.** There are several reasons for this:

- **Bond investors are wired for caution.** Unlike stock investors who can profit from unlimited upside, bond investors can only get their money back plus interest. This asymmetry makes them structurally more sensitive to the first signs of deterioration. When something smells off, bond investors raise the price of lending before stock investors lower the price they will pay for shares.
- **Banks trade on private information.** Banks that lend to companies have inside knowledge about their financial health. Research by Acharya & Johnson (2007) found evidence that this information leaks into credit markets -- through hedging activity in credit default swaps -- before it appears in stock prices.
- **The bond market is harder to fool.** Philippon (2009) showed that bond prices provide a cleaner signal of a company's fundamental value than stock prices. Stocks can be inflated by speculation and momentum; bond investors care only about getting their money back.

<!-- expander: The Merton Model -- Why stocks and bonds are mathematically linked -->
In 1974, economist Robert Merton proved something elegant: a company's stock and its debt are not separate instruments -- they are two different bets on the same underlying reality.

Imagine a company as a house with a mortgage. The homeowner (stockholder) profits if the house value rises above the mortgage. The bank (bondholder) gets paid as long as the house value stays above the mortgage. Now imagine the house value drops toward the mortgage amount. Two things happen at once: the homeowner's equity shrinks, and the bank starts worrying about getting paid back.

Merton showed that this analogy is mathematically precise. A company's stock is essentially a call option on its total asset value, with the strike price set at the value of its debts. When asset value drops toward the debt level, equity declines and credit spreads widen simultaneously. This is why credit spreads and stock prices tend to move in opposite directions during stress -- they are both responding to the same underlying reality, just viewed from different angles.

The practical implication: when you see credit spreads widening, it means the market is pricing in a higher probability that corporate asset values are falling toward their debt levels -- which is also bad news for equity holders.
<!-- /expander -->
"""

render_narrative(SECTION_STORY)

st.markdown("---")

# --- Historical Episodes ---
SECTION_HISTORY = """
### What History Shows

We analyzed 25 years of daily data (January 2000 through December 2025), covering four major market disruptions. Each episode reveals a different facet of how credit spreads interact with stock prices.

**The Dot-Com Bust (2001-2002).** Credit spreads began widening well before the recession officially started in March 2001. High-yield spreads climbed from roughly 500 to over 1,000 basis points as the telecom and technology sectors imploded, highlighted by the WorldCom bankruptcy in July 2002. The signal was genuine, though the lead time was shorter than in later episodes -- the dot-com bust was driven more by equity overvaluation than by credit deterioration, so the credit market was a contemporaneous confirmer rather than a leading indicator.

**The Global Financial Crisis (2007-2009).** This is the textbook example of credit leading equity. Credit spreads started widening in mid-2007, following the collapse of two Bear Stearns hedge funds that were exposed to subprime mortgages. The stock market did not peak until October 2007 -- giving attentive investors roughly five months of warning. By the time Lehman Brothers collapsed in September 2008, the HY-IG spread had already reached roughly 800 basis points. It eventually peaked above 2,000 basis points in December 2008. An investor who moved to cash when spreads crossed 2 standard deviations above their rolling mean would have avoided the majority of the drawdown -- though the timing of re-entry was equally critical.

**The COVID Crash (2020).** Credit spreads surged from about 350 to 1,100 basis points in just five weeks (late February to late March 2020). This time, credit and equity moved almost simultaneously -- the speed of the pandemic shock compressed the usual lead time to near zero. However, the signal still provided value: the sheer magnitude of spread widening confirmed that the sell-off was not a garden-variety correction but a genuine liquidity crisis. The Federal Reserve's unprecedented intervention -- including direct corporate bond purchases announced on March 23, 2020 -- truncated the stress episode faster than any previous crisis.

**The 2022 Rate Shock -- Where the Signal Struggled.** As the Federal Reserve raised interest rates at the fastest pace in four decades, credit spreads widened from about 300 to 500 basis points. The S&P 500 fell roughly 25%. But here is the honest caveat: the spread widening was modest compared to the equity decline. The mechanism was different -- this was not a credit crisis driven by deteriorating corporate balance sheets but a valuation repricing driven by higher discount rates. The HY-IG spread was reacting to the same force (rising rates) rather than providing an independent early warning. This episode illustrates a genuine limitation of the credit signal: it works best when stress originates in the credit cycle, and less well when the driver is pure monetary policy shock.

<!-- expander: The CCC-BB Quality Spread -- A deeper signal within the signal -->
Not all high-yield bonds are equally risky. Within the high-yield universe, there is a meaningful hierarchy: BB-rated bonds are the least risky high-yield issues (just one notch below investment grade), while CCC-rated bonds are at the edge of default.

The spread between CCC and BB yields -- what we call the **quality spread** -- provides an even more granular stress signal. When this quality spread widens, it means investors are specifically fleeing the weakest, most default-prone companies. This often happens before the broader HY-IG spread fully reflects the stress, because the weakest links break first.

During the GFC, the CCC-BB quality spread began widening months before the overall HY-IG spread reached crisis levels. During COVID, the quality spread spike was even more dramatic -- CCC-rated bonds briefly yielded over 20%, while BB bonds remained relatively contained. The quality spread is a "canary in the coal mine" within the credit market itself.

We include the CCC-BB quality spread as one of our tournament signals (S5) precisely because it captures a different dimension of credit stress than the broad HY-IG measure.
<!-- /expander -->
"""

render_narrative(SECTION_HISTORY)

st.markdown("---")

# --- Regime Chart ---
st.markdown("### Returns by Credit Regime")
load_plotly_chart(
    "returns_by_regime",
    fallback_text="SPY performance by credit spread regime (quartile analysis).",
    caption=(
        "Equity performance differs across credit spread regimes. "
        "When spreads are in their top quartile (highest stress), "
        "the credit-equity relationship strengthens significantly."
    ),
    pair_id="hy_ig_v2_spy",
)

st.markdown("---")

# --- Regime Dependence ---
SECTION_REGIMES = """
### It Is Not a Simple Relationship

If the story ended at "wider spreads = lower stocks," building a profitable trading strategy would be straightforward. But the relationship between credit spreads and stock returns is more nuanced than that, and understanding the nuances is essential for using the signal effectively.

The connection changes depending on the market **regime** (the overall state of financial conditions):

- **During calm periods** (when spreads are in their normal range of roughly 250-400 basis points), the predictive power of credit spreads for stock returns is modest. In fact, during these periods, stock prices tend to lead credit spreads -- equity markets set the pace, and credit markets follow. This makes intuitive sense: when things are going well, there is not much default risk to price, so the credit market mostly mirrors what equities are already saying.
- **During stress periods** (when spreads are in the top quartile of their historical range, roughly above 500 basis points), the relationship strengthens and may reverse direction -- credit markets appear to lead equity markets. This is consistent with the informed-trading and risk-appetite channels described above. It is also when the signal is most valuable: precisely when investors most need a warning.

This **regime dependence** is why simple trading rules based on credit spreads often fail. The signal is most powerful precisely when it is most needed -- during periods of financial stress -- but relatively quiet during the long stretches of calm in between. A strategy that responds to every twitch in credit spreads will generate excessive trading costs during calm periods with minimal benefit.

<!-- expander: What is a regime? -->
In financial economics, a "regime" refers to a distinct state of the market characterized by its own set of statistical properties -- its own average return, level of volatility, and pattern of correlations between assets. Think of weather: sunny days and stormy days are governed by different atmospheric dynamics, and a forecast that works in summer may be useless in winter.

The key insight from research by Hamilton (1989) and Guidolin & Timmermann (2007) is that financial markets do not behave the same way all the time. They switch between regimes -- sometimes abruptly. A model that assumes markets always behave the same way will miss the most important signals, because the relationship between credit and equity fundamentally changes when the market shifts from calm to crisis.

Our analysis uses Hidden Markov Models and Markov-switching regressions to statistically identify these regime changes, letting the data tell us when the market has shifted rather than imposing arbitrary thresholds.
<!-- /expander -->
"""

render_narrative(SECTION_REGIMES)

# --- Transition ---
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

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12 | "
    "~6,500 daily observations"
    "</div>",
    unsafe_allow_html=True,
)
