"""crude_oil_xle pair configuration (Rule APP-PT1).

Pair-specific narrative content for the Story / Evidence / Strategy /
Methodology templates. All prose sourced from
`docs/portal_narrative_crude_oil_xle.md` (Ray, 2026-06-02).

Authored under LEAD-NPB1 Mode 2 build by Lead Lesandro wearing the Ace hat.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: When Crude Gets Choppy, Energy Stocks Pay"
    PAGE_SUBTITLE = (
        "Can the shape of oil prices — calm vs choppy — help time energy-sector exposure?"
    )

    HEADLINE_H2 = (
        "## Oil-price volatility regime as a timing signal for XLE"
    )

    PLAIN_ENGLISH = (
        "Energy stocks rise and fall with the price of oil. That's mostly mechanical "
        "— oil companies make money selling barrels, so the share price tracks the "
        "barrel price. This research asks a different question: can the SHAPE of oil "
        "prices — calm vs choppy, drifting vs sprinting — tell us when energy stocks "
        "are a better-than-usual bet?\n\nWe tested twelve simple rules built on WTI "
        "crude prices and asked which one, if any, beat the obvious alternative of "
        "buying-and-holding XLE. The data picked a rule that surprised us: invest in "
        "XLE when oil prices have been unusually volatile for the past quarter, sit "
        "out otherwise. Out of sample (2015–2025), that rule earned a Sharpe of about "
        "0.47, while just holding XLE earned around 0.04."
    )

    WHERE_THIS_FITS = (
        "This is one indicator-target analysis — we ask whether WTI crude price "
        "behaviour can help time exposure to XLE (the Energy Select Sector SPDR). "
        "XLE is concentrated in oil-and-gas majors, so the contemporaneous link to "
        "crude is mechanical. The interesting question is whether the link's STRENGTH "
        "or DIRECTION shifts with crude's recent behaviour."
    )

    ONE_SENTENCE_THESIS = (
        "When WTI realized volatility sits in the top quartile of its 5-year "
        "history, XLE's risk-adjusted return tends to be elevated — and a simple "
        "rule that switches between long-XLE and cash on that signal beats "
        "buy-and-hold out-of-sample."
    )

    KPI_CAPTION = (
        "the tournament winner uses WTI's 13-week realized volatility as a regime "
        "indicator. When that volatility is in the top quartile of its trailing "
        "5-year window, we hold XLE; otherwise we sit in cash."
    )

    HERO_TITLE = "WTI Crude vs XLE — full sample (weekly, 1998–2025)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — WTI crude price (left axis, vermillion) "
        "and XLE share price (right axis, blue) on a common time axis. NBER "
        "recession bands shaded. Notice the close co-movement at low frequency "
        "and the volatility clustering around the 2008 / 2014–2016 / 2020 / 2022 "
        "episodes."
    )

    REGIME_TITLE = "What History Shows: XLE Forward Returns by WTI Volatility Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: mean 13-week forward XLE return conditioned on WTI's "
        "13-week realized-volatility quartile. The right tail (Q4 — high vol) shows "
        "the most elevated mean forward return — the regime the winning rule "
        "exploits. Error bars show standard error of the mean within each bucket."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "label": "Dot-com bust (2000-2002)",
            "title": "Dot-com bust (2000-2002)",
            "caption": "WTI and XLE during the 2001 dot-com bust.",
            "narrative": (
                "The 2001 dot-com bust did not strongly impair WTI or XLE because oil "
                "fundamentals were not the centre of the shock — equity exuberance was. "
                "WTI traded sideways through 2001; XLE was relatively flat."
            ),
        },
        {
            "slug": "gfc",
            "label": "Global Financial Crisis (2007-2009)",
            "title": "Global Financial Crisis (2007-2009)",
            "caption": "WTI and XLE during the 2008-2009 Global Financial Crisis.",
            "narrative": (
                "The 2008 GFC broke both series violently. WTI ran from ~$60 to $145 "
                "in mid-2008, then collapsed to $35 by year-end. XLE tracked the collapse "
                "closely. This is the canonical co-crash and the largest single drawdown "
                "in the sample."
            ),
        },
        {
            "slug": "covid",
            "label": "COVID shock (2020)",
            "title": "COVID shock (2020)",
            "caption": "WTI and XLE through the 2020 COVID shock.",
            "narrative": (
                "March-April 2020 saw the most extreme single episode in the sample: "
                "WTI futures briefly traded negative on 2020-04-20 (storage capacity "
                "shock), and XLE fell roughly 50% peak-to-trough. The series recovered "
                "unevenly through 2020 H2; XLE lagged WTI's recovery."
            ),
        },
        {
            "slug": "inflation_2022",
            "label": "2022 inflation / Ukraine cycle",
            "title": "2022 inflation / Ukraine cycle",
            "caption": "WTI and XLE during the 2022 inflation and Russia-Ukraine cycle.",
            "narrative": (
                "The 2022 inflation cycle and Russia's invasion of Ukraine pushed WTI "
                "back above $120/bbl in early 2022. XLE rallied strongly through "
                "mid-2022 then drifted as crude retraced. This episode is the clearest "
                "example in the sample of WTI volatility correlating with elevated XLE "
                "risk-adjusted return — and is one of the periods in which the winning "
                "rule was active."
            ),
        },
    ]

    NARRATIVE_SECTION_1 = (
        "Energy stocks and crude oil prices move together at high frequency because "
        "XLE constituents earn revenue in barrels. The contemporaneous Pearson "
        "correlation between WTI weekly log returns and XLE weekly log returns is "
        "approximately 0.55 across the 1998-2025 sample. This study does not try to "
        "beat that contemporaneous link — it asks whether the RECENT behaviour of "
        "WTI (its volatility, momentum, position in cycle) carries enough information "
        "to time XLE one week ahead in a way that beats simple buy-and-hold."
    )

    NARRATIVE_SECTION_2 = (
        "The winning rule's mechanism is NOT 'more vol = more upside.' It is: the "
        "rule selects out periods when XLE's risk-adjusted return is more likely to "
        "be elevated, conditional on what's been happening in the underlying "
        "commodity. The selection criterion is regime-based, not return-based."
    )

    SCOPE_NOTE = (
        "Sample 1998-12-22 to 2025-10-10. Weekly frequency (Friday close). "
        "WTI from FRED `WCOILWTICO`, XLE from `etf_prices` sheet. 60/40 IS/OOS "
        "split."
    )


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: Long XLE in High-Vol Crude Regimes"
    PAGE_SUBTITLE = "Twelve candidates were tested; one beat buy-and-hold meaningfully."

    PLAIN_ENGLISH = (
        "The rule is simple: each Friday, check whether the past three months of "
        "WTI crude have been unusually choppy by historical standards. If they have "
        "(top quartile of the past five years), hold XLE for the coming week. "
        "Otherwise, sit in cash. Out-of-sample (2015-2025) this rule earned a "
        "Sharpe ratio of about 0.47 versus 0.04 for simply holding XLE the whole "
        "time — and with smaller drawdowns. It fires about four times per year."
    )

    SIGNAL_RULE_MD = (
        "**Each Friday close:** compute WTI's 13-week realized volatility and "
        "rank it within its trailing 5-year history (260-week percentile rank, "
        "minimum 52 weeks of history). If the rank is **above the 75th percentile**, "
        "hold XLE for the coming week. Otherwise, hold cash."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "1. From WTI weekly log returns, compute the rolling 13-week standard "
        "deviation. Annualise by √52.\n"
        "2. For each week, compute the percentile rank of the current vol against "
        "the trailing 260 weeks (5 years) of vol.\n"
        "3. The signal is `rank > 0.75`.\n"
        "4. Position translation: signal True → +1 (long XLE); signal False → 0 "
        "(cash). Position is shifted by one week to avoid look-ahead.\n"
        "5. Costs: 5 basis points per unit of |Δposition|."
    )

    MANUAL_USE_MD = (
        "An end-user wanting to apply this rule manually can pull WCOILWTICO from "
        "FRED weekly, compute 13-week annualised vol, compare to the rolling 5-year "
        "distribution, and adjust position once per week. The rule fires roughly "
        "four times per year on average."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"

    CAVEATS_MD = (
        "- The rule was selected by maximum OOS Sharpe across 12 candidates. "
        "Multiple-comparisons risk is real; treat 0.47 as an upper bound on "
        "out-of-sample expectation.\n"
        "- Annual turnover ≈ 3.7. Costs above ~25 bps per leg would meaningfully "
        "erode the edge.\n"
        "- Not tested on pre-1998 crude regimes (XLE didn't exist) or on the "
        "energy-transition regime that may emerge post-2025.\n"
        "- The rule has no theoretical basis stronger than 'this is what the data "
        "showed in this window.' Treat it accordingly."
    )

    TRADE_LOG_EXAMPLE_MD = (
        "The broker-style trade log below lists each individual entry/exit pair "
        "over the OOS window (2015-2025). Each row shows entry date, exit date, "
        "side, symbol, quantity (notional 100 shares), entry/exit prices in USD, "
        "and trade P&L as a percentage of notional."
    )


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Series | Source | Frequency | Units | Sample |
|---|---|---|---|---|
| WTI crude oil price | FRED `WCOILWTICO` (cached in `data/Data Master.xlsx`) | Weekly | USD per barrel, NSA | 1986-01-03 → 2025-10-10 |
| XLE total return | `data/Data Master.xlsx` sheet `etf_prices` col XLE | Daily | USD | 1998-12-22 → 2025-10-23 |

XLE was resampled to weekly-Friday close to align with WTI's native frequency.
Joint sample 1998-12-22 to 2025-10-10 (1,400 weekly observations).
"""

