# Viz Vera — Outstanding Work

**Last updated:** 2026-05-13 (OW-1 closed — perceptual PNGs verified)

---

## Pending Items

### P1 — Perceptual PNGs (kaleido renders) for 9 pairs [CLOSED 2026-05-13]

**Status:** CLOSED. Verified on 2026-05-13: all 197 chart JSONs across the 9 pairs (`hy_ig_spy`, `indpro_spy`, `indpro_xlp`, `permit_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`, `vix_vix3m_spy`, `umcsent_xlv`) already have `_perceptual_check_*.png` sidecars on disk AND tracked in git (258 PNGs total across `output/charts/*/plotly/`, zero untracked). Batch render script confirmed idempotent: 0 generated, 197 skipped, 0 failures. Spot-checked one hero PNG per pair — all render correctly (titles, axes, legends, NBER bands visible). No new commit required; VIZ-CV1 perceptual mandate is satisfied. Quincy's WARN flag is stale.

---

### P2 — history_zoom charts for new pairs (forward-looking) [OPEN]

**Status:** VIZ-HZE1 gate now enforces this per-pair at handoff time. No backlog item — this is now mandatory per SOP. Any new pair will generate zoom charts as part of standard production.

---

### P3 — kaleido deprecation warnings [LOW, deferred]

**Status:** Upstream upgrade track. Warnings appear during perceptual-check PNG rendering. Does not affect Plotly JSON output. Will be addressed when kaleido releases a non-deprecated API.

---

### P4 — indpro_xlp and umcsent_xlv ukraine episode zoom charts [OPEN]

**Status:** Deliberately omitted at Wave 10J time.
- `indpro_xlp`: ukraine episode omitted because no SPY divergence during that period.
- `umcsent_xlv`: ukraine episode omitted — coverage assessment TBD.

**What is needed:** If Lead or Ray flags these as required, generate the missing charts and update `_meta.json` skip entries accordingly.

---

## Completed (reference)

| Wave | Item | Commit |
|------|------|--------|
| 10J | VIZ-HZE1 SOP rule authored | `da8f534` |
| 10J | 29 history_zoom charts + 31 sidecars across 8 pairs | `20669d9` |
| 10J | vix_vix3m_spy dot_com skip entry | `2f15547` |
| 10J | META-CPD cross-reference added to Viz SOP | `da8f534` |
| 10H.1 | VIZ-O1 disposition mandate + VIZ-E1 exploratory sidecar spec | — |
| 10F | Filename migration (bare-name canon) for indpro_xlp + umcsent_xlv | `3c6bb50` |
| 10G.4D | hy_ig_spy 22-chart suite | `c525470` |
