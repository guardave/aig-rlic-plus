# Validation Audit — Viz Vera
**Date:** 2026-04-19
**Author:** Viz Vera
**Scope:** Wave 4F post-cross-review validation audit against HY-IG v2 chart inventory (13 JSON charts under `output/charts/hy_ig_v2_spy/plotly/` + 3 canonical zooms under `output/_comparison/`).

**Charts audited:** 10 canonical method charts in the reference pair + 3 canonical zoom charts = **13 charts**; 7 `_meta.json` sidecars; 4 `_perceptual_check_*.png`; 1 `_smoke_test_20260419.log`; 1 `chart_type_registry.json`. Legacy `hy_ig_v2_spy_*`-prefixed duplicates are present on disk (not loader-reachable per VIZ-A3/APP-EP4 canonical-path contract) and treated as audit artifacts only.

---

## Axis 1 — Reproducibility: "Would another Vera produce an identical JSON?"

**Verdict headline:** No. A second Vera working from the current SOP would match the **structure** and **filenames** but diverge on **palette**, **event-date selection**, **annotation positioning**, **title phrasing**, and **alpha within the permitted band**. At least one divergence is evidence-grade: the reference pair ships both Okabe-Ito colors (hero) and matplotlib defaults (`#d62728`, `#1f77b4`, `#2ca02c`) in parallel — i.e., Vera herself has already produced non-identical outputs on reruns.

### Reproducibility Gap Table

