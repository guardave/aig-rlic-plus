"""UMCSENT × XLV pair configuration (Rule APP-PT1).

Wave 10I.A narrative port (Ray): prose fields authored from legacy
app/pages/10_umcsent_xlv_*.py (pre-migration, commit 24e2f16~1),
cross-checked against results/umcsent_xlv/winner_summary.json.

APP-TL1 note: `results/umcsent_xlv/winner_trades_broker_style.csv` is
present (shipped Wave 10H.2, commit 2c11046). `TRADE_LOG_EXAMPLE_MD`
is authored directly from that file.

Pair ID: umcsent_xlv  (richest hand-written pair — 1,563 legacy lines)
Winner (winner_summary.json, authoritative): UMCSENT YoY / zero-crossing /
P1_long_cash / 6-month lead — OOS Sharpe 1.02, OOS return +11.93%,
Max DD -10.87%, 81 trades, win rate 37%.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Consumer Sentiment and the Healthcare Sector"
    PAGE_SUBTITLE = (
        "Does University of Michigan consumer sentiment predict returns in "
        "the defensive Health Care Select Sector SPDR Fund (XLV)?"
    )

    HEADLINE_H2 = (
        "## University of Michigan Consumer Sentiment as a directional signal "
        "for Health Care Select Sector SPDR Fund (XLV)"
    )

    PLAIN_ENGLISH = (
        "The University of Michigan Consumer Sentiment survey asks roughly "
        "900-1,000 respondents under its newer web-interview process how "
        "confident they feel about the economy. This page "
        "asks whether those survey results — a number published monthly "
        "and free to download — can help time exposure to the Health Care "
        "Select Sector SPDR Fund (XLV). Health care is a defensive sector: "
        "people visit doctors whether the economy is booming or not. The "
        "working hypothesis is straightforward: higher or improving "
        "consumer sentiment should coincide with better XLV performance."
    )

    WHERE_THIS_FITS = ""

    ONE_SENTENCE_THESIS = (
        "*When consumer sentiment trends upward — measured by a year-over-"
        "year gain, with a 6-month lead — Health Care Select Sector SPDR "
        "Fund (XLV) has historically performed better, supporting the "
        "hypothesis that broad consumer confidence can lift even defensive "
        "sectors during stronger market regimes.*"
    )

    KPI_CAPTION = (
        "The winning rule uses University of Michigan Consumer Sentiment "
        "(UMCSENT) year-over-year change with a 6-month "
        "lead. When the 12-month change is positive (sentiment trending up), "
        "the strategy holds XLV; when negative, it moves to cash. The "
        "6-month lead suggests sentiment anticipates sector rotation well "
        "in advance rather than coinciding with it. Out-of-sample (OOS) "
        "Sharpe is 1.02 vs "
        "0.72 for buy-and-hold XLV — ~42% more return per unit of risk — "
        "with max drawdown reduced from -15.6% to -10.9%."
    )

    HERO_TITLE = "Consumer Sentiment vs. Healthcare Sector (XLV)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "University of Michigan Consumer Sentiment year-over-year percent "
        "change (red line, left axis) vs XLV "
        "adjusted price (blue line, right axis). Shaded bands mark periods "
        "when sentiment was falling year-over-year. Notice that XLV often "
        "continues rising even during modest sentiment declines — which is "
        "the surface pattern of the direction surprise explored below."
    )

    REGIME_TITLE = "What History Shows: XLV Returns by Consumer-Sentiment Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "Annualised XLV Sharpe ratio by quartile of University of Michigan "
        "Consumer Sentiment year-over-year change. Quartile 1 = lowest "
        "(most negative) year-over-year change; Quartile 4 = highest "
        "(most positive). The non-monotonic pattern (Quartile 2 ~1.09 > "
        "Quartile 4 ~0.93 > Quartile 3 ~0.56 > Quartile 1 ~0.23) confirms "
        "the procyclical direction — "
        "falling sentiment coincides with the worst XLV regime — while "
        "suggesting that the peak of optimism is itself a late-cycle "
        "warning sign."
    )

    NARRATIVE_SECTION_1 = (
        "### Why Consumer Sentiment and Health Care?\n\n"
        "The University of Michigan Consumer Sentiment Index has been "
        "published monthly since 1978. The current survey reaches roughly "
        "900-1,000 respondents under the newer web-interview process. "
        "Participants are asked about their financial situation, their outlook for the "
        "broader economy in the next 12 months, and their views on "
        "conditions five years out. The index is one of the most watched "
        "leading indicators in the world — central banks, equity analysts, "
        "and economists all track it because it has historically turned "
        "before consumer spending does.\n\n"
        "### The Defensive-Healthcare Hypothesis\n\n"
        "The standard economic story about health care stocks is that they "
        "are **defensive**: people consume health care regardless of the "
        "cycle, so health care companies generate stable cash flows in "
        "both good times and bad. The theory predicts that when consumers "
        "feel confident, they rotate money *out* of defensive sectors "
        "like health care and *into* cyclical growth sectors (technology, "
        "industrials, discretionary). When confidence falls, money flows "
        "back into defensives.\n\n"
        "That defensive-rotation story is plausible, but it is not the "
        "hypothesis supported by this pair. Here the tested hypothesis is "
        "that higher or improving sentiment goes with better XLV "
        "performance. Higher sentiment is often associated with stronger "
        "risk appetite and a lower required risk premium, but that is a "
        "market-regime relationship rather than a mechanical identity. The "
        "lower risk premium can lift broad equity valuations, including "
        "health care, even though health care remains less cyclical than "
        "technology, industrials, or consumer discretionary stocks.\n\n"
        "**The data supports the higher-sentiment hypothesis.** Periods of "
        "rising consumer sentiment (positive year-over-year change) have "
        "been associated with XLV *outperformance*. The most likely "
        "explanations are:\n\n"
        "1. **Bull markets lift everything.** In sustained bull markets, "
        "investor optimism drives all sectors higher. The defensive "
        "characteristic of health care reduces its beta relative to the "
        "S&P 500 ETF Trust (SPY), "
        "but XLV still participates in the upside when broad sentiment "
        "is strong.\n"
        "2. **Healthcare spending grows during booms.** When consumers "
        "feel wealthy, they actually spend *more* on elective care: "
        "voluntary procedures, premium medications, wellness. This "
        "revenue impact is captured in XLV earnings during high-sentiment "
        "periods.\n"
        "3. **Sentiment captures risk appetite broadly.** High consumer "
        "confidence is often associated with lower required risk premiums "
        "across risky assets — including health care equities — although "
        "the relationship can vary by market regime."
    )

    NARRATIVE_SECTION_2 = (
        "### Key Findings\n\n"
        "Two facts about this pair deserve special emphasis:\n\n"
        "**The year-over-year change, not the level, is the key signal.** "
        "Raw sentiment levels are non-stationary and reflect long secular "
        "trends. The year-over-year change captures whether sentiment is "
        "improving or deteriorating relative to a year ago — which is what "
        "correlates with forward XLV returns. A sentiment reading of 70 "
        "(below long-run average of ~85) still generates a bullish signal "
        "if it has risen from 65 a year ago.\n\n"
        "**A 6-month lead is optimal.** The rule works best with a "
        "6-month lag before acting on the signal — meaning current "
        "sentiment changes predict XLV performance half a year later, not "
        "immediately. This multi-month delay is typical of macro sentiment "
        "indicators feeding through to sector returns, and it means the "
        "rule is not a short-term timing tool.\n\n"
        "The main limits are sample length (XLV starts 1998-12, so the "
        "full sample is 325 monthly observations and the out-of-sample "
        "window is only about 6 years) and the sector-specific nature of "
        "the target (Affordable Care Act policy, drug-pricing policy, "
        "COVID, and demographics all affect "
        "XLV independently of consumer sentiment)."
    )

    SCOPE_NOTE = (
        "*Scope discipline (ECON-SD).* Only University of Michigan Consumer "
        "Sentiment and XLV derivatives are in-scope primary signals. "
        "The unemployment rate, 10-year Treasury yield, and CBOE Volatility "
        "Index (VIX) are used only as regression controls, not as trading "
        "signals. S&P 500 ETF Trust (SPY) appears as a benchmark comparison, "
        "not as a tradable target "
        "for this pair."
    )

    TRANSITION_TEXT = (
        "The direction surprise is the central finding of this analysis. "
        "The Evidence page shows the full battery of statistical tests "
        "that confirm this is a robust result, not an artefact of data "
        "selection or time period."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dot_com",
            "title": "Dot-Com Bust (2000–2002)",
            "narrative": "Consumer sentiment deteriorated sharply through 2001 as the economy contracted and unemployment rose. XLV, as a defensive health care holding, held up relatively well. But the year-over-year sentiment signal turned negative — and the strategy correctly moved to cash. This is a long-lead success case where the signal anticipated XLV's underperformance relative to its defensive reputation.",
            "caption": "2001 sentiment decline: University of Michigan Consumer Sentiment year-over-year change turned negative; XLV held up but signal correctly reduced exposure",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": "Sentiment collapsed through 2008-2009 as unemployment surged and household wealth evaporated. XLV declined meaningfully, though less than S&P 500 ETF Trust (SPY). The University of Michigan Consumer Sentiment year-over-year signal turned sharply negative in late 2007, moving the strategy to cash ahead of most of the health care drawdown. A clean long-lead case: sentiment fell before the equity trough, and the long-cash strategy avoided the worst of the decline.",
            "caption": "Global Financial Crisis: University of Michigan Consumer Sentiment year-over-year signal moved to cash late 2007; XLV declined -30% peak-to-trough but strategy avoided bulk of it",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": "Sentiment plunged to near-record lows in April 2020. XLV experienced a moderate drawdown before recovering sharply — health care stocks benefited from vaccine and treatment demand. The University of Michigan Consumer Sentiment signal went negative, and the 6-month lead meant the strategy was positioned cautiously. However, XLV's rapid recovery created a signal lag problem: the strategy sat in cash during some of the health care upswing. A mixed coincident case.",
            "caption": "COVID: University of Michigan Consumer Sentiment collapsed April 2020; XLV recovered fast on health care demand — 6-month lead caused cash lag into recovery",
        },
        {
            "slug": "rates_2022",
            "title": "Fed Hiking Cycle (2022)",
            "narrative": "Consumer sentiment hit multi-decade lows in June 2022 (University of Michigan index at 50) driven by inflation and rising rates. XLV outperformed S&P 500 ETF Trust (SPY) during this period — a partial vindication of the defensive thesis. But the University of Michigan Consumer Sentiment year-over-year signal had already turned negative, keeping the strategy in cash. This is a failure case: the signal was bearish, but XLV actually held up, so the strategy missed the relative outperformance.",
            "caption": "June 2022 sentiment hit 50-year low; XLV outperformed S&P 500 ETF Trust (SPY) but the University of Michigan Consumer Sentiment signal was bearish — missed defensive rally",
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 4 method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Pearson correlations measure the linear relationship between two "
        "variables on a scale from −1 to +1. We test six University of "
        "Michigan Consumer Sentiment-derived signals (level, year-over-year "
        "change, month-over-month change, z-score, 3-month moving average, "
        "direction, deviation) against XLV forward returns at 1-month, "
        "3-month, 6-month and 12-month horizons. "
        "Spearman rank correlations are run in parallel as a robustness "
        "check against outliers."
    ),
    question=(
        "Do any University of Michigan Consumer Sentiment-derived signals show a statistically meaningful "
        "linear relationship with future XLV returns — and in which "
        "direction?"
    ),
    how_to_read=(
        "Rows: University of Michigan Consumer Sentiment signals. Columns: "
        "forward XLV return horizons. "
        "Blue = positive correlation (higher sentiment → higher XLV); "
        "Red = negative. Stars: * p<0.05, ** p<0.01."
    ),
    chart_name="correlations",
    chart_caption=(
        "Pearson correlation heatmap between University of Michigan Consumer "
        "Sentiment signals and XLV "
        "forward returns. Blue cells indicate procyclical relationships "
        "(high sentiment → XLV outperforms). Stars mark statistical "
        "significance."
    ),
    observation=(
        "The 3-month moving-average signal shows the strongest negative "
        "correlation with 12-month forward XLV returns (r = -0.198, "
        "p = 0.0004) — a long-horizon mean-reversion effect. The year-over-year "
        "change — the winning tournament signal — shows a modest positive "
        "correlation with shorter horizons, consistent with the procyclical "
        "observed direction. Sixteen of 48 correlations clear the 5% "
        "significance threshold, confirming the relationship is not a "
        "statistical artefact."
    ),
    interpretation=(
        "Different University of Michigan Consumer Sentiment transforms "
        "capture different aspects of the sentiment cycle. The raw level "
        "and 3-month moving average capture the *state* of sentiment "
        "(high vs. low), while the year-over-year change captures "
        "*momentum* (improving vs. deteriorating). The tournament winner "
        "(year-over-year change) is a momentum signal that picks up improving/"
        "worsening trends, not absolute states. The negative 3-month moving "
        "average correlation at 12-month horizons may reflect mean-reversion — sustained "
        "high sentiment is followed by normalisation."
    ),
    key_message=(
        "University of Michigan Consumer Sentiment momentum "
        "(year-over-year change) shows a procyclical correlation "
        "with XLV forward returns: improving sentiment is associated with "
        "XLV outperformance, contradicting the defensive-rotation "
        "hypothesis."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "Granger causality asks whether past University of Michigan Consumer Sentiment values improve "
        "forecasts of future XLV returns beyond what XLV's own recent "
        "history already provides. We test both directions (consumer "
        "sentiment to XLV and XLV to consumer sentiment) at lags 1-6 months "
        "using F-tests on augmented vector autoregression regressions with "
        "HC3 robust standard errors."
    ),
    question=(
        "Does consumer sentiment carry information about future health care "
        "equity returns that is not already priced into XLV itself?"
    ),
    how_to_read=(
        "The CCF chart below serves as the combined visual for lead-lag "
        "structure. Bars below the 95% confidence bands at negative lags "
        "(consumer sentiment leads) indicate statistically significant predictive "
        "content from sentiment to health care returns."
    ),
    chart_name="ccf",
    chart_caption=(
        "Cross-correlation function between University of Michigan Consumer "
        "Sentiment year-over-year change and XLV "
        "monthly return at lags −12 to +12 months. Red bars are "
        "statistically significant at 95% confidence."
    ),
    observation=(
        "The CCF shows that the strongest predictive lags are at negative "
        "lags (consumer sentiment leading XLV), consistent with sentiment as a "
        "leading indicator. Several lags between -3 and -8 months clear "
        "the 95% significance threshold. Formal Granger tests confirm: "
        "University of Michigan Consumer Sentiment year-over-year change "
        "Granger-causes XLV returns at lags 3-6 (p < 0.05) but not at "
        "lags 1-2. The reverse direction (XLV to consumer sentiment) is "
        "not significant at any lag tested."
    ),
    interpretation=(
        "One-directional Granger causality is unusual in financial data, "
        "where contemporaneous correlations and feedback loops are common. "
        "The one-directional result here reflects the nature of consumer "
        "surveys: households form opinions based on their actual economic "
        "experience (jobs, wages, prices), not from watching XLV price "
        "ticks. This independence means consumer sentiment carries genuine new "
        "information about future sector dynamics that is not yet in "
        "health care stock prices at the time of the survey."
    ),
    key_message=(
        "Sentiment leads health care equity at 3-6 months — a directionally "
        "clean, one-way Granger causality that supports using consumer sentiment as "
        "an actionable leading indicator for XLV timing."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Analysis (Quartile Descriptive Statistics)",
    method_theory=(
        "We sort all monthly observations into four quartiles based on "
        "UMCSENT year-over-year change and compute full return statistics "
        "for XLV in each quartile. This is the simplest possible regime "
        "test: does XLV performance differ systematically across sentiment "
        "regimes, without any model-imposed structure?"
    ),
    question=(
        "If we had done nothing more sophisticated than 'hold XLV when "
        "sentiment is rising year-over-year and move to cash when it is "
        "falling', how would that strategy have performed historically?"
    ),
    how_to_read=(
        "Left panel: annualised Sharpe ratio in each University of Michigan "
        "Consumer Sentiment year-over-year quartile. Right panel: annualised "
        "return. Quartile 1 = lowest (most negative) year-over-year "
        "change; Quartile 4 = highest (most positive). Look for a monotonic "
        "pattern to confirm the regime-return relationship."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "Annualised XLV Sharpe ratio and return by quartile of University "
        "of Michigan Consumer Sentiment year-over-year change. Quartile 1 "
        "= most negative sentiment trend; Quartile 4 = most positive. "
        "The gradient reveals the procyclical "
        "relationship."
    ),
    observation=(
        "The pattern is directional but non-monotonic. Quartile 1 (lowest "
        "year-over-year change): Sharpe 0.23. Quartile 2: 1.09. Quartile "
        "3: 0.56. Quartile 4 (highest year-over-year change): 0.93. The "
        "highest Sharpe is in Quartile 2, not Quartile 4 — suggesting that *moderate* "
        "positive sentiment momentum is the strongest XLV regime, not "
        "extreme optimism. Quartile 1 (most negative) is the worst regime."
    ),
    interpretation=(
        "The Quartile 2 > Quartile 4 pattern is consistent with a well-documented "
        "phenomenon: extreme optimism can itself become a warning signal. "
        "When sentiment is at its most positive extreme (Quartile 4), it may be "
        "capturing late-cycle euphoria that historically precedes "
        "corrections. The highest predictive content is in the **direction "
        "of change** — positive but not extreme — which is exactly what "
        "the tournament-winning year-over-year zero-crossing rule captures."
    ),
    key_message=(
        "Falling consumer sentiment (Quartile 1) is the worst regime for XLV "
        "returns. Rising sentiment (Quartiles 2-4) is better, with the strongest "
        "signal being the direction of change, not the absolute level."
    ),
)


SIGNAL_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Signal Distribution Analysis",
    method_theory=(
        "We examine how XLV 3-month forward returns are distributed when "
        "the University of Michigan Consumer Sentiment direction signal is "
        "rising (+1) vs. falling (-1). "
        "This reveals whether the sentiment effect is concentrated in the "
        "tails (extreme outcomes) or is a shift in the median return — "
        "information that guides strategy design."
    ),
    question=(
        "When sentiment is rising, does the entire XLV return distribution "
        "shift upward, or is the effect concentrated in avoiding the left "
        "tail (worst outcomes) or boosting the right tail (best outcomes)?"
    ),
    how_to_read=(
        "Left panel: histogram of the University of Michigan Consumer "
        "Sentiment year-over-year-change distribution "
        "(how often sentiment improves vs. worsens). Right panel: box "
        "plots of XLV 3-month forward returns split by whether sentiment "
        "is rising or falling. Points beyond the whiskers are extreme "
        "observations under the box-plot rule; they are not treated as "
        "data errors unless a separate data-quality check identifies them "
        "as invalid."
    ),
    chart_name="signal_dist",
    chart_caption=(
        "Left: distribution of University of Michigan Consumer Sentiment "
        "year-over-year changes (roughly symmetric, "
        "centred near zero). Right: XLV 3-month forward returns when "
        "sentiment is rising vs. falling. The box plots reveal whether "
        "the effect is median-shifting or tail-driven."
    ),
    observation=(
        "The year-over-year change distribution is roughly symmetric with slightly "
        "more months in negative territory. The return box plots show "
        "that XLV forward returns are slightly higher when sentiment is "
        "rising (median ~+3% vs +2% over 3 months), but the distributions "
        "substantially overlap — confirming a weak average effect rather "
        "than a sharp categorical separator. The left tail is notably "
        "worse during falling-sentiment periods, which is where the risk-"
        "management value of the strategy resides."
    ),
    interpretation=(
        "A signal does not need to be right every month to produce a "
        "positive Sharpe. The strategy's win rate is ~37% — lower than "
        "buy-and-hold — but the losses avoided during falling-sentiment "
        "periods are larger in magnitude than the gains missed during "
        "those months, producing the positive Sharpe differential. The "
        "rule is a tail-risk manager, not a directional forecaster."
    ),
    key_message=(
        "The sentiment signal is a risk-management tool: it primarily "
        "avoids the worst XLV drawdown months rather than generating "
        "dramatically higher returns during positive months — consistent "
        "with health care's defensive role in a diversified portfolio."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "We subjected 27 years of monthly data to four complementary "
        "statistical methods. Each is designed to test a different aspect "
        "of the sentiment-health care relationship. All four converge on "
        "the same direction: procyclical, not countercyclical — the "
        "direction surprise flagged on the Story page."
    ),
    "plain_english": (
        "Four methods all point to the same direction: when sentiment "
        "trends upward year-over-year, XLV tends to do better over the "
        "following months. The surprise — and the honest finding — is "
        "that this is the *procyclical* direction, not the defensive/"
        "countercyclical pattern that standard economic theory predicts."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality"],
    "level2": [REGIME_BLOCK, SIGNAL_DIST_BLOCK],
    "level2_labels": ["Regime Analysis", "Signal Distribution"],
    "tournament_intro": (
        "With the econometric case established, we swept a 5-dimensional "
        "tournament over 7 signal transforms, 7 threshold methods, 3 "
        "strategy families, and 5 lead times — 1,305 raw combinations "
        "pruned to 1,196 valid. The top 5 strategies were validated with "
        "bootstrap significance testing and transaction-cost sensitivity. "
        "The winning specification is on the Strategy page."
    ),
    "transition": (
        "Four statistical methods converge on the same conclusion: "
        "consumer sentiment momentum (year-over-year change) is a procyclical "
        "leading indicator for XLV health care returns. Now: what does "
        "the winning strategy actually do, and how has it performed?"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating Consumer Sentiment Signals into XLV Positioning"
    PAGE_SUBTITLE = (
        "We tested over 1,300 strategy combinations to find the most robust "
        "way to time Health Care Select Sector SPDR Fund (XLV) exposure "
        "using consumer sentiment."
    )

    PLAIN_ENGLISH = (
        "We tested over 1,300 combinations of rules for using consumer "
        "sentiment to time XLV exposure. The winner is simple: hold XLV "
        "when consumer sentiment has risen year-over-year (measured six "
        "months ago), and move to cash when it has fallen. This rule "
        "out-performed buy-and-hold on a risk-adjusted basis over 6 years "
        "of out-of-sample data."
    )

    SIGNAL_RULE_MD = (
        "**Tournament winner:** Signal University of Michigan Consumer "
        "Sentiment (UMCSENT) year-over-year change / Threshold "
        "zero-crossing (crosses-up) / Strategy P1 Long/Cash / Lead 6 months.\n\n"
        "Each month, look at the current UMCSENT reading versus 12 months "
        "ago and compute the percentage change. Apply this to what the "
        "12-month change was 6 months ago (the lead). If the 6-month-ago "
        "year-over-year change was positive (sentiment improving) → hold XLV fully. "
        "If zero or negative → move to cash. No leverage, no shorting."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "The winning strategy uses **University of Michigan Consumer "
        "Sentiment (UMCSENT) Year-over-Year Change** with "
        "a **6-month lead**:\n\n"
        "1. Each month, look at the current UMCSENT reading versus 12 "
        "months ago; compute the percentage change.\n"
        "2. Check what this year-over-year change was **6 months ago** "
        "(the lead).\n"
        "3. If the 6-month-ago year-over-year change was **positive** (sentiment "
        "improving): hold XLV (Long/Cash position = 1).\n"
        "4. If the 6-month-ago year-over-year change was **zero or negative** "
        "(sentiment flat or deteriorating): move to cash (Long/Cash "
        "position = 0).\n"
        "5. Update the position at the start of each month.\n\n"
        "The 6-month lead means you are acting on information that is 6 "
        "months stale — and the strategy still works. This confirms that "
        "sentiment anticipates sector dynamics well in advance.\n\n"
        "**Metric definitions.** Out-of-sample (OOS) Sharpe measures return "
        "per unit of volatility in the test period that was not used to "
        "select the rule. OOS Return is the annualised return in that test "
        "period. Max Drawdown is the worst peak-to-trough loss. Turnover "
        "shows how often the strategy changes position each year. Win Rate "
        "is the share of tested periods or trades with a positive return."
    )

    MANUAL_USE_MD = (
        "You do not need software to implement this signal:\n\n"
        "**1. Retrieve the University of Michigan Consumer Sentiment "
        "(UMCSENT) reading.** Federal Reserve Economic Data (FRED) series: "
        "`UMCSENT`. Published mid-month for the current month. Free at "
        "fred.stlouisfed.org.\n\n"
        "**2. Compute the year-over-year change.** Divide today's reading "
        "by the reading from 12 months ago and subtract 1. Example: UMCSENT "
        "= 72.0, 12 months ago = 68.0 → year-over-year = +5.9%.\n\n"
        "**3. Check what this year-over-year reading was 6 months ago.** Pull the "
        "UMCSENT reading from 18 months ago and 6 months ago, compute "
        "the year-over-year change for 6 months back: (6 months ago / "
        "18 months ago − 1).\n\n"
        "**4. Apply the rule.** If that 6-month-ago year-over-year change was positive → "
        "hold XLV. If zero or negative → hold cash or short-duration bonds.\n\n"
        "**5. Rebalance monthly.** The signal changes once a month at "
        "most. Turnover averages ~2.4 round-trips per year — negligible "
        "transaction costs."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    # umcsent_xlv uses `wf_sharpe` rather than canonical `walk_forward`.
    WALK_FORWARD_CHART_NAME = "wf_sharpe"
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

    CAVEATS_MD = (
        "1. **Direction was a surprise.** The textbook countercyclical "
        "story was wrong for this pair. Do not assume economic theory "
        "determines the signal direction — validate empirically.\n\n"
        "2. **6-month lag limits responsiveness.** The strategy cannot "
        "avoid fast crashes (COVID, flash crashes). It works best for "
        "slow-moving sentiment cycles.\n\n"
        "3. **Out-of-sample period covers only ~6 years.** Shorter than "
        "the 8-year out-of-sample period for the high-yield minus "
        "investment-grade credit spread pair or the industrial production "
        "pair. Short out-of-sample windows "
        "can produce inflated Sharpe estimates.\n\n"
        "4. **Health care sector dynamics change.** The Affordable Care "
        "Act (ACA), drug-pricing "
        "regulation, COVID policy, and demographic shifts all affect "
        "XLV. The historical sentiment-XLV relationship may shift if "
        "sector fundamentals change structurally.\n\n"
        "5. **This is not portfolio insurance.** The strategy reduces "
        "but does not eliminate drawdowns. A -10.9% max drawdown still "
        "represents meaningful portfolio pain."
    )

    TRADE_LOG_EXAMPLE_MD = (
        "**Crisis anchor — February 2020 COVID entry.** From "
        "`results/umcsent_xlv/winner_trades_broker_style.csv` (the "
        "canonical APP-TL1 artefact shipped Wave 10H.2):\n\n"
        "- **2020-02-29 — BUY XLV, 100% long, price $83.70.** The trade "
        "log records a full-exposure entry into XLV on 29-Feb-2020 (the "
        "last business day before the COVID crash began in earnest on "
        "02-Mar). The signal rationale: 6-month-lagged UMCSENT "
        "year-over-year change = "
        "**+7.676%** — sentiment had been strongly improving through "
        "mid-2019, and the 6-month-lead rule translated that into a "
        "full long position in February 2020.\n"
        "- **Cumulative profit and loss (P&L) at entry: +14.25%.** The prior long holding "
        "had already compounded meaningfully since the strategy's "
        "out-of-sample start (2019-04-30 at University of Michigan "
        "Consumer Sentiment year-over-year change −1.619, initial entry), so "
        "the February 2020 buy added to an already-profitable book.\n"
        "- **Economic narrative.** This is the case study that defines "
        "the rule's limits. The 6-month lag is a feature against "
        "short-term noise, but it is also the reason the rule could not "
        "avoid the March 2020 drawdown. The trade was correct given its "
        "information set — University of Michigan Consumer Sentiment in "
        "August 2019 said 'procyclical, "
        "hold XLV' — but a once-in-a-century pandemic overran any "
        "monthly-frequency sentiment signal. The rule reduced XLV drawdown "
        "from -15.6% (buy-and-hold) to -10.9% over the full out-of-sample window; "
        "it did not eliminate the March 2020 pain.\n"
        "- **Honest caveat.** Users who need crash protection should "
        "pair this rule with a faster signal (the CBOE Volatility Index "
        "divided by the 3-month CBOE Volatility Index pair in this portal). "
        "University of Michigan Consumer Sentiment × XLV is a medium-frequency regime filter, "
        "not a crash hedge."
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **University of Michigan Consumer Sentiment** | Federal Reserve Economic Data (FRED) | UMCSENT | Monthly |
| **Health Care Select Sector SPDR Fund** | Yahoo Finance | XLV | Daily → Monthly |
| **S&P 500 ETF Trust benchmark** | Yahoo Finance | SPY | Daily → Monthly |
| **National Bureau of Economic Research (NBER) Recession Dates** | Federal Reserve Economic Data / NBER | USREC | Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |
| **Unemployment** | FRED | UNRATE | Monthly |

*Scope discipline (ECON-SD).* Only University of Michigan Consumer Sentiment
(UMCSENT) and Health Care Select Sector SPDR Fund (XLV) are in-scope primary
signals.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "**Michigan Consumer Sentiment (UMCSENT).** Federal Reserve Economic "
    "Data (FRED) series: monthly index "
    "of consumer confidence published by the University of Michigan Survey "
    "of Consumers. Index baseline = 100 (November 1966). Released mid-month "
    "for the current survey month. The newer web-interview process reaches "
    "roughly 900-1,000 respondents per month. "
    "Not seasonally adjusted (the survey methodology removes most "
    "seasonality at source).\n\n"
    "Derived signals entered into the tournament:\n\n"
    "| Signal | Formula | Stationarity |\n"
    "|:-------|:--------|:-------------|\n"
    "| `umcsent` | raw level | non-stationary (use transformed) |\n"
    "| `umcsent_yoy` | (umcsent / umcsent.shift(12) − 1) × 100 | **winner** — approximately stationary |\n"
    "| `umcsent_mom` | 1-month change | approximately stationary |\n"
    "| `umcsent_zscore` | 36M rolling z-score | stationary by construction |\n"
    "| `umcsent_3m_ma` | 3-month moving average | non-stationary (regime indicator) |\n"
    "| `umcsent_direction` | sign(umcsent_mom) | stationary by construction |\n"
    "| `umcsent_dev_ma` | level − 3M MA | approximately stationary |\n\n"
    "**Health Care Select Sector SPDR Fund (XLV) target.** Daily adjusted closing prices (Yahoo Finance, "
    "`auto_adjust=True`) resampled to monthly last close. Forward return "
    "series computed as `xlv.shift(-h) / xlv - 1` for h = 1, 3, 6, 12 "
    "months."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|:-------|:--------------------|:----------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline University of Michigan Consumer Sentiment-XLV test |
| Granger Causality | One-directional predictive content | Tests sentiment → XLV asymmetry |
| Regime Quartile Returns | Model-free gradient across sentiment distribution | Assumption-light regime check |
| Signal Distribution Analysis | Full empirical distribution of the signal | Diagnostic for threshold choice |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals (7)** | umcsent (level), umcsent_yoy, umcsent_mom, umcsent_zscore, umcsent_3m_ma, umcsent_direction, umcsent_dev_ma |
| **Thresholds** | T1 fixed IS percentile (p25/p50/p75), T2 rolling percentile (60M), T3 rolling z-score bands (±1.0, ±1.5, ±2.0), T4 zero-crossing (for change signals) |
| **Strategies (3)** | P1 Long/Cash (binary toggle), P2 Signal Strength (proportional scaling), P3 Long/Short (±1 position) |
| **Lead times (5)** | 0, 1, 2, 3, 6 months |
| **Direction** | Procyclical applied (empirically observed direction) |

Ranked by out-of-sample Sharpe. **1,305 total combinations tested; 1,196
valid** (out-of-sample Sharpe > 0, turnover ≤ 24/year, out-of-sample n ≥ 12). Winner (per
`results/umcsent_xlv/winner_summary.json`, authoritative): **umcsent_yoy /
zero-crossing (crosses-up) / P1_long_cash / Lead 6 months → out-of-sample
Sharpe 1.0202, out-of-sample annualised return +11.93%, max drawdown
−10.87%, out-of-sample volatility 11.7%, Sortino 2.01, Calmar 1.10, 81
out-of-sample trades, win rate 37.0%, annual turnover 2.4. Buy-and-hold
XLV benchmark: Sharpe 0.7164, max drawdown −15.6%.**
"""