_METHODS_TABLE_MD = """
| Level | Method | Notes |
|---|---|---|
| L1 | Pearson + Spearman correlation | Contemporaneous and lead-lag at 0..8 weeks |
| L1 | OLS lead-lag regressions | HC3 robust SE |
| L1 | ADF + KPSS stationarity tests | On every constructed feature |
| L2 | Rolling 52-week correlation | For regime visualization |
| L2 | CUSUM of recursive residuals | Structural break detection |
| L3 | Regime tournament | 12 strategy families, IS/OOS Sharpe ranking |
"""

_TOURNAMENT_DESIGN_MD = """
- **Universe:** 12 strategy families (momentum × 3 horizons, z-score × 4 entries,
  vol regime × 2 entries, long-short sign × 3 signals).
- **Split:** 60% in-sample / 40% out-of-sample by calendar.
- **Selection:** maximum OOS Sharpe via `scripts/tournament.py::select_winner`.
- **Cost model:** 5 bps per unit of |Δposition|, applied to each weekly return.
- **Benchmark:** XLE buy-and-hold over the same OOS window.
"""

_INDICATOR_CONSTRUCTION_MD = """
**WTI realized vol percentile (the winning signal):**

1. WTI weekly log return: `r_t = log(P_t / P_{t-1})`
2. 13-week realized vol, annualised: `σ_t = std(r_{t-12..t}) × √52`
3. 5-year rolling percentile rank: `q_t = rank(σ_t) in {σ_{t-259..t}}`
4. Signal: `s_t = (q_t > 0.75)`
5. Position: `pos_t = s_{t-1}` (one-week lag to avoid look-ahead)

Minimum periods for the percentile rank is 52 weeks, so the signal is
available from approximately 1999-12-31 onward.
"""