| # | Chart element | SOP rule | Deterministic? | Discretion point observed | Captured in sidecar / log? | Severity | Proposed fix |
|---|---|---|---|---|---|---|---|
| 1 | **Hero series colors** | VIZ-CP1 palette table | Partially | hero uses `#D55E00` (vermillion) + `#0072B2` (blue) — Okabe-Ito compliant | No — palette choice not in `_meta.json` | Low | Require `palette_id: "okabe-ito"` field in `_meta.json` (VIZ-V11 proposal) |
| 2 | **Zoom-chart data trace color** | VIZ-CP1 | **No** | `history_zoom_{dotcom,gfc,covid}` all use `#d62728` (matplotlib red, NOT Okabe-Ito) while hero uses Okabe-Ito `#D55E00`. Red-vs-vermillion: different hex, different colorblind profile. Rule says "standard colorblind-safe palette" but does not specify which of two near-reds a zoom chart should use | No | **HIGH** | Codify: indicator = `#D55E00` (Okabe-Ito vermillion) for ALL charts, drop matplotlib `#d62728` everywhere |
| 3 | **Granger / quartile / regime bar colors** | VIZ-CP1 | **No** | `granger_f_by_lag.json` (#d62728 red, #888 grey), `quartile_returns.json` (#009E73 green, #D55E00 orange — OK), `regime_quartile_returns.json` (#2ca02c, #7fb87f, #f5b377, #d62728 — matplotlib+custom). Two different palettes for two quartile charts on the same pair | No | **HIGH** | Codify quartile/diverging palette: require named palette (`ok_diverging_4`, `ok_stoplight_3`) referenced by key |
| 4 | **NBER shading alpha within 0.20–0.28 band** | VIZ-V2 rev 2026-04-19 | No (band, not single value) | Ref pair ships `rgba(150,120,120,0.22)` everywhere. Another Vera could legitimately pick 0.25. Band is a range; no single-value prescription | Yes — perceptual PNG, but PNG is a sample not a record | Medium | Promote `0.22` default to **THE default** in VIZ-V2 text; treat the band 0.20–0.28 as tolerance for post-hoc acceptance, not producer choice |
| 5 | **Zoom event-marker date selection** | VIZ-V1 "3–5 key dates" | **No** | Dot-Com picked 4 dates (Mar 2000, Aug 2000, Mar 2001, Jul 2002). GFC picked 5. COVID picked 3. SL-4 stakeholder sketch named Mar 2000 / Aug 2000 / Mar 2001 / Jul 2002 specifically, so dotcom is stakeholder-prescribed. GFC/COVID dates were Vera's pick from literature. No registry | Events list in `_meta.json` | **HIGH** | Machine-readable event registry keyed by episode slug (VIZ-V11) |
| 6 | **Zoom event-marker label text** | VIZ-V1 | **No** | "Mar 2000: Dot-Com peak" vs hypothetical "March 2000 — Dot-Com peak" or "Mar 2000 — Dot-Com equity peak". Format is loose | Text in sidecar events list | Medium | Label format spec: `"{MMM YYYY}: {event title ≤5 words}"` |
| 7 | **Annotation position** | VIZ-V1 (implementation note `annotation_position="top right"`) | Partially | Dot-Com annotations sit at descending y-values (867, 807, 748, 867). Vera hand-tuned y-positions to avoid overlap. No algorithm | No | Medium | Require `ann_position_strategy: "descending_stair" \| "top_right" \| "auto"` field |
| 8 | **Annotation density** | Chart Presentation Quality Patterns rule 3 (max 4–5) | No | Dot-Com 4 events + 2 footer = 6 total annotations. GFC 5 events + 2 footer = 7. The 4–5 cap refers to event markers, not all annotations, but the text is ambiguous | No | Low | Rewrite cap as: "≤5 event markers; footer/source annotations uncounted" |
| 9 | **Title exact wording** | VIZ-UR1 "title states takeaway" | No | "Credit Spreads During the Dot-Com Bust, 1998–2003" — three permissible alternatives: "1999–2002", "Bust", "Crash". No format | No | Medium | Title template per chart type: `"{Insight}, {YYYY}–{YYYY}"` for zooms |
| 10 | **Axis tick formatting** | None | No | Plotly defaults; Vera has not overridden. Acceptable for now | No | Low | None — defer |
| 11 | **Panel layout (N panels for hero)** | VIZ-V2 subplot rule | Structural (dual required for hero) | Hero is 2 panels due to SL-2 + dual-axis. No guidance on when to move to 3 panels (e.g., adding drawdown) | No | Low | Add panel-count decision rule to VIZ-V2 |
| 12 | **NBER shading fill color hex** | VIZ-V2 rev | Partially | Prescribed `rgba(150,120,120,0.22)`. Deterministic if followed exactly; previous "grey alpha 0.12" was also "followed the rule" and was wrong. Wave-3 bug | Perceptual PNG | Medium | Keep; add META-PV signoff log line (VIZ-V9 proposal carries forward) |
| 13 | **Chart filename mapping to method** | VIZ-V8 + chart_type_registry.json | **YES (post V8)** | Registry introduced 2026-04-19. Pre-V8 was the S18-11 Granger-fallback root cause | Registry file itself | Closed | N/A — V8 is the fix |
| 14 | **Legacy `hy_ig_v2_spy_*`-prefixed files on disk** | VIZ-A3 prohibits pair-prefixed filenames | N/A | Disk state has 14 legacy prefixed files alongside 7 canonical files. Not loader-reachable, but audit-noisy and violates Rule A3 literal intent | No | Low | Sweep-delete script: `scripts/cleanup_legacy_chart_filenames.py` or add to `.gitignore`; sop-changelog entry |
| 15 | **Color reference in narrative ("the red line")** | VIZ-CP1 | **No** | If Ray writes "the red line" and Vera ships zooms in `#d62728` vs hero in `#D55E00`, "red" is technically correct for both but is **two different reds**. Cross-agent contract gap | No | Medium | Narrative-color coupling: forbid color references in prose OR mandate single palette key |

### Severity summary
- **HIGH (3):** palette inconsistency between hero and zooms (#2, #3); zoom event-date selection discretion with no registry (#5)
- **Medium (5):** alpha single-value vs band (#4), label format (#6), annotation positioning algorithm (#7), title template (#9), shading-hex perceptual-follow-up (#12), color-in-prose contract (#15)
- **Low (5):** palette metadata (#1), annotation density cap ambiguity (#8), axis ticks (#10), panel count rule (#11), legacy files on disk (#14)
- **Closed (1):** filename→method mapping (#13, by V8)

---

## Axis 2 — Stakeholder Resolution: viz-lane items audited against HY-IG v2 evidence

| # | Stakeholder item | Claimed SOP rule | HY-IG v2 evidence | Spirit met? | Gap |
|---|---|---|---|---|---|
| SL-2 | NBER shading caption + annualized return overlay restored on hero | VIZ-V2 (caption + subplot + perceptual) | `hero_meta.json` records `"SL-2"` closed, `annualized_return_pct: 7.77`. Hero JSON has caption text "Vertical shaded bands mark NBER recessions." at y=-0.13 + overlay "<b>SPY Annualized return: 7.8%</b>" at (0.98, 0.97). 6 shapes split 3/3 across `xref=x` and `xref=x2` (subplot rule satisfied). Perceptual PNG exists dated 2026-04-19 | **Yes (spirit met)** | 7.77 → "7.8%" rounding is discretionary; no rounding rule |
| SL-3 | Chart + caption updated in same commit | GATE-24 + META-VNC | correlation_heatmap.json last touched 2026-04-11 (commit `b6dd6a9` — "Retroactive HY-IG v2 fixes" which paired chart canonicalization with Ray's narrative rewrite `d9aeaff`). Wave-2 rebuild and Wave-3 fixes respected the pairing. No orphaned chart-only commit observed since Wave 1 | **Yes (spirit met, process)** | Still a **manual** grep-check. No pre-commit hook. If Vera commits a chart alone tomorrow, nothing fires |
| SL-4 | Dot-Com annotated zoom | VIZ-V1 + META-ZI canonical | `output/_comparison/history_zoom_dotcom.json` exists, titled, 4 event markers (Mar 2000, Aug 2000, Mar 2001, Jul 2002) matching stakeholder sketch. Smoke test PASS. Perceptual PNG exists. Markers **are** informative (stakeholder-prescribed) | **Yes** | Event-date rationale not anchored to a machine-readable registry — re-run with a different Vera would need to re-derive from the stakeholder sketch |
| SL-5 | GFC annotated zoom | VIZ-V1 + META-ZI | `output/_comparison/history_zoom_gfc.json` exists, 5 event markers (Aug 2007 BNP, Oct 2007 widen, Mar 2008 Bear Stearns, Sep 2008 Lehman, Jun 2009 recession end). Informative, literature-anchored | **Yes** | Same as SL-4 — rationale source (which paper, which FRED note) not captured in sidecar |
| S18-8 | CCF quartile returns chart restored | VIZ-V4 + ECON-E2 | `regime_quartile_returns.json` exists (#2ca02c → #d62728 gradient, Q1=tightest → Q4=widest). Title explicit: "Annualized SPY Return by HY-IG Spread Quartile (Q1=Tightest → Q4=Widest)". Also legacy `quartile_returns.json` retained | **Yes (spirit met)** | Two files (`quartile_returns.json` + `regime_quartile_returns.json`) — registry discipline in `chart_type_registry.json` names the latter; the former should be retired per META-VNC |
| S18-11 | Granger chart distinct from Local Projections | VIZ-V3 + ECON-E1 + V8 registry | `granger_f_by_lag.json` standalone; title "Granger Causality: HY-IG Spread → SPY Returns, F-statistic by Lag"; 2 traces (bars + F-critical line at α=0.05); smoke test PASS. No longer falls back to `local_projections.json` | **Yes** | F-critical line value is not in `_meta.json` — reviewer cannot audit the threshold without opening JSON |
| VIZ-A1 | No inverted axes | Rule A1 | Hero dual-panel, no inversion | **Yes** | — |
| VIZ-A2 | Unit discipline | Rule A2 | Hero axis "HY-IG OAS Spread (bps, where 100 bps = 1%)". Values in 100s–1000s range. Pass. Annualized return callout uses `"7.8%"` (not dual notation "7.8% (78 bps ann.)") — acceptable under RES-4 for tidiness | **Yes** | — |
| VIZ-A3 | Canonical chart paths | Rule A3 + VIZ-V8 | All 7 canonical-named files present in `plotly/`. Legacy `hy_ig_v2_spy_*`-prefixed files also present (not loader-reachable per APP-EP4, but on disk) | **Yes for loader; No for cleanliness** | Sweep the 14 legacy prefixed files |
| VIZ-A4 | Regression note on rerun | Rule A4 | Commits `beca5aa`, `b6dd6a9` reference Wave-level regression narratives but `results/hy_ig_v2_spy/regression_note_*.md` file existence not verified in this audit pass | **Partial** | Verify regression_note_{YYYYMMDD}.md is physically present for each chart rerun |
| VIZ-A5 | Caption ownership split | Rule A5 | `hero_meta.json` caption: "Dual-panel time series of HY-IG OAS spread… Annualized SPY return overlay restored." Ray's display caption lives in narrative markdown. Both exist; no observed contradiction | **Yes** | No coupling check (cross-ref Wave 4B V7 proposal) |

### Stakeholder-resolution summary
- **All 8 viz-lane stakeholder items met in spirit.**
- **Residual gaps are process/discretion, not substance:** rounding rule (SL-2), pre-commit hook (SL-3), event-rationale capture (SL-4/5), legacy file cleanup (A3), regression_note file existence check (A4), caption coupling (A5).

---

## Axis 3 — Proposed SOP fixes (targeting palette, event selection, annotation positioning)

### VIZ-V11 — Palette Compliance Registry + `palette_id` Sidecar Field
**Blocking?** Yes for new charts; advisory for existing.
**Rule text:** The SOP ships `docs/schemas/color_palette_registry.json` (owner: Vera, per META-CF) enumerating named palettes: `okabe_ito_core` (primary indicator/target/strategy/baseline trio), `ok_diverging_4` (quartile gradient), `ok_stoplight_3` (pass/warn/fail bars), `ok_categorical_8` (multi-series). Every `_meta.json` sidecar MUST include `palette_id` naming the palette used. A chart whose trace colors are not subsets of the named palette fails VIZ-V5 smoke test. Pre-commit check scans trace colors against registry and rejects matplotlib defaults (`#d62728`, `#1f77b4`, `#2ca02c`, `#ff7f0e`) unless the chart declares `palette_id: "matplotlib_legacy"` with a grandfather date.
**Closes gap:** #1, #2, #3, #15 above; Wave-4B Q1 (red-vs-vermillion).

### VIZ-V12 — Historical Episode Event Registry (machine-readable)
**Blocking?** Yes.
**Rule text:** The canonical event-marker set per episode lives at `docs/schemas/history_zoom_events_registry.json` (owner: Vera + Ray, per META-CF), keyed by `episode_slug` → list of `{date, label, rationale_source, event_category}`. Every `history_zoom_{slug}.json` Vera produces MUST substitute events from this file; ad-hoc event picks are prohibited. Pair-override zoom charts (META-ZI path 2) MAY add pair-specific overlays but MUST retain the canonical baseline event set. Schema update requires an SOP changelog entry. Dot-Com slug is pre-loaded from SL-4 stakeholder sketch; GFC from NY Fed GFC timeline; COVID from CBO + Fed H.4.1.
**Closes gap:** #5, #6, SL-4/SL-5 rationale-capture residual.

### VIZ-V13 — Annotation Positioning Algorithm Specification
**Blocking?** Yes.
**Rule text:** VIZ-V1 step "Implementation" is extended: annotation placement uses one of three named strategies declared in `_meta.json` field `ann_position_strategy`:
- `top_right_uniform` — all annotations at chart-top right of marker (Plotly default, overlap-prone)
- `descending_stair` — y-values decrement by ~7% of y-range per annotation in event order (current Dot-Com approach)
- `alternating_top_bottom` — odd markers above data, even below (for dense zoom charts)
Vera picks strategy at chart-design time; choice is logged; another Vera with the same strategy reproduces identical y-positions given identical data. Free-form hand-tuning is prohibited except as sub-strategy `"manual_override"` which requires regression_note entry naming each moved annotation.
**Closes gap:** #7.

### VIZ-V14 — NBER Alpha Single-Value Default + Perceptual Signoff Log
**Blocking?** Yes for new charts.
**Rule text:** VIZ-V2 `alpha` prescription is tightened from a band (0.20–0.28) to a single default: `alpha = 0.22`, `fillcolor = "rgba(150,120,120,0.22)"`. The 0.20–0.28 band is reclassified as post-hoc acceptance tolerance (a chart shipped at 0.25 during a transition period is not rejected, but new charts are built at 0.22). Companion rule: append one line per perceptual check to `output/charts/{pair_id}/plotly/_perceptual_signoff.log` with `{timestamp} | {chart_name} | alpha={alpha} | signed_off_by={agent}` (subsumes Wave-4B V9 proposal).
**Closes gap:** #4, #12; SL-2 follow-up.

### VIZ-V15 — Title Template per Chart Type
**Blocking?** Advisory.
**Rule text:** The chart_type_registry gains a `title_template` field per method. Templates:
- `hero`: `"{Indicator Display Name} vs {Target Display Name} — {YYYY} to {YYYY}"`
- `history_zoom_{slug}`: `"{Indicator} During the {Episode Name}, {YYYY}–{YYYY}"`
- `granger`: `"Granger Causality: {X} → {Y}, F-statistic by Lag"`
- `quartile_returns`: `"Annualized {Target} Return by {Indicator} Quartile (Q1={low_semantic} → Q4={high_semantic})"`
Vera substitutes placeholders from `interpretation_metadata.json` + data dictionary. Titles outside the template require regression_note rationale.
**Closes gap:** #9.

### VIZ-V16 — Legacy Filename Sweep + Gitignore
**Blocking?** Yes before next release.
**Rule text:** Sweep `output/charts/{pair_id}/plotly/` for any basename matching `{pair_id}_*.json` (pair-id-prefixed) and delete or gitignore. VIZ-A3 prohibits these at production time; a one-time cleanup closes the disk state. Add `output/charts/*/plotly/<pair_id>_*.json` pattern to `.gitignore` to prevent re-creation.
**Closes gap:** #14.

### Proposal count: 6 VIZ-* rules. (Within the requested 4–7 band.)

---

## Axis 4 — Questions to Lesandro

1. **Palette authority.** The SOP mandates Okabe-Ito but three charts ship matplotlib defaults. Is this acceptable grandfathered state, or a Wave-5 fix? If Wave-5, do I block the HY-IG v2 reference-pair sign-off until VIZ-V11 is applied, or document the gap and ship?

2. **Event-date provenance.** Dot-Com zoom dates came from the SL-4 stakeholder sketch. GFC dates came from my reading of NY Fed's GFC timeline. COVID from CBO. Do you want every event in `history_zoom_events_registry.json` to cite a specific authoritative source (NBER paper, Fed staff memo, NY Fed timeline) as `rationale_source`, or is "Lesandro discretion" an acceptable placeholder for early episodes?

3. **Red-vs-vermillion colorblind impact.** I'm proposing to drop matplotlib `#d62728` everywhere in favor of Okabe-Ito `#D55E00`. Does the VIZ-CP1 palette need any user-study / accessibility validation before I refactor 13 charts + downstream prose references?

4. **Perceptual signoff.** I can produce `_perceptual_signoff.log` autonomously (my own eye) or gate it on your review. For canonical charts (`output/_comparison/*`), which should it be?

5. **Legacy-file sweep timing.** Deleting 14 legacy `hy_ig_v2_spy_*`-prefixed files will show up as a git-rm diff. Should it land in Wave-5 as a separate "housekeeping" commit, or folded into the VIZ-V11 palette-compliance PR?

**Top question (blocking):** #1 — palette authority — because it determines whether Wave-5 is a "polish" wave or an "audit-blocker remediation" wave.

---

## Appendix — Smoke test + perceptual check evidence

- `_smoke_test_20260419.log`: 10/10 PASS (7 HY-IG v2 canonical + 3 `_comparison/history_zoom_*`). Every chart has ≥1 data trace and a non-empty title.
- `_perceptual_check_hero.png` exists, dated 2026-04-19 16:14.
- `_perceptual_check_history_zoom_{dotcom,gfc,covid}.png` all exist, dated 2026-04-19 16:14.
- No perceptual signoff log file yet — VIZ-V14 proposal would create it.

## Counts at a glance

- Charts audited: **13** (10 reference-pair canonical + 3 canonical zooms; 14 legacy prefixed files noted but not loader-reachable)
- Reproducibility gaps: **3 HIGH / 5 Medium / 5 Low / 1 Closed**
- Stakeholder-resolution audit: **8 viz-lane items, 8 met in spirit, 6 residual process gaps**
- SOP proposals: **6** (V11–V16)
- Questions to Lesandro: **5** (top: palette authority)
