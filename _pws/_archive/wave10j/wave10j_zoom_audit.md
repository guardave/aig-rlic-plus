# Wave 10J — Historical Zoom Chart Audit

**Date:** 2026-04-24
**Auditor:** Viz Vera
**Rule applied:** VIZ-ZOOM1 (defined in Wave 10J SOP update)

---

## Current Zoom Chart Inventory

```
output/charts/hy_ig_spy/plotly/history_zoom_covid.json      ✓
output/charts/hy_ig_spy/plotly/history_zoom_dotcom.json     ✓
output/charts/hy_ig_spy/plotly/history_zoom_gfc.json        ✓
output/charts/hy_ig_v2_spy/plotly/history_zoom_covid.json   ✓
output/charts/hy_ig_v2_spy/plotly/history_zoom_dotcom.json  ✓
output/charts/hy_ig_v2_spy/plotly/history_zoom_gfc.json     ✓
```

Only two pairs (`hy_ig_spy`, `hy_ig_v2_spy`) have zoom charts. All other pairs have zero zoom charts.

---

## VIZ-ZOOM1 Trigger Assessment Per Pair

VIZ-ZOOM1 requires zoom charts for any pair where:
- (a) the indicator data spans the episode (data coverage check), AND
- (b) the narrative (Story page) references the episode by name, OR
- (c) the episode represents a major regime stress event relevant to the indicator's domain

### Active Pairs — Zoom Chart Status

| Pair | Sample Start | Dotcom | GFC | COVID | 2022 Rates | Status |
|------|-------------|--------|-----|-------|-----------|--------|
| `hy_ig_spy` | ~1997 | ✓ | ✓ | ✓ | MISSING | Partial — 2022 zoom missing |
| `hy_ig_v2_spy` | ~1997 | ✓ | ✓ | ✓ | MISSING | Partial — 2022 zoom missing |
| `indpro_spy` | ~1980 | MISSING | MISSING | MISSING | MISSING | **All missing** |
| `permit_spy` | ~1960 | MISSING | MISSING | MISSING | MISSING | **All missing** |
| `sofr_ted_spy` | ~2014 | N/A (pre-SOFR) | N/A (pre-SOFR) | MISSING | MISSING | COVID + 2022 required |
| `ted_spliced_spy` | ~1990 | MISSING | MISSING | MISSING | MISSING | **All missing** |
| `dff_ted_spy` | ~1990 | MISSING | MISSING | MISSING | MISSING | **All missing** |
| `vix_vix3m_spy` | ~2004 | N/A (pre-VIX3M) | MISSING | MISSING | MISSING | GFC + COVID + 2022 required |
| `indpro_xlp` | ~1980 | MISSING | MISSING | MISSING | MISSING | **All missing** |
| `umcsent_xlv` | ~1980 | MISSING | MISSING | MISSING | MISSING | **All missing** |

---

## Missing Required Zoom Charts (By VIZ-ZOOM1)

The following zoom charts are required and not present:

### `indpro_spy`
- `history_zoom_dotcom.json` (data spans 2000–2002)
- `history_zoom_gfc.json` (data spans 2007–2009)
- `history_zoom_covid.json` (data spans 2020)
- `history_zoom_inflation_2022.json` (data spans 2022)

### `permit_spy`
- `history_zoom_dotcom.json`
- `history_zoom_gfc.json`
- `history_zoom_covid.json`
- `history_zoom_inflation_2022.json`

### `ted_spliced_spy`
- `history_zoom_dotcom.json`
- `history_zoom_gfc.json`
- `history_zoom_covid.json`
- `history_zoom_inflation_2022.json`

### `dff_ted_spy`
- `history_zoom_dotcom.json`
- `history_zoom_gfc.json`
- `history_zoom_covid.json`
- `history_zoom_inflation_2022.json`

### `sofr_ted_spy`
- `history_zoom_covid.json` (SOFR data available from 2014)
- `history_zoom_inflation_2022.json`

### `vix_vix3m_spy`
- `history_zoom_gfc.json` (VIX3M available from 2004; GFC window 2007–2009 is within sample)
- `history_zoom_covid.json`
- `history_zoom_inflation_2022.json`

### `indpro_xlp`
- `history_zoom_dotcom.json`
- `history_zoom_gfc.json`
- `history_zoom_covid.json`
- `history_zoom_inflation_2022.json`

### `umcsent_xlv`
- `history_zoom_dotcom.json`
- `history_zoom_gfc.json`
- `history_zoom_covid.json`
- `history_zoom_inflation_2022.json`

### `hy_ig_spy` and `hy_ig_v2_spy` (partial)
- `history_zoom_inflation_2022.json` — MISSING from both pairs (2022 rates shock is a major credit event)

---

## Total Non-Compliance Count

- **Required zoom charts missing:** 34
- **Pairs with zero zoom charts:** 8 of 10 active pairs
- **Pairs partially compliant (have some but not all):** 2 (`hy_ig_spy`, `hy_ig_v2_spy`)

---

## Remediation Route

All missing zoom charts require:
1. Dual-panel layout (indicator top, target bottom, shared x-axis)
2. NBER shading on BOTH panels
3. 3–5 event markers from `docs/schemas/history_zoom_events_registry.json`
4. `annotation_strategy_id: "descending_stair"` in `_meta.json` sidecar
5. Episode-specific title naming the indicator and episode explicitly

Remediation is dispatched to the pair pipeline generator scripts (Evan coordination required for `inflation_2022` episode which is not yet in the episodes registry).
