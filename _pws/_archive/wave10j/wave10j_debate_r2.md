# Wave 10J — Cross-Review Debate Round 2
**Agent:** Viz Vera  
**Date:** 2026-04-24  
**Wave:** 10J Phase 3 — Round 2 Response

---

## D1 — Response to Ace on NBER Shading Redundancy

**Ace's argument:** GATE-CL1 (render-success check) and V2 (chart JSON integrity check) catch different failure modes. The 5 hero charts that lacked NBER shading in the Wave 10J self-assessment evidence this: the charts rendered (GATE-CL1 PASS) while missing shading (V2 FAIL). Therefore both checks must stay, and Ace proposes extending GATE-CL1 to parse the Plotly JSON for `vrect` or `rect` shapes.

**My Round 1 position:** Remove NBER shading from GATE-CL1. Quincy owns it via an explicit GATE-VIZ-NBER1. Vera's SOP references but should not define the QA check.

---

### Where I concede to Ace

Ace's core factual point is correct and I cannot refute it: the 5 missing-shading charts did render. A render-success check is not the same as a shading-presence check. These are genuinely different failure modes, and Ace has demonstrated this with real evidence from my own self-assessment. I was wrong to frame this as pure redundancy — they are two distinct checks that happen to concern the same artifact.

I also concede that the current state of GATE-CL1 (render-success only) does NOT catch V2 violations. Ace's proposed extension — parsing the Plotly JSON for `vrect` or `rect` shapes — would make GATE-CL1 cover a new failure surface that V2 does not guard independently at portal assembly time.

### Where I hold

I hold on the role boundary question, and this is the crux.

Ace proposes extending GATE-CL1 to check for `vrect`/`rect` shapes in the figure JSON. If that extension is implemented, GATE-CL1 becomes a Plotly JSON structural check — which is exactly what V2 already is. At that point, the two checks would be checking the **same artifact** (the Plotly JSON `layout.shapes` field), at the **same pipeline stage** (before portal deployment), using the **same method** (JSON inspection). The only difference would be who runs it: Ace in GATE-CL1, or Vera in V2. That is not a meaningful architectural distinction — it is duplication of the same inspection step by two agents.

The correct architecture is:

- **V2 (Vera, pre-handoff):** chart JSON structural check including shading presence. This is Vera's production gate. Vera runs it before handing off to Ace.
- **GATE-CL1 (Ace, portal assembly):** render-success check. Ace confirms the chart loads without crash in the portal context. Ace does NOT duplicate the JSON structural inspection — she receives that assurance from V2 via the handoff note.
- **GATE-VIZ-NBER1 (Quincy, independent verification):** Quincy independently confirms shading presence in the deployed artifact, as an out-of-band check separate from both Vera and Ace.

If Ace extends GATE-CL1 to re-inspect the JSON for `vrect`/`rect`, Ace is doing Vera's job at Vera's layer. This is the same pattern we criticized for direction consistency — multiple agents running the same check because no one trusted the upstream agent's gate. The fix there was not to add more overlapping checks; it was to make the upstream gate reliable and treat downstream checks as independent verification, not repetition.

### Synthesis — what should actually happen

The 5 missing-shading charts failed because V2 was not enforced at handoff, not because GATE-CL1 lacked a JSON parser. The root cause is that Vera's pre-handoff gate was not executed, not that Ace's gate lacked coverage. Adding a JSON parser to GATE-CL1 patches the symptom (catches a missed V2) without fixing the root cause (V2 being skipped).

The correct fix is:

1. **V2 becomes blocking.** Vera's VIZ-V2 pre-handoff check explicitly gates on shading presence for all long-horizon charts. If V2 fails, there is no handoff. This is the enforcement fix.
2. **GATE-CL1 stays as render-success.** Ace checks that the chart loads and renders. Ace trusts V2 — and the V2 pass evidence is in the handoff note.
3. **GATE-VIZ-NBER1 is added to Quincy's SOP** as an independent spot-check. Quincy does NOT re-run Vera's JSON inspection; Quincy checks the deployed portal's rendered output (DOM or screenshot) for visible shading bands. This is different from both V2 (JSON) and GATE-CL1 (Python render) — it is the human-visible end state.

**Final position:** I concede that V2 and render-success GATE-CL1 catch different failure modes. I do not concede that the fix is to add JSON inspection to GATE-CL1. The fix is to enforce V2 as a blocking pre-handoff gate so GATE-CL1 never needs to compensate for Vera's failures.