_REFERENCES_MD = """
- Curtin, R. T. (2007). Consumer sentiment surveys: Worldwide review and assessment. *Journal of Business Cycle Measurement and Analysis*, 2007(1), 7–42.
- Ludvigson, S. C. (2004). Consumer confidence and consumer spending. *Journal of Economic Perspectives*, 18(2), 29–50.
- Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645–1680.
- Lemmon, M., & Portniaguina, E. (2006). Consumer confidence and asset prices: Some empirical evidence. *Review of Financial Studies*, 19(4), 1499–1529.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Full sample: 1998-12 to 2025-12 (325 monthly observations). "
        "The in-sample/out-of-sample cut is computed dynamically using "
        "ECON-OOS2: OOS_months = min(max(36, round(N × 0.25)), 120). "
        "With N = 325, out-of-sample = 81 months. In-sample: 1998-12 "
        "to 2019-03 (~243 observations). "
        "Out-of-sample: 2019-04-30 to 2025-12 (~81 observations, ~6.75 years). "
        "XLV data starts 1998-12 (the exchange-traded fund's inception); "
        "University of Michigan Consumer Sentiment is available from 1978 "
        "but is aligned to the XLV sample for this pair."
    ),
    plain_english=(
        "This section explains exactly how we did the analysis: which "
        "data we used, how we constructed each signal, which statistical "
        "tests we ran, and what could go wrong. Normal readers can skip "
        "it. Expert readers can use it to reproduce or criticise our "
        "work."
    ),
)
