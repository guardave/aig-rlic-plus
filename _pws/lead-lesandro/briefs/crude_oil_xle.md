# Pair Brief — `crude_oil_xle`

**Status:** scheduled — not yet started.
**Authored:** 2026-06-02 by Lead Lesandro.
**Rule:** [LEAD-NPB1](../../../docs/agent-sops/lead-agent-sop.md) New-Pair Brief Discipline.

This brief is intentionally thin and neutral. It carries identity facts and the acceptance gate. It does NOT carry domain notes, expected directions, method preselections, or pitfall warnings — those are answers the data and agents produce after exploration, not assertions Lead injects before dispatch.

---

## 1. Pair identity (LEAD-DV1)

| Field | Value |
|---|---|
| **`pair_id`** | `crude_oil_xle` |
| **Indicator → target** | Crude Oil Price (WTI) → XLE (Energy Select Sector SPDR) |
| **Source CSV row** | `data/prospective_pairs.csv` line 39 |
| **Source CSV ticker** | `En - Crude Oil $` |
| **Indicator category** | energy (per source CSV) |
| **Pre-master row 2** | col 76, sheet `WCOILWTICO` col B |
| **Pre-master description** | "Crude Oil Prices: West Texas Intermediate (WTI), Units: Dollars per Barrel, Not Seasonally Adjusted, Weekly, Jan 1986 – Oct 2025" |
| **FRED series** | `WCOILWTICO` (sheet name matches FRED series ID; Dana confirms at dispatch) |
| **Frequency** | Weekly |
| **Units** | USD per barrel |
| **SA** | NSA |

**Disambiguation.** Pre-master has TWO crude-related columns. This pair uses the **price** series (`WCOILWTICO`, col 76). A separate inventory series (`WTTSTUS1`, col 40, Thousand Barrels) is mapped to a distinct pair (`wttstus1_spy`) in the catalog. Do not conflate.

---

## 2. Acceptance gate (GATE-CMP1)

Producer-side mechanical completeness validation. Exit 0 required for Lead ratification.

```bash
python3 scripts/gate_pair_completeness.py crude_oil_xle
```

Exit 1 blocks ratification. The gate runs `_check_backlog_hygiene` (schema/presence + mandatory items exist) without judging method choice or analytical content — agents remain free to explore.

Documented exceptions only (none currently anticipated):

```bash
python3 scripts/gate_pair_completeness.py crude_oil_xle \
  --allow-partial \
  --partial-reason "BL-<ID>: <human-readable justification>"
```

`--allow-partial` requires a matching `BL-*-EXCEPTION` row in `docs/backlog.md`. It is not for silencing legitimate drift.

---

## 3. Work mode

Per LEAD-WM1, mode is decided in the SOD conversation with the user. Recorded here after the conversation.

| Field | Value |
|---|---|
| **Mode** | _TBD — to be filled at SOD_ |
| **Recorded by** | _TBD_ |
| **Date** | _TBD_ |

---

## 4. Scope

Single Done-Y target in source CSV: XLE. No per-sector family from this pair's completion. Other crude-related pairs in the catalog (e.g. `wttstus1_spy` — inventory series, not price) are separate `pair_id`s with their own briefs.

---

*Brief authored under LEAD-NPB1. When pair ratifies, copy lessons-learned into `[[lessons_crude_oil_xle]]` auto-memory.*
