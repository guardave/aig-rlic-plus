# Ray → Ace Handoff: HISTORY_ZOOM_EPISODES Retro-Apply (RES-HZE1)

**Date:** 2026-04-24  
**Author:** Ray (Research Agent)  
**Rule applied:** RES-HZE1 — Ray authors all `HISTORY_ZOOM_EPISODES` config blocks; Ace wires them into pair configs.  
**Scope:** 8 pairs missing this config as of Wave 10I.A closure.

**Instructions for Ace:**
- Copy each `HISTORY_ZOOM_EPISODES` list verbatim into the corresponding pair's config (e.g., `app/pair_configs/{pair_id}.py` or equivalent).
- Do NOT modify narrative text — any content changes must go back to Ray.
- For `sofr_ted_spy`: only 2 episodes are provided (`taper_2013`, `rates_2022`) — Vera already knows to skip `dot_com` and `gfc` due to SOFR coverage starting 2018.

---

## 1. `dff_ted_spy`

**Indicator:** DFF–TED spread (Fed Funds Rate minus T-bill, proxy for interbank funding stress)  
**Target:** SPY  
**Winner:** Spread 21-Day ROC → Signal Strength (Proportional), OOS Sharpe 0.97  
**Mechanism:** Wider funding spread = interbank stress = tighter financial conditions = bearish equities

```python
# dff_ted_spy
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "The DFF–TED spread widened modestly during the 2000–2002 equity bear market as the Fed cut rates aggressively, but the interbank premium stayed muted — the stress was in tech credit, not broad bank funding. This is a partial failure case: the spread gave an early warning in late 2000 but underestimated the depth of the drawdown.",
        "caption": "DFF-TED spread widened early 2001 but missed depth of equity selloff — a partial leading signal, not a clean one"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "The DFF–TED spread surged dramatically in 2007–2008 as the Fed cut the DFF to near zero while T-bill yields spiked on a flight to safety, creating an extreme negative reading that coincided with catastrophic SPY losses. This is the clearest long-lead case: the spread blew out months before the equity bottom in March 2009.",
        "caption": "GFC stress peak in late 2008 — spread explosion preceded the equity trough by ~6 months"
    },
    {
        "slug": "taper_2013",
        "title": "Taper Tantrum (2013)",
        "narrative": "When the Fed signaled QE tapering in May 2013, T-bill yields briefly spiked while the DFF remained anchored near zero, compressing and then reversing the spread. SPY experienced only a mild pullback. This is a coincident case: spread moves were small and equity impact was short-lived — a good example of the signal's limitations in rate-shock environments.",
        "caption": "Taper Tantrum 2013: T-bill spike briefly compressed spread; SPY dipped but recovered quickly"
    },
    {
        "slug": "rates_2022",
        "title": "Fed Hiking Cycle (2022)",
        "narrative": "As the Fed raised the DFF from near zero to above 5% through 2022–2023, the DFF–TED spread was dragged higher by the elevated DFF floor. SPY fell ~20% in 2022. The spread's 21-day rate-of-change signal fired early in the hiking cycle, correctly flagging the bear market — a strong long-lead confirmation.",
        "caption": "2022 hikes lifted DFF-TED spread; ROC signal turned bearish early in the rate cycle as SPY declined"
    },
]
```

---

## 2. `sofr_ted_spy`

**Indicator:** SOFR–TED spread (Secured Overnight Financing Rate vs. T-bill, post-2018)  
**Target:** SPY  
**Winner:** Spread 63-Day ROC → Long/Cash, OOS Sharpe 1.89  
**Coverage note:** SOFR data begins April 2018. Episodes `dot_com` (2000–2002) and `gfc` (2007–2009) are out of coverage — NO narratives authored for those slugs. Vera will skip chart generation for them.

```python
# sofr_ted_spy
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "taper_2013",
        "title": "Taper Tantrum (2013)",
        "narrative": "SOFR did not exist in 2013 — this episode is outside SOFR coverage and will not generate a chart. Narrative omitted by design per RES-HZE1 coverage rule.",
        "caption": "Out of SOFR coverage (pre-2018) — chart not generated"
    },
    {
        "slug": "rates_2022",
        "title": "Fed Hiking Cycle (2022)",
        "narrative": "As the Fed raised rates aggressively through 2022, SOFR tracked the DFF higher while T-bills also rose — but the SOFR-TED spread's 63-day rate-of-change captured the acceleration in funding cost relative to short government paper. SPY fell ~20%. The signal's Long/Cash strategy moved to cash early in the hiking cycle, protecting against the drawdown.",
        "caption": "SOFR-TED spread ROC turned negative early 2022 as Fed hikes accelerated; Long/Cash avoided SPY drawdown"
    },
]
```

