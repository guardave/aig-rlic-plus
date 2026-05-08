# QA Quincy — Phase 3 Cross-Review: Handoff / Gate-Pairing Audit
**Date:** 2026-05-08  
**Reviewer:** QA Quincy  
**Scope:** Cross-review of five peer SOPs (Dana, Evan, Vera, Ray, Ace) from a handoff/QA-gate perspective only.  
**Binding constraints:** LA-1 through LA-10 accepted as-is; no findings re-litigate them.  
**Constraint:** LEAD-DL1 — `cloud_verify.py` not touched.  
**No edits made to any SOP or code file during this review.**

---

## Legend

| Severity | Meaning |
|----------|---------|
| CRITICAL | Blocks handoff or violates a binding LA arbitration |
| HIGH | Material gate↔producer mismatch; observable QA failure risk |
| MEDIUM | Gap that could let a defect slip; fix recommended before Wave 10K |
| LOW | Undocumented design choice or minor cross-ref hygiene |

---

## §1 — DANA (Data Agent)

### D-01
**rule_id:** DATA-D6b / GATE-NR  
**problem:** DATA-D6b asserts that GATE-NR already covers raw column identifiers (e.g. `ret_1m`, `excess_ret`) as well as instrument names. GATE-NR's pseudocode in the QA SOP checks only against `KNOWN_INSTRUMENTS` (ETF tickers and index names). Column identifiers are a distinct namespace and are not in KNOWN_INSTRUMENTS. A column labelled with a non-canonical suffix would pass GATE-NR undetected.  
**severity:** HIGH  
**who must fix:** Dana (narrow DATA-D6b to what GATE-NR actually checks, or define a new gate for column-suffix validation) + Quincy (if GATE-NR scope is intended to expand, update GATE-NR pseudocode in QA SOP)

---

### D-02
**rule_id:** DATA-D5 / (no gate)  
**problem:** DATA-D5 mandates sidecar schema validation (`schema_validators/`) for every data artefact handed off. No named QA gate in the QA SOP independently verifies that the sidecar schema file exists and that the artefact passes it. GATE-29 checks signals parquet structure but does not reference sidecar schema files.  
**severity:** MEDIUM  
**who must fix:** Quincy (define a gate or extend GATE-29 to include sidecar schema presence check; add to QA-CL1 checklist)

---

### D-03
**rule_id:** DATA-D12 / (no gate)  
**problem:** DATA-D12 requires a column-suffix linter pass before handoff (`linter/column_suffix_check.py`). There is no QA gate that independently re-runs or spot-checks this linter output. Dana's self-certification is the only control.  
**severity:** MEDIUM  
**who must fix:** Quincy (add a column-suffix spot-check step to QA-CL1 or define GATE-D12)

---

### D-04
**rule_id:** DATA-D11 / DATA-D13 / QA-CL1  
**problem:** DATA-D11 mandates sidecar file existence for each output artefact; DATA-D13 mandates a completeness manifest. Neither appears explicitly in QA-CL1's checklist items. GATE-29 and GATE-28 address content checks but not file-existence checks for sidecars and manifests.  
**severity:** LOW  
**who must fix:** Quincy (add sidecar-existence and manifest-presence line items to QA-CL1)

---

## §2 — EVAN (Econometrics Agent)

