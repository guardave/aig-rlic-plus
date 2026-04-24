# Wave 10J Self-Assessment — Viz Vera

**Date:** 2026-04-24
**Wave:** 10J

---

## Question 1: What mistakes did I make in recent waves that I should have caught myself before handoff?

### NBER Shading — Inconsistent Coverage
The most significant self-caught error: NBER shading is applied inconsistently across pairs and chart types. Hero charts for `permit_spy`, `sofr_ted_spy`, `ted_spliced_spy`, `dff_ted_spy`, and `vix_vix3m_spy` have NO NBER shading, while `hy_ig_spy`, `hy_ig_v2_spy`, `indpro_spy`, `indpro_xlp`, and `umcsent_xlv` do. This inconsistency violates the spirit of Rule V2, which says long-horizon time-series (>5 years) MUST include NBER shading. I should have enforced a consistent rule before delivering each pair.

### Missing Rule Codification for Zoom Charts
History zoom charts exist only for `hy_ig_spy` and `hy_ig_v2_spy`. No other pair has zoom charts. My SOP had Rule V1 covering zoom chart mechanics but did NOT have a clear, observable rule stating **when** zoom charts are required vs. optional. This left the judgment call implicit, leading to inconsistency across pairs.

### Filename Convention Non-Compliance (Pre-existing, Not Wave 10J-specific)
Several pairs ship with pair-prefixed filenames (`indpro_spy_hero.json`, `permit_spy_hero.json`, etc.) rather than bare-name canonical form (`hero.json`). The Wave 10F cross-review noted this but I did not remediate it in subsequent waves. This is a completeness gap I carry forward.

### No VIZ-CP1 Rule for Cross-Period Charts
When Evan (ECON-CP1/CP2) began generating cross-period consistency charts (rolling correlation, rolling Sharpe, rolling Granger, subperiod Sharpe, structural break), I had no documented visualization rule for these chart types. This means when Evan delivers results, I would have no canonical spec to follow — a gap that would lead to ad-hoc decisions.

---

## Question 2: What did my SOP say I should do that I did not do?

1. **Rule V2 (NBER shading):** The rule states long-horizon charts (>5 years) MUST have NBER shading. I did not apply this consistently — 5 hero charts across active pairs have no shading.

2. **Perceptual validation (V2 item 4):** I should have run `plotly.io.from_json` + kaleido render after every chart save to produce `_perceptual_check_{chart_name}.png`. I have no evidence this was done for recent pairs.

3. **Sidecar backfill (VIZ-O1):** Many charts — especially in prefixed-filename pairs — lack `_meta.json` sidecars with `disposition` fields. GATE-28 requires this.

4. **Input Quality Log:** My SOP requires maintaining `docs/agent-sops/viz-input-quality-log.md` after each task. This has not been updated consistently.

5. **End-of-Task Reflection (SOP §Task Completion Hooks):** While my `experience.md` has been updated, I did not always log input quality per the template.

---

## Question 3: What did I learn, and is it in experience.md?

### Confirmed in experience.md:
- NBER shading alpha floor (0.20–0.28), subplot coverage rule — YES
- Canonical contracts (chart-type registry, events registry, annotation strategies) — YES
- Bare-name migration pattern — YES
- Palette discipline (Okabe-Ito 2026, role keys) — YES
- Per-method ownership (VIZ-V3, V4) — YES
- Smoke test checklist (VIZ-V5) — YES
- Consumer-side references update on rename — YES

### NOT yet in experience.md (updating now):
- There is no rule yet defining **when** zoom charts are required (ZOOM1 gap). Experience should record that the absence of a trigger rule causes inconsistency.
- The CP-chart types (rolling correlation, rolling Sharpe, rolling Granger, subperiod Sharpe, structural break) have no canonical spec — first time Vera encounters them is Wave 10J.
- NBER shading in rolling charts (rolling_sharpe, rolling_correlation) is an open question that produced inconsistency.

**Action:** experience.md updated in Part 5 of this wave.