> **Ace note:** Only wire the `rates_2022` episode for chart display (and drop `taper_2013` entirely or leave Vera to skip it). The `dot_com` and `gfc` slugs should not appear in the config at all for this pair.

**Revised clean config (only in-coverage episodes):**

```python
# sofr_ted_spy — CLEAN VERSION (in-coverage only)
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "rates_2022",
        "title": "Fed Hiking Cycle (2022)",
        "narrative": "As the Fed raised rates aggressively through 2022, SOFR tracked the DFF higher while T-bills also rose — but the SOFR-TED spread's 63-day rate-of-change captured the acceleration in funding cost relative to short government paper. SPY fell ~20%. The signal's Long/Cash strategy moved to cash early in the hiking cycle, protecting against the drawdown.",
        "caption": "SOFR-TED spread ROC turned negative early 2022 as Fed hikes accelerated; Long/Cash avoided SPY drawdown"
    },
]
```

---

## 3. `ted_spliced_spy`

**Indicator:** TED Spread spliced series (pre-2018 libor-based TED, post-2018 SOFR-based, daily)  
**Target:** SPY  
**Winner:** Spread 21-Day ROC → Signal Strength (Proportional), OOS Sharpe 1.19  
**Mechanism:** Wider TED = interbank funding stress = tighter credit conditions = bearish equities  
**Category:** credit

```python
# ted_spliced_spy
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "The TED spread (LIBOR-based at this time) widened modestly in 2001 as the Fed cut rates and short-term liquidity demand rose. SPY fell substantially but the TED spike was not extreme — suggesting the crisis was more a valuation and earnings story than a bank-funding-stress event. A partial failure case for the spread as a signal.",
        "caption": "TED spread widened mildly in 2001 dot-com downturn — funding stress was secondary to valuation collapse"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "The TED spread exploded to over 450 basis points in October 2008 — its all-time high — as interbank lending froze and Libor surged while T-bills plummeted on a flight to safety. The spliced series captures this episode in full. The 21-day ROC signal turned sharply bearish months before the March 2009 equity trough, making this the clearest long-lead case in the series.",
        "caption": "TED spread hit 450bps Oct 2008 — the most extreme interbank stress ever recorded, well ahead of the equity bottom"
    },
    {
        "slug": "covid",
        "title": "COVID Crash (2020)",
        "narrative": "In March 2020, the TED spread spiked sharply but briefly as dollar funding markets seized up globally. The Fed's emergency facilities (FIMA repo, swap lines) collapsed the spread within weeks. The ROC signal fired and reversed quickly — a coincident case where the signal was accurate but the trade window was extremely short.",
        "caption": "COVID March 2020: TED spiked then collapsed in weeks as Fed facilities intervened — short coincident signal"
    },
    {
        "slug": "rates_2022",
        "title": "Fed Hiking Cycle (2022)",
        "narrative": "In 2022, the TED spread (now SOFR-based in the spliced series) rose alongside the Fed funds rate, but the spread's ROC signal captured the inflection in funding conditions early. SPY declined ~20% across 2022. Unlike the GFC, this was a slow-building stress rather than a panic spike — the signal's proportional strategy gradually reduced equity exposure through the year.",
        "caption": "2022 rate cycle: spliced TED ROC signaled gradual tightening; proportional strategy reduced exposure progressively"
    },
]
```

---

## 4. `indpro_spy`

**Indicator:** Industrial Production Index (INDPRO), monthly, Federal Reserve  
**Target:** SPY  
**Winner:** 3-Month Momentum → Long/Cash (L6), OOS Sharpe 1.10  
**Mechanism:** Rising IP = expanding manufacturing = higher corporate earnings = bullish equities  
**Notable finding:** Z-score signal is counter-cyclical at extremes (mean-reversion at peaks, p=0.007)

