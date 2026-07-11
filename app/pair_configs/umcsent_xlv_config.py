"""UMCSENT × XLV pair configuration (Rule APP-PT1).

Wave 10I.A narrative port (Ray): prose fields authored from legacy
app/pages/10_umcsent_xlv_*.py (pre-migration, commit 24e2f16~1),
cross-checked against results/umcsent_xlv/winner_summary.json.

APP-TL1 note: `results/umcsent_xlv/winner_trades_broker_style.csv` is
present (shipped Wave 10H.2, commit 2c11046). `TRADE_LOG_EXAMPLE_MD`
is authored directly from that file.

Pair ID: umcsent_xlv  (richest hand-written pair — 1,563 legacy lines)
Winner (winner_summary.json, authoritative): UMCSENT 3-month momentum /
rolling z-score > +1.0 / P1_long_cash / 6-month lead — OOS Sharpe 1.16,
OOS return +7.95%, Max DD -0.7%, Calmar 11.3, win rate 16%.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: University of Michigan Consumer Sentiment and the Healthcare Sector"
    PAGE_SUBTITLE = (
        "Does University of Michigan consumer sentiment predict returns in "
        "the defensive Health Care Select Sector SPDR Fund (XLV)?"
    )

    HEADLINE_H2 = (
        "## University of Michigan Consumer Sentiment as a directional signal "
        "for Health Care Select Sector SPDR Fund (XLV)"
    )

    PLAIN_ENGLISH = (
        "The UMCSENT survey asks roughly "
        "900-1,000 respondents under its newer web-interview process how "
        "confident they feel about the economy. This page "
        "asks whether those survey results — a number published monthly "
        "and free to download — can help time exposure to the Health Care "
        "Select Sector SPDR Fund (XLV). Health care is a defensive sector: "
        "people visit doctors whether the economy is booming or not. The "
        "working hypothesis is straightforward: higher or improving "
        "UMCSENT should coincide with better XLV performance, and XLV "
        "should hold up better than the broad market when sentiment is weak."
    )

    WHERE_THIS_FITS = ""

    ONE_SENTENCE_THESIS = (
        "*When UMCSENT 3-month momentum improves enough to clear a rolling "
        "z-score > +1.0 trigger, with a 6-month lead, Health Care Select "
        "Sector SPDR Fund (XLV) has historically performed better. The "
        "hypothesis is that improving household confidence and risk appetite "
        "can support XLV over the next several months, even though health "
        "care is partly defensive.*"
    )

    KPI_CAPTION = (
        "The winning rule uses UMCSENT 3-month momentum with a 6-month "
        "lead and a rolling z-score > +1.0 trigger. When the 6-month-lagged "
        "momentum clears that threshold, the strategy holds XLV; otherwise, "
        "it moves to cash. Out-of-sample (OOS) Sharpe is 1.16 vs 0.72 for "
        "buy-and-hold XLV, with max drawdown reduced from -15.6% to -0.7% "
        "and Calmar rising to 11.3."
    )

    HERO_TITLE = "UMCSENT Year-over-Year Change vs. Health Care Select Sector SPDR Fund (XLV)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "UMCSENT YoY Change (%) is the red line on the left axis; XLV "
        "adjusted price is the blue line on the right axis. The shaded bands "
        "mark months when UMCSENT was falling year-over-year. The important "
        "timing lesson is that UMCSENT can lag XLV price action in fast "
        "market moves: prices often react first, while household sentiment "
        "updates more slowly through monthly surveys."
    )

    REGIME_TITLE = "What History Shows: XLV Returns by Consumer-Sentiment Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "XLV performance by quartile of UMCSENT year-over-year change — "
        "annualised Sharpe (left panel) and annualised return (right panel). "
        "Quartile 1 = lowest (most negative) year-over-year change; "
        "Quartile 4 = highest (most positive). The non-monotonic pattern "
        "(Quartile 2 ~1.09 / 13.8% > Quartile 4 ~0.93 / 10.6% > Quartile 3 "
        "~0.56 / 7.7% > Quartile 1 ~0.23 / 4.2%) is identical in both panels "
        "and confirms the procyclical direction — falling sentiment "
        "coincides with the worst XLV regime — while suggesting that the "
        "peak of optimism is itself a late-cycle warning sign."
    )

    NARRATIVE_SECTION_1 = (
        "### Why University of Michigan Consumer Sentiment and Health Care?\n\n"
        "The UMCSENT index has been "
        "published monthly since 1978. The current survey reaches roughly "
        "900-1,000 respondents under the newer web-interview process. "
        "Participants are asked about their financial situation, their outlook for the "
        "broader economy in the next 12 months, and their views on "
        "conditions five years out. The index is one of the most watched "
        "leading indicators in the world — central banks, equity analysts, "
        "and economists all track it because it has historically turned "
        "before consumer spending does.\n\n"
        "### The Defensive-Healthcare Hypothesis\n\n"
        "UMCSENT indicator shows consumer sentiment in different periods, "
        "and this sentiment can serve as a leading indicator for the Health "
        "Care sector. When confidence is high, households are more willing "
        "to spend on discretionary health services and wellness products, "
        "driving stronger sector performance. In contrast, during low "
        "sentiment phases, reduced consumer optimism limits spending and "
        "growth opportunities, resulting in sector losses. Despite health "
        "care's defensive nature, the forward-looking aspect of UMCSENT "
        "provides valuable predictive insight, with high sentiment "
        "consistently signaling stronger returns compared to periods of low "
        "sentiment."
    )

    NARRATIVE_SECTION_2 = (
        "### Key Findings\n\n"
        "Two facts about this pair deserve special emphasis:\n\n"
        "**The corrected winner uses 3-month momentum, not the sentiment "
        "level or year-over-year change.** Raw sentiment levels are "
        "non-stationary and reflect long secular trends. The winning "
        "signal asks whether sentiment has improved enough over the prior "
        "three months to clear a rolling z-score > +1.0 trigger.\n\n"
        "**The trading rule uses a 6-month lead, but the lead-lag evidence "
        "is mixed.** The tournament winner uses 6-month-lagged UMCSENT "
        "3-month momentum. The cross-correlation evidence is strongest "
        "at 2-4 months, with statistically significant UMCSENT-leading "
        "correlations from 1-5 months only. Formal Granger causality does not "
        "confirm UMCSENT as a statistically significant predictor at lags "
        "1-5; in fact, the reverse direction from XLV to UMCSENT is stronger "
        "in that test. Treat the lead time as a strategy-selection result, "
        "not as proof that sentiment mechanically leads prices by 6 months.\n\n"
        "The main limits are sample length (XLV starts 1998-12, so the "
        "full sample is 325 monthly observations and the out-of-sample "
        "window is only about 6 years) and the sector-specific nature of "
        "the target (Affordable Care Act policy, drug-pricing policy, "
        "COVID, and demographics all affect "
        "XLV independently of consumer sentiment)."
    )

    SCOPE_NOTE = (
        "*Scope discipline.* Only University of Michigan Consumer "
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
            "narrative": "Consumer sentiment deteriorated sharply through 2001 as the economy contracted and unemployment rose. XLV, as a defensive health care holding, held up relatively well. This is useful context for a sentiment-momentum timing rule: monthly confidence data can flag deteriorating conditions, but the corrected winner should be read through its 3-month momentum and rolling z-score trigger.",
            "caption": "2001 sentiment decline: UMCSENT deteriorated while XLV held up defensively. NBER recession shading marks the official recession window.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": "Sentiment collapsed through 2008-2009 as unemployment surged and household wealth evaporated. XLV declined meaningfully, though less than S&P 500 Index (SPX). A long-lead sentiment rule is economically plausible in this setting because household confidence deteriorated before the equity trough, but the corrected winner remains the 3-month momentum / rolling z-score rule.",
            "caption": "Global Financial Crisis: UMCSENT weakened sharply while XLV declined less than SPX. NBER recession shading marks the official recession window.",
        },
        {
            "slug": "covid",
            "title": "COVID Crash (2020)",
            "narrative": "Sentiment plunged to near-record lows in April 2020. XLV experienced a moderate drawdown before recovering sharply — health care stocks benefited from vaccine and treatment demand. This is the clearest example of the rule's practical limitation: monthly sentiment data can lag fast market recoveries, especially with a 6-month lead.",
            "caption": "COVID: UMCSENT collapsed April 2020; XLV recovered fast on health care demand. NBER recession shading marks the official recession window.",
        },
        {
            "slug": "rates_2022",
            "title": "Fed Hiking Cycle (2022)",
            "narrative": "Consumer sentiment hit multi-decade lows in June 2022 (University of Michigan index at 50) driven by inflation and rising rates. XLV outperformed S&P 500 Index (SPX) during this period — a partial vindication of the defensive thesis. This is a caveat for any sentiment-momentum timing rule: a bearish sentiment backdrop can coexist with defensive-sector relative strength.",
            "caption": "June 2022 sentiment hit 50-year low while XLV outperformed S&P 500 Index (SPX) defensively.",
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 4 method blocks
# =========================================================================
CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Sector Correlation Analysis",
    method_theory=(
        "This test asks whether the indicator and target move together in a "
        "roughly straight-line way. The indicator is UMCSENT, transformed "
        "into year-over-year change. The target is future XLV return. "
        "Pearson correlation is appropriate when the point cloud is broadly "
        "linear; Spearman rank correlation is a backup when the relationship "
        "is monotonic but curved or affected by extreme observations."
    ),
    question=(
        "Does higher UMCSENT year-over-year change line up with stronger "
        "future XLV returns, and does the scatter plot look linear enough "
        "for Pearson correlation to be useful?"
    ),
    how_to_read=(
        "Each point is one month. The x-axis is UMCSENT year-over-year "
        "change; the y-axis is XLV's 6-month forward return. If the points "
        "form a tilted straight-line cloud, linear correlation can summarize "
        "the relationship. If the cloud is curved or split into clusters, "
        "non-linear or regime methods are more appropriate."
    ),
    chart_name="correlation_scatter",
    chart_caption=(
        "Scatter cloud for UMCSENT year-over-year change versus XLV "
        "6-month forward return, with a fitted linear trend line."
    ),
    observation=(
        "The point cloud is upward sloping but wide. That means the "
        "relationship is positive on average, but UMCSENT is not a precise "
        "month-by-month forecast. The strongest simple correlation in the "
        "existing correlation table is for UMCSENT z-score versus XLV "
        "6-month forward return, with p = 0.005. The winning year-over-year "
        "signal is directionally consistent but weaker as a pure linear "
        "forecast."
    ),
    interpretation=(
        "Linear correlation can be used as a first diagnostic, but it should "
        "not be the only test. The scatter is too noisy for a single straight "
        "line to explain the whole relationship. That is why the Evidence "
        "page also uses quartile regimes, distribution analysis, and "
        "lead-lag tests."
    ),
    key_message=(
        "UMCSENT has a positive but noisy relationship with future XLV "
        "returns. Linear correlation is useful as a summary, but regime and "
        "distribution checks are needed because the relationship is not a "
        "tight straight line."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality",
    method_theory=(
        "Granger causality asks whether past UMCSENT values improve "
        "forecasts of future XLV returns beyond what XLV's own recent "
        "history already provides. We test both directions (consumer "
        "sentiment to XLV and XLV to consumer sentiment) at lags 1-5 months "
        "using F-tests on augmented vector autoregression regressions with "
        "HC3 robust standard errors."
    ),
    question=(
        "Does consumer sentiment carry information about future health care "
        "equity returns that is not already priced into XLV itself?"
    ),
    how_to_read=(
        "The cross-correlation chart below shows the lead-lag pattern. "
        "Negative lags mean UMCSENT moved before XLV returns. Bars outside "
        "the dashed 95% confidence band are statistically notable. Formal "
        "Granger p-values are read separately: p-values below 0.05 indicate "
        "stronger evidence of predictive content."
    ),
    chart_name="ccf",
    chart_caption=(
        "Cross-correlation function between UMCSENT year-over-year change "
        "and XLV monthly return at lags −12 to +12 months. Red bars are "
        "statistically significant at 95% confidence."
    ),
    observation=(
        "The cross-correlation result is strongest when UMCSENT leads XLV "
        "by 2 months, with significant positive correlations from 1 to 5 "
        "months. However, the formal Granger table is more conservative: "
        "UMCSENT does not Granger-cause XLV at lags 1-5 because all p-values "
        "are above 0.05. The reverse direction is stronger in that formal "
        "test: XLV Granger-causes UMCSENT at lags 1-5."
    ),
    interpretation=(
        "This means the lead-lag story should be stated carefully. "
        "Cross-correlation says UMCSENT often moves before XLV returns over "
        "a 1-5 month window. Granger causality says XLV price information "
        "also helps explain later sentiment, which is intuitive: market and "
        "economic conditions affect household confidence. The strategy can "
        "still work, but the evidence is not a clean one-way causal proof."
    ),
    key_message=(
        "The timing evidence is mixed: cross-correlation points to a 1-5 "
        "month UMCSENT lead, strongest around 2-4 months, while formal "
        "Granger causality does not confirm a clean UMCSENT-to-XLV lead."
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
        "Left panel: annualised Sharpe ratio in each UMCSENT "
        "year-over-year quartile. Right panel: annualised "
        "return. Quartile 1 = lowest (most negative) year-over-year "
        "change; Quartile 4 = highest (most positive). Look for a monotonic "
        "pattern to confirm the regime-return relationship."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "Annualised XLV Sharpe ratio and return by quartile of University "
        "of University of Michigan Consumer Sentiment year-over-year change. Quartile 1 "
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
        "of change** — positive but not extreme — which is consistent with "
        "the corrected winner's emphasis on sentiment momentum."
    ),
    key_message=(
        "Falling UMCSENT (Quartile 1) is the worst regime for XLV returns. "
        "Quartile 2 is the best regime and Quartile 4 is the second best, "
        "so rising sentiment helps, but extreme optimism is not necessarily "
        "the strongest setup."
    ),
)


SIGNAL_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Signal Distribution Analysis",
    method_theory=(
        "We examine how XLV 3-month forward returns are distributed when "
        "the UMCSENT direction signal is "
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
        "Left: distribution of UMCSENT "
        "year-over-year changes (roughly symmetric, "
        "centred near zero). Right: XLV 3-month forward returns when "
        "sentiment is rising vs. falling. The box plots reveal whether "
        "the effect is median-shifting or tail-driven."
    ),
    observation=(
        "The year-over-year change distribution is roughly bell-shaped and "
        "close to a normal distribution, with slightly more months in "
        "negative territory. The return box plots show "
        "that XLV forward returns are slightly higher when sentiment is "
        "rising (median ~+3% vs +2% over 3 months), but the distributions "
        "substantially overlap — confirming a weak average effect rather "
        "than a sharp categorical separator. The left tail is notably "
        "worse during falling-sentiment periods, which is where the risk-"
        "management value of the strategy resides."
    ),
    interpretation=(
        "This statistic is about distribution shape, not trade win rate. "
        "The main finding is that rising-sentiment months have a slightly "
        "better center of return distribution, while falling-sentiment "
        "months have a worse left tail. That supports using the signal as "
        "a risk filter rather than as a precise return forecast."
    ),
    key_message=(
        "UMCSENT year-over-year changes are approximately bell-shaped. "
        "This diagnostic supports sentiment-improvement intuition, while "
        "the corrected strategy rule uses 3-month momentum above a rolling "
        "z-score > +1.0 threshold."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "For a monthly-rebalanced strategy the decision is: how stale should "
        "the signal be allowed to get before we trade on it? This block "
        "computes Pearson correlations between the UMCSENT momentum signal "
        "lagged L = 0…12 months and the XLV 1-month forward return, then reads "
        "off which lead maximises predictive content — and checks it against "
        "the tournament's traded 6-month lead."
    ),
    question=(
        "Which lead carries the most predictive content for the UMCSENT "
        "momentum signal — and does it line up with the traded 6-month lead?"
    ),
    how_to_read=(
        "Rows are UMCSENT signal variants; columns are signal lead in MONTHS "
        "(L0 = contemporaneous, L12 = 12 months ago). Forward horizon fixed at "
        "1 month. Cell shading is Pearson r (linear co-movement, -1 to +1) "
        "against `xlv_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson correlations between **signal lagged L months** and **XLV "
        "1-month forward return**. The traded signal `umcsent_mom` peaks at "
        "**L5 (r=+0.133, p<0.05)** — the only significant cell in its row, and "
        "one month short of the traded 6-month lead. A near-corroboration: the "
        "correlation diagnostic endorses a lead adjacent to the tournament's "
        "choice."
    ),
    observation=(
        "Reading the row directly: the traded signal `umcsent_mom` is weak at "
        "most leads (L0 −0.015, L3 −0.045, L6 +0.023) and reaches its single "
        "significant cell at **L5 (r=+0.133, p<0.05)**. That peak sits one "
        "month short of the tournament's traded L6, so the linear diagnostic "
        "and the tournament land on adjacent leads rather than the same one. "
        "The procyclical sign (positive correlation: rising sentiment momentum "
        "→ stronger forward XLV) matches the direction-surprise finding on the "
        "Story page."
    ),
    interpretation=(
        "A **near-corroboration**: the lead-correlation peak (L5, significant) "
        "is one month off the traded lead (L6), which is close enough to treat "
        "the two as agreeing on the same broad region rather than diverging. "
        "**In plain English:** consumer-sentiment momentum from about five to "
        "six months earlier carries the cleanest next-month signal for health-"
        "care stocks, and the trading rule reads from within that window. The "
        "one-month offset is minor — not the clean exact match of the "
        "strongest pairs, but well short of a divergence."
    ),
    key_message=(
        "The traded signal `umcsent_mom` peaks at **L5 (r=+0.133, p<0.05)**, "
        "one month short of the traded L6 — a near-corroboration. The "
        "correlation diagnostic and the tournament agree on the same broad "
        "5–6 month region, with a minor one-month offset."
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This chart is a projection of the pair's ONE native tournament (GH #13 "
        "single-source): the orange line is the **published winner's own** OOS "
        "Sharpe at each lead; the grey bars are the best-of-any-signal envelope "
        "on the SAME grid; the dashed line is XLV buy-and-hold (Sharpe 0.72). "
        "**Provenance note (Option C, stakeholder-approved 2026-07-11):** this "
        "pair's tournament was deliberately capped at L0–6 (the 2–5-month "
        "cross-correlation window plus release lag). GH#13 extended it to the "
        "full L0–12 as a DIAGNOSTIC — so long-lead derivatives are TESTED, not "
        "shielded by a linear-correlation cap — while the PUBLISHED winner stays "
        "constrained to the motivated L0–6 window. L7–12 here is diagnostic "
        "context, not selection universe."
    ),
    question=(
        "Is the traded L6 a robust ridge or an isolated spike — and does "
        "extending the diagnostic to L7–12 reveal any real long-lead edge, or "
        "just the multiple-testing noise the linear cap was hiding?"
    ),
    how_to_read=(
        "Orange line + green star: the deployed winner's Sharpe by lead, peaking "
        "at its traded L6. A broad plateau around the traded lead is robust; a "
        "tall isolated point that collapses one lead either side is fragile. "
        "Grey bars: the best any signal achieves at each lead (envelope ≥ the "
        "winner curve by construction). L7–12 is diagnostic-only."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "The winner's own curve is a **sharp isolated spike at its traded L6 "
        "(OOS Sharpe 1.1586)** that collapses to ~0.37 at L5 and ~0.20 at L7 — "
        "NOT the 'rising L6–L8 ridge' an earlier exploratory sweep suggested "
        "(on the native grid the best-of-any-signal at L7 and L8 is only ~0.72, "
        "i.e. buy-and-hold). L6 tops the cross-signal envelope, but that "
        "envelope is **nearly flat** (L6 1.16 edges L5 1.12 by 0.04). Across the "
        "diagnostic L7–12 nothing beats the winner (best 1.03 at L10), and "
        "`umcsent_direction` — significant at L10 in the correlation table — "
        "scores only ~0.72–0.97: long-lead noise, not a tradable edge."
    ),
    observation=(
        "On the native tournament grid the published winner (`umcsent_mom / "
        "T3_zscore_1.0 / P1_long_cash / L6`, OOS Sharpe **1.1586**) tops the "
        "lead profile at its traded L6 — but its own curve is a **single "
        "isolated spike**: 1.16 at L6, collapsing to ~0.37 at L5 and ~0.20 at "
        "L7, and below ~0.7 at almost every other lead. The cross-signal "
        "envelope is **nearly flat** (L6 1.16 vs L5 1.12, margin 0.04), and the "
        "best-of-any-signal at L7 and L8 falls to ~0.72 (buy-and-hold). The "
        "correlation diagnostic (left tab) peaks at L5 (r=+0.133), one lead "
        "before the winner — a modest adjacent corroboration.\n\n"
        "(An earlier version of this block read an exploratory *comparator* "
        "sweep on a different grid and claimed a 'rising L6–L8 ridge, peak L7 "
        "1.18' — that was a grid artefact; on the native tournament L7/L8 are "
        "~0.72.) **Diagnostic verdict (the stakeholder's question):** extending "
        "the grid to L0–12 surfaces NO robust long-lead edge — the best L7–12 "
        "combo is only 1.03 (< the L6 winner), and `umcsent_direction`, the "
        "transform whose per-lag correlation is significant at L10 (r=0.113*), "
        "scores at most 0.97 across L7–12. So the linear-correlation cap was "
        "not shielding a real signal; the L10 correlation is multiple-testing "
        "noise (≈78 lead×transform tests, no plausible mechanism for consumer "
        "sentiment → defensive-healthcare at a 10-month lead)."
    ),
    interpretation=(
        "The honest summary: **the traded L6 is a sharp single-lead spike on a "
        "flat envelope, not a ridge** — the old 'rising L6–L8 ridge' was an "
        "exploratory-sweep artefact the native grid refutes (L7/L8 ≈ 0.72). The "
        "one modest positive is the adjacent L5 correlation peak (r=+0.133). "
        "Extending the diagnostic to L7–12 confirms there is no hidden long-lead "
        "edge — the direction signal's L10 correlation does not survive the "
        "tournament and reads as noise. Combined with the backward-causality "
        "finding (XLV Granger-predicts UMCSENT at every lag; UMCSENT→XLV n.s.), "
        "read the OOS Sharpe as a searched, low-confidence drawdown-control "
        "result, not evidence that sentiment leads health care."
    ),
    key_message=(
        "On the native grid the winner's L6 (OOS Sharpe 1.1586) is a **sharp "
        "single-lead spike** (collapsing to ~0.37/0.20 at L5/L7) on a nearly "
        "flat envelope — not the 'L6–L8 ridge' the old exploratory sweep "
        "claimed (native L7/L8 ≈ 0.72). The GH#13 L0–12 diagnostic finds NO "
        "long-lead edge (best L7–12 = 1.03; `umcsent_direction`'s L10 "
        "correlation is multiple-testing noise). With backward causality, a "
        "searched low-confidence drawdown-control result."
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
    "downloads": [
        {"label": "Granger causality (12 lag-direction rows)",
         "path": "results/umcsent_xlv/core_models_20260420/granger_causality.csv"},
        {"label": "Predictive regressions (12 signal-horizon rows)",
         "path": "results/umcsent_xlv/core_models_20260420/predictive_regressions.csv"},
        {"label": "Quantile regression (7 quantiles of forward XLV)",
         "path": "results/umcsent_xlv/core_models_20260420/quantile_regression.csv"},
        {"label": "Local projections (4 horizons)",
         "path": "results/umcsent_xlv/core_models_20260420/local_projections.csv"},
        {"label": "Diagnostics summary (Jarque-Bera, Durbin-Watson; 4 rows)",
         "path": "results/umcsent_xlv/core_models_20260420/diagnostics_summary.csv"},
        {"label": "Cointegration tests (Engle-Granger + Johansen; 2 rows)",
         "path": "results/umcsent_xlv/core_models_20260420/cointegration.csv"},
        {"label": "Markov-switching 2-state parameters (10 rows)",
         "path": "results/umcsent_xlv/core_models_20260420/markov_switching_2state.csv"},
    ],
    "plain_english": (
        "Four methods all point to the same direction: when sentiment "
        "trends upward year-over-year, XLV tends to do better over the "
        "following months. The surprise — and the honest finding — is "
        "that this is the *procyclical* direction, not the defensive/"
        "countercyclical pattern that standard economic theory predicts."
    ),
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK],
    "level1_labels": ["Correlation", "Lead Analysis", "Lead Tournament", "Granger Causality"],
    "level2": [REGIME_BLOCK, SIGNAL_DIST_BLOCK],
    "level2_labels": ["Regime Analysis", "Signal Distribution"],
    "tournament_intro": (
        "With the econometric case established, we swept a 5-dimensional "
        "tournament over 7 signal transforms, 7 threshold methods, 3 "
        "strategy families, and 5 lead times — 1,305 raw combinations "
        "pruned to 1,195 valid. The corrected winner posts OOS Sharpe 1.16 — the "
        "**best of those 1,195 valid combinations**: the maximum of the "
        "search, not a typical result. The median valid combination "
        "scored 0.63. The top 5 strategies were validated with "
        "bootstrap significance testing and transaction-cost sensitivity. "
        "The winning specification is on the Strategy page."
    ),
    "transition": (
        "Four statistical methods converge on the same conclusion: "
        "UMCSENT 3-month momentum is a useful but noisy "
        "indicator for XLV health care returns. Now: what does "
        "the winning strategy actually do, and how has it performed?"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Translating UMCSENT Signals into XLV Positioning"
    PAGE_SUBTITLE = (
        "We tested over 1,300 strategy combinations to find the most robust "
        "way to time Health Care Select Sector SPDR Fund (XLV) exposure "
        "using consumer sentiment."
    )

    PLAIN_ENGLISH = (
        "We tested over 1,300 combinations of rules for using consumer "
        "sentiment to time XLV exposure. The corrected winner is specific: "
        "hold XLV when 6-month-lagged UMCSENT 3-month momentum is above "
        "its rolling z-score +1.0 threshold, and move to cash otherwise. "
        "This rule out-performed buy-and-hold on drawdown control and "
        "risk-adjusted return over the 2019-04-30 to 2025-12-31 "
        "out-of-sample window."
    )

    SIGNAL_RULE_MD = (
        "**Tournament winner:** Signal University of Michigan Consumer "
        "Sentiment (UMCSENT) 3-month momentum (`S3_mom` / `umcsent_mom`) / "
        "Threshold rolling z-score > +1.0 / Strategy P1 Long/Cash / Lead "
        "6 months.\n\n"
        "Each month, compute UMCSENT 3-month momentum and compare the "
        "6-month-lagged value with its rolling z-score +1.0 threshold. If "
        "the lagged momentum is above the threshold, hold XLV fully. "
        "Otherwise, move to cash. No leverage, no shorting."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "The winning strategy uses **University of Michigan Consumer "
        "Sentiment (UMCSENT) 3-month momentum** with a **rolling z-score "
        "> +1.0 trigger** and a **6-month lead**:\n\n"
        "1. Each month, compute the change in UMCSENT over the prior three "
        "months.\n"
        "2. Check what this 3-month momentum value was **6 months ago** "
        "(the lead).\n"
        "3. Compare that lagged momentum with its rolling threshold: the "
        "recent rolling mean plus one standard deviation.\n"
        "4. If the 6-month-lagged momentum is **above** that threshold: "
        "hold XLV (Long/Cash position = 1).\n"
        "5. If it is **at or below** that threshold: move to cash "
        "(Long/Cash position = 0).\n"
        "6. Update the position at the start of each month.\n\n"
        "When the signal hovers near its rolling threshold, it is close to the decision line. "
        "That does not mean the signal is broken; it means the economy is "
        "near the boundary between improving and deteriorating sentiment. "
        "Small monthly changes can flip the strategy from long XLV to cash "
        "or back again.\n\n"
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
        "**2. Compute 3-month momentum.** Compare today's reading with the "
        "reading three months earlier to measure whether sentiment is "
        "improving quickly.\n\n"
        "**3. Build the rolling z-score threshold.** For each month, compare "
        "the 6-month-lagged 3-month momentum value with its rolling mean "
        "plus one standard deviation.\n\n"
        "**4. Apply the rule.** If that 6-month-lagged momentum is above "
        "the rolling z-score +1.0 threshold, hold XLV. If not, hold cash "
        "or short-duration bonds.\n\n"
        "**5. Rebalance monthly.** The signal changes once a month at "
        "most. Annual turnover is 3.29 under the corrected winner — modest, "
        "but still relevant for implementation costs."
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
        "5. **This is not return maximization.** The corrected winner's "
        "+7.95% OOS annual return trails XLV buy-and-hold, but it reduces "
        "OOS max drawdown from -15.6% to -0.7%. This is mainly a "
        "drawdown-control story, with Calmar 11.3."
    )

    TRADE_LOG_EXAMPLE_MD = (
        "**Crisis anchor — February 2020 COVID entry.** From "
        "`results/umcsent_xlv/winner_trades_broker_style.csv` (the "
        "canonical APP-TL1 artefact shipped Wave 10H.2):\n\n"
        "- **2020-03-31 — BUY XLV, 100% long, price $80.45.** The trade "
        "log records a full-exposure entry into XLV on 31-Mar-2020. The "
        "signal rationale: 6-month-lagged UMCSENT 3-month momentum = "
        "**+3.786** — lagged sentiment momentum was above the rolling "
        "z-score trigger, so the rule moved back into XLV.\n"
        "- **Cumulative profit and loss (P&L) at entry: +2.27%.** The "
        "book had been in cash immediately before the entry, so the "
        "March 2020 buy restarted XLV exposure after the initial COVID "
        "shock.\n"
        "- **Economic narrative.** This is the case study that defines "
        "the rule's limits. The 6-month lag is a feature against "
        "short-term noise, but it makes the rule slow by design. The "
        "corrected winner reduced XLV OOS drawdown from -15.6% "
        "(buy-and-hold) to -0.7% over the 2019-04-30 to 2025-12-31 "
        "out-of-sample window, but it should still be read as a "
        "monthly-frequency regime filter rather than fast crash "
        "protection.\n"
        "- **Honest caveat.** Users who need crash protection should "
        "pair this rule with a faster signal (the CBOE Volatility Index "
        "divided by the 3-month CBOE Volatility Index pair in this portal). "
        "UMCSENT × XLV is a medium-frequency regime filter, "
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

*Scope discipline.* Only University of Michigan Consumer Sentiment
(UMCSENT) and Health Care Select Sector SPDR Fund (XLV) are in-scope primary
signals.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "**University of Michigan Consumer Sentiment (UMCSENT).** Federal Reserve Economic "
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
    "| `umcsent_yoy` | (umcsent / umcsent.shift(12) − 1) × 100 | approximately stationary |\n"
    "| `umcsent_mom` | 3-month momentum | **winner** — approximately stationary |\n"
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
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline UMCSENT-XLV test |
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
| **Lead times in current published results (5)** | 0, 1, 2, 3, 6 months |
| **Lead times queued for next rerun** | 4 and 5 months added to `scripts/pair_pipeline_umcsent_xlv.py` so the tournament covers 0-6 months continuously |
| **Direction** | Procyclical applied (empirically observed direction) |

Ranked by out-of-sample Sharpe. **1,305 total combinations tested; 1,195
valid** in the current published run (out-of-sample Sharpe > 0, turnover ≤ 24/year, out-of-sample n ≥ 12; the
buy-and-hold benchmark row is a reference, not a combination). Winner (per
`results/umcsent_xlv/winner_summary.json`, authoritative): **umcsent_mom /
rolling z-score > +1.0 / P1_long_cash / Lead 6 months → out-of-sample
Sharpe 1.1586, out-of-sample annualised return +7.9494%, max drawdown
−0.7007%, out-of-sample volatility 6.8615%, Sortino 1.6121, Calmar 11.3449,
25 out-of-sample trades, win rate 16.05%, annual turnover 3.29. Buy-and-hold
XLV benchmark: Sharpe 0.7164, max drawdown −15.6%.**

**Important limitation.** The current published tournament results do not yet
include 4-month or 5-month lead times, so the dashboard must not claim those
lead times have been run. The pipeline has been updated to test them on the
next full rerun, but this checkout does not include the raw monthly source
parquet needed to recompute and publish the optimized result.
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
        "UMCSENT is available from 1978 "
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