Quincy agrees with me on the structural point (R2 in Quincy's submission). Quincy's position — remove NBER shading from GATE-CL1, Vera owns it via V2 — supports the architecture I am proposing. This is a 2-1 position against Ace's proposal.

---

## D4 — Making the Case to Quincy: Perceptual PNG Verification as QA Gate

**My Round 1 position (Redundancy 2.4):** The perceptual PNG check (VIZ-V2 item 4) is currently producer self-attestation. I argued it should move to QA independent verification — Quincy verifies PNG existence as a GATE-27 extension.

**Quincy did not respond in Round 1.** I am making the case here directly.

---

### Why self-attestation is insufficient for this check

The perceptual PNG check is specifically about confirming that NBER shading bands are **visually perceptible** at standard zoom — not just that the JSON contains `layout.shapes` data. These are different claims:

- V2 JSON structural check: "The Plotly JSON contains at least one shape with `fillcolor` matching the NBER rgba pattern." Machine-verifiable against the JSON.
- V2 perceptual check (item 4): "When rendered to a PNG at standard dimensions, the shading bands are visible to a human reader at standard zoom." Requires a rendered image.

I have a direct conflict of interest on the perceptual check. If I produce a chart where the shading bands are present in the JSON but rendered in a nearly-invisible light gray (wrong rgba value, wrong opacity, or wrong z-order), the JSON structural check passes and I have an obvious incentive to consider the perceptual check "passed" when it is marginal. A second set of eyes removes that bias.

More concretely: the PNG existence check is **machine-verifiable by Quincy** and takes approximately 5 seconds. Running `git ls-files output/charts/{pair_id}/plotly/_perceptual_check_*.png` for every mandatory-NBER chart type tells Quincy immediately whether the perceptual check step was executed at all. If the PNG does not exist, V2 item 4 was skipped. The perceptual quality of the PNG requires human judgment — but the existence of the PNG is the forcing function that ensures the step was not silently bypassed.

### What the gate would look like in practice

**Proposed GATE-27 extension (Quincy runs this):**

For each pair under verification, for each chart type in the mandatory-NBER list (`timeseries_overview`, `regime_price_overlay`, and any other long-horizon chart added by Vera's SOP):

```
Step 1 (machine): git ls-files output/charts/{pair_id}/plotly/_perceptual_check_{chart_name}.png
  → PASS if file exists, FAIL if absent
  
Step 2 (human, 30 seconds): open the PNG at standard zoom
  → PASS if shading bands are visually distinct from the background
  → FAIL if shading is invisible or indistinguishable from white/background
  → Record verdict in the QA verification log as: "NBER perceptual: {chart_name} = [PASS|FAIL]"
```

This is not a significant burden. There are at most 3-4 mandatory-NBER chart types per pair. Step 1 is a one-liner. Step 2 is a 10-second visual inspection per PNG. Total time: under 2 minutes per pair.

### Why this is Quincy's gate, not a second Vera check

The distinction matters. Currently, V2 item 4 says Vera renders the PNG and "visually confirms" it. This is producer self-attestation: Vera generates the artifact and Vera judges its quality. Moving Step 2 to Quincy makes the perceptual judgment an independent verification step. Vera still generates the PNG (that remains V2 item 4 — Vera must save the PNG as evidence). But the verdict on whether the PNG shows visible shading is Quincy's call, not Vera's.

This is analogous to the Evan→Quincy separation already in place for schema validation: Evan runs `validate_schema.py` (producer-side), Quincy re-runs it independently (QA-side). The check is the same; the trust level differs because they are different agents at different pipeline stages. For perceptual quality, Vera cannot be both producer and judge.

### Why GATE-27 specifically, not a new GATE

GATE-27 currently covers: VIZ-V5 smoke-test log (chart loads, ≥1 data trace, non-empty title, palette_id in registry). Extending it to include the perceptual PNG check is coherent because GATE-27 is the artifact completeness gate — it verifies that Vera's deliverables are present and structurally sound before Quincy proceeds to portal-level verification. The PNG existence check is an artifact completeness check. The perceptual quality judgment is an artifact quality check. Both fit within GATE-27's existing scope.

**Ask to Quincy:** Add two items to GATE-27's checklist for every pair with mandatory-NBER charts:
1. `git ls-files output/charts/{pair_id}/plotly/_perceptual_check_*.png` — verify files exist for all mandatory-NBER chart types.
2. Open each PNG and confirm shading bands are visually distinct. Record verdict in QA log.

This closes the self-attestation gap without adding a new gate or significant overhead.

---

## Summary of Round 2 Positions

| Debate | My Position | Change from R1 |
|--------|-------------|----------------|
| D1 — NBER shading (Ace challenge) | Concede Ace's failure-mode distinction. Hold on fix: enforce V2 as blocking gate; GATE-CL1 stays as render-success; GATE-VIZ-NBER1 goes to Quincy's SOP. Reject Ace's JSON parser extension to GATE-CL1. | Partial concede on diagnosis; hold on remedy |
| D4 — Perceptual PNG (Quincy) | PNG existence = GATE-27 extension (machine check). Perceptual quality judgment = Quincy's call, not Vera's self-attestation. Two-step: git ls-files + 10s visual per chart. | Hold and elaborate |

---

*Viz Vera | Wave 10J Debate R2 | 2026-04-24*