### E-01 (LA-9 VIOLATION)
**rule_id:** ECON-SD / (absent gate)  
**problem:** LA-9 mandates that an ECON-SD audit gate must appear in the QA SOP. ECON-SD (pair scope discipline — enforce that each model uses only the designated pair's instruments) is defined in Evan's SOP. No gate named GATE-SD or equivalent exists in the QA SOP as of the Phase 1 snapshot or the Phase 2 arbitration. This is a direct violation of a binding Lead arbitration, not a pre-existing gap.  
**severity:** CRITICAL  
**who must fix:** Quincy (define GATE-SD in QA SOP, add to QA-CL1 checklist; Evan must confirm what artefact GATE-SD reads to verify pair scope)

---

### E-02
**rule_id:** ECON-FE1 / GATE-ES1 (step 5)  
**problem:** ECON-FE1 specifies exact numeric acceptability floors:  
- Equity pairs: Sharpe ≥ 0.30  
- Fixed Income pairs: Sharpe ≥ 0.50  
- Crypto pairs: Sharpe ≥ 0.20  
- Excess return vs benchmark: ≥ 0.00  
- Delta Sharpe vs benchmark: ≥ +0.10  
- Max drawdown: ≤ 5 pp worse than benchmark  

GATE-ES1 step 5 states only "compare expected versus observed headline metrics." No numeric floors are mentioned. A QA operator following GATE-ES1 step 5 literally has no objective threshold to FAIL against — they would need to look up ECON-FE1 out-of-band. The gate pseudocode diverges from the producer contract.  
**severity:** HIGH  
**who must fix:** Quincy (add ECON-FE1 numeric floors verbatim into GATE-ES1 step 5 pseudocode, with asset-class branching)

---

### E-03
**rule_id:** ECON-T4 / (no gate)  
**problem:** ECON-T4 is the leakage guard — it requires that no future data enters any estimation window. There is no named QA gate that verifies leakage-guard compliance. GATE-ES1 does not include a leakage check step.  
**severity:** MEDIUM  
**who must fix:** Quincy (define GATE-T4 or add a leakage-audit step to GATE-ES1; identify the artefact or log that evidences the T4 check ran)

---

### E-04
**rule_id:** ECON-INF1 / (no gate)  
**problem:** ECON-INF1 mandates block bootstrap inference for overlapping-return series. No QA gate verifies that the inference method used matches ECON-INF1's requirement. Standard error tables submitted at handoff could use OLS SEs without triggering any QA FAIL.  
**severity:** LOW  
**who must fix:** Evan (include inference-method metadata in handoff artefact); Quincy (consider a metadata-check step in GATE-ES1 or GATE-28)

---

## §3 — VERA (Visualization Agent)

### V-01 (CRITICAL — LA-2 VIOLATION)
**rule_id:** GATE-VIZ-NBER2 / LA-2  
**problem:** GATE-VIZ-NBER2 hardcodes the slug names `dot_com`, `rates_2022`, and `taper_2013`. LA-2 mandates canonical slugs: `dotcom`, `inflation_2022`, and `taper_2018`. The gate is therefore checking for slugs that will never appear in compliant producer output, making it a null check — it will always silently PASS even on non-compliant artefacts.  
**severity:** CRITICAL  
**who must fix:** Quincy (update GATE-VIZ-NBER2 slug table to canonical LA-2 names; this is a gate-side correction, not a producer-side fix)

---

### V-02 (HIGH)
**rule_id:** VIZ-IC1 / (undefined)  
**problem:** VIZ-IC1 is cross-referenced in VIZ-CP1 and in Vera's VIZ-O1/E1 completion criteria, but VIZ-IC1 itself is never defined anywhere in the Visualization SOP. It is a phantom producer rule. Any cross-reference to VIZ-IC1 as a gate companion or a handoff requirement is unverifiable.  
**severity:** HIGH  
**who must fix:** Vera (define VIZ-IC1 fully, including what it checks, its severity, and its gate companion) + standards.md registration (per LA-5)

---

### V-03 (HIGH)
**rule_id:** GATE-VIZ-ZOOM1 / (absent)  
**problem:** VIZ-ZOOM1 cross-references `GATE-VIZ-ZOOM1` as the QA companion gate for zoom-chart JSON validation. No such gate exists in the QA SOP. It is a phantom gate ID — Vera's SOP points to a gate that Quincy has never written.  
**severity:** HIGH  
**who must fix:** Quincy (define GATE-VIZ-ZOOM1 in QA SOP; add to QA-CL1 or QA-CL4) + Vera (confirm what GATE-VIZ-ZOOM1 must check: JSON structure, slug presence, data array non-empty)

---

### V-04 (HIGH)
**rule_id:** VIZ-NBER1 / GATE-VIZ-NBER1  
**problem:** VIZ-NBER1 is BLOCKING for all chart types that contain a time axis, including hero charts and equity-curve charts. GATE-VIZ-NBER1's pseudocode scans only the Evidence page HTML for the text "NBER" or a shading CSS class. Hero charts and equity-curve charts live on the Story and Strategy pages respectively — those pages are not scanned by GATE-VIZ-NBER1. A NBER-shading defect on a hero chart would pass GATE-VIZ-NBER1 undetected.  
**severity:** HIGH  
**who must fix:** Quincy (extend GATE-VIZ-NBER1 scope to Story and Strategy page scans, or define GATE-VIZ-NBER1b for non-Evidence pages)

---

### V-05 (LOW)
**rule_id:** VIZ-CV1 / GATE-27-PNG  
**problem:** Match confirmed — VIZ-CV1 (perceptual render mandate, Rule V5) correctly pairs with GATE-27-PNG. Severity alignment confirmed (both FAIL). Cross-reference present in GATE-27-PNG body. No gap found.  
**severity:** LOW (informational — confirmed clean)  
**who must fix:** No action required

---

## §4 — RAY (Research Agent)

### R-01 (CRITICAL — LA-1 VIOLATION)
**rule_id:** RES-HZE1 / LA-1  
**problem:** RES-HZE1 instructs Ray to validate episode slugs against `docs/schemas/episode_registry.json`. LA-1 mandates that the canonical episode registry is `history_zoom_events_registry.json`. Ray's SOP still points to the deprecated file. Any slug validation Ray performs uses the wrong authority, potentially accepting deprecated slugs (e.g. `dot_com`, `rates_2022`, `taper_2013`) as valid and rejecting canonical LA-2 slugs.  
**severity:** CRITICAL  
**who must fix:** Ray (update RES-HZE1 to reference `history_zoom_events_registry.json` as the validation authority)

---

### R-02 (MEDIUM)
**rule_id:** RES-HZE1 content requirements / (no gate)  
**problem:** RES-HZE1 specifies content requirements for history-zoom episode blurbs: a triad structure (setup / shock / signal-behaviour), caption length ≤ 120 characters, and narrative quality criteria. No QA gate verifies these content requirements. GATE-HZE1 checks structural presence (heading exists, JSON file present) but does not check triad compliance, caption length, or narrative quality.  
**severity:** MEDIUM  
**who must fix:** Quincy (define content-check steps within GATE-HZE1 or as GATE-HZE1b, covering triad presence, caption ≤ 120 char, non-placeholder narrative)

---

### R-03 (LOW)
**rule_id:** RES-HZE1 / GATE-HZE1 — scope asymmetry (undocumented)  
**problem:** RES-HZE1 governs content quality; GATE-HZE1 governs structural presence. This division is not documented in either SOP — neither SOP acknowledges the complementary split. A future maintainer reading GATE-HZE1 alone would believe content requirements are also checked; they are not.  
**severity:** LOW  
**who must fix:** Both SOPs (add a "does not check content quality — see RES-HZE1" note to GATE-HZE1; add "structural check performed by GATE-HZE1" note to RES-HZE1 — Quincy owns GATE-HZE1 note; Ray owns RES-HZE1 note)

---

### R-04 (LOW)
**rule_id:** RES-EGL1 / (no gate)  
**problem:** RES-EGL1 mandates evidence-grade logging for all research conclusions (source URL, access date, extract, grade). No QA gate verifies that submitted research artefacts include EGL1-compliant logs. GATE-28 checks artefact presence but not log completeness.  
**severity:** LOW  
**who must fix:** Quincy (consider a log-completeness spot-check in GATE-28 or QA-CL2)

---

## §5 — ACE (App Dev Agent)

### A-01 (CRITICAL — LA-1 VIOLATION)
**rule_id:** ACE-HZE1 / LA-1  
**problem:** ACE-HZE1 step 2 validates episode slugs in pair configs against `episode_registry.json`. LA-1 mandates that the canonical episode registry is `history_zoom_events_registry.json`. Ace's gate therefore enforces the wrong file, potentially accepting deprecated slugs and blocking canonical ones. This creates a situation where Ray and Vera produce LA-2 compliant slugs and Ace's own gate rejects them.  
**severity:** CRITICAL  
**who must fix:** Ace (update ACE-HZE1 step 2 reference from `episode_registry.json` to `history_zoom_events_registry.json`)

---

### A-02 (MEDIUM)
**rule_id:** GATE-CL1-8 / (no Quincy gate)  
**problem:** GATE-CL1 through GATE-CL8 are Ace's self-check gates defined within the App Dev SOP. No independent Quincy-owned gate re-verifies any of the GATE-CL1-8 checks. The aspirational `gate_cl_audit.py` is Ace-authored (Wave 10K backlog) — it is not an independent QA verification. For gates where Ace both defines and verifies the check, the control is self-certifying.  
**severity:** MEDIUM  
**who must fix:** Quincy (define at minimum a GATE-CL-SPOT that independently re-runs a sample of GATE-CL1-8 checks on the deployed artefact; Wave 10K delivery)

---

### A-03 (LOW)
**rule_id:** APP-WS1 / smoke_schema_consumers.py  
**problem:** APP-WS1 is validated by `smoke_schema_consumers.py` which Quincy runs independently — this is a functional gate. However, `smoke_schema_consumers.py` is not referenced by name in QA-CL1 or any named QA gate. The check exists in practice but has no formal gate ID, making it invisible in handoff sign-off checklists.  
**severity:** LOW  
**who must fix:** Quincy (assign a formal gate ID — e.g. GATE-WS1 — to the smoke_schema_consumers.py check; add to QA-CL1)

---

### A-04 (LOW — confirmed clean)
**rule_id:** APP-LP8 / GATE-ES1 step 7  
**problem:** Match confirmed — APP-LP8 (evidence-status honesty label) is correctly cross-referenced in GATE-ES1 step 7. Severity alignment confirmed. No gap found.  
**severity:** LOW (informational — confirmed clean)  
**who must fix:** No action required

---

## §6 — Cross-Cutting Themes

### Theme 1: Slug Namespace Fragmentation (LA-1 / LA-2)
Three peer SOPs (Ray RES-HZE1, Ace ACE-HZE1, and Vera GATE-VIZ-NBER2) still reference deprecated registry files and/or non-canonical slug names. LA-1 and LA-2 are binding. Until all three are corrected, any slug-based cross-agent handoff carries a CRITICAL mismatch risk where one agent's PASS is another's FAIL. Findings: R-01, A-01, V-01.

### Theme 2: Numeric Floor Absence in QA Gates (ECON-FE1 / GATE-ES1)
Producer-side contracts specify exact acceptability floors; QA-side pseudocode says only "compare." A QA operator running GATE-ES1 has no objective threshold. This pattern may repeat in other gate/producer pairs not yet reviewed. Finding: E-02.

### Theme 3: Phantom IDs (Undefined Rules and Undefined Gates)
VIZ-IC1 is a phantom producer rule (referenced, never defined). GATE-VIZ-ZOOM1 is a phantom QA gate (referenced in Vera's SOP, never written). Both create cross-reference chains that terminate at nothing. Findings: V-02, V-03.

### Theme 4: LA-9 Non-Compliance (ECON-SD)
The ECON-SD audit gate does not exist in the QA SOP. This is not a pre-existing gap — it is a binding Lead arbitration from Phase 2 that has not been acted on. Finding: E-01.

---

## §7 — Summary Table

| Finding | Peer | Severity | Fix Owner |
|---------|------|----------|-----------|
| D-01 | Dana | HIGH | Dana + Quincy |
| D-02 | Dana | MEDIUM | Quincy |
| D-03 | Dana | MEDIUM | Quincy |
| D-04 | Dana | LOW | Quincy |
| E-01 | Evan | CRITICAL | Quincy |
| E-02 | Evan | HIGH | Quincy |
| E-03 | Evan | MEDIUM | Quincy |
| E-04 | Evan | LOW | Evan + Quincy |
| V-01 | Vera | CRITICAL | Quincy |
| V-02 | Vera | HIGH | Vera + standards.md |
| V-03 | Vera | HIGH | Quincy + Vera |
| V-04 | Vera | HIGH | Quincy |
| V-05 | Vera | LOW (clean) | — |
| R-01 | Ray | CRITICAL | Ray |
| R-02 | Ray | MEDIUM | Quincy |
| R-03 | Ray | LOW | Ray + Quincy |
| R-04 | Ray | LOW | Quincy |
| A-01 | Ace | CRITICAL | Ace |
| A-02 | Ace | MEDIUM | Quincy |
| A-03 | Ace | LOW | Quincy |
| A-04 | Ace | LOW (clean) | — |

**Total findings: 20** (excluding 2 confirmed-clean entries)  
**Breakdown:** 4 CRITICAL, 5 HIGH, 5 MEDIUM, 4 LOW (+ 2 informational clean confirmations)

| Peer | CRITICAL | HIGH | MEDIUM | LOW |
|------|----------|------|--------|-----|
| Dana | 0 | 1 | 2 | 1 |
| Evan | 1 | 1 | 1 | 1 |
| Vera | 1 | 3 | 0 | 1 |
| Ray | 1 | 0 | 1 | 2 |
| Ace | 1 | 0 | 1 | 1 |

---

## §8 — Gate↔Producer Mismatches Not Covered by LA-1 to LA-10

The following mismatches are new findings from Phase 3 that LA-1 through LA-10 did not address:

1. **D-01** — GATE-NR scope (instrument names only) vs DATA-D6b claim (also covers column identifiers). Not addressed by any LA arbitration.
2. **E-02** — GATE-ES1 step 5 missing ECON-FE1 numeric floors. LA-9 addressed ECON-SD only; ECON-FE1 floor echo was not arbitrated.
3. **E-03** — No gate for ECON-T4 leakage guard. Not addressed by any LA.
4. **V-02** — VIZ-IC1 undefined. Phase 1 flagged registration gap; no LA resolved the definition gap.
5. **V-03** — GATE-VIZ-ZOOM1 phantom gate. Not addressed by any LA.
6. **V-04** — GATE-VIZ-NBER1 scope covers Evidence page only; VIZ-NBER1 is BLOCKING for all chart types. Not addressed by any LA.
7. **R-02** — No gate for RES-HZE1 content requirements (triad, caption length). Not addressed by any LA.
8. **A-02** — GATE-CL1-8 are self-certifying with no independent Quincy verification. Not addressed by any LA.

---

*Review completed: 2026-05-08. No edits made to any SOP, code, or configuration file.*