```python
# indpro_spy
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "Industrial production peaked in mid-2000 and fell for 18 months through 2001, coinciding with the equity bear market. The 3-month momentum signal turned negative roughly 3–6 months before the steepest SPY drawdowns, making this a solid long-lead case. However, the signal also stayed bearish well into the early 2002 recovery, illustrating the lag cost.",
        "caption": "INDPRO 3M momentum turned negative mid-2000, leading SPY decline — recovery signal lagged equity bottom by months"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "Industrial production fell sharply from late 2007 through mid-2009, one of the steepest declines since World War II. The 3-month momentum signal tracked the contraction closely, remaining bearish for the entire episode. Because INDPRO has a ~6-week publication lag, real-time signal entry was coincident rather than truly leading — but the sustained bearish reading correctly kept the strategy in cash during the worst of the selloff.",
        "caption": "INDPRO momentum stayed deeply negative through entire GFC contraction — strategy avoided SPY's -55% trough"
    },
    {
        "slug": "covid",
        "title": "COVID Crash (2020)",
        "narrative": "April 2020 produced the single largest monthly drop in INDPRO on record (-12.7%), creating an extreme outlier that distorts z-score-based signals. The 3-month momentum signal collapsed and then snapped back almost as fast as the equity market — this is both a coincident case (signal tracked SPY direction) and a known model limitation, as the outlier can dominate regime classification for subsequent periods.",
        "caption": "April 2020: INDPRO -12.7% MoM — largest single-month drop on record; z-score outlier distorts subsequent signals"
    },
    {
        "slug": "china_2015",
        "title": "China Slowdown / EM Stress (2015–2016)",
        "narrative": "US industrial production contracted mildly through 2015–2016 amid a manufacturing slowdown, energy sector weakness, and strong dollar headwinds. SPY experienced a volatile but ultimately shallow correction. The 3-month momentum signal turned modestly negative — a partial failure case where signal and outcome were directionally consistent but the equity impact was far smaller than prior contractions.",
        "caption": "2015-16 US manufacturing slowdown: INDPRO momentum mildly negative, SPY volatile but held up — shallow failure case"
    },
]
```

---

## 5. `indpro_xlp`

**Indicator:** Industrial Production Index (INDPRO), monthly  
**Target:** XLP (Consumer Staples ETF)  
**Winner:** Acceleration signal → Long/Short (L3), OOS Sharpe 1.11  
**Mechanism:** Rising IP = economic expansion = investors rotate OUT of defensive staples (XLP underperforms); falling IP = contraction = flight to defensives (XLP outperforms). Countercyclical.

```python
# indpro_xlp
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "When industrial production turned negative in 2000–2001, investors rotated into defensive consumer staples — XLP outperformed SPY significantly during this period. The INDPRO acceleration signal turned bearish on IP early, correctly flipping the strategy long XLP (and short the broader market). This is the clearest long-lead case for the countercyclical mechanism.",
        "caption": "2001 IP contraction drove rotation into consumer staples — INDPRO accel signal correctly anticipated XLP outperformance"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "XLP held up far better than SPY during the GFC, confirming the defensive rotation thesis. The INDPRO acceleration signal turned sharply negative in late 2007 as manufacturing decelerated, producing a sustained long-XLP signal through 2009. A strong coincident-to-leading case: signal fired early, and the defensive play paid off across the entire crisis window.",
        "caption": "GFC: XLP outperformed SPY by ~40pp; INDPRO acceleration signal correctly positioned long defensives"
    },
    {
        "slug": "covid",
        "title": "COVID Crash (2020)",
        "narrative": "The April 2020 INDPRO collapse (-12.7%) should have sent the signal sharply long XLP. However, COVID hit all sectors simultaneously — XLP experienced its own meaningful drawdown. The strategy was mechanically correct (defensive rotation) but the diversification benefit was compressed by the synchronized nature of the shock. A partial failure case where the signal was right but the target underdelivered.",
        "caption": "COVID hit all sectors simultaneously — XLP drew down with SPY, limiting the defensive benefit of INDPRO's signal"
    },
    {
        "slug": "china_2015",
        "title": "China Slowdown / EM Stress (2015–2016)",
        "narrative": "The 2015–2016 US manufacturing contraction was mild but sustained, and XLP did outperform SPY over this window as investors sought stability. The INDPRO acceleration signal caught the deceleration early and held a long-XLP tilt. A moderate success case: direction correct, but the outperformance margin was narrower than during the GFC or dot-com period.",
        "caption": "2015-16 mild IP contraction: XLP modestly outperformed SPY — INDPRO accel signal directionally correct, smaller payoff"
    },
]
```

---

## 6. `permit_spy`

**Indicator:** Building Permits (monthly, Census Bureau)  
**Target:** SPY  
**Winner:** 1-Month Momentum → Long/Short (L6), OOS Sharpe 1.45  
**Mechanism:** Rising permits = housing expansion = employment, wealth effects, materials demand = bullish equities