_REFERENCES_MD = """
- WTI crude reference: U.S. Energy Information Administration, *Weekly U.S.
  All Grades All Formulations Retail Gasoline Prices* — and FRED's
  `WCOILWTICO` series (weekly average West Texas Intermediate spot price).
- XLE composition: SSGA *Energy Select Sector SPDR Fund Prospectus*.
- Vol-regime literature: Hamilton (1989, 'A New Approach to the Economic
  Analysis of Nonstationary Time Series and the Business Cycle');
  Ang & Bekaert (2002, 'International Asset Allocation with Regime Shifts').
- Multiple-testing in strategy selection: Harvey & Liu (2014, '... and the
  Cross-Section of Expected Returns').
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    references_md=_REFERENCES_MD,
    sample_period_note="Joint sample 1998-12-22 to 2025-10-10. IS: first 60% (≈ 1998-12 to 2014-12). OOS: last 40% (2015-01 to 2025-10).",
)


# =========================================================================
# EVIDENCE PAGE METHOD BLOCKS
# =========================================================================
EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "*Twelve strategy candidates were tested out-of-sample (2015-2025) against "
        "an XLE buy-and-hold benchmark. The exploratory analysis confirms a strong "
        "contemporaneous link between WTI and XLE; the question is whether anything "
        "in WTI's recent past predicts XLE's near future.*"
    ),
    "plain_english": (
        "This section shows the statistical evidence behind the strategy. Correlation "
        "tests confirm that WTI and XLE move together at high frequency — about 0.55 "
        "Pearson on weekly returns. Lead-lag regressions show most of the relationship "
        "is contemporaneous (lag 0) with modest predictive power at lags 1-2 weeks. "
        "The structural-break test (CUSUM) shows the relationship is not constant "
        "across the sample — there are real regime shifts around 2008 and 2014. "
        "The regime-buckets test, conditioning on WTI's realized-volatility quartile, "
        "shows the cleanest pattern — high-vol regimes coincide with elevated XLE "
        "forward returns. This is the conditioning the winning strategy exploits."
    ),
    "level1": [
        {
            "id": "correlation",
            "method_name": "Contemporaneous correlation",
            "method_theory": (
                "Pearson correlation measures linear co-movement between two return "
                "series in the same period. A high contemporaneous correlation says "
                "the two series wiggle together."
            ),
            "question": (
                "Do WTI weekly log returns and XLE weekly log returns move together "
                "in the same week?"
            ),
            "how_to_read": (
                "ρ near +1 = strong co-movement; ρ near 0 = independent; ρ near -1 = "
                "inverse. Compare the rolling 52-week ρ chart against the long-run mean."
            ),
            "observation": (
                "Pearson ρ ≈ 0.55 across the full 1998-2025 sample. The rolling "
                "52-week ρ ranges from ~0.30 in calm regimes to ~0.85 in shock periods."
            ),
            "interpretation": (
                "The mechanical link is strong and stable in sign. XLE constituents' "
                "revenue is denominated in oil; same-week returns share most of their "
                "variance."
            ),
            "key_message": (
                "Same-week prediction is not the goal of this study. The interesting "
                "question is whether RECENT past WTI behaviour predicts NEXT WEEK's "
                "XLE return."
            ),
            "chart_name": "rolling_correlation",
        },
        {
            "id": "lead_lag",
            "method_name": "Lead-lag regressions",
            "method_theory": (
                "Lead-lag OLS regresses one series on lagged values of another. "
                "Significant non-zero-lag coefficients are evidence of temporal "
                "predictability beyond contemporaneous correlation."
            ),
            "question": (
                "Does WTI's return at week t-k predict XLE's return at week t, for "
                "k = 0..8?"
            ),
            "how_to_read": (
                "Look for non-trivial R² at lags > 0 with p-values < 0.05. R² at "
                "lag 0 just confirms contemporaneous correlation; R² at lag 1+ is "
                "the predictive content."
            ),
            "observation": (
                "Maximum R² at lag 0 (~0.30). R² decays smoothly with increasing lag. "
                "Coefficients significant at lags 0-2; insignificant beyond lag 4."
            ),
            "interpretation": (
                "Most of the WTI→XLE information is contemporaneous. There is modest "
                "predictive power at short lags but not enough on its own to drive "
                "a robust trading rule."
            ),
            "key_message": (
                "Simple lagged regression won't beat buy-and-hold. The tournament tests "
                "richer signal constructions to find what does."
            ),
            "chart_name": "rolling_correlation",
        },
        {
            "id": "stationarity",
            "method_name": "ADF + KPSS stationarity tests",
            "method_theory": (
                "ADF tests the null of a unit root (non-stationary); KPSS tests the "
                "null of stationarity. The two together (joint conclusion) give a more "
                "robust verdict than either alone."
            ),
            "question": (
                "Are the constructed signal features stationary, i.e. safe to use in "
                "regression and rule-based strategies?"
            ),
            "how_to_read": (
                "ADF p < 0.05 rejects unit-root (good). KPSS p > 0.05 fails to reject "
                "stationarity (good). When the two agree on stationarity, the feature "
                "is usable as-is."
            ),
            "observation": (
                "Levels (WTI, XLE) are non-stationary as expected. All derived signals "
                "(log returns, z-scores, vol percentiles) test stationary by both ADF "
                "and KPSS at standard significance."
            ),
            "interpretation": (
                "The tournament's signal universe is built on stationary derived "
                "features, so the OOS results are not spuriously driven by trending "
                "data."
            ),
            "key_message": (
                "Tests pass; the analytical pipeline rests on stationary inputs."
            ),
            "chart_name": "rolling_correlation",
        },
    ],
    "level1_labels": ["Correlation", "Lead-Lag", "Stationarity"],
    "level2": [
        {
            "id": "structural_break",
            "method_name": "CUSUM of recursive residuals",
            "method_theory": (
                "Recursive-residuals CUSUM tracks the cumulative sum of out-of-sample "
                "residuals as the OLS fit extends through time. Sustained departures "
                "from zero suggest the relationship has shifted."
            ),
            "question": (
                "Is the WTI-XLE return relationship stable across the sample, or "
                "does it shift in regime?"
            ),
            "how_to_read": (
                "Departures of the CUSUM line from zero are evidence of regime "
                "instability. The 95% bounds (not plotted) would be exceeded at "
                "p = 0.05."
            ),
            "observation": (
                "CUSUM departs from zero around 2008-2009 and 2014-2016, consistent "
                "with the GFC oil collapse and the 2014-2016 shale-glut regime shift."
            ),
            "interpretation": (
                "The contemporaneous WTI-XLE beta is not constant. A regime-aware "
                "rule is more likely to be robust than a single-state OLS."
            ),
            "key_message": (
                "Static models are mis-specified for this pair. Regime conditioning "
                "is the right primitive."
            ),
            "chart_name": "structural_break",
        },
        {
            "id": "regime_buckets",
            "method_name": "Vol-regime conditioning of forward returns",
            "method_theory": (
                "Conditioning a forward return on a regime variable (here, WTI's "
                "13-week realized-volatility quartile) tests whether the regime "
                "carries predictive content."
            ),
            "question": (
                "Does XLE's 13-week forward return vary systematically with WTI's "
                "current realized-volatility quartile?"
            ),
            "how_to_read": (
                "Bar height = mean 13-week forward return in each bucket. Error bars "
                "show standard error of the mean. Look for monotonic or extreme-tail "
                "patterns."
            ),
            "observation": (
                "Mean forward XLE return is highest in Q4 (top vol quartile) and "
                "lowest in Q1 (bottom vol quartile). The gradient is monotonic."
            ),
            "interpretation": (
                "When crude is choppy, energy equities tend to deliver higher "
                "subsequent returns. The mechanism is not pinned down (option-premium "
                "compression, risk-premium expansion, momentum) but the empirical "
                "pattern is robust."
            ),
            "key_message": (
                "This conditioning is the basis of the winning strategy rule "
                "`wti_high_vol_long`."
            ),
            "chart_name": "regime_stats",
        },
    ],
    "level2_labels": ["Structural Break", "Regime Conditioning"],
    "tournament_intro": (
        "Twelve strategy families were enumerated across momentum (3 horizons), "
        "z-score (4 entry variants), volatility regime (2 entries), and long-short "
        "sign (3 signals). Each was scored by out-of-sample Sharpe ratio over "
        "2015-2025. The winning combination — `wti_high_vol_long` with rank > 0.75 "
        "in a 5-year rolling vol-percentile window — earned OOS Sharpe ≈ 0.47 vs "
        "0.04 buy-and-hold XLE."
    ),
    "transition": (
        "**Transition:** the evidence supports a regime-conditional timing rule. "
        "Now: what does the winning strategy actually do, and how has it performed?"
    ),
    "level3": [
        {
            "id": "tournament",
            "method_name": "Strategy tournament",
            "method_theory": (
                "A tournament enumerates strategy families, scores each on identical "
                "out-of-sample data, and ranks. It is honest about multiple-comparisons "
                "risk and produces an upper-bound estimate of out-of-sample expectation."
            ),
            "question": (
                "Of 12 simple WTI-based strategy families, which beats XLE buy-and-hold "
                "out-of-sample, and by how much?"
            ),
            "how_to_read": (
                "Scatter plot of IS Sharpe (x) vs OOS Sharpe (y). Top-right quadrant = "
                "strategies that worked in both. Top-left = OOS overfits luck. "
                "Bottom-right = OOS deteriorated."
            ),
            "observation": (
                "Winner `wti_high_vol_long` (OOS Sharpe ≈ 0.47). Seven of 12 strategies "
                "have positive OOS Sharpe; five are net negative."
            ),
            "interpretation": (
                "The signal is genuine but not dominant — most simple rules fail to "
                "beat buy-and-hold. The winner exploits a regime conditioning, not "
                "return-following."
            ),
            "key_message": (
                "A regime-conditional timing rule beats the passive XLE benchmark by "
                "a meaningful risk-adjusted margin out-of-sample."
            ),
            "chart_name": "tournament_scatter",
        },
    ],
}


# =========================================================================
# Module-level exports for thin-wrapper page files (APP-PT1)
# =========================================================================
STORY_CONFIG = StoryConfig()
STRATEGY_CONFIG = StrategyConfig()