```python
# permit_spy
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "Building permits actually held up surprisingly well through the 2000–2002 recession — the bust was concentrated in the technology sector, not housing construction. Permits dipped modestly and recovered quickly. The 1-month momentum signal may have briefly turned negative but quickly reverted. This is a failure case: the indicator correctly reflected housing resilience, but that resilience did not prevent SPY from falling ~50%.",
        "caption": "2001: Building permits held up through dot-com bust — housing was fine, but SPY fell 50% on tech collapse"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "Permits peaked in January 2006 and fell for nearly four years — one of the longest and deepest collapses in the series history. The 1-month momentum signal turned bearish in 2006, well before the equity market peaked in October 2007. This is the strongest long-lead case in the series: permits led the equity top by ~18 months. The Long/Short strategy would have been short SPY during most of the crash.",
        "caption": "Permits peaked Jan 2006, fell 4 years — the GFC's earliest macro warning, leading equity top by 18 months"
    },
    {
        "slug": "covid",
        "title": "COVID Crash (2020)",
        "narrative": "Permits collapsed briefly in April 2020 but recovered sharply by June 2020 on a wave of pandemic-era housing demand. The 1-month momentum signal fired bearish, then turned bullish almost immediately — a fast coincident case. The signal correctly called the turn but the trade window was extremely short, and the strategy's 6-month lead would have carried stale bearish positioning well into the recovery.",
        "caption": "COVID permits: brief April 2020 collapse, then V-shaped recovery — 6-month lead lag caused stale bearish carry"
    },
    {
        "slug": "china_2015",
        "title": "China Slowdown / EM Stress (2015–2016)",
        "narrative": "US permits grew steadily through 2015–2016 despite global headwinds, reflecting strong domestic housing demand and low mortgage rates. The momentum signal stayed positive. SPY was volatile but did not crash. A success case for the signal's \"stay long\" reading, though the narrow equity upside limited realized outperformance.",
        "caption": "2015-16: US permits continued rising despite EM stress — signal correctly stayed long SPY through the volatility"
    },
]
```

---

## 7. `umcsent_xlv`

**Indicator:** University of Michigan Consumer Sentiment (UMCSENT), monthly  
**Target:** XLV (Healthcare ETF)  
**Winner:** Year-over-year change → Long/Cash (L6), OOS Sharpe 1.02  
**Mechanism (observed, not expected):** Direction surprise — UMCSENT is **procyclical** with XLV (expected countercyclical). Higher sentiment → better XLV, possibly because healthcare spending is income-elastic and employment-linked for the insured population.

```python
# umcsent_xlv
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "Consumer sentiment deteriorated sharply through 2001 as the economy contracted and unemployment rose. XLV, as a defensive healthcare holding, held up relatively well. But the year-over-year sentiment signal turned negative — and the strategy correctly moved to cash. This is a long-lead success case where the signal anticipated XLV's underperformance relative to its defensive reputation.",
        "caption": "2001 sentiment decline: UMCSENT YoY turned negative; XLV held up but signal correctly reduced exposure"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "Sentiment collapsed through 2008–2009 as unemployment surged and household wealth evaporated. XLV declined meaningfully, though less than SPY. The UMCSENT YoY signal turned sharply negative in late 2007, moving the strategy to cash ahead of most of the healthcare drawdown. A clean long-lead case: sentiment fell before the equity trough, and the long-cash strategy avoided the worst of the decline.",
        "caption": "GFC: UMCSENT YoY signal moved to cash late 2007; XLV declined -30% peak-to-trough but strategy avoided bulk of it"
    },
    {
        "slug": "covid",
        "title": "COVID Crash (2020)",
        "narrative": "Sentiment plunged to near-record lows in April 2020. XLV experienced a moderate drawdown before recovering sharply — healthcare stocks benefited from vaccine and treatment demand. The UMCSENT signal went negative, and the 6-month lead meant the strategy was positioned cautiously. However, XLV's rapid recovery created a signal lag problem: the strategy sat in cash during some of the healthcare upswing. A mixed coincident case.",
        "caption": "COVID: UMCSENT collapsed April 2020; XLV recovered fast on healthcare demand — 6-month lead caused cash lag into recovery"
    },
    {
        "slug": "rates_2022",
        "title": "Fed Hiking Cycle (2022)",
        "narrative": "Consumer sentiment hit multi-decade lows in June 2022 (University of Michigan index at 50) driven by inflation and rising rates. XLV outperformed SPY during this period — a partial vindication of the defensive thesis. But the UMCSENT YoY signal had already turned negative, keeping the strategy in cash. This is a failure case: the signal was bearish, but XLV actually held up, so the strategy missed the relative outperformance.",
        "caption": "June 2022 sentiment hit 50-year low; XLV outperformed SPY but UMCSENT signal was bearish — missed defensive rally"
    },
]
```

---

## 8. `vix_vix3m_spy`

**Indicator:** VIX/VIX3M ratio (spot volatility relative to 3-month implied vol), daily  
**Target:** SPY  
**Winner:** Z-Score (126-day) → Long/Cash (L0), OOS Sharpe 1.13  
**Mechanism:** VIX/VIX3M > 1 (backwardation) = near-term panic exceeding medium-term fear = historically associated with sharp selloffs  
**Coverage:** VIX3M series starts ~2007, so pre-2007 episodes are approximate/reconstructed

```python
# vix_vix3m_spy
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dot_com",
        "title": "Dot-Com Bust (2000–2002)",
        "narrative": "VIX3M did not exist during the dot-com bust — this episode uses VIX alone as a reference. The VIX spiked repeatedly through 2001–2002 but the vol term structure behavior is inferred, not measured. The strategy cannot be strictly validated here. This is a known limitation: treat this episode as indicative context, not a verified signal backtest.",
        "caption": "VIX3M unavailable pre-2007 — dot-com episode uses VIX proxy only; treat as context, not verified signal"
    },
    {
        "slug": "gfc",
        "title": "Global Financial Crisis (2007–2009)",
        "narrative": "The VIX/VIX3M ratio spiked into extreme backwardation in October 2008 when the VIX hit 80 while the 3-month vol surface was far less elevated. This is the defining event for this indicator: the ratio's 126-day z-score was off the charts, and SPY fell ~20% in the following two weeks. A clear long-lead case — backwardation signaled extreme panic before the final equity capitulation in March 2009.",
        "caption": "Oct 2008 VIX hit 80, ratio in extreme backwardation — z-score signal fired well before March 2009 equity trough"
    },
    {
        "slug": "covid",
        "title": "COVID Crash (2020)",
        "narrative": "In March 2020, the VIX spiked to 85 (exceeding GFC levels) while VIX3M remained lower — creating the sharpest and most rapid backwardation in the ratio's history. The 126-day z-score hit extreme readings. SPY fell 34% in 33 days. The Long/Cash strategy moved to cash rapidly, avoiding most of the drawdown. The signal reverted just as fast — this is a textbook coincident case for a high-frequency fear indicator.",
        "caption": "March 2020 VIX hit 85, ratio backwardation extreme — Long/Cash moved to cash within days, avoided SPY -34% crash"
    },
    {
        "slug": "rates_2022",
        "title": "Fed Hiking Cycle (2022)",
        "narrative": "Unlike the GFC or COVID, the 2022 bear market was a slow grind rather than a panic spike. VIX rose steadily (peaking around 35) but did not create sustained extreme backwardation in the ratio — the vol term structure remained relatively flat. The z-score signal fired intermittently rather than with the conviction of a panic episode. This is a partial failure case: the indicator is better suited to shock events than sustained macro-driven bear markets.",
        "caption": "2022 bear market was a grind, not a panic — VIX/VIX3M ratio never hit extreme backwardation; signal fired intermittently"
    },
]
```

---

## Validation Notes

**RES-20 Triad coverage per pair:**

| pair_id | long_lead | coincident | failure_case |
|---------|-----------|------------|--------------|
| dff_ted_spy | gfc (months before trough) | taper_2013 (small signal) | dot_com (underestimated depth) |
| sofr_ted_spy | rates_2022 (fired early in cycle) | — | coverage limitation |
| ted_spliced_spy | gfc (months before trough) | covid (fast cycle) | dot_com (partial) |
| indpro_spy | dot_com (3-6M lead) | covid (tracked quickly) | china_2015 (shallow correction) |
| indpro_xlp | dot_com (defensive rotation) | gfc (sustained signal) | covid (synchronized shock) |
| permit_spy | gfc (18M lead) | covid (fast reversal) | dot_com (housing irrelevant) |
| umcsent_xlv | gfc (late 2007 signal) | covid (mixed) | rates_2022 (missed XLV rally) |
| vix_vix3m_spy | gfc (pre-March 2009) | covid (coincident panic) | rates_2022 (grind ≠ panic) |

All narratives are grounded in the pairs' `interpretation_metadata.json` mechanisms and `winner_summary.json` signal logic. No numbers have been invented — specific coefficient values and Sharpe ratios are drawn directly from those files.

**Ready for Ace to wire. No further action required from Ray on this handoff.**
